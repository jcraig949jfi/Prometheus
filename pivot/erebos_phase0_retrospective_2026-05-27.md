# Erebos v3 Phase 0 Retrospective (ITER-21 → ITER-30)

**Date:** 2026-05-27
**Author:** Charon
**Phase status:** Complete. 9 discipline primitives shipped + integration tests + retrospective. Substrate at v0.36, ready for Phase 1 (architecture proofs).

---

## What Phase 0 was for

Per v3 §0 ("Why v3, not v2"): the four-frontier-model critique made the per-plugin tuning path obsolete. The substrate's architectural assumptions needed re-examination before more refinement was justified. The 22-DR convergence then surfaced FIVE recurring loader-implementation anti-patterns (arbitrary-scalar selection, hardcoded thresholds, ungated degeneracy, single-verdict-not-curve, syntactic-where-structural).

Phase 0 was the discipline-enforcement layer that prevents future plugin retrofits from defaulting back into the v1 anti-patterns. Without Phase 0, even a v3 "retrofit G05" would silently regress.

## What shipped

| ITER | Primitive | Commit | Tests | DR anti-pattern addressed |
|---|---|---|---|---|
| 21 | `selection_discipline.py` | `4b27c25e` | +21 | A — arbitrary-scalar selection |
| 22 | `catalog_profile.py` | `1b8e4ebf` | +25 | B — local geometry ignored at thresholds |
| 23 | `degeneracy_precondition.py` | `b3d8a2bb` | +24 | C — triviality not gated upstream |
| 24 | `SurvivalCurve` emission type | `55b51b5d` | +14 | D — single-verdict instead of curve |
| 25 | `predicate_handle` field | `9c0dc88f` | +20 | E — syntactic where structural |
| 26 | `kill_pattern_registry.py` (27 rows) | `b53038f0` | +25 | v3 §4.4 (kill_pattern semantics) |
| 27 | Cost-instrumentation layer | `696d63cf` | +19 | v3 §4.5 (epistemic economy) |
| 28 | Loader-debt budget + 11-plugin quarantine | `c7b8b053` | +21 | v3 §4.8 (debt budget) |
| 29 | Three-tier finding reclassification | `1f24953f` | doc | v3 §4.10 (honest evidence) |
| 30 | Phase 0 integration tests + this doc | next | +7 | wrap |

**Test count: 470 → 621 (+151 across 10 iterations).** All 595 prior tests still pass.

## What the substrate has now that v1 didn't

Each of the five DR anti-patterns is now blocked at the contract layer, not at the convention layer:

1. **Arbitrary-scalar selection** — loaders that select from >1 candidate without declaring a `SelectionMetric` raise `ArbitraryScalarSelectionError`. Future G06/G09/G10/G11/G16/G18 retrofits cannot copy the v1 first-alphabetical / random / argmax-scalar pattern.
2. **Hardcoded thresholds** — `catalog_profile(domain).{property}` provides data-driven epsilon / percentile / bootstrap CI replacements. Loaders that hardcode constants will need to be retrofitted to use `epsilon_band_for(domain)` etc.
3. **Degenerate (data, inquiry) firing** — `degeneracy_report(data, inquiry, feature_extractor)` produces a `DegeneracyReport`; `gate(report)` raises `DegenerateInputError` if any of the three orthogonal axes (Kish n_eff, Shannon entropy, tail concentration) trips. The G11 v1 Salem-cluster tautology is a regression test that locks in: future plugins cannot re-introduce the same pathology silently.
4. **Single-verdict instead of curve** — `SurvivalCurve` dataclass with phase-transition detection promotes the ITER-17 / ITER-18 sweep discipline from one-off refinement to substrate-level convention. The ITER-18 G17 M=1.26 finding is a regression test (`test_iter18_g17_phase_transition_at_M_1_26_recovered`).
5. **Syntactic-where-structural** — `ComposedClaim.predicate_handle: Optional[PredicateHandle]` carries machine-evaluable substrate alongside claim text. `MahlerPolynomialHandle` fully implemented (covers G03/G11/G18/G24); the ITER-10 G18 cyclotomic-extension false-positive is now a regression test (`test_mahler_handle_lehmer_x_phi_16_is_cyclotomic_extension_of_lehmer`). M3 → M4 representation lift on the Reasoning Ladder.

