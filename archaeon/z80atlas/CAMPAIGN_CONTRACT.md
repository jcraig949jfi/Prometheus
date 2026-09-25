# Z80 x ATLAS COMBINATORIAL CAMPAIGN -- CONTRACT (Archaeon build of the NESTOR directive, 2026-09-19)

Frozen 72-hour autonomous producer/consumer search. NO HITL. NO LLM IN THE LOOP. NO POST-RESULT THRESHOLD CHANGES.
NO NEW EXPERIMENT SEMANTICS DURING EXECUTION. The scheduler refuses to run if the grammar digest changes
(GRAMMAR_FROZEN.json vs grammar.digest()).

## What runs

- `vm.py`         Z80-like byte VM: 32 opcodes, any byte decodes; own tape [0,G), neighbour window [128,128+G), sandbox
                  elsewhere (writes counted as illegal, ignored). COPY primitive only in the `vmcopy` substrate. No multiply.
- `tasks.py`      tasks + accessibility manipulations as reward geometry (EXACT vs GRADED) and input regime (FORCED_READ vs
                  ANSWER_BEFORE_READ); witnesses and two known replicators (positive controls).
- `engine.py`     one run = (spec, seed): topologies (well_mixed, grid_vn torus, graph, ring_soup, niches), migration
                  policies, resources, env dynamics (nonstationary, local_shift, env_mutate, env_coevolve), reproduction
                  physics (EXTERNAL, ENDOGENOUS_COPY, ENDOGENOUS_PARTIAL, OVERWRITE, CONSTRUCTIVE, PAIR_EXECUTION),
                  pressures (up to two), mutation operators, init (random / seeded replicator / transplant), telemetry,
                  serendipity snapshots, damage ruler, integrity assertion (no runner-provided birth under endogenous physics).
- `grammar.py`    the frozen factor grammar, FROZEN constants, constraints, sparse sampler, matched controls, one-factor
                  mutation, crossover of factor vectors, positive controls and their verdict rules, promotion weights.
- `scheduler.py`  wall-clock stages EARLY (<16 h) / MIDDLE / LATE (>=60 h); 24 worker processes; exploration floor 0.30;
                  promotion = allocate (fresh seed + one-factor mutant + combine, each with matched controls);
                  retirement after 3 signal-less runs; LATE verification (fresh seeds, matched controls, transplants:
                  same / physics_swap / world_swap / environment_swap); STATUS.json <= 2 KB; resume from RUNS.jsonl.
- `packet.py`     CAMPAIGN_PACKET.md (ASCII) + PACKET.json at the end. No interpretation.

## Reproduction is endogenous where declared

Under any ENDOGENOUS physics a descendant exists only because the organism wrote bytes into the neighbour window
during its own execution (>= 90% of G for COPY/OVERWRITE/CONSTRUCTIVE/PAIR; >= 1 byte for PARTIAL, rest randomised).
The runner never copies for it; `engine.run` asserts births == endogenous births or raises (GLOBAL integrity halt for
that run). Copy noise applies to written bytes; a background mutation keeps endogenous populations evolving.
EXTERNAL physics is the matched control (tournament or uniform parent choice, replacement 15%/epoch, equal step cap).

## Mechanical signals -> flags -> allocation (frozen weights in grammar.FROZEN)

spontaneous_replication (5), moat_advantage (6: treatment crossed, its reproduction control did not), moat_crossed (2),
compression (2), ruler_gain (2), new_arch_events / coexistence / longevity / transport / env_lineage /
persistence_over_control (1 each), exploit (0). Promotion threshold 3. Promotion means MORE EXPERIMENTS, never a claim.
Special results are appended to CAMPAIGN_STATE.high_value immediately (spontaneous replication; exploits).

## Anti-cheat (record, do not patch)

- Sandbox writes counted; validation state is unreachable by construction (inputs/outputs are VM ports).
- Inputs are fresh per (run, epoch, cell): deterministic-input exploits are structurally impossible; `ruler.fresh16`
  records generalisation to 16 fresh cases.
- Neighbour dependence (competence collapses with a zeroed neighbour) is an INTERACTION, recorded per organism
  (DEPENDENTS.json, specimen frozen), not an evaluator exploit. It is the "execute / read your neighbour" phenomenon.
- Nontermination: step cap; cap_hit_frac recorded.
- ANSWER_BEFORE_READ crossings count only if the organism also solves fresh forced-read cases (guessing is the moat, not
  the crossing).

## Blocked factor levels (recorded, not silently dropped)

Nestor tape / tree organisms: BLOCKED_MISSING_CAPABILITY (not importable in this worktree). GraphWorld-like structure
is the `graph` topology (fixed sparse random interaction graph, degree ~3).

## Observatory (per run under campaign/runs/<family>/<run_id>/)

SPEC.json (full frozen configuration, seed, factor vector, parents, scheduler reason), RECEIPT.json (signals, wall),
TELEMETRY.json.gz (per-epoch rows, birth/overwrite/migration/first-crossing/extinction events, env changes),
SNAPSHOTS.json.gz (adaptive population snapshots incl. standing variation before env steps; final population with
genome, lineage, parent, niche, score), FORENSICS.json (ancestry of first-crossing organisms), DEPENDENTS.json,
EXPLOITS.json. ATLAS_INDEX.jsonl: one line per run (family, factors, signals, path) for Atlas ingest.

## Launch

`run_campaign.bat` under Windows Task Scheduler (task Z80Atlas) restarts `--resume` until CAMPAIGN_DONE.json exists; the
72 h clock is absolute from `--start`. Token cost during the run: zero. Check-ins read STATUS.json only.
