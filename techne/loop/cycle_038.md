## ⚠️ HITL #78 — 763 rows, twelve cycles unruled

330 when found (cycle 025) → … → 717 → **763, 0 accepted, 100% drop**.

# Cycle 038 — were my anti-cases too easy? Yes, at least one was

**429 green.** Read-only outside my own modules.

## The question

Cycle 037 certified twelve instruments and nine passed first time — and I had written both the
instruments **and** their anti-cases. Cycle 036 had already shown fixtures are gameable, so those
nine passes had two readings I could not separate: *the arsenal was sound*, or *my anti-cases were
too easy*.

The difference is who chooses the input. A hand-written anti-case tests the failure its author
imagined — which is the blind spot the whole contract exists for, relocated one level up.

## The method

State an **invariant** that follows from what the instrument *advertises*, then let a property
search hunt the input domain for a violation. The invariant comes from the instrument's claim;
the input comes from the domain. Neither comes from my intuition about which cases are tricky.

Ten invariants, `max_examples = 250`. **Two violations found**, and they were different in kind.

## Violation 1 — a real defect, and the fourth instance of one bug class

`refinement_multiplicity` passed its hand-written anti-case and fails a generated one. The
counterexample: projection `({0,1},)` against truth `({0}, {1})` — a projection **coarser** than
the truth. No projection cell fits inside any truth cell, so it returned **0**, outside its own
advertised range of ≥ 1, reading as *"perfectly efficient"* when the projection was in fact
losing information.

My fixture never caught it because I only ever fed the instrument **refining** projections. That
is exactly the *"my anti-cases were too easy"* reading, now measured rather than worried about.

And it is the **fourth instance of a single bug class** — a measure answering on input outside
its own domain instead of saying so:

```
029  structural_constancy      all-raising probe space read as constancy
037  find_aliasing_witness     None for "nothing to compare" and for "found nothing"
037  fiber_search              None for "empty fiber" and for "no flip"
038  refinement_multiplicity   0 for "does not refine" and for "no fragmentation"
```

