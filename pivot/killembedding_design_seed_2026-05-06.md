# KillEmbedding — Design Seed (K(c) Schema + Training Protocol)

**Date:** 2026-05-06
**Status:** Design seed for v2.2 sprint Tier-2 implementation. Awaits cross-review by Charon + Ergon + frontier models before code.
**Author:** Aporia
**Predecessor:** ChatGPT design seed in conversation 2026-05-06; absorbed into Techne handoff at `roles/Techne/APORIA_HANDOFF_2026-05-06_external_review_synthesis.md`; approved by Techne at `roles/Techne/RESPONSE_TO_APORIA_HANDOFF_2026-05-06.md` Decision 1 (YES with single-domain A149 prototype + commit-blocking synthetic-null guard, slot Day 13-17 of joint sprint).
**Time-sensitivity:** P5 NearMissCorpus emission stabilized at v2.3 commit `d17a2ff8`. Schema audit confirmed P5 stub already carries KillEmbedding inputs (operator_class, falsifier_ids, margins, neighbors_in_chart). KillEmbedding training can proceed on `emit_from_substrate` output without further P5 schema changes.

## Purpose

Turn the substrate's existing kill data from diagnostic-grade structured records into a navigable geometric space. Each killed candidate maps to a low-dimensional vector where:

- distance reflects structural similarity of failure
- nearby points fail for similar reasons
- direction = "reducing a specific class of falsification pressure"
- clusters near PROMOTE ≈ "almost viable mathematical structure"

Trained via metric learning (contrastive + triplet loss) using the substrate's existing P5 NearMissCorpus emission as training pairs. Replaces ad-hoc 6-axis MAP-Elites descriptor with learned cluster geometry. Lifts kill_vector_navigator coverage from current 2/16 region cells toward ≥12/16 by giving the navigator a continuous coordinate system rather than discrete cell IDs.

## What this seed commits to (and what it doesn't)

**Commits to:**
- The K(c) schema below as the canonical input format for KillEmbedding training
- Single-domain A149 prototype as the first build target (per Techne Decision 1)
- Commit-blocking synthetic-null guard as the validity discipline (per Techne Decision 1)
- Triplet + contrastive loss as the training objective
- Cluster-based MAP-Elites descriptor as the consumption surface

**Does NOT commit to:**
- Cross-domain training before Pre-Tier-0 0b telemetry instrumentation lands across all 6 envs
- Specific embedding dimensionality d (range 8–32; pick by elbow on validation)
- Specific neural architecture (start small — 2-layer MLP with skip connection; only escalate if simpler model underfits)
- Replacing the kill_vector_navigator's categorical mode (keep both modes; navigator picks margin mode if KillEmbedding cluster id is available, falls back to categorical otherwise)

## K(c) schema — the canonical kill object

For each killed candidate `c`, the substrate produces:

```python
@dataclass
class KillObject:
    """K(c) — canonical input record for KillEmbedding training.

    Sourced from prometheus_math.discovery_pipeline emit_from_substrate
    (v2.3) NearMissCorpus.pre_falsification_view + post_falsification_view.
    """

    # ─── Identity (provenance, non-feature) ─────────────────────────
    cell_id: str                          # canonical claim hash
    domain: str                           # 'A149' | 'Lehmer' | 'BSD' | 'modular_form' | 'knot_trace_field' | 'genus2' | 'OEIS_sleeping' | 'mock_theta'
    coordinate_chart_id: str              # P0 chart reference (e.g. 'lehmer_deg14_palindromic_pm5_v1')
    operator_class: str                   # 'structural' | 'symbolic' | 'anti_prior' | 'uniform' | 'structured_null'
    timestamp: str                        # ISO-8601, for temporal splits

    # ─── KillVector (12 v0.1 + 8 v2.2 components) ───────────────────
    # Each component is a dict with `triggered: bool` + optional
    # `margin: float | None` + optional `confidence: float`.
    # 12 v0.1 components: out_of_band, reciprocity, irreducibility,
    #   catalog_Mossinghoff, catalog_lehmer_lit, catalog_LMFDB,
    #   catalog_OEIS, catalog_arXiv, F1, F6, F9, F11
    # 8 v2.2 components: relativizes, naturalizes, local_global_gap,
    #   requires_unproven_conjecture, asymptotic_only, small_case_artifact,
    #   asymmetric_effort, interpretive_slack
    kill_vector: dict[str, KillComponent]  # 20 components

    # ─── Margin profile (continuous signal) ─────────────────────────
    # Per-component margin where applicable. Missing → np.nan.
    # Sign convention: negative = closer to passing (interesting near-miss);
    # positive = clearly failing.
    margin_profile: np.ndarray             # shape (20,), dtype float32

    # ─── Method metadata (per-falsifier) ────────────────────────────
    # MethodSpec from substrate v2.2 §6.2 P3 — independence_class +
    # drift_channel for triangulation-aware aggregation
    method_spec: dict[str, MethodSpec]     # falsifier_id → MethodSpec

    # ─── Stability metadata (per-component) ─────────────────────────
    # Substrate v2.2 §6.2 P2 — perturbation-stability for high-magnitude
    # buckets (≥3); structured object not bool. Type name per
    # prometheus_math/stability_adapters.py shipped at d17a2ff8.
    stability_pass: dict[str, StabilityResult]  # component_id → result

    # ─── Spatial neighbors (for triplet sampling) ───────────────────
    # P5 NearMissCorpus emission's `neighbors_in_chart` field — the
    # cluster of objects in the same coordinate chart that share
    # canonical-form proximity. Crucial for hard-negative mining.
    neighbors_in_chart: list[str]          # cell_ids

    # ─── Outcome label (target supervision) ─────────────────────────
    # The terminal verdict + which falsifier(s) killed it
    terminal_state: str                    # 'PROMOTED' | 'SHADOW_CATALOG' | 'REJECTED'
    dominant_kill_pattern: str             # for backwards-compat with legacy
    near_miss: bool                        # cleared k-of-N falsifiers, k ≥ floor

    # ─── Computational friction (substrate v2.2 §6.2 P1) ────────────
    # Populated by Pre-Tier-0 0b telemetry, shipped at d17a2ff8 across
    # all 6 cross-domain envs (bsd_rank, modular_form, knot_trace_field,
    # genus2, oeis_sleeping, mock_theta) emitting info["elapsed_seconds"]
    # + info["oracle_calls"] per step.
    elapsed_seconds: float | None
    oracle_calls: int | None
    peak_memory_mb: float | None             # expected NaN for cross-domain
                                             # envs in v0.1; psutil deferred
                                             # to Tier 3 rollout per Techne

    # ─── Cross-references (provenance, for replay) ─────────────────
    # triangulation_history: v0.1 carries path_ids only (string list);
    # v0.2 upgrade path is list[TriangulationPathRef] from
    # sigma_kernel/exclusion_certificate.py if geometry needs verdict +
    # method-diversity signal.
    triangulation_history: list[str] | None  # for upgraded INCONCLUSIVE; path_ids only in v0.1
    exclusion_certificate_ref: str | None    # if cell sits inside a registered exclusion
    # NOTE: parent_cell_ids is NOT in K(c) v0.1.
    # P5 emit_from_substrate doesn't currently produce lineage. For v0.1
    # training we'll source parent lineage from tools/lineage_replay.py
    # (Ergon W2.3) at training time. v0.2 may promote lineage into K(c)
    # if cross-review surfaces a geometry need.
```

## Embedding function φ: K(c) → ℝ^d

```python
def phi(k: KillObject) -> torch.Tensor:
    """Map K(c) → low-dim embedding."""
    # ─── Feature extraction (deterministic) ─────────────────────────
    # 1. KillVector triggered-flags (20-bit one-hot; 20 dims)
    # 2. Margin profile (NaN-handled; 20 dims with mask)
    # 3. Operator class one-hot (5 dims)
    # 4. Top-3 falsifier ids one-hot per cell (~10 dims after canonicalization)
    # 5. Method independence_class one-hot (~5 dims)
    # 6. Computational friction normalized (3 dims)
    # 7. Cluster-cardinality of neighbors_in_chart (1 dim)
    # 8. Outcome label (terminal_state one-hot, 3 dims)
    # Total raw feature dim: ~67
    raw = extract_features(k)              # shape (B, 67)

    # ─── Learned projection ─────────────────────────────────────────
    # 2-layer MLP with skip connection
    # Hidden: 64; Output: d (8–32, default 16)
    embedding = encoder(raw)               # shape (B, d)
    return embedding
```

The encoder is small (≪ 100K params). KillEmbedding's value is in the *geometry* it learns, not the *representation power* of the encoder. If a 2-layer MLP doesn't learn a useful geometry on the existing 314K kill ledger, more parameters won't fix it.

## Training objective — three-loss composition

