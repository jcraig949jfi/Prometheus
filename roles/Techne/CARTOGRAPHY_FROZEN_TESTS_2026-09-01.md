# Techne -- cartography campaign, the two frozen tests, run

## Date: 2026-09-01 (campaign cycle 038, M2)
## Artifacts
- Harness: `D:\Prometheus\techne\cartography\frozen_tests.py` (committed BEFORE it was run)
- Results: `D:\Prometheus\techne\cartography\frozen_test_results_20260901.json`
- Verdict writer: `D:\Prometheus\techne\cartography\record_frozen_test_verdicts.py`
- Cycle record: `D:\Prometheus\techne\cartography\cycles\cycle_038.json`
- Log: `D:\Prometheus\techne\cartography\store\taxonomy_events.jsonl` (5 new events)

---

## 0. Why this cycle exists

At cycle 032 the campaign recorded TRAJ-001 against itself: placed-paper growth had stopped
(6, 3, 1, 0 across cycle bands) while raw corpus growth continued, and the recommendation was
to stop spending cycles on acquisition and start spending them on the frozen tests TX-001 and
TX-003 already owed. Cycles 033-037 kept acquiring. This cycle is that redirection.

Corpus is unchanged at 304 genomes. Zero papers retrieved, by design.

---

## 1. TX-001 (partial cells) -- PASS, both clauses

The cycle-021 condition: the pairwise archive must place a strictly larger fraction of
held-out papers AND not degrade the cross-field neighbour quality of those it already placed.

```
                    frozen 25% holdout (3 seeds)        leave-one-out (all 218)
  placement
    four-tuple      1/54, 3/54, 3/54  (1.9-5.6%)        13/218   ( 6.0%)
    pairwise       28/54, 30/54, 26/54 (48-52%)        125/218   (57.3%)

  non-degradation, PAIRED on the papers the 4-tuple places
    comparable          1, 3, 3                              13
    degraded            0, 0, 0                               0
    improved            0, 1, 0                               1
```

Clause 1 is satisfied by roughly a factor of ten. Clause 2 is satisfied on the evidence
available, and the evidence available is thin: 0 of 13 degraded is consistent with a true
degradation rate up to about 25%, because 13 is how few papers the 4-tuple archive places at
all. That is not a hedge I am adding after the fact -- it is the arithmetic of the comparison
the frozen text asked for.

**My first implementation got clause 2 wrong** and I caught it before reporting. It compared
two marginal cross-field rates over two different paper sets, which is an easier and different
question than "does it degrade *those it already placed*". The paired reading is the one in
the frozen text; both are now in the artifact, and only the paired one is adjudicated.

### The chance floor and the ceiling (neither was in the frozen text)

A cross-field rate means nothing without a null. Under shuffled neighbours (200 resamples):

```
  pairwise, leave-one-out, n = 125 placed
    chance floor  ~ 91 papers
    observed        104 papers
    ceiling         108 papers   <- the most that can ever hit, see LIM-010
```

So the honest statement is not "0.83 vs a floor of 0.73". It is: **the archive captures about
76% of the headroom that exists above chance**, in a band 17 papers wide. Real signal, narrow
instrument.

### Not applied

A pass licenses replacing the 4-tuple archive with marginal + pairwise archives and computing
holes per axis-pair. That is a separate reviewable act with its own commit and it is not done
here. It is also constrained: passing this test unblocks the archive geometry, it does **not**
license reporting any hole as a research gap, for the reason in section 3.

---

## 2. TX-003 (MI coordinates) -- NOT ADJUDICABLE. The test cannot be passed.

The cycle-028 condition: a majority of the 23 held-out MI papers must have at least one
cross-field neighbour sharing a mechanism tag absent from the MI paper's own title.

```
  pass threshold needed        12 of 23
  satisfiability ceiling        7 of 23   <- the most that can EVER pass
  chance floor (p95)            6 of 23   <- random neighbours already reach this
  observed, current axes        2 of 23
  observed, mutated axes        2 of 23
```

The whole dynamic range of this metric is **one paper wide**, and the pass threshold sits five
papers above the ceiling. No archive, no axis set, no mutation can pass it.

Where the ceiling comes from: the criterion needs a shared tag *absent from the held-out
paper's title*, but the tagger is lexical and assigns a tag by finding its surface form in the
text. 11 of the 23 MI papers carry no tag that is not already printed in their own title, so
they can never register a hit. Of the remaining 12, five carry only `causal_attribution`,
`circuit_representation` or `sparse_autoencoder` as eligible tags -- and each of those appears
on **zero** non-MI papers, so they have no possible cross-field partner. 23 - 11 - 5 = 7.

