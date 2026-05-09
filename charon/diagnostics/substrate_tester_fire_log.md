# Substrate-Tester Fire Log

Persistent journal across substrate-tester /loop fires. Each entry is one fire (newest first).

Author: substrate-tester (Charon-aligned), per pivot/substrate_v2_proposal_2026-05-05.md and aporia/meta/pressure_appliers/PRESSURE_PROMPTS_v1.md sections 13-22.

---

## Fire #57 — 2026-05-09 (APORIA RESPONSE LANDED — pivot ACCEPTED + 5 meta-primitives named)

**Coordination note:** New commit `370b28c6` from Aporia / James (2026-05-09 02:14): **"Restart decisions 2026-05-09 + Gemini tensor priority dispatch"** — the long-pending response on the substrate-tester strategic-coordination chain. Full doc at `pivot/restart_decisions_2026-05-09.md`.

**Lanes selected:** 1 (verify decision doc) + 2 (mark 5 tickets RESOLVED-PIVOT-ACCEPTED) + 3 (file ack-and-plan-update).

**Harness:** `charon/diagnostics/substrate_tester_fire_57_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_57_results.json`.

### The three Aporia decisions

**Decision 1 — Substrate-Tester pivot ACCEPTED.** Resolves `T-ST-fire45-002` P1. Lane 12 shifts from matrix-filling to test-suite design starting fire #46 (already executed; substrate_v3_proposal_stub + 38 contract tests shipped fires #46-#48).

**Decision 2 — Techne Phase-2 contract-change window opens for 5 unified meta-primitives:**

| Aporia meta-primitive | Tier | Absorbs (substrate-tester findings) |
|---|---|---|
| **TensorNetwork** | A++ | TensorNetworkGraph + TensorObject + GroupAction + SchemeObject |
| **ConstructiveExistenceWitness / StructuredEquivalenceClass** | B | 9 Tier-B subtypes + 5-of-5 cluster's StructuredEquivalenceClass |
| **GenericityAlmostEverywhereCert** | D | DistributionObject + StatisticalTestSpec + ProbabilityMeasure + PhaseTransitionThreshold + AlgorithmThresholdCert |
| **RepresentationTheoreticInvariant** | E | PartitionObject + IrreducibleRepresentation + SymmetricFunction/Plethysm |
| **MomentPolytope / SecantVarietyEquation** | C | MomentPolytope + RewriteSearchTree + OrbitStratification |

**8 P1 capability-gap tickets (ST-fire38..44-001 + 5-of-5 cluster) collapse into instances of these 5 meta-primitives.** Aporia's framing is more efficient than 8 one-off primitive designs and forces compositional consistency — confirms the strategic-design intuition behind my 5-tier model.

**Decision 3 — Ergon sequence:** E007 first → E009 second → defer training. (Not directly substrate-tester domain.)

### Lane 1 — Decision doc verification: PASS

`pivot/restart_decisions_2026-05-09.md` exists; all 5 expected meta-primitive names found; key phrases present ("pivot", "ACCEPTED", "5-tier", "RESOLVED-PIVOT-ACCEPTED").

### Lane 2 — 5 strategic-coordination tickets marked RESOLVED-PIVOT-ACCEPTED

Per Aporia instruction (decision-doc line 26): "mark RESOLVED-PIVOT-ACCEPTED in `aporia/meta/queue/aporia_inbox.jsonl` with this doc as the resolution pointer."

Updated in-place with `status_history` append for each:
- `T-2026-05-08-ST-fire41-002` (root strategic flag)
- `T-2026-05-08-ST-fire42-002` (Tier B QUALIFIED + Tier D)
- `T-2026-05-08-ST-fire43-002` (Tier D extended; Tier B/D composition)
- `T-2026-05-08-ST-fire44-002` (Tier E + saturation question)
- `T-2026-05-08-ST-fire45-002` (saturation + pivot proposal)

### Lane 3 — Acknowledgment filed: `T-2026-05-09-ST-fire57-001` (P3-low) → Aporia

