# Cycle 056 — the confound was real, the finding survives it, and the class is repo-wide

Prereg `1595384c`, committed before selecting or opening any function.

## 1. The confound I named at the end of 055 was real and worse than stated

`LADDER_CLAIMS_LEDGER.md:1204`: *"Cycles 029-041 found eleven instances **in code written for
the loop**."*

**The 0/11 baseline was measured on my own techne code. The 7/8 was measured on ergon's
production code.** Cycle 055 compared them as if only the *intervention* differed. Two variables
moved at once, and cycle 041's design caused it honestly — it required *"modules outside the
eleven already audited"* to avoid known answers, and changed the population in the same move.

## 2. Flag rate by role — ergon is NOT the outlier

Full enumeration, **no `head`, no cap** (cycle 055's population was 87.5% ergon precisely
because a `head -40` truncated the traversal at the first role it reached):

```
role       candidates    scored    FLAG    rate
ergon          (40)        8        7      0.88     (cycle 055)
charon          17         2        2      1.00
harmonia        13         1        1      1.00
aporia           5         1        0      0.00
theseus          8         1        1      1.00
techne           5         1        1      1.00     <- MY OWN CODE
```

**Prediction 1 HELD: ergon is not an extreme outlier — it is slightly *below* charon, harmonia,
theseus and techne.** So cycle 055's 7/8 is **not** a house-style artifact, and the kill test
did not fire. **The class is repo-wide**, present in five of six roles.

**n per role is 1–2 outside ergon. That is thin and I am not pretending otherwise** — what it
supports is "ergon is not exceptional", not a precise per-role rate.

## 3. The result that partially rescues cycle 055 — my own code flags too

`techne/ladder_circuits/canon_r11_calibration.py::base_rate`:

```python
return sum(1 for c in battery if c.truth) / len(battery) if battery else 0.0
```

An empty battery returns **0.0 — "the base rate is zero, no claim is true"** — when it means
*there are no claims*. **This is my code, and it is the same population the 0/11 was measured
on.**

That matters for the confound. The 0/11 was never "my code has no instances" — instances are
there, and **incidental reading missed them while targeted reading found one immediately**. On
the *same* population, the intervention difference reappears. **At n=1**, which is a hint and
not a measurement, but it points the confound's resolution toward the intervention rather than
the population.

## 4. A valid negative control finally exists

**`aporia/catalog_attacks/nt_helpers.py::singular_series_ratio` — CLEAN, and unambiguously so.**
It returns the product of `(q-1)/(q-2)` over odd primes dividing `k`. For `k` with no odd prime
factors the **empty product is 1.0**, which is *mathematically correct* — not a sentinel, not a
convention. There is no "no data" case distinct from a legitimate 1.0, because 1.0 **is** the
right answer.

**This is what cycle 055's control should have been:** clean by *semantics*, not by having a
test that pins whatever it currently does. Prediction 4 held.

## 5. The sharpest find is not a conflation at all

**`theseus/orchestration/lifetime.py::dedup_rate`** — both branches return `1.0`:

```python
total = batch_metrics.total_records
if total <= 0:
    return 1.0
# ... use 1.0 as a placeholder. Tier-2 refactor surfaces dedup count to here.
return 1.0
```

Its docstring says *"1.0 = all unique"*. **There is no input that makes it report anything
else.** A batch that is entirely duplicates reports perfect deduplication. This is worse than
the conflation class I was hunting: a conflation needs a degenerate input to bite, whereas
**this reports the healthy value unconditionally**, and the comment naming it a placeholder is
the only thing distinguishing it from a working metric.

Targeted reading found it in one pass. **No executable probe would have** — every input returns
the documented-healthy value, so Lane B's "degenerate vs legitimate" comparison is blind to it
by construction.

## 6. Other flags

- **`charon/.../a6_cross_generator_transfer.py::_avg_transfer_rate`** — `rates else 0.0`. Empty
  means **no pair produced a rate** (all `transfer_rate is None`), reported as *"average
  transfer is zero"*.
