# INCIDENT 2026-09-29: an unauthorized third production run started; 10 of 11 run-2 1% sample files destroyed

- **Recorded by:** Nestor (M1 SKULLPORT) under MWO-0001 s12.
- **Run 3 was not authorized.** MWO-0001: "No third production run is authorized."
- **Run 3 did not produce evidence.** It is not evidence and must never be read as such.

## Identifiers

| item | value |
|---|---|
| MWO | MWO-0001 (sha256 007054ad...88f3) |
| campaign | roles/Nestor/campaigns/ancestry-replay-2026-09-28 (production run 2 = 81895e729, on main) |
| worktree | F:/Prometheus-worktrees/nestor-s1-forensics (HEAD 111794cf4, contains run 2) |
| scheduled tasks | \NestorAncestryProduction (scratchpad launch_prod.cmd), \NestorAncestryPin (launch_pin.cmd) |
| lease | lse-3db3a46c3932, skullport:cpu8, holder "Nestor ANCESTRY-PRODUCTION-RUN2", acquired 00:45:03-04:00, released by the wrapper after the kill |
| affected downstream | Archaeon Fabric task tsk-581bd93ac9f3 ("NPE 1% production sample", host-affine skullport, still `submitted`; stage 1 verifies the 11 files against the manifest pinned at 81895e729) |

## Timeline (local time, -04:00)

- **09-28 10:29 and 20:16:** Nestor created the pin and production launchers as `schtasks /create /sc once /st 23:59` placeholders and started them by hand with `/run`. Both runs completed; production run 2 exited 0 at 20:28.
- **09-28 23:59:00:** both one-time triggers FIRED (Last Run Time 23:59:00). Each wrapper blocked in `nestor_lease.py wait-acquire cpu8`, because Ananke held skullport:cpu8.
- **09-29 00:44:33:** Ananke's lease ended, and the pin launcher acquired the lease.
  - `pin_reproduce.py` refused itself ("pinned dir exists ... never overwrite") and exited 1 after 0.06 s. No damage.
- **09-29 00:45:03:** the production launcher acquired the lease and started `tracer/production_launch.py`, which is production RUN 3.
- **09-29 ~00:48:** Nestor, checking the lease table before the s4 v2.2 run, found an unexpected "Nestor ANCESTRY-PRODUCTION-RUN2" lease and traced it to the scheduled task.
- **09-29 00:49:25:** the process tree was killed. Before the kill, the PID and command line were matched against `tracer\production_launch.py`. The wrapper logged EXIT 1 and released the lease. Both scheduled tasks are now DISABLED.

## Damage

| object | state |
|---|---|
| main, and every committed file | **unaffected**: run 3 wrote only into the old worktree and committed nothing |
| 5 tracked births files + START_RECEIPT.json in the old worktree | partially rewritten by run 3; **restored to HEAD (run 2)** with `git checkout --` |
| the 11 run-2 1% sample files `exports/*.sample1pct.jsonl.gz` (git-ignored; pinned only by sha256 in SAMPLE_MANIFEST.json @ 81895e729) | **10 of 11 DESTROYED**: overwritten with truncated run-3 gzip streams, and none matches the manifest. Only `...s9200010__B_reimplant_actual.sample1pct.jsonl.gz` is intact (run 3 had not reached it). |
| partial run-3 outputs | preserved outside git with a sha256 manifest (19 files) in Nestor's M1 scratch `run3_partial_2026-09-29/`, for forensics only |

## Consequences

- **Births and s4:**
  - The committed births (29 distinct / 9 simulations) and the births-agreement PASS (#927) are unaffected.
  - s4 v2.2 recomputes from committed files and is unaffected.
- **The 1% sample check is BLOCKED.** #927 says it "stays required once a route exists", and Archaeon's host-affine route (tsk-581bd93ac9f3) cannot pass its stage-1 manifest check.
  - This blocks the science of that check only. It is not a safety block.
  - It does not broaden or change any ancestry claim.

## Options (for Archaeon's and the operator's ruling; Nestor takes none of them unilaterally)

1. **Restore from a surviving copy.** A disk-wide search of F:, C:\Users\jcrai and H: for `*.sample1pct.jsonl.gz` outside the exports directory is recorded below.
2. **Regenerate deterministically** by re-running production run 2 exactly as frozen (same launcher, same seeds).
   - Run 1 vs run 2 showed the sample content is deterministic apart from the gzip mtime header (addendum 2). A regenerated file would therefore match on decompressed content, not on the manifest's file sha256, and the comparison would need that content-level ruling.
   - **This IS a production run, and it needs operator authorization.**
3. **Declare the 1% sample lost.** Record the tracer-agreement evidence as the births agreement (34/34 victim halves, 0 discrepancies) without the per-interaction sample.

## Defects (MWO s12)

- **D-INC-1: Nestor process.**
  - Expected: a launch-once scheduled task has no live future trigger.
  - Observed: the `/sc once` placeholder fired hours after the manual run.
  - Aggravating: `wait-acquire` converted the stale trigger into a delayed, unattended launch that fired when another seat released the resource.
  - Repair: disable or delete launch-once tasks immediately after `/run`. Recorded as feedback memory.
- **D-INC-2: tracer/production_launch.py (frozen).**
  - Expected: a production launcher never overwrites an existing run's outputs (the pin runner has this guard).
  - Observed: it silently overwrote the git-ignored samples.
  - Not edited: the file is frozen. The guard belongs in any future launcher.
- **D-INC-3: evidence custody.**
  - Expected: evidence pinned by hash has an immutable second copy.
  - Observed: the 1% sample existed only as mutable, git-ignored files in one worktree.

## Copy search

The search of F:, C:/Users/jcrai and H: finished on 2026-09-29. It found two CANDIDATE directories holding the RUN-1 sample files, which were kept aside when run 1 was invalidated:
- `nestor-s1-forensics/.../ancestry-replay-2026-09-28/_scratch/exports_run1_original/` (11 files)
- `nestor-s1-forensics/.../ancestry-replay-2026-09-28/_scratch/production_run1_INVALIDATED/` (11 files)

**Nestor's check (NOT the frozen verifier):**
- Both directories match the committed SAMPLE_MANIFEST_CONTENT.json on all 11 files, by uncompressed sha256 and record count.
- The gz sha256 differs on every file. That is the gzip-mtime header already ruled in addendum 2.

**Nothing has been restored or copied.** Per Archaeon's ruling (#945, addendum 5), a candidate counts only if the frozen verifier passes all 11. The paths and hashes are reported in #952.
