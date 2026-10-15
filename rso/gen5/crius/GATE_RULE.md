# C-019-T021 Crius selection gate -- frozen rule and predictions

Author: Cadmus[harry1-c619844e], claude-sonnet-5-5 (Q2). Status: written and committed BEFORE any condition of this gate is run.
Role: temporary READ-ONLY compatibility steward of the frozen Crius interface (directive s2B). Nothing under `crius/` or
`roles/Crius/` is edited; no native physics change; none of the forbidden rescue moves (lower E/H, more budget, parts in the
population, C3). Everything this packet adds lives in `rso/gen5/crius/`.

## 1. What is read, and what I already know before predicting (honest preamble)

Reading `crius/` BEFORE writing this rule showed two facts the candidate contract (`rso/gen5/CANDIDATE_CONTRACT.md` s7.1) did not state:

1. `crius/configs/c1.json` has no `substrate` key. `vm.set_substrate({})` therefore leaves `typed_procedures=False`, so the rung-B
   silent calibration (`vm.py:428-429`, `_calibrate` `vm.py:461`) is OFF in the frozen C1 world and in the 18_021_001..003 smoke.
2. Every Python baseline in `crius/baselines_c1.py` (including `ProcedureReuseC1`) calibrates by its own metered probes
   (`classify`, `baselines_c1.py:~150`); none reads `env.last_primitive` / `observation()["last_primitive"]`
   (`grep last_primitive crius/baselines_c1.py` -> no hit). The label (`world_c1.py:81`, `env.py:97-98`) is exposed but
   unread by every organism in this gate.

So I expect the leaks to be INERT for the constructed positive. That is a prediction about a read-only fact, so the gate still has to
show it by execution, and it does not by itself qualify the world (demand, ablation, transplant, near-misses still have to hold).

## 2. Worlds (all on the frozen C1 relay world and the C1 `gate` stream namespace; every label says what changed)

