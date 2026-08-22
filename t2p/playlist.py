"""
TextListe2PlayListe – m3u/m3u8 Playlisten schreiben (foobar2000-kompatibel).

Projekt:     TextListe2PlayListe
Modul:       t2p/playlist.py
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
m3u / m3u8 Playlisten schreiben (foobar2000-kompatibel).

Historie
--------
Version 1.0.0 – 2026-08-01 – Inventar, Matching, m3u8-Export
Version 1.1.0 – 2026-08-18 – Styleguide 1.4.0: Dateikopf Pflichtfelder

Aufruf / Nutzung
----------------
  python textliste2playlist.py --help
"""

from __future__ import annotations

from pathlib import Path

from .inventar import Track


def playlist_entry_path(
    track: Track,
    *,
    library_prefix: str = "primary",
    use_forward_slashes: bool = True,
) -> str:
    """
    Beschreibung: Relativer Playlisten-Eintrag wie in FooBar-Playlisten.
    Parameter: track, library_prefix (z. B. primary), use_forward_slashes
    Rueckgabewert: Pfadstring z. B. primary/MP3/Tango/...
    Fehlerfaelle: keine
    Beispiel: playlist_entry_path(track) -> "primary/MP3/..."
    """
    rel = track.rel.replace("\\", "/") if use_forward_slashes else track.rel.replace("/", "\\")
    prefix = library_prefix.strip().strip("/\\")
    if prefix:
        return f"{prefix}/{rel}" if use_forward_slashes else f"{prefix}\\{rel}"
    return rel


def write_m3u(
    tracks: list[Track],
    dest: Path,
    *,
    library_prefix: str = "primary",
    rating_tag: bool = True,
    extm3u: bool = True,
) -> None:
    """
    Beschreibung: Schreibt eine m3u/m3u8-Playliste mit relativen Eintraegen.
    Parameter: tracks, dest, library_prefix, rating_tag, extm3u
    Rueckgabewert: None
    Fehlerfaelle: OSError beim Anlegen/Schreiben
    Beispiel: write_m3u(treffer, Path("out.m3u8"))
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    if extm3u:
        lines.append("#EXTM3U")
    for track in tracks:
        if rating_tag:
            lines.append("#EXT-X-RATING:0")
        lines.append(playlist_entry_path(track, library_prefix=library_prefix))
    # Unix-Newlines wie foobar; BOM-frei UTF-8
    dest.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
