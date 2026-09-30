# T-SWAP-REL5 PLAN (frozen by commit before any REL5 simulation)

Thread thr-5df816e9b844, experiment E-ANANKE-W-X (delegated worker; must NOT
edit this file; post-freeze deviations go in its own PLAN_ADDENDUM.md written
before the affected run). Authority: CWO 2026-09-30 ANANKE RESERVE ("analyze
before expanding") + MWO-0004 R2. Cap: 3 CPU core-hours.

## 1 Why (aimed at the claim)
W-W (T-SWAP-REL4, workers/W-W/REPORT.md) chose H2 = REL3 BOOTT with the
resample SD floored, sd*_b := max(sd*_b, sqrt(1/(4K))/sqrt(P)*0.5), and found
it promotable (FLIP/NO_EFFECT power 1.00 at p=.99, P64 K11). But H2's interval
lies inside REL3's and differs only on near-degenerate resamples, which the
REL4 FC grid never produced at the z=+-1/2 boundary truths. H2's false-
certificate (FC) rate where it actually differs from REL3 is untested. This
item tests exactly that before promotion.

## 2 Model (new, stated before simulation)
DEGEN model: pair statistics built from K scored trials per pair where a
fraction d of pairs is deterministic (normal arm all-correct; swap arm
constant) and the rest follow W-Q's realistic coupled model, with the truth
placed exactly at the verdict boundary (z = -1/2 for FLIP, z = +1/2 for
NO_EFFECT; CHANCE at both). Grid: P in {32, 64}, K in {3, 11},
d in {.5, .8, .95}, normal p in {.90, .95, .99}. n = 20,000 per point
(+60,000 where H2 lies in (0.8%, 1.2%]). Seeds: new namespace 0x660.

## 3 Candidates
H2 (the REL4 choice, workers/W-W/swap_rel4.py, unchanged) and H0 (REL3) as
reference. Must-fail control ZW: replace infinite t* by 0 (zero-width
degenerate intervals) -- must FAIL the FC target.

## 4 Decision rule (frozen)
- PROMOTE H2 iff pooled FC <= 1.00% for every verdict at every DEGEN point AND
  the ZW control fails (FC > 1% somewhere; else the model is not probing the
  degenerate region) AND H0's FC <= H2's FC at every point (sanity: H2 is
  nested inside H0).
- If H2 fails at some points: do not promote; record the failing (P, K, d, p)
  region; promote REL3 (H0) instead with the documented high-accuracy power
  blind spot (FLIP/NO_EFFECT NOT_ELIGIBLE when lo99(normal) >= .95, P < 128).
- If ZW does not fail: the check is uninformative; do not promote; report.
No new candidates, no floor tuning, no grid expansion in this item.

## 5 Resources
<= 3 CPU core-hours, Fabric lease skullport:cpu8 if > 2 threads, no GPU,
outputs <= 1 MB.