| id | label | label visible to organism | substrate calibration | construction |
|---|---|---|---|---|
| W1 | ORIGINAL_C1 = CF_NOCAL | yes | OFF | `crius/configs/c1.json` verbatim (this IS the world with calibration disabled; c1.json is rung A) |
| W2 | EXTERNAL_FILTER (a) | no | OFF | W1 + `TaskRun` subclass that returns -1 for `observation()["last_primitive"]` and the INPUT field; engine transitions untouched |
| W3 | RUNGB_SUBSTRATE (original runtime semantics, rung B) | yes | ON | c1.json + `substrate={typed_procedures:true, psim:false, version:"c2-typed-v1"}` (the c2b flags only; c2b's budgets/paired streams are NOT applied) |
| W4 | RUNGB + EXTERNAL_FILTER (a) | no (to the organism) | ON (the runtime still sees the truth) | W3 + the same filter; NOT leak-free at the runtime level |
| W5 | COUNTERFACTUAL_RUNTIME 'Crius-CF-nocal' (b), and (c) both | W5b yes / W5c no | OFF | W5b is semantically W1; W5c is semantically W2. Reported as aliases, with a test that their replay hashes equal W1/W2 |

Leak-controlled worlds for the gate rule: **W2 (filter), W1=W5b (calibration off), W5c=W2 (both)**. W3 is the original rung-B
runtime (both leaks live), W4 is reported for completeness; neither can qualify the world. Rung B's calibration is a RUNTIME
SEMANTIC, so W5 is never reported as the original rung-B world; W1 is the original C1 world.
Semantics test (required before any result is read): for every player and seed, replay hashes of W1 and W2 are byte-identical
(filter changes the observation only), and the number of reads of `last_primitive` by any player in W1 is recorded (expected 0).

## 3. Conditions and players

Positive: `PROCEDURE_REUSE_C1` (`baselines_c1.py:98`). Competitors / near-misses: `QUIT_C1`, `TABLE_MEMO_C1`, `PROCEDURE_NOCAL_C1`
(permutation-blind near-miss), `ENUMERATE_C1` (search-effort competitor). Lifetime conditions (`evaluate.run_lifetime`): ACCUMULATED,
FRESH, WORKSPACE_SCRAMBLED. Causal controls from the stage-D snapshot (`evaluate.causal_controls`, snapshot index 32; remainder =
tasks 32..49, 18 tasks): CODE_ONLY, COMPUTE_MATCHED, STORAGE_MATCHED, ARTIFACT_ABLATION (each block, ALL), ARTIFACT_TRANSPLANT,
FULL_WORKSPACE_TRANSPLANT. The leak-free reuse positive is `ProcedureReuseC1` itself (own metered probing, no label), constructible
without changing physics; no separate leaky variant is built (non-goal: not needed to decide the gate).

Seeds: **19_020_001 .. 19_020_005** (5 lifetimes; disjoint from 1, 201-203, 301-303 and 18_021_001..003), suite `gate`.
Unit of analysis: the LIFETIME (50 dependent tasks; no task-level pooling, no p-values across tasks).
All quantities are exact deterministic counts of successes; there is no sampling, so a lifetime either meets a threshold or not.

## 4. Frozen decision rule (margin fixed here; not tuned after data)

Let S(x) be the successes of x over the 18-task remainder (tasks 32-49), and T(x) successes over the 50-task lifetime.
For a world W and seed s the lifetime PASSES iff ALL of:

- P1 (demand, remainder): S(REUSE ACCUMULATED) - max(S(CODE_ONLY), S(COMPUTE_MATCHED), S(STORAGE_MATCHED), S(ACCUMULATED of QUIT, TABLE_MEMO, NOCAL, ENUMERATE)) >= **6** (one third of the remainder).
- P2 (lifetime): T(REUSE ACCUMULATED) - T(REUSE FRESH) >= **10**, and T(REUSE ACC) - T(REUSE SCRAMBLED) >= **10**.
- P3 (ablation removes it): with G = S(ACC) - S(CODE_ONLY): S(ABLATION_ALL) <= S(CODE_ONLY) + 0.2 G, AND at least one single-block ablation leaves S <= S(ACC) - 0.5 G. (All per-block values are tabulated.)
- P4 (transplant carries it): S(ARTIFACT_TRANSPLANT) >= S(CODE_ONLY) + 0.8 G.
- P5 (near-misses fail): for NOCAL, TABLE_MEMO, QUIT: T(ACC) - T(FRESH) <= 3 and S(ACC) - S(CODE_ONLY-of-that-player) <= 2.

World disposition: **QUALIFIED** only if every leak-controlled world (W2, W1=W5b, W5c) passes in **5/5** lifetimes (the packet text asks >= 3/3; the
frozen rule is stricter, 5/5, to leave room for none to be dropped). **NARROWED** if W1 passes but W2 does not (or reverse: the gain depends on label
visibility or its absence), or the gain is real in the positive but P3 or P4 fails. Otherwise **WORLD_DEMAND_NOT_QUALIFIED**. W3/W4 never
upgrade the disposition. The rule is applied unchanged to the instrument-failure probes below; if it also passes a probe it must fail, the rule is
non-discriminating and the disposition is NARROWED at best.

Falsifiability probes of the RULE itself (rso/qualify/FALSIFIABILITY.md items 4-6): apply P1-P5 with QUIT, TABLE_MEMO and NOCAL each substituted
as the "positive" (all three must fail; `constant_passes`/`near_miss_rejected`), and with the stored workspace scrubbed (WORKSPACE_SCRAMBLED)
instead of the artifact (must lose the gain).

## 5. Predictions (recorded now, before any condition runs)

1. Semantics test: W1 and W2 byte-identical for all players/seeds; label reads by players = 0. (Confident, ~95%.)
2. REUSE ACC succeeds on ~48-50/50 tasks in W1 and W2, FRESH 24-35; identical numbers in W1 and W2 (the leaks do not touch the positive).
   W3 differs from W1 only in cost (the substrate calibration block and `blocks.cost`), successes within +-2.
3. Remainder: REUSE ACC 18/18 (or 17); CODE_ONLY, COMPUTE_MATCHED, STORAGE_MATCHED ~5-6 (smoke: 5-6); ABLATION_ALL ~ CODE_ONLY; single-block ablation of
   block 0 (calibration) as damaging as ablating all (smoke: block 0 only); TRANSPLANT ~ ACC.
4. NOCAL / TABLE_MEMO / QUIT: no gain (ACC ~ FRESH; QUIT ~19-20; smoke). ENUMERATE: no reuse gain (cannot exceed ~6 in remainder).
5. Therefore the rule PASSES in W1 and W2 in 5/5 (disposition QUALIFIED as a world-demand statement for a CONSTRUCTED positive),
   and the leak hypothesis (CANDIDATE_CONTRACT s7.1) is refuted for the constructed positive: it is inert there. The more probable failure is not world
   demand but accessibility (Capability A/B ladder): native search has no Rung-1 path to A (prior 0/36), and a QUALIFIED world
   still licenses only constructed-positive attribution, never discovery (directive s3, "Discovery").
6. Honest uncertainty: an unforeseen interaction (e.g. the P1 ENUMERATE competitor reaching the remainder because the tasks are low depth) could
   make W1 fail P1; if so the disposition follows the rule, not this prediction.

## 6. Resources and process

One python process, minutes of CPU (5 seeds x 4 worlds x 5 players, `smoke_crius` measured 5.5 s for 3 seeds x 4 players). No search is run. A bounded
probe of the native search code for a Rung-1 path to A is read-only plus at most a few minutes (command committed with output) -- see SELECTION.md.
