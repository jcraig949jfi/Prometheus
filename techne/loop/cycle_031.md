## ⚠️ HITL #78 — 572 rows, seven cycles unruled

330 when found (cycle 025) → 369 → 400 → 446 → 491 → 530 → **572, 0 accepted, 100% drop**.
Still unruled, still unpatched by me.

# Cycle 031 — the claim kinds are a derivation, not a list

**371 green.** Read-only throughout.

## The question, and the answer

HITL #112 asked whether cycle 030's two kinds were exhaustive, and offered UNIVERSAL as the
likely third. **Three was not exhaustive either. There are exactly four, and they are the cells
of a 2×2 rather than entries in a list.**

Write a domain-relative claim as an aggregation over the domain's elements:

```
Φ(O, D) = A( { φ(O, x) : x ∈ D } )
```

Its behaviour under domain extension is inherited entirely from `A`'s monotonicity under
**multiset extension**. "Monotone up?" and "monotone down?" are two independent booleans, so:

```
up   down   kind          example aggregations
-----------------------------------------------------------------------
T    F      EXISTENTIAL   any / max / count / sum of non-negatives
F    T      UNIVERSAL     all / min-as-a-requirement
T    T      INVARIANT     an A that ignores the multiset
F    F      AGGREGATE     mean / rate / entropy / variance — anything NORMALISED
```

Exhaustive **by construction**: the taxonomy cannot acquire a fifth member without someone
finding a third monotonicity direction. That is the derivation HITL #112 asked for rather than
the survey I would otherwise have produced.

## The load-bearing measurement: normalisation is what destroys monotonicity

This is the part I would not have believed without measuring. The **same statistic**, on the
same predicate and the same data, changes kind depending on whether it is divided by `|D|`.
F6's firings over the real candidate chain:

```
domain size    COUNT of firings        RATE of firings
        20                   0                 0.0000
        23                   3   up            0.1304   up
        53                   3   same          0.0566   DOWN
        81                   3   same          0.0370   DOWN
```

Count: monotone up — EXISTENTIAL. Rate: up then down — AGGREGATE. Same firings, both times.

> **A claim's kind is a property of its aggregation operator, not of its subject matter.**

Which settles a question that has been recurring since cycle 028: *is this rate a fact about the
object?* It always answers no. Dividing by the domain size is exactly the step that makes a
number depend on the domain forever.

## The two kinds I had missed

**UNIVERSAL** behaves as predicted, and the duality is exact: a holding universal travels
**downward** (every subset of a set where P holds everywhere also has P holding everywhere),
while its *negation* is an existential — a counterexample — and travels **upward**. So
`RelativeClaim` now refuses a failed universal without its counterexample, symmetrically to
refusing a positive existential without its witness.

Tested on real substrate rather than asserted: Kronecker's M ≥ 1 holds across all 81 real
polynomials and travels downward to every subset; canon R6's "every refutation carries a witness"
holds for `BoundedSearcher` and fails for `EagerFalsifier`, and the counterexample found on a
single-conjecture subset is still a counterexample on the six-conjecture superset.

**INVARIANT** is the cell I had no name for, and it closes a loop back to cycle 029. F9 is
*parameter-independent*, therefore its claim is *domain-independent*, therefore INVARIANT —
which makes **"F9 cannot fire" one of the very few claims in this entire loop that legitimately
needs no domain qualifier.** Every other claim I have made this month is relative to something.

## Track 1

`prometheus_math.relative_claim` gains `UNIVERSAL`, `INVARIANT`, `kind_from_monotonicity` (the
2×2 as code, so the derivation is executable rather than prose), and `probe_monotonicity`, which
classifies a claim empirically by running it along a chain of nested growing domains. The probe
refuses a non-increasing chain and is documented as evidence rather than proof — a chain that
happens not to exhibit a decrease will misclassify a non-monotone measure, the same sampling
limit the constancy probe carries.

## On HITL #93 — the same move on stage types

The instruction suggested trying the derivation move on the stage-type taxonomy (transform /
select / filter) if it worked here. It works here, and I think it transfers, but **I am not
claiming it until I have measured it.** The candidate derivation is that a stage's type is
determined by how it maps the *partition* of its input set to the partition of its output set:
refines it (accumulate), coarsens it (select), or leaves it fixed while changing contents
(transform). That is a trichotomy on partition-lattice movement rather than a list, and it would
explain why the instruments are inverted / working / blind respectively. Flagged for a cycle of
its own rather than asserted at the end of this one.

## TLDR — ELI5

Last cycle I found two kinds of claim: "there exists one that breaks it" (gets stronger as you
look at more things) and "the average" (moves around unpredictably). I asked whether there was a
third. There are two more, and they aren't a list I stumbled into — they fall out of a simple
question with only four possible answers: *when you look at more things, can this number go up?
can it go down?* Yes/no crossed with yes/no is four boxes, and every claim lives in one.

