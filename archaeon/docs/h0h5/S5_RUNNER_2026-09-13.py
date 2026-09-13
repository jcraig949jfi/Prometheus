"""S5 runner (preregistered in S5_PREREG_2026-09-13.json). The hidden target lives only here (LOOP 4 stand-in).

WORLD CONSTRUCTION IS TARGET-FREE: a world is an evidence STATE (fossils with chosen mismatch counts, from the
shell / two-block families), and the harness then enumerates EVERY feasible target of that state as a census
(uniform prior over T(E), exactly the producers' named prior). No state is chosen by any producer's result.
Run from the repository root:  python archaeon/docs/h0h5/S5_RUNNER_2026-09-13.py [--quick] [--lengths 8,9] [--tag X]
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from archaeon.producer import acquisition as AQ, fossil_inference as FI, s4_producers as P, s5_producers as O5, s5_coordinates as C5  # noqa: E402

HERE = Path(__file__).parent
PRE = json.loads((HERE / "S5_PREREG_2026-09-13.json").read_text(encoding="utf-8"))
LENGTHS = PRE["worlds"]["L"]; NMAX = {int(k): v for k, v in PRE["worlds"]["max_feasible_targets"].items()}; NMIN = PRE["worlds"]["min_feasible_targets"]
B = PRE["budget"]["probes_per_arm"]; NAUC_B = PRE["secondary_metrics"]["nAUC_first_probes"]
ARMS = PRE["arms"]["order"]; BAR = PRE["verdict_rule"]["separation_bar_relative"]
QUICK = "--quick" in sys.argv; TAG = ""
if "--lengths" in sys.argv:
    LENGTHS = [int(x) for x in sys.argv[sys.argv.index("--lengths") + 1].split(",")]
if "--tag" in sys.argv:
    TAG = "_" + sys.argv[sys.argv.index("--tag") + 1]


def score(x, t):
    return sum(a == b for a, b in zip(x, t)) / len(t)


def bits(x, L):
    return format(x, "0%db" % L)[::-1]


# ------------------------------------------------------------------ worlds (states), target-free
def state_family(L):
    fam = [("shell", {"m": m}, [(0, m)]) for m in range(1, L)]
    for a in range(1, L):
        b = L - a; xa = (1 << a) - 1
        for uA in range(0, a + 1):
            for uB in range(0, b + 1):
                fam.append(("prod2", {"a": a, "b": b, "uA": uA, "uB": uB}, [(0, uA + uB), (xa, (a - uA) + uB)]))
    out = []; seen = set()
    for name, par, fos in fam:
        fossils = [FI.Fossil(bits(x, L), (L - m) / L) for x, m in fos]
        try:
            targets = FI.enumerate_targets(fossils)
        except Exception:
            continue
        N = len(targets)
        if N < NMIN or N > NMAX[L]:
            continue
        key = tuple(sorted(targets))
        if key in seen:
            continue
        seen.add(key)
        out.append({"state_id": "L%d_%s_%s" % (L, name, "_".join("%s%d" % (k, v) for k, v in par.items())), "L": L, "family": name, "par": par,
                    "fossils": [(f.bits, f.score) for f in fossils], "N": N, "targets": sorted(targets)})
    return out


# ------------------------------------------------------------------ exact per-decision-state quantities (target-free)
def exact_state(E):
    """V*(s), the optimal probe, and a closure giving Q*(s, q) for any probe q, from O's memoised DP."""
    L = E[0].length; D = O5._dist_matrix(L); stats = {"memo_hits": 0, "fresh_subsets": 0}
    S = np.array(sorted(O5._as_int(t) for t in FI.enumerate_targets(list(E))), dtype=np.int64)
    v, q = O5._dp(L, D, S, stats)
    def Q(probe):
        qi = O5._as_int(probe); row = D[qi, S]; c = 1.0
        for e in np.unique(row):
            cell = S[row == e]
            if len(cell) > 1:
                c += (len(cell) / len(S)) * O5._dp(L, D, cell, stats)[0]
        return c
    return v, Q, S, D


