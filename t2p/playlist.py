"""m3u / m3u8 Playlisten schreiben (foobar2000-kompatibel)."""

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
    Relativer Eintrag wie in bestehenden FooBar-Playlisten:
    primary/MP3/Tango/...
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
