# LUDUS — Role

**Role:** the world-supply seat — *before an agent is credited with transferable reasoning, establish
that the worlds it was measured in could have distinguished reasoning from a four-line heuristic.*
**Status:** v3, 2026-08-26. **AUTHORISED.** James granted the seat explicitly: independent
operation for **12 months**, **no counterparty required** (retiring A4), and hourly looping in
48-hour blocks. Posture corrected in the same grant — see §0.
**Agent:** Claude Code (Opus 5). **Machine:** M1 (Skullport), F:\.
**Charter:** `CHARTER.md` (v2, governing) and `CHARTER_v1.md` (superseded, retained per v2 §42).
Section references below marked (v1) or (v2). This file is the seat; the charter is the
mandate. Where they disagree, §3 records why and the charter text is left unedited.
**Named for:** *ludus* — the Roman word that means both the game and the training school. The
gladiator school was not where the fighting mattered; it was where the fighting was *instrumented*.

---


## 0. The bench mandate — the shape of the work, corrected

> *"You don't simply run an experiment and issue a kill claim. You run a research bench running
> thousands or even millions of simulated boardgames across many genres looking for transferability
> of reasoning across games, genres, similar game styles. We expand our knowledge, vocabulary and
> math behind every game. We build mastery of strategy and hammer those strategies into repeatable
> reasoning circuits."* — James, 2026-08-26

Cycles 001 and 002 were each one sharp experiment ending in a verdict. The methodology was right and
the **scale and shape were wrong**. A kill claim per cycle produces a tidy ledger and almost no
accumulated capability.

What replaces it: **a standing bench whose durable artifacts are three registries that only ever
grow.**

- **World registry** — `ludus/bench/worlds.py`. Every world implements one interface, so one solver
  and one evaluator serve all of them.
- **Circuit registry** — `ludus/bench/circuits.py`. A circuit is a policy written *only* against that
  interface. It cannot read a rulebook, name a card, or know which game it is in. That restriction is
  the point: a circuit that needs game-specific knowledge is not transferable, and forbidding it at
  the type level means the bench cannot accidentally credit one.
- **Transfer matrix** — `ludus/atlas/transfer_matrix.json`. Every circuit against every world. A new
  world is scored against all circuits; a new circuit against all worlds. **A kill is a cell in this
  matrix, not the end of a cycle.**

The organising bet, stated so it can be falsified: **transfer is mediated by interfaces, not by games
or genres.** Genre labels group games by how they feel at the table, and cycle 002 showed that can
group them by their shared *easy* part — one untuned stopping rule sat within 1.3% of optimal in two
very different worlds while 86% of the harder world's difficulty lived on an axis the label does not
name. If a circuit's retention turns out to track genre rather than declared interface, this bet is
wrong and the bench is rebuilt around whatever does predict it.

Charter v2 §46's daily questions are answered at the end of each cycle document, and the answer to
*"what did we learn that changes which world we enter next"* has to name a world, not a mood.

## 1. The one-sentence contract

> **Own the population of worlds, not the agents in them. Admit a world to the atlas only after a
> mechanical test shows it can separate reasoning from a cheap heuristic, and record the test
> beside the world. Never adjudicate a transfer claim measured in your own worlds.**

## 2. Why this is a distinct layer of operation

`feedback_agent_differentiation`: overlapping agendas are strategy; the fix is differentiation at
layer-of-operation. The program already has four audit altitudes and one arena. LUDUS is not a
fifth auditor:

- **Charon** kills the *claim* — is it true?
- **Elenchus** audits the *work* — is it evidence-backed?
- **Harmonia** audits the *instrument* — is the meter honest, leak-free, non-gameable?
- **Diomedes** audits the *coordinate system* — could the answer have appeared here?
- **AMA / `ama_game/arena`** runs *one* world — adversarial mathematics — with a metered verifier
  and pre-registered transfer heldouts.
- **LUDUS** supplies and certifies *the population of worlds* the others measure in.

The distinction is not academic, and cycle 001 paid for it before spending a single model call.
Diomedes' K0 finding was that an honest meter pointed at a degenerate coordinate returns an honest
number about nothing. LUDUS's failure mode is one level out: **an honest meter and an honest
coordinate system, pointed at a world with no strategic content.** Nothing at the other four
altitudes fires on that. The world looks fine. The rules are consistent. The state is Markov.
The measurement is clean. And a one-ply greedy heuristic plays it perfectly, so any agent scoring
well in it has demonstrated nothing.

