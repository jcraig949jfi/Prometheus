+==============================================================================+
|  AETHER -- EXTERNAL REVIEW PACKET                                            |
|  Artificial-physics substrate, AETH-02 closure, AETH-03 physics ladders      |
|  1-2, and the RunPod GPU platform (Iterations 2-4)                           |
|                                                                              |
|  Author : Aether seat (Claude Opus 5.5), host BUCKKEEP (i7-1260P laptop)     |
|  Date   : 2026-09-27 (work dated 2026-09-24 .. 2026-09-26)                   |
|  For    : the operator (HITL) and external reviewers                         |
|  Status : all runs finished; nothing in flight; no GPU pods active           |
|  Context: the operator is weighing Aether -- its research question and its  |
|           tooling -- as the next test bed for Prometheus campaigns,          |
|           experiments and task queues. Section 8 is written for that.       |
|                                                                              |
|  Self-contained: every load-bearing number is inline. No repo access is     |
|  needed. Artifact paths and commit SHAs are in section 11 for anyone who    |
|  wants to verify.                                                            |
+==============================================================================+

-----------------------------------------------------------------------------
0. SUMMARY AND VERDICT UP FRONT
-----------------------------------------------------------------------------

Aether is a synthetic computational lattice: a 2-D torus of sites, each
holding five bytes (opcode, arg0, arg1, payload, energy), updated by a
deterministic, exact-integer, hash-keyed local law. The baseline law is
called aeth01.v1. The research question is whether primitive local physics
can support anything with "room to compute" -- endogenous change, persistent
causal structure, history that matters -- without an architecture being
built in. Nothing here involves biology; biological words are banned from
the active surface by a linter.

Three lines of work are reported, kept separate on purpose:

  (A) SCIENCE, closing AETH-02 on aeth01.v1 ($0.00, CPU).
      Both open questions are closed. The "edges live 3x shorter than
      independence predicts" gap was a defect in the null model (it had no
      energy term; energy starvation ends 89% of edges). The cycle deficit
      (realized cycles 0.37x a matched random graph) is real at 512^2 and
      is carried almost entirely by two fields, each with a mechanism read
      off the law and tested.

  (B) SCIENCE, AETH-03 physics design ($0.00, CPU).
      Nine one-change variants of the law were scouted in two ladders.
      Ladder 1 (persistence): 4 killed, 1 unresolved and mostly trivial.
      The finding that reframed the work: under v1 and every variant, a
      one-bit difference stays within ~1 site for 500 ticks. The substrate
      lacks PROPAGATION, not only memory.
      Ladder 2 (propagation, with an exact causal-generation assay): only
      one law, rcv ("a written site fires once"), propagates a difference
      over multiple generations with injected noise off -- weakly (6 of 128
      origins), and what travels is activation timing along the law's own
      relay, not content. No candidate earned GPU scale-up.

  (C) INFRASTRUCTURE, the RunPod GPU platform ($0.84 of a $5.00 ladder).
      Iterations 2-4 passed. Measured provisioning, ~5% overhead on real
      workloads, sha256-verified artifacts, one-command scout -> calibrated
      estimate -> campaign, a 65-minute soak that withstood a hard controller
      kill and resumed without a second create, 13 injected failure modes
      with honest dispositions, and 3 concurrent pods with one shard
      designed to fail and isolated. Real flights found five platform
      defects, all fixed with tests.

