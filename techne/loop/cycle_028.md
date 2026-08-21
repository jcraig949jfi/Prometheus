# Cycle 028 — 2026-08-21 — the sample-size objection removed, and it was the wrong objection

**Read-only audit of `prometheus_math.discovery_pipeline`'s kill path.** 339 green.

## ⚠️ HITL #78 — 446 rows now

330 when found (cycle 025) → 369 (026) → 400 (027) → **446, 0 accepted, 100% drop**. The campaign
keeps writing and `load_prepass` keeps discarding everything. Still unruled, still unpatched by me.

## The instruction, and what actually settled it

The instruction was to widen the sample and remove the sample-size objection to cycle 027's
finding that F9 and F11 contribute 0.0000 bits. I did widen it — **n = 81** against 34, degrees
2–8, coefficients to ±5, **37 reciprocal and 44 non-reciprocal**, M spanning 1.0000 to 9.6071
rather than one narrow band. Both stay at exactly **0.0000**.

But reading the source settled it harder than any amount of sampling could, and the two zeros
turn out to have **completely different causes**. "Measure more samples" was the wrong instinct;
the objection was answerable from the code.

### F9 — the zero is structural. No sample can move it.

`_f9_simpler_explanation` is `return True, "F9: M > 1.001 rules out cyclotomic"` with **no
computation on `coeffs` at all**. It returns True for the empty list. No candidate set, at any
size, can make it fire.

Its own docstring is honest about this — the band gate upstream already excludes cyclotomic, and
the check exists *"for post-rejection record-keeping"*. **F9 is not pretending to be a filter.
It is simply counted as one.**

### F11 — vacuous by a theorem, and the surviving branch tests the caller

F11's docstring says it re-computes M *"via two independent paths"*. The second path is
`M(reversed(coeffs))`. But reversal maps every root α to 1/α while swapping the leading and
trailing coefficient, leaving `|a|·∏max(1,|α|)` unchanged — so

```
M(p) = M(reverse(p))   for EVERY polynomial, reciprocal or not
```

The two paths compute the same number by a theorem. Verified on 40 random **non-reciprocal**
integer polynomials, where the reversal genuinely is a different polynomial: **zero
disagreements.**

F11 is not inert. Its third comparison — against the caller's *reported* M — fires correctly
(measured: consistent M passes, drifted M fails). But no property of a polynomial can trigger it;
only an inconsistent `m_value` handed in from outside. **As a discriminator over candidates it
contributes zero by construction, while remaining a real assertion about bookkeeping.**

## Measured battery strength

```
F1   0.9599 bits      fires 31/81
F6   0.2285 bits      fires  3/81
F9   0.0000 bits      structurally constant
F11  0.0000 bits      vacuous over candidates; fires only on caller error

battery of 4 advertised, 2 discriminating over 81 candidates
```

Note F6 dropped from 0.9082 bits (cycle 027, narrow band) to 0.2285 here. A base-rate check is
sensitive to the candidate distribution, which is worth knowing separately: the battery's
strength is not a constant of the battery, it is a function of what you feed it.

**The fair statement, and I want to be careful here.** Neither F9 nor F11 is fraudulent. One is
an explicit record-keeper, the other a caller-consistency assertion, and both are correctly
placed for what they do. What is wrong is the *count*: quoting the kill path as a four-member
battery overstates it. Every claim that "survived the four-member battery" survived a two-member
discriminating test.

## Track 1 — `prometheus_math.battery`

`member_resolution` and `battery_strength`, separating a battery's **advertised** size from its
measured **discriminating** size. Four-category TDD, including a composition test that chains
into this cycle's live audit and asserts 4 advertised / 2 discriminating with F9 and F11 silent.

Two things it deliberately refuses. It does not call a silent member useless — a check guarding a
rare failure mode has zero resolution until the rare failure arrives, which is correct behaviour,
so `n_candidates` is part of every result. And it does not distinguish *cannot fire* from *has
not fired*; that distinction is structural rather than statistical and needs the member's source,
not more samples. Cycle 028 found both kinds in one battery, which is exactly why the module
declines to guess.

`total_bits` is documented as an upper bound rather than joint power — two members with identical
verdicts each measure 1 bit and jointly carry 1, and a test pins that.

## TLDR — ELI5

Last cycle I found that two of the discovery pipeline's four safety checks gave the same answer
to every candidate, and I noted honestly that I'd only tried 34 candidates. The instruction was
to try more. I tried 81, much more varied — same result, exactly zero.

Then I read the code, which settled it properly and showed the two cases aren't the same thing at
all. One check is literally `return True` — it does no work on its input, and returns True even
for an empty polynomial. It can never fire, ever. Its own comment says it's there for
record-keeping, so it isn't lying; it's just being counted as a safety check.

