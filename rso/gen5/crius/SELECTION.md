# C-019-T021 Crius selection gate -- SELECTION

Cadmus[harry1-c619844e], claude-sonnet-5-5 (Q2), temporary read-only compatibility steward of the frozen Crius interface (directive s2B).
Frozen rule + predictions: `GATE_RULE.md` (commit 18b5f7289, before any condition ran). Data: `results/gate_results.json`
(runner `run_gate.py`, 192 s wall, one process), `results/ladder_probe.json` (`ladder_probe.py`, one process), `test_semantics.py` (OK).
Nothing under `crius/`, `roles/Crius/`, Aether, Ananke or C-018 files was edited; no search was run; nothing ran on M2.

## 1. Disposition

**WORLD_DEMAND_NOT_QUALIFIED** -- by the frozen rule, mechanically applied, not tuned.

The rule required every leak-controlled world to pass P1-P5 in 5/5 lifetimes. It passed in **4/5** in every world (seed 19_020_001 fails
P1 and P2 in all six worlds, original and leak-controlled alike). The packet's own minimum (>= 3/3) is not met either on the first three frozen seeds (2/3).
I did not drop the failing seed.

The reading that matters, stated plainly:
- **The two leaks are INERT for the constructed positive.** Hiding the primitive label (EXTERNAL_FILTER) and disabling calibration
  (CF-nocal) leave every number identical to the original C1 world (replay hashes byte-identical, s2). The leak hypothesis of
  `CANDIDATE_CONTRACT.md` s7.1 ("the gain may be largely the leak plus calibration") is **refuted for `ProcedureReuseC1`**
  (it calibrates by its own metered probes and never reads the label; reads by an organism: 0).
- **Where the demand fails it fails for a different reason**: on stream 19_020_001 the positive itself records only 3 templates and never
  solves stage D (0/10 chain3 tasks even ACCUMULATED; accumulated 30 vs fresh 23 over 50, remainder 4 vs CODE_ONLY 2), so nothing there
  separates it from the competitors. This is a per-stream reliability limit of the hand-built positive / task generator (diagnosis read from the
  per-stage table, not tested further), not a label or calibration effect.
- In 4/5 lifetimes the gate is a clean pass: REUSE 49-50/50 vs FRESH 24-36, remainder 18/18 vs best competitor 3-10; ablation, transplant and near-misses behave as required.
Palamedes may treat the 4/5 result as NARROWED ("reuse is rewarded on most but not all streams of the frozen generator, independent of the leaks"); the
recorded disposition remains the rule's.

## 2. Worlds (every counterfactual is labelled; none is reported as the original)

| id | label | label visible to organism | calibration | what it is |
|---|---|---|---|---|
| W1 | ORIGINAL_C1 (= W5b CF-nocal) | yes | off | `crius/configs/c1.json` verbatim; rung A has no `substrate` key, so the `vm.py:428` calibration is already off |
| W2 | EXTERNAL_FILTER (a) | no | off | `adapt.FilteredTaskRun`: `last_primitive` and `observation()["last_primitive"]` return -1; engine transition code (`world_c1.py:77`, `env.py` act) untouched |
| W3 | RUNGB_SUBSTRATE (original runtime semantic) | yes | ON | c1.json + c2b `substrate` flags only (c2b budgets / paired streams NOT applied) |
| W4 | RUNGB + filter (a) | no (organism) | ON (runtime sees the truth) | observation filter only; **not** leak-free at the runtime level |
| W5b | COUNTERFACTUAL_RUNTIME 'Crius-CF-nocal' (b) | yes | off | `substrate={typed_procedures:false}`; semantically W1 |
| W5c | both (c) | no | off | semantically W2 |

Semantics tests (passing; `test_semantics.py`, `results/gate_results.json`): for five players on seed 19_020_002 the full action/object trajectory and replay
hash of W1 = W2 = W5b = W5c; over all 5 seeds x 5 players the replay hashes of W1, W2, W5b, W5c are equal. W3 vs W1 replay hashes differ for the positive in
3 seeds (and NOCAL in 2) because the substrate adds a calibration block the players never read; **successes are identical in all 5 seeds**.
**Reads of `last_primitive` by an organism: 0 in every run (6 worlds, 5 players, 5 seeds);** the engine's own reads (calibration, observation) are counted
separately (`label_reads`).

## 3. Condition tables (REUSE = `ProcedureReuseC1`; T = successes of 50; rem = tasks 32-49, 18 tasks)

W1 = W2 = W5b = W5c (identical, leak-controlled).