VERDICT (Aether's lean; the operator decides, section 9):
  - The SCIENCE has produced clean, honestly-scoped negatives and one weak,
    mechanistically explained positive. It has not produced anything that
    justifies GPU money yet. "The substrate lacks propagation" is the most
    useful result of the week.
  - The TOOLING (preregistration discipline, CPU scouts, exact twin assays,
    reducers that apply thresholds verbatim, a GPU platform with receipts)
    is in good shape and is the stronger argument for using Aether as a
    test bed. The science question is a good *driver* for that test bed
    because it produces many small, independent, reproducible jobs with
    preregistered pass/fail rules.
  - "Stop the science and keep only the platform" is a live option and is
    argued for in section 9.

-----------------------------------------------------------------------------
1. THE SUBSTRATE, IN ENOUGH DETAIL TO JUDGE THE RESULTS
-----------------------------------------------------------------------------

Lattice: H x W torus, 5 uint8 fields per site. One tick, synchronous:

  1. A site is ACTIVE if opcode == 0x01 (WRITE) and energy >= WRITE_COST.
     Every other opcode byte is inert.
  2. Each active site emits exactly ONE proposal: to the von Neumann
     neighbour chosen by arg0 mod 4, into the field chosen by arg1 mod 5.
     Fields 0-3 receive the source's payload byte (a copy). Field 4
     (energy) receives a transfer of min(payload, energy - WRITE_COST).
  3. Contests (several proposals into one site-field) are decided by a
     SplitMix64 hash of (seed, tick, target, field, source). The tick is in
     the hash, so contests are re-decided afresh every tick.
  4. The winner's value is stored. Then "Mu" (perturbation): with
     probability 0.1, a hash-keyed single bit of the stored value flips.
     Mu fires only on winning writes into fields 0-3, never on energy,
     never on untouched bytes.
  5. Energy: every emitter pays WRITE_COST (1); transfer sources pay the
     amount win or lose; winners' targets are credited (saturating at 255).
  6. Maintenance: -1 per tick, floored at 0.
  7. Replenishment: +8 with probability 1/8 per site per tick.

Consequences used below:
  - An active emitter drifts -1 energy/tick (pays 2, gains 1 on average),
    so without inflow it runs dry. An inert site's energy is a zero-drift
    walk.
  - A write REPLACES the target byte with the source's payload; nothing in
    the law ever combines two values.
  - arg1 mod 5: every single-bit change of arg1 changes its value mod 5
    (no power of two is divisible by 5). This "K2 property" was proven
    during the law's own qualification and turns out to matter (section 3).

Engineering properties (inherited, verified in earlier rounds, not
re-litigated here): exact-integer everywhere, deterministic replay, an
independent CPU oracle differential-tested against a GPU-shaped kernel, the
GPU kernel run bit-exact on real A40 hardware, 16384^2 (268M sites) fits on
one A40. Full test suite at the time of writing: 1,342 passed, 5 skipped
(the 5 are Linux-only pod-side gates, unmeasured on this Windows host, not
passed).

Prior science, one line each (inherited):
  - AETH-01 first light: six 4096^2 worlds, 30,000 world-ticks, no
    endogenous organization observed.
  - AETH-02 trajectory round (GPU, $2.83 of $3.00): persistent edges exist
    but are uncontested residue; 92% of sites make no net template change
    over 64 ticks; perturbation supplies ~42% of template change at once
    and ~95% within 500 ticks. Conclusion, at the width the operator set:
    no evidence that the measured structures perform a demonstrated
    nontrivial function under the assays run -- NOT "Aether cannot contain
    circuitry".

-----------------------------------------------------------------------------
2. HOW THE WORK WAS RUN (the discipline a reviewer should check)
-----------------------------------------------------------------------------

  - Every test's predictions and pass/fail thresholds were written into a
    committed file BEFORE the run at the reported size; commit timestamps
    are the preregistration record. Tests added after seeing data are
    labelled POST HOC wherever they appear.
  - Every threshold is applied by a reducer script that copies the numbers
    from the design document verbatim, so a verdict cannot drift from its
    preregistration without a visible document change.
  - Every new kernel variant runs on a shared code path that is asserted
    BIT-IDENTICAL to the frozen aeth01.v1 reference (observer outputs
    included) before any variant is layered on it.
  - Instruments carry their own controls: a null twin that must never
    differ; a hand-built relay chain that must count hops exactly; a
    detection control that must flag an undeclared causal radius.
  - aeth01.v1 is never modified. Every variant has its own semantics id.
  - Cost of all science in this packet: $0.00 (CPU on a laptop).

-----------------------------------------------------------------------------
3. AETH-02 CLOSURE (aeth01.v1, CPU)
-----------------------------------------------------------------------------

Runs: 512^2 x 2 seeds (2,500 warmup, 600 follow); 256^2 x 1 seed; and
256^2 with a 10,000-tick warmup as a stationarity control. The control
reproduced every number below (e.g. long-edge fraction 0.0713 vs 0.0705,
cycle deficit 0.360 vs 0.368), so nothing is a relic of the initial state.

3.1 H2 -- the edge-lifetime gap. CLOSED.

  The 09-24 null predicted 22% of edges would last >= 64 ticks; 7% did
  (3.1x over-prediction).

  512^2, opcode field, seed 0 / seed 1:
    observed P(run >= 64)                      0.0695 / 0.0726
    old null (all-site change rates, no energy) 0.226 / 0.229   (3.25x / 3.15x)
    measured per-tick edge hazard               0.128 / 0.127
      of which: the source ran out of energy    0.113 / 0.113   (89%)
    conditioned null, energy as i.i.d. walk     0.0103 / 0.0118 (0.15x / 0.16x)
    life-table self-check (instrument)          0.088 / 0.092

  Reading:
  - Preregistered H2-P1 CONFIRMED: the old null had no energy term, and
    starvation ends 89% of edges. The age profile shows why: starvation
    hazard spikes to 0.57 at exactly age 4 -- a starved emitter gets one
    replenishment of 8, pays 2 per tick, and burns out in four ticks.
  - Preregistered H2-P2 FAILED, in the informative direction: with energy
    added as an independent walk, the null now UNDER-predicts long edges
    6-7x. Real long edges outlast independent energy.
  - The law explains the residual: an active emitter with no inflow drifts
    -1/tick and energy caps at 255, so an edge older than ~255 ticks is
    impossible without net inflow. 65% of the >= 64-tick cohort was older
    than 255 ticks (654/1000 and 647/1018 sampled); those sources were fed
    by a neighbour's energy transfer in ~15% of recent ticks vs 1.3% for
    all sites.
  - Intervention 1 (post hoc): cut the feeders once. FALSIFIED at its own
    bar (effect 0.045 and 0.030 < 0.05). A one-shot cut reaches only the
    ~15% of sources fed at that instant.
  - Intervention 2 (post hoc, committed before running): remove inflow
    every tick; the sham re-aims the same number of emitters on the same
    ticks elsewhere. NOT FALSIFIED. Persistence of sampled long edges at
    +128 ticks: cut 0.273 / 0.285 vs sham 0.703 / 0.718 (ratio 0.39 / 0.40,
    bar was <= 0.5). Sham indistinguishable from no lesion.
  - Conclusion: long-edge persistence is energy supply from neighbouring
    emitters. A resource-transfer mechanism, not a structure-forming one.

3.2 H3 -- the cycle deficit. CLOSED as a question.

  512^2, 2 seeds, 48 samples, 37,042 cycle nodes (the 09-24 test had 205
  on-cycle edges and was underpowered). Two nulls: A rewires each source to
  a random neighbour; B shuffles arg0 among active emitters and runs the
  real kernel.

                         real    null A    null B   real/A
    cycle nodes/sample   ~772    ~2,044    ~2,046   0.37-0.38
    cycle edges, opcode     57   18,803    18,938   0.003
    cycle edges, arg0    8,503   22,183    22,003   0.383
    cycle edges, arg1       36   22,578    22,703   0.002
    cycle edges, payload 14,056  25,418    25,348   0.553
    cycle edges, energy  14,390   9,114     9,200   1.579  (ENRICHED)

  Nearly all cycles are 2-cycles (18,493 vs 14 four-cycles).

  - P1 (deficit is real, not noise) CONFIRMED; both nulls agree to three
    decimals.
  - P2 (deficit in opcode and arg0; arg1/payload/energy near 1) PARTLY
    FALSIFIED: right about opcode and arg0, wrong about arg1 (the most
    suppressed field), payload, and energy (enriched).
  - Mechanisms. A cycle member is overwritten by its predecessor EVERY
    tick.
      opcode: the write stores the predecessor's payload into the member's
        opcode, switching it off unless payload == WRITE. Deterministic:
        in a relaxation probe opcode cycle edges collapse 390 -> 15 within
        10 ticks, the same with perturbation off.
      arg1: the write sets the member's own field selector; every Mu flip
        of it changes the field (K2), so the member keeps re-picking which
        field it writes until it hits a destructive one. Test (post hoc,
        committed before running): arg1 cycle edges retain 0.40 of their
        count to +100 with perturbation OFF vs 0.095 ON (4.2x). NOT
        FALSIFIED.
      energy: 2-cycles of mutual energy transfer supply each other -- the
        same mechanism that powers H2's long edges.
  - P3 FALSIFIED: at a fixed written field, cycle members keep their
    out-edge LESS often than off-cycle writers (by 0.07-0.29 per tick).
    Cause NOT established.
  - P4 CONFIRMED: a direction-shuffled state starts at the null level
    (2,055 cycle nodes) and relaxes to the realized level (751 vs 793) in
    ~60 ticks.
  - Correction to the 09-24 report: its "state-changing edges are 1.97x
    enriched on cycles" was mostly field composition (Simpson's paradox):
    38% of on-cycle edges are energy edges, which change state 87% of the
    time anyway. Within a field the lift is 1.2-1.6x.

3.3 H1/H4 replicated on two more seeds.
  H1 (lesioned persistent edges are not repaired): recurrence <= 0.005 on
  all three seeds. H4 (perturbation off removes ~41% of template change at
  once, ~94% by +500): 0.411 / 0.437 / 0.425 and 0.945 / 0.944 / 0.937,
  energy change unaffected to 0.000000.

-----------------------------------------------------------------------------
4. AETH-03 LADDER 1 -- one-change laws for persistence (CPU)
-----------------------------------------------------------------------------

Five variants, each changing exactly one phase of the tick, no added state:
  add  a write stores (old + payload) mod 256 instead of payload
  hys  in a contest, a proposal equal to the target's current value wins
  chg  an emitter pays WRITE_COST only if its write would change the target
  cnd  a second opcode 0x02 writes only if the target's low 2 bits match a key
  str  direction = (arg0 + energy/64) mod 4 (energy steers aim)

Battery (identical for all, 128^2, 2 seeds): viability; template change
retained with perturbation OFF; twin divergence from 16 single-bit flips;
edge-set overlap across lags; contest-winner persistence. Kill and justify
thresholds were relative to v1 in the same battery, committed first.

                                   v1     add    hys    chg    cnd    str
  frozen fraction (64 ticks)     0.927  0.696  0.927  0.922  0.961  0.940
  change retained, pert off     0.064  0.998  0.026  0.062  0.048  0.056
  twin footprint/origin +500    0.72   1.19   0.72   0.69   0.50   0.56
  twin reach +500 (sites)          1      2    1.5      2      1      1
  edge overlap lag 100           0.36   0.33   0.36   0.86   0.34   0.33
  verdict                          -   UNRES  KILL   KILL   KILL   KILL

  - hys and chg failed exactly as their preregistered risks said (hys went
    sticky and more static; chg crystallised the graph: overlap 0.86).
  - add kept ~all of its change without perturbation, but a post hoc check
    found 83% of that change is constant-step counting and 86% comes from
    the same source as the previous tick. Counting, not history.
  - Cross-cutting: in ALL six laws a one-bit difference stayed within ~1
    site for 500 ticks, with or without perturbation (never more than
    0.22% of the lattice). This reframed the next round.

-----------------------------------------------------------------------------
5. AETH-03 LADDER 2 -- can a local difference propagate? (CPU)
-----------------------------------------------------------------------------

5.1 The assay (built this round; the part most worth reviewing)

  Two worlds, identical except for ONE BIT at one origin site. Same law,
  same seed, same hash-keyed perturbation stream, so any difference is
  caused by the flipped bit. Arms: perturbation OFF (primary) and ON.

  Because every law is strictly local (radius 1; one law radius 2, see
  below) and the noise stream is shared, a site with no differing
  neighbour cannot come to differ. So every newly differing site has a
  differing parent, and

      generation = 1 + min(generation of differing parents last tick)

  is the exact shortest causal chain from the origin -- not inferred. The
  assay checks the parent condition every tick; any violation voids the
  run. Classes: generation 1 = DIRECT mechanical spread; generation >= 2 =
  SECONDARY; SUSTAINED = generation >= 5 AND radius >= 5 AND still adding
  generations after tick 50.

  Controls (tests, all pass): null twin never differs; a 21-emitter relay
  chain gives generation k at hop k exactly; and for the radius-2 law, a
  hand-built case where the only cause is two sites away is correctly
  flagged as a violation when searched at radius 1.

5.2 Laws (as defined in the previous design doc, two deviations stated)

  mov  a winning source's payload is cleared: bytes move instead of copy.
       Causal radius is 2 (whether it won depends on the target's other
       neighbours) -- the assay was built to handle it.
  rcv  a site that received a winning write last tick fires this tick even
       if inert. DEVIATION: this needs one bit of per-site state, although
       the plan said "no added state". Implemented as defined, stated.
  m4   field selector = (arg1 >> 3) mod 5 (low-bit flips neutral).
       DEVIATION from the plan's example "mod 8 folded onto 5", which would
       double-weight three fields.
  add  carried as a control from ladder 1.

5.3 Results. 128^2, 4 seeds x 32 origins x 2 arms per law = 1,280 twin
pairs; 0 locality violations; full-size null self-test clean.

  Perturbation OFF, 128 origins per law:
                                   v1     add    mov    rcv    m4
  escape (radius >= 3)            .008   .062   .000   .203   .008
  secondary (gen >= 2)            .078   .242   .008   .406   .047
  SUSTAINED                       .000   .008   .000   .047   .000
  gen-1 share of new differences  .732   .898   .989   .399   .615
  max generation / max radius     56/3    6/5    2/2   12/11   3/3
  branch points                     18     32      4    448     55
  sustained per seed (0/1/2/3)       0  0/0/.03/0   0  0/.09/.03/.06  0

  Perturbation ON: rcv sustained 0.227 (4.8x its OFF rate), radius to 17;
  all others stay local.

  Verdicts by the preregistered thresholds:
    mov  KILLED (local; 99% direct; 41% of differences simply die because
         the differing byte moves on and the source is zeroed in both worlds)
    m4   KILLED (local)
    add  CLOSED (narrowly escaped two kill clauses by 0.012 and 0.002;
         median radius 1; closed under the operator's standing instruction
         that a local footprint closes it)
    rcv  UNRESOLVED: depth passes (median generation 10.5 among sustained
         origins) but frequency (0.047 < 0.10) and every-seed replication
         (seed 0 had none) fail.

  A caution v1 supplied: v1 reaches generation 56 WITHOUT leaving radius 3.
  A difference that heals and reappears between neighbours piles up
  generations in place. Generation depth alone is not reach; the SUSTAINED
  class needs radius too.

5.4 rcv attacked anyway (the operator's instruction for a weak real signal)

  Ring of sites at Manhattan radius 5-6 around the origin, re-applied every
  tick in both worlds; sham = same ring shape placed elsewhere; outcome =
  divergence reaching radius >= 8. 4 seeds x 32 origins, perturbation ON
  (the OFF arm reaches radius 8 only 3.1% of the time -- underpowered).

  Full ring starved:       0/128 cross vs sham 17/128.
    FORCED BY THE LAW, not evidence: influence travels only by emission and
    a zero-energy site cannot emit, so a starved closed ring blocks
    everything by construction. Recorded as a design error (section 7).
  Only INERT ring sites starved (WRITE emitters in the ring still powered):
                           0/128 cross vs sham 17/128  (100% reduction)
  Only WRITE ring sites starved (inert sites still powered):
                          13/128 cross vs sham 17/128  (24% reduction)
  Prediction (written before running): inert >= 50%, writers < 50%.
  NOT FALSIFIED. Spread up to the ring is unchanged in every arm (28-34 vs
  32 origins reaching radius 5).

  Mechanism probe (post hoc, descriptive): 42% of all active sites under
  rcv are active only because they were written. 80% of secondary
  differences land in inert sites; of 359 secondary differences, 269 are
  the received flag, 75 energy, 30 template bytes (8%), 0 opcode.

  Reading: rcv propagates ACTIVATION TIMING -- an extra or missing firing
  -- along its own "written -> fire once" relay through inert matter. A
  WRITE emitter re-sends its own payload whatever it received, so it
  passes a difference only if the difference lands in its own bytes; an
  inert relay fires BECAUSE it was written. What travels is not content,
  and nothing composes on the way. Perturbation amplifies it 4.8x
  (reasoned, not measured: a write that happens in only one world gets a
  bit flipped only there, turning timing differences into topology
  differences).

-----------------------------------------------------------------------------
6. RUNPOD GPU PLATFORM, ITERATIONS 2-4 (infrastructure, not science)
-----------------------------------------------------------------------------

Purpose: a reusable, cost-bounded, self-auditing way for any Prometheus
seat to fly GPU work. Campaign ceiling $5.00; spent $0.8446 (wall time x
quoted rates; not reconciled with provider billing). After every real
flight, an independent inventory read showed 0 active pods.

Iteration 2 ($0.0815, 6 flights, 2 of them refused for capacity at $0):
  - Provisioning MEASURED: a pod is up 2.1-22 s after create. Most of what
    Iteration 1 had bounded as "24 s provisioning" was the provider's proxy
    returning 404 for 20-33 s after the pod was already running.
  - Overhead 97% -> ~5% of wall time on 6-10 minute workloads; 96% GPU
    utilisation; 8 MiB artifacts at ~5 MB/s, sha256 verified end to end.
  - First real scout: scout-calibrated estimate 5.9% high vs actual; the
    spec-sheet estimate was 37% LOW (the L4 delivered 35% of its FP32 spec).

Iteration 3 ($0.5821): long-run reliability and failure injection.
  - 3,900 s soak on an RTX A5000. Controller killed with os._exit at
    +1,500 s; a new process resumed from the ledger 123 s later, confirmed
    the pod by name, created nothing, retrieved and verified all artifacts,
    terminated, and confirmed absence by LIST and GET.
  - 11 of 12 preregistered drift checks held: device memory flat and free
    memory byte-identical; throughput drift 0.06%; p99/p50 latency <= 1.02;
    no telemetry gap > 10.3 s including across the controller gap; 685
    fetches, 0 failures; clock drift 0.027 s; spend and receipt agree to
    0.08%. The host-memory prediction FAILED as written (+16.7%: a bounded
    step at the first two checkpoints, flat for the last 2,690 s) and is
    recorded as failed, not rewritten.
  - All 13 directive failure modes (nonzero exit, hang, timeout, artifact
    server gone, corruption, telemetry stall, controller restart, create
    response lost, LIST omission, GET/LIST disagreement, transient DELETE
    failure, ambiguous response, partial retrieval) are tests against a
    fake provider (52 tests); exit, hang and server loss also flown for
    real. Every receipt now carries a "disposition" block: what the
    controller believes, what the provider believes, what evidence
    remained, can it resume, is cleanup safe, uncertainty vs absence.
  - Five real defects found by real flights, each fixed with a test:
      1. killing the container's main process makes RunPod RESTART the
         container and re-run the module while the controller sees a normal
         run (now guarded; CONTAINER_RESTARTED is an outcome);
      2. the pod clock was queried once; now re-measured until it answers;
      3. a transient Windows file lock on the ledger aborted a healthy run;
      4. the error path skipped artifact retrieval before terminating;
      5. platform samples lived only on the pod and died with its server.
  - One-command scout -> calibrate -> campaign, with automatic re-scout when
    the pinned card is refused. Receipts carry spec-sheet, scout-calibrated
    and actual cost with both errors; latest: scout +1.5%, spec -4.3%.

Iteration 4 ($0.0570): 3 concurrent pods (A5000 / 4090 / L4), shard c
designed to exit at 60 s. Result PARTIAL as designed: a and b completed with
verified artifacts (both within 0.4% of 240 s), c isolated, three distinct
pods, per-pod cost and cleanup evidence. The concurrent creates hit real
HTTP 500s; each was reconciled by pod name before any retry, and no shard
adopted a sibling's pod.

Open, stated in receipts: a pod whose create response is lost AND that
every listing omits cannot be ruled out; a restart that loses the pod disk
is not covered; capacity refusal is still inferred (the client discards
400 bodies); cost bounds must be priced for every declared card.

-----------------------------------------------------------------------------
7. WHAT THIS DOES AND DOES NOT ESTABLISH; DEFECTS AND PROCESS HOLES
-----------------------------------------------------------------------------

Establishes:
  - For B-balanced aeth01.v1: edge persistence is energy supply; the cycle
    deficit is two field mechanisms; the edge structure is otherwise
    independence.
  - For nine single-change laws at 128^2, 400-500 ticks: none gives
    persistent, propagating, content-carrying causal structure. One (rcv)
    gives weak propagation of activation timing via its own relay.
  - A GPU platform that has come through its own failure-injection programme
    and a long flight with a hard controller kill, at under $1.

Does NOT establish:
  - That no local law can propagate content. Nine laws and one parameter
    regime is a small corner.
  - Anything about scale: every propagation number is 128^2 and <= 500
    ticks. A slow process at 4096^2 over 10^5 ticks is untested.
  - That rcv's effect would hold in another parameter regime; nothing was
    tuned, and nothing was varied either.
  - Any billing truth: platform dollars are wall-time x quoted rate.

Defects and holes, recorded rather than smoothed:
  - A preregistered intervention (full-ring starvation) was forced by the
    law and could not have come out otherwise. The same trap (a clamp
    "firewall") had been recognised and rejected earlier the same day and
    was not recognised in its second form. Ledgered.
  - A preregistered prediction (H3-P2) ignored the perturbation channel,
    even though the seat's own qualification had proven the property that
    drives the arg1 result. Ledgered.
  - The rcv law needs one bit of state the plan said it would not add.
  - One preregistered measurement (cnd's opcode share) was left out of the
    scout battery; recovered by deterministic replay, not by editing the
    battery afterwards.
  - The first sham of a sustained intervention made 17x more lesions than
    the treatment (matched its own hit count, not the treatment's). Caught
    by the smoke run before any real run.
  - During an integration merge a stray checkout detached the worktree
    while the test suite was starting; caught, rerun, nothing pushed from
    the wrong tree. Ledgered.
  - BUCKKEEP is a throttling laptop; >3 concurrent 512^2 jobs thrash cache
    and slow every job ~10x. One 512^2 seed was dropped for that reason.
  - Every science dollar figure is $0.00 because everything ran on CPU;
    nothing here has been checked at GPU scale.

-----------------------------------------------------------------------------
8. AETHER AS THE NEXT TEST BED FOR CAMPAIGNS, EXPERIMENTS AND TASK QUEUES
-----------------------------------------------------------------------------

Why the Aether question fits the job:
  - The work unit is naturally small, independent and replayable: (law,
    seed, origin batch, arm) -> one JSON result. Exact-integer determinism
    means any unit can be rerun bit-for-bit anywhere, which makes retries,
    duplicate detection and result verification checkable rather than
    trusted.
  - Every campaign already has the shape a queue needs: a preregistered
    design document, a battery of units, a reducer that applies committed
    thresholds, and a verdict that can be KILLED / UNRESOLVED / EARNS.
  - Negative results are the common case and are valuable. A queue that
    handles "null, reported honestly" as a normal outcome is the right test.
  - It spans both tiers: most units are CPU seconds-to-minutes; a few
    earned units become GPU scouts, and the platform already runs
    scout -> calibrated estimate -> campaign.

What the test bed would exercise (suggested acceptance items):
  1. A campaign spec: design doc + thresholds + unit list, hashed; the
     queue refuses to run units whose spec hash is not committed.
  2. Units as queue items with ownership, leases and idempotent results
     (a unit's output name is a function of its inputs; a rerun that
     disagrees is a determinism alarm, not an overwrite).
  3. Mixed CPU/GPU placement with the calibrated cost estimate as the
     admission rule, and per-unit spend in the receipt.
  4. Partial failure: a crashed unit is retried or marked, never silently
     dropped; the reducer refuses to issue a verdict on a battery with
     missing units (it can report "incomplete").
  5. Dormancy and productivity signals (Prometheus base rules 7-10): every
     worker loop declares a bound on non-productive ticks and a seat to
     notify when it parks.
  6. Contention-aware scheduling: this week's runs measured that too many
     concurrent 512^2 jobs slow each other ~10x on one host. A scheduler
     that knows the unit's memory footprint would have avoided that.

Candidate science to drive it (each small, each preregisterable):
  a. fwd -- a receipt-activated site emits what it RECEIVED instead of its
     own payload. The one-change test of "can content ride a relay?",
     baseline rcv. Risk to check first: it may directly encode a message
     path; its first falsifier is whether forwarded content is ever
     transformed or composed rather than only relayed.
  b. rcv replication across parameter regimes (write cost, replenishment,
     perturbation rate) -- the obvious fan-out campaign; many CPU units.
  c. m4's original question, never asked: without the K2 channel, do
     arg1-mediated cycles persist?
  d. A scale probe: does rcv's weak propagation change character at 512^2
     and 10^4 ticks? The first thing that would justify a GPU scout.
  e. RunPod Iteration 5: fly a module from another seat -- the direct test
     of whether the platform is reusable, not just usable by its author.

-----------------------------------------------------------------------------
9. THE DECISION (the operator's call) AND AETHER'S LEAN
-----------------------------------------------------------------------------

Options:
  (1) Keep both: Aether science as the driver workload for a campaign/queue
      test bed; platform continues to Iteration 5.
  (2) Platform only: stop the physics search; use Aether's existing
      laws and assays as a FIXED, well-understood benchmark workload for
      the queue and campaign machinery.
  (3) Science only: pause platform work at Iteration 4 (it already passes)
      and spend effort on the next physics ladder.
  (4) Stop Aether: record the results and redirect.

Aether's lean: (1), with a guard. The science question is now sharp
("can content propagate under a primitive local law?") and each rung costs
only CPU; that makes it a good, honest driver for a queue whose correctness
is itself under test. The guard: if fwd and one more ladder produce no
content propagation, (2) becomes the better choice -- keep the assays and
laws as a benchmark and stop searching.

Arguments for (2) or (4), stated at full strength:
  - Nine laws, zero content propagation. The search space is enormous and
    the prior that a lattice of copying bytes yields anything worth calling
    computation is low. The best-supported "positive" of the week is the
    law's own relay doing what it says.
  - The tooling is the durable asset; the science may be decoration for it.
  - A test bed does not need an open research question; a fixed workload
    with known answers may test a queue BETTER, because every result can
    be checked against a reference.

-----------------------------------------------------------------------------
10. QUESTIONS FOR THE REVIEWER (written to resist agreement)
-----------------------------------------------------------------------------

  Q1. Is the exact-generation argument actually sound? It rests on strict
      locality and an identical noise stream. Is there any path by which a
      site could differ without a differing neighbour that the assay would
      miss (e.g. through the arbitration hash, replenishment, or rcv's
      flag)? The detection control proves the assay can catch one such
      case; it does not prove there are no others.
  Q2. Is "activation timing propagates" a finding, or is it simply the
      definition of rcv restated? If the latter, rcv should be recorded as
      KILLED under "the rule directly encodes the communication it
      produces", not UNRESOLVED.
  Q3. Were the kill/justify thresholds strict enough, or so strict that
      nothing could pass? No law has passed a justify gate in two rounds.
      Is that the physics, or the bar?
  Q4. Is 128^2 x 400-500 ticks a fair test of propagation, or does it bias
      toward "local" for any process slower than ~1 site per 50 ticks?
  Q5. The H2 closure leans on a post hoc second intervention after the
      first was falsified. Is that a legitimate refinement (the first was
      underpowered by construction) or a forking path?
  Q6. The one-change-per-arm rule forbids combinations until each part is
      understood. Could that rule itself hide the only interesting region
      (effects that exist only in combination)?
  Q7. Is Aether a good queue/campaign test bed precisely BECAUSE its
      science is open, or would a closed benchmark with known answers be a
      stronger test of the machinery?
  Q8. The platform's spend figures are never reconciled with provider
      billing. Before any multi-hour campaign, should reconciliation be a
      hard gate?
  Q9. Should Aether stop? "Not worth continuing" is a first-class answer
      here, for the science, the platform, or both.

-----------------------------------------------------------------------------
11. ARTIFACTS (all on origin/main unless noted)
-----------------------------------------------------------------------------

Reports:
  Aether/AETH-03/PHYSICS_DESIGN_01_2026-09-26.md   AETH-02 closure + ladder 1
  Aether/AETH-03/PHYSICS_DESIGN_02_2026-09-26.md   ladder 2 + rcv falsifiers
  Aether/RUNPOD_ENGINEERING_02_2026-09-26.md       platform Iteration 2
  Aether/RUNPOD_ENGINEERING_03_2026-09-26.md       platform Iterations 3-4
  Aether/AETH-01/AETH-02_CLOSE_2026-09-24.md       prior AETH-02 closing report

Instruments:
  Aether/observatory/aeth02_closure.py (+ _reduce.py)   H2/H3 closure
  Aether/observatory/aeth02_h2x_inflow.py, _h2x_sustained.py, _h3x_arg1.py
  Aether/observatory/aeth03_variants.py                 all variant kernels
  Aether/observatory/aeth03_scouts.py (+ _reduce.py)    ladder-1 battery
  Aether/observatory/aeth03_propagation.py (+ _reduce.py) twin assay
  Aether/observatory/aeth03_ablation.py, aeth03_rcv_probe.py
  Aether/test/test_aeth03_variants.py (21), test_aeth03_propagation.py (3)
  Aether/runpod/ (platform; README.md is the entry point)

Evidence:
  Aether/AETH-01/evidence/2026-09-26_aeth02_closure/
  Aether/AETH-03/evidence/2026-09-26_scout0/
  Aether/AETH-03/evidence/2026-09-26_propagation/
  Aether/AETH-03/evidence/2026-09-26_rcv_falsifiers/
  Aether/runpod/receipts/ (i2_*, i3_*, i4_*; preregistration in
    i3_preregistration.json)

Preregistration commits (before the runs they govern):
  8e5bd7af9  AETH-02 closure predictions + ladder-1 candidates/thresholds
  1fa58991e  H2-X (one-shot feeder cut)
  febfc7c60  H2-X2 (sustained cut)
  f7b85d542  H3-X (arg1 mechanism)
  c324af5ba  ladder-2 kernels, propagation assay, thresholds
  e493fde8e  rcv full-ring ablation + probe
  bc9d2a80a  rcv partial-ring (inert / writers) arms
  f369c6855  platform Iteration 3 preregistration

Integration commits on main: 698144bce (AETH-02 closure, ladder 1,
Iteration 2), cf8135928 (ladder 2, Iterations 3-4).

Directives (verbatim, manifest-verified):
  roles/Aether/prompts/2026-09-26_resume_science/
  roles/Aether/prompts/2026-09-26_next_round/

Seat state: roles/Aether/TODO.md (authoritative resume point),
roles/Aether/STATUS.md, roles/Aether/calibration/LEDGER.md (every error
named in section 7).

+==============================================================================+
|  END OF PACKET.                                                              |
|  "Not worth continuing" -- for the science, the platform, or Aether as a    |
|  whole -- is a first-class answer. So is "the bar is wrong". Please say     |
|  which numbers you do not believe and why.                                   |
+==============================================================================+
