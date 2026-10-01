# Institutional timeline -- Ixion territory (14 seats + shared infrastructure)

Currency: 2026-10-01T10:00Z (from date -u). Base read: origin/main bed05507a (2026-10-01).
Compiled by Ixion from six read-only sub-crawls (labels: atlas, fleet, memory, coord, build, hist).
242 dated events, merged and sorted mechanically; nothing was re-dated by hand.

Columns: date | crawler | seat/system | event | evidence (sha/path) | epistemic tag.
Tags: IMPL implementation fact, INTENT design intent, HIST historical claim, REPORTED reported result
(unverified), CORR later correction/contradiction, INFER code-inferred, UNK unknown.
Where two crawlers logged the same event both rows are kept (different evidence).
Dates are commit/author dates or DB timestamps as each crawler read them; month-only rows sort first.

## Era map (orientation only; derived from the rows below)

    2026-03 .. 04     Era 1: Pronoia serial pipeline, Metis/Hermes/Aletheia agents, Hephaestus 1.0 forge
                      (most forge ledger rows), April Redis Agora (04-15..04-29)
    2026-05 .. 08     Aporia Deep Research dispatcher; M4 intelligence loop + mailer; Atalanta daemon;
                      Redis retired 06-24 (PgRedis); LLM brief -> deterministic-first 08-18
    2026-09-11        Base role + D-23 working contract + comms revived on Postgres; mass seat adoption
    2026-09-14 .. 22  Agora archaeology/retirement rec.; Atlas chartered (09-19); Fabric/Worlds Kernel builds
    2026-09-25 .. 26  SI peer stewards (Aporia M1 + Cyclops M2) -> operator freeze -> direct operator control
    2026-09-28 .. 29  Master Work Orders MWO-0001..0004; base role 2a work-conserving loop; boot step 1 -> CURRENT.md
    2026-09-30        CWO fleet activation (A, B, C); heartbeats reimposed; Achilles census built; Atlas inference harvest
    2026-10-01        Achilles census live every 6 h; Phase 3 forensic crawlers chartered (Sisyphus b3cb79806, Tantalus 21a47402a, Ixion b871bcd38; Tityos seat created 6a6d6d9b4, no charter on main at 10:3xZ)

## Events

