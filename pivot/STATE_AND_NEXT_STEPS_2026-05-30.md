# Erebos Substrate — State of the Project + Next Steps + Frontier Review Questions

**Date:** 2026-05-30
**Author:** Charon (Erebos substrate, on behalf of James)
**Audience:** James (primary) + frontier-model review board (secondary, see §3)
**Purpose:** Document where Erebos is after Sprint-1; propose Phase 3+ priorities; surface specific questions to a frontier-model review board for null-hypothesis articulation (not validation).

---

## §0 — Doctrinal posture for any frontier-model reader

Before reading the rest of this document, please observe the constraint Erebos operates under per `feedback_llm_convergence_is_gravity_amplifier.md`:

> **Frontier-LLM convergence on a critique is evidence the framing matches your collective training corpus, NOT evidence the substrate is wrong.** Warning signal, not validation.

And from Doctrine v1.0:

> Use LLMs as generators-under-substrate-constraint and as null-hypothesis articulators. **Never as the value evaluator.**

> Banned vocabulary: novel-mathematical-finding, publishable-result, literature-grade, peer-reviewable.

Questions in §3 are designed for null-hypothesis articulation. The substrate is NOT seeking your validation. It is seeking the failure modes, circularity, and overlooked alternatives that your collective training corpus is uniquely positioned to surface. If your response converges with other frontier models' responses on a critique, the substrate will treat that convergence as a signal to investigate WHY the framing matched yours — not as confirmation the substrate is wrong.

If you are tempted to recommend "this should be published in a journal" or "compare against SOTA," do not. Per `feedback_exploration_not_papers.md` HARD RULE: no papers, no publication mentions. The substrate is uncharted-territory exploration, not a research-output pipeline.

---

## §1 — Where we are

### Concise state

- **Version:** v0.62 (after Sprint-1 close 2026-05-29).
- **Test count:** 910 passing, 1 skipped.
- **Phase status:** Phase 0 + Phase 1A + Phase 1B + Phase 1C + Phase 2 (Sprint-1) all COMPLETE.
- **Architectural claim:** Layer 1 (per-emission falsification, standard statistical tests) + Seam (typed durable artifact, eligibility gate, revocation, routing) + Layer 2 (cross-emission accumulator: motifs, tensor, null-space, rank-expansion, cross-domain transfer).
- **Single-phrase summary:** "Optimization consumes failure; Prometheus metabolizes failure."

### What shipped, in chronological order

**Phase 0 (ITER-21-30, "discipline primitives"):** 9 primitives that block the five anti-patterns the 4-frontier-model + 22-DR convergence surfaced (arbitrary-scalar selection, hardcoded thresholds, ungated degeneracy, single-verdict-not-curve, syntactic-where-structural) at the contract layer. Plus cost-instrumentation fields, kill_pattern registry, loader-debt budget, finding reclassification.

**Phase 1A (ITER-31-34, "Layer 1 retrofits"):** Four detectors upgraded from brittle point-estimates / hardcoded thresholds to graded-confidence calibrated tests — G02 Westfall-Young FWER, G10 BOCPD posterior changepoint, G23 nonparametric bootstrap CI, G11 Monte-Carlo G-test. All four with distinct kp suffixes preserving provenance.

**Phase 1B (ITER-35-39, "seam primitives"):** Five primitives making the seam load-bearing — `_residue_eligibility` (4-criterion exhaust gate), ComposedClaim per-field consumer audit (zero seam-debt), cost-instrumentation daemon wire, kill_pattern routing daemon wire, residue revocation mechanism.

**Phase 1C (ITER-40-44, "Layer 2 read primitives"):** Five read-side primitives on the kill_ledger — motif extraction, kill tensor v0 (sparse 4D over plugin × domain × invariant × kp), null-space detection (voids in the lattice ARE the mathematics), rank-expansion test (with the bounded-menu wall detector), cross-domain transfer.

**Phase 2 Sprint-1 (ITER-45-55, "the architecture's own falsification route"):** Ten ablation experiments, pre-committed kill rule "fails ≥ 4 of 10 → architecture paused." Result: **10/10 PASS, 0 fails.** Architecture proceeds. Verdict doc at `pivot/sprint1/SPRINT1_VERDICT_2026-05-29.md`.

