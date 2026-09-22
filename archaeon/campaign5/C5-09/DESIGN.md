+=====================================================================+
|  C5-09 -- REACH / DISCOVERY TEST: PREREGISTRATION                     |
|  Archaeon[m2-49ee5a4d]   2026-09-18   Status: DRAFT, NO ROW RUN      |
|  Campaign 5, Phase B (written while C5-05 runs, before it reports)   |
+=====================================================================+

QUESTION. On worlds with measured headroom that the old substrate did
not climb (C5-02: the elite sat at the starting parent in most cells
for 36,000 evaluations), does evolution under representation B discover
more, at EQUAL TOTAL COMPUTE, than under the old representation -- and
if it does, is it the representation or the grammar?

WORLDS. The four screened Phase-A worlds (W2_K2d1, W2_K2_rand, W3_K3,
W4_K4; receipt WORLD_SCREEN_2026-09-18.json). W3_K3d1 and W2_K2d4 are
held out for C5-10 and are NOT touched here.

ARMS (identical N=50, G=100, E=16, seeds 1-6, starting subsample of the
57 CANONICAL parents by the seed's rng -- the same 50 programs in every
arm; total evaluations identical by construction: 4 x 50 x 100 per seed)
  OLD_v04      old evaluator, grammar v0.4            (the baseline)
  OLD_B        old evaluator, grammar B               (grammar only)
  B_FAIL       representation B FAIL, grammar B
  B_FIZZLE     representation B FIZZLE, grammar B
Held-out probe of the elite every 10 generations and at the end (48
held-out episodes, family heldout, index = seed).

PER CELL (world x seed) AGAINST OLD_v04 (band 1/16 on final held-out):
  WON  arm - OLD_v04 >= 1/16;  LOST  <= -1/16;  else TIED.
  net(arm) = WON - LOST over the 24 cells.
DISCOVERY TELEMETRY (reported): generation of first held-out gain over
the starting best; number of distinct held-out levels the elite passed;
crossing share, trapped share, faulted share of the population per
generation (B arms); elite genome length; elite fault sites (FIZZLE).

READINGS (fixed; C5-10/RULE.md reads the same numbers)
  DISCOVERY_GAIN(arm) iff net(arm) >= +4 AND net(OLD_B) < +4
  GRAMMAR_GAIN iff net(OLD_B) >= +4
  NO_GAIN otherwise
  Prediction written to be lost: NO_GAIN for both B arms (the flat elite
  of C5-02 is a property of the worlds and the parents, not of how
  programs die).

CONTROLS: OLD_v04 seed 1 trace equals a re-run (determinism); the four
arms' generation-0 populations are identical program for program; the
starting best held-out per world equals the screen receipt's best among
the 50 sampled (<= the receipt's best over 57).
