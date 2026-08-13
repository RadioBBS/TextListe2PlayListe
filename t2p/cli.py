"""Kommandozeile für TextListe2PlayListe."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import __description__, __version__
from .inventar import filter_tracks, load_inventory, save_inventory, scan_inventory
from .match import build_token_index, match_line, read_text_lines
from .playlist import write_m3u

DEFAULT_ROOT = Path("J:/")
DEFAULT_INVENTAR = Path("inventar/music_inventar.json")
DEFAULT_PLAYLIST_DIR = Path("J:/FooBar_Playlists")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="textliste2playlist",
        description=__description__,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command", required=True)

    p_inv = sub.add_parser("inventar", help="Musikdatenträger scannen und Inventar speichern")
    p_inv.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help=f"Wurzel des Datenträgers (Standard: {DEFAULT_ROOT})",
    )
    p_inv.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_INVENTAR,
        help=f"Ziel-Inventardatei (Standard: {DEFAULT_INVENTAR})",
    )
    p_inv.add_argument(
        "--progress-every",
        type=int,
        default=5000,
        help="Fortschritt alle N Dateien (0 = aus)",
    )

    p_search = sub.add_parser("suche", help="Im Inventar suchen")
    p_search.add_argument("query", help="Suchbegriffe (Künstler/Titel/Ordner)")
    p_search.add_argument(
        "-i",
        "--inventar",
        type=Path,
        default=DEFAULT_INVENTAR,
        help="Inventardatei",
    )
    p_search.add_argument("-n", "--limit", type=int, default=30, help="Max. Treffer")

    p_pl = sub.add_parser("playlist", help="Aus Textliste eine m3u/m3u8 Playliste erzeugen")
    p_pl.add_argument(
        "textliste",
        type=Path,
        help="Externe Textdatei mit einer Zeile pro Stück",
    )
    p_pl.add_argument(
        "-i",
        "--inventar",
        type=Path,
        default=DEFAULT_INVENTAR,
        help="Inventardatei",
    )
    p_pl.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Ziel-.m3u/.m3u8 (Standard: FooBar_Playlists/<Textlistenname>.m3u8)",
    )
    p_pl.add_argument(
        "--prefix",
        default="primary",
        help="Bibliothekspräfix in der Playliste (Standard: primary)",
    )
    p_pl.add_argument(
        "--min-score",
        type=float,
        default=0.55,
        help="Mindest-Score für einen Treffer (0–1)",
    )
    p_pl.add_argument(
        "--report",
        type=Path,
        help="Optionale Report-Datei für Nicht-Treffer / Alternativen",
    )
    p_pl.add_argument(
        "--dry-run",
        action="store_true",
        help="Nur matchen und Report ausgeben, keine Playliste schreiben",
    )

    return parser


def cmd_inventar(args: argparse.Namespace) -> int:
    root: Path = args.root
    print(f"Scanne Inventar unter: {root.resolve()}")
    t0 = time.perf_counter()
    inv = scan_inventory(root, progress_every=args.progress_every)
    save_inventory(inv, args.output)
    dt = time.perf_counter() - t0
    print(f"Fertig: {inv.track_count} Titel in {dt:.1f}s")
    print(f"Gespeichert: {args.output.resolve()}")
    return 0


def cmd_suche(args: argparse.Namespace) -> int:
    inv = load_inventory(args.inventar)
    hits = filter_tracks(inv.tracks, args.query)[: args.limit]
    print(f"{len(hits)} Treffer (Anzeige max. {args.limit}) – Inventar: {inv.track_count} Titel")
    for track in hits:
        print(f"  {track.rel}")
    return 0


def _default_playlist_path(textliste: Path) -> Path:
    name = textliste.stem.strip() or "playlist"
    # Windows-Dateiname säubern
    safe = "".join(ch if ch not in '<>:"/\\|?*' else "_" for ch in name)
    return DEFAULT_PLAYLIST_DIR / f"{safe}.m3u8"


def cmd_playlist(args: argparse.Namespace) -> int:
    if not args.textliste.is_file():
        print(f"Textliste nicht gefunden: {args.textliste}", file=sys.stderr)
        return 1
    if not args.inventar.is_file():
        print(
            f"Inventar fehlt: {args.inventar}\n"
            f"Zuerst: python textliste2playlist.py inventar --root J:\\",
            file=sys.stderr,
        )
        return 1

    inv = load_inventory(args.inventar)
    lines = read_text_lines(args.textliste)
    matched: list = []
    report_lines: list[str] = []
    missing = 0
    skipped = 0

    print(f"Inventar: {inv.track_count} Titel aus {inv.root}")
    print(f"Textliste: {args.textliste} ({len(lines)} Zeilen)")
    print("Baue Suchindex …")
    index = build_token_index(inv.tracks)

    for raw in lines:
        if not raw.strip():
            skipped += 1
            continue
        result = match_line(raw, inv.tracks, min_score=args.min_score, index=index)
        if result is None:
            skipped += 1
            continue
        if result.track is None:
            missing += 1
            report_lines.append(f"FEHLT\t{result.score:.3f}\t{result.line.raw}")
            for score, cand in result.candidates[:3]:
                report_lines.append(f"  ALT\t{score:.3f}\t{cand.rel}")
            print(f"  [?] {result.line.raw}")
            continue

        matched.append(result.track)
        report_lines.append(
            f"OK\t{result.score:.3f}\t{result.line.raw}\t->\t{result.track.rel}"
        )
        print(f"  [+] ({result.score:.2f}) {result.line.title} -> {result.track.name}")

    out = args.output or _default_playlist_path(args.textliste)
    if not args.dry_run:
        write_m3u(matched, out, library_prefix=args.prefix)
        print(f"\nPlayliste geschrieben: {out.resolve()}")
        print(f"Einträge: {len(matched)} | ohne Treffer: {missing} | leer/Kommentar: {skipped}")
    else:
        print(f"\nDry-Run: {len(matched)} Treffer, {missing} ohne Match")

    report_path = args.report
    if report_path is None and not args.dry_run:
        report_path = out.with_suffix(out.suffix + ".report.txt")
    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
        print(f"Report: {report_path.resolve()}")

    return 0 if missing == 0 else 2


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "inventar":
        return cmd_inventar(args)
    if args.command == "suche":
        return cmd_suche(args)
    if args.command == "playlist":
        return cmd_playlist(args)
    parser.error(f"Unbekanntes Kommando: {args.command}")
    return 2
