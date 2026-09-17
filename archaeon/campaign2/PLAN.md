# Campaign 2 -- the ten experiments (Phase B plan; fixed before C2-SFE-01 runs)

Selection rule (directive section 5): mandatory priorities first (five slots),
then successors that discriminate between explanations campaign 1 exposed.
Every row names its parent(s), the campaign-1 observation that motivates it,
the machine changes it exercises, and the question it discriminates. Budgets
are the SMALLEST that can pose the question; every target is chosen from
archaeon/campaign2/REACHABILITY.jsonl (table at Phase A close reproduced in
MACHINE_READINESS.md's evidence).

Reachability facts that fixed the choices (baseline runs, E0):
  4-bit  W2_K2 N200 G60 E16   4/9  REACHABLE  (first solved 48,50,54,59)
  4-bit  W1_d4 N200 G60 E16   1/6  RARE       (52)
  4-bit  W1_d1 N200 G60 E16   0/3  OBSERVED_UNREACHABLE_AT_BUDGET
  4-bit  W3_K2 N100 G40 E16   0/3  OBSERVED_UNREACHABLE_AT_BUDGET
  4-bit  W0                   UNESTABLISHED (no baseline row; producers in
                              SFE-10 solved it 1/6 at G12)
  8-bit  W1_d1 N200 G100 E24  2/3  REACHABLE  (49,79)     <- SFE-09's control
  8-bit  W0    N200 G100 E24  2/3  REACHABLE  (19,77)
  8-bit  W1_d4 N200 G100 E24  0/3  OBSERVED_UNREACHABLE_AT_BUDGET
  8-bit  W3_K2 N200 G100 E24  2/3  REACHABLE  (3,45)

-----------------------------------------------------------------------
C2-SFE-01  FAILURE-EPISODE TRANSPORT ON A REACHABLE TARGET      parent SFE-03
  motivation  SFE-03 never posed its question: W1_d4 was RARE (now 1/6).
  question    do transported failure episodes from a structurally relevant
              source raise held-out competence on the target above fresh
              search and above random-compatible transport, at matched
              evaluation budget?
  target      W2_K2 4-bit N200 G60 E16 (REACHABLE 4/9); six seeds so a 0/6
              baseline would itself be evidence (P < 0.04 at freq 0.44).
  arms        fresh | relevant (source W2_K2 8-bit: every structural knob equal,
              value width differs) | random (source W7_K2 4-bit: K=2, ASK2).
              k=8 transported episodes REPLACE 8 of the 16 training episodes
              every generation (matched evaluations), fed through the step API
              (no monkeypatching); the transport count is a row field.
  machine     A (target from the table), B (TARGET_UNREACHABLE /
              INTERVENTION_NOT_APPLIED / IMMATURE_ARTIFACT on the packs), C, D,
              E (packs carry maturity), G (episodes injected per step), I.
C2-SFE-02  REPRESENTATION: POSITIVE CONTROL FIRST, OPERATOR MASS MATCHED    parent SFE-09
  motivation  SFE-09's positive control (A on W1_d1 4-bit G60) was 0/3; L-029.
  question    (gate) does A_words reach W1_d1 8-bit N200 G100 E24 in >= 2 of 6
              seeds? (science, only if the gate passes) do field
              representations with the SAME operator mass reach the cell A
              cannot (W1_d4 8-bit, 0/3 at this budget) or reach W1_d1 faster?
  arms        A_words | B_fields | C_fields_class, mass-matched to the grammar's
              twelve weights; cells control W1_d1 and stuck W1_d4; six seeds;
              identical generation 0.
  machine     A, B (POSITIVE_CONTROL_FAILED stops the comparison), C, G, H
              (operator histograms per arm as a mass check), I.
C2-SFE-03  FALSIFY SFE-01's COMPONENT EFFECT                      parent SFE-01
  motivation  components 2/3 vs random segments 0/3 at n=3; source immature.
  question    is "spliced component segments from an above-floor source seed
              footholds on W2_K2" cheaper than it looks? Battery (each arm at
              n=12, common fill, same target): random_segments (original
              control), shuffled_components (composition kept, order lost),
              opcode_matched (opcodes kept, operands random), position_front
              (insertion position), self_segments (segments of the target's
              own gen-0 organisms: generic nonrandom material), other_lineage
              (components from a second source seed), mature_source
              (components from a source that SOLVED its cell: W0 4-bit run to
              solution). Claim survives an attack only if components beat the
              attack arm by the preregistered margin.
  machine     B (battery in decl; SUPPORTED needs every attack survived), C, E, H
              (genome/opcode summaries of every set), I.