def coordinates_at(E, g_probe):
    """Cheap pre-target coordinates at decision state E for the producer's chosen probe g (all from E and {0,1}^L)."""
    L = E[0].length; S = C5._feasible_ints(E); N = len(S); n = C5._counts(L, S)
    er = (n.astype(np.int64) ** 2).sum(1); Pm = n / N
    with np.errstate(divide="ignore", invalid="ignore"):
        H = -(np.where(Pm > 0, Pm * np.log2(np.where(Pm > 0, Pm, 1.0)), 0.0)).sum(1)
    gi = O5._as_int(g_probe); er_g = int(er[gi]); H_g = float(H[gi])
    dominated = bool(((er <= er_g) & (H > H_g + 1e-12)).any())                     # kappa_H: a probe no worse on ER and strictly better on entropy exists
    er_class = np.flatnonzero(er == er.min())
    mult = {tuple(sorted(int(x) for x in n[q] if x)) for q in er_class}
    st = FI.infer(E); unres = st.count_known_blocks + st.ambiguous_blocks
    return {"N": N, "ER_g": er_g / N, "H_g": H_g, "ER_min": float(er.min() / N), "H_max_in_ER_class": float(H[er_class].max()), "H_max": float(H.max()),
            "pool_suboptimal": er_g > int(er.min()), "kappa_H": dominated, "kappa_tie": len(mult) >= 2,
            "kappa_proxy": bool(len(unres) == 2 and min(b["size"] for b in unres) >= 3), "n_unresolved_blocks": len(unres)}


# ------------------------------------------------------------------ arms
def propose(arm, E, L, si, routed_rows):
    if arm == "U":
        return P.produce_U(L, si), None
    if arm == "G":
        return P.produce_G(E, si), None
    if arm == "GH":
        return O5.produce_GH(E, si), None
    if arm == "W":
        return P.produce_W(E, si), None
    if arm == "M":
        return P.produce_M(E, si), None
    if arm == "O":
        return O5.produce_O(E, si, max_units=PRE["compute_bounds"]["O_max_units"], max_targets=PRE["compute_bounds"]["O_max_targets"]), None
    if arm == "RH":
        # routed: G's own proposal unless kappa_H fires at this state for that proposal, in which case O's
        pg = P.produce_G(E, dict(si, arm="G"))
        if pg.probe is None:
            return pg, {"routed_to_O": False, "kappa_H": None}
        c = coordinates_at(E, pg.probe)
        if c["kappa_H"]:
            po = O5.produce_O(E, dict(si, arm="O"), max_units=PRE["compute_bounds"]["O_max_units"], max_targets=PRE["compute_bounds"]["O_max_targets"])
            if po.probe is not None:
                po.extra["routed_from_G"] = pg.probe
                return po, {"routed_to_O": True, "kappa_H": True}
            return pg, {"routed_to_O": False, "kappa_H": True, "O_outcome": po.extra.get("outcome")}
        return pg, {"routed_to_O": False, "kappa_H": False}
    raise ValueError(arm)


