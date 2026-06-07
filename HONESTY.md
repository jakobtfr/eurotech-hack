# HONESTY.md

Mandatory disclosure for the hackathon submission.

## 1. Team - who did what

Judges may compare this against `git shortlog -sn`, so this table names the
authors visible in git history. Update handles before final submission if any are
missing or duplicated.

| Member | GitHub handle | Main contributions |
|---|---|---|
| Jakob Friedrich | `Jakob Friedrich` | Backend anomaly pipeline, DINOv2/PCA experiment flow, run packaging, validation, documentation, demo evidence framing. |
| Jaylann | `jaylann` | Frontend/demo workbench implementation, product/pitch surface, UI integration. |
| Damia Vicens Ramis | `Damià Vicens Ramis` / `damiavicensramis` | Frontend/product implementation, research and demo support, numerical result creation and validation. |
| Justin Lanfermann | `Justin Lanfermann` | Frontend/product implementation, demo and repository support. |
| Sparsh Tyagi | `SparshTyagi` | Past Research Consolidation, collaboration on Jakob's PC for improvements, pitch/business framing, demo planning and creation. |

## 2. What is fully working

- The Next.js workbench runs locally and displays a curated inspection dashboard
  with raw SEM tiles, heatmaps, overlays, anomaly scores, triage decisions,
  caveats, support-shot count, metrics, and evidence provenance.
- The backend pipeline has real command surfaces for dataset ingestion/building,
  model scoring, calibration, evaluation, rendering, run freezing, demo manifest
  building, and validation.
- The recovered MIIC partial SEM proxy run is frozen into demo artifacts. The
  app reads `demo/manifest.json` and associated files under
  `demo/artifacts/miic_partial/`.
- The DINOv2 + PCA-residual baseline runs end to end on supported data. It fits
  a normal subspace from normal support examples and scores patch residuals.
- The MIIC partial proxy demo has valid image-level metrics documented in
  `docs/claim_table.md`: Image AUROC `0.866268`, Image AUPR `0.796814`, over
  463 test images.
- The real 4H-SiC photoluminescence oriented-box detector was trained and
  documented under `sic_results/`, including checkpoint, metrics, parameters,
  validation plots, split statistics, and provenance notes.
- A curated `results/` package for judges, including improved YOLO11s-OBB SiC metrics, MIIC proxy reliability figures, CFA/DRAEM comparisons, WM-811K proxy results, and
  compact reproduction/export scripts. These artifacts are
  part of the submitted evidence package.
- Validation and smoke-test entry points exist for the demo manifest, data
  registry, frozen runs, backend contracts, and MCP server.

## 3. What is mocked, stubbed, or hardcoded

| What is faked or shortcut | Where | Why we mocked it | What the real version would do |
|---|---|---|---|
| Fallback frontend manifest and mock research/metric/example data in case of missing data. | `apps/web/src/lib/mock/` and fallback logic in `apps/web/src/lib/demo-manifest.ts` | Keeps the UI usable during local development if `demo/manifest.json` is missing. | Always load the server-side validated production/pilot manifest from real frozen runs. |
| Curated demo example set | `demo/manifest.json`, `demo/artifacts/miic_partial/` | A two-minute demo needs stable examples including true positives, misses, and false positives. | Let an operator browse all run tiles and filter/sort dynamically from a persisted run store. |
| Triage thresholds are research calibration, not production release rules | `src/evaluation/calibrate.py`, `src/evaluation/evaluate.py`, model configs | Hackathon data is limited and proxy-based; thresholds are useful for review-queue demonstration. | Tune thresholds on target-line validation data with fab-specific cost and yield constraints. |
| MCP server is local stdio only | `src/mcp_server.py` | Shows machine-readable evidence and claim boundaries without deploying infrastructure. | Deploy an authenticated service connected to stored runs, source registries, and access control. |
| Some model configs are scaffolds or references | `configs/models/subspacead.yaml`, `configs/models/foundad.yaml`, docs | They document intended baselines and research context. | Run those exact upstream baselines and report only validated results. |
| WM-811K and MIIC comparison results are proxy evidence | `results/wm811k_silicon_proxy/`, `results/miic_sem_proxy/` on the pending results branch | They show semiconductor-adjacent feasibility and model comparison breadth. | Validate on licensed target-domain SiC inspection data before production claims. |

