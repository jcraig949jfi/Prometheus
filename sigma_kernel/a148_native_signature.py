#!/usr/bin/env python3
"""
A148 native signature probe.

Charon's prior Ask 3 response showed:
  - Strict A149 signature has 0 matches in A148 (vs 5/500 in A149).
  - 0 of 38 evaluated A148 sequences hit the F1+F6+F9+F11 unanimous battery.
  - 4 A148 sequences hit F14_phase_shift, 1 hits F13_growth_rate_filter.

Recommendation 2 in that response: extract those 5 hits, look for the
simplest structural signature distinguishing them from the 33 evaluated-
but-unkilled A148 sequences. If a clean signature emerges, that's a
candidate sister-obstruction anchored on the A148 corpus with its own
detection battery.

This script does NOT use the kernel — it's pre-promotion exploration.
If a signature lands, the next step is a kernel-driven A148 obstruction
script analogous to a149_obstruction.py.

Run:  python a148_native_signature.py
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations

from a149_obstruction import (
    ASYMPTOTIC, parse_step_set, features_of, load_jsonl, load_kill_verdicts,
)


# Native A148 detection battery — empirically observed, not pre-declared.
# Per Charon's structural probe, these are the only kill_tests that fire on
# any evaluated A148 sequence.
A148_NATIVE_KILLS = {"F14_phase_shift", "F13_growth_rate_filter"}


def load_a148_family():
    rows = load_jsonl(ASYMPTOTIC)
    out = []
    for r in rows:
        sid = r.get("seq_id", "")
        if not sid.startswith("A148"):
            continue
        steps = parse_step_set(r.get("name", ""))
        if not steps:
            continue
        r["_features"] = features_of(steps)
        r["_steps"] = steps
        out.append(r)
    return out


def feature_keys():
    return ["n_steps", "neg_x", "neg_y", "neg_z",
            "pos_x", "pos_y", "pos_z", "has_diag_neg", "n_axis_aligned"]


def find_distinguishing_signature(killed, unkilled, max_terms=4):
    """
    Search for the smallest set of feature constraints that hits all of
    `killed` and as few of `unkilled` as possible.

    Returns a list of (signature_dict, n_killed_match, n_unkilled_match,
    lift) tuples sorted by (precision desc, recall desc, complexity asc).
    """
    keys = feature_keys()

    # Candidate atomic constraints: equality on observed killed-group values
    constraints = []
    for k in keys:
        for r in killed:
            v = r["_features"][k]
            constraints.append((k, "==", v))
            if isinstance(v, int) and v > 0:
                constraints.append((k, ">=", v))
            if isinstance(v, int):
                constraints.append((k, "<=", v))
    constraints = list(set(constraints))

    def match(features, sig):
        for (k, op, v) in sig:
            fv = features[k]
            if op == "==" and fv != v: return False
            if op == ">=" and not fv >= v: return False
            if op == "<=" and not fv <= v: return False
        return True

    results = []
    for size in range(1, max_terms + 1):
        for combo in combinations(constraints, size):
            keys_used = [c[0] for c in combo]
            if len(set(keys_used)) != len(keys_used):
                continue
            n_k = sum(1 for r in killed if match(r["_features"], combo))
            if n_k != len(killed):
                continue
            n_u = sum(1 for r in unkilled if match(r["_features"], combo))
            recall = n_k / len(killed)
            precision = n_k / (n_k + n_u) if (n_k + n_u) else 0.0
            base_rate = len(killed) / (len(killed) + len(unkilled))
            lift = precision / base_rate if base_rate > 0 else 0.0
            results.append((combo, n_k, n_u, recall, precision, lift, size))

    results.sort(key=lambda x: (-x[4], -x[3], x[6]))
    return results


def fmt_sig(sig):
    return " AND ".join(f"{k}{op}{v}" for (k, op, v) in sig)


def main():
    print("=" * 72)
    print("A148 NATIVE SIGNATURE PROBE")
    print("=" * 72)

    family = load_a148_family()
    kills = load_kill_verdicts()
    print(f"\n[1] A148* family: {len(family)} sequences")

    # Partition the evaluated A148 sequences (those with battery verdicts)
    evaluated = [r for r in family if r["seq_id"] in kills]
    print(f"    Evaluated by battery_sweep: {len(evaluated)}")

    killed = [r for r in evaluated
              if A148_NATIVE_KILLS & kills[r["seq_id"]]]
    unkilled = [r for r in evaluated
                if not (A148_NATIVE_KILLS & kills[r["seq_id"]])]
    print(f"    Killed (F14 or F13 fired): {len(killed)}")
    print(f"    Unkilled (no kill_tests):  {len(unkilled)}")

    # ------------------------------------------------------------------
    # 2. The killed cohort: who and what shape?
    # ------------------------------------------------------------------
    print(f"\n[2] Killed cohort (A148 native obstruction candidates):")
    hdr = (f"    {'seq_id':<10} {'delta_pct':>10} {'kill_tests':<28} "
           f"{'n_steps':>4} {'nx,ny,nz':<10} {'px,py,pz':<10} "
           f"{'diag-':>6} {'n_ax':>5}")
    print(hdr)
    for r in sorted(killed, key=lambda x: -x.get("delta_pct", 0)):
        f = r["_features"]
        kt = ",".join(sorted(A148_NATIVE_KILLS & kills[r["seq_id"]]))
        nxyz = f"{f['neg_x']},{f['neg_y']},{f['neg_z']}"
        pxyz = f"{f['pos_x']},{f['pos_y']},{f['pos_z']}"
        print(f"    {r['seq_id']:<10} {r.get('delta_pct',0):>10.3f} "
              f"{kt:<28} {f['n_steps']:>4} {nxyz:<10} {pxyz:<10} "
              f"{str(f['has_diag_neg']):>6} {f['n_axis_aligned']:>5}")

    # ------------------------------------------------------------------
    # 3. Univariate marginals
    # ------------------------------------------------------------------
    print(f"\n[3] Univariate distribution of structural features:")
    print(f"    {'feature':<15} {'killed_dist':<25} {'unkilled_dist':<25}")
    for k in feature_keys():
        kc = Counter(r["_features"][k] for r in killed)
        uc = Counter(r["_features"][k] for r in unkilled)
        kstr = ", ".join(f"{v}:{c}" for v, c in sorted(kc.items()))
        ustr = ", ".join(f"{v}:{c}" for v, c in sorted(uc.items()))
        print(f"    {k:<15} {kstr:<25} {ustr:<25}")

    # ------------------------------------------------------------------
    # 4. Signature search
    # ------------------------------------------------------------------
    print(f"\n[4] Distinguishing-signature search "
          f"(max 4 conjunctive terms, must cover all {len(killed)} killed)")
    base_rate = len(killed) / len(evaluated)
    print(f"    Base rate (kill rate among evaluated A148): {base_rate:.3f}")

    results = find_distinguishing_signature(killed, unkilled, max_terms=4)
    if not results:
        print("    No conjunctive signature with full recall found.")
        return

    print(f"    Top 10 signatures by precision then recall then simplicity:")
    print(f"    {'recall':>6} {'prec':>6} {'lift':>6} {'kill/unk':>10} signature")
    for sig, nk, nu, rec, prec, lift, size in results[:10]:
        print(f"    {rec:>6.2f} {prec:>6.2f} {lift:>6.2f}x "
              f"{nk}/{nu:<8} {fmt_sig(sig)}")

    # ------------------------------------------------------------------
    # 5. Apply best signature to the WHOLE A148 family (extrapolation)
    # ------------------------------------------------------------------
    best_sig = results[0][0]
    print(f"\n[5] Best signature ({fmt_sig(best_sig)}) applied to ALL A148:")

    def match(features, sig):
        for (k, op, v) in sig:
            fv = features[k]
            if op == "==" and fv != v: return False
            if op == ">=" and not fv >= v: return False
            if op == "<=" and not fv <= v: return False
        return True

    full_matches = [r for r in family if match(r["_features"], best_sig)]
    full_evaluated = [r for r in full_matches if r["seq_id"] in kills]
    full_killed = [r for r in full_evaluated
                   if A148_NATIVE_KILLS & kills[r["seq_id"]]]
    print(f"    matches in full A148*:        {len(full_matches)}")
    print(f"    matches with battery verdict: {len(full_evaluated)}")
    print(f"    matches actually killed:      {len(full_killed)}")
    if full_evaluated:
        print(f"    in-match kill rate:           "
              f"{len(full_killed)}/{len(full_evaluated)} = "
              f"{len(full_killed)/len(full_evaluated):.3f}")

    # ------------------------------------------------------------------
    # 6. Verdict
    # ------------------------------------------------------------------
    print()
    print("=" * 72)
    print("READING")
    print("=" * 72)
    top_prec = results[0][4]
    top_lift = results[0][5]
    if top_prec >= 0.95 and top_lift >= 5.0:
        print(f"""
    Strong candidate signature: precision {top_prec:.3f}, lift {top_lift:.2f}x.
    Worth filing as a sister candidate `A148_OCTANT_WALK_OBSTRUCTION` with
    the F14/F13 kill battery as its detection regime.

    Next step: write a149_obstruction-style kernel script anchored on
    this signature; promote through CLAIM/FALSIFY/GATE/PROMOTE.
