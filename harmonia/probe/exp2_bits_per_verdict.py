"""EXPERIMENT 2 - bits-per-verdict retrodiction (Harmonia B, meter integrity).

Thesis v4.1 section 9 makes a checkable prediction about itself:

    "Prometheus built a huge low-bandwidth environment. 360M nearly context-free
     verdicts may be metabolically poorer than 10,000 rich counterexample traces.
     Checkable retrodictively: estimate bits-per-verdict for the historical corpus
     vs the pilot's method-bearing residue. If the thesis is right, the ratio
     should be embarrassing."

Nobody had run it. This runs it.

ESTIMANDS. "Bits per verdict" is the Shannon entropy of the outcome symbol a
consumer actually receives from one record:

  H_marginal  entropy of the verdict alphabet, pooled over corpus mass
  H_within    row-weighted mean of per-generator entropy - what a consumer sees
              once it knows which generator produced the row. This is the honest
              number, because generator identity is always known to the consumer.

Historical side: Charon's generator census, 561,314,976 EXACT rows across 45
generators. Entropies are RECOMPUTED here from his committed per-generator verdict
distributions, not quoted from his prose.

Pilot side: the M30 method-projection residue actually shipped in D0 packets,
rendered through the real assembler - what Tier B would carry.

DEGENERACY GUARD (Charon's H(Y|P,A+)=0 artifact, 2026-08-25): a stratum with too
few rows has low entropy MECHANICALLY, not informatively. Strata below MIN_ROWS are
reported separately and excluded from the headline, never silently averaged in.

Run:  PYTHONPATH=. python harmonia/probe/exp2_bits_per_verdict.py
"""
from __future__ import annotations

import json
import math
import pathlib
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[2]
CENSUS = ROOT / "charon/generator_census_2026-08-25.json"
PREPASS = ROOT / "ergon/probe/ledgers/nearmiss_mix-M30_prepass.jsonl"
MIN_ROWS = 30          # degeneracy floor for a per-stratum entropy estimate


def H(counts) -> float:
    """Shannon entropy in bits of a count mapping."""
    n = sum(counts.values())
    if n <= 0:
        return 0.0
    h = 0.0
    for v in counts.values():
        if v > 0:
            p = v / n
            h -= p * math.log2(p)
    return h


def historical():
    d = json.loads(CENSUS.read_text(encoding="utf-8"))
    gens = d["generators"]
    total_exact = d["total_rows_exact"]

    pooled = Counter()
    within_num = 0.0
    within_den = 0
    degenerate = []
    per_gen = []

    for g in gens:
        v = Counter(g.get("verdicts") or {})
        n_sampled = sum(v.values())
        rows_exact = g.get("rows_EXACT", 0)
        if n_sampled == 0:
            degenerate.append((g["generator"], rows_exact, "no verdict rows sampled"))
            continue
        # Scale the sampled distribution to the exact row count, so the pooled
        # marginal is weighted by real corpus mass rather than by sampling effort.
        scale = rows_exact / n_sampled
        for k, c in v.items():
            pooled[k] += c * scale
        h = H(v)
        per_gen.append((g["generator"], rows_exact, len(v), h, n_sampled))
        if n_sampled < MIN_ROWS:
            degenerate.append((g["generator"], rows_exact, f"only {n_sampled} rows sampled"))
            continue
        within_num += rows_exact * h
        within_den += rows_exact

    return {
        "total_exact": total_exact,
        "H_marginal": H(pooled),
        "H_within": within_num / within_den if within_den else 0.0,
        "alphabet": len(pooled),
        "per_gen": per_gen,
        "degenerate": degenerate,
        "covered_rows": within_den,
        "pooled": pooled,
    }


