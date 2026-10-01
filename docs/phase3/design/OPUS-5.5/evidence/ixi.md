# Evidence digest: Ixion group (institution, inference boundary, timeline, infrastructure)

Reader: read-only evidence reader for EPIMETHEUS (OPUS-5.5), 2026-10-01.
Worktree: C:/prometheus-worktrees/epimetheus-phase3, HEAD c9b18697b. Ixion crawl base: bed05507a (27 commits
earlier; none of them touch ops/). Independence: nothing under docs/phase3/design/ except OPUS-5.5/, nothing under
roles/Dionysus/, no holdout or secret paths were opened. No DB queries were run by this reader; every DB number
below is Ixion's (or a sub-crawler's) SELECT and is tagged accordingly.

Tags: IMPL (read in code/data by me), INTENT, HIST, REPORTED (unverified result), CORR (correction), INFER, UNK.
"Ixion-SELECT" = a DB count Ixion itself re-ran (one of its 9 checks). "sub-SELECT" = a sub-crawler count Ixion did
not re-run.

----------------------------------------------------------------------------------------------------------------

## 0. Bottom line for the architect

1. The institution built a strong deterministic provenance and transport layer (hash-locked migrations, row ->
   commit/blob/line pointers, verbatim hashed directives, DB-enforced task invariants, a deterministic census).
   It did NOT build any infrastructure that records the four Phase 3 axes. Atlas has world/organism/pressure/ruler
   columns, but they are empty: pressure_family 0/2,053, ruler 0/2,053, world+organism both set on 5 rows
   (REPORTED, sub-SELECT; Atlas dossier s"Experiment schema"). The fossil record cannot be indexed retroactively
   on the axes Phase 3 cares about. A producer has to emit them at registration.
2. Every "dead" verdict in this territory came from an apparatus that could not have shown anything else:
   - Hephaestus 1.0 generator: the ruler sits below a constant decoy, and 43% of rows are instrument failures.
   - Atalanta: no datum ever reached the detector.
   - PEW V1-V3: saturated instruments.
   - Era-1 Pronoia health: the audit graded stdout.
   - Metis 1a: never measured against a decision.
   None of these is a true_negative.
3. The guards that should have caught this either could not fire or never had a planted trigger:
   - forge FAIL_ABLATION: 0/203 verdicts (IMPL).
   - Era-1 zero_output: 0/37 (IMPL).
   - The Achilles park bound cannot fire on its success path (IMPL).
   - Atlas field_conflict: 0 rows (REPORTED).
   Phase 3 needs every gate to have a demonstrated firing, not just a definition.
4. Inference boundary. The "irreducible" model work is narrow: naming rival explanations and hypotheses, framing,
   reading external prose, interpreting novel results, and writing a typed spec or adapter for a new engine or wall.
   Most remaining model usage is clock-driven status prose and hand-maintained ledgers that a join over git, comms
   and receipts already computes. One migration is complete: the operator brief, deterministic by default since
   af9b4d9c9 (IMPL, scripts/metis_portfolio.py:449-460). It was never A/B-tested.
5. Model layers were actively harmful where they narrated over structured state:
   - The LLM brief confabulated "14 agents pending" from 43 UNKNOWNs (HIST).
   - Era-1 Metis briefs repeated three internal items in 6 of 8 briefs (HIST).
   - The model-authored Atlas catalogue disagrees with its own reference rows for 16 systems (REPORTED).
   - A prose-derived count was off by a factor of about 9 (Atalanta L-10, HIST).
6. Operator attention is the binding resource:
   - About 171-177 operator prompts in 20 days (IMPL reproduction of a REPORTED count).
   - Zero prompts on 09-15, 09-20 and 09-22, which coincide with fleet idling (REPORTED, Aphrodite; consistent with
     my prompt-dir count).
   - 7 control orders, 16,858 words, in 40.1 h (IMPL, exact).
   - Five control regimes in six days.
7. CORRECTION to Ixion: "no mechanism records inference cost" is too strong. Two hooks exist:
   - Fabric's claude executor copies total_cost_usd, num_turns and duration_ms into each attempt's env_receipt
     (IMPL, fabric/executors.py:144-147, fabric/worker.py:218-219).
   - prometheus_llm has a per-call usage/cost audit log (IMPL, prometheus_llm/client.py:49-66). It is opt-in via
     PROMETHEUS_LLM_LOG, and no committed launcher sets it.
   What is unmetered is Claude Code seat-session inference, which is the bulk (INFER).
8. Two deterministic instruments here are directly relevant to Phase 3 rulers:
   - Hephaestus closure gauntlet, a substrate-capacity probe with nested arms and extensional membership.
   - Metis compose.py, a dependence-grouping evidence kernel that tells how many independent reasons N agreeing items
     really are.
   Both are under-validated: the gauntlet has 2 boolean specimens plus Q045, and compose.py has n=5 with a post-hoc
   positive control.

----------------------------------------------------------------------------------------------------------------

## 1. What was really built (infrastructure engines)

Columns: what it actually does | correctness demonstrated? | inference | state.

- Atlas index (atlas/ CLI, M1 schema atlas, 34 tables)
  - What it does: versioned harvesters parse git blobs, idle SQLite and Postgres into experiment, attempt, fact and
    edge rows. Each row points to a harvest_run, and each fact points to a source (commit, blob, line).
  - Correctness, numbers: YES. Counts and values matched source in every sample: 158 = 158 NPE receipts, 130 = 130
    frontier RUNs, Vivarium 1,242 = 1,242 (REPORTED, sub-crawler checks).
  - Correctness, classes: NO. atlas/classify.py:106-116 maps COMPLETE, PASS and QUALIFIED to POSITIVE (IMPL).
    649 of 723 POSITIVE rows are Vivarium "completed" (REPORTED, sub-SELECT).
  - Primitive layer: inherited labels, null by construction (REPORTED).
  - Inference: code is inference-free. Its catalogue, theory and proposals are model-authored data, stored beside
    parsed rows.
  - State: READY, loop PARKED. The index lags experiment activity by 8.58 d. Adapters exist for 5 of 15 registered
    engines.
