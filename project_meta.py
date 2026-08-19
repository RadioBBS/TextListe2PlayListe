"""
TextListe2PlayListe – Gemeinsame Projekt-Metadaten.

Projekt:     TextListe2PlayListe
Modul:       project_meta.py
Version:     1.1.0
Stand:       2026-08-18
Abhaengig:   nur Python-Standardbibliothek (Python >= 3.11)
Bezug:       requirements.txt (leer – Stdlib only)
Lizenz:      –
Upstream:    –
Erstellt mit: Cursor Grok 4.6
Autor:       Frank Heider / RadioBBS

Beschreibung
------------
Einzelne Quelle fuer Name, Version, Datum und Abhaengigkeiten. Erzeugt
aus Textlisten m3u/m3u8-Playlisten ueber ein Musikinventar.

Historie
--------
Version 1.0.0 – 2026-08-01 – Inventar, Matching, m3u8-Export
Version 1.1.0 – 2026-08-18 – Styleguide 1.4.0: Pflichtblock, CLI --help/--version/--Ende

Aufruf / Nutzung
----------------
  from project_meta import __version__, metadata_block
  print(metadata_block("textliste2playlist.py"))
"""

from __future__ import annotations

PROJECT_NAME = "TextListe2PlayListe"
PROJECT_DESCRIPTION = "Erstelle aus einer Text-Liste eine m3u Playliste."
PYTHON_REQUIRES = ">=3.11"
STYLEGUIDE_VERSION = "1.4.0"

__version__ = "1.1.0"
__date__ = "2026-08-18"
__license__ = "–"
__created_with__ = "Cursor Grok 4.6"
__upstream__ = "–"
__author__ = "Frank Heider / RadioBBS"
__requires__ = "nur Python-Standardbibliothek (Python >= 3.11)"
__requirements_ref__ = "requirements.txt (leer – Stdlib only)"


def metadata_block(module: str) -> str:
    """
    Beschreibung: Erzeugt den standardisierten Dateikopf (Pflichtfelder plus Autor).
    Parameter: module – relativer Dateipfad (POSIX)
    Rueckgabewert: Mehrzeiliger String
    Fehlerfaelle: keine
    Beispiel: metadata_block("textliste2playlist.py")
    """
    return (
        f"Projekt:     {PROJECT_NAME}\n"
        f"Modul:       {module}\n"
        f"Version:     {__version__}\n"
        f"Stand:       {__date__}\n"
        f"Abhaengig:   {__requires__}\n"
        f"Bezug:       {__requirements_ref__}\n"
        f"Lizenz:      {__license__}\n"
        f"Upstream:    {__upstream__}\n"
        f"Erstellt mit: {__created_with__}\n"
        f"Autor:       {__author__}"
    )


def comment_header(module: str, zweck: str) -> str:
    """
    Beschreibung: Dateikopf als #-Kommentarblock.
    Parameter: module, zweck
    Rueckgabewert: Kommentarblock
    Fehlerfaelle: keine
    Beispiel: comment_header("requirements.txt", "Abhaengigkeiten")
    """
    lines = [f"# {PROJECT_NAME} – {zweck}.", "#"]
    for line in metadata_block(module).splitlines():
        lines.append(f"# {line}")
    return "\n".join(lines)
