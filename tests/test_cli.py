from pathlib import Path

import pytest

from file_compare.cli.main import parse_context


def test_parse_context_returns_none_without_dirs():
    assert parse_context([]) is None


def test_parse_context_builds_explicit_file_context():
    context = parse_context(
        [
            "--left-file",
            r"D:\Left\a.txt",
            "--right-file",
            r"D:\Right\b.txt",
            "--size",
        ]
    )

    assert context is not None
    assert context.left_dir == Path(r"D:\Left")
    assert context.right_dir == Path(r"D:\Right")
    assert context.left_file == Path(r"D:\Left\a.txt")
    assert context.right_file == Path(r"D:\Right\b.txt")
    assert context.options.compare_name is False
    assert context.options.compare_size is True


def test_parse_context_builds_selection_context(tmp_path=None):
    del tmp_path
    context = parse_context(
        [
            "--left-dir",
            "left",
            "--right-dir",
            "right",
            "--recursive",
            "--size",
            "--left-selected",
            "a.txt",
            "--right-selected",
            "a.txt",
        ]
    )

    assert context is not None
    assert context.left_dir == Path("left")
    assert context.right_dir == Path("right")
    assert context.options.recursive is True
    assert context.options.compare_size is True
    assert context.left_selected == (Path("a.txt"),)
    assert context.right_selected == (Path("a.txt"),)


def test_parse_context_reads_selection_list(temp_dir):
    left_list = temp_dir / "left.txt"
    right_list = temp_dir / "right.txt"
    left_list.write_text("a.txt\nsub/b.txt\n", encoding="utf-8")
    right_list.write_text("a.txt\nsub/b.txt\n", encoding="utf-8")

    context = parse_context(
        [
            "--left-dir",
            "left",
            "--right-dir",
            "right",
            "--left-selected-list",
            str(left_list),
            "--right-selected-list",
            str(right_list),
        ]
    )

    assert context is not None
    assert context.left_selected == (Path("a.txt"), Path("sub/b.txt"))
    assert context.options.compare_name is True


def test_parse_context_rejects_one_sided_selection():
    with pytest.raises(SystemExit):
        parse_context(
            [
                "--left-dir",
                "left",
                "--right-dir",
                "right",
                "--left-selected",
                "a.txt",
            ]
        )


def test_parse_context_rejects_mixed_file_and_directory_modes():
    with pytest.raises(SystemExit):
        parse_context(
            [
                "--left-file",
                r"D:\Left\a.txt",
                "--right-file",
                r"D:\Right\b.txt",
                "--left-dir",
                r"D:\Left",
                "--right-dir",
                r"D:\Right",
            ]
        )
