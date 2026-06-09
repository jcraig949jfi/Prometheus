# Battery Architecture v3
## F1-F22: Three-Tier Falsification + Inference System
## 2026-04-11

---

## The Question Each Tier Answers

**Tier A (Detection):** Is there a signal?
**Tier B (Structure):** Is the signal real, or a confound?
**Tier C (Ensemble/Representation):** What is the simplest correct description?

---

## Complete Battery

### Tier A — Statistical Detection
| Test | What it does | Key threshold |
|------|-------------|---------------|
| F1 | Permutation null | p < 0.05 |
| F3 | Effect size gate | d > 0.2 or r > 0.1 |
| F5 | Normalization sensitivity | Sign preserved across transforms |
| F6 | Base rate / Bonferroni | Survives multiple comparison |
| F8 | Direction consistency | Same sign in all subgroups |
| F10 | Outlier sensitivity | < 50% change after trimming 5% |
| F18 | Subset stability | CV ratio < 1.5× expected (context-aware) |

### Tier B — Structural Validation
| Test | What it does | What it catches |
|------|-------------|-----------------|
| F2 | Subset stability (signs) | Noise-driven sign flips |
| F4 | Confound sweep | Identified lurking variables |
| F7 | Monotonic dose-response | Non-monotonic artifacts |
| F9 | Simpler explanation | Overcomplicated models |
| F11 | Cross-validation | Overfitting |
| F12 | Partial correlation | Known confounds |
| F13 | Growth rate filter | Polynomial growth masking |
| F14 | Phase shift test | Periodic/lag confounds (NOT monotone trends) |
| F17 | Confound sensitivity sweep | Hidden confounds across strata |
| F21 | Trend robustness | Shared monotone trends (time-series confounds) |

### Tier C — Ensemble / Representation
| Test | What it does | What it reveals |
|------|-------------|-----------------|
| F15 | Log-normal calibration | Whether moments are explained by log-normality |
| F16 | Equivalence test (TOST) | Whether a value matches a prediction at given precision |
| F19 | Generative replay | Whether a proposed ensemble reproduces the data |
| F20 | Representation invariance | Whether a statistic depends on representation |
| F22 | Representation alignment | Which representation makes the system simplest |

---

## Acceptance Rules

1. **At least one Tier A test must pass** for the signal to be considered real
2. **At least one Tier B test must pass** for the signal to be accepted (not confound)
3. **Tier C tests are diagnostic, not gates** — they inform interpretation, not acceptance

---

## Calibration Notes (from stress tests)

- **F18:** Context-aware CV ratio, not fixed threshold. Compares observed CV to bootstrap-expected CV.
- **F14:** Works on periodic/lag signals. FAILS on monotone trends. Use F21 for trends.
- **F20:** Strong signals can mask representation dependence. Use F22 for representation selection.
- **F19:** z-score is primary, KS is secondary. KS on single synthetic sample is noisy.
- **F22:** The representation with simplest residuals (most normal, most homoscedastic) is the natural one. Guard against Gaussianization traps with a transformation complexity penalty.

---

## The Philosophical Shift

**Before this session:** "What are the constants?"
**After this session:** "What is the simplest structure that generates this data?"

The battery no longer just kills hypotheses. It infers the correct description.

- F1-F18 kill artifacts
- F19 tests generative models
- F20 detects representation dependence
- F21 catches trend confounds
- F22 selects the natural representation

**"Given a dataset, the instrument identifies whether a signal exists, whether it is structurally valid, and the representation under which it is most naturally expressed."**

---

## Known Limitations

1. F14 fails on monotone trends (mitigated by F21)
2. F18 old threshold (CV < 0.05) kills weak-but-real signals (fixed: context-aware)
3. F19 KS component is noisy on single samples (mitigated: z-score primary)
4. F20 misses representation dependence when correlation is strong (mitigated by F22)
5. F22 susceptible to Gaussianization traps (TODO: add complexity penalty)
6. No test for database version stability (F20-style across data versions — deferred)
7. No automated confound DISCOVERY (F17 requires manual candidate list)

---

*Architecture v3: 2026-04-11*
*22 tests across 3 tiers*
*Born from: 94 challenges, 5 stress tests, frontier model review*
*Implementation: battery_v2.py in cartography/shared/scripts/*
