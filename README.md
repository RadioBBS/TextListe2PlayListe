# TextListe2PlayListe

```
TextListe2PlayListe – Aus einer Textliste eine m3u-Playliste erzeugen.

Projekt:     TextListe2PlayListe
Modul:       README.md
Version:     1.1.1
Stand:       2026-11-02
Abhaengig:   nur Python-Standardbibliothek (Python >= 3.11)
Bezug:       requirements.txt (leer – Stdlib only)
Lizenz:      –
Upstream:    –
Erstellt mit: Cursor Grok 4.6
Autor:       (FFHB) / RadioBBS

Historie
--------
Version 1.1.1 – 2026-11-02 – Startausgabe und Python 3.11 nach Styleguide 2.1.0.
```

Erstelle aus einer Text-Liste eine m3u Playliste.

Das Tool legt zuerst ein **Inventar** aller Musikstuecke auf dem Datentraeger an.
Ueber dieses Inventar werden Textlistenzeilen (Kuenstler – Titel – Jahr) den Dateien
zugeordnet und als **m3u8** mit relativen Pfaden geschrieben – im Stil von
`J:\FooBar_Playlists\NEO.m3u8` (`primary/MP3/...`).

## Voraussetzungen

- Windows
- Python 3.11+ (nur Standardbibliothek)
- Musikbibliothek z. B. unter `J:\` (Ordner `MP3\`, Playlisten unter `FooBar_Playlists\`)

## Installation

```bat
cd /d "%USERPROFILE%\Documents\Cursor\GIT-Projects\TextListe2PlayListe"
python -m pip install -r requirements.txt
```

Keine Pip-Pakete noetig (Stdlib only). Empfohlen:

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Ablauf

### 1. Inventar anlegen

```bat
python textliste2playlist.py --help
python textliste2playlist.py --version
python textliste2playlist.py inventar --root J:\ -o inventar\music_inventar.json
```

Scannt alle Audio-Dateien unter der Wurzel und speichert Pfad, Dateiname und
normalisierten Suchtext. Das Inventar dient spaeter der Suche und Playlist-Erzeugung.

### 2. Im Inventar suchen

```bat
python textliste2playlist.py suche "Gobbi Adios Corazon"
```

### 3. Playliste aus Textliste erzeugen

```bat
python textliste2playlist.py playlist "PFAD\zur\Textliste" -o "J:\FooBar_Playlists\Milonga Sueno.m3u8" --Ende
```

- Leere Zeilen und `#`-Kommentare werden uebersprungen.
- Treffer landen als `primary/<relativer Pfad>` in der m3u8.
- Zusaetzlich entsteht ein Report (`*.m3u8.report.txt`) mit Score, Treffern und Alternativen.

Nur pruefen, ohne Datei zu schreiben:

```bat
python textliste2playlist.py playlist "PFAD\zur\Textliste" --dry-run
```

## Textlisten-Format

Eine Zeile pro Stueck, typisch:

```text
Alfredo Gobbi c. Tito Landi – Adios corazon – 1958
Francisco Canaro – Viejos tiempos
Edgardo Donato · Horacio Lagos – La milonga que faltaba
```

Erkannt werden u. a. Trennzeichen `–`/`-`, Vokalisten-Marker (`c.`, `·`, `y`, `&`) und Jahreszahlen.

## Projektstruktur

```text
textliste2playlist.py   Einstieg
t2p/                    Inventar, Matching, Playlisten-Schreiben
inventar/               erzeugte Inventardatei (gitignored)
```

## Hinweise

- Der Praefix `primary` entspricht dem foobar2000-Mediathek-Namen; aenderbar mit `--prefix`.
- Relative Pfade beziehen sich auf `--root` (Standard `J:\`).
- `--Ende` / `-E` wartet am Programmende auf Taste oder Enter.
