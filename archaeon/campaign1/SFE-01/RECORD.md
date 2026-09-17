# SFE-01 -- H0 FAILURE + COMPONENT EXCHANGE (record; directive IV shape)

## A. STARTUP

- experiment ID: SFE-01
- question: can residue from a prior search -- FAILURES (candidates that
  were tried and scored at the floor) and COMPONENTS (genome segments of
  candidates that scored above the floor) -- improve a LATER target
  search, when the residue is exchanged as SFE artifacts?
- starting commit: 3a34d207a (main), worktree archaeon-wse-2026-09-16
- services required: SFE engine v2 at https://192.168.1.191:8811
  (eng_906356f7, schema 8) for artifact exchange + lineage; no Vivarium,
  no PEW write (read-only PEW not needed).
- datasets/artifacts required: none pre-existing; the source run
  produces them.
- world/specification: the WSE event-stream grammar (archaeon/wse,
  DESIGN_v0.1 s2) -- SOURCE world W1_d1 (K=1, D=1, delay 1, 8-bit values
  in v01; here 4-bit for a foothold) and TARGET world W2_K2 (K=2, D=1,
  ask all). The target is a different cell of the same grammar so that
  source residue is "compatible" (same input syntax) without being the
  target's answer.
- seeds: campaign seed 20260917; cell seeds 1,2,3; families train /
  heldout never overlap.
- frozen assumptions: Proteus VM + grammar unmodified (runtime hash and
  grammar hash in every row); selection loop archaeon.wse.evolve.run_cell
  as used in v01-v0.4; reward = exact match; no LLM.
- smallest runnable design (D-003): four cells x 3 seeds, N=200, G=60,
  E=16, 4-bit values. Cells:
    00  target search from random generation 0
    10  FAILURES only: a tabu set of source genotypes that scored at the
        floor in the source's final generation; any target child whose
        genome equals a tabu genome is re-drawn (one retry) -- the
        failure residue prunes, it never proposes
    01  COMPONENTS only: generation 0 = random genomes into which one
        4-16-word segment of a source elite (top-8 of the final
        generation) is spliced at a random aligned position -- the
        component residue proposes, it never prunes
    11  both
  Exchange path: the source run publishes two artifacts to the engine
  (kind cmp1.failures.v0, cmp1.components.v0; blobs = JSON) under world
  cmp1-sfe01-source; each target cell FETCHES its residue back from the
  engine by artifact id/hash before generation 0 and records a lineage
  edge target-world -> source artifact. If the engine cannot do a step,
  D-004 applies (standalone, ENGINE_PATH=false).
- primary measurement: held-out competence of the target elite at G=60
  (48 episodes), per cell per seed; main effects F = mean(10,11) -
  mean(00,01), C = mean(01,11) - mean(00,10); interaction I = 11 - 10 -
  01 + 00; reported separately (directive: keep combined gain and
  interaction conceptually separate).
- controls: 00 is the baseline; a RANDOM-residue control per residue
  type (tabu set of random genomes; components spliced from random
  genomes) so that "residue helps" is separable from "any perturbation
  of generation 0 helps" -- cells 10r and 01r, same seeds.
- assay capability: the v01 survey found W2_K2 reachable at E0 (0.5 = the
  last-value plateau) in 1/3 seeds at N=200 G=100; W1_d1 in 2/3. At 4-bit
  values footholds are cheaper. If 00 never leaves the floor in any seed
  the assay cannot detect help and the row is INCONCLUSIVE, not NEGATIVE.
- time budget: 6 cells x 3 seeds = 18 runs x ~2 min = ~40 min on 18
  procs; engine calls seconds. Well inside D-003.

## B. EXECUTION

- attempts: 1 (RECEIPT_attempt1.json, rows_attempt1.json; 100 s; RNG confound
  + inert failure channel + hash-format bug + 422 on failure records) and 2
  (RECEIPT.json, rows.json; 170 s; the disposition below). Both preserved.
