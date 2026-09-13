"""S6 phase 2: the anatomy of G's information loss, on the L 8 eligible endgame (development set), exact.
For every eligible evidence state s (from S6_ENDGAME_UNIVERSE_L8) and EVERY probe q in {0,1}^8: the outcome partition,
ER, the cheap statistics, and the sealed oracle's Q*(s, q). Then, with G's actual pick g (G's own pool and seed):
  regret(s) = Q*(g) - V*;  what an exact-tie re-rank inside G's pool could recover;  what near-tie windows could;
  what the best pool member could;  the rest (outside the pool).
  For each statistic: tie-break accuracy inside exact ER tie classes; minimal counterexamples (same ER, same statistic,
  different Q*); sufficiency across all probes (same (ER, statistic) -> same Q*?).
Run from the repository root: python archaeon/docs/h0h5/S6_CHARACTERIZE_2026-09-13.py [--L 8] [--nmin 5 --nmax 18]"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from archaeon.producer import fossil_inference as FI, s4_producers as P, s5_producers as O5, s6_endgame as S6  # noqa: E402

HERE = Path(__file__).parent
L = int(sys.argv[sys.argv.index("--L") + 1]) if "--L" in sys.argv else 8
NMIN = int(sys.argv[sys.argv.index("--nmin") + 1]) if "--nmin" in sys.argv else 5
NMAX = int(sys.argv[sys.argv.index("--nmax") + 1]) if "--nmax" in sys.argv else 18
WINDOWS = (0.0, 0.02, 0.05, 0.10, 0.20)


def main():
    states = [s for s in json.loads((HERE / f"S6_ENDGAME_UNIVERSE_L{L}_2026-09-13.json").read_text(encoding="utf-8")) if NMIN <= s["N"] <= NMAX]
    oracle = S6.SealedOracle(L); rows = []; ce = {k: [] for k in S6.STATISTICS}; suff = {k: [] for k in S6.STATISTICS}
    tie_acc = {k: [0, 0] for k in S6.STATISTICS}; v2cache_shared = {}
    for s in states:
        fs = [FI.Fossil(b, sc) for b, sc in s["fossils"]]; S = S6.feasible_ints(fs); N = len(S); vstar = oracle.V(S)
        caches = {}
        probes = {}
        for q in range(1 << L):
            cells = S6.partition_cells(L, S, q)
            if len(cells) == 1:
                continue
            Q = oracle.Q(S, q)
            st = {k: S6.statistic(k, L, S, q, cells, caches) for k in S6.STATISTICS}
            probes[q] = {"cells": cells, "er": S6.er_num(cells), "Q": Q, "stat": st}
        er_min_all = min(p["er"] for p in probes.values()); q_opt = min(probes, key=lambda q: (probes[q]["Q"], probes[q]["er"], q))
        # G's actual choice with the S6 seed
        si = {"lane": "s6", "L": L, "world": s["eid"], "arm": "G", "step": 1}
        g = P.produce_G(fs, si); gi = O5._as_int(g.probe)
        st_, pool, vals = S6.g_pool_and_values(fs, si)
        pool_ints = [O5._as_int(v.probe) for v in vals]; pool_er = {O5._as_int(v.probe): v.er_numerator for v in vals}
        Qg = probes[gi]["Q"] if gi in probes else float("inf"); regret = Qg - vstar
        best_pool = min(probes[q]["Q"] for q in pool_ints if q in probes)
        er_min_pool = min(pool_er.values())
        rec = {}
        for w in WINDOWS:
            adm = [q for q in pool_ints if q in probes and pool_er[q] <= er_min_pool * (1 + w) + 1e-9]
            rec[str(w)] = {"admissible": len(adm), "best_Q": min(probes[q]["Q"] for q in adm), "recoverable": Qg - min(probes[q]["Q"] for q in adm)}
        # exact tie class in the pool: statistic tie-break accuracy and counterexamples
        tie = [q for q in pool_ints if q in probes and pool_er[q] == er_min_pool]
        if len(tie) > 1:
            qbest = min(probes[q]["Q"] for q in tie)
            tie_acc.setdefault("G_lex", [0, 0]); tie_acc["G_lex"][1] += 1; tie_acc["G_lex"][0] += int(abs(Qg - qbest) < 1e-9)
            for k in S6.STATISTICS:
                pick = max(tie, key=lambda q: (probes[q]["stat"][k], -q))       # higher statistic, then lex-smallest (G's rule)
                tie_acc[k][1] += 1; tie_acc[k][0] += int(abs(probes[pick]["Q"] - qbest) < 1e-9)
        # counterexamples against sufficiency: same ER (all probes of this state) and same statistic but different Q*
        by = defaultdict(lambda: defaultdict(set))
        for q, p in probes.items():
            for k in S6.STATISTICS:
                by[k][(p["er"], p["stat"][k])].add(round(p["Q"], 9))
        for k in S6.STATISTICS:
            for key, Qs in by[k].items():
                if len(Qs) > 1:
                    suff[k].append({"eid": s["eid"], "N": N, "er": key[0], "stat": key[1], "Qs": sorted(Qs)})
                    if key[0] == er_min_all:
                        ce[k].append({"eid": s["eid"], "N": N, "stat": key[1], "Qs": sorted(Qs)})
        # partition shapes: G's pick vs the oracle's preferred probe (among all probes) and vs the best exact-tie member
        rows.append({"eid": s["eid"], "N": N, "depth": s["depth"], "root": s["root"], "V_star": vstar, "Q_g": Qg, "regret": regret, "regret_rel": regret / Qg if Qg else 0.0,
                     "g_cells": probes[gi]["cells"] if gi in probes else None, "g_er": pool_er[gi], "er_min_pool": er_min_pool, "er_min_all": er_min_all, "pool_suboptimal_vs_all": er_min_pool > er_min_all,
                     "opt_cells": probes[q_opt]["cells"], "opt_er": probes[q_opt]["er"], "opt_er_rel_gap": (probes[q_opt]["er"] - er_min_all) / er_min_all,
                     "best_pool_Q": best_pool, "beyond_pool": best_pool - vstar, "windows": rec, "tie_size": len(tie), "g_stats": probes[gi]["stat"] if gi in probes else None, "opt_stats": probes[q_opt]["stat"]})
    out = {"L": L, "eligible": [NMIN, NMAX], "states": len(rows), "rows": rows, "tie_break_accuracy": {k: {"correct": v[0], "classes": v[1]} for k, v in tie_acc.items()},
           "counterexamples_at_er_min": {k: v for k, v in ce.items()}, "insufficiency_all_probes": {k: len(v) for k, v in suff.items()}, "insufficiency_examples": {k: v[:20] for k, v in suff.items()},
           "oracle_ledger": vars(oracle.ledger)}
    (HERE / f"S6_CHARACTERIZATION_L{L}_2026-09-13.json").write_text(json.dumps(out, indent=0, default=str), encoding="utf-8")
    # summary
    gap = [r for r in rows if r["regret"] > 1e-9]; tot = sum(r["regret"] for r in gap)
    print("eligible states", len(rows), "with G->O regret", len(gap), "mean regret %.4f (rel %.4f)" % (sum(r["regret"] for r in rows) / len(rows), sum(r["regret_rel"] for r in rows) / len(rows)))
    print("pool misses the exact one-step optimum in", sum(r["pool_suboptimal_vs_all"] for r in rows), "states; oracle-preferred probe has ER above the global minimum in", sum(1 for r in rows if r["opt_er_rel_gap"] > 1e-9), "states; mean rel ER gap of the oracle probe %.4f" % (sum(r["opt_er_rel_gap"] for r in rows) / len(rows)))
    print("regret decomposition over gap states (fraction of total regret recoverable):")
    for w in WINDOWS:
        print("  window %4.0f%%: admissible mean %.2f  recoverable %.3f  states fully recovered %d/%d" % (w * 100, sum(r["windows"][str(w)]["admissible"] for r in gap) / max(1, len(gap)), sum(r["windows"][str(w)]["recoverable"] for r in gap) / tot if tot else 0, sum(1 for r in gap if r["windows"][str(w)]["recoverable"] >= r["regret"] - 1e-9), len(gap)))
    print("  best pool member: %.3f   beyond the pool: %.3f" % (sum(r["Q_g"] - r["best_pool_Q"] for r in gap) / tot if tot else 0, sum(r["beyond_pool"] for r in gap) / tot if tot else 0))
    print("exact-tie classes in the pool (size > 1):", tie_acc["entropy"][1], "; tie-break accuracy per statistic:", {k: "%d/%d" % tuple(v) for k, v in tie_acc.items()})
    print("counterexamples against sufficiency at ER-min (same ER-min, same statistic, different Q*): states with >= 1:", {k: len({c["eid"] for c in v}) for k, v in ce.items()})
    print("insufficiency over all probes (same ER, same statistic, different Q*), groups:", {k: len(v) for k, v in suff.items()})
    sh = Counter((tuple(r["g_cells"]), tuple(r["opt_cells"])) for r in gap)
    print("most common (G shape -> oracle shape) among gap states:", sh.most_common(8))
    print("oracle ledger", vars(oracle.ledger))


if __name__ == "__main__":
    main()
