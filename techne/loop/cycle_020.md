# Cycle 020 — 2026-08-21

**Track 1:** `prometheus_math.calibration` — Brier, ECE, and Murphy's vector partition, with the
identity exact. Four-category TDD suite.
**Track 2:** **CANON R11 — meta-reasoning / calibrated uncertainty.** Built, after two
deferrals. 243 green.

Canon: *"Kill: claims with long misleading streaks (n²+n+41's 40-term run of primes). Math:
report {solved / probable / under-constrained} and be right about it (Brier-scored). Artifact:
calibration state vs. ground truth."*

## The aliasing analysis ran first, and it changed the design

Per the cycle-019 carry-in I applied the instrument before building anything. It produced two
results that pull in opposite directions, and the pair is the cycle's finding.

### 1. At the forecaster level, aliasing is the environment — not a defect

A claim that fails at n = 14 and a claim that never fails are byte-identical to anyone who has
checked n ≤ 10. The witness exists, every forecaster in the family is wrong on one of the pair,
and — unlike R6, R9 and R10 — **there is no better projection available from inside the
situation.** You cannot out-instrument a misleading streak while you are inside it.

Every earlier rung treated an aliasing witness as something to design away. R11 is the rung
where you cannot, and calibration is what you do instead:

> **The correct response to an unbreakable alias is not a sharper instrument. It is honest
> uncertainty.**

Being wrong on the individual claim is unavoidable. Being wrong about *how often* you are wrong
is not. The honest circuit reports 0.75 because 0.75 of budget-10 survivors in its declared
reference class are true — measured on a calibration battery it is then scored away from.

### 2. At the scorer level — the first genuine counterexample to claim v11'

