# Prometheus File Manifest — March 30, 2026

## Database
- **Location:** F:/Prometheus/noesis/v2/noesis_v2.duckdb
- **Last sanitized:** 2026-03-30
- **Foundation:** 131 traditions, 236 hubs, 9 operators, 2,335 edges

### Tables (post-sanitization)
| Table | Rows | Description |
|-------|------|-------------|
| ethnomathematics | 131 | Deduplicated traditions with enriched vectors |
| abstract_compositions | 236 | Deduplicated impossibility hubs |
| damage_operators | 9 | Canonical operator definitions |
| cross_domain_edges | 2,335 | Cross-domain links (orphans+dupes removed) |
| composition_instances | 4,702 | Spokes with provenance tags |
| floor1_matrix | 2,121 | Floor 1: 9×236 operator×hub (evidence-sourced) |
| tradition_hub_matrix | 2,213 | Floor 2: 131×236 (evidence-only, no templates) |
| depth2_matrix | 14,774 | Floor 3: 81×236 (source-evidence-based) |
| depth3_probes | 19 | Floor 4: Targeted depth-3 verifications |
| discoveries | 35 | Tensor predictions (5 verified, 30 unverified) |
| chains | 100 | Derivation chains |
| chain_steps | 400 | Steps within chains |
| transformations | 295 | Typed transformations between steps |
| operations | 1,714 | Mathematical operations catalog |
| cross_domain_links | 185 | Hub-to-hub links |
| validation_pairs | 6 | Ground-truth isomorphism test pairs |
| prime_landscape | 6 | Mathematical landscape entries |

## Scripts (production — in noesis/v2/)
| Script | Description |
|--------|-------------|
| sanitize_foundation.py | Items 1-3: dedup traditions, hubs, clean orphans |
| tag_provenance.py | Tag composition_instances with source provenance |
| reexplore_floor1.py | Build floor1_matrix from all source evidence |
| rebuild_tradition_hub_evidence.py | Item 4: evidence-only tradition_hub_matrix |
| rebuild_floor3_from_source.py | Evidence-based depth2_matrix |
| tucker_completion.py | SVD + Tucker tensor completion |
| probe_floor4.py | Targeted depth-3 chain probes |
| council_only_tensor.py | Council-only baseline rebuild |

## Scripts (one-off / superseded)
| Script | Status |
|--------|--------|
| build_floor2.py | SUPERSEDED by rebuild_tradition_hub_evidence.py |
| build_floor3.py | SUPERSEDED by rebuild_floor3_from_source.py |
| fill_floor3_remaining.py | SUPERSEDED |
| rebuild_floor3_differentiated.py | SUPERSEDED |

## Audit Exports (in audit/)
| Directory | Contents |
|-----------|----------|
| audit/scripts/ | Copies of production scripts for Athena review |
| audit/data/ | JSON exports: spokes, edges, traditions, hubs, predictions, hit rate trail, scope report |
| audit/reports/ | table_inventory.json, provenance_report.json, operator_statistics.json |

## Falsification Results (in falsification/)
| File | Test | Result |
|------|------|--------|
| test_01_result.json | Adaptive Localization | INCONCLUSIVE |
| test_02_result.json | Babylonian ↔ Fourier | INCONCLUSIVE |
| test_03_result.json | Convergent Evolution MSC | FAIL |
| test_04_result.json | Goodhart ↔ No-Cloning | FAIL |
| test_05_result.json | Reasoning Precipitation | INCONCLUSIVE (GPU) |
| test_06_result.json | Walls of Time | FAIL |
| test_07_result.json | Topology-Dependent Concentration | PASS |
| test_08_result.json | Arrow ↔ Map Projection | FAIL |
| test_09_result.json | Resolution Algebra | FAIL |
| test_10_result.json | Depth Convergence | PASS |
| test_11_result.json | AIECS Thermodynamics | INCONCLUSIVE (GPU) |
| test_12_result.json | Geometry of Impossibility | PASS |
| test_13_result.json | Cross-Cultural Mathematics | FAIL |
| test_14_result.json | States vs Trajectories | CONDITIONAL PASS |
| test_15_result.json | 11 Structural Primitives | FAIL |

## Journal
| File | Date | Content |
|------|------|---------|
| journal/2026-03-30-building-exploration.md | 2026-03-30 | Floors 2-4 exploration, Tucker completion, cross-floor analysis |

## Key Metrics (post-audit, verified with SQL)
| Metric | Value | Source |
|--------|-------|--------|
| Floor 1 fill (no op_remap) | 2,120/2,124 (99.8%) | floor1_matrix (DAMAGE_OP tags + edges only) |
| Floor 1 HIGH confidence | 184/2,120 (8.7%) | floor1_matrix WHERE confidence='HIGH' |
| Floor 2 fill (evidence only) | 246/30,916 (0.8%) | tradition_hub_matrix WHERE status='FILLED' |
| Floor 3 fill (derived from clean F1) | 18,813/19,116 (98.4%) | depth2_matrix WHERE status='FILLED' |
| Council-only spokes | 246/4,702 (5.2%) | composition_instances WHERE provenance='council_original' |
| Predictions verified | 48/78 EXACT (61.5%) | expanded_prediction_verification.json — SELF-REFERENTIAL |
| CONCENTRATE vs HIERARCHIZE (F1) | 0.569 | floor1_matrix weighted correlation |
| CONCENTRATE vs HIERARCHIZE (F3) | 0.626 | depth2_matrix op1 prefix correlation |
| op_remap contamination | ELIMINATED | No primitive-to-operator mapping in any production path |

## Audit Findings (2026-03-30)
- 61.5% hit rate: recovered from expanded_prediction_verification.json. 48/78 EXACT. Fully self-referential (Machine 3 graded its own homework). NOT citable without external validation.
- op_remap: found in 3 production scripts, all replaced by evidence-only versions.
- 9 production scripts from prometheus-research/noesis/v2/ copied to audit/scripts/ for Athena.
- All verification source files copied to audit/data/.
