# Cycle 027 — 2026-08-21 — REAL SUBSTRATE III: a chain that runs the other way

**Read-only audit of `prometheus_math.discovery_pipeline`'s kill-path battery.** 324 green.

Chose **(a)**, extending the real-substrate audit, because cycle 026 gave the instruments a
known-good domain and the right move was to point them somewhere new rather than speculate about
a second family. (b) — the rewrite-stage instrument spec — stays parked on HITL #88 awaiting a
ruling.

## ⚠️ HITL #78 — the loader drop is worse than when I found it

Re-checked at the top of this cycle: **400 rows on disk, 0 accepted, 100% drop.** It was 330 when
I found it two cycles ago and 369 last cycle. The campaign keeps writing and the loader keeps
discarding everything. Still unruled, still unpatched by me.

## Target chosen first, stage type verified before measuring

The cycle-025 guard, followed in order:

1. **Target:** the discovery pipeline's kill-path battery — F1 (permutation null), F6 (base
   rate), F9 (simpler explanation), F11 (cross-validation) — over polynomial candidates.
2. **Stage type:** each check is a **filter**. Filtering partitions the candidate set into
   survivors and killed, which is inter-record, so cycle 026's scope statement says the
   partition instruments apply.
3. **Direction check** — and this is where it got interesting.

Candidates are real: reciprocal integer polynomials with Mahler measures computed at high
precision, Lehmer's polynomial among them at M = 1.176281. Nothing is a fixture.

## Finding 1 — the battery ACCUMULATES, and the instrument inverts

Cycle 024 built the profile for a **transform** pipeline, where stage k+1 sees only stage k's
output. Those coarsen forward: deficit rises, excess falls.

A falsification battery does the opposite. Each check **adds a verdict bit** and discards
nothing, so the state after k checks refines the state after k−1. Measured over 34 real
candidates:

```
                      deficit    excess
before any check       1.8295    0.0000     H(terminal) = 1.8295 bits
after F1               0.8698    0.0000
after F6               0.0000    0.0000
after F9               0.0000    0.0000
after F11              0.0000    0.0000

forward  is_refinement_chain : False
reversed is_refinement_chain : True
matches cycle-024 assumption : False
```

**Deficit decreases to zero** — exactly what a working battery should do, and exactly what cycle
024 asserts cannot happen. `is_refinement_chain` returns False on a perfectly healthy battery,
which read naively says *"this is not a pipeline"*.

So the instruments are not blind here as they were on rewrite stages. They are **inverted**, and
that is the worse failure: an empty reading is obviously useless, a confident wrong one is not.

**The taxonomy is now three categories, each measured on live code rather than assumed:**

```
transform / rewrite    content changes, records stay distinct    instruments BLIND      (025)
select / reorder       records chosen and ordered                instruments WORK       (026)
filter / accumulate    verdict bits added, nothing discarded     instruments INVERTED   (027)
```

## Finding 2 — two of the four checks carry zero bits on this evidence

```
F1   0.9597 bits
F6   0.9082 bits
F9   0.0000
F11  0.0000
```

F9 and F11 return the same verdict for every candidate measured. The chain says the same thing
from the other side: deficit reaches zero at F6 and the last two stages move nothing.

That is **canon R11's hedging forecaster inside a real falsification battery** — a member that
never fires is observationally identical to a member that is not there, and both are perfectly
"sound". The R11 lesson applies unchanged: reliability alone is not the verdict, resolution has
to be scored beside it.

Reported, not judged. A check that has not fired on the candidates it has seen may still be the
one that catches the next thing, and 34 candidates is a small sample of a narrow band. What is
worth knowing is that the battery's discriminating power **on this evidence** is entirely F1 and
F6.

## Track 1 — `chain_direction`

`DESTROYING` / `ACCUMULATING` / `NEITHER`, computed from the partitions alone with no knowledge
of what the stages do. It is a **precondition**, not a new measure: reading a profile without
checking direction first is how a healthy accumulating chain gets flagged as broken. `NEITHER`
means consecutive stages are incomparable and no chain argument is available at all.

## TLDR — ELI5

The tools measure how information moves through a series of steps, and they were built assuming
each step *throws things away* — which is true of a pipeline that rewrites and trims.

A falsification battery is the opposite. Each check *adds* a verdict, nothing gets discarded, so
information piles up instead of draining. The tool's health check reads "this isn't even a
pipeline" for something that is a perfectly good pipeline running the other way. That's more
dangerous than last cycle's problem, where the tools simply saw nothing — a blank answer is
obviously useless, a confident wrong one isn't.

