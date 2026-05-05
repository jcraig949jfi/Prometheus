# Surviving-Claim Morphology Report

**Computed:** 2026-05-05  
**By:** Charon (substrate cartography suite, Task A)  

**Scope:** SINGLE_DOMAIN — battery_sweep_v2 is dominated by A149* lattice walks (100/103 from regime_change source). Cross-domain rich findings n=3 (battery_runs.jsonl) — case-study only.

---

## TL;DR

The brief assumed a unified per-claim kill ledger across 6 cross-domain envs. Survey found this does not exist at production scale: 100/103 kill records in `battery_sweep_v2.jsonl` come from one source (regime_change, A149* lattice walks); cross-domain rich findings are n=3 in `battery_runs.jsonl`. **Almost every feature-outcome correlation is INDETERMINATE** — substrate-grade calibrated negative. Strong within-domain effects exist (has_diag_neg → unanimous_kill at high difference) but cannot be classified productive vs blind-spot without cross-domain replication.

**N analyzed:** 103 kill-sweep records, 97 with parseable step-set features.

**Outcome distribution:**
- survives: 41
- near_miss: 86
- any_kill: 62
- early_kill_F1: 56
- late_kill_F11: 16
- unanimous_kill: 9

## Feature-outcome correlations (single-domain)

Binary-feature analyses report `P(outcome | feature) - P(outcome | ¬feature)` with Wald 95% CI. Correlations classified by the data-shape framework (productive / blind_spot / thin_data / overfitting / indeterminate).

