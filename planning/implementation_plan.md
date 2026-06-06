# SiC Wafer Anomaly Workbench - Execution-Ready Implementation Plan

Date: 2026-06-06
Timebox: one week
Team: four researchers
Status: implementation has not started

This document is the execution source of truth for the hackathon build. It
translates the research brief into one reproducible pipeline, one defensible
evaluation, and one reliable executive demo.

Control documents:

- `planning/prompt.md`: project thesis, candidate methods, datasets, and initial
  execution sketch.
- `planning/sources/repo_references.md`: upstream repository URLs, pinned
  commits, roles, and observed license status.
- `planning/AGENTS.md`: planning constraints and evidence-handling rules.

The project wins by proving three things in four minutes:

1. A few normal reference images are enough to generate useful anomaly
   heatmaps and review decisions.
2. Every visible result is traceable to its source image, preprocessing,
   support set, model configuration, and evaluation status.
3. The team understands exactly where semiconductor proxy evidence ends and
   SiC-specific evidence begins.

---

## 1. Executive Decision Record

### 1.1 Product statement

> The SiC Wafer Anomaly Workbench converts a small set of normal semiconductor
> images into localized anomaly heatmaps, tile-level review decisions, and a
> wafer-style risk map, while preserving the evidence needed to audit every
> result.

### 1.2 Fixed decisions

| Decision | Choice | Reason |
|---|---|---|
| Executable baseline | SubspaceAD-style frozen DINOv2 features plus PCA residual scoring | It is training-free, supports few-shot normal-only inspection, and is the lowest-risk path to heatmaps (`P9`, Sections 3.2-3.4). |
| Research comparison | FoundAD, only after the baseline and demo are complete | It strongly supports the foundation-encoder thesis but adds projector training and DINOv3 dependencies (`P8`, Sections 3-4). |
| Metric-bearing data | MIIC if obtained; MVTec/VisA as the benchmark fallback | MIIC is directly relevant to SEM and has image and pixel evidence; MVTec/VisA validate execution but not semiconductor transfer (`P7`, Sections 3-4; `P8`; `P9`). |
| SiC data role | Qualitative transfer unless labels and licenses are verified | The local evidence establishes the importance and difficulty of SiC PL inspection, not a public benchmark (`P1`, Sections 1-4; `P11`). |
| Final inference mode | Pre-rendered, offline artifacts | Reliability and auditability matter more than live model execution during the pitch. |
| User-facing decision vocabulary | `PASS`, `REVIEW`, `HOLD` | `HOLD` is an inspection escalation, not an unsupported production rejection. |
| Semantic defect names | Optional hints, never primary predictions | Anomaly localization does not establish defect identity. |

### 1.3 Explicitly out of scope

- A production-grade SiC accuracy claim.
- Replacing KLA, SICA, or a fab inspection process.
- Reliable BPD, TSD, TED, micropipe, or scratch classification without
  validated labels.
- Calling an example "novel" from anomaly score alone.
- Reporting pixel metrics without aligned ground-truth masks.
- Reporting a full-wafer result from a synthetic montage without labeling it
  synthetic.
- Integrating more than two anomaly methods during the week.
- Live training or internet access during the final demo.

### 1.4 Starting-state audit

As of 2026-06-06:

- The workspace contains planning documents, paper conversions, and lightweight
  upstream repository references.
- There is no implementation, dataset, environment lockfile, model weight, run
  artifact, or demo application.
- Upstream repository code is intentionally not vendored. Required checkouts
  must be cloned or cached outside this repo from
  `planning/sources/repo_references.md` and verified before use.
- Claims about SubspaceAD and FoundAD are currently supported by `P9` and `P8`,
  respectively. Repository-specific CLI details remain unverified until the
  external checkouts are restored and tested.

This audit makes external repository hydration and one rendered heatmap the
first critical gate.

---

## 2. Definition of a Winning Delivery

### 2.1 Required outcome

The final delivery must contain:

- One reproducible end-to-end pipeline from registered image to packaged demo
  artifact.
- One metric-bearing benchmark or proxy evaluation with valid splits and
  labels.
- Six to ten curated, traceable examples with raw image, heatmap, overlay,
  score, region contours, decision, and evidence badge.
- One wafer-style or tile-grid risk map with honest provenance.
- One concise comparison or ablation that demonstrates research judgment.
- One evidence view that exposes the exact run, support set, preprocessing, and
  limitations.
- One offline demo and one recorded fallback.

### 2.2 Success ladder

| Level | Meaning | Acceptance condition |
|---|---|---|
| L0 - Executable | The technical path works | A clean shell can build or load one run and render one heatmap. |
| L1 - Defensible | The result can be evaluated | A proxy dataset has leakage-safe splits, valid metrics, configs, and provenance. |
| L2 - Relevant | The work speaks to SiC | At least three licensed SiC examples are shown with qualitative-only badges, or the absence of usable SiC data is explicitly demonstrated. |
| L3 - Differentiated | The project has a research contribution | A controlled few-shot, preprocessing, or encoder comparison produces an interpretable result. |
| L4 - Memorable | The story is easy to understand | A judge can move from wafer risk map to one anomaly and then to its evidence in under 30 seconds. |

