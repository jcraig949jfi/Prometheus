# Bellerophon -- toolbox research for the two ecosystems (SFE, NPE)

Currency: 2026-09-18. Author: Bellerophon[m2-c95cc146], a seat with no
charter yet; this is a DISCUSSION INPUT, not a ruling and not a plan of
record. Every number below is either read from the tree (path given) or
measured today on this host (command given). Nothing is from recall.

Operator input (chat, 2026-09-18, paraphrased to one line; the long text is
the operator's and is not re-typed here): Archaeon designs WITH the toolbox
and does not BUILD it -- worlds / candidates / pressures / experiments are
Archaeon's degrees of freedom; their implementation lives below the
boundary (Techne finds, Nyx dissects, Daedalus/infra hardens, Vivarium
executes). Tools named: Box2D, MuJoCo, VM designs, interpreters, JIT,
SIMD evaluators, graph engines, physics kernels, search algorithms.

--------------------------------------------------------------------------
1. WHAT THE TWO ECOSYSTEMS ARE TODAY (read from the tree)
--------------------------------------------------------------------------

SFE ecosystem (M2, on main)
  runtime    SerendipityFoundry/SerendipityFoundryEngine/sfe/: worlds as the
             isolation unit, atomic work queue with leases, per-world hash
             chain, fork-by-reference, prediction ordering, budgets, a
             pluggable Executor(WorkPackage)->ExecutorResult contract with
             an honest reproducibility class per result (BIT_DETERMINISTIC
             / SEMANTIC / PARTIAL / NONDETERMINISTIC). One SQLite file.
             Reference executors are bitstring scorers; executors run
             in-process; no subprocess/remote isolation yet
             (SERENDIPITY_FOUNDRY_STATUS.txt "known limitations").
  loop       Archaeon -> Postgres queue -> Vivarium -> SFE/worlds/players
             -> PEW -> Archaeon (roles/Archaeon/CHARTER.md, roles/Vivarium/
             CHARTER.md). Vivarium evaluates a PREREGISTERED outcome rule
             mechanically; absent a rule it records INCONCLUSIVE.
  substrates Proteus tape VM: 25 frozen primitives, 4-word instructions,
             bounded tape of 32-bit words, pure stdlib, content-addressed
             manifests, 13 descent operators (proteus/ARCHITECTURE.md).
             Proteus graph substrate v0 behind proteus/graph/handover.py
             (player_for / meter_for / organism_record_for / descend_for /
             generate_for / fingerprint_for, dispatched on manifest schema).
             archaeon/campaign6/substrate.py runs EITHER through those six
             calls: this is already a substrate-neutral seam.
             wforge Encounter (SerendipityFoundry/worldfoundry/wforge/
             world.py): integer-only world, xorshift streams, trace hash per
             tick -- the semantic oracle both ecosystems use.
  composer   archaeon/frontier/: experiments as validated specs with declared
             capabilities (capabilities.py, specs.py), a Python scheduler
             that discovers / checks / executes / resumes / branches (DF-010,
             commit 16799b8bd). This is the "sweep / perturb / transfer /
             replay" layer in embryo.
  execution  everything is pure Python; no numba, no torch, no native
             kernels in the SFE tick path.

NPE = Nestor's Primordial Engine (M1; branch
nestor/sidequest-graphworld-2026-09-14, 1,093 files / 195,678 lines NOT
on main; primordial/ does not exist on origin/main)
  contract   primordial/core/contract.py: World (batched, n_envs stepped in
             lock-step, uint16 obs / int32 actions / int32 charge, and
             trace_hashes() as THE oracle), Brain (act/adapt/cost),
             Channel (metered send/recv), Genome (bytes + QD descriptor);
             receipts with engineering and science ledgers kept disjoint;
             HOT-PATH RULE: no str/JSON on the hot path.
  lanes      A fabric (Redis Streams + FalkorDB bus, durable ledger), B soup
             (worlds), C brain (tensor-train policies, plastic rank, affine
             plastic), D lingua (metered channels, codebooks), E qd (MAP-
             Elites archive in Redis), plus F/G/H/P/Q/W/T/U/R builders.
  measured   primordial/soup/review/REVIEW_PACKET_B_ROUND1_2026-09-14.txt:
             five exact forms of the wforge world (numpy batched, numba
             prange, Redis Lua, FalkorDB Cypher, fused numba world+brain),
             320/320 trace hashes == wforge. numba plateau 46-70M steps/s;
             numpy passes wforge between 16 and 64 envs; one Redis ~190k
             steps/s aggregate; FalkorDB slowest at every size (341 steps/s
             at n=1). Fused world+brain 6.6x-24x over numpy world +
             forward, 49.7x-99.8x over the numpy rollout.
             A Warp kernel of the same world exists (primordial/nv/warp/
             world.py, "N3"), plus cuTensorNet and CUDA-graph probes.
             Round 7 (REVIEW_PACKET_ROUND7_2026-09-16.txt): the torch GPU
             lock-step evaluator FAILED exactness (6 fitness + 3 cells
             mismatched in 819,200 evaluations) and ran ~7x slower than
             CPU; code chose cpu_sequential. GPU exactness is an OPEN
             anomaly there, not a closed question.
  contract   roles/Nestor/PROMETHEUS_SUCCESS_CONTRACT.md: A compression
             (parity at smaller footprint), B invariance (graft to domain B
             without modification), C scaffolding (evolve the evolver).
  state      R16 world screen complete, 74/74 cells, exactly ONE survived
             world; replication needs a DIFFERENT world set -- "a design
             question for round 8". That is a direct demand for more worlds.

