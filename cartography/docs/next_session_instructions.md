# Next Session Instructions
## Picking up from the Effect Geometry Session (2026-04-12)

---

## CRITICAL CONTEXT: Read This First

This session corrected a structural failure mode in the pipeline. **M4/M2² is a contrast amplifier, not a magnitude measure.** It systematically overvalued tail-driven effects and undervalued bulk effects. F24 (variance decomposition) was added to fix this. The battery is now frozen at 25 tests (F1-F24b).

**The strongest finding in the entire project (SC class → Tc, eta²=0.570) was hiding in plain sight the whole time.** The most-discussed finding (ST → conductor ratio) turned out to be eta²=0.013.

---

## State of the System

**Battery:** F1-F24b (25 tests, FROZEN). Four tiers:
- A (Detection): F1, F3, F5, F6, F8, F10, F18
- B (Structure): F2, F4, F7, F9, F11-F14, F17, F21, F23
- C (Ensemble): F15, F16, F19, F20, F22
- D (Magnitude): F24 (variance decomposition), F24b (metric consistency + tail localization)

**Finding ontology:** LAW / CONSTRAINT / TENDENCY / INTERACTION
- LAW: eta² > 0.14, not tail-driven. Dominant organizing principle.
- CONSTRAINT: tail-driven. Boundary condition / rare configuration.
- TENDENCY: small eta², consistent. Background effect.
- INTERACTION: irreducible multi-axis structure (proposed, not yet formalized).

**Key scripts:**
- `battery_unified.py` — F1-F24b, LAW/CONSTRAINT/TENDENCY classification
- `battery_v2.py` — F15-F24b implementations
- `battery_logger.py` — structured JSONL audit trail
- `reaudit_20_findings.py` — 20-finding re-audit script
- `sg_decomposition.py` — space group component analysis
- `retest_all_findings.py` — original retest script (needs F24 update)

**Python:** `C:\Users\James\AppData\Local\Programs\Python\Python312\python.exe`

---

## The 7 Confirmed LAWS (eta² > 0.14)

| # | Finding | eta² | Dataset | Notes |
|---|---------|------|---------|-------|
| 1 | SC class → Tc | 0.570 | 3DSC | Strongest effect. Chemical family dominates. |
| 2 | SG → Tc | 0.457 (0.221 after controls) | 3DSC | Irreducible — no single component explains it. |
| 3 | SG → Cell volume | 0.394 | 3DSC | |
| 4 | N_elements → Tc | 0.329 (0.063 after SC class) | 3DSC | Mostly mediated by chemical family. |
| 5 | SG → Formation energy | 0.328 | 3DSC | |
| 6 | Crossing number → determinant | 0.219 | KnotInfo | Only non-superconductor LAW. |
| 7 | SG → Density | 0.190 | 3DSC | |

### The SG Decomposition Result (Critical)

After controlling for SC class + crystal system + n_elements:
- **Full space group still explains 22% of Tc variance**
- But NO single SG component reproduces it (point group → 2.3%, lattice → 2.8%, all others < 0.1%)
- **The signal is irreducible.** The full symmetry object carries information that its projections don't.

### The Layered Constraint Model

```
Tc ≈ f(chemical class, symmetry, complexity)
       ↑ domain          ↑ orthogonal      ↑ modulation
       η²=0.57           η²=0.22*          η²=0.06*
                          *independent      *independent
```

---

## Priority 0: DO NOT ADD MORE TESTS

The battery is complete for now. 25 tests across 4 axes. Further tweaks risk overfitting the instrument to the test cases. The next move is re-measurement, not refinement.

---

## Priority 1: Full Re-Audit of ALL Prior Results

Re-run every past finding through the frozen F1-F24b battery. The goal is not new discovery — it's **reclassification**. Watch for:

- **Pattern A (Collapsed discoveries):** Looked large via M4/M2², actually eta² < 0.05. These are amplification artifacts.
- **Pattern B (Hidden laws):** Looked ordinary, actually eta² > 0.14. These are what the pipeline's geometry of attention missed.
- **Pattern C (Representation illusions):** Fail F24b metric consistency. These are measurement artifacts.

