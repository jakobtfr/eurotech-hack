# Executive Demo Script

Audience: semiconductor, manufacturing, and investment executives. Target time:
four minutes.

## Setup

```bash
PATH="$HOME/.nvm/versions/node/v24.16.0/bin:$PATH" pnpm --filter web dev
```

Open:

```text
http://localhost:3000/workbench
```

Backup route:

```text
http://localhost:3000/demo
```

## Four-Minute Run

| Time | Screen | Talk track |
|---|---|---|
| 0:00-0:25 | Workbench header | "Semiconductor inspection has a data problem: defects are rare, labels are expensive, and engineers still need traceable review decisions." |
| 0:25-0:55 | Worklist and risk map | "This is a recovered MIIC SEM proxy run. We use eight normal references, frozen DINOv2 features, and a PCA residual model. No gradient training, no hidden online step." |
| 0:55-1:35 | Obvious SEM anomaly | "The tile escalates because its patch features leave the normal subspace. The heatmap is the explanation, not just a score." |
| 1:35-2:05 | Moderate or sparse anomaly | "The useful product is a review queue: some cases are obvious, some are distributed, and every result carries the source image, support set, preprocessing, and run ID." |
| 2:05-2:35 | Missed anomaly / false positive | "We deliberately show failure cases. That is what makes this pilot-ready: threshold tuning and support-set design are visible, not buried." |
| 2:35-3:15 | Evidence / metrics | "Image AUROC is 0.866 on this recovered SEM proxy split. Pixel metrics are withheld because masks were not recovered. We do not claim evidence we do not have." |
| 3:15-4:00 | Close | "The ask is a focused pilot: licensed paired SiC PL/etch/SEM images with labels or masks. We already have the audit trail, baseline model, and demo shell to measure value quickly." |

## Demo Rules

- Say "SEM proxy" for MIIC. Do not say "validated SiC performance."
- Say "triage" or "inspection escalation." Do not say "reject."
- Mention that MIIC partial license status is unknown; use internally unless
  rights are clarified.
- If the live app fails, open the guided route `/demo`; if that fails, use the
  screenshots from browser verification and the metrics in `docs/claim_table.md`.

## Questions To Expect

**Why no pixel metric?**
The partial archive did not recover aligned masks. The heatmaps are real
artifacts, but pixel AUROC remains gated.

**Is this trained on defects?**
No. The baseline fits a normal subspace from normal support tiles. It is
few-shot normal-reference anomaly detection.

**What makes this valuable?**
It reduces sparse-label inspection into an auditable review queue: source,
support set, preprocessing, score, heatmap, decision, and known limitations.

**What do you need for a fab pilot?**
Licensed paired SiC inspection imagery, ideally PL plus etch/SEM evidence, with
image labels and a small set of masks for quantitative localization.
