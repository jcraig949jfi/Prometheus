# Dossier G8(d) -- the forge lineage (COSPLAY CONTROL)

forge/ + agents/hephaestus/ + agents/nous/ + hecate/ (seats Hephaestus, Nous, Hecate)

VERDICT: SALVAGE_COMPONENT -- no LLM-written "reasoning tool" in this lineage is more than a
regex/keyword/NCD scorer keyed to the trap templates, and the tiering does not compose; what
survives is the instrument layer (mechanism-knockout ablation, behavioural answer-vector
distance, the counterfeit-museum catalogue, Hecate's control-first world probes with
cheat controls) and the 25 hand-written forge_primitives as typed seed operators.

Auditor: Hestia audit worker (fork), 2026-10-06. Read-only. Rubric: AUDIT_PLAN.md s2-s4.
Conflict of interest: same model family as most forge tool authors and as Hecate's generators.

---------------------------------------------------------------------------------------------
## 0. Identity

Worktree C:/Prometheus-worktrees/hestia-boot-2026-10-06, HEAD 3fed30ac9 (origin/main merge).

| component | path | git files | seat docs |
|---|---|---|---|
| T1 forge (LLM tool generator) | agents/hephaestus/ | 17,364 | roles/Hephaestus/ (49) |
| T2/T3 tiers + "Iron Laws" rebuild | forge/ | 1,124 | (PipelineOrchestrator, retired) |
| concept-triple generator | agents/nous/ | 56 | roles/Nous/ (8) |
| triplicate deep-search funnel | hecate/ | 590 | roles/Hecate/ (76) |

agents/hephaestus/ enumerated by directory (git ls-files, grouped): humanreadable/ 11,351
(1,957 .py; per-triple narrative + tool), scrap/ 2,648 (1,130 .py), scrap_staging/ 1,261
(630 .py), forge/ 734 (368 .py = v1 library), forge_v4/ 375 (358 .py), forge_v5/ 367 (344),
forge_v3/ 333 (302), forge_v7/ 65, forge_v2/ 50, src/ 37, forge_v9/ 15, tier_specialists/ 8 .py,
runs/ ~100, ablation/, journal/, code_from_claude/.

