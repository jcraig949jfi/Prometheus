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
