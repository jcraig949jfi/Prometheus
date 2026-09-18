+=====================================================================+
|  C4-09 -- LATERAL EXAPTATION / PAIRED ECOLOGY: PREREGISTRATION       |
|  Archaeon[m2-49ee5a4d]   2026-09-18   Status: DRAFT, NO ROW RUN      |
+=====================================================================+

QUESTION (directive)
  Are we destroying useful stepping stones merely because they are bad
  at the environment that produced their parent?

THE ECOLOGY (frozen, cheap, related)
  Four worlds: W0 (K=1), W1_d1 (delay 1), W1_d4 (delay 4), W2_K2 (K=2),
  all 4-bit, the C4 environments. Each world carries its own population
  (N=50) evolving on its own training episodes (E=16, CRN); the same
  starting population in every world: the 188 depth-16 C4-05 walkers
  (digest-verified), subsampled to 50 by the world's rng. Held-out probe
  of each world's elite every 10 generations (48 held-out episodes).
  New neighbouring worlds are NOT generated (the optional clause is not
  taken; the ecology is the four fixed worlds).

ARMS (equal PRIMARY budget: 4 worlds x N=50 x G=100 x E=16; 3 seeds)
  control   a child that fails in its world ends there (ordinary
            selection: it simply does not reproduce)
  lateral   after each generation's evaluation, every child of that
            generation that is BELOW THE FLOOR in its own world
            (reward_per_ask < 3/16) but NOT degenerate (answered_share
            > 0) is a candidate; up to B=24 candidates per world per
            generation (in id order, no ranking) are evaluated on the
            other three worlds (the FIXED transfer budget: at most 3 x
            24 evaluations per world per generation); a candidate ENTERS
            a receiving world's population (replacing its worst member,
            via the evolver's inject) iff its reward there is >= 3/16
            AND >= that world's current population median fitness. No
            classifier predicts anything; only the measured reward there.
  The lateral arm's transfer evaluations are the extra compute and are
  counted, not hidden.

MEASUREMENTS (per arm, per seed, per world; pooled)
  rescues                 candidates that entered another world; the
                          transfer matrix (from -> to)
  rescue survival         share of rescued organisms whose descendants
                          (origins carry "rescued") are present in the
                          receiving world at G=100; share that became
                          that world's elite at any probe
  cross-world improvement receiving world's held-out best at G=100 vs
                          control's, per world
  novelty                 distinct held-out elite behaviours per world
  extra compute           transfer evaluations / primary evaluations

PREDICTIONS (written to be lost)
  P1  rescue survival at G=100 >= 0.25 (rescued lineages persist)
  P2  at least one world's held-out best is higher in the lateral arm
      than in the control arm by >= 1/16 in >= 2 of 3 seeds
  FAILURE SHAPE (the directive's): almost every rescue is permissive
  survival with no downstream consequence = rescue survival < 0.10 AND
  no world improved in >= 2 seeds -> "lateral evaluation is overhead".

CONTROLS
  positive   an injected organism (the receiving world's own elite,
             re-entered under the rescued tag in a dry pass) survives
             to the next generation: the inject path keeps what it
             should (tested in the self-test, not in the run)
  negative   with B=0 the lateral arm equals the control arm trace for
             trace (the machinery adds nothing when it does nothing)
  cheat      a hand-set candidate with reward 1.0 on another world is
             rescued
  determinism  seed 1 control reproduces its traces

DISPOSITIONS
  SUPPORTED if P1 and P2 hold; NEGATIVE (overhead) if the failure shape
  holds; INCONCLUSIVE otherwise (rescues persist but improve nothing, or
  improve without persisting); INSTRUMENT_INVALID on a control failure.

RECORDS
  one engine world; one observation per (arm, seed) with the four
  worlds' traces and the transfer matrix; rows.json.
