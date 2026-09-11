# Ludus archaeology of the 2026-09-01 queue (2026-09-11)

Currency: 2026-09-11. Booting an old seat is an archaeological event, not
an instruction to resume its last queue (base role, seat states; D-25).
Every item the seat held when it went quiet on 2026-09-01 is classified
here against the north star (roles/base-role/NORTH_STAR.md), the World
Foundry recharter (prompts/2026-09-11_reactivation/OPERATOR_PROMPT.md),
the current ecology (Proteus V0.6 + registry, Archaeon H0-H5, Vivarium
loader, comms) and the base-role doctrine (positive + cheat controls on
every instrument, rows with verdicts, eligible count before a gate).

NOTHING HERE IS EXECUTED. Only STILL_LIVE becomes executable work;
NEEDS_REPREMISE is re-stated in BACKLOG_H0H5.md before it can; the rest
are recorded. Nothing is marked dead: PARKED and SUPERSEDED items keep
their residue navigable (the cycle records, packets and ledgers stay in
this directory and under ludus/, annotated, never rewritten).

Sources, all at 57533fa76 (origin/main at boot):
ROLE.md s10 "Next, in order"; ludus/atlas/BACKLOG.md; ROLE.md s8
retirement conditions; ludus/bench/RULES_AUDIT.md; ATLAS_OF_WORLDS.md s6
defect table; CYCLE_005_verdict_demotion.md "Consequences";
SESSION_LOG_2026-08-31_to_09-01.md; REVIEW_PACKET_4 s7 ladder.

## A. What the seat was standing on

Three world families under three DIFFERENT interfaces, none of which
talks to the others (found on this pass, not previously recorded as a
defect):

- ludus/worlds.py: LOOM, WEIR, TITHE (cycle 001; solve/optimal_actions;
  all three FAIL GATE-W1 at k=4: 0.000 / 0.012 / 0.040).
- ludus/bench/worlds.py + worlds2.py: FLIP7, INCAN_GOLD, MARTIAN_DICE,
  CANT_STOP, FOUNDRY x8, FOUNDRY-DECAY x7, LUCKY_NUMBERS, COLORETTO
  (21 worlds in transfer_matrix.json, 10 circuits; bench World interface
  with compile_world; stopping/selection axes).
- ludus/arena/worlds.py + worlds_epistemic.py: TIC_TAC_TOE, NIM, PIG,
  RPS, KUHN_POKER, BALL_UNDER_COUCH (arena interface with
  current_player() in {id, CHANCE, SIMULTANEOUS}, observation(i), replay).
