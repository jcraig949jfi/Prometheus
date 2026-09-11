# READOUT -- Specimen 3 (Q045 unreachable class) -- first execution, 2026-09-11

**Prereg:** `PREREG_Q045_specimen3_2026-09-01.md` (filed 2026-09-01, commit efddd98f7, before any run).
**Run of record:** run 2, 2026-09-11 12:37:35Z to 13:01:46Z (1,450.6 s), PID 6132, worktree
`F:\Prometheus-worktrees\hephaestus-base-role`, base SHA ca300bcfa, dirty=True (the corrections
below were uncommitted at run time; they are committed with this readout).
**Result rows:** `hephaestus/closure_results/q045_lost_class.json` (30 targets x 4 arms, every witness
and alias listed). Run 1 is kept as `q045_lost_class_RUN1_superseded.json` (see section 4).
**Author:** Hephaestus (conflicted: author of the gauntlet, the basis, the prereg and the runner).
All numbers E3 (executed this session, read from the JSON).

## 1. Predictions, read exactly as preregistered

| # | preregistered statement | observed | verdict |
|---|---|---|---|
| P1 | >= 90% of LOST targets classify OPERATOR | 18 of 20 = 0.90; 2 INCONCLUSIVE (B did not reach); 0 SEARCH_ROUTING | TRUE, **at the line** (see 1a) |
| P2 | 100% of CONTROL targets SEARCH_ROUTING at margin A0, robust | 10 of 10, all robust; first A0 witness at depth 1 (4 targets) or 2 (6) | TRUE |
| P3 | A2_LEAK = 0 | 0 of 20 | TRUE |
| P4 | every C witness is robust under the shift | 20 of 20 targets have a C mechanism-bearing witness; 20 of 20 have a robust one | TRUE by the preregistered sentence; the runner's coded predicate (`C_robust == OPERATOR`, 20 vs 18) prints FALSE -- an encoding error, see 3c |
| P5 | some LOST targets have coerced aliases in A0 that die on the exhaustive check | 0 of 20 LOST targets have any A0 alias | **FALSE** (falsified prediction) |

**1a. P1 sits on its own gate.** 18/20 is exactly 0.90. With n = 20 the standard error of a proportion
at 0.9 is 0.067; the gate is not separated from the observed value by its own error, so "P1 TRUE" is
a statement about the rule's wording, not a discrimination. The substrate-relevant coordinate is
separate and not marginal: **20 of 20** LOST targets have NO witness and NO alias in A0, A1 (= A0
here) or A2 after 300,000 evaluations each, and **20 of 20** are reached robustly once `p05` is
named (arm C). The two non-OPERATOR rows are INCONCLUSIVE because arm B (the generic vector
language) did not reach them, and both route through `p07`/`p08`, which carry a scalar-typed
intermediate that B's six vector-only ops cannot express; two CONTROL targets (`p09(X, p07(X))`,
`p08(X, p07(X))`) show the same B = 0 while A0 reaches them at depth 2. B's failure is a property
of B as preregistered (section 3 of the prereg, "generic small vector language"), and the prereg's
section 7 names this case: "P1 fails because B does not reach: the target family exceeds 'small
generic program'; report." Reported. No reclassification.

**1b. P5, falsified.** The prediction was that Q045's "label leaks" (programs agreeing on the six
probes but differing elsewhere) would appear from inside the gauntlet on the LOST set. They did
not: no A0 or A2 program among 300,000 evaluated per target agreed with any LOST target on the six
probes. The phenomenon does exist in this run, on the CONTROL set: `p09(X, p07(X))` has 4 A0
aliases beside 1 mechanism-bearing witness and `p01(p03(X))` has 1 alias beside 4. So the alias
column works; the prediction about where aliases would fall was wrong. Recorded as counterfeit-
museum exhibit 009 (`hephaestus/counterfeit_museum/README.md`).

## 2. Two-coordinate result (never folded into one number)

- Coverage of the substrate question: 20 of 20 LOST targets are outside the impoverished
  inventory's reach at depth <= 4 under the gauntlet (A0/A2 witnesses 0, aliases 0), and 20 of 20
  are inside it once the operator is present (C). 10 of 10 CONTROL targets are inside without it.
- Classification under the preregistered rule: 18 OPERATOR, 2 INCONCLUSIVE(B), 0 SEARCH_ROUTING,
  0 INCONCLUSIVE(C). Eligible count 20; attainable range for P1 was 0..20 with INCONCLUSIVE
  possible on any row; both branches were reachable.

## 3. Tooling corrections made at first execution, all before a verdict was read

Every one of these was found because the committed runner (efddd98f7, "committed UNRUN") and the
frozen gauntlet (1f4c5ca72) met TINYPROG data for the first time today. None changes a
preregistered rule; each is a code path that did not implement the rule as written.

