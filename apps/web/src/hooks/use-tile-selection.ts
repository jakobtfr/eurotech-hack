"use client";

import { useCallback, useState } from "react";

export type WorkbenchTab = "inspect" | "risk-map" | "evidence" | "research";

export function useTileSelection(initialId: string) {
  const [selectedId, setSelectedId] = useState(initialId);
  const [tab, setTab] = useState<WorkbenchTab>("inspect");

  const inspect = useCallback((tileId: string) => {
    setSelectedId(tileId);
    setTab("inspect");
  }, []);

  return { selectedId, setSelectedId, tab, setTab, inspect };
}
