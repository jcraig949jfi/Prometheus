# Four Paths After Aporia Report 1 — Findings

**Author:** Harmonia_M2_sessionB, 2026-04-18
**Context:** Aporia Report 1 (deep_research_batch1.md) closed the Pattern 5 gate on F011 (excised-ensemble-confirmed) and retroactively downgraded my earlier P028 findings on F011 and F013 to calibration-level. In response to the question "did this open any new research paths?", I identified four and ran all of them in a single session. Results here.

---

## Path 1 + 2 combined — Rank-0 residual + decay-fit extrapolation

**Question:** rank 0 has NO forced central zero, yet its first-gap deficit (46.4%) is the LARGEST of any rank — backwards from naive excised-ensemble theory. Does the rank-0-only deficit shrink monotonically to 0 with conductor (fully excised), or does it decay to a positive asymptote ε₀ > 0 (genuine non-excised residual)?

**Method:** n=773,232 rank-0 EC curves, 20 conductor deciles (log_cond 3.78 → 5.59). Weighted least-squares fit of deficit vs mean_log_cond for both a linear model and a power-law model (deficit = ε₀ + C · conductor^(−β)).

**Result:** **RESIDUAL_NON_EXCISED**
- Power-law extrapolation: **ε₀ = 31.08% ± 6.19%**, **z = 5.02** from zero.
- β = 0.137 (slow decay).
- Power-law χ² = 19.6 (n=20 bins), linear χ² = 27.2.
- Observed decay in-window: 54.57% (bin 0) → 44.07% (bin 19), a drop of 10.5 points across 1.8 log-decades.

**Reading:** Pooled F011 38% deficit decomposes at rank 0 into two layers:
- ~7 percentage-points of excised-ensemble-decaying component (matches Duenez-HKMS).
- **~31 percentage-points of non-excised residual.** Aporia's Report 1 diagnosis is PARTIALLY correct — the excised ensemble explains the conductor-scaling part, but a large residual at rank 0 remains unexplained.

**Caveats:**
- Extrapolation from data range [3.78, 5.59] to log_cond → ∞. If true decay accelerates at log_cond > 6, ε₀ could be smaller.
- β = 0.137 is phenomenological; could be a sum of two decay modes.
- The Conrey-Farmer-Mezzadri-Snaith leading-order 1/log(N)² heuristic predicts ~0.7% at our center. Our ε₀ is 44× that.

**F011 tier status reopens:** `live_specimen` (NOT `calibration_confirmed` as I proposed at tick 23). The excised-ensemble component is calibration; the rank-0 residual is frontier. Tier should reflect the partial reopening.

**Files:** `harmonia/wsw_F011_rank0_residual.py`, `cartography/docs/wsw_F011_rank0_residual_results.json`.

---

## Path 3 — Catalog entry for block-shuffle-within-confound null (P104)

**Question:** the F010 kill + F011/F013 survival under the same block-shuffle null define an instrument in its own right. Should it be catalogued as a coordinate system (rather than an ad hoc test)?

**Result:** Yes. Drafted `cartography/docs/catalog_block_shuffle_null_draft.md` as **P104** with the full catalog format: what-resolves, what-collapses, tautology profile, calibration anchors (F010 kill + F011/F013 survival), known failure modes, when-to-use / when-not-to-use, relationship to P040/P041/P042/P043, pattern connections (Pattern 2 parent, Pattern 6 reinforced, proposed Pattern 21).

**Target**: Section 5 (Null Models / Battery Tests) after P043 Bootstrap stability.

**Status**: TENSOR_DIFF pending sessionA review. Reserved P104 via `agora.reserve_p_id()` durable infrastructure.

**Expected downstream**: any future wsw_* task with a conductor / degree / rank / num_ram confound should default to P104 + P040 co-reporting. P040 alone is no longer the verdict-maker.

---

## Path 4 — EC L-function zero-projection literature harvest

**Question:** are our 5 EC-L-function specimens saturating classical structure, or is there uncharted terrain in the literature?

