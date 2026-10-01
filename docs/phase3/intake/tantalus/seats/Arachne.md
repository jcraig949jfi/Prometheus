# Arachne -- Phase 3 intake dossier

Seat: Arachne
Crawler: Tantalus (worker)
Tree SHA: 21a47402a (origin/main)
Date: 2026-10-01

Summary. Arachne is a population of "crawlers" written and run in a single
day, 2026-06-04, from an operator epiphany ("an army of crawlers that crawl
mathematical landscapes ... the fewer rules the better ... crawlers may emerge
a novel structure of organization") [INTENT] (quoted verbatim in
roles/Arachne/ARCHAEOLOGY_2026-09-11.md A1-A2). What was built is a frontier
walker over six database/code "landscapes" (OEIS, LMFDB elliptic curves,
mathlib4, a sympy call graph, knots, groups) whose edges are typed by a small
set of hand-chosen relations ("shares_prefix", "isogenous", "same_order", ...)
each carrying a hard-coded constant "null_p" [IMPL]
(agents/arachne/landscapes/*.py); a swarm loop with death, branching by
ruleset mutation, a population floor and a "feral" landscape-hopper [IMPL]
(agents/arachne/swarm.py, crawler.py); a lexical and a computation-grounded
cross-landscape joiner [IMPL] (join.py, operational.py); and a separate
"damage-algebra" coverage script using OEIS as an exact oracle [IMPL]
(damage.py). It ran once by hand for 700 ticks (21,209 edges, 5,621 nodes)
[RESULT-UNVERIFIED] (roles/Arachne/archive/run_2026-06-04/README.md). On
2026-09-11 the seat was reactivated for "archaeology as experiment" on the
frozen specimen, preregistered two readouts and concluded EMERGENCE NOT EARNED,
branching was a "death rattle", and the feral crawler died of an implementation
defect [RESULT-UNVERIFIED] (roles/Arachne/ARCHAEOLOGY_AS_EXPERIMENT_2026-09-11.md).
No crawl has run since June.

## 1. Identity, charter and pivots

- agents/arachne/ (10 commits, all 2026-06-04 except 2026-09-11 instrumentation
  4ebb1643c); roles/Arachne/ (8 commits, all 2026-09-11) [IMPL] (git log).
- First code commits 7a29f8583 and f676638fc (2026-06-04). Seat folder
  created 58be0d237 (2026-09-11) "a seat spun up 2026-06-04 and never seated"
  [IMPL].
- Founding doc: pivot/math_crawlers_epiphany_2026-06-04.md (operator words
  verbatim) [CLAIM; cited by the archaeology, not opened by this crawl].
- Operator assignments: A1 mission, A2 five crawlers + loop + three-factor
  fitness, A3 widen/judge/harvest ("ALL THREE, per James", f62343df9), A4
  damage-algebra test (a2e5d83bd, 3b9d9ed15), A5 reactivation 2026-09-11
  [CLAIM] (ARCHAEOLOGY A1-A5).
- 2026-09-11 ruling ACTIVE for archaeology-as-experiment only: "Do not
  interpret ACTIVE as authorization to restart the crawlers"
  (roles/Arachne/prompts/2026-09-11_ruling_active/OPERATOR_RULING.md) [CLAIM].
- Pivot 2026-06-23 disposition plan names Arachne via Polyhymnia row 15
  [CLAIM] (ARCHAEOLOGY sources list).
- Host: M1 (STATUS) [CLAIM]. Recommendation at close: "C. METABOLIZE"
  (419b2db0b) [CLAIM].

## 2. Engine/system inventory

Engine A1: ArachneSwarm (crawler population).
- Paths: agents/arachne/crawler.py (Ruleset, Crawler), swarm.py (20 KB,
  population, branching, floor, watcher, --loop/--once, overrides),
  fabric.py (append-only edge store), landscapes/{oeis,lmfdb,mathlib,
  algolib,pgtable,_pg}.py, productivity.py (added 09-11) [IMPL].
- State: fabric/edges.jsonl, state/swarm_state.json, population.json,
  lineage.jsonl, gitignored; archived with hashes in
  roles/Arachne/archive/run_2026-06-04/ (MANIFEST.md) [IMPL].
- Deps: psycopg2 to local Postgres (prometheus_sci.analysis.oeis 394K rows;
  LMFDB; topology.knots 12,965; algebra.groups 544,831), a mathlib4 checkout
  (8,100 .lean files), sympy introspection [IMPL/RESULT-UNVERIFIED]
  (landscape census 2026-09-11).
- Execution: hand-run loop; one run 2026-06-04 ~06:20Z-11:21Z, 700 ticks,
  in the canonical checkout [CLAIM] (archive README).
Engine A2: Joiners. join.py (Rosetta token join; 1,870 rosetta edges in the
archive), operational.py (OperationalJoiner: computes 16 terms of a sympy
integer function and looks it up in OEIS; 11/12 functions recover their
canonical A-number) [IMPL; result RESULT-UNVERIFIED] (39cf9ea2e).
Engine A3: traverse.py (holdout judge, harvest) [IMPL].
Engine A4: damage.py, damage-algebra coverage test against OEIS [IMPL].
September instruments: roles/Arachne/science/{specimen.py (verifies six
archive hashes before loading), branch_fitness.py, emergence.py,
feral_autopsy.py, harvest_audit.py, census.py} + 2 test files (21 tests)
[IMPL].

## 3. Code architecture and dataflow

Per tick: each live crawler picks a landscape (its own, or random if
`hop`), reseeds the frontier on cadence, pops a node (bfs/dfs/random), calls
adapter.expand(node) which runs SQL/parse lookups returning (dst, op, null_p)
triples, drops triples with null_p above `novelty_floor`, appends up to
`max_neighbors` edges to the shared fabric, pushes destinations onto its
frontier [IMPL] (crawler.py step()). Fitness = mean over a 16-step window of
(2*new_nodes + new_edges) * (1 - 0.6*mean_null_p) [IMPL] (crawler.py
fitness(), _after()). Death on 12 zero-progress steps or 8 errors [IMPL].
Swarm branches near-death crawlers by mutating one ruleset knob
(max_neighbors, novelty_floor, frontier_mode, hop, reseed_every) [IMPL]
(Ruleset.mutate). Joiners run on the fabric every few ticks.

Code-vs-doc disagreements:
- "null-scored edges" / "would a random crawler make this as easily" [INTENT]
  vs. null_p is a constant per relation type set by hand (oeis shares_prefix
  0.2, similar_growth 0.6; lmfdb isogenous 0.15, same_conductor 0.55;
  pgtable same_determinant 0.40 ... same_exponent 0.60) [IMPL]
  (landscapes/oeis.py:74,86; lmfdb.py:68,73; pgtable.py:82-96). No null is
  computed; multiplicity is ignored (CALIBRATION row 6: top hubs are one
  group order with 544,831 groups behind it) [CORRECTION].
- "Branch strategies near death ... explore new linkages" [INTENT] vs. first
  implementation branched on low fitness so the dying reproduced most
  (8 of 12 crawlers mathlib) [CORRECTION] (CALIBRATION row 3; patched
  9cb4602bb with 70% escape to least-populated landscape).
- Feral hopper: `hop` re-draws the landscape each step while the frontier
  is one mixed queue, so nodes from one landscape are expanded with another
  landscape's adapter (expand returns [] on prefix mismatch, e.g.
  oeis.py expand: `if not node.startswith("oeis:"): return []`) [IMPL];
  the seat's autopsy names this the cause of death (p ~ 1/6 progress per
  step) [RESULT-UNVERIFIED] (1bf5be9fb).

## 4. Claimed computational primitive vs actual mechanism

- Label: "crawlers that create their own data fabric"; "emergent organization";
  "tree of life" evolution of rulesets [INTENT].
- Smallest actual mechanism: a BFS/DFS frontier over a database whose edge
  relations are fixed SQL equality/closeness queries; selection over five
  scalar knobs of the walk [IMPL].
- In principle: a typed multigraph over math objects whose topology reflects
  which hand-chosen invariants coincide [CODE-INFERRED]. The crawler cannot
  invent a relation; "the fewer rules the better" is contradicted by the fact
  that all relations are authored in the adapters [CODE-INFERRED].
- Phenomenon the ruler sought: (a) cross-cutting communities, (b) stable
  load-bearing structure, (c) candidate structure beyond nulls; plus
  "branching produces fitter children" [INTENT] (PREREG_EMERGENCE_v0.md,
  PREREG_BRANCH_FITNESS_v0.md).
- Could the organism perform it: the walk can only rediscover the invariant
  classes that the adapters encode; communities ARE those classes
  (within-landscape NMI 0.88-0.99) [RESULT-UNVERIFIED] (STATUS).
- Ruler vs shortcut: the September readouts used class-constrained, LIMIT-n,
  degree-preserving and pure-star nulls; every statistic sat inside or
  between cheaper nulls [RESULT-UNVERIFIED]. Three frozen gates were
  mis-specified (CALIBRATION rows 8-10) [CORRECTION]. The June judge had no
  positive or cheat control [CLAIM] (ARCHAEOLOGY B5).

Engine A4 (damage algebra): label "Noesis's nine damage operators exhibited
computationally" [CLAIM] (a2e5d83bd). Mechanism: the script applies a
designer-chosen transform to a known sequence (e.g. Catalan), and asks whether
OEIS lookup recovers the intended A-number [IMPL] (damage.py). The commits
themselves state "constructed break-then-repair (proves realizability +
detectability, not wild emergence)"; DISTRIBUTE was "realized" by choosing a
Beatty sequence floor(n*phi) -> A000201 after it first failed [CLAIM]
(3b9d9ed15). This is an authored-instance demonstration; it cannot fail for
an operator whose instance the author can construct [CODE-INFERRED].

## 5. Representation/state architecture

Edge = {src, dst, op, landscape, crawler, born_at, null_p} [IMPL]
(archive README). Node ids are strings "oeis:A000045", "lmfdb:ec/...",
"mathlib:<token>", "algolib:<sympy name>" [IMPL]. Crawler state: frontier
deque, visited set, 16-step progress window, frontier-hash loop detector
[IMPL]. No embedding, no learned representation.

## 6. Organism/player architecture

Organism = Ruleset of 7 fields (landscape, max_neighbors 2-32,
novelty_floor 0.50-0.99, hop bool, frontier_mode, reseed_every 10-120, seed)
[IMPL] (crawler.py Ruleset). Policy is fixed code; only these knobs vary.
Lifetime counts in the run: 82 branch, 124 death, 42 floor revivals [IMPL]
(archive lineage.jsonl summary in README).

## 7. World/environment architecture

Six landscapes backed by real databases (sizes above). Scale is real at the
data level (hundreds of thousands of objects) but the crawl touched 5,621
nodes [RESULT-UNVERIFIED]. The environment is static; nothing the crawler
does changes it [IMPL].

## 8. Search/training/adaptation mechanism

Mutation of one knob per branch; selection by death (stall/error) and by
branching at fitness trough; population floor revives gen-0 crawlers
[IMPL]. Collapse modes recorded: inverted selection (patched), floor reviving
the same dead mathlib crawlers repeatedly (mathlib-0-101, -122, -124, -127)
[RESULT-UNVERIFIED] (CALIBRATION row 4), OEIS monoculture (the 2*new_nodes
weighting was added against it) [IMPL comment, crawler.py _after].

## 9. Measurement/ruler stack

June: global cross-pair reachability vs degree-spread null (judge 1,
mis-specified: verified joins lowered reach 0.167 -> 0.092) [CORRECTION]
(CALIBRATION row 1); traverse.holdout held-out bridge recovery
(real_closer_frac 0.088, "fabric is bridge-only") [RESULT-UNVERIFIED]
(f62343df9); harvest (5 verified anchors, 58 void targets) [RESULT-UNVERIFIED].
September: branch-fitness readout (C1 63/63 biased by construction; C2
age-matched 30/43, CI [0.549, 0.814]; vs fresh default births 35/68, CI
[0.40, 0.63]); emergence readout with four nulls; feral autopsy; harvest
audit [RESULT-UNVERIFIED] (ledgers/*.json; ARCHAEOLOGY_AS_EXPERIMENT s2).
Reconstruction control: the recomputed fitness reproduces 82 logged parent
fitness values within 0.10 [RESULT-UNVERIFIED].

## 10. Baselines and controls

June: none beyond the degree-spread null [CLAIM]. September: age-matched,
contemporaneous and default-birth controls for branching; class-constrained,
LIMIT-n, degree-preserving rewiring, pure star nulls for emergence
[RESULT-UNVERIFIED]. Single-crawler ablation and discipline-partition tests
never ran [CLAIM] (ARCHAEOLOGY B5).

## 11. Historical experiment campaigns

C-A1 June swarm run. 2026-06-04. Q: does a low-rule crawler population
build an organized fabric. Organism: rulesets; world: 6 landscapes;
pressure: death/branch; measurement: judge 1, holdout judge; scale 700 ticks,
21,209 edges. Reported: "Emergent organization NOT beyond-null yet"
(f62343df9). Later: emergence NOT EARNED (419b2db0b). Paths: agents/arachne/,
archive/run_2026-06-04/. Label: REPORTED NEGATIVE/NULL.

C-A2 Lexical (Rosetta) join. 2026-06-04 de99a104a. Reported: bridges on
homonyms, lift -0.067. Label: REPORTED NEGATIVE/NULL.

C-A3 Operational join. 2026-06-04 39cf9ea2e. Reported: 11/12 sympy functions
recover canonical OEIS sequence. Label: REPORTED POSITIVE (as a lookup
verification; it is a known-identity check, not discovery).

C-A4 Damage-algebra coverage. 2026-06-04 a2e5d83bd, 3b9d9ed15. Reported: 9/9
operators exhibited, 8/9 canonical. Label: REPORTED POSITIVE (authored
instances; see section 13).

C-A5 Branch-fitness readout. 2026-09-11 prereg 16dba61d8, readout dbd5345c0.
Reported: children beat parents at same age but not fresh births; "mutation
decorative". Label: REPORTED NEGATIVE/NULL.

C-A6 Emergence readout. 2026-09-11 prereg dbd5345c0, result 419b2db0b.
Reported: not earned; gates (a)-(c) mis-specified. Label: REPORTED
NEGATIVE/NULL (with INSTRUMENT FAILURE in three gates).

C-A7 Feral autopsy. 2026-09-11 1bf5be9fb. Reported: died of implementation
defect; "uninformative about fewer rules". Label: INSTRUMENT FAILURE.

C-A8 Harvest audit. 2026-09-11. Reported: rule unrecoverable; 22 of 29 names
already state a rule; no consumer. Label: REPORTED NEGATIVE/NULL.

## 12. Reported results and later corrections

- Judge 1 "usefulness" -> verified edges reduced it -> judge mis-specified ->
  replaced by holdout (still no positive control) [CORRECTION].
- "Feral is the live test of fewer rules" -> n=1, died tick 28 -> defect ->
  "untested, not falsified" [CORRECTION] (CALIBRATION row 5).
- "Branch near death" -> inverted selection -> patched -> branching readout
  null on the fresh-birth comparison [CORRECTION].
- Emergence prereg gates: NMI < 0.5 attainable by any refinement (~0.46);
  STABLE unreachable (6.8 of 75 expected by chance); CANDIDATE between two
  nulls -> readings kept, dispositions annotated [CORRECTION].

## 13. False-positive archaeology

- Damage algebra "9/9 exhibited": the experimenter chose transform and target;
  first run also showed TRUNCATE/QUANTIZE "silently absorbed by the matcher's
  own preprocessing" (a2e5d83bd) [CLAIM]. Realizability by construction.
- Prereg gate (a) would have read CROSS_CUTTING on any refinement (row 8).
- Constant null_p makes a shared invariant with half a million objects look
  as "specific" as a rare one (row 6).

## 14. Likely false-negative regimes

- Feral hopper killed by the frontier/adapter mismatch, not by its rules.
- One run, 700 ticks, 5,621 nodes: fabric density too low for redundant
  cross-domain paths (holdout judge "bridge-only at this density").
- Population floor recycled dead crawlers, wasting slots.
- The organism cannot express a new relation, so "novel organization" is
  out of reach regardless of run length [CODE-INFERRED].

## 15. Phase 3 audit (engine A1 swarm; A4 noted)

a. Representation richness: hierarchy NO; compositional structure NO (edges
   are pairwise equality relations); variable binding NO; memory PARTIAL
   (visited set, 16-step window); recurrence NO; counterfactual state NO;
   latent variables NO; temporal abstraction NO; spatial abstraction NO;
   reusable substructure NO; dynamic routing PARTIAL (landscape hop, frontier
   mode); self-reference NO.
b. Reasoning opportunity: none beyond graph expansion by fixed queries; the
   environment rewards coverage (new nodes), which is running-count control.
c. Shortcut surface: fitness rewards new nodes x (1 - constant null_p), so a
   crawler wins by sitting on a low-null relation with large fan-out
   (group order, conductor hubs) [CODE-INFERRED].
d. Ruler resolving power: September nulls are adequate to reject emergence;
   June judges were not; branching readout limited by 20-63 eligible events.
e. Scale: 6 landscapes; ~12 concurrent crawlers; 700 ticks; 21,209 edges;
   5,621 nodes; 82 branch events; one run.

## 16. Research reports and substantial documents

- roles/Arachne/ARCHAEOLOGY_2026-09-11.md -- assignments A1-A5 and June queue
  classified.
- roles/Arachne/ARCHAEOLOGY_AS_EXPERIMENT_2026-09-11.md -- verdict matrix,
  METABOLIZE recommendation.
- roles/Arachne/prereg/PREREG_BRANCH_FITNESS_v0.md, PREREG_EMERGENCE_v0.md.
- roles/Arachne/CALIBRATION.md -- 11 self-corrections.
- roles/Arachne/REVIEW_PACKET_2026-09-11*.md -- two review packets.
- roles/Arachne/archive/run_2026-06-04/harvest_2026-06-04.md -- June harvest.

## 17. Journals/TODOs/backlogs/pivots/abandoned branches

roles/Arachne/journal/2026-09-11.md; BACKLOG_H0H5.md (ARACHNE-01..34; next
ARACHNE-32 joiner fixtures, -34 matched C4; -31/-33 await operator); prompts
for reactivation and ruling; comms report 74 to Archaeon (f900dfc93).
Abandoned: crawl continuation; tests (a) partition, (b) ablation, (c)
degree-preserving null as designed in June.

## 18. Dependencies on other engines and seats

Noesis (damage operators source), Polyhymnia (disposition row), Ergon
(DB diagnosis 06-23: LMFDB host moved), Archaeon (report recipient),
Evidence Wiki credential resolver (09-11 census) [CLAIM]. Databases:
prometheus_sci, LMFDB mirror [IMPL].

## 19. Scaling limitations

All relations are SQL lookups with 4 s statement timeouts [IMPL] (oeis.py);
scale is bounded by authored relations, not compute. Single-process loop.

## 20. Lens potential for Phase 3 (descriptive)

Substrate: typed graph over real math databases. Organisms: 7-knob walk
rulesets. Pressure: survival + coverage. Phenomenon family: emergent
organization of a knowledge graph. Resolving mechanism: null-model graph
statistics (September). Ceiling: rediscovery of adapter-encoded classes.
Reusable: landscape adapters with loud failure; OperationalJoiner
(computation-grounded bridges); frozen specimen with hash-verifying loader;
the September null suite. Toy-grade: constant null_p, single run, feral
hopper. Unknowns: behaviour with computed multiplicity-aware nulls, with
denser fabric, or with crawler-proposed relations.

## 21. Open questions / coverage gaps

Read: crawler.py in full, heads of join.py, operational.py, damage.py,
landscapes/oeis.py, null_p constants across adapters, STATUS, ARCHAEOLOGY
(A, B1-B6), ARCHAEOLOGY_AS_EXPERIMENT s0-s2, CALIBRATION, archive README,
four June commit messages. Not read: swarm.py, traverse.py, fabric.py bodies;
the September science scripts; preregs in full; review packets; journal;
ledgers JSON; founding pivot doc; edges.jsonl (not opened).
