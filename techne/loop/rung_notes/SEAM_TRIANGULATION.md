# Seam triangulation: a third implementation localizes responsibility

Doctrine extracted from cycle 042 and its correction. Reusable, and it earned its place by
changing a remediation claim rather than by sounding right.

## The rule

> **A two-party mismatch identifies a seam. A third independent conforming implementation
> localizes responsibility for it.**

When a producer and a consumer disagree, "schema mismatch" is symmetric: nothing in the pair says
which side should change. Arguing it from the code reads as a preference. So before deciding:

**search for another producer or consumer of the same interface, and measure it.**

If the third party conforms to the consumer, the deviating producer is the outlier and the fix is
on the producer side. If the third party deviates the same way, the consumer is the outlier. If
there is no third party, say so and leave ownership open.

## The instance that produced it

`load_prepass` (one consumer) against three producers:

    probe_prepass.jsonl              flat `rep`        loads correctly (50% = rep-2 filter)
    nearmiss_mix-M30_prepass.jsonl   flat `rep`        loads correctly (50% = rep-2 filter)
    p1_prepass.jsonl                 `key: [rep, uid]` 100% DROP

Two producers plus the consumer agree on flat `rep`; one producer differs. The simplest
explanation is that the campaign writer violates the producer contract, not that the loader lacks
compatibility.

**With only `p1_prepass.jsonl` and the loader, that conclusion was unavailable** — which is
exactly what cycle 042 published before the correction: the seam was named, the responsible side
was not.

## The limit, and it is a real one

**"The campaign writer is wrong" is a claim about a DE FACTO contract, not a canonical one.**

A repo-wide search found **no field-level schema specification for these ledgers anywhere in the
repository**. What exists:

- `load_prepass`'s docstring cites "prereg §4.2, review C1" — but that governs the **rep-1-only
  policy**, not the wire format, and the cited document is not in the repo.
- The `ResidueRecord` dataclass defines the **in-memory** shape, not the on-disk one.

So flat `rep` is the **observed contract**: what two of three producers and the sole consumer
actually do. That is strong triangulation and it is not authority. Absent a written schema,
"canonical" is not a thing anyone can claim here, and the honest form of the finding is:

> Three implementations, two conforming; the deviating one is the cheapest to change and the one
> that would align with existing practice. No document adjudicates it.

**And the absence is itself the finding underneath the defect.** Three producers write to one
consumer across three roles with no field-level contract written down anywhere. That is the
precondition for this class, not an incidental gap — a seam whose fields are unspecified will
drift, and the only question is which producer drifts first.

## Application rule

Before naming which side of a seam to repair:

1. Enumerate implementations of the interface **repo-wide**, never by chosen directories.
2. Measure at least one **known-good** pair as a control.
3. If a third conforming implementation exists, name the outlier and say **de facto**.
4. If no third exists, report the seam and leave ownership explicitly open.
5. Check whether a written schema exists. If not, report its absence as part of the finding.
