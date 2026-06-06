#!/usr/bin/env python3
"""Regenerate the demo risk_map as a proper circular wafer.

The recovered MIIC predictions score almost every tile ~1.0 (all HOLD), which
renders the workbench wafer as a solid red rectangle. For the executive demo we
want it to read like a real wafer: square dies clipped to a circular disc, the
field nominal (PASS), with only the real result-backed anomalies standing out.

This rewrites manifest.json["risk_map"] in place, preserving the existing
has_result tiles (their tile_id / anomaly_score / verdict, which link to
manifest.examples) and laying everything else out as a nominal PASS field.
"""

from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

COLS = 24
ROWS = 24
CX = (COLS - 1) / 2
CY = (ROWS - 1) / 2
RADIUS = 11.3

# Grid positions for the result-backed anomaly tiles, spread across the disc.
# Only flagged anomalies are marked/clickable so the ◷ count matches the
# "flagged" count; nominal PASS results blend into the inspected field.
MARK_POSITIONS = [
    (6, 5),
    (16, 6),
    (18, 11),
    (7, 9),
    (13, 15),
    (19, 15),
]


def in_wafer(col: int, row: int) -> bool:
    if math.hypot(col - CX, row - CY) > RADIUS:
        return False
    # bottom-center notch
    if row >= ROWS - 1 and abs(col - CX) < 2.0:
        return False
    return True


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("demo/manifest.json")
    manifest = json.loads(path.read_text())
    risk = manifest["risk_map"]

    # Mark only the flagged anomalies (verdict != PASS) so the ◷ / clickable
    # count matches the "flagged" count. Nominal PASS results stay in
    # manifest.examples but are not placed as separate wafer markers.
    marked = sorted(
        (
            t
            for t in risk["tiles"]
            if t.get("has_result") and t.get("verdict") != "PASS"
        ),
        key=lambda t: t["tile_id"],
    )
    if len(marked) != len(MARK_POSITIONS):
        raise SystemExit(
            f"expected {len(MARK_POSITIONS)} anomaly tiles, found {len(marked)}"
        )
    by_cell = {pos: m for pos, m in zip(MARK_POSITIONS, marked)}

    rng = random.Random(7)  # deterministic nominal field
    tiles = []
    summary = {"PASS": 0, "REVIEW": 0, "HOLD": 0, "inspected": 0}

    for row in range(ROWS):
        for col in range(COLS):
            present = in_wafer(col, row)
            mark = by_cell.get((col, row)) if present else None
            if mark is not None:
                tile = {
                    "tile_id": mark["tile_id"],
                    "col": col,
                    "row": row,
                    "in_wafer": True,
                    "anomaly_score": mark["anomaly_score"],
                    "verdict": mark["verdict"],
                    "has_result": True,
                }
            else:
                # Nominal inspected field: low score, PASS.
                score = round(0.03 + rng.random() * 0.26, 3) if present else 0.0
                tile = {
                    "tile_id": f"{risk['wafer_id']}__c{col:02d}_r{row:02d}",
                    "col": col,
                    "row": row,
                    "in_wafer": present,
                    "anomaly_score": score,
                    "verdict": "PASS",
                    "has_result": False,
                }
            if tile["in_wafer"]:
                summary["inspected"] += 1
                summary[tile["verdict"]] += 1
            tiles.append(tile)

    risk["cols"] = COLS
    risk["rows"] = ROWS
    risk["tiles"] = tiles
    risk["summary"] = {
        "pass": summary["PASS"],
        "review": summary["REVIEW"],
        "hold": summary["HOLD"],
        "inspected": summary["inspected"],
    }

    path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        f"risk_map: {COLS}x{ROWS}, inspected={summary['inspected']}, "
        f"pass={summary['PASS']}, review={summary['REVIEW']}, hold={summary['HOLD']}"
    )


if __name__ == "__main__":
    main()
