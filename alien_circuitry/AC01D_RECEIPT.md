# AC-01D-v1 final receipt (2026-09-13)

## Verdict (in the ruled language)

**AC-01D-v1 POSITIVE within frozen scope.**

In T_7 with rank-2 targets, after exact reachability is supplied by the known kernel invariant, compact structured
representations can capture navigation-relevant shortest-path geometry that exact row quotients, ordinary features,
and matrix low-rank completion do not. CP rank 16 captures roughly 55% of residual transition headroom with a
~1.7 KB representation; an evolved 24-expression DSL captures roughly 54% with ~1.4 KB; a ~227 KB learned digit
representation captures roughly 91% on unseen targets and unseen states with zero verification failures.

The learned representation is slower than explicit kernel-aware search at this scale, and its internal
mathematical structure is not yet characterized.

Scope statement (frozen): this is a statement about T_7 and rank-2 targets. It does not license "distance geometry
of transformation monoids is compressible". Rank-3 targets and n = 8 are separate replications.

## Provenance

Branch `alien-circuitry/phase-ab-2026-09-12` on `origin/main` 890c4d452, unpushed. Freeze commit 95f22c8
(`PREREGISTRATION_AC01.md`, `results/ac01d/FREEZE.json`). Family result commits: dff9a5e (C3/C4), 7ed2c17 (C1),
d8ec63a (TT/Tucker), 6694cbf (CP), 25ad9f6 (C5), 5a04706 (C5 controls), f462822 (C6 + forensic audit),
d84c9d0 (CP persistence), 517034d (dissection). Corpus hashes re-verified identical after a memory patch
(46963f0). Tests: 28 pass. Host incidents: three C6 runs and three earlier gate runs killed by host memory pressure
(an orphaned 6.5 GB `tail.exe` and the WSL VM); process-recovery provenance at
`results/ops/process_recovery_pid20436.json` (the PID was gone at check time; nothing was terminated by this seat).

## Frozen matrix, filled

```
Family / model                 Bytes     CR    HELD_STATES        HELD_TARGETS       HELD_BOTH          Band / class
----------------------------   -------   ----  ----------------   ----------------   ----------------   ------------------------------
C3/C4 exact quotient, sigs.    4.6-15.6M <0.25 n/a                n/a                n/a                KILLED (no row redundancy)
C1 masked low-rank             0.85-6.8M <1.25 n/a                n/a                n/a                KILLED (HC_D -2.3 on pairs)
C2 CP rank 16 (persisted)      1,708     621   0.61 [0.58,0.65]   0.55 [0.52,0.60]   0.57 [0.51,0.59]   MEANINGFUL, CR>=4, dominates KA-DFS
C2 CP rank 32                  3,312     320   0.45               0.45               0.43               meaningful
C2 TT rank 16 run 1            26,324    40    0.54 [0.49,0.58]   0.36 [0.27,0.43]   0.39 [0.31,0.46]   weak-but-real cross-target
C2 TT rank 16 run 2 (persisted) 26,344   40    0.45               0.46               0.43               meaningful (run-to-run +-0.1)
C2 Tucker k=2                  30,996    34   -0.08              -0.26              -0.37               no useful compression
C5 small (31,609 params)       58,772    18    0.67               0.57               0.59               meaningful, CR>=4
C5 medium (124,657 params)     226,956   4.7   0.91 [0.89,0.92]   0.91 [0.90,0.92]   0.91 [0.90,0.92]   STRONG, CR>=4, excess 0.0
C6 evolved DSL (24 trees)      1,428     743   0.59 [0.55,0.62]   0.54 [0.50,0.58]   0.54 [0.50,0.58]   MEANINGFUL, CR>=4, symbolic
```

All values: kernel-aware best-first (GBFS) HC_D on transitions, 300 problems per set, zero failures everywhere.
DFS-ordered variants are in the JSON (C5 medium 0.95; CP r16 0.43-0.49; C6 0.47-0.51). Wall-clock: C5 medium costs
0.19-0.47 ms per decision against 0.56 us per transition expansion; at this scale every representation is far
slower than kernel-aware explicit search. The positive claim is fewer symbolic transition examinations and more
compact navigation information, not faster reasoning.

