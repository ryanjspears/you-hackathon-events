"""Provider favicons: fetched once from the site itself, cached on disk and in memory.

`GET /api/favicon?domain=www.eventbrite.com` → the icon bytes (or 404). Resolution order:
the page's `<link rel="icon">` (also `shortcut icon`, `apple-touch-icon`), then `/favicon.ico` and a few
other common paths (`FALLBACK_PATHS`).
Cache: `<dir>/<domain>.bin` + `<domain>.json` ({content_type, fetched}); misses are remembered
in memory for a day so a site without an icon is not hammered.
"""
from __future__ import annotations

import json
import os
import re
import threading
import time
from html.parser import HTMLParser
from urllib.parse import urljoin

import httpx

from api import trace
from api.store import DB_PATH

CACHE_DIR = os.environ.get("EVENTS_FAVICON_DIR", os.path.join(os.path.dirname(DB_PATH), ".favicons"))
MAX_BYTES = 512 * 1024
MISS_TTL = 24 * 3600
DOMAIN_RE = re.compile(r"^[a-z0-9.-]{1,253}$")
# a browser-like UA: some providers (ra.co) answer 403 to anything else
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
FALLBACK_PATHS = ("/favicon.ico", "/static/favicon.ico", "/favicon.png", "/apple-touch-icon.png")

_mem: dict[str, tuple[bytes, str] | None] = {}
_miss_at: dict[str, float] = {}
_lock = threading.Lock()


class _IconLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.icons: list[tuple[int, str]] = []  # (priority, href)

    def handle_starttag(self, tag, attrs):
        if tag != "link":
            return
        a = dict(attrs)
        rel = (a.get("rel") or "").lower().split()
        href = a.get("href")
        if not href:
            return
        if "icon" in rel and "apple-touch-icon" not in rel:
            self.icons.append((0, href))
        elif "apple-touch-icon" in rel:
            self.icons.append((1, href))


def _paths(domain: str) -> tuple[str, str]:
    return os.path.join(CACHE_DIR, f"{domain}.bin"), os.path.join(CACHE_DIR, f"{domain}.json")


def _from_disk(domain: str) -> tuple[bytes, str] | None:
    bin_path, meta_path = _paths(domain)
    try:
        with open(meta_path) as f:
            meta = json.load(f)
        with open(bin_path, "rb") as f:
            return f.read(), meta["content_type"]
    except (OSError, KeyError, ValueError):
        return None


def _to_disk(domain: str, data: bytes, content_type: str) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    bin_path, meta_path = _paths(domain)
    with open(bin_path, "wb") as f:
        f.write(data)
    with open(meta_path, "w") as f:
        json.dump({"content_type": content_type, "fetched": int(time.time())}, f)


def _get_image(client: httpx.Client, url: str) -> tuple[bytes, str] | None:
    r = client.get(url)
    ctype = r.headers.get("content-type", "").split(";")[0].strip().lower()
    if r.status_code != 200 or len(r.content) < 16 or len(r.content) > MAX_BYTES:
        return None
    if not (ctype.startswith("image/") or url.endswith(".ico") and r.content[:4] in (b"\x00\x00\x01\x00", b"\x89PNG")):
        return None
    if not ctype.startswith("image/"):
        ctype = "image/png" if r.content[:4] == b"\x89PNG" else "image/x-icon"
    return r.content, ctype


def _fetch(domain: str) -> tuple[bytes, str] | None:
    with httpx.Client(timeout=6, follow_redirects=True, headers={"User-Agent": UA, "Accept": "*/*"}) as client:
        candidates: list[str] = []
        home = f"https://{domain}/"
        try:
            r = client.get(home)
            if r.status_code == 200 and "html" in r.headers.get("content-type", ""):
                p = _IconLinks()
                p.feed(r.text[:200_000])
                base = str(r.url)
                candidates = [urljoin(base, href) for _, href in sorted(p.icons, key=lambda x: x[0])]
        except httpx.HTTPError:
            pass
        candidates += [urljoin(home, path) for path in FALLBACK_PATHS]
        for url in candidates[:8]:
            try:
                img = _get_image(client, url)
            except httpx.HTTPError:
                img = None
            if img:
                return img
    return None


def get(domain: str) -> tuple[bytes, str] | None:
    """Icon bytes + content type for a host, from memory → disk → the site. None when the site has no usable icon."""
    domain = domain.strip().lower()
    if not DOMAIN_RE.match(domain) or ".." in domain:
        return None
    with _lock:
        if domain in _mem:
            return _mem[domain]
        if time.time() - _miss_at.get(domain, 0) < MISS_TTL:
            return None
    hit = _from_disk(domain)
    if hit is None:
        with trace.span("favicon.fetch", domain=domain) as s:
            hit = _fetch(domain)
            s["found"] = hit is not None
        if hit:
            _to_disk(domain, *hit)
    with _lock:
        if hit:
            _mem[domain] = hit
        else:
            _miss_at[domain] = time.time()
    return hit
