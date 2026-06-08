# Reasoning-Steering / Arachne — Progress Log

**Discipline:** append a datestamped entry for *every* step as it happens — design
decisions, files written, commits, kills, open forks. We lost the entire Arachne
build once to a network drop because it lived only in conversation; nothing that
matters stays in chat. Newest entries at the bottom.

---

## 2026-06-05/06 — Session: reasoning-steering v0.1 → v0.2, Arachne design

### Context recovered after network drop
- Session restarted; lost connectivity mid-work. Believed we were on
  `reasoning_steering_protocol_v0.1.md`; actual live thread was **Arachne** (math
  crawler swarm) + the reasoning-ladder unification.
- **Disk reality check:** NOTHING of Arachne persisted to this machine. No
  `arachne/` dir, no foundational doc, nothing in git. The "Doc filed. Now building
  the framework…" messages never flushed here (or happened on the other machine).
  Design fully recoverable from conversation; treated as design-stage, not code.

### Arachne — design state (NOT yet built)
- Epiphany (James): an army of math crawlers over formal libraries / databases /
  sequences / algorithms, emitting typed+provenanced edges into a shared fabric;
  fewest rules possible so novel organization can emerge.
- Aporia stand: **three rules, not zero** — every edge carries (1) provenance
  [enables crawler ablation], (2) operator-type not object-type [verbs over nouns],
  (3) a null [else it rediscovers the prime atmosphere]. Win condition: emergent
  partitions that (a) don't match human discipline boundaries, (b) survive single-
  crawler ablation, (c) survive degree-preserving graph null.
- **n=2 first, not an army.** Emergence must show at n=2 or it isn't emergence.
- ChatGPT verdict folded in: four products (Fabric / Void-map / Operator-ecology /
  Routing-substrate); "crawl the crawlers" meta-graph; first two crawlers =
  Proof-Dependency-Motif vs Statement/Type-Signature on mathlib4; minimal edge
  record schema; kill-ledger for edges.
- **Aporia adversarial correction (unexamined by the convergence):**
  - Convergence between ChatGPT and Aporia is a WARNING (gravity amplifier), not
    validation.
  - "super-additive at n=2 = emergence" is nearly automatic by set union; the real
    null must hold each crawler's MARGINALS fixed (degree+operator-matched random
    crawler A′,B′; compare A∪B surplus vs A′∪B′ surplus).
  - mathlib-first is right for the INSTRUMENT (machine-checkable) but likely wrong
    for the FINDING (mathlib is human-curated → table-of-contents gravity strongest
    there). Resolution: mathlib calibrates instrument; LMFDB tests finding
    (detrend primes first). Don't conflate "first landscape" with "where finding lives."
- **Local data confirmed crawlable:** mathlib4 cloned at
  `external_deps/mathlib4/Mathlib`; lmfdb lfunc_lfunctions 344GB, nf_fields 9.8GB,
  ec_curvedata 2GB, artin_reps 468MB; sympy/numpy/networkx installed; prometheus_math
  ~301 .py.
- **STATUS: Arachne not built. Foundational doc not (re-)filed on this machine.**
  Open item.

### Reasoning-ladder unification → reasoning-steering protocol
- James's move: each reasoning rung needs ≥1 gradient field to traverse, where
  directional failure-pointers point toward the well.
- Aporia formalization: the sharp (non-tautological) reading is that the failure
  field is **non-conservative**. Rigorous object = combinatorial Hodge / HodgeRank
  decomposition of the failure edge-flow on the state graph:
  `f = ∇φ (scalar diff) + δψ (curl/cyclic) + h (harmonic/H¹ holes)`.
  "Number of fields per rung" = local non-gradient rank.

### v0.2 written + committed (commit a90cb4d6)
- Filed `aporia/docs/reasoning_steering_protocol_v0.2.md`; v0.1 left immutable with a
  supersession pointer.
