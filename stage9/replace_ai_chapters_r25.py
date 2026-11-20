"""R25: validate and apply replacement AI chapter images in one controlled batch.

Input folder: replacement.json + source image bytes. Replacement records must
explicitly claim independent AI generation with source provenance, and cannot
be crops/upscaled repairs. Script checks real JPEG/PNG pixel dimensions.
Defaults to dry-run; --apply changes source images and their manifest only after
every replacement has passed validation. Original bytes are preserved in a
backup folder (not committed).
"""
import argparse
import hashlib
import json
import shutil
import struct
import re
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/"ai-assets"
VALID_TYPES={"individual-generation","procedural-3d-render","procedural-vector-render","open-licensed-photography"}
SOURCE_BY_TYPE={
    "individual-generation":"AI_GENERATED",
    "procedural-3d-render":"PROCEDURAL_ORIGINAL",
    "procedural-vector-render":"PROCEDURAL_ORIGINAL",
    "open-licensed-photography":"OPEN_LICENSED_PHOTOGRAPHY",
}
VALID_EXT={".jpg",".jpeg",".png"}

def native_dimensions(raw):
    if raw.startswith(bytes.fromhex("89504e470d0a1a0a")) and len(raw)>=24:
        return struct.unpack(">II",raw[16:24])
    if raw[:2]!=bytes.fromhex("ffd8"):
        raise ValueError("only JPEG/PNG originals are accepted")
    pos=2
    while pos+4<len(raw):
        if raw[pos]!=255:
            pos+=1
            continue
        while pos<len(raw) and raw[pos]==255:
            pos+=1
        if pos>=len(raw): break
        marker=raw[pos]; pos+=1
        if marker in (0xD8,0xD9,0x01) or 0xD0<=marker<=0xD7: continue
        if pos+2>len(raw): break
        length=int.from_bytes(raw[pos:pos+2],"big")
        if length<2 or pos+length>len(raw): break
        if marker in (0xC0,0xC1,0xC2,0xC3,0xC5,0xC6,0xC7,0xC9,0xCA,0xCB,0xCD,0xCE,0xCF):
            if length<7: break
            height=int.from_bytes(raw[pos+3:pos+5],"big")
            width=int.from_bytes(raw[pos+5:pos+7],"big")
            return width,height
        pos+=length
    raise ValueError("cannot read native JPEG dimensions")

