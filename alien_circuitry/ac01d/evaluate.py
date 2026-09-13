"""AC-01D-v1 frozen evaluation harness for representation families.

A family supplies a `Representation` with:
  name, serialized_bytes (int),
  predict_D(states, targets) -> float array (may return NaN where not applicable),
  eligible_sets (subset of HELD_PAIRS / HELD_STATES / HELD_TARGETS / HELD_BOTH),
  reach_score(states, targets) -> float array or None   (AC-01R; higher = more reachable)
The harness computes, per eligible set: HC_D (transitions, states) with bootstrap CI, the (transitions, excess)
frontier and dominance class against KA-DFS / KA-GBFS, failures, distance-channel metrics, CR and landmarks.
Navigation = KA pruning + best-first by predicted D, and KA pruning + DFS ordered by predicted D.  Nothing here reads
D except to score the oracle, verify solutions and label traps; the policy sees only the representation's predictions.
"""
from __future__ import annotations
import json, os, time
import numpy as np
from .corpus import build, save
from .baselines import gbfs, hc, bootstrap_hc, sample_eval_problems
from ..universe.metrics import Searcher
from ..universe.monoid import ecc_region_by_class
from ..gate2.observation_monoid import MonoidObserver
from ..gate2.navigation2 import guided_dfs, Cost
from ..gate2 import analysis2 as A

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DENOM_LZMA = 1_060_696
LANDMARKS = [1.5, 2.0, 4.0, 8.0]
BANDS = [(0.20, "no useful compression"), (0.40, "weak but real structure"), (0.60, "meaningful structural compression"), (10.0, "strong result")]


def band(h):
    for lim, name in BANDS:
        if h < lim:
            return name
    return "strong result"


def dominance(tr, ex, ka_tr, ka_ex, gb_tr, gb_ex, hcd):
    if tr < ka_tr and ex <= ka_ex - 5: return "DOMINATES KA-DFS"
    if ex <= gb_ex + 2 and tr <= ka_tr: return "APPROACHES KA-GBFS"
    if hcd > 0: return "COST ONLY"
    if ex < ka_ex: return "PATH ONLY"
    return "NONE"


