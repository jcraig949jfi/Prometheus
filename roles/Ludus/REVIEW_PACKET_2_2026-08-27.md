# LUDUS — External Review Packet #2: Playtest Design

**Date:** 2026-08-27 · **Supersedes:** review packet #1 (same day) · **Status:** five cycles, one
verdict issued and then demoted, apparatus repaired, no playtests yet designed

This is a technical brief, engineer-to-engineer. Not a publication, not intended for one. It is
self-contained: a reviewer who has seen nothing else should be able to give specific advice.

**Packet #1 asked whether our measurements meant anything. A review found they partly did not, and we
demoted our own verdict within the hour. This packet asks a different question: given a repaired
apparatus, what should we actually PLAY, and how?**

---

## 0. What review is wanted, and what is actively harmful

**Wanted.** Playtest design. Specifically: which experiments in game worlds would discriminate
between the live hypotheses in §4, what their controls should be, and where our proposed designs in
§5 are confounded, underpowered, or measuring the wrong thing. Attacks on §3's apparatus are also
welcome.

**Explicitly NOT wanted, and harmful here.** Do not tell us which *strategic concepts* to look for.
Not tempo, optionality, initiative, engine-building, threat, trajectory-shaping, risk aversion,
tilt, or similar. The largest single risk to this project is contaminating it with our own
vocabulary, and §6 records the two occasions we did it to ourselves — one of those circuits scored
0.2501 against a null circuit's 0.7398, i.e. a concept-seeded rule lost badly to one that reads
nothing at all. If a concept is unavoidable, frame it as a hypothesis with a stated kill condition,
never as a thing to go find.

**Also unhelpful:** endorsement. Convergence between language models on a critique is corpus gravity,
not validation. The previous review's entire value came from one cheap attack that reversed a
conclusion. One such attack beats ten pages of agreement.

**A note on what the last review achieved,** because it calibrates what we are asking for. It
identified that our headline metric was an on-policy score, therefore a *product* of exposure and
competence, and that we had attributed the whole thing to competence. We ran the separation. The
verdict flipped. That is the shape of useful review here.

---

## 1. The program, in one screen

**Prometheus** is a long-running research program asking whether failure, representation and search
state can be turned into structure that makes later reasoning cheaper. **LUDUS** is one seat inside
it, authorised for 12 months of independent operation.

Premise: a well-specified game is a bounded artificial world with enumerable physics — entities,
state, legal transformations, scarcity, uncertainty, irreversible commitments, measurable outcome.
Thousands of independently designed games therefore form an accidental laboratory.

**The central question:**

> Does solving one strategic world leave behind executable structure that reduces the cost of
> mastering a *different* one — and what exactly is that structure a property of?

The default alternative hypothesis is always that apparent transfer is memorisation, surface
similarity, shared vocabulary, or an artifact of how the benchmark builds its counterfactual.

---

## 2. Current state, including the verdict we withdrew

**21 worlds, all solved exactly** by backward induction over complete reachable state spaces. State
counts 34 to ~440,000. No sampling anywhere, so no standard errors — a difference of 0.0001 is real.

