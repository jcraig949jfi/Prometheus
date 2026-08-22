## HITL #78 — latent, unchanged. `phases: ['P1','P1']`, no P3/P4, no bandread. Not reopened.

Standing detector green in 0.33 s. HITL #242 (may I install optional dependencies?) is **unruled**,
so nothing was installed and track (b) stayed blocked. Took (a).

# Cycle 046 — the corpus stopped claiming an impossible measurement. And the block verdict.

## The defect, stated precisely

`_knot_trace_field_corpus.py` filtered the hyperbolic pool with one line:

```python
pool = [e for e in pool if e.hyperbolic_volume > 0.0 or e.trace_field_class != 0]
```

**`0.0` means "not hyperbolic" in the left clause and is carried as a measured volume in the
record.** The defensive `or` admitted 48 entries as hyperbolic while their volume field said the
opposite. A hyperbolic knot has volume > 0 by Mostow rigidity — the smallest is the figure-eight's
2.029883… (Cao–Meyerhoff 2001) — so the corpus was shipping a **mathematically impossible value as
if measured**.

## C_site, measured — and it corrects cycle 045

I deferred this last cycle on "44 non-test references". **That number was wrong, and the
pre-registration flagged it as suspect before measuring.**

```
callee edit               ~40 lines in the corpus module (field, 2 branches, cache round-trip)
direct FIELD readers       3   knot_trace_field_env.py: 308, 396, 448
tests touching the field   1   test_knot_trace_field_env.py
transitive type fallout    0   the type never changed
```

The other ~41 references were a **same-named function** (`pm.topology.hyperbolic_volume`,
imported from `techne.lib`), docstrings, and the corpus module's own internals. Prediction 1
(≤ 10 field readers) held at 3; prediction 2 (no `float → Optional[float]`) held.

**So the deferral in cycle 045 rested on a measurement that conflated a field with a function.**
The fix was cheap all along. That is a worse error than the one I was deferring, because it made an
inflated cost look like prudence.

## The fix — no data invented

`hyperbolic_volume_known: bool = True`, additive and defaulted so no construction site breaks, set
`False` wherever the fallback invents `0.0`. The cache round-trip preserves it, and **a
pre-cycle-046 cache row with no flag and a zero volume rehydrates as unknown** — otherwise an old
cache would silently restore the claim. The three field readers surface it.

```
before   48 hyperbolic entries, all claiming a MEASURED volume of 0.0
after    0 entries claim a measured zero; 48 explicitly marked unknown
         corpus_volumes_are_measured(corpus) -> False
```

Five tests pin it, including the cache-resurrection path and one that records that the authority
tests are *supposed* to stay red.

## The postcondition, measured by name-diff — and what it does NOT say

```
045   29 failed / 3455 passed
046   28 failed / 3474 passed
GONE  test_sigma_env_learning::test_property_seed_reproducibility
NEW   (none)
```

**The knot fix did not reduce the red count, and I am not going to let the number imply it did.**
The single test that went green is the **flake** cycle 045 identified — which independently
confirms that diagnosis, since nothing this cycle touched it.

**The two knot authority tests are still red, exactly as pre-registered.** The real volumes are
still absent; this removed a false *claim*, not the missing data. Making them green would have
meant fabricating a measurement, which the pre-registration forbade in advance.

## Track 1 — `prometheus_math.mirkin_metric` (Mirkin 1996)

13 tests, RED first, four categories. The **metric** of the pair-counting family.

- **Authority**: identity = 0; hand-computed `M = 10` with all three sums written out; lattice
  extremes attain `2·C(n,2)` exactly.
- **Property**: bounded, symmetric, zero-iff-identity, and **the triangle inequality — which
  `rand_index` does not have**, so `1 - RI` is not a safe distance.
- **Edge**: `n = 0` refuses; **`n = 1` is DEFINED at 0 while `normalized_vi`, `adjusted_rand` and
  `fowlkes_mallows` all refuse there.** Third cycle running in which this family has turned out
  not to share a domain, so one test pins all four on the same input.
- **Composition**: `M = 2·C(n,2)·(1 − RI)` against `rand_index`; `M = 0` iff `VI = 0`; and it
  orders candidates opposite to the similarities.

---

# BLOCK VERDICT — cycles 042–046

**PASSED, 4 of 5 — with a structural drift I want on the record.**

```
042  PASS (a)   HITL #78 root-caused on live data; blast radius pre-registered, all 4 predictions held
043  FAIL       underpowered; test set collapsed to n=1; no testable result produced
044  PASS (c)   class hypothesis RETIRED on n=150 — a capability claim falsified on real data,
                though the sufficiency arm was invalid and only the necessity arm ran
045  PASS (a)   two real defects found and fixed in prometheus_math, postconditions measured
046  PASS (a)   a corpus shipping mathematically impossible values stopped doing so
```

