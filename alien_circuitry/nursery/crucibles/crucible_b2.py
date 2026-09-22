"""CRUCIBLE-B run 2 (repaired control). Executes PREREG_C_B.md section B as amended by PREREG_B_ADDENDUM.md.

The only change from run 1 is the control: the infeasible "6 random length-matched macros excluding the mined set" is
replaced by the EXACT distribution over all C(9,6) = 84 six-element sets of length-2 generator sequences (the mined set is
one of them). Mining, world, harness, search, accounting, budget and thresholds are unchanged; MacroWorld is imported
from crucible_b unchanged. Results checkpoint per (macro set, held set) so host memory kills lose little.
Usage: python -m alien_circuitry.nursery.crucibles.crucible_b2 [--sets HELD_TARGETS,HELD_BOTH] [--kinds DFS,GBFS]
"""
from __future__ import annotations
import argparse, itertools, json, os, time
import numpy as np
from ...ac01d.evaluate import Context, write_result
from ...ac01d.baselines import hc, bootstrap_hc
from . import crucible_b as B

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
CKDIR = os.path.join(ROOT, "alien_circuitry", "results", "ac01d", "nursery", "crucible_b2_checkpoints")
ALL_LEN2 = list(itertools.product(range(3), repeat=2))
SUBSETS = list(itertools.combinations(ALL_LEN2, 6))          # 84, deterministic order


def key_of(subset): return "_".join(f"{a}{b}" for a, b in subset)


def run(sets, kinds):
    t0 = time.perf_counter(); ctx = Context(per_set=300); U, M = ctx.U, ctx.M; D = U["D"]; S = ctx.S; succ = M["succ"]
    sr, trole, pr, live = M["state_role"], M["target_role"], M["pair_role"], M["live"]
    fit = live & (sr == 0)[:, None] & (trole == 0)[None, :] & (pr == 0) & (D >= 5); Sx, Jx = np.nonzero(fit)
    rng = np.random.default_rng(B.FIT_SEED); sel = rng.choice(len(Sx), B.N_FIT_PROBLEMS, replace=False)
    paths = [B.oracle_path(S, D, succ, int(Sx[i]), int(Jx[i])) for i in sel]
    mined, counts = B.mine_macros(paths); mined_key = key_of(tuple(sorted(mined)))
    assert all(len(m) == 2 for m in mined) and len(mined) == 6, "mining no longer yields six length-2 macros; addendum does not apply"
    os.makedirs(CKDIR, exist_ok=True)
    refs = {s: ctx.references(s) for s in sets}
    rows = {}
    for n_done, subset in enumerate([tuple(sorted(mined))] + [s for s in SUBSETS if key_of(tuple(sorted(s))) != mined_key]):
        k = key_of(tuple(sorted(subset))); ck = os.path.join(CKDIR, f"{k}.json")
        if os.path.exists(ck):
            rows[k] = json.load(open(ck)); continue
        W = B.MacroWorld(ctx, list(subset)); rec = {"macros": [list(m) for m in subset], "is_mined": k == mined_key, "sets": {}}
        for set_name in sets:
            pl = ctx.probs[set_name]; O = refs[set_name]["oracle"]; kd = refs[set_name]["KA-DFS"]; rec["sets"][set_name] = {}
            for kind in kinds:
                fn = W.dfs if kind == "DFS" else W.gbfs
                R = [fn(s, j, D[:, j]) for s, j, d in pl]
                solved = np.array([r["solved"] for r in R]); tr = np.array([r["exm"] for r in R], float)
                e = {"solve_rate": float(solved.mean()), "failures": int((~solved).sum()), "mean_transitions": float(tr.mean()),
                     "mean_excess": float(np.mean([r["excess"] for r in R if r["solved"]])) if solved.any() else None}
                if solved.all():
                    e["HC_D_transitions"] = hc(tr, O[:, 1], kd["trans"]); e["HC_D_transitions_CI95"] = bootstrap_hc(tr, O[:, 1], kd["trans"])
                rec["sets"][set_name][kind] = e
        json.dump(rec, open(ck, "w"), indent=1); rows[k] = rec
        print(json.dumps({"n": n_done + 1, "subset": k, "mined": rec["is_mined"], "HC_D": {s: {kd_: rec["sets"][s][kd_].get("HC_D_transitions") for kd_ in kinds} for s in sets},
                          "t": round(time.perf_counter() - t0)}), flush=True)
    # verdict per addendum
    verdict = {}
    VERDICT_SETS = [s for s in ("HELD_TARGETS", "HELD_BOTH") if s in sets]   # frozen: verdict on these only; other sets are reported
    assert VERDICT_SETS == ["HELD_TARGETS", "HELD_BOTH"], "verdict sets must both be evaluated"
    for kind in kinds:
        ok = True; detail = {}
        for s in VERDICT_SETS:
            m = rows[mined_key]["sets"][s][kind]; mh = m.get("HC_D_transitions")
            others = [r["sets"][s][kind].get("HC_D_transitions") for kk, r in rows.items() if kk != mined_key]
            if mh is None: detail[s] = "mined set has failures"; ok = False; continue
            valid = [x for x in others if x is not None]; om = float(np.mean(valid)) if valid else None
            half = (m["HC_D_transitions_CI95"][1] - m["HC_D_transitions_CI95"][0]) / 2
            rank = 1 + sum(1 for x in valid if x > mh)   # 1 = best of all equally privileged sets
            beats = om is not None and (mh - om) > half
            detail[s] = {"mined_HC_D": mh, "mined_CI95": m["HC_D_transitions_CI95"], "others_mean_HC_D": om, "others_n_valid": len(valid), "others_with_failures": len(others) - len(valid),
                         "ci_half_width": half, "beats_others_mean_by_more_than_CI": beats, "rank_of_mined_among_84": rank}
            ok = ok and beats and mh > 0
        v = "B-KILL" if not ok else ("B-PASS" if all(detail[s]["mined_HC_D"] >= 0.20 for s in sets) else "B-WEAK")
        verdict[kind] = {"verdict": v, "detail": detail}
    out = {"prereg": "PREREG_C_B.md @ d3b9533 + PREREG_B_ADDENDUM.md", "mined": [list(m) for m in mined], "mined_counts": [counts[m] for m in mined],
           "n_subsets": len(rows), "sets": sets, "kinds": kinds, "verdict": verdict, "subsets": rows,
           "references": {s: {"oracle_transitions": float(refs[s]["oracle"][:, 1].mean()), "KA-DFS_transitions": float(refs[s]["KA-DFS"]["trans"].mean()), "KA-DFS_excess": refs[s]["KA-DFS"]["excess"],
                              "KA-GBFS_transitions": float(refs[s]["KA-GBFS"]["trans"].mean()), "KA-GBFS_excess": refs[s]["KA-GBFS"]["excess"]} for s in sets},
           "seconds": round(time.perf_counter() - t0, 1)}
    p = write_result(out, "CRUCIBLE_B2_macros_exact_control"); print(p); print(json.dumps(verdict, indent=1, default=float)); return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--sets", default="HELD_TARGETS,HELD_BOTH"); ap.add_argument("--kinds", default="DFS,GBFS")
    a = ap.parse_args(); run(a.sets.split(","), a.kinds.split(","))
