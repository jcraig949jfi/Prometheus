# Cycle 057 — the domain boundary is real, and it is not where I said it was

Prereg `61284fbe`, committed before building the battery.

## 1. A correction to cycle 056, which I posted to James

I claimed of `theseus::dedup_rate`: *"no executable probe could ever see it, because no input
makes it behave differently."* **That was too strong.**

```
s2_defective([])                    = 1.0
s2_defective([dup, dup])            = 1.0     <- SHOULD be 0.5
```

A probe compared against an input that **should score badly** — rather than one that is merely
"legitimate" — catches it immediately. My cycle-055 probe compared *degenerate vs
legitimate-negative*, and under that pairing S2 is invisible. **The invisibility was a property
of my probe design, not of the defect.** Prediction 1 was `high` confidence, tagged `D0`
near-tautological, and it is **falsified** — the tautology was mine, not the mechanism's.

`dedup_rate` is still a real defect and still worth Theseus's attention. What is retracted is
the claim that probing *cannot* reach it.

## 2. The boundary that IS real: probes cannot generate their own specification

The battery scores:

```
shape                        Lane B      truth     why
S1 empty-conflation           FLAG       DEFECT    comparison suffices
S2 unconditional-constant     FLAG       DEFECT    needs a SHOULD-DIFFER pairing
S3 doc-behaviour gap          FLAG       DEFECT    (see below)
S4 condition-number          CLEAN       DEFECT    MISSED -- needs an oracle
S5 silent-NaN                 FLAG       DEFECT    nan is self-announcing
```

**S3 is the sharp case.** `s3_defective` computes the *mean* while its docstring says *median*.
A probe with an oracle catches it instantly:

```
s3_defective([1.0, 2.0, 90.0]) = 31.0    true median = 2.0
```

**But the oracle came from reading the docstring.** The specification is in prose; no amount of
executing the function recovers it. So the boundary is not "reading sees things probes cannot" —
it is:

> **A probe can check any specification it is given, and cannot generate one. Where the
> specification exists only in prose, reading is the only lane that can supply it.**

That is a division of labour, not a ranking — which is what "different domains" should have
meant, and my A-vs-B framing across cycles 055–056 was asking the wrong question. **Kill test
did not fire** (S4 was missed by Lane B), so the domain hypothesis survives, but in a corrected
form I did not predict.

## 3. Lane B's two false positives were both MY errors — and one repeats cycle 055's

```
LANE B: detected 4/5 defects, missed 1, FALSE POSITIVES 2/5 clean
```

Neither false positive is a property of probing.

**`s3_clean` — I authored a "clean" counterpart that carries a different defect.** It fixes the
median/mean gap and still returns `0.0` on empty input, which is the S1 conflation. **This is
exactly cycle 055's invalid-control error, committed again, inside the battery built to fix
it.** Second instance, and I did not notice until the probe flagged it.

**`s4_clean` — my case selection was degenerate.** `s4_clean(1e8+1, 1e8) = 1.0` and
`s4_clean(2, 1) = 1.0`: both true answers are 1.0, so "indistinguishable" is correct and
meaningless. The probe was right; the question was empty.

**So the false-positive rate cycle 055 could not establish is still not established.** What this
cycle measured is that **2 of 5 "clean" controls I authored were not clean** — which says more
about control construction than about either lane.

## 4. The difficulty scale, adopted

Replacing binary `PRIOR`/`OPEN`, whose flaw was that two five-for-five sweeps (053, 056) read
identically to hard calls:

- **`D0 DEDUCED`** — follows from an established mechanism; being wrong means the mechanism is.
- **`D1 EXPECTED`** — open, but one outcome is clearly more plausible.
- **`D2 GENUINE`** — I would not bet either way.
- **`D3 CONTRARIAN`** — I predict against the obvious reading.

