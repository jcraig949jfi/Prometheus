# Seat dossier: Atlas

- Seat: Atlas (experiment-history index on M1, later "research-policy layer")
- Crawler label: atlas (Ixion sub-crawler)
- Date: 2026-10-01 (date -u at start of crawl: Thu Oct 1 09:35:45 UTC 2026)
- Base SHA read: bed05507a (origin/main, 2026-10-01 05:34 -0400), worktree F:/Prometheus-worktrees/ixion-phase3
- Fully read: atlas/__main__.py, db.py, classify.py, comb.py, policy.py, harvest/__init__.py, harvest/theory.py,
  header + ref logic of harvest/npe.py, headers of harvest/frontier_runs_m2.py and harvest/local_files.py,
  sql/views.sql, registry.json (hosts/engines), roles/Atlas/{RESPONSIBILITIES,MODEL,SOURCES,SIBLINGS,STATUS,
  BACKLOG_H0H5}.md, calibration/LEDGER.md, loop/TICK.md, all six journals, the charter (verbatim + ASCII),
  catalog/README.md, theory/*.jsonl (fields sampled), inference_harvest_2026-09-30/INFERENCE_HARVEST_HANDOFF.md.
- Sampled (headers / grep / first sections): charter addendum (482 lines, structure only), promotion directive (first
  20 lines), inference-harvest directive (first 80 lines), ATLAS_BURIED_SIGNALS, ATLAS_ONTOLOGY_GAPS_VNEXT (s0),
  ATLAS_OPERATOR_FRONTIER (head), workers/digests/atlas_index_and_history.md (grep), reports/REPORT_2026-09-30.txt
  (s1-s3), atlas/tests/test_atlas.py (head), report.py (collision + lag functions).
- Live Postgres (M1 prometheus_fire, schema atlas): read-only session (set_session(readonly=True)); every table
  counted, columns + timestamp ranges listed, ~25 targeted SELECTs. No writes.
- NOT read: harvest/archaeon_campaigns.py, frontier.py, cosmos.py, vivarium.py, pew.py, commits.py, catalog.py,
  proposals.py bodies (only headers/ORDER); sql/001-013 bodies (schema read from the live DB instead);
  the 1,131-line prior-art raid directive; workers/ digests other than the Atlas one; xfamily responses;
  the nestor/d2v1x-2026-09-29 branches (possible holdout lineage -- deliberately not opened); anything on M2.

Tags: [IMPL] read code/data myself; [INTENT] charter/plan; [HIST] journal says; [REPORTED] numeric result as
reported; [CORR] correction/contradiction; [INFER] code-inferred; [UNK] unknown.

---------------------------------------------------------------------------------------------------------

## 1 Charter and role history

- 2026-09-18 20:49 seat created, base role adopted, charter PENDING (f7283bc2e). Name clash noted at creation:
  "atlas" already used by Nyx ATLAS passes (nyx/atlas/), the ludus_atlas Postgres schema and a cancelled Ludus
  crawler cron [HIST] roles/Atlas/journal/2026-09-18.md item 4; ludus_atlas schema exists on M1 [IMPL] (pg_namespace).
- 2026-09-19 operator charter, committed verbatim alone (4fb8c7fc2): shadow SFE + NPE "from a scientific
  perspective", two-tier relational index on M1 Postgres, POINTERS not copies, machine is first-class, lineage of
  reruns, do not disturb engines, build re-runnable TOOLS so the data can be "recombed" for (a) missed science,
  (b) weak signals, (c) rerun opportunities [INTENT] roles/Atlas/prompts/2026-09-19_charter/OPERATOR_CHARTER_verbatim.md;
  itemised R1-R11 in CHARTER.md.
- 2026-09-19 charter ADDENDUM (cbe1d149d): separate WHAT RAN / WHAT WAS OBSERVED / WHAT SOMEONE CONCLUDED; tier 1
  master index + tier 2 facts; source pointers first-class; filenames never identity; host + engine_instance; machine
  merge [INTENT] prompts/2026-09-19_charter_addendum/OPERATOR_ADDENDUM_verbatim.md:19-229.
- 2026-09-19 ALife survey request -> external ecosystem catalogue (98972f55a) [HIST].
- 2026-09-21 directive 8 "prior-art science raid" -> 34-experiment proposal queue + Engine Five ladder (2c7a19adb) [HIST].
- 2026-09-24 PROMOTION (f8df65681): "Old Atlas: what have we done ... Upgraded Atlas: what should we believe ...
  what experiments should become more or less valuable". The operator text says this is "a better fit than creating a
  separate Metis seat" [INTENT] prompts/2026-09-24_promotion/OPERATOR_9_promotion_verbatim.md:3. Atlas becomes
  "memory AND research-policy layer" [INTENT] RESPONSIBILITIES.md s0.
- 2026-09-25 operator rulings: one pass then PARK; REPORTS ONLY (no directives posted to seats); keep inferring hosts,
  no interface requests [HIST] journal/2026-09-25.md.
- 2026-09-26 bounded repair: Cosmos adapter only (7190591f4) [HIST]+[IMPL] harvest_run 289-291.
- 2026-09-30 bounded "inference harvest" (unparked until 2026-10-01 05:00 ET): corpus repair + cross-engine
  synthesis by subagents (ea07398dc .. d95cffcc8) [HIST]+[IMPL] commits.
- Current: READY, loop PARKED, no watcher [HIST] roles/Atlas/STATUS.md:5-12.

## 2 Systems maintained

1. The `atlas` schema on M1 Postgres prometheus_fire: 34 base tables + 8 views [IMPL] information_schema (this crawl).
2. The `atlas` Python package: CLI (migrate | harvest | comb | policy | report | roadmap | status), 14 harvesters,
   comb rules R01-R13, policy scorer/portfolio [IMPL] atlas/__main__.py, atlas/harvest/__init__.py:6-14.
3. Committed text ledgers that feed the DB: roles/Atlas/catalog/ECOSYSTEMS.jsonl (365 lines),
   roles/Atlas/theory/{PROPOSITIONS(10),PRIMITIVES(20),BLIND_SPOTS(7)}.jsonl, roles/Atlas/proposals/*/EXPERIMENTS.jsonl
   (12 + 34) [IMPL] wc -l.
4. Generated reports: reports/REPORT_2026-09-{19,25,26,30}.txt, ROADMAP_2026-09-{24,25}.txt, PACKET/EXTERNAL_REVIEW
   2026-09-19 [IMPL] ls.
