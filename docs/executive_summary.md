# Executive Summary

## One-Line Pitch

Few-shot semiconductor anomaly triage: eight normal SEM references produce
auditable heatmaps, review decisions, and evidence boundaries.

## What Works Today

- Frozen DINOv2 + PCA residual scoring runs end to end.
- Recovered MIIC partial SEM proxy run is frozen and validated.
- The workbench shows raw images, heatmaps, scores, decisions, support count,
  metrics, and caveats from `demo/manifest.json`.
- Valid image-level metrics are available: AUROC `0.866268`, AUPR `0.796814`.
- Pixel metrics are withheld because masks were not recovered.

## Why It Wins

- It is a working product demo, not a slide-only research idea.
- It is honest: proxy evidence is separated from SiC claims.
- It is executive-readable: risk map → tile → heatmap → evidence → pilot ask.
- It is technically defensible: every result points to a frozen run artifact.

## Pilot Ask

Provide a small, licensed paired SiC dataset:

- normal reference images,
- labeled anomaly images,
- a subset with aligned masks or etch-confirmed regions,
- permission to display sanitized examples.

The first pilot milestone is not production rejection. It is a measured review
queue: fewer unprioritized images, visible explanations, and quantified failure
cases.
