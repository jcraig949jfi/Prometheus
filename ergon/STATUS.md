# Ergon Status

**Last updated:** 2026-05-14
**Updater:** Claude Opus 4.7 (1M context)

Ergon runs two parallel branches. This file is the single live status of both. State below is reconstructed from file mtimes, git history, and the most recent journal/handoff documents. Where a value is uncertain, it is marked TBD and the source of evidence is cited inline.

---

## Math-Research Branch

- **Mode:** frozen at reproducible milestone state
- **Last activity:** 2026-05-03 (per `wachs_reproduction.py` and `higher_gap_analysis.py` mtime 2026-05-03 18:31; `tensor.npz` rebuilt 2026-05-03 18:31). Bulk of the May-2 commit `3250f751` "Team backfill 2026-04-25 → 2026-05-04: accumulated multi-agent work" touched the rest.
- **Current focus:** None active. The thread last advanced under the 2026-04-18 HANDOFF.md plan (closure tests on Mechanism C, gap_k scans across CM / non-CM / G2C / MF / rank1 families, NBP cross-family work, h101/Salem-knot matching). After 2026-05-03 the focus shifted to the Learner branch.
- **Live artifacts:**
  - `F:\Prometheus\ergon\tensor.npz` — 28,352,304 B (27.0 MB), modified 2026-05-03 18:31. 4,755,770 objects x 208 features across 23 domains. See `tensor_manifest.md` beside it.
  - `F:\Prometheus\ergon\tensor_all.npz` — 37,856,233 B (36.1 MB), modified 2026-05-02 20:54. 5,079,774 objects x 263 features across 29 domains (core + extended + derived).
  - `F:\Prometheus\ergon\tensor_extended.npz` — 26,913,009 B (25.7 MB), modified 2026-05-02 20:54. 4,629,840 objects x 181 features across 20 domains (core + extended, no derived).
  - `F:\Prometheus\ergon\results\flajolet_odlyzko_results.json` — large run output (per logs/ listing).
  - `F:\Prometheus\ergon\results\hyperbolic_volumes.json` — 1.4 MB, 12,965 SnapPy volumes (per HANDOFF.md 2026-04-18).
  - `F:\Prometheus\ergon\results\hfk_features.json` — 3.97 MB, knot HFK features (2026-04-22).
  - `F:\Prometheus\ergon\results\shape_fingerprints.json` — 38.8 MB (2026-04-22).
  - `F:\Prometheus\ergon\meta\pilot_archive_s99_g30.pkl` — 8.79 MB MAP-Elites pilot archive (2026-04-25).
- **Ready-to-run threads:** (carried over from HANDOFF.md "Level 2 Research" — scripts written but not yet executed at handoff time; per git history have NOT been re-run since)
  - `F:\Prometheus\ergon\tamagawa_mediation.py` — Q1+P1: does Tamagawa mediate isogeny effect?
  - `F:\Prometheus\ergon\convergence_by_class_size.py` — Q5+P5: finite-conductor transient or structural?
  - `F:\Prometheus\ergon\wachs_reproduction.py` — Q3: reproduce Wachs displacement, correlate with variance. (Touched 2026-05-03; status of the May-3 run TBD — verify against `results/wachs_out.log`.)
  - `F:\Prometheus\ergon\higher_gap_analysis.py` — gap1 vs gap2-4 deficit, cross-family. (Touched 2026-05-03; status TBD.)
  - `F:\Prometheus\ergon\isogeny_sha_joint.py` — joint distribution, partial correlations, BSD connection.
- **Blocked threads:**
  - **Euler product deflation** — needs lfunc Dirichlet coefficient access (per HANDOFF.md 2026-04-18, item 4).
