# The Decaphony — Ten Coordinates of Mathematical Structure

*δεκαφωνία — ten voices*

Every mathematical object, across every domain, broadcasts on a subset of ten fundamental axes. These are the phonemes of mathematics — the articulatory features that generate all mathematical structure, the way place, manner, and voicing generate all human speech.

The first five were discovered through the connected core of 14 domains. The second five were revealed by the islands — domains that spoke on frequencies the original five couldn't hear.

---

## The Ten Phonemes

### The Original Five (discovered from the connected core)

| # | Greek Name | English | What it measures | Symbol |
|---|-----------|---------|-----------------|--------|
| 1 | **Megethos** (μέγεθος) | Magnitude | Conductor, discriminant, level, determinant — how "large" the object is in its natural metric | M |
| 2 | **Bathos** (βάθος) | Depth | Rank, degree, dimension — how "rich" or "deep" the structure is | B |
| 3 | **Symmetria** (συμμετρία) | Symmetry | Point group order, automorphism order — the size of the symmetry group | S |
| 4 | **Arithmos** (ἀριθμός) | Number | Torsion, class number, Selmer rank — arithmetic complexity, the discrete invariants | A |
| 5 | **Phasma** (φάσμα) | Spectrum | Spectral parameter, eigenvalues, zero spacings — the analytic fingerprint | P |

### The Island Five (revealed by the unnamed phonemes)

| # | Greek Name | English | What it measures | Revealed by | Symbol |
|---|-----------|---------|-----------------|-------------|--------|
| 6 | **Topos** (τόπος) | Place | Base field, localization, completion — where the object lives | Iris (Bianchi) | T |
| 7 | **Taxis** (τάξις) | Order | Group order, exponent, derived length — internal organization of finite structure | Proteus (Groups) | X |
| 8 | **Klados** (κλάδος) | Branch | Ramification type, monodromy, covering degree — how maps branch over singularities | Ariadne (Belyi) | K |
| 9 | **Auxesis** (αὔξησις) | Growth | Growth rate, recurrence depth, periodicity — the generative law of a sequence | Mnemosyne (OEIS) | U |
| 10 | **Kampyle** (καμπύλη) | Curve | Local curvature, embedding geometry, cluster structure — the shape of the landscape | Thalassa (Landscape) | C |

---

## The Phoneme Signature

Every mathematical object has a 10-letter signature: **M B S A P T X K U C**

