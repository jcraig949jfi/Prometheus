# Seat dossier: Aether

Crawler: Tantalus (worker)
Tree SHA: 21a47402a (origin/main, worktree F:/Prometheus-worktrees/tantalus-phase3-intake)
Date: 2026-10-01

Summary. Aether is a seat created 2026-09-19 on M2 with charter pending, which by 2026-09-20 had designed
a "fourth Prometheus ecosystem": an exact-integer, synchronous, hash-keyed 2-D torus cellular system whose
sites hold five uint8 fields (opcode, arg0, arg1, payload, energy). In the baseline law aeth01.v1 the only
active opcode is WRITE (1 of 256 values): an energised WRITE site proposes one byte write into one field of
one von Neumann neighbour, contests are decided by a per-tick hash, the winner replaces the target byte,
and a bit-flip "perturbation" is injected with probability 0.1. Energy is debited, decays and is randomly
replenished. There is no program counter, no individual, no selection and no objective. The seat moved to
host BUCKKEEP (an i7 laptop) and spent most of its time on infrastructure: a frozen conformance specimen
(AETH-00), CPU oracle vs GPU-shaped implementations proven bit-identical, a CuPy kernel run at 16384^2
(268 M sites) on a RunPod A40, an AGE pod-lifecycle controller and reaper, and a reusable RunPod GPU platform
(prometheus_gpu/). Its science (all at 128^2-2048^2, one energy regime) is a sequence of honestly scoped
nulls: the lattice settles to ~92% frozen by ~2,500 ticks, "circuit" structure is energy-supply residue,
and a one-bit difference stays within ~1 site for 10,000 ticks under v1 and ten one-change variants. The
only propagating single change (rcv, "a written site fires once") was reinterpreted as a calibration law
that transports activation timing along its own relay; two pairwise combinations (rcv_add, rcv_str) are
replicated super-additive propagation effects at 15-22 of 128 origins, explicitly "not content transport".
The "transition from infrastructure toward a scientific substrate" is real in the record (operator
directives 09-24 "the experiment is the platform" -> 09-26 three lanes -> 09-27 research block -> 09-30
interventional lesions E-010..E-012), but the substrate's measured dynamics remain near-static.

## 1. Identity, charter and pivots

- Created 2026-09-19 on M2 (Aether[m2-57e24282]) with "You're a new seat... we'll discuss your charter"
  (roles/Aether/RESPONSIBILITIES.md s0; commit 298c2a511) [IMPL].
- 2026-09-20: "fourth-ecosystem design capture pass 1 -- doctrine, working concept, open questions,
  decisions (docs only, no code)" (6a5ba2b56): Aether/AETHER_DOCTRINE.md, AETHER_CONCEPT.md,
  AETHER_OPEN_QUESTIONS.md, AETHER_DECISIONS.md; source notes Aether/notes/2026-09-20_raw_notes.md [IMPL].
  Concept: "a GPU-native artificial physics in which executable matter must discover persistent
  organization, configuration transmission, recursive construction and useful computation without being
  given predefined assemblies" and "Clean-room design... no copying... of [BEE, NPE, SFE]" [INTENT].
- The seat file was never rewritten into a charter; RESPONSIBILITIES.md carries a stale pre-charter body
  under two "CURRENT DIRECTIVE" banners; the governing texts are operator directives under
  roles/Aether/prompts/ and Aether/AETHER_DOCTRINE.md (STATUS.md 2026-09-22 block) [IMPL].
- Host: moved from M2 to BUCKKEEP (Aether[buckkeep-7a10ca4b], later Aether[buckkeep-5c60d0f5]); the
  RunPod key is held only on BUCKKEEP (AETHER_ENGINE_CARD.md s10-11) [CLAIM]. Atlas registry has no
  Aether engine row; the engine card notes "a registry lists Aether's host as M2, which is wrong" [IMPL /
  CLAIM].
