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

The backend currently implements the artifact contracts and stable command
surface while datasets and upstream model integration are pending. The model
runner produces deterministic placeholder scores only; do not report them as
SubspaceAD or FoundAD evidence.

```bash
uv run python scripts/doctor.py --config configs/demo.yaml
uv run python scripts/validate_registry.py data/registry/sources.jsonl
uv run python -m src.data.build --config configs/data/stub.yaml
uv run python -m src.models.run \
  --config configs/models/subspacead.yaml \
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
```

Backend-generated raw data, split CSVs, run folders, and demo manifests are
gitignored. Source-controlled files define the contracts, configs, and command
implementations.

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
