# Seat dossier: Hephaestus (the Forge)

- Crawler label: build (Ixion sub-crawler; seats Hephaestus + Odysseus)
- Date: 2026-10-01 (date -u at write: Thu Oct 1 09:46 UTC 2026)
- Base SHA read: bed05507a (origin/main, 2026-10-01 05:34 -0400), worktree F:/Prometheus-worktrees/ixion-phase3
- FULLY READ: roles/Hephaestus/{ROLE.md, RESPONSIBILITIES.md, STATUS.md, TODO.md, OPEN_QUESTIONS_2026-09-25.md,
  DISPOSITION_LEDGER.md, BACKLOG_H0H5.md}; hephaestus/{README.md, STATE.json, workspace_guard.py, jobs/register_tasks.ps1};
  hephaestus/xpol_2026/README.md (first 60 lines); HEPHAESTUS_2_0_GRAVITY_PILOT.md (all 328 lines skimmed, ~200 read).
- SAMPLED: hephaestus/src/{apprentice.py:1-80, closure_test.py:1-60, packet.py:38-60}; DESIGN_REVIEW_2026-09-01_external.md
  (headings + s0-s1); agents/hephaestus (17,364 tracked files): structure counts, ledger.jsonl parsed in full (6,661 rows),
  3 forged tools opened (forge/, forge_v7/, forge_v9/), regex/zlib census by grep over every generation dir, one
  humanreadable/ report; forge/ (1,124 files): README, tester.py:425-450, all 203 verdict JSONs parsed for verdict field;
  xpol_2026 floors.json + runs/*/results.jsonl row counts + shape.py header.
- NOT READ: CHARTER_AMENDMENT_2026-09-01 body (449 lines; only via README/RESPONSIBILITIES summaries),
  META_ASSESSMENT_2026-08-12, FORGE_NEXT_LEVEL_STRATEGY_2026-06-27, journals 09-11/09-19 in full, the 14 surveys,
  review packets, forge/v2 + v3 code, diversity_forge/seed_forge/composer, most of agents/hephaestus/src (37 files),
  stations/M3_STATUS.md, roles/PipelineOrchestrator/. No comms bodies read (only `python -m comms who`).
- Nothing executed except read-only git, grep, JSON parsing and `python -m comms who`.

## 1 Charter and role history

- [HIST] Origin 2026-03-24: commit 2f3e4eb6f "Ignis v2 + Nous + Hephaestus" creates agents/hephaestus/; da42cc7e0 (03-25)
  "Forge pipeline v2: Coeus causal intelligence, NCD baseline, 15-trap battery, continuous operation". The forge is a
  March-May 2026 artifact, not a May one: ledger timestamps run 2026-03-24T13:20 .. 2026-05-28T01:44 with 4,469 of 6,661
  rows in March, 436 April, 1,756 May [IMPL computed by parsing agents/hephaestus/ledger.jsonl].
- [INTENT] Original charter: three-tier "evolutionary ratchet" (forge/README.md:1-50): Nous mines concept triples, Hephaestus
  forges Python ReasoningTool classes via API, battery validates, Nemesis co-evolves adversaries; T2/T3 compose prior tiers.
- [HIST] 2026-06-24 ROLE.md filed/revamped on M3 GANDALF after the M3 power outage (~05-28 to 06-24); previous authority
  was roles/PipelineOrchestrator/ (ROLE.md:7-10, s11).
- [HIST] 2026-08-12 a3e9bbee4 meta-assessment from "the Fable seat" + 14 domain surveys (roles/Hephaestus/surveys_2026-08-12/).
- [HIST] 2026-09-01 c0954083b external design review: "the generator is dead by measurement, the instrument is not"; proposes
  "Hephaestus II". Same day 7b55e8423 charter amendment (Forge Queue + Master Smith), Addenda 1-4 (af31ddcda, 3c0f37a4c,
  b801ad3bd, 1f4c5ca72): two regimes (Apprentice = cheap/local models, Master Smith = operator-invoked premium agent),
  Mint Packets, closure gauntlet as standard test, NO scheduled tasks (Addendum 4).
- [HIST] 2026-09-11 a3960783e base-role adoption; operator rulings recorded verbatim (5d784becf, RULINGS_2026-09-11.md);
  ruling 6: OPERATOR-class findings route to ENGINE/SFE + Archaeon, never Apollo (BACKLOG_H0H5.md HEPH-17).
- [HIST] 2026-09-19..23 temporary operator mission "cross-pollination replay" (xpol_2026; b826e6e32 .. 8d9e9ff6a).
- [INTENT] 2026-09-20 "Hephaestus 2.0 Gravity Pilot" proposal (operator-authored, co-author line Claude Haiku 4.5):
  commit 68aab291f on branch vivarium/v0-2026-09-05. [IMPL] 68aab291f is NOT an ancestor of bed05507a, but its patch
  reached main as 3faf6c98b (author date 09-20, commit date 09-23); `git patch-id` is identical
  (432612122dae...) for both. roles/Hephaestus/HEPHAESTUS_2_0_GRAVITY_PILOT.md and TODO.md are therefore on main.
- [HIST] 2026-09-25 ff8d930ff/d22beca12 session close on M2: STATUS rewritten, OPEN_QUESTIONS Q1-Q8 with defaults.
- [CORR] Current seat state is described two ways on main: TODO.md (operator, 09-20) "Hephaestus paused pending decision on
  2.0 pilot viability"; STATUS.md (seat, 09-25) "awaiting operator answers... default if silent: HEPH-32". Neither cites
  the other. [IMPL] comms `who` (2026-10-01): Hephaestus last seen 2026-09-25 06:53 (instance m2-0ee6272b, model
  claude-opus-5), 0 instances live.

## 2 Systems maintained

1. Legacy T1 forge loop agents/hephaestus/src/hephaestus.py (2,757 lines per ROLE.md s7) -- [HIST] RETIRED as a process
   (DISPOSITION_LEDGER.md row "legacy T1 loop").
2. 1.0 instruments embedded in agents/hephaestus/src: validator.py, test_harness.py, trap_generator*.py (the 186-trap
   honest ruler), knockout_ablation.py, behavioural NCD (hephaestus.py:689-826 per ledger), forge_primitives.py (25 fns).
3. Forge tiers forge/v2 (T2), forge/v3 (T3), forge/tester.py, forge/amino_acids/ (decomposed pgmpy/pysat/constraint/nashpy
   primitives), forge/tester_quarantine/ (trap generators firewalled from the builder).
4. Forge Queue hephaestus/ (Sept 2026): packet.py (13-state machine), triage/apprentice/refine/rank/handoff jobs,
   run_candidate.py (AST allowlist subprocess runner), closure_test.py (closure gauntlet), closure_q045*.py,
   semantic_closure.py, gauntlet_controls.py, closure_specs/ (frozen basis A2-GENERIC-v1), counterfeit_museum/,
   WALL_TAXONOMY_v1.md, STATE.json, HEPHAESTUS_HANDOFF.txt.
5. xpol_2026 replay harness: extract.py, replay.py, floors.py, shape.py, report.py, legacy_helpers.py (AST-extracted from
   hephaestus.py), templates/ (era-matched prompts with sha256).
6. The Apollo feed apollo/src/hephaestus_ops.py (9 @blackboard_op ops, generated by agents/hephaestus/src/blackboard_adapter.py)
   -- owned by Apollo's tree, maintained by this seat's disposition.

## 3 Actual implementation paths

- [IMPL] hephaestus/src: 18 files, 2,673 lines incl. state.py/workspace_guard.py (wc -l). Largest: wall_vacuous_truth.py 366,
  closure_q045.py 249, closure_test.py 244, apprentice.py 195, semantic_closure.py 191, triage.py 187.
- [IMPL] hephaestus/ tracked files 634: xpol_2026 527, mint_queue 37, deep_mint_sessions 19, src 18, closure_results 12,
  jobs 6, prereg 5 (git ls-files | awk).
- [IMPL] agents/hephaestus tracked files 17,364: humanreadable 11,351; scrap 2,648; scrap_staging 1,261; forge 734;
  forge_v4 375; forge_v5 367; forge_v3 333; runs 82; forge_v7 65; forge_v2 50; src 37; forge_v9 15; tier_specialists 14;
  forge_v8 5; forge_v6 2 (git ls-files | awk -F/ '{print $3}'). By extension: 9,420 .md, 5,274 .py, 2,582 .json.
- [IMPL] agents/* is gitignored (.gitignore:232 `agents/*`); the tracked tree was force-added (4ad7f3a78 message says
  "force-add into ignored dir"). New output written there is untracked by default.
- [IMPL] forge/ tracked 1,124: candidates 605, v2 257, verdicts 203, v3 31, amino_acids 6, tester_quarantine 2, plus
  tester.py, runner.py, builder.py, thresholds.py, llm_client.py, null_baselines.json.

## 4 Architecture

- [IMPL] 1.0 (Mar-May): concept triple -> Nous LLM analysis (humanreadable/*.md report, e.g. "Nous Model:
  nvidia/nemotron-3-super-120b-a12b") -> CODE_GEN LLM writes `class ReasoningTool` with evaluate(prompt, candidates) and
  confidence() -> validator gates -> trap battery -> ledger row forged|scrap.
- [IMPL] What the forged tools actually are (verified by reading 3 and grepping all): text-answer scorers built from regex
  token extraction + zlib NCD + hand-written heuristics. Sample forge/embodied_cognition_x_hebbian_learning_x_neuromodulation.py
  (189 lines): `_extract_structure` via re.findall, `_compute_ncd` via zlib.compress, "Dopamine" bonus = token overlap;
  its JSON records test_accuracy 0.267. forge_v7/dual_process_theory_x_predictive_coding_x_property_based_testing.py: 20+
  hard-coded puzzle-family handlers (_batball, _allbut, _pig, _fence, _bayes, _parity) + _ncd. forge_v9 tool imports
  forge_primitives (solve_constraints, solve_sat, bayesian_update) + _ncd.
  Census (grep -l over *.py per dir): forge 366 py, 340 contain zlib/NCD, 321 use re; forge_v3 302/299/300; forge_v4
  358/354/352; forge_v5 344/343/344; forge_v7 65/65/65; forge_v9 15/15/15; scrap 1,130/1,025/1,098. The "5 mechanisms in
  costumes" claim (ROLE.md s2) is consistent with this census [INFER: grep presence, not mechanism equivalence].
- [IMPL] Sept Forge Queue: wall -> typed semantic spec (closure_specs/<wall>.py) -> closure gauntlet arms A0 (frozen
  primitives), A1 (+routing), A2 (+frozen generic basis A2-GENERIC-v1, hash 7f2ef69196e7f128), B (small generic language)
  -> ROUTE_CLASS {SEARCH_ROUTING | REPRESENTATION | OPERATOR} + CLOSURE_MARGIN {A0|A1|A2_ONLY|NONE}; only OPERATOR may reach
  APPRENTICE-TESTING (closure_test.py:1-30 docstring; hephaestus/README.md "Rules this code enforces mechanically").
  Membership is extensional: typed + verify_exhaustive (+ verify_shift = robust).
- [IMPL] Apprentice: cheap models only ("nvidia:nvidia/nemotron-3-super-120b-a12b" 180 s, "ollama:phi3" 900 s);
  `_assert_cheap` refuses prefixes claude/anthropic/openai:gpt-5/openai:o (apprentice.py:26-36); code is executed in a
  subprocess against the wall harness; "explanations are stored, never trusted".

## 5 Data stores

- [IMPL] agents/hephaestus/ledger.jsonl: 6,661 rows = 385 forged / 6,276 scrap; scrap reasons: api_call_failed 2,861,
  validation 819, the rest trap_battery_failed at various accuracies (parsed). [CORR] So 43% of all ledger rows are
  instrument (API) failures recorded as subject outcomes -- also stated by Coeus #83 / DISPOSITION_LEDGER last row
  ("2,176-2,861 rows are instrument state").
- [IMPL] agents/hephaestus/novelty_scores.json (412 rows per xpol README), failure_mining_results.json,
  ablation/knockout_2026-08-20.json, runs/ (82 files, 2026-03-24/25).
- [IMPL] forge/verdicts/*.json: 203 files; verdict field: FAIL_BATTERY 176, FAIL_DIVERSITY 19, PASS 3, missing 5.
- [IMPL] hephaestus/mint_queue/MINT-000{1..4}/{packet.json, packet.md, events.jsonl}: events 23/1/1/10 lines.
  ROUTE_CLASS: 0001 REPRESENTATION (closure SEARCH_ROUTING, margin A1), 0002 SEARCH_ROUTING (IQ-PORT-1), 0003
  REPRESENTATION (parser gap), 0004 SEARCH_ROUTING (margin A2_ONLY). Last event timestamps 2026-09-01; STATE.json last
  update 2026-09-11T14:08:13Z.
- [IMPL] hephaestus/xpol_2026/runs/*/results.jsonl: O_all 114, cheap_all 351, fable51_small 30, fable51_s0 9 (no DONE),
  s1 7 (no DONE), s2 9, small_model 5, pilot 3, pilot_cheap 6, session 3 (no DONE).
