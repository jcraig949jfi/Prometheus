# Diomedes — BOOTSTRAP (read this first, after any context reset)

**Written:** 2026-08-25, immediately before a planned context reset. **Purpose:** restore this seat
in minutes, not half an hour, and hand it an executable plan. Everything here is either a pointer or
a settled position; nothing here is speculation.

---

## 0. Who you are, in one paragraph

You are **Diomedes**, the Prometheus seat responsible for **coordinate adequacy** — *does Prometheus
represent mathematical search in coordinates that preserve information useful for deciding what
transformation to try next?* You operate a bounded autonomous research loop under
`LOOP_CHARTER.md`. You do **not** stop after every result to ask what to do next. You have run five
cycles; four are closed and the fifth is pre-registered and unrun. Your standing bias is that you
will tend to discover coordinate defects because that is your charter, and your prediction record is
poor — both are documented below and both are load-bearing.

## 1. Bootstrap — read in this order, nothing else

Five files. Stop when you can answer "what is pending and why."

1. **this file** — state and plan
2. `LOOP_CHARTER.md` — how you operate, incl. §20 (non-LLM controls) **as corrected by** file 3
3. `AMENDMENT_2026-08-25_arity_and_transport.md` — the corrections that supersede earlier framings
4. `CYCLE_005_PREREG_terminal.md` — the frozen, unrun experiment you are about to execute
5. `STATUS_2026-08-25.md` — the numbers, if you need them restated

**Do not** re-read cycles 001–004 unless a specific number is in dispute. Their conclusions are
summarised in §3 and their corrections in file 3. The cold-start tax is real; this list is the whole
tax.

**Verify the tree before working:** `git fetch origin && git rev-list --left-right --count
HEAD...origin/main` should read `0 0`. Other seats (Techne especially) commit to this repo
concurrently; expect to merge.

## 2. The synthesis — review vs. response, settled

An external review challenged the thread; the response accepted nearly all of it. What survives:

**Converged, adopted, no longer in dispute:**

- **The finding is arity, not geometry.** Not "failure geometry should become action geometry" but
  *Prometheus stored observations at the wrong causal arity.* And `verdict(state, action)` is **not**
  the fix either — the atomic object is `e = (x, a, x′, o, c)` with externally established evidence
  `o` and search context `c`. An **edge**, not a richer failure record.
- **The type argument is narrower than claimed.** It proves state-only residue is
  **action-insufficient by construction** (measured exactly 0.5000). It does **not** prove `Z(x,a)`
  is adequate — two actions with identical immediate statistics can enter different future basins.
  The real requirement is **decision-sufficiency relative to a horizon and objective**, which
  **nothing in this thread has tested.**
- **Locality is PROVISIONAL.** Anti-transfer establishes failure of the *tested representation and
  model family*, not intrinsic locality. Chart mismatch is unexcluded — that is Q2 of cycle 005.
- **The accumulation unit is a local transition model**, not a local policy. Policy is a downstream
  compression that has not been earned.
- **The LLM problem is solved architecturally and is not the hard part.** LLM proposes verbs →
  reality executes → record edges → statistics infer policies → **prospective execution judges
  policies**. The model is provenance for `a` and appears nowhere in `o`. `p(a|x)` may be
  arbitrarily contaminated; it cannot touch `P(x′,o|x,a)`.
- **There is no compiler for "right move."** A verifier establishes facts about *trajectories*;
  policy value is an estimate and demanding it carry event-grade certainty is impossible outside
  exhaustive spaces. For open action spaces use **paired empirical dominance under controlled
  budgets**: `P(solve|π₁,B)` vs `P(solve|π₂,B)`.
- **The §20 ladder had two axes conflated.** Certainty of *observation* is independent of uncertainty
  of *policy inference*. Doctrine: **infer freely; believe only prospective consequences measured
  through independent instruments.**

**Added by the response, beyond the review:**

- **The transport family was frozen in advance** (prereg §3.1). The review said "mathematically
  natural transformations" without specifying them; an unfrozen `T` makes the control
  unfalsifiable. Six are now fixed and may not be added to.
- **T1's ceiling was computed analytically before running**: raw transfer 0.4885 ⇒ sign-flip is
  exactly 0.5115 ⇒ maximum recovery **10.4%**. Sign inversion alone cannot resolve Q2.
- **Both cycle-005 predictions flatter the thread**, and this is stated in the prereg.

**Unresolved, and honestly so:**

- Decision-sufficiency is *named* but untested. No multi-step experiment exists anywhere in this
  thread.
- The transport family may be incomplete — a natural `T` may have been missed. If a reviewer names
  one, it is a **new cycle**, not an amendment to this one.
- Recommendation C (the `EDGE` primitive) touches `sigma_kernel/`, which is Techne's. Filed as a
  specification; **routing is unresolved and is James's call.**

## 3. Where the thread stands

Cycles 001–004 **closed**: REDESIGN, KILL, REDESIGN, REDESIGN. Cycle 005 **pre-registered and
unrun** (`94970ea8`), and it is **terminal** if it resolves both its questions.

The measured decomposition (positive control 1.0000, cheat control 0.4993–0.5005, digest
`1b4abb1a…`):

- chance 0.5000 · **Prometheus's recorded coordinates 0.5560** · best state-ignoring ranking 0.6254 ·
  cheap arithmetic `Z(x,a)` per cell 0.6600 · at finer conditioning 0.7101 · oracle 1.0000

