# Nyx (Chop Shop) -- status report for external consumption

Date: 2026-09-12 ~14:45 UTC. Seat: Nyx, Custodian of the Chop Shop. Worktree nyx-base-role; all work on main.
Written at the Keeper's request at a break in the catalogue loop (after batch 11). The loop is STOPPED; nothing is running.

## 1. What this seat does

Two products, both on demand only:
  (a) ANATOMY: chop a piece of machinery into ORGANs (reusable mechanisms, delivered to Archaeon) and PRESSUREs
      (selection pressures, delivered to Vivarium). Nyx never builds a world for her own pressure, never proposes
      reassembly, never validates her own claims. This loop is CLOSED by ruling until a consumer creates demand.
  (b) CATALOGUE (Keeper directive 2026-09-12): a searchable catalogue of the smallest computable algorithmic bits,
      classified BEHAVIOURALLY so that a strange solution seen in an organism can be matched against known bits
      WITHOUT knowing any name. This is the loop that ran today. Location: nyx/catalog/.

## 2. Catalogue state (numbers copied from the ledger, nyx/catalog/LOOP_LOG.jsonl and the bit files)

  bits: 321  (grades: {'T1-LOCAL': 16, 'T2': 305})  -- T1 = read from code by Nyx; T2 = classified from a list line + standard knowledge
  named instances attached to bits: 520
  source 1: Wikipedia 'List of algorithms' (revid 1373672109): 917 entries -> {'PENDING': 242, 'BIT': 304, 'INSTANCE_OF': 199, 'NOT_A_BIT': 128, 'DEFER': 44}
  source 2: Wikipedia 'List of data structures' (revid 1370346734): 220 entries, all PENDING
  source 3: Techne fossil vault batch 01 (13 runnable/source bodies): recorded as a pointer only, nothing opened
  batches committed: 11; planted name-blind controls: 10/10 pass at every commit (controls_all_pass at every log row: True)
  signature recurrence groups: 19; explicit cross-lineage RECURRENCE_OF links: 25
  bits by verb: {'SEARCH': 79, 'TRANSFORM': 52, 'PREDICT': 29, 'ORDER': 17, 'SELECT': 14, 'PARTITION': 14, 'GENERATE': 13, 'COMPRESS': 11, 'BOUND': 11, 'REPAIR': 11, 'SCHEDULE': 10, 'DETECT': 10, 'SAMPLE': 10, 'VERIFY': 9, 'REMEMBER': 7, 'ACCUMULATE': 7, 'SYNCHRONIZE': 7, 'ALLOCATE': 4, 'COMPARE': 4, 'CORRECT': 2}
  lineages touched (top 12): {'search': 80, 'scientific software': 72, 'numerical methods': 63, 'planning': 55, 'symbolic reasoning': 48, 'optimization': 47, 'memory and retrieval': 27, 'automated mathematics': 24, 'network protocols': 23, 'error-correcting systems': 20, 'games': 19, 'computational geometry': 18}
  remaining pending sections in source 1: {'Computer science / Computer graphics': 44, 'Computational science / Statistics': 41, 'Information theory and signal processing / Digital signal processing': 37, 'Computer science / Quantum algorithms': 29, 'Computer science / Programming language theory': 21, 'Computational science / Physics': 13, 'Software engineering': 9, 'Combinatorial algorithms / General combinatorial algorithms': 8}

## 3. What a bit is, and how it is found

A bit record (schema nyx.bit/0) = one mechanism described in behavioural prose with NO algorithm name in it, plus a
10-axis signature: verb, in_geometry, out_geometry, order_req, metric_req, state_req, control, guarantee, strategy,
iteration; plus cost, requires, fails_when, lineage tags, named instances, related links, sources, grade.
Search (nyx/catalog/search.py) takes a query over the axes and behavioural words; it REFUSES name/provenance keys.
Discipline: a named algorithm becomes INSTANCE_OF when its mechanism is already catalogued; headers/problems are
NOT_A_BIT; unknowns DEFER; a vocabulary noun is added ONLY when a planted control fails (changelog + backfill);
bits with identical signatures are kept as a NAMED recurrence group, never flattened.

## 4. What the catalogue has found (the product, per the directive)

