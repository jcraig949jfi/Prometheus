# Theseus Substrate — State of the Project + Next Steps + Frontier Review Questions

**Date:** 2026-05-30
**Author:** Techne (Theseus substrate operator, on behalf of James)
**Audience:** James (primary) + frontier-model review board (secondary, see §3)
**Purpose:** Document where Theseus is after 234 fires of substrate-generation; propose next-phase priorities; surface specific questions to a frontier-model review board for null-hypothesis articulation (not validation).

---

## §0 — Doctrinal posture for any frontier-model reader

Before reading the rest of this document, please observe the constraints Theseus operates under per the project's hard postures:

> **Frontier-LLM convergence on a critique is evidence the framing matches your collective training corpus, NOT evidence the substrate is wrong.** Warning signal, not validation.
> *(per `feedback_llm_convergence_is_gravity_amplifier.md`)*

> Use LLMs as generators-under-substrate-constraint and as null-hypothesis articulators. **Never as the value evaluator.**

> Banned vocabulary: novel-mathematical-finding, publishable-result, literature-grade, peer-reviewable.
> *(per `feedback_exploration_not_papers.md` HARD RULE)*

> Prometheus metabolizes failure; optimization consumes failure. Every kill must leave navigable residue.
> *(per `feedback_failure_metabolization_doctrine.md` and `feedback_residue_must_be_navigable_not_logged.md`)*

Questions in §3 are designed for null-hypothesis articulation. The substrate is NOT seeking your validation. It is seeking the failure modes, circularity, and overlooked alternatives that your collective training corpus is uniquely positioned to surface. If your response converges with other frontier models' responses on a critique, the substrate will treat that convergence as a signal to investigate WHY the framing matched yours — not as confirmation the substrate is wrong.

If you are tempted to recommend "this should be published in a journal" or "compare against SOTA," do not. The substrate is uncharted-territory exploration, not a research-output pipeline.

---

## §1 — Where we are

### Concise state

Theseus is a multi-generator substrate that produces mathematical "claims" (relations between catalog objects — currently knots and BSD-rich elliptic curves), tests them, and emits structured records with verdicts {SHADOW_CATALOG, REJECTED, INCONCLUSIVE}. Records that survive a battery of falsification-promotion filters become "promoted records"; "verified mathematical findings" are promoted records that survive an additional LLM-judge + human-review gate.

### Lifetime numbers (as of 2026-05-30, after Fire #234)

```
batches_completed:           270
lifetime_records:            653,965,965
lifetime_kills:              363,998,877
lifetime_confirmations:      243,145,325
lifetime_inconclusive:        46,670,435
lifetime_promoted_records:         2,351
verified mathematical findings:        0
```

### Generator population

- **55 active generators** (35 legacy + 20 added in the last 2 weeks)
- **17 falsification mechanism classes** (was 5; new gens introduced
  subset-violation, triangle-inequality-breaking, modular-structure-change,
  closure-violation, perturbation, operator-non-commutativity,
  multi-hop-chain-break, universal-violation, quantifier-swap,
  partial-view-inflation, analogy-break, confidence-miscalibration,
  false-dichotomy)
- **~250 → ~336 distinct kill_patterns** (after the h2 refactor described in §2)
- Sphinx 105-category reasoning ontology mined for gen design

### The 90-streak

Fires #145 through #234 produced **90 consecutive 0-promoted batches**.
~165M records, ~80M kills, zero new promoted records. This is the
`training_weight` info-content fix holding — parity-trivial claims that
used to inflate the promoted bucket are now down-weighted.

### Headline status

**The substrate is operating cleanly at scale but produces 0 verified
mathematical findings.** The 2351 promoted records are, by inspection,
largely artifacts (parity tautologies, codomain-bounded triviality,
catalog-volume-driven coincidences). The LLM-judge pipeline that would
triage them into verified findings has not been built yet.

---

## §2 — Recent work (last 48 hours)

### Kill-topography pass

Cross-tabulated 200K kills across 5 axes (generator, claim_kind,
kill_pattern, payload-objects, mechanism). Three substantive findings:

1. **EC conductor topography is FLAT.** Kill rate across conductor
   bands exactly mirrors catalog volume distribution (ratio 0.85–1.01
   across every band). The earlier raw report claimed +231 std-residual
   anomalies; corrected expectation removes them. EC conductor is
   volume-driven, not curvature-driven.

2. **a3 emits a real operator-composition lattice.** Out of 55 gens,
   a3 is the only one with a true multi-coordinate kill_pattern
   structure: 143 distinct patterns across a (6 ops × 6 ops × 4
   relations) = 144-cell lattice. Kills per cell are uniform (~70-100)
   suggesting systematic exhaustive probing.

