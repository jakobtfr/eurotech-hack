import type {
  CaveatKind,
  DemoExample,
  EvidenceClass,
  Modality,
  Verdict,
} from "@/lib/types";

export const THRESHOLD_REVIEW = 0.35;
export const THRESHOLD_HOLD = 0.7;
const RUN_TS = "20260603_1042";

export function verdictForScore(
  score: number,
  review = THRESHOLD_REVIEW,
  hold = THRESHOLD_HOLD,
): Verdict {
  if (score >= hold) return "HOLD";
  if (score >= review) return "REVIEW";
  return "PASS";
}

interface Seed {
  tile_id: string;
  wafer_id: string;
  source_id: string;
  modality: Modality;
  category: string;
  score: number;
  title: string;
  caption: string;
  region_tag: string | null;
  semantic_hint: string | null;
  novelty: boolean;
  source_label: string | null;
  license: "verified" | "restricted" | "unknown";
  evidence_class: EvidenceClass;
  caveats: CaveatKind[];
  k_shot: number;
  tile_x: number;
  tile_y: number;
  hasMask: boolean;
}

function build(s: Seed): DemoExample {
  const verdict = verdictForScore(s.score);
  const isAnomaly = verdict !== "PASS";
  const folder = isAnomaly ? "test/anomaly" : "test/good";
  const runDir = `runs/${RUN_TS}_subspacead_${s.category}`;
  return {
    title: s.title,
    caption: s.caption,
    evidence_class: s.evidence_class,
    caveats: s.caveats,
    k_shot: s.k_shot,
    registry: {
      tile_id: s.tile_id,
      wafer_id: s.wafer_id,
      source_id: s.source_id,
      source_file: `raw/${s.source_id}/${s.tile_id}.tif`,
      modality: s.modality,
      image_path: `datasets/workbench/${s.category}/${folder}/${s.tile_id}.png`,
      source_image_path: `raw/${s.source_id}/${s.tile_id}.tif`,
      split: "demo",
      source_label: s.source_label,
      mask_path: s.hasMask
        ? `datasets/workbench/${s.category}/ground_truth/anomaly/${s.tile_id}_mask.png`
        : null,
      license_status: s.license,
      demo_allowed: true,
      tile_x: s.tile_x,
      tile_y: s.tile_y,
      tile_size: 512,
      preprocess:
        s.modality === "PL" || s.modality === "etch"
          ? "rgb_repeat+clahe_v1"
          : "rgb_repeat",
    },
    result: {
      tile_id: s.tile_id,
      model: "subspacead",
      model_config_path: `${runDir}/config.yaml`,
      anomaly_score: s.score,
      heatmap_path: `${runDir}/heatmaps/${s.tile_id}.png`,
      overlay_path: `${runDir}/overlays/${s.tile_id}.png`,
      region_tag: s.region_tag,
      semantic_hint: s.semantic_hint,
      novelty_flag: s.novelty,
      verdict,
    },
  };
}

