#!/usr/bin/env python3
"""R50 review-only finishing pass.

Editorial typography is integrated into the rendered scene. No fixed side panel,
split canvas, opaque column, or template-wide panel is permitted. This stage
never approves artwork or changes licensing/release status.
"""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

COPY = {
    "agency": ("01 / CREATIVE WORLDS", "FORM FOLLOWS FEELING", "A considered space for ideas, identity and motion."),
    "product-3d": ("02 / OBJECT STUDY", "PRECISION IN FRAME", "Optical glass. Tactile controls. A camera built for the moment."),
    "gallery": ("03 / CURATED SPACE", "THE ART OF STILLNESS", "Sculptural forms arranged as a living collection."),
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

def wrap(draw, text, face, max_width):
    lines, current = [], ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if current and draw.textbbox((0, 0), trial, font=face)[2] > max_width:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines

def finish(path, key):
    image = Image.open(path).convert("RGBA")
    if image.size != (1600, 900):
        raise ValueError(f"{path}: expected 1600x900, got {image.size}")
    # A full-width bottom fade preserves a single uninterrupted image field.
    # The fade is tonal, not a panel: it has no vertical edge or separate column.
    fade = Image.new("RGBA", image.size, (0, 0, 0, 0))
    pixels = fade.load()
    for y in range(590, 900):
        t = (y - 590) / 310
        alpha = int(12 + 164 * (t ** 1.55))
        for x in range(1600):
            pixels[x, y] = (5, 10, 18, alpha)
    image = Image.alpha_composite(image, fade)
    draw = ImageDraw.Draw(image)
    eyebrow, title, description = COPY[key]
    left = 92
    draw.text((left, 652), eyebrow, font=font(15, True), fill=(226, 177, 111, 255), stroke_width=0)
    title_face = font(45, True)
    title_lines = wrap(draw, title, title_face, 1060)
    y = 690
    for line in title_lines[:2]:
        draw.text((left, y), line, font=title_face, fill=(250, 248, 242, 255))
        y += 54
    desc_y = min(820, y + 8)
    draw.text((left, desc_y), description, font=font(18), fill=(216, 224, 232, 255))
    # A restrained index floats at the far edge; it does not create a column.
    index = {"agency": "A / 01", "product-3d": "P / 02", "gallery": "G / 03"}[key]
    draw.text((1430, 842), index, font=font(14, True), fill=(226, 177, 111, 255))
    image.convert("RGB").save(path, format="PNG", optimize=True)

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
            row["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
            row["dimensions"] = [1600, 900]
            row["editorialFinishSha256"] = script_hash
            row["reviewStatus"] = "HUMAN_VISUAL_REVIEW_REQUIRED"
            row["productionEligible"] = False
    manifest_path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"finished": 3, "reviewOnly": True, "fixedSidePanel": False, "productionEligible": False}, indent=2))

if __name__ == "__main__":
    main()
