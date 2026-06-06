# eurotech-hack - SiC Anomaly Workbench

Monorepo for the SiC wafer anomaly/defect-detection hackathon. See
[`planning/implementation_plan.md`](planning/implementation_plan.md)
for the full demo plan, and
[`docs/research_findings.md`](docs/research_findings.md) for results, dataset
availability, and methodological findings.

## Layout

```text
apps/
  web/        # Next.js 16 + shadcn/ui + Tailwind frontend (the workbench dashboard)
src/          # Python backend pipeline modules and CLI entry points
scripts/      # Direct validation wrappers from the implementation plan
configs/      # Dataset, model, and demo configuration
data/         # Registry plus generated split manifests
demo/         # Generated offline demo manifest and prerendered artifacts
runs/         # Generated immutable run artifacts
packages/     # reserved for shared code (ui/config)
```

Tooling: Node 24, pnpm workspaces, and Turborepo for the frontend; uv, Ruff,
and pytest for the backend scaffold.

## SiC Results

The real 4H-SiC photoluminescence detection experiment is published separately
from the MIIC and WM811K proxy experiments in
[`sic_results/`](sic_results/README.md). It includes the best YOLO11n-OBB
checkpoint, exact parameters, validation metrics, plots, predictions, dataset
provenance, and a concise scientific summary.

## Getting Started

```bash
pnpm install        # install all workspaces
pnpm dev            # run every app (web on http://localhost:3000)
pnpm build          # production build
pnpm lint           # lint all workspaces
pnpm typecheck      # type-check all workspaces
pnpm validate:demo      # validate demo/manifest.json
pnpm validate:registry  # validate data/registry/sources.example.jsonl
```

Run a single workspace:

```bash
pnpm --filter web dev
```

## Backend Scaffold

The backend implements the artifact contracts and stable command surface. Use
`pixel_pca.yaml` for dependency-light smoke tests and `dinov2_pca.yaml` for the
GPU training/scoring path. Do not report either local baseline as upstream
SubspaceAD or FoundAD evidence.

```bash
uv run python scripts/doctor.py --config configs/demo.yaml
uv run python scripts/validate_registry.py data/registry/sources.jsonl
uv run python -m src.data.build --config configs/data/stub.yaml
uv run python -m src.models.run \
  --config configs/models/pixel_pca.yaml \
  --split data/splits/stub_v0.csv \
  --shots 1 \
  --seed 17
```

Convenience targets:

```bash
make lint       # Ruff lint, including annotation checks
make format     # Ruff format
make test       # pytest
make smoke      # empty scaffold run through freeze + validation
make sanity     # doctor + registry validation + lint + tests
make prepare-training-dataset DATASET_ROOT=/path/to/datasets_ready
make train-dinov2 DATA_ROOT=/path/to/datasets_ready SPLIT=/path/to/datasets_ready/splits/combined_no_miic.csv
```

Backend-generated raw data, split CSVs, run folders, and demo manifests are
gitignored. Source-controlled files define the contracts, configs, and command
implementations.

## Training Handoff

For new datasets, use the dataset-machine workflow below. The recovered partial
MIIC SEM archive is already staged for the demo; full MIIC remains gated by
access and license status.

```bash
uv sync --extra dinov2
uv run python scripts/prepare_training_dataset.py \
  --dataset-root /path/to/datasets_ready \
  --min-rows 100

./scripts/train_dinov2_pca.sh \
  --split /path/to/datasets_ready/splits/combined_no_miic.csv \
  --data-root /path/to/datasets_ready \
  --shots 1 \
  --seed 17
```

For Azure ML, use `cloud/azureml/prepare_dataset_asset.sh` from the dataset
machine, then submit `cloud/azureml/train_dinov2_pca.yml`.

### Reproduce the VisA `pcb1` DINOv2 runs

A complete, copy-pasteable walkthrough (env, dataset restore, build, run,
evaluate, freeze, validate) lives in [`docs/EXECUTION.md`](docs/EXECUTION.md),
and the honest results — few-shot localization scaling (Pixel AUROC
0.76 → 0.95) plus the below-chance image-AUROC domain-gap finding — are written
up in [`docs/run_summary.md`](docs/run_summary.md).

This baseline is **training-free**: there is no checkpoint to save. The only
weights are the frozen DINOv2 encoder (cached by torch); the PCA "normal
subspace" is re-fit at run time from the recorded `support_set.csv`. Run
artifacts under `runs/` are gitignored and immutable once frozen.

## MCP Server

The local MCP server exposes the demo manifest, tile evidence, source tracing,
claim-boundary summaries, and artifact validation over stdio.

```bash
uv run python -m src.mcp_server
```

For a quick end-to-end check:

```bash
make mcp-smoke
```

MCP client configuration can point at the repo with:

```json
{
  "mcpServers": {
    "sic-anomaly-workbench": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/jakobfriedrich/code/projects/eurotech-hack",
        "run",
        "python",
        "-m",
        "src.mcp_server"
      ]
    }
  }
}
```

## Frontend

`apps/web` is the dashboard with four tabs: **Inspect**, **Risk Map**,
**Evidence**, and **Research**. The app loads `demo/manifest.json` on the server
and passes the validated manifest into the client views. If the file is missing
during local iteration, the TypeScript mock manifest remains as a fallback.

## Data Intake

Before real datasets arrive, use `data/registry/sources.example.jsonl` as a
source registry template. The registry validator checks row shape and uniqueness
by default; add `--check-files` to verify that source, mask, and license paths
exist once files are staged.
