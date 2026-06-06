#!/usr/bin/env node

import { readFile } from "node:fs/promises";

const VERDICTS = new Set(["PASS", "REVIEW", "HOLD"]);
const MODALITIES = new Set([
  "SEM",
  "PL",
  "etch",
  "optical",
  "wafer_map",
  "synthetic",
  "other",
]);
const EVIDENCE_CLASSES = new Set(["verified", "qualitative"]);
const CAVEATS = new Set([
  "proxy metric",
  "SiC qualitative",
  "synthetic montage",
  "restricted source",
]);

const filePath = process.argv[2] ?? "demo/manifest.json";

function isRecord(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function fail(message) {
  throw new Error(message);
}

function string(value, path) {
  if (typeof value !== "string" || value.length === 0) fail(`${path} required`);
}

function number(value, path) {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    fail(`${path} must be finite number`);
  }
}

function boolean(value, path) {
  if (typeof value !== "boolean") fail(`${path} must be boolean`);
}

function oneOf(value, set, path) {
  if (typeof value !== "string" || !set.has(value)) {
    fail(`${path} invalid: ${String(value)}`);
  }
}

function nullableString(value, path) {
  if (value !== null && typeof value !== "string") {
    fail(`${path} must be string or null`);
  }
}

function validateMetric(metric, path) {
  if (!isRecord(metric)) fail(`${path} must be object`);
  string(metric.name, `${path}.name`);
  if (metric.value !== null) number(metric.value, `${path}.value`);
  oneOf(metric.requires, new Set(["labels", "masks", "none"]), `${path}.requires`);
  boolean(metric.available, `${path}.available`);
  oneOf(metric.format, new Set(["auroc", "percent", "raw"]), `${path}.format`);
  oneOf(metric.evidence_class, EVIDENCE_CLASSES, `${path}.evidence_class`);
}

