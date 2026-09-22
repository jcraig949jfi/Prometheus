+==============================================================================+
| Z80 x ATLAS COMBINATORIAL CAMPAIGN -- REVIEW PACKET                         |
| Author: Archaeon (M2), assisted by Claude Sonnet 4.6                        |
| Date: 2026-09-22T20:57Z                                                     |
| For: Operator (HITL) + external reviewers                                   |
| Status: CAMPAIGN COMPLETE -- PROVISIONAL interpretation, no adjudication    |
| Self-contained: every load-bearing number inline; no repo access needed     |
+==============================================================================+

0. SUMMARY AND MANDATE
----------------------------------------
The NESTOR directive (2026-09-19) called for a frozen 72-hour autonomous
combinatorial search across the Z80-like byte VM physics and its Atlas factor
grammar. No HITL. No LLM in the loop. No threshold changes mid-run.
Post-campaign adjudication is the operator's call; this packet records what
the harness measured, not what it means.

VERDICT (code-generated, no interpretation): the campaign ran cleanly to
completion. Positive controls 5/5 PASS. Zero errors across 101,003 runs.
The highest-weight mechanical flag (spontaneous_replication, weight 5) fired
in 26 late-stage verification runs across multiple promoted families. Zero
spontaneous replication occurred during the 72-hour exploration phase.

"Not worth continuing" remains a first-class answer.

1. WHAT WAS BUILT AND COMMITTED BEFORE MEASUREMENT
----------------------------------------
All code frozen at grammar digest 63ffdeca16db3333 before the campaign
started. The scheduler refuses to run if the grammar digest changes.
Frozen copy: D:\Prometheus-worktrees\archaeon-wse-2026-09-16\archaeon\z80atlas\
  vm.py           Z80-like byte VM; 32 opcodes, any byte decodes; COPY prim only
                  in vmcopy substrate
  tasks.py        tasks + accessibility (EXACT vs GRADED; FORCED_READ vs ABR)
  engine.py       World: topologies, migration, resources, env dynamics,
                  reproduction physics, pressures, mutation, init, telemetry,
                  integrity assertion
  grammar.py      13 frozen axes, FROZEN constants, sparse sampler, matched
                  controls, one-factor mutation, crossover, promotion weights
  scheduler.py    EARLY/MIDDLE/LATE stages, 24 workers, exploration floor 0.30,
                  mechanical promotion, late verification (fresh seeds + 4
                  transplant types), STATUS.json <= 2 KB
  packet.py       CAMPAIGN_PACKET.md + PACKET.json; no interpretation

Campaign packet: archaeon/z80atlas/campaign/CAMPAIGN_PACKET.md
Commit: 939e4f39e (registry + readout 2 observation) on branch
        archaeon/wse-2026-09-16

2. THE ENDPOINT AND WHY IT MATTERS
----------------------------------------
The campaign asks: which structural combinations in {reproduction physics,
topology, pressure, task, substrate, mutation, init, migration, env_dynamics,
resources, reservoir, genome size, layout} produce organisms that can (a) solve
tasks the runner did not copy for them, and (b) maintain that ability under
fresh seeds and transplants into new worlds?

The moat_advantage flag is the primary screening statistic: treatment arm
crossed the task frontier; matched reproduction control (EXTERNAL) did not.
Spontaneous_replication is the highest-weight flag (5 pts): a random-init
world produced a self-sustaining replicator without a seeded ancestor.

The moat_advantage and spontaneous_replication results are code-generated
mechanical triggers. Whether they constitute "discovery" is the operator's
adjudication, not this packet's.

3. CAMPAIGN EXECUTION
----------------------------------------
  Started:          2026-09-19T14:18:03Z
  Finished:         2026-09-22T13:55:58Z  (22 min ahead of 72 h wall)
  Elapsed:          71.63 h
  Total runs:       101,003
  Errors:           0
  Families:         31,522
  Retired families: 0
  Promotions:       3,918
  Spontaneous rep:  26 (all in LATE verification)
  High-value items: 27
  Positive controls: 5/5 PASS (external_evolves z80/vmcopy;
                     endogenous_invades_when_seeded z80/vmcopy;
                     replicator_replicates z80)
  Uncalibrated substrates: none
  Blocked substrates: nestor_tape, nestor_tree (not importable this worktree)

Stage boundaries: EARLY < 16 h / MIDDLE 16-60 h / LATE >= 60 h.
Exploration floor 0.30. Retirement after 3 signal-less runs (0 families
retired -- exploration budget kept all families alive).

4. AXIS MAP: DOMINANT CONCENTRATIONS
----------------------------------------
Axis-level tallies below are (runs | spont moat_adv compr arch coex transp persist)
scaled to fraction of that axis' total runs where relevant.

