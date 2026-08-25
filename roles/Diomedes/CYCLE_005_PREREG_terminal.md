# Diomedes cycle 005 — PRE-REGISTRATION (terminal): oracle-form replication + coordinate transport

**Filed:** 2026-08-25, **before any outcome measurement.** **Charter:** `LOOP_CHARTER.md` §20 as
corrected by `AMENDMENT_2026-08-25_arity_and_transport.md`.
**Terminal condition:** this cycle ends the reconnaissance **only if it resolves both** questions in
§1. If either fails, the grand interpretation shrinks and that shrinkage is the result.
**Step 0 complete:** operator semantics recovered exactly, three sources at 1.000000 agreement
(`04bc8490`).

---

## 1. The two questions that make this terminal

- **Q1 — oracle form.** Does the decomposition ordering survive an oracle whose answer is **not
  transparently encoded** in the cheap arithmetic features? Cycles 001–004 used parity and
  bounded-difference predicates over catalog values; arithmetic recovering that ordering is not
  wholly surprising.
- **Q2 — transport.** Does the anti-transfer of cycle 004 survive a serious attempt at
  **mathematically natural coordinate transport**? If a low-complexity `T_ij` restores most of the
  within-cell ordering, "navigation knowledge is local" was premature — it was chart mismatch.

Two arms, one per question. Both must report before a disposition is taken.

## 2. ARM A — b2 operator commutation (Q1). Rungs 1–4, fully enumerable.

**Space:** 6 operators × 6 × 101 values = **3,636 cells, exhaustively enumerated.** No sampling, no
SE, no permutation null. Every number is a count or a ratio of counts.

**Task:** state `x = (v, f)`; action `a = g`; oracle `f(g(v)) == g(f(v))`, computed from the
step-0 tables. Candidate set is all 6 operators, so `k = 6` at every state and the full
101 × 6 = 606 states are enumerated.

**The decomposition, all exact:**
- chance
- **marginal ceiling** — best fixed ranking of `g` ignoring both `v` and `f`
- **f-conditional ceiling** — best fixed ranking of `g` knowing `f` but **not** `v`; this is the
  analogue of cycle 001's state-independent ceiling
- **cheap `Z(x,a)`** — see §2.2
- oracle = 1.0 by construction

The quantity of interest is what knowing `v` adds **beyond knowing `f`**.

### 2.1 Generator-leakage test (mandatory — the mistake most worth finding)

The devastating alternative for the whole thread: the "conditional signal" is **reconstruction of the
benchmark generator**, not navigation signal. Changing the oracle predicate is necessary but may be
insufficient. Three nested feature sets, reported separately:

- **F_pure** — properties of `v` only (parity, `v mod 3`, sign, `|v|`, is-power-of-2, `v`) plus
  one-hot `f` and one-hot `g`. **No operator-table lookup at all.**
- **F_applied** — F_pure plus **one** table application (`g(v)`, `f(v)`). One step onto the oracle's
  path, not both.
- **F_oracle** — both compositions. This *is* the oracle; reported only as the 1.0 anchor.

**Interpretation, fixed now:** if F_pure alone approaches the f-conditional ceiling, the apparent
signal is operator-identity structure, i.e. the marginal, and Q1 is answered negatively. If
F_applied adds materially over F_pure but stays well below F_oracle, that increment is the
conditional navigation signal under a **different oracle form**, which is what Q1 asks.

### 2.2 Rule class — rung 4, exhaustively searched, no fitting

For each `(f, g)` pair, select the best predicate on `v` from a **frozen finite list** by exact
count over the enumerated table: `v` even · `v mod 3 ∈ {0,1,2}` · `v < 0` · `v = 0` · `|v| ≤ t` for
`t ∈ {1,2,4,8,16,32}` · `v` a power of 2 · constant true. All 36 pairs × the list are enumerable, so
the optimum is **found by exhaustive search, not gradient descent**. Integer parameters throughout.

## 3. ARM B — coordinate transport on the h1 population (Q2). Rung 5, sampled.

Runs on **cycle 004's population**, because that is where anti-transfer was measured. Same frozen
18-feature family, same cells, same identity-proved cache.

Three conditions per ordered cell pair `(c_i → c_j)`; **the decisive comparison is 2 vs 3**:

1. **raw transfer** — `f_i` applied to `c_j`. Reproduces cycle 004's B and C cells.
2. **coordinate transport** — `f_i(T_ij(x,a))` for each `T` in the frozen family below.
3. **local relearning** — `f_j` fit on `c_j` from scratch. This is cycle 004's A cell, 0.7101.

**Recovery fraction** = `(condition − raw) / (relearn − raw)`.

### 3.1 The transport family — FROZEN HERE, before seeing any result