- Atlas comb (13 SQL rules) and policy layer
  - Comb: 192 signals, all OPEN, none consumed (Ixion-SELECT).
  - Policy: fixed weights over model-written proposal fields (IMPL, policy.py:23-26). 92 scores, 0 outcomes ever
    (REPORTED). REDUCE and DEPRIORITIZE directives are appended unconditionally inside the horizon branch (IMPL,
    policy.py:203, 236).
  - Correctness is undemonstrable, because no outcome was ever written.
- Achilles census (achilles/census, host ELSA, every 6 h)
  - What it does: roster from roles/ on all origin refs plus a registry; S0-S6 activity rules over commits, comms
    and ew; field-level provenance; HTML page and email block.
  - Checked against git for 14 seats: 10 right, 4 wrong or weak (REPORTED, sub-crawler):
    - Mnemosyne ACTIVE came from path-majority misattribution of 2c8c81bbb.
    - Atlas PARKED: the parser takes the first "seat state:" line (IMPL, classify.py:198-205; Atlas STATUS.md line 5
      says READY, line 24 says PARKED for the LOOP).
    - Metis RETIRED: the mapping CLOSED -> RETIRED (IMPL, classify.py:195).
    - Pronoia DORMANT, while its daemon reports productive.
  - The email loop closed once (REPORTED, sub-SELECT).
  - Inference: free per run. The registry was model-authored once.
  - State: live. Two runs.
- comms (Postgres queue on M1)
  - Transport is stable since 09-11: 1,239 messages (Ixion-SELECT).
  - Pull-only. Presence understates live seats (Cyclops F4, IMPL in the audit text).
  - Message content is model-written.
- MWO/CWO control plane (ops/work_orders, ops/fleet)
  - The two-commit publication protocol ran cleanly 3 times with SHAs (HIST, PUBLICATIONS.md).
  - QUEUE.json and CENSUS.json are hand-edited by a model session.
  - fleet_status.py: 5 flags, no schedule, no receipts.
  - Authoring is ChatGPT plus the operator.
- Agent Fabric v0.2 (fabric/)
  - What it does: Postgres task, attempt and lease store with invariants enforced in the DB (one running attempt
    per task, one lease per resource, idempotent submit, fencing). Pull workers.
  - Correctness: invariants are enforced by schema; the FP-001 recovery probe passed (REPORTED); 23 defects in
    3 days.
  - Usage: 347 tasks and 373 attempts, all on ubu001 (337) and ubu002 (36) (Ixion-SELECT).
  - Inference: the runtime is free; the claude executor is model work by design.
  - State: live, idle since 09-30 15:33Z.
- promexec broker
  - A root sudo broker (systemd DynamicUser / PrivateNetwork) for model-proposed code.
  - NOT ENABLED; the install is blocked on the operator.
  - The round-2 pin 3cf32a64 reproduces from git. A Windows CRLF working copy hashes differently (REPORTED,
    Odysseus dossier).
- PEW / Evidence Wiki (ew schema, REST 8377)
  - Write-path gates (idempotency, derived-view refusal, vocabulary refusal); campaign reader.
  - Rows: 32,938 campaign observations with line provenance (REPORTED, sub-SELECT). The curated layer is frozen:
    79 experiments from 09-01..09-03 (Ixion-SELECT), and 143 of 147 claims are MODEL_EXTRACTED.
  - DOWN since 09-23: the watchdog parked it and posted #542, and nobody responded for 8 days.
  - The ew/db.py identity guard is the shared connector for comms, atlas, fabric, ludus and archaeon (live).
- M4 intelligence loop plus mailer (scripts/intelligence_loop.py, metis_portfolio.py, send_brief_email.py)
  - Deterministic brief by default (IMPL, metis_portfolio.py:449-460). Has a CoT-leak guard.
  - Runs about 6 times a day. Work-aware heartbeat since PRON-03. Live on M4, which no seat can reach.
- Pronoia Era-1 pipeline (pronoia.py, deleted 3b3c74bc0)
  - A serial subprocess chain gated on date-named files, with a regex health audit.
  - The audit was INVALID: 27 UNHEALTHY, 10 DEGRADED, 0 HEALTHY of 37 (IMPL, tallied from agents/pronoia/logs).
    zero_output (len < 20) never fired (IMPL predicate at 3b3c74bc0^:pronoia.py:481).
  - The orchestrator was free; 5 of its 9 stages were LLM. Retired.
- productive_liveness.py (Pronoia)
  - L0-L5 ladder. Cadence comes from config, not observation. Returns INCOHERENT on future timestamps (IMPL,
    productive_liveness.py:141-181).
  - Tests T1-T4; the live value reads 'productive' (REPORTED).
  - Inference-free. Wired into the live loop.
- Alethelia (agents/alethelia)
  - Every field is {value, query} or {unknown, query}. 7 tri-state rules. Calm requires 0 UNKNOWN, 0 FIRED and
    0 INDETERMINATE (IMPL, banner_text, alethelia.py:375-388). A planted stale-agent decoy test exists (IMPL,
    test_alethelia.py:111-112).
  - The 7/7 control pass is REPORTED, not re-run.
  - Inference-free. DORMANT: no host since 09-11.
