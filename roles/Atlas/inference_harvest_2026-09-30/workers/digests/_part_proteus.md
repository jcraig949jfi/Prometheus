# Proteus seat digest (Atlas part, 2026-09-30)

Tags: **RAN** = executed with receipt; **OBS** = number observed; **CON** = verdict quoted from a seat (author named); **ATLAS** = my hypothesis, not a seat claim. Repo = F:/Prometheus-worktrees/atlas-base-role @ origin/main 2026-09-30. `comms #N` = comms_since_0925.txt message id.

## Coverage

- Read: roles/Proteus STATUS v0_3/v0_4/v0_5/closure, V0.6 final packet (s.A, G1-G3, verdict ledger), journal 2026-09-18, NOTE_WITNESS_CASE_COLLAPSE; proteus/round2 (PROTEUS-46 prereg + result + falsifier_46.py walks), ANATOMY_L0 head; proteus/graph/GRAPH_ORGANISM_V1.md; proteus/eval/fingerprint.py header; proteus/v0_7 result keys; operator ruling 02_... G6-0; Harmonia RULING_PROTEUS_CURRENT_INSTRUMENT + VACUOUS_READINGS V-008; archaeon/frontier/suppressions/PROTEUS-46.json; Artemis D001 DIGEST, D002/D004 RESULT; comms grep (23 hits).
- Not read: v0/v0.1/v0.2 build packets in detail, V0.6 sections C-M, ROUND_2 design doc body, proteus/repb, contracts, CONSUMER_SURFACE_V0_6, HARMONIA_HANDOFF, journals 09-16/09-17.
- Seat state: **last Proteus commit 6a98ef0bb (2026-09-18)**; no proteus/ code change to HEAD (CON Artemis, roles/Artemis/dispatch/D001/DIGEST.md:43 @167327233). All later Proteus-relevant science is by other seats (Artemis, Archaeon, Harmonia, Odysseus).

## Experiment ledger (most recent first)

