import { SiteHeader } from "@/components/site-header";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const TABS = [
  {
    value: "inspect",
    label: "Inspect",
    title: "Inspect",
    description:
      "Raw image, heatmap overlay, contours/ROI, anomaly score, novelty flag, and verdict for a selected tile.",
    todo: [
      "Example selector with modality/source tags",
      "Raw image + heatmap overlay viewer",
      "Score, verdict (PASS / REVIEW / REJECT), caveat badge",
    ],
  },
  {
    value: "risk-map",
    label: "Risk Map",
    title: "Risk Map",
    description:
      "Tile-grid or wafer-style risk map built from per-tile scores, labeled by provenance.",
    todo: [
      "Tile-grid heat overlay",
      "Provenance label: real spatial / stitched / synthetic montage",
    ],
  },
  {
    value: "evidence",
    label: "Evidence",
    title: "Evidence",
    description:
      "Metrics table with split/config labels and run directory — no metric shown without provenance.",
    todo: [
      "Image AUROC/AUPR (requires labels)",
      "Pixel AUROC/PRO (requires masks)",
      "metrics_manifest.json: valid vs invalid metrics",
    ],
  },
  {
    value: "research",
    label: "Research",
    title: "Research",
    description:
      "Why SubspaceAD is the executable baseline, optional FoundAD result/blocker, and the domain-gap caveat.",
    todo: [
      "SubspaceAD path summary",
      "FoundAD status (optional comparison or documented blocker)",
      "Proxy-vs-SiC domain-gap note",
    ],
  },
] as const;

export default function Home() {
  return (
    <>
      <SiteHeader />
      <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-8">
        <Tabs defaultValue="inspect" className="gap-6">
          <TabsList>
            {TABS.map((t) => (
              <TabsTrigger key={t.value} value={t.value}>
                {t.label}
              </TabsTrigger>
            ))}
          </TabsList>

          {TABS.map((t) => (
            <TabsContent key={t.value} value={t.value}>
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    {t.title}
                    <Badge variant="secondary">placeholder</Badge>
                  </CardTitle>
                  <CardDescription>{t.description}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-sm font-medium text-muted-foreground">
                    Planned for this tab
                  </p>
                  <Separator />
                  <ul className="space-y-2 text-sm">
                    {t.todo.map((item) => (
                      <li key={item} className="flex items-start gap-2">
                        <span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-muted-foreground" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </TabsContent>
          ))}
        </Tabs>
      </main>
      <footer className="border-t">
        <div className="mx-auto max-w-6xl px-6 py-4 text-xs text-muted-foreground">
          Scaffold · Next.js + shadcn/ui · backend (apps/api) added later
        </div>
      </footer>
    </>
  );
}
