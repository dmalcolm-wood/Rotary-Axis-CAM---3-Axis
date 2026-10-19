# Rotary Axis CAM - 3 Axis — development and Windows build

Brian launches `Brian_Rotary_CAM.py` while developing from source. The program
remains one application even though the CAM engine, G-code reader, PyVista
viewer, and interface are separate modules.

## Run from source

```bash
python -m pip install -r requirements-brian.txt
python Brian_Rotary_CAM.py
```

## Build the Windows application

Build on a Windows computer; PyInstaller does not cross-compile a Windows `.exe`
from macOS. Clone or download the GitHub repository, open Command Prompt in the
project directory, and run:

```bat
build_brian_windows.bat
```

The distributable folder will be:

```text
dist\Rotary Axis CAM - 3 Axis\
```

Copy that entire folder to Brian's computer. The folder build is recommended
because Qt and VTK are large native libraries and are more reliable in this
form than a one-file executable.

For GitHub Actions builds and first Windows acceptance testing, see
[Windows build instructions](../docs/WINDOWS_BUILD.md).