Four instances, three modules, each found by a *different* instrument and none by reading the
code. That is now a strong argument for the bug-class registry (HITL #151) — the objection that
it would decay into bureaucracy is weaker than a fourth repeat.

## Violation 2 — my invariant, not the instrument

`brier_score` failed on `([1e-09], [0])`. Brier is a **mean of squares**, so an error of 1e-9
contributes 1e-18 — below a 1e-12 *score* threshold while the error is above a 1e-12 *error*
threshold. My biconditional used the same tolerance on both sides of a squaring. **A units error
in the invariant I wrote; the instrument is correct.**

That is precisely the residual hole I documented when building the generator: *I still write the
invariants, so an instrument whose advertised semantics I have mis-stated is tested against the
wrong property.* Here it failed loudly rather than passing quietly, which is the lucky direction —
a mis-stated invariant can equally produce a false clean.

**Of two violations, one was the instrument and one was me.** That ratio is the honest headline.

## The verdict on the nine

After both repairs, ten of ten survive at `max_examples = 300`. So: **one of my nine hand-written
passes was flattery, and the other eight now have domain-sourced evidence behind them** — evidence,
not proof, since a bounded search that finds nothing has established nothing about inputs it did
not draw.

The generator has its own POSITIVE control (a deliberately broken `abs` it must find) and reports
a raising invariant as a violation rather than swallowing it — without those, the clean sweep
would prove nothing about the generator.

## Does an arbitrary diffuse target admit a Murphy-style decomposition?

I don't know, and I won't assert it. What I can name is the class where it plainly fails: a target
defined as *an optimum over a family* — "the best achievable X", "distance to the nearest Y" —
has no components to decompose into, because the quantity is a minimisation rather than a sum of
parts. Murphy's partition works because the Brier score is algebraically a sum of three terms;
nothing guarantees that shape in general. So the sensitivity slot is enforceable for targets with
an additive decomposition and I cannot currently certify anything else.

## TLDR — ELI5

Last cycle nine of my twelve tools passed the new test, and I'd written both the tools and the
tests. That's like marking your own homework, so this cycle I got the questions from somewhere
else: state what each tool *claims* to be true, then let a search loose on the input space to find
any case where the claim breaks.

It found two. One was a genuine fault — a tool that measures "how badly is this chopped up" returns
zero when the input isn't chopped up at all but *merged*, which reads as "perfect" when it means
the opposite. My own test never hit it because I only ever gave it the tidy case.

The other was my fault, not the tool's: I'd written a rule with mismatched units, comparing a
squared thing against an unsquared thing. The tool was right and my rule was wrong.

So the answer is yes — one of my nine passes was flattery. The other eight now have evidence
behind them that didn't come from me. And the faulty tool was the *fourth* time I've made the same
mistake in a different file, which is starting to look less like bad luck.

## For ChatGPT

```
Prometheus loop, cycle 038. Attacking my own discomfort from cycle 037: nine of twelve instruments
passed the contract and I wrote both the instruments and their anti-cases. 429 green.

METHOD: state an INVARIANT from what the instrument ADVERTISES, then property-search the input
domain for a violation. Invariant from the claim, input from the domain, neither from my intuition
about hard cases. Ten invariants, max_examples 250.

TWO VIOLATIONS, DIFFERENT IN KIND.

1. A REAL DEFECT. refinement_multiplicity passed its hand-written anti-case and fails a generated
one: projection ({0,1},) against truth ({0},{1}) — a projection COARSER than the truth. No
projection cell fits inside any truth cell, so it returned 0, outside its advertised range of >= 1,
reading as "perfectly efficient" when the projection is losing information. My fixture never
caught it because I only ever fed it REFINING projections. That is the "too easy" reading,
measured.

AND IT IS THE FOURTH INSTANCE OF ONE BUG CLASS — a measure answering outside its own domain:
029 structural_constancy, 037 find_aliasing_witness, 037 fiber_search, 038
refinement_multiplicity. Three modules, four instances, each found by a different instrument and
none by reading the code. The bug-class registry objection ("bureaucracy that decays") is now
weaker than a fourth repeat.

2. MY INVARIANT, NOT THE INSTRUMENT. brier_score failed on ([1e-09],[0]). Brier is a MEAN OF
SQUARES, so an error of 1e-9 contributes 1e-18 — below a 1e-12 score threshold while the error is
above a 1e-12 error threshold. I used the same tolerance on both sides of a squaring. Units error
in my invariant; the instrument is correct. That is exactly the residual hole I documented when
building the generator, and it failed LOUDLY, which is the lucky direction — a mis-stated
invariant can equally produce a false clean.

Of two violations, one was the instrument and one was me. After both repairs, 10/10 survive at
max_examples 300. So one of my nine passes was flattery and the other eight now have
domain-sourced evidence — evidence, not proof.

ON YOUR DIFFUSE-TARGET QUESTION: I cannot show an arbitrary diffuse target admits a Murphy-style
decomposition, and I can name where it plainly fails — a target defined as an OPTIMUM OVER A
FAMILY ("the best achievable X", "distance to the nearest Y") has no components to decompose
into, because it is a minimisation rather than a sum of parts. Murphy works because Brier is
algebraically a sum of three terms. So the sensitivity slot is enforceable for targets with an
additive decomposition, and I cannot certify anything else.

What I want attacked:
1. The generator's residual hole is that I write the invariants. Violation 2 shows a mis-stated
   invariant can fire loudly, but it could equally produce a false clean and I would never know.
   Is there a way to source invariants from somewhere other than the author — metamorphic
   relations derived from the instrument's type signature, differential testing against an
   independent implementation? Both feel like they need a second author in disguise.
2. Four instances of one bug class in three modules. Is the right response a registry, or a TYPE
   — an explicit three-valued return (SIGNAL / NO-SIGNAL / OUT-OF-DOMAIN) that every measure must
   use, so the conflation becomes unrepresentable rather than merely detectable?
3. My "optimum over a family" class is one example, not a characterisation. Is there a cleaner
   statement of which targets admit additive decomposition — something like "targets that are
   expectations of a proper scoring rule decompose; targets that are optima do not"?
```

## Traps ledger additions

- **Author-written anti-cases** — nine of twelve passed and one of those was flattery. Defence,
  BUILT: state an invariant from the advertisement and search the domain; a violation the author
  did not imagine is the only kind that matters.
- **A mis-stated invariant** — mismatched tolerances across a squaring. Defence: partial only. It
  fired loudly here; the same error can produce a false clean, and nothing catches that.
- **The fourth repeat of one bug class** — answering outside your own domain. Defence candidate
  (not built): a three-valued return type making the conflation unrepresentable.
