from pathlib import Path

import pytest

from file_compare.core.scanner import resolve_selected_path, scan_directory, scan_selected_paths

def test_scan_empty(left_dir):
    entries = scan_directory(left_dir)
    assert len(entries) == 0

def test_scan_flat(left_dir, create_file):
    create_file(left_dir / "a.txt")
    create_file(left_dir / "b.txt")
    entries = scan_directory(left_dir)
    assert len(entries) == 2
    names = {e.name for e in entries}
    assert names == {"a.txt", "b.txt"}

def test_scan_recursive_off(left_dir, create_file):
    create_file(left_dir / "sub" / "c.txt") # Should be ignored
    create_file(left_dir / "root.txt")
    
    entries = scan_directory(left_dir, recursive=False)
    assert len(entries) == 1
    assert entries[0].name == "root.txt"

def test_scan_recursive_on(left_dir, create_file):
    create_file(left_dir / "sub" / "c.txt")
    create_file(left_dir / "root.txt")
    
    entries = scan_directory(left_dir, recursive=True)
    assert len(entries) == 2
    rel_paths = {str(e.relative_path).replace("\\", "/") for e in entries} # normalize sep
    assert "sub/c.txt" in rel_paths
    assert "root.txt" in rel_paths


def test_scan_selected_paths(left_dir, create_file):
    create_file(left_dir / "sub" / "c.txt")
    create_file(left_dir / "root.txt")

    entries = scan_selected_paths(left_dir, [Path("sub/c.txt"), Path("root.txt")])

    assert len(entries) == 2
    rel_paths = {str(entry.relative_path).replace("\\", "/") for entry in entries}
    assert rel_paths == {"sub/c.txt", "root.txt"}


def test_scan_selected_directory_recursive(left_dir, create_file):
    create_file(left_dir / "sub" / "c.txt")
    create_file(left_dir / "sub" / "nested" / "d.txt")

    entries = scan_selected_paths(left_dir, [Path("sub")], recursive=True)

    rel_paths = {str(entry.relative_path).replace("\\", "/") for entry in entries}
    assert rel_paths == {"sub/c.txt", "sub/nested/d.txt"}


def test_resolve_selected_path_rejects_outside_root(left_dir):
    with pytest.raises(ValueError):
        resolve_selected_path(left_dir, Path("..") / "other.txt")
