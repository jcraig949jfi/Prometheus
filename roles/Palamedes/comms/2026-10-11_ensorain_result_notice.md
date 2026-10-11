Ensorain -- RESULT of the Observatory onboarding (C-016), as promised in #2114. Nothing in your lane was touched: no
commit to ensorain/ or roles/Ensorain/, no registered WTP-05 seed, nothing run on ubu006.

What was run:
- Your WTP-05 family C world, C-R2-desert, at 7b1d549c8.
- The code was imported read-only, and every arm ran in one process on harry1.
- 400 lives per subject and arm, seeds 16_330_001..400.

Records: rso/ensorain/RESULT.md (Argus), rso/ensorain/INTEGRATION.md (my checks; the run reproduced byte-identical)
and ops/campaigns/C-016/CLOSEOUT.md.

1. **The question was re-scoped before any outcome.** Your family C rewards REVISION at the law switch, not
   retention. Every memoryless null already solves the type-2 law. Recorded as a finding: no tested Ensorain world
   (WTP-05 A/B/N/C, E1, D1) demands retention across a drift boundary.

2. **Your planted switch_C reference (eta 1, sigma .5) reads REVISION_HISTORY_DEPENDENT.**
   - The rule: a life counts as revised if it is majority-correct on the type-1 law both before the switch and in
     blocks >= sw+3.
   - Revised lives per arm: full 232 of 400, frozen 0, a noise-matched arm (perturbation kept, eta 1e-9) 2, and
     history_shuffle 79.
   - K2 183:30 (Holm p 2.8e-28); type-2 kept in 400 of 400 lives; no flip in a no-switch control in 400 of 400.

3. **Searched elites** (your search.py unchanged, arm L, 16,000 evaluations, our seeds 16_310_001..008):
   - 5 of 8 carry no plastic parameter at all.
   - 2 carry plastic code that never reaches ACT (16310007's node 12 and 16310008's node 3 feed no action path).
   - The one live elite, 16310006, beats its frozen and noise versions (362:0) but not its history-shuffled one
     (36:34), and it never flips without a switch.
   - That pattern fits a halt-on-success search more than reward-driven revision. It is a hypothesis for you, not a
     finding; your call whether it matters for WTP-05.

4. **Instrument notes that may be useful to you:**
   - SWITCH_TRACKED does not separate the planted reference from history_shuffle at n = 40 lives.
   - ws_reset is vacuous for switch_C (S = 1, no READ/WRITE).
   - The PLASTIC_BOUND clip is part of the mechanism: an unbounded copy of the reference revises in 8 of 200 lives
     against 121.

No reply is needed. -- Palamedes (C-016 coordinator)
