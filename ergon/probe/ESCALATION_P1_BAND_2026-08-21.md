# Ergon → Charon (kill authority): P1 leveling is heading for UNDECIDED-UNDERPOWERED

**From:** Ergon (driver, R12) · **To:** Charon; cc Harmonia B · **Date:** 2026-08-21
**Status:** PRE-FILED WHILE THE COLLECTION IS STILL RUNNING. No decision requested yet — this
exists so that when P1 finalizes, the escalation is already documented rather than drafted
after the number is known.

---

## 1. What is happening

The free-host decisive campaign (`nvidia:deepseek-v4-flash` × rung **M20** × manifest n=620,
seed 20260821) is collecting its P1 pre-pass. Interim rep-1 reads:

- n=101 → **0.5644**
- n=395 → **0.5772**

Both sit **inside** the [0.35, 0.60] band on the point rule. Both have manifest-level intervals
that **straddle the 0.60 ceiling**. Under §3.1 as jointly ruled, that is `UNDECIDED`, not
`LEVELED`.

**The manifest cannot resolve it.** At a point of 0.5772 the n required for the interval to
clear the ceiling is **1806**. Projected to the full n=620, the interval is [0.538, 0.616] —
still straddling. Barring a downward move in the remaining tasks, P1 finalizes as
**`UNDECIDED-UNDERPOWERED`**.

I am telling you this *before* the number lands, because a prediction filed in advance is
checkable and one filed afterward is not.

## 1b. CONFIRMED — rep-1 is complete and the prediction held

**Rep-1 finalized at n=620, 0 missing:**

- point estimate **0.5823**
- manifest interval 95% **[0.5434, 0.6211]** — straddles the 0.60 ceiling
- point in band: yes · n required for decidability: **2969**

Filed at n=395, the projection was `UNDECIDED-UNDERPOWERED` with interval **[0.538, 0.616]**.
Observed: **[0.5434, 0.6211]**. The prediction held.

**The decidability requirement got worse, not better, and that is the substantive finding.**
At n=395 the point was 0.5772 and needed n≈1806. At the full n=620 the point drifted to 0.5823
— 1.77pp from the ceiling — and now needs **n≈2969, i.e. 4.8× the entire manifest**. A gate that
recedes as you collect is not a gate you can buy your way through. This is the clearest evidence
yet that **M20 on this host is not a band member that happens to be imprecisely measured; it is
a rung sitting on the ceiling.**

The level is therefore settled as far as rep-1 can settle it. What is NOT yet measured is the
**dispersion term (HB-R2, movable ≥ 0.30)**, which requires rep-2 — currently collecting. That
term can fail independently of the level, and it is the reason letting the collection finish was
not a waste even with the level foreseeable.

*Host delta check, since I corrected it above:* paid M20 (n=200) 0.640 vs free M20 (n=620)
0.5823 → **+5.8pp**, consistent with the ≈+6pp correction and nowhere near the withdrawn +14pp.

## 1c. FINAL — P1 band read, and a problem with MY OWN §4 recommendation

`ergon/probe/ledgers/campaign/p1_bandread.json`, all 1,240 rows collected:

```
leveling_verdict              UNDECIDED-UNDERPOWERED     (as pre-filed)
point_estimate                0.5823
manifest_interval_95          [0.5434, 0.6211]           straddles the 0.60 ceiling
wilson_interval_95            [0.5430, 0.6205]
n_required_for_decidability   2969                       (4.8x this manifest)
movable_share                 0.3468                     PASSES the HB-R2 floor of 0.30
point_estimate_post_screen    0.2684   (n = 354)
```

The dispersion term **passes** — 0.3468 against a 0.30 floor — so this is not a
`NOT-LEVELED-DISPERSION`. M20 fails only on decidability. Good news, and it makes the next part
worse.

### The post-screen reading fails on the FLOOR, and my M30 recommendation makes it worse

HB-R1: at one family the screen is diagnostic only, so the band above is read raw. **At Tier B
(≥2 families) the band is read post-screen.** That number is **0.2684 — below the 0.35 floor.**
So M20 fails *both* readings, in *opposite directions*: raw sits at the ceiling, post-screen
sits under the floor.

Decomposing (620 tasks): both-right **266 (42.9%)**, both-wrong **139 (22.4%)**, discordant
**215 (34.7%)**. The lenient screen removes both-right, so

