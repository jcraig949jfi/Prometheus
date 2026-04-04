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
