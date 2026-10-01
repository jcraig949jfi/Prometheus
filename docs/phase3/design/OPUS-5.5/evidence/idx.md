# idx -- Cross-crawler index analytics: what Prometheus actually built, in numbers

Reader: EPIMETHEUS evidence reader (group idx), 2026-10-01. Read-only.
Tree: worktree C:/prometheus-worktrees/epimetheus-phase3, HEAD c9b18697b, origin/main 4c071e3c5.
Inputs: docs/phase3/intake/{sisyphus,tantalus,tityos,ixion}/{artifact_index,engine_index}.jsonl
(all 8 files parsed, 0 bad lines), plus tityos/ruler_inventory.jsonl (152 rows), the four REPORT.md
headers (method/coverage only), and git (rev-list, ls-tree, ls-files + byte-level line counts).
Spot-checks against source are listed in s9. Analysis scripts lived in the session scratchpad only.

Tags: [IMPL] read in code/data/git; [REPORTED] crawler record, not re-verified; [INFER] my coding of
crawler records; [CORR] later correction; [UNK]. Every count in s3-s6 is [IMPL] on the index files
(what the crawlers wrote), and everything about what an engine "was" is therefore at most [REPORTED]
unless s9 says I confirmed it. My categorical codes (s4.1) are [INFER] and are judgement calls.

---------------------------------------------------------------------------------------------------

## 0. Bottom line (numbers an architect should carry)

1. Scale of the fossil record [IMPL]: 11,779 commits reachable from origin/main between 2026-03-22
   and 2026-10-01 (4,269 first-parent, 1,159 merges); 7,224 of them (61%) in September 2026 alone.
   72 directories under roles/ (59 seats crawled + 6 Phase-3 seats + base-role + 7 legacy/unused).
   68,880 tracked files; 14,859 .py files; 3.19M Python lines.
2. Where the code mass went [IMPL counts, INFER families]: ~1.25M Python lines (39%) are
   LLM-forged / scrap reasoning-tool files (agents/hephaestus/{humanreadable,scrap,scrap_staging,
   forge*} 1.17M + forge/candidates 77k). ~0.86M (27%) are math-catalogue / falsification
   pipelines (cartography 285k, prometheus_math 183k, charon 95k, harmonia 80k, techne 68k,
   ergon 66k, ...). Only ~0.62M (20%) are organism/world engines, and the engines that produced
   the most mechanistically legible results are tiny: ares/ 3.8k lines, crius/ 6.9k, herakles/ 8.3k.
3. Engine census [IMPL count of records; INFER codes]: 171 engine/lens records from the three
   science/ruler crawlers + 76 institutional systems from Ixion = 247 records (~240 distinct
   systems after removing 4 exact and ~6 perspective duplicates). Of the 171: 58 (34%) are
   instruments/audits, 34 (20%) are organism-in-world simulations, 22 (13%) task benches with fixed
   or external solvers, 19 infrastructure, 16 LLM generation/review pipelines, 14 math-catalogue
   pipelines, 5 design-only, 2 bare substrates, 1 generator.
4. (a) Organism adapts: 44/171 (26%) have any adapting organism; 29 population search only,
   12 lifetime learning only, 3 both. Of the 34 simulations, 25 adapt only by population
   search. Lifetime learning is concentrated in one seat (Ensorain: 7 of the 15 LIFE/BOTH rows)
   plus LLM/RL rows; population variation AND in-life adaptation in the same organism: 3 (Ares
   Hebbian W1 + GA; Crius persistent workspace + program search; Ensorain E0 GA over a TT learner).
5. (b) World with hidden state: only 12/171 (7%) have a LATENT variable the organism must infer
   (regime, hidden card, hidden rule, hidden relabelling); 24 (14%) if memory-of-past-observation
   worlds are included; 11 more hide only a static target/field (black-box optimisation or field
   completion). Of the 12 latent-state engines, the realised demand was verified at D5 in one
   (Ensorain ARC3, hand-specified estimators on the Even process), D3 in two (Ares, Nyx reading
   of Ares), D1 in one, D0 in one, unknown/never verified in seven.
6. (c) Demonstrated-detectability ruler: 25/171 (15%) carry a ruler whose detectability was shown
   [REPORTED]: 10 exact-by-construction scorers of static tasks, 15 with planted or
   control-demonstrated recovery. Of those 15, only 5 sit on an organism/world engine (Ensorain
   D-series, WTP-03, Cosmos C3, Ergon E4, plus the Artemis heredity panel on NPE specimens); the
   other 10 are integrity/provenance/audit instruments or assays on synthetic generative models. Tityos's ruler inventory agrees: of 146
   distinct instruments, 30 "yes", 53 partial, 57 no, 5 unknown; of the 30 "yes", ~20 detect
   pipeline/integrity defects, ~7 are statistical methods calibrated on synthetic data, 2 are math
   ground truth, and 1 (CVT heredity certificate, constructed panel) measures an organism property.
   Cross-substrate transfer tested: 2 of 152 rows (one of which failed).
7. Intersection (a) AND (b) AND (c): exactly 1 of 171 engines (Ensorain ARC3 dev instruments), and
   its "organism" is a hand-chosen estimator family, not a developing machine. (a) AND (b): 8.
8. Max cognitive demand actually realised (organism/world subset, n=62): D1 lookup/static map 29,
   D0 nothing 9, unknown 8, D3 one-cue latch/delayed recall 6, D4 small FSM/sequential 5 (all by
   fixed hand-written or historical solutions, plus AlienCircuitry representations), D2
   interpolation 4, D5 hidden-state inference 1. Designed demand was >= D5 in 15 engines across
   all 171; realised D5 in 1. 23 engines show a designed > realised gap.
9. Self-described toy/prototype [IMPL keyword count on own records]: "toy" in 16/171 (9%);
   toy | prototype/stub | never-run/design-only markers in 45/171 (26%); 34% of organism/world
   engines, 29% of simulations; adding tiny/small/single-seed markers: 58% of organism/world.
10. Epistemic make-up of the 1,802 artifact rows [IMPL]: IMPL 38.6%, REPORTED 21.4%, HIST 16.6%,
   INTENT 14.0%, CORR 8.5%, INFER 0.6%, UNK 0.3%. In the three science packages there are 139
   CORR rows against 357 REPORTED rows: roughly 2 later corrections for every 5 reported results.

---------------------------------------------------------------------------------------------------

## 1. Inputs and their heterogeneity (read before trusting cross-package sums)

    package    artifact rows  seats  raw types  engine rows  engine schema
    sisyphus        528         15      171          51       shared 10 keys
    tantalus        528         15       16          46       shared 10 + 6 audit keys
    tityos          348         16      156          74       shared 10 keys (+ ruler_inventory 152)
    ixion           398         32       11          76       different: status/inference/tests
    total          1802                              247

- Ixion's artifact rows use kind/epistemic_class/first_commit/last_commit/summary and its engine
  rows describe institutional systems (status, inference_dependency, scheduling, tests), not
  organism/world/pressure/ruler. Ixion is therefore excluded from organism/world statistics and
  analysed separately (s4.8). [IMPL]
- Free-text fields: artifact_type has 171 / 156 distinct spellings in Sisyphus / Tityos; I
  normalised them into 9 classes by regex (s3.2). phase3_relevance is free text in all four;
  only Tantalus prefixes ratings (low 55, medium 51, high 23 of 528). [IMPL]
- Tantalus seat counts are by dossier; Tityos adds a "shared" pseudo-seat (27 rows); Ixion seat
  strings are compound ("Atlas;Mnemosyne") and I took the first token. [IMPL]
- Coverage gaps the crawlers themselves state [REPORTED]: host-local data not in git (M2 SFE
  ledgers, BEE results, Archaeon off-repo data) unread; harmonia/ ~40 of 766 files read closely;
  techne fossils 6/189; theseus 3/55 generators; cartography mostly unread; comms DB not read by
  Tityos. Not crawled by anyone: 7 legacy roles dirs (CrossDomainCartographer, Enceladus,
  EvolutionaryArchitectAndReasoningSpeciesEngineer, MPADatabaseArchitect, PipelineOrchestrator,
  ScienceAdvisor, StructuralMathematician) and the "Pythia" Gemini deep-research queue agent
  (423 commit subjects begin "Pythia", 2026-05-18..05-30; scripts/pythia_*.py) which has no seat
  dossier. [IMPL from git]

