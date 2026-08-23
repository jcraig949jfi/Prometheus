# Preregistration — O1: type-directed enumeration vs evolution

> **Author:** Apollo (M2) · **Written:** 2026-08-23, BEFORE the enumerator was run
> **Stop rule ratified by:** James, 2026-08-23 ("Go"), on the recommendation of two
> independent frontier reviews (Gemini, ChatGPT) which both ranked this experiment first
> and pre-committed to its consequence.
> **Cost:** CPU only, deterministic, no API.

---

## The question

Apollo's operators are strictly typed: each declares `reads` and `writes` over named
blackboard slots. **Nobody has ever enumerated the type-correct pipelines.** If exhaustive
enumeration finds the organisms four months of evolution found, substantially cheaper, then
the evolutionary search was decorative — the 2026-05-22 single-primitive falsification
repeated one level up, at the level of the *search* rather than the *organism*.

## Method

State = the set of slots written so far, seeded with `{problem_text, candidates}`. An
operator is **applicable** iff every slot it reads is already written (inputs excepted).
Breadth-first over applicable transformer sequences; at each reachable state, close with
every applicable scorer (and, for dispatch shapes, with sets of guarded scorers).

Two prunes, both principled rather than convenient:
- an operator must write **at least one slot not already written** — this is the
  minimisation the review demanded, and it makes padding unrepresentable by construction;
- no operator repeats within a pipeline.

Enumeration proceeds by depth k = 1, 2, 3, … and records the cumulative count of
**organism-evaluations** (one organism scored on the 120-task battery) at each depth.

## The comparator — evaluations, not wall time

Evolution's cost to reach its ceiling is known and fixed: population 24 × 131 generations
= **3,144 organism-evaluations** to first reach `max_acc = 0.833`. Wall time is reported
but is not the metric; evaluations are the currency both methods spend.

## Pre-committed decision rule

| enumeration result | verdict |
|---|---|
| reaches `max_acc ≥ 0.833` in **< 3,144** evaluations | **EVOLUTION IS DECORATIVE.** Apollo retires as a capability-climber and becomes an instrument (option O7). No post-hoc rescue, no "but evolution would scale better," no re-running with different settings to find a kinder number. |
| reaches ≥ 0.833 but needs **more** evaluations than evolution | evolution has a real efficiency advantage. Apollo survives O1 and proceeds to a bounded O2 test. |
| **cannot reach** 0.833 at any tractable depth (combinatorial explosion first) | evolution has a real reachability advantage — the strongest possible outcome for Apollo. |

**Secondary, reported regardless:** does enumeration find organisms evolution *never*
found (completeness)? A higher ceiling found by brute force is itself a finding about the
substrate, independent of the verdict above.

## What would make this experiment invalid

- If the enumerator's applicability rule is *stricter* than the substrate's real execution
  semantics, it would under-explore and hand Apollo an unearned win. Guarded scorers skip
  when their precondition fails, so a pipeline can be executable even when a guard's slot
  is unwritten. **Mitigation:** every enumerated pipeline is scored by the substrate's own
  `_evaluate_acc` on the real battery — no simulated scoring — and the enumerator's reach
  is reported against the known 0.833 organism as a positive control. If enumeration cannot
  even *represent* the known solver, the enumerator is broken, not the hypothesis.
- Enumeration order is deterministic, so "evaluations to first solution" depends on the
  order slots and operators happen to be listed. Reported with that caveat; the verdict
  uses a ≥2× margin rather than a hairline comparison.

## Positive control (mandatory, per the standing two-control rule)

The known 0.833 organism's minimised core must appear in the enumerated space. If it does
not, the run is `ENUMERATOR_BROKEN` and reports nothing about evolution.
