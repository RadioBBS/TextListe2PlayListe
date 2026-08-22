"""
TextListe2PlayListe – Musikinventar scannen, speichern und laden.

Projekt:     TextListe2PlayListe
Modul:       t2p/inventar.py
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
Musikinventar scannen, speichern und laden.

Historie
--------
Version 1.0.0 – 2026-08-01 – Inventar, Matching, m3u8-Export
Version 1.1.0 – 2026-08-18 – Styleguide 1.4.0: Dateikopf Pflichtfelder

Aufruf / Nutzung
----------------
  python textliste2playlist.py --help
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Iterator

from .normalize import normalize_text

AUDIO_EXTENSIONS = {
    ".mp3",
    ".flac",
    ".m4a",
    ".aac",
    ".ogg",
    ".opus",
    ".wma",
    ".wav",
    ".aiff",
    ".aif",
    ".alac",
}


@dataclass(slots=True)
class Track:
    path: str
    rel: str
    name: str
    stem: str
    ext: str
    size: int
    mtime: float
    norm: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Track:
        return cls(
            path=data["path"],
            rel=data["rel"],
            name=data["name"],
            stem=data["stem"],
            ext=data["ext"],
            size=int(data.get("size", 0)),
            mtime=float(data.get("mtime", 0)),
            norm=data.get("norm") or normalize_text(f"{data.get('rel', '')} {data.get('stem', '')}"),
        )


@dataclass(slots=True)
class Inventory:
    root: str
    created_at: str
    track_count: int
    tracks: list[Track]

    def to_dict(self) -> dict:
        return {
            "root": self.root,
            "created_at": self.created_at,
            "track_count": self.track_count,
            "tracks": [t.to_dict() for t in self.tracks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Inventory:
        tracks = [Track.from_dict(t) for t in data.get("tracks", [])]
        return cls(
            root=data.get("root", ""),
            created_at=data.get("created_at", ""),
            track_count=int(data.get("track_count", len(tracks))),
            tracks=tracks,
        )


def iter_audio_files(root: Path) -> Iterator[Path]:
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        # versteckte / System-Ordner überspringen
        dirnames[:] = [
            d
            for d in dirnames
            if not d.startswith(".")
            and d.lower() not in {"system volume information", "$recycle.bin"}
        ]
        for name in filenames:
            ext = Path(name).suffix.lower()
            if ext in AUDIO_EXTENSIONS:
                yield Path(dirpath) / name


def build_track(path: Path, root: Path) -> Track:
    rel = path.relative_to(root).as_posix()
    stem = path.stem
    # Norm: Dateiname + relative Ordnerpfade (hilft bei Künstler-Ordnern)
    searchable = f"{rel} {stem}"
    try:
        st = path.stat()
        size = int(st.st_size)
        mtime = float(st.st_mtime)
    except OSError:
        size = 0
        mtime = 0.0
    return Track(
        path=str(path),
        rel=rel,
        name=path.name,
        stem=stem,
        ext=path.suffix.lower(),
        size=size,
        mtime=mtime,
        norm=normalize_text(searchable),
    )


def scan_inventory(root: Path, progress_every: int = 2000) -> Inventory:
    root = root.resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Musikwurzel nicht gefunden: {root}")

    tracks: list[Track] = []
    started = time.perf_counter()
    for idx, path in enumerate(iter_audio_files(root), start=1):
        tracks.append(build_track(path, root))
        if progress_every and idx % progress_every == 0:
            elapsed = time.perf_counter() - started
            print(f"  … {idx} Dateien ({elapsed:.1f}s)")

    created = time.strftime("%Y-%m-%dT%H:%M:%S")
    return Inventory(
        root=str(root),
        created_at=created,
        track_count=len(tracks),
        tracks=tracks,
    )


def save_inventory(inventory: Inventory, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as fh:
        json.dump(inventory.to_dict(), fh, ensure_ascii=False, indent=None, separators=(",", ":"))


def load_inventory(path: Path | str) -> Inventory:
    path = Path(path)
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return Inventory.from_dict(data)


def filter_tracks(tracks: Iterable[Track], query: str) -> list[Track]:
    q_tokens = [t for t in normalize_text(query).split() if t]
    if not q_tokens:
        return []
    hits: list[Track] = []
    for track in tracks:
        if all(tok in track.norm for tok in q_tokens):
            hits.append(track)
    return hits
