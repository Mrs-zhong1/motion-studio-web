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


    def test_procedural_original_is_accepted_only_with_explicit_no_third_party_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); assets=base/"ai-assets";assets.mkdir(); inbox=base/"incoming";inbox.mkdir()
            old=b"old image bytes "*100
            (assets/"agency-1.png").write_bytes(old)
            rows=[]
            for template in ["editorial","product-3d","cinematic","architecture","agency","fashion","gallery","saas"]:
                for chapter in range(1,5 if template=="editorial" else 6):
                    name=f"{template}-{chapter}.png"
                    if (template,chapter)==("agency",1):
                        rows.append(dict(template=template,chapter=chapter,file=name,sha256=hashlib.sha256(old).hexdigest()))
                    else: rows.append(dict(template=template,chapter=chapter,file=name,sha256="0"*64))
            (assets/"manifest.json").write_text(json.dumps({"assets":rows}))
            Image.new("RGB",(1600,900),(80,100,120)).save(inbox/"agency-1.png","PNG")
            entry=dict(template="agency",chapter=1,file="agency-1.png",source="PROCEDURAL_ORIGINAL",
                sourceType="procedural-3d-render",trueHighResolutionGenerated=True,
                nativeSourceDimensions=[1600,900],generationSystem="Blender Eevee",
                generationDate="2026-11-19",sourceReference="stage9/r26_blender_pilot.py",
                termsUrl="https://github.com/Mrs-zhong1/motion-studio-web",
                commercialUseTermsChecked=True,embeddedThirdPartyAssets=False)
            (inbox/"replacement.json").write_text(json.dumps([entry]))
            _,planned=plan(inbox,assets/"manifest.json")
            self.assertEqual(len(planned),1)
            entry["embeddedThirdPartyAssets"]=True
            (inbox/"replacement.json").write_text(json.dumps([entry]))
            with self.assertRaisesRegex(ValueError,"embeddedThirdPartyAssets=false"):
                plan(inbox,assets/"manifest.json")

    def test_open_license_requires_attribution_and_rejects_nc_nd(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); assets=base/"ai-assets";assets.mkdir(); inbox=base/"incoming";inbox.mkdir()
            old=b"old image bytes "*100
            (assets/"architecture-2.png").write_bytes(old)
            rows=[]
            for template in ["editorial","product-3d","cinematic","architecture","agency","fashion","gallery","saas"]:
                for chapter in range(1,5 if template=="editorial" else 6):
                    name=f"{template}-{chapter}.png"
                    if (template,chapter)==("architecture",2):
                        rows.append(dict(template=template,chapter=chapter,file=name,sha256=hashlib.sha256(old).hexdigest()))
                    else: rows.append(dict(template=template,chapter=chapter,file=name,sha256="0"*64))
            (assets/"manifest.json").write_text(json.dumps({"assets":rows}))
            Image.new("RGB",(1600,900),(110,90,70)).save(inbox/"architecture-2.png","PNG")
            entry=dict(template="architecture",chapter=2,file="architecture-2.png",source="OPEN_LICENSED_PHOTOGRAPHY",
                sourceType="open-licensed-photography",trueHighResolutionGenerated=True,
                nativeSourceDimensions=[1600,900],generationSystem="Original source download",
                generationDate="2026-11-19",sourceReference="https://example.org/photo",
                termsUrl="https://example.org/license",commercialUseTermsChecked=True,
                creator="Photographer",licenseId="CC-BY-4.0",licenseUrl="https://creativecommons.org/licenses/by/4.0/",
                attributionText="Photo by Photographer, CC BY 4.0")
            (inbox/"replacement.json").write_text(json.dumps([entry]))
            _,planned=plan(inbox,assets/"manifest.json")
            self.assertEqual(len(planned),1)
            entry["licenseId"]="CC-BY-NC-4.0"
            (inbox/"replacement.json").write_text(json.dumps([entry]))
            with self.assertRaisesRegex(ValueError,"not explicitly approved for commercial reuse"):
                plan(inbox,assets/"manifest.json")

if __name__=="__main__":unittest.main()