- Hephaestus 1.0 forge (agents/hephaestus, forge/)
  - LLM-written ReasoningTool classes, mostly regex plus zlib-NCD scorers (REPORTED: grep census 340/366 forge
    files).
  - Ledger: 6,661 rows, 385 forged, 6,276 scrap, 2,861 of them api_call_failed (IMPL, parsed). 4,469 rows are from
    March.
  - Ruler: see section 4, R1. FAIL_ABLATION fired 0 of 203 times (IMPL).
  - Inference: generation is model work; scoring is free. Retired.
- Hephaestus Forge Queue plus closure gauntlet (hephaestus/src)
  - Gauntlet arms A0 (frozen primitives), A1 (+ routing), A2 (+ frozen generic basis) and B (small generic language).
    Membership is typed, verify_exhaustive on points disjoint from search, plus verify_shift. Output: ROUTE_CLASS and
    CLOSURE_MARGIN (IMPL, closure_test.py:1-30).
  - Controls: ALL_PASS for vacuous_truth and consistency_check (IMPL, hephaestus/STATE.json). Every receipt has
    dirty=true (IMPL).
  - Inference-free. Dormant since 09-11. No packet has completed a cycle (HIST).
- xpol_2026 replay
  - Floors computed before any model call (IMPL, floors.json, computed 2026-09-19T12:01Z). shape.py fingerprints
    mechanisms.
  - Generation arms are model work. 3-30 packets per arm (REPORTED).
- Metis compose.py
  - Set operations over declared structure: union-find over shared upstream tokens, instrument vetoes, cheapest
    partitioning discriminator (IMPL, compose.py docstring).
  - 13 adversarial tests (REPORTED). A frozen specimen; not integrated anywhere.
- Atalanta daemon
  - A primitive and composite-chain counter over Apollo runs. It scanned three guessed paths (IMPL,
    daemon.py:63-67) that Apollo never wrote (IMPL: Apollo's tracked runs are apollo/run_* and apollo/archive/*/run).
  - 0 runs read. 305 alarms with no recipient (REPORTED, sub-SELECT; the code path in daemon.py:547-552 has no
    return and no state change). Retired.

----------------------------------------------------------------------------------------------------------------

## 2. The inference boundary (which functions genuinely need a model)

Ixion's tally: 143 rows. 80 INFERENCE_FREE, 16 ASSISTED_PLAUSIBLY_DETERMINISTIC, 14 OCCASIONAL_JUDGMENT,
32 MODEL_MEDIATED, 1 other (inference_dependency_map.md s3). Rows are not distinct functions: the brief, the
census and liveness each appear under several crawlers. Read the tally as shape, not measure.

A. Demonstrated removable: a deterministic implementation exists AND has run.
- Operator brief narrative (IMPL; deterministic default since 08-18). The proof is removal with no recorded loss.
  There is no A/B and no consumption metric (UNK what was lost).
- Fleet liveness and activity (Achilles S0-S6; productive_liveness). This makes CWO heartbeat messages redundant:
  86 heartbeat-subject messages in about 25 h, 14 of them "no change" from one seat (REPORTED, sub-SELECT).
- Truthful status reporting (Alethelia). It ran 3 times and is unhosted.
- Mechanism classification of generated code (xpol shape.py, knockout_ablation.py).
- Substrate-capability route classification (closure gauntlet).
- Work-item routing (hephaestus refine.py). Never exercised through a full cycle.
- Era-1 pipeline orchestration. The orchestrator never needed a model.

B. Plausibly deterministic: the rule is fully stated, but a model executes or triggers it today.
- WORK_STATE, STATUS, QUEUE, CENSUS and MONITORS writing. 432 WORK_STATE commits since 09-27 (IMPL, git count).
- Cyclops reconciliation F1-F5: every finding is a join over git, comms, the fabric lease table and the process
  table (IMPL in the audit text). None of the 5 proposed predicates is implemented.
- Two-commit P/R publication. Fully specified, no script. The CWOs skipped it.
- S2 claim verification: C3-C6 reduce to grep and hash checks (REPORTED).
- Triggers for index passes, ingestion, batteries and census registry refresh, plus alarm FIRST response
  (restart / park / page). About 93 disabled one-shot launchers point into session scratchpads (REPORTED).

C. Occasional judgment (real, but bounded).
- Writing an index adapter for a new engine. This is the recurring cost behind the 8.6 d Atlas lag.
- Writing a typed closure spec for a new wall.
- Migration and contract authoring.
- Encoding historical evidence into bundles (Metis F4: the single encoder is the weak joint).
- Thresholds and which rules exist (Alethelia constants traced to the registry).

D. Irreducibly model or human today (every crawler converges on these).
- Naming rival explanations. SEASON1_RECEIPT: "someone still has to name BASE_RATE_PRIORS" (REPORTED in the
  receipt; quoted by Ixion).
- Hypothesis generation, experiment framing, interpreting novel results.
- Reading external prose (Deep Research: 53 of 423 fired, REPORTED).
- Security audit of novel code (D2 v1-v13). The validity of this verdict is itself unmeasured.
- Hard gates and retirement rulings (human).

E. Where model layers did harm (keep these as negative controls for any Phase 3 reporter).
- LLM brief: "14 agents pending" from 43 UNKNOWNs; CoT leaked into emails; narrated a frozen June snapshot 6 times a
  day for 8 weeks (HIST; af9b4d9c9 message).
- Metis 1a: 6 of 8 briefs repeat three items in different words, which defeats the sha256 staleness check (HIST).
- Model-authored Atlas catalogue: 16 verification strings disagree with the attached reference rows (REPORTED).
- Model-authored census registry: static thereafter, with no drift check (ACHILLES-10 unbuilt).
- 2026-06-24 AI salvage dossier recommended "directly portable" detectors that could not fire (CORR, Pronoia
  dossier s20).

F. Inference cost metering.
- Fabric records cost per claude attempt (IMPL code path; whether the stored values are non-null is UNK, because I
  ran no DB or blob read).
- prometheus_llm has an opt-in usage log, unused in committed launchers (IMPL, git grep finds no setter).
- comms.agents holds only a self-declared model string (REPORTED).
- Seat sessions are not metered.

----------------------------------------------------------------------------------------------------------------

## 3. Coordination overhead and operator-attention load (quantified)

Regime dwell. Timestamps are local -04, from git commit times (IMPL):

    regime / order                         start                 end / superseded        dwell
    April Agora (Redis)                    04-15                 04-29                   ~14 d
    no fleet channel                       04-29                 09-11                   ~135 d
    SI peer stewards                       09-25 11:29 (04379db69) 09-26 09:04 (b62b35eb2) 21.6 h
    sign-off release                       09-26 09:16 (4f5d9bac8)  -                      -
    direct operator control                09-26 09:16           09-28 21:48             ~60.5 h
    MWO-0001 (Cyclops sole custody)        09-28 21:48 (7e4c09f2c) 09-29 02:56 (89512068f) 5.1 h
    MWO-0002                               09-29 02:56           09-29 07:14 (624a686ea)  4.3 h
    MWO-0003                               09-29 07:14           09-29 07:42 (25a486d44)  0.47 h (28 min)
    base-role 2a H "no smart global scheduler" 09-29 09:09 (1e9042017) contradicted by CWO 19.2 h later
    CWO-A (Aporia "fleet scheduler")       09-30 04:18 (6a7a84569) 09-30 09:16 (d4e47ebf5) 5.0 h
    CWO-B (promotion frozen)               09-30 09:16           09-30 13:55 (7d373ac02)  4.65 h
    CWO-C                                  09-30 13:55           governing                -

Control-text volume (IMPL, wc -w): MWO-0001 3,249; MWO-0002 3,247; MWO-0003 972; MWO-0004 1,706; CWO-A 2,490;
CWO-B 2,241; CWO-C 2,953. Total 16,858 words, 09-28 21:48 to 09-30 13:55 (40.1 h). Every live session re-reads
each order. Mean dwell between consecutive orders was about 6.7 h, and the shortest was 28 min.

State bookkeeping. These are commits reachable from bed05507a by author date, all branches merged into it, counting
commits whose files are only WORK_STATE.json, journal or STATUS (IMPL, my count):

    day    commits  state-only  share
    09-24  176      11          6%
    09-25  240      40          17%   (steward era)
    09-26  199      18          9%
    09-27  135      0           0%
    09-28  256      17          7%
    09-29  379      84          22%   (MWO adoption wave)
    09-30  529      61          12%   (CWO + heartbeats)

432 commits touched WORK_STATE.json between 09-27 and bed05507a, about 98 a day (IMPL; matches Ixion). Cyclops F3:
5 seats wrote updated_at_utc in the future (IMPL, audit text). F7: QUEUE.json CURRENT differs from WORK_STATE for
10 of 13 seats. The auditor calls it "mostly legitimate self-promotion", so the queue of record is a snapshot,
not a live queue. Ixion's framing of this as pure drift is slightly stronger than the audit's.

Operator attention:
- Aphrodite's strict count: 177 operator prompts across 41 seats in 20 days, 8.9 per day (REPORTED; method in
  roles/Aphrodite/harvest_2026-09-30/evidence/findings_A4_human_reuse.md:11, 319).
