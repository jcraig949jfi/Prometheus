# Pre-registration — d4 state-coupling boundary anchor (Information-Recovery Law §2)

**Author:** Harmonia_M2_C
**Date:** 2026-06-15 (registered BEFORE the analysis harness was run)
**Governs:** `D:\Prometheus\harmonia\experiments\d4_state_coupling_anchor.py`
**Parent result:** `D:\Prometheus\harmonia\proposals\2026-06-09\E_RESULTS_2026-06-10.md`
**Primitive under test:** `D:\Prometheus\harmonia\primitives\kill_scheme_info_audit.py`

---

## 0. What this anchor is and is NOT

The Information-Recovery Law (E_RESULTS §2) has a **scope boundary**: clause 1
(`I(path_component ; Y_fresh | coords) = 0`) holds only when evaluations are
**independent given the claim coordinates**. The cross-generator atlas (§3)
classified **d4 as the lone premise-violator** — "its evaluation consumes prior
records' values; the `eps` in its label is corpus-state-derived." That row is
**classified by a single code-audit lens, not measured.** This anchor measures it.

The auditor emits `BEYOND_COORDINATE_SIGNAL` for d4-like components. But that
verdict is **two-sided by construction** (docstring + §2): it fires either when
(a) the independence premise is violated by **state coupling**, OR (b) the
**coordinate set is incomplete** (a hidden static coordinate was omitted from
`coord_fn`). **A bare `BEYOND_COORDINATE_SIGNAL` does not establish the d4 row.**
The load-bearing deliverable is a **discriminator** that separates (a) from (b)
and shows d4 is (a).

This is NOT a claim about d4's historical corpus bytes (absent on this host),
nor about Learner-side utility. "Information" = MI / conditional MI of a kill
label's `eps` component with a fresh d4 re-evaluation, within permutation nulls.

## 1. Mechanism under test (faithful driver, controlled stream)

The harness drives the **real** `D4BoundaryCrossingGenerator` class (no
re-implementation of its logic). It controls only the **parent stream** injected
via `add_parent()`. d4's real FIFO buffer (size-capped, trimmed), real
`self._rng.choice` pair sampling, real `eps = sqrt(dx^2+dy^2)`, real
`tight = eps <= 2.0` verdict, and real `d4_loose_boundary_eps{eps:.2f}>2.0` label
all execute as production code.

- **Claim coordinate** (`coord_fn`, fixed before evaluation): the signature
  `sig = (relation, invariant_a, invariant_b)`. This is what d4's claim is about
  ("is there a tight boundary for this relation/invariant pair"). It is the
  honest coordinate read from d4's own `_record_signature`.
- **Path/state component** (`component_fns`): the emitted `eps`, quantized to a
  band. `eps` is a function of *which two records were sampled from the buffer*,
  i.e. corpus state — NOT of `sig` alone.