function validate(manifest) {
  if (!isRecord(manifest)) fail("manifest must be object");
  string(manifest.version, "version");
  string(manifest.generated_at, "generated_at");
  string(manifest.model, "model");
  string(manifest.default_example_id, "default_example_id");
  number(manifest.threshold_review, "threshold_review");
  number(manifest.threshold_hold, "threshold_hold");
  if (manifest.threshold_review >= manifest.threshold_hold) {
    fail("threshold_review must be below threshold_hold");
  }

  if (!Array.isArray(manifest.examples) || manifest.examples.length === 0) {
    fail("examples must be non-empty array");
  }

  const exampleIds = new Set();
  const verdicts = new Set();

  manifest.examples.forEach((example, index) => {
    const path = `examples[${index}]`;
    if (!isRecord(example)) fail(`${path} must be object`);
    string(example.title, `${path}.title`);
    string(example.caption, `${path}.caption`);
    oneOf(example.evidence_class, EVIDENCE_CLASSES, `${path}.evidence_class`);
    number(example.k_shot, `${path}.k_shot`);
    if (!Array.isArray(example.caveats)) fail(`${path}.caveats must be array`);
    example.caveats.forEach((caveat, i) =>
      oneOf(caveat, CAVEATS, `${path}.caveats[${i}]`),
    );

    const registry = example.registry;
    if (!isRecord(registry)) fail(`${path}.registry must be object`);
    string(registry.tile_id, `${path}.registry.tile_id`);
    string(registry.wafer_id, `${path}.registry.wafer_id`);
    string(registry.source_id, `${path}.registry.source_id`);
    string(registry.source_file, `${path}.registry.source_file`);
    oneOf(registry.modality, MODALITIES, `${path}.registry.modality`);
    string(registry.image_path, `${path}.registry.image_path`);
    string(registry.source_image_path, `${path}.registry.source_image_path`);
    oneOf(
      registry.split,
      new Set(["support", "validation", "test", "demo"]),
      `${path}.registry.split`,
    );
    nullableString(registry.source_label, `${path}.registry.source_label`);
    nullableString(registry.mask_path, `${path}.registry.mask_path`);
    oneOf(
      registry.license_status,
      new Set(["verified", "restricted", "unknown"]),
      `${path}.registry.license_status`,
    );
    boolean(registry.demo_allowed, `${path}.registry.demo_allowed`);
    if (exampleIds.has(registry.tile_id)) {
      fail(`${path}.registry.tile_id duplicate: ${registry.tile_id}`);
    }
    exampleIds.add(registry.tile_id);

    if (example.result !== undefined) {
      const result = example.result;
      if (!isRecord(result)) fail(`${path}.result must be object`);
      string(result.tile_id, `${path}.result.tile_id`);
      if (result.tile_id !== registry.tile_id) {
        fail(`${path}.result.tile_id must match registry tile_id`);
      }
      string(result.model, `${path}.result.model`);
      string(result.model_config_path, `${path}.result.model_config_path`);
      number(result.anomaly_score, `${path}.result.anomaly_score`);
      string(result.heatmap_path, `${path}.result.heatmap_path`);
      string(result.overlay_path, `${path}.result.overlay_path`);
      nullableString(result.region_tag, `${path}.result.region_tag`);
      nullableString(result.semantic_hint, `${path}.result.semantic_hint`);
      boolean(result.novelty_flag, `${path}.result.novelty_flag`);
      oneOf(result.verdict, VERDICTS, `${path}.result.verdict`);
      verdicts.add(result.verdict);
    }
  });

  if (!exampleIds.has(manifest.default_example_id)) {
    fail("default_example_id does not reference an example");
  }
  if (!verdicts.has("PASS") || !verdicts.has("HOLD")) {
    fail("examples must include at least PASS and HOLD verdicts");
  }

  const riskMap = manifest.risk_map;
  if (!isRecord(riskMap)) fail("risk_map must be object");
  oneOf(
    riskMap.provenance,
    new Set(["real spatial", "stitched field", "synthetic montage"]),
    "risk_map.provenance",
  );
  string(riskMap.wafer_id, "risk_map.wafer_id");
  number(riskMap.cols, "risk_map.cols");
  number(riskMap.rows, "risk_map.rows");
  if (!Array.isArray(riskMap.tiles)) fail("risk_map.tiles must be array");

  const summary = { PASS: 0, REVIEW: 0, HOLD: 0, inspected: 0 };
  riskMap.tiles.forEach((tile, index) => {
    const path = `risk_map.tiles[${index}]`;
    if (!isRecord(tile)) fail(`${path} must be object`);
    string(tile.tile_id, `${path}.tile_id`);
    number(tile.col, `${path}.col`);
    number(tile.row, `${path}.row`);
    boolean(tile.in_wafer, `${path}.in_wafer`);
    number(tile.anomaly_score, `${path}.anomaly_score`);
    oneOf(tile.verdict, VERDICTS, `${path}.verdict`);
    boolean(tile.has_result, `${path}.has_result`);
    if (tile.has_result && !exampleIds.has(tile.tile_id)) {
      fail(`${path}.tile_id has_result without example`);
    }
    if (tile.in_wafer) {
      summary.inspected += 1;
      summary[tile.verdict] += 1;
    }
  });

  if (!isRecord(riskMap.summary)) fail("risk_map.summary must be object");
  const expected = {
    pass: summary.PASS,
    review: summary.REVIEW,
    hold: summary.HOLD,
    inspected: summary.inspected,
  };
  for (const [key, value] of Object.entries(expected)) {
    if (riskMap.summary[key] !== value) {
      fail(`risk_map.summary.${key} expected ${value}, got ${riskMap.summary[key]}`);
    }
  }

  const metrics = manifest.metrics;
  if (!isRecord(metrics)) fail("metrics must be object");
  string(metrics.run_dir, "metrics.run_dir");
  string(metrics.model, "metrics.model");
  string(metrics.model_config_path, "metrics.model_config_path");
  string(metrics.dataset, "metrics.dataset");
  string(metrics.split, "metrics.split");
  number(metrics.k_shot, "metrics.k_shot");
  number(metrics.image_res, "metrics.image_res");
  string(metrics.framing, "metrics.framing");
  if (!Array.isArray(metrics.metrics)) fail("metrics.metrics must be array");
  metrics.metrics.forEach(validateMetric);

  if (!Array.isArray(manifest.research) || manifest.research.length === 0) {
    fail("research must be non-empty array");
  }
}

const raw = await readFile(filePath, "utf8");
validate(JSON.parse(raw));
console.log(`OK ${filePath}`);
