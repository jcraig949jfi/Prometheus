"""Bounded upstream probe -- base rule 9 (upstream liveness is a launch
precondition) and the only thing that can satisfy a RESOURCE claim.

This is NOT a scan cycle. It makes a small, counted number of requests,
records what actually happened (status, latency, item count, the observed
rate-limit headers if any), and writes a measurement record. It never writes
the dedup index, never scores anything, never calls a model, and never
writes a digest.

Know before you knock (the Dawn Constitution, kept): every source probed
here carries its documented limit in the call site below, read from the
source's own terms, with the budget set at or under 75 percent of it.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parents[3]
OBSERVER = "eos-intake"
UA = "Prometheus-Eos/2.0 (bounded liveness probe; contact via repository)"

#: documented limit -> budget at or under 75 percent, per source.
BUDGETS = {
    # arXiv asks for 1 request per 3 seconds and no burst. 75% of that
    # cadence is one request per 4 seconds; we make at most 2 requests.
    "arxiv": {"documented": "1 request / 3 s", "min_interval_s": 4.0, "max_requests": 2},
    # OpenAlex polite pool: 10 req/s with a mailto. We make at most 1.
    "openalex": {"documented": "10 req/s (polite pool)", "min_interval_s": 1.0, "max_requests": 1},
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get(url: str, timeout: int = 30) -> Dict[str, Any]:
    """One request. Returns a measurement record whether it succeeds or not:
    a failure is a fact about the probe and is recorded as such."""
    rec: Dict[str, Any] = {"endpoint": url, "observed_at": _now(), "observed_by": OBSERVER}
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            rec.update(status=resp.status, latency_ms=int((time.time() - t0) * 1000),
                       bytes=len(body),
                       observed_limit_headers={k: v for k, v in resp.headers.items()
                                               if "rate" in k.lower() or "limit" in k.lower()})
            rec["_body"] = body
    except urllib.error.HTTPError as e:
        rec.update(status=e.code, latency_ms=int((time.time() - t0) * 1000),
                   error="HTTPError", detail=str(e)[:200])
    except Exception as e:  # network down, DNS, timeout, TLS
        rec.update(status="EXCEPTION", latency_ms=int((time.time() - t0) * 1000),
                   error=type(e).__name__, detail=str(e)[:200])
    return rec


def probe_arxiv(query: str, max_results: int = 12) -> Dict[str, Any]:
    b = BUDGETS["arxiv"]
    url = ("http://export.arxiv.org/api/query?"
           + urllib.parse.urlencode({"search_query": query, "start": 0,
                                     "max_results": max_results,
                                     "sortBy": "submittedDate", "sortOrder": "descending"}))
    rec = _get(url)
    rec["documented_limit"] = b["documented"]
    rec["budget"] = "{} request(s), min interval {} s".format(b["max_requests"], b["min_interval_s"])
    items: List[Dict[str, str]] = []
    body = rec.pop("_body", None)
    if body:
        ns = {"a": "http://www.w3.org/2005/Atom"}
        try:
            root = ET.fromstring(body)
            for e in root.findall("a:entry", ns):
                def _t(tag: str) -> str:
                    n = e.find("a:" + tag, ns)
                    return (n.text or "").strip().replace("\n", " ") if n is not None else ""
                items.append({"id": _t("id"), "title": " ".join(_t("title").split()),
                              "abstract": " ".join(_t("summary").split()),
                              "published": _t("published"), "url": _t("id")})
        except ET.ParseError as e:
            rec["parse_error"] = str(e)[:200]
    rec["items_returned"] = len(items)
    rec["items"] = items
    return rec


def main(argv: List[str]) -> int:
    # D-23: this writes a file, so it is mutating work.
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    from archaeon.workspace import assert_not_canonical
    ws = assert_not_canonical("an Eos upstream probe", allow_override=False)

    out = REPO / "roles" / "Eos" / "intake" / "probe_arxiv.json"
    queries = ["cat:cs.NE AND abs:\"quality diversity\"", "cat:cs.LG AND abs:\"program synthesis\""]
    records = []
    for i, q in enumerate(queries[: BUDGETS["arxiv"]["max_requests"]]):
        if i:
            time.sleep(BUDGETS["arxiv"]["min_interval_s"])
        r = probe_arxiv(q)
        r["query"] = q
        records.append(r)
        print("probe {!r}: status={} items={} latency={}ms".format(
            q, r.get("status"), r.get("items_returned"), r.get("latency_ms")))

    payload = {"written_at": _now(), "workspace": ws, "observer": OBSERVER, "records": records}
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=2)
        fh.flush()
    print("wrote", out.relative_to(REPO))
    live = [r for r in records if r.get("status") == 200 and r.get("items_returned", 0) > 0]
    print("UPSTREAM LIVENESS:", "LIVE" if live else "NOT LIVE -- do not launch (base rule 9)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
