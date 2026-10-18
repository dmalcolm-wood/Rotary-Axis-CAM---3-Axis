# v1.6 validation

All 11 tests passed using the existing Robot GCode Python environment. Tests cover rigid rotations, bounding-box centring, source immutability, oblique automatic alignment, ambiguous geometry rejection, reset/invalidation controls, and identical G-code for equivalent pre-aligned and prepared STLs, plus existing XAZ/YAZ tests. Windows packaging and a fresh-environment installation have not been run.

Control layout was inspected using a stub viewer. The full PyVista window could not be verified in this automated offscreen Mac session: native rendering exited with a segmentation fault. The actual PyVista mesh conversion is covered by a coordinate/triangle regression test. Interactive 3D rendering remains to be checked in a normal desktop launch.
