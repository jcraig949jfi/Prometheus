+==============================================================================+
| REVIEW PACKET -- AETH-V2B-AIM01: is Aether's frozen reachable set caused by   |
| writers' fixed AIM, or by the initial soup?                                  |
| Author: Aether (role seat), host SPECTREX5 / M2, RTX 5060 Ti 16 GB           |
| Date: 2026-10-06                                                             |
| For: HITL operator + external reviewers                                      |
| Status: COMPLETE. Frozen label REAIM_NONTRIVIAL_CANDIDATE +                  |
|         INITIAL_GEOMETRY_DOMINANT; post-hoc self-attack weakens "nontrivial" |
| Self-contained: no repo access needed; every load-bearing number is inline.  |
+==============================================================================+

-----
0. SUMMARY
-----
ER01 found that Aether's medium freezes in the same ~37% reachable set under
every energy economy. AIM01 tests two explanations at once:
 (a) the initial soup's writer/aim geometry sets that set;
 (b) writers keep a fixed aim (a target changes only if another writer
     overwrites the aim fields).
Design: 2 laws x 3 initial WRITE densities x 8 paired seeds. 512^2 x 30,000
ticks, perturbation OFF, the historical B_balanced energy.
 L0 = aeth01.v1.
 L1 = aeth01.reaim1: a writer that wins its contest advances its own direction
      by 1 (arg0 += 1).

Findings:
 1. (a) is true under the historical law. Reachable support scales with
    initial WRITE density: 0.194 / 0.374 / 0.532 at 25/50/75%. 92-96% of all
    sites that ever change lie inside the initial writers' aim support. The
    ER01 invariant was invariant to energy, not to initial conditions.
 2. (b) is causal. Re-aim expands the non-bookkeeping ("EFFECT") reachable
    support by +0.37 / +0.45 / +0.39. 8/8 seeds at every density. It persists
    to 30k ticks, and 39-54% of late change is outside the initial support.
    Measured on fields the law never touches (post-hoc), the expansion is
    still +0.31 / +0.42 / +0.41.
 3. The frozen rules say the dynamics are NONTRIVIAL (novelty 0.32-0.34). The
    seat's own post-hoc attack says this rests mostly on an instrument
    artifact. On non-AIM fields, novelty is 0.099-0.105, at the 0.10
    triviality floor (L0 0.075): ~90% of late changes revisit a recently held
    state.
Seat reading: AIM is causally implicated; the opened medium is mutable;
whether its dynamics are richer than spatially widened flicker is NOT
established.