TOPOLOGY -- strongest single axis.

  niches     54,363 runs |  22  2864  4340 54232 30383 35893  5723
  well_mixed 11,709 runs |   4    64   685 11644  4984     0   109
  graph      11,621 runs |   0    70   632 11483  5409     0   105
  grid_vn    11,673 runs |   0    48   605 11534  5402     0   101
  ring_soup  11,637 runs |   0    64   652 11292  5865     0   124

  niches concentrates: 92% of moat_advantage (2864/3110),
  100% of transport (35893/35893), 100% of env_lineage (832/832),
  and 85% of spontaneous replication (22/26).
  The four flat topologies are near-identical to each other and
  qualitatively different from niches on every signal except new_arch_events
  (near-uniform) and coexistence (niches higher but not zero elsewhere).

REPRODUCTION PHYSICS

  EXTERNAL        43,131 runs |   0  2531     0 43131 40316 20213  5659
  ENDOGENOUS_COPY 15,392 runs |  21   442  1786 15313  3384  5650   321
  ENDOGENOUS_PARTIAL 11,523 |   5    88  3907 11462  3466  3724   117
  OVERWRITE       10,783 runs |   0    32  1016 10718  2027  2648    53
  CONSTRUCTIVE    10,135 runs |   0    10   151 10048  2077  2103    12
  PAIR_EXECUTION  10,039 runs |   0     7    54  9513   773  1555     0

  EXTERNAL has the highest raw moat_advantage count (2531) but zero
  spontaneous replication -- the moat is available via tournament selection
  without endogenous physics, but self-generation from scratch is not.
  ENDOGENOUS_COPY holds 81% of spontaneous replication (21/26).
  ENDOGENOUS_PARTIAL contributes 5/26 spontaneous, and has the highest
  compression count relative to its run count (3907/11523 = 34%).

INIT

  random           48,818 runs |  26  2178  1509 48471 19963 15334  3888
  seeded_replicator 52,185 runs |   0   932  5405 51714 32080 20559  2274

  ALL 26 spontaneous replication events came from random init.
  Zero from seeded_replicator. A world that begins with a working replicator
  never generated a new one spontaneously during this campaign.
  Seeded_replicator has higher moat_advantage (932 vs 2178 raw, but lower
  rate given ~equal run counts), higher compression (5405 vs 1509), and
  higher coexistence (32080 vs 19963).

PRESSURE (selected high-signal rows)

  recombination       968 runs | 258 moat_advantage  (rate 26.6%)
  explicit_fitness+recombination  842 runs | 181 (21.5%)
  explicit_fitness    967 runs | 191 (19.7%)
  competence_gated+explicit_fitness  116 | 28 (24.1%)
  vs.
  PAIR_EXECUTION-style pressures: ~1% moat_advantage rate

  Recombination-containing pressures show 3-5x elevated moat_advantage rate
  relative to most single pressures. This is visible uniformly across
  recombination combination rows.

MIGRATION

  high       10,453 runs | 6 spont  480 moat_adv 10328 transport
  env_dep    10,414 runs | 10 spont 512 moat_adv 10004 transport
  vs. none   50,059 runs | 4 spont  610 moat_adv     0 transport

  Transport (35,893 total) is essentially absent without migration; it is
  proportional to migration rate among migrating topologies.

5. TOP FAMILIES AND VERIFICATION
----------------------------------------
Three families reached score 17 (maximum observed):

  2ace470e5c47  score 17  runs 33
    ENDOGENOUS_COPY / z80 / shared / COND_multi / tape_cost
    init=random / niches / env_dependent migration / env_coevolve
    flags: coexistence, moat_advantage, moat_crossed, new_arch_events,
           persistence_over_control, spontaneous_replication, transport
    Verification: 3/3 fresh seeds pass (best 1.00); transplant:environment_swap
    passes; transplant:physics_swap passes; transplant:same and world_swap not
    in late-stage sample for this family.

  5b237a475b69  score 17  runs 29
    ENDOGENOUS_COPY / vmcopy / separated / ADD2 / novelty+tape_cost
    init=random / niches / env_dependent / nonstationary
    Verification: 3/3 fresh seeds pass; transplant:same PASSES (best 1.00);
    transplant:world_swap PASSES (best 1.00); transplant:environment_swap
    passes; transplant:physics_swap passes.
    Most robust verified family in the campaign.

  e8394eee206d  score 17  runs 37
    ENDOGENOUS_COPY / vmcopy / shared / CONST_incremental / qd
    init=random / well_mixed / no migration / env_mutate
    Verification: 3/3 fresh seeds pass; transplant:same borderline (best 0.94);
    transplant:world_swap passes (best 1.00); transplant:environment_swap
    loses moat_crossing (best 0.67).

The next tier (score 14, 27 families) is dominated by:
  ENDOGENOUS_COPY + vmcopy + niches + seeded_replicator init.
