# Business Video Script

Target length: 2 minutes.

Goal: problem solved, market, Hong Kong fit, business plan, and why this can
scale. Keep the tone calm and credible. Do not overclaim production readiness.

## Recording Plan

| Time | Visual | Script |
|---|---|---|
| 0:00-0:15 | Title slide or landing/workbench hero | "Semiconductor inspection has a data bottleneck. Defects are rare, expert labels are expensive, and engineers still need fast, traceable review decisions." |
| 0:15-0:35 | Workbench/risk map | "We built an auditable anomaly-triage workbench for semiconductor imagery. With a small number of normal references, it produces anomaly scores, heatmaps, review decisions, and the evidence trail behind each decision." |
| 0:35-0:55 | Show raw image + heatmap + overlay | "The product is not a black box. An engineer can see the source image, the highlighted region, the score, the support-shot count, and the caveats. It is designed for inspection escalation, not automatic wafer rejection." |
| 0:55-1:15 | Open `results/judge_evidence/sic_performance_and_integrity.png` | "We also trained on real 4H-SiC photoluminescence imagery. Our improved YOLO11s oriented-box detector raised precision from 58.5% to 66.9% and mAP50-95 from 36.2% to 39.9% on an acquisition-session-disjoint validation split." |
| 1:15-1:35 | Open `results/judge_evidence/miic_reliability_evidence.png` | "For broader semiconductor anomaly triage, our MIIC SEM proxy evidence reaches about 0.905 AUROC with explicit false positives, false negatives, and uncertainty-review behavior. We separate proxy evidence from SiC claims on purpose." |
| 1:35-1:50 | Hong Kong / ecosystem slide | "This fits Hong Kong because the ecosystem has advanced manufacturing, packaging, inspection, logistics, and applied research partners. A pilot can start with a small licensed dataset rather than a massive labeling program." |
| 1:50-2:00 | Final ask | "Our go-to-market is pilot-first: partner with a lab, OSAT, fab, or inspection vendor; ingest licensed SiC inspection data; measure review-time reduction and failure modes; then integrate into the inspection workflow." |

## One-Take Version

Semiconductor inspection has a data bottleneck. Defects are rare, expert labels
are expensive, and engineers still need fast, traceable review decisions.

We built an auditable anomaly-triage workbench for semiconductor imagery. With a
small number of normal references, it produces anomaly scores, heatmaps, review
decisions, and the evidence trail behind each decision.

The product is not a black box. An engineer can inspect the source image, the
highlighted region, the score, the support-shot count, and the caveats. It is
designed for inspection escalation, not automatic wafer rejection.

We also trained on real 4H-SiC photoluminescence imagery. Our improved YOLO11s
oriented-box detector raised precision from 58.5% to 66.9% and mAP50-95 from
36.2% to 39.9% on an acquisition-session-disjoint validation split.

For broader semiconductor anomaly triage, our MIIC SEM proxy evidence reaches
about 0.905 AUROC with explicit false positives, false negatives, and
uncertainty-review behavior. We separate proxy evidence from SiC claims on
purpose.

This fits Hong Kong because the ecosystem has advanced manufacturing, packaging,
inspection, logistics, and applied research partners. A pilot can start with a
small licensed dataset rather than a massive labeling program.

Our go-to-market is pilot-first: partner with a lab, OSAT, fab, or inspection
vendor; ingest licensed SiC inspection data; measure review-time reduction and
failure modes; then integrate into the inspection workflow.

## Rubric Beats

- Innovation: few-shot, evidence-traceable semiconductor inspection rather than
  a score-only model.
- Impact and scalability: reduces unprioritized inspection review and can expand
  across modalities after target-line validation.
- Feasibility: working app, real SiC validation, proxy reliability package, and
  reproducible result artifacts.
- Hong Kong alignment: strong fit for advanced manufacturing, semiconductor
  packaging, inspection vendors, and applied university/fab partnerships.
- Presentation: be crisp, honest, and visual; lead with the problem, show proof,
  close with the pilot ask.

## Do Not Say

- "Production-ready."
- "Automatic wafer rejection."
- "This fully solves SiC inspection."
- "MIIC proves SiC performance."
- "Every defect is caught."
