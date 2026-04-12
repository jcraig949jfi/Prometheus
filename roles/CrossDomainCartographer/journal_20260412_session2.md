# Journal — 2026-04-12, Session 2
## From Re-Audit to Interaction Discovery

### The arc

Started with three tasks: re-audit all findings through F24, analyze SG dimensionality, stress-test the 7 LAWs. Ended with a fundamental reclassification of what "law" means in this project.

### Phase 1: Re-audit confirmed F24 works

Ran `reaudit_20_findings.py` — all 20 findings reproduced cleanly. 7 LAWs, 3 CONSTRAINTS, 6 TENDENCIES, 4 NEGLIGIBLE. SC_class → Tc (eta²=0.570) confirmed as strongest finding. The pipeline's M4/M2² detection bias confirmed: it systematically overvalued tail-driven effects and undervalued bulk effects.

### Phase 2: Independence analysis

Built `law_independence.py`. Found 3 independent axes controlling Tc:
- SC_class (57%), SG (14% independent after SC_class), N_elements (1.8% after both)
- Total model R²=0.73. Continuous properties (volume, density, formation energy) add <1% after the categorical axes.
- The continuous properties are *consequences* of the categorical structure.

### Phase 3: SG dimensionality — IRREDUCIBLE

Built `sg_dimensionality.py`. After residualizing Tc by SC_class + crystal_system + N_elements:
- Pure SG signal: R²=0.232
- PCs for 90% of signal: 27
- Participation ratio: 7.3
- **Later corrected**: Global irreducibility was an artifact of mixing families with different mappings. Within families, dimensionality ranges from 1 (Chevrel, trivial) to 11 (cuprates, genuinely irreducible).

### Phase 4: SG decomposition (from user's earlier work)

The user had already run the SG decomposition. Key result: after removing SC_class + crystal_system + N_elements, full SG still explains 22% of Tc variance. But no single SG component (point group, lattice type, rotation order, inversion, symmorphic) reproduces it. Point group drops to 2.3%, lattice type to 2.8%. The whole is more than the sum of its parts.

### Phase 5: Replication — the interaction discovery

Built `stanev_replication.py` with 5 strategies:
- **Strategy A** (Stanev cross-match): Inconclusive — formula format incompatible
- **Strategy B** (Leave-one-SC-class-out): **ALL OOS R² NEGATIVE** (-1 to -164)
- **Strategy C** (Permutation null): z=130.5, 23x above null. Real signal.
- **Strategy D** (Incremental): SG adds +14.1% after SC_class
- **Strategy E** (Subsample): CV=3.2%, stable

**The critical finding**: SG → Tc is real (z=130 vs null) but the mapping is class-specific. P4/mmm = 80.9K in cuprates, 2.3K in heavy fermions. Same SG, 35x different Tc. This is not failure — it's interaction dominance.

### Phase 6: Interaction analysis

Built `interaction_analysis.py`. Four priorities:

**Priority 1 — Rank consistency**: Mean Spearman rho = -0.041 across class pairs. SG rankings are completely independent across families. Two pairs show inversion (rho = -1.0). Pure interaction.

**Priority 2 — Variance decomposition**:
- SC_class main: 57.0%
- SG main (after SC): 14.1%
- SC_class × SG interaction: 8.5%
- Residual: 20.4%
- Interaction ratio: 38% of SG-related variance is interaction

**Priority 3 — Within-class PCA**: Irreducibility is LOCAL:
- Chevrel: 1 PC (reducible)
- Heavy fermion/Ferrite/Other: 5-6 PCs (partially reducible)
- Cuprate/Oxide: 9-11 PCs (genuinely irreducible)

**Priority 4 — Distribution bias**: 38% of SGs have >90% members in one class. Mean normalized entropy = 0.245. Highly skewed. Part of global eta² is compositional bias.

### Phase 7: Stress tests

