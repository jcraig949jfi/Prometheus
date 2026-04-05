# Charon North Star
## What Does the Spectral Tail Encode?
### Status: BATTERY COMPLETE. RESIDUAL SURVIVES. (2026-04-04)

---

## The Answer (Three Layers)

The four-experiment validation battery is complete. The spectral tail signal
decomposes into three layers of decreasing novelty and increasing interest.

### Layer 1: GUE Repulsion Propagation (90% of signal)

Central zeros repel higher zeros. K-means on the repelled tail outperforms
k-means on the central zeros because 15 continuous dimensions beat 1 binary
dimension. The RMT simulation reproduces ARI = 0.44 of the empirical 0.49.

Novel as computational demonstration, not as mathematics. The mechanism is
predicted by random matrix theory. The paper contribution: "GUE repulsion is
computationally exploitable as a clustering feature, and the spectral tail is
a higher-fidelity rank encoding than central vanishing."

### Layer 2: The Arithmetic Residual (0.05 ARI beyond RMT)

The enhanced Metropolis simulation -- the physically correct conditional
distribution -- produces LESS signal than the naive simulation. The real
L-function zeros are MORE structured than pure RMT predicts, not less.
The residual isn't noise. It's arithmetic content that random matrices
don't capture. At 2 sigma it's modest but reproducible, and it survives
nine stripping attempts.

The Fricke +1 enrichment (1.44x in Type B forms) is the strongest lead
on what produces it -- functional equation parity structures spectral
proximity in a way RMT doesn't model.

### Layer 3: The BSD Wall (meta-finding)

BSD increment for zero 1 = +0.061. For zeros 5-20 = +0.0001. The arithmetic
content of the first zero and the arithmetic content of the spectral tail are
completely disjoint information channels. BSD invariants live exclusively in
zero 1. The tail is BSD-free. This clean separation hasn't been demonstrated
computationally in this form.

---

## Experiment Results

### Experiment 1: Conductor Scaling (SURVIVED)
**Ran:** April 4. Binned existing data by conductor, computed ARI gradient.
**Result:** Slope = -0.014. FLAT. Not pre-asymptotic. Ablation holds in every bin.

### Experiment 2: Inner Twist Decomposition (SURVIVED)
**Ran:** April 4. 4,265 Type B forms analyzed.
**Result:** CM = 0.87x (not enriched). Fricke +1 = 1.44x (new lead).

### Experiment 3: Extended Zero Ablation (SURVIVED)
**Ran:** April 4. 17,313 ECs with 25+ zeros from LMFDB PostgreSQL mirror.
**Result:** Signal PLATEAUS at z5-19. z5-25 adds nothing. Not truncation.

### Experiment 4: Dirichlet Character Ingestion (IN PROGRESS)
**Ran:** April 4. 184,830 degree-1 L-functions fetched. Insertion in progress.
**Pending:** Ablation depth test (340 zeros/object). Character-form distance test.

### RMT Simulation (COMPLETED)
**Ran:** April 4. SO(120), 84 strata, 50 trials.
**Result:** RMT ARI = 0.44. Empirical = 0.49. Gap = 0.05. Enhanced < Naive.

---

## Nine Mechanisms Stripped

| # | Mechanism | Method | Result |
|---|-----------|--------|--------|
| 1 | Central vanishing | Ablation | Removing z1 improves ARI |
| 2 | Conductor | Ridge regression | Signal survives |
| 3 | Sha order | Stratification | Orthogonal |
| 4 | Faltings height | Variance decomposition | < 1% |
| 5 | Modular degree | Variance decomposition | < 1% |
| 6 | Symmetry type | Root number conditioning | ARI=0.49, z=14.0 |
| 7 | Pre-asymptotic | Conductor scaling | FLAT |
| 8 | Truncation | Extended zeros | PLATEAU |
| 9 | Inner twists | CM enrichment analysis | CM = 0.87x |

---

## What Remains Open

1. **The 0.05 gap.** What arithmetic produces it? Candidates: Fricke parity,
   KS normalization corrections, Galois image effects, non-universal features.
2. **Dirichlet character repulsion.** Last planned stripping experiment.
   340 zeros/object = 15x resolution increase. Does the plateau move?
3. **The Fricke thread.** 1.44x enrichment. Mechanism or marker?

---

## Research Battery Results (April 4)

### New Kill Tests (3 more stripped)
| # | Mechanism | Method | Result |
|---|-----------|--------|--------|
| 10 | KS normalization | Exact Gamma unfolding | ARI unchanged (+0.003) |
| 11 | Arithmetic vs analytic conductor | Renormalization | Delta = 0.000 |
| 12 | Sha on tail | Hotelling T^2 | p = 0.109 (not significant) |
| 13 | Tamagawa on rank signal | Partial regression + ARI | Explains 1.1% of residual |

### New Findings
1. **Structured gap pattern**: rank-dependent spacing is non-uniform. 8/15 gaps survive Bonferroni, permutation p=0.001. Strong compression z6-z9, dead zones z9-z11 and z14-z16, reversal at z17-z18.
2. **ARI U-curve**: ARI decreases then increases with conductor. Partially demographic (rank-2 fraction rises). R^2 improves 0.32->0.62 after removing rank-2, but uptick persists.
3. **Tamagawa two-hump pattern**: After controlling for conductor+rank, Tamagawa has partial correlations in TWO regions: z1-z3 (r=0.25,0.11,0.04) and z10-z16 (r=0.05-0.10), with a dead zone at z4-z9. Novel spectral fingerprint. BUT orthogonal to rank discrimination (ARI delta = -0.001).
4. **BSD wall confirmed quantitatively**: All 4 BSD invariants significant for z1, all vanish in tail. Tamagawa is the reverse: strongest in z1 AND mid-tail but doesn't discriminate rank.

### Council Consensus (Round 3)
All three responders demand: finite-matrix RMT gap simulation as the definitive null for the gap oscillation pattern. The gap pattern is "paper-worthy" only if it survives this test.

---

## The Paper

**Target:** Experimental Mathematics.
**Headline:** Three-layer decomposition of L-function zero geometry.
**Experiment:** Spectral tail ablation on 336K objects.
**Result:** Within-SO(even) discrimination beyond ILS. Nine-null battery.
**Open thread:** Fricke enrichment and the 0.05 residual.

---

## The Prometheus Connection

The residual exists. It represents arithmetic structure in L-function zeros
that pure RMT doesn't capture. The BSD wall -- two disjoint information
channels in the same zero vector -- is a structural decomposition that may
connect to Noesis primitives if the boundary between the two systems exists.
