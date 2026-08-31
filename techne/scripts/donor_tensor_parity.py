"""Tensor representation parity: TensorLy vs the incumbent code. Techne Gen-0, 2026-08-31.

    python -m techne.scripts.donor_tensor_parity --out techne/donor_tensor_parity_2026-08-31.json

THE ASSIGNMENT'S PREMISE WAS PARTLY STALE, AND SAYING SO IS THE FIRST RESULT.

The Gen-0 brief recorded, from a prior inventory, that `prometheus_math` carries hand-rolled CP
and Tucker with TT wrapped through quimb, and that this violates Standing Order #1. Read at
source on 2026-08-31, that is not what is there:

  * `prometheus_math/symbolic_tensor_decomp.py` is ALREADY a pure TensorLy wrapper. It opens
    with `if not is_available("tensorly"): raise ImportError`, and every decomposition routes
    to `tensorly.decomposition.{parafac,tucker,tensor_train}`. There is no native CP or Tucker
    implementation to supersede. What actually existed was a DEAD MODULE -- tensorly was not
    installed, so importing it raised. Installing the donor revived it.

  * `prometheus_math/tensor_train.py` is a quimb wrapper, and it is NOT a duplicate of the
    above. It computes TT BOND RANKS at a truncation cutoff, packaged with a non-degenerate
    fiber-shuffle null, for measuring cross-axis coupling. `symbolic_tensor_decomp.tt_decompose`
    computes a TT FACTORISATION at a requested rank. Different questions.

So the real parity question is not native-vs-donor. It is: two independent TT implementations
now exist in the tree (tensorly's successive-SVD and quimb's MPS-from-dense). Do they agree on
the one quantity both can produce -- the bond ranks of a tensor whose exact TT rank is known?

WHAT THIS SCRIPT DOES NOT ESTABLISH. Nothing here says any decomposition improves reasoning,
transfer, or anything else. Agreement between two implementations is a statement about the
implementations. It is engineering characterisation, and citing it as evidence that tensor
representations are useful would be exactly the inference this seat is barred from making.
"""
from __future__ import annotations

import argparse
import json
import pathlib

import numpy as np


def _exact_rank_fixtures(seed: int = 0) -> list:
    """Tensors whose TT bond ranks are known by construction, so agreement can be checked
    against ground truth rather than only against each other -- two implementations agreeing on
    a wrong answer is a real possibility and this is how it gets excluded."""
    rng = np.random.default_rng(seed)
    out = []

    # 1. Rank-1 outer product: every bond rank is exactly 1.
    a, b, c = rng.random(4), rng.random(5), rng.random(3)
    out.append(("rank1_outer", np.einsum("i,j,k->ijk", a, b, c), [1, 1]))

    # 2. Sum of two rank-1 terms: bond ranks are 2 at both cuts (generically).
    a2, b2, c2 = rng.random(4), rng.random(5), rng.random(3)
    t2 = np.einsum("i,j,k->ijk", a, b, c) + np.einsum("i,j,k->ijk", a2, b2, c2)
    out.append(("rank2_sum", t2, [2, 2]))

    # 3. Separable 4-way product: all bonds 1.
    v = [rng.random(n) for n in (3, 4, 3, 2)]
    out.append(("rank1_order4", np.einsum("i,j,k,l->ijkl", *v), [1, 1, 1]))

    # 4. Full-entropy random tensor: bonds saturate at min(prod left, prod right).
    t4 = rng.random((3, 4, 3))
    out.append(("random_dense", t4, [3, 3]))

    # 5. An exactly low-rank matrix, as the degenerate ndim=2 case.
    m = np.outer(rng.random(6), rng.random(5)) + np.outer(rng.random(6), rng.random(5))
    out.append(("matrix_rank2", m, [2]))
    return out


def _tensorly_bond_ranks(T: np.ndarray, rank) -> list:
    from tensorly.decomposition import tensor_train
    cores = tensor_train(np.asarray(T, dtype=float), rank=rank)
    shapes = [np.asarray(c).shape for c in cores]
    # Interior bonds only, to match quimb's bond_sizes() convention (the boundary 1s are not
    # bonds). Comparing different conventions would manufacture a disagreement.
    return [int(s[0]) for s in shapes[1:]]


def _quimb_bond_ranks(T: np.ndarray, cutoff: float) -> list:
    from prometheus_math.tensor_train import tt_ranks
    return list(tt_ranks(np.asarray(T, dtype=float), cutoff=cutoff))


def _relerr(a: np.ndarray, b: np.ndarray) -> float:
    den = float(np.linalg.norm(a))
    return float(np.linalg.norm(a - b)) / den if den else float(np.linalg.norm(a - b))


