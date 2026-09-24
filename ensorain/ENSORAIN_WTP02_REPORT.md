# ENSORAIN WTP-02 -- campaign report

Currency: 2026-09-24. Seat Ensorain[m2-14baf7d5].
Operator authorization: roles/Ensorain/prompts/2026-09-24_wtp02_authorization/ (verbatim).
Preregistration: ensorain/PREREG_WTP02.md (d7db1854b). Addenda:
  - A1-A5 (08fa0c8d3) and A6 (95529c3ce): pre-data;
  - A7 (7a00c4063): declared during admission, before any life was analysed;
  - A8: POST-DATA, marked as such.
Engine: ensorain/wtp2/.
Rows: ensorain/runs/wtp02/. These are:
  - validation.json, waveA_admission.json, waveA.json, waveA_summary.json;
  - waveB.json through waveF.json, fossil_factorial.json, summary.json;
  - kill_const.json, kill_const_f9.json, waveF_i9_genome.json.

## VERDICT

    Preregistered rule (s6), computed mechanically by campaign2.verdict:
        FOUND CANDIDATE INTELLIGENCE PHYSICS -- EXPAND

    Seat adjudication (A8 kill test, post-data):
        SEARCH SPACE REMAINS DEGENERATE -- PARK/REDESIGN

The mechanical EXPAND rests on one specimen (#10, world 0e3e9ca1cb88f30c, detector D3). It completed the whole chain:
  1. REPLICATED + STRUCTURE-DEPENDENT: 5/5 hits, 0/5 null hits.
  2. CAUSAL SUPPORT: 9 causal dials, 5 non-causal.
  3. ARTIFACT CARRIER.
  4. TRANSFERRED.

Specimen #10 is an organism whose entire memory is ONE FLOAT: a running mean of what it has observed.

Its "competence" comes from beating a zero predictor on unseen cells with a learned constant:
  - Replace the organism by its own learned constant, frozen and with no marks. The constant scores CGu 0.166; the organism
    scores 0.088 (medians over 5 seeds).
  - The chain's later links pass for the same reason. Ablating half of zero parameters is a no-op. Reskinning (permuting
    modes) cannot change a constant. A "fresh" frozen one-float organism scores exactly 0.000, so every transplant "gain" is
    simply the constant's own score.

Every Wave A positive meets the same fate (s3). This includes the single structure-dependent recombinant from Wave F. No
phenomenon survives the constant control, so the s6 branch that applies after adjudication is PARK/REDESIGN, not CONTINUE
SEARCH. CONTINUE SEARCH needs >= 1 surviving STRUCTURE-DEPENDENT phenomenon, and there is none.

The operator can rule otherwise. The mechanical verdict is recorded unaltered in runs/wtp02/summary.json.

**Answer to s21: does WTP-01's 1.1% collapse to 0 when memorisation is impossible?** Yes.

    WTP-01, competent fraction (memorisation possible)                       1.1%
    WTP-02, CGu >= .10 AND SD >= .10, per world (prereg metric)              8 / 1500  = 0.53%
    WTP-02, same, per founder lineage (A7)                                   3 / 187   = 1.6%
    WTP-02, positives that also exceed the best constant predictor by >= .10  0 / 1500

The zero in the last line is not specific to the 8 tested positives. The true field mean scores CGu 0.000 in every world
(the fields are zero-mean). Every other admitted world already has CGu < 0.10 against zero, so none can exceed a constant
by 0.10.

