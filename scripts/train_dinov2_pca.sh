#!/usr/bin/env bash
set -euo pipefail

CONFIG="configs/models/dinov2_pca.yaml"
DATA_ROOT=""
SEED="17"
SHOTS="1"
SPLIT=""

usage() {
  printf '%s\n' \
    "Usage: $0 --split PATH --data-root PATH [--config PATH] [--shots N] [--seed N]" \
    "" \
    "Runs DINOv2/PCA scoring, calibration, evaluation, rendering, freeze, and validation locally."
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config)
      CONFIG="${2:?missing value for --config}"
      shift 2
      ;;
    --data-root)
      DATA_ROOT="${2:?missing value for --data-root}"
      shift 2
      ;;
    --seed)
      SEED="${2:?missing value for --seed}"
      shift 2
      ;;
    --shots)
      SHOTS="${2:?missing value for --shots}"
      shift 2
      ;;
    --split)
      SPLIT="${2:?missing value for --split}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'error: unknown argument: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$SPLIT" || -z "$DATA_ROOT" ]]; then
  printf 'error: --split and --data-root are required\n' >&2
  usage >&2
  exit 2
fi

RUN="$(uv run --extra dinov2 python -m src.models.run \
  --config "$CONFIG" \
  --split "$SPLIT" \
  --data-root "$DATA_ROOT" \
  --shots "$SHOTS" \
  --seed "$SEED" \
  --plain | tail -n 1)"

uv run python -m src.evaluation.calibrate --run "$RUN"
uv run python -m src.evaluation.evaluate --run "$RUN"
uv run python -m src.rendering.render --run "$RUN"
uv run python -m src.packaging.freeze --run "$RUN"
uv run python scripts/validate_run.py "$RUN"

printf 'run=%s\n' "$RUN"
