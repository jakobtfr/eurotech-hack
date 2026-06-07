import type { RiskMap, RiskTile } from "@/lib/types";
import { clamp, rngFor } from "@/lib/viz/seeded-random";
import {
  DEMO_EXAMPLES,
  THRESHOLD_HOLD,
  THRESHOLD_REVIEW,
  verdictForScore,
} from "./examples";

const COLS = 24;
const ROWS = 24;
const CX = (COLS - 1) / 2;
const CY = (ROWS - 1) / 2;
const RADIUS = 11.3;

// Marked dies: the whole wafer reads as inspected, but only these cells carry a
// full result (◷ marked + clickable into Inspect). A handful are anomalies; the
// rest of the field is nominal/PASS. Each links to a real DEMO_EXAMPLE so the
// drill-in shows an actual heatmap + decision. `example` is an index into
// DEMO_EXAMPLES (a few are reused to seed extra anomaly dies).
const MARKED: { col: number; row: number; example: number }[] = [
  { col: 6, row: 6, example: 0 }, // nominal die (PASS)
  { col: 17, row: 7, example: 1 }, // nominal · field edge (PASS)
  { col: 9, row: 17, example: 4 }, // clean epi (PASS)
  { col: 15, row: 5, example: 2 }, // particle residue (REVIEW)
  { col: 18, row: 10, example: 3 }, // pattern collapse (HOLD)
  { col: 5, row: 13, example: 5 }, // BPD candidate (REVIEW)
  { col: 11, row: 19, example: 6 }, // etch-pit cluster (REVIEW)
  { col: 7, row: 9, example: 7 }, // montage · hot field (HOLD)
  { col: 13, row: 14, example: 3 }, // pattern collapse (HOLD)
  { col: 19, row: 16, example: 7 }, // montage · hot field (HOLD)
];

function markedAt(col: number, row: number) {
  const m = MARKED.find((x) => x.col === col && x.row === row);
  return m ? DEMO_EXAMPLES[m.example] : undefined;
}

function inWafer(col: number, row: number): boolean {
  const dx = col - CX;
  const dy = row - CY;
  const d = Math.sqrt(dx * dx + dy * dy);
  if (d > RADIUS) return false;
  // bottom-center flat / notch
  if (row >= ROWS - 1 && Math.abs(dx) < 2.0) return false;
  return true;
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
      const marked = present ? markedAt(col, row) : undefined;

      // Whole wafer is inspected: every in-wafer die gets a nominal PASS field
      // score; marked dies override with their real result score.
      let score = present ? clamp(noise * 0.15, 0, 0.97) : 0;
      if (marked?.result) score = marked.result.anomaly_score;

      const verdict = verdictForScore(score);
      if (present) {
        inspected++;
        if (verdict === "HOLD") hold++;
        else if (verdict === "REVIEW") review++;
        else pass++;
      }

      tiles.push({
        tile_id: marked?.registry.tile_id ?? `w12__c${col}_r${row}`,
        col,
        row,
        in_wafer: present,
        anomaly_score: score,
        verdict,
        has_result: Boolean(marked),
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
