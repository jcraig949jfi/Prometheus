# Substrate Coverage Map (BSD / modular / knot)

**Computed:** 2026-05-05  
**By:** Charon (substrate cartography suite, Task C)  
**Scope:** BSD / modular / knot triple per brief  
**Total objects analyzed:** 8927

---

## Coverage cells

| cell | n | tag | flags | missingness | battery_applicable | safe_for_ergon |
|---|---|---|---|---|---|---|
| BSD::elliptic_curve::arithmetic::cremona | 1000 | **misleading_dense** | low_invariant_diversity (2 invariants), low_diversity (distinct=3 on n=1000) | 0.0% | True | ✗ |
| BSD::elliptic_curve::L_function::cremona | 1000 | **dense** | — | 0.0% | True | ✓ |
| modular::newform::level_weight::lmfdb | 7875 | **dense** | — | 0.0% | True | ✓ |
| modular::newform::coefficients::lmfdb | 7875 | **misleading_dense** | low_invariant_diversity (1 invariants), low_diversity (distinct=1 on n=7875), uniform a_p length — likely fixed cap | 0.0% | True | ✗ |
| knot::hyperbolic_knot::topological::knotinfo | 52 | **moderate** | — | 0.0% | True | ✗ |
| knot::hyperbolic_knot::trace_field::knotinfo | 52 | **misleading_dense** | high_missingness (85%) | 84.6% | True | ✗ |

## Per-cell detail

### BSD::elliptic_curve::arithmetic::cremona

- n_objects: 1000, tag: **misleading_dense**
- missingness: 0.0%
- flags: low_invariant_diversity (2 invariants), low_diversity (distinct=3 on n=1000)
- notes: Cremona dataset, full ainvs + a_p available. F1+F6+F9+F11 all applicable. Rank distribution: r=0:n=500, r=1:n=400, r=2:n=100

Feature completeness:

| feature | n_with | n_missing | distinct | top_share | dominant |
|---|---|---|---|---|---|
| rank | 1000 | 0 | 3 | 50% | 0 |
| conductor | 1000 | 0 | 804 | 1% | 7350 |

Charon checks:
- **battery_applicable**: True
- **battery_kill_data_available**: false (battery_sweep_v2 is single-domain A149*)
- **real_failures_vs_missing_data**: missingness=0.0% on key invariants — missingness low; failures interpretable
- **cross_domain_links_via_shared_invariant**: modular forms + BSD share L-function structure (a_p, level); knot + BSD share number-field invariants (nf_discriminant). Cross-domain bridges are not 1:1 — they project through shared invariants. Apparent bridges may be artifacts of which invariants are mutually populated.
- **single_dataset_dominated**: True
- **safe_for_ergon**: False
- **low_confidence_reasons**: low_invariant_diversity (2 invariants), low_diversity (distinct=3 on n=1000)

### BSD::elliptic_curve::L_function::cremona

- n_objects: 1000, tag: **dense**
- missingness: 0.0%
- notes: Regulator, L1, real_period — full BSD-formula inputs

Feature completeness:

| feature | n_with | n_missing | distinct | top_share | dominant |
|---|---|---|---|---|---|
| regulator | 1000 | 0 | 500 | — | — |
| L1 | 1000 | 0 | 983 | — | — |
| real_period | 1000 | 0 | 991 | — | — |

Charon checks:
- **battery_applicable**: True
- **battery_kill_data_available**: false (battery_sweep_v2 is single-domain A149*)
- **real_failures_vs_missing_data**: missingness=0.0% on key invariants — missingness low; failures interpretable
- **cross_domain_links_via_shared_invariant**: modular forms + BSD share L-function structure (a_p, level); knot + BSD share number-field invariants (nf_discriminant). Cross-domain bridges are not 1:1 — they project through shared invariants. Apparent bridges may be artifacts of which invariants are mutually populated.
- **single_dataset_dominated**: True
- **safe_for_ergon**: True
- **low_confidence_reasons**: (none)

