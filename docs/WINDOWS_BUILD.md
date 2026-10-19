# Windows build and first test

## Build and download

1. Push these build files to GitHub. For the manual button to appear, the workflow
   must be on the default branch. Open **Actions → Build Windows application →
   Run workflow**, select the branch and start it. Relevant pushes and pull
   requests also build automatically.
2. Wait for the Windows job to succeed. Open its run summary and download
   **Rotary-Axis-CAM-3-Axis-Windows-x64** under **Artifacts** (sign in to GitHub).
   Artifacts are retained for 30 days, subject to repository policy.
3. Extract the downloaded artifact ZIP, then extract the application ZIP inside
   it. Keep the entire **Rotary Axis CAM - 3 Axis** folder, including `_internal`.
4. On a Windows x64 computer, open **Rotary Axis CAM - 3 Axis.exe** from that
   folder. Python is bundled; no separate Python installation is required.

## First Windows test

Use a writable test folder and a known STL. Confirm the window opens and the
model renders; orbit/zoom, alignment, visibility and shading work. Generate
roughing and finishing, inspect the displayed paths and G-code, then repeat with
roughing disabled. Test both XAZ and YAZ output and a folder path containing
spaces. Compare output against the source application using the same STL and
settings. Record the workflow run, Windows version and any error messages.
These are offline acceptance checks; do not run generated code on machinery as
part of the packaging test. A successful CI build alone does not establish that
VTK rendering works on the target computer's graphics hardware.

If startup fails, retain the entire extracted folder and report the traceback
or screenshot. Dependency versions used by that build are in
`build-dependencies.txt` beside the executable. This first build is unsigned;
there is no installer or automatic GitHub Release publication.

## Entry point, dependencies and resources

The entry point is `Rotary Axis CAM - 3 Axis/Rotary_Axis_CAM_3_Axis.py`.
It calls `Brian_Rotary_CAM.main()`, which loads `brian_rotary_cam.interface.run()`.
No CAM, UI or application Python files are changed for packaging.

| Package | Purpose |
| --- | --- |
| NumPy | Numerical arrays and geometry calculations |
| trimesh | STL loading and mesh preparation |
| PyVista | Model and toolpath visualization |
| VTK (`vtk`, imports as `vtkmodules`) | Native rendering, geometry and STL readers |
| pyvistaqt | PyVista QtInteractor integration |
| PySide6 | Existing Qt GUI binding and Windows platform plugins |
| QtPy | Qt binding abstraction used by pyvistaqt |
| PyInstaller 6.x | Build tool; embeds the Python runtime |
| pyinstaller-hooks-contrib | Packaging hooks for third-party dependencies |

The original `requirements.txt` and `requirements-brian.txt` list the five
source dependencies and PyInstaller. `requirements-windows-build.txt` includes
the former and explicitly adds VTK, QtPy and build hook requirements. Pip
resolves transitive dependencies (for example PySide6's Essentials, Addons and
shiboken6, plus PyVista plotting/IO dependencies). The complete resolved Python
dependency list is saved with every build via `pip freeze`; versions remain
unpinned pending the first Windows test. Standard-library imports need no pip
packages. The existing unittest suite requires no separate test framework.

Python 3.11 x64 is the initial Windows target. Source documentation mentions
3.12, but the application contains no identified requirement for 3.12.
`Brian_Rotary_CAM.spec` uses the public launcher and collects PyVista, pyvistaqt,
VTK modules/native libraries and trimesh resources, with PyInstaller's Qt hooks
collecting PySide6 libraries and platform plugins. Alternative Qt bindings are
excluded. No external icons, bundled models or other application data files are
required: STL input and generated G-code are selected/written by the user. The
application README is included as documentation.

The spec encodes `--onedir` using `EXE(exclude_binaries=True)` and `COLLECT`.
Do not add `--onedir` when building from a spec; packaging options are already
encoded there. On Windows, from the application subdirectory:

```powershell
python -m pip install -r requirements-windows-build.txt
python -m PyInstaller --clean --noconfirm Brian_Rotary_CAM.spec
```

The result is `dist/Rotary Axis CAM - 3 Axis/`. The workflow archives that entire
directory using Python's ZIP64-capable zipfile support through shutil.

References: [PyInstaller spec files](https://pyinstaller.org/en/stable/spec-files.html)
and [GitHub workflow artifacts](https://docs.github.com/en/actions/tutorials/store-and-share-data).