The minimum winning target is L0 + L1 + L2 + L4. L3 is included only when it
does not endanger those levels.

### 2.3 Final claim

Use this claim only if the required outcome is complete:

> We built a reproducible few-shot anomaly-inspection workbench for
> semiconductor imagery. It is proxy-validated on labeled data, produces
> traceable heatmaps and review decisions, and exposes the evidence still
> needed before making a SiC production claim.

---

## 3. System Architecture

### 3.1 End-to-end pipeline

```text
raw images
  -> source and license registry
  -> deterministic conversion and tiling
  -> leakage-safe split and support-set selection
  -> anomaly model adapter
  -> raw score and heatmap
  -> normal-score calibration
  -> contours, region statistics, and PASS/REVIEW/HOLD
  -> source-image and wafer-style aggregation
  -> metrics and failure-case report
  -> immutable run package
  -> offline demo manifest
```

### 3.2 Module boundaries

| Module | Responsibility | Must not do |
|---|---|---|
| Registry | Record source, modality, license, grouping, and demo permission | Infer labels from filenames without recording the rule |
| Dataset builder | Validate, convert, tile, split, and emit manifests | Modify raw source files |
| Model adapter | Fit on normal support images and emit raw predictions | Decide product thresholds |
| Calibrator | Convert raw scores into normalized scores and review decisions | Use test labels to tune thresholds |
| Postprocessor | Render overlays and extract region statistics | Claim semantic defect identity |
| Evaluator | Compute only valid metrics and uncertainty summaries | Compute mask metrics without masks |
| Packager | Freeze a run and build the demo manifest | Reference mutable notebook state |
| Demo app | Display packaged artifacts and evidence | Depend on network access or live training |

### 3.3 Target repository layout

This is the implementation contract to create:

```text
configs/
  data/
    <dataset>.yaml
  models/
    subspacead.yaml
    foundad.yaml
  demo.yaml
data/
  raw/                         # immutable and gitignored
  registry/
    sources.jsonl
  splits/
    <dataset>_<version>.csv
datasets/
  workbench/
    <dataset>/
      <category>/
        train/good/
        validation/good/
        validation/anomaly/
        test/good/
        test/anomaly/
        ground_truth/anomaly/
src/
  data/
  models/
  evaluation/
  rendering/
  packaging/
  app/
scripts/
  doctor.py
  validate_registry.py
  validate_run.py
  validate_demo.py
runs/
  <run_id>/
    run_manifest.json
    config.resolved.yaml
    environment.txt
    support_set.csv
    predictions.jsonl
    metrics.json
    metrics_manifest.json
    failure_cases.json
    heatmaps/
    overlays/
    risk_maps/
demo/
  manifest.json
  prerendered/
docs/
  claim_table.md
  run_summary.md
  demo_script.md
  architecture.png
tests/
```

---

## 4. Artifact and Interface Contracts

All paths stored in artifacts are relative to the repository root. All JSON
artifacts contain `schema_version`. All tabular outputs have stable column
names. Every run is immutable after it is marked `frozen`.

### 4.1 Source registry

File: `data/registry/sources.jsonl`

One row represents one original source image, not one generated tile.

```json
{
  "schema_version": "1.0",
  "source_image_id": "miic_image_000123",
  "dataset_id": "miic",
  "wafer_id": null,
  "source_path": "data/raw/miic/000123.png",
  "modality": "SEM",
  "source_label": "normal",
  "mask_source_path": null,
  "license_status": "verified",
  "license_reference": "data/raw/miic/LICENSE",
  "demo_allowed": true,
  "notes": ""
}
```

Required validations:

- `source_image_id` is unique.
- The source and mask paths exist when provided.
- `modality` is one of `SEM`, `PL`, `etch`, `optical`, `wafer_map`,
  `synthetic`, or `other`.
- `license_status` is one of `verified`, `restricted`, or `unknown`.
- `demo_allowed=true` requires `license_status=verified`.

### 4.2 Tile and split manifest

File: `data/splits/<dataset>_<version>.csv`

Required columns:

```text
tile_id,source_image_id,dataset_id,category,wafer_id,modality,split,label,
image_path,mask_path,tile_x,tile_y,tile_size,stride,preprocess_id,
support_eligible,demo_allowed
```

Tile identifier:

```text
<source_image_id>__x<tile_x:05d>_y<tile_y:05d>_s<tile_size>
```

Split rules:

- All tiles from one `source_image_id` belong to exactly one split.
- If `wafer_id` exists, all images from one wafer belong to exactly one split.
- Support images are normal, support-eligible, and excluded from validation and
  test.
- Test labels and masks are never read by fitting or calibration code.
- A split file is immutable after the first reported run.

### 4.3 Prediction contract

File: `runs/<run_id>/predictions.jsonl`

