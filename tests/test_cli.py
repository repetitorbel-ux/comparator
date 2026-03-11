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
    with pytest.raises(ValueError):
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


def test_parse_context_prefers_directory_mode_for_mixed_args_without_selections(temp_dir):
    left_dir = temp_dir / "left"
    right_dir = temp_dir / "right"
    left_dir.mkdir()
    right_dir.mkdir()
    left_file = left_dir / "a.txt"
    right_file = right_dir / "b.txt"
    left_file.write_text("a", encoding="utf-8")
    right_file.write_text("b", encoding="utf-8")

    context = parse_context(
        [
            "--left-dir",
            str(left_dir),
            "--right-dir",
            str(right_dir),
            "--left-file",
            str(left_file),
            "--right-file",
            str(right_file),
        ]
    )

    assert context is not None
    assert context.left_file is None
    assert context.right_file is None
    assert context.left_dir == left_dir
    assert context.right_dir == right_dir
    assert context.options.compare_name is True


def test_parse_context_falls_back_from_invalid_dir_tokens_to_file_parents(temp_dir):
    left_dir = temp_dir / "left"
    right_dir = temp_dir / "right"
    left_dir.mkdir()
    right_dir.mkdir()
    left_file = left_dir / "knopka.md"
    right_file = right_dir / "plan.md"
    left_file.write_text("same", encoding="utf-8")
    right_file.write_text("same", encoding="utf-8")

    context = parse_context(
        [
            "--left-dir",
            "Q",
            "--right-dir",
            "W",
            "--left-file",
            str(left_file),
            "--right-file",
            str(right_file),
            "--size",
            "--date",
        ]
    )

    assert context is not None
    assert context.left_dir == left_dir
    assert context.right_dir == right_dir
    assert context.left_file is None
    assert context.right_file is None


def test_parse_context_normalizes_quoted_directory_values():
    context = parse_context(
        [
            "--left-dir",
            '"left"',
            "--right-dir",
            "'right'",
        ]
    )

    assert context is not None
    assert context.left_dir == Path("left")
    assert context.right_dir == Path("right")


def test_parse_context_prefers_selected_mode_over_file_mode_for_mixed_args(temp_dir):
    left_dir = temp_dir / "left"
    right_dir = temp_dir / "right"
    left_dir.mkdir()
    right_dir.mkdir()
    left_file = left_dir / "knopka.md"
    right_file = right_dir / "plan.md"
    left_file.write_text("same", encoding="utf-8")
    right_file.write_text("diff", encoding="utf-8")
    (left_dir / "scema.md").write_text("left", encoding="utf-8")

    left_list = temp_dir / "left.txt"
    right_list = temp_dir / "right.txt"
    left_list.write_text("knopka.md\nscema.md\n", encoding="utf-8")
    right_list.write_text("knopka.md\nPLAN-file-compare.md\n", encoding="utf-8")

    context = parse_context(
        [
            "--left-dir",
            str(left_dir),
            "--right-dir",
            str(right_dir),
            "--left-file",
            str(left_file),
            "--right-file",
            str(right_file),
            "--left-selected-list",
            str(left_list),
            "--right-selected-list",
            str(right_list),
        ]
    )

    assert context is not None
    assert context.left_file is None
    assert context.right_file is None
    assert context.left_selected == (Path("knopka.md"), Path("scema.md"))
    assert context.right_selected == (Path("knopka.md"), Path("PLAN-file-compare.md"))
    assert context.options.compare_name is True


def test_parse_context_falls_back_to_directory_mode_when_file_args_are_directories(temp_dir):
    left_dir = temp_dir / "left"
    right_dir = temp_dir / "right"
    left_dir.mkdir()
    right_dir.mkdir()

    context = parse_context(
        [
            "--left-file",
            str(left_dir),
            "--right-file",
            str(right_dir),
            "--size",
            "--date",
        ]
    )

    assert context is not None
    assert context.left_dir == left_dir
    assert context.right_dir == right_dir
    assert context.left_file is None
    assert context.right_file is None
    assert context.options.compare_name is True
    assert context.options.compare_size is True
    assert context.options.compare_date is True


def test_parse_context_trims_embedded_switches_in_path_value(temp_dir):
    left_file = temp_dir / "left.txt"
    right_file = temp_dir / "right.txt"
    left_file.write_text("left", encoding="utf-8")
    right_file.write_text("right", encoding="utf-8")

    context = parse_context(
        [
            "--left-file",
            str(left_file),
            "--right-file",
            f'{right_file}" --size --date',
        ]
    )

    assert context is not None
    assert context.left_file == left_file
    assert context.right_file == right_file


def test_parse_context_repairs_swallowed_cli_switches_from_tc_directory_values(temp_dir):
    left_dir = temp_dir / "left"
    right_dir = temp_dir / "right"
    left_dir.mkdir()
    right_dir.mkdir()

    # Simulates a broken TC argv token when a quoted path ends with "\" and swallows next switches.
    swallowed_token = f'{left_dir}\\ --right-file {right_dir}\\ --size --date'
    context = parse_context(["--left-file", swallowed_token])

    assert context is not None
    assert context.left_dir == left_dir
    assert context.right_dir == right_dir
    assert context.left_file is None
    assert context.right_file is None
    assert context.options.compare_name is True
    assert context.options.compare_size is True
    assert context.options.compare_date is True

def test_parse_context_uses_directory_file_args_when_dir_tokens_are_invalid(temp_dir):
    root = temp_dir / "root"
    left_dir = root / "1"
    right_dir = root / "2"
    left_dir.mkdir(parents=True)
    right_dir.mkdir(parents=True)

    context = parse_context(
        [
            "--left-dir",
            "Q",
            "--right-dir",
            "W",
            "--left-file",
            str(left_dir),
            "--right-file",
            str(right_dir),
        ]
    )

    assert context is not None
    assert context.left_dir == left_dir
    assert context.right_dir == right_dir
    assert context.left_file is None
    assert context.right_file is None
    assert context.options.compare_name is True