export const DEMO_EXAMPLES: DemoExample[] = [
  build({
    tile_id: "miic_sem_w12__x0000_y0000_s0512",
    wafer_id: "MIIC-lot7-w12",
    source_id: "MIIC",
    modality: "SEM",
    category: "miic_sem",
    score: 0.08,
    title: "Nominal die",
    caption:
      "Integrated-circuit SEM tile. Dense periodic structure, no residual — matches the support set.",
    region_tag: null,
    semantic_hint: null,
    novelty: false,
    source_label: "normal",
    license: "verified",
    evidence_class: "verified",
    caveats: ["proxy metric"],
    k_shot: 4,
    tile_x: 0,
    tile_y: 0,
    hasMask: false,
  }),
  build({
    tile_id: "miic_sem_w12__x0512_y0000_s0512",
    wafer_id: "MIIC-lot7-w12",
    source_id: "MIIC",
    modality: "SEM",
    category: "miic_sem",
    score: 0.14,
    title: "Nominal die · field edge",
    caption:
      "Periodic layout near the field edge. Slight intensity gradient, still within normal variation.",
    region_tag: null,
    semantic_hint: null,
    novelty: false,
    source_label: "normal",
    license: "verified",
    evidence_class: "verified",
    caveats: ["proxy metric"],
    k_shot: 4,
    tile_x: 512,
    tile_y: 0,
    hasMask: false,
  }),
  build({
    tile_id: "miic_sem_w12__x1024_y0512_s0512",
    wafer_id: "MIIC-lot7-w12",
    source_id: "MIIC",
    modality: "SEM",
    category: "miic_sem",
    score: 0.52,
    title: "Particle residue",
    caption:
      "Localized bright residue breaking lattice periodicity. Routed for human review.",
    region_tag: "localized anomaly",
    semantic_hint: "particle / residue (hint)",
    novelty: true,
    source_label: "proxy_anomaly",
    license: "verified",
    evidence_class: "verified",
    caveats: ["proxy metric"],
    k_shot: 4,
    tile_x: 1024,
    tile_y: 512,
    hasMask: true,
  }),
  build({
    tile_id: "miic_sem_w12__x1536_y1024_s0512",
    wafer_id: "MIIC-lot7-w12",
    source_id: "MIIC",
    modality: "SEM",
    category: "miic_sem",
    score: 0.86,
    title: "Pattern collapse",
    caption:
      "Clustered structural break with high-area deviation from the support set.",
    region_tag: "high-area anomaly",
    semantic_hint: "pattern collapse (hint)",
    novelty: true,
    source_label: "proxy_anomaly",
    license: "verified",
    evidence_class: "verified",
    caveats: ["proxy metric"],
    k_shot: 4,
    tile_x: 1536,
    tile_y: 1024,
    hasMask: true,
  }),
  build({
    tile_id: "sic_pl_w03__x0000_y0000_s0512",
    wafer_id: "SiC-4H-w03",
    source_id: "Zenodo-SiC",
    modality: "PL",
    category: "sic_pl",
    score: 0.19,
    title: "Clean epi",
    caption:
      "Photoluminescence tile with uniform band-edge emission. No dislocation signature.",
    region_tag: null,
    semantic_hint: null,
    novelty: false,
    source_label: "normal",
    license: "verified",
    evidence_class: "qualitative",
    caveats: ["SiC qualitative"],
    k_shot: 2,
    tile_x: 0,
    tile_y: 0,
    hasMask: false,
  }),
  build({
    tile_id: "sic_pl_w03__x0512_y0512_s0512",
    wafer_id: "SiC-4H-w03",
    source_id: "Zenodo-SiC",
    modality: "PL",
    category: "sic_pl",
    score: 0.61,
    title: "BPD candidate",
    caption:
      "Low-contrast linear feature consistent with a basal-plane dislocation. Qualitative transfer.",
    region_tag: "localized anomaly",
    semantic_hint: "BPD-like (qualitative)",
    novelty: true,
    source_label: "unknown",
    license: "verified",
    evidence_class: "qualitative",
    caveats: ["SiC qualitative"],
    k_shot: 2,
    tile_x: 512,
    tile_y: 512,
    hasMask: false,
  }),
  build({
    tile_id: "sic_etch_w03__x0000_y0000_s0512",
    wafer_id: "SiC-4H-w03",
    source_id: "P11",
    modality: "etch",
    category: "sic_etch",
    score: 0.58,
    title: "Etch-pit cluster",
    caption:
      "KOH etch-pit field. Clustered pits suggest threading-edge dislocations — restricted source.",
    region_tag: "localized anomaly",
    semantic_hint: "TED cluster (qualitative)",
    novelty: true,
    source_label: "unknown",
    license: "restricted",
    evidence_class: "qualitative",
    caveats: ["SiC qualitative", "restricted source"],
    k_shot: 1,
    tile_x: 0,
    tile_y: 0,
    hasMask: false,
  }),
  build({
    tile_id: "wafer_montage__field_c4r2_s0512",
    wafer_id: "demo-montage",
    source_id: "private",
    modality: "synthetic",
    category: "montage",
    score: 0.79,
    title: "Montage · hot field",
    caption:
      "Synthetic montage field assembled from related crops. Concept visualization only.",
    region_tag: "clustered hot tiles",
    semantic_hint: null,
    novelty: true,
    source_label: null,
    license: "unknown",
    evidence_class: "qualitative",
    caveats: ["synthetic montage"],
    k_shot: 1,
    tile_x: 2048,
    tile_y: 1024,
    hasMask: false,
  }),
];

export const DEFAULT_EXAMPLE_ID = DEMO_EXAMPLES[0].registry.tile_id;
