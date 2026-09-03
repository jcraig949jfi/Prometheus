# Q - KILL CRITERIA

A killed particle is a successful archaeological result. Each criterion below
is stated so that it can fire.

| # | Criterion | Current status |
|---|---|---|
| K1 | Local accessibility descriptors do not distinguish successful precursors from matched controls | UNTESTED - no controls exist |
| K2 | Any descriptor difference disappears under lineage / task / fitness matching | UNTESTED |
| K3 | The descriptor predicts historical labels but not future acquisition under modern reruns | UNTESTED - reruns blocked, parameters UNSPECIFIED |
| K4 | Cheap conventional metrics (fitness, genome length, task count, gestation, viability fraction) predict acquisition equally well | UNTESTED. **Most likely to fire.** Task count alone is a strong free predictor - a genotype holding six of nine functions is visibly nearer EQU. |
| K5 | Ablation / reversion fails to causally alter the signal | UNTESTED |
| K6 | Results dominated by one historical run / survivorship | **ACTIVE NOW.** One population, successful lineage only. See K. |
| K7 | Historical reconstruction ambiguity is large enough to determine the result | **PARTIALLY ACTIVE.** Seven physics parameters UNSPECIFIED. Static analysis on exact recovered genomes is unaffected; anything requiring a rerun is fully exposed. |
| K8 | Modern reconstruction fails to reproduce the known historical phenomenon | UNTESTED - Avida 2.2 not yet compiled |
| K9 | Signal is merely the direct consequence of already holding a near-EQU task combination | **UNTESTABLE TODAY.** Requires post-EQU genotypes (N5), which are in the 345-genotype distributed file we do not hold. |
| K10 | Compute requirements make adequate replication infeasible | NOT FIRING for H1A (order 10^4 evaluations). Unknown for H1B. |

## The two that matter most right now

**K6 is active, not hypothetical.** With a single recovered population and only
its winning lineage, there is no base rate. Any signal computed today is a
property of one survivor.

**K9 is untestable.** This is worse than a firing criterion, because it means
the most banal alternative explanation - the detector notices that pd 101 is
nearly EQU - cannot currently be excluded. A detector that cannot be checked
against its most obvious confound should not be run.

Together these are the reason the gate packet does not recommend RUN_H1A.
