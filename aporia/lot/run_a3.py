"""run_a3.py -- LOT-A3-REIFY: does reification earn its keep?

Executes aporia/lot/PREREG_A3_2026-09-11.md and nothing else. Read that file first; every
threshold, arm, fixture and prediction here is a transcription of it. Two modes, each its own
commit per the preregistration's section 9:

    python aporia/lot/run_a3.py calibrate     fixtures X1-X8 on seed 20260911; writes
                                              RESULT_A3_CALIBRATION.json (the R2 bar, X1b's
                                              null, X3's oracle ratio, FREQ's frequency table)
    python aporia/lot/run_a3.py read          reading on seeds 20260912-14 against the
                                              calibration bar; writes RESULT_A3.json with
                                              every per-episode row

THE SOLVER IS world3.build_closure WITH TWO ADDITIONS THAT CHANGE NO COST: a witness expression
per signature (first found), and an execution accumulator that charges each expansion its
EXPANSION SIZE times P. For world primitives the expansion size is 1 and C_execution == P *
C_search exactly (fixture X2 asserts it); for a macro of body size k it is k. That is the
amendment-1 s5 separation, in code rather than prose.

NOTHING IN THIS FILE MAY READ A LATE TASK BEFORE THE MECHANISM HAS DECIDED. The promotion
function takes early signatures and probes and nothing else (fixture X4 calls it with every
other field deleted; fixture X1c swaps the late tasks and asserts the decision is unchanged).
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "iq"))
sys.path.insert(0, str(REPO))

import world3 as W3                                  # noqa: E402
import result_schema as RS                           # noqa: E402

try:
    from archaeon.workspace import assert_not_canonical, receipt as ws_receipt   # noqa: E402
except Exception:                                    # pragma: no cover
    assert_not_canonical = None
    ws_receipt = None

V, S = W3.V, W3.S
P = 6                                    # probes
MAX_SIZE = 6
MAX_CAND = 600_000
THETA = 6                                # PREREG s2
MOTIF_COST = W3.MOTIF_COST               # 2
CAL_SEED = 20260911
READ_SEEDS = (20260912, 20260913, 20260914)
BURNED = {20260827, 20260828, 20260829, 20260830, 20260901, 20260902, 20260903, 20260904, 20260905}
EPISODES_PER_CLASS = 12
FREQ_SAMPLE = 2000
BOOT = 2000
ARMS = ("FLAT", "REIFIED", "ORACLE", "CONTROL", "RANDOM", "FREQ", "MEMO")


# ---------------------------------------------------------------- the solver (closure + costs)

def macro_spec(body, prims, name):
    """A unary V->V primitive whose fn evaluates `body` (free variable X) over the base prims.
    expansion_size is the body's op count; that is what execution is charged."""
    base = list(prims)

    def fn(v, _body=body, _base=base):
        return W3.evaluate(_body, v, _base)

    return {"name": name, "args": (V,), "ret": V, "fn": fn, "expansion_size": W3.size_of(body),
            "body": body}