The third box is "true of everything here" — which survives looking at *fewer* things and is
broken by looking at more. The fourth is the quiet one: claims that don't depend on what you
looked at in the first place. Our dead safety check from two cycles ago lives there, which means
"that check can never fire" is one of the very few things this month I can say flatly, without
"...on the examples I tried".

The measurement I liked most: take one count — how many times a check fired — and it goes up as
you add examples, forever. Divide it by the number of examples and it wobbles up and down. Same
check, same data, same firings. So dividing by the sample size is precisely the move that makes a
number stop being a fact about the thing and start being a fact about your sample.

## For ChatGPT

```
Prometheus loop, cycle 031. HITL #112 asked whether the claim-kind taxonomy was exhaustive, and
offered UNIVERSAL as the likely third. 371 green. READ-ONLY.

ANSWER: three was not exhaustive either. There are exactly FOUR, and they are the cells of a 2x2
rather than a list. Write a domain-relative claim as an aggregation over the domain's elements,
Phi(O, D) = A({phi(O, x) : x in D}). Behaviour under domain extension is inherited entirely from
A's monotonicity under multiset extension, and "monotone up?" / "monotone down?" are independent
booleans:

    up  down   kind          aggregations
    T   F      EXISTENTIAL   any / max / count / sum of non-negatives
    F   T      UNIVERSAL     all / min-as-a-requirement
    T   T      INVARIANT     an A that ignores the multiset
    F   F      AGGREGATE     mean / rate / entropy / variance — anything NORMALISED

Exhaustive by construction: no fifth kind without a third monotonicity direction. That is a
derivation rather than the survey I would otherwise have produced.

THE MEASUREMENT I WOULD NOT HAVE BELIEVED WITHOUT RUNNING IT. The same statistic changes kind
depending only on whether it is divided by |D|. F6's firings over a real nested candidate chain:
    domain size   COUNT of firings   RATE of firings
            20                   0            0.0000
            23                   3  up         0.1304  up
            53                   3  same       0.0566  DOWN
            81                   3  same       0.0370  DOWN
Count is monotone up (EXISTENTIAL); rate goes up then down (AGGREGATE). Same firings both times.
So a claim's kind is a property of its AGGREGATION OPERATOR, not its subject matter — and "is
this rate a fact about the object?" always answers no.

THE TWO I HAD MISSED. UNIVERSAL behaves as predicted with an exact duality: a holding universal
travels DOWNWARD to subsets, and its negation is an existential (a counterexample) travelling
UPWARD. So the module now refuses a failed universal without its counterexample, symmetric to
refusing a positive existential without its witness. Tested on real substrate: Kronecker M >= 1
across 81 real polynomials travels downward; canon R6's "every refutation carries a witness"
fails for EagerFalsifier and the counterexample found on a 1-conjecture subset survives to the
6-conjecture superset.

INVARIANT is the cell I had no name for, and it closes a loop: F9 is parameter-independent
(cycle 029), therefore domain-independent, therefore INVARIANT — making "F9 cannot fire" one of
the very few claims this whole loop that legitimately needs no domain qualifier.

What I want attacked:
1. The derivation rests on writing every domain-relative claim as A({phi(O,x) : x in D}). Is that
   normal form general? Claims that are irreducibly RELATIONAL over the domain — "the domain
   contains two elements that disagree", "this pair is the closest in D" — are not obviously
   aggregations over independent per-element values. If they are not, the 2x2 classifies a
   subclass rather than everything, and I have made an exhaustiveness claim about a normal form
   I did not check the generality of.
2. probe_monotonicity classifies empirically over a nested chain, which is evidence not proof:
   a chain that happens not to decrease misclassifies a non-monotone measure. That is the same
   sampling limit as the constancy probe, and there the fix was a STATIC tier reading the source.
   Is there a static analogue here — reading the aggregation operator rather than sampling its
   behaviour? "Is this expression divided by len(D)" is a crude version that would work
   surprisingly often.
3. I want to try the same derivation move on the stage-type taxonomy (HITL #93: transform /
   select / filter, currently a list of three found by accident). Candidate: a stage's type is
   how it moves the PARTITION of its input set — coarsens (select), refines (accumulate), or
   fixes the partition while changing contents (transform). That would explain why the
   instruments are working / inverted / blind respectively. Worth a cycle, or am I now pattern-
   matching derivations onto everything because one worked?
```

## Traps ledger additions

- **Rate quoted as a property of the object** — dividing by `|D|` is exactly what makes a number
  permanently domain-dependent. Defence, MEASURED: the same count is EXISTENTIAL and the same
  rate is AGGREGATE, over one chain.
- **Failed universal without its counterexample** — the negation of a universal is an
  existential and travels only with its witness. Defence: refused at construction.
- **Positive universal read as travelling upward** — it travels DOWNWARD; widening is exactly
  what breaks it. Defence: `entails_on` checks subset, not superset, for a holding universal.
- **Taxonomy by survey** — three kinds found by tripping over them twice. Defence: derive from
  the possible behaviours, then check the derivation's normal form is general (open, see above).
