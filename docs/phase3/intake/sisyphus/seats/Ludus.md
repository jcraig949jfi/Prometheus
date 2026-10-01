# Ludus -- forensic dossier

Seat: Ludus (games-as-worlds bench; recharted 2026-09-11 as the World Foundry)
Crawl date: 2026-10-01
Base SHA of worktree: 19299e06b (origin/main at crawl)
Crawler: Sisyphus worker (Opus 5.5), read-only

Coverage statement.
READ: roles/Ludus/ROLE.md (sections 0-10, including the four v1 amendments A1-A4 and the
reconciliation against v2), CHARTER_v1.md (s0), CHARTER.md v2 (s0-2), CHARTER_v3_WORLD_FOUNDRY.md
(complete), STATUS.md (complete), ARCHAEOLOGY_2026-09-11.md (sections A, B1, B2 head), CYCLE_001
(s1-2.25), CYCLE_002 (annotation, s1-3), CYCLE_004_VERDICT (head), CYCLE_005 (head), REVIEW_PACKET
2026-08-27 (cycle 003 section), REVIEW_PACKET_4 (arena, s1-2 head), REVIEW_PACKET_8 (head),
GUARDRAILS.md (cycle-003 robustness lines), BACKLOG_H0H5.md (grep for status and the binding/foundry
rows), the reactivation OPERATOR_PROMPT.md (head); code ludus/bench/core.py (docstring + World),
ludus/bench/circuits.py (r0003-r0005), ludus/arena/core.py (docstring), ludus/controls/
CONTROLS_2026-09-16.json (25 rows); git log of ludus/ and roles/Ludus (14 commits, all refs);
comms listing for Ludus and bodies #46, #886; Achilles census rows for Ludus; Atlas harvest grep
(Ludus is listed as NOT COVERED).
NOT READ: CHARTER.md v2 sections 3-46 in full; CYCLE_004_PREREG; REVIEW_PACKET_2, _3, _5, _6, _7 in
full; SESSION_LOG; ATLAS_OF_WORLDS.md in full; CROSSWALK_INTAKE; ludus/atlas_of_worlds code bodies;
716 world dossiers under ludus/atlas_of_worlds/worlds/ (sampled names only); ludus/worlds.py,
stopworlds.py, bench/worlds*.py bodies; journals 2026-09-11 and 2026-09-16; ludus/docs strategic
roadmap. Reason: budget; headline numbers are taken from the cycle documents and packets and tagged
as reported results. The untracked atlas.db / Postgres ludus_atlas store was not opened.

-------------------------------------------------------------------------------------------------
## 1. Identity and purpose

Canonical name: LUDUS / Ludus ("the Roman word that means both the game and the training school",
ROLE.md header). Instance tag Ludus[m2-c3a5ef7a] (2026-09-16) [HIST]. Census aliases: the role-doc
pair CHARTER.md (v2) / CHARTER_v1.md (Achilles census seats registry) [HIST].

Charter lineage -- the v1 -> v2 -> ROLE v3 -> CHARTER_v3 pivots [HIST, from file provenance lines]:

- v1 (2026-08-26) CHARTER_v1.md, "Cartographer of Games, Strategic Worlds, and Transferable
  Reasoning", status "Proposed Prometheus agent role". Mission: "Build an executable atlas of games
  as reasoning environments, discover recurring strategic structures across superficially different
  worlds, and design falsifiable experiments testing whether competence acquired in one world
  transfers to another." Governing question: "When a system becomes competent in one world, what --
  if anything -- has it acquired that makes mastery of another world cheaper?" [INTENT]
- v2 (same day, 2026-08-26) CHARTER.md, "Long-Horizon Program Charter: Games as a Laboratory for
  Transferable Synthetic Reasoning", multi-year, "Atlas of Strategic Worlds"; founding corpus of 30-50
  named games (s3/s37); synthetic skill gradients from constructed policy ladders (s26); cheating
  assumption (s35); "no noun without a test" (s5); active selection by information gain (s41); daily
  questions (s46) [INTENT].
- ROLE.md "v3, 2026-08-26" (seat document, not a charter): authorised by James "for 12 months, no
  counterparty required (retiring A4), and hourly looping in 48-hour blocks". Section 0 records the
  operator's correction of the WORK SHAPE: "You don't simply run an experiment and issue a kill
  claim. You run a research bench running thousands or even millions of simulated boardgames ...
  hammer those strategies into repeatable reasoning circuits." -> the bench of three ever-growing
  registries (world registry, circuit registry, transfer matrix), with the bet "transfer is mediated
  by interfaces, not by games or genres" [INTENT/HIST].
  The four seat amendments to v1 and their fates (ROLE s3): A1 (C(G,theta) unmeasurable; LLM
  in-context meter) RETIRED by v2 s26; A2 (author small worlds, not 30-50 real games) RETIRED and
  "refuted by my own data" (cycle 001); A3 (strategic realm labels are not evidence) SURVIVES; A4 (no
  self-adjudication of transfer) RETIRED by explicit grant [HIST].
