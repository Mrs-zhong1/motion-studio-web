#!/usr/bin/env python3
"""Independent Pillow post-render finish for R50 review-only imagery.

Adds restrained, template-specific editorial typography after Blender exits.
Never changes review/rights status to approved.
"""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

COPY = {
    "agency": ("FORM FOLLOWS FEELING", "CREATIVE AGENCY / DIGITAL FLAGSHIP", "A considered space for ideas, identity and motion.", "01 — BRAND WORLDS"),
    "product-3d": ("SOUND IN PURE FORM", "OBJECT STUDY / INDUSTRIAL DESIGN", "Precision surfaces. Tactile controls. Quiet confidence.", "02 — PRODUCT DETAIL"),
    "gallery": ("THE ART OF STILLNESS", "EXHIBITION / SPATIAL EXPERIENCE", "Sculptural forms arranged as a living collection.", "03 — CURATED SPACE"),
}

def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()

def finish(path, key):
    image = Image.open(path).convert("RGBA")
    if image.size != (1600, 900):
        raise ValueError(f"{path}: expected 1600x900, got {image.size}")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    # Narrow editorial column; the rendered object remains the dominant image.
    draw.rectangle((1110, 0, 1600, 900), fill=(7, 13, 22, 222))
    draw.rectangle((1110, 0, 1116, 900), fill=(218, 160, 93, 255))
    eyebrow, title, description, footer = COPY[key]
    draw.text((1170, 170), eyebrow, font=font(15, True), fill=(195, 205, 215, 255))
    words = title.split()
    lines, line = [], ""
    for word in words:
        trial = (line + " " + word).strip()
        if draw.textbbox((0, 0), trial, font=font(42, True))[2] > 365 and line:
            lines.append(line); line = word
        else:
            line = trial
    if line: lines.append(line)
    y = 260
    for text in lines:
        draw.text((1170, y), text, font=font(42, True), fill=(248, 246, 239, 255))
        y += 58
    draw.line((1170, y + 28, 1510, y + 28), fill=(218, 160, 93, 220), width=2)
    y += 72
    # Controlled line wrapping for a compact supporting statement.
    line = ""
    for word in description.split():
        trial = (line + " " + word).strip()
        if draw.textbbox((0, 0), trial, font=font(18))[2] > 330 and line:
            draw.text((1170, y), line, font=font(18), fill=(183, 195, 207, 255)); y += 31; line = word
        else:
            line = trial
    if line:
        draw.text((1170, y), line, font=font(18), fill=(183, 195, 207, 255))
    draw.text((1170, 790), footer, font=font(13, True), fill=(218, 160, 93, 255))
    image = Image.alpha_composite(image, overlay).convert("RGB")
    image.save(path, format="PNG", optimize=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("r50-review"))
    args = parser.parse_args()
    manifest_path = args.out / "manifest.json"
    rows = json.loads(manifest_path.read_text(encoding="utf-8"))
    script_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    for row in rows:
        key = row["template"]
        if key in COPY:
            target = args.out / row["file"]
            finish(target, key)
            raw = target.read_bytes()
            row["sha256"] = hashlib.sha256(raw).hexdigest()
            row["dimensions"] = [1600, 900]
            row["editorialFinishSha256"] = script_hash
            row["reviewStatus"] = "HUMAN_VISUAL_REVIEW_REQUIRED"
            row["productionEligible"] = False
    manifest_path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"finished": 3, "reviewOnly": True, "productionEligible": False}, indent=2))

if __name__ == "__main__":
    main()
