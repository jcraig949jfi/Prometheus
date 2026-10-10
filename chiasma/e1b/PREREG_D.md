# PREREG D (DRAFT, NOT FROZEN): CHIASMA compression halves on PW-D

Seat: Hades. Status: **DRAFT**. It is frozen only by a later commit that adds
chiasma/e1b/FREEZE_D.json (this file's sha256 over LF bytes, the code blob ids, the
commit). The freeze waits on the G3 first-sight challenge of E1 and of the E1b dev
findings (Hestia; comms #2046, #2049, #2081). Until then this file may change, and
every change is visible in git history.

Basis: chiasma/e1b/DEV_NOTES.md s11-s16 (dev seeds 910001-910010 only).

## Exposure record

Before this draft, the author saw development seeds 910001-910010 on PW-D (dev-5,
dev-6) and PW-Dm (dev-7). The arms, caps, endpoints and thresholds below were chosen
after seeing those rows. That is why this is a confirmatory test on fresh seeds and
not a report of the dev rows. Evaluation seeds do not exist yet. They are derived from
this file's own hash at freeze time.

## Code under test

chiasma/world.py, organisms.py, runner.py (E1, frozen, imported) and chiasma/e1b/
world_d.py, arms.py, factor.py, run.py, sweep.py, verdict_d.py at the blob ids that
FREEZE_D.json will list. No change to these files after the freeze affects this test.

## Design

- World: PW-D, WorldSpecD defaults (m = 32; three 4-literal cores; loads 12:4, 8:8,
  4:12; marker = False).
- Binding budget: pevict on for every run (one P-eviction rule for every arm).
- Caps: 650 and 700 (deciding), 800 (reported, not deciding), 10^6 (uncapped
  instrument check).
- Arms (org_seed 0):
  - O0: flat geometry, projected shadow.
  - O0F: factored geometry, projected shadow.
  - SRF: factored geometry, raw failure FIFO.
  - SXF: factored geometry, random counterfeit shadow.
  - S0F: factored geometry, no failure memory.
  - SPFF: factored geometry, factored projected shadow (secondary only).
- Evaluation seeds: s_i = int(H[:8], 16) + i for i = 0..9, where H is this file's
  sha256 in FREEZE_D.json. If any s_i falls in 910001-910010 or 900001-900005, the block
  shifts by +10 until it does not.
- Command: python -B -m chiasma.e1b.sweep chiasma/runs/d-eval <s_0..s_9> --worlds D
  --arms O0,O0F,SRF,SXF,S0F,SPFF --caps-d 650,700,800,1000000 --pevict --procs 14
- Verdict: python -B -m chiasma.e1b.verdict_d chiasma/runs/d-eval/rows.jsonl
- Budget: dev-6 cost 4.57 core-hours for 250 runs, most of it SPFF. This run is 240
  runs, about 5 core-hours, inside MWO-0004 R2.

## Endpoint

err_CDE (probe errors summed over the C, D and E checkpoints), as defined in
chiasma/runner.py. "A beats B" in a cell means A's err_CDE is strictly lower on at
least 8 of 10 paired seeds. Ties do not count.

## Claims and verdicts

Instrument check (must hold, or every verdict is NOT_VERIFIED):
- I1: at cap 10^6, O0F's err_CDE equals O0's on 10/10 seeds (factoring is lossless).
- I2: every capped row has bytes_peak <= cap.

D1 (compression of the positive mesh keeps knowledge): O0F beats O0 at caps 650 and 700.
D2 (compression of the negative mesh beats raw and counterfeit failure memory): O0F
beats SRF AND O0F beats SXF at caps 650 and 700.

Per claim: PASS = holds at both deciding caps; FAIL = holds at neither; MIXED = holds
at exactly one; NOT_VERIFIED = a contrast lacks 10 paired seeds, or I1/I2 fails.

Secondary (reported, never deciding): every contrast at cap 800; O0F vs S0F; SPFF vs
O0F; SRF vs S0F.

## Predictions (written before evaluation seeds exist)

- D1 PASS (dev: 10/10 at 650 and 700).
- D2 PASS, with the risk at cap 700 vs SXF (dev 8/10, the threshold exactly).
- At cap 800, O0F vs O0 is about a tie (dev 5/10).
- SPFF vs O0F is mixed (dev 6-7/10).

## What a verdict would and would not show

PASS on D1 and D2 would show, for this world family only: under a byte budget between
the factored and flat sizes, lossless factoring of the positive mesh and projection of
the negative mesh each beat their uncompressed or counterfeit alternatives at matched
bytes. It would NOT show anything about revision (DEV_NOTES s15), eager seams, 8-16-D
coordinates, evolution, or worlds with noise. Conditions to repeat wherever a verdict is
quoted: PW-D defaults, pevict, caps 650/700, eval seeds from FREEZE_D.json, code at the
frozen blobs.
