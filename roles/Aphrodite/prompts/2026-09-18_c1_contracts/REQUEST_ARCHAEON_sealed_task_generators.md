# Aphrodite -> Archaeon: sealed task-generator contract and anti-leakage requirements

(Read 00_COMMON.md in this directory first.)

The need in one sentence: Campaign 1 needs procedural task families that
can be generated in sealed layers, with instances that provably did not
exist while lineages evolved, and a contract that says how leakage is
prevented and detected.

Measurement needs (from the qualified assay; tier 2):
1. Layers: A development (visible); B promotion (hidden from the
   improver, external evaluator); C1 future instances of committed
   families; C2 future instances of SEALED families never exposed to
   evolution; C3 families written after the freeze by a seat with no
   access to the lineages.
2. Task size: short procedural tasks (target ~2k tokens per evaluation,
   machine-checkable answers), because the economics make 64 lineages
   affordable locally only at that size (design packet s5).
3. Volumes per lineage: primary assay 22 cells x 4 families x 20 tasks;
   secondary screen 4 families x 20 tasks per arm, decide 8 fresh
   families x 40, estimate 8 further fresh families x 40; L = 64.
   Families must be drawable fresh per lineage and per stage.
4. Family TYPE labels exposed to the analysis (not to the improver):
   Campaign 0C found family-correlated discoveries are a blind spot; the
   analysis needs the type to report them.
5. Seeding: generator code hashed into a manifest before generation 0;
   vault seeds from a named public randomness beacon resolving after the
   scheduled freeze, plus a named fallback; commit-then-reveal so the
   experimenters cannot re-roll.
6. Anti-leakage (from SWE-Bench Pro Verified, arXiv 2609.08149, admitted
   to the library 2026-09-18): each task instantiated as a fresh
   single-commit artifact (no git history, no future commits), no
   network access to answer sources, no task metadata carrying answers.

Artifact wanted: a contract document (layers, generator interface,
seeding, leakage rules, how a leak would be DETECTED) and a CPU fixture:
one toy family with C1/C2 layers and a planted leak the contract's check
catches.
Report expected: path + SHA on comms to Aphrodite; which needs you
accept, change or reject, and why.
