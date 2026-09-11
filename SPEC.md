# SPEC.md — Events Scanner backend contract (for the frontend)

Base URL: `http://localhost:8000` (`NEXT_PUBLIC_API_URL`). CORS is open for `localhost:3000`. No auth — the "user" is a name string the client picks and sends on every call (lowercased server-side). All bodies and responses are JSON. Times are ISO 8601 with offset (`2026-09-13T17:00:00-04:00`).

What happens behind a search: **Planner** agent (parses the message) → **Scanner** agent (runs `scan.py` in a Daytona sandbox through One; the script calls You.com search + contents, extracts and normalizes events; agent repairs the script if it crashes) → **Curator** agent (ranks results, writes the reply). One search takes **40–90 s**; progress is streamed so the UI is never silent.

---

## 1. `GET /api/chat/stream` — run a search (SSE)

Query params:

| param | type | notes |
| --- | --- | --- |
| `user` | string, required | the logged-in name |
| `message` | string, required | free text, e.g. `jazz shows in Brooklyn this weekend` |
| `chaos` | `1`/`true`, optional | demo lever: injects a crashing candidate so the Scanner's repair loop fires (expect `attempts: 2`) |
| `history` | JSON string, optional (≤20 kB) | the earlier turns of this conversation, oldest first: `[{"role":"user","text":"running events in nyc"},{"role":"agent","plan":SearchPlan},{"role":"user","text":"how about jazz"}, …]`; agent turns may add `"clarify": "<question>"`. The Planner reads the new `message` as a follow-up, so city/dates carry over from the last searched plan unless the message changes them. Send the last ~8 turns. |

Response is `text/event-stream`. Use `new EventSource(url)` and `addEventListener(<event name>)`. Every `data:` payload is JSON. One request produces a sequence of **progress events** and exactly **one terminal event** (`done`, `clarify`, or `error`), after which the server closes the stream — call `es.close()` on any terminal event (the browser would otherwise auto-reconnect and start a new search).

Only one search runs at a time server-wide (single-user demo); a second request queues until the first finishes.

### Progress events

All progress payloads have the shape `{ stage: string, t: number (unix seconds), text: string, ...extra }`. `text` is a short human-readable line — rendering `stage: text` as a chip/log line is enough. Stages, in the order they typically appear:

| event name (`stage`) | when | `text` examples | extra fields |
| --- | --- | --- | --- |
| `recalled` | first, always | `Recalled: nothing yet for ryan` / `Recalled: Went to 'Jazz Vespers' (Eventbrite); likes jazz \| Profile: likes jazz, live-music` | `notes: string[]` |
| `plan` | Planner done | `plan: {"city":"Brooklyn, NY",...}` | `plan: SearchPlan` (see §5) |
| `crew` | crew kicks off | `crew started: Planner ✓ → Scanner (Daytona via One) → Curator` | |
| `sandbox` | sandbox lifecycle + script runs | `creating Daytona sandbox via One`, `sandbox 7efe03f1 ready`, `attempt 1: running scan.py in Daytona via One`, `exit 0 — 22 clean events`, `exit 1 — repairing` | on failure: `stderr: string` (tail of traceback) |
| `scan` | lines the script logs inside the sandbox, streamed live every ~3 s while it runs (≈10–20 per run) | `eventbrite.com: 12 results (priority)` (a requested site), `meetup.com: 9 results`, `10 listing pages read (49k chars)`, `page Eventbrite: 12 candidates` | |
| `sandbox` (heartbeat) | every ~9 s while the script runs, so the UI can show "thinking" with elapsed time | `scan.py running in Daytona · 24s` | `elapsed: number` (seconds) |
| `task` | an agent finished | `Event Scanner finished`, `Event Curator finished` | |
| `learned` | a note was written to One memory | `Learned: Searched for jazz in Brooklyn, NY this weekend` | `ok: boolean` |
| `trace` | every timed step as it finishes (≈50 per run: each One call, LLM call, tool call, sandbox phase) | `llm.call 2.48s agent=Event Planner model=gpt-4o … total_tokens=1242`, `sandbox.run 38.68s script_wall_s=38.0 polls=12` | `span: string`, `ms: number`, `at_ms: number` (offset from request start), `attrs: object`; the last one has `summary: true` and text `total 51.7s · sandbox.run 38.7s, llm.call 12.3s, …` |
| `ping` | every 10 s of silence (keep-alive) | `{}` — ignore | |