Each letter is a real number (the object's coordinate on that axis). Objects with similar signatures are structurally related, even if they come from completely different domains.

```
Elliptic curve 11.a1:     M=2.5  B=0.0  S=·    A=1.0  P=2.65  T=·    X=·    K=·    U=·    C=·
Modular form 11.2.a.a:    M=2.4  B=·    S=1.2  A=·    P=2.0   T=·    X=·    K=·    U=·    C=·
                           ↑ same                        ↑ similar
                           Megethos matches              Phasma correlates
                           (conductor = level)           (zeros align)
                           = MODULARITY THEOREM
```

The dots (·) mean the domain doesn't project onto that phoneme. When two objects from different domains share values on the phonemes they both project to, that's a cross-domain bridge.

---

## The Complete Naming System

### The Project
- **Prometheus** — the fire-bringer. The project itself.

### The Infrastructure
- **Charon** — the ferryman. Data pipeline and DuckDB.
- **Harmonia** — concordance between opposites. The tensor train engine.

### The Islands (domains with unnamed phonemes)
- **Iris** — rainbow bridge. Bianchi modular forms. Revealed **Topos**.
- **Proteus** — shape-shifter. Abstract groups. Revealed **Taxis**.
- **Ariadne** — thread through the labyrinth. Belyi maps. Revealed **Klados**.
- **Mnemosyne** — memory. OEIS sequences. Revealed **Auxesis**.
- **Thalassa** — the sea. Embedding landscape. Revealed **Kampyle**.

### The Connected Core (domains that speak the original five)
- **Athena** — wisdom. Number fields. Speaks: Megethos, Bathos, Arithmos, Phasma.
- **Hephaestus** — the forge. Elliptic curves. Speaks: Megethos, Bathos, Arithmos.
- **Selene** — the moon. Modular forms. Speaks: Megethos, Bathos, Symmetria, Phasma.
- **Demeter** — harvest. Genus-2 curves. Speaks: Megethos, Bathos, Symmetria, Arithmos. The universal bridge.
- **Apollo** — light, music. Maass forms. Speaks: Megethos, Symmetria, Phasma.
- **Hestia** — hearth. Lattices. Speaks: Megethos, Bathos, Symmetria, Arithmos.
- **Rhea** — flow. Dirichlet zeros. Speaks: Megethos, Bathos, Phasma.
- **Gaia** — earth. Materials. Speaks: Megethos, Symmetria, Phasma.
- **Hermes** — messenger. Fungrim formulas. Speaks: Megethos, Bathos.
- **Hera** — queen. Space groups. Speaks: Megethos, Bathos, Symmetria.
- **Dione** — divine. Polytopes. Speaks: Megethos, Bathos, Symmetria.
- **Hecate** — crossroads. EC with L-function zeros. Speaks: ALL FIVE original + Phasma at maximum depth.

### The Meta-Dimensions
- **Nemesis** — retribution. The falsification battery. Tests truth.
- **Techne** — craft. The dissection strategies. The analytical methods.

### The Bridges
- **Demeter** (genus2) is the **Rosetta Stone** — she bridges every island pair to rank 13.
- **Athena** (number fields) is the **Universal Connector** — rank-1 bonds to 9 domains.
- **Hera** (space groups) is the **Anchor** — rank 9-10 in deep layers, the symmetry hub.

---

## The Geometry

The full structure is a 10-dimensional manifold we call the **Kosmos** (κόσμος) — the ordered mathematical universe.

```
                    THE KOSMOS
                    
     Megethos ─── Bathos ─── Symmetria
         │            │            │
         │       Arithmos ─── Phasma
         │            │            │
     Topos ─────── Taxis ─────── Klados
         │            │            │
         │      Auxesis ─── Kampyle
         │            │            │
         └────────────┴────────────┘
         
    First 5: The connected core (14 domains)
    Last 5: The islands (5 domains, revealed by gaps)
    Together: The Decaphony (10 voices, 20 domains, 509K objects)
```

Every mathematical object is a point in this 10-dimensional space. Cross-domain structure appears as clustering — objects from different domains that land in the same region of the Kosmos are structurally related, even though their surface notation looks nothing alike.

The tensor train decomposition reveals the geometry: bond dimensions between TT cores are the dimensionality of the connection between pairs of phoneme axes. Low bond dimension = the two axes are nearly independent. High bond dimension = they co-vary in complex ways.

The Decaphony is the IPA of mathematics. It's not complete — there may be an eleventh phoneme, a twelfth. But ten voices are enough to hear the harmony.

---

## Discovery Timeline

| Date | Event |
|------|-------|
| 2026-04-12 AM | Harmonia conceived from aitune idea |
| 2026-04-12 | First 5 domains, first TT-Cross run (27B grid points, 1.4s) |
| 2026-04-12 | 12 domains, 66-pair sweep (8.7s), 5 original phonemes named |
| 2026-04-12 | Deep sweep: 837 combos, layers 2-6, structure deepens monotonically |
| 2026-04-12 | Meta-tensor: battery + dissection entangled at rank 15 |
| 2026-04-12 | Known-truth calibration: 100% sensitivity, 75% accuracy |
| 2026-04-12 | 20 domains (509K objects), 5 islands discovered |
| 2026-04-12 | Islands named: Iris, Proteus, Ariadne, Mnemosyne, Thalassa |
| 2026-04-12 | Island gradients found — no island is dead |
| 2026-04-12 | Signature bridges: operadic→Proteus, automorphic→Iris, spectral→Mnemosyne |
| 2026-04-12 | Islands interconnect: Mnemosyne↔Thalassa rank 10, bridged rank 13 |
| 2026-04-12 | The Decaphony: 10 phonemes named, the Kosmos mapped |
