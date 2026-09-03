# Generalization Level Analysis

The directive's ladder, applied to what S1 and S3 actually demonstrate.

    G0  recalling previously selected states
    G1  completing corrupted / partial versions of previous states
    G2  new combinations of previously selected substructures
    G3  novel states within the learned structural distribution
    G4  novel functional dimensions not represented in historical selection

## What S1 demonstrates — RECOVERED

The decisive passage:

> "development generalises from target phenotypes that have 1 or 3 loops to produce phenotypes
> with 0, 1, 2, 3 or 4 loops. This shows that by producing new combinations of modules,
> developmental memory can generalise in both an interpolative and extrapolative manner from
> phenotypes that have been selected in the past."

and:

> "the evolved developmental process is not just reproducing previously selected phenotypic
> patterns, but internalising structural information about the set of target patterns — thus
> producing phenotypes that have not been previously seen but are in the same family of
> phenotypes"

### Grading — DERIVED

| level | achieved? | reasoning |
|---|---|---|
| G0 recall | **YES** | stated directly |
| G1 completion | **YES** | S1 reports production of a phenotype resembling a previously selected one from partial input |
| G2 new combinations | **YES, explicitly** | "by producing new combinations of modules" |
| G3 novel within-distribution | **YES** | "phenotypes that have not been previously seen but are in the same family" — S1's own phrasing bounds it to the family |
| G4 novel dimensions | **NO** | nothing recovered supports it, and S1 does not claim it |

**Strongest demonstrated level: G3, self-limited by the source to "the same family".**

## The extrapolation claim needs care — DERIVED

S1 uses the word "extrapolative": trained on 1 and 3 loops, it produces 0 and 4. That is
extrapolation **along a dimension that was already the trained dimension**. Loop-count was the
axis of variation in the training set; the system produced unseen *values* on a *seen* axis.

That is G3, not G4. G4 would require a phenotypic dimension absent from every selected target.
Calling loop-count extrapolation "open-ended innovation" would be exactly the over-reading the
directive warns against, and I flag it because the word "extrapolative" in the source invites it.

## The honesty of the source — worth recording

RECOVERED: S1 states that this generalisation "is (necessarily) equivalent to a 'failure' to
restrict phenotypes to a set of training patterns accurately."

That is the authors describing their own positive result as an inability to memorise exactly.
It is the same object seen from both sides, and it is the cleanest statement in the lineage of
why memory and lock-in are not separable — see `MEMORY_VS_LOCKIN.md`.

## What S3 adds — RECOVERED

Kouvaris moves the test to **previously-unseen environments** and defines evolvability as
generalisation to them. That is a stronger evaluation protocol than S1's within-family
demonstration, and it is the reason S3 is the more important paper for Prometheus. It still
does not demonstrate G4: an unseen environment drawn from the same structural regularity is
G3 evaluated properly, not a new functional dimension.

## Verdict

    STRONGEST DEMONSTRATED: G3 (novel states within the learned structural distribution)
    G4 NOT DEMONSTRATED anywhere in the recovered sources.

Any Prometheus claim that this lineage produces open-ended novelty is unsupported by S1–S3.
