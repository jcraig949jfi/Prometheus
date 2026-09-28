# Q2: a fair neutral baseline for donor acquisition (design, pilot, recommendation)

Computational artificial life: integer programs on the z8 VM. Nothing biological. Delegate for Nestor, 2026-09-28.

**Question.** Does NPE's actual variation-selection process (pair-tape soup, ATOMIC runner) reach a COMPETENT
genome more efficiently than a neutral process that has the same mutation opportunities, instruction
distribution, starting material, evaluations and environment? The prior art is Knierim et al. 2026 (BFF): a
mutation walk needed 9.9e5 programs tested and a tuned byte distribution 9.4e4, against 5e6 for the soup.

## 1. What the soup actually does (read from the code, verified)

- **Mutation.** Every epoch, every live organism is paired (pop 256, no gating under QUALITY_DIVERSITY) and
  receives exactly ONE persisting `world._mutate` call. That is the ATOMIC write-back of its pre-interaction
  genome, mutated. The tape result is kept only when the predecessor criterion calls the interaction a
  replication, in which case the organism is overwritten by the (mutated) copy.
- **No other population change.** There is no death, reaping, immigration or task-based culling in cells
  7ae3 and ffa6 (the population never exceeds the cap).
- **What "selection" is.** It is only overwriting, plus copy errors inside LDIR. Before the first
  replication event, the soup's genomes follow **exactly the neutral mutation process**.
- **The ruler.** Every 100 epochs, every distinct live genome is screened: 4-seed stage 1, 20-seed COMPETENT,
  fresh registers.

## 2. Design

**Neutral process** (`neutral.py`, a subclass of `world.Runner` in which `step()` is replaced):

| factor | soup | neutral | how it is matched |
|---|---|---|---|
| starting material | `Runner.run()` initialisation, seed 16_000_000+s | the same code, same cell, same seed | identical initial 256 genomes. PLANT uses run_pl's planting RNG and rule verbatim |
| instruction distribution | uniform bytes (plus plant) | the same | same generator |
| mutation operator and rate | `_mutate`, 1 persisting call per organism per epoch | `_mutate`, 1 call per organism per epoch | same function and rate. Independent RNG draws (seed-paired, not draw-paired) |
| epochs | 2,000 | 2,000 | same |
| evaluations | `run_dd.screen` of distinct live genomes every 100 epochs | the same function, same schedule | identical ruler, VM and seed tags (label differs) |
| VM | STOCK / DENSE / SHAM | the same, per arm | one neutral walk is screened under all three VMs. `_mutate` does not depend on the VM because `dis` is unpatched |
| interaction, copying, carried registers | yes | none | **the treatment** |

**Evaluation.** One evaluation is one distinct genome screened by the ruler at a checkpoint. It is counted
identically in both processes. Program executions are also reported, as a separate count:

- The soup runs 256 slices per epoch, about 5.1e5 per run.
- The neutral process runs none outside the ruler.

A Knierim-style "programs tested" count therefore favours the neutral process by orders of magnitude. That
count is a cost statement, not a fairness statement.

**Endpoint.** The first checkpoint with at least 1 COMPETENT genome, reported as a hazard:

- per run-checkpoint at risk (discrete time; runs censored at epoch 2000);
- per evaluation at risk.

A secondary endpoint is the per-carrier-screen hazard lambda from ACCESSIBILITY.md section 2. It removes the
difference in how long copy encodings persist.

**Primary contrast.** The rate ratio soup/neutral per arm (DENSE, PLANT). PLAIN and SHAM are 0 vs 0 and
uninformative. The test is a conditional binomial on the pooled events given exposure.

**Alternative considered: replaying the soup's own mutation stream.** Log each persisting `_mutate` diff in
the soup and apply it to a non-interacting twin population. This is **not recommended as the primary
design**:

- After the first overwrite, the soup's diffs refer to a genome with a different frame and content.
- In 7ae3 an operand-site index is meaningless on a different skeleton.
- It forces draw-pairing only while both populations are identical, which is exactly the uninformative part.

Independent walks with the same operator, count, material and ruler match the stated opportunities without
this artefact. The replay variant could serve as a sensitivity check on runs with no replication events.

## 3. What would make the comparison unfair, and how the design prevents it

1. **Different evaluation counts or sampling.** The soup converges, so it has fewer distinct genomes per
   checkpoint (DENSE soup 3.4e5 evaluations vs 4.6e4 per 12 neutral runs). The design reports hazard per
   evaluation and per checkpoint, and both processes use the same ruler and schedule.
2. **Different mutation supply.** Matched per organism per epoch. The soup has **extra** variation the
   neutral process lacks: copy-error bit flips, and wholesale skeleton replacement by overwriting. In 7ae3
   overwriting is the only way to change an opcode, because OPERAND never mutates opcodes. This extra supply
   belongs to "the variation-selection process" being tested, so it is counted as part of the treatment, and
   the soup's replication-event count is reported.
3. **Different starting material.** Identical by construction (same `Runner` initialisation and seed).
4. **Detector leak.** The ruler resets registers, so neither process benefits from carried state. The soup's
   in-world copies (p11_events) are **not** the endpoint.
5. **Stopping or selection on the outcome.** A fixed 2,000 epochs and all checkpoints are screened.
6. **A neutral process that cannot reach the target, making the comparison trivial.** Excluded empirically:
   the neutral walk does reach COMPETENT genomes (section 4).
