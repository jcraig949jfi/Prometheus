# CYCLE 155-S — literature debt cleared, and the four categories are not four capabilities

Two results. The thrice-deferred literature debt is **paid and it confirms the claim rather than
narrowing it**. And the assumption my preregistered prediction rested on — four categories, four
capabilities — is **wrong in a way that matters for the north-star claim**.

## 1. Literature debt: CLEARED, and the measurement advantage survives

Fetched the full Stitch paper (POPL 2023, arXiv 2211.16605), 42 pages, 135,431 characters of
extracted text. Keyword census across the entire paper:

    downstream      0        compression   44
    accuracy        0        compressive   17
    success rate    0        dreamcoder    59
    synthesis time  0        memory        18
    solve           2        runtime       10

Their evaluation has four axes, quoted from the paper: library quality *"measured via a compression
metric"* against the DreamCoder baseline; resource efficiency *"by 2 and 3-4 orders of magnitude"* in
memory and runtime; scale, reporting *"a test set compression ratio of 2.55x-11.57x"*; and an
ablation.

**Compressivity is never validated against reachability or downstream solve rate. It is assumed as
the objective.** The words "downstream", "accuracy" and "success rate" do not occur once.

Worth noting what they *do* get right: they hold out a **test set** and measure compression on it, so
generalization is taken seriously — of compression. The methodological care is present; the objective
simply never closes the loop to task-solving.

So the position stated at 152-S survives its own verification: **Prometheus is ahead of this
literature on the measurement axis.** Apollo measures something Stitch does not measure at all. The
C-versus-R selector experiment is therefore not a re-run of published work — the R axis is genuinely
absent from the selector literature.

One honesty caveat: this is Stitch specifically, the *selector* paper. DreamCoder does report tasks
solved. The gap is in the abstraction-**selection** step, which is exactly where the selector
experiment sits.

## 2. The four categories are not four capabilities

Executed the ceiling pipeline over each category and recorded which slots get populated:

    transitivity        (SOLVED)    names 10 · relations 10 · ordered 10 · question_target 10
    temporal_ordering   (unsolved)  question_target 5 ONLY — relations EMPTY
    consistency_check   (unsolved)  NOTHING populated
    all_but_n           (unsolved)  NOTHING populated
    vacuous_truth       (unsolved)  NOTHING populated

**`temporal_ordering` is not a missing reasoning capability.** Its tasks — *"sunrise happened before
lunchtime, and dawn happened before sunrise… What happened first?"* — are structurally identical to
the solved `transitivity` category: a transitive chain plus an extreme selection. `op_build_ordering`
and `select_nth__g` already do exactly this, and they work on 10/10 transitivity tasks. The pipeline
fails because **`parse_names_and_relations` does not recognise "happened before"**, so `relations`
stays empty and the working ordering machinery never receives input.

That is an **input-parsing gap**, not an expressivity gap.

**`consistency_check`** uses "A is taller than B" — the same predicate transitivity parses — yet
populates nothing, which suggests the parser also fails on single-letter entities. It additionally
needs a contradiction predicate over the built ordering, which does not exist.

**`all_but_n`** ("There were 15 items. 1 were removed. How many remain?") populates nothing. I checked
whether `parse_numbers` was simply absent from O1's search space — **it is in the pool** (15
transformers, `parse_numbers` among them), so enumeration could and did reach it. The gap is that
**no operator in the entire 27-op registry computes an arithmetic difference.** Numbers can be
parsed; nothing subtracts. That is a genuine expressivity gap.

**`vacuous_truth`** ("Every element of the empty set is even. True?") is a genuine semantic gap.

### The corrected taxonomy

    all_but_n          GENUINE capability gap — no arithmetic-difference operator exists
    vacuous_truth      GENUINE capability gap — no vacuous-implication semantics
    temporal_ordering  PARSER gap — ordering machinery exists and works; predicate unrecognised
    consistency_check  PARSER gap + missing consistency predicate over an existing structure

**Two genuine capability gaps, two parser/predicate gaps that reuse machinery already present.**

## 3. Why this matters for the north-star claim, not just the arithmetic

The predicted ceiling movement per category is unchanged — each is 5/120 = 4.17%, and one category
covered still moves 0.8333 → 0.8750. **But the *kind* of demonstration differs completely.**

If Hephaestus mints a parser for "happened before" and the ceiling moves, **we have not demonstrated
acquiring a new reasoning operation.** We have demonstrated fixing an input gap in front of machinery
that already worked. That would be a real capability delta and a false organism demonstration.

**So the organism's first mint must target `all_but_n` or `vacuous_truth`** — the two genuine
capability gaps — and the specification should say so explicitly. Targeting `temporal_ordering`
because it looks cheapest would produce the most misleading possible success.

This is the sharpest thing this pass produced and it would not have been visible without executing
the per-category slot trace.

## 4. A caveat on "exhaustive" that should travel with the ceiling

O1's transformer pool is **15 ops**. The live registry holds **27**. Excluded from the pool are
`op_numeric_argmax`, `op_transitive_closure`, and five unguarded scorer variants whose guarded
counterparts are used instead.

The scorer exclusions are clearly correct. `op_transitive_closure` is flagged in
`composition_gauntlet.py` as a v1 op superseded by `op_build_ordering`, so its exclusion is
**plausibly deliberate** — I am not claiming a defect. But it does mean the 1,737,000-pipeline
enumeration is exhaustive **over a 15-op pool, not over the registry**, and "nothing in 1.74M
type-correct pipelines beats 0.833" should carry that qualifier.

## Self-identified weaknesses

- The parser diagnosis for `consistency_check` (single-letter entities) is inferred from nothing
  being populated, not from reading or instrumenting `parse_names_and_relations` directly. It is the
  weakest claim here.
- `synth` (30) and `cross_tier` (20) remain unexecuted by me; the exact 100/120 accounting still
  rests on Apollo's figures for 50 of 120 tasks. Budget went to the literature debt and the category
  analysis, both of which gated more.
- Five items per category remains thin and overfittable, unchanged from last pass.
- The Twitch paper was not read; Stitch answered the question and I stopped. Twitch may measure
  downstream proving success, which would matter for the "learning from failed proofs" divergence.

## Falsifier

Extending `parse_names_and_relations` to recognise "happened before" and finding that
`temporal_ordering` still fails — which would mean it is a capability gap after all; or finding an
arithmetic-difference operator somewhere in the registry I missed, which would void the `all_but_n`
target.

## Terminal

**CYCLE 155-S: TARGET REFINED.** Literature debt cleared and the measurement advantage confirmed by
direct reading. The four unsolved categories are two genuine capability gaps and two parser gaps, and
the organism's first mint must target a genuine one — `all_but_n` (no arithmetic difference exists)
or `vacuous_truth` — or the demonstration proves nothing about acquiring reasoning operations.