## 2. Git-level facts [IMPL]

    commits reachable from origin/main      11,779  (no-merges 10,583; first-parent 4,269)
    commits on all refs                     11,932
    first commit                            ffb3639d4 2026-03-22 "initialize Prometheus"
    by month    2026-03 211 | 04 1,187 | 05 1,527 | 06 283 | 07 192 | 08 1,080 | 09 7,224 | 10 75
    top subject prefixes  Harmonia 472, Pythia 423, Techne 389, Aporia 355, Bellerophon 213,
                          Apollo 194, Ergon 192, Archaeon 173, Ananke 144, Ensorain 142, Nestor 140
                          (+ Nestor-A..G sub-instances ~570 together), Aphrodite 136
    roles/ directories                      72
    top-level directories                   80
    tracked files                           68,880 (.json 24,126; .md 19,653; .py 14,859; .gz 3,491)

Python line counts per top-level tree (git ls-files *.py, newline count; "code" = non-blank,
non-comment):

    tree                 files     lines    note
    agents               5,423  1,230,078   agents/hephaestus 5,274 files 1,193,520 lines, of which
                                            humanreadable 446k, scrap 252k, scrap_staging 162k,
                                            forge* 310k (LLM-forged ReasoningTool files); src 20k
    roles                2,213    294,854   roles/Ananke 104k (research/), roles/Nestor 92k
                                            (campaigns 427 files, inference_saturation_wave2 309),
                                            roles/Aphrodite 29k, roles/Harmonia 17.5k
    cartography            762    284,854   cartography/shared/scripts 181k, v2 97k
    prometheus_math        406    183,389   (69k in test files)
    forge                  488    138,490   forge/candidates 77k (forged), v2 47k
    charon                 401     94,837
    harmonia               327     79,571
    techne                 364     67,827
    ergon                  293     66,300
    primordial             472     65,571
    archaeon               363     59,462
    SerendipityFoundry     197     47,076
    aporia                 229     40,566
    apollo                 172     39,080
    prometheus             235     39,045   cosmos 85 files, toolbox 62, ananke 48, z80atlas 27
    Aether                 130     35,932
    theseus                196     35,563
    vivarium                99     29,078
    hecate                 188     28,180
    sigma_kernel            57     21,906
    proteus                140     20,863
    ensorain               176     19,351
    ludus 12.3k | herakles 8.3k | crius 6.9k | alien_circuitry 6.2k | tyche 5.4k | atlas 5.3k |
    fabric 3.9k | ares 3.8k
    TOTAL               14,859  3,193,194   (non-blank non-comment ~2.46M; test-file lines ~269k)

Rough family split [INFER; boundaries fuzzy, e.g. techne/harmonia mix instruments and pipelines,
roles/Nestor and roles/Ananke include campaign scripts]:

    LLM-forged / scrap tool files       ~1.25M  39%
    math-catalogue / falsification      ~0.86M  27%
    organism/world engines + campaigns  ~0.62M  20%
    institution (aporia, scripts, ew, atlas, fabric, odysseus, hephaestus seat code) ~0.12M 4%
    other / unclassified                ~0.34M  10%

Design reading: lines of code are anti-correlated with legibility of result. The mechanism-level
results that survive spot-check (Ares carrier, s9) came from a 3.8k-line package; the largest tree
in the repository is LLM output stored as source.

## 3. Artifact index analytics (1,802 rows)

### 3.1 Per seat [IMPL]
Sisyphus: Archaeon 55, Nestor 54, Proteus 47, Vivarium 43, Bellerophon 41, Herakles 38, Ludus 35,
Crius 33, Ares 31, Rhadamanthus 29, Daedalus 28, Apollo 28, Theophrastus 26, Lexis 25, Chiron 15.
Tantalus: Ananke 54, Ensorain 53, Aphrodite 46, Theseus 43, Ergon 43, Aether 42, Cosmos 40,
Tyche 37, Diomedes 32, Koios 30, Arachne 24, Talos 23, Nous 21, Polyhymnia 20, Icarus 20.
Tityos: Charon 51, Techne 40, Harmonia 39, Hecate 33, Nyx 30, shared 27, Nemesis 21, Hypatia 17,
Clymene 16, Artemis 14, Kairos 13, Elenchus 11, Pheme 10, Eos 9, Skopos 9, Coeus 8.
Ixion: Atlas 82, Mnemosyne 44, Aporia 32, Hephaestus 32, Pronoia 20, Odysseus 20, Achilles 19,
Archaeon 17, Hermes 16, Metis 16, Atalanta 12, Alethelia 11, Cyclops 10, unclaimed 9, Atlas-M2 8,
others <= 6. 66 distinct seat names overall; 12 seats appear in two packages (always Ixion plus
one science crawler: Ananke, Aphrodite, Archaeon, Artemis, Bellerophon, Cosmos, Daedalus, Ergon,
Harmonia, Nestor, Techne, Vivarium).

### 3.2 Normalised artifact type x package [IMPL counts; INFER normalisation]

    type             sisyphus tantalus tityos ixion  total   pct
    code                128      159     82    168    537   29.8
    result/report       126      139     82     56    403   22.4
    status/journal       77       28     31     96    232   12.9
    design/intent        70       71     37     22    200   11.1
    review/audit         62       28     63      0    153    8.5
    ledger/data          25       40     24     56    145    8.0
    prereg               15       30     14      0     59    3.3
    correction           19       20     11      0     50    2.8
    other                 6       13      4      0     23    1.3

Only 59 preregistration artifacts were indexed against 403 result/report artifacts (1:7), and
the dedicated correction-type artifacts (50) undercount corrections: CORR as an epistemic tag
appears on 154 rows (s3.3).

### 3.3 Epistemic category x package [IMPL]

    cat       sisyphus      tantalus      tityos        ixion         total
    IMPL      143 (27.1%)   181 (34.3%)   113 (32.5%)   258 (64.8%)   695 (38.6%)
    REPORTED  133 (25.2%)   127 (24.1%)    97 (27.9%)    28 ( 7.0%)   385 (21.4%)
    HIST      122 (23.1%)    75 (14.2%)    58 (16.7%)    44 (11.1%)   299 (16.6%)
    INTENT     80 (15.2%)    82 (15.5%)    44 (12.6%)    47 (11.8%)   253 (14.0%)
    CORR       50 ( 9.5%)    54 (10.2%)    35 (10.1%)    15 ( 3.8%)   154 ( 8.5%)
    INFER       0             4             1             6            11 ( 0.6%)
    UNK         0             5             0             0             5 ( 0.3%)

Seats with the highest CORR share (>= 10 rows): Techne 22%, Theseus 19%, Bellerophon 18%,
Nestor 17%, Lexis 16%, Apollo 14%, Charon 14%, Ergon 14%, Ares 13%, Diomedes 12%, Ananke 12%,
Hecate 12%. These are the seats where the record itself shows result revision; a high CORR share
is evidence of a working correction loop as much as of bad first readings.

### 3.4 phase3_relevance (free text; regex buckets, multi-label) [INFER]
ruler/instrument/control 350 (19%), provenance/governance 210 (12%), failure/defect/artifact 197
(11%), reuse/pattern/template 175 (10%), organism/substrate 88 (5%), pressure/selection 77 (4%),
memory/hidden/reasoning/composition 62 (3%), world/environment 55 (3%), replication/statistics
46, mechanism/ablation 41, llm 28; 834 rows hit no bucket. Top words: reusable 74, design 70,
instrument 67, ruler 52, pattern 49, failure 48, never 47, deterministic 45, control 44, null 38,
provenance 36. The crawlers judged the corpus relevant to Phase 3 mainly as a source of rulers,
failure patterns and provenance discipline, rarely as a source of organisms or worlds.

### 3.5 Duplicates [IMPL]
1,737 distinct artifact paths; 43 (2.5%) indexed by more than one package (ixion+tityos 11,
ixion+sisyphus 10, sisyphus+tityos 9, tantalus+tityos 8, ...; 2 paths in three packages:
roles/Ananke/prompts/2026-09-26_c1b_operator_release/..., roles/base-role/RESPONSIBILITIES.md).
Within-package duplicate paths: sisyphus 10, tityos 9. The crawlers partitioned the territory
cleanly; overlap is mostly shared infrastructure (evidence_wiki, sigma_kernel, Necropolis,
Artemis results consumed by Nestor).

