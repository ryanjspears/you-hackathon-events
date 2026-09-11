"use client";

import { EventRow } from "@/components/EventCard";
import { EventList } from "@/components/EventList";
import { Worklog } from "@/components/Worklog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { forYou, interact, siteName, streamScan, suggestions, useUser, type EventItem, type ForYou, type HistoryTurn, type ScanResult, type Suggestion } from "@/lib/api";
import { createConversation, updateTurns, useActiveId, useConversations, type Turn } from "@/lib/history";
import { ArrowUp, Loader2, Sparkles } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";

// Shown until the API answers with chips built from this user's past searches and picks (SPEC §3c).
const GENERIC: Suggestion[] = ["jazz shows in Brooklyn this weekend", "AI meetups in NYC next week", "techno parties in Manhattan Friday night"].map(
  (text) => ({ text, why: "", kind: "search" }),
);
const NO_TURNS: Turn[] = [];

function isRunning(t: Turn) {
  return t.role === "agent" && t.running;
}

/** Applies `fn` to the last turn when it is the agent's (the one being streamed into). */
function patchLast(turns: Turn[], fn: (last: Extract<Turn, { role: "agent" }>) => Turn): Turn[] {
  const last = turns[turns.length - 1];
  if (!last || last.role !== "agent") return turns;
  return [...turns.slice(0, -1), fn(last)];
}