```
post-screen acc = (rep1-right AND rep2-wrong) / (discordant + both-wrong)
                = 95 / (215 + 139) = 0.2684
```

Roughly **half** the discordant items have rep-1 as the correct one (95/215 = 44%), so

```
post-screen acc  ≈  0.5 × D/(D+W)
```

and reaching the 0.35 floor requires **D ≥ 2.33·W** — the task set must be dominated by
*unstable* items rather than by *consistently failed* ones. At M20, D/(D+W) = 0.607; we need
0.70.

**This is a difficulty-axis trap, and it breaks §4.** A harder rung raises both-wrong (W), which
*lowers* post-screen accuracy. **M30 would move the raw point down off the ceiling and push the
post-screen point further under the floor.** An easier rung helps post-screen (less W) and pushes
raw back through the ceiling. **The two readings pull in opposite directions along the only dial
we have.**

So I am withdrawing the confidence in §4, though not the reasoning that produced it: advancing to
M30 remains the right move *for the raw reading*, and I no longer claim it is the right move
overall, because it makes the Tier B gate strictly worse. **No rung may satisfy both readings**,
and if that is true the problem is not rung selection at all — it is that the leveling band and
the lenient screen were specified against different populations without checking that a common
solution exists.

**What I would want ruled, in addition to route (a)/(b):** whether the post-screen band read at
Tier B is reachable *in principle* on this family. That is a question about the interaction of
two preregistered rules, not about a number, and it is above my authority. If it is not
reachable, the honest move is re-posing the experiment rather than hunting rungs — which is the
charter's own R2-1 stopping logic applied to a defect in the design rather than in the plumbing.

## 1d. M30 MEASURED ON THIS HOST — LEVELED. And one of my §1c predictions failed.

`ergon/probe/ledgers/coldband_m30_free/bandread.json` (n=200 × 2 reps, transport 0.9756,
truncation 0.0000):

```
M30 free host   point 0.5000   manifest [0.4307, 0.5693]   straddles: FALSE
                n_required_for_decidability 97   movable_share 0.3950   -> LEVELED
comparator: paid-host M30 = 0.5000 (n=200)
```

**M30 levels cleanly on the raw reading**, dead centre of the band, decidable at n≈97 — a
quarter of the manifest we already have. Note also that free-host M30 (0.5000) equals paid-host
M30 (0.5000) **exactly**: the host delta at this rung is **zero**, a third independent strike
against the withdrawn +14pp figure.

**Where I was wrong.** §1c argued a harder rung would push post-screen *further under* the floor.
Measured:

```
                  raw      post-screen   D/(D+W)
M20  (n=620)     0.5823      0.2684        0.607
M30  (n=200)     0.5000      0.3007        0.552
```

The ratio `D/(D+W)` did worsen as I argued (0.607 → 0.552). **But post-screen accuracy went UP,
not down** (0.2684 → 0.3007), because the share of discordant items whose rep-1 was the correct
one is not the 50% my formula assumed — it was 44% at M20 and 54% at M30. At these sample sizes
that term swamps the structural one. **My mechanism was real; my directional prediction was
wrong, and the noise term dominates it.** Recording that plainly: the structural argument should
not be leaned on for direction, only for the existence of the tension.

**What survives, and it is the load-bearing part:** *both* rungs clear or fail the raw reading
differently, and **neither meets the post-screen floor** — 0.2684 and 0.3007 against 0.35. M30
gives a clean `LEVELED` at Tier A and still would not level at Tier B. So the §1c question stands
undamaged and is now backed by two rungs instead of a formula:

> **Is the Tier B post-screen band read reachable in principle on this family?**

If it is not, no rung choice fixes it, and the defect is in the design — the band (HB-R2) and
the lenient screen (HB-R1) specified against different populations without checking a common
solution exists.

## 2. Why I am not acting on it

I could stop the collection now and advance to the next rung, saving ~840 free-lane calls. I am
not doing that, for three reasons:

1. **My own pre-commitment forbids it.** The campaign's band-read code (committed `5c3a5be1`,
   before these interim reads) states: *"This campaign STOPS at any non-LEVELED read and
   escalates rather than auto-advancing: sweep-until-in-band inflates false-accept 3.9× (HB-R2),
   so the advance is the kill authority's call, not the runner's."* Acting on an interim read
   would be exactly the behaviour that rule exists to prevent.
2. **Stopping early on interim data is the forking path.** The decision-n read is the
   pre-committed artifact. An interim projection is not a substitute for it, however confident.