| id | date | question | substrate | ruler | controls | n | OBSERVED | CONCLUDED | status | pointer |
|---|---|---|---|---|---|---|---|---|---|---|
| D004-04 (Artemis) | 09-30 | MDC of v0.5 kernel-current instrument; does current bias selection? | v0.4 grammar kernel | injected-current recovery | injected currents | n/r | full recovery at 1e-4, 75% at 3e-5, ~0 at 1e-5; max delta_L .004 instr | CON Artemis: "MDC = 1e-4 ... instrument CAN certify profiles at that level"; bias INDETERMINATE | RAN | roles/Artemis/dispatch/D004/RESULT.md:14 @0b0759dba |
| D002-03q (Artemis) | 09-30 | Can neutral drift cross the PROTEUS-46 cliff? (quick mode) | graph_grammar.v1 | two_key score | control drift, 'strict' mode | 50 walks x 300 steps | 5-edit duplicate-and-diverge path: 4 steps NEUTRAL (3/6) then 6/6; both single fixes 0/6; drift 'score' 1/50 hit (step 188) vs control 0/50, strict 0/50; pop 50x100 gens never 6/6 | CON Artemis: "the cliff IS crossable by a neutral path in principle"; "drift helps" NOT shown | RAN (full 500x3000 run timed out, 0 bytes) | roles/Artemis/dispatch/D002/RESULT.md:20,22 @ae043e65f; comms #1116, #1121 |
| S3 (Odysseus) | 09-27 | Is HEPH-32's "0/5,472 edits improve" (Proteus/WSE cliff) a cliff? | v0, C4-01 a02 children | eligible-edit outcome | eligibility filter | 1,568 eligible of 5,472 | 0 improved, 61.7% neutral, 4.7% deleterious, 33.6% lethal; rule-of-3 UB .0019 | CON Odysseus: "a large neutral plateau with no uphill single-edit neighbour, not a cliff" | RAN | comms #750; roles/Odysseus/frontier/poi/spikes/S3_mutational_cliff/RECEIPT.md @d53c189eb |
| PROTEUS-46 | 09-18 | Does connectivity grammar change search geometry around the v0.4 cliff? | v0.4 vs graph_organism.v1, hand-written one_value (3/6) + keyed (6/6) parents | two_key probe (0..6) | 2 seed batches as noise floor; identity children excluded | K=400/op; 4,267 v0 / 4,881 graph children (one_value) | USEFUL 0 vs 0; GRADED .0075 vs .0006 (floor .0028); DESTR .7047 vs .3567; NEUTRAL .2740 vs .6417; walks random 0/200 both, greedy 0/100 both, best seen 3 | CON Proteus: "CLIFF_SURVIVES -> FALSIFIER_FAILED ... SAFER ... not more GRADED ... the claim 'connectivity removes the cliff' is dead" | RAN, prereg eb58691fc, "departures: none" | proteus/round2/PROTEUS-46_FALSIFIER.md:3-13,79-83 @6a98ef0bb; GRAPH_ORGANISM_V1.md:79-90 |
| PROTEUS-45 behavior_fingerprint.v1 | 09-18 | T0 row for both substrates under C6 envelope | v0 + graph | row reproducibility, cap <=1 KiB | reward-leak keys refused; sensitivity | 40/40 | 40/40 reproducible both substrates; v0 cannot separate PUTs to different keys | CON Proteus: "KNOWN LIMIT (graph rows separate them)" | RAN (tests) | journal 2026-09-18:71-84 @6a98ef0bb; proteus/eval/fingerprint.py:20-23 @b3d27cbda |
| PROTEUS-43 graph_organism.v1 build | 09-18 | New runtime where structure = connectivity | graph (25 node kinds, 13 ops) | R4 drift band abs<=0.02 nodes/step | 3 seeds no selection; witness echo leaky/honest | 3 seeds x 100 org | drift -0.0023/+0.0016/-0.0069; earlier masses .06/.12 -> -0.026, .08/.10 -> +0.006/+0.019 (rejected); witness 12 nodes/72 ops 6/6+16/16 | CON Proteus: "GRAPH_ISA_EXPRESSES_KEYED_MEMORY"; "NO world has run it" | BUILT | journal 2026-09-18:44-69; GRAPH_ORGANISM_V1.md:12,64-68 |
| PROTEUS-37 ANATOMY_L0 | 09-18 | Structural differences between Archaeon specimen strata | v0 specimens (11/15/23) | 24 stats, permutation floor 20,000 | UNCORRECTED floor, 24-way correction | 49 | best: tick_budget p .0062, n_regs p .0008 (delay vs shelf) | CON Proteus (commit msg): "none past 24-way correction" [delay-vs-shelf n_regs .0008 < .05/24=.0021 appears to pass -- ATLAS: recheck] | RAN | proteus/round2/ANATOMY_L0.md:10-12,34-35 @e11e22370 |
| G5 remint | 09-18 | Population digest checkout-invariant | 57-member C4 pop | canonical digest | CRLF vs LF test | 57 | raw a3f9816f (CRLF) vs 3c2ebfd9 (LF); canonical 7f03cc82 | CON: defect was hashing raw checkout bytes | REPAIRED | journal 2026-09-18:3-21 |
| Witness-case collapse | 09-10 | Why all 35 witnesses land on cases 4-7 | cegis_boolean_v1 (Vivarium) | first-mismatch case index | reproduction vs publish receipt | 24 tasks, 35 witnesses | case_index {4:16,5:9,6:5,7:5} | CON Proteus: "a certainty, not a tendency" -- K=4 seed probes = cases 0-3 in same order as scan | RAN | roles/Proteus/NOTE_WITNESS_CASE_COLLAPSE_2026-09-10.md:30-60 @5dc8b3e40 |
| V0.7 closure studies | 09-04/05 | specimen/ablation/meter/transcript readiness | v0 64 specimens | several | size-matched meter floor | 64 | meter size_matched_rate .775 METER_DISCRIMINATES_BEYOND_SIZE; ablation confounded .0029 (1/343); transcripts: only 10/64 players emit >=1 value, largest class .6094; segment players 4/56 | CON Proteus: "'A+B == A' is a property of the instrument and NOT evidence about composition" | RAN | proteus/v0_7/RESULT_*.json @6be6103f1 / c8f848c65 |
| V0.6 full-space nonequilibrium | 09-03/04 | Is structural kernel detailed-balanced on full space? | v0.4 grammar, 2,044 states | cycle affinity, entropy prod, row TV | 2 independent kernels; closure probe 817,600 proposals, 0 escapes | 20,000/state/kernel | median row TV .0080 (limit .010); |J| total 3.4945e-02; zeroing dominant op: entropy -89.7%, affinity spread -2.5% | CON Proteus: "NOT_QUALIFIED_AUTHORED_NONEQUILIBRIUM_CURRENT"; "OPERATIONAL_SIGNIFICANCE_NOT_YET_ADJUDICATED" | RAN | PROTEUS_V0_6_FINAL_EXTERNAL_REVIEW_PACKET.txt s.A, ledger A7/A8 @b9128d8f3 |
| V0.5 equilibrium/confirmation | 09-03 | Replicate v0.4 halt/yield; detailed balance on 124 states | v0.4 | global Holm 350 cells; |J| vs MC floor | reversible reference | 50,000/state | halt/yield -0.0191 -> +0.0118 (p .9716); 0/350 survive; 166/506 pairs above floor 4.16e-05; max |J| 2.45e-04; sigma 9.97e-03; occupancy TV .0198 vs "floor ~.019" | CON: "V0_4_CONTENT_DISCOVERY_NOT_REPLICATED"; "STRUCTURAL_KERNEL_NONREVERSIBLE_AUTHORED_CURRENT_DETECTED" | RAN | STATUS_2026-09-03_v0_5.md:7-29 @fe27309f4 |
| V0.4 reversibility | 09-03 | Remove tape ratchet; reversibility | v0.4 grammar, 2,044 states | exhaustive blocked-shrink count; NC5 symmetric walk | NC5, two content nulls, dual Holm | 5 cohorts | blocked shrinks v0.3 510 -> v0.4 0; tape +1.18 -> -0.17; class_halt_yield -0.0191 z 3.53 @128; 16,172 asymmetric length-edge pairs | CON: "NOT_QUALIFIED_DIRECTIONAL_MUTATION_PRIOR_REMAINS"; "HISTORICAL_V0_LENGTH_FAILURE_RECLASSIFIED_AS_JOINT_GEOMETRY" | RAN | STATUS_2026-09-03_v0_4.md:3-47 @ccc5c8287 |
| V0.3 neutrality | 09-03 | Directional prior under neutral mutation? | v0.3 grammar | drift vs symmetric bounded null | reflected-walk geometry control; 6 ensembles | 10,000 neutral mutations | config_log2_tape_words +1.18 (c128), +0.48 (c256); NOP-share drift .133 -> <=.0299; Jaccard .9886-.9993 | CON: "NOT_QUALIFIED_DIRECTIONAL_MUTATION_PRIOR_REMAINS"; half-tape rule "blocks shrinking and never blocks growing" | RAN | STATUS_2026-09-03_v0_3.md:3-21 @c74ed8c1a |

