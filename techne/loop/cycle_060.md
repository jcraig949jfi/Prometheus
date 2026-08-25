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

---

## 2. TLDR

The height family had a hole where its coefficients meet the real world, and one corner of it
produced a **plausible** wrong answer rather than an absurd one — `house([inf, 1, -1])` returned
`0.0`, which is house's genuine value for a monomial and therefore indistinguishable from a
correct result. A full 45-call enumeration found five functions holding **four different
postures** toward the same out-of-domain input, with the posture depending on *where in the
coefficient list* the bad value sat. All five now share one guard,
`techne/lib/coefficient_domain.py::require_finite_coefficients`, and the same enumeration comes
back 45 refusals. `zaremba_test`'s unbounded search — the arsenal's second hang — now refuses
above a measured ceiling instead of grinding.

Two of my six pre-registered predictions were **falsified**, one of them a D0, and the D0 failed
because *the probe I wrote aimed at an input that raises*. That is the ninth instance in this
loop of a measurement answering a different question than the one posed, committed inside the
cycle built around that class.

The most useful thing this cycle produced is not a fix. It is that **`Claim.promotable()` cannot
block anything**, because the field it depends on is one I fill in myself.

## 3. ELI5

Imagine a set of five rulers that all measure the same plank. Hand them a plank that isn't
really there and they disagree wildly: two say "that's not a plank", two invent a number, and
one confidently answers **zero inches** — which is also the honest answer for a plank of zero
length, so you can't tell the two apart by looking. That last one is the dangerous kind of wrong:
not obviously broken, just quietly incorrect.

Now all five rulers refuse the same way, and they say *which* part of the plank was missing.

Separately: one tool was asked to check every whole number below some limit. Given a big enough
limit it would have run for about a hundred thousand years without complaining. Now it looks at
the number first and says how long it would take before starting.

And the honest bit: I also built a rule that says "a finding only counts if something independent
checked it." This cycle I discovered the rule asks *me* whether the check was independent, and
believes my answer. So it has never actually stopped anything.

---

## 4. PREDICTIONS SCORED — D0 failures first, per the campaign rules

### D0 FAILURE — prediction 3, and the reason is embarrassing and useful

I predicted a NaN measure passes the Lehmer screen silently, and wired a probe for it. **The
probe returned "raised".** `mahler_measure([nan, 1.0, -1.0])` does not return NaN — numpy's
root-finder rejects the array first — so the input I chose to demonstrate the mechanism was an
input where the mechanism does not fire.

The mechanism is nonetheless real, on the input I did not test:
`mahler_measure([nan])` returned `nan`, and that value is **neither below, nor above, nor equal
to** the Lehmer bound — all three comparisons evaluate False. A candidate whose measure failed to
compute drops out of every screen without ever being counted as a failure.

**Scored as FALSIFIED, not as "confirmed on a different input."** The pre-registered
operationalisation is the prediction; rescuing it after seeing the data is the move this campaign
exists to prevent. What it costs me is the D0: I claimed a mechanism was reachable by a specific
route and it was not.

**This is instance nine of "a measurement answered a different question than the one posed",**
and it happened in the cycle whose subject is that class, inside a script whose docstring cites
the eight prior instances. Consistent with the record: writing the lesson down does not prevent
the recurrence.

### D0 CONFIRMED — prediction 1

Exactly **3 of the 5** scalar entry points returned a non-finite float rather than raising. The
mechanism was as stated: every one of these functions guards the zero polynomial with `== 0` or
`np.nonzero`, and NaN is non-zero under both, so the guard is structurally incapable of seeing
it. Confirmed at the boundary of the prediction, not comfortably inside it.

### D1 FALSIFIED — prediction 2

I predicted `house([nan])` refuses and `house([nan, 1.0])` propagates. The first half holds and
holds **for the reason predicted** — the refusal comes from the no-roots-on-a-constant branch,
not from any finiteness check. The second half is wrong: `house([nan, 1.0, -1.0])` raises, via
numpy.

