# Scope 1: program-like organism substrates

Slot to fill: WM, the workspace machine (RSE_ARCHITECTURE.md 6.2), and the
affordance-knockout experiment P3.

Requirement areas to read: section 1; ORG-01 to ORG-09; DEV-01, DEV-02;
SRCH-01 to SRCH-04; COMP-01; REPR-01.

The slot needs: a total, deterministic, integer stored-program organism;
fast state the harness can reset; a persistent store of blocks that the
organism writes during life and later reads or executes; addressing that
survives insertion and deletion (tag or content addressing); call and
return with arguments; create, delete, copy and append; internal steps
before acting; cost per instruction and rent per stored cell; exact
snapshot, restore and fork; a state partition the harness controls; each of
those affordances with an off switch; measured throughput.

Components:

1. Proteus v0 VM ("proteus.foundry", 25 ops, 4-word instructions), its
   grammar, proteus.graph / graph_organism.v1, and the mutation-kernel
   crucible. Dossier: sisyphus/seats/Proteus.md. Code: proteus/.
2. Crius's 8-register bytecode VM with a persistent executable workspace,
   and its control battery (content tests, pre-search gate, neutral-edit
   baseline). Dossier: sisyphus/seats/Crius.md. Code: crius/.
3. The D-5 register machine used by Ergon E4 (8 x 16-bit registers, up to
   24 instructions, Numba fast path checked against a reference VM), and
   its genotype library. Dossier: tantalus/seats/Ergon.md. Code: ergon/.
4. The three "Z80" byte-soup machines: Nestor NPE (roles/Nestor/campaigns/
   z80atlas-*, primordial/), Bellerophon BEE (prometheus/z80atlas/),
   Archaeon z80atlas (archaeon/z80atlas/). Dossiers: sisyphus/seats/
   Nestor.md, Bellerophon.md, Archaeon.md. Do NOT open nestor_secrets.
5. Apollo's routing-DAG / blackboard evolvers and Lexis's closure search,
   only far enough to say whether any part is an organism in the slot's
   sense. Dossiers: sisyphus/seats/Apollo.md, Lexis.md.

For each machine answer specifically, from the source:

- the instruction set (list it), word format, and whether every word
  decodes to a legal instruction;
- what state exists (registers, tape, stack, memory, workspace) and what
  survives between episodes or evaluations;
- whether the organism can write code or data that it later executes or
  reads, and how that store is addressed;
- whether there is call/return, and whether arguments can be passed;
- how randomness is produced; whether a run is bit-reproducible;
- whether snapshot/restore exists;
- whether cost or energy is charged;
- evaluation throughput, if any number is recorded anywhere (evaluations
  per second, wall time for a stated number of evaluations);
- implementation language and whether a compiled path exists.

The decision Dionysus has to make: adopt one of these as the base of WM
(which one, with what changes), or write WM new and keep these as
historical controls. Give the facts that decide it.