## 4. Engine index analytics (171 science/ruler engines + 76 institutional)

### 4.1 Coding scheme (my judgement from each record's own fields) [INFER]
- cls: SIM organism(s) evaluated/adapting in a world; BENCH world/task suite with fixed or external
  solver; SUBSTRATE organism VM without campaign; GEN generator without environment; INSTR
  ruler/lens/audit/forensic; MATH catalogue/claim pipeline; LLM generation/review/literature;
  INFRA platform/ledger/catalogue; DESIGN not built.
- adapt: POP population search over organisms; LIFE within-lifetime learning/plasticity/
  accumulation; BOTH; NONE fixed; NA no organism.
- hidden: LATENT latent variable inferred from interaction (regime, hidden card/rule/relabelling);
  MEM needs memory of past observations only; STATIC hidden static target or field revealed via
  score/samples; NONE fully observed; NA no world.
- ruler: Ye exact-by-construction score (oracle, DP, enumeration); Yp planted/control-demonstrated
  recovery recorded; P partial (synthetic only, weak/forced controls, self-reported); N not shown
  or shown to fail; U unknown; NA none.
- demand ladder: D0 none; D1 lookup/static map/static optimisation/correlation; D2 estimation/
  interpolation; D3 1-bit latch or one-cue delayed recall; D4 small FSM/sequential/parity/
  multi-item memory/game depth-k; D5 hidden-state inference; D6 composition/procedure reuse/
  planning. "Designed" = what the world was built to demand; "realised" = what the records say
  solutions actually needed (U = never verified).

### 4.2 Distributions (n=171) [INFER codes over IMPL records]

    engine class   INSTR 58 | SIM 34 | BENCH 22 | INFRA 19 | LLM 16 | MATH 14 | DESIGN 5 |
                   SUBSTRATE 2 | GEN 1
    world          LEDGER/records 36 | none 36 | MATH catalogue 25 | EPISODIC toy/event 17 |
                   STATIC landscape/function 12 | CA/lattice 11 | TEXT battery 11 | FIELD/process 8 |
                   BYTE-VM soup 7 | FINITE enumerated 5 | GAME 3
    organism       none/NA 84 | evolved programs/tapes/graphs 24 | fixed hand-written/historical 23 |
                   LLM 18 | statistical learner/estimator 9 | evolved nets 4 | hypothesis records 4 |
                   RL policy 3 | ES 1 | bitstring genome 1
    adapt          NA 105 | POP 29 | NONE 22 | LIFE 12 | BOTH 3
    hidden         NA 107 | NONE 29 | MEM 12 | LATENT 12 | STATIC 11
    own ruler      P 87 | N 47 | Yp 15 | Ye 10 | U 8 | NA 4
    demand design  D0 100 | D1 28 | D4 13 | D5 10 | D6 5 | D3 5 | D2 5 | U 5
    demand real    D0 102 | D1 36 | U 14 | D3 8 | D4 6 | D2 4 | D5 1
    build status   ran 156 | built-never-run-on-science 10 | design only 5

Per crawler: Sisyphus supplied 20 of the 34 simulations and 20 of the 24 evolved-program
organisms; Tantalus supplied all 9 statistical learners and 8 of the 8 field worlds; Tityos
supplied 39 of the 58 instruments and 28 of the 36 records-as-world entries. The "worlds" of the
immune-system lane are mostly the program's own ledgers.

Subset organism/world engines (n=62: SIM/BENCH/GEN/SUBSTRATE/LLM with a world): adapt POP 27,
NONE 20, LIFE 9, BOTH 3; hidden NONE 26, LATENT 11, STATIC 10, MEM 10; ruler P 44, N 8, Ye 5,
Yp 4; realised demand D1 29, D0 9, U 8, D3 6, D4 5, D2 4, D5 1.
Subset SIM (n=34): worlds EPISODIC 10, STATIC 7, FIELD 6, TEXT 5, BYTE-VM 4; organisms evolved
programs 18, learners 5, fixed 5, evolved nets 3; realised demand D1 20, D3 4, D2 4, U 4, D0 2.

### 4.3 Headline questions
(a) adapting organism: 44/171 (25.7%). With lifetime learning (LIFE/BOTH): 15 = Ares, Crius,
    Ensorain E-engine, D-series, WTP-01, WTP-02, WTP-03, WTP-LM01, ARC3, Ergon E2c LoRA,
    AlienCircuitry, prometheus_math RL envs, Cognitive Ceiling v0 (artifact store), Lehmer RL,
    Techne cross-domain RL.
(b) latent hidden state: 12/171 (7.0%): Archaeon C6 observatory [realised U], Archaeon Deep
    Frontier [U], World Foundry wforge [U], Primordial Machine [D0: abstain floor wins], Ares [D3],
    Ludus arena (Kuhn poker, epistemic world) [U], Crius RELAY [U, contested], Ensorain WTP-LM01
    [never launched], Ensorain ARC3 [D5], Cognitive Ceiling v0 (hidden Z_3^3, lossy sensor) [U],
    Hecate alien-lawful assay [D1: table coverage], Nyx reading of Ares W4 [D3].
    LATENT or MEM: 24 (14%). STATIC hidden target/field: 11.
(c) own ruler with demonstrated detectability: 25/171 (14.6%):
    exact-by-construction (10): Archaeon policy bench (DP), cegis_boolean (8/8 coverage),
    evaluate_bitstring, SFE executors (certified optimum), proteus.eval (exhaustive oracle),
    Apollo O1 enumerator, Ensorain ARC3 (exact Bayes), Diomedes Lane N (exact oracle AUC),
    Diomedes Arm A (exact, vacuous), Polyhymnia PROBE-01 (exact single-flip reach).
    planted/control-demonstrated (15): Ensorain D-series (synthetic additive/coupled), WTP-03 (XC vs
    N0-N5 nulls, planted same-class fit), Cosmos C3 (planted classes 5/5), Aphrodite Campaign 0
    (own generative model), Ergon E4 (3 pp planted effect at n=100, MDE80 1.22 pp), Artemis CVT
    heredity panel (constructed specimens), Charon generator census (C1 rediscovery), Clymene vault
    audit, SFE conformance gate, Hecate Wave-2 audit harness, cheatlib, fossil vault hashes,
    Necropolis admissibility ladder (2 records), attack registry/preflight.
(a)&(b): 8. (a)&(b)&(c): 1 (Ensorain ARC3). (a)&(LATENT or MEM)&(c): still 1.

### 4.4 Designed versus realised demand (23 gaps) [INFER]
Archaeon WSE D4->D3 (two-stream keyed memory 0/60); damage harness D4->D3; C6 observatory D5->U
(G6-0 never verified, rulers saturated); Deep Frontier D5->U; D-13 Foundry D4->D1; wforge D5->U;
Primordial D5->D0; CW01 bespoke D6->D1 (organisms could not express state use or composition);
Worlds Kernel D3->U; Ares D5->D3; Ludus cycle-001 D4->D1 (greedy-decidable); Ludus arena D5->U;
Apollo Branch C D6->D1 (template parsers); herakles.ca_stream D4->D0 (v1 provably inert);
Crius D6->U; WTP-02 D2->D1 (learned constant admitted); WTP-LM01 D5->U; PTE D4->D3; Aphrodite
G4/W5 D6->D1 (additive folds); Icarus D4->D1 (R5 solvable by label lookup); Cognitive Ceiling
D5->U; Hecate alien-lawful D5->D1; ladder_circuits D6->U.
Realised demand >= D4 occurs in 7 engines, and in 5 of them the solution was a fixed hand-written
or historical artefact (CA density rules, proteus.eval witnesses, Ludus circuits); the two
learned cases are ARC3 estimators (D5) and AlienCircuitry representations (D4, navigation in an
enumerable graph). No evolved organism in the index has a verified realised demand above D3.