```python
def loss(batch: list[KillObject]) -> torch.Tensor:
    # ─── L1: contrastive (same-falsifier-class pull-together) ──────
    # Pairs (k_i, k_j) with same dominant_kill_pattern → minimize ||φ(k_i) - φ(k_j)||
    # Pairs (k_i, k_j) with different dominant_kill_pattern → push apart with margin α
    L1 = contrastive_loss(batch, alpha=0.5)

    # ─── L2: triplet (near-miss anchored to PROMOTE) ───────────────
    # The load-bearing part. Anchors come from P5 NearMissCorpus emission.
    # For each (anchor_promote, positive_near_miss, hard_negative_random):
    #   ||φ(anchor) - φ(near_miss)|| << ||φ(anchor) - φ(random)||
    # Hard-negatives MUST be drawn from same coordinate-chart neighborhood
    # (per Gemini's anti-trivial-separability concern in v2.2 §6.3).
    L2 = triplet_loss(batch, margin=0.3)

    # ─── L3: structural regularizer (anti-collapse) ────────────────
    # Penalize embedding variance below threshold; enforces the
    # geometry doesn't collapse to a single point.
    L3 = anti_collapse_regularizer(batch)

    return L1 + L2 + 0.1 * L3
```

## Synthetic-null guard (commit-blocking, per Techne Decision 1)

Before adopting KillEmbedding as MAP-Elites descriptor replacement, run the synthetic-null check:

1. Take the trained embedding φ.
2. Shuffle the falsifier-id labels across all training records (`dominant_kill_pattern` randomized per record while preserving marginal distribution).
3. Re-train φ' on the shuffled labels with same hyperparameters, same seed-set.
4. Compute structure metrics on both:
   - Silhouette score on cluster assignment
   - k-nearest-neighbor consistency
   - PROMOTE-distance distribution

5. **Decision rule:**
   - If φ produces meaningfully better structure than φ' (silhouette φ - silhouette φ' > 0.15 absolute, with bootstrap CI) → real geometry; adopt as MAP-Elites descriptor
   - If φ ≈ φ' on structure metrics → embedding learned corpus shape, not failure shape; **DO NOT ADOPT**; document as negative finding

This is the embedding-layer equivalent of the synthetic-null gate Ergon's Learner v0.5 uses at W4.0. Same discipline, different layer.

## Failure mode: domain collapse

The single most likely failure: KillEmbedding learns "Lehmer vs BSD vs modular vs ..." domain identity rather than failure-shape identity. Then `KillEmbedding distance ≈ domain distance + noise`, which is uninformative.

**Detection:** if synthetic-null guard passes (φ has structure beyond shuffled-label control), but PCA on φ shows the first principal component aligns >0.7 with one-hot domain encoding, the geometry is dominated by domain.

**Mitigation:**
- Train domain-by-domain initially. A149 prototype first (per Techne Decision 1).
- Cross-domain training waits for Pre-Tier-0 0b telemetry instrumentation across all 6 envs.
- When training cross-domain, add a domain-adversarial loss component (DANN-style) that penalizes embedding's ability to predict domain. Forces the geometry to encode failure-shape, not domain-shape.

## Constraint: data sufficiency

A149 has 314K logged kills with full per-record traces (cost telemetry, kill_vector, method_spec). Sufficient for training a 16-dim embedding with a 2-layer MLP encoder.

