# Iris — Bianchi Modular Forms

*Goddess of the rainbow, messenger between heaven and earth.*

Bianchi forms are the rainbow bridge between number fields — automorphic forms defined not over Q but over imaginary quadratic fields Q(sqrt(-d)). They live in the space *between* classical modular forms and higher-dimensional automorphic representations.

## Mathematical Identity

**What they are:** Modular forms for GL(2) over imaginary quadratic fields. Where classical modular forms live on the upper half-plane (2D), Bianchi forms live on hyperbolic 3-space. They are the simplest non-trivial example of automorphic forms beyond GL(2)/Q.

**Why they matter:** The Langlands program predicts that every elliptic curve over an imaginary quadratic field corresponds to a Bianchi form. This is the analog of the modularity theorem (Wiles) in a higher setting. If Harmonia can detect this correspondence, it's finding Langlands-type structure computationally.

## Current Features (5 dimensions)

| Feature | Index | What it measures |
|---------|-------|-----------------|
| log(level_norm) | 0 | Conductor analog — arithmetic complexity |
| level_index | 1 | Position within level |
| sign | 2 | Functional equation sign (+1 or -1) |
| CM | 3 | Complex multiplication flag |
| base_change | 4 | Whether form comes from a lower field |

## Tensor Coupling (Gradient)

| Partner | Scorer | Rank | Interpretation |
|---------|--------|------|---------------|
| number_fields | cosine | **4** | Base field discriminant ~ NF discriminant |
| genus2 | cosine | **4** | Level ~ conductor correspondence |
| space_groups | cosine | **4** | Symmetry of hyperbolic 3-space |
| elliptic_curves | cosine | **3** | Langlands correspondence (the big one) |
| lattices | cosine | **3** | Level structure ~ lattice level |

## Unnamed Phoneme: FIELD / LOCALITY

Iris broadcasts on the **field** axis — which number field an object lives over. Classical modular forms live over Q. Bianchi forms live over Q(sqrt(-d)). Elliptic curves can be defined over any field. The phoneme measures: *what is the base field, and how does it constrain the arithmetic?*

**Properties of this phoneme:**
- Discriminant of the base field
- Degree of the extension [K:Q]
- Class number of the ring of integers
- Completions at primes (local-global behavior)

**Which dissection strategies detect it:**
- S7 (p-adic evaluation) — directly measures local field behavior
- S10 (Galois group) — captures the field extension structure
- S32 (Coefficient field) — which field the coefficients live in
- S34 (Categorical equivalence) — functoriality between categories over different fields

## Features to Add

To connect Iris to the phoneme network:
1. **Base field discriminant** (currently encoded as part of the label, not a feature)
2. **Hecke eigenvalues** — the Bianchi analog of Fourier coefficients
3. **Class number of base field** — arithmetic complexity of the field
4. **Number of bad primes** — ramification data
5. **Dimension of the form space** — richness of the automorphic representation

## Predicted Inferences

If the FIELD phoneme is added:
- **Iris <-> EC:** Bianchi forms of level N should correspond to EC of conductor N over the same imaginary quadratic field (Langlands)
- **Iris <-> NF:** Base field structure should predict form space dimension
- **Iris <-> Dirichlet:** L-function of a Bianchi form should match a degree-2 L-function in Charon