class Context:
    def __init__(self, per_set=300, seed=20260912, budget=40000):
        self.U, self.M, self.manifest = build()
        ecc, region, _ = ecc_region_by_class(self.U); self.obs = MonoidObserver(self.U, ecc, region)
        self.S = Searcher(self.U); self.probs = sample_eval_problems(self.U, self.M, per_set, seed)
        self.budget = budget; self.seed = seed
        self.kmask = self.U["kmask"]; self.rank = self.obs.rank; self.targets = self.U["targets"]
        self._ref = {}

    def _ka_key(self):
        rank, kmask, targets = self.rank, self.kmask, self.targets
        def dead(s, t): return s != t and (rank[s] < rank[t] or (kmask[s] & ~kmask[t]) != 0)
        def ka(s, j, idx, cost):
            t = targets[j]
            if s == t: return (0, 0, idx)
            if dead(s, t): return (2, 0, idx)
            return (1, int(rank[s]) - int(rank[t]), idx)
        return ka, dead

    def references(self, set_name):
        if set_name in self._ref: return self._ref[set_name]
        ka, _ = self._ka_key(); D = self.U["D"]; pl = self.probs[set_name]
        O = np.array([[self.S.oracle(s, j)["states_expanded"], self.S.oracle(s, j)["transitions_examined"]] for s, j, d in pl], float)
        Rd = [guided_dfs(self.obs, ka, s, j, D[:, j], self.budget) for s, j, d in pl]
        Rg = [gbfs(self.obs, ka, s, j, D[:, j], self.budget) for s, j, d in pl]
        def pack(R):
            return {"states": np.array([r["exp"] for r in R], float), "trans": np.array([r["exm"] for r in R], float),
                    "excess": float(np.mean([r["excess"] for r in R if r["solved"]])), "solve": float(np.mean([r["solved"] for r in R]))}
        self._ref[set_name] = {"oracle": O, "KA-DFS": pack(Rd), "KA-GBFS": pack(Rg)}
        return self._ref[set_name]

    def evaluate(self, rep) -> dict:
        t0 = time.perf_counter(); D = self.U["D"]; tg = np.array(self.targets)
        ka, dead = self._ka_key(); rank, targets = self.rank, self.targets
        out = {"name": rep.name, "serialized_bytes": int(rep.serialized_bytes), "CR": DENOM_LZMA / max(1, rep.serialized_bytes), "sets": {}}
        for set_name in rep.eligible_sets:
            pl = self.probs[set_name]; ref = self.references(set_name); O = ref["oracle"]
            cache = {}
            def key(s, j, idx, cost):
                t = targets[j]
                if s == t: return (0, 0, idx)
                if dead(s, t): return (2, 0, idx)
                k = (s, j)
                if k not in cache:
                    p = float(rep.predict_D(np.array([s]), np.array([t]))[0]); cache[k] = p if np.isfinite(p) else 1e6
                return (1, cache[k], idx)
            res_set = {}
            for kind, fn in (("GBFS", gbfs), ("DFS", guided_dfs)):
                R = [fn(self.obs, key, s, j, D[:, j], self.budget) for s, j, d in pl]
                solved = np.array([r["solved"] for r in R]); tr = np.array([r["exm"] for r in R], float); st = np.array([r["exp"] for r in R], float)
                ex = float(np.mean([r["excess"] for r in R if r["solved"]])) if solved.any() else None
                entry = {"solve_rate": float(solved.mean()), "failures": int((~solved).sum()), "mean_transitions": float(tr.mean()), "mean_states": float(st.mean()),
                         "mean_excess": ex, "traps_taken": float(np.mean([r["trap_transitions"] for r in R]))}
                if solved.all():
                    kd = ref["KA-DFS"]
                    entry["HC_D_transitions"] = hc(tr, O[:, 1], kd["trans"]); entry["HC_D_transitions_CI95"] = bootstrap_hc(tr, O[:, 1], kd["trans"])
                    entry["HC_D_states"] = hc(st, O[:, 0], kd["states"]); entry["HC_D_states_CI95"] = bootstrap_hc(st, O[:, 0], kd["states"])
                    entry["band"] = band(entry["HC_D_transitions"])
                    entry["dominance"] = dominance(tr.mean(), ex, kd["trans"].mean(), kd["excess"], ref["KA-GBFS"]["trans"].mean(), ref["KA-GBFS"]["excess"], entry["HC_D_transitions"])
                else:
                    entry["HC_D_transitions"] = None; entry["note"] = "failures present: no HC_D"
                res_set[kind] = entry
            # distance channel on up to 300k rows of the set
            live = self.M["live"]; sr, trole, pr = self.M["state_role"], self.M["target_role"], self.M["pair_role"]
            masks = {"HELD_PAIRS": live & (sr == 0)[:, None] & (trole == 0)[None, :] & (pr == 1), "HELD_STATES": live & (sr == 2)[:, None] & (trole == 0)[None, :],
                     "HELD_TARGETS": live & (sr == 0)[:, None] & (trole == 1)[None, :], "HELD_BOTH": live & (sr == 2)[:, None] & (trole == 1)[None, :]}
            Sx, Jx = np.nonzero(masks[set_name]); rng = np.random.default_rng(1)
            if len(Sx) > 300000: sel = rng.choice(len(Sx), 300000, replace=False); Sx, Jx = Sx[sel], Jx[sel]
            p = rep.predict_D(Sx, tg[Jx]); y = D[Sx, Jx].astype(float); ok = np.isfinite(p)
            if ok.any():
                pp, yy = p[ok], y[ok]
                from scipy.stats import spearmanr
                res_set["distance"] = {"rows": int(ok.sum()), "coverage": float(ok.mean()), "R2": float(1 - ((yy - pp) ** 2).sum() / max(1e-9, ((yy - yy.mean()) ** 2).sum())),
                                       "exact": float((np.round(pp) == yy).mean()), "within_1": float((np.abs(np.round(pp) - yy) <= 1).mean()), "MAE": float(np.abs(pp - yy).mean()),
                                       "spearman": float(spearmanr(pp, yy).correlation)}
            res_set["references"] = {"oracle_transitions": float(O[:, 1].mean()), "KA-DFS_transitions": float(ref["KA-DFS"]["trans"].mean()), "KA-DFS_excess": ref["KA-DFS"]["excess"],
                                     "KA-GBFS_transitions": float(ref["KA-GBFS"]["trans"].mean()), "KA-GBFS_excess": ref["KA-GBFS"]["excess"]}
            out["sets"][set_name] = res_set
        # AC-01R
        if getattr(rep, "reach_score", None) is not None:
            corpus = self.M["corpus"]; sr, trole = self.M["state_role"], self.M["target_role"]
            m = corpus[:, None] & (sr == 2)[:, None] & (trole == 1)[None, :]
            Sx, Jx = np.nonzero(m); rng = np.random.default_rng(2)
            if len(Sx) > 400000: sel = rng.choice(len(Sx), 400000, replace=False); Sx, Jx = Sx[sel], Jx[sel]
            sc = rep.reach_score(Sx, tg[Jx]); y = (D[Sx, Jx] >= 0).astype(float); ok = np.isfinite(sc)
            if ok.any():
                out["AC01R"] = {"rows": int(ok.sum()), "prevalence": float(y[ok].mean()), "pr_auc": A._pr_auc(sc[ok], y[ok])}
        out["landmarks"] = {str(c): ("eligible" if out["CR"] >= c else "not reached") for c in LANDMARKS}
        out["seconds"] = round(time.perf_counter() - t0, 1)
        return out


def write_result(res, tag):
    out = os.path.join(HERE, "results", "ac01d", "families"); os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, f"{tag}.json"), "w") as f:
        json.dump(res, f, indent=1, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o))
    return os.path.join(out, f"{tag}.json")
