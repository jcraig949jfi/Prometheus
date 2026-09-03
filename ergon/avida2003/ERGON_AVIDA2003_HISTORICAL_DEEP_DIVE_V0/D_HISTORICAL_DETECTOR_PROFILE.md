# D - HISTORICAL DETECTOR PROFILE

The historical instrument treated as an artifact. This is the most important
document in the pass, because it contains a finding that inverts the directive's
working assumption.

## THE HEADLINE: Avida already had a mutational-landscape analyzer

`source/main/landscape.hh` / `landscape.cc` in the recovered 2.2 tree define
`cLandscape`, which enumerates a genome's mutational neighbourhood and reports:

    GetProbDead()   fraction of one-step mutants that cannot replicate
    GetProbNeg()    fraction deleterious
    GetProbNeut()   fraction neutral (within an explicit neut_max band)
    GetProbPos()    fraction beneficial
    GetAveFitness() / GetAveSqrFitness()
    pos_epi_count / neg_epi_count / dead_epi_count   two-step epistasis
    Process(int in_distance = 1)   distance is a PARAMETER, so k=2 is supported
    ProcessDelete() / ProcessInsert()   insertion and deletion landscapes

So the original investigators could, and did, instrument the local mutational
neighbourhood - including two-step and indel neighbourhoods. **The directive's
premise that one-step neighbourhood analysis is a modern addition is wrong, and
recording that is worth more than the metric would have been.**

## THE ACTUAL BLIND SPOT, located precisely

`landscape.cc` touches `cPhenotype` at exactly four places, and every one of
them reads a scalar:

    line 136  phenotype.GetFitness()
    line 137  phenotype.GetMerit()
    line 138  phenotype.GetGestationTime()
    line 763+ merit, gestation, fitness for output

`landscape.hh` contains **zero** references to tasks. The historical landscape
analyzer is **fitness-valued, not phenotype-partitioned**. It can tell you what
fraction of your neighbours are dead, worse, the same or better. It cannot tell
you **which logic functions** those neighbours gained or lost, nor how many
distinct phenotypes are reachable, nor how that reachable set is distributed.

That gap - and only that gap - is what P-MED, R1 and H1 add.

## The fourteen observables (directive section 4)

| # | Observable | Class | Evidence |
|---|---|---|---|
| 1 | fitness | HISTORICALLY_MEASURED | `cPhenotype::GetFitness`, reported per lineage step in supplementary IV |
| 2 | gestation time | HISTORICALLY_MEASURED | `GetGestationTime`, used in landscape output |
| 3 | logic-function phenotype | HISTORICALLY_MEASURED | 9-bit vector printed for every genotype on the line of descent |
| 4 | mutation effects | HISTORICALLY_MEASURED | `cLandscape` dead/neg/neut/pos |
| 5 | successful lineage ancestry | HISTORICALLY_MEASURED | the entire line of descent is published with genomes |
| 6 | deleterious/neutral ancestral mutations | HISTORICALLY_MEASURED | relative fitness per step in supplementary IV; the paper's central claim |
| 7 | extinct sibling lineages | HISTORICALLY_MEASURABLE_BUT_NOT_REPORTED | Avida can dump populations; none survives in a recovered artifact |
| 8 | local phenotype reachability around arbitrary contemporaries | REQUIRES_MODERN_RERUN | needs contemporaries (absent) AND phenotype partitioning (absent) |
| 9 | distribution of phenotypes reachable from a genotype | **NOT MEASURED, THOUGH THE MACHINERY EXISTED** | `cLandscape` enumerated the neighbourhood but classified it by fitness only. This is the genuine addition. |
| 10 | future acquisition probability from matched contemporaries | REQUIRES_MODERN_RERUN | no artifact supports it; needs forks |
| 11 | population-wide base rate of apparent stepping stones | REQUIRES_MODERN_RERUN | requires population dumps or reruns |
| 12 | change in the mutational neighbourhood before EQU | RECOVERABLE_FROM_SURVIVING_DATA (lineage only) | the 112 recovered genomes can each be landscaped; contemporaries cannot |
| 13 | acquisition cost of subsequent capabilities | REQUIRES_MODERN_RERUN | |
| 14 | failure trajectories of lineages that approached but did not reach EQU | NOT_IDENTIFIABLE from surviving artifacts | this is the survivorship gap; see K |

## Recovered detector strengths Prometheus should adopt (directive section 24)

1. **Distance-parameterised landscape enumeration.** `Process(in_distance)`
   generalises to k>1 with the same accounting. Prometheus's own Gen-1B
   mutational-redundancy work sampled neighbourhoods ad hoc; Avida had a
   parameterised, reusable enumerator in 2005.
2. **Indel landscapes as first-class.** `ProcessDelete` / `ProcessInsert` are
   separate entry points. Prometheus's D-5 substrate has INSERT-complete
   physics and never separated indel from substitution neighbourhoods.
3. **Explicit neutrality band.** `neut_max` makes "neutral" a declared
   parameter rather than an implicit equality test.
4. **Epistasis counters.** pos/neg/dead epistasis at two steps, already
   aggregated.

These go to O as detector parts.