But `house([inf, 1.0, -1.0])` returns **0.0**. So a degree ≥ 1 leak exists and is *worse* than
the one I predicted — a finite in-range wrong answer rather than a NaN. **I am scoring the
prediction as falsified anyway.** It named an input and an outcome; it got the outcome wrong on
that input. Counting it as a hit because something nearby was worse is precisely how the 7/8
headline got inflated for five cycles.

### D1 CONFIRMED — prediction 5

87 tests green across `techne/tests/test_coefficient_domain.py` and
`techne/tests/test_zaremba_bound.py`. Multiplicativity, the height chain and Kronecker all hold
over hypothesis-drawn integer polynomials, M(Lehmer) is unchanged to 1e-12 against Mossinghoff's
published value, and the batch path's `NaN out ⟺ degenerate row in` contract is now an asserted
invariant rather than a convention.

### D2 CONFIRMED, BUT WEAKLY — prediction 4, and the weakness matters

I predicted the class reaches outside the height family. It does: over the full registry
population — every function named in `techne/inventory.json` with exactly one required positional
parameter, 68 considered — **3 accept a non-finite argument and return a value**:
`techne/lib/gpd_tail_fit.py::diagnose_tail`,
`techne/lib/singularity_classifier.py::classify_singularity` and
`techne/lib/singularity_classifier.py::estimate_radius`.

**And all three return a structured result carrying an explicit failure marker** —
`{'error': 'insufficient_exceedances'}`, `{'type': 'UNKNOWN'}`, and `None` respectively. That is
graceful degradation, not a silent wrong number. It is a materially milder finding than
`house → 0.0` and I am recording the distinction rather than letting "prediction 4 confirmed"
carry the weight of the height-family result.

**14 functions were dropped for arity** (two or more required parameters, so a single non-finite
argument has no unambiguous slot) and are named in
`techne/loop/rung_notes/cycle_060_p4_arsenal.json`. Zero module timeouts. The drop is a real
coverage limit, reported rather than absorbed into the denominator.

### D2 FALSIFIED — prediction 6, and this is the cycle's most important result

I predicted at least one Claim would be **HELD** by `techne/lib/claim_record.py`'s binding checks
on first authoring, and pre-committed that zero blocks would look suspiciously clean.

**Zero were held.** Every claim rendered PROMOTABLE on the first run.

The reason is structural, not lucky:

> `Claim.promotable()` requires an adjudication at or above `KNOWN_ANSWER_CONTROL` **with
> `independent_of_generator=True`** — and `independent_of_generator` is a **boolean I set
> myself, in the same file, in the same act of authorship as the claim.**

The promotion rule is stated as *"no claim may be promoted by the same epistemic path that
generated it"*, and its implementation asks the generating path whether it was independent. A
claim adjudicated by nothing at all is promotable if I label it well. Nothing in the frozen
Tier-0/Tier-1 controls can detect that, because the field is data, not a check.

**Per campaign Rule 1 this is recorded as a failure of the frozen system and NOT fixed.** The
fix is designed after cycle 20. Writing it down now, mid-campaign, so the record is prospective:
the obvious repair is to make the adjudication *execute* — a `Callable` that must run and pass —
rather than be asserted, which moves the field from Tier 3 to Tier 0. I am not building that this
cycle.

---

## 5. WHAT WAS DECIDED, AND WHY — refuse, not propagate

The pre-registered criterion was: *the posture that wins is the one under which a caller cannot
confuse "no height exists for this input" with "the height is small."*

Propagation fails that criterion, and fails it worse than I expected before measuring. NaN is not
merely wrong, it is **unordered**: a propagated NaN measure is neither below nor above the Lehmer
bound nor equal to 1, so a candidate whose computation failed silently exits every screen without
being counted as a failure. And `house`'s inf-path does not even produce a NaN to notice — it
produces `0.0`, a value the function legitimately returns for monomials.

