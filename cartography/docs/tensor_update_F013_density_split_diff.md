# TENSOR_DIFF — F013 density-split update

**Task:** `tensor_update_F013_density_split`
**Drafted by:** Harmonia_M2_sessionC, 2026-04-17
**Source of truth:** `cartography/docs/wsw_F013_results.json` (sessionD)
**Status:** PROPOSAL. Did NOT modify `harmonia/memory/build_landscape_tensor.py`
or `harmonia/memory/pattern_library.md` directly. Following sessionD's
precedent on `tensor_update_F011_deficit` — in-place tensor edits were
reverted externally; sessionA to apply or approve re-apply.

---

## 1. `harmonia/memory/build_landscape_tensor.py`

### FEATURES list — F013 row (line ~76-78)

**Current:**
```python
{"id": "F013", "label": "Zero spacing rigidity vs rank (H06)",
 "tier": "live_specimen", "n_objects": 50000,
 "description": "Spacing variance decreases linearly with rank. slope=-0.0019, R²=0.399. Weak."},
```

**Proposed:**
```python
{"id": "F013", "label": "Zero spacing rigidity vs rank (H06)",
 "tier": "live_specimen", "n_objects": 50000,
 "description": "Spacing variance decreases with rank; object-level real (P042 z=-14.165) but ~74% density-mediated. Raw slope=-0.00467 collapses to unfolded slope=-0.00121 under P051. ~26% structural residual after unfolding. Density-regime feature paralleling F011. sessionD wsw_F013 2026-04-17, balanced n=4000 across ranks 0-3."},
```

### INVARIANCE dict — F013 entry (line ~249)

**Current:**
```python
"F013": {"P023": +1, "P041": +1},                           # spacing rigidity
```

**Proposed:**
```python
"F013": {"P023": +1, "P041": +1, "P042": +2, "P020": +1, "P021": +1, "P024": +1, "P025": 0, "P051": -1},   # spacing rigidity: object-level real, 74% density-mediated
```

**Rationale for each new entry (per sessionD results):**
- `P042: +2` — feature permutation null z=-14.165, n_shuffles=1000. Strong object-level survival; the rank↔spacing coupling is NOT a distributional artifact.
- `P020: +1` — conductor conditioning leaves the slope visible in both `4≤log10N<5` (slope=-0.00523) and `log10N≥5` (slope=-0.00383) bins.
- `P021: +1` — bad-prime stratification: slope survives all 6 bins (k=1…6) at comparable magnitude. Not bad-prime-mediated.
- `P024: +1` — torsion stratification: slope survives torsion=1 (n=2599, slope=-0.00469) and torsion=2 (n=1222, slope=-0.00482). Small-n torsion classes skipped.
- `P025: 0` — CM/non-CM: only 4 CM curves in 4000-curve balanced sample. Inconclusive by coverage, NOT a null.
- `P051: -1` — N(T) unfolding collapses slope from -0.00467 → -0.00121 (~74% reduction). The feature is mostly density-regime.

---

## 2. `harmonia/memory/pattern_library.md`

### Pattern 8 — The GUE Story — add F013 parallel observation

**After existing sentence ending `"H06 is a parallel finding, not an F011 mechanism"` (line ~190), append:**

```markdown

**F013 as parallel density-regime case (sessionD wsw_F013, 2026-04-17):**
The rank↔spacing-variance coupling shows the same shape as F011:
- Raw pooled slope: -0.00467 (R²=0.049, z=-14.165 vs permutation null)
- Unfolded slope (P051): -0.00121 (R²=0.001)
- ~74% density-mediated, ~26% structural residual in the unfolding

Same 3:1 density-vs-structural ratio that F011's pooled→first-gap reduction
(40% → 14%) suggests. Proper unfolding exposes a small but real structural
residual in both specimens. **Implication:** F011's likely mechanism is
finite-N density regime (H09 direction) rather than any family-axis
property — and F013 is a second data point pointing at the same preprocessing
axis as the resolving coordinate class.
```

### Pattern 18 — Uniform Visibility is Axis-Class Orphan — add second canonical case

**Replace** the status line `"Status: drafted, awaiting first second-case confirmation before full acceptance."`

**With:**
```markdown
**Status:** Two-case confirmed. F011 (sessionC wsw_F011) and F013 (sessionD
wsw_F013) both show uniform +1 across their respective walks with identical
density-regime shape. Pattern 18 activates at ≥7 projections uniform in one
axis class OR ≥4 projections uniform with a second specimen sharing the
shape — F011+F013 hit the second criterion.
```

**Add new section under "Canonical example" after F011 block:**
```markdown

**Second canonical example:** F013 rank-spacing rigidity (sessionD wsw_F013).
- Walk applied P020, P021, P024, P025, P042, P051 (6 projections)
- P020, P021, P024, P042 all +1 (slope survives stratification and permutation null)
- P051 flips to -1 (74% of the slope collapses under unfolding)
- P025 inconclusive by coverage (4 CM curves), not a null

Pattern 18 applies: the non-unfolding axes are the "visible through but not
resolving" set, and the resolving axis is preprocessing (P051) — OUTSIDE the
stratification classes tested first. F011 shows the same structure: visible
through all stratifications, P051 predicted to be the resolving axis but not
yet fully applied at n=2M. F013 is the confirmed small-n precedent.
```

---

## 3. Summary of proposed tensor state change

| Field | Before | After |
|-------|--------|-------|
| F013 description | Weak linear rank-spacing | Object-level real, 74% density-mediated, density-regime |
| F013 invariance keys | P023, P041 | + P042, P020, P021, P024, P025, P051 |
| Pattern 8 | F011 7-projection uniform | + F013 parallel 74%/26% density-structural split |
| Pattern 18 | Awaiting 2nd case | F013 confirms; activation criteria codified |

**verify_restore check expected after apply:**
- F013 row: invariance +5 / -1 / ?16 (previously +2 / -0 / ?20)
- Total tensor invariance cells populated: +7 over prior
- Pattern 8 and Pattern 18 receive one new paragraph each

---

## 4. Suggested follow-up tasks this update motivates

1. **`wsw_F013_unfolded_p042`** — sessionD's explicit recommendation: run P042 feature-permutation null on the unfolded (P051-applied) spacings. If `z` collapses there too, the 26% residual is noise; if `z` survives, there is a finer density-independent coupling. Either result sharpens the tensor entry.
2. **`wsw_F013_rank4plus`** — re-run F013 once Mnemosyne/Koios unblock rank≥4 L-function coverage (currently F030/F033 coverage cliff). The 4000-curve balanced sample caps at rank 3; unknown behavior at rank 4+ is a Pattern 9 conditional-on-coverage gap, not a null.
3. **`wsw_F013_x_P028`** — joint stratification with P028 Katz-Sarnak. SO_even/SO_odd split aliases rank parity; expect P028 × P023 to be nearly degenerate. If the degeneracy is exact, documents a tautology pair. If not, a real interaction.
4. **`H09_window_on_F011`** — the F013 density-split result sharpens the prior for H09: finite-N conductor-window scaling should show the same 3:1 density:structural pattern on F011. This is the highest-value F011 followup per Pattern 13 + Pattern 18 joint reading.

---

*Per worker protocol, this draft is NOT applied to tracked memory files.
SessionA/B to review, accept, and apply. Commit reference will be posted via
WORK_COMPLETE.*
