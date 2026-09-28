REPORT -- can selection value enabling (tool-building) actions?

1. WHAT I SET OUT TO TEST

Whether a selection rule that scores candidate actions by their immediate
payoff (a discrimination count / expected hypotheses eliminated, or fitness
in an evolutionary search) can ever choose a "constructive" step that pays
nothing now but unlocks much stronger later steps; what it takes to make it
do so (lookahead, a random-sample floor, a human forecast); whether a
directed sampler can do worse than a uniform one; and whether a ~20% uniform
floor actually turns this blind spot into something measurable. I also
checked whether the program's own selectors show the problem in committed
data.

2. WHAT I DID

(a) Controlled simulation (new code, scratch only):
    <scratch>/sim/enabling.py, driver2.py, extra.py
    World: 64 hypotheses, one true, noise-free, budget 16 steps.
    Direct assays: singleton tests "is h = j" (expected elimination ~2),
    D in {8, 24, 64} of them, always available. Enabling chain T1..Tk
    (k in 0,1,2,3,5,8), zero immediate gain, must be done in order; once
    complete, 6 bit-test "power" assays (expected elimination = half the
    live set) become available. Selectors: greedy discrimination count
    (ties random); greedy with 20% and 50% uniform floor; uniform over
    useful actions; open-loop h-step planner (h=2..10; forecasts the
    current-state gains of a best action sequence, i.e. what a filer who
    knows "this unlocks X" would predict); the same planner discounted
    (gamma 0.9, h=6/10/14). 400 trials per cell, paired worlds/truths
    across arms. For the floor-measurement question: 2000 greedy+20%-floor
    episodes (D=24, k=1 and 2) with per-step logs.
    Commands: python3 sim/driver2.py > sim/out2.jsonl (stopped at the
    580 s cap after 139 of 162 cells; the missing cells are D=64, k>=3
    duplicates of the D=24 pattern); python3 sim/extra.py > sim/out_extra.jsonl.
    An earlier design (16 hypotheses, weak direct assays good enough to
    finish without the tool) was aborted as uninformative; its partial log
    was not kept (sim/driver.py is its driver).
(b) Re-read of committed evolutionary evidence (no re-run):
    crius/runs/C2_SUMMARY.md and crius/CRIUS_C2_TERMINAL_REVIEW.md
    @ origin/main 6ff2b2f8a (PARTS ladder, 36 searches of 7208 candidates).
(c) Audit of the program's decision-market / backlog selector:
    aporia/docs/perpetual_engine_design_2026-08-17.md (rule: "execute the
    highest-discrimination affordable move"), engine/queues/MOVES.jsonl,
    engine/queues/BACKLOG.jsonl, engine/driver/backlog_gen.py
    @ origin/main 6ff2b2f8a; git log for the fate of the one
    tool-building move.

3. RESULT

(a) Simulation (success = true hypothesis identified within 16 steps;
    tools = fraction of episodes in which the chain was completed).

    Control, no enabling chain (k=0): greedy 1.00 success, 6.0 steps;
    20% floor 6.2-6.7 steps; uniform 7.7 / 10.5 / 13.8 steps and success
    1.00 / 0.97 / 0.49 at D = 8 / 24 / 64. Directed wins when nothing needs
    building.

    Enabling chain, plentiful cheap assays (D=24; D=64 same pattern):
      k=1: greedy 0.25 success, tools 0.00 | floor20 0.32, tools 0.20 |
           floor50 0.38 | uniform 0.43, tools 0.61 | planner h>=2 1.00 (7 steps)
      k=2: greedy 0.25, tools 0.00 | floor20 0.24, tools 0.02 |
           uniform 0.26 | planner h>=4 1.00 (8 steps), h=2 0.25
      k=3: greedy/floor/uniform 0.22-0.25, tools <=0.07 | planner h>=4 1.00
      k=5: all myopic arms 0.22-0.25, tools 0.00 | planner h=6 1.00 (11 steps)
      k=8: nothing succeeds (chain + payoff exceeds budget).
    Scarce cheap assays (D=8): greedy exhausts them, then builds the tool
    because nothing else is left (tools 0.86) -- fine at k<=2, too late at
    k=3 (0.52 vs uniform 0.75) and k=5 (0.15).

    Findings:
    - A myopic discrimination-count selector never takes a zero-gain
      enabling step while any positive-gain alternative exists (tools
      exactly 0.000 across all D>=24 cells). It builds tools only after
      exhausting everything else.
    - A 20% uniform floor rescues a depth-1 chain only partly (0.25->0.32)
      and nothing at depth >=2 (it must hit T1..Tk in order by chance; each
      random hit is then abandoned by the greedy arm). At k=0 it costs
      4-11% more steps.
    - Uniform beats greedy exactly when enabling structure exists and cheap
      alternatives run out (D=8, k=1..3); greedy beats uniform otherwise.
      "Directed can underperform uniform" is real but conditional.
    - A lookahead planner values the enabling step as soon as its horizon
      covers the chain plus one payoff step (h >= k+1): 1.00 success at the
      minimum possible step count in every such cell. So the premise that
      "algorithms cannot intrinsically value constructive actions" is false;
      one-step (myopic) scoring cannot, finite lookahead can.
    - New pathology: the UNDISCOUNTED planner with a horizon longer than
      needed procrastinates. Its forecast is order-invariant, so "do a
      cheap assay now, build the tool later" ties with "build now"; with
      random tie-breaking it degrades to exactly the uniform arm (D=24 k=1
      h=8/10: tools 0.61, success 0.52 -- identical tools rate to uniform).
      Valuing an enabling step is not the same as doing it now. A 0.9
      discount removed this in all 27 cells tested (success 1.00 at the
      minimum step count for h = 6/10/14, k = 1/3/5, D = 8/24/64).

    What a 20% random floor measures (D=24, 2000 episodes):
    - Per-action immediate gain is identical in both arms (direct 1.961
      random vs 1.963 greedy) and the enabling step reads 0.000 in both.
      The random/heuristic landing-rate ratio -- the quantity the floor
      proposal treats as the bias correction -- is ~1 and says nothing
      about the enabling action. The blind spot is NOT converted into a
      measurable by per-cell landing rates.
    - It becomes measurable only with delayed credit: sum of gain over the
      next 6 steps after a randomized draw is 44.1 when the draw was the
      tool vs 11.3 when it was a direct assay (k=1, n=384 vs 4827). At k=2
      the same contrast collapses to 10.8 vs 9.9: one random T1 is not
      followed by T2 because the greedy arm never picks it, so the floor's
      signal about a chain decays with chain depth.

(b) Program's evolutionary evidence (reproduction of known result, same
    shape): Crius PARTS ladder -- recorder alone dFit -0.001 (0/10
    streams), invoker alone -0.002 (0/10), recorder+invoker +1.138 (7/10);
    planner alone -0.057 (0/10), full chain +15.97 (10/10). The enabling
    parts carry zero-to-slightly-negative fitness, and 36 mutation-selection
    searches (129,744 candidates at rungs C/D alone) produced 0
    reproducible reuse candidates. Caveat: there the parts are also 7-47
    instruction edits from the seed, so the failure is accessibility
    (edit distance) as much as myopic valuation; a neutral part would not
    be found either.

