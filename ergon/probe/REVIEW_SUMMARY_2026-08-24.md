# Metabolization Probe — summary for external review, 2026-08-24

**Seat:** Ergon (driver, R12) · **Period:** 2026-08-21 → 08-24 · **Spend: $0** (free lane)
**Reviewers:** external · **cc:** Charon (kill authority), Harmonia B (independent), James (HITL)

---

## 1. The original request, restated

James, 2026-08-21:

> *"Can we try the decisive run on the free tier? Loop every 30 minutes, test whether the
> channel is open and if so, push api calls through, if not, sleep for that loop cycle."*

Context: the paid DeepSeek balance was exhausted at −$0.70 and James had said "no more money
spend right now." The probe's decisive run (Tier B) was blocked on funds. The ask was to run it
on the free NVIDIA lane with a polling loop.

**That request was fulfilled on day one.** `ergon/probe/campaign.py` + scheduled task
`PrometheusCampaign` does exactly it: probe the channel, push if open, sleep the cycle if not.
Everything after that is what the loop *found* — which is the substance of this document.

## 2. What the loop was supposed to produce, versus what it produced

**Supposed to produce:** a decisive Δ_carry reading — does retrieved failure residue improve the
next attempt (F-prom-retrieved − F-null), at D0, on a leveled task family.

**Produced instead:** the run has not reached its arms, and is currently **halted by its own
preregistered power floor**. What it produced is a chain of defects and mis-measurements, most
of them in the measuring apparatus rather than in the world. That is a real result for a program
whose thesis is *metabolize failure*, but it is not the result the run was for, and should not
be dressed as one.

## 3. Findings, ordered by what a reviewer should care about

### 3.1 The corpus finding — largest, and independent of the probe

Full scan of all 165 batch files (346 GB, `ergon/probe/corpus_scan_full.py`):
**132,312,039 REJECTED records · 43 (generator × claim_kind) cells · 131,649 kill_patterns.**

Aggregate entropy looks healthy (7.105 bits). **Per cell it collapses:**

- **27 of 43 cells — 89,949,006 records, 68.0% of the corpus — have a TOTAL failure vocabulary
  of ≤8 patterns (≤3 bits).**
- **16.8M records (12.6%) sit in cells with exactly ONE pattern: 0.0 bits — the designated
  failure signature is a constant.**
- `a1` and `f1` have **identical** vocabularies (Jaccard 1.0000).
- Nearly all apparent richness is two mid-sized cells (`d3`, `a3`).

**Reading:** a year of accumulation produced 132M failure rows whose *designated signature* is,
for two thirds of them, a ≤3-bit label. This is the "navigable vs merely logged" question
answered at corpus scale.

**Bounds that must travel with it:** `kill_pattern` is ONE field — `canonical_claim_text` and
`claim_payload` are 100% populated, `step_trace` 17.2%. The *record* is not 2 bits; the
*designated signature* is. And 132M rejections across 43 cells implies heavy duplication that
is **unmeasured** — this is not 132M distinct failures.

**In flight:** a channel-capacity measurement (`ergon/probe/channel_capacity.py`, spec committed
before it ran) is measuring how many bits survive *instance normalization* per cell, to
determine whether a D2/D3 arm has anything to ablate. Currently 90/165 files.

### 3.2 A defect class that recurred four times in four subsystems

**Wrong-population statistics** — a number true of the rows it was computed over, quoted as a
property of rows it was not:

- **"Free lane: ~40 calls/day."** Measured on `nemotron` (walls at 43). The lane served
  **1,058 calls/day** on `deepseek-v4-flash` with zero 429s. **25× error, in the direction of
  not doing work that was free all along.**
- **"+14pp host delta."** A settled paid read minus a free read of **n=40 whose own verdict was
  UNDECIDED, interval [0.303, 0.697]**. Real value ≈ +6pp; at rung M30 it is **0.000**. It had
  reached a BINDING prereg before being caught.
- **"kill_pattern has 33.6% nulls."** Computed over all records including non-failures. Among
  REJECTED it is **100% populated**. This framing had suppressed D2/D3 — the North Star
  question — as "residue too sparse" for a year.
- **The Tier B gate "unreachable."** *(Found by Charon, against me.)* I put single-family
  screens (0.2684, 0.3007) against a floor defined on a **cross-family** statistic. Nobody had
  computed the specified statistic; two families had never run a common manifest. When Charon
  found one they had both run, the two statistics read **0.3151 (NOT-LEVELED)** and
  **0.4764 (LEVELED)** on identical rows — 16pp apart, opposite verdicts. **I had proposed
  re-posing the experiment on the strength of the wrong one.**

The generalized ask this yields: *"measured over WHICH rows — and is this the statistic the RULE
names, or the one my data affords?"*

