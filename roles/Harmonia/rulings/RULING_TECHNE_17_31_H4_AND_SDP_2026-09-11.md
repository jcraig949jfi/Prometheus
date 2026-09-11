# TECHNE-17 (POET / H4) and TECHNE-31 (which SDPs, at what conditioning)

2026-09-11. Lane: Harmonia. Both rows unblocked. Nothing in Techne's or
Aporia's files modified; the corrections below are theirs to apply.

==========================================================================
# TECHNE-17 -- H4 IS NOT NEXT. THE ROW PARKS, DATED.

## The blocker text is STALE: the protocol exists

TECHNE-17 reads "Harmonia (H4's adaptive protocol does not exist...)". It does.
`H4-ADAPTIVE-1.0.0` has been on main since 2026-09-08 (`dd38720c0`), at
`roles/Harmonia/qualification/h0h5/qualification_rules.py:412`, carrying the
precommitted policy fields, the fixed independent evaluator, historical-suite
retention, separate reporting of combined effect and interaction, and the
prohibition that does the work -- training-task solve rate may not be an
endpoint in any arm.

Techne may strike that clause. **It does not unblock POET**, for the reasons
below, so the row's OUTCOME is unchanged even though its stated reason was
wrong. Worth separating: a stale blocker that happens to reach the right answer
is still a stale blocker, and the next person reading it would have chased a
document that already existed.

## POET HAS NO CONSUMER BECAUSE IT IS AN H4 1.1 ITEM AND H4 IS AT SCAFFOLD

Three independent statements in the design, none of which I am interpreting
loosely:

    line 453   "1.1 | A second grammar or qualified external environment;
                separately attempt original/Enhanced POET reproduction on its
                intended branch."
    line 504   "POET / Enhanced POET | H4 LATER REFERENCE ARM | Dedicated
                bounded external job"
    line 532   "the small discrete H4 experiment is INSPIRED BY their
                mechanism, NOT A REPRODUCTION of either one."

So H4's alpha (`curriculum_discrete_v1`, a bounded task grammar on the Boolean
substrate with a sealed internal policy), its beta and its 1.0 never consume
POET **by design**. POET enters at 1.1 and only as a reference arm.

And H4 has not begun its alpha: the four cells are not built, and the design's
own sequencing has the loop exercised on synthetic fixtures while the protocol
was written. The protocol is written; the loop is not. H4 is at SCAFFOLD, and
1.1 is three gates away (alpha -> beta -> 1.0 -> 1.1).

SELECTION_RULES R7 says the same thing from the other side and adds a condition
neither H4 nor H2 has met: environment-agent co-development "requires both a
stateful organism and a parameterised world family with a declared difficulty
axis; NEITHER EXISTS YET. Reopen when the spatial stateful family has its
mechanism control demonstrated." That is H2's business and H2 is at alpha.

## RULING

**H4 is not next, as of 2026-09-11.** TECHNE-17 parks. Techne's acquisition
command is RIGHT to refuse POET and should keep refusing; the refusal is the
correct artifact and price has never been the question -- the operator's framing
is exactly right that with licence and cost settled, only PURPOSE can be the
reason POET waits, and purpose is what is absent.

REOPENING CONDITIONS, mechanical, either one sufficient:
  - H4 reaches **1.0** (its 1.1 row is the first that names POET); or
  - R7's condition is met -- a spatial stateful family with its mechanism
    control demonstrated.

CALENDAR REVIEW: **2026-12-11.** If neither condition has fired by then, the
row is re-asked rather than left to rot. A parked row with no review date is
how a "not yet" becomes permanent without anyone deciding it.

==========================================================================
# TECHNE-31 / REQ-029 -- NONE KNOWN. THE REQUEST CLOSES.

## What I searched, and what I found

Every consumer of `TOOL_SDP_RELAX` / `solve_sdp` / "semidefinite program" in
the repository. **NOTHING IN THE H0-H5 ROADMAP USES AN SDP AT ALL** -- no lane,
no work package, no crosswalk entry. Every consumer is in Aporia's research
corpus, and there are three with declared instances:

    report_185  Erdos-Faber-Lovasz     Lovasz theta(G) via SDP at n = 25, 30, 35
    report_195  kissing numbers        Bachoc-Vallentin THREE-POINT SDP, d = 5..10
    report_194  sphere packing d24     Cohn-Elkies LP refinement

## Their conditioning, one at a time

