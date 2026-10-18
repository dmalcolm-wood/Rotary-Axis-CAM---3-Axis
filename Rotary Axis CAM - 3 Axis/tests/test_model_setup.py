import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import trimesh
from PySide6 import QtWidgets

from brian_rotary_cam.model_setup import prepare_mesh
from brian_rotary_cam.cam_core import process_job


class ModelSetupTests(unittest.TestCase):
    def test_rotates_centres_without_distortion_or_source_mutation(self):
        source = trimesh.creation.box(extents=[4, 20, 6])
        source.apply_translation([30, 50, -70])
        before = source.vertices.copy()
        mesh, matrix = prepare_mesh(source, {"source_axis": "Y", "centre": True})
        np.testing.assert_allclose(mesh.extents, [20, 4, 6])
        np.testing.assert_allclose(mesh.bounds.mean(axis=0)[1:], [0, 0], atol=1e-10)
        np.testing.assert_array_equal(source.vertices, before)
        np.testing.assert_allclose(mesh.vertices, trimesh.transform_points(before, matrix))
        self.assertAlmostEqual(np.linalg.det(matrix[:3, :3]), 1.0)
        self.assertAlmostEqual(abs(mesh.volume), abs(source.volume))

    def test_auto_aligns_oblique_long_geometry(self):
        source = trimesh.creation.box(extents=[30, 4, 6])
        source.apply_transform(trimesh.transformations.euler_matrix(.3, .6, .7))
        source.apply_translation([100, -90, 70])
        mesh, _ = prepare_mesh(source, {"source_axis": "AUTO", "centre": True})
        self.assertAlmostEqual(mesh.extents[0], 30)
        np.testing.assert_allclose(mesh.bounds.mean(axis=0)[1:], 0, atol=1e-9)
        self.assertAlmostEqual(abs(mesh.volume), abs(source.volume))

    def test_viewer_receives_prepared_vertices_and_faces(self):
        from brian_rotary_cam.pyvista_viewer import RotaryViewer
        from types import SimpleNamespace
        source = trimesh.creation.box(extents=[4,20,6])
        source.apply_translation([30,40,50])
        mesh, _ = prepare_mesh(source, {"source_axis": "Y", "centre": True})
        viewer = SimpleNamespace(rebuild=lambda: None, fit_view=lambda: None)
        RotaryViewer.set_mesh(viewer, mesh)
        np.testing.assert_allclose(viewer.mesh.points, mesh.vertices)
        np.testing.assert_array_equal(viewer.mesh.faces.reshape(-1,4)[:,1:], mesh.faces)

    def test_symmetric_auto_requires_explicit_axis(self):
        with self.assertRaisesRegex(ValueError, "No clear long axis"):
            prepare_mesh(trimesh.creation.box(), {"source_axis": "AUTO"})

    def test_original_placement_and_fine_rotations(self):
        source = trimesh.creation.box(extents=[4, 6, 20])
        source.apply_translation([10, 20, 30])
        unchanged, _ = prepare_mesh(source)
        np.testing.assert_array_equal(unchanged.vertices, source.vertices)
        transformed, _ = prepare_mesh(source, {"source_axis": "Z", "centre": True,
                                               "rotation_deg": [90, 0, 0]})
        np.testing.assert_allclose(transformed.extents, [20, 4, 6], atol=1e-9)
        np.testing.assert_allclose(transformed.bounds.mean(axis=0)[1:], 0, atol=1e-9)

    def test_preparation_generates_same_motion_as_pre_aligned_stl(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            original = trimesh.creation.box(extents=[20, 4, 6])
            moved = original.copy()
            moved.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 0, 1]))
            moved.apply_translation([50, 30, 80])
            aligned_path, moved_path = root/'aligned.stl', root/'moved.stl'
            original.export(aligned_path); moved.export(moved_path)
            before = moved_path.read_bytes()
            params = dict(stock_diameter=12, x_step=4,
                rough_tip_radius=.5, finish_tip_radius=.5,
                rough_cutter_diameter=3, finish_cutter_diameter=2,
                rough_spacing_fraction=.5, finish_spacing_fraction=.5,
                rough_manual_a=90, finish_manual_a=90, rough_min_z=0,
                finish_min_z=0, rough_depth_per_pass=2, rough_allowance=.5,
                rough_feed=500, finish_feed=300, finish_entry_depth_per_pass=2)
            first = process_job(aligned_path, params)
            second = process_job(moved_path, dict(params, model_setup={"source_axis":"Y", "centre":True}))
            for key in ['rough_path', 'finish_path']:
                motion = lambda p: [s for s in p.read_text().splitlines() if s.startswith(('G0 ', 'G1 '))]
                self.assertEqual(motion(first[key]), motion(second[key]))
            self.assertEqual(moved_path.read_bytes(), before)
            self.assertAlmostEqual(first['model_diameter'], second['model_diameter'])


class FakeViewer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.mesh = None
        self.paths = {}
    def set_mesh(self, mesh):
        self.mesh = mesh.copy()
        self.paths = {"rough": ([], []), "finish": ([], [])}
    def rebuild(self): pass
    def fit_view(self): pass
    def set_stl_visible(self, *_): pass
    def set_operation_visible(self, *_): pass
    def set_rapids_visible(self, *_): pass


class ModelSetupGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def test_controls_update_preview_clear_old_output_and_reset(self):
        from brian_rotary_cam.interface import RotaryCamWindow
        with patch('brian_rotary_cam.interface.RotaryViewer', FakeViewer):
            window = RotaryCamWindow()
        self.addCleanup(window.close)
        window.source_mesh = trimesh.creation.box(extents=[4,20,6])
        window.source_mesh.apply_translation([40,50,60])
        window.refresh_model()
        window.rough_text.setPlainText('obsolete G-code')
        window.viewer.paths['rough'] = ([1], [2])
        window.source_axis.setCurrentIndex(1)
        window.centre_model.setChecked(True)
        np.testing.assert_allclose(window.viewer.mesh.extents, [20,4,6])
        np.testing.assert_allclose(window.viewer.mesh.bounds.mean(axis=0)[1:], 0, atol=1e-9)
        self.assertEqual(window.rough_text.toPlainText(), '')
        self.assertEqual(window.viewer.paths['rough'], ([], []))
        window.reset_model_setup()
        np.testing.assert_array_equal(window.viewer.mesh.vertices, window.source_mesh.vertices)
        window.source_mesh = trimesh.creation.box()
        window.source_axis.setCurrentIndex(3)
        self.assertFalse(window.generate_button.isEnabled())
        self.assertIsNone(window.viewer.mesh)
        window.reset_model_setup()
        self.assertTrue(window.generate_button.isEnabled())

if __name__ == '__main__':
    unittest.main()
