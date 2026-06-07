"""Export MIIC anomaly-detection results into a visible, human-readable folder.

Reads a frozen run (predictions + heatmaps + overlays) and writes triptychs
(original | heatmap | overlay) plus a montage gallery into miic_results/, so the
defect highlights are easy to browse outside the gitignored runs/ tree.
"""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parent.parent
RUN = REPO / "runs" / "20260606T193603Z_dinov2_pca_baseline_v1_k16_seed17"
SPLIT = REPO / "data" / "splits" / "miic_partial.csv"
OUT = REPO / "miic_results"
DISPLAY = 448
TOP_ANOMALIES = 16  # for the montage gallery
NORMAL_SAMPLES = 8


def safe(name: str) -> str:
    return "".join(c if c.isalnum() or c in {"-", "_"} else "_" for c in name)


def load_original(image_path: str) -> Image.Image:
    """Match the overlay base: grayscale->RGB, top-left 448 crop, resize 448."""
    img = Image.open(REPO / image_path).convert("L").convert("RGB")
    w, h = img.size
    side = min(448, w, h)
    img = img.crop((0, 0, side, side))
    return img.resize((DISPLAY, DISPLAY), Image.Resampling.BILINEAR)


def label(img: Image.Image, text: str) -> Image.Image:
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, len(text) * 7 + 8, 18], fill=(0, 0, 0))
    draw.text((4, 4), text, fill=(255, 255, 255))
    return img


def triptych(orig: Image.Image, heat: Image.Image, over: Image.Image, caption: str) -> Image.Image:
    panel = Image.new("RGB", (DISPLAY * 3 + 20, DISPLAY + 24), (245, 245, 245))
    panel.paste(label(orig.copy(), "original"), (0, 24))
    panel.paste(label(heat.copy(), "heatmap"), (DISPLAY + 10, 24))
    panel.paste(label(over.copy(), "overlay (defecto)"), (DISPLAY * 2 + 20, 24))
    ImageDraw.Draw(panel).text((4, 6), caption, fill=(0, 0, 0))
    return panel


def main() -> None:
    if not RUN.exists():
        raise SystemExit(f"run not found: {RUN}")
    label_by_tile = {r["tile_id"]: r for r in csv.DictReader(SPLIT.open())}
    preds = [json.loads(line) for line in (RUN / "predictions.jsonl").open()]

    anom, good = [], []
    for p in preds:
        row = label_by_tile.get(p["tile_id"], {})
        (anom if row.get("label") == "anomaly" else good).append((p, row))
    anom.sort(key=lambda t: t[0].get("normalized_anomaly_score") or 0, reverse=True)
    good.sort(key=lambda t: t[0].get("normalized_anomaly_score") or 0)

    for sub in ("anomaly_comparisons", "normal_comparisons"):
        d = OUT / sub
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True, exist_ok=True)

    def render(p: dict, row: dict, rank: int, kind: str) -> Image.Image:
        slug = safe(p["tile_id"])
        orig = load_original(row["image_path"])
        heat = Image.open(RUN / "heatmaps" / f"{slug}.png").convert("RGB").resize((DISPLAY, DISPLAY))
        over = Image.open(RUN / "overlays" / f"{slug}.png").convert("RGB").resize((DISPLAY, DISPLAY))
        score = p.get("normalized_anomaly_score") or 0.0
        sid = row.get("source_image_id", "")
        cap = f"#{rank:03d} {kind}  {sid}  score={score:.3f}  decision={p['decision']}"
        tri = triptych(orig, heat, over, cap)
        tri.save(OUT / f"{kind}_comparisons" / f"{rank:03d}_{sid}.png")
        return tri

    print(f"anomalies={len(anom)} normals={len(good)}")
    montage_tiles = []
    for i, (p, row) in enumerate(anom, 1):
        tri = render(p, row, i, "anomaly")
        if i <= TOP_ANOMALIES:
            montage_tiles.append(tri)
    for i, (p, row) in enumerate(good[:NORMAL_SAMPLES], 1):
        render(p, row, i, "normal")

    # Montage gallery of top anomalies (2 columns).
    if montage_tiles:
        tw, th = montage_tiles[0].size
        cols = 2
        rows = (len(montage_tiles) + cols - 1) // cols
        gallery = Image.new("RGB", (tw * cols + 10, th * rows + 10), (255, 255, 255))
        for idx, tri in enumerate(montage_tiles):
            r, c = divmod(idx, cols)
            gallery.paste(tri, (c * (tw + 10), r * (th + 10)))
        gallery.save(OUT / "gallery_top_anomalies.png")
        print(f"gallery: {len(montage_tiles)} top anomalies")

    shutil.copy(RUN / "metrics.json", OUT / "metrics.json")
    print(f"done -> {OUT}")


if __name__ == "__main__":
    main()