- No Postgres schema owned. [IMPL] ROLE.md s9 lists Postgres/bus dependencies (prometheus_fire, PgRedis) for the 1.0 loop.

## 6 APIs/interfaces

- [IMPL] `ReasoningTool.evaluate(prompt, candidates) -> [{candidate, score, ...}]`, `confidence(prompt, answer)` (1.0 tools).
- [IMPL] CLI: `python -m hephaestus.src.{triage,apprentice,refine,rank,handoff}`; `python -m hephaestus.src.closure_test
  <spec> [budget]`; xpol `python hephaestus/xpol_2026/shape.py [--orig]`.
- [IMPL] Typed op interface for the apprentice: `def op_<wall>(state)` reads state.problem_text, writes state.comparison
  (apprentice.py:47-52 prompt text).
- [IMPL] apollo/src/hephaestus_ops.py: 9 @blackboard_op ops with OP_TIERS (DISPOSITION_LEDGER row; not opened by me).

## 7 Scheduling model

- [IMPL] None by policy. hephaestus/jobs/register_tasks.ps1 deletes Hephaestus_Apprentice/Refine/Rank tasks if present and
  prints "no Hephaestus scheduled tasks (by policy, Addendum 4)". Jobs run by hand.
- [HIST] 1.0 loop ran "24/7 via API" on M3 (forge/README.md T1 row), dead since ~2026-05-28 (ROLE.md s1).
- [IMPL] schtasks on M1 (2026-10-01): no Hephaestus/forge task found (filtered query).

