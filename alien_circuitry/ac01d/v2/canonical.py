"""AC-01D-v2 Step 1: exact symmetry and canonicalisation.

CORRECTION to the v1 dissection: value relabellings (f -> pi o f o pi^-1) preserve the metric only if pi fixes the
generator set under conjugation.  For {7-cycle, swap(0,1), collapse 0->1} the only such pi is the identity
(computed exhaustively).  The v1 "fix {0,1} setwise" symmetry test therefore tested a NON-symmetry and its finding is
withdrawn.  The exact metric symmetry of the left action is DOMAIN relabelling: (f, t) -> (f o sigma, t o sigma) for
any sigma in S_7, because left multiplication by a generator commutes with right composition.  Verified below on D.

Canonical form under domain relabelling: a pair (f, t) is determined up to sigma by the multiset of columns
(f(i), t(i)), i in [7].  Canonical representative = columns sorted lexicographically by (t(i), f(i)); this is
deterministic, target-aware only through the joint arrangement (which is the mathematically correct object: the
orbit of the PAIR, not of f alone), and preserves D exactly.  Orbit size = 5040 / |stabiliser|, stabiliser =
product of factorials of column multiplicities.
"""
from __future__ import annotations
import itertools, json, os
import numpy as np
from ..corpus import build

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FACT = np.array([1, 1, 2, 6, 24, 120, 720, 5040], dtype=np.int64)


def value_symmetries(gens: dict) -> list[tuple]:
    G = [tuple(np.asarray(v)) for v in gens.values()]
    out = []
    for pi in itertools.permutations(range(7)):
        pi = np.array(pi); pinv = np.argsort(pi)
        if {tuple(pi[np.array(g)[pinv]]) for g in G} == set(G): out.append(tuple(int(x) for x in pi))
    return out


def canonical_pair(fd: np.ndarray, td: np.ndarray):
    """fd, td: (n, 7) digit arrays. Returns canonical (fc, tc) with columns sorted by (t, f), plus stabiliser size and orbit size."""
    key = td.astype(np.int64) * 7 + fd.astype(np.int64)          # column key in [0, 14)
    order = np.argsort(key, axis=1, kind="stable")
    fc = np.take_along_axis(fd, order, axis=1); tc = np.take_along_axis(td, order, axis=1)
    ks = np.sort(key, axis=1)
    # multiplicities of equal columns -> stabiliser = prod factorial(mult)
    stab = np.ones(len(fd), dtype=np.int64)
    for v in range(14):
        m = (ks == v).sum(axis=1); stab *= FACT[m]
    return fc, tc, stab, 5040 // stab


def pair_index(fc, tc):
    """Integer id of the canonical pair (base-7 f digits then base-2 t digits)."""
    return (fc.astype(np.int64) * (7 ** np.arange(6, -1, -1))).sum(1) * 128 + (tc.astype(np.int64) * (2 ** np.arange(6, -1, -1))).sum(1)


def verify(U, M, n_check=300000, seed=0):
    """D(f o sigma, t o sigma) == D(f, t) on random reachable pairs and random sigma; canonical pairs share D."""
    D = U["D"]; F = U["F"]; tg = np.array(U["targets"]); live = M["live"]; rng = np.random.default_rng(seed)
    S, J = np.nonzero(live); sel = rng.choice(len(S), n_check, replace=False); S, J = S[sel], J[sel]
    pw = 7 ** np.arange(6, -1, -1)
    fd = F[S].astype(np.int64); td = F[tg[J]].astype(np.int64); d0 = D[S, J]
    # random domain relabelling; the relabelled TARGET must be re-identified as one of the 63 targets (it is a rank-2 map, but not
    # necessarily restricted-growth), so compare D of the relabelled pair via the relabelled target's own column in D when it is a
    # target, else via canonical form equality
    sig = np.stack([rng.permutation(7) for _ in range(n_check)])
    fs = np.take_along_axis(fd, sig, axis=1); ts = np.take_along_axis(td, sig, axis=1)
    tid = {int(t): j for j, t in enumerate(tg)}
    s_idx = (fs * pw).sum(1); t_idx = (ts * pw).sum(1)
    ok = np.array([int(t) in tid for t in t_idx]); jj = np.array([tid.get(int(t), -1) for t in t_idx])
    d1 = np.where(ok, D[s_idx, np.where(ok, jj, 0)], -99)
    invariant = int(((d1 == d0) | ~ok).sum()); tested = int(ok.sum()); violations = int(((d1 != d0) & ok).sum())
    # canonical: all pairs with the same canonical id must share D
    fc, tc, stab, orb = canonical_pair(fd, td); cid = pair_index(fc, tc)
    u, inv = np.unique(cid, return_inverse=True); dmin = np.full(len(u), 10**6); dmax = np.full(len(u), -1)
    np.minimum.at(dmin, inv, d0); np.maximum.at(dmax, inv, d0)
    return {"pairs_checked": n_check, "domain_relabel_tested_where_target_stays_a_target": tested, "violations": violations,
            "canonical_classes_in_sample": int(len(u)), "classes_with_inconsistent_D": int((dmin != dmax).sum()),
            "mean_orbit_size": float(orb.mean()), "orbit_size_hist": {str(k): int(v) for k, v in zip(*np.unique(orb, return_counts=True))},
            "stabiliser_hist": {str(k): int(v) for k, v in zip(*np.unique(stab, return_counts=True))}}


def orbit_census(U, M):
    """Exact number of canonical (f, t) orbits among ALL reachable corpus pairs, and the reduction factor."""
    D = U["D"]; F = U["F"]; tg = np.array(U["targets"]); live = M["live"]
    n_orbits = 0; total = 0; per_target = []
    for j, t in enumerate(tg):
        S = np.nonzero(live[:, j])[0]; fd = F[S].astype(np.int64); td = np.repeat(F[t][None, :].astype(np.int64), len(S), 0)
        fc, tc, stab, orb = canonical_pair(fd, td); cid = pair_index(fc, tc); u = np.unique(cid)
        n_orbits += len(u); total += len(S); per_target.append(int(len(u)))
    return {"reachable_pairs": int(total), "canonical_orbits": int(n_orbits), "reduction_factor": total / n_orbits, "orbits_per_target_min_max": [min(per_target), max(per_target)]}


if __name__ == "__main__":
    from ...universe.uc1_seed import pch_generators
    U, M, _ = build()
    out = {"value_symmetries_fixing_generator_set": value_symmetries(pch_generators(7)), "domain_relabelling": "all 5040 sigma in S_7 commute with the left action"}
    out["verification"] = verify(U, M); out["orbit_census"] = orbit_census(U, M)
    od = os.path.join(HERE, "results", "ac01d", "v2"); os.makedirs(od, exist_ok=True)
    json.dump(out, open(os.path.join(od, "canonical_symmetry.json"), "w"), indent=1); print(json.dumps(out, indent=1))
