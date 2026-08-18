# Report 85: Topos Phoneme Design

**Target agent:** Harmonia
**Topic:** Native observable for Belyi maps (dessins d'enfants)
**Date:** 2026-04-23

## 1. Problem Statement

Harmonia's existing phonemes are centered on arithmetic data from elliptic curves, modular forms, and Dirichlet series. The silent island `belyi ↔ *` (coupling to groups, OEIS, Bianchi, NF all near zero) reflects a missing *receiver channel*. Belyi maps carry genuinely new information — a finite combinatorial/group-theoretic shadow of Gal(Q̄/Q) action — that the current phoneme basis cannot encode.

**Topos** is proposed as a 3-component observable:

- `T1 = monodromy_group_type` — abstract isomorphism class of the monodromy group M(f) ≤ S_d, pulled back to group-theoretic invariant (order, solvability, simple-quotient signature).
- `T2 = passport_signature` — ordered triple of cycle types (λ_0, λ_1, λ_∞) of monodromy generators at {0, 1, ∞}, normalized to canonical partition triple.
- `T3 = (g, d)` — genus of source curve X and degree d of cover, coarse topological invariants.

Topos is a vector in (GroupType) × (PartitionTriple) × (Z≥0)². Discrete, exactly computable, has natural passport equivalence.

## 2. Literature

- **Grothendieck**, *Esquisse d'un Programme* (1984; published in Schneps & Lochak eds., LMS LNS 242, 1997). Source of dessin / Gal(Q̄/Q) programme: Belyi's theorem identifies curves definable over Q̄ with those admitting covers ramified only over {0, 1, ∞}; absolute Galois group acts faithfully on dessins.
- **Lando & Zvonkin**, *Graphs on Surfaces and Their Applications* (Springer, Encyclopaedia of Math. Sciences 141, 2004). Canonical computational reference.
- **Sijsling & Voight**, "On computing Belyi maps", *Publ. Math. Besançon*, 2014, 73–131. Algorithmic backbone for LMFDB `belyi_galmaps` table.
- **Birch**, "Noncongruence subgroups, covers and drawings," in *The Grothendieck Theory of Dessins d'Enfants* (Schneps, ed., LMS LNS 200, 1994).

## 3. Computability

LMFDB `belyi_galmaps` exposes: `monodromy_representation`, `abc` (passport), `g` (genus), `deg`, `group` label, `field_of_definition`. Pipeline:

1. Parse `monodromy_representation` into σ_0, σ_1, σ_∞ ∈ S_d.
2. Send triple to GAP via `Group(σ_0, σ_1)`; compute `StructureDescription`, `IsSolvable`, `CompositionFactors`, order. → T1.
3. Cycle types from `abc`; canonicalize to sorted partitions → T2.
4. T3 reads directly from `g` and `deg`.

No new scraping needed; computation is local and deterministic.

## 4. Cross-Domain Coupling

- **belyi ↔ groups**: T1 is a group; coupling via rate at which Belyi monodromy groups hit finite-group taxonomy (GAP Small Groups ID). Predicted non-trivial: monodromy groups concentrate on S_d, A_d, PSL_2(F_p) and products.
- **belyi ↔ NF**: Gal(Q̄/Q) permutes dessins within a passport; `field_of_definition` joins to `nf_fields`.
- **belyi ↔ bianchi**: For g ∈ {0, 1} and monodromy inside PSL_2(Z), dessin corresponds to (possibly noncongruence) finite-index subgroup; couple via index, signature, cusp widths at Q(i), Q(√-3).
- **belyi ↔ oeis**: Passport counts {N(g, [λ_0, λ_1, λ_∞])} and genus-by-degree counts match Hurwitz-number sequences.

## 5. Falsification Criteria

Topos fails as a phoneme if, after ingesting full `belyi_galmaps`:

- Permutation-null coupling of (T1, T2, T3) to groups, NF, Bianchi, OEIS all have |z| < 2 under mean-spacing-normalized comparison.
- T2 coupling collapses onto T3 (partial correlation of T2 controlling for (g, d) indistinguishable from noise).
- Permutation-over-passport null shows cross-domain signal fully explained by degree alone (rediscovery of Megethos).

## 6. Specific Computations for Harmonia

1. Ingest all `belyi_galmaps` rows; materialize (T1, T2, T3) per map.
2. Build passport-indexed histograms, compare to Hurwitz-number OEIS entries as prior.
3. Run standard 4-way coupling test: Topos vs. {groups, NF, Bianchi, OEIS}, permutation null at passport level per `feedback_permutation_null`.
4. Agora adversarial check: does detrending by (g, d) leave residual signal? If yes, T1 is active component.

**Word count: 778**
