#!/usr/bin/env python3
"""Create a review-only contact sheet for all registered R53 original assets."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import cairosvg
from io import BytesIO

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "release/R53_PRODUCTION_ASSET_REGISTER.json"
ASSETS = ROOT / "stage9/ai-assets"
OUT = ROOT / "r53-review-contact-sheet.png"
CELL_W, CELL_H = 360, 250
THUMB_W, THUMB_H = 336, 189
COLS = 3
PAD, HEADER = 24, 52

def main():
    doc = json.loads(REGISTER.read_text(encoding="utf-8"))
    rows = doc.get("assets", [])
    if len(rows) != 33:
        raise SystemExit(f"Expected 33 registered assets, found {len(rows)}")
    rows = sorted(rows, key=lambda r: (r["template"], int(r["chapter"])))
    groups = []
    for template in sorted({r["template"] for r in rows}):
        group = [r for r in rows if r["template"] == template]
        groups.extend(group)
    width = PAD * 2 + COLS * CELL_W
    height = PAD * 2 + HEADER + ((len(rows) + COLS - 1) // COLS) * CELL_H
    sheet = Image.new("RGB", (width, height), (13, 18, 24))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 15)
        small = ImageFont.truetype("DejaVuSans.ttf", 11)
        heading = ImageFont.truetype("DejaVuSans.ttf", 22)
    except OSError:
        font = small = heading = ImageFont.load_default()
    draw.text((PAD, PAD), "R53 ORIGINAL ASSETS · HUMAN REVIEW ONLY", font=heading, fill=(235, 242, 246))
    draw.text((PAD, PAD + 32), "33 generated slots · source/hash/dimensions checked by gate · NOT APPROVED FOR PRODUCTION", font=small, fill=(183, 196, 207))
    for i, row in enumerate(rows):
        x = PAD + (i % COLS) * CELL_W
        y = PAD + HEADER + (i // COLS) * CELL_H
        file_path = ASSETS / row["file"]
        if not file_path.is_file():
            raise SystemExit(f"Missing asset: {file_path}")
        raw = file_path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != row.get("sha256"):
            raise SystemExit(f"SHA-256 mismatch: {row['slotId']}")
        if file_path.suffix.lower() == ".svg":
            png = cairosvg.svg2png(bytestring=raw, output_width=THUMB_W, output_height=THUMB_H)
            image = Image.open(BytesIO(png)).convert("RGB")
        else:
            image = Image.open(BytesIO(raw)).convert("RGB")
            if list(image.size) != row.get("nativeDimensions"):
                raise SystemExit(f"Dimension mismatch: {row['slotId']} {image.size}")
            image.thumbnail((THUMB_W, THUMB_H), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (THUMB_W, THUMB_H), (28, 36, 44))
        tile.paste(image, ((THUMB_W-image.width)//2, (THUMB_H-image.height)//2))
        sheet.paste(tile, (x, y))
        draw.rectangle((x, y, x+THUMB_W-1, y+THUMB_H-1), outline=(85, 102, 116), width=1)
        draw.text((x, y+THUMB_H+8), row["slotId"], font=font, fill=(240, 245, 248))
        draw.text((x, y+THUMB_H+31), f"{row['file']} · {len(raw):,} bytes · {digest[:12]}…", font=small, fill=(165, 181, 194))
    sheet.save(OUT, "PNG", optimize=True)
    print(json.dumps({"contactSheet": str(OUT), "assets": len(rows), "sha256Verified": True,
                      "humanVisualApproval": False, "productionEligible": False}, indent=2))

if __name__ == "__main__":
    main()
