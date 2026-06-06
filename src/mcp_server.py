from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from src.common import REPO_ROOT, load_json, relpath, repo_path
from src.contracts import validate_run

DEMO_MANIFEST_PATH = Path("demo/manifest.json")

app = FastMCP(
    "sic-anomaly-workbench",
    instructions=(
        "Audit the SiC anomaly workbench demo artifacts. Keep proxy-validated evidence, "
        "qualitative SiC transfer, and missing artifact files clearly separated."
    ),
    log_level="ERROR",
)


def _manifest_path(path: str | Path = DEMO_MANIFEST_PATH) -> Path:
    return repo_path(path)


def _load_manifest(path: str | Path = DEMO_MANIFEST_PATH) -> dict[str, Any]:
    return load_json(path)


def _examples_by_tile(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    examples = manifest.get("examples") or []
    return {
        str(example.get("registry", {}).get("tile_id")): example
        for example in examples
        if isinstance(example, dict) and isinstance(example.get("registry"), dict)
    }


def _risk_tile(manifest: dict[str, Any], tile_id: str) -> dict[str, Any] | None:
    risk_map = manifest.get("risk_map") or {}
    tiles = risk_map.get("tiles") or []
    for tile in tiles:
        if isinstance(tile, dict) and tile.get("tile_id") == tile_id:
            return tile
    return None


def _claim_boundary(example: dict[str, Any]) -> str:
    evidence_class = example.get("evidence_class")
    caveats = set(example.get("caveats") or [])
    if evidence_class == "qualitative" or "SiC qualitative" in caveats:
        return "qualitative SiC transfer only; do not present this as metric-bearing production evidence"
    if "proxy metric" in caveats:
        return "proxy-validated metric evidence; transfer to SiC remains a separate caveat"
    return "verified demo evidence"


def _referenced_paths(manifest: dict[str, Any]) -> list[dict[str, str]]:
    references: list[dict[str, str]] = []
    for example in manifest.get("examples") or []:
        if not isinstance(example, dict):
            continue
        registry = example.get("registry") or {}
        result = example.get("result") or {}
        tile_id = str(registry.get("tile_id") or result.get("tile_id") or "<unknown>")
        for owner, record, keys in [
            ("registry", registry, ["image_path", "source_image_path", "mask_path"]),
            ("result", result, ["model_config_path", "heatmap_path", "overlay_path"]),
        ]:
            if not isinstance(record, dict):
                continue
            for key in keys:
                value = record.get(key)
                if isinstance(value, str) and value:
                    references.append({"tile_id": tile_id, "owner": owner, "field": key, "path": value})
        source_file = registry.get("source_file") if isinstance(registry, dict) else None
        if isinstance(source_file, str) and source_file:
            references.append({"tile_id": tile_id, "owner": "registry", "field": "source_file", "path": source_file})

    metrics = manifest.get("metrics") or {}
    if isinstance(metrics, dict):
        for key in ["run_dir", "model_config_path"]:
            value = metrics.get(key)
            if isinstance(value, str) and value:
                references.append({"tile_id": "<metrics>", "owner": "metrics", "field": key, "path": value})
    return references


def _missing_paths(manifest: dict[str, Any]) -> list[dict[str, str]]:
    missing: list[dict[str, str]] = []
    for reference in _referenced_paths(manifest):
        if not repo_path(reference["path"]).exists():
            missing.append(reference)
    return missing


def _run_manifest_paths() -> list[Path]:
    runs_dir = repo_path("runs")
    if not runs_dir.exists():
        return []
    return sorted(runs_dir.glob("*/run_manifest.json"))


def _read_json_text(path: str | Path) -> str:
    return json.dumps(load_json(path), indent=2, sort_keys=True)


@app.tool()
def list_demo_examples() -> list[dict[str, Any]]:
    """List curated demo examples with verdicts, scores, and evidence classes."""
    manifest = _load_manifest()
    examples: list[dict[str, Any]] = []
    for example in manifest.get("examples") or []:
        registry = example.get("registry") or {}
        result = example.get("result") or {}
        if not isinstance(registry, dict) or not isinstance(result, dict):
            continue
        examples.append(
            {
                "tile_id": registry.get("tile_id"),
                "title": example.get("title"),
                "modality": registry.get("modality"),
                "wafer_id": registry.get("wafer_id"),
                "score": result.get("anomaly_score"),
                "verdict": result.get("verdict"),
                "evidence_class": example.get("evidence_class"),
                "caveats": example.get("caveats") or [],
                "claim_boundary": _claim_boundary(example),
            }
        )
    return examples


@app.tool()
def get_tile_evidence(tile_id: str) -> dict[str, Any]:
    """Return full evidence and claim framing for one tile."""
    manifest = _load_manifest()
    examples = _examples_by_tile(manifest)
    example = examples.get(tile_id)
    if example is None:
        return {"error": f"unknown tile_id: {tile_id}", "known_tile_ids": sorted(examples)}

    result = example.get("result") or {}
    registry = example.get("registry") or {}
    return {
        "tile_id": tile_id,
        "title": example.get("title"),
        "caption": example.get("caption"),
        "verdict": result.get("verdict") if isinstance(result, dict) else None,
        "anomaly_score": result.get("anomaly_score") if isinstance(result, dict) else None,
        "threshold_review": manifest.get("threshold_review"),
        "threshold_hold": manifest.get("threshold_hold"),
        "evidence_class": example.get("evidence_class"),
        "caveats": example.get("caveats") or [],
        "claim_boundary": _claim_boundary(example),
        "registry": registry,
        "result": result,
        "risk_map_tile": _risk_tile(manifest, tile_id),
    }


@app.tool()
def trace_source(tile_id: str) -> dict[str, Any]:
    """Trace one tile back to source, license, preprocessing, and rendered artifact paths."""
    evidence = get_tile_evidence(tile_id)
    if "error" in evidence:
        return evidence
    registry = evidence.get("registry") or {}
    result = evidence.get("result") or {}
    paths = [
        {"field": "image_path", "path": registry.get("image_path")},
        {"field": "source_image_path", "path": registry.get("source_image_path")},
        {"field": "mask_path", "path": registry.get("mask_path")},
        {"field": "heatmap_path", "path": result.get("heatmap_path")},
        {"field": "overlay_path", "path": result.get("overlay_path")},
        {"field": "model_config_path", "path": result.get("model_config_path")},
    ]
    return {
        "tile_id": tile_id,
        "source_id": registry.get("source_id"),
        "source_file": registry.get("source_file"),
        "wafer_id": registry.get("wafer_id"),
        "modality": registry.get("modality"),
        "source_label": registry.get("source_label"),
        "license_status": registry.get("license_status"),
        "demo_allowed": registry.get("demo_allowed"),
        "tile_position": {
            "x": registry.get("tile_x"),
            "y": registry.get("tile_y"),
            "size": registry.get("tile_size"),
        },
        "preprocess": registry.get("preprocess"),
        "paths": [
            {
                "field": item["field"],
                "path": item["path"],
                "exists": bool(item["path"] and repo_path(str(item["path"])).exists()),
            }
            for item in paths
        ],
    }


@app.tool()
def summarize_claim_boundaries() -> dict[str, Any]:
    """Summarize which visible claims are metric-bearing and which are qualitative."""
    manifest = _load_manifest()
    metrics = manifest.get("metrics") or {}
    metric_rows = metrics.get("metrics") if isinstance(metrics, dict) else []
    examples = manifest.get("examples") or []
    return {
        "manifest": relpath(_manifest_path()),
        "model": manifest.get("model"),
        "metrics_framing": metrics.get("framing") if isinstance(metrics, dict) else None,
        "available_metrics": [
            metric for metric in metric_rows or [] if isinstance(metric, dict) and metric.get("available") is True
        ],
        "withheld_metrics": [
            metric for metric in metric_rows or [] if isinstance(metric, dict) and metric.get("available") is False
        ],
        "proxy_validated_tiles": [
            example.get("registry", {}).get("tile_id")
            for example in examples
            if isinstance(example, dict) and example.get("evidence_class") == "verified"
        ],
        "qualitative_tiles": [
            example.get("registry", {}).get("tile_id")
            for example in examples
            if isinstance(example, dict) and example.get("evidence_class") == "qualitative"
        ],
    }


@app.tool()
def list_run_manifests() -> list[dict[str, Any]]:
    """List local frozen run manifests discovered under runs/."""
    runs: list[dict[str, Any]] = []
    for path in _run_manifest_paths():
        manifest = load_json(path)
        runs.append(
            {
                "run_id": manifest.get("run_id"),
                "path": relpath(path),
                "status": manifest.get("status"),
                "model_name": manifest.get("model_name"),
                "dataset_split_path": manifest.get("dataset_split_path"),
                "review_threshold": manifest.get("review_threshold"),
                "hold_threshold": manifest.get("hold_threshold"),
            }
        )
    return runs


@app.tool()
def get_run_manifest(run_id: str = "") -> dict[str, Any]:
    """Return a local run manifest by run_id, or the first discovered run when omitted."""
    paths = _run_manifest_paths()
    if not paths:
        return {"error": "no run manifests found under runs/"}
    target = paths[0]
    if run_id:
        matching = [path for path in paths if path.parent.name == run_id]
        if not matching:
            return {"error": f"unknown run_id: {run_id}", "known_run_ids": [path.parent.name for path in paths]}
        target = matching[0]
    manifest = load_json(target)
    manifest["_path"] = relpath(target)
    return manifest


@app.tool()
def validate_demo_artifacts(check_files: bool = True) -> dict[str, Any]:
    """Validate the web demo manifest and optionally report missing referenced files."""
    manifest_path = _manifest_path()
    result: dict[str, Any] = {
        "manifest": relpath(manifest_path),
        "manifest_exists": manifest_path.exists(),
        "schema_ok": False,
        "schema_validator": "scripts/validate_demo.mjs",
        "missing_files": [],
        "run_manifests": [],
    }
    if not manifest_path.exists():
        return result

    schema_check = subprocess.run(
        ["node", "scripts/validate_demo.mjs", relpath(manifest_path)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    result["schema_ok"] = schema_check.returncode == 0
    result["schema_output"] = (schema_check.stdout or schema_check.stderr).strip()

    manifest = _load_manifest()
    if check_files:
        result["missing_files"] = _missing_paths(manifest)

    run_results: list[dict[str, Any]] = []
    for path in _run_manifest_paths():
        try:
            validate_run(path.parent, require_frozen=True)
        except Exception as exc:  # noqa: BLE001 - tool output should report every run, not stop at first failure.
            run_results.append({"path": relpath(path), "ok": False, "error": str(exc)})
        else:
            run_results.append({"path": relpath(path), "ok": True})
    result["run_manifests"] = run_results
    return result


@app.resource("demo://manifest")
def demo_manifest_resource() -> str:
    """Read the active demo manifest as JSON."""
    return _read_json_text(DEMO_MANIFEST_PATH)


@app.resource("tile://{tile_id}/evidence")
def tile_evidence_resource(tile_id: str) -> str:
    """Read one tile evidence bundle as JSON."""
    return json.dumps(get_tile_evidence(tile_id), indent=2, sort_keys=True)


@app.resource("run://{run_id}/manifest")
def run_manifest_resource(run_id: str) -> str:
    """Read a run manifest as JSON."""
    return json.dumps(get_run_manifest(run_id), indent=2, sort_keys=True)


@app.prompt()
def audit_tile(tile_id: str) -> str:
    """Prompt for auditing one tile without overstating evidence."""
    return (
        f"Audit tile {tile_id}. Use get_tile_evidence and trace_source. Explain the verdict, "
        "artifact provenance, missing files if any, and whether the evidence is proxy-validated "
        "or qualitative SiC transfer."
    )


@app.prompt()
def judge_brief() -> str:
    """Prompt for a short judge-facing evidence brief."""
    return (
        "Prepare a concise judge brief for the SiC anomaly workbench. Use list_demo_examples, "
        "summarize_claim_boundaries, and validate_demo_artifacts. Separate metric-bearing proxy "
        "evidence from qualitative SiC transfer and call out unresolved artifact gaps."
    )


def main() -> None:
    app.run(transport="stdio")


if __name__ == "__main__":
    main()
