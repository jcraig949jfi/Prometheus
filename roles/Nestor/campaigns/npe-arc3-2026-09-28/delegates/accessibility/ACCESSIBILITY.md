# Q1: mutational accessibility of usable copy behaviour (NPE ARC3 delegate)

Computational artificial life: integer programs on the z8 VM. Nothing biological. Delegate for Nestor, 2026-09-28.
Every number below comes from a JSON file in this directory. The campaign code was only read. The VMs are the
stock `z8`, `run_dc.dense_z8` (0xE5/0xE7 = LDIR/LDDR) and `run_sh.sham_z8`. The ruler is `run_dd.assay_one` /
`screen`: fresh zero-register start, donor on either side, a 4-seed stage 1, then COMPETENT iff at least 10 of
20 seeds pass. At most 2 processes were used.

## 0. The operator, verified (`operator_check.json`, `acc_lib.verify_operator`)

The brief's description is partly wrong for these two cells. Both cells use `mutation_operator=OPERAND` and
`mutation_locality=LOCAL`, and runs use `atlas_axis=NONE`, which means no recombination and no indels.

- **7ae3 (Z8_64).** Each byte mutates at rate 0.002, but OPERAND skips every opcode position of the linear
  disassembly. Out of 2,000 genomes, 0 mutated sites were at opcode positions and 0 genomes changed their
  linear frame. The program skeleton (every opcode byte, including every ED prefix and every 0xE5/0xE7 at an
  opcode position) is therefore **frozen for the lifetime of a lineage**. Only copying can change it.
  - A random 64-byte genome has only about 8-9 operand bytes. A neutral lineage therefore receives about
    **34 effective mutations in 2,000 epochs** (neutral pilot: 34.2 changed `_mutate` calls per lineage).
  - The second byte of `ED xx` is an operand, so `ED B0` can arise from an existing `ED` opcode by operand
    steps (a +/-8 delta, a bit flip, or a 10% uniform draw), and can be lost the same way.
- **ffa6 (Z8_SLOTTED).** Each 4-byte slot mutates at rate 0.008. OPERAND edits byte 1, 2 or 3 of the slot and
  never byte 0.
  - If the chosen byte is a linear-disassembly opcode, it is replaced uniformly (`perturb(j, j in opcodes)`).
    So **opcode positions at slot offsets 1-3 do mutate, and the frame does shift**: 917 of 2,000 mutated
    genomes shifted, at an inflated test rate.
  - A neutral lineage receives about **239 effective mutations in 2,000 epochs**.
- **Mutations per epoch in the soup.** The ATOMIC runner gives each live organism exactly one persisting
  `_mutate` call per epoch. The base `_pair_interact` also calls `_mutate`, but the ATOMIC write-back
  discards that result unless the organism was overwritten.
- **Population in the soup.** In these cells nothing dies or is reaped (the population stays at 256).
  "Selection" is therefore only overwriting by a replication event under the predecessor criterion.

For one-mutant and two-mutant neighbourhoods, `acc_lib.point_mutant` is `_mutate` conditioned on exactly one
event: in 7ae3 a uniform operand site with operand perturbation; in ffa6 a uniform slot, then byte 1 to 3,
perturbed as an opcode if it is a linear opcode.

## 1. Neighbourhood statistics

### 1a. Arm initial material (`q1_initial.json`; 400 genomes per row, plus 1 one-mutant and 1 two-mutant each)