**Its first use caught something binary tagging could not.** Prediction 1 was `D0` — and a `D0`
failure is the most informative kind, because it falsifies the *mechanism*, not the guess. Under
`PRIOR`/`OPEN` that prediction would have been an ordinary miss.

## 5. Predictions — 3 of 5

- **P1 `high` `D0` — S2 invisible to Lane B: FALSIFIED.** The most useful result in the cycle.
- **P2 `moderate` `D1` — S4 invisible to Lane A, visible to Lane B: PARTIAL/FALSIFIED.** Lane B
  **missed** S4 under comparison; it needs an oracle. Scored FALSIFIED as stated.
- **P3 `high` `D0` — at least one shape visible to both: HELD** (S1, S5).
- **P4 `low-to-moderate` `D2` — at least one shape invisible to both: FALSIFIED.** Every shape is
  reachable by some lane. **The two lanes together are complete over this taxonomy**, which the
  prereg named as the stronger outcome.
- **P5 `moderate` `D1` — no clean counterpart flagged: FALSIFIED**, 2 of 5 — both my errors.

Two `D0` predictions, one held and one falsified. **The falsified one is worth more than the
whole rest of the cycle**, because it corrects a claim I had already escalated.

## TLDR — ELI5

**I told James last cycle that a certain bug was impossible for automated testing to find. I was
wrong, and the reason is instructive.**

The bug: a function that reports "no duplicates found" no matter what you give it. I said no
test could catch that, since every input produces the same answer. But that's only true if you
compare it against *another* input you also expect to be fine. Feed it a batch that is **nothing
but duplicates** — where the right answer is obviously not "all unique" — and it fails instantly.
The blindness was in *my test design*, not in testing.

**What is genuinely different between reading and testing** turns out to be narrower and more
interesting. I built a function whose comment says "returns the median" and whose code computes
the average. A test catches that in one shot — *if* you tell it the answer should be the median.
But that instruction is only written in the comment. **A test can check any rule you give it; it
cannot read the rule off the page.** That's the real division: not one method being sharper, but
one of them being the only way to turn prose into a checkable rule.

**And I made the same mistake twice.** Last cycle my "known-good" control turned out to have the
defect I was hunting. So this cycle I built a fresh set of clean-and-defective pairs — and two of
my five "clean" ones weren't clean either. One still had the old bug in it. I only found out
because the automated check flagged them and I went to see why.

## For ChatGPT

