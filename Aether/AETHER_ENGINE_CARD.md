# AETHER ENGINE CARD

Version 1, 2026-09-27. Seat: Aether. The first engine card in the program
(no house format existed; the section list is the operator's, research
block Block I). It describes what Aether is FOR -- the questions it can
answer and the ones it distorts -- and points to the evidence. It is
updated by rewriting, not appending; superseded versions go to git history.

---

## 1. SCIENTIFIC LENS

**Aether asks what happens BELOW the level where other Prometheus engines
start.** BEE, NPE and Archaeon's Z80 causal-provenance machines begin with programs
that execute: identifiable code, a program counter, a birth event. Ananke's
PTE begins with executable configurations and crossover. Aether begins with bytes on a lattice
and one local rule. There is no program, no individual, no birth primitive,
no executable-configuration boundary, and nothing in the physics knows what an assembly is.

What that lets Prometheus ask that the others cannot:

- **Is propagation itself a property of the law?** In an engine with
  executing programs, influence travels because code runs. In Aether you
  can ask whether a local rule lets a difference travel at all, and measure
  it exactly (a one-bit twin, shortest causal chain, counterfactual parent).
- **Which assumption carries which behaviour?** Laws differ by one written
  rule change and share a code path proven bit-identical to the baseline,
  so an effect is attributable to one sentence of physics.
- **Is a "positive" the substrate or the rule?** Aether's own history is
  the calibration: `rcv` propagates, and the propagation is its own relay
  working as written. The lens is built to catch that.

## 2. WORLD

A 2-D torus of sites, five uint8 fields each (opcode, arg0, arg1, payload,
energy), updated synchronously by an exact-integer, hash-keyed local law.
Baseline law `aeth01.v1`: a site is active if its opcode is WRITE (1 of 256
values) and it has energy; each active site proposes ONE write -- its
payload into one field of one von Neumann neighbour (direction arg0 mod 4,
field arg1 mod 5; the energy field receives a transfer). Contests are
decided by a keyed hash re-drawn every tick. A winning write REPLACES the
target byte, then with probability 0.1 one bit of it flips (perturbation,
"Mu"). Energy: writes cost 1, maintenance 1 per tick, replenishment +8
with probability 1/8. Every change is local: radius 1 per tick (one scouted
variant, `mov`, radius 2). Full spec:
`Aether/AETH-01/AETH01_REPAIRED_FREEZE_CANDIDATE.md`.

Variant laws (scout kernels, each its own semantics id, never reported as
v1): `Aether/observatory/aeth03_variants.py`.

## 3. ASSEMBLY ASSUMPTIONS -- what is NOT built in (the directive's legacy term: organism assumptions)

Not built in: individuals, assemblies, bodies, executable-configuration
boundaries, predecessors, construction events, recursive construction, an
evaluation score, selection, termination as an event, any objective. Energy
is a conserved-ish resource, not a score. Nothing rewards spreading,
persisting or copying; the operator's standing rule for Aether is
"observation and intervention only; no steering".

Before any assembly-level language is justified here, Aether would have to
show, in order, each by intervention against a matched null:
1. a bounded region whose state persists because of its own internal
   interactions (not because it is frozen or fed from outside);
2. influence that crosses that region's boundary and changes something
   outside, repeatably;
3. that region's configuration being reproduced elsewhere by the
   dynamics (not by a copy rule).
None of the three has been observed. Current Aether results are about
causal influence and persistence in a medium, and are reported in those
words (`Aether/AETH-01/COMPUTATIONAL_TERMINOLOGY.md`; a linter enforces it).

## 4. BEST EXPERIMENT CLASSES -- send these to Aether

- **Does rule X let influence travel / transform / persist?** One-bit twin
  assays with exact locality, adjacency and counterfactual causal
  generations, content signatures. Seconds to minutes per unit on CPU.
- **Is this effect the substrate or the rule?** Minimal single-change laws
  on a shared, bit-identical code path; interventions that leave the effect
  a route to persist (partial-ring starvation), not ones the law forces.