def run_arm(arm, world, t, decision_rows):
    L = world["L"]; E = [FI.Fossil(b, s) for b, s in world["fossils"]]; traj = []; ident = None; exhausted = 0; scope = 0; o_calls = 0; units = 0; secs = 0.0
    for step in range(1, B + 1):
        st = AQ.feasible(E)
        if st.feasible_targets == 1:
            break
        si = {"lane": "s5", "L": L, "world": world["state_id"], "target_index": int(world["targets"].index(t)), "arm": arm, "step": step}
        p, route = propose(arm, E, L, si, decision_rows)
        secs += p.compute_seconds; units += int((p.ancestry or {}).get("work_units") or 0)
        if p.probe is None:
            if p.extra.get("outcome") == "BUDGET_EXHAUSTED":
                exhausted += 1
            else:
                scope += 1
            traj.append({"step": step, "probe": None, "outcome": p.extra.get("outcome"), "log2_after": math.log2(st.feasible_targets), "compute_s": p.compute_seconds})
            continue
        if arm == "O" or (route and route.get("routed_to_O")):
            o_calls += 1
        v = AQ.value(st, p.probe); s = score(p.probe, t); before = st.feasible_targets
        redundant = any(p.probe == f.bits for f in E) or v.er_numerator == before * before
        if arm in PRE["decision_state_audit"]["arms"] and step <= PRE["decision_state_audit"]["max_depth"]:
            vstar, Q, S, D = exact_state(E); c = coordinates_at(E, p.probe); qg = Q(p.probe)
            decision_rows.append(dict(c, L=L, state_id=world["state_id"], target_index=si["target_index"], arm=arm, step=step, probe=p.probe, snapshot=p.evidence_snapshot_id,
                                      V_star=vstar, Q_choice=qg, delta=qg - vstar, myopic_exact=bool(qg - vstar > 1e-9)))
        E.append(FI.Fossil(p.probe, s)); st2 = AQ.feasible(E)
        traj.append({"step": step, "probe": p.probe, "score": s, "log2_before": math.log2(before), "log2_after": math.log2(st2.feasible_targets), "gain_bits": math.log2(before) - math.log2(st2.feasible_targets),
                     "fixed_after": st2.n_fixed, "n_outcomes": v.n_outcomes, "entropy_bits": v.outcome_entropy_bits, "ER": v.expected_remaining, "compute_s": p.compute_seconds, "redundant": redundant,
                     "tie_class": len(p.tie_class), "snapshot": p.evidence_snapshot_id, "policy": p.evidence_policy, "producer_version": p.producer_version, "route": route})
        if ident is None and st2.feasible_targets == 1:
            ident = step
    final = AQ.feasible(E).feasible_targets
    first = [x["log2_after"] for x in traj][:NAUC_B]
    first += [first[-1] if first else math.log2(world["N"])] * (NAUC_B - len(first))
    return {"trajectory": traj, "identified_at": ident if ident else B + 1, "identified": final == 1, "final_log2": math.log2(final),
            "nAUC_0": sum(first) / (NAUC_B * math.log2(world["N"])), "mean_score": (sum(x["score"] for x in traj if x.get("probe")) / max(1, sum(1 for x in traj if x.get("probe")))),
            "compute_s": secs, "work_units": units, "budget_exhausted": exhausted, "scope_exceeded": scope, "o_calls": o_calls, "redundant": sum(1 for x in traj if x.get("redundant"))}


def sign_p(wins, n):
    from math import comb
    return sum(comb(n, j) for j in range(wins, n + 1)) / 2 ** n if n else None


