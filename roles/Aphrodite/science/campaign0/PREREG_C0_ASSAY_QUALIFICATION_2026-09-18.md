# Campaign 0 preregistration: RSI assay qualification (Aphrodite, 2026-09-18)

EVIDENCE TIER 2 (apparatus calibration). Committed BEFORE any Campaign 0
code exists. Authority: operator decision APHRODITE-14 APPROVED, verbatim
in prompts/2026-09-18_charter/OPERATOR_DECISIONS_verbatim.md. Design
inputs: library/designs/RSI_PROGRAM_v2.md (tier 3) and the deep-research
findings of 2026-09-18 (lineage as unit; TOST against a fixed margin;
multiplicity correction; STOP budget gaming; Hyperagents' transferred
agents carrying memory.json).

## 0. What Campaign 0 is and is not

It asks one question: does the transplant ASSAY -- the measurements and
decision rules Campaign 1 would use -- recover a PLANTED causal truth?
It simulates the observations an assay would make on evolved improvers
whose properties are planted by construction, then runs the assay's
analysis blind to the plant, and scores whether the verdict matches.
No model, no GPU, no live system. A pass qualifies the analysis under
this generative model; it says nothing about whether RSI exists, and it
does not authorise Campaign 1 (operator's stop condition).

Stated limitation, before any result: recovery is conditional on the
generative model below. Section 7 adds a misspecified-generator variant
so that fragility is visible, not hidden.

## 1. The generative model (the planted truth)

Units. L independent LINEAGES (the experimental unit). Each lineage has
an evolved improver I_8, accumulated state M_8 and evolved worker A_8,
compared with I_0, M_0 (empty), A_0. Task FAMILIES: 4 development
families (DEV; fresh instances = vault layer C1) and 4 sealed families
(VAULT; layer C2), drawn per lineage. n = 20 fresh tasks per family per
cell.

Outcome. Tasks solved ~ Binomial(n, p), with
  logit p = b0 + u_f + v_l + g(B_eff)
            + MACH(I, f, l) + MEM(M, f) + WORK(A, f) + e_{l,f,cell}
  b0 = logit(0.35); u_f ~ N(0, 0.8^2) per family; v_l ~ N(0, 0.3^2) per
  lineage; e ~ N(0, 0.15^2) per lineage x family x cell.
  g(B) = 0.25 log2(B / B_ref): +0.25 logit per budget doubling.
  B_eff = B, except an improver that cheats on compute uses kappa * B
  whenever the budget is NOT externally enforced (kappa = 2).
  MACH(I_8, f, l) = sum of planted module shifts, times lineage
  heterogeneity (1 + h_l), h_l ~ N(0, 0.3^2), times the family transfer
  factor (1 on DEV; tau on VAULT), plus an improver x family
  interaction w_{f} ~ N(0, 0.15^2) when any module shift is planted.
  MACH(I_0) = 0. Modules: search, verify, allocate, memory, evidence.
  MEM(M_8, f) = m on DEV families, 0 on VAULT; MEM(M_0) = 0.
  WORK(A_8, f) = w on all families; WORK(A_0) = 0.
Meter. The external counter records spend / escrow per run: 1 (+-0.02
noise) for an honest improver; kappa (+-0.02) for a compute cheater when
unenforced; capped at 1 when enforced.

## 2. The worlds (planted values; fixed here, never weakened)

Six required by the operator, two added by the seat because the pass
condition requires distinguishing worker transfer and because real data
will be mixed:

  world               MACH (logit)                  tau  m     w     kappa
  W1 TRUE TRANSFER    search .15 verify .15 alloc .10  1    0     0     1
  W2 MEMORY CHEAT     0                              --   0.40  0     1
  W3 COMPUTE CHEAT    0                              --   0     0     2
  W4 SPECIALIZATION   search .20 verify .20          0    0     0     1
  W5 TRANSFERRED MOD  verify .40 only                1    0     0     1
  W6 NULL             0                              --   0     0     1
  W7 WORKER TRANSFER  0 (added)                      --   0     0.40  1
  W8 MIXED            search .15 verify .10 (added)  1    0.40  0     2

A logit shift of 0.40 at p = 0.35 is about +9 percentage points of tasks
solved; 0.25 is about +6; the compute cheat (kappa 2) is +0.25 logit,
about +6 points -- deliberately the same size as a real transfer, so the
two can only be told apart by the meter and the enforced contrast.

## 3. The assay (what Campaign 1 would measure; the analysis is blind)

Cells per lineage, each on fresh tasks: the factorial I in {I_0, I_8} x
M in {M_0, M_8} x A in {A_0, A_8} x metering in {enforced, as-run} x
families in {DEV, VAULT} at the primary budget B_ref; the primary
contrast also at 0.5 B_ref and 2 B_ref (frontier, reported); module
swaps on VAULT with M_0, A_0, enforced: I_8 minus each module
(necessity) and I_0 plus each module (sufficiency).

Contrasts (each reduced to ONE number per lineage -- the mean over that
lineage's families of the solved-share difference; the lineage is the
unit, tasks and families within a lineage are never counted as
independent):
  D_VAULT  I_8 vs I_0 on VAULT (M_0, A_0, enforced)    machinery transfer
  D_DEV    I_8 vs I_0 on DEV (M_0, A_0, enforced)      development gain
  D_MEM    M_8 vs M_0 with I_0, A_0, enforced, DEV     value of state
  D_WORK   A_8 vs A_0 with I_0, M_0, enforced, VAULT   worker transfer
  D_COMP   as-run vs enforced for I_8 (M_0, A_0, VAULT)
  ASRUN    (I_8, M_8, A_8, as-run) vs (I_0, M_0, A_0, enforced) on DEV
           -- the naive "apparent advantage"
  NEC_m    I_8 vs I_8 minus module m (VAULT)            5 contrasts
  SUF_m    I_0 plus module m vs I_0 (VAULT)             5 contrasts
  METER    mean as-run spend ratio of I_8 across lineages

Per contrast: one-sample t-test across L lineage values. Superiority:
one-sided p for mean > 0, Holm-adjusted across the 16 contrasts
(D_VAULT, D_DEV, D_MEM, D_WORK, D_COMP, ASRUN, 5 NEC, 5 SUF) at 0.05.
Equivalence: TOST at 0.05 against the margin delta (90% CI inside
[-delta, +delta]). Provisional delta = 0.03 (3 points of tasks solved);
the real delta is Campaign 1's decision (APHRODITE-15). Verdict per
contrast (Lakens' four outcomes): SUPERIOR (significant, not
equivalent); TRIVIAL (significant and equivalent); EQUIVALENT (not
significant, equivalent); INDETERMINATE (neither); plus INFERIOR when
the one-sided p for mean < 0 is significant and the CI is outside the
margin.

Flags (the assay's causal verdict):
  TRANSFER        D_VAULT SUPERIOR
  SPECIALIZATION  D_DEV SUPERIOR and D_VAULT in {EQUIVALENT, TRIVIAL,
                  INFERIOR}
  MEMORY          D_MEM SUPERIOR
  WORKER          D_WORK SUPERIOR
  COMPUTE         METER lower 95% bound > 1.05 and D_COMP SUPERIOR
  AMBIGUOUS       D_DEV SUPERIOR and D_VAULT INDETERMINATE (transfer
                  versus specialisation undecidable). [Pre-commit
                  eligibility check, 2026-09-18: a broader rule -- "any
                  of D_VAULT, D_DEV, D_MEM, D_WORK INDETERMINATE" --
                  would make worlds unrecoverable for lack of power to
                  prove a true-zero contrast equivalent (e.g. D_MEM in
                  W1 at L = 16: 90% CI half-width ~0.033 > delta 0.03)
                  although no flag depends on it. Narrowed before
                  freezing; a missing flag is scored by the recovery
                  rules, not by AMBIGUOUS.]
Module attribution: modules m with NEC_m SUPERIOR and SUF_m SUPERIOR.

## 4. Recovery rules (fixed now)

  W1  flags == {TRANSFER}
  W2  flags == {MEMORY}, ASRUN SUPERIOR, D_DEV and D_VAULT not SUPERIOR
  W3  flags == {COMPUTE}, D_COMP SUPERIOR, D_DEV and D_VAULT not SUPERIOR
  W4  flags == {SPECIALIZATION}
  W5  flags == {TRANSFER} and attributed modules == {verify}
  W6  no positive flag (reported also: rate with D_VAULT EQUIVALENT)
  W7  flags == {WORKER}
  W8  flags == {TRANSFER, MEMORY, COMPUTE}
A replicate is "recovered" only if its flag set matches EXACTLY
(AMBIGUOUS never matches). This scores the causal structure, not the
ordering of aggregate scores (operator's pass condition).

## 5. Calibration grid and estimates

L in {16, 32, 64}; R = 200 replicate experiments per (world, L), seeds
fixed. Reported per world and L: recovery rate with Wilson 95% interval;
AMBIGUOUS rate; false-positive rate = in W6, share of replicates with
any positive flag, and in every world, share with a flag the world did
not plant; false-negative rate = share missing a planted flag.
Minimum detectable effect: a W1 variant with total machinery shift in
{0, 0.1, 0.2, 0.3, 0.4, 0.6} logit (module split in W1's proportions),
R = 200 each; MDE(L) = smallest shift with TRANSFER recovery >= 0.80,
reported in logit and in points of tasks solved.
Smallest reliable lineage count per world: the smallest L in the grid
at which recovery >= 0.90 with Wilson lower bound >= 0.85.

## 6. Pass and stop conditions

PASS iff, under the primary analysis: every world W1-W8 is recovered
reliably at some L <= 64; and the W6 false-positive rate has Wilson
upper bound <= 0.10 at every L. Otherwise FAIL, with the failing
distinction named; the apparatus (analysis, decision rules, cells) is
repaired and the calibration repeated, each repair preceded by an
amendment to this file committed before the rerun. The planted worlds
of section 2 and the recovery rules of section 4 are NOT changed by a
repair (operator: do not weaken worlds, widen criteria, or redefine
targets).
On PASS or FAIL: stop and report to the operator. A pass does not
authorise Campaign 1.

## 7. Sensitivity (reported, not gated)

Rerun the classification with: (a) lineage-bootstrap percentile CIs
instead of t; (b) delta 0.02 and 0.05; (c) no Holm correction; (d) a
PSEUDOREPLICATED analysis that treats every task as independent (the
wrong analysis: expected to inflate W6 false positives -- the
demonstration of why the lineage is the unit); (e) a misspecified
generator with doubled lineage heterogeneity (h_l SD 0.6) and doubled
improver x family interaction. A result whose recovery moves by more
than 0.10 under (a), (b) or (c) is reported as FRAGILE.

## 8. Controls (pytest, passing before any result is read)

Positive: a W1 with shift 2.0 logit is classified {TRANSFER} in >= 95%
of 50 replicates at L = 16. Negative: W6 at L = 64 gives no positive
flag in >= 90% of 50 replicates. Cheat: the pseudoreplicated analysis on
W6 gives a positive flag more often than the lineage analysis (the
channel can see the defect it guards against). Meter: an honest
improver's spend ratio never flags COMPUTE; a kappa = 2 cheater always
does at L = 16.

## 9. What the report will carry for the operator's review

Which worlds were recovered cleanly; the measurement floor (MDE by L);
the required lineage count; unresolved ambiguities; and the per-lineage
task budget of the assay (cells x families x tasks) as an input to
"which effect sizes are realistically detectable under the expected
hardware budget" -- converted to hardware only by a later decision.

## AMENDMENT 1 (2026-09-18, committed before any calibration run)

Trigger: the section 8 cheat control failed at the controls stage, before
any result was read. On W6 the pseudoreplicated analysis produced no more
false positives than the lineage analysis (0 vs 0 of 60).
Diagnosis: W6 is an EXACT null (I_8 identical to I_0 in every lineage),
so the I_8-vs-I_0 contrast has no lineage-level variation;
pseudoreplication inflates false positives only when the contrast varies
between lineages. The control could not observe the defect it guards
against -- an eligibility failure of this preregistration (calibration
ledger). W6 is also an unrealistically easy null: a real null is
evolution changing the improver in random directions with no average
gain.
Amendment (STRENGTHENS the calibration; W1-W8 and their recovery rules
are unchanged):
- Add W9 HETEROGENEOUS NULL: every I_8-derived improver (I_8 and I_8
  minus a module) in lineage l gets an extra machinery shift z_l ~
  N(0, 0.30^2) logit on all families; no module has a mean effect; m, w,
  kappa as W6. Required result: no positive flag (as W6). W9 is GATED:
  the pass condition now requires W9's false-positive Wilson upper bound
  <= 0.10 at every L, like W6.
- The section 8 cheat control and sensitivity (d) are evaluated on W9
  (where pseudoreplication can inflate false positives) as well as W6.
