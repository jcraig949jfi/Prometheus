"""U-A3 lookahead gate runner.
Usage: python -m alien_circuitry.gate.run_gate U_A3_ONEWAY_BRAID 10 [--per-stratum 300] [--no-nav] [--target-max-len 2]
Targets are MECHANICAL: every terminal (irreducible) state of length <= target_max_len, in index order.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, os, time
import numpy as np
from ..universe.enumerate import build, graph_hash
from ..universe.directed_rewriting import index_word, offsets
from ..universe import metrics as M
from .termination import termination_evidence
from .observation import Observer, FEATURES
from . import analysis as A
from .navigation import make_policy, greedy_walk, guided_dfs

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POLICIES = ["B0", "B1", "B2", "LA1", "LA2", "LA3", "LA4", "LA5"]


def mechanical_targets(name: str, L: int, target_max_len: int) -> list[int]:
    U0 = build(name, L, targets=[0])
    n = int(offsets(L)[target_max_len + 1])
    return [i for i in range(n) if U0["outdeg"][i] == 0]


def file_sha(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def run(name: str, L: int, per_stratum: int = 300, do_nav: bool = True, target_max_len: int = 2, seed: int = 20260912) -> dict:
    t0 = time.perf_counter()
    targets = mechanical_targets(name, L, target_max_len)
    U = build(name, L, targets=targets)
    obs = Observer(U)
    tw = [index_word(t, L) for t in targets]
    res = {"universe": name, "L": L, "rules": [f"{r.name}: {r.lhs!r}->{r.rhs!r}" for r in U["rules"]], "NS": U["NS"],
           "edges_nominal": int(len(U["src"])), "edges_distinct": int(len(U["dsrc"])), "hashes": graph_hash(U),
           "observation_language_sha256": file_sha(os.path.join(HERE, "gate", "observation.py")),
           "navigation_policies_sha256": file_sha(os.path.join(HERE, "gate", "navigation.py")), "features": FEATURES,
           "target_rule": f"all terminal (irreducible) states of length <= {target_max_len}, index order", "targets": tw,
           "target_length_hist": dict(collections.Counter(len(w) for w in tw))}
    # termination
    term, height = termination_evidence(U); res["termination"] = term
    # corpus / difficulty
    res["difficulty"] = M.difficulty(U)
    res["target_stats"] = M.target_stats(U)["targets"]
    s_idx, j_idx, d = M.candidate_problems(U)
    res["problems_per_target"] = {tw[j]: int((j_idx == j).sum()) for j in range(len(tw))}
    # traps
    T = A.trap_table(U, obs, height)
    sib = A.sibling_match(U, obs, T)
    fam = T["family"]
    def fam_stats(mask):
        if not mask.any(): return {"count": 0, "H_obs_graph": A.hobs_hist(np.zeros(0, dtype=np.int64)), "H_obs_tree": A.hobs_hist(np.zeros(0, dtype=np.int64))}
        return {"count": int(mask.sum()), "visible": int(T["visible"][mask].sum()), "region_hist": {str(k): v for k, v in sorted(collections.Counter(T["region"][mask].tolist()).items())},
                "ecc_hist": {str(k): v for k, v in sorted(collections.Counter(T["ecc"][mask].tolist()).items())},
                "height_hist": {str(k): v for k, v in sorted(collections.Counter(T["height"][mask].tolist()).items())},
                "D_src_hist": {str(k): v for k, v in sorted(collections.Counter(T["D_src"][mask].tolist()).items())},
                "H_obs_graph": A.hobs_hist(T["ecc"][mask]), "H_obs_tree": A.hobs_hist(T["height"][mask])}
    all_m = np.ones(T["n"], dtype=bool); canc = fam == "cancel"; rel = ~canc; matched = T["exact_match"]
    res["traps"] = {"total": int(T["n"]), "cancel": int(canc.sum()), "relator": int(rel.sum()), "siblings": sib,
                    "per_target": {tw[j]: int((T["target_j"] == j).sum()) for j in range(len(tw))},
                    "all": fam_stats(all_m), "cancel_traps": fam_stats(canc), "relator_traps": fam_stats(rel), "matched_subset": fam_stats(matched),
                    "H_pair_matched_graph": A.hobs_hist(T["H_pair"][matched]), "H_pair_matched_tree": A.hobs_hist(T["H_pair_tree"][matched]),
                    "H_pair_all_with_good_sibling_graph": A.hobs_hist(T["H_pair"][T["has_good_sibling"]])}
    q1 = A.q1_exact(U, T); res["Q1_exact_classification"] = q1
    res["traps"]["trap_rate"] = q1["prevalence"]
    res["lookahead_cost_per_call"] = A.lookahead_cost_sample(U, obs, n=3000, seed=seed)
    res["residual"] = A.residual_set(U, T)
    os.makedirs(os.path.join(HERE, "results", "gate"), exist_ok=True)
    csv_path = os.path.join(HERE, "results", "gate", f"{name}_L{L}_traps.csv.gz")
    res["trap_table_sha256_uncompressed"] = A.write_trap_csv(U, T, csv_path)
    # navigation
    if do_nav:
        S = M.Searcher(U)
        probs = [p for p in M.sample_problems(U, per_stratum, seed) if p[0] != "TRIVIAL"]
        res["navigation"] = {"problems": len(probs), "per_stratum_n": dict(collections.Counter(p[0] for p in probs)), "policies": {}}
        base = []
        for name_, s, j, dd in probs:
            t = targets[j]
            f = S.forward_bfs(s, t); b = S.bidirectional_bfs(s, t); o = S.oracle(s, j)
            assert f["dist"] == b["dist"] == dd == o["dist"]
            base.append((name_, dd, f, b, o))
        def agg_base(key):
            F = np.array([r[2][key] for r in base], float); B = np.array([r[3][key] for r in base], float); O = np.array([r[4][key] for r in base], float)
            best = np.minimum(F, B)
            return {"forward_bfs_mean": float(F.mean()), "bidirectional_bfs_mean": float(B.mean()), "per_problem_min_mean": float(best.mean()),
                    "oracle_mean": float(O.mean()), "oracle_SA_vs_min": float(1 - O.sum() / best.sum()), "oracle_SA_vs_fwd": float(1 - O.sum() / F.sum()), "oracle_SA_vs_bi": float(1 - O.sum() / B.sum())}
        res["navigation"]["baselines"] = {"states_expanded": agg_base("states_expanded"), "transitions_examined": agg_base("transitions_examined"),
                                          "mean_D": float(np.mean([r[1] for r in base]))}
        best_min_states = np.minimum(np.array([r[2]["states_expanded"] for r in base], float), np.array([r[3]["states_expanded"] for r in base], float))
        best_min_trans = np.minimum(np.array([r[2]["transitions_examined"] for r in base], float), np.array([r[3]["transitions_examined"] for r in base], float))
        O_states = np.array([r[4]["states_expanded"] for r in base], float); O_trans = np.array([r[4]["transitions_examined"] for r in base], float)
        for pol in POLICIES:
            policy = make_policy(pol, obs, seed)
            tg = time.perf_counter(); G = []
            for name_, s, j, dd in probs:
                G.append(greedy_walk(obs, policy, s, targets[j], U["D"][:, j]))
            tg = time.perf_counter() - tg
            td = time.perf_counter(); Dd_ = []
            for name_, s, j, dd in probs:
                Dd_.append(guided_dfs(obs, policy, s, targets[j], U["D"][:, j]))
            td = time.perf_counter() - td
            def agg(rows, strata=None):
                sel = [r for r, p in zip(rows, probs) if strata is None or p[0] == strata]
                if not sel: return None
                solved = np.array([r["solved"] for r in sel]); ex = np.array([r["excess"] for r in sel if r["solved"]], float)
                out = {"n": len(sel), "solve_rate": float(solved.mean()),
                       "mean_states_expanded_cached": float(np.mean([r["exp_c"] for r in sel])), "mean_transitions_examined_cached": float(np.mean([r["exm_c"] for r in sel])),
                       "mean_states_expanded_uncached": float(np.mean([r["exp_u"] for r in sel])), "mean_transitions_examined_uncached": float(np.mean([r["exm_u"] for r in sel])),
                       "mean_path_len_solved": float(np.mean([r["path_len"] for r in sel if r["solved"]])) if solved.any() else None,
                       "mean_excess_solved": float(ex.mean()) if len(ex) else None}
                if "catastrophic" in sel[0]:
                    out["catastrophic_choice_rate"] = float(np.mean([r["catastrophic"] for r in sel]))
                else:
                    out["mean_trap_transitions_taken"] = float(np.mean([r["trap_transitions"] for r in sel]))
                return out
            entry = {"greedy": {"all": agg(G), "wall_clock_s": round(tg, 2)}, "dfs": {"all": agg(Dd_), "wall_clock_s": round(td, 2)}}
            for st in ("EASY", "MEDIUM", "HARD"):
                entry["greedy"][st] = agg(G, st); entry["dfs"][st] = agg(Dd_, st)
            # residual headroom vs this policy (DFS, solved-all only meaningful if solve rate 1)
            Cs = np.array([r["exp_c"] for r in Dd_], float); Ct = np.array([r["exm_c"] for r in Dd_], float)
            entry["dfs"]["oracle_SA_residual_states_cached"] = float(1 - O_states.sum() / Cs.sum())
            entry["dfs"]["oracle_SA_residual_transitions_cached"] = float(1 - O_trans.sum() / Ct.sum())
            entry["dfs"]["SA_vs_best_uninformed_states_cached"] = float(1 - Cs.sum() / best_min_states.sum())
            entry["dfs"]["SA_vs_best_uninformed_transitions_cached"] = float(1 - Ct.sum() / best_min_trans.sum())
            res["navigation"]["policies"][pol] = entry
    res["seconds"] = round(time.perf_counter() - t0, 1)
    out = os.path.join(HERE, "results", "gate", f"{name}_L{L}.json")
    with open(out, "w") as f:
        json.dump(res, f, indent=1, default=lambda o: int(o) if isinstance(o, (np.integer,)) else (float(o) if isinstance(o, np.floating) else str(o)))
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("name"); ap.add_argument("L", type=int)
    ap.add_argument("--per-stratum", type=int, default=300); ap.add_argument("--no-nav", action="store_true"); ap.add_argument("--target-max-len", type=int, default=2)
    a = ap.parse_args()
    r = run(a.name, a.L, a.per_stratum, not a.no_nav, a.target_max_len)
    print(json.dumps({"universe": a.name, "L": a.L, "termination": r["termination"]["verdict"], "cycles": r["termination"]["cycles_present"],
                      "max_height": r["termination"]["max_height_longest_path"], "traps": r["traps"]["total"], "cancel": r["traps"]["cancel"], "relator": r["traps"]["relator"],
                      "H_obs_all_graph": r["traps"]["all"]["H_obs_graph"], "H_obs_all_tree": r["traps"]["all"]["H_obs_tree"],
                      "matched": r["traps"]["siblings"], "H_pair_matched_graph": r["traps"]["H_pair_matched_graph"], "H_pair_matched_tree": r["traps"]["H_pair_matched_tree"],
                      "R5": {k: v.get("count") for k, v in r["residual"].items()}, "seconds": r["seconds"]}, indent=1))