Cross-lineage recurrences -- the same behaviour under different names in different fields -- recorded as links:
  - fewest-options-first: knight's-tour move choice = exact-cover column choice = sparse-matrix minimum-degree ordering
  - halve the bracket: binary search = root bisection = unimodal bracketing (one signature group, two lineages)
  - one-variable-at-a-time sweep: Gauss-Seidel = min-conflicts repair = Gibbs sampling (stochastic) = mesh smoothing
  - accept-by-ratio: Metropolis acceptance = simulated-annealing acceptance
  - power iteration = stationary-score propagation (PageRank-type)
  - completion: Groebner-basis pair reduction = rewrite-rule critical-pair completion = lazy constraint addition (SMT)
  - leading-term cancellation: polynomial division = integer long division
  - guess-and-square: output-sensitive hull = iterative deepening
  - farthest-point split (Quickhull) = pivot partition (quicksort); advance-the-smaller: rotating calipers = merge-join
  - sweep with an active order: segment intersection = Voronoi construction
  - polynomial evaluation as fingerprint: rolling-hash pattern match = one-time MAC = CRC remainder check; LFSR = CRC
  - threshold secret sharing: polynomial evaluations = hyperplane intersection
  - key-scrambled permutation walk (stream cipher) = shuffle-by-swaps
Full list: grep '"rel": "RECURRENCE_OF"' under nyx/catalog/bits/ (25 links).

## 5. What is NOT claimed

  - The 10 planted controls were written by the same author who classified the bits. Passing them is a fit
    statistic, not a capability estimate. Name-blind retrieval on an INDEPENDENT query set has not been tested.
    An external reader can test it: write a behavioural description of a mechanism you know, run
    `python -m nyx.catalog.search` with axes/words only, and see whether the right bit ranks first.
  - T2 bits are classified from a list line plus standard knowledge, not from code. Errors of mechanism are
    possible; each T2 record names its list source and revid so it can be checked.
  - Recurrence groups are honest collisions of the 10-axis signature; some pairs differ on an axis the
    vocabulary does not carry (e.g. round structure of block ciphers). They are NOT vocabulary defects until a
    consumer query needs to separate them; that failed query is the licence to extend the vocabulary.
  - No organ has been CONSUMED by any Prometheus seat. The Chop Shop is PROMISING and UNDER TEST, nothing more.

## 6. Anatomy ledger (unchanged today except one executed control)

  6 specimens chopped (Lean/mathlib simp, Hypothesis shrinker, Diomedes census [negative chop], MAP-Elites,
  DreamCoder, Go-Explore). 18 organs delivered, 1 attempted, 0 consumed; 8 pressures delivered, 0 operationalized.
  NYX-44 (Go-Explore c04 representation-selection organ): Techne pinned the source (SOURCE_ONLY, comms #203); the
  pre-frozen controls were run unaltered -> CANNOT_INSTANTIATE (missing dependency at import, no shim). c04 stays
  specified / untested / no consumer. A minimal managed environment pin is requested (#204). Holds by ruling:
  c07 INTERFACE_INSUFFICIENT (four reopen conditions on an EXISTING consumer), c03 held, c01 held untested,
  Proteus/Diomedes halves HELD. No more anatomy until a consumer creates demand.

## 7. Open communications

  #176 (Vivarium, rewriting substrate), #189/#190/#192 (Proteus/Diomedes halves held), #197 (Archaeon routing
  repair), #198, #202 (N3 pressure to Vivarium+Archaeon), #204 (Techne env pin). Returns are processed before
  any batch when the loop runs.

## 8. How to use it

  status:  python -m nyx.catalog.loop status
  search:  python -m nyx.catalog.search  (behavioural query; provenance keys refused)
  gate:    python -m nyx.catalog.controls  (planted controls + validator + recurrence groups)
  a bit:   nyx/catalog/bits/<source>/<id>.json ; vocabulary nyx/catalog/schema.py (+ VOCAB_CHANGELOG in README)
  loop:    stopped. Restart = the /loop prompt in roles/Nyx/STATUS.md; one batch per wake, checkpoint every 3.

## 9. Next when the loop resumes

  batch 12 = computer graphics / DSP / statistics (pending 44 / 37 / 41), then quantum, programming-language
  theory, physics; then the data-structures list (220). Checkpoint due after batch 12. If #204 lands RUNNABLE,
  rerun the frozen NYX-44 controls unaltered and let them kill c04 if they can.

-- Nyx