- Pivots [IMPL from commit log and directives]:
  1. 2026-09-20: AETH-00 frozen (semantics_id aeth00.v1, 4 fields, no energy) as a REPLACEABLE
     conformance specimen; AETH-00A independent oracle + golden vectors + mutants; AETH-00B production CPU
     implementation (Aether/production/aeth00.py).
  2. 2026-09-20..22: AETH-01 primordial physics design, two-pass "Astra" architecture review, repairs,
     aeth01.v1 "repaired freeze CANDIDATE, not frozen"; RunPod canary, AGE controller, cleanup reaper;
     terminology refactor that removed biology words (abe63ef42; COMPUTATIONAL_TERMINOLOGY.md with a
     linter); GPU memory optimisation 240 -> 113 bytes/site; First Light (6 worlds 4096^2 x 5,000 ticks).
  3. 2026-09-23..24: AETH-02 Native Circuitry round (directive 2026-09-23): causal-graph observatory,
     3 x 2048^2 to 50,000 ticks, falsifiers H1-H4; CLOSED 2026-09-24.
  4. 2026-09-24: operator RUNPOD ENGINEERING LADDER becomes primary mission ("do not optimize this
     campaign around obtaining an interesting scientific result"; "the experiment is the platform",
     2026-09-26 next-round directive).
  5. 2026-09-26: "resume productive science in parallel": three lanes (ladder, close AETH-02 H2/H3,
     AETH-03 physics design).
  6. 2026-09-27: multi-hour research block (C-002, Blocks A-J): assay audit, rcv reinterpretation,
     horizon, combinations, known-answer lane, engine card.
  7. 2026-09-28..30: MWO-0001..0004, Fabric execution, CWO 2026-09-30: E-008..E-012; promexec reviews
     for Odysseus.
- Current state (WORK_STATE.json, updated 2026-09-30T10:21:30Z): WORKING; E-011 closed PARTIAL; E-012
  preregistered (7b7dea59e) with no RESULT on main [IMPL].
- Case note: `aether/` and `Aether/` resolve to the same directory on this Windows checkout; git tracks
  only `Aether/` (764 files; `git ls-files aether` = 0) [IMPL].

## 2. Engine/system inventory

E1. aeth01.v1 lattice physics ("AGE" in other seats' prose).
- Spec: Aether/AETH-01/AETH01_REPAIRED_FREEZE_CANDIDATE.md; PHYSICS_SPEC_DRAFT.md; ECONOMICS.md [CLAIM].
- Implementations [IMPL]: per-site Python CPU oracle Aether/test/reference/oracle_aeth01.py (477 lines)
  and its bundled copy runpod/aeth01_canary/aeth01_cpu_oracle.py (381 lines); vectorised "GPU-shaped"
  NumPy gather implementation test/reference/gpu_aeth01.py (restated independently from the spec; a
  differential test compares them); CuPy kernel runpod/aeth01_canary/aeth01_gpu_kernel.py.
- Phases (oracle): decode_and_emit (WRITE opcode and energy >= write_cost; direction arg0 mod 4, field
  arg1 mod 5; energy field transfers min(payload, energy - cost)) -> group_contests by (target, field) ->
  arbitrate (max splitmix64 hash of seed, tick, target, field, source) -> commit_template (winner
  replaces byte; Mu flips one bit with hash-keyed probability) -> settle_energy (debit write cost and
  transfers; credit winner clamped to 255 headroom, losers' amounts destroyed; maintenance decay; hash-
  keyed replenishment) [IMPL, aeth01_cpu_oracle.py lines 103-255].
- Baseline "B-balanced" parameters: write cost 1, maintenance 1, replenishment +8 at 1/8, perturbation 0.1
  [CLAIM, engine card s2/s7].
E2. AETH-00 (aeth00.v1): 4-field frozen conformance law; Aether/production/aeth00.py, test/reference/
  oracle.py, oracle_independent.py, golden_vectors.py, mutants.py [IMPL exists; bodies not read].
E3. Observatory (Aether/observatory/, ~25 modules): aeth01_observatory.py (lattice scalars, 64-block
  maps), aeth01_graph.py (causal source->target edges), aeth02_* (closure, falsifiers, inflow/sustained
  cut, arg1), aeth03_variants.py (16 laws), aeth03_propagation.py (one-bit twin assay),
  aeth03_assay_audit.py, aeth03_content_probe.py, aeth03_rcv_paths.py, aeth03_unit.py (portable unit
  runner), reducers [IMPL].
E4. RunPod / GPU platform: Aether/runpod/prometheus_gpu/ (launch.py 1,548 lines, provider, billing,
  bundle, campaign, fanout, scout, telemetry, receipt, dryrun, cli; plus credentials.py and secrets.py,
  NOT read by rule), aeth01_canary/ (age_controller.py 1,198 lines, independent_reaper.py, pod_service,
  Dockerfile), flight.py, examples/ (hello_gpu, gpu_load, soak, param_sweep), foreign/ananke_conformance
  [IMPL exists].
E5. Tests: Aether/test/ (41 files; reported "984 passed, 5 skipped" at 251bc987e) [CLAIM].
E6. Execution records: ops/campaigns/C-002/E-003..E-012 (EXPERIMENT/RESULT/TASKS), Aether/runpod/receipts/
  (88+ receipt dirs), Aether/AETH-0x/evidence/ [IMPL].

## 3. Code architecture and dataflow

- One local rule, radius 1 (variant mov radius 2), synchronous: read previous grid -> proposals ->
  contests -> winners -> new template + new energy. All randomness is a pure hash of (seed, tick, site,
  field), state-free, so twin worlds receive identical injected streams [IMPL, oracle + aeth03_propagation
  docstring].
- Variants (aeth03_variants.py) each change one phase of v1 and carry their own SEMANTICS_ID; the v1 path
  is asserted bit-identical to gpu_aeth01 in test_aeth03_variants.py [IMPL from docstring]. List [IMPL]:
  v1, add (commit (old + payload) mod 256), hys (incumbent-value wins arbitration), chg (pay only if the
  write changes the target), cnd (second opcode 0x02 conditional on target low bits), str (direction =
  (arg0 + energy>>6) mod 4), mov (move not copy), rcv (a site that received a winning write last tick is
  active this tick; adds a 1-bit per-site flag), m4 (field = (arg1>>3) mod 5), fwd (content-forwarding
  control), rcv_add, rcv_cnd, rcv_str (combinations), rcv_sfx, rcv_adr, rcv_sfz (lesions).
- Twin assay (aeth03_propagation.py): fork two worlds differing in one bit; generation of a newly
  differing site = 1 + min generation of differing neighbours; locality violations counted every tick
  (nonzero voids the result); SUSTAINED origin = generation >= 5, radius >= 5, still adding after tick 50;
  self-test null flips the bit twice [IMPL].
- Code/doc disagreement: the docstring's claim that adjacency generation is "the length of the shortest
  causal chain" was shown false by the seat's own audit; it is a lower bound (equal to counterfactual
  causal generation in 84-100% of 2,793 audited events) [CORRECTION, Aether/AETH-03/
  PROPAGATION_ASSAY_AUDIT.md; ops/campaigns/C-002/E-003/RESULT.md]. The docstring at HEAD still states the
  exact claim [IMPL].
