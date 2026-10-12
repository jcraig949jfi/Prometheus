"""C-018-T040 synthetic constructions against the FROZEN evaluator (rso/aether/evaluate.py, FROZEN v1.0.0).

Every function builds a record (meta, arrays) or a row set and asks the frozen functions what they say. Nothing here is
production code and nothing here changes a frozen file. Attack tooling only (roles/Pallas/RESPONSIBILITIES.md s2).

    B1  tree-tamper        the attribution tree's parent / gen / type are producer fields; tree_check verifies only
                           sites and first ticks (evaluate.py:91-100), and the replay compares arrays only
                           (confirm.py:157-159). Re-parenting B's subtree turns INSUFFICIENT into CONFIRMED with
                           problems == []; a one-byte type flip turns NO_CUT into an evaluable class.
    B2  no-cut honesty     disposition() (evaluate.py:177-194) has no status for "too few evaluable units": all-NO_CUT
                           populations are read as NEITHER or CONTENT_WITHOUT_INTERVENTIONAL_ANCESTRY.
    B3  radius-only cond.  conditioned_excess (evaluate.py:146-152) conditions on the radius band only; the content
                           evidence may come entirely from units with no demonstrated ancestry.
    B4  late N             a non-ancestor that first diverges AFTER every target cannot remove any target (CUT_N equals
                           IMPULSE until N diverges: adapter.py:66-90); ancestry() (evaluate.py:67) calls such an N
                           non-vacuous and the unit CONFIRMED.
"""
import copy
import json
import math
import os

import numpy as np

from rso.aether import adapter as A, evaluate as E
import prop01_tree as TR           # noqa: E402  (Aether, unmodified; path set by rso.aether.demand.fixtures)

REC = os.path.join(os.path.dirname(os.path.abspath(A.__file__)), "qual", "records")
N16 = 16


# ---------------------------------------------------------------- shared helpers
def tree_invariants(tree, n):
    """Structural invariants every native prop01 tree satisfies (prop01_run.py:181-199: a parent is a 4-neighbour that
    was divergent BEFORE the tick; gen = parent gen + 1). Counts of violations; a tamper that respects them is invisible
    to any structural check, only a replay of the attribution can tell."""
    par = dict(zip(tree["site"], tree["parent"]))
    ft = dict(zip(tree["site"], tree["ftick"]))
    gen = dict(zip(tree["site"], tree["gen"]))
    bad_adj = bad_ord = bad_gen = 0
    for s, p in par.items():
        if p < 0:
            continue
        sy, sx = divmod(s, n)
        py, px = divmod(p, n)
        dy = min((sy - py) % n, (py - sy) % n)
        dx = min((sx - px) % n, (px - sx) % n)
        if dy + dx != 1:
            bad_adj += 1
        if not ft[p] < ft[s]:
            bad_ord += 1
        if gen[s] >= 0 and gen[p] >= 0 and gen[s] != gen[p] + 1:
            bad_gen += 1
    return {"non_adjacent_parent": bad_adj, "parent_not_earlier": bad_ord, "gen_not_parent_plus_1": bad_gen}


def recompute_gen(tree):
    """gen from parent (root = the gen-0 site; unknown parents (-2) keep gen -1)."""
    par = dict(zip(tree["site"], tree["parent"]))
    out = []
    for s in tree["site"]:
        g, p, seen = 0, par[s], set()
        if p == -2:
            out.append(-1)
            continue
        while p >= 0 and p not in seen:
            seen.add(p)
            g, p = g + 1, par.get(p, -1)
        out.append(g)
    tree["gen"] = out
    return tree


def load_dev(name):
    return A.load_unit(os.path.join(REC, name))


def classify(meta, a):
    r = E.ancestry(meta, a)
    return {"cls": r["cls"], "removed_B": r["removed_B"], "removed_N": r["removed_N"], "r_int": r["r_int"],
            "n_targets": len(r["targets"]), "n_I": len(r["I"])}


def _set_parent(tree, s, p):
    i = tree["site"].index(s)
    tree["parent"][i] = p


# ---------------------------------------------------------------- B1 tree tamper (dev native records, arrays untouched)
def b1_naive(meta, a):
    """RX k=0: re-parent three sites of the interventional set I (divergent in IMPULSE, never in CUT_B, divergent in
    CUT_N) directly under B, ignoring adjacency. The arrays are untouched."""
    m = json.loads(json.dumps(meta))
    before = classify(meta, a)
    r = E.ancestry(meta, a)
    B = m["B"]
    cands = [s for s in r["I"] if s not in TR.descendants(m["tree"], B) and s != m["N"]][:3]
    for s in cands:
        _set_parent(m["tree"], s, B)
    recompute_gen(m["tree"])
    after = classify(m, a)
    return {"before": before, "after": after, "reparented": cands, "problems_after": E.tree_check(m, a) + E.binding_problems(m, a),
            "invariants_after": tree_invariants(m["tree"], m["n"]), "invariants_before": tree_invariants(meta["tree"], meta["n"]),
            "replay_arrays_check_passes": A.arrays_sha256(a) == meta["arrays_sha256"]}


