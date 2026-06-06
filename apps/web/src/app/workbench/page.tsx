import type { Metadata } from "next";
import { WorkbenchShell } from "@/components/workbench/workbench-shell";
import { loadDemoManifest } from "@/lib/demo-manifest";

export const metadata: Metadata = {
  title: "Workbench — SUBSTRATE",
  description:
    "Inspect tiles, risk maps, and proxy-validated evidence in the SiC anomaly workbench.",
};

export default async function WorkbenchPage() {
  const manifest = await loadDemoManifest();
  return <WorkbenchShell manifest={manifest} />;
}
