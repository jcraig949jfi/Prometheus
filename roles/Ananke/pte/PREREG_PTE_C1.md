# PREREG PTE-C1 -- first Packet-Tensor Engine campaign

Currency: 2026-09-24. Seat: Ananke. Status: PREREGISTERED (this file is
committed on its own, before the campaign freeze and before any campaign
row exists). Mission: roles/Ananke/prompts/2026-09-24_charter/ (verbatim).
Nothing below may be changed after launch; corrections are dated
annotations beside the original.

## 0. Question and what would count as an answer

Can cognitive-like organisation emerge from asynchronous, lossy packet
traffic through a mutable integer tensor substrate with no imported
neural architecture -- and WHERE in communication-physics space does
organised information processing become possible, persist, adapt and
transfer? The deliverable is an empirical phase map with graded,
conservative labels (s9), including NULL regions with their eligibility.

## 1. Substrate (normative spec: roles/Ananke/pte/DESIGN.md)

PTE-SUB-1 / PTE-OPS-1. B independent worlds x N sites; every value int32
saturated to +-32767; counter-hash randomness H(ws, stream, t, n, j) with
named disjoint streams; packets = (channel, payload[P]) that SUPERPOSE on
arrival (per-channel sums and counts), no source identity; per-copy loss,
latency (base + hop*dist + jitter), duplication, additive noise; receiver
bandwidth cap with none | aloha | saturate collisions; sync or async
updates; decay S -= S >> k (sign-asymmetric, DESIGN s10).
Local update law: a straight-line program of L instructions (5 integer
fields) over a register file [S | T | O | IN_sum | IN_cnt | SENSE |
ENERGY | ZERO]; 16 primitive ops: NOP MOV ADD SUB MULQ ADDI CONST GT SEL
MAX SHR XOR MOD RAND SETRULE WIMM. Adaptation channels: writable routing
weights (plastic_route), writable immediates (wimm; packet-mediated when
B reads an inbox register), state-conditioned rule selection (setrule, G
variants), in-lifetime parameter mutation (mut_site). Energy economy
(emit/op/memory costs) optional. Actuator readout = sign of S0.
Mutable state semantics: S persists (decays if k>0); T and O are zeroed
each run; inbox accumulates until the site next wakes.
Correctness: an independent CPU oracle written from DESIGN.md without
reading the engine agrees bit-for-bit (tests: 145 pass at freeze).
Determinism: all-integer; replay is exact on any hardware. There is no
GPU numerical tolerance: any replay mismatch is a DEFECT, not noise.

## 2. Environment families (envs.py)

RELAY (transport + delay), XOR (two separated inputs, each alone carries
zero information), MAJ (5 sensors each flipped w.p. 0.3; single-sensor
ceiling 0.70), FLIP (hidden mapping m flips every `block` trials; teacher
signal at the actuator only AFTER readout; first trial of a block
unscored), HOLD (sensor = actuator; distractors during the gap).
Targets are i.i.d. and worlds are MIRROR PAIRS (negated target sequence,
shared physics randomness): every constant policy scores exactly 0.5 per
pair; lag-1 target correlation ~0 (tested). Positions are redrawn per
world, so a homogeneous program cannot memorise its actuator.
Baselines on the gate's own scale, computed at prereg: constant = 0.500
exactly (pair mean); memoryless/no-communication = the champion's own
zero_comm control, run on the same held-out worlds for every cell;
single-sensor ceiling for MAJ = 0.70; XOR single-input = 0.500 exactly.

## 3. Search ranges (campaign.py DIALS / ENV_DIALS, drawn uniformly)

topology {torus, ring, random, smallworld, global}; n_sites {64,100,144};
radius {1,2,3}; k_random {3,6}; rewire {50,200} per mille; state_dim
{1,2,4,8}; payload_width {1,2,4}; channels {1,2,4}; fanout {1,2,4,8};
dest_mode {sample, all}; loss {0,.1,.3,.6}; loss_per_hop {0,1}; lat_base
{1,2,4}; lat_hop {0,1}; lat_jitter {0,1,3}; dup {0,.1}; noise {0,16,64};
cap {0,1,2,4}; collision {none,aloha,saturate}; decay_shift {0,1,3,6};
update_mode {sync,async}; update_period {1,2}; update_p {.5,.8}; rules
{1,2,4}; prog_len {8,12,16}; plastic_route {0,1}; adapt_shift {2,5};
wimm {0,1}; setrule {0,1}; mut_site {0,.001,.01}; economy {off, low
(income 4, max 200, emit 1), high (income 4, max 100, emit 4, op 1, mem 1)}.
Env: d {1,2,3,5}; delta {4,8,16}; gap {4,8,16}; block {2,4}; trials 12
(FLIP 16). Scale probe sizes: 400, 1024, 2304.

