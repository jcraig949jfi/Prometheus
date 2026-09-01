================================================================================
EXTERNAL REVIEW PACKET
LUDUS ARENA -- first vertical slice: five executable worlds, one interface
================================================================================
Prepared:        2026-09-01   draft, unaudited
Location/Code:   F:\Prometheus\ludus\arena\   (1,218 lines, 4 modules)
Artifacts:       roles/Ludus/arena_verification_2026-09-01.txt (full run)
Version/Hash:    arena 0.1.0; commit dabede3ad on ludus/atlas-of-game-worlds
Predecessor:     REVIEW_PACKET_3_2026-09-01.md (the Atlas breadth phase)
Headline:        20/20 verification checks pass across 5 structurally different
                 worlds and ~19,830 seeded episodes. The proposed sequential
                 interface BROKE on three of five worlds and was redesigned.
                 One defect found and fixed. Nothing is rule-audited; no
                 transfer claimed; no world admitted to any scored experiment.

Format note: single plain-ASCII block, as with packet #3. The whole file is the
copy-paste unit.

CORRECTION TO A FIGURE ALREADY IN THE RECORD: commit dabede3ad's message says
"16/16 groups pass". The correct count is 20 individual checks, all passing.
The commit message understates the count; no result changes.

--------------------------------------------------------------------------------
1. CLAIM / SUBJECT UNDER REVIEW
--------------------------------------------------------------------------------
CLAIM: a single world/player interface can host radically heterogeneous games
without special-casing them, and the resulting simulators can be verified
against ground truth established independently of this code.

This is the mandate's section 22 vertical slice. Its purpose was NOT to
demonstrate that a universal interface works. It was to find out WHERE it
breaks, early, on cheap games, rather than on the day something needs
stress-testing.

PRE-REGISTERED FALSIFIERS, and what happened to each:

  (a) The interface cannot express a game without per-game escape hatches.
      PARTIALLY CONFIRMED. The proposed sequential form failed on three of
      five worlds and required a structural change -- see section 9, F1.
      After the change, no world needed an escape hatch.

  (b) Simulators produce results contradicting known theory.
      NOT OBSERVED. Five independent ground-truth results reproduced; see
      section 6.

  (c) Episodes are not reproducible.
      OBSERVED, THEN FIXED. Determinism failed on all five worlds on the
      first run -- see section 9, D1.

  (d) The environment leaks information a player should not have.
      NOT OBSERVED, and explicitly tested for Kuhn poker.

NOT CLAIMED: that any ruleset is correct, that any world is ready for a scored
experiment, that any reasoning mechanism transfers, or that these five worlds
are a benchmark.

--------------------------------------------------------------------------------
2. METHOD / SETUP / SUBSTRATE
--------------------------------------------------------------------------------
Python 3.12.10, standard library only. No external dependencies, no network.

  Module        Lines   Role
  -----------   -----   ------------------------------------------------
  core.py         423   World / State / Player contracts, episode runner,
                        replay, invariant validator
  worlds.py       445   the five world implementations
  players.py      171   baseline and ground-truth players
  verify.py       179   the W6 verification harness
  utf8.py           9   stdout encoding

THREE OBJECTS, SEPARATED DELIBERATELY

  World    rules + parameters. Immutable. Identifies a ruleset version.
           Section 7's distinction made concrete: what identifies the GAME
           lives in the class; what identifies THIS INSTANCE lives in params.
           Two Worlds differing only in params are counterfactual neighbours,
           which is what one-axis perturbation testing will need.

  State    one episode in progress. clone / state_hash / serialize / validate.

  Player   chooses among legal actions. Receives an observation and a legal
           action list, and nothing else.

THE ENVIRONMENT CONTAINS OBJECTIVE TRUTH ONLY. legal_actions() is in the World.
There is no hook through which a strategy oracle could be reached: a World
cannot call a Player. This was an explicit design constraint from the mandate
(section 8) and it is enforced structurally, not by convention.

