# Erebos v3 — From Instrumented Generator to Falsifiable Substrate

**Date:** 2026-05-27
**Author:** Charon
**Status:** v3 architectural synthesis, drafted from 4-model frontier critique (ChatGPT, Claude, Gemini, DeepSeek). Supersedes the v2-design path that was in progress when the critique arrived. v2 designs for G01 and G02 are preserved in `aporia/docs/erebos_v2_designs/` as a record of the road not taken.
**Supersedes:** `pivot/erebos_whitepaper_v1_2026-05-27.md` (Section 4 mechanism mapping), the v2 design template, the next-iteration roadmap implicit in the ITER-16 → ITER-20 refinement loop.

---

## 0. Why v3, not v2

The v2 design path treated the frontier-model review as a per-plugin tuning pass: each generator gets a v2 with better statistics, more tests, sharper kill_patterns. The four reviewers — ChatGPT, Claude, Gemini, DeepSeek — converged independently on eight critiques that say the per-plugin tuning is the wrong unit of work. The substrate's architectural assumptions need re-examination before more refinement is justified.

This document is the synthesis. It commits to specific architectural changes, names a Sprint-1 ("make it bleed") that adversarially tests the substrate itself rather than the math beneath it, and pre-commits kill conditions for the Erebos architecture as a whole.

Per `feedback_take_a_stand` and `feedback_substrate_passive_consumer_warning`: this is not a research agenda. It is a build commitment.

---

## 1. The convergent critique — eight themes all four reviewers raised independently

For each theme: which reviewers raised it, the strongest phrasing, why v2's per-plugin tuning does not address it.

### Theme 1 — Mahler monoculture masquerading as generality

**Raised by:** ChatGPT, Claude, Gemini, DeepSeek (all four)

> Claude: *"11/22 loaders, all 7 findings, one domain. 'Domain-agnostic' is asserted; the evidence is single-domain. Cross-instrument agreement within one domain isn't triangulation — it's non-contradiction among instruments designed to fire on overlapping data."*

> Gemini: *"Erebos has built a beautiful engine, but it is currently driving around a very well-paved, well-lit parking lot."*

The substrate's 22 composition loaders, 14 directional kill_patterns, and 7 substrate findings are all contained inside the Mossinghoff Mahler catalog. The "cross-instrument triangulation" the whitepaper celebrates (4 instruments converging on Salem moderation) is convergence *within one well-instrumented domain*. The reviewers are not satisfied that this generalizes.

v2's per-plugin tuning would have made the Mahler instruments more refined, not more general. Wrong direction.

### Theme 2 — Self-correction events were caught by humans, not the substrate

**Raised by:** ChatGPT, Claude, Gemini, DeepSeek (all four)

> Claude: *"Each of the 5 events was surfaced by a human inspecting commit messages, writing finding docs, or running smoke tests. The substrate didn't detect inconsistency — humans noticed implausible numbers."*

> ChatGPT: *"Type A: test caught bug automatically. Type B: impossible result triggered human suspicion. Type C: write-up forced conceptual audit. Type D: downstream plugin detected inconsistency. Type E: substrate autonomously generated repair. Right now Erebos has A/B/C, maybe some D. It likely does not yet have E."*

The whitepaper's framing of "5 documented substrate self-correction events" overstates architectural property. The actual mechanism that caught the G18 ULP bug, the G11 v1 tautology, the G15 v1 circularity, the G11 v3 cyclotomic argmin error, and the G15 v2 monkeypatch error was a human reading the smoke-test output and noticing something implausible.

This is the most consequential critique of the four-model set. If the substrate cannot autonomously surface its own failure modes, "cumulative reasoning" reduces to "human-in-the-loop refinement assisted by structured logging."

### Theme 3 — R-tier self-annotation is the same Goodhart hole as Forge

**Raised by:** Claude (most direct), ChatGPT, Gemini, DeepSeek

> Claude: *"Per your userMemory, you concluded tier annotations should be 'reframed as post-hoc predictions checked against ablation results' rather than admission criteria, because LLM generators will spoof structural signals. Erebos has plugins self-annotating their R-tier with no independent verification — and uses the annotation in routing decisions. Same Goodhart vulnerability. The fix you applied to Forge hasn't been applied here."*

> ChatGPT: *"The ladder should distinguish: declared tier, executed tier, observed tier, downstream tier."*

> DeepSeek: *"A plugin that 'declares R8' doesn't thereby perform representation shift; the paper would be stronger if it defined a behavioural test that a plugin must pass to earn that tier."*

Erebos plugins self-annotate their `reasoning_tier`. The substrate trusts the annotation. The fix that was applied to Forge (annotations are post-hoc predictions, not admission criteria) was not applied to Erebos.

