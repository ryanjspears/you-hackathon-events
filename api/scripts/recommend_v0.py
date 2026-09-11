# Runs inside the Daytona sandbox via harness.py.
# INPUT = {"profile": {"tags": {tag: weight}, "platforms": {name: weight}, "venues": {name: weight}, "price_free_bias": float},
#          "candidates": [Event...], "exclude": [id...]}
import json
import re

profile = INPUT.get("profile", {})
tags_w = profile.get("tags", {})
plat_w = profile.get("platforms", {})
venue_w = profile.get("venues", {})
exclude = set(INPUT.get("exclude", []))


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def mentions(tag, text):
    # whole words only: "ai" must not light up "trail" or "mountain"
    return re.search(r"\b" + re.escape(norm(tag)) + r"\b", text) is not None


ranked = []
seen_titles = set()
for e in INPUT.get("candidates", []):
    if e["id"] in exclude:
        continue
    dup = (norm(e.get("title")), (e.get("start") or "")[:10])  # same listing scraped twice
    if dup in seen_titles:
        continue
    seen_titles.add(dup)
    score, why = 0.0, []
    text = norm(e.get("title")) + " " + norm(e.get("summary"))
    for t, w in tags_w.items():
        if t in (e.get("tags") or []) or mentions(t, text):
            score += w
            why.append(t)
    p = e.get("platform")
    if p and p in plat_w:
        score += 0.5 * plat_w[p]
        why.append(p)
    v = norm(e.get("venue"))
    if v and v in venue_w:
        score += 1.5 * venue_w[v]
        why.append(e.get("venue"))
    price = (e.get("price") or "").lower()
    if profile.get("price_free_bias") and ("free" in price or price in ("$0", "0")):
        score += profile["price_free_bias"]
    if score > 0:
        ranked.append({"id": e["id"], "score": round(score, 3), "reason": "Because you like " + ", ".join(dict.fromkeys(why[:3]))})

ranked.sort(key=lambda r: -r["score"])
print(json.dumps({"ranked": ranked[:20]}))
