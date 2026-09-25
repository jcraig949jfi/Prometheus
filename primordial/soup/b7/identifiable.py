"""B7b post-hoc diagnosis (NOT the verdict): are B7b's 4 H2 counterexamples exact-but-unidentifiable by C's learner?

C's fit_affine (primordial/brain/affine_plastic.py, read-only) solves a = (y_i - y_k) * inv(x_i - x_k) only from pairs
whose source difference is ODD (invertible mod 2^16). On reachable states x_q = A[q] s + b[q] with s free, so every
difference is A[q] (s_i - s_k): if every coefficient of A[q] is even, every difference is even and fit_affine can never
recover a -- even though y == a*x_q + c holds exactly.

For each counterexample: B7b's old-layout (q, a, c); min 2-adic valuation of A[q]; the exact relation checked on real
no_regime_flip register trajectories (t >= 1); C's fit_affine on the same pooled data with the old-layout inputs.
Also: an identifiability flag for every fixed-layout exact target (min valuation of the source row == 0).

usage: python -m primordial.soup.b7.identifiable --out primordial/ledger/rows/B/B7b-identifiability-posthoc.jsonl
"""
from __future__ import annotations

import argparse
import json
import pathlib

import numpy as np

from primordial.soup.b1.common import M, make_world
from primordial.soup.b7.reachable import layouts, reachable_fit, regimes, v2
from primordial.soup.b7.structural import compose

ROOT = pathlib.Path(__file__).resolve().parents[2]
B7B = ROOT / "ledger" / "rows" / "B" / "B7b-reachable-eligibility.jsonl"
COUNTEREXAMPLES = [(71, 1), (233, 1), (380, 3), (46, 3)]


def row_min_valuation(row) -> int | None:
    nz = [int(x) % M for x in row if int(x) % M]
    return min(v2(x) for x in nz) if nz else None


def null_register_trajectory(m, wid, seeds):
    from primordial.soup.b1.np_world import NpEncounter
    w = NpEncounter(m, wid, record=None, cheat="no_regime_flip", with_obs=False)
    w.reset(seeds)
    a = np.zeros((len(seeds), m.n_slots, m.act_width), np.int32)
    out = [w.regs.copy()]
    for _ in range(m.horizon - 1):
        w.step(a)
        out.append(w.regs.copy())
    return np.stack(out)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    from primordial.brain.affine_plastic import fit_affine          # lane C, read-only
    rng = np.random.default_rng(11)
    seeds = np.arange(72000, 72064, dtype=np.int64)
    rows = []
    for gs, j in COUNTEREXAMPLES:
        m, wid = make_world(gs)
        D, cc, col_old, order, col_fixed = layouts(m)
        in_old = [col_old[q] for q in range(D - 1) if col_old[q] is not None]
        r = col_old[j]
        fit = reachable_fit(m, r, in_old)
        h = fit["normal"]
        A, _ = compose(m, False)
        traj = null_register_trajectory(m, wid, seeds)
        X = traj[1:-1]                                              # s_t, t >= 1
        Y = traj[2:, :, r]                                          # s_{t+1}[r]
        if h["kind"] == "constant":
            exact_rate = float((Y == h["c"]).mean())
            val = None
        else:
            exact_rate = float((((h["a"] * X[:, :, h["q"]] + h["c"]) % M) == Y).mean())
            val = row_min_valuation(A[h["q"]])
        # the differences C's learner would see, on the real data
        xs = X[:, :, h["q"]].reshape(-1) if h["q"] is not None else None
        odd_diff_share = None
        if xs is not None:
            i = rng.integers(0, len(xs), 20000)
            k = rng.integers(0, len(xs), 20000)
            odd_diff_share = float((((xs[i] - xs[k]) & 1) == 1).mean())
        Xi = X[:, :, in_old].reshape(-1, len(in_old))
        yi = Y.reshape(-1)
        sel = rng.choice(len(yi), size=min(4096, len(yi)), replace=False)
        s_best, a_best, c_best, sup = fit_affine(Xi[sel], yi[sel], rng, pairs=512)
        rows.append({"kind": "counterexample", "gen_seed": gs, "j": j, "register": r, "old_inputs": in_old,
                     "b7b_hit_normal": h, "source_row_min_2adic_valuation": val,
                     "exact_relation_rate_on_null_trajectory": exact_rate,
                     "odd_difference_share_of_source": odd_diff_share,
                     "c_fit_affine_best_support": float(sup)})
        print(json.dumps(rows[-1]), flush=True)
    # identifiability flag for the fixed-layout deliverable
    b7b = [json.loads(l) for l in open(B7B, encoding="utf-8")]
    n_exact = n_ident = 0
    for w in (x for x in b7b if x["kind"] == "world"):
        m, _ = make_world(w["gen_seed"])
        per_regime = {False: compose(m, False)[0], True: compose(m, True)[0]}
        for t in w["fixed_layout_targets"]:
            if not t["exact_on_reachable"]:
                continue
            n_exact += 1
            ident = True
            for key, hit in t["fit"].items():
                if hit["kind"] == "single":
                    A = per_regime[key == "flip"]
                    ident &= row_min_valuation(A[hit["q"]]) == 0
            n_ident += ident
            rows.append({"kind": "fixed_target_identifiability", "gen_seed": w["gen_seed"],
                         "fixed_column": t["fixed_column"], "register": t["register"],
                         "regime_changes_form": t["regime_changes_form"], "identifiable_by_odd_differences": ident})
    print(json.dumps({"fixed_layout_exact": n_exact, "fixed_layout_exact_and_identifiable": n_ident}), flush=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        for x in rows:
            fh.write(json.dumps(x, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
