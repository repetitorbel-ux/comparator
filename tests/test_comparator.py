from pathlib import Path

from file_compare.core.comparator import Comparator
from file_compare.core.criteria import ByName, BySize
from file_compare.core.models import ComparisonCategory, FileEntry

def make_entry(rel_path, size=10):
    p = Path("/tmp") / rel_path
    rp = Path(rel_path)
    return FileEntry(p, rp, size, 0, 0)

def test_compare_match():
    left = [make_entry("a.txt", 100)]
    right = [make_entry("a.txt", 100)]
    
    # By default matching path + empty criteria = MATCH? 
    # Logic in comparator: checks criteria. If none, MATCH. 
    # But usually we have ByName. ByName checks name match.
    
    comp = Comparator([ByName(), BySize()])
    results = comp.compare(left, right)
    
    assert len(results) == 1
    assert results[0].category == ComparisonCategory.MATCH

def test_compare_mismatch_size():
    left = [make_entry("a.txt", 100)]
    right = [make_entry("a.txt", 200)]
    
    comp = Comparator([ByName(), BySize()])
    results = comp.compare(left, right)
    
    assert len(results) == 1
    assert results[0].category == ComparisonCategory.MISMATCH
    assert results[0].details["Size"] == "Differs"

def test_compare_left_only():
    left = [make_entry("a.txt")]
    right = []
    
    comp = Comparator([ByName()])
    results = comp.compare(left, right)
    
    assert len(results) == 1
    assert results[0].category == ComparisonCategory.LEFT_ONLY

def test_compare_right_only():
    left = []
    right = [make_entry("b.txt")]
    
    comp = Comparator([ByName()])
    results = comp.compare(left, right)
    
    assert len(results) == 1
    assert results[0].category == ComparisonCategory.RIGHT_ONLY

def test_compare_relative_path_match():
    # Test that files in subfolders match by relative path
    left = [make_entry("sub/a.txt")]
    right = [make_entry("sub/a.txt")]
    
    comp = Comparator([ByName()])
    results = comp.compare(left, right)
    
    assert len(results) == 1
    assert results[0].category == ComparisonCategory.MATCH