--------------------------------------------------------------------------------
3. GROUND TRUTH AND KEY DEFINITIONS
--------------------------------------------------------------------------------
Every world in the slice was selected because a result about it is known
INDEPENDENTLY of this implementation. That is what separates W5 (it runs) from
W6 (it runs correctly).

  World         External result relied upon
  -----------   ----------------------------------------------------------
  TIC_TAC_TOE   perfect play draws (minimax value 0)
  NIM           Bouton (1901): the player to move loses exactly when the
                XOR of heap sizes is zero
  PIG           a fair d6; the bust rule forfeits the accumulated turn pot
  RPS           uniform play is a Nash equilibrium with value 0
  KUHN_POKER    Kuhn (1950): the game value is -1/18 to player 0 under
                equilibrium play

WHAT A GREEN RUN PROVES, PRECISELY: that IF the encoded rules are correct, the
machinery does not corrupt them. It says nothing about whether the encoded
rules match any published rulebook. That is a separate gate (W3) and no world
here has passed it.

RULE PROVENANCE, recorded per world using the Atlas vocabulary:
  TIC_TAC_TOE, RPS ......... COMMUNITY_CONSENSUS (folk games, no publisher)
  NIM, PIG, KUHN_POKER ..... EXPERT_INTERPRETATION (Bouton; Neller and
                             Presser; Kuhn)
  OFFICIAL_RULE ............ zero worlds

--------------------------------------------------------------------------------
4. WORLD SELECTION AND JUSTIFICATION
--------------------------------------------------------------------------------
Selection was structural, not by title. Each world was chosen to stress a
different assumption in the proposed interface.

  World         Stresses                          Structural cell
  -----------   -------------------------------   -------------------------
  TIC_TAC_TOE   baseline; nothing unusual         NONE / PERFECT / STRICT
  NIM           closed-form solution as an         NONE / PERFECT / EXACT
                oracle over the harness
  PIG           CHANCE nodes; a live STOP axis     IID / TOTAL_RUIN /
                                                   RACE_TO_TARGET
  RPS           SIMULTANEOUS action; no turn       NONE / SIMULTANEOUS
                order exists to hold an id
  KUHN_POKER    PRIVATE observation; chance;       DEPLETING_DECK /
                imperfect information              HIDDEN_PRIVATE

PIG IS IN THE SLICE FOR A SPECIFIC REASON. Its accumulate-or-bank decision
under risk of losing the whole turn pot is the same shape as the bench's r0003,
the circuit currently blocked at PARTNER_ROBUST. A hold-at-N player is r0003 in
one line. This is the cheapest available executable instance of the structure
the bench cannot presently vary.

DELIBERATELY INCLUDED TRIVIAL GAMES. Mandate section 16 asks for calibration.
Tic-tac-toe and one-round RPS are trivial by construction; a system that
"succeeds" at them has demonstrated nothing, and knowing that requires having
them in hand.

--------------------------------------------------------------------------------
5. PROCEDURE AND METRICS
--------------------------------------------------------------------------------
Episode loop, per step:
  1. validate the state (invariants below)
  2. read current_player() -> player id | CHANCE | SIMULTANEOUS
  3. dispatch:
       CHANCE        draw from chance_outcomes() using the episode RNG
       SIMULTANEOUS  collect one action per player, apply together
       player id     show observation(p), take one action
  4. record a Step: actor, state hash before and after, legal actions,
     chosen action, description, per-step rewards, elapsed ms
  5. on termination, record returns() and notify players

INVARIANTS CHECKED AT EVERY STEP OF EVERY EPISODE
  - a non-terminal player-to-move state has at least one legal action
  - a CHANCE node has outcomes whose probabilities sum to 1 and are >= 0
  - a terminal state reports current_player() == TERMINAL
  - returns() has one numeric entry per player, at terminal states only
  - observation(p) is constructible for every p without raising
  - the applied action was in the legal action list
  - the episode terminates within max_steps

DETERMINISM CONTRACT: the same (world spec, seed, player classes) must
reproduce the same episode. Verified by digest comparison, not by eyeball.