```json
{
  "schema_version": "1.0",
  "run_id": "20260608T120000Z_subspacead_miic_k1_seed17",
  "tile_id": "miic_image_000123__x00000_y00000_s00448",
  "raw_anomaly_score": 12.34,
  "normalized_anomaly_score": 0.91,
  "decision": "REVIEW",
  "decision_reason": "score_above_review_threshold",
  "anomalous_area_fraction": 0.023,
  "region_count": 2,
  "heatmap_path": "runs/.../heatmaps/tile.png",
  "overlay_path": "runs/.../overlays/tile.png",
  "semantic_hint": null,
  "semantic_similarity": null,
  "novelty_status": "not_evaluated"
}
```

Allowed `novelty_status` values:

- `not_evaluated`: no semantic head was run.
- `known_like`: high semantic similarity to a validated prompt or class.
- `unknown_like`: high anomaly score and low semantic similarity.

`unknown_like` is a triage hint, not proof of a new physical defect.

### 4.4 Run manifest

File: `runs/<run_id>/run_manifest.json`

Required fields:

```json
{
  "schema_version": "1.0",
  "run_id": "20260608T120000Z_subspacead_miic_k1_seed17",
  "status": "frozen",
  "git_commit": "<commit>",
  "model_name": "subspacead",
  "model_source_commit": "<commit-or-null>",
  "dataset_split_path": "data/splits/miic_v1.csv",
  "config_path": "runs/.../config.resolved.yaml",
  "support_set_path": "runs/.../support_set.csv",
  "predictions_path": "runs/.../predictions.jsonl",
  "calibration_method": "normal_validation_quantiles",
  "review_threshold": 0.99,
  "hold_threshold": 0.999,
  "hardware": "<recorded hardware>",
  "started_at": "<ISO-8601>",
  "completed_at": "<ISO-8601>"
}
```

The threshold values above describe normalized quantiles, not fixed raw-score
values.

### 4.5 Metrics manifest

File: `runs/<run_id>/metrics_manifest.json`

For every possible metric, record whether it is valid and why:

```json
{
  "schema_version": "1.0",
  "image_auroc": {"valid": true, "reason": "test image labels available"},
  "image_aupr": {"valid": true, "reason": "test image labels available"},
  "pixel_auroc": {"valid": false, "reason": "aligned masks unavailable"},
  "pro": {"valid": false, "reason": "aligned masks unavailable"}
}
```

### 4.6 Demo manifest

File: `demo/manifest.json`

The demo manifest points only to frozen run artifacts and contains:

- Featured examples in a fixed presentation order.
- One risk map and its provenance label.
- One metrics table.
- One ablation or comparison figure.
- One failure case.
- Claim and caveat badges for each panel.

`scripts/validate_demo.py` must fail when any referenced path is missing, any
run is not frozen, or any example has `demo_allowed=false`.

---

## 5. Data Protocol

### 5.1 Dataset priority and role

| Priority | Dataset | Intended role | Required evidence |
|---|---|---|---|
| 1 | MIIC | Metric-bearing semiconductor SEM proxy | License, labels, masks, documented split |
| 2 | Licensed SiC PL or etch-pit images | Qualitative SiC transfer and failure analysis | Source, license, modality, demo permission |
| 3 | MVTec AD or VisA | Pipeline sanity and benchmark fallback | License and standard labels/masks |
| 4 | NFFA or other SEM images | Qualitative modality check | Source and license |
| 5 | Synthetic montage | Risk-map product visualization only | Prominent `synthetic montage` label |

MIIC contains real SEM imagery and supports image- and pixel-level evaluation,
but the local study also documents a natural-image-to-SEM domain gap (`P7`,
Sections 3.1, 4.1, and 4.2). That makes it both relevant and scientifically
useful.

SiC PL defects can have low contrast and indistinct boundaries; PL features may
need correlation with etch-derived evidence for physical labels (`P1`,
Sections 1, 2.1.3, and 3.3; `P11`, Materials and Equipment and Results and
Discussion). Consequently, SiC images without verified labels remain
qualitative.

### 5.2 Raw-data acceptance gate

No dataset enters the pipeline until the data lead records:

- Source URL or internal source reference.
- License or usage status.
- Number of source images.
- Modality and image dimensions.
- Available image labels, boxes, masks, or wafer identifiers.
- Whether examples may be shown publicly.
- Known transformations already applied by the source.

If any item is unknown, the dataset is marked `restricted` or `unknown` and is
excluded from the final public demo.

### 5.3 Deterministic preprocessing

MVP preprocessing:

1. Decode the original without modifying it.
2. Preserve the original bit depth in raw storage.
3. Convert model input to three channels by repeating grayscale channels.
4. Tile at `448 x 448` with stride `448`.
5. Pad incomplete edge tiles using reflection padding and record padding.
6. Save lossless PNG model inputs.
7. Record `preprocess_id`, image hash, source coordinates, and conversion
   parameters.

CLAHE is an explicit ablation, not an invisible default:

- `rgb_repeat_v1`: channel repeat only.
- `rgb_repeat_clahe_v1`: channel repeat plus fixed CLAHE parameters.

Do not mix preprocessing variants inside one support set. `P1` supports testing
image enhancement for low-contrast PL imagery, but not assuming that it always
improves anomaly detection.

### 5.4 Split and leakage policy

The largest evaluation risk is tile leakage. Randomly splitting tiles from the
same source image or wafer would produce misleading metrics.

Required policy:

- Group split by `wafer_id`; fall back to `source_image_id`.
- Keep the test split untouched until the pipeline and thresholds are frozen.
- Choose support sets only from `train/good`.
- Fit score normalization and thresholds only on `validation/good`, plus
  `validation/anomaly` only when explicitly evaluating a supervised threshold.
- Record every support tile in `support_set.csv`.
- Use three fixed support-set seeds for reported 1-, 2-, and 4-shot results.
  FoundAD reports repeated few-shot combinations across three seeds, which
  provides an appropriate minimum protocol for this timebox (`P8`, Section 4
  and Supplementary results).

### 5.5 Demo-example selection

Select the final examples by Day 5 using these roles:

- One obvious normal example.
- One obvious localized anomaly.
- One subtle anomaly.
- One false positive.
- One false negative, if labels permit.
- Two or more qualitative SiC examples.

Examples are selected for explanatory range, not presented as an unbiased
performance sample. The metrics panel carries the aggregate evidence.

---

## 6. Model, Calibration, and Decision Logic

### 6.1 Primary model path

The primary implementation is a SubspaceAD adapter:

1. Extract frozen DINOv2 patch features from `k` normal support images.
2. Fit a PCA normal subspace.
3. Score each test patch using residual distance from that subspace.
4. Aggregate patch scores into an image score.
5. Resize the patch score map into a pixel heatmap.

This behavior is supported by `P9`, Sections 3.2-3.4. The paper evaluates
1-, 2-, and 4-shot settings on MVTec AD and VisA, but that evidence must not be
presented as SiC performance.

Implementation rule:

- Prefer a verified upstream checkout once hydrated.
- Wrap upstream execution behind the local prediction contract.
- Do not let the demo depend directly on an upstream output layout.
- Record upstream commit, weights, layers, resolution, PCA variance, support
  set, and seed.

### 6.2 Fallback model path

If the SubspaceAD checkout cannot be restored or run by the Day 1 gate:

- Implement the minimal frozen-feature plus PCA-residual baseline locally, or
  use a verified anomalib baseline if already available.
- Preserve the same prediction contract.
- Rename the model accurately; do not label a local approximation as the
  upstream SubspaceAD implementation.

### 6.3 FoundAD research path

FoundAD is attempted only after all baseline acceptance tests pass. It uses a
foundation encoder and nonlinear projector for few-shot anomaly detection and
has evidence on MVTec AD and VisA (`P8`, Sections 3-4).

Stop conditions:

- Stop after four engineer-hours without a valid heatmap.
- Stop immediately if required weights or rights are unavailable.
- Do not change the demo artifact contract to accommodate FoundAD.
- If successful, compare it on exactly the same split and support sets.

### 6.4 Score calibration

Raw anomaly scores are not comparable across modalities, categories, or model
runs. Each run must normalize scores using only normal validation data.

Default calibration:

```text
normalized_score = empirical_CDF(raw_score | validation/good)
review_threshold = 0.990 normal-score quantile
hold_threshold   = 0.999 normal-score quantile
```

Decision logic:

```text
PASS:
  normalized_score < review_threshold

REVIEW:
  normalized_score >= review_threshold
  and normalized_score < hold_threshold

HOLD:
  normalized_score >= hold_threshold
  or anomalous_area_fraction exceeds the configured area threshold
```

Rules:

- These are triage rules, not yield or rejection rules.
- Thresholds are labeled `heuristic` unless tuned and evaluated on a separate
  labeled validation split.
- The demo always shows the reason for the decision.
- Raw and normalized scores are both preserved.

### 6.5 Region extraction

For visualization only:

1. Smooth the heatmap using one fixed, recorded kernel.
2. Threshold at the configured heatmap percentile.
3. Remove regions below the configured minimum area.
4. Extract contours.
5. Report region count, largest region area, and total anomalous area fraction.

Do not report contour precision or defect count accuracy without region-level
ground truth.

### 6.6 Optional semantic hints

The semantic head is a stretch feature:

- Run only on anomaly regions.
- Use a fixed prompt list derived from verified SiC terminology.
- Display the top hint as `resembles <term>`, not `is <term>`.
- Preserve prompt text, encoder, similarity score, and threshold.
- Set `unknown_like` only when the anomaly score is high and all prompt
  similarities are low.

Because FoundAD itself does not establish open-vocabulary naming, this feature
must be presented as an independent exploratory head, not a FoundAD capability.

### 6.7 Risk-map aggregation

Each source image or wafer-style view aggregates tile predictions:

```text
risk_score = max(tile normalized scores)
risk_area  = mean(tile is REVIEW or HOLD)
risk_count = count(tile is REVIEW or HOLD)
```

