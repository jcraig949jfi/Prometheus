"""S4 runner (preregistered in S4_PREREG_2026-09-12.json). The hidden target
lives only here (LOOP 4 stand-in); producers receive fossils or nothing.
Run from the repository root: python archaeon/docs/h0h5/S4_RUNNER_2026-09-12.py [--quick]
"""
from __future__ import annotations

import json
import math
import random
import sys
import time
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from archaeon.producer import acquisition as AQ, fossil_inference as FI, s4_producers as P  # noqa: E402

PRE = json.loads((Path(__file__).parent / "S4_PREREG_2026-09-12.json").read_text(encoding="utf-8"))
LENGTHS = PRE["regimes"]["L"]; N0S = PRE["regimes"]["initial_fossils_n0"]; SEEDS = {int(k): v for k, v in PRE["regimes"]["seeds"].items()}
BUDGET = {int(k): v for k, v in PRE["budget"]["probes_per_arm"].items()}
QUICK = "--quick" in sys.argv
if QUICK:
    SEEDS = {k: max(2, v // 10) for k, v in SEEDS.items()}
# SUBSET mode (2026-09-12 22:4x UTC, after the full batch's L 32 tail was stopped as COMPUTATIONALLY_INTRACTABLE):
# --lengths 8,12,16,24 --seeds 10 --tag SUBSET  runs the same preregistered design on fewer seeds so the
# SECONDARY analyses (trajectories, complementarity, convergence, cost) have rows; the PRIMARY verdict comes
# from the full batch log (S4_PRIMARY_FROM_LOG_2026-09-12.json). Labelled as a subset in the output file name.
TAG = ""
if "--lengths" in sys.argv:
    LENGTHS = [int(x) for x in sys.argv[sys.argv.index("--lengths") + 1].split(",")]
if "--seeds" in sys.argv:
    n = int(sys.argv[sys.argv.index("--seeds") + 1]); SEEDS = {k: min(v, n) for k, v in SEEDS.items()}
if "--tag" in sys.argv:
    TAG = "_" + sys.argv[sys.argv.index("--tag") + 1]


def score(x, t):
    return sum(a == b for a, b in zip(x, t)) / len(t)


def initial_evidence(L, n0, rng, t):
    x0 = "".join(rng.choice("01") for _ in range(L)); E = [FI.Fossil(x0, score(x0, t))]
    if n0 == 3:
        j = rng.randrange(L); x1 = x0[:j] + ("1" if x0[j] == "0" else "0") + x0[j + 1:]
        x2 = "".join(rng.choice("01") for _ in range(L))
        E += [FI.Fossil(x1, score(x1, t)), FI.Fossil(x2, score(x2, t))]
    return E


def run_arm(arm, L, t, E0, B, world_seed):
    E = list(E0); traj = []; ident = None
    for step in range(1, B + 1):
        si = {"lane": "s4", "L": L, "world": world_seed, "arm": arm, "step": step}
        st = AQ.feasible(E)
        if arm == "U":
            p = P.produce_U(L, si)
        elif arm == "G":
            p = P.produce_G(E, si)
        elif arm == "W":
            p = P.produce_W(E, si)
        else:
            p = P.produce_M(E, si)
        if p.compute_seconds > 60.0 and arm != "U":
            # preregistered computational bound: the arm is COMPUTATIONALLY_INTRACTABLE in this regime
            return {"trajectory": traj, "nAUC": None, "identified_at": None, "final_log2": None, "final_fixed": None, "mean_score": None,
                    "total_compute_s": sum(x["compute_s"] for x in traj) + p.compute_seconds, "max_compute_s": p.compute_seconds, "redundant_probes": None, "intractable_steps": 1, "intractable": True}
        v = AQ.value(st, p.probe)
        s = score(p.probe, t); before = st.feasible_targets
        redundant = any(p.probe == f.bits for f in E) or v.er_numerator == before * before
        E.append(FI.Fossil(p.probe, s)); st2 = AQ.feasible(E)
        traj.append({"step": step, "probe": p.probe, "score": s, "log2_before": math.log2(before), "log2_after": math.log2(st2.feasible_targets),
                     "gain_bits": math.log2(before) - math.log2(st2.feasible_targets), "fixed_after": st2.n_fixed, "dist_nearest": min(AQ.hamming(p.probe, f.bits) for f in E[:-1]),
                     "n_outcomes": v.n_outcomes, "entropy_bits": v.outcome_entropy_bits, "ER": v.expected_remaining, "compute_s": p.compute_seconds, "redundant": redundant,
                     "tie_class": len(p.tie_class), "intractable": bool(p.extra.get("intractable")), "snapshot": p.evidence_snapshot_id, "policy": p.evidence_policy})
        if ident is None and st2.feasible_targets == 1:
            ident = step
    nauc = sum(x["log2_after"] for x in traj) / (B * L)
    return {"trajectory": traj, "nAUC": nauc, "identified_at": ident if ident else B + 1, "final_log2": traj[-1]["log2_after"], "final_fixed": traj[-1]["fixed_after"],
            "mean_score": sum(x["score"] for x in traj) / B, "total_compute_s": sum(x["compute_s"] for x in traj), "max_compute_s": max(x["compute_s"] for x in traj),
            "redundant_probes": sum(1 for x in traj if x["redundant"]), "intractable_steps": sum(1 for x in traj if x["intractable"])}


def counterfactual_gains(L, t, E0, B, world_seed):
    """Complementarity at the SAME state: along G's own trajectory, what each
    other producer would have gained from that state (evaluated on G's
    evidence, not on their own lineages)."""
    E = list(E0); rows = []
    for step in range(1, B + 1):
        st = AQ.feasible(E); si = {"lane": "s4", "L": L, "world": world_seed, "arm": "G", "step": step}
        pg = P.produce_G(E, si); pw = P.produce_W(E, si); pu = P.produce_U(L, dict(si, arm="U"))
        if pg.compute_seconds > 60.0 or pw.compute_seconds > 60.0:
            rows.append({"step": step, "log2_before": math.log2(st.feasible_targets), "n_fixed": st.n_fixed, "gains": {"G": 0.0, "W": 0.0, "U": 0.0}, "same_probe_G_W": pg.probe == pw.probe, "ER_G": pg.objective_value, "ER_W": pw.objective_value, "intractable": True}); break
        cands = {"G": pg.probe, "W": pw.probe, "U": pu.probe}
        if L <= 16:
            cands["M"] = P.produce_M(E, dict(si, arm="M")).probe
        gains = {}
        for k, q in cands.items():
            s = score(q, t); st2 = AQ.feasible(E + [FI.Fossil(q, s)]); gains[k] = math.log2(st.feasible_targets) - math.log2(st2.feasible_targets)
        rows.append({"step": step, "log2_before": math.log2(st.feasible_targets), "n_fixed": st.n_fixed, "gains": gains, "same_probe_G_W": pg.probe == pw.probe, "ER_G": pg.objective_value, "ER_W": pw.objective_value})
        E.append(FI.Fossil(pg.probe, score(pg.probe, t)))
    return rows


def sign_p(wins, n):
    return sum(comb(n, j) for j in range(wins, n + 1)) / 2 ** n if n else None


def main():
    worlds = []; t_start = time.time()
    for L in LENGTHS:
        for n0 in N0S:
            for seed in range(SEEDS[L]):
                rng = random.Random(f"S4:{L}:{n0}:{seed}"); t = "".join(rng.choice("01") for _ in range(L)); E0 = initial_evidence(L, n0, rng, t)
                arms = ["U", "G", "W"] + (["M"] if L <= 16 else [])
                w = {"L": L, "n0": n0, "seed": seed, "initial_log2": math.log2(AQ.feasible(E0).feasible_targets), "arms": {}}
                for arm in arms:
                    w["arms"][arm] = run_arm(arm, L, t, E0, BUDGET[L], seed)
                w["counterfactual_along_G"] = counterfactual_gains(L, t, E0, BUDGET[L], seed)
                worlds.append(w); print("world", L, n0, seed, {a: (round(w["arms"][a]["nAUC"], 3) if w["arms"][a]["nAUC"] is not None else "INTRACTABLE") for a in arms}, "t=%ds" % (time.time() - t_start), flush=True)
    # producer x regime table
    table = {}
    for L in LENGTHS:
        for n0 in N0S:
            ws = [w for w in worlds if w["L"] == L and w["n0"] == n0]; arms = list(ws[0]["arms"].keys())
            cell = {"n": len(ws), "arms": {}}
            for a in arms:
                intr = [w for w in ws if w["arms"][a].get("intractable")]
                if intr:
                    cell["arms"][a] = {"COMPUTATIONALLY_INTRACTABLE": True, "worlds_hit": len(intr), "max_compute_s": max(w["arms"][a]["max_compute_s"] for w in intr)}
                    continue
                vals = [w["arms"][a]["nAUC"] for w in ws]
                cell["arms"][a] = {"mean_nAUC": sum(vals) / len(vals), "mean_identified_at": sum(w["arms"][a]["identified_at"] for w in ws) / len(ws), "identified_within_budget": sum(1 for w in ws if w["arms"][a]["identified_at"] <= BUDGET[L]),
                                   "mean_final_log2": sum(w["arms"][a]["final_log2"] for w in ws) / len(ws), "mean_final_fixed": sum(w["arms"][a]["final_fixed"] for w in ws) / len(ws), "mean_score": sum(w["arms"][a]["mean_score"] for w in ws) / len(ws),
                                   "mean_compute_s": sum(w["arms"][a]["total_compute_s"] for w in ws) / len(ws), "max_compute_s": max(w["arms"][a]["max_compute_s"] for w in ws), "redundant_probes": sum(w["arms"][a]["redundant_probes"] for w in ws), "intractable_steps": sum(w["arms"][a]["intractable_steps"] for w in ws),
                                   "best_or_tied_count": sum(1 for w in ws if w["arms"][a]["nAUC"] <= min(w["arms"][b]["nAUC"] for b in arms if w["arms"][b]["nAUC"] is not None) + 1e-12),
                                   "traj_log2": [sum(w["arms"][a]["trajectory"][k]["log2_after"] for w in ws) / len(ws) for k in range(BUDGET[L])],
                                   "traj_gain": [sum(w["arms"][a]["trajectory"][k]["gain_bits"] for w in ws) / len(ws) for k in range(BUDGET[L])],
                                   "traj_dist": [sum(w["arms"][a]["trajectory"][k]["dist_nearest"] for w in ws) / len(ws) for k in range(BUDGET[L])]}
            pair = {}
            arms = [a for a in arms if not cell["arms"][a].get("COMPUTATIONALLY_INTRACTABLE")]
            for i, a in enumerate(arms):
                for b in arms[i + 1:]:
                    d = [w["arms"][b]["nAUC"] - w["arms"][a]["nAUC"] for w in ws]      # > 0 means a better (lower nAUC)
                    wins_a = sum(1 for x in d if x > 0); wins_b = sum(1 for x in d if x < 0); n_eff = wins_a + wins_b
                    pair["%s_vs_%s" % (a, b)] = {"paired_mean_b_minus_a": sum(d) / len(d), "a_wins": wins_a, "b_wins": wins_b, "ties": len(d) - n_eff,
                                                 "p_a_better": sign_p(wins_a, n_eff), "p_b_better": sign_p(wins_b, n_eff),
                                                 "a_better_at_bar": (sum(d) / len(d) >= 0.02 and n_eff and sign_p(wins_a, n_eff) < 0.05), "b_better_at_bar": (-sum(d) / len(d) >= 0.02 and n_eff and sign_p(wins_b, n_eff) < 0.05)}
            cell["pairs"] = pair
            # convergence and complementarity along G's trajectory
            cf = [r for w in ws for r in w["counterfactual_along_G"] if not r.get("intractable")] or [{"same_probe_G_W": False, "log2_before": 0, "gains": {"G": 0, "W": 0, "U": 0}}]
            same = [r["same_probe_G_W"] for r in cf]; cell["G_W_same_probe_frac"] = sum(same) / len(same)
            by_bucket = {}
            for r in cf:
                bkt = "log2<=4" if r["log2_before"] <= 4 else ("log2<=10" if r["log2_before"] <= 10 else "log2>10")
                by_bucket.setdefault(bkt, []).append(r["same_probe_G_W"])
            cell["G_W_same_probe_by_uncertainty"] = {k: sum(v) / len(v) for k, v in by_bucket.items()}
            gG = sorted(r["gains"]["G"] for r in cf); q1 = gG[len(gG) // 4] if gG else 0
            poor = [r for r in cf if r["gains"]["G"] <= q1]
            cell["when_G_poor"] = {"n_states": len(poor), "G_q1_gain": q1, "mean_gain_G": (sum(r["gains"]["G"] for r in poor) / len(poor)) if poor else None,
                                  "mean_gain_W": (sum(r["gains"]["W"] for r in poor) / len(poor)) if poor else None, "mean_gain_U": (sum(r["gains"]["U"] for r in poor) / len(poor)) if poor else None,
                                  "W_beats_G_frac": (sum(1 for r in poor if r["gains"]["W"] > r["gains"]["G"]) / len(poor)) if poor else None, "U_beats_G_frac": (sum(1 for r in poor if r["gains"]["U"] > r["gains"]["G"]) / len(poor)) if poor else None}
            cell["all_equivalent_frac"] = sum(1 for r in cf if max(r["gains"].values()) - min(r["gains"].values()) < 1e-9) / len(cf)
            table["L%d_n0%d" % (L, n0)] = cell
    # verdict
    winners = {}
    for k, cell in table.items():
        for pk, pv in cell["pairs"].items():
            a, b = pk.split("_vs_")
            if pv["a_better_at_bar"]:
                winners.setdefault(k, set()).add(a)
            if pv["b_better_at_bar"]:
                winners.setdefault(k, set()).add(b)
    # a cell's winner = a producer better-at-bar than every other producer it was compared with in that cell
    cell_best = {}
    for k, cell in table.items():
        arms = [a for a in cell["arms"] if not cell["arms"][a].get("COMPUTATIONALLY_INTRACTABLE")]
        for a in arms:
            beats = 0
            for pk, pv in cell["pairs"].items():
                x, y = pk.split("_vs_")
                if a == x and pv["a_better_at_bar"]: beats += 1
                if a == y and pv["b_better_at_bar"]: beats += 1
            if beats == len(arms) - 1:
                cell_best[k] = a
    distinct = set(cell_best.values())
    if len(distinct) >= 2:
        verdict = "PRODUCER_PLURALITY_SUPPORTED"
    elif len(distinct) == 1 and all(v == next(iter(distinct)) for v in cell_best.values()) and cell_best:
        verdict = "SINGLE_POLICY_DOMINATES"
    else:
        verdict = "NO_SEPARATION"
    res = {"schema": "archaeon.fossil_metabolism_s4.results.v0", "preregistration": "S4_PREREG_2026-09-12.json", "producer_version": P.PRODUCER_VERSION, "quick": QUICK, "table": table, "cell_best_at_bar": cell_best, "verdict": verdict, "worlds": worlds}
    out = Path(__file__).parent / ("S4_RESULTS%s_2026-09-12.json" % (TAG or ("_QUICK" if QUICK else "")))
    out.write_text(json.dumps(res, indent=1), encoding="utf-8")
    for k, cell in table.items():
        print(k, {a: round(v["mean_nAUC"], 3) for a, v in cell["arms"].items()}, "best-at-bar:", cell_best.get(k), "| G=W frac", round(cell["G_W_same_probe_frac"], 2), "| when G poor: W>G", cell["when_G_poor"]["W_beats_G_frac"], "U>G", cell["when_G_poor"]["U_beats_G_frac"])
    print("VERDICT", verdict)


if __name__ == "__main__":
    main()