- 2026-09-01 library mandate (ROLE s10): "keep building this library of games out. Breadth and
  depthwise, and making it robust for computational accessibility" -> Atlas of Game Worlds (breadth)
  and the arena (depth/accessibility) [HIST].
- 2026-09-01 .. 09-11: seat quiet (ARCHAEOLOGY: "went quiet on 2026-09-01") [HIST].
- CHARTER_v3_WORLD_FOUNDRY.md (2026-09-11), from operator reactivation prompt (roles/Ludus/prompts/
  2026-09-11_reactivation/OPERATOR_PROMPT.md, sha256 793b3d57...): "Ludus is the World Foundry ...
  create, acquire, mutate, validate, classify and maintain computational environments whose fitness
  landscapes exert known and measurable pressures on candidate organisms and circuits. Proteus
  supplies players ... Ludus supplies worlds; Archaeon and Vivarium compose". The constitutional
  question is generalised to five questions (what is rewarded; what cheaper mechanism obtains it;
  under what perturbation the equivalence breaks; which parameters control pressure; can they be
  searched). A world may be any environment or GENERATOR; "the 1,338-game atlas is one source of
  structural components, not the boundary of the domain" [INTENT]. Superseded: ROLE s3 A1 LLM meter
  ("no LLM in the tick path"), s7.4 hourly looping (PARKED), s8 retirement conditions (restated as
  P4), s10 queue, v2 s3/s37 founding corpus [HIST].

Why the pivots happened [HIST]: (1) cycle 001 showed authored "strategic" worlds were greedy-decidable
(A2 refuted) and the LLM-in-the-loop path was dominated by harness defects; (2) cycle 002 showed exact
DP over small stochastic worlds made transfer measurement free of LLMs; (3) the operator rejected the
"one kill per cycle" shape in favour of a standing bench; (4) by 2026-09-11 the program's centre of
gravity had moved to organism ecology (Proteus/Archaeon/Vivarium), so Ludus was re-premised as the
world supplier for evolutionary experiments.

Current/terminal role: STATUS.md (currency 2026-09-16) says "seat state: ACTIVE (World Foundry)" [HIST].
Last commit on ludus/ or roles/Ludus: fb858dd5c, 2026-09-16 [IMPL]. Census engine state DORMANT
(derived) [HIST]. Comms after 09-16 addressed to Ludus: Aporia #547 (UNIQUE(slug) applied, 09-23),
Artemis #886 (worker findings, 09-28); no Ludus reply [HIST]. Effective status: DORMANT, still
self-declared ACTIVE -- a currency gap.

