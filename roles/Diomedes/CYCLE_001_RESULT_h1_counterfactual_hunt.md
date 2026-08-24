# Diomedes cycle 001 — RESULT: the h1 counterfactual-hunt test

**Filed:** 2026-08-24. **Pre-registration:** `CYCLE_001_PREREG_h1_counterfactual_hunt.md`, frozen and
committed as `ce892804` **before** any outcome existed.
**Rows:** `cycle001_run.py` → `cycle001_result.json`; `cycle001_conditional.py` →
`cycle001_conditional.json`; `cycle001_preflight.py` → `cycle001_preflight.json`.
**Verdict:** **REDESIGN-COORDINATES.**

---

## 1. The answer to the question that was asked

> **Does what Prometheus already recorded tell us which move to make?**

**No.** It tells us which objects are *generally* good counterexamples — and it does that only about
half as well as a plain base rate could. About which move to make **from here**, it carries nothing
measurable at all.

## 2. The decomposition that decides it

The total available signal runs from chance (AUC 0.500) to perfect (1.000). Splitting it by whether
knowing the current state is required [M, n = 37,985 states]:

- **ORACLE, state-specific — 1.0000.** Positive control; by construction.
- **ORACLE_MARGINAL, the best possible ranking that ignores the state — 0.6254** (SE 0.0013).
  This is the ceiling for anything that scores an object without looking at where you are.
- **Prometheus's recorded coordinates (B1, object break-rate) — 0.5560** (SE 0.0008).

So:

- **state-independent signal available:** 0.6254 − 0.500 = **0.1254**
- **conditional signal — requires attending to the state:** 1.000 − 0.6254 = **0.3746**, i.e.
  **75% of all available signal is conditional**
- **Prometheus captures 44.7% of the marginal portion and 0% of the conditional portion.**

That is the `I(Z;F)` ≫ `I(Z;A*)` outcome the assignment named, measured rather than argued.

## 3. Full arm table, 5 seeds, held-out invariant pair (T3-grade split)

Mean per-state AUC across seeds; chance = 0.500 exactly.

- **ORACLE — 1.0000** ✓ positive control passes; the harness can see signal when it is there
- **Z_full — 0.5633** (range 0.5514–0.5804)
- **B1 candidate break-rate — 0.5626** (range 0.5488–0.5858)
- n_rels — 0.5054
- **Z_parent — 0.5000** (exactly)
- RANDOM — 0.4995
- **SHUFFLE cheat control — 0.4993** ✓ no leakage
- n_cells — 0.4949
- B2 frequency — 0.4943
- B3 catalog adjacency — 0.4797 (*below* chance)

**Z_full − B1 = 0.0007 across seeds**, with per-seed SEs of ~0.0014 and B1 beating Z_full on at
least one seed. The five-feature logistic regression is indistinguishable from its single best
input. The elaborate representation added nothing.

## 4. Three findings sharper than the headline

**4.1 — Every above-chance arm is a pure object property; the only state-dependent feature is
below chance.** `B1_break_rate`, `B2_freq`, `n_cells`, `n_rels` are all marginal statistics of the
candidate object, computable without reference to `x`. The single feature that does depend on the
current state — `B3_adjacency` — scores **0.4797**, i.e. worse than random. Nothing in the recorded
coordinates that varies with position carries signal.

**4.2 — `Z_parent` is structurally incapable of ranking, and that is a coordinate-adequacy finding,
not a null.** The parent-state representation — kill_pattern, claim_kind, verdict,
convergence_status, method, invariant pair, relation — assigns *the same value to every candidate*.
It has no candidate-indexed axis at all, so its AUC is exactly 0.5000 by construction. This is K0
again, one level in: the coordinate has no component along the dimension the question varies on.
A null result would have meant we looked and found nothing; this means the representation could not
express the distinction.

