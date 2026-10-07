# Hestia audit 1 -- dossier: odysseus (distributed spiking brain substrate)

VERDICT: SALVAGE_COMPONENT -- the circuit is a fixed-weight random LIF placeholder with no plasticity, no input and no task, so nothing here reasons or learns; the deterministic record / hash-verified replay / counterfactual-fork layer is a sound instrument worth carrying into a substrate that does learn.

Audit group G2. Auditor: Hestia worker (Claude, same model family as the author; see AUDIT_PLAN s4 conflict note).
Currency: 2026-10-06. Worktree C:/Prometheus-worktrees/hestia-boot-2026-10-06 at 3fed30ac9.

## 0. Identity

- Paths: odysseus/ (23 files, `git ls-files odysseus`), seat roles/Odysseus/ (475 files).
- Seat: Odysseus. Census (docs/fleet/fleet_state.json, engines["odysseus"]): kind research-engine,
  state PARKED, quoting roles/Odysseus/RESPONSIBILITIES.md:6 ("the 2026-09-26 brain charter is a PARKED
  lane"). Last commit on the path 33e2ee2c8 (2026-09-26). Four commits total on odysseus/:
  bd76253c6 (tests red), e731ac509 (green), 37051a342 (review packet), 33e2ee2c8 (fleet test prep).
- Read in full: odysseus/brain/model.py, shard.py, player.py (fork/Branch section 150-262),
  odysseus/DESIGN.md, README.md, pivot/ODYSSEUS_BRAIN_V0_REVIEW_2026-09-26.md,
  roles/Odysseus/calibration/LEDGER.md, STATUS.md, receipts/2026-09-26_windows_SPECTREX5.txt,
  BACKLOG_H0H5.md (brain rows), RESPONSIBILITIES.md head.
- Read partially (function inventory + targeted excerpts): brain/node.py (barrier/NAK loop 97-115),
  frames.py, wire.py, cluster.py, transport.py, tests/test_fork.py (assertions).
- NOT read: brain/__main__.py, INSTALL.md, most test bodies, roles/Odysseus/journal/ beyond a grep,
  and the seat's later expedition / fabric_pilot / frontier work (roles/Odysseus/expedition, fabric_pilot,
  frontier) except EXPEDITION_1_REPORT.md section 0 and recert/RESULT.md excerpts. That later work
  audits OTHER engines (Z80/NPE, BEE, WSE, RBN) and the agent fabric; it is not part of the odysseus
  engine and is cited only where it bears on G2's primordial dossier.

## 1. Mechanism (code, cited)

What the code does, tick by tick:

- Neuron model: integer leaky integrate-and-fire. `v = v - (v >> leak_shift) + c`, clip to +-2^24,
  refractory countdown 2, threshold 1000, reset to 0 on fire (odysseus/brain/shard.py:90-110).
  State is three int32 words per neuron: v, refractory, fired-last-tick (shard.py:1-6, STATE_WORDS=3).
- Connectivity: procedural and FIXED. `targets(spec, j)` draws 8 distinct targets from
  `hash_ints(seed, j, k) % n` (odysseus/brain/model.py:80-93). Weight is a constant per source class:
  +520 excitatory, -900 if `j % 5 == 0` (model.py:35-38, 85). There is no weight array anywhere; weights
  cannot change because they are not stored.
- Input: `drive_at` adds +450 to a neuron on ~1/4 of ticks, chosen by a hash of (seed, tick, gid)
  (model.py:106-110). This is pseudo-random noise, not a stimulus; nothing encodes a task.
- Step: sum weights of last tick's local fired neurons plus remote inbound spikes into `current`
  (shard.py:77-80), then integrate and fire (shard.py:83-110). Ablation zeros a neuron (shard.py:101-103);
  injection adds current (shard.py:87-88). Those two are the only interventions.
- Transport: lockstep BSP supersteps, spikes delivered at t+1 (DESIGN.md D1), every peer sends TICK_END each
  tick, receiver-driven NAK repair (node.py:97-115).
- Record/replay: keyframes every K ticks plus a per-tick log of inbound spikes, outbound spikes and state
  hash; Merkle root per tick (DESIGN.md D8, D11; frames.py:42 merkle_root).
- Fork: `Branch` replays one shard against the RECORDED inbound spikes with an intervention;
  `diverged_at` = first state-hash mismatch, `escaped_at` = first tick its remote-bound spikes differ
  (player.py:198-211); `exact_until` returns `escaped_at` (player.py:194-196).

Documented claims vs code:
- DESIGN.md s1 says plainly: "v0 is an instrument, not a reasoner ... The circuit model is a placeholder
  that exercises the substrate; it will be replaced." The code agrees (model.py:4-5 docstring). There is no
  overclaim to deflate here; the seat did not call this cognition.
