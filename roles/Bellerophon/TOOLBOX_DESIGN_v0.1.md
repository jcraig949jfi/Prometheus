# The Prometheus Toolbox -- concept design v0.1

Currency: 2026-09-18. Author: Bellerophon[m2-c95cc146], explorer and
designer of the toolbox concept (operator directive 3, verbatim in
prompts/2026-09-18_charter/). Status: DRAFT FOR DISCUSSION. Nothing here
is built; the builders are other seats. Grounding: TOOLBOX_RESEARCH_
2026-09-18.md (what SFE and NPE are, with paths and measured numbers).

--------------------------------------------------------------------------
0. THE ONE SENTENCE
--------------------------------------------------------------------------

The toolbox is a small set of SLOTS with frozen integer-first contracts,
a frozen reference implementation per slot, an ADMISSION packet that any
donor or home-grown implementation must carry to fill a slot, and an
EXPERIMENT grammar that composes filled slots into specs that SFE
(frontier) and NPE (bus) can each execute -- so that Archaeon owns the
experimental degrees of freedom and never their implementation.

Design criterion (operator): if Archaeon ever has to know whether
Physics2D is Box2D, Warp or a Rust engine, the toolbox has failed.

--------------------------------------------------------------------------
1. WHERE IT SITS (the refinery, extended one stage)
--------------------------------------------------------------------------

  Techne      acquires bodies: executable fossil packets (identity, hash,
              license, runtime deps, fixtures, one demo command)
     |
  Nyx         dissects: ORGAN (reusable mechanism) + PRESSURE (what the
              mechanism answers), ancestry preserved
     |
  TOOLBOX     Bellerophon designs the slot contracts, admission packet,
  (concept)   reference implementations' SPECS and the experiment
              grammar; names which organ fills which slot
     |
  builders    fill slots: Daedalus (SFE execution ABI, isolation,
              metering), Nestor lanes (NPE fabric/soup/brain/qd), Proteus
              (candidate substrates), Ludus (worlds), Theophrastus
              (ecology pressures), or a vibe-coded amalgamation for the
              small pure-Python/numba pieces (most of them -- see s4)
     |
  Vivarium / NPE lanes   execute admitted components under specs
     |
  Archaeon    composes experiment(environment, candidate, pressure,
              sweep, controls); reads receipts; designs the next
     |
  Harmonia    adjudicates any claim that a component changed what search
              can find (the toolbox itself claims nothing)

