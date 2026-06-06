import { cn } from "@/lib/utils";
import { VERDICT_META } from "@/lib/mock/selectors";
import type { Verdict } from "@/lib/types";

const TONE: Record<string, string> = {
  pass: "var(--verdict-pass)",
  review: "var(--verdict-review)",
  reject: "var(--verdict-reject)",
};

export function VerdictRuleLegend({
  active,
  className,
}: {
  active?: Verdict;
  className?: string;
}) {
  return (
    <ul className={cn("flex flex-col gap-1.5", className)}>
      {(Object.keys(VERDICT_META) as Verdict[]).map((v) => {
        const meta = VERDICT_META[v];
        const isActive = active === v;
        return (
          <li
            key={v}
            className={cn(
              "flex items-start gap-2 rounded-md px-2 py-1.5 text-[0.72rem] transition-colors",
              isActive ? "bg-muted/60" : "opacity-65",
            )}
          >
            <span
              className="mt-1 size-2 shrink-0 rounded-full"
              style={{
                background: TONE[meta.tone],
                boxShadow: isActive ? `0 0 8px ${TONE[meta.tone]}` : undefined,
              }}
            />
            <span>
              <span
                className="font-mono font-semibold uppercase tracking-wider"
                style={{ color: TONE[meta.tone] }}
              >
                {v}
              </span>
              <span className="text-muted-foreground"> — {meta.blurb}</span>
            </span>
          </li>
        );
      })}
    </ul>
  );
}