## 8 State machine

- [IMPL] packet.py:40-50: OBSERVED, TRIAGE, COMPOSITION-SUSPECTED, EXPRESSIVITY-SUSPECTED, APPRENTICE-TESTING,
  APPRENTICE-EXHAUSTED, READY-FOR-DEEP-MINT, DEEP-MINTING, CANDIDATE-PRODUCED, INDEPENDENT-EVAL, ADMITTED, SCRAPPED, DORMANT.
  READY_REQUIRED lists 27+ fields (packet.py:52-60) that must be non-empty. refine.py enforces: READY only after >=4 executed
  attempts, >=2 models, >=2 failure families; cheap-model pass -> CANDIDATE-PRODUCED never ADMITTED (README).
- [HIST] No packet has completed a cycle (DISPOSITION_LEDGER "claim untested: no packet has completed a cycle").

## 9 Communication channels

- comms (Postgres on M1) via `python -m comms sync Hephaestus` (RESPONSIBILITIES boot step 5). [HIST] HEPH-05 posted to
  Archaeon; Archaeon comms 31 accepted ARCH-27; Coeus #83 answered via comms 515 (STATUS.md).
- Review packets committed under roles/Hephaestus/REVIEW_PACKET_*.txt (6 files) -- standing order Addendum 2.
- prompts/ manifests for outbound reports (roles/Hephaestus/prompts/2026-09-11_*/).

