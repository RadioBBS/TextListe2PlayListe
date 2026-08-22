"""
TextListe2PlayListe – Textnormalisierung fuer robustes Matching.

Projekt:     TextListe2PlayListe
Modul:       t2p/normalize.py
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
Textnormalisierung für robustes Matching von Künstlern/Titeln.

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
import unicodedata

# Häufige Trennzeichen in Textlisten und Dateinamen
DASH_RE = re.compile(r"\s*[–—―−\-]+\s*")
YEAR_RE = re.compile(r"(?:^|[\s\-–—])((?:19|20)\d{2})(?:\s*$|\s*[\(\[])")
NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
SPACE_RE = re.compile(r"\s+")
# „PorDos“ / „aandariego“ / „Ccorazon“ aus handgeschriebenen Listen
CAMEL_RE = re.compile(r"([a-z])([A-Z])")
DUP_CHAR_RE = re.compile(r"(.)\1+")
# „C.T.V.“ / „A.M.“ → ctv / am
DOTTED_ABBREV_RE = re.compile(r"\b(?:[a-z]\.){2,}[a-z]?\.?\b", re.IGNORECASE)

# Vokalisatoren / Konjunktionen in Tango-Notation
VOCALIST_MARKERS = (
    " c. ",
    " c ",
    " con ",
    " w/ ",
    " with ",
    " feat. ",
    " feat ",
    " ft. ",
    " ft ",
)

APOSTROPHE_MAP = str.maketrans(
    {
        "\u2018": "'",
        "\u2019": "'",
        "\u201a": "'",
        "\u2032": "'",
        "`": "'",
        "´": "'",
        "\u201c": '"',
        "\u201d": '"',
    }
)


def strip_accents(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def expand_camel_case(text: str) -> str:
    return CAMEL_RE.sub(r"\1 \2", text)


def collapse_dotted_abbrev(text: str) -> str:
    return DOTTED_ABBREV_RE.sub(lambda m: m.group(0).replace(".", ""), text)


def collapse_duplicate_letters(text: str) -> str:
    """aa → a (hilft bei Tippfehlern wie Aandariego, Ccorazon)."""
    return DUP_CHAR_RE.sub(r"\1", text)


def normalize_text(text: str, *, collapse_dupes: bool = False) -> str:
    """Kleinbuchstaben, ohne Akzente/Satzzeichen – für Fuzzy-Vergleiche."""
    if not text:
        return ""
    text = text.translate(APOSTROPHE_MAP)
    text = expand_camel_case(text)
    text = strip_accents(text).lower()
    text = collapse_dotted_abbrev(text)
    text = text.replace("&", " and ")
    text = text.replace("·", " ")
    text = text.replace("/", " ")
    text = NON_ALNUM_RE.sub(" ", text)
    text = SPACE_RE.sub(" ", text).strip()
    if collapse_dupes:
        text = collapse_duplicate_letters(text)
    return text


def tokens(text: str, *, collapse_dupes: bool = False) -> list[str]:
    return [t for t in normalize_text(text, collapse_dupes=collapse_dupes).split() if t]


def fuzzy_token_variants(token: str) -> list[str]:
    """Varianten eines Tokens für tolerantes Matching."""
    variants = [token]
    collapsed = collapse_duplicate_letters(token)
    if collapsed and collapsed not in variants:
        variants.append(collapsed)
    return variants


def collapse_dashes(text: str) -> str:
    return DASH_RE.sub(" – ", text.strip())