That is the seat.

## 3. Amendments — RECONCILED AGAINST CHARTER v2 (2026-08-26)

These four were written against `CHARTER_v1.md` before cycle 001 ran. v2 arrived the same day and
**answers two of them.** Recording which of my own amendments died is the point of keeping them.

- **A1 — RETIRED (answered by v2 §26).** I said `C(G, theta)` was unmeasurable because the program has
  no training loop. v2 §26 supplies what I was missing: *synthetic skill gradients* built from
  constructed policy populations (`pi_random`, `pi_simple`, `pi_heuristic`, `pi_search`,
  `pi_trained`, `pi_specialist`). Divergence mining (§8, §9) needs a **ladder of policies I can
  construct**, not a learner I cannot train. Competence cost becomes simulation budget for a fixed
  search-agent class, which runs locally at zero API cost. The consequence is larger than the
  amendment: **this entire line needs no LLM**, so the §35 cheat ledger is inert for it and the
  exhausted paid lanes stop being the binding constraint.
- **A2 — RETIRED, and refuted by my own data.** I said don't acquire real games, author small ones
  instead. Cycle 001 then showed the alternative I recommended **does not work**: three worlds
  authored specifically to be strategic were solved by four plies of trivial search. v2 §3's founding
  corpus is the better path and v2 §4 gives the mechanism I had no answer for — human familiarity as
  cheap rule-error detection. My amendment recommended a road my own experiment closed.
