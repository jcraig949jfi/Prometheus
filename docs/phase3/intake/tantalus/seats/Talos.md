# Talos -- Phase 3 intake dossier

Seat: Talos
Crawler: Tantalus (worker)
Tree SHA: 21a47402a (origin/main)
Date: 2026-10-01

Summary. Talos was chartered by Aporia on 2026-05-23 as a "reasoning-code
specialist": a small coder model (Qwen2.5-Coder-1.5B) to be LoRA-tuned on a
corpus of Prometheus "reasoning code" and tested on four capability targets
[INTENT] (agents/talos/CHARTER.md). What was BUILT is only Phase 0: an hourly
daemon that walks Python files with `ast`, extracts every function body with
its docstring, dedups by fingerprint and appends to JSONL shards [IMPL]
(agents/talos/daemon.py:325-451). It ran 170 ticks (160 null) between
2026-05-23 and 2026-05-30 and produced 24,847 rows from two of five streams
[RESULT-UNVERIFIED, but row counts re-verified by the seat 2026-09-11]
(agents/talos/corpus/manifest_latest.json; roles/Talos/STATUS.md). No model
was ever trained, no grader exists, the eval set is 5 hand-written cases, the
Apollo-organism stream was a stub that can return nothing, and no consumer
ever read the corpus. On 2026-09-11 the seat was reanimated under the base
role, preserved the shards byte-identically, and measured them: 75% of rows
are class methods stripped of their class, 69% of the corpus is one May forge
tool template, and only the prometheus_math families carry executable,
semantically real content [RESULT-UNVERIFIED] (roles/Talos/ledgers/). Talos
is a corpus-extraction pipeline and a set of honest measurements of that
corpus; it is not an organism, a substrate or a trained model.

## 1. Identity, charter and pivots

- Name: Talos; old path agents/talos/ (5 commits), seat path roles/Talos/
  (11 commits, all 2026-09-11) [IMPL] (git log).
- First commit 6e0a54d6b 2026-05-23 "Talos Phase 0: reasoning-code specialist
  corpus builder"; charter signed "Aporia, 2026-05-23" [IMPL]
  (agents/talos/CHARTER.md last line).
- Operator in the charter: Ergon ("Learner-family sibling") [CLAIM]; marked
  SUPERSEDED in the 2026-09-11 annotation at the top of CHARTER.md [CORRECTION].
- Host: M1 per STATUS ("workspace F:\Prometheus-worktrees\talos-base-role")
  [CLAIM]; the May daemon ran in the canonical checkout F:\Prometheus [IMPL]
  (manifest_latest.json searched paths F:\Prometheus\apollo\...).
- Pivot 2026-06-23: pivot/COMPONENT_DISPOSITION_PLAN_2026-06-23.md:50 labels
  Talos "REVIVE-SPINE | compute-trace corpus build (the +0.16-transfer
  feedstock)" [CLAIM]; the seat's own ledger calls this a label without a
  measurement (roles/Talos/calibration/LEDGER.md C-02) [CORRECTION].
- Reanimation 2026-09-11: 62dcbb9ea (base-role adoption; May queue classified
  0 STILL_LIVE, 6 NEEDS_REPREMISE), operator ruling TALOS-01 committed verbatim
  (roles/Talos/prompts/2026-09-11_talos01_ruling/OPERATOR_RULING.md): daemon
  NOT relaunched, Phase 1 NOT reconstructed, eval gate "not meaningful"
  [IMPL/CLAIM].
- Relationships: upstream = Hephaestus forge, prometheus_math, charon,
  theseus scripts (as raw text); downstream = none ever (TALOS-10 consumer
  search, 4 answers all NONE) [RESULT-UNVERIFIED]
  (roles/Talos/ledgers/CONSUMER_SEARCH_2026-09-11.md, INTERSECTION_2026-09-11.md).

## 2. Engine/system inventory

Engine T1: TalosCorpusDaemon (only engine).
- Paths: agents/talos/daemon.py (35 KB), corpus/manifest_*.json,
  corpus/README.md, eval/cases/ (5 JSON cases), eval/README.md,
  training/lora_config.yaml [IMPL].
- Purpose: extract (docstring, function body) records from five "streams"
  weighted 0.30/0.25/0.20/0.15/0.10 [INTENT].
- Entrypoints: `python -m agents.talos.daemon --once | --loop --interval 3600 |
  status | manifest` [IMPL] (CHARTER "CLI"; daemon.py main()).
- Key functions: extract_python_functions (ast.walk over FunctionDef /
  AsyncFunctionDef, daemon.py:325), _fingerprint (:355), scan_stream (:385,
  mtime cursor per file), scan_apollo_organisms (:454), append_to_shard (:478),
  write_manifest (:489), run_tick (:568) [IMPL].
