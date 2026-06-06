# eurotech-hack — SiC Anomaly Workbench

Monorepo for the SiC wafer anomaly/defect-detection hackathon. See
[`planning/implementation_plan.md`](planning/implementation_plan.md)
for the full demo plan.

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

Tooling: pnpm workspaces + Turborepo for the frontend, uv + Ruff + pytest for
the backend scaffold.

## Getting started

```bash
pnpm install        # install all workspaces
pnpm dev            # run every app (web on http://localhost:3000)
pnpm build          # production build
pnpm lint           # lint all workspaces
pnpm typecheck      # type-check all workspaces
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

`apps/web` is the dashboard with four tabs — **Inspect**, **Risk Map**,
**Evidence**, **Research** — currently scaffolded with placeholder content. It
reads the backend base URL from `NEXT_PUBLIC_API_URL` (see
`apps/web/.env.example`); no API calls are wired up yet.