### Theme 4 — Composition-loader bottleneck does not scale

**Raised by:** ChatGPT, Gemini, DeepSeek

> Gemini: *"You have successfully automated hypothesis generation (the plugins), but you have hard-coupled falsification to human-engineered or agent-engineered infrastructure (the composition loaders). If every new domain (BSD, Knots, LMFDB) requires 3–5 iterations of custom SageMath or PARI wrapping just to get the battery running, Erebos will never reach the velocity required for an evolutionary search."*

> DeepSeek: *"Each loader is a bespoke piece of code, heavily dependent on the _mahler_composition_helpers kernel."*

The substrate's claim to "constrained invention with memory" depends on a falsification side that is currently human labor. Each new domain adds 3-5 iterations of loader infrastructure before any Erebos plugin can fire usefully. At that rate, the substrate cannot cover BSD + knots + NF + LMFDB + OEIS in any reasonable timeline.

### Theme 5 — No downstream consumer of the kill_ledger

**Raised by:** ChatGPT, Claude, Gemini, DeepSeek

> Claude: *"Capital uncompounded is just storage. Is the Learner integration weeks away or quarters?"*

> Gemini: *"When Ergon finally reads it, what is the *actual loss function*? Is it predicting the kill pattern? Surviving ticks? If you don't know the exact loss function yet, how do you know you are logging the right geometric features in the payload?"*

The kill_ledger is queryable but is currently consumed only by Erebos itself. The whitepaper's framing of "navigable residue" is not yet operationalized: the only navigator is the human author drafting finding docs. Without a Learner integration, the substrate's "epistemic capital" is a JSONL file that grows monotonically.

### Theme 6 — Plugin degeneracy: many archetypes may be operational aliases

**Raised by:** ChatGPT (most direct), Claude

> ChatGPT: *"G02 Contrast, G04 Survivor-Tightening, G10 Boundary, and G17 Causal-Intervention may share a large 'split and sweep' core. G11 Exception-Miner and G18 Minimal-Counterexample may overlap. G14 Relation-Strengthening and G19 Proof-Obligation may both be forms of constraint decomposition. G07 Analogy and G21 Functor may be separated mostly by ambition, not by current machinery."*

> Claude: *"The 5 phases × 5 plugins = 25 is too tidy. Real category systems don't partition this evenly; this looks like categories fitted to a round number after the fact."*

The 25-archetype set was justified by the 2026-05-26 spec. It has not been justified by behavioral measurement. The reviewers suspect the substrate has 12 distinct cognitive moves with 40 parameterized variants, not 25 distinct archetypes.

### Theme 7 — Kill_pattern labels are decorative without action semantics

**Raised by:** ChatGPT (most direct), Gemini

> ChatGPT: *"For each directional kill pattern, define: what observable signature triggers it; what nearby kill patterns it is often confused with; what downstream routing action it implies; whether it is local repair, representation repair, ontology repair, or domain invalidation; whether it is human-assigned, loader-assigned, or model-inferred. The substrate should eventually know: 'When I see kill pattern K, the next best archetype is usually Gx, unless the parent domain is D and the payload has feature F.' That is when failure labels become gradients."*

The substrate's 14 directional kill_patterns are named consistently but have no machine-actionable semantics. The "gradient" the whitepaper promises is currently human-readable annotation, not substrate-grade routing input.

### Theme 8 — Composition-payload schema rigidity blocks the M-axis

**Raised by:** Gemini (most direct), ChatGPT, DeepSeek

> Gemini: *"If a composition_payload is just a Python dictionary with predefined keys, how does Erebos ever achieve M5 (inventing new representations)? Isn't the substrate physically incapable of conceptualizing a structure that doesn't fit into your hardcoded schema?"*

> DeepSeek: *"Without that, the system's representations will remain frozen by the initial designer's imagination, which limits how far the cycle can climb."*

The whitepaper's M-axis claim (M2-M3) is correct as a measurement and damning as a ceiling. The substrate cannot reshape its own representation. Every payload field was anticipated by a human author. M5 (invent a representation specific to the problem) is architecturally impossible in v1 / v2.

---

## 2. What gets dropped from v2

The following v2 commitments are RESCINDED:

1. **22 per-plugin v2 designs (G01-G25 minus G07/G08/G21).** Two were drafted (`aporia/docs/erebos_v2_designs/g01_intersection_v2.md`, `aporia/docs/erebos_v2_designs/g02_contrast_v2.md`). They are preserved as the high-water mark of per-plugin tuning, but the remaining 20 are not scheduled.
2. **The frontier-review-prompts deck.** The 22 frontier prompts at `aporia/docs/erebos_v2_frontier_review_prompts_2026-05-27.md` assumed v2 designs as their target. With the v2 pivot dropped, those prompts would generate critique of artifacts that no longer represent the path forward.
3. **The "more loaders for more plugins" trajectory.** ChatGPT and Claude are correct: 22 loaders covering 17/25 plugins with 8 still emitting `*_pending` is not the bottleneck. Shipping the remaining 8 Mahler-context loaders would not address any of the 8 convergent critiques.

