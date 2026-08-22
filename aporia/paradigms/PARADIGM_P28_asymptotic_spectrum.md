# PARADIGM P28 — Asymptotic Spectrum (worked example + decision tree + code skeleton)

Aporia P96, 2026-08-21. Source: taxonomy P28 (tensor round; Strassen
exemplar; catalog refs #1-2, #7-8, #16-17 in tensor_open_problems_v1.md).
Consumer: Learner corpus type C. Emitted to paradigm_trees.jsonl. Tier 27/30.

**The move**: the asymptotic value of a tensor pre-order is governed by its
MONOTONES — functionals respecting restriction; each admitted monotone is a
spectrum point (verb: ADMIT-MONOTONES; payoff verb:
ASYMPTOTIC-VALUES-FROM-FUNCTIONAL-EVALUATION).

## 1. Worked example — EXECUTED (`paradigm_p28_worked_example.py`)

- **A.** Restrictions CONSTRUCTED then verified ENTRYWISE: ⟨2⟩ ≤ ⟨3⟩
  (padding), **M⟨2⟩ ≤ ⟨7⟩ with the restriction maps built from P15's
  entrywise-verified Strassen triples** — cross-paradigm reuse: the same
  seven vectors serve P15 as a decomposition, P23 as a bootstrapping saving,
  and here as a restriction certificate.
- **B.** Admission test: all three flattening ranks monotone non-increasing
  under every verified restriction ((7,7,7)→(4,4,4) on the Strassen pair).
- **C.** DECLINE leg: the candidate functional nnz is REJECTED — two
  witnesses (rotation of ⟨2⟩: nnz 2→8; the Strassen pair itself: 7→8).
  An admission test that cannot reject admits nothing.
- **D.** Asymptotic flavor: ⟨2⟩⊗⟨2⟩ = ⟨4⟩ exactly with flattenings
  multiplying — the regularization that upgrades a monotone to a spectrum
  point. Verdict: **SPECTRUM-ADMITS**.

## 2. Decision tree

- Q1: Is the question ASYMPTOTIC (rank of powers, amortized cost, ω-class
  exponents) over a pre-order with a tensoring operation? — NO: single-shot
  rank questions belong to P15/P29/P31.
- Q1 YES — Q2: Do you have candidate MONOTONES, each with (a) computability
  and (b) a monotonicity proof or an executable admission test over verified
  restrictions? — NO: build the admission harness first — candidates are
  cheap, admitted spectrum points are the currency.
- Q2 YES — Q3: Are your restrictions VERIFIED (constructed maps, entrywise
  identity), not asserted? — NO: an unverified restriction can fake or hide
  monotonicity; verify first.
- Q3 YES — EXECUTE: run the admission test (with decline candidates
  included), evaluate admitted monotones on the target and its powers, and
  read the asymptotic bound as the max over admitted points — knowing the
  spectrum is COMPLETE is the deep part (Strassen's theorem), and partial
  spectra give one-sided bounds only, stated.

## 3. Code skeleton

```python
def spectrum_attack(candidates, restrictions, target, powers):
    """P28 template. Restrictions verified entrywise; admission test with
    decline candidates; partial spectra give one-sided bounds (stated)."""
    for (S, maps, T) in restrictions:
        assert entrywise_equal(apply_maps(S, *maps), T), "restriction unverified"
    admitted = [f for f in candidates
                if all(f(T) <= f(S) for S, _, T in restrictions)]
    assert len(admitted) < len(candidates), "no candidate rejected — test toothless"
    return {"admitted": admitted,
            "one_sided_bound": max(f(target) for f in admitted)}
```

## 4. Catalog assignment

Primary: tensor_open_problems_v1.md #1-2 (ω, Strassen's asymptotic rank
conjecture), #7-8, #16-17 (per the taxonomy refs — verified present in the
doc's structure). The substrate's CoordinateChart/asymptotic-restriction
primitive is the internal consumer. Anti-assignment: all triage MATH rows.

## Provenance and honesty

Strassen's spectrum theory is settled; the content is the executable
admission harness with verified restrictions and a decline leg that fired
twice, plus the three-way reuse of the Strassen triples across P15/P23/P28 —
the tier's instruments composing across paradigms for the first time.