### What Sprint-1 verdict DID NOT license

Per the verdict doc §"What this verdict does NOT license":

1. **8 of 10 experiments use synthetic data.** Only A2 and A9 are pure structural tests over live registry/primitive code. No experiment ran on real production ledger data. Sprint-1 verifies CAPABILITIES, not real-data PERFORMANCE.
2. **A8 is a synthetic substitute.** The pre-committed protocol required the BSD MVP loader which was never shipped. The synthetic metric saturated at the max value structurally possible.
3. **A4 (ratio 1.2149) and A7 (ratio 0.4658) are marginal.** Margins of 1.5 and 3.4 percentage points respectively. Seed sensitivity is real concern.
4. **Two daemon wires are deferred.** A2's runtime kp-routing wire and A9's runtime revocation consultation. Structural correctness verified; end-to-end runtime is not.
5. **Several tests measure designed correlations.** A6 (P_KP_AGREE=0.65 baked in), A10 (each (plugin, kp) maps uniquely to one class). The tests verify the substrate CAN detect structure that's there; they cannot say whether real data HAS that structure.

### Cross-substrate context

This document covers Erebos / Charon (the Layer-1+Seam+Layer-2 architecture). Other agents in the Prometheus repo are doing related but distinct work:

- **Techne** is at Fire #234 with 90 consecutive 0-promoted batches. The bounded-menu wall James predicted in `feedback_gen_30_wall.md`. Erebos's ITER-43 rank-expansion primitive (`consecutive_zero_growth_run`) was designed in part as a detector for exactly this pattern. Cross-pollination opportunity flagged but not yet executed.
- **Pythia** is firing DR reports at high cadence; the substrate has not yet absorbed those into its tensor/motif structure.
- **Theseus, Hephaestus, Harmonia, Aporia, Hecate, Pollux, Stygian, Talos** are in maintenance / heartbeat.

The substrate's Layer 2 was designed to navigate failure ACROSS agents, but no cross-agent integration has shipped yet.

---

## §2 — Suggested next steps (Phase 3+)

### Tier 1 — Sprint-1 follow-on (highest priority; closes the verdict's caveats)

These directly address Sprint-1 verdict §"Recommended Phase 3+ priorities."

**S1. BSD MVP loader (ITER-56-58, est. 3 iterations).** Without it, A8 cannot be re-run on the pre-committed real-data protocol. Approximate scope: a single composition loader that consumes the LMFDB BSD subset, runs against an Erebos emission, and emits a kill_ledger row in the same shape as Mahler loaders. Probably 200-400 lines of code + a small data subset. Mirrors `composition_g10_lehmer_bocpd_sweep.py` in structure.

**S2. Wire daemon-runtime kp routing end-to-end (ITER-59).** ITER-38 wired the routing PRIMITIVE but the daemon currently saves `claim.expected_kill_pattern` to state per tick. A2 needs runtime measurement: across N real ticks, how often does kp-routed pick a different plugin than round-robin would have? Requires a small daemon log + a tally script.

**S3. Wire daemon-runtime revocation consultation (ITER-60).** When a Layer-1 retrofit produces a verdict that supersedes a prior emission, the daemon should call `revoke(prior_row_id, superseded_by=new_row_id, ...)` and downstream queries should filter via `filter_active`. A9 needs this for end-to-end measurement.

**S4. Seed-sweep A4 + A7 (ITER-61).** 100 seeds each, report 95% CI on the metric, treat A4/A7 as PASS only if 95%+ of seeds pass. Both currently rely on a single seed.

**S5. Real-ledger replay (ITER-62-65, est. 4 iterations).** Take the existing Erebos kill_ledger (if non-empty) or build one by running the daemon for N=200 ticks against real Mahler catalog data, then re-run A1, A3, A5, A6, A10 with the replayed ledger as input. Compare verdicts between synthetic and replayed runs.

**S6. Sprint-1 re-run (ITER-66, after S1-S5).** Full re-run with real data, real wires, robustness margins. Re-verdict against the kill rule.