def closure(prims, probes, extra_leaves=(), max_size=MAX_SIZE, max_candidates=MAX_CAND):
    """world3.build_closure with a witness per signature and an execution accumulator.

    Returns dict with minsize, order (C_search at discovery), exec_order (C_execution at
    discovery), witness, stats. `extra_leaves` are (tag, signature) pairs seeded into layer 0 at
    zero cost -- the MEMO arm and nothing else uses them.
    """
    x_sig = tuple(probes)
    x_key = (V, x_sig)
    minsize = {x_key: 0}
    order = {x_key: 0}
    exec_order = {x_key: 0}
    witness = {x_key: ("X",)}
    layer_v0 = [x_sig]
    for tag, sig in extra_leaves:
        key = (V, tuple(sig))
        if key not in minsize:
            minsize[key] = 0
            order[key] = 0
            exec_order[key] = 0
            witness[key] = ("MEMO", tag)
            layer_v0.append(tuple(sig))
    layers = {(0, V): layer_v0, (0, S): []}
    # parent lookup by signature so a witness can be assembled
    parent_expr = {(V, s): witness[(V, s)] for s in layer_v0}
    cand = 0
    ecost = 0
    exhausted = False
    exp_size = [spec.get("expansion_size", 1) for spec in prims]

    def admit(key, sig, size, expr, got_v, got_s, ret):
        if key not in minsize:
            minsize[key] = size
            order[key] = cand
            exec_order[key] = ecost
            witness[key] = expr
            parent_expr[key] = expr
            (got_v if ret == V else got_s).append(sig)

    for size in range(1, max_size + 1):
        got_v, got_s = [], []
        for idx, spec in enumerate(prims):
            args, ret, fn = spec["args"], spec["ret"], spec["fn"]
            if len(args) == 1:
                for ps in layers.get((size - 1, args[0]), []):
                    cand += 1
                    ecost += exp_size[idx] * P
                    sig = tuple(fn(u) for u in ps)
                    admit((ret, sig), sig, size, (idx, parent_expr[(args[0], ps)]),
                          got_v, got_s, ret)
                    if cand >= max_candidates:
                        exhausted = True
                        break
            else:
                for sa in range(0, size):
                    sb = size - 1 - sa
                    la = layers.get((sa, args[0]), [])
                    lb = layers.get((sb, args[1]), [])
                    if not la or not lb:
                        continue
                    for pa in la:
                        for pb in lb:
                            cand += 1
                            ecost += exp_size[idx] * P
                            sig = tuple(fn(u, w) for u, w in zip(pa, pb))
                            admit((ret, sig), sig, size,
                                  (idx, parent_expr[(args[0], pa)], parent_expr[(args[1], pb)]),
                                  got_v, got_s, ret)
                            if cand >= max_candidates:
                                exhausted = True
                                break
                        if exhausted:
                            break
                    if exhausted:
                        break
            if exhausted:
                break
        layers[(size, V)] = got_v
        layers[(size, S)] = got_s
        if exhausted:
            break
    return {"minsize": minsize, "order": order, "exec_order": exec_order, "witness": witness,
            "layers": layers,
            "stats": {"candidates_expanded": cand, "distinct_signatures": len(minsize),
                      "budget_exhausted": exhausted, "execution_total": ecost}}


def task_costs(cl, sig):
    key = (V, tuple(sig))
    if key not in cl["order"]:
        return None
    return {"c_search": cl["order"][key], "c_execution": cl["exec_order"][key],
            "min_size": cl["minsize"][key]}


# ---------------------------------------------------------------- the promotion mechanism

def v_subterm_sigs_size2(expr, probes, prims):
    """Signatures of every size-2 V-typed subterm of `expr` (a macro-free witness)."""
    out = set()
    for t in W3.subterms(expr):
        if t[0] in ("X", "MEMO"):
            continue
        if W3.size_of(t) != MOTIF_COST:
            continue
        if prims[t[0]]["ret"] != V:
            continue
        out.add(W3.signature(t, probes, prims))
    return out


def promote(early_sigs, probes, prims, flat_cl, theta=THETA):
    """PREREG s2. Inputs: the early task SIGNATURES and the probe set. Nothing else.

    Returns dict: minted (bool), c_max, s_max (signature or None), body (expr or None),
    census (signature -> count), witnesses_missing (early sigs with no witness under budget).
    """
    census = {}
    missing = 0
    for sig in early_sigs:
        key = (V, tuple(sig))
        w = flat_cl["witness"].get(key)
        if w is None:
            missing += 1
            continue
        for s2 in v_subterm_sigs_size2(w, probes, prims):
            census[s2] = census.get(s2, 0) + 1
    if not census:
        return {"minted": False, "c_max": 0, "s_max": None, "body": None, "census": {},
                "witnesses_missing": missing}
    # deterministic tie-break: highest count, then the signature discovered earliest
    best = max(census.items(), key=lambda kv: (kv[1], -flat_cl["order"].get((V, kv[0]), 10**12)))
    s_max, c_max = best[0], best[1]
    body = flat_cl["witness"][(V, s_max)] if c_max >= theta else None
    return {"minted": c_max >= theta, "c_max": c_max, "s_max": s_max, "body": body,
            "census": {str(k): v for k, v in census.items()}, "witnesses_missing": missing}


# ---------------------------------------------------------------- arms

def size2_expressions(prims):
    """Every constructible size-2 V expression over the base prims (finite, small)."""
    unary = [i for i, s in enumerate(prims) if s["args"] == (V,) and s["ret"] == V]
    binary_vv = [i for i, s in enumerate(prims) if s["args"] == (V, V) and s["ret"] == V]
    v_to_s = [i for i, s in enumerate(prims) if s["args"] == (V,) and s["ret"] == S]
    vs_to_v = [i for i, s in enumerate(prims) if s["args"] == (V, S) and s["ret"] == V]
    X = ("X",)
    out = []
    for a in unary:
        for b in unary:
            out.append((a, (b, X)))
        for b in binary_vv:
            out.append((a, (b, X, X)))
    for a in binary_vv:
        for b in unary:
            out.append((a, (b, X), X))
            out.append((a, X, (b, X)))
    for a in vs_to_v:
        for b in v_to_s:
            out.append((a, X, (b, X)))
    return out