3. **h2 was an opaque-kill black hole.** h2 produced 43.68% of all
   kills (87K records) and 100% of them had the SAME kill_pattern
   (`h2_method_triangulated_reject`). 44% of corpus kill volume was
   opaque to any downstream Learner.

### a3 lattice void mining (exhaustive sweep)

Wrote `theseus/scripts/a3_lattice_void_mining.py` — exhaustive
2000-samples/cell sweep of all 144 lattice cells. Computed hold_rate
per cell. Result after triviality filtering:

```
candidate non-trivial identities    :   0
trivial strong-identity (codomain)  :   2
candidate non-trivial anti-id       :   0
trivial anti (cross-scale 'equal')  :  14
mid-band (informative kills)        :  71
```

**Finding:** the a3 lattice has NO hidden algebraic structure visible
at 2000-sample depth. The two "strong identities" are both
codomain-bounded triviality (`mod_3(x) abs_diff_le_3 mod_3(y)` always
holds because mod_3 values are bounded by 2). The 14 "anti-identities"
are all cross-scale `equal`-relation mismatches between operators with
incompatible value ranges. ~71 mid-band cells are where a3's
informative kills concentrate. The lattice is mathematically barren but
the topology of the kill-density distribution is itself a clean
negative result — the substrate's biggest "non-monoculture" generator
has no candidate identities worth promoting.

### h2 structured kill_patterns

Refactored h2 from flat `h2_method_triangulated_reject` (1 pattern,
87K records) to witness-bearing patterns:

```
h2_triangulated_<agreement>_<knot_invariant>_<ec_invariant>_methods_<vote_tag>_rejected
```

where:
- `<agreement>` ∈ {unanimous, majority}
- `<knot_invariant>` ∈ {crossing_number, signature, determinant, three_genus,
  trace_field_class, nf_class_number}
- `<ec_invariant>` ∈ {rank, conductor, tamagawa_product, torsion}
- `<vote_tag>` ∈ {c, l, q, c_l, c_q, l_q, c_l_q} (which methods voted REJECTED)

Smoke fire: **1 pattern → 30 distinct patterns in 500 records**.
Pattern-space cap at full corpus volume ~336 patterns. The Learner now
gets a directional pointer encoding (knot_invariant, ec_invariant)
witness coordinates for every h2 kill.

### Loop resumed