- My reproduction by filename rule alone (a dated prompt dir holding an OPERATOR* file, or a dir name containing
  "operator"): 171 dirs, 39 seats (IMPL). This agrees to within the text-match additions.
- Zero operator prompt dirs dated 09-15, 09-20 or 09-22 (IMPL), the days Aphrodite reports about 2 active seats.
- comms (sub-SELECT): coordination-only subject share 23% -> 20% -> 28% -> 40% over W37 to W40 (INFER-grade subject
  heuristic); broadcasts 10 -> 16 -> 26 -> 45 per week; 849 of 1,239 messages are kind=report.
- The base role makes the operator the transport for cross-model review: ASCII blocks pasted by phone (REPORTED,
  base role s4).
- Steward window: the two stewards sent 94 of 162 messages; the deepest thread is a 27-message, depth-21 exchange
  on prereg rules (REPORTED, sub-SELECT).

Seat role churn:
- Aporia held roughly 11-14 roles in 5.5 months, 9 of them in 09-25..09-30 (REPORTED). Its seat file still
  describes the 09-11 role (IMPL per dossier).
- Cyclops held three coordination roles in 6 days and was parked twice.
- Odysseus changed lane four times in four days.
- Hephaestus has two unreconciled 2.0 framings on main.

Reading: coordination cost scaled with control-regime changes and clock-driven reporting, not with science.
The single strongest throughput signal is operator presence. INFER: any Phase 3 design that needs a model session
to trigger, respond or relay will inherit the operator as its rate limiter.

----------------------------------------------------------------------------------------------------------------

## 4. Historical results, reclassified (evidence-profile axes Q S W R B Rep M)

R1. Hephaestus 1.0, "the generator is dead by measurement" (c0954083b, 09-01).
- Ruler facts (IMPL, floors.json):
  - chance 0.3238
  - NCD pass comparator 0.3925
  - position-majority decoy 0.4032, at idx=1 (75 of 186 correct answers sit at index 1, so the battery's answer
    positions are skewed)
  - random 200-tool p95 0.3817, max 0.4086
  - P(random tool passes the 1.0 gate) = 0.035
- 2,861 of 6,661 rows are api_call_failed (IMPL).
- FAIL_ABLATION: 0 of 203 (IMPL). T3 never launched.
- Axes: Q P | S U | W N (a constant decoy beats the comparator) | R N | B P (floors computed retroactively on 09-19) |
  Rep P (xpol: 3-30 packets per arm) | M N.
