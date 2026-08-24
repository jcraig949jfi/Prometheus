# Cycle 059 — three instrument faults, one valid measurement, and the stopping condition fires

Prereg `fcedea89`, with a stopping condition committed in advance.

## 1. THE INSTRUMENT WAS WRONG THREE TIMES, AND THE THIRD MEANT NO MEASUREMENT HAPPENED

Reported first, because this is the cycle's substance.

**Fault 1 — timeout measured import cost.** The first run flagged a pile of `HANGS` in
`prometheus_math`. Those modules initialise PARI and take **~12 s to import** against a 5 s
timeout. `polynomial_length([0])` does not hang; it raises, with a good message. Fixed by
measuring each module's import cost and budgeting `import_cost + call_budget`.

**Fault 2 — the same root cause as cycle 052, seven cycles later.** Cycle 052 read sympy's lazy
import (277.9 ms first call vs 0.2 ms steady-state) as a 16x regression. Cycle 059 read PARI's
import as a hang. **Setup time attributed to the thing under test, twice, with the first written
into my own traps ledger in between.**

**Fault 3 — every function received a STRING.** `call_isolated` had
`json.dumps(json.dumps(...))` while the runner applies one `json.loads`, so `0.0` arrived as
`"0.0"`.

```
cf_from_float(0.0)    -> [0]                                  what I meant to send
cf_from_float("0.0")  -> TypeError: '>=' not supported ...    what the sweep actually sent
```

**So "128/128 RAISES" was not a clean arsenal refusing degenerate input. It was "you passed me a
string", 128 times.** The 3-module smoke run was invalid for the same reason — `squarefree_factors`
returns `None` on a string exactly as it does on an empty list, which is precisely why that one
looked plausible enough to report.

**All three were caught by implausibility, none by a guard.** That is now the fourth, fifth and
sixth measurement of mine that answered a different question than the one posed (049, 051, 052,
059×3). **A plausible wrong answer would have shipped every time.**

## 2. The corrected sweep — a valid measurement at last

```
45 calls over 3 modules:   RAISES 18   RETURNS 24   NAN 3   HANGS 0
```

**Three silent NaNs, all in my own code:**

```
mahler_measure([nan])       -> nan
log_mahler_measure([nan])   -> nan
polynomial_length([nan])    -> nan
```

That is **S5**, in the arsenal I own. And it is an **internal inconsistency**, not merely a gap:
`polynomial_length` refuses the zero polynomial with a carefully argued `ValueError` — *"a screen
with a wider domain than the thing it screens passes inputs the expensive step then rejects"* —
and then passes a NaN coefficient straight through. **One function, two out-of-domain inputs,
two different postures.**

Verified as correct and not flagged: `mahler_measure([1e308, -1e308]) = 1e308` (the polynomial
is `1e308(x−1)`, root on the unit circle) and `is_cyclotomic([1e308, -1e308]) = True` (same
reason). `mahler_measure_batch` returning `array([nan])` where the scalar raises is a
**documented** contract difference, not a defect.

## 3. THE STOPPING CONDITION FIRES — the instrument line stops

Pre-registered: *"If the sweep yields zero hangs AND zero new shapes, I stop the instrument line
in this cycle's report."*

- **Zero hangs.** ✓
- **Zero new shapes.** ✓ — the three NaNs are `S5`, already in the taxonomy since cycle 057.

**So it stops.** Four cycles (056–059) of instrument-building have not produced the
false-positive rate they were for, and the pre-registered condition for stopping is met. **I am
not starting a fifth.**

**Prediction 1 (a hang outside `singular_series_ratio`) FALSIFIED** on this sample —
cycle 058's `S6` looks like an isolated incident rather than a class, and per the prereg's
opposite-outcome clause I say so rather than keeping `S6` alive on one instance.

A corrected wide sweep over 15 further modules is running in the background. **It is a background
job, not a cycle** — if it surfaces a hang I will report it, but the line is closed either way.

## 4. Findings owed, and where the work goes next

**Finding #8 (Aporia)** — `singular_series_ratio(0)` never terminates.
**Reachability checked, not assumed**: the sole caller iterates `range(1, 51)`, so **realised
blast radius is zero**. Latent, not live. Written up in
`rung_notes/FINDING_008_aporia_singular_series_ratio.md`.

**Findings #9–11 (mine, and therefore fixable under my own mandate)** — the three silent NaNs
above. Unlike the eight cross-role findings waiting on their owners, these need nobody's
permission. **That is where cycle 060 goes**, together with the 46 arsenal reds.

## TLDR — ELI5

**My measuring tool was broken three separate ways today. The third one meant the measurement
never happened at all.**

I built a tool that feeds functions deliberately silly inputs — zero, empty lists, infinity — to
see which ones crash, hang, or quietly return nonsense. It's the one technique that has found
problems I couldn't have thought of on my own.

First it reported dozens of functions "hanging". They weren't: those modules take twelve seconds
just to *load*, and my patience limit was five. **I'd made this exact mistake seven cycles ago**
and written a note to myself about it.

Then, after fixing that, it reported that all 128 functions correctly rejected every bad input —
a perfect score. That was also wrong. A bug in my code was converting every number into *text*
before sending it, so every function was really being asked to process the word "0.0" instead of
the number zero. They all refused, correctly, and I'd have recorded it as "my code handles bad
input beautifully."

**Every one of these I caught because the answer looked too neat, not because anything checked.**

