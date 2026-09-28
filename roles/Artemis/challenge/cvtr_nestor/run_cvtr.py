"""CVT-R on Nestor's three genome sets (comms #802). Preregistration: PREREG_CVTR_NESTOR.md (this directory).

    python3 -B run_cvtr.py check    -> results/ADAPTER_CHECK.json   (design check; phase 1)
    python3 -B run_cvtr.py select   -> results/SELECTION.json       (the frozen genome list; no VM runs)
    python3 -B run_cvtr.py pilot    -> results/PILOT.json           (timing on 3 genomes; phase 1)
    python3 -B run_cvtr.py run      -> results/ROWS.jsonl, results/SUMMARY.json   (phase 2 ONLY)

At most 2 worker processes. Resumable: rows already in ROWS.jsonl are not recomputed.
"""
from __future__ import annotations

import json
import math
import multiprocessing as mp
import pathlib
import random
import sys
import time
import traceback

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import adapter as A  # noqa: E402

OUT = HERE / "results"
NP2 = A.CAMP / "npe-p2-endogenous-heredity-2026-09-27"
F16 = A.CAMP / "npe-arc3-2026-09-28" / "delegates" / "forensic_16000006"
SEED_B = "CVTR-NESTOR-802-b"
N_B = 100
K_P11 = 20
TAG_P11 = "CVTR-NESTOR-802-P11"
NPROC = 2


# ------------------------------------------------------------------ selection (frozen in the prereg)
def selection():
    out = []
    for sub in ("x_p2_bridge", "c_zero_specific"):
        for i, d in enumerate(json.loads((NP2 / sub / "DONORS.json").read_text())):
            out.append({"set": "a", "subset": sub, "idx": i, "vm": "DENSE", "cell": d["origin"], "hex": d["hex"],
                        "src": {"origin": d["origin"], "run_seed": d["run_seed"]}})
    rows = [json.loads(l) for l in (NP2 / "delegates" / "corpus" / "q1_partial.jsonl").read_text().splitlines() if l.strip()]
    comp = sorted((r for r in rows if r["rate_full"] >= 0.5), key=lambda r: (r["vm"], r["cell"], r["hex"]))
    pick = random.Random(SEED_B).sample(comp, N_B)
    for i, r in enumerate(pick):
        out.append({"set": "b", "subset": "q1_competent", "idx": i, "vm": r["vm"], "cell": r["cell"], "hex": r["hex"],
                    "src": {"rate_full": r["rate_full"], "rate_noself": r["rate_noself"], "origin_run": r["origin_run"],
                            "nocopy_donor": r["nocopy_donor"], "n_pool": len(comp)}})
    causal_b = {x["orig"]: x["ctrl"] for x in json.loads((F16 / "causal.json").read_text())["b"]}
    for i, p in enumerate(json.loads((F16 / "paths700.json").read_text())["paths"]):
        c = causal_b.get(p["genome"], {})
        out.append({"set": "c", "subset": "epoch700_modal", "idx": i, "vm": "DENSE", "cell": "7ae3", "hex": p["genome"],
                    "src": {"vid": p["vid"], "count700": p["count700"], "root_vid": p["root_vid"],
                            "forensic_FRESH": c.get("FRESH"), "forensic_FR": c.get("FR"),
                            "forensic_competent": c.get("competent")}})
    for e in out:
        e["key"] = "%s:%s:%d" % (e["set"], e["subset"], e["idx"])
    return out


# ------------------------------------------------------------------ one genome
def job(e):
    t0 = time.time()
    rec = {"key": e["key"], "set": e["set"], "subset": e["subset"], "vm": e["vm"], "cell": e["cell"], "hex": e["hex"],
           "src": e["src"]}
    try:
        G = bytes.fromhex(e["hex"])
        P = A.params(e["vm"], e["cell"])
        rec["params"] = P
        want_vm = "z8_dense_copy" if e["vm"] == "DENSE" else "z8"
        if P["vm_name"] != want_vm:
            raise RuntimeError("VM assignment wrong: %s" % P["vm_name"])
        if len(G) != P["n"]:
            raise RuntimeError("genome length %d != L %d" % (len(G), P["n"]))
        either, s0, s1 = A.p11_rates(e["vm"], e["cell"], G, (TAG_P11, e["hex"]), K_P11)
        rec["P11"] = {"rate_either": either, "rate_side0": s0, "rate_side1": s1, "certified": either >= 0.5,
                      "certified_sides": [s for s, v in ((0, s0), (1, s1)) if v >= 0.5]}
        if e["set"] == "b":
            q = A.q1_reproduce(G, e["vm"], e["cell"])
            rec["q1_reproduced"] = q
            rec["q1_match"] = abs(q - e["src"]["rate_full"]) < 1e-9
        cv = A.cvt_genome(e["vm"], e["cell"], G, e["hex"])
        rec["CVT"] = {str(s): v for s, v in cv.items()}
        acc = [s for s in (0, 1) if cv[s]["CVTR"]["accept"]]
        rec["CVTR_accept"] = bool(acc)
        rec["CVTR_sides"] = acc
        rec["CVTR_TB_max"] = max(cv[s]["CVTR"]["TB"] for s in (0, 1))
        rec["CVT2_accept"] = any(cv[s]["CVT2"]["accept"] for s in (0, 1))
        cs = rec["P11"]["certified_sides"]
        rec["CVTR_on_P11_side"] = any(cv[s]["CVTR"]["accept"] for s in cs) if cs else None
        rec["status"] = "SCORED" if (e["set"] != "b" or rec["q1_match"]) else "UNSCORABLE"
        if rec["status"] == "UNSCORABLE":
            rec["unscorable_reason"] = "q1 rate_full not reproduced (VM/cell/seed environment mismatch)"
    except Exception as ex:          # never dropped: reported as UNSCORABLE with the reason
        rec["status"] = "UNSCORABLE"
        rec["unscorable_reason"] = "%s: %s" % (type(ex).__name__, ex)
        rec["traceback"] = traceback.format_exc()[-2000:]
    rec["seconds"] = round(time.time() - t0, 2)
    return rec


