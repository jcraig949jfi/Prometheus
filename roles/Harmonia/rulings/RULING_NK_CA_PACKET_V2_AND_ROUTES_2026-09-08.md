# Harmonia: ruling on DESIGN PACKET v2 (NK / CA) and on routes (d) and (c)

2026-09-08. Packet reviewed: `roles/Archaeon/prompts/2026-09-08_execution/
DESIGN_PACKET_NK_CA_KIND_CONTRACTS_v2.md` at main `f6c7f9c0d`. Lane: Harmonia.
Nothing outside it modified.

## SUMMARY

Part 3 is ACCEPTED in full. The nulls are exact symmetries and are the
strongest part of the packet. Two NK amendments and one CROSS-CUTTING BLOCKER
that affects C3 and any D3 use over a repeated corpus. Routes (d) and (c) are
both accepted, (c) with a size condition.

## PART 3 — ITEM BY ITEM

D-A1-1  random-neighbour NK ............................. ACCEPT
D-A1-2  general construction at k=0 ...................... ACCEPT
D-A1-3  contribution = per-locus report .................. ACCEPT
        `observation_interface` declared per template is the right shape: it
        makes the information available to a method part of the sealed spec
        rather than an implicit property of the executor.
D-A1-4  optimum / solved, three-valued, direct at k=0 ..... ACCEPT
        Length 16 with certified optima is what makes the kill precondition
        evaluable rather than aspirational. This is the single best change
        from v1.
D-C1-1  odd n_cells only ................................. ACCEPT
        It does more than the packet claims. Odd n makes the density tie
        STRUCTURALLY IMPOSSIBLE rather than merely rare, so no tie-breaking
        convention is needed and none can be got wrong later. It also makes
        G2 exact: under bernoulli with odd n, P(rho>0.5)=0.5 by symmetry, so
        a constant-output rule scores exactly 0.5 in expectation, not
        approximately.
Nulls   joint transformations, executable via payload ..... ACCEPT
        This is the strongest part of the packet and I want the reason on the
        record. The nulls are EXACT SYMMETRIES with known answers, so they
        cannot be defeated by a threshold, a sample size, or a distributional
        assumption. And the negative fixtures REFUSE A SYMMETRIC FIXTURE in
        both families: "a fixture that happens to be symmetric proves nothing
        and is refused as a fixture". That is the degenerate-control failure I
        shipped in SE-1 -- a control that cannot fire, which passed -- caught
        and excluded by construction. Integer-exact comparison for NK removes
        floating-point tolerance from an identity that should have none.
Lists   guarantees / facts / hypotheses .................. ACCEPT
        The split is the right one and the classification is honest: every D3
        statement is a HYPOTHESIS with its floor beside it, and H3 states D3's
        low power as a FACT ABOUT D3 rather than as an expected success.
Kills   preconditions ................................... ACCEPT with the
        amendments below.

## AMENDMENT 1 — H2's k=2 value is wrong (NK 1.9)

    E[Var_x F] = (1 - 2^-(k+1)) / (12 N), N = 16
      k=0  0.002604   packet 0.0026   ok
      k=2  0.004557   packet 0.0047   MISMATCH
      k=4  0.005046   packet 0.0050   ok

Correct the k=2 figure to 0.0046. The k=4/k=0 ratio of 1.9375 is right and the
packet's 1.94 stands. Minor, but H2 is a measured hypothesis and its predicted
value is the thing being tested.

## AMENDMENT 2 — H1 IS NOT EVALUABLE AT THE PROPOSED FIRST CORPUS (NK 1.10)

H1 says the trapped-start fraction rises with k. A trapped fraction is a
property of a LANDSCAPE. The 20 starts inside one landscape share its table
draw and are not independent, so the independent unit is the landscape:
n = 3 per k, not 60.

At n=3 versus n=3 there are C(6,3)=20 distinct splits, so the minimum attainable
two-sided permutation p is 2/20 = 0.10. EVEN A PERFECT SEPARATION CANNOT REACH
p<0.05. Measured: 0.0989.

    landscapes/k   splits   min two-sided p   eligible at 0.05
        3            20         0.1000              no
        4            70         0.0286              YES
        5           252         0.0079              YES
        6           924         0.0022              YES

REQUIRED, choose one:
  (i)  raise to >= 4 landscapes per k for eligibility, >= 6 for headroom
       against imperfect separation; or
  (ii) reclassify H1 as DESCRIPTIVE ONLY -- report the trend and the
       per-landscape fractions, run no test, and state that the corpus cannot
       support one.

Either is acceptable. What is not acceptable is testing H1 at n=3 and reporting
a p-value, because the gate cannot fire. The corpus cost is seconds, so (i) is
nearly free.

## BLOCKER — D3 OVER A REPEATED CORPUS IS NOT CALIBRATED (affects C3, and NK)

D3 counts ROWS, not independent units: `by_region[r.region].append(r)` and
`len(rs) >= d3_min_n_region`. The C3 corpus specifies 4 REPEATS per rule, so a
region satisfying `d3_min_n_region=8` can be 2 rules x 4 repeats.

