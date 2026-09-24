# C3 Session 1 -- PREREGISTRATION of the remaining substitution attacks (WITHHELD until D seals)

Written 2026-09-24 ~20:10Z, before the three families below exist. Operator decision 2026-09-24:
"Complete communication/population/recomputation substitution attacks ... If they break the
abstraction, then the law is not ready for D." The law is NOT modified here; the chaotic graph scar is
NOT patched.

## 1. Law under attack (preliminary, from S1_RESULT.md; no refit)
FUNCTIONAL iff sR > 0.0304 (sR from geometry.py, unchanged).

## 2. The three families (no explicit internal memory in any agent; retention may or may not arise)
COMM   two memoryless agents: a SENDER that sees the observations and a RECEIVER that answers. Each step
       the sender emits a d-dim message tanh(g_in U onehot(obs) + g W_s m_R) and the receiver emits
       tanh(g W_r m_S) (+ channel noise sigma on every message in flight). Messages in flight are the
       ONLY persistent state. The receiver's readout sees the message it just received + the current
       observation. Knobs: loop gain g, channel noise sigma, d.
POP    a population of M units, each holding one observation symbol (or blank). Each step: each unit
       copies a uniformly random unit with prob c; each unit adopts the CURRENT observation symbol with
       prob beta (units imprint on whatever they observe -- cue or distractor alike); each unit mutates to
       a uniform random symbol with prob mu. The actor's readout sees the symbol counts in a random
       sample of s units (+ the current observation). State = the population. Knobs: beta, mu, c, s.
RECOMP a discrete scrambler: z in {0..Z-1}; at t = 0 z is set by the observed symbol; afterwards
       z <- pi(z) for a fixed random permutation pi (distractors are ignored), and with prob eta z is
       replaced by a uniform random state. The cue is never STORED; it is RECOMPUTABLE by inverting pi^t.
       The actor's readout sees a random linear projection of onehot(z) to r dims (r = Z: the full state).
       Knobs: eta, r.
Each family: 24 worlds from its lattice (seed 20260927), k in {2, 4, 8}, certificate v3, coordinates as
in S1 (geometry.py, unchanged).

## 3. Criteria (fixed now)
Per family, over non-INDETERMINATE worlds: agreement of the law's prediction with the certificate.
  HOLDS      agreement >= 0.85 AND no single failure SHAPE accounts for >= 3 misses
  BREAKS     agreement < 0.85, or a single shape with >= 3 misses (reported with its coordinates)
Overall: the abstraction survives substitution iff all three families HOLD. If any BREAKS, the law is
NOT ready for D (operator), and the break is reported as a scar, not patched in Session 1.
Also reported: where history lives (P1 on the full state vs the actor's view; PASSIVE counts).

## 4. Precommitments
S1 COMM holds (loop gain carries history; sR sees it in the receiver's view).                      0.6
S2 POP holds but with PASSIVE worlds at small s (history in the population, not in a small sample). 0.5
S3 RECOMP breaks at small r: the projection keeps distance (sR > 0) but a LINEAR readout cannot use
   the scrambled code -- geometric signal without linearly usable information.                     0.5
