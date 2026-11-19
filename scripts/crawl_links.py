"""Crawl the site from a local server and report broken internal links, redirects and language switches.

    python3 -m http.server 8000 &   (in the repo)
    python3 scripts/crawl_links.py [http://localhost:8000]
"""
import re, sys
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.request import urlopen
from urllib.error import HTTPError

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000").rstrip("/") + "/"
HOSTS = {urlparse(BASE).netloc, "heocr.org"}

class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.links = []; s.refresh = None; s.attrs = {}
    def handle_starttag(s, tag, a):
        a = dict(a)
        for k in ("href", "src"):
            if k in a and tag != "meta": s.links.append((tag, a[k], a))
        if tag == "meta" and (a.get("http-equiv") or "").lower() == "refresh":
            s.refresh = re.sub(r"^\d+;\s*url=", "", a["content"])
        if tag == "html": s.attrs = a

def get(url):
    try:
        with urlopen(url) as r: return r.status, r.read().decode("utf-8", "replace")
    except HTTPError as e: return e.code, ""

OLD = ["he/", "he/index.html"] + [f"he/{n}.html" for n in ("benchmarks", "htext", "download", "rights", "privacy")]  # old URLs: redirects
seen, queue, broken, pages = set(), [BASE] + [BASE + o for o in OLD], [], {}
while queue:
    u = queue.pop()
    if u in seen: continue
    seen.add(u)
    st, body = get(u)
    if st != 200: broken.append((u, st)); continue
    if not u.endswith((".html", "/")): continue
    p = P(); p.feed(body); pages[u] = p
    targets = [(l, a) for _, l, a in p.links] + ([(p.refresh, {})] if p.refresh else [])
    for l, a in targets:
        if l.startswith(("mailto:", "data:", "#")): continue
        full = urldefrag(urljoin(u, l))[0]
        host = urlparse(full).netloc
        if host == urlparse(BASE).netloc:
            if full not in seen: queue.append(full)
        elif host in HOSTS: pass  # canonical/og absolute URLs on the production host
print(f"pages crawled: {len(pages)}, urls checked: {len(seen)}")
for u, p in sorted(pages.items()):
    print(f"  {u.replace(BASE, '/')}: lang={p.attrs.get('lang')} dir={p.attrs.get('dir')}"
          + (f" -> redirect {p.refresh}" if p.refresh else ""))
print(f"broken internal links: {len(broken)}")
for u, st in broken: print("  BROKEN", st, u)
sys.exit(1 if broken else 0)
