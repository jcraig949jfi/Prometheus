# Theophrastus -- forensic dossier (Sisyphus crawl)

Seat: Theophrastus
Crawl date: 2026-10-01
Worktree base SHA: 19299e06b (origin/main at crawl time)
Crawler: Sisyphus worker (Opus 5.5), read-only

Coverage statement.
READ: roles/Theophrastus/ CHARTER.md, RESPONSIBILITIES.md, STATUS.md, BACKLOG_H0H5.md (whole);
REVIEW_PACKET_FOUNDING_2026-09-13.txt (whole); REVIEW_PACKET_ROUND2_2026-09-14.txt (s1-s23); founding charter verbatim
(first ~60 lines); journal headers (host/instance); specimens/SPECIMENS_ROUND2_2026-09-14.md (SPEC-001 head);
crucible/theo14/THEO14_RESULT.json (parsed); ledger line counts. Code: theophrastus/adapter.py (head),
ecology.py (head), crucible.py and controls.py (function index); file sizes for all 13 modules. git log of
theophrastus/ and roles/Theophrastus/ (15 own commits, 2026-09-13..14). Code-location search:
`git grep -il theophrastus` outside roles/ with holdout/secret exclusions. Cross-seat: comms #239-#252 (own),
#268-#311 (replies to REQs), #322 (Archaeon WSE delegation), #1013 (Artemis Fabric Q7), #1070 (Nyx REQ-003 reply),
#1227 (Achilles); Atlas inference-harvest mentions (REGULARITIES, VERIFY_SYNTHESIS_2, atlas_index_and_history);
docs/fleet/FLEET_CENSUS.md row; MWO-0001/0002 mentions.
NOT READ: PREREG_FOUNDING_CRUCIBLE, ROUND2_DISSECTION_PLAN, PREREG_THEO14 bodies; FOUNDING_ROUND_REPORT beyond grep;
recon/CAPABILITY_MATRIX; reqs/*.md bodies; INBOX_* files; per_ic*.jsonl data; cell.py/contrast.py/curves.py/
dissect.py/round2.py/cross_consumer.py bodies; tests. The adapter reads an SFE token from a gitignored local file
and a PEW bearer from evidence_wiki/config.json; neither was opened.

---

## 1. Identity and purpose

Canonical name: Theophrastus. Instance: m1-af618b77 (both journals). [HIST]

Host: M1, not M2. The founding and round-2 journals are headed "instance m1-af618b77"; the adapter's default worker id
is "theophrastus@m1"; SFE engine eng_8a37a5d3 and PEW at 192.168.1.202 are on M1. Worktrees theophrastus-founding
and branch theophrastus/round2-2026-09-14. [HIST + IMPL adapter.py] (The crawl brief's "likely M2" does not hold for
this seat.)

Charter: operator founding charter 2026-09-13, verbatim at roles/Theophrastus/prompts/2026-09-13_founding_charter/
PROMPT_verbatim.md (sha256 00b8916b...). "Your subject is not algorithms. Your subject is COMPUTATIONAL ADAPTATION."
Explore MECHANISM x PRESSURE x WORLD x EVOLUTIONARY BRANCH x INTERVENTION on the same SFE + PEW substrate that
Archaeon and Vivarium use, looking for reversals, gradients, interactions, discontinuities, dormant mechanisms, regions
where Prometheus's representation fails. "Your output is not discovery. Your output is REPRODUCIBLE SIGNALS FOR OTHER
SEATS TO INVESTIGATE." [INTENT]

Operational reading (RESPONSIBILITIES): primitive object = CONTRAST(A, B) between replayable cells, never SCORE(A);
closed dispositions NO_SIGNAL / WEAK_SIGNAL / REPRODUCIBLE_SIGNAL / REPRESENTATION_BLOCKED / INSTRUMENT_BLOCKED;
three traversal modes (coverage, local expansion, counterfactual attack) instrumented not weighted; LLMs may propose,
never select; ten constitutional self-controls. [INTENT]

Second directive: 2026-09-14 "round 2 harvest the mechanism" (prompts/2026-09-14_round2_harvest/). [HIST]

Active span: 2026-09-13 to 2026-09-14 only (15 commits). No Theophrastus-authored commit after 6d72d1d19
(2026-09-14). FLEET_CENSUS lists the seat DORMANT, last activity 2026-09-14. [HIST/IMPL git log]

Terminal role: de facto dormant; STATUS still says ACTIVE (currency 2026-09-14). No parking or closure record exists.
Achilles (#1227) notes INHERITANCE.md has no Theophrastus entry-file row. MWO-0001 s10 and MWO-0002 list Theophrastus
as a lane with "no change". [HIST]

Relationships: consumer of Vivarium's SfeRunner and kind ca_density_v0, of Herakles's EvCA library (herakles/evca:
genomes, core, later derive.py), PEW (Mnemosyne), Harmonia's SFE conformance gate. Issued six change requirements
(THEO-REQ-001..006) to Mnemosyne, Vivarium, Proteus, Herakles. Recipient of: Archaeon's WSE survey delegation (#322,
09-16), Techne's MKW-1 freeze request (#311), Harmonia/Nyx ASAL broadcasts, Ares's cycle-2 export (#539), Artemis
Fabric findings (#1013), Nyx's REQ-003 reply (#1070, 09-30). None answered by Theophrastus. [HIST]

## 2. Engine / system inventory

Theophrastus built no world and no organism. It built an EXPLORER/CONTRAST HARNESS over an existing engine.

| component | path | role |
|---|---|---|
| cell model | theophrastus/cell.py (241) | content-hashed cell = (mechanism, pressure, world, branch, intervention, repeat), UNKNOWN never defaulted; spec_hash and execution_hash |
| founding ecology | theophrastus/ecology.py (143) | 4 mechanisms (maj, GKL, exp, par rule hexes asserted against herakles/evca/genomes.py), 4 worlds, 3 pressures, 2 branches, interventions NONE/REFLECT |
| controls | theophrastus/controls.py (220) | C1-C10 self-controls (duplicates, alias, changed world, branch without evidence, no-op, nondeterminism, provenance, stale reuse, LLM-in-selection, budget), selection modes, signal admission |
| contrast | theophrastus/contrast.py (131) | p_A - p_B with SE; z-rule |
| adapter | theophrastus/adapter.py (148) | cell -> Vivarium ExecutionRequest -> viv.runner.SfeRunner (as a library) -> SFE engine -> PEW fossil (namespace "theophrastus") -> ledger row |
| crucible | theophrastus/crucible.py (318) | batches, coverage/replicate/replay phases, scoring, queue_or_kill, report CLI |
| ledger | theophrastus/ledger.py (72) | JSONL ledgers rows/cells/contrasts/signals/dead |
| dissection | theophrastus/dissect.py (115), curves.py (151), round2.py (266) | offline per-IC re-derivation of fossils, signed-margin response curves, round-2 scoring |
| cross-consumer | theophrastus/cross_consumer.py (128) | THEO-14 re-derivation of Vivarium bench fossils |
| tests | theophrastus/tests/test_controls.py (249) | 19 tests (round-2 packet) |
| data | roles/Theophrastus/ledgers/*.jsonl (rows 67, cells 167, contrasts 123, signals 46, dead 5), crucible/round2/per_ic*.jsonl (29,800 + 16,000 per-IC rows), crucible/theo14/ | |

Execution model: on-demand CLI batches against a live SFE engine on M1 with a hard budget (45 executions / 3600 s
founding); offline re-derivation via herakles.evca.core. Scale: 46 founding executions + 21 round-2 executions (67
rows), each 800 ICs (founding) per cell; offline 59 fossils re-derived; THEO-14 150 bench fossils. [HIST]

## 3. Architecture

World: Vivarium kind ca_density_v0 -- the classic 1D binary cellular-automaton density classification task (radius 3,
128-entry rule table, odd ring of N cells, run for a fixed number of steps; success = converge to all-ones iff initial
density > 1/2). Worlds are (N, steps): W149 (149, 320), W599 (599, 1198), and horizon neighbours. [IMPL ecology.py]

Organism/mechanism: a FIXED rule table taken from the literature via Herakles: maj (majority, hand-designed), GKL
(Gacs-Kurdyumov-Levin, hand-designed), exp and par (GA-evolved, 1993-95, Mitchell/Crutchfield/Das lineage), plus
particle1 in round 2 as held-out. No genotype search, mutation, reproduction or learning is performed by Theophrastus.
[IMPL]

"Pressure": the initial-condition ensemble -- P_iid (unbiased Bernoulli), P_unif (10-density grid), single densities.
This is a measurement distribution over test inputs, not a selective pressure acting on a population. [IMPL;
CODE-INFERRED interpretation]

"Branch": a provenance label (hand_designed vs ga_evolved_1993_95) with evidence pointer to genomes.py; ancestry
recorded UNKNOWN. "Intervention": NONE or REFLECT (mirror table and ICs). [IMPL]

Data flow: SOURCE (genomes.py) -> REPRESENT (cell.py) -> PROPOSE (fixed preregistered list) -> control checks ->
EXECUTE (SFE via Vivarium runner) -> FOSSIL (PEW) -> ROW -> CONTRAST -> admission/queue/kill. [HIST founding report]

Design vs implementation: the charter's combinatorial space (mechanisms from many eras, Techne/Nyx organs, multiple
kinds) was realised as one kind, four (then five) CA rules, two world sizes and IC ensembles. The traversal modes
exist in select() but the founding/round-2 cells were a fixed preregistered list; the counterfactual mode was never run
(THEO-09 blocked on THEO-08). [IMPL + HIST]

## 4. World capability audit

- State: a ring of 149-999 binary cells; deterministic CA dynamics; stochasticity only in the IC draw.
- Spatial: 1D ring. Observation/action: none in the agent sense; the "organism" is the global update rule.
- Horizon: 320-1286 synchronous steps. No adversaries, agents, resources, ecology, environment change, task diversity,
  world generation or open-endedness. One task (density classification), a well-known benchmark since the 1990s.
- Toy assessment: a narrow, fully characterised benchmark; the seat's measurements reproduce published accuracies
  (within 2 SE for all eight P_iid cells). It is useful as a calibration bench, not as an arena where new machinery
  could arise. [HIST + CODE-INFERRED]

## 5. Organism capability audit

A radius-3 binary CA rule is a fixed 128-entry lookup table applied in parallel everywhere; it has no memory beyond
the lattice, no learning, no self-modification, no reproduction. Within Theophrastus nothing evolves. The capability
question "could this organism exhibit a nontrivial reasoning primitive" does not apply in the usual sense: the
organisms are fixed historical specimens, and the seat's job was to probe them, not to evolve them. Known CA phenomena
(particle/domain computation in GKL/exp/par) exist in the literature; the seat did not instrument particles. [IMPL +
CODE-INFERRED]

## 6. Search and pressure mechanism

No search over organisms. "Novelty" is produced by the explorer's choice of cells and contrasts. Founding: 25
coverage cells + 16 replication + replay; round 2: 20 planned cells (single-density inversion, horizon attenuation,
transport to a held-out rule, N=999 scaling). LLM proposals: allowed by charter, tested as not influencing selection
(C9); no record of LLM-proposed cells in the crawl sample. Bottleneck: SFE execution cost (round 2: 21 executions
in 315.8 s adapter wall; ~40 s per cell estimated at N=999 in THEO-03), budget caps, and dependency on other seats' REQs (005 table-level intervention, 006 exact-count ICs)
for the next steps. [HIST]

## 7. Measurement / ruler stack

- Contrast z-rule: NO_SIGNAL |z| < 2; WEAK 2 <= |z| < 4 or failed replication; REPRODUCIBLE |z| >= 4 in both passes
  with same sign; INSTRUMENT_BLOCKED on any failed side. SE_D <= 0.025 with 800 ICs per cell. [HIST]
- Positive controls: published accuracies and Herakles's independent offline C1-e reproduction. [HIST]
- Ten self-control cheats (C1-C10) plus CHEAT-SIGNAL; round 2 CHEAT-A (perturbed seed) and CHEAT-B (wrong rule's
  curve). Two explorer defects found by the cheats before live cells (alias keyed on spec_hash; wall budget
  under-count). [HIST]
- Round 2: per-IC re-derivation (bit-exact + mask digest), binomial z per 0.01 margin bin, per-cell predictions
  frozen before execution, harvest gate (SPECIMEN / BOUNDED / CANDIDATE). [HIST]
Known blind spots:
- The admission gate had no prior-evidence notion: 14 of 23 REPRODUCIBLE signals were positive controls the
  literature/record already predicted (packet s10; confirmed by Atlas VERIFY_SYNTHESIS_2 against the packet line).
  [CORRECTION, self-reported]
- Only 4-5 rules, one kind, one engine build.
- SPEC-001's core relation (success depends on IC only via its count k, under Bernoulli ICs) is "exact by
  exchangeability" (round-2 packet s21): its empirical pass is an instrument check, not an empirical finding. [HIST]
- Artemis Fabric Q7 (#1013, worker claim): SPEC-002 presents a failed preregistered prediction (exp W999 P_unif .7887
  vs predicted .8228) beside a "saturated 599 -> 999" statement, and the "all ones" collapse mechanism was asserted,
  never logged (final states not recorded). [HIST, unverified here]

## 8. Experiment inventory (campaigns)

### Campaign F -- Founding crucible (2026-09-13)
- Question: is a contrast-first ecological exploration loop real on the shared SFE+PEW substrate, and does its explorer
  catch its own failure modes?
- Cells: maj/GKL/exp/par x W149/W599 x P_iid/P_unif, plus REFLECT, horizon and criterion neighbours; 46 executions;
  41 contrasts in 6 families. Prereg 05ee51977; rows fcbbdd2da.
- Reported: LOOP IS REAL; 46/46 completed; replay identical n=3; all cheats caught; 23 REPRODUCIBLE (14 positive
  controls, 9 NEW_TO_RECORD, all "uniform-density regime at N=599"); 5 dead cells (maj under P_iid). Zero discoveries
  claimed. Signals THEO-SIGNAL-0001..0023.
- Later: round 2 retired the 9 "new" signals' interaction reading as ECOLOGICAL_CORRELATION_ONLY (= nominal-p
  parameterisation + rule-specific finite-size response). Atlas cites "14/23 signals are controls" as an R1-type
  regularity. Label: REPORTED POSITIVE (for the loop) / LATER OVERTURNED (for the novelty of its signals).

### Campaign G -- Round 2 mechanism harvest (2026-09-14)
- Question: what explains the founding P_unif x W599 contrasts? Seven competing explanations frozen (H1-H7).
- 21 rows (20 + 1 retry, 1 FAILED on a Vivarium validator off-by-one), offline 29,800 + 16,000 per-IC records.
  Plan 64e4189e7; Step A aa2d2d29d; harvest cd8d4c87c.
- Reported: SPEC-001 MARGIN_RESPONSE (specimen; H1 survives 8/8 + 2/2 held-out, "also exact by exchangeability"),
  SPEC-002 ONE_CLASS_COLLAPSE for exp (bounded: "published P_599/P_999 of exp are a constant classifier's"),
  CAND-003 maj boundary shift (stopped below binomial resolution); H4, H5, H3-absolute, H6-as-branch killed; transport
  of curve FORM across N holds, values do not (GKL W999 .7925 vs .7236 predicted).
- Later: Artemis Fabric Q7 (above); Nyx's REQ-003 reply (#1070) counts what a two-parent region-swap operator would
  produce on the six rules (par x GKL: 2550 distinct children), but no composition experiment was ever run.
- Label: MIXED.

### Campaign H -- THEO-14 cross-consumer re-derivation (2026-09-14)
- Question: does SPEC-001's offline instrument re-derive Vivarium's 150 bench fossils?
- Reported: 150/150 rows match bit-exactly (24/24 informative, 15 transformed); P2 cheat blind on a frozen all-zero row,
  caught 24/24 where eligible. Prereg 86abe4d69; result 1b067751f.
- Label: REPORTED POSITIVE (an instrument-validation result).

### Never run
THEO-02 interaction families prereg, THEO-03 W999 round, THEO-05 SFE comparison families, THEO-06 queue cross-consumer
probe, THEO-09 counterfactual mode, THEO-10 Nyx catalogue as mechanism source, THEO-11 exp table ablation (needed
REQ-005), THEO-12 boundary localisation (needed REQ-006), THEO-13 kind transport, THEO-15 standing collapse detector,
Archaeon's WSE contrast stencils (#322), Techne's MKW-1 freeze (#311). [HIST BACKLOG + comms]

## 9. False-positive / false-negative archaeology

Timeline 1 -- the "9 new-to-record signals".
claim (founding: 9 REPRODUCIBLE contrasts new to the record, all uniform-density at N=599) -> evidence (z >= 4 both
passes) -> challenge (round-2 H1-H7 dissection) -> correction (ECOLOGICAL_CORRELATION_ONLY: explained by margin
distribution + rule-specific finite-size response) -> status: retired by the seat itself within 24 h.

Timeline 2 -- "23 reproducible signals".
claim (founding headline) -> challenge (self-noted in packet s10: 14/23 are positive controls) -> later (Atlas uses it
as an example of "controls admitted as signals") -> status: the admission gate measured reproducibility, not novelty.

Timeline 3 -- SPEC-001 as a "mechanism specimen".
claim (round 2: MARGIN_RESPONSE harvested) -> self-caveat (H1 exact by exchangeability; reviewer question left open:
mechanism or instrument?) -> status: in substance an instrument (a per-IC phenotype curve) plus a reparameterisation of
the IC ensemble as a margin distribution; not evidence of a CA mechanism.

Timeline 4 -- SPEC-002 "exp is a one-class classifier at N >= 599".
claim (published exp accuracies at 599/999 are a constant classifier's) -> challenge (Artemis Q7: final states never
logged; a failed prediction reported as predicted) -> status: plausible description of the per-IC table (1.0 on
d > 1/2, near 0 on d < 1/2 near the boundary), mechanism UNKNOWN; worker's challenge unverified.

False-negative regimes:
- The charter's space (many eras, many kinds, Nyx organs, interventions that compose mechanisms) was never reached;
  what was explored is a 4-rule, 1-kind corner. Absence of "reversals", "revivals" or "non-additive combinations" is
  not evidence about the space -- composition (REQ-003) and table-level intervention (REQ-005) were delivered by other
  seats after Theophrastus went silent and were never used. [HIST]
- The counterfactual-attack traversal mode, the one designed to revisit dead terrain, never ran. [HIST]

## 10. Research outputs

- roles/Theophrastus/crucible/FOUNDING_ROUND_REPORT_2026-09-13.md, REPORT_2026-09-13.json, SIGNALS_ANNOTATED_2026-09-13.json
- roles/Theophrastus/crucible/PREREG_FOUNDING_CRUCIBLE_2026-09-13.md, ROUND2_DISSECTION_PLAN_2026-09-14.md,
  PREREG_THEO14_CROSS_CONSUMER_2026-09-14.md
- roles/Theophrastus/specimens/SPECIMENS_ROUND2_2026-09-14.md (SPEC-001, SPEC-002, CAND-003)
- roles/Theophrastus/REVIEW_PACKET_FOUNDING_2026-09-13.txt, REVIEW_PACKET_ROUND2_2026-09-14.txt
- roles/Theophrastus/recon/CAPABILITY_MATRIX_2026-09-13.md (8 NATIVE, 4 REP, 2 AWK, 2 MISSING) + conformance gate log
- roles/Theophrastus/reqs/THEO-REQ-001..006 (substrate change requirements)
- Downstream artifacts created by other seats in response: evidence_wiki ecology selector (REQ-001, Mnemosyne
  569a675f7), Kind.axes (REQ-002, Vivarium 660a8de1d), herakles/evca/derive.py (REQ-003/005 library, dbc41fd2f),
  proteus/eval/rule_table_mint.py + proteus/mint/RULE_TABLE_MINTS.jsonl (REQ-003 mint, 24e3caaf9), Vivarium validator
  fix (REQ-004, a9f81c7d6), exact-count ICs (REQ-006, 6358acea9), nyx/readings/theo_req_003_composition.py (09-30).

## 11. Journals, TODOs, pivots, abandoned branches

- Journals: 2026-09-13 (founding), 2026-09-14 (round 2, THEO-14).
- Pivot: founding (loop real) -> operator round-2 prompt "harvest the mechanism" (from signals to specimens).
- Abandonment: after 2026-09-14 the seat never booted again (no comms from Theophrastus after #252). All six REQs were
  closed by their owners between 09-16 and 09-30 without a consumer. STATUS.md was never updated.
- Backlog THEO-01..15 (above) is the unfinished plan; THEO-08 (rule-10 bound and accountable seat before any
  unattended crawl) was the gate for sustained crawling and never resolved.

## 12. Lens inventory

Lens: "contrast-first explorer over a shared execution substrate" (Theophrastus harness).
- Substrate: SFE engine + Vivarium kind ca_density_v0 + PEW fossils.
- Organisms: fixed historical CA rule tables (maj, GKL, exp, par, particle1).
- Worlds: density classification on rings of 149-999 cells.
- Pressures: IC density ensembles (test distributions), horizon, reflection intervention.
- Phenomenon family: how a fixed mechanism's performance shifts when world/pressure/intervention move; per-IC
  phenotype curves.
- Resolving mechanism: paired contrasts with SE and two-pass replication; content-hashed cells with alias/no-op/stale
  detection; offline bit-exact re-derivation of every fossil's per-IC outcomes.
- Resolution ceiling: 800 ICs per cell (SE ~0.018); margin bins need >= ~100 ICs; 4-5 rules.
- Noise: binomial; nominal-p vs realised-margin confusion (identified); no prior-evidence gate.
- Architectural limitation: no search, no evolution, one kind; depends on a live engine and other seats' REQs.
- Reusable: the cell identity model (spec_hash vs execution_hash), the ten self-control cheats, the closed disposition
  vocabulary, the offline per-IC re-derivation discipline (validated on 150 foreign fossils).
- Toy-grade: the arena (a 1990s benchmark with known answers).
- Unknown: whether the explorer finds anything non-trivial once given a prior-evidence gate, multiple kinds and
  composition operators -- never tried.

## Open questions / unknowns

1. Why did the seat stop after 09-14? No closure or parking record; host M1 instance never re-booted per comms.
2. Is SPEC-002's one-class collapse real at the final-state level (final states never logged)?
3. Was any THEO-SIGNAL consumed by another seat? No consumer record found.
4. STATUS.md says ACTIVE; FLEET_CENSUS says DORMANT; INHERITANCE.md lacks the row -- the seat's official state is
   inconsistent across the record.
