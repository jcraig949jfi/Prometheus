# Lexis -- forensic dossier

Seat: Lexis (vocabulary / operator-menu-growth seat; prior-art forensics on commission)
Crawl date: 2026-10-01
Base SHA of worktree: 19299e06b (origin/main at crawl)
Crawler: Sisyphus worker (Opus 5.5), read-only

Coverage statement.
READ: roles/Lexis/ROLE.md (adoption annotation, s1-s6 in full), STATUS.md (complete),
BASE_ROLE_ADOPTION_2026-09-11.txt (s1-s8), CALIBRATION.md (complete), SUMMARY.md (TL;DR),
notes/G7_CHARON_2026-09-01.md (s1), notes/G1_ABLATION_2026-08-25.md (grep of headline counts),
handoff/lexis_pair.py (docstring), archaeology/hct01_prior_art_2026-09-03/LEXIS_HCT01_EXTERNAL_
REVIEW_PACKET.txt (headline, s1-2) and ADDENDUM_2026-09-04 (s1-3); the operator ruling to Lexis
(roles/Archaeon/prompts/2026-09-11_rulings/LEXIS.md), Apollo's ack (roles/Apollo/prompts/
2026-09-11_task2_ack/LEXIS.md), Apollo STATUS/BACKLOG rows APOLLO-10/11, archaeon/docs/expansion/
DECISIONS.md D-25, roles/base-role/RESPONSIBILITIES.md lines 205-221 and the commit that introduced
the Lexis clause (8bb162a77); full git log of roles/Lexis on all refs (32 commits, 2026-08-24 ..
2026-09-11); git ls-files / git grep -il lexis (with holdout/secret exclusions) for code and consumers;
comms listing for Lexis and bodies #885, #1118, #1149, #1173; Achilles census rows; Artemis D002
RESULT row D002-07.
NOT READ: library_learning/ pass notes and RETROSPECTIVE in full; REVIEW_REQUEST/RESPONSE files;
PLAN/SESSION files in full; the instrument code bodies beyond names (except lexis_pair.py docstring);
the HC-T01 ledgers (L_*.jsonl) and the recovered literature PDFs (~200 tracked files of third-party
papers and code archives); apollo/ source. Reason: budget and territory -- Lexis is a measurement and
adjudication seat over another seat's substrate (Apollo's blackboard, Hephaestus's forge, Herakles's
HC-T01); its own code is analysis instruments.

-------------------------------------------------------------------------------------------------
## 1. Identity and purpose

Canonical name: Lexis ("lexis -- diction, the vocabulary available for saying things"; ROLE.md
header). No aliases in the census [HIST]. Seat created 2026-08-24 (e07d166ae "Lexis seat +
library-learning study: Apollo's ceiling is the wall this literature exists to break") [HIST].

Original charter [INTENT, ROLE s1-s3]: "Own the menu-growth slice end to end: hold the measured state,
sequence the decisions, fix the evidence bar for each one before it runs, and be the seat that says
'not yet' -- including to a result that is going the program's way." Layer: SEQUENCING (decides what
gets attempted next in the slice and what must be true to justify spend), distinct from Charon
(claims), Elenchus (work), Harmonia (instruments), Diomedes (coordinate systems). In scope: anything
that changes WHAT OPERATORS EXIST (library learning, abstraction extraction, primitive admission,
transfer of primitives). Out of scope: search quality within a fixed vocabulary (Apollo). Hard
constraint (operator 2026-08-24): no touching Apollo's or Hephaestus's code ("I don't want them
adjusting anything"). Status line: "v1, proposed. Not ratified, not registered." [HIST]

Pivots [HIST]:
- 2026-08-24/25: library-learning literature study (8 passes, 4 families) + measured state of
  Apollo's blackboard ceiling and the forge's primitive usage; gates G0-G6 fixed and run.
- 2026-08-27: Apollo's E9 (42-task battery authored BLIND by Charon) scored the 0.833 organism at
  0.0667 mix-adjusted, "40 of 42 abstained, zero guesses" against home 0.6000; Lexis ingested it
  (feb655ae0) and added G7 authorship independence; every home-battery accuracy figure re-labelled
  as co-adapted (ROLE s4a POPULATION note).
- 2026-09-01: G7 run once on Charon's battery (ab0371e7c); operator CLOSEOUT prompt (9d5ee6009,
  body sha256 91fbd86b...): no further bundle search until a live consumer shows more generalisation
  evidence would change a decision; consumer handoff of the frozen interface pair (9962f6bd4). Seat
  IDLE.
