# Dials retrospective (EXPLORATORY -- hypothesis generation, no gate)

Currency: 2026-09-24. Prompted by the operator's "dials of intelligence"
text (roles/Ensorain/prompts/2026-09-24_dials_of_intelligence/). The text
names Cosmos as the natural home for a dial SEARCH; this note only asks
what Ensorain's existing rows can say, in Ensorain's lane.

Question: in the one dial pair Ensorain swept on a full grid --
STABILITY (proximal pull lam: high = stable/less plastic; 3..100) x
CONSOLIDATION DEPTH (sweeps: 5..20) -- does competence (held-out R^2)
depend on the dials separately, or on their COUPLING?

Instrument: two-way ANOVA with replication (6 instances per cell),
interaction F test; R^2 clipped to [-1,1] (divergence = fail).
Controls: synthetic additive grid p = 0.85 (no false coupling);
synthetic coupled grid p = 1.2e-4 (detects real coupling). A first
instrument -- permutation null on 4x3 cell medians -- had a null 95th
percentile of ~0.8 and could not have fired; it is kept in the file and
reported as blind, not as evidence.

Rows: e1p5_calibrate.jsonl (TT latent order, caps 128-512),
e2_calibrate.jsonl (correct family, TT / MAT / CP worlds). Caps 192-512
of E1.5 use the SAME 192-float architecture: one test, not six.

    grid                      F      p       interaction share
    E1.5 TT cap 128          1.58   0.17    0.07
    E1.5 TT cap 160          0.22   0.97    0.02
    E1.5 TT cap >=192        2.70   0.022   0.17
    E2 TT world              1.54   0.18    0.10
    E2 MAT world             0.44   0.85    0.04
    E2 CP world              0.18   0.98    0.02

Reading (provisional): six independent grids, one nominal hit (p .022)
that fails a 6-test correction (.0083) and did NOT replicate in the E2
TT world (p .18). Competence here is mostly MAIN EFFECTS: a near-universal
good stability setting (lam ~ 10-30) and "deeper consolidation helps";
coupling carries <= 17% of variance. For this dial pair, in these
worlds, "intelligence = phase behaviour of couplings" is NOT supported.

Limits: one learner family (ALS), narrow ranges (lam 33x, sweeps 4x),
6 instances per cell, one competence ruler (held-out R^2). Coupling may
live across wider ranges, other dial pairs (plasticity x replay was
never gridded -- E0's buffer/replay genes were only evolved), or
precede competence in time (no per-event traces were saved). The
method -- replicated cells, an interaction test with additive and
coupled synthetic controls -- is the transferable part.
