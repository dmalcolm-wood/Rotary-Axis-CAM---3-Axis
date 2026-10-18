# Rotary Axis CAM - 3 Axis v1.5 with PyVista visualizer

This clean repository contains Brian's current rotary CAM application.

Version 1.5 includes:

- selectable XAZ or YAZ rotary alignment;
- STL and de-rotated roughing/finishing toolpath visualization using PyVista;
- roughing and finishing G-code text display;
- an introductory stepped entry for finishing with a tapered cutter.

## Windows build

GitHub Actions builds the application automatically after files are pushed to
the `main` branch. The workflow also checks that it is building version 1.5.

Download the artifact named `Rotary-Axis-CAM-3-Axis-v1.5-Windows`, extract it on the
Windows PC, and keep the complete extracted folder together. Run
`Rotary Axis CAM - 3 Axis.exe`; the adjacent `_internal` folder is required.

See `BRIAN_BUILD.md` for local development and Windows build instructions.
