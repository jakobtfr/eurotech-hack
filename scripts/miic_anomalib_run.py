"""Train + evaluate a published anomaly-detection model (CFA or DRAEM) on MIIC.

Uses the same MIIC split as the DINOv2+PCA baseline (692 train-good / 347 test-good
+ 116 anomaly), via symlink dirs under runs/anomalib_miic/data/. MIIC has no masks,
so only image-level metrics (AUROC, F1) are reported.

Writes into miic_results/<model>/:
  - metrics.json     : image-level AUROC / F1 + run config
  - heatmaps/        : sample original|heatmap|overlay triptychs (anomaly + normal)

Run (isolated env):
  .venv-anomalib/bin/python scripts/miic_anomalib_run.py --model cfa --epochs 5
  .venv-anomalib/bin/python scripts/miic_anomalib_run.py --model draem --epochs 15
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "runs" / "anomalib_miic" / "data"
DISPLAY = 384


def build_datamodule(image_size: int) -> Any:
    from anomalib.data import Folder
    from anomalib.data.utils import TestSplitMode, ValSplitMode
    from torchvision.transforms.v2 import Compose, Resize

    tf = Compose([Resize((image_size, image_size), antialias=True)])
    dm = Folder(
        name="miic",
        root=DATA,
        normal_dir="train_normal",
        normal_test_dir="test_normal",
        abnormal_dir="anomaly",
        test_split_mode=TestSplitMode.FROM_DIR,   # test = normal_test_dir + abnormal_dir
        val_split_mode=ValSplitMode.SAME_AS_TEST,
        train_batch_size=8,
        eval_batch_size=8,
        num_workers=4,
        augmentations=tf,
    )
    dm.setup()
    return dm


def build_model(name: str) -> Any:
    from anomalib.models import Cfa, Draem
    if name == "cfa":
        return Cfa()
    if name == "draem":
        return Draem()  # synthetic anomalies (perlin) when no DTD dir given
    raise SystemExit(f"unknown model {name!r}")


def label(img: Image.Image, text: str) -> Image.Image:
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, len(text) * 7 + 8, 18], fill=(0, 0, 0))
    d.text((4, 4), text, fill=(255, 255, 255))
    return img


def colorize(amap: np.ndarray) -> np.ndarray:
    x = np.clip((amap - amap.min()) / (np.ptp(amap) + 1e-9), 0, 1)
    r = np.clip(1.5 - np.abs(4 * x - 3), 0, 1)
    g = np.clip(1.5 - np.abs(4 * x - 2), 0, 1)
    b = np.clip(1.5 - np.abs(4 * x - 1), 0, 1)
    return (np.stack([r, g, b], -1) * 255).astype(np.uint8)


def collect_predictions(
    engine: Any, model: Any, dm: Any
) -> list[tuple[bool, float, str, np.ndarray | None]]:
    """One predict pass -> list of (is_anomaly, anomaly_score, image_path, anomaly_map)."""
    preds = engine.predict(model=model, dataloaders=dm.test_dataloader())
    items: list[tuple[bool, float, str, np.ndarray | None]] = []
    for batch in preds or []:
        maps = batch.anomaly_map
        scores = batch.pred_score
        paths = batch.image_path
        labels = batch.gt_label
        for i in range(len(paths)):
            amap = maps[i].squeeze().cpu().numpy() if maps is not None else None
            items.append((bool(labels[i]), float(scores[i]), paths[i], amap))
    return items


def compute_metrics(items: list[tuple[bool, float, str, np.ndarray | None]]) -> dict:
    """Image-level AUROC/AUPR via sklearn, directly comparable to the DINOv2 baseline."""
    from sklearn.metrics import average_precision_score, roc_auc_score

    y = np.array([1 if a else 0 for a, _, _, _ in items])
    s = np.array([sc for _, sc, _, _ in items])
    return {
        "image_auroc": float(roc_auc_score(y, s)),
        "image_aupr": float(average_precision_score(y, s)),
        "n_test": int(len(y)),
        "n_anomaly": int(y.sum()),
        "n_normal": int((y == 0).sum()),
    }


def save_triptychs(items: list[tuple[bool, float, str, np.ndarray | None]], out: Path, n_each: int = 6) -> None:
    out.mkdir(parents=True, exist_ok=True)
    anom = sorted([x for x in items if x[0]], key=lambda x: -x[1])[:n_each]
    good = sorted([x for x in items if not x[0]], key=lambda x: x[1])[:n_each]
    for kind, group in (("anomaly", anom), ("normal", good)):
        for rank, (_, score, path, amap) in enumerate(group, 1):
            orig = Image.open(path).convert("L").convert("RGB").resize((DISPLAY, DISPLAY))
            if amap is None:
                continue
            heat = Image.fromarray(colorize(amap)).resize((DISPLAY, DISPLAY))
            a = (np.clip((amap - amap.min()) / (np.ptp(amap) + 1e-9), 0, 1) ** 0.6 * 0.7)
            a = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize((DISPLAY, DISPLAY))) / 255.0
            over = (np.asarray(orig) * (1 - a[..., None]) + np.asarray(heat) * a[..., None]).astype(np.uint8)
            panel = Image.new("RGB", (DISPLAY * 3 + 20, DISPLAY + 24), (245, 245, 245))
            ImageDraw.Draw(panel).text((4, 6), f"{kind} #{rank}  score={score:.3f}  {Path(path).name}", fill=(0, 0, 0))
            panel.paste(label(orig.copy(), "original"), (0, 24))
            panel.paste(label(heat.copy(), "heatmap"), (DISPLAY + 10, 24))
            panel.paste(label(Image.fromarray(over), "overlay"), (DISPLAY * 2 + 20, 24))
            panel.save(out / f"{kind}_{rank:02d}.png")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=["cfa", "draem"])
    ap.add_argument("--epochs", type=int, default=10)
    ap.add_argument("--image-size", type=int, default=256)
    ap.add_argument("--accelerator", default="auto")
    args = ap.parse_args()

    from anomalib.engine import Engine

    dm = build_datamodule(args.image_size)
    model = build_model(args.model)
    run_dir = REPO / "runs" / "anomalib_miic" / args.model
    engine = Engine(
        default_root_dir=str(run_dir),
        max_epochs=args.epochs,
        accelerator=args.accelerator,
        devices=1,
        logger=False,
    )
    engine.fit(model=model, datamodule=dm)
    items = collect_predictions(engine, model, dm)
    metrics = compute_metrics(items)

    out = REPO / "miic_results" / args.model
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.json").write_text(json.dumps({
        "model": args.model,
        "epochs": args.epochs,
        "image_size": args.image_size,
        "accelerator": args.accelerator,
        "split": "miic_partial (692 train-good / 347 test-good / 116 anomaly)",
        "metrics": metrics,
        "metric_source": "sklearn roc_auc_score / average_precision_score on image-level anomaly scores",
        "note": "image-level only; MIIC has no GT masks",
    }, indent=2))
    print("METRICS:", metrics)

    try:
        save_triptychs(items, out / "heatmaps")
    except Exception as e:  # noqa: BLE001
        print(f"heatmap export skipped: {e}")
    print(f"done -> {out}")


if __name__ == "__main__":
    main()