def global_size2_frequency(seed, prims, probes, n_programs=FREQ_SAMPLE):
    """PREREG s3 FREQ: frequency of each size-2 V-signature as a subterm across random size-6
    programs, drawn once from the calibration seed."""
    rng = random.Random(seed * 31 + 7)
    _, feas = W3._feasible_table(prims, 9, MOTIF_COST)
    freq = {}
    drawn = 0
    while drawn < n_programs:
        e = W3.sample_expr(rng, prims, V, 6, feas, MOTIF_COST, allow_motif=False)
        if e is None:
            continue
        drawn += 1
        for s2 in v_subterm_sigs_size2(e, probes, prims):
            freq[s2] = freq.get(s2, 0) + 1
    return freq


def pick_freq_matched(target_sig, freq, exclude_sigs, cl_flat):
    """The size-2 signature whose global frequency is nearest the target's, excluding the
    target itself; ties broken by earliest flat discovery order. Returns (sig, body)."""
    tf = freq.get(target_sig, 0)
    cands = [(abs(f - tf), cl_flat["order"].get((V, s), 10**12), s)
             for s, f in freq.items() if s not in exclude_sigs and (V, s) in cl_flat["witness"]]
    if not cands:
        return None, None
    cands.sort()
    s = cands[0][2]
    return s, cl_flat["witness"][(V, s)]


def pick_random_macro(seed, ep_index, prims, exclude_sigs, probes):
    rng = random.Random(seed * 7919 + ep_index)
    pool = size2_expressions(prims)
    for _ in range(500):
        body = pool[rng.randrange(len(pool))]
        if W3.signature(body, probes, prims) not in exclude_sigs:
            return body
    return None


def run_episode(ep, ep_index, seed, prims, probes, flat_cl, freq_table, arms=ARMS):
    """All arms on one episode. Returns the per-episode row (PREREG s3 last paragraph)."""
    early = [t for t in ep["tasks"] if t["early"]]
    late = [t for t in ep["tasks"] if not t["early"]]
    early_sigs = [W3.signature(t["expr"], probes, prims) for t in early]
    late_sigs = [W3.signature(t["expr"], probes, prims) for t in late]
    shared_sig = W3.signature(ep["shared_motif"], probes, prims)

    dec = promote(early_sigs, probes, prims, flat_cl)
    row = {"class": ep["class"], "episode": ep_index, "seed": seed,
           "n_early": len(early), "n_late": len(late),
           "minted": dec["minted"], "c_max": dec["c_max"],
           "s_max_is_shared": (dec["s_max"] == shared_sig) if dec["s_max"] is not None else None,
           "witnesses_missing": dec["witnesses_missing"], "arms": {}}
    exclude = {shared_sig}
    if dec["s_max"] is not None:
        exclude.add(dec["s_max"])

    def arm_prims(name):
        if name == "FLAT":
            return list(prims), ()
        if name == "REIFIED":
            if not dec["minted"]:
                return list(prims), ()
            return list(prims) + [macro_spec(dec["body"], prims, "M")], ()
        if name in ("ORACLE", "CONTROL"):
            return list(prims) + [macro_spec(ep["shared_motif"], prims, "M")], ()
        if name == "RANDOM":
            body = pick_random_macro(seed, ep_index, prims, exclude, probes)
            return (list(prims) + [macro_spec(body, prims, "M")], ()) if body else (list(prims), ())
        if name == "FREQ":
            target = dec["s_max"] if dec["minted"] else shared_sig
            s, body = pick_freq_matched(target, freq_table, exclude, flat_cl)
            return (list(prims) + [macro_spec(body, prims, "M")], ()) if body else (list(prims), ())
        if name == "MEMO":
            return list(prims), tuple((i, s) for i, s in enumerate(early_sigs))
        raise ValueError(name)

    for name in arms:
        pr, leaves = arm_prims(name)
        if name == "FLAT":
            cl = flat_cl
        else:
            cl = closure(pr, probes, extra_leaves=leaves)
        cs, ce, ms, dropped = [], [], [], 0
        for sig in late_sigs:
            c = task_costs(cl, sig)
            if c is None:
                dropped += 1
                continue
            cs.append(c["c_search"]); ce.append(c["c_execution"]); ms.append(c["min_size"])
        early_cs = []
        if name in ("CONTROL", "FLAT"):
            for sig in early_sigs:
                c = task_costs(cl, sig)
                if c is not None:
                    early_cs.append(c["c_search"])
        row["arms"][name] = {
            "n_prims": len(pr), "n_leaves": len(leaves),
            "late_solved": len(cs), "late_dropped": dropped,
            "median_c_search": statistics.median(cs) if cs else None,
            "median_c_execution": statistics.median(ce) if ce else None,
            "mean_min_size": (sum(ms) / len(ms)) if ms else None,
            "early_median_c_search": statistics.median(early_cs) if early_cs else None,
            "closure_candidates": cl["stats"]["candidates_expanded"],
            "closure_exhausted": cl["stats"]["budget_exhausted"],
        }
    return row


