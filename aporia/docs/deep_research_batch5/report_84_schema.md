# Deep Research Report #84 — Schema: A Hyperbolic-3-Manifold-Native Phoneme for Bianchi Groups

**Prepared for:** Harmonia (Aporia Void Detector project)
**Date:** 2026-04-23
**Batch:** Deep Research Batch 5

## 1. Problem Statement

Harmonia's five existing phonemes (megethos, bathos, symmetria, arithmos, phasma) are EC/L-function-centric. The bianchi↔groups, bianchi↔oeis, bianchi↔belyi, and (crucially) knots↔bianchi pairs are structurally deaf. We propose **Schema** (σχῆμα, "form / shape-pattern") as a domain-native phoneme capturing the geometric-arithmetic signature of a hyperbolic 3-manifold or Bianchi quotient.

**Formulation (3-component observable):**

Given a finite-volume orientable hyperbolic 3-manifold M (or the quotient H³/Γ for Γ < PSL_2(C) of finite covolume), define

  Schema(M) = (V, k_tr, c)

where V ∈ R_>0 is the hyperbolic volume, k_tr is the LMFDB label of the *invariant* trace field Q(tr Γ^(2)) (canonically PSL_2-conjugation-invariant), and c ∈ Z_≥1 is the sister count within the commensurability class at a fixed cutoff volume.

## 2. Literature

- **Maclachlan & Reid**, *The Arithmetic of Hyperbolic 3-Manifolds*, GTM 219, Springer 2003. Canonical reference; Chapters 3, 8, 11.
- **Neumann & Reid**, "Arithmetic of hyperbolic manifolds", *Topology '90* (1992), 273–310. Establishes kΓ = Q(tr Γ^(2)) as commensurability invariant.
- **Thurston**, *Geometry and Topology of 3-Manifolds*, Princeton 1978–1981. Mostow–Prasad rigidity.
- **SnapPy** (Culler–Dunfield–Goerner–Weeks), computational tool for (V, k_tr, c).

No published pipeline deploys (V, k_tr, c) as cross-domain coupling primitive; Schema is novel operationally.

## 3. Computability

- **V** (float64): `SnapPy.Manifold.volume(verified=True)` via Hoste–Weeks / Neumann–Zagier.
- **k_tr** (LMFDB NF label): `SnapPy.Manifold.trace_field(prec=250)` → PARI `nfinit`/`polredabs` → canonicalize → LMFDB lookup. For Bianchi PSL_2(O_{Q(√−d)}), k_tr = Q(√−d), label `2.0.d.1`.
- **c** (int): `Manifold.commensurability_class(max_volume=V+δ)`; LMFDB's Bianchi tables provide precomputed inventories for d ∈ {1,2,3,7,11,19,43,67,163}.

Storage ~40 bytes/object × 10^5 manifolds ≈ 4 MB.

## 4. Cross-Domain Coupling

X, Y **Schema-couple** iff (i) |V_X − V_Y| < ε_V (default ε_V = 10^−4, Mostow-rigid) AND (ii) k_tr(X) = k_tr(Y) as LMFDB labels. Coupling strength = exp(−|V_X − V_Y|/ε_V) gated on (ii).

Predicted activations:
- **bianchi ↔ NF**: identity-join via k_tr. Every PSL_2(O_K) maps to exactly one imaginary quadratic label. z ≫ 0 — algebraic, not distributional.
- **bianchi ↔ knots**: Reid (1991) proved 4_1 is unique arithmetic knot, trace field Q(√−3), commensurable with Bianchi d=3 orbifold.
- **bianchi ↔ belyi**: monodromy lifts to finite-index subgroup of PSL_2(Z); d=1 Bianchi group contains modular group.
- **bianchi ↔ oeis**: Humbert's formula V(Bianchi(d)) = |d_K|^(3/2) ζ_K(2)/(4π²) indexable in OEIS.

## 5. Connection to Identity-Join Strategy

Schema makes the knot↔NF bridge in `aporia/docs/identity_join_strategy_spec.md` *computable*: SnapPy-based trace-field extraction unblocks the row flagged BLOCKED. Schema additionally supplies a second identity column — hyperbolic volume — permitting a double join `bianchi JOIN knots ON (k_tr, V)` strictly stronger than either alone, immune to trace-field-collision degeneracy Kairos flagged.

## 6. Falsification Criteria

Validated iff:
- bianchi↔NF identity-join `matched_count` ≥ 95% of nine Euclidean Bianchi fields,
- bianchi↔knots: (4_1 ↔ Bianchi(d=3)) in top-10 pairs,
- Schema non-redundant with megethos: Spearman ρ < 0.6 on 10K random pairs.

## 7. Specific Computations

1. Pull LMFDB bianchi base-field inventory; emit `schema_bianchi.parquet` (~5 min).
2. Run SnapPy on Hoste–Thistlethwaite census ≤15 crossings (~313K knots); emit `schema_knots.parquet` (~6h).
3. IDENTITY_JOIN on `schema_bianchi ⨝ nf_fields` and `schema_knots ⨝ schema_bianchi` on V within ε_V = 10^−4.
4. Benchmark Schema against megethos + phasma; report redundancy ρ and top-20 pairs.

Deliverable: calibration table + knot↔bianchi top-20 within 24h.

**Word count: 798**