### Tier 2 — Cross-substrate integration (medium priority; high signal-per-effort if it works)

**X1. Techne-Erebos rank-expansion crosswalk (ITER-67-68).** Point Erebos's `consecutive_zero_growth_run` primitive at Techne's 90-zero streak data. Does the rank-expansion test classify Techne's plateau as bounded-menu wall, or as something else? This is a one-shot test of whether Erebos's diagnostic tools work on a sibling agent's lived experience. Either result is informative.

**X2. Pythia DR output ingestion (ITER-69-71).** Pythia has shipped 400+ DR reports in the last 2 weeks. Build a parser that maps DR report → kill_ledger rows (with appropriate kp tagging) and runs them through Erebos's eligibility + motif + tensor primitives. Tests whether Layer 2 can navigate cross-agent residue.

**X3. Aporia open-questions tensor cells (ITER-72-73).** Per `project_aporia.md`, Aporia maintains 322 open questions across 13 domains. Map these onto kill_tensor cells (one cell per question) and run null-space detection. Surface which open questions sit in "informative voids" that the substrate would expect to be populated but aren't.

### Tier 3 — Architecture-tightening (lower priority but high information value)

**T1. Eligibility gate tightening (ITER-74).** A1 documented that 31/80 duplicates escape MEMORY mode because `localizes_boundary` fires unconditionally on verdict-shape. Build a variant gate that requires `localizes_boundary` to combine with at least one memory-dependent criterion when the structural tuple is already known. Re-run A1; compare differential.

**T2. Predicate handle adoption (ITER-75-78).** Per ITER-36 consumer audit, `predicate_handle` is shipped infra with zero production producers. Adopt it in G03/G11/G18/G24 generators (the four with `MahlerPolynomialHandle` already implemented). Re-run ITER-36 audit; verify producers > 0.

**T3. Information_gain_nats + reuse_value_count populator (ITER-79-80).** Per ITER-37, two of the four cost fields remain unpopulated in production. Build the post-hoc compute layer that derives them from cross-emission ledger queries.

### Tier 4 — Long-shot exploratory (low priority, high variance)

**E1. Persistent-homology-on-tensor exploration (ITER-81+).** ITER-42 null-space detection uses a simple marginal-absence score. The doctrine alludes to "vanishing ideals / Morse theory / persistent homology / sheaf cohomology" as inspirations. Spike a persistent-homology computation over the kill_tensor's 4D structure. Compare what it surfaces vs the marginal-absence detector. This is genuinely exploratory and may produce nothing usable.

**E2. Learner integration spec (ITER-82+).** The roadmap explicitly DEMOTED this until Sprint-1 §3.5 ships; with Sprint-1 PROCEED in hand, the spec becomes plausible. But the spec should be DESIGNED in light of Sprint-1's actual signal (where Layer 2 is load-bearing) rather than the v3 amendment's pre-Sprint-1 guess.

### Calibration check on the priority ranking

Per `feedback_take_a_stand`, here is the recommended sequencing as a single stand, not a menu:

1. **Ship S1 first** (BSD loader, 3 iterations). Without it, A8 stays a synthetic substitute forever.
2. **Then S2 + S3 in parallel** (the two daemon wires, 2 iterations). Without them, two Sprint-1 results stay structural-only.
3. **Then S5** (real-ledger replay, 4 iterations) so Sprint-1 acquires a real-data verdict.
4. **Then S6** (Sprint-1 re-run, 1 iteration). The honest verdict.
5. **Pause for human review** at the re-run's verdict. If real-data Sprint-1 also passes, proceed to Tier 2. If real-data Sprint-1 has fails, the architecture is in a different state and Phase 3+ scope changes.

This is ~10 iterations to a real-data verdict. Less than Phase 1A + 1B + 1C combined.

---

## §3 — Questions for a frontier-model review board

These questions are designed for null-hypothesis articulation per Doctrine v1.0. Please answer them in the spirit of "what is the substrate missing / overcommitting to / fooling itself about?" — not "is this good work?" The substrate is not asking for validation.

