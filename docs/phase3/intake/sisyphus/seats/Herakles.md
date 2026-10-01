# Herakles -- seat dossier (Sisyphus crawl)

Seat: Herakles ("Historical Collider / computational archaeology")
Crawl date: 2026-10-01
Base SHA of the crawl worktree: 19299e06b (F:/Prometheus-worktrees/sisyphus-base-role, = origin/main at crawl time)
Crawler: Sisyphus worker (Opus 5.5)

Coverage statement.
READ: roles/Herakles/ in full at the document level (CHARTER, BOOTSTRAP,
RESPONSIBILITIES, METHOD headings, BACKLOG_H0H5, todo_2026-09-03 and
todo_2026-09-16, D23_COMPLIANCE, all three journals, the 2026-09-17
operator-rulings capture, the 2026-09-11 replies directory listing);
herakles/ code: evca/core.py (structure + conventions block), evca/genomes.py
(keys), ca_stream/OBSTRUCTION.md, CA_STREAM_V2_PLAN.md, herakles/CRITERIA.md,
lineages/CATALOGUE_2026-09-11.md, HERAKLES_HISTORICAL_COLLIDER_V0/README.md and
GATE1_STATUS_2026-09-03.md, spec-toussaint-exploration HC_T01_CORRECTION,
HC_T01_COMPUTE_MODEL, HC_T01_EXECUTION_REVIEW_PACKET (head), the RA
re-analysis corrections file, hct01.c header; the full git history of herakles/
and roles/Herakles/ (98 commits, 2026-09-02..2026-09-17) with commit bodies of
the key engine commits (0641c567b, 175b5da08, feca5e688, 5a0458fd6, 7b8f364cb,
065c70d7f, 53f42a643, 19e13e5b1, 566e1e7ed, 19ad79d2e); comms index for
"Herakles"; consumers found by git grep for "from herakles|import herakles";
roles/base-role/RESPONSIBILITIES.md "verify the property" section;
Elenchus epistemic-debt LEDGER (C-04, C-05); archaeon/docs/expansion/DECISIONS.md
(D-18); Achilles census row; Artemis sfe_retrospective C_engines.md; Atlas
registry and inference-harvest mentions.
NOT READ in full: the ~120-family A_FIELD_MAP and the registry JSONL bodies
(B..Q) row by row; the 13 recovered PDFs; the specimen REPORT.md files for
Capcarrere/JP98/ABK96 (results taken from journal + catalogue, which cite them);
METHOD.md body; the deep_research decks and returned reports
(2026-09-04 constraint transfer, 2026-09-06 template mining) beyond commit
bodies; the 120+180+24 HC-T01 CSV rows. No code was executed. No path
containing "holdout" or "nestor_secrets" was opened.

---

## 1. Identity and purpose

Canonical name: Herakles. [IMPL] Installed 2026-09-02 by commit 815053e2e
("HERAKLES seat installed: Historical Collider V0 skeleton + seed").

Aliases: instance tag "Herakles[m2-5dfd8a81]" (2026-09-16/17 commits);
"Historical Collider", "retrospective instrument", "HC" (experiment prefixes
HC-T01, HC-R01, HC-L01); the engine is registered in Atlas as engine_id
"herakles.evca" ("Herakles EVCA", atlas/registry.json:147). [IMPL]

Original charter. [INTENT] roles/Herakles/prompts/DIRECTIVE_HISTORICAL_COLLIDER_V0_2026-09-02.txt
(sha256 c1301d79...) and roles/Herakles/CHARTER.md: recover, re-instrument and
re-interrogate ~40 years of artificial-evolution / adaptive-systems experiments
for "microscopic changes in what computation could acquire next" (evolvability,
accessibility, neutral precursors), via four missions: A particle search,
B detector archaeology, C parts archaeology, D composition search across
literatures. Standing orders insist on native vocabulary for retrieval, strict
provenance classes (ORIGINAL_SPECIMEN / RECOVERED_SPECIMEN / REIMPLEMENTATION /
APPROXIMATE_RECONSTRUCTION / CONCEPTUAL_REPRODUCTION), "detector before
verdict", and "no LLM is the historical judge" (rows from memory stamped
MODEL_RECALL_UNVERIFIED).

Charter changes and pivots. [HIST]
- 2026-09-03 operator ruling RULING_V0_CONTINUE_HYPOTHESIS_DAMAGED: the opening
  thesis ("history lacked a microscope for accessibility change") declared dead
  after research pass 1 found Altenberg 1994 and Mengistu/Lehman/Clune 2016
  already measured parts of it. Replaced by "recover the microscopes history
  built, identify what each could not see, determine whether their
  composition yields a detector" and by GATE-1..GATE-5 (no compute until an
  artifact is in hand; no blindness claim until candidates cleared; no invented
  measure before checking Q_DETECTOR_PARTS_REGISTRY; date-stamp "nobody
  measured" claims; citations in briefs carry evidence tiers). CHARTER.md
  "Standing Gates" section.
- 2026-09-06: the seat was used by Archaeon as the Deep-Research literature
  miner for the Archaeon expansion roadmap (69 discipline templates) -- a role
  outside the original charter.
- 2026-09-08..09-11: the seat's centre of gravity shifted from archaeology to
  supplying a pure CA-evaluation LIBRARY (herakles/evca, herakles/eca,
  herakles/ca_stream) consumed by Vivarium/SFE kinds, Archaeon campaigns and
  Theophrastus. This is the pivot that matters for Phase 3: the seat ended as a
  library/criteria maintainer for the EvCA density-classification lens.
- 2026-09-11 base-role adoption (072ea0cf5) and D-23 worktree compliance
  (91ca75f9f).
- 2026-09-16/17: moved to M2 (SPECTREX5); last seat commit a8258db99
  (2026-09-17) relays an operator host ruling. No commits since. [IMPL]

Current / terminal role. [HIST] Dormant since 2026-09-17 (14 days at crawl).
No lifecycle marker (Achilles census row, seats_part2.json: state NONE).
Open queue item #9 item 3 (ca_stream_v2) BLOCKED on Vivarium; HC-R01 review and
"EvCA Stage 1" authorisation PARKED with the operator (todo_2026-09-16.md).

