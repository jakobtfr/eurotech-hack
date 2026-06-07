# Tech Video Script

Target length: 2 minutes.

Goal: show the running demo, explain what was built, cite technical results, and
make the honesty boundaries obvious.

## Pre-Recording Checklist

Run the web app:

```bash
pnpm --filter web dev
```

Open:

```text
http://localhost:3000/workbench
```

Backup route:

```text
http://localhost:3000/demo
```

Use Node 24 if possible. The repo declares `>=24 <25`, and Node 25 prints an
engine warning.

## Recording Plan

| Time | Screen | Script |
|---|---|---|
| 0:00-0:15 | Terminal or repo tree | "This is the technical demo for our semiconductor anomaly workbench. The repo contains the Next.js app, backend pipeline, configs, validators, frozen demo artifacts, and curated result evidence." |
| 0:15-0:35 | `http://localhost:3000/workbench` | "The live workbench loads a validated demo manifest and shows raw SEM tiles, heatmaps, overlays, anomaly scores, verdicts, support-shot count, and caveats." |
| 0:35-0:55 | Click obvious anomaly | "This example is a recovered MIIC SEM proxy anomaly. The model output is real: residual heatmap, overlay, score, and HOLD decision. MIIC is a semiconductor SEM proxy, not our SiC validation claim." |
| 0:55-1:10 | Click missed anomaly / false positive | "We deliberately show misses and false positives. The point is auditability: the system exposes failure boundaries instead of hiding them behind a single metric." |
| 1:10-1:30 | Evidence/metrics panel or `results/judge_evidence/miic_reliability_evidence.png` | "For MIIC reliability evidence, the package reports about 0.905 AUROC, 0.897 AUPR, 91.8% accuracy, and the confusion matrix: 98 true positives, 327 true negatives, 20 false positives, and 18 false negatives." |
| 1:30-1:50 | `results/judge_evidence/sic_performance_and_integrity.png` | "For the real 4H-SiC result, we trained an improved YOLO11s-OBB detector at 1024 pixels. Precision improved from 0.585 to 0.669, mAP50 from 0.596 to 0.621, and mAP50-95 from 0.362 to 0.399 on an acquisition-session-disjoint validation split." |
| 1:50-2:00 | `HONESTY.md` or repo docs | "The repository includes `HONESTY.md`, result summaries, validators, and reproduction scripts. We are explicit about what is real SiC, what is proxy evidence, and what still needs target-domain pilot validation." |

## One-Take Version

This is the technical demo for our semiconductor anomaly workbench. The repo
contains the Next.js app, backend pipeline, configs, validators, frozen demo
artifacts, and curated result evidence.

The live workbench loads a validated demo manifest and shows raw SEM tiles,
heatmaps, overlays, anomaly scores, verdicts, support-shot count, and caveats.

This example is a recovered MIIC SEM proxy anomaly. The model output is real:
residual heatmap, overlay, score, and HOLD decision. MIIC is a semiconductor SEM
proxy, not our SiC validation claim.

We deliberately show misses and false positives. The point is auditability: the
system exposes failure boundaries instead of hiding them behind a single metric.

For MIIC reliability evidence, the package reports about 0.905 AUROC, 0.897
AUPR, 91.8% accuracy, and the confusion matrix: 98 true positives, 327 true
negatives, 20 false positives, and 18 false negatives.

For the real 4H-SiC result, we trained an improved YOLO11s-OBB detector at 1024
pixels. Precision improved from 0.585 to 0.669, mAP50 from 0.596 to 0.621, and
mAP50-95 from 0.362 to 0.399 on an acquisition-session-disjoint validation
split.

The repository includes `HONESTY.md`, result summaries, validators, and
reproduction scripts. We are explicit about what is real SiC, what is proxy
evidence, and what still needs target-domain pilot validation.

## Technical Claims To Keep Clean

- Say: "MIIC is semiconductor SEM proxy evidence."
- Say: "Real SiC evidence is the 4H-SiC photoluminescence YOLO11s-OBB result."
- Say: "Validation split is acquisition-session-disjoint."
- Say: "BPD recall remains a weakness."
- Do not say: "MIIC proves SiC performance."
- Do not say: "Confidence is physical proof of a defect."
- Do not say: "This is production rejection."

## Backup Demo Path

If the live app stumbles:

1. Open `results/judge_evidence/sic_performance_and_integrity.png`.
2. Open `results/judge_evidence/miic_reliability_evidence.png`.
3. Open `results/sic_4h_yolo11s_obb/medium_defect_mosaic_demo/01_model_predictions_with_defect_mosaic.jpg`.
4. Narrate the same script using those static artifacts.
