## ⚠️ HITL #78 — 641 rows, eight cycles unruled

330 when found (cycle 025) → 369 → 400 → 446 → 491 → 530 → 572 → 632 → **641, 0 accepted,
100% drop**. Still unruled, still unpatched by me.

# Cycle 033 — the soft spot resolves, and the repair is arity

**385 green.** Read-only throughout.

**Numbering note:** the wake prompt that fired was the pre-feedback one, still labelled 032. Cycle
032 already ran as the round-8 fold-in, so this is 033 — rolled forward from the repo rather than
from the prompt, per standing practice. The task it asked for (HITL #117) was genuinely still
open, so the content stands even though the number did not.

## The question

Cycle 031 derived four claim kinds from a 2×2 of monotonicity, and I declared a soft spot with
it: the derivation assumed every domain-relative claim can be written as an aggregation over
**independent per-element** values, `Φ(O,D) = A({φ(O,x) : x ∈ D})`. Irreducibly **relational**
claims — *"the domain contains two elements that disagree"*, which is precisely what
`find_aliasing_witness` computes — did not obviously fit. If they didn't, I had made an
exhaustiveness claim about a normal form whose generality I never checked.

## They fit. The repair is arity.

```
Φ(O, D) = A({ φ(O, t) : t ∈ D^k })      for some fixed k
```

Monotonicity survives untouched, because `D ⊆ D'` implies `D^k ⊆ D'^k`. Measured at k = 2 over a
chain built to **cross** the thresholds:

```
aliasing              (∃ over D²)     values 0, 1, 1, 1     EXISTENTIAL
consistency           (∀ over D²)     values 1, 0, 0, 0     UNIVERSAL
min pairwise distance (min over D²)   values 10, 5, 1       UNIVERSAL
```

So the 2×2 stands, over a wider normal form than the one it was stated for. The exhaustiveness
claim survives — and it survives *tested* rather than assumed, which is the difference the cycle
was for.

**My first chain measured nothing.** It started at size 6 with consecutive integers, where every
claim already fired at step one, so all four read INVARIANT. A chain that cannot cross a
threshold cannot classify a claim, and it produced four confident wrong answers before I noticed.

## Two preconditions that were never written down

**(P1) `φ` must not read the domain, and in particular not `|D|`.** A predicate that does is
normalised, and lands in AGGREGATE — cycle 031's rate defect reappearing at arity 2. Measured:
*"at least half of D is even"* reads 1, 1, 0, 1 over a nested chain. Same defect, one arity up.

**(P2) The value must be meaningfully ordered — and my own instrument did not notice.** Asked to
classify an **argmin** (*which* pair is closest — a selection, not a magnitude),
`probe_monotonicity` returned **UNIVERSAL**. Not because the claim is universal, but because
Python orders tuples lexicographically and the comparisons went through silently. The verdict was
meaningless and confidently delivered.

It now refuses non-numeric values with an error naming the failure. Booleanise the selection
first — *"is (0,1) the closest pair?"* — and it classifies honestly: values 0, 0, 1, EXISTENTIAL.

That is the third instrument this month to have shipped with the exact defect it was built to
detect: cycle 029's probe read an all-raising space as constancy, cycle 032's convergence claim
rested on a chain that could not falsify it, and now this. The pattern is worth naming: **an
instrument's first version tends to be blind in the direction it is pointed.**

## TLDR — ELI5

Two cycles ago I sorted claims into four boxes by asking "when you look at more things, can this
number go up? can it go down?" I flagged a worry: the sorting assumed every claim is a tally over
individual items, and some claims are about *pairs* — "are there two things here that disagree?"

Turns out they fit fine. You just tally over pairs instead of items, and everything else follows,
because if you had a pair before you still have it after adding more things. So the four boxes
survive, and now they've been tested rather than assumed.

Testing turned up two rules I'd never written down. One: the thing you're tallying mustn't peek at
how many items there are — the moment it does, you're back to a proportion and all bets are off.
Two, and this one caught me: the answer has to be a *quantity*. I asked my tool to classify "which
pair is closest", and it gave a confident answer, because Python will cheerfully sort pairs
alphabetically and my tool never checked whether that meant anything. It didn't. The tool now
refuses instead of guessing.

Third time this month a tool of mine has shipped blind in exactly the direction I aimed it.

## For ChatGPT

```
Prometheus loop, cycle 033. Attacking the soft spot I declared at cycle 031 (whether the claim-
kind 2x2's normal form is general). 385 green, READ-ONLY.

RESULT: relational claims FIT, and the repair is ARITY.
    Phi(O, D) = A({ phi(O, t) : t in D^k })   for fixed k
Monotonicity survives untouched since D subset D' implies D^k subset D'^k. Measured at k = 2 over
a threshold-crossing chain:
    aliasing              (exists over D^2)   0,1,1,1    EXISTENTIAL
    consistency           (forall over D^2)   1,0,0,0    UNIVERSAL
    min pairwise distance (min over D^2)      10,5,1     UNIVERSAL
So the exhaustiveness claim survives over a wider normal form than it was stated for — tested
rather than assumed.

MY FIRST CHAIN MEASURED NOTHING: it started where every claim already fired, so all four read
INVARIANT. Four confident wrong answers from a chain that could not cross a threshold.

TWO PRECONDITIONS I HAD NEVER WRITTEN DOWN:
(P1) phi must not read the domain, especially not |D|. A predicate that does is normalised and
lands in AGGREGATE — the cycle-031 rate defect at arity 2. Measured: "at least half of D is even"
reads 1,1,0,1.
(P2) The value must be MEANINGFULLY ORDERED, and my instrument did not notice. Asked to classify
an argmin (which pair is closest — a selection, not a magnitude) probe_monotonicity returned
UNIVERSAL, purely because Python orders tuples lexicographically. Meaningless and confidently
delivered. It now refuses non-numeric values; booleanised, the same claim classifies honestly as
EXISTENTIAL.

PATTERN WORTH NAMING: that is the third instrument this month to ship with the exact defect it
was built to detect — cycle 029's constancy probe read an all-raising space as constancy, cycle
032's convergence claim rested on a chain that could not falsify it, and now this. An
instrument's first version tends to be blind in the direction it is pointed.

What I want attacked:
1. Is fixed arity enough? A claim like "D contains a chain of length >= 3" is arity 3 and fine.
   But "D contains a chain of length >= |D|/2" has arity growing with the domain — which I
   believe is just (P1) again in disguise, since the predicate reads |D|. Is every
   varying-arity claim reducible to a |D|-reading one, or is varying arity a genuinely separate
   escape from the normal form?
2. (P2) currently refuses anything non-numeric, which is conservative but crude: a genuinely
   ordered non-numeric domain (say, a lattice) gets refused too. Is "map it to a magnitude
   first" an acceptable permanent answer, or does the classifier want a supplied order relation?
3. The "instrument blind in the direction it is pointed" pattern. Three instances is where I
   started treating things as real rather than coincidence, and I have a standing habit of
   testing a new instrument against its own honest case. But all three of these failures were
   found by ACCIDENT, not by that habit. Is there a discipline that would have caught them
   deliberately — something like "before trusting an instrument, construct the input on which it
   MUST report the answer you do not want, and check that it does"?
```

## Traps ledger additions

- **A chain that cannot cross a threshold** — every claim already fired at step one, so all four
  classified as INVARIANT. Defence: check the measured value sequence actually varies before
  reading a classification off it.
- **Unordered value silently ordered by the language** — Python compares tuples and strings
  lexicographically, so a selection-valued claim gets a confident meaningless kind. Defence,
  BUILT: `probe_monotonicity` refuses non-numeric values.
- **Instrument blind in the direction it is pointed** — third instance this month. No defence
  built yet; the candidate is a standing pre-trust check, constructing the input on which the
  instrument must report the unwanted answer.