- Class: ruler_insufficiency + implementation_defect (instrument failure counted as outcome). NOT true_negative.

R2. Hephaestus +11.1 pp R3 / +32.1 pp R4 from hand-built engines (11e919e20, 08-19).
- On the forge's own ruler; "oracle cannot grade it".
- Axes: Q P | S Y (engines exist) | W U | R N | B U | Rep P (re-run on the same ruler: closer to deterministic
  replay) | M P (knockout card).
- Class: survives_as_anomaly, instrument-relative.

R3. Closure gauntlet specimen 3 (Q045): 18 OPERATOR / 2 INCONCLUSIVE(B) / 0 SEARCH_ROUTING; controls ALL_PASS
(deb9ca34a, d57a5c80e).
- A v1 shift column caused 4 false negatives, since corrected (HIST).
- The gauntlet was frozen after two boolean specimens with a bool() coercion degenerate on vectors (HIST).
- Axes: Q Y | S Y (constructive enumeration) | W P | R P | B Y (arm B is the "any small program" control) | Rep N | M P.
- Class: instrument_positive with a corrected implementation_defect.

R4. xpol: "size buys mechanism existence, not quality" (9a4e3df54); Fable 5.1 "two tools >= 0.50".
- Axes: Q Y | S P | W N (same ruler as R1) | R N | B Y (floors before calls) | Rep N (n=1 draws) | M P (shape.py).
- Class: statistical_insufficiency + ruler_insufficiency.

R5. Atalanta: "designed to detect reusable primitives. She detected none" (051304cd0, retired 09-11).
- No Apollo run was ever read (IMPL path evidence; 354 UPSTREAM_NOT_FOUND per sub-SELECT).
- Retirement tested code uniqueness, not the hypothesis.
- Axes: Q N | S U | W U | R N (liveness = path existence) | B N | Rep N | M N.
- Class: implementation_defect (consumer-invented producer interface). The hypothesis is untested. Apollo is
  suspended (HIST), so there is now also world_insufficiency.

R6. Metis compose.py Season 1: SPECIMEN_SURVIVES_RETROSPECTIVE, "narrowly" (f9f90c0f7).
- In 5 of 5 episodes, N agreeing items collapsed to one independent reason, and a cheaper discriminator existed
  (REPORTED, receipt).
- Positive control E1b was built after the result (IMPL, receipt text).
- Axes: Q P | S Y | W P | R P | B N (no single-channel baseline; P-5 untested) | Rep N (one encoder) | M N.
- Class: survives_as_anomaly / statistical_insufficiency. "Retired" is a census artifact (CLOSED -> RETIRED, IMPL).

R7. Metis 1a literature analyst (March).
- Axes: Q N (never measured against a decision) | S P | W U | R N (hash novelty defeated by rewording) | B N |
  Rep N | M N.
- Class: ruler_insufficiency. The value of literature triage is unmeasured.

R8. Operator brief migrated from LLM to deterministic (af9b4d9c9).
- Axes: Q P | S Y | W Y | R P (CoT-leak marker guard) | B N (no A/B) | Rep Y (running about 6 a day since) |
  M P (removing the LLM removed confabulation).
- Class: instrument_positive for "model layer not needed". The magnitude of the loss is UNK.

R9. PEW V1-V3 memory advantage (METABOLIZATION_NOT_DEMONSTRATED; no design advantage; MARGINAL +0.111).
- Axes: Q N (all arms 4/4 in V1) | S Y | W N (priors greppable) | R N | B P | Rep N | M N.
- Class: ruler_insufficiency (saturated). The proposed fixes were declared and never run.

R10. PEW G6 TENSOR_NOT_YET_JUSTIFIED (MRR curated 0.605 vs BM25 0.078, embeddings 0.062, CP 0.023).
- Axes: Q P | S Y | W P | R P | B Y | Rep N | M N.
- Class: statistical_insufficiency (99 coordinates; the 1,000 trigger was never reached).

R11. Era-1 Pronoia health audit: 0 of 37 HEALTHY (IMPL tally).
- A single "429" or "backoff" substring forces UNHEALTHY. zero_output never fired. The VRAM check measured the whole
  GPU.
- Axes: Q N | R N | B N.
- Class: ruler_insufficiency (graded self-reports).

R12. check_intelligence_pipeline: "HEALTHY 7/7" while Groq returned 403 and extractions were 0.
- IDLE is treated as healthy, and the warning regex needs the bracketed form.
- Class: false_positive (ruler defect).

R13. Era-2 heartbeat read 'online' while work failed (09-12..09-17); PRON-03 fixed it.
- Axes for productive_liveness after the fix: R P (tests T1-T4; live 'productive', REPORTED) | Rep P.
- Class: false_positive, then instrument_positive.

R14. Atlas.
- Numeric facts: instrument_positive (R Y for counts). Q Y | B N/A | Rep P (re-harvest).
- atlas_class POSITIVE: false_positive. Execution state is merged into outcome (IMPL regex).
- Primitive/combination "TESTED/UNEXPLORED": ruler_insufficiency (inherited labels). Do not read any "primitive X
  does not matter" from it.

R15. Atlas policy layer.
- Q N (0 outcomes) | R N | B N.
- Class: untested. The constant directives are an implementation_defect (IMPL).

R16. Achilles census.
- Axes: Q Y | R P (10/14 vs git) | Rep P (two runs) | B N/A.
- Class: instrument_positive (partial) with a provenance_defect (path-majority), a parse defect, and a lifecycle
  over-claim. "62 experiments in 24 h" is a false_positive (verdict-word regex). Its park guard cannot fire on the
  success path (IMPL, run.py:171-172).

