APORIA -- WHICH ROADMAP PROBLEMS ARE SDPs (from the operator, 2026-09-10)
Read techne/acquisition/GAP_FIXTURE_SDP.json and techne/ARSENAL_ROADMAP.md
Tier 7.

Techne measured where the free conic path actually fails instead of trusting
the roadmap's MOSEK row. CLARABEL -- interior-point, Apache-2.0, installed and
previously unmeasured -- reaches 1.8e-9 on theta(C_5); it and SCS both solve to
n=120; BOTH FAIL at 1e10 spectral spread, returning different wrong answers on
a problem with a certified-feasible point. One regime, not a general gap.

DELIVER (clears TECHNE-31, with Harmonia)
1. the open problems on your side whose computational form is an SDP or a conic
   program -- P17 variational/extremal, flag-algebra work, anything in the
   69-proposal annex that reduces to one.
2. for each, the expected SIZE and the expected CONDITIONING, even to an order
   of magnitude. A guess labelled as a guess is usable; silence is not.
3. whether any of them needs a VERIFIABLE CERTIFICATE rather than a float. If
   yes, say so loudly: no double-precision solver serves that at any price,
   MOSEK included, and the answer is arbitrary precision rather than a purchase.

REPORT: the list with size and conditioning per entry, or "no SDPs on the
roadmap" -- which closes REQ-029 and saves $4,300.