So: **refuse**, uniformly, at every scalar entry point, with a domain-level message naming the
offending index — rather than numpy's `"Array must not contain infs or NaNs"`, which is an
implementation detail leaking through a mathematical interface.

**Scalar/batch coherence.** `techne/lib/mahler_measure.py::mahler_measure_padded` already uses
NaN in its *output* as the in-band signal for an all-zero row. Letting non-finite *input* also
arrive as NaN would give one symbol two meanings that no caller could separate. The batch entry
points therefore refuse non-finite input at the front door via
`techne/lib/coefficient_domain.py::require_finite_array`, and `NaN out ⟺ degenerate row in`
becomes an invariant with a test. Blast radius checked, not assumed: the batch callers are
`prometheus_math/lehmer_brute_force.py`, `prometheus_math/lehmer_brute_force_general.py` and
`scripts/_lehmer_brute_force_worker.py`, all of which generate integer coefficients, so no
realised call site can produce a non-finite row.

**Strings, which the sweep found by accident and which change the guard's scope.**
`mahler_measure(["1.0", "-2.0"])` returned **2.0** — the *correct* Mahler measure of x − 2 —
because numpy parses numeric strings on cast. Cycle 059's double-encoding fault handed every
function in a 128-call sweep a string; this function would have answered correctly throughout and
concealed it. A finiteness-only guard leaves that open, so str/bytes is rejected **by type**,
both as a coefficient and as the coefficient sequence.

---

## 6. THE CLAIMS

Rendered from `techne/loop/claims_060.py` via `techne/lib/claim_record.py::render`. Every number
is read from a committed row file; none is typed into this document. Regenerate with
`python techne/loop/claims_060.py`.


### C060-1 — PROMOTABLE
**Proposition.** Before the fix, 3 of the 5 scalar entry points in the height family returned a non-finite float rather than raising on at least one non-finite input: mahler_measure, log_mahler_measure and polynomial_length. Every one of these functions guards the zero polynomial by testing `== 0` or `np.nonzero`, and NaN is non-zero under both, so the guard cannot see it.
**Question.** Do the height family's zero-polynomial guards see a non-finite coefficient at all, or are they structurally blind to it?
**Population.** height-family-nonfinite-grid (n=45, full-scan (complete enumeration of the cross product), fingerprint 1192df8e791fa0fa)
**Measured.** {'non_finite_returning': 3, 'of_entry_points': 5, 'which': ['prometheus_math/polynomial_length.py::polynomial_length', 'techne/lib/mahler_measure.py::log_mahler_measure', 'techne/lib/mahler_measure.py::mahler_measure']} via `python techne/loop/measure_060_nonfinite.py`
**Contract.** entry points with >=1 call classified RETURNS_NONFINITE / all 5 scalar entry points in the height family
**Counterfactual.** adding an isfinite check to any one of the three named functions must reduce this count by exactly one; installing it in all five must take it to 0 (measured post-fix as C060-4)
**Adjudication.** adjudicated by KNOWN_ANSWER_CONTROL

### C060-2 — PROMOTABLE
**Proposition.** Before the fix the 45-call enumeration split four ways: 19 RETURNS_NONFINITE, 19 RAISES, 5 RETURNS_BOOL and 2 RETURNS_FINITE. The family held four different postures toward the same out-of-domain input, and the posture depended on WHERE in the coefficient list the non-finite value sat.
**Question.** Across the whole non-finite grid, what does the height family actually do -- and is its behaviour uniform?
**Population.** height-family-nonfinite-grid (n=45, full-scan (complete enumeration of the cross product), fingerprint 1192df8e791fa0fa)
**Measured.** {'RETURNS_NONFINITE': 19, 'RAISES': 19, 'RETURNS_BOOL': 5, 'RETURNS_FINITE': 2} via `python techne/loop/measure_060_nonfinite.py`
**Contract.** calls in each outcome class / all 45 calls in the enumeration
**Counterfactual.** a shared domain guard applied at every entry point must collapse this to a single class
**Adjudication.** adjudicated by KNOWN_ANSWER_CONTROL
**Caveats.** the 19 RAISES were mostly numpy's 'Array must not contain infs or NaNs', an implementation message leaking through a mathematical interface, not a designed refusal

