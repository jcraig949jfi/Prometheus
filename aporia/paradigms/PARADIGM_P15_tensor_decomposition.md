# PARADIGM P15 — Tensor and Multilinear Decomposition (worked example + decision tree + code skeleton)

Aporia P87, 2026-08-21. Source: taxonomy P15; DR grounding 00052 (Kruskal
uniqueness frontier — OPENED, key points read: matroidal refinements, secant
varieties, overcomplete-regime algorithms via Koszul-Young flattenings).
Consumer: Learner corpus type C. Emitted to paradigm_trees.jsonl.

**The move**: decompose multi-index arrays into structured sums; the rank IS
the hidden structure (verb: DECOMPOSE-MULTILINEARLY; payoff verb:
READ-INTERACTION-GEOMETRY-FROM-RANK).

## 1. Worked example — EXECUTED (`paradigm_p15_worked_example.py`)

- **A. Strassen rank-7, entrywise.** The 2×2 matmul tensor built from its
  bilinear-map DEFINITION (8 ones — gate), then reconstructed EXACTLY
  (64/64 integer entries) from both the naive rank-8 decomposition and
  Strassen's seven triples. The strict rank drop 8→7 — verified here at the
  entry level — is the seed of all fast matrix multiplication.
- **B. Kruskal certificate, computed and CORRECTLY DECLINING.** k-ranks by
  definition (all column subsets): kA=kB=kC=2, sum 6 < 2R+2=16 — the
  certificate cannot certify uniqueness for Strassen's factors, and that is
  RIGHT: matmul decompositions are famously non-unique. A certificate that
  declines exactly where uniqueness genuinely fails is evidence the
  certificate is real (the P13 detector lesson, decomposition edition).
  Report 00052's frontier (matroidal splittings, generic uniqueness via
  secant varieties) is precisely the study of when such certificates extend.

Verdict: **RANK7-VERIFIED**.

## 2. Decision tree

- Q1: Is the object naturally MULTI-INDEX (an array/multilinear map, order
  ≥ 3)? — NO: matrices have rotational ambiguity; order-2 belongs to SVD
  land, not this paradigm.
- Q1 YES — Q2: Is the question RANK-SHAPED (minimal terms, bond dimension,
  interaction structure)? — NO: elementwise/statistical questions do not
  need decomposition machinery.
- Q2 YES — Q3: EXACT or approximate regime? EXACT: verify any claimed
  decomposition ENTRYWISE (leg-A pattern — a decomposition unverified at the
  entries is a rumor); border-rank subtleties mean rank itself may be
  discontinuous — state which rank notion is in play. APPROXIMATE: fix the
  target precision and the decomposition model (CP/TT/Tucker) FIRST.
- Q3 → Q4: Does uniqueness MATTER for the conclusion (latent factors read as
  real objects)? — YES: compute an identifiability certificate (Kruskal by
  definition, or the 00052-class refinements) and respect its verdict — a
  declined certificate means the factors are NOT interpretable as unique
  latent structure, whatever the reconstruction error says.
- EXECUTE with both gates.

## 3. Code skeleton

```python
def decomposition_attack(tensor, triples, check_uniqueness=True):
    """P15 template. Entrywise reconstruction is mandatory; the Kruskal
    certificate's DECLINE is as informative as its assent."""
    rec = sum(np.einsum("i,j,k->ijk", a, b, c) for a, b, c in triples)
    assert np.array_equal(rec, tensor), "decomposition is a rumor — entries differ"
    result = {"rank_witnessed": len(triples)}
    if check_uniqueness:
        kA, kB, kC = (k_rank(np.stack([t[m] for t in triples], 1)) for m in range(3))
        result["kruskal_certifies"] = (kA + kB + kC >= 2 * len(triples) + 2)
    return result
```

## 4. Catalog assignment

Primary: Prometheus-INTERNAL — the dissection tensor (86K×145×11), TT bond
dimensions on Sleeping Beauties, Techne's pm.tensor_train lane (cycle 002)
— this paradigm is the program's compute fabric (feedback_tensors_near_and_
dear) more than a catalog attack. Catalog: 0334 (volume conjecture data is
tensor-shaped), 0332 (Jones via Temperley-Lieb representations). Secondary:
any archive-wide statistic that factors (0478's per-degree structure).
Anti-assignment: scalar-sequence rows (0057/0058/0479-0485) — no multi-index
structure (Q1=NO).

## Provenance and honesty

Strassen is 1969; Kruskal 1977. The content is the definition-built tensor
(index conventions being the classic trap — carried visibly), the entrywise
verification discipline, and the declined certificate read as SIGNAL. The
third-leg synergy is implicit: this paradigm's serious local consumer is
Techne's TT lane, one more cross-channel edge for the tier's consumption map.
