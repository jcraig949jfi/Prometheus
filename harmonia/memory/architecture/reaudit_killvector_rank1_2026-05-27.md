# Re-audit: the "rank-1 KillVector basis" finding is an instrumentation artifact

**Auditor:** Harmonia C
**Date:** 2026-05-27
**Target claim:** `topological_falsification_engine.md` §6.2 — *"Is the existing
KillVector basis real or proxy? — MEASURED 2026-05-27: rank-1 (the proxy pole)
... Effective dimensionality = 1.0 ... a single continuous band-distance ruler
wearing a 12-D costume."*
**Verdict:** **The rank-1 result does not measure the basis.** It measures the
candidate population's band-pass rate. The basis's dimensionality, orthogonality,
and "ruler-in-costume" status are **UNMEASURED** — not measured-as-1. The claim
as written (and the "FLIP" experiment built on it) must be downgraded.
**Validators:** `harmonia/tmp/kv_basis_dim_inband.py`,
`harmonia/runners/gen_inband_basis_demonstrator.py`

---

## 1. What the original audit measured

The original probe (`harmonia/tmp/kv_basis_dim.py`) loaded the 24,000 per-record
vectors in `prometheus_math/_native_kill_vector_pilot.json`, built a correlation
matrix over the components that show margin-variance, and reported
participation-ratio = 1.0 (only `out_of_band` alive; `out_of_band` triggers
99.93%). It correctly named the mechanism: *"a Phase-0 band gate rejects ~99.9%
of candidates before the downstream 11 falsifiers ever run — rank-1 by
population, not by design."*

## 2. What the re-audit found (VALIDATED)

Re-running conditioned on what the pipeline actually records
(`kv_basis_dim_inband.py`):

```
records by #canonical-components present:
   1 components present : 24000  (100.000%)
out_of_band triggered: 23983/24000 = 99.929%
IN-BAND (>1 component computed) records: 0  (0.0000%)
```

**Every one of the 24,000 vectors carries exactly one component** (`out_of_band`).
The other 11 falsifiers are not present in the data **even once** — not "they
don't fire", they were **never recorded**. This includes the success case:

```
episode 622, operator ppo_mlp@seed=0, reward 100.0,
  M = 1.1762808182599302   (Lehmer's number, essentially exact)
  kill_vector: [ {out_of_band, triggered: false, margin: 0.0} ]   # 1 component
```

The candidate that **hit the truth** still emitted a 1-component vector. So the
deep falsifiers are absent **not** because the operator produced gross misses,
but because the pilot's emission path never recorded them — even for an in-band,
reward-100 hit.

**A correlation matrix over single-component vectors is algebraically forced to
rank-1.** No other answer is possible. So "effective dimensionality = 1.0" is a
restatement of "this pilot logged one falsifier", and "126,983× distinguishability
wearing a 12-D costume" is unsupported: the other 11 dimensions are **unobserved,
not collapsed.**

**Both corpora the audit cited are structurally incapable of showing more.** The
legacy 315k backfill synthesizes "out_of_band component **plus the single**
triggered component" (`KILL_VECTOR_SPEC.md:95-97`) — ≤2 components by
construction. The basis has never been measured on data that records it.

## 3. The mechanism (two stacked short-circuits)

1. **Pipeline phase-0 short-circuit.** `discovery_pipeline.py:341-368`: when
   `M ∉ (1.001, 1.18)`, `process_candidate` returns immediately with a
   1-component (`out_of_band`) kill_vector. 99.93% of candidates exit here.
2. **Pilot never passes a full record.** `native_kill_vector_pilot.py`'s
   `emit_kill_vector_for_episode(..., pipeline_record=None)` emits the phase-0
   single component whenever no pipeline record is supplied
   (`test_native_kill_vector_pilot.py::test_smoke_emit_kill_vector_for_phase0`
   pins this). The pilot's wiring reads `env.pipeline_records()` (lines 235-247)
   but the emitted data shows it never carried full vectors for in-band episodes
   — including ep 622. Net: even the 0.07% in-band candidates emitted 1 component.

## 4. Why the "FLIP" experiment is invalid as stated

§6.2 proposes: *"if LLM-mutation raises the kill-space effective dimensionality
above 1, the thesis has legs; if it stays rank-1, the engine maps one ruler
forever."* This is confounded three ways:

- **It measures in-band yield, not basis structure.** On this instrumentation,
  dim stays 1 for *any* operator. Raising it requires recording all 12 (a
  logging change). "Dim climbs above 1" is then a restatement of "the operator
  produced ≥1 in-band candidate whose vector carries ≥2 components" — i.e. the
  survival rate already in `bottled_serendipity.md` §7.1 — not near-miss geometry.
- **It is blind to orthogonality**, which the doctrine itself says is the entire
  fork (§3: "the fork is entirely the basis"). PR > 1 is consistent with the
  doctrine's *own failure pole* (correlated rulers, "monoculture wearing a map
  costume"). The 5 catalog components are correlated by construction (overlapping
  catalogs), so a "pass" could land squarely in the failure pole.
- **It violates the doctrine's own Invariant A** ("frame before mechanism"):
  swapping the operator and attributing a dim rise to the near-miss thesis,
  without first controlling for the gate-ordering / in-band-yield confound, is
  ablating before the frame check.