7. **Residual non-equivalence that cannot be removed.** The soup's organisms execute every epoch and the
   neutral process does not, so the neutral process is not "the soup minus selection" in execution cost. The
   comparison answers the evaluation-matched question, not a compute-matched one. Under compute matching the
   neutral process would win by about 1e2-1e3x (see 1).

**Conclusion on fairness.** A fair comparison **is possible** on the evaluation-matched endpoint, because the
soup's only departures from a neutral walk are overwriting and copy errors. It is **not possible** to match
the soup's variation exactly (copy-generated skeleton changes have no neutral counterpart), and this must be
stated as part of what the treatment is.

## 4. Pilot (neutral process only, seeds s = 0..5, both cells; 2 processes, about 55 min wall)

`results_neutral/*.json`, `compare.json`, `neutral_lambda.json`. The soup numbers are read from the W1/P2
result files on the same seeds.

| arm | soup, paired 12 runs | neutral, paired 12 runs | soup, all 96 | soup first-L2 epochs (paired) | neutral first-L2 epochs |
|---|---|---|---|---|---|
| DENSE | 7/12 (hazard/ckpt 0.044) | 4/12 (0.022) | 49/96 | 100, 500, 800, 800, 1100, 1200, 1300 | 200, 300, 600, 800 |
| PLANT | 3/12 (0.015) | 2/12 (0.009) | 32/96 | 200, 400, 1600 | 100, 2000 |
| PLAIN | 0/12 | 0/12 | 0/96 | - | - |
| SHAM | 0/12 | 0/12 | 0/96 | - | - |

- **Hazard per evaluation.**
  - DENSE: soup 1.7e-4 (95% 6.9e-5 to 3.6e-4) vs neutral 8.7e-5 (2.3e-5 to 2.2e-4).
  - PLANT: soup 5.8e-5 vs neutral 3.5e-5.
- **Per-carrier-screen hazard, pooled over DENSE and PLANT.** Soup 10 events / 27,446 carrier-screens
  = 3.6e-4. Neutral 6 / 28,788 = 2.1e-4.
  - Rate ratio about 1.75. Conditional binomial, one-sided **p = 0.20**. There is no evidence that the soup
    finds competence faster.
- **Evaluations to first COMPETENT genome (inverse hazard).** Soup about 5.8e3 (DENSE, paired) and about
  7.0e3 (DENSE, all 96). Neutral about 1.1e4.
  - Measured as program executions, the soup spends about 5e5 slices per run. The neutral process spends
    about 5e3 ruler screens per run and no slices.
- **Material matters more than process.** The neutral walk reproduces the arm ordering: DENSE > PLANT >
  PLAIN = SHAM = 0.
- **Where the soup's advantage lies, if any.** Partly in spreading: soup stage-1 counts reach 700-1,900 in
  runs with copying, while the neutral process has at most 5 stage-1 genomes per run. That is the Knierim
  reading: interaction matters for spread, not for first appearance.
- **Note.** In paired runs, first appearance differs in timing and even in which seeds hit, so the seed
  pairing adds little. Treat the runs as independent draws.

## 5. Recommendation

**Run the full comparison.** It is cheap, and the pilot shows it is informative (the neutral hazard is not
zero). It should be run as follows:

- **Scope.** Neutral process, seeds s = 0..47, both cells, RANDOM material (screened under STOCK, DENSE and
  SHAM) and PLANT material. 96 runs per material, of which 24 are done.
  - Soup arms are read, not re-run.
- **Compute.** RANDOM (3 VMs) about 260 s per run and PLANT about 130 s per run on this host under load, so
  (84 + 84) runs ≈ 84 x 390 s ≈ **9.1 CPU-hours**. That is about 4.6 h on 2 processes or about 1 h on 10.
  - `neutral.py` skips runs already done: `python neutral.py RANDOM 7ae3 6 48`, and so on.
- **Expected power.** The neutral process expects about 32 (DENSE) + 16 (PLANT) events, against 81 in the
  soup. The standard error of log(RR) is about sqrt(1/48 + 1/81) = 0.18, which detects a rate ratio of 1.7
  at about 80% power.
- **Pre-register before launch.** Primary endpoint: pooled per-evaluation hazard ratio, soup/neutral, for
  DENSE and PLANT. Proposed thresholds:
  - SOUP_FASTER if the lower 95% bound of the ratio is > 1.
  - NO_ADVANTAGE if the upper bound is < 2.
  - WEAK otherwise.
- **Report alongside:** per-carrier lambda, per cell; the soup's replication events before first COMPETENT;
  program-execution counts.
- **Optional sensitivity check.** A neutral arm with copy-error-equivalent extra bit flips (the soup's LDIR
  cmr applied to overwritten genomes) would separate "copying adds variation" from "copying spreads partial
  copiers".

**Bottom line of the pilot.** On an evaluation-matched endpoint, a neutral mutation walk from the same
material reaches fresh-start COMPETENT genomes at a hazard within about 2x of the soup's (not significantly
different). Encoding persistence and frequency (the material and the VM) set the rate. Nothing yet shows that
pair-tape variation and selection help donors first appear.

Files: `neutral.py`, `compare.py`, `neutral_lambda.py`, `results_neutral/` (24 runs), `pilot_*.log`,
`compare.json`, `neutral_lambda.json`.
