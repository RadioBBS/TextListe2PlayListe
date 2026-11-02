"""
TextListe2PlayListe – Gemeinsame Projekt-Metadaten.

Projekt:     TextListe2PlayListe
Modul:       project_meta.py
Version:     1.1.1
Stand:       2026-11-02
Abhaengig:   nur Python-Standardbibliothek (Python >= 3.11)
Bezug:       requirements.txt (leer – Stdlib only)
Lizenz:      –
Upstream:    –
Erstellt mit: Cursor Grok 4.6
Autor:       (FFHB) / RadioBBS

Beschreibung
------------
Einzelne Quelle fuer Name, Version, Datum und Abhaengigkeiten. Erzeugt
aus Textlisten m3u/m3u8-Playlisten ueber ein Musikinventar.

Historie
--------
Version 1.0.0 – 2026-08-01 – Inventar, Matching, m3u8-Export
Version 1.1.0 – 2026-08-18 – Styleguide 1.4.0: Pflichtblock, CLI --help/--version/--Ende
Version 1.1.0 – 2026-08-20 – check_runtime(): Python-Mindestversion und optionales Windows
Version 1.1.1 – 2026-11-02 – Startausgabe und Python 3.11 nach Styleguide 2.1.0.

Aufruf / Nutzung
----------------
  from project_meta import check_runtime
  check_runtime()  # nach argparse, damit --help/--version zuerst gehen
  from project_meta import __version__, metadata_block
  print(metadata_block("textliste2playlist.py"))
"""

from __future__ import annotations

import re
import sys

PROJECT_NAME = "TextListe2PlayListe"
PROJECT_DESCRIPTION = "Erstelle aus einer Text-Liste eine m3u Playliste."
PYTHON_REQUIRES = ">=3.11"
REQUIRES_WINDOWS = False
STYLEGUIDE_VERSION = "2.1.0"

__version__ = "1.1.1"
__date__ = "2026-11-02"
__license__ = "–"
__created_with__ = "Cursor Grok 4.6"
__upstream__ = "–"
__author__ = "(FFHB) / RadioBBS"
__requires__ = "nur Python-Standardbibliothek (Python >= 3.11)"
__requirements_ref__ = "requirements.txt (leer – Stdlib only)"



def min_python_tuple() -> tuple[int, int]:
    """
    Beschreibung: Liest die Mindest-Python-Version aus PYTHON_REQUIRES.
    Parameter: keine
    Rueckgabewert: Tupel (major, minor), z. B. (3, 11)
    Fehlerfaelle: ValueError bei ungueltigem PYTHON_REQUIRES
    Beispiel: min_python_tuple() == (3, 11)
    """
    match = re.search(r"(\d+)\.(\d+)", PYTHON_REQUIRES)
    if match is None:
        raise ValueError(f"Ungueltiges PYTHON_REQUIRES: {PYTHON_REQUIRES!r}")
    return int(match.group(1)), int(match.group(2))


def found_os_name() -> str:
    """
    Beschreibung: Liefert einen lesbaren Namen des aktuellen Betriebssystems.
    Parameter: keine
    Rueckgabewert: Windows, Linux, macOS oder sys.platform
    Fehlerfaelle: keine
    Beispiel: found_os_name()
    """
    names = {
        "win32": "Windows",
        "linux": "Linux",
        "darwin": "macOS",
        "cygwin": "Cygwin",
        "msys": "MSYS",
    }
    return names.get(sys.platform, sys.platform)


def check_runtime(*, require_windows: bool | None = None) -> None:
    """
    Beschreibung: Prueft Python-Version und optional Windows nach argparse.
    Parameter: require_windows – None nutzt REQUIRES_WINDOWS aus diesem Modul
    Rueckgabewert: None
    Fehlerfaelle: SystemExit(2) bei zu altem Python oder falschem OS
    Beispiel: check_runtime()
    """
    needed = min_python_tuple()
    if sys.version_info[:2] < needed:
        print(
            "Dieses Python-Skript benoetigt Python >= "
            f"{needed[0]}.{needed[1]} (gefunden: "
            f"{sys.version_info.major}.{sys.version_info.minor}."
            f"{sys.version_info.micro}).",
            file=sys.stderr,
        )
        raise SystemExit(2)
    want_win = REQUIRES_WINDOWS if require_windows is None else require_windows
    if want_win and sys.platform != "win32":
        print(
            f"Dieses Skript benoetigt Windows (gefunden: {found_os_name()}).",
            file=sys.stderr,
        )
        raise SystemExit(2)


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
