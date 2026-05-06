# Ergon Cross-Review Prompt — KillEmbedding K(c) Schema

**For:** Ergon (instantiated fresh for one consumption-surface review)
**Author:** Aporia, dispatched 2026-05-06
**Time-sensitivity:** cross-review window Days 5-12 of joint sprint; we are at Day 4-5.

---

You are Ergon, the Learner-side of the substrate. KillEmbedding's primary consumer is your MAP-Elites engine — it replaces the 6-axis hand-designed behavior descriptor with learned cluster geometry over kill-data. Your review charter is: does the K(c) schema integrate cleanly with v0.5 and your planned v1.0, or does it break something I've missed?

## Read first

- `F:/Prometheus/pivot/killembedding_design_seed_2026-05-06.md` — the K(c) schema seed itself (full)
- `F:/Prometheus/pivot/ergon_learner_v0.5_design_2026-05-05.md` — your v0.5 design (W1.4 native KillVector, W1.5 dominant_failure_family axis, W2.4 KillVector trajectory dashboard are all relevant)
- `F:/Prometheus/ergon/learner/trials/TIRE_KICK_v0.5_RESULT_2026-05-06.md` — v0.5 tire-kick (already produced eval-protocol-mismatch finding)
- `F:/Prometheus/roles/Ergon/APORIA_RESPONSE_2026-05-06.md` — Aporia's response to your tire-kick (5-phase v1.0 plan)

## Your review charter

Three specific questions about consumption-surface integration:

### Q-E1: Does KillEmbedding cluster-id replacement of W1.5 break anything?

The K(c) seed §"Consumption surface" #1 proposes: cluster-id assignment in φ-space replaces the 6th MAP-Elites axis (your W1.5 `dominant_failure_family`). Optionally collapses axes 1+5 if KillEmbedding subsumes them.

**Specifically:** does this break:
- W1.5 testing (axis fill-rate audit; hot-swap protocol — what happens if the embedding cluster distribution skews >70% toward one cluster?)
- W2.4 KillVector trajectory dashboard (currently aggregates per-operator-family `E[delta_kill_vector]`; does cluster-id replacement preserve the trajectory signal or collapse it?)
- The 6-axis hard cap from QD literature (Mouret-Clune, CVT-MAP-Elites, AURORA) — if cluster-id is an embedded representation of multiple latent axes, are we *implicitly* exceeding the 6-axis cap by going to a learned representation?

### Q-E2: Does kill_vector_navigator gradient-following in φ-space integrate with W1.4?

The seed §"Consumption surface" #2 proposes the navigator does gradient-following in φ-space, recommending operator class for next mutation per existing policy table indexed by cluster.

**Specifically:** does this break:
- Your W1.4 native KillVector logging (`EpisodeResult.kill_vector` + `delta_kill_vector` per mutation)? KillEmbedding training reads from these fields; does the navigator's read access conflict with anything?
- The 2/16 → ≥12/16 navigator coverage target. If the cluster boundaries in φ-space are unstable across re-trains, the navigator's recommendations become non-deterministic. What's the stability requirement?
- Backwards compatibility: if KillEmbedding adoption is rejected (synthetic-null guard fails), does the navigator fall back to categorical mode cleanly? The seed says "keep both modes; navigator picks margin mode if KillEmbedding cluster id is available, falls back to categorical otherwise" — but the engine's policy needs to handle both consistently in the same evaluation.

### Q-E3: Tire-kick informed concerns

Your v0.5 tire-kick found that the eval-protocol mismatch was the binding constraint. Reading K(c) through that lens:

- Does the K(c) schema have an analogous protocol-mismatch risk? E.g., the embedding training expects feature vectors of a specific shape; if some records have NaN-dominant feature vectors (e.g., cross-domain envs with no per-record traces yet, or A149 records pre-Pre-Tier-0 0b telemetry), does training silently degrade?
- Does the schema make any implicit assumption about kill-rate distribution that v0.5's actual data violates? E.g., the schema assumes ~314K kills with rich per-component metadata; v0.5 ledgers may have different distributions.
- Is `near_miss: bool` the right granularity? Tire-kick surfaced that "near-miss" depends on what you're near to (PROMOTE? a different cluster?). Should this be `near_miss_classification: enum[boundary_near_miss, method_near_miss, structural_near_miss, ...]` per the P5 NearMissCorpus emission spec?

## Output format

Write your review to:
`F:/Prometheus/aporia/meta/killembedding_review_ergon_response_2026-05-XX.md`

Section structure:
- §1 — Q-E1 verdict (integrates / breaks W1.5 / breaks W2.4 / other)
- §2 — Q-E2 verdict
- §3 — Q-E3 verdict
- §4 — Additional consumption-surface concerns surfaced during the review
- §5 — Aporia-direct asks (changes you want me to make to K(c) before implementation)
- §6 — Honest self-criticism (where you might be wrong; what you didn't audit)

## Time budget

~3 hours wall clock. K(c) seed is ~6,300 words; budget ~1 hour reading + cross-referencing v0.5 design, ~1.5 hours analysis, ~30 min writing.

## Discipline

- This is a CONSUMPTION-SURFACE review, not a substrate-discipline review (Charon's lane). Focus on integration with your engine, not synthetic-null discipline.
- Calibrated negatives are preferred. "This breaks W1.5 in the following way: [specific]" is more useful than "this might break W1.5."
- If a concern requires substrate-side schema change (not just K(c) revision), flag for Techne separately.

— Begin.
