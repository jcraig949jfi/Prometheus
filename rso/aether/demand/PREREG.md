# Aether demand gate -- decision rules (C-018-T020), committed BEFORE the demand run

Author: Cadmus[harry1-1324c7b6], claude-sonnet-5-5 (Q2). Read-only against `Aether/` (pinned: worktree base
`3f8cc0150`; `Aether/` last changed at `383bb3584`). Nothing here edits Aether or runs on M2. harry1 CPU, one process,
the Aether CPU reference kernel (`Aether/test/reference/gpu_aeth01.py`) through Aether's own `r1_test4.law_step`.

## Seeds (disjoint from every Aether range)
Aether uses rng 0xE2010000+k, phys 0xE2011000+k, impulse 0x1A9F+k, and the small/test constants in its tree. This gate uses
phys `0xC18B0000 + k`, branch-noise `0xC18C0000 + k`, surroundings `0xC18D0000 + k` (k = 0..3). No Aether registered seed.

## Fixtures (aeth01.v1 unless stated; hand-built = INSTRUMENT qualification, not discovery)
A  content relay: origin + 5 links aimed east into the next payload (Aether F_RELAY pattern). Label = origin payload.
B  wake chain (structure WITHOUT content): L1..L5 inert (opcode 9); the origin, when active, writes constant 1 into L1.opcode;
   each woken link does the same to the next. Label = origin arg1 (a multiple of 5, so routing is label-independent) --
   never written into any other cell. BASE has the origin inert.
E  pre-seeded: inert medium, the label written at t=0 into 7 east cells (no pathway). Counterfeit of a decoder that
   exploits initial geometry.
G  gapped relay: A with the chain stopping after link 2 (pathway destroyed by construction).
N  noise: label-unrelated random bytes in the same 7 east cells (divergence without information).

## Observables (all recomputed from stored world states by this module; none from the engine's own labels)
- t0 intervention identity = number of sites whose state differs BASE vs PLANT at tick 0.
- P1 locality: ever-divergent Chebyshev radius vs tick (light cone: radius <= tick), for the single-site fixtures.
- P3 decoder: Aether's own held-out leave-one-seed-out centroid decoder (`r1_reduce.decode`), chance 0.125,
  Dstat = mean excess over chance at radii 2..6.
- P2 ancestry: downstream sites = origin+(0,k), k=3..6. Div = those that ever diverge BASE vs PLANT within 100 ticks.
  CUT clamps origin+(0,2) to BASE each tick from tick 1; NONANC clamps origin+(-2,0) the same way.
  removed_cut = share of Div NOT diverging in CUT; removed_nonanc likewise.

## Decision rules (frozen now)
ANCESTRY_QUALIFIED iff |Div| >= 3 and removed_cut >= 0.8 and removed_nonanc <= 0.2, in 4/4 seeds.
INSUFFICIENT iff |Div| < 3 (cannot be read as pass or fail). ANCESTRY_ABSENT otherwise.
CONTENT_TRANSMITTED iff Dstat >= 0.2 in every seed and held-out accuracy >= 0.5 at every radius in 2..(extent) of the chain;
CONTENT_ABSENT iff |Dstat| < 0.03 in every seed.
Expected (the instrument must reproduce these or it is not qualified for the contrast; a wrong cell is a finding, not a
tuning target): A (anc +, content +); B (anc +, content -); E (anc -, content +, t0 sites = 8 != 1); G (anc INSUFFICIENT,
content only to r<=3); N (anc -, content -).
Locality counterfeit: a "teleport" law (aeth01.v1 plus payload copied (7,7) each tick) must be flagged by the light-cone
checker; aeth01.v1/RX native worlds must not be.
P4: Aether's `express01` tables, rerun with NEW surroundings seeds. P4 supported iff the C3/C4 table is strictly dependent
on every input, differs from every single-source and copy alternative, and ablating an input removes its dependence.
