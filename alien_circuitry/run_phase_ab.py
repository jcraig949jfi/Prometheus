"""Phase A/B runner: enumerate a presentation at cap L and write results/<NAME>_L<L>.json.
Usage: python -m alien_circuitry.run_phase_ab BRAID_B3 10 [--per-stratum 500] [--no-M]
"""
from __future__ import annotations
import argparse, json, os, sys, time, platform
import numpy as np
from .universe.enumerate import build, graph_hash, save
from .universe import metrics as M

HERE = os.path.dirname(os.path.abspath(__file__))


def run(name: str, L: int, per_stratum: int = 500, do_M: bool = True, save_data: bool = True) -> dict:
    t0 = time.perf_counter()
    U = build(name, L)
    res = {"universe": name, "L": L, "NS": U["NS"], "rules": [f"{r.name}: {r.lhs!r}->{r.rhs!r}" for r in U["rules"]],
           "edges_nominal": int(len(U["src"])), "edges_distinct": int(len(U["dsrc"])),
           "enumeration_seconds": round(U["t_enumerate"], 2), "distance_seconds": round(U["t_distances"], 2),
           "targets": [__import__("alien_circuitry.universe.directed_rewriting", fromlist=["index_word"]).index_word(t, L) for t in U["targets"]],
           "hashes": graph_hash(U), "platform": platform.platform(), "numpy": np.__version__}
    t = time.perf_counter(); res["difficulty"] = M.difficulty(U); res["t_difficulty"] = round(time.perf_counter() - t, 2)
    t = time.perf_counter(); res["traps"] = M.trap_analysis(U); res["t_traps"] = round(time.perf_counter() - t, 2)
    t = time.perf_counter(); res["target_stats"] = M.target_stats(U); res["t_targets"] = round(time.perf_counter() - t, 2)
    t = time.perf_counter(); res["baselines"] = M.baselines(U, per_stratum); res["t_baselines"] = round(time.perf_counter() - t, 2)
    t = time.perf_counter(); res["chart_D"] = M.chart_D(U); res["t_chart_D"] = round(time.perf_counter() - t, 2)
    if do_M:
        t = time.perf_counter(); res["chart_M"] = M.chart_M(U); res["t_chart_M"] = round(time.perf_counter() - t, 2)
    t = time.perf_counter(); res["mask_proposal"] = M.mask_proposal(U); res["t_masks"] = round(time.perf_counter() - t, 2)
    res["total_seconds"] = round(time.perf_counter() - t0, 2)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out = os.path.join(HERE, "results", f"{name}_L{L}.json")
    with open(out, "w") as f:
        json.dump(res, f, indent=1)
    if save_data:
        save(U, os.path.join(HERE, "data"))
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("name"); ap.add_argument("L", type=int)
    ap.add_argument("--per-stratum", type=int, default=500); ap.add_argument("--no-M", action="store_true"); ap.add_argument("--no-save", action="store_true")
    a = ap.parse_args()
    r = run(a.name, a.L, a.per_stratum, not a.no_M, not a.no_save)
    d = r["difficulty"]; tr = r["traps"]; b = r["baselines"]["all"]
    print(json.dumps({"universe": a.name, "L": a.L, "NS": r["NS"], "edges_nominal": r["edges_nominal"], "edges_distinct": r["edges_distinct"],
                      "enum_s": r["enumeration_seconds"], "dist_s": r["distance_seconds"], "total_s": r["total_seconds"],
                      "candidates": d["candidate_problems"], "hist": d["distance_histogram"],
                      "EASY": d["eligible_EASY"], "MEDIUM": d["eligible_MEDIUM"], "HARD": d["eligible_HARD"],
                      "trap_rate": tr["trap_rate_of_live_triples"], "latent_frac": tr["latent_fraction_of_traps"], "latent": tr["totals"]["latent"],
                      "latent_region": tr["latent_successor_forward_region_size"], "latent_ecc": tr["latent_successor_eccentricity"],
                      "indist": tr["latent_traps_locally_indistinguishable_from_a_nontrap_sibling"],
                      "mismatches": r["baselines"]["distance_mismatches_bfs_bibfs_D_oracle"],
                      "SA_oracle_vs_bibfs_trans": b["oracle_SA_vs_bibfs_transitions"], "SA_oracle_vs_bfs_trans": b["oracle_SA_vs_forward_bfs_transitions"],
                      "SA_oracle_vs_bibfs_states": b["oracle_SA_vs_bibfs_states"], "inflation_trans_pts": b["ordering_inflation_transitions_points"]}, indent=1))