## Mechanisms

| mechanism (seat words) | claimed level | judged level | synonyms / notes |
|---|---|---|---|
| "a flat genome has no PART -- a functioning structure is a set of addresses whose meaning depends on position" (Proteus) | design rationale | ATLAS: supported only indirectly (C4-04 insertion/movement break routing); the connectivity fix did NOT remove the cliff | position-encoding, addressing damage |
| "the one-value -> two-value step is a coordinated change with no intermediate the probe can see" (Proteus) | CONCLUDED from greedy 0/100 | WEAKENED: Artemis found 4 NEUTRAL intermediates on a 5-edit path; greedy rule cannot accept neutral steps | epistasis, coordinated edit, valley |
| "dormant-attach operators are neutral by construction" (Proteus) | OBS (5 ops 400/400 NEUTRAL) | confirmed by Artemis C5: 2,000 of 3,132 graph NEUTRAL from those 5 ops | "SAFER" = neutral inflation by construction |
| authored nonequilibrium current: irreversibility is a property of the MIXTURE of directional operators; weights set magnitude not existence (Proteus A7/A8) | CONCLUDED | admitted as detector only (Harmonia HARM-44); source of existence U2 unresolved | circulation, detailed-balance violation, directional prior |
| length ratchet = joint geometry (R2) | RECLASSIFIED | stands; two grammar revisions made on false reading, the 2nd created real tape ratchet (A2) | geometry vs authored prior |

## Failures / invalidations

