import type { ResearchSection } from "@/lib/types";

export const RESEARCH: ResearchSection[] = [
  {
    id: "subspacead",
    title: "SubspaceAD",
    status: "executable baseline",
    tagline: "Training-free · frozen DINOv2 + PCA residual scoring",
    body: [
      "The executable path for this demo. SubspaceAD needs no training: it extracts frozen DINOv2 patch features from a handful of normal tiles, fits a PCA subspace over them, and scores each test patch by its residual outside that subspace.",
      "Because there is no fit-to-failure step, it works from scarce normal examples — exactly the few-shot regime semiconductor inspection lives in. Every heatmap in this workbench comes from this path.",
    ],
    badges: ["proxy metric"],
    source_ref: "P9 · 2602.23013v3 §3.2–3.4 · R2 README",
  },
  {
    id: "foundad",
    title: "FoundAD",
    status: "research headline",
    tagline: "Foundation-encoder anomaly detection · DINOv3 projectors",
    body: [
      "The research headline. FoundAD fits the foundation-encoder thesis and reports strong MVTec-AD / VisA numbers, but the quick path depends on DINOv3 rights and downloaded projector assets.",
      "It stays optional: shown as a comparison only if it runs by mid-week, otherwise framed as the direction-of-travel. The demo never risks itself on FoundAD.",
    ],
    badges: [],
    source_ref: "P8 · 2510.01934v1 Tables 1–5 · R1 README Quick Start",
  },
  {
    id: "domain-gap",
    title: "Proxy → SiC domain gap",
    status: "open caveat",
    tagline: "What transfers from SEM proxy, and what still needs SiC labels",
    body: [
      "Metrics are proxy-validated on MIIC SEM, which the source explicitly warns carries a natural-image-pretraining domain gap. SiC PL / etch-pit tiles are shown qualitatively only.",
      "PL dislocation signatures are low-contrast and their labels typically depend on destructive etch validation. We separate proxy-validated evidence from qualitative SiC transfer everywhere in the UI rather than overclaiming.",
    ],
    badges: ["SiC qualitative", "restricted source"],
    source_ref: "P7 §3.1, 4.1–4.2 · P1 · P11",
  },
];