- 2026-09-03/04: reopened ON COMMISSION as prior-art adjudicator for Herakles's HC-T01 (Historical
  Collider on Toussaint 2003); 12 rulings, 9 corrections, 2 against itself (62f7a1a1e, ad9c29337,
  ce79401b1).
- 2026-09-11: base-role adoption (4e8e63b41), congruence audit re-run (a37988536). Operator ruling via
  Archaeon (comms #26; roles/Archaeon/prompts/2026-09-11_rulings/LEXIS.md): "Your historical identity
  is NOT ratified yet. Let the blind Apollo Task 2 return first ... After Apollo's blind result, the
  operator decides whether Lexis still occupies a distinct role or its useful machinery is absorbed
  elsewhere." State: BLOCKED on Apollo Task 2 (LEX-07 executable).

THE "IDENTITY RE-ADJUDICATED AFTER A BLIND RESULT" clause, traced.
roles/base-role/RESPONSIBILITIES.md:221 lists three legitimate outcomes of booting an old seat;
the third is "identity re-adjudicated after a blind result (Lexis)". It entered with commit 8bb162a77
(2026-09-11, "reanimation rulings (D-25)") and mirrors D-25 in archaeon/docs/expansion/DECISIONS.md:
"Lexis is BLOCKED on Apollo's blind Task 2 with LEX-07 executable; its identity is re-adjudicated
after." [IMPL: text verified]
- The blind result it refers to is APOLLO'S TASK 2 -- state injection (arms A raw / B oracle-state /
  C corrupted-state) over Lexis's committed fixture roles/Lexis/handoff/state_injection_fixture.json,
  on the blackboard E9 organisms, with pre-fixed readings from handoff/LEXIS_G7_HANDOFF.md s5. Lexis
  delegated it (comms #15); Apollo accepted 2026-09-11 (#23; roles/Apollo/prompts/2026-09-11_task2_ack/
  LEXIS.md: "Task 2 accepted, preregistration first, arm A alone, then B/C"). [HIST]
