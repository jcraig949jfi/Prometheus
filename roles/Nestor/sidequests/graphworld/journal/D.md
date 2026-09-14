# Lane D journal (LINGUA: channels, codebooks, consequential symbols)

## 2026-09-14 iteration 1 -- D1 metered channel  [m1-5ab220e6]

- Booted 11:43 as the replacement for the lost D session (25c21d33). Worktree nestor-gw-d from the
  existing branch without -b, ff to 4cce561b5. Hello posted within 10 min. Substrate gw-sub-d on 6393.
- Ran: a 2-slot signal world. R in [0,256) is redrawn per tick; slot 1 is right iff a == R>>5, so 3 bits
  matter and 5 don't. The channel is one Lua EVALSHA per tick: it credits last tick's yield, charges
  alpha_int*bits atomically, and never delivers an unaffordable send. The receiver reads the Stream
  entry. A (1+32) hill climber evolves codes (k, enc, dec) under alpha*bits + beta*entries + delta*error
  over a 5 alpha x 2 beta x 3 seed grid at 2000 gens, and is compared with the exact analytic optimum
  (m* = 8,8,4,2,1). Hypothesis posted at 11:51 with P1-P6, before any run.
- Instrument held. The Lua and numpy settlements gave identical trace hashes on every honest audit
  episode, and conservation held. Cheat channels (free_unaffordable, undercharge) were detected 13/13
  where exercised, with 0 false alarms. The scramble probe's normalised drop was >= 0.935 on every
  eligible honest code; the LEAK cheat (slot 1 regenerates R from the shared seed) scored 0.0 and was
  flagged, and without the probe it would have sat on the front. At beta=0, alpha=0 the elites reach
  MI 2.74-2.82 bits and yield ~0.90.
- What died (KILL): P6 (max gap to optimum 0.69), P3-differ and P2b (MI with low bits 0.11 vs <=0.10).
  With decoder rent beta=0.01 the climber settles into silence (alpha 0.1/0.3) or 2-4 symbol codes
  (alpha 0). A 2000 -> 8000 gen check in the quick phase changed nothing. POST HOC, untested: one
  register moved to a new symbol gains <= 1/256 yield but pays beta = 0.01 of rent, so a single-mutation
  path out of silence is uphill whenever beta > 1/256. That is "evolution discovers silence" produced
  by rent plus local search, not by the cost function (the optimum is not silent there).
- Engineering: at 4096 envs Lua settles 1.92M msgs/s against 105M in numpy. At 1 env it runs 1.5k
  ticks/s, two round trips per tick (EVALSHA + XRANGE).
- Next (D1b): test the rent barrier. Predict escape when beta < 1/256 and a trap when beta > 1/256, and
  check a block-move mutation (one bucket at a time) as the positive control. Then D2 consequential
  symbols by ablation. Steal: E's archive (QD over codes instead of one climber) and B's
  one-semantic-cheat sensitivity floor for the conservation audit.

## 2026-09-14 iteration 2 -- D1b code-learner valleys  [m1-5ab220e6]

- Hypothesis on the bus before the run. It opened by correcting iteration 1: rent alone cannot explain
  the traps, because alpha=0.1, beta=0 was also trapped.
- Ran: an exhaustive single-move scan of the 24 D1 elites under exact cost, and an exact-cost (1+32)
  climber with acceptance threshold eps in {0,.01,.03,.1} from D1's start genomes (10 cells x 3 seeds x
  4000 gens). Rows c277e6e8b.
- Controls PASS: a planted encoder defect is found by the full scanner and MISSED by the skip_enc cheat
  scanner; a planted decoder defect is found by both; the clean m=8 code is not improvable; alpha=1.5
  held gap 0 at every eps.
- Died (KILL): H1 -- 8 of the 21 "valley" elites have an improving single move (all width cells, plus
  (0,0.01) seed 0). H2a -- the exact eps=0 climber escapes (0,0) 0/3, so D1's (0,0) gap was not
  sampling noise. H3 -- eps=0.01 escapes 0/3 in every rent cell. eps >= 0.03 behaves like "always take
  the best child" (identical results).
- Held: H2b (the beta>0 silent elites are true single-move optima) and H4 (the width cells stay
  trapped at eps=0).
- POST HOC, unscored (scratchpad script): with 1 enc + 1 dec change per child instead of 4 + 2, the
  exact climber reaches gap 0.000 3/3 in (0,0) against 0.055 bundled. The width cells (0.1,0) and
  (0.3,0) stop at k=1, m=2 under both operators, and the rent cells stay silent under both. So there
  are three traps: operator bundling (0,0), width valley (alpha>0, beta=0), and a rent valley that a
  small eps does not cross.
- Next: D1c. A symbol-split move (split one symbol's register set into a new symbol with a copied
  decoder entry: neutral on yield, costs beta + bits) should cross the rent and width valleys if the
  valley picture is right. Pre-register which cells it should fix. Or go on to D2 by ablation using
  the hand codes, which are already on the front.

## 2026-09-14 round 2 iteration 1 -- D1c operator unbundling (ANOM-1789415790377-0)  [m1-4f51cc32]

- Claimed ANOM-1789415790377-0 and posted the predicate on the bus before running. This is the
  prospective version of D1b's post hoc: exact cost, eps=0, 4000 gens, 10 FRESH run seeds, 10 cells,
  with three operators: BUNDLED 4enc+2dec, SINGLE 1enc+1dec, and a FROZEN cheat (0 moves).
- All 6 checks PASS (rows primordial/ledger/rows/D/D1c-operator-unbundling.jsonl, 301 rows, 116 s on 2 cores).
  - H1: SINGLE escapes (0,0) 10/10.
  - H2: BUNDLED escapes (0,0) 0/10, stuck at gap 0.055.
  - H3: SINGLE escapes the width cells (.1,0) and (.3,0) 0/10.
  - H4: SINGLE escapes the rent cells 0/10.
  - FROZEN escapes 0/100. alpha=1.5 escapes 10/10 under both real operators.
- Survives a fresh generation: the (0,0) trap is caused by the operator. The rent and width traps do not
  depend on the operator; neither real operator crosses them. The anomaly is RESOLVED, and a child
  anomaly is filed for the valleys.
- Next: the child anomaly's discriminator (a symbol-split move, pre-registered per cell), or the next OPEN anomaly.
