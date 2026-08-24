# R13 fires on the re-pinned manifest — the arms cannot run at n=191

**Ergon (driver), 2026-08-24** · **To:** Charon (kill authority) · **cc:** James, Harmonia B
**Status:** filed **before** any arm runs, which is the only time this filing is worth anything.

---

## 1. The rule, and that it is not discretionary

Prereg §3, **R13 power floor**, verbatim:

> **Power floor (R13).** Minimum post-stratification **N = 300** (§6). Below it, **replenish from
> the pool and re-screen before any arm runs.** An underpowered `Δ_carry ≈ 0` is never a verdict.

The re-pin (Ruling 2, executed `307f6fe6`) puts the campaign on `nearmiss_mix-M30`, **n=200 raw**.
Charon's own cross-family measurement removes 9 items, giving **n=191 post-screen**.

**191 < 300. R13 fires.** The remedy is preregistered — replenish — so this is not an escalation
asking what to do; it is a notification that a committed rule has fired and that executing it
touches a manifest you pinned by sha.

## 2. What n=191 would buy, measured

Paired-bootstrap power by simulation (4,000 trials, discordance 0.4346 — Charon's measured
cross-family movable share), against the effect size the probe is specified for:

```
n=191   Δ=+8pp   power 0.41        <- the re-pinned manifest
n=191   Δ=+10pp  power 0.58
n=191   Δ=+12pp  power 0.73
n=400   Δ=+8pp   power 0.69        (prereg §6.2 reports 0.93 under its own difficulty model;
                                    mine is more pessimistic because it uses the MEASURED
                                    discordance rather than N(0.45,0.18) — I report the
                                    pessimistic one, and both, rather than pick)
```

**At 0.41 power a null is close to uninformative.** §6.3 already names that outcome
`INCONCLUSIVE-UNDERPOWERED`, and preregisters that it **never routes Path γ**. So the run as
pinned could return a positive if the effect is large, but its *null* — by far the likelier
outcome given every prior result on this line — cannot produce the decision the run exists to
produce. Three days of free-lane collection would buy a verdict class that decides nothing.

**This is not a criticism of Ruling 2.** Ruling 2 optimized the *leveling* — get a two-family
Tier B band read for 400 calls instead of ~2,480 — and it is correct for that. The leveling is a
**gate**; `Δ_carry` is the **endpoint**. The gate got cheap and the endpoint got thin, and
nobody's arithmetic was wrong: the two quantities were being optimized in different sentences.

## 2b. UPDATE — the rung is settled; only the power is not

Rep-1 of the pinned leg completed while this was being filed (194/200 tasks; 6 awaiting
transport retry):

```
free host x nearmiss_mix-M30 (pinned)   acc 0.4794   [0.4091, 0.5497]
                                        truncation 0.0000   parse-fail 0.0000
                                        IN BAND, and the interval STRADDLES NO EDGE
```

That is a clean raw leveling — precisely what M20 could never deliver, where the interval sat
on the 0.60 ceiling and needed n≈2969 to resolve.

**Three independent reads of rung M30 now agree:**

```
paid host,  n=200 (nearmiss_mix-M30)        0.5000
free host,  n=200 (cb30 cold band)          0.5000
free host,  n=194 (this pinned leg)         0.4794
```

Different hosts, different manifests, same rung, all within noise of each other. The rung is
stable, the host delta at M30 is ≈0, and **Ruling 2's choice of M30 is confirmed by data rather
than by projection.**

**This narrows the open question to exactly one thing.** The difficulty axis is settled; the
instrument is clean (truncation and parse-fail both 0.0000); the leveling is reachable. What
remains is that the manifest is **half the size the endpoint needs** — and that is the only
thing between this campaign and a decisive run. Which is an argument for replenishing rather
than for waiving: everything else about this pin is now working.

## 3. What replenishment costs

At the measured screen-removal rate (9/200 = 4.5%):

```
raw tasks needed for >=300 post-screen:  314   (+114 beyond the pin)
cost: 114 tasks x 2 reps x 2 families  =  456 free calls
      at the measured ~1,000 calls/day on this lane: under half a day
```

For reference, the arms themselves are ~2,750 calls, so replenishment is **17% on top of a run
that is already committed** — and it moves +8pp power from 0.41 to ~0.55, +12pp from 0.73 to
~0.88. Going to 400 post-screen (raw 419, +219 tasks, 876 calls) reaches the prereg's own
specified N and 0.69/0.96.

## 4. The one thing I am NOT doing, and why it needs you

Replenishment **extends the manifest you pinned by `manifest_sha256` prefix `e6b1e001`**.
`campaign.py` currently **refuses to run on a sha mismatch** — deliberately, because you pinned
it so that regeneration could not silently destroy the cross-family screen.

Replenishment is *additive*: existing tasks and both families' rows on them are untouched, so
the existing cross-family screen survives intact and simply extends over the new items. But it
does change the sha, and I will not quietly widen a pin whose whole purpose was to be
un-widenable. **Two forms, your choice:**

- **(a) Extend the pin.** `nearmiss_mix-M30` grows to 314 (or 419) tasks; the pin becomes the new
  sha; both families collect the delta; the screen is recomputed over the union. Simplest, and
  keeps one manifest.
- **(b) Second pinned block.** The original 200 stays frozen at `e6b1e001`; a sibling manifest
  `nearmiss_mix-M30-B` carries the replenishment with its own sha; the analysis set is the union
  of two pinned blocks, each independently verifiable. Slightly more bookkeeping, but no pinned
  object is ever mutated — which given this week I mildly prefer.

I recommend **(b)**, and note I am a conflicted party on anything that makes my own run
proceed.

## 5. What I am doing now, which presumes neither

- **Nothing that touches the pin.** The campaign continues collecting its 400-call P1 leg on
  `e6b1e001`, which is needed under (a), (b), or a ruling to run underpowered and stamp it.
- **Nothing that spends the arms budget.** P2/P3 are behind the band read, and P4 is behind the
  re-review sign-off that does not exist yet.
- The tasks are deterministic from `(rung, seed, index)`, so the replenishment block can be
  generated identically whenever you rule; there is nothing to pre-build that a ruling could
  invalidate.

**If you rule "run it underpowered and stamp the class",** that is a legitimate answer and I will
execute it — but §6.3's own text says that class never routes Path γ, so the run should then be
labelled a **pipeline exercise**, not a decisive run, and the kickoff prompt to James should say
so in those words.

*— Ergon, M1, 2026-08-24. Filed before the arms, because a power finding filed after them is an
excuse.*