The other 5 cross-domain envs have aggregate kill_pattern counts only (per Charon's Substrate Cartography Suite: "data-rich but trace-poor"). Cross-domain KillEmbedding training waits on Pre-Tier-0 0b shipping. Pre-Tier-0 0b is in Techne's queue per `roles/Techne/RESPONSE_TO_APORIA_HANDOFF_2026-05-06.md`; ~1 day of work; gates on Techne next session.

**A149 prototype path (immediate, per Techne Decision 1):**
1. Schema audit — ✅ done (P5 emission carries inputs)
2. Implementation — Day 13-17 slot of joint sprint
3. Synthetic-null guard — commit-blocking before adoption
4. Negative finding allowed: if A149 prototype fails the guard, document and defer cross-domain expansion

## Consumption surface — how the substrate uses KillEmbedding

### 1. MAP-Elites descriptor replacement

Currently: 5-axis hand-designed descriptor (canonicalizer subclass / DAG entropy / output-type signature / magnitude bucket / canonical-form distance). Plus Ergon's W1.5 adds `dominant_failure_family` as 6th axis.

With KillEmbedding adopted: cluster-id assignment in φ-space replaces the 6th axis. Optionally collapses axes 1+5 if KillEmbedding subsumes them (verify by ablation).

### 2. kill_vector_navigator gradient-following

Currently: navigator works in raw vector space, covers 2/16 region cells.

With KillEmbedding adopted: navigator does gradient-following in φ-space. Given a candidate at embedding `z`, the navigator computes:
- nearest neighbors in φ
- direction toward lower-margin cluster (PROMOTE region)
- recommended operator class for the next mutation (per kill_vector_navigator's existing policy table, but indexed by cluster)

Coverage target: ≥12/16 region cells. Reported as observed policy table, NOT manifold chart (per ChatGPT/Gemini convergence in v2.2 §8 architectural lock-in).

### 3. ExclusionCertificate region-scoping

Currently: ExclusionCertificate scopes a single rectangular region in coordinate-chart space.

With KillEmbedding adopted: ExclusionCertificate can additionally scope a cluster region in φ-space. Allows "the failure mode that maps to this cluster has been fully enumerated" — a strictly stronger statement than "this region of the coordinate chart has been ruled out." Geometric exclusion certificate.

### 4. Novelty signal for new kills

Currently: a candidate's "novelty" is computed as Hamming-distance-to-Mossinghoff-catalog (or equivalent per-domain).

With KillEmbedding adopted: novelty becomes "is this kill in a sparsely-populated region of φ"? A new kill that lands far from all existing clusters in φ-space is a *new failure mode*, more interesting than another instance of an existing failure mode.

## Implementation slot (per Techne Decision 1)

Day 13-17 of joint sprint (`pivot/techne_ergon_joint_sprint_2026-05-05.md`). v2.3 already shipped (Day 4 in sprint clock); KillEmbedding implementation begins after v2.3 stabilizes and continues through Tier 3 cross-domain rollout.

**Deliverables in slot:**
1. `prometheus_math/kill_embedding.py` — encoder + training loop
2. `prometheus_math/kill_embedding_navigator.py` — extends `kill_vector_navigator` with φ-space gradient-following
3. `prometheus_math/tests/test_kill_embedding.py` — math-tdd 4-category coverage
4. `charon/diagnostics/KILL_EMBEDDING_VALIDITY_REPORT.md` — synthetic-null guard outcome + adoption recommendation
5. `prometheus_math/KILL_EMBEDDING_RESULTS.md` — adoption decision, structure metrics, ablation against the 5-axis descriptor

## Cross-review request

Before implementation begins:

- **Charon:** validate the synthetic-null guard discipline matches the substrate's existing falsification-first patterns. Flag if the structure metrics (silhouette, kNN-consistency, PROMOTE-distance) miss any class of trivial geometry (e.g., embedding that's structurally distinct from shuffled-label control but still uninformative).
- **Ergon:** confirm the consumption surface (MAP-Elites descriptor replacement, navigator gradient-following) integrates cleanly with v0.5 W1.5 (`dominant_failure_family`) and W2.4 (KillVector trajectory dashboard). Flag any breaking changes.
- **Frontier models (second-pass review):** identify failure modes not surfaced here. Especially: (a) whether contrastive + triplet + anti-collapse loss combo is sufficient for our scale, (b) whether the domain-adversarial mitigation actually generalizes when cross-domain training begins, (c) whether KillEmbedding adoption interacts with v3.0 hybrid kernel↔CoC translation (per Watch-1 PARTIAL verdict).

## Open questions for the implementer

1. **Embedding dimensionality d.** Default 16. Pick by elbow on validation silhouette across d ∈ {8, 12, 16, 24, 32}. Document in adoption report.
2. **Hard-negative mining strategy.** Random within-chart? Online hard-mining? Pre-computed? Document choice + rationale.
3. **Stability check at high-magnitude buckets.** KillEmbedding training on records with `stability_pass = NaN` — drop, impute, or weight down? Default: weight down by 0.5 in loss.
4. **Cross-domain transfer when 0b ships.** Train domain-specific encoders first, then a unified encoder with domain-adversarial loss? Or unified from start? Pilot both on first cross-domain pair (A149 → Lehmer is the natural first extension).
5. **Bookkeeping for embedding versions.** φ_v0.1 trained on 2026-05-XX corpus; v0.2 retrained when 0b lands; etc. Versioning policy: every embedding version carries `(corpus_hash, encoder_arch_hash, training_date, validation_silhouette_vs_null)` in its metadata.

## What this design seed does NOT cover

- Implementation of the encoder (Techne)
- Implementation of the training loop (Techne)
- The Illegibility Window (separate Watch-3 design pass; see watchlist)
- The kernel-foundation hybrid translation (separate Watch-1 v3.0 design pass)
- The Watch-4 substrate-vs-search baseline comparison (separate; runs at v1.0 design)

## Resolution status

Approved by Techne 2026-05-06 (Decision 1 in `roles/Techne/RESPONSE_TO_APORIA_HANDOFF_2026-05-06.md`). Awaits cross-review by Charon + Ergon + frontier models before code. Time-sensitive — P5 emission stabilized at v2.3 commit `d17a2ff8`; KillEmbedding training can run on `emit_from_substrate` output as currently shipped.

Implementation slot: Day 13-17 of joint sprint. We are at Day 4. Cross-review window: Days 5-12.

— Aporia, 2026-05-06