The audit's own best insight — *"rank-1 by population, not by design"* — taken
seriously, **invalidates the proposed test**, because dim > 1 would *also* be
"by population, not by design."

## 5. Corrected verdict

- The thesis (LLM-mutation populates the near-miss shell → real multi-dim basis)
  is **untested**, not confirmed and not refuted.
- "Rank-1 basis / 12-D costume" → downgrade to: **basis dimensionality
  UNMEASURED; the pilot recorded a single falsifier.**
- Environmental finding: `prometheus_math`'s battery imports `cypari`, which is
  **absent on the M2 Windows host**; the real battery cannot run here. The
  original pilot was generated on a cypari-equipped machine (M1/M2). Any
  production re-measurement must run there.

## 6. The corrected experiment ladder

1. **Instrument first (this re-audit's step 1).** Record all components for
   in-band candidates. Demonstrator: `gen_inband_basis_demonstrator.py` (control
   arm, cypari-free reference battery — see §7). Production fix: wire
   `emit_kill_vector_for_episode` to a real `process_candidate` record for
   in-band episodes; add a regression test asserting in-band → >1 component.
2. **Measure the §3 fork, not PR.** Report the eigenspectrum **and the max
   off-diagonal correlation** on in-band candidates. Orthogonal pole = success;
   any |corr|≈1 block = collinear rulers (the costume).
3. **Control arm.** Band-restricted random search matched on in-band yield (the
   demonstrator IS this arm). If the LLM arm gives the same in-band basis,
   hallucination adds nothing.
4. **Stratify on catalog-miss (outcome-2).** A pass driven by catalog *hits* is
   memorized rediscovery (`bottled_serendipity.md` Appendix B.1, outcome 1), not
   discovery — and for Salem/Lehmer the near-miss shell *is* memorizable catalog
   content, so this is load-bearing.

Only after 1–3 land in the orthogonal pole on catalog-miss survivors does
"dim > 1" mean what the FLIP wants.

## 7. First in-band basis measurement (demonstrator, control arm)

> Filled from `gen_inband_basis_demonstrator.py` output. Reference battery
> (out_of_band, reciprocity, irreducibility, F1, F6, F9), cypari-free, validated
> against the Lehmer anchor and the F6 test case. Catalog + F11 not evaluated
> here. This is the band-restricted-random CONTROL arm, not the LLM arm.

**Result (n = 15 in-band candidates, from 4M draws — band yield 0.0004%):**

```
component                trig_rate  n_finite   margin_std
out_of_band                0.0000        15     2.7e-06     (~const: in-band M cluster tightly)
reciprocity                0.0000        15     0           (dead by construction)
irreducibility             1.0000        15     0.8165      (ALL 15 reducible; factor-count varies)
F1_permutation_null        0.1333         0     0           (margin deferred per spec)
F6_base_rate               0.1333        15     0.8692      (distinct-coeff count varies)
F9_simpler_explanation     0.0000        15     2.7e-06     (= M-1.001, affine in M)

IN-BAND MARGIN basis (4 margin-alive cols):
            out_of_  irreduc  F6_base  F9_simp
out_of_      1.000    0.472    0.114    1.000
irreduc      0.472    1.000   -0.094    0.472
F6_base      0.114   -0.094    1.000    0.114
F9_simp      1.000    0.472    0.114    1.000
eigenvalues: [2.342, 1.055, 0.603, 0.000]
participation-ratio (EFF DIM): 2.30 of 4    max |off-diagonal corr|: 1.000
```

**Three findings, both halves of the critique confirmed empirically:**

1. **Effective dim = 2.30, not 1.0.** Once in-band candidates are actually
   recorded, the basis is multi-dimensional. "Rank-1 basis" is **refuted as a
   basis claim** — it was always a population artifact.
2. **`out_of_band` and `F9` are perfectly collinear (corr = 1.000; one
   eigenvalue is exactly 0).** Both are affine in M (`M-1.18`, `M-1.001`). Two
   of the twelve named "dimensions" are literally the same ruler. So the
   "12-D costume" intuition has a real kernel — there *is* redundancy — but the
   right diagnosis is "~3 independent axes (M-ruler, factor-count, distinct-coeff
   count), one double-counted," not "1." **This is exactly why PR alone is
   insufficient and the off-diagonals must be read** (ladder step 2): PR = 2.30
   would mislead; the corr matrix exposes the duplicated ruler.
3. **The control arm is 100% reducible** (irreducibility triggered 15/15). The
   band-restricted-random operator produces cyclotomic-product near-misses, not
   genuine irreducible Salem polynomials. This suggests the sharpest
   discriminator between a control operator and a "real" one may be the
   **irreducibility trigger-rate**, not effective dimensionality — a better
   target metric for the eventual LLM arm than the FLIP's dim test.

**Caveats (run the knockout on this result too):** n = 15 is small — the
band-restricted reciprocal space for coeffs ∈ {−2..2} contains very few in-band
polys; correlations are indicative, not settled. Widen the coeff range or seed
from known small-Salem polys to grow n. Reference battery only (catalog + F11
not evaluated; F1 margin deferred). This is the CONTROL arm — the LLM arm is the
open experiment.