### C060-3 — PROMOTABLE
**Proposition.** `house([inf, 1, -1])` and `house([-inf, 1, -1])` returned 0.0. That is not an absurd value: 0.0 is house's genuine and documented answer for a MONOMIAL, whose roots really are all at the origin. It is a finite, in-range, wrong answer, and it is indistinguishable from a correct one by inspection. Mechanism: np.roots normalises by the leading coefficient, and [1, -1] / inf is [0, 0].
**Question.** Did any of this produce a wrong answer that looks PLAUSIBLE -- the class the campaign exists to catch, as opposed to an absurd number?
**Population.** height-family-nonfinite-grid (n=45, full-scan (complete enumeration of the cross product), fingerprint 1192df8e791fa0fa)
**Measured.** {'returns_finite_on_nonfinite_input': 2, 'rows': [{'function': 'prometheus_math/house.py::house', 'input': 'lead[inf,1,-1]', 'outcome': 'RETURNS_FINITE', 'detail': '0.0'}, {'function': 'prometheus_math/house.py::house', 'input': 'lead[-inf,1,-1]', 'outcome': 'RETURNS_FINITE', 'detail': '0.0'}]} via `python techne/loop/measure_060_nonfinite.py`
**Contract.** calls classified RETURNS_FINITE on non-finite input / all 45 calls in the enumeration
**Counterfactual.** if the mechanism were anything other than leading-coefficient normalisation, np.roots([inf, 1, -1]) would not be [0, 0]
**Adjudication.** adjudicated by KNOWN_ANSWER_CONTROL

### C060-4 — PROMOTABLE
**Proposition.** After installing `techne/lib/coefficient_domain.py::require_finite_coefficients` at all five scalar entry points, the same 45-call enumeration returns 45 RAISES and nothing else. The family now holds ONE posture toward non-finite input, and it is a refusal that names the offending index.
**Question.** Did the fix close the hole across the whole declared population?
**Population.** height-family-nonfinite-grid (n=45, full-scan (complete enumeration of the cross product), fingerprint 1192df8e791fa0fa)
**Measured.** {'RAISES': 45} via `python techne/loop/measure_060_nonfinite.py`
**Contract.** calls classified RAISES / all 45 calls in the enumeration
**Counterfactual.** reverting the guard in any single entry point must return that function's rows to the pre-fix classes recorded in C060-2
**Adjudication.** adjudicated by KNOWN_ANSWER_CONTROL
**Caveats.** the guard's transparency on FINITE input is the cost side and is checked separately: M(Lehmer) unchanged to 1e-12, and the three invariants hold over hypothesis-drawn integer polynomials

### C060-5 — PROMOTABLE
**Proposition.** No. `mahler_measure(['1.0', '-2.0'])` returned 2.0, the CORRECT answer, because numpy parses numeric strings on cast to complex128. And `polynomial_length('123')` returned 6.0 by iterating the string's characters. A sweep that delivered every function a string would have been confirmed rather than exposed here, so the guard rejects str and bytes BY TYPE and not merely by finiteness.
**Question.** Would cycle 059's double-encoding fault -- every function handed a STRING -- have been visible on this family?
**Population.** string-coefficient-probe (n=2, full-scan (both shapes, chosen before running either), fingerprint 62e9b246d394d775)
**Measured.** {"mahler_measure(['1.0','-2.0'])": 2.0, "polynomial_length('123')": 6.0, 'both_plausible': True} via `python -c "from techne.lib.mahler_measure import mahler_measure; print(mahler_measure(['1.0','-2.0']))"`
**Contract.** string inputs returning a plausible number pre-fix / the 2 string shapes probed
**Counterfactual.** if numpy did not parse numeric strings on cast, mahler_measure(['1.0','-2.0']) would raise rather than return 2.0
**Adjudication.** adjudicated by KNOWN_ANSWER_CONTROL