| seed | REUSE T acc/fresh/scrambled | rem acc / code-only / compute-m / storage-m / ablate-all / transplant | per-block ablation (rem) | best competitor rem | P1-P5 | pass |
|---|---|---|---|---|---|---|
| 19020001 | 30/23/24 | 4/2/2/2/2/4 | b0 2, b1 3, b3 3 | 2 | nnYYY | **no** |
| 19020002 | 50/24/25 | 18/3/3/3/3/18 | b0 3, b1 7, b2 14, b3 18, b4 10 | 3 | YYYYY | yes |
| 19020003 | 50/29/29 | 18/7/7/7/7/18 | b0 6, b1 14, b2 8, b3 16, b4 18 | 7 | YYYYY | yes |
| 19020004 | 50/36/39 | 18/9/9/9/9/18 | b0 9, b1 17, b2 14, b3 18, b4 18, b5 18 | 10 | YYYYY | yes |
| 19020005 | 49/30/30 | 18/6/6/6/6/18 | b0 6, b1 15, b2 11, b3 10 | 6 | YYYYY | yes |

Competitors, W1 (ACC T / FRESH T / rem ACC), seeds 1..5: TABLE_MEMO 23/23/2, 24/24/3, 29/29/6, 37/37/10, 30/30/6; NOCAL 23/23/2, 24/24/3, 29/29/6, 36/36/9, 30/30/6;
ENUMERATE equal to TABLE_MEMO; QUIT 17/17/0, 19/19/0, 20/20/0, 20/20/0, 19/19/0. None gains from accumulation (ACC = FRESH in 20/20 cells); the 'best competitor'
is search effort, not memory.
W3 (original rung-B runtime) and W4 give the same successes in every cell; only the block set at the snapshot differs (the substrate calibration block is added).
Full per-cell numbers: `results/gate_results.json` (`runs`, `rule`).
Ablating block 0 (the positive's own calibration block) alone removes the whole gain in the 4 passing seeds (rem 3, 6, 9, 6 = CODE_ONLY).

## 4. Falsifiability rows (rso/qualify/FALSIFIABILITY.md)

| control | 1 alternative | 2 pass if alternative true | 3 fail if false | 4 impossible by construction? | 5 privileged access? | 6 discriminates / near-miss |
|---|---|---|---|---|---|---|
| ACC vs FRESH (P2) | lifetime-level learning of the stream | ACC > FRESH | ACC = FRESH | no: near-misses give ACC = FRESH, the positive ACC >> FRESH (4 seeds), seed 1 a small gap -- both outcomes occur | none: counts from task results | NOCAL (permutation-blind) is the near-miss; fails P5 as required |
| WORKSPACE_SCRAMBLED | stored bytes matter, not their content | scrambled keeps gain | scrambled loses gain | no | none | scrambled ~ FRESH (24-39 vs 24-36) |
| CODE_ONLY / COMPUTE_MATCHED / STORAGE_MATCHED | search effort, extra steps or capacity | matched control = ACC | matched control << ACC | no: the three coincide (5/5 seeds) and are far below ACC in 4/5 | none | effort-vs-artifact; identical across worlds |
| TABLE_MEMO | answer-table memorisation | ACC > FRESH | ACC = FRESH | no | reads (start, target): a competitor, not an instrument | gains 0 (ACC = FRESH); fails P5 as required |
| ARTIFACT_ABLATION (each / all) | gain lives elsewhere than the blocks | ablation leaves gain | ablation removes it | no: ablate-all = CODE_ONLY (4 seeds); single blocks vary (b3/b4 sometimes keep it, b0 always removes it) | recipe-predictable: the blocks are hand-built, so ablating b0 is predicted by the recipe (CANDIDATE_CONTRACT s7.3); attribution of a *constructed* mechanism only | P3 passes mechanically; this is not independent evidence of discovery |
| ARTIFACT_TRANSPLANT | gain needs the whole workspace | transplant = CODE_ONLY | transplant = ACC | no | none | transplant = ACC (rem 18 = 18; seed 1 4 = 4): the blocks alone carry it |
| the RULE P1-P5 | -- | -- | -- | `constant_passes` / `near_miss_rejected` analogue: QUIT, TABLE_MEMO, NOCAL, ENUMERATE each substituted as 'positive' in all 30 (world, seed) cells: **0 passes** (`probe_rule`) | none | rule discriminates |
| EXTERNAL_FILTER (leak control) | the label explains the gain | filtered world loses gain | filtered world keeps gain | no: `test_semantics.py` checks the filter hides the label and a unfiltered world shows it | acts on the label channel itself; organism reads = 0 in W1 means it is vacuous for these organisms **by observation** | would bite a VM organism that reads INPUT field 10 (`vm.py:401`); none here does |

Limitation (honest): the filter cannot intercept `vm.py:401` (`regs[a] = env.last_primitive`) selectively without editing `vm.py`, so W4 filters the observation dict
only; W2/W5c hide the attribute entirely, which is valid because calibration is off there.

## 5. Ladder answers (directive s3-s4)

- **Capability A in Crius** (constructed, independent): a *callable stored procedure block* -- the calibration object plus one template block (typed link RECORD ->
  INVOKE), built by `ProcedureReuseC1._record_template` (`baselines_c1.py`) and invoked by `BLK_INVOKE` / `vm.invoke_block`. As native bytecode: `P_REC_INV` (`crius/parts_c2.py`,
  recorder + invoker, ~26 edits from `P_BASE`, per the terminal review).
- **Capability B**: composition by planning in the head over several stored templates (chain2/3/4 tasks, stages C-E): `P_REC_INV_PLAN` (+PSIM/PMATCH; 47 edits).
- **Expressibility (Rung 0)** holds: `ladder_probe.py` (rung-C config `c2c.json`, suite gate, seeds 19_020_001..005, 5/5 lifetimes): `P_REC_INV_PLAN` ACC 37-41 vs FRESH 19-25
  (+14 to +20 in every seed); `P_REC_INV` +0..+3; `P_REC`, `P_INV`, `P_PLAN` alone +0 (ACC = FRESH) -- the same one-link valley / cliff Crius's own review reports
  (`CRIUS_C2_TERMINAL_REVIEW.md` s4). **World demand** for B holds in 4/5 gate lifetimes.
- **Rung-1 path for native search to A**: none that I can find. Read: `search.py` ((mu+lambda) over bytecode programs; mutations replace/arg/const/insert/delete/swap/duplicate, segment
  splice, takeover check) and the review: A is a *link* -- recorder alone and invoker alone score 0 and carry no gradient (review s4: -0.001, -0.002), and the first rewarded
  configuration needs recorder + invoker together (26 edits): a one-link valley. The prior (36 runs across rungs A-D: 0 reproducible ACC > FRESH, 0 complete mechanisms, 0 partials above the
  neutral-edit null) stands. I did not run a search: `search.py` writes under `crius/runs/` (an edit of the frozen lane) and minutes of CPU cannot move a 0/36 prior. At rung B the
  runtime hands calibration to every organism for free (`vm.py:461`), so part of "A" is given by the substrate, which makes A a poor test of *discovery* there.
- **Failure taxonomy** (this world, as measured/read):
  - *search could not find*: yes -- 0/36 native runs under the charter's fixed search budget (not changeable here).
  - *representation cannot express*: no -- `P_REC_INV_PLAN` expresses A and B in the 64-instruction bytecode (ladder probe).
  - *world does not reward*: partly -- rewards reuse in 4/5 gate lifetimes for the hand-built positive, not in 19_020_001; not a label/calibration effect.
  - *instrument would not recognise*: not for the constructed positive (P1-P5 separate it and reject 4 substitutes); unproven for a native mechanism -- ablating an evolved block is not
    recipe-predictable, and nothing here tests a native candidate (DETECTION_UNQUALIFIED for native claims, `CANDIDATE_CONTRACT.md` s7.2).
- What this licenses even if the world were QUALIFIED: **constructed-positive attribution** (directive s3: expressibility, world demand, reuse attribution) -- never a discovery claim.

## 6. Resources and provenance

CPU: `run_gate.py` 192 s wall (one process; 150 lifetimes plus causal batteries); `ladder_probe.py` about a minute (one process); `test_semantics.py` seconds.
Concurrent with T020's detached replay (<= 2 processes on harry1). Base: origin/main efe7bddc7; frozen files read-only; `crius/configs/c1.json` unchanged.
Reproduce: `python -B -m rso.gen5.crius.run_gate rso/gen5/crius/results/gate_results.json`; `python -B -m rso.gen5.crius.ladder_probe rso/gen5/crius/results/ladder_probe.json`;
`python -B -m rso.gen5.crius.test_semantics`.
Sequencing: `adapt.py` and `run_gate.py` were written after GATE_RULE.md was committed and before any condition ran; the rule text was not changed afterwards.
Predictions scored: 1 (semantics identical, reads 0) confirmed; 2 (W1 = W2, W3 within +-2) confirmed (identical); 3 (remainder 18/18) true for 4/5 seeds, seed 1 4/18;
4 (near-misses flat) confirmed; 5 (rule PASSES 5/5) **not confirmed** -- 4/5; the leak refutation part of 5 confirmed. Prediction 6 (an unforeseen failure) is what happened.
