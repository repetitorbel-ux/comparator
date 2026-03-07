# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


project_root = Path(SPECPATH)


a = Analysis(
    ["file_compare/cli/main.py"],
    pathex=[str(project_root)],
    binaries=[],
    datas=[],
    hiddenimports=["file_compare.gui.main_window"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="FileCompareTC",
    console=False,
)