(c) Program's decision-market selector: the written rule executes the
    highest discrimination count; the one tool-building move on the board
    (M-006, "build the R4 probe generator ... feeds every downstream
    measurement") has discriminates_against = [] and so scores zero under
    the rule. It was nevertheless built (commit 1206d504f, 2026-08-18) by
    hand dispatch, outside the rule; MOVES.jsonl still lists it QUEUED.
    In the backlog generator, priority is a fixed per-source score with no
    credit for what a thread unlocks: at the last committed regeneration
    (e6efb2958, 2026-08-21) 0 threads were runnable, 644 parked, and 493 of
    those were gated on a single enabling lane (spec authoring) whose only
    instance was a hand-filed thread. Enabling work in this program has in
    practice been chosen by people, not by the selector -- consistent with
    the external report's recommendation, but not because algorithms
    cannot do it.

4. DID IT RESOLVE THE QUESTION

Partly. In a controlled toy the answer is clean: one-step selection cannot
reward an enabling step, a uniform floor barely helps beyond depth 1, and
bounded lookahead with a discount solves it completely at modest horizon
(h = chain length + 1). What is not resolved: how long real enabling chains
are in the program's lanes and whether seat/engine forecasts of "what this
unlocks" are accurate enough to use as the lookahead (the calibration
tracking that would answer this has no realized_gain entries yet: all six
moves have realized_gain null or a non-numeric verdict). The toy is
noise-free and has a single known tool; real payoffs are uncertain.

5. CONSEQUENCES

- False premise (for whoever relies on the external research report's
  line "algorithms cannot intrinsically value constructive actions"): it
  is true of myopic scoring only. A selector with explicit unlock
  forecasts (each move/thread declares what it enables) plus a finite,
  discounted horizon values enabling steps. Engine/decision-market owners
  (Aporia) should know.
- Instrument/harness gap: the decision-market rule as written scores
  enabling moves at zero, and the backlog priority gives no unlock credit;
  a candidate fix is to score a move by discrimination of the best
  sequence it enables within h steps, discounted, and to let a gate-lifting
  thread inherit (discounted) priority from the threads it unblocks. The
  MOVES record for the R4 generator is stale (built, still QUEUED).
- Correction to the random-floor idea (Harmonia provocation, and any
  sampler owner adopting "keep a uniform arm", e.g. NPE/BEE samplers): keep
  the uniform arm -- it is the only thing that ever tries a zero-scored
  action, and uniform does beat directed when enabling structure exists --
  but its per-cell landing-rate ratio does not measure enabling value. It
  must be paired with delayed, state-conditioned credit (outcome over the
  next several steps after a randomized choice), and even then it only
  resolves shallow chains.
- New positive (small) result: undiscounted lookahead procrastinates on
  enabling steps via order-invariant ties; discounting fixes it. Relevant
  to anyone building a planner over moves.
- Reproduction of something known: Crius already measured the
  evolutionary version (fitness valley one link deep, cliff at the
  planner). Crius's framing "accessibility frontier" is the right one;
  nothing here changes it.

6. COST

About 1.5 hours of my time. CPU: about 25 CPU-minutes in total (an
aborted first design ~10 min, main sweep ~8 min, extra runs ~4.5 min),
single process, well under 2 GB. Not done: the remaining 23 sweep cells
(D=64, k>=3), noisy assays or uncertain unlock payoffs, any re-run of
program code (not needed; Crius numbers were read from committed
summaries), and any check of whether NPE/BEE samplers actually keep a
uniform arm today.
