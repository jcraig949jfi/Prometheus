# Greedy LoRA follow-up — consolidated findings (2026-06-07)

Four follow-ups to the 2026-06-03/04 greedy result, run sequentially at James's
direction: (1) source ablation, (2) a real OOD number, (3) a diverse-gold transfer
test, (4) un-stall the Theseus→Ergon handoff. Full method/log:
`GREEDY_FOLLOWUP_PROGRESS_2026-06-07.md`.

## Headline

The greedy LoRA's gain decomposes, in order of size, into: **format-following ≫ a
False/kill prior ≫ narrow per-source template-classes ≫ genuine reasoning**. There is
**no cross-domain transfer** — not across substrate sources, and not even across
sub-domains of the same meta-domain (number theory). The "needle moved +0.68" headline
is real but is almost entirely format + prior + per-template memorization. This is a
calibrating kill: **adding more failure data of the same shape will not grow the
reasoning share.**

## Task 1 — source ablation (leave-one-out, fixed 1,200-item gold)

Reproduced the headline exactly (base 0.228 → full 0.908), then dropped each source from
TRAIN and re-scored on the same gold set:
- The gold task is **three independent per-source slices with ~zero transfer**. Drop
  theseus → its slice 0.86→0.25 (overall collapses to all-False, −0.41); drop hephaestus
  → 1.0→0.29; drop pollux → 1.0→0.395. Every *other* slice is untouched each time.
- The pure failure-reasoning sources (erebos, charon prose, harmonia retractions) move
  accuracy ≤0.005 — **zero measurable contribution** to the gold metric. (Caveat: they
  have no gold slice of their own; this measures only their transfer, which is nil.)
- pollux: **86 train rows → 1.0** on its 200-item slice; remove them → 0.395. That is
  per-template class-learning, not reasoning.

## Task 2 — a real OOD number (computable-gold, since CounterMATH is leaderboard-gated)

CounterMATH ground truth is withheld by design (confirmed from the repo README; the HF
labeled repo 404s even with a token). Rather than fabricate via circular LLM-judge, I
built a **computable-gold OOD set** — 494 balanced number-theory claims, gold computed
deterministically, domains disjoint from training.
- **Format transfers fully** (base parse-fail 1.0 → trained 0.0).
- **Judgement barely transfers: 0.55 vs 0.50 chance**, and the T/F split (0.20/0.90)
  shows it's a **False prior**, not discrimination. Primality & summation show zero
  signal; only coprimality/perfect-square show a faint bump.
- The same False-lean explains the CounterMath shift (86% False) — "directionally right"
  only because CounterMath is counterexample-heavy; on a balanced set the lean is
  indiscriminate.

## Task 3 — diverse-gold transfer test (reframed from "Charon adapter")

Reframed after finding the literal task low-yield: stygian's 373-row structured ledger is
~95% infrastructure exhaust (logged ≠ navigable), and the rich Charon prose the rig
already ingests adds nothing to the metric. The high-value question instead: does adding
**balanced computable-gold judgement data from a new meta-domain** correct the prior and
transfer to held-out sub-domains? Train = substrate + 3,200 balanced number-theory rows
(4 domains); held out = 3 disjoint number-theory domains.
- **Transfer essentially absent**: held-out 0.532 → 0.558 (+0.027 on n=600, ~1.3σ, NOT
  significant). Substrate gold unchanged (0.908 → 0.903; no regression).
- The entire lift is **perfect_square (+0.095)**; summation and inequality are flat. The
  decisive read: **transfer appears only where the surface pattern is shared, and is
  absent exactly where genuine computation is required** (n(n+1)/2; comparing 2^k). The
  model is a bag of per-template surface classifiers.

## Task 4 — un-stall the Theseus→Ergon handoff

Pipeline was stalled since 2026-05-19. The audit's gate-fix (Fire #33: kills flow; 20%
floor) was already in code. What I found and did:
1. **Root cause of the stall, fixed.** `export_for_ergon`'s scoring loop walked the
   **entire 346 GB / 265-batch corpus** to pick 500 records (only the episode index was
   bounded). Bounded the scoring walk to the newest-N batches + added a `--max-recent-files`
   CLI guard. 7/7 handoff tests pass.
2. **Falsify floor raised 0.20 → 0.40** (proportional to the corpus's ~40% kill rate;
   failures first-class).
3. **Surfaced the pipeline is doubly blocked, not just stalled.** With the floor pulling
   kills, the first re-emit shipped 500 records that were all degenerate placeholders
   (generator d2 = `kill_neighborhood`) — because the `training_anchor` mapper **only
   renders `invariant_equality` knot×EC records**; other kinds become "Does relation `?`
   hold…" garbage. **This is the real reason the main Learner corpus is a knot×EC
   confirmation monoculture.** I added a mappability gate (never ship garbage) and
   quarantined that bundle — but the second re-emit then produced **0 records**, because
   recent `invariant_equality` records score w≈0.20 (max 0.33), all **below the 0.5
   threshold**, while the unmappable d2 kills sit exactly at 0.5. So the only mappable kind
   is below threshold and what clears threshold isn't mappable.
   - **Final state (strictly better than found):** mechanism un-stalled (bounded walk —
     daemon runnable, won't hang); floor 0.40; gate ⇒ nothing-or-clean, never garbage;
     inbox empty. Two Theseus-lane fixes remain before useful failure data flows: (a)
     extend the mapper to all claim_kinds — port `ergon/learner/greedy/serializers.py`
     (already renders kills correctly); (b) recalibrate `training_weight`/threshold so
     `invariant_equality` kills clear the bar. Given the ablation kill, ship-nothing-until-
     fixed is the right conservative state.

## What this means for the program

- The substrate-ingestion thesis, as measurable on the *gold-judgement* eval, is narrow
  and non-transferring. **The bottleneck is not data volume or variety — it's that the
  training produces surface classifiers, not computation.** Growing the reasoning share
  needs a different lever: multi-step claims where priors can't substitute, a model/method
  with more capacity than rank-16/1-epoch/1.5B, and an eval that is a transfer test rather
  than per-source slices.
- **Scope guard:** all of the above is about the gold-judgement metric. The Learner's
  actual objective — predicting productive search moves / routing by failure — has *no
  eval yet*. That missing eval is the deeper gap; failure-first corpus representation
  remains correct for that objective even though it doesn't move the gold metric. Building
  a routing eval is the natural next step.

— Ergon, 2026-06-07
