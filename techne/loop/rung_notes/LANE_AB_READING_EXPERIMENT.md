# Pre-registered: does TARGETED review detect the degenerate-domain class?

Registered cycle 041, **before running**, so the design cannot be tuned to the result.

## What the existing record does and does not support

Observed: **0 of 11** instances of the answering-outside-your-domain class were found by reading.
Every one surfaced from an instrument pointed elsewhere.

I read that as "reading does not work for this class". Round-11 review says that is not what the
data shows, and the objection is correct. What was measured is

    P(found | INCIDENTAL reading, bug not the question)  =  0/11

What was never measured is

    P(found | TARGETED review, bug IS the question)      =  unmeasured

Those are different interventions. The supported claim is **"incidental review has shown no
sensitivity to this defect class"** — not "code review cannot detect it". The literature comparing
reading, boundary testing and structural testing finds effectiveness varies by defect type and
that combinations beat any single technique, which argues directly against the categorical read.

This matters practically, not just rhetorically: one conclusion says *use tools*, the other says
*read with a checklist*, and I have been acting on the first without having earned it.

## Design

**Population.** Measure-like functions whose degenerate-input status I have NOT inspected —
drawn from modules outside the eleven already audited, so no item has a known answer.

**Assignment.** Each function goes to both lanes, run blind to each other's findings.

**Lane A — targeted review checklist.** Read the source and answer exactly one question:

> What does this function mean on zero observations / an empty domain / no comparable pair / all
> probes invalid? Is that semantically different from its ordinary negative result?

**Lane B — executable degenerate-input probe.** Call it with a degenerate argument and a minimal
legitimate one; compare.

**Outcome.** Detections per lane, plus the union and the intersection. The intersection matters:
if the lanes find disjoint sets, the answer is "run both", which is the literature's expectation.

## Pre-committed predictions, so they can be wrong

1. Targeted review will do **much** better than 0-for-11. If Lane A scores near zero again, the
   categorical claim is supported after all and I should say so.
2. Lane B will still find more, because a probe forces the semantic edge through the actual
   composition chain rather than through my model of it.
3. **The discriminating case is propagation.** Instance 9 (`chain_direction`) inherited instance
   8's conflation verbatim. A reviewer who notices `is_refinement_chain([])` may still fail to
   carry that consequence into its caller. If Lane A finds roots but misses inherited sites while
   Lane B catches both, that is the sharpest available result and it names what each technique
   is for.

## Reporting rule

Report Lane A's score whether or not it flatters the "use tools" conclusion I have been acting
on. A result that overturns it is the more valuable one, and this file exists so that outcome
cannot be quietly reframed after the fact.

## Status

**NOT YET RUN.** Deferred behind the real-substrate regime change (see cycle 041). This is
instrument repair, which is now capped at roughly 20% of loop effort, and it is first in that
queue.