5. A session-only index loop (AtlasIndexLoop), PARKED since 2026-09-19 [IMPL] roles/base-role/MONITORS.md:88.
6. The inference-harvest document set (prose; model-produced) [IMPL] roles/Atlas/inference_harvest_2026-09-30/.

## 3 Actual implementation paths

- atlas/__main__.py (108 lines): argparse CLI; refuses canonical checkout via archaeon.workspace.assert_not_canonical;
  per-host harvester allow-list from registry "harvester_hosts" [IMPL] atlas/__main__.py:43-63.
- atlas/db.py (333): connects through evidence_wiki/ew/db.py connect() (store identity guard); migrations applied
  once each with sha256 refusal on edit; Harvest context manager writes atlas.harvest_run; generic upsert with MERGE
  RULE (scalar COALESCE, arrays union, jsonb merge) and a WATCH list writing field_conflict; advisory locks
  7146001-7146003 [IMPL] atlas/db.py:27-29, 52, 63-104, 107-160, 163-238, 288-317.
- atlas/classify.py (186): regex-only commit classifier, host-from-tag/text, status_class() disposition regex ladder,
  science_class() for prose verdicts. Docstring: "No model in this path" [IMPL] atlas/classify.py:1-3, 106-126, 159-186.
- atlas/harvest/common.py (354): key builders, Batch, flush, prune (host-scoped), validity_from [IMPL] grep of defs.
- Harvesters (ORDER): reference, commits, archaeon_campaigns, frontier, npe, vivarium, pew, local_files,
  frontier_runs_m2 (M2), catalog, proposals, theory, cosmos [IMPL] atlas/harvest/__init__.py:6-14.
- atlas/comb.py (185): 13 SQL rules -> atlas.signal; re-run deletes the rule's OPEN rows and re-inserts [IMPL] comb.py:27-185.
- atlas/policy.py (263): score() and portfolio(); weights hard-coded in WEIGHTS dict [IMPL] policy.py:23-26.
- atlas/report.py (298): build(), status(), roadmap(), detect_collisions(), lag section [IMPL] report.py:38-64, 286-295.
- SQL: 13 migrations 001-013 + views.sql (re-applied each migrate) [IMPL] ls atlas/sql; atlas.schema_migrations 13 rows.
- Tests: atlas/tests/{test_atlas,test_cosmos,test_frontier4,test_frontier_runs_m2}.py, 58 test functions; index tests
  read the LIVE schema and roll back writes [IMPL] grep -c "def test_"; test_atlas.py:1-5.

## 4 Architecture

engines/seats write files, commits, SQLite ledgers, Postgres rows -> read-only collectors (git cat-file/ls-tree,
stat + small reads, SQLite mode=ro&immutable=1 on idle ledgers, SELECT in read-only transactions) -> atlas.* on M1 ->
comb rules (SQL) -> signals; theory ledgers + axis rules -> primitive_use/combination; policy.py -> scores/portfolio;
report.py -> text reports [INTENT] MODEL.md s1-s9, [IMPL] code as cited above. Identity keys are text built from native
ids (campaign '<program>/<native>', experiment '<campaign_key>:<native>', attempt '#', segment '@') [IMPL]
common.py:26-41; MODEL.md s3. Every row carries last_harvest_id -> harvest_run (host, seat, harvester version, source
ref/sha) [IMPL] db.py:107-131. No engine depends on Atlas [INTENT] MODEL.md s8; no non-Atlas code imports `atlas`
found by git grep at bed05507a (only docs/journals reference roles/Atlas) [IMPL].

## 5 Data stores

Live row counts (SELECT count(*), 2026-10-01 ~09:40Z) [IMPL]:

    experiment 2,053   attempt 1,742   segment 3,582   campaign 53   idea 54   defect 221
    fact 33,054        fact_evidence 33,055             conclusion 483  edge 5,494
    source 13,025      source_link 13,382               git_commit 7,419  entity_commit 117  seat_instance 95
    engine 15  engine_instance 136  host 4  harvest_run 136  schema_migrations 13  vocab 137
    signal 192 (all OPEN)  identity_collision 30 (all OPEN)  field_conflict 0
    ecosystem 365  ecosystem_reference 870
    proposition 10  proposition_evidence 7  primitive 20  primitive_use 4,249  combination 190
    experiment_score 92 (outcome NULL in all)  policy_version 2  portfolio_update 10  blind_spot 7
    schema size 639 MB (pg_total_relation_size sum)

