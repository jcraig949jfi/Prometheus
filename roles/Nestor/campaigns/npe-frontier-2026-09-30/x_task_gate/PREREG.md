# X-TASK-GATE: preregistration

- **Seat:** Nestor.
- **Dispatch:** Aporia #1150 (CWO-2026-09-30C s7). It authorizes design and freeze only.
- **Frozen:** at the commit that adds this file, together with `run_xtg.py` at that commit.
- **Execution:** not authorized by #1150. It needs a separate Aporia dispatch. Nothing here has been run: the instrument was syntax-checked only, and no pilot was run.

## Question

Is there task-coupled endogenous organization in NPE's pair-tape replicator regime?

Specifically: when the chance that two organisms interact depends on their task competence (TASK_GATED_INTERACTION), does task competence spread through the organisms' own causal replication?

Or is any competence that appears one of these artifacts?

| Artifact | What it means |
|---|---|
| Gating / sorting | Competent organisms are survivors of the initial soup, never born by replication. Or the gate's effect is an interaction-rate effect, not a coupling. |
| Input | An answer emitted without reading the key byte. |
| Bookkeeping | A birth that the predecessor label accepts but that fails the P-11 causal assay. |
| Seeded | Excluded by design: random populations, no implant. |

## Why this and not a larger design

This choice rests on committed data read before the freeze, and that data is disclosed here.

1. **Z80xAtlas observatory** (z80atlas-2026-09-19/observatory/INDEX.jsonl.gz, matched pressure-flip pairs; old world):
   - The whole TASK_GATED → NONE_IMPLICIT held effect (+0.108 over 223 pairs, PACKET.md) is in EXTERNAL reproduction: +0.25 to +0.37 across worlds.
   - Under PAIR_EXECUTION on PAIR_TAPE it is d = −0.037 over 32 pairs, and held ≥ 0.75 is reached in 2 of those 32.
   - Over all PAIR_EXECUTION/PAIR_TAPE TASK_GATED runs with RANDOM seeding: held > 0 in 21/45, held ≥ 0.75 in 2/45.
2. **C-A3-INTERNALIZE** (dense VM, ATOMIC runner, random populations, native QD pressure):
   - Runaway replication (depth ≥ 20) occurred in 25/72 ffa6 runs and 9/72 7ae3 runs, which is why ffa6 is chosen.
   - Those records carry no competence readout.
3. **C9-H1R and X-H1-GRADIENT:**
   - Under ANSWER_BEFORE_READ, competence is carried by guessers.
   - The ffa6 cell is FORCED_READ, where a guesser scores about 0. A reader ruler is applied anyway.

**Eligibility, declared honestly:** the most likely outcome of Stage 1 is FLOOR or NO_REPLICATOR_REGIME. Three reasons:
- the gate throttles every non-competent pair to p = 0.15, which slows replication;
- competence and endogenous replication have rarely co-occurred in the prior data;
- 18 seeds per arm gives about 6 expected runaway runs at the native-pressure rate.

A FLOOR is a finding for the frontier ("task coupling does not reach the replicator regime at this scale"), but it is not evidence of absence. Stage 0 exists so that the rulers can be shown to pass before Stage 1 compute is spent.

## World (fixed)

- **Cell:** the C-A3-INTERNALIZE ffa6 cell (`run_dd.CELLS['ffa6']`), with `atlas_axis=NONE`. Only `reproduction` and `pressure` are set per arm.
- **VM and runner:** dense VM (`run_dc.dense_z8()`), ATOMIC runner (`run_ds.runner_cls`).
- **Population:** random, no implant.
- **Run length:** 2000 epochs at the cell's tier M parameters.
- **Seeds:** 31_000_000 + s, fresh; no prior run used this range.

## Arms

| Stage | Arm | reproduction | pressure | seeds |
|---|---|---|---|---|
| 0 | EXT_TG | EXTERNAL | TASK_GATED_INTERACTION: the manager takes the most competent of 3 random organisms | s < 6 |
| 0 | EXT_NONE | EXTERNAL | NONE_IMPLICIT: random parent | s < 6 |
| 1 | TG | PAIR_EXECUTION | TASK_GATED_INTERACTION: a pair interacts with p = 0.15 + 0.85 · max(comp_a, comp_b) | s < 18 |
| 1 | SHUF | PAIR_EXECUTION | the same gate, reading max(comp) of two other random live organisms (private RNG) | s < 18 |

