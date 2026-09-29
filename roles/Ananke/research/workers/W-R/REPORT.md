<!-- DEPOSITED VERBATIM by Ananke for worker W-R; sha256(report)=7b8beb2ab247b2f6; delimited; see REPORT.provenance.json -->
W-R REPORT: T-INS-9, the SINGLE carrier-swap census split by update-clock phase
(E-ANANKE-W-R, successor of T-INS-6/8, thr-8c7342a7d513, MWO-0004)

WHAT I TESTED

1. Which physics have phase-dependent updates. I read this from the engine code and the physics dials, not from results.
   - engine.py step 3 (WAKE): in sync mode every site is awake at tick t exactly when t mod update_period == 0. This is one global clock.
   - In async mode, waking is a per-site hash of (world seed, t, site) compared with update_p. It is memoryless and has no period.
   - Asleep sites do not run their program and do not emit, but their inbox (Acc_sum/Acc_cnt) keeps accumulating. In period p, a delivered packet can wait up to p-1 ticks in a SITE array.
   - There is no other periodic update. The mailbox slot t mod LM is only ring indexing, decay runs every tick, and the rng streams are hashed.
   - Result (out/physics.json): 8 of 9 specs are sync with update_period 2: 2dccdaa5, c16d5231, 8c37f32e, e06701a5, 78f3b0ec, 4781b0a1, E1, E2.
   - 369f5a5b is async (update_p .8). It is the only negative control among the census cells.
   - Trial period Pd is odd for the 7 cells (11 or 19), so the trial onset t0 = k*Pd alternates parity across trials 1..11 (6 trials of one parity, 5 of the other).
   - E1 (Pd 12) and E2 (Pd 16) have even trial periods, so all their trials share one phase. For them one stratum is always empty.

2. Design (PLAN.md, frozen before any census run). Everything uses the SINGLE-trial arms.
   - Worlds: M = 256, from assays.world_seeds(0x620, 256).
   - Offsets 0..ro_off-1, trials 1..11.
   - Phase: q = (t0 + o) mod 2, the parity of the tick after which the swap is applied. q = 0 means the swap tick was a wake tick. For async physics q is a pseudo-parity that splits the trials the same way.
   - Classification: the frozen census() and classify() are applied unchanged (MIN_ELIGIBLE 20, MIN_IDENTITY .90) to the pooled trials, to q = 0 and to q = 1.
   - Phase-difference statistic: dX = fX(q1) - fX(q0) for X in {S, C, N}, with a 99% pair bootstrap (2000 draws, the same resampled pairs for both strata).
   - PHASE EFFECT at an offset: both strata have >= 20 eligible pair-trials, and some dX has a 99% CI excluding 0 with |dX| >= .10.
   - For a pooled MIXTURE, UNRESOLVED or NEITHER reading:
     - RESOLVES = both phases SITE or CHANNEL.
     - PARTLY = exactly one phase SITE or CHANNEL.
     - STAYS MIXED = no phase SITE or CHANNEL.
   - For the abstainers 78f3b0ec and e06701a5 the frozen census is UNDEFINED (0 eligible pairs). I report the W-M D1 follow census for them as secondary, labelled.

3. Runner (fork.py). It runs one normal pass, forks the state at each trial's first swap tick, and runs only to that trial's readout. It is checked bit-identical to lens_swap.run_arms (KA-F below). This made M = 256 affordable: about 3 core-hours in total.

RESULTS (M = 256, ns 0x620; fractions with 99% pair-bootstrap CIs; n = eligible pair-trials; full tables for every offset are in out/summary.txt)

Answer to the question. Stratifying by phase changes classifications in every sync period-2 cell whose trials cover both phases.

| Cell | Offsets with a PHASE EFFECT (all change class) |
|---|---|
| 2dccdaa5 | o0, o5 |
| c16d5231 | o0, o4, o5 |
| 8c37f32e | o0, o5 |
| 4781b0a1 | 16 of 16 (15 change class) |
| e06701a5 (follow census) | o0, o5 |
| 78f3b0ec (follow census) | o0, o9, o11, o14, o15 |

Effect sizes are |d| up to .53-.83 at o >= 1. Every flagged split is the most extreme of all 462 possible 5/6 trial splits (exact permutation p = .002, the floor). Dropping trial 1 or trial 11 changes no effect set.

Offsets that are pooled SITE or CHANNEL in the RELAY cells keep that class in both phases. The exception is 4781b0a1: o12 and o13 read CHANNEL pooled, but one phase is UNRESOLVED (C .69-.71, N .27-.29).

