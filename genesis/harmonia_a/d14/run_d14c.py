#!/usr/bin/env python
"""D-14C runner + frozen adjudication, per FREEZE_D14C.txt.
Comparator translation: output-hash -> state tuple (output_hash,
behavior vector, resource steps) on the original 8-case battery,
same persisted pairs. Resumable per site. Deterministic; no LLM."""

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

    rng8 = np.random.default_rng(np.random.SeedSequence([20260914]))
    cases8 = [[int(x) for x in rng8.integers(0, 256, size=4)]
              for _ in range(8)]
    t8 = [guarded(fc, fc.post, "/v0/tasks", {"train_cases": [[c, [0]]]},
                  trace_id=f"d14c-t8-{i}")["task_id"]
          for i, c in enumerate(cases8)]

    def tuples(aid):
        out = []
        for t in t8:
            r = guarded(fc, fc.post, "/v0/evaluate",
                        {"artifact_id": aid, "task_id": t, "seed": 0},
                        trace_id="d14c-ev")["result"]
            if r["failure"]["kind"] != "none":
                return None
            out.append((r["output_hash"],
                        tuple(r["behavior"]),
                        r["resources"]["steps"]))
        return out

    sites = [json.loads(l) for l in open("results/a2_sites.jsonl")]
    done = set()
    c_path = OUT / "c_sites.jsonl"
    if c_path.exists():
        for line in open(c_path):
            r = json.loads(line)
            done.add((r["parent"], r["site"]))
        print(f"RESUME: {len(done)} sites done", flush=True)

    parent_cache = {}
    replay_ok = None
    n_done = 0
    t0 = time.time()
    with c_path.open("a") as outfh:
        for s in sites:
            if "influence" not in s:
                continue                      # FAULT-class in A2: skip
            key = (s["parent"], s["site"])
            if key in done:
                continue
            pid, cid = s["parent"], s["child"]
            if pid not in parent_cache:
                parent_cache[pid] = tuples(pid)
            pt = parent_cache[pid]
            if pt is None:
                row = dict(parent=pid, site=s["site"], child=cid,
                           status="parent_faulted")
            else:
                if replay_ok is None:
                    replay_ok = bool(tuples(pid) == pt)
                    journal({"kind": "d14c_c1_replay", "ok": replay_ok})
                ct = tuples(cid)
                if ct is None:
                    row = dict(parent=pid, site=s["site"], child=cid,
                               status="FAULT", i8_a2=s["influence"])
                else:
                    out_diff = sum(1 for i in range(8)
                                   if ct[i][0] != pt[i][0])
                    st_diff = sum(1 for i in range(8)
                                  if ct[i] != pt[i])
                    hidden = sum(1 for i in range(8)
                                 if ct[i][0] == pt[i][0]
                                 and ct[i] != pt[i])
                    row = dict(parent=pid, site=s["site"], child=cid,
                               status="ok", i8_a2=s["influence"],
                               i_out=out_diff / 8.0,
                               i_state=st_diff / 8.0,
                               hidden_cases=hidden)
            outfh.write(json.dumps(row, sort_keys=True) + "\n")
            outfh.flush()
            n_done += 1
            if n_done % 100 == 0:
                print(f"{n_done} sites  calls={CALLS} "
                      f"{round(time.time()-t0,0)}s", flush=True)

    rows = [json.loads(l) for l in open(c_path)]
    ok = [r for r in rows if r["status"] == "ok"]
    c2_bad = sum(1 for r in ok if r["i_out"] != r["i8_a2"])
    mig = defaultdict(int)
    for r in ok:
        mig[(binof(r["i_out"]), binof(r["i_state"]))] += 1
    z_out = [r for r in ok if r["i_out"] == 0]
    e2 = (sum(1 for r in z_out if 0 < r["i_state"] <= 0.25)
          / len(z_out)) if z_out else None
    e3 = sum(1 for r in ok if 0 < r["i_state"] <= 0.25) / len(ok)
    e4_overall = sum(r["hidden_cases"] for r in ok) / (8.0 * len(ok))
    support_ok = (len(ok) >= 1400 and replay_ok and c2_bad == 0)
    if not support_ok:
        verdict = "D14C_INDETERMINATE"
    elif e3 <= 0.05 and (e2 is None or e2 <= 0.05):
        verdict = "COMPARATOR_STABLE"
    else:
        verdict = "COMPARATOR_DEPENDENT"
    report = dict(
        n_ok=len(ok),
        migration={f"{a}->{b}": v for (a, b), v in sorted(mig.items())},
        E2_danger=round(e2, 6) if e2 is not None else None,
        E3_middle_state=round(e3, 6),
        E4_reconvergence_rate=round(e4_overall, 6),
        controls=dict(c1_replay=replay_ok, c2_consistency_bad=c2_bad),
        support_ok=bool(support_ok), verdict=verdict)
    json.dump(report, open(OUT / "analysis_d14c.json", "w"), indent=1)
    journal({"kind": "d14c_complete", "verdict": verdict,
             "E2": report["E2_danger"],
             "E3": report["E3_middle_state"],
             "E4": report["E4_reconvergence_rate"]})
    print(json.dumps(report, indent=1))
    print("VERDICT:", verdict)


if __name__ == "__main__":
    main()