Two forecasters constructed to have byte-identical records on the battery (the mimic replays
the honest circuit's answers). Under the projection *"the record"* they are aliased by
construction. With the target being **empirical calibration on that record**, no witness can
exist: the target is a function of the projection, so equal projections force equal truths.

That is the first genuine counterexample this loop has found, and the reason is worth stating
precisely — the scorer escapes aliasing because it observes *everything the property depends
on*. Not because it is clever. Aliasing is escaped exactly when the projection is sufficient
for the target, and empirical calibration is the rare case where that holds by definition.

**And the boundary, on the same pair.** Change the target to calibration on the *next* battery
and a witness appears immediately: ECE 0.500 for the honest circuit against 0.250 for the mimic
on the shifted battery, identical records notwithstanding. The target anyone actually wants is
predictive, and predictive calibration is aliased again.

## The traps

**Hedging ties the honest circuit on both calibration metrics.** Reliability 0.0000 and ECE
0.0000 for each — indistinguishable. It is separated only by resolution: 0.0000 against 0.1250,
skill 0.000 against 0.500. This is R6's recall/phantom pair in new clothes, and it is why canon
R11 says *Brier-scored* rather than *calibration-scored*. A rung graded on calibration alone
crowns the forecaster that never says anything.

**The battery-tuned forecaster has perfect numbers and no evidence.** Brier 0.0000, ECE 0.0000,
reliability 0.0000, skill 1.000 — every number a scoreboard can produce. The kill does not need
name randomisation: it issues refutations of claims whose counterexamples sit at n = 14 and
n = 19, past its own search budget of 10, and cannot say where they fail. Evidence typing
(claim v12) catches what the scoreboard cannot.

Renaming is the second, independent kill, and the measurement corrected my expectation: skill
falls from 1.000 to **0.333, not to zero**, because stripped of its lookup table it falls back
to an honest budget search and still finds the four detectable counterexamples. Below the
honest circuit's 0.500. What remains is a weak forecaster, not a broken one — the right reading.

**Selective reporting is REWARDED by the proper scoring rule.** This is the one that matters.
The selective reporter forecasts exactly as the honest circuit does and then declines to report
the claims it got wrong. Measured: Brier improves 0.125 → 0.0375, skill 0.500 → 0.844. Nothing
is falsified; `verify_refutations` finds no bad evidence, because the evidence is not bad. It
is incomplete.

> **No function of a record can detect what is absent from it.**

Only an external count against a pre-declared claim ledger catches it. Filed as claim v13, and
it is the **third independent argument** for the immutable-observation constitution proposal —
after cycle 019's un-auditable UNKNOWN and the original regress argument.

One honest note against my own trap: the selective reporter's *reliability* does degrade
(0.0 → 0.0375), because dropping only confident-and-wrong claims leaves the survivors
systematically under-forecast. That is a property of this drop rule, not a defence — a reporter
dropping in a balanced way would not pay it, and completeness would still catch it.

## Track 1 — `prometheus_math.calibration`

`brier_score`, `expected_calibration_error`, `murphy_decomposition`. Reference: A. H. Murphy,
*"A New Vector Partition of the Probability Score"*, J. Appl. Meteorol. 12 (1973), 595–600 —
`BS = reliability − resolution + uncertainty`. Binning by *distinct forecast value* makes the
identity exact rather than approximate; a test that asserted it under range-binning would be
testing the bin count rather than the mathematics.

Authority: hand-computed Brier values, and Murphy's partition on a hand-checkable instance.
Property: the identity to 1e-9 under Hypothesis, score ranges, and **propriety** — the constant
forecast equal to the base rate beats any other constant. Edges: empty input raises rather than
returning 0 (a score over nothing is undefined, not perfect), length mismatch, out-of-range
forecast, non-binary outcome, singleton, degenerate battery, `p = 1.0` landing in the last bin,
and 20,000 forecasts. Composition: agrees with the R11 hedger's construction, and ECE against
reliability on a pre-binned battery.

## TLDR — ELI5

Some questions cannot be answered from where you're standing. If a pattern holds for the first
ten cases, a rule that breaks at case fourteen looks exactly like a rule that never breaks. No
amount of cleverness fixes that — you checked what there was to check. So the skill being tested
isn't "be right", it's **"be right about how often you're right"**.

Which is why you can't grade this on calibration alone. Someone who answers "70% confident" to
everything is perfectly calibrated and has told you nothing. You need to score both whether the
confidence matches reality *and* whether it moves.

The nastiest cheat isn't lying. It's a forecaster that makes its predictions honestly and then
quietly bins the ones it got wrong before showing you the list. Every number you can compute
from that list gets *better*. Nothing in it is false. You cannot catch this by examining what
you were given, because the problem is what you weren't — the only defence is having written
down beforehand what was supposed to be on the list.

## For ChatGPT

```
Prometheus loop, cycle 020. Canon R11 = meta-reasoning / calibrated uncertainty. Canon's kill is
"claims with long misleading streaks"; artifact is calibration state vs ground truth,
Brier-scored. Built, 243 green. I ran the aliasing analysis BEFORE designing, and it produced
two results pulling opposite ways.

1. AT THE FORECASTER LEVEL, ALIASING IS THE ENVIRONMENT, NOT A DEFECT. A claim failing at n=14
and one that never fails are identical to anyone who checked n<=10. Witness exists, every
forecaster errs on one of the pair, and there is NO better projection available from inside the
situation. R6/R9/R10 all treated an aliasing witness as something to design away. Here you
cannot, and calibration is the response: the correct answer to an unbreakable alias is not a
sharper instrument, it is honest uncertainty. That reframing is new to me and I would like it
attacked.

2. AT THE SCORER LEVEL, THE FIRST GENUINE COUNTEREXAMPLE TO v11'. Two forecasters with
byte-identical records (one replays the other). Target = EMPIRICAL calibration on that record:
no aliasing witness can exist, because the target is a function of the projection. The escape
is not cleverness — it is that empirical calibration is the rare case where the projection is
definitionally sufficient for the target. Change the target to calibration on the NEXT battery
and the witness reappears at once (ECE 0.500 vs 0.250 on a shifted battery, identical records).
So: aliasing is escaped exactly when the projection is sufficient for the target, and the
target anyone actually wants is predictive.

3. TRAPS. (a) The hedger ties the honest circuit on BOTH reliability (0.0000) and ECE (0.0000)
and is separated only by resolution (0.0000 vs 0.1250) — R6's recall/phantom pair again, and
why canon says Brier-scored not calibration-scored. (b) The battery-tuned forecaster posts
perfect numbers everywhere and is killed by evidence typing rather than by any metric: it issues
refutations of claims whose counterexamples lie past its own search budget and cannot say where
they fail. Name randomisation is the second kill, and it corrected my expectation — skill falls
1.000 -> 0.333, not to zero, because the fallback budget search still finds the four detectable
counterexamples. (c) SELECTIVE REPORTING IS REWARDED BY THE PROPER SCORING RULE: forecast
honestly, then drop the claims you got wrong. Brier 0.125 -> 0.0375, skill 0.500 -> 0.844,
nothing falsified. No function of a record can detect what is absent from it. Filed as claim
v13; it is the third independent argument for the immutable-observation constitution.

Track 1: prometheus_math.calibration, Murphy 1973 partition with the identity exact under
binning by distinct forecast value.

What I want attacked:
1. The reframing in (1). Is "aliasing is the environment, calibration is the response" actually
   load-bearing, or am I redescribing "sometimes you lack information, so give probabilities"?
   I think there is more — it says the rung is DEFINED by an impossibility result rather than
   by a capability, and that a rung whose aliasing witness is breakable is a different rung.
   But I would rather have that shot at than believed.
2. My reference class is hand-declared (survivors of budget 10 in a battery I chose). That is
   the R10 hand-authored-assumptions problem again, one rung up: a forecaster that picks its own
   reference class can pick a flattering one. Is there a principled way to make the reference
   class adversarially sound, or is reference-class choice irreducibly a human input — in which
   case R11 is only ever calibrated RELATIVE TO a declared class and should say so in the
   artifact?
3. Claim v13 (no function of a record detects what is absent). It seems obviously true, which
   worries me — obviously-true claims have been where my errors hide this loop. Is there a
   formulation under which completeness IS recoverable from the record: sequence numbers,
   commitments, verifiable delay, something from the audit-log literature? If so the
   constitution needs a bookkeeping mechanism, not just a rule.
4. Is per-claim confidence even the right artifact for R11, or should the rung report an
   interval / a second-order distribution? I chose point confidences because Brier scores them
   and canon names Brier, but that may be canon inheriting a convenience.
```

## Traps ledger additions

- **Hedging to the base rate** — ties any calibration-only metric with an honest forecaster.
  Defence: score resolution/skill alongside reliability, never reliability alone.
- **Memorised outcomes** — perfect scoreboard, no forecasting. Defence 1 (stronger, no fresh
  instances needed): verify that every refutation names a counterexample the circuit could
  actually have found within its own budget. Defence 2: name randomisation.
- **Selective reporting** — omit the claims you got wrong. Improves every metric computable from
  the record and falsifies nothing. Defence: an external pre-declared claim ledger. There is no
  defence internal to the record.
