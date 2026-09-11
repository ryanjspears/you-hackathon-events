"use client";

import { siteName, type Progress } from "@/lib/api";
import { Brain, ChevronDown, Wrench } from "lucide-react";
import { useState } from "react";

const STAGE_LABEL: Record<string, string> = {
  recalled: "Memory",
  plan: "Plan",
  crew: "Crew",
  search: "You.com",
  extract: "Extract",
  scan: "scan.py",
  sandbox: "Daytona",
  task: "Agent",
  learned: "Memory",
  recommend: "Rank",
  mem: "Memory",
  trace: "Timing",
};

function isRepair(p: Progress) {
  return p.stage === "sandbox" && /repair/i.test(p.text ?? "");
}

/** The one-line status shown while the agent runs: a friendly phrase for the raw progress line, or null to keep the previous one. */
function friendly(p: Progress): string | null {
  const t = (p.text ?? "").replace(/^\+[\d.]+s /, ""); // scan.py lines are prefixed with their elapsed time
  let m: RegExpMatchArray | null;
  switch (p.stage) {
    case "recalled": return "Remembering what you like";
    case "plan": return "Working out what to look for";
    case "crew": return "Getting the crew together";
    case "learned": return "Remembering this search for next time";
    case "recommend": return "Ranking events for you";
    case "task": return /curator/i.test(t) ? "Writing up the picks" : "Handing the events to the curator";
    case "sandbox":
      if (/creating/i.test(t)) return "Spinning up a sandbox";
      if (/ready/i.test(t)) return "Sandbox ready";
      if ((m = t.match(/^attempt (\d+)/))) return m[1] === "1" ? "Starting the scan" : "Running the fixed script";
      if (/running in Daytona/i.test(t)) return null; // heartbeat: keep the more specific scan line
      if ((m = t.match(/exit 0 — (\d+)/))) return `Found ${m[1]} events, tidying up`;
      if (/repair/i.test(t)) return "Hit a bug, fixing my own script";
      if (/poll error|failed/i.test(t)) return "Reconnecting to the sandbox";
      return null;
    case "scan":
      if (/^web: /.test(t)) return "Searching the web";
      if ((m = t.match(/^([a-z0-9.-]+): \d+ results/))) return `Searching ${siteName(m[1])}${/\(priority\)$/.test(t) ? " first" : ""}`;
      if (/^search took/.test(t)) return "Picking the best listing pages";
      if (/contents|listing pages read/.test(t)) return "Reading the listing pages";
      if ((m = t.match(/^page ([^:]+): \d+ candidates/))) return `Pulling events from ${m[1]}`;
      if (/^search snippets:/.test(t)) return "Pulling events from search results";
      if (/^(extract|normalize) took/.test(t)) return "Cleaning up dates and duplicates";
      return null;
    default:
      return null;
  }
}

/**
 * What the agent is doing right now, in one line, plus the lines worth keeping
 * (what it recalled, what it learned, when it repaired its own script) and a
 * collapsible full log for anyone who wants to see the work.
 */
export function Worklog({ items, running }: { items: Progress[]; running: boolean }) {
  const [open, setOpen] = useState(false);
  const lines = items.filter((p) => p.stage !== "ping");
  if (lines.length === 0 && !running) return null;

  const status = [...lines].reverse().map(friendly).find((s) => s !== null) ?? "Starting";
  const steps = lines.filter((p) => p.stage !== "trace").length;
  const first = lines[0]?.t, last = lines[lines.length - 1]?.t;
  const secs = first && last ? Math.max(0, Math.round(last - first)) : null;
  const repairs = lines.filter(isRepair).length;
  // the server's end-of-request timing summary ("total 81.2s · sandbox.run 62.0s, llm.call 12.1s, …")
  const timing = [...lines].reverse().find((p) => p.stage === "trace" && p.summary);

  return (
    <div className="space-y-2">
      <div className="flex min-h-7 flex-wrap items-center gap-x-3 gap-y-1 text-sm">
        {running ? (
          // fixed-size box so the row doesn't reflow every time the phrase changes
          <span className="inline-flex h-7 w-80 max-w-full shrink-0 items-center gap-2 text-foreground" role="status" aria-live="polite">
            <span className="inline-flex size-3 shrink-0 animate-pulse rounded-full bg-muted-foreground/40 blur-[1.5px]" aria-hidden />
            {/* key on the text so each new phrase restarts the sweep */}
            <span key={status} className="shimmer-text min-w-0 truncate" title={status}>
              {status}…
            </span>
          </span>
        ) : (
          <span className="text-muted-foreground">
            {secs !== null ? `Finished in ${secs}s` : "Finished"}
            {timing?.text && <span className="ml-2 tnum text-xs">{timing.text.replace(/^total [\d.]+s · /, "")}</span>}
            {repairs > 0 && (
              <span className="ml-2 inline-flex items-center gap-1 rounded-md bg-brand/15 px-1.5 py-0.5 text-xs font-medium text-brand-text">
                <Wrench className="size-3" /> Repaired its own script {repairs > 1 ? `${repairs} times` : "once"}
              </span>
            )}
          </span>
        )}
        {lines.length > 0 && (
          <button
            type="button"
            onClick={() => setOpen((o) => !o)}
            className="inline-flex items-center gap-1 rounded-full bg-foreground/8 px-2.5 py-1 text-xs font-medium text-foreground/65 transition-colors hover:bg-foreground/[0.14] hover:text-foreground"
            aria-expanded={open}
          >
            {open ? "Hide the work" : `Show the work (${steps} steps)`}
            <ChevronDown className={`size-3.5 transition-transform ${open ? "rotate-180" : ""}`} />
          </button>
        )}
      </div>

      {open && (
        <ol className="lux-card max-h-72 overflow-y-auto rounded-2xl p-3 text-xs">
          {lines.map((p, i) => {
            const repair = isRepair(p);
            const mem = p.stage === "recalled" || p.stage === "learned";
            return (
              <li key={i} className={`grid grid-cols-[4.5rem_1fr] gap-2 px-1 py-0.5 ${repair ? "text-brand-text" : ""}`}>
                <span className="tnum inline-flex items-center gap-1 text-muted-foreground">
                  {mem && <Brain className="size-3.5 shrink-0" aria-label="memory used" />}
                  {STAGE_LABEL[p.stage] ?? p.stage}
                </span>
                <span className="min-w-0 break-words">
                  {p.stage === "plan" && p.plan ? describePlan(p.plan) : p.text}
                  {p.stderr && <pre className="mt-1 max-h-32 overflow-auto rounded-sm bg-background p-2 font-mono text-[11px] leading-snug text-muted-foreground">{p.stderr}</pre>}
                </span>
              </li>
            );
          })}
        </ol>
      )}
    </div>
  );
}

function describePlan(plan: NonNullable<Progress["plan"]>) {
  const what = [...(plan.categories ?? []), plan.keywords].filter(Boolean).join(", ") || "anything";
  const when = plan.date_window ?? (plan.date_from && plan.date_to ? `${plan.date_from} to ${plan.date_to}` : "any time");
  const first = plan.sources?.length ? `, ${plan.sources.map(siteName).join(", ")} first` : "";
  return `Looking for ${what} in ${plan.city ?? "an unknown city"}, ${when}${first}`;
}
