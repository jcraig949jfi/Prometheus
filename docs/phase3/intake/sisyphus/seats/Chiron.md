# Chiron -- seat dossier (Sisyphus crawl)

Seat: Chiron ("Engine Five / Chiron Developmental Engine (CDE) design and delegation")
Crawl date: 2026-10-01
Base SHA of the crawl worktree: 19299e06b (F:/Prometheus-worktrees/sisyphus-base-role, = origin/main)
Crawler: Sisyphus worker (Opus 5.5)

Coverage statement.
READ (from origin/chiron/base-role-adopt-2026-09-21, via git show): STATUS.md,
RESPONSIBILITIES.md, BACKLOG_H0H5.md, calibration/LEDGER.md in full;
CDE_THESIS_REVIEW_2026-09-21.md sections 1-8 in full and headings of 9-15;
prompts/2026-09-21_cde_thesis/CDE_THESIS.md (1003 lines: sections 1-4 and
17-19 in full, all headings); prompts/2026-09-21_synthesis_directive/
SYNTHESIS_DIRECTIVE.md (594 lines: purpose, sections II-III, all headings);
journal/2026-09-21.md (searched, key lines read). Branch log and diff stat
against origin/main. On main: roles/Achilles/RECONSTRUCTION_2026-09-30.md:91,
roles/Achilles/census/registry/seats_part4.json (Chiron row),
roles/Artemis/threads/sfe_retrospective/notes/C_engines.md:84,
roles/Odysseus/expedition/census/CENSUS_B_other.md:61,
roles/Artemis/challenge/prospective/PREREG.md:124,
roles/Artemis/backlog/INDEX.md:99, roles/Artemis/selftest/runs/R-12/REPORT.md
(in full), roles/Atlas/proposals/2026-09-21_prior_art_raid/EXPERIMENTS.jsonl
(F5/EV-10/MEM-1 records' status fields).
Existence search (the brief's central question): (a) all remote branches'
trees for paths matching chiron / cde / engine_five / enginefive / f5 (one
pass over every origin/* branch, 2026-10-01); (b) git log --all with
case-insensitive glob pathspecs for the same; (c) git log --all --grep for
"engine five|engine 5|chiron|CDE|F5-[0-9]|EV-10|voyager|portable organ";
(d) git grep on main for "F5-0|F5-1|Engine Five|ENGINE_FIVE|Chiron";
(e) local filesystem: F:/prometheus/roles, F:/Prometheus-worktrees/*,
/c/Prometheus on this host (SKULLPORT). NOT READ: CDE thesis sections 5-16
and 20-22 line by line; the synthesis directive sections IV-XVI line by line;
Atlas's ENGINE_FIVE_EXPERIMENT_LADDER.md body; Techne FIRST_RETURN (Voyager
fossil). The BUCKKEEP host's C:\Prometheus clone is not reachable from this
host and was not inspected. No holdout/secret paths opened.

---

## 0. Bottom line on implementation (the brief's question)

NO CHIRON IMPLEMENTATION EXISTS ANYWHERE THIS CRAWL CAN REACH. [IMPL]
- The seat's entire footprint is 4 commits on one unmerged branch,
  origin/chiron/base-role-adopt-2026-09-21 (481dbfe40, fe3140d66, 9e54a51ce,
  ad7b05339, all 2026-09-21 05:07-06:40 -0400, author "Jim Craig"), merge-base
  with origin/main 3e2c59c31. The diff vs main is 13 files, +2646 lines, ALL
  Markdown (roles/Chiron/* plus a 2-line roles/base-role/INHERITANCE.md row).
  No .py, .c, .json, config or data file. [IMPL, git diff --stat]
- No roles/Chiron/ on main; no chiron/ or cde/ code directory on any origin
  branch; no commit on any branch whose message names Chiron/CDE/Engine Five
  other than the four above plus Atlas 2c7a19adb (ladder, on main) and Techne
  1182e5328 (Voyager fossil). Path hits for "F5" on other branches are
  unrelated (Ensorain WTP-LM01 nuisance family "F5", Nestor F-R5-5,
  SerendipityFoundry D8 task family "F5", Crius run hashes). [IMPL]
- The seat says so itself: STATUS "PRODUCTIVE = documents only -- no
  experiment has been designed, preregistered, delegated, run or measured";
  review header "no CDE code, world, controller or run exists"; journal close
  "No code. No experiment. No packet sent." [HIST, consistent with IMPL]
- Independent confirmations on main: Artemis PREREG.md:124 "FR-050 ...
  Engine Five rungs not implemented"; Artemis R-12 REPORT "I found no existing
  implementation in the repo. The nearest engine branch
  (origin/aphrodite/compounding-2026-09-27) has no library-vs-context test";
  Achilles census: kind BRANCH_ONLY_SEAT, engines []; Artemis C_engines.md:84
  "design only, no engine". [HIST]
- Closest executed thing, NOT Chiron's: Artemis self-test run R-12
  (2026-09-28, report committed 970c4e18c on main) built a ~CPU-only, no-LLM
  version of Atlas rung F5-0 (persistence vs equal-information context) plus
  swap/transplant organ tests. Its code lives OFF-REPO at
  /home/jcraig/artemis-selftest/work/R-12 (f50.py, phase1.py, phase2.py,
  phase2bx.py; sha256 prefixes in the report) on host ubu002; only the report is
  committed. [HIST; code not inspected because not in the repository]
- Residual uncertainty: the BUCKKEEP clone (C:\Prometheus, off-fleet) could hold
  uncommitted work after 2026-09-21. Nothing on origin indicates any. [UNKNOWN]

---

## 1. Identity and purpose

Canonical name: Chiron. No aliases. Working names in its documents: "Chiron
Developmental Engine (CDE)", "Engine Five", "fifth engine"; Atlas's queue uses
F5-0..F5-6 and EV-10 for the same rungs. [HIST]
Created 2026-09-21 (481dbfe40, "new seat created and base role adopted
(charter PENDING)"). No formal charter file; governing documents are two
operator texts captured verbatim with MANIFESTs:
- CDE_THESIS.md (status "Concept / reconnaissance"; delivered with "Capture
  this. Review it. Add your thoughts" and "Capture this. Do not start on it."),
- SYNTHESIS_DIRECTIVE.md ("PROMETHEUS -- SYNTHESIS CAPTURE DIRECTIVE",
  program-wide, "NOT an implementation directive", "NOT a decision to
  standardize any interface"). Committed as 9e54a51ce "PROGRAM-WIDE" -- but
  only on this unmerged branch, so a program-wide directive is not on main.
  Other seats read it from the branch (Artemis D1_program.md:492 and R-12 cite
  it "@ 9e54a51ce"). [IMPL]
Pivots (all same day). (1) 481dbfe40: "subject named, build withheld".
(2) 9e54a51ce + ad7b05339: remit = DESIGN + DELEGATION OF CODING + SOME CODING,
"build the experiment, not the engine"; scaling forbidden before rungs 0-2
(F5-0, F5-1, F5-4) report. (3) comms de-escalated: operator ruled the host is
off the fleet network; delegation degrades to repo-borne packets with no
notification. [HIST]
Terminal state. ACTIVE per its own STATUS (2026-09-21), i.e. 10 days stale;
next action CHIRON-04 (gap note against Atlas's F5 records) never committed.
Not booted in comms (psycopg2 missing; ruled not a blocker). [HIST]
Host: BUCKKEEP (Windows, outside M1-M4), single clone C:\Prometheus, seat
branch checked out in the canonical clone (recorded deviation from
WORKING_CONTRACT s2). [HIST]
Relationships (designed, not exercised): Atlas (ladder owner, experiment IDs),
Techne (chemistry; Voyager fossil), Nyx (organ cutting; mechanism ledger),
Harmonia (claim adjudication), Crius (in-house prior art / negative control),
Bellerophon/SFE (candidate hosts). [INTENT]

## 2. Engine / system inventory

None. [IMPL] Designed-only object: the CDE minimal prototype (thesis s17):
"2-5 structurally related worlds, 1 persistent organism identity, simple
generalist controller, world adapters, persistent executable artifact store,
retrieval, artifact composition, adaptive task/world generator, full lineage +
telemetry, transplant / ablation harness". [INTENT]

## 3. Architecture (as designed; nothing implemented)

[INTENT throughout]
- Loop: generated/unfamiliar world -> persistent organism -> experience ->
  acquired competence -> persistent reusable artifact -> retrieval /
  composition / modification -> newly reachable behaviour -> new tasks and
  worlds (thesis s2; directive V).
- Organism: one persistent identity across worlds with a growing library of
  "skills" = {identifier, semantic description, executable payload, retrieval
  representation} (Voyager abstraction, thesis s3; directive VII "portable-
  organ hypothesis", explicitly NOT to be standardised or declared true).
- Search: Voyager-style writer/critic acquisition, automatic curriculum,
  competence-aware world generation (CDE-3); later artifact ecology with
  mutation/competition/decay (CDE-5) and weak communication ingredients
  (CDE-6).
- Pressure: task success in generated worlds; curriculum.
- Measurement: "Does retained reusable competence causally expand the set of
  experiences an organism can subsequently reach?" (s17), with the CDE-4 library
  ablation ("If competence does not collapse, it was not causally
  responsible") and the s19 engine-existence kill gate (if it reduces to "BEE
  player + Voyager library + adaptive selector" it is an experiment family,
  not an engine).
- Design-internal tension flagged by the seat: s6 (ingredients, not answers)
  vs s9 (deliberately high-prior puddle supplying answers); proposed
  resolution: s9 governs developmental rungs 0-4, s6 governs 5-6 (review s6).

## 4. World capability audit

No worlds exist. Designed scale is explicitly small ("The first CDE should be
unimpressive"; 2-5 related worlds; no SIMA 2, Genie 3, photoreal worlds, giant
model). Techne reports SIMA 2 / Genie 3 NO_PUBLIC_SOURCE (STATUS "standing
external state"), so the "generated interactive worlds" pillar has no donor in
hand. [INTENT/HIST]

## 5. Organism capability audit

No organism exists. As designed, competence would reside largely in an LLM
artifact writer; the seat's own review s5 names this the central confound
("did the lineage develop, or did the writer receive a better prompt?") and
specifies information-matched ablation, frozen writer, writer-only baseline and
contamination checks. Review s8: "Nothing in CDE dies" -- one persistent
identity, accumulation without selection; CDE-0..4 are N=1 anecdotes unless
replicated across independent lineages. [INTENT/HIST]

## 6. Search and pressure mechanism

Not implemented. Predicted collapse modes recorded in the review: CDE-3
Goodhart (generator finds where its agent succeeds; precedent Icarus tier
calibration, SW-2 blind-oracle discipline); compute accounting deciding CDE-0
before the science; "reachable" undefined. [HIST]

## 7. Measurement / ruler stack

Designed only: Atlas F5-0 record controls cited by the seat as binding --
matched information AND compute, shuffled-library control, held-out tasks
absent from every prompt and library entry, late-run swap test (RESPONSIBILITIES
s4); review adds a Crius-style blind-search negative-control arm and a frozen
hashed held-out world family for CDE-3. Primary endpoint per Atlas: "tasks
solved per unit compute on held-out tasks after a context reset" (calibration
ledger row 1). [INTENT]

## 8. Experiment inventory

No Chiron experiments. Outcome label for the seat: UNKNOWN (nothing run).
Related executed experiment elsewhere (for the synthesis, not credited to
Chiron):
- R-12 (Artemis self-test, 2026-09-28): F5-0-shaped test in a synthetic
  list-transformation world (14 primitives, 10 hidden 3-primitive motifs per
  world seed, 4 seeds, BFS controller, 20000 primitive applications per task).
  Reported: persistent library D solved 125/160 vs naive context arms 11-31 at
  K=30, but a context arm allowed to extract a library (BX) ties or beats D at
  K=300 (131 vs 123; loop 418 vs 428); swap to empty library collapses probe
  competence 50 -> 2; same-world transplant 28; foreign-world 1/160. Author's
  conclusion: the F5-0 kill rung is "badly posed" -- persistence reduces to
  compression per byte plus caching once the context arm may extract.
  Label: REPORTED NEGATIVE/NULL for "persistence as such"; REPORTED POSITIVE
  for "retained library carries competence in a closed loop". [RESULT-
  UNVERIFIED; code off-repo]
- Crius C0-C2 (Crius dossier territory) is the in-house experiment the review
  identifies as CDE's nearest prior art: four preregistered NOs. [HIST]

## 9. False-positive / false-negative archaeology

T1. Novelty claim in the seat's own review. Claim (fe3140d66): "the thesis raids
DeepMind and does not raid Prometheus" plus nine recommended gaps -> challenge:
Atlas's Engine Five ladder and 34-experiment queue (2c7a19adb, 04:00 -0400 the
same morning, an ancestor of Chiron's base) already contained most of them ->
correction: calibration/LEDGER.md row 1 -> status: framing withdrawn,
substance retained. Class: claimed a gap without reading a sibling seat's
proposals directory (same class as memory rule
"read_sibling_seat_commits_before_claiming_a_gap").
T2. Over-escalated blocker: missing psycopg2/comms called "the blocking
defect" -> operator ruling -> ledger row 2. [HIST]
T3. Forward-looking false-negative/false-positive risks stated in the review:
undefined "reachable" (Crius lost prediction P1 on the same term; ENUMERATE
solved 3/6 "out of reach" tasks); LLM-writer confound; Goodhart curriculum;
N=1 lineage. R-12 subsequently showed the F5-0 kill rung cannot kill unless an
extract-from-context arm is present -- a ruler-design false-positive risk that
would have favoured "persistence works". [HIST / RESULT-UNVERIFIED]

## 10. Research outputs

All on origin/chiron/base-role-adopt-2026-09-21:
- roles/Chiron/prompts/2026-09-21_cde_thesis/CDE_THESIS.md (+ MANIFEST):
  operator's Engine Five thesis, 22 sections, ladder CDE-0..6, kill gate s19.
- roles/Chiron/prompts/2026-09-21_synthesis_directive/SYNTHESIS_DIRECTIVE.md
  (+ MANIFEST): program-wide synthesis (puddles, anti-anthropomorphic rule,
  portable-organ hypothesis, cross-engine algebra organism x world x pressure x
  machinery x observer, repeated structural convergence, failure data first-
  class, "do not overfreeze").
- roles/Chiron/CDE_THESIS_REVIEW_2026-09-21.md: the seat's review (Crius as
  prior art; "reachable" undefined; LLM confound; s6/s9 conflict; Goodhart in
  CDE-3; nothing dies; compute accounting; mechanism identity test; dated kill
  gate).
- roles/Chiron/RESPONSIBILITIES.md, STATUS.md, BACKLOG_H0H5.md (CHIRON-01..09),
  calibration/LEDGER.md (2 rows), journal/2026-09-21.md,
  superseded/RESPONSIBILITIES_2026-09-21_pre_synthesis.md.
On main (others' work Chiron designs against): roles/Atlas/proposals/
2026-09-21_prior_art_raid/{ENGINE_FIVE_EXPERIMENT_LADDER.md, EXPERIMENTS.jsonl,
ATLAS_EXPERIMENT_TODO.md} (F5-0, F5-1, F5-4, F5-5 READY_FOR_DESIGN; F5-2, F5-3
NEEDS_DONOR; F5-6 and EV-10 IDEA, as recorded in EXPERIMENTS.jsonl at the
crawl base).

## 11. Journals, TODOs, pivots, abandoned branches

Single journal day 2026-09-21. Backlog CHIRON-03 (four operator design
questions: host engine SFE vs Bellerophon; lineages per condition; Crius
sandbox as negative control; who executes rung 0), CHIRON-04 (gap note),
CHIRON-05 (Crius constraints note), CHIRON-06 (preregister F5-0 with a frozen
definition of reachable-space expansion), CHIRON-07 (portable-organ packet to
Nyx/Techne), CHIRON-08 (overloaded organism.development field in Atlas),
CHIRON-09 (a reachable-space measure a lookup table cannot satisfy, for Harmonia
to attack). None done. The branch was never merged forward (Achilles
RECONSTRUCTION_2026-09-30.md item 7; comms #1227 Achilles -> Archaeon flags
"Chiron branch-only" for INHERITANCE.md). Effectively abandoned after one day.

## 12. Lens inventory

Lens L-CHI-A (prospective, unbuilt): "Developmental high-affordance puddle".
- Substrate: a persistent agent with an executable artifact library across a
  few related generated worlds.
- Phenomenon family: whether retained, addressable competence causally
  expands later reachable behaviour; portable organs; composition; transfer.
- Current resolving mechanism: none (design + Atlas ladder + R-12's off-repo
  harness as the only executed analogue).
- Resolution ceiling / noise: dominated, by the seat's own analysis, by the
  LLM writer confound, Goodhart curricula and N=1 lineages.
- Architectural limitation: no selection; no donor for generated worlds.
- Reusable: the kill-gate logic (s19), CDE-4 ablation, the review's control
  list, R-12's swap/transplant design.
- Toy-grade: n/a (nothing built). Unknown: everything empirical.

## Open questions / unknowns

1. Does the BUCKKEEP clone hold uncommitted Chiron work after 2026-09-21?
2. Should the "PROGRAM-WIDE" synthesis directive (9e54a51ce) be on main? It
   currently is not, yet it is cited by other seats as governing.
3. Were CHIRON-03's four design questions ever answered by the operator? No
   record.
4. Does R-12's off-repo code still exist on ubu002, and does any seat own it?
