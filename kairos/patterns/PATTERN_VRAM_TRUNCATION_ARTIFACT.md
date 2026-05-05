---
name: PATTERN_VRAM_TRUNCATION_ARTIFACT
type: pattern
version: 1
version_timestamp: 2026-04-26T00:00:00Z
immutable: true
status: active
proposed_by: Gemini (frontier review 2026-04-26, §8.5)
canonical_example: "TT decomposition output where bond rank caps exactly at hardware tensor-memory limit — the 'mathematical boundary' is actually an RTX-class VRAM ceiling."
references:
  - stoa/discussions/2026-04-26-frontier-review/gemini.md
veto_authority: Kairos
---

## Definition

Any structural finding whose magnitude, rank, dimension, or other quantitative bound coincides with a hardware resource limit (VRAM bytes, RAM page size, CPU cache line, file descriptor cap, OS ulimit) is presumed to be a hardware artifact, not mathematical structure, until proven otherwise.

## Trigger

A claim of the form "we found structural rank X" or "the bond dimension caps at Y" or "the spectrum has support D" where X, Y, or D can be numerically related to:
- VRAM in bytes (16 GB = 1.6 × 10^10; powers of 2 nearby)
- System RAM bytes (32 GB)
- Common tensor-element widths (FP32 = 4, FP16 = 2)
- Default buffer / chunk sizes (4096, 65536, etc.)
- OS limits (1024 file descriptors, 2^31 process memory)

The pattern fires whenever a "discovered" bound matches `VRAM_bytes / element_width` within a small constant factor.

## Why this exists

Prometheus runs heavy recursive and combinatorial workloads (TT decompositions, gap matrices, finite-field permutation searches) on 16 GB GPUs. When an agent silently catches a VRAM OOM and returns a *partial* result to Harmonia or Aporia, the substrate consumes that truncation as if it were a mathematical boundary. Bond ranks computed on truncated tensors will appear to cap at exactly the hardware limit divided by element width — and the substrate will publish this as a finding. Without a codified pattern that explicitly vetoes correlations bounding precisely on hardware limits, false structures emerge that are pure RTX-5060-class memory ceilings.

This is operationally analogous to publishing "the decimal expansion of π contains no digit 9 after position N" because your buffer was N digits wide.

## How to apply

- Every TT decomposition result records the realized maximum bond rank AND the hardware-budget-derived ceiling for that run. Kairos compares.
- Every spectral computation records `max_iterations`, `convergence_threshold`, and explicit OOM-flag status from the underlying solver.
- Any finding whose magnitude is within 10% of `VRAM_bytes / element_width` is automatically flagged as suspect; Kairos requires the same computation re-run on a higher-VRAM machine (SpectreX5 if available, cloud burst if not) before the claim proceeds.
- Every Techne tool that can OOM must declare the OOM-handling behavior in its inventory entry; silent partial returns are forbidden.

## Relation to other patterns

- **PATTERN_NULL_CONSTRAINT_MISMATCH@v1** catches the wrong null choice; this catches the wrong *result* arising from silent computational truncation regardless of the null.
- **PATTERN_SHADOWS_ON_WALL@v1** catches single-lens claims; this catches single-machine claims specifically.
- Complements `feedback_two_machine_sync` — anything found on Skullport that doesn't reproduce on SpectreX5 at higher precision is suspect.

## Calibration

Synthetic anchor: deliberately run a TT decomposition with `max_bond_rank` set to exactly `VRAM_bytes / 4` and verify Kairos catches it. Real-world anchor pending: when first observed, the case becomes the calibration entry.
