# SiC Wafer Anomaly and Defect Detection - Week-Long Demo Plan

Date: 2026-06-06

This plan converts the research direction in `planning/prompt.md` into an
executable demo target for a one-week hackathon. The priority is a working,
offline, source-traceable demo by the end of the week. Research breadth is
secondary to a stable demo path.

Control documents:
- `planning/AGENTS.md`: planning artifact only, use local sources, keep outputs
  under `planning/output/`, and separate verified claims, assumptions, pitch
  framing, and open questions.
- `planning/prompt.md` (`BRIEF`): thesis, methods, datasets, repos, and
  week-long execution summary.
- `planning/sources/manifest.md`: source IDs and local file paths.

## 1. Demo Objective

Build a local demo that lets a judge inspect semiconductor/SiC imagery, view an
anomaly heatmap, see a wafer/tile risk map, and understand what is verified
versus qualitative.

End-of-week demo definition:
- Runs locally from pre-rendered artifacts.
- Shows 6-10 curated examples with raw image, heatmap overlay, anomaly score,
  contour/ROI, novelty flag, and verdict.
- Includes one tile-grid or wafer-style risk map labeled by provenance.
- Includes at least one metric-bearing proxy evaluation if data/labels are
  available.
- Includes qualitative SiC examples only when source/license status is recorded.
- Includes a research tab or appendix showing why SubspaceAD is the executable
  baseline and why FoundAD is the research headline only if it runs.

The demo claim:

> We built an open, few-shot semiconductor anomaly workbench that produces
> heatmaps and review decisions from scarce normal examples, while explicitly
> separating proxy-validated evidence from qualitative SiC transfer.

Non-goals for the week:
- No production-grade SiC accuracy claim.
- No public benchmark claim unless the dataset is actually licensed, split, and
  released.
- No reliable defect naming claim unless labels or a validated classifier exist.
- No live model training during the final demo.

## 2. Fixed MVP Scope

The week should optimize for one executable path and one convincing story.

Must ship:
- `datasets/workbench/<category>/...` in MVTec-style layout.
- `data/source_registry.jsonl` for every demo image.
- `runs/<timestamp>_subspacead_<category>/` with config, scores, heatmaps,
  overlays, and metrics manifest.
- `demo/manifest.json` pointing to all pre-rendered demo artifacts.
- A dashboard app, preferably Gradio as suggested in the brief, with preloaded
  examples and no network dependency.
- A manifest/path validator for the final demo artifact set.
- `docs/claim_table.md` and `docs/run_summary.md`.

Should ship if stable:
- FoundAD demo or FoundAD comparison on the same proxy split.
- k-shot comparison table: 1-shot, 2-shot, 4-shot.
- CLAHE on/off qualitative comparison for PL/etch-pit examples.
- Simple CLIP/SigLIP semantic hints labeled as hints, not predictions.

Explicit cuts:
- No TailedCore integration unless all MVP items are already done.
- No WaferDC integration unless the primary heatmap path is stable.
- No EfficientAD/anomalib baseline unless dependency setup takes less than half
  a day.
- No custom full dataset platform. Use files, CSV, JSON, and pre-rendered PNGs.
- No live upload requirement. Preloaded examples are enough.

## 3. Evidence-Backed Stack Choice

Primary executable path: SubspaceAD.
- It is training-free and uses frozen DINOv2 features plus PCA residual scoring
  (`R2`, `planning/sources/repos/SubspaceAD/README.md`, Introduction and Usage;
  `P9`, `planning/sources/md/2602.23013v3.md`, Sections 3.2-3.4).
- The local repo exposes CLI controls for dataset, categories, model checkpoint,
  resolution, k-shot, augmentations, PCA explained variance, CLAHE, scoring, and
  output directory (`R2`,
  `planning/sources/repos/SubspaceAD/src/subspacead/config.py`).

Research headline path: FoundAD.
- FoundAD fits the foundation-encoder thesis and supports `mode=demo`,
  `mode=train`, and `mode=AD`, but it requires DINOv3 rights and downloaded
  projector assets for the quick path (`R1`,
  `planning/sources/repos/FoundAD/README.md`, Quick Start and Training and
  Inference; `P8`, `planning/sources/md/2510.01934v1.md`, Abstract, Tables
  1-5).