TOTAL EPISODES IN THE VERIFICATION RUN: approximately 19,830.
  invariants     2,000   (5 worlds x 400)
  determinism       10
  minimax           20
  nim              800
  pig            1,000   (+ ~15,970 chance draws inspected)
  rps            4,000
  kuhn          12,000

--------------------------------------------------------------------------------
6. PRIMARY RESULT
--------------------------------------------------------------------------------
20 checks, 20 pass, 0 fail. Full output in
roles/Ludus/arena_verification_2026-09-01.txt.

INVARIANTS AND TERMINATION (random play, 400 episodes each)

  World                  Steps/ep   mean p0   Violations   Non-terminating
  --------------------   --------   -------   ----------   ---------------
  TIC_TAC_TOE                 7.6    +0.203            0                 0
  NIM                         6.2    +0.000            0                 0
  PIG                       185.8    +0.007            0                 0
  ROCK_PAPER_SCISSORS         1.0    +0.093            0                 0
  KUHN_POKER                  4.2    +0.167            0                 0

  Note: mean p0 under RANDOM play is not a result about the game; it is a
  first-mover artifact. It is reported because a wildly asymmetric value
  would indicate an encoding error, and none is present.

GROUND-TRUTH REPRODUCTION

  Check                                    Theory      Observed    Delta
  --------------------------------------   ---------   ---------   --------
  Nim (3,4,5), XOR=2, optimal vs random     +1.0000     +1.0000     0.0000
  Nim (1,2,3), XOR=0, optimal vs optimal    -1.0000     -1.0000     0.0000
  Tic-tac-toe, minimax vs minimax            draw        20/20        --
  Pig, P(bust face) over 15,970 rolls        0.16667     0.1679     0.0012
  RPS, uniform vs uniform (2,000 eps)        0.0000     +0.0025     0.0025
  RPS, constant rock vs uniform              0.0000     +0.0210     0.0210
  Kuhn poker, NE pair, 12,000 hands         -0.05556    -0.0535     0.0021

  The Nim results are exact, not approximate: the XOR theorem predicts a
  deterministic outcome and the harness reproduces it in every episode.

BEHAVIOURAL SANITY (not ground truth, but falsifiable)

  Pig, hold-at-25 vs hold-at-1 .............. +0.965  (25 dominates, as
                                              the STOP literature predicts)
  Pig, hold-at-25 mirror match .............. +0.015  (near-even; first-
                                              mover edge only)

DETERMINISM: all five worlds produce byte-identical replay digests across runs
from the same seed.

OBSERVATION HYGIENE: Kuhn poker observation(0) exposes keys
[bets, cards_dealt, done, my_card, pot, to_move] and no opponent card.

--------------------------------------------------------------------------------
7. DELIVERABLE AND READINESS LADDER
--------------------------------------------------------------------------------
Position of each world on the mandate's section 11 ladder. The levels are NOT
collapsed: a running simulator is not a verified game, and a verified game is
not a benchmark.

  World         W0  W1  W2  W3  W4  W5  W6  W7  W8
  -----------   --  --  --  --  --  --  --  --  --
  TIC_TAC_TOE    y   y   y   n   y   y   y   y   n
  NIM            y   y   y   n   y   y   y   y   n
  PIG            y   y   y   n   y   y   y   y   n
  RPS            y   y   y   n   y   y   y   y   n
  KUHN_POKER     y   y   y   n   y   y   y   y   n

  W3 RULE-AUDITED is 'n' for all five. No rulebook has been consulted. This
  is the same untouched gate as the Atlas phase and the bench before it.
  W8 EXPERIMENT-READY is 'n' by choice: frozen evaluation sets and a
  registered protocol do not exist, and creating them without an experiment
  to serve would be premature.