### What to re-audit (in order):
1. All remaining findings from `challenge_run_20260411.md` (65+ challenges)
2. Charon's 23 known-truth rediscoveries (calibration check)
3. Previous genocide round results (R1-R5)
4. Everything in `findings_tiered_20260411.md`

### What to compute for each:
```
{
    "finding_id": "...",
    "claim": "...",
    "detection": "PASS/FAIL (Tier A)",
    "structure": "PASS/FAIL (Tier B)",
    "magnitude": "eta² value",
    "shape": "CONSISTENT / TAIL_DRIVEN / EXTREME_TAIL_DRIVEN",
    "type": "LAW / CONSTRAINT / TENDENCY / INTERACTION / NEGLIGIBLE"
}
```

---

## Priority 2: Dimensionality Analysis (Not a Test — a Lens)

The SG result shows an irreducible, high-dimensional constraint. Add a dimensionality analysis:

1. **Encode SG as a binary feature vector** (230 possible groups → one-hot, or encode by symmetry operations)
2. **PCA on SG encoding**: How many components needed to capture most of the SG → Tc variance?
3. **Mutual information decomposition**: Which SG features carry the most information about Tc?

If top 1-2 components capture most variance → reducible (and we missed the right decomposition).
If many components needed → irreducible structure (the current interpretation).

This is the "effective dimensionality of the signal" the council asked for.

---

## Priority 3: Investigate the 7 LAWS

After re-audit, go deeper on the confirmed LAWS:

1. **SC class → Tc (0.570):** Stratify within each SC class. Does SG → Tc survive within cuprates? Within iron-based? This tests whether the 3 axes are truly independent.
2. **SG → Tc (0.221 independent):** Replicate on SuperCon (Stanev) dataset. File at `physics/data/superconductors/3DSC/superconductors_3D/data/source/SuperCon/`.
3. **Crossing number → determinant (0.219):** Is this trivial (more crossings → bigger determinant) or structural? Check if the relationship is monotonic or if specific crossing numbers have anomalous determinant distributions.
4. **Search for LAWS in other domains:** OEIS, number fields, genus-2 curves. Use eta²-first search, not M4/M2².

---

## Methodology: The New Epistemology

### Four axes of measurement
1. **Reality** (Tier A): Is there signal?
2. **Robustness** (Tier B): Is it real, not confound?
3. **Description** (Tier C): What's the simplest model?
4. **Magnitude** (Tier D): How big? What shape?

### Four types of finding
1. **LAW:** eta² > 0.14, not tail-driven. Dominant.
2. **CONSTRAINT:** tail-driven. Boundary condition.
3. **TENDENCY:** small eta², consistent. Background.
4. **INTERACTION:** irreducible, multi-axis. (SG → Tc is the prototype.)

### Key lessons
- M4/M2² is a detector, not a ruler. Use it to find signals, measure with eta².
- Large n + tail-sensitive statistic = false confidence. Always check eta².
- The geometry of the measurement tool determines what you see.
- Over-calibrated skepticism is also a failure mode. eta²=0.05 can be real physics.

### Warning from the council
> "You are now in danger of over-calibrated skepticism. eta²=0.05 is 'small' but in physics can still be a real mechanism-level signal."

Don't dismiss CONSTRAINTS. They're real — just not dominant.

---

## Key Files

| File | Purpose |
|------|---------|
| `cartography/docs/what_we_learned_v2.md` | Honest state of knowledge (v3 content) |
| `cartography/docs/reaudit_20_results.md` | 20-finding re-audit with F24 |
| `cartography/docs/next_session_instructions.md` | This file |
| `roles/CrossDomainCartographer/journal_20260412.md` | Full session journal |
| `cartography/shared/scripts/battery_unified.py` | Frozen battery (F1-F24b) |
| `cartography/shared/scripts/sg_decomposition.py` | SG component analysis |
| `cartography/shared/scripts/reaudit_20_findings.py` | Re-audit script |
| `cartography/convergence/data/battery_logs/battery_runs.jsonl` | Audit trail |

---

*Written: 2026-04-12, end of Effect Geometry Session*
*Battery frozen at 25 tests. 4 tiers. 4 finding types.*
*7 LAWS found. SG → Tc is irreducible (22% after controls, no component reproduces it).*
*Next: re-audit everything. Then dimensionality analysis. Then replicate.*
