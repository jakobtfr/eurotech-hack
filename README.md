# eurotech-hack — SiC Anomaly Workbench

Monorepo for the SiC wafer anomaly/defect-detection hackathon. See
[`planning/output/implementation_plan.md`](planning/output/implementation_plan.md)
for the full demo plan.

## Layout

```text
apps/
  web/        # Next.js 16 + shadcn/ui + Tailwind frontend (the workbench dashboard)
  # api/      # Python backend (SubspaceAD / FoundAD) — added later
packages/     # reserved for shared code (ui/config)
```

Tooling: pnpm workspaces + Turborepo.

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

## Frontend

`apps/web` is the dashboard with four tabs — **Inspect**, **Risk Map**,
**Evidence**, **Research** — currently scaffolded with placeholder content. It
reads the backend base URL from `NEXT_PUBLIC_API_URL` (see
`apps/web/.env.example`); no API calls are wired up yet.