## 1. What was run

    validation (s7)                  V1-V4 ALL_PASS (after A6 fixed V3's digest timing)
    candidates                       24,000 -> 1,717 passed every gate (7.2%) -> 1,500 used
      gate kills                     N5 7,512 / N3 6,308 / N1 4,982 / N2 1,983 / N2c 1,070 /
                                     N2b 269 / BUILD 141 / N4 14 / CRASH 4
      generator mix of the 1,500     mutation 1,313 / random 94 / grammar 49 / novelty 44
      founder lineages               187 (largest 221 worlds)
      substrate generators           spectral 522 / pairwise 355 / cp 237 / tt 174 /
                                     lowrank 125 / sum 74 / sparse 13
      memory bands                   .01 228 / .03 366 / .10 503 / .25 403
    Wave A lives                     6,000 (real + shuffled + frozen + random twin per world)
      real-life status               OK 1,478 / DEGENERATE 22 (caught per step, never scored)
    Wave B                           33 anomalies x 5 replicate units (x 4 twins)
    Wave C                           14 single-dial interventions x 3 seeds + causal sweeps
                                     on the 1 STRUCTURE-DEPENDENT family
    Wave D / E                       autopsy + transfer on that family
    Wave F                           100 recombinants -> 68 admitted -> 10 flagged -> replicated
    fossil lane                      WTP-01 specimen b235013022100e1f, 2^4 x 3 seeds = 48 lives
    compute                          M2, 20 workers, ~1 h wall

## 2. Distribution (Wave A, real lives)

    CGu quantiles   1%  -3.07 | 10% -0.39 | 50% -0.006 | 90% 0.000 | 99% 0.081 | max 0.339

Detector fires on real lives, compared with their named null twin:

    det  meaning                     real  null (twin)     lineages
    D1   CGu >= .10                    11     2 (shuffled)     3
    D2   one-checkpoint jump           81    88 (shuffled)    20
    D3   CGu per float, top 1%         15     4 (shuffled)     1
    D4   CG <= -1 (anti-competence)   107    12 (frozen)      34
    D5   utility vs competence split   62   295 (random)      20
    D6   survival ratio                 0     3 (frozen)       0
    D7   reorganisation                92    90 (shuffled)    17
    D8   reachability gain             15     9 (shuffled)    13
    D9   compute amortisation           0     0 (shuffled)     0

D2 and D7 fire as often on shuffled worlds as on real ones, and D5 fires more on random walkers than on the real organisms.
They detect generic dynamics, not structure. D3's 15 fires come from one lineage.

## 3. The kill (A8)

Every one of the 8 Wave A positives was re-run on 5 seeds. Scores are medians over those seeds.

    world             memory   floats  CGu org  CGu true mean  CGu learned const  excess  verdict
    0e3e9ca1cb88f30c  marks    1        0.088    0.000          0.166             -0.034  SCALAR-EXPLAINED
    45706a898230b127  none     16      -0.034    0.000         -0.031             -0.034  SCALAR-EXPLAINED
    0c6e917c3d99a27b  marks    1       -0.019    0.000          0.009             -0.028  SCALAR-EXPLAINED
    b616541b69a6abc3  marks    1        0.044    0.000         -0.280              0.044  SCALAR-EXPLAINED
    090d18d40035d252  marks    1        0.075    0.000          0.071              0.000  SCALAR-EXPLAINED
    84c07c121ba36cd5  cp       23      -0.000   -0.000         -0.000             -0.000  SCALAR-EXPLAINED
    8872caa4fc2d0393  marks    1        0.024    0.000          0.068              0.000  SCALAR-EXPLAINED
    acae04212998f400  marks    1       -0.227    0.000          0.049             -0.121  SCALAR-EXPLAINED

Two further points:
- None of the 8 reaches CGu 0.10 on the median of the fresh seeds. The Wave A positives were upper-tail draws.
- 6 of the 8 are one-float running-mean organisms, and 5 of those 6 descend from one founder lineage. All six see the world
  through a v_fft_abs -> v_tanh observation chain. Their observations are therefore a transformed, positive quantity,
  and the constant they learn is a statistic of that transform.

**Why SD > 0, i.e. why shuffling "kills" it.** The unseen battery cells are not a random sample. They are the cells the
organism did not visit, and in a smooth field their mean is correlated with the region the organism did see. Shuffling
the field breaks that correlation. This is the most plausible reading, but I have not tested it, so it stays an
explanation. It is not a finding. What the kill test does establish is that one scalar carries the whole effect.

**Wave F recombinant #9** (D2 jump; parents #10 and 996579edc9312ee0) is also a one-float organism, with learning rule
"none". A one-float memory keeps its running mean whatever the rule is, so "rule_none" is a no-op for it.

The organism's "jump" is the running mean converging from a noisy early estimate. The first checkpoint sits at -0.41 to
-0.51; the next is near 0. On 5 fresh seeds the jump fires 2/5 for the organism and 0/5 for its own constant
(kill_const_f9.json).

## 4. Instrument defects found (each is a WTP-03 requirement)

I1 **ZERO REFERENCE.** CG and CGu are measured against the zero predictor, which the best constant beats whenever the
   scored cells have a nonzero mean.
   Required: CGu := AC(org) - max(AC(0), AC(best constant)).
   The best constant is the organism-independent mean of the observations it saw. It becomes a fifth twin ("mean") and
   the null for D1, D3 and D8.
I2 **PER-FLOAT RATIO.** D3 divides by n_floats. A one-float learner maximises it. D3 needs a floor on n_floats, or a
   comparison to the mean twin.
I3 **SCALAR LEARNERS ARE ADMITTED AS ORGANISMS.** 684 of 1,500 worlds (46%) have n_floats = 1: memory "none" or "marks",
   which is the same class. The necessity gates (N1-N5) never ask whether the memory can hold more than a scalar.
   Required: admit them only as the baseline class, never as specimens.
I4 **AUTOPSY NO-OPS.** ablate_half, freeze and reskin do nothing to a parameterless memory, and reskin cannot affect a
   constant. Wave D/E "carrier" and "transferred" then pass automatically.
   Required: every intervention asserts that it changed the state it claims to change, else it returns NOT_APPLICABLE.
I5 **SHORT LIVES.**
   - Organisms live a median 25% of their lifetime (10% / 90% quantiles 4% / 98%). Only 10.7% are alive at the end.
   - The median trace has 5 checkpoints, not 20.
   - R5 ("deeper lives") therefore did not happen, and D2/D7 read 5-point traces.
   - A2 calibrated metabolism so that the ORACLE profits. Learners are far from the oracle, so they starve.
   - Required: calibrate against a reference learner, not only the oracle, and require median survival >= 75% in the dry
     run.
I6 **FOSSIL FACTOR NO-OP.** The fossil specimen's native credit delay is already 0, so both "delay" levels ran delay 0.
   The 24 "delay on" lives are byte-identical to the 24 "delay off" lives. The fossil lane actually ran 2^3 x 2 copies.
I7 **LINEAGE CONCENTRATION** (A7). Once admitted parents exist, mutants dominate admission (1,313 of 1,500). Per-world
   fractions overstate independence by roughly 8x (187 lineages).

## 5. Failure-fossil lane (WTP-01 specimen b235013022100e1f, WTP-01 engine)

48 lives: 16 cells x 3 seeds.

    CG                  negative in 48/48 lives (-0.36 to -141); no cell competent
    jump (WTP-01 D2)    32/48 overall: SGD 18/24, Hebbian 14/24 -- not a Hebbian phenomenon
    parameter norm      median 83,825 under SGD vs 4,995 under Hebbian; irreversibility x7;
                        Hebbian + irreversibility + frozen world diverges to 5e18
    credit delay        not tested (I6)

**Reading.** WTP-01's "jump" is a generic divergence and relaxation signature of an unstable learner. It appears whether
or not learning is Hebbian, while the error is catastrophic. The fossil stays a fossil: MECHANICAL.

## 6. Seat predictions (s8), scored

    admission 5-20%                                   7.2%          HIT
    CGu&SD fraction 0.2-2%                            0.53%         HIT on the number
      "dominated by low-rank/DCT/CP learners"         6/8 are one-float mean trackers   LOST (mechanism)
    verdict p: CONTINUE .5 / PARK .35 / EXPAND .15    mechanical EXPAND; adjudicated PARK

The number was right for the wrong reason. The calibration ledger records this as a loss, not a hit.

## 7. What WTP-02 did establish

- **The foundry works as a falsification machine.**
  - The necessity preflight, the separate RNG streams, the per-step collapse check and the fixed V0 all did their jobs.
    No WTP-01-style variance-collapse artefact reached a status other than METRIC ARTEFACT (6 caught in Wave B).
  - The same seed reproduces the admission record exactly (launch 1 vs relaunch, batch 1).
- **With memorisation impossible and a constant controlled, the structure-dependent competence fraction is 0 / 1,500 at
  the 0.10 threshold.**
- **The search space the foundry samples is dominated by organisms that cannot represent structure** (I3) and that die
  early (I5). Before WTP-03 runs, the foundry must change what it admits (I3, I5) and what it compares against (I1, I2),
  not how much it searches.

## 8. Recommended WTP-03 (for the operator's ruling; nothing launched)

  1. **Fix the reference (I1/I2).** Add a mean twin and rescore every existing Wave A row. The rows already hold enough to
     do this for D1/D3 without re-running.
  2. **Restrict the specimen class (I3).** Specimens need n_floats >= 4 and a nonzero learning rule. Scalar learners are
     kept as the baseline class.
  3. **Recalibrate the economy (I5).** Use a reference learner (the planted-panel additive fit) instead of only the
     oracle. Admit only worlds where it survives >= 75% of its life.
  4. **Add no-op guards on every intervention (I4); add a real delay level to the fossil (I6).**
  5. **Cap mutation share by lineage (I7)**, for example at most 10 admitted per founder.
  6. **Rerun Waves A-F at 1,500 worlds.** Prediction, written now to be losable: the structure-dependent fraction stays
     below 0.5% of lineages.