Committed text stores listed in s2. Git refs read by collectors: origin/*, refs/heads (incl. host-local nestor/*).

## 6 APIs/interfaces

- CLI only: `python -m atlas migrate|harvest <name>|all|comb|policy score|portfolio --horizon|report|roadmap|status`
  [IMPL] __main__.py:24-40. No HTTP service, no comms posting from code.
- SQL views/functions for readers: v_manifest, v_edge_dangling, v_local_only, v_coverage, v_shape_inventory,
  v_measurement_names, v_theory_frontier, v_writers, descendants(type,key), ancestors(type,key) [IMPL] views.sql; live
  information_schema.
- Inbound: any seat may ask Atlas to index an export (Cosmos did: roles/Cosmos/prompts/2026-09-23_atlas_harvest/) [HIST].
- Known consumers: Bellerophon atlas_bee froze a 6-experiment selection from read-only SELECTs on atlas
  (roles/Bellerophon/atlas_bee/SELECTION_FROZEN.json:5, 2026-09-19); Artemis/Odysseus cite Atlas ledger lines as
  sources (roles/Artemis/backlog/harvest/D1_program.md:438-501) [IMPL] git grep.

## 7 Scheduling model

- No scheduled task: `schtasks /query` on M1 shows no Atlas task (only \nestor_z80atlas, a Nestor launcher)
  [IMPL] this crawl.
- AtlasIndexLoop = Claude Code session /loop, ~60 min, bound 6 non-productive ticks, accountable Atlas-M2; ran 2
  productive ticks 2026-09-19 then PARKED by operator [IMPL] MONITORS.md:88; loop/TICK.md; [HIST] journal/2026-09-19.md.
- All later harvests were manual, operator-triggered passes (09-24, 09-25, 09-26, 09-30) [IMPL] harvest_run dates.
- Intended cadence MICRO ~10 / STRATEGY ~100 / THEORY ~1000 newly indexed experiments; event-driven version is backlog
  ATLAS-43 (not built) [INTENT] RESPONSIBILITIES.md s4; BACKLOG_H0H5.md ATLAS-43.

## 8 State machine

- harvest_run.status RUNNING(implicit)->DONE|FAILED [IMPL] db.py:117-146. 3 FAILED runs ever (npe x2 on 09-19:
  timestamp type mismatch, NaN json; reference x1 on 09-24: FK home_host 'unknown') [IMPL] harvest_run.notes.
- signal.status OPEN (comb only rewrites OPEN; anything moved off OPEN by a human is kept) -- no signal has ever left
  OPEN (192/192) [IMPL].
- portfolio_update ISSUED -> SUPERSEDED on next update at same horizon; ACKED never used (0 rows) [IMPL] policy.py:243-244; live counts.
- conclusion.status STANDING 479 / UNRESOLVED 3 / SUPERSEDED_INTERPRETATION 1 [IMPL].
- experiment_score: prediction -> outcome -> theory_delta (outcome never written; 0/92) [IMPL].
- Seat-level: PENDING -> chartered -> loop PARKED -> promoted -> REPORTS ONLY -> READY [HIST] STATUS.md.

## 9 Communication channels

comms (M1 Postgres) messages cited in journals: #499-#512 with Atlas-M2, #517 #523 #531 #556 FYIs, #544/#558/#562
Cosmos, #557 Nyx, #577 pass announcement, #735 Archaeon producer semantics [HIST] journals. Atlas posts no directives
to seats since 2026-09-25 ruling [HIST]. Prompts and outgoing message bodies committed under roles/Atlas/prompts/ with
MANIFESTs [IMPL] ls.

## 10 Failure recovery

- A harvester failing does not stop others; its harvest_run says FAILED with the exception text [IMPL] __main__.py:58-60; db.py:141-146.
- Migrations refuse if an applied file changed (hash check) [IMPL] db.py:92-96.
- Upsert never erases; prune only removes rows the same harvester on the same host wrote and did not re-emit [IMPL]
  db.py:163-171 comment; [INTENT] MODEL.md s5 (prune code in common.py:281 not read in full).
- Loss tracking for host-local files: present=false + dated file.missing fact (local_files/4) [IMPL] local_files.py:24-30 docstring.
- Resume records for reboots (RESUME_2026-09-25.md) [IMPL].

## 11 Persistence

Postgres schema atlas (derived; claimed rebuildable from sources + ledgers) plus committed text ledgers in
roles/Atlas/ [INTENT] MODEL.md s9 last bullet. Rebuildability not demonstrated end-to-end [UNK]. Host-local evidence
(M2 runs/, SFE ledgers) is only pointed to; if it disappears the index keeps the pointer with present=false [INFER].

## 12 Provenance

Strong at row level: every row -> harvest_run (harvester+version, host, seat, instance_tag, atlas_sha, source_ref,
source_sha) [IMPL] db.py:117-124. Facts -> fact_evidence -> source (uri, repo, ref, commit_sha, blob_sha, path,
line/byte range, visibility) [IMPL] live columns. Edges carry basis DECLARED/INFERRED/ATLAS_DERIVED + method +
confidence [IMPL]. Weak at semantic level: see "Provenance and reliability classes" below.

## 13 Resource usage

- Full M1 pass 2026-09-30 (reference..comb, 16 harvest_runs) wall 18:15:35 -> 18:17:01 = ~86 s [IMPL] harvest_run
  305-320 (note: harvest_run timing covers the DB flush, not the parse, for npe-style harvesters -- npe.py:89-91).
- DB footprint 639 MB (inflated history: frontier/3 once wrote 299,991 echo facts, later collapsed) [IMPL]+[HIST].
- No GPU, no compute lease [HIST] INFERENCE_HARVEST_HANDOFF.md s3 "Compute: none leased".

## 14 Model/inference dependency

- Collectors, classifier, comb, policy math, reports: no model call in code [IMPL] classify.py:1-3; no LLM import in atlas/.
- Model-authored INPUTS that the deterministic code then loads: ECOSYSTEMS.jsonl (six web-survey subagents),
  PROPOSITIONS/PRIMITIVES/BLIND_SPOTS.jsonl (Atlas session), proposal queues (Atlas session), axis_rules inside
  PRIMITIVES.jsonl [HIST] journal/2026-09-19.md "Six web-survey agents"; journal/2026-09-24.md item 2.
- Hard-coded prose directives inside policy.portfolio() (STRATEGY "REDUCE ... P-heredity-bootstrap-barrier", THEORY
  "DEPRIORITIZE ... raw population scaling") are emitted regardless of data [IMPL] policy.py:204-210, 228-233.
- Inference harvest: entirely model-mediated (Claude subagents + NVIDIA NIM kimi-k3 / deepseek-v4.1) [IMPL]
  workers/xfamily/query.py, query_log.jsonl; [HIST] handoff s3, s7.

## 15 Human dependency

Every pass since 09-19 was operator-triggered; the loop requires operator word to resume; scope changes (promotion,
raid, inference harvest, repairs) all arrived as operator directives [HIST] STATUS.md, journals. Interface requests to
seats forbidden without operator authority (ATLAS-26) [INTENT] RESPONSIBILITIES.md s6.

## 16 Major outputs

The populated schema (s5); ecosystem catalogue (365 systems / 870 refs); 46 indexed proposals (XE-01..12, raid A-I
incl. RA-1..RA-5); theory ledgers; REPORT/ROADMAP text files; inference-harvest set (F1-F8 findings, 16
contradictions, ~50 buried signals, 12+5 frontier directions) [IMPL] files; findings themselves [REPORTED].

## 17 Known failures (own calibration + this crawl)

- Own ledger (12 rows): prose minted into keys; frontier family-as-parent produced 207 dangling edges; R02/R13 first
  pass fired on schema fields (14/14); 'G-R16' misread as round 16; INSTANCES vs SIBLINGS identity error; policy/1
  novelty 0.000 for all 46; three identical horizons; quiet window misread as quiet engines; untested-vs-unmeasurable
  conflation [HIST] calibration/LEDGER.md.
- frontier/3 indexed 299,991 identical BLOCKED_BY_SUPPRESSION events as separate CONCLUDED facts (92% of CONCLUDED);
  held 5 days; fixed by frontier/4 + migration 013 on 09-30 (facts 333,044 -> 33,054; sources 313,015 -> 13,025)
  [HIST] journal/2026-09-25.md, handoff s3; current counts consistent [IMPL].
- This crawl: see "Provenance and reliability classes" for record-vs-source disagreements.

## 18 Pivots

index (09-19) -> +catalogue (09-19) -> +proposal queue (09-21) -> research-policy layer absorbing the Metis role
(09-24) -> PARKED/REPORTS ONLY (09-25) -> bounded adapter repair (09-26) -> model-mediated inference harvest over
digests rather than index rows (09-30) [HIST]. INSTANCES.md (one seat, two instances) deleted and replaced by
SIBLINGS.md within 3 minutes after Atlas-M2 objected (b8b6f8e59) [IMPL] git log --diff-filter=D.

## 19 Journals/TODOs/backlogs

journal/2026-09-{18,19,21,24,25,26}.md (no 09-30 journal file; 09-30 work recorded in STATUS WORK_STATE and the
harvest handoff) [IMPL] ls. BACKLOG_H0H5.md: ATLAS-04..43 open items incl. ATLAS-39 (5 unmeasured primitives),
ATLAS-40 (close scoring loop), ATLAS-34/35/36 (prereqs for reanalysis RA-2/4/5), ATLAS-28/29/30 (log scale) [IMPL].
Inference harvest handoff s6 lists adapters for PTE, BEE, Aether, Ensorain, Hecate, Tyche and NPE dirs after 09-22 as
Atlas-internal follow-ups [HIST].

## 20 Historical relevance to current Prometheus

Atlas is the only cross-engine, provenance-carrying relational record of experiments in the repo. It is current to
2026-09-22 for modelled experiment activity and to 2026-09-30 22:15Z for commit metadata [IMPL]. Its research-policy
tables exist but have never closed a loop (0 outcomes) [IMPL]. Its 09-30 findings are the most recent cross-engine
synthesis but are model-mediated over digests [HIST].

## 21 Inference-dependency classification of this seat's functions

| function | class | evidence |
|---|---|---|
| git commit harvest + seat/lane/id classification | INFERENCE_FREE | classify.py:13-71 regex only |
| receipt/ledger parsing into experiment/attempt/segment | INFERENCE_FREE | npe.py, archaeon_campaigns.py (versioned harvesters) |
| disposition -> atlas_class mapping | INFERENCE_FREE (but semantically lossy) | classify.py:106-126 |
| prose verdict reading (RECORD.md DISPOSITION) | ASSISTED_PLAUSIBLY_DETERMINISTIC | classify.science_class regex, confidence LOW/MEDIUM |
| host inference from tags/paths/IPs | INFERENCE_FREE | classify.py:80-101 |
| loss tracking of host-local files | INFERENCE_FREE | local_files.py docstring |
| comb weak-signal rules R01-R13 | INFERENCE_FREE | comb.py:27-161 |
| identity collision detection | INFERENCE_FREE | report.py:38-64 |
| index coverage lag | INFERENCE_FREE | report.py:286-295; policy.py:146-158 |
| writing adapters for a new engine | OCCASIONAL_JUDGMENT | MODEL.md s7; every adapter hand-written in session |
| ecosystem catalogue construction | MODEL_MEDIATED | journal 09-19 "Six web-survey agents" |
| propositions / confidence labels / blind spots | MODEL_MEDIATED | theory/*.jsonl authored in session 09-24 |
| primitive axis rules | OCCASIONAL_JUDGMENT | PRIMITIVES.jsonl axis_rules, then applied deterministically |
| primitive_use + combination derivation | INFERENCE_FREE | theory.py:69-149 |
| proposal scoring (policy/2) | INFERENCE_FREE given model-authored fields | policy.py:42-114 (reads extract.information_gain text label etc.) |
| portfolio directives | INFERENCE_FREE with hard-coded prose | policy.py:117-262 |
| cross-engine synthesis / buried signals / frontier | MODEL_MEDIATED | inference_harvest_2026-09-30/ |

## 22 False-negative / false-positive watch

False-negative candidates:
- Combination/primitive analysis looked "null" partly by construction: experiment-level primitive_use is inherited
  per campaign from 4 hand-labelled Prometheus ecosystem rows, so POS and NEG groups carry identical tuples; vivarium
  (1,242) gets none [IMPL] theory.py:96-115; live: 1,266/1,266 frontier, 1,420/1,420 npe, 265/265 sfe rows say
  "inherited"; 0 vivarium rows. Atlas itself says so [HIST] ATLAS_ONTOLOGY_GAPS_VNEXT.md:14-22. Any conclusion that
  "primitive X does not matter" from this table is a ruler defect, not evidence.
- R10 VISITED_ONCE fires on free-text world/organism strings ("any x any", JSON shape blobs), so genuinely rare
  regions are buried in noise [IMPL] live signal rows.
- Policy scoring never received an outcome; any "low score" proposal (RA-1, RA-3, RA-5 not in ROADMAP top-15 per
  Odysseus prompt_A2.md:842) is unrated by evidence, not rejected [IMPL] 0/92 outcome.
- ATLAS-36 (reanalysis pipeline) never built, so RA-2..RA-5 never ran [IMPL] no code; [HIST] backlog.
False-positive candidates:
- atlas_class POSITIVE: 649/723 are Vivarium queue "completed" (2 of them "completed (error)") [IMPL]; NPE graphworld
  PASS (incl. infrastructure checks) and CW01 "COMPLETE" also map to POSITIVE [IMPL] classify.py:113.
- R03 sign reversal pools any measurement whose name ends in "effect" across unrelated experiments (range -0.29..75) [IMPL].
- Proposition P-measurement-before-mechanism rated STRONG from defect class counts without a comparison set [IMPL]
  PROPOSITIONS.jsonl confidence_basis.

---------------------------------------------------------------------------------------------------------

## Atlas deep reconstruction

Each item: EXISTS AS code / data (rows) / prose only / not at all.

### Indexed engines
- Code + data. atlas.engine 15 rows; 5 with experiments: vivarium 1,242, archaeon.frontier 422, npe 276, sfe 57,
  cosmos 10 (+46 proposals with engine NULL) [IMPL] live. Registered but never harvested: bellerophon.toolbox,
  herakles.evca, proteus, ludus, harmonia.rulers, crius, ensorain, ananke (notes "not yet harvested"/"no runs
  indexed"); serendipity.foundry.d IGNORED by operator ruling [IMPL] atlas.engine.notes. Not registered at all:
  PTE (Ananke), BEE (Bellerophon), Aether, Hecate, Tyche, z80atlas campaign [HIST] handoff s4/s6; [IMPL] absent from
  engine table. archaeon.campaign is a registered RUNNER but its experiments are keyed under engine_id 'sfe' [IMPL].
- Stale registry text: npe "code only on nestor/* branches (not origin/main) as of 2026-09-19" -- primordial/ reached
  main via merge b10161316 (2026-09-22) [CORR] atlas.engine.notes vs git log --first-parent.

### Experiment schema
- Code + data. atlas.experiment 38 columns incl. world/organism/pressure/search_family, ruler, seeds, budget_summary,
  reported_disposition, reported_conclusion, atlas_class (+confidence, +method), validity_state,
  unresolved_interpretation, prereg/design/config digests, hosts, extract/inferred jsonb [IMPL] information_schema.
- Fill rates (count non-null): reported_disposition 2,036/2,053; question 429; world_family 58; organism_family 172;
  pressure_family 0; search_family 1; ruler 0 [IMPL] per-engine counts. validity_state UNKNOWN 1,947, PARTIAL_EVIDENCE
  96, VALID 10 [IMPL]. So "ruler" and "pressure" axes exist in schema only.
- atlas_class 722 UNKNOWN (35%) [IMPL] matches REPORT_2026-09-30 s1.

### Attempt schema
- Code + data. atlas.attempt 1,742 rows: attempt_no, of_record, reported_status, validity_state, rerun_reason,
  started/finished/duration, host_id + host_basis, instance_tag, operator_seat, engine_instance_key, branch,
  commit_sha, code/config digest, dirty, worktree_path, budget, seen_from_hosts [IMPL]. started_at range 2026-09-05
  .. 2026-09-19; finished_at to 2026-09-22 [IMPL]. Segments 3,582 rows, started_at/finished_at NULL in all [IMPL].
- Cross-check: 158 NPE graphworld attempts = 158 distinct exp_id across primordial/ledger/[A-Z].jsonl at bed05507a;
  130 frontier attempts = 130 "RUN" events in archaeon/frontier/registry/EVENTS.jsonl [IMPL] this crawl.

### Evidence pointers
- Code + data. atlas.source 13,025 (visibility: EXPECTED:M2 6,101; GIT_REMOTE 2,860; PG:M1 2,739; FS:M1 710;
  GIT_LOCAL:M1 275; FS:M2 244; EXPECTED:? 96); source_link 13,382; fact_evidence 33,055 [IMPL]. Pointer = uri + ref
  + commit_sha + blob_sha + path + line/byte range [IMPL]. Spot checks resolved: primordial/ledger/C.jsonl line 24
  engineering.wall_s 306.87 matches; cw01-arch4/P-I04/RESULT.json elapsed_s 477.5 at 6c14b17f89 matches [IMPL].
- Caveat: many pointers record ref = a host-local branch (e.g. nestor/d2v13-2026-09-29); resolution depends on the
  commit_sha surviving (6c14b17f89 is on main) [IMPL].

### Facts
- Code + data. 33,054 facts: RAN 8,719 / OBSERVED 22,655 / CONCLUDED 1,680 [REPORTED] REPORT_2026-09-30 s1, total
  [IMPL]. Largest blocks: cosmos phenomenon_verdict 8,840; npe measurement 6,516; local_files telemetry_availability
  5,356 (ATLAS_DERIVED); npe campaign_decision 1,330; frontier_runs_m2 detector_firing 1,195 [IMPL] group by.
  Facts are flattened json keys (name like "result.elapsed_s", "prereg.f_test") [IMPL] samples.

### Lineage / cross-engine edges
- Code + data. 5,494 edges. Cosmos-internal DEFORMATION_OF/COORD_PRESERVING/CONTROL_OF 3,096; ecosystem RELATED_TO
  967; experiment->idea TESTS 569; AFFECTED_BY 225; ANALOGUE_OF (proposal->ecosystem) 124; DESCENDANT_OF 202 [IMPL].
  Basis: DECLARED dominant; INFERRED 170 (119 frontier family-membership DESCENDANT_OF, 26 RERUN_OF, 17
  AFFECTED_BY...) [IMPL].
- Cross-engine experiment->experiment edges: 115 (archaeon.frontier->sfe DEFORMATION_OF 99; sfe->npe SUPERSEDES 5;
  npe->sfe CONTINUATION_OF 1; proposal->sfe TRANSPLANT_OF 10) [IMPL]. R09 surfaces 21 cross-engine lineage signals [IMPL].
  Spot check: C5-01 SUPERSEDES P-C09 matches PERTURBATIONS.jsonl superseded_by "C5-01 (...)" [IMPL]; the edge reason
  CROSS_SUBSTRATE_TRANSPLANT is not obviously derivable from P-C09 type "one-axis-walk" [UNK].
- Dangling endpoints: 3 (attempt->attempt) [IMPL] v_edge_dangling flags.

### Weak-signal detectors
- Code + data. comb.py R01-R13 (SQL), 192 signals all OPEN: R11 calibration specimens 40, R10 visited-once 35, R06
  null-with-rich-telemetry 33, R09 cross-engine lineage 21, R01 weak disposition 19, R08 defect clusters 18, R04
  conclusion changed across attempts 17, R07 3, R12 data gap 2, R02/R03/R05/R13 1 each [IMPL]. No signal has a
  recorded human disposition [IMPL]. Eligibility counts (ATLAS-18) not built [IMPL] backlog. Several rules are loose
  (R03, R10 -- see s22).

### Theory graph
- Code + data (small) + prose. proposition 10 (1 STRONG, 4 MODERATE, 2 WEAK, 3 UNTESTED), proposition_evidence 7
  rows, v_theory_frontier view [IMPL]. Source ledger roles/Atlas/theory/PROPOSITIONS.jsonl authored by Atlas on 09-24;
  first_stated_at / last_reviewed_at NULL for all 10 [IMPL]. Two confidence bases cite the operator as the source
  ("stated by the operator", "asserted by the operator") [IMPL] PROPOSITIONS.jsonl.
- Evidence row P-task-competence-not-mechanism SUPPORTS(HIGH) archaeon.campaign/cmp4:C4-07, while the index itself
  holds a SUPERSEDED_INTERPRETATION conclusion for C4-07's mechanism reading (superseded by C5-08) [IMPL]; the
  confidence_basis text does mention the supersession, so this is a scoping subtlety rather than an error [INFER].

### Primitive ontology
- Code + data + prose. 20 primitives; 15 AXIS_RULE, 5 UNMEASURED (partial_heredity, write_authority, temporal_gating,
  reproductive_closure, error_correction) [IMPL]. primitive_use 4,249 rows, all basis ATLAS_DERIVED, all state
  PRESENT; ecosystem rows 1,298 (348 ecosystems), experiment rows 2,951 all "inherited from <eco> via campaign"
  [IMPL]. combination 190 pairs: TESTED 89, UNEXPLORED 85, SUGGESTED_BY_EVIDENCE 16; status OPEN, routed_to NULL in
  all [IMPL]. Atlas's own vNext attack (prose) proposes new primitives (initialization_regime,
  encoding_accessibility, use_coupling, executor_referent) and ruler-side fields [HIST] handoff s1.

### External ecosystem catalogue
- Data + prose. 365 ecosystems (361 external + 4 prometheus) and 870 references (VERIFIED 667, SEARCH_RESULT 195,
  UNVERIFIED 8; group by url_status) [IMPL]. Built by six web-survey subagents; url_status VERIFIED means
  "fetched/API-resolved" by the surveyor [HIST] catalog/README.md:9, journal 09-19. Loaded deterministically by
  harvest catalog/1 [IMPL] harvest_run.
- Record-vs-record disagreement: the ecosystem.verification string disagrees with the attached reference rows for 16
  ecosystems (e.g. tierra "5/7 links VERIFIED" vs 6 reference rows; stringmol "4/10" vs 12 rows of which 5 VERIFIED)
  [IMPL]. Artemis records Stringmol/Squirm3 repo URLs as UNVERIFIED while Atlas marks them VERIFIED [CORR]
  roles/Artemis/backlog/prior_art/PA_origin_of_replication.md:238 vs atlas.ecosystem_reference.
- README totals (352/4, 834 refs) are 09-19 currency; DB now 365/870 after the 09-21 top-up [IMPL].

### World x organism x pressure catalogue
- Data for the EXTERNAL catalogue only: ecosystem.world_kind / organism_repr / pressure_kinds filled; densest cells
  documented [IMPL] catalog/README.md "Densest world x organism cells". For Prometheus experiments the axes are
  essentially empty (pressure_family 0/2,053; world+organism both set on 5 experiments, 39 ideas) [IMPL]. Prometheus
  engines appear as 4 hand-labelled ecosystem rows (origin=prometheus) [IMPL].

### Historical coverage gaps
- Data + prose. Not modelled: everything after 2026-09-22 15:07 (-0400) in experiment space; Nestor C9 / S-series /
  W1 / P2 / ARC3; PTE, BEE, Aether, Hecate, Ensorain, Tyche, Crius, Harmonia rulers, Proteus, Herakles, Ludus,
  Bellerophon toolbox runs; NPE QD cells; archaeon/wse git ledgers (4 PEW-only campaigns with 1 placeholder
  experiment each); M2-local frontier receipts beyond the 58 seen on 09-19 (Atlas-M2 measured 129 on 09-25) [IMPL]
  engine table + REPORT s3; [HIST] Atlas-M2 STATUS.md. EXPECTED:M2 pointers 6,101 [IMPL]. Commits: 2,297/7,419 (31%)
  have no seat attributed by the classifier [IMPL]. Vivarium is complete (1,242 = viv.research_experiment_queue 1,242;
  queue last created 2026-09-17) [IMPL].

### Lag (computed this crawl)
- Newest modelled experiment activity: 2026-09-22 15:07:51 -0400 [IMPL] max(last_activity_at).
- Newest commit in indexed areas at bed05507a: roles/Nestor 2026-10-01 05:09:22 (797d338ff); roles/Nestor/campaigns/
  cw01-2026-09-17 2026-10-01 05:05:49 (8abdab01a, a merge of an e05 replica lane); archaeon/ 2026-09-29 09:09:53;
  roles/Cosmos 2026-10-01 02:38:42; archaeon/frontier/registry last 2026-09-22 17:01; vivarium/ 2026-09-17 [IMPL] git log -1.
- Lag = 8.58 days (Nestor), 6.75 days (archaeon), 8.48 days (Cosmos); Atlas's own metric (newest indexed commit -
  newest modelled activity) = 8.13 days [IMPL] computed. Commits since 2026-09-22 not modelled: 275 under
  roles/Nestor, 57 under archaeon [IMPL] git log --since.
- Index age: last harvest 2026-09-30 22:17Z, 11.3 h before this crawl; git_commit newest 2026-09-30 18:15 (-0400),
  11.3 h behind HEAD [IMPL].
- History of the lag: 4.9 d (09-24), 2.7 d (09-25), 8.1 d (09-30) [HIST] STATUS.md; journals.

### Known identity collisions
- Data. identity_collision 30 rows, all namespace fact.CONTRADICTORY: RECEIPT.campaign says "cmp2" for cmp3/cmp4/cmp5
  experiments (runner reuse); membership taken from the directory [IMPL]; confirmed in archaeon/campaign{3,4,5}/*/
  RECEIPT.json campaign="cmp2" (C3-SFE-09, C4-07, C5-03, C5-05) [IMPL]. field_conflict: 0 rows ever -- the watch
  mechanism has never fired (M2 harvests have been tiny) [IMPL].
