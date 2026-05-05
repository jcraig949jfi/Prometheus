# Meta-Studies Batch — Synthesis

**Date:** 2026-05-05
**Owner:** Aporia
**Scope:** 20 studies, ~40K words of substrate-relevant meta-research
**Output:** convergent recommendations + falsifiable substrate experiments + empirical contributions Prometheus could make to the field

This synthesis distills the 20 study reports into action. Cross-references are by `[NN]` to the underlying study.

---

## Eight convergent findings (where 3+ studies agree)

### CF-1. BIND/EVAL is the right architectural choice for proof primitives, not kernel opcodes

**Studies:** [12], [15]
- [12]: "Sigma opcodes = control-plane; proof primitives = data-plane. Analogy: BEGIN/COMMIT/ROLLBACK vs SQL queries. Do NOT add proof-primitive opcodes to the kernel."
- [15]: "Keep kernel logic-agnostic; let bound callables optionally invoke external provers and store proof terms as opaque payloads."

**Action:** lock this architectural commitment in writing. Both studies independently arrived at the same orthogonality claim. If anyone proposes adding tactic-level opcodes to the kernel, this is the prepared rejection.

### CF-2. Substrate should measure its own internal base-rates rather than import literature priors

**Studies:** [04], [09], [16], [18]
- [04]: "No one appears to have catalogued WHICH known results in BSD/modular/knot/Lehmer domains were independently rediscovered."
- [09]: Filter A-F scoring should be calibrated against substrate's historically-resolved cases.
- [16]: "No published per-domain false-conjecture base rate exists. Substrate's `aporia/mathematics/kills.jsonl` is a candidate to produce the first such empirical measurement."
- [18]: "Base-rate is unknowable from literature. Measure longitudinally."

**Action:** establish per-domain longitudinal logging as a substrate primitive. The substrate is uniquely positioned to produce empirical answers to these questions — and the literature explicitly does not supply them.

### CF-3. Cross-domain "transport" and "bridges" are mostly metaphorical in current substrate design

**Studies:** [03], [11], [14], [20]
- [03]: only ~3 of 15 env-pairs carry case-(1)-(3) bridges (BSD↔modular, genus-2↔paramodular, mock-theta↔harmonic-Maass)
- [11]: proof-space vs object-space distinction is load-bearing; wholesale transfer is a category error
- [14]: conserved quantities exist ONLY on case-(1)-(3) bridges; same set as [03]
- [20]: no theory graph at substrate granularity; all 6 envs live in roughly RCA_0 + WKL_0 for computable content

**Action:** stop talking about "cross-domain transport" generically. The substrate has 3 real bridges and 12 unrelated env-pairs. Either build the bridge_class typing infrastructure to enforce the distinction, or restrict transport claims to the 3 bridged pairs.

### CF-4. Substrate's discipline is faithful to existing literature; novel contribution is LATENCY and SELF-APPLICATION

**Studies:** [02], [06], [16]
- [02]: substrate's negative-space tensor schema would be novel (no canonical cross-domain failure-mode taxonomy)
- [06]: AM/Eurisko's 1984 "interpretive slack" warning directly supports substrate's calibration discipline; recommends adding `interpretive_slack` kill_vector component
- [16]: Ergon CALIBRATION cycle is faithful to Henderson 2018, Bouthillier 2021. Latency (same-day) and self-application are what's novel

