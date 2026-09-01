# LUDUS — External Review Packet

**Date:** 2026-08-27 · **Prepared for:** external technical review · **Status of the work:** four
completed cycles, one issued verdict, several self-diagnosed defects

This is a technical brief, engineer-to-engineer. It is not a publication and nothing here is
intended for one. It exists so that a reviewer with no prior context can give useful, specific
methodological advice.

---

## 0. What kind of review is wanted

**Wanted:** attacks on method, measurement, identifiability, and inference. Places where a
conclusion outruns its evidence. Alternative explanations for the results in §5. Defects in the
instruments described in §4 and §7.

**Explicitly NOT wanted, and actively harmful here:** suggestions about which *strategic concepts*
we should be looking for. Do not propose that we investigate tempo, optionality, initiative,
engine-building, threat, trajectory-shaping, risk aversion, or similar. The single largest risk to
this project is contaminating it with our own vocabulary — see §6, where the seat did exactly that
and it is on the record. If a concept must be mentioned, frame it as a hypothesis to be attacked
with a stated kill condition, not as a thing to go find.

Also unhelpful: agreement. Convergence between language models on a critique is corpus gravity, not
validation. If the work looks sound, the useful contribution is the sharpest available alternative
explanation for §5's results, not endorsement.

---

## 1. The program and the seat

**Prometheus** is a long-running research program asking whether failure, representation, and search
state can be turned into structure that makes subsequent reasoning cheaper. **LUDUS** is one seat
within it, authorised for 12 months of independent operation.

LUDUS's premise: a well-specified game is a bounded artificial world with enumerable physics —
entities, state, legal transformations, scarcity, uncertainty, irreversible commitments, and a
measurable outcome. Thousands of independently designed games therefore form an accidental
laboratory for asking whether competence in one world makes another world cheaper to master.

**The central question, unchanged across all cycles:**

> Does solving one strategic world leave behind executable structure that reduces the cost of
> mastering a *different* one — and if so, what exactly is that structure a property of?

The default alternative hypothesis is always that any apparent transfer is memorisation, surface
similarity, shared vocabulary, or an artifact of how the benchmark constructs its counterfactual.

---

## 2. Scope and honest limits, stated up front

These bound everything below. A reviewer should read §5 with all of them in mind.

1. **No language model is involved in cycles 002–004 at all.** Those results are dynamic-programming
   tables and hand-written policies. This removes an entire class of contamination (memorised
   strategy, game-identity leakage, benchmark overlap) but it also means **none of this is currently
   evidence about LLM reasoning**. It is evidence about whether a *representation* is coherent.
2. **All 21 worlds are solved exactly.** Backward induction over complete reachable state spaces. No
   sampling, no estimation, no standard errors — a difference of 0.0001 is real. This is deliberate:
   approximation noise would hide the conceptual defects we are hunting.
3. **All worlds are solitaire.** Opponent interaction is out of scope in this phase. For some real
   games this is severe.
4. **All real-game rules are reconstructed from memory. No rulebook was consulted.** They are marked
   `HYPOTHESIZED`. An internal gate verifies each simulator against *the rules as written down*; it
   cannot verify those rules against the published game. A world can pass every check and still model
   a game nobody plays.
5. **The worlds are small.** State counts range from 34 to ~440,000.

---

## 3. What a "world" and a "circuit" are here

**World interface.** Every world implements exactly five methods:

```
initial()          -> S            starting state of a scoring episode
draws(s)           -> [(p, draw)]  exogenous outcome (cards, dice, deck)
options(s, draw)   -> [S]          player's choices after seeing it;
                                   an EMPTY list is death - the pot is lost
pot(s)             -> float        value banked if you stop here
forced_end(s)      -> bool         no further continuation is legal
```

Two decision **axes** fall out of it:

- **SELECT** — which option to take after the draw
- **STOP** — whether to bank after taking it

Exact value:

```
V(s)  = sum_draw p * max_{s2 in options(s,draw)} W(s2)     (no options -> 0)
W(s2) = pot(s2)                  if forced_end(s2)
      = max(pot(s2), V(s2))      otherwise
```

**Circuit.** A policy written *only* against a compiled transition table. A circuit cannot read a
rulebook, name a card, or know which game it is in. That restriction is architectural: a circuit
needing game-specific knowledge is not transferable, and forbidding it at the type level means the
bench cannot accidentally credit one. Circuits carry ugly identifiers (`r0003`) permanently; English
names are conveniences attached afterwards and are never canonical.

