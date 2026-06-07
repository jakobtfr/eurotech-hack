import type { SourceRegistryRow } from "@/lib/types";

/** Pretty ground-truth label from the raw source_label. */
function prettyLabel(label: string | null): string {
  if (!label) return "Unlabeled";
  const s = label.toLowerCase();
  if (s.includes("anom") || s.includes("abnormal")) return "Anomaly";
  if (s.includes("normal")) return "Normal";
  if (s === "unknown") return "Unknown";
  return label[0].toUpperCase() + label.slice(1);
}

/** Friendly dataset name from the wafer_id (e.g. "miic-partial-recovered" → "MIIC partial"). */
function prettyDataset(waferId: string): string {
  return waferId
    .replace(/-recovered$/i, "")
    .replace(/-/g, " ")
    .replace(/\bmiic\b/i, "MIIC")
    .trim();
}

/**
 * Human-readable tile name derived purely from real registry fields — no
 * hand-authored marketing copy.
 *   primary:   "Anomaly · #00022"
 *   secondary: "test split · MIIC partial"
 */
export function tileDisplayName(registry: SourceRegistryRow): {
  primary: string;
  secondary: string;
} {
  const label = prettyLabel(registry.source_label);
  const index = registry.source_file.match(/(\d+)(?=\D*$)/)?.[1] ?? null;
  return {
    primary: index ? `${label} · #${index}` : label,
    secondary: `${registry.split} split · ${prettyDataset(registry.wafer_id)}`,
  };
}
