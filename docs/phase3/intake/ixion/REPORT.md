# Ixion -- Phase 3 intake: Prometheus as an institution (forensic crawl report)

Seat: Ixion[m1-c3692e75], one of four Phase 3 forensic crawlers (siblings with charters on main: Sisyphus, Tantalus;
Tityos seat created 6a6d6d9b4, no charter on main at crawl time).
Charter: roles/Ixion/prompts/2026-10-01_charter/ (verbatim + MANIFEST, committed b871bcd38 before any output).
Date: 2026-10-01 (UTC). Repository state read: origin/main bed05507a, worktree
F:\Prometheus-worktrees\ixion-phase3, branch ixion/phase3-intake-2026-10-01. Host: SKULLPORT (M1).

Territory (14 seats): Atlas, Atlas-M2, Mnemosyne, Aporia, Odysseus, Hephaestus, Achilles, Agora, Pronoia,
Alethelia, Hermes, Cyclops, Metis, Atalanta -- plus the shared institutional infrastructure they built or
run (comms, ops/work_orders, ops/fleet, fabric, scripts/ schedulers and mailers, MONITORS registry,
evidence_wiki, atlas schema).

This report reconstructs what exists and what it does. It does not design Phase 3, recommend, launch
experiments or wake retired seats.

## 0. How this was produced, and how far to trust it

Method. Ixion wrote one shared brief and ran six read-only sub-crawls in parallel:
atlas (Atlas, Atlas-M2), fleet (Achilles + comms/ops/scripts/scheduler/MONITORS), memory (Mnemosyne,
Hermes, evidence_wiki), coord (Aporia, Cyclops, Agora + coordination history), build (Hephaestus, Odysseus,
fabric, forge, deploy, shared libraries), hist (Metis, Atalanta, Pronoia, Alethelia). Each read code, git
history (including deleted files and superseded/ bodies), and ran read-only SELECTs on the M1 Postgres
schemas its seats own (sessions forced READ ONLY). They also ran schtasks /query on M1. No git writes, no
process kills, no comms posts, no experiment or service runs. Every search excluded **/*holdout*/** and
**/nestor_secrets/**. No credential value appears in this package; where files carry credentials, only
the file is named.

Epistemic tags are used inline throughout this package: [IMPL] implementation fact (read in code, data or
receipt; cited), [INTENT] design intent, [HIST] historical claim, [REPORTED] reported result -- unverified,
[CORR] later correction or contradiction, [INFER] code-inferred capability, [UNK] unknown or ambiguous.
Infrastructure success claims without receipts are tagged [HIST].

Ixion's own verification of sub-crawler claims (re-run independently by Ixion on 2026-10-01):

    claim                                                      Ixion check                                   result
    comms holds 1,239 messages                                 SELECT count(*) FROM comms.messages           1,239  MATCH
    ew.experiments = 79, created 09-01..09-03                  SELECT count, min, max(created_at)            79, 09-01..09-03  MATCH
    Atlas: 192 signals, all OPEN                               SELECT status,count(*) FROM atlas.signal      OPEN 192  MATCH
    Atlas: 30 identity collisions                              SELECT count(*) FROM atlas.identity_collision 30  MATCH
    Fabric attempts only on ubu001 (337) / ubu002 (36)         SELECT host,count(*) FROM fabric.attempt      337 / 36  MATCH
    68aab291f (Gravity Pilot) reached main as 3faf6c98b        git patch-id --stable on both; merge-base      identical; 3faf6c98b on main  MATCH
    432 commits touched WORK_STATE.json since 09-27            git log --since=2026-09-27 -- roles/*/WORK_STATE.json | wc -l   432  MATCH
    PrometheusMachineProbeM1 enabled and failing               schtasks /query /tn ... /v                    Enabled, Ready, Last Result -2147024894  MATCH
    Operator brief is written by an LLM cascade (memory)       metis_portfolio.py:452-460; brief e9cf5ee16   NOT MATCH -- deterministic by default; corrected in seats/Hermes.md, engine_index.jsonl, inference map

One of nine checks failed. It was the claim that put the operator brief on the model side of the
boundary. The other eight hold. Read the package with that rate in mind: claims are cited and mostly
right, and a minority are wrong in ways a single line of code settles.

Package contents (docs/phase3/intake/ixion/):

    REPORT.md                    this file
    seats/<Seat>.md              14 dossiers, 22 numbered sections each (the charter's 20 + inference
                                 classification + false-negative/false-positive watch), 166-542 lines each
    artifact_index.jsonl         398 artifacts (438 rows from six crawls, de-duplicated by path), tagged
                                 IMPL 258 / INTENT 47 / HIST 44 / REPORTED 28 / CORR 15 / INFER 6
    engine_index.jsonl           76 executable systems (per-crawler perspective kept; disagreements annotated
                                 in ixion_note / ixion_correction fields)
    inference_dependency_map.md  the current boundary: charter example functions + 143 classified rows
    institutional_timeline.md    242 dated events, 2026-03 .. 2026-10-01

Note for anyone committing under docs/: `.gitignore:292` ignores `docs/*` (only the Pages files are
re-included). This package is tracked with `git add -f`; the ignore rule was not changed.

