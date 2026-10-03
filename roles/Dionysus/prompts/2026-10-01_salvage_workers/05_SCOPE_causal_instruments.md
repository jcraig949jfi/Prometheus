# Scope 5: causal, lineage and intervention instruments

Slots to fill: the RULERS layer of the kernel (RSE_ARCHITECTURE.md section
3): interchange and lesion, exact counterfactual twins, material tracing
for heredity and reuse, carrier localisation, search-power measurement,
and anything that already resembles class exclusion.

Requirement areas to read: section 1; CAUS-01 to CAUS-08; MEAS-01, MEAS-02,
MEAS-12; SRCH-02, SRCH-03; DEV-05; PROV-09; ORG-02, ORG-10.

Components:

1. Ananke's lens.py (between-tick carrier swaps with FLIP / NO-EFFECT /
   CHANCE verdicts; carrier_table; cue_arrival_profile; reach;
   verify_reach; arm_identical), the mirror-pair twin worlds, and the
   Wave-2 certification stack (attainability, must-fail adversaries,
   light-cone ceilings) that the Tantalus report says was never promoted
   out of research/. Dossier: tantalus/seats/Ananke.md.
   Code: prometheus/ananke/, roles/Ananke/research/.
2. Archaeon's taint VM and causal lens (per-byte material tracing, four
   identities per birth), and its census. Dossier:
   sisyphus/seats/Archaeon.md. Code: archaeon/.
3. Nestor's z8taint and the P-11 causal-copy assay; Bellerophon's
   bee_tracer; Artemis's CVT-R certificate. Report each one's documented
   false-accept mode. Dossiers: sisyphus/seats/Nestor.md, Bellerophon.md;
   tityos/seats/Artemis.md. Do NOT open nestor_secrets.
4. Ares's carriers.py (memory attribution to edges, cycles, nodes) and its
   carrier-blocking interventions, with the W4 lesion-coverage defect.
   Dossier: sisyphus/seats/Ares.md. Code: ares/.
5. Cosmos's C3 memory certificate (decodability plus state swap).
   Dossier: tantalus/seats/Cosmos.md. Do not open holdout directories.
6. Tyche's causality audit with a future-reading cheat control, TSD twins,
   keyed PRF negatives, the persistence-reason tracer. Dossier:
   tantalus/seats/Tyche.md. Code: tyche/.
7. Aether's one-bit twin assay with locality checks and the
   counterfactual-parent audit. Dossier: tantalus/seats/Aether.md.
8. Crius's content controls and neutral-edit baseline, and Proteus's
   mutation-kernel crucible with exact state enumeration. Dossiers:
   sisyphus/seats/Crius.md, Proteus.md.
9. Ergon E4's expressible / reachable / findable split, gate-fire worlds
   and planted-witness cheat control (MDE80 figures). Dossier:
   tantalus/seats/Ergon.md.
10. Diomedes's decomposition ladder (chance, state-independent ceiling,
    Z(x), Z(x,a), oracle) and proxy-reconstruction baseline. Dossier:
    tantalus/seats/Diomedes.md.

For each, answer from the source:

- what exactly is intervened on, and what is compared with what;
- whether the instrument is tied to one substrate's data structures or
  takes a generic description of state components;
- whether it has been run on a DESIGNED organism with a known answer
  (a plant) and recovered it, and on a known negative and rejected it;
- its verdict vocabulary and thresholds, and where they came from;
- its known false-accept and false-reject modes;
- what it would take to make it work through one common organism protocol
  that exposes named state components with reset, lesion and swap.

Two questions for the whole scope:

A. Search power. Does anything in the tree measure the probability that a
   search finds a PLANTED target as a function of its distance from the
   founders and of the budget? Ergon's expressible/reachable/findable
   split, Ananke's plants (XOR 0.850, FLIP 0.978) and verify_reach, Tyche's
   unmeasured needle size, Crius's neutral paths and Proteus's kernel
   crucible are the leads. Report what each actually measures.

B. Class exclusion. Does anything in the tree compute the best score that a
   restricted class of policies (memoryless, k-state, constant, lookup,
   copy-policy) can reach in a world, exactly or by enumeration, and
   compare an organism with it? The dossiers mention Ananke's light-cone
   ceilings and copy-policy ceilings (0.75), Ensorain's exact Bayes, Ludus's
   exact value, Diomedes's ceiling. Report what each bound is, how it was
   obtained and whether it was proved or measured.

The decision Dionysus has to make: which intervention instruments are
extracted into the shared ruler layer, and which stay behind as examples.
