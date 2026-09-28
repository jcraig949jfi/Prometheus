REPORT -- search leverage without recursion
============================================

1. WHAT I SET OUT TO TEST
-------------------------
The Aphrodite abstraction engine repeatedly shows "search leverage": a donor that
inherits the learned additive-fold abstraction (acc + {H}) spends much less search
than a pristine donor. The headline figure is about 40% less (8.57M-9.22M vs
14.51M-15.00M meta-charges in the 2026-09-26 campaign). But recursion, meaning the
inherited abstraction helping the donor derive a semantically new abstraction, keeps
failing. The question was whether leverage is an early form of recursion or a
different capability, and what experiment would connect the two. I made it testable
by breaking the 40% figure down cell by cell and family by family. Where does the
saving come from? Does any of it land on tasks the inherited abstraction cannot
express? Only that kind of saving could feed the derivation step with new material.

2. WHAT I DID
-------------
Data (read-only, committed): branch aphrodite/a16-campaign-2026-09-26 @ 4f937e88f,
  roles/Aphrodite/engine/A17_A_DONORS_2026-09-26.json (16 donor records),
  A17_CATALOGS_2026-09-26.json (catalog A families and roles),
  A17_E1_RESULT_2026-09-26.json, and the campaign report
  roles/Aphrodite/pivot/APHRODITE_AMENDMENT16_CAMPAIGN_REPORT_2026-09-26.md.
  For context only: COMPOUNDING_SYNTHESIS_2026-09-28.md on
  origin/aphrodite/compounding-2026-09-27 @ f6d60364a.
Code: I exported roles/Aphrodite/engine @ 4f937e88f with git archive into
  work/R-24/src and imported a17.py unmodified (fast evaluator on, as the gate
  admitted).
Scripts (mine): work/R-24/scripts/percell.py and work/R-24/scripts/analyse.py.
  - percell.py re-runs only the INHERITED-library searches for both donor kinds:
    G1 = L1 + pristine, P = pristine. It covers all 8 replicates of catalog A and
    uses the exact A17 cell labels and seeds: 4 OBSERVE families x 3 cells, and
    3 VALIDATE families x 8 cells. It records per-cell charges, whether the cell was
    solved and the solving body. 2 workers, 484 s wall.
  - analyse.py first checks the re-run against the committed records. It then breaks
    down the P-minus-G1 meta-charge gap by phase and family, including the extra
    selection candidates each donor evaluated.
  Command: env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE python3 scripts/percell.py
  then python3 scripts/analyse.py (output in data/analyse.out, raw in data/percell.json).

3. RESULT
---------
Reproduction: 16/16 donors match exactly. For each donor, observe-phase spend plus the
recorded selection-table cost equals the committed meta_charges with residual 0, and
the INHERITED validation mean cost matches to the unit.

Per family (8 replicates pooled; "solved" = found within the 250k escrow):
  phase  family      G1 solved  G1 mean   P solved  P mean   P/G1
  obs    add_ah      24/24      16,080    5/24      237,273  14.8
  obs    sub_az      24/24      21,722    0/24      250,000  11.5
  obs    fdiv_bf      0/24     250,000    0/24      250,000   1.00
  obs    gcd_al       0/24     250,000    0/24      250,000   1.00
  val    add_aa      64/64      30,436    0/64      250,000   8.2
  val    sub_ay      64/64      28,581    8/64      242,648   8.5
  val    gcd_bf       1/64     246,798    3/64      248,268   1.01