**The organising bet, stated so it can be killed:** *transfer is mediated by interfaces, not by games
or genres.* A circuit written against an interface is transplantable by construction to any world
exposing it, so the question is never "can it transfer" but "how much value does it **retain**".

**The measured quantity:**

```
E_ijk = EV(axis A uses circuit r_i, axis B uses partner r_j, in world W_k)
        ----------------------------------------------------------------
                       EV(exact optimal play in W_k)
```

---

## 4. The instruments, and what each was built to prevent

- **GATE-W1** — a world is inadmissible at an axis if a cheap policy already solves it. Keys on the
  gap at *search depth 4*, not depth 1.
- **Fitted-per-world baseline** — a pot threshold swept per world and marked non-transferable. A
  transferable circuit must beat a baseline that was allowed to tune to each world individually.
- **Visitation weighting** — states weighted by probability under competent play, never uniformly.
  (Uniform weighting once inflated a reading from 0.412 to 0.900, and in another case disagreed with
  the correct weighting by a factor of 78.)
- **Circuit ledger** — per circuit: `invented_on`, `tuned_on`, `predicted_worlds`,
  `predicted_direction`, `kill_condition`, `first_failure`, `split_history`, `current_scope`. Worlds
  used to invent or tune a circuit are subtracted from its evidence, as are worlds that do not
  expose its axis.
- **Maturity ladder** — PROPOSED → EXECUTABLE → IDENTIFIABLE → ABLATION_SUPPORTED → CROSS_WORLD →
  PARTNER_ROBUST → COMPOSITIONAL → TRANSFER_SUPPORTED. Promotion requires typed evidence fields per
  rung; more worlds at the same evidence class is explicitly insufficient.
- **Rules-fidelity gate** — runs before any circuit touches a world; nothing in it knows what a good
  move is.
- **FOUNDRY** — a synthetic world family parameterised so exactly one property moves at a time
  (`gate`, `decoy`, `arity`, `capacity`, `p_bust`, `decay`). These are controls, never reported as
  games.

---

## 5. What has actually been measured

### Cycle 001 — three authored worlds, all inadmissible

Three worlds were authored specifically to instantiate named strategic realms (resource conversion
with irreversibility and shared-stock denial; spatial control with budgeted denial; descending-price
auction timing). A **one-ply greedy heuristic** picks an optimal action in:

```
LOOM 100.0%      WEIR 85.7%      TITHE 85.0%
```

Depth profile (gap between depth-k search and exact optimal, k = 1..4):

```
        gap(1)  gap(2)  gap(3)  gap(4)
LOOM    0.000   0.000   0.000   0.000
WEIR    0.144   0.112   0.040   0.012
TITHE   0.156   0.144   0.056   0.040
```

Four plies of trivial search essentially solves all three. **A world can instantiate a named
strategic realm completely and contain no strategic decision.**

An LLM was measured on these (`nvidia:gpt-oss-120b`, exact ground truth, n=20/cell). Legality was
saturated (1.000 in all three worlds against random floors 0.410–0.675). At the optimal-action rung
the model was **statistically identical to the four-line heuristic** (exact paired McNemar p = 0.500
and p = 1.000). Exact game-value returned 0.900 against a ~0.000 chance floor — which did not
survive stratification: 24/24 where ≤2 plies remained, **7/17 (0.412)** where 5+ remained. The
headline was a property of the sampler, not the model.

### Cycle 002 — "push your luck" is a real family and nearly empty

Flip 7 and Martian Dice, solved exactly. One untuned rule —

```
r0003:  STOP iff P(death | continue) * pot >= E[immediate gain | continue]
```

— retains **0.9991** of optimal in Flip 7. Transplanted into Martian Dice with no tuning (cards and
numbers → thirteen dice with a satisfiability constraint) it retains **0.9095**, beating every
hand-tuned threshold in the world it was not designed for.

Then an axis ablation emptied it out. Of Martian Dice's 0.0905 residual:

```
upgrading ONLY the stop rule  : -0.0005
upgrading ONLY the claim rule : +0.0777     (86% of the residual)
```

Paired with a competent claim rule, the transplanted stopper retains **0.9872**. So the shared
computation is real and transfers across a wide surface gap — and accounts for almost none of what
makes the harder world hard. **The genre label groups those games by their shared *easy* part.**

### Cycle 003 — a passed prospective prediction, and an unpredicted reversal

