# Seat dossier: Metis

- Seat: Metis -- three bodies under one name: (A) March 2026 "Cunning Intelligence" literature analyst
  (agents/metis/), (B) May 2026 portfolio reporter (scripts/metis_portfolio.py), (C) September 2026 composition
  seat (roles/Metis/, Season 1).
- Crawler label: hist (Ixion sub-crawler)
- Date: 2026-10-01 (date -u 09:47Z)
- Base SHA read: bed05507a; history via `git log --all`.
- FULLY READ: agents/metis/README.md, configs/metis_config.yaml, src/metis.py lines 240-350 (prompt, staleness,
  generate_brief), briefs 2026-03-22/03-31/04-01; roles/Metis/STATUS.md; OPERATOR_RULING.md (season1_ruling);
  season1/SEASON1_RECEIPT.md; REPLAY_SUMMARY.txt; compose.py header + function index; FAILURE_LEDGER s1-2;
  ARCHAEOLOGY_2026-09-11.md s0-3; scripts/metis_portfolio.py lines 1-80, 449-535, 851-873.
- SAMPLED: season1 bundles (by name only), SEASON1_PROMPT.md (735 lines, NOT read), EPISODE_PRECONDITION ledger
  (via STATUS summary only), test_adversarial.py (not read), CALIBRATION.md (not read).
- LIVE READS: agora.intelligence_outputs (metis_* stages) read-only.
- NOT READ: SEASON1_PROMPT.md body, journals in full, the five source episodes' original records (Ergon greedy-LoRA,
  Apollo, Saxl, Geometry-1, Erebos) -- other crawlers' territory.

## 1 Charter and role history

- [IMPL] (A) created 2026-03-22 cc9527863 "feat: add Metis -- cunning intelligence agent"; 62 commits touch
  agents/metis/ (git log --all count), of which all but ~6 are "pronoia: auto-publish reports"; last b674a9976
  2026-04-03.
- [INTENT] (A) README: "Prometheus's analysis brain ... compress, don't expand -- Eos produces 50+ items. Metis
  produces 3-5 ... James-proof -- assumes a 10-second goldfish loop".
- [IMPL] (B) scripts/metis_portfolio.py first commit 56d128abc 2026-05-15 "Metis portfolio mode: LLM brief over Agora
  state"; docstring calls itself "the agent-state-reporting cousin" of (A).
- [HIST] 2026-06-10 program audit archives the serial chain including Metis (aporia/docs/program_audit_2026-06-10.md:135).
- [IMPL] (C) seated 2026-09-11 82fbe180d; operator ruling same day re-premised the seat to COMPOSITION
  (962e4a186; verbatim roles/Metis/prompts/2026-09-11_season1_ruling/OPERATOR_RULING.md): "Can Prometheus combine
  heterogeneous failure evidence into a better next experiment than any individual evidence channel would select?"
  and "No LLM judging correctness. Historical outcome supplies the falsification." Ruled OUT: orchestrator, judge,
  daily-report generator; Pronoia chain position NOT revived.
- [IMPL] Season 1 executed 2026-09-13: PREREG a4f345aa7 -> SPECIMEN FREEZE 2a650277b -> CLOSED f9f90c0f7.
- [CORR] "Retired": the operator charter (Ixion) and Achilles census (FLEET_CENSUS.md:81 RETIRED) say retired; the
  seat's own STATUS.md:6 says "SEASON 1 CLOSED -- awaiting operator on the F4 attack" and recommends Season 2. The
  census registry (roles/Achilles/census/registry/seats_part3.json, Metis) records lifecycle_marker state "CLOSED"
  quoting that line; the RETIRED label appears to be the census's mapping of CLOSED. No retirement ruling for
  Metis was found in the repo (git grep 'metis.{0,80}retir' outside roles/Metis returned only census/Skopos/
  dossier lines). [UNK] whether an operator retirement exists in comms (comms DB not reached).

## 2 Systems maintained

| System | Status | Evidence |
|---|---|---|
| (A) agents/metis/src/metis.py analyst | dormant since 2026-04-01 (last brief) | briefs/, MONITORS.md:84 |
| (B) scripts/metis_portfolio.py reporter | LIVE inside Pronoia's intelligence_loop on M4; owner-less by ruling | agora rows to 2026-10-01; MONITORS.md:85 |
| (C) roles/Metis/season1/specimen/compose.py | frozen specimen, not integrated anywhere | SEASON1_RECEIPT "Nothing integrated" |
| scripts/llm_cascade.py | extracted Metis cascade, imported by metis_portfolio | metis_portfolio.py:49-60 |

