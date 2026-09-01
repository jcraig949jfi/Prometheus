# LUDUS Cycle 001 — CEILING-1

**Date:** 2026-08-26. **Seat:** Ludus (Claude Code, Opus 5), M1 / F:\.
**Status:** COMPLETE. Disposition: **the band is empty** — three worlds authored to be strategic
cannot distinguish an affordable agent from four plies of trivial search, and the one apparent
positive was near-terminal item sampling (§5.3).
**Code:** `ludus/worlds.py`, `ludus/baselines.py`, `ludus/r0001_sweep.py`, `ludus/ceiling1.py`,
`ludus/report.py`. **Ledgers:** `ludus/ledgers/cycle001_*.json{,l}`.

---

## 1. Why this cycle and not the one the charter names

`CHARTER.md` §37 opens the first campaign with 30-50 acquired games. Program doctrine says the
opposite: `feedback_verify_signature_exists_before_controls` is a HARD POSTURE — controls against
bias do not protect a mis-aimed instrument, so establish that the target signature exists before
building the apparatus around it. `feedback_gate_must_be_shown_reachable` adds the companion rule:
compute the attainable range before reading anything off a gate.

So cycle 001 asks the cheapest question that could invalidate the whole programme:

> **Is there a measurable band at all — between what a trivial heuristic already achieves in a world,
> and what an agent this program can actually run achieves in it?**

If that band is empty, no transfer measurement can live in it, and 50 formalised rulebooks would
have been 50 rulebooks' worth of wasted work.

Three worlds were authored for the test — LOOM, WEIR, TITHE (`ludus/worlds.py`) — deliberately
**synthetic and novel**, not reskins. That removes cheat classes C001-C005 (rulebook, strategy-guide,
title, component and edition leakage) by construction rather than by control. All three are
two-player, deterministic, perfect-information, and small enough to solve exactly by minimax, so
every rung's ground truth is computed rather than judged. No judge model appears anywhere in this
cycle.

## 2. The finding, obtained with zero model calls

Each world was authored *specifically* to instantiate named realms from charter §4:

- **LOOM** — resource economy: a DRAW -> SPIN -> CLIMB conversion chain, destroyed intermediates,
  a monotone track, a shared depleting STOCK for denial, a fixed 6-move horizon.
- **WEIR** — spatial control: budgeted claiming of links on a shared graph, connectivity scoring,
  every link taken is a link denied, and a two-YIELD ending that lets a player ahead close the game.
- **TITHE** — temporal strategy: a descending-price queue, one offering at a time, timing windows,
  purse depletion.

Every one of those realms is genuinely present in the rules. And a **one-ply greedy heuristic —
four lines, maximise your own immediate score — picks an optimal action** in:

```
LOOM    100.0%      (0.0% gap)
WEIR     85.7%      (14.3% gap)
TITHE    85.0%      (15.0% gap)
```

n = 300 sampled reachable states per world with branching >= 2, seed 20260826, ground truth by exact
minimax. `ludus/ledgers/cycle001_attainable_range.json`.

**Every world fails GATE-W1 at the optimal-action rung** (`ROLE.md` §5: a rung is ineligible if
`max(random_legal, greedy_1ply, majority_class) >= 0.80`). At n = 300, SE at p = 0.85 is 0.021, so
the 0.80 line sits ~2.4 SE below the observed floors — the gate was decidable at this n, and it
fired.

TITHE additionally fails at the legality rung for a duller reason worth recording: its action
vocabulary is two words, so a state-blind guess is legal **100%** of the time. Legality cannot be
measured in a world where every utterance is legal.

### 2.1 Two rival explanations, both attacked

A gap of zero has two cheap explanations besides "the world has no strategic content". Both were
tested exhaustively — over the entire eligible state set, not a sample —
in `ludus/r0001_sweep.py`.

**Is it a small-world artefact?** Vary only the horizon:

```
LOOM moves/player   4      6      8     10     12
eligible states    78    528   2444   8412  23844
r0001 gap      0.0000 0.0000 0.0000 0.0008 0.0000
```

No. The gap does not open as the horizon grows by 3x. LOOM is structurally greedy-decidable.

**Is it an artefact of the score function I happened to write?** I authored the world, its scoring,
and the greedy baseline that reads that scoring — `feedback_control_must_break_the_selection_relation`
applies to me. Varying the score weights and the conversion yield moves the gap over
**[0.0000, 0.1004]**, so scoring *is* a cause — but the maximum gap reachable anywhere in the grid is
0.100, still half of what GATE-W1 requires. LOOM cannot be rescued by rescoring either.

