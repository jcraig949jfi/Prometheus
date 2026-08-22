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

## 4. My recommendation as driver (yours to accept or refuse)

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
