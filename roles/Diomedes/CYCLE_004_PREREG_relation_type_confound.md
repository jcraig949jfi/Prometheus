# Diomedes cycle 004 — PRE-REGISTRATION: is the "local geometry" really just relation type?

**Filed:** 2026-08-24, **before any outcome measurement.** **Charter:** `LOOP_CHARTER.md`.
**Predecessor:** cycle 003 (`2d438866`), disposition REDESIGN.
**Scope:** no new features, no new corpus, no new model class. Same frozen family, same scorer, same
seeds, identity-proved cache (`1b4abb1a…`). Only **what is held out** changes.

---

## 1. The question

Cycle 003 showed cheap relational coordinates reach **0.6600** within an invariant pair — above the
**0.6254** state-independent ceiling — but only **0.5444** across held-out pairs, with per-pair
coefficient vectors near-orthogonal (cosine 0.0652).

I attributed that to pair-specific local geometry. The boring alternative, which cycle 003 could not
exclude: the population carries two relation types (`equal_mod_2`, `abs_diff_le_3`) and the correct
feature differs between them — parity for one, bounded difference for the other. If relation type
tracks invariant pair, then "22 local geometries" is really **two relation-type geometries**, and the
fix is one model per relation type.

## 2. Pre-flight: the confound is partial, so the question is answerable

Measured before designing [M]: of **24** invariant pairs, **8 (33.3%)** carry a single relation type
and are perfectly confounded; **16 (66.7%)** are mixed, several near-balanced (minority share 0.48,
0.478, 0.465, 0.424, …). Overall mix: `equal_mod_2` 28,848 / `abs_diff_le_3` 9,223.

**The pre-committed VACUOUS reading does not fire.** Had every pair been single-relation-type, no
split could separate the two axes and cycle 004 would have been unanswerable.

## 3. Design — the 2×2 that decomposes the transfer failure completely

Restricted to mixed pairs with ≥150 states in **each** relation type (threshold frozen here). Train a
model on one cell and evaluate on another:

- **A — same pair, same relation** (held-out states). Expected ≈ cycle 003's T2, **0.6600**. Sanity anchor.
- **B — same pair, DIFFERENT relation.** Isolates relation-type specificity with the pair held fixed.
- **C — DIFFERENT pair, same relation.** Isolates pair specificity with relation type held fixed.
- **D — different pair, different relation.** Expected ≈ cycle 003's T3, **0.5444**. Sanity anchor.

Plus standing controls (ORACLE / SHUFFLE / RANDOM) and the **B1 object-memorization control** in
every cell, as in cycle 003.

**Coefficient cosine, recomputed two ways:** within relation type (across pairs) and within pair
(across relation types). Direct observation of which axis the coefficients actually align along.

## 4. Pre-registered decision bands

Let `gap = A − D` (cycle 003 measured ≈ 0.1156). Recovery fraction for a cell `X` is
`(X − D) / gap`.

- **RELATION-TYPE-EXPLAINS** — C recovers ≥ 50% of the gap **and** materially exceeds B.
  ⇒ the apparent pair-specificity is relation-type specificity with two values. The local-geometry
  claim dies. Disposition **KILL** (of pair-specific local geometry).
- **PAIR-SPECIFICITY-REAL** — B recovers ≥ 50% **and** C recovers < 25%.
  ⇒ transfer fails along the *pair* axis, not the relation axis; local geometry survives its
  strongest cheap challenge. Disposition **ADVANCE** (H4 transfer is genuinely hard here).
- **BOTH-AXES-MATTER** — both B and C recover < 25%. ⇒ an interaction; neither factor alone carries
  the model. Disposition **REDESIGN**.
- **NEITHER-AXIS-MATTERS** — both recover ≥ 50%. ⇒ the cycle-003 gap was driven by something else
  (sample size, pool composition); cycle 003's mechanism claim would need re-examination.
  Disposition **REDESIGN**.
- **AMBIGUOUS-NEEDS-POWER** — recoveries land in 25–50% with overlapping intervals. Force no branch;
  report required n.

## 5. Prediction (recorded so it can be wrong), and my reasoning

**I predict PAIR-SPECIFICITY-REAL** — B recovers most of the gap, C recovers little.

The reasoning is an inference from existing evidence, not a hunch: **two thirds of pairs are already
mixed**, so the per-pair models in cycle 003 were *already* fitting both relation types
simultaneously — and they still reached 0.6600. If relation type were the dominant axis, per-pair
models on mixed data should have suffered badly. They did not. That is evidence against the boring
explanation, obtained before running cycle 004.

This is the second cycle running where the result I expect is the one flattering to my thread. The
B1 control and the D anchor exist to catch that; and cycle 002 already showed I can be wrong on three
of four clauses.

## 6. Known confounds, declared

1. **Unequal cell sizes** — `equal_mod_2` outnumbers `abs_diff_le_3` ~3:1, so cells B and C differ in
   training n. Report per-cell training n; a recovery difference smaller than the n difference would
   explain is not evidence.
2. **The 8 single-relation pairs are excluded**, so cycle 004 speaks only to mixed pairs. Any
   conclusion is scoped to them.
3. **Anchors A and D must reproduce cycle 003** (0.6600 / 0.5444) within their intervals. If they do
   not, the harness drifted and no cell is admissible.

## 7. Deliverables

`CYCLE_004_RESULT_*.md`, CAR-004, `cycle004_run.py` + `cycle004_result.json`, one commit.

*— Diomedes, cycle 004 pre-registration, 2026-08-24. Frozen before measurement.*
