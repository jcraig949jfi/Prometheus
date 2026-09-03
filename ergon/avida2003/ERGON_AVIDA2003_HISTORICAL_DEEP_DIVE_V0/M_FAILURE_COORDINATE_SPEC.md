# M - FAILURE COORDINATE SPEC

The Historical Collider cares about failures. This spec derives failure
coordinates that Avida's physics actually supports, and refuses to invent
semantics it does not.

## Supported coordinates

| Coordinate | Support | Source |
|---|---|---|
| cannot replicate (lethal) | YES | Avida colony test; `cLandscape` dead_count |
| fitness decrease | YES | `GetFitness` on the mutant vs parent |
| gestation increase | YES | `GetGestationTime` |
| task loss | YES | 9-bit phenotype comparison (LOSS / ALT in H) |
| failed task gain | YES, as the complement of GAIN over viable mutants |
| phenotype unchanged (silent) | YES | SILENT in H |
| phenotype lateral move | YES | ALT in H - gain and loss simultaneously |
| offspring non-viability | PARTIAL | Avida distinguishes an organism that cannot divide from one that produces a non-viable child; the recovered accessors do not expose this split directly and it needs source work before use |

## NOT supported - do not invent

Avida has no notion of "almost solved a task": the 32-bit credit rule is a hard
threshold (see C). There is therefore **no partial-credit failure coordinate**,
and any near-miss metric would be a modern imposition on the specimen rather
than a recovered observable. Prometheus's own D-5 work used bitwise-Hamming
partial credit to restore a gradient; **that move is not available here** and
attempting it would change the specimen.

## The narrow tectonic test

Do not call every neighbourhood difference a failure-landscape bump. The narrow
question is:

    does the geometry of UNSUCCESSFUL neighbouring mutations change before a
    later acquisition transition?

and it must be run against cheap conventional predictors - fitness, genome
length, task count, gestation, total viability fraction. If those predict
future EQU equally well, failure geometry adds nothing and that is the result.

This is K4, and it is the kill criterion most likely to fire, because task
count in particular is a strong and nearly free predictor: a genotype holding
six of nine functions is manifestly closer to EQU than one holding zero. Any
accessibility signal must beat that trivial baseline before it means anything.
