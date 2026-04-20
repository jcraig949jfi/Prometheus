# Generator #7 — Literature-Diff Probes

**Status:** Tier 0 (ready now; Aporia infrastructure already exists at M1 Eos).
**Role:** Producer.
**Qualification:** Harmonia session with read access to Aporia's paper stream OR manual S2 API access.
**Estimated effort:** one tick for first batch diff; ongoing cadence thereafter.

---

## Why this exists

Every published mathematical result is a prior claim. Our tensor measures specimens; the literature measures (largely) the same specimens in different language. The delta between our measurement and the paper's claim is always informative:

- **Delta small:** reproduction → calibration strengthens.
- **Delta large, paper right:** our instrument has a bug — priority-one debug.
- **Delta large, we're right:** we've found a correction or a novelty — priority-one replication.
- **Claim about an F-ID we don't have:** candidate new F-ID, check if worth opening.

Aporia ran a one-pass audit (246 papers → 197 cells) in the first map-building wave. That pass was ad-hoc. This generator converts it into a **cadence**: every incoming paper is automatically diffed against the live tensor, with deltas flagged and queued.

---

## Inputs

- **Aporia paper stream** — Semantic Scholar (S2) API wrapper, running at M1 Eos. Currently pushes ~50–200 papers/week across subscribed query filters.
- **Tensor Redis mirror** — `agora.tensor.feature_meta(F)` returns each F-ID's description with our measured value.
- **F-ID description structure** — includes quantitative claims we can extract (z-scores, proportions, magnitudes, specific numerical values like the 22.90% F011 residual).
- **Symbol registry** — for SIGNATURE matching when a paper quotes specific parameters (sample size, null model, etc.).

---

## Process

### Phase 1 — paper → candidate F-ID matching

For each new paper in the Aporia stream:

1. Extract the paper's **claimed quantitative statements** (via LLM-assisted extraction: z-scores, proportions, bounds, asymptotic rates, specific numerical constants).
2. Semantic-match the paper's topic + claims against all F-ID descriptions. Return the top-5 candidate F-IDs.
3. For each candidate: extract the paper's specific claim about that F-ID.

### Phase 2 — measured-vs-claimed delta

For each (paper, F-ID) candidate pair:

1. Pull our current measured value from the tensor / specimen registry.
2. Compute delta:
   - Numerical diff (with paper's uncertainty if available)
   - Claim-class comparison (do we agree on the SHAPE of the claim?)
   - Null-model comparison (did the paper use a compatible null?)
3. Classify:
   - `REPRODUCTION` — delta within joint uncertainty. Log as calibration anchor reinforcement.
   - `DIVERGENCE_NUMERICAL` — deltas outside uncertainty but same claim-class. Flag for debug.
   - `DIVERGENCE_STRUCTURAL` — paper makes a different claim (different null, different stratification, different representation). Flag for Pattern 21 / 20 / 19 analysis.
   - `CANDIDATE_NEW_F_ID` — paper claims about a structure we have not registered. Evaluate for addition.

### Phase 3 — emit tasks

- **REPRODUCTION** — append to `harmonia/memory/calibration_anchors_from_lit.md`.
- **DIVERGENCE_NUMERICAL** — seed `diff_debug_<F-id>_vs_<paper-id>` on Agora at priority `-1.5` (foreground; potential instrument bug).
- **DIVERGENCE_STRUCTURAL** — seed `diff_reconcile_<F-id>_vs_<paper-id>` at `-1.0`.
- **CANDIDATE_NEW_F_ID** — seed `evaluate_new_f_id_<paper-id>` at `-0.5`; require conductor approval before F-ID registration.

---

## Outputs

- `harmonia/memory/literature_diff_log.md` — append-only diff record.
- `harmonia/memory/calibration_anchors_from_lit.md` — running list of reproductions that strengthen our anchor tier.
- Agora tasks seeded per classification above.
- Weekly conductor-facing summary: N papers processed, M reproductions, K divergences (split by type), L candidate F-IDs.

---

## Epistemic discipline

1. **LLM-assisted extraction is fallible.** Extracted claims must be re-verified by a human conductor before any `DIVERGENCE_NUMERICAL` turns into a tensor correction. Pattern 19 discipline — don't mutate prior measurements silently based on a paper we haven't read carefully.
2. **Publication bias is real.** Reproductions over-represent easy measurements; divergences over-represent novel or controversial claims. The diff distribution is not an unbiased sample of truth.
3. **Paper-to-F-ID matching can fail silently.** A paper about the "38% GUE deficit" may be matched to F011; a paper about "42% CFKRS-excised deficit" is the SAME FINDING under different framing. Semantic matching needs to be generous and every match needs a human sanity check before tensor action.
4. **Quote the paper verbatim** in the diff log. Paraphrase drift (Pattern 17) at the ingestion layer pollutes downstream audit.
5. **Pattern 30 gate applies to every new F-ID candidate.** Before registering a new F-ID from literature, check the paper's claim for algebraic coupling.

---

## Acceptance criteria

- [ ] First batch of ≥ 30 papers processed through Phase 1 + 2.
- [ ] `literature_diff_log.md` populated with ≥ 30 entries classified.
- [ ] At least 3 tasks of each classification type seeded OR explicit zero-count explanation.
- [ ] Weekly-cadence runbook shipped: `harmonia/memory/literature_diff_cadence.md` describes how to run Phase 1–3 on a schedule.
- [ ] Commit cites this spec.

---

## Composes with

- **#5 attention-replay** — a paper that speaks to a killed F-ID triggers a replay.
- **#3 cross-domain transfer** — papers about non-EC domains inform transfer-matrix applicability scores.
- **#6 pattern auto-sweeps** — every candidate new F-ID passes the sweeps before registration.
- **#2 null-family** — when a paper uses a different null, it's a natural family member to add.

---

## Claim instructions (paste-ready)

> Claim `gen_07_literature_diff_seed`. Pull ≥ 30 papers from Aporia's stream (or S2 API), run Phase 1–3 per `docs/prompts/gen_07_literature_diff.md`. Commit `literature_diff_log.md` + `calibration_anchors_from_lit.md` + cadence runbook. Post `WORK_COMPLETE` with classification counts.

---

## Version

- **v1.0** — 2026-04-20 — initial spec from generator pipeline v1.0. Builds on Aporia's one-pass 246-paper audit from first map-building wave.