- FoundAD is optional until SubspaceAD heatmaps, demo artifacts, and the
  dashboard are working.

Data path:
- Use MIIC or another available SEM dataset as the metric-bearing proxy before
  making any SiC transfer statement. P7 is the strongest local source for public
  semiconductor SEM anomaly validation and explicitly warns about natural-image
  pretraining domain gap (`P7`, `planning/sources/md/2505.07576v1.md`, Sections
  3.1, 4.1, 4.2).
- Use SiC PL/etch-pit data for qualitative transfer if license/source status is
  recorded. P1 and P11 support PL relevance but also justify caution: PL defects
  can be low contrast, labels often depend on etch validation, and the relevant
  data/models are not public in the local materials (`P1`,
  `planning/sources/md/1-s2.0-S0925963525008027-main.md`, Abstract, Sections 1,
  2.1.3, 3.3, 4; `P11`, `planning/sources/md/MSF.1004.321.md`, Abstract,
  Materials and Equipment, Results and Discussion).

## 4. Artifact Contract

The demo is built from durable artifacts, not ad hoc notebook state.

```text
data/
  source_registry.jsonl
  splits/
    <dataset>_<split>.csv
datasets/
  workbench/
    <category>/
      train/good/*.png
      test/good/*.png
      test/anomaly/*.png
      ground_truth/anomaly/*_mask.png
runs/
  <timestamp>_<model>_<category>/
    config.yaml
    labels.csv
    scores.csv
    metrics.json
    metrics_manifest.json
    heatmaps/*.png
    overlays/*.png
    examples/*.png
demo/
  manifest.json
  prerendered/
docs/
  claim_table.md
  run_summary.md
```

Model input contract:
- Use MVTec-style folder layout as the canonical runtime interface because
  SubspaceAD and FoundAD already support MVTec/VisA-like assumptions (`R2`,
  README Data Preparation and Usage; `R1`, README Dataset Preparation).
- Convert grayscale SEM/PL to RGB by channel repeat.
- Tile large images deterministically and record source image, tile coordinates,
  tile size, and preprocessing.
- Apply CLAHE only as an explicit preprocessing variant. P1 supports PL
  enhancement, and SubspaceAD has `--use_clahe` (`P1`, Sections 2.1.3, 2.2;
  `R2`, `src/subspacead/config.py`).

Minimum source registry row:

```json
{
  "tile_id": "source_image__x0000_y0000_s0512",
  "wafer_id": "unknown-or-wafer-id",
  "source_id": "MIIC|Zenodo-SiC|P1|P11|MVTec|VisA|private",
  "source_file": "relative/original/path",
  "modality": "SEM|PL|etch|wafer_map|synthetic",
  "image_path": "datasets/workbench/<category>/test/anomaly/example.png",
  "source_image_path": "raw/path/example.png",
  "tile_x": 0,
  "tile_y": 0,
  "tile_size": 512,
  "preprocess": "rgb_repeat+clahe_v1",
  "split": "support|validation|test|demo",
  "source_label": "normal|BPD|TD|unknown|proxy_anomaly|null",
  "mask_path": null,
  "license_status": "verified|restricted|unknown",
  "demo_allowed": true
}
```

Run output contract:

```json
{
  "tile_id": "source_image__x0000_y0000_s0512",
  "model": "subspacead",
  "model_config_path": "runs/.../config.yaml",
  "anomaly_score": 0.0,
  "heatmap_path": "runs/.../heatmaps/tile.png",
  "overlay_path": "runs/.../overlays/tile.png",
  "region_tag": "localized anomaly",
  "semantic_hint": null,
  "novelty_flag": true,
  "verdict": "REVIEW"
}
```

Metric rules:
- Image AUROC/AUPR require explicit labels in `labels.csv`.
- Pixel AUROC/PRO require real aligned masks.
- Missing labels means qualitative-only outputs and score distributions.
- Folder names alone are not sufficient evidence for reported metrics.

## 5. Demo Architecture

Use a simple local app with pre-rendered results.

Recommended app stack:
- Gradio dashboard for speed and reliability.
- Static PNG overlays from model runs.
- Local JSON/CSV loading only.
- No network calls during final demo.

