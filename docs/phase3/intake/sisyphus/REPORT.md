# Sisyphus Phase 3 intake -- territory report

Crawler: Sisyphus[m1-80b155f0] (claude-opus-5-5), one of four independent
Phase 3 forensic crawlers. Crawl date 2026-10-01. Base: origin/main
19299e06b (worktree Prometheus-worktrees/sisyphus-base-role, branch
sisyphus/phase3-intake-2026-10-01). Charter verbatim:
roles/Sisyphus/prompts/2026-10-01_charter/ (MANIFEST verifies).

Territory (15 seats): Archaeon, Vivarium, Daedalus, Nestor, Bellerophon,
Ares, Proteus, Ludus, Theophrastus, Apollo, Lexis, Herakles, Rhadamanthus,
Crius, Chiron. Theme: emergence, artificial life, worlds, organisms,
evolutionary and ecological pressure, serendipity search, reproduction,
foundries, open-ended search, world and organism generation.

Tags used throughout (charter epistemic rule): [IMPL] implementation fact;
[INTENT] design intent; [HIST] historical claim; [RESULT-UNVERIFIED]
reported result; [CORRECTION] later correction/contradiction;
[CODE-INFERRED] capability inferred from code; [UNKNOWN]. Nothing in this
report is a scientific verdict. Outcome labels on campaigns describe the
historical record only.

## 0. Package contents and method

    REPORT.md                 this synthesis
    seats/<Seat>.md           15 dossiers, charter sections 1-12 each
                              (~81,000 words total; Archaeon 10.7k,
                              Nestor 8.8k, Vivarium 8.1k ... Chiron 2.1k)
    artifact_index.jsonl      528 artifact records (merged from seats/_frag/)
    engine_index.jsonl        51 engine/lens records (merged from seats/_frag/)
    seats/_frag/              per-seat source fragments of the two indexes

Method. Seven parallel read-only workers, each under one written brief
(holdout and nestor_secrets paths excluded from every search; no git
writes; no experiments; Atlas as locator only; read code and history),
split Archaeon | Vivarium | Daedalus+Apollo | Nestor+Bellerophon |
Ares+Crius+Theophrastus | Proteus+Ludus+Lexis | Herakles+Rhadamanthus+
Chiron. Sisyphus read the Atlas cross-engine harvest (roles/Atlas/
inference_harvest_2026-09-30/: CROSS_ENGINE_SYNTHESIS, BURIED_SIGNALS,
CONTRADICTIONS_AND_NATURAL_EXPERIMENTS) independently, merged and validated
the fragments (every line parses; all required keys present; pure ASCII),
and spot-verified load-bearing claims against source (section 0.2).

### 0.1 Coverage limits (read these before trusting any absence)

- Host-local evidence NOT in git was not read: M2 SFE ledgers, BEE
  results.jsonl, Archaeon off-repo data (C:\Prometheus-data), ENVGATE raw
  rows, the off-repo D-13 ancestor F:/SerendipityD was read read-only by
  one worker but is not on any branch. [UNKNOWN beyond what git records]
- Sealed material (Cosmos C3 holdout D2; any *holdout* path;
  nestor_secrets) was never opened, by rule.