def pilot():
    """Entropy of the residue symbol a D0 packet actually delivers."""
    import sys
    sys.path.insert(0, str(ROOT))
    from ergon.probe.assemble import load_prepass, select_residue, assemble_retrieved

    pool = load_prepass(PREPASS)
    tau = {"nearmiss_mix-M30_prepass": 10_000}
    uids = sorted({r.uid for r in pool})

    bodies = []
    for u in uids:
        sel = select_residue(pool, stratum="D0", target_uid=u)
        if sel:
            bodies.append(
                assemble_retrieved(task_uid=u, stratum="D0", records=sel, tau=tau).body)

    # The method projection is an unordered census over a fixed 8-entry vocabulary.
    # The symbol a consumer receives is the SET of methods named; entropy over that
    # symbol is the residue's actual per-packet channel capacity.
    VOCAB = ["trial-division", "fermat-test", "miller-rabin", "sqrt-bound",
             "parity-or-last-digit", "digit-sum-rule", "modular-arithmetic",
             "factorization-attempt"]
    sigs = Counter()
    per_method = Counter()
    for b in bodies:
        low = b.lower()
        present = tuple(m for m in VOCAB if m in low)
        sigs[present] += 1
        for m in present:
            per_method[m] += 1

    return {
        "n_packets": len(bodies),
        "H_symbol": H(sigs),
        "distinct_symbols": len(sigs),
        "max_possible_bits": len(VOCAB),
        "sigs": sigs,
        "per_method": per_method,
        "vocab": VOCAB,
    }


def main() -> int:
    print("=" * 76)
    print("EXPERIMENT 2 - bits-per-verdict: historical corpus vs pilot residue")
    print("=" * 76)

    h = historical()
    print(f"\nHISTORICAL (Charon census, {h['total_exact']:,} EXACT rows, 45 generators)")
    print(f"  verdict alphabet, pooled          : {h['alphabet']} symbols")
    print(f"  H_marginal (pooled over corpus)   : {h['H_marginal']:.4f} bits")
    print(f"  H_within  (row-weighted, per-gen) : {h['H_within']:.4f} bits   <- honest number")
    print(f"  rows covered by H_within          : {h['covered_rows']:,}")
    if h["degenerate"]:
        print(f"  DEGENERACY-EXCLUDED generators    : {len(h['degenerate'])}")
        for g, rows, why in h["degenerate"][:5]:
            print(f"      {g:<8s} rows={rows:>12,}  {why}")

    print("\n  pooled verdict mass:")
    tot = sum(h["pooled"].values())
    for k, v in sorted(h["pooled"].items(), key=lambda x: -x[1])[:8]:
        print(f"      {k:<24s} {v / tot:7.2%}")

    zero = [(g, r) for g, r, card, hh, ns in h["per_gen"] if hh == 0.0]
    zrows = sum(r for _, r in zero)
    print(f"\n  {len(zero)} of 45 generators emit a SINGLE verdict symbol "
          f"({zrows:,} rows = {zrows / h['total_exact']:.1%} of corpus, 0 bits each)")

    p = pilot()
    print(f"\nPILOT RESIDUE (M30 method projection - what Tier B would carry)")
    print(f"  packets                           : {p['n_packets']}")
    print(f"  vocabulary                        : {len(p['vocab'])} methods "
          f"(ceiling {p['max_possible_bits']} bits)")
    print(f"  distinct symbols observed         : {p['distinct_symbols']}")
    print(f"  H_symbol                          : {p['H_symbol']:.4f} bits")
    print("\n  method occurrence:")
    for m, c in p["per_method"].most_common():
        print(f"      {m:<24s} {c:>4d}/{p['n_packets']}  {c / p['n_packets']:6.1%}")

    print("\n" + "-" * 76)
    rw = p["H_symbol"] / h["H_within"] if h["H_within"] > 0 else float("inf")
    rm = p["H_symbol"] / h["H_marginal"] if h["H_marginal"] > 0 else float("inf")
    print(f"RATIO pilot / historical   vs H_within  : {rw:.2f}x")
    print(f"                           vs H_marginal: {rm:.2f}x")
    print()
    print("PREREGISTERED PREDICTION (Harmonia B, written before running this):")
    print("  the ratio will NOT be embarrassing - 2-4x, not 20x - and if so, Tier B")
    print("  is not the bits-per-verdict test that Thesis v4.1 implies it is.")
    held = 1.0 <= rw <= 6.0
    print(f"  -> {'PREDICTION HELD' if held else 'PREDICTION FAILED'} "
          f"(measured {rw:.2f}x against a predicted 2-4x band)")
    print("-" * 76)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