**This is the LIM-003 error class, recurring.** At cycle 033 the campaign discovered it had
produced a false PERSISTENT_COVERAGE_HOLE because a fix had made kills structurally
impossible, and impossible kills read as confirmed absences. Reporting the observed 2/23 as
"mechanistic interpretability does not retrieve cross-field" would have been the same mistake
in a new place.

### What the mutation actually did

```
                        placed on 4-tuple    cross-field hits
  current axes                 0                    2
  mutated axes (TX-003)        4                    2
```

Adding `causal_intervention` and `faithfulness_to_reference` moved MI **placement** from 0 to
4 and moved MI **retrieval** by exactly zero. Placement and retrieval are decoupled. TX-003
argued for a retrieval failure and proposed a placement fix.

### Diagnostic (not part of the frozen test, makes no pass claim)

Re-running the same predicate under TX-001's pairwise geometry separates "MI is inexpressible"
from "the archive is empty so nothing retrieves":

```
                            MI placed   non-MI retrieval pool   cross-field hits
  current, 4-tuple              0                15                    2
  current, pairwise            16               156                    3
  mutated, pairwise            23               157                    3
```

A tenfold larger retrieval pool moved hits from 2 to 3, still below the chance floor. Archive
emptiness is not the binding constraint either. The binding constraint is the metric.

### What is owed

A replacement test for TX-003 whose satisfiability ceiling is computed and published *before*
it is frozen. Any replacement must not certify cross-field identity through a lexical tagger:
a lexical tag shared across two fields is a shared *word*, which is precisely what the
criterion was written to exclude. TX-003's status is unchanged -- PROPOSED_NOT_APPLIED.

---

## 3. Three limitations filed

**LIM-010 -- the cross-field metric has no dynamic range. HIGH.** `cross_field_retrieval` is
one of the four listed TAXONOMY_MUTATION_TESTS and the brief calls it the Rosetta Stone
question. Its capacity is the abstract-minus-title vocabulary residue of the tagger: 51% of
the corpus overall, and much less on any short-titled population. Consequence, binding on all
future cycles: **every frozen test that uses cross_field_retrieval must publish its
satisfiability ceiling next to its pass threshold before being frozen. A test whose ceiling is
below its threshold is not a test.** This is why a TX-001 pass does not license reporting
holes as research gaps -- the metric that certifies neighbour quality is 17 papers wide.

**LIM-009 -- the abstract flag is stale for every genome before cycle 019.** `abstract_available`
is None for all 135 genomes from cycles 0-018; 123 of them carry an abstract evidence span.
Nothing published is affected: every live consumer gates on the abstract text, verified as 0
claims on the 86 title-only genomes and 218 of 218 on the abstract-bearing ones. The comment
in `cycle.py` claiming the flag "stops every claim predicate" describes an intent, not the
implementation. But the frozen tests would have run on 95 genomes instead of 218, and those 95
are entirely post-cycle-020 -- a recency-biased sample of exactly the region where the
instrument is known to degrade. The harness derives the property from evidence spans instead.

**LIM-004 escalated -- polysemy contaminates a POPULATION, not just query results.** The 23
papers tagging as mechanistic interpretability include a survey of IoT security,
transmission-line fault classification, bearing fault diagnosis, aptamer-protein interaction
prediction, quantum circuit optimisation for NISQ architectures, TrakEM2 neural-circuit
reconstruction software, and microbial electron transfer. Roughly 12 of 23 are not MI papers;
`sparse_autoencoder` and `circuit_representation` are polysemous across speech processing,
power engineering, quantum computing and neuroscience.

This matters more than a bad lane. TX-003 was proposed at cycle 028 from the observation that
"19 MI papers are tagged better than EC papers and placed worse". That population was
contaminated the same way. A taxonomy mutation was proposed on the basis of a population the
instrument mis-assembled -- one level deeper than a lane returning bad results.

The 12-of-23 count is a read of titles by an LLM and is **PROPOSED, not adjudicated**. Under
the campaign's own adjudication rule that is exactly what may not write CONFIRMED. No paper
has been reclassified.

---

## 4. What I did not do

- Did not apply TX-001. A pass licenses application; performing it is a separate act.
- Did not apply TX-003, whose status is unchanged.
- Did not hand-audit or reclassify the MI population.
- Did not backfill the 135 stale `abstract_available` records -- rewriting stored records to
  repair a field with no live consumer is larger than the defect.
- Did not run an acquisition cycle. Corpus unchanged at 304.

## 5. Next, in order

1. **Replacement test for TX-003**, ceiling published before freeze. Until one exists the
   campaign has no evidence either way on whether the five chartered fields share mechanism
   structure -- which is its headline question.
2. **Apply TX-001** (marginal + pairwise archives, holes per axis-pair) as its own commit,
   with LIM-010 attached so no hole ships as a research gap on this metric alone.
3. **Hand-audit the MI population** against LIM-004 before any further MI reasoning.

*-- Techne, M2, 2026-09-01.*
