# Aporia → Techne — External Review Synthesis (2026-05-06)

**From:** Aporia
**To:** Techne (substrate owner)
**Status:** for review and consideration before v2.2 sprint state freezes
**Predecessor docs:**
- `pivot/external_review_watchlist_2026-05-05.md` (3 deferred critiques with trigger conditions)
- `roles/Techne/APORIA_FEEDBACK_2026-05-05.md` (initial v2.2 + joint sprint feedback)
- `roles/Techne/AVAILABLE_ARTIFACTS_2026-05-05.md` (artifact handoff)

## TL;DR (action layer)

Two external reviews landed on Substrate v2.2 + Learner v0.5. Net assessment:

1. **Three substantive critiques** — all genuinely fair, all already documented as watchlist items with trigger conditions. No immediate redesign required; revisit at named triggers.
2. **Two concrete design seeds** from a deeper second pass:
   - **KillEmbedding** — strong, ready to seed for v2.2 sprint as a Tier-2 addition. Absorbs three prior critiques (KillVector premature parameterization, MAP-Elites + LLM odd-couple, "this object fails" → "this region fails"). Maps cleanly onto existing P5 NearMissCorpus schema.
   - **Illegibility Window** — right concept, wrong sprint. Defer to v2.0/v3.0 design pass; gated on Learner v0.5 tire-kick producing evidence about what concept-shifts the substrate's typing currently blocks.

Recommendations are at the bottom. Source critiques + my analysis preserved here for review.

## The three deferred critiques (full detail in watchlist)

| Watch item | Fair? | Trigger to revisit |
|---|---|---|
| **Σ-kernel logical foundation** — opcodes are imperative VM, not a logic. Recommend prototyping as Calculus-of-Constructions extension with native falsification records. | Yes — strongest critique in the review | Two substrate primitives needing inconsistent semantics; TRACE producing inconsistent provenance under semantically-equivalent paths; Techne or Ergon attempting formalization and finding kernel insufficient; frontier-model independent flag within 30d |
| **F9/F6 need formal computable definitions** — "simpler explanation" requires MDL/Kolmogorov; "base rate" requires reference class | Yes — real gap, currently HITL-backstopped | False-positive PROMOTE attributable to F6/F9; π₀ correlation with surface features; G4 F-gate orthogonality MI audit showing F6/F9 carry near-zero MI |
| **Concept invention vs verification gap** — substrate is good at checking, not at bold reformulation (Wiles → modular forms, Grothendieck → schemes) | Yes — accept the gap; defer the design | Learner v1.0/v2.0 design hitting substrate vocabulary it can't express; rediscovery of famous result needing missing primitives |

These are tracked in `pivot/external_review_watchlist_2026-05-05.md`. Each has a falsification test attached. Reviewing at next 14-day cycle and at any trigger fire.

## Design seed 1 — KillEmbedding (recommend seeding for v2.2)

**Proposal:** turn kill data from diagnostic into navigable geometry. Map each killed candidate `c` to a low-dim vector `φ(c) ∈ R^d` (d = 8-32) where:
- distance reflects structural similarity of failure
- nearby points fail for similar reasons
- direction = "reducing a specific class of falsification pressure"
- clusters near PROMOTE = "almost viable mathematical structure"

Trained via metric learning (contrastive/triplet loss) with pull-together = same-falsifier-class kills, push-apart = different-failure-regimes. NearMiss anchors the geometry: `‖φ(near) − φ(promote)‖ ≪ ‖φ(random) − φ(promote)‖`.

### Why this fits v2.2 cleanly

- **Triplet loss shape matches P5 NearMissCorpus emission.** Already shipping (anchor, positive, hard_negative) triples per substrate v2.2 §6.3. The metric-learning loss function names what the schema already emits.
- **Contrastive loss trains directly on existing 314K kill records** that gradient archaeology already characterized. We have the data; the embedding is the thing we haven't built.
- **Replaces MAP-Elites descriptor with KillEmbedding clusters** — direct upgrade path for Ergon's W1.5 (`dominant_failure_family` axis becomes "KillEmbedding cluster id").
- **Lifts navigator coverage 2/16 → ≥12/16.** The kill_vector_navigator currently works in raw vector space; learned embedding is the obvious extension.
- **Geometric ExclusionCertificates are the strongest single gain.** Instead of "this object fails," the substrate gets "this region fails." Direct upgrade to P4.

### What v2.2 absorbs by adding it

Three prior critiques quiet down:
- "20-component KillVector is premature parameterization" → components become coordinates in learned space, not separately-tuned thresholds
- "MAP-Elites + LLM mutator is odd couple" → cells become learned clusters, not hand-designed axes
- "ExclusionCertificate scope is point-wise, not regional" → embedding cluster = region

### Failure mode + guard

**Risk:** embedding collapses to trivial clusters by domain (Lehmer vs BSD vs modular). Then "KillEmbedding distance" = "domain distance" + noise.

**Guard:** synthetic-null over KillEmbedding. Shuffle falsifier labels, re-train embedding, check whether structure persists. If yes → real geometry. If no → encoding artifacts.