## 4. The declared outer search

Mutation + truncation selection over world genomes (a GA over linear
register programs; the search, not the substrate). A1/B/C/D: pop 96, 36
generations, 8 fresh training worlds per generation (4 mirror pairs),
elite 4, top 25% parents, field resample 0.04, instruction resample
0.15, swap 0.10, uniform crossover 0.30. Selection fitness = training
accuracy + 0.10*max(actuator twin contrast, 0) + 0.02*substrate
sensitivity (max bonus 0.12). Reason: random program space is ~99% deaf
(preflight: 1-5% of random genomes let a cue perturb the substrate at
all, ~0.1% reach the readout), so pure accuracy gives a flat landscape.
The bonus rewards "the input sign causally moves the actuator", not any
architecture. The CHAMPION is chosen on training accuracy alone (fresh
16-world re-evaluation), then evaluated ONCE on 64 held-out worlds (32
mirror pairs) from a disjoint seed namespace, with its zero-comm control
on the same worlds. Plants are never injected into a population.

## 5. Waves and budgets (hours are hard caps; unrun cells are CENSORED)

A0 physics census, 5000 cells, 3.0 h: per cell 64 random genomes x 8
   worlds (random-substrate liveness: fraction sensitive, fraction
   emitting, telemetry) + plant viability (relay_flood for comm families,
   hold_latch for HOLD; prog_len max(L,12); + its zero-comm control).
A1 evolution census, 400 cells, 5.0 h: even cells uniform physics; odd
   cells re-draw a LIVING A0 cell of the same family (plant >= 0.75 or
   random-substrate sensitive fraction >= 0.30). Declared bias: toward
   physics where information demonstrably can move; half stay uniform.
B  boundary search, 3.0 h. phys track (census cells): per family the 3
   dials with the largest A0 effect on plant viability + 3 on
   sensitivity; bases = most viable A0 cell and the A0 cell whose plant
   accuracy is closest to 0.75; every level of the dial; 3 replicate
   seeds. evo track (evolve cells): only families with >= 1 A1 SIGNAL;
   3 dials by A1 held-accuracy effect; bases = best and best-other-
   physics A1 cells; 3 replicate search seeds per level.
B2 fresh-seed reproduction of every transect with a candidate, 1.5 h.
C  pressure diversification + transfer, 1.5 h: top 12 physics (by held
   lo99) re-evolved on every other family, frozen champion evaluated on
   every family and on env variants (d=5, delta=16) and (d=1, delta=4).
D  causal adjudication, 2.0 h: up to 24 SIGNAL cells (<= 4 per family),
   full control battery, twin assay, transplant battery, 2 fresh-seed
   search replications each.
E  scale probe, 1.5 h: top 5 promoted, frozen law at N = 400, 1024,
   2304 (where the mailbox bound allows) + one re-evolution at N = 400.
Total cap 17.5 h. Execution: local RTX 5060 Ti. NO RunPod spend in C1:
throughput suffices for every wave (A0 1.7 s/cell, A1 ~37 s/cell
measured); RunPod is justified only if E shows scale-dependent
strengthening, in a follow-up with its own cost ceiling.

## 6. Anomaly detectors (flags, never verdicts; campaign.anomaly_flags)

SILENT_COMPETENCE (held > .6, emit_rate < .01, non-HOLD);
COMPETENT_WITHOUT_COMM (held > .6, comm_delta < .02, RELAY/XOR/MAJ: a
leak or an unplanned channel); MEMORY_WITHOUT_USE (twin persistence >
3*delta and > 25% of sites carry the cue at readout, held <= .55);
ROBUST_UNDER_LOSS (held > .6 at loss >= .3); COMPETENT_UNDER_COST (held
> .6 at economy high); ANTI_CORRELATED (held < .45: a sign-locked
mechanism, e.g. via the decay asymmetry); TRAIN_HELD_GAP (train - held
> .15); DISTRIBUTED_MEMORY_UNDER_DECAY (HOLD held > .6 at decay 1 or 3
with comm_delta > .05). Discontinuities are detected by s8.

## 7. Promotion and labels (mechanical)

SIGNAL: held-out 99% bootstrap lower bound over mirror pairs > 0.55.
COMM_DEPENDENT: SIGNAL and (held - zero_comm) lower bound > 0.03.
LOCAL_ONLY: SIGNAL and not COMM_DEPENDENT.
INTEGRATION: MAJ lo99 > 0.70, or any XOR SIGNAL.
REPRODUCED_SIGNAL: a D-wave fresh-seed search replication of the same
  physics/env reaches SIGNAL (>= 1 of 2).