The mechanism is explicit rather than mysterious: CLIMB converts 1 THREAD to 1 RUNG for a net
`w_rung - w_thread`; SPIN converts 3 DROSS to `spin_out` THREAD for a net `spin_out * w_thread`.
Greedy ranks CLIMB above SPIN exactly when `w_rung - w_thread > spin_out * w_thread`, and throughout
that entire region greedy coincides with optimal play. The zero is a *region*, not a coincidence.

### 2.2 What this says about charter §4

> **A world can instantiate a strategic realm completely and still contain no strategic decision.**

The designed-in "denial" in LOOM never produces a decision, because the greedy priority order
(CLIMB > SPIN > DRAW > WAIT) already races for the contested stock. Naming a realm does not create
content, and the realm labels are not evidence that content exists. This is charter §5's own law
("no noun without a test") applied to charter §4's list, and it fired on the first three worlds
anyone built for this seat — mine.

Consequence, recorded as `ROLE.md` A3: realm labels never enter the atlas as findings. They may be
recorded as provenance for design intent, in a field that cannot be read as a measurement.

### 2.25 The gap does not survive depth either — r0002

r0001 asks about a one-ply heuristic. That leaves an obvious escape: perhaps WEIR (14.4% gap) and
TITHE (15.6%) are merely *awkward* at one ply and genuinely require lookahead a little deeper.

`ludus/depth_profile.py` tests it directly. `gap(k)` replaces greedy with depth-k minimax, using
`world.result(s)` read early as the cutoff evaluation — deliberately the **most favourable**
heuristic available to a cheap player, since it knows exactly what the world rewards.

```
        r0001    gap(1)  gap(2)  gap(3)  gap(4)
LOOM    0.000    0.000   0.000   0.000   0.000
WEIR    0.144    0.144   0.112   0.040   0.012
TITHE   0.156    0.156   0.144   0.056   0.040
```

n = 250 sampled reachable states per world, seed 20260826, exact minimax ground truth.
`ludus/ledgers/cycle001_r0002_depth_profile.json`.

**Four plies of search essentially solves all three worlds** — WEIR's gap collapses 12x, TITHE's 4x.
Their one-ply gaps were awkwardness, not depth. Four plies is trivial; any agent that can search that
far is at ceiling in every world this cycle produced.

This also corrected r0001's own reading. On the one-ply number alone, WEIR and TITHE looked
meaningfully better than LOOM — below the gate rather than degenerate. They are not. **r0001 is
demoted from an admission criterion to a diagnostic, and GATE-W1 now keys on `gap(k) >= 0.20` at
k = 4** (`ROLE.md` §5). All three worlds fail at 0.000, 0.012, 0.040.

The false positive r0002 was built to catch is specific and was worth catching before cycle 002 spent
its budget hunting for a world with a large r0001 gap: such a world can be produced trivially by
writing a score function that is a poor proxy for position, and it would be no more measurable than
LOOM.

### 2.3 r0001, and its own weakness

The first primitive is registered in the neutral namespace per charter §6:

```
r0001  greedy-decidability gap
       gap(G) = 1 - P[ greedy_1ply(s) in optimal(s) ]  over reachable s with |A(s)| >= 2
```

Executable, model-free, and it discriminated three worlds designed to be alike. Its stated weakness
is real and untested: `greedy_1ply` reads the world's own score function, which I also wrote. A world
whose score function is a poor proxy for position would show a large gap for a trivial reason and
would pass GATE-W1 while being no better. That is cycle 002's first job, not a caveat to be waved
through.

### 2.4 Decision-n: two cells can never be read at any n

`ludus/ledgers/cycle001_decision_n.json`, at 80% power, alpha 0.05:

```
cell        cheap floor   n for floor+0.10   n to distinguish from 0.98
WEIR:R0        0.401            191                     4
LOOM:R0        0.655            168                    11
WEIR:R2        0.857             74                    43
TITHE:R2       0.850             78                    40
LOOM:R2        1.000           none                  none
TITHE:R0       1.000           none                  none
```

`none` is the point. Where the cheap floor is exactly 1.000, **no sample size can detect an
improvement** — the gate is not merely underpowered, it is ineligible to fire on any input. That is
the `feedback_gate_must_be_shown_reachable` failure mode, caught here before it cost a run rather
than after.