## 3 Actual implementation paths

- (A) agents/metis/src/metis.py (438 lines), configs/metis_config.yaml, briefs/ (8 files, 702 lines).
- (B) scripts/metis_portfolio.py (928 lines); outputs docs/portfolio_brief.md, docs/briefs/, touches
  docs/manual_status.json.
- (C) roles/Metis/season1/{SEASON1_PREREGISTRATION.md 218, SPECIMEN_FREEZE.md 17, specimen/compose.py 442,
  specimen/test_adversarial.py 294, bundles/*.json (6), REPLAY_RESULTS.{json,txt}, FAILURE_LEDGER.md 180,
  SEASON1_RECEIPT.md 165}. Line counts by wc -l.

## 4 Architecture

- [IMPL] (A) single LLM call: Eos digest "attention items" (truncated to 4000 chars) + project context
  (PRIORITIES/TODO/RPH, truncated to 3000) + optional staleness warning -> call_llm (Nemotron 120B -> Cerebras
  Qwen3-235B -> Groq llama-3.1-8b; max_tokens 4000, temperature 0.3; metis.py:171-212) -> brief file. System prompt
  hardcodes the then-current program (Ignis CMA-ES, Noesis, Forge, RPH, RLVF; metis.py:246-253).
- [IMPL] (A) `_detect_staleness()` (added 2026-03-29, 6058e6eb1): sha256 of the normalised "Act on this" section of
  the last 5 briefs; warns only if the 3 newest hashes are identical. It feeds the warning INTO the LLM prompt.
- [IMPL] (B) deterministic-first: `generate_brief()` returns `_deterministic_brief(state, manual_status)` unless
  env METIS_LLM=1 (metis_portfolio.py:449-458). LLM path: state block + manual_status + 24 h git log + previous
  brief (with a "LOUD warning" header) -> call_llm -> `_strip_chain_of_thought` -> `_has_chain_of_thought_leak`
  (>=2 of 18 marker phrases => fall back to deterministic) (lines 501-534).
- [IMPL] (C) compose.py: "set operations over declared structure": availability filter (ADMISSIBLE =
  COMMIT/EXTERNAL/INTERNAL), search-completeness gate, union-find dependence grouping over shared upstream tokens
  (`_group_by_shared_upstream`, line 127), live-explanation elimination, vetoes (instrument-suspect via
  degenerate_boundary + generator_known_active, staleness), cheapest discriminator on an ordinal COST_RANK
  (TRIVIAL..WEEKS). Docstring: "Deterministic. No learned weights, no model call, no aggregate score."

## 5 Data stores

- (A) briefs/*.md (one file per day, OVERWRITTEN each cycle); reads agents/eos/reports, docs/*.md, Aletheia sqlite.
- (B) docs/state.json (input), docs/portfolio_brief.md, docs/briefs/portfolio_brief_<ISO>.md, docs/manual_status.json;
  agora.intelligence_outputs stage metis_brief_generated (498 rows, 495 success, 2026-05-23..2026-10-01; SELECT).
- (C) JSON evidence bundles (per episode: items, upstream tokens, rules_out, instruments, cutoffs).

## 6 APIs/interfaces

- (A) `python src/metis.py [--digest path]`. (B) `python scripts/metis_portfolio.py [--loop MIN]`, env METIS_LLM.
- (C) `compose(bundle) -> Result`, `load_bundle(path)`, `render(r)` (compose.py:191, 344, 395). Bundle schema
  validated by `validate()` (line 161).

## 7 Scheduling model

- (A) [IMPL] invoked by pronoia.py step 4 only after an Eos digest exists; no own schedule.
- (B) [IMPL] hourly/4-hourly via intelligence_loop on M4 (watchdog task); row cadence ~6/day.
- (C) none; manual, single season.

## 8 State machine

- (C) [IMPL] per-explanation states live / eliminated / vetoed; per-item admissibility; output labels
  CONFIRMED vocabulary DEPENDENT, VETO, INSTRUMENT_SUSPECT, STALE, CHEAP_KILL_AVAILABLE (5 of 7 kept; ORTHOGONAL,
  BASE_RATE_CONFOUNDED deleted under probation, SEASON1_RECEIPT).
- (A)/(B): none beyond the deterministic/LLM fallback switch.

## 9 Communication channels

- (A) brief file -> Hermes email -> GitHub auto-publish. (B) docs/portfolio_brief.md -> send_brief_email.py (Hermes) +
  GitHub Pages; Elenchus names it as its shadow-review surface [HIST STATUS.md].
- (C) seat posted a reply to Skopos defect 01 (prompts/2026-09-11_skopos_reply) [HIST]; METIS-14/TALOS-10 held at
  provisional NONE by ruling.

## 10 Failure recovery

- (A) [IMPL] on total cascade failure, writes the literal "(Metis could not reach any LLM provider)" as the brief
  body (metis.py:240; 2026-03-31_brief.md is 161 bytes of exactly that). 5 of 58 historical brief blobs contain
  that string (counted over every brief blob in `git log --all -- agents/metis/briefs`).
- (B) [IMPL] "a stub can never ship": unparseable LLM output replaced by deterministic brief (main(), lines 886-905).

## 11 Persistence

- (A) [IMPL] 8 brief filenames at HEAD but 58 distinct brief blobs across history (per-commit ls-tree, sort -u):
  e.g. 2026-03-23_brief.md has 21 committed versions. Only git preserves the intermediate briefs.
- (B) [IMPL] historical copies in docs/briefs/ plus 4-hourly commits; agora rows.

## 12 Provenance

- (C) [IMPL] strong: prereg commit precedes freeze commit precedes closure commit, all 2026-09-13; specimen hashes
  in SPECIMEN_FREEZE.md [HIST, hashes not re-verified here].
- [REPORTED] SEASON1_RECEIPT grades source provenance per episode; E1 greedy-LoRA graded INTERNAL_UNCORROBORATED
  (single retrospective document 7e38227ee, artifacts gitignored) (FAILURE_LEDGER s2).
- (B) [IMPL] `touch_manual_status_timestamp()` (metis_portfolio.py:851-871, since 0d2c7f015 2026-05-17) rewrites
  docs/manual_status.json last_updated_at to NOW every cycle and sets last_updated_by "Metis auto-stamp
  (per-cycle)". The operator's "authoritative" override therefore looks fresh on the producing host regardless of
  content age. In git the file's last commit is 27dcad44b 2026-05-18. [INFER] freshness-laundering of a ground-
  truth input, mitigated only by the last_updated_by marker.

## 13 Resource usage

- (A) one LLM call per cycle, up to 4000 output tokens, free tier. (B) deterministic path 0.3-0.5 s per cycle
  (agora output_summary). (C) negligible; "MINUTES"-class discriminators proposed, none executed.

## 14 Model/inference dependency

- (A) MODEL_MEDIATED end to end. (B) LLM opt-in only since 2026-08-18. (C) explicitly model-free by ruling.

## 15 Human dependency

- (A) consumer was James on phone. (B) consumer James (email) + Elenchus. (C) operator wrote the season prompt;
  F4 attack (blind second encoder) routing is "the operator's call".

## 16 Major outputs

- (A) [IMPL] 8 HEAD briefs / 58 historical versions; [HIST] ARCHAEOLOGY s2: 6 of 8 HEAD briefs repeat the same
  three internal actions (Eos API wiring 6/8, Qwen3-4B run 5/8, 7B cloud run 4/8) in different words.
- (B) [IMPL] ~495 successful briefs, the operator's 4-hourly dashboard and email body.
- (C) [REPORTED -- UNVERIFIED] Season 1 replay (REPLAY_SUMMARY.txt): in each of 5 historical episodes N agreeing
  items collapse to ONE independent reason; specimen vetoes all 5 and proposes a cheaper discriminator
  (E1 relation base-rate oracle MINUTES; E2 lineage cheat control MINUTES; E3 check object matches claim MINUTES;
  E4 permute the mask alone MINUTES; E5 permutation null on real ledger HOURS). Positive control E1b: 0
  confidence vetoes, 2 independent reasons. Ruling SPECIMEN_SURVIVES_RETROSPECTIVE "narrowly".
- (C) [REPORTED] Apollo instrument trap: "77 of 77 reports carrying [llm_alive] read zero in every stratum" while
  LLM call counts were 18/31/15 -- an instrument artifact the specimen vetoes at the April cutoff.

## 17 Known failures

- (A) [IMPL] hash-based staleness check defeated by LLM rewording (byte-distinct bodies, same content); added
  2026-03-29 and only 2 briefs (03-31 failure string, 04-01) followed, so it never had 3 eligible briefs [INFER].
- (A) [IMPL] failure string written as a brief; health checker counted it as output (Pronoia dossier 17.5c).
- (B) [HIST] LLM leaked chain-of-thought into emails (52b844afa, 65b6e0140, af9b4d9c9); confabulated "14 agents
  pending" from 43 UNKNOWNs, mailed 6x/day for seven weeks (aporia/docs/germline_infrastructure_2026-08-17.md:185;
  roles/Hephaestus/META_ASSESSMENT_2026-08-12_fable_seat.md:286, attributing it to "the M4 reporter"). [INFER] the
  M4 reporter = this script's LLM path inside Pronoia's loop.
- (B) [HIST] infra alarm dead since 2026-09-01 (reads state.infra_status, key removed in d46800bfb; optimistic
  literal fallback) -- roles/Metis/STATUS.md. Not re-verified.
- (C) [REPORTED] 5/5 veto rate is indistinguishable from veto-everything except for one post-hoc positive control;
  P-5 (composition beats single-channel) never tested -- no single-channel baseline run (SEASON1_RECEIPT).

## 18 Pivots

- 2026-03-22 analyst -> 2026-04 archived (with chain) -> 2026-05-15 name reused for fleet reporter -> 2026-08-18
  reporter deterministic-first -> 2026-09-11 seat re-premised to composition; reporter ruled out of the seat
  (METIS-01 closed NO; METIS-01R re-routed to operator/Archaeon) -> 2026-09-13 Season 1 closed.

## 19 Journals/TODOs/backlogs

- roles/Metis/BACKLOG_H0H5.md (METIS-01R, -03 state.json producer UNLOCATED, -05 hash-insufficiency to Eos/Archaeon,
  -07 manual_status freshness, -09 infra alarm repair, -14 TALOS-10, -15 analyst code ownership XL, -23 Skopos
  defect) [HIST]. calibration/CALIBRATION.md incl. C-05 (prefix `head -40` made greedy-LoRA "not locatable").

## 20 Historical relevance to current Prometheus

- (C) is the only executable, model-free "experiment selection under correlated evidence" specimen found in this
  crawl's territory; its vocabulary (dependence grouping by shared upstream, instrument-suspect veto, cheapest
  partitioning discriminator) is directly about LENS/RULER selection [IMPL compose.py].
- (B) is live and is the operator's daily view of the fleet [IMPL].
- [CORR] MONITORS.md rows say (B) DORMANT since 2026-09-09; git shows "auto: portfolio update" 6/day resumed
  2026-09-18 through 2026-10-01 (git log on docs/portfolio_brief.md, counted per day) and agora rows confirm. The
  census flagged this conflict (docs/fleet/fleet_state.json:15471).

## 21 Inference-dependency classification

| function | class | evidence |
|---|---|---|
| (A) literature triage into Act/Watch/Record | MODEL_MEDIATED | metis.py generate_brief |
| (A) novelty/staleness detection | INFERENCE_FREE (but insufficient downstream of an LLM) | _detect_staleness |
| (B) fleet brief | ASSISTED_PLAUSIBLY_DETERMINISTIC -> realised as INFERENCE_FREE default | metis_portfolio.py:449-458 |
| (B) chain-of-thought leak detection | INFERENCE_FREE | _has_chain_of_thought_leak |
| (C) dependence grouping / vetoes / discriminator choice | INFERENCE_FREE | compose.py |
| (C) encoding evidence bundles (rules_out, upstream tokens) from history | OCCASIONAL_JUDGMENT (and the F4 weak joint) | FAILURE_LEDGER item 4 |
| (C) naming rival explanations (e.g. BASE_RATE_PRIORS) | MODEL_MEDIATED / human | SEASON1_RECEIPT "Someone still has to name BASE_RATE_PRIORS" |

## 22 False-negative / false-positive watch

- FALSE NEGATIVE: (C) is labelled RETIRED by the census but the seat recorded no retirement and recommended a
  prospective Season 2 with two named preconditions (second blind encoder; >=3 positive controls). If retirement is
  real, it killed an instrument after ONE retrospective season of 5 episodes -- killed by SCALE, not by a negative
  result. [CORR/UNK]
- FALSE NEGATIVE: (A)'s literature triage died with the chain (archived as a unit); its measured defects are
  stale hardcoded context in the system prompt and rewording-defeats-hash, i.e. ruler/implementation.
- FALSE POSITIVE: (C)'s "survives" rests on author-encoded bundles and a post-hoc positive control (seat says so).
  The 5/5 "one independent reason" pattern could be an artifact of how the author tokenised upstreams [INFER].
- FALSE POSITIVE: (B) LLM-era briefs (May-August) -- confabulated calm and frozen-state narration; any historical
  claim sourced from those briefs needs re-derivation from state.json/agora rows.