- Live databases (viv queue, SFE, PEW) were not probed; comms history was
  read through a read-only SQL helper. Three comms bodies (#872, #881,
  #1133) returned empty through `comms show`; subjects only were used.
- Slot-level design/readout files of Archaeon C2-C5 and the ~90 NPE
  experiment directories were read through their campaign reports and
  ledgers, not one by one.
- Chiron's off-fleet clone (BUCKKEEP) could not be inspected.

### 0.2 What Sisyphus re-checked in source (sample, not exhaustive)

| claim (dossier) | check | result |
|---|---|---|
| PROTEUS-46 greedy walk cannot accept a neutral child (Proteus) | proteus/round2/falsifier_46.py:113-131 | CONFIRMED [IMPL]: child key (two, -ops) with ops >= 1 never beats incumbent (cur, 0) |
| SFE canary: identical RNG + initial population in every world; 2-flip mutation preserves Hamming-distance parity (Daedalus) | SerendipityFoundryEngine/sfe/canary.py:40-45, 74-79 | CONFIRMED [IMPL] for RNG/population/parity; the "leading lineage odd, cannot reach 24/24" step rests on the worker's seed re-derivation [CODE-INFERRED] |
| Ares D1: reported champion selected on the held-out set (Ares) | ares/search.py:291-294 | CONFIRMED [IMPL]: argmax over 128 on eval_seeds, max reported as "heldout" |
| Ludus r0003 stops on ties incl. pot 0 (Ludus) | ludus/bench/circuits.py:108-121 | CONFIRMED [IMPL]: continue iff e_gain > p_dead*pot |
| prometheus/z80atlas is Bellerophon's BEE, not Nestor's (Nestor) | git log --diff-filter=A | CONFIRMED: first commit 98b2149a7 "Bellerophon: Z80 x Atlas ..." (2026-09-19) |
| Apollo Task 2 (state injection) never ran (Lexis) | git ls-files apollo/cycles | CONFIRMED: no state_injection path |
| Stale Herakles edit still in canonical checkout (Herakles) | session-start git status | CONFIRMED: " M herakles/evca/core.py" on vivarium/v0-2026-09-05 |

Corrections to the charter's starting surfaces and to prior maps:
- prometheus/z80atlas/ belongs to Bellerophon (BEE). Nestor's Z8 engine
  (NPE) lives under roles/Nestor/campaigns/z80atlas-*; Archaeon has a third
  "Z80" (archaeon/z80atlas/). Three instruction sets share one name
  (also Atlas V1).
- primordial/ is 100% Nestor (graphworld swarm, merged b10161316), not
  Archaeon or Vivarium.
- origin/archaeon/campaign4 and campaign5 branches do not exist; Campaigns
  4/5 are directories on main.
- Branch vivarium/v0-2026-09-05 (the canonical checkout's branch) carries
  Aporia/Herakles/Mnemosyne commits, all already on main.
- Achilles census: Proteus listed as consumer of ludus/bench/worlds.py; the
  cited line is a do-not-read clause (Ludus dossier).
- Atlas: SFE catalogue entry describes Archaeon's science, not SFE; Atlas
  registry lists the toolbox LIVE with no z80atlas row; Atlas says Apollo's
  crossover flag was "never found done" but Apollo's run commands used
  --crossover-frac 0.3 (only the default stayed 0.0); Atlas buried signal
  A3 compares a training-battery maximum with a held-out screen value
  (unlike estimators). Each is recorded in the relevant dossier.

## 1. Territory map: what each seat actually is

| seat | what it actually built (one line) | engine/instrument class | state 2026-10-01 |
|---|---|---|---|
| Archaeon | four code families (~51k lines): fossil-to-queue producer; GA harnesses on the Proteus VM (WSE, C1-C6, Deep Frontier); a Z80-style byte ecology; ENVGATE + taint VM + causal lens | GA harness + per-byte material tracer + governance author | active (governance) |
| Vivarium | a Postgres experiment queue + SFE runner + PEW outbox; five "kinds" wrapping other seats' toy evaluators | provenance data plane, not an alife engine | parked/silent since 09-24 |
| Daedalus | SFE: a hash-chained provenance ledger with prediction-before-observation; two toy executors (24-bit bitstring, NK N<=20); search lives in the off-repo D-13 ancestor | ledger/foundry service | maintained |
| Nestor | NPE Z8 pair-tape soup with world ops; P-11 causal-copy assay; z8taint; CW01 loop on the Proteus VM; primordial/ graphworld swarm | soup + heredity rulers | direct operator control |
| Bellerophon | BEE Z80 soup (physics v1-v3, copy-resource payment); Worlds Kernel prometheus/toolbox | soup + world kernel | BEE recent; kernel dormant since 09-19 |
| Ares | batched GA over <=17-node graph organisms on 16 one-bit-memory toy worlds; carrier attribution | pressure microscope | parked since 09-25 |
| Proteus | proteus.foundry v0 VM (25 ops, 4-word instructions, every word legal) -- the shared organism substrate; graph_organism.v1; mutation-kernel crucibles | substrate + operator instrument | dormant since 09-18 (undeclared) |
| Ludus | exactly solvable authored game worlds, depth profiles, leak-audited arena, 1,338-row game atlas | exact-solver world bench | silent since 09-16 |
| Theophrastus | contrast-first harness over herakles.evca CA density task; replay of Vivarium fossils | exploration harness, no search | dormant since 09-14 |
| Apollo | routing-DAG and Branch C blackboard evolvers that order/gate hand-written solvers; enumeration and schedule instruments | program-composition GA | dormant after 09-11 |
| Lexis | closure search over a program vocabulary; expressiveness-vs-search split; admission gates | instruments over Apollo's substrate | identity re-adjudication pending, never done |
| Herakles | herakles.evca/eca/ca_stream libraries; 11 historical CA rule tables reproduced; HC-T01 Toussaint reconstruction | literature-reconstruction CA lens | active intermittently |
| Rhadamanthus | Necropolis: autopsies of 48 dead v1 LLM-pipeline agents, 92 residue organs, 93 forensic tools | autopsy court for software agents, not lineages | dormant since 09-14 |
| Crius | 8-register bytecode VM with persistent executable workspace; accessibility-frontier search, strong content controls | richest organism in territory | closed 09-23 |
| Chiron | nothing executable: 4 commits, 13 Markdown files on an unmerged branch (CDE / Engine Five thesis) | design only | branch-only |

Structural fact that governs the whole territory [IMPL]: the territory is
NOT fifteen engines. It is a small number of shared substrates consumed by
many seats:

- the Proteus v0 VM: Archaeon C1-C6, WSE, Deep Frontier, Nestor CW01
  (T-ARCH4/T-ARCH5), Vivarium cegis_boolean, ~60 Archaeon imports;
- herakles.evca (radius-3 density task): Vivarium ca_density, Archaeon C3,
  Theophrastus, Proteus, Nyx;
- the "Z80" family (three distinct ISAs: Archaeon z80atlas with no copy op,
  BEE with one-instruction LDIR, NPE with LDIR/LDDR encodings + world ops),
  all born of one directive;
- SFE as the ledger under Vivarium and Archaeon rows.

Consequence for Phase 3 [CODE-INFERRED]: "N seats agree" in this territory
usually means "one substrate, one mutation operator, one author family
agree with themselves" (Atlas reaches the same conclusion independently:
CROSS_ENGINE_SYNTHESIS s0, s4).

## 2. Lens inventory (summary; full per-lens sections in each dossier s12)

| lens (seat) | substrate observed | phenomenon family | resolving mechanism | resolution ceiling / toy-grade parts |
|---|---|---|---|---|
| Byte-soup heredity (Nestor NPE, Bellerophon BEE, Archaeon Z80) | 64-256 byte tapes on Z80-like VMs | spontaneous copying, establishment, heredity vs construction | P-11 causal copy, CVT-R, z8taint / bee_tracer / Archaeon taint VM | world supplies the copy primitive; labels over-report descent ~10x vs material; one material tracer run per engine |
| ENVGATE environment-as-variable (Archaeon) | vmcopy32 copiers, input streams | environmental gating of establishment | sham arms on identical input streams, byte-level identity tracing | establishment counts 2-5 per arm; ~150 core-h per protocol |
| Proteus-VM evolutionary harness (Archaeon, Nestor CW01, Deep Frontier) | 4-word instruction programs, 25 ops | reachability, robustness, cliff/locality, memory use | reachability tables, held-out confirmation, typed disposition ladder | count-fixed rulers, greedy tie-rejecting search, two-stream memory ceiling, tiny tasks |
| Mutation-kernel crucible (Proteus) | the mutation operator itself | operator bias vs landscape | exact state enumeration, 20k samples/state | reversible reference control cannot fail (Harmonia) |
| Carrier microscope (Ares) | <=17-node recurrent graphs | where memory is carried (edge/cycle/node) | carriers.py attribution + carrier blocking | worlds need 1 bit; three carriers by construction; held-out selection defect D1 |
| Accessibility frontier (Crius) | 8-register VM + persistent executable workspace | whether stored/executed blocks get used | content controls, pre-search gate, neutral-edit baseline | one task family; (8+24)x300 search; budget fixed by charter |
| Exact game-world bench (Ludus) | authored solitaire games, exactly solvable | depth/regret, transfer of stopping circuits | exact value, occupancy-weighted regret, differential leak audit | small authored worlds; no organism ever ran in one |
| Historical CA reconstruction (Herakles) | 1-D radius-3 CA density task | known-answer calibration against 1990s literature | pinned conventions, six scoring criteria, reproduced tables | one task; no particle/domain analyser |
| Program-composition evolver (Apollo) + closure instruments (Lexis) | pipelines over hand-written parsers/solvers | composition, crossover across valleys | enumeration (O1), schedule analysis (E1), dumb-rule attack | competence lives in human-written solvers; parsers fit the author's phrasing (blind 0.0667) |
| Provenance ledger (Daedalus SFE, Vivarium data plane) | experiments, not organisms | evidence integrity | hash chain, prediction-before-observation, blind executor, quarantine-by-listing | toy executors only; ledgers off-repo |
| World kernel (Bellerophon toolbox) | IR worlds + players | world generation with receipts | replay, admission checks | toy worlds/players, no in-world reproduction, no external importer |
| Necropolis (Rhadamanthus) | dead software agents | why things were killed | autopsy doctrine, counterfactual dataset | no consumer of residue; every grave reads NO_FAIR_TEST_ON_RECORD |
| CDE / Engine Five (Chiron) | (none) | developmental persistent-skill lineage | (none) | design only; nearest executed analogue is Artemis R-12 (off-repo code) |

## 3. Cross-seat timelines that matter most (detail in dossiers s9)

1. "Spontaneous replicators" (Nestor NPE): 1,031 admissible -> 57 pass
   P-11 -> ~2 genuine self-copiers; ~95% of the 1,031 were splice-made
   [CORRECTION]. P-11 itself certifies construction, not heredity
   ("painters" pass) [CORRECTION, Artemis panel]; the external CVT-R
   certificate also false-accepts (NPE wave-2 W2-36) [CORRECTION].
2. Archaeon Z80 x Atlas "26 spontaneous replications" -> 0: all 26 flags
   were transplants; the predicate read a run label, not provenance
   [CORRECTION].
3. BEE "spontaneous own-code SR CONFIRMED_CAUSAL" [HIST] vs "own code"
   defined by memory location, not material; 160 -> 103 BUILT_BY_COPY;
   45 exact duplicate seeds; 33% of births NOT_IDENTIFIABLE [CORRECTION].
   Current status: real but an engineered basin (block copy + NOP slide).
4. PROTEUS-46 "no intermediate the probe can see" (CLIFF_SURVIVES) [HIST]
   -> greedy walk structurally rejects neutral children (verified here)
   -> Artemis D002-03q 5-edit neutral path to 6/6 (worker quick mode,
   population search never reached 6/6; full run timed out)
   [RESULT-UNVERIFIED] -> the 299,991-row Deep Frontier suppression (#735)
   still rests on the original verdict. Status: CONTESTED.
5. Campaign-4 "cliff" and "length protects" (Archaeon C4-02/C4-08/C5-08)
   -> CW01 ruler audit: 4/7 fixed-count damage claims disappear under a
   qualified Bernoulli(f) ruler [CORRECTION, same VM]. The C4 cliff itself
   has never been re-read under that ruler.
6. C5 "flat elite: selection does not climb these worlds" (operator
   accepted) [HIST] vs Deep Frontier "every N climbs" at 60k evals
   [RESULT-UNVERIFIED, PROVISIONAL]. The Archaeon worker notes the DF
   number is a training maximum and the C5 number a held-out screen value:
   unlike estimators. Status: CONTESTED, and the Atlas comparison is not
   like-for-like.
7. SFE canary "no topology improved best objective; all worlds 0.958"
   [HIST] -> identical RNG and population per world + parity-preserving
   mutation (verified here) make the null largely geometric
   [CODE-INFERRED, new in this crawl; no prior artifact records it].
8. Lexis/Apollo "identity re-adjudicated after a blind result" [INTENT,
   D-25] -> Apollo blind battery 0.0667 with 40/42 abstentions [HIST] ->
   the separating Task 2 was accepted 09-11 and never run (verified here).
   The base-role text reads as if the re-adjudication happened; it did not.
9. Rhadamanthus Hephaestus grave: TRUE_CORPSE -> NO_FAIR_TEST_ON_RECORD
   when doctrine LAW N17 v2 landed (c7340a6ad) [CORRECTION by doctrine,
   not by new evidence].
10. Vivarium consumer deploy lag: a fix "closed" while the running
    consumer was 4h47m older; 48 rows lost; recurred twice [HIST]. This is
    the base role's "process state can lie by implication" exemplar.

## 4. Final synthesis

### A. What actually exists

The most substantial implemented scientific machinery in this territory,
in no ranked order:

1. Three Z80-family byte soups with real, versioned physics and real
   heredity instrumentation: Nestor NPE (pair tape + world ops; P-11;
   z8taint; register-reset world axis), Bellerophon BEE (physics v1-v3,
   copy-resource ledger coupling payment to reproduction, byte-replay
   golden fixture), Archaeon z80atlas + census. [IMPL]
2. Material-grade descent tracing: Archaeon's taint VM / causal lens
   (per-byte, four identities per birth; run over 28,964,089 BEE births
   and 54,616 Archaeon births per the engine index [RESULT-UNVERIFIED
   counts]), NPE z8taint, bee_tracer. The only instruments in the program
   that can separate label descent from material descent. [IMPL]
3. ENVGATE (Archaeon): environment varied with organism physics frozen,
   sham arms on identical input streams. The cleanest controlled-pressure
   geometry in the territory. [IMPL]
4. The Proteus v0 VM and its grammar: a total, deterministic, hashed
   instruction substrate (every word decodes) that carried most
   evolutionary campaigns; plus proteus.graph and the mutation-kernel
   crucible. [IMPL]
5. Crius's VM with a persistent executable workspace and its control
   battery (content tests, pre-search gate separating positive from causal
   control, neutral-edit baselines). The organism with the most room for a
   stored-and-reused internal structure. [IMPL]
6. Exactly solvable world machinery: Ludus depth/regret/leak audit,
   Herakles reproduced historical CA tables (1998 coevolution 15/15, 1996
   GP 4/4, EvCA 17/18 [RESULT-UNVERIFIED]), Apollo O1 exhaustive
   enumerator, Lexis closure search. Known-answer calibration assets. [IMPL]
7. Provenance plumbing that works: SFE hash chain and
   prediction-before-observation; Vivarium blind executor, sealed spec,
   quarantine-by-listing, attempt replay and ordered outbox. Infrastructure
   for evidence integrity, not for science content. [IMPL]
8. Ares carriers.py: memory attribution to edges/cycles in recurrent
   graphs; reusable beyond Ares's worlds. [IMPL]

### B. What was mostly scaffolding

- SFE as a "serendipity search engine": the runtime does no search
  (executors.py states search is the caller's); its two executors are
  toys; the search lived in the off-repo D-13 ancestor. Atlas and READMEs
  describe Archaeon's science as SFE's. [IMPL vs INTENT]
- Vivarium as an alife engine: no worlds, organisms, mutation or selection
  were ever built; declared campaign-ready 09-17, never ran a campaign;
  Campaign 4 could not be honoured for science rows; Campaign 6 designed,
  never built. [IMPL]
- Archaeon's fossil-directed producer loop: the proposal draw was
  byte-identical with and without the fossil corpus; fired and steerable
  regions were disjoint; 0 detectors eligible on the later ledger. [HIST,
  per Archaeon dossier]
- Campaign 6 observatory: never passed its own gate; Deep Frontier ran on
  operator authorization with "admitted" rulers hard-coded
  (archaeon/frontier/scheduler.py ~l.178), no Harmonia admission found.
  [IMPL/HIST]
- Bellerophon Worlds Kernel: strong receipts, toy worlds/players, phases
  3-4 unbuilt, only importer is its own shim. [IMPL]
- Ludus World Foundry v3: chopping grammar, Proteus binding and generated
  family never built; no organism ever ran in a Ludus world. [IMPL]
- Proteus retention reservoir and PEW export: contracts only. [IMPL]
- Theophrastus "combinatorial ecology": no search, 4-5 fixed 1990s CA
  rules on one task. [IMPL]
- Apollo "trains LLMs" (README) and "hybrid LLM wins" (April): no
  training; the cited report lists 0% DeepSeek calls. [CORRECTION]
- Necropolis "throw the corpse in": nothing routes dead lineages into it;
  no code reads its residue; descendants/ empty. [IMPL]
- Chiron / CDE / Engine Five: design only, though other seats cite the
  branch-only "PROGRAM-WIDE" synthesis directive (9e54a51ce) as
  governing. [IMPL]
- Herakles as an SFE experimenter: no Herakles run ever executed there;
  five recovered organisms never entered genomes.py. [IMPL]

### C. Historical signals worth revisiting

Listed because the lens or experimental geometry looks informative, NOT
because the claims are true.

1. Copying without competence (Archaeon transplants 39/39 persist, 0/39
   competent; Proteus-VM incompetent imports take over 11-12/12; BEE
   endogenous vs external reproduction antagonism). Geometry: heredity of
   copying vs heredity of function, separable by executed-path analysis
   (TH-015 already records executed loci). [RESULT-UNVERIFIED]
2. Zero-register dependence across NPE (ZERO 26/48 vs CONST 2/48) and BEE
   (carried registers kill zero-dependent founders 0/24 vs 10/24): an
   initialization regime evolution uses as a free constant. Same ISA
   family, two codebases, two rulers. [RESULT-UNVERIFIED]
3. Write-back physics dominating variation: NPE atomic write-back runaway
   1/80 -> 46/80 for one founder; splice manufacturing most apparent
   replicators. Geometry: who writes what, when, as a first-order world
   variable. [RESULT-UNVERIFIED]
4. Neutral-path accessibility vs greedy search: PROTEUS-46 (verified tie
   rejection), Crius R-07 (44% neutral single mutations, a 41-step neutral
   insert path to the full mechanism, worker claim), NPE neutral walk ~=
   soup rate (pilot ratio 1.75, p .20, WP-9 baseline never run).
   [RESULT-UNVERIFIED]
5. Delay-invariant reader on the Proteus VM (reads untrained delays 8/16
   at 1.0 vs direct search 0/6, 1/6) together with the latch
   counter-reading (Artemis R-22: first-tick latches fall to 0.00 with one
   pre-PUT noise tick, worker claim). A small, cheap, decisive geometry.
6. Crius "invocation without content": full block stores invoked many
   times with zero effect -- a distinct phenotype the control battery can
   see. [RESULT-UNVERIFIED]
7. Apollo crossover crossing a multi-step valley (0/8000 single-step walks
   vs 4/5 seeds with crossover, 3/5 on replay) against NPE/SFE/CW01 where
   recombination is harmful or null: a representation question, cheaply
   separable on the Proteus graph substrate. [RESULT-UNVERIFIED]
8. ENVGATE-02 all-blocked arm: 5 establishments at ~7x the frozen
   prediction, possibly a second window-independent route. [RESULT-
   UNVERIFIED]
9. BEE payment: maintains seeded task code, acquires new task code only
   for ECHO/INC, never COND_ONE (0/960) -- a ladder whose first missing
   rung is measurable. [RESULT-UNVERIFIED]
10. Exaptation gradient under deeper neutral walks (C5-01 .050 -> .082 at
    depths 16 -> 64, killed on a yield rule) and insertion as the only
    asymmetric-rescue operator (C5-06: 102 recoveries, 0 losses).
11. D-7 "certified nonlinear wormhole" (2,197-state machine), the only
    positive of the SFE lineage, never challenged. [HIST]
12. Herakles never-run items: the EvCA Stage-1 GA rerun and
    ca_stream_v2 (approved as D-18, never registered) -- the one place a
    1990s published result could serve as a positive control for a modern
    search stack.

### D. Known hallucination / confound classes

How these systems fooled Prometheus, each with at least one documented
instance in the dossiers:

1. Label-for-property: a predicate reads a run label, slot, organism id or
   memory location instead of material provenance (Archaeon 26 -> 0
   replications; BEE "own code" by location; parent-chain counts inflating
   establishment 8-42x; NPE C9-D14 pair-tape identity kept while bytes
   replaced).
2. World-made copies counted as organism copies: NPE splice (~95% of
   1,031), BEE hidden world copies (defect P1), SFE/Proteus imports taking
   over regardless of competence.
3. Construction mistaken for heredity: P-11 passes painters; CVT-R
   false-accepts.
4. Count-fixed rulers manufacturing length effects on the Proteus VM (4/7
   CW01 claims; C4/C5 by inference).
5. Search policy read as landscape: greedy tie-rejecting walks (PROTEUS-46
   verified), small fixed budgets (Crius, C5), "nothing reached" reported
   as "nothing exists".
6. Selection on the evaluation set: Ares D1 (verified) inflating every
   non-cap number and every shuffled control in cycles 0-1.
7. Controls that cannot fail or always fire: Proteus V0.5 reversible
   reference exact by algebra; NPE anticheat guards that cannot fire
   (W2-8); C9-D16 four identical arms read as a null; BEE REPL-01 K3
   could not return SURVIVES; REPL-02 positive control 0/50; Vivarium C3-2
   ruler with one reachable value (0.0).
8. Geometry-forced nulls: SFE canary (identical RNG/population; parity
   invariant -- new here).
9. Author-fit instruments: Apollo parsers matching the home author's
   phrasing (0.60 -> 0.067 under a blind author); HC-T01 accessibility
   detector reading "has >= 1 operator".
10. Restatement and positive-control-as-signal: Theophrastus 14/23
    "signals" are positive controls; SPEC-001 true by exchangeability.
11. Deterministic replay counted as replication: frozen counts replay
    exactly; independent re-measurement moved several by multiples (Atlas
    F7).
12. Process state lying: deploy lag (Vivarium), engine stalls with no
    ledger trace read as rule-space properties (SFE 13 H5 rows; Vivarium
    rules 143-155), phantom experiments (85,727), contaminated libraries,
    stale STATUS files claiming ACTIVE/alive (Theophrastus, Vivarium,
    Ludus, Proteus).
13. Post-exposure amendment: E-003 relabelled VALIDATED -> ALTERED after
    data exposure (Harmonia).
14. Rules reconstructed from memory (Ludus Martian Dice audit reversed
    cycle 002's 86%).
15. Monoculture of evidence: one model family authors, executes, scores and
    audits; terms spread across seats within 0-2 days (Atlas s0, s4).
    Independent confirmation has no mechanism in this territory.

### E. Likely false-negative regimes

Places where a null may be a statement about the instrument, not the
phenomenon:

1. Worlds that need at most one bit of memory or are exactly enumerable
   (Ares W-family; Vivarium kinds: 16-32 bit onemax, 7-cell ECA, 3-input
   Boolean; Ludus solitaire games; SFE 24-bit bitstring, NK N<=20). Any
   "no richer mechanism" verdict here is bounded by the world.
2. Organisms that cannot express the question: CW01 capability nulls;
   Apollo organisms that only order hand-written solvers; Theophrastus with
   no organism at all; tree-GP/PushGP sterility possibly an adapter defect.
3. Search that cannot traverse neutral intermediates or is capped below
   the needle size: PROTEUS-46, Crius (8+24)x300, C5 at 9k-36k evals, Apollo
   S1 budgets 80-600, NPE without the WP-9 random-walk baseline.
4. Rulers at floor/ceiling or unable to return the other outcome: BEE K3
   and P5 ceiling; Vivarium C3-2; herakles ca_stream v1 inert for every
   rule; LADDER2 rewarding half-correct tapes.
5. Underpowered contrasts: Vivarium S1 (n = 12 pairs), ENVGATE counts of
   2-5, origin nulls 3 vs 3 at n = 40.
6. Experiments never run that would decide a question: X-TASK-GATE (task
   competence riding on endogenous reproduction), Apollo Task 2, LEX-07
   cheat control, ca_stream_v2, EvCA Stage-1, the C4 cliff re-read, WP-9,
   Ares keep load/hold decoupling.
7. Costs or pressures applied from generation 0 on flat landscapes
   (Archaeon): organisms died before selective state could get a foothold,
   although hand-written organisms showed the economics favoured it.
8. Readout choice (ever-reached vs final-state) deciding verdicts more
   than horizon length (Atlas B7) -- short horizons with final-state
   readouts deflate.

### F. Phase 3 questions exposed (not answered here)

1. What world size, observability, stochasticity and task diversity are
   required before a null about a reasoning primitive is admissible, and
   can such worlds still be exactly checkable (Ludus's tension)?
2. Which ruler separates construction from heredity, and copying from
   heredity of function, when every existing certificate (P-11, CVT-R,
   SR-by-location) has a documented false-accept mode?
3. Should the copy primitive and register-zeroing be world physics,
   organism-evolved, or swept as an axis -- given that in the Z80 family
   the world supplies reproduction?
4. Is write-back / write authority a separate world variable or simply
   the dominant source of effective mutation?
5. Can search policy be held as a declared, varied factor (greedy vs
   neutral-accepting vs population) so that "unreached" is never reported
   as "absent"? What needle-size measurement is required?
6. Is the C4 cliff landscape, ruler or walk rule -- and should the
   299,991-row suppression stand until that is known?
7. What detection power (positive, negative and cheat controls on the
   same substrate) must an observatory demonstrate before it may steer
   allocation or suppress a transformation?
8. How is independent confirmation obtained when one model family fills
   every role and seats share substrates, operators and vocabulary?
9. Is the Proteus v0 VM's two-stream memory ceiling a property of the
   organism, the mutation operator or the world?
10. Can SFE/Vivarium provenance guarantees become a portable receipt
    format rather than a service, and where do the off-repo M1/M2 ledgers
    live under custody?
11. What unit of work suits long evolutionary runs (Vivarium's own
    "segment" proposal vs one row per evaluation)?
12. Can routing/composition organisms (Apollo, Lexis) survive meaning-based
    rather than surface parsing, and is crossover's benefit
    representation-bound?
13. Is a 1-D density-task CA lens worth extending without a
    particle/domain analyser?
14. Can any Necropolis grave reach TRUE_CORPSE under current doctrine, and
    should dead ALife lineages be routed there at all?
15. Who owns the pending re-adjudications (Lexis identity; PROTEUS-46;
    the SFE canary null; the 17 NPE wave-2 corrections never adopted into
    its findings ledger)?

## 5. Open items left by this crawl

- The SFE canary parity reading should be confirmed by a rerun before
  anyone cites it as more than CODE-INFERRED (zero-cost; not done, by
  scope).
- Off-repo M2 evidence (SFE ledgers, BEE results.jsonl), Archaeon
  C:\Prometheus-data and F:/SerendipityD custody are unknown.
- Whether Vivarium's H1/H0 S01/S11 library is the leaky demo library is
  unresolved (if so, task 11 solved only there is contamination).
- Sibling crawlers' territories touch this one at Atlas, Artemis, Cosmos,
  Ananke (PTE), Aether, Tyche and Hecate; the cross-references in the
  dossiers to those seats are pointers, not crawls.