### 3.3 Defects where the flaw pushed *toward* the answer it received

Two, in one week, in opposite directions — worth naming as a pattern:

- **Truncation flattering a leveling gate.** 3.13% of calls hit an 8192-token cap; truncated
  rows scored **0.000** while parse-failure read **0.000**, because the extractor lifted
  arithmetic scratch numbers out of mid-reasoning trial division and scored them as answers. The
  observed 0.604 = 0.624 × (1 − 0.031): the defect dragged the point **into** the band. Had it
  landed at 0.60 the host would have been certified LEVELED on a number the defect created.
- **A gate that could not fail.** My drip computed truncation from a field its own writer never
  emitted, so the comparison was always false and the rate was identically `0.0000` — not a
  measurement. *(Found by Charon.)* Direction: truncation depresses accuracy, and that verdict
  failed by being too low, so the unmeasured defect pushed toward the verdict received.

Both are now enforced: gates raise on absent inputs rather than returning a passing value.

### 3.4 The current blocker, which is preregistered

Charon's Ruling 2 re-pinned the campaign to a manifest a second family had already run — 400
calls to buy a two-family Tier B leveling instead of ~2,480. Correct for the *leveling*.

But the leveling is a **gate**; Δ_carry is the **endpoint**. That manifest yields **n=191
post-screen**, and prereg **R13** sets a hard floor of **N=300**, with a preregistered remedy.
Measured power at n=191 for the specified +8pp effect: **0.41** (4,000-trial paired bootstrap at
the measured discordance 0.4346). At that power a null routes `INCONCLUSIVE-UNDERPOWERED`, which
§6.3 preregisters as **never routing Path γ**.

So ~2,750 free calls would buy a verdict class that decides nothing. **The campaign now halts
before the arms.** Replenishment costs 456 free calls (17% on top of a committed run) but
extends a manifest pinned by sha specifically so it could not be widened — escalated, not
self-authorized (`ergon/probe/R13_REPLENISHMENT_2026-08-24.md`).

### 3.5 Method notes a reviewer may want to attack

- **A prediction was filed before its data existed and held.** At n=395 I filed
  `UNDECIDED-UNDERPOWERED`, projected interval [0.538, 0.616]. Observed at n=620: 0.5823,
  [0.5434, 0.6211]. (Commit `70459647`, before the data.)
- **A prediction of mine failed and is marked in place.** I argued a harder rung would push
  post-screen further under the floor; it went **up** (0.2684 → 0.3007). Mechanism real,
  direction wrong, noise term dominant at these n.
- **A sample of the same corpus produced the opposite conclusion** to the full scan, because a
  contiguous head-of-file window sees few generators and never contained `f1`. Both readings are
  in the record, the sample marked withdrawn.
- **A near-destruction of data.** A failed `git stash -u` plus a `stash drop` destroyed two
  collected ledgers; recovered via `git fsck` from the stash's third parent. Root cause: the
  ledgers were never committed — not ignored, merely uncommitted. All probe ledgers are now
  tracked.
- **A test wrote a gate-waiver file into the LIVE ledger directory**, because the path was bound
  at import instead of resolved at call time. A stray waiver silently disables a power floor.
  Removed; path fixed; the fixture now asserts the live tree is untouched after every test.

## 4. What is running, all free, none needing attention

- **M30 primary leg** — 140/400 rows, truncation 0.0000, transport ~97%.
- **Second family re-collection** — restarted under the fixed writer and cap; the drip now
  collects the *admitted* family first rather than burning each firing on transport-degraded
  candidates ahead of it.
- **Channel-capacity scan** — 90/165 files, 80,300 records sampled.

## 5. What blocks progress, and on whom

1. **Harmonia B's exit review #3** — the *only* gate on P4. Charon's passed; he correctly
   declined to create the sign-off on his own PASS.
2. **Charon's R13 replenishment ruling** — extend the pinned manifest, or add a second pinned
   block, or rule the run underpowered (in which case it should be labelled a pipeline exercise,
   not a decisive run).
3. **Nothing is blocked on money.** The free lane sustains ~1,000 calls/day.

## 6. The honest bottom line

The probe has not measured whether Prometheus can metabolize failure. It has spent this period
**measuring its own instrument, and finding it defective in six independent ways** — four of
them wrong-population errors, two of them defects that pushed toward the answer they received.
Every one was caught before it entered a verdict, several by seats other than the one that made
them, and each is now enforced in code rather than described in a document.

Whether that constitutes progress is exactly the question an external reviewer should press on.
The strongest case for "yes" is §3.1, which is a real finding about the accumulated corpus and
does not depend on the probe running at all. The strongest case for "no" is that the decisive
run has been three days from firing for two weeks, and the reason keeps changing.

*— Ergon, M1, 2026-08-24. Every number regenerable from a committed command.*
