import type { RiskMap, RiskTile } from "@/lib/types";
import { clamp, rngFor } from "@/lib/viz/seeded-random";
import {
  DEMO_EXAMPLES,
  THRESHOLD_HOLD,
  THRESHOLD_REVIEW,
  verdictForScore,
} from "./examples";

const COLS = 14;
const ROWS = 14;
const CX = (COLS - 1) / 2;
const CY = (ROWS - 1) / 2;
const RADIUS = 6.7;

// Deterministic anomaly hot-spots across the wafer field.
const HOT_SPOTS = [
  { cx: 10, cy: 3.5, amp: 0.96, sigma: 1.7 }, // hold cluster
  { cx: 3.5, cy: 9, amp: 0.58, sigma: 1.9 }, // review cluster
  { cx: 8.6, cy: 10, amp: 0.36, sigma: 1.5 }, // minor warm
];

// Map specific grid cells to demo examples so the map drills into Inspect.
const LINKS: Record<string, string> = {
  "10:3": DEMO_EXAMPLES[3].registry.tile_id, // pattern collapse (HOLD)
  "4:9": DEMO_EXAMPLES[2].registry.tile_id, // particle residue (REVIEW)
  "3:3": DEMO_EXAMPLES[0].registry.tile_id, // nominal die (PASS)
  "11:11": DEMO_EXAMPLES[1].registry.tile_id, // nominal edge (PASS)
};

function inWafer(col: number, row: number): boolean {
  const dx = col - CX;
  const dy = row - CY;
  const d = Math.sqrt(dx * dx + dy * dy);
  if (d > RADIUS) return false;
  // bottom-center flat / notch
  if (row >= ROWS - 1 && Math.abs(dx) < 1.4) return false;
  return true;
}

function fieldScore(col: number, row: number, noise: number): number {
  let s = noise * 0.16;
  for (const spot of HOT_SPOTS) {
    const dx = col - spot.cx;
    const dy = row - spot.cy;
    const d2 = dx * dx + dy * dy;
    s += spot.amp * Math.exp(-d2 / (2 * spot.sigma * spot.sigma));
  }
  return clamp(s, 0, 0.97);
}

function buildRiskMap(): RiskMap {
  const rng = rngFor("wafer-risk-map", "MIIC-lot7-w12");
  const tiles: RiskTile[] = [];
  let pass = 0;
  let review = 0;
  let hold = 0;
  let inspected = 0;

  for (let row = 0; row < ROWS; row++) {
    for (let col = 0; col < COLS; col++) {
      const noise = rng();
      const present = inWafer(col, row);
      const key = `${col}:${row}`;
      const linkId = LINKS[key];
      const linked = linkId
        ? DEMO_EXAMPLES.find((e) => e.registry.tile_id === linkId)
        : undefined;

      let score = present ? fieldScore(col, row, noise) : 0;
      if (linked?.result) score = linked.result.anomaly_score;

      const verdict = verdictForScore(score);
      if (present) {
        inspected++;
        if (verdict === "HOLD") hold++;
        else if (verdict === "REVIEW") review++;
        else pass++;
      }

      tiles.push({
        tile_id: linkId ?? `w12__c${col}_r${row}`,
        col,
        row,
        in_wafer: present,
        anomaly_score: score,
        verdict,
        has_result: Boolean(linked),
      });
    }
  }

  return {
    provenance: "stitched field",
    wafer_id: "MIIC-lot7-w12",
    cols: COLS,
    rows: ROWS,
    threshold_review: THRESHOLD_REVIEW,
    threshold_hold: THRESHOLD_HOLD,
    tiles,
    summary: { pass, review, hold, inspected },
  };
}

export const RISK_MAP: RiskMap = buildRiskMap();