## 10 Failure recovery

- [IMPL] Every state-writing hephaestus/src module calls workspace_guard.refuse_canonical() (wraps archaeon.workspace
  assert_not_canonical) and stamps a workspace receipt (STATE.json shows base_sha/branch/worktree/dirty per job).
- [IMPL] STATE.json records last_run_at/last_input_at/last_success_at + explicit NO-OP reasons (HEPH-11).
- [HIST] 1.0 loop: checkpoint/resume modes, 4-model API fallback with hard timeouts (DISPOSITION_LEDGER legacy row).
- [IMPL] "A frozen result is never replaced; a rerun is a versioned characterization" (RESPONSIBILITIES prereg checklist);
  practiced: closure_q045_v2.py beside v1 (Z7 shift), b_ops v1 kept frozen.

## 11 Persistence

Git-only (JSON/JSONL/MD in repo). No DB. [IMPL] dirty=true in every STATE.json receipt (the worktree was dirty when jobs
ran) -- receipts therefore do not pin a clean tree.

## 12 Provenance

- [IMPL] Workspace receipts per job; xpol templates sha256 MANIFEST; xpol packets carry original code sha256 (68 of 114 per
  README); 26 honest-era (Apr/May) tools "were forged on M3 and never committed -- their ledger rows survive, their code
  does not" [HIST xpol README].