| feature | outcome | P(o\|f) | P(o\|¬f) | diff (95% CI) | n | classification |
|---|---|---|---|---|---|---|
| has_diag_neg | survives | 0.440 | 0.403 | +0.037 [-0.188, +0.262] | 25/72 | overfitting |
| has_diag_neg | near_miss | 0.600 | 0.958 | -0.358 [-0.556, -0.161] | 25/72 | overfitting |
| has_diag_neg | early_kill_F1 | 0.560 | 0.528 | +0.032 [-0.194, +0.258] | 25/72 | overfitting |
| has_diag_neg | late_kill_F11 | 0.400 | 0.028 | +0.372 [+0.176, +0.568] | 25/72 | overfitting |
| has_diag_neg | unanimous_kill | 0.240 | 0.000 | +0.240 [+0.073, +0.407] | 25/72 | overfitting |
| has_diag_pos | survives | 0.000 | 0.417 | -0.417 [-0.515, -0.318] | 1/96 | thin_data |
| has_diag_pos | near_miss | 0.000 | 0.875 | -0.875 [-0.941, -0.809] | 1/96 | thin_data |
| has_diag_pos | early_kill_F1 | 1.000 | 0.531 | +0.469 [+0.369, +0.569] | 1/96 | thin_data |
| has_diag_pos | late_kill_F11 | 1.000 | 0.115 | +0.885 [+0.822, +0.949] | 1/96 | thin_data |
| has_diag_pos | unanimous_kill | 1.000 | 0.052 | +0.948 [+0.903, +0.992] | 1/96 | thin_data |
| any_axis_asymmetry_ge3 | survives | 0.000 | 0.435 | -0.435 [-0.536, -0.333] | 5/92 | thin_data |
| any_axis_asymmetry_ge3 | near_miss | 0.000 | 0.913 | -0.913 [-0.971, -0.855] | 5/92 | thin_data |
| any_axis_asymmetry_ge3 | early_kill_F1 | 1.000 | 0.511 | +0.489 [+0.387, +0.591] | 5/92 | thin_data |
| any_axis_asymmetry_ge3 | late_kill_F11 | 1.000 | 0.076 | +0.924 [+0.870, +0.978] | 5/92 | thin_data |
| any_axis_asymmetry_ge3 | unanimous_kill | 1.000 | 0.011 | +0.989 [+0.968, +1.010] | 5/92 | thin_data |
| max_x_asymmetry_ge3 | survives | 0.000 | 0.435 | -0.435 [-0.536, -0.333] | 5/92 | thin_data |
| max_x_asymmetry_ge3 | near_miss | 0.000 | 0.913 | -0.913 [-0.971, -0.855] | 5/92 | thin_data |
| max_x_asymmetry_ge3 | early_kill_F1 | 1.000 | 0.511 | +0.489 [+0.387, +0.591] | 5/92 | thin_data |
| max_x_asymmetry_ge3 | late_kill_F11 | 1.000 | 0.076 | +0.924 [+0.870, +0.978] | 5/92 | thin_data |
| max_x_asymmetry_ge3 | unanimous_kill | 1.000 | 0.011 | +0.989 [+0.968, +1.010] | 5/92 | thin_data |
| max_y_asymmetry_ge3 | survives | 0.000 | 0.412 | -0.412 [-0.510, -0.314] | 0/97 | thin_data |
| max_y_asymmetry_ge3 | near_miss | 0.000 | 0.866 | -0.866 [-0.934, -0.798] | 0/97 | thin_data |
| max_y_asymmetry_ge3 | early_kill_F1 | 0.000 | 0.536 | -0.536 [-0.635, -0.437] | 0/97 | thin_data |
| max_y_asymmetry_ge3 | late_kill_F11 | 0.000 | 0.124 | -0.124 [-0.189, -0.058] | 0/97 | thin_data |
| max_y_asymmetry_ge3 | unanimous_kill | 0.000 | 0.062 | -0.062 [-0.110, -0.014] | 0/97 | thin_data |
| max_z_asymmetry_ge3 | survives | 0.000 | 0.412 | -0.412 [-0.510, -0.314] | 0/97 | thin_data |
| max_z_asymmetry_ge3 | near_miss | 0.000 | 0.866 | -0.866 [-0.934, -0.798] | 0/97 | thin_data |
| max_z_asymmetry_ge3 | early_kill_F1 | 0.000 | 0.536 | -0.536 [-0.635, -0.437] | 0/97 | thin_data |
| max_z_asymmetry_ge3 | late_kill_F11 | 0.000 | 0.124 | -0.124 [-0.189, -0.058] | 0/97 | thin_data |
| max_z_asymmetry_ge3 | unanimous_kill | 0.000 | 0.062 | -0.062 [-0.110, -0.014] | 0/97 | thin_data |
| flagged | survives | 0.410 | 0.000 | +0.410 [+0.314, +0.506] | 100/0 | thin_data |
| flagged | near_miss | 0.850 | 0.000 | +0.850 [+0.780, +0.920] | 100/0 | thin_data |
| flagged | early_kill_F1 | 0.540 | 0.000 | +0.540 [+0.442, +0.638] | 100/0 | thin_data |
| flagged | late_kill_F11 | 0.140 | 0.000 | +0.140 [+0.072, +0.208] | 100/0 | thin_data |
| flagged | unanimous_kill | 0.070 | 0.000 | +0.070 [+0.020, +0.120] | 100/0 | thin_data |
| regime_change | survives | 0.410 | 0.000 | +0.410 [+0.314, +0.506] | 100/0 | thin_data |
| regime_change | near_miss | 0.850 | 0.000 | +0.850 [+0.780, +0.920] | 100/0 | thin_data |
| regime_change | early_kill_F1 | 0.540 | 0.000 | +0.540 [+0.442, +0.638] | 100/0 | thin_data |
| regime_change | late_kill_F11 | 0.140 | 0.000 | +0.140 [+0.072, +0.208] | 100/0 | thin_data |
| regime_change | unanimous_kill | 0.070 | 0.000 | +0.070 [+0.020, +0.120] | 100/0 | thin_data |
| delta_pct_high | survives | 0.000 | 0.423 | -0.423 [-0.521, -0.324] | 6/97 | thin_data |
| delta_pct_high | near_miss | 0.000 | 0.887 | -0.887 [-0.950, -0.823] | 6/97 | thin_data |
| delta_pct_high | early_kill_F1 | 1.000 | 0.515 | +0.485 [+0.385, +0.584] | 6/97 | thin_data |
| delta_pct_high | late_kill_F11 | 1.000 | 0.103 | +0.897 [+0.836, +0.957] | 6/97 | thin_data |
| delta_pct_high | unanimous_kill | 1.000 | 0.031 | +0.969 [+0.935, +1.004] | 6/97 | thin_data |
| n_steps_5 | survives | 0.412 | 0.000 | +0.412 [+0.314, +0.510] | 97/0 | thin_data |
| n_steps_5 | near_miss | 0.866 | 0.000 | +0.866 [+0.798, +0.934] | 97/0 | thin_data |
| n_steps_5 | early_kill_F1 | 0.536 | 0.000 | +0.536 [+0.437, +0.635] | 97/0 | thin_data |
| n_steps_5 | late_kill_F11 | 0.124 | 0.000 | +0.124 [+0.058, +0.189] | 97/0 | thin_data |
| n_steps_5 | unanimous_kill | 0.062 | 0.000 | +0.062 [+0.014, +0.110] | 97/0 | thin_data |
| known_count_low | survives | 0.423 | 0.000 | +0.423 [+0.324, +0.521] | 97/6 | thin_data |
| known_count_low | near_miss | 0.876 | 0.167 | +0.710 [+0.404, +1.015] | 97/6 | thin_data |
| known_count_low | early_kill_F1 | 0.526 | 0.833 | -0.308 [-0.622, +0.007] | 97/6 | thin_data |
| known_count_low | late_kill_F11 | 0.113 | 0.833 | -0.720 [-1.025, -0.415] | 97/6 | thin_data |
| known_count_low | unanimous_kill | 0.052 | 0.667 | -0.615 [-0.995, -0.235] | 97/6 | thin_data |

