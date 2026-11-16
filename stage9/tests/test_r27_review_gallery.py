"""R27 artifact gallery uses actual validated staged images, not placeholders."""
import hashlib,json,sys,tempfile,unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from review_r27_contact_sheet import make_gallery
from generate_r26_ai_scenes import storyboard

class GalleryTests(unittest.TestCase):
    def test_true_source_image_and_sha_integrity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); stage=root/'stage';stage.mkdir()
            spec=storyboard()[0]; filename=spec['file']
            Image.new('RGB',(1920,1080),(65,90,130)).save(stage/filename,format='JPEG',quality=90)
            raw=(stage/filename).read_bytes()
            row={'template':spec['template'],'chapter':spec['chapter'],'file':filename,
                 'sha256':hashlib.sha256(raw).hexdigest(),
                 'nativeSourceDimensions':[1920,1080],'sourceType':'individual-generation'}
            (stage/'replacement.json').write_text(json.dumps([row]))
            board=Path(__file__).resolve().parents[1]/'r26-storyboard.json'
            out=root/'visual'
            result=make_gallery(stage,board,out)
            self.assertEqual(result['reviewedForFileIntegrity'],1)
            self.assertFalse(result['artDirectionApproved'])
            self.assertTrue((out/'index.html').exists())
            self.assertTrue((out/f"{spec['template']}-review-strip.jpg").exists())
            row['sha256']='a'*64
            (stage/'replacement.json').write_text(json.dumps([row]))
            with self.assertRaisesRegex(ValueError,'hash mismatch'):
                make_gallery(stage,board,out)
    def test_reject_upscaled_artwork(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);stage=root/'stage';stage.mkdir()
            spec=storyboard()[0];filename=spec['file']
            Image.new('RGB',(828,306),(65,90,130)).save(stage/filename,format='JPEG',quality=90)
            raw=(stage/filename).read_bytes()
            row={'template':spec['template'],'chapter':spec['chapter'],'file':filename,
                 'sha256':hashlib.sha256(raw).hexdigest(),
                 'nativeSourceDimensions':[828,306],'sourceType':'crop-of-AI-generated-collage'}
            (stage/'replacement.json').write_text(json.dumps([row]))
            with self.assertRaisesRegex(ValueError,'Low-native-resolution'):
                make_gallery(stage,Path(__file__).resolve().parents[1]/'r26-storyboard.json',root/'output')

if __name__=='__main__':unittest.main()
