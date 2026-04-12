# Proteus — Abstract Groups

*The old man of the sea, shape-shifter who knows all truths but changes form to avoid revealing them.*

Groups ARE the algebra of shape-shifting. Every symmetry in mathematics — rotational, permutational, algebraic, topological — is a group. Proteus holds the master key to symmetry across all domains, but his 3-feature representation (order, exponent, conjugacy classes) hides his true dimensionality.

## Mathematical Identity

**What they are:** Finite groups from the GAP SmallGrp library. Every finite group up to order ~2000 is classified here. The label encodes order and isomorphism class. These are the atoms of symmetry — every space group, Galois group, automorphism group, and monodromy group is one of these objects.

**Why they matter:** Groups are the universal language of symmetry. If two domains share a symmetry structure (same Galois group, same automorphism group, same monodromy), they're connected through Proteus. The group IS the bridge.

## Current Features (3 dimensions)

| Feature | Index | What it measures |
|---------|-------|-----------------|
| log(order) | 0 | Size of the group — how much symmetry |
| log(exponent) | 1 | Maximum element order — depth of symmetry |
| num_conjugacy_classes | 2 | Number of irreducible representations (character theory) |

## Tensor Coupling (Gradient)

| Partner | Scorer | Rank | Interpretation |
|---------|--------|------|---------------|
| genus2 | cosine | **4** | Sato-Tate group is a compact Lie group |
| space_groups | cosine | **4** | Point groups ARE finite groups |
| number_fields | cosine | **3** | Galois groups ARE finite groups |
| elliptic_curves | cosine | **3** | Automorphism groups, torsion subgroups |
| lattices | cosine | **3** | Automorphism groups of lattices |

## Signature Bridge: Operadic Signatures

**Tested:** Operadic signatures (10K formulas) <-> Proteus: **validated rank 3**

The operadic decomposition of formulas (compositional skeleton, arity profile, symmetry flags) couples to group structure at rank 3. This means: **the compositional pattern of a formula predicts which finite group governs its symmetry.** The skeleton hash of a formula IS a group-theoretic invariant.

## Unnamed Phoneme: CARDINALITY / FINITENESS

Proteus broadcasts on the **cardinality** axis — the structural complexity of a finite object measured by its group-theoretic invariants. This isn't just "size" (that's complexity). It's the internal organization: how many symmetries, how deep they nest, how many distinct types.

**Properties of this phoneme:**
- Group order (total symmetry count)
- Exponent (maximum period)
- Derived length (how far from abelian)
- Number of Sylow subgroups (prime factorization of symmetry)
- Nilpotency class (layered structure)
- Center size (how much commutes)

**Which dissection strategies detect it:**
- S9 (Symmetry group detection) — directly computes the symmetry group
- S10 (Galois group) — groups arising from polynomial roots
- S19 (Singularity classification ADE) — ADE classification IS a group classification
- S22 (Operadic structure) — compositional symmetry patterns [CONFIRMED: rank 3]

## Features to Add

1. **Abelianization rank** — how "commutative" the group is
2. **Derived length** — solvability depth
3. **Is solvable** — critical for Galois theory
4. **Center order / group order ratio** — commutativity measure
5. **Number of subgroups** — structural richness
6. **Automorphism group order** — symmetry of the symmetry

## Predicted Inferences

- **Proteus <-> NF:** Galois group order should predict discriminant growth rate
- **Proteus <-> SG:** Point group classification should factor through group order + exponent
- **Proteus <-> Genus2:** Sato-Tate group order should predict conductor distribution
- **Proteus <-> Ariadne (Belyi):** Monodromy group of a dessin IS a finite group