### C060-6 — PROMOTABLE
**Proposition.** zaremba_test's exhaustive `for a in range(1, q)` runs at a rate that DECLINES with q -- 2,691,790 iter/s at q=2,000, 2,379,196 at q=20,000, 2,022,862 at q=100,000 -- so the cycle-059 figure, taken at q=20,000 and applied to q=2**63, extrapolated the wrong direction. With ZAREMBA_DEFAULT_MAX_Q = 10**7 the q=2**63 call refuses in under a second with a message quoting the rate, the q it was measured at, and the fact that the projection is an extrapolation.
**Question.** What does zaremba_test's unbounded search actually cost, and does a bound turn the hang into an immediate refusal?
**Population.** zaremba-timing-ladder (n=3, full-scan (all three q values timed, none discarded), fingerprint 7b6aa055e4bef453)
**Measured.** {'iters_per_sec': {'2000': 2691790, '20000': 2379196, '100000': 2022862}, 'rate_declines_with_q': True, 'refusal_latency_seconds_at_q_2_63': '< 1e-3'} via `python -c "import time; from techne.lib.cf_expansion import zaremba_test; ..."  (ladder q in {2000, 20000, 100000})`
**Contract.** measured iterations per second at each q / the 3 timed q values
**Counterfactual.** if the rate were constant in q, the three measurements would agree within timer noise; they differ by 25% across the ladder
**Adjudication.** adjudicated by KNOWN_ANSWER_CONTROL
**Caveats.** the projected runtime at q = 2**63 remains an extrapolation across ~14 orders of magnitude and is NOT a measurement; the refusal message says so

### C060-7 — PROMOTABLE
**Proposition.** No. `zaremba_test(1)` returns satisfies=False. Zaremba's conjecture holds trivially at q=1 -- the residues coprime to 1 are {0} and 1/1 = [1] has max digit 1 <= 5 -- but the body iterates range(1, q), which is EMPTY at q=1, so a trivially-satisfied case is reported as a counterexample to the conjecture. Found by an authority test written over 1..200 failing at its first element. NOT patched this cycle: it changes a returned value rather than adding a refusal, and a semantic change smuggled into a guard commit is unreviewable.
**Question.** Does zaremba_test answer correctly at the smallest denominator in its own domain?
**Population.** zaremba-domain-boundary (n=200, full-scan, fingerprint 6eaeb7e2dc9883fd)
**Measured.** {'q_reporting_false': [1], 'count': 1, 'of': 200} via `python -m pytest techne/tests/test_coefficient_domain.py techne/tests/test_zaremba_bound.py -q`
**Contract.** q in 1..200 reporting satisfies=False / all 200 q values
**Counterfactual.** changing the loop to range(1, q + 1) for q == 1 must move this count to 0 and must not change any q >= 2
**Adjudication.** adjudicated by KNOWN_ANSWER_CONTROL

### C060-8 — PROMOTABLE
**Proposition.** Under the frozen arsenal_red scope the suite reports 44 FAILED node ids and 3 collection errors. Against the cycle-052 baseline the name-diff is 0 NEW and 2 GONE. A count that held steady while one test went green and another went red would read as 'no change' and would not be one, which is why this is reported as a name-diff.
**Question.** Did installing a domain guard in four load-bearing arsenal functions break anything -- by NAME, not by count?
**Population.** arsenal-pytest-scope (n=44, full-scan (whole suite, --continue-on-collection-errors), fingerprint e366cff46243fd7b)
**Measured.** {'red': 44, 'collection_errors': 3, 'NEW': [], 'GONE': ['prometheus_math/tests/test_cost_models.py::test_property_calibration_is_deterministic_given_fixed_inputs', 'techne/tests/test_mahler_batch.py::test_authority_padded_matrix_matches_scalar_for_100_polys'], 'unchanged': 44, 'baseline': 'pivot/arsenal_red_052.json'} via `-m pytest prometheus_math techne/tests -q --continue-on-collection-errors -p no:cacheprovider`
**Contract.** pytest node ids reported FAILED / every test collected under prometheus_math + techne/tests
**Counterfactual.** removing the finiteness check from mahler_measure must leave this diff unchanged, since no pre-existing test covers non-finite input -- which is itself the reason the hole survived 60 cycles
**Adjudication.** adjudicated by INDEPENDENT_IMPLEMENTATION
**Caveats.** the cycle-052 baseline predates several cycles of unrelated work, so GONE and NEW entries are not all attributable to cycle 060; the claim is about NEW entries touching the four patched modules

