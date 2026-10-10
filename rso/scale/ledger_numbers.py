"""Measured numbers from RSO attempted-run ledgers (C-013-T020, for Workstream A / C-013-T030).

Read-only. Reads one or more ledger stores in the format of rso/slice001/ledger.py (START / END / REFUSED
JSONL rows) and prints, per store: launches by kind, END statuses, INTERRUPTED (START without END),
REFUSED rows, CPU-s by launch kind, artifact bytes, and wall time per TOP_LEVEL launch (START -> its own END,
or -> the latest END of its children when the TOP_LEVEL row carries none), plus the store's span.

Totals for usage (launches, cpu_s, artifact_bytes) use the same rules as Ledger.usage() and are cross-checked
against it when rso.slice001.ledger is importable; a mismatch is reported, never reconciled silently.

    python -B -m rso.scale.ledger_numbers rso/slice001/s2/LEDGER.jsonl rso/binding/LEDGER.jsonl \
        rso/witness/LEDGER.jsonl [--json]
"""
import argparse
import json
import statistics
import sys
from datetime import datetime, timezone


def _t(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def read_rows(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except ValueError:
            if i == len(lines) - 1 or all(not x.strip() for x in lines[i + 1:]):
                continue  # torn tail, tolerated as in ledger.py
            raise
    return rows


def numbers(rows):
    starts, ends, refused = {}, {}, []
    for r in rows:
        k = r.get("kind")
        if k == "START":
            starts[r["run_id"]] = r
        elif k == "END":
            ends[r["run_id"]] = r
        elif k == "REFUSED":
            refused.append(r)
    by_kind = {}
    statuses = {}
    cpu_by_kind = {}
    bytes_total = 0
    cpu_total = 0.0
    interrupted = 0
    for rid, s in starts.items():
        lk = s.get("launch_kind", "TOP_LEVEL")
        by_kind[lk] = by_kind.get(lk, 0) + 1
        e = ends.get(rid)
        if e is None:
            interrupted += 1
            statuses["INTERRUPTED"] = statuses.get("INTERRUPTED", 0) + 1
            continue
        statuses[e["status"]] = statuses.get(e["status"], 0) + 1
        c = float(e.get("cpu_s") or 0.0)
        cpu_total += c
        cpu_by_kind[lk] = cpu_by_kind.get(lk, 0.0) + c
        bytes_total += int(e.get("artifact_bytes") or 0)
    # wall time per TOP_LEVEL launch
    children_end = {}
    for rid, s in starts.items():
        p = s.get("parent_run_id")
        if p and rid in ends:
            t = _t(ends[rid]["end_utc"])
            if p not in children_end or t > children_end[p]:
                children_end[p] = t
    walls = []
    for rid, s in starts.items():
        if s.get("launch_kind", "TOP_LEVEL") != "TOP_LEVEL":
            continue
        t0 = _t(s["start_utc"])
        t1 = _t(ends[rid]["end_utc"]) if rid in ends else children_end.get(rid)
        if t1 is not None:
            walls.append((t1 - t0).total_seconds())
    times = [_t(s["start_utc"]) for s in starts.values()] + [_t(e["end_utc"]) for e in ends.values()]
    return {
        "rows": len(rows),
        "starts_by_launch_kind": dict(sorted(by_kind.items())),
        "top_level_launches": by_kind.get("TOP_LEVEL", 0),
        "end_status": dict(sorted(statuses.items())),
        "interrupted": interrupted,
        "refused": len(refused),
        "cpu_s_total": round(cpu_total, 1),
        "cpu_s_by_launch_kind": {k: round(v, 1) for k, v in sorted(cpu_by_kind.items())},
        "artifact_bytes": bytes_total,
        "top_level_wall_s": {
            "n": len(walls),
            "sum": round(sum(walls), 1),
            "median": round(statistics.median(walls), 1) if walls else None,
            "max": round(max(walls), 1) if walls else None,
        },
        "span_utc": [min(times).strftime("%Y-%m-%dT%H:%M:%SZ"), max(times).strftime("%Y-%m-%dT%H:%M:%SZ")]
        if times else None,
    }


def crosscheck(path, n):
    try:
        from rso.slice001 import ledger as L
    except ImportError:
        return "SKIPPED (rso.slice001.ledger not importable)"
    u = L.Ledger.from_contract(path, L.DEFAULT_CONTRACT).usage()
    ok = (u["launches"] == n["top_level_launches"] and u["artifact_bytes"] == n["artifact_bytes"]
          and abs(u["cpu_s"] - n["cpu_s_total"]) < 0.5)
    return "MATCH" if ok else "MISMATCH ledger.usage()=%s" % json.dumps(u, sort_keys=True)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -B -m rso.scale.ledger_numbers")
    ap.add_argument("stores", nargs="+")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    out = {}
    for p in a.stores:
        n = numbers(read_rows(p))
        n["crosscheck_ledger_usage"] = crosscheck(p, n)
        out[p] = n
    if a.json:
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0
    hdr = "%-30s %6s %6s %9s %8s %12s %9s %9s %9s %-6s" % (
        "store", "top", "rows", "cpu_s", "cpu_min", "art_bytes", "wall_sum", "wall_med", "wall_max", "check")
    print(hdr)
    for p, n in out.items():
        w = n["top_level_wall_s"]
        print("%-30s %6d %6d %9.1f %8.1f %12d %9s %9s %9s %-6s" % (
            p, n["top_level_launches"], n["rows"], n["cpu_s_total"], n["cpu_s_total"] / 60.0, n["artifact_bytes"],
            w["sum"], w["median"], w["max"], n["crosscheck_ledger_usage"][:6]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