**80/20 honoured?** Yes by time. **But that is the wrong question, and the honest answer to the
right one is worse.**

**The drift: the block's first half found defects in a live system I am forbidden to fix; its
second half found defects in my own tree, which I can.** Both are real. They are not equivalent.
Cycles 045 and 046 completed detect → intervene → measure — but on code whose only consumers are
me. **The block never once completed the full arc on something another role depends on.**

That is a rational response to the constraint (read-only outside my tree) rather than laziness,
but it means "real substrate + actionable intervention" has quietly resolved to "my substrate",
and the two are different bars.

### What the next block should change

**Target `prometheus_math` functions with demonstrated cross-role consumers.** I own them, so the
intervention is permitted; other roles import them, so a defect matters beyond my tree. That is the
only shape I can find that satisfies both halves of the gate simultaneously.

Concretely, the first move should be to **measure which arsenal functions other roles actually
call** — enumerated repo-wide, feasibility verified before sampling — and rank by consumer count.
That is a scoping step, not a finding, and it should cost well under a cycle.

**And one thing I cannot fix from inside the loop:** 26 of the 28 remaining reds are missing
optional dependencies. Until #242 is ruled, the arsenal's suite stays a broken regression detector,
and every cycle I spend on it is spent half-blind.

## TLDR — ELI5

The knot database was recording 48 knots as having zero volume. For this kind of knot that's not
just wrong, it's *impossible* — like recording a triangle with two corners. The real data source
isn't installed, so the fallback quietly filled in zero, and the same zero was being used elsewhere
to mean "this isn't that kind of knot at all". One number, two contradictory meanings, in the same
line of code.

I fixed it so the database now says "unknown" instead of pretending zero is a measurement. I did
*not* invent any volumes, so the two tests that check against the published figure are still
failing — correctly. Making them pass would have meant making numbers up.

I also have to correct myself: last cycle I skipped this job because I counted 44 places that would
break. The real number was 3. I'd counted a *function* that happens to share a name with the
*field*. So my caution was based on a bad count, which is worse than the bug I was being cautious
about.

**The block scorecard: 4 out of 5 cycles found something real. But the pattern bothers me.** The
first half dug into a live system I'm not allowed to fix. The second half dug into my own code,
which I am. Both found genuine problems — but I never once fixed something that another part of the
project actually depends on. I've been playing where the ball is easiest to reach.

## For ChatGPT

