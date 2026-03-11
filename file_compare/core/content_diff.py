from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from enum import Enum, auto
from pathlib import Path
import re


class DiffKind(Enum):
    EQUAL = auto()
    REPLACE = auto()
    LEFT_ONLY = auto()
    RIGHT_ONLY = auto()


@dataclass(frozen=True)
class DiffRow:
    left_line_no: int | None
    left_text: str
    right_line_no: int | None
    right_text: str
    kind: DiffKind
    left_spans: tuple[tuple[int, int], ...] = ()
    right_spans: tuple[tuple[int, int], ...] = ()


@dataclass(frozen=True)
class EditableText:
    text: str
    encoding: str


def read_text_lines(path: Path) -> list[str]:
    return _decode_for_display(path.read_bytes()).splitlines()


def read_editable_text(path: Path) -> str:
    return read_editable_document(path).text


def read_editable_document(path: Path) -> EditableText:
    raw_bytes = path.read_bytes()

    if raw_bytes.startswith(b"\xef\xbb\xbf"):
        encodings = ("utf-8-sig", "utf-8", "cp1251", "cp1252", "latin-1")
    elif raw_bytes.startswith((b"\xff\xfe", b"\xfe\xff")):
        encodings = ("utf-16", "utf-8", "cp1251", "cp1252", "latin-1")
    else:
        if b"\x00" in raw_bytes:
            raise ValueError("Binary files are read-only in edit mode.")
        encodings = ("utf-8", "utf-16", "cp1251", "cp1252", "latin-1")

    for encoding in encodings:
        try:
            content = raw_bytes.decode(encoding)
            normalized = content.replace("\r\n", "\n").replace("\r", "\n")
            return EditableText(text=normalized, encoding=encoding)
        except UnicodeError:
            continue

    raise ValueError("Unable to decode text file for edit mode.")


def build_side_by_side_rows(left_path: Path, right_path: Path) -> list[DiffRow]:
    left_lines = read_text_lines(left_path)
    right_lines = read_text_lines(right_path)
    matcher = SequenceMatcher(a=left_lines, b=right_lines, autojunk=False)

    rows: list[DiffRow] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            rows.extend(
                DiffRow(
                    left_line_no=i1 + offset + 1,
                    left_text=left_lines[i1 + offset],
                    right_line_no=j1 + offset + 1,
                    right_text=right_lines[j1 + offset],
                    kind=DiffKind.EQUAL,
                )
                for offset in range(i2 - i1)
            )
            continue

        if tag == "replace":
            rows.extend(_build_replace_rows(left_lines, right_lines, i1, i2, j1, j2))
            continue

        if tag == "delete":
            rows.extend(
                DiffRow(
                    left_line_no=line_index + 1,
                    left_text=left_lines[line_index],
                    right_line_no=None,
                    right_text="",
                    kind=DiffKind.LEFT_ONLY,
                )
                for line_index in range(i1, i2)
            )
            continue

        if tag == "insert":
            rows.extend(
                DiffRow(
                    left_line_no=None,
                    left_text="",
                    right_line_no=line_index + 1,
                    right_text=right_lines[line_index],
                    kind=DiffKind.RIGHT_ONLY,
                )
                for line_index in range(j1, j2)
            )

    return rows


def _build_replace_rows(
    left_lines: list[str],
    right_lines: list[str],
    i1: int,
    i2: int,
    j1: int,
    j2: int,
) -> list[DiffRow]:
    rows: list[DiffRow] = []
    for offset in range(max(i2 - i1, j2 - j1)):
        left_index = i1 + offset
        right_index = j1 + offset
        has_left = left_index < i2
        has_right = right_index < j2

        if has_left and has_right:
            kind = DiffKind.REPLACE
            left_spans, right_spans = compute_token_spans(
                left_lines[left_index],
                right_lines[right_index],
            )
        elif has_left:
            kind = DiffKind.LEFT_ONLY
            left_spans, right_spans = (), ()
        else:
            kind = DiffKind.RIGHT_ONLY
            left_spans, right_spans = (), ()

        rows.append(
            DiffRow(
                left_line_no=left_index + 1 if has_left else None,
                left_text=left_lines[left_index] if has_left else "",
                right_line_no=right_index + 1 if has_right else None,
                right_text=right_lines[right_index] if has_right else "",
                kind=kind,
                left_spans=left_spans,
                right_spans=right_spans,
            )
        )

    return rows


def compute_token_spans(left_text: str, right_text: str) -> tuple[tuple[tuple[int, int], ...], tuple[tuple[int, int], ...]]:
    left_tokens = tokenize_with_spans(left_text)
    right_tokens = tokenize_with_spans(right_text)
    matcher = SequenceMatcher(
        a=[token for token, _, _ in left_tokens],
        b=[token for token, _, _ in right_tokens],
        autojunk=False,
    )

    left_spans: list[tuple[int, int]] = []
    right_spans: list[tuple[int, int]] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        left_spans.extend((start, end) for _, start, end in left_tokens[i1:i2] if end > start)
        right_spans.extend((start, end) for _, start, end in right_tokens[j1:j2] if end > start)

    return tuple(_merge_spans(left_spans)), tuple(_merge_spans(right_spans))


def tokenize_with_spans(text: str) -> list[tuple[str, int, int]]:
    tokens: list[tuple[str, int, int]] = []
    for match in re.finditer(r"\s+|\w+|[^\w\s]+", text):
        tokens.append((match.group(0), match.start(), match.end()))
    if not tokens and text == "":
        return []
    return tokens


def _merge_spans(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not spans:
        return []

    ordered = sorted(spans)
    merged = [ordered[0]]
    for start, end in ordered[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
            continue
        merged.append((start, end))
    return merged


def _decode_for_display(raw_bytes: bytes) -> str:
    if raw_bytes.startswith((b"\xff\xfe", b"\xfe\xff")):
        encodings = ("utf-16", "utf-8-sig", "utf-8")
    else:
        encodings = ("utf-8-sig", "utf-8", "utf-16")

    for encoding in encodings:
        try:
            return raw_bytes.decode(encoding)
        except UnicodeError:
            continue

    return raw_bytes.decode("latin-1", errors="replace")
