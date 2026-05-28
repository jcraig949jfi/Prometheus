# Erebos Plugin Quarantine

**Date:** 2026-05-27
**Status:** Per Erebos v3 §4.8 (loader-debt budget). 11 of 25 plugins are quarantined as of v0.33. Quarantined plugins are filtered out of production runs by `applicable_plugins(state)`; only `include_quarantined=True` test fixtures invoke them.

**Cap:** A plugin may emit at most 200 `*_pending` rows OR run for 30 days without a composition loader, whichever comes first. Above the cap, the plugin is quarantined automatically. Revival path: ship the composition loader.

## Quarantine classes

- **`loader_missing`** (7 plugins): plugin works, no composition loader exists yet. Ship the loader to unblock.
- **`infrastructure_blocked`** (3 plugins): plugin works, but the infrastructure required for a composition loader does not exist yet. Per v3 whitepaper §6.
- **`vacuous_by_design`** (1 plugin): plugin's expected behavior is to NOT fire under current substrate state. Architecturally reserved.

## Per-plugin quarantine entries

| Plugin | Class | Quarantined since | Unblock criterion |
|---|---|---|---|
| **g01_intersection** | loader_missing | 2026-05-27 | ship `composition_g01_mahler_intersection.py` loader |
| **g05_confound_swap** | loader_missing | 2026-05-27 | ship `composition_g05_mahler_stratified_resample.py` loader |
| **g06_null_space** | loader_missing | 2026-05-27 | ship `composition_g06_mahler_void_objects.py` loader |
| **g12_invariant_substitution** | loader_missing | 2026-05-27 | ship `composition_g12_mahler_substitution.py` loader |
| **g13_relation_weakening** | loader_missing | 2026-05-27 | ship `composition_g13_mahler_predicate_weakening.py` loader |
| **g14_relation_strengthening** | loader_missing | 2026-05-27 | ship `composition_g14_mahler_predicate_strengthening.py` loader |
| **g22_subgraph_clique** | loader_missing | 2026-05-27 | ship `composition_g22_ledger_clique_master_property.py` loader |
| **g07_analogy** | infrastructure_blocked | 2026-05-27 | BSD-context infrastructure: per-domain dataset accessor + cross-domain translation table + re-run primitive. Est. 2-3 iterations of BSD infra work. |
| **g08_dimensional_lift** | infrastructure_blocked | 2026-05-27 | Ergon ML pipeline: per-parent dataset accessor + Ridge/GBT k-fold held-out + OOD validation. Timeline depends on Ergon's roadmap; not Erebos-blocked. |
| **g21_isomorphism_functor** | infrastructure_blocked | 2026-05-27 | Per-domain morphism enumerators + SageMath integration. Est. 3-5 iterations + SageMath wiring. Likely deferred to v1.0+. |
| **g20_instrument_disagreement** | vacuous_by_design | 2026-05-27 | Lethe v2 ships false-form-fired emissions on modern LLM cascades. May never need to ship; architectural slot reserved. |

## Plugins NOT quarantined (14 of 25)

Active in production: `g02_contrast`, `g03_failure_neighborhood`, `g04_survivor_tightening`, `g09_projection_collapse`, `g10_boundary`, `g11_exception_miner`, `g15_cross_gen_mi`, `g16_anti_anchor`, `g17_causal_intervention`, `g18_minimal_counterexample`, `g19_proof_obligation`, `g23_asymptotic_limit`, `g24_symmetry_twist`, `g25_degeneracy`. Each has at least one composition loader.

## Revival protocol

When a composition loader ships for a quarantined plugin:
1. Add the loader file to `charon/agents/stygian/loaders/` and wire its force-import to `charon/agents/stygian/executor.py`.
2. Add synthetic-control tests per the v3 Phase 0 ITER-16-20 pattern.
3. Run the full test suite to confirm no regressions.
4. Remove the plugin's entry from `QUARANTINE_RULES` in `charon/agents/erebos/_quarantine.py`.
5. Run the test suite again; `test_quarantine_class_counts_correct` and `test_applicable_plugins_excludes_quarantined_by_default` will reflect the new count.
6. Commit with the unblock action documented in the commit message.

## Implications for the substrate's framing

- The v1 whitepaper's "25/25 plugin REGISTRY" framing is technically still true (the REGISTRY still contains all 25) but is no longer the right number to cite for substrate capability. The accurate framing post-v3:
  - **REGISTRY size:** 25 plugins
  - **Active in production:** 14 plugins
  - **Quarantined:** 11 plugins (7 loader-missing + 3 infrastructure-blocked + 1 vacuous-by-design)
- The whitepaper's value claims that rely on "25/25 coverage" need v3-§4.10 reclassification (ITER-29).
- Substrate findings produced by quarantined plugins (none exist as of v0.33; G05 / G06 have only synthetic tests, no live emissions) would be downgraded to "test-coverage finding" rather than "substrate finding."

## Open question

The 7 plain `loader_missing` plugins are the natural Phase 1 / Phase 3+ work-queue. The order of unblocking should follow:
1. Cost/benefit per ITER-27 value_per_tick estimates.
2. Cross-plugin interaction (e.g., G06 Null-Space requires void-object generation that overlaps with G16 Anti-Anchor's adversarial-search).
3. Sprint-1 results — if Phase 2 surfaces specific gaps, those plugins jump the queue.