-----
1. WHAT WAS BUILT, AND WHAT WAS COMMITTED BEFORE MEASUREMENT
-----
 - reaim1 is a thin wrapper on the frozen aeth01.v1 GPU kernel. Contest winners
   are read from the kernel's own observer side channel, then arg0 += 1 (mod
   256; direction +1 mod 4) for every winning source. The exception: if the
   source's own arg0 was written that tick, the written value stands.
 - Proof that the instrumentation does not change dynamics: L0 with the
   observer is bit-identical to the ER01 runner (no observer). CPU == GPU for
   all 12 law x density x seed fixture cells.
 - Paired densities: same rng stream. Only the opcode of added writers differs;
   WRITE sets are nested (verified per seed).
 - RAW vs EFFECT: EFFECT reads arg0 as (arg0 - #re-aims) mod 256, so the law's
   own counter never counts.
    * Known answers pass: STATIC, FIXED_FLICKER, EXPANDING_SUPPORT,
      AIM_BOOKKEEPING_ONLY (RAW moves, EFFECT exactly 0), and bookkeeping plus
      a real write.
    * Gate: no EFFECT change without an executed write.
 - Two capped flights (Flight 1 6 min, Flight 2 34 min). Preregistration frozen
   at 1ec63c053 before production. Thresholds come from the order (0.05, 2 of
   3 densities, 7 of 8 seeds) or from ER01's frozen rules. Flight raw numbers
   were seen before the freeze (disclosed); rule outputs were not.

-----
2. WHY IT MATTERS
-----
TH-009 asks for a medium that rewrites itself. ER01 removed energy as the cause
of freezing. If the soup sets the reachable set, the frozen medium is partly an
initial-condition artifact. If fixed aim does, one law fact pins the medium. In
fact both are true, and they are one mechanism.

-----
3. GATES AND TECHNICAL
-----
 - 49/49 units rc=0. Run 01:15:53Z-06:38:34Z (5.38 h; projected 6.0 h).
 - Gates:
    * subset_violations 0 everywhere;
    * L0 RAW == EFFECT;
    * one table hash;
    * determinism: dup_L1D50_s0 bit-identical (final digest and full series);
    * continuity: L0 D50 late turnover 0.002364 vs ER01 0.002393 (-1.2%),
      frozen_strict 0.9881 vs 0.9880, ever_changed 0.3735 vs 0.3733.
 - Finite size (Flight 2, D50): L1 at 512^2 vs 1024^2 gives ever_changed 0.8203
   vs 0.8199.

-----
4. RESULTS (production, EFFECT, medians of 8 seeds)
-----
                         L0 D25  L1 D25  L0 D50  L1 D50  L0 D75  L1 D75
  init target support    0.228   0.228   0.415   0.415   0.565   0.565
  ever_targeted (site)   0.195   0.569   0.375   0.824   0.534   0.927
  ever_changed EFFECT    0.194   0.567   0.374   0.821   0.532   0.924
  ever_changed RAW       0.194   0.682   0.374   0.921   0.532   0.987
  late frozen_strict     0.9966  0.9330  0.9881  0.8264  0.9765  0.7433
  late turnover EFFECT   .000657 .009161 .002364 .025694 .004752 .040543
  late turnover RAW      .000657 .095551 .002364 .165686 .004752 .211983
  persistence            1.001   1.000   1.001   1.000   1.000   1.000
  late chg outside init  0.002   0.543   0.008   0.466   0.016   0.391
  changed inside init    0.962   -       0.938   -       0.924   -
  novelty (EFFECT)       0.078   0.337   0.077   0.331   0.076   0.322
  periodic p<=16         0       0       0       .0001   0       .0002
  arg0 share late chg    0.25    0.44    0.25    0.42    0.24    0.39
 - Paired L1-L0, 8/8 seeds favouring L1 at every density:
    * d ever +0.372 / +0.447 / +0.393;
    * d frozen -0.064 / -0.162 / -0.233;
    * d target support (site-field) +0.136 / +0.231 / +0.284.
 - Support saturates (99%) within 50 ticks in every cell.
 - Bookkeeping: 90% / 84% / 81% of RAW late movement is the re-aim itself.
 - ER01 comparator: free-compute / rich-rain flicker had turnover 0.0075 /
   0.0059 with support 0.373. L1 D25 has similar EFFECT turnover (0.0092), lower
   non-AIM turnover (0.0051), and support 0.567 (non-AIM 0.463). Reachability is
   not explained by activity.

-----
5. POST-HOC SELF-ATTACK (not preregistered; it does not change the label)
-----
Suspected artifact. A writer whose arg0 a neighbour keeps resetting to the same
raw value, while it re-aims in between, makes an EFFECT change at every reset.
The EFFECT value drifts with the re-aim count, so the change looks novel while
the raw byte cycles.

Probe: opcode, arg1 and payload only (untouched by the law). 512^2 x 5000 ticks
(stationary from tick 50), 2 seeds per cell (they agree within 0.004).
                         L0 D25  L1 D25  L0 D50  L1 D50  L0 D75  L1 D75
  ever changed, non-AIM  0.150   0.463   0.296   0.716   0.436   0.846
  late turnover non-AIM  .00051  .00507  .00180  .01484  .00358  .02472
  late frozen non-AIM    0.997   0.968   0.991   0.911   0.982   0.858
  novelty non-AIM        0.074   0.100   0.078   0.103   0.078   0.104
  arg0 resets to recent  0.92    0.89    0.92    0.89    0.92    0.89
  raw value (share)

=> The support expansion survives entirely. The nontriviality margin does not:
   novelty sits on the 0.10 floor and is only ~1.3x L0's flicker level.

-----
6. INCIDENTS / INSTRUMENT DEFECTS
-----
 - PREREGISTRATION DEFECT: the frozen attack measured novelty on the EFFECT
   state, which includes the subtracted arg0. The subtraction removes the
   counter but inflates novelty in that field. It should have been measured on
   non-AIM fields. The defect is recorded, not repaired retroactively; the
   frozen label is reported as computed.
 - None operational: no reruns, no terminations. The GPU stayed 60-70 C.

-----
7. WHAT THIS DOES AND DOES NOT ESTABLISH
-----
DOES:
 - Under aeth01.v1 the reachable set is set by the initial aim geometry
   (INITIAL_GEOMETRY_DOMINANT).
 - Fixed aim is the mechanism pinning it: one law change (re-aim) breaks it
   robustly, persistently, at every density, in non-AIM fields too.
DOES NOT:
 - Establish that the opened medium's dynamics are richer than flicker.
 - Establish content transport, computation, heredity, or organization.
 - Hold beyond B_balanced energy, P0, a 512^2 lattice, and this initial family
   (densities aside).

-----
8. DECISION / RECOMMENDATION
-----
Seat lean: treat AIM as CONFIRMED causal for frozen support, and treat
nontriviality as OPEN.

Before the order's content-persistence step (s27), run ONE preregistered,
production-scale MEASUREMENT with no physics change, on the existing L1:
 - Is L1's non-AIM activity richer than a turnover-matched flicker null (ER01
   R1/R2 re-measured on the same non-AIM instrument)?
 - Use 16- and 64-tick novelty memories and unique-states-per-site over a long
   window.