# ------------------------------------------------------------------ statistics
def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)]


def summarize(recs):
    S = {}
    groups = {"a": ["a"], "a/x_p2_bridge": ["a", "x_p2_bridge"], "a/c_zero_specific": ["a", "c_zero_specific"],
              "b": ["b"], "b/DENSE": ["b", "DENSE"], "b/PLAIN": ["b", "PLAIN"], "c": ["c"]}
    for name, sel in groups.items():
        rows = [r for r in recs if r["set"] == sel[0] and (len(sel) == 1 or sel[1] in (r["subset"], r["vm"]))]
        sc = [r for r in rows if r["status"] == "SCORED"]
        k = sum(r["CVTR_accept"] for r in sc)
        cert = [r for r in sc if r["P11"]["certified"]]
        kc = sum(r["CVTR_accept"] for r in cert)
        S[name] = {"n_listed": len(rows), "n_unscorable": len(rows) - len(sc), "n_scored": len(sc),
                   "CVTR_accept": k, "CVTR_accept_rate": round(k / len(sc), 4) if sc else None,
                   "CVTR_wilson95": wilson(k, len(sc)),
                   "CVTR_accept_if_unscorable_all_accept": round((k + len(rows) - len(sc)) / len(rows), 4) if rows else None,
                   "CVTR_accept_if_unscorable_all_reject": round(k / len(rows), 4) if rows else None,
                   "P11_certified": len(cert), "CVTR_accept_among_P11_certified": kc,
                   "CVTR_rate_among_P11_certified": round(kc / len(cert), 4) if cert else None,
                   "CVTR_wilson95_among_P11_certified": wilson(kc, len(cert)),
                   "CVT2_accept": sum(r["CVT2_accept"] for r in sc)}
    fails = [{"key": r["key"], "hex": r["hex"], "vm": r["vm"], "cell": r["cell"], "P11": r["P11"],
              "CVTR_TB_max": r["CVTR_TB_max"], "CVT1_TB": {s: r["CVT"][s]["CVT1"]["TB"] for s in r["CVT"]},
              "CVT2_TB": {s: r["CVT"][s]["CVT2"]["TB"] for s in r["CVT"]}}
             for r in recs if r["status"] == "SCORED" and r["P11"]["certified"] and not r["CVTR_accept"]]
    side_fails = [r["key"] for r in recs if r["status"] == "SCORED" and r["P11"]["certified"]
                  and r["CVTR_accept"] and not r["CVTR_on_P11_side"]]
    unscorable = [{"key": r["key"], "hex": r["hex"], "reason": r.get("unscorable_reason")}
                  for r in recs if r["status"] != "SCORED"]
    rec_fails = [r["key"] for r in recs if r["status"] == "SCORED" and not r["CVTR_accept"]]
    return {"per_set": S, "P11_certified_CVTR_fail": fails, "recorded_competent_CVTR_fail": rec_fails, "P11_certified_CVTR_only_on_other_side": side_fails,
            "unscorable": unscorable}