- State: agents/talos/state/state.json (per-file mtimes), events.jsonl,
  talos.pid lock; shards gitignored under agents/talos/corpus/shards/ [IMPL];
  copied byte-identical on 2026-09-11 to
  roles/Talos/ledgers/corpus_shards_2026-09-11/ (hephaestus_forge.jsonl
  28.8 MB, prometheus_substrate.jsonl 8.4 MB) [IMPL].
- Deps: stdlib (ast, json, hashlib) plus session_telemetry heartbeat [IMPL].
- Execution model: hand/hidden-window launched hourly loop; 2026-09-11
  TALOS-04 made it fail closed on the canonical checkout and without a
  committed unpark record (7eef9cc9b) [IMPL].
- Scale: 24,847 rows; 2,936 distinct source files [RESULT-UNVERIFIED]
  (CORPUS_CHARACTERIZATION_2026-09-11.md s1).

Non-engine scaffolds (written, never run): LoRA spec
(training/lora_config.yaml: r=16, alpha 32, 4-bit, 3 epochs) [INTENT]; eval
harness: 5 cases (T1-001, T1-002, T2-001, T3-001, T4-001) and no grader
(eval/score.py promised for Phase 0.5, absent) [IMPL by absence].

## 3. Code architecture and dataflow

files under stream roots -> mtime filter -> ast.parse -> every function node
-> {snippet, docstring, has_docstring, source_path, line} -> fingerprint
dedup -> append shard -> manifest [IMPL]. No quality filter is applied:
`require_docstring=False` for the forge, substrate and synthetic streams
(daemon.py:591, 610, 639) [IMPL].

Code-vs-doc disagreements:
- CHARTER stream 1 says only files "marked forged=True" that "survived
  ablation" are extracted [INTENT]; the extractor walked every .py under
  agents/hephaestus/ including scrap/ (1,021 rows) and src/ (422 rows) and no
  row carries an ablation tag [CORRECTION] (LEDGER.md C-03 annotation;
  CORPUS_CHARACTERIZATION s1).
- CHARTER stream 2 says Apollo elite organisms are compiled to Python
  [INTENT]; scan_apollo_organisms always returns an empty list even when an
  Apollo root exists ("compilation to Python deferred to Phase 0.5")
  [IMPL] (daemon.py:454-475). In the May runs the roots apollo/runs,
  apollo/runs_v2, apollo/organism_runs did not exist [IMPL]
  (manifest_latest.json "upstream_not_found"); they still do not exist at
  21a47402a (apollo/ holds run_branch_c*, run_v2d2b, cycles, etc.) [IMPL].
  So the "Apollo stream" never produced or could produce a record.
- CHARTER describes the corpus as (spec -> implementation) pairs; 18,669
  rows (75%) are methods without their class and 8,431 lack a docstring
  [CORRECTION] (LEDGER.md C-04).

## 4. Claimed computational primitive vs actual mechanism

- Label: "reasoning-code specialist"; "substrate-shaped training data
  produces substrate-shaped behavior in a small model" [INTENT].
- Smallest actual mechanism: an AST function-node extractor with byte-level
  dedup [IMPL]. There is no model, no training loop, no inference.
- What it could express in principle: a supervised (docstring -> body)
  dataset; in the prometheus_math tests family, (property statement ->
  executable check) pairs that pass on today's tree [CODE-INFERRED]
  (SEMANTIC_SAMPLE_2026-09-11.md s3).