Sampled stratified (one tool per stratum, index chosen by position not by name):
- forge/embodied_cognition_x_hebbian_learning_x_neuromodulation.py (v1, file #100)
- forge_v5/mechanism_design_x_free_energy_principle_x_type_theory.py (v5, #200)
- forge_v9/embodied_cognition_x_mechanism_design_x_property_based_testing.py (v9, #7)
- forge_v3 #150, forge_v7 #30 (frame_e_constructive_reasoner.py), scrap #500: listed and sized,
  NOT read line by line; covered instead by the whole-population static scans in s2.
- tier_specialists/r2_chain_v2.py (whole), src/composer.py (engines + aggregator),
  src/forge_primitives.py (function list + bat_and_ball), src/trap_generator.py (whole
  generator list + all fixed-answer sites), src/test_harness.py (gate, lines 272-355),
  src/validator.py (gate list), src/hephaestus.py 689-720 (behavioural fingerprint).
- forge/: README.md, thresholds.py, tester.py 410-455, runner.py header, all 203 verdicts/*.json
  (tallied), v2/hephaestus_t2/forge/*.py and v3/hephaestus_t3/forge/*.py (import lines, all 11),
  v2/hephaestus_t2/forge/_t1_parsers.py header, 171 v2 scrap tools (import scan).
- agents/nous/src/: concepts.py header, nous.py (function list, sampling 209-300),
  scorer.py assess_novelty 126-160.
- hecate/: all 16 programs/HT-*/program.json (verdict fields, candidateEngines), schema.py
  verdict vocabulary, HT-321a8fd8e0 file list and evidence summary.
- Seat documents: roles/Hephaestus/{ROLE.md 1-140, ABLATION_CARD_2026-08-19.md,
  CALIBRATION.md, DISPOSITION_LEDGER.md, STATUS.md, REVIEW_PACKET_2026-09-19_xpol_small_set.txt
  1-110}, agents/hephaestus/{README.md 1-120, STATUS.md 1-80}, roles/Nous/STATUS.md,
  roles/Hecate/{STATUS.md, REVIEW_PACKET_2026-09-30_first_cycle.txt (whole),
  calibration/LEDGER.md, harvest_w2/INV_J 1-25 + grep}, Hecate charter lines 105-125.
- Committed data tallied: agents/hephaestus/ledger.jsonl (6,661 rows),
  agents/hephaestus/ablation/knockout_2026-08-20.json, forge/verdicts/*.json (203).

What was NOT read: humanreadable/ narratives (only counted), scrap_staging/, runs/,
forge_v4 individual tools, most of hephaestus.py (2,757 lines), trap_generator_extended.py
and trap_generator_tier2.py bodies (only their entry points), forge/amino_acids/,
forge/ARCHITECTURE_T2_T3.md, forge/DESIGN_cluster_eval.md, roles/Hephaestus/
DESIGN_REVIEW_2026-09-01_external.md and META_ASSESSMENT_2026-08-12 (cited only via
DISPOSITION_LEDGER/CALIBRATION), apollo/src/hephaestus_ops.py, hecate world.py/evaluate.py
code for any world, hecate meta/ and gravity/ code, hecate/alien/. No engine was run; the
only computations were static scans (AST hashing, grep counts, JSON tallies) and the
combinatorics in the scratchpad script forge_calc.py.

---------------------------------------------------------------------------------------------
## 1. Mechanism (code, not prose)

### 1.1 The pipeline as built

Nous samples a triple of the 95 hand-written concepts (agents/nous/src/concepts.py:14 onward,
"95 concepts" docstring line 4) with cross-field bias (nous.py:209-300; random.choices,
nous.py:262,282) and asks an LLM to rate it; "novelty" is decided by substring counting of
words like "novel", "original", "unexplored" in the reply (scorer.py:126-160). Hephaestus
turns a triple into an LLM prompt (8 rotated "frames"), the LLM writes a class ReasoningTool
with evaluate(prompt, candidates) -> ranked list and confidence(prompt, answer)
(agents/hephaestus/README.md "Gate 3"). Gates are syntax / import allowlist / interface /
runtime (src/validator.py:26,35,56,87) plus the trap battery (src/test_harness.py:272-305),
which passes a tool iff it strictly beats an NCD (zlib) baseline on accuracy OR calibration
and loses on neither (test_harness.py:300-305). A second "novelty gate" admits any tool with
min source-NCD > 0.85 to the library and accuracy >= 20% (README "Gate B").

Every tool is a multiple-choice SCORER: it ranks supplied candidate strings. It generates
nothing. The seat itself established this is why no independent generative oracle can grade it
(ABLATION_CARD_2026-08-19.md s3).

### 1.2 What the "reasoning tools" actually compute (sampled)

- v1, embodied_cognition_x_hebbian_learning_x_neuromodulation.py. "Hebbian learning" is
  token-set overlap: base_score = |prompt_tokens & cand_tokens| / |prompt_tokens| (lines 83-84);
  "acetylcholine" adds 0.5 per logic word in the candidate (88-93); "negation consistency" adds
  0.2 if both contain a negation word (97-102); "numeric constraint propagation" is a 0.2/0.3
  bonus if the last number in the prompt relates to the candidate's number and the word "less"
  or "greater" appears (124-132); "serotonin exploration" is +0.05 for short candidates
  (140-142); NCD fallback when all scores are zero (162-169). No state persists between calls;
  nothing is learned; the neuroscience vocabulary is entirely in comments (docstring 7-26).
- v5, mechanism_design_x_free_energy_principle_x_type_theory.py. The scoring core _cat_score
  (131 onward) is a cascade of regexes that match the trap TEMPLATES by surface form: "is X
  larger than Y" (133-137), "pound of ... pound of ... heav" (144-146), bat-and-ball "cost ...
  more" (147-152), "coin ... flip ... heads" (153-156), "overtake ... 2nd place" (159-161),
  "0.999 ... repeating" (162-163), pigeonhole "people ... months" (164-168). The part named
  after the concept triple is _secondary (396-398): count of the words type/kind/class/category/
  set/group/form in the candidate, capped, times 0.08, then weighted x0.1 inside evaluate
  (409). Maximum contribution of "mechanism design x free energy x type theory" to a score:
  0.008. The triple label is a costume.
- v9, embodied_cognition_x_mechanism_design_x_property_based_testing.py. Imports 13 hand-written
  forge_primitives (lines 5-8) and calls them correctly (bat_and_ball, fencepost_count,
  modular_arithmetic for weekday offsets, check_transitivity); routing into them is again
  template regex (26-60). It also hard-codes the modus-tollens trap answer: any prompt
  matching "if ..., ... not ... is/does" returns "No" at 0.90 (line 57; also lines 94, 97). That is the
  trap generator's constant answer (trap_generator.py:108), not an inference.
- Hand-composed 9-engine tool, src/composer.py. ComposedReasoningTool (871-935) is a weighted
  vote of 9 keyword engines; any engine scoring >= 0.9 is DECISIVE and short-circuits the vote
  (912-917). ProbabilisticFallacyEngine (501 onward) returns 0.95 if the substring "no" or
  "not necessarily" occurs in the candidate when the prompt has "All X are Y" plus "are all"
  (519-529); CausalEngine (811-865) returns 0.9 for any candidate containing "cannot" or "no"
  whenever the prompt contains "correlat|associat|linked|related" and "does" (826-831). The
  substring test "no" in cand_lower also fires on "not", "none", "know", "cannot". These are
  answer-phrase lookup tables written against the battery's fixed answers.
- tier_specialists/r2_chain_v2.py, the "R2 forward chaining" specialist. known_facts is a set
  of regex 2-tuples (lines 13, 24); rules are (premise_string, conclusion_string) (25); the
  closure loop tests premise in known_facts (30), which compares a str to a set of tuples and
  can never be true, so no rule ever fires; the candidate score is candidate in known_facts
  (38), again str vs tuples, so every candidate scores 0 on every prompt. The specialist named
  as the keystone R2 op is, in this file, a constant function. (Not re-executed; this is a
  static type reading of lines 13-38. r2_chain_tracker.py, the version Apollo decomposed into
  apollo/src/blackboard_ops_r2.py, was not read.)
- forge_primitives.py (25 functions, lines 26-529): real, small, correct algorithms --
  solve_sat (26), modus_ponens closure (47), check_transitivity (68), topological_sort (200),
  counterfactual_intervention on a DAG (233), solve_constraints (280), solve_linear_system
  (364), track_beliefs / sally_anne_test (440, 461). Hand-written, not LLM-forged. They are the
  only components in the lineage that compute a relation rather than match a phrase.

### 1.3 Does forge's tiering compose? (forge/README.md: "each tier's tools become next tier's
primitives")

No, by the import graph:
- All 5 T2 tools (forge/v2/hephaestus_t2/forge/t2_*.py) import `_t1_parsers.try_standard`
  (e.g. t2_simpson_paradox_solver.py:17) -- a 251-line hand-written regex file whose own
  docstring says it handles "numeric comparison, bat-and-ball, pigeonhole, transitivity,
  modus tollens ..." (_t1_parsers.py:1-5). It is not a forged T1 tool. They also import
  forge_primitives_t2 (t2_simpson_paradox_solver.py:18) and fall back to zlib NCD (88-90).
- All 5 T3 tools import `_t1_parsers` (t3_*.py lines 7-23); one imports another T3 tool
  (t3_ensemble_meta_deliberator.py:21). Zero import any T2 tool.
- 171 T2 scrap tools: 0 load any agents/hephaestus/forge*/ tool (grep for forge_v / _x_ module
  imports / spec_from_file_location: 0 hits); they import forge_primitives and
  forge.amino_acids.
So the "evolutionary ratchet" is: T1 = LLM text; T2/T3 = new LLM text that calls one shared
hand-written parser plus hand-written primitives. No tier-N artifact is a primitive of tier
N+1. The forge's own cross-tier matrix (README.md lines 120-126: T1 tools 0% on T2 battery,
T2 tools 1% on T3 battery, each tier 100% on its own) is the signature of each tier fitting
its own battery, not of a ratchet.

### 1.4 The rebuilt forge/ "Iron Laws" tester (2026-04)

forge/runner.py separates Builder (no battery access) from Tester (docstring 1-11).
forge/tester.py computes a per-primitive ablation with load_bearing = |delta| >=
min_ablation_impact (0.20) (tester.py:161) but the verdict (437-451) uses only ablation_ok,
which checks that no primitive exceeds 60% of the ablation budget (411-420). If every delta is
0, budget shares are 0 and ablation_ok stays True. load_bearing is computed and never read.
forge/thresholds.py:3 says "DO NOT MODIFY after first evaluation run" while its own rationale
(lines 6-16) records lowering pass_threshold from 0.50 to 0.40 because 0.50 "filtered ALL 75+
candidates" and "0.40 admits 5 tools". A frozen gate moved to admit the population.

### 1.5 Hecate (hecate/)

A preregistered funnel over the historical Nous/Hephaestus triples: Pass 0-3 (fresh model
writes interpretations, mechanisms, lenses, executable worlds), probes with treatment /
control / null twin / positive control / CHEAT control over >= 5 seeds with outcome decided
in code, Pass 4 adversarial attack (replication, trivial-explanation ORIG, alternative ALT),
a meta experiment (triple vs pair vs single vs ordinary prompt). Verdict vocabulary
schema.py:21-24 (EXPAND / PARK / FOSSIL / REJECT; KILL_VERDICTS = FOSSIL, REJECT) and the
charter's terminal ENGINE / FOSSIL / REJECT (charter line 116). Validator enforces that
PROMISING/EXPAND needs a passing preregistered predicate on committed rows
(REVIEW_PACKET_2026-09-30 s3).

---------------------------------------------------------------------------------------------
## 2. Evidence (tiered)

OBSERVED (committed rows / files examined this session)

E1. Mechanism monoculture, whole population. Of 1,502 .py tools in forge/ + forge_v2..v9,
    1,437 (95.7%) import zlib (NCD) and the large majority call re.search/findall/match
    (static grep): forge 322/368 zlib, v3 292/302, v4 352/358, v5 343/344, v7 65/65, v9 15/15.
E2. Verbatim cloning. AST-hashing every function body: the share of function-body lines that
    sit in a body byte-identical across >= 5 files is v1 0.5%, v3 81.8%, v4 93.2%, v5 96.2%,
    v7 11.4%, v9 0.8%. In v5, 60 of 61 files with a _cat_score have the identical function
    (hash 22cfa565); only the 0.008-weight _secondary differs. v4/v5 are one tool in ~700
    filenames. (v1 and v9 are freshly LLM-written but E1 shows the same ingredients.)
E3. T1 forge ledger (agents/hephaestus/ledger.jsonl, 6,661 rows): forged 385 / scrap 6,276;
    2,861 rows (43%) are api_call_failed, i.e. instrument state, not subject outcome (the
    seat's DISPOSITION_LEDGER row "ledger.jsonl row schema" says the same). Of 3,800 real
    attempts, 385 forged (10.1%). Forged accuracies are multiples of 1/15: 290/385 (75%) sit
    at 0.20-0.33 (3-5 of 15 traps); maximum 0.67 (3 tools).
E4. The 15-trap static battery (test_harness.py TRAPS, 15 items: 10 binary, 5 four-way):
    chance expectation is 6.25/15 = 41.7% (forge_calc.py). The documented NCD baseline on it
    is 42% (README "Gate A"). Gate A therefore asked a tool to beat chance by one trap; under
    uniform random picking P(>= 8/15) = 0.248, P(>= 9/15) = 0.113. The Necropolis
    (2026-09-10, cited in the xpol packet s2) already ruled these 15-trap certificates vacuous.
E5. The 186-trap extended battery (trap_generator_extended, seed 42, 89 categories) floors,
    hephaestus/xpol_2026/floors.json via REVIEW_PACKET_2026-09-19 s1: position-majority decoy
    (always pick index 1) 0.4032; NCD 0.3925; random 0.3252; chance 0.3238.
E6. The hand-composed 9-engine tool on that battery: 0.3978 = 74/186
    (ablation/knockout_2026-08-20.json, "full"). The decoy is 75/186. The program's "one
    demonstrated metabolizer" scores one trap BELOW always-pick-index-1. Binomial SE at
    p = 0.4, n = 186 is 0.036, so tool, decoy and NCD are statistically indistinguishable.
E7. Knockout deltas reproduce (same JSON): prob_fallacy +11.1pp on R3 (36 items, = 4 items),
    temporal +32.1pp on R4 (28 items, = 9 items), causal -6.2pp on R5 (16 items, = 1 item);
    every other tier 0.0. These are real, localized, and tiny in item count; they are measured
    on a battery written by the same seat that wrote the engines.
E8. Cross-pollination replay (xpol packet s2-s3, E3 grade per the seat): 65 original 1.0
    tools median 0.355, max 0.473, 0 >= 0.50; Fable C_new 10 packets median 0.433, two >=
    0.50; groq-120B median 0.355 and agrees with NCD on 0.84 of picks. Shape fingerprint: the
    Fable tools are "the SAME costume as 1.0: regex structural parsing + NCD tiebreak +
    meta_confidence" with ~30 regex calls per tool vs ~3. Single draws; re-draw variance ~0.15.
E9. forge/verdicts (203 files): tier-2 FAIL_BATTERY 175, FAIL_DIVERSITY 19, PASS 3, tier-3
    FAIL_BATTERY 1, 5 untiered. Across all verdicts 2,106 primitive-ablation rows, 125 (5.9%)
    load_bearing. All three PASS tools have zero load-bearing primitives
    (t2_liar_detection_000, t2_simpson_paradox_003: every delta 0.0;
    t2_temporal_scheduling_007_gem: max delta 0.167 < 0.20). The anti-decoration law passed
    three fully decorative compositions (mechanism: s1.4).
E10. Nous corpus (roles/Nous/STATUS.md, reproducible by roles/Nous/science/corpus_audit.py):
    5,918 committed rows, 92.3% rated "novel", 4 rated "existing"; reasoning rating mode 7
    holds 57.7%; the composite separates the scorer's own reject class at z = +1.28, p = 0.31;
    zero controls; 4,187 further rows never committed (.gitignore); dormant 162 days.
E11. Hecate first cycle (REVIEW_PACKET_2026-09-30 s6, all 16 program.json files read):
    16 programs, currentVerdict PARK 14, PROBING 1 (HT-321a8fd8e0), SPECULATIVE 1
    (HT-a9e2ba7618). ENGINE 0, FOSSIL 0, REJECT 0 at program level; candidateEngines empty in
    all 16. 37 worlds probed over three rounds: 5 SIGNAL; 5 attacked at Pass 4; 0 survived.
    One Pass-4 outcome is ORIG_FOSSIL_ALT_PASS (HT-321a8fd8e0 W1: "Holography x Kolmogorov
    complexity x Mechanism design" reduced to textbook minimum-distance decoding, resistance
    step exactly at floor((d-1)/2)+1). Hecate's own audit INV_J found both round-3 SIGNALs
    pass by construction. Meta v1: triples vs pairs 5/8, INDETERMINATE; triples beat singles
    only as FAMILIAR -> COMPOSITE (0 UNFAMILIAR calls in any arm, and no unfamiliar control).

CLAIMED (prose only, not verified here)
- "~1,960 tools", "~12 distinct mechanism families", "~20 distinct mechanisms" (ROLE.md s2,
  ERRATA item 6 itself says both are prose).
- "85% on structured puzzles" for the composed tool (ROLE.md s2; a different, structured
  battery; no artifact located this session).
- forge/README.md cross-tier matrix (74% / 100% / 57% ...): prose table, no result file read.
- "Proven: 15 tools forged at 100% pass rate, up to 74% accuracy" (forge/README.md Break-Glass).

DESIGNED (not run)
- Apollo consumption of the 9 typed ops (DISPOSITION_LEDGER: "Apollo's one-experiment
  falsification never ran").
- Hecate Passes 5-10 (cross-substrate transfer, engine generation): "NO" in packet s7.
- Hephaestus 2.0 re-premise (boundary certifier + mechanism assay; HEPH-32), awaiting operator.

---------------------------------------------------------------------------------------------
## 3. Matrix

### 3a. Combinatorial explosion and reachability

- Concept space: C(95,3) = 138,415 unordered triples (147,440 with repetition, which
  random.choices permits). Committed Nous coverage 5,918 (4.3%); with uncommitted rows ~10,105
  (7.3%); Hecate's corpus 6,939 (5.0%); Hecate probed 16 (0.012% of the space, 0.23% of the
  corpus). The space is not what binds: E2 and E8 show the triple label does not reach the
  code. A tool's behaviour is a function of the code template and the battery, not the
  triple, so the effective search dimension is the prompt frame (8 frames) x model (5 usable
  of 12) -- tens of points, not 10^5.
- Program space actually searched: unbounded Python, sampled by an LLM conditioned on a
  battery-shaped prompt. The reachable set is a tight attractor ("regex + NCD + meta-
  confidence", E1/E2/E8): 12 models converge on it (ROLE.md s2), 5 models x 4-5 prompt
  strategies x ~100 candidates = 0 working R3+ algorithms (ROLE.md s2). This is a reachability
  desert in the opposite sense from combinatorial explosion: the generator collapses to one
  basin, and everything outside it (an actual inference procedure) has measured hit rate 0.
- Behaviour space as measured: the novelty fingerprint is an answer vector over the 15 static
  traps (hephaestus.py:689-720), at most 2^10 * 4^5 = 1,048,576 vectors, and tools that share
  a regex cascade share vectors. Behavioural novelty saturates almost immediately.
- Battery space: 28 generator families in trap_generator.py (1037-1069), 89 categories in the
  186-trap battery. At least 14 of the 28 base generators return a FIXED correct string
  regardless of parameters (trap_generator.py:108 modus_tollens "No", 129 quantifier "No",
  198 negation_scope, 248 temporal_ordering "Yes", 492, 573, 599, 640 double_negation "Yes",
  714, 745, 777, 810, 841, 874). The parameterisation varies nouns, not answers, so a lookup
  table keyed on category cue words reaches 100% of those categories. This is why the decoy
  floor is 0.40 and why "beats NCD" is cheap.

### 3b. Cosplay vs foundation

Which component does the work called "reasoning":
- In LLM-forged tools (v1-v9, scrap, T2/T3): hand-coded heuristics written by the LLM --
  surface regex routing to a fixed answer phrase, token overlap, numeric extraction, NCD
  tiebreak. Scientific concept names are decorative (v5 _secondary max contribution 0.008;
  v1 "Hebbian" = set intersection). Verdict: COSPLAY, by the seat's own words "5 mechanisms
  in costumes" (CALIBRATION.md first row) and by E1/E2.
- In the composed tool (composer.py): human/LLM-written keyword engines mirroring the trap
  battery's fixed answers, combined by a weighted vote with a decisive short-circuit. It ties
  the index-1 decoy (E6). Its +11/+32pp knockouts are template coverage of two trap families,
  not transferable inference. COSPLAY with honest bookkeeping.
- In forge_primitives.py and forge_v9 tools that call them: real algorithms (SAT, closure,
  topological sort, linear solve, belief tracking), hand-written; the LLM contributes only
  the NL-to-argument routing. This is a fixed algorithm library, not a learned or evolved
  mechanism; its ceiling is the ceiling of whoever writes the next primitive.
- Hecate: no reasoning is claimed; it is an adjudicator. What it adjudicated is that
  LLM-collided concept triples yield COMPOSITES of FAMILIAR mechanisms (meta v1: 0 UNFAMILIAR
  in 400 calls across arms) and that each surviving signal reduces to a textbook mechanism
  (decoding, endpoint location, channel reset, linear response).
Is any reasoning tool more than an LLM-written heuristic? On the evidence read: no. The best
candidates (Fable's 0.52 tools) are, by the seat's own shape fingerprint, more regexes, not a
different mechanism (E8).
Ceiling, concretely: a scorer that maps (prompt, candidates) to a ranking via cue-phrase
lookup has a ceiling equal to the fraction of test items whose answer is a function of
surface cues the author anticipated. On the forge's own 186-trap ruler that ceiling is near
the decoy floor plus the hand-coded families (~0.40-0.52 observed). On any held-out
generative task (grading_oracle Probe: produce a value) the ceiling is 0 by interface: the
tool cannot produce an answer not in the candidate list (ABLATION_CARD s3).

### 3c. Substrate bottlenecks

- Representation: the substrate is a Python source string. Nothing in it is typed beyond
  str -> list[dict]; no intermediate state is exposed, so nothing can be composed by anything
  other than an LLM re-reading source. composer.py passes a parsed dict, but engines re-read
  parsed["raw"] (e.g. 516, 819) -- the parse is bypassed.
- State/memory: every tool is stateless per call (v1 tool: no attribute written outside
  __init__). "Learning", "plasticity", "free energy" never update anything.
- Credit assignment: binary battery pass at tool granularity (test_harness.py:305). The one
  sub-tool credit signal that exists (tester.py:161 load_bearing) is not wired to the verdict
  (s1.4). Mechanism knockout (knockout_ablation.py) exists but is post hoc, per engine, on
  the author's ruler.
- Compositionality: zero inter-tier imports of forged tools (s1.3); T2/T3 share one
  hand-written parser. Composition only happens when a human writes composer.py.
- I/O bandwidth: multiple-choice ranking over 2-4 strings carries at most log2(4) = 2 bits
  per item; 186 items is ~ 300 bits of feedback per tool evaluation, mostly predictable from
  cue words. Generative evaluation is impossible through this interface.
- Measurement: the battery is authored by the same lineage as the tools, has fixed answers
  in half its base families, and was the selection target for thousands of generations;
  Goodhart is structural (each tier 100% on its own battery, ~0-1% on the next).

---------------------------------------------------------------------------------------------
## 4. Deliverable sections

### Discovery Approach

Collide distant human concepts (Nous triples), have an LLM render each collision as a Python
"reasoning tool", filter by gates and a trap battery, keep tools that beat compression
(NCD), and stack tiers so tier-N tools become tier-(N+1) primitives; later (Hecate) push each
collision through preregistered executable worlds and adversarial passes to see whether any
principle survives. The bet is that cross-domain recombination plus selection yields
reasoning "morphemes".

### The Brick Walls

1. Generator collapse (reachability desert): 95.7% of 1,502 library tools use the same NCD
   core; v5 is 96.2% byte-identical function bodies; 0 working R3+ algorithms from 5 models
   x ~100 candidates (seat's own count). Selection over LLM samples cannot leave a basin the
   LLM itself does not leave.
2. The ruler is beaten by a constant: index-1 decoy 75/186 vs the best hand-composed tool
   74/186; the 15-trap gate sat at chance (41.7%) and ~25% of random pickers would clear
   8/15. At least 14 of 28 base trap generators have a parameter-independent answer. Every
   "pass" in the T1 era measured template coverage.
3. No composition anywhere in the machinery: 0 of 10 T2/T3 tools import a lower-tier forged
   tool; 3 of 3 Iron-Law PASS tools have 0 load-bearing primitives (125/2,106 = 5.9% of
   primitive calls load-bearing overall); the anti-decoration check computes load_bearing
   and ignores it.
4. Interface cap: multiple-choice scorers cannot be graded on generation and cannot produce
   novel answers; this, not model choice, caps the whole lineage (seat agrees, ABLATION_CARD
   s3).
5. Concept collision does not produce new mechanisms: Hecate 0/5 signals survive, 0 ENGINE,
   0 UNFAMILIAR in meta v1; the PROBING program is textbook coding theory.

### Seed Viability

The LLM-forged tool population is a DEAD_END as a reasoning substrate, and this lineage is
the right cosplay control for the rest of the audit: it shows exactly what "a selection loop
over LLM-written heuristics" produces when measured honestly -- a scorer indistinguishable
from a constant index. Several components are worth carrying forward, which is why the
overall verdict is SALVAGE_COMPONENT, not DEAD_END:
- Mechanism-knockout protocol (src/knockout_ablation.py; its control behaved as predicted:
  each engine moves exactly one tier, causal is harmful). This is an instrument that WOULD
  detect a load-bearing mechanism if one arose in another engine.
- Behavioural answer-vector distance (hephaestus.py:689-826), once moved onto a battery
  without fixed answers, is a general population-diversity instrument.
- Counterfeit museum + calibration ledgers: a catalogue of ways to score without reasoning,
  directly reusable as negative controls for G1-G7 engines.
- Hecate's probe discipline (positive control, null twin, CHEAT control, preregistered
  clause, Pass-4 ORIG attack against the trivial explanation, by-construction audit INV_J):
  the best falsification harness seen in this group.
- forge_primitives.py (25 typed, correct algorithms) as a seed operator set for a typed
  substrate -- explicitly as hand-written primitives, not as evidence of discovery.
- The 6,276-scrap ledger and 203 verdicts as data about what cheap generation produces (with
  the 2,861 instrument-failure rows excluded).

### Evolutionary Roadmap

This lineage should not be scaled as a generator. The roadmap is for the salvaged parts.
1. Fix the ruler before anything else. Replace the trap battery with a generative,
   procedurally-parameterised task family whose answer is a computed value (e.g. random
   Horn-clause programs with queried atoms, random partial orders with queried pairs,
   random small Bayesian nets with queried posteriors), answer sets balanced so every
   constant / position / length decoy is at chance, held-out generators owned by a seat that
   writes no tools (Harmonia's scorer-mode request, ABLATION_CARD s3). Publish decoy floors
   first, as the xpol packet did.
2. Change the representation from str -> ranking to typed programs over a DSL built from
   forge_primitives: a simply-typed lambda calculus (or typed graph-rewriting over a
   blackboard, the Apollo shape) with types like Rel, Graph, Dist, Clause, Value, so a
   program must produce a value and composition is checkable by type. Search with
   enumerative + library learning (DreamCoder-style wake/sleep abstraction: compress
   recurring sub-programs into new primitives by MDL gain), which is the mathematically
   honest version of "tier N becomes tier N+1 primitives".
3. Credit assignment: enforce load_bearing (tester.py:161) as a hard gate and use
   data-flow knockout per intermediate slot (Apollo's rule: a slot counts only if zeroing it
   before a downstream read drops accuracy). Score compositions by description length
   under the library vs accuracy gain (MDL), not by battery pass.
4. Open-endedness metric: track library size, mean program depth, and fraction of solved
   tasks whose shortest solution uses an abstraction learned in a previous cycle. If that
   fraction stays 0, the ratchet is not turning.
5. Use the LLM only as a proposal distribution over typed programs (the seat's own doctrine:
   "LLMs propose transductions; verified kernels reason"), and Hecate as the adjudicator for
   anything claimed to be a new mechanism.

The ONE decisive experiment: a library-learning run on a held-out procedural task family
(step 1), seeded with the 25 forge_primitives as the only DSL, with an LLM-free enumerator
plus MDL abstraction, versus an equal-budget arm that may only add LLM-written ReasoningTool
scorers. Measure on held-out task instances generated after the run: accuracy above the
published decoy floors, and the count of learned abstractions that are load-bearing under
knockout. Kill criterion: if after N = 5 wake/sleep cycles the abstraction arm has learned
zero load-bearing abstractions (knockout delta < 2 SE) AND does not beat the frozen
primitive-only enumerator at equal evaluation budget on held-out instances, the "forge
composes" thesis is dead in its typed form too, and the forge should be kept purely as an
instrument shop.

---------------------------------------------------------------------------------------------
## 5. What would change this verdict

- Toward VIABLE_SEED: any LLM-forged tool (not hand-written, not composer.py) that, on a
  battery with balanced answers and a published decoy floor, beats the decoy by > 3 SE AND
  carries a mechanism that knockout shows load-bearing AND that the shape fingerprint
  classifies outside regex+NCD+meta-confidence. Or: a T(N+1) artifact that imports a T(N)
  forged artifact and loses accuracy when it is knocked out.
- Toward DEAD_END for the salvaged parts: if knockout_ablation, rerun by a seat other than
  Hephaestus on a held-out battery, fails its own control (engines smear across tiers), or
  if Hecate's Pass 10 independent review finds its probe controls also pass by construction
  beyond the two INV_J cases, the instrument layer loses its claim too.
- Facts that would correct this dossier: r2_chain_tracker.py (not read) may not share
  r2_chain_v2's type bug; trap_generator_extended.py (not read in body) may have balanced
  answers in its 61 extended categories, which would change the "half fixed-answer" count
  for the 186 battery (the base-28 count stands); forge_v4/forge_v7 individual tools were
  not read and could contain a distinct mechanism not visible to the grep-level scan.
- Any committed artifact for "85% on structured puzzles" with a decoy floor would move that
  number from CLAIMED to OBSERVED; it would not change the verdict unless the structured
  battery is held-out and decoy-balanced.
