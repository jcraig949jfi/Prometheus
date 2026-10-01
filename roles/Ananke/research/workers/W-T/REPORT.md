<!-- DEPOSITED VERBATIM by Ananke for worker W-T; sha256(report)=1a7baa67bd3bc7b9; delimited; see REPORT.provenance.json -->
W-T (E-ANANKE-W-T, T-INS-16, successor of T-INS-11 thr-8c7342a7d513, MWO-0004). Report on how far the first-broadcast latency rule reaches.

WHAT I TESTED
- **Predictors.** I used W-S's P8 and P8any exactly as W-S defined them. The definitions are copied into PLAN.md s2, pointing to W-S posthoc.py and posthoc_summary.py. My copy is wt.p8_features / p8any_of, and it reproduces W-S's rows bit-for-bit (KA-R below).
  - P8 takes the source's (sense_idx[:,0]) earliest cue-bearing emission to the readout. All of those copies arrived by tau → S; all after tau → C; some each way → M (abstain); none → U.
  - P8any reads C iff P8 is C or M, else S.
- **Decision rule (frozen).** A unit REACHES iff P8 decisive lo99 > .90 with coverage ≥ .25, AND P8any strict lo99 > .80.
- **Setup.** M = 256 worlds from assays.world_seeds(0x640, 256), trials 1–11, 99% bootstrap over mirror pairs.
  - PLAN.md was frozen and hashed (sha256 e2b5f7de…d5404580) at 14:13:07Z, before any run at 0x640.
  - A "mixed stratum" is an (offset, phase) with, in W-R's 0x620 data, n(S or C) ≥ 50 and max(fS, fC) < .80. I fixed this rule before looking at 0x640.
- **Units.**
  - (a) Direct-carrier plants on the c16d5231 physics (prog_len raised to 24; RELAY d3, delta 8; sync period 2; fanout 8 over 6 ports; loss .1; direct delay 4 + jitter):
    - P1: the source emits once per trial. This is the primary known-answer plant; P1_J0 is its jitter-off control.
    - PF: first broadcast on PAY0, then decoy re-emissions of the cue on PAY1 that the readout ignores.
    - PL: the readout follows the latest arrivals. This plant must fail.
  - (b) 4781b0a1 (MAJ): 22 mixed strata.
  - (c) 78f3b0ec (follow census): primary units o9q0, o11q1, o14q1, o15q1, plus o10q0 and o10q1.
  - (d) e06701a5 o5q0 (follow census).

RESULTS PER UNIT (99% CIs)
**(a) Plants**

| Plant, stratum | Census | P8 decisive (coverage) | P8any strict | Verdict |
|---|---|---|---|---|
| P1_J1 o4q0 (mixed) | C298 / S246 | 1.00 [1.00,1.00] (.605) | 1.00 [1.00,1.00] | REACHES |
| P1_J1 o5q0 (mixed) | C351 / S297 | 1.00 [1.00,1.00] (.602) | 1.00 [1.00,1.00] | REACHES |
| P1_J1 o4q1 (clean) | C553 / S95 | 1.00 [1.00,1.00] | 1.00 | REACHES |
| P1_J1 o5q1 (clean) | S544 | 1.00 [1.00,1.00] | 1.00 | REACHES |
| PF_J1 o4q0 | — | .844 [.792,.891] | .888 | DOES NOT REACH (decisive) |
| PF_J1 o5q0 | — | .863 [.820,.903] | .904 | DOES NOT REACH (decisive) |

- **P1_J1 detail.** P1_J1 splits are all C, as the plant was built to do; the 95 S pair-trials in o4q1 are no-copy stale cases that P8 abstains on (U).
- **PF_J1 detail.** On pair-trials where a first-broadcast (PAY0) copy reached the readout, P8 decisive is 1.00 [1,1] (n 329 and 390). Every P8 error is a pair-trial where no first-broadcast copy arrived, so the earliest cue-bearing emission P8 used was a decoy.
- **PL_J1.** DOES NOT REACH in o4q0 (.700) or o5q0 (.755); o5q1 is .406.

**(b) 4781b0a1 (MAJ): DOES NOT REACH in 22 of 22 units.**
- P8 decisive accuracy equals its own shuffle in every unit:
  - o0q0–o3q0: .01, because P8 says C (first copies still in flight) while the truth is S.
  - o8q0–o10q0 and o12q1–o13q1: .03–.10.
  - o4q0 .39 [.26,.52]; o5q0 .48; o6q0 .44; o7q0 .30; o14q1 .47; o15q1 .56.
  - o5q1, o6q1, o7q1, o8q1, o9q1: .71–.87, e.g. o7q1 .87 [.82,.92] against a shuffle of .85. These are simply the majority-S rate.