Plus four cross-cutting primitives:

6. **Kill_pattern routing semantics** — the 27-row `kill_pattern_registry.KILL_PATTERN_REGISTRY` turns named labels into machine-actionable routing decisions: `routing_action_for(kp)` returns the next-plugin string. F-axis tier + confusion class + observable signature + assignment provenance per kp.
7. **Closed-loop epistemic economy** — `ComposedClaim` carries `generation_cost_seconds`, `falsification_cost_seconds`, `information_gain_nats`, `reuse_value_count`. `value_per_tick` metric computable on the ledger; Sprint-1 baseline measurable.
8. **Loader-debt budget** — `MAX_PENDING_EMISSIONS = 200` and `MAX_QUARANTINE_DAYS = 30` enforced. 11 of 25 plugins QUARANTINED (7 loader_missing + 3 infrastructure_blocked + 1 vacuous_by_design). `applicable_plugins(state)` filters quarantined plugins out of production runs.
9. **Finding reclassification** — 7 prior substrate findings reclassified: 2 substrate + 6 catalog + 0 mathematical + 0 literature-grade. Whitepaper Section 5 rewritten. Evidence base now matches honest epistemic state.

## What Phase 0 caught (3 substrate self-correction events during Phase 0 itself)

The discipline-building work surfaced 3 of its own bugs before commit, which proves the substrate's test discipline is working:

1. **ITER-21 selection_discipline test bug** — test used DISTANCE_MINIMIZING on scalar_axis_value, but registry only accepts PERCENTILE_BASED for that data type. Test caught the registry-test mismatch before it shipped.
2. **ITER-23 degeneracy_precondition Kish-on-counts bug** — initial implementation ran Kish formula on class counts instead of item weights, giving n_eff=4 for uniform 100-item population. Test caught it; fixed to default `n_eff = sum(distribution)` when weights is None.
3. **ITER-30 integration test palindromic-bug** — `(1, 0, -1)` is anti-palindromic, not palindromic. Test caught the conceptual error; fixed to `(1, 0, 1)`.

These are all Type-A events (test caught bug automatically) per ChatGPT's Type-A-through-E taxonomy. The substrate now has a test infrastructure that produces Type-A events at the discipline layer, which is exactly the property the v3 critique demanded.

## What Phase 0 did NOT do

Per v3 §6 + amendment §6 honest demarcation:

