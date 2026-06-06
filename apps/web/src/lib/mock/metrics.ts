import type { MetricsManifest } from "@/lib/types";

// Proxy (MIIC SEM) evaluation. Image-level metrics are valid because labels
// exist; pixel PRO and any SiC image metric are intentionally ungated to null
// to demonstrate provenance gating — no metric is shown without evidence.
export const METRICS: MetricsManifest = {
  run_dir: "runs/20260603_1042_subspacead_miic_sem",
  model: "subspacead",
  model_config_path: "runs/20260603_1042_subspacead_miic_sem/config.yaml",
  dataset: "MIIC (SEM proxy)",
  split: "test",
  k_shot: 4,
  image_res: 512,
  framing:
    "Image metrics below are proxy-validated on MIIC SEM with real labels. " +
    "Pixel PRO and SiC image AUROC are withheld (null) because aligned masks " +
    "and labeled SiC data are not available — those remain qualitative.",
  metrics: [
    {
      name: "Image AUROC",
      value: 0.942,
      requires: "labels",
      available: true,
      format: "auroc",
      evidence_class: "verified",
      note: "MIIC test split · 4-shot support",
    },
    {
      name: "Image AUPR",
      value: 0.911,
      requires: "labels",
      available: true,
      format: "auroc",
      evidence_class: "verified",
      note: "Precision–recall area, anomaly = positive",
    },
    {
      name: "Pixel AUROC",
      value: 0.876,
      requires: "masks",
      available: true,
      format: "auroc",
      evidence_class: "verified",
      note: "2 annotated masks · localization sanity only",
    },
    {
      name: "Pixel PRO",
      value: null,
      requires: "masks",
      available: false,
      format: "auroc",
      evidence_class: "verified",
      note: "Needs aligned masks — 2/6 anomalies annotated",
    },
    {
      name: "SiC Image AUROC",
      value: null,
      requires: "labels",
      available: false,
      format: "auroc",
      evidence_class: "qualitative",
      note: "No labeled SiC data — qualitative transfer only",
    },
  ],
};
