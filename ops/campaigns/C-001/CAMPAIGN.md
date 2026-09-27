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
| E-001 | B6: who / where / what | E-001/TASKS.md |
| E-002 | B1: hereditary continuity under recombination | E-002/TASKS.md |

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
