from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

CATEGORIES = {
    "images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"},
    "documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".odt"},
    "spreadsheets": {".csv", ".xls", ".xlsx", ".ods"},
    "audio": {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg"},
    "video": {".mp4", ".mov", ".mkv", ".avi", ".webm"},
    "archives": {".zip", ".7z", ".rar", ".tar", ".gz"},
    "code": {".py", ".js", ".ts", ".html", ".css", ".json", ".yaml", ".yml"},
}

@dataclass(frozen=True)
class Move:
    source: Path
    target: Path


def folder_for(path: Path, mode: str) -> str:
    if mode == "extension":
        return path.suffix.lower().lstrip(".") or "no-extension"
    if mode == "date":
        return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m")
    suffix = path.suffix.lower()
    for category, suffixes in CATEGORIES.items():
        if suffix in suffixes:
            return category
    return "other"


def available_target(target: Path, reserved: set[Path]) -> Path:
    candidate = target
    counter = 1
    while candidate.exists() or candidate in reserved:
        candidate = target.with_name(f"{target.stem} ({counter}){target.suffix}")
        counter += 1
    return candidate


def build_plan(directory: Path, mode: str = "category", include_hidden: bool = False) -> list[Move]:
    directory = directory.expanduser().resolve()
    if not directory.is_dir():
        raise ValueError(f"Not a directory: {directory}")
    reserved: set[Path] = set()
    moves: list[Move] = []
    for source in sorted(directory.iterdir(), key=lambda p: p.name.lower()):
        if not source.is_file() or source.name == ".organizer-manifest.json":
            continue
        if not include_hidden and source.name.startswith("."):
            continue
        target = directory / folder_for(source, mode) / source.name
        target = available_target(target, reserved)
        reserved.add(target)
        moves.append(Move(source, target))
    return moves


def apply_plan(moves: list[Move], manifest: Path) -> None:
    completed: list[Move] = []
    try:
        for move in moves:
            move.target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(move.source), str(move.target))
            completed.append(move)
    except Exception:
        for move in reversed(completed):
            if move.target.exists() and not move.source.exists():
                shutil.move(str(move.target), str(move.source))
        raise
    manifest.write_text(json.dumps([
        {"source": str(move.source), "target": str(move.target)} for move in moves
    ], indent=2), encoding="utf-8")


def undo(manifest: Path) -> int:
    records = json.loads(manifest.read_text(encoding="utf-8"))
    restored = 0
    for item in reversed(records):
        source, target = Path(item["source"]), Path(item["target"])
        if not target.exists():
            raise FileNotFoundError(f"Cannot undo; missing: {target}")
        if source.exists():
            raise FileExistsError(f"Cannot undo; original path exists: {source}")
        source.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(target), str(source))
        restored += 1
    manifest.unlink(missing_ok=True)
    return restored


def main() -> None:
    parser = argparse.ArgumentParser(description="Safely preview, organize, and undo folder cleanup.")
    parser.add_argument("directory", nargs="?", default=".")
    parser.add_argument("--mode", choices=("category", "extension", "date"), default="category")
    parser.add_argument("--include-hidden", action="store_true")
    parser.add_argument("--apply", action="store_true", help="Apply the previewed moves")
    parser.add_argument("--undo", action="store_true", help="Undo the previous applied plan")
    args = parser.parse_args()
    directory = Path(args.directory).expanduser().resolve()
    manifest = directory / ".organizer-manifest.json"
    if args.undo:
        print(f"Restored {undo(manifest)} files.")
        return
    moves = build_plan(directory, args.mode, args.include_hidden)
    if not moves:
        print("No files need organizing.")
        return
    for move in moves:
        print(f"{move.source.name} -> {move.target.relative_to(directory)}")
    if args.apply:
        apply_plan(moves, manifest)
        print(f"Moved {len(moves)} files. Undo manifest: {manifest}")
    else:
        print("Preview only. Add --apply to move files.")

if __name__ == "__main__":
    main()
