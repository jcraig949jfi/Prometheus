# Ariadne — Belyi Maps

*She gave Theseus the thread to navigate the labyrinth.*

Belyi maps are the thread connecting three mathematical worlds that otherwise seem unrelated: algebraic geometry (curves), topology (surfaces with drawn graphs), and number theory (the absolute Galois group Gal(Q-bar/Q)). Grothendieck called them "dessins d'enfants" — children's drawings — because they look simple but encode the deepest structure in mathematics.

## Mathematical Identity

**What they are:** A Belyi map is a holomorphic map from a Riemann surface to the Riemann sphere, ramified only over {0, 1, infinity}. Belyi's theorem says every algebraic curve defined over Q-bar admits such a map. The preimage of [0,1] is a graph on the surface — the dessin.

**Why they matter:** Grothendieck's insight: the absolute Galois group Gal(Q-bar/Q) acts faithfully on dessins. This means the most mysterious object in number theory (the absolute Galois group) can be studied through combinatorial drawings on surfaces. Ariadne IS the bridge between arithmetic and geometry.

## Current Features (3 dimensions)

| Feature | Index | What it measures |
|---------|-------|-----------------|
| degree | 0 | Number of sheets — complexity of the covering |
| genus | 1 | Topological genus of the surface |
| orbit_size | 2 | Size of the Galois orbit — arithmetic richness |

## Tensor Coupling (Gradient)

| Partner | Scorer | Rank | Interpretation |
|---------|--------|------|---------------|
| number_fields | cosine | **3** | Galois orbits ~ field extensions |
| elliptic_curves | cosine | **3** | Genus 1 Belyi maps ARE elliptic curves |
| genus2 | cosine | **3** | Genus 2 Belyi maps ARE genus-2 curves |
| space_groups | cosine | **3** | Ramification type ~ symmetry structure |
| number_fields | alignment | **3** | Field of definition aligns with NF discriminants |

## Unnamed Phoneme: RAMIFICATION / TOPOLOGY

Ariadne broadcasts on the **ramification** axis — how a covering space branches over singular points. This is a fundamentally topological invariant that has no analog in the current 5 phonemes. Ramification type encodes:

**Properties of this phoneme:**
- Ramification type (partition triple [a, b, c] over 0, 1, infinity)
- Genus (topological genus of the covering surface)
- Monodromy group (the permutation group of the sheets)
- Number of automorphisms of the dessin
- Belyi height (arithmetic complexity of the map coefficients)

**Which dissection strategies detect it:**
- S4 (Topological signatures) — genus, Euler characteristic, Betti numbers
- S11 (Monodromy) — THE defining invariant of a Belyi map
- S12 (Zeta function of variety) — point counts of the curve over finite fields
- S19 (Singularity classification) — ramification IS singularity data
- S34 (Categorical equivalence) — the functor from dessins to Galois representations

## Features to Add

To connect Ariadne to the phoneme network:
1. **Ramification partition** — the triple (a, b, c) as feature vector
2. **Monodromy group order** — links directly to Proteus
3. **Passport size** — number of dessins with the same ramification type
4. **Base field degree** — links to Iris (FIELD phoneme)
5. **ABC triple** — the a+b=c values from the ramification
6. **Is Galois** — whether the covering is Galois (regular dessin)

## Predicted Inferences

If the RAMIFICATION phoneme is added:
- **Ariadne <-> Genus2:** Genus-2 Belyi maps should have conductor proportional to degree x discriminant
- **Ariadne <-> Proteus:** Monodromy group of each dessin IS a finite group in the SmallGrp library
- **Ariadne <-> Iris:** Bianchi forms over the field of definition of a Belyi map should have matching level
- **Ariadne <-> NF:** Galois orbit size should predict field discriminant