- design as executed (attempt 2): 6 cells x 3 seeds; target N=200 G=60 E=16;
  source N=200 G=100 E=16; common random numbers across cells (D-007);
  failure residue = opcode-signature tabu (D-008), component residue = one
  2-4-instruction segment of an above-floor source genotype spliced into
  each gen-0 genome; random-residue controls 10r/01r with matched counts.
- time: startup 0.61 s; source searches 35.7 s (3 procs); publish 1.14 s;
  target worlds + 12 imports + 12 content fetches 3.64 s; 18 target
  searches 121.7 s (12 procs); 18 experiments + 18 observations 5.44 s;
  teardown 1.23 s; total 169.5 s. Resource: 21 searches x 200 x 16 x
  60-100 generations; ~4e8 VM ops.
- engine objects created: 1 session, 1 topology group, 7 worlds, 6 artifacts
  (3 failure sets, 3 component sets), 3 first-class failure records, 12
  imports (all origin IMPORTED, source lineage kept, bytes hash-verified),
  18 experiments (committed, spec sealed), 18 observations, 1 hypothesis.
  knowledge frontier of target_11: 6 available identities (3 seeds x 2).
- autonomous decisions: D-005 (substrate), D-006 (residue semantics), D-007
  (common RNG), D-008 (opcode tabu). Failures: attempt-1 422 on the failure
  route (L-006); hash-format mismatch in my check (L-009). Recoveries: both
  fixed in the harness and rerun; restart = full rerun (no resume path in
  the harness: every artifact was re-created; the engine's idempotency
  keys were not used -- L-012).
- repeated work: the three source searches were rerun in attempt 2 because
  the residue definition changed; unavoidable. The 12 imports and 18
  records were re-created although attempt 1's worlds still hold theirs
  (TERMINATED, append-only): the ledger now carries both attempts under
  different world ids, distinguishable by world name only (L-013).

## C. SCIENCE

- primary outcome (held-out competence, 48 episodes, W2_K2 4-bit; footholds
  = seeds with >= 0.5, the last-value plateau):
    cell   s1     s2     s3     mean   footholds  first-solved gen
    00     0.042  0.531  0.302  0.292  1/3        -, 59, -
    10     0.042  0.094  0.302  0.146  0/3        (tabu hits 0/49/0)
    01     0.542  0.531  0.250  0.441  2/3        18, 20, -
    11     0.542  0.531  0.083  0.385  2/3        18, 45, -
    10r    0.312  0.094  0.302  0.236  0/3        (tabu hits 2/30/23)
    01r    0.042  0.094  0.042  0.059  0/3
  main effects: F = -0.101, C = +0.194; interaction I = +0.090 (11 ~ 01);
  vs random controls: F - Fr = -0.090, C - Cr = +0.382.
- controls: 00 baseline; 10r/01r random residue with matched counts and
  the same splice/tabu mechanics (so genome-length and tabu-redraw effects
  are in the control); common RNG so 00 and a control with zero hits are
  identical trajectories (10r s1 differs from 00 s1 only after its 2 hits).
