# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=[],
    datas=[('gui', 'gui'), ('indexer', 'indexer'), ('search', 'search'), ('utils', 'utils'), ('cli', 'cli')],
    hiddenimports=['customtkinter', 'CTkTable', 'whoosh', 'whoosh.qparser', 'whoosh.scoring', 'whoosh.sorting', 'whoosh.query', 'whoosh.analysis', 'pdfplumber', 'docx', 'openpyxl', 'pptx', 'bs4', 'lxml', 'yaml'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='FileIndexer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
