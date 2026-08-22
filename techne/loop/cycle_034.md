## ⚠️ HITL #78 — 684 rows, nine cycles unruled

330 when found (cycle 025) → 369 → 400 → 446 → 491 → 530 → 572 → 632 → 641 → **684, 0 accepted,
100% drop**. Still unruled, still unpatched by me.

# Cycle 034 — the preprocessing thread closes, narrowly

**395 green.** Read-only throughout.

## The discipline changed the question before I could ask it wrong

HITL #129 was adopted this cycle: *before trusting a new instrument, construct the input on which
it must report the answer you do not want.* The raw-syntax control was the new instrument, so it
went first — and it failed, **6 of 6**. `ast.parse` merges redundant parentheses, whitespace,
comments, numeric literal spelling (`1000` / `1_000`), radix (`0x10` / `16`) and string quoting.

> **There is no raw. Every keyer is a preprocessing map.**

So the assigned question — *what fraction of the invariance is the circuit's?* — was
unanswerable as posed, because it would have been computed against a floor quietly doing work of
its own. The right output is an **attribution across layers**. Three cycles running, an instrument
has shipped blind in the direction it was pointed; this is the first time the habit caught it
before the measurement rather than after.

## The layer ladder

```
L0  source text     no normalisation — the only true floor
L1  Python ast      lexical: parens, whitespace, comments, literal spelling, radix
L2  sympy srepr     algebraic: commutativity, associativity, folding, powers, cancellation
L3  circuit key     whatever the circuit adds on top of L2
```

Attribution over a 15-pair battery: **L1 = 4, L2 = 7, L3 = 3, never = 1.** Lexical invariance is
the parser's, algebraic invariance is sympy's, variable renaming is the circuit layer's. The one
distinction nothing erases is `x*(y+1)` vs `x*y+x` — equal as functions, distinct at every layer.

**One expectation of mine was wrong and is recorded rather than corrected away:** I predicted
`x+y` vs `x+z` would never merge. They merge at L3, and *correctly* — they are alpha-equivalent,
so a renaming quotient should identify them. The battery's prediction was wrong, not the circuit.

## The consequence, per rung — and it is narrower than the question assumed

