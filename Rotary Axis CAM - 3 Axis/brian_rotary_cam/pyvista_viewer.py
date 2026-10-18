"""Embedded PyVista presentation for STL and indexed rotary toolpaths."""

from pathlib import Path

import numpy as np
import pyvista as pv
from pyvistaqt import QtInteractor
from PySide6 import QtCore, QtWidgets

from .gcode_view import gcode_segments_for_view, segments_to_polydata


class RotaryViewer(QtWidgets.QWidget):
    """PyVista viewer using the colour scheme of Helpers/Vizualizer.py."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.shading_strength = 70
        self.mesh = None
        self.paths = {"rough": ([], []), "finish": ([], [])}
        self.actors = {}

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.plotter = QtInteractor(self)
        layout.addWidget(self.plotter.interactor)

        self.plotter.set_background("black")
        self.plotter.show_grid(color="white")
        self.plotter.add_axes(color="white")
        self.plotter.enable_trackball_style()

    def load_stl(self, path):
        mesh = pv.read(str(Path(path)))
        if mesh.n_points == 0:
            raise ValueError("The STL contains no points.")
        self.mesh = mesh.clean().compute_normals(consistent_normals=True)
        self.paths = {"rough": ([], []), "finish": ([], [])}
        self.rebuild()
        self.fit_view()

    def set_mesh(self, mesh):
        """Display the exact prepared triangle coordinates used by CAM."""
        faces = np.column_stack((np.full(len(mesh.faces), 3), mesh.faces))
        self.mesh = pv.PolyData(np.asarray(mesh.vertices).copy(), faces.ravel())
        # Keep vertex/triangle indices intact here; smoothing handles welding for rendering.
        self.paths = {"rough": ([], []), "finish": ([], [])}
        self.rebuild()
        self.fit_view()

    def load_toolpaths(self, rough_path, finish_path, x_origin, linear_axis="X"):
        self.paths["rough"] = gcode_segments_for_view(
            rough_path, x_origin, linear_axis
        ) if rough_path is not None else ([], [])
        self.paths["finish"] = gcode_segments_for_view(
            finish_path, x_origin, linear_axis
        )
        self.rebuild()
        self.fit_view()

    def set_shading(self, value):
        self.shading_strength = max(0, min(100, int(value)))
        actor = self.actors.get("stl")
        if actor is not None:
            self._apply_shading(actor)
            self.plotter.render()

    def _apply_shading(self, actor):
        strength = getattr(self, "shading_strength", 70) / 100.0
        prop = actor.GetProperty()
        prop.SetLighting(True)
        prop.SetAmbient(1.0 - 0.85 * strength)
        prop.SetDiffuse(0.95 * strength)
        prop.SetSpecular(0.20 * strength)
        prop.SetSpecularPower(30.0)
        prop.SetInterpolationToPhong()

    def rebuild(self):
        self.plotter.clear()
        self.actors.clear()
        self.plotter.set_background("black")
        self.plotter.show_grid(color="white")
        self.plotter.add_axes(color="white")
        self.plotter.enable_lightkit()

        if self.mesh is not None:
            self.actors["stl"] = self.plotter.add_mesh(
                self.mesh.clean().compute_normals(consistent_normals=True),
                color="lightgray",
                lighting=True,
                split_sharp_edges=True,
                opacity=1.0,
                smooth_shading=True,
                show_edges=False,
                name="Design STL",
            )
            RotaryViewer._apply_shading(self, self.actors["stl"])

        self._add_operation("rough", line_color="orange")
        self._add_operation("finish", line_color="red")
        self.plotter.render()

    def _add_operation(self, key, line_color):
        rapids, cuts = self.paths[key]
        rapid_poly = segments_to_polydata(pv, rapids)
        cut_poly = segments_to_polydata(pv, cuts)

        if rapid_poly is not None:
            self.actors[f"{key}_rapid"] = self.plotter.add_mesh(
                rapid_poly,
                color="gray",
                line_width=1,
                opacity=0.30,
                name=f"{key.title()} rapid moves",
            )

        if cut_poly is not None:
            self.actors[f"{key}_line"] = self.plotter.add_mesh(
                cut_poly,
                color=line_color,
                line_width=2,
                opacity=1.0,
                name=f"{key.title()} cutting path",
            )

    def set_stl_visible(self, visible):
        self._set_actor_visible("stl", visible)

    def set_operation_visible(self, key, visible):
        self._set_actor_visible(f"{key}_line", visible)

    def set_rapids_visible(self, visible):
        self._set_actor_visible("rough_rapid", visible)
        self._set_actor_visible("finish_rapid", visible)

    def _set_actor_visible(self, key, visible):
        actor = self.actors.get(key)
        if actor is not None:
            actor.SetVisibility(bool(visible))
            self.plotter.render()

    def fit_view(self):
        self.plotter.view_isometric()
        self.plotter.reset_camera()
        self.plotter.render()
