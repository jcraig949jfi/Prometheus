# H - PMED SPEC (phenotypic mutation-effect distribution)

## Neighbourhood definition

For a genome of length L over the verified alphabet of A = 26 instructions, the
one-step substitution neighbourhood is every valid single point substitution at
every site:

    |M1(g)| = L * (A - 1) = L * 25

For the recovered lineage (L between 50 and 61) that is **1250 to 1525 mutants
per genotype**. Exhaustive enumeration is trivially affordable; see L.

**Indels are NOT folded into M1.** The historical mutation operator's
insertion and deletion rates are UNSPECIFIED (see E), so whether indels were
important in 2003 is unknown. Avida's own analyzer treats them as separate
entry points (`ProcessInsert`, `ProcessDelete`) and this spec follows that
precedent: if indel rates are recovered, indel neighbourhoods are reported
**separately**, never silently merged.

## Outcome classes

Each mutant is executed in a faithful analysis environment, yielding viability
and a 9-bit phenotype `P(m)`. Classes are mutually exclusive and exhaustive
over viable mutants:

    LETHAL   cannot complete replication under the historical viability
             criterion (Avida's own test-CPU colony test)
    SILENT   P(m) == P(g).  Fitness, merit or gestation may still differ -
             this is a PHENOTYPIC classification, not a fitness one
    LOSS     P(m) is a strict subset of P(g)         (bits lost, none gained)
    GAIN     P(m) is a strict superset of P(g)       (bits gained, none lost)
    ALT      at least one bit gained AND at least one lost

Exhaustiveness argument over 9-bit masks: for viable m, either P(m) == P(g)
(SILENT) or they differ. If they differ, let `gained = P(m) & ~P(g)` and
`lost = P(g) & ~P(m)`; at least one is non-zero. The three cases (gained only,
lost only, both) are LOSS/GAIN/ALT. The partition is total.

**This must be property-tested exhaustively over the complete 512 x 512 mask
space before any historical genome is classified**, per directive section 21.
Do not trust the argument above; test it.

## Reported quantities

Per genotype: `f_lethal`, `f_silent`, `f_loss`, `f_gain`, `f_alt`, each over
the full L*25 denominator, plus raw counts.

## What P-MED adds over the historical detector

`cLandscape` already reports dead / neg / neut / pos fractions over the same
neighbourhood. P-MED does **not** add neighbourhood enumeration - Avida had it.
P-MED replaces the **fitness-valued** classification with a
**phenotype-partitioned** one. The honest statement of novelty is:

    the historical instrument asked "how good are my neighbours?"
    P-MED asks "what can my neighbours DO that I cannot?"

Those differ whenever fitness is not a monotone function of the phenotype
vector, which under a 2^v reward ladder with nine tasks it is not.