Host facts measured today on M2 (SPECTREX5), this worktree:
  python 3.14.4; numba 0.67.0 IMPORTS AND JITS (10M-element njit loop:
  compile+run 0.71 s, second call 0.0032 s) -- so TECHNE-85's "numba on
  3.14 blocked by Smart App Control" does NOT hold for this interpreter
  today (verified the property, not the label; TECHNE-85 may describe a
  different wheel or an earlier date); numpy 2.4.4; torch 2.11.0+cu128
  with CUDA available on an RTX 5060 Ti 16 GB; WSL Ubuntu 24.04 with docker
  29.1.3 and python 3.12.3 (no gcc on the WSL PATH). Not installed: jax,
  warp, graphblas, Box2D, mujoco, brax, taichi, wasmtime, pyribs, qdax,
  rustworkx. Techne's fossil catalog (techne/fossils/CATALOG.json, 121
  rows) holds NO physics engine; nearest relatives are avida, corewar-
  redcode, femtolisp, pforth, tinyscheme, picorv32, tinycc, go-explore,
  c-cmaes, minisat.

--------------------------------------------------------------------------
2. THE CRITERION, MAPPED ONTO WHAT EXISTS
--------------------------------------------------------------------------

"Archaeon owns the experimental degrees of freedom, not their
implementation" is already half-built, three times, without a shared name:

  seam                          SFE side                  NPE side
  ----------------------------  ------------------------  -----------------
  world ABI                     wforge World + campaign6  contract.World
                                worlds/runtime.py         (batched, trace
                                                          hash oracle)
  candidate/organism ABI        proteus handover (six     contract.Brain +
                                dispatch calls on the     contract.Genome
                                manifest schema)
  execution ABI                 sfe.executors.Executor    fabric worker +
                                (+ repro class)           broker grants
  experiment composition        archaeon/frontier specs   bus one-line
                                + capabilities            hypothesis + lane
                                                          run scripts
  selection                     archaeon/wse/evolve       primordial/qd
                                FOUNDRY, Proteus descent  (MAP-Elites in
                                                          Redis)

So the toolbox is not a greenfield package. It is (a) one ABI that both
sides' seams already satisfy or can be adapted to in a few lines, and (b)
the ADMISSION procedure that lets a new implementation of a slot (a Box2D
world, a numba evaluator, a Brainfuck VM) enter either ecosystem with the
same evidence: oracle agreement, controls, repro class, throughput row per
host, license and native-dependency declaration. NPE's contract.py is the
better starting text for (a) because it is batched, integer-typed, and
carries the oracle in the interface; SFE's Executor is the better starting
text for the execution/repro half. Neither should be rewritten; the
toolbox package IMPORTS both and provides adapters.