## 1. The territory at a glance

    seat         state (evidence)                         what it actually runs / ran                           live code path            inference
    Atlas        READY; index loop PARKED since 09-19     experiment/fact index on M1 (schema atlas, 34 tables)  atlas/ CLI, run by hand   code free; triggers + catalogue + synthesis model
    Atlas-M2     idle since 09-25                         one harvester (frontier_runs_m2.py) for M2 receipts     atlas/harvest/...m2.py   code free; session-triggered
    Mnemosyne    silent since 09-18; PEW down since 09-23 Evidence Wiki (ew schema + REST), campaign reader       evidence_wiki/ew          store free; claims model-extracted
    Aporia       harvest until 10-01 05:00 ET; CWO dispatcher  MWO publisher, fleet QUEUE/CENSUS (hand-edited)     ops/fleet/fleet_status.py coordination model-mediated
    Odysseus     active (fabric, promexec, D2 audits)     Agent Fabric v0.2 (live, idle), promexec (not enabled)  fabric/                   execution free; audits model
    Hephaestus   last seen 09-25; two unreconciled 2.0 framings  forge corpus (Mar-May), closure gauntlet, xpol     hephaestus/src            gauntlet free; generation model
    Achilles     active; census every 6 h on ELSA         59-seat fleet census, page, email block                 achilles/census           free per run; registry built once by model
    Agora        retirement recommended 09-14, AGORA-01 unruled  April Redis bus (dead), work_queue (dormant)      agora/                    free
    Pronoia      Era-2 loop live on M4 (health productive)  intelligence loop -> state -> brief -> email          scripts/intelligence_loop deterministic since 08-18
    Alethelia    DORMANT, no host since 09-11              truthful reporter (value + query per field)            agents/alethelia          free
    Hermes       deprecated 05-17; re-seated 09-11          mailer lineage (send_brief_email.py), convergence probe scripts/send_brief_email   free
    Cyclops      PARKED (twice)                            SI steward, MWO-0001 registrar, observability audit     prepost_check.py          rulings model
    Metis        "SEASON 1 CLOSED"; no retirement ruling found  Era-1 LLM analyst; fleet reporter; compose.py      roles/Metis/season1       compose free
    Atalanta     retired                                   primitive-hunter daemon (0 Apollo runs read)           agents/atalanta           free (never fed)

Sources: each seats/<Seat>.md sections 1, 2, 7, 14, 21. "State" is what the evidence shows, which in four
cases differs from the Achilles census label (section 9).

## 2. Atlas -- deep reconstruction (summary; detail in seats/Atlas.md)

What it is. [IMPL] A Postgres schema `atlas` on M1 (34 tables, about 639 MB), loaded by versioned Python
harvesters that read git blobs, idle SQLite ledgers and other Postgres schemas. 13 hash-locked migrations.
Every row points to a harvest_run (harvester version, host, seat, instance, atlas_sha, source ref/sha), and
every fact points through fact_evidence to a source (ref, commit, blob, path, line range). A full M1 pass
of 13 harvesters plus the signal comb took about 86 s wall (harvest_run 305-320, 2026-09-30).

The charter's 17 items, by what form they exist in (seats/Atlas.md "Atlas deep reconstruction"):
- Code + populated data: indexed engines (15 registered, 5 with experiments indexed); experiment and
  attempt schemas (2,053 experiments modelled; 2,951 experiment-level primitive rows); evidence pointers;
  facts (33,054 live after the 09-30 collapse of 299,991 duplicated suppression-echo facts); lineage/cross-
  engine edges; weak-signal detectors (atlas.comb, 13 SQL rules R01-R13, 192 signals); identity collisions
  (30 rows: RECEIPT.campaign="cmp2" on cmp3/4/5 experiments, confirmed against the RECEIPTs); lag (computed).
- Code + model-authored data: theory graph and primitive ontology (session-authored JSONL ledgers; 10
  propositions with first_stated_at/last_reviewed_at NULL; some bases cite the operator); external
  ecosystem catalogue (six web-survey subagents -> JSONL -> loader); research-policy layer (fixed-weight
  scoring over model-written proposal fields; 92 scores, 0 with an outcome; ruled REPORTS ONLY 09-25).
- Prose only: buried-signal work (ATLAS_BURIED_SIGNALS_AND_RESIDUALS.md, model digests); reanalysis plans
  and ruler-side ontology fields (ATLAS_ONTOLOGY_GAPS_VNEXT.md).
- Effectively empty: world x organism x pressure catalogue (pressure_family 0/2,053, ruler 0/2,053,
  world+organism both set on 5); field_conflict (0 rows).

Where its records come from, and the reliability class each deserves [IMPL unless tagged]:
1. Parsed from machine ledgers/receipts (counts, wall times, ids): HIGH. Matched source in every sample
   (158 = 158 NPE graphworld receipts; 130 = 130 frontier RUN events; Vivarium 1,242 = 1,242; fact values
   exact at blob/line).
2. Disposition/class words (atlas_class POSITIVE/NEGATIVE/...): LOW. A regex ladder maps COMPLETE / PASS /
   completed to POSITIVE. 649 of 723 POSITIVE rows are Vivarium queue "completed", and CW01 e01/e03
   "COMPLETE" become POSITIVE. The machine candidate overrides the author's RECORD verdict: C5-03 shows
   WEAK_POSITIVE (n=1 vs 1, effect 0.0) where RECORD.md:116 says REPRESENTATION_QUALIFIED.
3. Commit attribution: MEDIUM. Regex over subjects/trailers; 31% of 7,419 indexed commits have no seat.
4. Primitive/combination layer: NOT A MEASUREMENT. Inherited per campaign from 4 hand-labelled rows; the
   Vivarium experiments get none. "TESTED/UNEXPLORED" describes labels, not experiments. Atlas recorded
   this about itself on 09-30 [HIST].
5. Catalogue/theory/proposals: MODEL-AUTHORED, stored beside parsed rows with the same SQL surface. In 16
   catalogue systems the "verified links" string disagrees with the attached reference rows, and Artemis
   marks two catalogue URLs UNVERIFIED that Atlas marks VERIFIED [CORR].
6. Registry prose: STALE-PRONE. The NPE engine note still says the code is not on origin/main; it was
   merged in b10161316 on 09-22.

Lag. [IMPL] The newest modelled experiment activity is 2026-09-22 15:07 (-0400) against roles/Nestor HEAD
2026-10-01 05:09, a lag of 8.58 days. 275 Nestor and 57 archaeon commits since 09-22 are not modelled.
PTE, BEE, Aether, Hecate and Tyche are not registered at all. Atlas's own lag metric uses the newest commit
anywhere, not per area.

