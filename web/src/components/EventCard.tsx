"use client";

import { Button, buttonVariants } from "@/components/ui/button";
import { API, fmtDate, platformHue, timeOf, type EventItem } from "@/lib/api";
import { ArrowUpRight, Check, Globe, MapPin, Sparkles } from "lucide-react";
import { useState } from "react";

export type EventState = "going" | "skip" | undefined;

/**
 * A Luma-style event card: time on top in gray, bold title, "By <source>" and a
 * location line with small line icons, then pills for price and tags. Actions sit
 * to the right on wide screens and drop below on phones.
 */
export function EventRow({
  event,
  onGoing,
  onSkip,
  state,
  index = 0,
  showDate = false,
}: {
  event: EventItem;
  onGoing?: (e: EventItem) => void;
  onSkip?: (e: EventItem) => void;
  state?: EventState;
  /** Position in the list: cards fade and rise in one after another (capped so long lists don't wait). */
  index?: number;
  /** Show "Sat 13 Sep, 7:30 PM" instead of the bare time, for lists that have no day header. */
  showDate?: boolean;
}) {
  const time = showDate ? fmtDate(event.start) : timeOf(event.start);
  const where = [event.venue, event.city].filter(Boolean).join(", ");
  const going = state === "going";
  const skipped = state === "skip";

  return (
    <li
      className={`lux-card lux-card-hover flex flex-col gap-3 rounded-3xl p-4 transition-colors sm:flex-row sm:items-start sm:gap-5 sm:pl-5 motion-safe:animate-in motion-safe:fade-in motion-safe:slide-in-from-bottom-3 motion-safe:fill-mode-backwards motion-safe:duration-500 motion-safe:ease-out ${skipped ? "opacity-40" : ""}`}
      style={{ animationDelay: `${Math.min(index, 10) * 60}ms` }}
      aria-label={event.title}
    >
      <div className="min-w-0 flex-1 space-y-1.5">
        <p className="flex items-center gap-2 text-sm text-muted-foreground">
          {going && <span className="size-1.5 rounded-full bg-brand" aria-hidden />}
          {going && <span className="font-medium text-brand-text">Going</span>}
          <span className="tnum">{time ?? "All day"}</span>
        </p>

        <h3 className="text-[1.0625rem] font-semibold leading-snug">
          {event.url ? (
            <a href={event.url} target="_blank" rel="noreferrer" className="hover:text-foreground/80">
              {event.title}
            </a>
          ) : (
            event.title
          )}
        </h3>

        {event.reason && (
          <p className="flex items-start gap-1.5 text-sm text-memory-text">
            <Sparkles className="mt-0.5 size-3.5 shrink-0" />
            <span>{event.reason}</span>
          </p>
        )}
        {event.platform && (
          <p className="flex items-center gap-1.5 text-sm text-muted-foreground">
            <Favicon url={event.url} />
            <span className="truncate">By {event.platform}</span>
            {event.from_source && (
              <span className="shrink-0 text-xs text-brand-text" title="The site you asked for">
                · as asked
              </span>
            )}
          </p>
        )}
        {where && (
          <p className="flex items-center gap-1.5 text-sm text-muted-foreground">
            <MapPin className="size-3.5 shrink-0" />
            <span className="truncate">{where}</span>
          </p>
        )}
        {event.summary && <p className="line-clamp-2 max-w-prose text-sm text-muted-foreground">{event.summary}</p>}

        {(event.price || event.tags?.length) && (
          <div className="flex flex-wrap items-center gap-1.5 pt-1">
            {event.price && <Pill tone="green">{event.price}</Pill>}
            {event.tags?.slice(0, 4).map((t) => (
              <Pill key={t}>{t}</Pill>
            ))}
          </div>
        )}
      </div>

      <div className="flex shrink-0 items-center gap-1.5 sm:flex-col sm:items-end">
        <div className="flex items-center gap-1.5">
          {event.url && (
            <a
              href={event.url}
              target="_blank"
              rel="noreferrer"
              aria-label={`Open ${event.title} listing`}
              className={buttonVariants({ size: "icon-sm", variant: "secondary" })}
            >
              <ArrowUpRight className="size-4" />
            </a>
          )}
          {onSkip && (
            <Button size="sm" variant="secondary" onClick={() => onSkip(event)} disabled={skipped}>
              Not for me
            </Button>
          )}
          {onGoing && (
            <Button size="sm" variant={going ? "brand" : "default"} onClick={() => onGoing(event)} disabled={going} className="disabled:opacity-100">
              {going ? (
                <>
                  <Check className="size-3.5" /> Going
                </>
              ) : (
                "I'm going"
              )}
            </Button>
          )}
        </div>
      </div>
    </li>
  );
}

/** The provider's own favicon (served and cached by the API), or a globe when the site has none. */
export function Favicon({ url }: { url: string | null | undefined }) {
  const [failed, setFailed] = useState(false);
  let host: string | null = null;
  try {
    host = url ? new URL(url).hostname : null;
  } catch {
    host = null;
  }
  if (!host || failed) return <Globe className="size-3.5 shrink-0" />;
  return (
    // eslint-disable-next-line @next/next/no-img-element -- tiny icon from our own API, not worth next/image
    <img
      src={`${API}/api/favicon?domain=${encodeURIComponent(host)}`}
      alt=""
      width={14}
      height={14}
      loading="lazy"
      decoding="async"
      onError={() => setFailed(true)}
      className="size-3.5 shrink-0 rounded-[3px] object-contain"
    />
  );
}

/** Luma's small label pill: 12 px, medium, tinted fill with matching text. */
export function Pill({ children, tone = "gray" }: { children: React.ReactNode; tone?: "gray" | "green" | "brand" | "purple" }) {
  const tones = {
    gray: "bg-foreground/8 text-foreground/65",
    green: "bg-success/15 text-success",
    brand: "bg-brand/15 text-brand-text",
    purple: "bg-memory-soft text-memory-text",
  };
  return <span className={`inline-flex items-center rounded-md px-1.5 py-0.5 text-xs font-medium ${tones[tone]}`}>{children}</span>;
}

export function PlatformTag({ platform }: { platform: string }) {
  return (
    <span
      style={{ "--h": platformHue(platform) } as React.CSSProperties}
      className="rounded-md bg-[oklch(0.93_0.06_var(--h))] px-1.5 py-0.5 text-xs font-medium text-[oklch(0.4_0.13_var(--h))] dark:bg-[oklch(0.32_0.07_var(--h))] dark:text-[oklch(0.88_0.09_var(--h))]"
    >
      {platform}
    </span>
  );
}