```
Prometheus loop, cycle 057. THE DOMAIN BOUNDARY IS REAL AND NOT WHERE I SAID IT WAS.

*** A CORRECTION TO CYCLE 056, WHICH I ALREADY ESCALATED ***
I claimed of theseus::dedup_rate: "no executable probe could EVER see it, because no input makes
it behave differently." TOO STRONG.
  s2_defective([])         = 1.0
  s2_defective([dup, dup]) = 1.0    <- SHOULD be 0.5
A probe compared against an input that SHOULD SCORE BADLY -- not one merely "legitimate" --
catches it instantly. My cycle-055 probe paired degenerate vs legitimate-negative, and under
THAT pairing S2 is invisible. THE INVISIBILITY WAS A PROPERTY OF MY PROBE DESIGN, NOT THE
DEFECT. Prediction 1 was HIGH confidence, tagged D0 near-tautological, and is FALSIFIED. The
tautology was mine.

*** THE BOUNDARY THAT IS REAL ***
Battery of 5 authored shapes, ground truth by construction:
  S1 empty-conflation        Lane B FLAG   comparison suffices
  S2 unconditional-constant  Lane B FLAG   needs a SHOULD-DIFFER pairing
  S3 doc-behaviour gap       Lane B FLAG   but see below
  S4 condition-number        Lane B CLEAN  MISSED -- needs an oracle
  S5 silent-nan              Lane B FLAG   nan is self-announcing
S3 IS THE SHARP CASE: s3_defective computes the MEAN while its docstring says MEDIAN. An oracle
probe catches it instantly (s3_defective([1,2,90]) = 31.0, true median 2.0) -- BUT THE ORACLE
CAME FROM READING THE DOCSTRING. The specification is in prose; no amount of executing recovers
it. So the boundary is NOT "reading sees what probes cannot". It is:
  A PROBE CAN CHECK ANY SPECIFICATION IT IS GIVEN, AND CANNOT GENERATE ONE. WHERE THE SPEC
  EXISTS ONLY IN PROSE, READING IS THE ONLY LANE THAT CAN SUPPLY IT.
Division of labour, not a ranking. My A-vs-B framing across 055-056 asked the wrong question.

*** LANE B'S TWO FALSE POSITIVES WERE BOTH MY ERRORS -- AND ONE REPEATS CYCLE 055 ***
detected 4/5, missed 1, FALSE POSITIVES 2/5 clean.
s3_clean: I AUTHORED A "CLEAN" COUNTERPART THAT CARRIES A DIFFERENT DEFECT -- it fixes the
median/mean gap and still returns 0.0 on empty, which is the S1 conflation. EXACTLY CYCLE 055'S
INVALID-CONTROL ERROR, COMMITTED AGAIN, INSIDE THE BATTERY BUILT TO FIX IT. Second instance.
s4_clean: my case selection was degenerate -- s4_clean(1e8+1,1e8) = 1.0 and s4_clean(2,1) = 1.0,
both true answers 1.0, so "indistinguishable" is correct and meaningless.
SO THE FALSE-POSITIVE RATE IS STILL NOT ESTABLISHED. What I measured is that 2 of 5 controls I
authored were not clean.

*** DIFFICULTY SCALE ADOPTED ***
D0 DEDUCED / D1 EXPECTED / D2 GENUINE / D3 CONTRARIAN, replacing binary PRIOR/OPEN. FIRST USE
CAUGHT SOMETHING THE BINARY TAG COULD NOT: prediction 1 was D0, and a D0 FAILURE IS THE MOST
INFORMATIVE KIND because it falsifies the MECHANISM, not the guess. Under PRIOR/OPEN it would
have been an ordinary miss.

PREDICTIONS 3 OF 5. P1 D0 FALSIFIED (most useful result). P2 FALSIFIED as stated -- Lane B
missed S4 under comparison, needs an oracle. P3 HELD. P4 FALSIFIED: EVERY shape is reachable by
some lane, so THE TWO LANES TOGETHER ARE COMPLETE over this taxonomy -- the prereg named that as
the stronger outcome. P5 FALSIFIED, 2/5, both mine.

What I want attacked:
1. "A probe cannot generate its own specification" -- is that a real boundary, or does it
   dissolve once you count property-based testing (which generates specs from invariants)?
2. Twice now I have built a control that carries the defect under study. Is there a
   constructive way to certify a control clean, or is it turtles down?
3. My taxonomy has five shapes chosen by me from defects I already found. What shape would I
   be structurally unable to think of, and how would I know?
```

## Traps ledger additions

- **A negative control that carries a different defect from the one it controls for.**
  `s3_clean` fixed the doc gap and kept the empty-conflation. Defence: a control must be checked
  against **every** shape in the taxonomy, not only the one it was built to exclude.
- **A comparison whose two arms have the same true answer.** `s4_clean(1e8+1,1e8)` and
  `s4_clean(2,1)` are both 1.0, so "indistinguishable" carried no information. Defence: before
  reading a comparison, verify the arms **should** differ.
- **Claiming a method cannot detect something, from one probe design.** "No probe could ever see
  `dedup_rate`" was true of *degenerate-vs-legitimate* pairing and false in general. Defence:
  an impossibility claim about a method needs the **method**, not one instance of it.
- **A `D0` prediction is a mechanism claim.** When one fails, the mechanism is wrong — which is
  worth more than several `D1` hits. Defence: report `D0` failures at the top of a cycle, not
  in the score line.
