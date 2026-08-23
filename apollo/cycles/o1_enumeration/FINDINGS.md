# O1 — type-directed enumeration vs evolution: findings

> **Apollo (M2), 2026-08-23.** Prereg: `PREREGISTRATION.md`, written before the enumerator
> ran. Stop rule ratified by James before the number existed. Deterministic, CPU only.

## Verdict, by the pre-committed rule

**`EVOLUTION_MORE_EFFICIENT`.** Enumeration reached the 0.833 ceiling, but needed far more
evaluations than evolution did. Under §4 of the preregistration this means **Apollo survives
O1 and proceeds to a bounded O2 test.** The kill condition — enumeration reaching the
ceiling in *fewer* than 3,144 evaluations — did not fire.

| | evaluations to reach 0.833 |
|---|---|
| evolution (pop 24 × gen 131) | **3,144** |
| type-directed enumeration | **1,687,896** |
| ratio | **537×** |

Total search: 1,737,000 type-correct pipelines in 3,000 s. Positive control passed —
the known organism scores 0.8333, its body is orderable within k=10, and its five-guard
tail is reachable.

## The result that matters more than the verdict

**Enumeration's ceiling is also exactly 0.833 — with an identical per-subset profile.**

| | canary | synth | inference | cross_tier | overall |
|---|---|---|---|---|---|
| evolution's best organism | 0.6 | 1.0 | 1.0 | 1.0 | **0.833** |
| enumeration's best, 1.74M pipelines | 0.6 | 1.0 | 1.0 | 1.0 | **0.833** |

Nothing in 1.74 million type-correct pipelines beats the organism evolution found. Not one.

**So 0.833 is the substrate's ceiling, not evolution's.** The remaining 16.7% is not
reachable by *any* pipeline in this representation — it is an expressivity limit, now
measured by construction rather than inferred from a plateau. This is exactly the
outside-view objection the 2026-08-23 review raised (§9.5): *"You hit a ceiling at 0.833
not because the search failed, but because the genome lacks the expressivity to model the
remaining 16.7% of the battery."* Confirmed.

Two consequences follow immediately:

- **No search improvement can pass 0.833.** Better operators, better descriptors, better
  crossover — none of it matters for the headline while the genome is a flat operator list.
  Any plan whose deliverable is "a better search" is capped before it starts.
- **The 0.558 → 0.708 → 0.833 climb was never search finding capability.** Each step was a
  human raising the expressivity ceiling, after which *any* adequate search would have found
  the new optimum. Enumeration would have found each one too.

## The honest counterweight to "evolution wins"

The 537× favours evolution and should not be quoted without three caveats.

1. **Enumeration here is the dumbest possible baseline** — breadth-first by subset size,
   uniform 48-ordering sample per subset, no pruning, no best-first, no reuse of partial
   results. A search that ordered candidates by anything at all would close much of the gap.
   537× is the ceiling of evolution's advantage over *unguided* search, not a measurement of
   its advantage over *competent* search.
2. **Wall-clock tells the opposite story.** Brute force found the same organism in **50
   minutes of laptop CPU** with no MAP-Elites, no crossover, no archive, no dispatch wiring
   — and none of the four months of engineering that produced them. The evaluation-count
   metric flatters evolution; the engineering-cost comparison does not.
3. **RC7 is untouched.** Apollo rearranges human-authored operators; it does not mint them.
   Enumeration losing on sample-efficiency says nothing about that, and RC7 was the deepest
   objection in the review.

Evolution earned a narrow, real result: it is markedly more sample-efficient than blind
enumeration on this substrate. It did not earn the claim that it discovers anything
enumeration cannot.

## Two invalid runs, archived rather than deleted

Both would have produced a **false win for evolution**, and I found them only by continuing
to attack a result that was going my way. The under-exploration failure mode was named in
the preregistration, which is the only reason I looked.

**`RESULT_INVALID_tails_capped_at_3.json`** — guard-set tails capped at 3 while the known
organism carries a **five-guard tail**. The winning shape was not in the enumerated space
at all. Reported "enumeration cannot reach the ceiling."

**`RESULT_INVALID_orders_capped_at_4.json`** — only 4 topological orderings sampled per
subset. Order is semantically load-bearing: `relations_from_facts` **overwrites**
`relations`, so it must follow `parse_names_and_relations` or the bridge's output is
destroyed. Also reported "cannot reach the ceiling."

Measured directly, which is what settled it:

> The known 10-operator subset has **166,320 valid topological orderings. 45,360 — 27.3% —
> reach 0.833.** The first success is at DFS index 27. A cap of 4 could not see it.

The positive control now tests the **full** pipeline: body orderable within `max_k` **and**
tail reachable. A run whose control fails reports nothing about evolution.

**Standing lesson:** an experiment that returns the answer its author's project needs
deserves a second audit, not a write-up. Both errors here were silent, both favoured the
incumbent, and neither would have been caught by re-reading the code.

## Limits of this result

Not fully exhaustive: k ≤ 10 transformers, 48 orderings per subset (some subsets have
166,320), guard-set tails over the 5 guarded scorers plus single scorers. Multi-tails of
*plain* scorers were not enumerated. So "0.833 is the ceiling" is precisely: **no better
pipeline was found in 1.74M samples of the type-correct space under those bounds.** Given
that enumeration and evolution converged on the same number and the same per-subset profile
from completely different directions, I consider the ceiling claim well-supported but not
proven.

## What happens next, per the rule

Apollo proceeds to a **bounded O2 test** — re-key the MAP-Elites archive on a behavioural
descriptor (the solved-task signature) instead of pipeline syntax, and ask one narrow
question, pre-committed by the review: *does meaningful behavioural coverage per 10,000
evaluations materially increase?* Not cell count, not archive size.

Given the ceiling result, O2 is now explicitly **not** a route to a higher score — 0.833 is
fixed by the representation. It is a test of whether the archive can be made to index
capability rather than syntax, which is a prerequisite for anything later.
