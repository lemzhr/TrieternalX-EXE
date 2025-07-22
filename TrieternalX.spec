# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['TrieternalX.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('src/TrieternalX.ico', '.'),
        ('src/TrieternalX.gif', '.'),
    ],
    hiddenimports=[
        'cv2', 'mediapipe', 'numpy', 'screen_brightness_control',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TrieternalX',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='src/TrieternalX.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TrieternalX',
)
