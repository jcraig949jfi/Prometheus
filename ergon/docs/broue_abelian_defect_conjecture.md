# Broue's Abelian Defect Group Conjecture — Deep Research for Ergon

## The Conjecture (Broue 1990)

Let G be a finite group, p a prime, B a p-block of kG (k algebraically closed, char p) with **abelian** defect group D. Let b be the **Brauer correspondent** of B in N_G(D). Then there exists an equivalence of bounded derived categories: D^b(B-mod) ~ D^b(b-mod). The conjecture is that p-blocks with abelian defect are "homologically simple" — their entire derived category is controlled by the local structure at the normalizer.

A **block** partitions irreducible representations into families sharing a common defect group D (a p-subgroup measuring how far the block is from semisimple). The defect group controls complexity: |D| = 1 gives semisimple blocks (Maschke), cyclic D gives tame representation type, and wild type begins at Z/p x Z/p. "Abelian defect" means D is abelian — the boundary between tractable and intractable.

The **Brauer correspondent** b is the unique block of kN_G(D) satisfying Brauer's first main theorem: b and B share the same defect group D and their block idempotents are linked via the Brauer map. The normalizer N_G(D) is always a smaller group, so derived equivalence would reduce modular representation theory of B to a local computation.

## Tilting Complexes and Why They Are Hard

Rickard (1989) proved that derived equivalences between blocks are realized by **tilting complexes** — bounded chain complexes T of projective bimodules such that Hom(T,T[n]) = 0 for n != 0 and T generates the derived category. Constructing T explicitly requires: (1) identifying the correct projective modules, (2) finding maps between them whose mapping cones produce the right homology, (3) verifying the generation condition. For blocks of wild type this is a combinatorial nightmare — the number of indecomposable projectives grows with |D|, and the maps between them depend on detailed knowledge of the Ext algebra.

## Proven Cases

**Cyclic defect (Rickard 1996):** Full proof via explicit tilting complexes constructed from the Brauer tree. The tree structure makes the combinatorics tractable.

**Symmetric groups (Chuang-Rouquier 2008):** The breakthrough. They proved Broue's conjecture for all blocks of symmetric groups by constructing a **categorical sl_2 action** on the direct sum of derived categories of blocks with fixed weight. The sl_2 Chevalley generators (i-induction and i-restriction functors) provide the derived equivalences directly — the "reflection functors" implementing Weyl group symmetry are the tilting equivalences. This categorification approach avoids explicit tilting complex construction entirely.

**Blocks with defect Z/p x Z/p (Koshitani, Kunugi, Waki, various 2000s-2020s):** Case-by-case for specific groups. Each requires custom construction.

## Sporadic Groups Status

Systematic computational verification via GAP and MAGMA has checked Broue's conjecture for most blocks of sporadic groups with abelian defect. As of 2024: all 26 sporadic groups have been examined for small primes (p = 2, 3, 5, 7). The Mathieu groups M_11, M_12, M_22, M_23, M_24 are fully verified. The Monster and Baby Monster remain partially open for certain 2-blocks where the defect groups are large abelian 2-groups. Noeske-Hiss-Lux computed decomposition matrices and Brauer correspondents for many sporadic blocks. Koshitani-Muller verified specific cases for Conway groups and Janko groups. The principal block is often hardest because its defect group is a Sylow p-subgroup.

## Computational Tools

GAP's `PrimeBlocks` and MAGMA's `Blocks` compute block structure including defect groups. The key pipeline: (1) compute block decomposition of kG, (2) identify defect groups via vertices of indecomposable modules, (3) compute the Brauer correspondent in N_G(D), (4) compare derived categories via Cartan matrices, decomposition numbers, and perfect isometries (a weaker condition Broue also conjectured, often checkable computationally).

## Connection to Our 544K Groups Table

Our `groups` table (544,831 abstract groups from LMFDB) contains order, exponent, conjugacy class count, abelianness, and solvability. For a systematic scan: (1) for each group G and prime p dividing |G|, compute Sylow p-subgroups, (2) filter to cases where the Sylow is abelian, (3) compute block structure and Brauer correspondents. The table covers groups up to order ~2000, which includes thousands of (G, B, p) triples with abelian defect that could be computationally verified. Blocks with cyclic defect are already proven; the frontier is non-cyclic abelian defect groups Z/p^a x Z/p^b for small groups where no categorification shortcut exists. This is a tractable computational project: enumerate, construct tilting complexes via Rouquier's algorithm where possible, and catalog the results.