- Hypotheses (James's nested structure):
  - **H-R1** scalar-collapse falsifier (Stage 0, pure data): `non_gradient_mass =
    (‖δψ‖²+‖h‖²)/‖f‖²` beats the null battery.
  - **H-R1b** predictive lift — demoted to a *consequence*, not the primary test.
  - **H-R2** rung-rank, with the **LOCALIZATION FREEZE**: fixed graph-distance balls
    r∈{1,2,3}, two-of-three-radii criterion, curl-rank & harmonic-rank reported
    separately then summed, single-radius = `UNSTABLE_LOCALIZATION` (not evidence).
    Spectral localization rejected for v0.2 (too many knobs).
  - **H-R3** cross-protocol keystone: Stage-0 rung-rank predicts WHERE single-vector
    v_proj steering fails (rank-1 steerable by one contrast vector; rank-k needs k
    vectors / ordered sequences). Must beat baseline features.
  - **H-R4** training transfer, HARD-3-gated.
- **Guardrail (James):** non-conservativity is the NECESSARY condition / first
  structural falsifier, NOT "the whole game." Dies only if the basis collapses to
  scalar GLOBALLY, not when easy rungs are gradient-like.
- **The load-bearing distinction:** operator-induced vs state-induced curl. If curl
  dies under operator-label shuffle, the menu manufactured the basis (the H5-OEIS
  artifact); if it survives, the state landscape carries the structure.
- Null battery #1–8: operator-label shuffle, endpoint permutation, degree-preserving
  rewire, emitter-family holdout, synthetic no-cycle/no-void, planted-cycle,
  planted-hole, operator-menu artifact floor.
- **Stage 0 ordered controls-first:** 0a controls → `stage0_hodge_controls_report.json`
  BEFORE 0b H-R1 global → 0c H-R2 local (only after freeze + 0a pass) →
  `stage0_real_failure_results.json`. Prove the instrument sees nothing in
  no-structure data and recovers planted structure before touching the real ledger.
- **Bridge:** Arachne crawls → emits edge-flow; Hodge decomposes → rank/mass;
  steering tests → rank predicts steering failure. ONE pipeline. Per-edge `emitter`
  provenance is what makes the emitter-family-holdout null possible.

### Open forks / next moves (not yet decided or done)
- [ ] **Stage 0 decomposer** — build it, run synthetic controls #5–#8 FIRST, emit
  `stage0_hodge_controls_report.json`. Pure-data, HARD-3-clean, no ratification
  needed. Awaiting James's go.
- [ ] **Arachne** — not built; foundational doc not re-filed on this machine. Decide
  whether to rebuild here or recover from the other machine.
- [ ] Localization rule frozen in doc ✓ — but neighborhood/connected-component
  handling for harmonic at small radii still to validate empirically in 0a.
- [ ] Memory: localization-freeze / controls-first discipline not yet promoted to a
  `feedback_` memory (MEMORY.md over size limit; deferred pending trim).

---

## 2026-06-06 — Stage 0 build (TDD, self-paced loop)

**Env:** Python 3.11 (`...Programs\Python\Python311`) has the stack — numpy 2.2.6,
scipy 1.13.1, networkx 3.6.1, hypothesis 6.151.9, pytest 8.4.2. (The default
`python` / py3.12 do NOT have numpy — always use `py -3.11`.) Module lives at
`aporia/experiments/reasoning_steering/stage0/`.

### Iteration 1 — Hodge decomposer core ✓ (commit pending)
- Wrote 4-category tests first (`tests/test_hodge.py`), confirmed RED (ImportError),
  then implemented `hodge.py` to GREEN. **9/9 pass** (A:3 P:2 E:2 C:2).
- API: `hodge_decompose(G, flow) -> HodgeDecomposition` with
  gradient/curl/harmonic vectors + masses + non_gradient_mass + curl_rank +
  harmonic_rank. Canonical edge orientation = sorted pair; triangles = filled
  3-cliques; projections via least squares onto im(d0) and im(B2); harmonic =
  orthogonal residual.
- Authority fixtures (hand-computed, cited to HodgeRank / Jiang et al. 2011):
  filled triangle circulation = PURE CURL (curl_mass 1, curl_rank 1, harmonic_rank
  0); chordless 4-cycle circulation = PURE HARMONIC (harmonic_mass 1, harmonic_rank
  1); tree flow = PURE GRADIENT. This is exactly the curl-vs-harmonic distinction
  controls #6 (planted-cycle) and #7 (planted-hole) rely on.
- Property: Pythagorean mass partition + 3-way orthogonality (60 ex), gradient-of-
  potential ⇒ non_gradient_mass≈0 (40 ex). Composition: curl_rank+harmonic_rank ==
  |E|-|V|+components vs networkx (40 ex); triangle-free harmonic_rank ==
  len(cycle_basis) on a 4×4 grid.
- **Next (iter 2):** synthetic control generators — start with no-cycle/no-void
  (must read non_gradient_mass≈0) and planted-cycle (must read curl_mass>0 at the
  planted triangles).

### Iteration 2 — control generators #5 (no-cycle) + #6 (planted-cycle) ✓
- `controls.py`: `ControlGraph` dataclass (G, flow, kind, expected, seed,
  n_planted), `circulation_flow`, `no_cycle_graph(n,seed)`,
  `planted_cycle_graph(k,seed,with_backbone)`. Tests first → RED → GREEN, **7/7**
  (A:2 P:2 E:1 C:2). Full suite **16/16**.
- #5 no-cycle: random tree + gradient-of-potentials flow ⇒ non_gradient_mass≈0.
  Independent anchor: `nx.is_tree`/`is_forest`.
- #6 planted-cycle: k disjoint filled triangles each carrying a scaled circulation
  (PURE CURL), joined by a bridge backbone carrying gradient background (bridges are
  in no cycle ⇒ add no curl/harmonic). curl_rank==k, harmonic_rank==0, curl_mass>0.
  Independent anchor: networkx 3-clique count. **Composition test = protocol 0a**:
  decomposer recovers exactly the declared `expected`.
- **Next (iter 3):** #7 planted-hole (chordless cycles ⇒ harmonic_rank==#holes) +
  #8 operator-menu-artifact (random topology w/ operator labels ⇒ false-positive
  floor). Then iter 4 = §4 null battery.

### Iteration 3 — control #7 planted-hole ✓ (re-planned: #8 deferred to iter 4)
- On-the-fly adjustment: did #7 alone this cycle (clean harmonic-side parallel to
  #6); moved #8 operator-menu-artifact to iter 4, since it's the same
  operator-permutation family as the null battery and belongs with it.
- `planted_hole_graph(n_holes, hole_len, seed, with_backbone)` in `controls.py` +
  `test_controls_hole.py`. RED → GREEN, **4/4** (A:1 P:1 E:1 C:1). Full suite
  **20/20**.
- #7: k disjoint chordless cycles (len≥4, no fill) each carrying a scaled
  circulation (PURE HARMONIC), bridged by a gradient backbone (bridges are in no
  cycle ⇒ add no hole/triangle). curl_rank==0, harmonic_rank==k, harmonic_mass>0.
  Independent anchors: zero 3-cliques + first Betti number == k +
  harmonic_rank==len(nx.cycle_basis) (triangle-free).
- **The curl/harmonic instrument is now calibrated both ways:** triangle→curl
  (iter 2), chordless cycle→harmonic (iter 3), each recovered exactly across random
  configs. This is the §2 distinction the whole protocol rests on, now tested.
- **Next (iter 4):** §4 null battery (operator-label shuffle, endpoint permutation,
  degree-preserving rewire, emitter-family holdout) + control #8
  operator-menu-artifact (the operator-induced false-positive floor).

