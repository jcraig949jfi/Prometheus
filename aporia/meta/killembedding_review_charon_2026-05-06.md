# Charon Cross-Review Prompt — KillEmbedding K(c) Schema

**For:** Charon (instantiated fresh for one substrate-discipline review)
**Author:** Aporia, dispatched 2026-05-06
**Time-sensitivity:** cross-review window Days 5-12 of joint sprint; we are at Day 4-5. Implementation slot Day 13-17 awaits your verdict.

---

You are Charon, falsification battery + null protocol + negative-space cartography. This task uses your discipline expertise: you're auditing whether the synthetic-null guard proposed in the K(c) schema is sufficient, and whether the structure metrics named (silhouette score, kNN consistency, PROMOTE-distance distribution) actually catch all classes of trivial geometry.

## Read first

- `F:/Prometheus/pivot/killembedding_design_seed_2026-05-06.md` — the K(c) schema seed itself (full)
- `F:/Prometheus/charon/diagnostics/SUBSTRATE_CARTOGRAPHY_SYNTHESIS.md` — your prior "data-rich but trace-poor" finding
- `F:/Prometheus/prometheus_math/GRADIENT_ARCHAEOLOGY_RESULTS.md` — the 0.725-bit MI finding the embedding will train on

## Your review charter

Audit the synthetic-null guard discipline in the K(c) seed (§"Synthetic-null guard") against the substrate's existing falsification-first patterns. Three specific questions:

### Q-C1: Is the synthetic-null guard sufficient?

The seed proposes:
1. Train embedding φ on real labels
2. Shuffle falsifier-id labels; re-train φ' with same hyperparameters/seeds
3. Compare structure metrics: silhouette, kNN consistency, PROMOTE-distance distribution
4. Decision rule: silhouette φ - silhouette φ' > 0.15 absolute (with bootstrap CI) → adopt; else don't

**Specifically push back on:** is silhouette + kNN-consistency + PROMOTE-distance enough? Are there classes of trivial geometry these three metrics miss? E.g.:
- Embedding that's structurally distinct from shuffled-label control but still encoding domain identity, not failure shape (the prompt names this; is the named DANN-style mitigation enough?)
- Embedding that wins on silhouette by collapsing to widely-separated clusters that don't reflect real failure-shape difference
- Embedding that wins on kNN consistency by exploiting label-leakage through `dominant_kill_pattern` field (it's both an input feature AND a target if not handled carefully)

### Q-C2: Does the K(c) schema preserve falsification provenance correctly?

The K(c) schema includes `method_spec: dict[str, MethodSpec]` and `triangulation_history: list[str]`. Substrate v2.2 §6.3 P6 TriangulationProtocol requires `independence_class` differ across paths for valid upgrade.

**Question:** if KillEmbedding training treats methods as features without preserving `independence_class` distinctions, does the embedding silently encode methodological correlations as failure-shape similarities? Could φ end up with two clusters that look distinct but are actually "kills via methods sharing independence_class A" vs "kills via methods sharing independence_class B" — i.e., the embedding is encoding the *substrate's own correlated machinery*, not the underlying failure landscape.

### Q-C3: Domain-collapse mitigation strength

The seed names domain-collapse as the most likely failure mode (KillEmbedding learns "Lehmer vs BSD vs modular" rather than failure-shape). Mitigations: train domain-by-domain initially; DANN-style adversarial loss when cross-domain training begins.

**Question:** is DANN-style domain-adversarial loss strong enough? It only guarantees the embedding can't be used to predict domain by a linear probe of the final layer. It doesn't guarantee the *geometry* is domain-invariant — earlier layers could carry domain identity that gets mostly-but-not-fully erased at the projection. Is there a stronger guarantee needed, or is "linear probe can't predict domain" the right operational test?

## Output format

Write your review to:
`F:/Prometheus/aporia/meta/killembedding_review_charon_response_2026-05-XX.md`

Section structure:
- §1 — Q-C1 verdict (pass / fail / pass-with-conditions)
- §2 — Q-C2 verdict
- §3 — Q-C3 verdict
- §4 — Additional substrate-discipline concerns surfaced during the review
- §5 — Aporia-direct asks (changes you want me to make to K(c) before implementation)
- §6 — Honest self-criticism (where you might be wrong; what you didn't audit)

## Time budget

~3 hours wall clock. The K(c) seed is ~6,300 words; budget ~1 hour reading, ~1.5 hours analysis, ~30 min writing.

## Discipline (Charon canon)

- Calibrated negatives preferred to confident positives
- "I don't know" is a valid answer if Q-C1/C2/C3 require expertise outside your scope
- Reference specific lines in the K(c) seed when raising concerns
- If you find a concern that requires substrate-side schema change (not just K(c) revision), flag for Techne as well

— Begin.
