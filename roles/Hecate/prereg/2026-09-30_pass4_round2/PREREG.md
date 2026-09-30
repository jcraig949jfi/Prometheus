# PREREG -- Hecate Pass 4 (first falsification), round 2

Frozen: 2026-09-30Z, before any Pass 4 round-2 code exists. Author:
Hecate[m1-dd0c3882]. Targets: the round-3 SIGNALs
(hecate/programs/PROBE_ROUND3_REPORT.json, 88bb37ada). Common rules as
../2026-09-30_pass4_round1/PREREG.md (R replication, ORIG trivial-
explanation attack, ALT alternative implementation, controls reported
before any treatment statistic), plus two changes from round 1:

1. Every ALT world is built control-first (as ../2026-09-30_pass3_v2/):
   its positive control, cheat and null twin are run and must make every
   ALT clause attainable and discriminating BEFORE any treatment code for
   the ALT world exists. If not: ALT NOT_ELIGIBLE (recorded), no repair
   after a treatment statistic exists.
2. Arithmetic check (calibration ledger row 2): for each attack, the
   outcome expected under the "known mechanism" hypothesis is written
   below BEFORE freezing, and no attack is admitted whose outcome is
   fixed by counting or construction.

Predicate per world, computed in code: SURVIVES iff R reproduces AND ALT
passes AND controls detected; ORIG firing FOSSILs the original-world
claim regardless. Consequences as round 1 (SURVIVES -> PROMISING;
ORIG_FOSSIL_ALT_PASS -> PROBING; ALT fails or NOT_ELIGIBLE -> PARK).

## HT-8a87057933 W5 (core-guided forgetting)

  R    seeds 100-109: errors ratio vs drop-oldest <= 0.50 and 10/10 seeds.
  ORIG channel-reset heuristic, no SAT: on a violated observation, drop
       every stored clause about the mismatched channel. Kill if its
       total errors <= 1.10 x core-guided errors.
       Expected under the known-mechanism hypothesis: round 3 found every
       minimal unsatisfiable core was a same-channel pair, so the
       heuristic should match core-guided and ORIG should FIRE.
  ALT  a plant whose stored clauses are relations ACROSS channel pairs,
       so a conflict's minimal core spans channels and the mismatched
       channel does not identify the stale clause. Pass iff core-guided
       errors <= 0.50 x drop-oldest AND <= 0.80 x the channel-reset
       heuristic, 10 seeds.
       Arithmetic check: not fixed. Channel-reset may delete valid
       cross-channel clauses; core-guided deletes a clause from a minimal
       core but may pick the wrong one when a core holds several stale
       candidates. Either can win.

## HT-55162c0ac0 W6 (perturbation-spread grouping)

  R    fresh seeds: grouping score >= 0.8 on >= 9/10 seeds; correlation
       grouping stays at chance.
  ORIG non-chaotic carrier with the same coupling graph and noise (a
       contracting map, largest Lyapunov exponent < 0). Kill if the same
       perturbation-spread readout also groups >= 0.8: chaos is not
       needed, and the mechanism is perturbation-response network
       inference (prior art to be labelled KNOWN_ANALOGUE_FOUND).
       Expected under the known-mechanism hypothesis: linear response
       propagates along couplings in a stable system, so ORIG should FIRE.
  ALT  sweep the carrier from contracting to chaotic over >= 5 levels at
       matched coupling and noise. Pass iff the mean grouping score at
       every chaotic level exceeds that at every non-chaotic level by
       >= 0.2 AND Spearman(Lyapunov exponent, score) >= 0.6.
       Arithmetic check: not fixed. Under the known-mechanism hypothesis
       the score should be flat or fall with chaos (chaos scrambles
       response), so ALT is expected to FAIL; under the triplicate's claim
       it rises.

## Budget

<= 10 CPU core-minutes per world. MWO-0004 R2.