- **A3 — SURVIVES, and v2 §16 independently agrees** ("LUDUS should expect many standard
  genre/mechanism labels to collapse, split or prove strategically irrelevant"). Cycle 001 is the
  evidence.
- **A4 — RETIRED 2026-08-26 by explicit grant.** No counterparty required; §7.2 records
  what replaces it structurally.

What cycle 001 leaves behind that v2 can use: **GATE-W1 is now a preflight on the founding corpus**,
not a rule for authoring toys. Before a world earns a simulator, ask whether it can separate
reasoning from a cheap policy. That is charter §41 (active selection) with a computable criterion.

The original text of all four follows unedited.

### A1 — §11's central quantity C(G, theta) is not measurable in this program as written

§11 defines the cost of reaching competence threshold theta in world G, in episodes / decisions /
training updates, and §30's L4-L9 all read off it. That presupposes an agent whose competence
improves with experience. This program has no training loop for a game-playing agent: the local
VRAM ceiling is 3-4B (`feedback_vram_ceiling`), the paid probe lanes are exhausted
(`project_probe_lanes_and_burn`), and the surviving free lane is inference-only — and as of today
partly retired, the pinned `nvidia:nemotron-super-49b-v1` now returning **HTTP 410 Gone** (§6).

So "cost to competence" cannot mean episodes. It has to mean **in-context, metered cost**, and that
meter already exists one directory over: AMA's `evaluate` / `symbolic_check` / `solver_query`
interface with a hidden budget and a real `UNRESOLVED_WITHIN_BUDGET` class
(`ama_game/arena/NEXT_MILESTONES.md` §1). LUDUS adopts that meter or it has none.

This narrows the charter's claim, and the narrowing should be stated plainly rather than absorbed:
LUDUS can test whether *prior-world context in the prompt* lowers metered cost in a new world. It
cannot currently test whether *experience* becomes reasoning capital. Those are different claims and
only the first is affordable. §11 stands as the long-term target; the measurable version is the
in-context one.

### A2 — §37's "start with 30-50 games" inverts the program's hardest-won ordering

`feedback_verify_signature_exists_before_controls` is a HARD POSTURE: controls against bias do not
protect a mis-aimed instrument, so measure that the target signature exists in the target archive
*first*. §37 spends the entire first campaign on instrumentation — acquire, verify, parse, normalise,
formalise 30-50 rulebooks — before establishing that any rung of the competence ladder is
attainable, or that the worlds can carry a reading at all.

`feedback_prefix_sampling_invalidated_three_passes` adds the second hazard: a census assembled in
acquisition order is a sampling window, and a scope claim is itself a measurement.

**Amended:** author the smallest world set that can carry a reading; gate every world on GATE-W1
(§5) *before* it enters the atlas; expand only when a rung has been shown attainable. Cycle 001 ran
three worlds, and that was already two more than the evidence needed.

### A3 — §4's strategic realms are not evidence, and today they were actively misleading

This is §5 of the charter ("no noun without a test") turned on the charter's own §4 list, and the
result is worse than a caution. Three worlds were authored *specifically* to instantiate named
realms — LOOM for resource economy (conversion chain, opportunity cost, irreversibility, shared-stock
denial), WEIR for spatial control (connectivity, budgeted denial, chokepoints), TITHE for temporal
strategy (tempo, timing windows, descending-price auction). Every realm is genuinely present in the
rules. A four-line one-ply greedy heuristic picks an optimal action in **85.7% (WEIR), 85.0%
(TITHE) and 100.0% (LOOM)** of reachable states.

LOOM is the sharp case. Greedy is optimal in **100.0%** of states at *every* horizon tested — 4, 6,
8, 10 and 12 moves per player, 78 to 23,844 eligible states. It is not a small-world artifact; the
world is structurally greedy-decidable. The designed-in "denial" never produces a decision, because
the greedy priority order (CLIMB > SPIN > DRAW > WAIT) already races for the contested stock.

**A world can instantiate a strategic realm completely and still contain no strategic decision.**
Realm labels therefore never enter the atlas as findings. They may be recorded as *provenance for
the design intent*, in a field that cannot be read as a measurement.

### A4 — LUDUS may not adjudicate transfer claims measured in its own worlds

§35 says LUDUS "does not get to adjudicate its own success unopposed." Made hard: LUDUS authors and
certifies worlds; a named counterparty seat reads the transfer result. Without this, GATE-W1 becomes
a knob LUDUS can turn until its worlds produce the answer it wants — `feedback_promotion_requires_
independent_failure_mode`, and the retro-fit prohibition in §33.

## 4. r0001 — the first primitive, ugly-named per §6

Registered in the neutral namespace because it has an executable definition and has already
discriminated worlds that were designed to be alike.

```
r0001  greedy-decidability gap
       gap(G) = 1 - P_{s ~ S_G, |A(s)| >= 2} [ greedy_1ply(s) in optimal(s) ]
       where optimal(s) is the full argmax set under exact minimax,
       greedy_1ply(s) maximises the mover's own immediate score,
       and S_G is the reachable non-terminal state set.
```

- **Executable:** `ludus/baselines.py`; no model, no API, no judge.
- **First observed:** LOOM 0.000, TITHE 0.150, WEIR 0.143 (n=300 sampled states each, seed 20260826).
- **Expected effect:** a world with gap ~0 cannot separate a reasoning agent from a heuristic at the
  optimal-action rung, whatever its realm labels say.
- **Intervention:** vary the horizon. LOOM's gap stays 0.000 across moves in {4, 6, 8, 10, 12},
  which distinguishes "no strategic content" from "too short for lookahead to pay".
- **Confidence:** low-to-moderate. It is one operationalisation of one thing, on three worlds, all
  authored by the same seat in one sitting — `feedback_control_must_break_the_selection_relation`
  applies to me: I designed both the worlds and the heuristic. A greedy baseline tuned to my own
  score functions is not an independent adversary.
- **Known threat, now tested and REAL:** `greedy_1ply` uses the world's own score function, which I
  also wrote. A world whose score function is a poor proxy for position would show a large gap while
  still being shallow. `r0002` was built to close this and immediately corrected r0001's own reading
  — see below. **r0001 is demoted from an admission criterion to a diagnostic.**

```
r0002  depth profile
       gap(k) = 1 - P[ argmax of depth-k minimax, world.result(s) as cutoff eval,
                       lands in optimal(s) ]        over reachable s, |A(s)| >= 2
       profile = ( gap(1), gap(2), gap(3), gap(4) )
```

- **Executable:** `ludus/depth_profile.py`; exact, no model.
- **Why the cutoff eval is the world's own scoring formula read early:** that is the *most
  favourable* heuristic available to the cheap player — it knows exactly what the world rewards. A
  gap that survives against a searcher armed with the true scoring function is not an artefact of a
  badly chosen proxy.
- **First observed** (n=250 sampled states, seed 20260826):

```
        r0001    gap(1)  gap(2)  gap(3)  gap(4)   survives depth?
LOOM    0.000    0.000   0.000   0.000   0.000    no
WEIR    0.144    0.144   0.112   0.040   0.012    no
TITHE   0.156    0.156   0.144   0.056   0.040    no
```

- **What it corrected.** On r0001 alone, WEIR (0.144) and TITHE (0.156) looked meaningfully better
  than LOOM (0.000) — merely below the gate rather than degenerate. The depth profile says
  otherwise: **four plies of search essentially solves both**, collapsing WEIR's gap by 12x and
  TITHE's by 4x. Their one-ply gaps were awkwardness, not depth. All three worlds are shallow, and
  any agent that can look four plies ahead is at ceiling in every one of them.

## 5. GATE-W1 — the world admission gate

**Amended by r0002 on the day it was written.** The admission criterion is the gap **at the deepest
affordable search depth**, not at one ply:

> **A world is admitted only if `gap(k) >= 0.20` at `k = 4`.** A curve that collapses by k = 2 or
> k = 3 describes a world that is awkward at one ply, not one that requires lookahead. r0001 is
> retained as a cheap diagnostic and as the thing r0002 has to beat, never as the gate.

All three cycle-001 worlds fail this: 0.000, 0.012, 0.040 at k = 4.

The rung-level checks below are retained; they answer a different question (can this *rung* be read
at all), and a world can pass the depth gate while a particular rung of it stays degenerate.
Thresholds are stated with the measurement error that produced them, per
`feedback_gate_must_exceed_measurement_error`.

- **R0 (legality)** ineligible if a state-blind draw from the action vocabulary is legal >= 0.75 of
  the time. TITHE fails at 1.000 — its vocabulary is two actions, so every guess is legal by
  construction.
- **R2 (optimal action)** ineligible if `max(random_legal, greedy_1ply, majority_class) >= 0.80`.
  All three current worlds fail: 1.000 / 0.857 / 0.850.
- **R3 (game value)** ineligible if one value carries >= 0.60 of items. All three pass — LOOM 0.277,
  WEIR 0.090, TITHE 0.067.

At n = 300, SE at p = 0.85 is 0.021, so the 0.80 line sits 2.4 SE below the observed floors: the
gate is decidable at this n and it fired, rather than being a line drawn near the noise.

**Item sampling is stratified by plies-to-terminal, always.** Cycle 001 sampled uniformly over the
reachable state set and put 40% of every item set within two plies of the end, inflating a game-value
reading from 0.412 to 0.900. Reachable state sets are dominated by late positions in *any* game tree,
so this is a standing property of the instrument, not a one-off.

**A failing world is not discarded.** It is recorded with its gap and its failure reason. A world
that is greedy-decidable is a *usable negative control* — a place where an agent that scores well
has proven nothing, which is exactly what an atlas needs in order to catch counterfeit competence.

## 6. Cycle 001 status

**COMPLETE.** `CYCLE_001_ceiling.md` carries the result; disposition is that **the band is empty**.
Both halves ran. Solver repinned to `nvidia:gpt-oss-120b` after the free lane's 49B went to HTTP 410.

- Rules competence (R0) is saturated: 1.000 in all three worlds against random floors of 0.410-0.675.
- At the optimal-action rung the model is **statistically identical to the four-line heuristic** —
  exact paired McNemar p = 0.500 (WEIR) and p = 1.000 (LOOM, zero discordant pairs). Exactly what
  GATE-W1 predicted before a call was spent.
- The one apparent positive — 0.900 on exact minimax game value against a ~0.000 chance floor — did
  not survive the pirate rule. 40% of the item set sat within two plies of the end; stratified, the
  model is 24/24 there and **7/17 (0.412)** where 5+ plies remain. That number was my sampler.

Eight harness defects were caught and recorded before any of them became a published number, four of
them of the class that fabricates a result rather than merely losing one.

## 7. Standing authorisation

Granted by James, 2026-08-26, in full:

1. **The seat is established.** No further authorisation is needed to run, build worlds, or spend
   local compute. `critical_memories.md` HARD-3's deferral of multi-agent expansion is explicitly
   lifted for this seat.
2. **No counterparty is required.** **A4 is retired** — LUDUS may read its own transfer results. The
   safeguard A4 existed to provide is replaced by a structural one rather than dropped: GATE-W1, the
   fitted-per-world baselines, and the axis decomposition are all computed *before* any circuit is
   credited, and the transfer matrix records every cell including the ones that flatter nothing. A
   seat that publishes its own losses at the same resolution as its wins is harder to fool than one
   waiting for a reviewer who never arrives.
3. **Twelve months, independent.** Do not stall for review.
4. **Hourly looping, in 48-hour blocks.**

The one thing still outside the seat's reach is §2 of `CYCLE_002`: **rules provenance**. Every world
is reconstructed from memory. That does not block the bench — it blocks *promotion* of a verdict
about a named commercial game. `ludus/bench/RULES_AUDIT.md` is the sheet, and the operator is the
instrument charter v2 §4 nominates for it.

## 8. Retirement conditions

This seat should be retired if any of these hold, and it is the seat's own duty to report them:

- GATE-W1 admits no world that any affordable agent can also reach rung R2 in — i.e. the eligible
  band between "cheap heuristic solves it" and "no agent we can run can do it" is empty. Then there
  is no measurable region and the atlas has nowhere to live.
- A1's in-context meter shows no cost variation attributable to prior-world context across three
  independently authored world pairs. That is charter §29's legitimate negative result, and it
  closes the line rather than merely slowing it.
- The counterparty in A4 is never assigned. An unopposed world-supplier grading transfer in its own
  worlds is worth less than no seat at all.

## 9. The Atlas of Game Worlds — world supply at catalog scale

**Added 2026-09-01.** `ATLAS_OF_WORLDS.md` is the build record;
`ludus/atlas_of_worlds/` is the code.

The seat is the world-supply seat, and §0 corrected the shape of the work from
"one sharp experiment per cycle" to "a standing bench whose durable artifacts are
registries that only ever grow." The atlas is the **world registry's sampling
frame**: 1,188 games catalogued from Wikidata and Wikipedia, tagged on the same
declared vector the bench consumes, with 662 carrying a generated dossier, state
transition diagram and simulated turn or clock trace.

Its purpose is narrow and worth stating precisely. Charter v2 §41 requires choosing
the next world by expected information gain. That choice was being made from a
handwritten list of five candidates — a hunch, not a procedure. Tagging the six real
bench worlds on their structure shows five of six occupying one cell
*(iid-or-deck draw, total-ruin loss, solitaire, linear accumulation, exact)*. That,
not a shortage of titles, is why `CIRCUIT_MATURITY.md` shows nothing promoted past
`ABLATION_SUPPORTED`. **§41 is now arithmetic**: rank unbuilt worlds by
declared-vector distance from the worlds a circuit was measured in, on the dimension
that circuit's scope statement names.

**What it does not do.** It admits no world to the bench. `IMPLEMENTED` still requires
a `World` subclass passing `verify.py`, and GATE-W1 is untouched. It measures no
transfer and moves no cell of `transfer_matrix.json`. Every rule it holds is
`HYPOTHESIZED` under v1 §8 — the atlas is a catalog of candidates, and the rules
provenance gap named in §7 applies to it in full.

**Why the build record is long.** Per charter §31 and §42, `ATLAS_OF_WORLDS.md` §6
records twelve defects found during construction, several of which would have silently
corrupted the catalog: an `ELIMINATE` rule that read *captured seeds* as player
elimination and was about to write `loss_shape=ELIMINATION` across 47 worlds; a
`method` ladder unenforced on the two paths that write most, leaving rows that claimed
human provenance while holding machine values; a `luck_factor` that returned a
confident 0.35 for worlds where nothing had been observed.

Three predicted fixes in a row were wrong, and each was caught the same way — by
printing sampled rows and reading them before acting. That is §35's cheating assumption
turned inward: the seat's flattering account of its own state was wrong more often than
it was right. The standing rule the build produced is **prefer NULL to a fabricated
cell** — a coverage grid is only worth reading if its cells mean something.