- assay capability: YES for components (00 found the plateau in 1/3, so the
  target is reachable; 01 reached it in 2/3 seeds 3-4x earlier than 00's
  one); MARGINAL for failures (the tabu fired 0-49 times per run; with 0
  hits the arm equals the baseline by construction -- s1 and s3 of cell 10
  are literally cell 00's trajectories).
- evidence: components -- WEAK POSITIVE (2/3 vs 0/3 random-segment control
  and 1/3 baseline; n=3; the source organisms the segments came from
  scored 0.0625-0.125 on W1_d1, i.e. at or just above chance -- the source
  never solved its own cell in 100 generations, so what transferred is not
  a solver fragment; possibly a structural bias of the segments, e.g.
  IN/OUT-rich opcode runs). Failures -- NULL/NEGATIVE (0/3; the only run
  where the tabu fired often, 10 s2, ended at 0.094 vs 0.531 for its
  common-RNG baseline; pruning opcode sequences that a near-chance source
  population failed with removes the very sequences a target needs).
  Interaction -- NOT ESTIMABLE at n=3 (11 = 01 in two seeds, collapses in
  the third).
- confounders: n=3 with bimodal outcomes; source residue quality
  unmeasured beyond the source elite reward; the 4-bit alphabet's chance
  floor 0.0625; genome length after splice (controlled by 01r).
- must NOT be claimed: that source components are "reusable machinery"
  (their sources did not work); that failures are useless in general
  (only opcode-signature tabu from a near-chance source was tested); any
  interaction sign.

## D. TEARDOWN

- procedure: terminate every cmp1-sfe01 world (7), read back state; no
  session close (client has no wrapper, L-001); client token kept for the
  campaign (archaeon/campaign1/config.local.json, gitignored).
- time: 1.23 s. Orphans: none (python.exe count back to the 4 baseline
  processes; the engine's worker queue was never used). Stale leases:
  none (no work claims). Temporary state: attempt-1 worlds remain
  TERMINATED on the ledger (append-only; correct); log files under
  D:/Prometheus-data/archaeon/cmp1-sfe01*.log. Next experiment starts
  clean: yes.

## E. BENCH IMPROVEMENT (ledger L-001..L-013)

BUGS: L-006 (failure route strict vs client passthrough); L-009 (digest
prefix mismatch, mine).
FRICTION: L-001 (missing client wrappers); L-004 (detached launch ritual);
L-013 (attempt distinguishable by world NAME only -- no attempt/run id on
the world).
MISSING TELEMETRY: L-007 (applied-count for every intervention/residue
channel; INERT flag); L-010 (residue quality: source elite reward and the
share of residue items that came from above-chance organisms should be
stamped on the residue artifact meta and refused below a floor).
AUTOMATION: L-004 launcher; L-011 (the whole lifecycle -- register,
session, group, 7 worlds, 6 artifacts, 12 imports, 36 records, teardown --
ran in 12.7 s of engine time with zero manual steps: this experiment's
engine side is already deterministic machinery; what is not is the
science-side residue definition).
TO MACHINERY: L-008 (rng_label separate from provenance branch; common
random numbers as the default for multi-cell comparisons); L-012 (use the
engine's Idempotency-Key on every POST so a rerun after a client-side
crash resumes instead of duplicating).
KEEP POLICY: what counts as a "failure" and a "component" (D-006/D-008)
and the solve threshold (0.5) -- scientific choices, not machinery.
MISSING FAILURE STATE: L-007 (INTERVENTION_NOT_APPLIED for client-declared
channels); "source did not solve its cell" as a typed precondition
failure (L-010).
MISSING RECOVERY: no resume: a crash after publish re-creates worlds and
artifacts (L-012).
PORTABILITY: L-002 (M1 defaults).
OBSERVABILITY: L-003 (idle-engine alarm); L-013.

## F. LANDSCAPE / GRADIENT NOTES

- The binary "foothold reached" hides a gradient that IS measured in the
  rows but not summarised: first_solved_gen (18, 20, 45, 59) is a speed
  landscape; trace_best per generation shows plateaus at 0.25-0.31 (the
  1/K last-value shelf on W2_K2) before the 0.5 plateau. Telemetry to add:
  time-to-plateau per plateau level (0.25, 0.5) per cell, not only the
  final competence.
- tabu_hits per generation (recorded only as a total) would show WHEN the
  failure channel bites -- early (gen-0 diversity) or late (near the
  plateau, where it may prune the solver's neighbourhood: 10 s2 collapsed
  exactly there).
- Components: which segment kinds were spliced into the organisms that
  reached the plateau (opcode composition of the winning segments vs the
  pool) would turn "components help" into a landscape over segment
  content; not computed here (would require the elite's ancestry, which
  the loop records but this harness did not keep).
- Dead region: cell 10 with 0 hits is not an experiment; the tabu
  mechanism needs a hit-rate landscape over signature granularity (exact
  genome -> opcode sequence -> opcode multiset) before "failures" can be
  said to transport at all.

DISPOSITION: COMPLETE (attempt 2). Science: components WEAK POSITIVE at
n=3 with the random-segment control at 0/3; failures NULL/NEGATIVE;
interaction not estimable. Instrument: engine exchange path 0 errors.
