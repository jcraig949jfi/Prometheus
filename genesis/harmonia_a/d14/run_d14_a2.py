#!/usr/bin/env python
"""D-14 measurement runner under AMENDMENTS A1+A2. Deterministic; no LLM.
Resumable: per-parent incremental persistence (a2_progress.jsonl);
re-launch skips completed parents. Verdict logic: analyze_d14_a2.py."""

import base64
import hashlib
import json
import os
import ssl
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, r"D:\ZeusE\d12\client")
from remote import FoundryClient

D13_PIN = ("50b5c2327c64bf112c635ca1487f2b1a"
           "8fd64e1b7faade9476d5dfa7215fd492")
BASE = "https://192.168.1.202:8799"
PARENT_SEEDS = list(range(910001, 910201))      # 200 seeds (A2 R3)
K_MUT = 96                                       # 1..96 (A2 R3)
OPCFG = {"operator_id": "stackvm.point_indel.v1",
         "parameters": {"p_point": 1.0, "p_insert": 0.0,
                        "p_delete": 0.0, "p_dup_block": 0.0,
                        "max_point_sites": 1}}
# NOTE (A2 R1): the instrument ignores this config (defect filed);
# it is still sent so the request record matches A1 exactly.
OUT = Path("results")
JOURNAL = Path("JOURNAL.jsonl")


def journal(entry):
    entry.setdefault("t_utc", time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                            time.gmtime()))
    with JOURNAL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")


CALLS = 0


def guarded(fc, fn, *a, **kw):
    global CALLS
    CALLS += 1
    if CALLS % 25 == 0:
        fc._release_checked = False
        fc.check_release()
    return fn(*a, **kw)


