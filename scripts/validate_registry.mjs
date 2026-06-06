#!/usr/bin/env node

import { access, readFile } from "node:fs/promises";
import path from "node:path";

const MODALITIES = new Set([
  "SEM",
  "PL",
  "etch",
  "optical",
  "wafer_map",
  "synthetic",
  "other",
]);
const LICENSE = new Set(["verified", "restricted", "unknown"]);

const args = process.argv.slice(2);
const checkFiles = args.includes("--check-files");
const filePath = args.find((arg) => arg !== "--check-files") ?? "data/registry/sources.example.jsonl";
const root = process.cwd();

function isRecord(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function fail(line, message) {
  throw new Error(`line ${line}: ${message}`);
}

function string(row, key, line) {
  if (typeof row[key] !== "string" || row[key].length === 0) {
    fail(line, `${key} required`);
  }
}

function nullableString(row, key, line) {
  if (row[key] !== null && typeof row[key] !== "string") {
    fail(line, `${key} must be string or null`);
  }
}

async function assertPathExists(relativePath, line, key) {
  if (relativePath === null) return;
  const fullPath = path.resolve(root, relativePath);
  try {
    await access(fullPath);
  } catch {
    fail(line, `${key} does not exist: ${relativePath}`);
  }
}

const raw = await readFile(filePath, "utf8");
const seen = new Set();
let count = 0;

for (const [index, line] of raw.split(/\r?\n/).entries()) {
  const lineNumber = index + 1;
  if (line.trim().length === 0) continue;
  const row = JSON.parse(line);
  if (!isRecord(row)) fail(lineNumber, "row must be object");

  string(row, "schema_version", lineNumber);
  string(row, "source_image_id", lineNumber);
  string(row, "dataset_id", lineNumber);
  nullableString(row, "wafer_id", lineNumber);
  string(row, "source_path", lineNumber);
  if (!MODALITIES.has(row.modality)) fail(lineNumber, "invalid modality");
  nullableString(row, "source_label", lineNumber);
  nullableString(row, "mask_source_path", lineNumber);
  if (!LICENSE.has(row.license_status)) fail(lineNumber, "invalid license_status");
  string(row, "license_reference", lineNumber);
  if (typeof row.demo_allowed !== "boolean") fail(lineNumber, "demo_allowed must be boolean");
  if (typeof row.notes !== "string") fail(lineNumber, "notes must be string");

  if (seen.has(row.source_image_id)) {
    fail(lineNumber, `duplicate source_image_id: ${row.source_image_id}`);
  }
  seen.add(row.source_image_id);

  if (checkFiles) {
    await assertPathExists(row.source_path, lineNumber, "source_path");
    await assertPathExists(row.mask_source_path, lineNumber, "mask_source_path");
    await assertPathExists(row.license_reference, lineNumber, "license_reference");
  }

  count += 1;
}

if (count === 0) throw new Error(`${filePath} contains no registry rows`);
console.log(`OK ${filePath} (${count} rows${checkFiles ? ", files checked" : ""})`);