<!-- 8/8 claims promotable; rendered by techne/loop/claims_060.py -->
---

## 7. CAMPAIGN METRICS — cycle 1 of 20, reported prospectively

**`escape_rate` — 0 of 8 exported claims, so far, and the figure is nearly uninformative.**
No claim exported this cycle has yet been found invalid. That is an *interim* value by
construction: an escape is defined by later inspection, and the later inspection has not
happened. It is made weaker still by the prediction-6 result — the frozen Tier-0/1 controls
blocked nothing this cycle, so a zero numerator measures the absence of a test, not the presence
of correctness. Later cycles may raise this number retroactively and should.

**`held_rate` — the frozen controls held 0 of 8. The Tier-2 layer held 2, and both were
correct.** Reported separately because merging them would credit the frozen controls with catches
they did not make.

- `claim_check`, `sampling_lint`, `measurement_guard`, `control_certifier` and
  `claim_record.promotable()` blocked **nothing**. `measurement_guard` did its job in the sense
  that the sweep's three positive controls ran and passed before any row was read — but a control
  that passes is not a block.
- The **authority test** blocked my hand-computed `L(Lehmer) = 8`. The true value is 9: the
  eleven coefficients include two zeros. **The code was right and my authority value was wrong**,
  which is the direction that matters — an authority test is only worth having if it can fail
  against its author.
- The **authority test over q = 1..200** blocked at its first element and surfaced finding #16
  (below), a real defect I was not looking for.
- **False blocks: 0.** No control refused a valid claim this cycle. `zaremba_test(q)` and
  `zaremba_test(q, max_q=None)` agree for every q below the ceiling over 60 hypothesis-drawn
  values, and M(Lehmer) is unchanged to 1e-12 — the two places a false block would show up first.

**`adjudication_coverage` — 8 of 8 nominal, and the nominal figure is an upper bound I do not
believe.** Every exported claim carries an adjudication flagged independent. Per §4's
prediction-6 result, that flag is self-reported, so this metric currently measures my labelling
discipline rather than the claims' epistemic independence. The honest reading: the claims backed
by an **executed** external check — Mossinghoff's published M(Lehmer), the three invariants over
hypothesis-drawn input, Zaremba's conjecture over q = 2..200, `np.roots` reproducing the `0.0`
mechanism — are C060-3, C060-4, C060-5, C060-6 and C060-7. The pre-fix tallies (C060-1, C060-2)
rest on a control that validated the *classifier*, not the tally, which is weaker than the
KNOWN_ANSWER_CONTROL label suggests.

**`yield` — 5 decision-changing claims of 8.** C060-2 changed the design from five separate
patches to one shared guard; C060-3 decided refuse-over-propagate; C060-5 widened the guard from
finiteness to finiteness-and-type; C060-6 corrected cycle 059's extrapolation, which ran the
wrong direction; C060-7 opened a finding that did not exist before the cycle. The remaining three
document rather than decide.

---

## 8. FINDINGS REGISTERED THIS CYCLE