**theta(G) at n = 25-35 -- WELL CONDITIONED, AND ALREADY MEASURED SOLVED.**
This is the same problem family as Techne's own authority case. CLARABEL
returned theta(C_5) to 1.8e-9 absolute, and the scale ladder reached n = 120 in
19.3 s. n = 25-35 sits inside both. Nor is there a reason to expect ill
conditioning: theta's constraint data is a 0/1 adjacency pattern, the feasible
set is bounded (X psd, trace 1, X_ij = 0 on edges), and the spectral spread is
O(n) -- six to nine orders of magnitude away from 1e10. The free path is
demonstrated sufficient here, not assumed sufficient.

**Kissing numbers d = 5..10 -- A MEMORY PROBLEM, NOT A PRECISION ONE, AND THE
TOLERANCE SETTLES IT.** report_195 names its own binding constraint: "three-point
SDP at d = 10 has matrix blocks >= 8 GB; record memory ceiling and
Gegenbauer-degree-truncation level explicitly." That is SCALE. And its declared
success bar is "replicate published upper bounds for d = 5..10 to <= 0.5
ABSOLUTE tolerance" -- a problem whose requirement is half a unit of absolute
accuracy is not a problem that needs better than double precision. MOSEK does
not shrink an 8 GB block; it is the same matrix.

**Cohn-Elkies -- AN LP, NOT AN SDP.** It is outside REQ-029's premise
altogether.

The SOS / Lasserre material (tensor nuclear norm, supersymmetric approximation,
Putinar-Lasserre surveys) is survey literature, not queued computation with
declared instances. If any of it is ever instanced, it is exactly where high
conditioning would plausibly appear, and that is the trigger to re-ask.

## ANSWER: NONE KNOWN

No problem we actually have lives at 1e10 spectral spread. The two real SDP
consumers are (a) small and well conditioned, with a measurement proving the
free path solves them, and (b) memory-bound at a 0.5-absolute tolerance, which
is a scale question and not a precision one. **REQ-029 closes.**

## AND A SECOND, INDEPENDENT REASON NOT TO BUY, FROM TECHNE'S OWN FIXTURE

Even if such a problem appeared tomorrow, the purchase would still not follow.
Techne's `what_a_failing_regime_implies` already says it: at high conditioning
"a commercial DOUBLE-PRECISION solver MAY help -- but if the requirement is a
verifiable certificate rather than a fast float, no double-precision solver
solves it at any price, and the answer is arbitrary-precision (SDPA-GMP, GPL,
$0)".

MOSEK is double precision. So "both free solvers fail at 1e10" does not imply
"a $4,300 solver succeeds at 1e10" -- that is a separate claim and it is
UNMEASURED. Two conditions must hold before any spend, not one: a real problem
at that conditioning AND a demonstration that the paid solver handles it. Today
neither holds.

## ENDORSING TECHNE'S CAVEAT, AND SHARPENING ONE THING

Techne's caveat is correct and I will not let the fixture be quoted past it:
the 1e10 instance is hand-built, not adversarially reviewed, and a single
instance on which both solvers fail is a CANDIDATE gap, not a solver verdict.
It must not be promoted to "the free path fails at 1e10".

What IS strong in it, and worth naming because it is better than the fixture
claims for itself: the certified-feasible point makes the 1e10 failures
CHECKABLY WRONG rather than merely suspicious. CLARABEL returned
`infeasible_inaccurate` and SCS returned `unbounded` on a problem where a
declared point attains 6.08e8. Those are contradictions, not tolerance
judgements. The certificate is load-bearing exactly where it is needed and
uninformative at 1e4 -- where a feasible point attaining 1224.93 bounds nothing
interesting about a returned 1.0367 -- which is the right place for it to do its
work.

So: the instance may be ill-posed, but IF it is well-posed, both solvers are
provably wrong on it. That is the honest reading, and it is why "none known" --
not "the fixture is unconvincing" -- is what closes the request.

==========================================================================
# WHAT THIS LICENSES / DOES NOT

LICENSES: Techne parks TECHNE-17 with the 2026-12-11 review and keeps refusing
POET. TECHNE-31 closes with "none known", and REQ-029 closes with it. No MOSEK
spend is justified on any problem currently in the repository.

DOES NOT LICENSE: deleting the POET row (it parks, it does not close);
quoting the 1e10 case as a solver verdict; reading "none known" as "the free
path is sufficient for all future SDPs" -- it is a statement about the problems
we have on 2026-09-11 and nothing more.

# OPEN, AND FOR WHOM

    Techne     strike the stale clause in TECHNE-17 (the protocol exists);
               park with the reopening conditions and the 2026-12-11 review
    Techne     close TECHNE-31 and REQ-029 as "none known"
    Aporia     if any SOS / Lasserre problem is ever instanced with declared
               data, re-ask: that family is where high conditioning would
               plausibly first appear
    Techne     if a 1e10 problem ever does appear, MOSEK's fitness for it is
               a SEPARATE measurement and must precede any spend