If it is richer: proceed to the content test. If not: the next physics is a
richer retargeting rule (not faster re-aim), per s27.

-----
9. QUESTIONS FOR THE REVIEWER (try to disagree)
-----
 Q1. Is EFFECT = arg0 - #re-aims the right subtraction at all? It cleanly
     zeroes the counter, but as shown it manufactures novelty when a writer is
     reset. Would "exclude arg0 entirely" have been the right primary channel,
     at the cost of missing genuine arg0 writes?
 Q2. Does re-aim smuggle in support by definition? A rotating writer
     necessarily targets more neighbours (ever_targeted rises), and
     P(change | new target) is ~0.99 in BOTH laws, so changed support may
     follow targeted support almost mechanically. Is "support expanded" then
     just "aim expanded", restated?
 Q3. Is non-AIM novelty 0.10 vs L0's 0.075 trivial or not? Neither the frozen
     rule nor this packet has a calibrated null for "richer than flicker" at
     matched turnover.
 Q4. The density pairing changes only which sites start WRITE. Is that a fair
     manipulation of "initial geometry", given that it also changes writer
     count (and so activity) proportionally?
 Q5. Should the preregistered label (NONTRIVIAL_CANDIDATE) be formally
     superseded given a known instrument defect, or left as recorded with the
     caveat, as done here?

-----
10. ARTIFACTS
-----
Branch aether/mwo0001-2026-09-28; result eee3d9003; freeze 1ec63c053.
 - Order: roles/Aether/prompts/2026-10-05_aim01/
 - Aether/V2B/AIM01/:
    * RESULT.md, PREREGISTRATION.md, RULES.json
    * production/ (49 units, REDUCTION.json, posthoc/)
    * flight1/, flight2/
    * aim01_run.py, aim01_reduce.py, aim01_flight.py, aim01_conformance.py,
      posthoc_nonaim_probe.py
 - Aether/test/test_aim01_meter.py (known answers)

+==============================================================================+
| END. "Fixed aim was a known design property; this told us nothing new" and  |
| "the frozen-medium line is not worth continuing" remain first-class          |
| answers. Say so if you think it.                                             |
+==============================================================================+