def plan(folder,manifest_path=ASSETS/"manifest.json"):
    folder=Path(folder)
    entries=json.loads((folder/"replacement.json").read_text(encoding="utf-8"))
    manifest=json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    if not isinstance(entries,list) or not entries:
        raise ValueError("replacement.json must be nonempty array")
    existing={(x["template"],x["chapter"]):x for x in manifest["assets"]}
    if len(existing)!=39: raise ValueError("39 chapter source manifest invalid")
    accepted=[]
    seen=set()
    for entry in entries:
        key=(entry.get("template"),entry.get("chapter"))
        if key in seen or key not in existing:
            raise ValueError("duplicate/unknown chapter "+str(key))
        seen.add(key)
        name=existing[key]["file"]
        supplied=entry.get("file")
        if supplied!=name or Path(name).name!=name or Path(name).suffix.lower() not in VALID_EXT:
            raise ValueError("replacement file must have the existing exact chapter filename: "+name)
        source_type=entry.get("sourceType")
        if source_type not in VALID_TYPES or entry.get("trueHighResolutionGenerated") is not True:
            raise ValueError("independent native-resolution original required: "+name)
        if entry.get("source")!=SOURCE_BY_TYPE[source_type] or entry.get("commercialUseTermsChecked") is not True:
            raise ValueError("source class or commercial-use evidence missing: "+name)
        for field in ("generationSystem","generationDate","sourceReference","termsUrl"):
            if not isinstance(entry.get(field),str) or not entry[field].strip():
                raise ValueError("missing provenance "+field+" for "+name)
        if source_type in ("procedural-3d-render","procedural-vector-render"):
            if entry.get("embeddedThirdPartyAssets") is not False or entry.get("thirdPartyAssets") is not False:
                raise ValueError("procedural original must explicitly declare both third-party asset flags=false: "+name)
        if source_type=="open-licensed-photography":
            for field in ("originalSourceUrl","creator","licenseId","licenseUrl","attribution","attributionText","downloadedAt"):
                if not isinstance(entry.get(field),str) or not entry[field].strip():
                    raise ValueError("open-license provenance missing "+field+" for "+name)
            if not entry["originalSourceUrl"].startswith("https://") or not entry["licenseUrl"].startswith("https://"):
                raise ValueError("open-license source and license URLs must use HTTPS: "+name)
            license_id=re.sub(r"[^A-Z0-9.]+","-",entry["licenseId"].upper()).strip("-")
            allowed=bool(re.fullmatch(r"(?:CC0(?:-1[.]0)?|PUBLIC-DOMAIN|PDM-1[.]0|CC-BY-(?:2[.]0|2[.]5|3[.]0|4[.]0)|CC-BY-SA-(?:2[.]0|2[.]5|3[.]0|4[.]0))",license_id))
            if not allowed:
                raise ValueError("license is not explicitly approved for commercial reuse: "+name)
            if license_id.startswith("CC-BY-SA-") and entry.get("shareAlikeCompatibilityReviewed") is not True:
                raise ValueError("CC-BY-SA compatibility review missing: "+name)
            try:
                datetime.fromisoformat(entry["downloadedAt"].replace("Z","+00:00"))
            except ValueError as exc:
                raise ValueError("downloadedAt must be an ISO-8601 timestamp: "+name) from exc
        raw=(folder/name).read_bytes()
        if len(raw)<1000 or len(raw)>5_000_000: raise ValueError("image file size out of bounds "+name)
        dimensions=native_dimensions(raw)
        try:
            with Image.open(BytesIO(raw)) as photo:
                if photo.format not in ("JPEG","PNG"):
                    raise ValueError("unexpected media encoding "+name)
                photo.load()
                if photo.size!=dimensions:
                    raise ValueError("header/decoded dimensions disagree: "+name)
        except (UnidentifiedImageError, OSError) as e:
            raise ValueError("unreadable or corrupted original image: "+name) from e
        if dimensions[0]<1280 or dimensions[1]<720:
            raise ValueError("native image below 1280×720: "+name+" "+str(dimensions))
        if list(dimensions)!=entry.get("nativeSourceDimensions"):
            raise ValueError("manifest native dimensions do not match original bytes: "+name)
        if hashlib.sha256(raw).hexdigest()==existing[key]["sha256"]:
            raise ValueError("unchanged image is not a replacement: "+name)
        updated=dict(existing[key])
        provenance_fields=("source","sourceType","trueHighResolutionGenerated","nativeSourceDimensions",
                  "generationSystem","generationDate","sourceReference","termsUrl","commercialUseTermsChecked",
                  "embeddedThirdPartyAssets","thirdPartyAssets","creator","licenseId","licenseUrl",
                  "originalSourceUrl","attribution","attributionText","downloadedAt","shareAlikeCompatibilityReviewed")
        for k in provenance_fields:
            if k in entry: updated[k]=entry[k]
            else: updated.pop(k,None)
        updated.pop("cropGrid",None)
        updated["sha256"]=hashlib.sha256(raw).hexdigest()
        updated["presentation"]="native-independent-generation"
        updated["presentationDimensions"]=list(dimensions)
        accepted.append((key,name,raw,updated))
    return manifest,accepted

def apply(folder,backup_dir=None,manifest_path=ASSETS/"manifest.json"):
    manifest,items=plan(folder,manifest_path)
    folder=Path(folder)
    backup=Path(backup_dir or folder/("backup-"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")))
    if backup.exists(): raise ValueError("backup directory already exists")
    backup.mkdir(parents=True)
    old_manifest=Path(manifest_path).read_bytes()
    (backup/"manifest.json").write_bytes(old_manifest)
    for _,name,_,_ in items: shutil.copy2(Path(manifest_path).parent/name,backup/name)
    changed={(key[0],key[1]):updated for key,_,_,updated in items}
    manifest["assets"]=[changed.get((r["template"],r["chapter"]),r) for r in manifest["assets"]]
    manifest["croppedSceneImages"]=sum(r.get("sourceType")=="crop-of-AI-generated-collage" for r in manifest["assets"])
    manifest["individualImages"]=39-manifest["croppedSceneImages"]
    manifest["artDirectionStatus"]="REVIEW_REQUIRED"
    manifest["notes"]="R25 validated native originals; human full-story visual approval remains required."
    try:
        for _,name,raw,_ in items:
            (Path(manifest_path).parent/name).write_bytes(raw)
        Path(manifest_path).write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+chr(10),encoding="utf-8")
    except Exception:
        for _,name,_,_ in items: shutil.copy2(backup/name,Path(manifest_path).parent/name)
        Path(manifest_path).write_bytes(old_manifest)
        raise
    return {"replacements":len(items),"collageRemaining":manifest["croppedSceneImages"],
            "backup":str(backup),"humanVisualReview":"HOLD"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("replacement_folder",type=Path)
    p.add_argument("--apply",action="store_true")
    p.add_argument("--backup",type=Path)
    args=p.parse_args()
    if args.apply:
        outcome=apply(args.replacement_folder,args.backup)
    else:
        _,items=plan(args.replacement_folder)
        outcome={"validatedReplacementCount":len(items),"changedFiles":[name for _,name,_,_ in items],
                 "action":"DRY_RUN_ONLY","humanVisualReview":"HOLD"}
    print(json.dumps(outcome,indent=2,ensure_ascii=False))

if __name__=="__main__": main()