- `grep -rniE 'plastic|stdp|learn|weight|reward|task|train'` over odysseus/*.py returns exactly one hit,
  the docstring of `targets` (model.py:82). No plasticity, no reward, no readout, no task, no loss.

## 2. Evidence (tiered)

OBSERVED (committed files on main):
- Windows receipt (roles/Odysseus/receipts/2026-09-26_windows_SPECTREX5.txt): 71/71 tests pass on
  Windows 11 / Python 3.14.4; a 2000-neuron, 4-shard, 100-tick process-mode local run verifies root_ok=true.
- Test suite design (odysseus/tests/): fork controls in test_fork.py:14 (no-op fork never diverges),
  :28 and :46 (an ablated firing neuron diverges and ESCAPES at or before its firing tick), :87.

CLAIMED (prose in the review packet; rows not in the repo):
- 71/71 tests on Linux; 40% injected loss on a 6-process, 4000-neuron, 200-tick run repaired 18,462 lost
  datagrams, 0/200 tick roots differ from the in-process reference; 57.56 s wall at 40% loss vs 2.87 s at
  0% (pivot/ODYSSEUS_BRAIN_V0_REVIEW_2026-09-26.md s4). Shard-count invariance 1 vs 2/3/4/7 over 40 ticks.
- Circuit behaviour: "strong period-3 synchrony (~20-30% of neurons fire per tick)" (same packet s6).

DESIGNED, never run:
- Two real hosts (BACKLOG ODYSSEUS-02), global multi-shard fork (ODYSSEUS-09), re-sharding (13),
  vectorised step (17). The brain was parked 2026-09-28 before any of these.
- Any learning rule, any task, any consumer of the replay instrument ("no consumer yet", packet s7).

Seat's own calibration ledger (roles/Odysseus/calibration/LEDGER.md) records four wrong calls; the one
touching this engine is the seek-cost test that was wrong (implementation right). No engine-level
negative result exists because no engine-level scientific question was ever asked.

## 3. Matrix

### 3a Combinatorial explosion and reachability

- State space per neuron: v in [-2^24, 2^24] x refractory {0,1,2} x fired {0,1}: about 2^25 * 6 states;
  for N neurons about (2^27.6)^N. Irrelevant in practice: the dynamics are an autonomous deterministic map
  driven by hashed noise, and the review packet reports a period-3 synchronous attractor at 20-30% firing.
  A network locked into a period-3 global rhythm uses a vanishing fraction of that space; it is the
  textbook "epileptic" regime of random E/I networks with strong uniform excitation, not a computing regime.
- There is no search space at all in the learning sense: zero free parameters are ever adjusted. The
  "reachable set" of behaviours is one trajectory per (seed, N, shard-independent) spec.
- The fork instrument's reach. With fanout 8 and targets uniform over all N neurons, the probability that a
  spike stays entirely inside its own shard is (1/S)^8 (side calculation, scratchpad g2_calc.py):
  S=2: 3.9e-3; S=4: 1.5e-5; S=7: 1.7e-7; S=64: 3.6e-15. So the first changed spike almost surely changes
  remote-bound traffic and the branch ESCAPES on that very tick (the test asserts exactly this,
  test_fork.py:46). The exact counterfactual window therefore covers sub-threshold perturbation only;
  any intervention that changes one spike is exact for 0 further ticks. "How far and how fast an effect
  spreads is itself the measurement" (DESIGN D10) cannot be measured shard-locally under this connectivity.

### 3b Cosplay vs foundation

- Which component does the work called "brain"? Nothing is called reasoning here, to the seat's credit.
  The "brain" is a fixed random graph with constant weights and a hashed noise drive. It is neither a
  heuristic loop nor a selection loop: it is a simulator with no objective.
- Ceiling as built: zero. With no stored weights (model.py:80-93) and no input channel beyond noise
  (model.py:106-110), the circuit cannot represent anything about an environment, cannot be trained, and
  cannot be selected (no genome, no fitness). Any task performance would have to come from an external
  readout trained on its spikes (a reservoir), and none exists.
- The foundation-grade part is the instrument: bit-identical integer dynamics across OSes (D6), per-shard
  record/replay with hash chains (D8, D9, D11), counterfactual fork with an explicit exactness boundary
  (D10). These are the properties a microscope for emergent circuits needs. They are real engineering,
  verified on two OSes on one host each.

### 3c Substrate bottlenecks

- Representation: one int32 membrane per neuron, uniform weights by class. No synaptic state, no
  dendritic or neuromodulatory variable, no eligibility trace. Credit assignment is impossible because
  there is nothing to assign credit to.
- Procedural connectivity (D7) is the load-bearing scalability trick (zero synapse memory, routing by
  recomputation) and is exactly what forbids plasticity. A plastic version needs an explicit table:
  32 B/neuron at fanout 8 x int32, i.e. 32 GB at N = 1e9, against 12 GB of membrane state.
- Throughput: pure Python, about 1.67e6 neuron-ticks/s aggregated over 6 processes at 0% loss
  (6 x 4000 x 200 / 2.87 s). N = 1e9 would take about 600 s per tick before any learning cost.
- I/O: every spike is a u32 id (D4). At 20-30% firing and fanout to ~3.6 of 4 shards, traffic is
  essentially all-to-all; the "traffic = the cut" economy of D7 only pays if connectivity is local, which
  the random graph is not.
- Lockstep BSP: the slowest shard sets the pace (the seat raised this itself, packet s9 Q2).
- Determinism via integers is a strength for replay and a constraint on any future float learner (packet
  s9 Q1); fixed-point plasticity (Loihi-style) is the compatible route.

## 4. Deliverable

Discovery Approach. Odysseus does not try to discover reasoning. It builds the microscope: a sharded
spiking circuit whose every tick can be replayed, verified and counterfactually forked from files, so that
weak signals in long runs could be examined at the exact tick without re-running. The circuit was a
deliberately disposable placeholder.

The Brick Walls.
1. No learning, no task, no input (model.py:80-110): the substrate cannot exhibit any circuit beyond the
   attractor of its random wiring; the reported attractor is period-3 global synchrony at 20-30% firing.
2. Fork exactness collapses at the first spike change: P(spike stays local) = (1/S)^8 = 1.5e-5 at S=4,
   so shard-local counterfactuals are exact for 0 ticks after a spike-level effect; the core microtest
   promise (D10) needs a global fork (ODYSSEUS-09, never built) or local connectivity.
3. The scalability design forbids plasticity: procedural synapses have no memory; adding them costs
   32 B/neuron (32 GB at 1e9) and breaks the zero-memory routing argument; pure Python runs ~600 s/tick at
   1e9 neurons.
4. Never exercised across real hosts (ODYSSEUS-02 not done); parked since 2026-09-28 with no consumer.

Seed Viability. As a cognitive substrate: nothing to salvage; the LIF placeholder is a random reservoir in
a pathological regime. As an instrument: SALVAGE_COMPONENT. The record / hash-chain replay / escape-bounded
fork pattern (frames.py, player.py Branch) is the right shape for observing an emergent circuit and would
detect a real one only if (a) the observed substrate has state worth perturbing and (b) forks can run
globally. Today it would detect nothing because nothing is there.

Evolutionary Roadmap (only if the operator wants a spiking line at all; otherwise lift the instrument
into a learning engine and retire the circuit):
1. Replace D7 with an explicit per-shard synapse table (CSR, int16 weights) and add a three-factor
   integer plasticity rule: eligibility trace e_ij updated by pre/post spike timing, weight change
   = e_ij * M(t) where M is a broadcast reward/neuromodulator integer (the e-prop / R-STDP family,
   Bellec et al. 2020; Fremaux and Gerstner 2016). Keep all arithmetic integer so D6 replay survives.
2. Add a real I/O contract: input neurons clamped by a task encoder, output population read by a
   population-vote decoder; tasks with known memory demands (delayed match-to-sample, temporal XOR,
   n-back), so a circuit is a measurable object.
3. Balanced E/I with local (distance-dependent) connectivity and a homeostatic threshold, to leave the
   synchronous regime (target: asynchronous irregular firing, CV of ISI near 1) and to make traffic and
   fork escape local.
4. Global fork (ODYSSEUS-09) as the default microtest; measure effect light-cones (spike-difference
   spread per tick) as the instrument's primary readout.
5. Vectorised integer step (numpy int32 or a C kernel) with the same hash contract.

The ONE decisive experiment. "Does plasticity add anything over a fixed reservoir?" Implement step 1 + 2
on one host, N = 4000, 8 seeds, delayed match-to-sample with delay 5-20 ticks. Arms: (A) plastic circuit,
(B) the same circuit frozen with a ridge-regression linear readout on spike counts (the reservoir
control), (C) shuffled-reward plastic control. Kill criterion: if (A) does not beat (B) by >= 10
percentage points accuracy in >= 6/8 seeds at the longest delay it solves above chance, or if any replayed
tick root mismatches under plasticity, close the spiking line and keep only the instrument.

## 5. What would change this verdict

- Evidence of a consumer: a committed run where the fork/replay instrument localised a mechanism in some
  learning substrate (would raise the instrument to a confirmed component).
- A committed plastic variant with a task curve beating a reservoir control (would move toward VIABLE_SEED).
- Evidence that I misread connectivity (e.g. a local wiring mode exists) would weaken brick wall 2.
- Downgrade to DEAD_END if the replay/fork layer cannot be made global or cannot carry stored, mutable
  synaptic state without losing bit-identity.
