"""B7b: exact-fit eligibility on REACHABLE states (repairs B7, which demanded single-source over ALL states).

Setting (lane C's C7): zero actions, stoch_rate 0, obs_delay 0. One tick in regime g is affine:
    s_next = A_g s + b_g   (mod 2^16), lin_ops composed in order (primordial.soup.b7.structural.compose).
Every transition after the first starts from s_t = A_g s_{t-1} + b_g (a reachable state). For an in-regime pair
(s_t, s_{t+1}) the target register r and an input register q are
    y = A_g[r] (A_g s + b_g) + b_g[r],        x_q = A_g[q] s + b_g[q]
with s free. So y == a*x_q + c on every reachable state iff  A_g[r] A_g == a * A_g[q]  (mod 2^16, as row vectors),
and then c = (A_g[r] . b_g + b_g[r]) - a * b_g[q]. A zero left side means y is constant on reachable states.
`a` is solved exactly: pick the component of A_g[q] with the lowest 2-adic valuation k, solve mod 2^(16-k), and try its
2^k lifts against every component.

Layouts (lane C's C7 harness, read-only):
  old   (C7b/c/d rows up to 866b79406): target j = permuted obs column j < D-1; inputs = permuted columns 0..D-2
        (includes the charge bucket wherever it is not last; drops the last permuted column)
  fixed (d1f73fc3c): columns reordered = non-charge columns in permuted order, then charge; inputs = the D-1 registers

Checks:
  H1/H2/H3 against C7d's committed rows (old layout), with B7's full-fit definition
  positive control: every exact (a, c) reproduces the next register on 100% of in-regime transitions from tick 1 (real
                    zero-action register trajectories, uncorrupted)
  negative control: for every fixed-layout register classified NOT exact, C's own fit_affine on those transitions
                    stays below support 1.0
  cheat: B7's all-states rule scored against the same full-fit targets
Deliverable: per world, the fixed-layout exact-on-reachable target list for C's single C7 re-run.

usage: python -m primordial.soup.b7.reachable --out-dir primordial/ledger/rows/B
"""
from __future__ import annotations

import argparse
import json
import pathlib

import numpy as np

from primordial.soup.b1.common import M, make_world
from primordial.soup.b1.np_world import NpEncounter
from primordial.soup.b7.structural import compose

ROOT = pathlib.Path(__file__).resolve().parents[2]
C7D = ROOT / "ledger" / "rows" / "C" / "C7d-chance-grounded-contrast.jsonl"


def v2(x: int) -> int:
    k = 0
    while x % 2 == 0:
        x //= 2
        k += 1
    return k


def solve_scalar(v, w):
    """a with a*w == v (mod M) in every component, or None."""
    v = [int(x) % M for x in v]
    w = [int(x) % M for x in w]
    nz = [i for i in range(len(w)) if w[i]]
    if not nz:
        return 0 if not any(v) else None
    i = min(nz, key=lambda j: v2(w[j]))
    k = v2(w[i])
    if v[i] % (1 << k):
        return None
    mod = M >> k
    a0 = ((v[i] >> k) * pow((w[i] >> k) % mod, -1, mod)) % mod
    for t in range(1 << k):
        a = (a0 + t * mod) % M
        if all((a * w[j] - v[j]) % M == 0 for j in range(len(w))):
            return a
    return None


def regimes(m) -> list[bool]:
    return [False, True] if (m.regime_period and m.horizon > m.regime_period + 1) else [False]


def reachable_fit(m, r: int, inputs: list[int]) -> dict:
    """Per regime: first input register q (in the given order) making target register r exact on reachable states."""
    out = {}
    for flip in regimes(m):
        A, b = compose(m, flip)
        lhs = (A[r] @ A) % M
        k_y = (int(A[r] @ b) + int(b[r])) % M
        hit = None
        if not lhs.any():
            hit = {"kind": "constant", "q": None, "a": 0, "c": int(k_y)}
        else:
            for q in inputs:
                a = solve_scalar(lhs, A[q])
                if a is not None:
                    hit = {"kind": "single", "q": int(q), "a": int(a), "c": int((k_y - a * int(b[q])) % M)}
                    break
        out["flip" if flip else "normal"] = hit
    return out


def all_states_single_source(m, r: int, inputs: list[int]) -> bool:
    """B7's rule (the cheat): one source register over ALL states (normal regime), among the inputs."""
    A, _ = compose(m, False)
    src = [int(q) for q in np.nonzero(A[r] % M)[0]]
    return len(src) == 1 and src[0] in inputs


