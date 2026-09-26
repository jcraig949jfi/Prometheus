"""Preregistered analysis of the grounding round (GROUNDING_PREREG.md, frozen at a1b066309). Written while the round
was running and BEFORE any result was inspected; it implements s2-s4 of the prereg and nothing else. Anything not in
the prereg is printed under EXPLORATORY.
    python grounding_analysis.py --workdir C:/Users/James/z80atlas_grounding_2026-09-23 [--replay 0.05]
Writes receipts/GROUNDING_RESULTS.json."""
from __future__ import annotations

import argparse
import collections
import json
import math
import multiprocessing as mp
import os
import random
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(__file__))
import load as Ld  # noqa: E402

PINNED = "C:/Users/James/z80atlas_grounding_2026-09-23/code"


def _mods():
    if PINNED not in sys.path:
        sys.path.insert(0, PINNED)
    from prometheus.z80atlas import grounding as Gr, adjudication as A, vm
    from prometheus.z80atlas.world import Config
    from prometheus.z80atlas.tasks import Task
    return Gr, A, vm, Config, Task


# ---- statistics -----------------------------------------------------------------------------------------------------
def wilson(k, n, z=1.96):
    if not n:
        return None
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)]


def prop(k, n):
    return {"k": k, "n": n, "rate": round(k / n, 4) if n else None, "wilson95": wilson(k, n)}


def sign_test(a, b):
    """exact two-sided binomial test on discordant counts a (arm1-only) vs b (arm2-only)"""
    n = a + b
    if n == 0:
        return 1.0
    pk = [math.comb(n, i) / 2 ** n for i in range(n + 1)]
    return min(1.0, sum(p for p in pk if p <= pk[a] + 1e-15))


def detectable_share(n, alpha=0.05, power=0.8):
    """smallest discordant share (away from 0.5) a two-sided sign test on n discordant pairs detects at 80% power
    (normal approximation); None when n < 5."""
    if n < 5:
        return None
    za, zb = 1.959964, 0.841621
    return round(0.5 + (za * 0.5 + zb * 0.5) / math.sqrt(n), 3)


def diff_ci(k1, n1, k2, n2):
    """Newcombe hybrid score interval for p1 - p2"""
    if not n1 or not n2:
        return None
    p1, p2 = k1 / n1, k2 / n2
    l1, u1 = wilson(k1, n1); l2, u2 = wilson(k2, n2)
    d = p1 - p2
    return [round(d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), 4), round(d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2), 4)]


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i]); m = len(ps); adj = [None] * m; run = 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (m - r) * ps[i])); adj[i] = round(run, 6)
    return adj


# ---- detectors (prereg s2) ------------------------------------------------------------------------------------------
def sustained(r, d=3):
    s = r["summary"]
    return (s.get("sr_max_depth") or 0) >= d and (s.get("sr_alive_end") or 0) >= 1


def evo_active(r):
    return (r["summary"].get("sr_variants_transmitted") or 0) >= 1


def seeded_sr(r):
    return bool((r.get("first_self_replication") or {}).get("seeded"))


def g6_class(r, A, Config, Task, rep):
    fsr = r.get("first_self_replication") or {}
    gen = fsr.get("genealogy") or []
    if not gen:
        return None
    cfg = Config(representation=rep); L = cfg.L
    def sc(hexs):
        t = bytes.fromhex(hexs)[:L] if hexs else b""
        return A.repro_descriptor(t, cfg, Task("INC"))["self_copy"] if t else False
    def partial(hexs):
        """fraction of the window copied from own bytes by own code, alone"""
        _, _, vm, _, _ = _mods()
        t = bytes.fromhex(hexs)[:L] if hexs else b""
        if not t:
            return 0.0
        mem = bytearray(256); mem[:L] = t; mem[vm.IN_BASE] = 42
        tr = vm.execute(mem, L, 0, cfg.budget, [42], allow_copyall=cfg.allow_copyall)
        own = sum(1 for off, (src, pc, op) in tr.win_prov.items() if op in vm.COPY_OPS and src is not None and src < L and pc < L)
        return own / L
    w = gen[0]
    if w["mechanism"] == "init":
        cls = "CLIFF_AT_INIT" if sc(w["tape_at_birth"]) else "MUTATED_INIT"
    else:
        cls = "BUILT_BY_COPY"
    ramp = any(partial(a["tape_at_birth"]) >= 0.25 for a in gen[1:] if a.get("tape_at_birth"))
    # essential steps: writer's pre-execution tape vs its nearest non-SR reference (own birth tape if that did not
    # self-copy, else the parent's birth tape)
    ref = w["tape_at_birth"] if not sc(w["tape_at_birth"]) else (gen[1]["tape_at_birth"] if len(gen) > 1 else None)
    ess = None
    if ref:
        X = bytearray(bytes.fromhex(fsr["tape"])[:L]); R = bytes.fromhex(ref)[:L]
        diffs = [i for i in range(min(len(X), len(R))) if X[i] != R[i]]
        ess = 0
        for i in diffs:
            Y = bytearray(X); Y[i] = R[i]
            if not A.repro_descriptor(bytes(Y), cfg, Task("INC"))["self_copy"]:
                ess += 1
        ess = {"diffs": len(diffs), "essential": ess}
    return {"class": cls, "ramp": ramp, "steps": ess, "first_sr_tick": fsr.get("tick")}


