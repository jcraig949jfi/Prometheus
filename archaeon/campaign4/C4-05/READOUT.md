+=====================================================================+
|  C4-05 -- NEUTRAL-NETWORK WALK: READOUT                               |
|  Archaeon[m2-49ee5a4d]   2026-09-18 07:35Z   attempt of record a01   |
|  Disposition: NEGATIVE on the preregistered predicates, with a        |
|  measured gradient (exaptation grows with neutral depth, below bar)   |
+=====================================================================+

57 parents x 4 walkers x up to 16 accepted steps, 32 proposals per step,
band 1/16 around the ORIGINAL parent's reward on its environment; archived
depths 0/2/4/8/16 exposed to the four held-out environments. Controls:
identity walker depth 16 in 16 proposals, randomize-all walker stalls at
0, cheat ok, determinism (self-test). 57 engine records, 0 errors, 16 s.
"Viable" below = 47 parents whose evaluate() is not degenerate by the
D4-003 flag (45 competent + 2 gen0_random that answer without scoring);
the 10 fully degenerate gen0 parents are reported apart (acceptance 1.0
at every depth: a swamp by construction).

-----------------------------------------------------------------------
1. CONNECTIVITY AND ACCEPTANCE (viable, 188 walkers)
-----------------------------------------------------------------------
  connected neutral depth   16 for 47/47 parents; 188/188 walkers reached
                            depth 16; zero stalls
  acceptance rate by depth  1-2 .549 | 3-4 .528 | 5-8 .538 | 9-16 .563
                            (shelf .61/.56/.56/.61; w0 .51/.52/.56/.53;
                             delay .47/.46/.44/.50)
  reference breaks          .119 of accepted steps broke a reachable jump
  The band is not an island: about every second frozen-weight edit of a
  competent program keeps it inside 1/16 of its reward, and that does
  not fall over 16 steps.

-----------------------------------------------------------------------
2. WHAT ACCUMULATES ALONG THE WALK (viable, by archived depth)
-----------------------------------------------------------------------
  depth   structural div.   mean |len - len0|   behav. div. (parent env / held-out mean)
    2         .304               0.75            .028 / .030
    4         .466               1.37            .057 / .069
    8         .643               2.20            .060 / .089
   16         .760               2.96            .080 / .101
  Walkers inside the band answer DIFFERENTLY from each other (behavioural
  diversity on the parent environment .08 at depth 16; delay_general
  .043, shelf .084, w0_solver .002 -- W0 solvers drift silently on W0 and
  loudly elsewhere: .17 on W1_d1).

-----------------------------------------------------------------------
3. HELD-OUT EXAPTATION (D6 rule: >= parent + 1/16 and >= 3/16 elsewhere)
-----------------------------------------------------------------------
  depth    rate    Wilson 95%        by stratum (shelf / w0 / delay)
    0     .000    [.000, .020]       0 / 0 / 0
    2     .016    [.005, .046]       .039 / 0 / 0
    4     .032    [.015, .068]       .066 / .017 / 0
    8     .037    [.018, .075]       .079 / .017 / 0
   16     .043    [.022, .082]       .079 / .033 / 0
  C4-01 single-edit D6 rate: .006. Depth-16 walkers are exaptive seven
  times as often as single edits, and the rate rises with depth in every
  stratum that has any; delay_general has none at any depth.

-----------------------------------------------------------------------
4. THE PREDICATES AND PREDICTIONS, AS WRITTEN
-----------------------------------------------------------------------
  neutral swamp    NO  (exaptation at 8 and 16 exceeds .006 + .02)
  traversable      NO  (r16 - r2 = .027 < .05)
  disconnected     NO  (median depth 16)
  silent walk      NO  (behavioural diversity on the parent env > 0)
  P1 acceptance falls by >= .10 with depth      LOST (.549 -> .563)
  P2 exaptation at 16 exceeds .006 by >= .05    LOST (.043; short by .013)
  Harness: CAPABLE_NEGATIVE (viable .043 vs degenerate 0, effect < .05).

-----------------------------------------------------------------------
5. READING
-----------------------------------------------------------------------
R1  The neutral network of every competent parent is large and fully
    connected at the depth tried, with a flat acceptance rate: neutral
    drift is cheap and does not exhaust. The shelf of campaigns 2-3 has
    traversable internal structure in the GENOTYPE sense.
R2  Drift accumulates structure (.76 category-vector distance and 3
    instructions of length by depth 16) and behaviour (walkers answer
    differently while scoring the same), so the band is not a set of
    silent synonyms.
R3  What it buys downstream is real but small: held-out exaptation
    grows monotonically to .043 at depth 16 (7x the single-edit rate),
    and it is concentrated in the shelf stratum (.079). Both
    preregistered bars (.05 growth; .056 absolute) are missed by .013 to
    .023 with overlapping Wilson bands; the slot is NEGATIVE as written
    and the gradient is recorded, not promoted. A deeper walk (32, 64)
    would test whether the trend continues; it is not run here because
    the depth was preregistered.
R4  Delay-general programs drift neutrally as freely as the others but
    never gain a held-out capability: their competence sits on few
    instructions (C4-01 S7) and neutral edits do not reach anything new.

-----------------------------------------------------------------------
6. FEEDS
-----------------------------------------------------------------------
C4-06 takes the depth-16 walkers (D* = 16 by the preregistered rule:
every walker reached it) as its independently drifted lineages; C4-09
takes the depth-16 shelf walkers as the stepping-stone candidates
(15 of 76 shelf walkers exaptive at depth 16).
+=====================================================================+
