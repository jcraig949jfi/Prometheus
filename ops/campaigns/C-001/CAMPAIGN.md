# C-001 -- Causal Lens Hardening

Thread: TH-001. Owner: Archaeon. Opened 2026-09-27 as the operator-selected pilot of the ops/ structure (direction verbatim in
roles/Archaeon/prompts/2026-09-27_ops_pilot/). This is a pilot of shape, not a mandate for any other seat (ops/README.md).

Purpose: take the strongest unresolved findings from TH-001 and determine which distinctions are real enough to become
instrumentation, and which were artifacts of our current rulers. This is not "prove the causal lens"; it is the current body
of related work.

Constraints:
- Bellerophon's multi-day campaign occupies M2: no heavy compute on M2.
- Prefer moving Tasks off M2.
- No preregistration or launch of the host-conditioned assay without the operator.

Operational goal of the pilot: take one real Archaeon Task that would ordinarily run on M2, execute it somewhere else without
changing the science, and record what the Task needed in order to move.

| Experiment | Question | Tasks |
|---|---|---|
| E-001 | B6: who / where / what | CLOSED 2026-09-27 (E-001/RESULT.md) |
| E-002 | B1: hereditary continuity under recombination | READY, not urgent (E-002/TASKS.md); may be handed to a fresh worker as a pickup-from-Git test |

## Pilot finding 1 (2026-09-27): the first real Task moved off M2 -- T-001, A-002 on ubu001, science unchanged
Result: ubu001 reproduced T-001 bit-for-bit.
- result_sha256 = cd9547c2... (identical to M2's reference); 74,800/74,800 rows identical to BEE's preserved log.
- Harness module hashes = git 16fc6c2a.
- 50.9 s, 141 MB RSS on a 4-thread / 8 GB laptop.
- M2 was not needed to execute; it was needed only to verify against evidence that exists only on M2.

What the Task actually needed in order to move (observed, not designed):
1. Code addressable by commit. The frozen BEE harness happened to exist as git 16fc6c2a (byte-identical to M2's copy), and BEE's
   traced VM lives on a public seat branch. Without those commits, the code would have had to be shipped from M2's disk.
2. Inputs addressable by content. One 2 KB input (the run's config.json) existed ONLY on M2's disk. It had to be committed as a
   Task input with its sha256. M2-local evidence is the real portability barrier, not compute.
3. No host paths in the command. The probe hard-coded C:/Users/... paths, and BEE's tool has a Windows HARNESS constant. Both needed
   path arguments.
4. Proof of which code ran. The import order can let another checkout's `prometheus` package shadow the frozen harness. The probe
   now writes the sha256 of every harness module it actually imported, and the receipt compares them to the pinned commit.
5. A reference result and a verifier location. Executing and verifying split across hosts: the executor returns a result hash, and
   the full check against preserved evidence (a 74,800-row log in a 282 MB directory) ran where that evidence lives.
6. A relay for Git transitions. ubu001 has no GitHub push credentials, so the claim, failure and receipt commits were made by the
   controlling seat on M2. The Git-native claim model assumes executors can push; here they could not.
7. An access path, not just capacity. M3 (GANDALF) answers ping but accepts no SSH from M2, so it could not take the Task. ubu001
   could, because an SSH key from M2 had been set up.
8. Output transport. 13 MB copied back to M2's evidence store (scp), with the sha256 recorded in the receipt.
9. Cleanup as part of completion. The task directory was removed on ubu001, and absence of the directory and of any process was
   verified separately. My first absence check was a false positive: pgrep matched its own command line.
10. Attempts separate execution failure from science. A-001 failed on MY portability edit (a SyntaxError, pushed without a compile
    check). A-002 used a newer probe commit. The science identity (the result hash) was unchanged, and the Attempt log kept the
    failure out of E-001.

Minimum portable-Task record, as used by T-001: code refs (commits + file sha256); input artifacts (path in git + sha256); a
host-independent command; resources (CPU/RAM/wall); expected result hash; where verification must run; output destination; cleanup
rule. See E-001/TASKS.md "T-001 inputs".

## Pilot finding 2 (2026-09-27): the recipe fanned out to a second node
Outcomes:
- T-002 ran on ubu002 on the first attempt, with the T-001 recipe unchanged (only the run id and its committed config differ). It was
  bit-identical to M2 (fb10f7e4...; 83,384/83,384 rows).
- T-003 (NPE, different engine and different code) ran on ubu001 on the first attempt using the same recipe, with 3 workers on a 4-thread
  laptop.
- The T-004 measurement ran on ubu002. Two attempts failed on my script defects (a wrong assumption about the HITS.json format); the
  third succeeded.

Friction that actually occurred (and only that):
1. Script defects, not host defects. T-004 A-001 assumed a list where HITS.json has a dict keyed by representation. That assumption
   also hid a science trap (64-byte tapes cannot run on the 32-byte VM). Recorded as FAILED and retried.
2. Instrument timing hazard. NPE's VM advances pc before ED-prefixed writes, so the probe had to capture the instruction address at
   fetch. This is a correctness requirement of the observation, found by reading the engine before running it.
3. Runtime difference. Python 3.14 on Linux starts multiprocessing workers with forkserver, not fork, so runtime patches must be applied
   per worker (the probe did). Nothing else about the Linux nodes mattered: stdlib only, Python 3.14.4 on both, no installs.
4. Verification stayed on M2 in every task. BEE's preserved traced logs (282 MB) and the PORTABILITY-01 NPE replays exist only on M2's
   disk, so every "science unchanged" check ran there on outputs copied back (13-15 MB each).
5. The Git relay stayed on M2. The nodes cannot push, so every claim, failure and receipt was committed from M2.
6. Resources were not a problem. The largest was T-003: 932 s wall and 25 MB peak with 3 workers. BEE replays ran in 51-108 s and
   141-150 MB. Nothing came near the 8 GB nodes' limits.
7. Cleanup worked. Task dirs were removed on both nodes, and absence of the directory and of any process was verified.

What still ties work to M2: (a) M2-only preserved evidence used for verification; (b) the push relay. Compute does not.