def _replay(item):
    Gr, A, vm, Config, Task = _mods()
    import tempfile, shutil
    p, stored = item
    td = tempfile.mkdtemp(dir=str(Ld.LOCAL))
    try:
        p = dict(p, workdir=td)
        out = Gr._run(p)
        a = {k: v for k, v in stored["summary"].items() if k != "wall_s"}
        b = {k: v for k, v in out["summary"].items() if k != "wall_s"}
        return {"id": p["id"], "equal": a == b and stored.get("first_self_replication") == out.get("first_self_replication")}
    finally:
        shutil.rmtree(td, ignore_errors=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--replay", type=float, default=0.05)
    ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    Gr, A, vm, Config, Task = _mods()
    inputs = json.loads(open(os.path.join(a.workdir, "grounding_inputs.json"), encoding="utf-8").read())
    P = Gr.plan(inputs); planned = {p["id"]: p for p in P}
    R = {}
    for line in open(os.path.join(a.workdir, "results.jsonl"), encoding="utf-8"):
        try:
            r = json.loads(line); R[r["id"]] = r
        except ValueError:
            pass
    st_ = json.loads(open(os.path.join(a.workdir, "STATUS.json"), encoding="utf-8").read())
    out = {"plan_sha256": Gr.plan_hash(P), "status": st_, "planned": len(P), "completed": len(R)}
    by_cell = collections.defaultdict(list)
    for r in R.values():
        by_cell[(r["lane"], r["cell"])].append(r)
    notrun = collections.Counter((p["lane"], p["cell"]) for p in P if p["id"] not in R)
    out["not_run_by_cell"] = {"%s|%s" % k: v for k, v in notrun.items()}

    # G8 ---------------------------------------------------------------------------------------------------------------
    g8 = {}
    def cell(c):
        return by_cell.get(("G8", c), [])
    exp = {"pos_seeded_replicator": (lambda r: r["summary"]["self_rep_births"] > 0 and sustained(r), 18),
           "pos_witness_external": (lambda r: r["task_reached"], 18),
           "pos_hybrid_endogenous": (lambda r: r["summary"]["self_rep_births"] > 0, 18)}
    for c, (f, need) in exp.items():
        k = sum(1 for r in cell(c) if f(r)); g8[c] = {"k": k, "n": len(cell(c)), "need": need, "holds": k >= need}
    rs = cell("neg_external_neutral"); k = sum(1 for r in rs if r["summary"]["self_rep_births"] == 0)
    g8["neg_external_neutral"] = {"k_zero_SR": k, "n": len(rs), "holds": k == len(rs) == 20}
    rs = cell("neg_no_copy_chemistry"); k = sum(1 for r in rs if r["spontaneous"])
    g8["neg_no_copy_chemistry"] = {"k_spontaneous": k, "n": len(rs), "holds": k <= 1}
    for c in ("cheat_bare_ldir_transplant", "cheat_smear_transplant", "cheat_capture_partial"):
        rs = cell(c)
        bad = sum(1 for r in rs if r["spontaneous"] or seeded_sr(r))
        g8[c] = {"violations": bad, "n": len(rs), "holds": bad == 0 and len(rs) == 20}
    ids = sorted(R); rng = random.Random(2026092399)
    samp = rng.sample(ids, max(1, int(round(a.replay * len(ids))))) if a.replay > 0 else []
    if samp:
        with mp.Pool(a.workers) as pool:
            rep = pool.map(_replay, [(planned[i], R[i]) for i in samp], chunksize=1)
        g8["replay_sample"] = {"n": len(rep), "equal": sum(x["equal"] for x in rep), "holds": all(x["equal"] for x in rep),
                               "unequal_ids": [x["id"] for x in rep if not x["equal"]][:20]}
    g8["ALL_HOLD"] = all(v.get("holds", True) for v in g8.values() if isinstance(v, dict))
    out["G8"] = g8

    # G1 / G1T / G2 / G6 --------------------------------------------------------------------------------------------
    g1 = {}
    for (lane, c), rs in sorted(by_cell.items()):
        if lane in ("G1", "G1T"):
            k = sum(r["spontaneous"] for r in rs)
            ticks = sorted(r["first_self_replication"]["tick"] for r in rs if r["spontaneous"])
            g1["%s|%s" % (lane, c)] = dict(prop(k, len(rs)), first_sr_tick_median=ticks[len(ticks) // 2] if ticks else None,
                                         extinct=sum(r["summary"]["extinct"] for r in rs))
    out["G1"] = g1
    out["G1a_holds"] = (g1.get("G1|ENDOGENOUS_COPY/Z80_64") or {}).get("wilson95", [0])[0] > 0
    out["G1b_holds"] = (g1.get("G1|CONSTRUCTIVE/Z80_64") or {}).get("wilson95", [0])[0] > 0
    spont = [r for r in R.values() if r["spontaneous"] and (r["lane"] in ("G1", "G1T") or (r["lane"] == "G7" and r["cell"].startswith("RANDOM/")))]
    out["G2"] = {"spontaneous_runs": len(spont), "sustained_d3": prop(sum(sustained(r) for r in spont), len(spont)),
                 "sustained_d10": prop(sum(sustained(r, 10) for r in spont), len(spont)),
                 "evolutionarily_active": prop(sum(evo_active(r) for r in spont), len(spont))}
    out["G2a_holds"] = out["G2"]["sustained_d3"]["rate"] is not None and out["G2"]["sustained_d3"]["rate"] >= 0.5
    rep_of = {pid: planned[pid]["vec"]["representation"] for pid in planned}
    g6rows = [dict(g6_class(r, A, Config, Task, rep_of[r["id"]]) or {}, id=r["id"]) for r in spont]
    g6rows = [x for x in g6rows if x.get("class")]
    cc = collections.Counter(x["class"] for x in g6rows); n6 = len(g6rows)
    ess = [x["steps"]["essential"] for x in g6rows if x.get("steps")]
    out["G6"] = {"origins": n6, "classes": {k: prop(v, n6) for k, v in cc.items()}, "ramp": prop(sum(x["ramp"] for x in g6rows), n6),
                 "essential_steps_hist": dict(sorted(collections.Counter(ess).items())), "rows": g6rows}
    out["G6a_holds"] = n6 > 0 and cc.get("BUILT_BY_COPY", 0) / n6 >= 0.5
    out["G6b_holds"] = n6 > 0 and out["G6"]["ramp"]["rate"] >= 0.5

    # G3 -------------------------------------------------------------------------------------------------------------
    g3 = {}; pool_e = pool_x = 0
    for (lane, c), rs in sorted(by_cell.items()):
        if lane != "G3":
            continue
        pairs = collections.defaultdict(dict)
        for r in rs:
            pairs[r["pair"]][r["arm"]] = r
        full = [p for p in pairs.values() if len(p) == 2]
        e_only = sum(1 for p in full if p["ENDOGENOUS_COPY"]["task_reached"] and not p["EXTERNAL"]["task_reached"])
        x_only = sum(1 for p in full if p["EXTERNAL"]["task_reached"] and not p["ENDOGENOUS_COPY"]["task_reached"])
        both = sum(1 for p in full if p["EXTERNAL"]["task_reached"] and p["ENDOGENOUS_COPY"]["task_reached"])
        births = {arm: st.mean((p[arm]["summary"].get("endogenous_births") or 0) + (p[arm]["summary"].get("external_births") or 0) for p in full) if full else None
                  for arm in ("ENDOGENOUS_COPY", "EXTERNAL")}
        g3[c] = {"pairs": len(full), "endo_only": e_only, "ext_only": x_only, "both": both, "p": sign_test(e_only, x_only),
                 "detectable_share_80pct": detectable_share(e_only + x_only), "mean_births": births}
        if "extmut4" not in c:
            pool_e += e_only; pool_x += x_only
    out["G3"] = {"cells": g3, "pooled_primary": {"endo_only": pool_e, "ext_only": pool_x, "p": sign_test(pool_e, pool_x),
                                                  "detectable_share_80pct": detectable_share(pool_e + pool_x)}}
    out["G3a_holds"] = pool_x > pool_e

    # G5 -------------------------------------------------------------------------------------------------------------
    trip = collections.defaultdict(dict)
    for r in R.values():
        if r["lane"] == "G5":
            trip[r["pair"]][r["arm"]] = r
    def tla(r):
        d = r.get("dominant_sr_descriptor") or {}
        return bool(d.get("self_copy")) and (d.get("task_accuracy") or 0) >= 0.5
    full = [t for t in trip.values() if len(t) == 3]
    on_only = sum(1 for t in full if tla(t["ON"]) and not tla(t["OFF"])); off_only = sum(1 for t in full if tla(t["OFF"]) and not tla(t["ON"]))
    ex = lambda r: (r.get("dominant_sr_descriptor") or {}).get("exec_own_bytes")
    dd = [ex(t["ON"]) - ex(t["OFF"]) for t in full if ex(t["ON"]) is not None and ex(t["OFF"]) is not None]
    alt_inc = []
    for t in full:
        dom = t["ALT"].get("dominant_sr_tape")
        if dom:
            alt_inc.append(A.verify_tape(bytes.fromhex(dom), Config(task="INC"), Task("INC"))["accuracy"])
    out["G5"] = {"triples": len(full), "TLA": {arm: prop(sum(tla(t[arm]) for t in full), len(full)) for arm in ("ON", "OFF", "ALT")},
                 "ON_only": on_only, "OFF_only": off_only, "p": sign_test(on_only, off_only), "detectable_share_80pct": detectable_share(on_only + off_only),
                 "exec_own_bytes_ON_minus_OFF": {"n": len(dd), "pos": sum(x > 0 for x in dd), "neg": sum(x < 0 for x in dd),
                                                 "p": sign_test(sum(x > 0 for x in dd), sum(x < 0 for x in dd)), "median": st.median(dd) if dd else None},
                 "ALT_dominant_accuracy_on_INC_mean": round(st.mean(alt_inc), 4) if alt_inc else None,
                 "ALT_dominant_accuracy_on_ECHO_mean": round(st.mean((t["ALT"].get("dominant_sr_descriptor") or {}).get("task_accuracy") or 0 for t in full), 4) if full else None,
                 "task_reached": {arm: prop(sum(t[arm]["task_reached"] for t in full), len(full)) for arm in ("ON", "OFF", "ALT")}}

    # G7P1 / G7 ------------------------------------------------------------------------------------------------------
    g7p = {}
    for sp in ("NICHES_POLLINATION", "RESERVOIR", "NICHES_ISOLATED"):
        pairs = collections.defaultdict(dict)
        for r in by_cell.get(("G7P1", sp), []):
            pairs[r["pair"]][r["arm"]] = r
        full = [p for p in pairs.values() if len(p) == 2]
        v1_only = sum(1 for p in full if not p["v1"]["summary"]["extinct"] and p["v2"]["summary"]["extinct"])   # v1 survives, v2 dies
        v2_only = sum(1 for p in full if not p["v2"]["summary"]["extinct"] and p["v1"]["summary"]["extinct"])
        g7p[sp] = {"pairs": len(full), "extinct_v1": prop(sum(p["v1"]["summary"]["extinct"] for p in full), len(full)),
                   "extinct_v2": prop(sum(p["v2"]["summary"]["extinct"] for p in full), len(full)),
                   "survive_v1_only": v1_only, "survive_v2_only": v2_only, "p": sign_test(v1_only, v2_only),
                   "spont_v1": prop(sum(p["v1"]["spontaneous"] for p in full), len(full)), "spont_v2": prop(sum(p["v2"]["spontaneous"] for p in full), len(full)),
                   "world_copies_v1_mean": round(st.mean(p["v1"]["summary"]["world_copies_under_endogenous"] for p in full), 1) if full else None,
                   "world_copies_v2_max": max((p["v2"]["summary"]["world_copies_under_endogenous"] for p in full), default=None)}
    out["G7P1"] = g7p
    pol, iso = g7p.get("NICHES_POLLINATION", {}), g7p.get("NICHES_ISOLATED", {})
    out["G7a_holds"] = bool(pol) and pol["survive_v1_only"] > pol["survive_v2_only"] and pol["p"] < 0.05 and iso.get("survive_v1_only", 1) + iso.get("survive_v2_only", 1) == 0
    if pol and iso:
        ci = diff_ci(pol["spont_v2"]["k"], pol["spont_v2"]["n"], iso["spont_v2"]["k"], iso["spont_v2"]["n"])
        out["G7b"] = {"pollination_minus_isolated_spont_v2": ci}
        out["G7b_holds"] = ci is not None and ci[0] <= 0 <= ci[1] and abs((pol["spont_v2"]["rate"] or 0) - (iso["spont_v2"]["rate"] or 0)) <= 0.02
    g7 = {}
    for (lane, c), rs in sorted(by_cell.items()):
        if lane == "G7":
            g7[c] = {"n": len(rs), "spontaneous": prop(sum(r["spontaneous"] for r in rs), len(rs)), "sustained": prop(sum(sustained(r) for r in rs), len(rs)),
                     "extinct": prop(sum(r["summary"]["extinct"] for r in rs), len(rs)), "sr_alive_end": prop(sum((r["summary"]["sr_alive_end"] or 0) > 0 for r in rs), len(rs))}
    out["G7"] = g7

    # P8 -------------------------------------------------------------------------------------------------------------
    p8 = {}
    for (lane, c), rs in sorted(by_cell.items()):
        if lane == "P8":
            p8[c] = {"n": len(rs), "spontaneous": prop(sum(r["spontaneous"] for r in rs), len(rs)), "sustained": prop(sum(sustained(r) for r in rs), len(rs)),
                     "evo_active": prop(sum(evo_active(r) for r in rs), len(rs)), "task_reached": prop(sum(r["task_reached"] for r in rs), len(rs)),
                     "TLA": prop(sum(tla(r) for r in rs), len(rs)), "extinct": prop(sum(r["summary"]["extinct"] for r in rs), len(rs))}
    out["P8"] = p8
    def rate(c):
        return (p8.get(c) or {}).get("spontaneous", {}).get("rate")
    b = rate("RANDOM/COPY/base")
    out["P8a_holds"] = b is not None and rate("RANDOM/COPY/ldir_off") is not None and rate("RANDOM/COPY/ldir_off") < b
    out["P8b_holds"] = b is not None and rate("RANDOM/COPY/undefined_halt") is not None and rate("RANDOM/COPY/undefined_halt") < b

    # HIST -----------------------------------------------------------------------------------------------------------
    pairs = collections.defaultdict(dict)
    for r in R.values():
        if r["lane"] == "HIST":
            pairs[r["pair"]][r["arm"]] = r
    full = [p for p in pairs.values() if len(p) == 2]
    out["HIST"] = {"specimens": len(full), "intact_seeded_SR": prop(sum(seeded_sr(p["intact"]) for p in full), len(full)),
                   "intact_seeded_SR_sustained": prop(sum(seeded_sr(p["intact"]) and sustained(p["intact"]) for p in full), len(full)),
                   "ablated_seeded_SR": prop(sum(seeded_sr(p["ablated"]) for p in full), len(full))}
    hi = out["HIST"]
    out["HISTa_holds"] = bool(full) and hi["intact_seeded_SR"]["rate"] >= 0.5 and hi["ablated_seeded_SR"]["rate"] <= 0.05

    # confirmatory set, Holm ------------------------------------------------------------------------------------------
    ps = [out["G3"]["pooled_primary"]["p"], out["G5"]["p"], (g7p.get("NICHES_POLLINATION") or {}).get("p", 1.0)]
    out["confirmatory_holm"] = dict(zip(("G3_pooled", "G5_ON_vs_OFF", "G7a_POLLINATION_v1_vs_v2"), holm(ps)))
    p = Ld.write("GROUNDING_RESULTS.json", out)
    print(p)
    print(json.dumps({k: v for k, v in out.items() if k.endswith("_holds") or k in ("completed", "planned", "confirmatory_holm", "not_run_by_cell")}, indent=1))


if __name__ == "__main__":
    main()