- **Recent milestones (per HANDOFF.md 2026-04-18 + git log):**
  - 23-domain tensor v2 built; 4.76M objects x 208 features (commit `ce8ef247`).
  - Murmuration-by-isogeny COMPLETED: 5/21 large primes show significant F-test stratification, ~5-10x weaker than rank murmurations, NOVEL axis (no prior literature).
  - Scholz reflection p=3: zero violations across 344,130 number-field pairs; 71.5%/28.5% equality/differ-by-1 split; explains p=3 BST anomaly.
  - DHKMS prediction: 31% rank-0 residual is NOT a Wigner-vs-Gaudin reference error; DHKMS finite-N goes wrong direction; either unfolding error or genuine anomaly. Tracked as THREAD A "F011 rank-0 residual is genuine frontier."
  - lfunc origin index discovered — unblocks EC↔lfunc joins at scale (THREAD D).
  - Knot silence test: hyperbolic volumes + engineered features do NOT break cross-domain silence; Aporia confirmed bridge is categorical, not numerical.

## Learner Branch

- **Mode:** **substrate-first stand-down** — LoRA paused indefinitely per `pivot/strategic_pivot_2026-05-11_substrate_volume_first.md`. Tier-1 substrate Ergon shipped + 4-condition pilot LoRA design deferred (not retracted). 3-track substrate-first work shipped 2026-05-11; 2026-05-13 / 2026-05-14 operating reactive-plus-design per `ergon/PROMPT_2026-05-13_reactive_consumption.md` + 2026-05-14 work-queue.
- **Last activity:** 2026-05-14 — Track 1 second consecutive substrate-pipeline-to-Learner round-trip (2 EC-rank training_anchor blocks, both decidable); Track 2 P-vs-NP anti_anchor ingest gated on Techne AA-NNN registration (skipped, pickup tomorrow); Tracks 3 + 4 below.
  - **Track 1 (2026-05-14 EC-rank ingest — SUCCEEDED, behavior_delta_status=fixture_created):** Aporia hand-staged 2 EC-rank training_anchor blocks at `aporia/docs/staged_substrate_blocks/2026-05-14/validated.jsonl` (DR-S002 pilot, LMFDB elliptic-curve rank trust-tier split): anchor-ec_rank-001 analytically_proven 3M instances rank≤1 (Kolyvagin unconditional via mwrank + 2-descent), anchor-ec_rank-002 numerically_certified 800K instances rank≥2-or-Sha-non-trivial (BSD-conditional). Wrapped-shape unwrap fix from 2026-05-13 worked without modification — same Techne stager envelope. Dry-run 2→2 clean → full ingest with --write produced 2 LearnerRecord JSONL at `ergon/learner/corpus/v1_0_tier_pending/2026-05-14/under_threshold/training_anchor_learner_records.jsonl`. Both routed verification_tier=decidable + outcome_class=promoted (per spec §2.3 invariant_value + high-trust → promoted). **Caveat-preservation discipline confirmed:** anchor-ec_rank-002's BSD-conditional caveat preserved verbatim in `_training_anchor_meta.caveats` sidecar — AA-019-analog discipline for elliptic curves (explicit conditionality metadata, not silently absorbed into decidable routing). Today exercises the analytically_proven + numerically_certified path, complementing yesterday's ml_predicted → survived/conditional path; full trust-tier matrix now exercised in production. Populated ingest summary at `…/under_threshold/ingest_summary_2026-05-14_track1.json` with batch-adapted high_value_items (4/6 True, 2 False — AA-013 not in today's batch); behavior_delta_status.value="fixture_created" (≥1 LearnerRecord landed + AA-013 fixture persists from 2026-05-13). Cumulative: 4 LearnerRecords across 2 days, all below v1.0 inclusion threshold (≥5 total + ≥2 high-trust required; today's batch meets the high-trust bar at 2 but total still 2<5).
  - **Track 2 (2026-05-14 P-vs-NP anti_anchor ingest — SKIPPED, gated on Techne AA-NNN registration):** Aporia validated 3 anti_anchors at `aporia/docs/staged_substrate_blocks/2026-05-14/validated_reauthored.jsonl` (RELATIVIZATION_BARRIER_TOTALITY, NATURAL_PROOFS_UNIVERSALITY, ALGEBRIZATION_BARRIER_TOTALITY) using AA-XXX placeholder IDs. No Techne registration ticket in either inbox for 2026-05-14 confirming AA-NNN assignment. Per work-queue: "If Techne hasn't registered them by the time you finish Track 1, skip this track and pick it up tomorrow." Skipped. Will pick up when registration ticket lands.
  - **Track 3 (2026-05-14 stratification rule design — DESIGN-ONLY, awaiting Aporia adjudication):** Per Q2 commitment in `T-2026-05-11-aporia-to-techne-claim-stack-design-adjudication` (stratify by sub-domain, 5-15 per stratum, target 50-100 per major source, deterministic-reproducible). Filed spec at `ergon/learner/v1_0_plans/source_report_stratification_spec.md` (~270 lines, 7 sections). Proposes structured `stratification_rule` object on `source_report` with `strata_field` + `strata_classifier` (inline / external_function / enum; Tier-1 inline only) + `draws_per_stratum` + `target_total` + `seed_basis` (input_hash) + `tie_break` + `under_minimum_policy` + `over_target_policy` + `source_report_pointer`. Worked examples for KnotInfo (by knot_family) and LMFDB EC (by rank_stratum). Helper API contract: pure function `stratify(candidates, rule) → StratifiedDraw` at `ergon/learner/scripts/stratify_source_report.py` (NOT YET CREATED — locked until Aporia confirms). Determinism via SHA256-of-sorted-IDs → first-64-bits → `random.Random(seed)`. Filed closure `T-2026-05-14-ergon-to-aporia-stratification-rule-design` P2 with 7 open questions for Aporia adjudication. NO code shipped, NO schema modification landed — per James's instruction "do NOT ship code that locks the schema until Aporia confirms."
  - **Track 4 (2026-05-14 AA-013 fixture expansion — COMPLETE):** Expanded `ergon/learner/fixtures/smoke_tests/aa_013_tensor_rank_routing.json` v0.1 → v0.2. From MVP single-input to multi-case array: **6 test cases** = 1 positive (AA-013 / Rupniewski 2024 → TensorRankWitness) + 3 contrapositive (Schönhage 1981 border-rank additivity failure → BorderRankWitness; matmul exponent ω from border-rank constructions → BorderRankWitness/ComputationalComplexityCertificate; Lampert-Moshkovitz 2025 partition vs analytic rank → BorderRankWitness/CactusRankWitness or WaringRankWitness) + 2 ambiguous-edge (unspecified rank field — should surface uncertainty; matrix degenerate case where R=R̄ trivially — should surface degenerate-regime collapse recognition). Each case carries its own `expected_witness_route` + `rationale_for_routing`. Evaluation_method extended: positive/contrapositive use string_match; ambiguous-edge requires `routing_head_max_prob < 0.7` (calibrated uncertainty surfacing) OR explicit `request_clarification`. behavior_delta_status unchanged (fixture_created) — no Learner head exists to advance to eval_run. Filed closure `T-2026-05-14-ergon-to-aporia-track4-fixture-expansion` P3.
  - **(Prior 2026-05-13 sub-bullets preserved below for arc continuity)**
