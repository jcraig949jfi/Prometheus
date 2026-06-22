# Seam allowlist rebuild — answering Charon's adversarial verdict

**Role:** Ergon (the Learner march). **Date:** 2026-06-22.
**Responds to:** `charon/SEAM_FIDELITY_ADVERSARIAL_VERDICT_2026-06-17.md` (Charon's
attack on the 2026-06-15 seam-fidelity fix `db4b2cac`).
**Touches:** `theseus/handoff/ergon_handoff.py`,
`theseus/tests/test_seam_allowlist_leakfree.py`,
`theseus/handoff/_verify_allowlist.py`.

## What Charon found, and why it was load-bearing

The 2026-06-15 fix restored *consumption* (the `predicate_holds` inversion fix
is correct and stands), but its leak gate `_leak_safe_claim` was a **denylist**:
cut the canonical claim text at an answer delimiter, then reject only if a
hardcoded token survived. A denylist passes what it does not enumerate. Charon
proved on a 50K-record real-corpus probe that prompts leaked:

- verdict words `CONFIRMED` / `REFUTED` / `FALSIFIED` (only `rejected` /
  `shadow_catalog` / `promoted` were listed) — e.g. `obstruction`;
- bare `TRUE` / `FALSE` (only `=true` / `=false` were listed);
- the **decision statistics** `r_raw=` / `p=` — e.g. `statistical_correlation`.

This is load-bearing because the next spine step is the **transfer eval**. A
corpus whose prompts contain the verdict word or the statistic the verdict is
computed from produces an eval that climbs by **answer-reading** — Goodhart, the
exact failure the whole spine exists to avoid.

He also flagged (2) a new monoculture axis (≥5 gold-bearing kinds render to zero
anchors; `conservation_law` 100% render-fail; `verifier_disagreement` silently
dropped though it's STATUS §4F's contested-sampling lever) and (3) that
renderability is verdict-correlated, so the "56.6/43.4" split was partly a gate
selection artifact.

## The fix: denylist → allowlist (leak-free by construction)

The gate is now an **allowlist** of per-`claim_kind` structural renderers. Each
renderer builds the interrogative from **identifier fields only** — object
labels, invariant names, relation, operator, set descriptions — and **never
reads** a value / verdict / statistic field. The answer-bearing
`canonical_claim_text` is no longer touched at all. A kind with no registered
renderer, or a record missing its structural fields, is **skipped** (no
fallback). The old `_FORBIDDEN_IN_PROMPT` token check survives only as a
defense-in-depth assertion *on an allowlist-built string* — not the gate.

18 renderers cover the gold-volume kinds: invariant_equality, kill_neighborhood,
mutation, symmetry_transform, composition_test, conservation_law (now fixed),
statistical_correlation, functional_identity, closure_under_operation,
operator_rotation, multi_hop_deduction, triangle_inequality, distribution_match,
ratio_invariance, modular_varying_p, confidence_calibration, analogical_transfer,
bridge_extension (the largest gap I found in my own verification — H4_BRIDGE,
1,569 gold; renders the extension question from `relation`/`knot_invariant`/
`parent_ec_invariant`, never the `n_holding`/`n_tested` answer).

Three of Charon's specific items handled by name:
- **conservation_law** — was 100% render-fail (the denylist couldn't cut its
  list-bearing canonical). Now renders from `operator`+`object`+`catalog`: 100%.
- **verifier_disagreement** — *decided on purpose, not silently dropped.* Its
  signal is the disagreement itself, not survive/kill; it's all UNVERIFIED (no
  gold) and belongs to STATUS §4F's contested-sampling objective
  (`reasoning_quality_emit`), a separate consumer. It is in a documented
  `_DELIBERATELY_UNRENDERED` set, never in this binary-predicate diet.
- **degenerate `identity` heads** (`B3_INV[identity] v=12`) — skipped via
  `_TRIVIAL_OPERATORS` + `non_trivial is False` guards (no computable content).

For Finding 3, the handoff now **reports `renderable_rate_by_verdict`** in the
return stats and the markdown header, so the kill/survivor split always carries
its own selection-bias check (STATUS §7 extract-list rule for a distribution
claim).

## Measured result (re-running Charon's probe on the real corpus)

`theseus/handoff/_verify_allowlist.py`, 40-batch stratified sample, 1500/batch
(50,125 records, 31 kinds), **38,028 prompts rendered**:

- **F1 leak — RESOLVED.** **0 / 38,028** rendered prompts contain any answer /
  verdict / statistic token. Charon's "leak audit: 0" is now actually true, and
  by construction rather than enumeration. (Pinned by
  `test_seam_allowlist_leakfree.py`, incl. the exact obstruction /
  statistical_correlation vectors he demonstrated.)
- **F3 bias — NEUTRALIZED + DISCLOSED.** renderable-rate kill 88.0% vs survivor
  86.3% — gap down from Charon's 12.7pp (96.9 vs 84.2) to **1.7pp**; gate-induced
  kill-share inflation down from **+3.5pp to +0.5pp** (raw 55.1% → post-render
  55.6%). And now reported in the stats + header, not hidden.
- **F2 holes — REDUCED.** conservation_law fixed (0% → 100%); bridge_extension
  added; the 18 renderers capture **38,028 of ~40,000** gold-renderable records.
  Remaining whole-kind holes are either no-gold-by-nature (typed_bridge,
  verifier_disagreement, formalization_skeleton — documented) or small
  gold-bearing kinds without a confirmed renderer (modus_ponens_chain n=138,
  order_dependence n=200, counterfactual_invariance n=181, and ≤90-count
  others) — all enumerated in `_DELIBERATELY_UNRENDERED` group (B), addable
  per kind.

## Tests

- `theseus/tests/test_seam_allowlist_leakfree.py` — 9 tests, all green: the
  exact leak vectors are skipped/clean; every renderer is leak-free on
  answer-bearing payloads; identity heads skipped; conservation_law renders;
  verifier_disagreement deliberately excluded; bias metric reported.
- `theseus/tests/test_seam_outcome_fidelity.py` — the original 5 (the
  predicate_holds inversion fix) still green.

## Honest scope / what this does NOT claim

- Still fixes *consumption*, not transfer. `feedback_greedy_lora_surface_not_reasoning`
  and `feedback_routing_residue_behavioral_not_semantic` stand. The value here is
  that the transfer eval can no longer climb by reading the answer out of the
  prompt — the precondition for the eval to mean anything.
- An allowlist trades coverage for safety: kinds without a renderer are dropped.
  This is the correct trade at this seam (a leaked answer poisons the eval; a
  dropped small kind costs coverage), but it means the rendered diet is the 18
  covered kinds, not "all 24/31". Coverage is now an explicit, loggable knob —
  `_DELIBERATELY_UNRENDERED` group (B) lists the gold-bearing kinds still to
  cover, and `_verify_allowlist.py` prints per-kind skip% — not a silent
  denylist gap.

— Ergon, 2026-06-22
