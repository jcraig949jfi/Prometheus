# Cycle 060 — the non-finite hole in the height family

**Techne, 2026-08-25. Campaign cycle 1 of 20 under `CAMPAIGN_ESCAPE_RATE_PREREG.md`.**
Controls FROZEN at `94970ea8`. Section 1 was committed BEFORE any measurement in this cycle.

---

## 1. PRE-REGISTRATION (committed before measuring)

**Work selected:** item (a) of the campaign backlog — findings #9–12, which are mine and need
nobody's ruling. Plus the beginning of item (c), Tier-2 invariant coverage, because the
adjudicator for (a) has to come from somewhere and the domain supplies it free.

**The question, stated before the population.**

> Q: On which inputs does the height family return a NUMBER that is not a height?

Note what that is *not*. It is not "does `mahler_measure([nan])` return NaN" — I already know it
does, from cycle 059's corrected sweep. It is a question about the **class**: whether the zero-
polynomial guards that every one of these functions carries are structurally blind to
non-finite coefficients, and whether the blindness reaches past the three functions the sweep
happened to call.

**Declared population, before sampling.** The FULL enumeration of scalar entry points in the
height family — `techne/lib/mahler_measure.py::mahler_measure`,
`techne/lib/mahler_measure.py::log_mahler_measure`,
`techne/lib/mahler_measure.py::is_cyclotomic`,
`prometheus_math/polynomial_length.py::polynomial_length`,
`prometheus_math/house.py::house` — crossed with the full non-finite input grid
{nan, +inf, -inf} x {degree 0, degree >= 1, leading position, trailing position}. Full scan, no
sampling, no ordered slice. Any wider arsenal claim is a SEPARATE population and will be
declared as one.

### Predictions

1. **At least 3 of the 5 scalar entry points return a non-finite float instead of raising, on
   at least one non-finite input.** Confidence **high**; **D0**. This is a mechanism claim, not
   a guess: every one of these functions guards the zero polynomial by testing `== 0` or
   `np.nonzero`, and NaN is non-zero under both, so the guard is structurally incapable of
   seeing it. *Opposite:* if fewer than 3 propagate, the guards are not uniformly structured and
   my model of this code family is wrong — which would be the more interesting outcome.
2. **`house([nan])` refuses, and `house([nan, 1.0])` propagates.** Confidence
   **moderate-to-high**; **D1**. If true, `house`'s apparent NaN-safety is an accident of its
   no-roots-on-a-constant branch, not a finiteness check — an incidental refusal that would be
   silently lost by any future refactor of that branch. *Opposite:* a refusal on the degree-1
   case means there is a finiteness check in this family I have not found, and the whole finding
   narrows.
3. **A NaN measure passes the Lehmer screen silently.** `mahler_measure(f) < 1.17628` is
   **False** for NaN, so a candidate whose measure failed to compute is classified as "not below
   the Lehmer bound" rather than raising. Confidence **high**; **D0** — IEEE-754 comparison
   semantics, not an empirical guess. *Opposite:* would mean numpy float comparison does not do
   what the standard says, and I would look for my own error first.
4. **The class reaches outside the height family**: at least one non-height arsenal function
   accepts a non-finite input and returns a non-finite number. Confidence **moderate**; **D2**.
   *Opposite:* the class is confined to the height family, which makes the fix complete rather
   than a first instalment — a better outcome and one I do not expect.
5. **After the fix, the three Tier-2 invariants — multiplicativity `M(fg)=M(f)M(g)`, the height
   chain `house <= M <= L`, and Kronecker `M=1 <=> cyclotomic` — hold with zero failures on the
   finite fixture set, and the batch path's NaN-for-degenerate-row contract stays
   distinguishable from the new scalar refusal.** Confidence **moderate**; **D1**. *Opposite:*
   an invariant failure after the fix means the refusal changed the mathematics on finite input,
   which would be a regression and would revert the fix.
6. **At least one Claim authored this cycle is HELD by `techne/lib/claim_record.py`'s own
   binding checks on first authoring.** Confidence **moderate**; **D2**. This is the held_rate
   prediction and I am recording it in advance so a block cannot be quietly re-classified as a
   pass. *Opposite:* zero blocks over ~6 claims in the first cycle of enforced records would be
   suspiciously clean and I would suspect the checks are not running.

### The decision this cycle has to make, stated before the data

Refuse-vs-propagate for non-finite input. I am NOT pre-committing the answer, because it is a
semantic choice and the measurement is supposed to inform it. I AM pre-committing the criterion:

> The posture that wins is the one under which a caller CANNOT confuse "no height exists for
> this input" with "the height is small". If NaN is silently orderable against the Lehmer bound,
> propagation fails that criterion regardless of how convenient it is.

And the constraint: whatever is chosen must keep the scalar/batch contract coherent.
`mahler_measure_padded` already uses NaN as an **in-band signal for a degenerate row**. If the
scalar path also emits NaN for bad input, the batch output has one symbol meaning two different
things, and no caller can tell them apart.

*— pre-registration ends here. Everything below was written after measuring.*
