# RULES AUDIT — the HITL sheet

> ANNOTATION 2026-09-16 (LUDUS-01, Ludus[m2-c3a5ef7a]). The first published
> source has been consulted: the Tasty Minstrel Games Martian Dice rule sheet
> ((c) 2011; sha256 cc8297f2...; `ludus/bench/rules_audit.json` quotes the
> sentence behind every Martian Dice line). The seat marked the lines below
> under P3 (seat-performed audit, operator spot check); LUDUS-31 asks whether
> that counts for W3. Result: 0 constants moved, 2 RULES moved (MD-5 below),
> and the world, its per-world invariants and its matrix column were
> re-solved: 8,555 -> 14,653 states, optimal EV 2.093806 -> 3.110382, and the
> axis decomposition REVERSED (SELECT +0.0216/STOP +0.0091 of 0.0344 on the
> reconstruction; SELECT -0.0005/STOP +0.0486 of 0.0627 on the published
> rules). The old column is kept as MARTIAN_DICE_RECON_2026-08-27. Nothing
> below is edited; marks are added in brackets.
>
> ANNOTATION 2026-09-16 (LUDUS-15). Flip 7, Incan Gold and Can't Stop audited
> against publisher sources the same day: Flip 7 COMPLETE (0 moved); Incan Gold
> PARTIAL (IG-2 treasure values UNSURE); Can't Stop PARTIAL (CS-1 heights UNSURE;
> CS-3 wording corrected, code right). W3 under P3: 2 of 30 complete, 2 partial.

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

- [x] **MARTIAN DICE — each die has faces: tank, ray, ray, human, cow, chicken.** [OK 2026-09-16, MD-1: sheet COMPONENTS "1 Tank, 2 Death Rays, 1 Human, 1 Cow, and 1 Chicken"]
  The *doubled ray face* is the single highest-leverage constant in the bench. It sets how often the
  ray-vs-tank constraint binds, which is the mechanism cycle 002 credited with putting 86% of the
  world's difficulty on the SELECT axis. If rays are a single face, that result moves.
- [x] **MARTIAN DICE — scoring requires rays >= tanks, else the turn scores zero.** [OK 2026-09-16, MD-2]
- [x] **MARTIAN DICE — score is humans + cows + chickens, plus 3 for holding at least one of each.** [OK 2026-09-16, MD-3]
- [x] **FLIP 7 — rank r appears r times in the deck; rank 0 appears once (79 number cards).** [OK 2026-09-16, F7-1: The Op ruleset 3.1 "twelve 12's, eleven 11's, ten 10's... until you get to one 1; there is even one 0"]
- [x] **FLIP 7 — collecting 7 distinct ranks scores +15 and ends your round immediately.** [OK 2026-09-16, F7-2]

## Priority 2 — rules that shape the decision, not just the score

- [x] **MARTIAN DICE** — all tanks rolled are set aside compulsorily. [OK 2026-09-16, MD-4]
- [x] **MARTIAN DICE** — you must then claim *all* dice of exactly one symbol you have not claimed
  before this turn; if you cannot, the turn ends scoring zero. [WRONG 2026-09-16, MD-5: Death Rays
  "may always be chosen" (repeatable within a turn); an unclaimable roll ends the turn "proceed to
  Scoring", i.e. it SCORES, it is not a bust. Both fixed in `worlds.py`; the reconstruction is kept as
  `MartianDiceRecon`.]
- [x] **MARTIAN DICE** — after claiming you may stop or reroll the remaining dice. [OK 2026-09-16, MD-6]
- [x] **FLIP 7** — flipping a rank you already hold busts you; the round scores zero. [OK 2026-09-16, F7-3]
- [x] **INCAN GOLD** — five hazard types, three copies of each; the *second* revealed copy of a type
  ends the round and everyone still in loses their unbanked take. [OK 2026-09-16, IG-1: Eagle-Gryphon rulebooks 2018 ed. and 2023 v7]
- [ ] **INCAN GOLD** — treasure card values are `1 2 3 4 5 5 7 7 9 11 11 13 14 15 17` (15 cards). [UNSURE 2026-09-16, IG-2: the publisher confirms 15 cards and prints no values; BGA lists 14 values without the 17; a reimplementation lists all 15. Needs a components list or card images.]
- [ ] **CAN'T STOP** — column heights are `2:3 3:5 4:7 5:9 6:11 7:13 8:11 9:9 10:7 11:5 12:3`. [UNSURE 2026-09-16, CS-1: the 2021 rulesheet says only "a varying number of squares"; Wikipedia gives exactly these. Needs a board image.]
- [x] **CAN'T STOP** — three runners; a roll of 4d6 is split into two pairs; you must use both sums
  if any pairing allows it, otherwise one, otherwise you bust and lose the turn's progress. [OK IN CODE 2026-09-16, CS-2/CS-3; THIS SENTENCE was stricter than the rule: the obligation is per CHOSEN pairing ("a player may deliberately form the two dice pairs so that they are able to introduce or move only one runner"), which is what `options()` implements.]

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