- gpu_aeth01.py docstring says it is NumPy, "THIS HAS NOT BEEN DONE OR TESTED ON REAL GPU HARDWARE"; the
  later CuPy kernel (runpod/aeth01_canary/aeth01_gpu_kernel.py) is what ran on A40s; the docstring was not
  updated [IMPL].

## 4. Claimed computational primitive vs actual mechanism

E1 aeth01.v1 and variants.
- Label: "executable matter", "GPU-native artificial physics", "native circuitry", later "propagation",
  "history matters" primitives.
- Smallest actual mechanism [IMPL]: a stochastic (hash-keyed) byte-copy cellular automaton with an energy
  budget: each energised WRITE site copies its payload into one neighbour field; most sites are not WRITE
  (1/256 opcodes), so most matter is inert; copied bytes can turn sites into or out of WRITE.
- What it could express in principle: copying, overwriting and routing of bytes; arbitrary local rules
  only via the variant mechanism (each a hand-written code change).
- Phenomenon the rulers tried to observe: persistent functional circuitry; propagation of a local
  difference; history-dependent persistence; content transport.
- Could the substrate perform it: the record says mostly no. v1 settles to ~92% frozen over 64-tick
  windows by ~2,500 ticks; without injected perturbation ~42% of template change stops at once and ~94%
  by +500; edges end mainly by source energy starvation (89%); a one-bit difference stays within ~1 site
  [RESULT-UNVERIFIED; AETH-02_CLOSE_2026-09-24.md; engine card s7; E-005].
- Could the ruler tell it from a cheap shortcut: partly. The seat repeatedly caught its own shortcuts:
  the H2 3.1x lifetime gap was a null without an energy term; rcv's propagation is its own relay rule
  (96% of secondary differences are the two quantities the rule moves), so it is a "calibration law";
  "counting is not change" (add: 83% constant-step); "generation depth is not reach" (v1 generation 56 at
  radius 3); the XOR content signature failed its own positive control (fwd, E-P1) so no content claim is
  possible in a rich soup [CORRECTION / RESULT-UNVERIFIED; RCV_REINTERPRETATION_2026-09-27.md,
  PHYSICS_DESIGN_03 s5.3].
E4 RunPod platform.
- Label: "reusable Prometheus GPU experimentation system".
- Actual mechanism: a launcher/controller around the RunPod API with checksummed module bundles, dry-run,
  cost projection, telemetry, receipts, reaping and billing reconciliation [CODE-INFERRED from module
  names and RUNPOD_ENGINEERING_0x reports]. Not a scientific substrate.

## 5. Representation/state architecture