R17. Alethelia: 7/7 controls (REPORTED).
- R P (a decoy test exists) | Rep N (not re-run).
- Class: instrument_positive (REPORTED). DORMANT is a deployment gap, not instrument failure.

R18. Fabric S2/S3 coordination cost: 0.28 and 0.67 actions per execution vs 3.5 (IMPL text of RESULT.md; values
REPORTED).
- The control is another seat's self-test ledger, a lower bound, on a different task type.
- S3 blind quality was 10.0 vs 9.1 at the rubric ceiling (IMPL text).
- Axes: Q Y | B P | R N for quality | Rep N.
- Class: statistical_insufficiency (baseline mismatch) + ruler_insufficiency (ceiling).

R19. D2 firewall audit: FAIL v1-v12, PASS v13, same auditor lineage (REPORTED; bodies not opened, holdout-adjacent).
- R U | Rep N.
- Class: ruler validity unknown.

R20. SI peer-steward experiment, frozen after 21.6 h.
- Q N (no outcome variable declared) | M N. It contains real catches: the C1b guard false-release defect and the #627
  readout defect (REPORTED).
- Class: not a negative; cause UNK.

R21. FP-001 cold-start probe "PASS".
- Discovery came through same-day traces written by the prober (REPORTED, notes).
- Class: false_positive (the label overstates).

R22. Odysseus brain v0 (bit-identical under 40% datagram loss, REPORTED) and Expedition 1.
- Both were frozen after 1 day by operator lane changes or a host reaper.
- Class: not negatives (pressure / scheduling decision).

R23. PEW outage (#542 on 09-23, unanswered through 10-01) and PrometheusMachineProbeM1 (failing every 5 min for
about 4 months, Ixion-SELECT via schtasks).
- Class: detection without response (institutional); the probe failure is an implementation_defect.

R24. Ixion: "no mechanism records inference cost" (REPORT s7).
- Class: CORR. Hooks exist in fabric and in prometheus_llm (IMPL code). Coverage of seat sessions is absent.

----------------------------------------------------------------------------------------------------------------

## 5. Instruments, and whether their detectability was demonstrated

Demonstrated, or with real controls:
- Closure gauntlet: positive, negative and cheat controls ALL_PASS on two walls (IMPL, STATE.json).
- xpol floors: they exposed that the 1.0 ruler sits below a decoy, which is detection of ruler weakness itself
  (IMPL, floors.json).
- Atlas harvesters: counts and values match source in every sample (REPORTED, sub-crawler); 14 record-vs-source
  checks.
- Achilles census: 10 of 14 seats agree with git (REPORTED); 26 tests including cheat controls (not run).
- Atalanta DEAD_GATING predict-then-query: 305 alarms predicted from control flow, 305 observed (REPORTED,
  sub-SELECT). This is a code-to-data consistency check.
- prepost_check.py: 6 controls, including the real #585 body as a negative (REPORTED).
- Alethelia: a planted stale-agent decoy (IMPL test exists; pass REPORTED).
- productive_liveness: tests T1-T4 with an injected clock (IMPL code; pass REPORTED).
- Metis compose.py: 13 adversarial tests plus one post-hoc positive control (REPORTED).
- Fabric invariants: enforced by the DB schema; FP-001 kill-and-reap probe (REPORTED).
- Hermes failure-signature convergence (sha256 over at-failure observables): 2 of 5 historical cases converge
  (REPORTED).

Guards defined but never shown able to fire, or unable to fire:
- forge FAIL_ABLATION: 0/203. An all-zero tool passes the concentration test (REPORTED, Lexis G1).
- Era-1 zero_output: 0/37.
- Achilles park bound: reset by its own push and by M4 auto-commits.
- Atlas field_conflict: 0 rows.
- base-role scheduled-task self-test: its name regex misses FoundryAPI and nestor_z80atlas (REPORTED).
- Metis 1a sha256 staleness check: defeated by rewording.
- PEW M1 restore-verify: Task Scheduler last result 1, while MONITORS cites the run as good (CORR, REPORTED).

----------------------------------------------------------------------------------------------------------------

## 6. Informative geometries (worth carrying as patterns, not as components)

1. Nested-closure capacity probe (closure gauntlet).
   - Freeze the input-to-semantic-state arrow, then ask at which nested arm a mechanism-bearing witness exists:
     A0 primitives, A1 + routing, A2 + frozen generic basis, B any small program.
   - Membership is extensional: typed, exhaustive on points disjoint from search, robust on a shifted regime.
   - It answers "can this substrate instantiate the phenomenon at all", the S axis, by construction. That is the
     missing column in almost every historical result.
2. Floors before any call (xpol). Compute chance, the constant decoys, a position-majority decoy, the NCD baseline,
   and a random-tool distribution with P(random passes gate) before any generator runs. Any gate a random tool
   passes with probability 0.035 is not a capability gate.
3. Dependence-collapsed evidence counting (compose.py). Union-find over declared shared upstreams, so that N agreeing
   items become k independent reasons. Then veto suspect instruments and pick the cheapest discriminator that still
   partitions the live explanations. This is the right shape for honest Rep accounting: deterministic replays and
   shared-upstream "replications" collapse to one.
4. Query-carrying report with tri-state rules (Alethelia):
   - every value carries its query
   - UNKNOWN is a value
   - a rule over an UNKNOWN field is INDETERMINATE
   - calm requires zero of everything
   - dependency-injected fixtures supply positive and cheat controls
5. Work-aware liveness ladder (productive_liveness): L0 process, L1 eligibility, L2 attempt, L3 success, L4 artifact,
   L5 consumption (not inferable). Cadence is declared, not observed. Future evidence is INCOHERENT.
