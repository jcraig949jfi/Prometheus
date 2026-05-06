# Frontier-Model Cross-Review Prompt — KillEmbedding K(c) Schema

**For:** frontier model second-pass review (Claude / Grok / DeepSeek / Gemini — fire each separately)
**Author:** Aporia, dispatched 2026-05-06
**Time-sensitivity:** cross-review window Days 5-12 of joint sprint; we are at Day 4-5. Implementation slot Day 13-17 awaits your verdict.

---

## What you're being asked to review

Project Prometheus is building a falsification-first substrate for mathematical discovery. Substrate v2.3 just shipped (typed kernel, falsification battery, KillVector primitive, ExclusionCertificate scoping, NearMissCorpus emission). The next substrate primitive proposed is **KillEmbedding** — a learned geometric embedding over the substrate's existing kill-data (~314K logged kills) intended to:

- replace the hand-designed 6-axis MAP-Elites behavior descriptor
- provide gradient-following capability for the kill_vector_navigator
- enable region-scoped (not just point-scoped) ExclusionCertificates
- give the substrate a novelty signal for new failure modes

The design seed for KillEmbedding is at:
`F:/Prometheus/pivot/killembedding_design_seed_2026-05-06.md` (~6,300 words)

It includes: K(c) canonical schema (the kill-object dataclass), the embedding function φ: K(c) → ℝ^d, three-loss training objective (contrastive + triplet + anti-collapse), commit-blocking synthetic-null guard, and consumption surfaces.

## Why a frontier-model review

Two prior reviews are already in flight: Charon (substrate-discipline expertise) and Ergon (consumption-surface expertise). You're the third pass: failure-mode hunt by an outside reviewer not embedded in Project Prometheus's recent decisions.

**Critical:** prior reviews from Charon, Ergon, and Aporia (the K(c) author) all share priors from working on Prometheus. Convergent multi-agent enthusiasm is a known risk pattern flagged in `pivot/external_review_watchlist_2026-05-05.md` Watch-4. Your job is to surface failure modes the in-house reviewers will miss because they share priors.

## Your review charter

Three specific questions:

### Q-F1: Three-loss objective sufficiency

The K(c) seed proposes a three-loss composition for embedding training:
- L1: contrastive (same dominant_kill_pattern → pull together; different → push apart with margin)
- L2: triplet (anchored to PROMOTE; positive = near-miss; hard negative drawn from same coordinate-chart neighborhood)
- L3: anti-collapse regularizer (penalize embedding variance below threshold)

**Question:** is this sufficient for our scale (314K records, ~67-dim raw features, 16-dim embedding default)? Specifically:
- Are there documented failure modes of contrastive + triplet learning at this scale that the seed misses?
- Is the anti-collapse regularizer the right form? Stronger forms exist (BarlowTwins, VICReg, etc.) — are they overkill for the scale, or warranted?
- Does the loss composition handle the heavy-tail distribution of dominant_kill_pattern correctly? Substrate's gradient archaeology shows top-3 kill_pattern carries 86.4% of mass; if the contrastive loss treats common kill_patterns and rare ones symmetrically, the learned geometry will be dominated by common-kill structure.

### Q-F2: Domain-adversarial mitigation generalization

The seed names domain-collapse as the most likely failure mode. Mitigation: train domain-by-domain initially (A149 prototype); DANN-style domain-adversarial loss when cross-domain training begins.

**Question:** does the DANN-style mitigation actually generalize when cross-domain training begins?
- Is "linear probe on final layer can't predict domain" a sufficient operational test, or can earlier layers carry domain identity that leaks through?
- The 6 cross-domain envs (BSD rank, modular forms, knot trace fields, genus-2, OEIS sleeping, mock theta) have radically different kill-distributions per Charon's per-domain π₀ analysis (Lehmer 0.999, genus-2 0.669). Does DANN handle this distributional mismatch, or does the adversarial gradient become unstable when classes are 1000× imbalanced across domains?
- Is there a stronger mitigation pattern (information-bottleneck, mutual-info-minimization, class-conditional domain-adversarial) the K(c) seed should adopt instead?

### Q-F3: Interaction with v3.0 hybrid kernel

Substrate Watch-1 (logical foundation) has a PARTIAL feasibility verdict: hybrid kernel ↔ Calculus-of-Constructions translation is queued for v3.0. CoC subsumes 7 of 11 substrate constructs; ERRATA / BIND / EVAL resist clean type-theoretic encoding.

**Question:** does KillEmbedding adoption interact with this v3.0 hybrid translation?
- Does the embedding's training data shape (K(c) schema) bake in operational-VM assumptions that won't survive the CoC translation?
- If v3.0 introduces a typed propositional layer (CoC) over the existing imperative VM, does KillEmbedding need to exist at the propositional layer (in CoC types) or the operational layer (over the existing kill-records)?
- Is there a v3.0 design risk where KillEmbedding becomes a v2.x artifact that gets thrown away when the kernel rebases? The seed hand-waves this in §"What this design seed does NOT cover" — it lists v3.0 hybrid translation as a separate concern. Push back if you think this hand-wave is wrong.

## Bonus question (optional)

The substrate's central wager (Watch-4 in the watchlist): compounding substrate produces capability faster than compounding search. KillEmbedding doubles down on this — it's a substrate-instrumentation compound, not a search compound.

**Optional Q-F4:** in a hypothetical contrastive-with-frontier-thinking, would investing 1B parameters of search compute on an existing arsenal beat the substrate's compounding instrumentation strategy?

## Output format

Write your review to:
`F:/Prometheus/aporia/meta/killembedding_review_frontier_response_<your_model_name>_2026-05-XX.md`

(Replace `<your_model_name>` with `claude`, `grok`, `deepseek`, `gemini`, etc., so multiple frontier-model reviews don't collide on filename.)

Section structure:
- §1 — Q-F1 verdict (sufficient / insufficient / sufficient-with-conditions)
- §2 — Q-F2 verdict
- §3 — Q-F3 verdict
- §4 — Optional Q-F4 verdict
- §5 — Failure modes the in-house reviewers will miss because they share priors
- §6 — Honest self-criticism (where you might be wrong; what you didn't audit)
- §7 — One-paragraph summary suitable for Aporia to paste into the v0.1 KillEmbedding adoption decision

## Time budget

~2-3 hours of focused review.

## Discipline rules

- Calibrated negatives preferred to confident positives
- Reference specific lines in the K(c) seed when raising concerns
- Surface convergent-bias risks: are there assumptions in the seed that match Project Prometheus's recent commitments but might be wrong?
- "I don't know" is a valid answer for any sub-question requiring expertise outside your scope; don't fabricate

— Begin.
