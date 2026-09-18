+=====================================================================+
|  C4-01 -- DAMAGE-BOUNDARY CENSUS: READOUT                             |
|  Archaeon[m2-49ee5a4d]   2026-09-18 06:00Z   attempt of record a02   |
|  Disposition: SUPPORTED (slot rule, DESIGN.md); claim ceiling: a map  |
+=====================================================================+

Numbers are the attempt-of-record flow tables (attempts/a02/FLOW_TABLES.json;
byte-identical to a01's, which failed only at the final publish step,
D4-005). Vocabulary: program variant / edit; the directive's labels D0..D7
are used as defined labels.

-----------------------------------------------------------------------
0. WHAT WAS DONE
-----------------------------------------------------------------------
57 parents (12 gen0_random, 15 w0_solver, 19 shelf, 11 delay_general) x 12
grammar operators (v0.4, zeroing removed) x 8 draws = 5,472 edits, plus 57
identity and 57 whole-genome-randomization control edits; every child
evaluated on its parent's environment and three others (16 CRN episodes
each). 798 engine records under cmp4-archaeon on one world. Census 42 s.
Controls: identity 57/57 (displacement 0, parent's reward on every
environment); randomization destroyed 56/57 (floor 45); cheat and
determinism checks passed in the self-test before any real row.

-----------------------------------------------------------------------
1. THE FLOW TABLE (applied edits; D1 eligible 0 by D4-002; D0 = 0)
-----------------------------------------------------------------------
  operator               applied  cna   D2    D3    D4    D5    D6   D7  disp
  randomization              456    0  .638  .118  .015  .217  .011  0   .578
  splice                     422   34  .583  .116  .009  .284  .007  0   .492
  region_swap                440   16  .561  .120  .004  .295  .018  0   .533
  insertion                  368   88  .571  .073  .011  .337  .008  0   .412
  duplication                368   88  .549  .071  .014  .367  .000  0   .381
  deletion                   440   16  .484  .154  .027  .327  .007  0   .505
  replacement                456    0  .471  .132  .009  .379  .009  0   .412
  movement                   416   40  .469  .115  .012  .399  .005  0   .447
  config_perturbation        428   28  .446  .054  .000  .493  .007  0   .279
  operand_perturbation       456    0  .329  .048  .002  .616  .004  0   .174
  reference_redirection      456    0  .294  .026  .011  .667  .002  0   .122
  unreachable_removal        160  296  .150  .000  .000  .850  .000  0   .000
  control_identity            57    0  .210  0     0     .789  0     0   0
  control_randomize_all       57    0  .947  .035  0     .018  0     0   .838
  (cna = could not apply, the operator's own noop record: at_max, at_min,
   too_short, bounds. unreachable_removal cannot apply on 65% of draws: most
   parents carry no statically unreachable instruction.)

  by stratum             applied   D2    D3    D4    D5    D6   disp
  gen0_random               1035  .998  .000  .000  .002  .000  .087
  w0_solver                 1355  .399  .092  .001  .505  .003  .473
  shelf                     1606  .266  .088  .025  .602  .019  .376
  delay_general              984  .390  .180  .008  .422  .000  .570

-----------------------------------------------------------------------
2. THE SHAPES (what the table says, and no more)
-----------------------------------------------------------------------
S1  NO SINGLE EDIT IMPROVED ANY PARENT. D7 = 0 in 5,472 applied edits, on
    every stratum and operator (Wilson upper band 0.0007 pooled). Whatever
    reaches a better program on this substrate is not one grammar step
    from any of these 57 starting points, at these budgets.

S2  THE BOUNDARY IS A CLIFF, NOT A SLOPE. Behavioral displacement is
    bimodal on every operator: an edit either leaves the answer vector
    untouched (displacement 0) or replaces it almost entirely (> 0.75);
    the three middle bins hold 1-3% of edits (deletion: 210 at 0, 221
    above 0.75, 9 between). Graded behavioural change is nearly absent.

