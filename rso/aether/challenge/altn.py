"""C-018-T040 B8: counterfactual on the instrument's own choice of non-ancestor. For an evaluable challenge unit, the
warm snapshot is recomputed exactly as adapter.native_unit does (adapter.py:129-137, Aether's code), the SECOND-ranked
non-ancestor candidate N2 (same rule, same order: natives.n_candidates) is clamped instead of N, and the class is read with
the frozen thresholds (evaluate.ancestry on the fixture path, which takes B / N / targets explicitly). The impulse world of
the re-run is checked against the stored first-divergence array (a replay of that world).

    python -B -m rso.aether.challenge.altn <scratch> <LAW> <k> [<k> ...]
"""
import json
import os
import sys
import time

import numpy as np

from rso.aether import adapter as A, evaluate as E
from rso.aether.challenge import natives as NV
import prop01_tree as TR           # noqa: E402

P, K = A.P, A.K


def warm_snapshot(law, k, n, warm):
    with A._Seeds():
        f0, _ = P.R.build_initial(P.R.SPARSE_SOUP, n, n, P.RNG_SEED_BASE + k, write_density=P.DENSITY,
                                  energy_mode=P.R.ENERGY_UNIFORM)
        phys = P.PHYS_SEED_BASE + k
        s = [np.asarray(f).copy() for f in f0]
        for t in range(warm):
            s, _ = P.law_step(np, K, law, n, phys, t + 1, s)
        O = P.pick_origin(np, K, s, k)
    return s, phys, O


def run_one(scratch, law, k):
    meta, a = A.load_unit(os.path.join(scratch, "units", "native_%s_%d" % (law, k)))
    n, warm, H, O = meta["n"], meta["warm"], meta["H"], meta["origin"]
    tr = meta["tree"]
    B, _ = TR.choose_cut({"tree": tr})
    cands = NV.n_candidates(tr, B, O, n)
    out = {"law": law, "k": k, "B": B, "N": meta["N"], "candidates": [[int(d), int(t), int(s)] for d, t, s in cands[:4]]}
    if len(cands) < 2:
        out["N2"] = None
        return out
    N2 = int(cands[1][2])
    t0 = time.time()
    s, phys, O2 = warm_snapshot(law, k, n, warm)
    out["warm_digest_equal"] = P.digest(s) == meta["aether"]["warm_digest"]
    out["snap_equal"] = bool(np.array_equal(np.stack(s), a["snap"]))
    out["origin_equal"] = O2 == O
    oy, ox = divmod(O, n)
    imp = [f.copy() for f in s]
    imp[3][oy, ox] ^= np.uint8(1)

    def step(w, t):
        return P.law_step(np, K, law, n, phys, warm + t, w)[0]
    ft, dig, _ = A.pair_run(step, s, imp, H, {"cutN": N2})
    out["impulse_replay_equal"] = bool(np.array_equal(ft["impulse"], a["ftick_impulse"]))
    tg = sorted(TR.descendants(tr, B))
    cn2 = ft["cutN"]
    m2 = {"kind": "fixture", "n": n, "origin": O, "B": B, "N": N2, "targets": tg}
    a2 = dict(a, ftick_cutN=cn2)
    r1 = E.ancestry(meta, a)
    r2 = E.ancestry(m2, a2)
    out.update(N2=N2, ftick_N=int(a["ftick_impulse"][meta["N"]]), ftick_N2=int(a["ftick_impulse"][N2]),
               cls=r1["cls"], removed_B=r1["removed_B"], removed_N=r1["removed_N"],
               cls_N2=r2["cls"], removed_N2=r2["removed_N"], n_targets=len(tg),
               n_targets_removed_N2=sum(1 for s_ in tg if cn2[s_] < 0), wall_s=round(time.time() - t0, 1))
    return out


if __name__ == "__main__":
    scratch, law = sys.argv[1], sys.argv[2]
    rows = []
    for k in sys.argv[3:]:
        r = run_one(scratch, law, int(k, 0))
        rows.append(r)
        print(json.dumps(r, default=str), file=sys.stderr, flush=True)
    with open(os.path.join(scratch, "altn_%s.jsonl" % law), "a", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True, default=str) + "\n")