The fix is small and boring: check which way the chain runs before reading anything else.

Second thing, which fell out for free: of the battery's four checks, two of them gave the same
answer for every single candidate. They never disagree with anything, so they can't be helping
decide anything — the verdict is fully settled after the second check. That might be fine (a
check that hasn't fired yet may catch the next thing), but it's worth knowing that the battery's
actual discriminating power right now is two checks, not four.

## For ChatGPT

```
Prometheus loop, cycle 027 — third real-substrate audit. READ-ONLY on
prometheus_math.discovery_pipeline's kill-path battery (F1 permutation null, F6 base rate, F9
simpler explanation, F11 cross-validation). 324 green.

I followed the cycle-025 guard in order: target first, then stage type, then measure. Target =
the battery. Stage type = FILTER, which partitions the candidate set, so inter-record, so cycle
026's scope statement says the instruments apply. Then a direction check, which is where it went.

FINDING 1 — A FALSIFICATION BATTERY IS A CHAIN RUNNING THE OTHER WAY. Cycle 024 built the profile
for TRANSFORM pipelines where stage k+1 sees only stage k's output; those coarsen forward,
deficit rises. A battery ADDS a verdict bit per check and discards nothing, so it REFINES
forward. Measured over 34 real reciprocal polynomials (Mahler measures at high precision,
Lehmer's among them):
    deficit  1.8295 -> 0.8698 -> 0.0000 -> 0.0000 -> 0.0000   (H(terminal) = 1.8295)
    forward is_refinement_chain  = False
    reversed is_refinement_chain = True
Deficit DECREASES, which is what a working battery should do and what cycle 024 asserts cannot
happen. is_refinement_chain returns False on a healthy battery, which read naively says "this is
not a pipeline". So the instruments are not BLIND here as they were on rewrite stages — they are
INVERTED, which is worse: an empty reading is obviously useless, a confident wrong one is not.

The stage-type taxonomy is now three categories, each measured on live code:
    transform / rewrite    instruments BLIND      (cycle 025, ergon render/redact)
    select / reorder       instruments WORK       (cycle 026, ergon _order vs BC-2)
    filter / accumulate    instruments INVERTED   (cycle 027, discovery battery)

FINDING 2 — TWO OF FOUR CHECKS CARRY ZERO BITS. F1 = 0.9597 bits, F6 = 0.9082, F9 = 0.0000,
F11 = 0.0000. F9 and F11 return the same verdict for every candidate; the chain agrees, with
deficit hitting zero at F6 and the last two stages moving nothing. That is canon R11's hedging
forecaster inside a real falsification battery — a member that never fires is observationally
identical to a member that is absent, and both are perfectly "sound". Reported not judged: 34
candidates in a narrow band is a small sample and a check that has not fired may still catch the
next thing.

Track 1: chain_direction (DESTROYING / ACCUMULATING / NEITHER) computed from partitions alone. A
PRECONDITION rather than a new measure.

What I want attacked:
1. Three stage types found in three cycles, each by pointing the same instruments at a new
   pipeline. That rate makes me think the taxonomy is incomplete rather than converging. Is
   there a principled enumeration of how a stage can relate information in to information out —
   my three are "loses", "reorders", "adds" — or am I discovering categories one accident at a
   time?
2. Finding 2 worries me more than I have written. If two of four battery members never fire, the
   battery's advertised strength is 4 and its measured strength is 2, and every claim that
   survived it survived a weaker test than stated. Is there a defensible way to report battery
   strength that accounts for non-firing members without punishing a member that is genuinely
   guarding a rare failure mode? R11's resolution/reliability pair is the closest thing I have
   and it does not obviously transfer.
3. Is "check the direction first" enough of a repair, or does the existence of an inverted case
   mean the profile should not report monotonicity verdicts at all — just the numbers, with
   interpretation left to whoever knows the pipeline? I lean toward the latter but that removes
   the seam-location result from cycle 024, which was the most useful thing the profile did.
```

## Traps ledger additions

- **Inverted chain read as a broken one** — an accumulating pipeline violates every monotonicity
  a destroying pipeline satisfies. Defence: `chain_direction` as a precondition, before any
  profile is interpreted.
- **Non-firing battery member** — a check that returns the same verdict for every candidate
  contributes zero bits and is observationally identical to an absent check. Defence: per-member
  resolution reported alongside the battery's size; a battery of four with two non-firing members
  is a battery of two.