The other is subtler and more interesting. It claims to verify a number "by two independent
paths", and computes the second one by reversing the polynomial's coefficients. But there's a
theorem: reversing the coefficients doesn't change that number. Ever. So the "independent" check
is the same computation wearing a hat. The one part of it that can actually fail catches
*bookkeeping* mistakes by whoever called it — real, but nothing to do with whether the candidate
is any good.

So: four checks advertised, two that can tell candidates apart. Nobody is cheating; the count is
just wrong, and anything that "passed all four" passed two.

## For ChatGPT

```
Prometheus loop, cycle 028. Instruction was to widen the sample and remove the sample-size
objection to my cycle-027 finding (F9 and F11 contributing 0.0000 bits to the discovery
pipeline's kill path). 339 green. READ-ONLY throughout.

I did widen it: n = 81 vs 34, degrees 2-8, coefficients to +-5, 37 reciprocal and 44
NON-reciprocal, M spanning 1.0000 to 9.6071 rather than one narrow band. F9 and F11 stay at
exactly 0.0000.

BUT READING THE SOURCE SETTLED IT HARDER, and the two zeros have completely different causes.
"Measure more samples" was the wrong instinct — the objection was answerable from the code.

F9: _f9_simpler_explanation is `return True, "..."` with NO computation on coeffs at all. It
returns True for the empty list. No candidate set at any size can make it fire — the zero is a
property of the function. Its docstring is honest: the band gate upstream already excludes
cyclotomic and the check exists "for post-rejection record-keeping". It is not pretending to be
a filter; it is counted as one.

F11: its docstring says it recomputes M "via two independent paths". The second path is
M(reversed(coeffs)). But reversal maps each root alpha to 1/alpha and swaps leading/trailing
coefficient, leaving |a|*prod max(1,|alpha|) unchanged — so M(p) = M(reverse(p)) for EVERY
polynomial. The two paths compute the same number by a theorem. Verified on 40 random
non-reciprocal polys where the reversal really is a different polynomial: zero disagreements.
F11's surviving branch (vs the caller's REPORTED M) does fire correctly on drifted input — but
no property of a polynomial can trigger it, only caller error. As a discriminator over
candidates it is zero by construction while remaining a real bookkeeping assertion.

MEASURED: F1 0.9599 bits, F6 0.2285, F9 0.0000, F11 0.0000. Battery of 4 advertised, 2
discriminating over 81 candidates. Also: F6 fell from 0.9082 (narrow band) to 0.2285 (wide), so
a battery's strength is not a constant of the battery but a function of what you feed it.

Fair statement: neither check is fraudulent. One is an explicit record-keeper, one a
caller-consistency assertion, both correctly placed. What is wrong is the COUNT — anything that
"survived the four-member battery" survived a two-member discriminating test.

Track 1: prometheus_math.battery, separating advertised from discriminating size. It refuses to
call a silent member useless (a rare-failure guard has zero resolution until the failure comes)
and refuses to distinguish CANNOT-fire from HAS-NOT-fired, because that is structural not
statistical — cycle 028 found both kinds in one battery.

What I want attacked:
1. The general lesson I am drawing is "when a measurement reads zero, read the source before
   collecting more data" — a structural zero and a sampling zero look identical and only one is
   fixable by sampling. That matches a standing rule of ours (a structural zero needs its own
   pre-committed vacuous reading). Is there a way to make that a CHECK rather than a habit? The
   only mechanical version I can think of is mutation testing: perturb the member's input space
   and see whether ANY input flips it, which is what I did by hand for F9.
2. Am I being too generous in "neither is fraudulent"? An alternative read is that F11's
   docstring makes a false claim — "two independent paths" is not true, and a reader auditing
   the battery would believe it. That is a documentation defect with epistemic consequences,
   which our own doctrine treats as seriously as a code defect.
3. F6 moving 0.908 -> 0.229 with the candidate distribution bothers me more than the zeros. A
   battery whose measured strength depends on the input distribution cannot be quoted as a
   fixed property at all, and every "survived the battery" claim is implicitly relative to the
   distribution it was tested on. Is there a standard way to report that, or does it collapse
   into the reference-class problem from R11?
```

## Traps ledger additions

- **Structural zero mistaken for a sampling zero** — a member that CANNOT fire and one that has
  NOT fired both read 0.000 bits. Defence: read the source, or mutate the input space and check
  whether any input flips the member. More samples cannot distinguish them.
- **"Independent" verification that is the same computation** — F11 recomputes M by reversing
  coefficients, which is invariant by a theorem. Defence: verify the second path can DISAGREE on
  some input before calling it independent.
- **Battery strength quoted as a constant** — F6 measured 0.908 bits on a narrow band and 0.229
  on a wide one. Defence: report strength with the candidate distribution it was measured on;
  it is not a property of the battery alone.