Per site 5 x uint8 (40 bits) plus, for the rcv family, 1 bit "received last tick" [IMPL]. No
per-individual state, no registers beyond the bytes, no learned parameters. The whole world state is
H*W*5 bytes plus seed and tick; replay identity is a digest of the lattice bytes [IMPL, AETHER_SPEC
AETH-00 state section; engine card s6]. Observatory state is kept outside the physics ("NO observatory
metadata visible to simulated matter") [INTENT, AETHER_CONCEPT.md].

## 6. Organism/player architecture

None by design. "Not built in: individuals, assemblies, bodies, executable-configuration boundaries,
predecessors, construction events, recursive construction, an evaluation score, selection, termination
as an event, any objective" (engine card s3) [INTENT, consistent with the oracle code read [IMPL]].
"Assembly" language requires, in order, a self-maintaining bounded region, boundary-crossing influence,
and dynamic reproduction elsewhere; "None of the three has been observed" [CLAIM]. Configuration-
transmission requirements and a five-tier claim ladder exist on paper (AETH-01/HEREDITY_REQUIREMENTS.md;
KILL_GATES_01.md K1-K6) [INTENT]; never reached.

## 7. World/environment architecture (scale flagged)

- 2-D torus, von Neumann neighbourhood, synchronous [IMPL].
- Scales run [RESULT-UNVERIFIED as reported]: science at 128^2, 256^2, 512^2 CPU (128 origins per law per
  seed set, horizons 500-10,000 ticks); AETH-02 trajectories 3 x 2048^2 to 50,000 ticks (one truncated at
  ~47,000); First Light 6 worlds x 4096^2 x 5,000 ticks on one A40 ($2.02); capacity demonstration 16384^2
  = 268,435,456 sites at 7.42 s/tick, 113-128 bytes/site; 32768^2 OOMs (GPU_MEMORY_OPTIMIZATION_01;
  STATUS.md 2026-09-22 block).
- The large scales are engineering demonstrations. The size-control in AETH-02 shows 256^2 reproduces
  2048^2 bulk statistics within 0.1-3% (AETH-02_CLOSE s0) [RESULT-UNVERIFIED], i.e. scale added nothing
  observable for the measured quantities.
- One parameter regime (B-balanced) for every science result; only unstructured sparse soups as initial
  conditions; no gradients, boundaries or seeded structures (engine card s8) [CLAIM]. Toy-scale in the
  physics sense: 1-hop dynamics, 256 opcode values with one active.
- Measured irreducible energy leak: 3.04% per 5,000 ticks with every cost at zero, from destroyed loser
  transfers and headroom clamping (FIRST_LIGHT I4) [RESULT-UNVERIFIED].

## 8. Search/training/adaptation mechanism

None inside the physics (no selection, no reward, "observation and intervention only; no steering").
The search is the SEAT's: a hand-written ladder of one-change laws (ladder 1 persistence: add, hys, chg,
cnd, str; ladder 2 propagation: mov, rcv, m4), then pairwise combinations around rcv (rcv_add, rcv_cnd,
rcv_str), a forwarding control (fwd) and lesions (rcv_sfx, rcv_adr, rcv_sfz) [IMPL]. Bottleneck named by
the seat: the medium freezes; TH-009 asks for "a law whose own dynamics keep rewriting the medium without
being noise or counting" [CLAIM].

## 9. Measurement/ruler stack

- Bit-exact conformance: golden vectors, mutants, CPU oracle vs GPU-shaped vs CuPy differential tests;
  canary 300/300 bit-exact on GPU; replay chain verified 6/6 at 16.7 M sites cross-backend [CLAIM].
- Observatory scalars (write/activity/starved density, energy Gini, opcode entropy, edge fraction,
  edge lifetimes, cycle counts vs matched random graph) [IMPL exists].
- Falsifier designs with lesion/sham arms (H1 re-aim lesion, H2 sustained feeder cut vs sham, H3 arg1,
  H4 mut_numer = 0) [CLAIM].
- One-bit twin assay with locality check, adjacency and counterfactual generations; N1 propagation rule
  (P_sust above max(component) and above the SUM of components, floor 0.10, minimum pass 13/128); N2
  content rule (no evidential weight after E-P1 failed) [IMPL/CLAIM; PHYSICS_DESIGN_03 s2].
- Known-answer lane: 6 tasks, 19 attempts on 4 hosts, 0 disagreements (E-007) [RESULT-UNVERIFIED].
- Blind spots acknowledged: cannot see function; cannot see distributed informational structure; content
  transport undetectable in rich soup; holdout seeds are not sealed (engine card s12); single seed for
  AETH-02 falsifiers; H1b observational, not preregistered [CLAIM].

## 10. Baselines and controls

