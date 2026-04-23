"""Drum-shape separator scan (Aporia lens-scan pick #1).

For each pair of F-IDs in the tensor, compute:
  - spectral_sig: tuple of invariance values on SPECTRAL_COLS
  - arithmetic_sig: tuple of invariance values on ARITHMETIC_COLS

Pairs that match spectrally but differ arithmetically (or vice versa) are
drum-shape analogues: "two findings the spectrum lens cannot tell apart but
the arithmetic lens can" (or vice versa).

Output: ranked list of pairs, with the DIFFERENTIATING projection subset
printed per pair. Each pair is a named-new-invariant candidate for gen_11.
"""
import json
from collections import Counter
from pathlib import Path

from agora.tensor import reconstruct_matrix, features, projections

# Projection classification, derived from
# harmonia/memory/coordinate_system_catalog.md (2026-04-21 as of sessionE scan).
# Spectral / distributional lens: reads a spectrum-like shape across a family.
SPECTRAL_COLS = {
    "P001",  # CouplingScorer (cosine feature similarity)
    "P002",  # DistributionalCoupling (M4/M2 kurtosis)
    "P011",  # Lhash exact-match (isospectral grouping)
    "P012",  # trace_hash (Hecke eigenvalue hash)
    "P028",  # Katz-Sarnak family symmetry type
    "P034",  # AlignmentCoupling
    "P050",  # First-gap analysis
    "P051",  # N(T) unfolding
    "P052",  # Prime decontamination
    "P053",  # Mahler measure projection
}

# Arithmetic / structural lens: reads an algebraic / geometric invariant.
ARITHMETIC_COLS = {
    "P003",  # Megethos (log|magnitude|)
    "P010",  # Galois-label object-keyed scorer
    "P020",  # Conductor conditioning
    "P021",  # Bad-prime count
    "P022",  # aut_grp (genus-2)
    "P023",  # Rank
    "P024",  # Torsion
    "P025",  # CM vs non-CM
    "P026",  # Semistable vs additive
    "P027",  # ADE type
    "P029",  # MF weight
    "P030",  # MF level
    "P031",  # Frobenius-Schur Indicator
    "P032",  # MF parity
    "P033",  # Artin Is_Even parity
    "P035",  # Kodaira reduction
    "P036",  # Root number
    "P037",  # Sato-Tate group
    "P038",  # Sha
    "P039",  # Galois l-adic image
    "P100",  # Isogeny class size
    "P101",  # EC regulator
    "P102",  # Artin rep dimension
    "P103",  # EC modular degree
}


def build_row(row, projs, col_set):
    """Extract (p_id, invariance_value) tuples for non-zero cells in col_set."""
    return tuple(
        (p, int(v)) for p, v in zip(projs, row) if p in col_set and int(v) != 0
    )


def hamming_informative(sig_a, sig_b):
    """Agreement count, disagreement count, and the specific disagreeing projections.

    A cell in sig_a or sig_b is informative only if at least one side has a
    non-zero value. Both-zero positions carry no information (nobody tested).
    """
    d_a = dict(sig_a)
    d_b = dict(sig_b)
    informative_p = set(d_a) | set(d_b)
    agree = []
    disagree = []
    for p in sorted(informative_p):
        va = d_a.get(p, 0)
        vb = d_b.get(p, 0)
        if va == vb and va != 0:
            agree.append((p, va))
        elif va != vb:
            disagree.append((p, va, vb))
    return agree, disagree