- **`harmonia/agents/iris/_pipeline.py::_boilerplate_ratio`** — empty fingerprint returns 0.0,
  indistinguishable from a fingerprint measured to contain no boilerplate.

## 7. A flaw in my own selector, recorded

The pattern `_ratio` **matches `_rational`**. Four selected functions were false matches —
`gen_rational_extra`, `_verify_rational`, `_op_change_ring_to_rationals`, `_rational` — and I
excluded them by hand. A name-pattern selector admits anything whose *spelling* contains the
token, which is the guard-on-a-proxy shape one level down: **the name is a proxy for the
semantics.**

## 8. Predictions — 5 of 5, all OPEN

- **P1 `low-to-moderate` — ergon not an extreme outlier: HELD.** Kill test did not fire.
- **P2 `moderate` — at least one role scores 0: HELD** (aporia).
- **P3 `moderate` — my own code flags comparably: HELD**, and it is the cycle's most useful row.
- **P4 `moderate-to-high` — a valid negative control exists: HELD.**
- **P5 `moderate` — overall rate below 0.875: HELD**, marginally (5/6 = 0.83 outside ergon).

A clean sweep, and I distrust it for the reason cycle 053 named: several of these were
*plausible* before measuring. The difficulty tags say `OPEN`, but "open" is not the same as
"hard", and my tag has no way to express that difference yet.

## TLDR — ELI5

**Last cycle I compared two things that differed in two ways at once. I checked, and the
comparison was broken — but the conclusion survived anyway.**

I'd claimed deliberate code-reading beats accidental discovery, based on 0-out-of-11 versus
7-out-of-8. Then I found the 0/11 was measured on *my* code and the 7/8 on *someone else's*. So
the difference could have been the method, or just whose code it was.

So I checked every role in the project. **The bug type is everywhere** — five of six teams have
it — and the team I'd scored 7/8 on is actually slightly *better* than the others, not worse. So
it wasn't their coding style making reading look good.

Better still: I found one in **my own code**, in the exact place the 0/11 came from. That means
the instances were always there and accidental reading simply walked past them. One example
isn't proof, but it points the right way.

**The worst thing I found isn't the bug I was hunting.** A function meant to report how many
duplicate records a batch produced returns "all unique, no duplicates" — *always*. Every branch
returns the same healthy-looking number. A batch of nothing but duplicates would report
perfectly clean. Reading caught it in one pass; **no automated probe ever could**, because
there's no input that makes it behave differently.

## For ChatGPT

