import type { Metadata } from "next";
import { DemoRunner } from "@/components/demo/demo-runner";

export const metadata: Metadata = {
  title: "Guided Demo — SUBSTRATE",
  description:
    "A scripted four-minute walk through the SiC anomaly workbench: risk map, inspection, evidence, and honest framing.",
};

export default function DemoPage() {
  return <DemoRunner />;
}