Correct phrasing, **use verbatim**: *roughly three quarters of the observed improvement from chance
to the perfect state-specific oracle is unavailable to the best state-independent ranking.* These are
ranking accuracies, **not** information estimates. Never write "75% of the information."

Three findings, as corrected: **(1)** state-only residue is action-insufficient by construction —
KEEP, narrowed. **(2)** production omitted the transition semantics required to test its own thesis;
`sigma.symbols` = 0 rows, `step_trace` degenerate at 332,883/332,886 identical steps, yet ~48.4M
records carry parent links — KEEP, strong. **(3)** locality/anti-transfer — **PROVISIONAL**.

## 4. THE PLAN — execute in this order

### Step 1 — Cycle 005 Arm A (b2 commutation). Rungs 1–4.

Build `cycle005_armA_run.py`. Enumerate all 6×6×101 = 3,636 cells from
`cycle005_operator_tables.json` (already verified exact, three sources at 1.000000). Compute chance,
marginal ceiling, f-conditional ceiling, and the three nested feature sets `F_pure` / `F_applied` /
`F_oracle` exactly. Rule class = exhaustive search over the frozen predicate list, **not** gradient
descent. Emit ≥20 hand-checkable rows. Assert: perfect predictor = 1.0 exactly, constant = 0.5
exactly, monotone-invariance, permuted labels at chance, enumerated table reproduces b2's logged
`commutes` on all shared cells.

### Step 2 — Cycle 005 Arm B (transport). Rung 5, labelled.

Build `cycle005_armB_run.py` on cycle 004's population via `harvest_cache.load_verified()`. For each
ordered cell pair: raw transfer, each frozen `T0–T5`, and local relearning. Report recovery fraction
`(condition − raw)/(relearn − raw)`. **Decisive comparison is transport vs relearning.**

### Step 3 — Result, CAR-005, disposition.

Apply the joint dispositions in prereg §4 exactly as written. Do not soften them. Declare any
pre-registration defect openly, as was done in cycle 004.

### Step 4 — Terminal synthesis, then STOP.

Per charter §14 and the HITL disposition: what was tested, strongest positive and negative evidence,
surviving/killed/unresolved claims, what would have to become possible to reopen, consequences for
Prometheus. Commit, push, **stop**. **Do not manufacture a sixth question.**

### Step 5 — hand off, do not execute

- **Recommendation C** — the `EDGE(x_before, a, x_after, observations, provenance, context)`
  primitive with two interface-enforced invariants (no generator may write into the epistemic
  outcome namespace; observations are not collapsed to a success bit at write time). Techne's
  territory. **Raise, don't build.**
- **The smallest real test** — Lean tactic selection with a *closed* mathematical action vocabulary
  (`intro`, `apply Lᵢ`, `rw Lᵢ`, `simp`, `constructor`) and bounded premise candidates. Real proof
  states, exact execution, exact successor state, exact terminal verification, finite candidate sets,
  exhaustive evaluation at sampled states, **zero LLM**. Lean's own `exact?`/`apply?` provide
  non-LLM action generators as controls. This is a **new thread**, not a sixth cycle.

## 5. Hard constraints

Heredity rule — no new architecture. A6 — this thread still has no metabolic-cycle attachment;
closest is R2-5. HARD-2 — do not import the interpretability or RL research programme, only the
machinery. Pre-registration firewall — never move a gate after seeing a result; never add a feature
mid-measurement; never redefine a population that gave an inconvenient answer. Rows ship in the same
commit as the verdict. Contamination is the null hypothesis about your own output.

## 6. Known traps — your own record

**Calibration ledger, kept because it is unflattering.** Cycle 002: prediction wrong on 3 of 4
clauses. Cycle 003: right on direction, **under**-estimated the effect. Cycle 004: wrong on the
ordering — conflated "fits both passably" with "transfers." Synthesis 001: overreached on the "75%"
phrasing. Cycle 005 planning: recommended c4 as the replication target; it was **vacuous**, every
outcome field single-valued. Findings 1 and 3: overstated until external review corrected them.

**You are not well calibrated on this thread.** That is the argument for the firewall, not against
continuing.

**Three specific traps that have already fired once each:**

1. **Assuming semantics from field names.** Nearly assumed what `log2_floor` meant. Recover from data
   and differential-test. (Step 0 did this: 37,330/37,330 and 39,273/39,273.)
2. **Cross-cycle anchors between different estimators.** Cycle 004's prereg required arms to
   reproduce cycle 003's numbers; they diverged *by construction* because training regimes differed.
   State the estimator, not the label.
3. **Pre-flighting only some cycles.** Every cycle that skipped a pre-flight cost a redesign. Run
   one every time; it has twice returned VACUOUS and saved the cycle.

## 7. What NOT to do

Do not process the 346 GB corpus. Do not build a learned transfer function — cheap arithmetic has
not been exhausted and the prior is poor. Do not test cross-domain transfer because it sounds like
Prometheus. Do not let this become a standing lane. Do not claim navigation from edges alone —
**direction exists only relative to a terminal objective and horizon**, so assembled parent-linked
records are a **transition corpus**, never a "navigation corpus."

*— Diomedes, bootstrap for post-reset resumption, 2026-08-25.*
