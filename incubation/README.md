# incubation — executable symbolic learning substrate

> Full program documentation (design lineage, mechanics, scope, artifact
> registry): [`DOCUMENTATION.md`](DOCUMENTATION.md)

## Hypothesis

A symbolic composition learned in one problem world can become a reusable entity that
changes the computational cost of solving structurally related, surface-dissimilar
worlds. A concept is admitted only on demonstrated causal utility; interpretability is
not a criterion.

## Design

**Primitives** (`primitives.py`): four executable transformations with arbitrary IDs,
polymorphic over `Z_m^k` (tuples of residues), each with exact semantics, declared
types, an inverse (diagnostic side only), and at least one live consumer:
`r00` rotate-left, `r01` swap slots 0/1, `r02` slot0 += slot1, `r03` slot0 <- 2*slot0+1.

**Worlds** (`worlds/families.py`): three procedurally generated reachability families
sharing the primitive entities but differing in dimension, modulus, surface codec,
generator code, and dynamics:

- `wA` (discovery): k=6, m=997, int-tuple surface.
- `wB` (transfer): k=7, m=673, string surface (two letters per slot); independent
  generator and seed streams.
- `wC` (adversarial): k=8, m=809; entering any state with slot1 < m//5 is forbidden —
  moves into the band fail at runtime (execution still costs). Half its tasks carry
  witnesses free of the target composition.

A task is `{start, target}` and nothing else. The diagnostic-side composition
M = (r01, r02, r01) (effect: slot1 += slot0, a conjugation identity valid at every
k, m) is embedded by the generators; family filters (omniscient side, never
solver-visible) guarantee every embed task's minimal solutions ALL contain M and every
null task's minimal solutions contain none. World design was iterated under a
preregistered census (`experiments/census_v*.py`); v0 and v1 were REJECTED
(`results/census_v0.json`, `census_v1.json`) before v2 passed (`census_v2.json`).

**Solver** (`solver/`): iterative-deepening tree search (and BFS graph search for one
control arm) over an action alphabet, behind an observation boundary exposing only
`start`, equality `is_goal`, counted `apply`, and `read`. A reified concept occupies one
composition slot (one node) but pays full execution cost; a flat inline block pays
per-step nodes and depth.

**Arms**: P0 primitives-only IDDFS; P1 primitives-only BFS with duplicate elimination;
P2a flat expression tried once then P0; P2b unreified inline block; P3 reified concept
c0001; P3R random length-matched reified macro; P3G c0002 (c0001 + learned guard).

**Concept formation** (`concepts/`): n-grams of the solver's own solutions grouped by
execution fingerprint, scored support x depth-saved; admission is the preregistered
utility gate, not interpretability. Guards are learned from the concept's own runtime
failures as the cheapest exact cover by at most two executable probe atoms.

**Ledger** (`ledger/`): append-only entries with derivation, provenance, admission
evidence, effect sizes, ablations, transfer results, failure regions, revisions,
status (candidate/admitted/bounded/superseded/rejected).

## Preregistered metrics and gates

Unit of analysis: the task. Primary metric: search nodes to first verified solution;
secondary: candidate tests, primitive executions. Paired per-task ratios against P0,
median + bootstrap 95% CI (5000 resamples, fixed seeds), pooled over 5 master seeds
(11, 22, 33, 44, 55) with per-seed medians required on the same side of 1.0. The full
gate list with thresholds is the `PREREG` dict in `experiments/incubation_v1.py`
(committed before the run) and is reproduced verbatim in
`results/incubation_v1.json["prereg"]`. Highlights:

- ADMIT: median(P3/P0 nodes) <= 0.5 on held-out wA, CI upper < 1.0; P3 also beats the
  random-macro control; correctness 100%; ablation restores P0 counter-identically.
