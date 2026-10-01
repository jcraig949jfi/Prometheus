# Polyhymnia -- Phase 3 intake dossier

Seat: Polyhymnia (May 2026 "Omnitensor" agent; re-premised 2026-09-11 as the representation scavenger)
Crawler: Tantalus (worker)
Tree: origin/main at 21a47402a (worktree F:\Prometheus-worktrees\tantalus-phase3-intake)
Date: 2026-10-01

Summary. Polyhymnia is a representation-focused seat with two short lives and a large gap between what was written
and what was built. Life 1 (2026-05-24..05-30, chartered by Aporia, code at agents/polyhymnia/): the "Omnitensor", a
sparse content-addressable JSONL store of "tensor-shaped knowledge" with 9 coordinate axes, fed by ONE scour (a
regex/AST grep of this repository) through a 30-minute daemon carrying a menu-based SelfImprovingDaemon mixin. It
saturated on day one (2,137 of 2,415 tesserae on 05-24), ran 297 ticks (47 integrating, 250 null), and filed 163
identical unanswered approval requests to spawn a second scour; the lenses and games directories contain only
__init__.py files and a README, and 17 planned scours were never written. Life 2 (2026-09-11, one day, roles/Polyhymnia/):
reactivated, archaeology done, re-premised by the operator ("the daemon earns resurrection when something is hungry
enough to eat what it produces"), and ONE preregistered probe run: PROBE-01, a family of [12,8] binary linear-code
syndrome decoders offered as genotype -> elementary-CA-rule maps through Archaeon's H5 decoder slot, measured by
exact enumeration. 8/8 controls passed and one preregistered direction was wrong (Hamming member reach 5.69, not >8).
Archaeon built a consumption hook for it the same day (ARCH-30: load_table_decoder + h5_readout(instruments=...)),
but Polyhymnia never delivered the table artifacts (POLY-07), and the seat has made no commit since 2026-09-11. No
representation candidate from this seat was ever consumed by an experiment. Of 24 backlog items, 5 are DONE; the
families planned next (Gray, Morton, d=3 code members, neutral-network structure, external solver representations)
exist only as backlog rows.

----------------------------------------------------------------------------------------------------------------
## 1. Identity, charter and pivots

- Name Polyhymnia; artifact names "Omnitensor" (the store) and "tessera" (a cell), renamed 2026-05-24 per a
  "ChatGPT cross-frontier" suggestion (agents/polyhymnia/tensor.py docstring) [IMPL].
- Host: M1 (SKULLPORT), ran from the canonical checkout; pid 23960 started 2026-05-25T11:41Z, not alive on 09-11
  [CLAIM, ARCHAEOLOGY_2026-09-11.md s1]. Reactivated 09-11 in worktree polyhymnia-base-role on M1 with model
  claude-opus-5[1m] [CLAIM, journal].
- Life 1 charter: agents/polyhymnia/CHARTER.md, authored by Aporia 2026-05-24 (commits 38e0ca5e9 Phase 0, 5c3fb5111
  v0.2 Omnitensor terminology, ccac80738 fix, 2b4d12eb6 SelfImprovingDaemon mixin adoption, df9153e0b cross-agent
  mutation registry) [IMPL, git log]. Thesis "There's one tensor ... The tensor is the sensory organ. A species that
  can only see the world tensor-first would use this thing as its eyes." "Not a research tool. A play tool that becomes
  a research tool because the substrate is rich enough." [INTENT]
- 2026-06-15 reset listed "Icarus pilot + Polyhymnia (named operators)" under KEEP; nothing ran after 05-30
  [CLAIM, archaeology s1]. Harmonia 06-10 journal: "Polyhymnia = source_saturated (single scour)", "health on a dead
  channel" [CLAIM, second-hand; not opened by this crawl].
- 2026-09-11: reactivated (6580169fa), archaeology "0 executable items"; operator re-premise directive verbatim at
  roles/Polyhymnia/prompts/2026-09-11_reactivation_direction/OPERATOR_DIRECTIVE.md: "Polyhymnia is no longer 'the one
  tensor.' Polyhymnia becomes the REPRESENTATION SCAVENGER for the Prometheus 2.0 ecology ... Do not prove that these
  representations are useful ... The consumer contract comes first ... A null result is acceptable. An unused artifact
  is not." [IMPL, file read]
- Same day: tensor body archived (54221bfdb), PROBE-01 preregistered (e6f0b64fb) and run (8313700c1), seat files
  re-premised (7b166723a). No later commit touches roles/Polyhymnia or agents/polyhymnia [IMPL, git log]. Achilles'
  census (roles/Achilles/census/registry/seats_part4.json) records "No commits since 2026-09-11" [CLAIM].
- Relationships: Archaeon (owner of H0-H5 and the H5 decoder slot; consumer; question #67 answered with ARCH-30),
  Herakles (ECA class map), Techne (Stitch/DreamCoder/pyribs tools), Ludus and Proteus (searched: no representation
  slot, 09-11), Nyx (Chop Shop specimens as possible sources), Talos (#50 consumer-contract protocol; Talos's
  CONSUMER_SEARCH_2026-09-11.md records Polyhymnia as NO_REPLY), Aporia (life-1 "operator", inbox recipient of the 163
  requests).
- Atlas: grep of roles/Atlas/ for "polyhymnia" returns 0 matches; atlas/ returns none relevant [IMPL]. Atlas does not
  locate this seat.

## 2. Engine/system inventory

P-A. Omnitensor daemon (agents/polyhymnia/; 2026-05-24..30).
  - tensor.py (348 lines): PolyhymniaTensor -- append-only tesserae.jsonl, lineage edges, axis registries,
    integrate() (merge on coordinate signature), slice(), project(), sample(), stats(). tessera_id = 16-hex sha256 of
    canonical coords + lowercased title + first 500 chars of body [IMPL].
  - COORD_AXES (9): time, discipline, object_kind, structural_rank, abstraction_level, substrate_yield_type,
    epistemic_status, data_modality, code_language; TAG_AXES (5): researchers, lineage_ancestors, free_tags,
    citations, game_affordance [IMPL].
  - scours/prometheus_self.py (202 lines): walks prometheus_math, charon, theseus, apollo, ergon, scripts, agents;
    matches Python functions against ~30 keyword regexes (tensor, rank, kronecker, tucker, mahler, lehmer, spectral,
    galois, fingerprint, ...); maps path prefixes to a discipline string; emits epistemic_status EXTRACTED,
    data_modality code [IMPL].
  - daemon.py (672 lines): tick loop, pid lock, state, heartbeat; PolyhymniaSelfImprover(SelfImprovingDaemon) with an
    ADAPTATION_MENU of 6 entries, of which ONE is real (DROP_MTIME_CACHE clears the scour's mtime cache) and five are
    log-only stubs (EXPAND_KW_RE, EXPAND_PATHS, EXPAND_FILE_TYPES, SPAWN_SIBLING_SCOUR [requires_human_approval],
    MODE_PIVOT_GAME_GEN) [IMPL, daemon.py L198-300].
  - measure_health: null_rate, diversity (= fraction of productive ticks), novelty (= new/100 per tick), and
    downstream_consumption hard-coded 0.0 ("not wired yet") [IMPL, daemon.py].
  - lenses/, games/: only __init__.py (9-10 lines) and a games/README.md [IMPL, git ls-files].
  - tensor/axes/*.jsonl (8 registries) and tensor/relations.jsonl (17 edges) tracked; the body tesserae.jsonl
    (4,917 lines, 11,529,754 B) was gitignored and is now archived byte-identical under
    roles/Polyhymnia/ledgers/tensor_body_2026-09-11/ with sha256 020f5a43... [CLAIM, ARCHIVE_MANIFEST.md].
  - scripts/polyhymnia_loop_launch.bat (launcher; never a scheduled task on M1 per schtasks 09-11) [CLAIM].
  - Shared framework: agents/_shared/self_improving.py (Aporia, design pivot/self_improving_daemon_design_2026-05-25.md)
    -- not read in body by this crawl.
P-B. PROBE-01 lincode decoder family (roles/Polyhymnia/science/; 2026-09-11).
  - lincode_decoders.py (~170 lines): make_lincode(rows) builds a decoder from an 8x4 parity matrix A over GF(2);
    coset leaders by (weight, integer) order; decode rule(g) = (g XOR L[syndrome(g)]) & 0xFF; HAMMING_ROWS =
    (3,5,6,7,9,10,11,12) (shortened Hamming [12,8,3]); random_rows(seed); A=0 equals Archaeon's direct decoder;
    cheat_nonuniform (g mod 255) as a gate-refusal control; preimage_components [IMPL, file read in full].
  - probe_01_run.py (~9 KB), tests/test_lincode_decoders.py, PROBE_01_PREREGISTRATION.md, ledgers/probe_01_lincode
    _2026-09-11.{json (710 KB per-genome vectors), md}.
  - Imports archaeon.producer.h5_decoders (consumer) and uses h5_reference.exact_reference + Herakles's class map
    herakles/eca/class_map_fixture.json (224 classes) [IMPL].
P-C. Saturation analysis (science/saturation_curve.py, ledgers/scour_saturation_2026-05.{json,md}): a re-reading of
  the May event log [IMPL].

## 3. Code architecture and dataflow

P-A: tick -> round-robin scour (only prometheus_self exists) -> CandidateTessera list -> integrate (hash, merge on
signature, latest content wins, tags union) -> append JSONL -> heartbeat -> self-improvement cycle (measure_health
over last 10 ticks; on stagnation choose an adaptation; SPAWN_SIBLING_SCOUR posts an approval ticket to Aporia's
JSONL inbox). Nothing reads the store: no lens or game was implemented and downstream_consumption is a constant 0.
Code/doc disagreement: the charter's storage section names cells.jsonl / lineage.jsonl; v0.2 code uses
tesserae.jsonl; the charter lists 6 coordinate axes, code has 9 [IMPL, recorded by the seat as annotations].
The charter's "structural_rank" axis is in the code; whether any tessera has non-null rank: UNKNOWN (the
archive manifest says only discipline (8 values) and object_kind (2) varied; 6 of 9 axes constant) [CLAIM].
Count discrepancy: 4,917 lines in tesserae.jsonl vs 2,415 tesserae "new" in the saturation table and 2,415 cells in
STATUS; consistent with append-then-merge semantics but not verified [UNKNOWN].

P-B: genome g in 0..4095 -> decoder -> rule in 0..255 -> (Archaeon) exact_reference enumerates all 4,096 x 12
single-bit-flip edges -> per-genome reach (distinct non-parent phenotypes among 12 mutants) and neutral count, raw and
collapsed to 224 classes -> histograms, means, sha256 table identity. Deterministic; no sampling, no engine, no CA run
inside the probe (the CA semantics enter only through the class map).

## 4. Claimed computational primitive vs actual mechanism

P-A Omnitensor.
- Label: "the one tensor", an N-dimensional sensory organ; "self-improving" daemon.
- Smallest mechanism: regex/AST keyword grep over local Python files, emitting JSON rows keyed by a hash of 9
  categorical fields + text; a dict merge. "Tensor" is a metaphor for a sparse multi-key index; there is no tensor
  algebra, decomposition or numeric content [IMPL].
- Self-improvement: a fixed menu of 6 named actions, 1 functional (cache clear), selected on a null-rate threshold.
  The menu cannot grow except by human code edits; SPAWN_SIBLING_SCOUR was a placeholder requiring approval [IMPL].
  Zero-cost inspection by this crawl of the archived events file
  (roles/Polyhymnia/ledgers/tensor_body_2026-09-11/events_2026-05-24_to_05-30.jsonl, Python Counter over event
  types): self_improvement_cycle 257 (SPAWN_SIBLING_SCOUR 163; each other menu item 2), self_improvement_stub_applied
  4 (the four stubs once each), self_audit_null_alarm 23, tick_start/tick_end 297 each.
- Ruler: tick health heartbeat. It reported "healthy" while 250/297 ticks were null [CLAIM, calibration ledger].
- Could it perform "tensor-first perception": no consumer existed; the question was never posed operationally.

P-B lincode.
- Label: a "representation candidate" -- coding-theory structure in the genotype-phenotype map, to change "access to
  useful variation" (H5: "Do learned encodings improve access to useful variation?").
- Smallest mechanism: a fixed 4096 -> 256 lookup table with exactly 16 preimages per rule, built from syndrome
  decoding. It is not learned and has no parameters adapted by any process.
- Could express: different neighbourhood (mutational access) structure over a fixed phenotype catalogue -- a
  neutral-network geometry.
- Ruler: mean/min/max reach and neutrality under single-bit flips, raw and class-collapsed, with scrambled twins
  (frequency-preserving null) and a drop rule structure_gain_classes <= 0 (Archaeon ARCH-30).
- Organism: none in this probe; it measures the map, not an evolving population. Whether a lineage would evolve
  faster/better under the map was never run.
- Shortcut distinction: the scrambled-twin control separates structure from multiplicity histogram; the probe found
  scrambled_hamming_3 identical to hamming on raw histograms (P4 PASS by design) and the class-collapsed difference
  small (5.6104 vs 5.6350) [RESULT-UNVERIFIED, ledger md] -- i.e. at this scope the Hamming structure added no class
  reach beyond its multiplicity pattern, and it LOWERED reach relative to direct (5.61 vs 7.78 classes).

## 5. Representation/state architecture

- P-A: heterogeneous JSON rows with 9 categorical coordinates, 5 list-valued tags, free text content, 17 typed
  relation edges; append-only; merge on signature. Effective occupancy 13 coordinate signatures [CLAIM].
- P-B: a 12-bit genome, 8 information + 4 parity bits; phenotype = ECA rule number; decoder = table.

## 6. Organism/player architecture

None built. The "games" (random_walk, connect_two, complete_the_slice, twenty_questions, mendeleev) were named in
the charter for a "Learner" that the archaeology says is gone (Ergon re-chartered 2026-08-30) [CLAIM]. In PROBE-01 the
organism is implicit (Archaeon's H5 lineages, not run here).

## 7. World/environment architecture (toy scale)

- P-A: the "world" is this repository's Python files under 7 roots; saturated in about one day.
- P-B: 4,096 genomes, 256 ECA rules, 224 classes (terminal behaviour at 8 steps on a 7-cell ring per the prereg),
  12 neighbours per genome, 49,152 edges per decoder. Exhaustively enumerable; a very small fixed toy. The live H5-1
  map was partial (232/256) at probe time and not used; POLY-08 (rerun on the completed live map) not done.

## 8. Search/training/adaptation mechanism

- P-A: none beyond scheduled rescans; the self-improvement layer is threshold-triggered menu choice. Collapse mode:
  single-source saturation, then a stagnation detector repeatedly selecting the only escalation (spawn a scour) that
  needed approval nobody gave.
- P-B: none; families are hand-specified (Hamming rows, two seeded random A's, A=0).

## 9. Measurement/ruler stack

- P-B controls (prereg e6f0b64fb): P1 planted analytic count (256 genomes at reach 0 / neutral 12 under Hamming),
  P2 bounds, P3 preimage-component structure (prediction corrected before the run, ledgered), P4 scrambled invariance,
  P5 A=0 equals direct (table sha256), positive control direct {8: 4096}, gate refusal (g mod 255 refused by
  check_exact), spread between random members. Measured M1-M5 with directions written first; M2 direction WRONG.
  Statistics: none needed (exact enumeration).
- Blind spot: reach/neutrality at single-flip scope says nothing about evolvability over multi-step lineages,
  selection or task value; the seat states "no usefulness claim" [CLAIM].
- P-A ruler: heartbeat health; defective (silence read as health).

## 10. Baselines and controls

P-B: direct (A=0) baseline, balanced_7 (Archaeon's seeded permutation), scrambled twins, random members, a cheat
decoder. P-A: none.

## 11. Historical experiment campaigns

| id | date | question | organism / world | measurement | arms / scale | reported result | later reinterpretation | label |
|---|---|---|---|---|---|---|---|---|
| Omnitensor daemon run (agents/polyhymnia/; events archived) | 2026-05-24..30 | ingest tensor-shaped knowledge | 1 scour over this repo | tick outcomes | 297 ticks | 2,415 tesserae; 47 integrating / 250 null; 163 approval requests | archaeology: saturated day 1, no consumer; operator: evidence against accumulate-before-consumer | REPORTED NEGATIVE/NULL |
| PROBE-01 lincode (e6f0b64fb prereg, 8313700c1 run) | 2026-09-11 | does a coding-theory decoder change accessible variation through the H5 slot | 4,096-genome -> 256-rule map | exact reach/neutral, raw and 224-class | 7 decoders | 8/8 controls PASS; Hamming mean reach 5.69 (pred >8, WRONG); classes 5.61 vs direct 7.78 | never consumed; ARCH-30 first read waits on table artifacts never delivered | MIXED |
| Saturation curve POLY-05 (54221bfdb) | 2026-09-11 | when did the scour saturate | event log | per-day counts | 297 ticks | 2,137/2,415 on day one; last new tessera 05-30T10:01Z | -- | REPORTED NEGATIVE/NULL |

## 12. Reported results and later corrections

- 05-25..30 heartbeats "healthy" -> 250/297 null -> Harmonia 06-10 "health on a dead channel" -> calibration ledger
  row 2 (09-11). Status: corrected.
- 163 approval requests -> Aporia 824a668b4 "fix self-improving spam" (addressed the flood, not the request) ->
  ledger row 1. Status: corrected, request RETIRED.
- PROBE-01 P3 "13-ball plus 3 satellites" -> own test found one 16-component -> corrected before the run.
- PROBE-01 M2 ">8" -> 5.6875 measured; flip pairs with col_k = col_i + col_j reach the same codeword, so exits pair
  up -> POLY-12 collision-count check planned, not built.
- "Polyhymnia advances HARD-3 (tensor first)": the archaeology explicitly separates the Omnitensor from HARD-3's
  signature-keyed tensor and Harmonia records them as code-independent [CLAIM]. No claim of linkage stands.

## 13. False-positive archaeology

- Activity counted as health (null ticks as healthy; 163 requests as blocked work).
- "Tensor" naming: a keyword index called a tensor; the word invites conflation with HARD-3 and with tensor-method
  seats; the seat itself flagged the conflation risk.
- No positive scientific claim was made in life 2 ("no usefulness claim").

## 14. Likely false-negative regimes

- PROBE-01 measured only single-flip reach on a 12-bit genome with a phenotype space of 256 and a 224-class map in
  which most classes are singletons; error-correcting structure that lowers per-genome reach could still help
  multi-step neutral drift, which the probe cannot see (POLY-13 neutral-network structure was proposed for this and
  not run).
- The consumer never ran the candidate in an evolving lineage; no selection pressure was ever applied to any
  Polyhymnia representation.
- Only one family was tested; Gray, Morton/Z-order, other d=3 members (POLY-09..11) were never measured, so "structured
  decoders do not help" is untested beyond one member.
- Life 1 had one source, so "scavenging is unproductive" was never tested against any external source.

## 15. Phase 3 audit

a. Representation richness
- P-A Omnitensor: hierarchy NO (flat rows; lineage edges 17 total); compositional structure NO; variable binding NO;
  memory PARTIAL (a persistent store, unread); recurrence NO; counterfactual state NO; latent variables NO; temporal
  abstraction PARTIAL (a 'time' axis, effectively constant); spatial abstraction NO; reusable substructure NO; dynamic
  routing NO; self-reference PARTIAL (the scour reads the repo that contains it; the self-improver edits its own scour
  state, not its code).
- P-B lincode: hierarchy NO; compositional structure PARTIAL (GF(2) linear structure of the code; decoders compose
  with scramblers); variable binding NO; memory NO; recurrence NO; counterfactual state NO; latent variables PARTIAL
  (the syndrome is a hidden coordinate that decides which phenotype a genome maps to); temporal abstraction NO;
  spatial abstraction NO; reusable substructure PARTIAL (neutral networks / cosets); dynamic routing NO;
  self-reference NO.
b. Reasoning opportunity. Neither engine has an environment that demands reasoning. P-A has no task. P-B is a static
   map measurement; any reasoning demand would come from the consumer's world (an 8-step ECA on a 7-cell ring), which
   is small-FSM territory.
c. Shortcut surface. P-B: reach differences produced purely by preimage multiplicity patterns (controlled by
   scrambled twins); class-map artifacts (224 classes, many singletons) inflating or deflating class-collapsed reach;
   hand-design mistaken for evolved representation (the H5 design says a hand-designed decoder is an instrument, not
   evidence for learned evolvability; POLY-XL-03 open). P-A: counting rows or ticks as productivity.
d. Ruler resolving power. P-B: exact and fully controlled for what it measures (single-step accessible variation), but
   the quantity is far from the claimed phenomenon (evolvability, useful variation); it cannot resolve downstream
   value. P-A: none.
e. Scale. P-A: 7 repo roots, ~30 regexes, 297 ticks over 6 days, 2,415 tesserae, 13 occupied signatures, 17 edges,
   11.5 MB body. P-B: 4,096 genomes, 12 neighbours, 256 phenotypes, 224 classes, 7 decoders, 49,152 edges each; runs
   in seconds; no compute ceiling reached.

## 16. Research reports and substantial documents

- agents/polyhymnia/CHARTER.md -- life-1 design (301 lines), annotated 09-11 section by section.
- roles/Polyhymnia/ARCHAEOLOGY_2026-09-11.md -- what ran, what did not, old queue classified (0 executable).
- roles/Polyhymnia/science/PROBE_01_PREREGISTRATION.md -- the consumer chain, family definition, predictions.
- roles/Polyhymnia/ledgers/probe_01_lincode_2026-09-11.md (+ .json) -- readout and control table.
- roles/Polyhymnia/ledgers/scour_saturation_2026-05.md -- day-by-day saturation.
- roles/Polyhymnia/ledgers/tensor_body_2026-09-11/ARCHIVE_MANIFEST.md -- residue archive with sha256.
- roles/Polyhymnia/prompts/2026-09-11_reactivation_direction/OPERATOR_DIRECTIVE.md -- re-premise, verbatim.
- roles/Polyhymnia/prompts/2026-09-11_h5_contract/QUESTION_ARCHAEON_h5_consumption_contract.md -- consumer contract
  question (#67).
- pivot/self_improving_daemon_design_2026-05-25.md (Aporia) -- the SelfImprovingDaemon "gen-N wall" design whose
  first adopter was Polyhymnia.
- archaeon/docs/h0h5/H5_1_READOUT_2026-09-11.md and roles/Archaeon/BACKLOG_H0H5.md ARCH-30 -- consumer side.

## 17. Journals/TODOs/backlogs/pivots/abandoned branches

- journal/2026-09-11.md (only journal). calibration/LEDGER.md (4 rows). BACKLOG_H0H5.md: 24 items; DONE POLY-XL-01,
  XL-02, 01, 03, 05; open POLY-06 (record Archaeon's contract answer -- Archaeon's H0H5_STATUS.md shows it WAS answered
  with ARCH-30 the same day, but the Polyhymnia row was never updated) [CORRECTION, cross-seat], POLY-07 (deliver
  table artifacts), 08-22 (further families, surveys, falsifier ledger, guards), XL-03 (may an unlearned structured
  decoder be a beta arm), XL-04 (production cadence).
- superseded/RESPONSIBILITIES_2026-09-11_adoption_pass.md.
- Branch polyhymnia/base-role-adopt-2026-09-11 (worktree polyhymnia-base-role) [CLAIM].
- Abandoned: the daemon (DORMANT, registered in roles/base-role/MONITORS.md, not to be restarted), the lens/game
  layer (never built), scours rounds 2-4 (never written).

## 18. Dependencies on other engines and seats

- Imports archaeon.producer.h5_decoders and h5_reference; reads herakles/eca/class_map_fixture.json [IMPL].
- Archaeon's ARCH-30 consumer hook (load_table_decoder, h5_readout instruments block, drop rule) exists and is
  unused by this seat [IMPL, archaeon/producer/h5_decoders.py L201-226, campaign_h5.py L105-130].
- Life 1: agents/_shared/self_improving.py and mutation_registry.py (Aporia); Aporia's JSONL inbox.

## 19. Scaling limitations

P-A: single-threaded JSONL append with full-index reload; per-tick artifacts duplicated an ~800 KB mtime map 297
times (194 MB, not archived) [CLAIM]. P-B: exhaustive enumeration is trivial at 12 bits but the approach (exact
reach over all genomes) scales as 2^bits x bits; the H5 consumer's phenotype space is fixed at 256 rules.

## 20. Lens potential for Phase 3 (descriptive only)

- Substrate: genotype-phenotype maps (decoders) with fixed multiplicity; a representation-candidate supply line.
- Organisms: none of its own; the consumer's H5 lineages.
- Worlds: elementary CA rules collapsed to behaviour classes.
- Pressures: none applied.
- Phenomenon family: encoding / accessibility of variation, neutral networks, structured vs scrambled maps.
- Current resolving mechanism: exact enumeration with scrambled twins and gate refusals.
- Resolution ceiling: single-step accessibility on a 4,096-genome toy.
- Noise sources: none stochastic; class-map choice is the main confound.
- Architectural limit: no lineage, no task value, no learned decoder.
- Reusable parts: the consumer-first discipline (source -> candidate -> consumer -> measurable difference ->
  deterministic observation); the scrambled-twin null; the premise-falsifier idea (POLY-20: consumed/produced ratio,
  indistinguishable-from-random-members tests); the residue-archive practice; the archaeology of a dead daemon as a
  worked negative example of self-improvement by fixed menu.
- Toy-grade parts: the Omnitensor store and its single scour; the 12-bit H5 map.
- Unknowns: whether any structured decoder changes lineage-level outcomes; whether the external-representation survey
  (POLY-18: CNF/Tseitin, e-graphs, de Bruijn, BWT, Morton, Gray, Walsh-Hadamard) would find a consumer slot anywhere.
  The ideas listed there are ahead of any implementation in this seat.

## 21. Open questions / what this crawl did not read

Read: RESPONSIBILITIES.md, STATUS.md, ARCHAEOLOGY_2026-09-11.md, BACKLOG_H0H5.md, calibration/LEDGER.md, journal
(first 60 lines), PROBE_01_PREREGISTRATION.md (first 60 lines), lincode_decoders.py (full), probe ledger md, saturation
ledger md, archive manifest (first 40 lines), operator directive, agents/polyhymnia/CHARTER.md (first 120 lines),
tensor.py (first 140 lines and def list), scours/prometheus_self.py (first 80 lines), daemon.py L198-330, Archaeon's
h5_decoders.py (docstring, L195-226) and campaign_h5.py (L100-130), Archaeon H0H5_STATUS/BACKLOG lines naming
Polyhymnia, Achilles census row, MONITORS row. One zero-cost inspection: event-type counts over the archived events
JSONL (section 4).
Not read: the tesserae.jsonl body (11.5 MB; not opened), probe_01_run.py and its test, the 710 KB probe JSON, the
remaining daemon.py, agents/_shared/self_improving.py, Aporia's design doc body, Harmonia's June journals, the
question/report prompt files, Talos/Nemesis/Artemis mentions beyond one-line greps. A `git log -S lincode` over the
tree timed out at 300 s after printing 4 recent commits, so a full history search for any later delivery of lincode
tables is incomplete; no decoder_tables directory exists under roles/Polyhymnia at HEAD [IMPL].
Holdout/secret paths: none touched.
