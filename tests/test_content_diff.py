from file_compare.core.content_diff import (
    DiffKind,
    build_side_by_side_rows,
    compute_token_spans,
    read_editable_text,
    read_text_lines,
)


def test_read_text_lines_supports_utf8(temp_dir):
    path = temp_dir / "sample.txt"
    path.write_text("one\ntwo\n", encoding="utf-8")

    assert read_text_lines(path) == ["one", "two"]


def test_read_editable_text_supports_utf8(temp_dir):
    path = temp_dir / "editable.txt"
    path.write_text("left\nright\n", encoding="utf-8")

    assert read_editable_text(path) == "left\nright\n"


def test_read_editable_text_rejects_utf16(temp_dir):
    path = temp_dir / "utf16.txt"
    path.write_text("hello", encoding="utf-16")

    try:
        read_editable_text(path)
    except ValueError as exc:
        assert str(exc) == "Only UTF-8 text files can be edited."
    else:  # pragma: no cover - defensive
        raise AssertionError("Expected ValueError for utf-16 file")


def test_read_editable_text_rejects_binary(temp_dir):
    path = temp_dir / "binary.bin"
    path.write_bytes(b"\x00\x01\x02")

    try:
        read_editable_text(path)
    except ValueError as exc:
        assert str(exc) == "Binary files are read-only in edit mode."
    else:  # pragma: no cover - defensive
        raise AssertionError("Expected ValueError for binary file")


def test_build_side_by_side_rows_marks_replace_insert_and_delete(temp_dir):
    left = temp_dir / "left.txt"
    right = temp_dir / "right.txt"
    left.write_text("same\nold\nleft-only\n", encoding="utf-8")
    right.write_text("same\nnew\nright-only\n", encoding="utf-8")

    rows = build_side_by_side_rows(left, right)

    assert [row.kind for row in rows] == [
        DiffKind.EQUAL,
        DiffKind.REPLACE,
        DiffKind.REPLACE,
    ]
    assert rows[1].left_text == "old"
    assert rows[1].right_text == "new"
    assert rows[2].left_text == "left-only"
    assert rows[2].right_text == "right-only"


def test_build_side_by_side_rows_handles_unbalanced_replace_block(temp_dir):
    left = temp_dir / "left.txt"
    right = temp_dir / "right.txt"
    left.write_text("same\nremove-me\n", encoding="utf-8")
    right.write_text("same\ninsert-1\ninsert-2\n", encoding="utf-8")

    rows = build_side_by_side_rows(left, right)

    assert [row.kind for row in rows] == [
        DiffKind.EQUAL,
        DiffKind.REPLACE,
        DiffKind.RIGHT_ONLY,
    ]
    assert rows[2].left_line_no is None
    assert rows[2].right_line_no == 3


def test_compute_token_spans_marks_changed_words():
    left_spans, right_spans = compute_token_spans("alpha beta gamma", "alpha delta gamma")

    assert left_spans == ((6, 10),)
    assert right_spans == ((6, 11),)
