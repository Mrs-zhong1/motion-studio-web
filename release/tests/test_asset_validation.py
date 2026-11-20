import importlib.util
import tempfile
import unittest
from pathlib import Path

def load(name, path):
    spec=importlib.util.spec_from_file_location(name, path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

ROOT=Path(__file__).resolve().parents[2]
R52=load("r52_validator",ROOT/"release/validate_r52_photo_rights.py")
R53=load("r53_validator",ROOT/"release/validate_r53_production_assets.py")

class AssetGateUnitTests(unittest.TestCase):
    def test_r52_native_dimensions_accepts_1600x900(self):
        self.assertTrue(R52.valid_dimensions(1600,900))
        self.assertTrue(R52.valid_dimensions(1920,1080))

    def test_r52_rejects_low_or_wrong_ratio(self):
        self.assertFalse(R52.valid_dimensions(1599,900))
        self.assertFalse(R52.valid_dimensions(1600,1000))
        self.assertFalse(R52.valid_dimensions(2560,1080))

    def test_r53_native_dimensions(self):
        self.assertTrue(R53.valid_dimensions([1600,900]))
        self.assertTrue(R53.valid_dimensions([1920,1080]))
        self.assertFalse(R53.valid_dimensions([1599,900]))
        self.assertFalse(R53.valid_dimensions([1600,1000]))
        self.assertFalse(R53.valid_dimensions([1600]))

    def test_r53_svg_requires_real_svg_root_and_canvas(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"good.svg"
            p.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900"><rect width="10" height="10"/></svg>')
            self.assertEqual(R53.validate_svg(p),(1600,900))
            p.write_text('<html width="1600" height="900" viewBox="0 0 1600 900"></html>')
            with self.assertRaises(ValueError): R53.validate_svg(p)
            p.write_text('<svg width="1600" height="900" viewBox="0 0 800 600"></svg>')
            with self.assertRaises(ValueError): R53.validate_svg(p)

if __name__=="__main__": unittest.main()