def b1_invariant(meta, a):
    """RX k=0: the same, respecting every structural invariant (4-adjacency, parent earlier, gen = parent + 1), chosen
    at run time from I: a chain B -> s1 -> s2 of adjacent later-diverging sites plus one more adjacent child."""
    m = json.loads(json.dumps(meta))
    before = classify(meta, a)
    r = E.ancestry(meta, a)
    n, B = m["n"], m["B"]
    ft = dict(zip(m["tree"]["site"], m["tree"]["ftick"]))
    desc0 = TR.descendants(m["tree"], B)

    def adj(s, p):
        sy, sx = divmod(s, n)
        py, px = divmod(p, n)
        return min((sy - py) % n, (py - sy) % n) + min((sx - px) % n, (px - sx) % n) == 1
    pool = [s for s in r["I"] if s not in desc0 and s != m["N"]]
    moved = []
    # greedy: attach any pool site adjacent to a current member of B's subtree with a later first tick
    members = {B} | set(desc0)
    changed = True
    while changed:
        changed = False
        for s in sorted(pool, key=lambda s: ft[s]):
            if s in members:
                continue
            for p in sorted(members, key=lambda p: ft[p]):
                if adj(s, p) and ft[p] < ft[s]:
                    _set_parent(m["tree"], s, p)
                    members.add(s)
                    moved.append((s, p))
                    changed = True
                    break
    recompute_gen(m["tree"])
    after = classify(m, a)
    return {"before": before, "after": after, "reparented": moved, "problems_after": E.tree_check(m, a) + E.binding_problems(m, a),
            "invariants_after": tree_invariants(m["tree"], m["n"]),
            "replay_arrays_check_passes": A.arrays_sha256(a) == meta["arrays_sha256"]}


def b1_typeflip(meta, a):
    """RX k=3 (NO_CUT: the only generation-2 child is RULE-type, PREREGISTRATION s5): flip that one type byte to CARRY,
    record the B / N the rules now give (the producer writes meta), and read the class from the stored clamp arrays,
    which for a NO_CUT unit are all -1 (adapter.py:150-151: no clamp world was run)."""
    m = json.loads(json.dumps(meta))
    before = classify(meta, a)
    tr = m["tree"]
    g2 = [i for i, g in enumerate(tr["gen"]) if g == 2]
    flipped = []
    for i in g2:
        if tr["type"][i] == 3:
            tr["type"][i] = 2
            flipped.append(tr["site"][i])
            break
    B, _ = TR.choose_cut({"tree": tr})
    Nn = A.choose_nonancestor(tr, B, m["origin"], m["n"]) if B is not None else None
    m["B"], m["N"] = B, Nn
    after = classify(m, a)
    cb, cn = a["ftick_cutB"], a["ftick_cutN"]
    return {"before": before, "after": after, "flipped_sites": flipped, "B_after": B, "N_after": Nn,
            "clamp_arrays_all_minus_one": bool((cb < 0).all() and (cn < 0).all()),
            "problems_after": E.tree_check(m, a) + E.binding_problems(m, a), "invariants_after": tree_invariants(tr, m["n"]),
            "replay_arrays_check_passes": A.arrays_sha256(a) == meta["arrays_sha256"]}


def b1():
    m0, a0 = load_dev("native_RX_0")
    m3, a3 = load_dev("native_RX_3")
    return {"naive": b1_naive(m0, a0), "invariant": b1_invariant(m0, a0), "typeflip": b1_typeflip(m3, a3)}


# ---------------------------------------------------------------- B2 / B3 rows and accuracy dicts (frozen law_summary + disposition)
def row(cls, r_int=0, seed=0):
    ev = cls in ("CONFIRMED", "NONSPECIFIC", "NOT_INTERVENTIONAL")
    return {"seed": seed, "cls": cls, "r_int": r_int, "agreement": 1.0 if ev else None, "n_targets": 3 if ev else 0,
            "light_cone_ok": True}


def acc(seeds, value, T=4, R=6):
    return {s: np.full((T, R), value) for s in seeds}


def dispo(rows, acc_, acc_null):
    L = E.law_summary(rows, acc_, acc_null)
    d = E.disposition({"completeness": "COMPLETE", "records_ok": True, "qualified": True, "law": L})
    return d, L