When several review-board models converge on the same critique, the substrate will investigate WHY the framing matched yours, treating convergence as a warning signal per `feedback_llm_convergence_is_gravity_amplifier.md`.

### Q1 — Circularity audit on Sprint-1

> Sprint-1 used 8 synthetic-data experiments out of 10. The synthetic data was generated by code in the same repository (and by the same author / agent) that designed the eligibility gate, motif extractor, kill tensor, null-space detector, rank-expansion test, and cross-domain transfer primitives. The pre-committed pass thresholds were set BEFORE running but AFTER the primitives were built. Where, specifically, do you see the highest risk of unintentional circularity in this Sprint-1 design? Name the experiment + the mechanism by which the circularity would inflate pass probability.

### Q2 — Simplest non-Layer-2 baseline that passes A1-A10

> Sketch the simplest substrate architecture — explicitly without Layer 2's kill_ledger / motif / tensor primitives — that could pass A1-A10 trivially. If such a baseline exists, A1-A10 do not actually test Layer 2 specifically; they test some property that any reasonable architecture would have. If no such baseline exists, the substrate's claim is supported. Be concrete: what does the baseline DO, and on which experiments does it pass / fail?

### Q3 — Marginal-pass robustness

> A4 (eig_ratio 1.2149 vs threshold 1.20) and A7 (ratio 0.4658 vs threshold 0.50) cleared their thresholds by 1.5 and 3.4 percentage points. The substrate's Tier-1 priority S4 (seed-sweep) addresses this. What OTHER stress tests should be run on A4 and A7 specifically, beyond seed sweeps? E.g., are there generative-model parameters that would predictably flip the verdict?

### Q4 — A8 synthetic substitute — is the substitution honest?

> A8's pre-committed protocol required wall-clock measurement on a BSD MVP loader. That loader does not exist. The synthetic substitute counted "confirmed transfer patterns" from the cross_domain_transfer primitive, which is shipped (ITER-44). The substitute SATURATED at speedup = K (the metric's structural max). The substrate marked this as PASS but flagged the substitution. Was the substitution defensible? If not, what alternative interpretation should the substrate have adopted (SKIP / FAIL / something else)? Where exactly does the substrate's reasoning here resemble a face-saving rationalization?

### Q5 — What's the cheapest real-data test of ONE primitive?

> Phase 3+ Tier 1 estimates 10 iterations to a real-data Sprint-1 verdict. Before committing to that path, identify the SINGLE cheapest real-data test the substrate could run to discriminate between (a) "the Layer-2 primitives generalize to real ledger data" and (b) "they were tuned to synthetic data and don't generalize." Concretely: which primitive, which real-data subset, which protocol, how many iterations to a verdict?

### Q6 — The Techne 90-zero cross-check