def layouts(m):
    D = len(m.obs_perm)
    perm, obs_regs = list(m.obs_perm), list(m.obs_regs)
    cc = perm.index(D - 1)
    col_old = [None if perm[q] == D - 1 else int(obs_regs[perm[q]]) for q in range(D)]
    order = [q for q in range(D) if q != cc] + [cc]
    col_fixed = [col_old[order[c]] for c in range(D)]
    return D, cc, col_old, order, col_fixed


def reg_trajectory(m, wid, seeds) -> np.ndarray:
    """[T, n, R]: out[k] = registers after k zero-action steps."""
    w = NpEncounter(m, wid, record=None, cheat="", with_obs=False)
    w.reset(seeds)
    a = np.zeros((len(seeds), m.n_slots, m.act_width), np.int32)
    out = [w.regs.copy()]
    for _ in range(m.horizon - 1):
        w.step(a)
        out.append(w.regs.copy())
    return np.stack(out)


def in_regime_pairs(m, T: int, flip: bool) -> list[int]:
    """t >= 1 such that the steps producing s_t and s_{t+1} are both in regime `flip`."""
    rp = m.regime_period
    f = lambda k: bool(rp) and (k // rp) % 2 == 1
    return [t for t in range(1, T - 1) if f(t - 1) == flip and f(t) == flip]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--envs", type=int, default=64)
    a = ap.parse_args(argv)
    from primordial.brain.affine_plastic import fit_affine          # lane C, read-only (negative control)
    c7d = [json.loads(l) for l in open(C7D, encoding="utf-8")]
    header = next(r for r in c7d if r["kind"] == "header")
    worlds = [int(x) for x in header["worlds"].split(",")]
    seeds = np.arange(71000, 71000 + a.envs, dtype=np.int64)
    rng = np.random.default_rng(7)
    rows = []
    by_world = {}
    for gs in worlds:
        m, wid = make_world(gs)
        D, cc, col_old, order, col_fixed = layouts(m)
        in_old = [col_old[q] for q in range(D - 1) if col_old[q] is not None]
        in_fixed = [col_fixed[c] for c in range(D - 1)]
        traj = reg_trajectory(m, wid, seeds)
        T = traj.shape[0]
        pos_min, neg_max, neg_n = 1.0, 0.0, 0
        fixed_targets = []
        for c in range(D - 1):
            r = col_fixed[c]
            fit = reachable_fit(m, r, in_fixed)
            exact = all(h is not None for h in fit.values())
            forms = {}
            for flip in regimes(m):
                A, b = compose(m, flip)
                forms[flip] = ((A[r] @ A) % M).tolist() + [int((A[r] @ b + b[r]) % M)]
            changes = len(forms) == 2 and forms[False] != forms[True]
            for flip in regimes(m):
                ts = in_regime_pairs(m, T, flip)
                if not ts:
                    continue
                X = traj[ts]                                           # [P, n, R]
                Y = traj[[t + 1 for t in ts]][:, :, r]
                h = fit["flip" if flip else "normal"]
                if exact and h is not None:
                    pred = np.full(Y.shape, h["c"]) if h["kind"] == "constant" else (h["a"] * X[:, :, h["q"]] + h["c"]) % M
                    pos_min = min(pos_min, float((pred == Y).mean()))
                elif not exact:
                    Xi = X[:, :, in_fixed].reshape(-1, len(in_fixed))
                    yi = Y.reshape(-1)
                    sel = rng.choice(len(yi), size=min(4096, len(yi)), replace=False)
                    _, _, _, sup = fit_affine(Xi[sel], yi[sel], rng, pairs=512)
                    neg_max = max(neg_max, float(sup))
                    neg_n += 1
            fixed_targets.append({"fixed_column": c, "register": r, "exact_on_reachable": exact,
                                  "fit": {k: (None if v is None else {**v, "source_fixed_column":
                                          (None if v["q"] is None else in_fixed.index(v["q"]))})
                                          for k, v in fit.items()},
                                  "regime_changes_form": bool(changes)})
        old_cols = []
        for j in range(D - 1):
            r = col_old[j]
            if r is None:
                old_cols.append({"j": j, "class": "charge"})
                continue
            fit = reachable_fit(m, r, in_old)
            old_cols.append({"j": j, "register": r,
                             "class": "exact_on_reachable" if all(h is not None for h in fit.values()) else "not_exact",
                             "all_states_rule": all_states_single_source(m, r, in_old)})
        w_row = {"kind": "world", "gen_seed": gs, "D": D, "charge_column_permuted": cc, "fixed_order": order,
                 "regimes": ["flip" if f else "normal" for f in regimes(m)], "corrupt_rate": m.corrupt_rate,
                 "positive_control_min_match": pos_min, "negative_control_max_support": neg_max,
                 "negative_control_cases": neg_n, "fixed_layout_targets": fixed_targets, "old_layout_columns": old_cols}
        rows.append(w_row)
        by_world[gs] = w_row
        print(f"gs{gs:>4} D={D} charge@{cc} exact_fixed={sum(t['exact_on_reachable'] for t in fixed_targets)}/{D - 1} "
              f"pos_min={pos_min:.4f} neg_max={neg_max:.4f} (n={neg_n})", flush=True)
    # ---- cross-check with C7d rows (old layout), B7's full-fit definition
    for r in c7d:
        if r.get("kind") == "target":
            wr = by_world[r["gen_seed"]]
            col = wr["old_layout_columns"][r["j"]]
            rate = r.get("corrupt_rate") or 0
            sup = r["null_affine"]["support"]
            exp = (1 - 1 / rate) ** 2 if rate else 1.0
            full = r["null_affine"]["surprises_after_first_fit"] <= 2 and (sup >= 0.99 if not rate else abs(sup - exp) <= 0.05)
            rows.append({"kind": "c7d_target", "gen_seed": r["gen_seed"], "j": r["j"], "c_full_fit": bool(full),
                         "c_null_surprises": r["null_affine"]["surprises_after_first_fit"], "c_null_support": sup,
                         "b7b_class": col["class"], "b7_all_states_rule": col.get("all_states_rule")})
        elif r.get("kind") == "world" and "eligibility_null_surprises" in r:
            wr = by_world[r["gen_seed"]]
            for j_s, ns in r["eligibility_null_surprises"].items():
                j = int(j_s)
                if j not in r["eligible_targets"]:
                    col = wr["old_layout_columns"][j]
                    rows.append({"kind": "c7d_excluded", "gen_seed": r["gen_seed"], "j": j, "c_null_surprises": ns,
                                 "b7b_class": col["class"]})
    out = pathlib.Path(a.out_dir) / "B7b-reachable-eligibility.jsonl"
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        for x in rows:
            fh.write(json.dumps(x, sort_keys=True) + "\n")
    W = [x for x in rows if x["kind"] == "world"]
    ft = [x for x in rows if x["kind"] == "c7d_target"]
    ex = [x for x in rows if x["kind"] == "c7d_excluded"]
    full = [x for x in ft if x["c_full_fit"]]
    print(json.dumps({
        "H1_full_fit_exact_on_reachable": f"{sum(x['b7b_class'] == 'exact_on_reachable' for x in full)}/{len(full)}",
        "H1_exceptions": [(x["gen_seed"], x["j"], x["b7b_class"]) for x in full if x["b7b_class"] != "exact_on_reachable"],
        "H2_excluded_exact_on_reachable": f"{sum(x['b7b_class'] == 'exact_on_reachable' for x in ex)}/{len(ex)}",
        "H2_counterexamples": [(x["gen_seed"], x["j"], x["c_null_surprises"]) for x in ex if x["b7b_class"] == "exact_on_reachable"],
        "H3_g612_j2": [x["b7b_class"] for x in ft if x["gen_seed"] == 612 and x["j"] == 2],
        "positive_control_min": min(w["positive_control_min_match"] for w in W),
        "negative_control_max_support": max(w["negative_control_max_support"] for w in W),
        "negative_control_cases": sum(w["negative_control_cases"] for w in W),
        "cheat_all_states_rule_on_full_fit": f"{sum(bool(x['b7_all_states_rule']) for x in full)}/{len(full)}",
        "deliverable_fixed_layout_exact_targets": sum(t["exact_on_reachable"] for w in W for t in w["fixed_layout_targets"]),
        "deliverable_fixed_layout_exact_and_regime_sensitive": sum(t["exact_on_reachable"] and t["regime_changes_form"]
                                                                  for w in W for t in w["fixed_layout_targets"]),
    }, indent=1))


if __name__ == "__main__":
    main()