First screen:
- Left: preloaded example selector with modality/source tags.
- Center: raw image and heatmap overlay.
- Right: score, verdict, novelty flag, source status, and caveat badge.
- Top or bottom: tile-grid or wafer-style risk map.

Tabs:
- `Inspect`: raw image, overlay, contours, score, verdict.
- `Risk Map`: wafer/tile risk map with provenance label.
- `Evidence`: metrics table, split/config labels, run directory.
- `Research`: SubspaceAD path, optional FoundAD result/blocker, domain-gap
  caveat.

Verdict rules:
- `PASS`: all tile scores below threshold.
- `REVIEW`: localized anomaly or unknown/high-uncertainty flag.
- `REJECT`: high-area anomaly or clustered hot tiles.

Thresholds are demo heuristics unless calibrated on a validation split.

Wafer map provenance labels:
- `real spatial`: true wafer/source coordinates exist.
- `stitched field`: assembled from related tiles/crops.
- `synthetic montage`: product concept visualization.

## 6. Week-Long Execution Plan

### Day 1 - Lock Demo Scope and Prove One End-to-End Artifact

Owner focus:
- Research lead: claim boundaries and source rules.
- Model lead: SubspaceAD environment.
- Data lead: first proxy dataset or benchmark layout.
- Demo lead: app shell and visual design sketch.

Tasks:
- Freeze MVP scope from Section 2.
- Create `docs/claim_table.md` with verified claims, assumptions, pitch framing,
  and open questions.
- Create the initial artifact directories.
- Create a minimal dashboard shell that can load `demo/manifest.json`.
- Create a placeholder `demo/manifest.json` for the first sanity example.
- Install SubspaceAD from `planning/sources/repos/SubspaceAD/`.
- Run one known MVTec/VisA sanity category if data is available.
- If no benchmark data is ready, run the smallest available workbench category.

SubspaceAD setup from the local README:

```bash
cd planning/sources/repos/SubspaceAD
conda create -n subspacead python=3.10
conda activate subspacead
pip install -r requirements.txt
pip install -e .
```

Sanity command shape:

```bash
python main.py \
  --dataset_name mvtec_ad \
  --dataset_path datasets/mvtec-ad \
  --categories bottle \
  --model_ckpt facebook/dinov2-with-registers-large \
  --image_res 512 \
  --k_shot 1 \
  --aug_count 10 \
  --pca_ev 0.99 \
  --outdir results/day1_sanity
```

Day 1 exit gate:
- One heatmap exists, even if only on a benchmark category.
- One example can be traced through source registry or placeholder provenance,
  model output, overlay path, `demo/manifest.json`, and dashboard display.
- If no heatmap exists, Day 2 starts with environment/debug only. Do not start
  FoundAD or extra baselines.

### Day 2 - Build the Workbench Dataset and First Demo Manifest

Tasks:
- Stage the metric-bearing proxy dataset.
- Stage all candidate SiC qualitative examples.
- Convert at least one category to `datasets/workbench/<category>/...`.
- Generate `data/source_registry.jsonl`.
- Generate `data/splits/<dataset>_<split>.csv` and labels for metric-bearing
  examples.
- Select 6-10 demo candidates and mark `demo_allowed`.
- Create `demo/manifest.json` with expected artifact paths for each selected
  example.

Recommended dataset priority:
1. MIIC or available SEM proxy.
2. Zenodo SiC etch-pit or team-provided SiC examples.
3. MVTec/VisA safety category.

Day 2 exit gate:
- `datasets/workbench/<category>` exists.
- At least five demo-safe images are registered.
- The app can load `demo/manifest.json`, even before all heatmaps are populated.

### Day 3 - Run SubspaceAD on Workbench Data

Tasks:
- Run SubspaceAD on the workbench category.
- Save heatmaps, overlays, scores, and configs under `runs/`.
- Run 1-shot first. Add 2-shot/4-shot only after the first run succeeds.
- Run CLAHE on/off only for PL/etch examples.
- Create a simple score threshold rule for `PASS`, `REVIEW`, `REJECT`.

Workbench command shape from `planning/sources/repos/SubspaceAD/`:

```bash
python main.py \
  --dataset_name mvtec_ad \
  --dataset_path ../../datasets/workbench \
  --categories <category> \
  --model_ckpt facebook/dinov2-with-registers-large \
  --image_res 512 \
  --k_shot 1 \
  --aug_count 10 \
  --pca_ev 0.99 \
  --outdir ../../runs/day3_subspacead_<category>
```

