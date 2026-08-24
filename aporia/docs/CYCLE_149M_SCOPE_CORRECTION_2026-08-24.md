# CYCLE 149-M — the programme is NOT closed. I audited the wrong generators, in the wrong window.

**Decision: do not close. Open CYCLE 150-N on `c4`/`c5`.** This pass was sent to decide whether the
retrospective navigation programme on this corpus is finished. The answer is no, and the reason is a
scope failure in my own three preceding passes.

## Two errors, both mine, both found by one stratified scan

**Error 1 — I sampled the earliest batches, every time.** Passes 145-I through 148-L read
`files[:6]` and `files[:12]`: the chronologically first batches. That is precisely the
shard-window antipattern this loop has doctrine against, and I committed it four passes running.

A stratified scan (every 11th batch across all 165) shows what the window hid:

    h4 relations, earliest stratified batches :   0 distinct
    h4 relations, later batches               : 137 distinct

`abs_diff_le_N` is not one relation. It is a **parameterized family spanning N = 1 to 159.** My
148-L transfer test ran leave-one-out over *four* relations because four is all the early window
contained. With ~140 relations carrying a natural ordinal parameter, the transfer question becomes
"does the model transfer *along the threshold*" — a completely different and far more tractable test
than the categorical one I ran.

**Error 2 — I audited 3 of 8 edge-bearing generators, and picked the two least suitable.**

    d3  217,021 rows  100% parent  kill_neighborhood   <- audited: a variance estimator
    c4  143,227 rows  100% parent  MUTATION            <- never examined
    h2  131,186 rows  100% parent  kill_neighborhood   <- never examined
    h1   84,229 rows  100% parent  kill_neighborhood   <- never examined
    h4   72,038 rows  100% parent  bridge_extension    <- audited: measurement selection
    d2   41,492 rows  100% parent  kill_neighborhood   <- noted, never used
    c5   37,383 rows  100% parent  MUTATION            <- never examined
    d1    5,337 rows  100% parent  kill_neighborhood   <- never examined

145-I concluded "d3 is the only generator with parent pointers," was corrected to three, and the
true count is **eight**. Third consecutive scope claim of mine to fail.

## What the unexamined generators actually contain

This is the part that reopens the programme. I said the corpus could not express an action space of
*transformations* rather than *measurements*. That was wrong.

**`c4` — generalization.** `C4_GEN[abs_diff_le_3 ⇒ abs_diff_le_5]`. The action is *loosen the
relation*, recorded as `original_relation` → `relation`, with outcomes `holds`, `weak_holds`,
`self_consistent`. That is a transformation of the state, not a choice of what to measure.

**`c5` — specialization.** `C5_SPEC[divides ⇏ equal]`. The action is *tighten the relation*, with
outcomes `holds`, `strong_holds`, and — notably — **`boundary_revealed`**, an explicit
boundary-detection flag.

**`h1` — counterexample hunting.** Parent is a surviving relation; the action is `hunter_varied_side`
(`vary_a`) under a `hunt_budget`, with outcome `hunter_success`. The action is *which side to
perturb*, and the outcome is whether the perturbation killed the relation.

So the corpus contains, unexamined: **~180K transformation edges (c4+c5) where the action is
generalize/specialize along an ordinal parameter, and ~215K perturbation edges (h1+h2) where the
action is which side to vary and the outcome is whether the relation survived.**

Both are far closer to a navigation question than h4's four-way measurement choice.

## What this does and does not retract

**Not retracted:** 148-L's finding that rankings anti-transfer across four *categorically distinct*
relations, and 147-K's retraction. Those measurements stand on the data they used.

**Re-scoped:** 148-L's conclusion cannot be read as "the corpus carries no transferable navigational
knowledge." It shows that four categorically-different relations from the early window do not
transfer to one another. It says nothing about transfer along the `abs_diff_le_N` threshold, and
nothing at all about c4/c5/h1/h2.

**Withdrawn:** my statement last pass that "the corpus structurally cannot express relation as a
first-class axis." In `c4` and `c5` the relation *is* the thing being transformed — it is the action,
not held-constant context.

## Decision

**OPEN CYCLE 150-N** on the `c4`/`c5` mutation generators. Build-versus-research filter applied: the
data exists, the generators already ran, nothing needs building, and no instrument owned by another
agent is modified. This is research, not a build.

The question for 150-N: **given a relation that holds, does the recorded state predict whether
generalizing or specializing it will survive — and does that prediction transfer to threshold values
never seen?** The ordinal parameter makes the transfer test meaningful in a way four categorical
labels never could.

Mandatory for 150-N, from the errors above:

1. **Stratified batch sampling.** Never `files[:N]`. Sample across the full index range and report
   the stride. Generator populations and relation vocabularies both drift over the corpus timeline.
2. **Enumerate the generator inventory FIRST** and state which are in scope and why, rather than
   discovering the inventory in the results table three passes later.
3. Cluster-robust SE on the correct unit, per 147-K; count distinct model outputs before any SE.
4. Transfer tested along the **threshold parameter**, held out as ranges, not as identities.

## Self-identified weaknesses

- The stratified scan capped each batch at 80–120k rows, so within-batch ordering effects are still
  possible; only the across-batch window was fixed this pass.
- I have not verified that c4/c5's `holds` outcomes are non-degenerate, or that the parent states
  carry enough varying context to make prediction meaningful. 150-N must check that before reading
  anything, exactly as 146-J's contamination check did.
- The count of eight edge-bearing generators is from a 15-batch stratified sample; it is a lower
  bound, not a census.
- Three consecutive scope failures says the design review before running is the weak link, and
  naming that has not yet fixed it. The concrete change adopted here is procedural: inventory first,
  stratify always.

## Terminal

**CYCLE 149-M: OPEN 150-N.** The programme is not closed. It was never properly opened — I measured
a variance estimator and a measurement-selection generator, in the earliest 7% of the corpus, and
concluded from that about the whole.
