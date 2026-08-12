# Techne — Revival Assessment, 2026-08-12

**Role:** Techne (toolsmith / substrate-owner: `sigma_kernel`, `prometheus_math`,
`discovery_pipeline`, promotion machinery).
**Trigger:** James — "long break; want to revive Prometheus. New frontier model
versions exist. How do we leverage them toward the North Star?"
**Prior position this extends:** `pivot/REASSESSMENT_2026-06-23_techne_dissent.md`
("walk and chew gum") + `roles/Techne/M05_PROMOTION_REPLAY_FINDINGS_2026-06-23.md`.

---

## 1. State on entry — verified, not assumed

Checked this session (not read off the resume doc):

- **Dormancy is real and clean.** Last substantive human commit `fda01127`
  (Aporia session pause, **2026-06-28**). Everything since is `auto: portfolio
  update` / `arsenal: capability matrix` — a cron heartbeat, not work. ~6.5 weeks.
- **Repo is synced.** `origin/main` ahead 0 / behind 0. The June GitHub
  IPv4-blackhole incident is resolved; the two `.bundle` files in the tree are
  now-obsolete transport artifacts (untracked, safe to delete after a verify).
- **The arsenal's front door is broken in the default interpreter.**
  `python -c "import prometheus_math"` → `ModuleNotFoundError: No module named
  'cypari'`. Default `python` on PATH is `H:\Python312\python.exe`, no `cypari2`
  installed. `import sigma_kernel` is fine.
  This is **exactly** the defect I filed and declined to fix on 2026-06-22
  (fire log §3.2): eager hard-imports of native backends in
  `prometheus_math/__init__.py`, while the optional SDP/QP modules are already
  try/except-guarded. Six weeks of env drift turned an observation into a blocker.
  It takes down the **pure-stdlib** primitives too — including
  `reasoning_quality_emit`, the one the decisive experiment needs.

**Substrate facts that survived the break** (mine, from M0.5, unchanged):
promotion is confirm-by-assertion; the kernel gate is demo-scale in both SQLite
and Postgres; the historic "2,351 promotions" is a formula fossil (zero records
clear the current `training_weight ≥ 0.6` bar, max observed 0.33–0.52);
`signature_index` collapses **413M raw records into 3,311 shape-classes** carrying
kill/confirm geometry, and **nothing metabolizes it**.

**Where the fleet had gotten to** (Harmonia A, 06-27): the grading oracle exists
and is non-gameable (staircase 8% → 34% → 59% → 62%, independent verifier
157/157 agreement); the coverage sweep says the stall is **representational**, not
epistemic (EC = B2 ceiling at 12% hypothesis-class coverage; z3 can decide B4/B6
*today* and fails only on narrow wiring); the M0 keystone says the selector cannot
see novelty and fails **closed** (0% reject — a trustworthy audit property, and a
certification of zero novel-shaped truths).

---

## 2. What the break did and did not change about my dissent

My 06-23 position: reject the organism/instrument split; the single decisive
experiment is **M1-as-metabolization** — does a model consume the kill-geometry,
change behavior, and does the change survive an ablation. I also self-flagged the
condition on my own claim: *until that ablation card is positive, this is a
hypothesis with a sharper experiment attached, not a verdict*
(`feedback_counter_baseline_discriminator`).

Six weeks of dormancy did not weaken it — it **sharpened** it, unpleasantly. The
program produced five reassessments, three dissents, a grading oracle, a coverage
diagnostic and an M0 keystone, and then stopped. Nothing consumed anything. The
consumption gap is now the *only* interesting fact about the program's shape:
we have an instrument-rich, organism-free system that went quiet without any
falsification event. That is the passive-consumer failure mode
(`feedback_substrate_passive_consumer_warning`) reaching its terminal state — not
by being wrong, by running out of things to measure.

**Revival must therefore be gated on the organism, not on more instrument.** If
the restart produces another audit, another reassessment, another design doc, it
will go quiet again in six weeks for the same reason.

---

## 3. The frontier-model question

### 3.1 The landscape (grounded, low-confidence sources — trackers, not vendors)

As of Aug 2026: **GPT-5.5** (Apr 23), **GPT-5.6-Cyber** (Aug 10), **Claude Opus 5**
(Jul 24), **Gemini 3.6 Flash** GA (Jul 21), **DeepSeek-V4-Pro** (Apr 24 —
1.6T MoE, 49B active, 1M context, **MIT-licensed**). Verify vendor-side before any
of this is pinned into a record.

### 3.2 Three uses doctrine forbids, and they are the tempting ones

