#!/usr/bin/env python3
"""
TextListe2PlayListe – Einstiegspunkt: Textliste zu m3u-Playliste.

Projekt:     TextListe2PlayListe
Modul:       textliste2playlist.py
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
TextListe2PlayListe – Einstiegspunkt.

Erstelle aus einer Text-Liste eine m3u Playliste.

Historie
--------
Version 1.0.0 – 2026-08-01 – Inventar, Matching, m3u8-Export
Version 1.1.0 – 2026-08-18 – Styleguide 1.4.0: Dateikopf Pflichtfelder
Version 1.1.1 – 2026-11-02 – Startausgabe und Python 3.11 nach Styleguide 2.1.0.

Aufruf / Nutzung
----------------
  python textliste2playlist.py --help
"""

from __future__ import annotations

import sys

from t2p.cli import main

if __name__ == "__main__":
    sys.exit(main())
