#!/usr/bin/env bash
set -euo pipefail

CONFIG="configs/models/dinov2_pca.yaml"
DATA_ROOT=""
OUTPUT_DIR=""
SEED="17"
SHOTS="8"
SPLIT=""

usage() {
  printf '%s\n' \
    "Usage: $0 --split PATH --data-root PATH --output-dir PATH [--config PATH] [--shots N] [--seed N]" \
    "" \
    "Runs DINOv2/PCA scoring, calibration, evaluation, rendering, and freeze inside an Azure ML job."
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
    --output-dir)
      OUTPUT_DIR="${2:?missing value for --output-dir}"
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

if [[ -z "$SPLIT" || -z "$DATA_ROOT" || -z "$OUTPUT_DIR" ]]; then
  printf 'error: --split, --data-root, and --output-dir are required\n' >&2
  usage >&2
  exit 2
fi

python -m pip install --quiet --upgrade uv
uv pip install --system "pyyaml>=6.0.2" "numpy>=2.0" "pillow>=10.0"

RUN="$(python -m src.models.run \
  --config "$CONFIG" \
  --split "$SPLIT" \
  --data-root "$DATA_ROOT" \
  --shots "$SHOTS" \
  --seed "$SEED" \
  --plain | tail -n 1)"

python -m src.evaluation.calibrate --run "$RUN"
python -m src.evaluation.evaluate --run "$RUN"
python -m src.rendering.render --run "$RUN"
python -m src.packaging.freeze --run "$RUN"
python scripts/validate_run.py "$RUN"

mkdir -p "$OUTPUT_DIR"
cp -R "$RUN" "$OUTPUT_DIR/"
printf 'run=%s\n' "$RUN"
