# cw01-e09 — Substrate reconciliation (FIRST ACTION; decides whether e09 can be posed)

Written at HEAD 10ece30ba, after e08 closed. Answers the brief's seven questions from the
code, then reports one bounded probe (PROBE_E09.json, 32 s, no production seed, nothing
frozen) of the only composition form the substrate already owns. e08 is not reopened.

## The organism and its one act

The evolved organism is the tensor-train policy (`primordial/brain/genomes.py:213-263`):
observation digits -> contraction -> one action index in `[0, 8)` -> codebook row
(`uint8 [A, W]`) -> action vector. The world applies it as
(`primordial/soup/b1/np_world.py:92-102`, semantics copied from wforge `world.py:212-229`):

    x = action % 8                       # 3 bits of magnitude per action channel
    charge -= x.sum() * act_cost         # if affordable
    pend[target] += x * 251              # lands after `delay` ticks; w13: one target, register 5

Then the world's own fixed affine maps run on every register every tick
(`np_world.py:112-114`), the yield rule pays on a window of register 5, and the organism
observes a fixed projection of registers plus its charge bucket (`np_world.py:65-85`).

## The seven questions

1. **What can an organism call or compose?** Nothing. Its only act is to add one 3-bit
   magnitude times 251 to one fixed world register. It selects no operation, invokes no
   transform, and cannot address any register but the world's action target.
2. **Can the result of one operation become the input of another?** Only through the
   world: the nudge lands in register 5, the world's affine maps transform every register,
   and the organism may observe register 5 next tick. The composition is the world's
   (`lin_ops`, fixed by the world genome), not the organism's.
3. **Can an operation be invoked more than once?** The single nudge fires every tick;
   there is no other operation to invoke.
4. **Can intermediate results remain addressable?** World registers persist and a subset
   is observable, but they are world state under uncontrollable transforms, not
   organism-produced intermediates; the organism cannot allocate, name or protect one.
5. **What execution costs can be counted exactly?** `act_cost` per unit magnitude,
   `step_cost` per live slot-tick, TT flops per act (e08's burden vector). Exactly, yes.
6. **What representation controls operation choice, arguments, sequencing, reuse?**
   None. The TT chooses a codebook row; the row is a constant. There is no program, no
   dataflow, no argument, no sequence beyond the tick clock.
7. **What existing mechanism would accidentally provide equivalent composition in the
   control arm?** The world's `lin_ops` compose affine maps for EVERY arm every tick, and
   in two-slot worlds two organisms write into one register bank. Any soup would sit on
   top of a world that already composes, identically for all arms.

Other candidates inspected: `lingua/` (a 2-slot signal code, `signal.py:1-17`; encoder/
decoder tables, no operation composition); `soup/b2` (relations under GraphBLAS, no
organism, no action channel; cohort C aborted on it); the representation ecology's
**`program` kind** (`brain/c3_ecology.py:20-27, 56, 133-136`): a straight-line chain
`(((x_a o1 x_b) o2 x_c) o3 x_d) mod 16` over hex digits with ops add/sub/mul/xor/and/or,
fit by exhaustive search on a static regression target and never used as a world policy.
That chain is the ONLY substrate-native form in which one operation's output feeds
another. It has invocation, identity, order and dependency; it has no reuse (each
intermediate has exactly one consumer) and no workspace.

## The probe: can the substrate's own chain form pose the question in w13?

Organism = 4 digit indices + 3 op ids; action magnitude = value mod 8. Selection on the 8
train seeds; every capability number on held64 (seeds 30000..30063). Competence floor
166.47 (ledger), abstain floor 159.0.

| construction | train fitness (abstain 1272) | held64 | competent? |
|---|---|---|---|
| single op, exhaustive over 6 x 20 x 20 = 2400 | max 1386 | best-by-train 142.5; max over the top 64 = 159.0 | 0 / 64 |
| 3-op arithmetic chain, 4 pilot lineages x 150 gens x 128 | 1661 / 1828 / 1738 / 1723 | 145.6 / 148.7 / 145.9 / 145.9 | 0 / 4 |
| 3-op SCRAMBLED chain (seeded random 16x16 op tables) | 1844 / 1729 / 1868 / 1774 | 158.3 / 166.2 / 154.9 / 148.6 | 0 / 4 |

Reading: composition raises TRAIN fitness (depth 3 reaches 1828 where depth 1 reaches
1386) and none of it survives the held-out assay; every chain is at or below the
abstain floor on held64. The scrambled tables do as well as the arithmetic ones, so what
the chains fit is seed-specific structure, not usable primitive semantics. The primitive
ceiling on held64 is the floor itself, and no legal composition exceeds it.

## Decision

Meaningful composition is impossible in the present substrate: the organism owns no
call, no composition and no reuse mechanism; the only workspace is the world's register
bank behind a 3-bit write channel and uncontrollable transforms; exposing a soup would
require inventing a program representation with a private workspace, which the brief
forbids; and the one substrate-native chain form cannot exceed its own primitive ceiling
on held-out seeds. e09 is closed INCONCLUSIVE / DESIGN UNREACHABLE at reconcile, before
preregistration, without spending on a counterfeit instrument.

## What a future e09 needs (recorded, not built)

A substrate whose organism can select, invoke and chain operations over an addressable
workspace it owns, with reuse expressible as one intermediate feeding two consumers; and
a world in which capability generalises from the training seeds to held-out seeds, so
that a primitive ceiling and an above-ceiling target both exist on the assay
distribution. In this substrate that is a new organism family and a new world screen, not
an interface.
