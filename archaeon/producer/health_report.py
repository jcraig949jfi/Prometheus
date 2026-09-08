"""The program-health / monoculture report.

Challenge 3 says expansion recommendations must come from MEASUREMENT, not
taste. This is the measurement. It reads what crossed the canonical queue and
what PEW holds, computes diversity, and raises FLAGS -- each a number against a
stated threshold, never a verdict.

    python -m archaeon.producer.health_report --days 7

Flags are the only output that carries a recommendation, and each names the
lane it would fall to. A flag that fires is an entry for
roles/Archaeon/EXPANSIONS.md; a flag that later clears is the entry's closure.

Read-only. Nothing here writes to any table.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from typing import Any, Dict, List

from .. import vivqueue as vq

REPORT_VERSION = "archaeon.health.v0"

#: Thresholds. Named, explicit, and the only judgement in the file.
MONOCULTURE_SHARE = 0.80      # one kind/template above this share of rows
MIN_AXIS_ENTROPY_BITS = 1.0   # a parameter axis below this is effectively fixed
OUTCOME_STUCK_SHARE = 0.95    # one outcome above this share
EXEC_FAILURE_SHARE = 0.25     # failed / (completed+failed) above this


def _entropy_bits(counter: Counter) -> float:
    n = sum(counter.values())
    if n == 0:
        return 0.0
    return -sum((c / n) * math.log2(c / n) for c in counter.values() if c)


def gather(conn, days: int = 7, lane: str = "prod") -> Dict[str, Any]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT experiment_spec, source_evidence, status, source_reason
          FROM {q}
         WHERE created_at >= now() - (%s || ' days')::interval
           AND cadence_lane = %s
           AND status <> 'cancelled'
        """.format(q=str(vq.QUEUE)), (str(int(days)), lane))
    rows = cur.fetchall()

    kinds, templates, policies, statuses, reasons = (Counter() for _ in range(5))
    axes: Dict[str, Counter] = {}
    for spec, ev, status, reason in rows:
        spec = spec or {}
        ev = ev or {}
        kinds[(spec.get("work") or {}).get("kind", "<none>")] += 1
        templates[ev.get("template_id", "<none>")] += 1
        policies[ev.get("policy_version", "<none>")] += 1
        statuses[status] += 1
        reasons[reason] += 1
        payload = (spec.get("work") or {}).get("payload") or {}
        for k, v in payload.items():
            if k == "bits":
                continue                       # a 24-bit string is not an axis
            axes.setdefault("payload." + k, Counter())[str(v)] += 1
        w = spec.get("world") or {}
        if "seed_root" in w:
            axes.setdefault("world.seed_root", Counter())[str(w["seed_root"])] += 1

    cur.execute(
        """
        SELECT outcome, count(*) FROM ew.fossil_encounters
         WHERE namespace = 'prod'
           AND created_at >= now() - (%s || ' days')::interval
         GROUP BY outcome
        """, (str(int(days)),))
    outcomes = Counter({(o or "<null>"): int(n) for o, n in cur.fetchall()})

    return {"days": days, "lane": lane, "rows": len(rows),
            "kinds": kinds, "templates": templates, "policies": policies,
            "statuses": statuses, "reasons": reasons,
            "axes": {k: {"distinct": len(c), "entropy_bits": _entropy_bits(c)}
                     for k, c in axes.items()},
            "outcomes": outcomes}


def flags(g: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    n = g["rows"]

    def share(counter: Counter):
        if not n:
            return None, 0.0
        k, c = counter.most_common(1)[0]
        return k, c / n

    if n:
        k, s = share(g["kinds"])
        if s >= MONOCULTURE_SHARE:
            out.append({"flag": "KIND_MONOCULTURE", "value": s,
                        "threshold": MONOCULTURE_SHARE, "detail": k,
                        "lane": "archaeon+vivarium",
                        "unblocks": "a second executable kind / template"})
        # Rows with no template_id predate the registry (or came from a human
        # or another producer). They are UNTRACKED, not a template, and must
        # not be flagged as a monoculture of "<none>".
        tracked = Counter({k: v for k, v in g["templates"].items() if k != "<none>"})
        if tracked:
            k, c = tracked.most_common(1)[0]
            s = c / sum(tracked.values())
            if s >= MONOCULTURE_SHARE:
                out.append({"flag": "TEMPLATE_MONOCULTURE", "value": s,
                            "threshold": MONOCULTURE_SHARE, "detail": k,
                            "lane": "archaeon",
                            "unblocks": "admit a second template"})
        untracked = g["templates"].get("<none>", 0)
        if untracked:
            out.append({"flag": "UNTRACKED_TEMPLATE_ROWS", "value": untracked / n,
                        "threshold": 0.0, "detail": "{} rows without template_id"
                        .format(untracked), "lane": "archaeon",
                        "unblocks": "policy-by-template evaluation on these rows"})
        for axis, a in g["axes"].items():
            if a["entropy_bits"] < MIN_AXIS_ENTROPY_BITS:
                out.append({"flag": "AXIS_FIXED", "value": a["entropy_bits"],
                            "threshold": MIN_AXIS_ENTROPY_BITS, "detail": axis,
                            "lane": "archaeon",
                            "unblocks": "widen the template's space on this axis"})
        done = g["statuses"].get("completed", 0) + g["statuses"].get("failed", 0)
        if done:
            f = g["statuses"].get("failed", 0) / done
            if f >= EXEC_FAILURE_SHARE:
                out.append({"flag": "EXECUTION_FAILURE", "value": f,
                            "threshold": EXEC_FAILURE_SHARE,
                            "detail": "failed/(completed+failed)",
                            "lane": "vivarium",
                            "unblocks": "the endpoint counts executed experiments"})
    tot = sum(g["outcomes"].values())
    if tot:
        k, c = g["outcomes"].most_common(1)[0]
        if c / tot >= OUTCOME_STUCK_SHARE:
            out.append({"flag": "OUTCOME_STUCK", "value": c / tot,
                        "threshold": OUTCOME_STUCK_SHARE, "detail": k,
                        "lane": "harmonia+archaeon",
                        "unblocks": "an experiment family whose outcome can vary"})
    return out


def report(conn, days: int = 7, lane: str = "prod") -> Dict[str, Any]:
    g = gather(conn, days, lane)
    return {"report_version": REPORT_VERSION,
            "window_days": days, "lane": lane,
            "queue_rows": g["rows"],
            "kinds": dict(g["kinds"]), "templates": dict(g["templates"]),
            "policies": dict(g["policies"]), "statuses": dict(g["statuses"]),
            "source_reasons": dict(g["reasons"]),
            "axes": g["axes"], "pew_outcomes": dict(g["outcomes"]),
            "flags": flags(g),
            "authority": ("MEASUREMENTS against stated thresholds. A flag is a "
                          "recommendation addressed to a lane, never a verdict "
                          "about the science.")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="archaeon.producer.health_report")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--lane", default="prod")
    a = ap.parse_args(argv)
    from evidence_wiki.ew import db as ewdb
    conn = ewdb.connect()
    try:
        print(json.dumps(report(conn, a.days, a.lane), indent=2, default=str))
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
