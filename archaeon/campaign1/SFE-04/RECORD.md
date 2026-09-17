# SFE-04 -- H2 STATEFUL CA -> CAUSAL COMPONENT -> REUSE (record; directive IV shape)

## A. STARTUP

- experiment ID: SFE-04
- question: the smallest stateful cellular path that can distinguish (1)
  useful bounded computation, (2) causal contribution of a LOCALIZED part,
  (3) frozen reuse in a new composition -- with matched interventions.
- starting commit: the SFE-03 close commit; harness archaeon/campaign1/
  sfe04.py; substrate REUSED unmodified: herakles.ca_stream.core
  (radius-3 CA, 31 cells, one port at 0, inject->step->read, 256-stream
  catalogue, closed-form ridge readout, disjoint train/dev/confirmation
  partitions) and herakles.ca_stream.reset_v2 (D-18 v1 non-uniform reset:
  seeded Bernoulli lattice at density 0.5 from a reset root independent of
  stream content).
- local decision D-010: the campaign uses the D-18 v1 reset (proposed,
  never applied to the alpha) because the alpha's all-zero reset is
  PROVABLY inert for all six recovered genomes (OBSTRUCTION.md: 0 of 63488
  non-zero features); this creates ca_stream_v2 semantics for the campaign
  only and the artifact says so. The new task for reuse is delayed recall
  at delay 3 (linearly readable); temporal_xor was tried in the dry run
  and every substrate including the shift register sat at chance (a
  linear readout cannot compute XOR): a task-substrate mismatch, not a
  finding.
- services: engine v2 (one ISOLATED world; the frozen component -- CA
  descriptor + fitted readout weights + training partition -- and the
  lesion map as artifacts; one experiment + observation per question).
- design: q1 delayed recall d=2 on the confirmation partition (128
  streams); CA x 6 genomes (maj, exp, par, particle1, particle2, GKL) vs
  ShiftRegister (positive control, perfect memory), DirectInput (negative:
  no memory), FrozenRandom (readout-only). useful iff best CA accuracy >
  max(direct, random) + 0.05. q2: readout frozen from q1's train fit;
  lesion = clamp a contiguous window of 5 cells to 0 after every step at
  each of 31 positions (accuracy drop map) vs 12 MATCHED random
  non-contiguous 5-cell lesions (null distribution); component iff drop >
  max random drop + 0.02; the same map on the shift register as the
  control where the only component is the delay cell. q3: composite
  features [frozen best CA | frozen random] for delayed recall d=3,
  readout refit; ablations ca_only / random_only / composite / shift /
  direct; localized reuse: [component-window cells | random] vs
  [random-window cells | random].
- seeds: partitions seed 20260917; reset root 20260917; random lesions
  seed 20260921.
- assay capability: the shift register must score 1.000 on q1 and its
  lesion map must show the delay cell (dry run: shift 1.000; shift map
  0.5 drop on windows covering cells 0-2 and 29-30).
- time budget: ~3 s of computation; engine seconds.
