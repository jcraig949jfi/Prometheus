#!/usr/bin/env python
"""D-14B runner + frozen adjudication, per FREEZE_D14B.txt.
Same persisted pairs; battery 8 -> 64 (nested). Resumable per site.
Deterministic; no LLM."""

import json
import os
import ssl
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, r"D:\ZeusE\d12\client")
from remote import FoundryClient

D13_PIN = ("50b5c2327c64bf112c635ca1487f2b1a"
           "8fd64e1b7faade9476d5dfa7215fd492")
BASE = "https://192.168.1.202:8799"
OUT = Path("results")
JOURNAL = Path("JOURNAL.jsonl")
CALLS = 0


def journal(entry):
    entry.setdefault("t_utc", time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                            time.gmtime()))
    with JOURNAL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")


def guarded(fc, fn, *a, **kw):
    global CALLS
    CALLS += 1
    if CALLS % 25 == 0:
        fc._release_checked = False
        fc.check_release()
    return fn(*a, **kw)


def binof(v):
    if v == 0:
        return "zero"
    return "middle" if v <= 0.25 else "high"


def main():
    ctx = ssl.create_default_context(cafile=os.environ["FOUNDRY_M1_CERT"])
    fc = FoundryClient(BASE, token=os.environ["FOUNDRY_ADMIN_TOKEN"],
                       expected_release_hash=D13_PIN, tls_context=ctx,
                       timeout_s=120.0)
    fc.check_release()

    # nested battery: 8 A2 cases + 56 new
    rng8 = np.random.default_rng(np.random.SeedSequence([20260914]))
    cases8 = [[int(x) for x in rng8.integers(0, 256, size=4)]
              for _ in range(8)]
    rng56 = np.random.default_rng(np.random.SeedSequence([20260916]))
    cases56 = [[int(x) for x in rng56.integers(0, 256, size=4)]
               for _ in range(56)]
    t8 = [guarded(fc, fc.post, "/v0/tasks", {"train_cases": [[c, [0]]]},
                  trace_id=f"d14b-t8-{i}")["task_id"]
          for i, c in enumerate(cases8)]
    t56 = [guarded(fc, fc.post, "/v0/tasks", {"train_cases": [[c, [0]]]},
                   trace_id=f"d14b-t56-{i}")["task_id"]
           for i, c in enumerate(cases56)]
    tc56 = guarded(fc, fc.post, "/v0/tasks",
                   {"train_cases": [[c, [0]] for c in cases56]},
                   trace_id="d14b-tc56")["task_id"]

    def ev(aid, tid):
        r = guarded(fc, fc.post, "/v0/evaluate",
                    {"artifact_id": aid, "task_id": tid, "seed": 0},
                    trace_id="d14b-ev")
        res = r["result"]
        return res["output_hash"], res["failure"]["kind"]

    sites = [json.loads(l) for l in open("results/a2_sites.jsonl")]
    done = {}
    b_path = OUT / "b_sites.jsonl"
    if b_path.exists():
        for line in open(b_path):
            r = json.loads(line)
            done[(r["parent"], r["site"])] = True
        print(f"RESUME: {len(done)} sites done", flush=True)

    # per-parent 64-case hashes (cached per parent)
    parent_cache = {}

    def parent_hashes(pid):
        if pid in parent_cache:
            return parent_cache[pid]
        h8 = [ev(pid, t)[0] for t in t8]
        h56 = [ev(pid, t)[0] for t in t56]
        hc56, pf = ev(pid, tc56)
        parent_cache[pid] = (h8, h56, hc56, pf)
        return parent_cache[pid]

    replay_ok = None
    n_done = 0
    t0 = time.time()
    with b_path.open("a") as outfh:
        for s in sites:
            key = (s["parent"], s["site"])
            if key in done:
                continue
            pid, cid = s["parent"], s["child"]
            h8p, h56p, hc56p, pf = parent_hashes(pid)
            if replay_ok is None:
                h2, _ = ev(pid, tc56)
                replay_ok = bool(h2 == hc56p)
                journal({"kind": "d14b_c1_replay", "ok": replay_ok})
            if pf != "none":
                row = dict(parent=pid, site=s["site"], child=cid,
                           status="parent_faulted_64")
            else:
                hc56c, cf = ev(cid, tc56)
                if cf != "none":
                    row = dict(parent=pid, site=s["site"], child=cid,
                               status="FAULT64",
                               i8=s.get("influence"))
                elif (hc56c == hc56p
                      and s.get("influence") == 0.0):
                    # unchanged on new 56 and unchanged on old 8
                    row = dict(parent=pid, site=s["site"], child=cid,
                               status="ok", i8=0.0, i64=0.0,
                               changed8=0, changed56=0)
                else:
                    ch8 = 0
                    ch56 = 0
                    fault = False
                    for i, t in enumerate(t8):
                        h, f = ev(cid, t)
                        if f != "none":
                            fault = True
                            break
                        if h != h8p[i]:
                            ch8 += 1
                    if not fault:
                        if hc56c == hc56p:
                            ch56 = 0
                        else:
                            for i, t in enumerate(t56):
                                h, f = ev(cid, t)
                                if f != "none":
                                    fault = True
                                    break
                                if h != h56p[i]:
                                    ch56 += 1
                    if fault:
                        row = dict(parent=pid, site=s["site"],
                                   child=cid, status="FAULT64",
                                   i8=s.get("influence"))
                    else:
                        row = dict(parent=pid, site=s["site"],
                                   child=cid, status="ok",
                                   i8=s.get("influence"),
                                   i64=(ch8 + ch56) / 64.0,
                                   changed8=ch8, changed56=ch56)
            outfh.write(json.dumps(row, sort_keys=True) + "\n")
            outfh.flush()
            n_done += 1
            if n_done % 100 == 0:
                print(f"{n_done} sites  calls={CALLS} "
                      f"{round(time.time()-t0,0)}s", flush=True)

    # ---------------- frozen adjudication
    rows = [json.loads(l) for l in open(b_path)]
    ok = [r for r in rows if r["status"] == "ok"
          and r.get("i8") is not None]
    # C2 nested consistency: for A2 CHANGED children we know i8*8
    c2_bad = sum(1 for r in ok
                 if r["i8"] > 0 and r["changed8"] != round(r["i8"] * 8))
    mig = defaultdict(int)
    for r in ok:
        mig[(binof(r["i8"]), binof(r["i64"]))] += 1
    zero8 = [r for r in ok if r["i8"] == 0]
    e2 = (sum(1 for r in zero8 if 0 < r["i64"] <= 0.25)
          / len(zero8)) if zero8 else None
    e3 = sum(1 for r in ok if 0 < r["i64"] <= 0.25) / len(ok)
    e4 = [dict(i8=r["i8"], i64=r["i64"]) for r in ok
          if 0 < r["i8"] <= 0.25]
    hist = defaultdict(int)
    for r in ok:
        hist[round(r["i64"], 6)] += 1
    support_ok = (len(ok) >= 1400 and replay_ok and c2_bad == 0)
    if not support_ok:
        verdict = "D14B_INDETERMINATE"
    elif e3 <= 0.05 and (e2 is None or e2 <= 0.05):
        verdict = "BATTERY_RESOLUTION_STABLE"
    else:
        verdict = "BATTERY_RESOLUTION_DEPENDENT"
    report = dict(
        n_common_ok=len(ok),
        migration={f"{a}->{b}": v for (a, b), v in sorted(mig.items())},
        E2_critical=round(e2, 6) if e2 is not None else None,
        E3_middle64=round(e3, 6),
        E4_a2_middle_sites=e4,
        i64_histogram=dict(sorted(hist.items())),
        controls=dict(c1_replay=replay_ok, c2_nested_bad=c2_bad),
        n_fault64=sum(1 for r in rows if r["status"] == "FAULT64"),
        support_ok=bool(support_ok), verdict=verdict)
    json.dump(report, open(OUT / "analysis_d14b.json", "w"), indent=1)
    journal({"kind": "d14b_complete", "verdict": verdict,
             "E2": report["E2_critical"], "E3": report["E3_middle64"]})
    print(json.dumps({k: v for k, v in report.items()
                      if k not in ("i64_histogram",
                                   "E4_a2_middle_sites")}, indent=1))
    print("E4 (A2 middle sites at 64):", e4)
    print("VERDICT:", verdict)


if __name__ == "__main__":
    main()