C2-SFE-04  FALSIFY SFE-07's FAILED-GENOTYPE SEEDING               parent SFE-07 (+SFE-08)
  motivation  failed whole genotypes 2/3 vs random 0/3 (n=3); organs carried
              nothing (SFE-08); SFE-07's random fill was harness-seeded.
  question    what is the smallest description of what a failed W1_d1
              population transports to W3_K2? Battery at n=10: random |
              failed_A | failed_shuffled (instruction order) | failed_opcodes
              (operands random) | length_matched_random | manifest_matched_random
              | evolved_unrelated (floor genotypes of a W7_K2 search:
              relatedness) | evolved_solved (W0 solvers: maturity).
  machine     B, C (common fill for every set), E (maturity on every set), H, I.
C2-SFE-05  RETENTION REPLAY WITH A PROVEN-CAPABLE STREAM          parent SFE-02
  motivation  two streams (1024, 4096) held nothing above the sealed threshold.
  question    (gate) does the stream contain an organism scoring >= 0.5 on at
              least one sealed query cell? (science) do retention policies
              differ in prospective solve fraction under one cap?
  design      stream = every organism a W2_K2 4-bit search evaluates, run by
              the step API until 5 generations past its first solver (cap 70);
              capability checked on the sealed queries BEFORE freezing;
              threshold sealed at 0.5 and never touched; six seeds.
  machine     B (STREAM_BELOW_THRESHOLD from the check), G (stop rule), I.
C2-SFE-06  RETENTION ECONOMICS ON A RUNG LADDER                   parent SFE-05
  motivation  the battery mean hid a forgetting shelf (fixed/on lost Kd-0).
  question    under a schedule that moves the pressure up the Kd ladder, at
              what revisit rate p of earlier rungs (an ecological pressure, not
              a memory reward) does retained rung-0 competence stop costing
              top-rung competence? Arms p in {0, 0.1, 0.25, 0.5}; rung x
              generation matrix every 5 generations; shelf report per arm.
  machine     G (spec changes per step), H (rung x generation, shelf_report), I.
C2-SFE-07  PRODUCER-CONSUMER: MATURITY GATING AND WALL-CLOCK      parent SFE-10
  motivation  only a producer that SOLVED its cell paid; immature artifacts cost.
  question    does division of labour pay when (a) producers publish only once
              they have solved (gated, charged serially) or (b) producers run
              on their own clock in parallel and the consumer imports when an
              artifact exists (wall-clock accounting)? Comm and storage costs
              preserved. Arms mono | gated_serial | parallel | noex controls.
  machine     E (gate = maturity.solved), G (consumer imports mid-run), D, I.
C2-SFE-08  ENCODING GEOMETRY: WHAT PREDICTS SEARCH EFFICIENCY     parent SFE-06
  motivation  more accessible variation searched slower (L-023).
  question    over many encodings of one fixed evaluator, which preregistered
              neighbourhood statistic (accessible variation, useful variation,
              local improvement probability, greedy path length, deceptive
              branching, threshold reachability) rank-correlates with
              evaluations-to-first-hit? Encodings: direct, 6 balanced, 6
              scrambled; 4 score tables (seeds); exhaustive 4096-genotype
              neighbourhood statistics per encoding.
  machine     I (the criterion is preregistered; every statistic reported).
C2-SFE-09  CA SUBSTRATE: DISTRIBUTED vs REDUNDANT vs ARTIFACT      parent SFE-04
  motivation  0.608 with a flat lesion map; the leakage probe was never wired.
  question    which of four explanations survives: distributed computation,
              redundant/local computation invisible to single lesions, readout
              artifact (reset coupling), frozen dynamical bias? Measurements:
              reset-only readout (probe wired), cumulative greedy vs random
              lesion curves, time-shuffled features, input-shuffled control.
  machine     H (the missing telemetry L-019), I.
C2-SFE-10  FUNCTION-BEARING ORGANS                                 parent SFE-08 (+SFE-07, SFE-01)
  motivation  length-defined organs carried nothing; whole genotypes did.
  question    do organs defined by KNOCKOUT LOAD (instructions whose removal
              changes the organism's behaviour on probe episodes of its own
              cell) transfer where length-defined organs did not? Sets:
              functional-organ chimeras, length-organ chimeras (old
              definition), shuffled functional organs, whole ancestors, random.
  machine     H (load maps as telemetry), B, C, I.
-----------------------------------------------------------------------
Order: 01, 02, 03, 04, 05 (mandatory), then 06-10. Each: preregister ->
dry run -> capability gate where declared -> run -> machine disposition ->
addendum -> next.