def main():
    t_start = time.time(); worlds = []; decision_rows = []
    for L in LENGTHS:
        states = state_family(L)
        if QUICK:
            states = states[:6]
        print("L", L, "states", len(states), "targets", sum(s["N"] for s in states), flush=True)
        for w in states:
            E0 = [FI.Fossil(b, s) for b, s in w["fossils"]]
            w["root_coordinates"] = C5.all_coordinates(E0, with_two_step=(L <= 10))
            w["arms"] = {a: [] for a in ARMS}
            for t in w["targets"]:
                for a in ARMS:
                    w["arms"][a].append(run_arm(a, w, t, decision_rows))
            summ = {}
            for a in ARMS:
                rs = w["arms"][a]
                summ[a] = {"E_probes": sum(r["identified_at"] for r in rs) / len(rs), "identified_frac": sum(r["identified"] for r in rs) / len(rs), "mean_nAUC_0": sum(r["nAUC_0"] for r in rs) / len(rs),
                           "mean_score": sum(r["mean_score"] for r in rs) / len(rs), "compute_s": sum(r["compute_s"] for r in rs), "work_units": sum(r["work_units"] for r in rs),
                           "budget_exhausted": sum(r["budget_exhausted"] for r in rs), "scope_exceeded": sum(r["scope_exceeded"] for r in rs), "o_calls": sum(r["o_calls"] for r in rs),
                           "proposals": sum(len(r["trajectory"]) for r in rs), "redundant": sum(r["redundant"] for r in rs)}
            pairs = {}
            for a in ARMS:
                if a == "G":
                    continue
                d = [g["identified_at"] - x["identified_at"] for g, x in zip(w["arms"]["G"], w["arms"][a])]
                wins = sum(1 for v in d if v > 0); losses = sum(1 for v in d if v < 0)
                rel = (summ["G"]["E_probes"] - summ[a]["E_probes"]) / summ["G"]["E_probes"]
                pairs[a] = {"rel_advantage_over_G": rel, "arm_wins": wins, "G_wins": losses, "ties": len(d) - wins - losses, "separated_at_bar": bool(rel >= BAR and wins > losses)}
            w["summary"] = summ; w["pairs_vs_G"] = pairs
            print(w["state_id"], "N", w["N"], {a: round(summ[a]["E_probes"], 3) for a in ARMS}, "| rel vs G:", {a: round(pairs[a]["rel_advantage_over_G"], 3) for a in pairs}, "| RH O-calls", summ.get("RH", {}).get("o_calls"), "| t=%ds" % (time.time() - t_start), flush=True)
            worlds.append(w)
    res = evaluate(worlds, decision_rows)
    res["elapsed_s"] = time.time() - t_start
    out = HERE / ("S5_RESULTS%s_2026-09-13.json" % (TAG or ("_QUICK" if QUICK else "")))
    slim = []
    for w in worlds:
        slim.append({k: v for k, v in w.items() if k != "arms"} | {"arms": {a: [{k2: v2 for k2, v2 in r.items() if k2 != "trajectory"} | {"trajectory": [{k3: v3 for k3, v3 in x.items()} for x in r["trajectory"]]} for r in rs] for a, rs in w["arms"].items()}})
    res["worlds"] = slim; res["decision_states"] = decision_rows
    out.write_text(json.dumps(res, indent=1, default=lambda o: bool(o) if isinstance(o, np.bool_) else (float(o) if isinstance(o, (np.floating,)) else (int(o) if isinstance(o, np.integer) else str(o)))), encoding="utf-8")
    print("VERDICT", res["verdict"], "| O vs G:", res["world_level"]["O"], "| RH:", res["world_level"].get("RH"), "| GH:", res["world_level"].get("GH"))
    print("kappa audit:", res["decision_state_audit"])


