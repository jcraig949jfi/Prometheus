# BOOTSTRAP_NOTEBOOK — Harmonia A, expedition prologue

**Status: EXPLORATORY EVIDENCE ONLY** (expedition brief §3). Nothing here is a
scientific finding. Purpose: activate mathematical problem-solving mode against
five diverse landscapes, using the canonical strategy repertoire, and record the
process — especially operations that recur across problems.

**Canonical repertoire located and used** (not recreated from memory):
`aporia/meta/studies/2026-05-05/` — the 20-study meta-research batch
(study_01 minimal generative bases … study_19 notation meta, + SYNTHESIS.md).
Strategies invoked below are cited as [S-NN].

Computations: `explore.py` → `bootstrap_results.json` (deterministic, seeded).

---

## P1 — Union-closed sets (Frankl). Combinatorial/discrete.

**Strategies:** exhaustive small cases [S-04 empirical rediscovery], extremal
analysis [S-18 edge cases], invariant hunting [S-07].
**Did:** enumerated ALL union-closed families for n=2 (6 families) and n=3 (60);
sampled 20k closure-generated families for n=4.
**Observed:** worst max-element frequency = 2/3, 4/7, 8/15 — recognized as
`2^(n-1)/(2^n−1)`: the full power-set family is the extremal witness, frequency
→ 1/2 from above. The conjecture is tight only asymptotically.
**Failed decomposition:** tried to see a weighting/averaging argument over the
lattice; the natural averaging gives 1/2 only for the power set — no traction on
general families in the time budget (as expected; the known 2022 breakthrough
used entropy, a representation change I did not attempt to reproduce).
**Operations used:** enumerate-then-recognize; quotient by the extremal object.

## P2 — Lehmer's problem. Algebraic/symbolic.

**Strategies:** canonical forms [S-17] (reciprocal/palindromic normalization),
invariants as anchors [S-07], noise vs signal [S-16].
**Did:** sampled 120k height-1 integer polynomials deg 4–10, computed Mahler
measures; checked Lehmer's polynomial = 1.176281 (matches).
**INSTRUMENT LESSON (the best thing in this notebook):** my `floor_beaten`
flag fired TRUE — on inspection the "sub-Lehmer" measures (1.000001…1.000005)
are cyclotomic polynomials plus `np.roots` float error. My exclusion band
(1+1e-9) was tighter than my instrument's noise floor. The genuine nontrivial
minimum found was 1.230391 > 1.176281: the floor HELD. This is the
instrument-error-is-not-evidence doctrine reproducing itself spontaneously in a
20-line script: **a detection threshold must be calibrated against the
measurement noise, or the detector manufactures discoveries.** Direct
ancestor of Gen-2's triviality-epsilon decision.
**Operations used:** canonicalize; calibrate-the-detector-before-believing-it.

## P3 — Lonely runner. Geometric.

**Strategies:** projection/quotient [S-08 dimensional lifting, inverted],
extremal witness [S-18].
**Did:** view-from-runner-0 reduction (k runners → k−1 nonzero speeds on the
circle), exact-grid verification for k=3,4,5. Bound 1/k met in every case;
tight exactly at consecutive speeds (1,2,…,k−1).
**Observed:** the tight configuration is again the "most canonical" object —
same shape as P1. Two landscapes, one meta-pattern: **the extremal witness of
a hard conjecture tends to be the maximally symmetric object**, and progress
lives in proving nothing less symmetric beats it.
**Operations used:** quotient by one coordinate; grid-certify a continuous
claim with an explicit resolution bound.

## P4 — Collatz through the 2-adic lens. Dynamical/algorithmic.

**Strategies:** representation change [S-15 objects as programs], variance
decomposition [S-16].
**Did:** measured eta² of the low 8 bits on stopping time over n < 2^16:
**0.108**. Low bits determine the first 8 steps exactly, so some predictive
mass is forced; the measured 0.108 says the forced prefix does not dominate
long-horizon behavior.
**Noticed about my own process:** I reached for eta²-by-class — the SAME
adjudication operation I froze in Gen-1's analyzer. An analysis operation
built for one substrate transported unchanged to an unrelated one.
**Operations used:** lift to a completion (2-adic framing); decompose variance
by a mechanically defined class; separate forced-prefix from empirical-tail —
which is literally Gen-1's Layer-0/Layer-1 split, recurring in the wild.

## P5 — Shortest addition chains. Representation-hostile (chosen for it).

**Strategies:** exact search [S-11 search landscapes], mutation-operator
analysis [S-06].
**Did:** exact l(n) for n ≤ 128 by IDDFS; Scholz conjecture
l(2^n−1) ≤ n−1+l(n) verified for n = 2…6 (all tight, all hold).
**Observed:** l(128) = 7 vs l(127) = 10 — VALUE-adjacent targets are
CHAIN-SPACE-distant. The chain representation has hostile mutation geometry by
construction: a single early substitution invalidates every later element
(each element must be a sum of two predecessors), so "small edit" barely
exists. This is D-13's stackvm wall as a THEOREM-ADJACENT property of a
classical object: the representation's validity constraint couples every site
to every later site. Candidate mechanistic variable for Gen-3: **downstream
validity coupling** (how many later sites an edit at site i can invalidate).
**Operations used:** iterative deepening with admissible pruning; convert a
conjecture to finite spot checks; read the SEARCH TREE's shape as data about
the representation, not just the answer.

---

## Recurring operations across the five landscapes (Gen-4/5 candidates)

1. **enumerate-then-recognize** (P1, P3): exhaust a small regime, then match
   the extremal witness to a canonical object. Two uses, two hits.
2. **calibrate-the-detector** (P2): every threshold needs a measured noise
   floor before its firings mean anything. Program-wide doctrine, reinvented
   spontaneously at problem scale.
3. **variance-decomposition-by-mechanical-class** (P4 + Gen-1 analyzer): eta²
   against a frozen classing — transported unchanged across substrates.
4. **forced-layer-first** (P4, P2 + Gen-1 freeze §3): identify what arithmetic
   already determines before measuring anything; the same split three times.
5. **quotient-by-symmetry / canonicalize** (P1, P2, P3): reduce before search.
6. **read-the-search-tree-as-data** (P5): the shape of failure during search
   characterizes the representation — this is the expedition's own thesis
   appearing at problem scale.

Operations 3 and 4 are already reified in committed analyzer code (Gen-1).
Operations 1, 5, 6 are candidates for Gen-4's "operation derived from
experience" test families — flagged, not promoted.

## What this bootstrap changes about Gen-2 (design input, not evidence)

- P2's instrument lesson → Gen-2's triviality threshold must be justified
  against the object population's band, not chosen aesthetically.
- P5's validity-coupling observation → Gen-2's ruler must carry a FAULT class
  even though the circuit substrate cannot exercise it (Gen-3 substrates with
  validity constraints will).
- P4's forced/empirical split → Gen-2 declares forced cells before running,
  as Gen-0/Gen-1 did.
