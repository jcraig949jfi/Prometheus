# Mnemosyne — OEIS Sequences

*Titaness of memory, mother of the nine Muses.*

OEIS is the memory of mathematical pattern — 392,000 integer sequences that encode the generative structure of combinatorics, number theory, algebra, and physics. Every recurrence, every growth law, every counting function lives here. Mnemosyne remembers what other domains compute.

## Mathematical Identity

**What they are:** Integer sequences from the On-Line Encyclopedia of Integer Sequences. Each is a function N -> Z with an associated generating rule, formula, or recurrence. The first ~50 terms of each sequence are stored.

**Why they matter:** OEIS is the Rosetta Stone. A sequence appearing in two different mathematical contexts IS a cross-domain bridge. The partition function p(n) connects combinatorics to modular forms. The Bernoulli numbers connect number theory to topology. If Mnemosyne's growth signatures match another domain's spectral signatures, we've found a formula-level bridge.

## Current Features (7 dimensions)

| Feature | Index | What it measures |
|---------|-------|-----------------|
| log(mean_value) | 0 | Typical magnitude |
| log(max_value) | 1 | Range |
| growth | 2 | log(max) - log(first nonzero) — exponential vs polynomial |
| monotonicity | 3 | Fraction of increasing consecutive pairs |
| zero_fraction | 4 | Proportion of zeros |
| negative_fraction | 5 | Proportion of negatives |
| n_terms | 6 | How many terms available |

## Tensor Coupling (Gradient)

| Partner | Scorer | Rank | Interpretation |
|---------|--------|------|---------------|
| elliptic_curves | cosine | **4** | Growth rates match conductor distributions |
| lattices | cosine | **4** | Theta series ARE integer sequences |
| number_fields | cosine | **3** | Discriminant sequences are OEIS entries |
| space_groups | cosine | **3** | Counting sequences by crystal system |
| materials | cosine | **3** | Materials property distributions as sequences |

## Unnamed Phoneme: GROWTH / ASYMPTOTICS

Mnemosyne broadcasts on the **growth** axis — how fast a sequence grows, and what that growth law reveals about the underlying generative structure. Polynomial growth = counting finite objects. Exponential growth = combinatorial explosion. Subexponential = partition-type structure. The growth class IS the mathematical identity.

**Properties of this phoneme:**
- Growth rate (polynomial degree, exponential base, or subexponential class)
- Recurrence depth (order of the minimal recurrence relation)
- Modular periodicity (behavior of a(n) mod p for small primes)
- Autocorrelation structure (spectral signature of the sequence)
- Superseeker classification (OEIS's own similarity metric)

**Which dissection strategies detect it:**
- S5 (Fourier/spectral) — power spectrum of the sequence IS the growth signature
- S6 (Phase space/attractors) — recurrence iteration gives attractor geometry
- S24 (Information-theoretic) — compression ratio measures growth complexity
- S27 (Arithmetic dynamics) — orbit structure over finite fields
- S33 (Recursion operator) — the recurrence itself is an algebraic invariant

## Pre-Computed Signatures Available

From the convergence data directory, these are ALREADY computed and can be loaded:
- `spectral_signatures.jsonl` (33 MB, 50K records) — FFT spectra of sequences
- `arithmetic_dynamics_signatures.jsonl` (11 MB, 50K) — Lyapunov exponents, phase portraits
- `info_theoretic_signatures.jsonl` (16 MB, 100K) — entropy, compression
- `recursion_operator_signatures.jsonl` (7.8 MB) — recurrence operators
- `oeis_crossrefs.jsonl` (63 MB) — cross-reference network
- `oeis_programs.jsonl` (70 MB) — generating functions and recurrences
- `spectral_clusters.jsonl` (61 KB) — 40 spectral cluster groups

## Features to Add

To connect Mnemosyne to the phoneme network:
1. **Spectral centroid** from FFT — median frequency of the power spectrum
2. **Recurrence order** — depth of the minimal linear recurrence
3. **Modular fingerprint** — a(n) mod 2, 3, 5, 7 pattern vector
4. **First-difference growth** — growth rate of a(n+1) - a(n)
5. **p-adic valuation sequence** — v_p(a(n)) for p = 2, 3, 5

## Predicted Inferences

If the GROWTH phoneme is added:
- **Mnemosyne <-> EC:** EC rank distribution sequences should match OEIS growth classes
- **Mnemosyne <-> Lattices:** Theta series of lattices are OEIS sequences — direct identification
- **Mnemosyne <-> Maass:** Hecke eigenvalue sequences should have matching spectral signatures
- **Mnemosyne <-> Fungrim:** Formulas defining OEIS sequences create formula-level bridges