Every risk map displays exactly one provenance badge:

- `real spatial`: coordinates come from a real wafer or source image.
- `stitched field`: coordinates come from related microscopy fields.
- `synthetic montage`: layout is a product-concept visualization.

---

## 7. Reproducible Pipeline Commands

These are the stable local interfaces to implement. Upstream model commands may
change; these commands must not.

```bash
# 0. Validate environment, repositories, weights, and datasets
python scripts/doctor.py --config configs/demo.yaml

# 1. Validate source rights and metadata
python scripts/validate_registry.py data/registry/sources.jsonl

# 2. Build deterministic tiles and leakage-safe splits
python -m src.data.build --config configs/data/<dataset>.yaml

# 3. Fit on a recorded support set and predict one split
python -m src.models.run \
  --config configs/models/subspacead.yaml \
  --split data/splits/<dataset>_<version>.csv \
  --shots 1 \
  --seed 17

# 4. Calibrate scores and create review decisions
python -m src.evaluation.calibrate --run runs/<run_id>

# 5. Compute only valid metrics and failure cases
python -m src.evaluation.evaluate --run runs/<run_id>

# 6. Render overlays and risk maps
python -m src.rendering.render --run runs/<run_id>

# 7. Freeze artifacts and create the demo package
python -m src.packaging.freeze --run runs/<run_id>
python -m src.packaging.build_demo --config configs/demo.yaml

# 8. Validate and launch the offline demo
python scripts/validate_run.py runs/<run_id>
python scripts/validate_demo.py demo/manifest.json
python -m src.app.main --manifest demo/manifest.json --offline
```

Suggested convenience targets:

```text
make doctor
make sanity
make proxy-eval
make render
make demo
make test
make smoke
```

Each command must:

- Exit nonzero on invalid input.
- Print the generated artifact paths.
- Write resolved configuration and environment information.
- Avoid silently overwriting frozen runs.

---

## 8. Evaluation Plan

### 8.1 Evaluation questions

The evaluation must answer:

1. Does the pipeline detect and localize anomalies on a labeled benchmark?
2. Does it retain useful behavior on semiconductor SEM proxy data?
3. How sensitive is it to the number of normal support examples?
4. Does CLAHE help or hurt low-contrast SiC-style imagery?
5. What are the characteristic false positives and false negatives?

### 8.2 Required experiment matrix

Run in this order and stop when the evidence is sufficient:

| Priority | Dataset | Model | Shots | Variants | Purpose |
|---|---|---|---|---|---|
| P0 | MVTec/VisA one category | Primary baseline | 1 | raw | Pipeline sanity |
| P0 | MIIC or best SEM proxy | Primary baseline | 1 | raw | Main proxy result |
| P1 | Same proxy split | Primary baseline | 1, 2, 4 | raw | Few-shot research result |
| P1 | SiC qualitative set | Primary baseline | 1 | raw, CLAHE | Transfer and failure analysis |
| P2 | Same proxy split | FoundAD | best feasible shot count | raw | Controlled method comparison |
| P3 | Selected regions | Semantic head | n/a | fixed prompts | Exploratory naming only |

For reported few-shot rows, execute seeds `17`, `23`, and `42` and report mean
and standard deviation.

### 8.3 Valid metrics

| Evidence available | Report |
|---|---|
| Image labels | Image AUROC, image AUPR, thresholded precision/recall/F1 |
| Aligned pixel masks | Pixel AUROC and PRO |
| Region boxes only | Region-hit rate at a declared overlap rule |
| Normal-only validation data | False-positive rate at review and hold thresholds |
| No labels | Score distribution, heatmaps, and qualitative failure analysis only |

Always report:

- Dataset and split version.
- Number of source images and tiles by class.
- Support images and seeds.
- Preprocessing variant.
- Hardware and end-to-end latency.
- Whether metrics are image-, tile-, pixel-, or region-level.

### 8.4 Scientific validity checks

- Compare against a constant-score sanity baseline.
- Confirm all support images are normal.
- Confirm no source or wafer group crosses splits.
- Inspect score distributions before choosing a display range.
- Report per-source metrics when tiling could overweight large images.
- Include at least one failure case in the pitch.
- Do not select the best seed as the headline result.
- Do not compare methods on different splits, support sets, or preprocessing.

### 8.5 Research result selection

Choose exactly one headline result:

1. Few-shot scaling: performance from 1 to 2 to 4 normal examples.
2. Domain transfer: benchmark versus SEM versus qualitative SiC behavior.
3. Preprocessing sensitivity: raw versus CLAHE on low-contrast imagery.
4. Method comparison: SubspaceAD-style baseline versus FoundAD on one fixed
   split.

The result must fit on one slide and include a limitation. More experiments are
not automatically more persuasive.

---

## 9. Demo Product Specification

### 9.1 Demo architecture

- Local Gradio application or an equivalently simple local UI.
- Reads only `demo/manifest.json` and referenced static artifacts.
- No model initialization, network request, or data download at demo time.
- Fixed example order and a one-click reset.
- Runs from a clean shell using one documented command.