def b2():
    """No-cut honesty. (a) 48 NO_CUT with decodable content; (b) 44 NO_CUT + 4 CONFIRMED r_int 3 (one short of the
    need of 5); (c) 16 V1 all NO_CUT; (e) 43 NO_CUT + 5 CONFIRMED r_int 2 at chance content (P2 holds on 5 units)."""
    out = {}
    rows = [row("NO_CUT", seed=s) for s in range(48)]
    d, L = dispo(rows, acc(range(48), 1.0), acc(range(48), 0.125))
    out["a_all_nocut_with_content"] = {"disposition": d, "n_evaluable": 0, "classes": L["classes"]}
    rows = [row("NO_CUT", seed=s) for s in range(44)] + [row("CONFIRMED", 3, seed=44 + i) for i in range(4)]
    d, L = dispo(rows, acc(range(48), 0.125), acc(range(48), 0.125))
    out["b_44_nocut_4_confirmed_r3"] = {"disposition": d, "n_evaluable": 4, "confirmed_r2": L["confirmed_r2"],
                                        "need": max(3, math.ceil(0.1 * 48)), "reach_band": L["reach_band"]}
    rows = [row("NO_CUT", seed=s) for s in range(16)]
    d, L = dispo(rows, acc(range(16), 0.125), acc(range(16), 0.125))
    out["c_v1_all_nocut"] = {"disposition": d, "n_evaluable": 0}
    rows = [row("NO_CUT", seed=s) for s in range(43)] + [row("CONFIRMED", 2, seed=43 + i) for i in range(5)]
    d, L = dispo(rows, acc(range(48), 0.125), acc(range(48), 0.125))
    out["e_43_nocut_5_confirmed_r2"] = {"disposition": d, "n_evaluable": 5, "confirmed_r2": L["confirmed_r2"], "need": 5}
    out["statuses_available"] = ["INCOMPLETE", "REFUSED", "REFUSED_RECORD_INCONSISTENT", "DETECTION_UNQUALIFIED",
                                 "ANCESTRY_WITH_CONTENT", "CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE_CONTENT",
                                 "CONTENT_WITHOUT_INTERVENTIONAL_ANCESTRY", "NEITHER"]
    return out


def b3():
    """Radius-only conditioning: 5 CONFIRMED units (r_int 2) whose held-out accuracy is chance; 43 NO_CUT units whose
    accuracy is 1.0. conditioned_excess averages over ALL seeds at radii 2..band."""
    rows = [row("CONFIRMED", 2, seed=s) for s in range(5)] + [row("NO_CUT", seed=s) for s in range(5, 48)]
    ac = {**acc(range(5), 0.125), **acc(range(5, 48), 1.0)}
    d, L = dispo(rows, ac, acc(range(48), 0.125))
    conf_only = float(np.mean([(ac[s][:, 1:2] - 0.125).mean() for s in range(5)]))
    return {"disposition": d, "reach_band": L["reach_band"], "content_excess_cond_all_seeds": round(L["content_excess_cond"], 4),
            "content_excess_cond_confirmed_seeds_only": round(conf_only, 4), "n_confirmed": 5, "n_nocut": 43}


# ---------------------------------------------------------------- B4 late N (synthetic record, exact)
def b4(ft_n=50, n=N16, origin=(8, 3)):
    """East chain O..O+6 (first tick = distance), B = O+2, targets O+3..O+5 at ticks 3, 4, 5. N = a divergent site off
    the chain, first divergent at tick ft_n > 5, clamped in CUT_N. Because CUT_N is IMPULSE until N diverges, every
    target's CUT_N first tick equals its IMPULSE tick by construction: N cannot remove anything."""
    snap = np.zeros((5, n, n), np.uint8)
    imp = snap.copy()
    imp[3][origin] ^= 1
    ft = {w: np.full(n * n, -1, np.int16) for w in ("impulse", "cutB", "cutN")}
    sites = [origin[0] * n + origin[1] + c for c in range(7)]
    for c, s in enumerate(sites):
        ft["impulse"][s] = c
        ft["cutB"][s] = c if c < 2 else -1          # B's clamp removes everything downstream of B
        ft["cutN"][s] = c                           # N's clamp (late N) removes nothing on the chain
    Ns = (origin[0] - 1) * n + origin[1] + 1       # off-chain divergent site
    ft["impulse"][Ns], ft["cutB"][Ns], ft["cutN"][Ns] = ft_n, ft_n, -1
    a = {"snap": snap, "imp": imp, "ftick_impulse": ft["impulse"], "ftick_cutB": ft["cutB"], "ftick_cutN": ft["cutN"]}
    meta = {"kind": "fixture", "n": n, "origin": sites[0], "B": sites[2], "N": Ns, "targets": sites[3:6]}
    r = E.ancestry(meta, a)
    tks = [int(a["ftick_impulse"][s]) for s in meta["targets"]]
    return {"cls": r["cls"], "removed_B": r["removed_B"], "removed_N": r["removed_N"], "ftick_N": ft_n, "targets_ftick": tks,
            "n_targets_live_for_N": sum(1 for t in tks if t > ft_n), "vacuous_by_evaluator": r["cls"] == "CONTROL_VACUOUS"}


def truncate(a, Hp):
    """Horizon counterfactual on stored arrays: divergences after tick Hp are 'never' (the recorder with H = Hp)."""
    b = {k: v.copy() for k, v in a.items()}
    for w in ("ftick_impulse", "ftick_cutB", "ftick_cutN"):
        b[w][b[w] > Hp] = -1
    return b


if __name__ == "__main__":
    import sys
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    out = {}
    if which in ("b1", "all"):
        out["B1"] = b1()
    if which in ("b2", "all"):
        out["B2"] = b2()
    if which in ("b3", "all"):
        out["B3"] = b3()
    if which in ("b4", "all"):
        out["B4"] = b4()
    print(json.dumps(out, indent=1, default=str))
