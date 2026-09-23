"""B7: which observed columns of a B world are EXACTLY y = a*x_s + c (mod 2^16) of one input column?

Conditions (lane C's C7b/c/d setting): zero actions, stoch_rate 0, obs_delay 0. Then each register after one tick
is an exact affine form over the previous tick's registers:
    reg'[r] = sum_q coef[r, q] * reg[q] + const[r]   (mod 2^16)
obtained by composing lin_ops IN ORDER (a later op reads an earlier op's result). The regime flip (a -> M - a)
changes coefficients, never the op order.

Observation layout (B1 NpEncounter.observe_all, as C's trajectory() uses it, slot 0): vals[i] = reg[obs_regs[i]]
for i < D-1, vals[D-1] = charge bucket; obs column q = vals[perm[q]]. So the charge bucket sits at permuted
position q* with perm[q*] == D-1. Lane C's harness (read-only) uses targets j in range(D-1) and inputs X = obs[..., :-1],
i.e. it assumes q* == D-1.

Per world and column j, per regime, classification:
  charge                    column j is the charge bucket (not affine in registers)
  constant                  the form has no source register
  exact_in_inputs           exactly one source register, observed in some input column (the columns C passes as X)
  source_only_in_dropped    exactly one source register, observed only in the last permuted column (dropped from X)
  source_unobserved         exactly one source register, not observed at all
  multi_source              two or more source registers
Controls: the composed forms must reproduce next registers exactly on NpEncounter zero-action trajectories (every
env, every tick, real and no_regime_flip); the REVERSE-order cheat must fail that check where op order matters.

usage: python -m primordial.soup.b7.structural --out-dir primordial/ledger/rows/B
"""
from __future__ import annotations

import argparse
import json
import pathlib

import numpy as np

from primordial.soup.b1.common import M, make_world
from primordial.soup.b1.np_world import NpEncounter

ROOT = pathlib.Path(__file__).resolve().parents[2]
C7D = ROOT / "ledger" / "rows" / "C" / "C7d-chance-grounded-contrast.jsonl"
C7C = ROOT / "ledger" / "rows" / "C" / "C7c-fit-eligible-plasticity.jsonl"


def compose(m, flip: bool, reverse: bool = False):
    """-> coef int64 [R, R], const int64 [R]: reg' = coef @ reg + const (mod M)."""
    R = m.n_regs
    coef = np.eye(R, dtype=np.int64)
    const = np.zeros(R, dtype=np.int64)
    ops = list(m.lin_ops)[::-1] if reverse else list(m.lin_ops)
    for dst, a, s1, b, s2, c in ops:
        aa = (M - a) % M if flip else a
        row = (aa * coef[s1] + b * coef[s2]) % M
        k = (aa * const[s1] + b * const[s2] + c) % M
        coef[dst], const[dst] = row, k
    return coef, const


