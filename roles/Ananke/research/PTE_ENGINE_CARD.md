# Engine card: Ananke / PTE (Packet-Tensor Engine)

Currency: 2026-09-27. Code: prometheus/ananke/ (engine.py, oracle.py,
envs.py, assays.py, search.py, c1b.py, lens.py). Spec: roles/Ananke/pte/
DESIGN.md. Evidence: PTE-C1, PTE-C1b, the 2026-09-27 spikes.

SCIENTIFIC LENS
Where does information live, and how does it move, when computation is
forced through lossy, delayed, SUPERPOSING messages among identical
programs? PTE is the fleet's lens on CHANNEL STATE: information that exists
only between sites, in flight. It can decompose a working mechanism into
process state vs channel content, count, timing and destination, by exact
mirror-pair carrier swaps. Deterministic integer physics makes those swaps
exact, with no noise floor.

WORLD
B worlds x N sites on ring, torus, random, smallworld or global graphs.
int32 state saturates at +-32767. Randomness is a counter hash per named
stream (it never depends on state). Packets are (channel, payload[P]) and
SUM on arrival: no source identity. Per-copy loss, latency (base + hop +
jitter), duplication, noise; receiver caps with none/aloha/saturate;
sync or async wake; decay S -= S >> k; optional energy economy; plastic
routing weights; G rule variants selected by SETRULE; writable immediates
(WIMM); in-lifetime mutation. The environment is write-free: sense in,
S0 trace out.

ENTITY
There is no organism. The entity is a HOMOGENEOUS LAW (one genome run by
every site) plus the world's physics. A "mechanism" is a pattern of
channel and process state that the law produces. Individuals are not
defined. Reproduction is absent (the outer GA is external).

MEMORY (where useful state can reside)
Process: S, inbox (Acc), Kp, energy E, routing w, rule pointer r.
Channel: the in-flight ring (content per payload component, count, arrival
slot, recipient). Shown so far (12 D-wave cells + M2): channel CONTENT
(M2, M3, 3 RELAY), SITE state (HOLD latches, 1 RELAY, 1 MAJ), and a
JOINT channel+site carrier (MAJ 4781b0a1). Never counts, never routing.
Configuration (corrected 2026-09-27 by W-B): r is a bootstrap into the
zero-default rule variant in ~64% of the 42 qualifying C1 cells (incl. M3;
a physics artifact: registers are 0 at tick 0). In ~29% it is a
readout-local, per-tick CONDITIONAL BRANCH (sign-conditioned excursions
in RELAY; sample/hold alternation in HOLD). r was never the memory
carrier in 18/18 swap tests. Routing: infrastructure
only. No environmental memory is possible (write-free env).

BEST EXPERIMENT TYPES
- Carrier identification by mirror-pair swaps (exact counterfactuals).
- Physics sweeps: phase maps over loss, latency, superposition, caps,
  asynchrony, topology.
- Interval and latency tuning (deadline vs code vs tolerance).
- Evolved-vs-designed comparisons: hand plants as positive controls.
- Transfer across size (laws are size-free) and topology (they are
  topology-bound).

BAD FITS
- Anything needing individuals, heredity, open-ended growth or resource
  competition between entities (there are none).
- Long-horizon memory: champions tune to the trained interval (M2 fails
  beyond the trained gap).
- Rich composition: XOR and FLIP were NULL. Two-stage compositions are
  rarely found at C1 budgets.
- Questions whose answer depends on the GA (the search is a declared
  external GA, not part of the world).

OBSERVABILITY
Direct and exact: every state array per tick, per world; in-flight
content per slot, recipient, channel and component; stats (attempted,
delivered, lost, collided); single-cue twin differences. Inferred:
mechanism labels, "configuration" vs "memory", codes (from swaps and
decoders).

KNOWN FAILURE MODES (established)
- ZERO-DEFAULT RULE PRIVILEGE: registers start at 0, so SETRULE sends every
  site to rule 0 at tick 0. Random initial r acts as a site-deletion mask.
  Initialize r = 0 when asking whether rules are used (W-B).
- PRESENT-BUT-UNUSED carriers: a component can decode the cue without
  carrying it (4781b0a1 pay0: decoder 0.85, swap no effect). Decoders
  alone never identify a carrier.
- WRITTEN-BUT-NEVER-READ SCARS: non-decaying plastic stores (w, Kp)
  keep cue-signed traces forever with no effect (W-E). Retention is not
  use.
- TEMPORAL-WINDOW BLINDNESS: an ablation window missing the causal tick
  (C1 D-A). Fix: cue_arrival_profile reach checks.
- CHANNEL INERT BY PHYSICS: frozen routing under dest_mode "all".
- POSITIVE-CONTROL ELIGIBILITY: a plant may be unable to operate at
  specimen physics (C1b A3). Absence readings then go _UNRESOLVED.
- ABSOLUTE THRESHOLDS vs weak champions: "kills" is automatic near 0.6.
- FIXED-COMPONENT CENSUS: codes relabel across payload components; census
  per component or use swaps.
- CROSS-TRIAL CARRYOVER: waves can outlive a short ITI (relay_flood ~48
  ticks); census at trial onset.
- CELL-ID-KEYED metadata that should be physics-keyed (C1b eligibility).
- GENOMES NOT STORED for replication searches (C1b S2). They are
  regenerable, because the searches are deterministic.

PORTABILITY
Inherent: Python 3.12, numpy, torch. The CPU works for everything (the
oracle and tests run on CPU; the spikes ran in minutes). CUDA only speeds
things up (CUDA-graph tick replay; C1 ran 17.5 h on one RTX 5060 Ti).
Aether ran the conformance suite unmodified on RunPod (139 passed, #744).
Current host placement (M1, SKULLPORT) is circumstantial. Run state lives
outside git under ANANKE_HOME.

CROSS-POLLINATION
PTE -> others: the mirror-pair carrier swap (FLIP / NO-EFFECT / CHANCE);
the cue_arrival_profile reach check; the positive-control eligibility rule
(A3); golden-digest-before-edit. Others -> PTE: Cosmos's P1/P2
certificate (present vs used); Aether's site-class starvation; Lizier
storage/transfer measures with channel variables (JIDT/IDTxl) for
screening; the ping probe; CA carrier models (Crutchfield-Mitchell).