## 4. External APIs, services & data sources

| Service / API / dataset | Used for | Real call or mocked? | Auth |
|---|---|---|---|
| MIIC partial SEM data recovered from Dataverse/archive files | Proxy anomaly demo and frozen artifacts | Real local data/artifacts; license status unknown/restricted, disclosed in manifest caveats | None locally |
| VisA `pcb1` | Public proxy experiment documented in `docs/run_summary.md` | Real public dataset when restored locally; not committed in full | None |
| DINOv2 `dinov2_vits14` weights via PyTorch/torch hub cache | Frozen feature encoder for PCA residual baseline | Real model weights downloaded/cached by torch | None |
| 4H-SiC photoluminescence dataset | Real SiC-domain YOLO11n-OBB training results in `sic_results/` | Real local training result and metrics | None locally; dataset provenance documented |
| 4H-SiC improved YOLO11s-OBB result | Pending `results/sic_4h_yolo11s_obb/` branch artifact | Real local validation result and metrics if PR is merged | None locally; dataset provenance documented |
| CFA / DRAEM anomaly baselines | Pending `results/miic_sem_proxy/` branch artifacts | Real local proxy comparisons if PR is merged | None locally |
| WM-811K wafer-map dataset | Pending `results/wm811k_silicon_proxy/` branch artifact | Real silicon wafer-map proxy experiment if PR is merged | None locally |
| Azure ML configs | Future/cloud training handoff | Config files only; not required for the local demo | Would require Azure credentials |
| Next.js local server | Web demo | Real local app | None |

## 5. Pre-existing code

| Item | Source | Roughly how much | License |
|---|---|---|---|
| Next.js, React, Tailwind/shadcn-style UI, Radix, lucide, motion, Biome, Turborepo | Open-source dependencies listed in `package.json` and `apps/web/package.json` | Framework/dependency code, not authored by team | Upstream package licenses |
| Python dependencies including torch/DINOv2-related stack, pytest, ruff, numpy/scipy-style tooling | Open-source dependencies listed in `pyproject.toml` / `uv.lock` | Framework/dependency code, not authored by team | Upstream package licenses |
| DINOv2 model architecture/weights | Meta AI / PyTorch hub cache | External pretrained encoder used as frozen feature extractor | Upstream DINOv2 license/terms |
| YOLO11n-OBB base model | Ultralytics YOLO model family | Pretrained detector fine-tuned during the hackathon | Upstream Ultralytics license/terms |
| YOLO11s-OBB base model | Ultralytics YOLO model family | Larger pretrained detector fine-tuned during the hackathon on the pending results branch | Upstream Ultralytics license/terms |
| CFA and DRAEM methods/implementations | Existing anomaly-detection methods/libraries used for comparison on the pending results branch | Baseline/comparison method code and concepts | Upstream licenses/terms |
| Research papers and PDFs | `planning/sources/` | Background research material | Respective publisher/arXiv licenses/terms |
| Prior templates/scaffolding | Standard Next.js/shadcn-style project conventions | Boilerplate-level app structure | Upstream/template licenses where applicable |

All project-specific pipeline code, demo integration, experiment configuration,
results packaging, and submission documentation in this repository were produced
for the hackathon in the past 24 hours unless otherwise disclosed above.

## 6. Known limitations & next steps

- The live workbench demo uses MIIC SEM proxy evidence. It should not be claimed
  as validated SiC production performance.
- MIIC partial artifact license status is unknown; 
- VisA `pcb1` DINOv2/PCA experiments show strong few-shot pixel localization
  scaling, but source-level image ranking had domain-gap issues documented in
  `docs/run_summary.md`.
- The real SiC YOLO11n-OBB result is validation-set evidence, not an independent
  production test result.
- The improved YOLO11s-OBB result on the pending results branch improves
  precision and localization quality, but lowers recall; BPD recall remains the
  main weakness.
- Proxy results such as MIIC and WM-811K should support feasibility only, not be
  presented as target-domain SiC proof.
- The next pilot needs licensed paired SiC PL/etch/SEM imagery, image labels,
  a small mask subset, target-line threshold tuning, and operator workflow
  integration.