def main():
    feats, projs, mat = reconstruct_matrix()  # features list, projections list, 2D matrix
    feats = list(feats)
    projs = list(projs)
    rows = {f: [int(mat[i, j]) for j in range(len(projs))] for i, f in enumerate(feats)}

    spectral_sigs = {f: build_row(rows[f], projs, SPECTRAL_COLS) for f in feats}
    arith_sigs = {f: build_row(rows[f], projs, ARITHMETIC_COLS) for f in feats}

    # For each pair, score:
    #   - spectral_agree: count of projs where both F-IDs have the same non-zero value
    #   - spectral_disagree: count of informative disagreements on spectral cols
    #   - arith_agree / arith_disagree: same for arithmetic cols
    # "Drum-shape candidate": spectral_disagree == 0 AND spectral_agree >= 1
    #   AND arith_disagree >= 1 (i.e. spectrum cannot tell them apart,
    #   arithmetic can).
    # "Reverse drum": arith_disagree == 0 AND arith_agree >= 1 AND spectral_disagree >= 1
    # (arithmetic cannot tell them apart, spectrum can).
    results = []
    for i, fa in enumerate(feats):
        for fb in feats[i + 1 :]:
            s_agree, s_disagree = hamming_informative(spectral_sigs[fa], spectral_sigs[fb])
            a_agree, a_disagree = hamming_informative(arith_sigs[fa], arith_sigs[fb])
            # Drop pairs where neither lens has any agreement (no shared basis).
            if not s_agree and not a_agree:
                continue
            # Drop pairs where both lenses have zero informative positions (nobody tested).
            if not spectral_sigs[fa] and not spectral_sigs[fb]:
                continue
            if not arith_sigs[fa] and not arith_sigs[fb]:
                continue
            # Drum-shape: agree on spectrum, disagree on arithmetic
            drum_shape = len(s_disagree) == 0 and len(s_agree) >= 1 and len(a_disagree) >= 1
            # Reverse: agree on arithmetic, disagree on spectrum
            reverse = len(a_disagree) == 0 and len(a_agree) >= 1 and len(s_disagree) >= 1
            # Mixed: both lenses have some agreement AND some disagreement
            mixed = len(s_agree) >= 1 and len(s_disagree) >= 1 and len(a_agree) >= 1 and len(a_disagree) >= 1
            if drum_shape or reverse or mixed:
                results.append(
                    {
                        "f_a": fa,
                        "f_b": fb,
                        "shape": "drum_shape" if drum_shape else ("reverse_drum" if reverse else "mixed"),
                        "spectral_agree": s_agree,
                        "spectral_disagree": s_disagree,
                        "arith_agree": a_agree,
                        "arith_disagree": a_disagree,
                        "n_s_agree": len(s_agree),
                        "n_s_disagree": len(s_disagree),
                        "n_a_agree": len(a_agree),
                        "n_a_disagree": len(a_disagree),
                    }
                )

    # Ranking: drum_shape first (most informative), then mixed, then reverse.
    # Within each class, rank by (more lens agreement on the "same" side, more disagreement on the "different" side).
    shape_order = {"drum_shape": 0, "reverse_drum": 2, "mixed": 1}

    def rank_key(r):
        if r["shape"] == "drum_shape":
            # primary: max spectral agreement; secondary: max arith disagreement
            return (0, -r["n_s_agree"], -r["n_a_disagree"])
        if r["shape"] == "reverse_drum":
            return (2, -r["n_a_agree"], -r["n_s_disagree"])
        # mixed
        return (1, -(r["n_s_agree"] + r["n_a_agree"]), -(r["n_s_disagree"] + r["n_a_disagree"]))

    results.sort(key=rank_key)

    # Print summary
    shape_counter = Counter(r["shape"] for r in results)
    print(f"Total informative pairs: {len(results)}")
    print(f"  drum_shape (spectrum blind, arithmetic separates): {shape_counter['drum_shape']}")
    print(f"  reverse_drum (arithmetic blind, spectrum separates): {shape_counter['reverse_drum']}")
    print(f"  mixed (both lenses partially resolve):             {shape_counter['mixed']}")
    print()

    print("=== TOP 10 DRUM-SHAPE pairs ===")
    drum = [r for r in results if r["shape"] == "drum_shape"][:10]
    for r in drum:
        s_ag_str = ", ".join(f"{p}={v}" for p, v in r["spectral_agree"])
        a_dg_str = ", ".join(f"{p}=[{va} vs {vb}]" for p, va, vb in r["arith_disagree"])
        print(f"  {r['f_a']} ~ {r['f_b']}")
        print(f"    spectrum agree [{r['n_s_agree']}]:   {s_ag_str}")
        print(f"    arithmetic separates [{r['n_a_disagree']}]: {a_dg_str}")

    print()
    print("=== TOP 10 REVERSE-DRUM pairs ===")
    rev = [r for r in results if r["shape"] == "reverse_drum"][:10]
    for r in rev:
        a_ag_str = ", ".join(f"{p}={v}" for p, v in r["arith_agree"])
        s_dg_str = ", ".join(f"{p}=[{va} vs {vb}]" for p, va, vb in r["spectral_disagree"])
        print(f"  {r['f_a']} ~ {r['f_b']}")
        print(f"    arithmetic agree [{r['n_a_agree']}]:   {a_ag_str}")
        print(f"    spectrum separates [{r['n_s_disagree']}]: {s_dg_str}")

    # Dump full JSON to tmp for downstream analysis
    out_path = Path("harmonia/tmp/drum_shape_separator_scan.json")
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nFull results: {out_path} ({len(results)} pairs)")


if __name__ == "__main__":
    main()
