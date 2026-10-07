# Native runtime candidates for the first native retained-information witness (C-009-T012)

Author: Cadmus[m1-a86ec5e4], claude-opus-5-5, 2026-10-07. Base 5e2639d3e. Preparation only (directive s11): no
witness predicate was computed and no retention outcome was looked at. What was run is listed in section 4.
Palamedes selects (directive s6); this file recommends.

Selection rule used here (plan s3/s7.1; directive s6): a REAL runtime that already exists and runs in this
repository; it retains information natively across a boundary it names in its own terms; an allowed channel and a
forbidden one can be stated from its own code; a world-side oracle exists outside the organism; a delayed-leak reset
and a clean allowed-state twin can be built WITHOUT editing the runtime (adapter-side wrappers only); the adapter can
emit canonical receipt bytes and ledger rows through rso.binding without the shared code reading runtime state
(BX6); it is cheap; and it does not collapse into the slice001 register toy.

Source survey: a read-only repository sweep, then my own reading of the top three (file:line below) and smoke runs.

## 1. Candidates

### C1 Ares -- evolved graph organisms in partially observed worlds (ares/)   RECOMMENDED
- Entry: ares/search.py rollout(pop, world, seeds, record) (:63); worlds from make_world; populations from
  ares/substrate.py random_population / Population, genomes serialisable (Population.genome / from_genomes).
  numpy only, CPU.
- Native retention: W4HiddenRegime (ares/worlds.py:170) shows the regime bit r in the cue channel for steps 0-2 only;
  reward depends on acting on r for all 40 steps. W15Interrupt (:430) adds 4 unobservable RESET events after the cue
  that zero every hidden and output activation; its docstring states the channel split: "An activation carrier loses
  its contents; plastic weights survive."
- Named boundaries (its own terms): (B1) the W15 interrupt step (within a lifetime); (B2) Runtime.reset() between
  episodes (ares/substrate.py:398-400: v := 0, live W1 := genome W1).
- Allowed / forbidden: across B1, allowed = plastic live W1 (and the genome); forbidden = activations v (erased by the
  world). Across B2, allowed = the genome only; forbidden = everything the episode wrote (v and plastic W1 deltas).
- Delayed-leak reset (adapter wrapper, no runtime edit): an episode reset that zeroes v but skips restoring W1 from
  the genome, so episode k's regime written into plastic W1 can reach episode k+1. Clean twin: same genome, the
  correct reset. Allowed-channel twin: same genome with plasticity disabled (Config.allow_plasticity False or R = 0),
  which must lose retention across B1 if W1 is the carrier.
- Oracle: world.r, kept by the world (info["regime"]); the organism never sees it after step 2; the ruler reads
  actions and the oracle only.
- Readout / observer: rollout(record=True) returns actions, rewards and per-step info; reading them does not touch
  the runtime. Carrier instruments (ares/carriers.py: RECUR, KEEP, PLAST, edge ablation, transplant) exist for
  controls.
- Determinism and cost: seeded default_rng per episode; ares/tests test_determinism. Smoke: 64 organisms x 16 W15
  episodes = 0.08 CPU-s.
- Toy-collapse risk: moderate in general (a KEEP self-loop is a register), LOW across B1 in W15, because the world
  zeroes activations; only continuous plastic weights can carry r past an interrupt.
- Adapter: subject = a frozen genome (bytes hashed as code-like input); receipts carry the genome digest, world
  variant + seeds, action traces as artifacts, oracle digest; ledger rows via rso.binding (opaque node ids).

### C2 Ensorain -- lifetime learner with an audited persistent-memory cap (ensorain/e1, ensorain/d1)   FALLBACK
- Entry: ensorain/e1/life.py live(world, mem, events, econ, record) (:20); ensorain/d1/core.py run_life (:382).
  numpy.
- Native retention: a fitted tensor model plus replay/error stores within a float cap; the world's generative field
  drifts at a known event (d1/core.py PHASE2 = 600), so the phase boundary is native.
- Allowed / forbidden: allowed = audited persistent floats inside the cap; forbidden = anything outside it. The
  forbidden channel is coded natively: a Smuggler memory (e1/mem.py:320) is refused by AuditError
  (e1/tests/test_e1.py).
- Delayed-leak reset / twin: the Smuggler is a ready-made leak; a clean twin is the same memory class under the
  audit. Oracle: the true fields x_old / x_new.
