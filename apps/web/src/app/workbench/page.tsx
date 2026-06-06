import type { Metadata } from "next";
import { WorkbenchShell } from "@/components/workbench/workbench-shell";

export const metadata: Metadata = {
  title: "Workbench — SUBSTRATE",
  description:
    "Inspect tiles, risk maps, and proxy-validated evidence in the SiC anomaly workbench.",
};

export default function WorkbenchPage() {
  return <WorkbenchShell />;
}
