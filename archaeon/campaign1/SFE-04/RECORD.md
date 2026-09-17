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

## B. EXECUTION

- one attempt (RECEIPT.json; 5.5 s total: startup 0.49, q1 0.69, q2 2.58,
  q3 0.00, records 1.47, teardown 0.22; 0 errors). Engine: 1 session, 1
  world, 1 hypothesis, 2 artifacts (frozen component = CA descriptor +
  readout weights + train partition; lesion map), 3 experiments + 3
  observations. Dry run first (D-010 arose from it: temporal_xor replaced).
- reset-leakage probe NOT run (reset_v2.reset_leakage_probe's signature
  was not read; recorded as leak=None) -- L-019. The leakage risk is
  bounded by construction (reset seed from position, not content) but
  unverified here.

## C. SCIENCE

- q1 USEFUL BOUNDED COMPUTATION (delayed recall d=2, confirmation
  partition 128 streams x 6 defined steps; base rate 0.500):
    {'ca:GKL': 0.501, 'ca:exp': 0.52, 'ca:maj': 0.499, 'ca:par': 0.547, 'ca:particle1': 0.562, 'ca:particle2': 0.608, 'direct': 0.5, 'random': 0.5, 'shift': 1.0}
  best CA = ca:particle2 at 0.608; shift register 1.000 (positive
  control), direct input 0.500 (no memory), frozen random 0.500 (readout
  only). useful = TRUE (0.608 > 0.500 + 0.05), weakly: a linear readout
  recovers ~11 points of delayed information from the lattice.
- q2 CAUSAL CONTRIBUTION (frozen readout; 5-cell window clamped to 0 after
  every step): lesion map max drop 0.108 (window at 30), top five windows
  [('30', 0.1081), ('0', 0.0977), ('4', 0.0977), ('8', 0.0977), ('3', 0.0964)]; MATCHED random non-contiguous 5-cell lesions: drops
  [0.0703, 0.0964, 0.056, 0.0911, 0.0938, 0.0938, 0.0404, 0.0365, 0.069, 0.0508, 0.1133, 0.082] (max 0.1133).
  components = []: NONE. Every window costs about what
  any five cells cost: the delayed information is DISTRIBUTED across the
  lattice, not localized. Control: the same map on the shift register
  drops 0.500 exactly on the windows covering the delay cell and 0
  elsewhere -- the instrument localizes when there is something to
  localize.
- q3 FROZEN REUSE (new task delayed recall d=3; readout refit):
    {'ca_only': 0.583, 'component_window+random': 0.578, 'composite': 0.578, 'direct': 0.483, 'random_only': 0.483, 'random_window+random': 0.591, 'shift': 1.0}
  The frozen CA carries d=3 information (ca_only 0.583 vs random_only
  0.483, direct 0.483); composing it with a frozen random substrate adds
  nothing (0.578); localized reuse: component-window+random 0.578 vs
  random-window+random 0.591 -- no window is special, consistent with q2.
- evidence: (1) useful bounded computation: WEAK POSITIVE; (2) localized
  causal component: NEGATIVE with a working positive control (the
  computation is distributed); (3) frozen reuse: POSITIVE for the whole
  substrate on a neighbouring task, NEGATIVE for a localized component.
- confounders: one CA genome family (six recovered genomes), one port, one
  reset density, one window width; ridge lambda fixed; accuracy 0.58-0.61
  on a 0.50 base rate is small; no seeds over the reset root (one root).
- must NOT be claimed: that CA reservoirs "have" reusable components
  (none found); that the substrate computes beyond a linear readout's
  reach (untested); that 0.61 is more than a weak memory trace.

## D. TEARDOWN

- 1 world TERMINATED (0.22 s); no orphans; artifacts remain on the ledger
  (append-only). Clean start for SFE-05: yes.

## E. BENCH IMPROVEMENT

BUGS: none. FRICTION: the reuse task had to be changed after a dry run
(temporal XOR not linearly readable) -- the readout class and the task
class are coupled and nothing declares which tasks a readout can express
(L-020). MISSING TELEMETRY: L-019 (leakage probe not wired); the lesion
map is a landscape and should be a standing output of any reservoir run.
AUTOMATION: the whole path is 5.5 s and deterministic; the matched-random
lesion null is the piece that should become a library function.
TO MACHINERY: matched-lesion null (12 random lesions of matched size) as
the default causal test for any "component" claim. KEEP POLICY: window
width, reset density, task/delay. MISSING FAILURE STATE: "readout cannot
express task" (L-020) -- the shift register at chance is the detector.
MISSING RECOVERY: none. PORTABILITY: none. OBSERVABILITY: none new.

## F. LANDSCAPE / GRADIENT NOTES

- The lesion map IS a landscape (31 positions x drop) and it is flat at
  ~0.10 with a random-lesion band of 0.04-0.11: a distributed code. The
  interesting axis not measured: window width (1, 3, 5, 9, 15) -- the
  width at which the drop first exceeds the random band would give an
  effective "code length"; and delay (1..6) x genome (6) would give a
  memory-depth landscape per rule. Both are minutes of compute.
- q1 across genomes (0.50-0.61) is a gradient over rules: exp (0.52,
  nonzero share 0.20) and maj (0.50, near-saturated lattice) sit at the
  two dead ends (too quiet, too dense) with particle rules in between --
  the density-of-activity axis predicted by OBSTRUCTION.md.

DISPOSITION: COMPLETE. Science: useful computation weak positive; no
localized causal component (distributed); whole-substrate frozen reuse
positive on a neighbouring task. Instrument: engine path 0 errors.