Upgrade path if hardware is strong:
- Use `facebook/dinov2-with-registers-giant`.
- Use `--image_res 672`.
- Use `--aug_count 30`.

Fallback path if hardware is weak:
- Use `facebook/dinov2-with-registers-base` or smaller available checkpoint.
- Use `--image_res 448` or `512`.
- Keep only pre-rendered outputs in the app.

Day 3 exit gate:
- At least six demo examples have real heatmaps and overlays.
- `scores.csv` is joined into `demo/manifest.json`.
- The demo can show raw image, overlay, score, and verdict from local files.

### Day 4 - Metrics, Failure Cases, and Risk Map

Tasks:
- Compute valid metrics for proxy data:
  - image AUROC/AUPR if image labels exist.
  - pixel AUROC/PRO if masks exist.
- Write `metrics_manifest.json` explaining valid and invalid metrics.
- Create risk-map data from tile scores.
- Render one static tile-grid or wafer-style risk map.
- Collect 2-3 failure cases and label them honestly.
- Add caveat badges in the app:
  - `proxy metric`
  - `SiC qualitative`
  - `synthetic montage`
  - `restricted source`

Day 4 exit gate:
- The app has a risk map.
- The app has an evidence/metrics tab.
- No metric appears without split/config/provenance.

### Day 5 - FoundAD Attempt and Optional Comparison

FoundAD is a Day 5 task only if Days 1-4 gates are complete.

Tasks:
- Verify DINOv3 rights and projector access.
- Run the FoundAD MVTec or VisA demo from the local README.
- If the demo works, run FoundAD on the same proxy split as SubspaceAD.
- If it fails, document the blocker and show FoundAD as research framing.

Setup from `planning/sources/repos/FoundAD/`:

```bash
cd planning/sources/repos/FoundAD
conda create -n foundad python=3.10
conda activate foundad
pip install -r requirements.txt
pip install -e .
```

Demo commands from the local README:

```bash
python foundad/main.py mode=demo app=test testing.segmentation_vis=True data.dataset=mvtec data.data_name=mvtec_1shot data.test_root=assets/mvtec
python foundad/main.py mode=demo app=test testing.segmentation_vis=True data.dataset=visa data.data_name=visa_4shot data.test_root=assets/visa
```

FoundAD decision gate:
- If FoundAD runs by midday Day 5, add it as an optional comparison.
- If not, stop debugging and keep the demo on SubspaceAD.
- Do not risk the final demo for FoundAD.

Day 5 exit gate:
- The app still works after adding optional comparison or documented blocker.
- `docs/run_summary.md` contains the FoundAD status.

### Day 6 - Demo Hardening and Pitch Integration

Tasks:
- Remove live dependencies from the app.
- Pre-render every image used in the final demo.
- Add source/provenance labels everywhere.
- Add a "what is verified" section in the app or deck.
- Freeze demo examples. No new data after this point unless replacing a broken
  image.
- Record a first backup screen capture.
- Rehearse the 4-minute demo path:
  1. Problem and scarce-label setup.
  2. Show risk map.
  3. Inspect one clean/pass tile.
  4. Inspect one anomalous/review tile.
  5. Show evidence tab.
  6. State what remains qualitative for SiC.

Day 6 exit gate:
- App runs offline.
- Backup recording exists.
- Final example set is frozen.
- Unsupported claims are removed from the app/deck.

### Day 7 - Freeze, Rehearse, and Present

Tasks:
- Final smoke test from a clean shell.
- Verify every path in `demo/manifest.json` exists.
- Run the manifest/path validator.
- Verify `docs/claim_table.md` and `docs/run_summary.md` match the demo.
- Record final backup video.
- Prepare final one-slide fallback with static risk map and heatmap overlays.
- Rehearse exact claim language.

Final demo gate:
- If the app fails, present the screen recording and static fallback.
- If metrics are unavailable, present qualitative heatmaps and say metrics were
  not valid because labels/masks were unavailable.
- If SiC examples are unavailable, present SEM proxy results and frame SiC as
  the next data acquisition target.

## 7. Team Operating Model

