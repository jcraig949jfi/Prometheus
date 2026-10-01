INV_N -- Why did all SIGNAL worlds come from cheap worlds? (LEDGER Q5 follow-up)
Hecate harvest_w2, read-only analysis, 2026-09-30. No model calls, no git writes.
Script: scratchpad N/inv_n.py (not committed; numbers below are its output).

0. Order of work (honesty note)
Section 1 was written BEFORE any test in section 3 was computed. It was NOT
written blind: before writing it I had already looked at the per-world
outcome/cost table and read the clause values of most NULL and all SIGNAL
OUTCOME.json files, to learn their schemas. So these are predictions about
tests, not predictions made without having seen the data.

1. Predictions, written before computing (H = hypothesis, P = prediction)
(a) POWER. Cheap worlds buy more seeds/replicates per budget, so real effects
    become detectable.
    Pa1 SIGNAL worlds have more treatment seeds than valid NULL worlds.
    Pa2 seeds per arm fall as actual cost rises (negative Spearman).
    Pa3 a meaningful share of expensive NULLs are NEAR MISSES: the decisive
        clause misses by < ~2 between-seed SE, so more seeds could flip them.
    Pa4 cheap NULLs have fewer seeds / more noise than cheap SIGNALs.
(b) TRIVIAL CONSTRUCTION. Cheap worlds are tiny and near-deterministic; their
    effects follow from the construction (a known theorem, an exact tie, a
    degenerate dynamics), so they pass sharp thresholds and then die at Pass 4.
    Pb1 SIGNAL worlds have higher between-seed determinism (more zero-variance
        treatment readouts, lower CV) than valid NULL worlds.
    Pb2 determinism rises as actual cost falls.
    Pb3 seed count does NOT separate SIGNAL from NULL (power is not the lever).
    Pb4 NULLs are mostly FAR misses or fired failure clauses (deterministic
        misses), not near misses.
    Pb5 every Pass-4 kill names an exact/degenerate/known structure.
(c) READABILITY SELECTION. Cheap worlds are less often UNTESTABLE
    (INSTRUMENT_FAIL / NOT_BUILT / SPEC_UNATTAINABLE); SIGNALs are just the
    valid readings, and validity is what cost buys.
    Pc1 invalid worlds have higher CLAIMED cost than valid ones.
    Pc2 among VALID worlds only, cost no longer separates SIGNAL from NULL.
(d) GENERATOR COMPETENCE. The generator wrote cheap worlds for mechanisms it
    understood best (familiar, early-listed, cleanly specified).
    Pd1 CLAIMED cost separates SIGNAL from NULL at least as well as actual
        cost (the generator intended them cheap).
    Pd2 SIGNAL worlds come from early-listed mechanisms (M1-M3; INV_H showed
        position is the main driver of which mechanisms get worlds).
    Pd3 SIGNAL worlds self-declare a known/standard alternative more often
        (alternative_explanation / stupid_explanations naming textbook work).
    Pd4 SIGNAL worlds needed fewer build attempts and less code.
Not exclusive: (b) and (d) can both hold; (a) and (b) make opposite
predictions on Pa1/Pb3 and Pa3/Pb4 -- those are the decisive pairs.

2. Data and n
37 probed worlds (OUTCOME.json under hecate/programs/HT-*/worlds/, rounds 1-3).
VALID = NULL/SIGNAL/CONFOUNDED: 25 (5 SIGNAL, 19 NULL, 1 CONFOUNDED).
INVALID = INSTRUMENT_FAIL/NOT_BUILT/SPEC_UNATTAINABLE: 12.
Cost: actual = OUTCOME core_minutes; claimed = spec cost_estimate parsed with
hecate.probe_select.parse_cost. nT = distinct seeds in the TREATMENT arm of
rows.jsonl. Tests: exact two-sided permutation (all C(n,k) relabelings) on
ranks or means unless marked mc (20k-50k draws). n = 5 signals throughout;
every p below is post hoc and none is multiplicity-corrected (~20 tests).

3. Results
Q5 re-check first (it matters for every explanation):
- Q5 text "ALL 5 SIGNALs are the cheapest worlds" is WRONG as worded. The two
  cheapest valid worlds are NULLs (2a8a W4 0.0060, 47f4 W1 0.0094) and the 9
  valid worlds under 0.05 core-min are 5 SIGNAL + 4 NULL (+056d W5 0.0216,
  e106 W1 0.0404). The true pattern is a cliff: 5/9 SIGNAL below 0.05
  core-min, 0/16 above.
- Exact rank test, actual cost SIGNAL vs other valid: p = 0.012 two-sided
  (Q5's 0.006 is the one-sided value). Claimed cost: p = 0.167 (Q5 0.085
  one-sided). Holds within round (round-stratified permutation p = 0.010;
  round 2 had 0/7 signals) and among first-attempt worlds only (n = 15,
  p = 0.0027), so it is not produced by repair attempts inflating NULL cost.

