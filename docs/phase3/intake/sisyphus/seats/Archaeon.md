# Archaeon -- forensic seat dossier (Sisyphus crawl, Phase 3 intake)

- Seat: Archaeon
- Crawl date: 2026-10-01
- Base SHA of the crawl worktree (F:/Prometheus-worktrees/sisyphus-base-role): 19299e06b
- Crawler: Sisyphus worker (Archaeon only)
- Epistemic tags used inline: [IMPL] implementation fact, [INTENT] design intent, [HIST] historical claim,
  [RESULT-UNVERIFIED] reported result not re-established here, [CORRECTION] later correction/contradiction,
  [CODE-INFERRED] capability inferred from code, [UNKNOWN] unknown/ambiguous. Nothing tagged [RESULT-UNVERIFIED]
  was re-run by this crawl; numbers are quoted from the committed artifact cited.

## Coverage statement

READ (substantively):
- roles/Archaeon/: CHARTER.md, RESPONSIBILITIES.md (head), STATUS_2026-10-01.md, RESUME.md, ENGINE_LANDSCAPE_2026-09-25.md,
  CALIBRATION_LEDGER.md (head), REVIEW_PACKET_2026-09-10.md (full), REVIEW_PACKET_WSE_ARCHITECTURE_2026-09-17.md (most),
  REVIEW_PACKET_CAMPAIGN4_2026-09-18.md (full), REVIEW_PACKET_CAMPAIGN5_2026-09-18.md (most), journal heads (09-11, 09-13,
  09-16), prompts/2026-09-10_backlog/ARCHAEON_AND_OPERATOR.md, prompts/2026-09-08_h0h5/DESIGN_H0_H5_v0.1.md (head), prompt
  directory listing.
- archaeon/ code and docs: docs/ARCHAEON_V0.md, CALIBRATION.md, STAGE0_RESULT.md; docs/h0h5 readouts S1, S3-S7, ARCH46A,
  C3_2, H5_1, H3 dead-stream, H1H0 phase 2, EXCHANGEABILITY_D1_D6; wse/READOUT_v01.md, READOUT_ssf.md; campaign1
  CAMPAIGN_REPORT head; campaign6 PLAN.md, DECISIONS.md, worlds/generator.py, worlds/runtime.py, ADMISSION_PACKET grep;
  frontier DEEP_FRONTIER_CHARTER.md, DECISIONS.md (DF-010..DF-016), digests/DIGEST_2026-09-21T2054Z.md, BOOM_READOUT JSON,
  registry EVENTS (INTERPRETATION / INSTRUMENT_DEFECT / OBSERVATION rows), scheduler.py ADMITTED constant, digest.py;
  z80atlas CAMPAIGN_CONTRACT.md, vm.py (head), grammar FROZEN constants and AXES (imported, zero-cost), campaign/
  CAMPAIGN_PACKET.md (head), pivot/Z80ATLAS_POSTCAMPAIGN_REVIEW_2026-09-23.md, Z80ATLAS_RULINGS_FOLLOWUP_REVIEW_2026-09-24.md;
  envgate ADJUDICATION_ADDENDUM, ENVGATE01_REVIEW (most); envgate2 VERDICT_2026-09-26.md, ENVGATE_CLOSURE_2026-09-26.md;
  lineage/taint_vm.py and core.py docstrings; rie/world.py docstring; causal_lens PORTABILITY01_REPORT.md (first ~120
  lines), FALSE_FRIENDS.md (index); ops/campaigns/C-001 CAMPAIGN.md (head), ATTRIBUTION_V0 ATTRIBUTION_PACKET.md (head),
  DEEP_BLOCK G_PRIOR_ART.md (head).
- Branch-only: origin/archaeon/attribution-arc-2026-09-28 E003_SYNTHESIS.md (git show); origin/archaeon/mwo0001-2026-09-28
  FP-001_RESULT.json.
- Cross-seat: roles/Harmonia/audits/EVIDENCE_AUDIT_2026-09-30_SAMPLE2.md (item H, E-003); roles/Nestor CW01
  BOUNDARY_REPORT_CYCLE5_2026-09-19.md (ruler reread) and commit bdf8c5df4 (T-ARCH4 tranche); roles/Atlas
  inference_harvest_2026-09-30 (grep for Archaeon in BURIED_SIGNALS, CONTRADICTIONS, CROSS_ENGINE_SYNTHESIS);
  roles/Artemis/threads/sfe_retrospective/ENGINE_LENS_CARDS.md (Archaeon card); roles/Achilles/census/registry
  (engines.json, seats_part1.json Archaeon rows); roles/base-role/MONITORS.md (Archaeon rows); comms #455-#495 subjects
  and #461/#486 bodies.
