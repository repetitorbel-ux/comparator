from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from file_compare.core.models import FileEntry


def scan_directory(path: Path, recursive: bool = False) -> list[FileEntry]:
    """Scan a directory and return all files below it."""

    entries: list[FileEntry] = []
    if not path.exists() or not path.is_dir():
        return entries

    if recursive:
        for root, _, files in os.walk(path):
            for file_name in files:
                file_path = Path(root) / file_name
                entry = _build_entry(file_path, path)
                if entry is not None:
                    entries.append(entry)
        return entries

    try:
        with os.scandir(path) as iterator:
            for dir_entry in iterator:
                if not dir_entry.is_file():
                    continue
                entry = _build_entry(Path(dir_entry.path), path)
                if entry is not None:
                    entries.append(entry)
    except OSError:
        return entries

    return entries


def scan_selected_paths(
    root_dir: Path,
    selected_paths: Iterable[str | Path],
    recursive: bool = False,
) -> list[FileEntry]:
    """Scan selected files or directories relative to a panel root."""

    entries: list[FileEntry] = []
    seen_files: set[Path] = set()

    for raw_path in selected_paths:
        selected_path = resolve_selected_path(root_dir, raw_path)
        for file_path in iter_selected_files(selected_path, recursive=recursive):
            normalized_file = file_path.resolve()
            if normalized_file in seen_files:
                continue
            seen_files.add(normalized_file)
            entry = _build_entry(file_path, root_dir)
            if entry is not None:
                entries.append(entry)

    return entries


def resolve_selected_path(root_dir: Path, raw_path: str | Path) -> Path:
    """Resolve a selected path passed from Total Commander or the CLI."""

    candidate = Path(raw_path)
    selected_path = candidate if candidate.is_absolute() else root_dir / candidate

    try:
        normalized_root = root_dir.resolve()
        normalized_selected = selected_path.resolve()
    except OSError as exc:
        raise ValueError(f"Unable to resolve selected path: {raw_path}") from exc

    try:
        normalized_selected.relative_to(normalized_root)
    except ValueError as exc:
        raise ValueError(f"Selected path is outside panel root: {raw_path}") from exc

    if not normalized_selected.exists():
        raise ValueError(f"Selected path does not exist: {raw_path}")

    return normalized_selected


def iter_selected_files(path: Path, recursive: bool = False) -> list[Path]:
    """Expand one selected path into concrete files to compare."""

    if path.is_file():
        return [path]

    if not path.is_dir():
        return []

    if recursive:
        files: list[Path] = []
        for root, _, file_names in os.walk(path):
            for file_name in file_names:
                files.append(Path(root) / file_name)
        return files

    try:
        return [child for child in path.iterdir() if child.is_file()]
    except OSError:
        return []


def _build_entry(file_path: Path, root_dir: Path) -> FileEntry | None:
    return build_file_entry(file_path, root_dir=root_dir)


def build_file_entry(
    file_path: Path,
    *,
    root_dir: Path | None = None,
    relative_path: Path | None = None,
) -> FileEntry | None:
    try:
        if relative_path is None:
            if root_dir is None:
                raise ValueError("Either root_dir or relative_path must be provided.")
            relative_path = file_path.relative_to(root_dir)

        stats = file_path.stat()
        return FileEntry(
            path=file_path,
            relative_path=relative_path,
            size=stats.st_size,
            created_time=stats.st_ctime,
            modified_time=stats.st_mtime,
        )
    except (OSError, ValueError):
        return None
