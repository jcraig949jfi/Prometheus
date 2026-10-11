# EXP-05 -- stig: ring RETURN or ACCUMULATION? (EXPLORATORY; prereg 2026-10-11 before any EXP-05 world was run)

Origin: EXP-04 showed stig usability rising with k (.42 -> .67 -> .82 at k = 2, 4, 8) while every local model
predicted decay. Two explanations:
- H-ACCUM: the substrate integrates cue-conditioned drive; usability grows monotonically with episode length.
- H-RETURN: the agent writes the cue at its cell (t = 0), moves v cells per step on a ring of L cells and senses
  +-1 cell; after the T = k + 2 steps of an episode it sits at v(k + 2) mod L. The cue is readable iff it is back
  within its window. Zero-parameter predictor R(v, k, L) = [ ring_dist(v(k + 2) mod L, 0) <= 1 ].
  Verified BEFORE this prereg on synthetic deterministic worlds only (delta .02, D 0, v 2, j 0; L 16 and 24;
  k in {3,6,7,8,14,22}): B accuracy 1.0 exactly where R = 1, chance where R = 0. Natural worlds add decay (delta),
  diffusion (D) and jitter (j), which blur R.

Design (DISCOVERY batch 3; prometheus/cosmos/c4/exp05.py; run under prometheus.cosmos.supervise):
- 60 stig worlds from the natural proposal P (split_seed DISCOVERY 3, 500000 + i); knobs as sampled.
- For each world: k = 1..40 at L = 16 (native) AND L = 24 (INTERVENTION on ring length only; every other knob
  and every seed held). Label: Certificate B linear accuracy -> excess (acc - .25) / .75.
- Controls: 20 rnn and 20 phase worlds (600000 + i, 700000 + i), k = 1..40, native; descriptive only.

Decisions fixed now (worlds with v >= 1; per world over k = 1..40):
- r16 = Pearson(excess at L16, R(v, k, 16)); r24 likewise; r24x = Pearson(excess at L24, R(v, k, 16)).
- H-RETURN SUPPORTED if median r16 >= .50 AND median r24 >= .50 AND r24 > r24x in >= 70% of worlds (the
  intervention moves the return pattern with L).
- H-ACCUM SUPPORTED if median Spearman(k, excess at L16) >= .50 AND median mean|excess L24 - excess L16| < .05
  (no dependence on ring length).
- Neither -> INCONCLUSIVE. Both -> INCONCLUSIVE (rules not exclusive in principle).
- v = 0 worlds: descriptive (H-RETURN predicts the cue is always in the window, so excess is set by decay only).
- Consequence if H-RETURN is SUPPORTED: stig's k-dependence is ring aliasing (geometric reachability, which is
  exactly what T3-DOWN encodes); the EXP-04 "rise with k" was a sampling artifact of k in {2, 4, 8} vs v; H-ACCUM
  is retired and no stationary-local law should be expected to predict stig.
