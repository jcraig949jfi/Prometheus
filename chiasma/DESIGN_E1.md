# CHIASMA E1 design: four handcrafted organisms through one Ontological Shock

Seat: Hades. Charter: roles/Hades/prompts/2026-10-07_charter/ (s7, "the experiment
I would run first"). Status: DESIGN, v0.1, 2026-10-07. Code: chiasma/ at the commit
that carries this file. Claim level of everything here: AUTHOR_TESTED.

## 1. Question E1 answers (a narrowing of the charter's question)

The charter's s7 question is: under matched resources, does a dual mesh with
uncertainty and revision seams (O4) beat positive-only (O1) and positive + raw
failure memory (O2) through learn -> reinforce a false abstraction -> exceptions ->
falsification -> relearn -> novel descendants? If not, kill or radically revise
before any evolution.

E1 measures this on one world family. It does not test the full engine question
(compression/search at scale, fault-line prediction, evolution, transplant).

## 2. World: Paradigm World family H (chiasma/world.py)

- m = 16 latent primitives, independent at P = 1/2. A latent abstraction
  Y = c AND f is never labelled.
- Targets: ydep Z_i = Y AND u_i AND v_i; decoy D_k = c AND u'_k AND v'_k;
  unrel = one or two conjunctions without c or f (3 of 8 are disjunctive);
  INVALID = OR of 3 four-primitive incompatibility laws (an invalid object is a
  failed experiment and returns no other label); new = ydep-type targets active
  only in phase F.
- Phases A 1500, B 1500, C 1000, D 500, E 1500, F 1500 observations. In A-C the
  sampler forces c -> f, so the cheap abstraction "drop f" (H0) predicts every
  A/B label exactly (WT-0 checks this exhaustively). In C, 2% of objects are
  exceptions (c AND NOT f). D-F are unconstrained (c AND NOT f in about 25%).
  Organisms never see phase names.
- Known answer per target: ydep needs f, decoy does not. During A/B the data
  cannot tell them apart, so every organism must bet. The ydep:decoy ratio
  therefore decides who wins the bet, and is a factor: R21 (16:8), R11 (12:12),
  R12 (8:16).
- Probes: 300 unconstrained objects plus 4 critical probes per ydep/decoy/new
  target in the c AND NOT f region, scored every 100 observations.

## 3. Organisms (chiasma/organisms.py)

Shared positive geometry P: per target, cells = simplices over primitive vertices
(conjunctions). Weld on a false negative = the shared face (intersection) with an
unconsolidated cell, if the arm's weld test allows it. A cell that fires on a
negative is retracted. Consolidation after 6 supporting positives drops every
literal implied by another literal of the cell in all objects seen so far (an
implication table, part of P), and discards the anchor. That compression is
where the false foundation comes from.

| arm  | failure memory N                          | U / seams                                  | role |
|------|-------------------------------------------|--------------------------------------------|------|
| O1   | none (welds freely)                       | none                                       | charter O1 |
| O2   | raw (object, target) FIFO under the cap   | none                                       | charter O2 |
| O3   | compressed shadow: failures projected onto the target's own support, maximal sets only | none | charter O3 |
| O4   | as O3                                     | provenance (pruned literal, justifier) + eager seams: when a justification breaks, every dependent cell gets the literal back and is disputed until its own evidence confirms or reverses it | charter O4 |
| O4L  | as O3                                     | provenance only; a cell repairs itself from it when it fails (no eager seam) | ablation, added after dev run 1 |
| O0   | as O3                                     | none; never consolidates (keeps anchors)   | cheapest counter-organism |
| O3R  | random masks of the same size             | none                                       | counterfeit shadow |
| O4R  | as O3                                     | provenance names a random literal          | counterfeit seams |
| CEIL | raw, unbounded                            | none; never consolidates                   | unbounded-capacity ceiling |
| EMB  | stores whole labelled examples; 5-NN in Hamming distance | none                       | replay masquerading as memory |

Every arm gets the same observations, the same probe workload, and the same byte cap
(evicting N first, then U). Bytes are measured by one canonical ruler (WT-0 checks
it by hand). Operations are counted, not matched: extra operations would not help
O1 or O2. The ops ratio is reported beside every contrast.

## 4. Endpoints (chiasma/runner.py)

Integer only. Reported separately and never summed into one score (charter s5):
- bet_B: probe errors just before the shock (the pre-shock bet).
- err_CDE: probe errors summed over C, D, E checkpoints (the shock, integrated).
- collateral_CDE: decoy/unrel/invalid errors above their end-of-B level (knowledge
  that was right and broke).
- recovery_obs: observations from the first exception until all critical errors are
  0 for good.
- revise_DE, insert_F, insert_obs, bytes (P, N, U) per phase, ops per phase,
  structural events per phase (welds, new cells, retractions, repairs, seams).

OSI (charter WT-3) components map onto these: D(P_t, P_t+1) is the structural
events; Delta B is bytes per phase; C_revision is ops in C-E; F_collateral is
collateral_CDE; T_recovery is recovery_obs. No weights are chosen in E1.

## 5. WT-0 gate (G0)

chiasma/tests/test_wt0.py has 18 known-answer tests: world determinism, sampler
hiding, exact H0 consistency, the exception rate, invalid-object handling, the
critical-probe answers, weld = shared face, consolidation pruning exactly the
implied literal, seam open/confirm/reverse, lazy repair, retraction, exhaustive
equivalence of raw vs projected refutation, the compression bound, the
random-shadow control, the byte ruler by hand, cap enforcement, receipt
reproducibility and float refusal. chiasma/wt0_mutation.py plants 16 one-line
defects. All 16 are killed (the first pass killed 14; two tests were strengthened).
Receipt: chiasma/runs/wt0/RECEIPT.md.

## 6. What development sizing showed (dev seeds 900001-900005; sizing, NOT results)

Receipts: chiasma/runs/dev-sizing-1/rows.jsonl (420 runs, 1.26 CPU core-hours).
1. The pre-shock bet is set by the world ratio: O0 (keep f) wins R21, compressing
   arms win R12. Hence the ratio factor.
2. O4 as first designed (eager seams) behaves like a bet too. It wins when ydep
   dominate and loses when decoys do. Its counterfeit O4R does about as well. In
   this world, eager seams are not shown to carry a mechanism.
3. O4L (provenance repair) beat O1, O2 and O3 on err_CDE at every ratio and cap
   (5 wins, 0 losses), with collateral 0. This is why O4L exists. It was added
   after seeing data, so it is reported as an ablation and never decides the
   verdict.
4. Caps of 1000-10000 bytes did not change any O2-O4 endpoint: N does not bind in
   this world at those caps. Tighter caps (600, 800) were sized in dev run 2
   (chiasma/runs/dev-sizing-2/).
5. Nearly every arm except O1 has absorbed the shock before the decisive phase D,
   so revise_DE is about 0 and is not a useful primary.
6. O3/O4/O4L spend about 2.4x the ops of O2, mostly on shadow upkeep.

## 7. Known limits (stated before evaluation)

- One world family, conjunctive truths with few disjunctions, noise-free labels.
  The false foundation is a single redundant literal. Real paradigm shifts are
  larger.
- No 8-16-D coordinates, no factoring of shared abstractions, no evolution: E1
  tests the discrete mechanism only.
- The world and the organisms have the same author. A reviewer must try to build
  an organism or a world variant that reverses the verdict (G3).
- Compute is reported, not matched.
