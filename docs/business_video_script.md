# Business Video Script

Target length: 2 minutes.

Goal: problem solved, market, Hong Kong fit, business plan, team, and why this
can scale. Keep the tone calm and credible. Do not overclaim production
readiness.

## Recording Plan

| Time | Visual | Script |
|---|---|---|
| 0:00-0:15 | Title slide or landing/workbench hero | "Semiconductor inspection has a data bottleneck. Defects are rare, expert labels are expensive, and engineers still need fast, traceable review decisions." |
| 0:15-0:35 | Workbench/risk map | "We built an auditable anomaly-triage workbench for semiconductor imagery. With a small number of normal references, it produces anomaly scores, heatmaps, review decisions, and the evidence trail behind each decision." |
| 0:35-0:55 | Show raw image + heatmap + overlay | "The product is not a black box. An engineer can see the source image, the highlighted region, the score, the support-shot count, and the caveats. It is designed for inspection escalation, not automatic wafer rejection." |
| 0:55-1:15 | Open `results/judge_evidence/sic_performance_and_integrity.png` | "We also trained on real 4H-SiC photoluminescence imagery. Our improved YOLO11s oriented-box detector raised precision from 58.5% to 66.9% and mAP50-95 from 36.2% to 39.9% on an acquisition-session-disjoint validation split." |
| 1:15-1:35 | Open `results/judge_evidence/miic_reliability_evidence.png` | "For broader semiconductor anomaly triage, our MIIC SEM proxy evidence reaches about 0.905 AUROC with explicit false positives, false negatives, and uncertainty-review behavior. We separate proxy evidence from SiC claims on purpose." |
| 1:35-1:50 | Market / Hong Kong slide | "The market is real: semiconductor metrology and inspection equipment is roughly a nine-billion-dollar global market, while silicon carbide is a fast-growing power-semiconductor material. Hong Kong is building advanced manufacturing and microelectronics capacity, which makes it a strong pilot ecosystem." |
| 1:50-2:00 | Team / ask | "We are a TUM team with AI, CS, quantum systems, industry, and research experience. Our go-to-market is pilot-first: partner with a lab, OSAT, fab, or inspection vendor and prove review-time reduction on licensed SiC data." |

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

The market is real: semiconductor metrology and inspection equipment is roughly
a nine-billion-dollar global market, while silicon carbide is a fast-growing
power-semiconductor material. Hong Kong is building advanced manufacturing and
microelectronics capacity, which makes it a strong pilot ecosystem.

We are a TUM team with AI, CS, quantum systems, industry, and research
experience. Our go-to-market is pilot-first: partner with a lab, OSAT, fab, or
inspection vendor; ingest licensed SiC inspection data; measure review-time
reduction and failure modes; then integrate into the inspection workflow.

## Market Slide

Use this if the video has room for one compact investor-style slide.

| Layer | Definition | Sizing to say |
|---|---|---|
| TAM | Global semiconductor inspection/metrology and adjacent SiC inspection demand | Semiconductor metrology and inspection equipment was estimated around USD 8.98B in 2024, with forecasts around USD 16.21B by 2033. The silicon carbide market was estimated around USD 4.59B in 2025 and forecast near USD 9.56B by 2033. |
| SAM | Semiconductor fabs, OSATs, labs, inspection vendors, and SiC/power-device teams that need image-based defect triage | Start with inspection teams already paying for microscopy, metrology, yield engineering, and review workflows. |
| SOM | First beachhead | Paid pilots with Hong Kong / Greater Bay Area labs, OSATs, inspection vendors, and applied research partners using licensed SiC PL/SEM/etch data. |

Suggested wording: "We are not trying to replace inspection tools on day one.
We start as the AI review layer on top of existing imaging workflows."

## Team Slide

Keep this to 10 seconds unless the video is under time.

- We are all TUM students.
- Sparsh: Management and Technology, FDE at BCG, applied AI experience at
  Celonis, NUS, and Allianz. Eurotech Fellow
- Justin: Head of TUM.ai software engineering, experienced AI dev;
- Jakob is currently working at Amazon, also Head of TUM.ai software engineering.
- Damia: Quantum Systems at TUM/LMU, research experience with UPenn and
  Cambridge, currently working at Fraunhofer, TUM Venture Labs fellow, and
  EuroTech fellow.

Suggested wording: "The team combines applied AI delivery, software engineering
leadership, semiconductor-relevant research, and industry execution."

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
