"use client";

import { EventRow, type EventState } from "@/components/EventCard";
import { groupByDay, type DayGroup, type EventItem } from "@/lib/api";

/**
 * Luma's timeline: a dotted rail down the left with a dot per day, "Today Friday"-style
 * day headers, and one translucent card per event.
 * When `splitWindow` is set, events with in_window === false go under a "Later" divider.
 */
export function EventList({
  events,
  states,
  onGoing,
  onSkip,
  splitWindow = false,
}: {
  events: EventItem[];
  states?: Record<string, EventState>;
  onGoing?: (e: EventItem) => void;
  onSkip?: (e: EventItem) => void;
  splitWindow?: boolean;
}) {
  const now = splitWindow ? events.filter((e) => e.in_window !== false) : events;
  const later = splitWindow ? events.filter((e) => e.in_window === false) : [];
  return (
    <div>
      <Days groups={groupByDay(now)} states={states} onGoing={onGoing} onSkip={onSkip} />
      {later.length > 0 && (
        <>
          <div className="mb-4 mt-6 flex items-baseline gap-3">
            <h2 className="text-lg font-semibold">Later</h2>
            <p className="text-sm text-muted-foreground">Outside the dates you asked for, still upcoming.</p>
          </div>
          <Days groups={groupByDay(later)} states={states} onGoing={onGoing} onSkip={onSkip} />
        </>
      )}
    </div>
  );
}

function dayKey(d: Date) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

/** "Today", "Tomorrow", or "Sep 15" — the bold half of Luma's day header. */
function dayLabel(key: string, month: string, day: number) {
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(today.getDate() + 1);
  if (key === dayKey(today)) return "Today";
  if (key === dayKey(tomorrow)) return "Tomorrow";
  return `${month.slice(0, 3)} ${day}`;
}

function Days({
  groups,
  states,
  onGoing,
  onSkip,
}: {
  groups: DayGroup[];
  states?: Record<string, EventState>;
  onGoing?: (e: EventItem) => void;
  onSkip?: (e: EventItem) => void;
}) {
  let index = 0; // running position across day groups, for the staggered entrance
  return (
    <>
      {groups.map((g) => (
        <section key={g.parts?.key ?? "tbd"} className="relative border-l border-dashed border-foreground/15 pb-6 pl-5 last:border-transparent sm:pl-6">
          <span className="absolute -left-[5px] top-[7px] size-[9px] rounded-full bg-foreground/25" aria-hidden />
          <h2 className="mb-3 text-base leading-6">
            {g.parts ? (
              <>
                <span className="font-semibold">{dayLabel(g.parts.key, g.parts.month, g.parts.day)}</span>{" "}
                <span className="text-muted-foreground">{g.parts.weekday}</span>
              </>
            ) : (
              <span className="font-semibold text-muted-foreground">Date to be announced</span>
            )}
          </h2>
          <ol className="space-y-3">
            {g.events.map((e) => (
              <EventRow key={e.id} event={e} state={states?.[e.id] ?? e.kind} onGoing={onGoing} onSkip={onSkip} index={index++} />
            ))}
          </ol>
        </section>
      ))}
    </>
  );
}
