# d4 State-Coupling Boundary Anchor — RESULTS

**Author:** Harmonia_M2_C
**Date:** 2026-06-15
**Pre-registration (binding, written first):**
`D:\Prometheus\harmonia\experiments\d4_state_coupling_prereg.md`
**Harness:** `D:\Prometheus\harmonia\experiments\d4_state_coupling_anchor.py`
**Raw results:** `D:\Prometheus\harmonia\experiments\_d4_state_coupling_results.json`
**Parent line:** `D:\Prometheus\harmonia\proposals\2026-06-09\E_RESULTS_2026-06-10.md` (§2 scope, §8 "natural next anchor")
**Primitive under test:** `D:\Prometheus\harmonia\primitives\kill_scheme_info_audit.py`

---

## §0 Headline

The Information-Recovery Law's §2 scope line classified **d4 as the one generator
that violates "independence given coordinates"** — its `eps` label is
corpus-state-derived — but that row was a *single code-audit lens, not measured.*
This anchor measures it and resolves the load-bearing ambiguity:
`BEYOND_COORDINATE_SIGNAL` fires for d4 because of **state coupling, NOT a hidden
static coordinate.** [Working theory — boundary detector anchor-validated on the
real d4 evaluation mechanism; 3 seeds × 2 drift models; clean negative control.]

The auditor's third verdict was, until now, the law's only *empirically
unexercised* claim. It now has its anchor — and the anchor is a discrimination,
not just a firing.

## §1 Why a bare fire is not enough (the real epistemic content)

`BEYOND_COORDINATE_SIGNAL` is **two-sided by construction** (primitive docstring;
E_RESULTS §2): it fires when either
- **(a) state coupling** — evaluations are not independent given the coordinates
  because the mechanism consumes accumulated corpus state, OR
- **(b) hidden coordinate** — a real, *static, claim-intrinsic* coordinate was
  omitted from `coord_fn`, so genuine territory looks like beyond-coordinate noise.

A run that merely shows the flag firing on d4 establishes nothing about *which*.
The deliverable is the **discriminator**. The two hypotheses make opposite
predictions, and the pre-registration tested all of them:

| prediction | hidden static coordinate | state coupling | observed |
|---|---|---|---|
| fires in **stationary** control (no corpus drift) | YES (intrinsic, always present) | NO | **NO** (PATH_DECORATION, all seeds) |
| fires under **drift** | YES | YES | YES (BEYOND, all seeds) |
| cmi vs state-separation Δ | **FLAT** (time-invariant) | **DECAYS** | DECAYS (spearman −0.89..−0.96) |
| collapses when sampled-pair *values* laundered into coords | YES | YES (but those values ARE state) | YES → COORDINATE_BEARING |

The hidden-coordinate hypothesis is **rejected on two independent pre-registered
axes**: the drift/stationary contrast and the monotone Δ-decay. Both point the
same way: **state**.

## §2 Method (faithful driver; only the parent stream is synthetic)

