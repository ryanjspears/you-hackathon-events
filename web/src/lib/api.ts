import { useSyncExternalStore } from "react";
export const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// --- types (SPEC.md §5) ---
export type EventItem = {
  id: string;
  title: string;
  start: string | null;
  end?: string | null;
  venue?: string | null;
  address?: string | null;
  city?: string | null;
  url?: string | null;
  platform?: string | null;
  price?: string | null;
  tags?: string[];
  summary?: string | null;
  in_window?: boolean;
  from_source?: boolean; // it comes from a site the user asked for ("jazz on Eventbrite")
  score?: number;
  reason?: string;
  kind?: "going" | "skip";
  ts?: number;
};

export type SearchPlan = {
  city: string | null;
  state_code: string | null;
  categories: string[];
  keywords: string | null;
  date_window: string | null;
  date_from: string | null;
  date_to: string | null;
  clarifying_question: string | null;
  sources?: string[]; // bare hostnames the user asked to search first (optional: older saved chats lack it)
};

/** Display names for the sites the scanner knows. Mirrors scan.py PLATFORMS and crew.py SOURCE_NAMES — keep them identical. */
export const SITES: Record<string, string> = {
  "eventbrite.com": "Eventbrite", "meetup.com": "Meetup", "lu.ma": "Luma", "dice.fm": "Dice",
  "ra.co": "Resident Advisor", "songkick.com": "Songkick", "timeout.com": "Time Out",
};

export function siteName(domain: string): string {
  return SITES[domain] ?? domain;
}

export type Progress = {
  stage: string;
  text?: string;
  t?: number;
  notes?: string[];
  ok?: boolean;
  stderr?: string;
  plan?: SearchPlan;
  [k: string]: unknown;
};

export type ScanResult = {
  events?: EventItem[];
  clarify?: string;
  reply?: string | null;
  error?: string;
  attempts?: number;
  hits?: number;
  pages?: number;
  dropped?: Record<string, number>;
  stats?: { queries: number; hits: number; pages: number; chunks: number; candidates: number; sources?: Record<string, number> };
  recalled?: string[];
  plan?: SearchPlan;
  trace?: TraceSummary;
};

/** Per-request timing (SPEC §1 `trace`): one span per timed step, plus totals summed by span name. */
export type TraceSummary = {
  id: string;
  name: string;
  total_ms: number;
  spans: { name: string; ms: number; at_ms: number; depth: number; attrs: Record<string, unknown> }[];
  by_name: Record<string, { ms: number; n: number }>;
};

export type Recommendations = {
  user: string;
  recalled: string[];
  profile: string | null;
  recommendations: EventItem[];
  going: EventItem[];
};

// --- user (cookie) ---
export function getUser(): string | null {
  if (typeof document === "undefined") return null;
  const m = document.cookie.match(/(?:^|; )events_user=([^;]*)/);
  return m ? decodeURIComponent(m[1]) : null;
}

export function setUser(name: string) {
  document.cookie = `events_user=${encodeURIComponent(name)}; path=/; max-age=${60 * 60 * 24 * 30}`;
  notifyUser();
}

export function clearUser() {
  document.cookie = "events_user=; path=/; max-age=0";
  notifyUser();
}

const PROGRESS_STAGES = ["recalled", "plan", "crew", "search", "extract", "scan", "sandbox", "task", "learned", "recommend", "mem", "trace"];

/** An earlier turn of the conversation, as the Planner sees it (SPEC §1 `history`). */
export type HistoryTurn = { role: "user"; text: string } | { role: "agent"; plan: SearchPlan; clarify?: string };

/** Opens the SSE stream for a chat message (SPEC §1). Returns a closer. */
export function streamScan(
  user: string,
  message: string,
  onProgress: (p: Progress) => void,
  onDone: (r: ScanResult) => void,
  opts: { chaos?: boolean; history?: HistoryTurn[] } = {},
): () => void {
  const url = new URL(`${API}/api/chat/stream`);
  url.searchParams.set("user", user);
  url.searchParams.set("message", message);
  if (opts.chaos) url.searchParams.set("chaos", "1");
  if (opts.history?.length) url.searchParams.set("history", JSON.stringify(opts.history.slice(-8)));
  const es = new EventSource(url.toString());
  let finished = false;
  const finish = (r: ScanResult) => {
    if (finished) return;
    finished = true;
    es.close();
    onDone(r);
  };
  for (const stage of PROGRESS_STAGES) {
    es.addEventListener(stage, (e) => onProgress(JSON.parse((e as MessageEvent).data)));
  }
  es.addEventListener("done", (e) => finish(JSON.parse((e as MessageEvent).data)));
  es.addEventListener("clarify", (e) => finish(JSON.parse((e as MessageEvent).data)));
  es.addEventListener("error", (e) => {
    const data = (e as MessageEvent).data;
    finish(data ? JSON.parse(data) : { error: "The connection to the agent dropped. Try the search again." });
  });
  return () => {
    finished = true;
    es.close();
  };
}

export async function interact(user: string, eventId: string, kind: "going" | "skip") {
  const r = await fetch(`${API}/api/events/${eventId}/interact`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ user, kind }),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json() as Promise<{ ok: boolean; event: EventItem; kind: "going" | "skip" }>;
}