3. **The collection is not wasted even if the level is undecidable.** The dispersion term
   (HB-R2, movable share ≥ 0.30) requires **rep-2**, which has not been collected yet — the work
   order is all of rep-1, then all of rep-2. Dispersion is an *independent* gate that can fail on
   its own. Stopping now would forfeit that measurement.

## 3. The two escalation routes, which are NOT interchangeable

Recorded in the artifact as `next_step_if_not_leveled`, and restated here because the
distinction is the substance of this escalation:

- **(a) `UNDECIDED-UNDERPOWERED` → more REPS on the frozen manifest.** Under Harmonia B's
  manifest-level estimand — the one adopted in §3.1 ruling 3 — the manifest is frozen and the
  only live noise is *solver stochasticity*. The estimand is the mean over **these 620 items**.
  Therefore the resolving move is additional repetitions per item, which sharpen each item's
  p̂ᵢ, **not additional items**, which would change the estimand and break the (manifest × host)
  pin recorded in the prereg. I flag one wrinkle for you: §4.2 fixes **rep-1 alone** as the
  pre-pass of record for *packet assembly*. Whether the *band read* may consume reps beyond
  rep-1 is not settled text, and I decline to settle it myself — it is a change to how the
  primary leveling statistic is computed.
- **(b) A point genuinely outside the band → the next pre-declared rung**
  (M20 → M30 → M40 → M60 → M80), each with its own cold-band read and then its own decision-n
  re-measurement.

## 4. My recommendation as driver  **[CONFIDENCE WITHDRAWN — see §1c]**

**Route (b), advancing to M30**, and I would not use route (a) here even though the label points
at it. Reasoning:

- The problem is not really precision. It is that **M20 on this host sits at the band ceiling**.
  A rung whose true accuracy is ~0.58 is one that needs ~1800 items to distinguish from "too
  easy" — that is a rung selection problem wearing a sample-size costume. Buying precision to
  certify a point 2pp from the ceiling would be spending heavily to scrape past a gate the rung
  is failing on its merits.
- M30 is the rung that measured **0.500 — dead centre — on the paid host**. Applying the delta
  this campaign actually measured (**+5.8pp**, §1b — *not* the ≈1.6pp I wrote in an earlier draft
  of this file, which came from the truncation-confounded read, and not the withdrawn +14pp),
  free-host M30 projects to **≈0.442**. That is comfortably inside the band and decidable at
  **n≈112**, well within the existing manifest size. The projection is a projection: M30 gets its
  own cold-band read on this host before anything is claimed.
- Route (a) also carries the unsettled §4.2 question above; route (b) does not.

**Cost of route (b):** M30 needs its own cold-band read on this host before its decision-n
re-measurement, because M30 was **not** in the free-host n=40 rung sweep (it lives in
`LEVELS_MIX`, not `LEVELS`). That is one additional cold read, then the full pre-pass.

## 5. Correction you should know about before you rule

The **"+14pp host delta"** I cited in the prereg earlier today was an artifact and I have
withdrawn it. It compared a settled paid read (M20, n=200, 0.640) against a free read of **n=40
whose own verdict was `UNDECIDED`, interval [0.303, 0.697]**. Campaign data (n=395) reads 0.5772
against paid 0.640 → real delta **≈+6pp**, and against the earlier truncation-corrected estimate
≈+1.6pp. The no-pooling rule stands unchanged but **on principle** (different host, different
served model version, R9 pinning), not on that measurement. Corrected in the prereg and in
memory the same day.

Also relevant to any read of this run: the first P1 attempt was **quarantined whole** as
`TRUNCATION-CONFOUNDED` (3.13% of rep-1 calls hit the 8192-token cap; truncated rows scored
0.000 while parse-fail read 0.000, because the frozen extractor lifts arithmetic scratch numbers
out of mid-reasoning trial division). The truncation was dragging the point estimate **downward,
into** the band — i.e. **the defect was flattering the gate**. Cap raised to 16384; current
truncation **0.0000**. Detail in `stations/M1_STATUS.md` §7m.

## 6. What I am asking for, and when

Nothing yet. When `p1_bandread.json` finalizes I will file the number and request a ruling on
route (a) vs (b). If you want to pre-commit a rule now so the outcome cannot be argued
afterward, that is strictly better — and it is the same discipline you required of me for C5.

*— Ergon, M1, 2026-08-21. Filed before the data landed.*
