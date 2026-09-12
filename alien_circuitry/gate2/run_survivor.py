"""Survivor falsification gate runner.  Usage: python -m alien_circuitry.gate2.run_survivor PCH|UC1 [--per-stratum 40] [--budget 40000] [--no-nav]"""
from __future__ import annotations
import argparse, collections, json, os, time
import numpy as np
from ..universe.monoid import build_monoid, ecc_region_by_class, generated_monoid, hashes, map_str
from ..universe.uc1_seed import pch_generators, uc1_generators, SEED, SEED_STRING, FROZEN_MAP_SHA256
from ..universe import metrics as M
from .observation_monoid import MonoidObserver, sample_ball_costs, FEATURES
from . import analysis2 as A
from .navigation2 import make_policy, greedy_walk, guided_dfs

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STRATA = {"TRIVIAL": (1, 2), "EASY": (3, 8), "MEDIUM": (9, 14), "HARD": (15, 10**6)}
POLICIES = ["B0", "B1", "B2", "LA1", "LA2", "LA3", "LA4", "LA5", "KA"]


def sample_problems(U, per_stratum, seed):
    D = U["D"]; corpus = np.nonzero(U["rank"] >= 3)[0]
    S, J = np.nonzero(D[corpus] >= 1); S = corpus[S]; d = D[S, J]
    rng = np.random.default_rng(seed); out = []
    for name, (lo, hi) in STRATA.items():
        if name == "TRIVIAL": continue
        ii = np.nonzero((d >= lo) & (d <= hi))[0]
        if len(ii) == 0: continue
        pick = ii if len(ii) <= per_stratum else rng.choice(ii, per_stratum, replace=False)
        out += [(name, int(S[i]), int(J[i]), int(d[i])) for i in pick]
    return out