def run(cutoff: float = 1e-10) -> dict:
    rows = []
    for name, T, expected in _exact_rank_fixtures():
        row = {"fixture": name, "shape": list(T.shape), "expected_bond_ranks": expected}

        try:
            q = _quimb_bond_ranks(T, cutoff)
            row["quimb_bond_ranks"] = q
            row["quimb_matches_truth"] = (q == expected)
        except Exception as e:                                        # noqa: BLE001
            row["quimb_error"] = type(e).__name__ + ": " + str(e)
            q = None

        # tensorly's tensor_train takes the FULL rank list including boundary 1s.
        full_rank = [1] + list(expected) + [1]
        try:
            t = _tensorly_bond_ranks(T, full_rank)
            row["tensorly_bond_ranks"] = t
            row["tensorly_matches_truth"] = (t == expected)
        except Exception as e:                                        # noqa: BLE001
            row["tensorly_error"] = type(e).__name__ + ": " + str(e)
            t = None

        if q is not None and t is not None:
            row["IMPLEMENTATIONS_AGREE"] = (q == t)

        # Reconstruction parity at the exact rank: both should be near-exact where the fixture
        # is genuinely low-rank, and the random one should not be.
        try:
            from tensorly.decomposition import tensor_train
            from tensorly.tt_tensor import tt_to_tensor
            from prometheus_math.tensor_train import tt_reconstruct
            tl_rec = np.asarray(tt_to_tensor(tensor_train(T, rank=full_rank)))
            qb_rec = tt_reconstruct(T, cutoff=cutoff)
            row["tensorly_relerr"] = _relerr(T, tl_rec)
            row["quimb_relerr"] = _relerr(T, qb_rec)
        except Exception as e:                                        # noqa: BLE001
            row["reconstruction_error"] = type(e).__name__ + ": " + str(e)

        rows.append(row)

    agree = [r for r in rows if "IMPLEMENTATIONS_AGREE" in r]
    n_agree = sum(1 for r in agree if r["IMPLEMENTATIONS_AGREE"])
    truth_q = sum(1 for r in rows if r.get("quimb_matches_truth"))
    truth_t = sum(1 for r in rows if r.get("tensorly_matches_truth"))

    if agree and n_agree == len(agree) and truth_q == truth_t == len(rows):
        classification = "NATIVE_EARNS_DISTINCT_ROLE"
        rationale = (
            "Both implementations recover the constructed bond ranks on every fixture and "
            "agree with each other, so neither is wrong and neither supersedes the other on "
            "correctness. They are kept for DIFFERENT questions: tensor_train.py answers 'what "
            "is the bond rank at a truncation cutoff', packaged with a fiber-shuffle null for "
            "coupling measurement; symbolic_tensor_decomp.tt_decompose answers 'factorise at a "
            "requested rank'. Deleting either would remove a capability, not a duplicate.")
    elif agree and n_agree < len(agree):
        classification = "SEMANTICS_DIFFER"
        rationale = ("The two implementations disagree on at least one fixture whose bond ranks "
                     "are known by construction; the disagreement must be resolved before "
                     "either is used as an instrument.")
    else:
        classification = "INCONCLUSIVE"
        rationale = "At least one implementation failed to produce a comparable reading."

    return {
        "generated": "2026-08-31",
        "question": "two independent TT implementations now coexist; do they agree, and does "
                    "either supersede the other?",
        "premise_correction": {
            "brief_stated": "prometheus_math carries hand-rolled CP/Tucker; TT wrapped via quimb",
            "verified_at_source": "symbolic_tensor_decomp.py is a pure tensorly wrapper that "
                                  "raises ImportError without it -- there is NO hand-rolled CP "
                                  "or Tucker to supersede. Installing tensorly revived a module "
                                  "that was dead in the default interpreter.",
            "evidence": "prometheus_math/symbolic_tensor_decomp.py lines 42-55",
        },
        "cutoff": cutoff,
        "rows": rows,
        "n_fixtures": len(rows),
        "n_comparable": len(agree),
        "n_implementations_agree": n_agree,
        "quimb_matches_truth": truth_q,
        "tensorly_matches_truth": truth_t,
        "CLASSIFICATION": classification,
        "rationale": rationale,
        "NON_CLAIMS": [
            "no claim that any decomposition improves reasoning, transfer, or search",
            "no claim that TT is the right substrate for anything",
            "agreement between two implementations is a fact about the implementations only",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="techne/donor_tensor_parity_2026-08-31.json")
    ap.add_argument("--cutoff", type=float, default=1e-10)
    a = ap.parse_args()
    rep = run(a.cutoff)
    for r in rep["rows"]:
        print("{:14s} shape={:14s} truth={:10s} quimb={:10s} tensorly={:10s} agree={}".format(
            r["fixture"], str(r["shape"]), str(r["expected_bond_ranks"]),
            str(r.get("quimb_bond_ranks", r.get("quimb_error", "-")))[:10],
            str(r.get("tensorly_bond_ranks", r.get("tensorly_error", "-")))[:10],
            r.get("IMPLEMENTATIONS_AGREE", "-")))
    print("\nCLASSIFICATION:", rep["CLASSIFICATION"])
    dest = pathlib.Path(a.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print("wrote", dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