### Iteration 4 — null battery core + #8 operator-artifact ✓
- `controls.py`: `operator_artifact_graph(operator_counts, n_nodes, seed)` (#8) +
  new `edge_operators` field on `ControlGraph`. Random topology, edges labelled to
  match the operator multiset, flow = per-operator signature ⇒ operator structure
  with NO planted topology. The non_gradient_mass it reads = the operator-induced
  false-positive floor.
- `nulls.py`: `NullResult`, smoothed permutation `null_pvalue` =
  (#{null≥obs}+1)/(n+1), `degree_preserving_rewire` (double-edge-swap + flow-multiset
  reassign), `operator_label_shuffle` (permute labels, rebuild flow from signature),
  `run_null` orchestrator. `test_nulls.py` RED→GREEN, **9/9** (A:2 P:3 E:1 C:3).
  Full suite **29/29**.
- **THE central anti-artifact test passes:** planted-cycle (real curl) BEATS the
  rewire null (p<0.1); no-cycle does NOT (p>0.1); operator-artifact does NOT beat
  the label-shuffle null (p>0.1, the floor). This is the operator-vs-state-curl
  discriminator working — the protocol's load-bearing guard.
- **Done this cycle:** 2 of the 4 named §4 nulls (degree-preserving rewire,
  operator-label shuffle) + #8.
- **Next (iter 5):** remaining 2 nulls — endpoint-permutation (permute endpoints
  keeping operator multiset) + emitter-family-holdout (drop one operator family,
  does mass survive its absence — the beyond-generators clause). Then iter 6 = H-R2
  localization, iter 7 = the 0a runner.

### Iteration 5 — remaining 2 §4 nulls ✓ (null battery complete)
- `nulls.py`: `endpoint_permutation` (keep operator multiset, randomise vertex
  pairs), `emitter_family_holdout` (drop one family's edges), `run_emitter_holdout`
  (leave-one-family-out non_gradient_mass map), + `endpoint_permutation` branch in
  `run_null`. `test_nulls_extra.py` RED→GREEN, **7/7** (A:2 P:2 E:1 C:2). Full
  suite **36/36**.
- emitter-holdout composition is the beyond-generators clause working on a hand
  example: a triangle whose 3 curl edges are family "C" + a bridge family "B" —
  `run_emitter_holdout` reports C-removal collapses non_gradient_mass to 0 (C was
  load-bearing) while B-removal leaves pure curl (1.0). If a single emitter family's
  removal collapses the signal, that family manufactured it.
- **All 4 §4 nulls done:** degree-preserving rewire, operator-label shuffle,
  endpoint-permutation, emitter-family-holdout. Plus all 4 controls (#5–#8) and the
  decomposer. The anti-artifact battery is complete.
- **Next (iter 6):** H-R2 localization — graph-distance balls B_r(w) for r∈{1,2,3},
  separate curl-rank & harmonic-rank per ball, two-of-three-radii criterion,
  UNSTABLE_LOCALIZATION label. Then iter 7 = 0a runner →
  stage0_hodge_controls_report.json.

### Iteration 6 — H-R2 localization (the freeze) ✓
- `localization.py`: `ball_nodes`, `local_decompose` (induced subgraph B_r(w) →
  local Hodge ranks), `localized_rank` (the freeze) returning `LocalRank`
  (per-radius curl/harmonic/mass + declared values + status). `test_localization.py`
  RED→GREEN, **7/7** (A:3 P:1 E:1 C:2). Full suite **43/43**.
- The freeze, exactly as preregistered: fixed graph-distance balls r∈{1,2,3}, all
  three reported, curl-rank & harmonic-rank separate, a nonzero rank declarable only
  if the same value appears at two adjacent radii with mass>floor at both; else
  `UNSTABLE_LOCALIZATION`. Spectral localization rejected.
- **The freeze does real work (the load-bearing demonstration):** a chordless
  4-cycle's hole closes inside the r=2 ball and persists at r=3 → STABLE harmonic 1;
  a 6-cycle's hole only closes at r=3 (single radius) → **UNSTABLE_LOCALIZATION**,
  even though the GLOBAL decomposition sees harmonic_rank 1. Localization is stricter
  than global, on purpose — this is the artifact trap (neighborhood-radius DoF)
  being closed, tested directly.
- **Next (iter 7, final):** the 0a runner — assemble decomposer + 4 controls + 4
  nulls + localization into a report that proves the instrument (sees nothing in
  no-structure data, recovers planted structure, surfaces the operator floor) and
  emits `stage0_hodge_controls_report.json`. This is the protocol's
  "instrument-proven-before-real-data" gate.

### Iteration 7 (FINAL) — 0a runner + gate artifact ✓ STAGE 0 COMPLETE
- `runner.py`: `run_controls_0a(seed, n_null_samples)` + `write_report`.
  `test_runner.py` RED→GREEN, **4/4** (A:1 P:1 E:1 C:1). Full suite **47/47**.
- **Gate artifact generated — `stage0_hodge_controls_report.json`, all_passed=True**
  (n_null_samples=500, seed=0). All 6 checks PASS:
  - #5 no-cycle: non_gradient_mass = 2.4e-31 (~0) — instrument sees nothing.
  - #6 planted-cycle: curl_rank 4, harmonic 0, curl_mass 0.83 — recovers curl.
  - #7 planted-hole: harmonic_rank 3, curl 0, harmonic_mass 0.98 — recovers harmonic.
  - #8 operator-artifact floor: label-shuffle p=0.35, endpoint-perm p=0.39 (both
    >0.1) — does NOT beat its null; the operator floor holds.
  - planted-cycle beats rewire null: observed 0.83 vs null-mean 0.25, p=0.004 (<0.1)
    — real structure clears the null.
  - localization STABLE, curl_rank 1 on a planted well.
- **The protocol's "instrument proven before real data" gate (§5 step 0a) is met.**
  Stage 0b (H-R1 global on real failure data) and 0c (H-R2 local rank) are now
  unblocked — but per §5 they touch the real kill ledger, which is the next decision
  point for James, not an autonomous step.

### STAGE 0 SUMMARY (7 iterations, all TDD, 47 tests green)
- `hodge.py` — combinatorial Hodge decomposer (f = grad+curl+harmonic, masses, ranks).
- `controls.py` — 4 synthetic controls (#5 no-cycle, #6 planted-cycle, #7 planted-hole,
  #8 operator-artifact).
- `nulls.py` — §4 null battery (degree-preserving rewire, operator-label shuffle,
  endpoint-permutation, emitter-family-holdout) + p-value machinery.
- `localization.py` — H-R2 localization with the preregistered freeze.
- `runner.py` — 0a validation harness + `stage0_hodge_controls_report.json`.
- Commits: a5619bac, 774ab6f5, a1e7d500, 73e5ad49, d452c1d1, ad4745aa, + iter 7.
- **Loop stopped after iteration 7 (planned end).**

---

## 2026-06-06 — Stage 0a STATUS marker (James)

```
STATUS:            PASSED
SCOPE:             synthetic controls only
CLAIM ALLOWED:     the decomposer is instrument-valid under preregistered controls
CLAIM NOT ALLOWED: the real failure catalog is non-conservative
NEXT GATE:         Stage 0b real-catalog H-R1 (global only)
```

Two load-bearing outcomes (not just "it passes"):
1. Operator-vs-state curl discriminator PASSED — the existential guard against
   "operator-menu archaeology." Proves the instrument can tell planted state-structure
   from operator-artifact structure *under the synthetic regime* (NOT that the real
   ledger has state-structure).
2. Localization freeze REJECTED a seductive false positive — global Hodge accepts the
   6-cycle, H-R2 rejects it UNSTABLE_LOCALIZATION. The local-rank gate is not
   decorative; it actively blocks overclaiming.

### Frozen next sequence (James)
- 0a   synthetic controls .................. PASSED
- 0b-pre  freeze real-ledger graph mapping .. NEXT (author + commit, ratify before run)
- 0b   global H-R1 on real catalog .......... RUN after ratification
- 0b-audit  null battery + sensitivity ...... RUN
- 0c   H-R2 local rank around wells ......... ONLY IF 0b beats null
- 1    H-R3 steering prediction ............. ONLY IF 0c yields stable ranks
The "only if" is binding: if H-R1 fails globally, H-R2 is exploratory-labeled only,
never fishing for local exceptions. Publish 0b even if NULL.

### 0b discipline (austere, global)
- NO well-localization, NO rung-rank, NO steering yet. One question: does the real
  failure-flow contain non-gradient mass beyond the null battery?
- Artifact: `stage0b_real_hodge_global_report.json` (verdict
  BEATS_NULL|NULL|INVALID|INSUFFICIENT_DATA).
- Graph construction is the main remaining researcher DoF → frozen in
  `stage0b_graph_construction_freeze.md` BEFORE the ledger is touched. Schema
  inspection is allowed to author the freeze; outcome inspection is not.

### 0b-pre catalog recon (schema only — NO decomposition run on real data)
Surveyed real catalogs to author the freeze. **Finding: no existing catalog emits a
well-posed `(state, move, damage-change edge-flow)`.** The crux:
- **Charon kill ledgers** (erebos/pollux/stygian/hephaestus, ~200–370 records each)
  are the only substantial source. Structural mismatch with H-R1's needs:
  - lineage (the graph EDGES) lives in raw per-agent ledgers — erebos 216/233 have
    `parent_record_id` (93%) — BUT those are uniformly `verdict=UNVERIFIED`, single
    `generator_id`.
  - verdicts/outcomes (PROMOTED/REJECTED) live in the *enriched* files — BUT those
    have ZERO lineage (no parents).
  - emitter-family variation (needed for the emitter-holdout null) requires POOLING
    across the 4 agents.
  - No canonical damage scalar → the antisymmetric edge-flow must be invented, and
    that choice could manufacture/kill the H-R1 signal (the squishy-H-R1 risk).
- **mutation_registry.py** is the purest directional-pointer design (`delta_per_axis`
  is a flow vector) but NO data file exists, and it's a vector field in health-space,
  not a graph.
- **failure-signal §1 schema** (purpose-built: inputs/move/motif/outcome) — no
  dataset persisted (H5a OEIS MVP verdict was NULL).
- No repair-graph / RESOLUTION-edge dataset exists.
**Consequence:** this is exactly James's anticipated outcome ("the current
catalog/operators are not yet producing structural failure flow") — surfaced cheaply
at the MAPPING stage, before any misleading run. Fork taken to James (catalog/flow
choice is a non-recoverable research commitment). No freeze authored yet; it depends
on the fork.

### DECISION (James 2026-06-06): Substrate emit-change first (primary) + non-promotable sidecar
- **Primary:** the substrate must emit `(state_before, operator/move, state_after,
  Δdamage)` per applied move → 0b well-posed BY CONSTRUCTION, not reverse-engineered.
- **Sidecar:** exploratory pooled-ledger probe, clearly non-promotable, parallel.
- **Avoid:** pooled-ledger graph as the REAL preregistered H-R1 (bakes a frozen
  damage scalar chosen after-the-fact into the gate → epistemically soft).

### SIDECAR FEASIBILITY: INFEASIBLE — dropped
- The erebos raw lineage records (216/233 with parents) have ZERO numeric top-level
  fields and an empty/numeric-free `kill_vector`. There is no damage magnitude on any
  edge. Enriched records (which carry verdicts) use a 32-hex id vs the raw 64-hex id →
  cannot be joined onto the lineage to supply a node scalar.
- A sidecar would decompose an INVENTED CONSTANT, not data — uninformative even as
  scouting. **Not built.** This is the strongest confirmation that the emit-change is
  REQUIRED, not optional: nothing in the substrate ever recorded a Δdamage.

### NEXT: emit-schema freeze (primary path)
Author `stage0b_emit_schema_freeze.md`, present for ratification (the Δdamage metric
is the load-bearing decision), THEN build the emitter via TDD, generate data, run 0b.

### emit-schema freeze RATIFIED (James 2026-06-06) + feasibility confirmed
- **Damage metric:** EvidenceField Axis 2 (battery-survival depth), single axis,
  `damage = −(falsifiers passed before kill)`, `flow = Δdamage`. Axis 1 (margin) =
  preregistered SECONDARY robustness emitter. Degeneracy guard: `INVALID_SPARSE_SIGNAL`
  if >80% edges Δdamage=0 or <20 nonzero-flow edges; no post-hoc metric substitution.
- **Feasibility CONFIRMED:** scorer chain exists — `DiscoveryPipeline.process_candidate`
  → `kill_vector_from_pipeline_output` → `build_evidence_field(...).battery_survival_depth.n_passed`
  → `damage = −n_passed`. Polynomial-domain.
- **Stands (no-DoF):** corpus = Mossinghoff/Mahler polynomials (whole declared slice);
  operator set = ALL registered polynomial operators (no cherry-pick — nulls test
  against the menu).
- **NEXT:** emitter TDD build loop. Iteration 1 = the Axis-2 damage scorer with an
  authority test on a known polynomial (the critical-path feasibility resolver in
  code). Then corpus loader → operator application → emitter → graph builder → 0b
  runner (reuses Stage 0a's validated decomposer + nulls) → stage0b report. Global
  H-R1 only; publish even if NULL/INVALID_SPARSE_SIGNAL.

## 2026-06-06 — Stage 0b emitter build (TDD loop)

### Iteration 1 — Axis-2 damage scorer ✓ (but PERFORMANCE FLAG)
- Feasibility smoke confirmed the chain: Lehmer's poly → damage −9 (n_passed 9/12:
  out_of_band, reciprocity, irreducibility, LMFDB, arXiv, F1/F6/F9/F11 pass; the 3
  catalog-presence checks fail); out-of-band → damage 0.
- `stage0b/damage.py`: `Axis2DamageScorer` (builds DiscoveryPipeline once, reuses) +
  `Axis2Damage` result. `test_damage.py` **6/6 GREEN** (A:2 P:2 E:1 C:1).
- **⚠ PERFORMANCE FLAG:** test run took **570s (9.5 min)** for ~16 scores. At this
  cost a full corpus×operators sweep (iter 4) is intractable. `catalog:LMFDB` /
  `catalog:arXiv` in the falsifier set suggests possible network calls → also a
  REPRODUCIBILITY risk (network-dependent damage). MUST diagnose construction-cost vs
  per-score-cost and the catalog-network question BEFORE the emitter sweep (the freeze
  "if scoring can't be made to work cleanly, stop and report" clause). Diagnosing next.

### PERFORMANCE DIAGNOSIS → LOOP STOPPED (stop-and-report per freeze)
- Timing: import 75s (one-time), construct scorer **0s**, per in-band score **~55s**
  (out-of-band scores are ~free, phase-0 kill). Cost is PER-SCORE, in the falsifier
  battery (PARI irreducibility/Mahler + F1 permutation-null + F6/F9/F11 + local
  catalog lookups).
- **Reproducibility OK:** `catalog_consistency.py` has NO network calls — arXiv/LMFDB
  catalogs are LOCAL. Only caveat: F1 permutation-null uses RNG → need a FIXED battery
  seed for deterministic `damage` (freeze addendum).
- **Not intractable, but a resource decision.** A sweep of N in-band states × M
  operators ≈ N(1+M) scores; many operator-images fall out-of-band (cheap). Estimate
  N=50, M=8, ~half images in-band → ~250 expensive scores × 55s ≈ **3.8 hr serial**,
  or **~30 min with 8× multiprocessing** (parallelism is a legit engineering fix — it
  does NOT change the metric).
- **STOPPED the loop** (no ScheduleWakeup) per the freeze's explicit stop-and-report
  clause: the path forward (parallelize + corpus size + battery seed, vs optimize, vs
  re-ratify a cheaper metric) is James's decision. The damage scorer itself is correct
  and committed (629737af).

### Iteration 2 (corpus) → DESIGN CHECKPOINT, loop STOPPED again
Reconned the corpus before building. Three compounding findings make the experiment
as-specified ill-posed; stopped to bring James a design decision rather than burn the
sweep on a foregone NULL:
1. **Corpus tiny:** tier-0 palindromic generator yields 0 in-band in 3000 candidates.
   The canonical `prometheus_math.databases.mahler.MAHLER_TABLE` (8625 entries, has
   coeffs+M) has only **21 in-band** (1.001<M<1.18). So the corpus = 21 states, not 50
   (cap doesn't bind). In-band window is genuinely sparse (Lehmer 1.176 is near top).
2. **One-step moves are cycle-free (the killer):** "apply every operator to every
   corpus state" once = corpus→images = a FOREST. Hodge non_gradient_mass ≡ 0 on a
   forest BY CONSTRUCTION → H-R1 trivially NULL for a graph-topology reason, not a
   scientific one. Non-conservativity cannot exist without cycles. The move-graph MUST
   have cycles (paths that reconverge) for H-R1 to be a real test.
3. **Operator set ill-defined:** no clean registry of coeffs→coeffs move-functions;
   `operator_class` is claim metadata. The nulls test against the operator menu, so
   the menu must be a real, enumerable set — currently absent for this domain.
**This vindicates the disciplined approach:** building the real emitter surfaced that
the substrate's natural failure-flow over the polynomial domain is structurally
cycle-free at one step — a concrete "where the next substrate must change" finding,
caught before any expensive run. Design fork taken to James (loop STOPPED, no wakeup).

### ⛔ FUNDAMENTAL FINDING: the 0b flow is conservative BY CONSTRUCTION
While specifying the lattice redesign + continuous metric (James chose both), a deeper
flaw surfaced that SUPERSEDES corpus/operator/metric:
- The freeze defines `flow(before→after) = damage(after) − damage(before)`.
- If `damage` is a deterministic node function D (which fixed-seed determinism, ratified
  for reproducibility, GUARANTEES), then `f(i,j) = D(j) − D(i)` = the discrete gradient
  (coboundary) of D.
- In combinatorial Hodge theory a flow equal to a node-potential coboundary IS the pure
  gradient component: **curl ≡ 0, harmonic ≡ 0, non_gradient_mass ≡ 0 IDENTICALLY** —
  for ANY graph/operators/metric/corpus.
- ∴ H-R1 (non-conservativity) is **unfalsifiable-toward-positive**: it can only ever
  return NULL/conservative. The lattice, the 21 states, Axis 1 vs Axis 2 — all moot.
- The determinism we required for reproducibility is precisely what forces conservativity.
**Honest miss:** this is elementary and should have been caught at the emit-schema
freeze; it wasn't. Caught by the disciplined build BEFORE any expensive sweep.
**The fix (reconceptualization):** the edge flow must be a MOVE-INTRINSIC measurement
that is NOT reducible to a node-potential difference — i.e., a direct pairwise
comparison `compare(a,b)` elicited per-edge that CAN be inconsistent around a cycle.
This is literally HodgeRank's original setting (pairwise comparison data whose curl
measures inconsistency with any global ranking). Candidates: move-cost/resistance
(effort to apply the operator, not endpoint difference); operator-induced directional
derivative (feedback_kill_space_vector_field: "operators induce directional
derivatives") measured locally without integrating to a global potential; or direct
head-to-head battery comparison per edge. Reported to James; 0b build HALTED pending
reconceptualization of the flow.

### v0.3 RELATIONAL CORRECTION (James chose: relational flow + revise protocol + rebuild)
Filed `reasoning_steering_protocol_v0.3_relational_correction.md` (supersedes v0.2
§1–§2; v0.2 pointer added). The fix + a clarification that supersedes the lattice:
- **Relational flow:** `flow(a,b) = Σ_k sign(margin_k(b) − margin_k(a))` over the
  battery's per-falsifier margins (Condorcet; the `sign` non-linearity is what allows
  curl — linear aggregation collapses to a gradient). Non-transitivity = non-scalar
  structure = H-R1's real content.
- **Comparison-graph supersedes the lattice/operators:** a pairwise-comparison flow
  lives on the COMPLETE graph of states, intrinsically cyclic → no operators, no
  lattice, no sweep. Nodes = 21 in-band MAHLER_TABLE states, scored ONCE for their
  per-falsifier margin vector (~21×55s ≈ 19 min, cached). Dissolves the
  forest/operator-registry/corpus-sparsity blockers at once.
- **H-R1 sharpened:** do pairwise comparisons of reasoning states admit a consistent
  global difficulty ranking (gradient) or are they non-transitive (curl/harmonic) —
  i.e. "ladder is a basis not a scalar," correctly operationalized.
- **Nulls adapted:** falsifier-column-shuffle (operator-label-shuffle analog),
  sign-permutation, falsifier-family-holdout, degree-preserving rewire. Stage-0a
  instrument UNCHANGED (it was correct; only the flow fed to it was mis-defined).
- **NEXT (rebuild loop):** (1) extend the scorer to return the per-falsifier margin
  VECTOR (not just n_passed); (2) score the 21 in-band states once, cache; (3)
  comparison-flow builder (complete graph, sign-margin); (4) run Stage-0a decomposer +
  adapted nulls → `stage0b_relational_hodge_report.json` (BEATS_NULL|NULL|INVALID).

## 2026-06-07 — Stage 0b relational build (TDD loop)
- **iter 1 margin vector ✓** `margins_from_kill_vector` + `Axis2DamageScorer.margin_vector`
  → {falsifier: margin} from KillVector components (None/NaN dropped). 5/5 (incl. real
  Lehmer pipeline test, 120s). A:2 P:1 E:1 C:1.
- **iter 2 in-band corpus loader ✓** `corpus.load_in_band_states` → in-band (1.001,1.18)
  slice of MAHLER_TABLE, deterministic (sorted by M,coeffs), Lehmer included. 4/4.
  A:1 P:1 E:1 C:1.
- **iter 4 relational flow builder ✓** `flow.relational_flow` → complete graph +
  `flow(i,j)=Σ_k sign(margin_k(j)−margin_k(i))`. 5/5. A:2 P:1 E:1 C:1.
  - **KEYSTONE authority test passes:** a Condorcet 3-cycle decomposes to PURE CURL
    (non_gradient_mass 1.0) — the relational flow CAN be non-conservative, the whole
    point of v0.3.
  - **Build finding — saturation-curl baseline:** `sign` isn't path-additive, so even a
    transitive ordering leaves ~0.11 non_gradient_mass (gradient-dominated). ⇒ H-R1
    verdict must be **BEATS NULL**, never non_gradient_mass>0 (the null carries the
    same saturation floor). Folded into v0.3 §5. The TDD test caught a wrong premise
    and sharpened the protocol.
- **iter 3 score-and-cache ✓** `cache.score_states/write_cache/load_cache` (mock-scorer
  tested, 4/4); real ~21-state batch via `__main__` running in background.
- **iter 5 relational nulls ✓** `relational_nulls`: falsifier-column-shuffle,
  sign-permutation, falsifier-family-holdout (+run_relational_null/holdout). 5/5.
  - **Authority:** column-shuffle null SEPARATES Condorcet (observed 1.0, far above
    null mean) from transitive (saturation floor) — the null isolates genuine
    non-transitivity. (3-state toy underpowered for hard p<0.05 → assert separation;
    hard threshold is for the real ≥21-state run, matching the ≥8 guard.)
- **iter 6 runner ✓** `runner.run_h_r1` → verdict BEATS_NULL|NULL|INVALID over the
  relational nulls + family-holdout, degeneracy guard, emits
  stage0b_relational_hodge_report.json. 4/4.
- **Two build corrections (TDD caught both):**
  1. Degeneracy guard must be ALL-ZERO flow, not low-variance — a CONSTANT flow has
     curl (not degenerate). Fixed to max|flow|<eps.
  2. Degree-preserving rewire is INAPPLICABLE to a complete graph (no non-edges to
     swap) → dropped from the relational null set (column-shuffle + sign-permutation
     remain); v0.3 §5 corrected.
- **NEXT:** real cache batch completes → run `runner` on it → the actual H-R1 verdict.

### ⭐ STAGE 0b H-R1 VERDICT: NULL (the first hard H-R1 result)
Cache: 21 in-band states scored in 1242s (~20.7 min). Runner on the real cache →
`stage0b_relational_hodge_report.json`:
- **verdict = NULL.** Observed: gradient_mass **0.799**, curl_mass **0.201**,
  harmonic_mass ~0 (1e-30), non_gradient_mass **0.201**.
- **It does not beat either null** — in fact it sits BELOW them:
  - falsifier_column_shuffle: null_mean **0.251** > observed 0.201, **p=0.818**.
  - sign_permutation: null_mean **0.905** ≫ observed, **p=1.0**.
- falsifier-family-holdout: removing any single family leaves ~0.16–0.24 (≈ full
  0.201) — no single falsifier is load-bearing.
**Interpretation (scoped):** over the 21 in-band Mahler/Lehmer polynomials, compared
pairwise across the falsifier battery, the failure-comparison flow is GRADIENT-
DOMINATED and its modest curl is LESS than random falsifier-shuffling produces ⇒ NO
genuine non-transitivity. The pairwise comparisons of these reasoning states ARE
consistent with a single global scalar difficulty ranking. **H-R1 fails on this
substrate/corpus/metric: the failure landscape here is conservative (scalar difficulty
wins).** This is the clean killable negative the protocol was built to produce.
**Scope / caveats:** one narrow domain (in-band Mahler polynomials), one comparison
metric (battery falsifiers), n=21 (the in-band window is sparse). NULL here does NOT
refute H-R1 universally — it says THIS instantiation is conservative; other
domains/measurements remain open. The column-shuffle null is tightly estimated
(std 0.054), so the verdict is well-powered for its scope.
**Arc value:** the disciplined build caught a fatal flaw (scalar Δdamage conservative
by construction) BEFORE any expensive run, reformulated to a relational (HodgeRank)
flow, and produced a real verdict — all without ever overclaiming. Stage-0a instrument
reused unchanged throughout. **Loop STOPPED (verdict committed).**

### EXPANSION (James: "both in order — diagnostic then new domain")
**Diagnostic ran FREE on the cache (no re-score) and reclassifies the NULL.** Of the 8
falsifiers across the 21 in-band states: **5 are CONSTANT** (F9, catalog:Mossinghoff,
catalog:lehmer_literature, out_of_band, catalog:OEIS), only **3 vary** (F6_base_rate
5 values; irreducibility, reciprocity binary). Full-presence pairwise corr mean 0.26.
⇒ The corpus is too HOMOGENEOUS: the 21 in-band Mahler polynomials are so similar the
failure criteria barely move, so there is almost nothing to be non-transitive about.
**Reclassification:** the Mahler H-R1 NULL is **CORPUS-LIMITED (impoverished criteria),
NOT** "scalar difficulty wins." Swapping heterogeneous criteria over the SAME 21 states
would not help — the corpus is the limiter. So the diagnostic says: **skip ahead to the
new domain.** (Saved a ~20-min re-score by checking the cache first.)
**Pre-registered for the new domain (avoid post-hoc tuning):** add a CRITERIA-ADEQUACY
guard BEFORE running — require ≥ K criteria each with ≥2 distinct values across states
(K frozen ahead). The Mahler run would have tripped it (only 3 vary, 2 binary).
**NEXT:** elliptic curves (local LMFDB ec_curvedata) — heterogeneous objects with many
trading-off arithmetic invariants (rank, conductor, regulator, torsion, Tamagawa,
analytic-sha), and a large non-sparse corpus. Recon the EC data format/accessibility
first, then build the EC scorer + corpus, reuse the relational pipeline + nulls + runner.

### EXPANSION recon + build
- ec_curvedata NOT on this machine (only `_counts.json`). Used `g2c_curves.json`
  (66158 genus-2 curves, 13 numeric invariants) instead — RICHER (arithmetic-hardness:
  analytic_rank/mw_rank/analytic_sha/two_selmer_rank + structural: cond/abs_disc/
  torsion/tamagawa/num_rat_pts). Criteria = all numeric fields except row id (no
  cherry-pick); Condorcet sign-flow is scale-invariant (no normalization).
- `g2c_corpus.load_g2c_states` (stratified deterministic sample) + criteria-adequacy
  guard (MIN_VARYING_CRITERIA=3, frozen before the run). 8/8 tests.
- **Hodge OOM fix:** `_incidence_b2` used nx.enumerate_all_cliques (exponential on
  dense graphs; K30 → ~2^30 → MemoryError). Replaced with direct edge-common-neighbour
  triangle enumeration, behaviour-preserving (61/61 green), scalable. Latent Stage-0a
  bug surfaced by the K30 run.

### ⭐⭐ GENUS-2 H-R1 VERDICT: NULL — and this one is a FAIR, well-powered test
`stage0b_g2c_relational_report.json`: 30 curves, **n_varying_criteria = 13** (all
criteria vary — passed the adequacy guard that Mahler would have failed):
- gradient_mass **0.829**, curl_mass **0.171**, harmonic_mass **0.000**, non_grad 0.171.
- falsifier_column_shuffle: null_mean **0.164** (≈ observed 0.171), **p=0.355** — the
  observed curl is AT the saturation baseline, not above it.
- sign_permutation: null_mean 0.933, p=1.0.
**Interpretation (calibrated):** over genus-2 curves compared across 13 heterogeneous,
genuinely-trading-off invariants, the comparison flow is GRADIENT-DOMINATED and its
curl equals what random column-shuffling produces ⇒ NO non-transitivity beyond
saturation. The "difficulty/complexity" ordering of these curves IS consistent with a
single global scalar ranking. **H-R1 NULL on a fair test.** Unlike the Mahler NULL
(corpus-limited), this is well-powered: 13 varying criteria, 30 states, guard passed.
**Two substrates now point the same way:** where the test is fair (g2c), the
failure/difficulty landscape is CONSERVATIVE (scalar difficulty wins). H-R1
(non-conservativity / "ladder is a basis") is NOT supported on the tested substrates.
**Scope/caveat:** invariants-as-criteria (not a failure-battery), n=30, two
object-domains. A plausible deeper reading: arithmetic invariants are coupled BY
THEOREMS (BSD ties rank/sha/regulator), so mathematics itself may suppress
non-transitivity → consistent scalar ordering. Does NOT prove H-R1 false universally,
but it's a real, well-powered negative on fair ground.

### OPTION 3 (James): pivot to the TRUE test — relational FAILURE data
The real H-R1 is a reasoning claim: do per-move pairwise comparisons of reasoning
states, from MULTIPLE INDEPENDENT failure-detectors that can DISAGREE, exhibit
non-transitivity? Recon for a ready-made source: **none exists.** Kill ledgers thin/
single-agent-per-file; learner corpus is categorical (verdict/outcome_class/
kill_signature, NO numeric scores); no PRM/Walk-Z score files (heads are checkpoints,
not score dumps). ⇒ Option 3 = GENERATE relational failure data. The load-bearing
decision is the EVALUATOR SET — it must be genuinely independent / able to disagree
(the g2c NULL came from theorem-COUPLED invariants that can't). Fork to James.
Note: substrate's own lead (feedback_no_naive_score_combination: Walk-Z combined <
random; PRM-alone best) says multiple reasoning heads DO disagree — the strongest prior
for where curl might finally appear.

### Panel ("cycle through all evaluator-sources and score them" — James)
Feasibility recon of the 4 arms:
- **A multi-agent verdicts: UNDERPOWERED, dropped.** Only erebos (16 problems) + stygian
  (42) carry problem_ids; pollux has none. Shared by both = 15, but that's only **2**
  evaluators — Condorcet non-transitivity needs **≥3**. 2 evaluators can't cycle.
  Verdicts thin (mostly UNVERIFIED).
- **B orthogonal heuristic scorers: buildable, no inference,** but needs a real
  reasoning-state corpus + genuinely-orthogonal evaluators to be constructed (risk:
  correlation → NULL, the g2c failure mode).
- **C independent LLM judges + D PRM/Walk-Z heads: the decisive arms** (≥3 genuinely
  independent evaluators, known to disagree) — both need MODEL INFERENCE (VRAM ≤3-4B
  local / Apollo-Rhea owned / frontier), best as Rhea-scripted batches
  (feedback_rhea_scripts).
**Gate:** the real test reduces to C/D, which need model access. Fork to James on
resourcing. Panel harness (run_h_r1 across arms, tabulate verdicts) to be built once
≥1 decisive arm's data exists.

### Arm B (James picked) — intended data is UNPOPULATED; no-inference path blocked
Checked the kill-ledger quality dimensions (the orthogonal lenses): novelty_estimate /
diversity_score / info_density / training_weight are **absent across all ledgers**;
precision_dps constant. The substrate has rich SCHEMAS but sparse/categorical DATA.
**Deepest finding of the arc:** the relational reasoning-failure H-R1 cannot currently
be tested without model inference — the only genuinely-independent evaluators available
are models (deferred), and existing data lacks ≥3 varying, uncoupled reasoning-quality
dimensions. To test whether reasoning-difficulty is non-scalar, the substrate must EMIT
multi-evaluator reasoning-quality data — a concrete "where the substrate must change."
**One viable no-inference arm B remains, but it's a BUILD, not existing data:**
method-utility — states = problems, criteria = per-ALGORITHM performance (genuinely
different solvers disagree on which problems are hard → potential non-transitivity;
the method-utility gradient of feedback_gradient_synthesis). Needs a problem set +
≥3 diverse solvers. Fork to James: build method-utility arm B, or accept the inference
gate and resource C/D.

### Signal pre-screen (James: "what increases probability of signal?") — + a KEY correction
Built `prescreen.signal_screen` to gate expensive H-R1 runs. First built it on PAIRWISE
correlation (the "decorrelation is the lever" strategy). **Validating it disproved that
strategy:** the g2c criteria have min pairwise Spearman **-0.80 and 34 anti-correlated
pairs**, yet H-R1 was NULL. So **pairwise anti-correlation does NOT predict
non-transitivity** — two evaluators trading off is still WEIGHTABLE (a scalar combination
orders the states). Curl needs CYCLIC, non-weightable inconsistency (a>b>c>a) among ≥3
evaluators, which pairwise stats cannot see.
**Corrected screen** = a FAST curl measure (observed non_gradient_mass + a small
column-shuffle null, ~10x cheaper than the full run); pairwise correlation kept as a
REPORTED diagnostic, explicitly NOT the gate. 5/5 tests incl. the centerpiece
(anti-correlated-but-weightable → FAIL_NO_CURL despite min_corr<-0.5).
**Validated retroactively:** the corrected screen predicts BOTH known NULLs —
MAHLER FAIL_NO_CURL (obs 0.201 < null 0.249, p=0.79); G2C FAIL_NO_CURL (obs 0.171 vs
null 0.155, p=0.247) despite its 34 anti-correlated pairs.
**Corrected answer to "what increases P(signal)":** NOT pairwise decorrelation. The
lever is NON-WEIGHTABLE CYCLIC disagreement — evaluators whose conflicts no scalar
weighting can reconcile. Contested-state sampling, more evaluators/states (more triples
→ more cycle chances), and trade-off-rich REASONING domains still help, but the gate is
the fast curl screen, not correlation. Substrate-emit implication unchanged but sharper:
emit multi-evaluator data and gate it with the fast curl screen, hunting cyclic (not
merely anti-correlated) disagreement.
