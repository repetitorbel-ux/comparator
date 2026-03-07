from pathlib import Path

from file_compare.core.criteria import ByModifiedDate, ByName, BySize
from file_compare.core.models import FileEntry

def make_entry(name, size=10, time=100.0):
    p = Path(name)
    return FileEntry(p, p, size, time, time)

def test_by_name():
    c = ByName()
    e1 = make_entry("a.txt")
    e2 = make_entry("a.txt", size=20)
    assert c.matches(e1, e2) is True

    e3 = make_entry("b.txt")
    assert c.matches(e1, e3) is False

def test_by_size():
    c = BySize()
    e1 = make_entry("a", size=100)
    e2 = make_entry("b", size=100)
    e3 = make_entry("c", size=200)
    assert c.matches(e1, e2) is True
    assert c.matches(e1, e3) is False

def test_by_date():
    c = ByModifiedDate()
    e1 = make_entry("a", time=100.0)
    e2 = make_entry("b", time=100.0)
    e3 = make_entry("c", time=200.0)
    assert c.matches(e1, e2) is True
    assert c.matches(e1, e3) is False
