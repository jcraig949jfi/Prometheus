# MWO-0001 s12 adoption defect: host-affine Task for host-local evidence has no eligible worker (Archaeon, 2026-09-28)

**Identifiers:**
- MWO-0001 (commit bd48fac9b; sha256 007054ad...);
- Thread thr-a7fcb43e8092 (TH-015); Campaign C-001; Experiment E-003 (alias: ATTRIBUTION_ARC_2026-09-28);
- Task tsk-581bd93ac9f3; no Attempt exists;
- base_sha 028f2eff8c208eb59f27b84032705e7badfa9a6a (branch archaeon/attribution-arc-2026-09-28);
- Fabric frozen at fabric-v0.2 / 54e42c695.

**Work that exposed it:** the operator's decision on the NPE 1% production agreement sample.
- The sample is 11 .gz files, about 112 MB, host-local on SKULLPORT (M1), git-ignored.
- It is pinned by SAMPLE_MANIFEST_CONTENT e1584484 at Nestor 81895e729.
- The work is to be run as a Fabric Task with host affinity to the node holding the sample, not via SSH trust.
- The Task was submitted as `--executor script --host skullport --cap compute.cpu.light`. The module npe_sample_task runs the
  frozen pre-read verification, then the frozen reference only on PASS. It takes the sample directory from the allow-listed env
  var NPE_SAMPLE_DIR.

**Expected:**
- A worker on skullport claims the Task.
- Or Fabric reports why nothing can: a waiting reason naming the missing host or capability.

**Observed:**
- (1) `fabric agents` lists no worker on skullport, live or historical. Live workers exist only on ubu001 (worker.ubu001,
  worker.ubu001.sci) and ubu002 (worker.ubu002). So nothing can claim a Task whose evidence is host-local to M1.
- (2) `fabric submit` ACCEPTED the Task with host_affinity=skullport, state "submitted", waiting_reason null. There is no
  signal that the affinity cannot be satisfied. The Task will stay unclaimed silently.
- (3) Location gap (coordination, not Fabric): the owner's receipts (START_RECEIPT host=SKULLPORT, git_head) do not record
  the absolute path of the git-ignored sample. Any claimant needs the path; NPE_SAMPLE_DIR must be set by whoever runs the
  host's worker.
- (4) Environment note: the script executor assumes a POSIX environment (PATH=/usr/bin:/bin). SKULLPORT is Windows. Whether
  a v0.2 worker runs there at all is untested.

**Science/safety blocked?**
- Science: YES for this one item. The E-003 NPE 1% agreement check cannot run, so the NPE leg's tracer-agreement-on-production
  evidence stays pending.
- Safety: no.
- Nothing was worked around. No SSH trust was requested, no host access improvised, and no sample content was read.

**Needed (not requested from any seat by Archaeon beyond this notice):** a v0.2 worker on SKULLPORT with compute.cpu.light and
the script executor, and NPE_SAMPLE_DIR set to the exports directory. Or another operator-approved route. Any fix is governed
by fabric/FREEZE.md.
