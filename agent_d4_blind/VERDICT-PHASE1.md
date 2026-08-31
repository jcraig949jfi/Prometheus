# AGENT D-4 — PHASE 1 VERDICT

Date: 2026-08-27
Generation: agent_d4_blind, Phase 1 (blind accessibility geometry)
Constitution: PREREG-PHASE1.md, frozen 2026-08-27 (hashes in
anti_cheat/frozen_hashes.json); instrument v4, validated on all 8 synthetic
pathology controls at binding scale before freeze; engineering amendment E1
(memory-only, measurement-equivalent, applied before any binding
measurement existed) disclosed in PREREG-PHASE1.md.
Machine-readable verdict: results/phase1_verdict.json. All rows committed
with this document.

## OVERALL VERDICT

ACCESSIBILITY_GEOMETRY_ESTABLISHED: S2_STACK, S4_MEM
(2 of 4 substrates; S4_MEM robust, S2_STACK marginal — see disclosures)

- S1_REG     -> NAVIGATION_FAILURE
- S2_STACK   -> PASS (marginal; two near-miss disclosures below)
- S3_REWRITE -> ACCESSIBILITY_FRAGMENTED
- S4_MEM     -> PASS (robust margins)

Per the frozen protocol (s.32): the passing substrates are FROZEN. A
Phase-2 preregistration MAY now be designed. It is not executed in this
generation. No learner exists. No P5/P6 claim is made.

## Per-substrate findings (all gates frozen before any measurement)

### S4_MEM — PASS, robust

- Viability 0.593 [0.583, 0.602]; 9,575 combined viable phenotype classes;
  Good-Turing unseen mass 0.929 (the census sees a small fraction of the
  viable diversity).
- All 5 mutation mechanisms alive (identity 0.522, effective 0.384).
- Navigation (36 targets, hit = d1 <= 0.10, budget 1,200):
  N2 pooled 0.522, cluster-bootstrap CI [0.38, 0.67] — lower bound clears
  the 0.25 gate. N4 pooled 0.489 [0.35, 0.63]. Far stratum: N2 0.53 (32/60,
  all search-mediated, 9 of 12 distinct far targets), N4 0.42; even the N1
  random-walk floor reaches far 0.28. Median first passage 149 evals (N2).
- Re-findability (excluding the qualifying discovery): 0.69-0.71.
- Privilege: NO single-mechanism ablation approaches the gate (worst:
  remove rotation, far, rel drop 0.14, z = 0.77 — graceful degradation
  across the whole menu, the C5-navigable signature). Reweight/radius worst
  delta 0.056 (z = 0.67). Re-coding delta 0.097 (z = 1.17) — inside the
  band; largest representation sensitivity of the four, disclosed.
- Oracle: far episode-reach 0.73 vs achieved 0.53 — moderate navigation
  regret; topology exceeds what M0 exploits at this budget.

### S2_STACK — PASS, marginal (disclosures)

- Viability 0.500 [0.490, 0.510]; 7,281 combined classes; unseen mass 0.849.
- All 5 mechanisms alive (identity 0.590, effective 0.295).
- Navigation: N2 pooled 0.333, N4 0.344 — both clear the frozen 0.25
  point-estimate gate, but the cluster-bootstrap CIs ([0.19, 0.48] and
  [0.22, 0.48]) include the gate: DISCLOSURE 1 — the pooled pass is within
  cluster-level noise of the gate. Far stratum (best nav N4): 0.15 (9/60,
  all search-mediated, 5 of 12 distinct far targets) vs gate 0.10.
  Re-findability 0.61-0.69.
- Privilege: DISCLOSURE 2 — removing OP1 (cell substitution) drops far
  hits by rel 0.72 at z = 1.85, just under the frozen z = 1.96. The gate
  did not fire; the margin is reported because it is the closest privilege
  call in the generation, and the human-taxonomy red team notes OP1 is the
  mechanism whose edits most often change I/O-instruction counts (30% of
  its effective transitions). A successor generation testing S2 should
  treat OP1-dependence as the first thing to probe.
- Reweight/radius worst delta 0.069 (z = 0.86); re-coding delta 0.014.
- Oracle far reach 0.50 vs achieved 0.15 — substantial navigation regret.

### S1_REG — NAVIGATION_FAILURE (preserved)