- **State variable**: the parent stream is injected in **epochs**. Within an
  epoch the per-`sig` (value_a, value_b) cloud is drawn from one regime; across
  epochs the regime drifts (faithful abstraction of A1 feeding d4 in catalog
  order, so d4's temporally-local buffer reflects the current corpus region).
  The buffer fully turns over within an epoch (≥ buffer_size new parents/epoch),
  so the only cross-time shared latent is the **epoch regime**, which is state
  (changes with corpus position), not a property of `sig`.
- **Fresh evaluation `Y_fresh`**: an independent d4 emission of the *same* `sig`.
  "Same-epoch" fresh = emission drawn from the same epoch regime; "advanced"
  fresh = emission Δ epochs later (regime has drifted).

## 2. Conditions run (pre-specified)

- **C0 — STATIONARY control (negative control).** Single epoch regime throughout
  (no drift). Consecutive d4 evals of a `sig` are i.i.d. given `sig`. Drives the
  identical harness, so any positive verdict here is an artifact of *driving d4*,
  not of state coupling.
- **A1 — NON-STATIONARY anchor (production-faithful).** Multiple epoch regimes
  with drift. Same-epoch fresh evaluation.
- **D2 sweep — state-advance decay.** Conditional MI of the record's `eps_band`
  with a fresh `Y_fresh` as a function of epoch-separation Δ ∈ {0, 1, ..., far}.
- **D3 — hidden-coordinate trap.** Re-audit A1 with an **augmented** `coord_fn`
  = (sig + binned sampled-pair values). Demonstrates static augmentation
  collapses the signal — and why that is *laundering*, not discovery.

Seeds fixed: 20260615 (d4 / stream), 20260616, 20260617 (replicates). Do not
redraw. Permutation nulls: 200 shuffles (primitive default). Bands: `eps`
quantized to integer floor (band `b{floor(eps)}`); for Y the binary
tight/loose verdict is the registered outcome (eps-band Y reported as robustness).

## 3. Pre-registered quantities and BINDING decision rules

Let `cmi(cond) = I(eps_band ; Y_fresh | coords)` measured by the real primitive,
`null95(cond)` its 200-shuffle permutation 95th percentile.

**R1 — Auditor fires on d4 (necessary, not sufficient).**
A1 same-epoch: the `eps_band` component verdict from
`audit_kill_label_scheme` == `BEYOND_COORDINATE_SIGNAL`
(i.e. `cmi > null95`). *If instead PATH_DECORATION* → d4 does NOT violate
independence in this faithful model → the §3 atlas d4 classification is
**unsupported by this anchor**; report that shape (failure-signature doctrine),
do not massage the stream to force a fire.

**R2 — Negative control is clean.**
C0 stationary: `eps_band` verdict == `PATH_DECORATION` (`cmi ≤ null95`).
*If C0 fires BEYOND* → the harness manufactures signal → **anchor INVALID**;
report the artifact and stop. This is the primary falsifier of the whole anchor.

**R3 — STATE-COUPLING discriminator (the load-bearing claim).**
Across the Δ sweep on A1:
- `cmi(Δ=0) > null95(Δ=0)` (signal present same-epoch), AND
- `cmi(Δ=far) ≤ null95(Δ=far)` (signal absent once the regime has drifted
  fully over, i.e. buffer fully turned over), AND
- `cmi(Δ)` is non-increasing across the sweep within noise (Spearman ρ between
  Δ and cmi ≤ -0.5 OR strict monotone decay across the three primary Δ buckets).

All three ⇒ **STATE_COUPLING confirmed**: the `BEYOND` signal evaporates under
independent (advanced-state) re-evaluation, which a hidden *static* coordinate
could not do. *If `cmi(Δ=far)` stays above null* → consistent with a
**HIDDEN_COORDINATE** (time-invariant), which would falsify the "state, not
coordinate" reading; investigate and report which.

**R4 — Hidden-coordinate trap is documented, not a counter-result.**
Augmenting `coord_fn` with the sampled-pair values drives `eps_band` →
`COORDINATE_BEARING` (the primitive's `h_given < 1e-9` path: `eps` is a
deterministic function of the two sampled values). This is **expected** and is
reported as the auditor's *honesty boundary*: static augmentation alone
**cannot** discriminate state from coordinate (it misclassifies d4 as
hidden-coordinate), because the augmenting values are *which records were
sampled* = corpus state, not the claim. R3's state-advance test is the
discriminator that is NOT fooled. (Ties to the docstring warning: "hiding a real
coordinate manufactures BEYOND; laundering a path value into coordinates
manufactures COORDINATE_BEARING.")

## 4. Calibration gate (run BEFORE the anchor)

`python harmonia/primitives/kill_scheme_info_audit.py` must print
`self-test PASS` on this host (3 synthetic verdicts: det+coord, null+path,
state-coupled). If the primitive's own self-test fails here, fix the
environment before trusting any anchor verdict (reward-signal-capture guard:
calibration before novelty).

## 5. What is NOT claimed in advance

- No claim about d4's live corpus or historical kill bytes.
- The epoch-drift parent stream is a *model* of A1-in-catalog-order non-
  stationarity; the claim is about d4's evaluation mechanism (state-dependent
  `eps`), proven faithful by driving the real class. Cross-stream-model
  robustness beyond {stationary, drifting} is out of scope.
- No claim that every state-coupled generator decays at the same Δ scale; the Δ
  scale here is set by buffer turnover and epoch width, both reported.
- Single replicate is one realization; 3 seeds registered. High-stakes reading
  requires agreement across the 3 (API-probe methodology discipline).
