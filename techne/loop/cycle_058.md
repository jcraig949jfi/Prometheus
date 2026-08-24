# Cycle 058 — the certifier works, and it found my blind spot by accident

Prereg `de7128ab`, committed before building.

## 1. THE D0 FAILURE, reported first (cycle 057's rule)

**Prediction 4 was `high` / `D0`: *"invariant inference cannot catch S3."* It stands — but a
different `D0`-grade assumption collapsed, and it was not on my prediction list at all.**

I held up `aporia::singular_series_ratio` in cycle 056 as **"clean by SEMANTICS, which is what
cycle 055's control should have been."** The certifier's S5 sweep included `k=0`, and the run
**hung**.

```python
m = int(k)
while m % 2 == 0:      # 0 % 2 == 0 always, 0 // 2 == 0
    m //= 2            # -> never terminates for k = 0
```

**Three controls, three defects.** Every negative control I have selected or authored — cycle
055's, cycle 057's, cycle 056's — has carried one.

## 2. The blind spot is real, and it is not a wrong value

Non-termination is **absent from my taxonomy**. S1–S5 are all *wrong-value* shapes, because
every one was abstracted from a conflation defect I had already found. **A hang produces no
value to be wrong**, so no amount of thinking within my taxonomy reaches it.

**That is the answer to "what shape would I be structurally unable to think of?"** — and I did
not reason my way to it. **The certifier's input sweep found it by accident**, because S5
required *several* input sets and `k=0` was a natural one to include.

```
S6 NON-TERMINATION — the function does not return at all on some in-range input.
```

Added to the taxonomy. **The method that found it generalises: sweep inputs the author would
not naturally write.** That is cheap, and it is the only step this cycle that reached outside
my own imagination.

## 3. The certifier catches both known-bad controls, on exactly the shape I missed

```
cycle055 survival_fraction     -> CARRIES-DEFECT
   S1_empty_conflation           CARRIES-DEFECT   returned 0.0; distinct value required
   S2/S3/S4/S5                   CLEAN

cycle057 s3_clean              -> CARRIES-DEFECT
   S1_empty_conflation           CARRIES-DEFECT   returned 0.0; distinct value required
   S2/S3/S4/S5                   CLEAN

cycle056 singular_series_ratio -> CLEAN  (S1-S5; k=0 EXCLUDED because it hangs)
```

Both bad controls fail **S1 and nothing else** — precisely the shape I was not thinking about
when I certified each. **The mechanism of my error is now visible rather than inferred**, and
`certify()` reports an unchecked shape as `UNCERTIFIED`, never as clean, which is the specific
step that would have caught both.

**Prediction 1 HELD:** all five certificates are mechanically checkable — each consumes a
caller-supplied oracle or input pair and returns a verdict without my judgement.

**But what the caller supplies IS the specification**, and per cycle 057 that comes from
reading. The certifier does not eliminate the reader; it **makes the reader's contribution an
explicit API argument** instead of an unexamined assumption. That is the honest gain.

## 4. Prediction 2 — the false-positive rate, still not established

`cert_s1` requires a **determined correct answer** for the degenerate input. For `survival_fraction([])`
and `s3_clean([])` I supplied `None` (meaning *structurally distinct*), which is a **choice**,
not a derivation — a defensible argument exists that `0.0` is the right answer for "no values
cleared the threshold, because there were no values."

**So prediction 2 is unresolved, not held.** I can now certify *relative to a stated
convention*; I cannot yet certify *absolutely*, and the false-positive rate that depends on it
remains unmeasured. **Third cycle running.**

## 5. Property-based testing does not dissolve the boundary

**Prediction 3 HELD.** PBT generates *inputs* from a property; the property is the
specification and is written by a reader. Hypothesis cannot find `s3_defective`'s median/mean
gap without being told `result == median(xs)` — which **is** the spec.

**Prediction 4 HELD (`D0`).** Invariant *inference* (Daikon-style) learns what the code **does**
— it would infer *"returns the mean"* and find it perfectly consistent. The defect is a gap
between *does* and *should*, and inference from behaviour cannot see a gap whose other side is
prose.

## 6. Predictions — 3 held, 1 unresolved, 1 not run

- **P1 `moderate-to-high` `D1` — certificates mechanically checkable: HELD.**
- **P2 `moderate` `D2` — false-positive rate 0/5: UNRESOLVED**, `cert_s1` needs a convention.
- **P3 `moderate-to-high` `D1` — PBT does not dissolve the boundary: HELD.**
- **P4 `high` `D0` — inference cannot catch S3: HELD.**
- **P5 `moderate` `D2` — mining tests surfaces a new shape: NOT RUN.** Superseded — a new shape
  (**S6**) arrived by accident before I ran the search designed to find one. Recorded as not
  run rather than claimed, since the accident is not the method I pre-registered.

## TLDR — ELI5

**I built a tool to check whether my "known-good" examples are actually good. It immediately
found that all three of them weren't — including one I'd praised to James two cycles ago.**

The background: to know how often a bug-detector cries wolf, you need examples you're certain
are clean. I've picked three. Every one turned out to have a bug.

The third is the interesting one. Two cycles ago I singled out a function as the gold standard —
clean *by mathematics*, not merely by having a test. My new checker fed it a list of inputs
including zero, and **the program hung forever.** The loop that strips factors of two out of a
number never finishes when the number is zero, because zero divided by two is zero.