# ------------------------------------------------------------------ modes
def check():
    """Design check (phase 1): known verdicts reproduce; painter rejected; dense VM self-test."""
    import run_dc
    out = {"dense_selftest": run_dc.selftest()}
    nat = {json.loads(l)["run_id"][:8]: json.loads(l) for l in open(HERE / "artemis_p11" / "NATURAL_REAPPLY.jsonl")}
    pan = {json.loads(l)["id"]: json.loads(l) for l in open(HERE / "artemis_p11" / "PANEL.jsonl")}
    cases = []
    for rid, side, expect in (("7ae3f9c1", 1, True), ("12ad3d5f", 0, False)):
        r = nat[rid]
        G = bytes.fromhex(r["genome"])
        t0 = time.time()
        got = A.cvt_side(A.vm_module("PLAIN"), G, r["n"], 1 << (2 * r["n"] - 1).bit_length(), r["budget"], r["mask"],
                         side, r["run_id"])
        rec = r["sides"][str(side)]
        cases.append({"case": "NATURAL %s side %d (plain z8, n %d, slice %d, mask %#x)" % (rid, side, r["n"], r["budget"], r["mask"]),
                      "expected_CVTR_accept": expect, "got_CVTR": got["CVTR"],
                      "identical_to_record": all(got[c] == rec[c] for c in ("CVT1", "CVT2", "CVTR", "LOCAL")),
                      "seconds": round(time.time() - t0, 2)})
    for sid, vm, expect in (("Z1", "PLAIN", False), ("Z1", "DENSE", False), ("Z3", "DENSE", True)):
        r = pan[sid]
        G = bytes.fromhex(r["genome"])
        n = r["n"]
        t0 = time.time()
        got = A.cvt_side(A.vm_module(vm), G, n, 1 << (2 * n - 1).bit_length(), r["budget"], r["mask"], r["side"], sid)
        cases.append({"case": "PANEL %s on %s VM" % (sid, vm), "expected_CVTR_accept": expect, "got_CVTR": got["CVTR"],
                      "identical_to_record": all(got[c] == r[c] for c in ("CVT1", "CVT2", "CVTR", "LOCAL")),
                      "seconds": round(time.time() - t0, 2)})
    out["cases"] = cases
    out["pass"] = (out["dense_selftest"] == {"plain": False, "dense": True}
                   and all(c["got_CVTR"]["accept"] == c["expected_CVTR_accept"] for c in cases)
                   and all(c["identical_to_record"] for c in cases if c["case"].startswith("NATURAL") or "PLAIN" in c["case"]))
    out["files"] = A.file_hashes()
    OUT.mkdir(exist_ok=True)
    (OUT / "ADAPTER_CHECK.json").write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({k: v for k, v in out.items() if k != "files"}, indent=1, sort_keys=True))


def select():
    sel = selection()
    OUT.mkdir(exist_ok=True)
    (OUT / "SELECTION.json").write_text(json.dumps(sel, indent=1))
    from collections import Counter
    print(len(sel), Counter((e["set"], e["subset"], e["vm"], e["cell"]) for e in sel))
    print("distinct hex:", len({e["hex"] for e in sel}))


def pilot(keys):
    sel = {e["key"]: e for e in selection()}
    recs = []
    for k in keys:
        r = job(sel[k])
        recs.append(r)
        print(k, r["status"], r.get("P11"), r.get("q1_match"), "CVTR", r.get("CVTR_accept"), r.get("CVTR_TB_max"),
              "sec", r["seconds"], r.get("unscorable_reason", ""))
    OUT.mkdir(exist_ok=True)
    (OUT / "PILOT.json").write_text(json.dumps(recs, indent=1))


def run():
    sel = selection()
    OUT.mkdir(exist_ok=True)
    f = OUT / "ROWS.jsonl"
    done = {json.loads(l)["key"] for l in f.read_text().splitlines()} if f.exists() else set()
    todo = [e for e in sel if e["key"] not in done]
    t0 = time.time()
    with mp.Pool(NPROC, maxtasksperchild=8) as pool, open(f, "a", encoding="ascii") as fh:
        for r in pool.imap_unordered(job, todo, chunksize=1):
            fh.write(json.dumps(r, sort_keys=True) + "\n")
            fh.flush()
            print(r["key"], r["status"], r.get("CVTR_accept"), r["seconds"], flush=True)
    recs = [json.loads(l) for l in f.read_text().splitlines()]
    order = {e["key"]: i for i, e in enumerate(sel)}
    recs.sort(key=lambda r: order[r["key"]])
    assert len(recs) == len(sel) and {r["key"] for r in recs} == set(order), "row set != selection"
    summ = summarize(recs)
    summ["wall_seconds_this_invocation"] = round(time.time() - t0, 1)
    summ["cpu_seconds_sum_rows"] = round(sum(r["seconds"] for r in recs), 1)
    summ["files"] = A.file_hashes()
    summ["origin_main_sha"] = (HERE / "foreign" / "ORIGIN_MAIN_SHA").read_text().strip()
    (OUT / "SUMMARY.json").write_text(json.dumps(summ, indent=1, sort_keys=True))
    print(json.dumps(summ["per_set"], indent=1, sort_keys=True))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "check":
        check()
    elif mode == "select":
        select()
    elif mode == "pilot":
        pilot(sys.argv[2:] or ["a:x_p2_bridge:0", "b:q1_competent:0", "c:epoch700_modal:0"])
    elif mode == "run":
        run()
    else:
        print(__doc__)
