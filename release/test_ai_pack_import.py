"""Synthetic 39-chapter ZIP install exercises actual installer, no stock photography."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from install_ai_pack import install

IDS=["editorial","product-3d","cinematic","architecture","agency","fashion","gallery","saas"]

class PackImportTests(unittest.TestCase):
    def make_archive(self,root,corrupt=False):
        archive=root/"pack.zip"
        manifest=[]
        with ZipFile(archive,"w") as out:
            for name in IDS:
                for chapter in range(1,5 if name=="editorial" else 6):
                    fn=f"{name}-{chapter}.jpg"
                    data=(fn.encode()*300)[:2000]
                    manifest.append({"template":name,"chapter":chapter,"file":fn,
                        "source":"AI_GENERATED","commercialUseTermsChecked":True,
                        "sha256":hashlib.sha256(data).hexdigest()})
                    out.writestr("stage9/ai-assets/"+fn,data+b"x" if corrupt and fn=="editorial-1.jpg" else data)
            out.writestr("stage9/ai-assets/manifest.json",json.dumps({"assets":manifest}))
            out.writestr("release/R18_ASSET_TECHNICAL_AUDIT.json","{}")
        return archive
    def test_39_file_archive_imports(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            target=install(self.make_archive(root),root)
            self.assertEqual(len(list(target.glob("*.jpg"))),39)
            self.assertTrue((target/"manifest.json").exists())
    def test_corrupt_archive_rejected_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with self.assertRaisesRegex(ValueError,"SHA256"):
                install(self.make_archive(root,corrupt=True),root)
            self.assertFalse((root/"stage9"/"ai-assets").exists())

if __name__=="__main__":
    unittest.main()