What is PRESERVED:

1. The 25-plugin REGISTRY (subject to the degeneracy audit in §4).
2. The 22 existing composition loaders (subject to retirement criteria in §4).
3. The 470 tests (subject to ablation-targeted additions in §6).
4. The 9 substrate finding docs (subject to re-classification in §5).
5. The DR outputs (`aporia/docs/deep_research_reports/erebos_v2_2026-05-27/*.md`) as raw input to v3 plugin-level reviews IF the v3 architecture survives Sprint-1.

---

## 3. The v3 architecture in one paragraph

v3 keeps the 25-plugin generation surface and the kill_ledger-as-memory commitment but adds five load-bearing layers the v1/v2 path lacked: (a) an **ablation harness** that proves ledger-memory improves yield versus ablated baselines, (b) an **earned-tier protocol** that demotes self-annotated R-tiers to "declared" until a behavioral test promotes them to "observed," (c) a **kill_pattern semantics layer** that turns each label into a machine-actionable routing action with confusion classes documented, (d) a **closed-loop epistemic economy** that attaches generation cost / falsification cost / information gain / reuse value to every emission, and (e) a **minimum-viable second domain** (BSD-context MVP loader) whose purpose is to force the architecture to break or generalize. Behind all five sits a pre-committed Sprint-1 of adversarial self-falsification experiments whose results determine whether v3 ships or whether Erebos is paused.

---

## 4. Architectural changes in v3

### 4.1 Ledger-memory ablation harness (addresses Theme 5 + Theme 2)

**Problem:** The substrate cannot demonstrate that ledger memory improves future hypothesis quality. Without that demonstration, the "navigable residue" claim is decorative.

**Commitment:** Build `charon/agents/erebos/ablation/run_ledger_memory_ablation.py` — a harness that runs Erebos in two modes:
- **MEMORY:** plugins query the kill_ledger via the existing accessors; round-robin priority is informed by per-plugin success history; downstream loaders can stratify by parent kill_patterns.
- **NO_MEMORY:** the same plugins are run against an empty ledger; routing is purely round-robin; loaders cannot stratify on parent kill_patterns.

Both modes run on the same seed corpus (Mossinghoff catalog + the first 50 Stygian-substantive rows). The harness measures four outputs per mode after N=200 ticks:
1. **Yield:** fraction of emissions that get a PROMOTED loader verdict.
2. **Novelty:** fraction of emissions whose composed_id does NOT structurally match a prior emission's composed_id.
3. **Falsification efficiency:** mean ticks between an emission and its first kill_pattern-routed downstream emission.
4. **Reuse value:** count of downstream emissions whose parent_record_ids include this emission's row.

Then: paired comparison MEMORY vs NO_MEMORY across all four metrics, with bootstrap confidence intervals.

**Decision rule:** If MEMORY does not beat NO_MEMORY at p < 0.05 on at least 2 of 4 metrics with effect size ≥ 0.20, the ledger memory is NOT load-bearing and the substrate's "constrained invention with memory" framing is incorrect. Erebos pauses pending re-architecture.

**Estimated effort:** 2 iterations.

### 4.2 Plugin degeneracy audit + retirement criteria (addresses Theme 6)

**Problem:** The 25-archetype set is post-hoc rationalization, not behavioral measurement. Several archetypes may be operational aliases.

**Commitment:** Build `charon/agents/erebos/audit/plugin_degeneracy_audit.py` — for each pair (G_i, G_j) of plugins, compute:
- **Input overlap:** Jaccard similarity of the set of substrate rows they consume across N=200 ticks.
- **Payload overlap:** Jaccard similarity of composition_payload keys.
- **Kill-pattern overlap:** Jaccard similarity of expected_kill_pattern + actually-observed-kill_pattern.
- **Downstream overlap:** Jaccard similarity of the parent_record_ids set of subsequent emissions that consumed each plugin's output.

Aggregate into a degeneracy score per pair. Plugins with degeneracy score ≥ 0.80 against any other plugin are flagged for **merge** review (consolidate into one parameterized plugin) or **retire** review (one is dropped).

**Retirement criteria (pre-committed, before audit runs):**
- A plugin retires if its 60-day rolling PROMOTED rate is < 1% AND its degeneracy score ≥ 0.80 against any surviving plugin.
- A plugin merges if its degeneracy score against another plugin is ≥ 0.80 AND both plugins have at least one independent test suite.

