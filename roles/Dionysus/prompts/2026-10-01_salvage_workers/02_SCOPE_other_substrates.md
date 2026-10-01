# Scope 2: non-program substrates and designed learners

Slots to fill: PN, the plastic network (RSE_ARCHITECTURE.md 6.3); the open
substrate arms (6.4: function chemistry, lattice dynamics, message-passing
media, tensor-network organisms); and designed organisms that could serve
as positive controls for COMPOSE and RECURSE (a library learner).

Requirement areas to read: section 1; ORG-01 to ORG-09; DEV-01 to DEV-07;
XFER-03, XFER-07; COMP-01, COMP-03; REPR-01.

Components:

1. Ananke's packet-tensor engine (PTE): the substrate itself (sites running
   one shared integer program, packets summed per channel), the CUDA tick,
   the separately written CPU oracle. Dossier: tantalus/seats/Ananke.md.
   Code: prometheus/ananke/. (Its instruments lens.py and the Wave-2
   certification stack belong to scope 5; mention them only where the
   substrate depends on them.)
2. Aether's byte-copy lattice (aeth01): 5 uint8 fields per site, energy,
   law variants, CPU/NumPy/CuPy implementations. Dossier:
   tantalus/seats/Aether.md. Do not open credentials.py or secrets.py.
3. Ares's graph organisms (up to 17 nodes) and its batched GA. Dossier:
   sisyphus/seats/Ares.md. Code: ares/. (carriers.py belongs to scope 5.)
4. Ensorain's learners: the tensor-train class (ensorain/e0/tt.py) and the
   other bounded online regressors; the CSSR/HMM causal-state learners and
   the binary processes with exact Bayes (the "Even process").
   Dossier: tantalus/seats/Ensorain.md. Code: ensorain/.
5. Tyche's register-DAG lens programs and their evolution (lexicase, graft,
   fuse). Dossier: tantalus/seats/Tyche.md. Code: tyche/.
6. Theseus synth: rule programs on a 1-D field, exact genealogy, QD
   archive. Dossier: tantalus/seats/Theseus.md. Code: theseus/synth/.
7. Aphrodite's library-inheritance program synthesis: the fold DSL, the
   enumerator, anti-unification, escrow-metered search with paired common
   random numbers, transplant with shams. Dossier:
   tantalus/seats/Aphrodite.md. Code: roles/Aphrodite/engine/ and wherever
   else the dossier points. Do not open azure.env.
8. Any tensor-network code usable as an ORGANISM rather than a regressor:
   prometheus_math/tensor_train.py, symbolic_tensor_decomp.py,
   alien_circuitry CP/TT families. One sheet for the group.
9. Any network-like organism with lifetime plasticity anywhere in the tree
   (Hebbian, neuromodulated, structural). Search for it; the crawlers did
   not report one. Say how you searched.

For each, answer from the source: what is the organism (what adapts, what
is fixed); what state persists and for how long; is the physics integer and
bit-reproducible; is there an independent oracle; what is the throughput on
record; what does it cost to wrap it in one common organism protocol
(birth, step, snapshot, restore, state partition, cost).

Special question for Aphrodite: could its engine, as built, serve as the
DESIGNED POSITIVE CONTROL for the COMPOSE and RECURSE rulers (a learner
whose library growth cuts the cost of later acquisition), and as the
designed NEGATIVE (the same learner with its procedure frozen)? What is
fixed in it that would have to become mutable for the positive?

Special question for Ananke and Aether: these are the two existing
candidates for the "message-passing" and "lattice" open arms. Report
honestly whether anything in their record suggests a capability above
HOLD, and what a designed organism (a plant) for HOLD and ADAPT would look
like in each, if one exists already.
