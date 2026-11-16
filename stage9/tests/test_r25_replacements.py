"""R25 replacement import smoke tests with real decoded PNG pixels."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from replace_ai_chapters_r25 import plan,apply,native_dimensions

class ReplacementTests(unittest.TestCase):
    def test_full_resolution_replacement_and_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            assets=base/"ai-assets";assets.mkdir()
            inbox=base/"incoming";inbox.mkdir()
            before=b"old media"*180
            (assets/"editorial-1.png").write_bytes(before)
            record=dict(template="editorial",chapter=1,file="editorial-1.png",
                        sha256=hashlib.sha256(before).hexdigest(),source="AI_GENERATED",
                        sourceType="crop-of-AI-generated-collage",
                        nativeSourceDimensions=[828,306],presentationDimensions=[1600,900])
            # Test only one replacement using a complete 39-record manifest.
            records=[record]
            for template in ["editorial","product-3d","cinematic","architecture","agency","fashion","gallery","saas"]:
                for chapter in range(1,5 if template=="editorial" else 6):
                    if template=="editorial" and chapter==1:continue
                    records.append(dict(template=template,chapter=chapter,file=f"{template}-{chapter}.png",
                                        sha256="0"*64,source="AI_GENERATED"))
            (assets/"manifest.json").write_text(json.dumps({"assets":records}))
            image=Image.new("RGB",(1280,720),(32,80,120))
            image.save(inbox/"editorial-1.png",format="PNG")
            raw=(inbox/"editorial-1.png").read_bytes()
            self.assertEqual(native_dimensions(raw),(1280,720))
            entry=dict(template="editorial",chapter=1,file="editorial-1.png",
                       source="AI_GENERATED",sourceType="individual-generation",
                       trueHighResolutionGenerated=True,
                       nativeSourceDimensions=[1280,720],
                       generationSystem="fixture-generator",generationDate="2026-11-16",
                       sourceReference="fixture-original",commercialUseTermsChecked=True,
                       termsUrl="https://example.com/terms")
            (inbox/"replacement.json").write_text(json.dumps([entry]))
            manifest,planned=plan(inbox,assets/"manifest.json")
            self.assertEqual(len(planned),1)
            self.assertEqual((assets/"editorial-1.png").read_bytes(),before)
            result=apply(inbox,base/"backup",assets/"manifest.json")
            self.assertEqual(result["replacements"],1)
            self.assertEqual((base/"backup"/"editorial-1.png").read_bytes(),before)
            self.assertEqual((assets/"editorial-1.png").read_bytes(),raw)
            self.assertEqual(json.loads((assets/"manifest.json").read_text())["assets"][0]["nativeSourceDimensions"],[1280,720])
    def test_reject_collage_and_corrupt_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); inbox=base/"incoming";inbox.mkdir()
            assets=base/"ai-assets";assets.mkdir()
            rows=[dict(template="editorial",chapter=1,file="editorial-1.png",sha256="1"*64)]
            rows.extend(dict(template=t,chapter=c,file=f"{t}-{c}.png",sha256="0"*64)
              for t in ["editorial","product-3d","cinematic","architecture","agency","fashion","gallery","saas"]
              for c in range(1,5 if t=="editorial" else 6) if (t,c)!=("editorial",1))
            (assets/"manifest.json").write_text(json.dumps({"assets":rows}))
            entry=dict(template="editorial",chapter=1,file="editorial-1.png",source="AI_GENERATED",
                       sourceType="crop-of-AI-generated-collage",trueHighResolutionGenerated=False,
                       nativeSourceDimensions=[1280,720],generationSystem="fixture",
                       generationDate="2026-11-16",sourceReference="fixture",
                       termsUrl="https://example.com",commercialUseTermsChecked=True)
            (inbox/"editorial-1.png").write_bytes(b"not real pixels"*150)
            (inbox/"replacement.json").write_text(json.dumps([entry]))
            with self.assertRaises(ValueError): plan(inbox,assets/"manifest.json")
            entry.update(sourceType="individual-generation",trueHighResolutionGenerated=True)
            (inbox/"replacement.json").write_text(json.dumps([entry]))
            with self.assertRaises(ValueError): plan(inbox,assets/"manifest.json")

if __name__=="__main__":unittest.main()