Relationships. [HIST] Consumer of SFE (Daedalus) by charter; in practice a
supplier to Vivarium (kinds ca_density_v0, eca_rule_eval_v1), Archaeon
(C3 campaigns), Theophrastus (THEO-REQ-003..006), Proteus (mint consumes
herakles.evca.derive), Nyx. Adversarial reviewer of Archaeon's expansion
roadmap (fa7dbed50 critique). Ergon ran deep-dive lanes for it (Kouvaris 2017,
Avida 2003). Talos/Theophrastus/Archaeon sent it requests.

Hosts. [HIST] M1 era (2026-09-02..09-11, worktrees under F:/Prometheus-worktrees);
M2 SPECTREX5 from 2026-09-16 (journal 2026-09-16). BOOTSTRAP records that
comms from M2 needs EW_DB_HOST=192.168.1.202.

---

## 2. Engine / system inventory

E1. herakles.evca -- EvCA density-classification library (the main engine).
- Paths: herakles/evca/core.py (814 lines), genomes.py (112), derive.py (284),
  c3_null_check.py (302), c1e/ (run_c1e.py, compare_c3_2.py, PROTOCOL.md,
  REPORT.md, results JSON), tools/make_golden.py, tools/measure_sync_floor.py,
  tests/ (test_evca.py 565 lines, test_2026_09_16.py 378 lines),
  MAJ_STRUCTURAL_ZERO.md, sync_floor_2026-09-16.json. [IMPL]
- Purpose: executable form of the recovered 1993-95 EvCA rule tables
  (Mitchell, Crutchfield, Das, Hraber). Evaluate a radius-3, 128-entry binary
  CA rule on a periodic 1-D ring for density classification and related
  targets. [IMPL, core.py docstring]
- Versions: WP-C1 (0641c567b / 3466481b9, 2026-09-08) pure library; +C1-e
  protocol/runner/report (9ad85ca7f, 6052dc31b, 0fb23076a); +c3_null_check,
  cellwise_majority_match, MAJ_STRUCTURAL_ZERO (7b8f364cb, 09-10);
  +synchronisation_score, blinker control, C1-e vs C3-2 (065c70d7f, 09-10);
  +cellwise_synchronisation_match, make_ics(exact_count), correct_mask_hex,
  derive.py (dbc41fd2f, 6c9c55bfb, 09-16). [IMPL]
- Entry points: decode_table/encode_table, step/evolve, make_ics, classify
  (accuracy at T + bounded witness + mask digest), fixes_uniform_states,
  reflect/complement transforms, normalise_trajectory/trajectory_digest,
  majority_rule_table/gkl_rule_table/blinker_rule_table/random_table,
  cellwise_majority_match, synchronisation_score,
  cellwise_synchronisation_match; derive.derive_edit/flip/crossover/transform,
  verify_record. [IMPL]
- State: a numpy uint8 array of N cells (N odd, required); rule = 128-entry
  table, encoded as 32 hex, leftmost-neighbour-MSB convention re-derived in a
  test from maj and GKL definitions. [IMPL]
- Inputs/outputs: rule hex, N, steps (no default), IC seed and density
  (Bernoulli, uniform-density or exact-count ensembles); outputs dicts with
  accuracy, n_incorrect, bounded witness (64) and a whole per-IC mask. [IMPL]
- Persistence: none inside the library (pure; tested for no I/O, no global RNG
  consumption). Results persist only as committed JSON fixtures by tools. [IMPL]
- Execution model: single-process numpy, vectorised over ICs. [CODE-INFERRED]
- Scale: N = 149/599/999, 10^2..10^4 ICs typical, up to 10^7 ICs in the ABK
  reproduction; seconds to minutes per run (ABK run 83 s, journal 09-11). [HIST]
- Dependencies/consumers: vivarium/viv/ca_density.py (kind ca_density_v0),
  archaeon/campaign1..3 and archaeon/producer/campaign_c3.py,
  theophrastus/{dissect,ecology,round2,cross_consumer}.py, proteus/eval/
  rule_table_identity.py and the Proteus mint, nyx/readings/
  theo_req_003_composition.py, roles/Artemis FR-101 runner, Elenchus
  verify script. [IMPL, git grep]

E2. herakles.eca -- elementary (radius-1) CA library, kind eca_rule_eval_v1.
- Paths: herakles/eca/core.py (391), tests/test_eca.py (385), assay_alpha.json,
  class_map_fixture.json (T=8, 224 classes), class_map_fixture_T9.json
  (236 classes), tools/run_capcarrere_screen.py. [IMPL]
- Purpose: evaluate Wolfram rules 0..255 (LSB-index convention, deliberately not
  sharing the evca decoder); behavioural equivalence-class maps at small ring
  sizes (H5 lane); block_output criterion for Capcarrere-Sipper-Tomassini 1996
  rule 184/226. [IMPL, commit feca5e688 body]
- Built 2026-09-09 (feca5e688, cherry-picked from an Opus-5 session that also
  wrote ca_stream; the commit body says "herakles/evca is untouched").

E3. herakles.ca_stream -- streaming-memory probe of CA rules (H2 lane).
- Paths: herakles/ca_stream/core.py (374), run_alpha.py, reset_v2.py (249;
  deliberately unimported), tests/test_ca_stream.py (316), OBSTRUCTION.md,
  D18_AMENDMENT_v1.md, CA_STREAM_V2_PLAN.md, alpha_results.json,
  d18_development.json, d18_horizon_evidence.json. [IMPL]
- Purpose: inject a bit stream into declared ports of a CA lattice, step once
  per input, and fit a capacity-limited linear readout (32 params, closed-form
  ridge) over the CURRENT lattice for delayed-recall and temporal-XOR tasks;
  i.e. a reservoir-computing style memory assay. [IMPL, 175b5da08 body]
- v1 alpha ran; v2 (seeded Bernoulli reset, D-18) planned, never run. [IMPL/HIST]

E4. HC-T01 Toussaint reconstruction -- the only evolutionary simulator the seat
built and ran.
- Paths: herakles/specimens/spec-toussaint-exploration/derived/hct01.c
  (641 lines C; a compiled hct01.exe is committed beside it), analyze.py,
  make_results.py, verify_t0_claims.py (41 machine-checked claims), grid/
  (120 CSV: 4 cells x 30 seeds), sens/ (180), sens_long/ (24), noise*.csv,
  reanalysis/conditional_accessibility_2026-09-03/ (ra1.py, ra2.py, ra_audit.py,
  ra1_sensitivity_and_k7.py). [IMPL]