| item | LOST | SURVIVES | pointer |
|---|---|---|---|
| "connectivity removes the cliff" | claim dead (CON Proteus) | graph profile as substrate; 4 reopen conditions; neighbourhood_exhausted False | PROTEUS-46_FALSIFIER.md:85-89 |
| "no intermediate the probe can see" | as reachability claim (Artemis D002-03q) | zero USEFUL single edits (both substrates); single fixes 0/6 | D002 RESULT:20 |
| v0.4 halt/yield discovery | falsified F1 (opposite sign) | kept in record | V0.6 ledger F1 |
| analytic kernel | retired F2 (median TV .0162, max .1661 vs live) | live kernel | V0.6 ledger F2 |
| "max cycle affinity 3.0007 nats" | withdrawn W1 (0.3178 on 2nd kernel, top-1 shrinkage 89.4%) | affinity distribution (sd 1.1234, S/N 2.32) | V0.6 ledger W1 |
| V0.3 Holm | inert; would publish 20 coords not 1 (A4) | fixed + dual implementation aborting on disagreement | V0.6 ledger A4 |
| V0 "string layer PASS" | predated export.py (A5) | atomic audit identity | V0.3 STATUS:34-36 |
| commit cite d5185d092 | unreachable (rebased away) -> aafce2bd2 (F3) | -- | V0.6 ledger F3 |
| V0.5 "does not move occupancy" | Harmonia V-008: TV .019747 sits on a quoted-not-computed floor ~.019 -> vacuous | direction tallies .9356 vs .9969 (~275k each) DO answer | roles/Harmonia/VACUOUS_READINGS.md:56 @f2c2452ea |
| V0.5 byte-identical replay | CPython 3.12 sum() compensation -> 1e-14 diffs | V0.6 two-layer contract with math.fsum (S2) | V0.5 STATUS:34 |

## Rulers

| ruler | owner | audit | status |
|---|---|---|---|
| two_key probe (0..6) + all_keys (16) | Proteus | hand-written parents at 3/6; quantized: no 4/5 ever seen | coarse; ATLAS: 3-level plateau hides graded gains (cf. Archaeon Q2 "finer distance cliff->slope", D001 H-D1-24) |
| greedy 3-step walk (width 50) | Proteus | Artemis C2: key (two,-ops) vs incumbent (cur,0) -> neutral child with ops>=1 never accepted | structurally blind to neutral paths (falsifier_46.py:117-131) |
| v0.5 kernel current (|J| vs MC floor) | Proteus | Harmonia HARM-44: detector yes, absence no ("today the instrument has no X"); reversible-reference check "could not fire on any input" | Artemis D004-04 supplies MDC 1e-4 (partial repair of "no X") |
| behavior_fingerprint.v1 | Proteus | 40/40 repro; reward keys refused | v0 blind to written addresses |
| graph detectors (Archaeon C6) | Archaeon | graph 1 event/192 evals vs v0 ~30% at same thresholds | operator: do NOT recalibrate; UNABLE for structural reuse (02_OPERATOR_RULING:22-26 @eb58691fc) |
| transcript as composition ruler | Proteus | 10/64 emit a value | degenerate: A+B==A is instrument property |
| organism_id | Proteus | pins BYTES not EXECUTION | cite registry entry_id (RESULT_REGISTRY_IDENTITY.json) |

## Repairs

| repair | what changed | outcome moved? |
|---|---|---|
| v0.3 -> v0.4 tape rule | blocked-shrink 510 -> 0 | tape coordinate +1.18 -> -0.17; verdict unchanged (new blocker halt/yield) |
| global Holm (v0.5) | family = coordinate x cohort | 2 would-be discoveries rejected prospectively; 0/350 |
| full-space kernel (v0.6) | 124 -> 2,044 states, n 20,000 | phenomenon confirmed (|J| 2.84e-02 -> 3.4945e-02); verdict hardened |
| graph masses | .06/.12 and .08/.10 rejected -> .07/.11 | drift into band; runtime hash moved twice (grammar in runtime sources) |
| G5 canonical digest | raw -> canonical | manifest_hash unchanged 2dfc1c5d; gate went GREEN |
| PROTEUS-46 semantics | "retire under A" -> FALSIFIER_FAILED + reopen | Archaeon suppression covers only C4-cliff.T1 |

## Primitive-level interventions