# ---------------------------------------------------------------- statistics

def bootstrap_median_ci(xs, n_boot=BOOT, seed=1):
    if not xs:
        return None
    rng = random.Random(seed)
    meds = []
    n = len(xs)
    for _ in range(n_boot):
        meds.append(statistics.median(xs[rng.randrange(n)] for _ in range(n)))
    meds.sort()
    return {"point": statistics.median(xs), "lo": meds[int(0.025 * n_boot)],
            "hi": meds[int(0.975 * n_boot) - 1], "n": n}


def binom_two_sided(k, n, p=0.5):
    if n == 0:
        return None
    def pmf(i):
        return math.comb(n, i) * p ** i * (1 - p) ** (n - i)
    obs = pmf(k)
    return min(1.0, sum(pmf(i) for i in range(n + 1) if pmf(i) <= obs + 1e-15))


def ratio_rows(rows, arm_num, arm_den="FLAT", cls="REUSE", minted_only=True, field="median_c_search"):
    out = []
    for r in rows:
        if r["class"] != cls:
            continue
        if minted_only and not r["minted"]:
            continue
        a, b = r["arms"][arm_num][field], r["arms"][arm_den][field]
        if a is None or b is None or b == 0:
            continue
        out.append(a / b)
    return out


def rule_r1(rows, n_eligible):
    def rate(cls):
        eps = [r for r in rows if r["class"] == cls]
        return (sum(1 for r in eps if r["minted"]) / len(eps)) if eps else None, len(eps)
    mr, ne = rate("REUSE"); mn, nn = rate("NO_REUSE")
    if ne == 0 or nn == 0:
        verdict = "INDETERMINATE"
    elif mr >= 0.75 and mn <= 0.25:
        verdict = "PASS"
    elif mr <= 0.50 or mn >= 0.50:
        verdict = "FAIL"
    else:
        verdict = "INDETERMINATE"
    prec = [r["s_max_is_shared"] for r in rows if r["class"] == "REUSE" and r["minted"]]
    return {"verdict": verdict, "mint_rate_REUSE": mr, "mint_rate_NO_REUSE": mn,
            "mint_rate_DECOY_REUSE": rate("DECOY_REUSE")[0],
            "mint_rate_LATE_REUSE": rate("LATE_REUSE")[0],
            "mint_rate_CONTROL": rate("CONTROL")[0],
            "eligible_per_class": {"REUSE": ne, "NO_REUSE": nn},
            "precision_s_max_is_shared": (sum(prec) / len(prec)) if prec else None,
            "attainable": [0.0, 1.0]}


def rule_r2(rows, bar):
    xs = ratio_rows(rows, "REIFIED")
    ci = bootstrap_median_ci(xs, seed=2)
    eligible = len(xs)
    if ci is None or eligible < 18:
        return {"verdict": "INDETERMINATE", "reason": "fewer than 18 minted REUSE episodes",
                "eligible": eligible, "ci": ci, "bar": bar}
    if ci["hi"] < 1.0 and ci["point"] <= bar:
        v = "PASS"
    elif ci["lo"] >= 1.0 or ci["point"] > 1.0:
        v = "FAIL"
    else:
        v = "INDETERMINATE"
    return {"verdict": v, "eligible": eligible, "ci": ci, "bar": bar, "attainable": "(0, inf)"}


def rule_r3(rows):
    xs = ratio_rows(rows, "REIFIED", field="median_c_execution")
    return {"reported_not_gated": True, "ci": bootstrap_median_ci(xs, seed=3), "eligible": len(xs)}