### 4.5 Toy / prototype by own record [IMPL keyword counts]
"toy" 16 (9.4%); prototype/pilot/MVP/demo/stub 9; never-run/never-launched/design-only/never-
applied markers 25 (14.6%); any of these 45 (26.3%); plus tiny/small/single/one-seed/underpowered
markers 81 (47.4%). Organism/world subset: 34% (58% with size markers); SIM subset: 29% (59%).

### 4.6 Pressure and ruler vocabularies (regex, multi-label, n=171) [INFER]
pressure_type: none/n.a. 89; selection/search 29; economy/cost/energy 20; world schedule/drift/
catastrophe/curriculum 13; learning signal (SGD/RL/supervised) 8; endogenous reproduction 4.
ruler_type: planted/positive/cheat/synthetic/fixture/control 38; null/permutation/shuffle/twin 37;
exact/oracle/enumeration 26; intervention (ablation/knockout/transplant/swap/sham/reset) 24;
provenance/hash/receipt 21; replication/held-out/fresh-seed 18; LLM judge/review 9.
Note the gap between naming controls in a ruler (38) and having demonstrated detectability (25,
of which 10 are exact scorers).

### 4.7 Tantalus representation-richness audit (n=46 engines) [REPORTED]
hierarchy YES 0 (NO 32); binding YES 1 (NO 34); temporal YES 0 (NO 32); recurrence YES 2 (NO 30);
counterfactual YES 3 (NO 31); latent YES 2 (NO 23); reusable YES 1 (NO 19); routing YES 1;
compositional YES 2 (PARTIAL 19); memory YES 5 (PARTIAL 16). The Tantalus territory (substrates,
representation, synthetic cognition) almost never instantiated hierarchy, binding, temporal
structure or routing in an organism.

### 4.8 Ixion institutional systems (n=76) [REPORTED, partly IMPL-verified by Ixion]
status: dormant 34, live 21, retired 14, unknown 7. inference_dependency: INFERENCE_FREE 53,
MODEL_MEDIATED 14, ASSISTED_PLAUSIBLY_DETERMINISTIC 8, OCCASIONAL_JUDGMENT 1. scheduling: manual
39, schtasks 11, daemon 10, loop-in-session 7, event 6. Tests none/unknown: 30 of 76. Ixion's own
verification of 9 sub-crawler claims found 1 wrong (operator brief is deterministic by default,
metis_portfolio.py:452-460) [REPORTED by Ixion, CORR recorded in its engine row].

## 5. Ruler inventory (Tityos, 152 rows = 146 distinct instruments) [IMPL counts of REPORTED fields]

    detectability_demonstrated  rows: no 60 | partial 56 | yes 30 | unknown 5 | n/a 1
    distinct (best status)            no 57 | partial 53 | yes 30 | unknown 5 | n/a 1
    cross_substrate_transfer_tested   no 124 | partial 23 | n/a 3 | yes 2 (one "transfer failed")
    positive_controls field empty/none 62 of 152; negative_controls empty/none 53 of 152
    necropolis_status set on 16 rows (READY 8, READY_WITH_CAVEAT 3, UNTRUSTED 2, NEEDS_VALIDATION 2,
    NEEDS_DEPENDENCY 1)

What the 30 "yes" instruments detect [INFER classification]:
- integrity / provenance / pipeline correctness (~20): TR-007 detector-band census, TR-011 floor
  precheck, TR-012 audit primitives, TR-017 conformance gate, TR-021 tautology precondition,
  TR-061 fossil hash preservation, TR-077/078/079 Hecate validator/metamorphic/exact-arithmetic,
  TR-091 cheatlib chance floor, TR-126 seam leak probe, TR-128 stripped-text leak classifier,
  TR-130 admissibility preflight, TR-131 pool fingerprint, TR-137/138 Clymene repo probes,
  TR-142/143 Hypatia parse census and stall predicate, TR-146 ATK-014, TR-151 Necropolis ladder.
- statistical method calibrated on synthetic/planted data (~7): TR-035 equivalence-ruler
  calibration pair, TR-050 modal-collapse null, TR-052 Theseus F2, TR-111 battery_v2 F24,
  TR-116 Erebos A1-A10, TR-133 generator census v2, TR-136 TT-rank recovery.
- mathematical ground truth (2): TR-023 closed-form SDP, TR-047 Lehmer brute force.
- organism property (1): TR-084 CVT-2/CVT-R heredity certificates (constructed panel).
The program got good at catching its own pipeline defects; it almost never demonstrated that a
phenomenon detector would fire on a planted instance of the phenomenon in an organism.

## 6. Duplicates across crawlers (engines) [IMPL path overlap, INFER identity]
19 cross-package engine pairs share a path. Same system described twice: Necropolis workshop
(Sisyphus/Tityos), sigma_kernel (Tantalus/Tityos), Theseus claim/substrate daemon (Tantalus/
Tityos), Worlds Kernel (Sisyphus/Ixion). Overlapping perspectives on one system: Evidence Wiki
(Tityos 1 row vs Ixion 5 component rows), prometheus_math envs vs techne/lib arsenal, Ergon E3
probe vs Charon kill-authority apparatus (experiment vs its audit), SFE vs SFE deploy tooling,
Elenchus shadow review vs shadow WORKLOG, Cosmos C0 vs Cosmos holdout broker. Within-package
shared-path pairs: 68 (mostly wrappers over one library, e.g. Vivarium kinds over herakles/proteus,
and the F1-F38 falsification battery family recorded three times in Tityos plus TR-001/110/149).
Net: 247 records describe ~240 distinct systems; disagreements are rare and annotated (Ixion 4
notes + 1 correction).

## 7. The most informative experimental geometries visible from the index
(Geometry = organism with variation x world with a demand above D1 x ruler with interventions.
Only these rows had the capacity to reveal machinery; everything else could at most reveal
pipeline behaviour, static-map fitting or ledger statistics.)

1. Ares carrier microscope [S9-confirmed]: batched dataflow organisms with recurrence, leak and
   Hebbian plasticity; 16 toy episodic worlds with present/absent/shuffled modes; node, edge and
   SCC ablations. Could reveal WHICH carrier (recurrent activation vs leak vs plastic weight)
   holds a one-bit cue across a delay, and how carriers diversify under longer/noisier delays.
   Could not reveal anything above a 1-bit latch (world demand).
2. Crius RELAY [S9-confirmed world]: hidden per-stream relabelling of 12 primitives and a hidden
   procedure library; 50-task lifetimes; persistent workspace and executable block store; FRESH vs
   ACCUMULATED reuse_gain with RESET/SCRAMBLE/ABLATION/TRANSPLANT battery. The only engine whose
   world demands within-life procedure reuse (D6) with a mechanism battery; realised result
   contested (id-counter clocks pass ACC>FRESH by the letter; partial steps +-0.001 unresolvable).
3. Ensorain ARC3 [S9-confirmed source]: binary processes incl. Even process (finite causal state,
   no finite window) scored as excess log-loss against exact Bayes; CONST/TABLE/MARGINAL cheap
   competitors. The cleanest hidden-state ruler in the corpus; the "organisms" are hand-chosen
   estimators (STAT(k), HMM, CSSR), so it measures representational adequacy, not development.
4. Cosmos C3 usable-history certificate: P1 decodability with stratified permutation null + P2
   paired-CRN full-state swap ablation; separates planted classes 5/5 at V=4 k=6. A validated
   ruler for D3 memory, applied to fixed systems.
5. PTE mechanism lens: mirror-partner carrier swaps and resets with certified pair-bootstrap; exact
   counterfactuals at named ticks; but 1-bit tasks and forced controls in C1.
6. Ergon E4: per-lineage paired CFR with planted-witness cheat control and stated MDE (1.22 pp);
   the best-powered evolutionary comparison in the index; world is independent table fitting (D1).
7. Archaeon WSE + C2 transport: evolved VM programs on delayed keyed-memory event streams with
   held-out confirmation and preregistered falsification; produced honest negatives (two-stream
   keyed memory 0/60; relevant transport hurt, -0.160 held-out, 1/6 seeds) [C2 S9-confirmed].
8. Charon Cognitive Ceiling v0 [S9-confirmed source]: hidden Z_3^3 state, 4 opaque shift actions,
   lossy sensor, interaction budget, held-out long-word prediction vs chance/oracle. The one
   hidden-rule-inference world with an explicit oracle; solver was a frozen LLM or a non-model
   proposer, not a developing organism; spec reconstructed after data loss.