- **3a. Runner sort (TypeError).** Canonical order sorted S (int) and V (tuple) signatures together.
  Now V only; S was never eligible. Order over eligible targets unchanged.
- **3b. Runner closure enumerator under-enumerated the FULL inventory.** `range(0, size - 1)` never
  paired a size-(n-1) left argument with the size-0 terminal on the right, so `op(p(X), X)` and even
  `op(X, X)` at size 1 were missing for binary ops. Measured against the world's own
  `world3.build_closure` on the same six probes: full-inventory V-signatures at size <= 5 were
  2,975 (runner) vs 3,502 (world); impoverished 1,366 vs 1,366; impoverished at size <= 8 61,230
  vs 61,230. After the fix all three are set-identical and minimal sizes agree; candidate counts
  match the world's (12,716 / 4,771 / 333,667). The dossier's 3,502 / 1,366 / 2,136 reproduce.
  Run 1 (19 OPERATOR / 1 INCONCLUSIVE / 0 SEARCH_ROUTING on a differently selected target set) was
  produced with the defective enumerator and is superseded, not deleted.
- **3c. P4 encoding.** The runner encodes P4 as `C_robust == OPERATOR`; the prereg says "every C
  witness is robust". The two differ whenever a non-OPERATOR row has a C witness (the two
  INCONCLUSIVE rows do). The prose is the preregistration; the code is corrected in this commit to
  count targets-with-a-C-witness; the run-of-record JSON carries the old predicate value (FALSE)
  and this readout carries the prose evaluation (20/20). Both stay visible.
- **3d. Gauntlet coercion was bool() (closure_test.py).** For vector-valued outputs `bool(vec)` is
  True on every probe, so every vector program "matched" the target on the six probes and on the
  1,290-point exhaustive domain. Before the fix the gauntlet would have reported A0 mechanism-
  bearing witnesses for every LOST target and classified all 20 SEARCH_ROUTING -- P1 would have
  failed for a reason with no substrate content, on the specimen chosen as the OPERATOR positive
  control. The spec now declares COERCE (exact tuple equality, the prereg's own "equal on the six
  probes"); the default remains bool(), and the boolean specimens' outputs are byte-identical
  under the new code (six arm/spec pairs re-run; evaluated 300000/300000/107629 and 55/908/20).
- **3e. Gauntlet inner loop was O(pool^2 x |last layer|) and uncounted by the budget.** One target
  ran 907 s CPU without finishing. Depth tag on layer entries; predicate identical; the same six
  arm/spec pairs byte-identical. A target now takes ~48 s at budget 300,000 per arm.

## 4. What run 1 and run 2 share and where they differ

Same gauntlet code (3d, 3e applied), same basis hash 7f2ef69196e7f128, same depth/budget, same
verification domains, same R_imp5 and R_imp8 (identical to the world's in both runs). Different
LOST target set because 3b changed which size <= 3 behaviours existed to be selected (run 2's first
target, `p05(X, X)`, could not be generated by run 1's enumerator at all). Run 1: 19/1/0. Run 2:
18/2/0. Both INCONCLUSIVE rows in run 2 are B-did-not-reach through `p07`/`p08`; run 1's single
INCONCLUSIVE row is the same family. Neither run has an A0/A2 witness or alias on any LOST target.

## 5. What this does and does not establish (prereg section 7 and 8)

- The gauntlet **can** report OPERATOR on a wall where an operator is missing by construction, and
  SEARCH_ROUTING A0 on behaviours the impoverished inventory reaches: the discriminator has a
  demonstrated positive case and a demonstrated negative case in one world. Arm C is the injected-
  success (cheat) control: closure appears exactly when the operator is present.
- It does NOT establish anything about Apollo, about representation (arrow one), about whether
  `p05` is "the" missing operator beyond the world's construction, or about specimens 1 and 2 --
  whose outputs are unchanged under the corrected code and whose earlier readings therefore stand
  as they were, including their non-OPERATOR classifications.
- It does establish that the "standard Forge test" declared at Addendum 3/4 had not been shown to
  work on a non-boolean target until today, and that a committed-unrun runner carried three
  defects. The instrument was green for the wrong reason on two of the three; the third would have
  changed which targets were selected. CALIBRATION.md carries all of them.

## 6. Reproduce

    git -C <canonical> worktree add <path> -b hephaestus/<task> origin/main
    cd <path>; set PYTHONPATH to <path>
    python -m hephaestus.src.closure_q045 8 30000000      # ~25 min; refuses the canonical checkout
    # deterministic: probes seed 20260827 (world), shift rng seed 20260901, enumeration order fixed

Expected: `closure_sizes` 3502 / 1366 / 61230, `summary.LOST` 18 / 2 / 0 with A2_LEAK 0 and
C_robust 20, `summary.CONTROL` 10 / 10.
