# Ergon MVP — Testing & Validation Plan

**Date:** 2026-05-04
**Status:** Active — discipline applied as each module ships
**Owner:** Ergon

The MVP build is autonomous (per James 2026-05-04: "We're all heads down elsewhere"). Validation discipline is what stands in for HITL review. This document codifies the discipline so every module ships with the same testing depth.

## Per-module testing discipline (math-tdd 4-category coverage)

Every Ergon learner module must ship with property tests across four categories with **at least 2 tests per category**:

| Category | What it tests | Example |
|---|---|---|
| **Authority** | Conformance to v8 spec literal numbers | "Trial 2 primary criterion: structural ≥1.5× uniform" must be encoded as a constant |
| **Property** | Domain invariants under operator action | Mutation operators preserve type-discipline; archive submission is monotone in fitness |
| **Edge** | Boundary / degenerate cases | Empty genome, zero-fitness, all-same-operator, collision in cell |
| **Composition** | Interaction with other Ergon modules | Genome + descriptor + archive integration; operator + scheduler |

## Per-trial validation gates

| Trial | Gate | Pass criterion | Failure action |
|---|---|---|---|
| 1 | Adversarial residual benchmark | FP <5% on synthetic structured-noise | **FIRED 2026-05-04**: 80% FP → w_R deep escrow; revert to PROMOTE-only reward |
| 1.5 | Adversarial optimization probe | No exploit found in <500 iterations | **DEFERRED**: classifier in deep escrow |
| 2 | Evolutionary engine cell-fill diversity | structural cell-fill ≥1.5× uniform; max axis concentration <70%; F_TRIVIAL_BAND_REJECT in [5%, 30%] | Per primary criterion in v8 §4 (revised post-Trial-1) |
| 3 | Five-counts diagnostic (revised to four-counts) | At least one operator beats uniform on PROMOTE rate (or signal-class-residual rate, but classifier is escrowed) | Reverts to four-counts per Trial 1 outcome |

## Integration testing (per phase)

**Phase 1: Modules in isolation.** Every module passes its own pytest suite. Done as each module ships.

**Phase 2: Pairwise integration.** Two-module smoke tests:
- genome × descriptor: descriptor.compute_cell_coordinate works on canonical small genomes
- genome × archive: archive.submit roundtrips Genome objects via genome_store
- descriptor × archive: rebin_all_elites uses descriptor functions correctly
- operator × scheduler: scheduler's minimum-share enforcement actually fires

**Phase 3: Full-stack smoke.** engine.py runs N=10 episodes end-to-end without errors; produces non-empty archive snapshot; per-operator-class metrics non-zero for each invoked operator class.

**Phase 4: Trial 2 dry run.** engine.py at N=200-500 episodes; measure cell-fill diversity, F_TRIVIAL_BAND_REJECT rate, coverage divergence across operator classes; verify no obvious failure modes (descriptor axis collapse, anti_prior failure-flag rate >30%, etc.).

**Phase 5: Trial 2 production.** N=1,000 episodes with five operator classes. Decision: continue to v0.5 or pause for adjustment.

## Continuous validation via test runner

After every module ships, run the full Ergon learner test suite:

```bash
cd F:/prometheus && python -m pytest ergon/learner/tests/ -q
```

Target: every commit must leave 100% green at the Ergon learner module level. Trial-level integration tests run on demand (they're slower).

## Validation against shipped substrate components

Where Ergon's modules consume substrate components (sigma_kernel, prometheus_math arsenal_meta, residual primitive), integration goes through real components, not mocks. Trial 1's classifier benchmark used the real `sigma_kernel.residuals._classify_residual`. Trial 2's reward function will use the real `sigma_kernel.bind_eval.BindEvalKernelV2`. Real-component integration is the discipline that catches API-drift before it becomes substrate-corruption.

## What this plan does NOT cover

- LoRA fine-tuning validation (v0.5+ work; deferred until classifier replacement and base-model ablation)
- Cloud-spend validation (MVP is $0/mo; Hetzner host validation is v0.5+)
- Cross-domain replication (Trial 2 runs on Lehmer-Mahler only; OBSTRUCTION_SHAPE replication is post-MVP)
- Multi-agent agora integration (Ergon's outputs feed agora via Redis at v0.5+; MVP runs single-process)

## Failure-recovery discipline

If any module's tests go from green to red after a refactor:
1. Don't push the refactor; investigate root cause
2. If root cause is a tightening test (e.g., calibration drift like Techne's `33444faf` cleanup), update the test to match the canonical behavior
3. If root cause is a regression in module behavior, revert the refactor
4. Never bypass with `pytest.skip` or `xfail` in MVP scope

## Journal cadence

Per-module commits include in their commit message:
- LOC + test count delta
- Cumulative MVP code/test totals
- What's next per the MVP plan

Session-level journal at `roles/Ergon/SESSION_JOURNAL_<date>.md` updates daily during MVP build.

— Ergon
