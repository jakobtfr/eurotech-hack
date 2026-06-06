import type {
  CaveatKind,
  DemoManifest,
  EvidenceClass,
  Modality,
  Verdict,
  WaferMapProvenance,
} from "@/lib/types";

const VERDICTS = ["PASS", "REVIEW", "HOLD"] satisfies Verdict[];
const MODALITIES = [
  "SEM",
  "PL",
  "etch",
  "optical",
  "wafer_map",
  "synthetic",
  "other",
] satisfies Modality[];
const EVIDENCE_CLASSES = ["verified", "qualitative"] satisfies EvidenceClass[];
const CAVEATS = [
  "proxy metric",
  "SiC qualitative",
  "synthetic montage",
  "restricted source",
] satisfies CaveatKind[];
const PROVENANCE = [
  "real spatial",
  "stitched field",
  "synthetic montage",
] satisfies WaferMapProvenance[];

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function assertString(value: unknown, path: string) {
  if (typeof value !== "string" || value.length === 0) {
    throw new Error(`${path} must be a non-empty string`);
  }
}

function assertNumber(value: unknown, path: string) {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new Error(`${path} must be a finite number`);
  }
}

function assertBoolean(value: unknown, path: string) {
  if (typeof value !== "boolean") {
    throw new Error(`${path} must be a boolean`);
  }
}

function assertEnum<T extends string>(
  value: unknown,
  allowed: readonly T[],
  path: string,
) {
  if (typeof value !== "string" || !allowed.includes(value as T)) {
    throw new Error(`${path} must be one of: ${allowed.join(", ")}`);
  }
}

function assertStringOrNull(value: unknown, path: string) {
  if (value !== null && typeof value !== "string") {
    throw new Error(`${path} must be a string or null`);
  }
}

