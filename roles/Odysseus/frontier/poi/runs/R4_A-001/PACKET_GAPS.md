R4_A-001 PACKET GAPS -- what R4 (and 00_READ_FIRST) did not tell me
==================================================================

Test of research-readiness. Each item is something I had to work out,
decide, or discover myself. Ordered by how much it cost or how much it
could change the result. "Cost" = my time / risk of a wrong answer.

G1  PRIOR ART NOT CITED (highest impact). The packet frames neutral walks
    from the shelf as new. They are not:
    - C4-05 (archaeon/campaign4/C4-05/READOUT.md, c4_05.py) already ran
      4 walkers x 16 neutral steps from ALL 57 parents including the 19
      shelf parents (same band, same CRN episodes) and found the network
      fully connected (188/188 walkers to depth 16, ~55% acceptance).
      It measured held-out exaptation, NOT own-environment improvement,
      and its walk loop silently rejects improving proposals (band test
      is |r - r0| <= 1/16) without logging them.
    - C5-01 replicated to depth 64 (raw/I4 TH-I4-06).
    - C3-SFE-02 (archaeon/campaign3/CAMPAIGN_REPORT.md s4): 12 shelf
      elites x 400 children, 1/4,800 "useful" (r > parent + 1/32), and
      0/480 greedy 3-step paths reaching 0.90. That is a direct prior
      answer to "improvement within k=3" by a stronger (greedy) search.
    The packet cites raw/I4 TH-I4-02/04/06, which mention these, but it
    does not say "these exist; your contribution is X". A worker could
    easily re-run C4-05 and call it new.

G2  "THE SUMMIT IS KNOWN" -- IT IS NOT, IN GIT. No W2_K2 summit genotype
    exists in the repo. proteus/eval/keyed_memory_witness.py is a
    keyed-memory witness for a DIFFERENT two-channel protocol, not W2_K2
    (it says so). raw/I4 s5 D4 proposes hand-writing one; nobody did. I
    wrote one (18 instructions, r4lib.summit_genome, 1.0 train and 1.0 on
    64 held-out episodes). Also, "nearest summit genotype" is ill-posed:
    the summit set is infinite, so any distance to a known member is an
    UPPER bound only. The packet should say which distance it wants.

G3  CONTROLS UNDERSPECIFIED AND ONE IS UNDERPOWERED BY CONSTRUCTION.
    - Positive control: "a planted parent one neutral step from a known
      improvement must be found at k=2" gives no construction, no
      probe budget, no pass rule. With a budgeted sample of edits, the
      detection probability is a power question, and a random neutral
      step rarely IS the planted neutral step. My preregistered version
      FAILED (0/16 walkers) for both reasons; a forced-path version
      passed (12/32 seeds at L=2, 0/32 at L=1). See PREREG_AMENDMENTS A1.
    - Negative control: "shuffled evaluator (improvement undefined)" and
      "the chance floor" are not defined (shuffle what? floor computed
      how?). I used a fixed permutation of the 32 expected answers (S_A)
      and an independent permutation (S_B) as the floor.
    - Matched random-sampling and random-walk baselines are required by
      00_READ_FIRST but not defined for this packet; I defined RW (accept
      any edit) and RS (compound (d+1)-edit mutants of the parent).

G4  "TEST ALL SINGLE EDITS" IS NOT POSSIBLE. The grammar's edits include
    uniform 32-bit words (replacement, insertion, reference_redirection,
    randomization); the neighbourhood is not enumerable. The packet
    allows "a budgeted sample; report which" but gives no default, no
    operator distribution (frozen weights vs census-uniform over the 12
    operators), and no power target. I used the census design (12 ops x
    4 draws = 48 per genotype).

G5  NEUTRALITY AND IMPROVEMENT ARE ANCHORED WHERE? Band relative to the
    ORIGINAL parent (C4-05) or to the current genotype? Improvement vs
    original parent or vs current? With a current-anchored band a walk
    can ratchet upward inside the band and "improve" by accumulation. I
    anchored both to the original parent (C4-05 convention) and also
    logged improvement-vs-current. The primary threshold (D7, > 1/16)
    vs C3-SFE-02's "useful" (> +1/32) was also unstated; I report both.

G6  UNIT OF THE PREREGISTERED FRACTION. "the fraction of k-step neutral
    walks that reach an improvement" -- per probe, per walk, per parent?
    Walks from one parent are not independent (19 parents only). Number
    of walkers per parent unspecified. I report all three levels.

G7  THE 19 PARENTS ARE NOT ONE KIND. 17 score 17/32 = 0.531 (one-value
    memories, both-asks-correct 1/16 episodes) and 2 score 22/32 = 0.6875
    with both-asks-correct 11/16 episodes: those two answer BOTH streams
    in most episodes. Worked out later (RESULT.md): they are POSITIONAL
    two-value memories whose 0.6875 is an ask-order skew in the 16 CRN
    episodes (10/16 ask order == put order); on 2,000 episodes all 19
    parents score 0.529-0.536. The packet (and S3) carry "0.531 or
    0.688" as two real levels; neither warns that 16 episodes / 32 asks
    is too few to rank shelf variants.

G8  EVALUATOR LOCATION / RUNTIME FACTS. "find them from the attempt
    directory" works but costs time. The exact call is
    archaeon.wse.evolve.evaluate(m, episodes_for(W2_K2 = WorldSpec("W2_K2",
    K=2, value_bits=4), 20260921, "train", 1, 16), rng_seed=0,
    reward_mode="per_ask"), with sys.path = repo root +
    SerendipityFoundry/SerendipityFoundryClient; ~30-36 ms per evaluation
    per core; 16 episodes = 32 asks (reward granularity 1/32). None of
    this is in the packet.

G9  NO HELD-OUT REPLICATION ASKED FOR. 32 asks with 4-bit values means a
    child can gain 2-3 asks by value coincidence. The packet's decision
    rule for "connected" would accept an episode-set overfit. I added
    re-evaluation on 64 fresh episodes (train family, index 2).

G10 RULES THAT DID NOT FIT THE RUN CONTEXT (resolved by the operator's
    local adjustments, recorded here for the packet author): output path
    roles/<seat>/poi_R4/ vs "write only under the output path" vs
    "update nothing in roles/Odysseus/"; "commit prereg in its own
    commit" when the worker may not commit; comms posting.

G11 MACHINE CONTENTION NOT ANTICIPATED. The 4-core laptop had load
    average ~12 from other processes during my run; the packet's "2-4 h"
    and I4's "50 ms/eval" budgets assume an idle machine. Wall times in
    RESULT.md are under contention.

G12 NOOP EDITS. The eligibility rule for noop edits (at_max, too_short,
    bounds) is in C4-01, not in the packet; small shelf parents with full
    tapes lose ~25% of probes to noops (e.g. the 8-instruction parent,
    tape 32 words: insertion/duplication always at_max).