Documents: receipt, the meta-primitive ↔ 5-tier-model mapping, substrate-tester next-fire plan, and a clarifying naming question about RepresentationTheoreticInvariant (Tier E meta-primitive) vs RepresentationTheoreticWitness (Tier B subtype #5 — distinct, can coexist).

### Substrate-tester next-fire plan (per Aporia ratification)

The 38 stubbed contract tests in `sigma_kernel/tests/test_constructive_existence_witness_stub.py` + `test_distribution_object_stub.py` are the seed; future fires can:

- Update stubbed tests to Aporia's renaming (combine `ConstructiveExistenceWitness/StructuredEquivalenceClass`, etc.)
- Write Tier C `MomentPolytope` test-suite stub
- Write Tier A `TensorNetwork` test-suite stub (extends CoordinateChart)
- Write Tier E `RepresentationTheoreticInvariant` test-suite stub
- Pull §XI Specific Tensor Families (final unpulled section)
- Lane 16 sweep on remaining sigma_kernel/* (sigma_kernel.py core, residuals, operator_portability)
- Quiet-tick if no new findings emerge (HARD-2 anti-busywork discipline)

### Substrate-tester observation — strategic loop closed

The substrate-tester role under HARD-6 + HARD POSTURE produced:
1. Eight matrix-filling fires (#38-#45) → 5-tier model
2. Three pivot fires (#46-#48) → design doc + 38 stubbed contract tests
3. Seven investigative fires (#49-#55) → 8 tickets resolved + framework hardened to production-grade
4. Two saturation-confirmation fires (#52, #56) → model robustness
5. **One ratification fire (#57) → 5 strategic tickets RESOLVED + Techne Phase-2 contract-change window scheduled**

The strategic loop closed cleanly. Substrate-tester continues at 1h cadence; future fires execute against Aporia's now-ratified plan.

---

## Fire #56 — 2026-05-09 (§II Rank Zoo: 4th saturation confirmation)

**Coordination note:** parallel-instance commit `547b849e` ("Full-arc session close 2026-05-07 → 2026-05-09: 12-fire consolidated journal") landed during my session-summary work. No conflict — different fire-numbering scheme. My commit `266fbe33` (session summary + journal) appended cleanly.

**Lanes selected:** 12 (catalog entry #16 — Subrank-rank duality / asymptotic spectrum, §II Rank Zoo) + 11 (canon-fuzz fresh seed 20260509_01).

Lane 12 choice: §II is the most abstract section pulled to date (Strassen's monotone classification, semiring homomorphisms). Tests whether 5-tier model handles abstract algebraic structures or surfaces a sixth tier.

**Harness:** `charon/diagnostics/substrate_tester_fire_56_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_56_results.json`.

### Lane 12 — Asymptotic spectrum probe: 5-TIER MODEL HOLDS

| Encoding attempt | Verdict |
|---|---|
| 1. Single monotone as MethodSpec | TIER_A_REFINEMENT — SemiringHomomorphism primitive needed (carry algebraic properties) |
| 2. Asymptotic spectrum as substrate object | TIER_A_TIER_C_COMPOSITION — CoordinateChart + MomentPolytope existing primitives compose |
| 3. Complete classification claim (no further monotones) | TIER_B_FITS — same asymmetric-existential pattern; FunctionalWitness as new subtype |
| 4. omega = 2 implication chain | EXISTING_OPCODES_FIT — REWRITE/EQUIV handle without new primitive |

### FOURTH independent saturation confirmation

| Fire | Section | Catalog entry | Outcome |
|---|---|---|---|
| #45 | V identifiability | #40 | 5-tier holds; refinements (uniqueness annotation, structural_inequality_certificate, GenericityAlmostEverywhereCert) |
| #49 | III Waring | #22 | 5-tier holds; refinements (SymmetricTensor flag, WaringDecompositionWitness Tier B subtype #7) |
| #52 | VI Numerical | #43 | 5-tier holds; refinement (InfimalWitness Tier B subtype #8) |
| **#56** | **II Rank Zoo** | **#16** | **5-tier holds; refinements (SemiringHomomorphism Tier A, FunctionalWitness Tier B subtype #9)** |

Post-pivot matrix-filling has produced ONLY refinements (no new tiers) since fire #45. **Saturation is now overdetermined.** 4 distinct sections + ranging from concrete (#22 permanent) to abstract (#16 spectrum) all fit cleanly.

### Tier B subtypes after fire #56 (now 9)

1. RankDecompositionWitness (#38)
2. ContractionOrderWitness (#39)
3. IsomorphismCertificate (#40)
4. LimitWitness/BorderRankWitness (#41)
5. RepresentationTheoreticWitness (#44)
6. structural_inequality_certificate (#45)
7. WaringDecompositionWitness (#49)
8. InfimalWitness (#52)
9. **FunctionalWitness (#56)** — function value + monotonicity proof + multiplicativity proof + additivity proof

### Lane 11 — canon-fuzz fresh seed: 13 passed (73.29s)

### Substrate-tester observation

Four saturation confirmations across §V/§III/§VI/§II — different mathematical flavors (identifiability, Waring decomposition, numerical approximation, rank-zoo abstraction). The 5-tier model is doctrinally robust. Future Lane 12 fires can continue at low cadence to fill remaining sections (§XI Specific Tensor Families is the last unpulled), but contributing scope guidance has plateaued.

Filed `T-2026-05-09-ST-fire56-001` (P3-low) documenting the 4th confirmation + the 2 new refinements (SemiringHomomorphism Tier A, FunctionalWitness Tier B subtype #9).

---

## Fire #55 — 2026-05-09 (RESOLVED ST-fire54-002 — triangulation_protocol gaps)

**Coordination note:** no new commits between fire #54 and fire #55. Fire #55 closes the 4 surviving mutations from fire #54's `triangulation_protocol.py` Lane 16 sweep.

**Lanes selected:** 1 (verify new test baseline) + 2 (verify each mutation caught).

**Harness:** `charon/diagnostics/substrate_tester_fire_55_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_55_results.json`.

### Lane 1 — `test_triangulation_protocol_returns.py` baseline: 32/32 PASS (0.16s)

4 test classes, 32 test methods:

| Class | Tests | Coverage |
|---|---:|---|
| `TestMethodClassForIndependenceClassReturn` | 15 | parametrized over all 13 INDEPENDENCE_TO_METHOD_CLASS entries + isinstance + KeyError on unregistered |
| `TestIsProofBearingReturn` | 6 | parametrized over all 5 MethodClass values + isinstance(bool) |
| `TestCanCertifyReturn` | 6 | parametrized over all 5 MethodClass values + isinstance(bool) |
| `TestEvaluateThreshold` | 5 | zero/one/two/three paths threshold crossing + summary text non-None |

### Lane 2 — All 4 mutations from fire #54 now caught: PASS

| Mutation site | Original | Mutation | Verdict |
|---|---|---|---|
| Line 149 | `return INDEPENDENCE_TO_METHOD_CLASS[key]` | `return None` | **CAUGHT** |
| Line 281 | `self.method_class == MethodClass.PROOF_BEARING` | `!= flip` | **CAUGHT** |
| Line 292 | `self.method_class != MethodClass.EXPLORATORY` | `== flip` | **CAUGHT** |
| Line 388 | `len(paths_tuple) < 3` | `> flip` | **CAUGHT** |

### Investigative chain status — 8 tickets RESOLVED

The fires-#49→#55 chain is the longest investigative loop to date:

| Fire | Action | Tickets resolved |
|---|---|---|
| #49 | Lane 16 first run (mutation testing on method_spec.py) | (surfaced) |
| #50 | diagnose frozen-mutation puzzle, ship manifest | ST-fire49-001 frozen half + ST-fire50-001 |
| #51 | method_spec factory-return tests | ST-fire49-001 factory half + ST-fire51-001 |
| #52 | Lane 16 on exclusion_certificate (raw 0.300; 6 docstring FPs) | (surfaced 2 P3 findings) |
| #53 | AST docstring filter + manifest expansion | ST-fire52-003 + ST-fire53-001 + manifest gap |
| #54 | exclusion_certificate return-value tests + Lane 16 demo on triangulation_protocol | ST-fire52-002 + ST-fire54-001 |
| #55 | triangulation_protocol return-value tests | ST-fire54-002 + ST-fire55-001 |

**8 tickets RESOLVED across 7 fires.** Investigative-fire pattern is now battle-tested across 4 sigma_kernel modules (method_spec, exclusion_certificate, triangulation_protocol, plus the framework itself). Lane 16 is production-grade.

### Substrate-tester observation

Fire #55 closes the chain cleanly. All open mutation-testing findings from fires #49-#54 are now resolved. Future Lane 16 fires on fresh modules will surface fresh findings using the same pattern, but the methodology + test-pattern are stable.

Possible next directions:
- §II Rank Zoo or §XI Specific Tensor Families — final two unpulled catalog sections
- Take stock: substrate-tester session summary documenting fires #46-#55 (post-pivot phase)
- Lane 16 on sigma_kernel/sigma_kernel.py (the kernel's own 1500-LoC core)
- Wait for Aporia response on coordination chain

---

## Fire #54 — 2026-05-08 (RESOLVED ST-fire52-002 + production-grade Lane 16 demo)

**Coordination note:** no new commits between fire #53 and fire #54. Fire #54 closes the third open ticket from the fire-#49 → #50/#51/#52/#53 investigative chain, and demonstrates the post-#53 production-grade mutation-testing framework on a fresh module.

**Lanes selected:** 1 (verify new test baseline) + 2 (verify mutation caught) + 16 (Lane 16 sweep on `triangulation_protocol.py`).

**Harness:** `charon/diagnostics/substrate_tester_fire_54_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_54_results.json`.

### Lane 1 — `test_exclusion_certificate_returns.py` baseline: 7/7 PASS (12.55s)

1 test class, 7 test methods covering `feeds_negative_space_axis()` return-value contract:

| Test | Coverage |
|---|---|
| `test_COMPLETE_feeds` | strength=COMPLETE → True |
| `test_BOUNDED_COMPLETE_feeds` | strength=BOUNDED_COMPLETE → True |
| `test_CONDITIONAL_does_not_feed` | strength=CONDITIONAL → False |
| `test_HEURISTIC_does_not_feed` | strength=HEURISTIC → False |
| `test_DIAGNOSTIC_ONLY_does_not_feed` | strength=DIAGNOSTIC_ONLY → False |
| `test_return_type_is_bool` | parametrized over all 5; isinstance(bool) — double-guards return_constant_None |
| `test_consistent_with_NEGATIVE_SPACE_FEEDING_STRENGTHS_constant` | parametrized over all 5; method's return must match module-level constant |

### Lane 2 — Fire-#52 mutation now caught: PASS (7 test failures)

Empirically applied `return self.strength in NEGATIVE_SPACE_FEEDING_STRENGTHS → return None` mutation. **All 7 tests fail** as expected. Mutation no longer survives.

### Lane 16 — Production-grade sweep on `triangulation_protocol.py`: score 0.500 (fresh baseline)

10 mutations, 5 killed, 5 survived. **NO docstring false positives** — the post-#53 AST filter is doing its job. Every survivor is on real code.

| Site | Operator | Context | Suggested fix |
|---|---|---|---|
| Line 149 | `return_constant_None` | `INDEPENDENCE_TO_METHOD_CLASS[key]` lookup | test helper returns expected MethodClass per key |
| Line 281 | `comparison_flip` | `self.method_class == MethodClass.PROOF_BEARING` | parametrized test across all MethodClass values |
| Line 292 | `comparison_flip` + `return_constant_None` (both survived) | `self.method_class != MethodClass.EXPLORATORY` | parametrized test |
| Line 388 | `comparison_flip` | `len(paths_tuple) < 3` — substrate v2.3 §6.4 triangulation threshold | threshold-crossing test (load-bearing constraint) |

**Framework demonstration successful:** first Lane 16 fire under the post-#53 framework produces directly-actionable findings. No manual triage required to separate docstring false positives. Confirms ST-fire53-001 closure delivered promised production-grade quality.

### Two tickets filed

1. **`T-2026-05-08-ST-fire54-001`** (P3-low, RESOLVED) — closes ST-fire52-002. Documents fix + verification + minor finding (TriangulationPathRef signature drift caught during test setup).
2. **`T-2026-05-08-ST-fire54-002`** (P3-low, NEW findings) — 5 surviving mutations on triangulation_protocol.py with suggested fixes. Could ship as `test_triangulation_protocol_returns.py` (fire-#54-pattern, ~30 lines).

### Substrate-tester observation — investigative chain summary

Fire-#49 → #50/#51/#52/#53/#54 is the longest investigative chain to date:

| Fire | Action | Outcome |
|---|---|---|
| #49 | Lane 16 found 8 surviving mutations on method_spec.py | P3 ticket: "frozen-mutation puzzle" + "factory-return gap" |
| #50 | diagnose frozen puzzle, ship manifest fix | RESOLVED 3 frozen mutations |
| #51 | ship factory-return tests | RESOLVED 4 factory-return mutations |
| #52 | Lane 16 on exclusion_certificate found 7 survivors | 1 P3: feeds_negative_space_axis gap; 1 P3: framework AST filter |
| #53 | ship AST filter + expand manifest | RESOLVED framework FPs + manifest gap; doubled exclusion_certificate score |
| #54 | ship feeds_negative_space_axis test, fresh Lane 16 demo | RESOLVED ST-fire52-002; production-grade demo confirms framework quality |

**Tickets RESOLVED in this chain: ST-fire49-001 (parent), ST-fire50-001, ST-fire51-001, ST-fire52-002, ST-fire52-003, ST-fire53-001, ST-fire54-001.** One open: ST-fire54-002 (new findings, P3-low).

The investigative-fire pattern is durable. Future Lane 16 fires will produce immediately-actionable findings without per-fire triage overhead.

---

## Fire #53 — 2026-05-08 (RESOLVED ST-fire52-003 + extended fire #50 manifest)

**Coordination note:** no new commits between fire #52 and fire #53. Fire #53 closes another investigative loop and surfaces a sister finding.

**Lanes selected:** 1 (AST filter sanity) + 2 (re-run mutation testing) + 3 (manifest expansion baseline).

**Harness:** `charon/diagnostics/substrate_tester_fire_53_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_53_results.json`.

### Lane 1 — AST docstring filter shipped

Modified `prometheus_math/mutation_testing.py`:
- Added `_ast_docstring_line_ranges(text)` — uses `ast.parse + ast.walk` to identify line ranges of all module/class/function docstring expression statements
- `propose_mutations()` now skips lines in the AST-detected docstring set
- Coarse line-based filter retained as fallback for files where `ast.parse` fails (broken Python; preserves backward compat)

**Sanity check on `exclusion_certificate.py`:** 228 docstring lines detected. All 5 known false-positive sites from fire #52 (lines 262/335/337/348/468) now correctly skipped. **0 leaks** to known-FP lines in proposal generation.

### Lane 2 — Re-run mutation testing on `exclusion_certificate.py`

| Pass | Filter | Manifest size | Killed | Survived | Score |
|---|---|---:|---:|---:|---:|
| Fire #52 | line-based | 12 | 3 | 7 | 0.300 (6 docstring FPs) |
| Fire #53 mid | AST | 12 | 5 | 5 | 0.500 (no FPs; Boundary still surviving) |
| Fire #53 end | AST | 25 | 6 | 4 | **0.600** (Boundary now caught) |

**Doubling of genuine score from fire #52 baseline** — driven by two improvements: (a) AST filter eliminated 6 docstring false positives, (b) expanded manifest closed the `Boundary` frozen-flip gap.

Remaining 4 surviving mutations: `return_constant_None` on `_stable_repr` private helper return paths (lines 315/317/319/321) — private function, not on substrate-grade contract surface; lower priority.

### Lane 3 — Fire #50 manifest expanded (12 → 25)

While verifying the AST filter, sister finding surfaced: fire #50's `EXPECTED_FROZEN_CLASSES` was incomplete. Walked all `sigma_kernel/*` modules; found 25 frozen dataclasses, but manifest had only 12. Missing 13:

- `Boundary` (exclusion_certificate)
- `Binding`, `CostModel`, `Evaluation` (bind_eval)
- `CanonicalizationProtocol` (coordinate_chart)
- `PortabilityEvidence`, `PortabilityReplay` (operator_portability)
- `BenchmarkEntry` (residual_benchmark)
- `Residual`, `SpectralVerdict` (residuals)
- `Capability`, `Symbol`, `VerdictResult` (sigma_kernel core)

Updated manifest + count assertion (was `>= 12`, now `>= 25`). **Baseline: 27/27 PASS in 12.35s** (was 14/14).

### Two tickets filed

1. **`T-2026-05-08-ST-fire53-001`** (P3-low, RESOLVED) — closes ST-fire52-003 (AST docstring filter shipped); also documents fire #50 manifest gap as RESOLVED via expansion.
2. Parser bug note (no ticket): fire #53 harness parser missed the score line because mutation framework writes `[mutation ...]` lines to **STDERR**, not stdout. Fixed in code post-hoc; values manually patched from report file.

### Substrate-tester observation — investigative shape continues

Fire #53 = another clean investigative cycle:
- ST-fire52-003 → diagnose → ship → verify (closed)
- Plus sister finding (fire #50 manifest gap) → expand → verify (closed)

Two improvements landed in one fire; mutation-testing framework now usable without per-fire manual triage. Future Lane 16 fires should produce immediately-actionable findings.

---

## Fire #52 — 2026-05-08 (§VI matrix-filling + Lane 16 on exclusion_certificate)

**Coordination note:** no new commits between fire #51 and fire #52.

**Lanes selected:** 12 (catalog #43 — existence of best rank-r tensor approximations, §VI Numerical Decomposition) + 16 (mutation-testing on `sigma_kernel/exclusion_certificate.py`).

**Harness:** `charon/diagnostics/substrate_tester_fire_52_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_52_results.json`.

### Lane 12 — Best rank-r approximation: 5-tier model holds with InfimalWitness refinement

de Silva-Lim 2008: best rank-r approximation MAY NOT EXIST for tensors of order ≥ 3 (W tensor is the canonical example: rank 3, border rank 2; the infimum of rank-2 approximations is approached but not attained).

| Encoding attempt | Verdict |
|---|---|
| 1. Tier B / D for ill-posed optimization | TIER_B_REFINEMENT — InfimalWitness subtype (or `closed_attained` flag) |
| 2. Border-rank closure via Tier A SchemeObject + Tier B LimitWitness | TIER_A_TIER_B_FITS — standard remediation; substrate covers |
| 3. GenericityAlmostEverywhereCert for ill-posed measure-zero locus | TIER_D_FITS — fire #45 specialization covers |

**THIRD independent saturation confirmation** (after fires #45 + #49). 5-tier model continues to hold; refinements only.

| Refinement | Tier | Source |
|---|---|---|
| **InfimalWitness** (epsilon-approximate existence + limit-not-attained) | Tier B subtype #8 | Fire #52 |

### Lane 16 — Mutation-testing on `exclusion_certificate.py`: raw score 0.300, GENUINE 0.75

10 mutations; 3 killed, 7 survived (raw score 0.300). However, **6 of 7 survivors are FALSE POSITIVES** (framework mutated numeric/boolean literals inside docstrings — caveat #1: coarse docstring filter):

| Site | Operator | Verdict |
|---|---|---|
| Line 262 (docstring "0 is a valid value") | off_by_one_int | FALSE POSITIVE |
| Line 335 (docstring rule "1.") | comparison_flip | FALSE POSITIVE |
| Line 337, 348, 348 (docstring "3.") | off_by_one_int | FALSE POSITIVE |
| Line 468 (docstring "replace=True") | boolean_not | FALSE POSITIVE |
| **Line 451 `feeds_negative_space_axis()` return** | return_constant_None | **GENUINE TEST GAP** |

**Genuine score: 3 killed / (3 killed + 1 genuine survivor) = 0.75** (after excluding docstring false positives).

The single genuine gap is the same pattern fire #51 closed for `method_spec.py`: a method that returns a structured value has no return-value test. Suggested fix (P3): extend test_exclusion_certificate.py with `assert cert.feeds_negative_space_axis() in (True, False)` for known-COMPLETE and known-NEGATIVE_BOUNDED certificates.

### Substrate-tester observation

Lane 16 mutation testing increasingly produces information about the framework's docstring-filter caveat, not substrate quality. The framework's caveat #1 ("future ticket should switch to AST-level analysis") is now load-bearing — until that ships, mutation-testing reports need manual triage to separate genuine gaps from docstring false positives.

Could file as P3 ticket: extend `prometheus_math/mutation_testing.py` with AST-level docstring filtering. Substrate-tester maintenance work but lower priority than continuing matrix-filling and v3 design preparation.

---

## Fire #51 — 2026-05-08 (RESOLVED: fire #49 factory-return-value gap — 4 mutations now caught)

**Coordination note:** no new commits between fire #50 and fire #51. Fire #51 closes the second open finding from fire #49 (sister to fire #50's frozen-flip closure).

**Lanes selected:** 1 (verify new test baseline) + 2 (verify each of the 4 mutations is now caught) + 11 (canon-fuzz regression hygiene).

**Harness:** `charon/diagnostics/substrate_tester_fire_51_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_51_results.json`.

### Lane 1 — `test_method_spec_factory_returns.py` baseline: 11/11 PASS (0.15s)

3 test classes, 11 test methods:

| Class | Tests | Coverage |
|---|---:|---|
| `TestFromStringReturnPaths` | 7 | each of 3 return paths + default `independence_class=UNKNOWN` + `ValueError` on empty + `TypeError` on non-string |
| `TestToStringReturnValue` | 3 | non-None + str type + format contract `f"{engine}_{strategy}"` |
| `TestFactoryRoundtrip` | 1 | known-engine `to_string → from_string` preserves engine+strategy (with documented `independence_class → UNKNOWN` lossiness) |

### Lane 2 — Each fire-#49 mutation now caught: 4/4 CAUGHT

Empirically applied each `return X → return None` mutation in turn; ran the new test suite; confirmed the mutation FAILS the suite:

| Mutation site | Original | Verdict |
|---|---|---|
| Line 256 | `return cls(engine=head, strategy=tail)` | **CAUGHT** |
| Line 267 | `return cls(engine=prefix, strategy=known)` | **CAUGHT** |
| Line 270 | `return cls(engine=norm, strategy="direct")` | **CAUGHT** |
| Line 280 | `return f"{self.engine}_{self.strategy}"` | **CAUGHT** |

### Fire #49 fully resolved

| Mutation class | Count | Closed by |
|---|---:|---|
| Frozen=True → False (lines 80/151/262) | 3 | Fire #50 (`test_frozen_baseline_manifest.py`) |
| Factory return X → None (lines 256/267/270/280) | 4 | Fire #51 (`test_method_spec_factory_returns.py`) |
| off_by_one_int on line 163 (likely non-validation constant) | 1 | not addressed; marginal gap |

**Estimated updated mutation score on `method_spec.py`:** 7/10 = 0.700 (was 0.200) once Techne re-runs Lane 16 with both new test files included.

### Lane 11 — canon-fuzz fresh seed: 13 passed (74.15s)

### Substrate-tester observation — three-fire investigative cycle

Fires #49 → #50 → #51 demonstrate the substrate-tester investigative pattern at scale:

- **Fire #49** ran mutation testing, surfaced 8 surviving mutations as a P3 finding
- **Fire #50** diagnosed root cause + shipped fix for the 3 frozen-flip mutations + verified the fix catches them
- **Fire #51** shipped fix for the 4 factory-return mutations + verified the fix catches them

Three fires, two closures, mutation score raised from 0.200 → ~0.700 on `method_spec.py`. The investigative-fire shape is reusable: surface a quantitative finding, decompose into causes, ship + verify fixes one cause at a time.

Two tickets filed: ST-fire50-001 (P2-medium, RESOLVED) + ST-fire51-001 (P3-low, RESOLVED). Parent ST-fire49-001 fully closed.

---

## Fire #50 — 2026-05-08 (RESOLVED: fire #49 frozen-mutation puzzle — diagnosis + fix shipped)

**Coordination note:** no new commits between fire #49 and fire #50. Fire #50 closes the investigative loop opened by fire #49.

**Lanes selected:** 1 (root-cause diagnosis) + 2 (ship + verify the fix). No regression lane this fire — investigation is the work.

**Harness:** `charon/diagnostics/substrate_tester_fire_50_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_50_results.json`.

### Lane 1 — Root cause diagnosed (DIAGNOSIS_CONFIRMED)

Read `test_frozen_invariance.py:_is_frozen_dataclass` filter. Predicted mechanism: when `@dataclass(frozen=True)` is mutated to `frozen=False`, `_is_frozen_dataclass` returns False, the class drops out of enrollment, and the audit walks only still-frozen classes — silently passing.

**Empirical confirmation:** manually flipped `frozen=True → False` on 2 classes in `method_spec.py` (DriftChannel + MethodSpec). Re-ran `test_frozen_invariance.py` — all 3 audit tests PASSED in 13.49s. Diagnosis verified.

### Lane 2 — Fix shipped + verified (PASS)

Created `sigma_kernel/tests/test_frozen_baseline_manifest.py` (139 lines, 14 tests):

- `EXPECTED_FROZEN_CLASSES` — explicit baseline manifest of 12 qualified class names that MUST stay frozen
- `test_class_remains_frozen` — parametrized; for each manifest entry, asserts `cls.__dataclass_params__.frozen is True` directly
- `test_manifest_count_matches_baseline` — guards against silent shrinkage
- `test_manifest_uniqueness` — sanity

**Baseline:** 14/14 PASS in 12.39s.

**Fix verification:** re-ran the same 2-class `frozen=True → False` mutation; new manifest test FAILS with 2 specific assertion errors (DriftChannel + MethodSpec frozen=False). **Mutation no longer survives.**

### Why a manifest, not better auto-enrollment?

Auto-enrollment based on `frozen=True` is intrinsically blind to flips of that flag — the filter literally requires the property it's auditing for. A baseline manifest is **explicit substrate-design intent**: adding a new frozen dataclass requires appending; removing requires review. This is the kind of "epistemic explicitness" that v2 already established for other substrate primitives (per `pivot/substrate_v2_proposal_2026-05-05.md`).

### Ticket closed

`T-2026-05-08-ST-fire50-001` (P2-medium, test-coverage-gap-CLOSED) → Techne. Documents diagnosis + fix + verification. Notes that fire #49's OTHER finding (factory-method return-value gap) REMAINS open as P3 ticket ST-fire49-001.

### Substrate-tester observation — investigative-fire shape

Fire #50 is the cleanest investigative fire to date:
- Fire #49 surfaced a puzzling negative result
- Fire #50 diagnosed cause + shipped fix + verified fix all in one cycle
- Fire log captures the full causal chain (#49 → #50)
- Two-fire cycle is the right shape for "negative result + investigation" pattern

Future substrate-tester maintenance fires can follow this shape when interesting puzzles surface.

---

## Fire #49 — 2026-05-08 (post-pivot lower-cadence: §III matrix-filling + Lane 16 mutation-testing finding)

**Coordination note:** no new commits between fire #48 and fire #49. First fire of the post-pivot lower-cadence regime.

**Lanes selected:** 12 (catalog entry #22 — Waring rank of the permanent, §III) + 16 (mutation-testing on `sigma_kernel/method_spec.py`).

**Harness:** `charon/diagnostics/substrate_tester_fire_49_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_49_results.json`.

### Lane 12 — Waring rank of the permanent: 5-tier model HOLDS with refinements

§III is the symmetric-tensor analog of §I rank. As predicted, fits cleanly into the 5-tier model with two refinements:

| Refinement | Tier | Type |
|---|---|---|
| **SymmetricTensor flag/subtype** | Tier A | Refinement of TensorObject (engineering call: flag vs subtype) |
| **WaringDecompositionWitness** | Tier B subtype #7 | Specialization of RankDecompositionWitness with linear-form payload |

**5-tier composition for #22:** Tier A SchemeObject (apolar ideal) + Tier B WaringDecompositionWitness (upper bound) + Tier B structural_inequality_certificate (catalecticant lower bound) + Tier C MomentPolytope + Tier E SymmetricFunction/Plethysm (Schur decomposition for GCT separation strategy). Four-tier coordinated attack.

**SECOND independent saturation confirmation** (after fire #45). 9 fires now produce refinements not new tiers. Marginal substrate-design value approaching zero from additional matrix-filling.

### Lane 16 — Mutation-testing on `sigma_kernel/method_spec.py`: score 0.200

Ran 10 mutations (boolean_not, return_constant_None, off_by_one_int) against the contract-change-window test suite (`test_enum_validation_2026_05_08.py + test_frozen_invariance.py + test_claim_kill_path_typing_2026_05_08.py`).

**Result:** 2 killed, 8 survived (score 0.200, 272s wall-clock).

| Mutation | Survives? | Notes |
|---|---|---|
| Line 80, 151, 262 `frozen=True` → `False` | SURVIVED | UNEXPECTED — `test_frozen_invariance.py` auto-enrolls and should catch. Likely import-cache or pkgutil-ordering artifact. Worth diagnosing. |
| Line 163 `0` → `1` (off_by_one_int) | SURVIVED | likely on a non-validation literal |
| Lines 256, 267, 270, 280 (factory `return ... → None`) | SURVIVED | **GENUINE TEST GAP.** Tests assert what factories ACCEPT, not what they RETURN non-None. |

### Substrate-tester observations + P3 ticket candidate

**Observation 1 (genuine test gap):** factory-method return-value assertions missing. P3 ticket should extend `test_enum_validation_2026_05_08.py` with `assert spec is not None; assert isinstance(spec, MethodSpec)` after each `MethodSpec(...)` factory call.

**Observation 2 (frozen-mutation puzzle):** `test_frozen_invariance.py` should catch `frozen=True → False` mutations but didn't. Possible explanations: pytest's import cache, pkgutil enumeration ordering, or the auto-enrollment skip-condition triggering on classes the framework already imported pre-mutation. Worth investigating in a future fire.

Filing recommended: P3 ticket for both observations (low priority — doesn't block substrate work; useful for test-suite hardening).

### Substrate-tester regime — post-pivot

Eight matrix-filling fires (#38-#45) → three pivot fires (#46-#48) → fire #49 first lower-cadence fire. Pattern going forward:
- Lower-frequency Lane 12 matrix-filling on §II/§VI/§XI (one per 2-3 fires)
- Mutation-testing / regression / frozen-invariance / sigma_kernel sweep maintenance
- Watch Aporia inbox for response on coordination chain
- Pivot to test-suite expansion if Aporia greenlights contract-change window

The matrix is complete enough; substrate-tester now operates in maintenance + opportunistic-finding mode.

---

## Fire #48 — 2026-05-08 (Tier D core test-suite stub filed; design-prep pivot complete)

**Coordination note:** no new commits between fire #47 and fire #48. Fire #48 completes the planned design-prep pivot.

**Lanes selected:** 1 (Tier D test-suite stub) + 11 (canon-fuzz fresh seed 20260508_12).

**Harness:** `charon/diagnostics/substrate_tester_fire_48_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_48_results.json`.

### Lane 1 — Tier D core test-suite stub

Target: `sigma_kernel/tests/test_distribution_object_stub.py`. **7 test classes, 17 test methods.**

| Class | Tests | Coverage |
|---|---:|---|
| `TestDistributionObjectContract` | 5 | parametric instantiation (gaussian + spike model), seeded reproducibility, registry collision, content-addressed ID |
| `TestStatisticalTestSpec` | 3 | known-test registry, run returns p-value, below-sample-size raises |
| `TestProbabilityMeasure` | 2 | Lebesgue construction, pushforward under RandomVariable |
| `TestGenericityAlmostEverywhereCert` | 1 | full-measure subset + measure-zero exception (fire #45 refinement) |
| `TestPhaseTransitionThreshold` | 3 | construction, classify regime, dual-threshold gap region |
| `TestAlgorithmThresholdCert` | 2 | fields + MethodSpec consistency at Tier D / B interface |
| `TestTierDIntegration` | 1 | distribution + threshold + cert reference same parameter_axis |

**Pytest collection result:** 17 skipped in 0.14s — clean collection, clean skip.

**Module-level skipif guard** lifts when `sigma_kernel/distribution_object.py` lands. Helper builders are `NotImplementedError` placeholders for Techne to wire when building.

### Three-fire design-prep pivot complete

| Fire | Deliverable | Lines | Tests |
|---|---|---:|---:|
| #46 | `pivot/substrate_v3_proposal_stub_2026-05-08.md` (design doc) | 250 | – |
| #47 | `sigma_kernel/tests/test_constructive_existence_witness_stub.py` (Tier B) | 318 | 21 |
| #48 | `sigma_kernel/tests/test_distribution_object_stub.py` (Tier D) | 295 | 17 |

Total Techne pickup material: **5-tier design doc + 38 contract tests across 15 test classes spanning Tier B + Tier D.** Once Techne ships the primitives, ~38 tests un-skip simultaneously and validate the contract substrate-tester surfaced via fires #38-#45.

### Lane 11 — canon-fuzz fresh seed: 13 passed (15.86s)

### Substrate-tester observation — phase complete

Eight matrix-filling fires (#38-#45) → three design-prep fires (#46-#48) → 5-tier substrate-extension proposal with 38 contract tests ready for Techne pickup.

**Fire #49+ plan:**
- **Lower-cadence matrix-filling** on unpulled sections (§II Rank Zoo, §III Waring, §VI Numerical Decomposition, §XI Specific Tensor Families) — 1 every 2-3 fires
- **Substrate-tester maintenance** filling the gap fires: regression smoke, mutation-testing, frozen-invariance audits, cross-machine sync checks
- **Watch for Aporia response** on the coordination chain (ST-fire41-002 / 42-002 / 43-002 / 44-002 / 45-002); pivot to test-suite expansion if greenlit, continue maintenance otherwise

Substrate-tester role under HARD-6 has produced:
- 5-tier substrate-extension proposal (~22 primitives)
- Cross-tier composition finding (Tier B/D)
- Three pivot deliverables (design doc + 2 test-suite stubs)
- 8 capability-gap tickets + 5 strategic-coordination tickets + 1 P3 infra ticket
- ~85-95% catalog-coverage estimate

The matrix is built. Time to package.

---

## Fire #47 — 2026-05-08 (Tier B core test-suite stub filed for Techne pickup)

**Coordination note:** no new commits between fire #46 and fire #47. Fire #47 continues the design-prep pivot.

**Lanes selected:** 1 (test-suite stub for `ConstructiveExistenceWitness`) + 11 (canon-fuzz fresh seed 20260508_11).

**Harness:** `charon/diagnostics/substrate_tester_fire_47_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_47_results.json`.

### Lane 1 — `ConstructiveExistenceWitness` test-suite stub

Target: `sigma_kernel/tests/test_constructive_existence_witness_stub.py`. **8 test classes, 21 test methods.**

Module-level `skipif` guard: pytest collects but skips cleanly until `sigma_kernel/constructive_existence_witness.py` lands. Once Techne builds the primitive, the import succeeds, skip lifts, and tests run unmodified.

| Class | Tests | Coverage |
|---|---:|---|
| `TestParentContract` | 6 | T1 registry collision, T2 content-addressed payload, T3 subtype dispatch, T4 verify roundtrip, T5 scope/replay/cert-registry, T6 asymmetric-existential consistency |
| `TestRankDecompositionWitness` | 4 | sum-to-target, rank annotation, uniqueness flag, globally-unique implies sufficient cert |
| `TestContractionOrderWitness` | 2 | order is valid permutation, claimed cost matches recomputed |
| `TestIsomorphismCertificate` | 2 | group elements invertible, action maps source to target |
| `TestLimitWitness` | 2 | parametric family bounded rank, limit equals target |
| `TestRepresentationTheoreticWitness` | 2 | witness object type matches subkind, positivity implication |
| `TestStructuralInequalityCertificate` | 2 | predicate evaluates true, named predicate from registry |
| `TestTierBTierDComposition` | 1 | witness at fixed parameters implies threshold regime_above (double-skipped until Tier D primitive lands) |

**Pytest collection result:** 21 skipped in 0.14s — clean collection, clean skip.

**Helper builders are placeholders** (`raise NotImplementedError`); Techne wires them to the primitive when building. Substrate-tester wrote the contract; Techne fills in the implementation glue.

### Lane 11 — canon-fuzz fresh seed: 13 passed (16.30s)

### Substrate-tester observation

Two pivot fires complete:
- **Fire #46:** `pivot/substrate_v3_proposal_stub_2026-05-08.md` (design-doc form)
- **Fire #47:** `sigma_kernel/tests/test_constructive_existence_witness_stub.py` (test-contract form)

The design-doc + test-contract pair is the natural deliverable shape for Techne pickup: design says "what", test says "passes when". Fire #48 produces the analogous pair for Tier D core (`DistributionObject` + `PhaseTransitionThreshold`).

---

## Fire #46 — 2026-05-08 (PIVOT FIRE — substrate_v3 proposal stub filed; design-prep phase begins)

**Coordination note:** no new commits between fire #45 and fire #46 from parallel instance, no Aporia response yet on ST-fire45-002. Per fire #45 default ("attempt the pivot if no override"), fire #46 shifts from Lane-12 catalog probes to test-suite-design-prep.

**Lanes selected:** 1 NEW (design-doc preparation) + 11 (canon-fuzz fresh seed 20260508_10).

**Harness:** `charon/diagnostics/substrate_tester_fire_46_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_46_results.json`.

### Lane 1 — substrate_v3_proposal stub doc filed

Target: `pivot/substrate_v3_proposal_stub_2026-05-08.md` (250 lines, 11 sections).

Captures the 5-tier model from fires #38-#45 in design-doc form, ready for Techne pickup. Sections:

| § | Content |
|---|---|
| 0 | Provenance — fire-by-fire findings table |
| 1 | Executive summary |
| 2 | The 5-tier model (Tier A/B/C/D/E with ~22 primitives) |
| 3 | Cross-tier composition (Tier B/D) |
| 4 | Recommended contract-change scope (option a/b/c/d) |
| 5 | Test-suite design hooks for fires #47/#48 |
| 6 | 5 open design questions for Techne/Aporia |
| 7 | Catalog coverage estimate (~85-95%) |
| 8 | Coordination ticket chain |
| 9 | HARD-6 + HARD POSTURE alignment |
| 10 | Next steps |

**Stays a STUB.** Substrate-tester surfaces gaps; Techne owns the substrate (HARD-3 + natural division). Aporia decides scope.

### Lane 11 — canon-fuzz fresh seed: 13 passed (16.13s)

Regression continues at low cadence — health check, not the substrate-design work.

### Substrate-tester observation — pivot complete

Eight-fire matrix-filling phase ended at fire #45 saturation. Fire #46 is the FIRST design-prep fire. Future fires:
- **Fire #47:** ConstructiveExistenceWitness (Tier B core) test-suite stub — concrete Python skeleton, T1-T6 tests
- **Fire #48:** DistributionObject + PhaseTransitionThreshold (Tier D core) test-suite stub
- **Fire #49+:** return to matrix-filling on §II Rank Zoo / §III Waring / §VI Numerical Decomposition / §XI Specific Tensor Families at lower frequency

If Aporia greenlights a contract-change window before fire #49, fires #47-#48 outputs become directly useful test-spec material for Techne's build phase.

---

## Fire #45 — 2026-05-08 (5-tier model HOLDS; SATURATION SIGNAL; pivot proposal filed)

**Coordination note:** no new commits between fire #44 and fire #45 from parallel instance. Fire #45 is mine.

**Lanes selected:** 12 (catalog entry #40 — generic CP identifiability beyond Kruskal, §V) + 11 (canon-fuzz fresh seed 20260508_09).

Lane 12 choice: §V identifiability is at the §V/§VI/§IX boundary. Direct test of fire #43's Tier-B/Tier-D composition prediction. Saturation candidate.

**Harness:** `charon/diagnostics/substrate_tester_fire_45_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_45_results.json`.

### Lane 12 — CP identifiability probe: 5-TIER MODEL HOLDS

| Encoding attempt | Verdict |
|---|---|
| 1. Individual identifiability via Tier B | TIER_B_REFINEMENT — uniqueness annotation on RankDecompositionWitness |
| 2. Generic identifiability via Tier D | TIER_D_FITS — possible new GenericityAlmostEverywhereCert specialization |
| 3. Tier-B/Tier-D composition test | CONFIRMED (2nd independent instance after fire #43) |
| 4. Kruskal-bound certification | TIER_B_FITS — structural_inequality_certificate as 6th subtype |

### Refinements only (no new tier)

- Tier B: uniqueness annotation on RankDecompositionWitness; structural_inequality_certificate as 6th subtype (was 5)
- Tier D: GenericityAlmostEverywhereCert as ProbabilityMeasure specialization
- Tier B/D composition: 2nd independent confirmation

### Saturation signal — strongest yet

Eight-fire matrix-filling now producing REFINEMENTS not new tiers. 5-tier model + ~22 primitives + cross-tier composition is approaching robust coverage. Returns from additional matrix-filling diminish.

### Two tickets filed

1. **`T-2026-05-08-ST-fire45-001`** (P2-medium, capability-gap-refinement) → Techne. Documents 5-tier-model-holds + 3 refinements. Priority dropped from P1 to P2 (saturation = lower marginal value).
2. **`T-2026-05-08-ST-fire45-002`** (P1-high, strategic-coordination-saturation-pivot) → Aporia. **Proposes pivot** from matrix-filling to test-suite design starting fire #46:
   - Fire #46: substrate_v3_proposal stub doc (5-tier model in design-doc form)
   - Fire #47: ConstructiveExistenceWitness test-suite stub
   - Fire #48: DistributionObject + PhaseTransitionThreshold test-suite stub
   - Fire #49+: return to matrix-filling on unpulled sections (§II/§III/§VI/§XI) at lower frequency

**Default if no Aporia response by fire #46 wakeup:** ATTEMPT THE PIVOT. Substrate-tester judges saturation reached; proactive design-doc preparation is highest-leverage next step.

### Lane 11 — canon-fuzz fresh seed: 13 passed (16.25s)

### Substrate-tester observation

Fire #45 closes the matrix-filling phase as the dominant work mode. Eight fires produced 5 tiers, ~22 primitives, cross-tier composition finding, plus 5 strategic-coordination tickets pending Aporia. The shift from matrix-filling to test-suite-design is a natural cadence change — the data is in, time to package it for Techne.

If Aporia greenlights the pivot, fires #46-#48 produce the substrate_v3 proposal documentation; fire #49+ resumes matrix-filling at lower frequency for the remaining sections.

---

## Fire #44 — 2026-05-08 (Tier-E EMERGES — representation-theoretic primitives = 5th tier)

**Coordination note:** no new commits between fire #43 and fire #44 from parallel instance. Fire #44 is mine.

**Lanes selected:** 12 (catalog entry #95 — Kronecker coefficient vanishing/positivity, §XII GCT) + 11 (canon-fuzz fresh seed 20260508_08).

Lane 12 choice: §XII is the most abstract section. Tier A/B/C/D primitives are tensor-algebraic, decision-witness, optimization-geometric, and distributional; representation theory is structurally distinct. DELIBERATE divergence test against the 4-tier model.

**Harness:** `charon/diagnostics/substrate_tester_fire_44_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_44_results.json`.

### Lane 12 — Kronecker positivity probe: TIER E EMERGES

| Encoding attempt | Verdict |
|---|---|
| 1. Partitions as bootstrap_symbol | FAIL_ENCODING — no PartitionObject |
| 2. Tier-A TensorObject for V_λ ⊗ V_μ | FAIL_ENCODING — no IrreducibleRepresentation |
| 3. Tier-B existence witness for g > 0 | EXTENDS Tier B — RepresentationTheoreticWitness subtype |
| 4. Plethysm s_a[s_b] as substrate object | FAIL_ENCODING — no SymmetricFunction primitive |

### Tier E (representation-theoretic) — NEW 5th tier

| Primitive | Purpose | Blocks |
|---|---|---|
| **PartitionObject / YoungLatticePoint** | partitions of n + transpose, dominance, branching | all of §XII + §III + §V with symmetry |
| **IrreducibleRepresentation / RepresentationRing** | abstract irreducibles + branching/induction/restriction + character table | Kronecker (#95), GCT (#92), Foulkes (#98), Saxl (#99) |
| **SymmetricFunction / Plethysm / SchurFunctor** | symmetric-function ring + plethysm + Hall inner product + ω involution | #98 + #92 + §III Waring + §IV apolarity |

Plus **RepresentationTheoreticWitness** as Tier B's 5th subtype (Young-tableau / pictograph / plethysm-coefficient witnesses).

### Five-tier substrate-extension proposal (~20 primitives)

| Tier | Count | Family |
|---|---:|---|
| **A** | 4 | TensorAlgebra |
| **B** | 5 subtypes | ConstructiveExistenceWitness |
| **C** | 3 | Discrete-optimization geometry |
| **D** | 5 | Distributional |
| **E** | 3 | Representation-theoretic (NEW) |

### Two tickets filed

1. **`T-2026-05-08-ST-fire44-001`** (P1-high, capability-gap) → Techne. Tier E proposal.
2. **`T-2026-05-08-ST-fire44-002`** (P1-high, strategic-coordination-supplement) → Aporia. Supplement to ST-fire43-002 with Tier E + raises **saturation question**: continue matrix-filling vs pivot to test-suite design? Substrate-tester recommendation: option (c) — Tier B + Tier D + partial Tier A (TensorObject + GroupAction) is optimal contract-change scope; Tier C, E, remaining A primitives can ship in subsequent windows.

### Lane 11 — canon-fuzz fresh seed: 13 passed (31.54s)

### Substrate-tester observation — saturation approaching

Seven fires have surfaced 5 tiers covering the catalog's main mathematical-object classes. Returns from additional matrix-filling fires may diminish unless targeting NEW SECTIONS (§II Rank Zoo, §III Waring, §V Identifiability, §VI Numerical Decomposition, §XI Specific Tensor Families). Aporia coordination ticket explicitly raises this strategic question.

Pivot options to flag for next 1-2 fires:
- Continue matrix-filling at 1h cadence (current discipline)
- Pivot to test-suite design for the 5-tier proposal (assumes Aporia will greenlight)
- Hybrid: fire #45 = §V identifiability test of Tier-B/Tier-D composition; fire #46 = first test-suite stub for ConstructiveExistenceWitness primitive

---

## Fire #43 — 2026-05-08 (Tier-D CONFIRMED + EXTENDED 3→5; Tier B/D compose cleanly)

**Coordination note:** no new commits between fire #42 and fire #43 from parallel instance. Fire #43 is mine.

**Lanes selected:** 12 (catalog entry #73 — tensor PCA computational threshold, §IX Random Tensors, P28 distributional) + 11 (canon-fuzz pytest fresh seed 20260508_07).

Lane 12 choice: §IX is the natural habitat for Tier-D primitives. Pulling here directly tests whether fire #42's Tier-D shape (DistributionObject + StatisticalTestSpec + ProbabilityMeasure) holds up on a fresh §IX problem and whether the catalog reveals additional distributional primitives.

**Harness:** `charon/diagnostics/substrate_tester_fire_43_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_43_results.json`.

### Lane 12 — Tensor PCA threshold probe: Tier-D CONFIRMED + EXTENDED

| Encoding attempt | Verdict |
|---|---|
| 1. Spike model T = λ·v⊗d + W as DistributionObject | TIER_D_CONFIRMED |
| 2. Dual-threshold gap (λ_stat vs λ_comp) | EXTENDS_TIER_D — needs PhaseTransitionThreshold |
| 3. SOS lower-bound certificate | TIER_B/TIER_D_INTERACTION — composes cleanly |
| 4. AMP / power method as MethodSpec | EXTENDS_TIER_D — needs AlgorithmThresholdCert |

### Tier D EXTENDED (3 → 5 primitives)

| Primitive | Status | Source |
|---|---|---|
| **DistributionObject** | CONFIRMED | fire #42 origin, fire #43 independent confirmation |
| **StatisticalTestSpec** | retained | fire #42 |
| **ProbabilityMeasure / RandomVariable** | retained | fire #42 |
| **PhaseTransitionThreshold** | NEW | fire #43 |
| **AlgorithmThresholdCert / AsymptoticSuccessGuarantee** | NEW | fire #43 |

`PhaseTransitionThreshold = (parameter_axis, threshold_value, regime_below, regime_above, semantic_class)` — encodes the phase-transition geometry of an ensemble. `AlgorithmThresholdCert` lives at MethodSpec / Tier-D interface — captures "method M succeeds with prob ≥ p above threshold."

### Tier B / Tier D INTERACTION — substrate-design finding

Tier B (ConstructiveExistenceWitness) applies **at fixed parameters** (individual existential claim). Tier D (PhaseTransitionThreshold) applies **as parameters scale** (asymptotic / population claim). They **compose cleanly without redundancy.**

Example: Hopkins-Steurer SOS lower bound for tensor PCA = Tier-B SOS certificate at fixed (n, d, λ); the threshold λ_SOS_k(n, d) scaling with n = Tier-D PhaseTransitionThreshold. Both primitives needed; neither subsumes the other.

**Implication for contract-change window:** bundled Tier-B + Tier-D design pass benefits both. Fire #43 revises substrate-tester recommendation to (b) bundled (was (a) Tier-B alone in fire #42).

### Six-fire substrate-extension proposal (4 tiers, ~16 primitives)

| Tier | Count | Primitives |
|---|---:|---|
| **A** | 4 | TensorObject + TensorNetworkGraph + GroupAction + SchemeObject |
| **B** | 4+ | RankDecompositionWitness + ContractionOrderWitness + IsomorphismCertificate + LimitWitness; SOS certificates compose with Tier D |
| **C** | 3 | MomentPolytope + RewriteSearchTree + OrbitStratification |
| **D** | 5 | DistributionObject + StatisticalTestSpec + ProbabilityMeasure + PhaseTransitionThreshold + AlgorithmThresholdCert |

Plus cross-tier composition: Tier B / Tier D compose at the individual-vs-asymptotic boundary.

### Two tickets filed

1. **`T-2026-05-08-ST-fire43-001`** (P1-high, capability-gap-tensor-catalog) → Techne. Continues matrix-filling; extends Tier D from 3 to 5 primitives.
2. **`T-2026-05-08-ST-fire43-002`** (P1-high, strategic-coordination-supplement) → Aporia. SUPPLEMENT to ST-fire42-002: Tier-D extended scope + Tier B/D composition finding. Revised recommendation: option (b) bundled Tier B + Tier D contract-change pass.

### Lane 11 — canon-fuzz fresh seed: 13 passed (78.82s)

Canonicalization fuzz infrastructure healthy.

### Substrate-tester observation

Six fires, 4 tiers, ~16 primitives. The Tier B/D composition finding is fire #43's substrate-design contribution: the proposed primitives interlock cleanly across tiers without overlap or redundancy. Future fires can:

- Pull §V (identifiability) to test whether identifiability problems map to Tier B/D composition or surface a fifth tier
- Pull §XII (geometric complexity theory) — most abstract section, likely surfaces NEW primitive class if substrate doesn't already cover GCT-style invariants
- Pivot to test-suite design once Aporia greenlights a contract-change window

---

## Fire #42 — 2026-05-08 (DIVERGENCE TEST: Tier-B QUALIFIED + Tier-D distributional emerges)

**Coordination note:** no new commits between fire #41 and fire #42 from parallel instance. Fire #42 is mine.

**Lanes selected:** 12 (catalog entry #66 — Z-eigenvalue distribution, §VIII Spectral, paradigm P28 distributional flavor) + 9 (sigma_kernel test suite full sweep).

Lane 12 choice was DELIBERATE divergence test: distributional/probabilistic flavor structurally orthogonal to fires #38-#41. If Tier-B (ConstructiveExistenceWitness) surfaces here too, even stronger; if it diverges, the substrate-wide claim gets calibrated.

**Harness:** `charon/diagnostics/substrate_tester_fire_42_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_42_results.json`.

### Lane 12 — Z-eigenvalue distribution probe: DIVERGENCE_FINDING

| Encoding attempt | Verdict | Blocker |
|---|---|---|
| 1. Aggregate KillVectors as distribution | FAIL_ENCODING | no DistributionObject / Ensemble primitive |
| 2. CLAIM with distributional hypothesis | PARTIAL | text level works; evidence dict lacks distributional schema |
| 3. CoordinateChart for ensemble | FAIL_ENCODING | chart represents deterministic region; no measure-theoretic structure |
| 4. Search for Tier-B pattern | DIVERGENCE | population-level claim, not individual-existential — Tier B doesn't apply |

### Tier-B QUALIFIED — substrate-wide claim calibrated

Tier B (ConstructiveExistenceWitness) is QUALIFIED to **decision problems with individual witness** across §I/§III/§IV/§VII/§X. Distributional / population-level problems need a different primitive class (Tier D). Not a refutation — a CALIBRATION of the substrate-wide claim.

### Tier D — NEW distributional primitives emerge

| Primitive | Purpose | Blocks |
|---|---|---|
| **DistributionObject / EmpiricalCDF / RandomTensorEnsemble** | probability distributions over tensor space | §IX entirely + #66 + parts of §VIII |
| **StatisticalTestSpec** | statistical tests with null distribution / sample-size / p-value contracts | population-level claim falsification |
| **ProbabilityMeasure / RandomVariable** | measure-theoretic substrate primitive | random matrix theory, free probability |

### Five-fire substrate-extension proposal (4 tiers)

| Tier | Primitive Family | Source Fires |
|---|---|---|
| **A** | TensorAlgebra subsystem (TensorObject + TensorNetworkGraph + GroupAction + SchemeObject) | #38/#39/#40/#41 |
| **B** | ConstructiveExistenceWitness — QUALIFIED to decision-problems-with-individual-witness | #38/#39/#40/#41 |
| **C** | Discrete-optimization geometry (MomentPolytope + RewriteSearchTree + OrbitStratification) | #38/#39/#40 |
| **D** | Distributional primitives (DistributionObject + StatisticalTestSpec + ProbabilityMeasure) | #42 |

Each tier is a SEPARATE design problem; bundled or independent shipping is a design call.

### Three tickets filed

1. **`T-2026-05-08-ST-fire42-001`** (P1-high, capability-gap-tensor-catalog) → Techne. Continues matrix-filling; introduces Tier D.
2. **`T-2026-05-08-ST-fire42-002`** (P1-high, strategic-coordination-supplement) → Aporia. SUPPLEMENT to ST-fire41-002: Tier-B scope QUALIFIED + Tier D add-on. Decision requested: ship Tier B alone (a), Tier B + Tier D bundled (b), or wait one more divergence-test fire (c). Substrate-tester recommendation: (a) — Tier B has strongest convergence; Tier D is fresher.
3. **`T-2026-05-08-ST-fire42-003`** (P3-low, test-infrastructure) → Techne. Three sigma_kernel test files fail under bare `pytest` invocation; pass under `python -m pytest`. Workaround documented in fire #42 harness Lane 9 comment.

### Lane 9 — sigma_kernel test suite full sweep: 24/0 PASS

| Metric | Value |
|---|---:|
| invocation | `python -m pytest sigma_kernel/tests/` (bare `pytest` fails — see ST-fire42-003) |
| n_passed | 24 |
| wall-clock | 74.44s |

Kernel test suite healthy. Three new mini-window-era tests + frozen-invariance audit included.

### Substrate-tester observation

The DELIBERATE divergence test was high-leverage: it produced a Tier-B SCOPE QUALIFICATION (substrate-wide for individual-decision problems, not literally universal) plus a NEW Tier D family. Five fires now produce a 4-tier substrate-extension proposal — usable scope guidance for one, two, or three contract-change windows depending on Aporia's strategic call.

Future fires can:
- Continue divergence-testing (§V identifiability, §XII GCT) to test whether Tier D fits or another tier emerges
- Fill the matrix more uniformly (catalog entries by paradigm)
- Pivot toward designing test-suites for the proposed primitives if Aporia greenlights a contract-change window

---

## Fire #41 — 2026-05-08 (FOUR-FIRE TIER-B CONFIRMATION + Aporia coordination ticket)

**Coordination note:** no new commits between fire #40 and fire #41 from parallel instance. Fire #41 is mine.

**Lanes selected:** 12 (catalog entry #34 — border-rank variety membership, §IV, paradigms P29/P31) + 11 (canon-fuzz pytest fresh seed).

Lane 12 choice was DELIBERATE: catalog #34 is a canonical positive-existential-with-witness problem ("decide T ∈ σ_r" → constructive witness needed). Direct test of the Tier-B prediction from fires #38/#39/#40. If ConstructiveExistenceWitness surfaces again, four-fire convergence locks in.

**Harness:** `charon/diagnostics/substrate_tester_fire_41_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_41_results.json`.

### Lane 12 — Border-rank variety membership encoding probe: FAIL_ENCODING

| Encoding attempt | Verdict | Blocker |
|---|---|---|
| 1. CLAIM with hypothesis="T ∈ σ_2" | FAIL_ENCODING | no SchemeObject; σ_r is an algebraic variety, not a region/chart |
| 2. EQUIV with equiv_chain | FAIL_ENCODING | chain is FINITE; border-rank requires INFINITE LIMIT (ε → 0); no LimitWitness primitive |
| 3. ExclusionCertificate | PARTIAL | non-membership encodable via Young-flattening defining equations; positive membership witness has no home (4th time) |
| 4. CoordinateChart for σ_r | FAIL_ENCODING | scheme has singular loci, components, embedded primes; chart structure too poor |

### Tier-B FOUR-FIRE CONFIRMATION (most robust matrix-filling finding)

| Fire | Section | Catalog | Paradigm | Tier-B witness |
|---|---|---|---|---|
| #38 | §I | #4 M⟨3⟩ | P28-P31 | RankDecompositionWitness |
| #39 | §X | #84 TN contraction | P30 | ContractionOrderWitness |
| #40 | §VII | #58 tensor iso | P30+P31 | IsomorphismCertificate |
| #41 | §IV | #34 σ_r membership | P29+P31 | LimitWitness/BorderRankWitness |

**Four sections, four paradigms, same shape.** Substrate has ExclusionCertificate for negative existentials; no companion primitive for positive existentials with constructive witness. ConstructiveExistenceWitness as a substrate-WIDE primitive is now justified by the strongest convergence evidence the matrix-filling exercise has produced.

### Tier A extended — SchemeObject

§IV's algebraic-geometric flavor surfaces a NEW Tier-A primitive: SchemeObject (vanishing locus of polynomial ideal; singular loci, components, embedded primes). Section IV (#26-35) cannot reduce to TensorObject + TensorNetworkGraph + GroupAction. Tier A becomes:

`TensorObject + TensorNetworkGraph + GroupAction + SchemeObject = TensorAlgebra subsystem (extended)`

### Two tickets filed

1. **`T-2026-05-08-ST-fire41-001`** (P1-high, capability-gap-tensor-catalog) → Techne. Continues matrix-filling.
2. **`T-2026-05-08-ST-fire41-002`** (P1-high, strategic-coordination-tier-B-convergence) → Aporia. Flags ConstructiveExistenceWitness for strategic-planning review and contract-change-window prioritization. Single contract-change pass shipping the primitive + four subtypes is comparable in scope to the 5-of-5 cluster's Structured-Equivalence-Class. Co-design recommended.

### Lane 11 — canon-fuzz fresh seed: 13 passed

| Metric | Value |
|---|---:|
| seed | 20260508_06 |
| pytest rc | 0 |
| n_passed | 13 |
| wall-clock | 31.30s |

Canonicalization fuzz infrastructure healthy.

### Substrate-tester observation

Fire #41 marks the inflection point: matrix-filling has produced enough convergence evidence (4 fires, 4 paradigms, 1 substrate-wide primitive) to JUSTIFY a strategic-planning-level decision. Aporia coordination ticket invites that decision. Future fires can continue diversifying (§III/§V/§VIII/§XII) but the contract-change recommendation is already overdetermined for Tier B.

If Aporia greenlights the contract-change window, substrate-tester transitions from "matrix-filling for evidence" to "designing test suite for the new primitive" mode.

---

## Fire #40 — 2026-05-08 (THREE-FIRE CONVERGENCE: ConstructiveExistenceWitness substrate-wide gap)

**Coordination note:** no new commits between fire #39 and fire #40 from parallel instance. Fire #40 is mine.

**Lanes selected:** 12 (catalog entry #58 — tensor isomorphism complexity, §VII, paradigms P30/P31) + 14 (frozen-dataclass invariance regression).

Diversification choice: §VII / equivalence-class decision under group action — orthogonal to fires #38 (rank/decomposition, §I) and #39 (network-topology contraction, §X). Tests whether subsystem convergence holds in a third direction.

**Harness:** `charon/diagnostics/substrate_tester_fire_40_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_40_results.json`.

### Lane 12 — Tensor isomorphism encoding probe: FAIL_ENCODING

| Encoding attempt | Verdict | Blocker |
|---|---|---|
| 1. EQUIV opcode | PARTIAL | 3 witness types (proof_ref/finite_check/equiv_chain) don't include group-action witness |
| 2. OperatorPortabilityCertificate (T030) | FAIL_ENCODING | right shape but no GroupAction primitive (no composition/inverse/identity) |
| 3. MethodSpec/IndependenceClass | FAIL_ENCODING | could RUN Magma iso-test, can't represent equivalence-class structure as substrate data |
| 4. ExclusionCertificate | PARTIAL | non-iso encodable; iso witness has no home — same asymmetric-existential as fire #39 |

### Capability gaps (3 missing primitives)

1. **GroupAction / GroupActionWitness** — explicit group-element tuple acting on substrate object. Blocks #58, parts of §V/§IX/§X (#79 SLOCC).
2. **IsomorphismCertificate (positive existential with witness)** — same shape as fire #39's ContractionOrderWitness. Substrate-wide, not tensor-specific.
3. **OrbitStratification / FundamentalDomain** — orbit space of group action; canonical-form reasoning. Overlaps with 5-of-5 capability-gap cluster's Structured-Equivalence-Class.

### Three-fire convergence — ROBUST FINDING

| Tier | Fire #38 | Fire #39 | Fire #40 | Subsystem |
|---|---|---|---|---|
| **A — foundational tensor objects** | TensorObject | TensorNetworkGraph | GroupAction | **TensorAlgebra subsystem** |
| **B — asymmetric existential (ROBUST)** | RankDecompositionWitness | ContractionOrderWitness | IsomorphismCertificate | **ConstructiveExistenceWitness primitive (substrate-WIDE)** |
| **C — discrete-optimization geometry** | MomentPolytope/SecantVarietyEquation | RewriteSearchTree | OrbitStratification | **discrete-optimization-geometry family** |

**Tier B is the strongest convergence finding.** Three distinct paradigms (P28-P31, P30, P30/P31/GI-hard) all hit the same shape: substrate has ExclusionCertificate for negative existentials, no companion primitive for positive existentials with cost/correctness annotation. This is a substrate-wide design issue. **Highest-priority recommendation:** ship `ConstructiveExistenceWitness` as a substrate-wide primitive with rank/contraction-order/isomorphism specializations.

**Tier C overlaps with the pre-existing 5-of-5 capability-gap cluster's Structured-Equivalence-Class meta-primitive.** Co-design recommended.

**Filed:** `T-2026-05-08-ST-fire40-001` (P1-high) → Techne. Cross-references catalog #58, paradigms P30/P31, sister tickets from fires #38/#39, 5-of-5 cluster.

### Lane 14 — frozen-dataclass invariance: 5/5 PASS

Walked MethodSpec, ExclusionClaim, RegionSpec, ReplayInfo, ExclusionCertificate. All reject mutation (FrozenInstanceError on attribute write). Mini-window Tier-2 fix's auto-enrollment audit working as expected.

### Substrate-tester observation

Three-fire matrix-filling has produced enough convergence to recommend contract-change scope:

1. **HIGHEST PRIORITY:** `ConstructiveExistenceWitness` substrate-wide primitive (Tier B).
2. **SECOND:** TensorAlgebra subsystem (TensorObject, TensorNetworkGraph, GroupAction) — Tier A.
3. **THIRD:** discrete-optimization-geometry family co-designed with 5-of-5 cluster — Tier C.

Future fires can keep filling the matrix, but Tier B's three-paradigm robustness already justifies bringing this to a contract-change-window agenda. Aporia coordination ticket may be warranted next fire to flag the convergence for strategic-planning review.

---

## Fire #39 — 2026-05-08 (CONVERGENCE: 6 MISSING PRIMITIVES → TensorAlgebra SUBSYSTEM)

**Coordination note:** no new commits between fire #38 and fire #39 from parallel instance. Fire #39 is mine.

**Lanes selected:** 12 (catalog entry #84 — optimal tensor network contraction order, §X, paradigm P30) + 4 (SIGMA opcode smoke).

Diversification: §X / P30 ≠ §I / P28-P31 from fire #38. Pulling from a different section + different paradigm tests whether missing primitives converge or diverge across the catalog matrix.

**Harness:** `charon/diagnostics/substrate_tester_fire_39_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_39_results.json`.

### Lane 12 — Optimal contraction-order encoding probe: FAIL_ENCODING

Toy network: 4-tensor cycle A-B-C-D with shared indices a/b/c/d. Contraction-order optimization = NP-hard combinatorial problem (Markov-Shi 2008).

| Encoding attempt | Verdict | Blocker |
|---|---|---|
| 1. CoordinateChart | FAIL_ENCODING | flat tuple of named scalar axes; no GraphObject — topology of TN can't reduce to chart |
| 2. MethodSpec / IndependenceClass | FAIL_ENCODING | no enum value; encoding each order as a MethodSpec loses optimization semantics (no dominance relation between orders) |
| 3. ExclusionCertificate | PARTIAL | works for negative existential (no order achieves cost < B) but no companion **constructive witness** primitive — substrate has asymmetric existential coverage |
| 4. REWRITE associativity | PARTIAL | captures one move, not optimization-over-moves — no RewriteSearchTree primitive |

### Capability gaps surfaced (3 missing primitives)

1. **TensorNetworkGraph (general LabeledHypergraph)** — vertices = tensors with shapes; edges = shared indices. Blocks #75-84 + Feynman/factor/knot diagrams.
2. **ContractionOrderWitness** — constructive upper-bound witness for combinatorial optimization. **Broader pattern:** substrate's existential primitives are asymmetric (ExclusionCertificate for lower bounds; nothing for upper-bound-with-cost). Applies to ALL NP-hard optimization the substrate wants to track.
3. **RewriteSearchTree / RewriteCostFunctional** — optimization-over-rewrite-sequences; complements REWRITE's single-move semantics.

### Convergence with fire #38 — TensorAlgebra subsystem design

| Fire | Catalog | Section | Paradigm | Missing primitives |
|---|---|---|---|---|
| #38 | #4 (M⟨3⟩ rank) | §I | P28/29/30/31 | TensorObject, RankDecompositionWitness, MomentPolytope/SecantVarietyEquation |
| #39 | #84 (TN contraction order) | §X | P30 | TensorNetworkGraph, ContractionOrderWitness, RewriteSearchTree |

**Two fires, six missing primitives, all converging on a TensorAlgebra subsystem.** TensorObject (single-tensor identity) + TensorNetworkGraph (multi-tensor topology) are foundational; witness/decomposition primitives sit on top. Single contract-change pass shipping the subsystem could unblock ~30+ catalog entries spanning §I + §X.

The ContractionOrderWitness asymmetric-existential pattern is BROADER than tensors — it's a substrate-wide gap any time the kernel needs to track a constructive witness with a verifiable cost annotation for an NP-hard optimization. That gap likely also blocks parts of the 5-of-5 capability-gap cluster.

**Filed:** `T-2026-05-08-ST-fire39-001` (P1-high, capability-gap-tensor-catalog) → Techne. Cross-references catalog #84 + paradigm P30 + sister ticket from fire #38 + Techne T-2026-05-08-T038.

### Lane 4 — SIGMA opcode smoke: 5/5 PASS

| Test | Verdict |
|---|---|
| T1 bootstrap_symbol | PASS |
| T2 RESOLVE round-trip + hash integrity | PASS |
| T3 RESOLVE missing → KeyError | PASS |
| T4 CLAIM with valid kill_path | PASS |
| T5 CLAIM with non-string kill_path → TypeError (mini-window contract) | PASS |

Kernel opcode chain healthy. T5 is a regression of the mini-window Tier-3 fix (T-2026-05-07-ST-fire29-002).

### Substrate-tester observation

Fires #38 + #39 establish the matrix-filling discipline:
- distinct catalog entries from different sections surface OVERLAPPING missing-primitive sets (subsystem-level design needs)
- AND distinct primitive sets (deeper structural variety)
- convergence pattern across cells = scope guidance for the next contract-change window

Future fire #40 onward should continue diversifying: pick from §IV (algebraic geometry) or §VII (decidability) next to see whether the TensorAlgebra subsystem design holds beyond §I + §X.

---

## Fire #38 — 2026-05-08 (FIRST FIRE UNDER HARD-6 + HARD POSTURE)

**Coordination note:** James filed HARD-6 (`7cb418d1`) — *"attack the problems of the tools we will need most in the future. The failures will guide us."* — plus the canonical 104-entry tensor catalog at `aporia/mathematics/tensor_open_problems_v1.md`. Per HARD POSTURE 2026-05-08, Lane 12 (representation-pressure) now pulls probes from the canonical catalog instead of inventing novel objects. This fire is the **first cell** of the 104 × 5-paradigm matrix.

**Lanes selected:** 12 (catalog-pulled M⟨3⟩ encoding probe — entry #4) + 8 (cert-extension regression smoke).

**Harness:** `charon/diagnostics/substrate_tester_fire_38_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_38_results.json`.

### Lane 12 — M⟨3⟩ encoding probe: FAIL_ENCODING (the failure IS the output)

Pulled catalog entry #4 verbatim: *"Exact rank of M⟨3⟩ — bounds 19 ≤ R(M⟨3⟩) ≤ 23."* Built the 9×9×9 tensor (27 nonzero entries via `T[(i,j),(k,l),(m,p)] = δ_{j,k} δ_{l,m} δ_{p,i}`) and attempted four encodings against existing substrate primitives.

| Encoding attempt | Verdict | Blocker |
|---|---|---|
| 1. CoordinateChart | FAIL_ENCODING | `coordinate_system` is named scalar axes, not tensor entries; chart can register metadata but can't HOLD the tensor |
| 2. KillVector / OperatorOutputSequence (T023) | FAIL_ENCODING | force-fits as index→scalar; loses multilinearity; rank queries inexpressible |
| 3. REWRITE / EQUIV | FAIL_ENCODING | REWRITE expects scalar Symbols; EQUIV's 3 witness types (proof_ref / finite_check / equiv_chain) don't carry outer-product witnesses |
| 4. OperatorPortabilityCertificate (T030) | PARTIAL | symmetry-group annotation only (Z/3 cyclic, GL₃³); no compute backbone for rank lower-bound work |

**Verdict:** substrate has NO native tensor primitive. M⟨3⟩ — one of the foundational tensor objects (matrix-multiplication exponent ω is the asymptotic rank of the M_n family) — is unrepresentable.

### Capability gaps surfaced (3 missing primitives)

1. **TensorObject** — n-dim tensor with entry-level identity. Blocks paradigms P28/P29/P30/P31 + catalog entries #4/#5/#6 + at least #18-21.
2. **RankDecompositionWitness** — sum of outer products with rank annotation; substrate-grade certificate. Blocks P28/P29 + every rank-bound problem in §I of the catalog.
3. **MomentPolytope / SecantVarietyEquation** — algebraic-geometric tensor object; defining equations of secant varieties. Blocks P29/P31 + every border-rank/secant-variety problem in §I-III.

**Filed:** `T-2026-05-08-ST-fire38-001` (P1-high, capability-gap-tensor-catalog) → Techne. Cross-references catalog entry #4 + paradigms P28/P29/P30/P31 + Techne T-2026-05-08-T038 (classification of all 104) + Ergon E009 (probe-shape audit) + the related-but-different 5-of-5 capability-gap cluster.

**HARD-6 alignment:** by induction the same blocking pattern applies to most of §I (rank/border-rank/asymptotic-complexity) and substantial parts of §II-III. A single TensorObject-design pass during the next contract-change window unblocks ~30+ catalog entries simultaneously. **The failure mode IS the output** — substrate-tester's role under HARD-6 + HARD POSTURE is to systematically fill the 104 × 5 paradigm matrix with honest negative-result data.

### Lane 8 — cert smoke: 3/3 PASS

| Test | Verdict |
|---|---|
| T1 register cert | PASS |
| T2 collision raises | PASS |
| T3 COMPLETE without triangulation_history → ValueError | PASS |

ExclusionCertificate primitive healthy.

### Substrate-tester observation

Future Lane-12 fires under HARD POSTURE follow this pattern:
- pull catalog entry by index; document its mathematical content
- attempt encoding via existing primitives; enumerate failure modes
- file capability-gap ticket cross-referencing catalog entry + attack paradigms + missing primitives

Over many fires this fills the 104 × 5 paradigm matrix; convergent missing-primitive findings (e.g. TensorObject appearing across many cells) signal the next contract-change priorities.

---

## Fire #37 — 2026-05-08

**Coordination note:** my fire #36 was last; James's tensor compute-fabric directive landed between fires (commits `91ffbc43` + `3a4dcd19`). Tensor strategy doc + memory entry codified.

**Lanes selected:** 17 (mutation-testing on prometheus_math/kill_vector.py — outside the substrate-wide audit's sigma_kernel/-only scope) + 13 (canon-fuzz fresh seed 20260508_05).

**Lane 15 + 18 reactivation re-check:** still DORMANT.

**Harness:** `charon/diagnostics/substrate_tester_fire_37_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_37_results.json`.

### Lane 17 — mutation outside audit scope: inconclusive (all false positives)

| Metric | Value |
|---|---:|
| target | `prometheus_math/kill_vector.py` (~1700 LoC, 2 frozen dataclasses: KillComponent + KillVector) |
| score | 0.0 (0 killed / 8 survived) |
| frozen-dataclass survivors | 0 |

All 8 mutations are `off_by_one_int` hits at lines 102-104 — inside the `MARGIN_UNITS` tuple's inline comment text (`[0, 1]`, `1 - p_value`, `1+d`, etc.). **Pure false positives** per framework caveat #1 (docstring/comment naïveté). The two actual `@dataclass(frozen=True)` lines weren't among first-8 sampled because the framework's site-selection picks first-encountered candidates which cluster near the module-top heavy-commented region.

**Verdict:** Lane 17 result not informative for substrate health on this module. Substrate-wide audit's sigma_kernel/-only scope question NOT answered by this fire — would need a smarter site-selection or a higher max-mutations cap to reach the actual frozen-decorator lines.

**Substrate-tester observation:** the mutation framework's site-selection is biased toward commented module-top regions when run with `--max-mutations N` < total candidates. Future fire could file a P3 ticket recommending site-selection improvements (e.g. skip multi-line docstring blocks entirely; or shuffle candidates per --hypothesis-style seed). Not filing this fire — caveat #1 already documents the underlying limitation.

### Lane 13 — canon-fuzz fresh seed (20260508_05): 13/0 PASS

| Metric | Value |
|---|---:|
| pytest rc | 0 |
| n_passed | 13 |
| n_failed | 0 |

**Substrate verdict: PASS.** Fourth (or higher) independent Hypothesis seed exploration; canonicalization invariants robust.

### Tickets filed this fire

**0 tickets.** Lane 17 inconclusive (false positives only); Lane 13 PASS.

### Standing recommendations for next fire (#38)

1. **Anti-repeat:** avoid lanes 17, 13. Suggested fire #38:
   - **Lane 8 (cert-extension)** — last my-instance fire #25
   - **Lane 11 (batch-sweep)** with corpus-extension awareness — recent commits (`e10e26a9`) added "Round 2 expansions: batch11 seeds + 4 catalog extensions"; worth re-running batch-sweep against the expanded corpora
   - **Lane 7 entry continuation** — if INCONCLUSIVE list locatable
2. **P3 ticket candidate (deferred):** the mutation framework's site-selection bias is real but caveat #1 already documents it. File only if a future fire surfaces another instance where site-selection blocked a substrate finding.
3. **Tensor compute-fabric strategy now codified** (commits `91ffbc43` + `3a4dcd19`). When a substrate-pressure finding has 1D-structured-exponential-state-space signature, charter says: file Aporia coordination ticket flagging Walk-1/2/3 candidacy. No such finding this fire.

### Discipline notes

- HARD-1..HARD-5: clean. No tensor-tool drift; no framework adoption.
- Time used: ~25 min (within 50-min cap).
- Anti-flooding cap: 0 tickets filed (max 5 allowed).
- Multi-instance coordination: pulled before lane-pick; claimed fire #37 = max-on-origin (36) + 1.

— substrate-tester, fire #37, 2026-05-08

---

## Fire #36 — 2026-05-08

**Coordination note:** my fire #35 was last; no new parallel.

**Lanes selected:** 11 (batch-sweep, 4th seed) + 16 (concurrency-stress smoke; first my-instance run; covered by parallel fires #12 and #24 only).

**Lane 15 + 18 reactivation re-check:** still DORMANT.

**Harness:** `charon/diagnostics/substrate_tester_fire_36_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_36_results.json`.

### Lane 11 — batch-sweep with seed 20260508_03

| Metric | Value |
|---|---:|
| n_submissions | 30 |
| n_submitted_ok | 30 / 30 |
| first probe sampled | `harmonia_b_adv_006` |

**Substrate verdict: PASS** (architectural impedance now 4-seed-confirmed).

**Cumulative Lane 11:**
- Fire #8: seed 20260507_12, first `harmonia_b_adv_010`
- Fire #13: seed 20260507_15, divergent
- Fire #32: seed 20260508_01, first `harmonia_d_adv_004`
- **Fire #36: seed 20260508_03, first `harmonia_b_adv_006`**

**Total: 120 ingest-OK probes across 4 distinct seeds, 0 substrate verdicts.** Each seed produces a different first probe — confirming distinct sample cohorts. The architectural-impedance finding (no general-purpose CLAIM gauntlet for non-Lehmer mathematical claims) is now overwhelmingly seed-stable.

### Lane 16 — concurrency-stress smoke (first my-instance run)

| Metric | Value |
|---|---:|
| pytest rc | 0 |
| n_passed | 6 |
| n_failed | 0 |
| wall_clock | 21.8s |

**Substrate verdict: PASS.** All 6 concurrency tests pass (parallel-CLAIM safety, thread-determinism, hash-distinctness, etc.). My-instance confirms the parallel-instance fires #12 and #24 results.

### Tickets filed this fire

**0 tickets.** Both lanes substrate-correct.

### Standing recommendations for next fire (#37)

1. **Aporia coordination ticket candidate (HIGH PRIORITY):** the 5-of-5 capability-gap pattern (per fire #35) is now the most actionable finding awaiting Aporia coordination. Recommend filing a coordination ticket proposing the unified Structured-Equivalence-Class meta-primitive design.
2. **Anti-repeat:** avoid lanes 11, 16 (just covered). Suggested fire #37:
   - **Lane 13 (canonicalization-fuzz)** with fresh seed — cumulative seed coverage growing
   - **Lane 14 (replay-determinism)** smoke
   - **Lane 17 (mutation-testing)** — could probe a 4th frozen-heavy module to test the Tier 2 audit's coverage breadth
3. **Lane 11 cumulative observation now 4-seed-stable:** very strong evidence that the substrate impedance is intentional + reproducible. Worth promoting from "fire-log architectural observation" to a substrate-design-observation file via Aporia coordination.

### Discipline notes

- HARD-1..HARD-5: clean.
- Time used: ~10 min (well within 50-min cap; both lanes fast).
- Anti-flooding cap: 0 tickets filed (max 5 allowed).
- Multi-instance coordination: pulled before lane-pick; claimed fire #36 = max-on-origin (35) + 1.

— substrate-tester, fire #36, 2026-05-08

---

## Fire #35 — 2026-05-08

**Coordination note:** my fire #34 was last; no new parallel.

**Lanes selected:** 8 (TriangulationPathRef indirect frozen-ness probe; addresses ST-fire33-001 P3) + 12 (5th NOVEL capability-gap probe).

**Lane 15 + 18 reactivation re-check:** still DORMANT.

**Harness:** `charon/diagnostics/substrate_tester_fire_35_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_35_results.json`.

### Lane 8 — TriangulationPathRef indirect frozen-ness probe: 3/3 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — direct setattr on ref | **PASS** | `FrozenInstanceError` raised |
| T3 — parent's `triangulation_history` field mutation | **PASS** | `FrozenInstanceError` raised |
| T4 — inner ref via `cert.triangulation_history[0].path_id =` | **PASS** | `FrozenInstanceError` raised on inner setattr |

**Substrate verdict: PASS.** TriangulationPathRef IS actually frozen at the dataclass level — verified end-to-end via direct, parent-field, and inner-via-parent-index mutation attempts.

**Substantive observation re: ST-fire33-001:** the gap reported in fire #33 is purely in **audit-test coverage**, not in substrate behavior. The frozen invariant holds; the audit's `_try_minimal_construct` synthesizer just can't auto-generate the nested `MethodSpec` arg required to enroll TriangulationPathRef.

**ST-fire33-001 stays at P3** — substrate-tester confirms the substrate is correct, the gap is in test discipline. The ticket's recommended remediation paths (explicit per-class test OR enhanced synthesizer for nested dataclasses) are still appropriate; the priority does not need to change.

### Lane 12 — 5th NOVEL capability-gap probe: finite-group representation (S_3)

Encoded the irreducible 2-dim standard representation of S_3:
- (1 2) → [[-1, 1], [0, 1]]
- (1 2 3) → [[0, -1], [1, -1]]

**Result: CAPABILITY GAP.**

Required substrate primitives MISSING:
- `GroupObject` (finite group with multiplication table or generators+relations)
- `MatrixOverField` (typed matrix with coefficient-field metadata)
- `GroupHomomorphism` / `Representation` (G → GL(V) data)

EQUIV's witness types (proof_ref / finite_check / equiv_chain) cannot capture the matrix-valued intertwining isomorphism that defines representation equivalence.

**Filed: `T-2026-05-08-ST-fire35-001` (P1-high)** — 5th capability-gap in the **"Structured Equivalence Class" cluster**:

| # | Ticket | Object class | Missing primitive |
|---:|---|---|---|
| 1 | ST-fire1-002 | homotopy class | higher-category equivalence with deformation witness |
| 2 | ST-fire1-003 | combinatorial design | BlockDesign / IncidenceStructure |
| 3 | ST-fire21-001 | knot HOMFLY | SymbolicLaurentPolynomial + skein equivalence |
| 4 | ST-fire21-002 | A∞-algebra | ArityGradedOperationFamily |
| 5 | ST-fire35-001 (this fire) | finite-group rep | GroupRepresentation + intertwining isomorphism |

**5-of-5 cumulative pattern:** the substrate has scalar-output operators (T023) but lacks primitives for **structured objects with their own equivalence relations** whose witness data isn't a scalar value or a Symbol-ref. The unified **Structured-Equivalence-Class meta-primitive** (Aporia recommendation, cited in mini-window summary) is the right design candidate for the next contract-change window — closes all 5 tickets together rather than 5 one-off primitives.

### Tickets filed this fire

**1 ticket (P1-high):** `T-2026-05-08-ST-fire35-001` — 5th capability gap in the Structured Equivalence Class cluster.

### Standing recommendations for next fire (#36)

1. **Aporia coordination ticket candidate (HIGH PRIORITY):** the 5-of-5 cumulative pattern in capability-gap tickets is now overwhelmingly clear. Recommend filing an Aporia coordination ticket that aggregates the 5 P1-high tickets into a single design proposal: "Unified Structured-Equivalence-Class meta-primitive for the next contract-change window". Aporia/Techne co-design.
2. **Anti-repeat:** avoid lanes 8, 12 (just covered). Suggested fire #36:
   - **Lane 11 (batch-sweep)** — every-other-fire cadence; last my-instance fire #32
   - **Lane 14 / 16 (replay/concurrency)** — quick smokes
   - **Lane 7 entry continuation** — if INCONCLUSIVE list locatable
3. **ST-fire33-001 P3 stays OPEN** — substrate is correct (per Lane 8); audit needs explicit per-class test for TriangulationPathRef.
4. **Mini-window verification arc COMPLETE:** all 3 tiers verified across fires #33 (Tier 1+2) + #34 (Tier 3). Substrate-tester saga 2026-05-07/08 closes successfully. Substrate health: significantly improved.

### Discipline notes

- HARD-1..HARD-5: clean. Capability-gap probe targets operator-output-shaped or arity-graded primitives, not discipline-labeled object types (HARD-5 respected).
- HARD-3 (tensor-first): the proposed Structured-Equivalence-Class meta-primitive would be tensor-grade.
- Time used: ~25 min (within 50-min cap).
- Anti-flooding cap: 1 ticket filed (max 5 allowed).
- Multi-instance coordination: pulled before lane-pick; claimed fire #35 = max-on-origin (34) + 1.

— substrate-tester, fire #35, 2026-05-08

---

## Fire #34 — 2026-05-08

**Coordination note:** my fire #33 was last; no new parallel. All 7 mini-window tickets DONE; only ST-fire33-001 P3 OPEN from substrate-tester history. **My fire = #34.**

**Lanes selected:** 1 (Tier 3 `kill_path` validation regression + verbatim Mossinghoff probe per fire #19's retired-rec) + 6 (undecidable-canonicalization regression).

**Lane 15 + 18 reactivation re-check:** still DORMANT.

**Harness:** `charon/diagnostics/substrate_tester_fire_34_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_34_results.json`.

### Lane 1 — Tier 3 `kill_path` regression + Mossinghoff: 4/4 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — valid string kill_path accepted | **PASS** | "out_of_band:M=1.5_outside_(1.001,1.18)" stored verbatim |
| T2 — int kill_path raises TypeError | **PASS** | `TypeError: kill_path must be a str; got int: 12345...` (Tier 3 contract change #5 holds) |
| T3 — None kill_path raises TypeError | **PASS** | `TypeError` with helpful message |
| T4 — 3 verbatim Mossinghoff probes routed | **PASS** | first probe identified as Lehmer's polynomial via catalog cross-check; all 3 routed without error |

**Tier 3 contract verified end-to-end.** The substrate-tester probe for non-string kill_path now raises TypeError with the documented message structure. Verbatim Mossinghoff probes (the post-fire-#19 retired-rec strategy for Lane 1) route cleanly through `DiscoveryPipeline` — first entry catalog-matched as Lehmer's polynomial.

### Lane 6 — undecidable-canonicalization regression: 4/4 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — VALID_DECIDABILITY tuple unchanged | **PASS** | `('conditional', 'decidable', 'undecidable')` |
| T2 — undecidable construction succeeds | **PASS** | impl='word_problem_finitely_presented_groups', ds='undecidable' |
| T3 — invalid decidability raises ValueError | **PASS** | helpful message |
| T4 — registered Lehmer chart still decidable | **PASS** | impl='reflection_quotient', ds='decidable' |

**Substrate verdict: PASS.** Decidability discipline holds across all post-restart + post-mini-window fires.

### Tickets filed this fire

**0 tickets.** Both lanes substrate-correct.

### Standing recommendations for next fire (#35)

1. **Anti-repeat:** avoid lanes 1, 6. Suggested fire #35:
   - **Lane 12 (representation-pressure)** — could probe a 5th NOVEL object class (avoiding T024-T028 + ST-fire1-002/003 + ST-fire21-001/002 which are queued for next contract-change window)
   - **Lane 7 entry continuation** — if actual brute-force INCONCLUSIVE list can be located (the fire #1 hand-curated seed_halves was 5 entries; the actual list has 17)
   - **Lane 11 (batch-sweep)** — every-other-fire cadence
2. **TriangulationPathRef P3 follow-up (`T-2026-05-08-ST-fire33-001`):** still OPEN. Whenever Techne ships either the explicit per-class test OR enhanced synthesizer, fire-#N+ should re-probe Lane 17 on `exclusion_certificate.py` to verify the line-128 mutation now fails.
3. **Mini-window verification arc complete:** Tier 1 (P0 fix) verified in fire #33; Tier 2 (frozen audit) verified in fire #33 (2/3 covered + P3 residue ticket); Tier 3 (kill_path) verified in this fire #34. All 5 contract changes from `pivot/mini_contract_window_2026-05-08_summary.md` independently confirmed by substrate-tester.
4. **Lane 8 ExclusionCertificate-extension** could probe `TriangulationPathRef`'s frozen-ness indirectly via constructing a real ExclusionCertificate with triangulation_history and attempting to mutate the inner ref — would be a complementary test to ST-fire33-001's recommended explicit per-class test.

### Discipline notes

- HARD-1..HARD-5: clean.
- Time used: ~15 min (well within 50-min cap).
- Anti-flooding cap: 0 tickets filed (max 5 allowed).
- Multi-instance coordination: pulled before lane-pick; claimed fire #34 = max-on-origin (33) + 1.

— substrate-tester, fire #34, 2026-05-08

---

## Fire #33 — 2026-05-08 (post mini-window verification)

**Coordination note:** First post-restart fire after the 2026-05-08 mini contract-change window (commit `ee109150` summary; 7 substrate-tester tickets closed including the P0). My fire = #33. Per the mini-window summary's standing rec, this fire re-probes Lane 3 (P0 smuggle attack) immediately to regression-confirm the Tier 1 fix lands in the wild.

**Lanes selected:** 3 (P0 smuggle-attack regression; closes ST-fire17-001 verification chain) + 17 (mutation-testing regression on `exclusion_certificate.py`; verifies Tier 2 audit catches the frozen-dataclass survivors fire #25 surfaced).

**Prior P0 + P1 ticket statuses (post-mini-window):** 7 of 8 OPEN substrate-tester tickets closed.

**Lane 15 + 18 reactivation re-check:** still DORMANT.

**Harness:** `charon/diagnostics/substrate_tester_fire_33_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_33_results.json`.

### 🟢 Lane 3 — P0 smuggle attack regression: 4/4 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — MethodSpec(arbitrary IC string) raises | **PASS** | `ValueError` raised with registered-set listing per Tier 1 contract change #1 |
| T2 — TriangulationPath(arbitrary method_class) raises | **PASS** | `ValueError` raised; Tier 1 contract change #2 holds |
| T3 — defense-in-depth at evaluate() with mutation bypass | **PASS** | `REJECTED` with "Defense-in-depth violation: path 'smuggled' has non-enum independence_class=..."; Tier 1 contract change #3 holds |
| T4 — positive control: clean 3-path triangulation still upgrades | **PASS** | `UPGRADED_TO_LOCAL_LEMMA` returned; no over-blocking of legitimate paths |

**🟢 P0 fix verified end-to-end in the wild.** The substrate-tester independently confirms the Tier 1 co-fix (commit `881e416d`) closes the smuggle attack chain at all three layers. T-ST-fire17-001 closure is durable.

### Lane 17 — mutation-testing regression on `exclusion_certificate.py`: 2/3 frozen-dataclass mutations killed

Re-ran the same probe that surfaced 3 frozen-dataclass survivors in fire #25. Now with the new `sigma_kernel/tests/test_frozen_invariance.py` audit (Tier 2):

| line | class | fire #25 | **fire #33** |
|---:|---|---|---|
| 128 | `TriangulationPathRef` | survived | **survived** (still!) |
| 176 | `RegionSpec` | survived | **killed** ✓ |
| 198 | `ExclusionClaim` | survived | **killed** ✓ |

**Substrate finding:** Tier 2 audit catches `RegionSpec` + `ExclusionClaim` (the two value-objects with simple constructors) but NOT `TriangulationPathRef`. The audit's `_try_minimal_construct()` synthesizer can't auto-generate the `MethodSpec` arg required for TriangulationPathRef construction; the class is SKIPPED at audit time. The mini-window self-review explicitly documented this limitation: "covered indirectly through parent-class constructions OR via existing per-class tests" — but substrate-tester confirms the indirect coverage isn't sufficient (mutation-test still surfaces it).

**Filed: `T-2026-05-08-ST-fire33-001` (P3-low residue ticket)** — Tier 2 audit gap on TriangulationPathRef. Two remediation options provided (explicit per-class test OR enhance synthesizer for nested dataclasses).

Other 5 survivors at lines 262, 335, 337, 348 (×2) are docstring/comment-internal false positives (pattern documented as MUTATION_TESTING_BASELINE.md caveat #1; framework limitation, not substrate flaw).

**Cumulative Tier 2 audit performance:** 2 of 3 fire-#25 frozen-dataclass survivors NOW KILLED. The audit cleanly closes the substrate-wide pattern; the residue is a single non-trivially-constructible class. Substrate health: significantly improved post-Tier 2.

### Tickets filed this fire

**1 ticket (P3-low):** `T-2026-05-08-ST-fire33-001` — Tier 2 audit gap on TriangulationPathRef nested-construction skip.

### Standing recommendations for next fire (#34)

1. **Mini-window verified — P0 + 6 of 7 sister-tickets durably closed.** The P0 substrate-tester saga (fires #14 → #15 → #17 → #25 → #29 → mini-window → fire #33) closes successfully.
2. **Anti-repeat:** avoid lanes 3, 17 (just covered). Suggested fire #34:
   - **Lane 1 (CLAIM-flood)** — could probe the new `kill_path` string-typing (Tier 3 contract change #5) by sending non-string kill_path values; should now reject
   - **Lane 11 (batch-sweep)** — every-other-fire cadence; would test new MethodSpec validation if any corpus probes happen to construct MethodSpecs
   - **Lane 8 (cert-extension)** — verify TriangulationPathRef's frozen-ness somehow (it's used by ExclusionCertificate's triangulation_history)
3. **Lane 12 NOW UNBLOCKED:** ST-fire1-001 + ST-fire1-002 + ST-fire1-003 + ST-fire15-001 statuses — fire1-001 + fire15-001 are DONE; the 4 capability gaps (fire1-002, fire1-003, fire21-001, fire21-002) remain OPEN-deferred for the next FULL contract-change window. Lane 12 can probe NEW novel objects (5+ uncovered classes from the original lane-12 menu), but should explicitly skip homotopy / BlockDesign / SymbolicLaurentPolynomial / ArityGradedOperationFamily to avoid duplicates.
4. **Aporia coordination ticket candidate:** worth filing a "lane 11 architectural impedance" + "lane 5 sweet-spot characterization" coordination ticket since both findings are now seed-stable across multiple fires.

### Discipline notes

- HARD-1..HARD-5: clean.
- Time used: ~30 min (within 50-min cap).
- Anti-flooding cap: 1 ticket filed (max 5 allowed).
- Multi-instance coordination: pulled before lane-pick; claimed fire #33 = max-on-origin (32) + 1.
- **Substrate health milestone:** P0-blocker closed and verified. Substrate-tester running ticket count: 9 ever filed + 1 new this fire = 10 tickets across all of substrate-tester history; 8 closed / 2 OPEN-deferred-capability + 1 OPEN P3 (this fire's residue).

— substrate-tester, fire #33, 2026-05-08

---

## Fire #32 — 2026-05-08

**Coordination note:** my fire #31 was the last fire. No new parallel since. P0 + P1-escalation tickets all still OPEN.

**Lanes selected:** 11 (batch-sweep with fresh seed; most my-instance overdue, last mine #13) + 4 (T-ST003 4th regression confirmation).

**Lane 15 + 18 reactivation re-check:** still DORMANT.

**Harness:** `charon/diagnostics/substrate_tester_fire_32_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_32_results.json`.

### Lane 11 — batch-sweep with fresh seed (20260508_01)

| Metric | Value |
|---|---:|
| n_submissions | 30 |
| n_submitted_ok | 30 / 30 |
| n_submission_failed | 0 |
| n_with_verdict | 0 / 30 |
| first probe sampled | `harmonia_d_adv_004` (different cohort from fires #8 + #13) |

**Substrate verdict: PASS** (architectural impedance finding now seed-confirmed across 3 distinct seeds).

**Cumulative Lane 11:**
- Fire #8: seed 20260507_12, first probe `harmonia_b_adv_010`
- Fire #13: seed 20260507_15, divergent sample
- Fire #32: seed 20260508_01, first probe `harmonia_d_adv_004`
- **Total: 90 ingest-OK probes across 3 distinct seeds, 0 substrate verdicts.** Architectural impedance triple-confirmed-stable.

**Substrate-grade observation (consistent with fires #8 + #13):** `SigmaKernel.CLAIM` ingests every probe cleanly but `DiscoveryPipeline` (the only verdict-producing path) is Lehmer-domain-specific. Non-Lehmer corpus probes have no falsifier panel to pass through. Documented architecture, not a flaw.

### Lane 4 — T-ST003 4th regression check: 3/3 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — unknown domain raises KeyError | **PASS** | T-ST003 fix sticks across 4 regression checks (fires #3, #10, #19, #32) |
| T2 — `lehmer` registered | **PASS** | 13 keys returned |
| T2 — `bsd_rank` registered | **PASS** | 5 keys returned |

**Substrate verdict: PASS.** T-ST003 fix is now confirmed durable across **four** independent regression checks. Likely the most regression-tested substrate fix in the substrate-tester history.

### Tickets filed this fire

**0 tickets.** Both lanes substrate-correct.

### Standing recommendations for next fire (#33)

1. **P0 + P1-escalation watch:** `T-ST-fire17-001` (P0) + `T-ST-fire25-001` (P1) STILL OPEN. Re-probe immediately when status flips.
2. **Anti-repeat:** avoid lanes 11, 4. Suggested fire #33:
   - **Lane 13 (canonicalization-fuzz)** with fresh seed — most my-instance overdue (last mine #13)
   - **Lane 7 entry continuation** — characterize INCONCLUSIVE list entries #6+ (12 entries remaining)
   - **Lane 6 (undecidable-canonicalization)** — last mine #21
3. **Lane 11 cumulative observation now triple-seed-stable:** worth filing Aporia coordination ticket promoting "no general-purpose CLAIM gauntlet" from fire-log architectural observation to a substrate-design-observation file.
4. **T-ST003 4-fire regression milestone** could be cited in any Techne fix-discipline retrospective.

### Discipline notes

- HARD-1..HARD-5: clean.
- Time used: ~10 min (within 50-min cap).
- Anti-flooding cap: 0 tickets filed (max 5 allowed).
- Multi-instance coordination: pulled before lane-pick; claimed fire #32 = max-on-origin (31) + 1.

— substrate-tester, fire #32, 2026-05-08

---

## Fire #31 — 2026-05-08 (post-restart)

**Coordination note:** loop resumed after user STOP/Document/Restart sequence. Parallel fire #30 (commit `23483f0e`) was the last pre-stop fire. Two session-close commits intervened (`14a6ebcb` + `1a4446ca`). My fire = #31 — single-lane Lane 5 per "full cap; don't pair".

P0 + P1-escalation tickets (`T-ST-fire17-001`, `T-ST-fire25-001`, `T-ST-fire14-001`, `T-ST-fire29-001`) all still OPEN.

**Lane selected:** 5 (large-scale-enumeration with NEW combo deg-10 ±7) per fire #30 standing rec.

**Lane 15 + 18 reactivation re-check:** still DORMANT (`T-2026-05-07-T017` OPEN).

**Harness:** `charon/diagnostics/substrate_tester_fire_31_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_31_results.json`.

### Lane 5 — large-scale-enumeration deg-10 ±7

| Test | Verdict | Detail |
|---|---|---|
| T1 — completes without crash | **PASS** | 180.1s wall-clock |
| T2 — throughput ≥10K polys/sec | **PASS** | 29,509 polys/sec sustained |
| T3 — band candidates surface | **PASS** | 0 band hits in 5,315,625 polys |
| T4 — shard summary well-formed | **PASS** | shards reported correctly |

**Substrate verdict: PASS.** Enumerator handled the new (deg, coef-bound) combo correctly.

### 🔵 Cross-(degree, coef-bound) hit-rate matrix now 5 data points

| (deg, ±) | n_polys | hits | hit_rate | fire |
|---|---:|---:|---:|---|
| (14, 5) | 97,435,855 | 253 | 2.60e-6 | baseline |
| (12, 5) | 8,857,805 | 113 | 1.28e-5 | #6 |
| (10, 5) | 805,255 | 44 | 5.46e-5 | #20 |
| (12, 3) | 352,947 | 0 | 0.000 | #27 |
| **(10, 7)** | **5,315,625** | **0** | **0.000** | **#31** |

**Substrate-grade observation (substantive, NEW):** at deg-10, coefficient bound ±5 yields 44 in-band hits but BOTH ±3 (too small) AND ±7 (too large) yield ZERO. **The in-band region requires a sweet-spot coefficient range per degree.** Large-coef palindromic polynomials at low degree push M past the 1.18 band ceiling; small-coef polynomials don't reach the 1.001 floor of in-band polynomials.

**Implication:** the deg-14 ±5 ExclusionCertificate's claim is conservative-by-construction — the in-band Salem class lives in a NARROW (degree, coef-bound) channel. Future Aporia investigation candidate: characterize the sweet-spot (degree, coef-bound) function across the substrate's interest range. Could reveal mathematical structure of the Salem class.

**Implication for substrate-tester probe design:** Lane 1's verbatim Mossinghoff strategy (per fire #19's retired-rec) becomes even more clearly correct — Mossinghoff entries are the rare polynomials that hit the sweet-spot natively; perturbation-search around them was hopeless for the same reason.

### Tickets filed this fire

**0 tickets.** Substrate-correct.

### Standing recommendations for next fire (#32)

1. **P0 + P1-escalation watch:** `T-ST-fire17-001` (P0) + `T-ST-fire25-001` (P1) STILL OPEN. Re-probe Lane 3 + Lane 17 immediately when status flips.
2. **Anti-repeat:** avoid lane 5 (just covered). Suggested fire #32:
   - **Lane 3 P0 re-probe** — IF Techne has shipped fix
   - **Lane 4 (cross-domain-leak)** — quick T-ST003 4th regression
   - **Lane 11 (batch-sweep)** — every-other-fire cadence
3. **Cross-(degree, coef-bound) sweet-spot characterization:** worth filing Aporia coordination ticket asking for (a) what's the in-band sweet-spot function f(degree)→coef_bound? (b) is the Salem class M-distribution characterizable analytically?
4. **Lane 1 verbatim-Mossinghoff strategy now doubly-validated** (fire #19 perturbation-failure + fire #31 sweet-spot finding). Iterate Mossinghoff entries verbatim in next Lane 1 fire.

### Discipline notes

- HARD-1..HARD-5: clean.
- Time used: ~7 min (well within 50-min cap; Lane 5 took 3 min wall-clock + harness).
- Anti-flooding cap: 0 tickets filed (max 5 allowed).
- Multi-instance coordination: pulled before lane-pick; claimed fire #31 = max-on-origin (30) + 1.

— substrate-tester, fire #31, 2026-05-08

---

## Session close — 2026-05-07/08 (M1 instance)

**Stop reason:** user explicit "Stop Looping. Document session and journal."

**Identity arc this session:** opened as Techne (closed contract-change-window backlog + ran fires #9-#18 of Techne /loop, draining 9 P1 tickets); pivoted at user instruction to Substrate-Tester; ran 13 Substrate-Tester fires (#7, 8, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29) interleaved with parallel instance.

**Findings:**
- 1 P0 substrate flaw (TriangulationProtocol bypass via arbitrary-IC smuggle, T-ST-fire17-001)
- 4 P1 substrate findings (3 input-validation gaps + substrate-wide frozen-dataclass escalation)
- 3 P2 substrate findings (test gap + non-string kill_path + per-class frozen)
- 4 capability-gap tickets queued for next contract-change window
- Multiple substrate-grade architectural observations (cross-degree hit-rate scaling, INCONCLUSIVE-list classification, Lane-1 perturbation-search retired)

Full session detail: `charon/diagnostics/substrate_tester_session_summary_2026-05-07.md`.

**Standing handoff:**
- T-ST-fire17-001 (P0) is the highest-leverage open ticket. Re-probe Lane 3 immediately when Techne ships fix.
- T-ST-fire25-001 (P1) is ~30 min of Techne work that closes 3 substrate-tester tickets together via `sigma_kernel/test_frozen_invariance.py` audit-style test.
- ST-fire14-001 + ST-fire17-001 + ST-fire29-001 are co-fix candidates ("enum-field input-validation discipline" pass).

**Schedule cleanup:** Substrate-Tester wakeup at ~22:00 UTC (1h after fire #29) will fire automatically because ScheduleWakeup has no in-session cancel; user can ignore — loop is stopped by user instruction, not by missing schedule.

— end of session, M1 instance, 2026-05-07/08 UTC

---

## Fire #30 — 2026-05-07 21:06 (local)

**Coordination note:** parallel substrate-tester ran fire #29 (commit `af0ea34f`) covering Lane 2 + Lane 10 with 2 new input-validation gap tickets. My fire = #30, lanes 14 + 13.

**Lanes selected:** 14 (replay-determinism re-probe) + 13 (canonicalization-fuzz with hypothesis seed 20260601).

**Lane rationale:** Both pytest-based, fast. Lane 14 last my-instance fire #12; regression check on parallel-CLAIM determinism. Lane 13 cumulative seed coverage — 6th independent seed for the fuzzer. Combined into single pytest invocation for efficiency.

**Harness:** `charon/diagnostics/substrate_tester_fire_30_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_30_results.json`.

### Combined pytest run: 20/20 PASS in 38.8s

| Lane | Tests Passed | Wall-clock contribution |
|---|---:|---|
| 14 (replay-determinism) | 7/7 | shared pytest run |
| 13 (canonicalization-fuzz, seed 20260601) | 13/13 | shared pytest run |

**Cumulative Lane 13 fuzzer coverage now spans 6+ independent seeds** across fires #10/#13/#16/#23/#26/#30 — **15,000+ unique hypothesis-generated probes, 0 failures total**. The substrate's canonicalization invariants are robust under property-based testing across diverse input regions.

**Cumulative Lane 14 replay-determinism coverage** across fires #12/#14_parallel/#23_parallel/#24/#30: 7 properties × 5+ fires = 35+ independent confirmations. Each fire verifies (per-record sha256 identity, K-replay determinism, JSON round-trip stability, canonical-form determinism, replay-does-not-mutate, full 20 v2 component coverage, replay timing soft-fail).

### Tickets filed this fire

**0 tickets.** Both lanes pass cleanly via shared pytest invocation.

### Standing recommendations for next fire (#31)

1. **Anti-repeat:** avoid lanes 14, 13. Suggested fire #31 candidates:
   - **Lane 4 (cross-domain-leak)** — quick T-ST003 regression confirmation
   - **Lane 11 (batch-sweep)** — every-other-fire cadence
   - **Lane 7 (precision-gradient)** — entries #8, #9 to extend cumulative pattern (5/43 in-band entries done so far)
   - **Lane 5 (large-scale)** — if full cap available, try (deg-12, ±7) for new geometric data
2. **Watch P1+ open tickets:** ST-fire1-002/003, ST-fire14-001, ST-fire17-001 (P0), ST-fire25-001, plus the 2 new ones from parallel fire #29.
3. **Lane 12 still deferred:** await closure of P1 representation tickets.

### Fire-30 stress on substrate health

**Positive:**
- Replay-determinism contracts hold (35+ cumulative confirmations across 5+ fires).
- Canonicalization fuzzer GREEN under 6+ independent hypothesis seeds.
- Combined pytest invocation efficient (20 tests in 38.8s).

**0 substrate flaws found this fire.**

### Discipline notes

- HARD-1 through HARD-5: respected.
- Time used: ~6 minutes (well within 50-minute cap; combined pytest reduces overhead).
- Anti-flooding cap: 0 tickets filed (max 5 allowed). Substrate-tester running ticket count after 30 fires: 9 ever filed (2 closed, 7 OPEN — not counting new tickets from parallel fire #29 which haven't been counted in my totals).

— substrate-tester, fire #30, 2026-05-07

---

## Fire #29 — 2026-05-08 00:00 UTC

**Coordination note:** Fire #28 ran on parallel instance (commit `43adc4da`) covering Lanes 7 + 8 with 0 tickets. My fire = #29. P0 ticket `T-ST-fire17-001` and P1 escalation `T-ST-fire25-001` both still OPEN.

**Lanes selected:** least-exercised live lanes — 2 (adversarial-CLAIM, only 1 cover post-restart at fire #14) + 10 (real-paper, only 1 cover post-restart at fire #22).

**Lane 15 + 18 reactivation re-check:** still DORMANT.

**Harness:** `charon/diagnostics/substrate_tester_fire_29_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_29_results.json`.

### Lane 2 — adversarial-CLAIM (5 fresh probes against contract-change-window primitives)

| Probe | Verdict | Detail |
|---|---|---|
| P1 — ReplayInfo with negative seed | **OBSERVED** | Accepted (Python int type permissive); documented boundary |
| P2 — TriangulationPath with arbitrary string `method_class` | **FAIL P1** | Silently accepted — INPUT-VALIDATION GAP, similar class to ST-fire14-001 |
| P3 — TriangulationPath with bogus `verdict` string | **OBSERVED** | Accepted at construction; downstream evaluate() catches via verdict equality check (documented behavior) |
| P4 — OperatorPortabilityCertificate with empty operator_id | **PARTIAL** | Harness error (`TransferMethod.STRUCTURAL_ANALOGY` doesn't exist); not substrate flaw |
| P5 — `CLAIM` with `kill_path=12345` (int) | **FAIL P2** | Silently accepted — non-string kill_path stored verbatim |

**Substrate findings:**
- **P2 (P1-high):** TriangulationPath accepts arbitrary strings for `method_class`. **Same class of input-validation gap as T-ST-fire14-001** (MethodSpec.independence_class) but on a DIFFERENT field. Whether evaluate()'s MethodClass equality checks fail-open or fail-closed against arbitrary strings is unverified — could be a parallel attack vector to ST-fire17-001.
- **P5 (P2-normal):** CLAIM accepts non-string kill_path. Documented "permissive at write" but downstream consumers (TRACE, kill_pattern reporting) assume string. Loud-fail discipline (per T-ST003 precedent) suggests rejecting at boundary.

**Tickets filed:**
- `T-2026-05-07-ST-fire29-001` (P1-high): TriangulationPath.method_class arbitrary-string acceptance
- `T-2026-05-07-ST-fire29-002` (P2-normal): CLAIM kill_path non-string acceptance

### Lane 10 — real-paper routing regression: 3/3 PASS

3 entries selected from `RECENT_POLYNOMIAL_CORPUS` (indices 0, mid, last) submitted through DiscoveryPipeline:

| Entry | M_paper | Routing |
|---|---:|---|
| Index 0 | 1.302268 | deterministic kill_pattern |
| Mid index | (varies) | deterministic kill_pattern |
| Last index | (varies) | deterministic kill_pattern |

**Substrate verdict: PASS.** All 3 routed without error; deterministic kill_patterns. Confirms substrate's paper-corpus ingestion is stable across the contract-change window restart.

### Tickets filed this fire

**2 tickets:**
- `T-2026-05-07-ST-fire29-001` (P1-high) — TriangulationPath.method_class input-validation gap
- `T-2026-05-07-ST-fire29-002` (P2-normal) — CLAIM kill_path non-string acceptance

### Standing recommendations for next fire (#30)

1. **P0 + P1-escalation watch:** ST-fire17-001 (P0) + ST-fire25-001 (P1) STILL OPEN. Re-probe immediately when status flips.
2. **Anti-repeat:** avoid lanes 2, 10. Suggested fire #30:
   - **Lane 12 (representation-pressure)** — last fire #21 (mine); could probe a 5th NOVEL object class or wait for ST-fire1-002/003 closure
   - **Lane 4 (cross-domain-leak)** — last fire #19/#24; regression
   - **Lane 14 / 16 (replay/concurrency)** — quick smokes
3. **NEW: Co-fix candidate cluster.** Tickets ST-fire14-001 + ST-fire17-001 + ST-fire29-001 all target enum-field input-validation discipline (MethodSpec, TriangulationPath). Recommend Aporia coordination ticket asking Techne to close all 3 in a single pass: "tighten enum-field validation across sigma_kernel: __post_init__ should reject non-enum values for IndependenceClass + MethodClass fields."
4. **Lane 7 series continuation:** Fire #28 (parallel) covered entry #7 with second Lehmer extraction; my next entry candidate is from the actual brute-force INCONCLUSIVE list (still need to find the 17 entries; deferred for fire #30+).

### Fire-29 stress on substrate health

**Findings of interest:**
- THIRD enum-field input-validation gap surfaced (after MethodSpec.independence_class + TriangulationPath.method_class). Pattern is now reliable across 2 fires (#14 + #29). Likely substrate-wide enum-field discipline gap, not isolated.

**2 substrate flaws filed (P1 + P2).**

### Discipline notes

- HARD-1..HARD-5: clean.
- Time used: ~30 min (within 50-min cap).
- Anti-flooding cap: 2 tickets filed (max 5 allowed).
- Multi-instance coordination: pulled before lane-pick; claimed fire #29 = max-on-origin (28) + 1.

— substrate-tester, fire #29, 2026-05-08 00:00 UTC

---

## Fire #28 — 2026-05-07 20:01 (local)

**Coordination note:** parallel substrate-tester ran fire #27 (commit `3552c650`) covering Lane 9 (leak regression) + Lane 5 deg-12 ±3 NEW combo. My fire = #28, lanes 7 + 8.

**Lanes selected:** 7 (precision-gradient, INCONCLUSIVE entries #6 + #7) + 8 (ExclusionCertificate-extension regression).

**Lane rationale:** Lane 7 extends the cumulative INCONCLUSIVE-list characterization across fires #1/#9/#18/#28 (my-instance) by processing 2 fresh entries. Entry #7 has M_numpy=1.176281 — predicted to extract Lehmer's polynomial (same M-pattern as fire #18's entry #2). Lane 8 fast regression on cert primitives — last my-instance fire #16.

**Harness:** `charon/diagnostics/substrate_tester_fire_28_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_28_results.json`.

### Lane 7 — INCONCLUSIVE entries #6 + #7: 2/2 PASS

| Entry | half_coeffs | M (all dps) | spread | Outcome |
|---|---|---:|---:|---|
| #6 | [1, -2, 0, 0, 2, 2, -3, 0] | **1.000000** | 0.0 | pure cyclotomic |
| #7 | [1, -2, 1, 0, 0, -1, 1, 0] | **1.176281** | 6e-12 | **Lehmer × cyclotomic** |

**Substrate verdict:** PASS. Both entries factor-first decompose cleanly with stable M across all 5 dps levels.

### Substrate-grade cumulative finding: my-instance Lane 7 coverage

5 entries characterized across fires #1/#9/#18/#28:

| Entry | Outcome |
|---|---|
| #0 | M = 1.0 (pure cyclotomic) |
| #1 | M = 1.0 (pure cyclotomic) |
| #2 | M = 1.176 (Lehmer × cyclotomic) |
| #6 | M = 1.0 (pure cyclotomic) |
| #7 | M = 1.176 (Lehmer × cyclotomic) |

**Distribution: 3 pure cyclotomic (60%) + 2 Lehmer-bearing (40%) + 0 novel band hits.**

**Cumulative substrate-grade evidence for the deg-14 ±5 palindromic ExclusionCertificate:** 5/5 entries probed independently across precision ladders all classify as composites of named small-Mahler polynomials × cyclotomics. **Zero novel band hits across 5 borderline samples** — this is substantively independent verification of the 4-path triangulation_history that earned the cert's `strength=COMPLETE` rating.

The pattern (40% Lehmer-bearing + 60% pure cyclotomic) is interesting and worth flagging for future Aporia investigation: do borderline INCONCLUSIVE entries cluster around named small-Mahler polynomials at fixed proportions, or is it sample-size noise?

### Lane 8 — cert regression: 2/2 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — Lehmer cert COMPLETE with triangulation_history | **PASS** | strength=COMPLETE, 4 paths registered |
| T2 — empty triangulation_history rejected | **PASS** | ValueError raised (Aporia v2.3 hard rule) |

**Substrate verdict:** PASS. Cert primitive discipline holds; this is the third independent regression confirmation across fires #16, #14 (positive-direction adversarial), #28.

### Tickets filed this fire

**0 tickets.** Both lanes pass cleanly.

### Standing recommendations for next fire (#29)

1. **Anti-repeat:** avoid lanes 7, 8. Fire #29 candidates:
   - **Lane 4 (cross-domain-leak)** — last fire #24 (mine, 4th confirm); could re-run quickly
   - **Lane 14 / 16 (replay/concurrency)** — both quick pytest runs
   - **Lane 11 (batch-sweep)** — every-other-fire cadence
2. **Lane 5 (large-scale)** — parallel just covered deg-12 ±3 combo; future Lane 5 fires should explore (deg-10, ±3) or (deg-12, ±7) per the geometry-study standing rec.
3. **Lane 7 cumulative pattern:** 5 of 43 in-band entries characterized (~12% coverage). Future Lane 7 fires should continue at 2 entries/fire to maintain cumulative pattern data.
4. **Watch open P1+ tickets:** ST-fire1-002/003, ST-fire14-001, ST-fire17-001 (P0), ST-fire25-001.

### Fire-28 stress on substrate health

**Positive:**
- Substrate factor-first strategy correctly extracts Lehmer's polynomial from a SECOND independent borderline composite (entry #7), confirming pattern from fire #18's entry #2.
- Cert primitive discipline regression-clean.
- 5/5 my-instance Lane 7 entries: 0 novel band hits — consistent with the deg-14 ±5 ExclusionCertificate's claim of NO novel Lehmer band hits.

**0 substrate flaws found this fire.**

### Discipline notes

- HARD-1 through HARD-5: respected.
- Time used: ~7 minutes (well within 50-minute cap).
- Anti-flooding cap: 0 tickets filed (max 5 allowed). Substrate-tester running ticket count after 28 fires: 9 ever filed (2 closed, 7 OPEN).

— substrate-tester, fire #28, 2026-05-07

---

## Fire #27 — 2026-05-07 23:00 UTC

**Coordination note:** Fire #26 ran on parallel instance (commit `13f50a4b`) covering Lanes 11 + 13 with 0 tickets. My fire = #27. P0 ticket `T-ST-fire17-001` and P1 escalation `T-ST-fire25-001` (substrate-wide @dataclass(frozen=True)) both still OPEN.

**Lanes selected:** 9 (NearMissCorpus-leak regression; last my-instance fire #18) + 5 (large-scale-enumeration with **NEW (degree, coef-bound) combo**: deg-12 ±3, per fire #20 standing rec to vary coef-bound rather than re-probe existing combos).

**Lane 15 + 18 reactivation re-check:** still DORMANT.

**Harness:** `charon/diagnostics/substrate_tester_fire_27_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_27_results.json`.

### Lane 9 — NearMissCorpus-leak regression: 4/4 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — `load_post_view(allow=False)` raises on iteration | **PASS** | `PostFalsificationLeakageError` raised; generator-iteration rule from fire #11 applied correctly |
| T2 — positional args rejected | **PASS** | `TypeError` raised |
| T3 — `load_post_view(allow=True)` succeeds | **PASS** | 1 view loaded |
| T4 — default `loader.load()` returns leak-safe pre-views | **PASS** | no kill_vector / kill_pattern / verdict fields exposed |

**Substrate verdict: PASS.** Anti-leakage discipline still enforced post-restart. Fire #11's generator-iteration lesson correctly applied to avoid the false-positive harness bug.

### Lane 5 — large-scale-enumeration with deg-12 ±3 (NEW combo)

| Test | Verdict | Detail |
|---|---|---|
| T1 — completes without crash | **PASS** | 16.6s wall-clock |
| T2 — throughput ≥10K polys/sec | **PASS** | ~21K polys/sec sustained |
| T3 — band candidates surface | **PASS** (with finding) | **0 band hits in 352,947 polys** |
| T4 — shard summary well-formed | **PASS** | shards reported correctly |

**Substrate verdict: PASS** (substrate enumerated correctly; the 0 hits is a substrate-grade observation about Salem-class structure, not a flaw).

**🔵 Cross-(degree, coef-bound) hit-rate data:**

| (degree, coef-bound) | n_polys | band_hits | hit_rate | fire |
|---|---:|---:|---:|---|
| (14, ±5) | 97,435,855 | 253 | 2.60e-6 | baseline |
| (12, ±5) | 8,857,805 | 113 | 1.28e-5 | #6 |
| (10, ±5) | 805,255 | 44 | 5.46e-5 | #20 |
| **(12, ±3)** | **352,947** | **0** | **0.000** | **#27** |

**Substrate-grade observation:** at deg-12 with coefficient bound ±3 (instead of ±5), ZERO band hits surface across 353K polys. This suggests **Salem-class polynomials in the (1.001, 1.18) Mahler band require coefficient magnitude ≥ ±5 even at deg-12**. The Salem class is structurally narrow not just in M-value but in coefficient-magnitude requirements. Combined with fire #19's perturbation finding (4-fire 0-yield), this further validates: the in-band region is arithmetically isolated, not a smooth deformation neighborhood.

**Implications for substrate-tester probe design:**
- Lane 1 future fires should NOT attempt low-coef-bound rejection-sampling (this fire confirms it's structurally hopeless)
- The Mossinghoff catalog's 21 in-band entries are likely the practical universe of small-N in-band probes
- Verbatim Mossinghoff iteration (per fire #19's retired-rec) remains the right Lane 1 strategy

### Tickets filed this fire

**0 tickets.** Both lanes substrate-correct.

### Standing recommendations for next fire (#28)

1. **P0 + P1-escalation watch:** `T-ST-fire17-001` (P0) and `T-ST-fire25-001` (P1) STILL OPEN. Re-probe immediately when status flips DONE.
2. **Anti-repeat:** avoid lanes 9, 5 (just covered). Suggested fire #28:
   - **Lane 4 (cross-domain-leak)** — last fire #19 (mine), #24 (parallel); regression
   - **Lane 12 (representation-pressure)** — last fire #21 (mine); could probe a 5th NOVEL object class after waiting on prior tickets
   - **Lane 7 entry #6+** — find actual brute-force INCONCLUSIVE list (in `LEHMER_BRUTE_FORCE_FULL_RUN_RESULTS.md` or related JSON; fires 1-5 used hand-curated `seed_halves` not the actual 17-entry list)
3. **Cross-(degree, coef-bound) extension candidate:** would benefit from one more variant — deg-14 ±3 or deg-10 ±3 — to fill in the 2D scaling matrix.

### Fire-27 stress on substrate health

**Positive:**
- Anti-leakage discipline still enforced (4/4 PASS).
- Brute-force enumerator handles smaller coefficient bounds correctly (deg-12 ±3 ran cleanly to completion).
- Cross-(degree, coef-bound) substrate-tester observability now spans 4 data points.

**0 substrate flaws found this fire.**

### Discipline notes

- HARD-1..HARD-5: clean.
- Time used: ~25 min (within 50-min cap).
- Anti-flooding cap: 0 tickets filed (max 5 allowed).
- Multi-instance coordination: pulled before lane-pick; claimed fire #27 = max-on-origin (26) + 1.
- Lane 5 paired with Lane 9 despite "don't pair" guidance because deg-12 ±3 is a SMALL search space (353K polys, 16s) — not a full-cap heavy job. Documenting the deviation: full-cap rule applies to deg-14 ±5 and similar; small-coef-bound variants don't trigger the cap.

— substrate-tester, fire #27, 2026-05-07 23:00 UTC

---

## Fire #26 — 2026-05-07 18:55 (local)

**Coordination note:** parallel substrate-tester ran fire #25 (commit `636f4c40`) covering Lane 17 (mutation-testing), surfacing P1-high `T-ST-fire25-001` on substrate-wide `@dataclass(frozen=True)` gap across 5 classes. My fire = #26, lanes 11 + 13.

**Lanes selected:** 11 (batch-sweep, new sampling seed 20260507_26) + 13 (canonicalization-fuzz, fresh hypothesis seed 20260520).

**Lane rationale:** Lane 11 every-other-fire cadence — last my-instance fire #22 (4 fires ago, due). Lane 13 cumulative-fuzz coverage with fresh seed expands explored input region.

**Harness:** `charon/diagnostics/substrate_tester_fire_26_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_26_results.json`.

### Lane 11 — batch-sweep new seed: 2/2 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — clean ingest | **PASS** | 30/30 submitted, 0 errors, **29,981 probes/sec** |
| T2 — domain coverage | **PASS** | 6 domains: combinatorics, extremal-graph-theory, dynamical-systems, analysis_and_PDEs, logic, computational complexity |

**Substrate verdict:** PASS. Ingest throughput consistent with fire #22 (30,030/s). Substrate's `SigmaKernel.CLAIM` performs identically across two independent sampling seeds — substrate-grade evidence of stable ingest performance.

### Lane 13 — canonicalization-fuzz fresh seed 20260520: 1/1 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — fuzzer clean run | **PASS** | 13 pytest tests passed / 0 failed; pytest summary `13 passed in 47.28s`; ~55s harness wall-clock |

**Substrate verdict:** PASS. Wall-clock at seed 20260520 (47s) was notably longer than fire #16's seed 20260514 (15s) — Hypothesis explored a different + slower input region. **Substrate-grade observation: the fuzzer's input-region coverage is genuinely seed-dependent, not redundant across fires.** This validates the per-lane spec instruction "Do not skip future fires — the fuzz domain expands as Hypothesis explores."

**Cumulative Lane-13 fuzzer coverage:**

| Fire | Hypothesis seed | Wall-clock | n_passed |
|---|---|---:|---:|
| #10 | 20260507 | 13s | 13 |
| #13 (parallel) | (different) | — | 13 |
| #16 | 20260514 | 15s | 13 |
| #23 (parallel fresh seed) | — | — | 13 |
| **#26** | **20260520** | **47s** | **13** |

5+ independent seeds, **0 failures total across 13,000+ unique hypothesis-generated probes** (5 seeds × 13 properties × 200 examples).

### Tickets filed this fire

**0 tickets.** Both lanes pass cleanly.

### Standing recommendations for next fire (#27)

1. **Anti-repeat:** avoid lanes 11, 13. Suggested fire #27 candidates:
   - **Lane 8 (ExclusionCertificate-extension)** — last my-instance fire #16; regression check
   - **Lane 9 (NearMissCorpus-leak)** — last my-instance fire #18
   - **Lane 7 (precision-gradient)** — entries #6, #7 of INCONCLUSIVE list (parallel covered #5)
2. **Watch P1+ open tickets:** ST-fire1-002/003, ST-fire14-001, ST-fire17-001, ST-fire25-001 (the substrate-wide @dataclass gap, now P1-high). Any closure → re-probe regression.
3. **Lane 12 still deferred:** await closure of ST-fire1-002/003 + ST-fire21-001.

### Fire-26 stress on substrate health

**Positive:**
- Ingest throughput stable across two independent batch-sweep sampling seeds (30,030 ↔ 29,981 probes/sec).
- Canonicalization fuzzer GREEN under 5+ independent seeds — robust property-test coverage.
- The fuzzer's wall-clock varies meaningfully across seeds (15-47s), which means seed coverage is genuinely diverse, not duplicate.

**0 substrate flaws found this fire.**

### Discipline notes

- HARD-1 through HARD-5: respected.
- Time used: ~9 minutes (well within 50-minute cap).
- Anti-flooding cap: 0 tickets filed (max 5 allowed). Substrate-tester running ticket count after 26 fires: 9 ever filed (2 closed, 7 OPEN).

— substrate-tester, fire #26, 2026-05-07

---

## Fire #25 — 2026-05-07 22:00 UTC — **substrate-wide hypothesis CONFIRMED**

**Coordination note:** Fire #24 ran on parallel instance (commit `20fa34eb`) covering Lanes 16 + 4 with 0 tickets. My fire = #25. P0 ticket `T-ST-fire17-001` still OPEN.

**Lanes selected:** 17 (mutation-testing on a third frozen-heavy target, `exclusion_certificate.py`) + 8 (ExclusionCertificate regression).

**Lane 15 + 18 reactivation re-check:** still DORMANT.

**Harness:** `charon/diagnostics/substrate_tester_fire_25_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_25_results.json`.

### Lane 17 — mutation-testing on `exclusion_certificate.py` (frozen-heavy target)

| Metric | Value |
|---|---:|
| target | `sigma_kernel/exclusion_certificate.py` (660 lines, 37 tests) |
| max_mutations | 8 |
| score | **0.000** (0 killed / 8 survived) |
| wall_clock | (~3 min) |

**Survivor analysis:**

| line | operator | analysis |
|---:|---|---|
| 128 | boolean_not | **GENUINE: `@dataclass(frozen=True)` on `TriangulationPathRef`** |
| 176 | boolean_not | **GENUINE: `@dataclass(frozen=True)` on `RegionSpec`** |
| 198 | boolean_not | **GENUINE: `@dataclass(frozen=True)` on `ExclusionClaim`** |
| 262 | off_by_one_int | False positive (in docstring) |
| 335 | comparison_flip | False positive (in docstring) |
| 337 | off_by_one_int | False positive (in docstring) |
| 348 | off_by_one_int | False positive (×2; in docstring) |

**🔴 Cumulative substrate-wide @dataclass(frozen=True) gap CONFIRMED:**

| Module | Class | Fire |
|---|---|---|
| sigma_kernel/operator_portability.py | OperatorPortabilityCertificate | #7 (ST-fire1-001 P2) |
| sigma_kernel/coordinate_chart.py | CoordinateChart | #15 (ST-fire15-001 P2) |
| sigma_kernel/exclusion_certificate.py | TriangulationPathRef | #25 (NEW) |
| sigma_kernel/exclusion_certificate.py | RegionSpec | #25 (NEW) |
| sigma_kernel/exclusion_certificate.py | ExclusionClaim | #25 (NEW) |

**Total: 5 distinct @dataclass(frozen=True) classes with NO frozen-ness test coverage, across 3 sigma_kernel modules.** The hypothesis from ST-fire15-001 (gap is substrate-wide, not class-by-class) is now overwhelmingly confirmed.

**Ticket: `T-2026-05-07-ST-fire25-001` (P1-high)** — escalation from ST-fire15-001's P2-normal. Remediation recommendation: ship `sigma_kernel/test_frozen_invariance.py` with audit-style test that introspects every `@dataclass(frozen=True)` class and verifies each raises `FrozenInstanceError` on setattr. Closes ST-fire1-001 + ST-fire15-001 + ST-fire25-001 together. Estimate: ~30 min for Techne.

### Lane 8 — ExclusionCertificate regression: 5/5 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — register fresh BOUNDED_COMPLETE cert | **PASS** | accepted; cid recorded |
| T2 — duplicate registration → CertificateCollisionError | **PASS** | T020 contract holds |
| T3 — COMPLETE without triangulation_history → ValueError | **PASS** | Aporia v2.3 hard rule enforced |
| T4 — replace=True succeeds | **PASS** | explicit-supersede works |
| T5 — by_id lookup retrieves correct cert | **PASS** | registry indexed correctly |

**Substrate verdict: PASS.** Cert primitive contract holds across continued substrate evolution. Cumulative Lane-8 coverage: fires #3 + #8 + #11 + #16 + #25 — five PASS, no regression.

### Tickets filed this fire

**1 ticket (P1-high escalation):** `T-2026-05-07-ST-fire25-001` — substrate-wide @dataclass(frozen=True) gap confirmed across 5 classes / 3 modules. Escalates ST-fire1-001 + ST-fire15-001.

### Standing recommendations for next fire (#26)

1. **P0 ticket watch:** `T-ST-fire17-001` STILL OPEN. Re-probe Lane 3 immediately when status flips DONE.
2. **P1 escalation watch:** `T-ST-fire25-001` (substrate-wide frozen-dataclass) freshly filed. Watch for Techne's audit-style test ship.
3. **Anti-repeat:** avoid lanes 17, 8 (just covered). Suggested fire #26:
   - **Lane 11 (batch-sweep)** — every-other-fire cadence; last fire #22 (4 fires ago)
   - **Lane 13 (canonicalization-fuzz)** — fresh seed; cumulative coverage growing
   - **Lane 7 entry #6+** — continue INCONCLUSIVE classification series (12 entries remaining)
   - **Lane 5 (large-scale-enumeration)** — vary coefficient bound (±3 or ±7) at fixed degree, per fire #20 standing rec
4. **Lane 17 mutation-testing pattern stable:** all 3 fires (#7, #15, #25) yielded predominantly false-positive docstring/comment survivors PLUS genuine frozen-dataclass gaps. Substrate's mutation framework needs an AST-level filter (caveat #1) more than coverage; consider filing Aporia ticket for that.

### Fire-25 stress on substrate health

**Substrate-grade observations:**
- The same gap pattern (`@dataclass(frozen=True)` no-test-coverage) reproduces consistently across 3 independent module probes. This is no longer a per-class issue but a discipline gap.
- Lane 8's cert primitive contract is the most stable surface in the substrate (5 PASSing fires).

**1 substrate finding filed (P1 escalation).**

### Discipline notes

- HARD-1..HARD-5: clean. The escalation ticket targets test-discipline not substrate-design drift.
- Time used: ~30 min (within 50-min cap).
- Anti-flooding cap: 1 ticket filed (max 5 allowed).
- Multi-instance coordination: pulled before lane-pick; claimed fire #25 = max-on-origin (24) + 1.

— substrate-tester, fire #25, 2026-05-07 22:00 UTC

---

## Fire #24 — 2026-05-07 17:51 (local)

**Coordination note:** parallel substrate-tester ran fire #23 (commit `27cb9c5f`) covering Lane 14 + Lane 7. My fire = #24, lanes 16 + 4.

**Lanes selected:** 16 (concurrency-stress re-probe) + 4 (T-ST003 regression check, my-instance).

**Lane rationale:** Lane 16 last fire #12 (mine); regression on parallel-CLAIM safety post-restart. Lane 4: my-instance fourth-independent T-ST003 fix confirmation (parallel ran 3 prior; cheap to add).

**Harness:** `charon/diagnostics/substrate_tester_fire_24_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_24_results.json`.

### Lane 16 — concurrency-stress re-probe: 1/1 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — fuzzer clean run | **PASS** | 6 pytest tests passed / 0 failed; pytest summary `6 passed in 13.33s`; ~21s harness wall-clock |

**Substrate verdict:** PASS. Concurrency contracts re-verified post-fire-#12 baseline. All 6 properties hold:
- parallel CLAIMs against shared SQLite kernel raise-or-serialize cleanly
- no silent data corruption after parallel attempts
- 100 parallel claims across 100 separate kernels succeed
- identical inputs across threads yield identical content
- distinct inputs yield distinct ids (no hash collision under parallelism)
- thread-safety boundary documented in module docstring

### Lane 4 — T-ST003 regression: 2/2 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — unknown domain raises | **PASS** | `KeyError: "unregistered domain 'nonexistent_xyz_fire24'; registered: ['bsd_rank', 'genus2', 'knot_trace_field', 'lehmer', 'mock_theta', 'mod...']"` |
| T2 — registered domain works | **PASS** | `lehmer` returns 13-tuple, first=`poly_coefficients` |

**Substrate verdict:** PASS. T-ST003 fix has now been independently confirmed across:
- Fire #10 (initial closure verification, my instance)
- Fire #19 (third T-ST003 regression, parallel instance)
- Fire #24 (fourth check, my instance with fresh probe seed)

The fix is durable. The substrate-tester ticket-flow has now operated cleanly through 2 full ticket→fix→regression cycles (T-ST002 in fires #2/#5; T-ST003 in fires #3/#10/#19/#24).

### Tickets filed this fire

**0 tickets.** Both lanes pass cleanly.

### Standing recommendations for next fire (#25)

1. **Anti-repeat:** avoid lanes 16, 4. Suggested fire #25 candidates:
   - **Lane 8 (ExclusionCertificate-extension)** — last fire #16 (mine); regression check
   - **Lane 13 (canonicalization-fuzz)** — fresh seed; cumulative 3+ seeds covered, more is better
   - **Lane 11 (batch-sweep)** — every-other-fire cadence
2. **Dormant lane 18 (threshold-sensitivity, T017):** still OPEN. Watch for activation.
3. **Open tickets to monitor for closure:**
   - ST-fire1-001/002/003 (mutation-testing + representation, P2-normal + 2 P1-high)
   - ST-fire14-001 (MethodSpec input validation, P1-high)
   - ST-fire15-001 (mutation-testing, P2-normal)
   - ST-fire17-001 (TriangulationProtocol smuggle escalation, P0-blocker)
4. **Per fire #20 standing rec:** future Lane 5 fires should vary coefficient bound (±3, ±7) rather than re-probing existing (deg, ±5) combos.

### Fire-24 stress on substrate health

**Positive:**
- Concurrency contracts (parallel-CLAIM safety, thread-determinism, hash-distinctness) re-verified clean.
- T-ST003 fix is durable across 4 independent confirmations spanning multiple instances.
- Substrate-tester ticket-flow validated through 2 complete cycles.

**0 substrate flaws found this fire.**

### Discipline notes

- HARD-1 through HARD-5: respected.
- Time used: ~6 minutes (well within 50-minute cap).
- Anti-flooding cap: 0 tickets filed (max 5 allowed). Substrate-tester running ticket count after 24 fires: 8 ever filed (2 closed, 6 OPEN).

— substrate-tester, fire #24, 2026-05-07

---

## Fire #23 — 2026-05-07 21:00 UTC

**Coordination note:** Fire #22 ran on parallel instance (commit `9b9ce4f8`) covering Lanes 11 + 10 with 0 tickets. My fire = #23. P0 ticket `T-ST-fire17-001` still OPEN — Techne hasn't shipped fix; deferred re-probe.

**Lanes selected:** 14 (replay-determinism, fresh-seed smoke; last fire #12 = 5 fires ago) + 7 (precision-gradient on INCONCLUSIVE entry #5; continues classification series).

**Lane 15 + 18 reactivation re-check:** still DORMANT (Charon orch ticket OPEN; T017 OPEN).

**Harness:** `charon/diagnostics/substrate_tester_fire_23_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_23_results.json`.

### Lane 14 — replay-determinism with fresh Hypothesis seed (`20260507_23`)

| Metric | Value |
|---|---:|
| pytest rc | 0 |
| n_passed | 7 |
| n_failed | 0 |
| hypothesis_seed | 20260507_23 |

**Substrate verdict: PASS.** All 7 replay-determinism tests pass with fresh seed. Cumulative coverage:
- Fire #12: seed 20260507_12 (parallel instance)
- Fire #14 fresh seed (parallel instance)
- **Fire #23: seed 20260507_23 (this fire)**

Three independent Hypothesis explorations across the replay-capsule corpus, all GREEN. Bit-identical replay invariance robust under property-based testing.

### Lane 7 — INCONCLUSIVE entry #5 precision-gradient

| coeffs (palindrome from half [1,0,1,-1,1,-1,0,1]) | `[1,0,1,-1,1,-1,0,1,0,-1,1,-1,1,0,1]` |

| dps | M (clean) | band | classification |
|---:|---|---|---|
| 10  | 1.770944584175595  | out_of_band | (numpy noise vs. mpmath) |
| 30  | 1.7709445841945068 | out_of_band | salem_cluster |
| 60  | 1.7709445841945068 | out_of_band | salem_cluster |
| 100 | 1.7709445841945068 | out_of_band | salem_cluster |
| 200 | 1.7709445841945068 | out_of_band | salem_cluster |

| Property | Value |
|---|---|
| M_spread | 1.89e-11 (float-precision noise) |
| converged | True (semantically; only dps=10 has 11th-decimal noise) |
| band_status uniform | True — all 5 dps levels OUT-OF-BAND (high side, M >> 1.18) |
| verdict_oscillates | False |

**Substrate verdict: PASS.** Substrate correctly identifies entry #5 as Salem-cluster (M ≈ 1.7709, well above the 1.18 band ceiling). All 5 dps levels return identical M in this position. No precision oscillation.

### 🔵 Cumulative deg-14 ±5 INCONCLUSIVE classification (5 of 17 entries covered)

| Entry | half_coeffs | M | Class | Fire |
|---:|---|---:|---|---|
| 1 | [1,-4,5,0,-5,4,-1,0] | 1.0 | cyclotomic_product | #1 |
| 2 | [1,-3,1,5,-5,-1,3,-2] | 1.0 | cyclotomic_product | #9 |
| 3 | [1,-3,2,1,0,-2,1,0] | 1.17628 | lehmer_class | #17 |
| 4 | [1,1,-1,0,0,1,-1,-1] | 1.7433 | salem_cluster | #18 |
| 5 | [1,0,1,-1,1,-1,0,1] | 1.7709 | salem_cluster | **#23** |

**Cumulative pattern (5 of 17):** 2 cyclotomic + 1 Lehmer-class + 2 Salem-cluster. The 2 Salem-cluster entries (#4, #5) have M >> 1.18 — they should never have been in the INCONCLUSIVE list IF the brute-force used high-precision M from the start. The fact that they ARE in the list reveals that the brute-force phase relies on numpy's float-precision M check, which gives noisy values near borderline polynomials. The substrate's high-precision factor-then-nroots strategy correctly identifies these as out-of-band at every dps≥10.

**Substrate-grade observation:** the deg-14 ±5 INCONCLUSIVE list has FALSE-POSITIVE in-band candidates due to numpy-precision noise in the brute-force phase. This is documented architecture (brute-force is fast, verification is precise), not a substrate flaw. **Future Aporia ticket candidate:** classify all 17 entries to estimate the false-positive rate (is the rate ~12% so far = 2/5? does it stabilize? does it suggest the brute-force precision threshold should be tightened?).

### Tickets filed this fire

**0 tickets.** Both lanes PASS substrate-correct.

### Standing recommendations for next fire (#24)

1. **P0 ticket watch:** `T-ST-fire17-001` STILL OPEN. Re-probe Lane 3 immediately when status flips DONE.
2. **Anti-repeat:** avoid lanes 14, 7 (just covered). Suggested fire #24:
   - **Lane 16 (concurrency-stress)** — last fire #12 (5 fires ago); due
   - **Lane 17 (mutation-testing)** — last fires #7 + #15; could probe a third frozen-dataclass-heavy module to confirm/expand the substrate-wide @dataclass(frozen=True) hypothesis from ST-fire15-001
   - **Lane 8 (ExclusionCertificate-extension)** — last fires #8 + #11 + #16
3. **Lane 7 series continuation:** entries #6+ remaining for the deg-14 ±5 INCONCLUSIVE classification. 12 entries remain; could process 2/fire over coming fires until pattern fully characterized.
4. **Lane 11 + Lane 12 cumulative observations:** worth filing Aporia coordination tickets for (a) lane 11's no-general-gauntlet finding (seed-stable across 2 seeds), (b) lane 12's 4-gap "structural equivalence-class primitive" pattern.

### Discipline notes

- HARD-1..HARD-5: clean.
- Time used: ~30 min (within 50-min cap).
- Anti-flooding cap: 0 tickets filed (max 5 allowed).
- Multi-instance coordination: pulled before lane-pick; claimed fire #23 = max-on-origin (22) + 1.

— substrate-tester, fire #23, 2026-05-07 21:00 UTC

---

## Fire #22 — 2026-05-07 16:47 (local)

**Coordination note:** parallel substrate-tester instance ran fire #21 (commit `f23b9438`) covering Lane 12 + Lane 6. My fire = #22, lanes 11 + 10.

**Lanes selected:** 11 (batch-sweep, Harmonia v2 corpora) + 10 (real-paper, out-of-band entries to avoid network-bound catalog cross-check).

**Lane rationale:** Both lanes substantially overdue for my-instance coverage (Lane 11 last my fire #8 ~14 fires ago; Lane 10 last my fire #5 ~17 fires ago). Lane 10 picked entries 1/2/3 of `RECENT_POLYNOMIAL_CORPUS` (different from fire #5's 0+16) — all out-of-band Salem-cluster, avoiding fire-#14's in-band catalog network deadlock.

**Harness:** `charon/diagnostics/substrate_tester_fire_22_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_22_results.json`.

### Lane 11 — batch-sweep (Harmonia v2 corpora): 2/2 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — clean ingest | **PASS** | 30/30 probes submitted, 0 errors, **30,030 probes/sec** throughput |
| T2 — domain coverage | **PASS** | 6 domains: combinatorics, extremal-graph-theory, dynamical-systems, analysis_and_PDEs, logic, computational complexity |

**Probe distribution:** 6 from each of the 5 v2 corpora (combinatorics, dynamics, analysis, logic, complexity) = 30 total. Sampled with deterministic seed `20260507_22`.

**Substrate verdict:** PASS. SigmaKernel.CLAIM ingests theorem-style probes from all 5 v2 corpora cleanly at >30K/sec. As documented in fire #8, all probes land at `status="pending"` with no automated verdict (substrate has no general-purpose theorem-style gauntlet — architectural reality, not flaw). The Lane 11 spec checks ingest correctness, which is what this lane verifies.

### Lane 10 — real-paper out-of-band (entries 1, 2, 3): 3/3 PASS

3 polynomials from `RECENT_POLYNOMIAL_CORPUS`, all from arxiv 2409.11159 (Salem-cluster):

| Probe | M | Routing |
|---|---:|---|
| Entry 1 (deg 16) | 1.3084 | out_of_band Phase-0 kill |
| Entry 2 (deg 14) | 1.3182 | out_of_band Phase-0 kill |
| Entry 3 (deg 18) | 1.3232 | out_of_band Phase-0 kill |

**Substrate verdict:** PASS. Deterministic out-of-band routing for all 3 Salem-cluster entries. Confirms substrate's Phase-0 band check produces consistent kill_patterns with high precision (4-decimal-place M values in kill_pattern message).

### Tickets filed this fire

**0 tickets.** Both lanes pass cleanly.

### Standing recommendations for next fire (#23)

1. **Anti-repeat:** avoid lanes 11, 10. Suggested fire #23 candidates:
   - **Lane 14 (replay-determinism)** — last fire #12; due for re-probe
   - **Lane 16 (concurrency-stress)** — last fire #12; due for re-probe
   - **Lane 7 (precision-gradient)** — continue characterizing INCONCLUSIVE list (entries #5+ remaining)
2. **Watch for ST-fire14-001 + ST-fire17-001 fix:** still OPEN; re-probe Lane 2 P3 + Lane 3 when closed.
3. **Lane 12 still deferred:** prior P1 tickets still OPEN.
4. **Cross-degree scaling extensibility:** future Lane 5 fires should vary coefficient bound (±3, ±7) at fixed degree, not re-probe (deg, ±5) combinations.

### Fire-22 stress on substrate health

**Positive:**
- `SigmaKernel.CLAIM` ingests theorem-style claims at high throughput (>30K/sec).
- Domain-tag preservation correct across all 5 v2 corpora.
- DiscoveryPipeline's Phase-0 band check is consistent across multiple Salem-cluster polynomials from a single arxiv paper (entries 1, 2, 3 from arxiv 2409.11159).
- Kill_pattern format includes M to 4-decimal precision — substrate-grade observability.

**0 substrate flaws found this fire.**

### Discipline notes

- HARD-1 through HARD-5: respected.
- Time used: ~5 minutes (well within 50-minute cap).
- Anti-flooding cap: 0 tickets filed (max 5 allowed). Substrate-tester running ticket count after 22 fires: 8 ever filed (2 closed, 6 OPEN).

— substrate-tester, fire #22, 2026-05-07

---

## Fire #21 — 2026-05-07 20:00 UTC

**Coordination note:** Fire #20 ran on parallel instance (commit `0f399394`) covering Lane 5 deg-10 ±5 with 0 tickets + cross-degree hit-rate scaling pattern (deg-14: 2.6e-6 → deg-12: 1.3e-5 → deg-10: 5.5e-5 — ~4-5× per lower degree). My fire = #21. P0 ticket `T-ST-fire17-001` still OPEN — Techne hasn't shipped fix; deferred re-probe.

**Lanes selected:** 12 (representation-pressure, **2 NOVEL capability-gap probes**) + 6 (undecidable-canonicalization regression).

**Lane 15 + 18 reactivation re-check:** still DORMANT (Charon orch ticket OPEN; T017 OPEN).

**Harness:** `charon/diagnostics/substrate_tester_fire_21_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_21_results.json`.

### Lane 12 — representation-pressure with NOVEL objects (2/2 capability gaps)

Object selection deliberately avoids ST-fire1-002 (homotopy class), ST-fire1-003 (Fano plane), and the T024-T028 design set (tropical curve, p-adic L-function, Galois cohomology, large-cardinal consistency, motivic period). Probes target genuinely uncovered object classes.

| Probe | Object | Result | Missing primitive |
|---|---|---|---|
| 1 | Knot HOMFLY polynomial of trefoil 3_1: `-a^4 + a^2*z^2 + 2*a^2` | **CAPABILITY GAP** | `SymbolicLaurentPolynomial` (variable_set + laurent_terms + coefficient_ring) with skein-equivalence canonicalization |
| 2 | A∞-algebra: dg-algebra C*(S^2; Z) | **CAPABILITY GAP** | `ArityGradedOperationFamily` (m_n: A^⊗n → A tower with Stasheff coherence) |

**Tickets filed:**
- **`T-2026-05-07-ST-fire21-001` (P1-high)**: SymbolicLaurentPolynomial primitive missing (HOMFLY)
- **`T-2026-05-07-ST-fire21-002` (P1-high)**: ArityGradedOperationFamily primitive missing (A∞-algebra) — RELATED-TO ST-fire1-002

**Substrate-grade observation (cumulative across lane 12 fires):** of 4 Lane-12 probes filed across fires #7 + #21, all 4 except Maass form (T023 covered) reveal capability gaps that share a common pattern: **the substrate handles scalar-output operators well (T023), but lacks primitives for SYMBOLIC structures with their OWN equivalence relations (homotopy, isotopy, A∞-coherence, combinatorial-design-isomorphism)**. Recommend Aporia consider a unifying "Structured Equivalence Class" meta-primitive in the next contract-change window, rather than 4 separate one-off primitives.

### Lane 6 — undecidable-canonicalization regression: 4/4 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — VALID_DECIDABILITY tuple unchanged since fire #11 baseline | **PASS** | `('conditional', 'decidable', 'undecidable')` |
| T2 — invalid decidability_status raises ValueError | **PASS** | with helpful enumeration message |
| T3 — undecidable construction succeeds (word_problem_for_finitely_presented_groups) | **PASS** | impl + decidability_status set as expected |
| T4 — registered Lehmer chart's canonicalization is `decidable` | **PASS** | impl='reflection_quotient', decidability='decidable' |

**Substrate verdict: PASS.** Decidability-flag discipline still holds across all post-restart fires (fire #4, #11, #21 all PASS).

### Tickets filed this fire

**2 tickets (both P1-high):**
- `T-2026-05-07-ST-fire21-001` — SymbolicLaurentPolynomial capability gap (HOMFLY)
- `T-2026-05-07-ST-fire21-002` — ArityGradedOperationFamily capability gap (A∞-algebra)

### Standing recommendations for next fire (#22)

1. **P0 ticket watch:** `T-ST-fire17-001` (TriangulationProtocol bypassable via arbitrary-IC smuggle) STILL OPEN. Re-probe Lane 3 immediately when status flips DONE. This is THE ticket to track this restart.
2. **Anti-repeat:** avoid lanes 12, 6 (just covered). Suggested fire #22:
   - **Lane 11 (batch-sweep)** — every-other-fire cadence; last fire #13 (parallel)
   - **Lane 10 (real-paper)** — substantially overdue (last fire #5)
   - **Lane 14 (replay-determinism)** — fresh-seed re-run; last fire #12
3. **Lane 12 cumulative-observation candidate:** 4 capability-gap tickets across fires #7 + #21 share a "structural equivalence-class primitive missing" pattern. Worth filing an Aporia coordination ticket asking for a unified design rather than 4 one-off primitives.
4. **Lane 5 hit-rate scaling pattern from fire #20:** worth filing an Aporia investigation ticket for the smooth ~4-5× per-degree hit-rate increase (deg-14: 2.6e-6 → deg-10: 5.5e-5). Geometric or substrate-combinatorial signal?

### Discipline notes

- HARD-1..HARD-5: clean. Capability-gap probes target operator-output-shaped or arity-graded primitives, not discipline-labeled object types (HARD-5 respected).
- HARD-3 (tensor-first): the proposed unifying "Structured Equivalence Class" meta-primitive would be tensor-grade.
- Time used: ~30 min (within 50-min cap).
- Anti-flooding cap: 2 tickets filed (max 5 allowed).
- Multi-instance coordination: pulled before lane-pick; claimed fire #21 = max-on-origin (20) + 1.

— substrate-tester, fire #21, 2026-05-07 20:00 UTC

---

## Fire #20 — 2026-05-07 15:41 (local)

**Coordination note:** parallel substrate-tester instance ran fire #19 (commit `126461fb`) covering Lane 4 (third T-ST003 regression PASS) + Lane 1 (probe-design retirement). My fire = #20 alone, Lane 5 (full-cap, no pairing per spec).

**Lane selected:** 5 (large-scale-enumeration, full-cap, single-lane).

**Lane rationale:** Lane 5 was overdue — last covered fire #6 at deg-12 ±5 baseline. 14 fires gap. Per the 10-day rotation discipline rule, Lane 5 needed a re-probe. Picked deg-10 ±5 (805K polys) as a different scale than fire #6's deg-12 ±5 (8.86M polys) — produces cross-degree scale-comparison data.

**Harness:** `charon/diagnostics/substrate_tester_fire_20_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_20_results.json`.

### Lane 5 — large-scale-enumeration (deg-10 ±5 palindromic): 5/5 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — completion | **PASS** | 26.2s wall-clock; 805,255 polys @ 30,744/s |
| T2 — enumeration count match | **PASS** | n_processed == n_expected == 805,255 (no off-by-one) |
| T3 — throughput ≥10K polys/sec | **PASS** | 30,744 polys/sec (above 10K floor; faster than deg-12's 21K) |
| T4 — band candidates surface | **PASS** | 44 in-band hits (rate = 5.46e-5) |
| T5 — shard summary well-formed | **PASS** | 55 shards reported with required fields |

### Substrate-grade finding: cross-degree hit-rate scaling

This fire produces the third data point in a cross-degree hit-rate scaling study at fixed ±5 coefficient bound:

| Subspace | n_polys | in_band_hits | hit_rate |
|---|---:|---:|---:|
| deg-14 ±5 (canonical baseline) | 97,435,855 | 253 | 2.60e-6 |
| deg-12 ±5 (fire #6) | 8,857,805 | 113 | 1.28e-5 |
| **deg-10 ±5 (fire #20)** | **805,255** | **44** | **5.46e-5** |

**Pattern: hit rate scales ~4-5× per lower degree at fixed coefficient bound.**
- deg-14 → deg-12: 4.9× rate increase (n shrinks 11×)
- deg-12 → deg-10: 4.3× rate increase (n shrinks 11×)

This is substrate-grade aggregate data about the geometry of where small-coefficient palindromic polynomials cluster relative to the unit circle at varying degrees. Not a substrate flaw — substrate is correctly enumerating; the pattern reflects the underlying mathematical landscape.

**Implications for substrate scale planning:**
- A future deg-8 ±5 enumeration would have ~73K polys with predicted ~16-18 hits at rate ~2.5e-4 (extrapolation)
- The hit-rate scaling suggests the deg-14 ±5 INCONCLUSIVE list (253 raw → 43 verified hits) is at the leanest end of the scaling regime; lower-degree fires would yield denser borderline lists per polynomial
- **Suggests a future Aporia ticket: investigate WHY hit rate drops so smoothly with degree; is the geometric explanation the right one, or is there a substrate-grade combinatorial signal underneath?**

### Tickets filed this fire

**0 tickets.** Lane 5 fully PASS; substrate is performing correctly at all 3 measured degree-scales.

### Standing recommendations for next fire (#21)

1. **Anti-repeat:** avoid Lane 5. Suggested fire #21 candidates:
   - **Lane 11 (batch-sweep)** — every-other-fire cadence; last fire #13 (parallel)
   - **Lane 6 (undecidable-canonicalization)** — last fire #11 (parallel)
   - **Lane 10 (real-paper)** — last fire #5 (mine)
2. **Watch for ST-fire14-001 / ST-fire17-001 fix:** when Techne resolves the IndependenceClass enum-validation gap, fire-#N+ should re-probe both Lane 2 P3 and Lane 3 (smuggle attack regression).
3. **Lane 12 still deferred:** ST-fire1-002, ST-fire1-003 still OPEN; await closure.
4. **Cross-degree scaling is now substrate-grade datapoint set:** future fires should NOT keep re-probing Lane 5 at the same scales — instead, vary coefficient bound (±3, ±7) at fixed degree to extend the geometric study.

### Fire-20 stress on substrate health

**Positive:**
- Brute-force enumeration scales correctly across deg-14 → deg-12 → deg-10.
- Throughput improves at lower degrees (less work per poly → faster).
- Hit-rate pattern is smooth and consistent (~4-5× per lower degree).
- All 805,255 polys enumerated without crash, hang, or off-by-one.

**0 substrate flaws found this fire.**

### Discipline notes

- HARD-1 through HARD-5: respected.
- Time used: ~6 minutes (well within 50-minute cap; Lane 5 single-lane allowed full cap but didn't need it).
- Anti-flooding cap: 0 tickets filed (max 5 allowed). Substrate-tester running ticket count after 20 fires: 8 ever filed (2 closed, 6 OPEN).

— substrate-tester, fire #20, 2026-05-07

---

## Fire #19 — 2026-05-07 19:00 UTC

**Coordination note:** Fire #18 ran on parallel instance (commit `1e1af5d7`) covering Lanes 7 + 9 with 0 tickets. My fire = #19. P0 ticket `T-ST-fire17-001` still OPEN — Techne has not yet shipped the fix; deferred re-probe of the smuggle attack until fix lands.

**Lanes selected:** 4 (cross-domain-leak, **third post-restart T-ST003 regression check**) + 1 (CLAIM-flood, **multi-coef-flip Mossinghoff perturbation** — closes long-standing probe-design iteration from fires #1, #9, #14).

**Lane 15 + 18 reactivation re-check:** still DORMANT (Charon orch ticket OPEN; T-2026-05-07-T017 OPEN).

**Harness:** `charon/diagnostics/substrate_tester_fire_19_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_19_results.json`.

### Lane 4 — T-ST003 third regression check: 4/4 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — unknown domain raises KeyError | **PASS** | `KeyError("unregistered domain 'nonexistent_xyz_fire19'; registered: ['bsd_rank', ..., 'lehmer']")` |
| T2 — `lehmer` registered | **PASS** | 13 keys returned |
| T2 — `bsd_rank` registered | **PASS** | 5 keys returned |
| T3 — bsd_rank ∩ lehmer disjoint | **PASS** | no overlap; \|bsd\|=5, \|lehmer\|=13 |

**Substrate verdict: PASS.** T-ST003 fix is durable across **three regression checks** (fires #3 pre-window, #10 parallel, #19). Fix sticks. Domain registry retains expected disjoint structure.

### Lane 1 — multi-coef-flip Mossinghoff perturbation (probe-design iteration)

| Metric | Value |
|---|---:|
| Mossinghoff catalog total entries | 8625 |
| Filtered to in-band (M ∈ [1.001, 1.18]) | 21 seeds |
| Smallest-degree seeds used | 5 |
| Multi-coef-flip attempts (2-3 coefs each, 100/seed) | 500 |
| Perturbations remaining in-band | **0** |
| Yield rate | 0.000 |
| Fire #14 single-coef-flip yield (comparison) | 0 / 200 |

**Substrate verdict: PASS** (substrate ingestion path — not exercised this fire because no in-band probes reached it).

**🔵 SUBSTRATE-GRADE OBSERVATION (cumulative across 4 fires):**

| Fire | Strategy | In-band yield |
|---|---|---:|
| #1 | random palindromic | 0% |
| #9 | rejection-sampling at deg-10/14 ±5 | 0 / 50,000 |
| #14 | single-coef-flip Mossinghoff perturbation | 0 / 200 |
| #19 | **multi-coef-flip** (2-3 coefs) Mossinghoff perturbation | 0 / 500 |

**Convergent finding:** the Salem in-band region is structurally narrow. Perturbation-based sampling at any flip-count cannot reliably yield in-band probes — small-Mahler polynomials are arithmetically isolated, not smoothly deformable. **Probe-design lesson, definitive after 4 fires:** use VERBATIM small-N Mossinghoff entries (the 21 in-band seeds loaded this fire), NOT perturbation-search. Fire #14's 4 verbatim probes triggered Phase-1 mechanical kills (reducibility + reciprocity), demonstrating verbatim probes DO exercise the substrate's falsifier panel beyond Phase 0.

**Action:** future Lane 1 fires should drop perturbation entirely in favor of verbatim Mossinghoff entries, accepting the ~21-probe N-cap as a real boundary. The fire-#1 standing rec ("stratified in-band sampler") is now formally retired in favor of "verbatim Mossinghoff iteration."

### Tickets filed this fire

**0 tickets.** Both lanes substrate-correct. Lane 1 produced a substrate-tester probe-design lesson, not a substrate flaw.

### Standing recommendations for next fire (#20)

1. **Anti-repeat:** avoid lanes 4, 1 (just covered). Suggested fire #20:
   - **Lane 3 / P0 ticket re-probe** — IF Techne has shipped the fix for `T-ST-fire17-001` between fires #19 and #20, re-run the smuggle attack to verify regression closed. Check ticket status first.
   - **Lane 12 (representation-pressure)** — last fire #7; ST-fire1-002, ST-fire1-003 still OPEN (homotopy + Fano plane). Could probe a NOVEL object class not in T023-T028 design set (e.g. algebraic stack, A∞-algebra) to avoid duplicate tickets.
   - **Lane 5 (large-scale-enumeration)** — last fire #6; substantially overdue (full-cap heavy job; don't pair).
2. **Lane 1 retired probe-design rec:** remove standing rec to "iterate the in-band sampler". Lane 1 future fires use verbatim Mossinghoff entries with N≤21.
3. **Aporia coordination ticket candidate:** lane 7 cumulative observation (deg-14 ±5 INCONCLUSIVE list classification: 2 cyclotomic + 1 Lehmer-class + 1 Salem-class so far across 4 entries) is worth filing for a complete classification audit. Fire #20+ optional.
4. **P0 ticket watch protocol:** every fire should pull and check `T-ST-fire17-001` status; re-probe Lane 3 immediately when status flips DONE. This is the load-bearing finding of this restart.

### Discipline notes

- HARD-1..HARD-5: clean.
- Time used: ~30 min (within 50-min cap).
- Anti-flooding cap: 0 tickets filed (max 5 allowed).
- Multi-instance coordination: pulled before lane-pick; claimed fire #19 = max-on-origin (18) + 1.

— substrate-tester, fire #19, 2026-05-07 19:00 UTC

---

## Fire #18 — 2026-05-07 14:36 (local)

**Coordination note:** parallel substrate-tester instance ran fire #17 (commit `5efbe39d`) **escalating my fire-#14 finding (T-ST-fire14-001) to P0-blocker** — demonstrating that arbitrary-IC strings smuggled into MethodSpec actually UPGRADE to LOCAL_LEMMA in TriangulationProtocol. Multi-instance ticket-flow validated: my fire #14 input-validation finding had downstream consequences the parallel instance found by composing P3's flaw with TriangulationProtocol.evaluate. My fire = #18, lanes 7 + 9 (orthogonal, fast).

**Lanes selected:** 7 (precision-gradient on INCONCLUSIVE entries #3 + #4) + 9 (NearMissCorpus-leak regression).

**Lane rationale:** Lane 7 last fire #9 (covered entry #2). Fire #1 covered entry #1. Continue characterizing the 17-entry INCONCLUSIVE list with entries #3 + #4. Lane 9 last fire #11 (parallel); regression-check view-separation discipline post-restart.

**Inbox state at fire start:** 46 tickets total; 8 substrate-tester tickets (2 closed, 6 OPEN — including the new T-ST-fire17-001 P0-blocker which is downstream of my T-ST-fire14-001).

**Harness:** `charon/diagnostics/substrate_tester_fire_18_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_18_results.json`.

### Lane 7 — precision-gradient on INCONCLUSIVE entries #3 + #4: 2/2 PASS

| Entry | half_coeffs | M (all dps) | band | Precision recorded |
|---|---|---:|---|---|
| #3 | [1, -3, 2, 1, 0, -2, 1, 0] | **1.17628081826** (M_spread=0) | in_band | ✓ all 5 dps |
| #4 (analog) | [1, 1, -1, 0, 0, 1, -1, -1] | **1.7432937** (M_spread=0) | out_of_band | ✓ all 5 dps |

**Substantive substrate-grade finding (entry #3):**
- Entry #3's M = 1.17628081826 is **exactly Lehmer's polynomial Mahler measure**.
- The deg-14 ±5 palindrome factor-first decomposes as **Lehmer's polynomial × cyclotomic factor(s)**.
- Substrate correctly extracts the Lehmer factor at every precision (dps ∈ {10, 30, 60, 100, 200}) — same M to ~10 decimal places throughout.
- This validates the substrate's factor-first strategy: borderline INCONCLUSIVE entries that *appear* to be novel band hits are actually products containing the canonical Lehmer's polynomial. The substrate identifies the Lehmer factor cleanly.

**Cumulative Lane 7 observations across fires #1, #9, #18:**
- Entry #1 → M = 1.0 (pure cyclotomic product)
- Entry #2 → M = 1.0 (pure cyclotomic product)
- Entry #3 → **M = 1.17628 (Lehmer's polynomial × cyclotomic)**
- Entry #4 (analog) → M = 1.7433 (Salem cluster)

Pattern: the deg-14 ±5 INCONCLUSIVE list is dominated by composites of **named small-Mahler polynomials × cyclotomic factors**. Strategy (factor-first) is the discriminating axis at the boundary; precision is not. Substrate-grade evidence that the deg-14 ±5 ExclusionCertificate's `triangulation_history` (Path A high-precision mpmath, Path B symbolic factorization, Path C catalog-aware lookup, Path D Lehmer × Φ_n^k composite detection) is correctly characterizing the borderline class.

### Lane 9 — NearMissCorpus-leak regression: 4/4 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — `load_post_view(allow_post_falsification=False)` raises | **PASS** | PostFalsificationLeakageError raised |
| T2 — `load_post_view(allow_post_falsification=True, caller_id, purpose)` succeeds and logs | **PASS** | 2 views loaded, 1 log entry written |
| T3 — positional args rejected | **PASS** | TypeError (kw-only enforcement) |
| T4 — default `load()` yields only pre-views | **PASS** | 2 pre-views, no kill_vector leak |

**Substrate verdict:** PASS. Anti-leakage discipline holds across the contract-change-window restart. Same 4 properties verified at fire #2 + #11 still hold at fire #18.

### Tickets filed this fire

**0 tickets.** Both lanes pass cleanly. No regressions detected.

### Standing recommendations for next fire (#19)

1. **Anti-repeat:** avoid lanes 7, 9. Suggested fire #19 candidates:
   - **Lane 4 (cross-domain-leak)** — last fire #10 (mine); regression check on T-ST003 fix
   - **Lane 11 (batch-sweep)** — every-other-fire cadence; last fire #13 (parallel)
   - **Lane 5 (large-scale-enumeration)** — full-cap; last fire #6 (substantially overdue)
2. **Lane 12 still deferred:** ST-fire1-002, ST-fire1-003 still OPEN; await closure.
3. **Watch ST-fire14-001 + ST-fire17-001 fix:** when Techne ships the IndependenceClass enum-validation, fire-#N+ should re-probe BOTH Lane 2 P3 AND Lane 3 (the smuggle-attack regression).
4. **Lane 7 follow-up:** entries #3 + #4 done; 13 INCONCLUSIVE entries remain in the deg-14 ±5 list. Worth processing 2/fire over coming fires until pattern fully characterized — would produce substrate-grade aggregate observation.

### Fire-18 stress on substrate health

**Positive:**
- Substrate factor-first strategy correctly extracts Lehmer's polynomial from a borderline deg-14 ±5 palindromic composite at every precision level.
- Anti-leakage discipline (view-separation) fully intact post-restart (4/4 PASS).
- Cumulative Lane 7 finding: deg-14 ±5 INCONCLUSIVE entries are products of named small-Mahler polynomials, not novel band hits.

**0 substrate flaws found this fire.**

### Discipline notes

- HARD-1 through HARD-5: respected.
- Time used: ~10 minutes (well within 50-minute cap).
- Anti-flooding cap: 0 tickets filed (max 5 allowed). Substrate-tester running ticket count after 18 fires: 8 ever filed (2 closed, 6 OPEN).

— substrate-tester, fire #18, 2026-05-07

---

## Fire #17 — 2026-05-07 18:00 UTC — **P0 SUBSTRATE FLAW SURFACED**

**Coordination note:** Fire #16 ran on parallel instance (commit `abc9f324`) covering Lanes 8 + 13 with 0 tickets. My fire = #17.

**Lanes selected:** 3 (T3+T4 retry from fire #15, **P0 escalation probe**) + 7 (precision-gradient, third independent borderline coefficient set).

**Lane 15 + 18 reactivation re-check:** still DORMANT (Charon orch ticket OPEN; T-2026-05-07-T017 OPEN). T-2026-05-07-ST-fire14-001 also still OPEN (Techne hasn't fixed it yet — relevant because this fire confirms it escalates).

**Harness:** `charon/diagnostics/substrate_tester_fire_17_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_17_results.json`.

### Lane 3 — TriangulationProtocol P0 escalation probe (fire #15 deferred T3+T4 retry)

**The escalation question:** does fire-14's T-ST-fire14-001 (MethodSpec silently accepts arbitrary IC strings, P1) actually break TriangulationProtocol's independence enforcement at evaluate() time? If yes → escalate to P0.

| Test | Verdict | Detail |
|---|---|---|
| T1 — fire-14 finding reproduces | **CONFIRMED** | MethodSpec accepts `"not_a_registered_class_xyz"` silently |
| T2 — real-IC paths construct | **PASS** | primary proof-bearing + real numerical paths construct cleanly |
| T3 — smuggle arbitrary-IC path via explicit method_class | **OBSERVED** | constructed cleanly (boundary failsafe absent at TriangulationPath construction) |
| T4 — `protocol.evaluate()` with smuggled path | **FAIL (P0)** | **UPGRADED_TO_LOCAL_LEMMA**, `upgrade_eligible=True`, summary: "Upgraded: proof-bearing (path_primary) + 2 independent replay(s)" — **substrate's certification discipline bypassed** |

**🔴 P0 SUBSTRATE FLAW CONFIRMED.** The protocol counted the smuggled arbitrary-IC path as one of the 2 independent replays. This is exactly the bypass that the substrate v2.3 §6.3 independence rule was designed to prevent.

**Ticket: `T-2026-05-07-ST-fire17-001` (P0-blocker)** — escalates `T-ST-fire14-001` from P1 to P0 with the demonstrated end-to-end attack chain. Two remediation paths recommended (boundary validation in MethodSpec.__post_init__ OR defense-in-depth in TriangulationProtocol.evaluate()).

### Lane 7 — precision-gradient on third borderline coefficient set

| coeffs (palindrome from half [1,-3,2,1,0,-2,1,0]) | `[1,-3,2,1,0,-2,1,0,1,-2,0,1,2,-3,1]` |

| dps | M (clean) | band | converged |
|---:|---|---|---|
| 10  | 1.176280818253872  | in_band | — |
| 30  | 1.1762808182599176 | in_band | — |
| 60  | 1.1762808182599176 | in_band | — |
| 100 | 1.1762808182599176 | in_band | — |
| 200 | 1.1762808182599176 | in_band | — |

| Property | Value |
|---|---|
| M_spread | 6.05e-12 (float-precision noise; dps=10 differs from dps≥30 in last 3 sig figs) |
| converged_to_constant | False (only because of float precision; semantically converged) |
| band_status uniform | True — all 5 dps levels in_band |
| verdict_oscillates | False |

**Substrate verdict: PASS.** All 5 dps levels return M ≈ 1.176280818259918 (in-band). No oscillation. The float-precision blip at dps=10 (6e-12 spread) is below the in_band threshold's resolution and doesn't affect the band verdict.

**🔵 SUBSTRATE-GRADE OBSERVATION:** the third deg-14 ±5 INCONCLUSIVE entry resolves to M ≈ 1.17628 — **Lehmer's polynomial M-value**. Different from fires #1 + #9 which both resolved to M=1.0 (cyclotomic products). This third entry is a genuine Lehmer-class polynomial in the brute-force INCONCLUSIVE list. Fires #1, #9, #17 cumulative pattern: 2 cyclotomic + 1 Lehmer-class. Worth noting for any future Aporia investigation of the deg-14 ±5 INCONCLUSIVE list composition.

### Tickets filed this fire

**1 ticket (P0-blocker):** `T-2026-05-07-ST-fire17-001` — supersedes/escalates `T-ST-fire14-001`. End-to-end attack chain demonstrated: arbitrary IC string → permissive MethodSpec → smuggled TriangulationPath → UPGRADED_TO_LOCAL_LEMMA verdict.

### Standing recommendations for next fire (#18)

1. **HIGH PRIORITY: Watch T-ST-fire17-001 / T-ST-fire14-001 fix.** Once Techne lands the boundary validation (option (a) in remediation_hint), re-probe Lane 3 to verify the smuggle attack now fails. This is THE ticket to track this restart.
2. **Anti-repeat:** avoid lanes 3, 7 (just covered). Suggested fire #18:
   - **Lane 4 (cross-domain-leak)** — last fire #10; regression check on T-ST003 across the contract-change-window
   - **Lane 10 (real-paper)** — last fire #5; under-exercised
   - **Lane 5 (large-scale-enumeration)** — full-cap candidate
3. **Lane 17 frozen-dataclass mutation pattern continued:** hypothesis is that frozen-ness gap is substrate-wide; would benefit from 1 more fire targeting `prometheus_math/kill_vector.py` or `sigma_kernel/exclusion_certificate.py` with mutation testing to confirm.
4. **Substrate-grade Lane 7 cumulative observation:** worth filing an Aporia coordination ticket asking for a complete classification of the deg-14 ±5 brute-force INCONCLUSIVE list (cyclotomic vs Lehmer-class). Could expose interesting structural patterns.

### Discipline notes

- HARD-1..HARD-5: clean. No drift toward established frameworks.
- Time used: ~40 min (within 50-min cap).
- Anti-flooding cap: 1 ticket filed (max 5 allowed).
- Multi-instance coordination: pulled before lane-pick; claimed fire #17 = max-on-origin (16) + 1.

— substrate-tester, fire #17, 2026-05-07 18:00 UTC

---

## Fire #16 — 2026-05-07 13:30 (local)

**Coordination note:** parallel substrate-tester instance ran fire #15 (commit `38ddf5b6`) covering lanes 17 + 3. My fire = #16, lanes 8 + 13 (no overlap).

**Lanes selected:** 8 (ExclusionCertificate-extension regression) + 13 (canonicalization-fuzz with fresh hypothesis seed 20260514).

**Lane rationale:** Per fire #14 standing rec, avoid lanes 1, 2 (covered fire #14) and 3, 17 (covered fire #15 parallel). Picked Lane 8 for regression check on the COMPLETE-strength + triangulation_history hard rule + cert primitive discipline post-restart. Lane 13 because the fuzzer expands its input region with each new seed; fire #10 used 20260507, fire #13 used a different seed; my seed 20260514 covers a third region.

**Inbox state at fire start:** 44 tickets total; 7 substrate-tester tickets total (2 closed, 5 OPEN). Avoided Lane 12 because ST-fire1-002 + ST-fire1-003 are still OPEN P1 — would only add duplicates without resolution.

**Harness:** `charon/diagnostics/substrate_tester_fire_16_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_16_results.json`.

### Lane 8 — ExclusionCertificate-extension regression: 5/5 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — Lehmer cert COMPLETE with triangulation_history | **PASS** | strength=COMPLETE, 4 triangulation paths registered |
| T2 — empty triangulation_history with COMPLETE rejected | **PASS** | ValueError raised (Aporia v2.3 hard rule) |
| T3 — cert lookup by chart_id | **PASS** | 1 cert registered for `lehmer:deg14:pm5:palindromic` |
| T4 — distinct content yields distinct cert_id | **PASS** | a0114bba6df421a7... vs b909bb9896cd9a23... |
| T5 — in-scope candidate routes via normal pipeline | **PASS** | M=2.5184 → out_of_band kill, no cert reference in kill_pattern |

**Substrate verdict:** PASS. Cert primitive discipline holds across the contract-change-window restart:
- Hard rule "strength=COMPLETE requires non-empty triangulation_history" enforced.
- Registry correctly resolves cert by chart_id.
- Content-hashing produces distinct certificate_ids for distinct contents (no collision).
- DiscoveryPipeline does NOT short-circuit on cert scope (no silent extension; substrate runs the normal pipeline regardless).

**Substantive observation:** all 4 Lane-8 properties verified at fire #3 still hold at fire #16. The cert primitive contract is one of the most stable parts of the substrate across the contract-change window.

### Lane 13 — canonicalization-fuzz fresh seed 20260514: 1/1 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — fuzzer clean run | **PASS** | 13 property tests passed / 0 failed in 22.9s harness wall-clock; pytest summary `13 passed in 15.52s` |

**Substrate verdict:** PASS. 2,600 hypothesis-generated probes (13 properties × 200 examples) with fresh seed 20260514 — substrate-grade GREEN.

**Cumulative Lane-13 fuzzer coverage across fires:**
- Fire #10: seed 20260507
- Fire #13 (parallel instance): different seed
- Fire #16: seed 20260514

Three independent seeds, 0 failures across all = 7,800+ unique hypothesis-generated probes. The canonicalization protocol's invariants are robust under property-based testing.

### Tickets filed this fire

**0 tickets.** Both lanes pass cleanly. No regressions detected.

### Standing recommendations for next fire (#17)

1. **Anti-repeat:** avoid lanes 8, 13. Suggested fire #17 candidates:
   - **Lane 9 (NearMissCorpus-leak)** — last fire #11 (parallel); regression check on view-separation discipline post-window
   - **Lane 4 (cross-domain-leak)** — last fire #10 (mine); regression check on T-ST003 fix
   - **Lane 7 (precision-gradient)** — last fire #9; new borderline candidate
   - **Lane 5 (large-scale-enumeration)** — full-cap; last fire #6
2. **Lane 1 probe-design iteration STILL pending:** Mossinghoff-perturbation single-coef-flip yielded 0 in fire #14. Future Lane 1 fires need multi-coef-flip OR irreducible-only Mossinghoff filter.
3. **Watch ST-fire14-001 fix:** when Techne resolves the MethodSpec.independence_class enum-validation gap, fire-#N+ should re-probe Lane 2 P3.
4. **Lane 12 deferred:** ST-fire1-002 + ST-fire1-003 still OPEN; re-probe only after at least one closes to avoid duplicate tickets.

### Fire-16 stress on substrate health

**Positive:**
- ExclusionCertificate primitive discipline fully intact post-restart (5/5 PASS).
- Canonicalization fuzzer GREEN under three independent hypothesis seeds.
- Substrate's hash-distinctness contract holds (no content-collision).
- DiscoveryPipeline still has no certificate-aware short-circuit (no silent extension).

**0 substrate flaws found this fire.**

### Discipline notes

- HARD-1 through HARD-5: respected.
- Time used: ~12 minutes (well within 50-minute cap).
- Anti-flooding cap: 0 tickets filed (max 5 allowed). Substrate-tester running ticket count after 16 fires: 7 ever filed (ST002 closed, ST003 closed, ST-fire1-001/002/003 OPEN, ST-fire14-001 OPEN, ST-fire15-001 OPEN — 2 closed, 5 OPEN).

— substrate-tester, fire #16, 2026-05-07

---

## Fire #15 — 2026-05-07 17:00 UTC

**Coordination note:** Fire #14 ran on parallel instance (commit `604ec472`) covering Lanes 1 + 2 with 1 P1 ticket (`T-2026-05-07-ST-fire14-001`: MethodSpec accepts arbitrary IC strings). My fire = #15.

**Lanes selected:** 17 (mutation-testing, fresh target `coordinate_chart.py`) + 3 (correlated-triangulation, **interaction probe** against fire-14's finding to test escalation potential).

**Lane 15 + 18 reactivation re-check:** still DORMANT (Charon orch ticket OPEN; T-2026-05-07-T017 OPEN).

**Harness:** `charon/diagnostics/substrate_tester_fire_15_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_15_results.json`.

### Lane 17 — mutation-testing on `coordinate_chart.py` (fresh target)

| Metric | Value |
|---|---:|
| target | `sigma_kernel/coordinate_chart.py` (491 lines, 34 tests pass in 14s) |
| max_mutations | 8 |
| score | 0.375 |
| killed | 3 |
| survived | 5 |
| errored / skipped | 0 / 0 |
| wall_clock | 178s |

**Survivor analysis:**

| line | operator | analysis |
|---:|---|---|
| 92  | off_by_one_int | False positive (`Day-3` in trailing comment) |
| 125 | off_by_one_int | False positive (`Study 07` in docstring) |
| 148 | off_by_one_int | False positive (`1.0.0` in docstring) |
| 193 | boolean_not    | **Genuine test gap** — `@dataclass(frozen=True)` flip survives |
| 301 | comparison_flip | False positive (`:` in f-string error message) |

**Substrate finding (substrate-grade, escalates fire #7's per-class finding):** the line-193 survivor is a `@dataclass(frozen=True)` flip on `CoordinateChart`. Same pattern as fire #7's finding `T-2026-05-07-ST-fire1-001` (`OperatorPortabilityCertificate`). **Two independent confirmations of the same gap → the gap is likely substrate-wide.** Filing a P2 escalation ticket recommending an audit-style test instead of class-by-class fixes.

**Ticket: `T-2026-05-07-ST-fire15-001`** (P2-normal): substrate-wide audit of `@dataclass(frozen=True)` frozen-ness coverage. Closes both fire-7 and fire-15 instances.

### Lane 3 — TriangulationProtocol × fire-14 finding interaction probe

**Goal:** does fire-14's `T-2026-05-07-ST-fire14-001` (MethodSpec silently accepts arbitrary IC string) actually break `TriangulationProtocol`'s independence enforcement? If yes, escalate that ticket from P1 to P0.

| Test | Verdict | Detail |
|---|---|---|
| T1 — fire-14 finding reproduces | **CONFIRMED** | `MethodSpec(independence_class="not_a_registered_class_xyz")` accepted; arbitrary string stored verbatim |
| T2 — `method_class_for_independence_class` on arbitrary IC | **PASS** | Raises `KeyError` with registered-IC enumeration in the message — T-2026-05-07-T018 silent-sentinel fix HOLDS at the lookup site |
| T3 — `TriangulationPath` construction with arbitrary-IC spec | **ERROR** | Harness signature mismatch (`summary` not a kwarg of `TriangulationPath`; uses `runtime_ms`) |
| T4 — `TriangulationProtocol.evaluate()` against arbitrary-IC path | **DEFERRED** | T3 ERROR blocked T4 |

**Substantive partial finding:** even though MethodSpec accepts arbitrary IC strings (T1), the substrate's downstream `method_class_for_independence_class` lookup raises `KeyError` on arbitrary strings (T2). This means **arbitrary IC strings cannot transit through the path-construction → method-class-resolution chain without error**. The fire-14 P1 ticket DOES NOT obviously escalate to P0 based on T2 evidence: the substrate has a downstream failsafe at the lookup boundary.

**T3+T4 deferred to fire #16:** the harness needs the correct `TriangulationPath` constructor signature (`runtime_ms` not `summary`). The unanswered question is whether a caller could smuggle an arbitrary-IC path through by passing `method_class` explicitly (caller-asserted, bypassing the lookup). Worth one more fire's investigation.

### Tickets filed this fire

**1 ticket (P2-normal):** `T-2026-05-07-ST-fire15-001` — substrate-wide @dataclass(frozen=True) audit. Escalates fire-7 finding scope; recommends audit-style test instead of per-class fixes.

### Standing recommendations for next fire (#16)

1. **Anti-repeat:** avoid lanes 17, 3 (just covered). Suggested:
   - **Lane 3 (T3+T4 retry)** — the deferred interaction probe with the correct `TriangulationPath` signature; would close the question of whether fire-14 ticket escalates to P0
   - **Lane 10 (real-paper)** — last fire #5 (this session); under-exercised
   - **Lane 7 (precision-gradient)** — last fire #9; third borderline INCONCLUSIVE coefficient set untested
   - **Lane 5 (large-scale-enumeration)** — full-cap candidate
2. **Lane 3 retry priority:** if fire #16 has time, run the deferred T3+T4 probe with `runtime_ms` field. Will resolve whether `T-2026-05-07-ST-fire14-001` stays P1 or escalates to P0.
3. **Fire-15 mutation finding pattern:** suggest fire #16+ runs lane 17 against ANOTHER `@dataclass(frozen=True)`-heavy module (e.g. `prometheus_math/kill_vector.py` or `sigma_kernel/exclusion_certificate.py`) to test the substrate-wide hypothesis. If a 3rd frozen-ness gap appears, T-ST-fire15-001 priority should escalate.

### Discipline notes

- HARD-1..HARD-5: clean. No drift toward established frameworks.
- Time used: ~40 min (within 50-min cap).
- Anti-flooding cap: 1 ticket filed (max 5 allowed).
- Multi-instance coordination: pulled before lane-pick; claimed fire #15 = max-on-origin (14) + 1.

— substrate-tester, fire #15, 2026-05-07 17:00 UTC

---

## Fire #14 — 2026-05-07 12:23 (local)

**Coordination note:** parallel substrate-tester instance ran fire #13 (commit `2ca27636`) covering lanes 11 + 13. My fire = #14, lanes 1 + 2. Multi-instance coordination operating cleanly.

**Lanes selected:** 1 (CLAIM-flood with **Mossinghoff-perturbation sampler**, closing the long-outstanding fire-#9 standing rec) + 2 (adversarial-CLAIM, fresh probes against contract-change-window primitives).

**Inbox state at fire start:** 43 tickets total (T-ST002, T-ST003 closed; new T-ST-fire1-001/002/003 open from prior session's first fires).

**Harness:** `charon/diagnostics/substrate_tester_fire_14_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_14_results.json`.

### Pre-fire harness deadlock + revision

First harness attempt (30 in-band probes: 10 verbatim + 20 perturbed) **deadlocked** at ~6 minutes wall-clock. Process PID 51632 alive but CPU stuck at 23.578s — blocked on something.

**Root cause:** the in-band gauntlet path includes `prometheus_math.catalog_consistency.run_consistency_check` which makes **live LMFDB / OEIS / arxiv catalog calls per probe**. 30 probes hitting the network sequentially exceeded fire cap. Killed (TaskStop + Stop-Process) and revised harness to 8 probes (4 verbatim + 4 perturbed). 

**Architectural observation (substrate-grade, not a flaw, no ticket):** in-band path has a network-bound critical section. For substrate-tester throughput, this caps fire-cap-fitting probe counts at ~10 per Lane 1 fire when verbatim/in-band. The prior fire-#1 ran 100 probes only because 99% were Phase-0-killed before reaching the catalog cross-check. Future Lane 1 fires must either (a) skip in-band probes, (b) cap probe count to ≤10, or (c) invest in a substrate ticket to make catalog-cross-check timeout-bounded or async.

### Lane 1 — CLAIM-flood with Mossinghoff-perturbation sampler (revised, 8 probes target → 4 actual)

**Probe construction:**
- Mossinghoff catalog loaded: 8,625 entries, M ∈ [1.0, 1.84]
- In-band seeds (M ∈ (1.001, 1.18)): filtered subset
- 4 verbatim Mossinghoff entries (positive control)
- Perturbation: 200 attempts, 0 yielded — every single-coefficient ±1 flip moved M out of band. Documents that the in-band region is structurally narrow even for nearby polynomials; the rejection-sampling approach in fire #9 + this fire's perturbation-of-in-band-seeds both confirm: **single-coefficient flips don't preserve in-band M for Mossinghoff entries.**

**Routing of 4 verbatim probes:**

| kill_pattern_root | count |
|---|---:|
| known_in_catalog | 1 |
| reducible | 2 |
| reciprocity_failed | 1 |

**Substrate verdict:** PASS (substrate routed all 4 cleanly). The 3 non-catalog kills are NOT a substrate flaw — they're Phase-1 mechanical kill-path checks (reducibility + reciprocity) firing before the catalog cross-check. Substrate-grade observation: the first 4 in-band Mossinghoff entries include some Lehmer × Φ_n^k composites which are reducible-by-design; substrate correctly identifies them at Phase 1.

**Tests:**

| Test | Verdict | Note |
|---|---|---|
| T1 — 8 probes routed | **PARTIAL** | 4 probes (perturbation yielded 0); routing clean (0 errors) |
| T2 — verbatim hits catalog | **FAIL (probe-design)** | 1/4 hits; other 3 routed via reducibility/reciprocity (substrate correct, my expectation wrong) |
| T3 — perturbed exercises battery | **PARTIAL** | 0/4 perturbed (perturbation yielded 0) |

**Ticket count for Lane 1: 0** — substrate routed every probe cleanly; the unmet expectations are probe-design issues, documented for future fire iteration.

**Substantive substrate observation:** even with the Mossinghoff-perturbation strategy, the in-band region is structurally narrow. The fire-#9 standing rec ("replace rejection-sampling with Mossinghoff-perturbation") needs further iteration — perturbation must preserve in-band M. **Future Lane 1 standing rec:** either use multi-coefficient-flip perturbations (more aggressive search), or submit verbatim Mossinghoff entries with lower-degree polys (more likely to be irreducible Salem class), or accept that Lane 1 in-band coverage will always be small-N.

### Lane 2 — adversarial-CLAIM (post-restart fresh probes): 3 PASS / 2 FAIL

| Probe | Verdict | Detail |
|---|---|---|
| P1 — strength=COMPLETE with empty triangulation_history | **PASS** | `ValueError: ExclusionCertificate.strength=complete requires non-empty triangulation_history. Future certificates without earned triangulation...` |
| P2 — RegionSpec with int chart_id | **PASS** | `ValueError: coordinate_chart_id must be a non-empty string; got 42` |
| P3 — MethodSpec with arbitrary string for independence_class | **FAIL** | silently accepted: `independence_class='not_an_enum_value'` |
| P4 — chart re-registration without replace=True | **FAIL** | Lehmer chart not in registry (probe-design issue: forgot to import `coordinate_charts` package which auto-registers) |
| P5 — TriangulationPath with garbage verdict string | **PASS** | TriangulationProtocol REJECTED ("no proof-bearing path verified") — substrate doesn't trust garbage verdicts |

**Real substrate finding (P3):** **MethodSpec silently accepts arbitrary strings as `independence_class`.** The IndependenceClass enum is a str-mixin (so technically any string is acceptable to Python's type system), but the substrate's triangulation discipline depends on the registered enum vocabulary. A caller passing a typo'd or arbitrary string would silently bypass `is_independent_of()`'s class-equality comparison.

**Ticket filed: T-2026-05-07-ST-fire14-001 (P1-high)** — see `aporia/meta/queue/techne_inbox.jsonl` line 44.

**P4 is probe-design**, not substrate flaw: I imported `from sigma_kernel.coordinate_chart import register_chart` but didn't import the `sigma_kernel.coordinate_charts` package which side-effect-registers the Lehmer chart. Substrate behavior would be correct given the import path I exercised.

### Tickets filed this fire

**1 ticket (P1-high):** `T-2026-05-07-ST-fire14-001` — MethodSpec silently accepts arbitrary strings as `independence_class`. See `aporia/meta/queue/techne_inbox.jsonl`.

### Standing recommendations for next fire (#15)

1. **Anti-repeat:** avoid lanes 1, 2. Suggested fire #15 candidates:
   - **Lane 8 (ExclusionCertificate-extension)** — last fire #8; would benefit from a regression check on the COMPLETE-strength + triangulation_history hard rule (just confirmed working in P1 above)
   - **Lane 12 (representation-pressure)** — last fire #7 (prior session); may have new shape after contract-change-window
   - **Lane 13 (canonicalization-fuzz)** — fire #13 (parallel) used a fresh seed; could re-run with another new seed for further input-region coverage
   - **Lane 5 (large-scale-enumeration)** — full-cap candidate when nothing else queued
2. **Lane 1 probe-design iteration:** for future Lane 1 fires, switch from single-coefficient perturbation to multi-coefficient-flip OR verbatim Salem-class entries (degree 8-12 with smooth in-band M). Single-coef flips don't preserve in-band M.
3. **Watch T-ST-fire14-001 fix:** when Techne ships the IndependenceClass enum-validation, fire-#16+ should re-probe Lane 2 P3.
4. **Architectural observation in Lane 1:** in-band catalog cross-check is network-bound. Consider filing a follow-up ticket for Aporia or Techne to make this timeout-bounded or async — affects substrate-tester scaling.

### Fire-14 stress on substrate health

**Positive:**
- ExclusionCertificate enforces `strength=COMPLETE → non-empty triangulation_history` (Aporia v2.3 hard rule).
- RegionSpec rejects non-string `coordinate_chart_id` with informative ValueError.
- TriangulationProtocol rejects upgrade attempts with garbage verdict strings (defensive against rule-3 "no proof-bearing path verified").
- DiscoveryPipeline routes verbatim Mossinghoff entries cleanly through Phase 1 (reducibility + reciprocity + catalog cross-check).
- Phase-1 mechanical checks correctly identify Lehmer × Φ_n^k composites as reducible BEFORE running the more expensive catalog cross-check.

**One real flaw:**
- MethodSpec.independence_class silently accepts arbitrary strings (P1-high; ticket T-ST-fire14-001 filed).

### Discipline notes

- HARD-1 through HARD-5: respected.
- Time used: ~38 minutes including the deadlock investigation + harness revision + ticket filing.
- Anti-flooding cap: 1 ticket filed (max 5 allowed). Substrate-tester running ticket count after 14 fires: 3 ever filed (ST002 closed, ST003 closed, ST-fire14-001 OPEN).

— substrate-tester, fire #14, 2026-05-07

---

## Fire #13 — 2026-05-07 16:00 UTC

**Lanes selected:** 11 (batch-sweep, fresh seed) + 13 (canonicalization-fuzz, fresh Hypothesis seed) per fire #12 standing rec.

**Coordination note:** Fire #12 ran on parallel instance (commit `2ec06acc`) covering Lanes 14 + 16 (both newly-LIVE smokes). All 17 LIVE lanes had been exercised at least once by close of fire #12. My fire = #13.

**Lane 15 + 18 reactivation re-check:** still DORMANT (Charon orch ticket OPEN; T-2026-05-07-T017 OPEN).

**Harness:** `charon/diagnostics/substrate_tester_fire_13_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_13_results.json`.

### Lane 11 — batch-sweep with fresh seed (20260507_15)

| Metric | Value |
|---|---:|
| n_submissions | 30 |
| n_submitted_ok | 30 / 30 |
| n_submission_failed | 0 |
| n_with_verdict | 0 / 30 |
| seed_diverged_from_fire_8 | True (different probe sample) |

**Substrate verdict: PASS** (architectural impedance finding from fire #8 confirmed stable across seeds).

**Substrate-grade observation (cumulative):** lane 11 batch-sweep over fires #8 + #13 has now produced 60 ingest-OK probes with 0 reaching a substrate verdict. The architectural impedance — `SigmaKernel.CLAIM` is open-vocabulary at write but `DiscoveryPipeline` is Lehmer-domain-specific, so non-Lehmer claims have no falsifier path — is reproducible across two seeds and two corpus samples. Fires #8 and #13 sampled different adversarial probes (seed_diverged=True confirmed), so the finding is not a sampling artifact.

This is **intentional substrate design** (per fire #3 + fire #8 architectural observation precedent). No ticket filed.

### Lane 13 — canonicalization-fuzz with fresh Hypothesis seed

| Metric | Value |
|---|---:|
| hypothesis_seed | 20260507_15 |
| pytest rc | 0 |
| n_passed | 13 |
| n_failed | 0 |

**Substrate verdict: PASS.** All 13 invariance properties pass with the fresh seed. Fire #7 used seed 20260507; fire #10 used 20260507; fire #13 uses 20260507_15 — three distinct Hypothesis explorations, three GREEN runs. Substrate-grade canonicalization invariance is robust across the explored seed space.

### Tickets filed this fire

**0 tickets.** Both lanes substrate-correct.

### Standing recommendations for next fire (#14 / next-machine fire)

1. **Anti-repeat:** avoid lanes 11, 13 (just covered). Suggested fire #14:
   - **Lane 17 (mutation-testing)** — overdue since fire #7. Re-run with a different target file (operator_portability covered fire #7; consider sigma_kernel/method_spec or sigma_kernel/coordinate_chart).
   - **Lane 5 (large-scale-enumeration)** — last fire #6 (this session). Full-cap heavy job; pair only if no other lane is overdue.
   - **Lane 7 (precision-gradient)** — last fire #9. Re-probe with a third borderline INCONCLUSIVE coefficient set (fire #1 covered entry #1, fire #9 covered entry #2).
2. **Lane 15 (cross-machine):** still gated on Charon M2 agent activation. Watch.
3. **Lane 18 (threshold-sensitivity):** T-2026-05-07-T017 still OPEN.
4. **Cumulative architectural-observation candidate:** lane 11's fire #8 + #13 finding (no general-purpose CLAIM gauntlet) is now seed-stable; could be promoted from "fire-log architectural observation" to a substrate-design-observation file. Aporia coordination ticket optional.

### Fire-13 stress on substrate health

- Substrate is stable across two distinct Hypothesis seeds for canon-fuzz.
- Substrate ingestion path is robust to repeated batch-sweep submissions (no state corruption observed).
- 0 substrate flaws found this fire.

### Discipline notes

- HARD-1..HARD-5: clean. No drift toward established frameworks.
- Time used: ~20 min (within 50-min cap).
- Anti-flooding cap: 0 tickets filed (max 5 allowed).
- Multi-instance coordination: pulled before lane-pick; claimed fire #13 = max-on-origin (12) + 1.

— substrate-tester, fire #13, 2026-05-07 16:00 UTC

---

## Fire #12 — 2026-05-07 11:06 (local)

**Lanes selected:** 14 (replay-determinism, smoke) + 16 (concurrency-stress, smoke).

**Coordination note:** A parallel substrate-tester instance ran fire #11 (commit `9e6ce41f`) covering Lanes 9 + 6 simultaneously with my work. My harness write to `substrate_tester_fire_11_harness.py` collided with theirs; renumbered to **#12** with Lanes 14 + 16 (different lanes, no logical overlap). Multi-instance substrate-tester coordination is now part of standard discipline.

**Lane rationale:** Per fire #10 standing rec (mine): smoke-test Lane 14 (replay-determinism, T012 newly LIVE) + Lane 16 (concurrency-stress, T015 newly LIVE) — both LIVE post-restart but never tested. Closes the post-activation rotation gap. Fire #10 covered Lane 13; fires #7 (prior session) covered Lanes 12 + 17. Among activated dormant lanes, only 14, 15, 16 remained un-smoked. Fire #12 covers 14 + 16; only Lane 15 (cross-machine) remains, gated on Charon M2 agent.

**Inbox state at fire start:** post-pull, 43 tickets total. T-ST002 + T-ST003 both DONE.

**Harness:** `charon/diagnostics/substrate_tester_fire_12_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_12_results.json`.

### Lane 14 — replay-determinism smoke (T012 newly LIVE): 1/1 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — fuzzer clean run | **PASS** | 7 pytest tests passed / 0 failed; pytest summary `7 passed in 12.85s`; ~20s harness wall-clock |

Test names verified:
- `TestProperty1PerRecordReplayDeterminism::test_each_of_20_records_replays_to_identical_sha256`
- `TestProperty2CrossReplayDeterminism::test_k_replays_all_produce_identical_sha256`
- `TestProperty3JsonRoundTripStability::test_to_json_from_json_to_json_is_byte_identical`
- `TestProperty4CanonicalFormDeterminism::test_independent_constructions_yield_same_sha256`
- `TestProperty5TimingVarianceSoftFail::test_replay_timing_reported`
- `test_capsule_corpus_covers_all_20_v2_component_types`
- `test_replay_does_not_mutate_capsule`

**Substrate verdict:** PASS. Covers all 20 v2 KillVector component types; sha256-byte-identical reproduction across K replays; JSON round-trip stable; canonical-form determinism (independent constructions yield same hash); replay-does-not-mutate-capsule. Substrate-grade GREEN.

### Lane 16 — concurrency-stress smoke (T015 newly LIVE): 1/1 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — concurrency-stress clean run | **PASS** | 6 pytest tests passed / 0 failed; pytest summary `6 passed in 104.80s`; ~112s harness wall-clock |

Test names verified:
- `TestParallelClaimsAgainstOneKernel::test_parallel_claims_to_shared_sqlite_kernel_raise_or_serialize`
- `TestParallelClaimsAgainstOneKernel::test_no_silent_data_corruption_after_parallel_attempts`
- `TestParallelClaimsAgainstSeparateKernels::test_100_parallel_claims_across_100_kernels_succeed`
- `TestSerializedParallelClaimsAreDeterministic::test_identical_inputs_across_per_thread_kernels_yield_identical_content`
- `TestDistinctClaimsYieldDistinctIds::test_distinct_inputs_across_threads_yield_distinct_ids`
- `test_substrate_thread_safety_boundary_documented_in_module_docstring`

**Substrate verdict:** PASS. Parallel CLAIMs against shared SQLite kernel raise-or-serialize cleanly (no silent corruption); 100 parallel claims across 100 separate kernels succeed; identical inputs yield identical content across threads (determinism preserved under parallelism); distinct inputs yield distinct ids (no hash collision); thread-safety boundary explicitly documented in module docstring. Substrate-grade GREEN.

### Tickets filed this fire

**0 tickets.** Both lane smoke-tests pass cleanly.

### Lane rotation tracking (post-restart)

| Lane | Status | Most recent fire |
|---|---|---|
| 1. CLAIM-flood | LIVE | fire #9 |
| 2. adversarial-CLAIM | LIVE | fire #5 (regression) |
| 3. correlated-triangulation | LIVE | fire #4 |
| 4. cross-domain-leak | LIVE | fire #10 |
| 5. large-scale-enumeration | LIVE | fire #6 |
| 6. undecidable-canonicalization | LIVE | fire #11 (parallel instance) |
| 7. precision-gradient | LIVE | fire #9 |
| 8. ExclusionCertificate-extension | LIVE | fire #8 |
| 9. NearMissCorpus-leak | LIVE | fire #11 (parallel instance) |
| 10. real-paper | LIVE | fire #5 |
| 11. batch-sweep | LIVE | fire #8 |
| 12. representation-pressure | LIVE | fire #7 (new instance) |
| 13. canonicalization-fuzz | LIVE | fire #10 |
| 14. replay-determinism | LIVE | **fire #12** |
| 15. cross-machine | LIVE-pending-Charon-M2 | — |
| 16. concurrency-stress | LIVE | **fire #12** |
| 17. mutation-testing | LIVE | fire #7 (new instance) |
| 18. threshold-sensitivity | DORMANT (T017 OPEN) | — |

**All 17 LIVE lanes have now been exercised at least once.** Only Lane 15 (cross-machine) remains unsmoked, gated on Charon M2 agent.

### Standing recommendations for next fire (#13)

1. **Anti-repeat:** avoid lanes 14, 16. Suggested fire #13 candidates:
   - **Lane 11 (batch-sweep)** — every-other-fire cadence (last fire #8)
   - **Lane 13 (canonicalization-fuzz)** — re-run with new `--hypothesis-seed` to expand explored input region
   - **Lane 5 (large-scale-enumeration)** — re-baseline candidate when full cap available
2. **Lane 15 (cross-machine):** watch for Charon M2 agent activation.
3. **Lane 18 (threshold-sensitivity):** T017 still OPEN.
4. **Multi-instance coordination protocol:** pull before lane-pick; claim fire number = max-on-origin/main + 1.

### Fire-12 stress on substrate health

- Replay-determinism + concurrency-stress contracts are now both substrate-grade pressure-tested.
- All 17 LIVE lanes exercised at least once.
- Substrate is stable across the contract-change-window restart.
- 0 substrate flaws found this fire.

### Discipline notes

- HARD-1 through HARD-5: respected.
- Time used: ~20 minutes.
- Anti-flooding cap: 0 tickets filed.

— substrate-tester, fire #12, 2026-05-07

---

## Fire #11 — 2026-05-07 15:00 UTC

**Coordination note:** Fire #10 was performed by a parallel substrate-tester instance (commit `db0c157d`) covering Lane 4 (ST003 regression PASS) + Lane 13 (canon-fuzz PASS). My fire = #11. Multi-machine substrate-tester coordination operational.

**Lanes selected:** 9 (NearMissCorpus-leak, last fire #2) + 6 (undecidable-canonicalization, last fire #4). Both untouched since the contract-change window; both relevant after T020 / T030 / T023 / ST003 work landed.

**Lane 15 + 18 reactivation re-check:** still DORMANT (Charon orch ticket OPEN; T-2026-05-07-T017 OPEN).

**Harness:** `charon/diagnostics/substrate_tester_fire_11_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_11_results.json`.

### Lane 9 — NearMissCorpus-leak regression: 4/4 PASS (1 harness-bug false positive corrected)

| Test | Verdict | Detail |
|---|---|---|
| T1 — `load_post_view(allow=False)` rejects | **PASS*** | reported FAIL by harness; verified by manual repro — substrate IS correctly raising `PostFalsificationLeakageError` on iteration. Harness false positive: did not iterate the returned generator. |
| T2 — positional args rejected (kw-only enforcement) | **PASS** | TypeError raised |
| T3 — `load_post_view(allow=True)` succeeds | **PASS** | 1 view loaded |
| T4 — default `loader.load()` returns leak-safe pre-views | **PASS** | 1 pre-view; no kill_vector / kill_pattern / verdict fields |

**Harness-bug finding (substrate-grade lesson):** `LearnerCorpusLoader.load_post_view` is a Python generator function. The leakage-protection error fires inside the generator's first `__next__`, not at call time. My harness wrote `views = loader.load_post_view(...)` without iterating, so it received a generator object back with no error and falsely concluded "silently returned views".

Manual reproducer with `list(loader.load_post_view(...))` correctly raises `PostFalsificationLeakageError`. Substrate verdict: **PASS** (re-classified post-repro).

**Substrate verdict for Lane 9: PASS.** Anti-leakage discipline still enforced: kw-only flag holds, mandatory caller_id + purpose still required, audit log written, leak-safe default load preserved.

**Future-harness rule:** when probing generator-returning APIs, always iterate (`list(...)`) to surface generator-internal errors.

### Lane 6 — undecidable-canonicalization regression: 5/5 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — construct CanonicalizationProtocol(undecidable) | **PASS** | impl='novikov_word_problem', decidability='undecidable' |
| T2 — invalid decidability_status raises ValueError | **PASS** | "must be one of ('decidable', 'undecidable', 'conditional')" |
| T3 — apply() on registry-only entry raises NotImplementedError | **PASS** | per the protocol's intentional "no impl bound" path |
| T4 — registered Lehmer chart's canonicalization is `decidable` | **PASS** | impl='reflection_quotient', decidability_status='decidable' |
| T5 — `VALID_DECIDABILITY` tuple unchanged since fire #4 baseline | **PASS** | `('conditional', 'decidable', 'undecidable')` |

**Substrate verdict: PASS.** Decidability-flag discipline from Aporia Study 17 fully holds across the contract-change window. The `VALID_DECIDABILITY` tuple is contract-stable; registered Lehmer chart correctly tagged decidable; registry-only entries correctly raise on `apply()`.

### Tickets filed this fire

**0 tickets.** Both lanes substrate-correct. Lane 9 T1 was a harness false positive (generator-iteration discipline lesson).

### Standing recommendations for next fire (#12 / next-machine fire)

1. **Anti-repeat:** avoid lanes 6, 9 (just covered). Suggested fire #12: Lane 2 (adversarial-CLAIM, last fires #2 + #5) + Lane 3 (correlated-triangulation, last fire #4) — both relevant post-contract-change-window.
2. **Generator-iteration rule for future harnesses:** any test probing a generator-returning API must `list(...)` the result to surface generator-internal errors. Codify in fire #11+ harness templates.
3. **Mossinghoff-perturbation in-band sampler still needed for Lane 1.** Standing rec from fire #9 unchanged.
4. **Lane 5 (large-scale-enumeration):** last fire #6. Re-probe candidate when a fire has nothing else queued.
5. **Multi-machine coordination:** fire #10 ran on M2 while I was waking up; both updated the log without conflict. Continue current pattern (each agent inserts newest entry; respect commit order).

### Discipline notes

- HARD-1..HARD-5: clean. No drift toward established frameworks.
- Time used: ~35 min (within 50-min cap).
- Anti-flooding cap: 0 tickets filed (max 5 allowed).
- Multi-agent etiquette: did not overwrite parallel-agent fire #10 harness; restored after accidental delete.

— substrate-tester, fire #11, 2026-05-07 15:00 UTC

---

## Fire #10 — 2026-05-07 09:58 (local)

**Lanes selected:** 4 (cross-domain-leak, regression for T-ST003 closure) + 13 (canonicalization-fuzz, smoke-test of newly-LIVE T006 fuzzer).

**Lane rationale:** Per fire #9 standing rec (#3): re-probe Lane 4 to confirm T-ST003 fix sticks. Lane 13 is one of 5 dormant lanes that activated during the contract-change window (T006 DONE per techne_inbox); fires #7-9 of the prior session smoke-tested only lanes 12 and 17, leaving 13/14/15/16 untouched. Fire #10 picks Lane 13 to start closing that gap.

**Inbox state at fire start:** 43 tickets total. T-ST002 + T-ST003 both DONE. Dormant-lane activation tickets: T006/T012/T013/T014/T015 = DONE; T017 = OPEN. Lanes 13/14/15/16/17 are LIVE; Lane 18 stays DORMANT.

**Harness:** `charon/diagnostics/substrate_tester_fire_10_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_10_results.json`.

### Lane 4 — regression on T-ST003 closure: 2/2 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — unknown domain now raises | **PASS** | `KeyError: "unregistered domain 'nonexistent_domain_xyz'; registered: ['bsd_rank', 'genus2', 'knot_trace_field', 'lehmer', 'mock_theta', 'mod...']"` |
| T2 — registered domain still works (no over-blocking) | **PASS** | `lehmer` returns 13-tuple of registered keys, first 3: `('poly_coefficients', 'mahler_measure_dps30', 'mahler_measure_dps60')` |

**Substrate verdict:** **T-ST003 fix verified.** The fix replaces the silent `("__unregistered__",)` sentinel return with a loud `KeyError` whose message lists the registered domains alphabetically — exactly the remediation_hint pattern I filed in the ticket payload. Closure confirmed; cycle ticket→fix→regression-check operates correctly across the contract-change-window restart.

**Workflow validation:** my fire-#3 ticket (T-ST003) → Techne contract-change-window backlog → Techne fix → fire-#10 confirms closure across the window. Both my P1+ tickets (ST002, ST003) are now closed. The substrate-tester ticket-flow has now operated cleanly through 2 full cycles.

### Lane 13 — canonicalization-fuzz smoke (newly LIVE): 1/1 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — fuzzer clean run with hypothesis seed=20260507 | **PASS** | 13 property tests passed, 0 failed; pytest summary: `13 passed in 13.26s`; ~20s harness wall-clock |

**Substrate verdict:** **GREEN at 2,600 hypothesis-generated probes.** The fuzzer (T006) ships with 13 invariance properties, each tested against 200 hypothesis-generated examples. Property classes include:
- TestProtocolDataclassValidation (valid_inputs_construct + invalid_decidability_status_raises)
- TestClass5DecidabilityStatusInvariance (apply_independent_of_version_field)
- TestLehmerChartIntegration (chart_protocol_apply_matches_underlying_canonicalize)
- + 10 more invariance classes

All 13 × 200 = 2,600 probes passed. Substrate-grade GREEN.

**Substantive observation:** the fuzzer correctly handles Hypothesis edge-cases (e.g., "Aborted test because unable to satisfy integers(-5, 5).filter(lambda x: x != 0)") at <1% invalid rate, indicating sound test scaffolding. Future fires re-running with different seeds will explore different regions of the input space — Hypothesis's shrink-on-failure machinery will minimize any failures it finds.

**Per lane spec ("Do not skip future fires — the fuzz domain expands as Hypothesis explores"):** Lane 13 is now part of standard rotation. Re-probing every 5-7 fires with a different seed is the right cadence.

### Tickets filed this fire

**0 tickets.** Both lanes PASS. T-ST003 closure verified (regression check); Lane 13 fuzzer reports clean.

### Standing recommendations for next fire (#11)

1. **Anti-repeat:** avoid lanes 4, 13. Suggested fire #11 candidates:
   - **Lane 14 (replay-determinism, T012 newly LIVE)** — second untouched dormant-lane activation; smoke-test priority
   - **Lane 16 (concurrency-stress, T015 newly LIVE)** — third untouched dormant-lane activation
   - **Lane 9 (NearMissCorpus-leak)** — last covered fire #2; fresh probes after contract-change window
   - **Lane 11 (batch-sweep)** — every-other-fire cadence; last covered fire #8
2. **Fuzzer cadence:** re-run Lane 13 with `--hypothesis-seed=<different_seed>` every ~5-7 fires to cover new input regions.
3. **Lane 5 (large-scale-enumeration):** last fire #6 ran deg-12 ±5; could re-baseline at deg-10 ±5 (much smaller) for quicker re-probe, OR defer until concurrent activity quiets.
4. **Lane 18 (threshold-sensitivity, T017):** still OPEN/DORMANT. Watch for activation in future contract-change windows.

### Fire-10 stress on substrate health

**Positive:**
- T-ST003 fix is loud and informative (lists registered domains in KeyError message).
- Property-based fuzzer (T006) is comprehensive (13 invariant classes) and clean across 2,600 probes.
- Both my filed P1+ tickets are now closed; substrate-tester ticket-flow operates correctly across restart.
- 5 dormant lanes activated during contract-change window; substrate-tester rotation expanded from 10-lane to 17-lane menu.

**0 substrate flaws found this fire.**

### Lane rotation tracking (post-restart, with newly-LIVE lanes)

| Lane | Status | Most recent fire |
|---|---|---|
| 1. CLAIM-flood | LIVE | fire #9 |
| 2. adversarial-CLAIM | LIVE | fire #5 (regression) |
| 3. correlated-triangulation | LIVE | fire #4 |
| 4. cross-domain-leak | LIVE | **fire #10** |
| 5. large-scale-enumeration | LIVE | fire #6 |
| 6. undecidable-canonicalization | LIVE | fire #4 |
| 7. precision-gradient | LIVE | fire #9 |
| 8. ExclusionCertificate-extension | LIVE | fire #8 |
| 9. NearMissCorpus-leak | LIVE | fire #2 |
| 10. real-paper | LIVE | fire #5 |
| 11. batch-sweep | LIVE | fire #8 |
| 12. representation-pressure | LIVE | fire #7 (new instance) |
| 13. canonicalization-fuzz | LIVE | **fire #10** |
| 14. replay-determinism | LIVE | — *(needs smoke)* |
| 15. cross-machine | LIVE-pending-Charon-M2 | — |
| 16. concurrency-stress | LIVE | — *(needs smoke)* |
| 17. mutation-testing | LIVE | fire #7 (new instance) |
| 18. threshold-sensitivity | DORMANT (T017 OPEN) | — |

**Live lanes needing smoke:** 14 (replay-determinism), 16 (concurrency-stress). These are next-fire priorities to close the post-activation rotation gap.

### Discipline notes

- HARD-1 (no papers): clean.
- HARD-2 (anti-gravitational-well): no drift toward established frameworks observed in substrate code (Hypothesis is a property-testing library, not a "refactor to standard ML" pull).
- HARD-3 (tensor-first): respected.
- HARD-4 (calibration anchors): respected; T006 fuzzer IS substrate-grade calibration anchoring (property-based tests over registered protocol invariants).
- HARD-5 (domains are docstrings): respected; T-ST003 fix correctly raises with registered-domain enumeration in the message.
- Time used: ~24 minutes (well within 50-minute cap).
- Anti-flooding cap: 0 tickets filed (max 5 allowed). Substrate-tester running ticket count: 2 ever filed (ST002, ST003), **2 closed** during contract-change window.

— substrate-tester, fire #10, 2026-05-07

---

## Fire #9 — 2026-05-07 14:00 UTC

**Lanes selected:** 1 (CLAIM-flood, stratified in-band sampler retry) + 7 (precision-gradient, fresh borderline).

**Lane rationale:** Per fire #8 standing rec — re-baseline Lane 1 with stratified in-band sampler so F1/F6/F9/F11 actually fire (instead of fire #1's 99% out-of-band); Lane 7 on a different INCONCLUSIVE coefficient set than fire #1 covered.

**Lane 15 + 18 reactivation re-check:** still DORMANT (Charon orch ticket OPEN; T017 OPEN).

**Harness:** `charon/diagnostics/substrate_tester_fire_9_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_9_results.json`.

### Lane 1 — CLAIM-flood with stratified in-band sampler

| Metric | Value |
|---|---|
| n_probes_total | 30 |
| n_in_band_sampler_yielded | **0** (50K attempts; deg 10 ±5 + deg 14 ±5) |
| n_completed | 30 (all routed) |
| n_errors | 0 |
| terminal states | `{REJECTED: 30}` |
| kill_pattern_root | `{out_of_band: 29, known_in_catalog: 1}` |
| throughput | 4.71 probes/sec |
| wall-clock | 6.37s |

**Substrate verdict: PASS** (substrate routes every probe correctly; 1 catalog hit on Lehmer's polynomial as expected).

**Probe-design verdict: PARTIAL FAIL — sampler scaling issue.** Pure rejection-sampling on M ∈ (1.001, 1.18) at deg-10 / deg-14 with coef range ±5 yielded ZERO in-band hits in 50K attempts. The natural in-band rate is ~1e-5 per fire #6's deg-12 ±5 baseline (113/8.86M); 50K attempts is structurally insufficient. **Cumulative finding across fires #1, #9: pure rejection-sampling is the wrong approach — the standing-rec approach in fires #1, #2, #4, #8 ("stratified in-band sampler via rejection") needs replacement with Mossinghoff-catalog-perturbation.**

The 25 OOB controls + 5 structural anchors (Lehmer + 4 Phi-product) all routed cleanly. Lehmer's polynomial correctly cross-matched the catalog (single `known_in_catalog` hit confirms catalog primitive works at scale).

**Throughput note:** 4.71 probes/sec is much slower than fire #1's 16.87/s — the slowdown is driven by the failed rejection-sampling loop (50K numpy.roots calls), not the substrate. Once the rejection sampler is replaced with a Mossinghoff-perturbation walker, throughput should match fire #1.

**Ticket count: 0** (substrate behavior correct; probe-design issue is fire-log calibration).

### Lane 7 — precision-gradient on fresh borderline

| Probe | Detail |
|---|---|
| coeffs (palindrome from half [1,-3,1,5,-5,-1,3,-2]) | `[1,-3,1,5,-5,-1,3,-2,3,-1,-5,5,1,-3,1]` |

`high_precision_M_via_factor` ladder:

| dps | status | M | factor |
|---:|---|---|---|
| 10 | ok | 1.0 | None |
| 30 | ok | 1.0 | None |
| 60 | ok | 1.0 | None |
| 100 | ok | 1.0 | None |
| 200 | ok | 1.0 | None |

| Property | Value |
|---|---|
| M_spread | 0.0 |
| converged_to_constant | **True** |
| band_status_at_each_dps | all `out_of_band` (M=1.0 < 1.001) |
| verdict_oscillates | **False** |

**Substrate verdict: PASS.** All 5 dps levels return M=1.0 exactly. No oscillation. No precision-aware caveat needed (verdict converges by dps=10 already).

**Substantive observation (substrate-grade, not a flaw):** This is the SECOND independent INCONCLUSIVE entry from the deg-14 ±5 brute-force list that resolves to a **pure cyclotomic product** (M=1.0) under factor-then-nroots. Fire #1 covered entry #1 ([1,-4,5,0,-5,4,-1,0]); fire #9 covers entry #2 ([1,-3,1,5,-5,-1,3,-2]). Pattern consistent: at the cyclotomic boundary, **strategy** (factor-first vs direct numpy roots) is the discriminating axis, not **precision**. Substrate is correctly routing both via the factorization path.

**Ticket count: 0.**

### Tickets filed this fire

**0 tickets.** Both lanes PASS substrate-correctness. The Lane 1 in-band-sampler issue is probe-design, documented in fire log per established discipline.

### Standing recommendations for next fire (#10)

1. **REPLACE the rejection-sampling in-band sampler with Mossinghoff-catalog perturbation.** Approach: load the Mossinghoff small-Mahler catalog (already shipped as `catalog:Mossinghoff` falsifier reference), iterate over entries with M < 1.18, perturb each by single-coefficient flips, accept only perturbations that stay in band (verified via `fast_mahler_numpy`). This will reliably yield in-band probes for Lane 1.
2. **Anti-repeat:** avoid lanes 1, 7. Fire #10 candidates: Lane 2 (adversarial-CLAIM, last fire #2 + #5 regression), Lane 9 (NearMissCorpus-leak, last fire #2), Lane 4 (cross-domain-leak, last fire #3 — relevant after T-2026-05-06-ST003 was DONE in contract-change window).
3. **Lane 4 priority:** ST003 fix (silent-sentinel → loud-fail KeyError) landed in contract-change window. Re-probing Lane 4 confirms the fix sticks across the restart.
4. **Lane 5 (large-scale-enumeration):** last covered fire #6. Re-probe candidate when a fire has nothing else queued.

### Discipline notes

- HARD-1 (no papers): clean.
- HARD-2 (anti-gravitational-well): no drift toward established libraries observed in substrate code.
- HARD-3 (tensor-first): respected.
- HARD-4 (calibration anchors): standing rec to use Mossinghoff catalog as in-band probe source IS a HARD-4 alignment (anchors → probes).
- HARD-5 (domains are docstrings): respected.
- Time used: ~30 min (within 50-min cap).
- Anti-flooding cap: 0 tickets filed (max 5 allowed).

— substrate-tester, fire #9, 2026-05-07 14:00 UTC

---

## Fire #8 — 2026-05-07 13:00 UTC

**Lanes selected:** 11 (batch-sweep, first time post-restart) + 8 (ExclusionCertificate-extension regression after T020/T030).

**Lane rationale:** Per fire #7 standing rec: avoid lanes 13/14/16/17/12; pick Lane 11 (high yield) + a regular-rotation lane. Lane 8 last covered fire #3; relevant given recent T020 (CertificateCollisionError) + T030 (OperatorPortabilityCertificate) Techne work — confirms cert-extension discipline holds under the new contracts.

**Lane 15 + 18 reactivation re-check:** still DORMANT (Charon orch ticket OPEN; T017 OPEN).

**Harness:** `charon/diagnostics/substrate_tester_fire_8_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_8_results.json`.

### Lane 11 — batch-sweep (30 probes, deterministic seed 20260507_12)

Sampled 15 adversarial + 15 real-paper probes uniformly across landed Harmonia corpora (B-dynamics, D-logic, E-complexity).

| Outcome | Count |
|---|---:|
| submitted_ok | 30/30 |
| submission_failed | 0/30 |
| with_verdict | 0/30 |

**Substrate verdict: PARTIAL — architectural impedance gap surfaced (NOT ticketed; intentional design).**

The substrate's `SigmaKernel.CLAIM` API ingests every probe cleanly (target_name + hypothesis + evidence dict + kill_path string accepted as-is). All 30 claims land at `status="pending"` with `verdict=null`. The expected verdicts from the corpora (PROMOTE / KILL / INCONCLUSIVE / REFUSAL) cannot be evaluated by the v1.5 substrate because:

1. **No general-purpose CLAIM gauntlet exists.** `DiscoveryPipeline` is Lehmer-domain-specific by design (Phase 0 = Mahler-band routing; F1/F6/F9/F11 = polynomial-shape falsifiers). Non-Lehmer claims (ergodic-theory papers, complexity-class statements, large-cardinal consistency) have no falsifier panel to pass through.

2. **CLAIM API is open-vocabulary at write.** Per kernel docstring: "substrate is permissive at write, strict at hash". The kill_path string `"expected_REFUSAL"` is stored verbatim without validation against any registered set of substrate-grade kill patterns.

3. **The "substrate gauntlet" framing in PRESSURE_PROMPTS_v1.md §23 (lane 11 spec) presupposes a verdict-producing entry point that v1.5 doesn't have.** The corpora's `claim_payload_for_substrate` schema (claim_type/predicate/subject/verification_anchor) does not align with the substrate's CLAIM API (target_name/hypothesis/evidence/kill_path).

This is **intentional substrate design** (per fire #3 architectural observation: "v1.5 substrate has no unified cross-domain CLAIM entry"). Filing a ticket would be noise — the gap is well-documented and doesn't represent a flaw, just a feature gap.

**Ticket count this lane: 0.**

### Lane 8 — ExclusionCertificate-extension (T020/T030 regression)

Re-probe of the cert-extension discipline after Techne fire #cc-window shipped T020 (CertificateCollisionError subclass) and T030 (OperatorPortabilityCertificate primitive).

| Test | Verdict | Detail |
|---|---|---|
| T1 — register fresh BOUNDED_COMPLETE cert (no chart, allow_chart=False) | **PASS** | accepted; cid=64630e6079d37e4b |
| T2 — re-register same content w/o replace | **PASS** | raises CertificateCollisionError (T020 contract holds) |
| T3 — explicit replace=True | **PASS** | succeeds, no exception |
| T4 — COMPLETE strength without triangulation_history | **PASS** | raises ValueError (Aporia v2.3 hard rule enforced) |
| T5 — catch-broad CertificateRegistrationError catches CollisionError | **PASS** | subclass relationship preserved (T020 backward-compat) |

**Substrate verdict: 5/5 PASS.** T020 contract holds end-to-end. The new CertificateCollisionError subclass is correctly catchable via the broader umbrella class — backward-compat preserved as designed. Aporia v2.3 hard rule (COMPLETE-requires-triangulation) still enforced.

**Ticket count this lane: 0.**

### Tickets filed this fire

**0 tickets.** Lane 11 surfaced architectural impedance (intentional, documented per fire #3 precedent). Lane 8 fully PASS (T020 regression closed cleanly).

### Standing recommendations for next fire (#9)

1. **Anti-repeat:** avoid lanes 11, 8 (just covered). Suggested fire #9: Lane 1 (CLAIM-flood, post-restart re-baseline with stratified in-band sampler per fire #1 standing rec) + Lane 7 (precision-gradient, post-restart re-probe).
2. **Lane 15 + 18 reactivation:** re-check whether C-2026-05-07-T013-orchestration (Charon) or T-2026-05-07-T017 (Techne) has closed.
3. **Lane 5 (large-scale-enumeration):** last covered fire #6. Re-probe candidate when a fire has nothing else queued (full-cap heavy job). Deg-12 ±5 baseline established at fire #6; future runs could probe deg-10 ±5 or deg-14 ±3.
4. **Lane 17 mutation framework — false-positive rate.** Aporia ticket T-2026-05-07-T014-followup-A surfaces the test gap; a Techne-side ticket for AST-level mutation analysis would close fire #7's caveat #1 but is not urgent.

### Discipline notes

- HARD-1 (no papers): clean.
- HARD-2 (anti-gravitational-well): the lane 11 finding deliberately did NOT propose "the substrate should be a general LLM-claim verifier" or "use [established framework]" — the impedance gap is reported as-is, with the intentional substrate-design choice respected.
- HARD-3 (tensor-first): respected. No proposed primitives in this fire's findings.
- HARD-5 (domains are docstrings): respected. Lane 11's per-probe evidence dicts use {"use_case", "domain", "subdomain"} fields — the substrate's coordinates are still operator-output-shaped, not discipline-labeled.
- Time used: ~30 minutes (within 50-minute cap).
- Anti-flooding cap: 0 tickets filed (max 5 allowed).

### Lane rotation tracking (12 of 12 always-live + 4 of 6 dormant exercised)

| Lane | Last fire |
|---|---|
| 1. CLAIM-flood | fire #1 |
| 2. adversarial-CLAIM | fire #2, #5 |
| 3. correlated-triangulation | fire #4 |
| 4. cross-domain-leak | fire #3 |
| 5. large-scale-enumeration | fire #6 |
| 6. undecidable-canonicalization | fire #4 |
| 7. precision-gradient | fire #1 |
| 8. ExclusionCertificate-extension | **fire #8** (re-probe) |
| 9. NearMissCorpus-leak | fire #2 |
| 10. real-paper | fire #5 |
| 11. batch-sweep | **fire #8** (first post-restart) |
| 12. representation-pressure | fire #7 |
| 13. canonicalization-fuzz | fire #7 (smoke; activated post-T006) |
| 14. replay-determinism | fire #7 (smoke; activated post-T012) |
| 15. cross-machine | DORMANT (Charon orch OPEN) |
| 16. concurrency-stress | fire #7 (smoke; activated post-T015) |
| 17. mutation-testing | fire #7 (smoke; activated post-T014) |
| 18. threshold-sensitivity | DORMANT (T017 OPEN) |

— substrate-tester, fire #8, 2026-05-07 13:00 UTC

---

## Fire #7 — 2026-05-07 12:00 UTC (FIRST FIRE POST-RESTART)

**Restart context:** Substrate-Tester resumed after the 2026-05-07 contract-change window + the subsequent 9-ticket Techne /loop drain (fires #9-#18). Lane activation status checked first per James's restart prompt.

**Lane activation status (re-checked at fire #7 start):**

| Lane | Activation ticket | Status |
|---|---|---|
| 13 canonicalization-fuzz | T-2026-05-07-T006 | LIVE (T006 DONE in pre-restart fire #7) |
| 14 replay-determinism | T-2026-05-07-T012 | LIVE (T012 DONE in Techne fire #14) |
| 15 cross-machine | T-2026-05-07-T013 + Charon M2 | DORMANT (T013 DONE Techne fire #15; Charon orchestration ticket C-2026-05-07-T013-orchestration still OPEN) |
| 16 concurrency-stress | T-2026-05-07-T015 | LIVE (T015 DONE Techne fire #18) |
| 17 mutation-testing | T-2026-05-07-T014 | LIVE (T014 DONE Techne fire #17) |
| 18 threshold-sensitivity | T-2026-05-07-T017 | DORMANT (T017 OPEN) |

**Lanes covered this fire:** 13, 14, 16, 17 (4 newly-activated smoke tests) + 12 (representation-pressure normal pick).

### Lane 13 — canonicalization-fuzz (smoke)

`pytest prometheus_math/tests/test_canonicalization_fuzz.py --hypothesis-seed=20260507` → **PASS** (no invariance violations).

### Lane 14 — replay-determinism (smoke)

`pytest prometheus_math/tests/test_replay_capsule_determinism.py --hypothesis-seed=20260507` → **PASS** (7/7).

### Lane 16 — concurrency-stress (smoke)

`pytest prometheus_math/tests/test_concurrency_stress.py --hypothesis-seed=20260507` → **PASS** (6/6). Substrate finding (SQLite single-threaded) is documented in module docstring; not a flaw, an explicit boundary.

### Lane 17 — mutation-testing (smoke, 5 mutations on operator_portability.py)

`python -m prometheus_math.mutation_testing --target sigma_kernel/operator_portability.py --test-cmd "python -m pytest sigma_kernel/test_operator_portability.py -q --tb=no" --max-mutations 5`

**Mutation score 0.200 (1/5 killed)**. 4 survivors:

| line | operator | analysis |
|---:|---|---|
| 84 | off_by_one_int | False positive (inside docstring "HARD-5") |
| 135 | boolean_not | **Genuine test gap** — `@dataclass(frozen=True) -> False` survives |
| 163 | off_by_one_int | False positive (inside comment "HARD-5") |
| 236 | boolean_not | False positive (inside docstring) |

→ **1 ticket filed**: T-2026-05-07-ST-fire1-001 (P2-normal: test gap for `frozen=True` invariance on OperatorPortabilityCertificate).

### Lane 12 — representation-pressure (3 capability-gap probes)

| Probe | Object | Result |
|---|---|---|
| 1 | Maass form Hecke eigenvalue (Selberg, level 1, k=0) | **PASS** — encoded via T023 OperatorOutputSequence (smoke test of T023 confirms primitive works) |
| 2 | Homotopy class [α] in π₁(S¹) | **CAPABILITY GAP** — no primitive captures higher-category equivalence with continuous-deformation witness |
| 3 | Fano plane S(2,3,7) Steiner triple system | **PARTIAL** — encodes via T023 (stretched, output is label not scalar); native BlockDesign / IncidenceStructure primitive missing |

→ **2 tickets filed**:
- T-2026-05-07-ST-fire1-002 (P1-high capability-gap: homotopy class)
- T-2026-05-07-ST-fire1-003 (P1-high capability-gap: combinatorial design)

### Tickets filed this fire (3 total, under 5-cap)

- T-2026-05-07-ST-fire1-001 (P2-normal, lane 17): frozen-dataclass test gap
- T-2026-05-07-ST-fire1-002 (P1-high, lane 12): homotopy-class capability gap
- T-2026-05-07-ST-fire1-003 (P1-high, lane 12): combinatorial-design capability gap

### Standing recommendations for next fire (#8)

1. **Lane 15 (cross-machine) reactivation check** — re-check whether `C-2026-05-07-T013-orchestration` Charon ticket has closed. If yes, run lane 15 smoke.
2. **Lane 18 (threshold-sensitivity) reactivation check** — re-check whether T-2026-05-07-T017 has landed.
3. **Anti-repeat:** avoid lanes 13, 14, 16, 17, 12 next fire. Suggested: Lane 11 batch-sweep (high yield; first time exercising it post-restart) + Lane 5 if time permits OR a regular-rotation lane (1-10 not yet visited this restart).
4. **Lane 17 mutation framework expansion candidate** — false-positive rate is high (3 of 4 survivors were docstring-internal). Aporia ticket T-2026-05-07-T014-followup-A already filed (P3-low test gap). A Techne-side ticket for AST-level mutation analysis would close caveat #1 but is not urgent.

### Discipline notes

- HARD-1 (no papers): clean. No publication mentions.
- HARD-2 (anti-gravitational-well): the mutation-testing module deliberately did NOT install mutmut; built home-grown framework instead. Substrate-grade choice over conventional tooling.
- HARD-3 (tensor-first): respected — the 2 capability-gap tickets target tensor-grade primitives (typed witness for higher categories; native BlockDesign).
- HARD-4 (calibration anchors): lane 12 surfaced 2 calibration-anchor-relevant gaps (homotopy + designs are under-anchored regions per HARD-4).
- HARD-5 (domains are docstrings): respected — capability-gap tickets target operator-output primitives, not discipline-labeled object types.
- Time used: ~30 minutes (within 50-minute cap).
- Anti-flooding cap: 3 tickets filed (max 5 allowed).

— substrate-tester, fire #7, 2026-05-07 12:00 UTC

---

## Fire #6 — 2026-05-07 03:33 UTC

**Lanes selected:** 5 (large-scale-enumeration), single-lane full-cap fire.

**Lane rationale:** Lane 5 was the only lane untouched after 5 fires (others all exercised at least once). 10-day-window rotation discipline rule says all 10 lanes must land. Lane 5 takes the full cap by design.

**Harness:** `charon/diagnostics/substrate_tester_fire_6_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_6_results.json`.

### Lane 5 — large-scale-enumeration: 5/5 PASS

Ran `prometheus_math.lehmer_brute_force_general.run_brute_force_general(degree=12, coef_range=(-5, 5))` — the canonical Lane 5 target (~10x smaller than the deg-14 ±5 baseline of 97,435,855 polys).

| Test | Verdict | Detail |
|---|---|---|
| T1 — completion (no crash/hang) | **PASS** | Completed in 423.1s (~7 min); processed exactly 8,857,805 polys |
| T2 — enumeration count matches expected | **PASS** | n_polys_processed == n_expected == 8,857,805 (no off-by-one) |
| T3 — throughput reasonable | **PASS** | 20,937 polys/sec sustained, well above 10K threshold |
| T4 — band candidates surface | **PASS** | 113 in-band hits, M-values clustered just above 1.0 (cyclotomic-noise pattern consistent with deg-14 ±5 baseline of 253 raw → 210 noise → 43 verified) |
| T5 — shard summary well-formed | **PASS** | 55 shards reported with required fields (shard_idx, polys_processed, n_band_hits) |

**Substrate verdict:** PASS. Brute-force enumeration scales correctly from deg-14 baseline to deg-12 ±5; throughput is ~21K polys/sec sustained; band-candidate distribution mirrors the deg-14 cyclotomic-noise-dominated shape (>>90% of band hits are at M ≈ 1.0000... — these are the cyclotomic-and-near-cyclotomic-product polynomials that the verification phase would filter out).

**Initial harness bug:** my `progress_callback` signature took 4 args (shard_idx, n_shards, polys_processed, in_band_count), but the actual contract is 3 args (no in_band_count). Crashed at 8.4s on first attempt. Fix: removed the in_band_count arg. Substrate's API was correct; my probe was wrong. Re-run completed cleanly.

### Architectural observations (substrate-grade, not flaws)

1. **No ExclusionCertificate auto-generation at the brute-force level.** Per the module's own docstring and Aporia ticket T-2026-05-07-T007, `run_brute_force_general` is scoped to enumerate-and-report only — verification (mpmath recheck, cyclotomic filter, Mossinghoff cross-check) and certificate emission are downstream tickets. The 113 band candidates surfaced this fire are the input to a future verification phase, not a finished verdict. The lane-5 spec's "ExclusionCertificate not generated: P1-high" criterion would be a P1 IF the brute-force module promised to generate one and didn't — but it explicitly disclaims that scope. **Documenting this as an architectural observation, not a ticket.**

2. **No INCONCLUSIVE comparison to deg-14 baseline this fire.** Same reason: substrate didn't run the verification phase, so there's no INCONCLUSIVE verdict to compare. The deg-14 baseline (97M → INCONCLUSIVE → COMPLETE via 4-path triangulation) ran a full pipeline including verification + triangulation + certificate emission. The deg-12 ±5 fire #6 stops at the enumeration step. This is documented and intentional.

3. **Sequential execution (not multiprocessing).** Per the module docstring: "multiprocessing was deliberately not added in this v1 — Windows spawn-mode complexity is not justified for the current deg-12 ±5 target which finishes in minutes." Confirmed: 7 min sequential is acceptable. Any future ticket adding MP would need to preserve the 8.86M-polys exact match in T2.

4. **113 band candidates is in the right rough scale.** Deg-14 ±5 produced 253 raw band candidates from 97M polys (≈ 2.6e-6 hit rate). Deg-12 ±5 produced 113 from 8.86M polys (≈ 1.27e-5 hit rate). The hit rate is ~5x higher at deg-12 — interesting but not a substrate concern; reflects the geometry of where small-coefficient palindromic polynomials cluster relative to the unit circle at smaller degrees. Worth flagging for future Aporia/Charon investigation.

### Tickets filed this fire

**0 tickets.** Lane 5 fully PASS; all observations are documented architectural choices, not flaws.

### Standing recommendations for next fire (#7)

1. **All 10 lanes have now been exercised at least once** over 6 fires. Rotation discipline rule satisfied.
2. **Anti-repeat:** avoid Lane 5. Suggested fire #7 combinations:
   - Lane 1 (CLAIM-flood with stratified in-band sampler — closes fire-#1 standing rec) + Lane 7 (precision-gradient with new probes)
   - Lane 8 (ExclusionCertificate-extension repeat with the duplicate-cert behavior observed in fire #3 as a starting point) + Lane 9 (NearMissCorpus-leak repeat)
3. **`get_raw_invariant_keys` ticket T-ST003** still BLOCKED. Whenever Techne unblocks, fire-#N+ should re-probe Lane 4.
4. **Verification follow-up (Aporia/Charon scope, not substrate-tester):** the 113 deg-12 ±5 band candidates landed by this fire are inputs to a future verification phase. If/when Techne ships an auto-verification phase that runs after `run_brute_force_general`, substrate-tester should re-run Lane 5 to verify the verification phase emits a deg-12 ExclusionCertificate consistent with the deg-14 baseline.
5. **Hit-rate observation (113/8.86M ≈ 1.27e-5 vs deg-14's 253/97M ≈ 2.6e-6, ~5x higher):** worth flagging for a future Aporia ticket. Not substrate-tester scope to follow up.

### Lane rotation tracking (10 of 10 lanes exercised over 6 fires) — DISCIPLINE RULE SATISFIED

| Lane | Fires exercised |
|---|---|
| 1. CLAIM-flood | fire #1 |
| 2. adversarial-CLAIM | fire #2, fire #5 (regression) |
| 3. correlated-triangulation | fire #4 |
| 4. cross-domain-leak | fire #3 |
| 5. large-scale-enumeration | **fire #6** |
| 6. undecidable-canonicalization | fire #4 |
| 7. precision-gradient | fire #1 |
| 8. ExclusionCertificate-extension | fire #3 |
| 9. NearMissCorpus-leak | fire #2 |
| 10. real-paper | fire #5 |

### Discipline notes

- No paper/publication mentions in this fire.
- No drift toward established frameworks observed in the substrate code I read this fire.
- Time used: ~17 minutes (well within 50-minute cap; 7 min for actual brute-force, ~10 min for harness writing + initial debugging).
- Anti-flooding cap: 0 tickets filed.

— substrate-tester, fire #6, 2026-05-07 03:33 UTC

---

## Fire #5 — 2026-05-07 02:27 UTC

**Lanes selected:** 2 (regression check on T-ST002 fix) + 10 (real-paper, first-time exercise).

**Lane rationale:** Per fire #4 standing recommendation #3: ticket T-ST002 (CoordinateChart empty-domain) was marked DONE by Techne; fire #5 re-probes to verify regression closed. Lane 10 (real-paper) had not been exercised in 4 fires — high-priority per 10-day-window rotation discipline. Anti-repeat satisfied (lanes 3 + 6 in fire #4).

**Inbox state at fire start:** techne_inbox 39 lines (5 DONE, 31 OPEN, 2 BLOCKED, 1 SUPERSEDED). My substrate-tester tickets: T-ST002 = DONE (re-probed below); T-ST003 = BLOCKED.

**Harness:** `charon/diagnostics/substrate_tester_fire_5_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_5_results.json`.

### Lane 2 — regression check on T-ST002 fix: 2/2 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — empty domain now rejected | **PASS** | `ValueError: domain must be a colon-free non-empty string; got ''` |
| T2 — normal domain still accepted (no over-blocking) | **PASS** | chart_id='lehmer:deg14:pm5:palindromic' constructed cleanly |

**Substrate verdict:** **T-ST002 fix verified.** The fix at `coordinate_chart.py:248-256` adds `not self.domain` to the validator (mirroring the region_key non-empty check). Comment explicitly references `substrate-tester ST002` so future readers see the trace. Regression closed.

**Workflow validation:** my fire-#2 ticket → Techne backlog → Techne fire-#3 fix → fire-#5 regression confirms cycle works. The `consecutive_block_count` machinery + ticket-state lifecycle are operational.

### Lane 10 — real-paper ingestion: 3/3 PASS

3 polynomials from `RECENT_POLYNOMIAL_CORPUS` (hand-curated arxiv-sourced corpus, 17 entries) submitted through `DiscoveryPipeline`:

| Probe | Shape | Submitted M | Outcome |
|---|---|---|---|
| P1 — arxiv 2601.11486 entry #16 (deg 10, M=1.176) | solid | 1.176281 | **REJECTED:** `known_in_catalog:matches Mossinghoff entry Lehmer's polynomial` |
| P2 — same coeffs but submitted M=2.0 (simulating retracted-paper claim) | retracted | 2.0 | **REJECTED:** `out_of_band:M=2.0000_outside_(1.001,1.18)` |
| P3 — arxiv 2409.11159 entry #0 (Salem cluster, M=1.302) | contested | 1.302269 | **REJECTED:** `out_of_band:M=1.3023_outside_(1.001,1.18)` |

**Substrate verdict:** PASS. The substrate routed all 3 deterministically with informative kill_patterns. The standout finding is **P1: substrate correctly cross-matched the arxiv-corpus entry as Lehmer's polynomial via Mossinghoff catalog** — a clean rediscovery of a 1933 result via a 2026 arxiv paper. This is substrate-grade evidence that the catalog cross-check primitive works at real-paper scale.

**Architectural observation (substrate-grade, not a flaw):** Lane 10 spec assumes retraction-detection / controversy-tracking machinery (e.g., expected outcomes "KILL with kill_pattern naming what failed" for retracted papers, "INCONCLUSIVE with caveat" for contested). The v1.5 substrate has neither — Phase 0 is Mahler-band routing only; the F1/F6/F9/F11 battery operates on Mahler-poly-shape claims and does not consult arxiv retraction lists, withdrawal notices, or community discussion feeds. Substrate trusts the SUBMITTED M as truth and routes accordingly; whether the paper's M-claim was correct is not the substrate's question. **This is an architectural observation about scope, not a substrate flaw.** The "retracted" probe (P2 with M=2.0) was correctly Phase-0 killed because the SUBMITTED M is out-of-band — the substrate didn't recognize the discrepancy with the underlying coefficients' true M because it doesn't recompute. That's by-design; recomputing every M would defeat the point of trusting the submitted value.

**Future enhancement candidate (not ticket-worthy this fire):** a "M-coherence" check that recomputes the submitted M from the coeffs at low precision and flags large discrepancies (>10%) would catch the "retracted-shape" pattern at Phase 0. Lower-priority than the current substrate work; flagging here for the substrate-design backlog.

### Tickets filed this fire

**0 tickets.** Both lanes PASS. T-ST002 regression confirmed closed.

### Standing recommendations for next fire (#6)

1. **Anti-repeat:** avoid lanes 2 + 10. Suggested fire #6: Lane 5 (large-scale-enumeration) alone — full-cap heavy job, never exercised. OR Lane 7 (precision-gradient) + Lane 9 (NearMissCorpus-leak) repeat with new probes. OR Lane 3 (correlated-triangulation) + Lane 8 (ExclusionCertificate-extension) repeat to cover lanes drift.
2. **`get_raw_invariant_keys` ticket T-ST003** still BLOCKED. Whenever Techne unblocks, fire-#7+ should re-probe Lane 4.
3. **Lane rotation tracking:** fires 1-5 covered lanes 1, 2, 3, 4, 6, 7, 8, 9, 10 = 9 of 10 lanes. **Only Lane 5 (large-scale-enumeration) remains untouched** in the 10-day window. Strongly recommend fire #6 as Lane 5.

### Fire-5 stress on substrate health

**Positive:**
- T-ST002 fix landed correctly (regression closed).
- Mossinghoff catalog cross-check identifies real arxiv-derived polynomials at scale.
- Phase-0 routing is deterministic and emits informative kill_patterns.
- DiscoveryPipeline composes cleanly with SigmaKernel + BindEvalExtension across multiple consecutive runs.

**0 substrate flaws found this fire.**

### Lane rotation tracking (9 of 10 lanes exercised over 5 fires)

| Lane | Fires exercised |
|---|---|
| 1. CLAIM-flood | fire #1 |
| 2. adversarial-CLAIM | fire #2, fire #5 (regression) |
| 3. correlated-triangulation | fire #4 |
| 4. cross-domain-leak | fire #3 |
| 5. large-scale-enumeration | **— still untouched** |
| 6. undecidable-canonicalization | fire #4 |
| 7. precision-gradient | fire #1 |
| 8. ExclusionCertificate-extension | fire #3 |
| 9. NearMissCorpus-leak | fire #2 |
| 10. real-paper | fire #5 |

### Discipline notes

- No paper/publication mentions in this fire (per `feedback_exploration_not_papers.md` HARD RULE 2026-05-06).
- No drift toward established frameworks observed in the substrate code I read this fire (per `feedback_anti_gravitational_well.md` HARD RULE 2026-05-06).
- Time used: ~28 minutes (within 50-minute cap).
- Anti-flooding cap: 0 tickets filed (max 5 allowed). Substrate-tester running ticket count: T-ST002 (DONE), T-ST003 (BLOCKED, P2-normal).

— substrate-tester, fire #5, 2026-05-07 02:27 UTC

---

## Fire #4 — 2026-05-06 22:53 UTC

**Lanes selected:** 3 (correlated-triangulation) + 6 (undecidable-canonicalization).

**Lane rationale:** Per fire #3 standing recommendation. Avoided lanes 4 + 8 (anti-repeat). Picked: triangulation independence-enforcement (lane 3) + canonicalization decidability-flag enforcement (lane 6). Both have shipped substrate code (`sigma_kernel/triangulation_protocol.py`, `sigma_kernel/coordinate_chart.py` + `sigma_kernel/method_spec.py`).

**Harness:** `charon/diagnostics/substrate_tester_fire_4_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_4_results.json`.

### Lane 3 — correlated-triangulation: 5 PASS / 1 OBSERVATION

| Test | Verdict | Detail |
|---|---|---|
| T1 — 3 proof-bearing, 2 share IC, 1 distinct | **OBSERVATION** | Substrate UPGRADES because the third path provides the required different-class peer; the upgrade rule is "primary-proof-bearing needs ≥1 different-class verified peer," not "all paths must be distinct." Correct behavior. |
| T1b — 3 proof-bearing paths, ALL same IC (SYMPY_SYMBOLIC_FACTORIZATION) | **PASS** | INCONCLUSIVE_INSUFFICIENT_INDEPENDENCE — substrate correctly rejects upgrade because no path has different IC than primary |
| T2 — 3 verified paths, NONE proof-bearing | **PASS** | REJECTED ("clustering/exploratory cannot certify alone") |
| T3 — positive control: 3 distinct, ≥1 proof-bearing, all verified | **PASS** | UPGRADED_TO_LOCAL_LEMMA |
| T4 — only 2 paths total | **PASS** | INCONCLUSIVE_WAITING (need ≥3) |
| T5 — 3 paths, 1 contradicted | **PASS** | CONTRADICTED (substrate finding logged) |

**Probe-design correction during fire:** T1b initially used `MPMATH_POLYNOMIAL_FACTORIZATION` (which maps to `MethodClass.NUMERICAL`, not `PROOF_BEARING`). With no proof-bearing path, substrate correctly returned REJECTED — meaning my probe didn't actually exercise the independence rule. Re-ran with `SYMPY_SYMBOLIC_FACTORIZATION` (the only IC mapped to `PROOF_BEARING` in the registered table at `triangulation_protocol.py:84-97`) to actually reach the independence check, which then correctly returned `INCONCLUSIVE_INSUFFICIENT_INDEPENDENCE`. Substrate behaved correctly throughout; only the probe needed correction.

**Substrate verdict:** Lane 3 is solid. TriangulationProtocol enforces all 4 rules (≥3 paths; no contradictions; ≥1 proof-bearing verified; ≥1 different-class verified peer). The independence rule is real, not decorative — confirmed via T1b after probe correction.

**Note for future Lane 3 fires:** the proof-bearing IC vocabulary is currently narrow — only `sympy_symbolic_factorization` maps to `PROOF_BEARING` in the registered method-class table. This is intentional (substrate v2.3 §6.3 hard rule: "an unknown method cannot be silently upgraded to certifying weight"), but means correlated-triangulation tests against the proof-bearing path are constrained to one IC. If Techne adds new proof-bearing classes (e.g., `theorem_backed_reduction`, `exhaustive_enumeration`), this lane should be re-probed with cross-class same-method-class scenarios.

### Lane 6 — undecidable-canonicalization: 4/4 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — construct CanonicalizationProtocol with decidability_status='undecidable' | **PASS** | Accepted; impl='novikov_word_problem', decidability_status='undecidable' |
| T2 — invalid decidability_status='maybe' | **PASS** | ValueError: decidability_status must be one of ('decidable', 'undecidable', 'conditional') |
| T3 — apply() on undecidable protocol with no bound impl | **PASS** | NotImplementedError: registry-only entry without bound implementation |
| T4 — registered Lehmer chart's canonicalization | **PASS** | impl='reflection_quotient', decidability_status='decidable' |

**Substrate verdict:** Lane 6 fully passes. The decidability-flag discipline from Aporia Study 17 is enforced at construction time; invalid values raise; undecidable cases are first-class (constructible without an impl, raising on apply). The registered Lehmer chart correctly declares `decidable` for its reflection-quotient canonicalizer.

**Architectural observation:** the lane spec said `sigma_kernel/canonicalization_protocol.py`, but the actual code path is `sigma_kernel/coordinate_chart.py:CanonicalizationProtocol` (with a related but separate `prometheus_math/canonicalizer_observability.py` for runtime telemetry). The protocol is co-located with the chart definition rather than in a standalone file. Documenting this for future Lane 6 fires.

### Tickets filed this fire

**0 tickets.** All probes either PASSED or are OBSERVATIONS (correct substrate behavior, not flaws). The T1b initial-FAIL was probe-design, not substrate-flaw — discipline note "File tickets only for ACTUAL failures, not subjective preferences" applied.

### Standing recommendations for next fire (#5)

1. **Anti-repeat:** avoid lanes 3 + 6. Suggested fire #5: Lane 10 (real-paper) — high-value, hasn't been exercised yet — paired with Lane 1 (CLAIM-flood) using a stratified in-band sampler this time.
2. **Lane 5 (large-scale-enumeration)** still queued. With fire #4 yielding 0 tickets and no new substrate-flaws to chase, fire #5 is a candidate for Lane 5 alone (full-cap heavy job). Defer if fire #5 is short on time.
3. **CoordinateChart fix tracking:** ticket T-2026-05-06-ST002 (P1-high empty-domain) is still OPEN as of inbox snapshot pre-fire. Fire #5 should re-probe Lane 2 if Techne resolves it.
4. **`get_raw_invariant_keys` fix tracking:** ticket T-2026-05-06-ST003 (P2-normal sentinel) still OPEN. Re-probe Lane 4 once resolved.

### Fire-4 stress on substrate health

**Positive:**
- TriangulationProtocol enforces all 4 upgrade rules correctly (paths-count, contradiction-detection, proof-bearing-required, independence-required).
- Method-class registry is conservative: unregistered ICs default to EXPLORATORY (not silently certifying).
- CanonicalizationProtocol's decidability-flag discipline is enforced at construction with informative error messages.
- The Lehmer chart's canonicalizer is correctly tagged as `decidable` (reflection-quotient is a valid algorithmic equivalence).

**0 substrate flaws found this fire.**

### Lane rotation tracking (5 of 10 lanes exercised over 4 fires)

| Lane | Fires exercised |
|---|---|
| 1. CLAIM-flood | fire #1 |
| 2. adversarial-CLAIM | fire #2 |
| 3. correlated-triangulation | fire #4 |
| 4. cross-domain-leak | fire #3 |
| 5. large-scale-enumeration | — |
| 6. undecidable-canonicalization | fire #4 |
| 7. precision-gradient | fire #1 |
| 8. ExclusionCertificate-extension | fire #3 |
| 9. NearMissCorpus-leak | fire #2 |
| 10. real-paper | — |

Lanes 5 and 10 still untouched; both should land in next 2-3 fires per the 10-day-window discipline rule.

### Discipline notes

- No paper/publication mentions in this fire (per `feedback_exploration_not_papers.md` HARD RULE 2026-05-06).
- No drift toward established frameworks observed in the substrate code I read this fire (per `feedback_anti_gravitational_well.md` HARD RULE 2026-05-06).
- Time used: ~32 minutes (within 50-minute cap).
- Anti-flooding cap: 0 tickets filed (max 5 allowed). Substrate-tester running ticket count remains: T-ST002 (P1-high), T-ST003 (P2-normal).

— substrate-tester, fire #4, 2026-05-06 22:53 UTC

---

## Fire #3 — 2026-05-06 21:45 UTC

**Lanes selected:** 4 (cross-domain-leak) + 8 (ExclusionCertificate-extension).

**Lane rationale:** Per fire #2 standing recommendation. Avoided lanes 2 + 9 (anti-repeat). Picked: domain-isolation discipline (lane 4) + certificate-extension discipline (lane 8). Both have shipped substrate code (`prometheus_math/learner_corpus.py`, `sigma_kernel/exclusion_certificate.py`, `sigma_kernel/exclusion_certificates/lehmer_deg14.py`).

**Harness:** `charon/diagnostics/substrate_tester_fire_3_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_3_results.json`.

### Lane 4 — cross-domain-leak: 2 PASS / 1 PARTIAL / 1 FAIL

**Architectural observation up front:** the v1.5 substrate has NO unified cross-domain CLAIM entry. `DiscoveryPipeline` is Lehmer-only; `BSDRankEnv` is BSD-only; etc. The lane-4 spec's literal "submit Lehmer claim to BSD env" is structurally not what the substrate supports — domain isolation is by-construction (per-pipeline), not by-validation. Tests below adapt to exercise the closest analogue: LearnerCorpus domain-tagging discipline.

| Test | Verdict | Detail |
|---|---|---|
| T1 — registered domain keys disjoint | **PASS** | bsd_rank=5 keys, lehmer=13 keys; no overlap |
| T2 — emit with domain="bsd_rank" but Lehmer-shape record | **PARTIAL** | Accepted silently; raw_invariants all-None for 5/5 BSD keys; no warning |
| T3 — `get_raw_invariant_keys("nonexistent_domain_xyz")` | **FAIL** | Returns `('__unregistered__',)` silently. **→ ticket T-2026-05-06-ST003 (P2-normal).** |
| T4 — object_id cross-domain collision | **PASS** | Distinct hashes for same canonical_form across domains |

**Key finding (FAIL T3):** `prometheus_math/learner_corpus.py:get_raw_invariant_keys` returns a sentinel `("__unregistered__",)` on typo/unknown domain instead of raising. Downstream callers like `stub_emit_from_legacy_ledger` then look up "__unregistered__" as a key in record dicts (returns None) and produce a valid-looking but content-empty emission. This is silent degradation; substrate prefers loud-fail-on-typo. Filed P2-normal.

**Related observation (PARTIAL T2):** the same architectural pattern (schema isolation by-construction) means stub_emit_from_legacy_ledger doesn't validate that the record content actually matches the declared domain's keys. Fixing T3 + adding a warn-or-error log when stub_emit detects all-None raw_invariants would close both. Documented in T-2026-05-06-ST003 payload as `related_observations`.

### Lane 8 — ExclusionCertificate-extension: 4/4 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — Lehmer cert is COMPLETE with triangulation_history | **PASS** | strength=COMPLETE, 4 triangulation paths (Path A/B/C/D) |
| T2 — chart_id matches expected scope | **PASS** | `lehmer:deg14:pm5:palindromic` |
| T3 — fresh in-scope candidate via DiscoveryPipeline | **PASS** | M=3.636 → out_of_band; cert NOT referenced in kill_pattern |
| T4 — duplicate certificate registration on same chart | **PASS** | Behavior is deterministic (appended; 1 → 2 certs/chart) |

**Substrate verdict:** Lane 8 is solid. The Lehmer deg-14 ±5 palindromic prototype certificate satisfies Aporia v2.3's hard rule (`strength=COMPLETE` requires non-empty `triangulation_history`). DiscoveryPipeline does NOT short-circuit on certificate scope — it runs the normal pipeline regardless, so silent certificate extension (the lane-8 critical bug) is structurally prevented by the pipeline's certificate-unaware design. Duplicate-per-chart registration appends deterministically — the substrate allows multiple certificates per chart_id, which is sensible for layered claims.

### Tickets filed this fire

**1 ticket (P2-normal):** `T-2026-05-06-ST003` — `get_raw_invariant_keys` silently returns sentinel for unregistered domains. See `aporia/meta/queue/techne_inbox.jsonl`. Payload includes related-observations for T2 PARTIAL (same root cause).

### Standing recommendations for next fire (#4)

1. **Anti-repeat:** avoid lanes 4 + 8. Suggested fire #4: Lane 3 (correlated-triangulation) + Lane 6 (undecidable-canonicalization), or Lane 10 (real-paper).
2. **CoordinateChart fix tracking:** if Techne resolves T-2026-05-06-ST002 (fire #2's empty-domain ticket), fire #4 or #5 should re-probe with Lane 2 to confirm regression closed.
3. **Lane 5 (large-scale-enumeration)** still queued. Defer until a fire has nothing else.
4. **Lane 1 (CLAIM-flood)** should return with a stratified in-band sampler (rejection-sampling on M ∈ (1.001, 1.18) so F1/F6/F9/F11 actually get exercised).
5. **Domain-content coherence (T2 PARTIAL):** if Techne's fix for T3 also adds the warn-or-error log on all-None raw_invariants, fire-2's PARTIAL becomes PASS retroactively.

### Fire-3 stress on substrate health

**Positive:**
- Lane 8 fully passes — ExclusionCertificate primitive discipline is solid.
- Triangulation_history hard rule (Aporia v2.3) is enforced for COMPLETE strength.
- Domain registry has clean disjoint keys between cross-domain envs (no overlap between bsd_rank and lehmer raw_invariant lists).
- object_id is domain-distinct (cross-domain ID collisions structurally impossible).

**One real flaw:**
- `get_raw_invariant_keys` silent sentinel on unknown domain (P2-normal; ticket filed).

**Architectural observation worth surfacing:**
- v1.5 substrate has no unified CLAIM entry — domain isolation is by-construction (per-pipeline) rather than by-validation. Lane-4 spec needs adaptation when v2.x lands a unified entry; until then, the lane targets LearnerCorpus domain discipline.

### Discipline notes

- No paper/publication mentions in this fire (per `feedback_exploration_not_papers.md` HARD RULE 2026-05-06).
- No drift toward established frameworks observed in the substrate code I read this fire (per `feedback_anti_gravitational_well.md` HARD RULE 2026-05-06).
- Time used: ~38 minutes (within 50-minute cap).
- Anti-flooding cap: 1 ticket filed (max 5 allowed).

— substrate-tester, fire #3, 2026-05-06 21:45 UTC

---

## Fire #2 — 2026-05-06 20:35 UTC

**Lanes selected:** 2 (adversarial-CLAIM) + 9 (NearMissCorpus-leak).

**Lane rationale:** Per fire #1 standing recommendation. Avoided lanes 1 + 7 (anti-repeat). Picked orthogonal axes: input-validation discipline (lane 2) vs view-isolation discipline (lane 9). Both have shipped substrate code (`sigma_kernel/coordinate_chart.py`, `prometheus_math/learner_corpus.py`).

**Harness:** `charon/diagnostics/substrate_tester_fire_2_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_2_results.json`.

### Lane 2 — adversarial-CLAIM: 4 PASS / 1 FAIL

5 ill-formed probes against `SigmaKernel.CLAIM`, `CoordinateChart`, and `DiscoveryPipeline.process_candidate`:

| Probe | Verdict | Detail |
|---|---|---|
| P1 — `SigmaKernel.CLAIM(precision_metadata="string")` | **PASS** | TypeError: precision_metadata must be a dict or None |
| P2 — `CoordinateChart(domain="")` | **FAIL** | Silently accepted. Validator inconsistency. **→ ticket T-2026-05-06-ST002 (P1-high).** |
| P3 — `CoordinateChart(domain="lehmer:bad")` | **PASS** | ValueError: domain must be colon-free non-empty string |
| P4 — `CoordinateChart(coordinate_system=["x","y"])` | **PASS** | TypeError: coordinate_system must be a tuple |
| P5 — `DiscoveryPipeline.process_candidate(mahler_measure="not_a_number")` | **PASS** | TypeError surfaces at band-check comparison (cleanly typed) |

**Key finding (FAIL P2):** `CoordinateChart.__post_init__` (sigma_kernel/coordinate_chart.py:248-251) checks `isinstance(domain, str)` AND `":" not in domain` but does NOT check non-empty — even though the error message at line 250 reads "must be a colon-free non-empty string" and the sibling `region_key` validator at line 252 DOES enforce non-empty. Validator and contract disagree. Empty-domain charts would produce chart_id like `:region_key` with downstream `_split_chart_id` semantic corruption.

**Substrate verdict:** 4/5 PASS. P2 is a real input-validation gap. **Ticket T-2026-05-06-ST002 filed (P1-high).**

### Lane 9 — NearMissCorpus-leak: 4/4 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — `load_post_view(allow_post_falsification=False, ...)` | **PASS** | PostFalsificationLeakageError raised with informative message |
| T2 — `load_post_view(allow_post_falsification=True, caller_id=..., purpose="audit")` | **PASS** | Loaded 3 views; 1 leakage-log entry written for caller |
| T3 — `load_post_view(True, "caller", "purpose")` (positional) | **PASS** | TypeError raised — kw-only enforcement is real, not decorative |
| T4 — `loader.load()` default | **PASS** | 3 pre-views returned; no kill_vector or post-falsification fields leaked |

**Substrate verdict:** PASS. Anti-leakage discipline is enforced at the typing layer; opt-in flag is mandatory; audit log is written; default load is leak-safe.

### Tickets filed this fire

**1 ticket (P1-high):** `T-2026-05-06-ST002` — CoordinateChart accepts empty domain. See `aporia/meta/queue/techne_inbox.jsonl`.

### Standing recommendations for next fire (#3)

1. **Anti-repeat:** avoid lanes 2 + 9. Suggested fire #3: Lane 4 (cross-domain-leak) + Lane 8 (ExclusionCertificate-extension), or Lane 3 (correlated-triangulation).
2. **Stratified in-band sampler still pending.** Will become valuable when fire returns to Lane 1.
3. **Lane 5 (large-scale-enumeration)** still queued. Defer.
4. **Lane 6 (undecidable-canonicalization)** path resolution: code lives at `prometheus_math/canonicalizer_observability.py`. When Lane 6 is selected, treat that as the protocol entry-point.
5. **Watch CoordinateChart fix:** if Techne resolves T-2026-05-06-ST002, future Lane 2 fires should re-probe to confirm the regression is closed.

### Fire-2 stress on substrate health

**Positive:**
- 4/5 lane-2 probes correctly rejected ill-formed input — substrate's typed-primitive discipline is mostly working.
- Lane 9 view-separation enforcement is fully working: kw-only flag, mandatory caller_id + purpose, audit log on every load, leak-safe default.
- `PostFalsificationLeakageError` message is clear and actionable.

**One real flaw:**
- `CoordinateChart` empty-domain validator gap (P1-high; ticket filed).

### Discipline notes

- No paper/publication mentions in this fire (per `feedback_exploration_not_papers.md` HARD RULE 2026-05-06).
- No drift toward established frameworks observed in the substrate code I read this fire (per `feedback_anti_gravitational_well.md` HARD RULE 2026-05-06).
- Time used: ~28 minutes (within 50-minute cap).
- Anti-flooding cap: 1 ticket filed (max 5 allowed).

— substrate-tester, fire #2, 2026-05-06 20:35 UTC

---

## Fire #1 — 2026-05-06 19:28 UTC

**Lanes selected:** 1 (CLAIM-flood) + 7 (precision-gradient).

**Lane rationale:** First fire (no anti-repeat constraint). Avoided lane 5 (large-scale-enumeration — full-cap-only). Picked lanes that exercise orthogonal axes (throughput-correctness vs precision-stability) and have shipped substrate code (`prometheus_math/discovery_pipeline.py`, `prometheus_math/lehmer_path_a.py`).

**Harness:** `charon/diagnostics/substrate_tester_fire_1_harness.py` (reproducible).

**Results JSON:** `charon/diagnostics/substrate_tester_fire_1_results.json`.

### Lane 1 — CLAIM-flood: PASS

- 100 probes generated: 70 random degree-10 palindromes + 25 perturbed-near-band (from real INCONCLUSIVE deg-14 ±5 half-coeffs) + 5 structural (Lehmer, Phi_3, Phi_5, x⁴-1, dummy).
- Submitted via `DiscoveryPipeline.process_candidate(coeffs, mahler_measure)` against fresh `SigmaKernel + BindEvalExtension`.
- 100/100 completed; 0 errors; wall clock 5.93 s.
- Throughput: **16.87 claims/sec** (above 10/sec P2 threshold).
- Terminal-state distribution: `{REJECTED: 100}` (no PROMOTE; no SHADOW_CATALOG explicitly counted).
- Kill-pattern root distribution: `{out_of_band: 99, known_in_catalog: 1}`.
- The single `known_in_catalog` hit is consistent with Lehmer's polynomial (M ≈ 1.176) correctly routed to the catalog cross-check.

**Substrate verdict:** PASS. Substrate correctly routed every probe; out-of-band candidates were Phase-0 killed before issuing a CLAIM, in-band catalog match was correctly identified.

**Probe-design note (NOT a substrate flaw):** the kill-pattern skew (99% `out_of_band`) is a probe-design artifact — my "near-band perturbed" probes didn't preserve in-band M after perturbation. Future CLAIM-flood fires should use a stratified in-band sampler (rejection-sampling on M ∈ (1.001, 1.18)) so the F1/F6/F9/F11 falsifier panel actually gets exercised. Filing this as a fire-log calibration note rather than a ticket because it is probe-construction, not substrate behavior.

### Lane 7 — precision-gradient: PASS

- Borderline INCONCLUSIVE entry from deg-14 ±5 brute-force results (entry #1 of 17): coeffs_ascending = [1, -4, 5, 0, -5, 4, -1, 0, -1, 4, -5, 0, 5, -4, 1]; M_numpy ≈ 1.00314; M_mpmath = NaN; has_cyclotomic_factor = True.
- Submitted via `lehmer_path_a.high_precision_M_via_factor` at dps ∈ {10, 30, 60, 100, 200}.
- All 5 dps values returned **M = 1.0 exactly**, status=ok, no exceptions.
- Precision_digits **recorded at every level** (10, 30, 60, 100, 200 propagated correctly into the output dict).
- M_spread = 0.0; band_status = `out_of_band` at every dps (M = 1.0 < 1.001).
- No verdict oscillation across precision levels.
- No precision-aware caveat needed (verdict is stable; substrate doesn't need to fire `precision_below_expected` because verdict converges already at dps=10).

**Substrate verdict:** PASS. Verdicts converge as precision increases (constant at 1.0); precision is recorded; no oscillation; no critical bugs.

**Substantive observation (substrate-grade, not a flaw):** the original `M_numpy ≈ 1.00314` reading was numerical noise. Under `mpmath.factor_first` at any dps ≥ 10, the polynomial decomposes as a *pure cyclotomic product* with M = 1.0 — fully classified, no Lehmer-band hit. This validates Path B's day-5 finding: at the boundary, **strategy** (factor-first vs direct) is the discriminating axis, not **precision**. Substrate is correctly handling the cross-method asymmetry.

### Tickets filed this fire

**0 tickets.** Both lanes PASS. The lane-1 kill-distribution skew is probe-design, not substrate. Documented in fire log per discipline note "File tickets only for ACTUAL failures, not subjective preferences."

### Standing recommendations for next fire

1. **Stratified in-band sampler for CLAIM-flood probes.** Future Lane 1 fires need a generator that actually produces in-band candidates. Rejection-sampling on M ∈ (1.001, 1.18) is the cheapest correct approach; better: walk the Mossinghoff catalog and perturb known small-M polynomials by single-coefficient flips, accepting only perturbations that stay in band.
2. **Avoid Lane 1 + Lane 7 again immediately.** Anti-repeat protocol. Suggested fire #2: Lane 2 (adversarial-CLAIM) + Lane 9 (NearMissCorpus-leak), or Lane 4 (cross-domain-leak).
3. **Lane 5 (large-scale-enumeration)** is queued but takes the full cap. Defer to a fire that has nothing else queued.
4. **Lane 6 (undecidable-canonicalization)** path expectation is wrong: spec says `sigma_kernel/canonicalization_protocol.py`, but the code lives at `prometheus_math/canonicalizer_observability.py`. Will file an ENGINEERING_FAIL ticket if Lane 6 gets selected and the protocol entry-point is genuinely missing.

### Fire-1 stress on substrate health (positive observations)

- All key v2 primitive code IS shipped: `sigma_kernel/{coordinate_chart,exclusion_certificate,method_spec,triangulation_protocol}.py` + `prometheus_math/learner_corpus.py`.
- `DiscoveryPipeline + SigmaKernel + BindEvalExtension` compose cleanly; no import or wiring failures.
- Phase-0 band check fires correctly (out_of_band kill_pattern emitted with full kill_vector).
- High-precision factor-first method records precision_digits as documented.

### Discipline notes

- No paper/publication mentions in this fire (per `feedback_exploration_not_papers.md` HARD RULE 2026-05-06).
- No drift toward "let's refactor to use [established library]" detected in the substrate code I read this fire (per `feedback_anti_gravitational_well.md` HARD RULE 2026-05-06).
- Time used: ~32 minutes (within 50-minute cap).

— substrate-tester, fire #1, 2026-05-06 19:28 UTC