""")
    elif top_prec >= 0.7:
        print(f"""
    Partial signature: precision {top_prec:.3f}, lift {top_lift:.2f}x. Above
    base rate but not saturating. Likely either:
      (a) The killed cohort spans two structurally-distinct sub-clusters
          that no single conjunction can capture cleanly.
      (b) Killed-group is small (n={len(killed)}) so any signature is
          fragile until more anchors accumulate.

    Recommended: inspect Section [2] for sub-cluster structure; try
    splitting by kill_test (F14 vs F13) and probing each separately.
""")
    else:
        print(f"""
    No clean signature found. Top precision {top_prec:.3f}, lift {top_lift:.2f}x.
    The 5 A148 native kills do not share a simple conjunctive structural
    signature distinguishing them from the unkilled cohort.

    Reading: the F14/F13 hits in A148 are not a coherent obstruction
    family at this descriptor level. Either (a) the descriptors are too
    coarse (need richer features beyond n_steps / neg_x / pos_x /
    has_diag_neg / n_axis_aligned), or (b) the kills are not structurally
    related — they happen to be killed by F14/F13 for different reasons.

    OBSTRUCTION_SHAPE@v1 still does not gain a cross-family anchor from
    A148. Recommend pursuing Charon's Recommendation 3 (a third family,
    A147 or A150) before rewriting the agora drafts.
""")


if __name__ == "__main__":
    main()
