# Addendum to PREREG_V0_3 — three implementation corrections, each disclosed with its trigger

Filed 2026-09-03, during execution. Nothing here changes a tolerance, a coordinate, or the
verdict vocabulary. Each item states what was wrong, when it was found, and what it could have
done to the answer.

## A. NC4's configuration matching (found before any V0.3 coordinate was examined)

NC4 was implemented drawing fresh uniform genomes at the V0.3 length distribution but with the
**cohort template** configuration. Organisms whose `tape_words` had drifted could not be
represented and the run aborted with `ManifestError: genome longer than tape`. Corrected so NC4
mirrors each V0.3 organism's **length and full configuration** with fresh uniform content. This
makes NC4 a strictly closer geometry match. The correction was made from a crash, before any
coordinate was read.

## B. NC1's configuration half (defined before the run, implemented after the V0.3 arm)

PREREG section 3 defines NC1 as "the same construction applied to each numeric configuration
coordinate". The first implementation covered genome length only. The configuration half (`NC1B`)
was implemented after the V0.3 arm had run but **before any configuration coordinate was
examined**. It is a symmetric bounded walk over the six configuration fields, blocked only by the
published bounds and by manifest validity. It deliberately omits the grammar's stricter rule that
a tape halving is a no-op unless the genome would occupy at most half the new tape, because that
rule is a property of the grammar and must remain visible as a mutation prior rather than being
absorbed into the geometry control.

## C. Two defects in my own adjudicator (found at adjudication, both reported)

1. **The Holm correction was inert.** It compared a z-equivalent against a *ratio* of normal
   quantiles rather than against the quantile, and had no step-down stop, so the "corrected" set
   was identical to the uncorrected set and was in fact a weaker test than excluding zero. With
   the bug, twenty coordinates appeared to survive correction. Fixed to a proper step-down Holm
   on the z-equivalent; **one** coordinate survives. The first, wrong number is recorded here
   because it is the number I would have published.

2. **The preregistered null for content coordinates is confounded by length.** PREREG section 3
   matches opcode, class and operand coordinates to NC2/NC3, both of which **freeze genome
   length**. In cohorts whose length changes materially (1, 8, 256) that is a comparison against
   a different population, which is the wrong-population error this program has paid for before.
   Rather than silently re-matching, the adjudicator now computes **both**: the preregistered
   NC3 comparison and the length-matched NC4 comparison, reports both, and declares an effect
   only when it survives against the length-matched null. That is strictly more conservative than
   the preregistration. Under the preregistered NC3 matching alone, six content coordinates would
   have been declared at cohort 1; under the length-matched null, none is.

Both defects moved the answer toward *fewer* declared effects. That direction is stated
explicitly because the direction of a correction relative to the hypothesis is exactly what this
program requires be disclosed.