6. Predict-then-query (Atalanta specimen). Predict a count from control flow, then query the store. A mismatch means
   code and data disagree.
7. Retrospective replay at a historical cutoff with an admissibility filter (compose.py PREREG s4: COMMIT /
   EXTERNAL / INTERNAL). A cheap way to test a selection rule against the fossil record before running it forward.
   Its weakness is author encoding, and a second blind encoder is required.
8. Preregistered adoption experiment with the scoring key committed by sha256 before scoring (Fabric S3). Good
   protocol shape; it was undone by a ceilinged rubric and a mismatched control.
9. Separate "ran", "observed" and "concluded" layers, with author verdict and machine candidate both kept (Atlas
   addendum). The data supports it even where the manifest column picks wrongly.

----------------------------------------------------------------------------------------------------------------

## 7. Failure shapes (distinct classes, not collapsed)

- ruler_insufficiency:
  - 1.0 battery below a decoy
  - PEW saturated arms
  - Era-1 stdout audit
  - Metis 1a hash novelty
  - Fabric S3 rubric ceiling
  - Atlas primitive layer
  - Atlas class regex
- implementation_defect:
  - 43% API-failure rows recorded as subject outcomes
  - Atalanta guessed paths
  - machine probe file-not-found
  - Q045 v1 shift column
  - Atlas policy constant directives
  - Achilles first-line STATUS parse
  - Alethelia wrong-directory run overwriting the canonical report
- provenance_defect:
  - Achilles path-majority attribution
  - PEW submitted_by='Mnemosyne' for 73 experiments attributed to 18 agents
  - every Hephaestus receipt dirty=true
  - PEW migration 015 applied from a dirty tree
  - batteries write the receipts they are judged by
  - host-local refs as sources
- statistical_insufficiency:
  - compose.py n=5, single encoder
  - xpol n=1 per packet
  - tensor at 99 coordinates
  - S2/S3 control from a different task type
- world_insufficiency: Atalanta now (Apollo suspended); PEW V1-V3 tasks whose priors are greppable (the world did not
  demand memory).
- search_insufficiency (weak evidence): 1.0 Nous queue exhaustion, forge rate 0.6% at the last heartbeat (HIST);
  370 of 423 Deep Research prompts never fired.
- false_positive:
  - LLM brief calm
  - Era-1 and Era-2 health labels
  - atlas_class POSITIVE
  - census "62 experiments"
  - FP-001 PASS
  - 32 of 36 agora heartbeat rows still 'online' after 7 days (REPORTED)
  - Atalanta 354 of 354 "productive" ticks under any emission metric
- Institutional, cross-cutting (not experimental classes, but they produced the false negatives above):
  - detectors without responders
  - guards that cannot fire
  - label tables outliving their writers
  - control-regime churn with authority residue in code: the C1b release guard outlived the steward authority
  - consumer-invented producer interfaces (D-28 still unruled)
  - retirement by code-uniqueness or bundle membership rather than by a hypothesis test
  - name reuse across eras hiding lineage (Metis A/B/C, Pronoia, Aletheia/Alethelia)

----------------------------------------------------------------------------------------------------------------

## 8. Design implications (requirement-relevant, each tied to evidence)

See the structured output (design_implications) for the condensed list. Expanded notes:

- Axes must be born with the experiment. Atlas shows that retrofitting world, organism, pressure and ruler onto a
  corpus yields empty columns. Registration should refuse an experiment without declared world, organism, pressure,
  development regime, ruler id and ruler-validation reference.
- Producers declare their interface (D-28). The consumer never guesses; Atalanta is the specimen. The index ingests
  through declared schemas, not per-engine hand adapters; the Atlas lag of 8.6 d and 5 of 15 engines adapted show
  the cost of hand adapters.
- Outcome vocabulary must keep execution state separate from scientific outcome. It must carry the distinct failure
  classes and keep the author verdict beside the machine candidate. Atlas collapses COMPLETE, PASS and QUALIFIED into
  POSITIVE.
- Before any generator, organism or capability verdict, the ruler ships with: chance and constant decoys, an
  answer-position decoy, a random-organism distribution, P(random passes gate), a planted positive, and a matched
  negative. Instrument failures go in a separate table (forge 43%).
- Every gate and guard has a planted trigger test that proves it can fire: FAIL_ABLATION 0/203, park bound,
  zero_output, field_conflict.
- Detection gets a deterministic first responder (restart, park, page) with a named recipient. Model involvement
  comes after the first response. The PEW outage went 8 days unanswered; the machine probe has failed for 4 months.
- Status, liveness and queue state are derived from receipts by code (Achilles, Alethelia, productive_liveness). No
  model-written heartbeats or hand ledgers. Timestamps come from the clock, and future timestamps are rejected.
- The control model is fixed with a minimum dwell between regime changes. Authority encoded in code is removed when
  the authority is retired.
- Metered inference is a first-class receipt field: extend the fabric env_receipt pattern to every model call
  (turn on the prometheus_llm audit and meter sessions).
- Replication is counted after dependence collapse (compose.py pattern). Deterministic replay is not Rep.
- Receipts pin a clean tree. Tests never mutate tracked receipts.
- Model-authored rows (catalogue, theory, extracted claims, registry) carry a row-level reliability class distinct
  from parsed rows.
- Execution capacity: Fabric workers were only ever two laptops; no attempt ran on M1-M4. Host handover stranded the
  PEW and the probes. Phase 3 engines need declared hosts and durability, independent of seat sessions.

----------------------------------------------------------------------------------------------------------------

## 9. Verification log (what this reader confirmed, corrected, or could not check)

