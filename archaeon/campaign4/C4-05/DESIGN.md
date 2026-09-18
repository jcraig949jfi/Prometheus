+=====================================================================+
|  C4-05 -- NEUTRAL-NETWORK WALK: PREREGISTRATION                       |
|  Archaeon[m2-49ee5a4d]   2026-09-18   Status: DRAFT, NO ROW RUN      |
+=====================================================================+

QUESTION (directive)
  Can lineages move through genotype space while preserving current
  competence, and does such movement expose new reachable behaviours?

PARENTS AND ENVIRONMENTS
  The 57 starting program variants; parent environment per stratum
  (D4-004); the SAME CRN episode sets as C4-01/02 (family train, index
  1, E=16). The 12 gen0_random parents are DEGENERATE on their
  environment (C4-01): any walk from them is a neutral swamp BY
  CONSTRUCTION (reward 0 stays 0). They are walked and reported in their
  own row, never pooled with the 45 viable parents.

THE WALK (bounded, no selection for the later challenge)
  4 walkers per parent, seeds (campaign_seed, organism_id, "walk", w).
  A step proposes ONE frozen-weight grammar edit (name=None) of the
  current walker; it is ACCEPTED iff the child's reward_per_ask on the
  parent environment is within the equivalence band of the ORIGINAL
  parent's reward (|r - r0| <= 1/16, D4-003), else rejected and another
  proposal drawn. At most 32 proposals per step; if none is accepted the
  walker STALLS at its current depth. Maximum depth 16. Steps whose
  operator returned its noop record are not steps (do not count toward
  the 32 and do not advance depth).
  Recorded per accepted step: operator, args, proposals tried, whether
  the step broke a reachable jump (C4-04's reference_facts), the
  structural descriptor after the step.
  Archived: the walker's manifest at depths 0, 2, 4, 8, 16 (or its last
  depth if stalled earlier, marked stalled).

MEASUREMENTS
  connected neutral depth   per parent: max depth reached by any walker;
                            per walker: depth at stall or 16
  acceptance rate           accepted / proposals, by depth bin (1-2, 3-4,
                            5-8, 9-16)
  structural diversity      mean pairwise L1 distance between the
                            walkers' opcode histograms (normalized by
                            instruction count) and mean |len - len0|, by
                            archived depth
  behavioural diversity     mean pairwise displacement among a parent's
                            walkers on the parent environment (inside
                            the band, so silent vs distinct), and on
                            each held-out environment, by archived depth
  held-out exaptation       share of archived walkers at depth d that
                            score >= parent(there) + 1/16 AND >= 3/16 on
                            any held-out environment (D6 rule), by depth;
                            depth 0 is the parent's own rate (0 by
                            definition) -- so the comparison is depth d
                            vs the C4-01 single-edit D6 rate (.006)
  reference breaks          share of accepted steps that broke a jump

SHAPES (predicates, before any row)
  neutral swamp    median connected depth over viable parents >= 8 AND
                   held-out exaptation at depth 8 and 16 <= C4-01's
                   single-edit rate + 0.02
  traversable      median connected depth >= 8 AND exaptation at depth
                   16 > depth-2 rate by >= 0.05 (later behaviour grows
                   with neutral distance)
  disconnected     median connected depth < 4 (the band is an island)
  silent walk      behavioural diversity on the parent environment stays
                   0 at every depth (the walkers never change what they
                   answer) -- structural drift without behavioural drift

PREDICTIONS (written to be lost)
  P1  acceptance rate in depth bin 9-16 is lower than in bin 1-2 by
      >= 0.10 (walkers drift into more brittle programs)
  P2  held-out exaptation at depth 16 exceeds C4-01's single-edit D6
      rate (.006) by >= 0.05

CONTROLS
  positive   a walker whose every proposal is the identity edit reaches
             depth 16 in 16 proposals with displacement 0 (the acceptance
             machinery accepts what it should)
  negative   a walker whose every proposal is whole-genome randomization
             stalls at depth 0 on every viable parent (rejects what it
             should)
  cheat      a hand-set archived walker with reward 1.0 on a held-out
             environment reads exaptive
  determinism  one parent's walk reproduces byte-for-byte on rerun

DISPOSITIONS
  SUPPORTED if traversable in >= 1 viable stratum; NEGATIVE if neutral
  swamp or disconnected or silent walk in every viable stratum;
  INSTRUMENT_INVALID on a control failure. gen0_random reported apart.

RECORDS
  one engine world; one observation per parent (walk summary, archived
  digests, held-out scores); rows.json; steps.json.gz with every step.