- Purpose: "faithful reconstruction of Toussaint 2003 thesis section 1.5"
  (hct01.c header): genotype = egg cell + ordered list of string-rewrite
  operators; development = one pass applying operators (T=1); first-type
  mutations (replace/duplicate/delete, Poisson(alpha*len)) and second-type
  structural rewrites (Poisson(beta)); alphabet 8, target length 25, period 5,
  lambda 100, 1000 generations; detector = 2000 offspring samples per
  individual per generation, NMI matrix over 25 phenotypic variables. [IMPL]
- Scale: 2.3 M detector samples/s/core measured; one 1000-generation run 8 s;
  120-run grid 2.5 min on 12 cores; detector cost 2000x evolution cost.
  [RESULT-UNVERIFIED, HC_T01_EXECUTION_REVIEW_PACKET s2]

E5. The Historical Collider registry set (literature instrument, not code).
- Path: herakles/HERAKLES_HISTORICAL_COLLIDER_V0/ (deliverables A..Q: field map,
  specimen, detector-archaeology, failure/anomaly, parts, composition graph,
  circuit genealogy, calibration particles, negative controls, recovered
  artifact manifest J, reconstruction queue K, compute leverage L, blind-spot
  matrix M, top-20 lists N/O/P, Q detector-parts registry with a D0-D5 ladder),
  build_hca_*.py generators. [IMPL as files; content mostly HIST/INTENT]
- herakles/specimens/: five specimen directories with immutable originals
  (PDFs) and derived/ transcriptions + reproduction scripts:
  spec-evca-density (13 PDFs + evolved_rule_tables.json),
  spec-capcarrere-r1-density, spec-juille-pollack-1998,
  spec-andre-bennett-koza-1996, spec-toussaint-exploration. [IMPL]
- herakles/lineages/CATALOGUE_2026-09-10.md and _2026-09-11.md: per-organism
  status table (RECOVERED / TRANSCRIBED / HELD / NOT_FOUND / AMBIGUOUS). [HIST]
- herakles/CRITERIA.md: every CA success criterion with its published-figure
  convention, range and floor. [IMPL-adjacent documentation; numbers cite
  commits]

E6. herakles/workspace.py (+tests): the D-23 refusal guard that refuses to run
from the canonical checkout. Infrastructure, not science. [IMPL]

E7. Deep-research and template-mining tooling (in roles/Herakles/deep_research/):
build_deck.py, ingest.py, compile_matrix.py for the 2026-09-06 Archaeon
template-mining pass; outputs landed in archaeon/templates/inbox/ (69
PROPOSED templates) and expansion_pass/MATRIX.{md,json}. [IMPL]

---

## 3. Architecture

What constitutes a world. [IMPL] For evca: a periodic 1-D binary ring of N
cells (odd N enforced), radius-3 neighbourhood (7 cells), synchronous update
via numpy.roll, a declared number of steps. The "task" is fixed by the
criterion (density classification at T, cellwise variants, synchronisation,
block_output for r=1). There is no world generator beyond the IC ensemble
(Bernoulli(p), uniform-over-density, exact-count-k). For ca_stream: the same
ring (N=31) driven by an external bit stream at port 0, with tasks
delayed_recall d=0..3 and temporal_xor d=0,1 over a 256-stream catalogue split
64/64/128 train/dev/confirmation. For HC-T01: a string-development world
whose fitness is matching a periodic target phenotype of length 25.

What constitutes an organism. [IMPL] evca/eca/ca_stream: the organism is ONE
rule table (128 bits, or 8 bits for ECA). It has no internal state beyond the
lattice it acts on; it is evaluated, never evolved, inside these libraries.
The held organisms are fixed historical genomes: maj, GKL, exp, par, particle1,
particle2 in genomes.py; plus das1995, davis1995, abk_gp, coev1, coev2 and rules
184/226 held only in specimen derived/ directories (NOT in genomes.py --
verified by grep, 2026-10-01). HC-T01: genotype = egg string + ordered list of
<=32 operator strings over an 8-letter alphabet (MAXSEQ 256, MAXOPS 32,
MAXPHENO 512, POPMAX 128 in hct01.c). [IMPL]

Genotype -> phenotype. [IMPL] evca: hex -> 128-entry table -> repeated
application on the lattice; the "phenotype" is the space-time diagram and its
terminal state. HC-T01: one developmental pass applying each rewrite operator
in order to the egg cell (T=1).

Memory model. [IMPL] The CA has only the lattice state as memory; the rule is
stateless. ca_stream's readout is explicitly forbidden from seeing input
history or earlier lattices (structural, asserted by test).

Mutation/search operators. [IMPL] Inside the libraries: none that run a
search. derive.py supplies provenance-carrying single-table edits (bit flip,
entry edit, one-point and uniform crossover, symmetry transforms) for OTHER
seats' searches; it "mints nothing". HC-T01 has real mutation: Poisson
first-type symbol replace/dup/delete and five second-type structural rewrites,
(mu,lambda)-style selection over lambda=100 [CODE-INFERRED from the header;
selection details not re-read line by line].