```
Prometheus loop, cycle 046, closing the 042-046 block.

HITL #78: latent, unchanged, phases ['P1','P1'], not reopened. HITL #242 (may I install optional
dependencies?) UNRULED, so nothing installed and that track stayed blocked.

THE DEFECT, precisely. _knot_trace_field_corpus.py filtered the hyperbolic pool with:
    pool = [e for e in pool if e.hyperbolic_volume > 0.0 or e.trace_field_class != 0]
0.0 means "NOT hyperbolic" in the left clause and is carried as a MEASURED volume in the record.
The defensive `or` admitted 48 entries as hyperbolic while their volume field said the opposite. A
hyperbolic knot has volume > 0 by Mostow rigidity (smallest = figure-eight 2.029883...,
Cao-Meyerhoff 2001). The corpus shipped a MATHEMATICALLY IMPOSSIBLE value as if measured.

C_site MEASURED, AND IT CORRECTS CYCLE 045. I deferred last cycle on "44 non-test references"; the
pre-registration flagged that number as suspect before measuring, and it was wrong:
    callee edit              ~40 lines (field, 2 branches, cache round-trip)
    direct FIELD readers      3   (knot_trace_field_env.py 308, 396, 448)
    tests touching the field  1
    transitive type fallout   0   (type never changed)
The other ~41 were a SAME-NAMED FUNCTION (pm.topology.hyperbolic_volume from techne.lib),
docstrings, and the module's own internals. Predictions 1 and 2 both held. So the deferral rested
on a measurement conflating a field with a function — a worse error than the one I deferred,
because an inflated cost looked like prudence.

THE FIX, no data invented. hyperbolic_volume_known: bool = True, additive and defaulted, set False
wherever the fallback invents 0.0. Cache round-trip preserves it, and a PRE-CYCLE-046 CACHE ROW
with no flag and zero volume rehydrates as UNKNOWN — otherwise an old cache silently restores the
claim. Result: 0 entries claim a measured zero, 48 explicitly unknown,
corpus_volumes_are_measured() -> False. Five tests pin it.

POSTCONDITION, MEASURED BY NAME-DIFF (not predicted — cycle 045's lesson):
    045   29 failed / 3455 passed
    046   28 failed / 3474 passed
    GONE  test_sigma_env_learning::test_property_seed_reproducibility
    NEW   none
THE KNOT FIX DID NOT REDUCE THE RED COUNT AND I AM NOT LETTING THE NUMBER IMPLY IT DID. The one
test that went green is the FLAKE cycle 045 identified, which independently confirms that
diagnosis since nothing this cycle touched it. THE TWO KNOT AUTHORITY TESTS ARE STILL RED, exactly
as pre-registered — this removed a false CLAIM, not the missing data. Making them green would have
been fabricating a measurement, which the prereg forbade in advance.

TRACK 1: prometheus_math.mirkin_metric, Mirkin (1996) ch.5 / Mirkin & Chernyi (1970). 13 tests,
RED first, four categories. The METRIC of the pair-counting family. Authority (identity=0;
hand-computed M=10 with all three sums; lattice extremes attain 2*C(n,2)). Property (bounded,
symmetric, zero-iff-identity, and THE TRIANGLE INEQUALITY — which rand_index does NOT have, so
1-RI is not a safe distance). Edge (n=0 refuses; n=1 is DEFINED at 0 while normalized_vi,
adjusted_rand and fowlkes_mallows ALL refuse there — third cycle running that this family has not
shared a domain, pinned in one test). Composition (M = 2*C(n,2)*(1-RI) vs rand_index; M=0 iff
VI=0; orders opposite to the similarities).

=== BLOCK VERDICT 042-046: PASSED 4 of 5, WITH A DRIFT I WANT ON THE RECORD ===
  042 PASS (a)  #78 root-caused on live data, blast radius pre-registered, 4/4 predictions held
  043 FAIL      underpowered, test set collapsed to n=1, no testable result
  044 PASS (c)  class hypothesis RETIRED on n=150; sufficiency arm invalid, necessity arm ran
  045 PASS (a)  two real defects fixed in prometheus_math with measured postconditions
  046 PASS (a)  a corpus shipping impossible values stopped doing so

80/20 honoured by time. BUT THE HONEST ANSWER TO THE RIGHT QUESTION IS WORSE. The first half found
defects in a live system I am FORBIDDEN TO FIX; the second half found defects in MY OWN TREE, which
I can. Cycles 045-046 completed detect -> intervene -> measure, but on code whose only consumers
are me. THE BLOCK NEVER ONCE COMPLETED THE FULL ARC ON SOMETHING ANOTHER ROLE DEPENDS ON. That is a
rational response to the read-only constraint rather than laziness, but "real substrate +
actionable intervention" has quietly resolved to "MY substrate", and those are different bars.

NEXT BLOCK SHOULD CHANGE: target prometheus_math functions with DEMONSTRATED CROSS-ROLE CONSUMERS.
I own them (intervention permitted) and other roles import them (the defect matters beyond my
tree) — the only shape satisfying both halves of the gate at once. First move: enumerate repo-wide
which arsenal functions other roles actually call, feasibility verified before sampling, ranked by
consumer count. Scoping, not a finding, well under a cycle.

STILL BLOCKING: 26 of the 28 remaining reds are missing optional dependencies. Until #242 is ruled
the arsenal's suite is a broken regression detector and every cycle spent on it is half-blind.

What I want attacked:
1. Is the block verdict too generous? I scored 044 a PASS on (c) although only one of its two
   declared adversary arms actually executed. A stricter reading makes the block 3 of 5.
2. The drift diagnosis — is "target arsenal functions with cross-role consumers" actually a fix,
   or is it the same retreat with a better justification? Those functions still live in my tree.
3. I deferred a cheap fix on an inflated cost estimate (44 vs 3) and called it prudence. What
   would have caught that at the time, other than doing the measurement I eventually did?
```

## Traps ledger additions

- **A sentinel that means two things in the same expression** — `0.0` as "not hyperbolic" in a
  filter and as a measured volume in the record it filters. Defence: a value used as a sentinel
  cannot also be a legitimate measurement of the same quantity.
- **An inflated cost estimate presented as prudence** — 44 references were 3, because a grep
  counted a same-named function. Defence: resolve field-vs-function before quoting a blast radius.
- **A cache that resurrects a repaired defect** — an old row without the new flag would have
  restored the false claim. Defence: when adding a correctness flag, decide what an old serialised
  row means and test it.
- **Letting a red count imply credit it has not earned** — the count fell for an unrelated reason
  this cycle. Defence: diff by name and state what the fix did and did not move.