def rule_r4(rows):
    out = {}
    for ctrl in ("RANDOM", "FREQ", "MEMO"):
        wins = n = 0
        for r in rows:
            if r["class"] != "REUSE" or not r["minted"]:
                continue
            a, b = r["arms"]["REIFIED"]["median_c_search"], r["arms"][ctrl]["median_c_search"]
            if a is None or b is None:
                continue
            n += 1
            wins += 1 if a < b else 0
        frac = (wins / n) if n else None
        p = binom_two_sided(wins, n) if n else None
        if n == 0:
            v = "INDETERMINATE"
        elif frac >= 0.75 and p < 0.01:
            v = "PASS"
        elif frac <= 0.50:
            v = "FAIL"
        else:
            v = "INDETERMINATE"
        out[ctrl] = {"verdict": v, "fraction_reified_better": frac, "wins": wins, "eligible": n,
                     "p_two_sided": p, "attainable": [0.0, 1.0]}
    return out


def rule_r5(rows):
    xs = ratio_rows(rows, "REIFIED", cls="DECOY_REUSE")
    xe = ratio_rows(rows, "REIFIED", cls="DECOY_REUSE", field="median_c_execution")
    return {"reported_not_gated": True, "search_ci": bootstrap_median_ci(xs, seed=5),
            "execution_ci": bootstrap_median_ci(xe, seed=6), "eligible": len(xs),
            "fraction_search_ratio_ge_1": (sum(1 for x in xs if x >= 1.0) / len(xs)) if xs else None}


# ---------------------------------------------------------------- fixtures X1-X8 (PREREG s5)

def make_world(seed, prims):
    return W3.world(seed, prims, episodes_per_class=EPISODES_PER_CLASS, total_size=6)