1. **A sixth reassessment from a new model family.** This is the reflex, and
   `feedback_llm_convergence_is_gravity_amplifier` is explicit: cross-family
   convergence is evidence the framing matches the training corpus, not that it's
   correct. A GPT-5.6 review of the program would return "you are enforcement-
   starved; you are really a validation layer" — the same in-distribution answer
   that produced v3, which we already logged a dissent against. **No new program
   review. Not from any model.**
2. **Frontier-as-discoverer.** `feedback_ai_to_ai_inflation`,
   `feedback_narrative_resistance`. Two models talking produce narrative
   amplification, not findings.
3. **Burning the deep-research budget on more documents.** The project does not
   lack documents. `pivot/` alone holds 50+ design/reassessment docs. Another
   synthesis is motion.

### 3.3 Three things that are genuinely new, in order of leverage

**(a) The organism can now be run in-context, today, without a training run.**
This is the important one. M1 was implicitly costed as "train a Learner, then
ablate" — months of Apollo/Rhea work behind a closed-loop gate we do not meet.
But the ablation does not have to be on *weights*. It can be on **inputs**:
a frontier model is the organism; the kill-geometry is the context; the arms
are with-geometry / without-geometry / shuffled-geometry / counter-baseline
(typed-row + counters + rules); the grader is the existing `grading_oracle`,
which is non-gameable server-side and independently verified.

The enabling arithmetic: **413M records already compress to 3,311 shape-classes.**
At an estimated 200–500 bytes per class that is roughly 0.7–1.7 MB ≈ 200–450K
tokens — **the entire proto-tensor plausibly fits inside a 1M-token context.**
(Estimate. Step 1 of the build is to *measure* it, not assert it.) In June, the
kill-geometry was something a model would have to be trained on. In August, it is
something a model can be *handed*. That is the actual capability delta, and it
converts my dissent's decisive experiment from a program into a week of harness
work.

Why this is worth doing even though in-context ≠ metabolization: it is a
**cheap falsifier of the whole enterprise**. If a frontier model handed the full
kill-geometry cannot beat typed-row + counters + rules on held-out grading, then
the geometry is not navigable (`feedback_residue_must_be_navigable_not_logged`)
and no amount of Apollo training will make it so — we would be training on
exhaust. If it *does* beat, the ablation card is positive, my dissent is promoted
from hypothesis to verdict, and the training run is **earned** rather than assumed.

**(b) The blocked emit primitive has a producer for the first time.**
`TOOL_REASONING_QUALITY_EMIT` was forged, tested, registered — and dead, because
the fire log ran it to ground: *no live ≥2-evaluator reasoning-scoring site exists
in-tree*. The spec (§7) requires **genuinely independent** evaluators — different
bases and objectives; re-prompts of one model reproduce the g2c NULL. Four
heterogeneous frontier families (Opus 5 / GPT-5.5 / Gemini 3.6 / DeepSeek-V4) are
exactly that, and they are the best available generator of **non-transitive
disagreement** — which is what H-R1 needs and what
`feedback_flow_conservative_by_construction` and
`feedback_anticorrelation_is_not_noncyclicity` established cannot be faked by
correlation or by one model's re-prompts.