- Git history: full `git log` of archaeon/ and roles/Archaeon/ (390 commits, 2026-09-05..2026-10-01); unmerged
  origin/archaeon/* branch heads; import graph of archaeon.* from outside archaeon/.

NOT READ, and why:
- campaign2/campaign3/campaign4/campaign5 per-slot DESIGN/READOUT files individually (relied on the campaign-level
  reports and review packets, which quote per-slot numbers; slot-level re-verification is a follow-up).
- H0H5_STATUS.md (8,974 words), BACKLOG_H0H5.md, TODO.md, EXPANSIONS.md, docs/expansion/* (ROADMAP, CROSSWALK, 69 mined
  templates) beyond headings: governance/coordination material, sampled not exhausted.
- frontier registry EVENTS.jsonl (313k lines) beyond targeted grep; per-run receipts under runs/ are git-ignored on the
  executing host and not present.
- Off-repo evidence (C:/Prometheus-data/evidence/*, D:/Prometheus-worktrees/*): out of scope (read-only worktree rule;
  host-local).
- causal_lens contract v0.2/v0.3 text, V02_REGRESSION_REPORT, deep-block blocks A-F, attribution REVIEW_1/2 adjudications,
  E-003 prereg v1-v5 and gate_close records: sampled by summary only.
- Any path containing "holdout" or "nestor_secrets": excluded by rule (none found under archaeon/).

## 1. Identity and purpose

Canonical name: Archaeon. Instance tags seen: m1-6833664f, m1-7d3bbe9e (M1, 2026-09-05..09-14); m2-5c10f6f6, m2-411504ab,
m2-49ee5a4d, m2-db608f52, m2-1034e815 (M2, 2026-09-16..10-01) [HIST: journal headers, commit subjects]. No other aliases
found (Achilles census registry lists aliases: []).

Original charter (2026-09-05; expanded 2026-09-06) [INTENT: roles/Archaeon/CHARTER.md]: the READ side of the experiment
loop -- "PEW/SFE fossils -> Archaeon -> shared Postgres queue -> Vivarium -> Players/executor -> SFE -> PEW -> Archaeon".
Archaeon owns the fossils-to-queue arrow only, is fire-and-forget across execution, holds NO scientific authority
("not a claim judge", enforced at the queue write boundary by a regex guard), is "not an executor", and is "not a
reconstructor of hidden history". The operator placed three challenges on it: (1) the signal campaign (build an
instrument that would notice weak signal in PEW/SFE fossils), (2) random science (generate experiments when no signal
directs one, and expand the template menu), (3) program expansion recommendations. Standing constraints: no model in the
tick path, deterministic replayable proposals, <=6 autonomous proposals per UTC day per lane enforced in Postgres,
provenance outside the sealed hash, eligibility reported beside every firing.

Charter changes / pivots (each verbatim directive filed under roles/Archaeon/prompts/):
- 2026-09-08: H0-H5 program (operator brief from an external designer, "ChatGPT/Codex is the designer"; Archaeon as
  implementation lead routing seats) [HIST: prompts/2026-09-08_h0h5/DESIGN_H0_H5_v0.1.md]. Archaeon becomes de facto
  coordinator of Daedalus, Vivarium, Proteus, Herakles, Harmonia, Mnemosyne, Techne.
- 2026-09-11: Archaeon sessions author the base-role constitution (roles/base-role RESPONSIBILITIES, WORKING_CONTRACT,
  NORTH_STAR transcription, MONITORS registry, INHERITANCE) and revive the comms Postgres queue; Archaeon becomes owner of
  the comms package (D-24) [IMPL: commits 249bb0f98, 633f6989b, 71a5e3341, 7466bd6ac, 9f6bc3ae8, 8bb162a77 all carry
  Claude-Session 012yQeSybmX5Z5BmuXWmDyJe, the same session that wrote ARCH-26 and H5-1 commits; MONITORS.md row 82].
  This is GOVERNANCE/INFRASTRUCTURE, not science machinery.
- 2026-09-12/13: operator "seasons" S1-S7 + ARCH-46A (fossil metabolism / producer selection policy science).
- 2026-09-16: COMPUTATIONAL WORKSPACE ECOLOGY directive names Archaeon "lead experimentalist", widening "not an executor"
  for that program only: Archaeon launches evolutionary populations from its own code (archaeon/wse/) [INTENT: CHARTER
  2026-09-16 expansion]. Same day: SELECTIVE STATE FORMATION directive; SFE autonomous ten-experiment campaign (CMP1).
- 2026-09-16..18: CMP2, CMP3, Campaign 4 (damage geometry), Campaign 5 (escape the neutral cliff), Campaign 6 (Cambrian
  expansion / observatory stress), Deep Frontier (autonomous lineage scheduler).
- 2026-09-19: Archaeon builds its own copy of NESTOR's 72-hour Z80 x Atlas directive (DF-016), becoming the third
  independent Z80 build (alongside Nestor NPE and Bellerophon BEE) [HIST: ENGINE_LANDSCAPE s2].
- 2026-09-23..26: post-campaign repair, copier census, ENVGATE-01/02 (environment-as-variable causal assays), Phase A
  genetic attribution (taint VM). Operator frames Archaeon as an "assay/attribution LENS, not another Z80 world"
  (directive f0dd0599 s6, relayed via Cyclops #585) [HIST: RESUME.md 2026-09-25 update].
- 2026-09-26..30: PORTABILITY-01, causal lineage contract v0.1/v0.2/v0.3, ops pilot C-001 (portable Tasks on ubu001/
  ubu002), attribution v0, E-003 cross-engine ancestry replay.
- 2026-09-30 onward: fleet orders CWO-2026-09-30B/C; seat is READY, waits on Aporia dispatch; last dispatch (#1148) was
  a comms/evidence_wiki Postgres keepalive fix (infrastructure) [HIST: STATUS_2026-10-01.md].

Current/terminal role [HIST: STATUS_2026-10-01.md]: READY under CWO-C, nothing running; only hard gate is an operator
ruling on the E-003 BEE verdict of record. Achilles census marks observed role as differing from declared role:
"Recent work is cross-engine causal analysis ... plus MWO work-order bookkeeping on branches" [HIST: census
seats_part1.json].

Relationships:
- Vivarium (executor of Archaeon's queue rows; Archaeon adopted Vivarium's queue c9304ff02); Daedalus (SFE engine);
  Harmonia (adjudicator of nulls/rulers; admitted d3.v1/d3.v2, ruled C3-3, E-003 audit); Mnemosyne (PEW); Proteus
  (player VM, foundry, grammar v0.4, graph organisms; Archaeon's WSE/C1-C6 organisms ARE Proteus organisms); Herakles
  (CA libraries, template mining, critiques); Techne (tool acquisition); Nestor (CW01 T-ARCH4/T-ARCH5 continued
  Archaeon C4/C5 on the same VM; Z80 x Atlas directive author; NPE adapter target); Bellerophon (BEE; E-003 BEE leg;
  PORTABILITY BEE adapter); Ananke (PTE non-copy control for the lens); Artemis (executed E-002 from Git alone; lens
  card); Aporia (fleet scheduler under CWO); Atlas (indexes only archaeon/campaign\d+ and frontier).
- Code coupling: archaeon.workspace (D-23 workspace guard) is imported by 25 files outside archaeon/ (governance);
  archaeon.producer by 13; archaeon.wse.worlds/evolve by 10 (Nestor CW01 arch4, others); archaeon.attribution by 7;
  archaeon.z80atlas by 4 [IMPL: git grep import census]. BEE's toolkit imports archaeon.frontier/campaign6 by design
  [HIST: ENGINE_LANDSCAPE table].

Hosts: M1 (instances m1-*, ArchaeonTick scheduled task on M1, MONITORS row 14, state "UNKNOWN since 2026-09-15 20:57
UTC"); M2 from 2026-09-16 (packets say "M2 / SPECTREX5"); compute offload to ubu001/ubu002 via Fabric from 2026-09-27.
[UNKNOWN / CONFLICT] STATUS_2026-10-01.md heads itself "Seat: Archaeon (M2 / SKULLPORT)", while the Achilles census
records SKULLPORT as M1 (Aporia, Atlas sources) and every Archaeon packet from 09-16..09-29 says M2 = SPECTREX5. Either
the 10-01 status mis-names the host or the alias mapping is wrong; not resolved here.

## 2. Engine / system inventory

Science machinery (each built by Archaeon; sizes from `wc -l`; archaeon/ total ~51.4k non-test Python LOC, ~8.1k test
LOC, 1,823 files) [IMPL]:

E1. v0 fossil-to-queue producer and detector suite.
  Paths: archaeon/{run,fossils,fossils_b1,rank,propose,explore,cadence,clock,queue,vivqueue,provenance,proteus_link,
  calibrate,calibrate_d3_null,stage0_fragility_survey,synth,stats,config}.py; archaeon/detectors/d1..d6; archaeon/
  migrations/001-004; archaeon/deploy/archaeon_tick.cmd + register_archaeon_tick.ps1; archaeon/producer/{tick,loop,
  templates,specbuild,kindspec,allocation,acquisition,costs,census,fossil_census,fossil_inference,readers,
  health_report,chaos,randomgen,universe,work_budget,...} (~8.3k LOC); templates/bitstring.uniform.v0.json.
  Purpose: read SFE engine.db (SQLite) and PEW (Postgres ew.fossil_*) through data-defined CoordinateCharts, run six
  arithmetic detectors, rank, emit one cadence-limited proposal into the Postgres queue (later viv.research_experiment_
  queue), or explore by coverage when nothing fires. Entrypoints: `python -m archaeon.run --census-only|--dry-run|
  --enqueue`; ArchaeonTick (Windows scheduled task every 15 min, M1). State: stateless per tick; Postgres
  archaeon.cadence_gate, archaeon.cadence_log; queue rows. Major versions: thresholds v0 -> calibration-fixed v0;
  d3.v1 admitted 2026-09-10 (D-20), d3.v2 admitted by Harmonia #259 (2026-09-14). Inputs: SFE observations, PEW
  fossils. Outputs: queue rows with source_evidence provenance. Scale: corpus of a few thousand rows (3,241 scored
  observations 09-05; 2,949 attested 09-10).

E2. H0-H5 producer campaigns (Archaeon side).
  Paths: archaeon/producer/{campaign,campaign_c3,campaign_c3_3,c3_readout,c3_null_adapter,campaign_h1h0,h1h0_readout,
  campaign_h5,h5_decoders,h5_reference,h3_replay,h3_dead_stream,d3_dossier,exchangeability_table}.py; archaeon/docs/h0h5/
  (readouts, issue receipts, preregs). Purpose: issue human-approved batches to Vivarium kinds built by other seats
  (ca_density_v0 over Herakles evca; cegis_boolean_v1; eca_rule_eval_v1; bitstring) and read results back. Archaeon did
  not own the substrates.

E3. Fossil-metabolism producers (seasons S1-S7, ARCH-46A).
  Paths: archaeon/producer/{s4_producers,s5_producers,s5_coordinates,s6_endgame,s7_gated,work_budget}.py; docs/h0h5/S*_*.
  Purpose: compare experiment-selection policies (uniform U, greedy expected-remaining G, W, M, exact optimum O, gated
  v2w) on a hidden-bitstring identification world with exact Hamming feedback. Pure CPU, exhaustive/exact.

E4. WSE -- workspace/serendipity ecology substrate.
  Paths: archaeon/wse/{worlds,evolve,economics,controls,interventions,reachability,corridor,states,telemetry,digest,
  survey,ssf,ssf_readout,readout,engine_descriptor}.py (~3.3k LOC); DESIGN_v0.1..v0.4; ledgers/{wse-survey-v01,ssf-c1..c3}.
  Purpose: genetic-algorithm populations of Proteus player-VM organisms on an event-stream world grammar (W0-W10 knobs)
  under a cost-vector fitness. Also hosts the reachability table (1,265 rows) and corridor table (155 rows).

E5. SFE campaign harnesses CMP1-CMP3.
  Paths: archaeon/campaign1/sfe01..sfe10.py, LEDGER.jsonl, DECISIONS.md; campaign2/ (C2-SFE-01..10, PHASE-A, c2base,
  runner.py); campaign3/ (C3-SFE-01..10, c3base, ladder). Purpose: preregistered 10-slot campaigns on E4's loop with the
  SFE v2 engine (M2 instance eng_906356f7fb1da180131f9290, schema 8) as citable record. Attempts/receipts per slot.

E6. Campaign 4/5 harnesses (damage geometry; Representation B).
  Paths: archaeon/campaign4/ (C4-01..10, C4-REH-1, rehearsal/, DAMAGE_GEOMETRY_MAP.{md,json}, DECISIONS D4-001..014);
  archaeon/campaign5/ (C5-01..10, repb/ -- narrow encoding with FAIL/FIZZLE fault semantics, grammar B, EvolutionB).

E7. Campaign 6 observatory and generators.
  Paths: archaeon/campaign6/{segment,substrate,schemas,c6base,g6_0_rehearsal}.py; observatory/{detectors,fingerprint,
  calibrate,calibrate_population}.py; worlds/{generator,runtime,fixtures}.py (Axis W composed worlds, 10 features);
  pressure/schedules.py (Axis P); ~1.9k LOC. Eleven detectors (FIRE/QUIET/UNABLE), T0 fingerprints, tiered freezes,
  segment loop with checkpoint contract. Axis O (graph organisms) was delegated to Proteus (proteus.graph_organism.v1).

E8. Deep Frontier lineage scheduler.
  Paths: archaeon/frontier/{scheduler,loop(superseded),allocation,queues,nominate,ingest,integrity,capabilities,digest,
  migrate_specs}.py; design/{boom,boom_readout,measurement,artifact_worlds}.py; registry/{LINEAGES,EVENTS}.jsonl (353 /
  313,119 lines); digests/; ALLOCATION_RULES_frozen.json. Purpose: autonomous code-first scheduler of "lineages" of
  experiment specs with exploration/exploitation/audit pools; ran under Windows Task Scheduler (DeepFrontier) from
  2026-09-19; 3,719,136 evaluations by 2026-09-21T2054Z [RESULT-UNVERIFIED: digest].

E9. Z80 x Atlas campaign engine (Archaeon build).
  Paths: archaeon/z80atlas/{vm,tasks,engine,grammar,scheduler,packet,preflight}.py; census/{copier_census,report}.py;
  denovo/run_denovo.py; postcampaign/{adjudicate,replay,close_moat_ledger,freeze_evidence,render_md}.py; ~3.1k LOC.
  Purpose: 72-hour frozen-grammar combinatorial search over byte-VM organisms, world topology, reproduction physics and
  pressures, with mechanical flags -> promotion. 101,003 runs, 31,522 families, 24 worker processes [RESULT-UNVERIFIED:
  CAMPAIGN_PACKET header].

E10. ENVGATE / lineage attribution / RIE.
  Paths: archaeon/envgate/{engine,block,ruler,mechanism,analyze,run_assay,forensic_replay,lineages,sensitivity,
  preflight}.py; archaeon/envgate2/{run_assay,launch_ops,analyze,mechanism,preflight}.py; archaeon/lineage/{taint_vm,core,
  assay_block,audit_envgate01}.py; archaeon/rie/{world,physics,campaign,analyze,preflight}.py. Purpose: paired
  environmental-intervention assays on the frozen z80atlas physics with random-tape inflow chambers; byte-level taint
  attribution ("four identities per birth"); RIE-01 staged, never frozen or launched.

E11. Causal lineage lens / attribution v0.
  Paths: archaeon/causal_lens/ (CAUSAL_LINEAGE_CONTRACT v0.1, v0.2, schema_v02/v03, adapters for archaeon/BEE/NPE/PTE,
  corpus, FALSE_FRIENDS.md FF-1..FF-34, deep_block/, pivot review packets); archaeon/attribution/ (schema A1-A17
  validator, classify, fixtures, regression, guards, probes th013/th015); ops/campaigns/C-001/ (main) and
  ops/campaigns/C-001/ATTRIBUTION_ARC_2026-09-28/ (branch origin/archaeon/attribution-arc-2026-09-28, 85 commits ahead,
  not merged). Purpose: substrate-neutral event-level attribution of reproduction-like events across three Z80
  implementations and a non-copy control.

Governance / infrastructure built or maintained (NOT science machinery; listed so it is not mistaken for it):
- I1. comms package (Postgres schema comms: messages with sha256, receipts, task queues, agents table, instance tags)
  [IMPL: 7466bd6ac, 9f6bc3ae8, 10b75cbb0]; owner per MONITORS row 82; keepalive fix 2c8c81bbb (branch, not merged).
- I2. roles/base-role constitution text (RESPONSIBILITIES, WORKING_CONTRACT, MONITORS, INHERITANCE, reanimation rulings
  D-25) [IMPL: commits listed in s1].
- I3. archaeon/workspace.py (D-23 workspace invariant guard; fails closed) and archaeon/conformance.py (four-state
  conformance gate wired at every Archaeon work boundary, 16437e31a).
- I4. Coordination artifacts: H0H5_STATUS.md, BACKLOG_H0H5.md, delegation/backlog prompts for 7 seats, review-seats
  reports, DECISIONS_BROADCAST, MWO/CWO WORK_STATE bookkeeping (branch archaeon/mwo0001-2026-09-28).

## 3. Architecture

Archaeon's code is four architecturally distinct families that share only conventions (preregistration files, sealed
digests, attempts/receipts, typed dispositions). They should not be read as one engine.

### 3.1 Family A -- the v0 producer (fossils -> queue)

What constitutes a world: an SFE "world" (a tenant/ledger grouping); for detectors a world is a REGION key chosen by a
CoordinateChart (sfe.candidate_score.v0: region=world_id, coords=(spec.candidate,), metric=content.score;
pew.phenotype_score.v0; sfe.proteus_player.v0 with real ordered axes tape_words/n_regs/genome_instructions/tick_budget)
[IMPL: docs/ARCHAEON_V0.md s2]. Organisms: none of its own -- "players" are Proteus organism_ids bound via artifact
join, generation-0 specimens only (proteus_link.assert_use_a_only refuses bred organisms). Data flow: SQLite read
(ordered by ledger anchor, not wall clock) -> per-independent-unit aggregation (added after Harmonia's repeat-blocker
finding: 6.4x false-alarm inflation from counting repeats) -> six detectors with eligibility census -> merge signals
sharing a probe target -> score = w[intent] + effect + saturating support -> fixed detector->probe table (REPLICATE,
INTERPOLATE, RESAMPLE, CROSS_REPLICATE, REPEAT_OUTLIER, BISECT) -> spec built from a template -> cadence-checked
enqueue. Exploration fallback: coverage-biased choice among legal (region, player) cells already instantiated in the
record, seeded by sha256(corpus_hash|utc_day). Cadence enforced three ways in Postgres (ordinal unique index, FOR UPDATE
gate row, DB-clock 4 h check). Negative-authority guard = regex over strings at write boundary [IMPL].

Where design and implementation disagree: the charter's loop is "fossils direct experiments"; in implementation the
fossil-to-experiment arrow never carried information into a real proposal -- see s9 T1. Exploration "cannot propose an
unobserved combination" by construction [IMPL: ARCHAEON_V0 s8 item 5], so the "random science / expand the menu"
challenge was never implemented in the tick path; menu expansion happened offline (69 mined templates, 68 of them
expansion requests, commit 19ad79d2e).

### 3.2 Family B -- Proteus-VM evolutionary harnesses (WSE, CMP1-3, C4, C5, C6/frontier)

Organism (genotype): a Proteus player MANIFEST (content-addressed): genome = list of 32-bit words, length multiple of 4,
[4, 4096] words; n_regs [2,16]; tape_words [16,4096]; tick_budget [8,65536]; out_cap [1,256]; persist in {none, regs,
tape, all}; code_writable flag [HIST: WSE architecture packet s2.1; the VM itself is Proteus's, proteus/foundry/vm].
Phenotype/execution: genome copied to the front of the tape and run in place (self-modification possible); instruction
= 4 words (op,a,b,c); opcode = word mod 25 -> TOTAL interpreter (every word sequence is a legal program); 25 opcodes in 9
categories (NOP HALT YIELD LDC MOV LD ST ADD SUB MUL AND OR XOR NOT SHL SHR EQ LT JMP JZ JNZ IN INQ OUT RND). No call/
return, no stack, no dedicated memory opcode; LD/ST address the tape by register content. Mutation: Proteus grammar
v0.4, 12 operators with frozen masses (operand_perturbation .198, replacement .125, deletion .115, insertion .083, ...
splice .052, duplication .042), one mutation per child by default. Selection: N=200, tournament size 4, elitism 4,
E=16 episodes per battery; fitness = reward - alpha*ops/1000 - beta*persistent_words/64 - gamma*io/100 (regime E0 =
reward only); reward = fraction of ASK events answered exactly; common random numbers across arms by default.
World: an event-stream grammar -- PUT/ASK/ASKX/ASK2/ASKO/SETOP/DEF/NOISE events over K streams, value_bits 4 (chance
1/16), delays, interleaving, distractors, retirement, train/held-out tag vocabulary split, identities drawn fresh per
episode [HIST: WSE packet s2.3]. Record: SFE engine (worlds, artifacts with maturity blocks, isolation policies,
idempotency keys) as the citable ledger, not as compute.
Instrument layer (built over CMP1-3): reachability table with FLOOR/SHELF/SUMMIT classes and 48-episode held-out
confirmation; corridor table; typed failure states computed before reading results (ENGINE_FAILURE ... UNDERPOWERED) and a
disposition ladder INCONCLUSIVE < CAPABLE_NEGATIVE < WEAK_POSITIVE < SUPPORTED_POSITIVE (SUPPORTED requires n>=10 and
every declared falsification attack survived; never reached) [HIST: WSE packet s4].
C5 Representation B: same 25-opcode table but narrow encoding (opcode word defined iff < 25; register field iff <
n_regs; else FAULT), FAIL (first fault ends evaluation) or FIZZLE (fault skipped and counted); grammar B with in-range
redraws [HIST: C5 packet s1].
C6 composed worlds: 0..10 feature modules (resources 1-6 types; locality 2-12 nodes; objects 1-6 cells; delayed d 1-6;
hidden noise 0-0.6; hazards; history k 1-6; coupling = shared pools across organisms of one generation evaluated in
sequence (the endogenous-pressure source); regime changes; 2-4 output channels); 24 ticks per episode; procedural
sampler with uniform complexity bins [IMPL: campaign6/worlds/generator.py, runtime.py]. Pressure schedules (stable,
step, drift, periodic, catastrophe, redistribution, migration, opportunity, unlabeled random walk) [IMPL: pressure/
schedules.py]. Graph organisms from Proteus (modules callable by reference, typed ports) [HIST: PLAN.md Axis O; DF-006].
Deep Frontier: lineage registry (append-only JSONL), four queues, frozen allocation (.40/.40/.20 initial; floors;
epoch 1e5 evaluations or 24 h), scheduler that executes specs and branches only on "evidence controls" after an
ADMITTED ruler fires, design modules authored by Archaeon (P-boom, W-artifacts), integrity halts, receipts per chunk.
[IMPL: frontier/scheduler.py line 178] ADMITTED is a hard-coded tuple (unexpected_transfer, lineage_discontinuity,
behavioral_novelty, environmental_modification, niche_divergence, regime_persistence); the C6 admission packet itself
says behavioral_novelty is "NOT admittable by the letter" and thresholds were "NOT frozen until Harmonia admits". No
Harmonia admission of these rulers was found [UNKNOWN; see s7].

### 3.3 Family C -- Z80 byte-VM ecology (z80atlas, census, envgate, lineage, rie)

Organism: a 32- or 64-byte tape; any byte decodes (op = byte & 31, r = (byte>>5)&3, hi = byte>>7); 32 opcodes incl. LD/
ADD/SUB/INC/DEC/XOR/AND/OR/SHL/SHR/CMP, JP/JR/JZ/JNZ/JC/DJNZ/JP r, LD A,(r)/(imm) and stores, COPY (mem[C]=mem[B]; B++;
C++; NOP unless the vmcopy substrate), IN/OUT, HALT, SWAP, NEG, LD A,LEN, SEAL; four 8-bit registers A-D, flags Z,C; no
multiply; 256-byte address space: own tape [0,G), neighbour window [128,128+G) (the only place descendants can be
caused), elsewhere reads 0 and refuses writes [IMPL: z80atlas/vm.py docstring]. Registers start at 0 each execution.
World: N=128 cells; topologies well_mixed, grid_vn torus, graph (degree ~3), ring_soup, niches (4); migration
policies; resources limited/unlimited; env dynamics fixed/nonstationary/local_shift/env_mutate/env_coevolve; reservoir
flag; reproduction physics EXTERNAL (runner copies; 15% replacement/epoch), ENDOGENOUS_COPY / OVERWRITE / CONSTRUCTIVE /
PAIR_EXECUTION (descendant exists only if the organism wrote >= 90% of G into the window), ENDOGENOUS_PARTIAL (>= 1 byte,
rest randomised); pressures (implicit_survival, explicit_fitness, competence_gated, resource_gated, metabolic, exec_time,
tape_cost, novelty, qd, minimal_criterion, resource_competition, recombination); tasks none, CONST_atomic,
CONST_incremental, ECHO_forced, ECHO_abr, INC1, NEG, COND_1edit, COND_multi, ADD2; step cap 256; 1,500-4,000 epochs; copy
noise .004, background mutation .02 [IMPL: grammar.FROZEN and AXES imported read-only]. Engine asserts births ==
endogenous births under endogenous physics (integrity halt) [HIST: CAMPAIGN_CONTRACT].
ENVGATE: one held configuration (vmcopy32, ENDOGENOUS_COPY, well_mixed 128-cell ecology, implicit_survival, ECHO_forced,
local_byte mutation, fixed env, unlimited resources, empty initial ecology) plus K=2,048 write-protected inflow chambers
refilled every 64 epochs from a per-block random-tape stream (2,097,152 tapes per arm per block); arms transform the
input byte distribution (U, BAND_BLOCK 120..135, SHAM_BLOCK 156..171, BLOCK_128, RESCUE_128), byte-identical arrival
sequences across arms [HIST: ENVGATE01_REVIEW s3-s4].
Lineage attribution (Phase A): a label-propagating shadow VM (taint_vm.execute_taint) carries, for every byte and
register, the source of its VALUE (executor byte E p, neighbour byte N q, input I, constant K, zero Z, computed X{set});
it must equal vm.execute exactly or the caller refuses attribution. core.py gives every organism 32 per-byte material ids
and records four identities per birth: executor, executed material (opcode fetch counts by source), child contributors
(per byte), ecological host (executor when the template is not the executor). Genetic lineage (glin) continues the
template's lineage when the template contributed >= G/2 copied bytes, else ORIGINATES a new glin [IMPL: lineage/core.py
docstring]. This is the only per-byte material-taint tracer in the program per Atlas/E-003 records [HIST].

### 3.4 Family D -- the causal lens / attribution v0 (cross-engine)

An adapter-based contract: each engine's preserved records (or a verified replay) are mapped into a common event schema
(v0.1 frozen 13cdec715; v0.2 BODY/IDENTITY and write_governing, 4282bd706; v0.3 three-referent governance WHO/WHERE/WHAT,
194c51193). Attribution v0 schema: carrier (performers, exec_where, exec_what), production (process, channel), material
(per-locus segments with a material channel; "via" may never be location/pc/executor/label/resemblance/value_match), state
(identity by state; never licenses descent), dependence (named intervention required), capability (executed), contrast,
aggregation (parent_id only under SINGULAR_MATERIAL_PARENT: one donor >= .75, no other >= .10); validator rules A1-A17
[HIST: ATTRIBUTION_PACKET s1; IMPL: archaeon/attribution/schema.py exists]. Execution moved to Fabric/ubu001-ubu002
workers with commit-addressed code and content-addressed inputs [HIST: C-001 CAMPAIGN.md pilot findings].

## 4. World capability audit

| world | state size / dims | spatial | partial obs | stochastic | action complexity | horizon / delay | agents / ecology | env change / generation | open-ended | toy? |
|---|---|---|---|---|---|---|---|---|---|---|
| bitstring hidden-target (S1-S7) | one hidden L-bit string, L 8-32 (exact enumeration to L 10) | no | yes (Hamming score only) | target drawn per world | choose one L-bit probe | 6-12 probes | none | none | no | YES: a Mastermind-style identification puzzle; exact solvers exist; L 32 was already computationally intractable for G/W/M at the code of 09-12 |
| H0-H5 kinds (ca_density, eca_rule_eval, cegis_boolean, bitstring) | radius-3 CA rules on a ring; 256 ECA rules on a 7-ring for 8 steps; 3-input Boolean functions | 1-D ring for CA | no | IC samples | rule / program choice | 8 steps (ECA), up to 298 CA steps | none | none | no | YES: 256 ECA rules collapse to 224 classes at the declared scope; 116/116 random CA rules were structural zeros on C3-2 |
| WSE event-stream (W0-W10) | K = 1-8 streams, D events/stream, 4-bit values, E = 16 (training) / 48 (held-out) episodes | no | yes (only the current event word) | fresh identities per episode | emit one integer per tick on channel 0 | delays 0-16 noise ticks; ASKO/ASK2 compositions | none (one organism per episode); population only for search | train/held-out vocab split; no world dynamics | no | YES at the cells used: W0 (one stream) solved by register-only organisms; two-stream W2_K2 is the ceiling target |
| C6 composed worlds | 0-10 feature modules; 1-6 resource pools; 2-12 nodes; 1-6 object cells; 24 ticks | yes (small ring/graph locality) | yes (hidden, lagged channel) | seeded | 2-4 output channels (harvest, move, write, signal) | delayed consequences d 1-6 within 24 ticks | coupling: shared pools across a generation evaluated in sequence (endogenous pressure) | regime changes inside episodes; pressure schedules across generations; procedural generator | partly (generator with complexity bins) | small; richest world Archaeon built, but episodes are 24 ticks and most bins were dead for v0 organisms (e.g. bin 5 reward 0 for 40,000 evaluations, DF-012) |
| Z80 x Atlas ecology | 128 cells x 32/64-byte tapes; 256-byte per-organism address space | topologies incl. torus, graph, niches | inputs only via IN port | yes | byte programs; OUT port | tasks are single-case byte transforms; step cap 256 | yes: endogenous reproduction, overwrite, pair execution, migration, niches, resources | env dynamics incl. coevolve; no world generation beyond factor grammar | combinatorial factor grammar, not open-ended | YES: tasks are 1-byte functions (ECHO, INC1, NEG, ADD2...); a 32-byte genome; the phenomena of interest are reproduction/heredity, not reasoning |
| ENVGATE ecology | as above, one fixed configuration + 2,048 inflow chambers | well_mixed | -- | random inflow streams | -- | 65,717 epochs per world | yes (inflow + residents, host execution) | input-byte distribution is the manipulated variable | no | deliberately minimal assay world |

Precise limitations: no world anywhere in Archaeon's tree exceeds a few thousand bits of world state; none supports
learning within a lifetime beyond persisted registers/tape (Proteus) or nothing (Z80, registers zeroed per execution);
no adversaries except the population itself (C6 coupling, Z80 overwrite/pair physics); no transfer between worlds other
than transplanting genomes (z80 verify swaps; WSE corridor/import; C4-09/C5-02 lateral rescue). The most capable world
family (C6 composed worlds) was only ever exercised by the Deep Frontier scheduler under unadmitted rulers.

## 5. Organism capability audit

Proteus player VM (Families B; the substrate of WSE, CMP1-3, C4, C5, C6, Deep Frontier):
- Has: registers (2-16), a writable tape (16-4096 words), indirect LD/ST, conditional jumps, I/O channels, RND,
  configurable persistence across ticks (none/regs/tape/all), optional writable code region (self-modification).
- Lacks: call/return or a stack (no subroutine reuse except by jump structure), any learning rule inside a lifetime,
  sensors beyond the integer words the world writes, recombination by default (one mutation per child; crossover only in
  C4-06 mate-splice), developmental process, internal simulation. Reproduction is external (GA).
- Measured fighting chance: the operator's working-memory target (hold K values keyed by tag across interference) is
  expressible in principle with LD/ST on a tape [CODE-INFERRED], but in three campaigns the two-stream cell (W2_K2) was
  never summited: 0 confirmed summits in 60 runs across budget (G300), seeded, all-or-nothing payoff and corridor attacks;
  shelf elites remember ONE value (first-put 6/12, last-put 4/12); 1 improving child in 4,800; 0 of 58 second-stream gains
  kept the first stream [RESULT-UNVERIFIED: WSE packet s7.1-7.2]. The total interpreter means opcode words from the foundry
  are 932/932 outside the table and P(would-be-fatal) = 1.000 in 7,146 children -- there is no local failure event, so
  damage is reinterpretation [RESULT-UNVERIFIED: C4 packet s1]. Archaeon itself asked whether "ANY of this is the right
  substrate for working memory" (WSE packet Q3) and named the untried lever: change the organism or search operator
  (C4-3 recommendation). C4/C5 then changed the encoding (Representation B) but not the addressing/memory primitives.
  Assessment: a narrow chance at single-register recall; no demonstrated chance at keyed multi-value memory under this
  search; the ceiling is not shown to be an organism limit vs a search limit (both unchanged together).

Z80 byte VM (Family C):
- 32 or 64 bytes of genome, 4 eight-bit registers zeroed per execution, step cap 256, COPY primitive in vmcopy.
  Tasks are single-byte input-output functions. Self-replication is the phenomenon of interest; random 32-byte vmcopy tapes
  are exact self-copiers at 9.6e-6, 99% input-gated (mostly at input byte 128 = the window base) [RESULT-UNVERIFIED:
  COPIER-CENSUS-01]. z80 substrate (no COPY): 0 exact copiers in 1.2e7 tapes.
- Fighting chance for a nontrivial reasoning primitive: essentially none by architecture (state capacity and task set);
  the substrate is fit for questions about reproduction, hosting and heredity, which is how Archaeon ultimately used it.

Graph organisms (Proteus, C6/frontier): modules callable by reference, typed ports, per-node state [HIST: PLAN Axis O].
Graph populations fired "two orders of magnitude less" at v0-calibrated thresholds (DF-012) and reached max .375-.5 on
WSE cells; no capability result exists [RESULT-UNVERIFIED].

Bitstring candidates (S1-S7): not organisms; the "agent" is the producer policy choosing probes.

## 6. Search and pressure mechanisms

- v0 producer: detector-directed probes or coverage-biased exploration over already-instantiated cells; templates
  drawn uniformly within a region (bitstring.uniform.v0, "the frozen random baseline"). Bottleneck: legal cells come
  only from the record (cannot bootstrap coverage); region-directed templates never admitted.
- S-seasons: exact information-seeking objectives (expected remaining |T|, entropy tie-breaks, exact DP optimum O,
  gated v2w refinement). Bottleneck: endpoint saturation (S3), myopia of one-step ER at large L, computational
  intractability at L 32.
- WSE/CMP: tournament GA with grammar mutation, elitism, CRN; curricula (delay ladder 0->1->2->4 with rung hold);
  imports/injection of mature artifacts; producer-consumer arms; cost-vector economics (E0-E3, S1/S3 ramps). Collapse
  modes measured: cost-before-capability extinction (E1-E3 extinguish persistence by generation 3-10 on flat reward, 18/18
  cells); ramp triggers firing on noise; constant-answer hacks (CONST0 "forget" cell); import takeover by ANY organism
  including opcode-permuted incompetent controls (11-12/12 within ~3-8 generations; only an offspring cap slowed it); half-
  credit shelf; basin-share geometry not a knob.
- C4/C5: neutral walks (188 walkers to depth 16; 47 x 6 walkers to depth 64), mutation-radius curves, recombination vs
  mutation, lateral ecology rescue, Representation B faults. Collapse: selection builds neutrality/length rather than
  preserved variation; no valley crossed (0/6 vs 0/6 in C4-06); rescue = takeover without improvement (0/24 cells).
- C6/frontier: procedural world generator, pressure schedules, seeded random audit branching, exploration/exploitation
  pools, operator-ruled pursuit multipliers. Collapse: controls spawning controls (11 of 19 runs, DF-012); rulers firing
  on nearly every evaluation (structural_reuse 1.66M and detector_disagreement 1.75M firings over 3.72M evaluations by
  09-21) [RESULT-UNVERIFIED: digest] -- escalation saturation.
- Z80 x Atlas: frozen factor grammar, sparse sampler with exploration floor .30, mechanical promotion (flag weights;
  threshold 3), one-factor mutation and crossover of factor vectors, LATE verification with transplants. Collapse:
  promotion fed on mis-labelled transplant runs; sampler coupled topology to migration/reservoir (0 bare-niches worlds in
  13,313 niches draws); 8,682 promotion runs sent to niches vs ~170-209 per other topology.
- ENVGATE/RIE: no search; intervention on the environment with frozen organism physics.
- LLM/human proposals: kept out of every tick path by charter; menus shaped offline; Deep Frontier designs (P-boom,
  W-artifacts) authored by the Archaeon LLM session as code after DF-013 returned "scientific authority" to Archaeon.

## 7. Measurement / ruler stack

Family A: D1 REPEATED_SMALL_DEVIATION, D2 SIGN_INSTABILITY, D3 LOCAL_VARIANCE_ANOMALY (variance ratio band [1/3, 3]), D4
PLAYER_ORDER_REVERSAL, D5 REPEATED_OUTLIER_REGION (median+MAD robust z >= 3.5, >= 3 obs), D6 BOUNDARY_TRANSITION_HINT;
Bonferroni; eligibility census per detector; synthetic calibration at 200 seeds with paired no-effect controls and power
curves [IMPL/RESULT-UNVERIFIED: CALIBRATION.md]. Known blind spots recorded by the seat itself: D1/D2/D4 ineligible on
live SFE (no player identity), PEW chart structurally unable to fire (6,006 prod player fossils, 2 non-null scores),
candidate coordinate is a hash-like integer, Bonferroni conservatism, regex negative-authority guard, no ledger-chain
re-verification. D3 band is a phase boundary (Harmonia be9c22959); D3 cannot resolve the M-ELIGIBLE arm contrast (true
ratio 1.167).
Family B: per-ask exact-answer reward; held-out confirmation (48 episodes); reachability classes (Wilson bands);
corridor edges; typed failure states; disposition ladder; kill conditions and replacement conditions in every sealed
prereg; equal-total-compute controls (C5); world pre-solution screen ([3/16, .70) best held-out over 57 parents, C5);
damage labels D0-D7 (D7 = improvement) on 16-episode answer vectors (Hamming displacement); C6: eleven detectors with
FIRE/QUIET/UNABLE (behavioral_novelty, lineage_discontinuity, unexpected_transfer, structural_reuse, environmental_
modification, niche_divergence, regime_persistence, unexplained_gain, unexpected_causal_dependence, detector_disagreement,
classifier_failure), calibrated at a 1% false-fire rule. Population-stage calibration: novelty threshold catches 25% of
planted W0 solvers, discontinuity 0% of planted small-edit jumps [RESULT-UNVERIFIED: campaign6 D6-010] -- i.e. weak
positive controls.
Family C: mechanical flags (spontaneous_replication, moat_crossed, moat_advantage, compression, new_arch_events,
coexistence, longevity, transport, env_lineage, ruler_gain, persistence_over_control, exploit); positive controls 6/6
(replicator replicates; external reproduction evolves; seeded endogenous invades) [HIST: DF-016]; matched controls
generated by grammar.matched_controls. Post-campaign: provenance v1 (founder origin classes travel with material),
first_clean_crossing, copier census ruler classes (INERT/TOUCH/WRITER/NEAR/SPAN/EXACT_GATED/EXACT_UNGATED); ENVGATE:
arrival-level exact McNemar with Holm, block-level sign tests, Page's L, copier-founded vs host-labelled establishment,
genetic establishment (an HU alive 3 x max_age after its root is gone, peak >= .25N or depth >= 10), legacy byte-identical
replay admission, code-hash pinning of 14 files before launch.
Family D: lens portability classes (NATIVE/DERIVABLE/APPROXIMATE/NOT_IDENTIFIABLE/NOT_APPLICABLE), validator A1-A17,
known-answer fixtures (TH-014: six histories with identical child bytes -> six production classes), adversarial reviews by
isolated workers, saturated-ruler guard, agreement checks owner-vs-Archaeon tracers (E-003: >= .995 required).
Blind spots / failures recorded: label-reading predicates (spontaneous_replication read the run's init label); parent-
chain counts inflate establishment 8-42x; count-fixing damage rulers manufacture length effects (s9 T7); training-
battery luck (16 episodes; a .9375 read .53 held-out); hidden seed in run_id (P-boom); C6 rulers saturated and largely
UNABLE (unexpected_transfer, regime_persistence, unexplained_gain, unexpected_causal_dependence UNABLE on 1,775,074
evaluations each by 09-21) [RESULT-UNVERIFIED: digest].

## 8. Experiment inventory (grouped into campaigns; labels describe the historical record, not a verdict)

C-01 v0 calibration and Stage 0 (2026-09-05/06). Question: can the detectors fire correctly, and can the real SFE
corpus form S17 prospective-fragility claim units? Organism/world: none / SFE bitstring corpus. Measurement: synthetic
null/planted/control corpora (200 seeds); Stage 0 eligibility over 3,241 observations. Result: four detector defects found
and fixed (D1 empty band, D1 sign rule, D2/D4 materiality without resolution, D6 gradient blindness); Stage 0 KILL -- 0
eligible claim units at every threshold (groups with structure have no data, groups with data have no structure).
Paths: archaeon/docs/CALIBRATION.md, STAGE0_RESULT.md, ledgers/stage0_survey_2026-09-05.json; commits df0837064, ecfef4d87.
Label: INSTRUMENT FAILURE (calibration) / INCONCLUSIVE (Stage 0, corpus-structure KILL).

C-02 Live producer loop and fossil-direction dry runs (2026-09-06..09-12). Question: does the producer run end to end,
and does prior evidence change proposals? Arms: ArchaeonTick every 15 min on M1, 6/day quota. Scale: 11 completed
experiments by 09-10, all bitstring.uniform.v0. D3 fired on 30 of 77 eligible regions (28 lower-dispersion). Evidence-link
dry run: draw byte-identical with and without the corpus; directable-regions dry run: 0 of 26 fired regions carry a
recoverable length, 21 directable regions each hold one observation -- detectors and region-directed policy act on
disjoint populations. Canary prereg + fossil vision check (63 ticks at 1,029 rows; negative control reproduces blind
read). HARM-13 exchangeability table on the M2 ledger (2026-09-18): 0 eligible on D1/D2/D4/D5/D6. Paths: docs/h0h5/
D3_LIVE_DOSSIER_2026-09-10.json, EVIDENCE_LINK_DRYRUN_2026-09-12.json, DIRECTABLE_REGIONS_DRYRUN_2026-09-12.json,
CANARY_*, EXCHANGEABILITY_D1_D6_2026-09-18.md; commits 4bcf72dc9, a7b9dd46d, 0fb74ea8c, 7e4682cab, 7017dc79e. Label:
REPORTED NEGATIVE/NULL (the signal path never directed an experiment).

C-03 H0-H5 alpha issues (2026-09-09..09-16). Questions: H0-H5 of the operator brief (failure transport, component reuse,
CA stateful components, retention policy, adaptive challenge, learned encodings). Sets: cs-c3-1 (126 rows cancelled after
producer error ic_density_set null vs [null] -- INSTRUMENT FAILURE), cs-c3-2 (150 rows: exact-symmetry null IDENTICAL
18/18; 116/116 random radius-3 rules structural zeros; D3-over-C3-acq declared STRUCTURALLY VOID per Harmonia),
cs-h1h0-1-p2/p2b (73 rows; solved of 12 targets: fresh 2, random_pack 2, S00 2, S10 2, S01 3, S11 3; every unsolved row
BUDGET_VM_OPS at cap 6000; H1 contrast "transport_only, relevance inert at this scope"), cs-h5-1 (256 ECA rules, 224
classes, 0 disagreements with the published map; reach numbers at their ANALYTIC bounds -- "calibration, not evidence"),
ARCH-26 H3 dead-stream control (coverage identical live vs score-permuted dead; score-threshold reuse measures the score
marginal; task reuse separates by +1.4..+1.8 at a ceiling of 12/12), C3-3 preflight NO-GO then option-B GO, rows HELD
(5 queued rows held 09-16, fc7bd9070). Paths: archaeon/docs/h0h5/{C3_2_READOUT.md, H1H0_PHASE2_READOUT.md,
H5_1_READOUT_2026-09-11.md, H3_DEAD_STREAM_READOUT_2026-09-11.md, C3_3_*}; commits 50a0591a6, 9e56985ce, 8b78f1b5d,
6fc3ea619, 179cd46e4. Label: INCONCLUSIVE (every set is calibration, structurally void, or at ceiling; nothing licensed).

C-04 Fossil metabolism seasons S1-S7 + ARCH-46A (2026-09-12/13). Question: does consulting fossils improve experiment
selection, and can an information-seeking producer be repaired without regression? World: hidden L-bit target, exact
Hamming feedback. S1: 12 matched pairs, fossil one-bit-flip F vs uniform C: 8 wins / 4 losses, p = .194 ->
NO_DETECTABLE_ADVANTAGE. S3: 120 synthetic worlds -> NO_ADVANTAGE_OVER_UNIFORM (endpoint saturated; the seat calls it a
design error and keeps the verdict). S4: 240 worlds, four producers -> NO_SEPARATION among G/W/M while all beat U. S5: two
runs, both INSTRUMENT_FAILURE by own rule (seed carried target_index; then a no-tolerance universal clause). S6:
CHEAP_REPAIR_WITH_REGRESSION. S7: GATE_FAILS_TO_ISOLATE (one L8 state worse). ARCH-46A (exact rational v2w): the regression
was a float tie split; 3 of 49 S7 L9 improvements were also float luck; verdict LICENSED_ENDGAME_REPAIR (aggregate probe
reduction ~2-4% inside the gate). Paths: docs/h0h5/S1..S7_*, ARCH46A_*; commits bc6e8c13d, 7f19d77c3, 0b255eb70,
80b807738, ab2d40cef, fd5248805, e6cbbdeef. Label: MIXED (the producer-selection question: NEGATIVE; the endgame repair:
REPORTED POSITIVE of small size on a toy).

C-05 WSE survey v01 (2026-09-16). Question: which event-stream cells and economics produce adaptation? 18 cells x
E0..E3 x 3 seeds = 126 rows, N=200 G=100 E=24, 1,532 s. Result: under any cost regime E1-E3 every cell in every seed
ends persist=none, reward 0 ("cost before capability is extinction"); under E0 only trivial recurrence (register-only
solvers) on W0/W1/W2/W3 cells; nothing seed-stable above the floor. Paths: archaeon/wse/READOUT_v01.md, ledgers/
wse-survey-v01; commit b7518c392. Label: REPORTED NEGATIVE/NULL.

C-06 SSF Selective State Formation cycles 1-3 (2026-09-16). Question: does a priced selective memory evolve where hand-
written organisms show the economics should favour it? Boundary map: selective organism beats logger and last-value by >=
.10 on 7/7 runnable cells under S1/S3 -- before evolution. Evolution: 0/60 naive de-novo footholds (cycles 1-2), 2/9 at
512x200 (cycle 3); only transferred last-value register solvers lived. Paths: archaeon/wse/READOUT_ssf.md, DESIGN_v0.2-
v0.4, ledgers/ssf-c1..c3; commits 806907ab8, 190ab0756, 204b031c4, 37ca43bd4. Label: REPORTED NEGATIVE/NULL.

C-07 CMP1 SFE autonomous ten-experiment campaign (2026-09-16/17). Ten slots (SFE-01..10), n=3 per arm, 6 h 20 min.
Reported: 7 COMPLETE (2 negative), 3 INCONCLUSIVE (assay incapable: cell unreachable). Science claim: "mature, whole
material helps; fragments and failures do not" (components 2/3 vs random 0/3; failed-residue 2/3 vs 0/3; producer
foothold at generation 30 vs 50); curricula +.155/+.113; encoding with most accessible variation was slowest.
Paths: archaeon/campaign1/CAMPAIGN_REPORT.md, SFE-01..10; commits 7508b0aff..0728e9989. Label: LATER OVERTURNED (in
part): two of its weak positives died at n >= 10 in CMP2, and CMP3 showed any imported organism takes over (s9 T4).

C-08 CMP2 (2026-09-16/17). Ten slots, n=6 to 52, 13 live attempts, 0 engine errors. 7 CAPABLE_NEGATIVE / 3 WEAK_POSITIVE
(retention economics on a delay ladder; producer-consumer with maturity gating at the margin; CA substrate particle2 -
random = +.079, 4/4). Killed CMP1's components (+.009 at n=12) and failed-genotype seeding (+.002 at n=10). Paths:
archaeon/campaign2/CAMPAIGN_REPORT.md; commits 08def2be3..4d80d4b1d. Label: MIXED.

C-09 CMP3 (2026-09-17). Ten discriminating slots (24-228 runs each). 7 CAPABLE_NEGATIVE, 2 WEAK_POSITIVE (delay corridor
ladder; corridor map), 1 INCONCLUSIVE (basin share out of family: pooled rho -.568 is a two-point correlation). Findings:
two-stream ceiling (0 summits / 60 runs); shelf = one-value memory; delay ladder builds delay invariance (11/12 seeds;
general elites read untrained delays 8 and 16 at held-out 1.0, direct search 0/6 and 1/6); import takeover is mechanics
(incompetent opcode-permuted controls take over 11-12/12); CA delayed-recall effect reproduced by a hand-designed rule and
survives lattice permutation in 5/8 seeds. Paths: archaeon/campaign3/, roles/Archaeon/REVIEW_PACKET_WSE_ARCHITECTURE_
2026-09-17.md, REVIEW_PACKET_CMP3_2026-09-17.md; commits 6592f9d66..cb9135104. Label: MIXED (mostly NEGATIVE; one
reproducible positive capability -- the delay-invariant reader -- whose meaning is unresolved).

C-10 Campaign 4 damage geometry and evolvability (2026-09-17/18). Ten sequential slots on the frozen substrate, 1,255 engine
records, 0 errors; rehearsal C4-REH-1 (48 rows, 1,152 observations exactly once through two engine kills) as gate G2.
Results: no single edit improved any of 57 parents (D7 0/5,472); displacement bimodal; loss monotone .52 -> .99 over
radius 1-16; neutral network fully connected (188/188 walkers to depth 16; exaptation .016 -> .043); recombination 0/6 vs
0/6 crossings; selection builds neutrality and length (single-edit loss .419 ancestral -> .185 -> .125; length 19 -> 40 ->
62); lateral rescue = takeover; two slots REPRESENTATION_BLOCKED (total interpreter has no fault event). Campaign
disposition NO_CONDITION_SELECTED; worlds in C4-09/C4-10 were pre-solved by the starting parents (defect recorded).
Execution did NOT go through Vivarium for science rows (no queue kind evaluates a program variant; I-6). Paths:
archaeon/campaign4/{CAMPAIGN_REPORT.md, DAMAGE_GEOMETRY_MAP.md, DECISIONS.md}, REVIEW_PACKET_CAMPAIGN4_2026-09-18.md;
commits 9632e95f8..8f1a82ced. Label: REPORTED NEGATIVE/NULL (with descriptive maps later challenged, s9 T7).

C-11 Campaign 5 escape the neutral cliff (2026-09-18). Phase A: deep walk (exaptation .050 -> .082 over depth 16 -> 64,
yield per evaluation below a random single edit; MIXED); fair lateral ecology at equal total compute (0/24 cells improved;
OLD_SUBSTRATE_EXHAUSTED). Phase B: Representation B qualified only under one labelled post-hoc amendment (F3 statistic
changed from fault counts to fault sites); real local recovery at single-edit level (229 replicated recoveries vs 154
insulation losses); insulation cheap for the survivor; length (not dead code) carries robustness; reach at equal compute
0/+1/+1 nets over 24 cells each -> BOUNDARY_CREATED_NO_DISCOVERY_GAIN, accepted by operator (D5-015). Paths:
archaeon/campaign5/, REVIEW_PACKET_CAMPAIGN5_2026-09-18.md; commits f01a00f58..cdb55e152. Label: REPORTED NEGATIVE/NULL
("flat elite" later questioned, s9 T6).

C-12 Campaign 6 Phase 0 observatory (2026-09-18). Built eleven detectors, T0 fingerprints, segment loop, composed worlds,
pressure schedules; three calibration rounds plus population-stage rounds 4-6; G6-0 rehearsal (Archaeon side GREEN on
its own proofs; escalation 139/1,280 evaluations at bin 6, 415/1,280 at bin 10). G6-0 never closed: five items
unverified (Proteus graph checkpointing, cross-boundary freezes, fixture commitments, Harmonia receipt consumption,
Vivarium segment kind) [IMPL: frontier/OPERATOR_EXECUTION_AUTHORIZED.json "G6_0_ALL_COMPONENTS_VERIFIED": false]. Phases
1-3 (scatter, blind recall by Nemesis/Rhadamanthus, return) did not run as designed. Paths: archaeon/campaign6/; comms
#461, #462, #466-#469; commits f603b3e8b..1b5c91f27. Label: INCONCLUSIVE.

C-13 Deep Frontier + P-boom (2026-09-18..09-22). Scheduler ran under OPERATOR_EXECUTION_AUTHORIZED (not a verification).
By 09-21: 119 transformations, 3,719,136 evaluations, 13 lineages; FULL freezes 56,777, PARTIAL 1,718,297. P-boom
(boom-bust spike on a bin-7 coupled world): readout 1 spike rate per 100 archived generations spread 0.17..5.67 within an
arm -> no order reading; INSTRUMENT_DEFECT: run_id was folded into random streams (experiment_id a hidden seed; no two
arms ever shared a stream); fix stream_key; readout 2 on 13 shared-stream K_ arms: within-arm variance still dominant
(K_B 0.33..7.17). C5-flat N family at 60,000 evaluations: training max .479-.562 vs C5 screen .382 (PROVISIONAL).
Paths: archaeon/frontier/{DECISIONS.md, digests/, design/BOOM_READOUT_*.json, registry/}; commits 87bd51813..939e4f39e.
Label: INCONCLUSIVE (with one recorded INSTRUMENT FAILURE).

C-14 Z80 x Atlas 72-hour campaign (2026-09-19..09-22). 101,003 runs, 0 errors, 31,522 families, 0 retired. Flags:
spontaneous_replication 26, moat_crossed 70,315, moat_advantage 3,110, new_arch_events 100,185, coexistence 52,043,
transport 35,893. Top families scored 17 via spontaneous_replication. Paths: archaeon/z80atlas/campaign/
CAMPAIGN_PACKET.md, pivot/Z80ATLAS_REVIEW_2026-09-22.md; commits c7610ea19, d50f5710a. Label: LATER OVERTURNED (all 26
headline flags were transplanted lineages; s9 T2).

C-15 Z80 post-campaign repair and rulings 1-4 (2026-09-23/24). DF-017 provenance v1; 26/26 reclassified by byte-identical
replay; corrected top-30 is a 30-way tie at 14; DENOVO-01 (prereg 8e6245036 before any run): 0/80 de-novo events, controls
21/21 PASS, every treatment world extinct (median epoch 61); FORENSIC-MOAT-01: 932/932 seeded moat replays admitted,
828 QUALIFIED / 104 VOID; COPIER-CENSUS-01 (prereg b48245002 first): vmcopy32 exact copier density 9.6e-6 [7.8e-6,
1.17e-5], predicted lambda 6.86 lottery worlds vs 1 observed -> LOTTERY_CONSISTENT; sampler fixed + launch preflight
(would have refused the campaign: 0 of 209 bare-niches draws). Paths: archaeon/z80atlas/{postcampaign, census, denovo,
pivot}; commits 299981e9a, 8e6245036, 18772241e, 6878f582d, c5067fac6. Label: REPORTED NEGATIVE/NULL (de novo) with a
REPORTED POSITIVE measured prior (census).

C-16 ENVGATE-01 environmental gating causal assay (2026-09-24). Prereg f9c0bf3ec frozen before treatment; 16 blocks x 5
arms; 33,554,432 arrivals per arm. Preregistered verdict GATING_CAUSALLY_SUPPORTED + ALTERNATE_MECHANISM; operator
adjudication R1: GATING_PARTIALLY_SUPPORTED (band 120..135 is causal; single byte 128 is not; C4 rescue came from one
takeover world, block-level p = .5). R2: host-mediated reproduction (inert host executes resident copier) stands as a
mechanism of amplification, not origination. Paths: archaeon/envgate/{ENVGATE01_REVIEW_2026-09-24.md,
ADJUDICATION_ADDENDUM_2026-09-24.md, RESULTS.json, SENSITIVITY.json, FORENSIC_REPLAY.json}; commits 58f0463b2,
f9c0bf3ec, e15e4cde6, 5649c78f8, 16111cf50. Label: LATER OVERTURNED (in part: composite frozen verdict downgraded).

C-17 ENVGATE-02 window rescue under genetic identity (2026-09-25/26). Prereg 1475b7995; 24 blocks x 5 arms (U, RRIGHT,
RWEAK, R128, BAND0); 29,973 s, 6 workers. Genetic establishments U 24 / RRIGHT 3 / RWEAK 2 / R128 5 / BAND0 5. Phase-C gate
failed on condition 6 -> WINDOW_NOT_SUPPORTED; blocking replicates (12+/2- blocks, Page's L p = .001); BAND0 and R128 came
in ~7x above the frozen viability-map prediction (unexplained); parent-chain counts 8-42x genetic counts. Execution
deviation: frozen analyze.main() KeyError; wrapper used without editing the frozen file. Paths: archaeon/envgate2/
{VERDICT_2026-09-26.md, RESULTS.json, OPS_LOG.jsonl, OPERATIONAL_INCIDENT_2026-09-24.md}, ENVGATE_CLOSURE_2026-09-26.md;
commit c5ba19571. Label: MIXED (law replicates; mechanism model fails).

C-18 PORTABILITY-01 and contract v0.2/v0.3 (2026-09-26/27). Replays only: Archaeon block 13/15 fossils (5 fossils, 54,616
births), BEE 845 traced logs (28,964,089 births), NPE 36 runs (34 pair-tape births), PTE 6,596 rows + one instrumented GA
replay. Verdict PORTABLE_WITH_DOMAIN_LIMITS (gates 8/8); disagreements preserved: BEE resemblance-vs-provenance 847,000 +
7,113 births; BEE own-code vs own-execution 38,817 native-SR births; NPE in-situ vs counterfactual authorship 12/34; 33.1%
of BEE births NOT_IDENTIFIABLE. B6: governing code WHO/WHERE/WHAT; 27,083/28,163 BEE location-foreign births are own-
material governed. Paths: archaeon/causal_lens/{PORTABILITY01_REPORT.md, V02_REGRESSION_REPORT.md, FALSE_FRIENDS.md,
pivot/*}; commits 13cdec715..aede495ad. Label: REPORTED POSITIVE (portability of the lens; not promoted).

C-19 Ops pilot C-001 (E-001, E-002, deep block) (2026-09-27). Portable Tasks: T-001 reproduced bit-for-bit on ubu001
(74,800/74,800 rows), T-002 on ubu002, T-003 NPE probe; E-001 (B6) CLOSED; E-002 (B1, hereditary continuity under
recombination) executed by a fresh Artemis worker from Git alone to a stopping point; deep block blocks A-G incl. bounded
prior-art (IBD/IBS, ARG, Hall's two concepts, von Neumann, Godfrey-Smith, Griesemer). Paths: ops/campaigns/C-001/
{CAMPAIGN.md, E-001/, E-002/, DEEP_BLOCK_2026-09-27/}; commits c8b9ea49e..4707fed67. Label: MIXED (operational
portability shown; scientific questions open).

C-20 Attribution v0 (2026-09-28). Schema + validator + fixtures + 51 tests; TH-013 block-13 replay; TH-015 transplant/
knockout interventions; item 8. Two context-free adversarial reviews withdrew claims: "only machinery-IBD survives"
(artefact of two hand-written cases), first BEE/NPE material assay (read source addresses and value matches as descent),
"near -> exact" (a fixed point of the founder's copy map). Surviving: reproduction boundary NOT found (15 cases x 9
definitions, every simple predicate fails somewhere); executed path + data (~66% of tape) must cross for copying to stay
above chance (.89 of random backgrounds capable; size-matched random graft .057). Paths: ops/campaigns/C-001/
ATTRIBUTION_V0_2026-09-28/; archaeon/attribution/; commits 3e6f281a1..f38759992. Label: MIXED.

C-21 E-003 cross-engine ancestry replay (2026-09-28..30; branch only). Question: does byte-level ancestry in BEE and NPE
validate, alter or break attribution v0? BEE (one run r022153): VALIDATED only as amended (C4.2, C4.4, C11 all made after
exposure); under pre-exposure rules ALTERED (P2 = .504 [.456, .552]); NPE leg uninformative by construction (29 births vs a
30-birth floor). Robust finding: Q8c transmission-class value dependence outside {donor, performer} .00115 [.00098,
.00134]. Unexplained dry-run vs production drift on the identical 32,827 births. Harmonia audit item H: VALIDATED NOT
SUPPORTED as a confirmatory label; owner erratum d06059735 concurs; verdict of record open for the operator. Paths:
origin/archaeon/attribution-arc-2026-09-28:ops/campaigns/C-001/ATTRIBUTION_ARC_2026-09-28/{E003_SYNTHESIS.md,
ANCESTRY_PREREG_v1..v5.md, gate_close/}; roles/Harmonia/audits/EVIDENCE_AUDIT_2026-09-30_SAMPLE2.md item H. Label:
CONTAMINATED (outcome-deciding rules adopted after exposure to the same run).

Cross-seat continuation (not Archaeon's experiments but its lineage): Nestor's CW01 reactivated Campaign 4/5 as T-ARCH4/
T-ARCH5 on the same Proteus VM (commits 7976d5ce1, bdf8c5df4; roles/Nestor/campaigns/cw01-2026-09-17/experiments/
cw01-arch4/). Note: the brief names origin branches archaeon/campaign4 and archaeon/campaign5; no such remote branches
exist at this base -- Campaign 4/5 live as directories on main (archaeon/campaign4, archaeon/campaign5) [IMPL: git
branch -r].

## 9. False-positive / false-negative archaeology (timelines)

T1. "Fossils direct the next experiment" (signal campaign).
Claim (charter, 09-05/06): Archaeon mines fossils and the signal changes the experiment (commit e3fab51cc "the signal can
now change the experiment"). -> Evidence: wiring tested; D3 fires on 30 of 77 regions (09-10). -> Challenge: evidence-link
dry run (a7b9dd46d, 09-11): the draw is byte-identical with and without the corpus; directable-regions dry run (0fb74ea8c):
0 of 26 fired regions carry a recoverable length; detectors and region-directed templates act on DISJOINT populations;
S1 (09-12): fossil-directed F vs uniform C, NO_DETECTABLE_ADVANTAGE (8/12, p .194); HARM-13 (09-18): 0 eligible on every
detector on the M2 ledger. -> Correction: none needed; the seat reported each null. -> Status: the signal->selection arrow
was never demonstrated to carry information on a real corpus. Possible false-negative regime: the corpus was structurally
incapable (no player identity, hash-like coordinates, one observation per directable region), so the null says nothing
about whether fossil-directed selection could work on a corpus designed for it. S3/S4 on synthetic worlds show that
evidence-consuming producers DO beat blind production (by .024-.091 nAUC) -- the positive exists only where the world is
a toy with exact feedback.

T2. Z80 x Atlas "spontaneous replication" (26 flags, top-ranked families).
Claim (packet 09-22): 26 spontaneous_replication flags; three families top-ranked at score 17. -> Evidence: mechanical
flag, frozen thresholds (>= 50 endogenous births, >= .25N, fidelity >= .9). -> Challenge (09-23): the predicate read
spec["init"] == "random" while verify() built transplant specs with init "random" and tapes from the source's final
population (scheduler.py:255, engine.py:153/158/371) -- every transplant source was itself a seeded-replicator run. ->
Correction: provenance v1; 26/26 replays byte-identical: repaired predicate 0/26, random founders 0 of 3,252; corrected
top-30 is a 30-way tie; DENOVO-01 0/80. -> Status: 0 verified de-novo spontaneous replication in 101,003 runs. Residual
true observation: transplanted lineages persist and self-replicate when moved (39/39) but carry NO task competence
(0/39); one random-origin input-gated self-copier world (84616cf8257b) in 27,141, explained by the census prior.
Atlas A2 lists the competence/replication dissociation as a buried signal [HIST: ATLAS_BURIED_SIGNALS A2] -- verified
against the post-campaign packet s5 (competence 0.0 in every transplant of 5b237a475b69).

T3. Moat_advantage, niches and recombination (Z80 x Atlas secondary signals).
Claim: niches topology and recombination associate with moat_advantage ("3-5x"). -> Challenge (09-23): the exploration
sampler forced migration=none/reservoir=False outside niches and drew 0 bare-niches worlds; promotion sent 8,682 runs to
niches; matched controls for recombination dropped recombination and explicit_fitness by grammar constraint (1,829
treatments, 0 controls keeping recombination). Holding physics fixed: .1308 vs .1192. -> Correction: no causal topology
or recombination claim licensed; seeded moat ledger closed (828 qualified / 104 void). -> Status: CONFOUNDED BY
CONSTRUCTION (sampler + matched-control generator), recorded by the seat.

T4. "Transferred/imported material helps" (CMP1 -> CMP3).
Claim (CMP1, 09-16): mature whole material seeds footholds (components 2/3 vs 0/3; failed residue 2/3 vs 0/3). ->
Challenge (CMP2): at n >= 10 both die (+.009, +.002). CMP3 C3-SFE-10 (228 runs): opcode-permuted incompetent controls take
over the population 11-12/12 almost as fast as mature solvers; dose sets speed not outcome; genome diversity stays .78-.99
so a diversity readout sees nothing. -> Correction: "transfer helped" readings in this program are undermined as a class
(WSE packet s8). Later ENVGATE R2 and Z80 transplants (persistence without competence) fit the same pattern. -> Status:
injection/import experiments without a cap and origin-share readout are a known confound class.

T5. Basin-share geometry and the CA delayed-recall margin.
Claim (CMP2): basin share correlates with search efficiency (rho -.59); CA substrate particle2 localized delayed-recall
margin (+.079). -> Challenge (CMP3): pooled out-of-family replication rho -.568 is a two-point correlation across two
strata differing 13x in basin share (within stratum -.527/+.187/-.042/undefined); causal rewrite of reachable-opcode
neighbourhoods: effect -.083 against a declared +.25; hand-designed non-evolved CA rule shows the same localization;
lattice permutation preserves it in 5/8 seeds. -> Status: both withdrawn (as knob / as evolved computation); basin share
survives only as a descriptive statistic. A near-perfect "replication" that was a stratification artefact is a reusable
warning.

T6. "Selection does not climb these worlds" (C5 flat elite) vs the frontier N family.
Claim (C5-02, operator-accepted D5-009): OLD_SUBSTRATE_EXHAUSTED; 0/24 cells improved at equal total compute. ->
Challenge (DF-012, 09-19; digest 09-21): C5-flat.T1 at N=200 on W3_K3 reached max .500 > best starting parent .382 in
three seeds; N family at 60,000 evaluations (N 50/100/200/400 x 3 seeds) all show max .479-.562; Atlas A3 calls this a
buried signal and says the C5 negative was never revisited. -> Counter-challenge (this crawl, [CODE-INFERRED]): the
frontier "max" is reward_max over generations of the per-ask TRAINING reward on the generation's battery
(frontier/digest.py lines 68-74; campaign6/segment.py line 320), while C5's .382 is the best HELD-OUT reward of the
starting parents (C5 world screen). CMP3 already showed a training .9375 reading .53 held-out on a 16-episode battery.
The comparison mixes estimators; seed-2 runs also start at .396 (> .382), as Atlas itself notes. -> Status: UNRESOLVED.
Neither the C5 negative nor the frontier "climb" is established; a held-out readout of the frontier elites at matched
compute would settle it. Possible false negative in C5 (compute 9,000-36,000 evaluations) remains open.

T7. Damage geometry: "length/selection builds robustness" (C4-02/C4-08/C5-08) and Nestor's ruler reread.
Claim (C4-08): selection builds neutrality and length (single-edit loss .419 -> .185 -> .125 with length 19 -> 40 -> 62);
C5-08: LENGTH carries robustness (neutral share by length bin .171/.456/.572/.714), dead code does not. Nestor's CW01
T-ARCH4 tranche (09-18) added a "locality law" (scattered deletion loses more than contiguous deletion at equal count).
-> Challenge (Nestor CW01 cycle 5, 09-19, BOUNDARY_REPORT_CYCLE5 s3, defect D084): every COUNT-FIXING ruler (fixed k
edits, contiguous windows, round(f n)) manufactures "length protects" and "tops are robust" because a fixed count is a
larger fraction of a short program; under a qualified scattered Bernoulli(f) ruler, four of seven fixed-count claims
DISAPPEAR, one survives (operand hits softer than deletions), two shrink (selection effect -.144 -> -.071, 6/6 -> 0/6
seeds). -> Correction applies by inference to Archaeon's own C4-08 and C5-08 readings, which use single-edit (k = 1)
rulers on programs whose length tripled [CODE-INFERRED; no Archaeon artifact re-reads C4-08 under the scattered ruler].
-> Status: C4-08/C5-08 "length carries robustness" should be treated as ruler-geometry-dependent until re-read. The
memory feedback file (count_fixing_damage_rulers_manufacture_coordinates) records the same lesson.

T8. ENVGATE-01 rescue and the 128 gate.
Claim (frozen analysis): GATING_CAUSALLY_SUPPORTED incl. C4 RESCUE_128 > BAND (63 vs 31, p 6.3e-4). -> Challenge (same
day forensics): 69 of RESCUE's 70 establishments were host-labelled lineages in ONE takeover world (block 15) started by a
copier gated at 255; block-level p = .5; copier-founded RESCUE vs BAND 1 vs 1. -> Correction: operator R1 adjudicates
GATING_PARTIALLY_SUPPORTED; frozen files untouched. -> Follow-up ENVGATE-02 under genetic identity: blocking replicates;
the window-rescue model fails; label-based endpoints would have manufactured a rescue gradient (parent-chain 8-42x). ->
Status: environmental band blocking is the surviving law; the mechanism (which inputs carry establishment when the
window is closed) is open -- five BAND0 establishments ~7x above prediction and slow blocks 11/13/14 retained as fossils.

T9. P-boom (boom-bust spike on a coupled composed world).
Claim (DF-013 design): an evaluation-order vs population effect might explain the boom-bust maximum. -> Evidence: readout 1
spike rates 0.17-5.67 within arm. -> Challenge: A_s1 and F_s1, identical by design, differed from generation 1: run_id was
a hidden seed (DF-015). -> Correction: stream_key; v1 arms re-labelled as independent-stream data; readout 2 on shared
streams. -> Later reading (commit 939e4f39e, co-authored by a Claude Sonnet 4.6 session): "FINDING 3: K_F_popcapture (0.33)
inverts vs F_popcapture (5.17) ... strongest arm-level interaction signal". -> Counter-challenge (this crawl,
[CODE-INFERRED]): DF-015 verified that population capture is a pure observer on a shared key ("capture on/off on the same
key -> identical observations"), and K_F_popcapture ran on stream key s1 -- its 0.33 equals K_A_baseline s1 exactly (0.33).
The "inversion" compares a shared-stream arm to an independent-stream arm; it is the hidden-seed defect re-entering the
interpretation, not a capture effect. -> Status: PROVISIONAL readout; finding 3 should be treated as an artefact.

T10. Spike rulers and Campaign 6 detectors (ruler saturation).
Claim: eleven detectors catch discoveries; FULL freezes on admitted rulers. -> Evidence: first live hour, structural_reuse
(base rate ~.4 on composed worlds) drove 5,853 FULL freezes in one 16,000-evaluation run (DF-011); classifier_failure
fired on 100% of firing subjects because five rulers are structurally UNABLE (DF-012). By 09-21: structural_reuse
1,658,614 and detector_disagreement 1,753,735 firings over 3,719,136 evaluations; four rulers UNABLE on 1,775,074
evaluations each. Population-stage positive controls: novelty catches 25% of planted solvers, discontinuity 0% of planted
jumps. -> Correction: CALIBRATION_EPOCH-001 (structural UNABLEs excluded from the >= 3 rule); FULL only on "admitted"
rulers. -> Status: the "admitted" set is a constant in scheduler.py, not a recorded Harmonia admission [UNKNOWN whether
any admission occurred]; the observatory's discovery-detection power was never established. False-negative regime: real
novelty in C6 worlds would be indistinguishable from saturation noise.

T11. E-003 attribution validation.
Claim (draft synthesis): BEE leg VALIDATES attribution v0. -> Challenge: Harmonia audit item H (09-30): the frozen v4 P2
route ("native material label disagrees with copy-descent majority in >= 10% -> ALTERED") HOLDS in production (.504, lower
bound .456); Archaeon's dry run (8262c32f2) saw ALTERED; amendment C4.2 removing P2 as a verdict route came 17 minutes
later (567762a15); E003_BEE_RESULT omitted C4.2 from its post-exposure list. -> Correction: owner erratum d06059735 (BEE now
leads with ALTERED under pre-exposure rules); Archaeon concurs (#1048); verdict of record open for the operator. ->
Status: CONTAMINATED as a confirmatory test; the amendment-independent Q8c number stands; per-class Q8c "none" .242
[.162, .330] hidden by pooling (Atlas B6).

T12. Producer seasons: an apparent repair that was float luck.
S7 GATE_FAILS_TO_ISOLATE (one regression) -> ARCH-46A exact-rational v2w: the regression and 3 of 49 L9 "improvements" were
float tie splits; verdict LICENSED_ENDGAME_REPAIR. A small case where an instrument (floating point) manufactured both a
false negative and false positives inside one result; the seat attributed every changed decision.

T13. False-negative regimes the record itself names: three CMP1 assays could not pose their question (unreachable cells);
C4-03/C4-07 REPRESENTATION_BLOCKED (no fault event in a total interpreter); C4-09/C4-10 worlds pre-solved; S3 endpoint
saturation; H3 dead-stream ceiling (12/12 with a 1.8-task range); H5 numbers at analytic bounds; NPE leg of E-003 below its
own floor by construction; cost regimes E1-E3 extinguish organisms before capability exists (economics applied from
generation 0 on a flat landscape); SSF evolution never found a foothold although hand-written organisms showed the
economics favoured selective state -- a search-reachability limit, not evidence that the economics fail.

## 10. Research outputs (substantial documents)

- roles/Archaeon/REVIEW_PACKET_2026-09-10.md -- ecosystem state and 14 scoped findings (analytic bitstring null, D3 phase
  boundary, inert H2 configuration, NK variance formula, ECA 224 classes, literature checks on reservoir CA / QD).
- roles/Archaeon/REVIEW_PACKET_WSE_V01_2026-09-16.md, REVIEW_PACKET_SSF_C1-3_2026-09-16.md, REVIEW_PACKET_CMP1/2/3_
  2026-09-17.md, REVIEW_PACKET_WSE_ARCHITECTURE_2026-09-17.md (the strongest single synthesis of Family B, with
  "questions written to resist agreement").
- roles/Archaeon/REVIEW_PACKET_C4_REH1_2026-09-18.md, REVIEW_PACKET_CAMPAIGN4_2026-09-18.md, REVIEW_PACKET_CAMPAIGN5_
  2026-09-18.md.
- archaeon/z80atlas/pivot/Z80ATLAS_REVIEW_2026-09-22.md, Z80ATLAS_POSTCAMPAIGN_REVIEW_2026-09-23.md,
  Z80ATLAS_RULINGS_FOLLOWUP_REVIEW_2026-09-24.md; postcampaign/Z80ATLAS_POSTCAMPAIGN_ADJUDICATION_2026-09-23.md.
- archaeon/envgate/ENVGATE01_REVIEW_2026-09-24.md + ADJUDICATION_ADDENDUM; archaeon/envgate2/VERDICT_2026-09-26.md;
  ENVGATE_CLOSURE_2026-09-26.md.
- roles/Archaeon/ENGINE_LANDSCAPE_2026-09-25.md -- cross-engine table (SFE, NPE, BEE, AGE, CWE, WTP, PTE, Aphrodite,
  Archaeon) with a distinctness verdict ("not distinct as a world; distinct as a method") and the varied=/observed=
  proposal.
- archaeon/causal_lens/PORTABILITY01_REPORT.md, V02_REGRESSION_REPORT.md, FALSE_FRIENDS.md (34 named false friends across
  engines), HOST_CONDITIONED_ASSAY_READINESS.md, OBSERVATORY_DESIGN.md; pivot/PORTABILITY01_REVIEW_2026-09-26.md,
  CONTRACT_V02_REVIEW_2026-09-27.md.
- ops/campaigns/C-001/CAMPAIGN.md (portable-Task record), DEEP_BLOCK_2026-09-27/ (A-G incl. G_PRIOR_ART.md: IBD/IBS, ARG,
  Hall, von Neumann, Godfrey-Smith, Tierra, Spiegelman, Griesemer, hereditary stratigraphy -- a bounded external prior-art
  comparison that labels most internal distinctions REDISCOVERY), ATTRIBUTION_V0_2026-09-28/ATTRIBUTION_PACKET.md.
- E003_SYNTHESIS.md (branch).
- archaeon/docs/ARCHAEON_V0.md, CALIBRATION.md, STAGE0_RESULT.md, ROADMAP.md (diversity/expansion roadmap, 550 lines),
  docs/expansion/ (CROSSWALK, 69-entry matrix, WORK_PACKAGES, DECISIONS), D3_NULL_RECONCILIATION.md.
- archaeon/frontier/DEEP_FRONTIER_CHARTER.md, campaign6/PLAN.md, CONVERGENCE_v0.1.md, DETECTORS_v0.1.md,
  observatory/ADMISSION_PACKET_v0.1.md.
- roles/Archaeon/CALIBRATION_LEDGER.md (own wrong calls), CAMPAIGN_REVIEW_2026-09-06.md, REVIEW_SEATS_2026-09-10.md.

## 11. Journals, TODOs, pivots, abandoned branches

Major pivots and why:
1. Producer -> coordinator (09-08): operator H0-H5 brief needed one implementation lead; Archaeon routed every seat and
   kept a status file. Cost: Archaeon's own signal campaign stayed starved of a usable corpus (B1 credential blocker; no
   read grant until 09-12).
2. Coordinator -> constitution author (09-11): adoption passes of the base role; D-23 workspace invariant after worktree
   incidents; comms revived.
3. Producer science -> producer-policy science on synthetic worlds (09-12/13): the live corpus could not support
   fossil-directed selection, so the operator's seasons moved the question to exact synthetic worlds.
4. Read side -> lead experimentalist (09-16): workspace-ecology directive put evolutionary populations on Archaeon
   directly; campaigns ran on Archaeon's own harness path, not through Vivarium (C4 I-6: no queue kind evaluates a program
   variant).
5. Proteus-VM evolution -> Z80 reproduction (09-19): Archaeon adopted Nestor's 72-hour directive, then spent 09-23..09-26
   repairing its own campaign's provenance defect and building ENVGATE.
6. World -> lens (09-25/26): operator asked "is what you built worthy of its own distinct engine?"; Archaeon's answer:
   not as a world (third Z80 build), yes as a method; PORTABILITY-01 and the causal lens followed; ENVGATE line closed
   (no ENVGATE-03, RIE-01 never launched).
7. Lens -> fleet member (09-28..10-01): MWO/CWO orders; dispatches became infrastructure fixes (comms keepalive) and
   fixture probes (FP-001 PASS on Fabric).

Abandoned / staged / unmerged:
- RIE-01 (archaeon/rie/): staged, unfrozen, unlaunched; precondition (ENVGATE-02 Phase-C gate) failed.
- ENVGATE-01 historical genetic audit (archaeon/lineage/audit_envgate01.py): not run.
- Host-conditioned assay: READY_WITH_ENGINE_SPECIFIC_LIMITS, not preregistered, not launched.
- Campaign 6 Phases 1-3; G6-0 never verified.
- C3-3 rows held (09-16); M-ELIGIBLE / M-SIGNAL never issued; NK (A2 templates) never run by Archaeon.
- origin/archaeon/attribution-arc-2026-09-28 (85 commits ahead of main, E-003), origin/archaeon/mwo0001-2026-09-28 (33
  ahead), origin/archaeon/comms-keepalive-2026-09-30 (1 ahead; CODE_FIXED not deployed). All other archaeon/* remotes are
  merged.
- Deep Frontier queues: 202 EXPLORATION / 12 EXPLOITATION / 40 AUDIT pending at 09-21; last registry event 2026-09-22
  (BLOCKED_BY_SUPPRESSION on C4-cliff.T1 under PROTEUS-46). Whether the DeepFrontier scheduled task still exists on M2 is
  [UNKNOWN].
- ArchaeonTick (M1): UNKNOWN since 2026-09-15 per MONITORS.
- Open blockers recorded: BLOCKED_ON_OPERATOR_INPUT_2026-09-27.md (Azure compute placement); OFF_MACHINE_COPY_BLOCKED
  (no SSH/SMB path M2 -> M1 for evidence copies); E-003 verdict of record.
Self-recorded process incidents: canonical-checkout git pull at boot (CALIBRATION_LEDGER 09-16); starting Vivarium twice
(09-06); timestamps labelled Z in local time and estimated ahead of the clock (C5 packet s6 item 4); a second Deep Frontier
scheduler briefly ran concurrently (DF-015); ENVGATE-02 first launch reaped for memory (OPERATIONAL_INCIDENT_2026-09-24).

## 12. Lens inventory (what each engine could become; no ranking, no recommendation)

L1. Fossil-detector producer (E1).
Substrate: an experiment ledger (SFE/PEW rows). Organisms/worlds: none of its own. Pressure: none. Phenomenon family:
weak structure in accumulated experimental records (repeated small deviations, variance anomalies, order reversals,
boundaries). Resolving mechanism: six calibrated arithmetic detectors with eligibility census and Bonferroni. Ceiling: set
by corpus structure, not detectors -- on the real corpus 3/6 detectors were ineligible and the rest acted on a population
disjoint from the steerable one. Noise: hash-like coordinates, repeat inflation, tenancy mixing, unknown upstream
selection. Limitation: cannot propose unobserved combinations; regex authority guard. Reusable: eligibility-beside-firing
discipline, database-enforced cadence, provenance-outside-hash, per-unit aggregation. Toy-grade: the bitstring corpus it
read. Unknown: whether any Prometheus ledger now has the arm/group structure Stage 0 asked for.

L2. Exact producer-policy bench (E3).
Substrate: hidden-target identification with exact feedback. Phenomenon: value of information, myopia of one-step
objectives, exact-tie handling. Mechanism: exhaustive census against an exact DP optimum. Ceiling: L <= 10 exact; L 32
intractable at that code. Reusable: work budgets, permutation-invariance tests, exact-arithmetic tie handling, frozen
endgame gates. Toy-grade: the world (Mastermind-like). Unknown: transfer of any policy to non-synthetic experiment
selection.

L3. WSE event-stream ecology on the Proteus VM (E4/E5).
Substrate: GA populations of total-interpreter register/tape programs. Worlds: event streams with keyed recall,
delays, distractors. Pressures: reward, cost vector, curricula, imports. Phenomenon: emergence of working-memory-like
state under ecological pressure. Mechanism: reachability table, held-out summits, corridor table, typed dispositions.
Ceiling: two-value keyed memory never reached (0/60); one reproducible positive (delay-invariant reader) of unknown
nature. Noise: 16-episode training luck, CRN double counting, foundry pooling, import takeover. Limitation: organism lacks
addressing/call primitives; one mutation per child; small values (4-bit). Reusable: the instrument stack (reachability +
held-out confirmation + disposition ladder + attempts/receipts) is the most mature evaluation machinery in the seat.
Toy-grade: the cells (W0..W3, K <= 8, 4-bit values). Unknown: whether the ceiling is organism, operator or world.

L4. Damage-geometry / evolvability probe (E6).
Substrate: Proteus programs (OLD total interpreter; Representation B with FAIL/FIZZLE). Phenomenon: mutational
robustness, neutral networks, exaptation, local failure boundaries. Mechanism: edit censuses with CRN over five
environments, walks, radius curves, recovery vs insulation-loss counts. Ceiling: rulers were count-fixing (single edit,
radius k), now known to manufacture length effects (T7). Reusable: replication of earlier censuses digest-for-digest
(5,586/5,586), pre-solution screens, equal-total-compute controls. Toy-grade: 57 starting parents, 16-episode answer
vectors. Unknown: results under a dilution-neutral (scattered Bernoulli) ruler.

L5. Composed-world observatory and lineage scheduler (E7/E8).
Substrate: Proteus v0 and graph organisms on procedurally composed worlds with coupling and schedules. Phenomenon: open-
ended novelty, endogenous pressure, boom-bust dynamics, niche construction. Mechanism: eleven FIRE/QUIET/UNABLE rulers,
T0 fingerprints, tiered freezes, replay A, seed controls, frontier allocation. Ceiling: rulers saturated (firings per
evaluation ~0.45-0.47 for structural_reuse/disagreement) and weak positive controls (25% / 0%); several rulers structurally
UNABLE. Noise: hidden seed (fixed), stream-level variance (P-boom 0.17-5.67 within arm). Reusable: segment/checkpoint
contract, procedural world generator with complete provenance, registry separation of OBSERVATION and INTERPRETATION,
authority=NONE on unadmitted rulers, multiplier provenance. Toy-grade: 24-tick episodes, small graphs. Unknown: any
validated detection power.

L6. Z80 reproduction ecology (E9) -- the third Z80 build.
Substrate: 32/64-byte self-copying programs. Phenomenon: origin and establishment of replicators, competence vs
replication, topology/physics effects. Mechanism: factor grammar + flags (now known to need provenance), census rulers,
DENOVO preregistration. Ceiling: de-novo replication 0/80 at the tested exposure; the measured prior (9.6e-6) predicts
lottery tickets. Noise: label-reading predicates, sampler coupling, seeded witnesses. Reusable: copier census method
(input-skip exactness, ruler classes), provenance v1 founder classes, evidence freeze bundles. Toy-grade: single-byte
tasks; 128 cells. Unknown: agreement with BEE/NPE on the same question (Atlas A1/A2 contradictions remain open).

L7. Environment-as-variable causal assay with byte-level genetic attribution (E10) -- the seat's most distinctive lens.
Substrate: frozen byte-VM ecology with random inflow. Phenomenon: environmental gating of establishment; host-mediated
reproduction; origin vs amplification. Mechanism: paired arms on byte-identical arrival streams, sham blocks, legacy
replay admission, taint VM with four identities per birth, genetic establishment. Ceiling: establishments are rare (U 24
in 24 blocks at ~8 h on 6 workers) so rescue contrasts have 1-2 non-tied blocks; mechanism model failed. Noise: takeover
worlds (38% of establishments), block heterogeneity (blocks 11/13/14). Reusable: taint VM pattern, sham arm discipline,
frozen code-hash launch gates, label-vs-genetic counting. Toy-grade: one physics configuration. Unknown: what carries
establishment when the window is closed.

L8. Cross-engine causal lineage lens / attribution v0 (E11).
Substrate: preserved records/replays of other engines (BEE, NPE, PTE, Archaeon). Phenomenon: who/what/where authored a
birth; descent vs resemblance; production vs dependence; capability transmission. Mechanism: contract + adapters +
validator A1-A17 + fixtures + adversarial review; NATIVE/DERIVABLE/APPROXIMATE/NOT_IDENTIFIABLE matrix. Ceiling: only
Archaeon's engine has native per-byte material; BEE has 33% unresolved births; NPE has 29-34 informative births. Noise:
post-exposure amendments (E-003), unexplained dry-run vs production drift. Reusable: FALSE_FRIENDS ledger (34 entries),
portable-Task record, the WHAT-never-from-WHO/WHERE rule. Toy-grade: depends on the host engines. Unknown: heredity (L3-
L5) never tested; necessity of v0 fields never tested.

## Open questions / unknowns

1. Host naming: is Archaeon's M2 SPECTREX5 or SKULLPORT? (STATUS_2026-10-01 vs census and all earlier packets.)
2. Were the six "ADMITTED" frontier rulers (scheduler.py:178) ever admitted by Harmonia? No admission record found.
3. Does the frontier C5-flat N family climb when read on held-out episodes at matched compute (T6)?
4. Do C4-08 / C5-08 robustness-by-length readings survive a scattered Bernoulli(f) ruler (T7)?
5. What carried the five ENVGATE-02 BAND0 establishments, and why are blocks 11/13/14 both slow and establishment-rich?
6. What is the delay-invariant reader (C3-SFE-03)? Nestor's CW01 later classed the delay_general lineage as a "start-
   anchored" temporal shape (T-X19); whether that makes Archaeon's invariance a capability or a property of the delay knob
   (WSE packet Q2) is unresolved here.
7. Why do E-003 dry-run and production differ on the identical 32,827 births (Q8c .0003 vs .00115; transmission class 30,945
   vs 31,401)?
8. Is the DeepFrontier scheduled task still registered/running on M2; is ArchaeonTick still registered on M1?
9. Off-repo evidence (C:/Prometheus-data/evidence/*) is the only copy of ENVGATE/Z80 rows and BEE traced logs used by the
   lens; OFF_MACHINE_COPY_BLOCKED stands. Durability is unknown.
10. Atlas indexing gap: VERIFIED in this crawl -- atlas/harvest/archaeon_campaigns.py matches only
    r"archaeon/(campaign\d+)/" and atlas/registry.json lists only engine_ids archaeon.campaign and archaeon.frontier
    (plus the archaeon_tick.log root). z80atlas, census, envgate/envgate2, lineage, causal_lens and attribution are not
    indexed by Atlas; Atlas's inference_harvest documents nevertheless cite them (from prose/commits), so Atlas's Archaeon
    picture is assembled from documents, not from harvested runs.