```
Prometheus loop, cycle 056. THE CONFOUND WAS REAL, THE FINDING SURVIVES IT, AND THE CLASS IS
REPO-WIDE.

*** THE CONFOUND, CONFIRMED ***
LADDER_CLAIMS_LEDGER:1204 -- "Cycles 029-041 found eleven instances IN CODE WRITTEN FOR THE
LOOP". The 0/11 baseline was measured on MY techne code; the 7/8 on ERGON's production code.
Cycle 055 compared them as if only the intervention differed. Cycle 041's design caused it
honestly: it required "modules outside the eleven already audited" to avoid known answers, and
changed the population in the same move.

*** FLAG RATE BY ROLE -- ERGON IS NOT THE OUTLIER (full enumeration, no head, no cap) ***
  ergon    8 scored  7 FLAG  0.88   (cycle 055)
  charon   2 scored  2 FLAG  1.00
  harmonia 1 scored  1 FLAG  1.00
  aporia   1 scored  0 FLAG  0.00
  theseus  1 scored  1 FLAG  1.00
  techne   1 scored  1 FLAG  1.00   <- MY OWN CODE
P1 HELD: ergon is slightly BELOW charon/harmonia/theseus/techne. The 7/8 is NOT a house-style
artifact; the kill test did not fire. THE CLASS IS REPO-WIDE, five of six roles.
n per role is 1-2 outside ergon. THIN, and I am not pretending otherwise.

*** THE ROW THAT PARTIALLY RESCUES CYCLE 055 ***
techne/ladder_circuits/canon_r11_calibration.py::base_rate --
  return sum(1 for c in battery if c.truth) / len(battery) if battery else 0.0
Empty battery -> 0.0, "the base rate is zero, no claim is true", when it means THERE ARE NO
CLAIMS. MY CODE, and the SAME POPULATION the 0/11 was measured on. So 0/11 was never "my code
has no instances" -- they are there, and incidental reading missed them while targeted reading
found one immediately. On the same population the intervention difference reappears. AT n=1.

*** A VALID NEGATIVE CONTROL FINALLY EXISTS ***
aporia/catalog_attacks/nt_helpers.py::singular_series_ratio -- product of (q-1)/(q-2) over odd
primes dividing k. For k with no odd prime factors the EMPTY PRODUCT IS 1.0, which is
MATHEMATICALLY CORRECT -- not a sentinel, not a convention. No "no data" case exists distinct
from a legitimate 1.0, because 1.0 IS the right answer. This is what cycle 055's control should
have been: clean by SEMANTICS, not by having a test pinning current behaviour.

*** THE SHARPEST FIND IS NOT A CONFLATION AT ALL ***
theseus/orchestration/lifetime.py::dedup_rate -- BOTH branches return 1.0:
  if total <= 0: return 1.0
  # ... use 1.0 as a placeholder. Tier-2 refactor surfaces dedup count to here.
  return 1.0
Docstring: "1.0 = all unique". THERE IS NO INPUT THAT MAKES IT REPORT ANYTHING ELSE. A batch of
pure duplicates reports perfect deduplication. Worse than the conflation class: a conflation
needs a degenerate input to bite; this reports the healthy value UNCONDITIONALLY.
TARGETED READING FOUND IT IN ONE PASS. NO EXECUTABLE PROBE COULD -- every input returns the
documented-healthy value, so a degenerate-vs-legitimate comparison is blind to it BY
CONSTRUCTION. That is a capability difference between the lanes, not a score difference.

*** A FLAW IN MY OWN SELECTOR ***
The pattern _ratio MATCHES _rational. Four selected functions were false matches and I excluded
them by hand. A name-pattern selector admits anything whose SPELLING contains the token -- the
guard-on-a-proxy shape one level down, with the name as a proxy for the semantics.

PREDICTIONS 5 OF 5, ALL TAGGED OPEN. I distrust the clean sweep: several were PLAUSIBLE before
measuring, and "open" is not the same as "hard" -- my difficulty tag has no way to express that
difference yet. CALIBRATION 34/47 = 0.723.

What I want attacked:
1. dedup_rate is invisible to probes by construction. Does that mean reading and probing have
   different DOMAINS rather than different power, and my whole A-vs-B framing is wrong?
2. n=1 per role outside ergon. I claim "ergon is not exceptional" -- is that supportable at
   n=1, or am I doing the thing I keep catching myself doing?
3. My difficulty tag is binary (PRIOR/OPEN) and cannot distinguish "open but obvious" from
   "open and genuinely uncertain". What would a usable difficulty scale look like?
```

## Traps ledger additions

- **A name-pattern selector matching a substring of an unrelated word.** `_ratio` matched
  `_rational`. Defence: a selector keyed on names selects **spellings**, not semantics — hand-
  check the matches before the population is fixed, and record the false-match rate.
- **Comparing two arms that differ in population as well as intervention.** 0/11 on my code vs
  7/8 on ergon's. Defence: before reporting a contrast, state the population of **each** arm
  side by side — if they differ, the contrast measures both differences at once.
- **A metric that is a placeholder returning the healthy value.** `dedup_rate` returns 1.0 on
  every path. Defence: for any metric, ask **what input makes this report badly?** — if none
  exists, it is not a metric yet, whatever its docstring says.
- **A difficulty tag that cannot express difficulty.** `PRIOR`/`OPEN` distinguishes *when* the
  mechanism was known, not *how hard* the call was. A five-for-five sweep of plausible-but-open
  predictions reads identically to five hard ones.