`r0003`'s scope prediction (≥ 0.97 with a competent SELECT partner; residual localises off the stop
axis) was registered **before Incan Gold and Can't Stop were built**. Both returned **1.0000**, and
Can't Stop's residual localised exactly as predicted (SELECT +0.0611, STOP +0.0000). It beats the
fitted-per-world baseline in all four worlds (0.9976 / 0.9223 / 0.9448 / 0.9405).

Unpredicted: **the SELECT ordering completely reverses between two worlds sharing an interface.**

```
MARTIAN_DICE  r0012 0.9656 > r0010 0.8655 > r0014 0.8004 > null 0.7398 > r0011 0.2501
CANT_STOP     r0011 0.9389 > r0014 0.9358 > r0012 0.9278 > r0010 0.8983 > null 0.7864
```

`r0011` is the worst circuit available in one world and the best in the other.

A world property was registered to explain it — `w0001`, gating fraction, the share of states whose
pot is exactly zero despite capacity already spent:

```
FLIP7 0.0002    INCAN_GOLD 0.0001    MARTIAN_DICE 0.4272    CANT_STOP 0.0000
```

(The *first* proposed mechanism was refuted by its own test: it predicted a positive
consumption/pot-gain correlation in Martian Dice and none in Can't Stop; measured −0.0623 and
+0.2390, opposite sign. `w0001` is the replacement.)

### Cycle 004 — the basis audit

Prompted by a failure: `r0003` read **0.0000** in gated worlds and in two new real worlds, which
looked like a clean kill. It was not. Same world, same circuit, different partner:

```
FOUNDRY[gate=1,k=3,cap=4]   optimal-select 0.0000   greedy-select 1.0000
LUCKY_NUMBERS               optimal-select 0.0000   greedy-select 0.6667
```

Holding the other axis at *optimal* is not a neutral control: an optimal selector maximises long-run
value and takes options with no immediate gain; `r0003` reads immediate gain and banks instantly.

The failure was frozen as a fossil before repair, then the full partner matrix was computed and
decomposed exactly (complete factorial, no fitting, no noise):

```
                            FOUNDRY (identified)    REAL WORLDS
  world                           0.3497              0.0696
  circuit x world                 0.1692              0.4374
  partner                         0.1645              0.0990
  partner x world                 0.1026              0.1416
  circuit                         0.0998              0.2126
  circuit x partner x world       0.0834              0.0277
  circuit x partner               0.0307              0.0122

  S_circuit                       0.2605              0.3082
  Kendall tau across partners     0.9721              0.9225
```

`S_circuit` = share of a circuit's own variance that is marginal rather than conditional.

**Verdict issued: `CONTEXTUAL_BASIS_REQUIRED`.** A circuit's measured value is primarily a property
of the world it is measured in. Both designs agree that `circuit × world` overwhelms
`circuit × partner` — by 5.5× and 36× respectively. The partner effect that *triggered* the audit is
the smallest term in it, and it is spatially concentrated: 12 of 21 worlds have `r0003`
partner-spread below 0.01, and adding a decoy to a gated world collapses the spread from 1.0000 to
0.0396. Partner-dependence turned out to be world-dependence wearing a partner's clothes.

Supporting checks:

- **Identifiability initially FAILED.** `r0004` and `r0007` had identical signatures across all 400
  cells, because `p_bust` was pinned at 0.25 in every factorial world so `r0007`'s threshold could
  never fire. Separating intervention found and applied (vary `p_bust`) → 5/5 distinct signatures.
- **Construct validity holds.** Recomputed under three denominators (optimal EV, best-cheap-policy,
  range-normalised): CONTEXTUAL in all three.
- **Prospective value is poor.** Leave-one-partner-out mean |error| **0.3424**; leave-one-world-out
  **0.3353**, on a 0–1 scale. The circuits do not predict their own behaviour where they were not
  constructed.
- **What survives is rank, not magnitude** (tau 0.92–0.97).

---

## 6. Defects the seat found in its own work

Listed because a reviewer should not spend time rediscovering them, and because the pattern across
them may be more informative than any single one.

**Scientific / inferential**

- A 0.900 result on exact game-value was an artifact of uniform state sampling over-weighting
  near-terminal positions (0.412 when stratified).
- A proposed causal mechanism was refuted by its own test (correlation sign was opposite).
- Two circuits (`r0011`, `r0014`) were written from the seat's own conceptual vocabulary rather than
  from data. `r0011` then scored **0.2501** against a null circuit's **0.7398** — a concept-seeded
  circuit losing badly to one that reads nothing. Both carry contamination flags.
