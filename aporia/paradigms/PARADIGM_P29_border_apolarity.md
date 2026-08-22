# PARADIGM P29 — Border Apolarity (worked example + decision tree + code skeleton)

Aporia P96, 2026-08-21. Source: taxonomy P29 (tensor round; Buczynska-
Buczynski / Landsberg-Michalek exemplar). Consumer: Learner corpus type C.
Emitted to paradigm_trees.jsonl. Tier 28/30. **Hybrid: executed shadow +
typed STRUCTURAL-GAP** (Macaulay2 probed ABSENT — `which M2 macaulay2`
empty).

**The move**: bound border rank via apolar schemes and Hilbert-function
bookkeeping (verb: BOUND-BY-APOLAR-SCHEME; payoff verb:
BORDER-RANK-CERTIFICATES-FROM-COMMUTATIVE-ALGEBRA).

## 1. Worked example — the pure-python shadow, EXECUTED
(`paradigm_p29_worked_example.py`)

Classical binary apolarity, where the whole theory is exact linear algebra:

- **A.** Catalecticant (Hankel) matrices built from the apolarity pairing's
  DEFINITION; ranks on power-sum anchors x^d+y^d all exactly **2** (their
  Waring rank), d = 3..6.
- **B.** x·y²'s middle catalecticant rank = **2** — the border-rank-2
  signature.
- **C.** The rank/border-rank GAP at the smallest possible case, both sides
  executed: the rank-2 family (1/3ε)[(y+εx)³ − y³] converges to x·y² with
  coefficient error of log-log slope **1.0000** (derived: the ε term
  dominates) — border rank 2 witnessed; while the degree-2 annihilator
  computed from the apolar action is spanned by **X² alone** — a double
  root, so no square-free apolar conic exists and exact Waring rank is 3
  (Sylvester). The paradigm's raison d'être — limits reach what sums
  cannot — as a five-line computation. Verdict: **APOLARITY-SHADOW-RUNS**.

## STRUCTURAL-GAP (typed)

Border apolarity PROPER — multigraded Hilbert schemes, B-invariant ideal
enumeration, the R̲(M⟨3⟩) ≥ 17 class of bounds — needs Macaulay2-class
machinery (SecantVarieties, Apolarity packages), probed absent. What the
toolchain would need: an M2 install (free, scriptable) or a pure-python
multigraded Hilbert-function engine (a real project). The shadow above is
the paradigm's ENGINE (apolar bookkeeping separating rank from border rank)
at the scale our tools reach.

## 2. Decision tree

- Q1: Is the target a BORDER-RANK (or cactus/scheme-rank) bound where
  flattening-class methods stall? — NO: flattenings (P28's monotones) are
  cheaper; use them first.
- Q1 YES — Q2: Is the apolar/annihilator structure COMPUTABLE at your scale
  (binary forms: Hankel algebra; general: Macaulay2-class tooling)? — NO:
  type the tooling gap with its exact requirements; the binary shadow may
  still calibrate intuitions.
- Q2 YES — Q3: Does the Hilbert-function bookkeeping give a certificate
  (Gorenstein symmetry, root structure of the annihilator) that DISTINGUISHES
  rank from border rank? — YES: execute both sides — the convergent family
  (border) AND the algebraic obstruction (exact) — one side alone tells half
  the story.

## 3. Code skeleton

```python
def apolarity_attack(form, degree):
    """P29 template (binary shadow). Both sides of the gap, always."""
    cats = [hankel_rank(form, k) for k in range(1, degree)]
    border_lb = max(cats)                       # catalecticant lower bound
    ann = annihilator_basis(form, 2)            # apolar operators
    exact_rank_obstruction = has_only_multiple_roots(ann)
    return {"border_rank_lb": border_lb,
            "exact_exceeds_border": exact_rank_obstruction,
            "certificates": {"catalecticants": cats, "annihilator": ann}}
```

## 4. Catalog assignment

Primary: tensor_open_problems_v1.md #4-5 (M⟨3⟩ rank/border-rank — the gap's
research frontier, gated on the M2 tooling), #26-35 class. Anti-assignment:
all triage MATH rows; and within tensors, anything flattenings already
settle (Q1's guard). Escalation: an M2 install is the single unlock for
this paradigm's research range — filed as the gap's requirement.

## Provenance and honesty

Sylvester 1851 at toy scale; the content is both sides of the border-rank
gap executed in one script (the convergent family AND the double-root
obstruction), the definition-built Hankel machinery, and the honestly-typed
tooling gap with its one-item unlock.