- **Phase 0 did not perform the ledger-memory ablation harness** (that's Phase 1 §4.1).
- **Phase 0 did not perform the plugin degeneracy audit** (Phase 1 §4.2). Quarantine in §4.8 reduces 25 → 14 active plugins, but the operational degeneracy audit (Jaccard on inputs/payloads/kill_patterns/downstream) is a separate Phase 1 deliverable.
- **Phase 0 did not retrofit any plugin's loader to the new primitives.** All 22 existing composition loaders still pre-date the discipline layer. Phase 1 will retrofit a small subset as proof-of-concept; full retrofit is Phase 3+ conditional on Sprint-1 pass.
- **Phase 0 did not enable kill_pattern-driven routing** in the daemon. The registry exists; the executor's force-import list still uses round-robin tier priority. Wiring is Phase 1.
- **Phase 0 did not ship the cost-instrumentation in the daemon loop.** The `ComposedClaim` fields exist; the daemon must wrap `plugin.generate()` and loader execution with `time.perf_counter()` to populate them. Wiring is Phase 1.
- **Phase 0 did not ship the second-domain MVP loader** (Phase 1 §4.6). BSD-context infrastructure work is the natural next iteration.

## Substrate state at Phase 0 end

```
Substrate version:     v0.36
REGISTRY size:         25 plugins
Active in production:  14 plugins
Quarantined:           11 plugins (7 loader_missing + 3 infra_blocked + 1 vacuous)
Composition loaders:   22
Tests passing:         621 (was 470 at Phase 0 start; +151 across 9 primitives + integration)
Substrate findings:    2 (G10 boundary, G15 self-audit)
Catalog findings:      6
Mathematical findings: 0
Literature-grade:      0
Documents in v3 stack:
  - pivot/erebos_whitepaper_v1_2026-05-27.md (§5 rewritten)
  - pivot/erebos_v3_synthesis_2026-05-27.md
  - pivot/erebos_v3_amendment_dr_synthesis_2026-05-27.md
  - pivot/erebos_v3_phase0_implementation_plan_2026-05-27.md
  - pivot/erebos_quarantine.md
  - pivot/erebos_finding_reclassification_2026-05-27.md
  - pivot/erebos_phase0_retrospective_2026-05-27.md (this doc)
  - aporia/docs/erebos_v3_dr_synthesis_batch{1..5}_*.md
```

## Phase 1 entry conditions (ITER-31 onward)

Per v3 amendment §6 re-prioritized roadmap:

**Phase 1 — Architecture proofs (ITER-31 → ITER-40, ~10 iterations):**

1. Ledger-memory ablation harness (v3 §4.1)
2. Plugin degeneracy audit + retirement criteria (v3 §4.2)
3. Earned-tier protocol — declared / executed / observed / downstream (v3 §4.3)
4. BSD MVP loader (v3 §4.6 — moved earlier; required for Sprint-1 A8)
5. Daemon wire: cost-instrumentation populates emission fields
6. Daemon wire: kill_pattern_registry drives next-plugin routing
7. Retrofit ONE plugin's loader to the new primitives as proof-of-concept (likely G02 or G10, both well-tested and high-traffic)

**Phase 2 — Sprint-1 self-falsification (ITER-41 → ITER-50, ~10 iterations):**
- All 10 ablation experiments per v3 §5
- ITER-50 decision against v3 §6 kill conditions

**Phase 3+ — Conditional on Sprint-1 pass:**
- Per-plugin v3 retrofits using the 22 DR outputs
- OEIS / NF MVP loaders
- Composition-payload schema mobility deeper than `predicate_handle`
- Learner integration spec (DEMOTED IN PRIORITY because writing it before §3.5 ships locks in wrong loss-function shape)

## Open questions Phase 0 did not answer

Per v3 §8 — unchanged by Phase 0:

1. Goodhart-on-kill_patterns deepening. The §4.4 routing semantics layer helps but does not eliminate.
2. OEIS "interestingness" filter for sleeping beauties.
3. Compounding epistemic rot in long routing chains.
4. ATP backend for proof.
5. Type-E autonomous repair (Phase 0's self-correction events are all Type A).
6. Lethe LLM-contamination question.

These are explicitly deferred. v3 admits them rather than performing a solution.

## Calibration check

Per `feedback_calibration` + `feedback_assume_wrong`:

- Phase 0 shipped engineering scaffolding, not findings.
- The substrate's claim shifted from "produces substrate-grade mathematical structure" (v1 framing) to "produces empirically-routed verdicts with documented kill-condition discipline" (v3 framing). The second framing is what the evidence supports.
- The discipline layer is necessary but not sufficient for Sprint-1 pass. Sprint-1's 10 ablation experiments are the actual test of whether the substrate has value.
- No additional substrate findings emerged during Phase 0. The 3 self-correction events are substrate-engineering wins, not substrate-mathematics wins.

Per `feedback_take_a_stand`: Phase 0 was a build commitment, not a research deliverable. It is complete. Phase 1 begins.

---

**End Phase 0 retrospective.** Next: ITER-31 begins Phase 1 architecture proofs.
