# Diomedes cycle 002 — PRE-REGISTRATION: are the missing 0.3746 reachable with stupid relational coordinates?

**Filed:** 2026-08-24, **before any outcome measurement.**
**Authorized:** James, this session — *"Don't build a rich representation yet. There is a cheaper
test."*
**Scope boundary, hard:** no neural net, no embeddings, no RL, no successor representation, no new
corpus, no new architecture, no 346 GB campaign. A frozen family of ≤30 hand-written arithmetic
features and the same logistic scorer cycle 001 used.
**Predecessor:** `CYCLE_001_RESULT_h1_counterfactual_hunt.md` (verdict REDESIGN-COORDINATES) and its
AMENDMENT.

---

## 1. The question

Cycle 001 established the decomposition: chance 0.500 → **state-independent information ceiling
0.6254** → state-specific oracle 1.000. Candidate-only features reach ~0.56. Parent-only features
reach exactly 0.500 **by type error** — `f(Z(x))` scores every candidate identically and cannot
express `a_3 > a_7`.

The conditional signal is **0.3746, i.e. 74.92% of the total available.** Cycle 002 asks the cheapest
possible question about it:

> **Is the missing conditional signal reachable with embarrassingly obvious relational coordinates
> `φ(x, a)` — differences, parities, magnitudes, rank deltas — or does it require something learned?**

The quantity, in the corrected conditional form: **`I(A*; Z_a | Z_x)`**.

## 2. What counts as legitimately available

A feature is admissible iff it can be computed **without evaluating the tested invariant of the
candidate**. Reading that value *is* the oracle; an arm that reads it scores 1.000 and has performed
the search it was meant to save.

Admissible: the candidate's **other** invariants in the same catalog, the parent's values, the
relation and its threshold, catalog rank positions, and the cycle-001 corpus-history features.

**Economic caveat, stated so it is not later discovered as a flaw.** In h1 all invariants cost the
same catalog lookup, so this experiment carries **no economic claim** — h1 is an instrument
validation environment, not a demonstration that navigation saves work. The eventual quantity is
`C_enumerate` vs `C_rank + C_evaluate(top-m)`, or *oracle evaluations avoided per useful move lost*.
Out of scope for cycle 002 and pre-registered as out of scope.

## 3. The frozen feature family

Companion invariants `J` = up to **3** invariants of the varied side's catalog, excluding the tested
one, selected by largest value-table coverage (deterministic rule, no tuning).

For each `j ∈ J`, with `u = value_j(candidate)`, `p = value_j(parent object on the varied side)`,
`t = the value on the fixed side`:

1. `delta_j = u − p` — how far the candidate moved along axis `j`
2. `absdelta_j = |u − p|`
3. `parity_match_j = 1[(u − t) mod 2 = 0]`
4. `absdiff_target_j = |u − t|`
5. `absdiff_le3_j = 1[|u − t| ≤ 3]`
6. `rank_delta_j = quantile_rank(u) − quantile_rank(p)`

**18 relational features.** Plus the four cycle-001 candidate-only carryovers (`B1_break_rate`,
`B2_freq`, `n_cells`, `n_rels`) = **22 total.** Frozen here; no additions after seeing results.

Features 3 and 5 deliberately mirror the two relation predicates under test (`equal_mod_2`,
`abs_diff_le_3`) but applied to a **different invariant** than the one being tested. That is the
whole hypothesis in one line: does a relational fact about a cheap axis predict the same relational
fact on the expensive axis?

## 4. Arms

- **ORACLE** — positive control, must be 1.0000 or nothing else is admissible.
- **SHUFFLE** — cheat control, must fall to 0.500.
- **RANDOM** — the floor.
- **CYCLE1_B1** — candidate break-rate alone; the cycle-001 reference at ~0.556.
- **PHI_REL** — logistic on the 18 relational features only. **The primary arm.**
- **PHI_ALL** — logistic on all 22.
- **Per-feature individual AUCs** — reported for every one of the 22, required by §6.

Split: held-out **invariant pair**, the same T3-grade split as cycle 001. 5 seeds. Primary metric
per-state AUC, chance exactly 0.500, SE reported, gates use `mean ∓ 3·SE`.

## 5. Pre-registered decision bands

Adopted from James's three outcomes, made SE-aware, **plus a fourth for the middle** — cycle 001
taught that a pre-registration which does not cover its own middle forces a verdict.

- **NOT-IN-SIMPLE-RELATIONAL** — `PHI mean + 3·SE ≤ 0.6254`. State dependence exists but is not in
  obvious local coordinates. Learned transition representations become defensible *for the first
  time*, having been shown necessary rather than assumed.
- **AMBIGUOUS-NEEDS-POWER** — the 3·SE interval straddles 0.6254. Report as ambiguous; do **not**
  force a branch; state the n required to resolve it.
- **ELEMENTARY-COORDINATE-DEFECT** — `PHI mean − 3·SE > 0.6254`. Prometheus stored `Z(x)` and `Z(a)`
  when it needed `Z(x, a)`. The year-long coordinate problem is elementary.
- **STOP-AND-UNDERSTAND** — `PHI mean − 3·SE > 0.90`. Halt and diagnose before building anything.

## 6. The functional-dependency guard (mandatory, and the likeliest way to be fooled)

If a companion invariant is mathematically determined by — or strongly determines — the tested
invariant in that catalog, a feature can approach 1.000 and **that is a fact about the catalog, not
navigation**. Knot determinants are always odd; such structure is exactly what would counterfeit a
spectacular result.

**Pre-registered rule:** if any *single* feature reaches AUC ≥ 0.90 alone, the verdict is
**CATALOG-DEPENDENCY**, not a navigation finding, and the result is reported as a discovered
functional relationship between invariants. A STOP-AND-UNDERSTAND reading requires that no single
feature clears 0.90 while the ensemble does — genuine relational composition, not one lucky axis.

Additionally report, per companion invariant, whether its values are constant-parity or otherwise
degenerate, so a null from a dead axis is not read as a null from the method.

## 7. Secondary deliverable — the `divides` robustness population

Per cycle 001 AMENDMENT A3: re-run the frozen cycle-001 analysis on `divides` states **separately**,
labelled **"results under a 99.15%-agreement oracle."** Never merged with the clean population.
Qualitative ordering surviving is reassuring; changing is a finding to investigate.

## 8. What I expect (recorded so it can be wrong)

`PHI_REL` lands **0.60–0.70** — above the cycle-001 arms, at or slightly above the state-independent
ceiling, most likely reading **AMBIGUOUS-NEEDS-POWER or a weak ELEMENTARY-COORDINATE-DEFECT.** I
expect `parity_match_j` to be the strongest single feature on `equal_mod_2` states and
`absdiff_target_j` on `abs_diff_le_3` states. I do **not** expect to approach 1.000, and if anything
does I expect §6 to catch it as a catalog dependency rather than navigation.

## 9. Deliverables

`CYCLE_002_RESULT_*.md`, CAR-002, `cycle002_run.py` + `cycle002_result.json`, and the `divides`
robustness rows — all in one commit with the runner.

*— Diomedes, cycle 002 pre-registration, 2026-08-24. Frozen before measurement.*
