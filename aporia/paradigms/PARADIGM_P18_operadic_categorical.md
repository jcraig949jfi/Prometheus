# PARADIGM P18 — Operadic / Categorical Composition (worked example + decision tree + code skeleton)

Aporia P89, 2026-08-21. Source: taxonomy P18; no DR grounding in BACKCORPUS
(checked). Consumer: Learner corpus type C. Emitted to paradigm_trees.jsonl.

**The move**: make the composition structure itself the object; prove theorems
about how structures combine (verb: COMPOSE-AS-OBJECT; payoff verb:
ONE-COHERENCE-THEOREM-COVERS-EVERY-DIAGRAM).

## 1. Worked example — EXECUTED, hybrid per the P14 pattern
(`paradigm_p18_worked_example.py`)

Mac Lane's pentagon meeting group cohomology, non-tautologically:

- For Z/2-graded lines with associator scalars ω: (Z/2)³ → {±1}, the pentagon
  identity was checked by TWO routes sharing no code: literal 16×16
  diagonal-matrix composition of both re-bracketing paths on the 4-fold
  product, vs the pointwise 3-cocycle formula. **Agreement on all 256
  candidate ω** — the categorical diagram and the algebraic condition are the
  same fact, verified rather than recited.
- Cohomology census: 8 cocycles / 4 distinct coboundaries (enumerated by
  definition) → **|H³(Z/2, Z/2)| = 2**, the classical value ARRIVING from the
  count. Coherence data up to equivalence IS cohomology, witnessed at the
  smallest nontrivial scale. Verdict: **COHERENCE-IS-COHOMOLOGY**.

STRUCTURAL-GAP (typed): ∞-categories, topos-level structure, and the
Fargues-Scholze/Gaitsgory frontier have no executable local substrate — the
decidable shadow is FINITE coherence (pentagon/hexagon on concrete gradings),
which is exactly what runs here. Lean+Mathlib could formalize more (the P10
bind is the road); typed as the escalation path, not attempted in a pass.

## 2. Decision tree

- Q1: Is the difficulty about how structures COMBINE (compositions,
  products, gluings) rather than about any single structure? — NO: category
  theory as bookkeeping adds names, not power; exit.
- Q1 YES — Q2: Is there a COHERENCE-CLASS theorem (Mac Lane, operad
  recognition) or a classifying invariant (cohomology) that collapses
  infinitely many diagrams to finitely many conditions? — NO: ad-hoc diagram
  chasing scales exponentially; find the coherence theorem first.
- Q2 YES — Q3: Is the compositional shadow DECIDABLE at your scale (finite
  group gradings, finite operads, concrete monoidal data)? — NO: type the
  meta-level as a gap with its escalation path (kernel formalization); the
  paradigm still serves as an ORGANIZING lens.
- Q3 YES — EXECUTE: verify coherence by two independent routes (diagram-level
  composition vs condition-level formula — the routes' agreement is the
  certificate), then read the classifying invariant from the census.

## 3. Code skeleton

```python
def coherence_attack(candidates, diagram_route, condition_route, classify):
    """P18 template. Diagram-level and condition-level routes must agree on
    EVERY candidate before the classifying census is read."""
    for c in candidates:
        assert diagram_route(c) == condition_route(c), f"routes disagree at {c}"
    satisfying = [c for c in candidates if condition_route(c)]
    return {"n_satisfying": len(satisfying), "classes": classify(satisfying)}
```

## 4. Catalog assignment

Primary: none executable at catalog level — the paradigm is an ORGANIZING
lens (fourth empty primary; same family as P14's diagnostic duty — the
composition lens explains WHY translations compose in P01 chains and what the
Rosetta-stone ambitions need structurally). Prometheus-internal: the
cross-domain operadic-skeleton idea (taxonomy's own note) targets the tensor,
not catalog rows. Anti-assignment: all single-object rows (Q1=NO for
0057-0485-class attacks as stated).

## Provenance and honesty

Pentagon-coherence-equals-cocycle is textbook (Mac Lane / Eilenberg); the
content is the two-route verification (the routes genuinely could disagree
under an index fault — that is what makes agreement a certificate), the
census-derived H³, and the honest typing of everything above finite coherence
as escalation rather than execution.
