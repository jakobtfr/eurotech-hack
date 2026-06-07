"""Export the SiC 4H DINOv2+PCA anomaly run into a browsable results folder.

Mirrors scripts/export_miic_results.py: reads the frozen run (heatmaps + overlays),
writes original | heatmap | overlay triptychs and a montage gallery into
results/sic_4h_anomaly_heatmaps/ so the unsupervised highlights are easy to browse.

Run: ``.venv/bin/python scripts/export_sic_anomaly_results.py``
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parent.parent
RUN = REPO / "runs" / "20260606T225256Z_dinov2_pca_baseline_v1_k16_seed17"
SPLIT = REPO / "data" / "splits" / "sic_4h.csv"
OUT = REPO / "results" / "sic_4h_anomaly_heatmaps"
DISPLAY = 448


def load_original(image_path: str) -> Image.Image:
    """Match the overlay base: full-image grayscale->RGB resized to DISPLAY."""
    img = Image.open(REPO / image_path).convert("L").convert("RGB")
    return img.resize((DISPLAY, DISPLAY), Image.Resampling.BILINEAR)


def label(img: Image.Image, text: str) -> Image.Image:
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, len(text) * 7 + 8, 18], fill=(0, 0, 0))
    draw.text((4, 4), text, fill=(255, 255, 255))
    return img


def main() -> None:
    if not RUN.exists():
        raise SystemExit(f"run not found: {RUN}")
    (OUT / "triptychs").mkdir(parents=True, exist_ok=True)
    label_by_tile = {r["tile_id"]: r for r in csv.DictReader(SPLIT.open())}
    preds = [json.loads(line) for line in (RUN / "predictions.jsonl").open()]
    preds.sort(key=lambda p: p.get("raw_anomaly_score", 0.0), reverse=True)

    panels: list[Image.Image] = []
    for rank, p in enumerate(preds, 1):
        row = label_by_tile.get(p["tile_id"])
        if row is None:
            continue
        orig = load_original(row["image_path"])
        heat = Image.open(REPO / p["heatmap_path"]).convert("RGB").resize((DISPLAY, DISPLAY))
        over = Image.open(REPO / p["overlay_path"]).convert("RGB").resize((DISPLAY, DISPLAY))

        panel = Image.new("RGB", (DISPLAY * 3 + 20, DISPLAY + 24), (245, 245, 245))
        cap = (
            f"#{rank:03d}  {row['source_image_id']}  "
            f"score={p.get('raw_anomaly_score', 0):.3f}  decision={p.get('decision', '')}"
        )
        ImageDraw.Draw(panel).text((4, 6), cap, fill=(0, 0, 0))
        panel.paste(label(orig.copy(), "original PL"), (0, 24))
        panel.paste(label(heat.copy(), "anomaly heatmap"), (DISPLAY + 10, 24))
        panel.paste(label(over.copy(), "overlay"), (DISPLAY * 2 + 20, 24))
        panel.save(OUT / "triptychs" / f"{rank:03d}_{row['source_image_id']}.png")
        panels.append(panel)

    # MIIC-style mosaic: 2-column montage of triptychs, most anomalous first
    # (preds are already sorted by raw_anomaly_score, descending).
    if panels:
        tw, th = panels[0].size
        cols = 2
        rows = (len(panels) + cols - 1) // cols
        gallery = Image.new("RGB", (tw * cols + 10, th * rows + 10), (255, 255, 255))
        for i, panel in enumerate(panels):
            r, c = divmod(i, cols)
            gallery.paste(panel, (c * (tw + 10) + 5, r * (th + 10) + 5))
        gallery.save(OUT / "gallery_top_anomalies.png")

    (OUT / "summary.json").write_text(json.dumps({
        "run": str(RUN.relative_to(REPO)),
        "method": "DINOv2 (vits14, frozen) + PCA-residual, k=16 shots, CLAHE preprocess",
        "note": "Unsupervised: no SiC labels used. pixel/image AUROC null (no GT anomaly labels).",
        "n_test_images": len(panels),
        "scores": [
            {"image": label_by_tile[p["tile_id"]]["source_image_id"],
             "raw_anomaly_score": p.get("raw_anomaly_score"),
             "decision": p.get("decision")}
            for p in preds if p["tile_id"] in label_by_tile
        ],
    }, indent=2))
    print(f"wrote {len(panels)} triptychs -> {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
