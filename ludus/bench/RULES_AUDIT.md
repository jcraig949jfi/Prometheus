# RULES AUDIT — the HITL sheet

**What this is.** Every world in the bench is reconstructed from memory. **No rulebook has been
consulted for any of them.** Under charter v1 §8's epistemic states every rule below is
`HYPOTHESIZED`. Charter v2 §4 names the operator as the instrument for exactly this: fabricated
rules, impossible moves and missing mechanics are cheap for someone who knows the game to spot, and
expensive for a simulator to notice.

**What it blocks and what it doesn't.** A failed audit does not invalidate the bench's *machinery* —
the solver, the circuits and the transfer matrix are game-agnostic and would be re-run in minutes
against corrected rules. It invalidates any **claim about a named commercial game**. So: the audit
gates *promotion* of a verdict, never the running of the bench.

**How to use it.** For each line, mark `OK`, `WRONG: <what it should be>`, or `UNSURE`. Anything
marked wrong gets fixed and the affected worlds re-solved; the matrix rebuild is automatic.

---

## Priority 1 — constants that carry a published result

These are load-bearing. If one is wrong, a stated finding moves.

- [ ] **MARTIAN DICE — each die has faces: tank, ray, ray, human, cow, chicken.**
  The *doubled ray face* is the single highest-leverage constant in the bench. It sets how often the
  ray-vs-tank constraint binds, which is the mechanism cycle 002 credited with putting 86% of the
  world's difficulty on the SELECT axis. If rays are a single face, that result moves.
- [ ] **MARTIAN DICE — scoring requires rays >= tanks, else the turn scores zero.**
- [ ] **MARTIAN DICE — score is humans + cows + chickens, plus 3 for holding at least one of each.**
- [ ] **FLIP 7 — rank r appears r times in the deck; rank 0 appears once (79 number cards).**
- [ ] **FLIP 7 — collecting 7 distinct ranks scores +15 and ends your round immediately.**

## Priority 2 — rules that shape the decision, not just the score

- [ ] **MARTIAN DICE** — all tanks rolled are set aside compulsorily.
- [ ] **MARTIAN DICE** — you must then claim *all* dice of exactly one symbol you have not claimed
  before this turn; if you cannot, the turn ends scoring zero.
- [ ] **MARTIAN DICE** — after claiming you may stop or reroll the remaining dice.
- [ ] **FLIP 7** — flipping a rank you already hold busts you; the round scores zero.
- [ ] **INCAN GOLD** — five hazard types, three copies of each; the *second* revealed copy of a type
  ends the round and everyone still in loses their unbanked take.
- [ ] **INCAN GOLD** — treasure card values are `1 2 3 4 5 5 7 7 9 11 11 13 14 15 17` (15 cards).
- [ ] **CAN'T STOP** — column heights are `2:3 3:5 4:7 5:9 6:11 7:13 8:11 9:9 10:7 11:5 12:3`.
- [ ] **CAN'T STOP** — three runners; a roll of 4d6 is split into two pairs; you must use both sums
  if any pairing allows it, otherwise one, otherwise you bust and lose the turn's progress.

## Priority 3 — deliberate scope cuts (NOT rule claims)

Listed so they are never mistaken for errors. Each is a stated limitation.

- **FLIP 7** — action cards (Freeze, Flip Three, Second Chance) and modifier cards
  (+2/+4/+6/+8/+10/x2) are **not implemented**. Number-card core only.
- **ALL FOUR WORLDS ARE SOLITAIRE.** Opponent interaction is out of scope for this cut. For Incan
  Gold this is severe: the entire character of the real game is that other players leaving changes
  your split and leaves treasure on the path. The solitaire version is a strictly easier world and
  is labelled as such wherever it is reported.
- **CAN'T STOP** — a single turn from an empty board, not a full game to three claimed columns.
- **CAN'T STOP** — banked progress is valued as the sum of fraction-of-column-completed. This is a
  **modelling choice, not a rule**: counting raw steps would undervalue the short outer columns
  (three steps claims column 2, thirteen claims column 7) and would bias every stopping circuit
  toward the middle of the board for a reason that is an artefact of the metric.

## Not yet built

- **PIRATEN KAPERN** — the fifth world charter v2 §17 nominates. Not implemented.
- Everything else in charter v2 §3's founding corpus.