| cell / material / VM | carries copy encoding | at a linear opcode position | block copy executes from fresh start | stage 1 (self / m1 / m2) | COMPETENT (self / m1 / m2) | best fid >= 0.5 |
|---|---|---|---|---|---|---|
| 7ae3 RANDOM STOCK | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0 |
| 7ae3 RANDOM DENSE | 157 | 143 (all frozen) | 141 | 0/0/0 | 0/0/0 | 12 |
| 7ae3 RANDOM SHAM | 0 | 0 | n/a | 0/0/0 | 0/0/0 | 30 |
| 7ae3 PLANT STOCK | 400 | 338 | 235 | 1/2/0 | 0/0/0 | 19 |
| ffa6 RANDOM STOCK | 1 | 1 | 1 | 0/0/0 | 0/0/0 | 0 |
| ffa6 RANDOM DENSE | 171 | 154 (45 frozen at offset 0) | 133 | 0/0/0 | 0/0/0 | 15 |
| ffa6 RANDOM SHAM | 1 | 1 | n/a | 0/0/0 | 0/0/0 | 32 |
| ffa6 PLANT STOCK | 400 | 338 | 218 | 0/0/0 | 0/0/0 | 9 |

- **Competence is more than two operator steps from random material in every arm.** 0 of 3,200 genomes and 0
  of 6,400 mutants were COMPETENT, and stage 1 fired only 3 times, all in 7ae3 PLANT.
- **Execution of a copy is not the bottleneck.** A block copy executes from a fresh start in 35-59% of dense
  and planted genomes. What is missing is register setup (BC, DE, HL) that points the copy at the partner half.
- **Partial-copy scores do not discriminate arms.** SHAM, which acquires 0 of 96, has the highest share of
  random genomes with best fid_final >= 0.5 (30-32 of 400), because its random block writes land donor-like
  bytes by chance. `best_fid_final` should not be used as an accessibility proxy.

### 1b. Around competent and near-miss genomes (`q1_focal.json`; corpus `q1_partial.jsonl`, 24 focal x 24 m1 + 24 m2)

| stratum | focal rerun rate | m1 COMPETENT | m2 COMPETENT | m1 stage 1 | executed copy site |
|---|---|---|---|---|---|
| DENSE 7ae3 competent | 0.86 | 0.72 | 0.61 | 0.84 | alias, frozen 24/24 |
| DENSE ffa6 competent | 0.91 | 0.80 | 0.66 | 0.84 | alias: 15 mutable, 7 frozen |
| PLAIN 7ae3 competent (1 run, 15000022) | 0.94 | 0.73 | 0.56 | 0.73 | `ED B8`, B8 mutable 24/24 |
| DENSE 7ae3 near-miss (0 < rate < 0.5) | 0.34 | 0.22 | 0.18 | 0.68 | alias, frozen 22/24 |
| DENSE ffa6 near-miss | 0.37 | 0.27 | 0.21 | 0.76 | alias |
| PLAIN 7ae3 near-miss (n=1) / PLAIN ffa6 competent (n=1) | 0.35 / 0.50 | 0.38 / 0.21 | 0.21 / 0.42 | - | - |

- **Neutral paths exist.** Competent copiers sit on a broad neutral network: 72-80% of one-mutants and 56-66%
  of two-mutants stay COMPETENT. The spread between focal genomes is large (per-focal m1 share from 0.0 to 1.0).
- **Partial copiers are real stepping stones.** Near-miss genomes, which carry an intact copy site, become
  COMPETENT in one step 22-27% of the time. Most of their neighbours pass stage 1.
- **Losing the copy site is a trap.** The site was knocked out (set to 0x00) in 8 competent genomes per
  stratum, followed by 6 neutral walks of up to 12 operator steps each. **0 of 144 walks regained competence.**
  - In 7ae3-dense the alias is at a frozen opcode position, so the loss is **irreversible** without copying.
  - In 7ae3-plain the lost `B8` operand needs several specific operand hits among about 9 mutable sites.
- **Opposite persistence of the two encodings in 7ae3.** The one-byte alias at an opcode position can never
  be mutated away. The two-byte `ED B0/B8` keeps its `ED` fixed but its second byte mutates freely. This is
  why planted copy encodings decay:
  - PLANT carriers fall from about 210 to 7-21 per 256 over 2,000 epochs, in the soup and in the neutral
    walk alike (`compare.json` pairs).
  - Dense carriers stay flat (about 100 per 256) in the neutral walk.