Suggested UI: a horizontal list of chips or a collapsible log; highlight `recalled`/`learned` (that's the learning story judges look for) and `sandbox` lines containing `repairing` (self-repair story).

### Terminal events

**`done`** — the search finished:

```jsonc
{
  "events": Event[],            // ranked by the Curator, best match first (see §5)
  "reply": "I found 22 listings…",   // Curator's 2-3 sentence reply for the chat bubble; may be null
  "attempts": 1,                // sandbox runs; 2+ means the repair loop fired
  "hits": 40,                   // raw You.com search results considered
  "pages": 10,                  // listing pages read via You.com Contents
  "dropped": { "no_date": 5, "past": 3, "too_far": 0, "dupe": 0, "no_title": 0 },  // candidates filtered out by the normalizer
  "stats": { "queries": 8, "hits": 40, "pages": 10, "chunks": 11, "candidates": 30, "sources": { "eventbrite.com": 14 } },  // sources: deduped hits per requested site (0 = it had nothing)
  "plan": SearchPlan,
  "recalled": string[],         // same notes as the `recalled` event
  "trace": {                    // per-request timing (see the `trace` progress event); absent if TRACE=0
    "id": "1f55b6f5", "name": "chat", "total_ms": 51677,
    "spans": [{ "name": "llm.call", "ms": 2480, "at_ms": 260, "depth": 1, "attrs": { "agent": "Event Planner", "total_tokens": 1242 } }, …],
    "by_name": { "llm.call": { "ms": 12286, "n": 5 }, "sandbox.run": { "ms": 38677, "n": 1 }, … }
  }
}
```

`stats.timing` (inside the sandbox, seconds): `search`, `contents`, `extract`, `normalize`, `total`, plus per-call lists `search_calls` and `extract_calls`.

`events` can be empty (`[]`) — show `reply` (it will suggest widening the search).

**`clarify`** — the Planner could not find a city in the message; nothing was searched:

```json
{ "clarify": "Which city should I search in?", "plan": SearchPlan }
```

Show `clarify` as the assistant's bubble and let the user answer; the answer is just a new message sent with `history` (the earlier request plus the `clarify` turn), and the Planner combines the two.

**`error`** — the crew failed: `{ "error": "…" }`. Show it and let the user retry.

### Client sketch

```ts
const url = new URL(`${API}/api/chat/stream`);
url.searchParams.set("user", user); url.searchParams.set("message", text);
const es = new EventSource(url);
["recalled","plan","crew","sandbox","scan","task","learned"].forEach(s =>
  es.addEventListener(s, e => onProgress(JSON.parse(e.data))));
const finish = (e: MessageEvent) => { es.close(); onDone(JSON.parse(e.data)); };
es.addEventListener("done", finish);
es.addEventListener("clarify", finish);
es.addEventListener("error", e => { es.close(); onDone((e as MessageEvent).data ? JSON.parse((e as MessageEvent).data) : { error: "connection lost" }); });
```

---

## 2. `POST /api/events/{id}/interact` — "I'm going" / "not for me"

Body: `{ "user": "ryan", "kind": "going" | "skip" }`
Response `200`: `{ "ok": true, "event": Event, "kind": "going" }`
Errors: `400` bad kind, `404` unknown event id (only ids returned by a previous search exist).

Side effects (asynchronous, after the response): a `Learned:` note goes to One memory and the "For you" ranking is recomputed in the sandbox (takes ~5–15 s). Repeating the same `(user, event, kind)` is idempotent. Marking an event `going` after `skip` (or vice versa) records both; the latest one wins in the profile.

UI: optimistic toggle on the card (`Going ✓` / dimmed for skip); toast; if the user is on the home page, refetch recommendations ~2 s later.

---

## 3. `GET /api/recommendations?user=ryan[&refresh=1]` — the "For you" page

```jsonc
{
  "user": "ryan",
  "recalled": string[],              // preference notes from One memory ("Recalled: …" chips)
  "profile": "likes jazz, live-music; finds events on Eventbrite; in Brooklyn, NY" | null,
  "recommendations": (Event & { "score": number, "reason": string })[],   // best first, ≤12; excludes going/skipped
  "going": (Event & { "kind": "going", "ts": number })[]                  // events the user marked going, newest first
}
```

- `reason` is a short phrase like `Because you like jazz, Eventbrite, Saint Peter's Church` — show under the title.
- `recommendations` is empty until the user has at least one `going`/search that yields tags; show an empty state pointing to search.
- `refresh=1` forces a re-rank in the sandbox before responding (2–10 s, useful for a "re-rank" button); without it the cached ranking is returned instantly.

---

## 3b. `GET /api/going?user=ryan` — the "Going" timeline page

```jsonc
{ "user": "ryan", "going": (Event & { "kind": "going", "ts": number })[] }   // soonest first; undated last
```

Only events whose **latest** interaction is `going` (a later `skip` removes them). No memory call, so it answers instantly — use it for the timeline page instead of `/api/recommendations`.

UI: `/going` — a top-down day-rail timeline (same component as search results) with an "Upcoming" list and a muted "Past" section; **Not for me** on a card removes it.

## 3c. `GET /api/suggestions?user=ryan[&limit=4]` — home-page prompt chips

```jsonc
{ "user": "ryan", "personalized": true,
  "suggestions": [{ "text": "jazz shows in Brooklyn, NY next week", "why": "you searched this on Tuesday", "kind": "search" | "tag" | "going" }] }
```

3–5 ready-to-send prompts built from recent searches (topic + city, date window moved forward), the tags of events marked going (`kind: "going"`, `why` names the event), and the profile's most-picked tags (`kind: "tag"`). `personalized: false` means the user has no history and the generic examples came back. SQLite only, answers in milliseconds; never calls memory or the crew. `text` is phrased so the Planner parses it without a clarifying question.

UI: render the generic examples immediately, swap in the response; show `why` as the chip tooltip; refetch after a search finishes and ~0.5 s after a `going` mark.

## 3d. `GET /api/for-you?user=ryan[&limit=4][&refresh=1]` — the home page's targeted picks

```jsonc
{ "user": "ryan",
  "profile": "likes jazz, running; finds events on Eventbrite; in Queens, NY" | null,
  "recommendations": (Event & { "score": number, "reason": string })[],   // best first, ≤ limit; excludes going/skipped
  "refreshing": boolean }   // true while the sandbox is re-ranking: poll again in a few seconds
```

Instant: returns the cached ranking. When the user has done something since it was written (a search, a going or skip), or has a profile but no ranking yet, or `refresh=1`, a re-rank starts on a background thread (One → Daytona, ~4 s warm, ~35 s cold) and `refreshing` is true; the API also kicks one off after every search that returned events. Candidates come from every city the user searched or is going to (any spelling: "NYC", "New York", "Brooklyn" all count as New York).

UI: home page, under the prompt chips, when the conversation is empty: "For you" heading, the `profile` line, up to 4 cards with `reason` and **I'm going** / **Not for me**; while `refreshing`, a spinner line and skeletons if there are no cards yet; poll every ~4 s until it clears. A pick removes the card at once and refetches ~1.5 s later.

## 4. Small endpoints

- `GET /api/events/{id}` → `Event` or `404`.
- `GET /api/favicon?domain=www.eventbrite.com` → the provider's favicon bytes (`image/*`, `Cache-Control: max-age=604800`) or `404` when the site has none. Fetched from the site itself once (`<link rel="icon">`, then `/favicon.ico`) and cached on disk in `.favicons/`; use the host of `Event.url` as `domain` and fall back to a generic icon on error.
- `GET /api/health` → `{ ok, connections: ["you","daytona"], actions: {...} }` — poll this on app load; while it's not `200` the API is still starting (One MCP + memory warm-up, ~10–15 s).

---

## 5. Types

```ts
type Event = {
  id: string;                 // 16-hex, unique per (url, title, day); stable across searches; use as React key and for /interact
  title: string;
  start: string;              // ISO 8601 with offset; midnight means "date known, time not"
  end: string | null;
  venue: string | null;
  address: string | null;
  city: string | null;
  url: string | null;         // ticket/listing link — open in new tab
  platform: string | null;    // "Eventbrite" | "Meetup" | "Luma" | "Dice" | "Resident Advisor" | "Songkick" | "Time Out" | hostname
  price: string | null;       // free text: "Free", "From $28.52", "$20"
  tags: string[];             // lowercase, hyphenated, ≤8: ["jazz","live-music","williamsburg"]
  summary: string | null;     // ≤280 chars
  in_window: boolean;         // inside the dates the user asked for (false = later, still upcoming)
  from_source: boolean;       // from a site the user asked for ("jazz on Eventbrite"); such events come first within in_window
};

type SearchPlan = {
  city: string | null;          // "Brooklyn, NY"
  state_code: string | null;    // "NY"
  categories: string[];         // ["jazz"]
  keywords: string | null;
  date_window: string | null;   // "this weekend"
  date_from: string | null;     // "2026-09-11"
  date_to: string | null;       // "2026-09-13"
  clarifying_question: string | null;
  sources: string[];          // bare hostnames the user asked to search ("on Eventbrite" → ["eventbrite.com"]); searched and ranked first, other sites still included. Max 3. Carries over between turns; a source in a follow-up replaces, "also …" adds, "anywhere" clears
};
```

Formatting hints: `in_window === false` events should be visually separated ("Later" section or muted badge). `start` ending in `T00:00:00` → render date only. Platform badge colour by `platform`. `from_source === true` → a small "as asked" mark next to the platform; the result summary can say "Eventbrite first (n)" from `plan.sources` + `stats.sources`.

---

## 6. Screens the backend supports

1. **Login** — just a name (cookie/localStorage); no server call.
2. **Home / For you** — the chat page's empty state: prompt chips from `GET /api/suggestions` (§3c), then "For you" picks from `GET /api/for-you` (§3d) with the profile line, `reason` under each title, and **I'm going** / **Not for me**. (`GET /api/recommendations` §3 remains for a fuller page with `recalled` chips and a "Re-rank" button.)
3. **Going** — `GET /api/going` on load; the day-rail timeline of everything the user marked going, soonest first; past events under a muted "Past" heading. Linked from the sidebar and from the "See timeline" action on the going toast.
4. **Search / chat** — message → SSE; show progress chips while running; on `done` render `reply` as the assistant bubble and the `events` as cards with **I'm going** / **Not for me** buttons (§2); on `clarify` render the question. Prompt chips come from `GET /api/suggestions` (§3c); the generic examples (`jazz shows in Brooklyn this weekend`, `AI meetups in NYC next week`, `techno parties in Manhattan Friday night`) are the fallback.

Demo flow the UI should make easy: search → mark two events going (`Learned:` appears) → log out/in → home shows `Recalled:` + recommendations ranked by what was picked.
