import tempfile
import unittest
from pathlib import Path

import numpy as np

from brian_rotary_cam.cam_core import (
    estimate_gcode_time,
    generate_finishing_gcode,
)
from brian_rotary_cam.gcode_view import gcode_segments_for_view


class BrianAxisSelectionTests(unittest.TestCase):
    def generate(self, axis, entry_depth=2.5):
        tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(tempdir.cleanup)
        path = Path(tempdir.name) / "finish.tap"
        generate_finishing_gcode(
            path,
            x_relative=np.array([0.0, 5.0, 10.0]),
            machine_angles_deg=np.array([0.0, 90.0]),
            radius_map=np.array([[10.0, 11.0], [9.0, 10.0], [8.0, 9.0]]),
            stock_radius=15.0,
            stock_diameter=30.0,
            cutter_diameter=3.0,
            tip_radius=1.5,
            min_cutter_z=0.0,
            a_step=90.0,
            pass_count=2,
            spacing=2.0,
            feed=600.0,
            x_step=5.0,
            linear_axis=axis,
            entry_depth_per_pass=entry_depth,
        )
        return path

    def test_y_mode_outputs_yaz_motion_without_x_words(self):
        path = self.generate("Y")
        lines = path.read_text().splitlines()
        motion = [line for line in lines if line.startswith(("G0", "G1"))]
        self.assertTrue(any("Y10.0000" in line for line in motion))
        self.assertTrue(any(line.startswith("G1 A90") for line in motion))
        self.assertFalse(any("X" in line for line in motion))
        self.assertIn("(Y = longitudinal axis", path.read_text())

    def test_x_mode_remains_the_default(self):
        path = self.generate("X")
        motion = [line for line in path.read_text().splitlines()
                  if line.startswith(("G0", "G1"))]
        self.assertTrue(any("X10.0000" in line for line in motion))
        self.assertFalse(any("Y" in line for line in motion))

    def test_y_time_estimate_and_derotation_use_y_as_longitudinal(self):
        path = self.generate("Y")
        minutes, moves, distance = estimate_gcode_time(path, 600.0, "Y")
        self.assertGreater(minutes, 0.0)
        self.assertGreater(moves, 0)
        self.assertGreater(distance, 0.0)

        rapid, cuts = gcode_segments_for_view(path, x_origin=3.0, linear_axis="Y")
        self.assertTrue(cuts)
        longitudinal = np.concatenate(cuts)[:, 0]
        self.assertGreaterEqual(float(longitudinal.min()), 3.0)
        self.assertLessEqual(float(longitudinal.max()), 13.0)

    def test_finishing_starts_with_feed_down_entry_layers(self):
        path = self.generate("X", entry_depth=2.5)
        text = path.read_text()
        self.assertIn("Introductory finishing entry layers at first A angle: 3", text)
        self.assertIn("Finishing entry layer 1 of 3 - limiter Z 14.0000", text)
        self.assertIn("Finishing entry layer 2 of 3 - limiter Z 11.5000", text)
        self.assertIn("Finishing entry layer 3 of 3 - limiter Z 9.5000", text)
        self.assertIn("G1 Z14.0000 F600.0", text)
        self.assertNotIn("G0 Z14.0000", text)
        self.assertEqual(text.count("G1 A90.00000"), 1)


if __name__ == "__main__":
    unittest.main()