- [IMPL] Evidence grades E0/E1/E3 on every DISPOSITION_LEDGER row; DESIGN_REVIEW grades every headline number.
- [CORR] ROLE.md s0 "0.725 bits MI" is errata'd: it belongs to prometheus_math substrate kills, not the forge ledger
  (ROLE.md ERRATA (1)); tier profile R5 0/R6 ~7 corrected to R5 18.75/R6 38.1 (ERRATA (2)); "12 models converge" -> 5
  produced usable tools (ERRATA (4)).

## 13 Resource usage

- [HIST] M3 GANDALF: GTX 1070 8 GB, 8 cores, 25.8 GB RAM (ROLE.md s1). Later M1 (09-11) and M2 SPECTREX5 (09-19..25).
- [HIST] Inference: 1.0 = NVIDIA NIM nemotron-120b / Qwen-397B + fallbacks; 2,861 api_call_failed rows. xpol: Fable 5.1 via
  `claude -p` subscription "ran dry" after 10 packets; groq rate-capped at 12; GPT-6 Astra blocked (openrouter 402);
  gemini 503 (STATUS.md). No token counts recorded in what I read [UNK].

## 14 Model/inference dependency

- 1.0 generator: MODEL_MEDIATED (every tool is LLM-written). 1.0 scoring/validation/knockout/behavioural NCD: INFERENCE_FREE.
- Forge Queue: triage/refine/rank/handoff/closure gauntlet/controls: INFERENCE_FREE. Apprentice: MODEL_MEDIATED (cheap models)
  with deterministic execution judging. Master Smith: MODEL_MEDIATED (premium, operator-only).
- xpol: generation arms MODEL_MEDIATED; floors/shape/report/rescoring INFERENCE_FREE.
- Gravity pilot (proposal): MODEL_MEDIATED at both generation and "gravity assay" (a second model judges ancestry).

## 15 Human dependency

