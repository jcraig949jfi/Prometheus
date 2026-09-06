# Six findings about existing machinery, found by feeding it proposed templates

**Date:** 2026-09-06. **Seat:** Herakles. **Branch:** `vivarium/v0-2026-09-05`
at `7a91054ad`. Reviewed source pinned in `01_STARTING_POINT.md`.

These were not the object of the pass. They surfaced because the pass ran real
proposed templates through the real registry and the real executor instead of
reasoning about them. Each is reproducible in under a minute. Each belongs to a
lane that is not mine.

---

## F-1. A length mismatch is scored silently, with a lowered ceiling

**Lane: SFE / Vivarium. Severity: this is the highest-severity item here.**

`evaluate_bitstring` accepts a candidate whose length differs from the declared
`length` and returns a COMPLETED result with a plausible score. There is no
error and no flag.

The scoring function is

    n = min(len(bits), len(target))
    return sum(1 for i in range(n) if bits[i] == target[i]) / len(target)

It matches over the overlap but **divides by the target length**. So a short
candidate is scored against the full target, and its achievable score is capped
at `len(bits) / length`, with `solved` (score >= 1.0) unreachable.

Measured, target length 32, seed_root 110663:

    len(bits)   status      score    achievable ceiling
    ---------   ---------   ------   ------------------
           16   COMPLETED    0.250   0.500
            8   COMPLETED    0.125   0.250
           32   COMPLETED    0.531   1.000

This is the failure shape this programme has been burned by repeatedly: a
ceiling that hides the quantity of interest, and an outcome rule that cannot
fire. A template with this defect would run, fossilize, and contribute
observations that look like weak performance rather than a broken spec.

**It is reachable today from a template that passes every existing check.** Two
of my own mined templates do exactly this. See F-3.

**Smallest fix:** reject `len(bits) != length` in the executor, as an invalid
candidate, the same way non-binary characters are already rejected. That is one
condition added to a check that already exists. A weaker alternative, returning
the mismatch as a result field, is worse: it keeps the bad observation in the
record and relies on every downstream reader to notice.

**Related, and separate.** `BitStringExecutor`'s docstring says the target is
derived "from the world's seed so every world shares the SAME landscape iff it
shares the seed". Vivarium deliberately passes the REPEAT's derived seed, not
the world seed, and says so in its own comment. Under `seed_derivation` of
`sha256_index` or `linear_index` the SFE docstring's invariant no longer
describes what happens: repeats of one world get DIFFERENT landscapes. Both
sides are internally consistent; the shared claim between them is stale. Worth
one docstring correction so nobody designs against the wrong invariant.

---

## F-2. `templates.check()` validates parameter names, not drawability

**Lane: Archaeon.**

`check()` compares `set(param_space["payload"])` against the kind's exact
parameter set and returns `runnable: True` when they match. It does not verify
that each axis carries a spec the draw vocabulary can actually consume.

Measured over the 69 mined templates after shape migration:

    check() says runnable ....................... 7
      of those, draw_params() succeeds .......... 3
      of those, draw_params() raises ............ 4

The four that raise carry an axis whose value was destroyed upstream, so the
spec is `{"int_range": null}`. `check()` sees the key `int_range` is absent
from nothing, matches the name set, and passes. `_draw_value` then unpacks
`null` and raises `TypeError`.

A registry that reports a template runnable and then crashes when the tick
draws from it will fail inside the scheduled producer, not at admission, which
is the expensive place to find out.

**Smallest fix:** have `check()` attempt a draw with a fixed seed and report
failure with the offending axis named. It is the same work the tick will do
anyway, and doing it at admission is free.

---

## F-3. Nothing validates coherence BETWEEN axes

**Lane: Archaeon, with F-1 as the reason it matters.**

`bits` and `length` are not independent: for the experiment to mean what it
says, `len(bits)` must equal `length`. The registry's draw vocabulary has a
`uniform_bits` spec that expresses exactly this dependency, and the frozen
baseline uses it. But nothing REQUIRES it.

A template may declare `bits` as a literal choice list and `length` as a
separate choice list, and the draw will happily pair a 16-bit string with
length 32. Two of the three templates that draw successfully do this:

    template                    drawn bits            drawn length   coherent
    ------------------------    ------------------    ------------   --------
    evolcomp.fitness.v0         24 bits (uniform)               24   yes
    algorithm_discovery.v0      16 bits (literal)               32   NO
    discovery_informatics.v0     8 bits (literal)               32   NO

Combined with F-1, the incoherent pair produces a silently capped score. So the
full path from a PROPOSED template to a corrupted observation is:

    check() runnable -> draw succeeds -> executor COMPLETED -> capped score

with no error raised at any step.