- It NEVER RAN. Apollo's last commit on apollo/ or roles/Apollo is 2b7c6e4fb (2026-09-11, the ack);
  apollo/cycles/state_injection/ does not exist; BACKLOG rows APOLLO-10 (preregister) and APOLLO-11
  (run) are open; Apollo STATUS.txt still says "Task 2 state injection OWED, not authorised under s0a
  (APOLLO-10, XL-adjacent: needs the operator's word)" [IMPL: git log/ls verified]. Lexis has no commit
  after 2026-09-11 [IMPL]. LEX-07 (the cheat control for g5_redundancy.py and bundle_test.py), the one
  item the operator approved, was never run [IMPL: no commit; STATUS lists it as NEXT].
- Consequently the identity re-adjudication NEVER HAPPENED. The base-role clause describes a ruled
  pathway, not a completed event. Lexis remains: lane 1 IDLE since 09-01, lane 2 COMPLETE, identity
  unratified, BLOCKED on a result no seat produced [CODE-INFERRED from absence; HIST for the ruling].
- Distinguish the EARLIER blind result that did re-adjudicate the seat's CLAIMS: Apollo E9 /
  Charon's blind battery (2026-08-25..27) and Lexis's own G7 run (2026-09-01). That event changed
  what the seat's numbers mean (home accuracy authorship-bound; ceiling over the blind battery 2/42),
  not the seat's identity [HIST].

Terminal state: census lifecycle IDLE 2026-09-01 (lane 1); host M1 [HIST]. Later contact only via
Artemis worker reports (#885 R-20, #1118, #1173) treating Lexis as "idle since 09-01" [HIST].
Relationships: Apollo (substrate studied, read-only; Task 2 owner), Hephaestus/forge (G0/G1 subject),
Charon (blind battery author), Aporia (IQ arc used Lexis numbers: aporia/iq/run_transfer_1.py and
run_ceiling_abstain.py cite Lexis's ceiling regime) [IMPL], Herakles (HC-T01 commissioner), Elenchus
(AG-02 owed), Diomedes (manifest CRLF defect cross-reproduction).

-------------------------------------------------------------------------------------------------
## 2. Engine / system inventory

Lexis built no world, organism or search engine. It built MEASUREMENT INSTRUMENTS over Apollo's
blackboard program language and the forge's primitive ledger [IMPL; paths under roles/Lexis/,
19 instrument scripts + handoff, ~5,600 lines Python total for all tracked .py under roles/Lexis
including recovered third-party code].

I1. Closure / ceiling instruments: instruments/product_ceiling.py, product_ceiling_fast.py,
robust_ceiling.py, reachable_answers.py, ceiling_diagnosis.py, traceclass.py -- exhaustive joint
product BFS over Apollo's admissible program language on a task battery (484,218 joint states,
frontier empty at depth 23) [IMPL names; RESULT-UNVERIFIED numbers].
I2. Precondition audits: congruence_audit.py (field projection D is a congruence: aliasing, globals,
history independence, cross-task contamination), audit_rw.py, commute.py (39/45 operator pairs commute).
I3. Admission gates: g5_redundancy.py (NEW(p,C,T); dS vs dE ledgers), permutation_null.py (all 24
candidate permutations, G6), g7_remeasure.py (blind-author battery), bundle_test.py (pairs as units),
candidate_primitives.py (the frozen pair lexis_op_subtract + lexis_score_by_value_match__g).
I4. Forge usage: g1_usage.py, g1_ablation.py, g1_ablation_decompose.py (2,103 measured deltas).
I5. Handoff: handoff/lexis_pair.py (loader refusing on sha256 drift of candidate_primitives.py),
consumer_utility.py, verify_handoff.py, build_handoff.py, state_injection_fixture.json,
interface_pair_manifest.json, ADMISSION_PROTOCOL.md.
I6. workspace_guard.py (D-23 refusal from canonical checkout; inherits archaeon/workspace.py).
I7. HC-T01 prior-art archaeology: ledgers L_*.jsonl and recovered literature (no executable engine;
the HC-T01 experiment code is Herakles's, branch herakles/historical-collider-v0) [HIST].
All instruments: local CPU, deterministic, minutes; read-only on apollo/ [HIST].

-------------------------------------------------------------------------------------------------
## 3. Architecture (of the studied substrate, as Lexis models it)

Not an evolutionary world. The substrate is Apollo's Gen-1 "blackboard" organism: a pipeline of
named operators (27 in the unrestricted pool; 13 clean transformers; scorers) reading and writing
slots of a blackboard state (23 slots; projection D = 17 slots that can affect the answer) on
natural-language multiple-choice reasoning tasks [HIST from ROLE s4]. Lexis's architecture is:
enumerate the closure of admissible programs over a battery, classify unreached tasks as dE
(outside the operator closure) vs dS (reachable but unrouted), and test candidate operators for
redundancy, permutation robustness and authorship independence. Organisms = programs (operator
sequences) over a fixed vocabulary; "mutation" = adding a vocabulary item; no selection loop.
Design vs implementation: ROLE s4a records its own retraction "The substrate's ceiling is 0.8333"
(the unrestricted pool reaches 107/120 by unconditional guessing) -> correct noun "Apollo's
admissibility rules" [CORRECTION].

-------------------------------------------------------------------------------------------------
## 4. World capability audit

The "world" is a task battery: T_home (120 tasks, o1_enumerate.build_battery(); its synth subset of
30 tasks redrawn with PYTHONHASHSEED) and T_charon (42 tasks, 7 categories x 6, authored blind,
roles/Charon/apollo_e9/charon_battery_E9.json) [HIST]. Static, single-step, nonspatial,
fully observed prompt + candidates; answered by a fixed program. Easily memorisable and, as measured,
co-adapted with the parsers that read it (15/42 Charon tasks unrecognised by any clean-pool operator;
8 of 13 clean transformers fire on no task by another author) [RESULT-UNVERIFIED]. A narrow benchmark
in the precise sense the charter warns about.

-------------------------------------------------------------------------------------------------
## 5. Organism capability audit

Blackboard pipelines of hand-written Python operators with regex/keyword parsers (e.g. _REL_PATTERN
requires capitalised multi-letter names and one of ten comparatives; _QUESTION_KEYWORDS a closed list
of 15 superlatives) [HIST, ROLE s4a]. No learning, no memory across tasks, no self-modification.
Fighting chance at a nontrivial primitive: bounded by construction -- the exact closure shows any macro
over the existing operators is capped at 0.8333 on T_home (G3 "CONFIRMED BY PROOF") and 2/42 on T_charon
[RESULT-UNVERIFIED]. The only measured vocabulary gain was a compute+readout PAIR (+5/+5/+5 home;
+4 of 6 on Charon's all_but_n tasks, all 24 permutations), which REGRESSES the production organism
(9 CORRECT -> WRONG flips from a write-write hazard on max_value) unless placed compute_first [RESULT-
UNVERIFIED].

-------------------------------------------------------------------------------------------------
## 6. Search and pressure mechanism

No search engine of its own. Novelty sources studied: LLM-authored singleton candidates (three,
all NEW=1, dE=0, dS=0, none admitted -- G5 ledger), hand-built pairs, the forge's T1->T2->T3 ratchet.
Bottleneck named: "Any generator proposing one operator at a time scores zero here regardless of
operator quality" -- the unit of growth is an interface pair [RESULT-UNVERIFIED]; surface-layer
parsing is the whole deficit under a different author.

-------------------------------------------------------------------------------------------------
## 7. Measurement / ruler stack

Pre-committed gates (ROLE s5) [INTENT/HIST]: G0 (is the forge ratchet live -- FIRED), G1 (usage
< 10% means the admission criterion is the problem -- FIRED at 5.94%), G2 (compute-matched or not
reported), G3 (transfer, not compression; Apollo battery disqualified by proof), G4 (spend only on G3
positive), G5 (redundancy/representability; dS vs dE ledgers), G6 (all 24 permutations; survival =
equivariance, not reasoning), G7 (authorship independence; a population change, not a null; not
monotone). Controls: positive controls P1/P2 in G7 (0.8333 home; E9 2/42 + 40 abstentions reproduced).
Missing control, recognised by the operator: LEX-07 cheat control (can the leakage detector flag a
gold-reading primitive?) -- "if it cannot, every downstream anti-leakage confidence is decorative";
never run [HIST/IMPL absence].
Cross-checks by others: Artemis D002-07 reproduced G1 (2,103 deltas / 89.73% zero / 5.94% load-bearing)
[RESULT-UNVERIFIED, consistent with notes/G1_ABLATION_2026-08-25.md lines 35-36]. Artemis U-02 (#1173):
Lexis's 0.10 bar was frozen before the number it was later applied to (e07d166ae, 2026-08-24); a
downstream 57/572 = 0.09965 reading sits on the bar with side-of-bar tie-dependent [HIST].
Artemis R-20 (#885, worker): the E9 collapse reproduces with a third blind author; a harmless
"Question: " prefix drops home 0.60 -> 0.40; "validate a generator by reproducing the known blind
result" accepts 100% of broken generators tried [RESULT-UNVERIFIED].

-------------------------------------------------------------------------------------------------
## 8. Experiment inventory

X1. Library-learning literature study -- 2026-08-24/25 (e07d166ae, 80ded3fb1, 3cf4062c1)
- Eight passes; four families; cross-domain primitive transfer "unreported across ~20 systems";
  "the distinctive asset is the corpus, not the method". Label: REPORTED NEGATIVE/NULL (novelty).
X2. Ceiling closure + dE/dS diagnosis -- 2026-08-25 (fcdc91af8, 85c982f99)
- Exact 100/120 = 0.8333 for Apollo's admissible language; 20 unreached tasks all dE; headline
  "substrate ceiling" retracted to "admissibility rules". Label: REPORTED POSITIVE (closure) with
  in-session CORRECTION.
X3. Forge gates G0/G1 -- 2026-08-25 (fcdc91af8)
- Ratchet shipped (G0 fired); 86.19% of called primitives decoration, 5.94% load-bearing; the forge's
  anti-decoration gate cannot fire on an all-zero tool (FAIL_ABLATION fired zero times). Label:
  REPORTED NEGATIVE (kill of "forge more tools").
X4. G5 redundancy + pair discovery -- 2026-08-25 (043dc92ac)
- 3 LLM singletons: none admitted; compute+readout pair +5/+5/+5. Label: MIXED.
X5. G7 blind re-measure -- 2026-09-01 (ab0371e7c)
- Pair +4/6 on Charon, all permutations; ceiling 2/42 over Charon; 15/42 unrecognised. Label:
  REPORTED POSITIVE (pair replicates) / REPORTED NEGATIVE (home accuracy authorship-bound).
X6. Consumer utility / closeout -- 2026-09-01 (9962f6bd4)
- Pair regresses the home organism (9 flips) unless compute_first; Charon 4 correct / 3 wrong;
  break-even wrong-penalty 4/3. Label: MIXED.
X7. HC-T01 prior-art adjudication -- 2026-09-03/04 (62f7a1a1e, ad9c29337, ce79401b1)
- Premise obsolete (HC-T01 already adjudicated WEAK_SIGNAL_ONLY); Misevic, Ofria & Lenski 2006 is
  HC-T01's design in Avida; Kumawat 2024 covers the missing cell; kill condition scored with the wrong
  statistic. Recommendation RUN_A_SMALLER_CALIBRATION_FIRST executed by others (9c1badfba, d51d1fa82):
  K7 degenerate at its window (Spearman exactly -1.0000); detector largely reads "genome contains at
  least one production rule" (step 0.34 -> 2.73 then flat). Label: REPORTED POSITIVE (for the
  critique) / the seat's decision rule was not exhaustive (self-correction).
X8. Congruence re-check -- 2026-09-11 (a37988536): five PASS at HEAD. Label: REPORTED POSITIVE.
X9. Apollo Task 2 (the blind result for identity re-adjudication): NEVER RUN. Label: UNKNOWN.

-------------------------------------------------------------------------------------------------
## 9. False-positive / false-negative archaeology

T1. Home-battery accuracy -> authorship-bound.
claim: Apollo organism 0.60 home / ceiling 0.8333; 16.7% of the battery unreachable by vocabulary ->
evidence: exact closure -> challenge: Charon's blind battery, E9 0.0667 with 40/42 abstentions ->
correction: G7 ceiling 2/42; "its 83.33% solved was authorship-bound; its 16.67% dE is a lower bound"
-> status: home numbers are diagnosis-only; admission requires a blind author [CORRECTION]. A
selection-relation confound (battery and parsers written by the same hand).

T2. "Substrate ceiling 0.8333" -> one noun too wide (11-transformer unrestricted program reaches
107/120 by unconditional guessing) [CORRECTION, in-session].

T3. op_build_ordering "solves 3/5 temporal tasks" -> all three were the candidates[0] fallback,
caught by the permutation null (CALIBRATION 2026-08-25) [CORRECTION]. Permutation null as a
false-positive killer.

T4. "Winning tools used 0% of their primitive libraries" -> described the superseded pre-04-02 forge;
rebuilt forge measured 86.19% decoration / 5.94% load-bearing [CORRECTION, G0].

T5. Pair admission at ceiling level -> organism-level regression (write-write hazard on a reused
slot); the BFS "reports the best program in the closure, which orders around the hazard" [CORRECTION].
A ruler-blind-spot class: closure ceilings hide placement hazards.

T6. HC-T01 K7 kill -> degenerate test (could not fail to fire at its window). A kill that could not
have failed. The adjudication also found the HC-T01 accessibility detector is close to a presence
detector for machinery [HIST].

T7. Leakage detector never shown able to fire (LEX-07 unrun) -> every "no leak" reading in the slice
remains unqualified [UNKNOWN].

Calibration pattern (CALIBRATION.md): 10 of 17 recorded errors pushed toward a BIGGER claim; "no
measurement in the ledger has been overturned" -- all retractions were interpretations [HIST].

-------------------------------------------------------------------------------------------------
## 10. Research outputs

- roles/Lexis/ROLE.md (measured state, gates), SUMMARY.md (three depths), SESSION_2026-08-25.md,
  PLAN_2026-08-25.md, CONTROLS.md, EXTERNAL_REVIEW_REQUEST / REVIEW_REQUEST / REVIEW_RESPONSE (R1, R2).
- roles/Lexis/library_learning/{README, RETROSPECTIVE, SIDE_BY_SIDE, SOURCES, notes/PASS_01..08}.
- roles/Lexis/notes/{G0_FORGE_RATCHET, G1_ABLATION, G5_LEDGER, STEP1_CEILING_CLOSED, E9_INGESTION,
  G7_CHARON, PROVENANCE, CONGRUENCE_RECHECK} + result JSONs.
- roles/Lexis/handoff/LEXIS_G7_HANDOFF.md, ADMISSION_PROTOCOL.md, REVIEW_PACKET_CLOSEOUT_2026-09-01.txt,
  PROMPT_CLOSEOUT_2026-09-01.txt.
- roles/Lexis/archaeology/hct01_prior_art_2026-09-03/ (external review packet, causality audit,
  Kouvaris reconstruction assessment, cross-seat comparison, addendum, eight ledgers, recovered papers).
- roles/Lexis/CALIBRATION.md, BACKLOG_H0H5.md (LEX-01..26; XL LEX-18..24), STATUS.md.

-------------------------------------------------------------------------------------------------
## 11. Journals, TODOs, pivots, abandoned branches

- journal/2026-09-11.md only. Branches: origin/lexis/g7-closeout-2026-09-01 (merged; deletion pending
  per adoption receipt), local lexis/base-role-adopt-2026-09-11 (merged: a37988536 is an ancestor of
  HEAD) [IMPL].
- Backlog: STEP 3 bundle generator arms BLOCKED by the 09-01 closeout; generator-indistinguishability
  test proposed; second blind author (LEX-22) deferred; open operator decisions LEX-18..24 (program-
  wide authorship independence, ratify the seat, ratify G2/G5/G6, the one-line forge fix and owner,
  three 08-25 freeze recommendations).
- Pivot causes: E9 (external validity of every number), operator closeout (no consumer), HC-T01
  commission (forensics lane), D-25 (identity contingent on Apollo Task 2).

-------------------------------------------------------------------------------------------------
## 12. Lens inventory

L-X1. Vocabulary-closure lens (exact closure / dE vs dS / congruence precondition)
- Substrate: a fixed operator vocabulary over a finite task battery; organisms: programs.
- Phenomenon: whether a capability gap is expressive (vocabulary) or search (routing); whether a new
  primitive adds expressible function.
- Resolution: exact (exhaustive BFS) on small batteries; requires a congruence-valid state projection.
- Noise/limits: battery authorship co-adaptation; single-draw synth subsets; placement hazards
  invisible to the closure.
- Reusable: the dE/dS split, the congruence audit, G5/G6/G7 as admission gates for any primitive in
  any substrate (including evolved VMs).
- Toy-grade: the substrate (regex parsers on 120/42 NL tasks).

L-X2. Primitive-usage lens (G1 ablation census of a forge)
- Phenomenon: whether admitted primitives are load-bearing in consumers; decoration rates.
- Reusable: ablation census with dead-import vs called-but-inert split.

L-X3. Prior-art adjudication lens (HC-T01) -- method only, applicable to any "novel" claim.

-------------------------------------------------------------------------------------------------
## Open questions / unknowns

- Who owns the re-adjudication now that Apollo Task 2 never ran? No later ruling found in comms or
  DECISIONS [UNKNOWN].
- LEX-07 (cheat control for the leakage detector) never ran; anti-leakage confidence in the slice
  remains unqualified.
- Artemis R-20 claims a third blind author reproduces the E9 collapse; not verified here.
- Relevance to the emergence territory is indirect: Lexis's gates (authorship independence,
  permutation robustness, dE/dS, compute-matching) are rulers, not organisms or worlds.