The toolbox is a LAYER, not a seat's private code: components live where
their builders live; the toolbox owns the contracts, the registry, the
admission tests and the adapters. Concretely one package (name open,
decision D-BELL-1) with: contracts/, registry/, admission/, adapters/
{sfe,npe}/, experiments/. Reference implementations are IMPORTED from
where they already live (wforge, proteus, primordial) and wrapped, never
copied (primordial/README.md's provenance rule generalised).

--------------------------------------------------------------------------
2. THE SLOTS (seven, and why exactly these)
--------------------------------------------------------------------------

The operator's list -- worlds, candidates, pressures, observations,
controls, transformations, sweeps -- factors into seven slot kinds. Each
has a contract, a frozen reference, and an oracle.

  slot          what fills it                          reference today
  ------------  -------------------------------------  ------------------
  World         batched environment; integer obs/act;  wforge Encounter
                trace_hashes() per env                 (integer, xorshift,
                                                       sha256 trace)
  Candidate     an organism: genome bytes + controller primordial Brain/
                act()/adapt()/cost(); descent ops      Genome, Proteus
                                                       tape VM + 13 ops
  Pressure      a World TRANSFORMER: wraps any World    NPE charge/delay/
                and changes its economy, observability regime_period,
                or dynamics; carries its own oracle     lingua metered
                                                       channel, SFE budget
  Observer      descriptors and measures over traces:  NPE QD descriptor,
                behaviour descriptor, cost vector,      Proteus transcript
                yield, novelty-to-observer (kept        class + knockout
                SEPARATE from novelty of structure --   vector, campaign6
                operator, POET/ASAL directive)          detectors
  Transform     perturbations of world or candidate     NPE D3 (relabel
                between episodes: relabel, permute      ids, add edges),
                channels, add irrelevant edges, time-   Proteus grammar,
                warp, corrupt, graft/transfer           NPE Clause B graft
  Selector      population step: MAP-Elites, novelty,   primordial/qd,
                truncation, lexicase, POET-style        archaeon/wse
                admission; archive as data              FOUNDRY
  Control       generators of positive / negative /     NPE B1 cheat
                CHEAT arms for a given experiment       (skip lin_ops must
                (a control is a component, not a       FAIL), O8 planted
                sentence)                              negatives, Clause B
                                                       sham

Why Pressure is a World transformer and not a World: it lets Archaeon
apply DelayedResourceTask to Physics2D AND to CellularWorld AND to
GraphWorld with one object, and it lets the same pressure carry one cheat
control ("a world where the pressure is silently disabled must be
detectable by the pressure's own probe") across every world it wraps.
That is the operator's "what pressure should I apply" as a first-class
degree of freedom.

Why Control is a slot: the base role makes positive+cheat controls
constitutional; today each lane hand-writes them. A control generator
that ships WITH a world or pressure (Box2DWorld.cheat() returns a world
whose physics is replaced by a lookup of the expected trace) makes the
control reusable and testable, and makes "measurement carries its
answer" mechanical.

--------------------------------------------------------------------------
3. THE CONTRACT (v0.1; a merge of primordial/core/contract.py and
   sfe/executors.py, not a third thing)
--------------------------------------------------------------------------

Hot-path rules, inherited from NPE and kept: integer arrays and packed
bytes only; no str/JSON on the tick path; strings live in receipts.
Batched by construction: every World steps n_envs in lock-step.

  World
    n_envs, n_slots, obs_dim, act_dim : int
    reset(seeds: u64[n_envs]) -> obs u16[n_envs, n_slots, obs_dim]
    step(actions: i32[n_envs, n_slots, act_dim])
        -> (obs, charge i32[n_envs, n_slots], done bool[n_envs])
    trace_hashes() -> list[bytes]         # THE oracle
    repro: BIT | SEMANTIC | PARTIAL | NONDET   (SFE's classes, declared)
    quantise(state) -> integer view       # required when repro != BIT
    manifest() -> dict                    # content-addressed identity

  Candidate
    genome: bytes; manifest() -> dict (schema names the substrate)
    act(obs, msg_in) -> (actions, msg_out)
    adapt(signal) -> None                 # plasticity, may be a no-op
    cost() -> {params, flops, state_bytes, ops}   # Success Contract A
    descend(rng, op_id) -> Candidate      # one syntactic operator
    fingerprint(worlds) -> bytes          # substrate-neutral identity

  Pressure
    wrap(world: World) -> World           # returns a World, same ABI
    probe(world) -> bool                  # does the pressure bind here?
    cheat(world) -> World                 # pressure silently disabled;
                                          # probe() must return False
    manifest()

  Observer
    describe(trace) -> f32[k]             # QD descriptor
    measure(trace) -> dict of ints/floats # yield, error, novelty-to-me
    manifest()                            # observer identity is part of
                                          # any "novelty" claim

  Transform
    apply(world | candidate, rng) -> same kind
    inverse() -> Transform | None
    manifest()

  Selector
    step(archive, population, descriptors, fitness, rng) -> archive
    archive is DATA (rows), never process memory (SFE s26 / NPE Redis)
    manifest()

  Control
    positive(experiment) -> experiment    # real signal injected
    negative(experiment) -> experiment    # no signal possible
    cheat(experiment)    -> experiment    # instrument must catch it
    manifest()

  Experiment (the composition Archaeon writes)
    experiment(environment=World, candidate=Candidate | Selector-seeded
               population, pressure=Pressure | [Pressure], observer=
               Observer, controls=[Control], sweep=dict of axes, seeds=
               range, budget=dict, outcome_rule=<preregistered predicate>)
    .compile("sfe")  -> archaeon/frontier spec (validated, capabilities
                        declared) with the outcome rule Vivarium needs
    .compile("npe")  -> NPE bus job(s) with the one-line hypothesis
    .replay(receipt) -> re-execute from manifests+seeds, compare hashes
    never .run()     -- the toolbox does not execute

  Experiment grammar (Archaeon's verbs, defined once)
    sweep(axes)      product over declared axes; every cell a spec;
                     eligibility count computed BEFORE dispatch
    perturb(T, ...)  apply Transform between episodes; paired design
    transfer(c, A->B) candidate evolved in A evaluated in B; ALWAYS with
                     scratch AND sham arms (NPE E-R7-1: the sham beat the
                     graft; "vs scratch alone" would have read PASS)
    replay(receipt)  BIT: hashes equal; SEMANTIC: quantised hashes equal
                     within declared tolerance; else the receipt is
                     downgraded, never the tolerance widened

  Receipt (what every executed spec returns; SFE ExecutorResult +
  NPE receipt merged): manifests of every slot, seeds, repro class
  actually achieved, engineering dict and science dict DISJOINT, rows
  path, controls run, cost vectors, host class, build hashes.

--------------------------------------------------------------------------
4. FILLING THE SLOTS: acquire, chop, or write (the amalgamation plan)
--------------------------------------------------------------------------

Rule: WRITE it ourselves when the reference semantics are integer and
under 500 lines (then it is hashable, BIT-reproducible, and dependency-
free on every host); BIND when the physics is the point and the engine is
the accumulated expertise (Box2D, MuJoCo); CHOP when a fossil contains a
mechanism nobody would re-derive (POET's PATA-EC, Avida's ancestry
records, Go-Explore's cell archive).

  slot / component          route   source                     builder
  ------------------------  ------  -------------------------  ----------
  World.Discrete            wrap    wforge Encounter (frozen)  Ludus/Nestor
  World.Cellular            write   integer CA (numba), Lenia  amalgam
                                    via quantised float
  World.Graph               wrap    NPE B2 GraphBLAS form      Nestor B
                            +chop   Proteus graph substrate    Proteus
  World.ResourceNetwork     write   flow-on-graph, integer     amalgam
  World.Physics2D           bind    Box2D v3 C API via ctypes; Techne
                                    quantised readout,         (acquire)
                                    SEMANTIC                   + builder
  World.Physics3D           bind    MuJoCo CPU (later, if      Techne
                                    asked); MJWarp when stable
  World.TapeSoup            write   BFF (Computational Life)   amalgam
                                    batched numba, the
                                    paper's 40%/16k as the
                                    positive control
  Candidate.TinyVM          wrap    Proteus tape VM            Proteus
  Candidate.GraphProgram    wrap    Proteus graph organism     Proteus
  Candidate.StateMachine    write   Mealy machine over int     amalgam
                                    alphabets, ~150 lines
  Candidate.TensorBrain     wrap    NPE TT / affine plastic    Nestor C
  Candidate.Rewrite         write   string/graph rewrite       amalgam
                                    machine (the "weird
                                    rewrite machine")
  Pressure.Charge/Delay/    wrap    NPE B1 params as wrappers  Nestor B
   RegimeSwitch
  Pressure.MeteredChannel   wrap    NPE lingua                 Nestor D
  Pressure.Budget           wrap    SFE budget classes         Daedalus
  Pressure.PartialObs/      write   mask/noise wrappers        amalgam
   Noise/Adversary
  Observer.QD               wrap    NPE descriptor, pyribs     Nestor E
                                    archive helpers (acquire)
  Observer.Transcript       wrap    Proteus probes/signatures  Proteus
  Transform.*               write   relabel/permute/add-edges  amalgam
                            +chop   Clause B graft/sham        Nestor
  Selector.MAPElites        wrap    primordial/qd; pyribs      Nestor E /
                                    CMA-ME as second impl      Techne
  Selector.POETAdmission    chop    POET minimal-criterion +   Nyx (in
                                    PATA-EC (directive 4)      flight)
  Selector.GoExplore        chop    fossil go-explore cells    Nyx
  Evaluator.numba_fused     wrap    NPE B6 fused kernel        Nestor B
  Evaluator.warp            wrap    NPE N3 kernel; oracle-     Nestor W
                                    gated (R7 GPU failure)
  Evaluator.llvm_genome     write   llvmlite JIT of TinyVM     builder
                                    genomes; an EXPERIMENT     (later)
  Control.*                 write   per slot, shipped with it  each

Acquisitions this implies for Techne (as executable fossil packets, NOT
a new harvest census; each is one body with a demo command): Box2D v3
source (MIT), MuJoCo (Apache-2.0) later, BFF reference implementation,
pyribs (MIT), python-graphblas (Apache-2.0), NVIDIA Warp (Apache-2.0 from
1.0), llvmlite (BSD). Dissections this implies for Nyx: POET admission
boundary and PATA-EC (already directed), Go-Explore cell archive, Avida
ancestry record (already directed), BFF's copy-head mechanism. Both lists
are DRAFTED, not posted: operator directive 4 (2026-09-18) told Techne and
Nyx to stop broadening until ten mechanisms have verdicts, and this seat
does not override that. Drafts: prompts/2026-09-18_drafts_not_posted/.

--------------------------------------------------------------------------
5. ADMISSION (what turns a body into a component)
--------------------------------------------------------------------------

A component is ADMITTED to a slot when the following are committed beside
it and pass on the merged tree:
  1. contract conformance test (runtime_checkable Protocol + a 20-line
     behavioural test: reset/step shapes, dtype, done semantics)
  2. ORACLE: agreement with the slot reference on a published episode
     sample (trace hash for BIT; quantised hash within declared tolerance
     for SEMANTIC); a NEW world class publishes its own reference and
     becomes the oracle for later implementations of itself
  3. controls: positive, negative, CHEAT (the skip-the-mechanics
     implementation must FAIL the oracle; the disabled-pressure world
     must fail probe())
  4. throughput row: steps/s vs n_envs on each host class, dated, with
     library versions (NPE B1 table is the format)
  5. provenance: fossil id / organ id / author; license SPDX; native
     deps; host class; build recipe (Techne's packet fields verbatim)
  6. adapters: one SFE Executor kind, one NPE job kind (each one file);
     the same receipt schema from both
  7. a registry row: slot, name, manifest hash, reference-or-not, repro
     class, state (ADMITTED / PROVISIONAL / RETIRED), dormancy per base
     rule 7 if it has a loop

Admission is a deterministic predicate over committed files -- no seat
"approves" a component; the operator or Harmonia adjudicates only claims
ABOUT components (e.g. "Box2DWorld changes what R16 screens find").

--------------------------------------------------------------------------
6. WHAT THE TOOLBOX IS NOT
--------------------------------------------------------------------------

- Not a reasoner and not a ladder: no slot names a cognitive function
  (Proteus's frozen/evolvable principle, generalised).
- Not an executor: compile() emits specs; Vivarium and the NPE lanes run.
- Not an adjudicator: it carries controls and oracles; verdicts are
  Harmonia's and the operator's.
- Not a monoculture: two implementations per slot is the target state
  (numba + Warp; wforge + GraphBLAS; MAP-Elites + CMA-ME), because an
  ecosystem whose only evaluator is one kernel has an instrument-
  monoculture blind spot (Harmonia D, 2026-06-22).
- Not RL: no reward channel in the World contract; yield is a Pressure's
  economy and an Observer's measure.

--------------------------------------------------------------------------
7. WHAT WOULD FALSIFY THE DESIGN (written so it can lose)
--------------------------------------------------------------------------

  F1  One Experiment object cannot compile to BOTH a frontier spec and an
      NPE bus job without per-ecosystem rewriting of the experiment.
      Test: BELL-14 compiles the same CA-world sweep to both; if the two
      specs differ in anything but transport, F1 holds and this is two
      toolboxes.
  F2  Pressure-as-transformer loses semantics: a pressure wrapped over
      two different worlds fails its own probe() on one of them for
      reasons that are not "does not bind here". Test: BELL-16.
  F3  Admission cost exceeds building cost: if admitting Box2D takes
      longer than writing an integer 2D physics toy that answers the
      same questions, the bind route is wrong for this program.
  F4  No admitted component changes what an R16-style world screen can
      find (the one-survivor result stays one survivor across the new
      world classes). Then worlds-as-machinery is not the bottleneck.

--------------------------------------------------------------------------
8. DECISIONS THE OPERATOR HOLDS (XL rows in the backlog)
--------------------------------------------------------------------------

  D-BELL-1  package location and name (prometheus/toolbox/ at repo root
            is the proposal; `prometheus` as a top-level package name
            collides with nothing on the tree today)
  D-BELL-2  NPE on main: adapters/npe cannot import primordial/ from a
            main worktree while NPE lives only on Nestor's branch. Either
            NPE lands on main (Nestor's call) or the NPE adapter is built
            on Nestor's branch and the toolbox package is merged into
            both. Recommendation: ask Nestor to land primordial/ on main
            as-is (it is already 1,093 files of receipts).
  D-BELL-3  native builds host: gcc in WSL on M2, or the coming Linux
            host, for Box2D/Warp. Recommendation: WSL on M2 now, one
            apt line, recorded.
  D-BELL-4  whether Bellerophon may post the drafted acquisition/chop
            lists to Techne/Nyx now, or after directive 4's ten-verdict
            bar. Recommendation: after; the CA/BFF/state-machine slots
            need no acquisition and are enough for the first admission
            cycle.

--------------------------------------------------------------------------
9. THE FIRST ADMISSION CYCLE (what "shaped enough to build" looks like)
--------------------------------------------------------------------------

  0  freeze contracts v0.1 as code (contracts/*.py with Protocols and
     schema JSON) + ABI diff vs primordial/wforge/proteus/sfe (BELL-04)
  1  registry + admission test harness + receipt schema (BELL-10..12)
  2  three home-written components through admission on M1 and M2:
     World.Cellular, Candidate.StateMachine, Pressure.Delay-as-wrapper
     over wforge (BELL-05, -13, -16)
  3  experiments.sweep compiled to a frontier spec AND an NPE job for
     the same CA sweep (BELL-14, the F1 test)
  4  World.TapeSoup (BFF) with the emergence-rate control (BELL-06)
  5  first bound engine: Box2D v3 (BELL-07) -- after D-BELL-3
  6  Archaeon writes one experiment against the toolbox without reading
     any implementation; the receipt is the milestone (BELL-20)
