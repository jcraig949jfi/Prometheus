# N - SFE TRANSLATION PLAN

Do not port Avida into SFE. First reproduce the specimen faithfully; then state
what SFE would add, and where it cannot represent the specimen honestly.

## Mapping

| Historical primitive | SFE equivalent | Fidelity |
|---|---|---|
| Avida world (grid of CPUs competing for cycles) | world identity | CLEAN, provided population size and geometry are recovered - both UNSPECIFIED today |
| genome: string over 26 instructions | genotype identity | CLEAN. Content-addressed hash of the instruction string. |
| point substitution | mutation event | CLEAN |
| insertion / deletion | mutation event, SEPARATE class | CLEAN, but rates UNSPECIFIED |
| parent -> offspring on divide | lineage edge | CLEAN |
| 9-bit rewarded logic vector | phenotype observation | CLEAN, and the natural SFE observable |
| merit = 2^(sum of reward exponents) | derived scalar on the phenotype | CLEAN once the reward table is pinned |
| colony test outcome (viable / not) | failure coordinate | CLEAN |
| update | compute budget / clock | **LOSSY.** An Avida update is a population-wide CPU allocation, not a per-organism step. SFE budgets in Prometheus are per-organism evaluations. These are not interconvertible without population size. |
| phylogenetic depth | checkpoint | CLEAN, and G shows it is the better clock |
| random seed | replay seed | CLEAN in principle; no historical seed survives |
| population dump | fork point | CLEAN |
| ancestral reversion | ablation | CLEAN |
| artifact hash | artifact hash | CLEAN |

## Where SFE cannot faithfully represent the specimen

1. **The update clock.** See above. Any SFE budget claim about this specimen
   must be stated in evaluations and must NOT be silently relabelled as updates.
2. **Population-level selection.** Avida's selection is spatial and
   CPU-allocation-based. Prometheus's D-5-class consumers use a fixed-size
   population with tournament selection. These are different physics, and a
   translation that quietly swaps them produces a different experiment.
3. **The hard 32-bit task threshold.** SFE substrates in Prometheus have used
   graded distance objectives. Grading this specimen would change it (see M).

## What SFE would genuinely add

Replication at a scale the original could not reach: many independent
populations from a common checkpoint, with per-organism lineage and failure
coordinates retained. That is the whole value proposition, and it is worth
stating that it is a **statistical** addition, not a resolution one - Avida's
own analyzer already resolved the one-step neighbourhood (see D).

## Recommendation

**Do not build an SFE world for this specimen yet.** With seven physics
parameters UNSPECIFIED, an SFE port would encode assumptions as if they were
history. Recover the configuration first.
