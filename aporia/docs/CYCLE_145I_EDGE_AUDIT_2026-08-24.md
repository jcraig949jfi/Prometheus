# CYCLE 145-I — TERMINAL: REDESIGN. The corpus does contain edges. I audited the wrong generator.

**Question:** does `theseus/corpus` preserve (state, OPERATION, outcome) triples in which the
operation varies between siblings — genuine edges — or only repeated measurements of one operation?

This pass exists because the operator raised a prior question that subsumes the 140→144 line: the
substrate may have been recording *failed objects* when the information-bearing unit is the
*transition between objects*. If the corpus stores vertices and not edges, no amount of failure
accumulation can yield directional information, and that would be a property of the schema rather
than of the mathematics.

## What the audit measured, and that part is solid

Generator `d3` (~27% of sampled rows, and the largest single generator) branches 5 ways per parent
and records an R² per child. It looked like an edge corpus: 401,399 sibling sets, **99.91% with real
R² spread across children**, 16.5% with mixed child verdicts. All four controls passed, including a
shuffled-label negative control that scored at chance.

Then the operation comparison:

    sibling sets that are RESAMPLES of one operation : 401,399 (100.00%)
    sibling sets varying in an OPERATIONAL key      :       0 ( 0.00%)
    varying step_input keys, across all 401,399 sets: ['child_seed']

Every d3 branch has identical `ec_invariant`, `knot_invariant`, `polynomial_degree` and method.
`step_kind` reads `"resample"`. **The R² spread is sampling noise of a single operation, not a
gradient over operator space.** d3's branching factor is a variance estimate, not a search.

That is a real and useful finding on its own: it is exactly what "vertices with error bars" looks
like, and it would read as directional signal to anyone who measured only outcome variance.

## But my preregistered scope was falsified by my own run

The preregistration stated: *"Generator d3 is the ONLY generator that populates parent_record_id and
step_trace."* The run's own coverage table contradicts it:

    d3   402,455 rows | 100.0% carry a parent pointer
    h4    75,664 rows | 100.0% carry a parent pointer
    d2    27,549 rows | 100.0% carry a parent pointer

`h4` and `d2` were dropped by the audit's parse rule because they carry no `step_trace` — the very
field the audit keyed on. So the branch condition `A == 0` fired correctly *for d3*, while the
reading it licences — "the corpus records vertices with error bars" — is wrong for the corpus.

## And those two generators are exactly what the question was looking for

**`h4` (`bridge_extension`) is a genuine edge corpus.** The parent state is a relation that held for
one invariant; each child *extends it to a different invariant* and records whether it survives:

    extension attempts : 226,992    holds=True 124,197 | holds=False 102,795   (55/45)
    n_holding/n_tested : 3/3 20,230 | 2/3 21,461 | 1/3 20,585 | 0/3 13,388
    operations varied  : conductor, tamagawa_product, torsion, rank
    distinct parents   : 28,187

The **operation varies**, the **outcome varies**, and `n_holding/n_tested` is graded across the full
0–3 range rather than piling at an extreme. That is (state, operation, outcome) — roughly 227,000
labelled edges, already on disk.

**`d2` (`kill_neighborhood`) is a boundary-distance corpus.** Its records carry `band`, `margin`,
`threshold_k`, `in_bracket`:

    comfortable_failure 16,453 | barely_fails 4,913 | barely_survives 4,718 | comfortable_survival 1,465

An **ordered four-level distance-to-boundary coordinate with every level populated**, plus a
continuous signed margin. This is the closest thing in the corpus to a measured boundary of damage —
which is the object the operator's question was about.

## Verdict

**REDESIGN**, not NO_EDGES. The preregistered branch fired correctly on the population it examined;
the population was the wrong one, and the run said so in its own output. Reporting NO_EDGES on that
basis would have been a false negative on the most consequential question this loop has been asked
in fifty passes.

Same discipline as withdrawing 143-G pass 1: a branch condition is not the finding when a scope
assumption underneath it has failed.

## What this changes

The retrospective navigation test does **not** need purpose-built neighbourhoods to get started. It
can run on `h4` now:

> Given a parent relation and the set of invariants it could be extended to, does the recorded
> representation rank the extensions that HOLD above those that FAIL — better than chance, and
> better than a deliberately embarrassing baseline?

Chance is well defined (4 invariants, ~55% base rate), the labels already exist, and the generator
produced them without knowing this question would be asked, so there is no authored-for-the-test
contamination. `d2`'s bands give an independent ordered target for the same representation.

## Self-identified weaknesses

- 6 batches of 165, 300k rows each — 1.5M of ~132M rows. Generator proportions could differ in the
  unsampled 96%, and the h4/d2 counts are sample counts, not census counts.
- The audit keyed on `step_trace` and therefore silently excluded exactly the generators that turned
  out to matter. A parse rule that drops records should have been a *loud* control, not a quiet
  `continue`. This is the second time on this line that a silent exclusion hid the answer.
- `h4`'s "operation" is a choice of which invariant to extend to, which is a narrow and possibly
  degenerate notion of operator. It may be closer to feature selection than to a mathematical verb,
  and that distinction should be settled before any ranking result is interpreted.
- No ranking was run this pass, so nothing is yet known about whether the representation has
  directional skill — only that the question is now askable.
- The d3 resample finding is solid but says nothing about whether d3 *could* have varied operations;
  the generator may have been built as a variance estimator on purpose.

## Falsifier

An operationally-varying sibling set in d3 anywhere in the unsampled batches; evidence that h4's
`extensions` are generated by a rule making `holds` predictable from the invariant identity alone
(which would make the ranking test trivial rather than informative); or a census over all 165
batches showing h4 and d2 to be negligible fractions of the corpus.

## Terminal

**CYCLE 145-I: REDESIGN.** The corpus is not a graveyard of vertices. It holds roughly 227,000
labelled edges in `h4` and an ordered boundary-distance coordinate in `d2` — and the audit that
concluded otherwise was scoped to the one generator that happens to be a variance estimator.
