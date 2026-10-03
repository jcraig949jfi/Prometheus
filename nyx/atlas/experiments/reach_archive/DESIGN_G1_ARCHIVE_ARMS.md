# DESIGN: separating the archive arm's bundled effects (Atlas G1 follow-through)

Nyx[gandalf-d1f90ae1], 2026-10-03. Operator directive 2026-10-03, queue item 6: "turn the G1 critique into the
cheapest discriminating design you identified ... separate the archive arm's bundled effects ... a design/patch is
sufficient initially; do not launch an expensive campaign."

**DESIGN ONLY.** Nothing here has been run on the reach world. The reference implementation (archive_arms.py) is
exercised only by toy-landscape controls (nyx/tests/test_reach_archive_arms.py).

## 1. The problem (from the attack, B1)

Atlas G1's archive arm S4 differs from the chain searches S1-S3 in three ways at once:

1. it RETAINS every cell's elite;
2. it SELECTS parents by visit counts, which favours rarely visited cells;
3. it ACCEPTS a child that lands in a new cell.

S4's detachment index is zero by construction. So "S4 beats the chain" cannot be attributed to detachment, or to
any one of the three.

## 2. The ladder

There are three new arms, each ONE factor away from its neighbour. Every adjacent contrast isolates one ingredient.

| arm | archive | parent choice | child admitted if | contrast | what it isolates |
|---|---|---|---|---|---|
| chain | none | the current parent | f(child) >= f(parent) | (existing reach.py 'neutral') | -- |
| X1 | kept | the elite of the best-scoring cell | f(child) >= f(parent) | X1 vs chain | RETENTION |
| X2 | kept | count weight 1/sqrt(1 + times chosen) | f(child) >= f(parent) | X2 vs X1 | RARELY-VISITED SELECTION |
| X3 | kept | as X2 | as X2, OR the child's cell is EMPTY | X3 vs X2 | NEW-CELL ACCEPTANCE |

- An admitted child replaces its cell's elite iff it is at least as fit, or the cell is empty.
- X3 is S4, the full bundle.
- The existing reach.py strict and margin regimes stay as further references.

**What X3 really adds. This is a correction the toy controls forced, before any real run.** With ">= parent"
acceptance, X1 and X2 ALREADY admit neutral moves, and a neutral move into an empty cell founds that cell. The
toy test is test_on_a_flat_plateau_ge_acceptance_already_admits_new_cells.

So on a flat plateau, X3 = X2. X3's own contribution is admitting a STRICTLY WORSE child into an empty cell, i.e.
crossing a deceptive valley. The toy control is test_new_cell_acceptance_is_what_crosses_a_deceptive_valley.

Consequence for interpretation: "X3 > X2" means the target needs downhill steps in behaviour space. It does not
mean that zero-reward plateaus were the barrier.

## 3. Cells

The harness's state is the program, so a cell must be a behaviour descriptor that is computable without new
instruments. The proposal:

- **C-BEH:** the per-type (novel, repeat, probe, other) correct counts on the training block, i.e. the full
  `counts[:, 1]` vector that wm_mini.eval_life already accumulates.
- **C-FIT:** fitness bins, Atlas's S5.
- **C-GENO-HASH:** a genotype hash with a bucket count matched to C-BEH's realised cell count. This is the
  structure-free baseline (attack M2), not a must-fail.

Run the ladder under C-BEH first. Add C-FIT and C-GENO-HASH only if the C-BEH ladder separates.

## 4. Where and how much

- **Targets:** the p1_slice reach world, T5. Same distances d = 1, 2, 3, 8; 24 lineages per cell; budget 200,000
  proposals; the same SELECTION and SEALED certification.
  - Reason: the existing grid ran in 425.8 s (RECEIPT_reach.json), and it is the only target with a census-able
    machine (G6).
- **Cost:** 3 arms x 4 distances x 24 lineages. The reference implementation is pure Python; a numba port of
  `run_lineage` is the one engineering step before a real run. Estimated tens of minutes on 8 cores once ported.
- **Power:**
  - 0/24 vs 6/24 separates at Fisher p = 0.022; 0/24 vs 3/24 does not (p = 0.234).
  - So a contrast is read only where one arm reaches at least 6/24.
  - Every 0/24 is reported as an upper bound (below 3/24 at 95%), never as "impossible".

## 5. Decision rules (to be frozen in a preregistration before any run)

| reading | conclusion |
|---|---|
| X1 > chain | retention helps on this target ("detachment" in the population-genetic sense) |
| X2 > X1 | rarely-visited selection helps beyond retention |
| X3 > X2 | admitting worse-but-new behaviour helps: the target sits beyond a deceptive valley |
| every arm ~ chain at every d, AND the G6 census shows solutions exist within the budget's coverage | a search fact: none of the three ingredients is the barrier |
| every arm ~ 0 AND the census shows a needle | a landscape fact; stop comparing searches there |

## 6. What this does not do

- It does not test Go-Explore's own mechanism (no MDP trajectory is re-traversed; attack B2).
- It does not run anything.
- It does not modify reach.py, which belongs to the FABLE-5.1 prototype. The arms live in Nyx's lane and would call
  reach.py's knock_out, mutation hash and certification unchanged.

## 7. Owed before a run

1. The operator's go.
2. A numba port of `run_lineage` with a differential test against the reference.
3. A preregistration that freezes section 5 together with the seeds.