## 8. Failure shapes visible only in aggregate
- Demand collapse: 15 engines designed for >= D5, 1 realised; 23 designed > realised gaps; no
  evolved organism verified above D3. Classes: world_insufficiency (Ares one bit, Primordial
  abstain floor, Ludus greedy-decidable), organism_insufficiency (CW01 e07/e09, WSE no call/stack/
  addressing), search_insufficiency (Crius budget, D-13 85/87 ties), ruler_insufficiency (C6
  saturated/UNABLE, ca_stream linear readout cannot express XOR).
- Ruler inversion: detectability demonstrated mostly for integrity instruments (~20/30 "yes"), and
  only 1 organism-property instrument; 124/152 rulers never tested across substrates. Phenomenon
  claims therefore rested on rulers of unknown sensitivity (false-negative risk) and of unknown
  specificity (false-positive risk) at the same time.
- Instrument hypertrophy: 58 instruments vs 34 simulations; Tityos alone indexed 146 distinct
  rulers. Many instruments were never applied to science (10 engines BUILT but never run on a
  real question; 25 never-run markers).
- Generator-scorer coupling: same author for world and baseline (Ludus), auditor-built specimens
  (Artemis), adjudicator-built instruments (Nyx/Harmonia), generator self-verdicts 99.98%
  (Theseus), same-family LLM reviewers (Charon council, Elenchus, Hecate) [REPORTED].
- Volume without depth: September 2026 = 61% of all commits; 658M Theseus records; 3.7M Archaeon
  Deep Frontier evaluations; 101k Z80 runs; yet realised demand stayed at D1-D3.
- Correction pressure: CORR:REPORTED = 0.39 in the science packages; highest in Techne, Theseus,
  Bellerophon, Nestor.

## 9. Spot-checks against source (what I confirmed myself) [IMPL unless noted]
- Ares W4: ares/ARES_CYCLE1_REPORT.md s3.1-3.3 (lines 82-114): self-loops in 9/10 W4 champions,
  self-loop cut collapses 6/10, KEEP cut 0/10, "the early cue is held in RECURRENT ACTIVATION";
  W5 (26-step delay) plasticity load-bearing 8/10; cycle-0 "accreted" claim retracted (CORR).
- Primordial abstain floor: primordial/ledger/G.jsonl exp G-M1-floors-w134 (git 5d846f9ce):
  "a 0-byte do-nothing policy beats every w1/w3/w4 held64 baseline ... the QD archives never
  reached it"; rejudge_record_cells_below_floor "28/28"; independent conductor re-derivation.
- Crius world: crius/world_c1.py lines 1-8: "per-stream relabeling, hidden procedure library";
  12 primitives (INC/DEC/SWAP x 4 positions) mapped by a hidden permutation.
- PTE task families: prometheus/ananke/analysis_a0.py and assays.py name RELAY/XOR/MAJ/HOLD/FLIP;
  c1b.py adjudicates "delay-line HOLD memory".
- Ensorain ARC3: ensorain/arc3/THREADS.md:222 "W3 Even process (finite causal state, no finite
  window)"; :311 "a 2-state EM-HMM reaches Bayes on the Even process".
- Cognitive Ceiling: charon/ceiling_v0/ITERATION_LOG.md:13 "Hidden state Z_3^3 (27 states), 4
  opaque actions each a hidden shift".
- Archaeon C2 transport negative: archaeon/campaign2/C2-SFE-01/RECORD.md:83 (relevant - fresh =
  -0.160 held-out; CAPABLE_NEGATIVE accepted; preregistered falsification fired).
- Chiron CDE: git ls-files on HEAD shows no chiron code outside docs/phase3/intake (design only).
- Hephaestus forge mass: git ls-files agents/hephaestus -> 5,274 .py files, 1,193,520 lines;
  e.g. agents/hephaestus/forge/active_inference_x_free_energy_principle_x_model_checking.py.

## 10. Design implications (each tied to evidence above)
1. Make world demand a measured, preregistered quantity with an ablated-capability baseline per
   world (present/absent/shuffled as in Ares), because 23/171 engines realised less than designed
   and no evolved organism exceeded D3 (s4.4).
2. Gate every phenomenon ruler on a planted-positive / matched-negative panel inside the target
   substrate before any campaign; the corpus has 30/146 instruments with demonstrated
   detectability and only 1 that measures an organism property (s5).
3. Require a constructive existence proof that the organism substrate can express the target
   machinery (hand-written witness, as proteus.eval and the CA/Ludus fixed solutions did) before
   searching for its emergence; CW01 and WSE failures were organism_insufficiency discovered late.
4. Put lifetime learning and population variation in the same organism by design; only 3/171
   engines had both (Ares, Crius, Ensorain E0), and only Ares showed by ablation that the
   plastic channel was load-bearing (W5 8/10) (s0.4, s9).
5. Build worlds with genuine latent state and an exact oracle (ARC3 Even process, ceiling_v0
   Z_3^3, Crius hidden library are templates as geometries); 12/171 had latent state and only one
   was paired with a demonstrated ruler (s4.3).
6. Keep engines small and legible: the results that survive mechanistic reading came from 3.8k-
   6.9k-line packages, while 39% of Python lines are LLM-forged tool files (s2).
7. Count instruments only when applied: 10 engines were built but never run on a question, and
   instruments outnumber simulations 58:34 (s4.2); the architecture should bind each ruler to an
   engine and a phenomenon.
8. Separate generator, world author, scorer and adjudicator, and log independence explicitly; the
   aggregate failure shapes (s8) repeatedly involve self-built rulers and same-family review.
9. Report realised demand, ruler validity and replication as first-class fields in any future
   engine index; the four crawlers had to reconstruct them by reading, with heterogeneous schemas
   (s1), and 834/1,802 relevance notes fit no analytic bucket.
10. Treat transfer across substrates as untested by default (124/152 rulers "no").

## 11. Open questions
- Realised demand codes marked U (14 engines) need a per-engine reader: especially Crius (D6
  claim contested), Archaeon C6/Deep Frontier (D5 designed, rulers saturated), wforge, Ludus arena.
- The organism/world line-count split (s2) is coarse; roles/Ananke/research (862 files) and
  roles/Nestor/inference_saturation_wave2 (309 files) were not inspected for what they contain.
- Host-local data (M2 ledgers, BEE results, Archaeon off-repo) is outside every index; any
  replication claim depending on it is unverifiable from git.
- Whether the 15 Yp detectability claims survive re-execution: all are REPORTED by crawlers from
  receipts; none were re-run here.
- Pythia (423 commits) and 7 legacy roles dirs were not crawled.

## 12. Files opened by this reader
docs/phase3/intake/sisyphus/{artifact_index,engine_index}.jsonl, REPORT.md (head)
docs/phase3/intake/tantalus/{artifact_index,engine_index}.jsonl, REPORT.md (head)
docs/phase3/intake/tityos/{artifact_index,engine_index,ruler_inventory}.jsonl, REPORT.md (head)
docs/phase3/intake/ixion/{artifact_index,engine_index}.jsonl, REPORT.md (head)
ares/ARES_CYCLE1_REPORT.md (lines 75-114); crius/world_c1.py (head); techne/ladder_circuits/
canon_r12_conjecture.py (head); grep hits only: primordial/ledger/G.jsonl, primordial/ledger/
B.jsonl, archaeon/campaign2/C2-SFE-01/RECORD.md, ensorain/arc3/THREADS.md, charon/ceiling_v0/
ITERATION_LOG.md, prometheus/ananke/{analysis_a0,assays,c1b}.py, docs/phase3/intake/sisyphus/
seats/Nestor.md (grep), prometheus/z80atlas/vm.py (grep), roles/Bellerophon/forensics_2026-09-23/
GROUNDING_*.md (grep). Git metadata: rev-list, log subjects, ls-tree, ls-files, line counts.

