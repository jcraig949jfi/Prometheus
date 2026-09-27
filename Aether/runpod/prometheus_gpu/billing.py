"""Provider billing, read-only, and reconciliation against run receipts.

RunPod exposes what it actually billed, per pod and per time bucket, at
`GET https://rest.runpod.io/v1/billing/pods` (qualified 2026-09-27 on this
account): each row carries `podId`, `amount` (USD), `timeBilledMs` and
`diskSpaceBilledGB`, bucketed by `time`. Account-level state is at GraphQL
`myself { clientBalance currentSpendPerHr spendLimit }`.

Until this module, every receipt said "measured wall time at a quoted
rate, not provider billing" and carried `billing_reconciled: false`. This
is the other half: it fetches what the provider billed and sets the two
side by side, per pod, without changing any receipt already written.

Nothing here can spend money or change provider state; every call is a
GET or a read-only GraphQL query. The credential comes from
`credentials.resolve()` and is never logged or returned.

Billing rows can lag the pod's termination (the provider aggregates into
buckets); `reconcile` therefore reports a pod with no billing row as
NOT_YET_BILLED, never as "free".
"""

import datetime as _dt
import glob
import json
import os

from . import credentials

REST = "https://rest.runpod.io/v1"
GRAPHQL = "https://api.runpod.io/graphql"


def _open(req, timeout=30):
    from urllib.request import build_opener, ProxyHandler
    return build_opener(ProxyHandler({})).open(req, timeout=timeout)


def _headers(key):
    from .provider import USER_AGENT
    return {"User-Agent": USER_AGENT, "Authorization": "Bearer " + key,
            "Accept": "application/json"}


def fetch_pod_billing(start_utc, end_utc=None, bucket="day", fetch=None):
    """List of billing rows from the provider. `fetch` is injectable for tests."""
    q = "bucketSize=%s&startTime=%s" % (bucket, start_utc)
    if end_utc:
        q += "&endTime=%s" % end_utc
    if fetch is not None:
        return fetch("/billing/pods?" + q)
    from urllib.request import Request
    key, _src = credentials.resolve()
    req = Request(REST + "/billing/pods?" + q, method="GET", headers=_headers(key))
    with _open(req) as r:
        return json.loads(r.read())


def account_state(fetch=None):
    """{clientBalance, currentSpendPerHr, spendLimit} from GraphQL."""
    query = "query { myself { clientBalance currentSpendPerHr spendLimit } }"
    if fetch is not None:
        return fetch(query)
    from urllib.request import Request
    key, _src = credentials.resolve()
    h = _headers(key)
    h["Content-Type"] = "application/json"
    req = Request(GRAPHQL, data=json.dumps({"query": query}).encode("utf-8"),
                  method="POST", headers=h)
    with _open(req) as r:
        return (json.loads(r.read()).get("data") or {}).get("myself") or {}


def billed_by_pod(rows):
    """{podId: {usd, billed_s, disk_gb_buckets, buckets}} summed over buckets."""
    out = {}
    for row in rows or []:
        pid = row.get("podId")
        if not pid:
            continue
        a = out.setdefault(pid, {"usd": 0.0, "billed_s": 0.0,
                                 "disk_gb_buckets": 0, "buckets": 0})
        a["usd"] += float(row.get("amount") or 0.0)
        a["billed_s"] += float(row.get("timeBilledMs") or 0) / 1000.0
        a["disk_gb_buckets"] += int(row.get("diskSpaceBilledGB") or 0)
        a["buckets"] += 1
    return out


def receipt_pods(receipt):
    """[(pod_id, hourly_usd, elapsed_s, usd_estimated, gpu)] for one receipt."""
    cost = receipt.get("cost") or {}
    pods = receipt.get("pods") or []
    rows = []
    for p in pods:
        pid = p.get("id") if isinstance(p, dict) else None
        if pid:
            rows.append((pid, cost.get("hourly_usd"), cost.get("elapsed_s"),
                         cost.get("usd_estimated"), receipt.get("gpu_used")))
    return rows


def reconcile(receipt_dir, billing_rows):
    """Per-pod table joining receipts to provider billing.

    Discrepancy is (billed - estimated). The billed-time columns separate
    the two usual sources: billed_s vs the receipt's elapsed_s (time the
    controller did not count: startup before RUNNING, the gap between
    the controller's terminate and the provider's stop, per-bucket
    rounding), and billed USD vs billed_s x quoted rate (a rate or a
    storage component the quote did not include).
    """
    billed = billed_by_pod(billing_rows)
    table = []
    seen = set()
    for path in sorted(glob.glob(os.path.join(receipt_dir, "*.json"))):
        try:
            with open(path, encoding="utf-8") as fh:
                rec = json.load(fh)
        except (OSError, ValueError):
            continue
        if not isinstance(rec, dict) or "cost" not in rec:
            continue
        for pid, rate, elapsed, est, gpu in receipt_pods(rec):
            if pid in seen:
                continue
            seen.add(pid)
            b = billed.get(pid)
            row = {"receipt": os.path.basename(path), "run_id": rec.get("run_id"),
                   "pod_id": pid, "gpu": gpu, "quote_usd_per_h": rate,
                   "receipt_elapsed_s": elapsed, "receipt_estimate_usd": est}
            if b is None:
                row["status"] = "NOT_YET_BILLED_OR_NOT_VISIBLE"
            else:
                row.update({
                    "status": "BILLED",
                    "billed_usd": round(b["usd"], 6),
                    "billed_s": round(b["billed_s"], 1),
                    "disk_gb_buckets": b["disk_gb_buckets"],
                    "discrepancy_usd": (round(b["usd"] - est, 6)
                                        if est is not None else None),
                    "billed_over_estimate": (round(b["usd"] / est, 4)
                                             if est else None),
                    "billed_s_over_elapsed": (round(b["billed_s"] / elapsed, 4)
                                              if elapsed else None),
                    "billed_usd_per_billed_h": (round(b["usd"] / (b["billed_s"] / 3600.0), 4)
                                                if b["billed_s"] else None),
                })
            table.append(row)
    unmatched = sorted(set(billed) - seen)
    return {"rows": table,
            "billed_pods_without_receipt": [
                {"pod_id": p, "billed_usd": round(billed[p]["usd"], 6),
                 "billed_s": round(billed[p]["billed_s"], 1)} for p in unmatched],
            "totals": {
                "receipt_estimate_usd": round(sum((r["receipt_estimate_usd"] or 0.0)
                                                  for r in table), 6),
                "billed_usd_matched": round(sum(r.get("billed_usd", 0.0)
                                                for r in table), 6),
                "billed_usd_unmatched": round(sum(billed[p]["usd"]
                                                  for p in unmatched), 6)}}


def utc_days_ago(days):
    t = _dt.datetime.utcnow() - _dt.timedelta(days=days)
    return t.strftime("%Y-%m-%dT00:00:00Z")