Pooled mixed readings:

| Group | RESOLVES | PARTLY | STAYS MIXED |
|---|---|---|---|
| Frozen census, period-2 cells with both phases | 0 | 11 | 6 |
| Follow census, abstainers | 0 | 5 | 1 |

- Frozen census, PARTLY (11): 2dccdaa5 o5; c16d5231 o4, o5; 8c37f32e o5; 4781b0a1 o1-4, o11, o14, o15.
- Frozen census, STAYS MIXED (6): 4781b0a1 o5-10.
- Follow census, PARTLY (5): e06701a5 o5; 78f3b0ec o9, o11, o14, o15.
- Follow census, STAYS MIXED (1): 78f3b0ec o10, which is UNRESOLVED in both phases with no effect.
- Not evaluable: E1 and E2 (o3, o7 MIXTURE with one stratum empty) and the async control (14 UNRESOLVED readings, all staying mixed).

The dominant pattern: in the RELAY cells, the pooled MIXTURE is one clean phase plus one phase that is itself a roughly 50/50 S/C mixture.

| Cell / offset | Pooled | q1 | q0 |
|---|---|---|---|
| 2dccdaa5 o5 | MIXTURE S .66 [.61,.69] C .32 | SITE S 1.00 [1.00,1.00] (n310) | MIXTURE S .47 [.41,.53] C .49 [.44,.55] (n573) |
| c16d5231 o5 | MIXTURE S .69 C .31 | SITE 1.00 (n550) | MIXTURE S .44 [.39,.49] C .56 [.51,.61] (n661) |
| c16d5231 o4 | MIXTURE S .28 C .71 | CHANNEL C .85 [.81,.88] | MIXTURE S .45 C .55 |
| 8c37f32e o5 | UNRESOLVED S .57 C .23 N .18 | SITE .99 [.97,1.00] (n361) | UNRESOLVED S .33 C .36 N .28 (n634) |

- Pattern o0: pooled IDENTITY-BROKEN becomes CHANNEL in q0 (SITE for 78f3b0ec) and stays IDENTITY-BROKEN in q1. The second cue tick falls on an asleep tick in q0, so it is never read and identity holds. This matches the plant derivation.
- 2dccdaa5 and c16d5231 were replicated post hoc at ns 0x621 with identical classes (e.g. 2dccdaa5 o5 q1 SITE 1.00, q0 MIXTURE .51/.45).

4781b0a1 (MAJ):

| Offset | q0 | q1 |
|---|---|---|
| o1 | UNRESOLVED | SITE .83 [.78,.87] |
| o2 | UNRESOLVED | SITE .80 [.76,.85] |
| o3 | UNRESOLVED | SITE .87 [.83,.91] |
| o4 | NEITHER N .68 [.63,.74] | SITE .87 [.83,.90] |
| o5 | NEITHER N .63 | UNRESOLVED S .78 |
| o6 | NEITHER N .78 | UNRESOLVED S .65 |
| o7 | NEITHER N .62 | UNRESOLVED S .66 |
| o8 | NEITHER N .64 | UNRESOLVED S .50 |
| o9 | UNRESOLVED C .65 | UNRESOLVED S .48 |
| o10 | UNRESOLVED C .59 | NEITHER N .53 |
| o11 | CHANNEL .95 [.93,.97] | UNRESOLVED N .48 |
| o12 | CHANNEL .96 | UNRESOLVED |
| o13 | CHANNEL 1.00 | UNRESOLVED |
| o14 | CHANNEL 1.00 [1.00,1.00] | NEITHER N .65 [.59,.71] |
| o15 | SITE 1.00 | NEITHER N .64 [.57,.70] |

- The N fraction concentrates in one phase at every offset, but that phase is never clean. The other phase is clean only at o1-4 and o11-15.

Follow census (secondary):
- e06701a5 o5: q1 SITE 1.00, q0 NEITHER .55 [.48,.62].
- 78f3b0ec o9, o11, o14, o15: one phase is clean (SITE 1.00, CHANNEL 1.00, CHANNEL 1.00, SITE 1.00). The other phase is a near-thirds blend (S .32-.37, C .32-.37, N .30-.31). The same blend holds at o10 in both phases.

