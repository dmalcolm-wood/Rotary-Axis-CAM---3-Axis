# Rotary Axis CAM - 3 Axis

Formerly Brian Rotary CAM, this is the modular v1.7 application renamed Rotary Axis CAM - 3 Axis.

- Selectable XAZ or YAZ alignment: one linear axial axis, radial Z and rotary A.
- STL-based roughing and finishing toolpath generation.
- PyVista display of the model and de-rotated roughing/finishing paths.
- Roughing and finishing G-code text views.
- Stepped finishing entry for tapered cutters.
- Windows application packaging with PyInstaller and GitHub Actions.

The internal brian_rotary_cam package and compatibility launcher names are retained to preserve imports. The visible application and Windows build output use the new name.

## Run from source

Use Python 3.12 with a project-local virtual environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python "Rotary_Axis_CAM_3_Axis.py"
```

On Windows, activate with `.venv\Scripts\activate`. Tkinter-based applications require a Python installation with Tk support.

See [About](ABOUT.md) and [source selection](SOURCE_SELECTION.md). Existing detailed documentation is retained under `docs/` where available.

## Publication status

Prepared locally; not published. Choose a licence before public release, and review ownership of bundled models and examples. Local machining projects and generated outputs are excluded by `.gitignore`; review the staged file list before uploading.

## Centre and align an STL

1. Choose the STL. It initially retains its original placement.
2. Under **Model alignment — preview along X**, select its length direction: **Model Y → X**, **Model Z → X**, or **Keep model X**. For an oblique model, try **Automatic long axis → X (estimate)**.
3. Tick **Centre on rotary axis (Y=0, Z=0)**. This centres the rotated bounding box across the axis, not its centre of mass.
4. Use the X/Y/Z rotation adjustments to refine the orientation or turn the model end-for-end (180° about Y or Z). Adjustments use fixed axes through the aligned model's bounding-box centre, in X, Y, Z order.
5. Inspect the prepared bounds and preview, then generate roughing and finishing files.

The original STL is never rewritten. Preview and CAM use the same loaded geometry and preparation settings. Changing placement clears displayed G-code and toolpaths; previously saved files on disk remain until regeneration overwrites them. **Reset model placement** restores the imported orientation and position. Choose the file again to load external edits.

Automatic alignment estimates the long axis from unique STL vertices. Uneven tessellation or asymmetry can affect this estimate; it does not infer a designed spindle centreline. Nearly equal principal dimensions require manual axis selection. The manual rotations also support models exported at arbitrary angles.

The model preview is always longitudinal along X. **Rotary alignment** independently chooses X/A/Z or Y/A/Z machine output. Centring affects only Y/Z placement; longitudinal G-code zero remains the first cutting section after the cutter-dependent end inset.

## Display and optional roughing (v1.7)

The STL is fully opaque. Cutting paths are plain orange/red lines with uniform width and no endpoint/depth markers. Use the STL visibility checkbox to see paths hidden behind the model.

**Generate roughing toolpath** is checked by default above the roughing settings. Untick it for finishing only: roughing controls are disabled, no roughing surface is sampled, and no roughing file is written or loaded into the preview. Old roughing files on disk are left unchanged. End clearance then uses only the finishing cutter tip radius. Finishing entry layers remain enabled.

### Adjustable surface shading

Use the Surface shading slider above the model view: 0% gives flat colour; 100% increases directional shading and highlights. The default is 70%. The STL remains opaque. The setting survives model/toolpath refreshes in the current session and changes display materials only. Display normals are recomputed on a display copy of the mesh.

## Free-end finishing (v1.8)

Under **Free-end finishing — aligned model X**, independently select the low-X and/or high-X end. Both are off by default. Only select unsupported ends clear of the chuck, tailstock and fixtures. These refer to the prepared model bounds shown in the viewer, including when machine output is Y/A/Z.

Enabled finishing sides sample close to the STL end rather than stopping one ball radius short. After the ordinary finishing traverses, separate end-face passes place the cutter centre one finishing tip radius beyond the selected STL boundary plane and feed radially down to **Finishing → Minimum cutter Z**. A positive ball/tip radius is required. Z=0 reaches the rotary centreline; a positive value leaves the central region uncut. This is flat boundary-plane machining, not contour following of a sculpted or recessed end.

End-face radial depth per layer uses **Entry depth / layer** and the existing finishing A-angle spacing. The cutter retracts above stock before every A index and end-to-end move. Finishing feed applies to radial cuts. The original longitudinal work zero is retained; low-end finishing can generate negative X (or Y). Review travel limits and stock placement. Roughing paths retain their original end inset; end-face cutting is included only in the finishing file.

**Tapered/conical cutter warning:** ball-centre clearance does not establish clearance for the cone, shank or holder. These can contact the part during end-face cuts. No cutter-body or fixture collision checking is performed. Inspect the toolpath and cutter geometry and verify the move before machining. The same warning is shown in the application and written into generated end-face G-code.

## Automated Windows builds

See [Windows build, download and test instructions](../docs/WINDOWS_BUILD.md).
