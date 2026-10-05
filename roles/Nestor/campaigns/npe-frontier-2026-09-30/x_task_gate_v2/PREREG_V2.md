# X-TASK-GATE v2: preregistration and freeze

- **Seat:** Nestor, on BUCKKEEP (CPU only).
- **Authority:** operator science order of 2026-10-05, verbatim at
  `roles/Nestor/prompts/2026-10-05_xtg_v2_science_order/`. It authorizes the freeze and the execution. No Aporia dispatch
  is needed.
- **Frozen:** at the commit that adds this file, together with `xtg2.py` and `test_xtg2.py` at that commit.
  - The code SHA is recorded in every verdict file (`XTG2_CODE_SHA`).
  - No production row exists before this commit.
- **Historical freeze:** `../x_task_gate/` at 62d30e443 is preserved unchanged and is not executed (its ERRATA file).

## Question

Can task competence propagate through the organisms' own P-11-certified causal replication when the probability of
interaction depends on the competence of the interacting pair? The alternatives are that it appears through injection,
sorting, bookkeeping or a broken competence ruler.

## World (fixed)

- **Cell:** the C-A3-INTERNALIZE ffa6 cell (`run_dd.CELLS['ffa6']`). Overrides:
  - `atlas_axis = NONE`
  - `environment = STATIC` (repair: COEVO_ENV rotated the task away from ADD37 after epoch 25)
  - `reproduction = PAIR_EXECUTION`
  - `pressure = TASK_GATED_INTERACTION`
  - Everything else is the cell's own: Z8_SLOTTED, OPERAND mutation at rate LOW, NICHES_HIGH_MIG (migration has no
    task effect under STATIC), PRIMITIVE self-location, BLOCK copy, tier M (pop 256, 2000 epochs, slice 300).
- **VM and runner:** dense VM (`run_dc.dense_z8()`) and the ATOMIC runner (`run_ds.runner_cls`). One job per process.
- **Task (exact):** FORCED_READ ADD37.
  - Inputs are (v, key, r): v in [0, 255], key in [1, 255], r in {0, 1}.
  - base = v XOR key. The expected answer is base when r = 0 and (base + 37) mod 256 when r = 1.
  - The regime cue is input index 2.
  - Scoring VM: plain z8 (`tasks.z8`), world ops disabled, 512-byte scratch arena, budget 140, UNRESTRICTED output,
    VM cue cost. The answer is the first OUT. These are `tasks.score`'s settings, unchanged.

## Competence ruler (repairs W2-8 D1, D6, D7, D9, D15 and W2-10 D1-D4)

- **Cue-flip USE score `u(g, set)`:** each of 16 matched pairs (v, key) is run twice, with r = 0 and with r = 1. A pair
  counts only if BOTH answers are exact. `u` is the share of pairs that count.
  - The two expected answers always differ, so a program whose answer does not depend on the cue scores exactly 0.
  - That covers reading-but-ignoring (CT_U), echoing base, an always-transform guesser and a copier alone.
- **Episode sets:** GATE (seed 43_777_001) and HELD (seed 43_777_002). Both are fixed and disjoint, and neither is
  seeded by epoch.
- **Competent:** u(GATE) >= 0.75 AND u(HELD) >= 0.75.
- **Gate quantity:** u(GATE) of the organism's CURRENT genome. It is recomputed at every use; no stale value is carried
  across a relabel or a mutation.
- **Cache identity:** (STATIC, transform, read_order, budget, episode-set seed, n_pairs, blake2b-12(genome)).
  - Regression RG-1: the same genome under XOR5A after ADD37 must miss and must score 0.
- **The old ruler (`bridge >= 0.5 and reads >= 3`) is reported beside every row as `bridge_ge_0.5_and_reader`.** It is
  never used in a verdict.

## Provenance and mutation-created competence (repairs erratum D2 and W2-8 D13)

Per organism (the Org object persists on the pair tape; its oid changes at a conversion):

- **prov:**
  - INIT: never converted since epoch 0. It may have mutated in place under ATOMIC, so it is NOT "unchanged since epoch 0".
  - P11: the last conversion onto this half passed the P-11 causal assay.
  - LABEL: the last conversion was accepted by the predecessor criterion only.
