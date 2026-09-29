+==============================================================================================================+
| REVIEW PACKET: PKG-F SELECTION-SIGNAL PROBES (v2-v5b) + LEARNED WINDOW CRYPTICITY                           |
| Author: Ensorain (M2, seat m2-32b65655)   Date: 2026-09-29                                                   |
| For: HITL operator + external reviewers   Status: DEV probes, per-tick precommitments (not preregistered)     |
| Self-contained: every load-bearing number is inline. No repo access is needed.                              |
+==============================================================================================================+

-----
0. SUMMARY
-----
Two ARC3 dev lines reached resting points today. Both contain a self-correction that a reader should see first.

(A) PKG-F: can obsolete distinctions stay stored and be IGNORED rather than discarded?
    - YES in these worlds, IF the readout's selection signal comes from the current regime.
    - The first apparent success at DISCOVERING that signal (v3) was an artefact. It was withdrawn after the next test.
    - A model-free detector (v5) then did discover it: 16/16 switches, 0/16 false alarms, harm 0.000 vs -1.26.
    - Its power fades below ~100 same-cell pairs. So, in these worlds, does the harm (exploratory).

(B) Learned window crypticity D_k: can a learned model say how much a bounded window misses (an LM02 moderator)?
    - With a good learner, YES: rho .946 vs truth.
    - With a weak learner it fails SILENTLY toward "the window is sufficient". That is the dangerous direction.
    - A model-quality gate catches catastrophic failures but not partial ones.
    - Net: a gated learned D_k is a ONE-SIDED lower bound.

-----
1. WORLDS AND INSTRUMENTS
-----
(A):
- The frozen LM01 world families at L2 (read-only use): F3_switch (obsolete episodes) and F2_latent (stationary twins,
  the no-change control); generators cp and tt; dev seeds in 9.8M.
- Substrate: the frozen LM01 SELECTIVE arm at cap cells/4.
- Readout: S(q) + a * g(q), where g is a nearest-Hamming residual smoother over the stored records and a is in
  {0, .25, .5, 1}, chosen on a holdout.
- Metric: dAC on the headline (never-seen) test vs S alone.
(B):
- 24 held-out random binary unifilar machines (S = 3-5), T = 4000.
- D6 = the model's log-loss from the last 6 symbols minus that from the full past.

-----
2. RESULTS (A): PKG-F, obsolete stored history
-----
Holdout used to choose a, and the resulting F3 harm (dAC vs S):
  all history (random 20%)          -0.74 .. -2.21 (mean -1.26)       the readout is fooled by the old regime
  last 20%, handed in (v2)          ~0                                selection, not storage, is the problem
  v3: BIC residual segmentation     F3 7/8 fresh at 0, BUT stationary twins "change" in 6/8
  v4: same on an order-agnostic     twins 1/8 false (fixed), BUT F3 detected only 4/8, harm back to -0.61
      substrate
  v5: model-free same-cell          F3 16/16 detected (all at .667-.673 of the stream), twins 0/16 false,
      detector                      F3 harm 0.000, twins cost 0

v5 statistic:
- For successive records of the same cell, take the squared disagreement.
- Split score = straddling mean - same-side mean.
- Null: within-cell time permutation, 200 draws; accept at p < .01; recurse on the later part.

The correction (process honesty):
- v3's failure on twins was first attributed to a "learning curve". That was wrong: v3's residuals come from the
  FINAL model.
- The corrected hypothesis was committed BEFORE the next run: retention recency of the bounded substrate.
- v4 confirmed it: shuffled training removed the false alarms.
- v3's F3 success therefore came from a RECENCY PRIOR, not from discovery. It must not be cited as "discovered
  recency".

v5b power vs repeat density (L2 thinned to a fraction f of records; fresh seeds):
  f = .25 (~570 pairs): detected 8/8, false 0/8, undetected harm -0.02 .. -0.54
  f = .10 (~110 pairs): detected 0/8, false 0/8, harm ~0
  f = .05 (~30 pairs):  detected 0/8, false 2/8 (1 seed, 2 correlated variants; at the 30-pair floor), harm ~0

