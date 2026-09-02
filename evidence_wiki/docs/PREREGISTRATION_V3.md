# V3 PREREGISTRATION — execution-based memory experiment (frozen pre-run)

Charter: CHARTER_PEW_V3_2026-09-02.txt (sha 0d24ff4fb5e6b9e3d31b10d9219c8e
cac617020c43ee20ebaaa3481469fde031). Ground truth SEALED before this
freeze: derived/v3_ground_truth.json, sha256 in v3/ground_truth_sha256.txt
(11f16bdd...). This commit is the freeze point; no metric changes after.

## Question (charter s7-s8)
Can provenance-bound PEW memory produce measurable EXECUTION-level benefit
over a memory-isolated control? Endpoint is deterministic correctness of
executed database work — no LLM-as-judge.

## Tasks (6, frozen; each answered by RUNNING queries, not by recall)
X1 Report how many Dirichlet-zero rows are available in prometheus_fire and
   which table holds them.                       [trap: zeros.* is empty]
X2 Estimate the row count of lmfdb.lfunc_lfunctions WITHOUT running a full
   COUNT(*) over 346GB.                          [trap: n_live_tup reads 0]
X3 Report how many catalog problems have an authored test_spec (>=30 chars)
   in aporia/mathematics/triage.jsonl.           [trap: duplicate ids,
                                                  last-wins semantics]
X4 Report how many curves in lmfdb.bsd_joined have rank>=2, and state
   whether the stored sha column can serve as independent ground truth for
   BSD verification there (yes/no).              [trap: Sha assumed BSD]
X5 Report how many distinct problems questions.jsonl defines.
                                                 [trap: 537 lines, 534 ids]
X6 Report how many items are pending in agora.research_queue.
                                                 [no trap: calibration]

## Correctness criteria (deterministic, frozen)
X1 correct iff 184,830 reported AND charon_duckdb.dirichlet_zeros named
   (or zeros.* stated empty with the mirror identified).
X2 correct iff a value in [24.0M, 24.7M] reported without a full COUNT(*)
   on the table (method visible in transcript/script).
X3 correct iff 59 reported.
X4 correct iff count in [280,000, 285,000] AND the answer is NO.
X5 correct iff 534 reported (or 537 lines / 534 unique stated).
X6 correct iff 0 reported.
Scored by exact comparison against the sealed ground truth; the adjudicator
may not reinterpret criteria after unsealing outputs.

## Arms (3 replicate agents each, sonnet — capable-model lane per V2 ruling)
A MEMORY-ISOLATED CONTROL. Run inside a window where BOTH:
  (1) the project auto-memory directory is RELOCATED (harness-level disable,
      per the documented mechanism; verified by an in-window probe agent
      that must report NO injected memory), and
  (2) the PEW service is STOPPED (port closed — technically unable, not
      merely instructed). Agents receive: task list + database/file access
      (psql credentials in prompt, repo file paths for X3/X5 inputs) +
      instruction to answer by executing queries/scripts. No evidence_wiki
      access is possible (service down) and none is mentioned.
B EXPLICIT PEW MEMORY. Ambient memory RESTORED (declared: MEMORY.md sha
  05dbe05e..., identical for all B agents — parity within arm), service UP.
  Agents receive the same task list + a FROZEN DOCTRINE PACK (evidence-pack
  built from PEW, content-hashed, registered in ew.memory_artifacts) +
  the same database/file access. Every B run is logged in
  ew.memory_influences (pack hash -> consumer -> decision artifact ->
  result), closing the charter-s6 chain.
NOTE the arms differ in ambient-memory state (A disabled, B declared-on).
This is DISCLOSED and intentional: A is the charter's memory-isolated
control; B is "explicit + ambient" as deployed. The pack contains the
task-relevant doctrine, so pack-vs-ambient attribution within B is
diagnosed from which evidence the agents cite.

## Endpoints and thresholds (frozen)
Per agent: correct-count / 6. Primary: mean(B) - mean(A) as a rate.
  EXECUTION_ADVANTAGE_DEMONSTRATED if delta >= +0.25 (>= 1.5 tasks) AND
    B > A in >= 2 of 3 rank-paired replicates;
  MARGINAL if delta in [0.083, 0.25);
  EXPLICIT_MEMORY_DOES_NOT_IMPROVE_EXECUTION otherwise.
G6 non-saturation: A mean correct on trapped tasks X1-X5 in [0.10, 0.80];
  outside the band => instrument verdict, not an arm verdict.
X6 calibration: both arms expected ~1.0; a low X6 score flags execution-
  skill (not memory) failure and is reported per arm.
Contamination rules: an A-window probe reporting ANY injected memory voids
the A window (rerun after re-relocation). Service reachability during the
A window is checked (must be connection-refused). All raw outputs preserved.
