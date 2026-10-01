# Scope 3: world machinery

Slot to fill: the world foundry (RSE_ARCHITECTURE.md section 5): world
families RECALL, TRACK, IDENTIFY, RETAIN, RECOMBINE, CHAIN, FAMILIES, DOUBT
and MINED, each with a demand certificate (exact or proven bounds for
restricted policy classes), a baseline ladder, twins, sealed sets and leak
probes.

Requirement areas to read: section 1; WLD-01 to WLD-17; MEAS-03, MEAS-04,
MEAS-12; SRCH-05; PROV-10.

Components:

1. Ludus: exactly solvable authored game worlds, exact value, depth
   profiles, occupancy-weighted regret, the differential leak audit, the
   arena, the 1,338-row game atlas. Dossier: sisyphus/seats/Ludus.md.
   Code: ludus/.
2. Bellerophon's Worlds Kernel: prometheus/toolbox (IR, compile, execute,
   replay, receipt hash chain, admission, mutation ledger). Dossier:
   sisyphus/seats/Bellerophon.md.
3. Archaeon's world machinery: the WSE event-stream world grammar W0-W10
   (streams, delays, distractors), the Campaign 6 composed worlds (feature
   modules), ENVGATE (environment varied with organism physics frozen, sham
   arms). Dossier: sisyphus/seats/Archaeon.md. Code: archaeon/.
4. Herakles: herakles.evca / eca / ca_stream and the reproduced historical
   CA rule tables. Dossier: sisyphus/seats/Herakles.md. Code: herakles/.
5. Hecate: the control-first world generator (specification frozen only
   after its controls attain every clause), null twins, the alien-lawful
   assay with a certified answer key. Dossier: tityos/seats/Hecate.md.
   Code: hecate/.
6. Ensorain: the world-genome foundry with named RNG streams, the WTP-03
   null ladder (N0 to N5), the exact marginal-preserving surrogate, the
   binary processes scored against exact Bayes. Dossier:
   tantalus/seats/Ensorain.md. Code: ensorain/.
7. Cosmos: the sealed-holdout broker and receipts (do NOT open any holdout
   directory; describe the broker from its code only), the C3
   decodability-plus-state-swap memory certificate, the boundary-location
   attack, the zero-parameter "definition rung". Dossier:
   tantalus/seats/Cosmos.md. Code: prometheus/cosmos/ excluding holdout.
8. Tyche: world certificates by exact subset mutual information; keyed PRF
   negatives; TSD twins. Dossier: tantalus/seats/Tyche.md.
9. Ares W-family toy worlds and Vivarium "kinds", briefly, only to say
   what they demand.
10. The existing "reasoning ladder" (R0..R7 or similar; the dossiers and
    docs/phase3/PHASE3_CHALLENGES.md mention a ladder v0.1 and an R6 oracle
    that leaked its answer). Find where it is defined, what each rung
    requires, and how rungs were graded.

For each, answer from the source:

- what the organism observes and what it can do;
- what hidden state exists and what is the minimum a policy must remember
  or infer to do well (in bits or states, if the code or docs let you say);
- whether an EXACT optimal value, or the best value of a restricted class
  (memoryless, k-state, non-adaptive, lookup), is computed anywhere;
- whether cheap baselines ship with the world or arrived later;
- whether there are held-out or sealed instances and how they are kept
  from the search;
- whether a leak test exists and what it can and cannot detect;
- determinism, integer physics, seeds;
- which of my nine families it could seed, if any, and what would have to
  be added to give it a demand certificate.

The decision Dionysus has to make: which existing world code, solvers and
certificate ideas become part of the foundry, and which families are
written new.