-----
3. RESULTS (B): learned crypticity
-----
  C1  CSSR_EM learned D6 vs true D6                 rho .946  (survived)
  C3  true D6 vs state entropy H6                   rho .721  (REFUTED; H6 over-counts states that predict alike)
  exploratory: gain of discovery over STAT6 at T = 16000 vs {true D6, learned D6, H6} = .922 / .910 / .606
  X1  random-restart HMM8 D6 vs true D6             rho .695  (REFUTED)
      Shape: D6 ~ 0 on exactly the 4 worlds where random-init EM failed (true D6 ~ .05).
  K1  quality gate (held-out loss < STAT6) catches silent failures: 5/7 (REFUTED; misses partial failures)
  K2  gated D6 vs true D6                           rho .900  (survived)
  K3  worlds passing the gate                       12/24     (survived; the rejected set includes the window-sufficient
                                                               worlds)

-----
4. WHAT THIS DOES AND DOES NOT ESTABLISH
-----
DOES:
- (A) In F3 L2 worlds, stored obsolete history is harmful only through the readout's selection signal. A selection
  signal discovered from the stored records themselves removes the harm, and it costs nothing on stationary twins.
- (B) The predictive window cost D_k is the right moderator (not state entropy). A learned D_k is reliable only as a
  lower bound, behind a quality gate.
DOES NOT:
- Anything about multiple or gradual switches, drifting nuisances, decaying reliability, or other readout families.
  F3 L2 has ONE sharp switch at a fixed 2/3 point: the detector's easiest case.
- That the detector "fails only where it is not needed". That is the v5b co-variation, exploratory, and untested on a
  world where harm and repeat density are decoupled.
- That a small learned D_k means the window suffices. It does not (K1 shape).
- Anything about WTP-LM01, which is frozen, on HOLD, and not used beyond read-only world generators.

-----
5. PROCESS NOTES / DEFECTS
-----
- Result JSONs were gitignored repo-wide (`**/results/`). They were force-added once found. It is now in the seat's
  resume rule.
- LM01 errata recorded outside the freeze:
  - E-2: outputs are bitwise platform-bound (Windows vs Linux ULP), found by the MWO-0003 FP-001 probe;
  - E-3: transient float overflow in the frozen CP selective arm's training; final predictions finite.
- All design choices after the first run in each line were made on aggregate results, with fresh seeds for every
  precommitted test. But the same author designed, ran and judged everything.

-----
6. DECISION / RECOMMENDATION (HITL's call)
-----
Ensorain's lean:
- Freeze both lines as dev results.
- Carry into the next designs:
  - (A) -> PKG-F v0.2's learned-regime arm;
  - (B) -> LM02's one-sided moderator rule.
- The next PKG-F step needs a NEW world variant (harm without same-cell repeats; multi-switch). That is a design task
  and should be reviewed before building.
"Not worth continuing" is a legitimate answer for (B): its practical content is one rule ("gated D_k is a lower
bound").

-----
7. QUESTIONS FOR THE REVIEWER (written to resist agreement)
-----
Q1 Is v5 just an oracle in disguise? Same-cell disagreement is a very direct regime probe in a world whose switch
   re-randomizes every cell. Would it survive a switch that changes only a subset of cells?
Q2 v5b's co-variation (power and harm fade together) may be one confound: fewer records mean a weaker S and a weaker
   g. Is "the detector fails where it is not needed" a property of the problem or of this readout?
Q3 Is D6 circular as an LM02 moderator? It is computed from the same kind of model whose gain it predicts. The
   cross-family test (X1) failed.
Q4 Should the v3 episode be counted as a near-miss that the protocol caught, or as evidence that the per-tick
   precommitments are too weak? The wrong mechanism was stated in a committed file for one tick.

-----
8. ARTIFACTS (branch ensorain/base-role-adopt-2026-09-23 on origin)
-----
(A):
- ensorain/arc3/RESULTS_PKGF_PROBE.md (v2-v5b with every precommitment);
- code pkgf_cp.py, pkgf_cp2.py, pkgf_cp3.py, pkgf_cp3_sparse.py;
- results in ensorain/arc3/results/pkgf_cp*.json;
- precommit commits 4ef32124c (v3), f11553f85 (v3 correction + v4), 370922f19 (v5), d17be0163 (v5b);
- design: ensorain/arc3/packages/PKG_F_CAUSAL_SELECTIVITY.md v0.2.
(B):
- ensorain/arc3/suff/CRYPT_LEARNED.md;
- code crypt_learned.py, crypt_crossfamily.py, crypt_gate.py;
- precommit commits e0a67493c, f5eb1437a, 6c3723bcc;
- LM02 design: ensorain/arc3/packages/PKG_LM02_DESIGN.md v0.2.

+==============================================================================================================+
| END. "Not worth continuing" is a first-class answer for either line.                                          |
+==============================================================================================================+