- **origin of the current competence:**
  - INIT: competent at epoch 0.
  - P11_TX / LABEL_TX: carried in at a birth from a donor whose PRE-interaction genome was competent. The organism
    inherits the donor's competence root, and P11_TX adds one P-11 transmission hop.
  - P11_CREATED / LABEL_CREATED: competent at a birth from a non-competent donor.
  - MUT: became competent by an in-place mutation.
  - If an organism loses competence, its origin is cleared.
- **Every creation event is logged as a root** (kind, epoch, oid), so "when and how competence first appeared in a
  lineage" is answerable.
- **Tests:**
  - PV-1: transmission.
  - PV-2: MUT.
  - PV-3: a donor mutated in place during the same interaction still transmits from its PRE genome. PV-3 fails on the
    pre-fix code and passes on the frozen code (Flight 1 repair).

## Readouts (live organisms at the final epoch; the share denominator is the live count)

| readout | definition |
|---|---|
| CS | competent share |
| CD | competent and prov = P11 |
| **CD_TX (decisive)** | competent and prov = P11 and origin = P11_TX |
| other shares | label-only, INIT, mutation-created (MUT, P11_CREATED, LABEL_CREATED) |
| descent and events | max causal depth, P-11 events, P11-born share, max P-11 transmission hops |
| interaction | pairs considered and pairs interacted (interaction rate) |
| genomes and roots | genomes of competent organisms with counts; root log; P-11 birth edges (gz detail file) |

- **Trajectory:** snapshots every 10 epochs up to epoch 200, then every 50.
  - `CD_TX_peak` and `CS_peak` are **descriptive only**. No verdict reads them; a peak is a historical event, not a final
    state.

## Constructs (W2-10 bytes, verified equal to `construct.genomes()`)

- **CT_UA (positive):** `ED327DEE405FE5DB0047DB004FDB005779FE02380E78A9477AFE00782802C625D3007678D3007679A4B8C83F4C602745135FECC26DAE628982C868A00D767F86`
- **CT_U (reads, does not use):** `ED327DEE405FE5DB0047DB004FDB005779FE02380578A9D3007678D3007679A4B8C83F4C602745135FECC26DAE628982C868A00D767F86F5E75EB8C61DE6C7F9`
- **COPY_ONLY:** W2-10 `pad(COPIER)` = `ED327DEE405FE579A4B8C83F4C602745135FECC26DAE628982C868A00D767F86F5E75EB8C61DE6C7F93E37FCC35AD85A911BF8E3087BE0E744F289727E2F6266`
  - This is the same 7-byte copier as CT_UA with no task routine. The compact motif `2E001E40E5` is not planted (it was
    not needed; no control zoo).
- **Static known answers (selftest):**

  | construct | u GATE | u HELD | old bridge |
  |---|---|---|---|
  | CT_UA | 1.0 | 1.0 | 1.0 |
  | CT_U | 0 | 0 | 0.75 (reads 3, so it PASSES the old ruler) |
  | COPY_ONLY | 0 | 0 | 0 |

  - The world witness scores 1.0.

## Arms and seeds

| stage | arm | gate | plant (one organism, slot i = 0; world `implant=ACTUAL_GENOME`) | seeds |
|---|---|---|---|---|
| 0 | PAIR_POS | TG | CT_UA | 43_000_000 + s, s < 6 |
| 0 | PAIR_READ_NO_USE | TG | CT_U | same seeds (paired background) |
| 0 | PAIR_COPY_ONLY | TG | COPY_ONLY | same seeds |
| 1 | TG | TG: p = 0.15 + 0.85 * max(u_a, u_b) of the pair | none (random) | 43_100_000 + s, s < 18 |
| 1 | SHUF | the same gate, reading u of two OTHER random live organisms (private RNG) | none | same seeds |

- Flights used 43_900_000 + s. They are excluded from every production readout.
- No range above was used before (repository grep of 43_0xx_xxx, 43_1xx_xxx and 43_9xx_xxx).

## Stage 0 decision rule (frozen; read before any Stage 1 run)