- **4 reconstructed named worlds** (Flip 7, Martian Dice, Incan Gold, Can't Stop) plus 2 more
  (Lucky Numbers, Coloretto) — rules reconstructed **from memory, no rulebook consulted**, all marked
  `HYPOTHESIZED`.
- **15 FOUNDRY synthetic controls** — parameterised so exactly one property moves at a time
  (`gate`, `decoy`, `arity`, `capacity`, `p_bust`, `decay`). Controls, never reported as games.

**9 circuits** — executable policies written only against a compiled transition table. A circuit
cannot read a rulebook, name a card, or know which game it is in. Ugly identifiers (`r0003`) are
permanent; English names are conveniences and never canonical.

### The result sequence, compressed

- **Cycle 001.** Three worlds authored specifically to instantiate named strategic realms. A one-ply
  greedy heuristic plays them optimally 100.0% / 85.7% / 85.0% of the time; four plies of trivial
  search essentially solves all three. *A world can instantiate a named strategic realm completely
  and contain no strategic decision.*
- **Cycle 002.** One untuned rule — `r0003: STOP iff P(death)·pot >= E[immediate gain]` — retains
  0.9991 of optimal in Flip 7 and, transplanted with zero tuning into a completely different surface
  (cards→dice), 0.9095 in Martian Dice, beating every hand-tuned threshold there. But an ablation put
  **86% of Martian Dice's residual on the *other* axis**. The genre label groups those games by their
  shared *easy* part.
- **Cycle 003.** `r0003`'s scope prediction was registered *before* two worlds were built; both
  returned 1.0000. Unpredicted: the SELECT circuit ordering **completely reverses** between two
  worlds sharing an interface (one circuit worst-of-five in one, best-of-five in the other).
- **Cycle 004.** A basis audit. Partner matrix `E_ijk` over circuit × partner × world, exact
  decomposition. Issued **`CONTEXTUAL_BASIS_REQUIRED`** — circuit value is mainly a property of the
  world.
- **Cycle 005 — we withdrew that verdict.** External review pointed out `E_ijk` is on-policy and
  therefore *exposure × competence*. We measured per-decision regret against optimal continuation
  under three state weightings:

```
REAL (reconstructed) worlds          circuit   world   circuit x world
  REFERENCE occupancy (common dist)   0.8528  0.0451       0.1021
  SELF occupancy (circular)           0.7409  0.0301       0.2289
  UNWEIGHTED (all states equal)       0.2623  0.1155       0.6222
  DISAGREEMENT rate                   0.2530  0.0564       0.6906

  cycle 004 on-policy, same worlds:   0.2126  0.0696       0.4374
```

Under a **common reference distribution** of decision states the circuit main effect dominates
(0.8528) and `circuit × world` collapses to 0.1021. Verdict demoted to
`CHALLENGED-AND-NOT-SUSTAINED`, replaced by `EXPOSURE_CONFOUNDED_HETEROGENEITY` with a registered
kill condition.

**The sharper statement that survived:** *where* a circuit is wrong is world-conditional
(disagreement-rate interaction 0.6906) while *how much its errors cost where competent play actually
goes* is largely circuit-determined (0.1021).

**And one claim we corrected.** Cycle 004 said "what survives is rank, not magnitude" on the strength
of a cross-**partner** Kendall tau of 0.9721. The cross-**world** matrix had never been computed. It
now has:

```
                      mean tau    min tau    negative pairs
REAL (reconstructed)   +0.1079    -0.5556       3 of 6
FOUNDRY                +0.7981    -0.1111       2 of 120
```

Across real worlds, rank does **not** survive — half the world pairs are negatively correlated. And
note the synthetic block says the opposite of the reconstructed block. FOUNDRY says worlds *rescale*;
real games say worlds *reorder*. The controls would have misled us.

---

## 3. The apparatus, and the one lesson that matters most for playtest design

**World interface.** Five methods; every world implements exactly these:

```
initial()          -> S            starting state of a scoring episode
draws(s)           -> [(p, draw)]  exogenous outcome (cards, dice, deck)
options(s, draw)   -> [S]          player's choices after seeing it;
                                   an EMPTY list is death - the pot is lost
pot(s)             -> float        value banked if you stop here
forced_end(s)      -> bool         no further continuation is legal
```

Two decision axes fall out: **SELECT** (which option) and **STOP** (bank or continue). Exact value:

```
V(s)  = sum_draw p * max_{s2 in options(s,draw)} W(s2)     (no options -> 0)
W(s2) = pot(s2) if forced_end(s2) else max(pot(s2), V(s2))
```

**Instruments, each built to prevent a specific failure we actually suffered:** a world-admission
gate keyed on the gap at search depth 4; a fitted-per-world baseline a transferable circuit must
beat; a circuit provenance ledger that subtracts worlds used to invent or tune a circuit from its
evidence; a maturity ladder requiring typed evidence per rung; a rules-fidelity gate that runs before
any circuit touches a world; and a fossil archive that freezes failures before repair.

**THE LESSON MOST RELEVANT TO PLAYTEST DESIGN.** State weighting determines the answer. On identical
circuits and identical worlds, `circuit × world` reads 0.1021, 0.2289, or 0.6222 depending purely on
how decision states are weighted. Two of our three weightings were defective in opposite directions:

- **self-occupancy is circular** — it concentrates weight on states the subject steered itself into,
  which are disproportionately states it handles well;
- **uniform is the mirror defect** — it counts states no competent play ever reaches. (Uniform
  sampling once inflated one of our readings from 0.412 to 0.900.)

**Any playtest proposed below inherits this problem**, and human playtests inherit it worst: a human
generates their own occupancy, so comparing humans to circuits compares two different state
distributions unless something is done about it. Reviewer input on that specific point would be
disproportionately valuable.

---

## 4. What we currently believe, and how weakly

Ranked by confidence, with what would overturn each.

1. **A genre label can group games by their shared easy part.** *Confident.* Overturned by finding a
   genre whose label names the axis carrying most of the difficulty.
2. **Cheap heuristics are far stronger than expected in small worlds.** *Confident.* One-ply greedy
   was optimal in 100% of one world's states; four plies essentially solved three worlds authored to
   be strategic.
3. **`r0003` (myopic stopping) transfers across wide surface gaps.** *Moderate.* Two untouched worlds
   with predictions registered in advance, both 1.0000; beats fitted-per-world baselines in all four.
   Blocked from promotion because it is not yet partner-robust.
4. **Circuit competence is more world-invariant than cycle 004 claimed.** *Weak, one cycle old.*
   Overturned if a common-reference decomposition on ≥4 worlds returns `circuit × world > circuit`.
5. **Interfaces (STOP/SELECT) are the right decomposition.** *Very weak, and possibly circular* —
   see §5.G. We may be measuring our own API.
6. **Nothing whatsoever about LLM reasoning.** Cycles 002–005 contain no model calls at all.

---

## 5. PROPOSED PLAYTESTS — and the questions we cannot answer ourselves

This is what the packet is for. Each subsection states what the playtest would test, the design as
currently conceived, and the specific open questions where reviewer input would change what we build.

### 5.A — Opponent play. All 21 worlds are solitaire.

**What it tests.** Every world so far isolates a player against nature. Real games have opponents,
and opponents introduce denial, hidden information, relative rather than absolute scoring, and the
possibility that a "good" move is good only because of what it forecloses for someone else.

**Design as conceived.** Two-player exact minimax is already implemented (cycle 001's worlds were
two-player). Small worlds remain exactly solvable with an opponent. Opponents would be drawn from the
circuit library itself, so an opponent *is* a circuit, and the existing partner-matrix machinery
extends to (circuit × partner × opponent × world).

**Open questions.**

1. Does an opponent create a **new interface** — something like DENY, a decision whose value is
   entirely about the opponent's option set — or does it change the *mechanism* behind interfaces we
   already have? These imply completely different builds and we cannot tell them apart a priori.
2. If opponents are drawn from our own circuit library, have we built a closed world where the only
   opponents are the ones we already thought of? Is self-play a genuine opponent ladder or does it
   collapse to a single style?
3. Is there a principled opponent to measure *against* — an analogue of the "common reference
   distribution" from §3 — or does every opponent choice smuggle in an arbitrary measure the way
   every partner choice did?
4. Should relative scoring (margin over opponent) or absolute scoring be the outcome variable? These
   give different answers about whether a denial move was good, and we do not know which question we
   are asking.

### 5.B — Human-in-the-loop play, which doubles as the rules audit

**What it tests.** We have exact optimal play for every world. A human's every decision can therefore
be scored as regret against exact optimum, on precisely the same scale as a circuit's. That is an
unusually clean comparison and we have never run it.

It also solves a standing problem: **all our named-game rules were reconstructed from memory and
never checked against a rulebook.** A human who knows the game and plays our simulator will notice
within a few turns that something is wrong. HITL play *is* the rules audit.

**Design as conceived.** Operator plays each reconstructed world through a minimal interface;
every decision is logged with the full option set, the exact optimal action, and the exact regret. No
feedback during play.

**Open questions.**

5. **How many decisions before a human regret profile means anything?** With circuits we have exact
   numbers and no sampling error. A human generates a sample. What is the minimum useful n, and
   should it be counted in games, in decisions, or in *consequential* decisions (states where the
   optimal-vs-alternative gap exceeds some threshold)?
6. **The occupancy problem from §3 bites hardest here.** A human generates their own state
   distribution. Comparing human regret to circuit regret compares two different distributions. Do we
   (a) score the human only on states they actually reached, (b) replay the human's *policy* through
   the reference distribution — which requires inferring a policy from few samples, (c) present the
   human with a pre-selected battery of states drawn from the reference distribution, destroying game
   continuity, or (d) something better?
7. Should the human see **our reconstruction** or the **real game**? Showing the reconstruction makes
   the rules audit work and makes the comparison to circuits exact. Showing the real game measures
   something we cannot score. Are these separable sessions or does one contaminate the other?
8. The operator **knows several of these games well and others not at all.** Is that variation a
   confound to eliminate or the most interesting variable we have — a within-subject skill gradient
   at zero cost?
9. Is there any value in a human playing the **FOUNDRY synthetic worlds**, which have no theme at
   all? It would isolate structure from familiarity completely, but may simply be unpleasant enough
   that the data measures fatigue.

### 5.C — Synthetic skill ladder, and whether it is a valid model of skill

**What it tests.** Construct `π_random`, `π_greedy`, `π_1ply`, `π_2ply`, `π_4ply`, `π_optimal` and
locate the states where consecutive rungs diverge. Those states are candidates for where reasoning
actually matters. This is cheap, exact, and needs no humans and no models.

**Open questions.**

10. **Is a search-depth ladder a valid model of skill at all?** Human expertise may be categorically
    different — pattern recognition and state abstraction rather than deeper search. If depth is the
    wrong axis, a divergence analysis built on it finds the wrong states. What would be a better
    constructed ladder?
11. Should ladder rungs differ in **depth**, in **evaluation quality at fixed depth**, or in
    **which state features they can see**? These are three different theories of what skill is, and
    the third is the only one we have not implemented.
12. Divergence between rungs is measured *somewhere*. Same weighting problem: divergence under whose
    occupancy — the weaker policy's, the stronger's, or the reference?

### 5.D — Bringing language models back in, as circuit AUTHORS rather than players

**What it tests.** Cycles 002–005 contain no model calls. Cycle 001 did: a model was measured on
three exactly-solved worlds, achieved saturated legality (1.000), and at the optimal-action rung was
**statistically indistinguishable from a four-line greedy heuristic** (exact paired McNemar p = 0.500
and p = 1.000). Its one impressive number — 0.900 on exact game value — collapsed to 0.412 when
stratified by how much game actually remained.

**The design we think is more interesting than move-prediction:** ask the model to emit a **circuit**
— an executable stopping or selection rule written against the same five-method interface — rather
than a move. Then the model's output enters the same registry, faces the same fitted-per-world
baselines, the same partner matrix, the same provenance ledger, and the same maturity ladder as our
hand-written circuits. Model output becomes directly comparable to human-authored structure, and it
is exactly measurable because the worlds are exactly solved.

**Open questions.**

13. Is "emit a policy, not a move" the right elevation, or does it merely test **program synthesis in
    a constrained DSL** rather than anything about strategic reasoning? We genuinely cannot tell, and
    it determines whether the whole line is worth building.
14. What is the correct control? A model emitting a circuit that beats a fitted-per-world threshold
    has done something — but so would a model that has memorised push-your-luck strategy from
    training data. The worlds are named games with public strategy discussion.
15. Should the model see the **rules text**, the **compiled transition table**, or **sampled
    trajectories**? These are three very different tasks, and the second removes surface entirely
    while the third removes rules comprehension.
16. If a model-authored circuit *fails*, is that informative? Our own concept-seeded circuits failed
    badly (§6). A failure mode shared between model-authored and human-authored circuits would be far
    more interesting than either succeeding.

### 5.E — Reskin and contamination playtests

**What it tests.** Rename every entity, scramble thematic vocabulary, permute strategically
irrelevant constants, preserve mechanics exactly. A circuit or model whose performance moves was
reading the surface.

Our circuits are *architecturally* immune — they see only a compiled table — and we test it anyway,
because there is one channel the architecture does not close: **argmax tie-breaking** leaks option
enumeration order into any circuit facing a tie.

**Open questions.**

17. For a **model** rather than a circuit, what is the right control for "it recognised the game"?
    Asking it is worthless. Measuring degradation confounds recognition with prose quality.
18. Is a **mechanics-preserving reskin** even well defined? Renaming a die face is clearly safe;
    renaming "death rays" to a neutral token may change how a model parses a scoring constraint that
    is genuinely about a comparison between two counts.
19. What is the inverse control — **preserve the theme, break the mechanic** — and would a model's
    failure to notice be evidence of anything, given it may simply be following the prose?

### 5.F — The learning-cost playtest, which is the actual transfer experiment

**What it tests.** Everything measured so far is a *policy score*. The central question requires
**learning cost**: does prior structure make a new world cheaper to master? The previous review
sharpened our two-arm design into four:

```
Arm A   no prior library
Arm B   same number of random / exhaustively sampled circuits          (content control)
Arm C   circuits from other worlds, source->target associations permuted (structure broken)
Arm D   intact prior library plus whatever indexing LUDUS claims transfers
```

Primary currency: **exact policy evaluations to reach retention θ** in an unseen world, plus area
under the best-so-far search curve. Decisive criterion: **D must beat C.** Otherwise the library
helps only because it contains useful programs, not because anything was learned about where to look.

**Open questions.**

20. Is "evaluations to θ" the right cost currency for a search that has access to exact evaluation?
    Real learners pay for *experience*, not for oracle calls. Does using an exact evaluator as the
    cost unit measure something no learner would ever face?
21. What exactly is the "indexing structure" in Arm D? If we cannot state it as an executable object
    *before* running, Arm D is unfalsifiable and the whole design collapses to "libraries help".
22. Should θ be absolute retention, or retention relative to that world's cheap-heuristic floor? Our
    worlds differ enormously in how much headroom exists above a fitted threshold.
23. How many worlds are needed for a learning-cost result to be worth anything — and does the
    cross-world rank instability in §2 (mean tau +0.11, three of six pairs negative) mean that
    transfer between arbitrary world pairs should not be expected at all?

### 5.G — The representation test: is STOP/SELECT manufacturing our results?

**What it tests.** Our architecture asserts that every decision decomposes into SELECT then STOP. The
previous review argued this may not be a neutral factorization: an optimal selector optimises a
continuation that assumes optimal stopping, so replacing the stopper can make its selections
pathological. We measured exactly that — the same circuit scoring 0.0000 beside one partner and
1.0000 beside another in the same world.

**Design.** Compile the identical transition systems two ways: (A) the current SELECT→STOP interface;
(B) a single joint policy choosing `(option, continue/bank)` from the same state, with program
complexity matched as tightly as possible. Repeat the heterogeneity analysis.

**Open questions.**

24. If the heterogeneity changes materially under a refactor of an **equivalent MDP**, what exactly
    have we learned — that the axes are wrong, or that any factorization would show this?
25. Is there a principled way to choose a decomposition of a decision, or is every such choice a
    modelling commitment that must simply be declared and varied?
26. Are there games whose decisions **resist** any STOP/SELECT reading — and would building one be a
    legitimate admission ticket under our rule that a world must answer a specific unresolved
    question?

### 5.H — Which worlds to build next, if any

Our rule: a world earns admission only by answering a specific unresolved question, stated
prospectively. "Famous game" and "we need more auctions" are not admission questions.

**Open questions.**

27. Which of §5.A–G generates the strongest **world-admission ticket** — a sentence of the form
    "world X distinguishes H1 from H2 because property P varies while Q is held fixed"?
28. We have deliberately not built: auctions with real bidding, negotiation, hidden roles, deduction,
    or anything cooperative. Which of those attacks our current apparatus hardest rather than merely
    extending its coverage?
29. Is there a case for **abandoning exact solvability** to reach games with genuinely interesting
    structure — and if so, what would we need to establish first so that approximation noise cannot
    hide the kind of conceptual defect the exact bench has repeatedly exposed?

---

## 6. Defects we found in our own work

Listed so a reviewer does not rediscover them, and because the pattern may matter more than any one.

**Inferential**

- A 0.900 result was an artifact of uniform state sampling over-weighting near-terminal positions
  (0.412 when stratified).
- A proposed causal mechanism was refuted by its own test — predicted correlation sign was opposite.
- Two circuits were written from our own conceptual vocabulary rather than from data. One scored
  **0.2501** against a null circuit's **0.7398**. Both carry contamination flags.
- A registered kill condition was **mis-specified** (named a reversal "outside" a family; it occurred
  inside). Replaced rather than reinterpreted — registering it in advance is what made it visible.
- A rank-stability statistic computed across **partners** was used to support a claim about
  **worlds**. The cross-world statistic, computed later, says the opposite.

**Instrument**

- Measuring an axis against a **single** partner produced a column of zeros that read as a kill —
  the same mismatch already documented in our own code for the *other* axis.
- A maturity **promotion guard was a string test** and was defeated by its own first test case.
- A preregistered **decision rule short-circuits**: an early threshold check preempts the comparison
  carrying the real content. Left as written rather than fixed post hoc.
- **State weighting determines the verdict** (§3). Our first two weightings were defective in
  opposite directions.

Three of these share a shape: **a criterion written as a sequence of checks, where an early check
short-circuits a later one that carried the real content.**

**Representation / compute** (these change which worlds are tractable, so they are not mere notes)

- A redundant state counter caused a ~21× blowup.
- A "simplification" (drawing with replacement) measured **worse** than the problem it solved.
- A pinned parameter across a factorial made two circuits unidentifiable.
- Deep recursion crashed silently; piping through `tail` made the shell report exit 0.
- `lru_cache` on a hot path was a measured **regression** (4.1s → 20.1s).
- A quantity recomputed per-option instead of per-state made one run ~10¹⁰ operations.

---

## 7. Constraints a proposed playtest must live within

- **No paid model lanes.** All paid API budget is exhausted. One free inference lane exists and is
  partly retired. Cycles 002–005 cost nothing because they involve no model calls at all.
- **Single workstation.** Largest world compiles to ~3 GB and takes ~10 minutes. Anything requiring
  large-scale training is out of reach.
- **No human-play dataset**, and no rights to scrape one. Any human data must come from voluntary
  play by the operator or people who agree.
- **All named-game rules are unaudited reconstructions.** Nothing about a published game can be
  promoted past provisional until that is fixed — which is part of why §5.B is attractive.
- **One operator**, part-time, who knows some of these games well and others not at all.

---

## 8. Reproduction

Everything runs locally with no API access and no model calls.

```
python -m ludus.bench.verify           # rules-fidelity gate
python -m ludus.bench.run              # 21-world transfer matrix
python -m ludus.bench.partner_matrix   # E_ijk + exact variance decomposition
python -m ludus.bench.occupancy        # exposure vs competence separation
python -m ludus.bench.ledger           # circuit provenance
python -m ludus.bench.maturity         # maturity ladder
```

Artifacts under `ludus/atlas/`, `ludus/fossils/`, `roles/Ludus/CYCLE_00{1..5}_*.md`.

---

## 9. The single most useful thing a reviewer could do

Pick **one** playtest from §5, and either show that its design is confounded in a way we have not
seen, or replace it with a cheaper experiment that would discriminate the same hypotheses.

If forced to choose for you: **question 6** (how to compare human regret to circuit regret when the
human generates their own state distribution) is the one blocking the most downstream work, and
**question 21** (what the transferable "indexing structure" is, stated as an executable object before
running) is the one whose absence would make our central experiment unfalsifiable.

The standard we are applying: the useful outcome is not that the next playtests confirm the
architecture. It is that they force it to become more precise. The last review demoted our headline
verdict in under an hour, and that was the most valuable thing anyone has done for this project.