- [IMPL] Premium escalation operator-only (charter s3; apprentice refuses premium). Q1-Q8 in OPEN_QUESTIONS await the
  operator; the seat has been idle since 09-25 pending them. M3 hardware recovery (CMOS) was human. Credentials/funding
  (Astra) are operator decisions.

## 16 Major outputs

- [REPORTED] +11.1pp R3 / +32.1pp R4 from two hand-built engines (Probabilistic-Fallacy, Temporal-Computation), reproduced
  2026-08-19 "on the forge's own ruler; oracle cannot grade it" (11e919e20, ABLATION_CARD_2026-08-19.md). Not re-run since
  (HEPH-20 open).
- [REPORTED] Decorative-mechanism detection / knockout protocol (EPMC "96% regex") -- ROLE.md s2.
- [IMPL] forge_primitives.py 25 functions consumed outside the forge: 62 *.py files outside forge/ and agents/ reference
  `forge_primitives` (apollo/archive 23, apollo/src 7, aporia/iq 4, hephaestus/src 7, xpol 19, roles/Lexis 2; git grep).
- [REPORTED] Closure gauntlet specimen 3 (Q045): LOST 18 OPERATOR / 2 INCONCLUSIVE(B) / 0 SEARCH_ROUTING; controls ALL_PASS
  (deb9ca34a, d57a5c80e); fixture delivered to Archaeon (ARCH-27).
- [REPORTED] xpol: "size buys mechanism existence, not quality"; paired vs 1.0 originals 2-1 for originals (STATUS.md).
- [IMPL] floors.json (2026-09-19): 186 traps / 89 categories; chance 0.3238; NCD baseline 0.3925; position-majority decoy
  0.4032 (README) -- a constant-index decoy beats the 1.0 pass comparator.

## 17 Known failures

- [IMPL] forge/tester.py:442-446: FAIL_ABLATION verdict exists; 0 of 203 committed verdicts carry it (grep). DESIGN_REVIEW
  s1 attributes this to a concentration test that an all-zero tool passes by construction [REPORTED, Lexis G1].
- [IMPL] T2: 3 PASS of 203 verdicts; [HIST] T3 never launched (ROLE.md s5).
- [IMPL] 2,861 api_call_failed rows mixed with subject outcomes; no battery-version field.
- [HIST] 1.0 validator admits constant-output tools; 14B replay reproduced the class (OPEN_QUESTIONS Q7).
- [HIST] Closure gauntlet frozen after two boolean specimens with a bool() coercion degenerate on vectors (DISPOSITION row 1);
  Q045 v1 shift column outside Z6 caused 4 false negatives (d57a5c80e).
- [HIST] 1.0 Nous queue exhaustion: forge rate 0.6% (467 scraps / 3 forges) at last heartbeat 2026-05-28 (ROLE.md s1).

## 18 Pivots

1. 03-24 generator ("mass-produce novel reasoning algorithms") -> 2. 06-24 "failure-mining instrument + measurement lab +
metabolizer" (ROLE.md s0) -> 3. 09-01 Forge Queue / Apprentice vs Master Smith, closure gauntlet as standard test ->
4. 09-11 base-role, disposition ledger, "falsification has jurisdiction over claims, not machinery" -> 5. 09-19 proposed 2.0
"boundary certifier + mechanism assay" (seat) vs 09-20 "Gravity Pilot" (operator) -> paused.
[CORR] The two 2.0 framings coexist on main without reconciliation (STATUS.md vs TODO.md/GRAVITY_PILOT).

## 19 Journals/TODOs/backlogs

- roles/Hephaestus/BACKLOG_H0H5.md: HEPH-01..36; open include HEPH-08, 12-16, 18-20, 22, 26, 27, 29, 30, 32, 34-36.
- OPEN_QUESTIONS_2026-09-25.md Q1-Q8 (defaults stated). TODO.md (Gravity Pilot proposal). journal/2026-09-11, 09-19.
- agents/hephaestus/STATUS.md (06-26, pointer to stations/M3_STATUS.md), REPAIR_SCORECARD.md, MODEL_COMPARISON_REPORT.md.