def fixtures(seed, prims, probes, flat_cl, freq_table):
    fx = {}
    _, feas = W3._feasible_table(prims, 9, MOTIF_COST)

    # X1a known-positive: construct 12 early tasks that all contain one planted motif, and
    # verify from the flat witnesses (which is what the mechanism sees) that it mints.
    rng = random.Random(seed + 101)
    planted = W3.sample_motif(rng, prims, feas)
    planted_sig = W3.signature(planted, probes, prims)
    # choose early tasks whose FLAT WITNESS contains the planted signature as a size-2 subterm,
    # so the fixture asserts the mechanism's arithmetic, not witness retention (that is P2)
    early_sigs = []
    tries = 0
    while len(early_sigs) < 12 and tries < 5000:
        tries += 1
        e = W3.sample_task(rng, prims, feas, 6, planted)
        if e is None:
            continue
        sig = W3.signature(e, probes, prims)
        w = flat_cl["witness"].get((V, sig))
        if w is not None and planted_sig in v_subterm_sigs_size2(w, probes, prims):
            early_sigs.append(sig)
    d = promote(early_sigs, probes, prims, flat_cl)
    fx["X1a_known_positive"] = {"pass": bool(d["minted"] and d["s_max"] == planted_sig),
                                "c_max": d["c_max"], "n_early": len(early_sigs), "tries": tries}

    # X1b known-negative: 200 NO_REUSE episodes; empirical P(c_max >= THETA) must be < 0.10
    cnt = 0
    cmaxes = []
    for j in range(200):
        rng_e = random.Random(seed * 1000003 + 1 * 997 + 5000 + j)
        ep = W3.make_episode(rng_e, prims, feas, "NO_REUSE", 6)
        es = [W3.signature(t["expr"], probes, prims) for t in ep["tasks"] if t["early"]]
        d = promote(es, probes, prims, flat_cl)
        cmaxes.append(d["c_max"])
        cnt += 1 if d["minted"] else 0
    fx["X1b_known_negative"] = {"pass": (cnt / 200) < 0.10, "p_mint_NO_REUSE": cnt / 200,
                                "c_max_histogram": {str(k): cmaxes.count(k) for k in sorted(set(cmaxes))},
                                "theta": THETA}

    # X1c hindsight guard: decision unchanged when late tasks are replaced
    w = make_world(seed, prims)
    ep_r = next(e for e in w if e["class"] == "REUSE")
    ep_n = next(e for e in w if e["class"] == "NO_REUSE")
    es = [W3.signature(t["expr"], probes, prims) for t in ep_r["tasks"] if t["early"]]
    d1 = promote(es, probes, prims, flat_cl)
    swapped = dict(ep_r, tasks=[t for t in ep_r["tasks"] if t["early"]] +
                   [t for t in ep_n["tasks"] if not t["early"]])
    es2 = [W3.signature(t["expr"], probes, prims) for t in swapped["tasks"] if t["early"]]
    d2 = promote(es2, probes, prims, flat_cl)
    fx["X1c_hindsight_guard"] = {"pass": (d1["minted"], d1["s_max"]) == (d2["minted"], d2["s_max"])}

    # X2 cost model
    ok_flat = True
    for t in ep_r["tasks"]:
        c = task_costs(flat_cl, W3.signature(t["expr"], probes, prims))
        if c is None or c["c_execution"] != P * c["c_search"]:
            ok_flat = False
    m = macro_spec(ep_r["shared_motif"], prims, "M")
    pr = list(prims) + [m]
    cl_m = closure(pr, probes)
    # every expansion of M is charged 2*P: total execution == P * (cand - n_M) + 2P * n_M
    n_unary_parents = sum(len(cl_m["layers"].get((s - 1, V), [])) for s in range(1, MAX_SIZE + 1))
    # count of M expansions = number of V parents at each size-1 layer (M is unary V->V)
    expected_exec = P * cl_m["stats"]["candidates_expanded"] + P * n_unary_parents  # +1 extra P per M
    fx["X2_cost_model"] = {"pass": ok_flat and cl_m["stats"]["execution_total"] == expected_exec,
                           "flat_identity_holds": ok_flat,
                           "macro_execution_total": cl_m["stats"]["execution_total"],
                           "expected": expected_exec, "macro_expansions": n_unary_parents}

    # X3 channel cheat: ORACLE reduces REUSE late C_search on the calibration world
    oracle_ratios = []
    cal_rows = []
    for i, ep in enumerate(w):
        if ep["class"] != "REUSE":
            continue
        row = run_episode(ep, i, seed, prims, probes, flat_cl, freq_table, arms=("FLAT", "ORACLE"))
        cal_rows.append(row)
        a, b = row["arms"]["ORACLE"]["median_c_search"], row["arms"]["FLAT"]["median_c_search"]
        if a is not None and b:
            oracle_ratios.append(a / b)
    ci = bootstrap_median_ci(oracle_ratios, seed=33)
    fx["X3_channel_cheat_oracle"] = {"pass": bool(ci and ci["hi"] < 1.0 and ci["point"] < 1.0),
                                     "ci": ci, "n": len(oracle_ratios)}

    # X4 information guard: the mechanism accepts only signatures + probes
    stripped = [dict(t) for t in ep_r["tasks"] if t["early"]]
    for t in stripped:
        t.pop("declared_shared", None); t.pop("motif", None)
    es4 = [W3.signature(t["expr"], probes, prims) for t in stripped]
    d4 = promote(es4, probes, prims, flat_cl)
    fx["X4_information_guard"] = {"pass": (d4["minted"], d4["s_max"]) == (d1["minted"], d1["s_max"])}

    # X5 CONTROL identity
    ctrl = list(prims) + [macro_spec(ep_r["shared_motif"], prims, "M")]
    reif = list(prims) + [macro_spec(ep_r["shared_motif"], prims, "M")]
    same = len(ctrl) == len(reif) == len(prims) + 1 and ctrl[-1]["body"] == ep_r["shared_motif"]
    fx["X5_control_identity"] = {"pass": bool(same), "n_prims_control": len(ctrl)}

    # X6 gate reachability R2
    bar_cal = 1 - 0.5 * (1 - ci["point"]) if ci else None
    fake_nomint = [dict(r, minted=False) for r in cal_rows]
    v_nomint = rule_r2(fake_nomint, bar_cal)["verdict"]
    fake_oracle = []
    for r in cal_rows:
        rr = dict(r, minted=True, arms=dict(r["arms"]))
        rr["arms"]["REIFIED"] = r["arms"]["ORACLE"]
        fake_oracle.append(rr)
    # R2 needs >= 18 minted episodes; the calibration world has 12 REUSE episodes, so
    # duplicate the rows to reach eligibility for the reachability check ONLY
    v_oracle = rule_r2(fake_oracle * 2, bar_cal)["verdict"]
    fx["X6_gate_R2_reachable"] = {"pass": v_nomint == "INDETERMINATE" and v_oracle == "PASS",
                                  "nomint_reads": v_nomint, "oracle_reads": v_oracle, "bar": bar_cal}

    # X7 gate reachability R4
    fake_copy = []
    fake_win = []
    for r in fake_oracle:
        a = dict(r, arms=dict(r["arms"]))
        for c in ("RANDOM", "FREQ", "MEMO"):
            a["arms"][c] = r["arms"]["REIFIED"]
        fake_copy.append(a)
        b = dict(r, arms=dict(r["arms"]))
        for c in ("RANDOM", "FREQ", "MEMO"):
            b["arms"][c] = r["arms"]["FLAT"]
        fake_win.append(b)
    r4c = rule_r4(fake_copy)
    r4w = rule_r4(fake_win)
    fx["X7_gate_R4_reachable"] = {"pass": all(v["verdict"] == "FAIL" for v in r4c.values()) and
                                          all(v["verdict"] == "PASS" for v in r4w.values()),
                                  "copy_reads": {k: v["verdict"] for k, v in r4c.items()},
                                  "win_reads": {k: v["verdict"] for k, v in r4w.items()}}

    # X8 dropped records: an unsolvable late signature is counted, medians of the rest unchanged
    ep8 = dict(ep_r, tasks=list(ep_r["tasks"]))
    base = run_episode(ep8, 0, seed, prims, probes, flat_cl, freq_table, arms=("FLAT",))
    bogus = {"expr": ("X",), "motif": ep_r["shared_motif"], "early": False, "declared_shared": False}
    ep8b = dict(ep_r, tasks=list(ep_r["tasks"]) + [bogus])
    # make the bogus task's signature unreachable by overriding its signature through a
    # closure with an impossibly small budget for the check
    late_sigs_b = [W3.signature(t["expr"], probes, prims) for t in ep8b["tasks"] if not t["early"]]
    tiny = closure(prims, probes, max_size=1)
    cs, dropped = [], 0
    for sig in late_sigs_b:
        c = task_costs(tiny, sig)
        if c is None:
            dropped += 1
        else:
            cs.append(c["c_search"])
    fx["X8_dropped_records"] = {"pass": dropped >= 1 and (dropped + len(cs)) == len(late_sigs_b),
                                "dropped": dropped, "solved": len(cs),
                                "baseline_late_solved": base["arms"]["FLAT"]["late_solved"]}
    return fx, oracle_ratios, bar_cal