Usefulness as a Phase 3 design-corpus substrate (observational). It can supply, with row-level provenance,
the parsed numeric history of the engines it adapted up to 09-22. It cannot by itself supply: anything
after 09-22; the five unregistered engines; trustworthy outcome classes; primitive usage; world/organism/
pressure axes; or M2-local evidence (71+ frontier receipts, SFE ledgers, BEE raw results; the M2 pass ran
once, on 09-19). The 09-30 inference harvest had to reconstruct cross-engine state from prose digests with
about 14 model readers, synthesists and verifiers because the index had stopped. All loops are open: no
signal, score or conflict has ever been consumed. No scheduled task runs any Atlas step. Atlas is a map:
accurate where it parses ledgers, unreliable where it classifies, empty where it was meant to theorise.

## 3. Achilles -- deep reconstruction (summary; detail in seats/Achilles.md)

[IMPL] achilles/census is deterministic per run. It enumerates roles/ directories on all origin refs
(10,679 commits deep, in about 40 s) plus a registry (88 seats, 133 engines), joins comms, ew and agora,
and emits fleet_state.json (1.28 MB), an HTML page (0.69 MB) and an email block. Two scheduled runs
succeeded (189e12502, db657a6df). The 6-hourly task runs on host ELSA under an interactive logon (it needs
the operator's credential store for git push).

The 16 mechanisms the charter names, in brief (code paths in the dossier):
- Roster discovery: roles/ directories on every origin ref, plus the registry.
- Role discovery: registry declared_role / observed_role, model-authored once, now static; the drift check
  (ACHILLES-10) is not built.
- Activity inference: S0-S6 rule cascade over commits, comms and ew.
- Engine mapping: registry.
- Last-task mapping: newest of QUEUE / CENSUS / prompt / delegation. The source ledgers are hand-written by
  Aporia.
- Experiment mapping: a verdict-word regex over commit subjects. "62 experiments in 24 h" includes
  rulings, harvest deliverables and a method freeze.
- Git mapping: attribution rules A1-A6 (7% unattributed). Path-majority attribution credited Archaeon's
  2c8c81bbb to Mnemosyne.
- Canonical state: a state cascade with rule id and every declared state, its source and its age.
- HTML generation: render.py, with client-side freshness.
- Email integration: the census block in send_brief_email. The loop is closed: the 04:15Z email carried
  census 03:46Z, and its email_dispatched row is in agora.intelligence_outputs.
- Scheduling: ELSA schtasks every 6 h.
- Incremental crawl: cursors in build.py.
- Provenance: source, source_time, observed_at and confidence per field; run receipts with code_sha,
  base_sha and host.
- Conflict detection: flags for declared-state, host and ownership conflicts. Resolution is "freshest
  wins".
- Stale-task detection: flags.
- Failure reporting: a park record, and a comms post only on census failure or park.

Checked against git for 14 seats: 10 right, 4 wrong or weak [IMPL]:
- Mnemosyne ACTIVE: wrong, because of the path-majority attribution above.
- Atlas PARKED: wrong. The parser took the first matching STATUS line, which describes the index loop,
  over "state: READY".
- Pronoia DORMANT: wrong. Its heartbeat reads health='productive', with a last success today.
- Metis RETIRED: the census read "SEASON 1 CLOSED" as retirement; no ruling was found.

[INFER] The park-after-4-non-productive-runs guard cannot fire: the census's own push and the M4 loop's
4-hourly auto-commits reset it, and the census counts its own commits as Achilles work (run.py:171-172).

Accounting signals it already produces (observational): per-seat last commit, last comms post/sync,
declared vs observed state, host, MWO adoption, and the email receipt join. It does not produce tokens,
session minutes, dollars or per-experiment cost. No mechanism anywhere in the territory records inference
cost (section 7).

## 4. Coordination history (detail: seats/Aporia.md, Cyclops.md, Agora.md; timeline)

    regime                          dates (2026)          authority / transport                       how it ended
    April Agora                     04-15 .. 04-29        Redis streams, coordinator session, 60 s     Redis under WSL would not stay up; Redis
                                                          heartbeats, 5-min death rule                 retired 06-24 (PgRedis drop-in, 0 rows today)
    no fleet channel                04-29 .. 09-11        seat files, commits, operator                comms revived 09-11
    Era-1 baseline (Pronoia)        03 .. 04              serial subprocess chain, date-named files,   pipeline archived as a bundle; pronoia.py
                                                          regex health audit (0/37 HEALTHY)            deleted 04-23 (3b3c74bc0)
    comms + base role (D-23..27)    09-11 ..              Postgres queue; presence from sync (D-25)    live
    SI peer stewards                09-25 15:29Z ..       Aporia (M1) + Cyclops (M2), 20-30 min ticks  operator freeze 09-26 13:04Z; sign-off release 13:16Z
    direct operator control         09-26 ..              operator + ChatGPT -> seat -> operator       MWO model 09-28
    Master Work Orders              09-28 21:48 ..        operator + ChatGPT author, publisher seat    live (MWO-0004)
    CWO fleet scheduling            09-30 04:18 ..        Aporia queue/dispatch + heartbeats           live (CWO-C); coordinator diverted to harvest

What worked [IMPL]:
- comms transport. It has been stable since 09-11 (code unchanged for 20 days) and holds 1,239 hashed
  messages with per-instance receipts. It also served as this crawl's measurement instrument.
- Verbatim, hashed capture of every operator directive (358 MANIFESTs).
- The two-commit MWO publication protocol. It ran cleanly three times, with SHAs and broadcast ids in
  PUBLICATIONS.md.
- One closed measure-and-fix loop: the MWO-0002 census found that boot files never pointed at CURRENT.md,
  the FP-001 cold-start probe followed, and MWO-0004 R4 made a one-line base-role repair (17e25e67b).
  FP-001 is labelled PASS although its own caveat says discovery came through same-day traces [CORR].
- CWO-C dispatches closed with receipts the same day (comms/ew hang repair 2c8c81bbb; Windows Fabric P0
  c97fe81a5, SHAs as cited in Aporia's journal [HIST]).
- prepost_check.py, the blind-lane guard, ships with real-message negative controls.

What generated inference-heavy administrative churn [IMPL unless tagged]:
- Regime churn: five regimes in six days, all set by the operator, several reversing the last within
  hours:
  - MWO-0001 gave Cyclops sole custody of the work orders; MWO-0002 moved it to Aporia about 5 h later.
  - MWO-0004 partly reversed MWO-0003 28 minutes after MWO-0003 was published.
  - MWO-0002 and base-role 2a H ("do not build a smart global scheduler") were followed about 20 h later
    by a CWO making Aporia "fleet scheduler".
  - CWO auto-promotion was removed after about 5 h.
  - In total: 7 orders, 16,858 words, in about 40 h.
- Heartbeat resurrection: retired 09-14 ("a heartbeat label is a meaning that expired", D-25), then
  reimposed by CWO-B/C on 09-30 as model-written messages.
  - 86 heartbeat-subject messages followed in about 25 h.
  - 14 of them were hourly "no change" reports from one seat, sent to a coordinator that had been assigned
    an inference harvest.
  - Four liveness mechanisms now coexist.
- Rising coordination share: on a subject-word heuristic [INFER-grade], coordination-only comms subjects
  went 23% -> 20% -> 28% -> 40% of weekly traffic (W37 -> W40).
  - kind=report is 849 of 1,239 messages, and broadcasts rose 10 -> 16 -> 26 -> 45 per week.
- State bookkeeping: 432 commits touched WORK_STATE.json since 09-27. 158 commits on 09-28..10-01 changed
  only WORK_STATE, journal or STATUS files.
  - QUEUE.json disagreed with WORK_STATE for 10 of 13 seats (Cyclops F7).
  - Five seats had hand-written timestamps in the future (Cyclops F3).
- Steward-era serial approvals: during the steward window the two stewards sent 94 of 162 messages
  (17 rulings, 11 acks).
  - The deepest thread in comms is a 27-message, depth-21 exchange on prereg rules.
  - The steward-era release guard kept requiring an Aporia release after that authority was abolished.
- Coordinator role churn: Aporia went through 14 role states in 5.5 months, 9 of them between 09-25 and
  09-30. Its seat file records none of the latest; the live role exists only in WORK_STATE.state_reason.
- Operator as transport: the base role makes the operator a phone relay of ASCII blocks between seats and
  external models.
  - [REPORTED by Aphrodite] 177 operator prompts 09-11..09-30.
  - Days with zero operator prompts had about 2 active seats. comms volume agrees in shape: 2 messages on
    09-15, and none on 09-20 or 09-22.
- Decision record fragmentation: the decisions register DECISIONS.md last changed 09-11. Later rulings live
  across prompts/, RULINGS.md and MWO/CWO texts. AGORA-01 is still unruled after 17 days [UNK whether it
  was ruled outside the repo].

## 5. Builders and toolsmiths (detail: seats/Hephaestus.md, Odysseus.md; build inventory in seats)

Shared libraries [IMPL; counts are files that mention the module, from git grep]:
- prometheus_math: 216 external importing files; 3,176 test functions.
- techne/lib: 72 external; 433 tests.
- prometheus.toolbox (Worlds Kernel, Bellerophon): 21 external; 231 tests. It has an IR, compile/execute/
  replay, receipt hash chain, and admission with "no approver".
- archaeon.workspace (D-23 guard): 38 external. 13 workspace-guard modules exist, and 5 reimplement it
  rather than import it.
- evidence_wiki.ew.db (identity-attested connector): in the connect path of comms, atlas, fabric, ludus and
  archaeon.
- prometheus_llm: the single model-call choke point; 8 external importers.
- RowWriter: used by primordial and Nestor.

Execution fabric [IMPL; Ixion re-verified the host split]:
- Agent Fabric v0.2 (Odysseus) is live and frozen except for defect repair. It holds 347 tasks, 373
  attempts, 40 leases and 12 principals; 302 tasks completed and 36 were requeued automatically.
- Attempts ran only on ubu001 (337) and ubu002 (36), never on M1 or M2. Three workers were online and
  idle, with no task since 09-30 15:32Z.
- At least 8 queue/lease mechanisms coexist: fabric, Vivarium research queue, comms task_queue, SFE
  work_items, agora research_queue + gpu_reservations, primordial Redis leases + CPU token broker,
  archaeon file queues, host-file leases.

Broker/security:
- promexec: a root-owned sudo broker for model-proposed code (systemd DynamicUser/PrivateNetwork). It is
  NOT ENABLED; the round-2 install waits on the operator.
- The fabric claude-executor sandbox is live, with scoped tools, secret-path denial and rogit for git.
- The Cosmos holdout broker and the primordial CPU-token broker are capacity/sealing mechanisms, not
  security.
- The D2 firewall audit took 13 model rounds in about 2 days.

Deployment tooling:
- SFE verify_deploy.py checks that served code equals committed code, using LF-normalised hashes.
- DEPLOYED_BUILD.json records M1 (disabled) and M2 (production).
- [IMPL] The canonical checkout F:\prometheus is on a vivarium branch that lacks the deployment records
  main tracks. That is the hazard verify_deploy.py was written for.

Reusable experiment components [IMPL file-name census]: 42 *null* modules in 15 top-level directories, 31
*receipt*, 13 *freeze*, 9 *manifest*, 20 *ruler*, 10 *lease*. They are mostly per-seat, not shared.

Automation that already does work sessions spend inference on [IMPL]:
- xpol shape.py and knockout_ablation.py classify generated code mechanically.
- The closure gauntlet decides route classes, with controls passing.
- hephaestus refine.py routes work items by rule.
- handoff.py regenerates cold-start handoffs.
- STATE.json carries last_input/last_success freshness.
- The fabric worker runtime handles dispatch, babysitting and salvage [REPORTED S2: 126 coordination
  actions for 36 runs by hand vs 0.28 per run through the fabric].
- Claims C3-C6 in S2 reduce to grep/hash checks.
- TH-006 and odysseus brain check do cross-host reproducibility.
- The canary scan checks for leaks.
- toolbox admission makes slot decisions.

Hephaestus 1.0 forge [IMPL]:
- 6,661 ledger rows, mostly March (4,469), not May.
- 2,861 rows (43%) are api_call_failed, recorded as if they were tool outcomes.
- The forged tools are regex + zlib-NCD scorers (forge 340/366 zlib, forge_v7 65/65).
- The pass comparator (NCD 0.3925) scores below a constant-position decoy (0.4032).
- forge/tester.py FAIL_ABLATION fired 0 times in 203 verdicts.
- The 09-01 verdict "the generator is dead by measurement" therefore rests on a ruler below a decoy and an
  instrument with a 43% failure rate. Whether the generator is dead is not settled by this record [INFER].

## 6. Memory architecture (detail: seats/Mnemosyne.md "Memory architecture", Hermes.md)

There are 14 institutional memory stores [IMPL]: git journals and ledgers; WORK_STATE/STATUS files; the
ew schema (PEW); the atlas schema; comms; agora tables; the doctrine file aporia/doctrine/critical_
memories.md; the base-role constitution; prompt MANIFESTs; per-session Claude memory directories (156
M1-local feedback files); and others listed in the dossier.

How they relate:
- The curated "canonical empirical memory" (ew.experiments, 79 rows, all from 09-01..09-03; 78 of them by
  Mnemosyne or probes) is frozen. 143 of its 147 claims are model-extracted.
- The large, current layer came from deterministic readers: 32,938 campaign observations and 12,935
  fossil encounters, with line provenance.
- The doctrine file has not changed since 05-08 and is referenced by 118 files. Lessons now accrue in
  non-portable per-host memory.

Eight drift examples are documented with both sides cited. Examples:
- MONITORS says the brief producer has been DORMANT since 09-09, but it commits 6 times a day.
- Hermes's 09-11 row said the mailer had no record, while 369 dispatch rows existed.
- The evidence-wiki skill points at M1 localhost, but the service moved to M2 on 09-16.

The Evidence Wiki has been down since 09-23 [IMPL]. The M2 watchdog parked it and posted #542. Vivarium
reported it on 09-24 (#563). 14 messages to Mnemosyne are unread. The health endpoint answers on neither
host. The detection is deterministic; the response requires a model session that nobody scheduled.

Security residue (named, values not copied): evidence_wiki/config.json carries committed credentials
(tracker R-1 OPEN); mnemosyne/STATE.md carries plaintext DB credentials; agora/README.md names a retired
Redis host and default credentials.

## 7. The inference boundary today (detail: inference_dependency_map.md)

The six crawls classified 143 institutional functions, counted under the first class named in each row:
80 INFERENCE_FREE, 16 ASSISTED_PLAUSIBLY_DETERMINISTIC, 14 OCCASIONAL_JUDGMENT, 32 MODEL_MEDIATED, 1
other. The shape that recurs across all six:

- The machinery is deterministic but its TRIGGER is a model session or the operator. Atlas passes, PEW
  campaign ingestion, integration batteries, MWO publication, the census registry refresh and alarm
  response are all "run by hand". About 93 disabled one-shot launchers on M1 point into session
  scratchpads.
- Detection is deterministic and response is model-mediated. Atlas signals (192 OPEN), census flags, the
  PEW watchdog park (#542), fleet_status.py and Alethelia's rules exist, but nothing acts on their output
  without a session.
- Content is model-written over structured inputs. Heartbeats, reports, QUEUE/CENSUS ledgers,
  WORK_STATE/STATUS and MONITORS rows restate information that git, comms and receipts already hold.
- There is one completed migration: the operator brief. An LLM cascade confabulated ("14 agents pending"
  from 43 UNKNOWNs) and leaked chain-of-thought into emails for weeks. Since af9b4d9c9 (08-18) the brief
  is deterministic by default and takes 0.1-0.5 s. The record shows no loss, though no A/B test exists
  [UNK what was lost].
- The irreducible model/human work today: hypothesis generation, naming rival explanations, framing an
  experiment, interpreting results, authoring control documents, writing new index adapters, and hard
  gates.

No mechanism records inference cost per seat, per function or per message. comms.agents holds a
self-declared model string with 6 spellings for Opus variants. Every cost statement about inference in
this package is therefore [UNK].

## 8. Historical research-program archaeology (detail: seats/Metis.md, Atalanta.md, Pronoia.md, Alethelia.md)

Retired is not irrelevant. In these seats, the strongest surviving asset is a deterministic instrument
with controls, not the model-mediated function the seat was built for. Each seat was retired or archived
by a process that tested code uniqueness or bundle membership, not its hypothesis.

Metis is three architectures under one name:
- 1a, March, literature-compression analyst. One model and one prompt, with a stale self-description as
  its relevance ruler. 6 of 8 briefs recommended the program's own pending tasks, and rewording defeated
  its hash-based novelty check. It was never measured against a decision it changed. False-negative risk:
  moderate.
- 1b, May to now, fleet reporter. It moved from LLM to deterministic. This is the clearest in-house
  evidence that a model layer over structured state could be removed.
- 1c, September, composition specimen (compose.py, 13 adversarial tests). It is a model-free experiment-
  selection kernel: it groups evidence by shared upstream sources, vetoes suspect instruments, and picks
  the cheapest discriminator that partitions the remaining explanations.
  - [REPORTED] Across 5 dead episodes, N agreeing items collapsed to one independent reason each.
    Cheaper discriminators were available in 4 of 5.
  - It ran one retrospective season with a single encoder and a positive control added afterwards.
  - Its own receipt says it does not generate rivals ("someone still has to name BASE_RATE_PRIORS").
  - No retirement ruling exists; the census read "CLOSED" as RETIRED. False-negative risk: HIGH. It would
    have died of scale, not of a negative result.

Atalanta. [INTENT] The hypothesis was that, in evolving primitive-routing DAGs (Apollo), high-reuse
primitives and repeatedly re-derived length-2/3 composite chains mark the vocabulary the substrate should
name. That would be an automated vocabulary-growth loop and a candidate lens for concept formation.
- [IMPL] It was never tested. All 354 ticks ended UPSTREAM_NOT_FOUND because the consumer guessed three
  output directories Apollo never wrote (daemon.py:63-67). It raised 305 alarms with no recipient; Ixion's
  sub-crawler re-verified the 305.
- Retirement tested whether the code was unique, not the hypothesis. The retirement text itself says the
  premise was "never tested". Apollo has been suspended since 09-01 [HIST].
- Risks the record already names: survivor frequency confounds with selection pressure and base rates.
- What it did produce is governance: base rule 10 (bounded no-op loops), the C1/C2/C3 loop-risk
  predicate, "emission is not productivity", and the still-unruled D-28 (a producer must declare where it
  writes).
- False-negative risk: HIGH.

Pronoia. Era 1 (March) was a serial subprocess chain with date-named file handoff and a regex audit over
its children's stdout. The audit reported 0 of 37 HEALTHY: it graded self-reports, never fired its zero-
output check, and had no knowledge-growth rule. Era 2's M4 loop reproduced Era 1's defect: 'online' while
work failed 09-12..09-17. A work-aware heartbeat followed (productive_liveness.py, PRON-03), and the loop
is live and productive today.

Alethelia. Built as the antibody to 1b's confabulation: every field carries the query that produced it,
UNKNOWN is a value, calm requires zero fired and zero indeterminate rules, and decoys must be caught. Its 7
controls are reported passing (not re-run). It has had no host since 09-11.

Cross-cutting [INFER]: Metis's correlated-evidence collapse and Atalanta's guessed producer are both
failures of declared dependency structure. One is in evidence, the other in data flow.

## 9. Cross-crawler contradictions and Ixion corrections

- Operator brief: inference-free by default, not LLM-generated. The memory crawler said otherwise; Ixion
  corrected it in place, marked [CORR -- Ixion verification 2026-10-01].
- PrometheusMachineProbeM1: the fleet crawler says retired, the hist crawler says live. Ixion checked:
  enabled, firing every 5 min, failing (file not found). Last M1 data 2026-05-30. Unresolved 20 days after
  a handover. Both rows are kept with an ixion_note.
- fleet_status.py: the fleet crawler says unknown, the coord crawler says live. It was built and tested,
  and used by two seats on 09-30, but has no schedule and no committed run receipts.
- Emails sent: the fleet crawler counted 485 email_dispatched rows; the memory crawler counted 820. The
  difference is 335 pronoia_email_dispatched rows. Both counts are right for their filter.
- Census labels vs evidence: Mnemosyne ACTIVE (false), Atlas PARKED (false), Pronoia DORMANT (false),
  Metis RETIRED (unsupported).
- MONITORS.md says the portfolio producer has been DORMANT since 09-09. The DB shows it resumed on 09-11
  and has run 6 times a day since. Its currency line is 09-18.
- Atlas registry: "NPE not on origin/main" is stale since b10161316.
- Odysseus: ABOUT.md says 73 tests; the crawler counts 59 test functions and a Cyclops receipt says 71
  passed. On Windows the working copy of fabric/promexec/broker.py hashes c3544f92 (CRLF) against the
  committed pin 3cf32a64, so a Windows checkout would fail the broker's own pin check.
- Hephaestus: the operator's TODO (09-20, "paused") and the seat's STATUS (09-25, "boundary certifier",
  default HEPH-32) are both on main and neither cites the other.
- Metis status: census RETIRED vs Metis STATUS "awaiting operator"; no ruling found.

## 10. What this crawl did not establish

- Anything only on M2, M3 or M4: Atlas-M2's local evidence, the PEW M2 service, backups and watchdog
  logs, M4's mailer host and scheduled tasks, ELSA's census log and local state.
- Holdout-adjacent material, excluded by rule: the D2 audit bodies, and the nestor/d2v10..13 refs the
  Atlas NPE harvester auto-selected on 09-30. Whether those refs carry sealed material is [UNK] and flagged
  for the owners.
- Every [REPORTED] scientific number. None was re-run: +11/+32 pp, S2/S3, Alethelia 7/7, Atalanta 9/9,
  Metis P-1..P-5.
- Token, dollar and session-time costs, for which no records exist.
- Whether operator rulings exist outside the repository (AGORA-01, Metis retirement, HERMES-XL-1 mailer
  ownership).
- Ixion verified nine claims itself, not every row. The 398 artifact rows and 76 engine rows carry the
  sub-crawlers' tags as written, except where noted.

----------------------------------------------------------------------------------------------------------------

## A. What Prometheus already automates well

- [IMPL] Provenance capture:
  - prompt MANIFESTs (358, LF sha256)
  - MWO publication blob verification
  - Atlas harvest_run + fact_evidence pointers to commit/blob/line
  - PEW write-path gates (idempotency keys, content-addressed ids, vocabulary refusal, 6,077 write_log rows
    with reasons)
  - store-identity attestation, fail-closed, shared by comms, atlas, fabric, ludus and archaeon
  - SFE verify_deploy.py
  - the D-23 canonical-checkout guard
- [IMPL] Parsing machine ledgers into indexed rows: Atlas counts matched source in every sample, and the PEW
  campaign reader produced 32,938 rows with line provenance.
- [IMPL] Message transport: comms has been stable for 20 days, with hashes, per-instance receipts and a
  task queue (149 rows, 114 done).
- [IMPL] Durable task execution with DB-enforced invariants: Fabric guarantees one live attempt per task,
  one lease per resource, idempotent submit and fencing.
- [IMPL] A deterministic fleet census with field-level provenance, and closed-loop email delivery
  verification.
- [IMPL] An operator brief that has been deterministic since 08-18, delivered about 6 times a day since May
  with an event row per send. The M4 loop has a watchdog and kill switch.
- [IMPL] Instrument controls where they exist: Hephaestus gauntlet, toolbox mutation ledger, Achilles cheat
  controls, Alethelia decoy law, prepost_check real-message negatives, xpol floors computed before any
  model call.
- [IMPL] Backup and restore qualification (pg_dump + scratch restore + table compare). The M1 tasks are
  disabled; the M2 status is unobservable from M1.

## B. Where model inference is currently wasted

Measured where possible; the costs themselves are [UNK] because nothing records them.
- [IMPL] Clock-driven heartbeat reports with unchanged content: 86 in about 25 h, 14 of them hourly
  "no change" from one seat to an unavailable coordinator. Achilles derives the same fields
  deterministically every 6 h.
- [IMPL] Hand-maintained state ledgers that a join could compute:
  - QUEUE.json and CENSUS.json are written by Aporia sessions and drift from WORK_STATE for 10 of 13 seats.
  - 158 commits in 4 days changed only state, journal or STATUS files.
  - MONITORS rows drift from DB facts.
- [IMPL] Control-document churn: 7 orders and 16,858 words in about 40 h, several superseding each other
  within hours. Every one is broadcast to and re-read by every live session.
- [IMPL] Instrument failures paid for as outcomes: 2,861 of 6,661 forge rows are api_call_failed. Model
  arms ran on saturated memory instruments (PEW V1-V3, all arms 4/4).
- [IMPL/HIST] The LLM brief narrated a frozen snapshot 6 times a day for about 8 weeks and confabulated,
  until it was made opt-in.
- [HIST] Index staleness pushed work up into inference: the 09-30 harvest used about 14 model roles to
  rebuild cross-engine state from prose digests.
- [REPORTED] Run babysitting outside the fabric: 126 coordination actions for 36 runs, against 0.28 per run
  through it.
- [IMPL] Repeated archaeology of retired seats by each re-seated session. One such pass asserted a fact a
  single COUNT refutes.
- [IMPL] Serial steward approvals: a 27-message, depth-21 thread on prereg rules, plus 13 model audit
  rounds of one firewall in about 2 days.

## C. Existing machinery suitable for deterministic Phase 3 operation

Observational inventory of code that exists, runs or ran, and needs no model per execution:
- Index: atlas/ harvesters + comb rules + report lag + MANIFEST-gated producer import (cosmos.py, with
  cheat controls); harvest_run/fact_evidence schema.
- Evidence store: ew schema + campaign reader + projections with rebuild-digest equality; ew/db.py
  identity-attested connector; pew_backup/pew_restore_verify.
- Execution: Fabric store/worker/script executor/leases/events; prometheus.toolbox
  IR/compile/execute/replay/admission/receipts; RowWriter.
- Fleet observability: achilles/census, attribution and state rules, field provenance, incremental
  cursors, run receipts; fleet_status.py checks (STALE_MWO, STALE_UPDATE, NO_QUEUE, IDLE_HOLD,
  IDLE_WORKERS); Alethelia query-carrying report with tri-state rules; productive_liveness.py ladder;
  null_bound.py rule-10 reference.
- Event logs already populated: comms.messages/receipts/task_queue (kinds, reply_to, instances);
  agora.intelligence_outputs (18,733 stage events); fabric.events; atlas.harvest_run.
- Decision kernels: Metis compose.py (cheapest partitioning discriminator, instrument vetoes); hephaestus
  refine/rank/handoff state machine; closure gauntlet; xpol floors/shape/report.
- Guards and verifiers: comms/manifest.py; prepost_check.py; archaeon.workspace; verify_deploy.py; TH-006
  pack; Hermes failure-signature convergence (sha256 over at-failure observables); hermes.py per-section
  hash dedup.
- Fully specified algorithms not yet scripted: the P/R publication protocol; Cyclops' five reconciliation
  predicates; MWO-0004 R2 envelope numbers.

## D. Institutional failure modes

Each is cited in the dossiers.
- Detectors without responders: alarms route to a seat that has no running session (#542 unanswered for
  8 days), and 192 Atlas signals have never been consumed.
- Guards that cannot fire:
  - forge FAIL_ABLATION, 0 of 203 verdicts
  - the Achilles park rule, reset by its own pushes
  - the Era-1 zero-output check, 0 of 37
  - Atlas field_conflict, 0 rows
  - the self-test's scheduled-task regex, which misses FoundryAPI and nestor_z80atlas
- Grading self-reports instead of properties, repeatedly in one lineage: the Era-1 stdout audit, the
  filename-date health check, and 'online' heartbeats while work failed.
- Label tables outliving their writers:
  - 32 of 36 agora heartbeat rows still read 'online' after 7+ days
  - MONITORS states, registry notes, seat charters (Aporia, Cyclops) and ops/README "PILOT ONLY" all
    describe roles or states that have since changed
- Coverage lag: the index is only as current as its last hand-written adapter (8.6 days; 5 engines
  unregistered).
- Class-word inflation and verdict override at the index layer: "completed" becomes POSITIVE, and the
  machine candidate replaces the author's verdict.
- Coordination regime churn, plus authority residue in code (the release guard outlived the steward
  authority).
- Reinvention instead of sharing: 8+ queue/lease mechanisms, 13 workspace guards, 42 null modules.
- A consumer inventing its producer's interface (Atalanta), with D-28 unruled.
- Host handover stranding services: PEW on M1 went dark at handover, the machine probes have been dead
  since 05-30 and are still firing, and the canonical checkout sits on a branch without the deploy records.
- Single points:
  - comms and the reporting DB on M1
  - the census on ELSA under an interactive logon
  - mailer credentials only on M4
  - Fabric workers only on two laptops
  - the operator as the transport for cross-model review
- Credentials in tracked files (three named locations, values not copied).
- Name reuse across eras hiding lineage: Metis, Pronoia and Aletheia/Alethelia, and Theseus as recorded by
  that seat.

## E. Evidence/provenance strengths and weaknesses

Strengths [IMPL]:
- Row-level pointers to commit, blob and line, in Atlas and in PEW campaign_observations.
- harvester VERSION on every row.
- EXPECTED:<host> distinguishes "not visible from here" from "absent" (6,101 rows).
- Verbatim author conclusions are kept beside machine dispositions.
- Prompts and orders are hashed at issuance.
- Census fields carry source, time and confidence.
- Alethelia ties every field to a query.
- Negative results are first-class in PEW: 76 of 133 evidence rows are negative.
- Frozen results are never overwritten, and calibration ledgers record seats' own wrong calls.

Weaknesses:
- [IMPL] Outcome classes at the index layer are not trustworthy (section 2, reliability class 2), and the primitive layer is
  inherited labels.
- [IMPL] Attribution errors: PEW submitted_by='Mnemosyne' for 73 experiments attributed to 18 agents;
  census path-majority credit; 31% of commits unattributed in Atlas.
- [IMPL] Model-authored ledgers (catalogue, theory, proposals, 143 extracted claims) sit beside parsed
  ledgers with no row-level reliability class beyond a method field.
- [IMPL] Receipts that do not pin a clean tree: Hephaestus workspace receipts all say dirty=true, and PEW
  migration 015 was applied from a dirty tree.
- Batteries write the receipts they are judged by. Test runs mutate tracked receipts in the canonical
  checkout.
- [IMPL] Self-declared fields: comms message kind, the model id at boot, and WORK_STATE state (an
  uncontrolled vocabulary with no validator; future timestamps).
- [IMPL] Missing failure detail: agora error fields are empty on 37 consecutive failed pushes, and success
  means "SMTP accepted".
- [IMPL] Host-local refs (e.g. nestor/d2v13) recorded as sources resolve only while that host keeps them.
  M2/M4/ELSA state is unobservable from M1.
- [HIST] 26 honest-era forge tools were never committed; only their ledger rows survive.

## F. Historical infrastructure worth preserving

- The atlas schema and its 13 hash-locked migrations: the only cross-engine relational record of SFE
  C1-C6, DEEP FRONTIER, NPE graphworld r1-r8 + CW01, Vivarium and Cosmos C0, up to 09-22. Also its
  calibration ledger (12 self-corrections) and SIBLINGS rules.
- The ew write-path invariants, the campaign reader and its 32,938 provenance-carrying rows; comms/
  identity.py and the environment registry.
- The comms tables as the complete inter-seat record since 09-11, and agora.messages (the 196 April rows)
  with the Agora archaeology mapping each April function to its successor.
- agora.intelligence_outputs: the per-stage history of the reporting loop since May, and the
  atalanta_* lifecycle.
- The Era-1 failure corpus (37 audits, 5 health reports, the deleted pronoia.py blob 96f674b2), as a
  labelled negative-control set for any future monitor.
- The forge corpus (ledger.jsonl, forge*/ trees, scrap, verdicts), the counterfeit museum, the wall
  taxonomy and the closure results. Both xpol and the Gravity Pilot depend on them.
- Instruments with controls: compose.py, productive_liveness.py, null_bound.py, alethelia.py,
  prepost_check.py, Achilles census tests, fabric DEFECTS.md and fabric.events.
- Protocol texts: the two-commit publication protocol and PUBLICATIONS.md; the MWO-0002 census rubric
  C1-C9 and the cold-start probe design; Cyclops' observability audit.
- The Deep Research queue: 370 unfired prompts with tier, consumer and template fields.
- The metis_portfolio deterministic-first switch with its CoT-leak guard: the documented model-to-code
  migration.

## G. Questions the Phase 3 designers must answer

These are questions the evidence raises, not recommendations.
1. Which store is primary for "what was tried and what happened": git ledgers, PEW campaign_observations,
   Atlas experiments, or the frozen ew.experiments? They overlap and disagree in coverage today.
2. Who or what triggers deterministic machinery that today waits for a session? That covers index passes,
   adapter authoring for new engines, ingestion, alarm response, and the census registry refresh.
3. When a deterministic monitor fires and the owning seat has no session, what responds? (#542 went 8
   days unanswered.)
4. How is inference cost to be measured at all? No token, session or dollar record exists per seat,
   function or message, and model ids are self-declared.
5. Which of the four coexisting liveness mechanisms is authoritative, and should liveness be change-
   triggered rather than clock-triggered?
6. Should outcome class at the index layer derive from the author's RECORD verdict, the machine
   candidate, or both? Should execution state (completed/PASS of infrastructure) be a separate axis from
   scientific outcome?
7. Should model-authored ledgers (catalogue, theory, proposals, extracted claims) carry a row-level
   reliability class distinct from parsed ledgers?
8. Which of the 8+ queue/lease mechanisms remain authoritative? Is Fabric, whose workers have only ever
   been two laptops, expected to carry heavy science? What is the execution boundary for model-proposed
   code while promexec is not enabled?
9. Who may change the control model, with what minimum dwell between regime changes, and is there a
   single decisions register again?
10. Should WORK_STATE get a schema, an enum and a future-timestamp check before anything is scheduled from
    it? Should P/R publication be a script, and should CWOs follow it?
11. Which reusable components (nulls, gates, receipts, workspace guards, leases) become shared libraries?
12. Are the following false negatives to be re-tested before they are cited as negatives?
    - Hephaestus 1.0: its ruler scores below a constant decoy, and 43% of its rows are API failures.
    - Atalanta: the hypothesis was never fed data.
    - Metis compose.py: 5 retrospective episodes and one encoder.
    - PEW V1-V3: the instruments saturated.
    - Era-1 literature intake: never measured against a decision.
    - The machine probes: possibly a path defect.
13. What is the sustainable operator relay load, given idle fleet days when the operator is away?
14. Ownership gaps: the M4 loop and mailer (HERMES-XL-1), machine probes, agora tables, Alethelia
    (ALET-04), AGORA-01, Metis status, D-28 producer declaration.
15. Do the nestor/d2v10..13 refs the Atlas NPE harvester auto-selected carry sealed holdout material?
    (Not opened; owners must check.)
