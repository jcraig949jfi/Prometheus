+============================================================================+
| RESEARCH SCIENCE OBSERVATORY -- STATUS FOR EXTERNAL REVIEW                 |
| Four engines qualified; one evidence gap open; where should it go next?    |
| Author: Palamedes (Lead RSO Engineer, Builder Cell coordinator),           |
|         harry1/M4, claude-opus-5-5, instance harry1-679179c6               |
| Date:   2026-10-15                                                         |
| For:    the operator (HITL); external reviewers                            |
| Status: NO ACTIVE CAMPAIGN. C-018 (Generation 4) CLOSED 2026-10-12.        |
|         Self-contained: no repository access needed.                       |
+============================================================================+

0. SUMMARY
----------
The Observatory is a small engineering cell that takes another team's
artificial-life or computational engine and, without changing it, asks one
narrow causal question of it. Each answer goes through a fixed procedure:
  1. Select: a gate that may narrow or reject the question.
  2. Build: an adapter and a frozen, preregistered assay.
  3. Challenge: an independent adversarial review by a different model
     (called "Q3").
  4. Repair: ONE repair round.
  5. Confirm: one confirmatory run.
  6. Integrate: an integrator check.
  7. Preserve: reusable parts go to a registry.

Four engines have been through it:
  - Gen 1, Ares: does a subject retain a bit?
  - Gen 2, Ensorain: does it revise at a law switch?
  - Gen 3, Z80: who wrote the bytes?
  - Gen 4, Aether: is spatial causal ancestry separate from recoverable
    content?

All four produced bounded, honest results. The cell has been idle since
2026-10-12 awaiting two operator decisions:
  (1) whether to run a cheap post-confirmation audit that closes a known
      evidence gap in the Gen-4 result;
  (2) what Generation 5 should be, if anything.
This packet states where things stand and asks the reviewer where to go.

Headline judgment, ours and the operator's: the Observatory has become a
credible instrument for DISTINGUISHING mechanisms. None of the four
campaigns has shown an organism DISCOVERING a new reusable mechanism.
The growth so far is in the instrument, not in the organisms. The next
choice decides whether that changes.

1. WHAT EXISTS NOW (reusable, committed)
-----------------------------------------
- Registry of qualified components: 15 entries, each with a scope it is
  qualified for and a NOT-FOR note, pinned by LF-normalised sha256.
  Examples: an execution binding, an evidence custody keeper, a mutation
  runner, canonical receipts, stratified Holm analysis, a Z80 attribution
  instrument, an Aether ancestry/content instrument.
- Experiment-completeness contract (Gen 4): a sealed manifest of shards,
  seeds and arm counts, checked BEFORE any verdict.
  - Missing, duplicated, substituted or altered shards are refused.
  - It would have caught a real Gen-3 defect: the frozen analyser printed
    a qualified verdict on 5 of 6 shards.
  - 40 tests; 12 of 13 mutants killed (1 equivalent).
- Control-falsifiability requirement (Gen 4): every claim-critical control
  in a preregistration must show that it CAN fail, that it reads no
  answer-bearing field, and that a registered near-miss is rejected.
  - Executable checks exist, each tested on a miniature of a real past
    defect from Gens 1-3.
  - 14 tests.
- An operational pattern for headless agent seats:
  - the model identity is verified across the WHOLE session log, not just
    at boot (a mid-session refusal fallback once swapped the reviewer
    model);
  - long jobs run as detached OS processes that own their own state;
  - every integration includes one integrator mutation and one
    independent reproduction.

2. GENERATION 4 RESULT (Aether), IN ONE PARAGRAPH
-------------------------------------------------
Recoil + exchange law (RX), 128^2, CPU, Aether's own physics, attribution
and decoder consumed unchanged.
  Verdict: CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE_CONTENT.
  - Of 48 native units, 13 were evaluable.
  - 8 were CONFIRMED: clamping the claimed ancestor removes its
    descendants, while clamping a matched, diverging non-ancestor does
    not. They reach radius 2 to 6.
  - Over the same radius band, Aether's held-out decoder recovers
    essentially no planted content:
      excess over chance           0.0135
      on the confirmed units' seeds 0.0099
      margin                       0.05
  - Excesses below ~0.05-0.10 are NOT excluded.
Comparison law aeth01.v1: 0 of 16 units evaluable, i.e. "not evaluated",
  NOT a negative.
Transformation of several inputs (P4): unsupported natively; recorded,
  not constructed.
Q3 provenance: the challenge (2.8 h) and the re-check were both Fable 5.1
  for every message (verified from logs).
What the challenge found BEFORE any data existed: the first analyser
  would have printed
  - a positive verdict on a re-sealed 5-shard design;
  - inflated content (0.112 vs a genuine 0.012) from duplicated units;
  - classes flipped by edited tree fields.
  All were fixed in the one repair round.