Test | prediction | result | p | verdict on prediction
Pa1 nT SIGNAL vs other valid | S higher | S 20,10,60,10,10; others median 10 | 0.19 (log 0.17) | not supported (one 60-seed world)
Pa2 Spearman nT vs actual cost | negative | rho = +0.16 | 0.44 | FAILED: seeds set by spec, not budget
Pa3 expensive NULLs are near misses | many | 3/19 NULLs near, all > 0.6 core-min (sec. 4) | rank vs cost 0.21 | weak, minority
Pa4 cheap NULL vs cheap SIGNAL nT | NULL fewer | median 5 vs 10 | 0.26 | direction only; all 4 cheap NULLs FAR misses
Pb1 zero-variance share S vs NULL (auto index) | S higher | +0.03 | 0.85 | not supported
Pb1' median between-seed CV (auto index) | S lower | -0.007 | 0.88 | not supported
Pb2 zero-variance share vs cost (auto) | negative | rho = -0.28 | 0.19 | direction only
Pb2' decisive statistic exact/degenerate (hand-coded) | cheap higher | cheap 5/9, expensive 2/16 | Fisher 0.058 | suggestive
Pb3 nT does not separate S | true | see Pa1 | -- | supported
Pb4 NULLs mostly far misses | true | 16/19 far (sec. 4) | -- | supported
Pb5 Pass-4 kill names exact/degenerate structure | 5/5 | 5/5 (sec. 5) | no comparison group | supported; untestable vs cost
Pc1 claimed cost invalid > valid | higher | median 2.0 vs 2.0 | 0.26 (mc) | FAILED
Pc1' invalid rate by claimed cost | higher above 1 | 3/13 (<= 1) vs 9/24 (> 1) | (in Pc1) | direction only
Pc2 cost effect gone within valid | gone | Q5 contrast IS within valid, p 0.012 | -- | FAILED: (c) cannot explain Q5
Pd1 claimed cost separates S | as well as actual | 0.167 vs 0.012 | -- | FAILED (claimed vs actual rho 0.33, p 0.11)
Pd2 SIGNAL from M1-M3 | early | 3/5 vs 9/20 | 0.64 | not supported (S: M1,M2,M3,M11,M12)
Pd3 self-declared known alternative | S higher | 1/5 vs 3/20 | 1.0 | not supported (regex flag, weak proxy)
Pd4 build attempts | S fewer | S all 1; others mean 1.75 | 0.12 | confounded: round-2 counts include pilot phases
Pd4' code lines | S fewer | median 391 vs 441 | 0.48 | not supported