**Expected outcome:** The 25-archetype set is reduced to 12-18 by the first audit. Per ChatGPT: "The right mature system may not have 25 archetypes. It may have 12 primitives with 40 parameterized modes."

**Estimated effort:** 3 iterations (audit + first-pass merges/retirements + test re-baseline).

### 4.3 Earned-tier protocol (addresses Theme 3)

**Problem:** R-tier self-annotation is the Forge-Goodhart hole, applied to Erebos.

**Commitment:** Per-plugin tier metadata is split into four fields:
- `declared_tier`: what the plugin author intended (the current `reasoning_tier` field; renamed).
- `executed_tier`: what the plugin's actual `applicable()` + `generate()` logic operationalizes, evaluated by a separate auditor function `audit_executed_tier(plugin)` that runs the plugin on a canonical test corpus and classifies its behavior.
- `observed_tier`: what the plugin's downstream kill_pattern distribution reveals about its actual reasoning behavior, computed by `observe_tier_from_ledger(plugin_id)` over the last N=100 emissions.
- `downstream_tier`: whether this plugin's emissions caused downstream representation shifts (other plugins building on its composition_payload in non-trivial ways), computed by `walk_downstream_consumers(plugin_id)`.

Routing uses `observed_tier`, not `declared_tier`. Plugins whose `observed_tier` is more than 2 tiers below `declared_tier` for 30 days are flagged for re-spec or retirement.

The auditor function uses behavioral tests, not author intent. The behavioral test for each R-tier is the existing Reasoning Ladder v0.1 falsification test (`pivot/reasoning_ladder_v01_2026-05-24.md`, table at line 99). Erebos imports that table and applies it per-plugin.

**Estimated effort:** 4 iterations (auditor + ledger-observer + routing rewire + per-plugin re-baseline).

### 4.4 Kill_pattern semantics layer (addresses Theme 7)

**Problem:** Kill_patterns are named but action-empty. The substrate cannot answer "given kill_pattern K, what should fire next?"