ACCEPTANCE CRITERIA
  One interface hosts all five worlds without escape hatches ........ yes
  Chance is explicit and reproducible .............................. yes
  Simultaneous action is a first-class case ........................ yes
  Private observation is enforced, not merely intended ............. yes
  Every episode is deterministic from its seed ..................... yes
  Every step is instrumented for replay ............................ yes
  Invariants checked continuously, not once ........................ yes
  Ground truth reproduced for every world .......................... yes
  Environment cannot consult a player .............................. yes
  Any ruleset audited against a rulebook ........................... NO
  Any world admitted to a scored experiment ........................ NO

--------------------------------------------------------------------------------
8. CONTROLS AND WHAT RULES OUT CHEAPER EXPLANATIONS
--------------------------------------------------------------------------------
  RANDOM PLAYER          the floor. Present for every world. A result against
                         random means almost nothing, and the mandate is
                         explicit about that; it is here so the distribution
                         is known rather than assumed.

  FIRST-ACTION PLAYER    a null control BENEATH random -- it reads nothing at
                         all, not even the legal list beyond its first entry.
                         Used to confirm that RPS's equilibrium is genuinely
                         unexploitable by a constant strategy.

  GROUND-TRUTH ORACLES   NimOptimalPlayer and MinimaxPlayer exist to test the
                         HARNESS, not to compete. If Bouton's theorem holds
                         and the harness is faithful, NimOptimalPlayer cannot
                         lose from a won position; it does not, in 400/400.

  A DOCUMENTED CONTRACT VIOLATION, declared rather than hidden:
  MinimaxPlayer requires the STATE, not an observation, because it must clone
  and search forward. It is therefore strictly better informed than the
  interface permits and is NOT a valid comparator against observation-limited
  agents. This is recorded in the code and here, because a convenient oracle
  quietly becoming a baseline is exactly how a benchmark rots.

--------------------------------------------------------------------------------
9. DEFECTS AND ARCHITECTURAL FINDINGS
--------------------------------------------------------------------------------
F1  THE PROPOSED INTERFACE BROKE ON THREE OF FIVE WORLDS.        STRUCTURAL
    The mandate's candidate form was ApplyAction(player_id, action).
      Pig    the die roll is nobody's action
      RPS    there is no turn order to hold an id
      Kuhn   what a player may observe is not the public state
    RESOLUTION: current_player() returns a player id, CHANCE, or
    SIMULTANEOUS, and the caller dispatches. After the change no world
    required a special case.
    NOTE: this is the same resolution OpenSpiel reached. Converging on it
    independently is mild corroboration, and it makes the section 5
    cross-validation adapter a translation rather than a rewrite. It is NOT
    evidence that the design is right -- two designs agreeing is weaker than
    either being tested.

D1  DETERMINISM FAILED ON ALL FIVE WORLDS.                       FIXED
    First verification run: 5/5 determinism checks failed. Investigation
    showed the simulation was in fact bit-identical -- actions, state
    hashes and returns all matched across runs -- and only wall-clock
    elapsed_ms differed, because timing sat inside the compared payload.
    ROOT CAUSE: instrumentation was placed inside replay IDENTITY.
    FIX: Replay now separates to_json() (full record with timing, for
    section 18 observability) from digest() (identity, timing excluded).
    GENERAL LESSON: anything legitimately non-deterministic -- timing, host,
    pid -- must be recorded but kept out of the thing that answers "is this
    the same episode?".

F2  MINIMAX CANNOT HONOUR THE PLAYER CONTRACT.                   ACCEPTED
    Forward search needs the state, not an observation. Rather than widen
    the observation to satisfy it -- which would have leaked information to
    every player in every world -- the oracle is marked as contract-violating
    and excluded from comparator use. The interface was NOT bent to
    accommodate a convenience.

F3  PIG EPISODES ARE LONG UNDER RANDOM PLAY.                     NOT A DEFECT
    185.8 steps per episode versus 138 under hold-at-25. Random play rolls
    until it busts, so turns are long and scores accumulate slowly. Recorded
    because it looked like a non-termination risk and is not one.

E1  A FIGURE WAS MISREPORTED IN THE COMMIT MESSAGE.              CORRECTED
    Commit dabede3ad states "16/16 groups pass". The correct count is 20
    checks. The error was in the summary, not the run; the saved verification
    output has always shown all 20. Corrected here and noted in section 0.