### 9.2 Main screen

The first screen must communicate the product in under ten seconds:

- Top: wafer-style risk map with provenance badge and summary counts.
- Left: curated example selector with source and modality.
- Center: raw image and heatmap overlay with opacity control.
- Right: `PASS`, `REVIEW`, or `HOLD`, normalized score, region count, and
  decision reason.
- Bottom: evidence badge such as `proxy metric`, `SiC qualitative`, or
  `synthetic montage`.

### 9.3 Evidence screen

The evidence view is the differentiator for expert judges. It shows:

- Metric table with valid/invalid metric indicators.
- Dataset split and support-set thumbnails.
- Model, seed, preprocessing, and run ID.
- Research comparison or ablation.
- One false positive and one limitation.
- A short statement of what would be required for a production SiC pilot.

### 9.4 Four-minute presentation runbook

| Time | Action | Message |
|---|---|---|
| 0:00-0:25 | State the inspection problem | SiC defect labels are scarce and destructive validation is costly. |
| 0:25-0:55 | Show the risk map | A few normal references produce an auditable review map. |
| 0:55-1:35 | Open one anomalous tile | The heatmap localizes why the tile was escalated. |
| 1:35-2:05 | Open one subtle or failure case | The team understands limitations, not just successes. |
| 2:05-2:50 | Open evidence view | Show proxy metrics, support set, run ID, and the headline experiment. |
| 2:50-3:30 | Show qualitative SiC transfer | Explain exactly what is and is not validated. |
| 3:30-4:00 | Close with pilot path | Ask for licensed paired PL/etch data to validate the next step. |

### 9.5 Demo reliability package

Before presentation, produce:

- Offline application.
- Final screen recording.
- Static PDF or slide fallback containing the risk map, two overlays, metrics,
  and limitation.
- `docs/demo_script.md` with exact clicks and spoken claims.
- A clean-shell smoke-test log.

---

## 10. Automated Checks and Acceptance Tests

### 10.1 Data tests

- Registry schema and path validation.
- Unique source and tile IDs.
- No split overlap by source image or wafer.
- Support set contains only normal images.
- Image and mask dimensions align.
- Model input dimensions and channels are valid.
- Demo examples have verified licenses and permission.

### 10.2 Run tests

- Every split tile has exactly one prediction.
- No prediction contains `NaN` or infinite scores.
- Every heatmap matches its tile dimensions.
- Every prediction references existing heatmap and overlay files.
- Calibration uses validation-normal data only.
- Every metric has a validity reason.
- Frozen run config, support set, and predictions cannot change.

### 10.3 Demo tests

- Every manifest path exists.
- Every referenced run is frozen.
- The app starts with network disabled.
- The first screen renders in under five seconds on the presentation machine.
- All featured examples can be opened.
- Reset returns to the initial state.
- The risk-map provenance badge is visible.
- No unsupported claim or placeholder text remains.

### 10.4 Final acceptance checklist

The project is complete only when all are true:

- `make doctor`, `make test`, and `make smoke` pass.
- At least one proxy run has valid image-level metrics.
- At least six featured examples have traceable artifacts.
- At least one failure case is visible.
- A research result or honest negative result is documented.
- The demo runs offline from a clean shell.
- The backup recording and static fallback both exist.
- `docs/claim_table.md` matches the spoken pitch.

---

## 11. Seven-Day Execution Plan

The four lanes run in parallel:

- Lane A - Data and provenance.
- Lane B - Model and evaluation.
- Lane C - Pipeline and quality.
- Lane D - Demo, evidence, and pitch.

No lane may bypass the artifact contracts.

### Day 1 - Restore dependencies and prove one heatmap

**Objective:** reach L0.

Tasks:

- Clone or cache verified upstream commits outside this repository.
- Record upstream commit IDs and license files.
- Run environment diagnostics and record hardware.
- Obtain one benchmark category and verify its license.
- Render one real heatmap from one normal support image.
- Create the target repository skeleton and prediction adapter boundary.
- Draft `docs/claim_table.md`.

Exit gate:

- One command produces or loads a heatmap.
- The heatmap, image score, config, support image, and upstream commit are
  recorded.
- Repository-specific commands have been verified rather than copied from an
  unavailable checkout.

Kill rule:

- If the preferred upstream implementation has not produced a heatmap after
  four engineer-hours, use the fallback model path.

### Day 2 - Build the data plane

**Objective:** make every example traceable and leakage-safe.

Tasks:

- Register the metric-bearing proxy dataset.
- Register all candidate SiC and fallback images.
- Verify licenses and demo permission.
- Implement deterministic conversion and tiling.
- Generate grouped train, validation, and test splits.
- Implement registry and split validators.
- Select initial support sets for seeds `17`, `23`, and `42`.

Exit gate:

- One dataset builds from raw sources into the workbench layout.
- Automated leakage checks pass.
- At least six demo-safe candidate images exist.
- Every candidate can be traced to a source registry row.

