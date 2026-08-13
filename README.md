# TextListe2PlayListe

Erstelle aus einer Text-Liste eine m3u Playliste.

Das Tool legt zuerst ein **Inventar** aller Musikstücke auf dem Datenträger an.
Über dieses Inventar werden Textlistenzeilen (Künstler – Titel – Jahr) den Dateien
zugeordnet und als **m3u8** mit relativen Pfaden geschrieben – im Stil von
`J:\FooBar_Playlists\NEO.m3u8` (`primary/MP3/...`).

## Voraussetzungen

- Windows
- Python 3.11+ (nur Standardbibliothek)
- Musikbibliothek z. B. unter `J:\` (Ordner `MP3\`, Playlisten unter `FooBar_Playlists\`)

## Installation

```bat
cd /d C:\Users\radio\Documents\Cursor\GIT-Projects\TextListe2PlayListe
```

Keine Pip-Pakete nötig.

## Ablauf

### 1. Inventar anlegen

```bat
python textliste2playlist.py inventar --root J:\ -o inventar\music_inventar.json
```

Scannt alle Audio-Dateien unter der Wurzel und speichert Pfad, Dateiname und
normalisierten Suchtext. Das Inventar dient später der Suche und Playlist-Erzeugung.

### 2. Im Inventar suchen

```bat
python textliste2playlist.py suche "Gobbi Adios Corazon"
```

### 3. Playliste aus Textliste erzeugen

```bat
python textliste2playlist.py playlist "C:\Users\radio\Documents\Cursor\TXT\Playlist Milonga Sueño 15.11.2025 Los Mejores Éxitos de la Época de Oro" -o "J:\FooBar_Playlists\Milonga Sueno 15.11.2025.m3u8"
```

- Leere Zeilen und `#`-Kommentare werden übersprungen.
- Treffer landen als `primary/<relativer Pfad>` in der m3u8.
- Zusätzlich entsteht ein Report (`*.m3u8.report.txt`) mit Score, Treffern und Alternativen.

Nur prüfen, ohne Datei zu schreiben:

```bat
python textliste2playlist.py playlist "PFAD\zur\Textliste" --dry-run
```

## Textlisten-Format

Eine Zeile pro Stück, typisch:

```text
Alfredo Gobbi c. Tito Landi – Adios corazon – 1958
Francisco Canaro – Viejos tiempos
Edgardo Donato · Horacio Lagos – La milonga que faltaba
```

Erkannt werden u. a. Trennzeichen `–`/`-`, Vokalisten-Marker (`c.`, `·`, `y`, `&`) und Jahreszahlen.

## Projektstruktur

```text
textliste2playlist.py   Einstieg
t2p/                    Inventar, Matching, Playlisten-Schreiben
inventar/               erzeugte Inventardatei (gitignored)
```

## Hinweise

- Der Präfix `primary` entspricht dem foobar2000-Mediathek-Namen; änderbar mit `--prefix`.
- Relative Pfade beziehen sich auf `--root` (Standard `J:\`).
- Exit-Code `2`, wenn mindestens eine Zeile keinen Treffer hatte (Playliste wird trotzdem geschrieben).
