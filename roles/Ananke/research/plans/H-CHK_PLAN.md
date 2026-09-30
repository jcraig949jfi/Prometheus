# H-CHK PLAN: three decisive checks from the inference harvest (frozen by commit before any run)

Authority: operator inference-harvest directive 2026-09-30 (bounded tests allowed; no campaign).
Worker: H-CHK (delegated). Cap: 3 CPU core-hours total, CUDA_VISIBLE_DEVICES=-1, device="cpu", no GPU.
Source of the questions: harvest/H-SCI/REPORT.md (12a, 12d, claim 10). The worker must NOT edit this file;
post-freeze deviations go in harvest/H-CHK/PLAN_ADDENDUM.md before the affected run.

## C1: does a noisy count threshold reproduce 4781b0a1's "joint carrier" signature?
- Plant: 5 sensors as direct neighbours of the readout, W-V plant physics adjusted to the champion's
  delivery (loss .1, fanout-8 sampled over 6 ports, sync period 2, jitter as the champion's physics).
- Sensors re-emit their rectified cue on payload 1; the readout computes S0 := sum(arrivals in its last
  wake window) - theta with theta fixed a priori (the smallest value for which majority accuracy is >= .7
  at those settings, computed on seeds disjoint from the test).
- Run it through W-P's truth-table classifier (workers/W-P/tt.py, ana.py) and W-V's per-sensor
  classifier (workers/W-V/wv.py, ana.py) at the offsets W-P/W-V reported.
- Frozen reading:
  - REDUCES iff the plant shows (i) AND/OR-dominated N in one clock phase and (ii) DISTRIBUTED-NONMAJ
    (pivotality contrast D_piv < .3) under W-V's frozen classifier.
  - DOES NOT REDUCE iff the plant reads MAJORITY (D_piv > .7) or shows no N.
  - Otherwise PARTIAL.

## C2: does W-V's "not a majority" survive a lossy majority control?
- Re-run W-V's PMAJ majority plant at the champion's loss .1 and fanout-8 sampling (everything else as
  W-V), with W-V's frozen classifier.
- Frozen reading:
  - W-V's champion verdict is ROBUST iff PMAJ still reads MAJORITY (D_piv > .7).
  - It is WEAKENED-CONFIRMED iff PMAJ's D_piv < .3 under these settings (loss and sampling alone produce
    the champion's signature).
  - Otherwise PARTIAL.

## C3: does the mirror swap confuse an integrator with a lag-k store?
- Specimens: P1S (W-N plants_rel, clean lag-1 store) and the W-L n-back integrator champions n1_s0 and
  n2_s2 (W-L/W-N).
- Two swap modes at the same tick (k*Pd - 1, SINGLE trial):
  - (a) the mirror swap of S as in W-N;
  - (b) a single-cue-twin swap, where world B differs from A only in cue k (twin_trace semantics) and S is
    exchanged between A and B.
- Statistic: z = (s - .5)/(a - .5) with W-N's paired CI, M = 512.
- Frozen reading:
  - CONFUSION CONFIRMED iff the integrators read z <= -.95 under (a) AND |z| <= .5 under (b), while P1S
    reads z <= -.95 under both.
  - NOT CONFIRMED iff the integrators read similarly under both modes.
- Must-fail input: P1S under (b) with the twin differing at cue k-1 instead of k must NOT read z <= -.95.

## Known-answer gate (COMMON_RULES_ARC3 s5)
Before any champion run: hold_latch and echo_hold through the reused classifiers reproduce their
workers' published known answers. If not, stop and report.

## Report
harvest/H-CHK/REPORT.md in the final message (delimited), with each frozen reading, CIs, compute used, and
any addendum items.
