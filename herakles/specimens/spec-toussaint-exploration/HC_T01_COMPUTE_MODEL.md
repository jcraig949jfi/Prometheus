# I. HC-T01 COMPUTE MODEL

**Status: derived from recovered parameters. The wall-clock rows are ESTIMATED and must be replaced by a measured benchmark at the shakedown, which is gated behind the section 24 review.**

## Per-run counts, from `PARAMETER_CERTAINTY_TABLE.md`

| quantity | value |
|---|---|
| offspring population lambda | 100 |
| detector samples per individual per generation | 2,000 |
| detector samples per generation | 200,000 |
| generations, Experiment 1 | 1,000 |
| detector samples per Experiment-1 run | 2.0e8 |
| fitness evaluations of the evolution itself, per run | 1.0e5 |
| **detector cost divided by evolution cost** | **2000x** |

That last row is the load-bearing number and it answers the directive's question directly. **The instrument costs two thousand times more than the process it observes.** Running the detector is not a marginal addition to the experiment; it is the experiment, and the evolution beside it is a rounding error.

## Confirmatory set

| quantity | value |
|---|---|
| cells | 4 |
| historical replicates per cell | 10 |
| historical total runs | 40 |
| historical total detector samples at 1,000 generations | 8.0e9 |
| modern replicates per cell, proposed | 30 |
| modern total runs | 120 |
| modern total detector samples | 2.4e10 |

Modern replication is required because the historical n of 10 per cell carried no uncertainty estimate of any kind, and because the unit of analysis is the run. With beta needing a sensitivity arm at 0.01 and the insertion/deletion rate needing one as well, the full grid could reach 4 cells x 2 sensitivity axes x 30 runs = 240 runs and 4.8e10 samples.

## Cost of one detector sample

One sample is: clone the parent genotype, draw and apply Poisson(beta) second-type rewrites, draw and apply Poisson(alpha x length) first-type mutations per sequence, develop for T = 1, then update the statistics. The statistics update dominates. The normalised mutual information matrix over 25 phenotypic variables needs joint counts for 300 unordered variable pairs, each into an 8x8 histogram, so roughly 300 counter increments per sample against roughly 25 to 60 symbol operations for mutation and development.

Estimated 1 to 3 microseconds per sample in compiled code, single core.

## Estimated wall clock, to be replaced by measurement

| scenario | samples | at 1 us | at 3 us |
|---|---|---|---|
| one Experiment-1 run | 2.0e8 | 3.3 min | 10 min |
| historical 40-run grid | 8.0e9 | 2.2 h | 6.7 h |
| modern 120-run grid | 2.4e10 | 6.7 h | 20 h |
| full sensitivity 240-run grid | 4.8e10 | 13 h | 40 h |

Runs are embarrassingly parallel, so on eight cores the modern grid is roughly one to three hours. **This is affordable and is not a reason to reduce the design.**

## Why this matters historically, and it is testable

On 2003 hardware, roughly one core near 1 GHz with no vectorisation, a conservative 20 to 60 microseconds per sample gives:

| scenario | at 20 us | at 60 us |
|---|---|---|
| one Experiment-1 run | 1.1 h | 3.3 h |
| the 40-run ablation grid | 44 h | 5.5 days |

So the detector was affordable for the **single demonstration run** of Experiment 1 and would have cost days of continuous computation across the **forty runs** of Experiment 2. That is a concrete, quantitative and falsifiable explanation for why the cell is missing, and it is a better explanation than oversight. It is recorded here as a hypothesis about the historical record, not as a finding of this seat.

## Storage

| item | per run at 1,000 generations | 120 runs |
|---|---|---|
| five scalars, best and population mean, per generation | 80 KB | 10 MB |
| population-mean 25x25 MI matrix per generation, float32 | 2.5 MB | 300 MB |
| per-individual MI matrices per generation | 250 MB | 30 GB |

**Decision fixed now:** store the population-mean matrix every generation, and per-individual matrices only at preregistered checkpoints. Thirty gigabytes of per-individual matrices is not justified by any preregistered analysis.
