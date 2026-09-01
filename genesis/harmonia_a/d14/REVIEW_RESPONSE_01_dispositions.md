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