- **What does a null model miss?** Aether's AETH-02 lesson: the 3.1x
  lifetime "gap" was a missing energy term. Aether is a good place to test
  null models, because the true mechanism can always be read off the law
  and checked by counterfactual.
- **Reproducibility and distributed-execution test beds.** Units are exact
  and bit-identical across Windows/Linux, Python 3.11/3.13 and NumPy
  1.26/2.4; known answers exist in committed evidence.

## 5. BAD FITS -- questions Aether distorts

- **Anything about selection or ensembles of assemblies.** There is no
  inheritance of anything but bytes and no selection of anything; asking
  "does the evaluation score rise" imports a frame the physics does not have.
- **Continuous or stochastic chemistry.** Aether is exact-integer and
  synchronous by design (replay, differential testing); rate-based or
  continuous phenomena are poorly represented.
- **Large-scale emergent structure on a budget.** v1 is 92% frozen; most
  interesting-looking large patterns would be frozen residue. Scale is not
  the bottleneck (see Search frontier).
- **Questions requiring meaning or task performance.** Nothing here
  computes a task, and a task imposed from outside would be steering.

## 6. OBSERVABILITY

Exact:
- the full state of every site at every tick (deterministic replay from
  seed + parameters + lattice bytes);
- every write proposal, contest and winner (observer side channel);
- twin divergence: which sites differ, with locality checked every tick;
- adjacency generation (a lower bound on causal depth) and, on demand,
  counterfactual single-parent causal generation
  (`Aether/AETH-03/PROPAGATION_ASSAY_AUDIT.md`);
- energy accounting to the unit (a closed identity, tested).

Ambiguous or open:
- joint causation (two differences needed together) -- rare (2 in 2,793
  audited events), assigned conservatively;
- "function": nothing in Aether's observatory can say a structure does
  something useful, only that it causes differences;
- anything spatially distributed and informational rather than resource-
  routing, which the current assays were not built to see
  (AETH-02 closing report s6).

## 7. KNOWN PHYSICS (established, with evidence)

For B-balanced `aeth01.v1` (write cost 1, maintenance 1, replenishment 8
at 1/8, perturbation 0.1), each item intervened on or preregistered:

- **The bulk goes stationary by ~2,500 ticks** and is ~92% frozen over any
  64-tick window (AETH-02 H1b; stationarity control at 10,000 ticks).
- **Without injected perturbation the substrate almost stops:** ~42% of
  template change vanishes at once, ~94% by +500 (H4, 3 seeds); ~93% of
  template bytes never change again (rcv path probe).
- **Edges end mostly because their source runs out of energy (89%).** Long
  edges exist only where a neighbour keeps feeding energy; cut the supply
  every tick and they end (H2-X2: 0.39x sham).
- **Cycles are 0.37x a matched random graph**, the deficit carried by two
  field mechanisms: opcode overwrite (deterministic) and arg1 perturbation
  re-picking the field (the K2 mod-5 property; tested).
- **A one-bit difference stays within ~1 site**, with or without injected
  perturbation, for 500 ticks and for 10,000 (E-005).

Of the single-change laws (PHYSICS_DESIGN_01-02): `hys`, `chg`, `cnd`,
`str`, `mov`, `m4` do not propagate and several freeze further; `add`
turns redundant writes into counting (83% constant-step) and stays local;
`rcv` ("a written site fires once") propagates ACTIVATION TIMING along its
own relay through inert matter, weakly without noise, on a frozen map --
a calibration law (RCV_REINTERPRETATION). Pairwise combinations and the
content-forwarding control are in PHYSICS_DESIGN_03 s5.

## 8. SEARCH FRONTIER

Explored: the neighbourhood of one baseline law (B-balanced `aeth01.v1`)
by single rule changes to each tick phase (decode, emit, arbitrate,
commit, settle), three pairwise combinations around the one propagating
rule, one content-forwarding control; one parameter regime; 128^2-512^2;
horizons to 10,000 ticks.