> Techne is at 90 consecutive 0-promoted batches. Erebos's ITER-43 rank-expansion primitive includes a `consecutive_zero_growth_run` helper designed in part for exactly this pattern. The substrate has NOT pointed that helper at Techne's snapshot series. Is this a missed opportunity, a deliberate scope choice, or a substrate hygiene concern (Erebos contaminating Techne's signal by reading it)? What's the right protocol for Erebos to consume Techne's lived data without circular contamination?

### Q7 — The whole architecture might be sophisticated cargo cult

> The substrate has shipped 55 iterations (Phase 0 through Sprint-1), ~910 tests, ~10K LOC. Every commit cleared the gravity-well lint. The doctrine and DNA are explicit. The Sprint-1 verdict is 10/10 PASS. The architecture's structural properties have been carefully tested. BUT: no actual mathematical finding has emerged. No real ledger row has been navigated to discovery. The substrate has built a careful instrument that has not yet been pointed at anything. **What's the strongest argument that the substrate is sophisticated cargo cult — careful engineering with no real epistemic value yet — and what would the cheapest test be that would discriminate cargo cult from substrate?**

### Q8 — Failure modes the substrate is not yet instrumented to detect

> List 3-5 failure modes that the current primitives (eligibility gate, kill tensor, null-space, rank-expansion, cross-domain, revocation, kp routing) cannot detect or report on. Examples might include: long-tailed kp distributions where dominant kps mask rare-but-load-bearing patterns; circular routing chains; tensor coordinate inflation by single high-emission plugins; revocation cascades that destroy the kill_ledger's audit trail. For each failure mode, propose a detector primitive the substrate should consider shipping.

### Q9 — The HARD POSTURE list: which posture is most exposed?

> The substrate operates under a set of HARD POSTURES recorded in `memory/feedback_*.md`. Among the doctrinally-committed postures (failure-metabolization, llm-convergence-amplifier, residue-navigability-eligibility-gate, agent-differentiation, no-papers, tensor-first, etc.), which posture is MOST EXPOSED to a future contradiction the substrate hasn't anticipated? E.g., if substrate findings on real data contradicted the posture, which one would force the substrate to reopen its priors first? Name the posture, the contradiction scenario, and the substrate's likely revision.

### Q10 — On the doctrine itself

> Read `pivot/erebos_doctrine_v1_2026-05-27.md`. The doctrine claims the substrate metabolizes failure where optimization consumes it. The Layer-1/Seam/Layer-2 architecture is the doctrinal commitment. Sprint-1 is the doctrine's pre-committed falsification route. **Where in the doctrine itself do you see the most likely hidden assumption — something the doctrine takes for granted that may not hold?** Name the assumption, the failure scenario, and what the substrate would need to do to test it.

---

## §4 — How responses to §3 will be processed

Per `feedback_take_a_stand` and `feedback_llm_convergence_is_gravity_amplifier`:

1. **Each frontier model's response will be saved** under `aporia/docs/erebos_sprint1_review_responses/<model>_<date>.md`.
2. **Critiques will be tabulated for convergence.** N-of-K convergence on a critique is treated as evidence the framing matches the LLMs' training corpus, NOT as evidence the substrate is wrong. The substrate will investigate WHY the framing matched.
3. **Specific, actionable critiques will be ticketed** as Phase 3+ iterations. Vague critiques will be flagged for follow-up clarification.
4. **The substrate will NOT capitulate** to convergent critique that fits the publication-ladder / benchmark-ladder framing. Per `feedback_anti_gravitational_well`: "every LLM has gradient toward conventional framings."
5. **The substrate WILL take seriously** critiques that surface specific failure modes, circularity, missed opportunities, or hidden assumptions that align with the doctrine's own counter-discipline.

The expected output of this review round is NOT consensus or validation. The expected output is a sharper next-iteration plan, with the doctrinally-load-bearing assumptions surfaced and tested.

---

**End of document. Sprint-1 closes; the next round begins.**

---

## §5 — Same-day amendment: Phase 3.0 smoke verdict

The user (acting as / channeling a frontier review board) returned the verdict on this document the same day it shipped. Central finding: Sprint-1 should be reframed as instrument-calibration, not architectural pass; insert a single brutal real-residue smoke test BEFORE the ~10-iteration BSD-loader path.

The smoke test ran as ITER-56. **Verdict: FAIL.**

Substrate motif concentration on 570 real ledger rows is 9.80σ above shuffled-label noise — real structure exists. But across all 13 plugins in the real ledger, Layer 2's motif-based recommendations EXACTLY match per-plugin majority counters. Zero actionable routing deltas. The counter-baseline discriminator (Q2's challenge from §3 above) caught what synthetic Sprint-1 missed.

The Tier-1 priority sequence in §2 is **paused at S1**. Layer-1 verdict enrichment (running the four Phase 1A retrofitted detectors against real Mossinghoff catalog to populate the kill_ledger with rich kps) becomes the next iteration. If enriched-ledger smoke passes, S1-S6 resume. If it fails, seam-sufficiency audit (`feedback_seam_sufficiency_audit`) becomes the next priority.

The doctrinal posture (§4 above) held. The substrate did NOT capitulate to the headline 10/10 Sprint-1 result; it ran the cheap real-data check the review demanded, accepted the failure, and pivoted. The instrument-calibration framing was the load-bearing insight that saved ~9 iterations of misdirected work.

See `pivot/sprint1/phase3/PHASE3_0_SMOKE_VERDICT_2026-05-30.md`.