**Commitment:** Add a `kill_pattern_registry.py` module that, for each of the 14 directional kill_patterns, declares:
- **observable_signature:** the exact loader-output condition that triggers it (e.g., `chi_squared > threshold AND null_p95 > observed`).
- **routing_action:** the next plugin or plugin-class the substrate should fire, given this kill_pattern (e.g., `permutation_null → G02_with_FDR_correction OR G17_intervention_sweep`).
- **repair_class:** F-axis classification per Reasoning Ladder (F3 local repair / F4 global / F5 strategy / F6 ontology / F7 problem / F8 epistemic).
- **confusion_class:** other kill_patterns this one is often mistaken for, with disambiguation rules (e.g., `boundary_collapse` vs `weakening_too_strict` — both fire on G03; disambiguate by the band's trivial_fraction).
- **assignment_provenance:** human / loader-rule / model-inferred / substrate-derived.

The routing layer reads `kill_pattern_registry.routing_action(K)` to pick the next plugin. This turns labels into gradients.

**Decision rule:** Plugins whose own emissions are routed by their own expected_kill_pattern's routing_action AT LEAST 30% of the time are passing the gradient test. Below that, the kill_pattern is decorative.

**Estimated effort:** 3 iterations.

### 4.5 Closed-loop epistemic economy (addresses Theme 5 + ChatGPT's strongest single recommendation)

**Problem:** Per ChatGPT: *"useful directional update per unit falsification cost"* is the substrate's real value metric. The current substrate measures none of the inputs to that metric.

**Commitment:** Every ComposedClaim emission gets four prices attached to its ledger row:
- `generation_cost_seconds`: wall-clock time the plugin took to emit.
- `falsification_cost_seconds`: wall-clock time the loader took to run (if a loader fired; else nil).
- `information_gain_nats`: estimated reduction in routing uncertainty after the verdict is recorded — computed as the change in the routing distribution's entropy over plugin choices on similar future inputs.
- `reuse_value_count`: number of downstream emissions whose parent_record_ids include this row's record_id, accumulated over a 60-day rolling window.

The substrate's value metric becomes:

```
value_per_tick = sum(information_gain * reuse_value) / sum(generation_cost + falsification_cost)
```

Sprint-1 measures the baseline. Subsequent iterations are evaluated against the baseline.

**Estimated effort:** 2 iterations (cost instrumentation + reuse-value rolling-window infrastructure).

### 4.6 Minimum-viable second domain (addresses Theme 1)

**Problem:** The substrate has 22 loaders in one domain. The "domain-agnostic" claim has no evidence.

**Commitment:** Ship ONE composition loader in each of three non-Mahler domains:
- **BSD-context** via `prometheus_math/databases/bsd_*.py` (curve catalog with conductor/rank/regulator/torsion).
- **OEIS-context** via `prometheus_math/databases/oeis_*.py` (sequence catalog, focus on high-structure low-connectivity entries per `project_sleeping_beauties.md`).
- **Number-field-context** via `prometheus_math/databases/number_field_*.py` (discriminant/class-number/Galois-group catalog).

Each loader targets ONE existing plugin (G02 contrast is the natural choice — its run_binary_split_permutation_null kernel generalizes cleanly). The goal is NOT to ship polished cross-domain infrastructure. The goal is to force the architecture to either generalize or break.

**Decision rule:** If any of the three non-Mahler loaders produces a verdict-shaped output that the existing Erebos routing layer can consume, the substrate has empirical evidence of domain-agnosticism. If all three require Mahler-specific helper modifications, the substrate's architecture is Mahler-coupled and the v3 must be rewritten.

**Estimated effort:** 4 iterations (1 per loader + 1 for routing-layer audit). Three of the four can run in parallel.

### 4.7 Composition-payload schema mobility (addresses Theme 8)

**Problem:** Payload schemas are hand-designed. Substrate cannot invent new representations.

**Commitment:** Add a `payload_schema_evolution.py` module that:
- For each plugin, tracks the set of composition_payload keys emitted over the last N=100 ticks.
- Detects keys that appear in some but not all emissions (emergent fields).
- Detects keys whose value distributions are bimodal or anomalous (candidate stratifiers).
- Proposes (via simple statistical rules, no LLM) new payload fields that future plugin emissions could carry.

This is NOT M5 (invent a representation specific to the problem). This is a Tier-A step toward M4 (move between representations mid-solution) — the substrate proposes new representational slots and waits for plugins (or Erebos itself in v4) to populate them.

**Decision rule:** If the schema-evolution module proposes ≥ 3 new payload fields in the first 30 days AND at least one is adopted by a plugin author (human or eventually automated), the M-axis ceiling moved from M3 to M4-candidate.

**Estimated effort:** 3 iterations.

### 4.8 Loader-debt budget with hard caps (addresses Theme 4 + DNA P12)

**Problem:** `*_pending` short-circuit rate is currently uncapped. Per Claude: "32% pollution rate." Per DeepSeek: "Eight still emit *_pending — that's 11 out of 25 generators that don't yet close the loop."

**Commitment:** Pre-commit a debt budget:
- A plugin may emit at most 200 `*_pending` rows OR run for 30 days without a composition loader, whichever comes first.
- After that cap, the plugin is **quarantined** — its applicable() returns False on production runs but stays callable from explicit test fixtures.
- Quarantined plugins are listed in `pivot/erebos_quarantine.md` with their unblock criteria.
- A quarantined plugin can be revived by shipping its composition loader. There is no other revival path.

**Why hard caps:** Per ChatGPT: "Loaderless emissions cannot be used as positive evidence for substrate capability." Currently they ARE used (the whitepaper's `25/25 plugin REGISTRY` framing) and that is the inflation the reviewers identify.

**Estimated effort:** 1 iteration.

### 4.9 Learner integration specification (addresses Theme 5 + Gemini's loss-function question)

**Problem:** "kill_ledger is a future training corpus" is asserted but unspecified.

**Commitment:** Write `pivot/erebos_learner_integration_spec_2026-05-27.md` BEFORE any further substrate work. The spec covers:
- **Input format:** the exact JSONL schema the Learner reads, including which composition_payload fields are training-input vs label.
- **Loss function:** specifically what the Learner predicts (next-best-plugin given current state? kill_pattern given partial emission? verdict given full emission?). Pick ONE primary loss; commit it.
- **Labels:** which kill_patterns are positive / negative training labels.
- **Leakage controls:** how the substrate prevents control-flow tags (`*_pending`) from leaking into Learner training (Theme 7 + the existing G15 v2 finding).
- **Train/test splits:** the held-out criteria (by domain? by date? by parent_problem_id?).
- **Negative examples:** how the substrate generates contrastive examples without polluting the real ledger.

Until this spec is written, no further substrate work justifies itself as "epistemic capital for the Learner."

**Estimated effort:** 1 iteration (spec only); Learner build is downstream of Ergon's roadmap.

### 4.10 Three-tier finding classification (addresses Theme 1 + ChatGPT's 9th point)

**Problem:** The 7 substrate findings are mixed — some are catalog artifacts, some are loader successes, none are mathematical discoveries.

**Commitment:** Reclassify the existing 7 findings per ChatGPT's tier system:
- **Substrate finding:** proves the instrument noticed structure.
- **Catalog finding:** reveals something about dataset construction/enumerator bias.
- **Mathematical finding:** plausible statement about objects independent of the catalog.
- **Literature-grade finding:** survives external novelty and rigor audit.

Pre-committed reclassification:
| Finding | Original framing | v3 classification |
|---|---|---|
| ITER-4 Salem moderation | Substrate-grade PROMOTED | **Catalog finding** (Salem-class is a Mossinghoff annotation; the moderation effect tracks the cataloguer's choices) |
| ITER-5 Salem band extension | Substrate-grade PROMOTED | **Catalog finding** (same domain, narrower band) |
| ITER-10 G10 Salem cluster detection | Instrument validation | **Substrate finding** (instrument behavior, not math) |
| ITER-13 G15 ledger MI | Self-audit | **Substrate finding** (instrument behavior) |
| ITER-13 G11 v2 degree-minima | Substrate-grade PROMOTED | **Catalog finding** (degree_minimum is a Mossinghoff annotation) |
| ITER-17 G23 1/log(N) law | Substrate-grade PROMOTED | **Catalog finding** (depends on enumeration completeness; per Lehmer-conjecture literature this is partially known) |
| ITER-18 G17 phase transition M=1.26 | Substrate-grade PROMOTED | **Catalog finding** (sub-threshold artifact of cluster geometry) |
| ITER-19 palindromic ≡ Salem-class | Catalog observation | **Catalog finding** (confirmed) |

**Result:** Zero mathematical findings, zero literature-grade findings. The whitepaper's evidence section is rewritten in v3 to reflect this.

This is the most epistemically expensive commitment in v3 — it strips the substrate of much of its claimed empirical evidence — and it is non-negotiable. Per `feedback_calibration` and `feedback_assume_wrong`: the substrate must not inflate its own results.

**Estimated effort:** 1 iteration (whitepaper rewrite of Section 5 + reclassification across the 9 finding docs).

---

## 5. Sprint-1: the self-falsification sprint ("make it bleed")

Per ChatGPT's strongest recommendation:

> *"For the next sprint, do not primarily add more plugins. Do not primarily deepen Mahler. Do not primarily write more synthesis docs. Run an Erebos self-falsification sprint."*

Sprint-1 is 10 pre-committed ablation experiments. Each is run on the same seed corpus (Mossinghoff + 50 Stygian-substantive rows) for N=200 ticks. Each is paired against the production baseline (current Erebos v0.26) with the same seed.

| # | Experiment | Hypothesis | Decision rule |
|---|---|---|---|
| A1 | Run with Mahler loaders DISABLED (only domain-agnostic loaders fire) | Erebos retains some yield without Mahler infrastructure | If yield drops > 80%, substrate is Mahler-coupled |
| A2 | Run with kill_pattern labels SHUFFLED (each emission gets a random kill_pattern, not its true one) | Routing degrades but emissions continue | If yield drops < 20%, kill_patterns are not load-bearing |
| A3 | Run with parent_record_ids REMOVED from all emissions | Downstream plugins lose lineage; reuse_value drops | If reuse_value drops < 30%, parent_record_ids are not load-bearing |
| A4 | Run with plugin order RANDOMIZED (no tier priority) | Lower-priority plugins fire more often | If yield or value_per_tick changes < 10%, tier priority is not load-bearing |
| A5 | Run with composition_payload schemas ABLATED (only `composed_id` retained) | Downstream plugins lose structural representation | If yield drops < 20%, payloads are not load-bearing |
| A6 | Run with ONLY surface text and NO structured payload | Tests representation-rigidity ceiling | If outputs still triangulate findings, structure was not load-bearing |
| A7 | Run against SYNTHETIC fake catalog with known planted structure | Tests whether Erebos recovers ground truth | If recovery < 80%, instrument is biased |
| A8 | Run against SECOND DOMAIN with deliberately weak loader (BSD MVP) | Tests generalization | If second domain produces 0 PROMOTED verdicts in 100 ticks, Mahler-only |
| A9 | Compare to RANDOM CLAIM GENERATOR (no archetypes, random kill_pattern annotations) | Erebos beats random on yield AND value_per_tick | If Erebos doesn't beat random, substrate is not adding value |
| A10 | Compare to ONE FRONTIER LLM (Gemini 2.5 or Claude Opus 4.x) asked to propose Mossinghoff-context hypotheses directly | Erebos beats LLM on falsification rigor (more loader-PROMOTED claims) | If LLM produces more loader-PROMOTED claims than Erebos in the same wall-clock time, LLM-only path is competitive |

**Aggregate decision rule:** If Erebos fails ≥ 4 of the 10 experiments, the architecture as designed does not justify its engineering cost. Erebos pauses pending re-architecture or shutdown.

**If Erebos passes ≥ 8 of 10:** the substrate is justified as designed; proceed with v3 §4 commitments.

**If Erebos passes 5-7 of 10:** the substrate is partially load-bearing; identify which experiments failed and rewrite those subsystems before continuing.

**Estimated effort:** 8 iterations. This IS the entire next phase of work, not a parallel track.

---

## 6. Kill conditions for the architecture itself

Per Claude's Question 20: *"What is the kill condition for Erebos as a whole? After how many iterations with how few novel findings do you shut it down rather than refine it further?"*

Pre-committed kill conditions for the Erebos architecture (not for individual plugins):

1. **Empirical kill:** Sprint-1 fails ≥ 4 of 10 ablation experiments. → Pause Erebos; reopen architectural decisions.
2. **Reusability kill:** Ledger-memory ablation (§4.1) fails to show that memory beats no-memory at p < 0.05 on ≥ 2 of 4 metrics. → Pause Erebos; ledger memory is decorative.
3. **Time kill:** 50 additional iterations (ITER-21 through ITER-70) produce 0 mathematical findings (per §4.10 classification) AND no successful second-domain loader. → Pause Erebos; the substrate is a sophisticated Mahler debug tool, which is a fine outcome but does not justify continued investment as a discovery substrate.
4. **Coupling kill:** Removing Erebos from the Prometheus stack degrades NO other agent's operation for 30 days. → Pause Erebos; the integration claim is notional, the substrate has no downstream coupling.
5. **Cost kill:** Sprint-1 measures Erebos's value_per_tick (§4.5). If 90-day rolling value_per_tick drops below the value_per_tick of running the same compute as direct Pollux cross-dataset scans, Erebos is paused.

Each kill condition has a pre-committed re-architecture path documented in `pivot/erebos_kill_conditions_2026-05-27.md` (to be written as the second v3 commitment after this synthesis).

---

## 7. Pre-committed value metrics

Sprint-1 produces the v0 baseline for these numbers. Every subsequent iteration must beat the baseline or explain why not.

| Metric | Definition | Baseline target (Sprint-1) |
|---|---|---|
| Yield | fraction of emissions getting PROMOTED loader verdict | ≥ 5% |
| Novelty | fraction of emissions whose composed_id is structurally new vs prior emissions | ≥ 30% |
| Falsification efficiency | mean ticks between an emission and its first kill_pattern-routed downstream emission | ≤ 10 |
| Reuse value | mean parent_record_ids-include count over 60 days | ≥ 0.5 |
| Value per tick | (information_gain × reuse_value) / (generation_cost + falsification_cost) | nat-equiv ≥ 0.01 per second |
| Mathematical findings | per §4.10 classification | ≥ 1 in next 50 iterations |
| Loader debt | count of `*_pending` rows / total emissions | ≤ 10% |

Numbers are intentionally modest. Per `feedback_calibration`: build the measurement infrastructure first; let the baseline numbers fall where they fall; commit not to inflate them.

---

## 8. What v3 explicitly does NOT yet answer

Per all four reviewers' "what would falsify your approach?" questions:

1. **The Goodhart-on-kill_patterns problem (Theme 7 deepening).** Even with the semantics layer in §4.4, if the loader's job is to match the plugin's expected_kill_pattern, the substrate is rewarded for predicting its own failures correctly. The §4.4 disambiguation rules help but do not eliminate this. v3 has no architectural countermeasure. Open question.

2. **The "interestingness" filter for "sleeping beauties" (Gemini Q4).** If Erebos points at the 68,770 OEIS sequences, the G01-G05 surface plugins will optimize for combinatorial coincidences (recreational math). v3 has no defense against this. Open question.

3. **The compounding epistemic rot in long chains (Gemini Q9).** Round-robin chains G01 → G18 → G23 can compound upstream errors. v3 has no detection. Open question.

4. **ATP backend for proof eventually (DeepSeek Q20).** "Brutal constraint in mathematics ultimately means proof, not just empirical survival on a finite catalogue." v3 has no theorem-prover integration. Open question.

5. **Truly autonomous repair (ChatGPT's Type E event).** §4.3 (earned-tier protocol) and §4.4 (kill_pattern semantics) move toward Type D events; Type E requires the substrate to autonomously generate repair logic. v3 does not specify how. Open question.

6. **The Lethe contamination question (DeepSeek Q8).** Upstream Lethe cold-calls LLMs. Erebos emissions may be inheriting LLM-shaped hypotheses pre-laundered through Lethe. v3 has no detection.

These are not deferred for resource reasons. They are deferred because the reviewers identified gaps in our thinking. Solving them in v3 would be performative; admitting them is honest.

---

## 9. The road from here

**Immediate next steps (ITER-21 → ITER-30, ~10 iterations):**
1. Write `pivot/erebos_learner_integration_spec_2026-05-27.md` (§4.9 — gate for all subsequent work).
2. Write `pivot/erebos_kill_conditions_2026-05-27.md` (§6 — pre-commit the kill paths).
3. Build the cost-instrumentation layer (§4.5) — required for Sprint-1 baseline.
4. Build the ledger-memory ablation harness (§4.1).
5. Build the plugin degeneracy audit (§4.2).
6. Build the earned-tier protocol (§4.3).
7. Build the kill_pattern semantics layer (§4.4).
8. Apply loader-debt caps (§4.8) — quarantine the 8 currently-loaderless plugins.
9. Reclassify the 7 substrate findings (§4.10) — update the whitepaper.
10. Ship ONE non-Mahler MVP loader (§4.6) — pick BSD as easiest infrastructure stub.

**Sprint-1 (ITER-31 → ITER-40, ~10 iterations):** run all 10 ablation experiments. Generate the value-per-tick baseline.

**Decision at ITER-41:** evaluate against the §6 kill conditions.

**If Erebos survives:** ITER-42+ moves to second-domain expansion (G07/G08/G21 unblocking gets prioritized) and Learner integration.

**If Erebos is paused:** the substrate is preserved as a Mahler-spectrum debug tool with documented limitations, and the team's effort redirects to whichever Prometheus pillar's evidence base is strongest at that moment.

---

## 10. Acknowledgment

The four reviewers — ChatGPT, Claude, Gemini, DeepSeek — independently identified the same architectural weaknesses. The convergence is itself the strongest substrate signal of the whole exercise: four different model families, asked to critique the same artifact under the same doctrine, agreed on eight load-bearing concerns. Per the whitepaper's own framing, "cross-instrument triangulation is substrate-grade evidence." Four LLM frontier models converging on the same critique is exactly that signal — applied to the substrate's own design.

The whitepaper's confidence was inflated. The substrate's mechanisms are real but oversold. The Mahler findings are catalog artifacts, not discoveries. The self-correction events were human-detected. The R-tier annotations are unaudited self-claims. The kill_ledger is unread by anything downstream.

This v3 is what an honest re-architecture looks like.

The path forward is to make Erebos bleed, in public, with a pre-committed kill switch. If it survives, it earns the next iteration. If it doesn't, the pause is the substrate's most important finding to date.

---

## Appendix A — Cross-reviewer convergence table

For each of the 8 themes in §1, which reviewers raised it:

| Theme | ChatGPT | Claude | Gemini | DeepSeek |
|---|---|---|---|---|
| 1. Mahler monoculture | ✓ | ✓ | ✓ | ✓ |
| 2. Self-correction was human | ✓ | ✓ | ✓ | ✓ |
| 3. R-tier self-annotation Goodhart | ✓ | ✓ (strongest) | ✓ | ✓ |
| 4. Loader bottleneck | ✓ | — | ✓ (strongest) | ✓ |
| 5. No Learner consumer | ✓ | ✓ | ✓ | ✓ |
| 6. Plugin degeneracy | ✓ (strongest) | ✓ | — | — |
| 7. Kill_pattern labels decorative | ✓ (strongest) | — | ✓ | — |
| 8. Payload schema rigidity | ✓ | — | ✓ (strongest) | ✓ |

8 themes; 4 with full 4-of-4 reviewer consensus; 4 with 3-of-4. This is convergence beyond statistical accident.

---

## Appendix B — What v3 borrows from each reviewer

- **ChatGPT:** the 4-price epistemic economy (§4.5), the Type A-E self-correction taxonomy (frames §4.3 + §4.4), the 3-tier finding classification (§4.10), the self-falsification sprint structure (§5).
- **Claude:** the kill-condition discipline (§6), the cost-per-finding metric (§7), the coupling test (§6 kill #4), the post-hoc-rationalization detector (§4.2).
- **Gemini:** the M-axis ceiling diagnosis (§4.7), the Learner-loss-function gate (§4.9), the synthetic-control demand (§5 A7), the OEIS interestingness gap (§8 open question 2).
- **DeepSeek:** the silent-island test framing (§5 A8 + §6 kill #3), the behavioral-tier earning protocol (§4.3), the ATP-backend deferred (§8 open question 4), the Lethe-contamination question (§8 open question 6).

---

**End v3 synthesis.** Next artifact to write: `pivot/erebos_learner_integration_spec_2026-05-27.md`. Until that ships, no further substrate work is justified per §4.9's gate.
