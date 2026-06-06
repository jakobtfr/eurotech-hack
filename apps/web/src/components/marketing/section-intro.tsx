import { cn } from "@/lib/utils";

export function SectionIntro({
  index,
  eyebrow,
  title,
  className,
}: {
  index: string;
  eyebrow: string;
  title: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("max-w-2xl", className)}>
      <div className="flex items-center gap-3">
        <span className="font-mono text-sm font-medium text-primary">{index}</span>
        <span className="h-px w-8 bg-border" />
        <span className="eyebrow">{eyebrow}</span>
      </div>
      <h2 className="mt-4 font-display text-3xl font-bold leading-tight tracking-tight text-foreground sm:text-[2.5rem]">
        {title}
      </h2>
    </div>
  );
}
