from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any


FILE_PAIR_RELATIVE_PATH = Path("__selected_pair__")


@dataclass(frozen=True)
class FileEntry:
    """Represents a file inside a scanned directory tree."""

    path: Path
    relative_path: Path
    size: int
    created_time: float
    modified_time: float

    @property
    def name(self) -> str:
        return self.path.name


class ComparisonCategory(Enum):
    MATCH = auto()
    LEFT_ONLY = auto()
    RIGHT_ONLY = auto()
    MISMATCH = auto()


@dataclass
class ComparisonResult:
    """Comparison outcome for a single relative path."""

    left: FileEntry | None = None
    right: FileEntry | None = None
    category: ComparisonCategory = ComparisonCategory.MISMATCH
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def name(self) -> str:
        if self.left:
            return self.left.name
        if self.right:
            return self.right.name
        return "Unknown"

    @property
    def relative_path(self) -> Path:
        if (
            self.left
            and self.right
            and self.left.relative_path == FILE_PAIR_RELATIVE_PATH
            and self.right.relative_path == FILE_PAIR_RELATIVE_PATH
        ):
            if self.left.name == self.right.name:
                return Path(self.left.name)
            return Path(f"{self.left.name} vs {self.right.name}")

        if self.left:
            return self.left.relative_path
        if self.right:
            return self.right.relative_path
        return Path(".")