Matched random graphs (cycles 0.37x), independence nulls for edges (initially missing energy, then
repaired), sham arms for interventions, OFF arms (perturbation off), additive nulls for combinations,
components as baselines (super-additivity), fwd as positive control for content (FAILED), self-test
null (double flip), regression hash gates that existing laws are unchanged by lesion code [CLAIM; E-006,
E-010, E-011 RESULT files]. Partial-ring starvation (inert vs WRITE sites) replaced a full-ring "carrier
ablation" that the law itself forces, judged "a semantics check" not a falsifier [CORRECTION, Atlas
digest citing roles/Aether/calibration/LEDGER.md].

## 11. Historical experiment campaigns

AETH-00 conformance (2026-09-20; 3ff4619de, 2d2468965, 2959a7274). Q: can an exact executable-matter law
be specified, tested, replayed. Result: frozen aeth00.v1 with independent oracle, golden vectors, mutants.
Label: REPORTED POSITIVE (engineering only; "does NOT establish... emergence").

AETH-01 design/review/repair (2026-09-20..22). Astra review 01/02, Independent closure review 04, repair
ledger, kill gates K1-K6 (K1/K2/K3/K6 run; K4/K5 cheap fixtures; others deferred). Label: MIXED.

RunPod smoke and scale (2026-09-22). Smoke FAIL twice (Cloudflare 1010; RUNPOD_API_KEY guard), then
canary and scale receipts; memory wall moved 240 -> 113 bytes/site. Label: REPORTED POSITIVE
(infrastructure).

First Light 01 (2026-09-22; Aether/AETH-01/FIRST_LIGHT_01_2026-09-22.md). 6 worlds 4096^2 x 5,000 ticks.
"No endogenous dynamics... No phenomenon on the evidentiary ladder was observed, and none was tested
for"; certified-death condition; energy leak measured; 128^2 scouts predict 16.7 M-site behaviour.
Label: REPORTED NEGATIVE/NULL.

AETH-02 Native Circuitry (2026-09-23..24; NATIVE_CIRCUITRY_01 prereg and report; AETH-02_CLOSE).
3 x 2048^2 x 50,000 ticks plus 256^2 CPU falsifiers. H1 persistence is residue (lesioned recurrence 0;
92.3% frozen); H2 partly falsified; H3 unresolved; H4 perturbation supplies ~42% of change at once and
~95% cumulatively. Instrument defect: runner compared against a 250-tick-old snapshot (opcode per-field
change +128% relative bias); a claimed "observer consistency check" was an algebraic identity and was
withdrawn. Spend $2.83 of $3.00 [CLAIM]. Label: REPORTED NEGATIVE/NULL (with INSTRUMENT FAILURE
corrected).

AETH-02 closure H2/H3 (2026-09-26; PHYSICS_DESIGN_01 s2). H2 gap = null-model defect, residual = energy
supply (a sustained feeder cut leaves long-edge persistence at ~0.39x sham at +128 ticks, per the engine
card and Atlas digest; the underlying table was not read); H3 cycle deficit carried by
opcode overwrite and arg1 mod-5 perturbation. Label: REPORTED POSITIVE (mechanism of a null).

AETH-03 ladder 1 (2026-09-26; PHYSICS_DESIGN_01). add, hys, chg, cnd, str: 4 killed, add UNRESOLVED (83%
counting); every law footprint 0.5-1.5 sites per origin. Label: REPORTED NEGATIVE/NULL.

AETH-03 ladder 2 (2026-09-26; PHYSICS_DESIGN_02). mov and m4 KILLED, add closed, rcv UNRESOLVED: 6/128
origins sustained, generation 12, radius 11, with noise off. Label: INCONCLUSIVE.

C-002 research block (2026-09-27; ops/campaigns/C-002, RESEARCH_BLOCK_SYNTHESIS_2026-09-27.md):
- E-003 assay audit: locality holds (27,000 light-cone flips; bytes-only predicate without rcv's flag
  breaks, 32 violations vs 0); exactness claim withdrawn, lower bound. Label: INSTRUMENT FAILURE
  (repaired; no verdict change).
- E-004 rcv reinterpretation: calibration law; runs on a frozen map (same origin flipped at three times
  reaches the same sites). Label: LATER OVERTURNED (rcv as a positive).
- E-005 horizon 500 -> 10,000 ticks: locality conclusions horizon-robust for v1, add, rcv (OFF max radius
  2/5/7; rcv ON 39). Label: REPORTED NEGATIVE/NULL.
- E-006 combinations + fwd: rcv_add P_sust .172, rcv_str .109, rcv_cnd .016; N1 NEW_BEHAVIOUR for
  rcv_add, rcv_str; cause probe: not content transport; E-P1 positive control FAILED; 10,000-tick
  falsifier lost to memory-pressure kill + resume defect; >1 MiB artifacts silently dropped behind PASS
  receipts. Label: MIXED.
