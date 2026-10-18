import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock
import pyvista as pv
from brian_rotary_cam.pyvista_viewer import RotaryViewer

class ShadingTests(unittest.TestCase):
    def test_slider_changes_material_without_rebuilding_geometry(self):
        actor=MagicMock();plotter=MagicMock()
        view=SimpleNamespace(actors={'stl':actor},plotter=plotter)
        view._apply_shading=lambda a:RotaryViewer._apply_shading(view,a)
        RotaryViewer.set_shading(view,0)
        prop=actor.GetProperty.return_value
        prop.SetAmbient.assert_called_with(1.0)
        prop.SetDiffuse.assert_called_with(0.0)
        RotaryViewer.set_shading(view,100)
        prop.SetDiffuse.assert_called_with(.95)
        prop.SetSpecular.assert_called_with(.2)
        plotter.clear.assert_not_called()
        plotter.add_mesh.assert_not_called()

    def test_rebuild_keeps_strength_and_uses_normals(self):
        mesh=pv.Cube().triangulate();original=mesh.points.copy()
        view=SimpleNamespace(shading_strength=100,actors={},mesh=mesh,plotter=MagicMock(),_add_operation=lambda *a,**kw:None)
        RotaryViewer.rebuild(view)
        view.plotter.enable_lightkit.assert_called_once()
        args=view.plotter.add_mesh.call_args
        self.assertTrue(args.kwargs['lighting'])
        self.assertEqual(args.kwargs['opacity'],1.0)
        self.assertIn('Normals',args.args[0].point_data)
        view.actors['stl'].GetProperty().SetDiffuse.assert_called_with(.95)
        import numpy as np
        np.testing.assert_array_equal(mesh.points,original)