export async function recommendations(user: string, refresh = false) {
  const r = await fetch(`${API}/api/recommendations?user=${encodeURIComponent(user)}${refresh ? "&refresh=1" : ""}`, { cache: "no-store" });
  if (!r.ok) throw new Error(await r.text());
  return r.json() as Promise<Recommendations>;
}

export type ForYou = { user: string; profile: string | null; recommendations: EventItem[]; refreshing: boolean };

/** Home-page picks (SPEC §3d): cached ranking, instant; `refreshing` means the sandbox is re-ranking, poll again. */
export async function forYou(user: string, limit = 4) {
  const r = await fetch(`${API}/api/for-you?user=${encodeURIComponent(user)}&limit=${limit}`, { cache: "no-store" });
  if (!r.ok) throw new Error(await r.text());
  return r.json() as Promise<ForYou>;
}

export type Suggestion = { text: string; why: string; kind: "search" | "tag" | "going" };

/** Home-page prompt chips from past searches and going events (SPEC §3c). SQLite only, instant. */
export async function suggestions(user: string, limit = 4) {
  const r = await fetch(`${API}/api/suggestions?user=${encodeURIComponent(user)}&limit=${limit}`, { cache: "no-store" });
  if (!r.ok) throw new Error(await r.text());
  return r.json() as Promise<{ user: string; suggestions: Suggestion[]; personalized: boolean }>;
}

/** Every event the user marked going, soonest first (SPEC §3b). Instant: no memory call. */
export async function going(user: string) {
  const r = await fetch(`${API}/api/going?user=${encodeURIComponent(user)}`, { cache: "no-store" });
  if (!r.ok) throw new Error(await r.text());
  return r.json() as Promise<{ user: string; going: EventItem[] }>;
}

/** True once the API answers 200 on /api/health (it warms One + memory for ~10–15 s). */
export async function healthy(): Promise<boolean> {
  try {
    const r = await fetch(`${API}/api/health`, { cache: "no-store" });
    return r.ok;
  } catch {
    return false;
  }
}

// --- dates ---
// Work from the ISO string itself so the event keeps its own timezone (a 7pm Brooklyn show stays 7pm).
const DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

export type DayParts = { key: string; day: number; weekday: string; month: string; year: number };

export function dayParts(iso: string | null | undefined): DayParts | null {
  if (!iso || iso.length < 10) return null;
  const y = +iso.slice(0, 4), m = +iso.slice(5, 7), d = +iso.slice(8, 10);
  if (!y || !m || !d) return null;
  const dt = new Date(Date.UTC(y, m - 1, d));
  return { key: iso.slice(0, 10), day: d, weekday: DAYS[dt.getUTCDay()], month: MONTHS[m - 1], year: y };
}

/** "7:30 PM" (Luma's format), or null when the time is midnight (date known, time not). */
export function timeOf(iso: string | null | undefined): string | null {
  if (!iso || iso.length < 16) return null;
  const hh = +iso.slice(11, 13), mm = +iso.slice(14, 16);
  if (hh === 0 && mm === 0) return null;
  const h12 = hh % 12 === 0 ? 12 : hh % 12;
  return `${h12}:${String(mm).padStart(2, "0")} ${hh < 12 ? "AM" : "PM"}`;
}

export function fmtDate(iso: string | null | undefined) {
  const p = dayParts(iso);
  if (!p) return "Date to be announced";
  const t = timeOf(iso);
  return `${p.weekday.slice(0, 3)} ${p.day} ${p.month.slice(0, 3)}${t ? ", " + t : ""}`;
}

export type DayGroup = { parts: DayParts | null; events: EventItem[] };

/** Groups events by calendar day, keeping the incoming (ranked) order inside each day. Undated events go last. */
export function groupByDay(events: EventItem[]): DayGroup[] {
  const map = new Map<string, DayGroup>();
  for (const e of events) {
    const p = dayParts(e.start);
    const k = p?.key ?? "tbd";
    if (!map.has(k)) map.set(k, { parts: p, events: [] });
    map.get(k)!.events.push(e);
  }
  return [...map.values()].sort((a, b) => {
    if (!a.parts) return 1;
    if (!b.parts) return -1;
    return a.parts.key < b.parts.key ? -1 : 1;
  });
}

// --- platform colour: a stable hue per source ---
const PLATFORM_HUE: Record<string, number> = {
  eventbrite: 40,
  meetup: 20,
  luma: 340,
  dice: 265,
  "resident advisor": 195,
  songkick: 330,
  "time out": 5,
};
export function platformHue(platform: string | null | undefined): number {
  if (!platform) return 290;
  const k = platform.toLowerCase();
  if (k in PLATFORM_HUE) return PLATFORM_HUE[k];
  let h = 0;
  for (const c of k) h = (h * 31 + c.charCodeAt(0)) % 360;
  return h;
}

// --- user cookie as an external store (avoids setState-in-effect) ---
const listeners = new Set<() => void>();
export function subscribeUser(cb: () => void) {
  listeners.add(cb);
  return () => listeners.delete(cb);
}
export function notifyUser() {
  listeners.forEach((l) => l());
}
export function useUser(): string | null {
  return useSyncExternalStore(subscribeUser, getUser, () => null);
}