## 3. Eight harness defects, each caught before it became a number

Recorded because `feedback_verdict_without_rows_is_an_assertion` and because each would have shipped
a confident wrong reading.

1. **Rules that the implementation did not obey.** WEIR's rules text promised a consecutive-YIELD
   ending that `is_terminal` never applied, and TITHE's discard clause was stated ambiguously against
   its own code. The model would have been scored against rules it was never given. Found by reading
   a rendered prompt rather than trusting the code. Fixed; the yield count is now real, strategic
   (a player ahead can close the game), and shown in the position.
2. **Markov incompleteness.** After adding the yield rule, the rendered position had to expose it or
   the item would have been unanswerable in principle. Now tested: across all reachable states in all
   three worlds, **zero** rendered positions map to more than one answer.
3. **Transport failures counted as wrong answers.** The first pilot reported
   **accuracy 0.000, parse_failure_rate 1.00** — a hard ceiling that was entirely four HTTP 410s.
   Transport failure is now its own row class, excluded from the denominator and reported beside the
   number.
4. **R1 scored against a format never shown.** Rung R1's ground truth was an internal state
   signature; the model was shown a different rendering and asked for "the same field format". It
   was being scored on format compliance, not transition prediction. Truth is now the rendered
   position, and `ludus/report.py` reports strict and loose normalisations **separately** — choosing
   one after seeing the answers would be the post-hoc fitting charter §33 forbids.
5. **The item set was not reproducible.** Per-cell seeds derived from Python's `hash()`, which is
   salted per process, so the items drawn during a run could not be rebuilt afterwards. An offline
   diagnosis I ran compared answers against the wrong items and produced a confident, void reading.
   Fixed with `zlib.crc32`; rows now also carry their own `truth` and `position`, so rescoring never
   needs a rebuild.
6. **A token cap that manufactured a competence gradient.** The pinned solver is a reasoning model
   that emits its answer only after a long hidden pass. At `max_tokens = 4096`, a WEIR R2 call
   returned `completion_tokens = 4096` **exactly, with an empty content channel** — the entire budget
   spent reasoning, no ANSWER line ever produced. A full 9-cell run at that cap
   (`ludus/ledgers/cycle001_ceiling_TRUNCATED-4096.*`, quarantined rather than deleted) showed
   **parse-failure rate equal to truncation rate in every single cell**, and truncation tracking rung
   difficulty: 0.00 at R0, 0.15-0.30 at R2, 0.25-0.45 at R3. Read naively that is a clean competence
   gradient down the ladder. It was the cap. The scores were depressed most exactly where the task
   was hardest — arm-correlated missing data, the artefact `feedback_truncation_can_flatter_a_gate`
   names. It cannot be rescued by dropping truncated rows either: truncation correlates with item
   difficulty, so conditioning on "produced an answer" conditions on a post-treatment variable, the
   same collider AMA's review caught in its own amended objective. Calibrated at 8192 and 16384 on
   the same three items: no truncation at either, completions 2653-5662 tokens. Repinned to 8192.
7. **A patch that failed silently and was believed.** The cap fix above was applied with
   `str.replace` against a comment string containing an em dash where the patch text had a hyphen.
   It matched nothing, wrote the file back unchanged, raised no error — and the "fixed" run was
   launched and completed at the old cap. Caught only because the report header printed
   `max_tokens: 4096`. Every later patch asserts its target matched, the constant is imported and
   asserted before launch, and **every row now records the cap it ran under** so a ledger can never
   again be silently mixed-config.
8. **A baseline conditioned on the model's success.** `score_row` stamps `greedy_correct` only on
   rows where the model produced a parseable answer, so reading the greedy baseline off the ledger
   measured the heuristic on an easier subset exactly when the model struggled — conditioning the
   *control* on a post-treatment variable. On WEIR:R2 it moved the baseline from 0.800 to 0.842 in
   the flattering direction for the gate. `ludus/report.py` now rebuilds the full item set (possible
   only because defect 5 was fixed) and scores greedy over every item, and compares model to
   heuristic with an exact paired McNemar rather than a Wilson interval against a point estimate
   that was measured on the same twenty items.

## 4. Cross-seat flag for Ergon — not acted on, not repaired

