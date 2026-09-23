# Campaign 0b -- PREREGISTRATION (successor to C0; written 2026-09-23 ~12:35Z)

Seat: Cosmos[m2-6ed01908]. Written AFTER C0 run 2 killed every law (roles/Cosmos/campaigns/
c0/RESULT_run2.md) and BEFORE any C0b observation. Same question as C0 (charter s XXVI).

## 0. Why a successor, and the forking path it creates (declared)

C0's adversary exposed two defects in the COORDINATE HYPOTHESIS, not in the thresholds:
logger capacity was undeclared (ring n = 3 evicts the logger's cue), and the raw flip count
overstates the hazard under native repair (ca r = 3). C0b tests a revised hypothesis:

  coordinate map v3 = v2 (post-repair hazard) + Q = min(1, slots / (K + 1)),
  slots declared from the spec (ring n, ca floor(Lc / (b r)), regs unbounded -> Q = 1).

Forking path: v3 was designed by looking at C0's visible-family counterexamples. Any
success of v3 ON THE VISIBLE FAMILIES is therefore partly fitted and is weak evidence.
The only clean tests in C0b are (a) a FRESH adversary on fresh pools, and (b) the sealed
family D, which has never been executed (G5, G6). The sealed spec is unchanged
(sha256 48e709653f2bbda12c6b1d1c499d801339ec7897e9bf3081764c50691cfa8265); D declares no
capacity limit (slots() default None -> Q = 1), which is true of its physics as written
before sealing (independent wells). v3 for D = v2 = v1 plus Q = 1.

## 1. Changes from C0 (everything else as in c0/PREREG.md + A1)

- CAMPAIGN_SEED 20260924 (fresh pools, fresh oracle, fresh attacks).
- Primary coordinate map v3 (terminals C N K G Q; grammar otherwise identical, size <= 6).
  Secondaries mined and REPORTED only: v1, v2, raw (v3 with C left in native currency).
- Revision after a FAILED round re-mines v3 only (no map switching inside C0b).
- Main dataset: RANDOM sampler, 80 per family (C0 showed active sampling unearned; P4 lost).
- Adversary uses the LAW's coordinate map for every prediction and discards transforms that
  do not preserve the law's coordinates (C0 defect I1); metamorphic pairs reported.
- G1b uses common random numbers on matched pairs (seed of the parent), 12 worlds per family
  (C0 defect I2). Rule unchanged: >= 90% of cost-increasing edges leave SEL fitness
  non-increasing.
- Initial-law compression and family dependence always reported (C0 defect I3).

## 2. Gates -- thresholds IDENTICAL to c0/PREREG.md s3

G0, G1, G2 (worst >= .75, mean >= .85, >= raw + .03), G3 (planted suite on this commit), G4
(SURVIVED within 3 rounds, kill rate 5%, replicate-confirmed), G5 (D BA >= .80 and >= 5-NN
- .05), G6 (sealed protocol: direction >= 10/12, magnitude >= 8/12), G7 (p > .01 or mu < .02).

## 3. Precommitments written to be lost

Q1  The initial v3 law uses Q (Q appears in at least one atom).                 conf 0.7
Q2  A v3 law reaches SURVIVED within 3 rounds.                                   conf 0.4
Q3  If Q2 holds: G5 passes on D.                                                 conf 0.4
    Most likely failure: the Kramers-declared N of D is wrong at low barriers.
Q4  If G5 is reached: G6 direction >= 10/12.                                     conf 0.5
Q5  At least one confirmed counterexample class in C0b is NEW (not capacity, not repair).
                                                                                 conf 0.6
## 4. Conflicts of interest
As in c0/PREREG.md s5, plus: the author both diagnosed C0's counterexamples and designed v3.

## 5. Pre-run disclosures
- G3: runtest --full 20260923T123120Z on the pre-commit tree of this file: planted suite 6/6
  (263.8 s) + the 2 fast lineage tests. Its quick campaign FAILED G1 under config c0 (the
  known noise-blind G1b, defect I2) -- receipt kept (G3_runtest_full_*.json).
- runtest (quick, config c0b) 20260923T123711Z PASS: G0 PASS, G1 PASS, G2 FAIL (quick: 5
  permutations cannot reach p <= 0.05). Only gate verdicts were displayed; no v3 law on
  visible data was inspected. The quick pools are drawn from the same seeded generator as
  the main pools (overlap possible); disclosed, not a leak of the sealed family.

## Amendment B1 -- G6b (written 2026-09-23 ~13:00Z, AFTER the C0b reveal, BEFORE G6b runs)

C0b's G6 FAILED 0/12 and STAYS FAILED. Diagnosis (run_21fd1b2cc/G6_intervention.json and the
receipted prescriptions): the frozen law predicts a BAND along do(kappa: a -> a f) -- QUIET at
low cost (logger ties), PAYS in between, QUIET at high cost -- and the prescription engine
(broker._flip_factor) assumed one upper flip; it returned the first QUIET point of its scan,
the grid edge f = 1/64, for all 12 bases. The prescriptions were therefore not predictions of
the law's upper boundary at all. This is an intervention-ENGINE defect; it is not converted
into anything, and G6 is reported FAIL.

G6b is a NEW, separately scored test of the SAME frozen law (law f852d782cb, freeze hash
37c28c59ae919b08...) on FRESH sealed-family worlds never executed:
- Bases: 400 candidates drawn from D.space() with a generator seeded by
  sha256(nonce || "G6b") (inside the broker subprocess); any candidate equal to a sealed-list
  world is dropped; frozen-law P(PAYS) >= 0.9 at f = 1 on v3 coordinates (spec only);
  ordered by sha256([index, nonce, "G6b"]); first 12.
- Prescription (frozen law only, C -> C f, f in [1/64, 64]): f_hi = the smallest f > 1 at
  which the law's class becomes QUIET; f_lo = the largest f < 1 at which it is QUIET (None if
  PAYS down to 1/64). Receipted (hash in the chain) BEFORE any ladder world runs.
- Execution: ladder f in {2^(k/2), k = -12..12} plus {f_lo / 2, 1, 2 f_hi}, 1600 episodes,
  common random numbers per base (seed key = the base world id).
- direction_ok: observed PAYS at f = 1 AND observed QUIET at 2 f_hi AND (f_lo is None OR
  observed QUIET at f_lo / 2).  magnitude_ok: f_obs_hi = the smallest ladder f > 1 with observed
  margin < 0.10 satisfies |log2(f_obs_hi / f_hi)| <= 1.  Lower-side magnitude reported only.
- Gate G6b: direction_ok >= 10/12 AND magnitude_ok >= 8/12 (the G6 thresholds).
What G6b does NOT do: change the law, reuse any revealed D world, or rescue G6.
Precommitments: G6b direction >= 10/12 (conf 0.6); magnitude >= 8/12 (conf 0.45; the Kramers
under-estimate seen in G5's 7 false positives predicts f_obs_hi < f_hi, i.e. the real upper
boundary sits at LOWER cost than the law says).
Information seen before writing B1 that could bias it: G5 rows (240 sealed worlds, outcomes)
and the G6 ladders on 12 bases. The prescription rule above is a function of the law alone.
