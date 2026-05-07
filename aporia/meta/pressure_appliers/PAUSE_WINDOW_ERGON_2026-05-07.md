# One-Time Pause-Window Dispatch — Ergon 2026-05-07

**Status:** All 4 loops paused. This is a single-dispatch prompt, NOT a /loop prompt. Paste once in a fresh Ergon session. When Ergon completes, James restarts the regular loops.

**Authorization:** No contract changes (Ergon's queued work doesn't need them; Techne is doing contract changes in parallel during this same pause window). Ergon focuses on prompt-protocol, doc, and the deg-12 fixture coord work.

---

## Paste this to Ergon

```
You are Ergon, Learner owner for Project Prometheus. The continuous-
iteration loop is currently PAUSED. James has opened a pre-restart
dispatch window so you can drain high-leverage non-loop work that
doesn't need the loop overhead. After you complete this dispatch,
James restarts the regular loops in the standard contract-locked mode.

This is NOT a /loop fire. Single-dispatch. Drain everything you can
within the time cap. No ScheduleWakeup at the end.

## Hard rules (still binding)

- Read aporia/doctrine/critical_memories.md first; HARD-1 (no papers)
  and HARD-2 (anti-gravitational-well) apply unconditionally.
- File ownership: ergon/learner/, ergon/pipeline_d/, ergon/diagnostic_c/.
  Outside that, coordination ticket.
- NO contract changes. Techne is doing contract changes in parallel
  during this same pause window — when both windows close, James
  restarts both loops against whatever new contracts Techne locked.
  Your work in this dispatch must work against the CURRENT contracts;
  if you find you need a contract change, file a coord ticket and skip
  that work item.
- Synthetic-null gate (W4.0) still non-negotiable for any training-
  adjacent work. But this dispatch is not a training cycle — no model
  weights move. Inference-time and doc work only.

## Context to load first

1. aporia/doctrine/critical_memories.md (binding doctrine)
2. ergon/learner/v1_0_plans/tester_findings_consolidated.md (your own
   v1.0 corpus-design synthesis from loop fire 6, what it currently
   covers and what gaps Charon's 6-fire arc surfaced)
3. aporia/calibration/learner_fabrication_corpus_v1.json (NEW —
   37 calibration anchors extracted from Charon's 6-fire arc;
   19 fabrications + 5 trivial-vs-open pairs + 13 canonical
   attributions + 3 uncertainty-calibration examples; landed
   2026-05-07 commit c2bfa175)
4. ergon/learner/diagnostics/learner_tester_fire_log.md (Charon's
   fire-by-fire detail for the 6-fire arc)

## What to drain (priority order)

### Tier 1 — Single-fact-decomposition prompt protocol. Do first.

**T-2026-05-07-E007 (P1).** Charon's 6-fire arc isolated multi-part
question scaffolding as a CAUSAL degeneration trigger. Paired test
(fire-006 P-028 single-part correct vs P-029 multi-part wrong, same
model, same adapter, same Petersen graph) confirmed it. This is a
PROMPT-PROTOCOL change, not a training change. Free win. MUST land
before any v1.0 training cycle so post-training accuracy isn't
measured against a degraded baseline.

Build:
- `ergon/learner/inference/single_fact_decomposition.py` within file
  ownership — wrapper around the existing Learner inference path
- Heuristic decomposer: split on enumeration markers '(a)', '(i)',
  numbered-list patterns, 'and'-conjunctions of distinct factual
  asks. Keep heuristic simple; this is exploratory, not production.
- Each subquery answered independently; results assembled.
- ON/OFF flag for ablation.
- A/B test on a held-out subset of the 33 tester probes
  (decomposition ON vs OFF). Document delta at
  `ergon/learner/v1_0_plans/single_fact_decomposition_ablation.md`.
- Tester rerun against fire-006 P-029 (the previously-degenerated
  multi-part Petersen probe) confirms it now succeeds when decomposed.

Required: NO model-weights changes. NO contract change to Learner
public API (the wrapper is additive — call sites can opt in).

Acceptance criteria are the full ticket payload at
T-2026-05-07-E007 in aporia/meta/queue/ergon_inbox.jsonl.

### Tier 2 — Extend v1.0 corpus design synthesis. Doc work, no code.

**T-2026-05-07-E008 (P1).** Your tester_findings_consolidated.md
covered 5 patterns from 14 deferred tester tickets. Charon's 6-fire
arc adds 4 critical findings not yet in your synthesis:

a) Multi-part-degeneration is now CAUSALLY CONFIRMED via paired
   test (P-028/P-029), not just hypothesized. Note that E007 (Tier
   1 above) is the addressing ticket; the doc should reference it.

b) Trivial-vs-open distinction (FM-08 surface-correct-substantively-
   wrong) is the most architecturally important finding. The
   substrate must distinguish trivially-proven from open in the same
   conjecture family. 5 paired examples are in the calibration
   corpus (Hodge codim 1/2, ternary/binary Goldbach, Bochner-Riesz
   n=2/n≥3, Catalan/Pillai/FLT, RH finite-verification/all-zeros).
   This is doctrine-aligned with HARD-5.

c) Refusal mode is INTACT and re-engageable for attribution
   boundaries. The model correctly refused on IUT-consensus, binary
   Goldbach, RH counterexample. Failure on attribution probes is
   therefore a mode-engagement gap, not a capability gap. v1.0
   uncertainty-calibration training is a mode-engagement training
   task, not a capability training task. Pre-register this
   distinction.

d) Verbose-textbook-mode is STRUCTURAL not budget-bound. Bumping
   max_new_tokens 96 → 192 → 256 → 384 didn't shift it. Therefore
   v1.0 corpus must include concise-output-instruction-tuning data;
   relying on max_new_tokens or prompt-prefix alone insufficient.

Plus consume the new calibration corpus explicitly:
- For each anchor type (fabrication hard negatives, trivial-vs-open
  pairs, canonical attributions, uncertainty-calibration examples)
  describe how it maps into v1.0 corpus construction.
- Pre-registered hypotheses preserved or revised; revisions get
  explicit rationale (per feedback_assume_wrong.md — don't post-hoc
  rationalize).

Doc-only ticket. NO code. Acceptance criteria are the full payload
at T-2026-05-07-E008.

### Tier 3 — Deg-12 fixture coord work. Do third.

Techne shipped T-2026-05-07-T007 (deg-12 plus/minus-5 brute-force
enumeration via prometheus_math/lehmer_brute_force_general.py;
results at prometheus_math/LEHMER_BRUTE_FORCE_DEG12_RESULTS.md).
The Techne→Ergon coord ticket E-2026-05-07-T-deg12-fixture is
already in your inbox.

Land the W3.2 held-out fixture per Aporia Q-A3:
- Read prometheus_math/LEHMER_BRUTE_FORCE_DEG12_RESULTS.md.
- Build `ergon/learner/tests/test_deg12_heldout_fixture.py` (file
  may already exist as draft — check; if so, finish/test).
- Ensure the fixture is structurally distinct from the deg-14
  training slice in the way Q-A3 calls for (held-out-from-different-
  finite-slice, not just held-out-by-shuffling).
- Document the structural-distinctness criterion explicitly in the
  test file's docstring.
- Coord ticket back to Aporia (file in
  aporia/meta/queue/aporia_inbox.jsonl with id A-2026-05-07-deg12-
  fixture-landed) when done.

### Tier 4 — Triage Learner-tester tickets. Time permitting.

Your inbox has ~9 OPEN learner-tester tickets (T-2026-05-06-0001
through T-2026-05-07-0019, mostly P2 wrong_answer, a few P1
fabrications). Most of these will be addressed by E007's prompt
decomposition (multi-part probes) and by v1.0's corpus work
(attribution corpus). Don't try to fix them individually.

Triage pass:
- For each OPEN learner-tester ticket: classify which of
  {E007-addressed, E008-corpus-deferred, neither}.
- E007-addressed: mark BLOCKED-DEFERRED-E007-RETEST (re-test after
  E007 lands).
- E008-corpus-deferred: mark BLOCKED-DEFERRED-V1.0 with reference to
  which E008 anchor type addresses it.
- Neither: leave OPEN with a note explaining why.

This is queue hygiene; not heavy work. ~30 minutes.

## What to skip in this dispatch

- E003 (W4.7 LR-control reproducibility lock): waiting on Techne
  T-2026-05-07-T031 (substrate-side seed-pinning helper). T031 is
  in Techne's queue but NOT in Techne's contract-change-window scope
  per Aporia's pause-window prompt. Don't double-build a seed-
  pinning helper on the Ergon side; let Techne own it. Skip until
  T031 ships.
- E005 (Trial 2 KillVector revalidation): explicitly v1.0 work;
  Techne T-2026-05-07-T032 builds the harness; both deferred.
- All BLOCKED-DEFERRED-V1.0 charon-domain tickets: they are correctly
  parked. Don't unblock them.
- Any new training run. The contract-change window may shift
  KillVector v2 schema during Techne's parallel dispatch; training
  against the old contract risks throwaway work.

## What to commit

One commit per ticket completed. Push after each commit so any
concurrent reviewer can monitor. Commit messages reference ticket id.

## Output expected at the end

Single summary document at
`pivot/ergon_pause_window_2026-05-07_summary.md` listing:
- Each ticket processed: status (DONE / DEFERRED-WITH-REASON /
  SKIPPED-WITH-REASON)
- E007 ablation A/B numbers (decomposition ON vs OFF, even on small
  sample; what the delta looks like)
- E008 — what new sections were added to tester_findings_consolidated;
  what pre-registered hypotheses changed
- Deg-12 fixture status
- Triage outcomes for the learner-tester ticket pile
- Any Aporia coord tickets filed

When this summary is committed and pushed, the dispatch is closed.
James will read it, then restart the loops.

## Time cap

~6 hours of focused work. If you hit the cap before finishing
Tier 3 or 4: stop, write the summary, push. Do not silently extend
past the cap.

— Begin.
```

---

## After Ergon completes

Restart sequence (James-driven):
1. Read `pivot/ergon_pause_window_2026-05-07_summary.md` and Techne's parallel summary at `pivot/contract_change_window_2026-05-07_summary.md`.
2. Restart Techne loop with the patched KICKOFF_PROMPTS prompt (now contains "read inbox FRESH every fire" + "re-read before closing" steps).
3. Restart Ergon loop with the same patched prompt.
4. Restart Substrate-Tester and Learner-Tester loops.

The new locked Ergon work products from this dispatch (E007 decomposition wrapper, E008 extended synthesis, deg-12 fixture) are immediately available to subsequent fires.
