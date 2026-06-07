#!/usr/bin/env python3
"""Generate the improved-model poster in the established SiC mosaic format."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO

REPO = Path(__file__).resolve().parents[2]
ROOT = Path(__file__).resolve().parent
SOURCE_DEMO = REPO / "sic_results" / "medium_defect_mosaic_demo"
OUT = ROOT / "medium_defect_mosaic_demo"
IMAGE = (
    REPO
    / "datasets"
    / "sic_dislocation_detection_db"
    / "leakage_safe"
    / "images"
    / "val"
    / "20250117test6 (190).jpg"
)
WEIGHTS = ROOT / "training" / "weights" / "best.pt"
CONF = 0.18
DISPLAY_WIDTH = 1275
COLS = 3
CELL_HEIGHT = 280
TD_COLOR = (35, 190, 70)
BPD_COLOR = (255, 145, 0)


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in ("Arial.ttf", "DejaVuSans.ttf", "Helvetica.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def polygon(
    draw: ImageDraw.ImageDraw, corners: np.ndarray, color: tuple[int, int, int], width: int
) -> None:
    points = [tuple(point) for point in corners]
    draw.line(points + [points[0]], fill=(255, 255, 255), width=width + 4, joint="curve")
    draw.line(points + [points[0]], fill=color, width=width, joint="curve")


def annotate_prediction(
    image: Image.Image, corners: np.ndarray, label: str, confidence: float, index: int
) -> None:
    color = TD_COLOR if label == "TD" else BPD_COLOR
    draw = ImageDraw.Draw(image)
    polygon(draw, corners, color, 4)
    cx, cy = corners.mean(axis=0)
    radius = 18
    draw.ellipse(
        (cx - radius, cy - radius, cx + radius, cy + radius),
        fill=color,
        outline=(255, 255, 255),
        width=3,
    )
    draw.text((cx - 6, cy - 12), str(index), fill=(0, 0, 0), font=font(21))
    draw.text(
        (cx + 22, cy - 14),
        f"{label} {confidence:.2f}",
        fill=color,
        stroke_width=2,
        stroke_fill=(255, 255, 255),
        font=font(20),
    )


def make_crop(
    original: Image.Image,
    corners: np.ndarray,
    label: str,
    confidence: float,
    index: int,
    cell_width: int,
) -> Image.Image:
    color = TD_COLOR if label == "TD" else BPD_COLOR
    min_x, min_y = corners.min(axis=0)
    max_x, max_y = corners.max(axis=0)
    cx, cy = corners.mean(axis=0)
    span = max(max_x - min_x, max_y - min_y, 180)
    half = max(280, span * 2.4)
    crop_box = (int(cx - half), int(cy - half), int(cx + half), int(cy + half))
    crop = original.crop(crop_box)
    available_h = CELL_HEIGHT - 48
    scale = min((cell_width - 42) / crop.width, available_h / crop.height)
    crop = crop.resize((int(crop.width * scale), int(crop.height * scale)), Image.Resampling.LANCZOS)
    panel = Image.new("RGB", (cell_width, CELL_HEIGHT), (248, 248, 248))
    panel.paste(crop, ((cell_width - crop.width) // 2, 42))
    draw = ImageDraw.Draw(panel)
    draw.rectangle((0, 0, cell_width - 1, CELL_HEIGHT - 1), outline=(190, 190, 190), width=2)
    draw.text(
        (10, 8),
        f"#{index}   {label}   confidence {confidence:.2f}",
        fill=(20, 20, 20),
        font=font(18),
    )
    draw.rectangle(
        ((cell_width - crop.width) // 2, 42, (cell_width + crop.width) // 2, 42 + crop.height),
        outline=color,
        width=3,
    )
    return panel


def predict(weights: Path, image: Path, image_size: int) -> list[dict]:
    result = YOLO(str(weights)).predict(
        str(image), imgsz=image_size, conf=CONF, device="mps", verbose=False
    )[0]
    predictions = []
    for corners, cls, confidence in zip(
        result.obb.xyxyxyxy, result.obb.cls, result.obb.conf, strict=True
    ):
        predictions.append(
            {
                "corners": corners.cpu().numpy().reshape(4, 2),
                "class": result.names[int(cls)],
                "confidence": float(confidence),
            }
        )
    return predictions


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ("00_expert_boxes_with_defect_mosaic.jpg", "02_original_medium_sic_image.jpg"):
        shutil.copy2(SOURCE_DEMO / name, OUT / name)

    original = Image.open(IMAGE).convert("RGB")
    predictions = predict(WEIGHTS, IMAGE, 1024)
    sx = DISPLAY_WIDTH / original.width
    display_height = int(original.height * sx)
    annotated = original.resize((DISPLAY_WIDTH, display_height), Image.Resampling.LANCZOS)
    for index, prediction in enumerate(predictions, 1):
        annotate_prediction(
            annotated,
            prediction["corners"] * sx,
            prediction["class"],
            prediction["confidence"],
            index,
        )

    header_height = 100
    cell_width = DISPLAY_WIDTH // COLS
    rows = (len(predictions) + COLS - 1) // COLS
    canvas = Image.new(
        "RGB", (DISPLAY_WIDTH, header_height + display_height + rows * CELL_HEIGHT), (248, 248, 248)
    )
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (24, 14),
        "Medium-complexity 4H-SiC: improved model-predicted imperfections",
        fill=(10, 10, 10),
        font=font(28),
    )
    draw.text(
        (24, 51),
        f"Whole image above; each model prediction at confidence >= {CONF:.2f} is enlarged below.",
        fill=(30, 30, 30),
        font=font(17),
    )
    draw.text((24, 76), "GREEN = TD     ORANGE = BPD", fill=(30, 30, 30), font=font(16))
    canvas.paste(annotated, (0, header_height))

    for index, prediction in enumerate(predictions, 1):
        row, col = divmod(index - 1, COLS)
        panel = make_crop(
            original,
            prediction["corners"],
            prediction["class"],
            prediction["confidence"],
            index,
            cell_width,
        )
        canvas.paste(panel, (col * cell_width, header_height + display_height + row * CELL_HEIGHT))

    canvas.save(OUT / "01_model_predictions_with_defect_mosaic.jpg", quality=95)

    baseline = predict(
        REPO / "sic_results" / "yolo11n_obb_cbms_sic" / "weights" / "best.pt", IMAGE, 768
    )

    def stats(items: list[dict]) -> dict:
        confidences = [item["confidence"] for item in items]
        return {
            "detections": len(items),
            "TD": sum(item["class"] == "TD" for item in items),
            "BPD": sum(item["class"] == "BPD" for item in items),
            "mean_confidence": float(np.mean(confidences)) if confidences else 0.0,
            "median_confidence": float(np.median(confidences)) if confidences else 0.0,
            "max_confidence": max(confidences, default=0.0),
            "confidences": confidences,
        }

    summary = {
        "source_image": str(IMAGE.relative_to(REPO)),
        "confidence_threshold": CONF,
        "expert_annotations": {"TD": 3, "BPD": 3, "total": 6},
        "baseline_model": stats(baseline),
        "improved_model": stats(predictions),
        "warning": "Predictions are model hypotheses; confidence is not proof of a physical defect.",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