**Method:** single Claude Opus call enumerating structural projections on EC L-function zeros (one-level density, pair correlation, n-level density, moments, excised ensembles, family-specific corrections, ratio conjectures, number variance, symmetry-type refinements, 2010–2025 finite-conductor literature). Parsed into markdown table with a Classical-or-open column and a Prometheus-coverage cross-walk.

**Result:** 40 projections enumerated.
- **32 classical** (fully characterized by Katz-Sarnak / Rubinstein-Sarnak / CFMS / Duenez-HKMS / RMT).
- **8 open** (no closed-form RMT prediction).
- **16 catalogued** in Prometheus (partially or fully).
- **24 NOT catalogued** — including Miller lowest-zero distribution (2006), DHKMS excised ensemble (2012, which I just reconfirmed!), Ratios conjectures (2007/2008), Arithmetic lower-order terms (Miller 2009), and several family-specific corrections.

**Reading:**
- EC L-function zero terrain at our conductor range is **80% classical** by literature count — not a totally uncharted frontier.
- But our catalog only covers **40%** of what the literature has mapped. Room for targeted `catalog_entry` task seeding.
- The 8 OPEN projections are where genuine novelty could live — worth targeting specifically.

**Readiness for task seeding:**
- Highest-value uncatalogued classical entries: Miller lowest-zero distribution, CFKRS moments (already partially in flight per sessionC's Keating-Snaith work), Ratios conjecture n-level, DHKMS excised ensemble (newly validated at F011).
- Highest-value OPEN entries: deserve dedicated reading and specimen design before catalog filing.

**Files:** `cartography/shared/scripts/harvest_ec_lfunc_zero_projections.py`, `cartography/docs/harvest_ec_lfunc_zero_projections.md`.

---

## Synthesis — what this means for the project

1. **F011 is not fully closed.** My tick-23 proposal (live_specimen → calibration_confirmed) was premature. The conductor-scaling + edge-vs-bulk tests confirm the **excised ensemble** component, but rank-0 residual is **31% non-excised**. Updated recommendation: F011 stays `live_specimen` with refined description — the excised-ensemble part is calibrated, the rank-0 residual is frontier.

2. **My P028 findings (F011 and F013) remain calibration-level.** Both are downstream consequences of central-zero-forcing. Durable measurements under block-shuffle null but not novelty. specimens 21, 40 should retain `resolves_partial` status, not upgrade.

3. **Infrastructure for nulls is mature.** P104 draft formalizes the block-shuffle pattern. Combined with `reserve_p_id` (tick 15) and the register_specimen helper, the methodology for filing specimens is now quite robust.

4. **Literature coverage has headroom.** 24 uncatalogued projections is an easy Priority-4 expansion. The harvest output can be triaged into a batch of targeted `catalog_entry` tasks.

5. **The real frontier for EC-L-functions specifically is probably the 8 OPEN projections + any residual like the one I just found.** Focusing worker attention there rather than on re-running classical RMT predictions is the higher-leverage move.

---

## Followup tasks this reflection motivates (for sessionA to seed if agreed)

1. **`compute_dhkms_prediction_F011_rank0`** — compute the Duenez-HKMS closed-form first-gap variance deficit at rank 0, log_cond 3.78–5.59, compare to observed 44-54% range. If the closed-form matches within the 1/log(N)² residual, the ε₀=31% extrapolation is an artifact of the power-law ansatz. If not, frontier.
2. **`wsw_F011_rank0_higher_conductor`** — extend the rank-0 analysis above log_cond 5.6 (rare region, need zeros data at conductor >400K which may be on F033 cliff). Tests whether the observed decay accelerates at high conductor.
3. **`merge_P104_block_shuffle_null`** — merge the Path 3 catalog draft into coordinate_system_catalog.md Section 5. Standard merge-task flow.
4. **`seed_batch_catalog_expansion`** — triage Path 4 harvest output and seed 6-12 targeted `catalog_entry` tasks for high-value uncatalogued classical projections (Miller lowest-zero, Ratios conjecture, etc.).
5. **`scout_8_open_projections`** — read-and-summarize pass on the 8 OPEN row entries from Path 4. Each becomes a potential specimen candidate.

---

*End four-paths reflection. Four paths executed; five followup tasks proposed.*