Every body G1 solved with is an instance of (acc + {H}). Its one gcd_bf "solve" is
(acc + (first // v)), which matches that family only on the development examples.

Breakdown of the mean meta-charge gap (P - G1 = 5.85M per replicate):
  - add/sub families (in the inherited schema's span): +8.29M
  - fdiv/gcd families (out of span): +0.02M (0.3% of gross saving; gcd_bf noise)
  - G1 evaluating a third selection candidate: -2.45M. That candidate (SCHEMA_0) is
    the re-derived inherited schema and costs exactly the same as INHERITED. P
    derived nothing, so it evaluated only 2 candidates.
  - Net: 5.86M (matches the recorded 5.85M)
Like-for-like (observe phase + INHERITED validation only), G1 is 54% cheaper, not
40%. The headline 40% is diluted by the duplicate candidate. The per-task ratio on
in-span families is 8-15x, and even that is a lower bound: 272 of P's 288 cells hit
the escrow cap, against 111 of G1's (and those 111 are all fdiv/gcd).

Plain conclusion: in this campaign the leverage is entirely in-span transfer. The
inherited abstraction shortens search only for tasks whose solutions are its own
instances. It gives exactly zero leverage on the non-additive families (fdiv, gcd),
the only ones that could have shown the donor something new. The derivation step
only sees certified classes built from solved observations. So the leverage just
feeds it more instances of the inherited schema, and anti-unification returns that
same schema; the donor traces record this, with candidate (acc + {H}) and 0 new
mechanism bodies on 8/8 replicates. Measured this way, leverage cannot be a
precursor of recursion. It is a different capability: object-level reuse, not
improvement of the improver.

What would link them (proposed, not run): split leverage into an in-span part and an
out-of-span part. Out-of-span leverage is the saving on families whose solving
programs are not instances of any inherited schema. Recursion needs out-of-span
leverage above zero, and in-span leverage adds nothing to it. The test: in a world
where composition is allowed and there are enough non-additive tasks (the W5/T4
world on the compounding branch), record both parts per donor replicate against
matched shams. Then ask whether out-of-span leverage predicts selecting a
semantically new, reusable schema, while in-span leverage does not.
  - The compounding branch has one forensic replicate (CON1) consistent with this:
    the composed library solved families that L1 and pristine both failed at 10M
    charges.
  - That replicate is the only committed example of out-of-span leverage, and it
    comes together with novelty.

4. DID IT RESOLVE THE QUESTION
------------------------------
Partly.
  - Resolved for this engine and campaign. The measured leverage is 99.7% in-span
    and 0% on out-of-span families, and the pipeline's structure means in-span
    leverage cannot produce a new schema. So here, "leverage YES, recursion NO" is
    expected rather than puzzling, and the two are different capabilities.
  - Not resolved in general. With only one out-of-span family type per role, and
    those families judged junk-prone by a later tribunal, I cannot say whether
    out-of-span leverage predicts recursion when it exists. That needs the proposed
    experiment in a world where it can occur.
  - I did not re-analyse the earlier Tier 3B (47x) and 3C (345x) figures. A later
    synthesis on the compounding branch says the old tribunal admitted only
    commutative bounded folds, i.e. G1's span, which suggests the same in-span
    explanation. That is unverified by me.
  - I also did not address the other packaged question: whether whole-program
    identity generalises beyond this DSL.

5. CONSEQUENCES
---------------
  - Premise correction (Aphrodite; anyone who quotes the figure): "about 40%
    cheaper" is not a clean leverage measure.
    - The donor meta-charge includes the cost of evaluating however many selection
      candidates a donor derives. A donor that re-derives its own inherited schema
      pays for an identical extra candidate.
    - The like-for-like saving is 54%, the per-task in-span ratio is 8-15x (a lower
      bound because of censoring), and the out-of-span saving is 0.
    - The figure should be reported split by span, not as one percentage.
  - Minor instrument issue (Aphrodite, a17.py r1()):
    - The R1b meta-cost fallback compares donors' meta_charges when both select new
      schemas. Because meta_charges grows with candidate count, that comparison is
      confounded by how many schemas each donor derived.
    - It did not trigger in this campaign, so no verdict is affected.
    - A future prereg should compare a fixed-candidate cost.
  - Positive analytic result: "in-span vs out-of-span leverage" is a concrete,
    cheap diagnostic that turns the open question into a measurable link. It should
    be added to donor traces in the composition-world assays.
  - This is consistent with, and adds numbers to, the compounding synthesis. That
    synthesis found the earlier negative was partly forced by the task world, and
    that the only non-additive observe families supplied were ones G1 cannot touch;
    the zero out-of-span leverage here is the measured form of that.
  - Who should know: the Aphrodite seat, and anyone citing leverage as progress
    toward recursive self-improvement.

6. COST
-------
  - Time: about 45 minutes of my own work.
  - CPU: about 16 CPU-minutes (2 workers x 484 s), under 100 MB RAM.
  - No GPU, cloud, holdout or database used.
  - Not done: re-analysis of the Tier 3B/3C leverage figures, the proposed linking
    experiment (it needs the composition-world foundry and more CPU than this
    budget), and the question of whether whole-program identity generalises.
