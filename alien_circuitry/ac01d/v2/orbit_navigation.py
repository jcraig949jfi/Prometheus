"""AC-01D-v2 navigation with the exact ORBIT TABLE representation (equivariant by construction).

Representation = map from canonical joint arrangement of (f, t) (14 integers) to D, built from FIT rows only.
Coverage matters: an unseen orbit falls back to (a) the rank-difference mean.  Evaluated by the frozen harness on all
held sets, so HC_D, CR and the path frontier are directly comparable with C5 / CP / C6.  Also: the same table built
from ALL reachable pairs (exact, 25,130 orbits) as the upper reference for this coordinate system.
"""
from __future__ import annotations
import json, lzma, os, time
import numpy as np
from ..corpus import build
from ..evaluate import Context, DENOM_LZMA, write_result
from .canonical import canonical_pair, pair_index


class OrbitTableRep:
    def __init__(self, name, keys, values, fallback_by_rankdiff, gmean, F, nbytes):
        self.name = name; self.keys = keys; self.vals = values; self.fb = fallback_by_rankdiff; self.gmean = gmean; self.F = F
        self.serialized_bytes = nbytes; self.eligible_sets = ["VAL", "HELD_PAIRS", "HELD_STATES", "HELD_TARGETS", "HELD_BOTH"]; self.reach_score = None

    def predict_D(self, states, targets):
        fd = self.F[np.asarray(states)].astype(np.int64); td = self.F[np.asarray(targets)].astype(np.int64)
        fc, tc, _, _ = canonical_pair(fd, td); k = pair_index(fc, tc)
        pos = np.clip(np.searchsorted(self.keys, k), 0, len(self.keys) - 1); seen = self.keys[pos] == k
        rd = (fc.max(1) * 0 + (np.stack([(fc == v).sum(1) > 0 for v in range(7)], 1).sum(1) - 2))
        fb = np.array([self.fb.get(int(r), self.gmean) for r in rd])
        return np.where(seen, self.vals[pos], fb)


def build_table(F, tg, D, S, J):
    fc, tc, _, _ = canonical_pair(F[S].astype(np.int64), F[tg[J]].astype(np.int64)); k = pair_index(fc, tc); y = D[S, J].astype(np.float64)
    u, inv = np.unique(k, return_inverse=True); m = np.bincount(inv, weights=y) / np.bincount(inv)
    rank_f = (np.stack([(fc == v).sum(1) > 0 for v in range(7)], 1).sum(1)); rd = rank_f - 2
    fb = {int(r): float(y[rd == r].mean()) for r in np.unique(rd)}
    blob = u.astype(np.int64).tobytes() + np.round(m).astype(np.uint8).tobytes()
    return u, m, fb, float(y.mean()), len(lzma.compress(blob, preset=6)), int((np.round(m) != m).sum())


def run(per_set=300):
    t0 = time.perf_counter(); ctx = Context(per_set=per_set); U, M = ctx.U, ctx.M; D = U["D"]; F = U["F"]; tg = np.array(U["targets"])
    sr, trole, pr, live = M["state_role"], M["target_role"], M["pair_role"], M["live"]
    out = {"family": "AC-01D-v2 orbit table (canonical joint arrangement -> D)", "models": {}}
    # BUG FIX (run 1): the table must cover every reachable pair the searcher can query, including rank-2 successors (the last step
    # before a target), which lie outside the rank>=3 corpus used for problem STARTS.  Fit rows = reachable pairs of any rank whose
    # state is a train state and target a train target, pair role fit (for rank>=3) -- rank-2 pairs carry no pair-role mask and are
    # included for train states x train targets.
    reach = U["D"] >= 0
    fit = reach & (sr == 0)[:, None] & (trole == 0)[None, :] & ((pr == 0) | ~M["corpus"][:, None]); S, J = np.nonzero(fit)
    u, m, fb, gm, nb, nonint = build_table(F, tg, D, S, J)
    rep = OrbitTableRep("ORBIT-TABLE-fit", u, m, fb, gm, F, nb); ev = ctx.evaluate(rep); ev["fit"] = {"orbits_seen_in_FIT": int(len(u)), "fit_rows": int(len(S)), "cells_with_non_integer_mean": nonint}
    out["models"]["fit_only"] = ev
    Sa, Ja = np.nonzero(reach); u2, m2, fb2, gm2, nb2, nonint2 = build_table(F, tg, D, Sa, Ja)
    rep2 = OrbitTableRep("ORBIT-TABLE-exact-all-pairs", u2, m2, fb2, gm2, F, nb2); ev2 = ctx.evaluate(rep2); ev2["fit"] = {"orbits": int(len(u2)), "rows": int(len(Sa)), "cells_with_non_integer_mean": nonint2, "note": "upper reference; built from all reachable pairs incl. held sets"}
    out["models"]["exact_all_pairs"] = ev2
    out["seconds"] = round(time.perf_counter() - t0, 1)
    print(write_result(out, "V2_orbit_table"))
    for k, ev in out["models"].items():
        print(k, "bytes", ev["serialized_bytes"], "CR", round(ev["CR"], 1), ev["fit"])
        for s, e in ev["sets"].items():
            for kind in ("GBFS", "DFS"):
                x = e[kind]; print("   ", s, kind, "solve", x["solve_rate"], "fail", x["failures"], "trans", round(x["mean_transitions"], 1), "excess", None if x["mean_excess"] is None else round(x["mean_excess"], 2), "HC_D", None if x.get("HC_D_transitions") is None else round(x["HC_D_transitions"], 3), x.get("HC_D_transitions_CI95"), x.get("dominance"))
            d = e["distance"]; print("       distance R2", round(d["R2"], 4), "exact", round(d["exact"], 4), "within1", round(d["within_1"], 4))
    return out


if __name__ == "__main__":
    run()