Proposed shape (names as the operator wrote them; package name open):

  prometheus/toolbox/worlds/       DiscreteWorld (wforge Encounter as the
                                   reference impl), GraphWorld (NPE B2 /
                                   Proteus graph), CellularWorld,
                                   Physics2D, ResourceNetwork
  prometheus/toolbox/candidates/   TinyVM (Proteus tape VM wrapped),
                                   GraphProgram (Proteus graph organism),
                                   StateMachine, TensorBrain (NPE C),
                                   TapeSoup (BFF-style, see s3.5)
  prometheus/toolbox/pressures/    charge / delay / regime-switch /
                                   metered-channel (NPE D) / budget (SFE)
  prometheus/toolbox/experiments/  sweep, perturb, transfer, replay ->
                                   emit archaeon/frontier specs (SFE) or
                                   NPE bus jobs; never execute directly
  prometheus/toolbox/admission/    the packet a component must carry
                                   before either ecosystem may schedule it

--------------------------------------------------------------------------
3. THE TOOLS, SLOT BY SLOT (research + fit)
--------------------------------------------------------------------------

3.1 Physics2D
  Box2D v3 (C library; SIMD, multithreaded, cross-platform deterministic
    by design). Python bindings are the weak point: box2d-python 0.1.2
    (early preview, API unstable, last release 2025-03), pyb2d3
    (DerThorsten), giorgosg/box2d-py; legacy pybox2d (v2.3) unmaintained
    since 2016 and conda-only; POET's world is gym[box2d] on that legacy
    binding (roles/Techne/BACKLOG_H0H5.md TECHNE-104/112).
    FIT: high for the SLOT, low for any current binding. Recommended route:
    a thin ctypes/cffi layer over Box2D v3's C API compiled once per host
    (WSL gcc or MSVC), owned below the boundary, exposing step-N-worlds
    with fixed-point-quantised state readout so a trace hash exists.
    Repro class SEMANTIC (float) unless the readout quantisation is proven
    bit-stable across hosts -- then BIT on that host class only.
  MuJoCo (pip wheels for Windows; CPU; deterministic given same binary).
    MJX = JAX (GPU on Windows means WSL2 only). MuJoCo Warp (alpha,
    NVIDIA-only, reported >100x MJX on complex scenes, PyTorch-friendly;
    will fold into MJX when it leaves alpha). Brax = JAX.
    FIT: 3D is not asked for today; MuJoCo CPU is the cheapest honest 3D
    slot if Archaeon ever wants one; do NOT take a JAX dependency on the
    Windows hosts (jaxlib refuses on M3 already: TECHNE-113).
  Rapier (Rust, cross-platform deterministic mode) has no official Python
    binding; parked.
  NVIDIA Warp: NPE already has a Warp world kernel (N3). Warp is the one
    GPU route that keeps integer semantics under our control; the torch
    lock-step evaluator was rejected for INEXACTNESS in R7, not for speed
    alone, so any GPU world enters through the trace-hash oracle or not
    at all.

