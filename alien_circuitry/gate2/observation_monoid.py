"""FROZEN PAIRWISE-FREE OBSERVATION LANGUAGE for transformation-monoid universes (see SURVIVOR_GATE_PREREG.md).

Permitted, for a state f and target t: rank(f); block-size multiset of f; per-value counts c_v(f); presence of values
in the image; action id and no-op flag; immediate target equality; the same statistics of t; bounded-lookahead
summaries.  EXCLUDED: position-specific values, pairwise equalities, kernel blocks/ids/canonical forms/hashes.

Exact bounded lookahead (graph BFS ball of depth h from a candidate successor) is implemented literally in
`real_lookahead` and used for tests and per-call cost sampling.  Because the balls on this graph are large, the
verdict inside navigation is EMULATED by `verdict`, which returns exactly what the literal procedure would return
(SAFE iff D <= h, TRAP iff the forward region is exhausted, i.e. eccentricity <= h, else UNKNOWN); equivalence is
asserted by tests on random samples.  Cost is charged per call from the sampled mean ball size at that depth.
"""
from __future__ import annotations
import numpy as np

FEATURES = ["rank", "block_sizes", "value_counts", "has_value0", "has_value1", "action", "noop", "eq_target", "rank_t", "block_sizes_t", "value_counts_t", "lookahead_summary"]


class MonoidObserver:
    def __init__(self, U: dict, ecc: np.ndarray, region: np.ndarray):
        self.n = U["n"]; self.NS = U["NS"]
        self.rank = U["rank"].astype(np.int64); self.C = U["C"].astype(np.int64); self.bs_id = U["bs_id"]
        self.outdeg = U["outdeg"].astype(np.int64)
        fi, fx = U["fwd"]; self.fi, self.fx = fi.tolist(), fx.tolist()
        self._D = U["D"]; self._ecc = ecc; self._region = region  # used ONLY by verdict emulation (tested against real_lookahead)
        self.targets = U["targets"]
        self.families = [r.family for r in U["rules"]]

    def features(self, s: int, t: int) -> dict:
        return {"rank": int(self.rank[s]), "block_sizes": tuple(sorted(self.C[s][self.C[s] > 0].tolist(), reverse=True)),
                "value_counts": tuple(self.C[s].tolist()), "has_value0": bool(self.C[s, 0] > 0), "has_value1": bool(self.C[s, 1] > 0),
                "eq_target": bool(s == t), "rank_t": int(self.rank[t]), "block_sizes_t": tuple(sorted(self.C[t][self.C[t] > 0].tolist(), reverse=True)),
                "value_counts_t": tuple(self.C[t].tolist())}

    def provably_dead(self, s: int, t: int) -> bool:
        """Depth-0 sound rules available in the language: rank cannot increase, so rank(s) < rank(t) is fatal."""
        return s != t and self.rank[s] < self.rank[t]

    def verdict(self, s: int, j: int, h: int) -> str:
        if s == self.targets[j]:
            return "SAFE"
        d = int(self._D[s, j])
        if 0 <= d <= h:
            return "SAFE"
        if d < 0 and self._ecc[s] <= h:
            return "TRAP"
        return "UNKNOWN"

    def real_lookahead(self, s: int, t: int, h: int):
        """Literal graph-BFS ball of depth h.  Returns (verdict, states_expanded, transitions_examined)."""
        fi, fx = self.fi, self.fx
        if s == t:
            return "SAFE", 0, 0
        visited = {s}; frontier = [s]; d = 0; exp = exm = 0
        while True:
            if d == h:
                for v in frontier:
                    exp += 1; exm += fi[v + 1] - fi[v]
                    for u in fx[fi[v]:fi[v + 1]]:
                        if u not in visited:
                            return "UNKNOWN", exp, exm
                return "TRAP", exp, exm
            nxt = []
            for v in frontier:
                exp += 1; exm += fi[v + 1] - fi[v]
                for u in fx[fi[v]:fi[v + 1]]:
                    if u not in visited:
                        visited.add(u); nxt.append(u)
            d += 1
            if not nxt:
                return "TRAP", exp, exm
            if t in visited:
                return "SAFE", exp, exm
            frontier = nxt


def sample_ball_costs(obs: MonoidObserver, U: dict, n: int, seed: int, hmax: int = 5) -> dict:
    rng = np.random.default_rng(seed)
    src, dst, D = U["src"], U["dst"], U["D"]; T = len(U["targets"])
    e = rng.integers(0, len(src), size=n * 4); j = rng.integers(0, T, size=n * 4)
    live = D[src[e], j] >= 0; e, j = e[live][:n], j[live][:n]
    out = {}
    for h in range(hmax + 1):
        exp = exm = 0; agree = 0; verdicts = {}
        for ee, jj in zip(e.tolist(), j.tolist()):
            s = int(dst[ee]); t = U["targets"][jj]
            v, a, b = obs.real_lookahead(s, t, h); exp += a; exm += b
            verdicts[v] = verdicts.get(v, 0) + 1
            agree += (v == obs.verdict(s, jj, h))
        out[str(h)] = {"calls": len(e), "mean_states_expanded": exp / len(e), "mean_transitions_examined": exm / len(e),
                       "verdicts": verdicts, "emulation_agreement": agree / len(e)}
    return out