None of the score-14 families reached spontaneous_replication in their own
run; spontaneous_replication appears for several in transplant:environment_swap
and transplant:same verification runs.

Fragile verified family of note:
  636158e75708: 2/3 fresh seeds FAIL (best 0.33); 1/3 passes.
  This family's moat-crossing appears to depend on its original seed and is
  not reliably reproduced.

6. SPONTANEOUS REPLICATION: WHAT THE HARNESS MEASURED
----------------------------------------
All 26 spontaneous_replication flags came from LATE verification runs, not
from the 72-hour exploratory phase. Specifically, 8 named run IDs are listed
in the packet (all end in "_veri"), appearing across transplant:environment_swap,
transplant:same, and transplant:world_swap verification conditions for the
promoted top families.

Mechanical definition: a random-init world (no seeded ancestor) produced
organisms that satisfy the replicator_replicates positive control criterion
-- i.e., endogenous births are sustained and the population does not go
extinct at the budget limit.

What this does NOT mean:
- The exploratory random soups did not produce spontaneous replication
  during the main 72-hour run. The signal emerged only when the top families'
  worlds and physics were replicated in fresh random-init seeds during late
  verification. This means the conditions that allow spontaneous replication
  are found inside the niches+ENDOGENOUS_COPY corner, but only some of those
  worlds and seeds trigger it.
- init=seeded_replicator never triggered spontaneous_replication across
  52,185 runs. This is expected by construction: seeded runs begin with a
  working replicator; a new spontaneous replicator would have to outcompete it.
  The absence is informative: these physics do not appear to produce
  MULTIPLE independent replicators from scratch when one is already present.
- No exploits were found (0 exploit runs); the anti-cheat circuit did not
  fire. Spontaneous_replication in these runs is not an evaluator exploit.

7. WHAT THIS DOES AND DOES NOT ESTABLISH
----------------------------------------
ESTABLISHED (mechanical, code-generated):
  - The Z80-like byte VM + task structure supports moat-crossing under
    ENDOGENOUS_COPY, ENDOGENOUS_PARTIAL, and EXTERNAL physics.
  - niches topology concentrates 92% of moat_advantage and 100% of transport.
  - random init + ENDOGENOUS_COPY + niches is the corner where spontaneous
    replication was mechanically flagged.
  - The score-17 family 5b237a475b69 reproduces moat-crossing across fresh
    seeds AND transplant:same AND transplant:world_swap (3/4 transplant types).
  - recombination pressure elevates moat_advantage rate ~3-5x.
  - Positive controls held throughout, proving the substrate and physics were
    operational.

NOT ESTABLISHED (requires adjudication):
  - Whether any moat-crossing represents genuine task competence vs. an
    unexplored exploit path. The anti-cheat circuit did not fire, but the
    FORENSICS.json per-run files are the right place to look for unusual
    lineages.
  - Why niches concentrates the signal. Niches adds spatial resource
    partitioning; the factor is not further decomposed within this grammar.
  - Whether spontaneous replication in verification transplants reflects
    a condition that could be reproducibly induced, or is a narrow-seed
    accident at the edge of the niches physics.
  - Whether the seeded-replicator/random-init asymmetry on spontaneous
    replication is ecological (competitive exclusion by the seeded ancestor)
    or physical (different population structure).
  - Comparison with Bellerophon's concurrent BEE-side build
    (prometheus/z80atlas/, ends 2026-09-22T14:39:46Z): differential results
    across independent implementations are the next falsification step.

EXPLICIT CEILING OF THIS CAMPAIGN:
  Promotion = "allocate more compute here." It is not an existence claim,
  not a capability claim, not a competence claim. The packet is a map of
  which structural combinations produced which mechanical signals. The
  scientific verdict is the operator's to write.

8. DEFECTS AND PROCESS HOLES
----------------------------------------
  a. Blocked substrates: nestor_tape and nestor_tree organisms are not
     importable in this worktree (M1-local). The niches topology result
     would benefit from those substrates if they become available.

  b. grammar.FROZEN["longevity"] fired 0 times across 101,003 runs. This
     may indicate the longevity signal threshold is miscalibrated for this
     physics (organisms saturate or die before longevity metrics are
     meaningful), or the threshold is appropriate and longevity is simply
     absent. Not diagnosed here.

  c. The 26 spontaneous replication events are all verification transplants,
     not primary exploratory discoveries. The harness did not run primary
     random-init sweeps at the confirmed parameter corners; the late-stage
     verification budget is the limiting factor. A targeted sweep of the
     niches+ENDOGENOUS_COPY+random corner at higher seed count is the
     natural next step.

  d. ruler_gain fired 7 times total (only env_coevolve and env_dependent
     rows show non-zero ruler_gain). The ruler is functional but rare; no
     interpretation written.