### modular::newform::level_weight::lmfdb

- n_objects: 7875, tag: **dense**
- missingness: 0.0%
- notes: weight distribution: top values {2: 2463, 4: 1905, 6: 1131, 8: 567, 10: 305}

Feature completeness:

| feature | n_with | n_missing | distinct | top_share | dominant |
|---|---|---|---|---|---|
| weight | 7875 | 0 | 23 | 31% | 2 |
| level | 7875 | 0 | 779 | 1% | 576 |
| char_order | 7875 | 0 | 2 | 89% | 1 |

Charon checks:
- **battery_applicable**: True
- **battery_kill_data_available**: false (battery_sweep_v2 is single-domain A149*)
- **real_failures_vs_missing_data**: missingness=0.0% on key invariants — missingness low; failures interpretable
- **cross_domain_links_via_shared_invariant**: modular forms + BSD share L-function structure (a_p, level); knot + BSD share number-field invariants (nf_discriminant). Cross-domain bridges are not 1:1 — they project through shared invariants. Apparent bridges may be artifacts of which invariants are mutually populated.
- **single_dataset_dominated**: True
- **safe_for_ergon**: True
- **low_confidence_reasons**: (none)

### modular::newform::coefficients::lmfdb

- n_objects: 7875, tag: **misleading_dense**
- missingness: 0.0%
- flags: low_invariant_diversity (1 invariants), low_diversity (distinct=1 on n=7875), uniform a_p length — likely fixed cap
- notes: a_p length distribution: median=None, min=None, max=None

Feature completeness:

| feature | n_with | n_missing | distinct | top_share | dominant |
|---|---|---|---|---|---|
| a_p_length | 7875 | 0 | 1 | 100% | 30 |

Charon checks:
- **battery_applicable**: True
- **battery_kill_data_available**: false (battery_sweep_v2 is single-domain A149*)
- **real_failures_vs_missing_data**: missingness=0.0% on key invariants — missingness low; failures interpretable
- **cross_domain_links_via_shared_invariant**: modular forms + BSD share L-function structure (a_p, level); knot + BSD share number-field invariants (nf_discriminant). Cross-domain bridges are not 1:1 — they project through shared invariants. Apparent bridges may be artifacts of which invariants are mutually populated.
- **single_dataset_dominated**: True
- **safe_for_ergon**: False
- **low_confidence_reasons**: low_invariant_diversity (1 invariants), low_diversity (distinct=1 on n=7875), uniform a_p length — likely fixed cap

### knot::hyperbolic_knot::topological::knotinfo

- n_objects: 52, tag: **moderate**
- missingness: 0.0%
- notes: crossing range [None, None], hyperbolic_volume range [0.00, 12.35]

Feature completeness:

| feature | n_with | n_missing | distinct | top_share | dominant |
|---|---|---|---|---|---|
| crossing_number | 52 | 0 | 8 | 40% | 8 |
| signature | 52 | 0 | 6 | 29% | 0 |
| three_genus | 52 | 0 | 4 | 42% | 2 |
| hyperbolic_volume | 52 | 0 | 49 | — | — |

Charon checks:
- **battery_applicable**: True
- **battery_kill_data_available**: false (battery_sweep_v2 is single-domain A149*)
- **real_failures_vs_missing_data**: missingness=0.0% on key invariants — missingness low; failures interpretable
- **cross_domain_links_via_shared_invariant**: modular forms + BSD share L-function structure (a_p, level); knot + BSD share number-field invariants (nf_discriminant). Cross-domain bridges are not 1:1 — they project through shared invariants. Apparent bridges may be artifacts of which invariants are mutually populated.
- **single_dataset_dominated**: True
- **safe_for_ergon**: False
- **low_confidence_reasons**: (none)

### knot::hyperbolic_knot::trace_field::knotinfo

- n_objects: 52, tag: **misleading_dense**
- missingness: 84.6%
- flags: high_missingness (85%)
- notes: trace_field_class top values: {6: 41, 5: 5, 0: 4, 2: 1, 4: 1}

