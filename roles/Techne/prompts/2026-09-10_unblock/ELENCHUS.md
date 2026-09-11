ELENCHUS -- ADVERSARIAL REVIEW OF ONE FIXTURE (operator, 2026-09-10)
Read techne/acquisition/GAP_FIXTURE_SDP.json case C_illcond_1e10 and
techne/scripts/capability_gap_fixture.py.

Techne built a capability-gap fixture to decide whether a $4,300 MOSEK purchase
is justified. Its one failing case is hand-built by Techne and unreviewed. Both
free solvers return DIFFERENT wrong answers on it -- CLARABEL
infeasible_inaccurate, SCS unbounded -- on a problem Techne believes has a
certified-feasible point (X = I/m satisfies trace X = 1 and X >> 1e-6 I).

DELIVER (clears TECHNE-38)
1. a verdict: is C_illcond_1e10 a SOLVER FAILURE, or a badly posed instance
   that fails for a reason Techne did not see? Attack the feasibility claim
   first -- it is the load-bearing one.
2. if badly posed: the specific defect, and whether any reposing of it still
   fails both solvers.
3. if a genuine failure: whether ONE instance licenses the word "gap", or
   whether a purchase needs a family of them.

Techne's own caveat already says a single instance is a CANDIDATE gap and not a
solver verdict. The request is to confirm or kill that, not to soften it.

REPORT: the verdict, the defect if any, and whether a purchase may cite this.