Cut rule:

- If MIIC is not usable by end of day, lock MVTec/VisA as the metric-bearing
  fallback and keep any SEM/SiC imagery qualitative.

### Day 3 - Complete the baseline pipeline

**Objective:** produce the first frozen end-to-end run.

Tasks:

- Wrap the primary model behind the local run interface.
- Emit predictions, raw heatmaps, and resolved config.
- Implement normal-validation score calibration.
- Implement contours, decisions, overlays, and risk-map aggregation.
- Implement run validation and freezing.
- Build the first demo manifest from frozen artifacts.

Exit gate:

- One frozen run passes all run tests.
- At least six examples display raw image, overlay, score, and decision.
- One risk map renders with an honest provenance badge.
- The app reads the demo manifest without model code.

### Day 4 - Produce defensible evidence

**Objective:** reach L1.

Tasks:

- Run the main proxy evaluation.
- Run three seeds for the selected shot counts.
- Generate `metrics.json`, `metrics_manifest.json`, and failure cases.
- Verify per-source and tile-level results for tiling bias.
- Measure runtime on the actual presentation hardware.
- Add metrics and failure cases to the evidence view.

Exit gate:

- At least one valid aggregate metric is reported.
- Every metric identifies split, level, support set, and preprocessing.
- One false positive and one limitation are documented.
- No test data was used for threshold calibration.

### Day 5 - Add relevance and one research result

**Objective:** reach L2 and, if stable, L3.

Tasks:

- Run the baseline on the licensed SiC qualitative set.
- Run raw versus CLAHE if PL or etch imagery is available.
- Select exactly one headline research result.
- Attempt FoundAD only if all prior gates are green.
- Freeze the final featured examples.
- Write the first complete `docs/run_summary.md`.

Exit gate:

- SiC examples are explicitly labeled qualitative, or their absence is
  explained with a concrete data-acquisition ask.
- One controlled result or honest negative result is presentation-ready.
- No unfinished optional feature is required by the demo.

Kill rule:

- Stop FoundAD after four engineer-hours or on any rights/weights blocker.

### Day 6 - Harden the demo and narrative

**Objective:** reach L4.

Tasks:

- Remove runtime network and model dependencies.
- Finish the main and evidence screens.
- Validate every artifact and claim.
- Freeze `demo/manifest.json`.
- Rehearse the four-minute runbook with exact clicks.
- Record the first full backup video.
- Create the static fallback.

Exit gate:

- Offline clean-shell smoke test passes three consecutive times.
- Demo completes in under four minutes.
- Every visible claim is present in `docs/claim_table.md`.
- Backup video and static fallback are usable.

### Day 7 - Freeze and present

**Objective:** protect the finished result.

Tasks:

- Make fixes only for presentation-blocking defects.
- Run all tests and archive the final logs.
- Verify the presentation machine, display scaling, and offline mode.
- Record the final backup video.
- Rehearse questions on metrics, labels, domain gap, and pilot requirements.

Final gate:

- If the app fails once during final checks, use the recording or static
  fallback instead of debugging live.

---

## 12. Ownership and Daily Operating Model

### 12.1 Primary owners

| Role | Primary ownership | Required handoff |
|---|---|---|
| Research lead | Claim table, experiment question, result interpretation, executive story | Gives the demo lead approved language and the model lead the experiment matrix |
| Data lead | Sources, licenses, registry, tiling, splits, support sets | Gives the model lead validated split files and the demo lead approved examples |
| Model lead | Model adapters, calibration, experiments, metrics, failure analysis | Gives pipeline/demo leads frozen runs only |
| Demo and integration lead | Contracts, validators, packaging, app, smoke tests, fallback media | Gives the full team a reproducible demo package |

### 12.2 Daily rhythm

- 09:00: gate review, blocker decision, and scope cuts.
- 13:00: artifact integration into one frozen candidate run.
- 18:00: automated checks and end-to-end demo smoke test.
- 18:30: update `docs/run_summary.md` and the claim table.

### 12.3 Decision rule

When there is a conflict, prioritize in this order:

1. Demo reliability.
2. Evidence validity.
3. SiC relevance.
4. Research novelty.
5. Additional visual polish.

---

## 13. Scope-Cut Ladder

Cuts are made from the bottom upward as soon as a gate is threatened:

1. Remove semantic naming.
2. Remove FoundAD.
3. Remove extra shot counts and keep 1-shot plus one comparison.
4. Remove CLAHE ablation.
5. Replace live app interactions with fixed example navigation.
6. Replace the app with the recorded demo and static evidence slide.

Never cut:

- Source and license traceability.
- Leakage-safe splits.
- Metric validity labels.
- The failure case.
- Offline fallback.
- Honest separation of proxy and SiC evidence.

---

## 14. Risk Register and Pivots