Feature completeness:

| feature | n_with | n_missing | distinct | top_share | dominant |
|---|---|---|---|---|---|
| nf_discriminant | 8 | 44 | 5 | 50% | 1 |
| nf_class_number | 8 | 44 | 1 | 100% | 1 |
| trace_field_class | 52 | 0 | 5 | 79% | 6 |

Charon checks:
- **battery_applicable**: True
- **battery_kill_data_available**: false (battery_sweep_v2 is single-domain A149*)
- **real_failures_vs_missing_data**: missingness=84.6% on key invariants — treat kills as conflated with missingness
- **cross_domain_links_via_shared_invariant**: modular forms + BSD share L-function structure (a_p, level); knot + BSD share number-field invariants (nf_discriminant). Cross-domain bridges are not 1:1 — they project through shared invariants. Apparent bridges may be artifacts of which invariants are mutually populated.
- **single_dataset_dominated**: True
- **safe_for_ergon**: False
- **low_confidence_reasons**: high_missingness (85%)

## Cross-dataset bridges (from bridges.jsonl)

Total bridges: **4410**

Top datasets by bridge-frequency:

| dataset | n_bridges referencing |
|---|---|
| NumberFields | 3768 |
| LMFDB | 2469 |
| Genus2 | 1586 |
| Isogenies | 1229 |
| mathlib | 263 |
| Fungrim | 237 |
| KnotInfo | 174 |
| Lattices | 38 |
| ANTEDB | 17 |
| SpaceGroups | 15 |
| LocalFields | 8 |
| Polytopes | 7 |
| Maass | 3 |
| MMLKG | 3 |
| OpenAlex | 2 |

bridges.jsonl is concept-keyed cross-dataset coverage. Dataset name → number of bridge-concepts referencing that dataset.

## Honesty notes

- SCOPE: BSD/modular/knot triple per brief. Genus2/mock_theta/oeis_sleeping coverage cells deferred — pilots have corpus stats but not richer feature-level analysis. Quick-survey extension is feasible (~1h additional).
- INCONCLUSIVE_DATA fields (n_claims_generated, n_kills, n_promotes, n_near_misses) reflect Task A's finding: there is no unified per-claim ledger across these 6 envs. The cell counts in the brief schema cannot be populated from persisted data. Coverage map is structural-side only (corpus available + features present); kill-side coverage is INCONCLUSIVE.
- Coverage tags computed at corpus level: dense (n>=200, no flags), moderate (30 <= n < 200), thin (n<30), void (n=0), misleading_dense (n>=30 with one or more of: missingness>20%, top_value_share>80%, low invariant diversity, low distinct values).
- knot corpus has 52 records — borderline thin. Below the 100-record threshold for 'safe_for_ergon'. Hyperbolic-volume coverage range is broad but n is dominated by degree_5_plus trace fields per pilot stats.
- modular_forms DB has 7875 records but pilot uses 1000 (12.7% sample). The pilot's coverage report applies to the sample, not the full corpus. Coverage scaling is feasible: re-run with the full DB for stronger coverage claims.
- The 'cross_domain_link_count' cell field collapses to an INCONCLUSIVE proxy: bridges.jsonl gives concept-keyed cross-dataset links but not per-record cross-domain claim counts. Per-record cross-domain provenance is not persisted.
- Battery applicability is qualitative — based on which standard invariants exist for each domain (BSD has rank+L1, modular has weight+a_p, knot has crossing+hyperbolic_volume). The per-falsifier applicability matrix (does F1 work on knots? does F11 work on modular? etc.) is NOT in this report — that's a separate task requiring battery code-walking.
- 'Safe for Ergon' = (tag ∈ {dense, moderate}) AND battery_applicable AND missingness<20% AND n>=100. This is a coarse threshold; Ergon's actual training-grade requirement may differ.

---

— Charon, Task C, 2026-05-05