--------------------------------------------------------------------------------
10. KNOWN LIMITATIONS AND CAVEATS
--------------------------------------------------------------------------------
  1. NO RULE IS AUDITED. W3 is unmet for all five worlds. Provenance is
     COMMUNITY_CONSENSUS or EXPERT_INTERPRETATION; zero OFFICIAL_RULE.
  2. FIVE WORLDS IS A SLICE, NOT A LIBRARY. The gold set (section 16, 20-50
     worlds) does not exist. Nothing here has negotiation, real-time play,
     more than two players, asymmetric roles, cooperation, long horizons,
     spatial topology, or resource economies. The interface has not met
     those, and F1 is a warning that it will bend again when it does.
  3. THE HARDEST CASES ARE ABSENT BY CONSTRUCTION. Diplomacy-style
     negotiation as first-class action, real-time clocks, and vector or
     non-scalar rewards are exactly the cases the mandate predicts will
     break the API, and none is in this slice.
  4. GROUND TRUTH IS NOT RULE CORRECTNESS. Reproducing Kuhn's -1/18 shows
     the implementation matches KUHN'S game. If the encoding diverged from
     the published rules in a way that preserved the value, this would not
     catch it.
  5. STATISTICAL CHECKS ARE TOLERANCE-BASED. The Kuhn check accepts within
     0.02 of -1/18; observed 0.0021. RPS accepts within 0.08. These
     tolerances are chosen, not derived, and a subtle bias smaller than the
     tolerance would pass.
  6. NO CROSS-VALIDATION AGAINST AN EXTERNAL ENGINE. The arena, like the
     Atlas before it, currently grades itself. Ground truth from literature
     is stronger than self-consistency but weaker than an independent
     implementation.
  7. NO PERFORMANCE BASELINE ABOVE HEURISTIC. Section 17 asks for stronger
     reference players where practical. None exists here.
  8. TWO PLAYERS ONLY. num_players is parameterised but every world in the
     slice is 2-player. n>2 turn management is untested.
  9. THE ATLAS AND THE ARENA ARE NOT YET JOINED. Each world declares an
     atlas-style vector by hand; nothing reconciles it against the
     catalogued row for the same game, and disagreement would currently be
     silent.

--------------------------------------------------------------------------------
11. REPRODUCTION
--------------------------------------------------------------------------------
  cd F:\Prometheus\ludus\arena
  python verify.py 400          # the full run; ~20 s, prints 20 checks

FIVE-MINUTE SPOT CHECKS FOR A REVIEWER

  1. Nim ground truth is exact, not fitted. Change the heaps and the
     prediction must follow the XOR rule:
       python -c "import worlds as W, players as P, core;
       w=W.Nim(heaps=(1,2,3));
       print(core.run_episode(w,[P.NimOptimalPlayer(),P.NimOptimalPlayer()],
       seed=1).returns)"
     XOR(1,2,3)==0, so the player to move must LOSE: expect [-1.0, 1.0].

  2. The environment cannot consult a player. grep the world code:
       grep -n "Player\|best_move\|evaluate" worlds.py
     Expect no hits. A World must not import or call a Player.

  3. Private observation is real, not intended. In Kuhn poker,
     observation(0) must lack the opponent's card while the state has it.
     Check 7 in verify.py asserts this; read the printed key list.

  4. Determinism excludes timing but nothing else. Run verify.py twice and
     confirm the printed digests in section [2] are identical across runs.

  5. Invariants are checked continuously. Break one deliberately -- e.g.
     return a bad probability from PigState.chance_outcomes -- and confirm
     the run reports violations rather than passing quietly.

