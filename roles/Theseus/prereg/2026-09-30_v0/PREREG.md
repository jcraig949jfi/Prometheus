# Theseus v0 preregistration -- concept tensor / synthetic ancestry, first loop

Currency: 2026-09-30. Committed BEFORE the full v0 run, in its own commit
(base role s2). One smoke run (--smoke: 7 generations, per_cell 1, arms of
12) was executed to prove the pipeline end to end; its outputs were deleted
unread except for the pipeline-health lines quoted in s8. Code hashes are in
CODE_SHA256.txt beside this file; the run must be executed from a tree whose
theseus/synth/ files match them.

Charter: roles/Theseus/prompts/2026-09-30_charter/ (verbatim, MANIFEST).
Governing order: MWO-0004 (R1 defaults, R2 envelope). Compute: local, 4
logical CPUs on DESKTOP-RUAPVAI; estimated < 1 CPU-hour; guard: the ecology
stops at 4 h wall. No Fabric lease (below "substantial"; recorded).

## 1. Question

Do deep synthetic descendants of an executable collision ecology occupy
behavioural niches that are not reached by (A) LLM semantic synthesis,
(B) direct executable triplets, (C) direct executable sextuplets, or (R)
random programs of matched complexity -- under shared rulers, equal n?
(Charter: FIRST HARD TEST.) Secondary: arity, depth vs arity, the lens loop,
mechanistic reproduction.

The thesis is NOT assumed. v0 is built to be able to say no.

## 2. Machinery (theseus/synth/, all executable, no LLM in any tick path)

- substrate.py: genome = typed program over a field X[C<=4, N=32] + memory,
  T=128, sequential (noncommutative) rules from 19 primitive ops (transport,
  coupling, bounding, conservation, memory, switching, copying, selection,
  symmetry, scale, delay, state topology, order, forcing, routing,
  observation via a Tyche lens). THE OP SET IS ITSELF A HUMAN PRIOR: nothing
  can leave the space it spans.
- compile_g0.py: G0 = the 95 concepts of agents/nous/src/concepts.py
  (source "hephaestus"), text enriched by Hecate Pass-0 extractions where
  present (45 of 95). Deterministic keyword compiler -> 16 charter
  properties (evidence words stored) -> fixed property->op table. KNOWN
  BIAS: enriched concepts compile to ~10-14 rules, description-only ones to
  2-3 (text-length confound); every G0 records whether it was enriched.
- collide.py: ordered k-way collision = bind (seeded rule subsets, position-
  dependent channel remap) + generated k-ary interaction law (a concept-
  tensor entry in CP form, gains from latent factors) + a seeded subset of
  operators (parameter inheritance, substitution, symmetry inheritance,
  cross-scale coupling, memory transfer, bc exchange, state merge,
  mutation). Exact rule provenance.
- battery.py: fingerprint = 12 descriptors + 22 intervention responses
  (34 dims), averaged over IC seeds 0 and 1. Viability: deterministic,
  stable, nontrivial, lifetime, transforms, responsive, replicable.
- rulers.py: calibration FROZEN from viable G0 before any arm; 3 grids
  (pca, desc, resp; 7 bins/axis at G0 quantiles), 3 metrics (euclid_z,
  cosine, quantile_l1). No scalar novelty score.
- known.py: 12 known-mechanism families in the same substrate, library 40
  per family, 16 refinement evals per target; verdicts REPRODUCED_BY_KNOWN
  (d <= tau_rep), PARTIALLY_REPRODUCED (<= 2 tau_rep), NOT_REPRODUCED_YET.
- dark.py: DARK_OBJECT = viable, residual under L0 lenses >= 0.25 on a held-
  out IC, held-out targets temporally structured (|ac1| >= 0.5). Lens
  evolution with Tyche lens genomes; admission = held-out drop >= 0.05 and
  > 95th pct of 30 random lenses. Admitted lenses become entities.
- ecology.py: the giant ball; coalition partner modes near 0.3 / far 0.3 /
  underexplored 0.2 / random 0.2; POP_CAP 400; fossilisation.
- run_v0.py: 30 generations x lanes {G0, SHALLOW, DEEP, VERY_DEEP,
  DEEP_LENS} x arities {2, 3, 6} x 3 collisions per cell; deep threshold
  generation >= 5; 2 lens evolutions per generation.

Design history before this commit (not amendments -- no full run existed):
dark-object gate changed from a full-state linear observer (which was worse
than L0 on G0) to the temporal-structure gate; organisms train on IC seeds
{0,2,3,4} and test on 1; viability gained "transforms" after the execution-
neutral control design showed a static structured IC would otherwise pass.

