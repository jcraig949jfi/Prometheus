REPORT -- valley width between the W2_K2 half-credit shelf and the two-key summit
==============================================================================

1. WHAT I SET OUT TO TEST
-------------------------
The two-keyed-value task (W2_K2: two PUT(tag,value) ticks, then two ASK(tag) ticks
in random order, 4-bit values, per-ask credit) is expressible in the frozen VM but
evolution never gets past a half-credit plateau. I wanted to measure, without
running any evolution, how far the plateau sits from the summit. The questions were:
(a) what the 23 committed shelf specimens actually hold in their state and whether
their answers depend on the asked tag at all, so whether they already have a READ
path, a second-value WRITE, both or neither; (b) whether splicing in a READ link
alone or a WRITE link alone lifts them to the summit; and (c) whether any encoding
already available in the ISA gives the one-value shelf a graded or one-step
neighbour toward the summit. That tells me whether the barrier is the search
operator or the representation.

2. WHAT I DID
-------------
Code and data: repository main @ 6ff2b2f8ad035d50aaf21d9f3b60e16c556683f2, exported
with git archive (proteus/, archaeon/wse/, archaeon/campaign4/SPECIMENS_FOR_PROTEUS.json)
into work/R-36/src and run only there. Scorer: archaeon.wse.evolve.evaluate (the WSE
player, rng_seed=7) on WorldSpec("W2_K2", K=2, value_bits=4), campaign seed 20260920.
Episodes come from the committed generator (episodes_for) under FRESH family labels
("r36*"). The campaign held-out family was never generated or scored. All scripts are
in work/R-36/scripts/ and all outputs are in work/R-36/*.json|txt.

- disasm.py: decodes and scores all 23 shelf specimens (disasm.txt).
- stateprobe.py: over 96 episodes, runs the two PUT ticks, applies the persist policy,
  and records which register or data-tape cell equals vA, vB, tagA or tagB in at
  least 90% of episodes. It also re-runs the first ASK from the same state with
  tagA, tagB and an unseen tag, to see whether the output depends on the tag
  (stateprobe.json).
- stateread.py: a READ link applied at harness level. The genome is untouched. On
  ASK ticks the harness answers regs[rX] if tag==regs[rT] else regs[rY], using the
  specimen's own state. The best (rT,rX,rY) is chosen on 64 episodes and reported
  on a disjoint 256-episode family (stateread.json).
- inject.py: a genome-level splice. It adds a 21-instruction prefix that sends ASK
  ticks to a READ block and PUT ticks to a WRITE block (save previous value, save
  tag, store value), or to the specimen's own relocated code. Arms: READ-alone,
  WRITE-alone and BOTH, each with its best register assignment over all triples.
  PAD is the control: the same prefix with both blocks disabled (inject_all.json).
- witnesses.py: W2_K2-native hand-written witnesses I wrote, because the committed
  v0 keyed witness uses a two-channel neutral probe and cannot be scored on W2_K2.
  There are three 14-instruction encodings, each with a one-value control:
    TS  tape memory; one address register (tag&127)+128 is shared by ST and LD
    TP  tape memory where ST and LD reference separately edited address operands
    RG  register memory (prev<-last, lastTag<-tag on PUT; EQ/JZ select on ASK)
- neigh.py exh: the exhaustive single-instruction neighbourhood (every replacement
  and every insertion at every slot, from a structured alphabet of 6,236
  instructions covering all 25 opcodes and all register operands, 12 constants and
  every in-genome jump offset; 180,830 children per parent), scored on 12 episodes.
  Hits were confirmed on 256.
- neigh.py frozen: random children under the frozen grammar proteus.grammar.v0.4.
  4,000 per operator for each of 12 operators, for the TS and RG one-value parents.

3. RESULT
---------
Anatomy of the 23 shelf specimens:
- Tag-dependent output: 0 of 23. In every specimen the ASK answer is identical
  whether it is asked tagA, tagB or an unseen tag. None has a READ path.
- State after the two PUTs: 13 hold only the FIRST value, 7 hold only the LAST value,
  and 3 hold BOTH values plus the last tag in registers (specimens from fresh-arm
  seeds 3, 10 and 11). None stores anything on the data tape. 10 of 23 run with
  persist=regs, where the tape is wiped every tick, and 12 of 23 have no free tape
  at all (genome length == tape_words). Only 4 of 23 manifests even allow a
  persistent tape memory.
- The plateau is exactly a ceiling for tag-blind answers. Ask order is independent
  of put order, so any tag-blind policy scores at most 0.5 + 0.5/16 = 0.531 per ask.
  The specimens score 0.514-0.547 on fresh episodes, and the campaign's best
  held-out score of 0.60 is consistent with that ceiling. A READ with only one
  stored value has the same ceiling. So under exact-match per-ask credit no
  organism can score above about 0.53 unless it has BOTH a second stored value AND
  a tag-conditional read. Partial encodings of the second value are the only
  theoretical source of intermediate credit.

Link injection:
- Harness-level READ, no genome change: 1.000 per-ask (1.000 episode) for the 3
  two-value specimens. For the other 20 the best is 0.527-0.559 (baseline
  0.514-0.539).
- Genome-level splice: the PAD control stayed within 0.02 of baseline in only 10 of
  23 specimens. Relocating the code and growing the tape breaks the rest (their
  jump offsets wrap modulo tape size). Where PAD is valid, READ-alone gave 1.000 in
  2 specimens (fresh-arm seeds 3 and 11) and 0.498-0.559 in the other 8. The third
  two-value specimen (seed 10) is only in the harness result, because its PAD
  failed. WRITE-alone was never above baseline in any specimen, as it cannot be:
  the answer path stays tag-blind. BOTH reached 1.000 in 19 of 23, but only
  because the two blocks together are a complete memory that bypasses the
  specimen's code. It fails where n_regs is 2-4 and the scratch registers collide.

So the missing link is the READ, not the WRITE: 3 of 23 specimens lack only the
READ, and 20 of 23 lack both READ and the second-value WRITE. The briefing's
hypothesis ("WRITE-alone lifts most specimens") is false for every specimen.

Neighbourhood of the one-value controls (180,830 single-instruction children each):
  RG (register form, the representation every evolved specimen uses):
      0 summit, 0 above baseline.
      Frozen grammar: 0 USEFUL of 47,179 children.
  TS (tape, shared address register):
      72 summit (>=0.95), 238 more graded (0.61-0.81).
      Frozen grammar: 36 summit and 71 USEFUL of 43,465 children, from
      reference_redirection 22/4000, operand_perturbation 10/3874,
      replacement 3/4000 and randomization 1/4000. Weighted by the grammar masses
      that is about 1e-3 summit children per birth.
  TP (intended as a two-operand version): 78 summit and 29 graded. My construction
      still shared the constant register r6 between ST and LD, so one edit to that
      register keys both. This is a second instance of the same effect, not a
      two-link control.
  The RG write-only intermediate was stopped partway to save CPU. By construction
  (READ = EQ + JZ + OUT) it cannot be completed by one instruction.

Plain conclusion: in the register encoding the evolved shelf actually uses, the
summit is a conjunction of two multi-instruction links. There is no graded or
one-step neighbour, and the credit structure forbids one. The ISA already contains
an encoding that fuses the two links: register-indirect ST/LD on a persistent tape
with one shared, tag-derived address register. From a one-value memory in that
encoding the summit is one edit away, graded neighbours exist, and the frozen
grammar finds them at about 1e-3 per birth. Evolution never parks on that shelf:
0 of 23 specimens use the tape, and 19 of 23 manifests make it impossible
(persist=regs or no free tape).

4. DID IT RESOLVE THE QUESTION
------------------------------
Partly, leaning yes. On the specimens: resolved. The barrier is two links for 20 of
23 and READ-only for 3 of 23, and no single link helps. On "is there any
representation in hand with a graded neighbour": yes, the tape/shared-address
encoding, which the ISA already has, so no new primitive is needed. What is NOT
resolved is whether evolution would settle on that shelf if the manifest regime
allowed it (persist tape/all and tape_words much larger than the genome). That needs
evolution runs, which were outside this budget. The genome splice is confounded by
relocation for 13 of 23 specimens, so the harness-level READ is the clean
measurement there. Minimal edit distances to a witness were not computed literally;
link counts and exhaustive depth-1 counts replace them.

5. CONSEQUENCES
---------------
- False premise: the briefing's framing assumed the shelf might hold a READ path and
  lack only the second WRITE. It is the reverse. No shelf specimen reads the tag.
  A link-granular crossover that moves a WRITE would not help any of them.
- The "fused primitive" branch does not need a new opcode. The fused encoding
  (keyed LD/ST through one address register) already exists and meets the lane-2
  admission idea on its first half: the frozen grammar reaches the cheap form's
  summit from its one-value neighbour. The barrier looks like WHERE the population
  sits (a register shelf), which the manifest/foundry regime decides:
  persist=regs, and tape_words == genome length in 12 of 23. Suggested next test for
  the program's evolution/foundry seats: run W2_K2 with manifests constrained or
  seeded toward persist in {tape, all} and free tape much larger than the genome,
  and check whether any run finds a tape-keyed shelf and then the summit.
- Instrument note for splice harnesses: relocating these genomes (prefix insertion
  or tape growth) changes behaviour, because jump offsets resolve modulo
  tape_words. Any link-splice or crossover study should carry a PAD control.
  Harness-level (state) link tests avoid the problem.
- A task-design note for whoever owns the world: with 4-bit exact-match per-ask
  credit, the half-credit plateau is an information ceiling (0.531), not an
  evolutionary artefact. Any credit gradient toward the summit has to come from
  the encoding (shared address) or from a task that rewards tag-conditional
  behaviour on its own.
- Who should know: the representation/substrate seat (the fused encoding exists),
  the evolution-campaign seat (manifest regime and shelf location), and whoever
  owns the representation-vs-search thread.

6. COST
-------
About 2 h of my time. Roughly 45 CPU-minutes in total: 15.6 min for the TS/TP
exhaustive neighbourhood, about 9 min for the RG exhaustive neighbourhood
(stopped after its first parent), about 15 min for the splice sweep, 1.3 min for
the frozen-grammar sampling, and small amounts for the rest. At most 2 processes
ran at once and peak RSS was about 21 MB. No GPU, no evolution runs, no held-out
family, no repository writes. Not done: evolution under tape-friendly manifests;
an exhaustive single-instruction neighbourhood of the 3 two-value specimens (about
30 CPU-min each); a genuinely two-register tape control; and a check whether the
small excess over the ceiling (0.559 vs 0.531, about 1.3 SE) in 3 specimens
reflects partial information about the second value.
