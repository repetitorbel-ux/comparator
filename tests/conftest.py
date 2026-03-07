import shutil
import uuid
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a sandbox-friendly temporary directory inside the repo."""
    base_dir = Path.cwd() / "testdata_tmp"
    base_dir.mkdir(exist_ok=True)
    temp_path = base_dir / f"case_{uuid.uuid4().hex}"
    temp_path.mkdir()
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)

@pytest.fixture
def left_dir(temp_dir):
    d = temp_dir / "left"
    d.mkdir()
    return d

@pytest.fixture
def right_dir(temp_dir):
    d = temp_dir / "right"
    d.mkdir()
    return d

@pytest.fixture
def create_file():
    def _create(path: Path, content: str = "test", size: int | None = None):
        path.parent.mkdir(parents=True, exist_ok=True)
        if size is not None:
            path.write_bytes(b"\0" * size)
        else:
            path.write_text(content, encoding="utf-8")
        return path

    return _create
