#!/usr/bin/env bash
# Two-run demo against a running API (uvicorn api.main:app --port 8000).
# Run 1: search → mark the first two events "going" (Learned:). Run 2: recommendations (Recalled:).
set -euo pipefail
USER_NAME="${1:-demo}"
API="${API:-http://localhost:8000}"
MSG="${2:-jazz shows in Brooklyn this weekend}"

echo "== Run 1: scan as $USER_NAME: \"$MSG\""
STREAM=$(curl -sN "$API/api/chat/stream?user=$USER_NAME&message=$(python3 -c 'import sys,urllib.parse;print(urllib.parse.quote(sys.argv[1]))' "$MSG")")
echo "$STREAM" | grep -E '^event: (recalled|search|sandbox|learned|clarify|error)' -A1 | grep '^data:' | sed 's/^data: //' | python3 -c '
import json,sys
for line in sys.stdin:
    try: d=json.loads(line)
    except Exception: continue
    if d.get("text"): print("  ", d["text"])'
DONE=$(echo "$STREAM" | awk '/^event: done/{getline; sub(/^data: /,""); print}')
[ -n "$DONE" ] || { echo "no done event (missing city? error?)"; exit 1; }
IDS=$(echo "$DONE" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(" ".join(e["id"] for e in d["events"][:2])); print(len(d["events"]), "events", file=sys.stderr)')
for id in $IDS; do
  echo "== I'm going: $id"
  curl -s -X POST "$API/api/events/$id/interact" -H 'content-type: application/json' -d "{\"user\":\"$USER_NAME\",\"kind\":\"going\"}" | python3 -c 'import json,sys; print("  ", json.load(sys.stdin)["event"]["title"])'
done
sleep 8
echo "== Run 2: recommendations for $USER_NAME"
curl -s "$API/api/recommendations?user=$USER_NAME&refresh=1" | python3 -c '
import json,sys; d=json.load(sys.stdin)
print("   Recalled:", " | ".join(d["recalled"]) or "nothing")
print("   Profile:", d["profile"])
for r in d["recommendations"][:5]: print(f"   {r['score']:.1f}  {r['title']}  — {r['reason']}")'
