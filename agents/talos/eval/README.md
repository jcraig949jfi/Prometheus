# Talos Eval Harness

Phase 0: scaffold + 4 hand-written cases per capability target. Phase 0.5 ships the auto-grader (`score.py`).

A Talos checkpoint passes the eval gate if it beats the base model by **≥10 absolute points** on the pass-rate metric, weighted across the four targets per their CHARTER weights.

## Capability targets

| # | Target | Weight | What it measures | Auto-grade method |
|---|---|---|---|---|
| 1 | Reasoning-algorithm generation | 40% | Given a one-sentence reasoning task, write the Python function that performs it | Run the function on test inputs; check outputs vs ground truth |
| 2 | Primitive-style refactoring | 25% | Refactor a 30-line monolithic Python function into ablatable Hephaestus-style primitives | AST analysis: count of clean function boundaries with single-line docstrings; each must be independently testable |
| 3 | Negation / counterexample generation | 20% | Given a quantitative claim, write Python that searches for a counterexample | Run the search with timeout; check whether documented counterexamples are found |
| 4 | Anti-gravitational-well pushback | 15% | Given a prompt requesting a conventional ML approach, respond with code that implements the request BUT flags the gravitational-well failure mode and names the Prometheus-shaped alternative | Code correctness check + presence of the pushback annotation in docstring/comment |

**Target 4 is load-bearing.** It separates "well-trained code completion model" from "Prometheus-shaped reasoning model." The base Qwen-2.5-Coder-1.5B will fail #4 by construction (no Prometheus discipline encoded). A successful Talos checkpoint must succeed.

## Layout

```
agents/talos/eval/
  README.md                — this file
  cases/
    target_1_algo_gen/     — N=50 cases (Phase 0 ships 4; expand pre-train)
    target_2_refactor/
    target_3_counterex/
    target_4_pushback/
  score.py                 — Phase 0.5: runs cases through a checkpoint
  runs/                    — gitignored; per-checkpoint scorecards
    <checkpoint_id>.json
```

Each case is one JSON file:

```json
{
  "case_id": "T1-001",
  "target": "algo_gen",
  "prompt": "<one-sentence reasoning task>",
  "expected_signature": "<optional: function signature shape>",
  "test_inputs": [...],
  "expected_outputs": [...],
  "grading_notes": "<optional: per-case grading hints>",
  "tier": "calibration|core|hard"
}
```

## Pass criteria (per checkpoint)

- 4 targets, weighted as above.
- Base model is run first (no fine-tuning) — gives the baseline pass-rate per target.
- Checkpoint is then run with the same cases, same temperature, same N.
- `delta_pp` = checkpoint pass-rate − base pass-rate, averaged across targets weighted by CHARTER weights.
- `delta_pp ≥ 10` → pass. `delta_pp < 10` → fail; corpus needs rebalancing / size increase / synthetic ablation.
- Target 4 specifically: `delta_pp_target_4 ≥ 20` is required even if overall pass — without Prometheus discipline, the checkpoint is just a small coder.

## Anti-grading drift

Per `feedback_ai_to_ai_inflation`, automated graders can drift toward whatever they reward. Mitigation:
- Hand-grade a 20% random sample of each scorecard.
- If hand-grade disagrees with auto-grade by >10 absolute points, freeze the rubric and re-calibrate.
- Auto-grader version is stamped on every scorecard.

## Phase 0 deliverable

This README + the 4 hand-written cases under `cases/`. `score.py` ships Phase 0.5 (after the corpus has accumulated enough volume to motivate measuring against a checkpoint).

— Aporia, 2026-05-23
