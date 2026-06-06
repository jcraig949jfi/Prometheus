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