- FLAT: P3 beats both flat controls (P2a <= 0.5, P2b <= 0.7; CI upper < 1.0).
- TRANSFER: frozen c0001 on wB: median(P3/P0) <= 0.5, CI upper < 1.0, hash unchanged.
- NEG: wC hostile median(P3/P0) >= 1.5 (CI lower > 1.0); friendly <= 0.7.
- DETECT: runtime-failure rate >= 0.05 in wC (>= 100 attempts), 0 in wA/wB.
- REV: guard out-of-sample failure prediction >= 0.95 per seed; >= 90% failure
  reduction; exec overhead <= 1.10, node overhead <= 1.02; friendly advantage kept.

## Kill conditions

The ten conditions of the spec are each evaluated against data in
`results/incubation_v1.json["KILL_CONDITIONS"]`. One is answered by scoping rather than
survival and is stated openly: a bidirectional search over inverse primitives solves
these tasks in ~1e3 node visits. Inverses are excluded from the solver's action
alphabet by design, so every cost claim here is relative to the forward-composition
solver class (K2 = SCOPED).

## Results observed

Run of 2026-08-26, 5 master seeds, 3,125 per-task rows in
`results/incubation_v1.json` (per-task rows ship with the verdict). All 16
preregistered gates passed; the anti-cheat battery passed; kill conditions K1-K10
survived with K2 SCOPED as stated above. An earlier full run FAILED the anti-cheat
battery (6 witness-word collisions between wA and wB cells made the transfer
measurement partially non-independent); the fix — witness words sampled without
replacement across all cells of a replicate — is in the generator, and the run was
repeated from scratch.

Discovery: the miner produced the identical candidate `(r01, r02, r01)` in 5/5 seeds
from the solver's own solutions, with no access to generators or witnesses.

Paired per-task node ratios, pooled median [bootstrap 95% CI], per-seed medians all on
the same side of 1.0 in every row:

- Admission (wA held-out): P3/P0 = 0.169 [0.164, 0.171]; correctness 1.0 in all arms.
- Content specificity: P3/P3R = 0.041; the random reified macro is ~3.3x WORSE than
  P0 (median 230,626 vs 70,088 nodes) — carrying a useless concept has real cost.
- Reification vs computation: P2a is node-identical to P0 (the flat expression never
  solves a task alone), P2b is ~10% worse than P0 (inline unreified block is pure
  overhead); P3/P2b = 0.154. The advantage comes from the composition slot, not from
  possessing the composition.
- Transfer (wB, frozen, content hash unchanged): P3/P0 = 0.170 [0.168, 0.173];
  P3/P1 = 0.43 against the strongest primitive-only search; correctness 1.0.
- Ablation: removing c0001 restores P0 counter-identically on every checked task, in
  wA and wB.
- Negative transfer (wC blind): hostile P3/P0 = 2.85 [2.72, 3.01]; friendly 0.154.
  Detection signal without any label: 2,102,725 runtime failures over 6,978,052
  attempts in wC (rate 0.30) against exactly 0 in wA and wB.
- Revision: learned guard = comp0(s) < 161 OR comp0(r02(s)) < 161 (the dynamics
  boundary is m//5 = 161; the learner recovered it from failure evidence alone).
  Out-of-sample failure prediction accuracy 1.0/0.9975/1.0/1.0/1.0 by seed. Guarded
  c0002: 0 runtime failures vs 2,207,501 blind on validation tasks, node ratio
  exactly 1.0 (no false positives), exec overhead 1.035, friendly advantage retained
  (P3G/P0 = 0.162).
- Bounded region, recorded not repaired: hostile node harm persists under the guard
  (P3G/P0 = 2.91) because it is a task-level property — the hostile tasks' minimal
  solutions avoid the composition — and is not predictable from any state the guard
  can probe. c0001 status: bounded; c0002 status: admitted; full history in
  `ledger/entries/`.

Section-9 verdict computed from the gates: A-G all true — evidence for executable
symbolic learning with revision, within the scope stated under kill condition K2.