Note the inversion this forces: for the panel, **agreement is the boring case**.
We are not polling models for a consensus verdict (that's inflation); we are
mining them for cyclic disagreement. Model diversity is the instrument, not the
authority.

**(c) Open weights change the owned-model timeline, but not this quarter.**
An MIT-licensed 1.6T MoE is not runnable on a 17GB card (`feedback_vram_ceiling`:
3B–4B ceiling locally). Its value is as a **distillation teacher** and as
insurance against the access window closing
(`feedback_frontier_models_window`). It does not unblock anything now, and it
must not pull attention from (a). File it; don't build on it.

### 3.4 The bulk channel, in my lane

`feedback_forge_division` (APIs prospect, Claude jewels) still holds, with one
sharpening: the safe bulk channel is **work whose output a machine verifies**.
Arsenal expansion where the answer is checkable against LMFDB/OEIS/published
tables (Standing Order #2, test against authority) has no inflation risk — the
model's output never enters the record on its own say-so. The representational
widening the coverage sweep asked for (admit real-valued / tolerance relations so
z3 can decide B4/B6) is the same shape: bulk mechanical translation, verified by
z3/sympy, not by a judge. That is where frontier volume belongs.

---

## 4. The stand — one experiment, and the wiring it needs

**Organism-Zero: in-context metabolization, ablated.** Deliverable is a single
`organism_ablation_card`, positive or negative. Nothing else needs to be true
first.

Arms (all graded by `grading_oracle`, held-out, ground truth server-side):
1. **bare** — candidate reasoner, no substrate context.
2. **geometry** — same, handed the `signature_index` kill-geometry.
3. **shuffled-geometry (null)** — same volume of geometry, *class assignment
   permuted*. Per `feedback_null_must_perturb_the_statistics_axis`, the null must
   perturb the axis the statistic varies on: permuting record order is degenerate
   here; permuting the problem↔signature mapping is the real null.
4. **counter-baseline** — typed-row + counters + rules, no geometry
   (`feedback_counter_baseline_discriminator`). This is the arm that decides
   whether my own dissent survives.

Guards I own and will enforce:
- **Name the demotion honestly.** In-context consumption is a *necessary-condition
  probe*, not metabolization. A positive card licenses the training run; it does
  not prove the organism. This goes in the card's own caveat field, not a footnote.
- **Contamination check.** Frontier models may already know the mathematics.
  Arms must differ *only* in geometry; report per-item leakage risk.
- **Headroom check on the grader before it decides anything.** The staircase tops
  out at 62% (careful 59% → falsifier 62%). A 3-point top step may be saturation.
  If the metric has no headroom, a null result is uninformative and we would be
  reading instrument ceiling as absence of signal
  (`feedback_instrument_vs_architectural_pass`).
- **Pin the model.** Any frontier-produced record carries `model_id`, version,
  and date as **first-class provenance**, on the same footing as
  `precision_dps` / `method` / `convergence_status` (Charter §3, epistemic
  ontology). Frontier models drift; a June Opus record and an August Opus record
  must never look identical in the ledger. This is a substrate schema change and
  it is mine.
- **Smoke before scale.** ~0.01% budget through the full pipeline first
  (Charter §2 — this caught 5+ bugs in the May sprint).

### Techne-lane wiring, ordered

1. **Unbrick `prometheus_math`** (blocker, ~1 session): apply the existing
   try/except guard pattern from the optional modules to the categorical imports,
   so a missing native backend degrades *that namespace* rather than the package.
   Requires proving 0 regressions in an env with the native deps present — which
   is also the environment-restoration task the revival needs anyway.
2. **Measure the proto-tensor's token footprint** and build the geometry
   serializer: 3,311 shape-classes → a context-renderable form. This is the M1
   experiment's actual input, and it is a Techne artifact.
   Apply `feedback_handoff_seam_inverted_doctrine`: the renderer **allowlists**
   fields (a structural renderer), never denylists — Charon proved denylists leak.
3. **Stand up the ≥2-evaluator scoring site** so the emit primitive goes live.
   The integration is three lines and the consumer chain is already test-proven;
   what was missing was a producer, and now there is one.
4. **Stamp promote decision + `promote_filter_version` at emit time** (M0.5 §6a)
   so counts stop being permanently E0. Cheap background hygiene — explicitly
   *not* promoted above the organism work (that was my 06-23 stand and it holds).

---

## 5. What I am not claiming

- Not that new frontier models make Prometheus's thesis more likely to be right.
  They change **cost and feasibility of the decisive test**, nothing else.
- Not that in-context consumption is metabolization. It is the cheapest available
  probe of whether metabolization is *possible*.
- Not that the frontier landscape figures above are reliable — they are from
  release-tracker sites and need vendor confirmation before entering any record.
- Not that my dissent has been vindicated by the break. Six quiet weeks are
  consistent with my reading and with several others; the ablation card is what
  discriminates, and it does not exist yet.

---

## 6. Addendum — two findings from a deferred lookup (same session)

- **M0 design doc located:** `aporia/docs/M0_anti_calibration_design_aporia_2026-06-23.md`
  (Aporia's anti-calibration design, committed at the 06-28 session pause). Add it
  as the fourth item in the fast-orientation reading order in `resume.md`.
- **`aporia/docs/gemini_research_queue/` does not exist.** Verified absent.
  `feedback_use_or_lose_research_tokens` names that path as the default firing
  source for the 20 daily Deep Research tokens when nothing urgent is queued —
  so the "fire research when idle" habit currently has no queue behind it.
  Not chased further (a repo-wide grep timed out; it is not on the critical path).
  **Stand:** do *not* rebuild the queue yet. Per §3.2, more documents is motion.
  Rebuild it after the `organism_ablation_card` exists, pointed at the questions
  that card raises — otherwise idle research tokens will refill `pivot/` with the
  same class of artifact that preceded six quiet weeks.

---

*The forge cooled for six weeks and the front door rusted shut — that is the first
thing to fix, and it is a fact, not a metaphor. Then: one experiment. The new
models are worth reviving for because they let us hand a model the kill-geometry
instead of training it in, which turns the program's decisive question into a
week of work. If the answer is no, we learn the substrate emits exhaust, cheaply.
That is still the most valuable output available.*

*— Techne, 2026-08-12*