def main():
    OUT.mkdir(exist_ok=True)
    ctx = ssl.create_default_context(cafile=os.environ["FOUNDRY_M1_CERT"])
    fc = FoundryClient(BASE, token=os.environ["FOUNDRY_ADMIN_TOKEN"],
                       expected_release_hash=D13_PIN, tls_context=ctx,
                       timeout_s=120.0)
    v = fc.check_release()
    journal({"kind": "gate", "op": "check_release", "result": "match",
             "source_tree_hash": v.get("source_tree_hash")})

    rng = np.random.default_rng(np.random.SeedSequence([20260914]))
    cases = [[int(x) for x in rng.integers(0, 256, size=4)]
             for _ in range(8)]
    task_ids = []
    for i, c in enumerate(cases):
        t = guarded(fc, fc.post, "/v0/tasks",
                    {"train_cases": [[c, [0]]]},
                    trace_id=f"d14a2-task-{i}")
        task_ids.append(t["task_id"])
    tc = guarded(fc, fc.post, "/v0/tasks",
                 {"train_cases": [[c, [0]] for c in cases]},
                 trace_id="d14a2-task-comb")
    task_comb = tc["task_id"]

    done = set()
    prog = OUT / "a2_progress.jsonl"
    if prog.exists():
        for line in open(prog):
            done.add(json.loads(line)["pseed"])
        print(f"RESUME: {len(done)} parents already persisted",
              flush=True)

    def geno(aid):
        g = guarded(fc, fc.get, f"/v0/artifacts/{aid}/genotype")
        return base64.b64decode(g["genotype_b64"])

    def ev_hash(aid, tid):
        r = guarded(fc, fc.post, "/v0/evaluate",
                    {"artifact_id": aid, "task_id": tid, "seed": 0},
                    trace_id="d14a2-ev")
        res = r["result"]
        return res["output_hash"], res["failure"]["kind"]

    controls_path = OUT / "a2_controls.json"
    controls = (json.load(open(controls_path))
                if controls_path.exists() else
                {"c1_replay_eval": None, "c1_replay_mutate": None,
                 "c2_noop_bad": 0, "c5_handcheck": []})
    t_start = time.time()
    n_sites_total = 0

    for pi, pseed in enumerate(PARENT_SEEDS):
        if pseed in done:
            continue
        parent_sites, parent_kids = [], []
        a = guarded(fc, fc.post, "/v0/artifacts",
                    {"engine_id": "stackvm-v1", "op": "create_random",
                     "seed": pseed}, trace_id=f"d14a2-p-{pseed}")
        pid = a["artifact_id"]
        gp = geno(pid)
        if len(controls["c5_handcheck"]) < 5:
            controls["c5_handcheck"].append(dict(
                artifact=pid,
                match=a["genotype_addr"].endswith(
                    hashlib.sha256(gp).hexdigest())))       # A2 R2
        p_comb, p_fail = ev_hash(pid, task_comb)
        if p_fail != "none":
            parent_kids.append(dict(parent=pid, pseed=pseed,
                                    note="parent_faulted",
                                    fail=p_fail))
        else:
            p_case = [ev_hash(pid, t)[0] for t in task_ids]
            if controls["c1_replay_eval"] is None:
                p2, _ = ev_hash(pid, task_comb)
                controls["c1_replay_eval"] = bool(p2 == p_comb)
            seen_sites = {}
            for k in range(1, K_MUT + 1):
                m = guarded(fc, fc.post, "/v0/artifacts",
                            {"engine_id": "stackvm-v1", "op": "mutate",
                             "seed": k, "parent_ids": [pid],
                             "config": OPCFG},
                            trace_id=f"d14a2-m-{pseed}-{k}")
                cid = m["artifact_id"]
                if controls["c1_replay_mutate"] is None:
                    m2 = guarded(fc, fc.post, "/v0/artifacts",
                                 {"engine_id": "stackvm-v1",
                                  "op": "mutate", "seed": k,
                                  "parent_ids": [pid],
                                  "config": OPCFG},
                                 trace_id=f"d14a2-m-{pseed}-{k}-r")
                    controls["c1_replay_mutate"] = bool(
                        m2["artifact_id"] == cid)
                gc = geno(cid)
                if len(gc) != len(gp):
                    parent_kids.append(dict(parent=pid, pseed=pseed,
                                            k=k, child=cid,
                                            excl="length_changed"))
                    continue
                diff = [i for i in range(len(gp)) if gp[i] != gc[i]]
                if len(diff) == 0:
                    h, _f = ev_hash(cid, task_comb)
                    if h != p_comb:
                        controls["c2_noop_bad"] += 1
                    parent_kids.append(dict(parent=pid, pseed=pseed,
                                            k=k, child=cid,
                                            excl="diff0_noop",
                                            noop_ok=bool(h == p_comb)))
                    continue
                if len(diff) > 1:
                    parent_kids.append(dict(parent=pid, pseed=pseed,
                                            k=k, child=cid,
                                            excl="multisite_default_"
                                                 "sampler",
                                            diff_count=len(diff)))
                    continue
                site = diff[0]
                parent_kids.append(dict(parent=pid, pseed=pseed, k=k,
                                        child=cid, site=site))
                if site in seen_sites:
                    continue                        # first-hit rule
                h_comb, f_comb = ev_hash(cid, task_comb)
                if f_comb != "none":
                    seen_sites[site] = "FAULT"
                    parent_sites.append(dict(parent=pid, pseed=pseed,
                                             site=site, k=k,
                                             child=cid, cls="FAULT",
                                             fail=f_comb))
                    continue
                if h_comb == p_comb:
                    infl = 0.0
                else:
                    changed = 0
                    faulted = False
                    for i, t in enumerate(task_ids):
                        h, f = ev_hash(cid, t)
                        if f != "none":
                            faulted = True
                            break
                        if h != p_case[i]:
                            changed += 1
                    if faulted:
                        seen_sites[site] = "FAULT"
                        parent_sites.append(dict(parent=pid,
                                                 pseed=pseed,
                                                 site=site, k=k,
                                                 child=cid,
                                                 cls="FAULT"))
                        continue
                    infl = changed / 8.0
                seen_sites[site] = infl
                parent_sites.append(dict(parent=pid, pseed=pseed,
                                         site=site, k=k, child=cid,
                                         influence=infl))
        with (OUT / "a2_sites.jsonl").open("a") as f:
            for r in parent_sites:
                f.write(json.dumps(r, sort_keys=True) + "\n")
        with (OUT / "a2_children.jsonl").open("a") as f:
            for r in parent_kids:
                f.write(json.dumps(r, sort_keys=True) + "\n")
        with prog.open("a") as f:
            f.write(json.dumps({"pseed": pseed}) + "\n")
        json.dump(controls, open(controls_path, "w"), indent=1)
        n_sites_total += len(parent_sites)
        if (pi + 1) % 10 == 0:
            print(f"parent {pi+1}/{len(PARENT_SEEDS)} "
                  f"new_sites={n_sites_total} calls={CALLS} "
                  f"{round(time.time()-t_start,0)}s", flush=True)

    json.dump(dict(controls=controls, n_calls_this_session=CALLS,
                   cases=cases, task_ids=task_ids,
                   task_combined=task_comb,
                   wall_s=round(time.time() - t_start, 1)),
              open(OUT / "a2_run_meta.json", "w"), indent=1)
    journal({"kind": "a2_measurement_complete",
             "controls_summary": {k: (v if not isinstance(v, list)
                                      else "see meta")
                                  for k, v in controls.items()}})
    print("DONE")


if __name__ == "__main__":
    main()
