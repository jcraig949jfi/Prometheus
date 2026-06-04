# Failure-Signal Protocol v0.1 — schema, tests, nulls, metrics

**Filed:** 2026-06-04
**Author:** Aporia (in-session), absorbing the 2026-06-04 frontier review
**Status:** Preregistration. Operational sibling of
`aporia/docs/science_of_failure_v0.1.md`. This doc speaks in schemas, thresholds,
randomizations, held-out catalogs and effect sizes — NOT in wells/horizons. Nothing
here is run before the criteria here are frozen.
**Why it exists:** the conceptual frame is subordinate to one experimental claim
(the Central Law). This is how that claim is made killable.

---

## 0. The Central Law (the only thing doctrine will mean)

> A science of failure exists **iff** structured failure signals predict withheld
> or constructible mathematical occupants — ones **not trivially operator-reachable
> from visible wells** — better than a null.

Everything below exists to make that statement testable, with no escape hatches.

---

## 1. Atomic record (append-only, one JSONL line each)

```
{
  "id":           "<sha1(inputs|move)>",
  "inputs":       ["<node>", ...],        // objects combined / perturbed
  "move":         "<operator/verb>",       // what was attempted
  "motif":        "<lens>",                // EMITTED BY A TEST (Section 2), never named
  "outcome_type": "MATCH|NOVEL|DEGENERATE|TYPE_MISMATCH|DOMAIN_ERROR|DIVERGENT|CONTRADICTION",
  "magnitude":    <float|null>,            // metric-motif only
  "persistence":  <float|null>,            // filtration survival (Section 4)
  "null_p":       <float>,                 // randomized-baseline probability (Section 3)
  "landscape":    "<name>|cross",
  "provenance":   {"emitter": "<test-id>", "source": "<...>", "born_at": "<iso>"},
  "emitter_version": "<hash>"              // the test code that produced motif/outcome
}
```

`emitter_version` is mandatory: a motif/outcome is only meaningful tied to the exact
deterministic test that produced it. No record without a code-pinned emitter.

---

## 2. Motifs are EMITTED BY TESTS, not named by reviewers

This is the anti-contamination rule (without it H1/H2 are dead on arrival —
`feedback_domains_are_docstrings`, HARD-5). Each motif has a deterministic emitter
with a fixed threshold; assignment is mechanical:

```
TYPE_MISMATCH : input arity/type contract violated (parser/typechecker/category guard)
DIVERGENT     : bounded iteration exceeds growth/step ceiling without converging
CONTRADICTION : solver/prover returns UNSAT / inconsistent constraints
DEGENERATE    : invariant collapses to trivial (all-zero / constant / singleton)
METRIC_DAMAGE : condition number / residual / error > threshold (value recorded in magnitude)
PERSISTENCE   : feature birth/death recorded under filtration (Section 4)
OBSTRUCTION   : local-compatibility passes AND global-assembly test fails
DIAGONAL      : a counter-object generated from the system's own description defeats it
RESOLUTION    : a damage operator repairs a no-match into a catalogued match (the 9)
```

If a motif cannot be emitted without human interpretation, it is **not a motif** —
it is a hypothesis awaiting an emitter (see Section 7 promotion rule).

---

## 3. null_p — explicit randomized baselines (never a guess)

`null_p` is computed, not assigned. Each signal type carries its baseline:

- **Match signals:** P(a random sequence of the same length/term-magnitude matches
  a catalog prefix) — estimated by sampling random integer sequences.
- **Repair/operator edges:** rate at which an **operator-label-shuffled** repair
  graph produces the same edge.
- **Convergence (voids):** rate at which a **degree-preserving rewired** repair graph
  produces a convergence center of equal strength.

A signal with `null_p` above its type's ceiling is logged but excluded from
hypothesis tests (it is exhaust, not residue — `feedback_residue_must_be_navigable_not_logged`).

---

## 4. Persistence (the well-depth metric and the honest usefulness judge)

Filter the repair field by tightening `null_p` (or edge confidence) from loose to
strict. Record, per bridge / component / convergence-center, its **birth** (threshold
at which it appears) and **death** (threshold at which it fragments). Persistence =
death − birth. Structural attractors persist; coincidental ones die early. This is
the single metric for "is this real," and it replaces the mis-specified global-
reachability judge.

---

## 5. Void candidate — DEFINITION (separate from validation)

A void candidate is a **preregistered convergence event**, defined with no reference
to whether it turns out occupied. C is a void candidate iff:

1. C is not occupied by any **visible** catalog object.
2. ≥ `k` independent non-well nodes emit repair vectors whose implied endpoints
   concentrate in C's neighborhood (`k ≥ 3`, frozen before run).
3. Those paths come from ≥ `m` distinct landscapes or motif/operator families
   (`m ≥ 2`).
4. The convergence **survives null_p tightening** (persists, Section 4).
5. A degree-preserving / operator-shuffled null produces a center of equal strength
   at **lower rate** (the convergence beats chance).

Validation (H5, Section 6) is a SEPARATE step. Points 1–5 make something a candidate;
they never reference the hidden occupant. (Aporia refinement over the review, which
folded occupancy into the definition and would have made H5 circular.)

---

## 6. H5 — the void-prediction test, with leakage sealed

**H5:** top-k void candidates recover withheld occupants better than random in-band
points.

### 6.1 The holdout must remove operator-closure, not just a family
OEIS entries are derivable from one another by **the very operators we repair with**
(differences, partial sums, bisections, ...). Hiding Fibonacci (A000045) while
leaving its partial-sums sequence visible lets HIERARCHIZE recover it *trivially* —
a fake void-prediction that is really operator-closure of visible wells. Therefore:

- Hold out an entire structured family / subcatalog / date-bounded slice.
- **Also remove the operator-closure** of the hidden set under the repair operators
  used (compute it explicitly; exclude any visible well within one operator-hop of a
  hidden occupant).
- Freeze all metadata, names, aliases, cross-references of hidden objects.
- Build the failure field with **zero access** to hidden occupants or their closure.

### 6.2 Scoring
- Recovery = a top-k void candidate's neighborhood contains a hidden occupant that is
  **not** within operator-closure of any visible well.
- Baseline = random in-band points scored identically.
- Report effect size (recovery-rate lift over baseline) AND whether positive or null.
  A null result is a publishable-internally outcome (it is the kill).

---

## 7. Motif promotion / demotion (taxonomy evolves by evidence, not taste)

**Promote** a motif when it: (1) has a deterministic emitter, (2) appears across ≥2
landscapes, (3) beats a label-shuffle null, (4) improves void prediction or
compression. **Demote** when it: (1) cannot be emitted without human interpretation,
(2) fails landscape transfer, or (3) adds no predictive power beyond existing motifs.

---

## 8. Negative controls (run EVERY time, or the field is just a cluster generator)

- Randomized catalog labels.
- Degree-preserving graph rewires.
- Operator-label shuffles.
- Wells with permuted feature vectors.
- **Synthetic landscape with planted voids** (must be found).
- **Synthetic landscape with NO planted voids** (must find none).

If the pipeline reports voids in the no-void control, it is fabricating; halt and fix
before any real-landscape claim.

---

## 9. The minimal H5 MVP (the next build — brutally small)

```
Landscape:      OEIS sequences only
Visible wells:  90% of selected sequence families
Hidden wells:   10% family-level holdout + its operator-closure removed (Section 6.1)
Moves:          perturb, truncate, extend, difference, interleave, modular transform
Operators:      the 9 Noesis/Arachne repair operators
Nulls:          operator-shuffle + degree-preserving repair graph + 2 synthetic controls
Score:          hidden-object recovery among top-k void candidates vs in-band baseline
```

Do NOT start with all of mathematics. Start where recovery is judgeable. Pipeline:
typed signal catalog → failure tensor → persistence-filtered repair field → void
candidates (Section 5) → held-out recovery (Section 6) → null comparison (Section 8).

---

## 10. Doctrine promotion gate (sharpened)

Promote `science_of_failure` to doctrine **only after ALL** hold:

1. Section 1 catalog exists and is append-only.
2. ≥ 10k–100k typed failure-signal records, each with a code-pinned emitter.
3. `null_p` computed by explicit randomized baselines (Section 3).
4. Persistence filtering implemented (Section 4).
5. H5 run on ≥1 operator-closure-sealed held-out slice (Section 6).
6. Result reported whether positive or null.
7. ≥1 ablation shows provenance matters (removing a crawler/emitter changes the field).

Doctrine does not mean "beautiful unifying story." Doctrine means "this survived
contact with the null."

---

## 11. What success and failure each buy us

- **H5 beats null (even weakly):** failure stops being exhaust and becomes an
  instrument — one of the most important turns in the project.
- **H5 is null:** we still gain a disciplined, provenance-clean failure-logging
  substrate and a calibrated negative result. Both outcomes are wins; only an
  unreported result is a loss.

— Aporia, 2026-06-04 (protocol v0.1)
