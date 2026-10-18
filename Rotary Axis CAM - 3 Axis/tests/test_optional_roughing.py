import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
import trimesh
import pyvista as pv
import numpy as np
from PySide6 import QtWidgets
from test_model_setup import FakeViewer
from brian_rotary_cam import cam_core
from brian_rotary_cam.interface import RotaryCamWindow
from brian_rotary_cam.pyvista_viewer import RotaryViewer

class OptionalRoughingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def test_finishing_only_skips_roughing_and_preserves_existing_file(self):
        with patch('brian_rotary_cam.interface.RotaryViewer',FakeViewer):w=RotaryCamWindow()
        self.addCleanup(w.close)
        w.fields['rough_tip'].setText('invalid and unused')
        w.fields['rough_manual'].setText('invalid and unused')
        w.roughing_box.setChecked(False)
        w.fields['finish_manual'].setText('90')
        params=w._parameters()
        self.assertNotIn('rough_tip_radius',params)
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder)/'model.stl';trimesh.creation.box(extents=[20,4,6]).export(source)
            old=source.with_name('model_roughing.tap');old.write_text('previous roughing')
            with patch.object(cam_core,'generate_roughing_gcode') as rough,patch.object(cam_core,'build_radius_map',wraps=cam_core.build_radius_map) as sample:
                result=cam_core.process_job(source,params)
            rough.assert_not_called();self.assertEqual(sample.call_count,2)
            self.assertIsNone(result['rough_path']);self.assertTrue(result['finish_path'].exists())
            self.assertEqual(old.read_text(),'previous roughing')
            self.assertEqual(result['end_inset'],params['finish_tip_radius'])
            self.assertIn('skipped',w._result_text(result))
            old.unlink()
            cam_core.process_job(source,params)
            self.assertFalse(old.exists())

    def test_roughing_default_remains_enabled(self):
        with patch('brian_rotary_cam.interface.RotaryViewer',FakeViewer):w=RotaryCamWindow()
        self.addCleanup(w.close)
        self.assertTrue(w._parameters()['generate_roughing'])
        w.roughing_box.setChecked(False);w.roughing_box.setChecked(True)
        self.assertIn('Roughing + Finishing',w.generate_button.text())

    def test_no_point_markers_and_solid_stl(self):
        plotter=MagicMock()
        view=SimpleNamespace(plotter=plotter,actors={},mesh=pv.Cube(),_add_operation=lambda *a,**k:None)
        RotaryViewer.rebuild(view)
        self.assertEqual(plotter.add_mesh.call_args.kwargs['opacity'],1.0)
        plotter.reset_mock()
        view.paths={'finish':([], [np.array([[0,0,0],[1,1,1]])])}
        RotaryViewer._add_operation(view,'finish','red')
        self.assertEqual(plotter.add_mesh.call_count,1)
        self.assertEqual(plotter.add_mesh.call_args.kwargs['line_width'],2)
        self.assertNotIn('finish_points',view.actors)
        self.assertEqual(plotter.add_mesh.call_args.args[0].n_verts,0)

    def test_finishing_only_clears_previous_roughing_preview(self):
        view=SimpleNamespace(paths={'rough':([1],[2])},rebuild=lambda:None,fit_view=lambda:None)
        with patch('brian_rotary_cam.pyvista_viewer.gcode_segments_for_view',return_value=([],[])) as read:
            RotaryViewer.load_toolpaths(view,None,'finish.tap',0)
        self.assertEqual(view.paths['rough'],([],[]));read.assert_called_once_with('finish.tap',0,'X')