Untouched, and large:
- **Parameter space.** Every result is one energy regime. Write cost,
  maintenance, replenishment and perturbation rate were never varied as
  experiments; the frozen-medium result may be a property of B-balanced
  energy, not of the law.
- **Initial conditions.** Only unstructured sparse soups. No seeded
  structures, no gradients, no boundaries.
- **Rules that change the medium.** Every law so far leaves ~93% of the
  template frozen without noise; the frontier question (TH-009) is a law
  whose own dynamics keep rewriting the medium without being noise or
  counting.
- **Asynchronous or multi-site rules**, and the candidate families rejected
  at AETH-01 design (reaction automata, mobile particles), which were
  never built.

## 9. RUNTIME

- CPU (NumPy): a 128^2 twin tick about 0.012 s alone on a laptop core;
  256^2 about 0.05 s; 512^2 about 0.3 s. Peak memory per unit 39 MB (128^2
  assay slice) to 66 MB (256^2 long-horizon). Memory-bound at 512^2: more
  than ~3 concurrent jobs on one laptop slow each other ~10x.
- GPU (CuPy kernel, bit-exact vs the CPU oracle on real A40 hardware):
  16384^2 = 268M sites at 7.42 s/tick, 113-128 bytes/site.
- Remote CPU: a RunPod L4 host exposes 48 vCPUs; 14 units in parallel in
  about 2 minutes (scout), 10,000-tick 256^2 units in about 10 minutes.

## 10. DEPENDENCIES -- what genuinely must be reachable

- For science units: Python >= 3.11 and NumPy (1.26 and 2.4 verified
  bit-identical). Nothing else. No network, no database, no GPU.
- For pinned remote execution: read access to the public repository at a
  commit (GitHub raw).
- For GPU flights: CuPy on the pod, and a RunPod key -- held only on
  BUCKKEEP today (an operator policy question, RUNPOD_ENGINEERING_04).
- For coordination only: comms on M1 (EW_DB_HOST=192.168.1.202). Aether's
  science never reads it.

## 11. PORTABILITY -- BUCKKEEP is the control host, not a requirement

BUCKKEEP (an i7-1260P laptop) is where the Aether seat and its worktrees
live and where the RunPod key sits. Nothing in Aether's science requires
it: the same unit ran bit-identically on BUCKKEEP (Windows 11, Python
3.13.5, NumPy 2.4.3) and on two RunPod Linux hosts (Python 3.11.10, NumPy
1.26.3), 13 known-answer attempts, 0 disagreements. What ties work to
BUCKKEEP today: the RunPod key; worker nodes (ubu001/ubu002) are not
reachable from it (no SSH key); a registry lists Aether's host as M2,
which is wrong.

## 12. CROSS-POLLINATION

Into Aether:
- **Archaeon's causal-provenance contract discipline (its CAUSAL_LINEAGE_CONTRACT, legacy name)** (adapters frozen before
  native results are read; a FALSE_FRIENDS catalogue). Aether has its own
  false friends from this week -- generation depth is not reach; counting
  is not change; activation timing is not content; a forced intervention is
  not a falsifier -- and should keep them as a catalogue.
- **Cosmos's sealed holdouts**: Aether preregisters thresholds but not
  holdout seeds; sealing seeds before a verdict would close a remaining gap.
- **Ananke's CUDA-graph finding** (eager GPU stepping is launch-bound; graphs
  8-11x faster, RUNPOD_ENGINEERING_04): directly applicable to Aether's GPU
  kernel before any GPU campaign.

Out of Aether:
- **The one-bit twin with checked locality and counterfactual parents** is
  a general causal instrument for any deterministic engine with a local
  update (BEE, NPE and the Z80 machines are deterministic; locality there is
  not spatial, so the "neighbour" becomes "instruction that read the byte").
- **The known-answer lane** (expected results derived from committed
  evidence, attempts compared by result hash across hosts) is a reusable
  determinism and portability check for any engine.
- **The RunPod platform** (now flying another seat's suite unmodified).

Kept distinct: Aether's lens only works because the physics is small,
exact and local. Importing program-level concepts (individuals, evaluation scores)
would erase what it is for.