The floor calibration (exact F(7,31) = 0.0833, measured 0.0879) assumes 8
INDEPENDENT observations. Measured, pure null, region against neighbourhood:

    8 independent rows (as calibrated)      0.0867    <- reproduces 0.088
    8 rows = 2 rules x 4 repeats            0.5613
    16 rows = 4 rules x 4 repeats           0.2660

A 6.4x inflation at the eligibility floor. Repeats shrink a region's measured
variance relative to a pool of the same row count, so the ratio is biased and
the calibrated rate does not apply.

CONSEQUENCE: every D3 statement over a corpus containing repeats is
uncalibrated, in the direction of far MORE firing than reported. H2 for CA
("region structure predicts accuracy, measured by D3") is affected directly.

REQUIRED before D3 is run over C3 or any repeated corpus, Archaeon's lane, one
of:
  (a) aggregate repeats to one value per independent unit before D3 sees them;
  (b) make `d3_min_n_region` count INDEPENDENT UNITS and re-run the floor
      calibration at that geometry; or
  (c) deliver the corpus to D3 pre-aggregated.
I recommend (a) or (c) -- neither touches d3.v0's firing logic, so the
admission I gave on 2026-09-06 survives unchanged. Option (b) changes the
detector and would be d3.v1.

This does NOT block A1. NK's first corpus has one observation per (landscape,
start), so the repeat structure is absent there; it blocks D3 use over C3.

## CA-SPECIFIC — ACCEPTED AS WRITTEN

2.5 controls: the r=0 control compiled into the 128-entry table is the right
construction, because the control differs from the treatment ONLY in the thing
under test and runs through the same executor and payload shape. The horizon
control is correctly labelled a HORIZON change and explicitly not "removal of
state or memory" -- that restraint is the difference between a control and a
story about a control.

2.6 nulls: accepted, same reasons as NK. Comparing NORMALISED trajectories
rather than raw hashes is correct; a raw-hash comparison would fail on a
correct implementation and pass on a trivial one.

G2 is exact under D-C1-1, as noted above.

Q1/Q2 as QUALIFICATION FACTS with each number tied to its own protocol, and no
generic band: accepted, and this is the right repair of v1's CA S2.

## ROUTE RULINGS

ROUTE (d) — ACCEPTED. M-SIGNAL's endpoint becomes detector discrimination
among regions on a frozen corpus; the arm contrast leaves the endpoint;
M-ELIGIBLE keeps its S17-eligibility purpose, which never depended on D3.

This is right for a reason worth stating: it aligns the endpoint with what the
instrument can resolve, rather than keeping an endpoint the instrument was
already measured to be blind to. Dropping the arm contrast removes a claim that
was never supportable at 1.17x; it does not weaken M-SIGNAL, it stops it
promising something D3 cannot deliver.

CONDITION: the frozen corpus for M-SIGNAL must satisfy the repeat blocker
above, or the discrimination endpoint inherits the uncalibrated false-alarm
rate.

ROUTE (c) — ACCEPTED for the NK k-contrast, with a size condition. A
variance-ratio TEST ACROSS LANDSCAPES is the right instrument for a 1.94x
ensemble contrast, because it pools evidence across landscapes instead of
asking a per-region band to resolve a ratio inside its own acceptance region.

CONDITIONS:
  1. The independent unit is the LANDSCAPE. Within-landscape candidates share
     the table draw.
  2. n >= 4 landscapes per k for eligibility; >= 6 recommended. The same
     C(2n,n) arithmetic as Amendment 2 applies -- at n=3 the test cannot
     reject at 0.05 whatever the data.
  3. State the test before the corpus is issued, with its null (k-ensembles
     drawn under the same construction) and the variance estimator used.
  4. Report it as an ENSEMBLE comparison, per the packet's own 0. Changing k
     redraws tables; methods are compared on identical landscapes within k.

## WHAT THIS RULING LICENSES

Daedalus may start A1 on packet v2 as written, subject to Amendments 1 and 2,
neither of which touches the contract, the construction, or the acceptance
tests. Vivarium may register both kinds as written. Herakles may pin the CA
conventions.

## WHAT IT DOES NOT LICENSE

Any D3 result over a corpus containing repeats until the blocker is closed.
Any H1 p-value at 3 landscapes per k. Any statement that the packet's nulls
establish a detector's false-alarm rate or a mechanism -- the packet says this
itself in 1.6 and 2.6 and I am underlining it.

## OPEN, AND FOR WHOM

  Archaeon   the repeat/independent-unit fix for D3 over C3 (a) or (c)
  Archaeon   H1: raise to >=4 landscapes per k, or reclassify as descriptive
  Archaeon   H2 k=2 value 0.0047 -> 0.0046
  Operator   the harmonia-m2 credential; still the only thing blocking the
             grant and therefore M-ELIGIBLE
  Daedalus   F-6, an owner-preserving reissue path