Reproducibility note: TT is the only family whose fitting is not bit-reproducible (GPU Adam); the persistence rerun
with the same seed gave VAL RMSE 1.365 vs 1.386 and cross-target HC_D 0.46/0.43 vs 0.36/0.39. Both runs are committed;
the family's cross-target band is reported as straddling 0.40 with run-to-run variation of about 0.1. CP (ALS,
deterministic) and C6 (seeded CPU) reproduced within bootstrap noise; C5 was not re-fitted (ruled).

Selection note: the frozen text lets VAL steer hyperparameters without naming the criterion. For CP, VAL RMSE
selects rank 32 and VAL navigation selects rank 16; both are above the 0.40 line and both are reported. No sweep
was extended after held results were seen; TT was left at rank 16 with VAL RMSE still falling; C6 was left at its
24-stage budget with VAL RMSE still falling.

## Forensic audit (C5-medium, `results/ac01d/forensic/C5_medium_audit.json`): PASS

- Provenance: 0 of 4,289,843 FIT rows contain any of the 13 held targets; VAL objects are val states x train targets;
  the only target-independent statistic derived from D is the scalar FIT mean (16.7334, re-derived).
- Serialization: 20 float16 tensors matching the declared architecture exactly, 124,657 parameters, no extra
  tensors, no integer tables, 255,759 bytes on disk (226,956 after lzma).
- Isolated evaluation: a subprocess importing no project module and never holding D reproduces exact-match 0.896 /
  R^2 0.988 on 200,000 HELD_TARGETS rows and 0.898 / 0.988 on HELD_BOTH.
- Relabelling: state and target ids never cross the process boundary; the same digit rows reordered give
  predictions differing by exactly 0.0.
- Label-permutation control (earlier): the same architecture trained on permuted D collapses to chance.

## C5 frozen for interpretation

Weights `results/ac01d/families/weights/C5-medium-D.pt` sha256 ab5819601c258cba…; reachability head
`C5-medium-R.pt`; architecture = `families/c5_learned.DigitNet(16, 256)` (14 embeddings of width 16, two ReLU
layers of 256, scalar output, predicts D minus 16.7334); isolated inference script sha256 cbe26c6e52639dd3….
No further fitting of this model is permitted.

## What the frozen C5 computes (`results/ac01d/interpret/C5_dissection.json`; 60k/60k HELD_BOTH rows)

Frozen ridge probes (R^2 unless noted; the RAW column is the same probe from one-hot digits, so a quantity is
"represented" only where a layer beats RAW):

```
quantity                     RAW digits   L0 embed   L1 relu   L2 relu
rank(f)                          0.004      0.004     0.997     0.916
count vector of f                1.000      1.000     0.994     0.944
block-size multiset of f         0.003      0.003     0.424     0.439
kernel bits of f (21)  R2/acc  0.085/0.90  0.085/0.90 0.26/0.91 0.17/0.90
kernel bits of t (21)  R2/acc  0.742/0.91  0.742/0.91 0.92/0.995 0.80/0.96
rank(f) - rank(t)                0.004      0.004     0.997     0.916
exact D                          0.077      0.077     0.689     0.990
successor D minus D (3)          0.117      0.117     0.325     0.493
shortest action (one-hot)  acc   0.80       0.80      0.84      0.88
```

Findings, mapped to the ruled hypotheses:

- M1 (kernel rediscovery only): rejected. The kernel-aware baseline already has the invariant and sits at HC_D 0;
  the model's own value is 0.91.
- M2 (rank/count refinement): rank and the rank difference are computed exactly by the first hidden layer (R^2
  0.997 from a linear probe, 0.004 from the raw digits), so the network builds the permitted scalar summaries
  internally. But those summaries explain only R^2 ~0.45-0.62 of D by the earlier feature-model baseline, and the
  model reaches 0.99, so M2 is necessary and not sufficient.
