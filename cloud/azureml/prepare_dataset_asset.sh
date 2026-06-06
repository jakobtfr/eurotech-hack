#!/usr/bin/env bash
set -euo pipefail

ASSET_NAME="eurotech-hack-datasets-ready"
COMBINED_SPLIT="splits/combined_no_miic.csv"
DATASET_ROOT=""
MIN_ROWS="1"
VERSION="$(date -u +%Y%m%d%H%M%S)"

usage() {
  printf '%s\n' \
    "Usage: $0 --dataset-root PATH [--asset-name NAME] [--version VERSION] [--min-rows N]" \
    "" \
    "Creates registry/config/split artifacts inside PATH, excludes MIIC, and registers PATH as an Azure ML uri_folder data asset."
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --asset-name)
      ASSET_NAME="${2:?missing value for --asset-name}"
      shift 2
      ;;
    --dataset-root)
      DATASET_ROOT="${2:?missing value for --dataset-root}"
      shift 2
      ;;
    --min-rows)
      MIN_ROWS="${2:?missing value for --min-rows}"
      shift 2
      ;;
    --version)
      VERSION="${2:?missing value for --version}"
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

if [[ -z "$DATASET_ROOT" ]]; then
  printf 'error: --dataset-root is required\n' >&2
  usage >&2
  exit 2
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

if ! command -v az >/dev/null 2>&1; then
  printf 'error: Azure CLI is not installed or not on PATH\n' >&2
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  printf 'error: uv is not installed or not on PATH\n' >&2
  exit 1
fi

mkdir -p "$DATASET_ROOT/splits"
COMBINED_SPLIT_PATH="$DATASET_ROOT/$COMBINED_SPLIT"

uv run python scripts/prepare_training_dataset.py \
  --dataset-root "$DATASET_ROOT" \
  --combined-split "$COMBINED_SPLIT" \
  --exclude-dataset miic \
  --min-rows "$MIN_ROWS" \
  --plain

az extension add --name ml --upgrade --yes >/dev/null
az ml data create \
  --name "$ASSET_NAME" \
  --version "$VERSION" \
  --type uri_folder \
  --path "$DATASET_ROOT"

printf 'asset=azureml:%s:%s\n' "$ASSET_NAME" "$VERSION"
printf 'combined_split=%s\n' "$COMBINED_SPLIT_PATH"