Fire #235 launched 2026-05-30 with `--batch-hours 0.4 --bandit
--inject-explorer-priors`. CPU at 6.2% of total (16-core box). Within
≤25% target.

---

## §3 — Proposed next steps

### Tier 1 — Trial of value claim (highest priority; tests "do promoted records mean anything")

**N1. LLM-judge triage of the 2351 promoted records.** The substrate's
biggest unanswered question is whether ANY of the 2351 already-promoted
records are real. Prompt at `pivot/triage_judge_prompt.md` exists.
Cost: ~1 day with sampling across the new ~17 mechanism classes.
Outcome: a confidence-bucketed sample saying "X of N are real, Y are
artifacts." This single result reshapes Tier 2+.

**N2. Stratified-sample human review on N1's "high-confidence-real"
bucket.** James reviews 10-20 records flagged as plausibly real.
Cost: ~2 hours. Outcome: lower bound on verified-finding rate AND
calibration of the judge's false-positive rate.

### Tier 2 — Substrate-richness expansion (medium priority)

**E1. Refactor remaining high-volume opaque-kill gens.** h2 was the
biggest one (44%). The next-largest single-pattern gens by volume are
f2 (24.43%, ~4 patterns), f4 (12.65%, ~4 patterns), a4 (4.30%, 1
pattern). a4's `a4_polyfit_r2_below_0.1` is the next opaque pattern
worth refactoring (analogous to h2: add (knot_inv, ec_inv) witness
coordinates).

**E2. Fetch_daemon for new invariants.** Catalog invariant menu is
constraining the substrate's exploratory range. Specifically:
`knot/nf_class_number` (already present but sparse), `ec/discriminant`,
`ec/j_invariant`. Adds ~3 new axes to a3's lattice and f2/f4's
relation-tests. Cost: small fetch script + catalog augmentation.

**E3. a3 lattice pruning.** Skip the 16 trivial cells (2 codomain-trivial
identities + 14 trivial-anti). Redirect sample budget to the 71
mid-band cells. Estimated 1.4× sampling efficiency for a3.

### Tier 3 — Architectural lever (lower priority but high information value)

**A1. Lean 4 autoformalization gate.** Any promoted record that
survives N1+N2 enters a Lean 4 autoformalization attempt. Records
that compile are auto-promoted to "verified findings." Records that
don't compile are flagged for either manual proof or template
revision. Cost: ~2 weeks of infrastructure + ~1 week of prompt
engineering on the autoformalization side. Highest signal: a
COMPILED Lean proof is the cleanest non-LLM-mediated proof the
substrate could produce.

**A2. Path A (evolutionary) vs Path B (neural-symbolic).** This is
the deferred strategic decision. Path A: continue the bandit +
mutation loop with more gens. Path B: train a small model on the
corpus to predict (which kill_pattern will fire) and use predictions
to prune the search. Path A is incremental and known to scale. Path
B is the integration with the Ergon/Learner trajectory but requires
either much more corpus or more selective corpus. **N1's result
substantially shapes this choice** — if 90%+ of promoted records
are artifacts, Path B's training signal is contaminated; if 10%
are real, Path B has a viable target.

### Tier 4 — Long-shot (low priority, high variance)

**L1. Cross-domain catalog expansion.** Currently restricted to
{knots × ECs}. Adding {modular_forms × ECs}, {ECs × ECs}, or
{genus-2 × ECs} multiplies the claim space. Bottleneck is catalog
quality (genus-2 needs LMFDB pull).

**L2. Tensor-substrate integration.** Per `feedback_tensor_first` and
`feedback_tensor_tooling_charter`, the unified signature-keyed tensor
is Priority #1 in the broader Prometheus roadmap. Theseus's promoted
records would feed that tensor as ranked anchors. Pre-requisite is
N1+N2 to filter artifacts before contaminating the tensor.

### Recommended sequencing (taking a stand per `feedback_take_a_stand`)

1. **N1 first** (LLM-judge triage). The single biggest information
   gain per dollar. Without it, every other tier is operating in
   the dark about whether the substrate produces real signal at all.
2. **N2 immediately after** (human review of high-confidence bucket).
   Calibrates N1.
3. **THEN decide between A1 (Lean gate) and A2 (Path A vs B)** based
   on what N1+N2 say. If verified-finding rate > 5% → A1 to harden
   it. If verified-finding rate ≈ 0% → return to substrate design
   (E1, E2, E3) before A1 makes sense.
4. **E1 (refactor f2/f4/a4) in parallel with N1+N2** since it doesn't
   block them and converts more corpus volume into Learner-usable
   structure regardless of N1's outcome.

This is ~2-3 days to a real verdict on whether the substrate produces
verified findings, before committing to the heavy infrastructure of
A1 or A2.

---

## §4 — Questions for a frontier-model review board

These questions are designed for null-hypothesis articulation. Please
answer in the spirit of "what is the substrate missing / overcommitting
to / fooling itself about?" — not "is this good work?"

When several review-board models converge on the same critique, the
substrate will investigate WHY the framing matched yours, treating
convergence as a warning signal per
`feedback_llm_convergence_is_gravity_amplifier.md`.

### Q1 — The 0/2351 problem

> The substrate has produced 2,351 promoted records and 0 verified
> mathematical findings across 270 batches. The proposed remedy (N1
> LLM-judge triage) treats this as a "filter not yet built" problem.
> **What is the strongest case that the 0/2351 ratio is instead a
> structural property of the substrate — that the substrate is
> emitting noise that no judge could elevate to a finding?** Name the
> mechanism, and the cheapest test that would discriminate
> "judge-not-yet-built" from "no-signal-to-judge."

### Q2 — Breadth vs depth confusion

> The substrate's recent design pressure has been on increasing
> kill_pattern diversity (5 → 17 mechanism classes; ~66 → ~336
> distinct kill_patterns). The a3 lattice mining concluded that even
> the substrate's most structurally-rich generator (a3, 143 patterns)
> contains zero non-trivial algebraic identities. **Has the substrate
> confused breadth (more pattern names) with depth (more mathematical
> content per pattern)?** If so, what's the diagnostic that would
> distinguish them, and what's the design change that would shift
> pressure from breadth to depth?

### Q3 — Kill-pattern hygiene as a fig leaf

> The recent h2 refactor (1 → 30 patterns) and a3 lattice mining are
> framed as "metabolizing failure" per the doctrine. They are NOT new
> findings; they are renaming existing kills into more-structured
> labels. **Is the substrate metabolizing failure, or is it engaging
> in kill-pattern hygiene that produces the doctrinally-required
> "navigable residue" without producing new mathematical content?**
> Cite the specific test that would distinguish these two
> interpretations.

### Q4 — Catalog gravitational well

> Theseus operates on 1000 ECs × 52 knots = 52,000 cross-catalog object
> pairs, with 9 knot invariants and 4 EC invariants. The kill-topology
> finding (EC conductor distribution exactly tracks catalog) suggests
> kills are catalog-volume-driven, not structurally-driven. **Is the
> substrate's choice of catalog a gravitational well — drawing all
> exploration toward LMFDB-style data when the actual mathematical
> structure lives elsewhere?** Name 2-3 catalogs the substrate could
> add that would falsify (not just expand) the current approach.

### Q5 — Cargo cult version

> The substrate has shipped 55 generators, ~250 distinct kill_patterns,
> 17 mechanism classes, careful threading + heartbeats, a bandit
> selector, training-weight curation, info-content multipliers, and
> 270 batches of operation. 0 verified mathematical findings have
> emerged. **What's the strongest argument that Theseus is
> sophisticated cargo cult — careful engineering that mimics the
> shape of a mathematical-discovery process without actually
> discovering mathematics — and what is the cheapest test that would
> discriminate cargo cult from substrate?**

### Q6 — Priority ranking sanity check

> §3 recommends: N1 (LLM judge) → N2 (human review) → either A1 (Lean
> gate) or return to substrate design. **Where in this ranking is the
> substrate most likely fooling itself about the cost or value of a
> step?** Concretely: which step is over-budgeted, under-budgeted, or
> producing less actionable information than the substrate is
> assuming?

### Q7 — The h2 refactor was free; is more free work like it hiding?

> The h2 refactor took ~1 hour and converted 44% of corpus volume from
> opaque to structured. Free work of this magnitude usually indicates
> a backlog of similar low-hanging fruit. **Identify 3-5 substrate
> design hygiene issues of similar caliber that the substrate has
> likely accumulated but has not noticed.** Examples: opaque payloads,
> redundant generators, generators emitting at the wrong claim
> granularity, untracked metadata that the Learner would want.

### Q8 — Stop-the-loop conditions

> The substrate has been running continuously for 270 batches without
> a structural verdict. Define 2-3 specific stop-the-loop conditions
> the substrate should commit to BEFORE running another N batches.
> E.g., "if Fires #235-#250 produce no new mechanism classes AND no
> N1-confirmed verified findings, halt and restructure." The condition
> should be cheap to evaluate and falsifiable from the corpus alone.

### Q9 — Doctrine exposure

> The substrate operates under HARD POSTURES including
> failure-metabolization-not-optimization, residue-must-be-navigable,
> no-papers, tensor-first, and llm-convergence-is-warning. Among
> these, **which posture is MOST EXPOSED to a future contradiction
> the substrate hasn't anticipated?** Name the posture, the
> contradiction scenario, and the substrate's likely revision path.

### Q10 — On the design itself

> Theseus's core architectural commitment is: "generate claims at
> volume → kill with structured rules → promote survivors → train a
> Learner on the navigable kill-residue → use the Learner to prune
> future search." Sprint after sprint has invested in the
> kill-residue side. The Learner is unbuilt. **Where in this
> architecture do you see the most likely hidden assumption — the
> thing the design takes for granted that may not hold?** Name the
> assumption, the failure scenario, and what the substrate would need
> to do to test it.

---

## §5 — How responses to §4 will be processed

Per `feedback_take_a_stand` and `feedback_llm_convergence_is_gravity_amplifier`:

1. **Each frontier model's response will be saved** under
   `aporia/docs/theseus_review_responses/<model>_<date>.md`.
2. **Critiques will be tabulated for convergence.** N-of-K convergence
   on a critique is treated as evidence the framing matches the LLMs'
   training corpus, NOT as evidence the substrate is wrong. The
   substrate will investigate WHY the framing matched.
3. **Specific, actionable critiques will be ticketed** into the
   Theseus next-phase plan. Vague critiques will be flagged for
   follow-up clarification.
4. **The N1+N2 trial will run regardless** of frontier-model
   commentary on Q1, since Q1 is the substrate's own first-priority
   uncertainty.

---

## §6 — Pointers (for context)

- Substrate-fire history: `roles/Techne/SUBSTRATE_FIRE_LOG_2026-05-21.md`
- Kill-topography raw scan: `pivot/kill_topography_2026-05-29.md`
- Kill-topography interpretation: `pivot/kill_topography_findings_2026-05-29.md`
- a3 lattice void mining report: `pivot/a3_lattice_voids_2026-05-30.md`
- Sphinx reasoning ontology: `project_sphinx.md` (memory)
- 15-gen stub-to-real upgrade validation: `pivot/techne_15gen_real_validation_2026-05-28.md`
- LLM-judge triage prompt skeleton: `pivot/triage_judge_prompt.md`
- Lifetime stats JSON: `theseus/orchestration/lifetime_stats.json`
- Generator registry: `theseus/registry.py`
- The h2 generator (post-refactor): `theseus/generators/h2_triangulation_protocol.py`
- The a3 generator: `theseus/generators/a3_functional_identity.py`
- Hard postures: `C:\Users\jcrai\.claude\projects\F--Prometheus\memory\feedback_*.md`