def evaluate(worlds, decision_rows):
    R = PRE["verdict_rule"]; wl = {}
    n_states = len(worlds)
    for a in ARMS:
        if a == "G":
            continue
        seps = [w["pairs_vs_G"][a]["separated_at_bar"] for w in worlds]; rels = [w["pairs_vs_G"][a]["rel_advantage_over_G"] for w in worlds]
        wl[a] = {"states": n_states, "separated_states": sum(seps), "separated_frac": sum(seps) / n_states, "mean_rel_advantage": sum(rels) / n_states,
                 "worse_than_G_at_bar_states": sum(1 for r in rels if r <= -BAR), "budget_exhausted": sum(w["summary"][a]["budget_exhausted"] for w in worlds), "scope_exceeded": sum(w["summary"][a]["scope_exceeded"] for w in worlds),
                 "o_call_frac": (sum(w["summary"][a]["o_calls"] for w in worlds) / max(1, sum(w["summary"][a]["proposals"] for w in worlds))), "compute_s": sum(w["summary"][a]["compute_s"] for w in worlds)}
    # decision-state audit: does each cheap coordinate predict the exact per-state myopia flag of G's own choice?
    rows = [r for r in decision_rows if r["arm"] == "G"]; audit = {"n_decision_states": len(rows), "myopic_frac": (sum(r["myopic_exact"] for r in rows) / len(rows)) if rows else None}
    for k in ("kappa_H", "kappa_tie", "kappa_proxy", "pool_suboptimal"):
        pos = [r for r in rows if r[k]]; neg = [r for r in rows if not r[k]]
        tp = sum(r["myopic_exact"] for r in pos); fn = sum(r["myopic_exact"] for r in neg)
        audit[k] = {"fires": len(pos), "precision": (tp / len(pos)) if pos else None, "recall": (tp / (tp + fn)) if (tp + fn) else None, "myopia_rate_when_off": (fn / len(neg)) if neg else None,
                    "mean_delta_when_on": (sum(r["delta"] for r in pos) / len(pos)) if pos else None, "mean_delta_when_off": (sum(r["delta"] for r in neg) / len(neg)) if neg else None}
    # frozen verdict
    fail = []
    if wl["O"]["budget_exhausted"] or wl["O"]["scope_exceeded"]:
        fail.append("O could not complete on some proposal (BUDGET_EXHAUSTED/SCOPE_EXCEEDED)")
    if wl["O"]["worse_than_G_at_bar_states"]:
        fail.append("the exact optimum is worse than G at the bar in some state")
    if wl["U"]["separated_states"]:
        fail.append("blind U beats G at the bar in some state")
    if fail:
        verdict = "INSTRUMENT_FAILURE"
    else:
        o_sep = wl["O"]["separated_frac"] >= R["min_separated_state_fraction"] or wl["O"]["mean_rel_advantage"] >= BAR
        aud = audit["kappa_H"]; routes = (aud["precision"] is not None and aud["precision"] >= R["kappa_min_precision"] and aud["recall"] is not None and aud["recall"] >= R["kappa_min_recall"]
                                          and wl["RH"]["separated_frac"] >= R["min_separated_state_fraction"] and wl["RH"]["o_call_frac"] <= R["routed_max_O_call_fraction"])
        if not o_sep:
            verdict = "NO_SEPARATION"
        elif routes:
            verdict = "PLURALITY_SUPPORTED"
        else:
            verdict = "DIFFERENCE_WITHOUT_ROUTABILITY"
    return {"schema": "archaeon.fossil_metabolism_s5.results.v0", "preregistration": "S5_PREREG_2026-09-13.json", "producer_versions": {"s4": P.PRODUCER_VERSION, "s5": O5.PRODUCER_VERSION}, "quick": QUICK,
            "world_level": wl, "decision_state_audit": audit, "instrument_failures": fail, "verdict": verdict}


def combine(paths):
    """Pool per-L result files for the verdict exactly as evaluate() defines it (the prereg pools L 8 and L 9)."""
    worlds = []; rows = []
    for p in paths:
        r = json.loads(Path(p).read_text(encoding="utf-8")); worlds += r["worlds"]; rows += r["decision_states"]
    res = evaluate(worlds, rows); res["combined_from"] = [str(p) for p in paths]; res["per_L"] = {}
    for L in sorted({w["L"] for w in worlds}):
        res["per_L"][str(L)] = evaluate([w for w in worlds if w["L"] == L], [x for x in rows if x["L"] == L])
    out = HERE / "S5_RESULTS_COMBINED_2026-09-13.json"; out.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print("COMBINED VERDICT", res["verdict"], "| per L:", {k: v["verdict"] for k, v in res["per_L"].items()}); print(json.dumps(res["world_level"], indent=0)); print(json.dumps(res["decision_state_audit"], indent=0))


if __name__ == "__main__":
    if "--combine" in sys.argv:
        combine(sys.argv[sys.argv.index("--combine") + 1:])
    else:
        main()