| primitive | intervention | outcome |
|---|---|---|
| encoding | flat position genome -> connectivity graph (PROTEUS-43) | cliff survives; neutral share .27 -> .64, destroyed .70 -> .36; useful 0 -> 0 |
| locality | v0.4 ops act on contiguous k in [1,4] aligned instructions (MUTATION_GRAMMAR.md:10-12); graph ops act on edges/subgraphs | no scattered-vs-contiguous damage test in Proteus. ATLAS: per-op table shows v0 contiguous-block ops (region_swap .995, deletion .97, movement .9718 destroyed) far worse than point ops (operand_perturbation .354) -- consistent with Nestor/Archaeon locality law but NOT tested as such |
| copying / duplication | v0 duplication; graph SUBGRAPH_COPY(_ATTACH) | graph copy 100% neutral (dormant attach); Artemis path to 6/6 is "duplicate-and-diverge" -- copy is the route, not a failed operator |
| heredity | lineage_record.v1 = parent + edit list, replay 300/300, tampered refused | integrity only; no world ran |
| write authority | code_writable 34/64 specimens; ANATOMY code_writable delay vs shelf .727 vs .304 (p .0295 uncorr) | not intervened |
| selection | none in any Proteus experiment (all neutral/no-selection) | C4-08 (Archaeon): selection builds LENGTH and neutrality |
| mutation weights | zero dominant operator | entropy production -89.7%, affinity spread -2.5% |

## Buried signals

1. **Reachability masquerading as physics** (ATLAS, strong): PROTEUS-46's walks were 3 steps and greedy rejects ties; the only noticed route is 5 neutral-then-up steps. "Cliff" is a claim about the search policy + horizon, not the landscape. Artemis D002 is the correction; Proteus inactive since 09-18 never answered.
2. **Suppression cannot self-lift** (ATLAS): PROTEUS-46.json `lifts_when neighbourhood_exhausted==true -> retirement_candidate_A`; no path to *executable* except reopen; with Proteus inactive, C4-cliff.T1 produced 299,991 identical BLOCKED rows = one decision (comms #735, Archaeon).
3. **Hand-written vs evolved parent** (ATLAS): C3-SFE-02 on evolved v0 shelf organisms = 0.64 neutral / 0.36 destructive, 1/4,800 useful (archaeon/campaign3/CAMPAIGN_REPORT.md:120-124 @cb9135104); PROTEUS-46 hand-written v0.4 = .27/.70, 0 useful; graph = .64/.36. The graph's "safer" split equals what evolution already gave v0 (length/neutral padding). The v0-vs-graph contrast may be parent choice, not representation.
4. ANATOMY_L0 delay-vs-shelf n_regs p .0008 is below 0.05/24 = .0021 yet commit says "none past 24-way correction" (ATLAS: check whether correction was per-pair or across 3 pairs x 24 = 72 -> .00069, which it would fail).
5. Transcript degeneracy (10/64 emitters) predates many composition claims fleet-wide.
6. Keyed-parent v0 insertion/duplication GRADED .19/.18 vs graph NODE_KIND .072: v0 is MORE graded from the 6/6 parent -- graded-ness is parent-dependent.

## Contradictions and cross-engine hooks

| A | B | nature |
|---|---|---|
| Proteus: "no intermediate the probe can see" | Artemis D002-03q: 4 neutral intermediates, 5 edits | reachability vs landscape; greedy tie rule |
| Proteus prereg s5: improvement "two edge retargets away by construction" | Artemis: both single fixes 0/6 | 2-edit path goes through a 0/6 valley; neutral route is longer |
| HEPH-32 "cliff" | Odysseus S3 "neutral plateau, not a cliff" | same zero, different shape/denominator |
| Archaeon C4-01/02 "cliff at every radius" (cited in GRAPH_ORGANISM_V1.md:18) | Nestor CW01 cycle 5: fixed-count damage rulers manufacture claims; scattered > contiguous (locality law, T-ARCH4) | ATLAS: C4 damage radius ruler should be re-audited under the qualified Bernoulli(f) ruler before the cliff premise is reused |
| Harmonia HARM-44 "no X" | Artemis D004-04 MDC 1e-4 | partial repair; absence admission not yet re-ruled |
| Archaeon graph detectors 1/192 vs ~30% | operator: substrate-conditioned rulers later | open hook for Harmonia geometry validation |
| Vivarium cegis_boolean_v1 seed probes | Proteus witness-collapse note | harness order = scan order -> witness region forced (instrument, not phenomenon) |
| Nyx #1070 THEO-REQ-003: interface is Proteus's | Proteus inactive | owner gap for composition organ interface |