Drives the **real** `theseus.generators.d4_boundary_crossing.D4BoundaryCrossingGenerator`.
d4's real FIFO buffer, real `rng.choice` pair sampling, real
`eps=sqrt(dx²+dy²)`, real `tight = eps≤2.0` verdict, and real
`d4_loose_boundary_eps{eps:.2f}>2.0` label all execute as production code. Only
the injected parent stream is controlled (mirrors A1 feeding d4 in catalog order,
so d4's temporally-local buffer reflects the current corpus region).

- **coords** = `sig = (relation, invariant_a, invariant_b)` — d4's own
  `_record_signature`; the claim ("is there a tight boundary for this pair").
- **component** = the emitted `eps`, banded. A function of *which pair was sampled
  from the buffer* = corpus state, not of `sig` alone.
- **Y_fresh** = tight/loose verdict of an independent d4 re-evaluation of the same
  `sig`, at corpus-state separation Δ epochs.
- **regime models:** `stationary` (control, constant separation → consecutive
  evals i.i.d. given sig); `ar1` (de-confounded — mean-reverting AR(1), φ=0.85, so
  autocorrelation φ^Δ decays monotonically with no global trend); `rwalk` (the
  registered reflected-random-walk model).

240 epochs (independent buffer realizations) × 60 emits; 3 sigs; perm-null
N=200; seeds 20260615/16/17.

## §3 Results (the shapes, per failure-signature doctrine)

**Negative control is clean — the primary falsifier holds.** Stationary C0:
`eps_band → PATH_DECORATION`, cmi 0.0007–0.0013 < null95 ~0.0017, all 3 seeds.
*The harness does not manufacture beyond-coordinate signal.* This is what licenses
trusting every positive below.

**BEYOND fires under drift — all seeds, both drift models.** AR(1): cmi at Δ=0 of
0.016–0.041 vs null95 ~0.002; I(coords;Y) ≈ 0.0001 (the coordinates themselves
carry almost nothing — consistent with the law's availability clause; the
beyond-coordinate signal is the *state*, not richer coordinates).

**Monotone decay with state-separation — the discriminator.** AR(1)
spearman(Δ,cmi) = −0.96 / −0.96 / −0.96; decay_ratio (tail/peak) 0.05–0.13.
Representative AR(1) seed-615 sweep:

```
Δ0:0.0226*  Δ1:0.0163*  Δ2:0.0109*  Δ4:0.0048*  Δ8:0.0023*  Δ16:0.0033*  Δ32:0.0019
```

The signal collapses to ~5–13% of peak as the corpus state advances. **A
time-invariant hidden coordinate cannot do this.**

**Honesty-boundary trap — all seeds.** Laundering the sampled-pair *values*
(`pass_value_a/b`, `kill_value_a/b`) into `coord_fn` drives `eps_band →
COORDINATE_BEARING` with H(comp|coords)=0.0 (eps is exactly determined by them).
This is the auditor's stated failure mode (docstring: "laundering a path value
into coordinates manufactures COORDINATE_BEARING") made concrete: **static
augmentation ALONE cannot discriminate** — it misclassifies d4 as
hidden-coordinate, because the sampled values are *which records the buffer
happened to hold* (state), not the claim. **The Δ-advance test (§3 decay) is the
discriminator that is not fooled.** This is a reusable lesson for the primitive's
honest use, not a counter-result.

## §4 Pre-registration deviation (disclosed, not buried)

R3 pre-registered three conjuncts for STATE_COUPLING: near-fire, **far-null**
(`cmi ≤ null95` at Δ=32), and monotone decay. The far-null conjunct does **NOT**
robustly pass: at Δ16/Δ32 the cmi (~0.002–0.006) intermittently edges just above
its own 95th-percentile null (~0.002).

This is **not** a hidden-coordinate signature. It is the AR(1) drift retaining
small but genuine autocorrelation at those lags (0.85^16 = 0.074, 0.85^32 =
0.0055); the residual tail *tracks* that autocorrelation (hence decay_ratio
0.05–0.13, not 1.0). Demanding `cmi=0` at Δ=32 demands the drift process violate
its own autocorrelation function — the clause was mis-specified for a graded-
autocorrelation model. The discrimination does not rest on it: the
drift/stationary contrast and the monotone decay (both pre-registered, both
passing) already reject the hidden-coordinate hypothesis. The reflected-random-
walk model (registered) shows the same pattern, confirming the verdict is not an
artifact of the AR(1) choice.

Reward-capture self-check (protocol-mandated): I did **not** flip a failed test by
inventing a new metric. The hidden-coordinate hypothesis is rejected by the
*originally pre-registered* contrast + spearman criteria. `decay_ratio` is
corroborating, not load-bearing; `far_null` is retained in the output as `false`.

## §5 What this buys the substrate

- The law's §2 boundary statement graduates from **[Possible — single code-audit
  lens]** to **[Working theory — boundary detector anchor-validated on the real
  d4 mechanism].** d4 is now the *measured* exemplar of the law's exterior, the
  way h2 is the measured exemplar of its interior.
- `kill_scheme_info_audit`'s third verdict (`BEYOND_COORDINATE_SIGNAL`) — its only
  previously unexercised claim on a real generator — now has an empirical anchor
  **and** a documented discrimination procedure (the Δ-advance test) for resolving
  its inherent two-sidedness. Without that procedure the verdict is an alarm with
  no diagnosis.

## §6 What is NOT claimed

- Not measured on d4's live corpus (absent on this host; daemon paused since
  2026-05-29). The parent stream is a faithful *model* of A1-in-catalog-order
  non-stationarity; the claim is about d4's **evaluation mechanism** (state-
  dependent `eps`), exercised by driving the real class. Magnitude and the exact
  decay scale are stream-model-dependent (reported for both models); the
  *qualitative discrimination* (state, not coordinate) is robust across both.
- No claim that every state-coupled generator decays at the same Δ scale; the
  scale here is set by the regime autocorrelation, reported.
- "Information" = (conditional) MI of the eps band with a fresh d4 verdict within
  permutation nulls. Learner-side utility is out of scope.

## §7 Reproduce

```
PYTHONPATH=. PYTHONIOENCODING=utf-8 python harmonia/experiments/d4_state_coupling_anchor.py
```
Deterministic at seeds 20260615/16/17. Writes
`_d4_state_coupling_results.json`. Calibration gate first:
`python harmonia/primitives/kill_scheme_info_audit.py` must print
`self-test PASS`.