Once fixed, the real result: no hangs, but **three of my own functions quietly return "not a
number" instead of refusing** when handed a nonsense coefficient. One of them refuses a
*different* bad input with a carefully-worded error — so it has two different personalities
depending on which way you break it.

**And I'd committed in advance to stopping if this came up empty of new discoveries. It did. So
I'm stopping** — four cycles of tool-building without delivering what the tools were for is
enough, and next cycle goes to fixing the three bugs I found and the 46 failing tests I've been
carrying.

## For ChatGPT

```
Prometheus loop, cycle 059. THREE INSTRUMENT FAULTS, ONE VALID MEASUREMENT, AND THE
PRE-REGISTERED STOPPING CONDITION FIRES.

*** THE INSTRUMENT WAS WRONG THREE TIMES; THE THIRD MEANT NO MEASUREMENT HAPPENED ***
FAULT 1: timeout measured IMPORT cost. prometheus_math modules initialise PARI (~12s import)
against a 5s timeout, so a pile of "HANGS" were nothing of the kind. polynomial_length([0])
raises, correctly.
FAULT 2: SAME ROOT CAUSE AS CYCLE 052, SEVEN CYCLES LATER. 052 read sympy's lazy import (277.9ms
first vs 0.2ms steady) as a 16x regression; 059 read PARI's import as a hang. Setup time
attributed to the thing under test, twice, with the first in my own traps ledger in between.
FAULT 3: EVERY FUNCTION RECEIVED A STRING. call_isolated had json.dumps(json.dumps(...)) while
the runner applies ONE json.loads, so 0.0 arrived as "0.0".
   cf_from_float(0.0)   -> [0]                                what I meant to send
   cf_from_float("0.0") -> TypeError: '>=' not supported ...  what was actually sent
So "128/128 RAISES" was NOT a clean arsenal. It was "you passed me a string" 128 times. The
3-module smoke was invalid identically -- squarefree_factors returns None on a string exactly as
on an empty list, which is why it looked plausible enough to report.
ALL THREE CAUGHT BY IMPLAUSIBILITY, NONE BY A GUARD. Fourth, fifth and sixth measurements of
mine that answered a different question than the one posed. A PLAUSIBLE wrong answer would have
shipped every time.

*** THE CORRECTED SWEEP ***
45 calls / 3 modules: RAISES 18, RETURNS 24, NAN 3, HANGS 0.
THREE SILENT NaNs, ALL IN MY OWN CODE: mahler_measure([nan]), log_mahler_measure([nan]),
polynomial_length([nan]) all return nan without raising. That is S5, and it is an INTERNAL
INCONSISTENCY: polynomial_length refuses the ZERO polynomial with a carefully argued ValueError
and then passes a NaN coefficient straight through. One function, two out-of-domain inputs, two
different postures.
Verified correct and not flagged: mahler_measure([1e308,-1e308]) = 1e308 and
is_cyclotomic([1e308,-1e308]) = True (the polynomial is 1e308(x-1), root on the unit circle).
mahler_measure_batch returning array([nan]) where the scalar raises is a DOCUMENTED contract
difference.

*** THE STOPPING CONDITION FIRES ***
Pre-registered: "zero hangs AND zero new shapes -> stop the instrument line in this cycle's
report." Zero hangs. Zero new shapes (the NaNs are S5, known since 057). SO IT STOPS. Four
cycles (056-059) of instrument-building did not produce the false-positive rate they were for,
and I am not starting a fifth.
PREDICTION 1 (a hang outside singular_series_ratio) FALSIFIED -- cycle 058's S6 looks like an
ISOLATED INCIDENT, not a class, and per the prereg's opposite-outcome clause I say so rather
than keeping S6 alive on one instance.

NEXT: findings #9-11 are MINE and need nobody's permission, unlike the eight cross-role findings
waiting on owners. Cycle 060 goes there and to the 46 arsenal reds.

What I want attacked:
1. Three instrument faults in one cycle, all caught by implausibility. Is there any general
   guard for "my measurement answered a different question", or is implausibility genuinely the
   only signal?
2. I committed to a stopping condition and it fired on a 3-module sample, with the wide re-run
   still in flight. Is stopping on the small valid sample right, or is that the pre-registration
   being used to justify quitting?
3. polynomial_length refuses the zero polynomial with a paragraph of reasoning and silently
   NaNs on a NaN coefficient. What makes an author guard one out-of-domain input carefully and
   not notice the neighbouring one?
```

## Traps ledger additions

- **A timeout that does not separate setup from the thing under test measures the harness.**
  Twice now (052 sympy import, 059 PARI import). Defence: measure setup cost explicitly and
  budget `setup + work`, never a flat wall-clock.
- **Double-encoding across a subprocess boundary.** `json.dumps(json.dumps(x))` against one
  `json.loads` delivers a string. Defence: for any cross-process argument, assert the
  **received type** inside the runner before the call — one line, and it converts a silent
  invalidation into a loud one.
- **A result too clean to be real.** 128/128 RAISES with zero returns is not what a real arsenal
  looks like. Defence: treat a perfect score as a **defect report about the instrument** until
  a spot-check says otherwise.
- **A function that guards one out-of-domain input with an argument and misses its neighbour.**
  `polynomial_length` refuses the zero polynomial in a paragraph and NaNs on a NaN coefficient.
  Defence: when writing a domain guard, enumerate the *other* ways the domain can be violated.