**Constraint stress test** (`stress_test_constraints.py`):
- ST → conductor: Log-normal replay z=24.9 — NOT distributional artifact. Strengthens under log (eta²=0.031). REAL CONSTRAINT confirmed.
- ST → discriminant: z=2.7 vs log-normal. MARGINAL.
- ST → exponent structure: eta²=0.110, CONSISTENT (not tail-driven). Within/between CV ratio = 1.28. CONSTRAINT confirmed, upgraded from 0.05.

**Tautology test** (`stress_test_tautology.py`):
- max Jones ~ determinant: R²=0.995. NEAR-IDENTITY. Removed from LAW list.
- Jones length ~ crossing: KNOWN THEOREM (Kauffman-Murasugi-Thistlethwaite).
- EC count ~ MF count: MODULARITY THEOREM (Wiles 1995). EC ≤ MF at 97.9%.
- **All three non-superconductor "LAWs" are identities/rediscoveries. Zero novel LAWs outside superconductors.**

**Interaction classification** (`stress_test_interaction.py`):
- Initially classified everything as "CONTEXT_LOCKED"
- User corrected: negative OOS R² is expected for interaction-dominated systems
- The correct classification is CONDITIONAL LAW, not failure

### Phase 8: Final classification

Built `final_classification.py`. The empirical hierarchy:

| Level | Type | Count | Examples |
|-------|------|-------|----------|
| 1 | IDENTITIES | 4+ | Modularity, KMT, near-identities |
| 2 | UNIVERSAL LAWS | **0** | None found across 21 datasets |
| 3 | CONDITIONAL LAWS | **3** | SC_class→Tc, (SG×SC_class)→Tc, N_elements→Tc |
| 4 | CONSTRAINTS | **2** | ST→conductor, endomorphism→uniformity |
| 5 | MARGINAL | **1** | ST→discriminant |

Plus 1 EXACT IDENTITY: E_6 forces root number = +1.

### The meta-finding

**Most real-world "laws" are conditional mappings, not universal ones.** P(Y|X) ≠ P(Y|X, new context). The battery can now detect, quantify, and classify them. The absence of universal laws across 21 datasets is itself informative.

### Scripts produced this session

| Script | Purpose |
|--------|---------|
| `reaudit_20_findings.py` | 20-finding re-audit with F24+F24b (existed, re-ran) |
| `law_independence.py` | Partial eta², sequential decomposition, axis counting |
| `sg_dimensionality.py` | PCA on SG encoding, participation ratio, effective dimensionality |
| `law_deep_analysis.py` | Within-class SG→Tc, knot triviality check, CV |
| `stanev_replication.py` | 5-strategy replication (Stanev, leave-one-class-out, permutation, incremental, subsample) |
| `interaction_analysis.py` | Interaction surface, rank correlation, variance decomposition, within-class PCA, distribution bias |
| `reaudit_genocide_f24.py` | All genocide survivors through F24 |
| `stress_test_constraints.py` | F24+F22+F19 on CONSTRAINT findings |
| `stress_test_tautology.py` | Tautology/identity detection for too-strong laws |
| `stress_test_interaction.py` | Interaction classification for all categorical findings |
| `final_classification.py` | Complete finding hierarchy and instrument summary |

### The deepest lesson

The instrument's biggest failure mode was not false positives or false negatives. It was **misclassification of interaction as universality**. A conditional law looks like a universal law if you never test cross-context transfer. The leave-one-group-out test exposed this permanently. The correction: conditional laws are not failed universal laws — they are the dominant type of real-world structure, and they require interaction decomposition to characterize properly.

---

*3 Conditional Laws. 2 Constraints. 1 Exact Identity. 1 Marginal. 0 Universal Laws.*
*The strongest finding (SC_class → Tc, eta²=0.570) is conditional on structure.*
*The deepest finding (SG × SC_class → Tc) is an interaction, not a main effect.*
*Most scientific "laws" are conditional mappings. The instrument now knows this.*
*April 12, 2026, Session 2*