Confirmed in the artifact (IMPL):
- floors.json values: chance 0.3238, NCD 0.3925, position-majority 0.4032, random p95 0.3817, P_pass 0.035.
- ledger.jsonl: 6,661 rows; 385 forged / 6,276 scrap; 2,861 api_call_failed; 4,469 / 436 / 1,756 rows in March,
  April, May.
- forge/verdicts: 203 files, FAIL_BATTERY 176 / FAIL_DIVERSITY 19 / PASS 3 / missing 5; FAIL_ABLATION 0. The code
  path is at forge/tester.py:444-445.
- Atalanta APOLLO_RUN_ROOTS (daemon.py:63-67) vs Apollo's tracked run dirs. The alarm branch at 547-552 has no
  return.
- metis_portfolio.py:449-460 is the deterministic default.
- compose.py docstring: "Deterministic. No learned weights, no model call".
- SEASON1_RECEIPT replay table and post-hoc E1b.
- atlas/classify.py:106-116 regex ladder. atlas/policy.py WEIGHTS and the unconditional REDUCE/DEPRIORITIZE.
- achilles run.py:171-172 productive predicate. classify.py:195 maps CLOSED to RETIRED; 198-205 takes the first
  "seat state:" line.
- Alethelia banner_text logic and the decoy test.
- productive_liveness derive_health: config cadence, INCOHERENT on future timestamps.
- Era-1 audits: 27 UNHEALTHY / 10 DEGRADED / 0 HEALTHY. zero_output predicate at pronoia.py:481 (3b3c74bc0^).
- Fabric S2/S3 RESULT text (0.28 / 0.67 vs 3.5 lower bound; rubric ceiling).
- Cyclops audit F1-F7 text.
- Total of the 7 order texts: 16,858 words.
- Regime transition SHAs and times.
- 432 WORK_STATE commits.
- Operator-prompt dir count, 171 by filename rule.
- Hephaestus STATE.json: controls ALL_PASS, dirty=true.
- Closure gauntlet arm definitions.

Corrected or nuanced:
- Inference cost hooks exist (fabric env_receipt; prometheus_llm opt-in audit). Ixion's "no mechanism" is too strong.
- The position-majority decoy is answer-position-informed (idx=1 holds 75 of 186). It is a property of the battery's
  answer distribution, not a "constant decoy" in the naive sense. The point stands: the gate does not demand
  reasoning.
- QUEUE.json vs WORK_STATE (10/13): the auditor calls it mostly legitimate self-promotion, so it is
  snapshot-staleness, not error.
- State-only commits on 09-28..10-01: 169 by my file filter, 158 per Ixion's. Same shape.

Not checked (no DB access used): the comms counts (1,239, 86 heartbeats, coordination share), atlas.signal 192,
fabric task and attempt counts, ew counts, agora rows, and schtasks state. The ones Ixion re-ran itself are tagged
Ixion-SELECT above.

----------------------------------------------------------------------------------------------------------------

## 10. Open questions

- Do fabric env_receipts actually carry non-null total_cost_usd for the 105 completed claude tasks? That would be
  the only real per-task inference-cost dataset.
- Would the 1.0 corpus, rescored on a decoy-calibrated ruler with the API-failure rows removed, put any tools above
  the random-tool p95?
- Does the closure gauntlet survive vector-valued walls once the bool() coercion degeneracy is removed? Only 2
  boolean specimens and Q045 have run.
- Does compose.py's 5/5 one-independent-reason pattern survive a second blind encoder and at least 3 positive
  controls (its own Season 2 preconditions)?
- Is fleet idling on zero-prompt days caused by operator absence, or is it confounded with weekends and host events?
- Do operator rulings exist outside the repo (Metis retirement, AGORA-01, D-28)?
- Do the nestor/d2v10..13 refs that Atlas npe/5 auto-harvested carry sealed material? (Flagged by Ixion; not opened.)

----------------------------------------------------------------------------------------------------------------

## 11. Files opened by this reader

docs/phase3/intake/ixion/REPORT.md; inference_dependency_map.md; institutional_timeline.md; engine_index.jsonl
(parsed); seats/{Atlas,Achilles,Mnemosyne,Aporia,Odysseus,Hephaestus,Metis,Atalanta,Pronoia,Alethelia,Cyclops}.md;
hephaestus/xpol_2026/floors.json; agents/hephaestus/ledger.jsonl (parsed); forge/verdicts/*.json (parsed);
forge/tester.py (420-450); agents/atalanta/daemon.py (55-75, 215-230, 540-556); git ls-files apollo;
scripts/metis_portfolio.py (445-462); roles/Metis/season1/specimen/compose.py (1-30);
roles/Metis/season1/SEASON1_RECEIPT.md (1-60); atlas/classify.py (100-130); atlas/policy.py (20-30, 196-236);
achilles/census/run.py (160-180); achilles/census/classify.py (192-210); roles/Atlas/STATUS.md (grep);
agents/alethelia/alethelia.py (370-392); agents/alethelia/test_alethelia.py (grep);
roles/Pronoia/science/productive_liveness.py (141-181); agents/pronoia/logs/audit_*.md (grep);
git show 3b3c74bc0^:pronoia.py (grep); roles/Odysseus/fabric_pilot/s2/RESULT.md and s3/RESULT.md (grep);
prometheus_llm/client.py (40-70), types.py (25-45), README.md (grep); fabric/executors.py (grep),
fabric/worker.py (205-225); hephaestus/STATE.json (parsed); hephaestus/src/closure_test.py (1-30);
roles/Cyclops/audits/2026-09-30_observability.md (16-79);
roles/Aphrodite/harvest_2026-09-30/evidence/findings_A4_human_reuse.md (grep);
ops/work_orders/archive/MWO-000{1,2,3,4}_*.md and ops/fleet/CWO_*.md (wc -w); git log metadata.