- Viability 0.093 [0.088, 0.099]; 3,452 combined classes — a real, diverse,
  displacement-live space (identity 0.519, effective 0.278, all ops alive).
- Pooled navigation passes (N2 0.317, N4 0.289) but the far stratum is
  dead: N2 0.00, N4 0.02 (gate 0.10). Near/mid are navigable; remote
  register-machine behaviors demonstrated to exist by the target-gen
  process were not reached by any generic navigator.
- Oracle far episode-reach 0.41: for ~2/5 of far episodes an observed
  path existed — attribution is search weakness/lottery topology at this
  budget, not proven fragmentation. S1 is "locally navigable, remotely
  inaccessible at 1,200 evaluations."
- Diagnostics: identifiability 0.501 (chance 0.365), anisotropy 0.817.

### S3_REWRITE — ACCESSIBILITY_FRAGMENTED (preserved)

- The charter's central warning made flesh (s.4, s.22): the HIGHEST
  validity and viability of the four (0.996 [0.995, 0.997] — almost every
  random rule table is a viable input-sensitive program) and the LARGEST
  phenotype mass (11,717 combined classes, unseen mass 0.99), with a dead
  accessibility geometry: far-stratum hits 0.00 for every navigator, and
  oracle far episode-reach 0.00 — across ~1.5M metered evaluations, not
  one observed viable path led from any episode's starts into any far
  target's ball. Deep-rewrite phenotypes appear on target-generation walks
  and are then unreachable again: one-off lottery phenotypes.
- Validity is a coordinate, not the objective; diversity is a coordinate,
  not the objective. S3 maximized both and failed the only property that
  matters for a learning substrate.

## Human-taxonomy red team (weaken-only; results/human_taxonomy_redteam.json)

- Across S1/S2/S4, large behavioral displacements (d1 > 0.3) are dominated
  by REARRANGEMENT of existing code (70-79%), not by edits that change the
  count of designed I/O primitives (7-9%): no evidence of an I/O vending
  machine behind the passes.
- Block-swap and rotation change no instruction-class counts by
  construction (pure permutation edits); substitution/copy are the count-
  changing mechanisms. For S2 this aligns with the OP1 disclosure above —
  the red team WEAKENS the S2 pass narrative accordingly.
- S3's effective edits are mostly unclassifiable by the human taxonomy
  (OTHER_UNKNOWN 56-84% per mechanism). Recorded as unclassifiable, not as
  novelty, per s.27.

## Strongest allowed claim (s.39, scoped as frozen)

For S4_MEM (and, with the two disclosures, S2_STACK):

"Under the frozen computational physics, executable behavioral change
forms a substantially diverse, reproducibly navigable accessibility
geometry under multiple generic history-free search processes, without
evidence that navigation is dominated by any single designer-privileged
mutation mechanism or by the particular binary encoding."

Nothing stronger. In particular this verdict does NOT establish: AGI,
intelligence, understanding, autonomous diagnosis, human-independent
cognition, elimination of human priors, or open-ended evolution. It
establishes properties of two frozen computational substrates under a
1,200-evaluation budget, 8 frozen probes, and a d1 <= 0.10 hit ball.

## Known limits carried into any Phase 2

1. S2's pass sits inside cluster-level noise on the pooled gate and one
   z=1.85 privilege near-miss; S4 is the load-bearing basis.
2. Privilege was tested for single-mechanism ablations and byte-level
   re-coding only; mechanism-PAIR privilege is untested (combinatorial).
3. "Accessible mass" is measured against phenotypes the physics itself
   exhibited under an independent seed (reproducible accessibility), not
   against all mathematically existing phenotypes.
4. Navigation regret (oracle-reach minus achieved) is substantial on S2
   (0.35 far) and present on S4 (0.20 far): the M0 suite under-exploits
   demonstrated topology; a stronger M0 would raise, not lower, the bar
   for any future learner comparison.
5. Phenotype identity is exactness on 8 frozen probes; no global
   equivalence is claimed.

## Phase-2 gate (per s.32)

S4_MEM (primary) and S2_STACK (secondary, with disclosures) are frozen as
the substrates a Phase-2 preregistration may target. Phase 2 would ask
whether accumulated executable history alters which transformations can be
acquired under fixed resources — it is NOT asked or answered here, and no
Phase-2 work beyond preregistration design is authorized by this verdict.
