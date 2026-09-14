# Every CA success criterion in these libraries, its published-figure convention, its range and its floor

Herakles, 2026-09-11. Backlog C-1 and C-3. One place, so a sixth criterion
is added beside these and never instead of one. Every number below names
the commit or file it was measured in; nothing is from recall.

Conventions that apply to all five: periodic ring; `steps` is always
explicit; the eligible count is the number of initial conditions unless
the row says otherwise; the unit of analysis is the initial condition.

## The five criteria

    name                     library / kind          published figure it is comparable to
    ----                     --------------          ------------------------------------
    at_T                     evca (radius 3)         P_N of the EvCA line (Mitchell,
                             vivarium ca_density     Crutchfield, Das, Hraber 1993-95):
                                                     fraction of ICs whose lattice is
                                                     uniform in the IC's majority state
                                                     at step T. Requires odd N (a tie has
                                                     no target). C1-e reproduced 17 of 18
                                                     published cells with it (a91bce6c4).
    stable                   vivarium ca_density     NOTHING published. at_T AND one more
                             (derived from at_T)     update leaves the lattice unchanged.
                                                     Stricter than at_T by construction;
                                                     criteria_agree is reported per run.
    cellwise_majority_match  evca (radius 3)         NOTHING published. Mean over cells of
                             vivarium ca_density     agreement with the majority target
                                                     at T. Equals at_T EXACTLY for a rule
                                                     that always reaches a uniform state;
                                                     differs for maj (MAJ_STRUCTURAL_ZERO
                                                     .md s3). Added 2026-09-10 because
                                                     at_T gives random tables the single
                                                     point {0}.
    synchronisation          evca (radius 3)         NOTHING held yet. Fraction of ICs
                                                     whose lattice is uniform at T and at
                                                     T+1 and differs between them (a
                                                     whole-ring period-2 blink). The task
                                                     of Das, Crutchfield, Mitchell, Hanson
                                                     1995 (citation held: evca-review.pdf
                                                     cites it by name) and Jimenez-Morales
                                                     et al. 2001 (A_FIELD_MAP.md; citation
                                                     not yet held, MODEL_RECALL tier);
                                                     their rules are NOT recovered (L-7),
                                                     so no published P is comparable yet.
    block_output             eca (radius 1)          Footnote [13] of Capcarrere, Sipper,
                                                     Tomassini PRL 77:4969 (1996), at T =
                                                     ceil(N/2): a same-state adjacent
                                                     pair of the majority state exists
                                                     and none of the minority state; on
                                                     d = 0.5 strict alternation. Every IC
                                                     eligible, ties included, any N >= 3.
                                                     Reproduced 2026-09-11 (spec-
                                                     capcarrere-r1-density/REPORT.md).
                                                     Comparable to NOTHING in the
                                                     radius-3 line: rule 184 scores
                                                     0.000 under at_T (P6 there).

## Attainable range, chance floor, eligible count (C-3)

    name                     range   floor for a random / constant rule            measured where
    ----                     -----   -----------------------------------            --------------
    at_T                     [0,1]   {0}: 40 of 40 random 128-entry tables and      cs-c3-2 corpus,
                                     maj scored exactly 0.0. A gate on at_T        MAJ_STRUCTURAL_
                                     cannot be shown reachable from random         ZERO.md s1-2
                                     tables; it can only be shown reachable from
                                     a known organism. Eligible = n ICs (odd N).
    stable                   [0,1]   {0} on the same 40 tables (stricter than       same
                                     at_T). Eligible = n ICs.
    cellwise_majority_match  [0,1]   random tables 0.4998 mean, range              MAJ_STRUCTURAL_
                                     [0.4939, 0.5099] over 20 tables at N = 149,   ZERO.md s3
                                     100 ICs, 298 steps; sampling spread of the
                                     mean about 0.004. Floor is 0.5, not 0.
                                     Eligible = n ICs x N cells (a mean, not a
                                     fraction of ICs; SE is NOT sqrt(p(1-p)/n_ics)).
    synchronisation          [0,1]   {0} for every organism we hold, and for the    core.py
                                     positive control `blinker_rule_table` it       synchronisation_
                                     fires from a pre-synchronised IC only; no      score docstring;
                                     rule that SOLVES the task from random ICs      backlog C-2
                                     is held, so 0.0 cannot yet be separated
                                     from an unreachable target. Eligible = n ICs.
    block_output             [0,1]   0.5 ANALYTIC: a constant rule ends uniform,     spec-capcarrere-
                                     so it is correct on exactly the ICs on one     r1-density/
                                     side of 0.5. Measured: rule 0 at 0.5022,       PROTOCOL.md,
                                     rule 255 at 0.4978 (5 seeds, sum = 1000        REPORT.md
                                     correct exactly, N odd); 88 of 256 rules
                                     in (0.45, 0.55) under Bernoulli(0.5) ICs.
                                     Identity (204): 0.000 Bernoulli, 0.151
                                     uniform-density. Eligible = n ICs.

The contrast in the second table is the whole argument for having more
than one criterion, stated once: two of the five give a random table the
single point {0}, so no gate on them can be shown reachable from noise;
two put the floor at 0.5, so any number quoted on them is quoted as its
distance above 0.5; and one has no positive organism yet, so its zeros
are unmeasurable rather than structural until C-2 lands.

## Rules for adding a sixth

1. A row in both tables above, in the same commit as the code.
2. The published figure it is comparable to, or the word NOTHING.
3. Its floor for a random or constant rule, computed or measured, with
   the eligible count and the correct SE unit, before any organism is
   scored on it.
4. Positive, cheat and negative controls in the test suite.
