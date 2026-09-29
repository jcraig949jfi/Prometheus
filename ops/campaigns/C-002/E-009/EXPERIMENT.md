# E-009 -- Fresh-seed replication of the Block D positives (rcv_add, rcv_str)

Campaign: C-002. Thread: TH-007 (thr-10216c7f001e). Authority: MWO-0004 G4 ("continue the narrow existing rcv_add /
rcv_str line within R2"). This file is the preregistration. It was committed and pushed BEFORE any E-009 unit was
submitted.

Why: Block D (E-006) called rcv_str NEW_BEHAVIOUR on N1 with 14/128 origins, where 13 is the minimum pass and one seed
was below the floor. Its N2 pass was an exact tie on a metric that failed its own control (E-P1). Amendment A1 therefore
records rcv_str as UNRESOLVED. The smallest move that settles this without changing any rule is an independent
replication on seeds never run before.

Design (unchanged from Block D except the seeds):
- Laws: rcv, add, str (the components) and rcv_add, rcv_str (the combinations). rcv_cnd, cnd and fwd are not re-run.
- Seeds: seed_index 4, 5, 6, 7 (Block D used 0-3). Arm OFF only (the rule's arm). 32 origins per seed, 128 per law.
- Instrument: aeth03_propagation.assay via Aether/observatory/aeth03_unit.py, slice 0:32, n=128, warmup 1500, ticks 400
  (the unit runner's defaults, as in Block D).
- Code pinned: c49f2ebad4c888e49fde639e49ecb0d8be3eea83 (as in Block D and E-008).
- Reducer: Aether/observatory/aeth03_combinations_reduce.py at fd7ca4fdeda7, unchanged, over the 20 unit files.
- Execution: 20 Fabric script Tasks (python.numpy), no replicas. About 3 CPU-hours estimated from T-001 on ubu001,
  inside the MWO-0004 R2 envelope. No RunPod.

Decision rule, fixed now:
- For each combination, apply Block D's N1 VERBATIM to the fresh seeds alone, with components from the same seeds:
  P_sust >= max(0.10, 2 x the larger component's P_sust) AND > the sum of the components'.
- **REPLICATED** if N1 holds; **NOT_REPLICATED** if it fails.
- N2 is computed and reported but carries no weight: its metric failed E-P1 (PHYSICS_DESIGN_03 s5.3, Amendment A1).

Consequences, fixed now:
- rcv_str REPLICATED: the Amendment A1 UNRESOLVED status is lifted; NEW_BEHAVIOUR (N1) stands on two independent seed
  sets. rcv_str NOT_REPLICATED: the E-006 pass is recorded as not confirmed, and rcv_str's Block D reading becomes
  NOT_REPLICATED.
- rcv_add REPLICATED: as expected, recorded. NOT_REPLICATED: rcv_add's Block D reading is reopened.
- A pooled 8-seed (E-006 + E-009) figure is reported as description only, never as a verdict.
- One run. No seeds are added, removed or re-run depending on the result. A unit that fails to execute is re-run
  unchanged (same inputs); a unit whose result hash differs across a re-run is reported as DIVERGED and excludes
  nothing.