CAUSAL_SUPPORT: adjudication shows the family's mechanism is necessary:
  comm families: zero_comm <= 0.55 AND packet_ablation <= normal - 0.10;
  HOLD: memory_ablation <= normal - 0.10; and the env-permutation null
  lies within [0.40, 0.60]. The full ablation pattern is reported as the
  mechanism map regardless.
TRANSFER_SUPPORT: a frozen champion reaches SIGNAL in a condition it was
  not trained in (other family; env variant; other size; transplanted
  physics in the D battery).
INCONCLUSIVE: the family's key control is NOT_APPLICABLE (no-op guard),
  or the cell was budget-censored.
NULL: everything else, reported with the region's eligibility (the
  plant-viability and liveness of that physics), so "nothing fired" is
  never confused with "nothing could have fired".
No machine-generated label stronger than these exists. "Intelligence"
is never a label.

## 8. Phase-boundary criteria

On a transect (one dial varied over all its levels, everything else at a
base cell) with >= 3 replicates per level, metric m in {held accuracy
(evo track only), plant accuracy, random-substrate sensitive fraction,
random-substrate emitting fraction}:
CANDIDATE at adjacent levels (i, i+1) iff |jump| >= max(0.10, 3 * SE of
the difference) AND the transect range >= 0.10 AND |jump| >= 0.5 * range
(a single step carries at least half the change: the smooth-amplifier
null, tested in test_campaign_logic).
SUPPORTED iff the same (family, dial, metric, track) boundary (same sign,
location within +-1 level) is met again on fresh seeds (B2) AND on the
second base point.

## 9. Transplant criteria

Update-law transplants (the genome is the law): loss +0.2, latency +1,
jitter +2, noise +32, size x2.25, async 0.7, topology -> random. FLIP
only: adapted-state transplant at a block boundary (S, w, Kp, r) vs a
fresh-state recipient. A transplant counts as TRANSFER_SUPPORT only if
the recipient reaches SIGNAL; a collapse is reported as what the
mechanism depended on.

## 10. Stopping conditions

Per-wave hour caps (s5); PARK after 5 consecutive failed cells
(PARKED.json, accountable seat Ananke, resume only on clearance); the
driver refuses to start if the code SHA differs from the frozen SHA or
prometheus/ananke is dirty; watchdog relaunch cap 20.

## 11. Eligibility and attainability (from preflight, not campaign data)

Preflight seeds 1-3 (never reused): 110 cells. A0 plant viability >= 0.75
in 20% of cells (HOLD 11/12, RELAY 1/12, XOR/MAJ/FLIP 0/12 -- the relay
plant cannot solve XOR or FLIP by design); random-substrate sensitive
fraction >= 0.30 in 17%; living (either) 32%. A1 at the frozen budget:
1/10 SIGNAL (HOLD, local, 0.977); best RELAY 0.554 (lo99 0.531, zero-comm
0.500). Expected: SIGNAL in ~5-15% of A1 cells, mostly HOLD;
COMM_DEPENDENT rare. Therefore a NULL in a comm family is only
informative where plant viability or liveness shows the physics could
carry the signal.

## 12. Losable predictions (Ananke's, scored in the final report)

P1 The phys track finds >= 1 PHASE_BOUNDARY_SUPPORTED in RELAY plant
   viability along latency (lat_base), loss, delta or d.
P2 decay_shift is among the top 3 A0 dials for HOLD plant viability or
   sensitivity, and HOLD evolved competence at decay_shift = 1 is NULL.
P3 Zero XOR cells reach SIGNAL.
P4 <= 5% of A1 cells are COMM_DEPENDENT.
P5 Zero cross-family TRANSFER_SUPPORT for comm-family champions.
P6 Zero DISTRIBUTED_MEMORY_UNDER_DECAY flags.
P7 HOLD champions keep held accuracy within +-0.05 from N=100-ish to
   N=1024 (a local mechanism is size-free).
P8 At least one ANTI_CORRELATED flag is traceable to the sign-asymmetric
   decay (decay_shift > 0 in that cell).

## 13. Conflicts of interest

The same author (Ananke) wrote the substrate, the environments, the
search, the detectors and these predictions; only the oracle has an
independent author. Holdouts are seed namespaces, not sealed worlds from
another seat. Adversarial review of the evidence package by Kairos,
Elenchus or Nemesis is the independent failure mode promotion requires.
