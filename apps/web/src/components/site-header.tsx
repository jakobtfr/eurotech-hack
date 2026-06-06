"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/", label: "Overview" },
  { href: "/demo", label: "Guided Demo" },
  { href: "/workbench", label: "Workbench" },
] as const;

function WaferMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={className} fill="none" aria-hidden>
      <circle cx="16" cy="16" r="12.5" stroke="currentColor" strokeWidth="1.4" opacity="0.85" />
      <circle cx="16" cy="16" r="7.5" stroke="currentColor" strokeWidth="1" opacity="0.4" />
      <path
        d="M16 3.5 L16 6.5 M16 25.5 L16 28.5 M3.5 16 L6.5 16 M25.5 16 L28.5 16"
        stroke="currentColor"
        strokeWidth="1"
        opacity="0.55"
      />
      <circle cx="16" cy="16" r="2.6" fill="var(--primary)" />
      <path d="M13.5 28 L16 25.7 L18.5 28" stroke="currentColor" strokeWidth="1.1" opacity="0.6" />
    </svg>
  );
}

export function SiteHeader() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/85 backdrop-blur-md">
      <div className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between gap-4 px-6">
        <Link href="/" className="group flex items-center gap-2.5">
          <span className="text-foreground">
            <WaferMark className="size-7" />
          </span>
          <span className="flex items-baseline gap-2">
            <span className="font-display text-[1.05rem] font-bold tracking-[0.04em] text-foreground">
              SUBSTRATE
            </span>
            <span className="hidden font-mono text-[0.6rem] uppercase tracking-[0.2em] text-muted-foreground sm:inline">
              SiC workbench
            </span>
          </span>
        </Link>

        <nav className="hidden items-center gap-7 md:flex">
          {NAV.map((item) => {
            const active =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "relative py-1 text-[0.82rem] transition-colors",
                  active
                    ? "text-foreground"
                    : "text-muted-foreground hover:text-foreground",
                )}
              >
                {item.label}
                {active && (
                  <span className="absolute -bottom-px left-0 h-px w-full bg-primary" />
                )}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-2 font-mono text-[0.68rem] text-muted-foreground">
          <span className="size-1.5 rounded-full bg-verdict-pass" />
          <span className="hidden sm:inline">
            model <span className="text-foreground">subspacead</span>
          </span>
        </div>
      </div>
    </header>
  );
}