E1 and E2 (single phase by construction):
- The q = o mod 2 stratum equals the pooled census exactly, and the other stratum is UNDEFINED (P1 held).
- The MIXTUREs at o3 and o7 all lie in q1: E2 o3 S .45 [.42,.48] C .48; E2 o7 S .47 C .52; E1 o3 and o7 are similar.
- So they cannot be phase pooling.

Negative control (369f5a5b, async):
- Classes are identical in both strata at all 16 offsets: UNRESOLVED at o1-14, SITE at o15, IDENTITY-BROKEN at o0.
- The frozen rule FAILED by one offset: PHASE EFFECT at o1 (dN -.15 [-.25,-.04]) and o3 (dN -.14 [-.23,-.03]), where at most 1 was allowed.
- Post hoc (labelled): it does not come from trial 1 or trial 11. The exact split test gives p = .006 and .004.
- The replication at ns 0x621 (M = 256) has 0 of 16 effect offsets and no class change. I read the 0x620 flags as sampling: trial-level variation across 5-6 trials per stratum is not covered by the pair bootstrap.
- For scale: the control's |d| is at most .15, against .53-.83 in the period-2 cells.

Prediction scorecard:

| Prediction | Result |
|---|---|
| P1 (E1/E2 single-phase bookkeeping) | held |
| P2 (negative control shows no effect) | FAILED the frozen rule at 0x620; clean at 0x621 |
| P3 (4781b0a1: effect at >= 8 of o1-15; o14/o15 at least partly resolve; 0-2 full resolutions) | held: 15 of 15, o14/o15 PARTLY, 0 full |
| P4 (>= half of the pooled MIXTUREs in period-2 cells RESOLVE) | FAILED: 0 resolve; all are PARTLY (one phase clean, the other still a within-phase mixture) |
| P4b (pooled SITE/CHANNEL offsets keep their class) | held for the RELAY cells, failed for 4781b0a1 o12/o13 |
| P5 (4781b0a1 mixed readings stay mixed or only partly resolve) | held |

KNOWN-ANSWER CHECKS

| Check | Result | Must-fail input, shown to fail |
|---|---|---|
| KA-F: fork runner vs lens_swap.run_arms (M = 16, all offsets, trials 1 and 2) | Bit-identical (per-trial score and raw S0 of every arm, plus the normal arm): PLANT2 52/52 arms, 369f5a5b 64/64, 4781b0a1 64/64 | Forking one tick late: 1 mismatched arm (PLANT2) and 4 (each cell), all at o0 → not identical |
| KA-P: echo_hold under c1b_echo_physics with update_period 2 (HOLD gap 11, iti 3, Pd 17), predicted by hand in PLAN s4 | PASS. The discordant offsets are exactly {0, 5, 6, 11}. All 26 per-phase classes match the hand table (o5: q0 CHANNEL 1.00, q1 SITE 1.00; o6 and o11 likewise). o5, o6 and o11 are pooled MIXTURE (fS .45-.55) and RESOLVE. Normal accuracy is 1.00 in both phases. | (a) The same plant with update_period 1: no discordant offset, o5/o6 read CHANNEL, so checks i-iii fail. (b) Phase labels randomly permuted: discordant set {6}, so checks i-iii fail. Caveat: a shuffle of 11 labels leaves most labels in place, so this is a weak must-fail. |
| KA-N: the no-phase-effect rule applied to known positives | Must fail on 4781b0a1 and PLANT2: it does (16 and 4 effect offsets). It passes on PLANT1. | — |
| KA-B: pytest bookkeeping | A synthetic phase-locked S/C table reads pooled MIXTURE, q0 SITE, q1 CHANNEL, and RESOLVES | Labels shifted by one tick swap the per-phase classes (asserted). A phase-independent 50/50 mixture reads MIXTURE in both phases with no effect (asserted). |

DISAGREEMENTS

1. With W-M (REPORT.md). Its pooled MIXTUREs in the period-2 RELAY cells (2dccdaa5 o5, c16d5231 o4/o5, follow 78f3b0ec o9/o14) are partly update-clock pooling.
   - One phase is 100% SITE or CHANNEL. For example, c16d5231 o5 "fS .67" is a 100%-SITE phase pooled with a 44/56 phase.
   - The per-trial S/C mixture W-M found is real, but it lives inside one phase only. The pooled fS/fC values are phase-weighted blends.
   - W-M's E2 reading (a per-trial S/C mixture at lag -6) survives here, because E2 is single-phase.