- Reasoning phenomenon the ruler targeted: four capabilities (algorithm
  generation, primitive refactoring, counterexample code, "anti-gravitational
  -well pushback") [INTENT].
- Could the organism perform it: no organism exists [IMPL].
- Could the ruler tell it from a shortcut: the ruler does not exist (5 cases,
  0 graders, 0 baselines; gate "NOT ELIGIBLE TO FIRE") [IMPL]
  (LEDGER.md C-01). The pushback target (T4-001) grades presence of
  Prometheus vocabulary ("prime-atmosphere detrending", "matched-null") in a
  docstring [IMPL] (eval/cases/target_4_pushback/T4-001_*.json) -- a
  keyword-recall test that a model memorising house jargon would pass
  [CODE-INFERRED].

## 5. Representation/state architecture

Records are flat JSON with raw source text; no AST, graph, type or call
structure retained beyond the snippet string [IMPL]. 21% of rows are closed
under builtins; 1,668 of 2,841 prometheus_math module rows call another
family function [RESULT-UNVERIFIED] (INTERSECTION_2026-09-11.md).

## 6. Organism/player architecture

None found. The intended organism (LoRA-tuned Qwen2.5-Coder-1.5B) was never
instantiated [IMPL by absence: no adapters, no training logs in tree].

## 7. World/environment architecture

None. The "world" is the repository's own source tree [IMPL].

## 8. Search/training/adaptation mechanism

None ran. Charter Phase 1 LoRA training was gated on >=10K pairs, a GPU slot
and a base-model baseline; only the first condition was met [IMPL/CLAIM].

## 9. Measurement/ruler stack

May 2026: corpus size, per-stream counts, null-tick counter, SYNTHETIC_RISK
alarm (synthetic weight > 0.30) [IMPL]. No quality signal.
September 2026 (the seat's own measurements, all [RESULT-UNVERIFIED]):
- characterize_corpus.py with 7 controls (planted duplicates, builtin-closure
  cheat, method-parse, syntax error) (roles/Talos/science/characterize_corpus.py;
  ledgers/CORPUS_CHARACTERIZATION_2026-09-11.{json,md}).
- semantic_faithfulness.py, preregistered at 38049e210 before its first run,
  6 controls, 746 sampled rows, seed 20260911: claim grammar RAISES /
  RETURNS / MENTIONS checked against bodies, tests executed with pytest
  (ledgers/SEMANTIC_SAMPLE_2026-09-11.{json,md}).
Blind spots, named by the seat: MENTIONS over-extracts (40 of 48 UNFAITHFUL
rows fail only MENTIONS) [CORRECTION] (LEDGER C-06); first run's batched
pytest reported 90 runnable tests as NOT_COLLECTED (instrument fault, caught,
repaired) [CORRECTION] (LEDGER C-05). HAS_ORACLE is name collision for forge
rows (`evaluate`, `confidence`) [RESULT-UNVERIFIED].

## 10. Baselines and controls

May: none (no base-model eval was run) [IMPL by absence]. September: the
seven characterization controls and six faithfulness controls above; these
are instrument controls, not capability baselines.

## 11. Historical experiment campaigns

C-T1 Phase 0 corpus build. 2026-05-23..05-30. Question: build >=10K
reasoning-code pairs. Organism/world: none. Measurement: counts. Scale: 170
ticks, 24,847 rows (forge 18,671; substrate 6,176; apollo 0; OSS 0; synthetic
0). Reported: corpus grew. Later: characterized as template-dominated, no
ablation filter. Paths: agents/talos/corpus/manifest_2026-05-23.json,
manifest_2026-05-30.json; commits 6e0a54d6b, a8a276a40. Label: INSTRUMENT
FAILURE (3 of 5 streams empty, quality filter never applied; as a corpus
build it is MIXED).

C-T2 TALOS-03/11 corpus characterization. 2026-09-11. Commit 905be25f7.
Result: 0 exact duplicates, 8,216 template repeats, 75% class methods without
class, 69% one forge template [RESULT-UNVERIFIED]. Label: REPORTED
NEGATIVE/NULL (on the corpus's claimed nature).

C-T3 TALOS-24 semantic faithfulness. 2026-09-11. Prereg 38049e210, result
c236551ab. Result: "semantically real" per family -- prometheus_math_tests
86/100, modules 43/100, theseus 18, charon 15, hephaestus 3/346
[RESULT-UNVERIFIED]. Label: MIXED.

C-T4 TALOS-10 consumer search. 2026-09-11. Question #50 broadcast to all
seats. Result: 4 answers, all NONE; intersection EMPTY (provisional)
[RESULT-UNVERIFIED] (INTERSECTION_2026-09-11.md). Label: REPORTED
NEGATIVE/NULL.

## 12. Reported results and later corrections

- "24,847 (spec -> implementation) pairs" (62dcbb9ea draft) -> characterization
  -> 75% class methods, 8,431 no docstring -> annotated (LEDGER C-04)
  [CORRECTION]. Current status: corpus is mostly decontextualised fragments.
- "+0.16-transfer feedstock" (pivot 06-23) -> no transfer run exists ->
  LEDGER C-02 [CORRECTION]. Current: aspirational label.
- "eval gate >= 10 points on N=50" (charter) -> 5 cases, 0 graders -> C-01
  "cannot fire on any input" [CORRECTION].

## 13. False-positive archaeology

- The 0.16-transfer label attached to Talos with no measurement (C-02).
- Stream-1 "proved by ablation" phrasing describing an unfiltered walk (C-03).
- A near-miss the seat itself caught: 90 tests reported NOT_COLLECTED due to a
  batched-pytest fault (C-05).

## 14. Likely false-negative regimes

Not applicable to capability (nothing was trained). For the corpus: the
"hephaestus 3/346 semantically real" reading depends on a docstring-claim
grammar that cannot check property statements; rows with no checkable claim
are UNMEASURABLE, not false [RESULT-UNVERIFIED]. Executable content outside
tests may be undercounted [CODE-INFERRED].

## 15. Phase 3 audit (engine T1, corpus daemon)

a. Representation richness: hierarchy NO (flat records); compositional
   structure NO (call edges not retained); variable binding NO; memory NO;
   recurrence NO; counterfactual state NO; latent variables NO; temporal
   abstraction NO; spatial abstraction NO; reusable substructure PARTIAL
   (1,668/2,841 library rows call another family function, but the link is
   not represented); dynamic routing NO; self-reference NO.
b. Reasoning opportunity: none; there is no environment or task loop.
c. Shortcut surface: the T4 pushback grader rewards house vocabulary; T2
   refactor grader (charter) counts function boundaries with one-line
   docstrings (AST count) -- both gameable by surface form [CODE-INFERRED].
d. Ruler resolving power: zero for capability (no grader); moderate for
   corpus hygiene (September controls).
e. Scale: 24,847 rows, 37.2 MB; 5 eval cases; 0 training steps; planned model
   1.5B params, LoRA r=16.

## 16. Research reports and substantial documents

- agents/talos/CHARTER.md -- May charter, annotated HISTORICAL 2026-09-11.
- roles/Talos/ARCHAEOLOGY_2026-09-11.md -- May queue (T01-T15) classified.
- roles/Talos/ledgers/CORPUS_CHARACTERIZATION_2026-09-11.md -- 7-control
  characterization.
- roles/Talos/ledgers/SEMANTIC_SAMPLE_2026-09-11.md -- preregistered
  per-family faithfulness.
- roles/Talos/ledgers/INTERSECTION_2026-09-11.md -- real x demanded = EMPTY.
- roles/Talos/ledgers/CONSUMER_SEARCH_2026-09-11.md -- protocol and answers.
- roles/Talos/calibration/LEDGER.md -- 6 self-corrections.

## 17. Journals/TODOs/backlogs/pivots/abandoned branches

roles/Talos/journal/2026-09-11.md (three passes); roles/Talos/BACKLOG_H0H5.md
(TALOS-xx items; TALOS-22/25 open by protocol); INBOX files
INBOX_APORIA_TALOS10_2026-09-11.md, INBOX_TECHNE_TALOS10_NONE_2026-09-11.md
(Techne answered NONE with two preconditions, 0c35c1c30). Abandoned: Phase
0.5 (Apollo compiler, quality gate, score.py), Phase 1 LoRA, Phase 2 3B.

## 18. Dependencies on other engines and seats

Reads: agents/hephaestus/ (forge tool files), prometheus_math/,
charon/diagnostics/, theseus/scripts/ (as text) [IMPL]. Apollo (intended,
never wired). Aporia (author), Ergon (named operator, superseded), Archaeon
(named a possible "door": small declared grammar + executable checkers;
condition 2 ABSENT) [RESULT-UNVERIFIED] (INTERSECTION).

## 19. Scaling limitations

Extraction is cheap and could scale to any Python tree; the limitation is
content (decontextualised methods, one dominant LLM template) and the absence
of any learner or grader.

## 20. Lens potential for Phase 3 (descriptive)

- Substrate: Python source text. Organisms: none. Worlds: none.
- Reusable parts: the preserved, hashed shards; the two September
  instruments (characterize_corpus.py, semantic_faithfulness.py) with their
  controls; ~2,500 (estimated) passing prometheus_math tests as executable
  checkers [RESULT-UNVERIFIED].
- Toy-grade parts: 5-case eval, keyword pushback grader, Apollo stub.
- Phenomenon family it could serve: program synthesis against executable
  checkers (repair or re-synthesis of a removed function against its tests)
  [CODE-INFERRED]; nothing of this is built.
- Resolution ceiling: bounded by the prometheus_math test suite.
- Unknowns: whether any LLM-trained-on-corpus effect exists (never measured).

## 21. Open questions / coverage gaps

Read: CHARTER.md, daemon.py (selected functions), manifest_latest.json, the
T4 eval case, STATUS, LEDGER, SEMANTIC_SAMPLE.md, INTERSECTION.md,
CORPUS_CHARACTERIZATION.md (s1-s2), git log for both paths. Not read in full:
roles/Talos/journal/2026-09-11.md, ARCHAEOLOGY items T02-T15 in detail,
CONSUMER_SEARCH, the two science scripts line-by-line, the JSON ledgers and
shards (not opened). The pivot dossiers of 06-07 and 06-24 cited by the
archaeology were not read. Open: whether any adapter or training artifact
exists off-tree (none found in tree).
