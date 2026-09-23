# PREREGISTRATION -- the ancestry ground-truth ruler (instrument before specimen)

Author: Harmonia[gandalf-6cd1348b] (M3), 2026-09-18. Operator (refinery
directive s3): "Harmonia builds the ground-truth ruler it already proposed:
recorded ancestry -> deliberately degraded history -> reconstruction ->
measurable loss. That ruler can then be reused on POET, Tierra, Nestor and
eventually Prometheus itself." Amendment 2 C11: the instrument must survive
controls that could reveal instrument failure before any fossil is read
with it. No Avida .spop exists yet (Techne TECHNE-105); this file
preregisters the ruler on SYNTHETIC ground truth whose every edge is known
by construction, so that when the .spop lands the ruler is already
calibrated and the specimen is not the first thing it ever measured.

## 0. Objects

    POPULATION RECORD (the ruler's input; the .spop adapter maps onto it)
        organisms: id, parent_id (or null), birth_time, genome (string over an
        alphabet), alive_at_end (bool), plus any fossil-specific fields carried
        through untouched
    GROUND TRUTH        the full record: every organism ever born, with its parent
    DEGRADATION         a named, parameterised loss of history applied to the truth
    RECONSTRUCTION      an inference of parent edges from what the degradation left
    LOSS                the measured distance between the reconstruction and the truth

## 1. The synthetic world (fixed by seed; nothing about it is tuned to the ruler)

Asexual population, N = 200, G = 60 generations, genome length 50 over a
26-symbol alphabet (Avida's instruction-count shape, not its semantics).
Per generation: each organism's fitness is f = 1 + 0.02 * (number of sites
equal to a fixed target string) (mild directional selection so lineages
sort); N children are drawn by fitness-proportional sampling; each child
copies its parent's genome with per-site mutation probability mu = 0.02
(substitution) and, with probability 0.01, one insertion or deletion.
Every birth records (id, parent_id, generation, genome). Organisms live one
generation (non-overlapping), so "alive_at_end" = generation G. Seeds:
world 20260918; three replicates (20260918, 20260919, 20260920) so that a
loss curve has an interval. World size is enough to yield extinct branches
(most lineages die) -- the phenomenon the operator wants measured.

## 2. Degradations (each applied to the ground truth; each is a HISTORY_MODE analogue)

    D0  NONE                     the full record (HISTORY_MODE recorded_directly)
    D1  ENDPOINTS_ONLY           only alive_at_end organisms, genomes, no parent ids
                                 ("history compressed into endpoint organisms")
    D2  ENDPOINTS_PLUS_ANCESTORS every ancestor of a surviving organism kept WITH
                                 parent ids; extinct branches dropped (the .spop-with-
                                 ancestry shape: what Avida keeps)
    D3  SUBSAMPLED(k)            every k-th generation kept in full (k in 2, 5, 10), no
                                 parent ids across the gaps ("selectively banked")
    D4  PARENT_IDS_DROPPED       every organism kept, parent ids removed (genomes and
                                 birth times only)
    D5  NOISY_IDS(p)             every organism kept, a fraction p of parent ids replaced
                                 by a random other id (p in 0.05, 0.10, 0.25) -- a
                                 corrupted rather than missing history

## 3. Reconstruction (one method, fixed; others may be added as descendants)

PARSIMONY-NEAREST-ANCESTOR: for each organism without a recorded parent,
the inferred parent is the organism with the smallest Levenshtein distance
among those with strictly earlier birth_time (ties: the most recent; if
birth times are unknown, ties: the one with the smaller id). Recorded
parent ids, where present, are kept as edges. Nothing else is inferred (no
invented intermediates).

## 4. Loss measures (against the truth restricted to organisms the degradation retained)

    edge_recall        fraction of true parent edges (both endpoints retained) that the
                       reconstruction reproduces exactly
    edge_precision     fraction of reconstructed edges that are true
    ancestor_recall_k  for each retained organism, fraction of its true ancestors within
                       k generations that are reachable in the reconstruction (k = 1, 5, all)
    depth_error        mean |inferred depth - true depth| over retained organisms
    extinct_recoverable fraction of extinct organisms (true) that are retained at all
                       (0 by construction under D1/D2; reported so the loss is visible)
    mrca_error         for 200 random pairs of survivors, |inferred MRCA generation -
                       true MRCA generation|

## 5. Controls, run first; the ruler is not calibrated until all pass

    C-CHEAT   reconstruct from D0 (all parent ids present) -> edge_recall = precision = 1.0
              exactly, depth_error 0, mrca_error 0
    C-POS     D5 with p = 0.10 -> edge_recall <= 0.95 and the reconstruction's disagreement
              with the recorded ids is concentrated on the corrupted 10% (>= 80% of the
              corrupted edges are flagged when the recorded parent is farther in edit
              distance than the nearest earlier organism by >= 3)
    C-NEG     a population with NO reproduction (all organisms generation 0, no parents,
              distinct random genomes) -> zero edges inferred; edge_precision undefined and
              reported as NO_EDGES, never as 1.0
    C-ORDER   the same truth with organism ids permuted -> identical losses (the ruler
              must not read id order as time)

## 6. Predictions (instrument-level; the fossil predictions are the packet's)

    P1  D1 (endpoints only) has edge_recall < 0.5 in every replicate: from survivors'
        genomes alone, most parent edges are unrecoverable because most parents are
        extinct and absent.
    P2  D2 (endpoints + ancestors) has edge_recall = 1.0 among retained edges by
        construction, and extinct_recoverable = 0: the .spop-with-ancestry shape loses
        exactly the extinct branches and nothing else.
    P3  D3 loss is monotone in k (recall(k=2) > recall(k=5) > recall(k=10)).
    P4  D4 (genomes + birth times, no ids) has edge_recall in [0.6, 0.95]: parsimony
        recovers most edges at mu = 0.02 but not all (siblings and near-identical
        cousins are confusable). Band is wide; it is a calibration, not a claim.
    Any prediction outside its band is a finding about the ruler or the world, recorded;
    nothing here is adjudicative.

## 7. Adapters owed

    .spop (Avida SavePopulation)   when TECHNE-105 lands: columns id, parent ids,
                                   sequence, update born, num_units -> population record
    POET lineage                   optimizer id, parent_optim_id (from the log text),
                                   iteration -> population record (genome = env config)
    Prometheus / NPE receipts      lineage rows with parent references

Host: M3 (pure Python; Levenshtein in numpy; N x G = 12,000 organisms,
pairwise distances only against earlier organisms; minutes). Nothing from
this ruler enters a Soup record; it produces loss curves and the HISTORY_MODE
calibration for the pipeline.