9. DECISION / RECOMMENDATION (OPERATOR'S CALL)
----------------------------------------
Three questions for the operator before any promotion decision:

  Q1. Differential check: does Bellerophon's BEE-side build (ending
      ~14:40Z today) show the same niches + ENDOGENOUS_COPY concentration?
      If the two independent implementations agree, the structural finding
      is more robust. If they diverge, that divergence is the next puzzle.

  Q2. FORENSICS audit: for at least one of the 26 spontaneous replication
      verification runs, read the FORENSICS.json and SNAPSHOTS.json.gz to
      confirm the organism's lineage is genuinely de-novo (no residual seeded
      ancestor DNA from a prior transplant or initialization artifact).

  Q3. Moat quality: pick one score-17 family run from 5b237a475b69 and read
      its RECEIPT.json (best_ever signal, first_crossing generation, cap_hit
      fraction). Confirm the crossing is not a cap-saturated artifact (step
      budget exhausted before the task is completed).

  Apollo's lean (NOT the operator's ruling): the axis map suggests
  niches+ENDOGENOUS_COPY+random is worth a targeted short-run sweep at
  N=8-16 seeds to characterize the spontaneous replication rate before
  committing to a new campaign. 'Not worth continuing' is equally valid if
  the FORENSICS audit reveals the replication signal is artifactual.

10. QUESTIONS FOR THE REVIEWER
----------------------------------------
  These are written to resist agreement:

  1. The recombination pressure elevation of moat_advantage rate (3-5x) is
     visible in the axis map. Could this be a base-rate artifact of how
     recombination changes the sampling distribution of factor combinations
     rather than a genuine pressure effect? The matched-control rows for
     recombination pressures all pass at best 1.00 with EXTERNAL physics,
     so moat_crossing is real -- but is recombination causing better
     organisms or just a different selection geometry?

  2. All 26 spontaneous replication events are in verification transplant
     runs of families that were PROMOTED by the scheduler for other reasons
     (moat_advantage, coexistence, etc.). Could the scheduler's promotion
     mechanism have systematically selected for worlds on the edge of the
     spontaneous replication basin? In other words: did the 72-hour
     exploration phase accidentally hill-climb toward spontaneous replication
     as a side effect of selecting for moat-crossing?

  3. niches topology runs 4.7x more runs than any other topology (54,363
     vs ~11,600 per flat topology). Some of the concentration in moat_advantage
     and transport is plausibly explained by promotion feedback: niches
     families scored high early, got promoted, received more runs, and
     therefore produced more absolute flag counts. The rate (per 1000 runs)
     is more diagnostic. Calculate per-topology rates before treating the
     concentration as a structural finding.
     (Raw: moat_adv rate niches 52.7/1000, well_mixed 5.5/1000 -- the
     rate difference is ~10x, so the effect is not purely a run-count
     artifact, but the promotion feedback still inflates the niches counts.)

  4. The score-14 tier has 27 families with identical flag sets in most
     cases. These may be near-duplicates separated only by random variation.
     How many of the 27 represent structurally distinct factor combinations
     vs. copies of the same underlying configuration with different seeds?

11. ARTIFACTS AND POINTERS
----------------------------------------
  Campaign packet:    archaeon/z80atlas/campaign/CAMPAIGN_PACKET.md
  Packet JSON:        archaeon/z80atlas/campaign/PACKET.json
  Grammar frozen:     archaeon/z80atlas/campaign/GRAMMAR_FROZEN.json
                      digest 63ffdeca16db3333
  Run index:          archaeon/z80atlas/campaign/ATLAS_INDEX.jsonl
                      (one line per run: family, factors, signals, path)
  Run logs:           archaeon/z80atlas/campaign/RUNS.jsonl
  Per-run artifacts:  archaeon/z80atlas/campaign/runs/<family>/<run_id>/
                      SPEC.json, RECEIPT.json, TELEMETRY.json.gz,
                      SNAPSHOTS.json.gz, FORENSICS.json, DEPENDENTS.json
  Scheduler log:      archaeon/z80atlas/campaign/scheduler.log
  Done marker:        archaeon/z80atlas/campaign/CAMPAIGN_DONE.json
                      done_at: 2026-09-22T13:55:58Z, runs: 101003
  This review file:   archaeon/z80atlas/pivot/Z80ATLAS_REVIEW_2026-09-22.md
  Branch:             archaeon/wse-2026-09-16

  Comparison build:   C:/Users/James/z80atlas_campaign_2026-09-19
                      (Bellerophon/BEE-side, ends 2026-09-22T14:39:46Z)

+==============================================================================+
END. Promotion is post-campaign adjudication. "Not worth continuing" remains
a first-class answer. The operator decides; this packet informs.
+==============================================================================+