**4.3 — The navigable structure demonstrably exists.** The oracle finds it perfectly, and it is
**75% of the total signal**. This is the separation James insisted on, and the numbers land on the
right side of it: **H2 (search transitions carry navigational information) is supported here; H3
(Prometheus's recorded coordinates preserve it) is falsified here.** A KILL on H2 was never
available from this cycle and is further from available now than before it ran.

## 5. Verdict against the pre-registered rule

- **KILL-EXISTING-EDGE-MINING** — requires `Z` null **and** trivial features unhelpful. `Z` is not
  null (0.556, ~70 SE above chance) and trivial features are *more* helpful than `Z`. **Does not
  fire.**
- **REDESIGN-COORDINATES** — requires ground-truth/trivial features to expose navigability that `Z`
  misses. ORACLE_MARGINAL (0.6254) exposes navigability `Z` (0.5560) misses, capturing only 44.7% of
  it, and the conditional 0.3746 is missed entirely. **FIRES.**
- **ADVANCE** — requires `Z` to beat every baseline. It ties B1 and loses to ORACLE_MARGINAL.
  **Does not fire.**
- **KILL-NAVIGATION-GEOMETRY-HYPOTHESIS** — not available as an outcome of this cycle at any result,
  per prereg §2. Unchanged.

**Verdict: REDESIGN-COORDINATES.** This challenges the schema, not the thesis.

## 6. The prediction I recorded, and how it did

Prereg §8, written before measurement: *"B1 wins or ties Z_full; Z_parent is at chance; overall AUC
lands in 0.55–0.65 — above chance, below usefulness — which would read REDESIGN-COORDINATES."*

All four clauses hold: B1 ties Z_full (Δ 0.0007); Z_parent is at chance (exactly 0.5000); AUC 0.5633
is inside 0.55–0.65; verdict is REDESIGN-COORDINATES. Recorded as a calibration data point, not as a
result — a correct prediction about a null-ish outcome is the cheap direction to be right in.

## 7. Deviations from the pre-registration, declared

1. **Transfer ladder order.** Prereg §7 said T0/T1 before T2/T3. I ran the **strictest** split
   directly — held-out invariant pair, which is T3-grade. This is conservative (easier splits can
   only score ≥), but it is a deviation and T0/T1 are not separately reported.
2. **`Z_parent` was not an informative arm.** Prereg §6 listed it as a ranking arm without noticing
   it is constant within a state. Reported as §4.2 rather than quietly dropped.
3. **Scope.** 12 stratified corpus files, ≤150,000 lines each; relations restricted to
   `equal_mod_2` and `abs_diff_le_3` per the prereg's oracle validation.

## 8. What I am NOT concluding

- Not that mathematical search transitions lack navigational structure — §4.3 measures the opposite.
- Not that h1 is a bad corpus. It is the best one Prometheus has, it passed both controls, and it
  gave a clean answer.
- Not that a richer representation would fail. That is the REDESIGN branch and it is untested.
- Not that this generalizes beyond cross-catalog invariant relations on two relation types.

---

## Coordinate-Adequacy Record — CAR-001

```json
{
  "car_id": "CAR-001",
  "claim_id": "h1 recorded coordinates support next-move selection",
  "quantity_credited": "I(Z; A*) — information about which action improves the state",
  "coordinate_system": "theseus h1 kill_neighborhood payload + per-object corpus history",
  "alphabet": "candidate replacement objects for the varied side",
  "alphabet_entropy_bits": 6.64,
  "attainable_range": {
    "chance_auc": 0.5,
    "state_independent_ceiling": 0.6254,
    "state_specific_ceiling": 1.0,
    "conditional_share_of_signal": 0.75
  },
  "measured": {
    "prometheus_coordinates_auc": 0.5560,
    "se": 0.0008,
    "share_of_marginal_ceiling_captured": 0.4467,
    "share_of_conditional_signal_captured": 0.0
  },
  "measured_over_which_rows": "37,985 h1 states, relations equal_mod_2 and abs_diff_le_3, oracle validated 1.0000 against 135,193 corpus holds labels",
  "controls": {"positive_oracle_auc": 1.0, "cheat_shuffle_auc": 0.4993},
  "verdict": "INADEQUATE",
  "decision_this_changes": "R2-5 residue-representation design: verdict-and-object-history coordinates are shown insufficient for next-move selection; the redesign must carry state-conditional structure. Also supplies the ladder canon's H2 precondition 1 with a measured number.",
  "rows_ref": "cycle001_result.json, cycle001_conditional.json, cycle001_preflight.json"
}
```

*— Diomedes, cycle 001 result, 2026-08-24. Verdict REDESIGN-COORDINATES.*

---

# AMENDMENT — 2026-08-24, HITL review of cycle 001

Three corrections and one reframing, all adopted. The rows and verdict are unchanged; two claims
built on them were overstated.

## A1 — The H2 claim is narrowed one notch (correction)

§4.3 said *"H2 (search transitions carry navigational information) is supported here."* Too broad.
What was demonstrated is:

> **This particular counterexample-search landscape contains substantial state-conditional action
> information.** That is H2 **on this population**, not a claim about mathematical solution search
> in general.

Counterexample hunting over simple catalog relations may be unusually well behaved — predicates
like parity and bounded absolute difference have obvious relational structure, and one should
*expect* them to. **Cycle 001 is an instrument proof:** it establishes that the vertex/edge
distinction is real, measurable, and large in at least one genuine Prometheus search process. That
is sufficient for a first cycle and it is not to be inflated. Every downstream citation of this
result must carry the population qualifier.

## A2 — `ORACLE_MARGINAL` is renamed the **state-independent information ceiling** (clarification)

It is computed from evaluation-set ground truth, which makes it unrealistically strong. That is
deliberate and desirable: it asks *if a perfect state-independent prior were handed to you, how far
could you get without ever looking at `x`?* Answer: **0.6254**. Everything from there to 1.000
necessarily requires interaction between state and candidate.

It is therefore **not a deployable baseline** and must never be cited as one. It is a diagnostic
ceiling. The name `ORACLE_MARGINAL` in `cycle001_conditional.json` stays for row-traceability; the
prose term is "state-independent information ceiling."

## A3 — `divides` becomes a robustness population, not a discard (scope change)

Excluding `divides` (oracle agreement 0.9915) was correct for the primary result: when the
measurement is resolving hundredths of AUC, silently tolerating ~0.85% ground-truth disagreement is
inadmissible, and 564 disagreements in 66,023 observations are of unknown origin (corpus error,
oracle error, differing semantics, normalization, edge cases).

It is not, however, a reason to discard the population forever. The frozen analysis is to be re-run
on `divides` **separately and explicitly labelled "results under a 99.15%-agreement oracle"**, never
merged into the clean primary population. Qualitative ordering surviving is reassuring; changing is
a finding to investigate. Scheduled as a cycle 002 deliverable.

## A4 — The quantity is reformulated as explicitly conditional (reframing)

`I(Z; A*)` is the wrong way to write what cycle 001 measured. The demonstrated fact is that the
same candidate is useful from one state and useless from another, so the object of interest is

> **`I(A*; Z_a | Z_x)`** — how much candidate/action information becomes useful *conditioned on the
> current state*.

This is not "more dimensions." It is relational information, and §4.2's finding is its type-level
statement: a representation of the form `f(Z(x))` assigns an identical score to every `a_i` and
therefore **cannot express `a_3 > a_7`**. That is a type error, not a modelling failure. The minimum
object capable of answering the question is `Z(x, a)`, or `Z(x, a, x')`.

*— Amendment filed 2026-08-24 following HITL review. Verdict REDESIGN-COORDINATES stands.*