- ludus/atlas_of_worlds/atlas.db: 1,338 catalogued rows, 0 IMPLEMENTED,
  0 AUDITED. The database is NOT tracked (.gitignore *.db); it lived only
  in the canonical checkout until this pass copied it to the seat
  worktree (sha256 648aef04...). Its dossiers (worlds/*.md) are tracked.

Rung counts on this day, measured, not recalled:
- W3 (rule-audited): 0 of 30 executable worlds. No rulebook has ever
  been consulted for any world in any family.
- bench verify.py, run on this pass: 4 of 21 matrix worlds
  VERIFIED-INTERNALLY; the other 17 (FOUNDRY x15, LUCKY_NUMBERS,
  COLORETTO) FAIL with "NO PER-WORLD INVARIANTS WRITTEN" -- they pass
  the universal and acyclicity checks and have never had a per-world
  invariant. The committed rules_fidelity.json (2026-08-27) covers only
  the four. r0003's PARTNER_ROBUST block was measured in FOUNDRY, an
  unverified world. Recorded as defect L-1 below.
- arena verify.py: 20/20 checks pass; test_epistemic.py: 25/25.
- Cheat controls: 0 of 4 qualification instruments (GATE-W1 depth
  profile, bench verify, arena verify, the epistemic differential
  audit) has ever run a cheat half.
  GATE-W1 has a positive half (WEIR/TITHE gaps fire at k=1) and a
  negative half (LOOM flat at every horizon); neither is a cheat.

## B. Queue items, classified

Format: item | class | why | what would have to be true to change it

### B1. ROLE.md s10 "Next, in order" (the 09-01 queue proper)

1. Hanabi as the next interface breaker | NEEDS_REPREMISE | the old
   reason ("famous cooperative game with hints") is the wrong reason.
   The right reason is the structural cell it would open: a world where
   observation(i) is not a subset of public state (every hand but your
   own), where the current observation is insufficient without history,
   and where communication is a costed action. No existing world in any
   of the three families has any of those three properties. Re-premised
   as a CELL-OPENING item, admitted only if the chopping grammar (LUDUS-
   02) names the cell first, and built as a minimal-sufficient variant
   (2 players, small deck) rather than the full published game | the
   grammar shows the cell is already occupied, or a cheaper world opens
   the same cell.
2. Cross-validate the arena against OpenSpiel | NEEDS_REPREMISE | the
   need is real (an independent oracle so the arena stops grading
   itself; base rule 2) but OpenSpiel is a name, not the property. The
   property is "an implementation not written by this seat reproduces
   the same game values". Kuhn -1/18, Nim XOR and TTT draw are already
   external theorems; the residual value of OpenSpiel is the ACTION
   ENUMERATION and the observation strings, i.e. a rule audit by a
   second implementation. Folded into the W3 item as one of two
   admissible audit instruments (published rulebook OR independent
   implementation) | Herakles's external-backend route lands an
   OpenSpiel backend, at which point it becomes cheap.
3. Fix D13 (year_created conflates setting with creation date) | PARKED
   | maintenance on a catalog field no current consumer reads; the
   operator ruled taxonomy housekeeping must not consume the seat.
   Cheap (a regex over the extract plus a NULL where ambiguous), so it
   rides along the next time the atlas classifier is touched; it is
   never a standalone item | a consumer needs oldest-N ordering.
4. Join arena to atlas (reconcile hand-declared structural vectors with
   catalogued rows) | SUPERSEDED | by the chopping grammar: once worlds
   carry a declared primitive vector, the join is the grammar applied
   to both sides and the "silent disagreement" becomes a test. Doing
   the join first would build a second vocabulary | n/a.
5. Measure classifier accuracy on a hand-labelled stratified sample |
   PARKED | the atlas is now a SOURCE of structural components, not the
   domain boundary; precision/recall of its heuristic tags matters only
   when a tag is used to select a world for building. Re-opens as a
   per-field spot check at that moment, never as a whole-catalog audit |
   the atlas becomes an input to an automated world selector.

### B2. ludus/atlas/BACKLOG.md (bench world backlog, 2026-08-27)

6. FOR SALE (SELECT axis with no STOP axis; monoculture breaker) |
   NEEDS_REPREMISE | still the right question (is SELECT-circuit
   ordering genre-mediated?) but the registered prediction is about
   r0012/r0011, both blocked at IDENTIFIABLE with contamination flags.
   Re-premise as a world-family question: generate the SELECT-only
   variant from bench primitives rather than reconstruct a named game
   whose rules cannot be audited | the grammar can express "SELECT
   without STOP"; then it is a generated variant, not a new world.
7. COLORETTO (STOP-with-decay vs STOP-with-ruin) | TRANSFERRED to the
   FOUNDRY-DECAY family | COLORETTO was built (worlds2.py) but has no
   per-world invariants; the interface-splitting question it was meant
   to ask is answered more cleanly by FOUNDRY-DECAY's decay parameter
   (0.25/0.5/0.75), which is a generated family with a control knob.
   The named game stays in the registry as a reconstructed world | n/a.
8. PIRATEN KAPERN (fifth push-your-luck world) | RETIRED as a build
   item; residue stays (charter v2 s17 nomination) | its own backlog
   entry said "lower information gain"; the family is characterised;
   the north star says reproducing a named artifact is calibration, not
   the goal | a rule audit of the four existing push-your-luck worlds
   passes and a fifth is needed for a preregistered family claim.
9. CAN'T STOP full game (race to three columns) | PARKED | tests whether
   the solitaire scope cut is load-bearing; real but second-order until
   any Can't Stop rule is audited (W3), because a claim about the real
   game's objective needs the real game's rules | CANT_STOP passes W3.
10. SPLENDOR (engine building) | PARKED | a genre label, not a cell; the
    grammar decides whether "compounding long-horizon SELECT" is an
    unoccupied cell before any named game is reconstructed for it |
    the grammar names the cell empty.

### B3. ROLE.md s8 retirement conditions and s7 authorisation

11. Retirement condition "GATE-W1 admits no world any affordable agent
    can reach R2 in" | NEEDS_REPREMISE | still a real emptiness test,
    but under "nothing is marked dead prematurely" it is a DORMANT-
    instrument observation, not a seat-retirement trigger; and the
    band it names is now measured per organism population (Proteus
    specimens, cheap baselines), not per LLM | restated in CHARTER_v3
    s6 as a reported observation.
12. Retirement condition "A1's in-context meter shows no cost variation
    across three world pairs" | SUPERSEDED | the A1 meter was the LLM
    in-context route; the program has no LLM in the tick path and the
    transfer question is now H4's (adaptive challenges and transfer
    improve independently evaluated competence) with organisms, not
    prompts | n/a.
13. Retirement condition "the A4 counterparty is never assigned" |
    RETIRED | A4 was retired by the 08-26 grant; the structural
    replacement (fitted baselines, full matrix, losses at the same
    resolution as wins) stands and now has a base-role name: rows with
    verdicts, cheat controls | n/a.
14. "Hourly looping in 48-hour blocks" (s7.4) | PARKED | no loop exists
    (the 30-minute atlas cron 503c90b4 was cancelled 2026-09-01); base
    rule 8 forbids a loop without a domain-level productivity signal.
    A Ludus loop is re-created only when it has a named input (a world
    queue) and writes last_input_at / last_success_at | a world queue
    exists (LUDUS-06).

### B4. ludus/bench/RULES_AUDIT.md (the HITL sheet, 17 lines)

15. Priority-1 constants (Martian Dice die faces, ray>=tank rule,
    scoring; Flip 7 deck composition and the 7-distinct bonus) |
    STILL_LIVE, re-scoped | these are exactly the W3 debt the operator
    named. The instrument changes: instead of waiting for the operator
    to tick boxes, the seat fetches the published rules (or an
    independent implementation) and records the audit with source
    provenance; the operator's tick becomes a spot check. First target
    is the world whose ONE constant carries the most published weight
    (Martian Dice's doubled ray face carries cycle 002's 86% SELECT-axis
    result) | none; this is LUDUS-01.
16. Priority-2 rules (12 lines) | STILL_LIVE, ride with 15 | same
    instrument, same commit | none.
17. Priority-3 scope cuts (Flip 7 action cards; all four solitaire;
    Can't Stop single turn; banked-progress metric) | PARKED as scope
    statements; they are not audit items | a claim about the full game
    is promoted.

### B5. ATLAS_OF_WORLDS.md s6 defects and the atlas crawler

18. D13 year_created | PARKED (see item 3).
19. The two unfixed defects of thirteen (source ceiling; classifier
    method ladder on secondary write paths) | PARKED | catalog quality
    items with no consumer | a consumer reads those fields.
20. Restart the crawler when a structural cell is empty | NEEDS_REPREMISE
    | "structural cell" now means a cell of the chopping grammar, not
    of the eight-field declared vector; the crawler is the breadth
    instrument for finding candidate components, and is restarted with
    a named target cell, never on a schedule | LUDUS-02 names an empty
    cell the atlas could fill.
21. atlas.db home (untracked 11 MB SQLite in WAL mode; side files left
    in the canonical checkout on 2026-09-01) | STILL_LIVE, done on this
    pass for the residue (0-byte WAL and 32 KB SHM deleted from the
    canonical checkout, integrity_check ok on a copy, 1,338 worlds
    intact; atlas.db-wal / atlas.db-shm ignored under
    ludus/atlas_of_worlds/.gitignore); the HOME question is open as an
    XL row (LUDUS-30) | operator decision on tracked-binary vs data
    area.

### B6. CYCLE_005 consequences

22. "r_i(W) is NOT built" and "the world-property registry is deferred"
    | NEEDS_REPREMISE | the deferral was right for the reason given (an
    artifact was being explained away). The World Foundry's world-
    primitive vector is NOT that registry: it is a declared, testable
    decomposition of the world, not a fitted per-circuit property. The
    difference is stated in CHARTER_v3 s4 so the old reason cannot be
    used against the new object | n/a.
23. "Reference-weighted conditional regret is primary; on-policy
    retention is secondary" | STILL_LIVE as a standing rule of the
    matrix | it is the selectivity-profile statistic the operator's
    "what does W discriminate" question needs | none.
24. "The review's four-arm learning-cost design is adopted" | PARKED |
    a learning-cost design presupposes a learner; the program's
    learners are Proteus populations under Archaeon/Vivarium selection,
    and H4 owns that question. Ludus's part is the world family and its
    qualification, not the arm design | H4 alpha starts and names its
    world family.

### B7. Session log items (09-01) not elsewhere

25. Multi-language Wikipedia fallback (rejected) | RETIRED | measured
    and rejected on 09-01; residue in the session log | n/a.
26. BoardGameGeek source (401 on every endpoint) | PARKED | needs
    credentials; no consumer | a component search needs BGG-only fields.
27. Replay.redacted_for(player) leak handling (one standing leak: the
    omniscient replay names chance outcomes) | STILL_LIVE, folded into
    the epistemic cheat control (LUDUS-04) | none.

## C. Defects found on this pass (not in any prior record)

- L-1. Seventeen of 21 transfer-matrix worlds have never passed bench
  verify.py (no per-world invariants); the committed fidelity ledger
  silently covers four. A committed-unrun instrument on new specimens
  (feedback_frozen_instrument_is_not_validated, Hephaestus 09-11, same
  shape). Consequence: r0003's PARTNER_ROBUST block and the whole
  FOUNDRY column carry an "unverified world" caveat until invariants
  exist. Backlog LUDUS-05.
- L-2. Three world interfaces in one seat (s A). The World Foundry
  needs one; which one survives is decided by the chopping grammar,
  not by seniority. Backlog LUDUS-03.
- L-3. The 09-01 arena mandate (the W0-W8 ladder's level names) was
  never committed verbatim; only REVIEW_PACKET_4 s7 quotes the level
  labels. The standing rule (significant prompts committed verbatim +
  hashed) was broken on 09-01. The labels recoverable from the packet:
  W3 RULE-AUDITED, W5 runs, W6 verified against external ground truth,
  W8 EXPERIMENT-READY. CHARTER_v3 s5 restates the ladder in full so it
  has a committed definition.
- L-4. No Ludus row existed in roles/base-role/MONITORS.md; the seat
  had no standing loop, so this is a missing "none" row, added on this
  pass.
- L-5. Ludus's 09-01 session worked in the canonical checkout (the
  session log records other seats committing onto its branch mid-
  session). Every prior Ludus SHA is valid; the working practice was
  the D-23 violation the missive describes.
