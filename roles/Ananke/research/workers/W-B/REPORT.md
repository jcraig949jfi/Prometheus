# W-B REPORT: what does SETRULE contribute in PTE champions?

(Saved by Ananke from W-B's final message; the harness refused the
worker's write. PLAN.md (addenda A-C), LOG.md (A0-A13), scripts and
out/*.json are in this directory. The GPU lease was held and released
(tokens 949b0f52f816, f3b256647b52); it was never BUSY.)

Namespace 0x5E5, 64 worlds = 32 mirror pairs, 99% pair bootstrap. Paired
verdicts from rules frozen in PLAN.md: HURTS if hi99(d) < 0; EQUIV if
lo99(d) > -0.05.

## 1. M3 (0a23398f, f6b623cd): the bootstrap account holds, more narrowly
- Mechanism (static, then confirmed): at tick 0 every register is 0.
  Every rule variant in both genomes has a SETRULE whose A operand is
  still 0, so each awake site goes to rule 0. The expectation
  0.8 + 0.2*0.25 = 0.85 matches s_m3's 5442/6400. The rest reach rule 0
  by tick 4-7. Then no site ever changes rule, and r never differs
  between mirror partners (count 0).
- Uniform r := 0 before tick 1 with SETRULE frozen is EQUIV to normal
  (+0.014 / +0.007; the gain is all in trial 0, 0.53 -> 0.67). r := 0
  with SETRULE on is identical, so SETRULE does nothing once at rule 0.
  Uniform r := 1/2/3 gives exactly 0.50.
- Exact reduction: a rules=1 law running the rule-0 program is
  bit-identical to rules=4 with r := 0 frozen, in both specimens. The
  functional law IS a one-rule law.
- Rules 1-3 are dead: frozen in them a world emits 0 packets. Pinning 25%
  of the non-readout sites to rule 1/2/3 gives bit-identical traces. Only
  "rule 0 or not" matters.
- Per-site dose response: readout frozen at r0 HURTS; others frozen at r0
  HURTS. With r := 0 and a fraction f of non-readout sites pinned to
  junk: f .05-.1 EQUIV; .25 EQUIV (0a23) / HURTS (f6b6, -0.04); .5 HURTS
  (-0.05 to -0.07); 1.0 chance.
- Latent repair, never used in normal physics: r randomized at mid
  trial 4 is repaired in ~5 ticks with SETRULE on; frozen after, it goes
  to chance.
- Transfer: in three neighbouring physics (update_p 1.0, loss .15,
  lat_base 3), r := 0 frozen is EQUIV; a random-init freeze HURTS.
Verdict M3: SETRULE's only exercised role is to replace the random
initial rules with the single functional variant. That variant is
privileged by a PHYSICS ARTIFACT (the zero-register default), not by an
evolved configuration. No gating, no cue dependence, no per-site pattern.

## 2. Census: 42 C1 cells (SIGNAL, rules > 1, setrule = 1, held lo99 > .55)
A random-init freeze HURTS in all 42. Classes (rules frozen before the
census):
- UNIFORM_BOOT 25 (24 ZERO; 1 settles on rule 1: 9bbe8637), incl. both M3;
- PATTERN_BOOT/GENERIC 2 (c7d7d2a4, 88f94654): uniform r := 0 is also EQUIV,
  so functionally bootstrap;
- TRANSIENT 1 (cc18858f, d = -0.02 [-0.056, 0.014]; underpowered);
- UNRESOLVED 2 (dd6fdf49: weak cue-independent excursions, freeze after
  settling -0.045; 8e1caf6b: readout mostly in rule 1, all uniform arms
  HURT);
- ONGOING 12 (9 RELAY, 3 HOLD): freezing after settling HURTS (-0.02 to
  -0.28). All carry the CUE_CARRYING tag (partner r differs somewhere).
Bootstrap is sufficient for 27/42 (64%) and clearly fails for 12/42
(29%). 5 of the 12 are from one lineage (c939c3c7 + 4 wave-B children),
so there are fewer independent ONGOING cases.

## 3. ONGOING cells: a per-tick conditional branch, not a memory
- r is NEVER the carrier: an r-swap at mid-interval gives NO-EFFECT in
  17/18, CHANCE in 1 (b059e735, 0.75 -> 0.71), FLIP in 0. At the readout,
  r predicts y at 0.50-0.65 (best in-sample map).
- The need is local to the readout site: pinning the readout's r after
  settling HURTS in 12/18 (b59e6c3a -0.26, 63d17a90 -0.27, b059e735
  -0.26, 311c465f -0.28). Pinning every other site changes accuracy by
  exactly 0.000 in 13/18 (it HURTS only in 95649e2c, 369f5a5b, 42716814).
- Timing: in 6 RELAY cells the readout makes a brief mid-interval
  excursion to a non-zero rule, only in worlds of ONE cue sign, and
  returns to rule 0 before the readout. A SIGN-CONDITIONED BRANCH,
  recomputed from state every tick by SETRULE: swapping r does nothing
  (it is recomputed next tick), while pinning it removes the branch.
- HOLD cells (311c465f, faafa5b0; readout = sense site): only rule 1
  writes S0 from SENSE, and the site enters rule 1 around cue onset (rule
  1 = SAMPLE, rule 0 = HOLD). The frozen hypothesis G ("the gate only
  blocks distractors") FAILED: pinned to rule 1 is chance even without
  distractors. The alternation IS the hold mechanism.
- Unexplained: 311c465f falls from 0.76 to 0.55 when distractors are
  removed. The champion depends on distractor input.

## Predictions
Held: all Part-1 (M3) predictions. Failed: UNIFORM_BOOT >= 60% (59.5%);
ONGOING <= 20% (29%); CUE_CARRYING <= 3 (12, but the tag was weak: by the
swap test, r carries the bit in 0 cells); Z2 gate test.

## Proposed threads
1 Branch mechanism: decompile the readout excursion (b59e6c3a, 63d17a90)
  and test "recomputed each tick" directly (swap r AND block SETRULE at
  the readout for one tick).
2 Engine-card correction (below).
3 Physics confound: the zero-register default privileges rule 0, so for
  bootstrap cells rules > 1 act as a random site-deletion mask at t=0.
  Future preregs should initialize r = 0 when asking whether rules are
  USED.
4 A lineage-aware recount of ONGOING.
5 Distractor dependence of 311c465f.