Pairs are formed uniformly at random, so SHUF has the same distribution of interaction probability as TG. It differs only in whether the gate is coupled to the competence of the interacting pair. SHUF is the planted null for coupling.

## Rulers

- **Provenance** is recorded at birth:
  - **P11:** an accepted pair-tape replication whose P-11 causal assay passed. P-11 re-executes the donor against a randomized victim.
  - **LABEL:** accepted by the predecessor criterion, but not P-11 causal. This is the bookkeeping class.
  - **EXT:** a manager birth.
  - **INIT:** placed at epoch 0 and never overwritten. This is the sorting class.
- **Competent:** held ≥ 0.5 (disjoint held-out episodes) AND reader. A reader has reads_at_answer ≥ cue_index + 1, meaning the answer follows the key byte.
  - Competence is re-validated once after the run (readout only).
  - `competent_nonreader` is reported beside it.
- **Per-run readouts over live organisms:**
  - **CS:** the competent share.
  - **CD:** the share that is competent AND P11.
  - sorting share and label-only share.
  - held_max_final and max causal replication depth.
- **Regime:** depth ≥ 20.

## Stage 0: planted positive (read alone, before any Stage 1 run)

- **PASS** iff both hold:
  - mean held_max_final(EXT_TG) − mean held_max_final(EXT_NONE) ≥ 0.15;
  - at least 3 of 6 EXT_TG runs have CS ≥ 0.10.
- **What PASS shows:** that the competence ruler, the reader filter and the coupling statistic can pass when coupled selection is known to work. The old-world data shows EXTERNAL/TASK_GATED raising held, with 15/19 reaching ≥ 0.75 on PAIR_TAPE against 7/19.
- **FAIL → INSTRUMENT_UNREACHABLE.** Stage 1 is not run, and no claim is made.

## Stage 1 verdict (first matching rule)

1. **NO_REPLICATOR_REGIME** if TG or SHUF has fewer than 4 of 18 runs with depth ≥ 20. No claim.
2. **FLOOR** if fewer than 3 TG runs have CS ≥ 0.10. Competence is not reached; no claim either way.
3. **GATE_OR_SORTING_ARTIFACT** if fewer than 2 TG runs have CD ≥ 0.10. Competence appears but is not carried by causal endogenous descendants: it is sorting survivors, label-only births or non-readers.
4. **ENDOGENOUS_TASK_COUPLED** if n_TG(CD ≥ 0.10) ≥ 4 AND n_TG ≥ n_SHUF + 3.
5. **ENDOGENOUS_UNCOUPLED** if n_TG ≥ 4 AND n_SHUF ≥ n_TG − 2. Competence descends endogenously, but the coupling of the gate adds nothing beyond the interaction rate.
6. **MIXED** otherwise.

Both positive classes (4 and 5) need a count threshold. An empty or weak readout can only produce 1, 2, 3 or 6.

## Limits, declared now

- Competence is validated every 10 epochs during the run. An overwritten organism carries its predecessor's stale competence until then. The final readout re-validates every organism, but the gate itself acts on the world's own (possibly stale) values.
- The cell is COEVO_ENV: the task is proposed per niche by a coevolving environment. It is not changed here.
- The ATOMIC runner is used because C-A3 used it. Its write-back semantics are part of the world.
- 18 seeds per arm detects only large effects. This is a recurrence bar, not an effect-size estimate.

## Compute

- **Plan:** 12 Stage-0 runs + 36 Stage-1 runs = 48 runs of 2000 epochs.
- **Estimate:** at most about 1085 CPU-s per run, the X-MAT tainted mean. This run is untainted, so that is an upper bound for PAIR; EXTERNAL cost is not measured. The total is about 14.5 core-h, at most 16 (MWO-0004 R2), local, under a skullport:cpu8 lease.
- **Stop rule:** after the first 8 Stage-0 runs finish, project the total. If it exceeds 16 core-h, halt and request budget from Aporia; the sample is never cut.
- **Stage 0 alone** is about 3.6 core-h.
