# Deep Research Report #83 — Taxis: A Group-Theory-Native Phoneme for LMFDB Finite Groups

**Prepared for:** Harmonia (Aporia Void Detector project)
**Date:** 2026-04-23
**Batch:** Deep Research Batch 5

## 1. Problem Statement

Harmonia's five existing phonemes (megethos, bathos, symmetria, arithmos, phasma) are anchored to elliptic curves, modular forms, and L-functions. This leaves the `groups` domain structurally mute: the currently-silent pairs groups↔oeis, groups↔charon_landscape, and groups↔bianchi have no phoneme that listens to the object's *internal arithmetic of representations*. We propose **Taxis** (τάξις, "arrangement / order"), a finite-group-native phoneme built from the two canonical multisets that co-determine most of a group's character-theoretic behaviour.

**Formulation (2-component primary observable, 1 secondary):**

For a finite group G, define

  Taxis(G) = (D(G), K(G);  m(G))

where D(G) = {{χ(1) : χ ∈ Irr(G)}} is the multiset of **irreducible complex character degrees** (with multiplicity), K(G) = {{|[g]| : g conjugacy-class representative}} is the multiset of **conjugacy class sizes**, and the optional secondary m(G) is the order of the **Schur multiplier** H²(G, ℂ*).

Both D(G) and K(G) are partitions of |G|: ∑χ(1)² = |G| (column-orthogonality of the character table) and ∑|[g]| = |G| (orbit-counting). Taxis is therefore a pair of ordered partitions of the group order plus a small integer — a compact, canonical fingerprint.

## 2. Literature

- Isaacs, I. M., *Character Theory of Finite Groups*, AMS Chelsea 2006 — standard reference; Chapters 2–3 establish D(G) and its constraints (Ito's theorem, degree-divides-index).
- Huppert, B., *Character Theory of Finite Groups*, de Gruyter 1998 — character-degree-graph classification programme (Huppert's ρ–σ conjecture).
- Bertram, E. A., Herzog, M., Mann, A., "On a graph related to conjugacy classes of groups", *Bull. LMS* 22 (1990) 569–575.
- Navarro, G., *Character Theory and the McKay Conjecture*, Cambridge 2018 — modern refinements and p-local structure tied to D(G).
- GAP **SmallGroups Library** (Besche–Eick–O'Brien) and LMFDB `gps_groups` table realize Taxis computations at scale.

## 3. Computability

LMFDB's `gps_groups` table carries 544K entries with columns including `order`, `irrep_degrees` (= D), `conjugacy_class_sizes` (= K), `derived_length`, `schur_multiplier` where computed, plus GAP IDs. For small groups (|G| ≤ 2000, excluding 1024) both D and K are precomputed; for larger groups Harmonia can call GAP via `gap.CharacterDegrees(G)` and `gap.SizesConjugacyClasses(G)`, O(|G|²·log|G|) character-table time dominated by Dixon–Schneider. Expected pass cost: ~15 min for all LMFDB-resident groups. Storage ≈ 110 MB to `ergon/taxis_groups.parquet`.

## 4. Cross-Domain Coupling Structure

Two objects X, Y **Taxis-couple** iff:

1. D(X) = D(Y) as multisets *within tolerance*: sorted-degree vectors match after padding, Hamming tolerance ≤ 1 for |G| ≤ 64, 0 otherwise;
2. K(X) = K(Y) under same rule;
3. (optional tiebreaker) |H²(X)| = |H²(Y)| when both known.

Coupling strength = 1 − (d_H(D_X, D_Y) + d_H(K_X, K_Y)) / (|D| + |K|). Stricter than megethos; orthogonal to symmetria.

Expected hits:
- **Galois group of number field ↔ abstract group**: exact via `nf_fields.galois_label`.
- **Belyi monodromy ↔ group**: `belyi_galmaps.monodromy` → S_n → abstract group.
- **OEIS ↔ groups**: character-degree-enumeration OEIS subfamily (~150 sequences).

## 5. Tensor Activation Predictions

- **groups↔oeis**: coupling ≥ 0.35
- **groups↔NF**: ≥ 0.50 via Galois label (ground truth)
- **groups↔belyi**: ≥ 0.25
- **groups↔bianchi**: ≤ 0.15 (harder test)
- **groups↔charon_landscape**: ≥ 0.20

## 6. Falsification Criteria

Validated iff:
- groups↔NF coupling ≥ 0.40 (ground truth; failure here kills),
- ≥ 2 of {groups↔oeis, groups↔belyi, groups↔charon} exceed 0.20,
- Non-redundant with symmetria: Spearman ρ (coupling matrices) < 0.55.

## 7. Specific Computations for Harmonia

1. Full LMFDB Taxis pass: pull D, K, multiplier to parquet.
2. Galois ground truth join.
3. OEIS sweep for small-int multiset matches.
4. Belyi monodromy join via GAP `IdGroup`.
5. Redundancy benchmark vs symmetria.

Deliverable: coupling-rank table + redundancy within 24h.

**Word count: 798**
