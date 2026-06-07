"""One large overview image of the whole 4H-SiC validation set with every detected
imperfection marked (RED circle = TD, ORANGE box = BPD).

Runs the trained YOLO11-OBB over ALL validation PL frames, annotates each, and tiles
the frames that contain detections into a single big composite, plus a high-res
standalone of the busiest frame.

Outputs into ``results/sic_4h_detection_markers/``:
  - ``overview_all_defects.png`` : big montage of every frame that has defects
  - ``overview_busiest_frame.png``: single large annotated frame (most defects)

Run: ``.venv/bin/python scripts/sic_detection_overview.py``
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO

REPO = Path(__file__).resolve().parent.parent
WEIGHTS = REPO / "sic_results" / "yolo11n_obb_cbms_sic" / "weights" / "best.pt"
VAL_IMAGES = REPO / "datasets" / "sic_dislocation_detection_db" / "leakage_safe" / "images" / "val"
OUT = REPO / "results" / "sic_4h_detection_markers"
CONF = 0.25
TD_COLOR = (255, 40, 40)     # red
BPD_COLOR = (255, 150, 0)    # orange
TILE_W = 620                 # per-frame width in the montage
COLS = 5
FULL_W = 2200                # standalone busiest-frame width


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in ("Arial.ttf", "DejaVuSans.ttf", "Helvetica.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def annotate(
    path: Path,
    model: YOLO,
    width: int,
    line: int,
    rad: int,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
) -> tuple[Image.Image, int, int]:
    result = model.predict(str(path), conf=CONF, verbose=False)[0]
    full = Image.open(path).convert("L").convert("RGB")
    ow, oh = full.size
    h = int(width * oh / ow)
    img = full.resize((width, h), Image.BILINEAR)
    draw = ImageDraw.Draw(img)
    sx, sy = width / ow, h / oh
    obb = result.obb
    n = 0 if obb is None else len(obb)
    td = bpd = 0
    for i in range(n):
        corners = obb.xyxyxyxy[i].cpu().numpy().reshape(4, 2)
        corners[:, 0] *= sx
        corners[:, 1] *= sy
        cls = int(obb.cls[i].cpu())
        cx, cy = corners[:, 0].mean(), corners[:, 1].mean()
        if cls == 0:
            draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=TD_COLOR, width=line)
            td += 1
        else:
            c = (corners - corners.mean(0)) * 1.35 + corners.mean(0)
            draw.polygon([tuple(p) for p in c], outline=BPD_COLOR, width=line)
            bpd += 1
    draw.text((6, 4), f"{path.name}", fill=(255, 255, 0), font=font)
    return img, td, bpd


def main() -> None:
    images = sorted(VAL_IMAGES.glob("*.jpg"))
    model = YOLO(str(WEIGHTS))
    small = _font(16)

    annotated: list[tuple[int, Image.Image]] = []  # (n_defects, image) for frames with defects
    busiest = None  # (n, path)
    tot_td = tot_bpd = 0
    for path in images:
        img, td, bpd = annotate(path, model, TILE_W, line=3, rad=16, font=small)
        n = td + bpd
        tot_td += td
        tot_bpd += bpd
        if n > 0:
            annotated.append((n, img))
            if busiest is None or n > busiest[0]:
                busiest = (n, path)

    print(f"frames with defects: {len(annotated)}/{len(images)}  TD={tot_td} BPD={tot_bpd}")

    # Big montage of every frame with defects.
    annotated.sort(key=lambda t: t[0], reverse=True)
    panels = [im for _, im in annotated]
    if panels:
        tw, th = panels[0].size
        rows = (len(panels) + COLS - 1) // COLS
        gap = 8
        title_h = 60
        canvas = Image.new("RGB", (COLS * tw + (COLS + 1) * gap, title_h + rows * (th + gap) + gap), (255, 255, 255))
        d = ImageDraw.Draw(canvas)
        d.text((14, 12), f"4H-SiC validation — all detected imperfections   "
                          f"(RED circle = TD {tot_td}   ORANGE box = BPD {tot_bpd})",
               fill=(0, 0, 0), font=_font(26))
        for i, im in enumerate(panels):
            r, c = divmod(i, COLS)
            canvas.paste(im, (gap + c * (tw + gap), title_h + gap + r * (th + gap)))
        canvas.save(OUT / "overview_all_defects.png")
        print(f"saved overview_all_defects.png  {canvas.size}")

    # High-res standalone of the busiest frame.
    if busiest:
        img, td, bpd = annotate(busiest[1], model, FULL_W, line=5, rad=34, font=_font(30))
        header = Image.new("RGB", (img.width, img.height + 60), (250, 250, 250))
        ImageDraw.Draw(header).text((14, 16), f"4H-SiC — {busiest[1].name}   "
                                              f"RED circle = TD ({td})   ORANGE box = BPD ({bpd})",
                                    fill=(0, 0, 0), font=_font(30))
        header.paste(img, (0, 60))
        header.save(OUT / "overview_busiest_frame.png")
        print(f"saved overview_busiest_frame.png  {header.size}  ({busiest[1].name})")


if __name__ == "__main__":
    main()
