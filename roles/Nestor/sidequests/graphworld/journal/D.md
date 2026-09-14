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