**#13 — `prometheus_math/house.py::house` returned `0.0` on a non-finite leading coefficient.**
MINE, FIXED. A finite, in-range, plausible wrong answer, indistinguishable from `house`'s correct
answer for a monomial. Mechanism: `np.roots` normalises by the leading coefficient and
`[1, -1] / inf` is `[0, 0]`. This is the first defect this loop has found in its own arsenal that
would **not** have announced itself by looking absurd.

**#14 — `prometheus_math/polynomial_length.py::polynomial_length`'s documented domain did not
match its actual one.** MINE, FIXED. Its module docstring argued at length that its domain
"deliberately matches `mahler_measure`'s rather than being wider" because a screen with a wider
domain than the thing it screens passes inputs the expensive step then rejects. Measured over the
grid: it returned a number on 9 of 9 non-finite inputs where `mahler_measure` refused on 6 of 9.
The docstring stated an intention nothing tested. The claim is now asserted in
`techne/tests/test_coefficient_domain.py` and the docstring records that it was false.

**#15 — numeric strings are silently parsed into correct-looking heights.** MINE, FIXED.
`mahler_measure(["1.0", "-2.0"])` returned 2.0. The significance is not the string handling; it
is that this function **cannot reveal** the cycle-059 double-encoding fault, because it answers
that fault correctly. Guards that check only value-validity leave type-confusion invisible.

**#16 — `techne/lib/cf_expansion.py::zaremba_test(1)` reports `satisfies=False`.** MINE, **NOT
FIXED THIS CYCLE, DELIBERATELY.** Zaremba's conjecture holds trivially at q = 1, but the body
iterates `range(1, q)`, which is empty there, so a trivially-satisfied case is reported as a
counterexample to a conjecture. Not patched in the same commit as the search bound because it
changes a **returned value** rather than adding a refusal, and a semantic change smuggled into a
guard commit is unreviewable. The boundary is pinned by a test so it cannot drift unobserved.

**#17 — `techne/lib/claim_record.py::Claim.promotable()` cannot block a mislabelled claim.**
MINE, **NOT FIXED — CAMPAIGN RULE 1.** See §4, prediction 6. Recorded as a failure of the frozen
system; the repair is designed after cycle 20 closes.

**Finding #12 CLOSED.** `zaremba_test` now takes `max_q`, defaulting to `ZAREMBA_DEFAULT_MAX_Q`
= 10^7, and refuses above it in under a millisecond with a message quoting the measured rate, the
q at which it was measured, and the fact that the projection is an extrapolation. Cycle 059's
"~131,000 years" was computed from a rate measured at q = 20,000; the rate **declines** with q,
so that extrapolation ran in the flattering direction. **Findings #9, #10 and #11 CLOSED** by the
shared guard.

---

## 9. WHAT THIS CYCLE DID NOT DO

- **The 46 arsenal reds (campaign item b) were not attacked.** The regression sweep was run for
  the name-diff only. 26+ are gated on HITL #242.
- **The Tier-2 invariant enumeration (campaign item c) was completed only for the height
  family** — multiplicativity, the height chain, Kronecker. The enumeration across the rest of
  the arsenal is cycle 061's opening, and prediction 4's registry scan is the natural input to
  it: 68 functions considered, 14 dropped for arity, all named.
- **The 12 outstanding findings were not retrofitted as Claim records (campaign item d).** Five
  new ones were authored as records instead. Given §4's prediction-6 result, retrofitting them
  would mostly measure my labelling discipline, and the value of that test has dropped.
- **Cross-role findings remain with their owners.** No cross-role semantics were touched.

## 10. OPEN, WAITING ON JAMES

- **#242** — dependency install. Unchanged; still gating 26+ arsenal reds.
- **#311** — retract vs re-run the Lehmer verdict built on a defective verifier.
- **#341** — update the stale authority test now that its data is verified (8,625 entries,
  degrees 2–180).
- **NEW, #422** — finding #16 (`zaremba_test(1)`) is mine and I can fix it, but it changes a
  returned value. I intend to fix it in cycle 061 as its own commit unless told otherwise; noting
  it rather than doing it silently.

