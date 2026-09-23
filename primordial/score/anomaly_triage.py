"""Anomaly triage (backlog S2): age, children and cohort for every open anomaly, plus the D-share rule.

Inputs are the anomaly records and status events in the bus export (pm_anomalies): each filed
anomaly (id, lane, ts, source) and each status event (id, status, ts, exp_id). Parents are
`ANOM-<id>` identifiers in an anomaly's `source` field. Subjects and observations are never read.

Epochs: 30-minute windows (EPOCH_S) from the round start, by default the first cohort (B-E) hello
at or after ROUND2_START in the swarm export, through the last cohort message.

At the end of each epoch:
  open        anomalies filed before the end whose latest status event before the end is not
              RESOLVED / REFUTED (an INDETERMINATE close leaves it open)
  resolved    RESOLVED / REFUTED events inside the epoch
  rule        RAISE_D when open > RULE_FACTOR x resolved (operator/backlog: "D's share rises when
              OPEN > 2x RESOLVED per epoch")
  triage      open anomalies ordered by children (more first), then age (older first), then id

When the rule fires, `proposal` moves D_STEP of the split from B (exploitation) to D. The split
belongs to the operator; this is a computed proposal the conductor can enforce once the operator
adopts the step, never a change made here.

    python -m primordial.score.anomaly_triage [--write]
"""
from __future__ import annotations

import argparse
import math
import re

from primordial.score.round2 import DATE, EXPORT, ROOT, ROUND2_START, jsonl

EPOCH_S = 1800.0
RULE_FACTOR = 2.0
D_STEP = 0.05
CLOSED = ("RESOLVED", "REFUTED")
COHORT_LANES = ("B", "C", "D", "E")
SHARES = {"B": 0.40, "C": 0.25, "D": 0.20, "E": 0.15}
OUT = ROOT / "primordial" / "ledger" / "rows" / "H" / "S2-anomaly-triage-r2.jsonl"


def split_records(records: list[dict]) -> tuple[dict, list]:
    filed = {a["id"]: a for a in records if not a.get("event")}
    events = sorted((a for a in records if a.get("event")), key=lambda a: float(a["ts"]))
    return filed, events


def parents(a: dict, ids) -> list[str]:
    return [p for p in re.findall(r"ANOM-(\d+-\d+)", str(a.get("source", ""))) if p in ids and p != a["id"]]


def status_at(aid: str, t: float, events: list) -> str:
    st = "OPEN"
    for e in events:
        if e["id"] == aid and float(e["ts"]) < t:
            st = e["status"]
    return st


def epoch_report(filed: dict, events: list, t0: float, t1: float) -> dict:
    live = {aid: a for aid, a in filed.items() if float(a["ts"]) < t1}
    open_ids = [aid for aid in live if status_at(aid, t1, events) not in CLOSED]
    resolved = [e["id"] for e in events if t0 <= float(e["ts"]) < t1 and e["status"] in CLOSED]
    kids = {aid: [c for c, a in live.items() if aid in parents(a, filed)] for aid in live}
    triage = sorted(({"id": aid, "cohort": live[aid]["lane"], "age_s": round(t1 - float(live[aid]["ts"]), 3),
                      "children": len(kids[aid]), "parents": parents(live[aid], filed)} for aid in open_ids),
                    key=lambda x: (-x["children"], -x["age_s"], x["id"]))
    fired = len(open_ids) > RULE_FACTOR * len(resolved)
    return {"window": [t0, t1], "open": len(open_ids), "resolved": len(resolved), "resolved_ids": resolved,
            "rule": "RAISE_D" if fired else "HOLD", "triage": triage}


def proposal(shares=SHARES, step=D_STEP) -> dict:
    s = dict(shares)
    moved = min(step, s["B"])
    s["B"], s["D"] = round(s["B"] - moved, 4), round(s["D"] + moved, 4)
    return s


def round_window(swarm: list[dict]) -> tuple[float, float]:
    cohort = [float(m["ts"]) for m in swarm if m.get("lane") in COHORT_LANES and float(m["ts"]) >= ROUND2_START]
    starts = [float(m["ts"]) for m in swarm if m.get("lane") in COHORT_LANES and m.get("kind") == "hello"
              and float(m["ts"]) >= ROUND2_START]
    return min(starts), max(cohort)


def triage(export=EXPORT, start: float | None = None, end: float | None = None) -> dict:
    records = jsonl(f"{export}/pm_anomalies_{DATE}.jsonl")
    if start is None or end is None:
        s0, e0 = round_window(jsonl(f"{export}/pm_swarm_{DATE}.jsonl"))
        start, end = start if start is not None else s0, end if end is not None else e0
    filed, events = split_records(records)
    n = max(1, math.ceil((end - start) / EPOCH_S))
    epochs = []
    for i in range(n):
        rep = epoch_report(filed, events, start + i * EPOCH_S, start + (i + 1) * EPOCH_S)
        rep["epoch"] = i + 1
        epochs.append(rep)
    fired = [e["epoch"] for e in epochs if e["rule"] == "RAISE_D"]
    return {"start": start, "end": end, "epoch_s": EPOCH_S, "rule_factor": RULE_FACTOR, "epochs": epochs,
            "raise_d_epochs": fired, "proposal": proposal() if fired else None}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", default=str(EXPORT))
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    out = triage(a.export)
    for e in out["epochs"]:
        head = ", ".join(f"{x['id']}({x['cohort']} c{x['children']} {x['age_s'] / 60:.0f}m)" for x in e["triage"][:4])
        print(f"epoch {e['epoch']}: open {e['open']} resolved {e['resolved']} -> {e['rule']}; top: {head}")
    print("proposal", out["proposal"])
    if a.write:
        if OUT.exists():
            print(f"{OUT.relative_to(ROOT).as_posix()} exists; rows are append-only, not rewritten")
            return 1
        from primordial.fabric.rows import RowWriter
        with RowWriter(OUT, "S2-anomaly-triage-r2", commit_every_s=10**9) as w:
            for e in out["epochs"]:
                w.write({"kind": "anomaly_triage_epoch", "status": "record", **e})
            w.write({"kind": "anomaly_triage_round", "status": "record",
                     **{k: v for k, v in out.items() if k != "epochs"}})
        print(f"wrote {OUT.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