Automated determinism index = for TREATMENT rows, per (row index within
seed, numeric field) SD across seeds; share of zero-SD keys and median CV.
It averages over every logged number, most of them not the decisive
statistic, which is likely why it is blind here. The hand-coded column
(Pb2') reads only the statistic the criterion used, but the coder (me) was
not blind to outcome or cost; treat Pb2' as suggestive only.

4. Margin of each valid non-SIGNAL world (decisive clause; from OUTCOME.json)
FAR = miss > ~4 between-seed SE, wrong sign/order, or a failure clause fired.
cost  | world   | decisive miss                                    | class
0.006 | 2a8a W4 | off_ratio 1.00-1.08 vs >= 1.2, 0/10 seeds         | FAR
0.009 | 47f4 W1 | twin ratio 0.2115 vs >= 0.9 (seed SD 0.0008)      | FAR, exact
0.022 | 056d W5 | S1 75 vs <= 12; F1, F3 fire                       | FAR
0.040 | e106 W1 | R = 1.0, CI [1.0, 1.0] vs >= 4                    | FAR, exact
0.226 | 47f4 W4 | CONFOUNDED: null twin meets success               | not power
0.438 | e743 W1 | ratio 0.35 vs >= 1.3 (opposite sign)              | FAR
0.442 | faa9 W6 | RIF 0.009 vs >= 0.25                              | FAR
0.454 | 9744 W6 | I_perp 0.4505 vs 0.6, SE 0.034 (4.4 SE)           | FAR
0.465 | 056d W4 | k=3 Lasso rate 0.62 vs >= 0.8 per seed            | FAR
0.466 | e743 W3 | KL clause fails; failure (T/N 0.90) fires         | FAR
0.504 | a9e2 W4 | drop 0.125 vs <= 0.05 (sd 0.008); F fires         | FAR
0.521 | 2a8a W1 | S1 0/10 in all 9 cells; F fires                   | FAR, exact
0.689 | ae38 W3 | dAIC_sat 5-7.6 vs >= 10 in every seed             | NEAR, systematic (not variance)
0.789 | 37e3 W5 | completion 0.732 vs 0.8, boot SE 0.038 (1.8 SE)   | NEAR, power-plausible
0.806 | e106 W5 | S1 0.027 vs 0.2; F1 fires                         | FAR
0.920 | a9e2 W3 | ARI osc 0.789 < comp 0.804 + 0.02; F fires        | FAR (wrong order)
1.034 | 9744 W3 | masked_frac 1.0 at k3 and k50 (SD 0); F fires     | FAR, exact
1.261 | ae38 W5 | S1 0.334 vs 0.40, SE 0.153 (0.4 SE)               | NEAR, power-limited (contested C1)
1.914 | 79e9 W4 | Spearman 0.33 vs 0.8 over 8 levels; F fires       | FAR (C3 instrument-weak)
2.612 | 79e9 W1 | decline and control clauses fail; F fires         | FAR
Signals' own margins: 321a rates exactly 0 or 1 in every seed; 5516 ARI =
1.0 in 10/10 seeds; 71b6 passes on an exact accuracy tie (T = L1 = L2 =
0.7427); 8a87 S1 0.32 vs <= 0.5 (seed CV ~5%); 5b0b OR 1.58 vs >= 1.5
(p 2e-4 from 1747 pooled cells -- thin margin carried by large n).

5. Pass-4 kill reasons (all 5 SIGNALs; no NULL and no expensive world ever
reached Pass 4, so reason-vs-cost cannot be tested)
321a W1 ORIG fired: textbook minimum-distance bound (KNOWN_ANALOGUE); its
        PROBING rests on a degenerate counting ALT (CORRECTIONS C2).
71b6 W3 ORIG fired: fixed depth L1 matches adaptive (0.74355 vs 0.74370).
8a87 W5 ORIG fired: channel reset gives IDENTICAL per-seed error counts to
        the core-guided treatment (ratio 1.000).
5516 W6 ORIG fired in substance (K1); the original world ran at sigma 0
        with collapsed trajectories (traj std ~5e-138): degenerate dynamics.
5b0b W4 ORIG fired (outcome variance in 0/20 strata); ALT failed.
Every kill is an exact identity, tie, textbook bound or degenerate regime.

6. Which explanations survive
(a) POWER -- REJECTED as the explanation of the cost cliff. Seeds were fixed
    by the spec (5/10/20/30), not scaled to budget (rho +0.16); SIGNALs did
    not have more seeds; 16/19 NULLs miss by margins more seeds cannot
    close, including all 4 cheap NULLs. Residual: 2 expensive NULLs (37e3
    W5, ae38 W5) are plausibly underpowered -- a footnote, not the cause.
(b) TRIVIAL/DEGENERATE CONSTRUCTION -- SURVIVES, best supported, refined.
    Cheap worlds tend to be degenerate (exact or zero-variance decisive
    statistic 5/9 vs 2/16, p 0.058, non-blind coding), and degenerate
    worlds give binary readings: an exact pass (321a, 5516, 71b6) or an
    exact fail (47f4 W1, e106 W1). No cheap world near-missed. Every SIGNAL
    died at Pass 4 on an exact/degenerate structure. Not shown: that
    degeneracy favours passing over failing; the automated determinism
    index does not separate SIGNAL from NULL.
(c) READABILITY SELECTION -- REJECTED for Q5. The Q5 contrast is already
    within valid worlds, and claimed cost does not predict invalidity
    (p 0.26).
(d) GENERATOR COMPETENCE -- NOT SUPPORTED by any available proxy (claimed
    cost, list position, self-declared known alternative, code size). The
    generators did not know which worlds would be cheap. Proxies are weak,
    so (d) is unsupported, not refuted.
Net: read the cost-SIGNAL link as "cheap = degenerate = sharp thresholds
pass (or fail) by construction", not "cheap = well-powered". The cliff is
real (round- and attempt-robust) but n = 5 and post hoc.

7. Corrections recommended for LEDGER Q5 (not applied; this file only)
- Replace "ALL 5 SIGNALs are the cheapest worlds" with "all 5 SIGNALs are
  among the 9 valid worlds under 0.05 core-min (5/9 vs 0/16 above)".
- Mark p = 0.006 / 0.085 as ONE-SIDED (two-sided 0.012 / 0.167).
- Q5's own competitor (b) "near-deterministic so clean thresholds pass"
  survives here; its (c) "tiny worlds cannot host strange mechanisms" was
  not tested.

8. Next (design only; no compute authorized here)
- Pass-3 gate: flag a world whose decisive statistic has zero between-seed
  variance in the frozen CONTROL/pilot rows (would have flagged 321a, 5516,
  71b6 before the probe).
- Build each world's own simpler_alternative as an arm (LEDGER Q6 rule):
  5/5 Pass-4 kills here were such identities.
- Re-probe 37e3 W5 and ae38 W5 with ~3x seeds: the only power-limited NULLs.