- P8all (secondary: each of the 5 sensors' own first emission) does no better: o5q1 .99 but coverage only .29; elsewhere .02–.92.

**(c) 78f3b0ec: DOES NOT REACH in 6 of 6 units.**

| Unit | P8 decisive (coverage) | P8any |
|---|---|---|
| o9q0 | .481 [.416,.547] (.99) | .485 |
| o11q1 | .567 [.494,.632] | .567 |
| o14q1 | .507 [.437,.575] | .507 |
| o15q1 | .433 [.365,.504] | .433 |
| o10q0 | .567 | — |
| o10q1 | .480 | — |

- All of these equal their shuffles.
- In the clean strata P8 is right at o15q0 (1.00) and o9q1 (.98), but wrong at o11q0 and o14q0 (.015 / .004: it says S, the truth is C).

**(d) e06701a5 o5q0: DOES NOT REACH, and only the P8any part fails.**
- P8 decisive is 1.00 [1.00,1.00] with coverage .525; P8any strict is .734 [.659,.807].
- Split cases go S 74 / C 58, a coin toss. All 304 N pair-trials are split cases.
- The clean o5q1 stratum reaches (S375, P8 1.00).

**What the cue-bearing traffic looks like** (mean per S/C pair-trial; "copies" means cue-bearing copies reaching the readout)
- **e06701a5:** 1.9 copies, all from a single source emission at tau−4. No re-broadcast, no relays. The failure is only in the split outcomes.
- **78f3b0ec:** 5.6–6.1 copies, all from the source (relay share 0). The source emits on about 4.4–5 distinct ticks, so 78% of source copies are re-broadcasts. The first emission is at about t0+1 and lands long before the swap, which is why P8 says S nearly everywhere.
  - POST HOC (posthoc.py): no emission-index predictor (E1–E6) works at o9–o11.
  - "Latest source emission with te ≤ tau" (ELAST) is 1.00 [1,1] at o15q1 and .751 at o14q1. So late in the trial the readout follows the latest broadcast, not the first.
- **4781b0a1:** about 30 copies per pair-trial, 7–9 of them in flight at tau. 79% of the first sensor's copies are re-broadcasts.
  - POST HOC (posthoc_maj.py): the 81% "non-source" share comes entirely from the other 4 sensors (true relays 0): about 6 copies from sensor 0 and about 25 from the other sensors.
  - Traffic counts are the same across S, C and N. The readout integrates many broadcasts from 5 sensors, so no single-emission timing rule applies.

KNOWN-ANSWER CHECKS (+ must-fail inputs)
All pass.
- **KA-R:** my P8 reproduces W-S posthoc_c16d5231_ns632.json on 584 of 584 rows (pairs < 32, M = 64 prefix): keyset, pattern, P8, n1_held, n1_flight and te1_rel all identical. Must-fail: against the ns 0x630 file, the keysets differ and 282 of 482 common rows mismatch.
- **KA-P1:** REACHES in both mixed strata with decisive 1.00 (point ≥ .99). Must-fail: shuffled first-broadcast labels drop decisive accuracy to .465 and .467 (≤ .65). Clean strata are 1.00.
- **KA-J0 (jitter off):** zero M predictions; in every stratum the decisive S/C pair-trials are a single class; decisive 1.00.
- **KA-PF:** decisive 1.00 on pair-trials that received a first-broadcast copy; 100% of errors are on pair-trials that received none (61/61, 62/62, 62/62, 61/61).
- **KA-PL (must-fail plant):** DOES NOT REACH in both mixed strata; o5q1 decisive .406.

DISAGREEMENTS
- **W-S:**
  - The rule is validated in principle: P8 is exact on a direct carrier (KA-P1).
  - But it does not generalise. It fails when the first cue-bearing emission is not the causal one. Decoy re-broadcasts break it whenever the first broadcast misses the readout (PF, about 11% of pair-trials).
  - Its reach stops at W-S's three RELAY cells. It does not hold in MAJ, in the larger-delta cell 78f3b0ec (where the readout follows later, and at the end the latest, source broadcasts), or for split outcomes in e06701a5.
  - W-S's R3 finding that split outcomes are c16d5231-specific holds: in e06701a5 splits are a coin toss.
- **W-R:** the 78f3b0ec phase effects at o9–o15 are real (mixed thirds replicate at 0x640). They are not first-arrival jitter; the late-offset (o15) mixture tracks the latest source emission.
- **W-P:** MAJ phase effects at every offset replicate. N is concentrated in one phase: q0 at o4–o8, q1 at o10–o15. But no first-broadcast timing explains them. MAJ traffic is dense and multi-sensor, which confirms W-S's development observation.
- **Brief framing:** "one latency-jitter draw on the first broadcast" is a property of specific cells, not a general law of the update-clock phase.

PYTEST
`PYTHONDONTWRITEBYTECODE=1 python -m pytest roles/Ananke/research/workers/W-T/test_wt.py -q -p no:cacheprovider` → 10 passed, RC=0 (logs/pytest.log).

LEASE AND COMPUTE
- Lease lse-33d3f78d0178 on skullport:cpu8, taken `--as Ananke` at 14:13:07Z. Released at 14:26:09Z with `--lease --token`, which printed RELEASED; `python -m fabric lease status` then returned [].
- 4 processes × 2 threads, CPU only, no GPU.
- PIDs were logged at launch (7300, 20312, 7324, 15596). Win32_Process shows 0 W-T processes left, and no background tasks remain.
- Compute was about 0.9 core-hours, against 16 allowed. Wall time was about 25 minutes.
- No git writes, no .pyc files, no edits outside W-T/.

FILES (all under `F:/Prometheus-worktrees/ananke-base-role/roles/Ananke/research/workers/W-T/`)
- PLAN.md (frozen), LOG.md (A0–A19; A13, A15 and A17 are labelled POST HOC)
- Code: wt.py (plants and runner), summ.py (decision rule and descriptors), posthoc.py, posthoc_maj.py, test_wt.py, launch.sh
- out/summary_{PLANT_P1_J1, PLANT_P1_J0, PLANT_PF_J1, PLANT_PL_J1, 4781b0a1, 78f3b0ec, e06701a5}.{txt,json}
- out/rows_*.npz, out/meta_*.json, out/posthoc_summary_78f3b0ec.*, out/posthoc_maj_traffic.json, out/*dev* (development runs)
- logs/

PROPOSED FOLLOW-UPS
- A causal-emission version of P8: identify the carrier by cue-flipping each source emission separately, rather than taking the earliest cue-bearing one.
- For 78f3b0ec o9–o11: test whether the mixture is the source's emission clock (site → flight hand-off) rather than arrival timing.
- For MAJ: a per-sensor carrier census.