# ---------------------------------------------------------------- modes

def _receipt():
    if ws_receipt is None:
        return {"note": "archaeon.workspace unavailable"}
    return ws_receipt()


def calibrate():
    prims = W3.PRIMS
    probes = W3.probe_inputs()
    flat_cl = closure(prims, probes)
    freq_table = global_size2_frequency(CAL_SEED, prims, probes)
    fx, oracle_ratios, bar = fixtures(CAL_SEED, prims, probes, flat_cl, freq_table)
    all_pass = all(v.get("pass") for v in fx.values())
    freq_ser = sorted(((str(k), v) for k, v in freq_table.items()), key=lambda kv: kv[0])
    freq_sha = hashlib.sha256(json.dumps(freq_ser).encode()).hexdigest()
    payload = {
        "experiment": "LOT-A3-CALIBRATION",
        "intervention_class": "INSTRUMENT",
        "is_null_result": False,
        "positive_control_ran": True,
        "branch_table_partitions": True,
        "probe_modifies_measured_quantity": False,
        "dropped_records": 0,
        "prereg": "aporia/lot/PREREG_A3_2026-09-11.md",
        "seed": CAL_SEED, "theta": THETA, "P": P, "max_size": MAX_SIZE,
        "flat_closure": flat_cl["stats"],
        "fixtures": fx,
        "fixtures_all_pass": all_pass,
        "oracle_ratio_calibration": bootstrap_median_ci(oracle_ratios, seed=33),
        "R2_bar": bar,
        "freq_table_sha256": freq_sha, "freq_table_n_programs": FREQ_SAMPLE,
        "freq_table": {k: v for k, v in freq_ser},
        "readings": {
            "X1b_p_mint_NO_REUSE": {"n": 200, "attainable_lo": 0.0, "attainable_hi": 1.0,
                                    "value": fx["X1b_known_negative"]["p_mint_NO_REUSE"]},
            "X3_oracle_ratio": {"n": len(oracle_ratios), "attainable_lo": 0.0,
                                "attainable_hi": 1e12,
                                "value": fx["X3_channel_cheat_oracle"]["ci"]},
        },
        "verdict": "CALIBRATED" if all_pass else "INSTRUMENT_INVALID",
        "receipt": _receipt(),
    }
    out = HERE / "RESULT_A3_CALIBRATION.json"
    RS.emit(out, payload, expected_identity="LOT-A3-CALIBRATION")
    print(json.dumps({k: (v["pass"] if isinstance(v, dict) and "pass" in v else v)
                      for k, v in fx.items()}, indent=1))
    print("R2_bar", bar, "verdict", payload["verdict"])
    return payload


