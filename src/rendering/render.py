from __future__ import annotations

import argparse
from pathlib import Path

from src.cli import add_common_flags, run_cli
from src.common import SCHEMA_VERSION, relpath, repo_path, save_json
from src.contracts import validate_predictions, validate_run


def render_run(run_path: str | Path) -> str:
    run_dir = repo_path(run_path)
    manifest = validate_run(run_dir, require_frozen=False)
    predictions = validate_predictions(manifest["predictions_path"])
    for row in predictions:
        score = float(row["normalized_anomaly_score"] or 0.0)
        _write_svg(repo_path(row["heatmap_path"]), row["tile_id"], score, "heatmap")
        _write_svg(repo_path(row["overlay_path"]), row["tile_id"], score, "overlay")
    risk_map_path = run_dir / "risk_maps" / "risk_map.json"
    save_json(
        risk_map_path,
        {
            "schema_version": SCHEMA_VERSION,
            "run_id": manifest["run_id"],
            "provenance": "synthetic montage",
            "tile_count": len(predictions),
            "risk_score": max([float(row["normalized_anomaly_score"] or 0.0) for row in predictions] or [0.0]),
            "review_or_hold_count": sum(1 for row in predictions if row["decision"] in {"REVIEW", "HOLD"}),
        },
    )
    _write_svg(run_dir / "risk_maps" / "risk_map.svg", "risk map", 0.0, "risk")
    return relpath(risk_map_path)


def _write_svg(path: Path, label: str, score: float, kind: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    intensity = max(0, min(255, int(score * 255)))
    cool = 255 - intensity
    radius = 80 + int(score * 120)
    svg = "\n".join(
        [
            (
                f'<svg xmlns="http://www.w3.org/2000/svg" width="448" height="448" '
                f'viewBox="0 0 448 448" role="img" aria-label="{kind}">'
            ),
            f'  <rect width="448" height="448" fill="rgb({cool},{cool},255)"/>',
            f'  <circle cx="224" cy="224" r="{radius}" fill="rgb(255,{cool},64)" opacity="0.68"/>',
            f'  <text x="24" y="52" font-family="monospace" font-size="20" fill="#111">{kind}</text>',
            f'  <text x="24" y="84" font-family="monospace" font-size="14" fill="#111">{label}</text>',
            f'  <text x="24" y="116" font-family="monospace" font-size="14" fill="#111">score={score:.3f}</text>',
            "</svg>",
            "",
        ]
    )
    path.write_text(svg, encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Render static heatmap, overlay, and risk-map artifacts.")
    parser.add_argument("--run", required=True, help="Run directory.")
    add_common_flags(parser)
    run_cli(parser, lambda args: render_run(args.run), argv)


if __name__ == "__main__":
    main()
