"""R32 media gate tests: actual decoded pixels cannot disguise collage origin."""
import hashlib,json,sys,tempfile,unittest,subprocess
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from audit_r32_real_media import audit,TEMPLATES
class R32MediaAuditTests(unittest.TestCase):
    def test_native_dimensions_and_provenance_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            records=[]
            for template_index,template in enumerate(TEMPLATES):
                for chapter in range(1,5 if template=='editorial' else 6):
                    name=f'{template}-{chapter}.jpg'
                    Image.new('RGB',(1280,720),(15+template_index*24,chapter*31,20+template_index*9)).save(root/name,'JPEG',quality=85)
                    raw=(root/name).read_bytes()
                    records.append({'template':template,'chapter':chapter,'file':name,
                       'source':'AI_GENERATED','sourceType':'individual-generation',
                       'trueHighResolutionGenerated':True,
                       'nativeSourceDimensions':[1280,720],'presentationDimensions':[1280,720],
                       'generationSystem':'test fixture','generationDate':'2026-11-16',
                       'sourceReference':name,'termsUrl':'https://example.org/terms',
                       'commercialUseTermsChecked':True,'sha256':hashlib.sha256(raw).hexdigest()})
            (root/'manifest.json').write_text(json.dumps({'assets':records}))
            ok=audit(root)
            self.assertTrue(ok['summary']['productionMediaEligible'])
            self.assertEqual(ok['summary']['decodedAndCheckedImages'],39)
            self.assertEqual(ok['by_template'][0]['sourceEligibleOriginals'],4)
            cli=subprocess.run([sys.executable,str(Path(__file__).resolve().parents[1]/'audit_r32_real_media.py'),
                                '--assets',str(root)],capture_output=True,text=True)
            self.assertEqual(cli.returncode,0,cli.stderr)
            self.assertIn('source-eligible originals',cli.stdout)
            records[0].update(source='PROCEDURAL_ORIGINAL',sourceType='procedural-3d-render',
                              embeddedThirdPartyAssets=False)
            records[1].update(source='OPEN_LICENSED_PHOTOGRAPHY',sourceType='open-licensed-photography',
                              creator='Photographer',licenseId='CC-BY-4.0',
                              licenseUrl='https://creativecommons.org/licenses/by/4.0/',
                              attributionText='Photo by Photographer, CC BY 4.0')
            (root/'manifest.json').write_text(json.dumps({'assets':records}))
            mixed=audit(root)
            self.assertTrue(mixed['summary']['productionMediaEligible'])
            self.assertEqual(mixed['summary']['proceduralOriginalCount'],1)
            self.assertEqual(mixed['summary']['openLicensedPhotographyCount'],1)
            records[1]['licenseId']='CC-BY-NC-4.0'
            (root/'manifest.json').write_text(json.dumps({'assets':records}))
            nc=audit(root)
            self.assertFalse(nc['summary']['productionMediaEligible'])
            self.assertIn('commercially_incompatible_license',nc['scenes'][1]['technicalRisk'])
            records[3]['sourceType']='crop-of-AI-generated-collage'
            records[3]['nativeSourceDimensions']=[828,306]
            (root/'manifest.json').write_text(json.dumps({'assets':records}))
            blocked=audit(root)
            self.assertFalse(blocked['summary']['productionMediaEligible'])
            self.assertEqual(blocked['summary']['flaggedImages'],1)
            self.assertIn('source_native_resolution_insufficient',blocked['scenes'][3]['technicalRisk'])
            self.assertIn('upscaled_output_cannot_restore_original_pixels',blocked['scenes'][3]['technicalRisk'])
            records[3]['sourceType']='individual-generation'
            records[3]['nativeSourceDimensions']=[1280,720]
            (root/'manifest.json').write_text(json.dumps({'assets':records}))
            (root/'editorial-4.jpg').write_bytes(b'not an image')
            corrupted=audit(root)
            self.assertFalse(corrupted['summary']['productionMediaEligible'])
            self.assertTrue(any('undecodable' in s for s in corrupted['summary']['structuralErrors']))
if __name__=='__main__':unittest.main()