## Categorical breakdowns

### best_model → survives

| category | n | n_outcome | p_outcome |
|---|---|---|---|
| poly_log_d5 | 100 | 41 | 0.410 |

### best_model → near_miss

| category | n | n_outcome | p_outcome |
|---|---|---|---|
| poly_log_d5 | 100 | 85 | 0.850 |

### best_model → early_kill_F1

| category | n | n_outcome | p_outcome |
|---|---|---|---|
| poly_log_d5 | 100 | 54 | 0.540 |

### best_model → late_kill_F11

| category | n | n_outcome | p_outcome |
|---|---|---|---|
| poly_log_d5 | 100 | 14 | 0.140 |

### best_model → unanimous_kill

| category | n | n_outcome | p_outcome |
|---|---|---|---|
| poly_log_d5 | 100 | 7 | 0.070 |

## Cross-domain rich findings (battery_runs.jsonl, n=3)

n=3 cross-domain rich findings. Case studies only — too few for statistical morphology comparison. F2 (materials Tc) achieved 'LAW' tier with eta²=0.46; F1 + F3 (genus2) at B+ constraint/tendency. All 3 'CONFOUND_ROBUST' on F17 and 'STABLE' on F18 — but n=3 prevents inference about what feature distinguishes the LAW from the constraints.

| finding_id | claim | data_source | n_samples | verdict | tier |
|---|---|---|---|---|---|
| F1_ENDO | ST group constrains conductor factorization | genus2 3K sample | 3000 | CONSTRAINT | B+ (constraint, eta²=0.050) |
| F2_SG_TC | Space group predicts Tc | 3DSC_MP.csv (3995 records) | 3995 | LAW | B+ (law, eta²=0.457) |
| F3_FIBER | ST group determines fiber ratio | genus2 66K curves | 66158 | TENDENCY | B+ (tendency, eta²=0.027) |

## Ergon per-class hit-rate cross-reference

