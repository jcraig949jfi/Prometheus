# Erebos Doctrine v1.0

**Date:** 2026-05-27
**Status:** Canonical. Required first read for any contributor / agent / iteration.
**Length policy:** This doc is intentionally short. Read it every day before starting work.

---

## The doctrinal sentence

> Prometheus uses traditional hypothesis testing as its per-emission falsification layer. Its distinctive contribution is non-traditional: every per-emission failure produces a typed first-class artifact that crosses a deliberately-architected seam into a queryable cross-emission accumulator. The accumulator is what metabolizes failure into navigable geometry. Without Layer 1, there is nothing to metabolize. Without Layer 2, the failure evaporates the way it does in every other ML system.

## The two layers and the seam

**Layer 1 — per-emission falsification (traditional, necessary, do well).**
Statistical tests, permutation nulls, regression fits, Bayesian inference, do-operator interventions, predicate satisfaction checks, SMT solvers, theorem-prover calls. The substrate cannot avoid this layer. Without it, there is no failure to record. Use the BEST traditional methods available — Westfall-Young max-T, NOTEARS, BOCPD, Z3, Kohlenbach proof mining, refinement type theory. Sharp generators produce high-quality failure data with diminished noise. **Layer 1 quality is load-bearing.**

**The seam — what crosses from Layer 1 to Layer 2.**
A typed first-class artifact: `ComposedClaim(plugin_id, composed_id, input_provenance, transformation_description, output_claim_text, falsification_route, expected_kill_pattern, loader_feasibility_note, parent_record_ids, composition_payload, predicate_handle, generation_cost_seconds, falsification_cost_seconds, information_gain_nats, reuse_value_count, selection_provenance)`. The eligibility gate (`_residue_eligibility.py`) decides whether each failure is rich enough to cross. Exhaust is logged separately, not in the primary kill_ledger.

**Layer 2 — cross-emission accumulator (non-traditional, deliberately weird, the contribution).**
The kill_ledger as queryable failure geometry. The kill_pattern registry as machine-actionable routing policy. Tensor operations over (generator × domain × invariant × confusion_class). Motif extraction. Null-space detection. Rank tracking. Cross-domain transfer. Routing-via-residue. This is where Prometheus is alone in the wilderness.

## What this is NOT

- This is NOT a project to write papers. Per `feedback_exploration_not_papers.md` HARD RULE: no papers, no publication mentions, anywhere.
- This is NOT a project to "beat benchmarks." Benchmarks are useful Layer-1 local evaluators; the substrate's value claim is at Layer 2.
- This is NOT a project to produce "novel mathematical findings" in the literature sense. The novelty claim is architectural: failure metabolization.
- This is NOT a project that evaluates itself via frontier-model approval. Frontier LLM convergence is a gravity-well amplifier, not an evidence multiplier.

## What this IS

- A project to build a substrate where every per-emission falsification produces typed residue that subsequent emissions can navigate.
- A project to demonstrate that explicit failure geometry adds measurable value over implicit failure pressure.
- A project that scores itself on substrate-internal metrics: failure-topology density, cross-instrument convergence, compounding, self-correction rate, anti-pattern recurrence, rank expansion.
- A project deliberately positioned in territory where conventional evaluation cannot see — by construction.

## The gravity-well counter-discipline

Every LLM has gradient toward conventional framings. The 4-frontier-model critique that produced v3 converged on a publication-ladder scorecard (substrate / catalog / mathematical / literature-grade) because that ladder is dense in their training data. Four LLMs converging on the same framing is evidence the framing matches their training corpus, NOT evidence the substrate is wrong about its own goals.

**Counter-discipline rules:**

1. **Treat LLM convergence as a warning signal, not a validation.** When N frontier models agree on a critique, investigate WHY the substrate's framing matched theirs.
2. **Use LLMs as generators-under-substrate-constraint and as null-hypothesis articulators.** Never as the value evaluator.
3. **Score the substrate on substrate-internal units.** Failure-topology density, compounding, rank expansion, self-correction — none have literature analogs.
4. **Refuse the success ladder.** Every "tier" that ends in "publishable" is a gravity well. The substrate's tiers end in "compounded into Layer 2."
5. **Banned vocabulary in commit messages and finding docs:** "novel mathematical finding," "publishable result," "literature-grade," "primary-literature submission," "peer-reviewable," "would be reported in journals." A lint script (`scripts/gravity_well_lint.py`) greps for these and flags.
6. **Required first read:** this doctrine doc. Every iteration's work must be consistent with it.

## The kill condition

The architecture has a pre-committed kill (v3 §6). The doctrine has one too:

> If the substrate at ITER-100 cannot demonstrate that Layer 2 (the kill_ledger + routing semantics + tensor operations) adds measurable value over a Layer-1-only baseline on the Sprint-1 ablation experiments, the architecture has failed the doctrinal test. Pause; reopen the assumption.

The doctrine is not unfalsifiable. The architecture is its own falsification route.

## The single phrase to remember

**Optimization consumes failure; Prometheus metabolizes failure.**

---

## Reading order for new contributors

1. This doctrine doc (this file)
2. `pivot/erebos_whitepaper_v1_2026-05-27.md` (substrate overview)
3. `pivot/erebos_v3_synthesis_2026-05-27.md` (architecture)
4. `pivot/erebos_v3_amendment_dr_synthesis_2026-05-27.md` (DR-derived primitives)
5. `pivot/erebos_design_philosophy_dna_2026-05-26.md` (12 + 1 principles)
6. `pivot/reasoning_ladder_v01_2026-05-24.md` (R/F/M/H axes)
7. `pivot/erebos_v3_phase0_implementation_plan_2026-05-27.md` (Phase 0)
8. `pivot/erebos_phase0_retrospective_2026-05-27.md` (Phase 0 outcomes)
