"use client";

import { EventList } from "@/components/EventList";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { dayParts, going, interact, useUser, type EventItem } from "@/lib/api";
import { CalendarCheck } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { toast } from "sonner";

function todayKey() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

/**
 * The user's own timeline: every event they said "I'm going" to, soonest first, on the same
 * day rail as search results. Past events sink to a muted section underneath.
 */
export default function GoingPage() {
  const user = useUser();
  const [events, setEvents] = useState<EventItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0); // bumped by "Try again"

  useEffect(() => {
    if (!user) return;
    let alive = true;
    going(user)
      .then((r) => {
        if (!alive) return;
        setEvents(r.going);
        setError(null);
      })
      .catch((err) => {
        if (alive) setError(String(err));
      });
    return () => {
      alive = false;
    };
  }, [user, attempt]);

  // Changing your mind here removes the event from the timeline (the latest interaction wins, SPEC §2).
  async function skip(e: EventItem) {
    if (!user) return;
    const before = events;
    setEvents((list) => list?.filter((x) => x.id !== e.id) ?? null);
    try {
      await interact(user, e.id, "skip");
      toast.success(`Removed ${e.title} from your timeline`);
    } catch (err) {
      setEvents(before);
      toast.error(String(err));
    }
  }

  const today = todayKey();
  const upcoming = events?.filter((e) => (dayParts(e.start)?.key ?? "9999") >= today) ?? [];
  const past = events?.filter((e) => (dayParts(e.start)?.key ?? "9999") < today) ?? [];

  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-[1.75rem] font-semibold leading-tight sm:text-3xl">You&apos;re going to</h1>
        <p className="mt-2 max-w-prose text-muted-foreground">
          {events === null
            ? "Loading your timeline."
            : events.length === 0
              ? "Nothing yet. Mark an event as I'm going from a search and it will show up here, in order."
              : `${upcoming.length} upcoming${past.length ? `, ${past.length} past` : ""}. The agent uses these to rank what it shows you next.`}
        </p>
      </section>

      {error && (
        <p role="alert" className="text-sm text-destructive">
          {error}{" "}
          <button type="button" className="underline underline-offset-4" onClick={() => setAttempt((n) => n + 1)}>
            Try again
          </button>
        </p>
      )}

      {events === null && !error && (
        <div className="space-y-3">
          {[0, 1, 2].map((k) => (
            <Skeleton key={k} className="h-24 rounded-3xl bg-foreground/5" />
          ))}
        </div>
      )}

      {events !== null && events.length === 0 && (
        <div className="lux-card flex flex-col items-start gap-4 rounded-3xl p-6">
          <div className="flex size-10 items-center justify-center rounded-full bg-foreground/8 text-foreground/70">
            <CalendarCheck className="size-5" />
          </div>
          <p className="max-w-prose text-sm text-muted-foreground">
            Your timeline fills up as you pick events. Each pick is also remembered, so the next search is already ranked around what you like.
          </p>
          <Button render={<Link href="/" />} size="sm">
            Find something to go to
          </Button>
        </div>
      )}

      {upcoming.length > 0 && <EventList events={upcoming} onSkip={skip} />}

      {past.length > 0 && (
        <section className="opacity-60">
          <div className="mb-4 flex items-baseline gap-3">
            <h2 className="text-lg font-semibold">Past</h2>
            <p className="text-sm text-muted-foreground">Already happened. Still counts toward what the agent learns.</p>
          </div>
          <EventList events={past} />
        </section>
      )}
    </div>
  );
}
