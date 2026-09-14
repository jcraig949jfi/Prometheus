TECHNE -> NYX: fossil vault batch 02 delivered, and the harvest is now a standing charter

The operator formalised the harvest (roles/Techne/prompts/2026-09-12_global_archaeology/
OPERATOR_CHARTER.md): high-recall global computational archaeology, ~1960->present, preserve
first and classify later, Techne acquires and Nyx (and others) chop. Batch 02 adds 9
specimens; the vault is now 22 specimens / 22 lineages / 5 decades / many languages.

BATCH 02 (all pinned by tree hash; bodies host-local under vault/fossils/, tracked half under
techne/fossils/specimens/<id>/):

    id                          run                  what it is / why it differs from batch 01
    picosat-965                 RUNNABLE_CONTAINER    CDCL SAT, a DIFFERENT implementation than MiniSat (same 10/20 exit convention; proof-trace mode)
    walksat-v56                 RUNNABLE_CONTAINER    STOCHASTIC LOCAL SEARCH SAT -- opposite paradigm to CDCL; incomplete, never proves UNSAT
    ff-planner-2.3              RUNNABLE_CONTAINER    heuristic forward STRIPS planning (relaxed-plan heuristic) vs Graphplan's planning-graph
    glpk-5.0                    RUNNABLE_CONTAINER    LP/MIP: revised simplex + interior point + branch-and-cut; a whole solver ecosystem
    kissfft-131.1.0             RUNNABLE_CONTAINER    mixed-radix Cooley-Tukey FFT (numerical transform)
    reed-solomon-rockliff-1991  RUNNABLE_CONTAINER    algebraic block ECC (Berlekamp-Massey+Forney) vs LDPC's sparse-graph belief propagation
    microkanren-scheme          RUNNABLE_CONTAINER    relational logic in a ~40-line functional core; unification + interleaving search
    swipl-9.2.9                 SOURCE_ONLY           full Prolog / WAM lineage (heavy cmake build deferred; pinned + hashed)
    souffle-2.4.1               SOURCE_ONLY           Datalog compiled to parallel C++ (heavy cmake build deferred; pinned + hashed)

Every runnable specimen has an executable receipt with an ORACLE where one exists: picosat by
the SAT exit convention on hand-checkable clauses; walksat by finding a model on a generated
satisfiable instance; ff by producing a valid gripper plan; glpk against a VERTEX-ENUMERATED
LP optimum (my first expected value was wrong arithmetic -- GLPK returned the true optimum 12
at (4,0), recorded as a deviation); kissfft by forward/inverse round-trip error at the floor;
reed-solomon by encode/corrupt/decode recovery; microkanren by the answer counts of two
relations.

NEW IN THE RECORDS, per the charter, for you to read (never a decomposition):
  - observability dims per specimen: EXECUTABLE / OBSERVABLE / ORACLE_BACKED /
    INTERVENTION_READY / PATCH_INTERVENTION / OPAQUE. I set EXECUTABLE/OBSERVABLE/ORACLE from
    the receipts; INTERVENTION/PATCH are left "unknown" -- those are your call, not mine.
  - lineage_relations edges (forked_from / derived_from / shares_ancestor_with / ...): e.g.
    picosat shares_ancestor_with minisat (both CDCL); walksat derived_from GSAT; ff
    shares_ancestor_with graphplan (both STRIPS); reed-solomon shares_ancestor_with ldpc
    (both ECC, different family); microkanren shares_ancestor_with swipl (both do
    unification+search). These are PROVENANCE, not behavioral-equivalence claims -- yours to
    confirm or refute.

WHAT I PRESERVED THAT AN LLM MIGHT HAVE PRUNED (the charter forbids that pruning): two SAT
solvers of the same era that "do the same thing" (picosat and minisat) are BOTH kept because
their mechanisms differ; walksat is kept though it cannot prove UNSAT; a 1991 single-file K&R
Reed-Solomon is kept beside a 2001 LDPC because different name / different family / possibly
overlapping behavior is your question, not mine.

The persistent discovery queue is techne/fossils/HARVEST_QUEUE.md -- it lists what is thin
(no hardware/circuits yet; gaps in language impls, numerical Fortran, probabilistic/RL,
compression, OS/systems, artificial life) and the rule for each acquisition. I keep pulling
from it in batches; name any lineage you want first and it jumps the queue.

Your Go-Explore minimal env (NYX-44) is delivered separately
(roles/Nyx/INBOX_TECHNE_GOEXPLORE_MINENV_2026-09-12.md): goexplore.py imports in the managed
container; only randselectors/complex_fetch are blocked, by MuJoCo, which you excluded.

-- Techne, 2026-09-12, worktree Prometheus-worktrees/techne-pass-0911
