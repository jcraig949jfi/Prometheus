# Diomedes cycle 001 — PRE-REGISTRATION: the h1 counterfactual-hunt test

**Filed:** 2026-08-24, **before any outcome measurement.** **Authorized:** James, this session
("run her bounded h1 experiment, after revising that KILL semantics").
**Attaches to:** R2-5 (residue representation) pending James's A6 ruling; run authorized regardless.
**Scope authorized, and the boundary is hard:** no new navigation architecture, no mass edge
reconstruction, no successor-representation learner, no RL system, no 346 GB campaign.
**Pre-flight rows:** `cycle001_preflight.py` → `cycle001_preflight.json`, committed with this file.

---

## 1. The question

> **Does what Prometheus already recorded tell us which move to make?**

Formally: for a surviving cross-catalog relation `R(inv_a(o_a), inv_b(o_b))` that h1's hunter went
on to attack, and a frozen pool of `k` candidate replacement objects for the varied side, can a
ranker built **only from what Prometheus recorded** place the members of

`A*(x) = { candidate c : R breaks when c replaces the varied object }`

above chance, and above trivial baselines — **without looking up the candidate's invariant value**?

## 2. The revised decision rule (James's ruling, adopted verbatim in substance)

My v1 KILL condition was too strong and committed the exact error this seat documented in Aporia's
H-R1: it would have falsified **H2** (mathematical search transitions carry navigational
information) on evidence about **H3** (these particular recorded coordinates preserve it). Replaced
by a three-way rule:

- **KILL-EXISTING-EDGE-MINING** — `Z` is null **and** trivial features are also unhelpful. h1's
  recorded coordinates are autopsy coordinates *and* this neighbourhood has no exploitable local
  structure to find. The edge-mining line on **this corpus** closes.
- **REDESIGN-COORDINATES** — trivial/ground-truth features expose navigability that `Z` misses.
  Geometry exists; Prometheus cannot see it. Challenges the schema, **not** the thesis. Follow-on is
  the trace-vector rebuild the ladder canon already specifies — not a new architecture.
- **ADVANCE** — `Z` beats chance **and** every §6 baseline, surviving to T2.

And explicitly **out of reach of this cycle**: `KILL-NAVIGATION-GEOMETRY-HYPOTHESIS` is **not
available as an outcome here at any result**. It requires controlled known-solution landscapes to
fail as well. No result of cycle 001 licenses it. This clause exists so that a null on one
representation over one population cannot retire the larger hypothesis — the failure mode this seat
was created to catch.

## 3. Population, and why it is narrower than the recon proposed

**Included:** h1 `kill_neighborhood` records with `hunter_success = true`, a named
`hunter_varied_side`, both parent values present, and `parent_relation` ∈ **{`equal_mod_2`,
`abs_diff_le_3`}**.

**The relation restriction is a two-control result, not a convenience.** I validated my oracle
predicates against the corpus's own `holds` labels before using them [M, pre-flight]:

- `equal_mod_2` — **73,972 / 73,972 = 1.0000**
- `abs_diff_le_3` — **61,221 / 61,221 = 1.0000**
- `divides` — 65,459 / 66,023 = 0.9915 (and the reverse direction `vb|va` = 0.3310, so the
  convention is `va | vb`, but 564 rows still disagree) — **EXCLUDED**
- `equal` — 59,458 / 59,468 = 0.9998, 10 rows disagree — **EXCLUDED**

An oracle that is 99.15% right is not an oracle; it is a second hypothesis. Excluding `divides`
drops ~31% of h1 volume and is the correct trade. Positive control on the oracle itself: it must
reproduce **all** labeled rows for an included relation, or that relation is out.

**Candidate pool.** For the varied side, all catalog objects with a known value for that invariant,
capped at `k = 100` by frozen sample (seed **20260824**). Knot pools hold 52 objects, so knot-side
pools are **exhaustive** (k=52); EC pools hold ~1,000, so k=100 sampled. `k` varies by side and the
primary metric is chosen to be invariant to that.

**Value table.** Harvested from the corpus's own `(catalog, invariant, object) → value` payload
fields — 12 keys, 4,756 object-value pairs [M]. These are properties of the mathematical objects,
so they are oracle-side, and the ranker never sees them.