3. WHAT HAS HAPPENED SINCE (2026-10-12 .. 10-15)
------------------------------------------------
No new experiment, no new code. The operator reviewed the Gen-4 packet
and agreed with the result as scoped. They raised one substantive concern,
which we verified:

  THE CLAMP-REPLAY GAP.
  - Only 6 of 64 confirmatory units were fully re-executed, as the
    preregistered sample.
  - The other 58 rest on producer-written clamp arrays. Those arrays are
    bound by snapshot hashes, a replayed attribution tree and invariants,
    but they were not themselves independently re-executed.
  - The challenger demonstrated that this matters: an invariant-respecting
    rewrite of one clamp array flipped a unit's class
    (NONSPECIFIC -> CONFIRMED) with every check passing.

  Correction to the operator's count:
  - Of the 8 CONFIRMED units, TWO have been independently re-executed,
    not one:
      8228  in the preregistered sample;
      8201  re-executed by the integrator; bit-identical arrays
            (sha 567d483e).
  - The RESULT text still says "only 8228". It needs a one-line
    correction, which has NOT been made yet.

  Size of the open gap:
  - 6 of 8 CONFIRMED units, and all 5 NOT_INTERVENTIONAL units, are
    unreplayed.
  - So are the units whose class depends on their arrays:
    CONTROL_VACUOUS 8 and INSUFFICIENT 3.
  - Closing it: replay all 57 remaining units, about 65 s each, about
    1 core-hour, local CPU. It is read-only on the Aether lane.
  - It must be recorded as a NEW post-confirmation audit. It must not
    alter C-018's registered rule or verdict, whichever way it comes out.

4. THE COST TREND (four generations, no difficulty normalisation)
-----------------------------------------------------------------
                 Gen1 Ares  Gen2 Ensorain  Gen3 Z80    Gen4 Aether
  adapter lines  ~1,800     662            707         881
  shared code    n/a        0 modified     0 modified  0 modified
  open->result   6.2 h      4.0 h          7.1 h       10.3 h
  Q3 time        ~1.7 h     ~1.6 h         ~2.0 h      ~2.8 h
  real defects   2          2              1+3         6
    found by Q3
  repair rounds  1          1              1           1
  waiting share  69%        49%            24%         21%
  cash           $0         $0             $0          $0

Reading:
  - BUILDING got cheaper and has flattened.
  - PROVING did not get cheaper. Reviewer time rose with the richness of
    the evidence chain.
  - Every challenge found real defects in rules the builder believed
    sound.
  - The selection gate re-scoped the operator's question in all three
    new engines:
      retention    -> revision
      heredity     -> attribution
      P4 dropped; P1 used only as a guard
  - Coordination waiting fell from 69% to 21%.

5. OPEN STATE (verified 2026-10-15)
-----------------------------------
  - Active campaign: none. The seat is idle. A light hourly check of
    comms and the integration queue is running.
  - Pending operator decisions:
    (a) Aether clamp-replay audit: proposed, not started.
    (b) Generation 5: not opened. A candidate contract exists (below).
    (c) External reviews of the C-013 packets (Astra, Fable): still not
        performed.
  - Known text fix: RESULT.md "1 of 8 replayed" should read "2 of 8".
  - Constraints that still bind:
      local resources only; no paid cloud;
      engine lanes read-only; no new physics laws;
      no silent model upgrade;
      one repair round per campaign;
      no campaign without bounded authority.

6. GENERATION 5 OPTIONS
-----------------------
A candidate contract was written by a survey seat (Sonnet, read-only,
one 5.5 s smoke run). Two candidates:

  CRIUS (primary in the contract)
  Question: does a stored, callable procedure CAUSALLY account for later
  capability, as opposed to compute, storage, memorisation, or the
  world's own help?
  - Native interventions already exist in the engine:
      accumulated vs fresh lifetime;
      per-block ablation;
      transplant;
      code-only;
      compute-matched and storage-matched controls.
  - Smoke test: a hand-built reuse organism scores 49-50 of 50 tasks;
    the simpler controls score 26-32 (3 seeds).
  - Calibration only, NOT evidence.
  - Problems:
      (1) The world exposes which primitive an action performed, and the
          substrate silently calibrates action ids. The measured "reuse"
          gain may be the world's help, not reuse.
      (2) Native search has never found reuse: 0 of 36 runs.
      (3) The Crius seat is CLOSED, with no steward to answer interface
          questions.
  - Expected honest result: "constructed reuse is attributable; native
    discovery is not found or not qualified". Same shape as Gen 3.

  ANANKE (runner-up)
  Question: two-part composition (FLIP/XOR), where each part is worthless
  alone ("the composition wall"). Search scores FLIP 0/290 and XOR 0/83.
  - Strengths:
      best independent oracle of any candidate (an integer
      re-implementation with a conformance test);
      mirror-pair worlds in which every constant policy scores exactly
      0.5;
      exact state-transplant interventions.
  - Problems:
      only 4 of 200 FLIP cells admissible;
      a needle landscape (62% of single edits kill);
      the known answer is hand-built;
      the Ananke seat has its own planned next run on exactly this wall
      (block-duplication FLIP). An Observatory campaign risks duplicating
      or racing the owner.

  Our recommendation:
  - Before choosing, run a decisive, cheap selection gate on EACH:
      Crius:  remove the world's primitive labels and the calibration;
              does the reuse advantage survive?
      Ananke: is the owner already running this question? If yes, join
              or defer; do not duplicate.
  - If both survive, we lean Ananke: reachability is nearer the North
    Star than another attribution instrument.
  - Separately, turn the challenger's recurring attacks into a
    deterministic kit in the registry, so that reviewer time is spent
    only on new attacks:
      drop a shard;
      duplicate units;
      invariant-respecting rewrite of a derived field;
      constant detector;
      scrub the answer field.

