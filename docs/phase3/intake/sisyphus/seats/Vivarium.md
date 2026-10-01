# Vivarium -- forensic dossier

Seat: Vivarium (experimental execution service / "data plane" in front of SFE)
Crawl date: 2026-10-01
Base SHA of worktree: 19299e06b (origin/main at crawl)
Crawler: Sisyphus worker (Opus 5.5), read-only

Coverage statement.
READ IN FULL: roles/Vivarium/{CHARTER,RESPONSIBILITIES,STATUS,DELIVERABLE_V0_2026-09-05,
MACHINE_REPORT_2026-09-06,INVESTIGATIVE_REPORT_2026-09-11,NOTES_POSTMORTEM_2026-09-08_to_09-11,
H0H5_ITERATION1_RECEIPT_2026-09-09,H0H5_ITERATION1_ADDENDUM_2026-09-10,BACKLOG_H0H5,
INBOX_ARCHAEON_BASE_ROLE_RULINGS_2026-09-11,INBOX_THEOPHRASTUS_WITNESS_BOUND_OFF_BY_ONE_2026-09-14}.md,
campaign6/VIVARIUM_LANE_2026-09-18.md, ledgers/S1_SEASON_RECEIPT_2026-09-12.md,
receipts/INCIDENT_2026-09-24_M2_HOST_EXHAUSTION.md, point_release/VIVARIUM_EVIDENCE_INVENTORY.md.
READ IN PART: TIER0_TIER1_REPORT (sections 0-8, 11), campaign6/DIRECTIVE_verbatim.md (first 150 lines),
INBOX_HERAKLES_DEGENERACY_AND_BACKEND (first defect), point_release/{EXPERIMENT_TRANSACTION_MODEL (s0-2),
STAGE2_SELF_CRITIQUE (Q1-Q4)}, journal/2026-09-17 (passes 1-2), vivarium/README.md.
CODE: vivarium/viv/kinds.py (all kind registrations), spec.py (repeat plan, outcome ops, aggregates,
degeneracy rule), queue.py (claim, release_stranded), loop.py (stage method list), deadman.py
(auto-recovery and stranded-release paths), ca_density.py and cegis_boolean.py (module docstrings and
function inventory), migrations/001 (single-slot index), migration list 001-010, file inventory of
viv/, deploy/, tools/, tests/ (49 test files, ~590 test functions by grep).
HISTORY: full git log of vivarium/ and roles/Vivarium/ (136 commits, 2026-09-05 .. 2026-09-24) with
bodies of ~15 load-bearing commits; origin/vivarium/v0-2026-09-05 (8 unmerged commits, diffed against
main); worktrees F:/Prometheus/.claude/worktrees/vivarium-campaign-e1-e6-e16 (log only),
F:/Prometheus-worktrees/vivarium-base-role, vivarium-consumer (ancestry only); primordial/ authorship
(git log over 2,092 commits) and how it reached main.
CROSS-SEAT: archaeon/docs/h0h5/{C3_2_READOUT,H5_1_READOUT_2026-09-11,H1H0_PHASE2_READOUT,
S1_READOUT_2026-09-12,S2_CENSUS_2026-09-12}.md (heads), roles/Archaeon/H0H5_STATUS.md (grep + key
lines), roles/Artemis/threads/sfe_retrospective/{REPORT.md s2.2, notes/A_chronology.md s3 and s7},
Atlas (atlas/harvest/vivarium.py, atlas/registry.json, reports/*, inference_harvest_2026-09-30 digests;
grep only), Achilles census registry (grep), Odysseus census (one line), Aphrodite STATUS + engine
review (Vivarium lines), ops/work_orders MWO-0001 Vivarium clause, base-role RESPONSIBILITIES and
WORKING_CONTRACT (Vivarium lines), theophrastus/adapter.py header. Comms (read-only SQL helper):
listing of every message matching "Vivarium"; bodies of #454, #455, #483, #532, #573, #1014.
NOT READ and why: BOUNDARY_REVIEW_2026-09-05 (467 lines; superseded in substance by TIER0_TIER1 and
quoted in commit a0f70c72d), the point_release design docs beyond the two named (schema detail, not
history), journals 09-11/12/14/16 in full (commit bodies cover them), the INBOX_ARCHAEON_* files
other than the rulings (their content is mirrored in Archaeon's H0H5_STATUS), the per-window JSON
receipts (counts quoted from commit messages), runner.py/loop.py bodies beyond the stage list (the
behaviour is described from tests, docstrings and receipts, not traced line by line), the live
databases (viv schema, SFE engine.db, PEW) -- all numbers about rows are HISTORICAL CLAIMS from
Vivarium's or Archaeon's own receipts, not re-derived here. No holdout or secret path was opened.

Bottom line up front. Vivarium is NOT an artificial-life engine, despite the name and despite the
thematic territory it was filed under. It built no world, no organism, no mutation operator and no
selection mechanism. It is a carefully engineered, Postgres-backed, single-slot experiment queue and
SFE/PEW execution adapter ("QUEUE -> EXECUTE FAITHFULLY -> RECORD -> REPEAT"), plus thin wrappers
(kinds) around other seats' scientific libraries: Herakles's radius-3 density-classification CA and
radius-1 ECA, Proteus's 3-input Boolean CEGIS VM, and SFE's hidden-target bitstring scorer. Its
scientific relevance to Phase 3 is as INSTRUMENT INFRASTRUCTURE (provenance, blinding, sealed specs,
replay, attempt/step receipts) and as a rich record of HOW EXECUTION FAILURES MASQUERADE AS SCIENCE.
It has been dormant since 2026-09-18 00:20Z (last productive row) and silent since 2026-09-24.

-------------------------------------------------------------------------------------------------
## 1. Identity and purpose

Canonical name: Vivarium. No aliases found. Instance tags seen: m1-416d588d (M1/SKULLPORT pass,
09-11/12), m2-fce3fe0b (first M2/SPECTREX5 boot, 09-16 onward). Worker ids: vivarium@m1,
vivarium@m2, vivarium@e2e-viv (demo), vivarium@debit-receipt (one-shot). [HIST]

Original charter (roles/Vivarium/CHARTER.md, seat opened 2026-09-05 in commit 8b940a165): "The
trustworthy mechanical hand at the research bench ... Vivarium is not a scientist." Pipeline
"Archaeon -> PostgreSQL experiment queue -> VIVARIUM -> SFE / worlds / players -> PEW -> Archaeon".
Seven standing invariants: no double execution by race; a malformed experiment never mutates into a
different one; sealed spec hash checked against the SFE ledger before work runs; terminal rows never
reclaimed; failures preserved, no silent retry; a stranded run is left visibly stranded and "an
operator releases it explicitly"; queue holds pointers, never copies of the scientific record. Non-
goals: no scheduling intelligence, no interpretation, no LLM, one experiment globally at a time
enforced by the database. [INTENT]

Why it was created: founding commit subject "the execution loop had no queue, so 'what ran' was
unreconstructable" (8b940a165). Artemis's retrospective notes SFE already had a world-scoped
claim/lease work queue and that "nothing in the evidence explains why SFE's own queue was not used
as the program queue" (Artemis notes/A_chronology.md s3, INFERRED there). My reading of the founding
deliverable: the gap was a cross-world, cross-tenant REGISTER of requested experiments with
provenance outside the hash, which SFE's per-world work items do not provide. [CODE-INFERRED]

Charter changes and pivots:
- 09-06: boundary with Archaeon written (Archaeon must not start/stop Vivarium) after two daemons
  consumed production concurrently (MACHINE_REPORT s10; Archaeon commit 1097458e6). [HIST]
- 09-06: Archaeon independently adopted the same queue contract (c9304ff02); archaeon.experiment_queue
  RETIRED, Vivarium's migration authoritative (TIER0_TIER1 s0-1). [HIST]
- 09-08 .. 09-10: H0-H5 program: the seat became the "integrating owner" of the artifact loader
  (H0H5 iteration 1) and wrapped other seats' libraries as kinds (ca_density_v0, eca_rule_eval_v1,
  cegis_boolean_v1). The "no scientist" line was preserved by putting adaptive search INSIDE a sealed
  kind (cegis_boolean_v1 docstring, "design C3"). [INTENT/IMPL]
- 09-11: inherited the base role (aee89ff8b); its adoption pass found four constitutional defects
  that the operator ruled on (journal gitignored; .claude/worktrees allowed; stranded rows are an
  epistemic question; cheat control required) -- INBOX_ARCHAEON_BASE_ROLE_RULINGS_2026-09-11.md.
  Vivarium's stranded-row rule became the base-role model for all seats (base-role
  RESPONSIBILITIES.md ~line 554). [HIST]
- 09-16: operator topology ruling: the SFE ecosystem (engine, PEW, consumer, Archaeon tick) runs on
  M2 only; Postgres/Redis shared on M1 (STATUS.md). Seat relocated to M2. [HIST]
- 09-17: "point release" after Campaign 3: absorb Archaeon's campaign-runner durability mechanics
  (attempts, keyed steps, replay, outbox) into the queue (point_release/*). Pivot from "a row is
  claim-once" to "a row has attempts; a stranded or transport-failed row may be released to a NEW
  ATTEMPT", then (1023f81bd) to a dead-man that performs that release AUTOMATICALLY, bounded at 3 per
  rolling 24 h. This is a material weakening of charter invariant 6 (see s9, T4). [HIST/IMPL]
- 09-18: Campaign 6 lane analysis; "Nothing built or deployed" (8291e211f). [HIST]
- Terminal state: consumer parked 2026-09-19T00:29:52Z on its own 24 h idle bound with an empty queue
  (comms #483); dead-man parked 09-23 (store unreadable) and 09-25 (SFE 8811 unreachable, #573).
  Last seat commit 8c5a1a23b (09-24, incident). No WORK_STATE.json, no MWO-0001 adoption (MWO-0001
  addressed Vivarium "if live"; ops/work_orders/archive/MWO-0001_2026-09-28.md). Artemis classes the
  queue DORMANT (REPORT.md s2.2). Aphrodite's Campaign-1 execution-contract requests (#454, #491,
  #532: qualification envelope E1-E4 assigned to Vivarium) were acknowledged in passing (#455) but
  never answered with a contract; Aphrodite STATUS lists C1 as blocked partly on them. [HIST]

Relationships: Archaeon = producer (what to run, outcome rules); Daedalus = SFE engine owner (Vivarium
consumes /v2 only); Mnemosyne = PEW (fossil record); Proteus = player/Boolean semantics; Herakles =
CA/ECA library semantics; Harmonia = adversary/qualification; Theophrastus used Vivarium's SfeRunner
as a library (theophrastus/adapter.py) bypassing the queue; Atlas harvests the queue (atlas/harvest/
vivarium.py, "vivarium/2"). [IMPL/HIST]

Hosts: M1 SKULLPORT 09-05..09-14 (consumer from .claude/worktrees then pinned worktree
F:/Prometheus-worktrees/vivarium-consumer); M2 SPECTREX5 (192.168.1.191) from 09-16, pinned worktree
D:/Prometheus-worktrees/vivarium-consumer, data D:/Prometheus-data/vivarium (atlas/registry.json).
The canonical store (schema viv in prometheus_fire) stayed on M1. [HIST]

Ownership of the named surfaces (task item):
- vivarium/ -- Vivarium only (code authored under the Vivarium seat; the kinds' scientific semantics
  are imported from herakles/evca, herakles/eca, proteus/eval, SFE executors). [IMPL]
- roles/Vivarium/ -- Vivarium only (plus inbound INBOX_* notes written by Archaeon, Herakles,
  Theophrastus). [IMPL]
- primordial/ (789 tracked files) -- NESTOR ONLY. Every one of its 2,092 commits is a Nestor lane
  (Nestor-A..H/P/Q/T/U/W, tags m1-*), first commit a901ba0c9 (2026-09-14, "Primordial Machine swarm
  kit v0"), README "primordial -- the Primordial Machine swarm (Nestor side quest)", plan at
  roles/Nestor/sidequests/graphworld/SWARM.md. It reached main on 2026-09-22 via first-parent merge
  b10161316 "Merge nestor/sidequest-graphworld-2026-09-14 into main". The only Vivarium mentions
  inside primordial/ are host-load notes ("M1 shared with lanes B/C + SFE/Vivarium"). Archaeon
  authored nothing in it. [IMPL]
- origin/vivarium/v0-2026-09-05 -- a MISNOMER today. It was the seat's v0 branch (8b940a165) but the
  canonical checkout F:/Prometheus was parked on it after the branch was retired, and the 8 commits
  it carries beyond main (a62c9085e .. afd3548db, 09-08..09-10) are Aporia, Herakles and Mnemosyne
  work (H0-H5 evidence deck, H1 directory, program proposal, ca_stream/eca alphas, PEW typed refs),
  not Vivarium's. All 63 files it touches exist on main: 50 byte-identical, 13 further evolved on
  main; git cherry marks 6 of 8 commits patch-equivalent. Nothing unique remains on it. The local
  canonical checkout additionally carries unpushed commit 68aab291f (Hephaestus) and uncommitted
  edits that are not Vivarium's (not touched). [IMPL]
- Worktree .claude/worktrees/vivarium-campaign-e1-e6-e16 (HEAD 363120e08, merged into main): the
  09-06..09-11 authoring worktree; "e1-e6-e16" names Archaeon's expansion-roadmap items E1
  (policy_version + template_id into the PEW producer block), E6 (candidate sets bound to SFE
  selection families with alternatives) and E16 (outcome-rule aggregation over repeats), per
  vivarium/tests/test_campaign_e1_e6_e16.py -- NOT "campaigns e1 to e16". [IMPL]

-------------------------------------------------------------------------------------------------
## 2. Engine / system inventory

2.1 The Vivarium data plane (vivarium/viv, ~35 modules; vivarium/migrations 001-010; 49 test files).
[IMPL unless noted]
- Purpose: register requested experiments with provenance outside the sealed hash; execute exactly
  one at a time against SFE; write the PEW fossil; never adjudicate.
- Entrypoints: `python -m viv.cli run|tick|status|trace|show|kinds|family|candidates|health|errata|
  stranded|release|stop|unpark|hold|grant-reader|production|sfe-identity|limits` (cli.py, 959
  lines); viv/daemon.py (thin loop around tick); viv/deadman.py (scheduler-fired one-shot watchdog);
  viv/deliver.py (PEW outbox deliverer one-shot); deploy/{window,canary,prepare_m2,
  g3_identity_proof,rehearse_window}.py.
- Important modules: spec.py (canonical spec hash byte-identical to sfe/ids.py content_hash; strict
  closed-key validation; repeat plan; outcome rule with ops ==,!=,<,<=,>,>= and v3 aggregates
  first/any/all/max/min), queue.py (claim with FOR UPDATE SKIP LOCKED, transitions, release),
  loop.py (stages recover/claim/validate/build_request/dispatch/collect/fossilize/finalize + tick),
  runner.py (1,347 lines; SFE adapter: session -> world -> start -> hypothesis -> prediction ->
  experiment -> ledger seal read-back -> work claim -> executor -> complete -> observation ->
  anchor), kinds.py (kind registry), executors.py, preflight.py + artifacts.py (immutable artifact
  loader, digest-keyed address book), resources.py (resource vector with enforcement classes),
  selection.py (candidate set -> SFE selection family), attempts.py/stepkey.py/bundle.py (point
  release transaction model), outbox.py/deliver.py (PEW outbox), conformance.py (fail-closed
  engine-contract gate before claim), db.py (credential precedence + cluster identity guard),
  library_leak.py (component-library contamination checker), stalls.py, scope.py (B1 read grants).
- State: Postgres schema viv on M1: research_experiment_queue (status machine queued/claimed/running/
  completed/failed/cancelled, generated active_singleton + unique index = one active row globally),
  research_experiment_events (append-only by trigger), worker_heartbeat, register_errata(+_rows) and
  view register_clean, candidate_sets view, artifact_locators (004), candidate-set append refusal
  trigger VIV01 (005), execution_attempt / steps (006/007), bundles / gate and intervention receipts
  (008), pew_outbox (009), release of ENGINE_TRANSPORT-failed rows (010). Host-local state in var/
  (stop flag, park records, session keys, read-scope bindings, logs).
- Execution model: single global slot, FIFO by (priority, created_at), fixed 5 s idle interval, no
  batching, no retry (until 010); one queue row = one SFE world (name derived viv-<spec_hash[7:23]>)
  = one SFE experiment = one work item carrying N repeats (spec v3 `repeat`).
- Scale (HIST, Vivarium/Archaeon receipts): ~1,155 queue rows by the 09-17 window (completed 579,
  cancelled 492 of which 246 are declared test contamination, failed 79 -- Artemis/Archaeon
  7c89a7199), Atlas indexes 1,242 rows / 1,254 attempts by 09-19 (REPORT_2026-09-19.txt). Lifetime
  observations to 09-11: 987 (FALSIFIED 592 / SURVIVED 395). The SFE ledger carried ~85,727
  never-observed "phantom" experiments created by Vivarium's selection binding (s9, T2).
- Throughput: "The science is 0.1s. The row is 95-193s. 98%+ is SFE round-trips" (09-10,
  NOTES_POSTMORTEM s4); S1's 24 rows ran in 9.5 s on 09-12 after engine repairs. [HIST]

2.2 Kind wrappers (the only "scientific" code paths; registry vivarium/viv/kinds.py). [IMPL]
- noop_v0 (vivarium): no params; plumbing only.
- evaluate_bitstring (vivarium; delegates to SFE's reference executor): params bits, length;
  score = fraction of positions matching a hidden target derived from sha256("target:<seed_root>:
  <length>"); solved = score >= 1.0. This is a seeded onemax/Hamming landscape (Herakles called it
  "single-peaked, additive, noiseless, undeceptive", INBOX_HERAKLES_BITSTRING_EXECUTOR via Artemis
  F12).
- archaeon.probe.v0 (archaeon; RETIRED 2026-09-06, never implemented): kept readable because
  the sfe.candidate_score.v0 corpus it targeted was scored by an unknown harness (candidate 6926509:
  0.42289 there vs 0.33333 under the 24-bit reference; 0.42289 is not a multiple of 1/24).
- random_walk_v0 (vivarium; stateful): deterministic 1-D walk, a bench primitive for repeat.state
  semantics; "not a scientific claim".
- ca_density_v0 (herakles semantics / vivarium wrapper; vivarium/viv/ca_density.py, 463 lines):
  radius-3 binary CA, rule as 32 hex digits (128-entry table), periodic ring of n_cells, `steps`
  updates, ensembles of ICs (unbiased / Bernoulli(p) / exact-count k), optional `transform`
  (reflect / complement / reflect_complement) applied to rule AND ICs, success masks at_T and stable
  (plus a third, cellwise_majority_match, added 09-10), witness indices of misclassified ICs.
- eca_rule_eval_v1 (herakles/vivarium): radius-1 elementary CA over ALL 2^n_cells initial
  configurations for exactly `steps` updates; returns a behaviour digest and the equivalence class
  of rules with identical terminal behaviour ("reports the observable, not a score").
- artifact_probe_v1 (vivarium): "AN INSTRUMENT, NOT AN EXPERIMENT": a checksum-like fold over an
  artifact's ordered rows, existing only to prove the artifact loader end to end.
- cegis_boolean_v1 (vivarium contract / proteus semantics; viv/cegis_boolean.py, 508 lines): a
  bounded counterexample-guided enumerative synthesis loop over 3-input Boolean expressions using
  Proteus's grammar/compiler/VM and an independent truth-table oracle; 16 sealed parameters (target
  table, grammar version, candidate policy + seed, max_expr_size, max_candidates, oracle/VM caps,
  trace bound, case ordering, termination, seed_probe_count, shortfall rule, two optional artifact
  slots source_pack and component_library).
- Unbuilt, named in BACKLOG_H0H5 s A: ca_stream_v2 (D-18), nk_landscape_v0, a scored ECA kind,
  encoding_search_v1 (H5 beta), curriculum_discrete_v1 (H4), a temporal program interface,
  boolean_cegis_v2 (4-6 inputs), an external-process contract (Z3/DreamCoder), wse_evaluate_v1
  (Campaign 4/5/6), a segment kind for long evolutionary runs (Campaign 6). All BLOCKED or never
  started. [HIST]

2.3 Operational machinery (IMPL): conformance gate (fail-closed before claim, 09-11, 583a2c1f0);
rule-10 self-park (17,280 non-productive ticks = 24 h at 5 s, accountable Archaeon; halt on first
ENGINE_TRANSPORT failure, accountable Daedalus; fa14903d7); heartbeat carries running SHA, var_dir,
instance tag (C6/C7); in-row pulse (C2, 1bed23074); dead-man with BUSY-not-DEAD pid check, rule-9
engine-identity precondition, bounded auto-recovery (f249ae21c, 16d41d287, 1023f81bd); ClaimGrant
(no claimed row, no world; 49ef27f9d); store identity guard pinning schema viv to the canonical
cluster (a6d1ba114); PEW outbox + deliverer (12d690d5f, 5c90a26de); production descriptor
(a67c20ee5).

-------------------------------------------------------------------------------------------------
## 3. Architecture

What constitutes a world: an SFE world created per queue row, named from the spec hash, holding one
experiment and one work item; never terminated by Vivarium (588 RUNNING worlds by 09-11,
INVESTIGATIVE_REPORT s4). The "world" in any scientific sense is whatever the kind computes inside
one executor call: a hidden 16-32-bit target string (evaluate_bitstring), a ring lattice (CA kinds),
or a 3-input truth table (CEGIS). [IMPL/HIST]

What constitutes an organism/player: nothing Vivarium owns. DELIVERABLE_V0 s6 item 1: "No player
execution ... It does not run a Proteus organism"; a proteus_player kind was proposed and never
built. The closest objects are a CA rule table (ca_density_v0, eca_rule_eval_v1), a candidate
bitstring (evaluate_bitstring) and an enumerated Boolean expression (cegis_boolean_v1). [IMPL]

Genotype/program representation: 128-bit CA rule (hex), 8-bit ECA rule number, bitstring, Proteus
Boolean expression trees compiled to Proteus VM bytecode (NOT compiled as XOR x, ONE). Phenotype/
execution: CA lattice trajectory; VM execution on 8 assignments. [IMPL]

Memory model / compute model: stateless kinds except random_walk_v0; state never carries between
queue rows; repeat.state=persist legal only for stateful kinds. Compute is in-process Python
(numpy for CA) inside the consumer, ~0.1 s per row of science. [IMPL/HIST]

Mutation/search operators: none in the data plane. The only search is inside cegis_boolean_v1:
seeded, size-bounded enumeration of candidate expressions with counterexample accumulation, ordered
first-witness rule, caps on VM ops / oracle calls / candidates. Archaeon's autonomous producer
(outside this seat) proposed rows by a declared `random.v0` policy or "weak signal" drafts. [IMPL]

Selection/admission: admission = spec validation (closed keys; exact kind params; value checkers at
admission since 09-16 D2/D2b), conformance gate, cadence quota (Archaeon's 6 autonomous slots/day,
uq_req_cadence_day_ordinal), candidate-set registration (unchosen candidates CANCELLED, never
deleted; appending to a set refused by trigger VIV01). Vivarium itself selects nothing. [IMPL]

Pressure mechanism: none. "Pressure" appears only as a label on kind axes (THEO-REQ-002:
ic_density_set / n_ic / success_criterion = pressure for ca_density_v0; target table = pressure for
cegis_boolean_v1). [IMPL]

Observation/action model, reward/fitness/scoring: the kind's result dict validated against a declared
result_schema; the requester's pre-registered outcome_rule (one comparison over one top-level field,
plus a declared aggregate over repeats) maps it to SURVIVED / FALSIFIED / INCONCLUSIVE. Absent a rule,
INCONCLUSIVE. [IMPL]

Temporal dynamics / spatial topology: within-kind only (CA steps on a periodic ring; ECA exhaustive
over 2^n configurations). Across rows: none. [IMPL]

Reproduction / learning / communication / cross-world transfer: none in Vivarium. The artifact loader
(H0H5 iteration 1) is the only cross-world transport: a sealed spec names artifact bytes by digest;
preflight resolves them through SFE's authorised read, verifies digest/size/codec/interface/closure,
and hands the kind frozen data with no client. This is what made "transfer of a failure pack between
tasks" (H1) expressible. [IMPL]

Lineage tracking and provenance: the strongest part of the design. Provenance columns (created_by,
source_reason, source_evidence, family_id, arm_id, replication_of, candidate_set_id, request_key,
cadence) are frozen by trigger and NEVER enter spec_hash; the runner receives only (experiment_id,
spec_json, spec_hash[, artifact_locators]) and tests assert it cannot see the arm
(tests/test_blinding.py). The sealed hash is read back from the SFE ledger and compared before any
work is claimed. PEW fossils anchor on OBSERVATION_RECORDED (binds exp_id and obs_id) and carry the
queue's producer block. Point release adds attempt/step keys (REUSED/REPLAYED/RECOMPUTED/NEW/FAILED),
start bundles (closed key set, design_digest), intervention receipts (intended vs realised), gate
receipts, a termination envelope, and an ordered outbox to PEW. [IMPL]

Experimental control structure: families and arms declared before execution and frozen; E16
aggregates must be named; `repeat` axes (count, order, seed_derivation, state, budget) all mandatory
and hashed; `degenerate_by_construction` flags constant-seed reset repeats as zero-variance (fixed
after Herakles found the stateful-kind hole; spec.py ~line 443). [IMPL]

Where implementation and design documents disagree:
- Charter invariant 6 ("an operator releases it explicitly") vs deadman.py `_release_stranded`, which
  releases a dead worker's claimed/running rows to a NEW ATTEMPT automatically before relaunch, and
  auto-clears ENGINE_TRANSPORT parks (bounded 3 per rolling 24 h). CHARTER.md was not amended. [IMPL
  vs INTENT]
- README "release always resolves to failed, never back to queued" vs migration 010 (failed ->
  queued legal in the release path when the newest attempt failed on ENGINE_TRANSPORT). README text
  is stale. [IMPL vs INTENT]
- Charter diagram "Vivarium -> SFE / worlds / players": no player execution path was ever built.
- Rule-10 MONITORS row says an idle tick on an empty queue is "the explicit no-op", yet the bound
  counted those ticks and parked the consumer on 09-19 (Vivarium's own finding F2, INCIDENT
  2026-09-24 s3; designed fix not built). [IMPL vs INTENT]
- vivarium/config.json still names M1 addresses after the M2 move (EVIDENCE_INVENTORY L-002 row).

-------------------------------------------------------------------------------------------------
## 4. World capability audit

Vivarium itself provides no world generator. The worlds reachable through its kinds:

- evaluate_bitstring: one hidden binary target of declared length (runs used 16, 24, 32 bits),
  score = Hamming agreement fraction. Nonspatial, fully determined by (seed_root, length), no
  partial observability beyond the hidden target, deterministic, single action (submit a string),
  horizon 1, no delayed consequences, no adversaries, no agents, no resources, no ecology, no
  environmental change, no task diversity beyond (seed, length). A single scored submission leaks
  exact Hamming information about the target (Archaeon S2_CENSUS phase 1). This is the textbook
  "easily memorised narrow benchmark": a 16-32-bit onemax with a hidden optimum. [IMPL]
- ca_density_v0: radius-3 binary CA on a periodic 1-D ring (campaign scale 149 cells, 320 steps;
  library refuses any radius other than 3), density-classification task (does the lattice settle to
  all-ones iff the IC majority is one). Spatial (1-D), deterministic given IC seed, IC ensemble is
  the only stochasticity, one fixed task family. Rule space 2^128 but the campaigns used 6-7 named
  rules (GKL, maj, exp, par, particle1/2) plus 120 random tables. Classic toy benchmark (Mitchell/
  Crutchfield lineage). [IMPL/HIST]
- eca_rule_eval_v1: 256 elementary rules on a 7-cell ring, 8 steps, exhaustive over 128 initial
  configurations -> 224 behavioural classes (H5_1_READOUT). A fully enumerable finite object; the
  "world" is a lookup table. [IMPL/HIST]
- cegis_boolean_v1: 3-input Boolean functions (8 assignments, 256 possible targets); campaign task
  set 12 targets (tgt-00..tgt-11). Fully enumerable; solved requires all 8 cases. [IMPL/HIST]
- Not reachable through Vivarium: Archaeon's WSE (Campaigns 1-5 ran on Archaeon's harness, not the
  queue; EVIDENCE_INVENTORY s0; Campaign 4 report "'Execution: Vivarium' could not be honoured for
  science rows: no admissible kind evaluates a program variant", 8f1a82ced), Proteus's graph
  substrate, Nestor's primordial worlds, Campaign 6 composable worlds (never built).

Scaling limitations: one row = one SFE world = one experiment with ~a dozen REST calls; 98% of row
time was engine round trips; the engine's single-writer SQLite stalled under Vivarium's write bursts.
Vivarium's own Campaign 6 analysis states the per-evaluation row cannot carry "millions of
evaluations" and proposes a SEGMENT kind (VIVARIUM_LANE s2); Daedalus measured a ~400-900 ledger
events/s ceiling (Artemis F16). Neither was built. [HIST]

Verdict, stated as a fact about capability: every world that actually ran through Vivarium is a small,
fixed, fully enumerable or near-enumerable toy (16-32-bit hidden string; 7-cell ECA; 3-input Boolean
tables; a 149-cell density-classification ring). None has open-endedness, multiple agents, resources,
ecology or environmental change.

-------------------------------------------------------------------------------------------------
## 5. Organism capability audit

There is no organism in this seat. The candidate "organisms" are:
- a bitstring (no control flow, no memory, no sensors/actuators, no learning, no reproduction);
- a CA rule table (a fixed local update function; no memory beyond the lattice; no adaptation
  within a run; "reproduction" only in Theophrastus's derived-rule provenance (THEO-REQ-005) which
  Vivarium carries but does not perform);
- an ECA rule number (same, smaller);
- a 3-input Boolean expression enumerated by CEGIS (straight-line expression, no loops, no state,
  no recursion; size bounded by max_expr_size; the "learning" is the CEGIS loop's counterexample
  set within one task, discarded after the row; the only cross-task channel is a sealed
  source_pack of inputs and an optional component_library of sub-expressions).

Did any of these have a realistic fighting chance to exhibit a nontrivial reasoning primitive? On the
architecture: no for the bitstring and the CA/ECA tables (fixed functions evaluated on a fixed task;
nothing composes or adapts). For cegis_boolean_v1 the question H1/H0 asked -- does a transported
failure pack or a reusable component library make search cheaper -- is a legitimate (small) question
about reuse and transfer, but the task family was 3-input Boolean functions where (a) the whole
target space has 256 members, (b) the phase-1 solutions shared no extractable abstractions ("0
abstractions on the three phase-1 solutions by both Stitch and campaign_h1h0.extract_library",
roles/Archaeon/H0H5_STATUS.md line ~102), so the library cells had ZERO eligible input, and (c) the
enumeration order is fixed by the sealed seed so that only cost, not reachability, can differ
(cegis_boolean.py docstring: "remove the cap and this design measures nothing"). The organism could
express reuse in principle; the task family made reuse impossible to observe. [IMPL/HIST]

-------------------------------------------------------------------------------------------------
## 6. Search and pressure mechanism

Novelty production that passed through Vivarium:
- Human/LLM-designed campaign rows issued by hand by Archaeon (C3-1, C3-2, H1/H0 p1/p2, H5-1, S1).
- Archaeon's autonomous tick: declared random.v0 draws and "weak signal" drafts over
  evaluate_bitstring, capped at 6 per UTC day with a minimum separation (tick log 09-11: 58 ticks,
  WROTE_RANDOM 4, NO_WRITE_CADENCE 41, REFUSED_MIN_SEPARATION 35, REFUSED_DAILY_CAP 6;
  INVESTIGATIVE_REPORT s3).
- Inside cegis_boolean_v1: seeded enumeration + counterexample-guided pruning.
No evolution, no QD, no novelty search, no recombination, no curriculum, no environmental or
ecological pressure ever ran through the queue. [HIST]

Bottlenecks and collapse modes (all HIST, from the seat's own records):
- Throughput: minutes per row on a 0.1 s computation; write-lock contention in SFE's SQLite
  (bimodal 0.03-0.32 s vs 23.46 s writes); engine stall episodes 09-11 cost 24 H5-1 rows.
- Producer starvation: the autonomous tick read ZERO fossils on every tick on 09-11 ("sfe db not
  found", 45/45 ticks) because it looked for the ledger in its own worktree -- so "fossil-informed"
  proposals were the random baseline in fact (INVESTIGATIVE_REPORT s5).
- Kind lag: from Campaign 4 on, science moved to Archaeon's in-process harness because no queue kind
  could evaluate a program variant; the queue's last productive row is 2026-09-18 00:20Z (#483).
- Self-park on idle: a consumer with nothing to do parks after 24 h and needs a human (F2).
- Watchdog escalation through the failed medium: the dead-man's notice used comms on the same
  Postgres it could not read, then disabled itself (F1, INCIDENT 2026-09-24).

-------------------------------------------------------------------------------------------------
## 7. Measurement / ruler stack

What counted as success at the Vivarium layer: an EXECUTION fact, never a scientific one. Tick
outcomes {IDLE, BUSY, EXECUTED, FAILED, REJECTED, BLOCKED}; row status; typed failure classes
(EXECUTOR_ERROR, WORK_NOT_CLAIMABLE, EXECUTOR_NOT_IMPLEMENTED, LEASE_LOST, BUDGET_EXCEEDED later
BUDGET_EXHAUSTED-as-COMPLETED-and-censored, ENGINE_TRANSPORT, ENGINE_REJECTED, UNCLAIMED_EXECUTION).
The outcome label is the requester's pre-registered single-field comparison. [IMPL]

Rulers inside kinds (owned by other seats, enforced by Vivarium's wrapper):
- evaluate_bitstring: score in multiples of 1/L; solved iff 1.0. F-1 defect (Herakles; fixed WP-0a
  85d6ff060 09-08): a short bitstring was scored against the full target and silently capped at
  len/length; "all 40 evaluate_bitstring observations on the live M1 ledger have len(bits) ==
  length, so no sealed result can move" (Atlas _part_sfe digest quoting the commit). [HIST]
- ca_density_v0: accuracy under at_T / stable / cellwise_majority_match; both fixed-point facts
  (table entries 0 and 127) reported; witness list with truncation declared both ways (THEO-REQ-004
  fixed an off-by-one that refused a legal 64-witness vector, 6d21bd5ef); mask digests; wrapper vs
  library digest parity refusal. Exact-symmetry null: transformed rule + transformed ICs must give
  IDENTICAL accuracy, counts, witness ICs and mask digests (C3_2_READOUT: 18/18 IDENTICAL). [IMPL/HIST]
- eca_rule_eval_v1: behaviour digest + class membership checked against Herakles's published
  class_map_fixture.json; explicitly "scored_against_a_target: always false". [IMPL]
- cegis_boolean_v1: solved requires full 8/8 coverage; three distinct BUDGET_* statuses vs
  EXHAUSTED_CANDIDATES; costs vm_ops / oracle_calls / candidates_tried; library_leak.py verdicts
  SOLVES_A_TASK / COMPOSES_TO_A_TASK (depth 1) / SUBTERM_OF_SOLUTION before any library effect is
  reported. [IMPL]

Controls the seat built (IMPL; tests): positive / negative / cheat controls on nearly every change
(operator ruling 4, 09-11, defines cheat control as "the measurement channel can observe the thing
claimed"); blinding tests; hash-parity test against sfe.ids.content_hash; degeneracy flag;
exact-symmetry null; spec-hash dedup; canary rows; synthetic qualification fixture (8/8 s16
answers true, QUALIFICATION_SYNTHETIC_2026-09-17.json); 11 production canary runs (window
C4-20260917-W1) that found and fixed 10 production defects.

Statistical tests: none in Vivarium (by charter). Archaeon's readouts applied them (S1 exact one-sided
sign test; Harmonia's H1/H0 block design n = 12).

Known blind spots and failures of the ruler stack (HIST):
- Outcome rules over one field "narrow silently" a multi-metric result (TIER0_TIER1 s11 item 4).
- The original kind contract validated KEYS exactly and VALUES not at all (cost: C3-1, 24 rows).
- Heartbeat fired only between stages, so a healthy long row read as a dead consumer (I-4, near-miss
  release of a live row).
- The ledger cannot distinguish "committed but unobserved because the engine stalled" from
  "committed but unobserved because the executor refused the payload" (I-5).
- ca_density masks: 40 of 40 random tables scored exactly 0.0 under both masks; "a criterion whose
  attainable range for random rules is a single POINT cannot rank anything" (30e97ed94). The third
  criterion was added after C3-2 had already run with success_criterion=stable.
- H5-1 quantities sit at their analytic bounds by construction (direct reach <= 8, permuted <= 12),
  so the readout "carries NO evidence about learned evolvability".

-------------------------------------------------------------------------------------------------
## 8. Experiment inventory (campaigns that ran THROUGH Vivarium)

Important framing: Campaigns 1-5 of the SFE program (Archaeon's WSE campaigns) did NOT execute through
Vivarium (EVIDENCE_INVENTORY s0; Artemis A_chronology s5 table). What did run through the queue is
below. Outcome labels describe the historical record, not a verdict.

V-1 Bring-up and v0 qualification. 2026-09-05/06. Question: does queue -> SFE -> PEW work and stay
reconstructable. Kinds noop_v0, evaluate_bitstring. Measurement: 37 then 82 then 114 tests on real
Postgres; live bring-up row e009b59e (outcome SURVIVED, verify-anchor valid); crash/restart demo
(kill -9 in running -> refuse restart exit 2 -> release -> failed). Reported: works. Later: 7 v0
bring-up worlds turned out to have no register row (RUNNER_MADE_UNREGISTERED; D7; ORPHAN_VERDICTS);
44 throwaway SFE tenants from per-process registration (5be9b847c). Artifacts:
DELIVERABLE_V0_2026-09-05.md, MACHINE_REPORT_2026-09-06.md, TEST_RESULTS_*.txt; commits 8b940a165,
63c39a636, 0b2f92734. Outcome: REPORTED POSITIVE (infrastructure).

V-2 Archaeon Stage 0 and the autonomous tick over evaluate_bitstring. 2026-09-06 .. 09-15. Question
(Archaeon's): can a fossil-reading producer propose better probes than a random baseline. Organism:
bitstring; world: seeded hidden-target onemax (L 16/24/32). Pressure: none (declared random.v0 or
weak-signal drafts, 6 slots/day). Measurement: outcome rule "solved == false" -> SURVIVED. Scale:
hundreds of rows. Reported: rows executed; outcome labels both ways historically. Later: (a) 245
Archaeon pytest rows written into the PRODUCTION register on 09-06 (one claimed by a live cycle);
erratum 1 declares 246 rows excluded; analysis must read viv.register_clean (migration 003); (b) on
09-11 the tick read 0 fossils on 45/45 ticks ("sfe db not found") so every autonomous proposal that
day was effectively random; (c) one candidate_set_id reused per campaign misbound executions as
one-chosen-over-N. Artifacts: TIER0_TIER1 s11, MACHINE_REPORT s9, INVESTIGATIVE_REPORT s5,
migrations/003_register_errata.sql. Outcome: CONTAMINATED (register) / INSTRUMENT FAILURE (producer
input) for any selection-quality claim.

V-3 C3-1 (cs-c3-1), density-classification CA. 2026-09-10. Question: Herakles/Archaeon "C3" rule
density comparison (null/base/hist arms). Kind ca_density_v0. Every executed row FAILED at the
executor: producer sent "ic_density_set": null instead of [null]; 24 rows lost (null 12, base 6,
hist 6 -- proportional to arm size, checked by Vivarium), each after world + fossil were committed.
Artifacts: NOTES_POSTMORTEM I-3; BACKLOG D2; H0H5_STATUS line ~243. Outcome: INSTRUMENT FAILURE.

V-4 C3-2 (cs-c3-2 + r1). 2026-09-10. Question: exact-symmetry null and whether random tables /
"acquired" rules carry density-classification ability (D3-over-C3-acq). Arms: C3-null 18, C3-hist 6,
C3-base 6, C3-acq 120 random tables; 4 shared IC samples, 149 cells, 320 steps,
success_criterion=stable. Reported: null 18/18 IDENTICAL (symmetry control passes); every C3-acq
random rule 0.0 on every IC sample -> "116/116 random rules structural zeros; D3-over-C3-acq
STRUCTURALLY_VOID" (Archaeon wake 14, 9e6c1ff0c); 1 transport failure reissued. Later: Vivarium
showed the zeros are a property of the CRITERIA, not of the rules ("maj is not a structural zero, it
was an unmeasurable one"; maj 0.0/0.0/0.5919 cellwise; random tables ~0.49-0.51 cellwise, 30e97ed94).
Harmonia separately found D3 UPPER fires on SFE charts to be TREND artifacts (H0H5_STATUS line ~211).
Artifacts: archaeon/docs/h0h5/C3_2_READOUT.md, C3_2_NULL_CHECK_HERAKLES_2026-09-10.json. Outcome:
MIXED (null control positive; acquisition arm a ruler-floor null -- effectively INSTRUMENT FAILURE
for the acquisition question).

V-5 H1/H0 alpha (cs-h1h0-1-p1, -p2, -p2-r1, -p2b), cegis_boolean_v1. 2026-09-10. Question: H1 --
does a transported failure pack from related tasks seed more discriminative CEGIS constraints than a
random pack at equal caps; H0 -- does a component library interact with it (four cells S00/S10/S01/
S11). 12 targets, vm_op_cap 6000. Reported (H1H0_PHASE2_READOUT): solved of 12 -- fresh 2,
random_pack 2, S00 2, S10 2, S01 3, S11 3; every unsolved row BUDGET_VM_OPS; degeneracy check
BIT_IDENTICAL as designed; H1 contrast label "transport_only ... relevance inert at this scope
(Harmonia 745d9c698)". History: all 48 artifact-bearing phase-2 rows first FAILED with 404 on
/budget/reserve because the running consumer was 4h47m older than the fix and the engine was schema 7
(I-1, the "consumer build lag" incident); Archaeon's cancel predicate also swept 14 slot-free rows by
mistake; reissued as -p2b, 48/48 completed. H0 library cells had ZERO eligible input on this split
("nothing could have fired"). The S01/S11 component library was flagged instrument_control: true
(H1H0_PHASE2_LOCATORS); separately Vivarium's own demo library was found to contain a complete
solution to one of its own tasks (105893e2f) and a "library solved maj3" line reported 09-10 was
withdrawn as "contamination measuring itself". Whether the campaign's S01/S11 instrument library is
the same object as the leaky demo library: UNKNOWN (see open questions); tgt-11 solved only in the
library cells is exactly the shape the leak checker exists to catch. Outcome: REPORTED NEGATIVE/NULL
for H1 relevance; INCONCLUSIVE for H0 (eligibility zero).

V-6 H5-1 (cs-h5-1, 256 rows + cs-h5-1-r1, 24 rows), eca_rule_eval_v1. 2026-09-10/11. Question:
calibrate the H5 instrument (does an encoding change evolvability/class reach). Reported: 256/256
rules read, 224 classes, 0 disagreements with Herakles's published map; reach quantities at the
analytic bounds -> "calibration, not evidence" (H5_1_READOUT_2026-09-11.md). History: 24 rows lost
in two engine stall episodes (rows 143-155 contiguous, 245-255); Vivarium flagged that a 13-row gap
"is the shape most likely to be read as a property of rule space" (8e4fc377a); the shared
candidate_set_id made Vivarium register ~255 uncommitted alternative experiments per row -> 85,727
phantom experiments and 510 OPEN selection families, and the stall episodes FOLLOWED those write
bursts (INVESTIGATIVE_REPORT s6; causal link proposed, not proved). Outcome: INCONCLUSIVE
(instrument calibration; no evidential reach by construction).

V-7 Fossil metabolism S1 (cs-fossil-s1). 2026-09-12. Question: does consulting the fossil record
improve proposal quality vs the uniform policy. 12 matched pairs F (best fossil + one bit flip) vs C
(uniform draw), evaluate_bitstring, preregistered (S1_PREREG, commit 8fc994e1f, 66 s before rows).
Vivarium receipt: EXECUTION_CLEAN (24/24, 9.5 s, 0 retries, identity vs prereg 24/24). Reported
(Archaeon): wins 8 / losses 4, exact p 0.194 vs critical 10 -> NO_DETECTABLE_ADVANTAGE; every F
score landed on its arithmetic prediction set. Follow-on S2 census (analysis, not execution):
REPRESENTATION_INFORMATION_SPARSE. Outcome: REPORTED NEGATIVE/NULL (with a power ceiling: n = 12
pairs and a one-bit rule whose predicted advantage on L = 32 was 0.059).

V-8 Point-release qualification and production canaries (window C4-20260917-W1). 2026-09-17.
Question: is the absorbed transaction model (attempts, keyed steps, replay, outbox) correct on
production. 11 canary runs (GKL ca_density rows; deaths inside the repeat loop and while posting);
10 production defects found and fixed with acceptance tests (session-bound worlds 403
SESSION_MISMATCH; WORK_NOT_CLAIMABLE after completion; 409 one-ORIGINAL-per-experiment; page-object
list routes read as absence; Idempotency-Key reuse across rows; 4xx mis-typed as ENGINE_TRANSPORT).
Final: canary run 11 OK 35/35 with zero human commands; disposition QUALIFIED_FOR_CAMPAIGN with
named caveats (point_release/READINESS_DISPOSITION.md). Outcome: REPORTED POSITIVE (infrastructure).

V-9 Campaigns 4/5/6 (SFE program). 2026-09-18. Vivarium did NOT execute science rows: C4 "could not
be honoured ... no admissible kind evaluates a program variant"; C5 "wse_evaluate_v1 did not exist";
C6 lane designed (segment kind, provenance labels, T0/T1 telemetry, replay packets, fixture
commitment) and nothing built. Outcome: UNKNOWN for the queue (no Vivarium-executed rows).

Also through Vivarium code but not its queue: Theophrastus's ecology rounds (09-13/14) built Vivarium
ExecutionRequests and called SfeRunner as a library under its own SFE client
(theophrastus/adapter.py); a Theophrastus row failed on Vivarium's off-by-one witness bound
(INBOX_THEOPHRASTUS_WITNESS_BOUND_OFF_BY_ONE_2026-09-14.md). Those campaigns belong to the
Theophrastus dossier.

-------------------------------------------------------------------------------------------------
## 9. False-positive / false-negative archaeology

T1 "The fix is in" vs "the fix is running" (the consumer build lag incident).
claim: 09-10 Vivarium told Archaeon the schema-7 fallback was on main -> evidence: the running
consumer PID 29884 started 07:29:23, fallback landed 12:16:52 (4h47m later) -> challenge: all 48
artifact-bearing H1/H0 phase-2 rows failed 404 -> correction: viv.cli stop (C4, 57eb8d148), running
SHA in heartbeat (C6, fa14903d7), restart receipts, pinned worktree; recurrences I-5 and I-6
(09-11: the pinned build predated a runner fix described to Archaeon as closed, c13867fcc) ->
current status: base-role doctrine ("process and control state can lie by implication -- a consumer
running a build four hours older than the fix reported as closed", roles/base-role/RESPONSIBILITIES.md
~line 45) and fleet memory "deployed is not live". No result was reversed; 48 rows lost and reissued.

T2 Phantom experiments and engine stalls.
claim: Daedalus measured stall episodes as "one client's burst of hundreds of creations, then the
stall" without naming the client -> evidence: Vivarium identified itself (85,727 CREATED-never-
observed experiments, 99.4% of what it wrote; per-minute bursts preceding episodes 1 and 2) ->
challenge: no counterfactual run -> correction: Archaeon's submit refuses reused candidate sets
(6fc3ea619), Vivarium's trigger VIV01 (005); Daedalus later attributed the root cause to a consumer
SMR disk (C: NVMe burst 20.6 s vs F: SMR 633.8 s, e031cb4fb) -> status: two candidate causes
recorded, both mitigated; the phantom residue remains in the M1 ledger and any experiments-per-world
reader must filter state=OBSERVED or overcount ~164x in cs-h5-1 worlds.

T3 Stall gap that looked like science.
claim-risk: H5-1 rows 143-155 missing contiguously -> Vivarium flagged before interpretation that a
contiguous gap "is the shape most likely to be read as a property of rule space" (8e4fc377a) ->
reissue r1 closed it -> status: a near-miss false positive, correctly prevented.

T4 Stranded-row rule: from doctrine to automation.
claim: charter invariant 6 and the 09-11 operator ruling: never resolve a stranded row by inference
-> evidence: crash demo, ORPHAN_VERDICTS -> challenge: Campaign 4 "make S3-S6 boring" (PROMPT 3) ->
correction: 09-17 the dead-man releases a dead worker's rows to a NEW ATTEMPT automatically and
auto-clears transport parks (bounded); engine-verified replay of steps makes this safe IN DESIGN ->
status: the rule cited across the fleet as the model of fail-closed behaviour is, in this seat's own
code, now a bounded automatic transition. The safety argument rests on step verifiers that find acts
"by content" (12f815a66), proven on 11 canaries; never exercised on a real campaign.

T5 Orphan classification.
claim: Daedalus's first classifier labelled 5 abandoned runs "pending" -> Vivarium's verdicts
(119 committed-but-unobserved: ABANDONED 33, NOT_FROM_THIS_REGISTER 79, RUNNER_MADE_UNREGISTERED 7)
-> challenge inside the seat: 24 of 33 "abandoned" were executor refusals (C3-1), not stall
casualties; the frame reader named the wrong failing call twice -> status: committed-but-unobserved
has at least two causes the ledger cannot separate; Vivarium's own ORPHAN_VERDICTS ledger is the
record (ledgers/ORPHAN_VERDICTS_2026-09-11.json).

T6 Ruler floor read as a structural zero (C3-2).
claim: 116/116 random rules are structural zeros; D3-over-C3-acq STRUCTURALLY_VOID -> evidence:
0.0 on every IC sample under stable -> challenge: Vivarium/Herakles: 40/40 random tables score 0.0
under BOTH masks, so the masks cannot rank anything; cellwise criterion gives ~0.49-0.51 for random
tables and 0.5919 for maj -> correction: third criterion added (30e97ed94) -> status: the
acquisition arm of C3-2 is a false-negative regime (ruler saturated at its floor), not evidence that
the rules lack density information. No rerun under cellwise found.

T7 Component library: contamination measuring itself (H0).
claim: 09-10 "the library solved maj3 (unreachable without it) and lost xor3" (W-2) -> challenge:
Techne showed an extracted library contained complete held-out solutions; Vivarium found its own demo
library contained and(x0,x1) = task and01 and the subterms of maj3 (105893e2f) -> correction:
viv/library_leak.py (SOLVES_A_TASK, COMPOSES_TO_A_TASK at depth 1) run BEFORE counts are printed;
the ALL_17 leak was the cheat control firing correctly -> status: the maj3 line is withdrawn; H0
library cells had zero eligible input on the H1 split ("nothing could have fired"); ARCH-29 demands
a task family with shared parts and an eligibility count before any H0 run. Never rerun.

T8 Seeding is not monotone (H1 mechanism).
claim: seeding CEGIS constraints makes rejection cheaper (W-1) -> measurement: cut oracle calls
everywhere, cut VM ops on fast targets, RAISED VM ops ~47% on maj3 -> status: caught before it
became a claim; recorded in cegis_boolean.py docstring as the reason H1's sign is not decided by the
design.

T9 Degeneracy guard hole.
claim: degenerate_by_construction catches zero-variance repeats -> challenge (Herakles 09-06):
random_walk_v0 under constant seed + reset gave four identical displacements and was NOT flagged ->
correction: stateful exemption removed (WP-0b, 295482d4e) -> status: fixed; a zero-variance unit
could have been read as a measured null before 09-08.

T10 Producer input zero (fossil-informed selection).
claim (implicit in any autonomous-tick result): proposals are fossil-informed -> evidence: tick log
"fossils": {"rows": 0, "error": "sfe db not found"} 45/45 on 09-11 -> correction: Archaeon's fossil
repair 29f1f54b8 (09-12) -> status: any selection-quality inference from autonomous rows before
09-12 had no fossil input; later S1 tested the question properly and found no detectable advantage
at n = 12.

T11 Test rows in production.
245 Archaeon pytest rows landed in viv.research_experiment_queue on 09-06 and a live cycle claimed one
(TIER0_TIER1 s11 item 1). Nothing deleted; erratum 1 enumerates 246 rows; viv.register_clean is the
analysis surface. Atlas records "246 test contamination" (inference_harvest digest
atlas_index_and_history.md row 22). Status: CONTAMINATED rows quarantined by enumeration.

T12 Accepted-but-inert fields.
claim (Vivarium 09-10): two engine defects in cost-event indexing -> challenge: Daedalus reproduced
the opposite -> correction: Vivarium had put refs on the cost EVENT instead of the resource ENTRY;
"accepted but inert is what a dropped field looks like from the outside" (I-2, 6c779ddef) -> status:
a false positive about another seat's engine, retracted by the seat itself.

T13 Unresolved: the dormant queue as a false-negative regime for the whole SFE pathway.
From 09-18 science moved to in-process harnesses because the queue lacked kinds (Artemis F15). Any
Phase 3 reading that "SFE/Vivarium produced little science" must separate "the instrument was idle
and kind-starved" from "the hypotheses failed".

-------------------------------------------------------------------------------------------------
## 10. Research outputs

- roles/Vivarium/DELIVERABLE_V0_2026-09-05.md -- v0 build, state machine, identity linkage, 8
  unresolved failure modes stated up front.
- roles/Vivarium/BOUNDARY_REVIEW_2026-09-05.md -- boundary review against Harmonia S13-S18 (not read
  in full; summarised by a0f70c72d: notes/experiment_kind/world.name leak policy into spec_hash; the
  runner could see the arm; `length` defaulted to 24).
- roles/Vivarium/TIER0_TIER1_REPORT_2026-09-06.md -- "sealed spec contains exactly the execution
  inputs; provenance lives outside the hash"; idempotency/replication semantics; production
  contamination finding.
- roles/Vivarium/MACHINE_REPORT_2026-09-06.md -- unattended producer/consumer loop, crash test,
  contamination erratum.
- roles/Vivarium/H0H5_ITERATION1_RECEIPT_2026-09-09.md and _ADDENDUM_2026-09-10.md -- artifact loader
  slice, 24 real boundary executions on a dev engine, "NO scientific result".
- roles/Vivarium/NOTES_POSTMORTEM_2026-09-08_to_09-11.md -- the most useful single document: six
  incidents, six self-corrections W-1..W-6, patterns P-1..P-6 ("deployed is not live"; "aggregates
  hide the finding"; "exact keys without exact values").
- roles/Vivarium/INVESTIGATIVE_REPORT_2026-09-11.md -- operator-requested current-state audit:
  phantom experiments, tick reading zero fossils, orphan work items, tenant sprawl.
- roles/Vivarium/BACKLOG_H0H5.md -- 24+ items with blocker owner per row.
- roles/Vivarium/ledgers/{S1_SEASON_RECEIPT,CANARY_ONE_ROW,B1_RECURRENCE_RECEIPT}_2026-09-12.md,
  ORPHAN_VERDICTS_2026-09-11.json -- execution receipts.
- roles/Vivarium/point_release/* (13 docs) -- transaction model, identity translation contract,
  start bundle, intervention/gate receipts, termination envelope, PEW outbox, production descriptor,
  evidence inventory of Campaigns 1-3, Stage-2 self-critique, readiness disposition.
- roles/Vivarium/campaign6/{DIRECTIVE_verbatim,VIVARIUM_LANE_2026-09-18}.md -- Campaign 6 data-plane
  design (segment as unit, provenance classes, EXOGENOUS/ENDOGENOUS pressure tags, replay classes
  A-G, fixture commitment).
- roles/Vivarium/receipts/{CONSUMER_DEATH_2026-09-13_WT_CRASH,CONSUMER_DEATH_2026-09-14_M1_REBOOT,
  INCIDENT_2026-09-24_M2_HOST_EXHAUSTION}.md -- postmortems.
- vivarium/docs/{ARTIFACT_LOADER,CEGIS_BOOLEAN,EXTERNAL_BACKEND_CONTRACT}.md -- design notes (the
  external-backend contract's rule is "no").
- roles/Vivarium/REVIEW_PACKET_M2_BOOT_2026-09-16.txt -- review packet.
External prior-art comparisons, literature reviews: none by this seat.

-------------------------------------------------------------------------------------------------
## 11. Journals, TODOs, pivots, abandoned branches

Journals: roles/Vivarium/journal/2026-09-{11,12,14,16,17}.md (journals were gitignored until the
09-11 base-role fix that Vivarium itself triggered). STATUS.md currency 2026-09-17 16:4x UTC, never
updated after the 09-19 park or the 09-24 incident (STATUS still says "Is Vivarium alive: YES").
No WORK_STATE.json, no RESUME file. BACKLOG_H0H5.md is the TODO.

Major pivots (dates, cause):
1. 09-05 -> 09-06: v0 single-observation rows -> spec v3 `repeat` (N observations in one world)
   because no family could reach S17's >= 4 observations-per-world eligibility (b70d7a665).
2. 09-06: provenance moved out of the hash after the boundary review (a0f70c72d, 63c39a636).
3. 09-08 .. 09-10: from executor of bitstrings to integrating owner of the H0-H5 loader and wrapper of
   three libraries (CA, ECA, CEGIS).
4. 09-11: base-role adoption; reliability stack (conformance identity, running-code identity,
   worker-address identity) ordered by the operator.
5. 09-13/14: two unobserved consumer deaths (11.9 h behind a Windows Terminal crash; 35.9 h after the
   M1 reboot) -> dead-man design.
6. 09-16: relocation to M2; store identity guard after an unset VIV_DB_HOST reached a quarantined
   fork (incident c84e26826cc12217).
7. 09-17: point release -- absorption of Archaeon's campaign-runner durability semantics; claim-once
   rows become multi-attempt rows; human recovery becomes bounded automatic recovery.
8. 09-18: Campaign 6 design; operator ruling that the SFE ledger moves off SQLite (Harmonia #448)
   undercut the substrate the queue was qualified on; nothing built.
9. 09-19 -> 09-24: idle park, then host exhaustion incident; F1/F2 fixes designed, not built.
10. After 09-24: silence. MWO-0001/0002 left Vivarium unchanged; Aphrodite's C1 contracts unanswered.

Abandoned / superseded: archaeon.probe.v0 kind (retired 09-06, kept readable); a self-built
"calibration rung" deleted when Archaeon's routing was found better (MACHINE_REPORT s10 item 5);
migration drafts under vivarium/migrations/drafts/ (promoted byte-identical 09-17); branch
vivarium/v0-2026-09-05 (retired; now only carries other seats' already-merged content); branch
vivarium/base-role-adopt-2026-09-11 and worktree-vivarium-campaign-e1-e6-e16 (merged); the
Campaign 6 build order items 1-7 (never started); wse_evaluate_v1 (promised "build now regardless",
never built).

-------------------------------------------------------------------------------------------------
## 12. Lens inventory

L-V1 The sealed-execution data plane (queue + runner + attempts + outbox) as a PROVENANCE lens.
- Substrate observed: any executor kind's results, with who-asked-why kept outside the hash.
- Organisms/worlds/pressures: none of its own; whatever kinds are registered.
- Phenomenon family: not a phenomenon -- it resolves "what exactly ran, once, under which sealed
  inputs, and what happened", including failures and selection (candidate sets, cancelled
  alternatives, errata).
- Current resolving mechanism: Postgres constraints/triggers, spec-hash read-back from the SFE
  ledger, blinding of the executor, keyed steps with REPLAYED/RECOMPUTED, outbox ordering.
- Resolution ceiling: one row per SFE world, ~a dozen REST calls per row, single global slot; SFE's
  SQLite ledger and its ~400-900 events/s ceiling; qualified only on toy kinds and 11 canaries.
- Noise sources: engine stalls, host resource exhaustion, consumer deaths, deploy lag, credential
  and topology drift (M1/M2), self-park on idle.
- Architectural limitation: unit of work is too small and too expensive for evolutionary runs
  (Vivarium's own C6 analysis); outcome rule is a single-field comparison; no multi-world attempt.
- Reusable: the sealed-spec rule (exact execution inputs only), blinding, frozen relations,
  enumerated errata with a clean view, candidate-set register with cancellation-not-deletion,
  attempt/step replay semantics, intended-vs-realised intervention receipts, the cheat-control
  discipline, the library-leak checker.
- Toy-grade: the kinds, the single-slot scheduler, the dependence on SFE's REST/SQLite substrate.
- Unknown: behaviour under any real long run; whether the outbox/replay model survives the SFE
  ledger move off SQLite.

L-V2 ca_density_v0 wrapper as a density-classification lens (semantics Herakles's).
- Substrate: radius-3 binary CA rule tables on a periodic ring.
- Phenomenon: global coordination (majority) from local rules; symmetry invariance.
- Mechanism: accuracy under three criteria, fixed-point facts, witness ICs, exact-symmetry null.
- Ceiling: random-rule accuracies collapse to a floor under at_T/stable; one task; radius 3 only.
- Noise: IC ensemble choice (unbiased vs Bernoulli vs exact-count are different ensembles).
- Reusable: the exact-symmetry null and the measured (not declared) transform flags.
- Toy-grade: fixed task, small rule sample. Unknown: anything about acquired rules under the
  cellwise criterion (never rerun).

L-V3 cegis_boolean_v1 as a reuse/transfer lens (semantics Proteus's).
- Substrate: 3-input Boolean expression enumeration with counterexamples.
- Phenomenon: whether transported failure inputs or a component library reduce search cost.
- Mechanism: cost-at-fixed-cap contrast on a fixed enumeration order; budget statuses kept distinct;
  leak checker.
- Ceiling: 256 possible targets, 12-task family, zero shared abstractions on the H1 split; most rows
  hit the 6000 VM-op cap.
- Reusable: "the empty input is a declared input" (null slots inside the hash), budget-status
  taxonomy, leak checker.
- Toy-grade: the arity and the task family. Unknown: behaviour on a family built with shared parts
  (ARCH-29), or on the 4-6-input extension (A7, never built).

L-V4 eca_rule_eval_v1 / H5 as an encoding-evolvability lens.
- Substrate: 256 ECA rules on a 7-ring, 8 steps, exhaustive.
- Mechanism: behavioural equivalence classes; class reach under decoders.
- Ceiling: quantities at analytic bounds by construction; "calibration, not evidence".
- Reusable: the class map as a calibration fixture. Toy-grade: the scope.

L-V5 evaluate_bitstring as a fossil-metabolism lens (Archaeon's question).
- Substrate: hidden-target Hamming landscape.
- Phenomenon: does reading prior scored fossils improve proposals.
- Ceiling: each fossil is exact Hamming information; the landscape is onemax; n = 12 pairs.
- Toy-grade: entirely. Reusable: the preregistration-to-execution reconciliation pattern (S1).

-------------------------------------------------------------------------------------------------
## Atlas and cross-seat disagreements recorded

- Atlas comb.py deliberately excludes engine_id 'vivarium' from conclusions ("executor terminal
  states are not conclusions") -- consistent with the charter.
- Atlas counts 1,242 Vivarium experiments / 1,254 attempts (REPORT_2026-09-19.txt); Vivarium's
  window receipt counts 1,155 rows (09-17); Artemis quotes 579/492/79 = 1,150 by 09-16. The
  difference is post-window canary and held rows; not a contradiction, but any count must name its
  snapshot. Atlas PACKET_2026-09-19 cites 66,958 engine experiments 09-01..11 (63,403 Vivarium) while
  the Atlas SFE digest cites 89,939 (86,296 Vivarium) -- different windows; both are dominated by
  phantom CREATED experiments, not observations.
- Artemis REPORT s2.2: "parked with SFE unreachable". Source: the consumer parked 09-19 on its idle
  bound with an empty queue (#483); SFE unreachability is the later dead-man refusal (#573).
- Achilles census: "no vivarium/ commit since 2026-09-17" -- true for code; roles/Vivarium/ has
  8c5a1a23b (09-24).
- Fabric S3 Q7 (Artemis #1014, workers' claim, unverified here): a density-CA intervention on
  Vivarium-derived rules (derive_edit / derive_flip since 09-16) was never submitted.

-------------------------------------------------------------------------------------------------
## Open questions / unknowns

1. Was the S01/S11 component library used in cs-h1h0-1-p2b (instrument_control: true) the same
   hand-built demo library later found to contain a complete task solution (105893e2f)? If yes,
   tgt-11 solved only in S01/S11 is contamination. Not settled from the files read.
2. What is the current state of the viv schema rows, the M2 consumer, dead-man and deliverer tasks,
   and SFE 8811 / PEW 8377 on SPECTREX5? Last evidence 09-25 (#573); not probed here.
3. The burst-stall causal link (phantom experiment bursts vs SMR disk) was never tested by the
   proposed counterfactual on Daedalus's twin.
4. Whether the automatic NEW ATTEMPT release (T4) was ever exercised on a non-canary row: no
   evidence found; the queue had no rows after 09-18.
5. C3-2 acquisition arm under the cellwise criterion: never rerun; the "structurally void" reading
   stands on the record without its correction having been applied to data.
6. Exact lifetime queue counts after 09-17 (Atlas 1,242 vs window 1,155): not re-derived.
7. Who owns Vivarium now: no WORK_STATE, no MWO adoption, Aphrodite's E1-E4 envelope requests open.
8. Whether the 7 QUEUED orphan SFE work items and the 7 + 2 runner-made orphans were ever
   adjudicated (D7 closed in code 09-16; residue not cleaned by design).
