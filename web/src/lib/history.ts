import { useSyncExternalStore } from "react";
import type { EventItem, Progress, ScanResult } from "@/lib/api";

// --- chat history, kept per user in localStorage (the backend has no conversation store; SPEC.md) ---

export type Turn =
  | { role: "user"; text: string; sent?: string } // `sent`: legacy field from before conversation history was sent to the API
  | { role: "agent"; text?: string | null; events?: EventItem[]; progress: Progress[]; result?: ScanResult; running: boolean };

export type Conversation = {
  id: string;
  user: string;
  title: string;
  createdAt: number; // unix ms
  updatedAt: number;
  turns: Turn[];
};

const KEY = (user: string) => `events_history:${user}`;
const MAX_CONVERSATIONS = 40;
const EMPTY: Conversation[] = [];

const cache = new Map<string, Conversation[]>();
let activeId: string | null = null;
const listeners = new Set<() => void>();

function emit() {
  listeners.forEach((l) => l());
}

function subscribe(cb: () => void) {
  listeners.add(cb);
  return () => {
    listeners.delete(cb);
  };
}

function read(user: string): Conversation[] {
  const hit = cache.get(user);
  if (hit) return hit;
  let list: Conversation[] = EMPTY;
  try {
    const raw = typeof localStorage !== "undefined" ? localStorage.getItem(KEY(user)) : null;
    if (raw) list = (JSON.parse(raw) as Conversation[]).map(settle);
  } catch {
    list = EMPTY;
  }
  cache.set(user, list);
  return list;
}

function write(user: string, list: Conversation[]) {
  const sorted = [...list].sort((a, b) => b.updatedAt - a.updatedAt).slice(0, MAX_CONVERSATIONS);
  cache.set(user, sorted);
  try {
    localStorage.setItem(KEY(user), JSON.stringify(sorted));
  } catch {
    // quota or private mode: the in-memory copy still works for this session
  }
  emit();
}

/** A turn that was streaming when the page was closed can never finish; say so instead of showing a spinner forever. */
function settle(c: Conversation): Conversation {
  return {
    ...c,
    turns: c.turns.map((t) =>
      t.role === "agent" && t.running ? { ...t, running: false, text: t.text ?? "This search was interrupted before it finished. Ask again to rerun it." } : t,
    ),
  };
}

export function titleFor(text: string) {
  const t = text.trim().replace(/\s+/g, " ");
  return t.length > 60 ? t.slice(0, 57).trimEnd() + "…" : t;
}

// --- hooks ---

export function useConversations(user: string | null): Conversation[] {
  return useSyncExternalStore(
    subscribe,
    () => (user ? read(user) : EMPTY),
    () => EMPTY,
  );
}

export function useActiveId(): string | null {
  return useSyncExternalStore(
    subscribe,
    () => activeId,
    () => null,
  );
}

// --- actions ---

export function selectConversation(id: string | null) {
  if (activeId === id) return;
  activeId = id;
  emit();
}

/** "New search": just drop the selection; a conversation is created when the first message is sent. */
export function startNewConversation() {
  selectConversation(null);
}

export function createConversation(user: string, firstMessage: string): Conversation {
  const now = Date.now();
  const c: Conversation = {
    id: `${now.toString(36)}${Math.random().toString(36).slice(2, 8)}`,
    user,
    title: titleFor(firstMessage),
    createdAt: now,
    updatedAt: now,
    turns: [],
  };
  write(user, [c, ...read(user)]);
  activeId = c.id;
  emit();
  return c;
}

export function updateTurns(user: string, id: string, fn: (turns: Turn[]) => Turn[]) {
  const list = read(user);
  const i = list.findIndex((c) => c.id === id);
  if (i < 0) return;
  const next = [...list];
  next[i] = { ...list[i], turns: fn(list[i].turns), updatedAt: Date.now() };
  write(user, next);
}

export function deleteConversation(user: string, id: string) {
  write(
    user,
    read(user).filter((c) => c.id !== id),
  );
  if (activeId === id) {
    activeId = null;
    emit();
  }
}

export function clearHistory(user: string) {
  write(user, []);
  activeId = null;
  emit();
}

// --- grouping for the sidebar ---

export type HistoryGroup = { label: string; items: Conversation[] };

export function groupByAge(list: Conversation[], now = Date.now()): HistoryGroup[] {
  const day = 24 * 60 * 60 * 1000;
  const startOfToday = new Date(now).setHours(0, 0, 0, 0);
  const buckets: HistoryGroup[] = [
    { label: "Today", items: [] },
    { label: "Yesterday", items: [] },
    { label: "Previous 7 days", items: [] },
    { label: "Older", items: [] },
  ];
  for (const c of list) {
    const t = c.updatedAt;
    if (t >= startOfToday) buckets[0].items.push(c);
    else if (t >= startOfToday - day) buckets[1].items.push(c);
    else if (t >= startOfToday - 7 * day) buckets[2].items.push(c);
    else buckets[3].items.push(c);
  }
  return buckets.filter((b) => b.items.length > 0);
}

/** "22 events · Brooklyn" style subtitle from the last finished agent turn. */
export function summarize(c: Conversation): string | null {
  const last = [...c.turns].reverse().find((t) => t.role === "agent" && !t.running);
  if (!last || last.role !== "agent") return c.turns.some((t) => t.role === "agent" && t.running) ? "Searching…" : null;
  if (!last.result) return "Interrupted";
  if (last.result.error) return "Failed";
  if (last.result?.clarify) return "Needs a city";
  const n = last.events?.length ?? 0;
  const city = last.result?.plan?.city;
  return [n === 1 ? "1 event" : `${n} events`, city].filter(Boolean).join(" · ");
}