3.2 CellularWorld
  Lenia / Flow-Lenia: already in the refinery via ASAL (Techne HARM-55,
    Harmonia's 395 rollouts). cax (JAX cellular automata) is the neat
    library and is JAX -- same Windows caveat. A numba/torch CA kernel is
    ~100 lines and can carry a trace hash on integer-state CA (GoL,
    totalistic, Wireworld) and a quantised hash on Lenia.
  Golly/hashlife for Life-family worlds is available but overkill.
  FIT: high; cheapest new world class; integer CA gives BIT repro for free.

3.3 GraphWorld / graph engines
  python-graphblas (SuiteSparse): NPE B2 already proved GraphBLAS mxm/ewise
    rules and Cypher give the same trajectory hash (50/50). FalkorDB was
    the slowest form at every size and is SSPL (primordial/README.md's
    provenance rule). rustworkx (Rust, fast, permissive) and networkx
    (installed, slow) for topology/analysis, not for the tick path.
  Proteus graph substrate is the SFE-side organism-as-graph.
  FIT: GraphWorld should be the GraphBLAS form; FalkorDB stays a bus/
    ledger convenience on M1, never a tick-path dependency of the toolbox.

3.4 DiscreteWorld / ResourceNetwork
  wforge Encounter is the reference and the oracle; keep it frozen.
  PufferLib Ocean (C environments, millions of steps/s, RL-framed) and
    Craftax/Gymnax/Jumanji (JAX) are the external fast-env families; they
    carry RL assumptions (reward, episodic reset) and JAX or C build
    chains. Take IDEAS (shared-memory vectorisation, C step kernels), not
    the packages, unless a specific world is wanted.
  ResourceNetwork has no external donor worth the dependency; a
    GraphBLAS flow-on-graph world is the natural build.

3.5 Candidates: VMs, interpreters, soups
  Proteus tape VM (frozen, stdlib, 25 primitives) is TinyVM today.
  BFF (Agueras y Arcas et al. 2024, "Computational Life"): self-modifying
    Brainfuck dialect over 64-byte tapes, self-replicators emerge in ~40%
    of runs within 16k epochs, no explicit fitness. Pure-Python reference
    implementations exist; a numba port is a day. This is the most
    north-star-shaped candidate substrate on the list (no designed
    reasoner, selection emerges from interaction) and it is trivially
    batched and hashable.
  CoreWar/redcode, Avida, Tierra: already fossils in Techne's catalog;
    Avida is being made the reconstruction benchmark (operator directive 4).
  Push / Cartesian GP / linear GP: evoGP (EMI-Group, PyTorch + CUDA
    kernels) is the tensorised tree-GP evaluator that matches our torch
    stack; JAX-based ones do not.
  wasmtime as a sandbox for evolved NATIVE candidates: deterministic,
    metered (fuel), memory-safe; heavy for now, right shape for later.

3.6 Evaluators: JIT / SIMD / batching
  numba is the measured winner on M1 (46-70M steps/s, fused 50-100x) and
    works on M2 today (measured above). It is the default "fast
    evaluator" implementation for integer worlds and brains.
  llvmlite (numba's backend) is the honest JIT route for EVOLVED PROGRAMS:
    compile a TinyVM genome to LLVM IR once, run it over a batch. This is
    where "JIT" in the operator's list belongs -- not JIT of the runtime
    but JIT of the organism. Cost: medium; gain: unknown until measured
    against the fused numba interpreter (a real experiment, not a given).
  torch: keep for tensor brains; do not route integer worlds through it
    (R7 exactness failure).
  Warp: the GPU path with a semantics contract; already prototyped.
  "SIMD evaluators" in the GP sense (evaluate the population as one
    vectorised program over env batches) is exactly NPE's fused kernel
    B6; the toolbox should name it and expose it, not rebuild it.

3.7 Search / selection
  MAP-Elites: NPE has its own Redis-archived implementation; pyribs
    (numpy, CPU, permissive, Windows-clean) is the reference library for
    CMA-ME/CMA-MAE variants; QDax is JAX. EvoX (PyTorch, 50+ EAs,
    torch.compile) fits the torch stack for population-side GPU work.
  CMA-ES (c-cmaes fossil), Go-Explore (fossil, runnable container),
    POET (fossil, in the refinery), novelty search, MCTS: all exist as
    bodies; the toolbox slot is `pressures/` + `experiments/`, and the
    admission packet is what decides whether a body becomes a component.

--------------------------------------------------------------------------
4. INTEGRATION AS COMPONENTS: what "admitted" would mean
--------------------------------------------------------------------------

A component (world, candidate, pressure, evaluator, selector) is ADMITTED
to a toolbox slot when it carries, committed beside it:
  1. the slot ABI it implements (World / Brain / Genome / Channel /
     Executor) and a 20-line conformance test against the ABI;
  2. its ORACLE: trace-hash agreement with the slot's reference
     implementation on a sampled episode set (wforge for DiscreteWorld,
     GraphBLAS form for GraphWorld, the CA reference for CellularWorld;
     a quantised-state hash + tolerance for float physics), with the
     repro class declared as SFE does (BIT / SEMANTIC / PARTIAL / NONDET);
  3. three controls where it is measured: positive (detects real
     signal), negative (no signal from nothing), CHEAT (an implementation
     that skips the mechanics must FAIL the oracle -- NPE B1's rule);
  4. a throughput row per host class (steps/s, n_envs sweep) so the
     "fast evaluator" claim is a number with a date;
  5. license (SPDX), native deps, host class, build recipe (Techne's
     "executable fossil packet" fields, reused verbatim);
  6. the two ecosystem adapters: an SFE Executor kind and an NPE fabric
     job kind, each one file.

Then each ecosystem consumes components the way it already consumes its
own: SFE via a new Executor kind claimed by Vivarium and specs emitted by
archaeon/frontier; NPE via lane B/C/E jobs on the bus. Archaeon's code
then reads as the operator wrote it -- experiment(environment=...,
candidate=..., pressure=..., sweep=...) -- and the toolbox turns that into
frontier specs (SFE) or bus jobs (NPE) without Archaeon naming Box2D,
numba or Redis.

Ownership under the operator's division, as I read it:
  Techne     finds + preserves the machinery (fossil / acquisition packet)
  Nyx        dissects when a body is interesting; names the pressure
  toolbox    ABI, adapters, admission tests, throughput rows -- the layer
  curator    the operator's text calls "infrastructure exposes primitives"
  Daedalus   hardens the SFE-side execution ABI (subprocess/remote
             executor isolation, metering) once a component needs it
  Nestor/A   hardens the NPE-side fabric for the same components
  Vivarium   executes; Archaeon composes and interprets
The curator seat is the one that does not exist today. If that is what
Bellerophon is for, the charter should say so; I am not claiming it.

--------------------------------------------------------------------------
5. FIVE THINGS I WOULD START, IN ORDER (each with the artifact)
--------------------------------------------------------------------------

  1. ABI unification note, not code: a one-file diff table showing that
     contract.World / wforge / campaign6 worlds and contract.Brain /
     proteus handover already agree or differ on each method, with the
     adapter cost in lines. Artifact: roles/Bellerophon/ABI_DIFF.md.
     Blocker: none (all read-only).
  2. CellularWorld (integer CA, numba, trace hash) as the FIRST admitted
     component, because it needs no native dependency, gets BIT repro,
     and exercises the whole admission packet end to end on both hosts.
     Artifact: prometheus/toolbox/worlds/cellular.py + admission/ rows.
     Blocker: package location / name (operator; NEW decision).
  3. BFF TapeSoup candidate substrate, numba, batched, hashable; measured
     for self-replicator emergence rate against the paper's 40% / 16k
     epochs as the positive control. Artifact: candidates/tapesoup.py +
     the emergence-rate rows. Blocker: none.
  4. Box2D v3 through a ctypes shim built in WSL, quantised-state hash,
     SEMANTIC repro, throughput row vs n_worlds. Artifact: worlds/
     physics2d.py + the build recipe + the packet. Blocker: gcc in WSL
     (not on PATH today) -- a one-line apt install, but it is a host
     change and I would ask first.
  5. JIT-the-organism experiment: llvmlite compile of Proteus tape-VM
     genomes vs the fused numba interpreter, same oracle, same batch.
     This is a REAL question (it may lose). Artifact: evaluators/
     llvm_vm.py + the crossover rows. Blocker: item 1.

What would make this whole direction NOT worth continuing: if Archaeon's
frontier specs and NPE's bus jobs cannot be emitted from one experiment
object without a per-ecosystem rewrite of the experiment (then the
toolbox is two toolboxes and should be named so), or if no admitted
component changes what R16-style world screens can find (then the
bottleneck is worlds-as-science, not worlds-as-machinery, and Archaeon
should be designing worlds directly on wforge).

Conflicts of interest: a new seat benefits from there being a new layer
to own. Read section 4's ownership paragraph with that in mind.

Sources consulted outside the tree (2026-09-18):
  box2d-python https://pypi.org/project/box2d-python/ ; pyb2d3
  https://github.com/DerThorsten/pyb2d3 ; pybox2d
  https://github.com/pybox2d/pybox2d ; MuJoCo Warp
  https://mujoco.readthedocs.io/en/latest/mjwarp/ and
  https://github.com/google-deepmind/mujoco_warp ; Computational Life
  https://arxiv.org/pdf/2406.19108 and
  https://github.com/gustavsoderstrom/computational-life ; QDax
  https://github.com/adaptive-intelligent-robotics/QDax ; pyribs
  https://docs.pyribs.org/en/stable/ ; PufferLib https://puffer.ai/docs.html ;
  EvoX https://github.com/EMI-Group/evox ; evoGP
  https://github.com/EMI-Group/evogp
