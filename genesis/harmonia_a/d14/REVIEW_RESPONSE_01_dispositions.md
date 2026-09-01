# D-14 external review #1 — dispositions (2026-09-01)

Reviewer response received via operator (full text held by operator; key
content restated here for the record). Dispositions before resuming:

| item | reviewer position | disposition |
|---|---|---|
| Finish A2 | Finish unchanged; stops were operational; do NOT inspect partial spectrum | **ADOPTED** — resumed now; no interim reads |
| SURVIVES weight | Narrow replication/extension unless bridged; falsification would be highly informative | **ADOPTED** into final packet's claim ceiling wording |
| Q1 bridge | Separate labeled instrument-equivalence assay, NOT a D-14 amendment: same pairs under I_final and I_traj; 2x2 transition table; dangerous cell = traj-changed/final-unchanged; ~30 clean parents, >=300 single-site pairs, stratified by final-output class | **QUEUED** as post-verdict assay B1 (design to probe what trajectory signal is obtainable for persisted artifacts: evaluate.behavior vector / trace_addr / limits) |
| Q3 resolution | Keep 8-case battery for D-14; afterwards re-evaluate stratified site sample at 64 cases; measure bin migration | **QUEUED** as post-verdict assay B2 |
| Q2 estimand | Middle_mass stands; NEXT prereg should characterize conditional nonzero spectrum G(t) = P(I<=t \| I>0) or fixed quantiles of I\|I>0 | **RECORDED** for any successor prereg |
| Q4 estimand wording | A2 estimates the spectrum under the default-operator-induced distribution over eligible single-site changes, NOT the uniform site spectrum; verdict wording must say so; site-exhaustive coverage required only for representation-level claims ("no graded sites") | **ADOPTED** — final packet wording bound |
| Q5-Q7 | D-15 should be the causal encoding experiment (same semantics, E0 gapped / E1 graded / E2 graded+neutral-redundant; prereg graded->band-appears), not a fourth substrate survey; encoding intervention before operator intervention; transfer test for shared mechanism (frozen predictor, disjoint parents, shuffled-address + distance-matched controls, semantically-equivalent-different-genotype arm) | **RECORDED** — D-15 not authorized by the D-14 charter; carried as the recommended successor |
| Q8-Q12 | intervene() contract (requested vs effective, reject-on-uncertifiable, no silent coercion); selective pair persistence (3 retention tiers; "scientific addressability is itself provenance"); requested/effective/hash config echo as release-blocking invariant; per-response release header; behavior_distance as versioned server primitive | **FILED** upstream as D14_M1_REQUIREMENTS (below) |
| Q13 | Reframe target as encoding-induced geometry G->E->P->B; local controllability; reachable consequence spectrum R_x(eps) with hole near zero: R_x ~ {0} U [c,inf) | **RECORDED** — sharper than "gapped spectrum"; candidate invariant renamed "resolution of controllable consequence" |
| Q14 | Court-for-operators: Acquisition -> Novel Reach -> Ablation -> Transfer -> Composition -> Retention; delta-reach under matched compute; matched random operators mandatory; "a reasoning operation is something whose causal availability expands reachable solution space under controlled resources" | **RECORDED** — the operational north-star definition; feeds Gen-4 of the expedition |
| Q15 | Resurrect D-9 as retrieval/intervention experiment (C_raw vs I_generic vs I_machine vs I_shuffled; same solver+evaluator; held-out problems per fixed compute) — removes mutation-geometry confound | **RECORDED** |
| Q16 | Injected-known-consequence ladder (delta_0..delta_3, blinded) as ruler calibration standard: "before concluding nature contains no millimeters, prove the ruler can measure a millimeter" | **RECORDED** — Gen-2 battery gains this cell family in any revision |
| IF-1 severity | UPGRADED per reviewer: not a defect recurrence but the absence of a reliable requested-vs-executed distinction in the API; requested->effective equality/rejection must be a RELEASE-BLOCKING invariant before the experimental surface expands | **ADOPTED** — upstream requirements updated |

## D14_M1_REQUIREMENTS (upstream, consolidated)
R1 RELEASE-BLOCKING invariant: every configurable field either changes the
   effective configuration or the request is rejected 422; creation records
   carry requested_config, effective_config, effective_config_hash.
R2 Site-addressed intervention endpoint per the reviewer's contract
   (coordinate_system/site/rule; server rejects uncertifiable interventions;
   response carries requested+effective spec, ids+genotype_addrs, exact diff,
   per-case parent/child output hashes, optional trajectory hashes, typed
   faults, aggregate consequence, seeds, event_seq, release identity).
R3 Opt-in persisted search-physics pairs; 3-tier retention (lineage forever;
   genotype+consequence for preregistered experiments forever; traces tiered).
R4 Per-response release identity header + ledger events.
R5 behavior_distance(artifact_a, artifact_b, battery_id, metric_id,
   metric_version) as a versioned first-class primitive.