def validate(m, wid, seeds, reverse: bool = False) -> dict:
    """Fraction of (env, tick) where the composed forms predict every register exactly, real and null worlds."""
    out = {}
    for cheat in ("", "no_regime_flip"):
        w = NpEncounter(m, wid, record=None, cheat=cheat, with_obs=False)
        w.reset(seeds)
        a = np.zeros((len(seeds), m.n_slots, m.act_width), np.int32)
        forms = {f: compose(m, f, reverse) for f in (False, True)}
        ok = total = 0
        for t in range(m.horizon - 1):
            prev = w.regs.copy()
            flip = bool(m.regime_period) and (t // m.regime_period) % 2 == 1 and cheat != "no_regime_flip"
            coef, const = forms[flip]
            pred = (prev @ coef.T + const) % M
            w.step(a)
            ok += int((pred == w.regs).all(1).sum())
            total += len(seeds)
        out["real" if cheat == "" else "null"] = ok / total if total else None
    return out


def classify(m, flip: bool) -> list[dict]:
    coef, _ = compose(m, flip)
    D = len(m.obs_perm)
    perm, obs_regs = list(m.obs_perm), list(m.obs_regs)
    col_reg = [None if perm[q] == D - 1 else obs_regs[perm[q]] for q in range(D)]
    input_regs = {col_reg[q] for q in range(D - 1) if col_reg[q] is not None}
    dropped_reg = col_reg[D - 1]
    out = []
    for j in range(D):
        r = col_reg[j]
        if r is None:
            out.append({"j": j, "class": "charge"})
            continue
        src = [int(q) for q in np.nonzero(coef[r] % M)[0]]
        if not src:
            cls = "constant"
        elif len(src) >= 2:
            cls = "multi_source"
        elif src[0] in input_regs:
            cls = "exact_in_inputs"
        elif src[0] == dropped_reg:
            cls = "source_only_in_dropped"
        else:
            cls = "source_unobserved"
        out.append({"j": j, "register": int(r), "sources": src, "class": cls})
    return out


def _jsonl(p):
    return [json.loads(x) for x in open(p, encoding="utf-8")] if p.exists() else []


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--val-envs", type=int, default=64)
    a = ap.parse_args(argv)
    c7d = _jsonl(C7D)
    c7c = _jsonl(C7C)
    header = next(r for r in c7d if r["kind"] == "header")
    worlds = [int(x) for x in header["worlds"].split(",")]
    seeds = np.arange(70000, 70000 + a.val_envs, dtype=np.int64)
    rows = []
    for gs in worlds:
        m, wid = make_world(gs)
        D = len(m.obs_perm)
        q_charge = int(list(m.obs_perm).index(D - 1))
        val = validate(m, wid, seeds)
        val_rev = validate(m, wid, seeds, reverse=True)
        cls_null = classify(m, flip=False)
        cls_flip = classify(m, flip=True)
        rows.append({"kind": "world", "gen_seed": gs, "D": D, "n_regs": m.n_regs, "lin_ops": len(m.lin_ops),
                     "stoch_rate": m.stoch_rate, "obs_delay": m.obs_delay, "corrupt_rate": m.corrupt_rate,
                     "regime_period": m.regime_period, "obs_perm": list(m.obs_perm), "obs_regs": list(m.obs_regs),
                     "charge_position": q_charge, "charge_is_last": q_charge == D - 1,
                     "validation": val, "validation_reverse_cheat": val_rev,
                     "classes_null": cls_null, "classes_flip": cls_flip})
    # ---- cross-check against lane C's committed rows (read-only)
    by_world = {r["gen_seed"]: r for r in rows}
    for src_name, crows in (("C7d", c7d), ("C7c", c7c)):
        for r in crows:
            if r.get("kind") == "target":
                gs, j = r["gen_seed"], r["j"]
                wr = by_world.get(gs)
                if wr is None:
                    continue
                rate = r.get("corrupt_rate") or 0
                sup = r["null_affine"]["support"]
                exp = (1 - 1 / rate) ** 2 if rate else 1.0
                full = (sup >= 0.99) if not rate else (abs(sup - exp) <= 0.05)
                clean_fit = r["null_affine"]["surprises_after_first_fit"] <= 2 and full
                rows.append({"kind": "c_target", "source": src_name, "gen_seed": gs, "j": j, "corrupt_rate": rate,
                             "c_null_surprises": r["null_affine"]["surprises_after_first_fit"],
                             "c_null_support": sup, "expected_support": exp, "c_full_fit": clean_fit,
                             "c_detected": r["plastic_affine"]["detected"], "c_switches": r["plastic_affine"]["switches"],
                             "b7_class_null": wr["classes_null"][j]["class"],
                             "b7_class_flip": wr["classes_flip"][j]["class"],
                             "b7_sources_null": wr["classes_null"][j].get("sources")})
            elif r.get("kind") == "world" and "eligibility_null_surprises" in r:
                gs = r["gen_seed"]
                wr = by_world.get(gs)
                if wr is None:
                    continue
                for j_s, ns in r["eligibility_null_surprises"].items():
                    j = int(j_s)
                    rows.append({"kind": "c_sensitive", "source": src_name, "gen_seed": gs, "j": j,
                                 "c_elig_null_surprises": ns, "c_eligible": j in r["eligible_targets"],
                                 "b7_class_null": wr["classes_null"][j]["class"],
                                 "b7_class_flip": wr["classes_flip"][j]["class"]})
    out = pathlib.Path(a.out_dir) / "B7-structural-eligibility.jsonl"
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    worlds_r = [r for r in rows if r["kind"] == "world"]
    ct = [r for r in rows if r["kind"] == "c_target" and r["source"] == "C7d"]
    cs = [r for r in rows if r["kind"] == "c_sensitive" and r["source"] == "C7d"]
    g612 = [r for r in ct if r["gen_seed"] == 612 and r["j"] == 2]
    print(json.dumps({
        "worlds": len(worlds_r),
        "charge_not_last": sum(not w["charge_is_last"] for w in worlds_r),
        "validation_exact_worlds": sum(w["validation"]["real"] == 1.0 and w["validation"]["null"] == 1.0 for w in worlds_r),
        "reverse_cheat_fails_worlds_ge2ops": (sum((w["validation_reverse_cheat"]["real"] < 1.0 or
                                                   w["validation_reverse_cheat"]["null"] < 1.0)
                                                  for w in worlds_r if w["lin_ops"] >= 2),
                                              sum(w["lin_ops"] >= 2 for w in worlds_r)),
        "c7d_full_fit_targets": sum(r["c_full_fit"] for r in ct),
        "c7d_full_fit_exact_in_inputs": sum(r["c_full_fit"] and r["b7_class_null"] == "exact_in_inputs" for r in ct),
        "c7d_full_fit_exceptions": [(r["gen_seed"], r["j"], r["b7_class_null"]) for r in ct
                                    if r["c_full_fit"] and r["b7_class_null"] != "exact_in_inputs"],
        "g612_j2": [(r["b7_class_null"], r["b7_sources_null"], r["c_null_support"]) for r in g612],
        "c7d_excluded_gt2": [(r["gen_seed"], r["j"], r["c_elig_null_surprises"], r["b7_class_null"]) for r in cs
                             if not r["c_eligible"]],
        "c7d_class_counts_targets": {k: sum(r["b7_class_null"] == k for r in ct) for k in
                                     sorted({r["b7_class_null"] for r in ct})},
    }, indent=1))


if __name__ == "__main__":
    main()