- **PASS** iff ALL of these hold:
  1. At least 3 of 6 PAIR_POS runs have **final** CD_TX >= 0.10 (the erratum's requirement, on the stricter CD_TX).
  2. 0 of 6 PAIR_READ_NO_USE runs have CD >= 0.10, AND 0 of 6 have CS >= 0.10.
  3. 0 of 6 PAIR_COPY_ONLY runs have CD >= 0.10, AND 0 of 6 have CS >= 0.10.
- **If (1) fails: INSTRUMENT_UNREACHABLE.** Stop; Stage 1 is not run (the runner refuses).
  - A descriptive subtype is reported beside it: TRANSIENT_ONLY if >= 3 of 6 PAIR_POS runs reach a CD_TX peak >= 0.10,
    otherwise NOT_FIRING_AT_PEAK_EITHER.
- **If (1) holds and (2) or (3) fails: INSTRUMENT_INVALID_NEGATIVE_PASSED.** Stop.
- **Reported, not gating:** whether each negative arm copies (P11-born share >= 0.10 in >= 3 of 6 runs), which shows
  that its rejection is not vacuous.

## Stage 1 verdict (first matching rule; CD_TX decisive; CD reported as descriptive)

1. **NO_REPLICATOR_REGIME** if TG or SHUF has < 4 of 18 runs with causal depth >= 20.
2. **FLOOR** if < 3 TG runs have CS >= 0.10.
3. **GATE_OR_SORTING_ARTIFACT** if < 2 TG runs have CD_TX >= 0.10.
4. **ENDOGENOUS_TASK_COUPLED** if n_TG(CD_TX >= 0.10) >= 4 AND n_TG >= n_SHUF + 3.
5. **ENDOGENOUS_UNCOUPLED** if n_TG >= 4 AND n_SHUF >= n_TG - 2.
6. **MIXED** otherwise.

## Flight evidence disclosed before the freeze (`flights/`)

These runs used flight seeds only, at production settings, with 2000 epochs.

- **Flight 1** (3 workers, seeds 43_900_000-001) and **Flight 2** (6 workers, seeds 43_900_002-005), PAIR_POS:
  - **Final** CD_TX = 0 in 6 of 6 runs.
  - CT_UA established (depth >= 20) in 3 of 6; in the others the single plant was lost in the first epochs.
  - Where it established, CD_TX rose to about 0.48 by epoch 20 (1-epoch trace) and was 0 by about epoch 70-100.
  - Meanwhile the copier stayed at fixation: P11-born share about 0.95 at the end, causal depth 103-114.
- **Negatives** CT_U and COPY_ONLY: CD = CS = 0 at the final epoch and at every snapshot. This held including 4 of 6
  runs per arm that ran away (depth 91-138).
- **Expected Stage 0 outcome, declared now:** INSTRUMENT_UNREACHABLE (subtype likely TRANSIENT_ONLY or
  NOT_FIRING_AT_PEAK_EITHER).
  - This rests on the observed mechanism: copies of the 40-byte task routine are eroded by mutation.
  - In this world nothing selects for competence on the pair tape. The gate raises a competent organism's
    interaction rate, but every interaction both copies it and overwrites it, and in this world every interaction
    also mutates both halves (ATOMIC).
- **The decisive rule is NOT loosened in response.** It is the erratum's rule on the final state, the same readout
  time Stage 1 uses. A ruler that cannot be shown to fire at the readout time cannot qualify Stage 1.
  - No world parameter (mutation, epochs, gate floor, plant count) is changed in response to the flights.

## Compute

- **Host and receipts:** BUCKKEEP, CPU only, **4 worker processes**. Each `results/stage*/RECEIPT_*.json` records the
  host, worker count, peak RSS per run, start and end.
- **Why 4 workers:** Flight 2 showed that 6 workers give no throughput gain over 3: 12 jobs took 565 s at 6 workers,
  against 6 jobs in 270 s at 3; per-run wall time was 1.75x. 8 is not used.
- **Measured cost:** 85-313 s per run; peak RSS <= 89 MB per worker.
  - Stage 0: 18 runs, about 15 min.
  - Stage 1: 36 runs, about 30-60 min.
- **Hard wall:** 12 h from the production launch.
- **Stop conditions:**
  - Stage 0 failing as above.
  - During Stage 1, only for evidence corruption, a semantic failure, a technical failure that invalidates the
    comparison, or the 12 h wall.
  - A null TG is not a stop condition.
