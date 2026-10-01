# BUILDER-EXPERIMENT proposals: operational failure patterns (Ananke, 2026-09-29/30)

Each pattern below actually happened in Ananke's own work in the last 48 h. Each proposal has: problem,
observed examples, proposed primitive/API, invariant, positive-control test, negative-control test, and
the semantics it must never silently change. The statistical and instrument patterns are in
H-INST/REPORT.md.

## BX-1 Plan freeze provable from git
- PROBLEM: a plan written "frozen" in a log but first committed together with its results cannot be
  shown to predate them.
- OBSERVED: W-O (Harmonia audit G1, 93e2e544b). Fixed for Ananke by the principal committing plans before
  launch (REL4 017259a48, REL5 22b9bbd51, T-INS-20 fc8bfa171, AUDIT3 6f25dc642).
- PRIMITIVE: `ops/tools/freeze_check.py <plan> <result_glob>`. It PASSes iff
  `git log --diff-filter=A --format=%cI -- <plan>` predates the first commit adding any file matching
  <result_glob>, and the plan blob is unchanged since.
- INVARIANT: every PASS implies plan-add commit < first result commit, and plan blob at HEAD = blob at add.
- POSITIVE CONTROL: REL4 (plan 017259a48 before W-W results) -> PASS.
- NEGATIVE CONTROL: W-O (PLAN.md added in 93e2e544b with REPORT) -> FAIL.
- MUST NOT CHANGE: plan content; it reads git only.

## BX-2 Worker process envelope guard
- PROBLEM: delegated workers relaunch jobs they think failed and exceed their lease envelope.
- OBSERVED: W-P ran 7 processes (14 threads) on an 8-thread lease for ~12 min after a launch it believed
  had failed.
- PRIMITIVE: `envelope.launch(tag, argv, threads)`. It records PIDs and thread counts in a per-lease
  registry and refuses a launch that would exceed the lease's declared threads, counting live registered
  PIDs checked through the OS process table, not memory.
- INVARIANT: the sum of the threads of live registered PIDs <= the lease envelope at every launch.
- POSITIVE CONTROL: launching 4x2 threads on an 8-thread envelope succeeds.
- NEGATIVE CONTROL: a 5th 2-thread launch is refused; a launch after killing one succeeds.
- MUST NOT CHANGE: the job's arguments or seeds.

## BX-3 No implicit accelerator
- PROBLEM: the engine defaults to cuda when available, so CPU-only workers silently use the GPU without a
  lease.
- OBSERVED: W-Y dev check (~2 s on cuda:0, unleased). Mitigated by CUDA_VISIBLE_DEVICES= in briefs
  (COMMON_RULES_ARC3 s5).
- PRIMITIVE: engine-level `device` must be passed explicitly in worker contexts. A `PROMETHEUS_DEVICE`
  env var defaults to cpu, and choosing cuda requires a GPU lease token present in the env.
- INVARIANT: no tensor on cuda unless a lease token for <host>:gpu is live.
- POSITIVE CONTROL: with a token, World(..., device=None) lands on cuda.
- NEGATIVE CONTROL: without one it lands on cpu (or raises, by policy).
- MUST NOT CHANGE: numerics. The CPU/GPU bit-identity tests (test_conformance) must still pass.

## BX-4 Fabric lease release by resource+token
- PROBLEM: `python -m fabric lease release <res> --as X --token T` prints NOT RELEASED. It works only with
  `--lease <id>` as well.
- OBSERVED: Ananke FP-001 (lse-848b29b24607); workers then had to be told to pass --lease.
- PRIMITIVE: a Fabric CLI fix (Odysseus owns it; Fabric is frozen, so this is a report). Release by
  (resource, token), or refuse with a message naming the missing flag.
- INVARIANT: release with a valid token either releases or prints the actionable reason.
- POSITIVE CONTROL: acquire, then release with resource+token -> RELEASED.
- NEGATIVE CONTROL: a wrong token -> NOT RELEASED with the reason.
- MUST NOT CHANGE: token fencing.

## BX-5 Report deposition must refuse empty or undelimited extractions
- PROBLEM: the principal's extraction of a worker's final message wrote an empty REPORT.md, and
  deposit.py accepted it as "undelimited".
- OBSERVED: W-M first deposit attempt (removed before commit).
- PRIMITIVE: deposit.py refuses an empty message, and refuses "undelimited" unless `--allow-undelimited`
  is given.
- INVARIANT: every deposited REPORT.md is non-empty; delimited mode is the default requirement.
- POSITIVE CONTROL: a delimited message deposits.
- NEGATIVE CONTROL: an empty file is refused, and an undelimited file is refused without the flag.
- MUST NOT CHANGE: the verbatim byte content or the provenance hashing.

## BX-6 Known-answer gate enforcement
- PROBLEM: a worker ran the champion although its own pre-registered known-answer gate failed.
- OBSERVED: W-Y D-1 (T-INS-20).
- PRIMITIVE: `gate.require(ka_result_path)` at the top of champion runners. It exits non-zero unless the
  KA json records PASS for every pre-registered check. The principal's brief template lists the KA json
  path.
- INVARIANT: no champion output file exists with an mtime earlier than a PASSing KA record.
- POSITIVE CONTROL: KA PASS -> the runner proceeds.
- NEGATIVE CONTROL: one KA FAIL -> the runner exits before touching the specimen.
- MUST NOT CHANGE: the KA definitions.

## BX-7 "Does the promotion change any real verdict?" check
- PROBLEM: an instrument change validated on synthetic data can be empirically inert on real data. Then
  its promotion changes nothing, and its validation effort is invisible.
- OBSERVED: REL4/REL5's H2 interval equals REL3 on 439/439 real group-arms (harvest census).
- PRIMITIVE: before promoting a new rule, run it and the incumbent on all saved real inputs and report
  the transition table (how many real verdicts change). This belongs in the promotion commit.
- INVARIANT: every promotion commit carries a real-data transition table.
- POSITIVE CONTROL: REL2 -> REL3 changes some W-O rows (W-U: 64 ambiguous).
- NEGATIVE CONTROL: H2 vs REL3 on W-Z arrays -> 0 changes, reported as inert.
- MUST NOT CHANGE: the rule. This is reporting only.

## BX-8 Per-seat rolling compute ledger
- PROBLEM: the MWO-0004 R2 envelope (48 core-h / 24 h) was overrun by estimate (~55). Usage was
  reconstructed from memory of worker processes x threads x wall time, and the first note undercounted it
  ("~20").
- OBSERVED: Ananke 2026-09-29.
- PRIMITIVE: Fabric lease acquire/release already has timestamps and a purpose. Add a declared-threads
  field, and a `fabric usage --seat X --window 24h` report (threads x leased wall). Unleased <= 2-thread
  work is logged by the worker envelope (BX-2).
- INVARIANT: the reported usage is >= the true usage of leased work (an upper bound by construction).
- POSITIVE CONTROL: two leases of 8 threads x 1 h -> 16 core-h.
- NEGATIVE CONTROL: a released lease stops accruing.
- MUST NOT CHANGE: lease semantics.
