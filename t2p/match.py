"""
TextListe2PlayListe – Textlistenzeilen parsen und gegen das Inventar matchen.

Projekt:     TextListe2PlayListe
Modul:       t2p/match.py
Version:     1.1.0
Stand:       2026-08-18
Abhaengig:   nur Python-Standardbibliothek (Python >= 3.11)
Bezug:       requirements.txt (leer – Stdlib only)
Lizenz:      –
Upstream:    –
Erstellt mit: Cursor Grok 4.6
Autor:       (FFHB) / RadioBBS

Beschreibung
------------
Textlistenzeilen parsen und gegen das Inventar matchen.

Historie
--------
Version 1.0.0 – 2026-08-01 – Inventar, Matching, m3u8-Export
Version 1.1.0 – 2026-08-18 – Styleguide 1.4.0: Dateikopf Pflichtfelder

Aufruf / Nutzung
----------------
  python textliste2playlist.py --help
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from .inventar import Track
from .normalize import (
    DASH_RE,
    YEAR_RE,
    collapse_duplicate_letters,
    fuzzy_token_variants,
    normalize_text,
    tokens,
)

STOPWORDS = {
    "the",
    "el",
    "la",
    "los",
    "las",
    "de",
    "del",
    "y",
    "and",
    "orquesta",
    "orchestra",
    "tipica",
    "su",
    "con",
    "c",
    "vol",
    "volume",
}

# Reihenfolge: längere Marker zuerst
ARTIST_SPLIT_MARKERS = (
    " c. ",
    " feat. ",
    " ft. ",
    " with ",
    " con ",
    " · ",
    " y ",
    " & ",
    " / ",
    " c ",
    " feat ",
    " ft ",
)


@dataclass(slots=True)
class ParsedLine:
    raw: str
    artist: str
    title: str
    vocalist: str
    year: str | None
    query_tokens: list[str]


@dataclass(slots=True)
class MatchResult:
    line: ParsedLine
    track: Track | None
    score: float
    candidates: list[tuple[float, Track]]


def split_artist_vocalist(artist_field: str) -> tuple[str, str]:
    text = artist_field.strip()
    lower = f" {text.lower()} "
    for marker in ARTIST_SPLIT_MARKERS:
        needle = marker.lower()
        pos = lower.find(needle)
        if pos < 0:
            continue
        # lower hat führendes Leerzeichen → Offset -1
        start = pos - 1
        artist = text[:start].strip(" -–—·/")
        vocalist = text[start + len(marker) :].strip(" -–—·/")
        if artist and vocalist:
            return artist, vocalist
    return text, ""


def extract_year(text: str) -> tuple[str, str | None]:
    m = YEAR_RE.search(text)
    if not m:
        m2 = re.search(r"(?:^|[\s\-–—])((?:19|20)\d{2})\s*$", text)
        if not m2:
            return text, None
        year = m2.group(1)
        cleaned = text[: m2.start(1)].rstrip(" -–—\t")
        return cleaned, year
    year = m.group(1)
    cleaned = (text[: m.start(1)] + text[m.end(1) :]).strip(" -–—\t")
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    return cleaned, year


def _query_tokens(artist: str, title: str, vocalist: str) -> list[str]:
    toks: list[str] = []
    for chunk in (title, artist, vocalist):
        for t in tokens(chunk):
            if t in STOPWORDS or len(t) == 1:
                continue
            if t not in toks:
                toks.append(t)
    return toks


def parse_playlist_line(raw: str) -> ParsedLine | None:
    line = raw.strip()
    if not line or line.startswith("#"):
        return None

    line, year = extract_year(line)
    parts = [p.strip() for p in DASH_RE.split(line) if p.strip()]

    if len(parts) == 1:
        return ParsedLine(
            raw=raw.strip(),
            artist="",
            title=parts[0],
            vocalist="",
            year=year,
            query_tokens=_query_tokens("", parts[0], ""),
        )

    if len(parts) == 2:
        artist_field, title = parts
        artist, vocalist = split_artist_vocalist(artist_field)
        return ParsedLine(
            raw=raw.strip(),
            artist=artist,
            title=title,
            vocalist=vocalist,
            year=year,
            query_tokens=_query_tokens(artist, title, vocalist),
        )

    # 3+ Teile: „Orchester – Vokalist – Titel“ oder „Künstler c. Sänger – Titel – Extra“
    first, *middle, last = parts
    artist, vocalist_in_first = split_artist_vocalist(first)
    if vocalist_in_first:
        vocalist = vocalist_in_first
        title = " – ".join([*middle, last])
    else:
        if middle:
            vocalist = " – ".join(middle)
            title = last
        else:
            vocalist = ""
            title = last

    return ParsedLine(
        raw=raw.strip(),
        artist=artist,
        title=title,
        vocalist=vocalist,
        year=year,
        query_tokens=_query_tokens(artist, title, vocalist),
    )


def build_token_index(tracks: list[Track]) -> dict[str, list[int]]:
    """Invertierter Index: Norm-Token → Track-Indizes."""
    index: dict[str, list[int]] = {}
    for i, track in enumerate(tracks):
        seen: set[str] = set()
        for tok in track.norm.split():
            if len(tok) < 2 or tok in seen:
                continue
            seen.add(tok)
            index.setdefault(tok, []).append(i)
        loose = collapse_duplicate_letters(track.norm)
        if loose != track.norm:
            for tok in loose.split():
                if len(tok) < 2 or tok in seen:
                    continue
                seen.add(tok)
                index.setdefault(tok, []).append(i)
    return index


def _candidate_indices(
    primary_variants: list[str],
    tracks: list[Track],
    index: dict[str, list[int]] | None,
) -> list[int]:
    if index is None:
        return list(range(len(tracks)))
    found: set[int] = set()
    for variant in primary_variants:
        for idx in index.get(variant, ()):
            found.add(idx)
    return sorted(found)


def _best_title_ratio(title_norm: str, stem_norm: str) -> float:
    if not title_norm or not stem_norm:
        return 0.0
    best = SequenceMatcher(None, title_norm, stem_norm).ratio()
    for part in re.split(r"[\s\-_./]+", stem_norm):
        if len(part) < 3:
            continue
        if abs(len(part) - len(title_norm)) > max(3, len(title_norm) // 2):
            continue
        best = max(best, SequenceMatcher(None, title_norm, part).ratio())
    return best


def _token_in_hay(token: str, hay: str, hay_loose: str) -> bool:
    for variant in fuzzy_token_variants(token):
        if variant in hay or variant in hay_loose:
            return True
    return False


def _score_track(parsed: ParsedLine, track: Track) -> float:
    title_toks = [t for t in tokens(parsed.title) if t not in STOPWORDS and len(t) > 1]
    # Abkürzungen wie CTV (nach Normalisierung ein Token Länge >= 2)
    if not title_toks:
        title_toks = [t for t in tokens(parsed.title) if t not in STOPWORDS]
    artist_toks = [t for t in tokens(parsed.artist) if t not in STOPWORDS and len(t) > 1]
    vocal_toks = [t for t in tokens(parsed.vocalist) if t not in STOPWORDS and len(t) > 1]

    if not title_toks:
        return 0.0

    hay = track.norm
    hay_loose = collapse_duplicate_letters(hay)
    title_hits = sum(1 for t in title_toks if _token_in_hay(t, hay, hay_loose))
    title_ratio = title_hits / len(title_toks)

    title_norm = normalize_text(parsed.title, collapse_dupes=True)
    stem_loose = collapse_duplicate_letters(normalize_text(track.stem))
    seq = _best_title_ratio(title_norm, stem_loose)
    # auch gegen gesamten normierten Pfad (oft enthält Dateiname den Titel klarer)
    seq = max(seq, _best_title_ratio(title_norm, hay_loose))

    if title_ratio < 0.6 and seq < 0.72:
        return 0.0
    if title_ratio < 0.6:
        title_ratio = max(title_ratio, seq)

    artist_ratio = 1.0
    if artist_toks:
        artist_hits = sum(1 for t in artist_toks if _token_in_hay(t, hay, hay_loose))
        artist_ratio = artist_hits / len(artist_toks)

    vocal_bonus = 0.0
    if vocal_toks:
        vocal_hits = sum(1 for t in vocal_toks if _token_in_hay(t, hay, hay_loose))
        vocal_bonus = 0.08 * (vocal_hits / len(vocal_toks))

    year_bonus = 0.05 if parsed.year and parsed.year in hay else 0.0

    phrase_bonus = 0.0
    title_phrase = normalize_text(parsed.title, collapse_dupes=True)
    if title_phrase and title_phrase in hay_loose:
        phrase_bonus = 0.12
    elif len(title_toks) >= 2:
        # leichte Abwertung, wenn alle Wörter treffen, aber nicht als Phrase
        # (z. B. „Viejos tiempos“ vs. „Tiempos viejos“)
        if title_ratio >= 0.99 and title_phrase not in hay_loose:
            phrase_bonus = -0.06

    score = (
        0.55 * title_ratio
        + 0.30 * artist_ratio
        + 0.10 * seq
        + vocal_bonus
        + year_bonus
        + phrase_bonus
    )
    if artist_toks and artist_ratio == 0:
        score *= 0.35
    return score


def find_candidates(
    parsed: ParsedLine,
    tracks: list[Track],
    *,
    limit: int = 8,
    min_score: float = 0.45,
    index: dict[str, list[int]] | None = None,
) -> list[tuple[float, Track]]:
    title_toks = [t for t in tokens(parsed.title) if t not in STOPWORDS and len(t) > 1]
    if not title_toks:
        title_toks = [t for t in tokens(parsed.title) if t not in STOPWORDS]
    if not title_toks:
        return []

    title_toks_sorted = sorted(title_toks, key=len, reverse=True)
    primary = title_toks_sorted[0]
    secondary = title_toks_sorted[1:]
    primary_variants = fuzzy_token_variants(primary)
    artist_toks = [t for t in tokens(parsed.artist) if t not in STOPWORDS and len(t) > 1]

    scored: list[tuple[float, Track]] = []
    for idx in _candidate_indices(primary_variants, tracks, index):
        track = tracks[idx]
        hay = track.norm
        hay_loose = collapse_duplicate_letters(hay)
        if not any(v in hay or v in hay_loose for v in primary_variants):
            continue
        if len(secondary) >= 2 and not any(
            _token_in_hay(t, hay, hay_loose) for t in secondary
        ):
            continue
        score = _score_track(parsed, track)
        if score >= min_score:
            scored.append((score, track))

    if not scored and artist_toks:
        # Fuzzy-Fallback bei Tippfehlern im Titel (Bombonsito ↔ Bomboncito)
        title_norm = normalize_text(parsed.title, collapse_dupes=True)
        artist_indices = _candidate_indices(artist_toks, tracks, index)
        for idx in artist_indices:
            track = tracks[idx]
            hay = track.norm
            if not any(_token_in_hay(a, hay, collapse_duplicate_letters(hay)) for a in artist_toks):
                continue
            stem_loose = collapse_duplicate_letters(normalize_text(track.stem))
            if _best_title_ratio(title_norm, stem_loose) < 0.82:
                continue
            score = _score_track(parsed, track)
            if score >= min_score:
                scored.append((score, track))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:limit]


def match_line(
    raw: str,
    tracks: list[Track],
    *,
    min_score: float = 0.55,
    index: dict[str, list[int]] | None = None,
) -> MatchResult | None:
    parsed = parse_playlist_line(raw)
    if parsed is None:
        return None
    candidates = find_candidates(
        parsed, tracks, min_score=min_score * 0.75, index=index
    )
    if not candidates:
        return MatchResult(line=parsed, track=None, score=0.0, candidates=[])
    best_score, best = candidates[0]
    if best_score < min_score:
        return MatchResult(line=parsed, track=None, score=best_score, candidates=candidates)
    return MatchResult(line=parsed, track=best, score=best_score, candidates=candidates)


def read_text_lines(path: str | Path) -> list[str]:
    return Path(path).read_text(encoding="utf-8-sig").splitlines()