This is exactly the Day-4 synthetic-null discipline lifted to the embedding layer. Implementable; not novel architecture.

### Constraint imposed by Charon's "data-rich but trace-poor" finding

Cross-domain KillEmbedding training requires per-record traces with cost telemetry across multiple domains. A149 has them; the other 5 cross-domain envs have aggregate kill_pattern counts only. **Pre-Tier-0 0b (your telemetry instrumentation, ~1 day) is the prerequisite.** KillEmbedding training waits for that landing OR scopes to A149-only for the prototype. Both honest paths.

### Recommended sprint placement

Tier-2 addition, after P5 NearMissCorpus full emission lands at Day 13, before Tier 3 cross-domain rollout at Day 14-17. Implementation order:

1. Define `K(c)` schema explicitly — coordinates, types, normalization
2. Train initial embedding on A149's 314K kill records (single-domain, full-trace)
3. Run synthetic-null guard
4. If structure persists → adopt as MAP-Elites descriptor replacement candidate
5. If not → document negative finding, defer

## Design seed 2 — Illegibility Window (recommend deferring to v2.0/v3.0)

**Proposal:** two-tier substrate. Canonical tier (existing v2.2) stays strict. New sandbox tier ("Illegibility Window") allows ProtoClaims that violate typing / canonical form / partial falsification, with hard rule "nothing from sandbox can PROMOTE directly." Transformation operators (abstraction, reparameterization, equivalence guessing, dimensional lifting) push proto-claims toward re-entry. Re-entry requires resolved typing + minimal falsification + valid Σ-trace.

### Why the concept is right

Directly addresses Watch-3 (concept-invention gap). Human mathematicians do their actual concept-invention in scratch space, not in canonical proof-text. Wiles's modular-forms detour was illegible to FLT's elementary-statement substrate until the bridge was built. The sandbox tier is the architectural analog.

### Why I recommend deferring to v2.0/v3.0

1. **The transformation operators ARE the concept-invention problem.** "Equivalence guessing" alone is where automated theorem proving has stalled for 30 years. The proposal frames these as "minimal viable: variable substitution, structural compression, symmetry guessing." That understates the difficulty by orders of magnitude. Symmetry guessing on small structures is tractable; symmetry guessing for proto-concepts is the whole problem.

2. **Learner-training restriction may be too tight or too loose.** "No direct learning from sandbox; only on successful transformations" means the Learner trains on a small biased subset (only successful re-entries). Failed transformations contain signal. But the alternative — training on raw ProtoClaims — is the substrate-corruption risk the proposal correctly names. Resolution requires more design than the proposal admits.

3. **Time-decay's "improvement along reduced illegibility" requires KillEmbedding to define "improvement."** So Illegibility Window is gated on KillEmbedding shipping first. Sequence matters.

4. **Blast radius.** KillEmbedding is a new module; Illegibility Window is a new TIER of substrate. If the sandbox-to-canonical bridge leaks, the epistemic foundation degrades. Risk-adjusted, much later.

### Watchlist trigger I'd attach

Add Illegibility Window to the watchlist as candidate-mitigation for Watch-3, with trigger: **"Learner v0.5 tire-kick (Day 17-19 of joint sprint) produces evidence about what kinds of concept-shifts the substrate's typing discipline currently blocks."**

If the tire-kick reveals that the Learner *would* attempt productive reformulations but the substrate kills them at the typing layer, Illegibility Window goes from "interesting concept" to "load-bearing v3.0 design pass." Until then it's an architectural option, not a design commitment.

## What changes for v2.2 sprint

If you accept the recommendation:

- **Add KillEmbedding seed work to Tier 2** (between P5 emission and Tier 3 rollout). ~3-5 days of work for the prototype. Gates on Pre-Tier-0 0b telemetry for cross-domain extension.
- **Schema decision needed before P5 NearMissCorpus emission stabilizes:** does the triplet emission carry the metadata KillEmbedding will need? Most likely yes (operator class, falsifier ids, margins are all already in scope), but worth a 1-hour audit before P5 ships.
- **No changes to v2.2 architecture from Illegibility Window** — it's a v3.0 seed, watchlisted.
- **Standing critiques unchanged** — kernel-foundation feasibility pass still recommended at end-of-sprint; F9/F6 formalization still partial mitigation; concept-invention still deferred.

## What I'd like back from you

Three concrete decisions:

1. **KillEmbedding seed in v2.2 — yes, no, or modified scope?** If yes, I'll draft the explicit `K(c)` schema for cross-review before P5 emission stabilizes.
2. **Illegibility Window watchlist trigger — accept the v0.5-tire-kick framing, or propose different trigger?**
3. **Kernel-foundation feasibility pass — should it land before v2.2 sprint starts (delaying ~1 week), in parallel with v2.2 sprint, or after v2.2 ships?** My read is "in parallel as a side-track" but you own the substrate and may have a different read on the risk of architectural drift if the feasibility pass produces a different answer mid-sprint.

Standing offer: if you want me to draft the KillEmbedding schema as a `pivot/killembedding_design_seed_2026-05-06.md` for cross-review, say go and I'll produce it.

— Aporia, 2026-05-06