**Smallest fix:** in `check()`, for kind `evaluate_bitstring`, require that
`bits` is declared as `uniform_bits` referencing `length`, or that every
literal choice has a length matching every declared length. Generalising, the
registry needs a place to declare cross-axis constraints; the narrow version
above is worth having before the general one.

---

## F-4. The degeneracy guard misses every stateful kind under `state = reset`

**Lane: Vivarium. Surfaced by an analyst on chunk 5; verified here by
execution.**

`repeat_plan` computes:

    degenerate = (how == "constant" and rep["count"] > 1
                  and rep["state"] == "reset"
                  and not (kind.stateful if kind else False))

The last term excludes stateful kinds. But `state = "reset"` ALREADY means no
state carries between repeats, so a stateful kind under reset behaves exactly
like a stateless one. The exclusion is wrong in precisely the case the guard
was built to catch.

Measured. Constant seed derivation, `state = reset`, count 4:

    kind                 flagged degenerate   four displacements
    ------------------   ------------------   -------------------------
    evaluate_bitstring   True                 (stateless, correctly caught)
    random_walk_v0       False                0.473975951 x 4, identical

Within-world variance is exactly zero and the bench reports the spec as
non-degenerate. The guard's own docstring says degeneracy here is "arithmetic,
not a judgement". The arithmetic is simply incomplete.

**Smallest fix:** drop the `not kind.stateful` term. `state == "reset"` is
sufficient on its own; requiring statelessness as well makes the condition
strictly too narrow. Under `state = "persist"` the term is unnecessary anyway,
because the state genuinely carries and the repeats genuinely differ.

**Why it matters beyond tidiness.** Both random-walk templates in chunk 5 are
exposed to it, and this is the guard whose entire purpose is to stop a
zero-variance experiment being mistaken for a measured null. A silent
zero-variance arm is the same failure family as F-1.

---

## What this says about the pass itself

The first four share a shape. Each layer validates the thing it owns and
assumes the neighbouring layer validated the rest. Names are checked but not
values; values are checked but not their relationships; relationships are
assumed but never asserted. Nothing here is careless work. It is the ordinary
seam failure that appears when three seats each hold one layer.

It also means the count that matters is not "how many templates are runnable"
but "how many produce a coherent observation". After shape migration:

    load .................................. 69
    check() runnable ....................... 7
    draw succeeds .......................... 3
    draw is coherent with the executor ..... 1

That last number, one, happens to agree with my earlier review packet's
headline. The agreement is a coincidence: the packet reached it by conflating
executor availability with parameter completeness, and this reaches it by
following a template all the way to a valid observation. The reasoning that
produced the earlier number was still wrong, and section 2 of
`01_STARTING_POINT.md` records why.

## F-5. `step_scale` is a pure rescaling, not an independent axis

**Lane: Vivarium and Archaeon jointly. Surfaced by an analyst on chunk 6;
verified here by execution.**

`random_walk_v0` draws each increment as `step_scale * (uniform(0,1)*2 - 1)`
from the repeat's seed. The scale multiplies every increment identically, so at
a FIXED seed the whole trajectory is the same walk rescaled.

Measured, seed 999, steps 100:

    step_scale   displacement    displacement / step_scale
    ----------   -------------   -------------------------
           0.1     +0.26428096          +2.6428095958
           0.5     +1.32140480          +2.6428095958
           1.0     +2.64280960          +2.6428095958
           2.0     +5.28561919          +2.6428095958
           7.3    +19.29251005          +2.6428095958

Identical to ten decimal places across a 73-fold range. The walk therefore has
ONE informative payload axis, `steps`, plus the seed. Its declared 2-D
parameter space is one dimension and a scale factor.

**Why this is more than a curiosity.** A template that sweeps `step_scale`
within a seed manufactures observations that are PERFECTLY correlated by
construction. Fed to a variance-based detector, a set of exactly proportional
displacements is not noise and not signal; it is an artifact of the sweep. D3
reads a variance ratio against neighbouring regions and D6 reads a jump against
a pooled SD, and both are exposed to a family of observations whose spread is a
deterministic multiple of a swept parameter.

This is the same hazard the programme already names in
`feedback_scale_vs_shape`: test mean-spacing normalisation FIRST on any gap
comparison. Here the normalisation is exact and free, because dividing by
`step_scale` removes the axis entirely.

**Smallest fix, and it is a template rule rather than a code change:** a walk
template should sweep `steps` and the seed, and hold `step_scale` fixed, unless
the experiment is specifically about the scale-invariance itself. If a sweep is
wanted anyway, the analysis must divide by `step_scale` before anything else.
Worth stating in the registry README so it is not rediscovered per template.

---

## F-3a. I committed F-3 myself, one commit after documenting it

Worth recording, because it is the cleanest available evidence that F-3 is a
real trap rather than a theoretical one.