7. WHAT THIS STATUS DOES AND DOES NOT ESTABLISH
-----------------------------------------------
Does:
  - Four bounded, reproducible, independently challenged results on four
    different substrates, at $0 and a few core-hours each.
  - Two reusable qualification requirements (completeness and
    falsifiability) that close defect classes seen across engines.
Does NOT:
  - any claim of intelligence, circuits, computation or cognition in any
    engine;
  - spontaneous evolutionary discovery of a new reusable primitive. None
    of the four campaigns tested or found it;
  - full independent verification of every Gen-4 intervention (section 3);
  - evidence that qualification cost will ever fall. The trend says it
    has not.

8. DECISION REQUESTED (the operator's call)
--------------------------------------------
  D1  Run the Aether clamp-replay audit (~1 core-h, local)?
      Our lean: yes, first.
  D2  Generation 5:
        Crius, Ananke, both gated first (our lean), or neither.
  D3  Invest in a deterministic adversarial kit to cut reviewer cost,
      before or alongside Gen 5?
  D4  Commission the overdue C-013 external reviews, or retire them?

9. QUESTIONS FOR THE REVIEWER (written to resist agreement)
-----------------------------------------------------------
Q1  Is the Gen-4 ancestry result qualified, or only qualified under a
    trust boundary that accepted producer-written intervention outcomes?
    Is replaying the 57 remaining units the minimum fix? Is a fresh
    confirmatory seed block needed because the repair round chose its
    rule after seeing challenge data?
Q2  Four engines have produced four instruments: retention, revision,
    attribution and ancestry. Is the Observatory advancing toward
    measuring cumulative cognitive development, or accumulating
    forensics? What is the SHORTEST experiment from here that could show
    a preserved discovery making a later discovery more reachable?
Q3  The selection gate narrowed the question in every new engine. Are we
    learning about the engines, or mainly about what our instruments can
    ask? Would a reviewer trust a gate that has never said "no, choose
    another engine"?
Q4  Qualification cost is flat to rising (reviewer time 1.7 -> 2.8 h).
    Is that the correct price of richer evidence, or a sign the registry
    is not capturing what reviewers actually check? Would a deterministic
    attack kit replace reviewer judgment, or merely hide its absence?
Q5  Crius's measured "reuse" gain may come from the world leaking
    primitive labels. If the leak explains it, is there ANY native
    Crius result worth qualifying, or should Gen 5 go straight to the
    composition wall (Ananke), even at the risk of racing its owner?
Q6  Should Generation 5 be another engine at all? The alternative is to
    stop onboarding engines and turn the existing instrument set on ONE
    engine's open-ended runs over time.
Q7  What result in the next campaign would convince you the Observatory
    is measuring the wrong thing, and should stop?

10. ARTIFACTS (repository paths; for those with access)
-------------------------------------------------------
  Gen-4 review packet  rso/scale/review/GEN4_REVIEW_PACKET.md
  C-018 closeout       ops/campaigns/C-018/CLOSEOUT.md
                       (closeout commit 85e0cd7fb)
  Aether               rso/aether/RESULT.md, PREREGISTRATION.md (v1.1.0),
                       challenge/REPORT.md, challenge/R2/REPORT.md
  Integrator replay    ops/campaigns/C-018/tasks/C-018-T050/TASK.json
    of unit 8201       (history note)
  Shared requirements  rso/completeness/
                       rso/qualify/FALSIFIABILITY.md
  Registry             rso/registry/ (15 entries)
  Gen-5 contract       rso/gen5/CANDIDATE_CONTRACT.md
                       smoke: rso/gen5/smoke_crius_result.json
  Earlier generations  rso/witness/RESULT.md, rso/ensorain/RESULT.md,
                       rso/z80/RESULT.md

+============================================================================+
| "Not worth continuing", "stop onboarding engines" and "the Observatory     |
| is measuring the wrong thing" remain first-class answers.                  |
+============================================================================+
