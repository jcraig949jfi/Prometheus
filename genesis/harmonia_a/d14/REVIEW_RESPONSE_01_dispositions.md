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
