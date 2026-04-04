# Charon Roadmap
## Last Updated: 2026-04-04

---

## Status: Publishable Finding (Earned)

Four-day sprint. 336K objects. Nine mechanisms stripped. The spectral tail signal
decomposes into three layers: GUE repulsion (90%), arithmetic residual (10%),
and the BSD wall. The core finding is stable. Paper target: Experimental Mathematics.

### What's Proven
- Zero vectors create continuous rank-aware geometry (ARI = 0.55, independent of conductor)
- The spectral tail (zeros 5-19) is a higher-fidelity rank encoding than central vanishing
- GUE repulsion explains 90% of the within-SO(even) signal (RMT simulation)
- A 0.05 ARI residual beyond RMT survives nine stripping attempts
- The BSD wall: zero 1 and zeros 5-20 are completely disjoint information channels
- Signal plateaus at z5-19 (not truncation-limited, confirmed with 25+ zeros)
- Signal is flat across conductor (not pre-asymptotic)
- Inner twist / CM structure is NOT the mechanism (CM = 0.87x)
- Fricke +1 enrichment (1.44x) in Type B forms is a new structural lead

### What's Open
- What arithmetic mechanism produces the 0.05 gap beyond RMT?
- Does Fricke eigenvalue parity drive spectral proximity or just mark it?
- Does the ablation plateau shift with 340 zeros (Dirichlet characters)?
- Does character-form zero distance predict landscape position?
- Does the 0.05 gap shrink at conductor > 5000?

---

## Immediate Priority: Paper Preparation

### 1. Dirichlet Character Analysis (IN PROGRESS)
- 184,830 L-functions ingested, insertion completing
- Two tests: ablation depth with 340 zeros, character-form distance
- Last planned stripping experiment

### 2. Council Prompt Fire
- Updated prompt ready: `charon/docs/council_prompt_april4_update.md`
- Presents all four experimental results to hostile reviewers
- Asks five targeted questions about the surviving residual

### 3. Fricke +1 Deep Dive
- Why is functional equation parity enriched 1.44x in Type B forms?
- Does Fricke +1 predict spectral proximity directly, or is it correlated
  with something else that drives it?

### 4. Paper Draft
- Three-layer structure is the narrative
- Nine-null battery is the methodology
- Spectral tail ablation is the experiment
- Within-SO(even) discrimination is the result beyond ILS

---

## Expansion Priority (Post-Paper)

### 1. Conductor > 5000 Extension
- Test whether the 0.05 RMT gap shrinks at higher conductor
- If it shrinks: finite-conductor correction (interesting but explained)
- If it persists: structural (the finding deepens)

### 2. Number Fields
- Dedekind zeta zeros. Tests whether zeros encode class number like rank.
- New graph edge types (field extensions, Galois containment)

### 3. Artin Representations
- Galois side of Langlands. Bridges to modular forms via Artin conjecture.
- Highest complexity, highest payoff.

---

## Sprint Ledger (April 1-4)

| Day | Objects | Kills | Key Result |
|-----|---------|-------|------------|
| Apr 1 | 133,223 | 0 | First crossing. Architecture validated. |
| Apr 2 | +1,252 | 3 | Spectral tail finding. BSD wall. |
| Apr 3 | +0 | 3 | RMT hypothesis. Root number test. z=14.0. |
| Apr 4 | +202,143 | 3 | RMT simulation. Validation battery. Residual holds. |
| **Total** | **~336K** | **9** | **Three-layer decomposition. Paper-ready.** |

---

## Kill Test Results (Cumulative)

### Nine Mechanisms Stripped
| # | Mechanism | Method | Outcome |
|---|-----------|--------|---------|
| 1 | Central vanishing | Ablation | Removing z1 improves ARI |
| 2 | Conductor | Ridge regression | Signal survives |
| 3 | Sha order | Stratification | Orthogonal |
| 4 | Faltings height | Variance decomposition | < 1% |
| 5 | Modular degree | Variance decomposition | < 1% |
| 6 | Symmetry type | Root number conditioning | ARI=0.49, z=14.0 |
| 7 | Pre-asymptotic | Conductor scaling | FLAT (slope=-0.014) |
| 8 | Truncation | Extended zeros (25+) | PLATEAU at z5-19 |
| 9 | Inner twists | CM enrichment | CM=0.87x (depleted) |

### The 163 / Type B Forms
| Test | Result | Implication |
|------|--------|-------------|
| Kill Test 1: dim-2 sufficient? | SURVIVED (10.7%) | Real subset, not generic |
| Kill Test 2: character driver? | PARTIAL KILL (3.3x) | Amplifies but doesn't explain |
| Kill Test 3: inner twist driver? | SURVIVED (CM=0.87x) | NOT the mechanism |
| Fricke enrichment | NEW LEAD (1.44x) | Functional equation parity |

---

## Principles (Unchanged)

1. The fare is tokens. Spend them on crossings, not sightseeing.
2. Known bridges are the calibration set.
3. Schema emerges from data.
4. Classify every failure.
5. The landscape is not the territory.
6. Don't pollute the stream.
7. Fail fast, loop tight.
8. Do NOT overclaim. The data says what the data says. Nothing more.
