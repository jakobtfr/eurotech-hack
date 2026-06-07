"""Clean marker visualisations for 4H-SiC dislocations (reuses the trained YOLO11-OBB).

For tiny point-like defects a diffuse heatmap is the wrong tool: a TD is ~19 px in a
2500 px image (<1 patch of the DINOv2 grid). Instead we mark each detection with a
bold coloured shape, sized to be clearly visible:

  - TD  (threading, dark spots)  -> GREEN circle
  - BPD (basal-plane, dark lines) -> ORANGE oriented rectangle

Each defect is numbered and enlarged in a crop strip below the full image, matching
the style of sic_results/medium_defect_mosaic_demo. Outputs into
``results/sic_4h_detection_markers/``:
  - ``posters/<name>.png`` : full annotated image + numbered enlarged crops
  - ``annotated/<name>.png``: just the full annotated image
  - ``gallery.png``         : 2-column mosaic of posters, busiest first
  - ``summary.json``

Run: ``.venv/bin/python scripts/sic_detection_markers.py``
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO

REPO = Path(__file__).resolve().parent.parent
WEIGHTS = REPO / "sic_results" / "yolo11n_obb_cbms_sic" / "weights" / "best.pt"
VAL_IMAGES = REPO / "datasets" / "sic_dislocation_detection_db" / "leakage_safe" / "images" / "val"
OUT = REPO / "results" / "sic_4h_detection_markers"
DISPLAY = 1100         # full-image render width
MAX_IMAGES = 24
CONF = 0.25
TD_COLOR = (255, 40, 40)     # red
BPD_COLOR = (255, 150, 0)    # orange
CROP = 220                   # crop size (display px) around each defect
CROP_COLS = 5


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in ("Arial.ttf", "DejaVuSans.ttf", "Helvetica.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_marker(draw: ImageDraw.ImageDraw, corners: np.ndarray, cls: int, idx: int,
                font: ImageFont.ImageFont) -> tuple[float, float]:
    """Draw a numbered green circle (TD) or orange box (BPD); return the centre."""
    cx, cy = corners[:, 0].mean(), corners[:, 1].mean()
    if cls == 0:  # TD -> circle
        r = 22
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=TD_COLOR, width=4)
        col = TD_COLOR
    else:         # BPD -> oriented rectangle, slightly inflated so it stays visible
        c = corners - corners.mean(0)
        c *= 1.35
        c += corners.mean(0)
        draw.polygon([tuple(p) for p in c], outline=BPD_COLOR, width=4)
        col = BPD_COLOR
    tag = str(idx)
    tx, ty = cx + 24, cy - 30
    draw.rectangle([tx - 2, ty - 2, tx + 9 * len(tag) + 4, ty + 22], fill=(0, 0, 0))
    draw.text((tx + 1, ty), tag, fill=col, font=font)
    return cx, cy


def main() -> None:
    if not WEIGHTS.exists():
        raise SystemExit(f"weights not found: {WEIGHTS}")
    images = sorted(VAL_IMAGES.glob("*.jpg"))[:MAX_IMAGES]
    for sub in ("posters", "annotated"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    model = YOLO(str(WEIGHTS))
    title_font, tag_font, small = _font(30), _font(20), _font(18)
    posters: list[tuple[int, Image.Image]] = []
    summary: list[dict] = []

    for path in images:
        result = model.predict(str(path), conf=CONF, verbose=False)[0]
        orig_full = Image.open(path).convert("L").convert("RGB")
        ow, oh = orig_full.size
        dh = int(DISPLAY * oh / ow)
        base = orig_full.resize((DISPLAY, dh), Image.BILINEAR)
        sx, sy = DISPLAY / ow, dh / oh

        annotated = base.copy()
        adraw = ImageDraw.Draw(annotated)
        obb = result.obb
        n = 0 if obb is None else len(obb)
        crops: list[tuple[int, int, Image.Image]] = []  # (idx, cls, crop)
        counts = {"TD": 0, "BPD": 0}

        for i in range(n):
            corners = obb.xyxyxyxy[i].cpu().numpy().reshape(4, 2)
            corners[:, 0] *= sx
            corners[:, 1] *= sy
            cls = int(obb.cls[i].cpu())
            counts["TD" if cls == 0 else "BPD"] += 1
            idx = i + 1
            cx, cy = draw_marker(adraw, corners, cls, idx, tag_font)
            # enlarged crop from the full-res original, re-annotated.
            fcx, fcy = cx / sx, cy / sy
            half = int(CROP / 2 / (DISPLAY / ow))
            box = (int(fcx - half), int(fcy - half), int(fcx + half), int(fcy + half))
            crop = orig_full.crop(box).resize((CROP, CROP), Image.BILINEAR)
            cd = ImageDraw.Draw(crop)
            col = TD_COLOR if cls == 0 else BPD_COLOR
            if cls == 0:
                cd.ellipse([CROP / 2 - 30, CROP / 2 - 30, CROP / 2 + 30, CROP / 2 + 30], outline=col, width=3)
            cd.rectangle([0, 0, CROP - 1, CROP - 1], outline=col, width=4)
            cd.text((6, 4), f"#{idx} {'TD' if cls == 0 else 'BPD'}", fill=col, font=small)
            crops.append((idx, cls, crop))

        annotated.save(OUT / "annotated" / f"{path.stem.replace(' ', '_')}.png")

        # Poster: header + full annotated image + crop strip.
        crop_rows = (len(crops) + CROP_COLS - 1) // CROP_COLS if crops else 0
        head_h, gap = 70, 12
        strip_h = crop_rows * (CROP + 28) + (gap if crop_rows else 0)
        poster = Image.new("RGB", (max(DISPLAY, CROP_COLS * (CROP + gap)), head_h + dh + strip_h), (250, 250, 250))
        pd = ImageDraw.Draw(poster)
        pd.text((12, 10), f"4H-SiC dislocations — {path.name}", fill=(0, 0, 0), font=title_font)
        pd.text((12, 44), f"RED circle = TD ({counts['TD']})    ORANGE box = BPD ({counts['BPD']})    conf>{CONF}",
                fill=(60, 60, 60), font=small)
        poster.paste(annotated, (0, head_h))
        for j, (_idx, _cls, crop) in enumerate(crops):
            r, c = divmod(j, CROP_COLS)
            x = c * (CROP + gap)
            y = head_h + dh + gap + r * (CROP + 28)
            poster.paste(crop, (x, y))
        poster.save(OUT / "posters" / f"{path.stem.replace(' ', '_')}.png")

        posters.append((n, poster))
        summary.append({"image": path.name, **counts, "detections": n})

    # 2-column mosaic of posters, busiest first.
    posters.sort(key=lambda t: t[0], reverse=True)
    panels = [p for _, p in posters if _ > 0] or [p for _, p in posters]
    if panels:
        tw = max(p.width for p in panels)
        scale = 540 / tw
        thumbs = [p.resize((int(p.width * scale), int(p.height * scale))) for p in panels]
        colw = max(t.width for t in thumbs)
        rowh = max(t.height for t in thumbs)
        cols = 2
        rows = (len(thumbs) + cols - 1) // cols
        gallery = Image.new("RGB", (colw * cols + 30, rowh * rows + 30), (255, 255, 255))
        for i, t in enumerate(thumbs):
            r, c = divmod(i, cols)
            gallery.paste(t, (c * (colw + 10) + 10, r * (rowh + 10) + 10))
        gallery.save(OUT / "gallery.png")

    (OUT / "summary.json").write_text(json.dumps({
        "weights": str(WEIGHTS.relative_to(REPO)),
        "conf_threshold": CONF,
        "legend": {"TD": "green circle", "BPD": "orange box"},
        "total_TD": sum(s["TD"] for s in summary),
        "total_BPD": sum(s["BPD"] for s in summary),
        "images": summary,
    }, indent=2))
    print(f"wrote {len(images)} posters -> {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
