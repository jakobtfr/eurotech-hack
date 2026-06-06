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
}

/** A demo example as referenced by demo/manifest.json. */
export interface DemoExample {
  registry: SourceRegistryRow;
  result?: TileResult;
}