Selection/admission. [IMPL] None in evca/eca/ca_stream. Selection over CA rules
happened in other seats' machinery (Archaeon C3 campaigns via SFE/Vivarium,
Proteus mint). EvCA "Stage 1" -- re-running the 1990s GA that evolved the rules
-- was specified (FIRST_EXPERIMENT_PROPOSAL.md, GATE1_STATUS) and NEVER
authorised or run (todo_2026-09-16: "Authorise or refuse EvCA Stage 1
(operator) PARKED"). [HIST]

Pressure. [IMPL] Fixed task fitness only (density classification accuracy).
No ecology, no resource, no coevolution inside Herakles code; coevolved
organisms (Juille-Pollack coev1/coev2) were recovered as static tables.

Observation/action. [IMPL] Cells see 7 neighbours; there is no action other
than writing the next cell state. ca_stream adds one externally written port.

Scoring. [IMPL] Six named criteria in herakles/CRITERIA.md: at_T (the
published P_N), stable, cellwise_majority_match, synchronisation,
cellwise_synchronisation_match, block_output. Each carries a declared floor.

Temporal dynamics. [IMPL] Synchronous discrete time; steps required (2N or 600
conventions); at_T is "state at T", explicitly distinguished from "ever
reached by T" via fixes_uniform_states.

Spatial topology. [IMPL] 1-D ring only. No 2-D CA anywhere in herakles/.

Reproduction / learning / communication / cross-world transfer. [IMPL] None in
the CA libraries. HC-T01 has asexual reproduction with mutation; no learning,
no communication. Cross-world transfer: none.

Lineage tracking and provenance. [IMPL] The strongest part. Content-derived
player id "evca:r3:<canonical hex>" (ruled comms #271); derive.py records
parents by content id, operator, canonical params and a route-derived
derivation_id; specimen originals hashed in manifest J; every derived file
carries a derived_from pointer; prediction text committed before measurement
(dbc41fd2f before 6c9c55bfb).

Experimental control structure. [IMPL] Protocols committed before runs
(C1-e 9ad85ca7f before 6052dc31b/0fb23076a; JP98 protocol 7379a5634 before
transcription; RA-1 frozen 9c1badfba before any number); positive, cheat and
negative controls as tests (blinker rule; constant rules; shift register;
direct input; frozen random; leakage probe for ca_stream).

Design vs implementation disagreements.
- RESPONSIBILITIES.md says Herakles owns herakles/reconstructions/ "created on
  first build": that directory does not exist on main. Reconstructions live
  under herakles/specimens/<spec>/derived/ instead. [IMPL vs INTENT]
- The charter frames Herakles as an SFE experimenter ("I consume SFE ... fork-
  by-reference, null arms"); no Herakles run was ever executed on the SFE. The
  libraries were wrapped by Vivarium kinds and executed by other seats. [IMPL
  vs INTENT]
- The catalogue reports eleven RECOVERED organisms; the executable library
  genomes.py holds six. X-4 ("Vivarium taking coev1, coev2, abk_gp, das1995,
  davis1995 as ca_density organisms") never closed. [IMPL vs HIST]
- CA_STREAM_V2_PLAN.md says "Nothing here runs until that [D-18] decision";
  the operator decision was taken 2026-09-10 ("D-18: APPROVE v1",
  archaeon/docs/expansion/DECISIONS.md:52) and the run still never happened
  because the kind was never registered. The plan text was not updated. [HIST]

---

## 4. World capability audit

- Dimensions/state size: 1-D ring, N in {149, 599, 999} (also 7..11 for ECA
  class maps; 31 for ca_stream). State = N bits. [IMPL]
- Spatial: yes, 1-D, periodic; nothing 2-D or higher. [IMPL]
- State complexity: binary cells; rule space 2^128 (r=3) or 256 (r=1). [IMPL]
- Partial observability: each cell sees 7 neighbours; the global density is not
  locally observable -- that is precisely the classical "hard" feature of the
  density task. [IMPL]
- Stochasticity: only in the IC ensemble; dynamics deterministic. [IMPL]
- Action complexity: a single bit per cell per step. [IMPL]
- Temporal horizon: ~2N (298 at N=149) or 600 steps; ca_stream horizon 8. [IMPL]
- Delayed consequences: yes in the weak sense that classification is read at T.
- Adversaries / multiple agents / resources / ecology: none in the libraries.
  Coevolution (Juille-Pollack) exists only as recovered static outputs. [IMPL]
- Environmental change: none. Task diversity: six criteria on one substrate,
  plus 256-rule ECA class maps. World generation / open-endedness: none.
- Transfer between worlds: none, except that the same rule can be scored under
  several criteria and IC ensembles.
- Toy-grade statement (precise, not pejorative): the EvCA lens is a fixed
  1-D binary ring evaluating a fixed 128-bit lookup table against a single
  global-majority target. It is a canonical, well-understood benchmark from
  1993-2001 with a published reference distribution, which is why it calibrates
  well; it is also an easily memorised, narrow task with a known ceiling
  (~0.86 at N=149 for the best coevolved rules held). The ECA class maps are
  exhaustive enumerations at ring sizes 7-11 (the class count saturates at 236
  by T=9 on a 7-ring; 065c70d7f). ca_stream at N=31 with a 32-parameter linear
  readout is a deliberately small reservoir probe.
- HC-T01's world is a single target string of length 25 over 8 symbols with a
  periodic structure; also small and fixed.

---

## 5. Organism capability audit

CA rule organisms (evca/eca/ca_stream):
- Instruction set / architecture: a lookup table; no instructions, no control
  flow, no addressable memory, no recurrence beyond the lattice. [IMPL]
- Sensors: 7-cell neighbourhood (3 for ECA). Actuators: the cell's next state.
- Learning / adaptation / planning / representation construction / tool use /
  communication / self-modification / reproduction / recombination /
  development / internal simulation: none within an organism. [IMPL]
- What a successful organism can do: emergent particle/domain computation
  across the lattice (the EvCA line's "embedded particle" result) -- i.e.
  distributed information transport and collision logic. This is the one
  genuinely non-trivial computational phenomenon this lens can resolve, and the
  libraries do not currently analyse it: backlog L-8 "Particle catalogue
  (Hordijk, Crutchfield, Mitchell) as an executable fixture" is OPEN. [IMPL +
  HIST]
- Fighting chance at a nontrivial reasoning primitive? Grounded answer: for
  classical primitives (memory, composition, planning) essentially no -- a
  single fixed rule table on a 1-D ring has no persistent store and no input
  channel except the IC. For spatially distributed signal propagation and
  collision-based "computation" (particles), yes, and history shows it does
  (GKL, coev rules). ca_stream was the attempt to add an input channel and
  test memory; the six held density rules provably annihilate a lone injected
  bit (OBSTRUCTION.md; independently verified by Elenchus C-04), so under v1
  they had zero chance by construction, and v2 never ran.
HC-T01 organisms: string-rewrite genomes with operator lists -- a developmental
genotype-phenotype map with a real "second-type" representational rewrite
mechanism. They can change their own mutational neighbourhood (that is the
phenomenon measured). No behaviour, no environment interaction. [IMPL]

---

## 6. Search and pressure mechanism

- Inside Herakles libraries: no search. Novelty enters only via (a) recovery
  of historical organisms (human archaeology: author websites, printed hex
  tables, Deep Research), (b) random_table(seed) for floors, (c) derive.py
  single-step edits handed to Proteus/Theophrastus/Archaeon. [IMPL]
- HC-T01: evolution with Poisson mutation of two operator types; selection on
  phenotype-target match. Treatment = second-type operator on (beta=0.1) vs
  off (beta=0); alpha in {0.03, 0.06}; 30 seeds per cell. [IMPL/HIST]
- Upstream (other seats, using this library): Archaeon C3 campaigns ran GA-like
  searches over CA rule tables via SFE; Proteus mints derived rule tables.
  Those are outside this dossier. [HIST]
- Bottlenecks/collapse modes recorded:
  * Random 128-bit tables score exactly 0 on at_T (40/40 tables), so a search
    gated on at_T has no gradient from random starts (CRITERIA.md C-3,
    MAJ_STRUCTURAL_ZERO.md). This is why cellwise criteria were added.
  * The density task floor for constant rules is 0.5 on block_output and
    cellwise metrics; numbers must be quoted as distance above floor.
  * In ca_stream v1 the reset+single-port design made every held rule inert.
  * In HC-T01 the treatment arm alone can construct extra machinery, so the
    comparison cannot separate "history reorganised machinery" from "one arm
    was allowed extra machinery" (HC_T01_CORRECTION s1).

---

## 7. Measurement / ruler stack

Metrics and their floors (herakles/CRITERIA.md, all citing commits):
- at_T (published P_N; range [0,1], floor {0} for random tables).
- stable (no published analogue; stricter than at_T).
- cellwise_majority_match (floor 0.4998 mean, [0.4939, 0.5099] over 20 random
  tables at N=149; maj 0.5736).
- synchronisation (floor {0}; no solving organism held, so zeros are
  "unmeasurable rather than structural", C-2 open).
- cellwise_synchronisation_match (random band [0.057, 0.307]; blinker on
  random ICs 0.531; constants 0.000).
- block_output (r=1; analytic floor 0.5).
Reproduction rule (C1-e): REPRODUCED iff |measured - published| <= z*SE with a
Bonferroni-style z (2.935 for JP98's 15 cells; 2.498 for ABK's 4), binomial SE
from n ICs; DISCREPANT is a lead, not a defect (c1e/PROTOCOL.md). [IMPL/INTENT]
Controls: positive (blinker; shift register; GKL derived from definition),
cheat (blinker on exact-k ICs returns max(k,N-k)/N exactly), negative
(constants; frozen random; direct-input readout), leakage probe (readout fit on
reset lattices with no input must equal base rate). Symmetry checks: raw
digests must DIFFER and normalised must AGREE, so the normaliser is shown to
do work. c3_null_check returns IDENTICAL / NOT_IDENTICAL / INDETERMINATE and
names a target-flip bug signature. [IMPL]
HC-T01 rulers: historical validation targets V1-V7 (genome length 11 by gen
200; neutral degree 0.45->0.70; stall at alpha .06 beta 0 ~20%; MI stripes at
distance 5; misaligned modules), estimator-noise qualification across 20
replicate estimator seeds, paired permutation at run level, kill conditions
K1..K7 (K7: current fitness predicts acquisition at least as well as any
accessibility statistic). RA-1 conditional test with eligibility rule (>=2
eligible points per cell/horizon or INDETERMINATE). [IMPL/HIST]
Known blind spots:
- at_T cannot distinguish a frozen non-uniform lattice from a wrong-uniform one
  (maj "structural zero": maj reaches uniform in 23/200 undriven samples).
- No ruler for particle/domain structure (L-8 open).
- cellwise_majority_match mean cannot separate constant from random rules;
  dispersion does (0.50 vs 0.10).
- Synchronisation has no solving positive control.
- ca_stream's linear readout cannot express XOR of stored bits, so a low XOR
  score is not evidence of missing memory (H2-4).
- Class maps are TERMINAL-state equivalence; path-dependent merit invisible
  (H5-1).

---

## 8. Experiment inventory (campaigns)

C-HER-1. Research pass 1 / detector survey 1 (literature).
- Date 2026-09-03. Question: did history lack an accessibility microscope?
- Arms: six reachability candidates + three families read from primary sources.
- Reported result: opening hypothesis partly dead (Altenberg 1994; Mengistu,
  Lehman, Clune 2016); no clean D4/D5 detector; Draghi & Wagner 2008/2009 left
  as D4-shaped unread papers; two recalled paper titles found not to exist.
- Paths: HERAKLES_HISTORICAL_COLLIDER_V0/RESEARCH_PASS_2026-09-03.md,
  DETECTOR_SURVEY_2026-09-03.md; commits d2799dd70, d75c766c9, 12a6d8081.
- Outcome label: REPORTED NEGATIVE/NULL (for the original thesis).

C-HER-2. EvCA artifact recovery + GATE-1 (spec-evca-density).
- Date 2026-09-03 (83ef98885). Six genomes from printed hex in 13 hashed PDFs;
  maj and GKL derived from definitions match all 32 hex digits; measured at
  N=149 within ~2 SE of published for 5 of 6 (particle2 -0.013); a typo in a
  1995 PNAS table found.
- Outcome: REPORTED POSITIVE (recovery/reproduction, not a science claim).

C-HER-3. HC-T01 Toussaint missing-cell experiment (the only evolutionary run).
- Dates 2026-09-03 (b9a891686 directive; 10317a0d4 T0 gate; 911f9282e
  MISSING_CELL_CONFIRMED; 64cc041da EXECUTED; 834e6e0d3 packet;
  226d75cf2 OVERRULED; a22792dc6 CORRECTED).
- Question: does an operator that rewrites representation change future
  accessibility (local offspring distribution) beyond its immediate mechanical
  effect, and does accessibility predict later acquisition?
- Organism/world: Toussaint 2003 string-development genomes; periodic target.
- Arms: alpha {0.03, 0.06} x beta {0, 0.1}, 30 seeds each (120 runs) +
  sensitivity 180 + long 24.
- Measurement: 2000-sample offspring detector per individual per generation;
  frozen-population probe; estimator-noise floor.
- Reported: history effect 24-108x estimator noise; immediate knob effect 0.003
  vs historical 2.4; K7 fired (fitness predicts acquisition as well as
  accessibility).
- Later reinterpretation: operator verdict HC_T01_WEAK_SIGNAL_ONLY (seat had
  claimed PARTICLE_SURVIVES); wider-literature "missing cell" claim withdrawn
  (Tiso 2024, Petak 2025, Kounios 2016 missed by a one-author citation-graph
  search); RA-1 INDETERMINATE (K7's comparison was at windows where outcome was
  a deterministic function of the conditioner); RA-2: detector largely reads
  presence of >=1 production rule (0 ops 0.341 -> 1 op 2.730 modular degree).
- Outcome label: LATER OVERTURNED (headline verdict downgraded; underlying
  measurement retained as MIXED).

C-HER-4. HC-R01 / HC-L01 (accessibility recurrence review; neutral-network
literature lane).
- Date 2026-09-03 (226d75cf2, 22556c863, cdd6e9151, dc0492a3b, 2a5ac0117).
- Reported: "HCA-2 already exists in the literature, Part C does not";
  neutral-network literature has no H3 (Draghi SI 6.2); section 6 later
  corrected after a sibling seat explained why K7 fired.
- Outcome: MIXED (and the HC-R01 packet review is PARKED with the operator).

C-HER-5. Cross-seat meta-analysis (2026-09-04, bbc3710bd): "six convergences,
and not one of them is about evolution". Outcome: UNKNOWN (not re-read).

C-HER-6. Archaeon template mining + expansion pass (Deep Research).
- Dates 2026-09-06 (566e1e7ed .. 19e13e5b1; duplicated commits exist as
  cherry-picks).
- Question: what is the smallest experiment each of 69 disciplines would run on
  the bench, and what does the bench lack?
- Reported: 1 of 69 runnable (later corrected: 7 name an implemented kind, 62 a
  missing one, 50 carry destroyed parameter values; against the real registry
  0 runnable); 66 of 69 salvaged from a corrupted Deep Research run; three SFE
  defects found by running proposals through real machinery: F-1 length
  mismatch silently capped scores (fixed as WP-0a 85d6ff060 per Atlas digest),
  F-2 check() validates names not drawability, F-3 no cross-axis coherence;
  F-4 degeneracy guard misses stateful kinds under state=reset; F-5 step_scale
  is a rescaling; "bits is not a discriminating axis" (score distribution
  identical for any bitstring; usable as a free negative control).
- Outcome: INSTRUMENT FAILURE findings about SFE (REPORTED POSITIVE as defect
  discovery); template content CONTAMINATED by salvage (structure from the
  miner, numbers nulled).

C-HER-7. WP-C1-e: reproduce 18 published EvCA cells.
- Date 2026-09-08 (9ad85ca7f protocol, 6052dc31b runner, 0fb23076a report).
- Arms: 6 genomes x 3 lattice sizes. Reported 17/18 REPRODUCED; particle2 at
  N=149 DISCREPANT; four suspects killed; transcription the surviving suspect
  (X-2, untestable without original bytes). maj reproduced 0.000 exactly over
  16000 ICs at three N.
- Outcome: REPORTED POSITIVE (reproduction), one cell INCONCLUSIVE.

C-HER-8. H2 alpha ca_stream_v1.
- Date 2026-09-09 (175b5da08); D-18 amendment measured 2026-09-10 (5a0458fd6).
- Question: can the recovered CA rules serve as a streaming memory substrate?
- Reported: 0 of 63488 non-zero feature entries for all six genomes over the
  256-stream catalogue: proven inertness (every rule outputs 0 for every
  neighbourhood with popcount <= 1). Instrument controls passed (shift register
  solves delayed recall; fails XOR as linear theory requires).
- D-18 v1 (seeded Bernoulli reset, horizon 8) approved by the operator
  2026-09-10; ca_stream_v2 never registered by Vivarium; never run.
- Elenchus C-04 independently verified inertness ("EARNED"); Elenchus C-05
  judged "a density classifier MUST annihilate a lone minority cell"
  OVERSTATED (counterexample constructed), which bears on why "different
  rules" was ruled out at alpha.
- Outcome: INSTRUMENT FAILURE (configuration provably inert); v2 UNKNOWN.

C-HER-9. H5 alpha eca_rule_eval_v1 and class maps.
- Date 2026-09-09/10 (feca5e688, 5a0458fd6, 065c70d7f). 256 ECA rules collapse
  to 224 behavioural classes (7-ring, T=8); 236 at T=9 = ring ceiling; N=9 232,
  N=11 238. Outcome: REPORTED POSITIVE (fixture), scope-bound.

C-HER-10. C1-e vs Archaeon C3-2 comparison.
- Date 2026-09-10 (065c70d7f). 24/24 cells agree; largest 2.95 SE vs Bonferroni
  3.078; n_ics=100 per cell so "no detectable disagreement" rather than tight
  agreement (seat's own caveat). Outcome: REPORTED POSITIVE (weak power).

C-HER-11. Criterion floors: cellwise_majority_match (7b8f364cb) and
synchronisation / cellwise_synchronisation (065c70d7f, dbc41fd2f, 6c9c55bfb).
- Reported: random-table floors measured; prediction for the sync floor
  ("~0.27, narrow, spread 0.005") LOST (measured spread 0.049, band
  [0.057, 0.307]); particle1 one-IC-in-100 still flipping at T=298 (unreplicated
  row). Outcome: REPORTED POSITIVE (instrument calibration) with a recorded
  failed prediction.

C-HER-12. Lineage widening: Capcarrere 1996, Juille-Pollack 1998, ABK 1996.
- Date 2026-09-11 (bea2f1c99, d7e807b3e, 7379a5634, 7901a1e03, 36278862e).
- Reported: Capcarrere footnote [13] replicated; ranking clause reproduces only
  under Bernoulli(0.5) ICs (rules 168,172,224,228 overtake under uniform
  density); JP98 Table 1 15/15 REPRODUCED (z 2.935; coev1/coev2 0.8548/0.8574 at
  N=149, above GKL 0.816); ABK96 4/4 REPRODUCED at horizon 600; GP rule and Das
  1995 bit-identical across two printings.
- Outcome: REPORTED POSITIVE (reproduction).

---

## 9. False-positive / false-negative archaeology

T1. The opening thesis. Claim (09-02): history lacked a longitudinal
accessibility microscope -> evidence: seeded registries from model recall ->
challenge: research pass 1 primary-source reads (Altenberg 1994, Mengistu et al
2016) -> correction: RULING_V0_CONTINUE_HYPOTHESIS_DAMAGED (09-03) -> status:
withdrawn; narrowed to "find pairs of instruments a programme had but never
pointed at each other". Class: premature interpretation from model recall.

T2. Particle-transition rate recalled as "rare". Claim: one rare figure ->
challenge: primary read -> correction: two experiments, 0/50 (Physica D config)
vs 7/300 (PPSN III) -> status: a reconstruction of the wrong configuration would
have targeted a setup where the phenomenon never occurred (README "Honest
reading"). Class: recall error that would have produced a false negative.

T3. HC-T01. Claim: HC_T01_PARTICLE_SURVIVES + MISSING_CELL_SUPPORTED ->
evidence: 24-108x noise history effect at identical phenotype/fitness ->
challenge: K7 fired; operator adjudication; Ergon's Kouvaris forensics ->
correction: WEAK_SIGNAL_ONLY; missing-cell claim withdrawn (selection effect:
one-author citation graph); RA-1 shows K7 itself was ill-posed (deterministic
conditioner) and returns INDETERMINATE; RA-2 shows machinery PRESENCE explains
most of the effect -> current status: "history changes measured local
accessibility in this substrate" survives; "reorganised generator" language
unsupported; prospective value of accessibility unanswered. Confound classes:
treatment-only machinery; ruler that reads a count; mis-drawn literature
population.

T4. H2 inertness. Claim: CA rules as stream memory -> evidence: 0/63488 ->
challenge: none needed; proof -> correction (two layers): XOR-injection escape
withdrawn (5a0458fd6); Elenchus C-05 shows the "must annihilate" generalisation
is overstated -> status: v1 configuration is a TRUE instrument failure; the
substrate hypothesis is UNTESTED (v2 never run; "different rules" barred at
alpha on an overstated premise). False-negative regime.

T5. particle2 DISCREPANT (C1-e). Claim: 17/18 reproduce -> suspects tested
(lattice size, horizon, IC ensemble, encoding) -> transcription surviving
suspect -> untestable without original bytes (X-2 HELD). Status: one cell
INCONCLUSIVE; flagged as a possible transcription contamination of one of the
six core organisms.

T6. Template mining count. Claim: "1 of 69 runnable, 68 missing executor" ->
challenge: own recomputation -> correction (53f42a643): 7 implemented kinds, 62
missing, 50 damaged; 0 runnable against the real registry. Also "Ingest flagging
under-reported the damage: 0 flagged, 50 actually null" (fed189cfb / 0b6be489b, cherry-pick pair).
Class: validator that could not fire; metric conflating two axes.

T7. Sync floor prediction lost (6c9c55bfb): narrow interval predicted, band 10x
wider measured; kept visible. Class: correctly handled prediction failure.

T8. Repository state lying by implication (base-role example). Claim in seat
records that work was on main -> what was true: the canonical checkout's
herakles/evca/core.py held a stale 67-line appended synchronisation_score that
was strictly behind main (D23_COMPLIANCE_2026-09-11.md "a.") and a test run
"from canonical" executed canonical's pre-guard code and wrote a file into the
canonical tree -> correction: test rewritten to point REPO at canonical ->
status: base-role RESPONSIBILITIES.md:42 cites Herakles: "repository state can
lie by implication (a SHA quoted before it was an ancestor; a path that resolves
to nothing from where others read)". VERIFIED STILL LIVE 2026-10-01: the
canonical checkout F:/prometheus (on branch vivarium/v0-2026-09-05) still shows
"M herakles/evca/core.py" with exactly that +67-line stale diff -- three weeks
after the seat said it "needs a git restore from whoever performs the canonical
reset". [IMPL, git diff --stat in F:/prometheus, read-only]

T9. Possible false-negative regimes left open by design: synchronisation (every
held organism scores 0; no solving rule held, L-7/C-2); particle catalogue
(L-8); EvCA Stage 1 GA never re-run, so the 7/300 particle-strategy transition
-- the seat's first-chosen "bump" -- was never measured under SFE.

---

## 10. Research outputs

- roles/Herakles/CHARTER.md, RESPONSIBILITIES.md, METHOD.md, BOOTSTRAP.md:
  doctrine of a retrospective instrument (provenance classes, native
  vocabulary, detector-before-verdict). [INTENT]
- herakles/HERAKLES_HISTORICAL_COLLIDER_V0/README.md + deliverables A..Q,
  RESEARCH_PASS_2026-09-03.md, DETECTOR_SURVEY_2026-09-03.md,
  GATE1_STATUS_2026-09-03.md, FIRST_EXPERIMENT_PROPOSAL.md,
  EVCA_HCA1_HCA2_DESIGN_NOTE.md, HCL01_NEUTRAL_NETWORK_LITERATURE_PASS_2026-09-03.md,
  HC_R01_CORRECTION_2026-09-03.md, CROSS_SEAT_META_ANALYSIS_2026-09-04.txt,
  Q_DETECTOR_PARTS_REGISTRY.md (D0-D5 ladder), M_BLIND_SPOT_MATRIX.md. [HIST]
- herakles/specimens/spec-toussaint-exploration/: HC_T01_PREREGISTRATION,
  COMPUTE_MODEL, RESULTS.jsonl, two review packets, CORRECTION,
  reanalysis/conditional_accessibility_2026-09-03/ (RA1 preregistration,
  corrections, reproduction). [HIST]
- herakles/specimens/spec-{capcarrere-r1-density, juille-pollack-1998,
  andre-bennett-koza-1996}/PROTOCOL.md + REPORT.md. [HIST]
- herakles/evca/c1e/PROTOCOL.md, REPORT.md; herakles/evca/MAJ_STRUCTURAL_ZERO.md;
  herakles/CRITERIA.md. [HIST/IMPL]
- herakles/ca_stream/OBSTRUCTION.md, D18_AMENDMENT_v1.md, CA_STREAM_V2_PLAN.md.
- herakles/lineages/CATALOGUE_2026-09-10.md, CATALOGUE_2026-09-11.md.
- Review packets in roles/Herakles/prompts/ (REVIEW_PACKET_HISTORICAL_COLLIDER_V0,
  HERAKLES_V0_ARC, LINEAGES_WIDENED_2026-09-11, SYNC_CRITERION_AND_DERIVE_2026-09-16).
- Deep research: roles/Herakles/deep_research/2026-09-04_constraint_transfer/
  (Gemini Deep Research report) and 2026-09-06_archaeon_template_mining/
  (deck, ingest, expansion_pass MATRIX of 69 entries, EXPANSION_REQUESTS.md).
- Critique of Archaeon's expansion roadmap (fa7dbed50, e9f81abef) in
  roles/Archaeon/INBOX_* files.
- Handoffs to Ergon (Altenberg 1994, Avida 2003 EQU, Mengistu 2016) and to
  Daedalus (evolvability positive control): roles/Herakles/handoffs/.

---

## 11. Journals, TODOs, pivots, abandoned branches

- Journals: 2026-09-11, 2026-09-16, 2026-09-17 only (earlier work recorded in
  commit bodies, README STATUS table and todo_2026-09-03.md).
- TODO lineage: todo_2026-09-03.md -> todo_2026-09-16.md (re-classifies the old
  queue: HC-R01 review PARKED; EvCA Stage 1 PARKED; Petak 2025 re-analysis,
  Tiso 2024 ch.3 read, neutral-network lane, Teller 1996 verification
  STILL_LIVE; Kounios cell NEEDS_REPREMISE).
- BACKLOG_H0H5.md lanes: LIT (L-1..L-3 DONE; L-4 publisher-gated; L-5 par
  identity AMBIGUOUS; L-6 inventory; L-7 sync rule; L-8 particle catalogue;
  L-9 Avida 2003 thread in ergon/avida2003 (2041 files, wrong Avida version);
  L-10 Kouvaris 2017 thread), CRIT (C-2 open), H5 (H5-1 trajectory classes,
  H5-2 ring ceilings), H2 (H2-1 v2 blocked; H2-2 rule search; H2-3 wider
  injection; H2-4 nonlinear readout), X (X-1, X-2, X-3 F-20 recording gap,
  X-4 second lineage into Vivarium, X-5, X-6).
- Pivots: (1) thesis killed 09-03; (2) archaeology -> library supplier 09-08;
  (3) used as Deep Research miner 09-06; (4) host move to M2 09-16; (5) silent
  dormancy after 09-17. Why: the operator/Archaeon routed the H0-H5 lanes
  through Herakles's library once GATE-1 opened for EvCA; the seat's own
  evolutionary programme (Stage 1, HC-R01) stalled awaiting operator decisions
  that the record does not show being taken.
- Abandoned / never-built: herakles/reconstructions/; run_alpha_v2 (deliberately
  unwritten); EvCA Stage 1 GA; Avida H3 specimen.
- Duplicate history: 09-06 commits appear twice (cherry-picks, e.g. 53f42a643
  and a611a0f10); not a content difference as far as checked.
- Artemis sent two findings digests to Herakles (comms #884 2026-09-28, #1007
  2026-09-29) after dormancy; no Herakles response exists.

---

## 12. Lens inventory

Lens L-HER-A: "EvCA density-classification reproduction lens" (herakles.evca +
eca + specimens).
- Substrate observed: 1-D binary CA rule tables, r=3 (and r=1).
- Organisms: 11 historical rules from 4 lineages and 3 search processes (GA,
  GP with ADFs, coevolution with resource sharing) + hand-designed rules;
  random tables as floors.
- Worlds: fixed ring, IC ensembles.
- Pressures: none inside; fixed task fitness via external searches.
- Phenomenon family: emergent distributed computation (particles/domains);
  calibration of evolutionary-search claims against a published reference.
- Resolving mechanism: six criteria with measured floors; exact provenance;
  symmetry normalisation; reproduction tests with SE.
- Resolution ceiling: one task family, one substrate dimension, ~0.86 best held
  score; criteria read terminal or near-terminal states only.
- Noise sources: IC sampling (binomial SE), horizon conventions (2N vs 600;
  shown immaterial for held rules), IC ensemble (Bernoulli vs uniform-density
  changes rankings), transcription errors from printed hex (particle2).
- Architectural limitation: no particle/domain analyser; no 2-D; no search; no
  input channel (except ca_stream).
- Reusable: the provenance/criteria discipline, content-addressed rule ids,
  derive.py provenance records, the reproduction protocol pattern, the floor
  table pattern (CRITERIA.md "rules for adding a sixth").
- Toy-grade: the task itself (density classification on a small ring).
- Unknown: whether the coevolved and GP rules behave differently from the GA
  rules under the cellwise criteria (never run; X-4).

Lens L-HER-B: "CA streaming-memory (reservoir) probe" (ca_stream).
- Substrate: CA as reservoir with one injected port; linear readout.
- Phenomenon: memory / temporal computation in a CA.
- Current resolution: zero (v1 inert by proof); v2 frozen plan with leakage
  gate and pre-stated predictions (maj and exp should sit at baseline).
- Limitation: linear readout cannot see XOR; single port; held rules selected
  for a different task.
- Reusable: the control suite (shift register, shift+XOR, direct input, frozen
  random, leakage probe) is a clean reservoir-assay template.
- Unknown: everything about v2.

Lens L-HER-C: "Developmental accessibility microscope" (HC-T01 hct01.c +
detector).
- Substrate: Toussaint string-rewrite development.
- Phenomenon: history-dependent change in local offspring distribution
  (evolvability) independent of current fitness.
- Resolving mechanism: 2000-sample offspring detector per individual per
  generation, frozen-population probe, estimator-noise floor, operator on/off.
- Ceiling/limitations: one small target; the treatment arm alone has the
  operator class; detector response dominated by a count of operators (RA-2);
  K7-type prospective tests need eligibility windows not available in the
  frozen rows.
- Reusable: the detector-cost model (2000x evolution), noise qualification,
  RA-1 eligibility discipline, and the "cheap-state baseline mandatory" rule.
- Toy-grade: the world. Unknown: behaviour at larger targets / richer
  development; whether the rigour-cell result generalises.

Lens L-HER-D: "Historical specimen recovery" (process, not code): recovering
evolved artifacts from printed tables and author sites with hash custody. Its
resolving power is archival; its known failure is population-drawing for
"nobody did X" claims (T3).

---

## Open questions / unknowns

1. Was EvCA Stage 1 (re-run of the 1990s GA under SFE, targeting the 7/300
   particle-strategy transition) ever decided by the operator? No record found.
2. Was the HC-R01 packet ever reviewed? PARKED as of 2026-09-16; nothing later.
3. Why did Vivarium never register ca_stream_v2 after D-18 v1 approval on
   2026-09-10? Not investigated here (Vivarium dossier territory).
4. Is particle2's N=149 discrepancy a transcription error? Untestable without
   the original EvEmComp bytes.
5. particle1's single still-flipping IC at T=298: unreplicated.
6. Whether the 5 non-EvCA organisms ever entered any SFE/Vivarium run: grep
   finds them only in herakles/specimens/ and the catalogue.
7. The contents of A_FIELD_MAP (~120 families, mostly MODEL_RECALL) and the
   ranking files N/O/P were not audited row by row; they were "candidate pool
   only, no ranking" at last update.
8. The stale canonical-checkout edit to herakles/evca/core.py (T8) is still
   present on F:/prometheus; whether anything imports from canonical is unknown.
9. Atlas registers herakles.evca with 0 harvested experiments (Artemis
   C_engines.md line 152); the Atlas map is therefore silent on every campaign
   above. Atlas did not disagree with the source; it simply has no data.