export default function ChatPage() {
  const user = useUser();
  const router = useRouter();
  const activeId = useActiveId();
  const conversations = useConversations(user);
  const active = conversations.find((c) => c.id === activeId) ?? null;
  const turns = active?.turns ?? NO_TURNS;

  const [input, setInput] = useState("");
  const [states, setStates] = useState<Record<string, "going" | "skip">>({});
  const [sugg, setSugg] = useState<{ items: Suggestion[]; personalized: boolean } | null>(null);
  const [suggVersion, setSuggVersion] = useState(0); // bump to refetch after a search or a going mark
  const [picks, setPicks] = useState<ForYou | null>(null);
  const closer = useRef<() => void>(() => {});
  const bottom = useRef<HTMLDivElement>(null);
  const shownId = useRef<string | null>(null);

  // Switching conversations jumps to the top; new turns in the same one scroll to the bottom.
  useEffect(() => {
    if (shownId.current !== activeId) {
      shownId.current = activeId;
      window.scrollTo({ top: 0 });
      return;
    }
    if (turns.length) bottom.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [activeId, turns.length]);
  useEffect(() => () => closer.current(), []);

  // Personalized chips. The generic ones render first, so a warming or dead API never leaves a gap.
  useEffect(() => {
    if (!user) return;
    let alive = true;
    let retry: ReturnType<typeof setTimeout> | undefined;
    const load = (attempt: number) =>
      suggestions(user)
        .then((r) => {
          if (alive && r.suggestions.length) setSugg({ items: r.suggestions, personalized: r.personalized });
        })
        .catch(() => {
          if (alive && attempt === 0) retry = setTimeout(() => load(1), 3000);
        });
    load(0);
    return () => {
      alive = false;
      if (retry) clearTimeout(retry);
    };
  }, [user, suggVersion]);

  // "For you": cached ranking first; while the sandbox re-ranks (`refreshing`), poll every few seconds.
  useEffect(() => {
    if (!user) return;
    let alive = true;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let polls = 0;
    const load = () =>
      forYou(user)
        .then((r) => {
          if (!alive) return;
          setPicks(r);
          if (r.refreshing && polls++ < 20) timer = setTimeout(load, 4000);
        })
        .catch(() => {
          if (alive && polls++ < 3) timer = setTimeout(load, 3000);
        });
    load();
    return () => {
      alive = false;
      if (timer) clearTimeout(timer);
    };
  }, [user, suggVersion]);

  const running = turns.some(isRunning);
  // Only one search runs at a time server-wide (SPEC §1); a second would just queue and confuse the story.
  const busy = conversations.some((c) => c.turns.some(isRunning));

  function send(text: string) {
    const shown = text.trim();
    if (!user || !shown || busy) return;
    const id = (active ?? createConversation(user, shown)).id;
    // SPEC §1 `history`: the earlier turns go along, so "how about jazz" keeps the city from "running events in nyc"
    // and an answer to a clarifying question is combined with the request that prompted it.
    const history = historyOf(turns);
    setInput("");
    updateTurns(user, id, (t) => [...t, { role: "user", text: shown }, { role: "agent", progress: [], running: true }]);
    closer.current = streamScan(
      user,
      shown,
      (p) => updateTurns(user, id, (t) => patchLast(t, (a) => ({ ...a, progress: [...a.progress, p] }))),
      (r) => {
        updateTurns(user, id, (t) =>
          patchLast(t, (a) => ({ ...a, running: false, result: r, events: r.events, text: r.clarify ?? (r.error ? r.error : r.reply) })),
        );
        if (r.events) setSuggVersion((v) => v + 1); // the search is now in the user's history
      },
      { history },
    );
  }

  async function mark(e: EventItem, kind: "going" | "skip") {
    if (!user) return;
    setStates((s) => ({ ...s, [e.id]: kind }));
    // A pick leaves the home-page list either way (SPEC §3: going/skipped are excluded from the ranking).
    setPicks((p) => (p ? { ...p, recommendations: p.recommendations.filter((x) => x.id !== e.id) } : p));
    try {
      await interact(user, e.id, kind);
      if (kind === "going") {
        toast.success(`Going to ${e.title}. I'll remember that.`, { action: { label: "See timeline", onClick: () => router.push("/going") } });
      } else {
        toast.success("Noted, fewer like this");
      }
      setTimeout(() => setSuggVersion((v) => v + 1), 1500); // chips and picks both learn from this
    } catch (err) {
      setStates((s) => {
        const rest = { ...s };
        delete rest[e.id];
        return rest;
      });
      toast.error(String(err));
    }
  }

  const empty = turns.length === 0;
  const chips = sugg?.items.length ? sugg.items : GENERIC;

  return (
    <div className="flex min-h-[70vh] flex-col">
      <div className="flex-1 space-y-8">
        {empty && (
          <section className="pt-6 sm:pt-16">
            <div className="mb-5 flex size-12 items-center justify-center rounded-full bg-foreground/8 text-foreground/70">
              <Sparkles className="size-5" />
            </div>
            <h1 className="max-w-2xl text-[1.75rem] font-semibold leading-tight sm:text-4xl">What do you want to do, and where?</h1>
            <p className="mt-3 max-w-prose text-muted-foreground">
              Say it like you&apos;d say it to a friend. The agent searches Eventbrite, Meetup, Luma, Dice, Resident Advisor and the open web at once, then remembers what you pick.
            </p>
            <p className={`mt-6 flex items-center gap-1.5 text-xs font-medium ${sugg?.personalized ? "text-memory-text" : "text-muted-foreground"}`}>
              {sugg?.personalized && <Sparkles className="size-3" />}
              {sugg?.personalized ? "Based on what you've searched and picked" : "Try one of these"}
            </p>
            <ul className="mt-2 flex flex-wrap gap-2">
              {chips.map((s) => (
                <li key={s.text} className="motion-safe:animate-in motion-safe:fade-in motion-safe:duration-300">
                  <Button variant="secondary" size="sm" title={s.why || undefined} onClick={() => send(s.text)}>
                    {s.text}
                  </Button>
                </li>
              ))}
            </ul>
          </section>
        )}

        {empty && picks && (picks.recommendations.length > 0 || picks.refreshing) && (
          <section aria-label="For you">
            <div className="mb-1 flex items-baseline gap-3">
              <h2 className="text-lg font-semibold">For you</h2>
              {picks.refreshing && (
                <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <Loader2 className="size-3 animate-spin" /> Re-ranking in the sandbox from what you picked
                </p>
              )}
            </div>
            {picks.profile && (
              <p className="mb-4 flex items-start gap-1.5 text-sm text-memory-text">
                <Sparkles className="mt-0.5 size-3.5 shrink-0" />
                <span>The agent remembers you {picks.profile.replace(/^likes/, "like")}.</span>
              </p>
            )}
            {picks.recommendations.length > 0 ? (
              <ol className="space-y-3">
                {picks.recommendations.map((e, i) => (
                  <EventRow key={e.id} event={e} index={i} showDate state={states[e.id]} onGoing={(x) => mark(x, "going")} onSkip={(x) => mark(x, "skip")} />
                ))}
              </ol>
            ) : (
              <div className="space-y-3">
                {[0, 1, 2, 3].map((k) => (
                  <Skeleton key={k} className="h-24 rounded-3xl bg-foreground/5" />
                ))}
              </div>
            )}
          </section>
        )}

        {turns.map((t, i) =>
          t.role === "user" ? (
            <div key={i} className="flex justify-end">
              <p className="max-w-[85%] rounded-2xl bg-foreground/8 px-4 py-2.5">{t.text}</p>
            </div>
          ) : (
            <div key={i} className="space-y-4">
              <Worklog items={t.progress} running={t.running} />
              {t.text && (
                <p className={`max-w-prose text-base leading-relaxed ${t.result?.error ? "text-destructive" : ""}`}>
                  {t.text}
                  {t.result?.error && (
                    <>
                      {" "}
                      <button type="button" className="underline underline-offset-4" onClick={() => retry(turns, i, send)}>
                        Try again
                      </button>
                    </>
                  )}
                </p>
              )}
              {t.running && (
                <div className="space-y-3 pt-2">
                  {[0, 1, 2].map((k) => (
                    <Skeleton key={k} className="h-24 rounded-3xl bg-foreground/5" />
                  ))}
                </div>
              )}
              {t.events && t.events.length > 0 && (
                <div>
                  <ResultSummary r={t.result} count={t.events.length} />
                  <EventList events={t.events} states={states} onGoing={(e) => mark(e, "going")} onSkip={(e) => mark(e, "skip")} splitWindow />
                </div>
              )}
            </div>
          ),
        )}
        <div ref={bottom} />
      </div>

      <form
        className="sticky bottom-4 mt-10 rounded-2xl border border-border bg-card p-2 shadow-[0_8px_30px_rgba(0,0,0,0.12)] dark:shadow-[0_8px_30px_rgba(0,0,0,0.45)]"
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
      >
        <div className="flex items-center gap-2">
          <Input
            className="h-11 border-0 bg-transparent px-3 text-base shadow-none focus-visible:ring-0 dark:bg-transparent"
            placeholder={busy && !running ? "Another search is still running" : empty ? "jazz in Brooklyn this weekend" : "Ask for something else"}
            aria-label="What do you want to do, and where?"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={busy}
          />
          <Button type="submit" size="icon" aria-label="Search" disabled={busy || !input.trim()} className="size-10">
            {running ? <Loader2 className="size-4 animate-spin" /> : <ArrowUp className="size-4" />}
          </Button>
        </div>
      </form>
    </div>
  );
}

/** The conversation so far as Planner context: what the user said and what was actually searched. */
function historyOf(turns: Turn[]): HistoryTurn[] {
  const out: HistoryTurn[] = [];
  for (const t of turns) {
    if (t.role === "user") out.push({ role: "user", text: t.text });
    else if (t.result?.plan && !t.result.error) out.push({ role: "agent", plan: t.result.plan, ...(t.result.clarify ? { clarify: t.result.clarify } : {}) });
  }
  return out;
}

function retry(turns: Turn[], agentIndex: number, send: (text: string) => void) {
  const prev = turns[agentIndex - 1];
  if (prev?.role === "user") send(prev.text);
}

function ResultSummary({ r, count }: { r?: ScanResult; count: number }) {
  if (!r) return null;
  const dropped = r.dropped ? Object.values(r.dropped).reduce((a, b) => a + b, 0) : 0;
  const sources = r.plan?.sources ?? [];
  const fromSource = (r.events ?? []).filter((e) => e.from_source).length;
  const names = sources.map(siteName).join(", ");
  const bits = [
    `${count} events`,
    sources.length ? (fromSource ? `${names} first (${fromSource})` : `nothing matching on ${names}`) : null,
    r.hits ? `from ${r.hits} search results` : null,
    r.pages ? `and ${r.pages} listing pages` : null,
    dropped ? `${dropped} filtered out as past, undated or duplicate` : null,
  ].filter(Boolean);
  return <p className="mb-4 text-sm text-muted-foreground">{bits.join(", ")}.</p>;
}
