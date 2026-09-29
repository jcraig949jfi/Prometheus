# Fabric adoption defect record (Odysseus; MWO-0001 s12)

Infrastructure defects that real MWO work exposed, recorded as adoption evidence, not worked around. Fabric
repairs remain governed by fabric/FREEZE.md: only science- or safety-blocking fixes, each with a regression test.
Earlier pilot defects D1-D12 are in fabric/README.md s10.

| id | exposed by | identifiers | base SHA | expected | observed | science/safety blocked? | status |
|---|---|---|---|---|---|---|---|
| DEF-ODY-001 | promexec smoke test (experimental; not MWO work) | fabric/promexec SMOKE_RECEIPT | 739ab28ed (broker 1db20165) | files returned by the broker keep their mtime | returned files carry mtime 0 (1970): the tar transfer sets TarInfo.mtime to 0 | no (promexec NOT ENABLED) | recorded; fix with the promexec hardening in a later MWO |
| DEF-ODY-002 | D2 v2 re-audit (Nestor) | MWO-0001; thr-d2-firewall-audit; tsk-6989ee1b86bd att-ab2a11c2ec85, tsk-b43d70a88ce7 att-909dc9fd2546 | f4cde414d | audit replicas can read history and hashes | both ran on the pre-D12 runtime (3ba6fcc0c, then the live node runtime) with no git access, so history and hash sub-claims were CANNOT-VERIFY | partly: it weakened the re-audit, but the verdict was decidable without them | resolved for new work: node workers now run fabric-v0.2 with rogit. Mitigation for principals: require `fabric.runtime==0.2`. |
| DEF-ODY-003 | D2 v2 re-audit replica 1 | tsk-6989ee1b86bd att-ab2a11c2ec85 | f4cde414d | one pinned model (`--model claude-opus-5-5`) | modelUsage lists claude-opus-4-8 AND claude-opus-5-5. Claude Code used a second model for part of the session. | no, but replica independence and reproducibility are reported per model | recorded; the receipt already exposes it (model_used) |
| DEF-ODY-004 | D2 v2 re-audit replica 2 | tsk-b43d70a88ce7 att-909dc9fd2546 | f4cde414d | the worker writes its full findings artifact | the worker reports its output was stopped mid-write, so there is no findings.md, only a shorter final summary. The runtime captured that summary automatically, with no manual salvage. | no, the verdict was decidable | recorded; the runtime deposition worked as designed |
| DEF-ODY-005 | Aether promexec round-1 review, surface 8 (d2b27c2b9) | fabric claude executor (live v0.2) | 54e42c695 | a worker's Task instruction and context are not visible to other local accounts | the instruction and system prompt are passed as `claude -p` argv, which is world-readable via /proc/<pid>/cmdline | not blocking now: on ubu001/ubu002 the only other accounts are system accounts and the NOT ENABLED promexec. It becomes blocking before promexec is enabled or on a multi-user node. | recorded; fix (pass the prompt via stdin or a file) is post-freeze, or earlier if it becomes blocking |
| DEF-ODY-006 | Ensorain replication Task | MWO-0001; tsk-ba120344aa29 att-32409eb521dc | 51ddc856e | real MWO work runs on the frozen v0.2 runtime | it was claimed by the pre-freeze v0.1 pilot worker `worker.ubu002` (no environment probe in its receipt; no rogit or plain-git deny). The Task did not require `fabric.runtime==0.2`, and the old worker is still live (idle timer reset by this Task). | no (read-only research; completed) | recorded. Per the operator, the old worker is left to expire and is not killed remotely. Principals should require `fabric.runtime==0.2`. |
| DEF-ODY-007 | Ensorain replication Task (capability gap, not a code defect) | tsk-ba120344aa29 | 51ddc856e | an independent replication can compute its result | the worker delivered `suff_replica.py` plus its stated implementation choices but could not execute it, since no Claude worker may run code while promexec is NOT ENABLED. The principal must run it separately (as a pinned `script` Task after committing it, or by hand). | partly: computational replication needs two steps | recorded as adoption evidence. This is the use case promexec is for. |

## Related (not Fabric defects; recorded because the MWO names them)

- **DEF-ENS-002** (roles/Ensorain/DEFECTS.md): the legacy WTP-01 engine records replay_ok but does not gate
  REPLICATED on it.
  - It was found from an Artemis disposable-worker claim (old orchestration model) and verified by the owner. No
    WTP-01 label was affected.
  - Adoption relevance: the path from worker claim to owner verification to a recorded defect worked without a
    Fabric Task.
