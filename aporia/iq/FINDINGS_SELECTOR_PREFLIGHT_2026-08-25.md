# SELECTOR pre-flight — VACUOUS. The DV cannot vary, and the one positive is a constant.

Preregistration `aporia/iq/PREREG_SELECTOR_2026-08-25.md` committed **01bfbfa6**, which predicted
this outcome **in advance** precisely so it could not later be re-read as a kill.
Ledger: `aporia/iq/RESULT_SELECTOR_PREFLIGHT.json`.

---

## Verdict: VACUOUS_DV_CANNOT_VARY. The five-selector comparison did not run.

    frozen pool            27 candidates, sha256 2ad41a2d... (hashed BEFORE any score)
    expressible            18 · not expressible 9, each with a named reason
    ΔE distinct values     {0.0, 0.016667}
    ΔE variance            1.46e-05
    candidates with ΔE > 0 1        (PF3 threshold: 3)

**All readings use the rotation-wrapped abstain pool.** Measuring ΔE under the guessing pool
would hand any firing-but-wrong candidate a 1-in-4 floor — the contamination CEILING-ABSTAIN
characterised, and here it would have manufactured exactly the positive ΔE the pre-flight exists
to detect the absence of.

## The one positive is an answer counterfeit

`pigeonhole_check` scored ΔE = +0.016667, two tasks of 120. The declared adaptation rule wires
both its `int` parameters to the same slot, giving `pigeonhole_check(max_value, max_value)`.
Executed:

    pigeonhole_check(v, v) for v in 0..5  ->  [False, False, False, False, False, False]

**It is a constant.** It writes `comparison = False` unconditionally, `score_by_comparison__g`
fires, and it wins the two tasks whose answer happens to be "No" (9 such tasks exist in the
battery). No reachability is involved.

So the honest count of candidates that move ΔE **for a reason related to capability is zero**,
not one. PF3 fails either way; recording it as 1 would overstate the pool's headroom.

## What this does and does not mean

**It is NOT the preregistered KILL.** The KILL requires PF3 to *pass* and then R-ranking to fail
against compression or random. That comparison was never reached. **ΔE-as-selector is UNTESTED
here, not refuted** — and the preregistration says so in advance rather than after seeing the
number.

**It is a statement about the substrate's headroom.** It confirms Lexis's ΔS = 0.00% from a
different direction: not one primitive in the frozen forge pool supplies vocabulary that moves
the reachable set. Two independent instruments, same conclusion — the 20 unreached tasks need
vocabulary this library does not contain.

**Consequence for SELECTOR as designed:** it cannot be run on this substrate with this candidate
pool. A five-selector comparison over a DV with variance 1.46e-05 and one distinct non-zero value
— itself a constant-answer artifact — would have produced a confident "no selector beat random"
that meant nothing. That is the artifact this arc has produced three times and the reason the
pre-flight was made mandatory.

## An instrument defect I caught mid-run

The first execution reported **5 expressible of 27**, including `all_but_n` as NOT expressible —
a primitive I had already successfully ported in IQ-PORT-1. Cause: builtin annotations stringify
as `<class 'int'>`, not `int`, so the adaptation table missed every builtin-typed parameter.

Corrected: **18 expressible**. The expressibility count is a reported number, so an
annotation-formatting bug is a measurement bug, not a cosmetic one. Both readings are on the
record. Note the direction: the defect *understated* the pool, which would have made the vacuity
verdict look better supported than it was.

## The nine that cannot be expressed at all

`solve_sat`, `expected_value`, `counterfactual_intervention`, `solve_constraints`,
`bat_and_ball`, `solve_linear_system`, `temporal_order`, `track_beliefs`, `sally_anne_test` —
each blocked by a parameter or return type with no corresponding blackboard slot, reason recorded
per candidate. **9 + 18 = 27, asserted in code**; nothing dropped.

`temporal_order` is worth naming: it is the primitive that would target the unsolved
`temporal_ordering` category, and it is not expressible because
`list[tuple[str, str, str]]` has no slot. The library contains the verb and the substrate has
nowhere to put it.

## Scope

- Single seed. ΔE per candidate is an exhibited lower bound: the candidate inserted at every
  valid position in the ceiling body, best accuracy taken. A candidate that only helps in
  combination with another candidate would read 0 here.
- The adaptation rule is mechanical and declared before scoring, which makes it reproducible but
  crude — a hand-written adapter could express more than 18, as IQ-PORT-1's hand-written port
  demonstrates. **The 18 is a floor on expressibility, not a ceiling.**
- `C` untouched, `apollo/src/` untouched, battery unmodified.