## 3. Arms

D  DEEP + VERY_DEEP ecology children (no raw-human parent; parents gen >= 5)
E  DEEP_LENS children (deep parents + one admitted lens parent)
P/B/C  300 one-shot G0 collisions each at arity 2/3/6 (fixed-depth controls)
A  60 genomes written by a fresh Claude agent from SPEC.md + TUPLES.json
   only (30 triplets, 30 sextuplets; theseus/controls/llm_arm_v0/),
   committed with this preregistration
R  300 random programs, complexity-matched (n_rules, C, max src) to D
W  60 deliberately weird high-gain programs; X 40 execution-neutral
   programs; HK 20 known mechanisms hidden behind SYN names

## 4. Primary decision rule (H1) -- theseus/synth/analysis.py hard_test

Viable candidates only; n = min viable count over D, A, B, C, R; n < 30 ->
INDETERMINATE. One seeded equal-n subsample per arm.
  EX_g(D): cells of grid g occupied by D and by none of A, B, C, R;
  permutation p over 1000 label shuffles of the pooled equal-n set.
  O_m(X): median min-distance of X to the union of the other four arms;
  bootstrap (200) 95% CI of O_m(D) - O_m(R).
PASS: >= 2 of 3 grids with p < 0.05 and EX(D) > EX(R), AND >= 2 of 3
metrics with CI lower bound > 0.
FAIL: >= 2 of 3 grids with EX(D) <= null median, OR >= 2 of 3 metrics with
CI upper bound < 0.
INDETERMINATE otherwise. Note A has at most 60 candidates, so n <= 60.

A PASS would mean only: at v0 scale, under these rulers and this op set,
deep descendants reach fingerprint regions the four comparison arms did
not. It would NOT mean human priors are absent, and it would NOT mean
novelty of mechanism (that is H5 and the strongest-candidate table).

## 5. Predictions (scored mechanically by analysis.score_predictions)

P1  H1 is FAIL or INDETERMINATE.                                  p = 0.65
P2  one-shot viable fraction: pairs > triplets > sextuplets.      p = 0.45
P3  R viable fraction < B viable fraction.                        p = 0.6
P4  DEEP-lane mean raw-human rule fraction < 0.2.                 p = 0.7
P5  >= 1 lens admitted against an ecology dark object.            p = 0.6
P6  E lens-dependent fraction > D lens-dependent fraction.        p = 0.55
P7  hidden-known control passes (>= 80%).                         p = 0.8
P8  >= 50% of top-20 D are NOT_REPRODUCED_YET.                    p = 0.5
P9  Spearman(generation, distance to one-shot union) > 0.1.       p = 0.5
Wrong predictions go to roles/Theseus/calibration/LEDGER.md.

## 6. Validity gates (an instrument that fails its gate voids its ruler)

- HK: >= 80% REPRODUCED or PARTIAL, else the mechanistic ruler is INVALID.
- X: <= 5% viable, else the viability ruler is INVALID.
- Lineage integrity: 0 ancestry mismatches, 0 foreign provenance.
- Lineage-shuffle and behaviour-shuffle controls are reported, not gated.
- W (weird) is reported: its viable share and whether it outreaches D.

## 7. Secondary (descriptive, no verdicts)

Arity (P/B/C viable fraction with Wilson CI, EX among one-shots, O);
depth vs arity (distance of each viable ecology child to the one-shot
union, by lane x arity); genealogy per lane; mechanistic verdicts per arm;
lens loop counts; decision-state counts; strongest candidates in the
charter's precise language.

## 8. Smoke health (the only smoke numbers read)

Pipeline completed; hidden-known 4/4; execution-neutral 0/6 viable (all on
"transforms"); lineage integrity 0/0; one-shot law depth max 1; the A arm
parsed 60/60. D was empty (7 generations cannot reach generation 5), so no
smoke number bears on H1.

## 9. Conflicts of interest

The builder (Claude, this seat) wrote the substrate, the op set, the
compiler, the known library and every ruler, and would prefer an
interesting result. The A arm was written by the same model family, so A
measures "Claude semantic synthesis in this DSL", not LLMs in general. The
known library is 12 families chosen by the builder; NOT_REPRODUCED_YET
against it is weak evidence by construction.

## 10. What would falsify / what to stop

H1 FAIL with valid controls = at v0 scale, recursive ancestry does not
expand behavioural space beyond one-shot and random machinery; the next
step is then to ask whether the op set, the fingerprint or the ecology is
the bottleneck (successor candidates in the backlog), not to rerun until it
passes. If D's advantage is carried by W-like (weird) signatures, the
viability gate is too weak and is the thing to fix.