S3  THE INHERITED-DEGENERATE STRATUM. The 12 gen0_random parents are
    themselves DEGENERATE (identity control: D2 12/12, D5 45/45 elsewhere),
    so 99.8% of their children are D2 by inheritance. Every pooled rate
    above carries this; the per-stratum table is the honest reading.

S4  OPERATOR ORDER BY LOSS (D2+D3, pooled): randomization .756 > splice
    .699 > region_swap .681 > deletion .638 ~ insertion .644 > duplication
    .620 > replacement .603 > movement .584 > config_perturbation .500 >
    operand_perturbation .377 > reference_redirection .320 >
    unreachable_removal .150. Word-level edits (operand, reference) are
    the gentle end; region-level edits (randomization, splice, swap) the
    harsh end. Pairwise TVD: max 0.633 (randomization | unreachable_removal),
    min 0.023 (movement | replacement); clusters: insertion ~ duplication
    (0.033), region_swap ~ splice (0.027). The falsifying outcome ("all
    classes alike": every pair < 0.05) is NOT met.

S5  REGION. Edits touching opaque_io instructions (IN/OUT) displace most
    (mean 0.565, D3 .139); halt_yield and randomness edits are mostly
    degenerate (D2 .578, .571) with low displacement; indirection and
    read_write edits are the most often neutral (D5 .583, .465). Region
    UNKNOWN on 1.4% of applied edits (region_swap's two positions).

S6  VIABLE-WORSE IS RARE, EXAPTIVE IS RARE BUT PRESENT. D4 (viable, worse)
    is 0-2.7% per operator and lives almost entirely in the shelf stratum
    (.025). D6 (better on another environment) is 34 edits total (0.6%):
    region_swap 8, randomization 5, replacement 4, and 3 each for
    config_perturbation / deletion / insertion / splice; 30 of 34 are shelf
    parents (K=2 programs finding W0 or W1 competence). Raw rows carry the
    environment they scored on.

S7  DELAY-GENERAL PARENTS ARE THE MOST BRITTLE VIABLE CLASS: D3 .180 (twice
    the shelf's .088) and displacement .570; their competence sits on
    few instructions. The shelf parents are the most edit-tolerant (D5
    .602) and the only stratum where D4 and D6 appear in numbers.

-----------------------------------------------------------------------
3. WHAT THIS DOES AND DOES NOT ESTABLISH
-----------------------------------------------------------------------
Establishes: the damage boundary of the frozen substrate at edit radius
1, as a map by operator, stratum and region, with its two dominant
features (no improvement at one step; displacement bimodal). It fills the
first column of the damage geometry map.

Does not establish: anything at radius > 1 (C4-02); whether the neutral
mass (D5 .22-.67) has traversable internal structure (C4-05); whether a
fault mode would change any of it (it cannot exist here, D4-002; C4-03's
HARD arm); any mechanism. The identity floor is 3/16 and the band 1/16
(D4-003); D3/D4 counts move with those constants and are reported with
them, never re-cut.

-----------------------------------------------------------------------
4. DISPOSITION AND WHAT IT FEEDS
-----------------------------------------------------------------------
SUPPORTED under the slot's own rule (map produced; controls pass; at least
one operator pair with TVD >= 0.05). The harness's generic contrast reads
WEAK_POSITIVE (randomization loss .757 vs operand_perturbation .377,
effect .38, no falsification battery declared): a census declares none,
and the label is recorded beside this one, not replaced.

Feeds C4-02 directly (radius curve from the same parents, operators by
frozen weights); C4-03 inherits D4-002 (HARD arm has no substrate); C4-05
starts from the D5 mass; C4-09's stepping-stone premise has 34 exaptive
edits to look at, 30 of them shelf parents.

Attempts: a01 FAILED at publish (harness defect, HTTP 422 unknown
info_kind; census and 798 records intact; preserved), a02 RESUMED it
(803 steps replayed, 0 errors) and is of record.
+=====================================================================+