- M3 (explicit partition reconstruction): weak. The 21 source-kernel bits are only linearly decodable at R^2 0.26
  (bit accuracy 0.91 against a 0.90 majority baseline) from any layer; the network does not linearly represent the
  full source partition. The target partition is decodable (0.92 at L1), but that is nearly readable from the raw
  target digits already (0.74). The reachability head, trained separately, does reach PR-AUC 0.99997, so the
  partition relation is computable by this architecture; the distance head does not appear to expose it linearly.
- M4 (target-conditioned alignment) and M5 (approximate word metric): consistent with the data but not
  separated by these probes. D becomes linearly readable only at the last layer (0.69 at L1, 0.99 at L2), i.e. the
  network's penultimate representation is a coordinate system in which shortest generator distance is nearly linear;
  successor-D differences and the shortest action are only partially linear there (0.49, 0.88), so the navigation
  signal is carried mostly through D itself, not through an explicit action-preference code.
- Ablations (no retraining, HELD_BOTH): zeroing any single source-digit embedding drops D R^2 from 0.988 to
  0.62-0.67 and shortest-action top-1 from 0.888 to 0.73-0.81; zeroing any single target-digit embedding drops R^2
  to 0.69-0.75. No hidden unit group of 16 does more than 0.15 of damage (worst h1 group: 0.847). Reachability
  (R head) is damaged more by source digits 1 and 3 (PR-AUC 0.66-0.68) than by target digits (0.74+). The
  computation is distributed: there is no small subspace controlling either D or reachability, and every position
  matters roughly equally, which is what a permutation-sensitive but position-symmetric geometry predicts.
- Symmetry (ruled section 10): the model is NOT invariant under simultaneous value relabelling. Under the 20
  relabellings that fix {0,1} setwise (which preserve the generator set and therefore the true metric exactly),
  predictions change by 2.05 on average, 5.19 at the 95th percentile, and 82% of rows move by more than 0.5. The
  model learned the geometry in the fixed digit convention it was trained in, not the intrinsic semigroup
  geometry. This is the most important negative interpretive finding: C5 is a table-like function of the specific
  symbols, generalising across unseen combinations of them, and not an equivariant model of the action.
- C5 versus CP rank 16 (60,000 HELD_BOTH rows): CP is exact on 20.5% of rows, C5 on 89.7%; C5 is exact on 97.5%
  of the rows where CP is wrong; error correlation 0.04; C5 explains R^2 0.974 of CP's residual. The subsets do not
  differ in mean D, rank, or rank difference (all within 0.3), so the geometry C5 adds is not concentrated in an
  identifiable stratum: CP captures the smooth multilinear part of the count-vector-to-distance map and C5 adds the
  rest almost uniformly. C5 is not a refinement of the same low-rank coordinate in any way these probes can
  separate; what it adds is diffuse.

Answer to "what structure was actually discovered": rank and collapse count are computed exactly in the first
layer; the target partition is recovered; the penultimate layer is a coordinate system in which D is linear; the
representation is symbol-bound rather than action-equivariant; nothing in the probe set names the coordinate. The
M7 category is not invoked. The honest status is: characterised as a distributed, convention-bound, near-linear
distance embedding whose basis is not yet identified in known mathematical terms.

## C6 interpretation

C6 succeeds at the meaningful band with 24 evolved expressions over count-vector and digit terminals plus ridge
weights. The expressions are nested comparisons of image-value counts against target digits; I cannot read them as
rules. The "strongly interpretable symbolic rule" outcome is therefore not claimed; the frozen-matrix row becomes
"symbolic compact representation also exists".

## Remaining scientific question (ruling 15)

What coordinate system makes D(f, t) almost trivial to the C5 model? The dissection narrows it: it lives in the
256-dimensional penultimate layer, it is linear in D there, it is not the kernel partition, it is not rank or counts
alone, and it is tied to the digit convention. Candidate next steps, none started: fit an equivariant model under
the {0,1}-fixing relabelling group as a separate preregistered family and test whether it matches C5 at smaller
size; or canonicalise inputs by that group before probing, to see whether the residual geometry is a function of
orbit coordinates plus collapse depth (M6).