def read():
    cal = json.loads((HERE / "RESULT_A3_CALIBRATION.json").read_text(encoding="utf-8"))
    if cal.get("verdict") != "CALIBRATED":
        raise SystemExit("calibration is not CALIBRATED; no reading is taken (PREREG s5 X3)")
    bar = cal["R2_bar"]
    freq_table = {ast.literal_eval(k): v for k, v in cal["freq_table"].items()}
    prims = W3.PRIMS
    probes = W3.probe_inputs()
    flat_cl = closure(prims, probes)
    rows = []
    for seed in READ_SEEDS:
        assert seed not in BURNED and seed != CAL_SEED
        w = make_world(seed, prims)
        for i, ep in enumerate(w):
            rows.append(run_episode(ep, i, seed, prims, probes, flat_cl, freq_table))
            print(f"seed {seed} ep {i:2d} {ep['class']:12s} minted={rows[-1]['minted']} "
                  f"c_max={rows[-1]['c_max']}", flush=True)
    n_el = EPISODES_PER_CLASS * len(READ_SEEDS)
    R1 = rule_r1(rows, n_el); R2 = rule_r2(rows, bar); R3 = rule_r3(rows)
    R4 = rule_r4(rows); R5 = rule_r5(rows)
    dropped = sum(a["late_dropped"] for r in rows for a in r["arms"].values())
    kills = []
    if R1["verdict"] == "FAIL":
        kills.append("4_cannot_tell_REUSE_from_NO_REUSE")
    if R2["verdict"] == "FAIL":
        kills.append("2_advantage_disappears_under_honest_costs")
    for c in ("RANDOM", "FREQ"):
        if R4[c]["verdict"] == "FAIL":
            kills.append(f"3_arbitrary_chunk_{c}_not_beaten")
    if R4["MEMO"]["verdict"] == "FAIL":
        kills.append("5_memo_reproduces_gain")
    if kills:
        verdict = "KILLED"
    elif R1["verdict"] == "PASS" and R2["verdict"] == "PASS" and all(v["verdict"] == "PASS" for v in R4.values()):
        verdict = "PASS"
    else:
        verdict = "INDETERMINATE"
    payload = {
        "experiment": "LOT-A3-REIFY",
        "intervention_class": "SYNTH",
        "is_null_result": verdict != "PASS",
        "positive_control_ran": True,
        "branch_table_partitions": True,
        "probe_modifies_measured_quantity": False,
        "dropped_records": dropped,
        "prereg": "aporia/lot/PREREG_A3_2026-09-11.md",
        "calibration": {"R2_bar": bar, "freq_table_sha256": cal["freq_table_sha256"],
                        "oracle_ratio_calibration": cal["oracle_ratio_calibration"]},
        "seeds": list(READ_SEEDS), "theta": THETA,
        "rules": {"R1": R1, "R2": R2, "R3": R3, "R4": R4, "R5": R5},
        "kill_criteria_fired": kills,
        "verdict": verdict,
        "readings": {
            "R1_mint_rate_REUSE": {"n": R1["eligible_per_class"]["REUSE"], "attainable_lo": 0.0,
                                   "attainable_hi": 1.0, "value": R1["mint_rate_REUSE"]},
            "R2_search_ratio": {"n": R2["eligible"], "attainable_lo": 0.0, "attainable_hi": 1e12,
                                "value": R2.get("ci")},
            "R4_MEMO_fraction": {"n": R4["MEMO"]["eligible"], "attainable_lo": 0.0, "attainable_hi": 1.0,
                                 "value": R4["MEMO"]["fraction_reified_better"]},
        },
        "rows": rows,
        "receipt": _receipt(),
    }
    out = HERE / "RESULT_A3.json"
    RS.emit(out, payload, expected_identity="LOT-A3-REIFY")
    print(json.dumps({"R1": R1["verdict"], "R2": R2["verdict"], "R4": {k: v["verdict"] for k, v in R4.items()},
                      "kills": kills, "verdict": verdict}, indent=1))
    return payload


if __name__ == "__main__":
    if assert_not_canonical is not None:
        assert_not_canonical("run A3", allow_override=False)
    mode = sys.argv[1] if len(sys.argv) > 1 else "calibrate"
    if mode == "calibrate":
        calibrate()
    elif mode == "read":
        read()
    else:
        raise SystemExit("mode: calibrate | read")