Ergon's per-class hit rates show structural ~7x uniform on promote rate. That confirms predicate-template family matters WITHIN predicate-search. Does NOT confirm cross-domain morphology — different unit (predicate vs claim), different corpus (a149 only).

- structural promote rate: 0.333
- uniform promote rate: 0.048
- ratio: 6.88×

## Feature extraction decisions

- Walk-step-set geometry features (n_steps, neg/pos x/y/z, has_diag_*, n_axis_aligned, axis_asymmetry) extracted from sequence name via regex parsing of step-set notation. Same logic as ergon._a149_real_corpus.
- Corpus features (delta_pct, regime_change, best_model, n_terms, known_count) read directly from asymptotic_deviations.jsonl.
- Source field used as a proxy for record-template (regime_change vs ast_bridges vs root_probes). 100/103 are regime_change → effectively single-template; flagged in classification.
- Outcome flags derived from kill_tests array: survives = empty array; near_miss = len <= 1; unanimous = len >= 4; F1/F11 by name match.
- MISSING from this analysis (substrate hasn't measured them): cross_domain_count per claim (no per-claim cross-domain ledger), feature_family (collapses to single family for sweep data), descriptor_cell (MAP-Elites cells not persisted), claim_template (only 'asymptotic_growth_rate_anomaly' template in this data), uses_learned_embedding (no per-claim embedding metadata persisted), uses_mod_p_fingerprint (no mod_p data joined), uses_spectral_feature (no spectral feature in sweep+deviations join), uses_graph_feature (N/A for lattice-walk domain), uses_database_join (single-source).
- Cross-seed CIs not available: battery_sweep_v2 records do not carry a seed field. Each record represents one battery run; reproducibility across seeds would require re-running, which isn't in scope. Wald CIs on within-data feature-outcome differences are reported instead.

## Honesty notes

- SCOPE FLAG: this morphology analysis is single-domain (A149* lattice walks, 100/103 records from regime_change source). The brief assumed a cross-domain unified kill ledger; survey 2026-05-05 found this does not exist at production scale. Cross-domain rich findings n=3 — case-study-only, statistically uninformative.
- Productive vs blind-spot vs thin-data classification requires cross-domain replication. With only one substantial domain in the kill ledger, almost all features get flagged INDETERMINATE. This is the honest answer. Targeting the substrate's expansion at multi-domain kill-record collection is the next-step ask.
- All correlations are within-domain (lattice walks). The '~7x lift on has_diag_neg for any_kill' style finding may reflect: (a) genuine boundary-geometry obstruction signal, (b) regime_change source template that systematically labels diag-neg walks as flagged, (c) corpus selection bias (the seed sequences were chosen because they showed asymptotic deviations).
- Wald CIs are based on independence assumption that doesn't fully hold (sequences in a149 family share construction templates). Effective n is plausibly less than reported n; treat CIs as optimistic.
- battery_runs.jsonl (3 cross-domain records: F1_ENDO genus2, F2_SG_TC materials, F3_FIBER genus2) is the only multi-domain rich-falsifier data. n=3 means even single-feature trends are case-study-only.
- Ergon per-class hit rates from 2026-05-05 are cross-referenced as qualitative sanity check, not as cross-domain validation. Different unit (predicate vs claim), different corpus (a149 only), same domain — they tell us about predicate-template hierarchy, not about cross-domain morphology.
- The 4 honesty classes (productive / blind_spot / thin_data / overfitting) collapse here because most signal is INDETERMINATE. When the substrate has BSD/modular/knot kill ledgers at >100 records each, this analysis can be re-run with productive vs blind-spot actually testable.
- Empty 'kill_path' fields in some records: not all sweep records had kill_tests populated; those with empty arrays count as SURVIVES per the schema. Confirmed 41/103 = 0 kills; this is consistent with the verdict='SURVIVES' field count.

---

— Charon, Task A, 2026-05-05