Relationships [HIST]: Charon/Elenchus/Harmonia/Diomedes (audit altitudes; ROLE s2); AMA/ama_game
arena (the "one world" precedent; ROLE A1 adopted its metered interface before v3); Proteus (organism
supplier; Ludus to write the world-side binding, LUDUS-06, never written); Archaeon (H4 lane
consumer; LUDUS-24 coupling spec never posted); Vivarium (executor; never consumed a Ludus world);
Hephaestus, Herakles (component and external-backend routes); Aporia (moved atlas.db to Postgres
schema ludus_atlas, #299). No code outside ludus/ imports ludus [IMPL: git grep 'from ludus|import
ludus' outside ludus/ returns only two Ludus role docs].

Hosts: M1 (Skullport, F:\) through 2026-09-11 (ROLE header; adoption worktree); M2 from 2026-09-16
(STATUS: worktree ludus-boot-2026-09-16) [HIST]. Atlas canonical store on M1 Postgres [HIST].

-------------------------------------------------------------------------------------------------
## 2. Engine / system inventory

Three world families under three different interfaces, none of which talks to the others
(ARCHAEOLOGY s A, "found on this pass, not previously recorded as a defect") [HIST, consistent with
code layout IMPL].

E1. Cycle-001 authored worlds + baselines (2026-08-26) [IMPL]
- ludus/worlds.py (LOOM resource economy, WEIR spatial control, TITHE temporal/auction; 2-player,
  deterministic, perfect-information, exact minimax), ludus/baselines.py (r0001 greedy-decidability
  gap), ludus/depth_profile.py (r0002 gap(k)), ludus/r0001_sweep.py, ludus/ceiling1.py (LLM harness,
  pinned nvidia:gpt-oss-120b after the free 49B lane returned HTTP 410), ludus/report.py; ledgers
  ludus/ledgers/cycle001_*.

E2. Stochastic-stopping family (cycle 002) [IMPL]
- ludus/stopworlds.py (Flip 7 number-card core, Martian Dice reconstruction; solitaire), ludus/
  stopgate.py; ledgers cycle002_*. Exact DP (Flip 7 8,192 reachable states; Martian Dice 6,176).

E3. The bench (cycles 003-005) [IMPL]
- ludus/bench/core.py (World interface: initial, draws, options, pot, forced_end; exact V/W recursion;
  SELECT and STOP axes), worlds.py + worlds2.py (FLIP7, INCAN_GOLD, MARTIAN_DICE, CANT_STOP,
  FOUNDRY x8, FOUNDRY-DECAY x7, LUCKY_NUMBERS, COLORETTO, MartianDiceRecon), circuits.py (circuit
  registry, e.g. r0003 myopic stopper, r0004/r0005 floors, r0010-r0014 selectors), compiled.py
  (compile_world exact), partner_matrix.py, occupancy.py, maturity.py, ledger.py, loop.py, run.py,
  verify.py (bench verify; universal + acyclicity + per-world invariants), audit.py, rules_audit.json
  + RULES_AUDIT.md.
- Durable artifacts: ludus/atlas/transfer_matrix.json (21 worlds x 10 circuits, per ARCHAEOLOGY),
  circuit_ledger, circuit_maturity (ladder up to PARTNER_ROBUST), cycle004_partner_matrix,
  cycle004_identified_design, cycle005_occupancy, rules_fidelity.json; fossil ludus/fossils/
  FOSSIL_r0003_2026-08-27.json.

E4. The arena (2026-09-01) [IMPL]
- ludus/arena/core.py (World/State/Player separation; current_player in {id, CHANCE, SIMULTANEOUS};
  deterministic replay; "A World cannot call a Player"), worlds.py (TIC_TAC_TOE, NIM, PIG, RPS,
  KUHN_POKER), worlds_epistemic.py + epistemic.py (ontic vs observation; BALL_UNDER_COUCH synthetic
  epistemic laboratory), players.py, verify.py (20 checks), audit.py (differential leak audit),
  test_epistemic.py (25 tests). 1,218 lines at packet 4.

E5. Atlas of Game Worlds (breadth) [IMPL]
- ludus/atlas_of_worlds/ (crawl.py, wikidata.py, wikipedia.py, seeds.py, classify.py, taxonomy.py,
  coherence.py, deepen.py, store.py, report.py, from_postgres.py) + 716 tracked dossiers worlds/*.md.
- Catalogue 1,188 games at 09-01 (662 with generated dossier/state diagram/simulated trace), 1,338 at
  09-11; store atlas.db NOT tracked (.gitignore *.db), moved to canonical Postgres schema ludus_atlas
  on M1 (5,774 rows across tables; 1,338 worlds) on 2026-09-16 [HIST: #299/#300/#547].
- Every row 0 IMPLEMENTED, 0 AUDITED (ARCHAEOLOGY s A) [HIST].

E6. Qualification controls (2026-09-16) [IMPL]
- ludus/controls/{fixtures.py, run_controls.py, CONTROLS_2026-09-16.json (25 rows)}: control halves for
  the depth profile, bench verify, arena key-name check, arena differential audit.

E7. Scaffolding / not built [IMPL: absent]: chopping grammar v0 (LUDUS-02), Proteus binding (LUDUS-06),
World Foundry vertical slice with mutate/distance/admission (LUDUS-05), world_ref identity (LUDUS-14),
interface unification (LUDUS-07), held-out evaluator for coevolution (LUDUS-23), Hanabi-minimal,
cart-pole, grid world with learnability regions.

Scale: ludus/ 799 tracked files (716 are atlas dossiers); ~12,300 lines of Python [IMPL wc].
Everything single-machine, standard library, CPU, exact.

-------------------------------------------------------------------------------------------------
## 3. Architecture

What constitutes a world (three definitions) [IMPL]:
- Cycle-001: 2-player alternating deterministic game with solve()/optimal_actions(), scored by
  exact minimax.
- Bench: a single-agent stochastic stopping/selection process: initial(); draws(s) -> [(p, draw)];
  options(s, draw) -> successor states (empty = death, pot lost); pot(s) banked value; forced_end(s).
  Exact value V(s) = sum_draw p * max_options W(s2); W(s2) = pot or max(pot, V). Only two decision
  axes exist: SELECT (which option) and STOP (bank or continue).
- Arena: OpenSpiel-like extensive-form interface with chance and simultaneous moves and per-player
  observation(i); World (immutable ruleset version) / State (cloneable, hashable) / Player separation.

What constitutes a player/organism [IMPL]: a "circuit" -- a Python policy written only against the
bench interface (cannot name a card or a game; "forbidding it at the type level"), registered with a
neutral id (r0003 etc.), STOP or SELECT axis, transferable flag. Arena players are Python policies.
No genotype, no mutation, no evolutionary organism anywhere in ludus/. LLM agents appear only in cycle
001 (ceiling1.py).

Search/mutation/selection: none on organisms. Circuits are hand-authored. Worlds are hand-authored or
parameter families (FOUNDRY with gate/k/cap knobs; FOUNDRY-DECAY with decay). The "World Foundry"
mutate/distance/admission loop is design only (LUDUS-05).

Reward/scoring [IMPL]: exact expected value retention (circuit EV / optimal EV); per-decision regret
against optimal continuation (cycle 005); optimal-action rates; gap(k).

Temporal/spatial: episodic, short horizons (LOOM 4-12 moves per player); no spatial topology except
WEIR's link graph; no persistent world state across episodes.

Transfer: measured as RETENTION of a circuit's EV in another world exposing the same interface -- a
transplant assay over the transfer matrix, not learning transfer [IMPL/INTENT].

Provenance: rules_state field per world (HYPOTHESIZED until audited); rules_audit.json with publisher
source sha256 per rule line (sources kept locally, not committed) [IMPL/HIST].

Design vs implementation disagreements:
- CHARTER_v3 s1 says Ludus supplies worlds whose landscapes exert pressure on ORGANISMS; no ludus world
  has ever been bound to an organism ABI or run by a consumer [IMPL: no binding, no importer].
- ROLE s5 says "Item sampling is stratified by plies-to-terminal, always"; LUDUS-34 records that
  profile() samples uniformly and a default n=250 read CTRL_NIM345 gap(4)=0.200 ON the gate where the
  exhaustive reading is 0.240 [CORRECTION, seat's own].
- ROLE s0 says "one solver and one evaluator serve all"; three incompatible interfaces exist
  (archaeology L-2) [CORRECTION].
- Library mandate says arena worlds are "verified against external ground truth"; bench verify had
  only checked 4/21 matrix worlds and 17 had no per-world invariants (L-1) [CORRECTION].

-------------------------------------------------------------------------------------------------
## 4. World capability audit

Explicitly small/toy, precisely:
- LOOM/WEIR/TITHE: tiny 2-player perfect-information deterministic games, fully solvable by minimax;
  4 plies of search essentially solves all three (gap(4) 0.000 / 0.012 / 0.040) [RESULT-UNVERIFIED].
  Greedy-decidable: LOOM gap 0.000 at every horizon 4-12 (78 -> 23,844 eligible states).
- Bench worlds: single-agent stochastic stopping problems; exact DP over thousands of states (Flip 7
  8,192; Martian Dice 6,176 reconstruction; 14,653 in the controls row for the committed MD). Solitaire
  by construction (CYCLE_002 s2: "Both worlds are solitaire"; Incan Gold's player-leaving dynamics and
  Can't Stop's race removed). Flip 7 action/modifier cards not implemented. Two axes only.
  Five of six real bench worlds occupy one structural cell (iid-or-deck draw, total-ruin loss,
  solitaire, linear accumulation, exact) (ROLE s9) [HIST].
- FOUNDRY / FOUNDRY-DECAY: generated parameter families (gate, k, cap, decay) -- the closest thing to
  a world generator; small and exact.
- Arena: TTT, Nim, Pig, RPS, Kuhn poker, Ball-under-couch -- textbook games with known theory; ~19,830
  seeded episodes verified. Partial observability present only in Kuhn and the epistemic world;
  simultaneity in RPS; chance in Pig/Kuhn.
- Atlas: 1,338 catalogue rows from Wikidata/Wikipedia, HYPOTHESIZED, 0 executable from the catalogue.
Absent everywhere: multiple interacting agents beyond 2-player zero-sum toys, ecology, resources
shared across a population, environmental change/nonstationarity, open-endedness, communication,
long horizons, spatial worlds of any size, transfer between worlds by a LEARNER (only transplant of
fixed circuits), world generation beyond parameter knobs.
Qualification: W3 (rule-audited) 2 of 30 executable worlds COMPLETE (Martian Dice, Flip 7), 2 PARTIAL
(Incan Gold, Can't Stop) as of 09-16, under the seat's own P3 rule with operator spot check pending
(LUDUS-31) [HIST].

-------------------------------------------------------------------------------------------------
## 5. Organism capability audit

There is no organism. The "agents" are:
- Hand-written circuits (myopic stopper r0003: stop iff P(death)*pot >= E[immediate gain]; selectors
  r0010-r0014; floors r0004 never-bank, r0005 always-bank) [IMPL].
- Constructed policy ladders (random-legal, greedy-1ply, depth-k minimax with the world's own score as
  cutoff, majority class) as cheap baselines [IMPL].
- An LLM (nvidia:gpt-oss-120b) in cycle 001 at the rules/optimal-action/game-value rungs [HIST].
Did an organism have a fighting chance at a nontrivial primitive? Not applicable as posed: no
adaptive organism was ever placed in a Ludus world. The cycle-001 LLM was "statistically identical to
the four-line heuristic" at the optimal-action rung (exact McNemar p .500 WEIR, 1.000 LOOM) in worlds
the gate had already shown could not separate them [RESULT-UNVERIFIED]. What Ludus measured is whether
WORLDS can separate mechanisms, and its own answer for most authored worlds was no.

-------------------------------------------------------------------------------------------------
## 6. Search and pressure mechanism

Novelty production: human/LLM-authored worlds and circuits; parameter sweeps over world families; a
catalogue crawler (Wikidata/Wikipedia) for candidate worlds. No evolution, no QD, no curriculum. The
"pressure" concept appears only as design intent in CHARTER_v3 (selectivity profile per world;
generated families with a control knob as "the unit the World Foundry prefers") [INTENT].
Bottlenecks named in the record: world authoring cost and rules provenance (no rulebook consulted
for anything until 09-16); monoculture of structural cells; three interfaces; exact-solvability
requirement limits world size (the instrument is exact precisely because worlds are small).

-------------------------------------------------------------------------------------------------
## 7. Measurement / ruler stack

[IMPL unless marked]
- r0001 greedy-decidability gap -> demoted to diagnostic by r0002 depth profile gap(k), k=1..4.
- GATE-W1: admit only if gap(4) >= 0.20 (amended the day it was written). Rung checks R0 legality
  (state-blind guess legal >= .75 -> ineligible), R2 optimal action (max cheap baseline >= .80 ->
  ineligible), R3 game value (one value >= .60 of items).
- Stochastic family gate (cycle 002, preregistered): not measurable if best cheap policy retains >= .98
  of optimal EV; action gap kept on visitation-weighted states (uniform vs visitation differ 78x for
  the myopic rule on Flip 7).
- Transfer: EV retention of a transplanted circuit; axis decomposition (how much residual sits on
  SELECT vs STOP); fitted-per-world baselines to beat.
- Cycle 004: exact variance decomposition of E_ijk over 5 circuits x 5 partners x 16 worlds;
  preregistered rule S_circuit < .30 and V_cxw > V_cxp -> CONTEXTUAL_BASIS_REQUIRED.
- Cycle 005: per-decision regret vs optimal continuation under REFERENCE / SELF / UNWEIGHTED occupancy.
- Circuit maturity ladder up to ABLATION_SUPPORTED and PARTNER_ROBUST.
- Arena verify (20 checks: theory reproduction -- Kuhn -1/18, Nim XOR, TTT draw; determinism;
  invariants), epistemic tests (25), key-name leak check, differential leak audit.
- Bench verify (universal mass/acyclicity + per-world invariants).
- W-ladder W0..W8 (CHARTER_v3 s5; W1, W2, W4, W7 the seat's reconstruction).
Controls run 2026-09-16 (CONTROLS_2026-09-16.json, 25 rows) [IMPL, rows read]:
- depth profile: regression rows reproduce LOOM/WEIR/TITHE; negative CTRL_LEDGER 0 at all k; positive
  CTRL_ORCHARD fires; CHEAT CTRL_NIM345 / NIM3456: the gate ADMITS normal-play Nim although Bouton's
  4-line xor rule is optimal -> GATE-W1 cannot see closed-form cheap policies (LUDUS-33).
- bench verify: catches pot+1 and a cycle and a large probability halving; does NOT detect a halved
  smallest probability (below tolerance) and is BLIND to the draw law (one-ray Martian Dice verifies).
- arena key-name check: fires only on the named-key leak, silent on 3 of 4 injected leaks
  (innocuous key, action-order leak, public-state leak); differential audit fires on all 4.
Known blind spots: uniform state sampling (fixed only partially); world authored by the same seat as
the baseline (ROLE s4 "I designed both the worlds and the heuristic"); rules reconstructed from memory.

-------------------------------------------------------------------------------------------------
## 8. Experiment inventory (campaigns)

LC1. Cycle 001 CEILING-1 -- 2026-08-26
- Q: is there a measurable band between a trivial heuristic and an affordable agent?
- Worlds LOOM/WEIR/TITHE; agent: LLM (gpt-oss-120b, n=20 per cell) vs greedy/depth-k; exact minimax.
- Reported: band EMPTY; every world fails GATE-W1 (k=4 gaps .000/.012/.040); LLM statistically
  identical to greedy at optimal action; the one positive (0.900 game value) was near-terminal item
  sampling (stratified: 7/17 = .412 where 5+ plies remain). Eight harness defects caught.
- Paths: roles/Ludus/CYCLE_001_ceiling.md; ludus/ledgers/cycle001_*.
- Label: REPORTED NEGATIVE/NULL (with an internal false positive caught -> LATER OVERTURNED for the 0.900).

LC2. Cycle 002 stochastic stopping -- 2026-08-26
- Q (v2 s17): is "push your luck" one strategic family?
- Worlds Flip 7 core, Martian Dice (reconstructed); exact DP; constructed policies; zero model calls.
- Reported: "family REAL but NEARLY EMPTY"; Flip 7 NOT MEASURABLE at the stop decision (myopic rule
  retains .9991); transplanted stopper retains .9872 with a competent claim rule; 86% of Martian Dice's
  residual lives on the claim (SELECT) axis.
- Later: LUDUS-01 (2026-09-16) audit against the publisher sheet moved 2 Martian Dice rules (rays
  claimable every roll; unclaimable roll scores rather than busts); EV 2.093806 -> 3.110382; SELECT
  recovers -0.0005 and STOP +0.0486 -> the 86%-on-claim-axis reading "is a fact about the
  reconstruction, not about Martian Dice" (annotation in CYCLE_002).
- Label: LATER OVERTURNED (Martian Dice axis reading); Flip 7 non-measurability stands (Flip 7 audit
  COMPLETE, 0 moved).

LC3. Cycle 003 prospective scope prediction -- ~2026-08-27
- Registered before Incan Gold and Can't Stop were built: r0003 retains >= .97 with a competent SELECT
  partner and the residual localises off the stop axis.
- Reported: both 1.0000; Can't Stop residual SELECT +.0611, STOP +.0000; beats fitted-per-world baseline
  in four worlds. Unpredicted: SELECT ordering reverses between Martian Dice and Can't Stop (r0011
  worst in one, best in the other); first mechanism refuted (wrong sign), w0001 gating fraction
  registered as replacement.
- Later: rules of both worlds were HYPOTHESIZED at the time; 09-16 audit found Incan Gold and Can't Stop
  rules confirmed, one constant each unconfirmable from text; Martian Dice (where w0001 = .4272 lives)
  had 2 rules wrong -> the reversal that w0001 explains rests partly on the reconstruction [CODE-INFERRED
  link; not re-run here].
- Label: REPORTED POSITIVE (prediction) / MIXED (mechanism).

LC4. Cycle 004 basis audit -- 2026-08-27
- Prompted by r0003 reading 0.0000 in gated FOUNDRY and Lucky Numbers beside an optimal selector.
- Exact factorial 5 circuits x 5 partners x 16 worlds = 400 cells. Reported CONTEXTUAL_BASIS_REQUIRED:
  world .3497, circuit x world .1692, circuit x partner .0307; S_circuit .2605.
- Later: cycle 005 DEMOTED it (support mismatch). Artemis R-32 worker (2026-09-28): r0003 "stops on exact
  ties e_gain == p_dead*pot including at pot=0, manufacturing the 0.0000 cells in Coloretto, Lucky
  Numbers and the gated FOUNDRY fossil; a tie-continue variant scores 0.999-1.0 and retains >= 0.944 vs
  every partner in 18 worlds"; "the 'identified design' has no committed script or cells"
  [RESULT-UNVERIFIED]. Verified here in code: circuits.py r0003 returns `not (e_gain > p_dead * pot)`,
  i.e. it STOPS on equality, including pot = 0 with e_gain = 0 [IMPL, verified].
- Label: LATER OVERTURNED (demoted by cycle 005; the triggering 0.0000 cells are plausibly a tie-rule
  artifact per an unverified worker).

LC5. Cycle 005 occupancy / demotion -- 2026-08-27
- Reported: under a common reference occupancy circuit main effect .8528, circuit x world .1021
  (vs cycle 004 on-policy .2126/.4374) -> VERDICT DEMOTED: much of "contextual competence" was support
  mismatch. Reference-weighted conditional regret adopted as the primary statistic (CHARTER_v3 s6).
- Label: REPORTED POSITIVE (for the correction).

LC6. Atlas of Game Worlds build -- ~2026-08-31 .. 09-01
- 1,188 -> 1,338 catalogued rows; 12 construction defects recorded (e.g. an ELIMINATE rule about to
  write loss_shape=ELIMINATION across 47 worlds from "captured seeds"; luck_factor fabricating 0.35).
- Label: UNKNOWN as science (infrastructure); classifier accuracy never measured (PARKED).

LC7. Arena vertical slice -- 2026-09-01
- 5 worlds, one interface; sequential interface broke on 3/5 (Pig chance, RPS simultaneity, Kuhn
  private observation) and was redesigned; determinism failed on all five at first run, fixed;
  20/20 checks; epistemic layer found two defects (test [6] passed on an EMPTY information set).
- Label: REPORTED POSITIVE (interface works for 5 textbook games) -- unaudited rules.

LC8. Qualification controls LUDUS-03 -- 2026-09-16 (44d3dd7ff)
- Reported: GATE-W1 admits Nim (cheat); bench verify blind to the draw law; key-name check silent on
  3/4 leaks; n=250 depth sample sits on the gate where exhaustive reads .240.
- Label: INSTRUMENT FAILURE (findings about the instruments, by design).

LC9. Rule audits LUDUS-01 / LUDUS-15 -- 2026-09-16 (333e19715, fb858dd5c)
- Martian Dice: 0 constants moved, 2 rules moved; Flip 7 COMPLETE; Incan Gold and Can't Stop PARTIAL
  (treasure values; column heights printed on components, not in text).
- Label: REPORTED POSITIVE (audit), which simultaneously OVERTURNED cycle 002's Martian Dice reading.

-------------------------------------------------------------------------------------------------
## 9. False-positive / false-negative archaeology

T1. Near-terminal sampling (cycle 001): claim 0.900 game-value accuracy -> evidence: sampled items ->
challenge: 40% within two plies of the end -> correction: stratified 7/17 = .412 -> status: retracted
in-cycle; standing rule "stratify by plies-to-terminal"; LUDUS-34 shows the profile code still samples
uniformly [CORRECTION, partially unremediated].

T2. Realm labels (A3): worlds designed to instantiate resource economy, spatial control, temporal
strategy contained no strategic decision (greedy optimal 85-100%) -> labels banned as findings.
A false positive class ("the world has strategic content because it names it") caught by the seat.

T3. Martian Dice "86% on the claim axis" (cycle 002) -> rules reconstructed from memory -> publisher
audit 2026-09-16 reverses the decomposition -> status: reading attached to MartianDiceRecon only.
A contamination class: unaudited rules masquerading as a real game.

T4. r0003 0.0000 cells -> cycle 004 "contextual basis" -> cycle 005 demotion (support mismatch) ->
Artemis R-32: tie-stopping at pot=0 manufactures the zeros [RESULT-UNVERIFIED; tie rule verified in
code]. Timeline: claim (partner dependence, 08-27) -> evidence (400-cell exact factorial) -> challenge
(external review: exposure x competence) -> correction (cycle 005) -> second challenge (tie rule, 09-28)
-> current status: cycle 004's verdict demoted; the PARTNER_ROBUST block on r0003 was measured in an
unverified FOUNDRY world (L-1) and may be an implementation artifact of the circuit itself.

T5. Verification greens that could not fail: bench verify "VERIFIED-INTERNALLY" cannot see the draw
law (a one-ray Martian Dice verifies); arena key-name check misses 3/4 leaks; GATE-W1 admits Nim.
All found by the 09-16 controls pass, after the cycles that relied on them.

T6. Likely false negative: Ludus's empty-band verdicts (cycle 001; Flip 7) are verdicts on SMALL,
AUTHORED or SOLITAIRE worlds with exact solutions. They do not show games cannot separate reasoning
from heuristics; they show these worlds cannot. The seat said so (A2 refuted by its own data, the
founding corpus re-endorsed) [HIST]. The World Foundry that was meant to supply richer worlds never
produced one.

-------------------------------------------------------------------------------------------------
## 10. Research outputs

- roles/Ludus/CHARTER_v1.md, CHARTER.md (v2), CHARTER_v3_WORLD_FOUNDRY.md, ROLE.md, BOOTSTRAP.md,
  GUARDRAILS.md.
- roles/Ludus/CYCLE_001_ceiling.md, CYCLE_002_stochastic_stopping.md, CYCLE_004_PREREG_basis_audit.md,
  CYCLE_004_VERDICT_basis_audit.md, CYCLE_005_verdict_demotion.md.
- roles/Ludus/REVIEW_PACKET_2026-08-27.md, REVIEW_PACKET_2_2026-08-27.md, REVIEW_PACKET_3_2026-09-01.md
  (atlas breadth), REVIEW_PACKET_4_2026-09-01_arena.md, REVIEW_PACKET_5_2026-09-11_adoption.txt,
  REVIEW_PACKET_6_2026-09-16_controls.txt, REVIEW_PACKET_7_2026-09-16_rule_audit.txt,
  REVIEW_PACKET_8_2026-09-16_three_audits.txt.
- roles/Ludus/ATLAS_OF_WORLDS.md (build record, 12 defects), ludus/atlas_of_worlds/ATLAS.md, README.md.
- roles/Ludus/ARCHAEOLOGY_2026-09-11.md (26-item queue classification), CROSSWALK_INTAKE_2026-09-11.md.
- roles/Ludus/arena_verification_2026-09-01.txt, epistemic_verification_2026-09-01.txt.
- ludus/atlas/CIRCUIT_LEDGER.md, CIRCUIT_MATURITY.md, BACKLOG.md; ludus/bench/RULES_AUDIT.md.
- ludus/docs/Worlds as Part of the Prometheus Strategic Roadmap.md (preserved roadmap).
- Cross-seat: roles/Artemis/selftest/runs/R-32/REPORT.md (r0003 tie rule; worker claim).

-------------------------------------------------------------------------------------------------
## 11. Journals, TODOs, pivots, abandoned branches

- Journals: 2026-09-11, 2026-09-16 only; SESSION_LOG_2026-08-31_to_09-01.md for the atlas/arena push.
- History compression: all pre-09-01 work (cycles 001-005, bench, atlas) landed in bulk commits on
  2026-09-01 (e85bfa6b9, 5e4f68c76) on branch ludus/atlas-of-game-worlds; dates inside documents
  (08-26, 08-27) are not git-verifiable [IMPL: earliest git add of ROLE/CHARTER/CYCLE files is
  e85bfa6b9 2026-09-01].
- BACKLOG_H0H5.md: 38 rows LUDUS-01..37 (+); closed by 09-16: 01, 03, 15, 35 (30 answered). Next
  executable action named: LUDUS-02 chopping grammar, then LUDUS-04 per-world invariants -- neither
  done. XL operator decisions open: LUDUS-31 (seat-performed audits count for W3), LUDUS-32 (arena
  interface survives).
- Superseded/abandoned: hourly loop (PARKED), LLM in-context meter, founding corpus of 30-50 named games,
  "Next in order" queue (Hanabi, OpenSpiel cross-validation, D13, arena-atlas join, classifier accuracy).
- No unmerged ludus/* branch on origin [IMPL: git branch -r].

-------------------------------------------------------------------------------------------------
## 12. Lens inventory

L-L1. Discriminability-of-worlds lens (GATE-W1, depth profile, EV retention gate, cheat fixtures)
- Substrate: small exactly-solvable games; organisms: cheap baselines and circuits.
- Phenomenon: whether a world separates a mechanism from a cheap substitute; reading-ceiling of a world.
- Mechanism: exact minimax/DP, gap(k), retention, stratified sampling, controls.
- Ceiling: exact solvability caps world size; cheap-policy family limited to depth-k search with the
  world's own score (closed-form programs not enumerated -- Nim cheat).
- Noise: uniform vs visitation weighting (78x); same author for world and baseline.
- Reusable: the question form itself ("could this world distinguish X from a four-line heuristic"),
  the cheat-fixture pattern (Nim), the controls table; directly applicable to any Phase 3 world.
- Toy-grade: the worlds it was applied to.

L-L2. Transplant/transfer-matrix lens (bench, circuit registry, axis decomposition, occupancy-weighted regret)
- Phenomenon: whether a fixed policy component retains value across worlds sharing an interface;
  separation of support (exposure) from conditional competence.
- Mechanism: exact retention, partner matrices, variance decomposition, reference occupancy.
- Ceiling: two axes (SELECT/STOP), solitaire, hand-written circuits; a single circuit tie-rule can
  manufacture zeros.
- Reusable: the cycle-005 exposure-vs-competence correction (reference-weighted conditional regret) is
  a general confound remedy for any "transfer" claim on on-policy outcomes.

L-L3. Epistemic/leak lens (arena differential audit)
- Phenomenon: information leakage from environment to player; observation sufficiency.
- Mechanism: hold everything fixed, change the secret, see what moves (fires 4/4 injected leaks).
- Reusable: high -- the differential audit is world-agnostic.

L-L4. World catalogue lens (atlas of worlds)
- Substrate: 1,338 catalogue rows with heuristic structural tags; nothing executable.
- Reusable as a sampling frame for structural cells; classifier precision/recall unknown; ~41% of rows
  above the English-Wikipedia source ceiling.

-------------------------------------------------------------------------------------------------
## Open questions / unknowns

- Was any Ludus world ever run with a Proteus/Archaeon organism? Code evidence says no (no binding, no
  importer); confirm no off-repo run [UNKNOWN beyond git].
- Does r0003's tie rule account for all 0.0000 cells (Artemis R-32 worker claim)? Not re-run here.
- Cycle 003's w0001 mechanism was registered on reconstructed Martian Dice rules; not re-tested after
  the 09-16 audit [UNKNOWN].
- STATUS says ACTIVE (currency 09-16); no activity after 09-16 -- is the seat parked? [UNKNOWN]
- The "identified design" of cycle 004 lacks a committed script per R-32 [RESULT-UNVERIFIED claim;
  not checked here].
- Atlas classifier accuracy and the Postgres ludus_atlas contents were not inspected.
- Atlas (the locator seat) lists Ludus as NOT COVERED in its cross-engine synthesis; there is no Atlas
  cross-check for any Ludus claim.
