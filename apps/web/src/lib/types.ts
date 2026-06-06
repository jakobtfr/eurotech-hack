// Shared domain types for the SiC Anomaly Workbench.
// Mirrors the artifact contracts in planning/output/implementation_plan.md.

export type Verdict = "PASS" | "REVIEW" | "REJECT";

export type Modality = "SEM" | "PL" | "etch" | "wafer_map" | "synthetic";

export type WaferMapProvenance =
  | "real spatial"
  | "stitched field"
  | "synthetic montage";

/** One scored tile produced by a model run (SubspaceAD / FoundAD). */
export interface TileResult {
  tile_id: string;
  model: string;
  model_config_path: string;
  anomaly_score: number;
  heatmap_path: string;
  overlay_path: string;
  region_tag: string | null;
  semantic_hint: string | null;
  novelty_flag: boolean;
  verdict: Verdict;
}

/** Provenance/registry metadata for a demo image. */
export interface SourceRegistryRow {
  tile_id: string;
  wafer_id: string;
  source_id: string;
  source_file: string;
  modality: Modality;
  image_path: string;
  source_image_path: string;
  split: "support" | "validation" | "test" | "demo";
  source_label: string | null;
  mask_path: string | null;
  license_status: "verified" | "restricted" | "unknown";
  demo_allowed: boolean;
  // Tiling / preprocessing provenance (plan §4).
  tile_x?: number;
  tile_y?: number;
  tile_size?: number;
  preprocess?: string;
}

/** A demo example as referenced by demo/manifest.json. */
export interface DemoExample {
  registry: SourceRegistryRow;
  result?: TileResult;
  /** Short human label for selectors / narration. */
  title: string;
  /** One-line caption describing the tile. */
  caption: string;
  evidence_class: EvidenceClass;
  caveats: CaveatKind[];
  /** k-shot used for this support set (demo flavor). */
  k_shot: number;
}

// ---------------------------------------------------------------------------
// Honest-framing + evidence vocabulary
// ---------------------------------------------------------------------------

export type CaveatKind =
  | "proxy metric"
  | "SiC qualitative"
  | "synthetic montage"
  | "restricted source";

export type EvidenceClass = "verified" | "qualitative";

// ---------------------------------------------------------------------------
// Risk map
// ---------------------------------------------------------------------------

export interface RiskTile {
  /** Links back to a DemoExample when has_result is true. */
  tile_id: string;
  col: number;
  row: number;
  in_wafer: boolean;
  anomaly_score: number;
  verdict: Verdict;
  has_result: boolean;
}

export interface RiskMap {
  provenance: WaferMapProvenance;
  wafer_id: string;
  cols: number;
  rows: number;
  threshold_review: number;
  threshold_reject: number;
  tiles: RiskTile[];
  summary: {
    pass: number;
    review: number;
    reject: number;
    inspected: number;
  };
}

// ---------------------------------------------------------------------------
// Evidence / metrics
// ---------------------------------------------------------------------------

export interface EvidenceMetric {
  name: string;
  value: number | null;
  /** What is needed to compute this metric. */
  requires: "labels" | "masks" | "none";
  available: boolean;
  format: "auroc" | "percent" | "raw";
  evidence_class: EvidenceClass;
  note?: string;
}

export interface MetricsManifest {
  run_dir: string;
  model: string;
  model_config_path: string;
  dataset: string;
  split: string;
  k_shot: number;
  image_res: number;
  metrics: EvidenceMetric[];
  framing: string;
}

// ---------------------------------------------------------------------------
// Research
// ---------------------------------------------------------------------------

export interface ResearchSection {
  id: "subspacead" | "foundad" | "domain-gap";
  title: string;
  status: "executable baseline" | "research headline" | "open caveat";
  tagline: string;
  body: string[];
  badges: CaveatKind[];
  source_ref?: string;
}

// ---------------------------------------------------------------------------
// Top-level demo manifest (mirrors demo/manifest.json)
// ---------------------------------------------------------------------------

export interface DemoManifest {
  version: string;
  generated_at: string;
  model: string;
  default_example_id: string;
  threshold_review: number;
  threshold_reject: number;
  examples: DemoExample[];
  risk_map: RiskMap;
  metrics: MetricsManifest;
  research: ResearchSection[];
}