def run(which: str, per_stratum: int = 40, budget: int = 40000, do_nav: bool = True, seed: int = 20260912) -> dict:
    t0 = time.perf_counter(); n = 7
    gens = pch_generators(n) if which == "PCH" else uc1_generators(n)
    U = build_monoid(which, n, gens, target_rank=2)
    res = {"universe": which, "n": n, "generators": U["gens"], "NS": U["NS"], "edges_nominal": int(len(U["src"])), "self_loops_nominal": U["self_loops_nominal"],
           "edges_distinct": int(len(U["dsrc"])), "targets": len(U["targets"]), "hashes": hashes(U), "features": FEATURES,
           "build_seconds": round(time.perf_counter() - t0, 1)}
    if which == "UC1":
        res["frozen_seed"] = {"seed_string": SEED_STRING, "seed": SEED, "map": U["gens"]["map_r5"], "map_sha256": FROZEN_MAP_SHA256}
    res["generated_monoid_from_identity"] = generated_monoid(U)
    from ..gate.termination import scc_evidence
    res["scc"] = scc_evidence(U)
    ecc, region, ncls = ecc_region_by_class(U); res["count_vector_classes"] = ncls
    obs = MonoidObserver(U, ecc, region)
    D = U["D"]; corpus = U["rank"] >= 3
    live = (D >= 0) & corpus[:, None]
    dl = D[live]; hist = collections.Counter(dl.tolist())
    res["difficulty"] = {"corpus_states": int(corpus.sum()), "reachable_pairs": int(live.sum()), "distance_histogram": {str(k): int(v) for k, v in sorted(hist.items())},
                         "max_D": int(dl.max()), "strata": {k: int(((dl >= lo) & (dl <= hi)).sum()) for k, (lo, hi) in STRATA.items()},
                         "branching_distinct_hist": {str(k): int(v) for k, v in sorted(collections.Counter(U["outdeg"].tolist()).items())}}
    T = A.trap_edges(U)
    fam = np.array([r.family for r in U["rules"]]); rn = np.array([r.name for r in U["rules"]])
    res["traps"] = {"total": int(T["n"]), "by_generator": {str(g): int(c) for g, c in zip(*np.unique(rn[T["rule"]], return_counts=True))},
                    "post_trap_region_quartiles": [int(np.percentile(region[T["dst"]], q)) for q in (0, 25, 50, 75, 100)],
                    "post_trap_ecc_quartiles": [int(np.percentile(ecc[T["dst"]], q)) for q in (0, 25, 50, 75, 100)],
                    "rank_visible": int((U["rank"][T["dst"]] < U["rank"][np.array(U["targets"])[T["target_j"]]]).sum()),
                    "D_src_hist": {str(k): int(v) for k, v in sorted(collections.Counter(T["D_src"].tolist()).items())}}
    res["Q1"] = A.q1_exact(U, T, ecc)
    res["ball_costs"] = sample_ball_costs(obs, U, 3000, seed)
    lay = A.layers(U, T); R1_flags = lay.pop("R1_flags"); res["layers"] = lay
    if R1_flags.any():
        res["traps"]["R1_trap_ecc_quartiles"] = [int(np.percentile(ecc[T["dst"][R1_flags]], q)) for q in (0, 25, 50, 75, 100)]
        res["traps"]["R1_trap_region_quartiles"] = [int(np.percentile(region[T["dst"][R1_flags]], q)) for q in (0, 25, 50, 75, 100)]
    t1 = time.perf_counter(); res["leakage"] = A.leakage_attack(U, T); res["t_leakage"] = round(time.perf_counter() - t1, 1)
    t1 = time.perf_counter(); res["distance_attack"] = A.distance_attack(U); res["t_distance"] = round(time.perf_counter() - t1, 1)
    if do_nav:
        S = M.Searcher(U); probs = sample_problems(U, per_stratum, seed)
        nav = {"problems": len(probs), "per_stratum": dict(collections.Counter(p[0] for p in probs)), "budget": budget, "policies": {}}
        base = []
        for _, s, j, d in probs:
            t = U["targets"][j]; f = S.forward_bfs(s, t); b = S.bidirectional_bfs(s, t); o = S.oracle(s, j)
            assert f["dist"] == b["dist"] == d == o["dist"]; base.append((f, b, o, d))
        F_ = np.array([[r[0]["states_expanded"], r[0]["transitions_examined"]] for r in base], float)
        B_ = np.array([[r[1]["states_expanded"], r[1]["transitions_examined"]] for r in base], float)
        O_ = np.array([[r[2]["states_expanded"], r[2]["transitions_examined"]] for r in base], float)
        mn = np.minimum(F_, B_)
        nav["baselines"] = {"mean_D": float(np.mean([r[3] for r in base])), "forward_bfs_mean": F_.mean(axis=0).tolist(), "bidirectional_bfs_mean": B_.mean(axis=0).tolist(),
                            "per_problem_min_mean": mn.mean(axis=0).tolist(), "oracle_mean": O_.mean(axis=0).tolist(),
                            "H0_states": float(1 - O_[:, 0].sum() / mn[:, 0].sum()), "H0_transitions": float(1 - O_[:, 1].sum() / mn[:, 1].sum())}
        for pol in POLICIES:
            policy = make_policy(pol, obs, U, res["ball_costs"], seed)
            tg = time.perf_counter(); G = [greedy_walk(obs, policy, s, j, D[:, j]) for _, s, j, _ in probs]; tg = time.perf_counter() - tg
            td = time.perf_counter(); Dd = [guided_dfs(obs, policy, s, j, D[:, j], budget) for _, s, j, _ in probs]; td = time.perf_counter() - td
            def agg(rows):
                solved = np.array([r["solved"] for r in rows]); ex = [r["excess"] for r in rows if r["solved"]]
                exp = np.array([r["exp"] + r["look_exp"] for r in rows]); exm = np.array([r["exm"] + r["look_exm"] for r in rows])
                out = {"n": len(rows), "solve_rate": float(solved.mean()), "mean_states_expanded_incl_lookahead": float(exp.mean()), "mean_transitions_examined_incl_lookahead": float(exm.mean()),
                       "mean_search_states": float(np.mean([r["exp"] for r in rows])), "mean_lookahead_calls": float(np.mean([r["calls"] for r in rows])),
                       "mean_excess_solved": float(np.mean(ex)) if ex else None}
                if "catastrophic" in rows[0]: out["catastrophic_choice_rate"] = float(np.mean([r["catastrophic"] for r in rows]))
                else: out["mean_trap_transitions"] = float(np.mean([r["trap_transitions"] for r in rows]))
                return out, exp, exm
            ga, _, _ = agg(G); da, dexp, dexm = agg(Dd)
            entry = {"greedy": ga, "dfs": da, "wall_greedy_s": round(tg, 1), "wall_dfs_s": round(td, 1),
                     "dfs_SA_oracle_states": float(1 - O_[:, 0].sum() / dexp.sum()), "dfs_SA_oracle_transitions": float(1 - O_[:, 1].sum() / dexm.sum()),
                     "dfs_solved_only_SA_oracle_transitions": None}
            sol = np.array([r["solved"] for r in Dd])
            if sol.any():
                entry["dfs_solved_only_SA_oracle_transitions"] = float(1 - O_[sol, 1].sum() / dexm[sol].sum())
            for st in ("EASY", "MEDIUM", "HARD"):
                ii = [i for i, p in enumerate(probs) if p[0] == st]
                if ii:
                    entry[st] = {"dfs_solve_rate": float(np.mean([Dd[i]["solved"] for i in ii])), "dfs_mean_transitions": float(np.mean([dexm[i] for i in ii])),
                                 "greedy_solve_rate": float(np.mean([G[i]["solved"] for i in ii])), "oracle_mean_transitions": float(O_[ii, 1].mean())}
            nav["policies"][pol] = entry
        cheap = [p for p in POLICIES if p != "KA"]
        best = min(cheap, key=lambda p: (-(nav["policies"][p]["dfs"]["solve_rate"]), nav["policies"][p]["dfs"]["mean_transitions_examined_incl_lookahead"]))
        nav["H1"] = {"best_cheap_policy": best, "transitions": nav["policies"][best]["dfs_SA_oracle_transitions"], "states": nav["policies"][best]["dfs_SA_oracle_states"],
                     "best_cheap_solve_rate": nav["policies"][best]["dfs"]["solve_rate"]}
        nav["H2"] = {"kernel_aware_residual_blind": "KA", "transitions": nav["policies"]["KA"]["dfs_SA_oracle_transitions"], "states": nav["policies"]["KA"]["dfs_SA_oracle_states"],
                     "KA_solve_rate": nav["policies"]["KA"]["dfs"]["solve_rate"]}
        res["navigation"] = nav
    res["seconds"] = round(time.perf_counter() - t0, 1)
    os.makedirs(os.path.join(HERE, "results", "survivor"), exist_ok=True)
    with open(os.path.join(HERE, "results", "survivor", f"{which}_n{n}.json"), "w") as f:
        json.dump(res, f, indent=1, default=lambda o: int(o) if isinstance(o, np.integer) else (float(o) if isinstance(o, np.floating) else str(o)))
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("which"); ap.add_argument("--per-stratum", type=int, default=40); ap.add_argument("--budget", type=int, default=40000); ap.add_argument("--no-nav", action="store_true")
    a = ap.parse_args(); r = run(a.which, a.per_stratum, a.budget, not a.no_nav)
    q = r["Q1"]; print(json.dumps({"universe": a.which, "NS": r["NS"], "edges": r["edges_nominal"], "traps": r["traps"]["total"], "H_obs": q["H_obs"],
                                     "LA5_recall": q["per_depth"]["5"]["recall"], "layers": {k: r["layers"][k] for k in ("R0", "R1", "reachable", "R1_fraction_of_kernel_compatible", "R1_traps", "R1_trap_fraction_of_traps")},
                                     "leak_A_prauc": r["leakage"]["tuple_A"]["pr_auc"], "leak_B_prauc": r["leakage"]["tuple_B"]["pr_auc"], "leak_B_nmi": r["leakage"]["tuple_B"]["normalised_MI"],
                                     "dist_table": r["distance_attack"]["table_regressor"], "dist_linear": r["distance_attack"]["linear_regressor"],
                                     "H0": r.get("navigation", {}).get("baselines", {}), "H1": r.get("navigation", {}).get("H1"), "H2": r.get("navigation", {}).get("H2"), "seconds": r["seconds"]}, indent=1))