--------------------------------------------------------------------------------
12. FUTURE DIRECTIONS
--------------------------------------------------------------------------------
RANKED BY INFORMATION PER UNIT EFFORT

  1. CROSS-VALIDATE AGAINST OPENSPIEL. The single highest-value next step,
     and the only one that stops the arena grading itself. All five worlds
     have OpenSpiel counterparts (tic_tac_toe, nim, pig, matrix_rps,
     kuhn_poker). Compare per-state: legal action sets, chance outcome
     distributions, terminal detection, and returns. Disagreement produces
     review candidates and neither side is assumed correct.
     This is mandate section 5, and F1 has already made the adapter cheap.

  2. BREAK THE INTERFACE ON PURPOSE, WITH THE HARD CASES. The value of this
     slice was F1. Repeat it deliberately with the worlds most likely to
     bend the design further:
       negotiation      Diplomacy-like; messages as first-class actions
       real-time        clocks, AdvanceClock, action duration
       n > 2            turn management, coalitions, kingmaking
       cooperative      shared reward, no zero-sum assumption
       vector reward    outcomes that do not reduce to a scalar
     Each is a predicted failure. Finding out which predictions are wrong is
     the point, given that three of my last four predictions in this project
     were wrong.

  3. JOIN THE ARENA TO THE ATLAS. Each arena world hand-declares a structural
     vector. Reconcile it against the catalogued row for the same game and
     report disagreement. This is a free, standing cross-check between two
     independently produced descriptions -- the same trick that made
     coherence.py productive in the Atlas phase.

  4. PARAMETER SWEEPS AS COUNTERFACTUAL NEIGHBOURS. World params already
     support this. Pig with bust_face varied, target varied, sides varied,
     produces a one-axis family. That is the substrate section 7 asks for and
     it costs nothing beyond running it.

  5. A HOLD-AT-N SWEEP IN PIG AS A BENCH-FACING PROBE. Pig is r0003's shape.
     Sweeping N and measuring the optimal threshold against the exact DP
     value would be the first executable contact between the arena and the
     bench's blocked circuit. Note this is a MEASUREMENT, not a transfer
     claim, and it should not be run as a scored experiment without
     authorisation.

  6. GOLD SET SELECTION. 20-50 worlds, justified structurally. Should follow
     items 1 and 2, not precede them: selecting 50 worlds against an
     interface known to be incomplete would bake in the incompleteness.

EXPLICITLY DEFERRED
  - Stronger reference engines (section 17). Premature before item 1.
  - Strategy-knowledge ingestion (section 10). Premature before a gold set.
  - Transfer-panel logic (section 13). Dormant by instruction.

--------------------------------------------------------------------------------
13. VERDICT
--------------------------------------------------------------------------------
  ONE INTERFACE HOSTS 5 HETEROGENEOUS WORLDS ........ YES (after redesign)
  GROUND TRUTH REPRODUCED FOR EVERY WORLD ........... YES (5/5)
  EPISODES DETERMINISTIC AND REPLAYABLE ............. YES (after D1 fix)
  PRIVATE INFORMATION ENFORCED ...................... YES (tested)
  ENVIRONMENT FREE OF STRATEGY ORACLES .............. YES (structural)
  VALIDATED AGAINST AN INDEPENDENT IMPLEMENTATION ... no
  ANY RULESET AUDITED ............................... no
  GOLD SET EXISTS ................................... no
  READY FOR A SCORED EXPERIMENT ..................... no, by choice

  STATUS: WORKING SUBSTRATE, NARROW AND UNVALIDATED.

  The slice did its job. It was built to locate the interface's failure
  point and it found one on three of five worlds within the first hour,
  plus a reproducibility defect that a less instrumented harness would have
  shipped silently. What it has not done is meet a game hard enough to bend
  the design a second time, and the mandate is explicit that those games --
  negotiation, real-time, n-player, non-scalar reward -- are where the
  expensive surprises live.

REVIEWER'S BOTTOM LINE
  The interface survived five games chosen BY ME to break it, which is the
  weakest possible version of that test -- so which world would you pick to
  break it that I would not have thought to choose, and is OpenSpiel
  agreement worth anything as validation given that this design already
  converged on OpenSpiel's shape?
================================================================================
END OF PACKET
================================================================================