export function assertDemoManifest(value: unknown): asserts value is DemoManifest {
  if (!isRecord(value)) throw new Error("manifest must be an object");
  assertString(value.version, "version");
  assertString(value.generated_at, "generated_at");
  assertString(value.model, "model");
  assertString(value.default_example_id, "default_example_id");
  assertNumber(value.threshold_review, "threshold_review");
  assertNumber(value.threshold_hold, "threshold_hold");

  if (!Array.isArray(value.examples) || value.examples.length === 0) {
    throw new Error("examples must be a non-empty array");
  }

  const exampleIds = new Set<string>();
  value.examples.forEach((example, i) => {
    const path = `examples[${i}]`;
    if (!isRecord(example)) throw new Error(`${path} must be an object`);
    assertString(example.title, `${path}.title`);
    assertString(example.caption, `${path}.caption`);
    assertEnum(example.evidence_class, EVIDENCE_CLASSES, `${path}.evidence_class`);

    if (!Array.isArray(example.caveats)) {
      throw new Error(`${path}.caveats must be an array`);
    }
    example.caveats.forEach((caveat, j) => {
      assertEnum(caveat, CAVEATS, `${path}.caveats[${j}]`);
    });
    assertNumber(example.k_shot, `${path}.k_shot`);

    const registry = example.registry;
    if (!isRecord(registry)) throw new Error(`${path}.registry must be an object`);
    assertString(registry.tile_id, `${path}.registry.tile_id`);
    assertString(registry.wafer_id, `${path}.registry.wafer_id`);
    assertString(registry.source_id, `${path}.registry.source_id`);
    assertString(registry.source_file, `${path}.registry.source_file`);
    assertEnum(registry.modality, MODALITIES, `${path}.registry.modality`);
    assertString(registry.image_path, `${path}.registry.image_path`);
    assertString(registry.source_image_path, `${path}.registry.source_image_path`);
    assertEnum(
      registry.split,
      ["support", "validation", "test", "demo"],
      `${path}.registry.split`,
    );
    assertStringOrNull(registry.source_label, `${path}.registry.source_label`);
    assertStringOrNull(registry.mask_path, `${path}.registry.mask_path`);
    assertEnum(
      registry.license_status,
      ["verified", "restricted", "unknown"],
      `${path}.registry.license_status`,
    );
    assertBoolean(registry.demo_allowed, `${path}.registry.demo_allowed`);
    const registryTileId = registry.tile_id;
    if (typeof registryTileId !== "string") {
      throw new Error(`${path}.registry.tile_id must be a string`);
    }

    if (exampleIds.has(registryTileId)) {
      throw new Error(`${path}.registry.tile_id is duplicated: ${registryTileId}`);
    }
    exampleIds.add(registryTileId);

    if (example.result !== undefined) {
      const result = example.result;
      if (!isRecord(result)) throw new Error(`${path}.result must be an object`);
      assertString(result.tile_id, `${path}.result.tile_id`);
      assertString(result.model, `${path}.result.model`);
      assertString(result.model_config_path, `${path}.result.model_config_path`);
      assertNumber(result.anomaly_score, `${path}.result.anomaly_score`);
      assertString(result.heatmap_path, `${path}.result.heatmap_path`);
      assertString(result.overlay_path, `${path}.result.overlay_path`);
      assertStringOrNull(result.region_tag, `${path}.result.region_tag`);
      assertStringOrNull(result.semantic_hint, `${path}.result.semantic_hint`);
      assertBoolean(result.novelty_flag, `${path}.result.novelty_flag`);
      assertEnum(result.verdict, VERDICTS, `${path}.result.verdict`);
      const resultTileId = result.tile_id;
      if (typeof resultTileId !== "string") {
        throw new Error(`${path}.result.tile_id must be a string`);
      }
      if (resultTileId !== registryTileId) {
        throw new Error(`${path}.result.tile_id must match registry.tile_id`);
      }
    }
  });

  if (!exampleIds.has(value.default_example_id as string)) {
    throw new Error("default_example_id must reference an example tile_id");
  }

  const riskMap = value.risk_map;
  if (!isRecord(riskMap)) throw new Error("risk_map must be an object");
  assertEnum(riskMap.provenance, PROVENANCE, "risk_map.provenance");
  assertString(riskMap.wafer_id, "risk_map.wafer_id");
  assertNumber(riskMap.cols, "risk_map.cols");
  assertNumber(riskMap.rows, "risk_map.rows");
  assertNumber(riskMap.threshold_review, "risk_map.threshold_review");
  assertNumber(riskMap.threshold_hold, "risk_map.threshold_hold");
  if (!Array.isArray(riskMap.tiles)) throw new Error("risk_map.tiles must be an array");
  const summary = { PASS: 0, REVIEW: 0, HOLD: 0, inspected: 0 };
  riskMap.tiles.forEach((tile, i) => {
    const path = `risk_map.tiles[${i}]`;
    if (!isRecord(tile)) throw new Error(`${path} must be an object`);
    assertString(tile.tile_id, `${path}.tile_id`);
    assertNumber(tile.col, `${path}.col`);
    assertNumber(tile.row, `${path}.row`);
    assertBoolean(tile.in_wafer, `${path}.in_wafer`);
    assertNumber(tile.anomaly_score, `${path}.anomaly_score`);
    assertEnum(tile.verdict, VERDICTS, `${path}.verdict`);
    assertBoolean(tile.has_result, `${path}.has_result`);
    const tileId = tile.tile_id;
    if (typeof tileId !== "string") {
      throw new Error(`${path}.tile_id must be a string`);
    }
    if (tile.has_result && !exampleIds.has(tileId)) {
      throw new Error(`${path}.tile_id must reference an example when has_result=true`);
    }
    if (tile.in_wafer) {
      summary.inspected += 1;
      summary[tile.verdict as Verdict] += 1;
    }
  });
  const riskSummary = riskMap.summary;
  if (!isRecord(riskSummary)) throw new Error("risk_map.summary must be an object");
  if (riskSummary.pass !== summary.PASS) {
    throw new Error(`risk_map.summary.pass must be ${summary.PASS}`);
  }
  if (riskSummary.review !== summary.REVIEW) {
    throw new Error(`risk_map.summary.review must be ${summary.REVIEW}`);
  }
  if (riskSummary.hold !== summary.HOLD) {
    throw new Error(`risk_map.summary.hold must be ${summary.HOLD}`);
  }
  if (riskSummary.inspected !== summary.inspected) {
    throw new Error(`risk_map.summary.inspected must be ${summary.inspected}`);
  }

  const metrics = value.metrics;
  if (!isRecord(metrics)) throw new Error("metrics must be an object");
  assertString(metrics.run_dir, "metrics.run_dir");
  assertString(metrics.model, "metrics.model");
  assertString(metrics.model_config_path, "metrics.model_config_path");
  assertString(metrics.dataset, "metrics.dataset");
  assertString(metrics.split, "metrics.split");
  assertNumber(metrics.k_shot, "metrics.k_shot");
  assertNumber(metrics.image_res, "metrics.image_res");
  assertString(metrics.framing, "metrics.framing");
  if (!Array.isArray(metrics.metrics)) {
    throw new Error("metrics.metrics must be an array");
  }
  metrics.metrics.forEach((metric, i) => {
    const path = `metrics.metrics[${i}]`;
    if (!isRecord(metric)) throw new Error(`${path} must be an object`);
    assertString(metric.name, `${path}.name`);
    if (metric.value !== null) assertNumber(metric.value, `${path}.value`);
    assertEnum(metric.requires, ["labels", "masks", "none"], `${path}.requires`);
    assertBoolean(metric.available, `${path}.available`);
    assertEnum(metric.format, ["auroc", "percent", "raw"], `${path}.format`);
    assertEnum(metric.evidence_class, EVIDENCE_CLASSES, `${path}.evidence_class`);
  });

  if (!Array.isArray(value.research)) throw new Error("research must be an array");
  value.research.forEach((section, i) => {
    const path = `research[${i}]`;
    if (!isRecord(section)) throw new Error(`${path} must be an object`);
    assertEnum(
      section.id,
      ["subspacead", "foundad", "domain-gap"],
      `${path}.id`,
    );
    assertString(section.title, `${path}.title`);
    assertEnum(
      section.status,
      ["executable baseline", "research headline", "open caveat"],
      `${path}.status`,
    );
    assertString(section.tagline, `${path}.tagline`);
    if (!Array.isArray(section.body) || section.body.length === 0) {
      throw new Error(`${path}.body must be a non-empty array`);
    }
    section.body.forEach((paragraph, j) => {
      assertString(paragraph, `${path}.body[${j}]`);
    });
    if (!Array.isArray(section.badges)) {
      throw new Error(`${path}.badges must be an array`);
    }
    section.badges.forEach((badge, j) => {
      assertEnum(badge, CAVEATS, `${path}.badges[${j}]`);
    });
  });
}
