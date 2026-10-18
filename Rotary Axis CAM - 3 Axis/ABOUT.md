# About Rotary Axis CAM - 3 Axis

Formerly Brian Rotary CAM, this is the modular v1.7 application renamed Rotary Axis CAM - 3 Axis.

- Selectable XAZ or YAZ alignment: one linear axial axis, radial Z and rotary A.
- STL-based roughing and finishing toolpath generation.
- PyVista display of the model and de-rotated roughing/finishing paths.
- Roughing and finishing G-code text views.
- Stepped finishing entry for tapered cutters.
- Windows application packaging with PyInstaller and GitHub Actions.

The internal brian_rotary_cam package and compatibility launcher names are retained to preserve imports. The visible application and Windows build output use the new name.

- Model-axis alignment to X, automatic long-axis estimation, manual rotation adjustments and centring on the rotary axis, shared by preview and CAM.

- Optional finishing of either free end face down to the finishing minimum Z, with a tapered-cutter warning.
