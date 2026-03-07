from __future__ import annotations

from abc import ABC, abstractmethod

from file_compare.core.models import FileEntry


class Criterion(ABC):
    """Abstract base class for comparison criteria."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable criterion name."""

    @abstractmethod
    def matches(self, left: FileEntry, right: FileEntry) -> bool:
        """Return True when entries match."""


class ByName(Criterion):
    @property
    def name(self) -> str:
        return "Name"

    def matches(self, left: FileEntry, right: FileEntry) -> bool:
        return left.name == right.name


class BySize(Criterion):
    @property
    def name(self) -> str:
        return "Size"

    def matches(self, left: FileEntry, right: FileEntry) -> bool:
        return left.size == right.size


class ByModifiedDate(Criterion):
    @property
    def name(self) -> str:
        return "Date"

    def matches(self, left: FileEntry, right: FileEntry) -> bool:
        return left.modified_time == right.modified_time