`ergon/probe/solver.py` pins `nvidia:nemotron-super-49b-v1` as a verified solver. As of 2026-08-26
both it and `-v1.5` return **HTTP 410 Gone**; `nvidia:deepseek-v4-flash` returned HTTP 529;
`nvidia:gpt-oss-120b` is alive. `ergon/probe/ledgers/coldband_drip/console.log` records
`block A/B nvidia:nemotron-super-49b-v1 -> complete` at 20:38 UTC today, and the last rows in
`blockB_nvidia_nemotron-super-49b-v1.jsonl` are genuine `status: ok` completions — so the solver was
alive when those rows were written and this may simply be a retirement that happened since.

**I have not touched that lane, its ledgers, or its pins** — another seat's ledger state is not mine
to repair (`feedback_autostash_empty_diff_is_not_committed`, and the Diomedes precedent of recording
ledger state without repairing it). Ergon should verify whether the drip's `-> complete` line can be
emitted over transport failures. If it can, the drip would silently produce arm-correlated missing
data, which is the one artefact that probe is built to avoid.

LUDUS is repinned to `nvidia:gpt-oss-120b`, and the repin is recorded in `ludus/ceiling1.py` rather
than silently swapped — a solver change is a solver-set change.

## 5. Model half — result

Pinned `nvidia:gpt-oss-120b`, max_tokens 8192 (calibrated, §3.6), n = 20 per cell, 3 workers.
**Screening resolution, not decision-n** — §2.4 gives the decision-n for each cell and none of them
is 20. `ludus/ledgers/cycle001_ceiling_screening8k.*`, report in `cycle001_report_screening8k.json`.

Rung R1 was dropped from this screening: its cells were taking >20 minutes each at 30 items and it
answers a rules-competence question, not the ceiling question. Deferred, not silently omitted.

```
cell        n   acc    Wilson95        rand   greedy   maj    pfail  trunc
WEIR:R0     20  1.000  [0.839,1.000]   0.410    -      0.150   0.00   0.00
WEIR:R2     20  0.900  [0.699,0.972]   0.321  0.800    0.450   0.05   0.05
WEIR:R3     20  0.900  [0.699,0.972]   0.000    -      0.250   0.05   0.05
LOOM:R0     20  1.000  [0.839,1.000]   0.675    -      0.400   0.00   0.00
LOOM:R2     20  0.950  [0.764,0.991]   0.517  1.000    0.400   0.05   0.05
LOOM:R3     20  0.900  [0.699,0.972]   0.000    -      0.250   0.10   0.10
TITHE:R0    20  1.000  [0.839,1.000]   1.000    -      1.000   0.00   0.00
TITHE:R2    20  0.700  [0.481,0.855]   0.500  0.950    0.750   0.30   0.30   NOT READABLE
TITHE:R3    20  0.650  [0.433,0.819]   0.000    -      0.150   0.35   0.35   NOT READABLE
```

**TITHE:R2 and TITHE:R3 are not readable.** Truncation is 0.30 and 0.35 even at the calibrated cap,
and parse-failure equals truncation exactly in both — the same artefact as §3.6, merely smaller. Their
numbers are floors, not ceilings, and are excluded from every conclusion below. TITHE:R0 is separately
vacuous: its action vocabulary is two words, so 1.000 against a 1.000 random floor says nothing.

### 5.1 Rules competence is saturated

R0 is **1.000 in all three worlds**, against random floors of 0.410 (WEIR) and 0.675 (LOOM). Wilson
[0.839, 1.000] clears both. The pinned model produces legal actions in novel worlds it has never
seen, from the rules text alone. That rung is at ceiling and is not worth measuring again.

### 5.2 At the optimal-action rung the model is indistinguishable from four lines of code

The comparison must be paired — greedy's rate is estimated on the *same 20 items*, so testing a
Wilson interval against greedy's point estimate is the wrong test. Exact McNemar on the discordant
pairs only:

- **WEIR:R2** — model 0.900, greedy 0.800. Discordant 2/0 in the model's favour, **p = 0.500**.
- **LOOM:R2** — model 0.950, greedy 1.000. Discordant **0/0**: on every row the model parsed, it and
  the heuristic chose identically. Its single miss is the one truncated row. **p = 1.000**.

This is exactly what GATE-W1 predicted before any call was made. The model is not beaten by the
heuristic and does not beat it — at this n, in these worlds, **the two are the same policy**. That is
the point of the gate: a world where a reasoning agent and a four-line function are
indistinguishable cannot carry a transfer claim, whatever the agent scores.

