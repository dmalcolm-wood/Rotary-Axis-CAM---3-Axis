import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import trimesh
from PySide6 import QtWidgets
from brian_rotary_cam.cam_core import generate_finishing_gcode,process_job,SAFE_CLEARANCE_MM
from brian_rotary_cam.interface import RotaryCamWindow
from brian_rotary_cam.gcode_view import gcode_segments_for_view
from test_model_setup import FakeViewer

class EndFaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def test_faces_reach_minimum_at_each_angle_and_index_retracted(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'face.tap'
            generate_finishing_gcode(path,np.array([0.,5.]),np.array([0.,90.,180.,270.]),np.full((2,4),3.),6,12,2,1,0,90,4,2,300,1,'Y',2,end_faces=[('low X',-2),('high X',8)])
            text=path.read_text();face=text.split('(END FACE FINISHING:')[1]
            position={};bottoms=[];layers=[]
            for line in face.splitlines():
                if line.startswith('(End face radial layer'):layers.append(float(line.split('Z ')[1].rstrip(')')))
                if not line.startswith(('G0 ','G1 ')):continue
                words={w[0]:float(w[1:]) for w in line.split()[1:]}
                if 'Y' in words or 'A' in words:self.assertGreaterEqual(position.get('Z',0),7+SAFE_CLEARANCE_MM)
                position.update(words)
                if line.startswith('G1 ') and words.get('Z')==0:bottoms.append((position['Y'],position['A']))
            self.assertEqual(set(bottoms),{(x,a) for x in [-2,8] for a in [0,90,180,270]})
            self.assertEqual(layers,[5,3,1,0]*2)
            self.assertIn('conical cutters',text)
            _,cuts=gcode_segments_for_view(path,0,'Y')
            self.assertTrue(any(np.allclose(segment[-1],[8,0,0]) for segment in cuts))

    def test_selected_end_bounds_origin_and_other_end_preserved(self):
        with patch('brian_rotary_cam.interface.RotaryViewer',FakeViewer):w=RotaryCamWindow()
        self.addCleanup(w.close)
        w.roughing_box.setChecked(False);w.fields['finish_manual'].setText('90');w.fields['finish_tip'].setText('1');w.fields['finish_min_z'].setText('0')
        params=w._parameters()
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder)/'block.stl';trimesh.creation.box(extents=[20,4,6]).export(source)
            base=process_job(source,params);original=base['finish_path'].read_text()
            self.assertNotIn('END FACE FINISHING',original)
            for low,high in [(False,True),(True,False),(True,True)]:
                result=process_job(source,dict(params,finish_low_end=low,finish_high_end=high))
                self.assertEqual(result['x_origin'],base['x_origin'])
                expected=[]
                if low:expected.append(('low X',-11-base['x_origin']))
                if high:expected.append(('high X',11-base['x_origin']))
                self.assertEqual(result['end_faces'],expected)
                text=result['finish_path'].read_text()
                self.assertIn('minimum Z 0.0000',text)
                self.assertEqual('End face low X' in text,low)
                self.assertEqual('End face high X' in text,high)
                self.assertIn('End faces:',w._result_text(result))
            with self.assertRaisesRegex(ValueError,'positive ball'):
                process_job(source,dict(params,finish_high_end=True,finish_tip_radius=0))

    def test_positive_minimum_and_roughing_unaffected(self):
        with patch('brian_rotary_cam.interface.RotaryViewer',FakeViewer):w=RotaryCamWindow()
        self.addCleanup(w.close)
        w.fields['stock'].setText('14');w.fields['rough_manual'].setText('90');w.fields['finish_manual'].setText('90');w.fields['finish_min_z'].setText('2')
        params=w._parameters()
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder)/'block.stl';trimesh.creation.box(extents=[20,4,6]).export(source)
            base=process_job(source,params);rough=base['rough_path'].read_text()
            result=process_job(source,dict(params,finish_high_end=True))
            self.assertEqual(result['rough_path'].read_text(),rough)
            face=result['finish_path'].read_text().split('(END FACE FINISHING:')[1]
            targets=[float(line.split()[1][1:]) for line in face.splitlines() if line.startswith('G1 Z')]
            self.assertEqual(min(targets),2.)
