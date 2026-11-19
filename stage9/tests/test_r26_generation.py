"""R26 offline tests: no API key, no paid calls, no fake original images."""
import base64
import json
import sys
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from generate_r26_ai_scenes import storyboard,prompt,extract_image,process_image,run,request_payload

class R26Tests(unittest.TestCase):
    def test_storyboard_has_exact_33_noncollage_chapters(self):
        rows=storyboard()
        self.assertEqual(len(rows),33)
        self.assertEqual(len({(r['template'],r['chapter']) for r in rows}),33)
        for r in rows:
            p=prompt(r)
            self.assertIn(r['subject'],p)
            self.assertIn(r['chapterTitle'],p)
            self.assertIn('not a crop',p)
    def test_decode_real_model_output_and_reject_fake(self):
        bio=BytesIO()
        Image.new('RGB',(1920,1080),(22,44,66)).save(bio,format='PNG')
        encoded=base64.b64encode(bio.getvalue()).decode()
        response={'status':'completed','id':'int_test','steps':[{'type':'model_output',
          'content':[{'type':'image','mime_type':'image/png','data':encoded}]}]}
        source,identifier=extract_image(response)
        self.assertEqual(identifier,'int_test')
        jpeg,dims=process_image(source)
        self.assertEqual(dims,[1920,1080])
        self.assertTrue(jpeg.startswith(bytes.fromhex('ffd8')))
        self.assertRaises(ValueError,extract_image,{'steps':[]})
        self.assertRaises(ValueError,extract_image,{'steps':[{'type':'model_output',
          'content':[{'type':'image','mime_type':'image/png','data':encoded}]*2}]})
        small=BytesIO()
        Image.new('RGB',(828,306),(1,2,3)).save(small,format='PNG')
        self.assertRaises(ValueError,process_image,small.getvalue())
    def test_provider_interactions_contract_and_output_image_format(self):
        row=storyboard()[0]
        body=request_payload(row)
        self.assertEqual(body['model'],'gemini-3.1-flash-image')
        self.assertEqual(body['response_format'],{'type':'image','mime_type':'image/png',
          'aspect_ratio':'16:9','image_size':'2K'})
        bio=BytesIO()
        Image.new('RGB',(1920,1080),(13,77,121)).save(bio,format='PNG')
        encoded=base64.b64encode(bio.getvalue()).decode()
        raw,ident=extract_image({'status':'completed','id':'single-image',
          'output_image':{'type':'image','data':encoded,'mime_type':'image/png'}})
        self.assertEqual(raw,bio.getvalue())
        self.assertEqual(ident,'single-image')
        self.assertRaises(ValueError,extract_image,{'status':'in_progress','output_image':{'data':encoded}})
        self.assertRaises(ValueError,extract_image,{'output_image':{'mime_type':'text/plain','data':encoded}})
    def test_paid_generation_is_disabled_under_zero_cost_plan(self):
        class Args:
            generate=True
        with self.assertRaisesRegex(ValueError,'disabled by the R26 zero-cost hybrid plan'):
            run(Args)

    def test_dry_run_never_requires_api_key_or_writes_images(self):
        with tempfile.TemporaryDirectory() as td:
            class Args:
                storyboard=Path(__file__).resolve().parents[1]/'r26-storyboard.json'
                out=Path(td)/'out'
                template='cinematic'
                limit=2
                generate=False
            run(Args)
            self.assertFalse(Args.out.exists())

if __name__=='__main__':unittest.main()
