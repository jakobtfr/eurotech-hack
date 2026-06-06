import { access, readFile } from "node:fs/promises";
import path from "node:path";
import { demoManifest as fallbackManifest } from "@/lib/mock/manifest";
import type { DemoManifest } from "@/lib/types";
import { assertDemoManifest } from "./manifest-validation";

async function exists(filePath: string): Promise<boolean> {
  try {
    await access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function findRepoRoot(start: string): Promise<string> {
  let dir = start;
  while (true) {
    if (await exists(path.join(dir, "pnpm-workspace.yaml"))) return dir;
    const parent = path.dirname(dir);
    if (parent === dir) return start;
    dir = parent;
  }
}

async function defaultManifestPath() {
  const root = await findRepoRoot(process.cwd());
  return path.join(root, "demo", "manifest.json");
}

export async function loadDemoManifest(): Promise<DemoManifest> {
  const manifestPath = process.env.DEMO_MANIFEST_PATH
    ? path.resolve(process.env.DEMO_MANIFEST_PATH)
    : await defaultManifestPath();

  if (!(await exists(manifestPath))) {
    assertDemoManifest(fallbackManifest);
    return fallbackManifest;
  }

  const raw = await readFile(manifestPath, "utf8");
  const parsed: unknown = JSON.parse(raw);
  assertDemoManifest(parsed);
  return parsed;
}