- Name-level collisions around "atlas" (not in the DB): nyx/atlas/ (Nyx fossil census, 2026-09-14, 65c319ef7),
  ludus_atlas schema + ludus/atlas_of_worlds, prometheus/z80atlas (Bellerophon "Z80 x Atlas" harness, whose "Atlas
  transplant axes" are a factor family), Odysseus noting the Z80 entry ECOSYSTEMS.jsonl:78 is an outside paper not
  z80atlas (roles/Odysseus/fabric_pilot/s2/results/C9_tsk-9639a05e419a_final.md:10) [IMPL].
- Seat identity collision: Atlas vs Atlas-M2 (INSTANCES.md deleted, SIBLINGS.md) [IMPL] b8b6f8e59.

### Buried-signal work
- Prose only. ATLAS_BURIED_SIGNALS_AND_RESIDUALS.md: ~50 observations separated from the interpretation that buried
  them, ranked A..., each cross-referenced against Tyche's residual catalogue (122 entries) [HIST] file s0. Built from
  subagent digests, not SQL [HIST] handoff s4 "The synthesis ran over the record through digests". Deterministic
  analogue: comb R06/R01 (s "Weak-signal detectors") [IMPL].

### Research-policy layer
- Code + data, never closed. policy.py score(): 9-feature vector with fixed WEIGHTS (information gain 0.25, theory
  impact 0.25, causal 0.15, novelty 0.10, cross-engine 0.10, ... cost -0.20); features read model-written proposal
  fields (information_gain label, compute_class, controls, target_engine string) [IMPL] policy.py:23-28, 70-101.
  92 score rows (46 x 2 policy versions), outcome/theory_delta NULL in all [IMPL]. portfolio_update 10 rows (3 ISSUED);
  REPORTS ONLY ruling means none were posted to seats [HIST]. Some directives are constant text in code [IMPL]
  policy.py:204-233. blind_spot 7 (5 COMMISSIONED as proposals, 2 OPEN) [IMPL].

### Reanalysis plans
- Prose + proposal rows; no code. RA-1 frontier-queue-as-curriculum (READY_FOR_DESIGN), RA-2 learned descriptors
  over GraphWorld/CW01 (NEEDS_DONOR), RA-3 evaluator-exploitation census (READY_FOR_DESIGN), RA-4 Crius PARTS
  takeovers (IDEA), RA-5 rediscovery rate (IDEA) [IMPL] proposals/2026-09-21_prior_art_raid/EXPERIMENTS.jsonl.
  Prerequisites ATLAS-34/35/36 not built [IMPL] backlog; no harvester/pipeline for them in atlas/ [IMPL] ls.
  Inference-harvest FR-1..FR-12 add more (prose, "NOT a queue") [HIST].

---------------------------------------------------------------------------------------------------------

## Provenance and reliability classes of Atlas records

Collector -> source map (from ORDER, harvest_run.source_ref and code headers) [IMPL]:

| record family | collector | source | reliability class (crawler's assessment) |
|---|---|---|---|
| host, engine | reference | atlas/registry.json (hand-edited) | HAND-CURATED; can go stale (npe note stale since 09-22) |
| git_commit, seat_instance | commits | git refs since 2026-08-25 | PARSED-FROM-GIT; seat attribution by regex, 31% unattributed |
| SFE campaign/experiment/attempt/segment, prereg/receipt facts | archaeon_campaigns | archaeon/campaign*/ PREREG/RECEIPT/ATTEMPTS json at origin/main | PARSED-FROM-LEDGER (high for numbers; disposition = machine candidate) |
| SFE conclusions | archaeon_campaigns | RECORD.md DISPOSITION paragraphs, READOUT.md | PARSED-FROM-PROSE (verbatim kept; class by regex) |
| frontier ideas/transformations/RUN attempts | frontier | archaeon/frontier/registry/*.jsonl | PARSED-FROM-LEDGER; DESCENDANT_OF by family-membership rule = INFERRED |
| frontier receipts/chunks on M2 | frontier_runs_m2 (Atlas-M2) | M2 git-ignored runs/ | PARSED-FROM-HOST-FILES (one pass, 09-19) |
| NPE graphworld + CW01 | npe | primordial/ledger/*.jsonl, CW01 CAMPAIGN_STATE/RESULT/loop/*.jsonl on newest 4 nestor refs | PARSED-FROM-LEDGER; superseded_by edges = ids PARSED-FROM-PROSE |
| vivarium experiments | vivarium | viv.research_experiment_queue / execution_attempt (SELECT) | PARSED-FROM-DB (executor state, not science) |
| PEW pointers | pew | ew.campaign_observations / ew.experiments (SELECT) | POINTER-ONLY |
| host-local files, telemetry_availability facts | local_files | stat of registry roots | ATLAS_DERIVED from file metadata |
| ecosystems + references | catalog | roles/Atlas/catalog/ECOSYSTEMS.jsonl | LLM-EXTRACTED (web-survey agents) then loaded |
| proposals (kind=proposal) | proposals | roles/Atlas/proposals/*/EXPERIMENTS.jsonl | LLM-AUTHORED (Atlas) |
| propositions, primitives, blind spots | theory | roles/Atlas/theory/*.jsonl | LLM-AUTHORED; confidence labels are judgments |
| primitive_use, combination | theory | rule over catalogue axes, inherited per campaign | ATLAS_DERIVED from LLM-labelled axes |
| scores, portfolio | policy | proposal fields + fixed weights + constant text | ATLAS_DERIVED; predictions never scored |
| cosmos stores | cosmos | roles/Cosmos/campaigns/atlas_export_c0 (MANIFEST sha256 verified, fail-closed) | PARSED-FROM-EXPORT (producer-curated) |
| signals, collisions | comb / report | SQL over the above | ATLAS_DERIVED |

Sampled records checked against source (this crawl, 14 checks):

1. Vivarium count: atlas 1,242 = viv.research_experiment_queue 1,242 (649 completed / 96 failed / 492 cancelled / 5
   queued) -- AGREES on counts [IMPL]. DISAGREES in meaning: 649 "completed" become atlas_class POSITIVE (incl. 2
   "completed (error)"), 649 of all 723 POSITIVE rows [IMPL]. Method label says "completion, not a scientific
   disposition" but the class word is POSITIVE.
2. NPE graphworld: 158 attempts = 158 distinct receipt exp_ids; rounds r1,r2,r4..r8 (+3 'R16' unassigned) -- AGREES [IMPL].
3. C-R4-01-nk-cp-metered-rent-gpu: receipt status FAIL -> atlas FAILED. Agrees literally; but NPE "FAIL" is a claim
   verdict, while Atlas FAILED also covers crashes ("CRASH|ERROR|ABORT") -- semantic merge [IMPL] classify.py:108.
4. D-R6-3-skip-odd-held64-coverage: NULL -> NULL -- AGREES [IMPL].
5. B-R2-1-int4-linear-nibble-w3-train8: PASS -> POSITIVE -- agrees with the classifier rule [IMPL].
6. archaeon.campaign/cmp3:C3-SFE-09: CAPABLE_NEGATIVE in receipt disposition_candidate and RECORD.md:104 -> NEGATIVE;
   identity collision for RECEIPT.campaign="cmp2" recorded -- AGREES [IMPL].
7. archaeon.campaign/cmp5:C5-03: experiment.atlas_class WEAK_POSITIVE (from receipt disposition_candidate: n_treatment 1,
   n_control 1, effect 0.0, battery 0/0/0) while the author's RECORD.md:116 says "DISPOSITION: REPRESENTATION_QUALIFIED
   (machine candidate WEAK_POSITIVE)" -- MANIFEST DISAGREES with the author verdict; the conclusion table holds both
   [IMPL]. R01 lists it as a weak signal [IMPL].
8. archaeon.campaign/cmp4:C4-07: atlas_class INCONCLUSIVE (machine candidate) vs RECORD.md:71 "DISPOSITION:
   REPRESENTATION_BLOCKED" -- DISAGREES at manifest level; conclusions hold both plus a SUPERSEDED_INTERPRETATION
   row [IMPL].
9. archaeon.campaign/cmp5:C5-05: UNDERPOWERED -> INCONCLUSIVE, matches RECORD.md:130 -- AGREES [IMPL].
10. nestor.cw01 e01 and e03: CAMPAIGN_STATE.json and RESULT.json say disposition "COMPLETE"; atlas_class POSITIVE --
    DISAGREES (completion promoted to a positive verdict) [IMPL] classify.py:113 maps COMPLETE -> POSITIVE.
11. nestor.cw01 e07: INCONCLUSIVE with reason text -- AGREES with CAMPAIGN_STATE [IMPL].
12. Facts: C.jsonl@24 wall_s 306.87 and P-I04 RESULT elapsed_s 477.5 -- AGREE [IMPL].
13. SFE campaign sizes cmp1..5 = 10/11/10/11/10 experiment dirs with PREREG/RECEIPT -- AGREE; frontier 130 RUN events
    = 130 attempts -- AGREE [IMPL].
14. atlas.engine 'npe' note "not origin/main" -- STALE since b10161316 (2026-09-22) [CORR]. Ecosystem verification
    strings disagree with reference rows for 16 systems [IMPL]. Commit 68aab291f (local canonical branch, subject
    "Hephaestus 2.0 Gravity Pilot ...") stored with seat NULL -- classifier miss [IMPL].

Summary: numeric facts and counts parsed from ledgers matched in every sampled case; the manifest-level CLASS word
(atlas_class / reported_disposition) is the least reliable field because it (a) takes the engine's machine
disposition_candidate over the author's later RECORD.md verdict, (b) maps execution states (completed, COMPLETE,
PASS of infrastructure checks) to POSITIVE. Atlas's own 09-30 digest already reports (b) [HIST]
workers/digests/atlas_index_and_history.md:176.

## Usefulness as substrate for a Phase 3 design corpus (observational)

Can support [IMPL unless tagged]:
- Enumerating what ran, where, on which commit, with which attempts and reruns, for SFE campaigns 1-6, the DEEP
  FRONTIER registry, NPE graphworld r1-r8 + CW01 (to 09-22), Vivarium queue, Cosmos C0 export.
- Resolving any fact back to a git blob/line or DB row (pointer schema), and listing what exists only on M2 (EXPECTED).
- Declared lineage graph (DECLARED edges) incl. a few cross-engine supersessions; descendants()/ancestors() walks.
- Separating author conclusions (verbatim, with line locator) from machine dispositions -- the data is there even
  where the manifest column picks the wrong one.
- Defect inventory (221; 129 SFE friction-ledger rows, 92 NPE) and identity-collision records.
- Commit metadata for 7,419 commits (2026-08-25 .. 2026-09-30) with seat/lane/ids for ~69%.
- A deterministic, versioned, tested ingestion pattern (harvest_run provenance, MERGE RULE, MANIFEST-gated import).

Cannot support (as is):
- Anything after 2026-09-22 in experiment space, or any engine without an adapter (most current lines: PTE, BEE,
  Aether, Hecate, Ensorain, Tyche, Nestor C9 and later).
- Science-vs-infrastructure outcome counts from atlas_class without re-deriving (POSITIVE inflation).
- Primitive/combination inference (inherited labels; 5 key primitives UNMEASURED).
- World x organism x pressure analysis over Prometheus's own experiments (axes empty).
- Ruler identity per experiment (ruler column empty; Atlas's vNext asks for ruler_id / ruler_can_return_opposite).
- Any learned prioritisation (no outcomes ever written).
- M2-local truth beyond one 09-19 pass.
- Truth: Atlas is a map built from producers' own records; it inherits their dispositions and adds its own labels.

## Atlas-M2 (summary; full dossier seats/Atlas-M2.md)

Separate seat on M2 (SPECTREX5), "not an instance of Atlas", same index on M1 via shared keys [IMPL]
roles/Atlas-M2/RESPONSIBILITIES.md s0. 8 harvest_runs, all on 2026-09-19 (reference, local_files x2, frontier_runs_m2
x2, comb x3) [IMPL] harvest_run seat='Atlas-M2'. Parked 2026-09-19 12:45Z; pre-reboot save 2026-09-25 (53e071604);
nothing since [IMPL] git log.

## NPE "only on M1-local branch" history

- 2026-09-19: SOURCES.md and npe.py docstring: primordial/ is NOT on origin/main; best ref is the M1-LOCAL branch
  nestor/sidequest-graphworld-2026-09-14 (origin copy stopped at b22a09b19); sources from commits not on any remote
  recorded GIT_LOCAL:M1 [IMPL] atlas/harvest/npe.py:3-6; SOURCES.md "NPE" section. harvest_run 7-10, 25, 35, 45, 105,
  206, 210, 212 carry notes "host-local ref" [IMPL].
- 2026-09-22 16:55: merge b10161316 "Merge nestor/sidequest-graphworld-2026-09-14 into main" brings primordial/ to
  main [IMPL]. Today origin/nestor/sidequest-graphworld-2026-09-14 == local (695a0425a) [IMPL].
- 2026-09-24: npe/5 auto-discovers refs (_npe_refs, newest 4 nestor refs carrying CW01 or primordial/ledger); harvests
  211/213 read the origin copies [IMPL] npe.py:43-64. It never considers origin/main (filter "nestor" in ref name) [IMPL].
- 2026-09-30: the 4 newest nestor refs were local nestor/d2v10..13-2026-09-29 (harvest 309-312, "host-local ref");
  GIT_LOCAL:M1 sources 275 remain [IMPL]. Whether those branches carry holdout material: [UNK] -- not opened by this
  crawler. Atlas's handoff states "Holdout D2 is sealed and was not read" [HIST] handoff s4.
- Branches: `git branch -a | grep -i atlas` -> local atlas/promotion-2026-09-24 (checked out elsewhere, merged) and
  remotes/origin/archaeon/z80atlas-postcampaign-2026-09-23 (not Atlas's) [IMPL]. Journal 09-25: "all seven atlas/*
  branches merged" [HIST].
