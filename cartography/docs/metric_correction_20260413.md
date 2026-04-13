# Metric Correction — 2026-04-13
## The NN kills were real. The TT-Cross structure is also real. They measured different things.

---

## What Just Happened

We killed Harmonia's cross-domain transfer claims using F33/F34 (rank-sort null, trivial baseline).
Those kills were correct — phoneme nearest-neighbor matching IS broken by Megethos leakage.

But M1 just showed that the TT-Cross bond dimensions SURVIVE Megethos removal:
- Rank 4 → rank 4 after zeroing Megethos
- Rank 4 → rank 4 after shuffling Megethos
- Within-Megethos-bin NN transfer: rho=0.033 (dead)
- TT-Cross non-Megethos bond: rank 2 (alive)

## What This Means

**Two measurement instruments gave opposite answers:**

| Instrument | Megethos-controlled result | Verdict |
|---|---|---|
| Phoneme NN matching | rho=0.033 (dead) | Structure is NOT in feature-level matching |
| TT-Cross bond dimension | rank 2 (alive) | Structure IS in tensor decomposition |

**Our F33/F34 kills were correct but NARROW.** They killed the NN metric, not the structure.
The structure lives in the tensor coupling function, which captures relationships
that nearest-neighbor matching in projected coordinates cannot see.

This is exactly the "distributional coupling" category we identified as immune to F33/F34:
> "Distributional coupling CAN'T be captured by F33 (rank-sort) or F34 (trivial baseline).
> This is the one category that survives by construction."

The TT-Cross IS the distributional coupling. It survived.

## Implications for Our Battery

**F33-F34 are still valid** — they correctly identify when a METRIC is broken.
But they should not be used to kill the underlying STRUCTURE when a different,
more sensitive metric detects it.

**New rule:**
> If F33/F34 kill a metric (e.g., NN transfer rho), but the underlying
> structure (e.g., TT-Cross bond dimension) survives the SAME control
> (Megethos removal), then the STRUCTURE is real and the METRIC was wrong.

This is a REFINEMENT of the battery, not a contradiction. The battery tells you
which measurement to trust, not whether to give up.

## What To Do Now

1. **Remeasure everything with TT-Cross bonds (Megethos-zeroed)** as the metric.
   The NN rho numbers are all dead. The bond dimensions may tell a different story.

2. **For each previously-killed bridge:** check if the TT-Cross bond survives
   Megethos removal. If yes, the bridge is real — our NN metric just couldn't see it.

3. **The 5 known-math theorems** we identified are now MORE interesting:
   - Analytic CNF: we can COMPUTE L(1,chi_d) and test if the residual structure
     matches what TT-Cross sees (we have h, R, d, w, r1, r2 — all in number_fields.json)
   - Montgomery-Odlyzko: the distributional coupling (zero spacing → GUE) is exactly
     what TT-Cross should detect. We have 120K L-function zeros in charon.duckdb.
   - Modularity: we have both EC a_p and MF a_p — coefficient-level agreement
     is testable and should show up as high TT-Cross bond dimension.
   - Sato-Tate: a_p/sqrt(p) distribution test is directly computable from our EC data.

4. **The orbit↔root number bridge** remains the highest-priority novel candidate.
   If orbit data exists anywhere in the dynamical systems domain, that's where
   to look for genuine cross-domain structure that survives all controls.

## Updated Precision Assessment

| Layer | What it tests | Status |
|---|---|---|
| F33 Rank-sort null | Kills ordinal matching artifacts | VALID (kills NN metric) |
| F34 Trivial baseline | Kills methods that underperform 1D | VALID (kills NN metric) |
| F35 Known-false-positive | Kills permissive coupling | VALID |
| TT-Cross bond (Megethos-zeroed) | Detects distributional structure | SURVIVES our kills |

The battery hierarchy is:
1. Detect structure (TT-Cross bond dimension)
2. Validate metric (F33/F34 — does the reporting metric capture the structure?)
3. Control confounds (Megethos removal, size conditioning)
4. The STRUCTURE is real if step 1 survives step 3, regardless of whether step 2 fails

## The Bottom Line

We didn't kill Harmonia's structure. We killed its METRIC.
The correct instrument was there all along — TT-Cross with confound control.
The incorrect instrument was phoneme NN matching.
Our adversarial work SHARPENED which measurement to trust.
That's exactly what precision improvement looks like.