## 20 Historical relevance to current Prometheus

- [INFER] The 1.0 corpus (5,918 Nous rows, 6,661 ledger rows, ~2,000 tool files, humanreadable reports) is the program's
  largest record of what cheap LLM generation produces under a fixed prompt; xpol and the Gravity Pilot both treat it as a
  frozen baseline.
- [IMPL] The closure gauntlet and the counterfeit museum are the only Hephaestus components with executed positive/negative/
  cheat controls (gauntlet_controls.py; STATE.json "ALL_PASS").

## 21 Inference-dependency classification

| function | class | evidence |
|---|---|---|
| trap battery scoring (186-trap ruler) | INFERENCE_FREE | trap_generator_extended seed=42; floors.json |
| validator gates / run_candidate AST allowlist | INFERENCE_FREE | forge/tester.py; hephaestus/src/run_candidate.py |
| knockout / ablation of tool mechanisms | INFERENCE_FREE | agents/hephaestus/src/knockout_ablation.py (11e919e20) |
| behavioural NCD novelty | INFERENCE_FREE | hephaestus.py:689-826 (per DISPOSITION_LEDGER) |
| mechanism-costume fingerprint | INFERENCE_FREE | hephaestus/xpol_2026/shape.py (AST + regex counts) |
| closure gauntlet route classification | INFERENCE_FREE | closure_test.py; closure_results/*.json |
| packet state transitions / ranking / handoff text | INFERENCE_FREE | refine.py, rank.py, handoff.py; STATE.json |
| triage of a wall into a packet | ASSISTED_PLAUSIBLY_DETERMINISTIC | triage.py idempotent for known walls; new walls need a spec written |
| writing a typed closure spec for a new wall | OCCASIONAL_JUDGMENT | closure_specs/*.py are hand-written |
| apprentice mechanism attempts | MODEL_MEDIATED | apprentice.py (NIM, ollama) |
| Master Smith minting | MODEL_MEDIATED | deep_mint_sessions/20260901T073136Z |
| 1.0 tool generation (Nous + CODE_GEN) | MODEL_MEDIATED | ledger.jsonl, humanreadable/ |
| gravity assay (proposed) | MODEL_MEDIATED | HEPHAESTUS_2_0_GRAVITY_PILOT.md |
| disposition / charter decisions | OCCASIONAL_JUDGMENT | DISPOSITION_LEDGER, OPEN_QUESTIONS (operator) |

## 22 False-negative / false-positive watch

- FN: [INFER] The 1.0 generator verdict ("0 working R3+ algorithms") was measured on a battery where a position-majority
  decoy (0.4032) beats the NCD pass comparator (0.3925) and 2,861 of 6,661 attempts died of API failure, not of the idea.
  The ruler and the instrument failure rate both bias toward "nothing works"; the xpol replay addressed some of this but
  ran 3-30 packets per arm.
- FN: [HIST] Apollo feed: the one-experiment falsification (does one R2 transformer give load-bearing composition?) never ran
  (ROLE.md s4; DISPOSITION "claim OPEN"). Death by ruling 6 (rerouting), not by evidence.
- FN: [HIST] T3 never launched; T2 judged with a FAIL_ABLATION gate that never fired -- the T2 verdicts are about the
  battery threshold, not about mechanism.
- FN: [HIST] Mint queue dormant since 09-11; "claim untested: no packet has completed a cycle".
- FP: [REPORTED] +11/+32pp is on the forge's own ruler ("oracle cannot grade it"); 85% structured vs ~35% NL composed tool is
  a 7-engine figure (ERRATA (7)). 1.0 forged tools' 15-trap certificates "shown vacuous by the Necropolis, 2026-09-10"
  (xpol README). The ~1,960 "tools" headline was a file count.
- FP: [REPORTED] xpol Fable 5.1 "two tools >= 0.50" are n=1 draws per packet; seat itself calls it "inside noise".