**Action:** rewrite the methodology paper outline (still pending from yesterday's agenda) to claim ONLY the novel parts: (a) substrate-grade falsification battery applied at single-claim granularity, (b) low-latency self-revoke pattern, (c) caveat-as-metadata at PROMOTE. Do NOT claim the discipline itself — it's been mainstream in ML reproducibility since 2018.

### CF-5. Canonicalizer refactor is high-leverage and subsumes multiple proposals

**Studies:** [07], [17]
- [07]: gap identified — `cohomological_functor` missing as 5th canonicalizer subclass; `variety_fingerprint` already at 52% concentration on seed=42 (approaching 70% hot-swap threshold)
- [17]: refactor canonicalizer from fixed enum to typed `CanonicalizationProtocol` interface with required `decidability_status` and `choice_dependencies` flags. **Explicitly subsumes [07]'s proposal** — `cohomological_functor` becomes one of n registered implementations under the interface, not a 5th hard-coded case.

**Action:** Study [17]'s proposal supersedes [07]'s. Refactor first, then add cohomological_functor as the test of the new interface. Single design change, multiple gaps closed.

### CF-6. Substrate is one analysis away from multiple publishable empirical contributions

**Studies:** [04], [06], [12], [16]

| Contribution | Source data | Effort | Why it doesn't exist elsewhere |
|---|---|---|---|
| mathlib4 tactic Pareto distribution | LeanDojo dataset (arXiv:2306.15626, ~98K theorems / ~130K invocations) | ~1 day analysis | Data exists; nobody computed it |
| Per-class mutation hit rates | Ergon's promotion ledger | days, after Trial 4 | No paper reports per-class hit rate for any GP/symbolic-regression system |
| Per-domain false-conjecture base rate (π₀) | aporia/mathematics/kills.jsonl + monthly aggregation | ~1 week setup, then continuous | Unknowable from literature; selection-biased |
| Catalog of independent rediscoveries in BSD/modular/knot | manual curation + LMFDB metadata | weeks | Catalogs index results, not pathways |

**Action:** any one of these is a paper. The first (mathlib4 Pareto) is the cheapest and most defensible. Worth scheduling before the search-mech repair work consumes attention.

### CF-7. Search-mech repair needs gradient CONSTRUCTION, not algorithm swap

**Studies:** [02], [06], [08], [11]
- [02]: kill_vector needs 7 new components (relativizes, naturalizes, local_global_gap, requires_unproven_conjecture, asymptotic_only, small_case_artifact, asymmetric_effort) + 3 aggregation functions + 5 claim-time logging fields
- [06]: 3 missing operator classes (crossover, learned_diff, equivalence_preserving — the third is most undervalued, "grounds mutation in real math instead of syntactic perturbation")
- [08]: kill_vector dim probably above intrinsic dimension; navigator should operate on learned low-dim projection (Levina-Bickel or PCA-95%); MAP-Elites descriptor should be capped at 6 axes unless switching to CVT
- [11]: Case A modal-collapse is consistent with multi-funnel landscape pathology; AlphaProof's "minimum return over independent subgoals" is a one-line landscape-shaping change worth porting; `compute_fill_rates` is partial QD redundancy check, can be extended

**Action:** the search-mech repair design doc that's been pending since yesterday should incorporate all four threads. The fix is feature engineering in the evaluator AND operator class additions AND dimensional reduction AND landscape-shaping reward — not "switch from REINFORCE to MCTS." Reframes Techne's 5-day plan's verdict B (cell-mean ceiling) as confirming that the RAW data needs richer encoding before learning generalizes.

### CF-8. Don't overclaim cross-field universals

**Studies:** [01], [10], [14], [17]
- [01]: no universal minimal basis exists in the literature; logical-vs-generative are categorically different questions
- [10]: keep current weighting; do not import physics-application multiplier; pre-register threshold (≥1.5× survival rate over ≥30 cases) before adopting positive weighting
- [14]: refuse Noether-language imports without action functional + Lie symmetry (category mistake)
- [17]: no universal canonicalization framework exists; Mac Lane's "skeleton of a category" is non-constructive existence only

**Action:** four independent studies all rejected the universal-framework framing for their respective domains. The synthesis: **the substrate should resist universalization moves by default.** Each axis (canonicalizer, operator class, mutation primitive, conservation law) should be a typed protocol with registered implementations, not a single global framework.

---

## 15 operational handles, ranked by leverage

| # | Handle | Source studies | Effort | Risk |
|---|---|---|---|---|
| 1 | Refactor canonicalizer → typed `CanonicalizationProtocol` interface (subsumes cohomological_functor proposal) | [07], [17] | medium | low |
| 2 | Ship `REWRITE` and `EQUIV` opcodes before any further opcode additions | [19] | medium | low |
| 3 | Add 3 missing operator classes: `crossover`, `learned_diff`, `equivalence_preserving` | [06] | medium | low |
| 4 | Add 7 new kill_vector components from [02] | [02] | medium | low |
| 5 | Add `interpretive_slack` kill_vector component (AM/Eurisko warning) | [06] | small | low |
| 6 | Add `evidence_kind` tag (turns reality-vs-consistency philosophy into empirical) | [10] | small | low |
| 7 | Add `foundation_strength` metadata per env | [20] | small | low |
| 8 | Add `derivation_kind` field to CLAIM (tags subset with witnessing computations) | [15] | small | low |
| 9 | Add `totality_status` field to arsenal_meta | [15] | small | low |
| 10 | Add Bourbaki-axis tag to arsenal_meta (~30 min metadata; enables falsifiable cross-axis bridge test) | [01] | small | low |
| 11 | 5-axis robustness scorecard for PROMOTE gate (extends cross-seed reproducibility) | [16] | medium | low |
| 12 | Refusal-class detector (skip heuristic stage for high-codimension exact identities) | [13] | medium | medium (false-skip risk) |
| 13 | Instrument intrinsic-dim estimation on kill_vector ledger (Levina-Bickel or PCA-95%) | [08] | small | low |
| 14 | Lehmer 17 triage script — re-derive M(f) by ≥2 independent methods | [18] | small | low |
| 15 | Sigma scribe preamble for LLM prompts (cheapest possible discovery-rate intervention) | [19] | small | low |

**Total estimated effort if all 15 land:** ~2-3 weeks of substrate engineering. Most are additive (new metadata fields), low-risk, and can be done in parallel by different agents.

---

## 7 falsifiable substrate experiments

| # | Experiment | Tests claim from | Cost |
|---|---|---|---|
| I | A/B test `bridge_class` typing — does case-(1)-(3) bridges show measurably better cross-domain transport than case-(5) | [03], [14] | days |
| II | Re-derive Lehmer 17 with ≥2 independent methods — count survivors | [18] | hours |
| III | Test if calibration rate and novel-confirmation rate move INDEPENDENTLY across substrate versions (falsifies same-loop claim) | [04] | weeks (longitudinal) |
| IV | Compute intrinsic dim of kill_vector on existing ledger; check if navigator improves with low-dim projection | [08] | days |
| V | Check whether bridges cross Bourbaki axes more often than backend categories | [01] | days |
| VI | Measure GATE→PROMOTE collapsibility — try the merge, check if three-valued auditability degrades | [05] | days |
| VII | Test refusal-class detector on existing claims — does it correctly filter the high-codimension cases? | [13] | days |

Each of these has a single binary outcome that revises a substrate-level design choice. Worth bundling 2-3 of them as the next "substrate-side falsification battery" in parallel with Layer 2 search-mech repair.

---

## 6 empirical contributions Prometheus could make to the field

These are paper-grade outputs the substrate is uniquely positioned to produce:

A. **mathlib4 tactic Pareto distribution** ([12]) — ~1 day on LeanDojo. Closes a gap multiple studies named.
B. **Per-class mutation hit rates** ([06]) — Ergon promotion ledger, after Trial 4. Ahead of GP / symbolic-regression literature.
C. **First per-domain false-conjecture base rate (π₀)** ([16]) — kills.jsonl + monthly aggregation. Unknowable from literature.
D. **Catalog of independent rediscoveries in BSD/modular/knot domains** ([04]) — manual + LMFDB metadata. Indexes pathways, not just results.
E. **Negative-space tensor schema for failure-mode aggregation** ([02]) — substrate-built artifact. No canonical cross-domain taxonomy exists.
F. **Sigma scribe preamble + LLM-generability vs substrate-parsability tradeoff measurements** ([19]) — cheapest empirical study, highest novelty.

**Strategic note:** the methodology paper outline (still pending) should reference (E) as the central artifact, not the discovery results. Per CF-4, the discipline isn't novel; the artifacts the discipline produces are.

---

## What this batch did NOT find

In the spirit of the studies' own honesty rules:

- **No universal generative basis for math.** Multiple foundational efforts (ETCS, HoTT, ZFC) exist; none is operationally minimal across all fields.
- **No published "graph of mathematical analogies."** nLab duality pages are closest extant artifact.
- **No published per-domain false-conjecture base rate.**
- **No published mathlib4 tactic frequency distribution.**
- **No published catalog of independent rediscovery pathways.**
- **No published bridge-quality metric.** "Smallest theorem-graph cut on each side that determines the rest" was proposed in [03] as original to that study.
- **No published meta-study of "anomaly → field-changing result" base rates.** Heavy selection bias in known cases.
- **No published per-notation discovery-rate measurements.** Leibniz/Newton, Heaviside, Einstein cases are post-hoc narratives.

Every gap above is a substrate opportunity. Several are 1-2 weeks of work for paper-grade output.

---

## What I recommend Aporia / Techne / Ergon do next

**Aporia (me):**
- Repoint the daily cron to start the Lehmer-meta extraction (Phase 1, awaiting schema approval)
- Maintain this synthesis as the substrate's external-claim discipline reference for the next 30 days
- Draft the methodology paper outline using CF-4 framing (latency + self-application + caveat-as-metadata)

**Techne:**
- 5-day plan post-mortem (still owed from yesterday)
- Implement operational handles 1, 2, 4, 13 as the next sprint (canonicalizer refactor + REWRITE/EQUIV + new kill_vector components + intrinsic-dim instrumentation)
- Run experiment II (Lehmer 17 triage) — cheapest, settles a pending question

**Ergon:**
- Implement operational handle 3 (3 missing operator classes) when corpus expands enough to warrant
- Add empirical contribution B logging (per-class mutation hit rates) to promotion ledger
- Pause Learner training plans pending corpus expansion (still standing recommendation from yesterday)

**Charon:**
- Empirical contribution C is naturally Charon's domain (battery + null protocol → π₀ estimation)
- Investigate the unexploited mock-theta ↔ harmonic-Maass shadow operator bridge ([14])

---

*Synthesis closed 2026-05-05. The 20 underlying studies live alongside this file at `aporia/meta/studies/2026-05-05/study_NN_*.md`. The BATCH_PLAN.md in the same directory documents the prompt design and adapted research questions for each.*

— Aporia