| Risk | Early signal | Decision deadline | Pivot |
|---|---|---|---|
| Empty or unavailable upstream repos | No verified checkout or license | Day 1, hour 2 | Restore exact commits or implement a clearly named local PCA-residual baseline |
| Model or weight access blocked | Download/authentication failure | Day 1, hour 4 | Use the smallest available frozen DINOv2 model or verified anomalib fallback |
| No metric-bearing semiconductor data | MIIC unavailable or license unclear | End of Day 2 | Use MVTec/VisA for metrics and semiconductor imagery for qualitative transfer |
| Tile leakage inflates results | Same source/wafer appears across splits | Immediately | Regenerate grouped splits and invalidate affected runs |
| Weak proxy metrics | AUROC near chance or unstable seeds | Day 4 midday | Make domain-gap and failure analysis the research result |
| SiC heatmaps are uninformative | Scores follow illumination/noise | Day 5 midday | Present raw-versus-CLAHE failure analysis and request paired PL/etch pilot data |
| FoundAD integration consumes time | No valid heatmap after four hours | Day 5 | Stop and document it as future comparison |
| Thresholds appear arbitrary | No validation-normal calibration | Day 3 | Show continuous risk scores and `REVIEW` only; remove `PASS/HOLD` |
| Demo app is unstable | Any failure in repeated smoke tests | Day 6 | Use a simpler static navigator or recording |
| Unsupported business number | No local, verifiable source | Before final freeze | Remove the number and use a qualitative yield-impact statement |

---

## 15. Claims, Evidence, and Pitch Boundaries

### 15.1 Verified claims

- Few-shot anomaly detection can be implemented using frozen DINOv2 patch
  features and a PCA residual subspace; SubspaceAD evaluates this approach on
  MVTec AD and VisA (`P9`, Sections 3.2-4).
- FoundAD uses foundation-encoder features and a nonlinear projector for
  few-shot anomaly detection, with evaluation on MVTec AD and VisA (`P8`,
  Sections 3-4).
- MIIC is a large real-world SEM dataset used to evaluate image- and
  pixel-level visual anomaly detection, and the study identifies a domain gap
  from natural-image-pretrained extractors (`P7`, Sections 3.1, 4.1, and 4.2).
- 4H-SiC PL dislocations can be low contrast and have indistinct boundaries;
  image enhancement and oriented detection have been studied for BPD and TD
  detection (`P1`, Abstract and Sections 1-4).
- Paired PL and etch evidence can support non-destructive SiC defect
  localization and classification, but the demonstrated high-volume method
  relies on proprietary data and validation (`P11`, Materials and Equipment and
  Results and Discussion).

### 15.2 Assumptions to verify

- The team can legally obtain and use at least one metric-bearing dataset.
- The team can legally show at least three SiC images.
- A presentation machine can run the chosen model during development.
- A pre-rendered offline demo is acceptable to the judges.
- The upstream repositories and required model weights can be restored.

### 15.3 Approved pitch language

Use:

- "Few-shot anomaly inspection."
- "Proxy-validated on labeled benchmark or SEM data."
- "Qualitative transfer to SiC imagery."
- "Review decision" or "inspection escalation."
- "Unknown-like anomaly hint."
- "Wafer-style risk map" with its provenance label.

Avoid:

- "We solve SiC inspection."
- "Production ready."
- "We classify every SiC defect."
- "Novel defect discovered."
- "Full-wafer result" for a synthetic montage.
- "Reject" or "kill" without calibrated production evidence.
- Any accuracy number that does not come from the team's frozen run.

### 15.4 Executive close

> The next step is a focused pilot using licensed, paired SiC PL and etch
> imagery. The workbench already provides the traceability, few-shot baseline,
> and evaluation protocol needed to measure whether this approach is useful in
> that setting.

---

## 16. Immediate Start Sequence

The first four hours should happen in this order:

1. Clone or cache the exact SubspaceAD and FoundAD source commits listed in
   `planning/sources/repo_references.md` outside this repository; verify
   licenses and record any mismatch.
2. Confirm hardware, Python, CUDA or MPS support, disk space, and network/model
   access.
3. Obtain one licensed MVTec/VisA category and one candidate semiconductor
   dataset.
4. Produce one heatmap with the lowest-risk available model path.
5. Record the support image, config, source commit, and output paths.
6. Create the repository skeleton and implement the local prediction contract.

Do not begin semantic naming, a dashboard, or additional model integrations
before this sequence is complete.

---

## 17. Open Decisions

Resolve these by the stated deadline and record the answer in
`docs/run_summary.md`:

| Decision | Deadline | Owner |
|---|---|---|
| Exact judging rubric and presentation duration | Day 1 morning | Research lead |
| Available GPU and model-weight access | Day 1 morning | Model lead |
| Metric-bearing dataset and legal usage | Day 2 morning | Data lead |
| Publicly displayable SiC examples | Day 2 evening | Data lead |
| Primary headline experiment | Day 4 evening | Research lead |
| Whether FoundAD is attempted | Day 5 morning | Whole team |
| Final example set and risk-map provenance | Day 5 evening | Demo lead |

Any unresolved decision defaults to the lower-risk, more conservative claim.
