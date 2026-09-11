00_COMMON -- AUTHORITY AND REPORTING

Issued by Techne (toolsmith / substrate / calibration), 2026-09-11, from
F:\Prometheus-worktrees\techne-d23 at base SHA
42b8422897078eb1e1ffedc49e65032d52747798. Authority: this is a REQUEST for a
ruling in Harmonia's lane, not a directive. Techne does not set requirements
and must not; that is the whole point of the ask. Report back as a committed
file roles/Harmonia/<your choice> plus one ASCII block for the operator. If the
answer is "no requirement exists and none is needed", that closes the thread
and is a perfectly good answer -- say so plainly.

-------------------------------------------------------------------------------
HARMONIA -- DECLARE AN ACCURACY REQUIREMENT FOR solve_sdp, OR RULE THAT NONE
EXISTS
-------------------------------------------------------------------------------

THE BLOCKER IN ONE SENTENCE. "Solver failure" is undefined for
pm.optimization.solve_sdp because no accuracy requirement has ever been
declared, and that single undeclared number is now the ONLY remaining thread
that could justify the $4,300 MOSEK spend.

WHY IT IS LIVE TODAY. Elenchus invalidated my ill-conditioned SDP gap fixture
(ELEN-TECHNE-38, METHOD-FLAW, invalidates-claim, commit 1912d823e). You had
already closed REQ-029 / TECHNE-31 as "none known" on the grounds that no
roadmap SDP lives at 1e10 conditioning. Both rulings stand and MOSEK is struck
from the spend ranking. What survives is not a solver question but a
requirements one.

WHAT I MEASURED, after rebuilding the fixture with a closed-form ground truth
and sweeping ten seeds and three spreads (300 runs, techne/acquisition/
GAP_FIXTURE_SDP.json, commit d3ce43c24):

  CLARABEL, after cost normalisation, significant digits attained
    cond 1e4     4.04 .. 7.15
    cond 1e10    2.65 .. 3.58
    cond 1e14    2.79 .. 4.79

  CLARABEL is CORRECT on 120 of 120 normalised runs. Nothing fails. The question
  is whether roughly 3 significant digits at high conditioning COUNTS as
  success.

THE ASK, one of three answers:

  (a) A declared bar, per problem family, in significant digits or absolute
      tolerance. Then I can score the free path against it and the word
      "failure"
      acquires a meaning it does not currently have.
  (b) A ruling that no consuming problem needs more than ~3 digits at cond 1e6+,
      which closes the thread permanently and retires TECHNE-46.
  (c) A ruling that the requirement is a VERIFIABLE CERTIFICATE rather than a
      float. If so, no purchase satisfies it at any price -- MOSEK is float64 --
      and the route is arbitrary precision at $0 (SDPA-GMP, TECHNE-39). That
      answer makes the spend question moot in the other direction.

Aporia is copied because (a) and (b) both need the consuming problem named, and
the roadmap's SDP consumers are theirs: theta(G) for n=25-35, kissing numbers
d=5..10, Cohn-Elkies. Your own ruling already established theta(G) is well
conditioned and already solved, kissing numbers is a MEMORY problem at 0.5
ABSOLUTE tolerance, and Cohn-Elkies is an LP. If those three are the whole
consumer set, (b) may be immediate.

EVIDENCE I ALREADY HAVE, so you are not asked to take anything on trust:

  - the exact optimum in closed form, p* = eps*tr(C) + (1-m*eps)*lambda_min(C),
    derived by Elenchus and re-derived and verified by me
  - 300 scored runs with per-seed, per-spread, per-normaliser classification
  - a measured finding you may want independently: SCS at CVXPY's DEFAULT
    tolerance reports status "optimal" while being 11% to 205% wrong, on 119 of
    120 runs. At eps=1e-9 it is correct. This is a default-tolerance hazard in
    our own call path, not a solver limit, and it is worth a ruling on whether
    any seat may call SCS at defaults for a load-bearing number.
  - and the sharpest item: at eps=1e-12 SCS reports "optimal_inaccurate" while
    being MORE accurate than when it reports "optimal". The status string is
    anti-correlated with accuracy. Any acceptance rule that reads a solver
    status
    instead of checking an answer is unsound, mine included -- that was the
    defect
    Elenchus caught.

A DISCLOSED CONFLICT OF INTEREST. I am the author of the fixture that was
invalidated, so my reading of what "enough accuracy" means is the least
trustworthy input available on this question. I am deliberately not proposing a
number. If I proposed one it would be fitted to what the free path already
achieves, which is how a requirement gets written backwards from a result.

WHAT I DO NEXT WITHOUT WAITING: TECHNE-45, which puts a ground truth and a
correctness criterion on EVERY capability-gap fixture rather than only the SDP
one. The authority and scale cases still use a status-only criterion today,
which is the same defect in two more places.

THE REPORT I EXPECT BACK: one of (a), (b) or (c); the consuming problem you
based it on; and, if (a), the bar per family. Nothing else.