- Cost: seconds per life. Risk: low (memory is a fitted model). Weakness vs C1: the boundary is a drift in the
  world, not a reset of the organism, so "erase forbidden past while preserving allowed state" maps less directly.

### C3 Z80 Atlas -- self-replicating byte-VM soup (archaeon/z80atlas/)
- Entry: engine.run(spec, seed) (:159), "pure function of (spec, seed)"; pure Python (SplitMix64).
- Native retention: heritable executable tapes across births; a run boundary crossed by spec["transplant"]
  (:179-194) with provenance labels; byte-level attribution in archaeon/lineage/core.py.
- Allowed / forbidden: tape bytes are the only heritable channel; provenance rules define what may cross.
- Oracle: founder origin classes and ancestry sets. Cost: unmeasured per spec (test suite 28 s). Risk: low.
- Weakness: retention here is heredity across generations; a "useful bit" claim needs a task and a readout that
  the engine does not expose directly; larger build.

### C4 Prometheus toolbox kernel (prometheus/toolbox/)
- Native episode / lifetime / persistent state scopes with STATE_DISCARD events, reset / snapshot / restore,
  Observer protocol, checkpoint and resume. Best machinery; HIGH toy risk with its state-machine players (one KV
  slot is the slice001 register under another name). Usable only with non-register players.

### C5 Campaign-6 composed worlds (archaeon/campaign6/worlds/runtime.py)
- World pools, cells, signal word and delay queue; `shared` dict carries them across organisms in a generation.
  Oracle: hidden rich-pool index. Risk moderate (the signal is one word); organisms are proteus VM players
  (standalone run not checked).

### C6 Herakles CA stream reservoir (herakles/ca_stream/)
- Explicit reset per stream, reset_leakage_probe, delayed-recall oracle. HIGH risk: its positive controls are shift
  registers and the recorded result is that the recovered rules carry nothing (test_ca_stream.py:271-294).

Weaker, not recommended: ergon/gen1a persistence (a search library, not an organism); nyx avida_ancestry (its own
docstring calls it a toy); primordial regressors / predator-prey (no carried memory) and nv (GPU).

## 2. Recommendation

C1 Ares, world W15 (with W4 as the no-interrupt reference). Reasons, in order:
1. The channel split the witness needs is stated by the runtime itself (activations erased, plastic weights
   survive); nothing about allowed vs forbidden is imposed by the observatory (BX6, plan s3).
2. Two native boundaries map one-to-one onto the slice's predicates: B1 for retention through an allowed channel
   (and CHANNEL by plasticity ablation), B2 for ERASE / PRESERVE (delayed-leak reset = skipped W1 restore).
3. The oracle (r) lives in the world and is never shown after step 2.
4. It runs here now, is seeded, and is cheap (0.08 CPU-s per 64 x 16 episodes), far inside the C-009 caps.
5. Across B1 the carrier must be continuous plastic weights, which is not the slice001 register.

Fallback: C2 Ensorain (audited cap with a native smuggler control). Third: C3 Z80 Atlas.

Reversibility (for Palamedes's record): choosing Ares commits no shared code; the adapter is a client module, and
switching to the fallback costs only that adapter and its fire cases. Revisit if the frozen subject evolves no
carrier at all (then the witness can still conclude NEGATIVE or DETECTION_UNQUALIFIED honestly), or if the
calibration gate in DESIGN_DRAFT.md fails on W15.

## 3. Risks recorded now
- Ares outcomes are stochastic: the slice's exact enumeration does not apply; the witness needs registered sample
  sizes, thresholds and an INDETERMINATE band (DESIGN_DRAFT.md s5). This is new relative to C-004 (closure D02).
- The subject must be frozen (genome bytes) before any witness episode; its selection must use seeds disjoint from
  the witness seeds.
- Existing author tests of hand-wired carriers (ares/tests/test_carriers.py) are not witness evidence.

## 4. What was run (smoke only) and what was not
Run on SKULLPORT, 2026-10-07: `python -B -m pytest -q -x` on ares/tests (19 passed, 12 s), archaeon/tests/
test_z80atlas_provenance.py (33 passed, 1 skipped, 28 s), ensorain/e1/tests (17 passed, 1.3 s); one Ares W15 rollout
of a random 64-organism population over 16 episodes, printing only the fitness array SHAPE and CPU time (0.08 s).
Not run: no evolved subject, no witness predicate, no retention statistic, no controls, nothing for C4-C6.