Four-person split:
- Research lead: claims, source ledger, judging story, final deck.
- Data lead: data staging, tiling, registry, labels, license status.
- Model lead: SubspaceAD, optional FoundAD, metrics, run artifacts.
- Demo lead: dashboard, overlays, risk map, backup recording.

Daily rhythm:
- Morning: gate review and cut decisions.
- Midday: artifact sync into `demo/manifest.json`.
- Evening: app smoke test and one screenshot/video.

Cut policy:
- Anything blocking the next day gate gets cut or downgraded to future work.
- The demo path takes priority over additional baselines.
- The final app uses pre-rendered outputs, not live training.

## 8. Risks and Pivots

Risk: SubspaceAD does not produce heatmaps by end of Day 1.
- Pivot: debug only the environment/data layout on Day 2. Do not add FoundAD or
  extra baselines.

Risk: No metric-bearing proxy data is available by Day 2.
- Pivot: use MVTec/VisA for executable proof and treat SiC/SEM as qualitative
  until labels arrive.

Risk: No usable SiC data is available by Day 3.
- Pivot: demo on SEM proxy and licensed context figures/deck references. Phrase
  as "proxy-validated workbench for SiC data acquisition."

Risk: FoundAD is blocked by DINOv3/projector access.
- Pivot: keep FoundAD as the research headline and show SubspaceAD as the
  executable foundation-feature baseline.

Risk: Metrics look weak.
- Pivot: emphasize review routing, heatmap audit, failure-mode discovery, and
  the domain-gap result. Do not overclaim accuracy.

Risk: The dashboard breaks on presentation day.
- Pivot: use the backup screen recording and static PNG fallback.

## 9. Verified Claims

- 4H-SiC PL dislocation detection is relevant but hard because defects can be
  low contrast with unclear boundaries; P1 uses preprocessing plus YOLO11-OBB
  and still reports limitations (`P1`, Abstract, Sections 1, 2.1.3, 3.3, 4).
- PL-NDT can connect non-destructive PL images with etch-derived SiC defect
  labels, but the Wolfspeed/Cree implementation and data are proprietary
  (`P11`, Abstract, Materials and Equipment, Results and Discussion).
- MIIC is the strongest local public SEM proxy source and highlights the
  natural-image-pretraining domain gap (`P7`, Sections 3.1, 4.1, 4.2).
- FoundAD evidence is on MVTec-AD and VisA, not SiC; DINOv3 rights/projectors
  are external dependencies (`P8`, Abstract, Tables 1-5; `R1`, README Quick
  Start).
- SubspaceAD evidence is on MVTec-AD and VisA, not SiC, but it is the simplest
  executable few-shot baseline in the local sources (`P9`, Sections 3.2-3.4;
  `R2`, README Usage).
- Wafer-map sources are useful for business/yield context but are not
  microscope/PL anomaly-localization evidence (`P5`, Section 2.1; `R5`,
  README; `R6`, README).

## 10. Assumptions

- The team has at least one machine that can run a DINOv2 SubspaceAD category.
- Internet or pre-staged model/data assets are available early in the week.
- Pre-rendered model outputs are acceptable for the final demo.
- At least five demo-safe images can be used legally.
- The judging rubric rewards a working, honest, well-framed demo more than an
  unsupported production claim.

## 11. Pitch Framing

Use this positioning:

> This is a demo of an open few-shot inspection workbench for semiconductor
> imagery. It turns a handful of normal examples into heatmaps, risk maps, and
> review decisions, and it explicitly shows what transfers from proxy SEM data
> to SiC-style imagery and what still needs labeled SiC data.

Avoid:
- "We replace KLA/SICA."
- "We solve SiC inspection."
- "We classify every defect type."
- "We created the first public SiC benchmark" unless the release exists.

## 12. Open Questions

- Which datasets are actually available by Day 1: MIIC, Zenodo SiC, NFFA SEM,
  MVTec, VisA, or private wafer images?
- Are DINOv3 weights and FoundAD projector assets available legally?
- What are the exact judging criteria?
- Are paper figure crops allowed for demo use, deck use only, or not at all?
- What GPU and storage are available for the week?
- Is the Resonac wafer-savings figure sourced outside the local brief?
- Should the post-hackathon path be a private pilot or a public dataset release?
