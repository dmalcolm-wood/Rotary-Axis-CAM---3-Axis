# PyInstaller one-folder build for Windows.
# Run from the project root: pyinstaller --clean Brian_Rotary_CAM.spec

from pathlib import Path

from PyInstaller.utils.hooks import collect_all

project_dir = Path(SPECPATH)

datas = []
binaries = []
hiddenimports = []

# Include dynamically imported VTK extensions, DLLs and package resources.
# PyInstaller's standard Qt hooks collect PySide6 plugins (including qwindows).
for package in ("pyvista", "pyvistaqt", "vtkmodules", "trimesh"):
    package_datas, package_binaries, package_hidden = collect_all(package)
    datas += package_datas
    binaries += package_binaries
    hiddenimports += package_hidden

# QtPy selects its binding dynamically; bundle the application's existing binding.
hiddenimports += ["PySide6.QtCore", "PySide6.QtGui", "PySide6.QtWidgets"]
datas += [(str(project_dir / "README.md"), ".")]

a = Analysis(
    [str(project_dir / "Rotary_Axis_CAM_3_Axis.py")],
    pathex=[str(project_dir)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "PyQt5", "PyQt6", "PySide2"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Rotary Axis CAM - 3 Axis",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="Rotary Axis CAM - 3 Axis",
)