- 2026-03 | build | Hephaestus | 4,469 of 6,661 ledger rows written in March | ledger.jsonl timestamps (parsed) | IMPL
- 2026-03-22 | hist | Metis | Era-1 analyst agent created ("cunning intelligence") | cc9527863 | IMPL
- 2026-03-22 | hist | Pronoia | first "pronoia: auto-publish reports" commits (pipeline running before its own commit) | 2947dae6f | IMPL
- 2026-03-23 | fleet | Hermes | agents/hermes mailer first committed (SMTP) | eb17886fa | IMPL
- 2026-03-23 | hist | Pronoia | pronoia.py + Aletheia/Clymene/Hermes added; full serial pipeline wired | eb17886fa | IMPL
- 2026-03-23 | hist | Pronoia | first committed audit, UNHEALTHY (Metis 429) | agents/pronoia/logs/audit_2026-03-23_134526.md | IMPL
- 2026-03-23 | memory | Hermes | agents/hermes digest agent added to the Pronoia scan chain; first digests | eb17886fa; agents/hermes/digests/ | IMPL
- 2026-03-24 | build | Hephaestus | agents/hephaestus created with Nous + Ignis v2; first ledger row 13:20 | 2f3e4eb6f; agents/hephaestus/ledger.jsonl | IMPL
- 2026-03-24 | hist | Pronoia | pronoia.py +369/-37 (Skopos, audit, Titan generate) | 7e9719cb0 | IMPL
- 2026-03-25 | build | Hephaestus | forge pipeline v2: NCD baseline, 15-trap battery, continuous operation | da42cc7e0 | HIST
- 2026-03-29 | hist | Metis | hash-based staleness detector added to metis.py | 6058e6eb1 | IMPL
- 2026-03-31 | hist | Metis | brief body is the cascade failure string "(Metis could not reach any LLM provider)" | agents/metis/briefs/2026-03-31_brief.md | IMPL
- 2026-03-31 | hist | Pronoia | 5 health_intelligence reports read HEALTHY 7/7 while Aletheia logs Groq 403 + 0 extractions | agents/pronoia/logs/health_intelligence_enhanced_2026-03-31_191441.md | IMPL
- 2026-04-01 | hist | Pronoia | last audit (DEGRADED) and last auto-publish; check_intelligence_pipeline.py committed | 726b51ae8, 9e189d683 | IMPL
- 2026-04-01 | memory | Hermes | last March digest (2026-04-01_0326_digest.md); 42 digests tracked in git | git ls-files agents/hermes/digests | IMPL
- 2026-04-03 | build | Hephaestus | forge/ tiered tree committed (T1/T2/T3 README, tester, amino_acids, forge_primitives) | b674a9976 | IMPL
- 2026-04-03 | hist | Metis | last commit touching agents/metis | b674a9976 | IMPL
- 2026-04-06 | build | Hephaestus | T2 "dead in the water since ~2026-04-06" | roles/Hephaestus/ROLE.md s5 | HIST
- 2026-04-15 | coord | Agora | Redis-backed "distributed adversarial science team" created; streams, 60 s heartbeats, 5-min death rule | 98b65559a | IMPL
- 2026-04-15 | coord | Agora | Postgres persistence + catchup for session recovery (agora.messages) | db8e9a3b5 | IMPL
- 2026-04-15 | coord | Agora | 107 of 196 agora.messages rows written on this one day | select created_at::date,count(*) from agora.messages | IMPL
- 2026-04-15 | coord | Aporia | seat created; Phase 1 triage 23A/17B/450C | 9c4789aa7, c03a17de3 | HIST
- 2026-04-15 | fleet | Agora | Redis-backed Agora created; agora.messages holds 196 messages 2026-04-15..29 | 98b65559a; comms/README.md:3-6 | IMPL/HIST
- 2026-04-15 | memory | Mnemosyne | seat created as DBA & Data Steward; M2 -> Postgres migration of 162,769 rows | da460b7e1, 831fa3295; SESSION_JOURNAL_20260415.md | HIST
- 2026-04-17 | coord | Aporia | charter rewritten as Void Detector, 5 strategies, overseer role | 4b2790e5b | INTENT
- 2026-04-17 | coord | Harmonia/agora | delegation layer + joint catalog; work_queue; reserve_p_id counter | 4f42135aa, c8f3745f2 | IMPL
- 2026-04-23 | fleet | Pronoia | Era 1 pronoia.py deleted in repo cleanup for external visibility | 3b3c74bc0 (per MONITORS row + RECONSTRUCTION s2) | HIST
- 2026-04-23 | hist | Pronoia | pronoia.py deleted "for external visibility" and gitignored | 3b3c74bc0 | IMPL
- 2026-04-23 | memory | Hermes | pronoia.py (caller of Hermes) deleted from tree and gitignored | 3b3c74bc0 per MONITORS.md row 46 | HIST
- 2026-04-29 | coord | Agora | last agora.messages row (07:06) | select max(created_at) from agora.messages | IMPL
- 2026-04-29 | memory | Mnemosyne | stand-in Claude session applies sigma schema to prometheus_fire | 7a053e6b6 | HIST
- 2026-05-02 | coord | Aporia | pivot doc + 20 pivot research reports | 68cf5efd3 | HIST
- 2026-05-06 | coord | Aporia | tracked doctrine critical_memories.md (HARD-1 no papers) | 18383103b | IMPL
- 2026-05-06 | memory | (doctrine) | aporia/doctrine/critical_memories.md created as portable doctrine replacing M1-local feedback memory | 18383103b | IMPL
- 2026-05-08 | memory | (doctrine) | last edit of critical_memories.md (HARD-6) | 7cb418d1d | IMPL
- 2026-05-11 | coord | Aporia | Gemini Deep Research dispatcher + daily burn orchestrator | 4c6131fe9 | IMPL
- 2026-05-13 | fleet | (M4 loop) | scripts/portfolio_monitor.py first committed (hard-coded EXPECTED_AGENTS) | 8b8676272; scripts/portfolio_monitor.py:85 | IMPL
- 2026-05-15 | hist | Pronoia/Metis | name reuse: "Metis portfolio mode: LLM brief over Agora state" + intelligence loop scheduler | 56d128abc, b0787cfc4 | IMPL
- 2026-05-15 | memory | Hermes | send_brief_email.py + Pages dashboard built under HERMES_* namespace | 74c4c5834, 36c0f4be3 | IMPL
- 2026-05-17 | fleet | Hermes | agents/hermes mailer deprecated; scripts/send_brief_email.py becomes the mailer | 74c4c5834; RECONSTRUCTION s2 | HIST
- 2026-05-17 | hist | Metis | manual_status.json per-cycle auto-stamp introduced | 0d2c7f015 | IMPL
- 2026-05-17 | memory | Hermes | agents/hermes deprecated by Aletheia; intelligence_loop 4-hour cadence; 'hermes' marker row in agora | pivot/hermes_deprecation_2026-05-17.md; ab55ea85e; agora.intelligence_outputs stage 'hermes' | IMPL
- 2026-05-17 | memory | Hermes | first "auto: portfolio update" commits | git log --grep | IMPL
- 2026-05-19 | hist | Metis | chain-of-thought strip; email 17K -> 3.5K chars | 52b844afa | IMPL
- 2026-05-19 | memory | Hermes | email cleanup strips Metis chain-of-thought inside the delivery layer | 52b844afa | IMPL
- 2026-05-23 | fleet | Pronoia lineage | orchestration_logging emit_event -> agora.intelligence_outputs | edefec3cf | IMPL
- 2026-05-23 | hist | Pronoia | PG dual-write heartbeat; first pronoia_* rows in agora.intelligence_outputs | 373d81469; DB min(started_at) 2026-05-23 | IMPL
- 2026-05-23 | hist | Metis | deterministic fallback when LLM rambles; personas not flagged | 65b6e0140 | IMPL
- 2026-05-23 | hist | Atalanta | Aporia creates Atalanta (with Hypatia, Pheme); daemon launched 04:28 -04 | e6b3746f0; agora atalanta_startup | IMPL
- 2026-05-23 | memory | Hermes | TypeError guard after silent multi-day send death; emit_event logging lands; first email_dispatched row | cce4505ed, edefec3cf; agora min(started_at) | IMPL
- 2026-05-24 | fleet | (unclaimed) | machine probes on M1-M4 begin writing agora.machine_probes; M1 task registered | 113720af4; DB min(taken_at) 2026-05-24 | IMPL
- 2026-05-24 | hist | Atalanta | first anti-silence alarm row (tick 50) | agora atalanta_self_audit_null min 2026-05-24 04:09 | IMPL
- 2026-05-26 | build | Hephaestus | last change to legacy loop hephaestus.py ("behavioral NCD") | 1a0614161 | IMPL
- 2026-05-28 | build | Hephaestus | last ledger row 01:44; last heartbeat at 0.6% forge rate; M3 goes down | ledger.jsonl; ROLE.md s1 | IMPL/HIST
- 2026-05-30 | coord | (agora schema) | 17 agora.agent_heartbeats rows last beat on this date | select last_heartbeat::date,count(*) | IMPL
- 2026-05-30 | fleet | (unclaimed) | last machine_probes rows for M1, M2, M3 (M4 continues); charon/hecate/moros/lethe ticks stop | DB max(taken_at); intelligence_outputs stages | IMPL
- 2026-05-30 | hist | Atalanta | last row of any kind (354th null tick; process killed) | agora max finished_at 12:10:49 -04 | IMPL
- 2026-06-10 | hist | Pronoia/Metis/Atalanta | program audit archives serial chain + Pronoia; Atalanta "starved by dead upstreams" | aporia/docs/program_audit_2026-06-10.md:130-136 | HIST
- 2026-06-23 | memory | Hermes | disposition plan proposes deleting Hermes ("needs James confirm"); never confirmed | pivot/COMPONENT_DISPOSITION_PLAN_2026-06-23.md | HIST
- 2026-06-24 | build | Hephaestus | M3 back; ROLE.md revamped "failure-mining instrument, measurement lab, metabolizer" | ROLE.md s0-s1 | HIST
- 2026-06-24 | coord | Ergon | Redis retired ("too difficult to keep running under WSL"); PgRedis on schema bus | c04199724 | IMPL
- 2026-06-24 | fleet | Agora | Redis retired (per Achilles reconstruction) | roles/Achilles/RECONSTRUCTION_2026-09-30.md s2 | HIST
- 2026-06-24 | hist | Pronoia | AI dossier: Era 2 "REFACTOR", claims dashboard fresh, detectors portable | pivot/COMPONENT_DOSSIERS_2026-06-24.md:608-615 | CORR
- 2026-06-24 | hist | Pronoia/Metis | Redis retired; state.json freezes (PgRedis lacks exists/hlen/zcard) | af9b4d9c9 message | HIST
- 2026-06-24 | memory | Mnemosyne | Redis and DuckDB retired (PgRedis bus, charon_duckdb mirror) -- recorded by Mnemosyne 09-01 | mnemosyne/STATE.md | HIST
- 2026-08-12 | build | Hephaestus | meta-assessment from the Fable seat + 14 domain surveys | a3e9bbee4 | HIST
- 2026-08-12 | hist | Metis | ruling "reporter tells the truth or is silenced"; M4 reporter confabulation named | metis_portfolio.py:453-456; roles/Hephaestus/META_ASSESSMENT_2026-08-12_fable_seat.md:286 | HIST
- 2026-08-17 | hist | Alethelia | charter ratified; name chosen against Aletheia collision | aporia/docs/germline_infrastructure_2026-08-17.md s6 | HIST
- 2026-08-18 | coord | Aporia | gemini_research_queue (423 prompts) filed | cf2438a5d | IMPL
- 2026-08-18 | fleet | Metis lineage | metis_portfolio made deterministic-first (METIS_LLM default off) after LLM chain-of-thought leaked into emails; 8-week frozen dashboard chain documented | af9b4d9c9; 71d809b49; scripts/metis_portfolio.py:452-458 | IMPL
- 2026-08-18 | hist | Metis | metis_portfolio deterministic-FIRST (LLM opt-in METIS_LLM=1) | af9b4d9c9 | IMPL
- 2026-08-18 | hist | Pronoia | M4 dashboard unfrozen after 8 weeks, verified through repo only | 71d809b49 | HIST
- 2026-08-19 | build | Hephaestus | ablation card: +11/+32pp reproduces on the forge's own ruler | 11e919e20 | REPORTED
- 2026-08-20 | hist | Alethelia | v0 built (P29); finds 31/34 heartbeat rows stale-online | 756b7cf16 | IMPL/REPORTED
- 2026-08-20 | hist | Atalanta | Aporia P47 autopsy counts 354 UPSTREAM_NOT_FOUND artifacts on M1 | roles/Atalanta/DEAD_GATING_SPECIMEN.md s1.1 | HIST
- 2026-08-20 | memory | Hermes | last email_dispatched row before a stage-name gap (pronoia_email_dispatched continues 09-01..09-08) | agora.intelligence_outputs | IMPL
- 2026-08-22 | build | program | prometheus_llm: one model API replacing seven client implementations | 25623303e | IMPL
- 2026-08-24 | coord | Aporia | standing loop stopped; CYCLE 152 closes P145-P151 arc; *.jsonl-only glob miss surfaced | aporia/docs/PROGRAM_SUMMARY_2026-08-24.md; 4ceeda03c | HIST
- 2026-08-25 | atlas | Atlas | commit harvest window start (--since default); git_commit min authored_at | atlas/__main__.py:30; atlas.git_commit | IMPL
- 2026-08-26 | coord | Aporia | mutable-language-of-thought charter | 72583930f | INTENT
- 2026-08-27 | hist | Alethelia | manual M1 run, not committed for 15 days | roles/Alethelia/notes/BOOTSTRAP_M1_2026-08-27.md | HIST
- 2026-09-01 | build | Hephaestus | external design review: generator dead, instrument alive; Hephaestus II proposed | c0954083b | HIST
- 2026-09-01 | build | Hephaestus | charter amendment Forge Queue + Master Smith; first loop built; MINT-0001 | 7b55e8423 | IMPL
- 2026-09-01 | build | Hephaestus | Addenda 1-4: semantic closure test, review-packet standing order, closure gauntlet standard test, scheduled tasks deleted | af31ddcda, 3c0f37a4c, b801ad3bd, 1f4c5ca72 | IMPL
- 2026-09-01 | memory | Mnemosyne | read-only world-state refresh; Evidence Wiki V0 built (ew schema, REST 8377, skill); G6 TENSOR_NOT_YET_JUSTIFIED | 60721f003, c711c5bf6 | IMPL
- 2026-09-02 | memory | Mnemosyne | V1 (metabolization not demonstrated, instrument saturated), V2 (retrieval without design advantage), V3 (MARGINAL, saturated); PEW FROZEN | 08b391ea7, d4da2f4f5, cb43847e9 | REPORTED
- 2026-09-03 | memory | Mnemosyne | reopened for Harmonia first integration; fossil contract v1; world-provenance seam pew.fossil.v2 | 1376df4fd, 4cb02c733 | IMPL
- 2026-09-04 | memory | Mnemosyne | PEW durability: verified backup + restore | 81b7aa2d4 | IMPL
- 2026-09-05 | atlas | Atlas | earliest indexed experiment activity (Vivarium queue) | atlas.experiment min(first_seen_at) | IMPL
- 2026-09-05 | memory | Mnemosyne | execution lineage (engine/session binding); Vivarium starts writing fossils | 5f8b70d7a; write_log vivarium min 09-05 | IMPL
- 2026-09-09 | fleet | (M4 loop) | portfolio_monitor/metis/email events stop (0 rows 09-09..09-10) | agora.intelligence_outputs per-day counts | IMPL
- 2026-09-09 | hist | Pronoia/Metis | last portfolio commit before gap (02:15Z); 0 pronoia_* rows 09-09/09-10 | 64de18126; agora | IMPL
- 2026-09-09 | memory | Hermes | portfolio brief producer stops (last auto-commit 64de18126); no email rows 09-09..09-10 | git; agora | IMPL
- 2026-09-10 | build | Daedalus | SFE M1 schema-8 deploy pinned in DEPLOYED_BUILD.json | d269c6c7a | IMPL
- 2026-09-11 | build | Hephaestus | base-role adoption, D-23 guard in 8 entry points; specimen 3 executed; gauntlet controls ALL_PASS; disposition ledger opened | a3960783e, deb9ca34a, d57a5c80e, 5d784becf | IMPL
- 2026-09-11 | build | Hephaestus | last Forge Queue job receipts (STATE.json 14:08Z) | hephaestus/STATE.json | IMPL
- 2026-09-11 | coord | base-role | base role created (103 base-role commits this day) | 249bb0f98; git log --format=%cs -- roles/base-role | IMPL
- 2026-09-11 | coord | Archaeon | comms queue revived in Postgres (D-24); agents table; D-25 presence from sync receipts; instances | 7466bd6ac, 9f6bc3ae8, 8bb162a77, 10b75cbb0 | IMPL
- 2026-09-11 | coord | base-role | MONITORS.md registry; rule 8 (scheduled activity is not progress); rule 10 (loop must not outlive usefulness) | 71a5e3341, 58fe2fc57, 7f68f5093 | IMPL
- 2026-09-11 | coord | Aporia | base-role adoption; seat file rewritten (APO-25); DISSENT_LEDGER | 7e2dbe0a9, 4305c1de9 | IMPL
- 2026-09-11 | coord | Archaeon | last change to DECISIONS.md register (D-1..D-29) | git log -1 -- archaeon/docs/expansion/DECISIONS.md = 10b75cbb0 | IMPL
- 2026-09-11 | coord | comms | busiest early day: 191 messages, 19 ack-kind | comms group-by day/kind | IMPL
- 2026-09-11 | fleet | Archaeon | comms revived in Postgres (messages/receipts/task_queue), then agents table, D-25 presence-from-sync, fail-closed host, identity guard, instance tags | 7466bd6ac, 9f6bc3ae8, 8bb162a77, 5f9d8ea7e, f7d7c2eac, 10b75cbb0 | IMPL
- 2026-09-11 | fleet | Archaeon | roles/base-role/MONITORS.md registry seeded from the M1 task list; self-test requires enabled tasks to have rows | 71a5e3341 | IMPL
- 2026-09-11 | fleet | (M4 loop) | portfolio loop resumes (2 events 09-11, then 6/day) -- contradicts MONITORS rows still saying DORMANT since 09-09 | agora.intelligence_outputs; roles/base-role/MONITORS.md rows "Portfolio brief producer", "MetisPortfolioBrief" | CORR
- 2026-09-11 | fleet | Alethelia | truthful reporter adopted, last committed stations/REPORT_latest (5 of 7 anomaly rules FIRED) | d2c54fa2b; stations/REPORT_latest.md:1-3 | IMPL
- 2026-09-11 | fleet | comms | busiest day before CWOs: 191 messages, 723 kB bodies | comms.messages per-day query | IMPL
- 2026-09-11 | hist | Atalanta | adopted, L-09 canonical git pull, specimen, rule-10 proposal, RETIRED same day | b33712c94, 827d021eb, 051304cd0 | IMPL
- 2026-09-11 | hist | Atalanta | base rule 10 adopted as D-27; D-28 producer-declaration opened | 7f68f5093 | IMPL
- 2026-09-11 | hist | Metis | seated, re-premised to composition by operator ruling | 82fbe180d, 962e4a186 | IMPL
- 2026-09-11 | hist | Pronoia | adoption; Era-1 audit autopsy; M2 ghost pronoia.py neutralised; PRON-03 work-aware heartbeat | 18fee46d0, 630f086df, 8b0cecadc | IMPL
- 2026-09-11 | hist | Alethelia | base-role adoption, v0.1 rules + 7 controls; wrong-directory run overwrites canonical stations/REPORT_latest | d2c54fa2b | IMPL
- 2026-09-11 | memory | Hermes | seated on M2 by operator; archaeology; identity guard built; comms wiring accepted (#73); convergence probe; HERMES-32 | da5d6880e, 88337a141, f7d7c2eac, 84cc58224, 283687393 | IMPL
- 2026-09-11 | memory | Hermes | asserts Agora "not fed"; corrected same day by Pronoia #91 | b026db8cc | CORR
- 2026-09-11 | memory | Mnemosyne | base-role adoption; boundary ruling D-23 amendment 3 (substrate science); store-identity guard in ew.db; Kairos read-only token | 4616c9797, 633f6989b; BACKLOG_H0H5 DONE rows cite a36a8234d, b08a4f0de | IMPL
- 2026-09-11 | memory | Hermes | last Hermes comms post (#118) and last seat activity | comms.messages; comms.agents | IMPL
- 2026-09-11 | memory | Hermes | mailer email rows resume (pronoia_email_dispatched + email_dispatched, 6-12/day) | agora.intelligence_outputs | IMPL
- 2026-09-12 | memory | Mnemosyne | Techne reports PEW tests rewrite tracked JSON receipts | INBOX_TECHNE_TEST_MUTATES_TRACKED_JSON_2026-09-12.md | HIST
- 2026-09-13 | hist | Metis | Season 1 prereg -> freeze -> closed SPECIMEN_SURVIVES_RETROSPECTIVE (narrowly) | a4f345aa7, 2a650277b, f9f90c0f7 | IMPL/REPORTED
- 2026-09-13 | memory | Mnemosyne | M1 PEWRestoreVerifyWeekly runs; Task Scheduler last result 1; MONITORS cites it as a good receipt | schtasks query 2026-10-01; MONITORS row 17 | CORR
- 2026-09-14 | atlas | Nyx | nyx/atlas/ ATLAS PASS 01 created (unrelated namesake of the later seat) | 65c319ef7 | IMPL
- 2026-09-14 | build | Nestor | RowWriter commit-on-write rows (primordial/fabric/rows.py) | 2d3122a5c | IMPL
- 2026-09-14 | build | Daedalus | M1 SFEngine scheduled task last run (now Disabled) | schtasks /query 2026-10-01 | IMPL
- 2026-09-14 | coord | Agora | adoption pass: 26 April items, 0 STILL_LIVE; AGORA-01 (retire?) to operator | 31f51c722, 8dc34fe32 | IMPL
- 2026-09-15 | memory | Mnemosyne | M1 handed to Nestor; last M1 watchdog read 17:11 -04; M1 PEW dormant | ccb26df01; ew.read_log | IMPL
- 2026-09-16 | build | Daedalus | SFE production moved to M2 on its own ledger; M1 candidate never deployed | CANDIDATE_BUILD.json SUPERSEDED_2026-09-16 | HIST
- 2026-09-16 | memory | Mnemosyne | PEW restored on M2 fronting the M1 store; qualified from M2; one watchdog script for both hosts | 1e0708472, 9ca1bcb91 | IMPL
- 2026-09-17 | atlas | Vivarium | last row created in viv.research_experiment_queue (1,242 total, all indexed) | viv.research_experiment_queue max(created_at) | IMPL
- 2026-09-17 | build | Daedalus | SFE 9.0.1 deployed on M2 (699ca0f9); NVMe long-run proof | 2983bd548, e7a699099 | REPORTED
- 2026-09-17 | coord | base-role | ONE COMMS DATABASE ON M1 ruling | dcd749ab7 | IMPL
- 2026-09-17 | coord | Pronoia/M4 | Agora heartbeat cadence slowed to 30 min on M4 | 6be994430 | IMPL
- 2026-09-17 | hist | Pronoia | M4 heartbeats slowed to 30 min; "M4 agents will read stale/offline" accepted | 6be994430 | IMPL
- 2026-09-17 | memory | Mnemosyne | O2 ruling MNE-D1: backup of record on M2; point release: migration 014 + campaigns 1-3 ingested (26,636) ; migration 015 applied from dirty tree | 67b6f7323, e8683ea3f; ew.schema_migrations | IMPL
- 2026-09-18 | atlas | Atlas | seat created, base role adopted, charter PENDING | f7283bc2e | IMPL
- 2026-09-18 | build | Bellerophon | prometheus/toolbox Worlds Kernel first commit | 4c0435544 | IMPL
- 2026-09-18 | fleet | (M4 loop) | M4 popups stopped; probe/heartbeats slowed to 30 min; last code change to intelligence_loop | 6be994430 | IMPL
- 2026-09-18 | hist | Pronoia/Metis | portfolio commits + successful cycles resume 6/day | git log docs/portfolio_brief.md; agora | IMPL
- 2026-09-18 | memory | Mnemosyne | Campaigns 4-5 ingested (cmp4 4,739, cmp5 1,563); C6 storage contract v0.1 design only; last seat commit and last ew write | f81ddddbe, 0d448387e, 8915b660f; write_log max | IMPL
- 2026-09-18 | memory | Hermes | portfolio brief auto-commits resume, ~6/day through 10-01 | git log --grep | IMPL
- 2026-09-19 | atlas | Atlas | operator charter committed verbatim | 4fb8c7fc2 | IMPL
- 2026-09-19 | atlas | Atlas | charter addendum (ran/observed/concluded, pointers, host/engine_instance) | cbe1d149d | IMPL
- 2026-09-19 | atlas | Atlas | migrations 001-005 applied, first populated pass (index v1) | 61c3985fc; atlas.schema_migrations; harvest_run 1-46 | IMPL
- 2026-09-19 | atlas | Atlas | first npe harvest FAILED (timestamp type), retried DONE on M1-local ref nestor/sidequest-graphworld-2026-09-14 | harvest_run 7-8 | IMPL
- 2026-09-19 | atlas | Atlas-M2 | seat created on M2 as a brother seat | 094d0558c | IMPL
- 2026-09-19 | atlas | Atlas | INSTANCES.md deleted, replaced by SIBLINGS.md after Atlas-M2 #499 | b8b6f8e59 | IMPL
- 2026-09-19 | atlas | Atlas | migration 006 seat coordination, advisory locks | 431a9d5ad | IMPL
- 2026-09-19 | atlas | Atlas | AtlasIndexLoop registered and launched | 542f31b91 | IMPL
- 2026-09-19 | atlas | Atlas-M2 | loop ticks 1-3: local_files + frontier_runs_m2 on M2 (harvest_run 90-133) | 658d6ebec, 3d1fa6f91, 2f4db08eb | IMPL
- 2026-09-19 | atlas | Atlas | AtlasIndexLoop PARKED by operator after 2 productive ticks | 55fb84c7b, f890b3d70 | IMPL
- 2026-09-19 | atlas | Atlas-M2 | comms loop PARKED (tick 4) | 442867f72 | IMPL
- 2026-09-19 | atlas | Atlas | ecosystem catalogue (352 external + 4 internal; 834 refs) by six web-survey subagents; migration 008 | 98972f55a | IMPL (commit) / HIST (method)
- 2026-09-19 | atlas | Bellerophon | atlas_bee froze a 6-experiment selection from read-only SELECTs on atlas | roles/Bellerophon/atlas_bee/SELECTION_FROZEN.json | IMPL
- 2026-09-19 | build | Hephaestus | xpol_2026 replay infrastructure; floors computed before any call | b826e6e32; floors.json | IMPL
- 2026-09-19 | build | Hephaestus | Fable small set done (credits exhausted at XP-036); groq arm rate-capped | c802db53b, 3eb954e16 | REPORTED
- 2026-09-20 | build | operator | Hephaestus 2.0 Gravity Pilot proposal committed on vivarium/v0-2026-09-05 | 68aab291f | INTENT
- 2026-09-21 | atlas | Atlas | prior-art raid: 34 proposals (incl. RA-1..RA-5), catalogue to 365, migration 009 | 2c7a19adb | IMPL
- 2026-09-22 | atlas | Nestor | primordial/ reaches origin/main by merge (ends "NPE only on M1-local branch") | b10161316 | IMPL
- 2026-09-22 | atlas | Atlas | newest modelled experiment activity in the index (19:07Z) | atlas.experiment max(last_activity_at) | IMPL
- 2026-09-23 | build | operator | same patch lands on main as 3faf6c98b (identical patch-id) | git patch-id | IMPL
- 2026-09-23 | build | Hephaestus | xpol session arm + 14B addendum: "size buys mechanism existence, not quality" | 9a4e3df54, 8d9e9ff6a | REPORTED
- 2026-09-23 | coord | Aporia | boot after 12-day ACTIVE gap (P182 09-11 -> P183) | roles/Aporia/STATUS.md:6-8 | HIST
- 2026-09-23 | memory | Mnemosyne | M2 watchdog parks after 12 non-productive ticks (search model not ready); posts #542; last read_log row | comms #542; ew.read_log | IMPL
- 2026-09-24 | atlas | Atlas | PROMOTION to research-policy layer (in place of a separate Metis seat); migrations 010-011; policy/1 then policy/2 | f8df65681 | IMPL
- 2026-09-24 | atlas | Atlas | policy/1 novelty 0.000 for all 46 proposals; identical horizons; lag 4.9 d misread as quiet engines (self-caught) | roles/Atlas/calibration/LEDGER.md | HIST
- 2026-09-24 | atlas | Atlas | reference harvest FAILED on FK home_host 'unknown' | harvest_run 204 | IMPL
- 2026-09-24 | memory | Mnemosyne | Vivarium reports PEW 8377 and SFE 8811 hung, M2 at 98% commit | comms #563 | HIST
- 2026-09-25 | atlas | Atlas | operator rulings: one pass then PARK; REPORTS ONLY; no interface requests | d5141caa9; journal/2026-09-25.md | HIST
- 2026-09-25 | atlas | Atlas | frontier/3 found to have indexed 299,991 identical suppression-echo facts (92% of CONCLUDED) | journal/2026-09-25.md | HIST
- 2026-09-25 | atlas | Atlas-M2 | pre-reboot save; 71 M2 receipts left uningested by decision | 53e071604 | IMPL
- 2026-09-25 | build | Hephaestus | session close on M2; OPEN_QUESTIONS Q1-Q8; seat last seen 06:53 | ff8d930ff, d22beca12; comms who | IMPL
- 2026-09-25 | build | Odysseus | seat created on ubu001 | fe38c055d | IMPL
- 2026-09-25 | coord | Cyclops | created on M2 15:24Z; charter (SI stewardship) 16:25Z | f4202098d, 608b672d5 | IMPL
- 2026-09-25 | coord | Aporia | paired with Cyclops (operator one-liner), 15:29Z | 04379db69 | IMPL
- 2026-09-25 | coord | Aporia+Cyclops | SI shared record skeleton 16:28Z; memo co-signed 19:16Z | e65b93070, d50103524 | IMPL
- 2026-09-25 | coord | Aporia | given HOLD-release / SI01 go / GPU-check gates over Ananke | f137e0e96; RULINGS.md 20:05Z | IMPL
- 2026-09-25 | coord | Cyclops | INCIDENT #585 exposed blind seat Bellerophon; DO_NOT_BRIEF + prepost_check built | 3de747dd8, add51a9a4 | IMPL
- 2026-09-26 | atlas | Atlas | ATLAS-37 Cosmos adapter (MANIFEST-verified, fail-closed); frontier/4 HELD | 7190591f4 | IMPL
- 2026-09-26 | build | Odysseus | charter: distributed brain; brain v0 GREEN; Windows receipt by Cyclops (71 passed) | bd76253c6, e731ac509, 428d4b442 | IMPL
- 2026-09-26 | coord | Aporia | C1b launch-guard false-release defect; exact release-token rule | 4f7836be3; RULINGS.md 05:45Z | IMPL
- 2026-09-26 | coord | Cyclops | PARKED by operator 06:26Z | 8083cdc1b | IMPL
- 2026-09-26 | coord | operator | steward management via comms FROZEN 13:04Z | b62b35eb2 (#732) | IMPL
- 2026-09-26 | coord | operator | all agents released from Aporia/Cyclops sign-off 13:16Z | 4f5d9bac8 (#733) | IMPL
- 2026-09-26 | coord | operator | "direct operator control" directives to Nestor and Ananke (C1B HOLD RELEASE) | 345e0ceef, f6fff610c | IMPL
- 2026-09-27 | build | Odysseus | brain lane FROZEN by operator; TH-006 slice; POI frontier program | 626d8c396, e40904023, ade0d6243 | HIST
- 2026-09-27 | build | Harmonia | GIT_NATIVE_EXISTING_MACHINERY inventory of queues/leases | c17d4c477 | IMPL
- 2026-09-27 | coord | Harmonia | Git-native lab control plane initiative captured as PILOT ONLY | c17d4c477 | IMPL
- 2026-09-27 | fleet | Harmonia | ops/ Git-native lab control plane initiative captured, PILOT ONLY | c17d4c477; ops/README.md | IMPL/INTENT
- 2026-09-28 | build | Odysseus | expeditionary role adopted; expedition 1 then FROZEN | 02800d2b5, 1abf82d0f | HIST
- 2026-09-28 | build | Odysseus | Agent Fabric v0 (A2A gateway, TCK MUST 65/65); v0.1; v0.2 lease canonical; FREEZE | 9ff7dd967, ee2948cab, 3ba6fcc0c, 54e42c695 | IMPL
- 2026-09-28 | build | Odysseus | lease cutover: Ananke/Nestor lease CLIs onto fabric row | 8370083ae | IMPL
- 2026-09-28 | build | Odysseus | S2 result: 0.28 vs 3.5 coordination actions per execution | 7421fa500 | REPORTED
- 2026-09-28 | build | Odysseus | promexec round-1 installed on ubu001 (NOT ENABLED); first fabric task 13:32 -0400 | 739ab28ed; fabric.tasks | IMPL
- 2026-09-28 | coord | Cyclops | MWO-0001 published as registrar (P 7e4c09f2c 21:48, R bd48fac9b, #914) | PUBLICATIONS.md | IMPL
- 2026-09-28 | fleet | operator/Cyclops | MWO-0001 published (CURRENT.md + archive), broadcast #914 | 7e4c09f2c; ops/work_orders/PUBLICATIONS.md | IMPL
- 2026-09-28 | fleet | comms | 145 messages, 37 broadcasts in one day (MWO adoption wave) | comms per-day query | IMPL
- 2026-09-29 | build | Odysseus | D2 firewall re-audits v2..v13 (FAIL x11 then PASS v13) | f8eedbbce .. 6f5ac3192 | REPORTED
- 2026-09-29 | build | Odysseus | DEF-ODY-015 ubu001 disk full failed 20 Tasks; repaired under FREEZE | 5266ccebe | IMPL
- 2026-09-29 | build | Odysseus | S3 result gate MET; corrected 0.33 -> 0.67 coordination/exec | b3974ed8b, 6f5ac3192 | CORR
- 2026-09-29 | coord | Aporia | MWO-0002 candidate, revision, publication (P 89512068f 02:56, R e9e169d01, #961) | 7c84a44b4, ed71a292d | IMPL
- 2026-09-29 | coord | Aporia | migration census self-report: bootstrap independence NO | adf21bba8 | IMPL
- 2026-09-29 | coord | Aporia | MWO-0003 published (P 624a686ea 07:14, R 9d86a303b, #987); FP-001 cold start PASS via own traces | f63a8589a | IMPL
- 2026-09-29 | coord | Aporia | MWO-0004 published 28 min after MWO-0003 (P 25a486d44 07:42, R 13de76162, #988) | PUBLICATIONS.md | IMPL
- 2026-09-29 | coord | base-role | boot step 1 reads CURRENT.md + WORK_STATE (R4); 2a work-conserving loop incl. H "no smart global scheduler" | 17e25e67b, 1e9042017 | IMPL
- 2026-09-29 | coord | fleet | 198 commits touch roles/*/WORK_STATE.json (84 of them state/journal/STATUS-only) | git log name-only analysis | IMPL
- 2026-09-29 | fleet | Aporia | MWO-0002, -0003, -0004 published same day (two-commit protocol) | 89512068f, 624a686ea, 25a486d44 | IMPL
- 2026-09-30 | atlas | Atlas | inference harvest unparked (until 2026-10-01 05:00 ET) | ea07398dc | IMPL
- 2026-09-30 | atlas | Atlas | frontier/4 + migration 013 collapse echoes: facts 333,044 -> 33,054, sources 313,015 -> 13,025 | 244ef7691; live counts | IMPL
- 2026-09-30 | atlas | Atlas | last full harvest pass (harvest_run 305-320, 22:15-22:17Z) | atlas.harvest_run | IMPL
- 2026-09-30 | atlas | Atlas | npe/5 auto-selected local nestor/d2v10..13-2026-09-29 refs | harvest_run 309-312 | IMPL
- 2026-09-30 | atlas | Atlas | synthesis F1-F8, two verifiers (32 confirmed / 25 corrected / 3 contradicted of 60), cross-model check via NIM | 7b06faae3, 777ac43dc, f6cfc9852 | REPORTED
- 2026-09-30 | atlas | Atlas | inference harvest complete; state READY | d95cffcc8 | IMPL
- 2026-09-30 | build | Odysseus | S3 corrections per Harmonia #1038; legacy lease detection removed; DEF-ODY-019/023 | 3eb8af06b, 9c022347e, c97fe81a5 | IMPL
- 2026-09-30 | build | Odysseus | promexec round-2 source pinned (3cf32a64); install BLOCKED on operator | 9f95f9ea0; WORK_STATE.json | IMPL
- 2026-09-30 | build | Odysseus | last fabric task created 11:32 -0400; last attempt ended 15:33Z | fabric.tasks / fabric.attempts | IMPL
- 2026-09-30 | coord | Aporia | CWO fleet activation 04:18: Aporia "fleet scheduler", auto-promotion; #1024 + 12 delegations; fleet_status.py | 6a7a84569 | IMPL
- 2026-09-30 | coord | Cyclops | observability audit F1-F7, then PARKED | 029dd5555 | IMPL
- 2026-09-30 | coord | Aporia | CWO-B 09:16 removes auto-promotion; 16 heartbeat prompts #1081-#1096 | d4e47ebf5 | IMPL
- 2026-09-30 | coord | Aporia | census after 1-h heartbeat window, 10/16 responded, 6 silent | 7cb91eaf9 | IMPL
- 2026-09-30 | coord | Aporia | CWO-C 13:55 governing; 6 VISIBILITY_STALE prompts; 4 dispatches | 7d373ac02; comms #1140-#1150 | IMPL
- 2026-09-30 | coord | Aporia | operator inference harvest directive and deliverables (P5 coordination churn "real") | 66fc8b1d0, 140a6612e | IMPL/REPORTED
- 2026-09-30 | coord | Achilles | 59-seat census live, every 6 h (host elsa, not M1) | 189e12502, 49aac03d0 | IMPL
- 2026-09-30 | fleet | Aporia | CWO fleet activation + fleet_status.py + QUEUE.json | 6a7a84569 | IMPL
- 2026-09-30 | fleet | Aporia | CWO-30B finish-in-place + CENSUS.json v1 scaffold; CWO-30C governing order (heartbeat every 90 min) | d4e47ebf5, 7d373ac02 | IMPL
- 2026-09-30 | fleet | comms | 174 messages; 66 with "heartbeat" in subject | comms per-day query | IMPL
- 2026-09-30 | fleet | Achilles | seat created on ELSA (charter pending) | d56ac4937, 090317f9f | IMPL
- 2026-09-30 | fleet | Achilles | charter adopted: census engine, rules, registry, mailer section, MONITORS row, 6-hourly task | a797beabd | IMPL
- 2026-09-30 | hist | all four | Achilles census: Metis RETIRED, Atalanta RETIRED, Pronoia DORMANT(Uncertain), Alethelia DORMANT | a797beabd; docs/fleet/FLEET_CENSUS.md:60,77,81,82 | IMPL
- 2026-09-30 | memory | Hermes | Achilles adds fleet-census block to send_brief_email.py (file "claimed by Hermes"); notice #1224 unseen by Hermes | a797beabd; comms #1224 | IMPL
- 2026-09-30 | memory | Mnemosyne | keepalive fix to ew/db.py by another lane on unmerged branch; census labels Mnemosyne ACTIVE from it | 2c8c81bbb (not ancestor of bed05507a); docs/fleet/fleet_state.json | CORR
- 2026-10-01 | atlas | Atlas | crawl: index lag 8.58 d vs roles/Nestor HEAD; 8.13 d by Atlas's own metric; index age 11.3 h | this crawl | IMPL
- 2026-10-01 | build | Odysseus | D2 rulings on Nestor #1218/#1220: NO_INFORMATION | 76059a9f0, a336f6e73 | REPORTED
- 2026-10-01 | build | Odysseus | fabric workers ubu001 .a/.b/.sci online and idle at 09:40Z | fabric.agent_instances | IMPL
- 2026-10-01 | coord | Bellerophon | 14 hourly "no change" HEARTBEAT reports to Aporia 09-30 15:17 .. 10-01 05:31 | comms query | IMPL
- 2026-10-01 | coord | Ixion | crawl at bed05507a | -- | IMPL
- 2026-10-01 | fleet | Achilles | first census (deep, 59 seats, 28 anomalies, 40 s) pushed by the scheduled task | 189e12502; roles/Achilles/census/runs/2026-10.jsonl | IMPL
- 2026-10-01 | fleet | Hermes/M4 loop | 04:15Z brief email carried census 03:46:12Z (receipt tag) | agora.intelligence_outputs email_dispatched | IMPL
- 2026-10-01 | fleet | Achilles | second census (incremental, 4 commits, 27 s); mailer.census_included_last=true | db657a6df; docs/fleet/fleet_state.json | IMPL
- 2026-10-01 | fleet | (M1 host) | PrometheusMachineProbeM1 still enabled and failing every 5 min (0x80070002) ~4 months after last row | schtasks /query; agora.machine_probes | IMPL
- 2026-10-01 | hist | Pronoia | heartbeat health 'productive' (PRON-03 live on M4); brief lists Pronoia "DEAD" at 23 min | agora.agent_heartbeats; docs/portfolio_brief.md e9cf5ee16 | IMPL
- 2026-10-01 | hist | Pronoia | PrometheusMachineProbeM1 still failing (Last Result -2147024894) | schtasks /query on M1 | IMPL
- 2026-10-01 | memory | Hermes | mailer still sending (last 08:15Z, census tag age_h=3.7) | agora.intelligence_outputs | IMPL
- 2026-10-01 | memory | Mnemosyne | PEW not answering on M2 or M1 health endpoints; M1 PEW tasks Disabled | curl; schtasks | IMPL