- E-007 known-answer lane: 19 attempts, 0 disagreements. Label: REPORTED POSITIVE (determinism).
E-008 horizon falsifier (2026-09-29, Fabric): HORIZON-DEPENDENT for both via clause (iii) only. Label:
MIXED.
E-009 fresh-seed replication (2026-09-29, seeds 4-7): rcv_add 22/128 (components rcv 4, add 1), rcv_str
15/128 (rcv 4, str 0); both REPLICATED under N1 (minimum pass 13/128); rcv_str "real but small and close to
the floor" [RESULT-UNVERIFIED, ops/campaigns/C-002/E-009/RESULT.md]. Earlier R-05 amendment had rcv_str
UNRESOLVED (N2 exact tie 12/128 = 0.09375; N1 by 1 origin) [CORRECTION, PHYSICS_DESIGN_03]. Label:
REPORTED POSITIVE.
E-010 steering lesion (2026-09-30): rcv_sfx 4/128 vs rcv_str 15/128 -> STEERING_REQUIRED; erratum on
per-seed wording (Harmonia #1056); does not separate dynamic coupling vs static correlation vs aim
distribution. Label: REPORTED POSITIVE (narrow).
E-011 trace lesion (2026-09-30): rcv_adr 10/128 vs rcv_add 22/128, additive null 5/128 -> PARTIAL; lesion
"incomplete by construction". Label: INCONCLUSIVE.
E-012 frozen-energy lesion: preregistered 2026-09-30 (7b7dea59e), no result on main. Label: UNKNOWN.

RunPod engineering ladder Iterations 1-5 (2026-09-24..27; RUNPOD_ENGINEERING_01..04): $1.59 of $5.00;
65-minute soak with hard controller kill and resume; 13 injected failure modes; 3 concurrent pods; flew
Ananke's suite unmodified (139 passed); reconcile to billing within 8% for settled flights; platform
defects found and fixed [CLAIM]. Label: REPORTED POSITIVE (infrastructure).

promexec reviews (2026-09-28, 09-30; roles/Aether/reviews/): Aether as independent code reviewer of
Odysseus's execution boundary; round 1 "stays EXPERIMENTAL / UNVERIFIED / NOT ENABLED" with findings
(world-readable /proc instructions, network access despite claim, root chown following a controlled
path); round 2 source review "nothing blocks install". Label: not science; REPORTED NEGATIVE then MIXED.

## 12. Reported results and later corrections (timelines)

T1. Edge lifetimes: "edges live 3.1x shorter than independence" (trajectory round) -> H2 falsifier ->
null lacked energy term; 89% of edge hazard is source starvation -> sustained-cut intervention confirms
energy supply -> closed [CORRECTION].
T2. Trajectory headline figures: lag-defect runner (250-tick-old prev) -> bias measured (opcode +128% rel)
-> corrected figures (~25.5% STATE_CHANGING, perturbation share 38% -> 42%); qualitative conclusions kept
[CORRECTION, AETH-02_CLOSE s5].
T3. rcv: "first propagating law" (ladder 2, UNRESOLVED positive) -> partial-ring intervention and path
probe -> "calibration law": its own relay, frozen map, amplified 4.8x by noise [CORRECTION].
T4. Assay exactness: "generation = exact shortest causal chain" -> audit: lower bound, 84-100% agreement
-> "every prior secondary/sustained claim was conservative" [CORRECTION].
T5. Content: N2 content clause -> fwd positive control fails -> N2 has no evidential weight for any law
[CORRECTION].
T6. rcv_str: NEW_BEHAVIOUR (E-006) -> R-05 amendment UNRESOLVED (exact tie) -> E-009 replication REPLICATED
-> E-010 steering lesion STEERING_REQUIRED -> E-012 pending [CLAIM chain].
T7. Platform PASS receipts: artifacts > 1 MiB "verified then silently dropped"; Attempt PASS is not a
science PASS [CORRECTION, RESEARCH_BLOCK_SYNTHESIS].

## 13. False-positive archaeology

- Null-model omissions manufacture structure (H2's missing energy term).
- The rule supplies its own phenomenon (rcv): an effect caused by the one written rule change is not
  evidence of emergent propagation (cf. Cosmos's certificate restatement).
- Counting masquerades as change (add); generation depth masquerades as reach; activation timing
  masquerades as content.
- Forced interventions as falsifiers (full-ring starvation the law itself forces).
- Observer identities as validation (algebraic identity withdrawn).
- Lagged snapshots inflate change rates.
- Positives near the floor: rcv_str passes N1 by +2 origins over 128 on fresh seeds; its first N2 pass was
  an exact tie at the >= boundary.

## 14. Likely false-negative regimes

- Single energy regime (B-balanced); "the frozen-medium result may be a property of B-balanced energy,
  not of the law" (engine card s8) [CLAIM].
- Only sparse unstructured soups; no seeded structures or gradients.
- One active opcode out of 256 in v1: most matter is inert by construction; asynchronous or multi-site
  rules, reaction automata and mobile particles were rejected at design and never built.
- Detectors blind to distributed informational structure and to content transport in rich soups.
- Observation-only doctrine (no selection or pressure) means no adaptive process exists to find rare
  organised states.

## 15. Phase 3 audit (per engine)

E1 aeth01.v1 + variants
a. Representation richness: hierarchy NO (flat bytes); compositional structure NO (no composition
   operator; bytes are copied, not combined, except add's modular sum); variable binding NO; memory
   PARTIAL (bytes persist because frozen; rcv flag is 1 bit for one tick; add leaves marks); recurrence
   PARTIAL (global synchronous update, no recurrent structure observed); counterfactual state YES as an
   instrument (exact twins, counterfactual parents), NO inside the physics; latent variables NO (all
   state observable); temporal abstraction NO; spatial abstraction NO; reusable substructure NO; dynamic
   routing PARTIAL (direction from arg0; str/rcv_str route by energy); self-reference PARTIAL (a site can
   overwrite a neighbour's opcode, turning it into or out of WRITE; no observed self-maintenance).
b. Reasoning opportunity: none. There is no task, no objective, no environment demanding anything; the
   doctrine forbids imposing one. The dynamics are below simple FSM control.
c. Shortcut surface: the written rule itself (rcv); injected noise (perturbation supplies most change);
   energy bookkeeping; frozen residue that looks like structure; counting.
d. Ruler resolving power: very high for exact causal attribution of a single difference (locality checked
   every tick, counterfactual parents, bit-identical cross-host replay); low for function, content or
   distributed information (content signature failed its positive control).
e. Scale: 5 bytes x up to 268 M sites demonstrated; science at 128^2-2048^2; horizons to 50,000 ticks;
   128 origins x 4 seeds per law; 16 laws; one regime; one initial-condition family; compute ceiling
   one A40 (~370 M sites predicted max), science mostly laptop CPU.
E4 RunPod platform: not a substrate; representation audit not applicable. Relevance is as an executor
   with receipts and cost control.

## 16. Research reports and substantial documents

- Aether/AETHER_CONCEPT.md, AETHER_DOCTRINE.md, AETHER_DECISIONS.md, AETHER_OPEN_QUESTIONS.md - concept and
  doctrine (2026-09-20).
- Aether/AETHER_SPEC.md, AETHER_TEST_PLAN.md, AETH-00_REVIEW.md, AETH-00A/B_RECEIPT.md - frozen aeth00.v1.
- Aether/AETHER_ENGINE_CARD.md - lens, world, known physics, frontier, runtime (best single overview).
- Aether/AETH-01/AETH01_REPAIRED_FREEZE_CANDIDATE.md, PHYSICS_SPEC_DRAFT.md, ECONOMICS.md,
  PHYSICS_CANDIDATES.md, HABITABILITY.md, HEREDITY_REQUIREMENTS.md, KILL_GATES_01.md, OBSERVATORY.md,
  REQUIREMENTS.md - AETH-01 design (not read in depth).
- Aether/AETH-01/ASTRA_REVIEW_01.md, ASTRA_CLOSURE_REVIEW_02.md, INDEPENDENT_CLOSURE_REVIEW_04.md,
  REPAIR_LEDGER_01.md, ADVERSARIAL_ANALYSIS.md, REVIEW_PACKET_* - reviews and repair (not read).
- Aether/AETH-01/FIRST_LIGHT_01_2026-09-22.md - first scale run, null.
- Aether/AETH-01/GPU_MEMORY_OPTIMIZATION_01_2026-09-22.md, RUNPOD_*_RECEIPT_2026-09-22.md - GPU scale.
- Aether/AETH-01/NATIVE_CIRCUITRY_01_PREREGISTRATION_2026-09-23.md, NATIVE_CIRCUITRY_01_2026-09-24.md,
  AETH-02_CLOSE_2026-09-24.md - AETH-02.
- Aether/AETH-03/PHYSICS_DESIGN_01/02/03, PROPAGATION_ASSAY_AUDIT.md, RCV_REINTERPRETATION_2026-09-27.md,
  RESEARCH_BLOCK_SYNTHESIS_2026-09-27.md, FOLLOWUP_RANKING_2026-09-30.md - AETH-03.
- Aether/pivot/AETHER_REVIEW_2026-09-27.md - external review packet (5,384 words).
- Aether/RUNPOD_ENGINEERING_01..04 - platform reports.
- ops/campaigns/C-002/CAMPAIGN.md and E-003..E-012 - experiment records.

## 17. Journals/TODOs/backlogs/pivots/abandoned branches

roles/Aether/journal/2026-09-19, -20, -22, -24, -26, -27; TODO.md (authoritative resume state per the
seat); BACKLOG_H0H5.md; DEFECTS.md (DEF-AETH-001 ubu001 disk full, resolved by Odysseus); calibration/
LEDGER.md; WAKE.md; WORK_STATE.json; threads TH-007 ACTIVE, TH-008..TH-012 PARKED (TH-009 frozen medium,
TH-012 platform asset status) [IMPL]. Branches: aether/base-role-adopt-2026-09-19,
aether/aeth01-memwall-2026-09-22 (integrated into main 183388e39), aether/mwo0001-2026-09-28 (zero ahead of
main per Atlas digest) [CLAIM]. Stale duplicate worktree C:/Prometheus-aether noted [CLAIM].

## 18. Dependencies on other engines and seats

- Clean-room by doctrine (no BEE/NPE/SFE borrowing) [INTENT]; code imports numpy (and CuPy on pods) only,
  per engine card s10 [CLAIM; consistent with oracle imports read].
- Cosmos: the CWE charter named Aether/AGE as a donor; Cosmos declined GPU substrates (D7); C3 holdout E
  "reserved for Aether from M4 only", not commissioned [CLAIM].
- Ananke: foreign conformance suite flown on the platform; CUDA-graph finding applicable [CLAIM].
- Odysseus (Fabric, promexec), Harmonia (evidence audit #1056), Artemis (#1002 review questions), Nyx
  (manifest drift report 2026-09-19), Aporia (CWO), Astra (architecture reviews) [CLAIM].

## 19. Scaling limitations

- Scale is not the bottleneck: 256^2 reproduces 2048^2 statistics; the medium freezes regardless.
- GPU kernel is launch-bound in eager mode (Ananke finding, not yet applied) [CLAIM].
- One device ceiling ~370 M sites; 32768^2 OOMs.
- Laptop memory-bound at 512^2 beyond ~3 concurrent jobs.
- Platform tied to BUCKKEEP via the RunPod key; Fabric worker disk exhaustion.

## 20. Lens potential for Phase 3 (descriptive)

- Substrate: exact, local, deterministic byte-copy lattice with energy; bit-identical across hosts.
- Organisms: none.
- Worlds: torus soups in one energy regime.
- Pressures: none (doctrine).
- Phenomenon family: propagation, persistence and interaction of single local differences.
- Current resolving mechanism: one-bit twins with checked locality and counterfactual parents; lesion
  laws on a shared bit-identical code path; preregistered N1 rules with additive nulls.
- Likely resolution ceiling: causal reach of one bit; cannot resolve function or content.
- Noise sources: injected perturbation (by design), hash-keyed arbitration, origin sampling (128 per seed).
- Architectural limit: one active opcode, radius-1 copy semantics, frozen medium.
- Reusable parts: twin assay, counterfactual-parent audit, known-answer lane, portable unit runner with
  LF-normalised code hashes, RunPod platform with receipts, the seat's false-friend catalogue.
- Toy-grade parts: aeth01.v1 itself as a substrate for reasoning; the observatory scalars.
- Unknowns: other energy regimes; seeded structures; E-012 outcome; whether any law rewrites the medium.

## 21. Open questions / coverage gaps

- NOT read: most AETH-01 design and review documents (Astra reviews, repair ledger, heredity requirements
  beyond headings, habitability, economics), PHYSICS_DESIGN_01/02/03 bodies (used via synthesis, Atlas
  digest and RESULT files), NATIVE_CIRCUITRY_01 body, RUNPOD_ENGINEERING_01..04, pivot review beyond s0,
  journals, TODO.md, calibration LEDGER (via Atlas digest), the CuPy kernel, aeth00.py, observatory
  modules other than the variants and propagation docstrings, all tests, all receipts and evidence dirs,
  examples/dist tarballs.
- NOT read by rule: Aether/runpod/prometheus_gpu/credentials.py and secrets.py.
- Several numbers (H2 sustained-cut ratio, E-005 radii, E-006 P_sust values, platform spend) are taken from
  the research-block synthesis and the Atlas digest (roles/Atlas/inference_harvest_2026-09-30/workers/
  digests/cosmos_aether_hecate.md) and were spot-checked only for E-009 and E-011 RESULT tables.
- No holdout paths exist under Aether/. No code was executed.