---

# D-14 external review #2 (second reviewer) — dispositions (2026-09-01)

Received via operator. Adjudicated against review #1 and the freeze; where
the reviewers conflict, the freeze and the declared estimand govern.

| item | reviewer-2 position | disposition |
|---|---|---|
| "Epistemically compromised; demand 64-case battery now; exhaustive coverage mandatory" | Abort/upgrade mid-experiment | **DECLINED for D-14, ADOPTED for weight**: changing battery or sampler mid-run is exactly the outcome-contingent modification the no-rescue rule forbids. A2 completes as frozen; its verdict is BOUND to the narrow estimand (review-1 Q4 wording) and its evidential weight is explicitly conditioned on B1+B2. Reviewer-2's demands are the B1/B2 acceptance criteria, not amendments. |
| Comparator "strictly a lower bound; middle mass artificially depressed" | | **PARTIALLY CORRECTED, then adopted**: pointwise I_final <= I_traj is TRUE (final-differs implies trajectory-differs). But the induced bias on middle_mass is NOT signed a priori: true-middle sites can read 0 under I_final (depressing) AND true-high sites can read middle (inflating). The 2x2 bridge table measures both flows; the dangerous cell stays traj-changed/final-unchanged. Recorded precisely. |
| 8-case quantization ("binomially, low-p sites often read 0") | | **ADOPTED** into the final packet's caveat wording (sampling, not rounding — but the practical point stands). B2 measures bin migration directly. |
| B1 size: 1,000 pairs + false-negative rate < threshold margin | vs reviewer-1's >=300 | **ADOPTED the stricter**: B1 = 1,000 paired artifacts, both comparators, 2x2 table + FN rate vs the 0.05 margin. FEASIBILITY GATE: trajectory comparison for PERSISTED artifacts must first be shown obtainable from the instrument (trace/limits/behavior-vector probe); if not obtainable, B1 is BLOCKED and that fact itself goes upstream (R5/behavior_distance + trace requirement) — a blocked bridge caps any SURVIVES at "comparator-relative". |
| Wasserstein vs matched synthetic control; trace-divergence depth | future statistic | **RECORDED** for successor prereg alongside review-1's G(t). |
| Q5 cellular-automaton controlled-spectrum family | vs review-1's three encodings | **MERGED**: CA is a legitimate (cheaper, analytically controlled) instantiation of the same causal design; D-15 candidate family = {CA rule-radius family, three-encoding family}; choice belongs to the D-15 freeze, not to taste today. |
| Q7 continuous relaxation / latent walks (incl. tensor-train genotype maps) | | **RECORDED**. Note for the record: Gen-0 killed tensor reps as a *reachability rescue on the existing substrate*; using them as a *designed encoding* is a different, legitimately motivated hypothesis and is not barred by that null. |
| Q13 temperature prediction (relaxation -> 0 collapses the band) | | **RECORDED** — a genuinely frozen-prediction-shaped successor claim. |
| Q14 leave-one-out operator court; Q15 D-9 as compression ratio (description-length accounting); Q16 internal-state hooks | | **RECORDED**; Q16 merges with review-1's injected-ladder into a two-sided calibration doctrine: prove the ruler sees a millimeter (injection) AND check internal-state shift vs output-identity (blunt-ruler detector). |
| Backend: /v0/artifacts/{id}/perturb single-transaction contract; divergence_step; X-Foundry-Release header with client fatal-on-deviation; 30-day trace-prune tier; /v0/physics/distance | | **MERGED into D14_M1_REQUIREMENTS** (R2 gains divergence_step + single-transaction wording; R3 gains the 30-day trace tier; R4 gains the header name and client fatal behavior; R5 gains the metric enum + divergence index). |

## Where the two reviewers agree (binding on the final packet)
1. Finish A2 under the freeze; the verdict adjudicates the frozen statistic
   under the default-operator estimand, nothing more.
2. A SURVIVES is weak/narrow until B1 (comparator bridge) and B2 (resolution)
   pass; a FALSIFICATION is informative as-is.
3. Requested-vs-executed configuration integrity is release-blocking upstream.
4. The interesting successor is causal encoding intervention, not a fourth
   observational substrate.

---

# D-14 external review #3 (third reviewer) — dispositions (2026-09-01)

The most demanding review; two findings are accepted as defects in MY freeze,
one claim is partially rebutted, and the run-grading question is resolved
across all three reviews.