### 5.3 The one number that looked like a finding, and did not survive

WEIR:R3 and LOOM:R3 both return **0.900 on exact minimax game value** against a chance floor of
~0.000 and a majority-class baseline of 0.250. Taken at face value that is a striking result: the
model computing exact game-theoretic values in novel worlds.

Charter §36 says attack it first. Stratifying the same items by how much game is actually left
(longest remaining play from the position):

```
                  1-2 plies left   3-4 plies left   5+ plies left
WEIR                  8/8              9/10             1/2
LOOM                  8/8              5/5             5/7
TITHE                 8/8              4/4             1/8
combined            24/24 (1.000)    18/19 (0.947)    7/17 (0.412)
```

**40% of every R3 item set had two or fewer plies remaining**, and the model is perfect on all of
them — those positions are nearly over and their value is close to readable off the board. Where five
or more plies remain, accuracy falls to **0.412**.

The headline 0.900 is a fact about my sampler, not about the model. Uniform sampling over the
reachable state set over-weights late positions, because the game tree fans out toward its end. The
sampling strategy was the analysis (`feedback_sampling_strategy_is_analysis`), and it inflated an
apparent capability by ~0.5 in the stratum that matters.

Honest statement of the R3 result: **the pinned model computes exact game values reliably only when
the game is nearly over, and at 5+ plies remaining it is at 0.412 with n = 17 pooled across three
worlds** — a screening number with an SE of 0.119, quoted with that width rather than without it.

### 5.4 What the model half establishes

The band this cycle set out to find — between what a trivial policy achieves and what an affordable
agent achieves — is **empty at R0 (both at ceiling), empty at R2 (statistically identical), and
present only at R3, where it is largely an artefact of near-terminal item sampling.**

That is a coherent negative result and it is charter §29's kind of victory. It does not say the model
cannot reason. It says **these three worlds cannot tell**, which is what GATE-W1 said before the
calls were spent, and is why the gate is the seat's product rather than the worlds are.

## 6. What this changes about which world to enter next (charter §38)

Not "we added three worlds". The three answers that change the next move:

1. **Do not acquire rulebooks yet.** The gating problem is not world supply, it is world
   *eligibility*. Three worlds authored by someone actively trying to make them strategic all failed
   GATE-W1 at R2. Published games have no obligation to do better, and each one costs acquisition,
   verification, formalisation and a contamination control that synthetic worlds do not need.
2. **The next world must be authored to a target r0001 gap, and the gap must be swept over scoring,
   not read once at the author's chosen weights** (§2.1). GATE-W1 gains that requirement.
3. **Attack r0001 before trusting it** (§2.3). A gap that is large only because the score function
   is a poor proxy for position is not a measurable world, and the current definition cannot tell the
   difference.

4. **Stratify item sampling by plies-to-terminal, always.** §5.3 showed uniform sampling over the
   reachable state set put 40% of every item set within two plies of the end, where the model is
   perfect, and inflated an R3 reading from 0.412 to 0.900. The reachable state set of any game is
   dominated by its late positions; that is a property of game trees, not of these three worlds, so
   the defect would have recurred in every world LUDUS ever builds. Stratified sampling with
   per-stratum reporting becomes part of the item builder, not a per-cycle remembering.
5. **Raise the token cap per world, not globally.** TITHE still truncated 30-35% at the calibrated
   8192 while WEIR and LOOM sat at 0.00-0.10. The cap has to be calibrated against the *hardest cell
   in each world* and the calibration recorded, or a world's numbers are floors.

Cycle 002 is therefore: build the world-admission gate into world *construction* — search the design
space for a world whose depth profile still shows `gap(4) >= 0.20` — with stratified sampling and
per-world cap calibration in the harness from the start. The atlas gets its first entries when there
is a world worth entering into it.

**And the honest possibility that cycle 002 has to hold open:** it may be that small, exactly
solvable, contamination-free worlds and measurable strategic depth are in tension — that anything
small enough to solve exactly is small enough to search exhaustively. If three more attempts fail
GATE-W1 the same way, that tension is the finding, and it is a sharper one than the atlas was ever
going to be. It would say the transfer question cannot be asked in worlds we can also ground truth,
which is a real constraint on the charter rather than a failure to execute it.