- A registered kill condition was **mis-specified**: it named a reversal "outside push-your-luck",
  and the reversal occurred inside it. Replaced rather than reinterpreted — registering it in
  advance is what made the error visible.

**Instrument**

- Measuring an axis against a **single** partner produced a whole column of zeros that read as a
  kill. This is the same mismatch already documented in the code for the *other* axis, committed a
  second time by the seat that wrote the warning.
- The maturity **promotion guard was a string test** (`"world count" in evidence`) and was defeated
  by its own first test case — the phrase "support from 21 worlds" promoted a circuit on exactly the
  reasoning the guard exists to forbid. Replaced with typed evidence fields per rung.
- The preregistered **decision rule short-circuits**: it tests `S_circuit` first and only compares
  world-vs-partner conditionality *below* 0.30, so the real worlds (36× world-conditional) classify
  as "partner-conditional" on a 0.0082 margin. Left as written rather than fixed post hoc; the
  corrected form is registered for the next cycle before use.

Two of these three share a shape: **a criterion written as a sequence of checks, where an early check
short-circuits a later one carrying the real content.**

**Representation / compute** (these change which worlds are tractable, so they are not mere
implementation notes)

- A redundant state counter caused a ~21× state blowup.
- A "simplification" (drawing with replacement) was measured **worse** than the problem it solved.
- `p_bust` pinned across a factorial made two circuits unidentifiable.
- Deep recursion crashed silently; piping through `tail` made the shell report exit 0, so a crash
  read as success.
- `lru_cache` on a hot path was measured as a **regression** (4.1s → 20.1s).
- A quantity recomputed per-option instead of per-state made one run ~10¹⁰ operations.

---

## 7. Where review would be most valuable

1. **Is the variance decomposition the right instrument for this question?** It is exact over a
   complete factorial, but it presumes the effects are meaningfully additive-plus-interaction. Is
   there a better way to ask "what is this measurement a property of"?
2. **Is `E_ijk` the right measured quantity at all?** It is a ratio to exact optimal. Three
   denominators were tried and agreed, but all three are normalisations of the same underlying EV.
   Is there a construction that would fail differently?
3. **Is the interface abstraction (STOP / SELECT) doing real work, or is it imposing a decomposition
   the worlds do not have?** The bench found `circuit × world` dominant; one reading is that the
   axes are the wrong cut.
4. **Does the synthetic/real split hold up?** FOUNDRY controls isolate properties by construction,
   but a control family that mostly talks to itself may calibrate an instrument that measures
   nothing. The real worlds agreed on substance and disagreed on label (§5). How much weight should
   the synthetic block carry?
5. **The largest acknowledged gap:** every number is a *policy score*. Nothing yet measures
   **learning cost** — the actual transfer claim requires showing prior structure makes a new world
   cheaper to master, not that a fixed policy scores better. Proposed measurable form: number of
   exact policy evaluations to reach retention θ in an unseen world, searching over circuit
   compositions, seeded library vs shuffled control. Is that a sound operationalisation?
6. **Given `CONTEXTUAL_BASIS_REQUIRED`, what is the right representation?** The seat's reading is
   that the data demands circuits indexed by *world properties* — `r_i(W)` — and that
   `circuit × partner` at 0.0122–0.0307 is too small to justify a relational or hypergraph basis.
   Is that the right inference, or is it under-reading the 0.0834 three-way term?
7. **Is the world-property vocabulary (`w0001` gating, decoy, `p_bust`) the right next object**, or
   is that just relocating the same contamination risk from circuits to properties?

---

## 8. Reproduction

Everything runs locally with no API access and no model calls.

```
python -m ludus.bench.verify           # rules-fidelity gate
python -m ludus.bench.run              # 21-world transfer matrix
python -m ludus.bench.partner_matrix   # cycle 004 E_ijk + exact decomposition
python -m ludus.bench.ledger           # circuit provenance ledger
python -m ludus.bench.maturity         # maturity ladder
```

Artifacts: `ludus/atlas/*.json`, `ludus/fossils/FOSSIL_r0003_2026-08-27.json`,
`roles/Ludus/CYCLE_00{1,2,3,4}_*.md`, `roles/Ludus/GUARDRAILS.md`.

## 9. The standard being applied

> The best outcome is not that the next worlds confirm the architecture. It is that they force the
> architecture to become more precise.

A reviewer who can show that §5's verdict is wrong, under-determined, or measuring an artifact would
be delivering the most valuable possible contribution.
