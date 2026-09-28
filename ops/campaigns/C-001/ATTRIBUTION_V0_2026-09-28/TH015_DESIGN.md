# TH-015 -- what has to cross a generation for reproductive competence to stay above chance? (design + Archaeon leg)

Thread: ops/threads/TH-015.md (thr-a7fcb43e8092). Directive 2026-09-28 item 6.

## Question
For each engine, intervene SEPARATELY on:
- copied material;
- copy machinery;
- execution context;
- environmental scaffold;
- control state.

Then find the smallest transferable object that keeps copying competence above the chance floor.

## Common protocol (same for all three engines)
- **Subjects:** capable organisms (demonstrated by execution, never by label) sampled from one established lineage per engine.
- **Machinery M:** loci whose single knockout removes the capability. Scan ALL loci, because opcode-address masks miss operands:
  failed representation F4.
- **Interventions**, each with K random backgrounds (fixed seed):

| intervention | what crosses | what is replaced |
|---|---|---|
| MATERIAL_ONLY | everything but M | M re-randomised |
| MACHINERY_ONLY | M | everything else random |
| EXECUTED_ONLY | M plus executed opcode loci | the rest random |
| RANDOM_SAME_SIZE | a random locus set of size abs(M) | control for transplant size |
| NEIGHBOUR_CONTEXT | the whole organism | the neighbour / partner / pair tape randomised |
| CONTROL_STATE | the whole organism | start state (pc, registers, frame) randomised |
| INPUT_SCAFFOLD | the whole organism | input stream restricted / the gating input removed |
| CHANCE | nothing | random organisms |

- **Readout:** capable (the engine's own birth predicate) and exact, per intervention. Report the rate, the chance floor, and the
  smallest set whose transplant rate exceeds chance with a one-sided binomial p < 0.01.

## Engine legs
- **Archaeon (RUNS HERE):** archaeon/attribution/probes/th015_archaeon.py over the member tapes recorded by the TH-013 replay
  (block 13, BLOCK_128 arm).
  * Capability: a birth (>= 0.9 of the neighbour window written) on an allowed input, zero neighbour.
  * Control state = the start pc.
  * Scaffold = the input stream (input 128 is blocked in this arm).
- **BEE (DESIGN ONLY):** the subjects are writers of is_sr births in r038751, where 60% of writer-majority children seen writing
  later self-replicate.
  * Capability must be re-tested by the harness's own VM (prometheus/z80atlas at 16fc6c2a) in a controlled two-slot world:
    writer + blank partner. BEE reproduction is PAIR_EXECUTION or ENDOGENOUS_COPY, so NEIGHBOUR_CONTEXT = the partner tape.
  * M is by knockout over 64 loci.
  * Known prior: Bellerophon's HIST ablation found byte knockouts of copy ops "rescued" by re-created copy ops (126/345). Machinery
    there is an ISA-level capability, not a locus set. Expect MACHINERY_ONLY to fail and EXECUTED_ONLY to be partial; the smallest
    object may be "a copy op anywhere plus a NOP slide".
  * Blocker: needs Bellerophon's consent to run their harness (a portable replay recipe exists; TH-016 overlaps).
- **NPE (DESIGN ONLY):** the subjects are the 6 P-11-causal donors of T-003, plus BLOCK-grammar P-11 donors (Artemis FR-011:
  33/47 carry ED B0/B8).
  * Capability = P-11 C2 against a random victim (a dependence test on the event, re-used as the capability ruler).
  * NEIGHBOUR_CONTEXT = the pair partner.
  * CONTROL_STATE = the thread's saved context (prov / pc).
  * Prediction from W1 (C-CORE): OP_SELF + LDIR are conserved as material, so MACHINERY_ONLY = {OP_SELF, LDIR} is the candidate
    smallest object. Pair-tape co-execution may make NEIGHBOUR_CONTEXT necessary: the "relation between agents" answer.
  * Blocker: NPE is Nestor's; needs their harness and a ruling.

## What would change the thesis
- MACHINERY_ONLY >> chance while MATERIAL_ONLY ~ chance: the transmitted object is the machinery, and founder cargo is irrelevant
  to competence (supports D7).
- NEIGHBOUR_CONTEXT or INPUT_SCAFFOLD collapsing competence: the object is machinery PLUS context (scaffolded; the capacity is
  relational, F7).
- No transplant set beating chance while the whole organism does: the competence is distributed, not local.

Results: TH015_RESULT.md (Archaeon leg).