## 2. Predictive model (`model.py`, `model.json`)

Two one-parameter models were fitted on one arm and tested on the other arms (out-of-arm test):

- **M0 raw frequency.** Predictor: the share of genomes carrying a copy encoding at epoch 100.
- **M1 carrier exposure.** E = the sum, over checkpoints at risk, of screened genomes carrying a copy
  encoding. Each carrier-screen converts to a first COMPETENT genome with hazard lambda.
  - This is frequency times persistence. It is the simplest quantity that includes the decay described in 1b.

| arm | observed runs with COMPETENT | M1, fit on DENSE | M1, fit on PLANT | M0, fit on DENSE | M0, fit on PLANT |
|---|---|---|---|---|---|
| DENSE | 49/96 | (49.0 fit) | **54.8** | (48.8 fit) | 18.6 |
| PLANT | 32/96 | **28.6** | (32.0 fit) | 70.8 | (32.2 fit) |
| PLAIN | 0/96 | 0.29 | 0.33 | 0.37 | 0.11 |
| SHAM | 0/96 | 0.31 | 0.34 | 0.39 | 0.12 |

- **M1 predicts both cross-arm tests within about 15%.** M0 misses by a factor of 2.2-2.6 in both directions:
  raw frequency ranks PLANT (100% carriers at t=0) above DENSE (40%), which is the wrong order.
- **The fitted hazard is nearly arm-independent.** lambda = 3.4e-4 (DENSE) and 3.8e-4 (PLANT) per carrier-screen.
  - Within a cell the arms agree: 7ae3 2.4e-4 vs 2.7e-4; ffa6 4.6e-4 vs 6.2e-4.
  - The cells differ by about 2x, consistent with ffa6's 7x larger mutational throughput and mutable opcodes.
- **PLAIN and SHAM are predicted near 0.3 each**, consistent with 0/96. The earlier W1 stock arm observed 1/96
  (seed 15000022).
- **Interpretation.** Acquisition is controlled by how many genome-screens carry an executable copy
  encoding, integrated over time. A 1-byte alias beats a planted 2-byte copy because the alias **persists**
  (it is frozen in 7ae3 and mostly neutral in ffa6), not because it is more frequent at the start.
  - Once a carrier exists, the conversion hazard per carrier is the same whether the copy is 1 byte or 2 bytes.
  - The SHAM arm's block-write density adds nothing, which M1 predicts because SHAM has no carriers.

## 3. Caveats

- **E is not fully exogenous.** In the soup, copying can raise or lower the carrier count before the first
  COMPETENT genome. For example, ffa6 PLANT carriers fall faster in the soup than in the neutral walk.
  - The neutral pilot gives a partly exogenous check: its per-carrier lambda is 2.2e-4 (DENSE) and 1.9e-4
    (PLANT), the same order and again arm-independent (`neutral_lambda.json`).
- **Only two arms carry information.** PLAIN and SHAM have 0 events, so M1 is tested on two informative arms,
  with one parameter each way. It is a small model on four data points, not a law.
- **The competent corpus is dominated by DENSE.** The PLAIN competent stratum is 24 genomes from a single run.
  No planted-arm competent genomes are stored (x_p2_plant keeps counts only), so no PLANT-copier
  neighbourhood was measured.
- **These are neighbourhoods under the fresh-start ruler.** In-world competence with carried registers is a
  different quantity (see the corpus analysis, Q2 and Q3).
- **Knockout walks are 12 steps, so "trap" means "not reversible on short timescales".** In 7ae3-dense it is
  strictly irreversible without copying, because the site is frozen.
- **Near-miss here means sub-threshold corpus genomes that were competent in the world screen.** True
  never-competent near-misses (stage-1 passes) are not stored in any result file.

Files: `acc_lib.py`, `q1_landscape.py` (initial, focal), `model.py`, `neutral_lambda.py`, `q1_initial.json`,
`q1_focal.json`, `model.json`, `neutral_lambda.json`, `operator_check.json`.