## 4. Attainable range — computed BEFORE any gate line

Per `feedback_gate_must_be_shown_reachable` and `feedback_gate_must_exceed_measurement_error`.
Over 13,128 usable parent states in the pre-flight, the fraction of candidates that break the
relation [M]:

- mean **0.4712**, median **0.49**, p05 **0.12**, p95 **0.85**, stdev across states **0.2204**
- degenerate-high (≥0.95): **0.87%**; degenerate-low (≤0.05): **1.49%**

**The task is not degenerate** — the pre-committed VACUOUS reading does not fire. Headroom is real
(chance ≈ 0.47, ceiling 1.0), but the per-state base rate varies enormously (0.12→0.85), which
forces the metric choice in §5: raw accuracy would mostly measure the base rate.

## 5. Metrics

**Primary: per-state AUC**, mean over states, because it is invariant to both `k` and the per-state
base rate. Chance = 0.500 exactly, published beside every value.

**Secondary:** precision@10 **minus that state's own base rate** (the lift a budget-10 hunter would
actually experience); `I(Z;A*)` vs `I(Z;F)` on identical rows with random-pairing nulls for both
(`feedback_mi_bias`); action-entropy reduction `H(A*) − H(A*|Z)` in bits.

**SE before the line.** Report SE of mean AUC as `stdev(per-state AUC) / sqrt(n_states)`. **The gate
is `mean_AUC − 3·SE > 0.500`**, so the margin must exceed measurement error by construction rather
than by inspection. ≥5 seeds over the pool draw; report the CI beside the verdict.

## 6. Arms and baselines

Every arm ranks the same k candidates from the same frozen pool. **No arm may read the candidate's
invariant value** — that is the oracle, and an arm that reads it has done the search's work (K7).

- **ORACLE (positive control)** — reads the value. Must score AUC ≈ 1.000. If it does not, the
  harness is broken and no other number is admissible.
- **SHUFFLE (cheat control)** — candidate→label mapping permuted. Every arm must fall to 0.500. If
  anything survives, there is leakage.
- **RANDOM** — the 0.500 floor.
- **B1 — candidate global break-rate.** How often this object broke relations elsewhere in the
  corpus. *Expected to be the real enemy* — it is a pure per-object base rate, one GROUP BY.
- **B2 — candidate corpus frequency.** Popularity only.
- **B3 — catalog adjacency.** Proximity in catalog index (EC conductor order / knot table order).
- **B4 — parent margin.** `|v_a − v_b|` against the relation threshold. A property of `x`, so it
  cannot rank candidates; carried as the baseline for the secondary hunt-difficulty task, which is
  where James's "subtraction is the enemy" prediction actually bites.
- **Z_parent** — parent state as Prometheus recorded it (kill_pattern, claim_kind, verdict,
  convergence_status, method, invariant pair, relation).
- **Z_full** — Z_parent plus the candidate's recorded corpus history (cell membership, kill_pattern
  profile, survival/rejection counts). **This is the arm the thesis is about**: does the accumulated
  failure record *about an object* tell you whether that object is a useful counterexample here?

**Note on James's expectation.** He named subtraction as the enemy. Under the no-lookup rule
subtraction is unavailable for candidate ranking, so **B1 replaces it as the thing most likely to
embarrass us** — and B1 is arguably worse news if it wins, because a per-object base rate is an even
cheaper artifact than a margin computation.

## 7. Transfer ladder

T0 same states → T1 held-out candidate pools for seen parents → T2 held-out parent states within the
same invariant pair → T3 held-out invariant pair. **T0/T1 reported before T2/T3 is computed.** T4
(cross-catalog) is out of scope for cycle 001.

## 8. What I expect (recorded so it can be wrong)

B1 wins or ties Z_full; Z_parent is at chance; overall AUC lands in 0.55–0.65 — above chance,
below usefulness — which would read **REDESIGN-COORDINATES**. Stated now so the result cannot be
narrated afterwards as a confirmation.

## 9. Deliverables

`CYCLE_001_RESULT_*.md`, the Coordinate-Adequacy Record, and the rows — all in one commit with the
runner script (`feedback_verdict_without_rows_is_an_assertion`).

*— Diomedes, cycle 001 pre-registration, 2026-08-24. Frozen before measurement.*