2. With W-P. Numbers agree within CIs:
   - o14: C 1.00 in q0 vs N .65 in q1 (W-P: 1.00 vs .70).
   - o15: S 1.00 vs N .64 (W-P: 1.00 vs .64).
   - o4: N .68 vs .13 (W-P: .73 vs .12).
   I extend it: 4781b0a1 has a phase effect at every offset, and even the pooled CHANNEL offsets o12/o13 hold an UNRESOLVED phase. W-P's clean phase is never matched by a clean other phase.

3. With the corrections register (CORRECTIONS_2026-09-29_SWAP_AUDIT / W-O corrections_WI.csv).
   - c16d5231 o5 M->S and 8c37f32e o5 J->S: "S" is correct in one clock phase only. The other phase is 44/56 S/C (c16d5231) or S .33 / C .36 / N .28 (8c37f32e).
   - 4781b0a1 o5 J->S: S reaches .78 only in q1; q0 is NEITHER .63.
   - 4781b0a1 o11 M->C, o14 J->C, o15 J->S: correct in q0 only; q1 is UNRESOLVED or NEITHER.
   - 369f5a5b o2 J->S is not supported: UNRESOLVED fS .50 in both phases (as W-P said). o14 reads UNRESOLVED fS .74 at 0x620 but SITE at 0x621, so it is threshold jitter.
   - On period-2 cells, single letters should be phase-indexed.

4. With my own frozen plan: P2 (negative control) and P4 (MIXTUREs resolve) failed, as above.

5. With W-I: I did not read W-I's reports, only the W-I letters listed in the W-O corrections file, so there is no direct disagreement to report.

PYTEST

`python -m pytest roles/Ananke/research/workers/W-R/test_fork.py -q -p no:cacheprovider` (with PYTHONDONTWRITEBYTECODE=1): 6 passed in 8.86 s, RC=0 (logs/pytest.log).

LEASES AND HYGIENE

- Fabric lease `lse-be98c3489db7` on skullport:cpu8, taken `--as Ananke`, acquired 12:23:35Z and renewed at 12:47Z.
  - RELEASED at 12:56Z with `--lease --token`; the command printed RELEASED.
  - `python -m fabric lease status` then listed only Aether's buckkeep:cpu8 lease.
- Peak use was 4 processes × 2 threads. PIDs were checked through Win32_Process before each launch. No GPU.
- Total compute was about 3.3 CPU core-hours, against the 16 allowed. Wall time was about 50 minutes.
- No git writes. The only side effect outside W-R: probe_physics.py ran before PYTHONDONTWRITEBYTECODE was set and rewrote W-M/__pycache__/apply.cpython-312.pyc. That is a git-ignored bytecode cache, not a record, and I left it in place.
- No W-R processes are running (Win32_Process count 0).
- Context contamination (logged in LOG A0): per the brief, I read W-P's RESULTS and DISAGREEMENTS and W-M's report and summary before writing PLAN.
- LOG A6 corrects clock times I had estimated in A2-A5 instead of reading them from the clock.

FILES (all under F:/Prometheus-worktrees/ananke-base-role/roles/Ananke/research/workers/W-R/)
- PLAN.md, LOG.md (A0-A18)
- Code: fork.py (runner, phase bookkeeping, stratified census), specs.py, stratify.py, probe_physics.py, ka_fork.py, summarize.py, test_fork.py
- Post-hoc (labelled): posthoc.py (leave-trial-out), posthoc_split.py (exact split test), followdiff.py (follow-census phase effect)
- out/physics.json
- out/strat_<spec>.json and out/raw_<spec>.npz for the 9 specs plus PLANT1 and PLANT2
- Replications: out/strat_{369f5a5b,2dccdaa5,c16d5231}_ns0x621.json
- out/ka_fork_*.json, out/posthoc_*.json, out/split_*.json, out/followdiff_*.json
- out/summary.txt and out/summary.json (the authoritative tables)
- logs/*.log

Proposed follow-ups
- Index every carrier-swap class on sync period-p physics by swap-tick phase, and report the pooled class only as a weighted summary.
- Re-run E2 with iti 3 (odd Pd) to see whether its o3/o7 mixtures persist in both phases.
- Find what makes the "mixed" phase mixed in the RELAY cells (per-trial jitter of the arrival tick relative to the wake tick?). Split it by the delivery tick of the carrier packet.
- Add a trial-level (not only pair-level) resampling to phase-difference CIs. The 0x620 control flags show that pair-only CIs are anti-conservative for 5-6 trials per stratum.