**R0 contributes zero invariance of its own.** Its keyer `ast_key` *is* `sympy.srepr`; its
projection is precisely L2. Measured: trained on `x+y` it retrieves `y+x` (sympy's doing) and
abstains on `a+b`.

The rung consequence stated exactly: canon R0 is exact recall that **abstains** on isomorphs.
With sympy's key it does not abstain on algebraic isomorphs — it retrieves them. So R0-with-sympy
sits slightly *above* its rung, and the excess is entirely borrowed.

**But R0's kill test still stands, and that is not luck I should claim as design.** Renaming is
the one isomorphism sympy does not collapse, and renaming is exactly what the fresh-seed test
uses. The test was aimed at the right axis. What is wrong is the *docstring* — "identity
congruence" should read "sympy normal form".

**R1 and R2 are not in R0's position.** `2*x+4` and `3*x+6` have different sympy keys and the
same R1 answer, so that identification is the rule's. R2 likewise: scaling a rational leaves its
root fixed, and sympy does not know that. Both perform genuine many-to-one work the CAS does not.

## So the thread closes rather than escalating

HITL #124 asked whether the ladder's bottom rungs measure a normaliser rather than reasoning.
**R0 does. R1 and R2 do not.** No rebuild on raw syntax is called for — there is no raw syntax.
What is called for is *declaring each rung's congruence* instead of advertising one it does not
implement, and that is a one-line docstring correction plus a standing audit, not a substrate
crisis.

I want to be careful not to undersell it either: R0 is the ladder's floor, and its floor is
borrowed. Anything that reasons *from* R0's congruence inherits sympy's choices without a record
of having done so. The audit is now executable and should run whenever a rung's congruence is
claimed.

## TLDR — ELI5

Last cycle's finding was that our simplest circuit doesn't really tell expressions apart by
structure — the maths library tidies them up first. The plan was to build a "raw" comparison that
skips the tidying, and see how much the circuit was really doing.

The first thing I did was try to break my own raw comparison, and it broke instantly. Python's
parser tidies too — it throws away spacing, comments, extra brackets, and whether you wrote a
number as 16 or 0x10. There is no untidied version. So the question "how much is the circuit
doing" has no answer; the honest question is "which tidying happens at which stage", and now
every one is labelled with where it came from.

The result: the bottom circuit adds nothing of its own — the library does all of it. The two
circuits above it genuinely do their own work: they know that 2x+4 and 3x+6 have the same answer,
and the library doesn't. So this is a real problem with exactly one rung, not a rot through the
whole ladder — and the test we use to check that rung happens to probe the one thing the library
leaves alone, so the old result survives. The description was wrong, not the experiment.

## For ChatGPT

```
Prometheus loop, cycle 034. HITL #124: does the sympy preprocessing finding reach far enough that
the ladder's bottom rungs measure a normaliser rather than reasoning? 395 green, READ-ONLY.

FIRST, THE DISCIPLINE CHANGED THE QUESTION. I adopted "before trusting a new instrument,
construct the input on which it must report the answer you do not want". The raw-syntax control
was the new instrument, so it went first — and failed 6/6. ast.parse merges parentheses,
whitespace, comments, numeric literal spelling (1000 / 1_000), radix (0x10 / 16), string quoting.
THERE IS NO RAW. Every keyer is a preprocessing map. So "what fraction of the invariance is the
circuit's" is unanswerable as posed — it would be computed against a floor quietly doing work.
The right output is an ATTRIBUTION ACROSS LAYERS. Third cycle running an instrument shipped blind
in the direction it was pointed; first time the habit caught it BEFORE the measurement.

THE LADDER: L0 source / L1 python-ast (lexical) / L2 sympy-srepr (algebraic) / L3 circuit key.
Attribution over 15 pairs: L1 = 4, L2 = 7, L3 = 3, never = 1. The only distinction nothing erases
is x*(y+1) vs x*y+x. One of my own predictions was wrong and is recorded: I said x+y vs x+z would
never merge; they merge at L3 and correctly, since they are alpha-equivalent.

THE CONSEQUENCE IS NARROWER THAN THE QUESTION ASSUMED:
* R0 contributes ZERO invariance of its own. ast_key IS sympy.srepr; its projection is exactly
  L2. Trained on x+y it retrieves y+x (sympy) and abstains on a+b. Canon R0 is exact recall that
  ABSTAINS on isomorphs; with sympy's key it does not abstain on algebraic isomorphs, so it sits
  slightly ABOVE its rung on borrowed strength.
* R0's KILL TEST still stands: renaming is the one isomorphism sympy does not collapse, and
  renaming is exactly what the fresh-seed test uses. The docstring is what is wrong — "identity
  congruence" should read "sympy normal form".
* R1 and R2 DO contribute. 2*x+4 and 3*x+6 have different sympy keys and the same R1 answer;
  scaling a rational leaves its root fixed and sympy does not know that. Genuine many-to-one work.

So the thread closes narrowly: one rung, not the ladder. No rebuild on raw syntax is called for —
there is no raw syntax. What is called for is declaring each rung's congruence rather than
advertising one it does not implement.

What I want attacked:
1. Am I letting R0 off too lightly? "The kill test happens to probe the one axis sympy leaves
   alone" is a fact about renaming, not evidence that the rung was designed well. An alternative
   read is that R0 has no congruence of its own AT ALL, so it is not a circuit in any meaningful
   sense — it is a dictionary keyed by sympy's normal form, and the rung is vacuous rather than
   merely mislabelled.
2. Does the layered attribution generalise past keyers? Every rung in this ladder consumes some
   library. The same accounting should apply to anything with a preprocessing stage — a tokeniser,
   a parser, a canonicaliser — but I have only demonstrated it where the layers are cleanly
   separable functions. Where preprocessing is entangled with the computation I do not know how
   to attribute at all.
3. Three cycles of instruments shipping blind. The habit caught it before the measurement this
   time, which is progress, but the habit is mine and unenforced. Is there a way to make "test
   the instrument against its unwanted answer" structural rather than remembered — something a
   test suite can require of any new measurement module?
```

## Traps ledger additions

- **A "raw" baseline that normalises** — `ast.parse` merges six kinds of source-level difference.
  Defence, APPLIED FIRST: construct the inputs the control must merge if it is a normaliser, and
  check before using it for any comparison.
- **Fraction-of-invariance framing** — unanswerable when the baseline is itself a layer. Defence:
  attribute each invariance to the layer that first delivers it.
- **A congruence advertised but not implemented** — R0's docstring claims an identity congruence
  and its key is sympy's normal form. Defence: the layered audit, run whenever a rung's
  congruence is claimed.
