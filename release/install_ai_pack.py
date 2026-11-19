#!/usr/bin/env python3
"""Install the 39-file R18 AI original media pack without trusting filenames alone."""
import argparse
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

IDS = ["editorial", "product-3d", "cinematic", "architecture", "agency", "fashion", "gallery", "saas"]
EXPECTED = {(template,chapter) for template in IDS for chapter in range(1,5 if template=="editorial" else 6)}
PREFIX = "stage9/ai-assets/"

def install(archive, checkout):
    checkout=Path(checkout).resolve()
    target=checkout/"stage9"/"ai-assets"
    with ZipFile(archive) as zip_file:
        names=zip_file.namelist()
        if len(names)!=41 or len(names)!=len(set(names)):
            raise ValueError("R18 archive must contain 39 images, manifest and audit report")
        if any(not (n.startswith(PREFIX) or n=="release/R18_ASSET_TECHNICAL_AUDIT.json") or
               ".." in Path(n).parts or n.startswith("/") for n in names):
            raise ValueError("R18 archive contains an unexpected path")
        manifest=json.loads(zip_file.read(PREFIX+"manifest.json"))
        assets=manifest.get("assets",[])
        if len(assets)!=39 or {(x.get("template"),x.get("chapter")) for x in assets}!=EXPECTED:
            raise ValueError("R18 AI chapter manifest incomplete or duplicated")
        if len(set(x.get("file") for x in assets))!=39:
            raise ValueError("R18 AI media names must be unique")
        with TemporaryDirectory(prefix="motion-r18-ai-") as tmp:
            staging=Path(tmp)
            for item in assets:
                file=item["file"]
                if not isinstance(file,str) or Path(file).name!=file or not file.lower().endswith((".jpg",".jpeg",".png",".webp")):
                    raise ValueError("Unsafe image filename")
                data=zip_file.read(PREFIX+file)
                if (hashlib.sha256(data).hexdigest()!=item.get("sha256") or
                    item.get("source")!="AI_GENERATED" or
                    item.get("commercialUseTermsChecked") is not True):
                    raise ValueError("Invalid AI source claim or SHA256 for "+file)
                (staging/file).write_bytes(data)
            (staging/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            target.mkdir(parents=True,exist_ok=True)
            for file in staging.iterdir():
                (target/file.name).write_bytes(file.read_bytes())
    return target

def main():
    p=argparse.ArgumentParser()
    p.add_argument("archive",type=Path)
    p.add_argument("--checkout",type=Path,default=Path(__file__).resolve().parents[1])
    args=p.parse_args()
    print("Installed verified R18 assets into",install(args.archive,args.checkout))

if __name__=="__main__":
    main()