| item | reviewer-3 position | disposition |
|---|---|---|
| 2.1 "Site identity fatal for variable-length programs" | byte offsets are not semantic loci across parents | **PARTIALLY REBUTTED, CONCESSION EXTRACTED**: the frozen estimand is over (parent, site) PAIRS — the freeze never claims cross-parent site identity or aligned loci, and the packet's ceiling already binds to that. Not fatal. BUT the embedded collider objection is CORRECT and is the review's real payload (next row). |
| 2.1b COLLIDER BIAS in A2 sampling | filtering default-operator outcomes on "single-site change" conditions on a post-mutation outcome; sampled sites may differ systematically from the site population | **ACCEPTED — the sharpest new objection across all three reviews.** Under the original I-L_strong sampler this could not arise (site chosen, then value); under default-operator filtering it does. Consequence: A2's estimand is conditioned on a collider, which grades A2 BELOW "narrow replication" — to PILOT grade. Adopted into the verdict wording (below). |
| 2.3 NO STATISTICAL INFERENCE PLAN | frozen rule is a point-estimate line in the sand; no CI, no parent clustering, ~8 sites/parent are not independent | **ACCEPTED AS A DEFECT IN MY FREEZE.** Gen-1/2/3 all used cluster bootstraps; D-14's freeze did not. Handling: the frozen A2 rule adjudicates as written (no-rescue cuts both ways — the adjudication cannot be changed after data in EITHER direction), and a cluster-bootstrap upper confidence bound is reported alongside as a labeled POST_HOC_DIAGNOSTIC. The A3 spec adopts the UCB rule (SURVIVES iff 95% cluster-robust UCB < 0.05; FALSIFIED iff LCB > 0.05; else INDETERMINATE) as its PRIMARY. |
| 2.4 "A2 contaminated; run a fresh A3; A1/A2 are pilots" | | **ADOPTED AS GRADING, DECLINED AS ABORT.** All disclosed facts support pilot-grading: A2's sampler was re-declared after observing A1, and the void A1 spectrum was seen. But aborting the 75%-complete frozen run buys nothing: its adjudication is legitimate FOR ITS OWN ESTIMAND, and reviewer-1 directed completion. RESOLUTION: A2 completes and adjudicates as frozen; its verdict is RECORDED AS PILOT-GRADE, not confirmatory; the confirmatory experiment is A3 on a repaired instrument (Phase 0-4), which requires M1 capability this seat can only file requirements for. |
| 2.5 threshold 0.05 / bin (0,0.25] untheorized | | **CONCEDED**; the numbers came from the D-13 channel convention (0.25) and a conventional margin (0.05). Full distribution ships regardless; A3's spec requires either a mechanistic derivation of the edges or shape-based reporting with the UCB rule. |
| 2.6 "influence must vary" gate too weak | degenerate distributions could pass | **CONCEDED for A3** (bin-occupancy gates >= 5% per bin adopted there); A2's frozen gate stands for A2. |
| 3.x A3 protocol (fixed-length parents or structural coordinates; 64-case battery; server-side comparator; exhaustive + uniform site sampling via site-addressed endpoint; mixed model / cluster bootstrap; power analysis via pilot overdispersion; bridging kappa >= 0.8 gate) | | **ADOPTED WHOLESALE as the A3 specification** (filed as D14_A3_PROTOCOL_SPEC; cannot run until Phase 0 instrument work lands upstream). |
| Roadmap Phases 0-6 | instrument hardening -> protocol freeze -> pilot calibration -> main run -> adjudication -> causal encoding (D-15) -> spectrum-to-search | **ADOPTED as the program roadmap**, merged with reviews 1-2 (D-15 candidate family: synthetic encodings / CA rule-radius / graded-opcode StackVM variant). Phase 6 is where the north star becomes operational; until then, spectrum results are substrate properties, not reasoning properties — wording adopted verbatim into the claim ceiling. |
| Q1 bridge minimum (50 pairs, kappa, false-zero rate; >10% false-zero disqualifies output hash) | vs review-2's 1,000 | B1 keeps the 1,000-pair size (strictest), ADDS the kappa >= 0.8 and false-zero <= 10% acceptance criteria. |
| "Connection to north star is rhetorical, not operational" | | **CONCEDED AND ALREADY BOUND**: the packet's own ceiling says a verdict "says nothing about reasoning, search improvement, or cross-substrate transfer". The operationalization is exactly reviewer-1/3's court-for-operators (reach expansion under matched compute with ablation) — recorded as the Gen-4 spec. |

## Tri-review synthesis (now binding)
1. A2 completes under its freeze and adjudicates its own narrow, collider-
   conditioned, quantized, comparator-unbridged estimand. Its verdict is
   PILOT-GRADE by unanimous reviewer weighting.
2. The confirmatory experiment is A3: repaired instrument (Phase 0 = the
   D14_M1_REQUIREMENTS, now release-blocking), fixed-length or structurally
   addressed sites, 64-case battery, server-side comparator, uniform +
   exhaustive site sampling, cluster-robust UCB adjudication, powered via
   pilot overdispersion. A1/A2 supply the overdispersion and exclusion-rate
   estimates -- their honest final role.
3. B1 bridge: 1,000 pairs, 2x2 table, kappa >= 0.8, false-zero <= 10%.
4. D-15 (causal encoding) follows a confirmed A3, not A2.
