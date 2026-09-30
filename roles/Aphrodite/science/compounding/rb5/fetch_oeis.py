"""RB-5: fetch an OEIS subset (forensic, not a disposition).

Selection is OEIS's OWN, not ours: every sequence with keyword:core, then
sequences with keyword:easy in OEIS's default search ranking, until TARGET
unique sequences are cached. Only (number, name, data, offset, keyword,
formula[:3]) are kept. Pages are cached under rb5/cache/ so reruns are offline.
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / "cache"
CACHE.mkdir(exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Prometheus RB-5 research census; polite, cached)"}
TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 600


def page(q, start):
    fn = CACHE / ("oeis_%s_%04d.json" % (q.replace(":", "_").replace(" ", "+"), start))
    if fn.exists():
        return json.loads(fn.read_text(encoding="utf-8"))
    url = "https://oeis.org/search?q=%s&fmt=json&start=%d" % (q.replace(" ", "+"), start)
    for attempt in range(3):
        try:
            raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
            d = json.loads(raw) or []
            break
        except Exception as e:  # noqa: BLE001
            print("retry", url, e, flush=True)
            time.sleep(5)
    else:
        return None
    if isinstance(d, dict):
        d = d.get("results") or []
    keep = [{"number": x["number"], "name": x.get("name", ""), "data": x.get("data", ""),
             "offset": x.get("offset", ""), "keyword": x.get("keyword", ""),
             "formula": (x.get("formula") or [])[:3]} for x in d]
    fn.write_text(json.dumps(keep), encoding="utf-8")
    time.sleep(1.5)
    return keep


def main():
    seen = {}
    for q in ("keyword:core", "keyword:easy"):
        start = 0
        while len(seen) < TARGET:
            rows = page(q, start)
            if not rows:
                break
            for x in rows:
                seen.setdefault(x["number"], dict(x, source=q))
            print(q, start, len(seen), flush=True)
            start += 10
            if q == "keyword:core" and start > 400:
                break
    out = sorted(seen.values(), key=lambda x: x["number"])
    (CACHE / "oeis_selection.json").write_text(json.dumps(out, indent=0), encoding="utf-8")
    print("cached", len(out))


if __name__ == "__main__":
    main()