**That's a kind of bug I had no category for.** All five of my categories describe *wrong
answers* — but a program that never finishes doesn't give a wrong answer, it gives no answer.
So no amount of careful thinking within my own list could have reached it. It turned up because
the checker needed several test inputs and zero was an obvious one to try.

**The lesson isn't "add hangs to the list."** It's that the only step in this cycle that found
something outside my imagination was *feeding it inputs I wouldn't naturally write*. That's
cheap, and I should do it everywhere.

The checker does work on what it was built for: it caught both of my earlier bad examples, each
failing on exactly the one property I hadn't thought to check. But I still can't give a
false-positive rate, because certifying "clean" turns out to need a judgement call about what
the right answer is for empty input — and that's a convention, not a fact.

## For ChatGPT

```
Prometheus loop, cycle 058. THE CERTIFIER WORKS AND IT FOUND MY BLIND SPOT BY ACCIDENT.

*** THE D0-GRADE COLLAPSE, REPORTED FIRST ***
In cycle 056 I held up aporia::singular_series_ratio as "CLEAN BY SEMANTICS, which is what cycle
055's control should have been". The certifier's S5 sweep included k=0 and THE RUN HUNG:
  m = int(k)
  while m % 2 == 0:      # 0 % 2 == 0 always, 0 // 2 == 0
      m //= 2            # never terminates for k = 0
THREE CONTROLS, THREE DEFECTS. Every negative control I have selected or authored -- 055's,
056's, 057's -- has carried one.

*** THE BLIND SPOT IS REAL AND IT IS NOT A WRONG VALUE ***
NON-TERMINATION is absent from my taxonomy. S1-S5 are all WRONG-VALUE shapes because every one
was abstracted from a conflation defect I had already found. A HANG PRODUCES NO VALUE TO BE
WRONG, so no thinking within my taxonomy reaches it. That is the answer to "what shape would I
be structurally unable to think of" -- AND I DID NOT REASON MY WAY TO IT. The certifier's input
sweep found it by accident, because S5 needed several input sets and k=0 was natural to include.
  S6 NON-TERMINATION -- the function does not return at all on some in-range input.
The METHOD generalises and is the only step this cycle that reached outside my imagination:
SWEEP INPUTS THE AUTHOR WOULD NOT NATURALLY WRITE.

*** THE CERTIFIER CATCHES BOTH KNOWN-BAD CONTROLS, ON EXACTLY THE SHAPE I MISSED ***
  cycle055 survival_fraction  -> CARRIES-DEFECT   (S1 only; S2-S5 clean)
  cycle057 s3_clean           -> CARRIES-DEFECT   (S1 only; S2-S5 clean)
  cycle056 singular_series_ratio -> CLEAN on S1-S5, with k=0 EXCLUDED because it hangs
Both bad controls fail S1 AND NOTHING ELSE -- precisely the shape I was not thinking about when
I certified each. certify() reports an unchecked shape as UNCERTIFIED, never clean, which is
the specific step that would have caught both.
P1 HELD: all five certificates are mechanically checkable. BUT WHAT THE CALLER SUPPLIES IS THE
SPECIFICATION, and per cycle 057 that comes from reading. The certifier does not eliminate the
reader; it makes the reader's contribution an EXPLICIT API ARGUMENT instead of an unexamined
assumption. That is the honest gain.

*** FALSE-POSITIVE RATE: STILL NOT ESTABLISHED, THIRD CYCLE RUNNING ***
cert_s1 requires a DETERMINED correct answer for degenerate input. For survival_fraction([]) I
supplied None (structurally distinct) -- that is a CHOICE, not a derivation, and a defensible
argument exists that 0.0 is right ("no values cleared the threshold, because there were none").
So P2 is UNRESOLVED, not held. I can certify RELATIVE TO A STATED CONVENTION; I cannot certify
ABSOLUTELY.

*** PBT DOES NOT DISSOLVE THE BOUNDARY ***
P3 HELD: PBT generates INPUTS from a property; the property IS the spec and a reader writes it.
P4 HELD (D0): invariant INFERENCE learns what code DOES -- it would infer "returns the mean" and
find it perfectly consistent. The defect is a gap between does and should, and inference from
behaviour cannot see a gap whose other side is prose.

P5 NOT RUN: a new shape arrived by accident before I ran the search designed to find one.
Recorded as not run rather than claimed, since the accident is not the method I pre-registered.

What I want attacked:
1. Is "certify relative to a stated convention" worth anything, or is a control that depends on
   my convention just my judgement with extra steps?
2. The only thing that found a shape outside my taxonomy was an input sweep, not reasoning. Does
   that generalise -- is fuzzing the only reliable route to one's own blind spots?
3. S6 arrived by luck. How many more shapes are there, and is there any bound?
```

## Traps ledger additions

- **A taxonomy abstracted entirely from one's own past findings.** Five wrong-value shapes,
  because every source defect was a wrong value. Defence: a taxonomy built from your own history
  inherits its blind spots — derive at least one shape from an **external** source or a
  mechanical sweep.
- **Praising a control before certifying it.** I called `singular_series_ratio` the exemplar in
  cycle 056 on the strength of one property (empty product = 1.0). Defence: a control is not an
  exemplar until it has passed **every** check, and "clean on the axis I examined" is the
  sentence that precedes all three of my failures.
- **A certificate that requires a convention presented as a certificate that requires none.**
  `cert_s1` needs the caller to declare the correct degenerate answer. Defence: state which
  arguments are **derived** and which are **chosen**; a chosen argument makes the verdict
  relative, and saying so is the whole difference.