## Appendix A. Per-engine codes (171 rows; INFER; order = crawler file order)

    #   pkg  engine (truncated)                                   cls       world    organism   adapt hidden ruler demand(d>r) built
    1   sis  Archaeon v0 fossil-to-queue producer + detectors D1- INSTR     LEDGER   NONE       NA    NA     P     D0>D0   RAN
    2   sis  Archaeon exact producer-policy bench (seasons S1-S7, BENCH     STATIC   FIXED      NONE  STATIC Ye    D1>D1   RAN
    3   sis  Archaeon WSE workspace ecology on the Proteus VM     SIM       EPISODIC EVO-PROG   POP   MEM    P     D4>D3   RAN
    4   sis  Archaeon damage-geometry / Representation B harness  INSTR     EPISODIC EVO-PROG   POP   MEM    N     D4>D3   RAN
    5   sis  Archaeon Campaign 6 observatory + composed worlds +  SIM       EPISODIC EVO-PROG   POP   LATENT N     D5>U    RAN
    6   sis  Archaeon Deep Frontier lineage scheduler             SIM       EPISODIC EVO-PROG   POP   LATENT N     D5>U    RAN
    7   sis  Archaeon Z80 x Atlas ecology (third Z80 build)       SIM       BYTEVM   EVO-PROG   POP   NONE   P     D1>D1   RAN
    8   sis  Archaeon ENVGATE environment-as-variable assay + byt SIM       BYTEVM   EVO-PROG   POP   NONE   P     D1>D1   RAN
    9   sis  Archaeon causal lineage lens / attribution v0        INSTR     LEDGER   NA         NA    NA     P     D0>D0   RAN
    10  sis  Vivarium data plane (viv queue + SFE runner + PEW ou INFRA     NA       NONE       NA    NA     NA    D0>D0   RAN
    11  sis  ca_density_v0 (Vivarium wrapper over herakles/evca)  BENCH     CA       FIXED      NONE  NONE   P     D4>D4   RAN
    12  sis  cegis_boolean_v1 (Vivarium kind over proteus/eval Bo BENCH     STATIC   FIXED      NONE  NONE   Ye    D1>D1   RAN
    13  sis  eca_rule_eval_v1 (Vivarium wrapper over herakles/eca BENCH     CA       FIXED      NONE  NONE   P     D0>D0   RAN
    14  sis  evaluate_bitstring (Vivarium kind over SFE reference BENCH     STATIC   NONE       NONE  STATIC Ye    D1>D1   RAN
    15  sis  Serendipity Foundry Engine (SFE) /v2                 INFRA     NA       NONE       NA    NA     NA    D0>D0   RAN
    16  sis  SFE reference executors (bitstring, nk_landscape_v0) BENCH     STATIC   NONE       NONE  STATIC Ye    D1>D1   RAN
    17  sis  Gen-2 canary driver                                  SIM       STATIC   EVO-GENOME POP   STATIC N     D1>D1   RAN
    18  sis  D-9/D-13 Serendipity Foundry /v0 (off-repo ancestor) SIM       STATIC   EVO-PROG   POP   MEM    P     D4>D1   RAN
    19  sis  World Foundry v0 / wforge                            BENCH     EPISODIC FIXED      NONE  LATENT P     D5>U    BUILT
    20  sis  Microstructure Hadron Collider (MHC) + admission led INSTR     LEDGER   FIXED      NONE  NA     N     D0>D0   BUILT
    21  sis  Primordial Machine (graphworld swarm)                SIM       EPISODIC EVO-NET    POP   LATENT P     D5>D0   RAN
    22  sis  CW01 bespoke worlds                                  SIM       EPISODIC EVO-NET    POP   MEM    P     D6>D1   RAN
    23  sis  CW01 loop on Proteus/Archaeon tape VM (consumer)     SIM       EPISODIC EVO-PROG   POP   MEM    P     D3>D3   RAN
    24  sis  NPE: Nestor Z8 engine (Z80 x Atlas / Cycle-9)        SIM       BYTEVM   EVO-PROG   POP   NONE   P     D1>D1   RAN
    25  sis  Ancestry-replay shadow tracer                        INSTR     BYTEVM   NA         NA    NA     P     D0>D0   RAN
    26  sis  Worlds Kernel (prometheus.toolbox)                   SIM       EPISODIC EVO-PROG   POP   MEM    P     D3>U    RAN
    27  sis  BEE: Z80 soup (prometheus.z80atlas)                  SIM       BYTEVM   EVO-PROG   POP   NONE   P     D1>D1   RAN
    28  sis  Ares pressure-engineering sandbox (carrier microscop SIM       EPISODIC EVO-NET    BOTH  LATENT P     D5>D3   RAN
    29  sis  proteus.foundry v0 (Player Foundry VM + grammar)     SUBSTRATE NA       EVO-PROG   NA    NA     NA    D0>D0   BUILT
    30  sis  Proteus mutation-kernel crucibles (V0.3-V0.6)        INSTR     NA       EVO-PROG   NA    NA     P     D0>D0   RAN
    31  sis  proteus.graph graph_organism.v1                      SUBSTRATE NA       EVO-PROG   NA    NA     P     D0>D0   BUILT
    32  sis  proteus.eval identity/witness/mint toolkit           INSTR     STATIC   FIXED      NONE  MEM    Ye    D4>D4   RAN
    33  sis  Ludus cycle-001 authored worlds + depth profile      BENCH     GAME     LLM        NONE  NONE   P     D4>D1   RAN
    34  sis  Ludus bench (stopping/selection transfer matrix)     BENCH     GAME     FIXED      NONE  NONE   P     D4>D4   RAN
    35  sis  Ludus arena (universal world/player interface + epis BENCH     GAME     FIXED      NONE  LATENT P     D5>U    RAN
    36  sis  Ludus Atlas of Game Worlds                           INFRA     NA       NONE       NA    NA     N     D0>D0   RAN
    37  sis  Theophrastus contrast-first ecology explorer (harnes BENCH     CA       FIXED      NONE  NONE   P     D4>D4   RAN
    38  sis  Apollo v1 forge-tool gene splicer                    SIM       TEXT     EVO-PROG   POP   NONE   P     D1>D1   RAN
    39  sis  Apollo v2 routing-DAG evolver (v2-beta..v2d)         SIM       TEXT     EVO-PROG   POP   NONE   P     D1>D1   RAN
    40  sis  Apollo Branch C blackboard evolver                   SIM       TEXT     EVO-PROG   POP   NONE   P     D6>D1   RAN
    41  sis  Apollo analysis instruments (O1 enumerator, E1 sched INSTR     TEXT     NA         NA    NA     Ye    D0>D0   RAN
    42  sis  Apollo Gen-2 Serendipity adapter + Source Viability  SIM       STATIC   EVO-PROG   POP   NONE   P     D1>D1   RAN
    43  sis  Lexis vocabulary-closure and admission instruments   INSTR     TEXT     FIXED      NA    NA     P     D1>D1   RAN
    44  sis  herakles.evca (EvCA density-classification library)  BENCH     CA       FIXED      NONE  NONE   P     D4>D4   RAN
    45  sis  herakles.eca (eca_rule_eval_v1)                      BENCH     CA       FIXED      NONE  NONE   P     D0>D0   RAN
    46  sis  herakles.ca_stream (CA streaming-memory probe)       BENCH     CA       FIXED      NONE  MEM    P     D4>D0   RAN
    47  sis  HC-T01 Toussaint reconstruction (hct01.c)            SIM       STATIC   EVO-PROG   POP   NONE   P     D1>D1   RAN
    48  sis  Necropolis autopsy court (engine/necropolis)         INSTR     LEDGER   NA         NA    NA     P     D0>D0   RAN
    49  sis  Necropolis workshop / tool morgue                    INSTR     LEDGER   NA         NA    NA     Yp    D0>D0   RAN
    50  sis  Crius adaptive-workspace sandbox (accessibility fron SIM       EPISODIC EVO-PROG   BOTH  LATENT P     D6>U    RAN
    51  sis  Chiron Developmental Engine (CDE) / Engine Five -- D DESIGN    NA       NONE       NA    NA     U     U>U    DESIGN
    52  tan  Ensorain E-engine (E0/E1/E1.5/E2)                    SIM       FIELD    LEARNER    BOTH  STATIC P     D2>D2   RAN
    53  tan  Ensorain D-series dial engine                        SIM       FIELD    LEARNER    LIFE  STATIC Yp    D2>D2   RAN
    54  tan  Ensorain WTP v1 foundry (WTP-01)                     SIM       FIELD    LEARNER    LIFE  STATIC N     D2>D2   RAN
    55  tan  Ensorain WTP v2 executor (WTP-02)                    SIM       FIELD    LEARNER    LIFE  STATIC P     D2>D1   RAN
    56  tan  Ensorain WTP v3 substrate collider (WTP-03)          SIM       FIELD    LEARNER    LIFE  STATIC Yp    D2>D2   RAN
    57  tan  Ensorain WTP-LM01 harness                            BENCH     FIELD    LEARNER    LIFE  LATENT U     D5>U    BUILT
    58  tan  Ensorain ARC3 dev instruments (suff / PKG-F / LM02)  BENCH     FIELD    LEARNER    LIFE  LATENT Ye    D5>D5   RAN
    59  tan  PTE (Packet-Tensor Engine) substrate + GA + task fam SIM       EPISODIC EVO-PROG   POP   MEM    P     D4>D3   RAN
    60  tan  PTE mechanism lens (carrier swaps / C1b batteries)   INSTR     EPISODIC NA         NA    NA     P     D0>D0   RAN
    61  tan  Wave-2 instrument certification stack (unpromoted)   INSTR     EPISODIC NA         NA    NA     P     D0>D0   RAN
    62  tan  theseus.synth (concept tensor / synthetic ancestry)  GEN       CA       NONE       POP   NA     N     D0>D0   RAN
    63  tan  May 2026 theseus claim-generation engine             MATH      MATH     HYP        NA    NA     P     D0>D0   RAN
    64  tan  CWE C0 chamber (law miner + regs/ring/ca)            BENCH     EPISODIC FIXED      NONE  MEM    P     D3>D3   RAN
    65  tan  C3 P1/P2 usable-history certificate (+ withheld visi BENCH     EPISODIC FIXED      NONE  MEM    Yp    D3>D3   RAN
    66  tan  C4 successor design (upstream causes of usable histo DESIGN    NA       NONE       NA    NA     U     U>U    DESIGN
    67  tan  aeth01.v1 lattice physics + AETH-03 variant laws     SIM       CA       NONE       NONE  NA     P     D0>D0   RAN
    68  tan  RunPod GPU platform (prometheus_gpu + AGE canary/con INFRA     NA       NONE       NA    NA     NA    D0>D0   RAN
    69  tan  Tyche lens ecology (v0-v2)                           SIM       FIELD    FIXED      POP   MEM    P     D1>D1   RAN
    70  tan  Tyche residual catalogue                             INFRA     LEDGER   NONE       NA    NA     P     D0>D0   RAN
    71  tan  Aphrodite RSI toy E2 (self-referential ES)           SIM       STATIC   ES         POP   NONE   P     D1>D1   RAN
    72  tan  Aphrodite local engine v1 (membrane + endogenous dis SIM       TEXT     FIXED      POP   NONE   P     D1>D1   RAN
    73  tan  Aphrodite G4/W5 library-inheritance engine (Tier 3 t SIM       STATIC   FIXED      POP   NONE   P     D6>D1   RAN
    74  tan  Aphrodite Campaign 0 synthetic assay                 INSTR     NA       NA         NA    NA     Yp    D0>D0   RAN
    75  tan  Ergon E1 tensor-native hypothesis engine (April 2026 MATH      MATH     HYP        NA    NA     P     D1>D1   RAN
    76  tan  Ergon E2 Learner typed-DAG MAP-Elites                MATH      MATH     EVO-PROG   POP   NA     N     U>U    RAN
    77  tan  Ergon E2c LoRA / compute-trace / routing learners    LLM       TEXT     LLM        LIFE  NONE   P     D1>D1   RAN
    78  tan  Ergon E3 metabolization probe                        BENCH     TEXT     LLM        NONE  NONE   P     D1>D1   RAN
    79  tan  Ergon E4 retention-policy lineages on D-5 register m SIM       STATIC   EVO-PROG   POP   STATIC Yp    D1>D1   RAN
    80  tan  Ergon E5/E6 historical forensics and latent-neighbou DESIGN    NA       NONE       NA    NA     U     U>U    DESIGN
    81  tan  Diomedes Lane N candidate ranker (h1 counterfactual  INSTR     MATH     LEARNER    NA    STATIC Ye    D1>D1   RAN
    82  tan  Diomedes Arm A operator-commutation enumeration      INSTR     MATH     NONE       NA    NA     Ye    D1>D1   RAN
    83  tan  Diomedes K0 coordinate census                        INSTR     NA       NA         NA    NA     P     D0>D0   RAN
    84  tan  Diomedes representational-multiplicity Diagnose pref DESIGN    NA       NONE       NA    NA     U     U>U    DESIGN
    85  tan  Polyhymnia Omnitensor daemon                         INFRA     LEDGER   NONE       NA    NA     N     D0>D0   RAN
    86  tan  Polyhymnia PROBE-01 lincode decoder family           INSTR     CA       NONE       NA    NA     Ye    D0>D0   RAN
    87  tan  TalosCorpusDaemon                                    INFRA     LEDGER   NONE       NA    NA     N     D0>D0   RAN
    88  tan  ArachneSwarm                                         SIM       MATH     FIXED      POP   NONE   P     D1>D1   RAN
    89  tan  ArachneDamageCoverage                                INSTR     MATH     NONE       NA    NA     N     D0>D0   RAN
    90  tan  IcarusCycleDaemon                                    LLM       TEXT     LLM        POP   NONE   P     D4>D1   RAN
    91  tan  NousGenerator                                        LLM       NA       LLM        NA    NA     N     D0>D0   RAN
    92  tan  Collider (shared surface)                            INFRA     NA       NONE       NA    NA     N     D0>D0   RAN
    93  tan  KoiosMPAGates                                        MATH      MATH     NONE       NA    NA     N     D0>D0   RAN
    94  tan  KoiosRankAnalysis                                    MATH      MATH     NONE       NA    NA     N     D0>D0   RAN
    95  tan  AlienCircuitry AC-01/AC-01D/Nursery (shared surface) BENCH     FINITE   LEARNER    LIFE  NONE   P     D4>D4   RAN
    96  tan  sigma_kernel (shared surface)                        INFRA     NA       NONE       NA    NA     N     D0>D0   RAN
    97  tan  prometheus_math discovery envs (shared surface)      MATH      MATH     RL         LIFE  NONE   N     D1>D1   RAN
    98  tit  Artemis blind self-test / dispatch reconciliation    INSTR     NA       LLM        NA    NA     N     D0>D0   RAN
    99  tit  Artemis heredity certificate panel (P-11 falsificati INSTR     BYTEVM   EVO-PROG   NA    NA     Yp    D0>D0   RAN
    100 tit  Artemis research frontier + prior-art pipeline       LLM       LEDGER   LLM        NA    NA     U     D0>D0   RAN
    101 tit  Charon LLM council harness                           LLM       NA       LLM        NA    NA     N     D0>D0   RAN
    102 tit  Charon Langlands landscape pipeline                  MATH      MATH     NONE       NA    NA     N     D0>D0   RAN
    103 tit  Charon frontier/BSD/abc LMFDB hypothesis scripts     MATH      MATH     NONE       NA    NA     N     D0>D0   RAN
    104 tit  Charon kill-authority ruling apparatus (Metabolizati INSTR     TEXT     NA         NA    NA     P     D0>D0   RAN
    105 tit  Charon spectral-tail research battery + RMT null     MATH      MATH     NONE       NA    NA     N     D0>D0   RAN
    106 tit  Charon swarm (CharonAgent daemons)                   LLM       LEDGER   LLM        NA    NA     N     D0>D0   RAN
    107 tit  Erebos composer + Stygian battery executor           MATH      MATH     HYP        NA    NA     P     D0>D0   RAN
    108 tit  Generator census + step-2 regret harness             INSTR     LEDGER   NA         NA    NA     Yp    D0>D0   RAN
    109 tit  Substrate-Tester + substrate cartography suite       INSTR     LEDGER   NA         NA    NA     P     D0>D0   RAN
    110 tit  Cognitive Ceiling v0                                 BENCH     FINITE   LLM        LIFE  LATENT P     D5>U    RAN
    111 tit  CrossDomainCartographer v10 falsification battery    INSTR     MATH     NA         NA    NA     N     D0>D0   RAN
    112 tit  Clymene hoarder                                      INFRA     NA       NA         NA    NA     N     D0>D0   RAN
    113 tit  Clymene vault audit (CLY-01)                         INSTR     LEDGER   NA         NA    NA     Yp    D0>D0   RAN
    114 tit  Coeus causal intelligence layer                      LLM       LEDGER   LLM        NA    NA     N     D0>D0   RAN
    115 tit  Coeus residue trace (2026-09)                        INSTR     LEDGER   NA         NA    NA     P     D0>D0   RAN
    116 tit  Elenchus literature forensics (MVG)                  LLM       LEDGER   NA         NA    NA     P     D0>D0   RAN
    117 tit  Elenchus shadow review loop                          LLM       LEDGER   LLM        NA    NA     N     D0>D0   RAN
    118 tit  Eos horizon scanner (Dawn Scanner)                   LLM       NA       NA         NA    NA     N     D0>D0   RAN
    119 tit  Eos typed intake gate                                INSTR     LEDGER   NA         NA    NA     P     D0>D0   RAN
    120 tit  Campaign 1 hostile adjudication harness (HA-1.0.1)   INSTR     NA       FIXED      NA    NA     P     D0>D0   BUILT
    121 tit  Campaign 6 observatory qualification (OQ-1.0.0)      INSTR     NA       NA         NA    NA     N     D0>D0   BUILT
    122 tit  Charon falsification battery F1-F38 (as consumed by  INSTR     MATH     NA         NA    NA     P     D0>D0   RAN
    123 tit  Fleet evidence-system and ruler-quality audit (09-30 INSTR     LEDGER   NA         NA    NA     P     D0>D0   RAN
    124 tit  H0-H5 qualification library (QR/AF/EX/FP/PR/AP)      INSTR     LEDGER   NA         NA    NA     P     D0>D0   BUILT
    125 tit  Harmonia TT-Cross coupling engine and landscape tens MATH      MATH     NONE       NA    NA     N     D0>D0   RAN
    126 tit  Mechanism-archaeology rulers (ASAL, particles, RS, a INSTR     LEDGER   NA         NA    NA     P     D0>D0   RAN
    127 tit  NULL_BSWCD null family                               INSTR     LEDGER   NA         NA    NA     N     D0>D0   RAN
    128 tit  Program instrument audits (monoculture, detector ban INSTR     LEDGER   NA         NA    NA     P     D0>D0   RAN
    129 tit  SFE conformance contract and four-state gate         INSTR     NA       NA         NA    NA     Yp    D0>D0   RAN
    130 tit  Charon Hecate gradient archaeology                   INSTR     LEDGER   NA         NA    NA     N     D0>D0   RAN
    131 tit  Hecate Wave-2 audit harness                          INSTR     NA       NA         NA    NA     Yp    D0>D0   RAN
    132 tit  Hecate alien-lawful structure assay                  BENCH     FINITE   LLM        NONE  LATENT P     D5>D1   RAN
    133 tit  Hecate gravity (prior-recognition) detector          INSTR     NA       LLM        NA    NA     N     D0>D0   RAN
    134 tit  Hecate meta-experiment v1                            LLM       NA       LLM        NA    NA     N     D0>D0   RAN
    135 tit  Hecate novelty autopsy                               INSTR     LEDGER   NA         NA    NA     P     D0>D0   RAN
    136 tit  Hecate triplicate funnel (Pass 0-4 + probe worlds)   LLM       FINITE   LLM        NA    NA     P     D0>D0   RAN
    137 tit  Hypatia D-track daemon                               LLM       MATH     LLM        NA    NA     N     D0>D0   RAN
    138 tit  Hypatia season-1 ladder verifier                     INSTR     LEDGER   NA         NA    NA     P     D0>D0   RAN
    139 tit  Kairos April adversarial review (LMFDB)              INSTR     MATH     NA         NA    NA     N     D0>D0   RAN
    140 tit  Kairos claim lint                                    INSTR     LEDGER   NA         NA    NA     P     D0>D0   BUILT
    141 tit  NEM-14 instrument floor census                       INSTR     NA       NA         NA    NA     U     D0>D0   RAN
    142 tit  Nemesis 1.0 adversarial co-evolution engine          SIM       TEXT     FIXED      NONE  NONE   N     D1>D1   RAN
    143 tit  cheatlib acceptance-attack kit (Nemesis 2.0)         INSTR     NA       NA         NA    NA     Yp    D0>D0   RAN
    144 tit  Nyx ASAL probe battery                               INSTR     CA       NA         NA    NA     P     D0>D0   BUILT
    145 tit  Nyx Atlas of Computational Behavior                  INFRA     LEDGER   NA         NA    NA     N     D0>D0   RAN
    146 tit  Nyx Avida ancestry apparatus                         INSTR     BYTEVM   NA         NA    NA     P     D0>D0   RAN
    147 tit  Nyx Chop Shop                                        INSTR     LEDGER   NA         NA    NA     P     D0>D0   RAN
    148 tit  Nyx catalogue of algorithmic bits                    INFRA     NA       NA         NA    NA     P     D0>D0   RAN
    149 tit  Nyx evolved-network reading (Ares W4)                INSTR     EPISODIC EVO-NET    NA    LATENT P     D3>D3   RAN
    150 tit  Nyx prediction-packet pipeline and mechanism ledger  INSTR     LEDGER   NA         NA    NA     P     D0>D0   RAN
    151 tit  Pheme May demand daemon                              INFRA     NA       NA         NA    NA     N     D0>D0   RAN
    152 tit  Pheme attention contract (design only)               DESIGN    LEDGER   NA         NA    NA     U     D0>D0   DESIGN
    153 tit  Skopos relevance filter                              LLM       LEDGER   LLM        NA    NA     N     D0>D0   RAN
    154 tit  ASAL/Lenia observer instruments                      INSTR     CA       NA         NA    NA     N     D0>D0   RAN
    155 tit  Gen-0 donor adapters                                 INFRA     NA       NA         NA    NA     P     D0>D0   RAN
    156 tit  H3 retention adapter                                 INFRA     LEDGER   NA         NA    NA     P     D0>D0   RAN
    157 tit  Lehmer discovery pipeline + KillVector + navigator   MATH      MATH     RL         LIFE  NONE   P     D1>D1   RAN
    158 tit  Theseus substrate-generation daemon                  MATH      MATH     HYP        NA    NA     N     D0>D0   RAN
    159 tit  cartography literature archive                       LLM       LEDGER   NA         NA    NA     N     D0>D0   RAN
    160 tit  cross-domain RL envs + modal-collapse synthetic null MATH      MATH     RL         LIFE  NONE   P     D1>D1   RAN
    161 tit  fossil vault + FOSSIL_PACKET pipeline                INFRA     LEDGER   NA         NA    NA     Yp    D0>D0   RAN
    162 tit  ladder_circuits                                      INSTR     FINITE   FIXED      NA    NA     P     D6>U    RAN
    163 tit  sigma_kernel                                         INFRA     NA       NA         NA    NA     N     D0>D0   RAN
    164 tit  techne self-audit loop + epistemic controls          INSTR     NA       NA         NA    NA     P     D0>D0   RAN
    165 tit  techne/lib + prometheus_math arsenal                 INFRA     MATH     NA         NA    NA     P     D0>D0   RAN
    166 tit  Noesis falsification tests                           LLM       MATH     NA         NA    NA     N     D0>D0   RAN
    167 tit  Cartography falsification battery                    INSTR     MATH     NA         NA    NA     N     D0>D0   RAN
    168 tit  Mutation harness                                     INSTR     NA       NA         NA    NA     P     D0>D0   RAN
    169 tit  Evidence Wiki (PEW)                                  INFRA     NA       NA         NA    NA     P     D0>D0   RAN
    170 tit  Necropolis workshop tool morgue                      INSTR     LEDGER   NA         NA    NA     Yp    D0>D0   RAN
    171 tit  Attack registry + admissibility preflight            INSTR     NA       NA         NA    NA     Yp    D0>D0   RAN