Specified in advance precisely so the control is falsifiable. Each `T` is derived from the
**mathematics of the relation and the invariants**, not learned:

- **T0 — identity.** Definitionally equals raw transfer. Sanity anchor.
- **T1 — sign flip.** Negate the score. Tests whether anti-transfer is *pure inversion*.
  **Analytically bounded in advance:** cycle 004's raw B was 0.4885, so T1 gives exactly 0.5115 and
  can recover at most `(0.5115−0.4885)/(0.7101−0.4885) = 10.4%`. **T1 alone cannot resolve Q2** —
  it is included so that outcome is on the record rather than discovered later.
- **T2 — threshold normalisation.** Divide every difference-valued feature by the target relation's
  threshold (`abs_diff_le_k` ↦ divide by `k`). The natural transport between bounded-difference
  relations of different width.
- **T3 — modulus alignment.** Replace parity features `(u − t) mod 2` with `(u − t) mod m` for the
  target relation's modulus `m`. The natural transport between congruence relations.
- **T4 — quantile standardisation.** Replace each companion invariant value by its quantile rank
  within that invariant's own distribution. The natural transport between invariants on different
  scales (conductor ~10³ vs signature ~10⁰).
- **T5 — T2 ∘ T4.** The only composition permitted; no further search over compositions.

**No `T` may be added, tuned, or removed after measurement begins.** A `T` that requires fitting to
the target cell is not a transport — it is relearning, and is scored as condition 3.

## 4. Pre-registered dispositions

Taken jointly. Each maps to exactly one of ADVANCE / REDESIGN / PARK / KILL per charter §2.

- **BOTH SURVIVE** — Arm A shows F_applied materially above F_pure and below oracle, **and** Arm B's
  best transport recovers < 25% of the relearning gap. ⇒ the decomposition is not an artifact of
  arithmetic oracles, and locality survives a serious transport attempt. **Disposition ADVANCE**, and
  the reconnaissance **terminates** with enough to justify rebuilding the instrument.
- **Q1 FAILS** — F_pure alone reaches the f-conditional ceiling, i.e. the signal is generator
  structure. ⇒ the positive lift of cycles 003–004 is substantially reinterpreted as benchmark
  reconstruction. **Disposition KILL** of the "cheap coordinates recover conditional navigation
  signal" claim; the arity finding survives untouched, being a type argument.
- **Q2 FAILS** — a frozen `T` recovers ≥ 50% of the relearning gap. ⇒ **chart mismatch, not
  locality.** Finding 3 is withdrawn, not merely demoted. **Disposition REDESIGN**, and the
  accumulation unit becomes a transportable law in better coordinates.
- **MIXED / AMBIGUOUS** — recovery 25–50%, or Arm A's increment inside noise. Report, force no
  branch, state the n required. **Disposition PARK.**

## 5. Prediction (recorded so it can be wrong)

**Q1: F_applied lands materially above F_pure** — I expect the commutation oracle to carry genuine
conditional structure, because commute rate varies with `v` within a fixed `(f,g)` pair (e.g.
`abs`/`neg` commute exactly at `v = 0`).
**Q2: no transport recovers ≥ 50%** — I expect locality to survive, with T4 the most likely to help.

**Discount this.** My record: wrong on 3 of 4 clauses in cycle 002; under-estimated in 003; wrong on
the ordering in 004; overreached on the "75%" phrasing; recommended a vacuous target for 005; and
overstated two of three findings until corrected. **Both predictions above are also the outcomes
that flatter the thread**, which is exactly why §2.1 and §3.1 were frozen before measurement.

## 6. Non-LLM controls (charter §20)

No LLM in the loop. Arm A's oracle is integer arithmetic over tables established by three-source
differential test; its space is exhaustively enumerated; its rules are exhaustively searched.
Arm B is rung 5 and **labelled as such** — a fitted, sampled estimate whose role is comparison
against condition 3, not standalone evidence.

**Mandatory assertions, failing loudly:** perfect predictor exactly 1.0; constant predictor exactly
0.5; metric invariant under strictly monotone score transforms; permuted labels at chance;
population digest matches `1b4abb1a…`; and for Arm A, the enumerated commutation table must
reproduce b2's logged `commutes` on all shared cells (already 39,273/39,273 at step 0).

**Hand-checkable rows:** ≥ 20 fully expanded rows per arm — state, candidate, every feature, label,
rank — so the arithmetic is verifiable without running the code.

## 7. Deliverables

`CYCLE_005_RESULT_*.md`, CAR-005, runners and raw outputs, and — per charter §14 and the HITL
disposition — the **terminal synthesis**, in one commit.

*— Diomedes, cycle 005 pre-registration, 2026-08-25. Frozen before measurement.*