My migration filled a destroyed `length` axis from the producer's generic
`ALLOWED_LENGTHS` of 16, 24 and 32. But that template's `bits` axis is a
literal list of 16-character strings. Two of the three drawable lengths
therefore produce exactly the F-1 silent ceiling: a 16-bit candidate against a
32-bit target, capped at 0.5, `solved` unreachable, no error.

I wrote the finding and then shipped the bug in the next commit. An analyst
reading the same template caught it independently and, correctly, called the
fix a REPAIR rather than a design choice: the length is entailed by data the
template still carries, so recovering it is not an invention.

The migration now derives `length` from the surviving literals when they exist,
and refuses to fill when the literals disagree with each other. Verified after
the fix:

    drawable templates ........ 7
    draws that succeed ........ 3
    INCOHERENT payloads ....... 0   (was 2)

The four that still fail at draw are the walk templates whose `steps` and
`step_scale` were destroyed. Nothing in the repository declares a range for
either, so there is no bench-native value to recover and they stay null. That
is the correct outcome, not an omission.

---

## F-6. `bits` is not a discriminating axis, and two templates rest on it

**Lane: a design rule for the registry, not a code defect. Predicted
analytically in `01_STARTING_POINT.md` section 4; surfaced independently by an
analyst on chunk 4; confirmed here by execution.**

The hidden target is a hash, so it is uniform and independent of the candidate.
Every position matches with probability one half regardless of what was
submitted. So the score distribution for a FIXED bitstring across seeds is the
same distribution for every bitstring. The candidate is exchangeable.

Measured, length 16, 4000 hash-derived targets per pattern:

    pattern           mean     stdev    P(score >= 0.75)
    --------------   ------   -------   ----------------
    blocky           0.5036   0.1248             0.0418
    alternating      0.5015   0.1277             0.0437
    all ones         0.5004   0.1242             0.0365
    all zeros        0.4996   0.1242             0.0352
    arbitrary        0.4999   0.1248             0.0343

    analytic prediction: mean 0.5, stdev sqrt(1/(4L)) = 0.1250

Agreement is exact to sampling error, and the differences between patterns are
noise.

**The consequence is a rule.** A template whose arms differ ONLY in the
bitstring is comparing exchangeable arms. It cannot separate them at any
threshold, at any sample size, for any choice of literals. This is knowable
before anything runs, which makes it the `feedback_gate_must_be_shown_reachable`
case in its purest form: the contrast has no attainable difference.

Two templates in the inbox are built exactly this way:

    template                    field                   literal candidates
    ------------------------    --------------------    ------------------
    algorithm_discovery.v0      Algorithm Discovery                      2
    discovery_informatics.v0    Discovery Informatics                    3

Both should be marked degenerate rather than admitted. Neither is salvageable
by choosing better literals, because the defect is in the axis, not the values.

**The same fact is a gift, used the other way round.** Because the distribution
is known in closed form and is independent of the candidate, a bits-varying
template is a FREE NEGATIVE CONTROL for the whole bitstring family: it must
show no effect, and any effect it does show is an instrument defect. That is
worth admitting deliberately, labelled as a null, and it costs nothing to run.

**What IS discriminating**, and this is where a bitstring template should put
its contrast: `length`, which changes the variance as 1/(4L) and changes the
landscape entirely; the seed, which changes the target; `seed_derivation`,
which decides whether repeats share a target; and the RELATIONSHIP between a
candidate and a target, which the bench cannot currently express at all and is
the missing relatedness axis recorded in `03_LEADING_DESIGN_VERSION_SPACE.md`.

---

## A limitation on this pass, declared

The session's web-search budget was exhausted during chunk 5, so REFERENCE
VERIFICATION could not be completed for most templates. Analysts were
instructed to mark an attribution UNRESOLVED rather than assert it, and their
VERIFIED marks after that point rest on established knowledge rather than a
fresh fetch. One correction did land before the budget ran out: the
computational-serendipity template names a two-author standards document; the
actual work is a five-author ICCC 2013 discussion paper proposing chance,
sagacity and value. Treat every remaining reference as unverified.

## Reproduction

    cd F:/Prometheus
    python - <<'EOF'
    import sys; sys.path.insert(0,'SerendipityFoundry/SerendipityFoundryEngine')
    from sfe.executors import BitStringExecutor, WorkPackage
    ex = BitStringExecutor(length=32)
    for bits in ('1111000011110000', '10101010', '0'*32):
        wp = WorkPackage(work_id='w', world_id='w', kind=ex.kind,
                         payload={'bits': bits}, seed_root=110663)
        r = ex.execute(wp)
        print(len(bits), r.status, r.result['score'])
    EOF

For F-2 and F-3, run `migrate_to_registry_shape.py` in this directory, then
call `templates.check()` and `templates.draw_params()` over the output.