- **Last activity (2026-05-13):** Track 1 first end-to-end substrate-pipeline-to-Ergon round-trip attempted (empty-cycle); Track 2 v1.1 schema consumption documented + regression-confirmed.
  - **Track 1 (2026-05-13 pilot ingest — SUCCEEDED via Aporia hand-stage, behavior_delta_status=fixture_created):** Today's substrate-shaped pilot DR-001/DR-007/DR-231 fired; Techne's automated stager rejected all 14 candidate blocks on schema-conformance (3 different YAML/JSON conventions in Gemini's output, parser keyed on `# substrate_block:` comment-tag that Gemini didn't follow). Aporia ran a deeper source-doc analysis (16 blocks present, substantive content) and hand-staged 4 schema-conforming blocks at `aporia/docs/staged_substrate_blocks/2026-05-13/`: 1 anti_anchor (AA-013), 2 training_anchor (anchor-maass_gl3-001 ml_predicted + anchor-maass_gl3-002 numerically_certified — the AA-019 trust-tier distinction made concrete), 1 primitive_proposal (SecondCoefficientPositivityObstruction). **First end-to-end substrate-shaped-pipeline-to-Learner-corpus round-trip succeeded:** ingester unwrap fix applied (~25 LOC at parse loop to accept Techne's `{block_type, payload, metadata}` shape AND filter by `block_type==training_anchor` so the same code consumes a type-agnostic validated.jsonl); dry-run 2→2 clean; full ingest with --write produced 2 LearnerRecord JSONL at `ergon/learner/corpus/v1_0_tier_pending/2026-05-13/under_threshold/training_anchor_learner_records.jsonl` with correct trust-tier routing (ml_predicted → survived/conditional, numerically_certified → promoted/decidable; AA-019 mitigation made concrete). Below v1.0 inclusion threshold (2 < 5, 1 high-trust < 2) — correctly routed to `under_threshold/` per spec §3.2. Per Aporia P2 ticket `T-2026-05-13-aporia-to-ergon-aa-013-consumer-hook-fixture-and-behavior-delta-status-enum`, AA-013 routing-correction smoke-test fixture created at `ergon/learner/fixtures/smoke_tests/aa_013_tensor_rank_routing.json` (named per primitives.md TensorRankWitness entry's consumer-hook section; closes the doctrine-to-fixture loop ChatGPT 2026-05-13 flagged). Populated ingest summary at `…/under_threshold/ingest_summary_2026-05-13_track1.json`: all 6 routing_checks exercised pass (1 untested — v1.1 explicit-bs_coverage path remains untested at runtime, no v1.1 blocks staged); all 6 high_value_items_present True; **behavior_delta_status.value = "fixture_created"**. Filed earlier `T-2026-05-13-ergon-to-techne-pilot-ingest-results` P2 (consumer-side first read on automated-path empty cycle) superseded on substance by Aporia's deeper diagnosis; left in inbox as-is. Closure ticket to Aporia pending.
  - **Track 2 (2026-05-13 v1.1 schema consumption — COMPLETE):** Techne shipped `training_anchor` v1.1.0 today (`T-2026-05-13-techne-to-aporia-and-ergon-training_anchor-v1.1-ready`) with optional `bs_coverage: Array[String matching ^BS-\d{3,5}$]` field. Zero ingester code change needed — existing `derive_bs_coverage` at `ingest_training_anchors.py:142-153` already implements explicit-field-with-regex-fallback dual path (preemptively shipped 2026-05-11). Spec updated: §3.1 documents v1.1 explicit-path discipline, §5.1 Gap 1 marked RESOLVED, §6 calibration caveat updated. Regression test `test_blind_spot_probe_coverage.py` re-run: **7/7 PASS, 0.32s.**
  - **Track 3 (2026-05-13 EEC-004 runtime check — DEFERRED):** Techne's `tier_1_claim_runner.py` not yet shipped against Aporia's 20-claim starter batch (`aporia/meta/queue/claim_stack_aporia_starter_2026-05-13.md`). When that runner produces LearnerRecord output, inspect 5-10 records to confirm whether `verification_tier` reads decidability-status (current behavior per EEC-004) or KC/BS-tier (gate's actual need). No action today.
  - **(Prior 2026-05-11 work, preserved for reference):** Track 1 entry harness `ergon/learner/scripts/ingest_training_anchors.py` (~400 LOC, dry-run smoke-tested against synthetic input; BS-coverage heuristic silent-miss bug caught + fixed same hour); Track 2 scaffold `ergon/learner/v1_0_plans/episode_emission_consumption_2026-05-11.md` (8 opcodes, EEC-001..EEC-007); Track 3 BS-probe coverage gate `ergon/learner/eval/v1_0_eval_set_manifest.json` + test.
- **Prior arc (preserved for reference):** 2026-05-07 → 2026-05-09 12-fire post-restart Learner-Tester arc closed cleanly. Substrate↔Learner first round-trip completed 2026-05-11 (Techne Tier-1 instrumentation shipped commit `20d64203` — generator-level enrichment, no contract change, 36/36 tests pass).
- **Current focus:** v1.0 design intake. The 12-fire post-restart arc closed cleanly with 0 OPEN tickets, 60 BLOCKED-DEFERRED-V1.0, 7 DONE, 1 ABLE_TO_ADVANCE, 1 WONTFIX. (Note: handoff prompt cited "fire 15"; the journal numbering is fires 4-15 of the post-restart sub-sessions, with a separate Learner-Tester thread reaching fire 19 per `_session_close_2026-05-07_to_2026-05-08.md`.)
- **Pipeline status:**
  - **Trial 1 (residual classifier benchmark):** complete — `trials/trial_1_results.json` (2026-05-03), `TRIAL_1_REPORT.md`.
  - **Trial 2 (evolutionary engine, dry-run + production):** complete — `TRIAL_2_PRODUCTION_REPORT.md` (2026-05-04), bindeval smoke + revalidation (`learner/v1_0_plans/trial_2_kv_revalidation.md`).
  - **Trial 3 (5K scaling + iter-13/14/15/18/25/26/27/28/31 explorations):** complete — multiple iter reports through `TRIAL_3_ITER31` (2026-05-04 04:36 — 06:04). Ledgers in `learner/trials/ledgers/` (largest = `trial_3_iter28_a149_u05_canonical_ledger.jsonl` at 2.5 MB).
  - **Pipeline D (boundary-layer fixture + null-gate + tire-kick + v0.5b training):** v0.5 baseline established; `pipeline_d/runs/v0_5b_null_*` (2026-05-06), `pipeline_d/v0_5b_rerun.py` (2026-05-06 20:42). Boundary-layer fixture frozen at 17 entries (`pipeline_d/fixtures/boundary_layer_17.jsonl`).
  - **Inference / single-fact decomposition (E007 ablation):** complete — `learner/inference/single_fact_decomposition.py` (2026-05-07), `inference/ablation_e007_ab.py`. H-decomp-1 confirmed at n=3 paired tests.
- **Blind-spots confirmed (BS catalog, n>=2):** (per `_session_close_2026-05-07_to_2026-05-09_full_arc.md` and `tester_findings_consolidated.md` §5b.8.1.1)
  - **BS-001 Cohen** — set-theoretic forcing / independence (confirmed earliest, n=4)
  - **BS-003 Helfgott** — circle method / ternary Goldbach (confirmed fire 11)
  - **BS-004 Faltings** — algebraic-geometric methods / Mordell (confirmed fire 13)
  - **BS-005 McKay** — confirmed fire 13
  - **BS-006 Margulis** — confirmed fire 13
  - **BS-002 Lefschetz** — only n=1 BOTH-SKIP at fire 7 (NOT yet promoted to n>=2)
- **Failure-mode patterns:** **9 patterns** + sub-class structure (Pattern 9 emerged fire 8, falsified the saturation prediction at 8). Sub-classes: Pattern 1 = {1.A ASCII-misspell, 1.B Unicode-glitch}; Pattern 6 = {token-loop, abbreviation-loop, verbatim-paragraph-candidate}; Pattern 9 = {9.A LaTeX-document-mode-leak, 9.B Python-execution-mode-leak}. Fabrication archetypes within Pattern 1 family: FM-04 award-fab, FM-04 institutional-affiliation-fab, FM-14 self-aware-fab, FM-15 self-correction (n=1 tracked-only). Canonical doc: `learner/v1_0_plans/tester_findings_consolidated.md` (73,693 B, 2026-05-07).
- **Tickets:** 0 OPEN / 60 BLOCKED-DEFERRED-V1.0 / 7 DONE / 1 ABLE_TO_ADVANCE / 1 WONTFIX = 69 total.
- **Awaiting:**
  - Aporia v1.0 corpus design (standing coordination ticket `T-2026-05-07-ergon-to-aporia-format-mode-anchors`, scope expanded each substrate-grade fire — full scope listed in `_session_close_2026-05-07_to_2026-05-09_full_arc.md` §"Cross-pillar coordination state").
  - James review of `learner/v1_0_plans/v1_0_design_suggestions_2026-05-09.md` (5 user-tracked items A1-A5 + Ergon's additional suggestions B + sequencing C + open questions D).

---

## Surface area

- **Total `.py` files in tree (excluding `__pycache__`):** 168
- **Subdirectory inventory** (non-pycache .py counts):
  - `ergon/` (root) — 49
  - `ergon/learner/` — 11
  - `ergon/learner/operators/` — 9
  - `ergon/learner/trials/` — 21
  - `ergon/learner/tests/` — 22
  - `ergon/learner/diagnostics/` — 16
  - `ergon/learner/inference/` — 3
  - `ergon/learner/tools/` — 5
  - `ergon/learner/corpora/` — 2
  - `ergon/learner/v1_0_plans/` — 0 (4 .md docs only)
  - `ergon/pipeline_d/` — 13
  - `ergon/pipeline_d/fixtures/` — 0 (.jsonl fixtures)
  - `ergon/pipeline_d/runs/` — 0 (output JSON only; .gitignored)
  - `ergon/meta/` — 11
  - `ergon/diagnostic_c/` — 2
  - `ergon/scripts/` — 4
  - `ergon/docs/` — 0 (10 conjecture .md files)
  - `ergon/results/` — 0 (large JSON / JSONL outputs only)
  - `ergon/logs/` — 0 (8 jsonl files; latest `ergon_20260418_090119.jsonl` 1.5 MB; oldest 2026-04-13)
  - `ergon/graphify-out/` — 0 (cache subdirectory)
- **Tensor artifacts:**
  - `tensor.npz` — 27.0 MB, 2026-05-03 18:31, 4.76M x 208, 23 domains (live)
  - `tensor_all.npz` — 36.1 MB, 2026-05-02 20:54, 5.08M x 263, 29 domains (full incl. derived)
  - `tensor_extended.npz` — 25.7 MB, 2026-05-02 20:54, 4.63M x 181, 20 domains (no derived)
- **Most recent commits touching `ergon/`** (per `git log --oneline -10 -- ergon/`):
  - `b3bbaddb` v1.0 design suggestions doc: forward plan with user-tracked items + Ergon additions
  - `547b849e` Full-arc session close 2026-05-07 → 2026-05-09: 12-fire consolidated journal
  - `760d28e2` Session close 2026-05-08 resume: 2-fire quiet-tick session
  - `96f1e4cf` Fire 15 post-restart: quiet tick, empty inbox; loop stopped by user
  - `e00d8b6e` Fire 14 post-restart (post-resume): quiet tick, empty inbox

---

## Update protocol

- Anyone touching `ergon/` should update this file's **Last updated** timestamp + the relevant branch section (Math-Research, Learner, or both).
- For new branches/modes (e.g., a future Trainer or Inference-server branch), add a new top-level section between Learner and Surface area.
- For abandoned threads, do not delete — move to a "Retired threads" section appended at the bottom of this file, with one-line cause-of-death and the last commit hash that touched the thread.
- Recompute the Surface area section opportunistically (after structural changes; a one-line `find` + `wc -l` is sufficient).
- Tensor artifact sizes / dates should be updated whenever `tensor*.npz` is rebuilt; mirror those updates into `tensor_manifest.md`.

---

## Retired threads

(none yet)
