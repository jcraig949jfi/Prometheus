# Four defects in existing machinery, found by feeding it proposed templates

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

The four defects share a shape. Each layer validates the thing it owns and
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
