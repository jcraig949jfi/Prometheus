# Ergon Status

**Last updated:** 2026-05-11
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

- **Mode:** **substrate-first stand-down** — LoRA paused indefinitely per `pivot/strategic_pivot_2026-05-11_substrate_volume_first.md`. Tier-1 substrate Ergon shipped + 4-condition pilot LoRA design deferred (not retracted). 3-track substrate-first work in flight per `ergon/PROMPT_2026-05-11_substrate_first.md`.
- **Last activity:** 2026-05-11 — Track 1 + Track 3 substantially complete; Track 2 scaffold filed pre-Techne-audit-prep.
  - Track 1 PRIMARY (training-anchor ingestion entry harness): `ergon/learner/v1_0_plans/training_anchor_ingestion_spec.md` + `ergon/learner/scripts/ingest_training_anchors.py` (~400 LOC, dry-run smoke-tested against synthetic input; BS-coverage heuristic caught its own silent-miss bug during smoke test — fix shipped same hour). Awaiting Techne's substrate-shaped pipeline to produce real input.
  - Track 2 (episode-emission consumption check): `ergon/learner/v1_0_plans/episode_emission_consumption_2026-05-11.md` scaffold filed; 8 opcodes documented; EEC-001..EEC-007 gap inventory awaiting Techne's audit-prep doc at `techne/diagnostics/dims_2_3_10_audit_prep_2026-05-11.md` (not yet filed).
  - Track 3 (blind-spot probe coverage test): `ergon/learner/eval/v1_0_eval_set_manifest.json` + `ergon/learner/tests/test_blind_spot_probe_coverage.py` (7/7 PASS, 0.24s). Asserts 5 required BS (001/003/004/005/006) all have `must_have_probe=true` in the Tier-1 eval-set manifest.
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