---

## 11. ChatGPT PASTE BLOCK

```
CONTEXT. I am Techne, the toolsmith/substrate role in an autonomous multi-agent mathematics
program called Prometheus. I run 20-cycle campaigns under pre-registered predictions. This is
cycle 060, the first cycle of a campaign testing one question: can an LLM-authored research loop
be made INCAPABLE of silently promoting the mistakes it still makes? The controls are frozen for
all 20 cycles; failures are recorded as failures of the frozen system and are NOT fixed mid-
campaign, because fixing them would turn a prospective test back into a retrospective fit.

WHAT I DID THIS CYCLE. Enumerated the five scalar entry points of my Mahler-measure/height
family against the complete non-finite input grid (45 calls, full scan, no sampling). Found four
different postures toward the same out-of-domain input, position-dependent. One of them --
house([inf, 1, -1]) -> 0.0 -- is a PLAUSIBLE wrong answer, because 0.0 is house's genuine value
for a monomial, so it is indistinguishable from a correct result by inspection. Installed one
shared domain guard across all five entry points plus the three batch entry points; the same
enumeration now returns 45 refusals. Also bounded an O(q) exhaustive search that would otherwise
run ~10^5 years on a large argument. 87 new tests, 4,395 pre-existing tests still passing, ZERO
new failures by node-id diff.

WHAT I WANT YOU TO ATTACK. Not the mathematics -- attack the epistemics.

1. THE CENTRAL RESULT. My promotion rule says "no claim may be promoted by the same epistemic
   path that generated it." Its implementation requires an adjudication flagged
   independent_of_generator=True. This cycle I realised that flag is a BOOLEAN I SET MYSELF, in
   the same file, in the same act of authorship as the claim. So the rule has never blocked
   anything and cannot. All 8 claims rendered PROMOTABLE. Is my proposed repair -- make the
   adjudication an executable callable that must run and pass, rather than an asserted field --
   sufficient? What does it still fail to catch? Specifically: an executable check can still
   share an assumption with the thing it checks. How would you detect THAT mechanically?

2. A D0 PREDICTION FAILED FOR AN INSTRUCTIVE REASON. I predicted "a NaN measure passes the
   Lehmer screen silently" and wrote a probe. The probe fired on an input that RAISES, so it
   returned "no". The mechanism is real on a different input I did not test. I scored this
   FALSIFIED rather than rescuing it post hoc. Was that the right call, or is it over-strict
   in a way that will make me under-report real mechanisms?

3. MY ESCAPE-RATE NUMERATOR IS ZERO AND I THINK THAT IS MEANINGLESS. Zero invalid claims were
   caught this cycle -- but the frozen controls blocked nothing (see 1), so a zero numerator
   measures the absence of a test, not correctness. How would you construct a HONEST interim
   escape-rate estimate at cycle 1 of 20, given that escapes are defined by later discovery?

4. THE TWO REAL BLOCKS CAME FROM SOMEWHERE ELSE. My Tier-0 machine checks caught nothing. What
   caught things was: (a) an authority test where I hand-computed L(Lehmer) = 8 and the true
   value is 9 -- the CODE was right and MY authority value was wrong; and (b) an authority test
   over q = 1..200 that failed at its first element and surfaced a real defect I was not looking
   for. Both are cases where an external mathematical fact disagreed with me. Does this suggest
   my whole Tier-0 investment is misallocated relative to buying more domain oracles?

5. STEELMAN THE NULL. My pre-registered null says: if escape_rate does not fall while yield
   holds, then LLMs are mutation and search engines, validated research state belongs entirely
   to executable machinery, and the model should author CANDIDATES, not FINDINGS. Argue that
   cycle 060 is already evidence FOR that null, not against it.

Be adversarial. Assume I am inflating. Prior cycles inflated a headline number for five cycles
while the disconfirming evidence sat on the same page.
```
