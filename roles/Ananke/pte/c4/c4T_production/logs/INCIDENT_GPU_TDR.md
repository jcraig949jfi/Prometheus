# C4-T infrastructure incident: GPU driver reset (recorded 2026-10-09T02:05:07Z)

## What happened
- Around 2026-10-09T01:34-01:35Z, the System log shows nvlddmkm event 153 (a GPU timeout/reset) five times.
- All three workers died:
  - w2 with "torch.AcceleratorError: CUDA error: unknown error";
  - w0 and w1 with exit code -1073741819 (0xC0000005, access violation).
- Rows written before the crash: 110 of 168. All are complete rows. Integrity flags: none.

## Context
- An unidentified python process on M1 (not Ananke's) was holding about 24.5 GB of commit from 01:04Z (PID 16248).
- After the reset, another unidentified python process (PID 18812, started 01:36:18Z, about 12 GB working set) was
  using the GPU: 6.5 GB VRAM and 63% utilisation. Comms #1939.

## Repair (order: an infrastructure defect is repaired and rerun ONCE)
- The 3 jobs that were in flight and wrote no row were un-claimed. Their claims were moved to
  aborted_claims_gpu_tdr/:
  - FLIP-0000|FLIP|A|05
  - FLIP-0004|GATE|B|05
  - FLIP-0004|GATE|C|05
- The same 3 workers were relaunched with the SAME launch commands and the SAME frozen deadline,
  2026-10-09T06:20:34Z. Nothing in the code, plan or deadline changed.
- The searches are deterministic in their seeds, so a re-run job is the same search the crash interrupted.

Identification (Aporia, comms #1944): PID 18812 is ComfyUI (the operator's image-generation app, port 8188), run under the operator's own account. PID 16248 was very likely the same app before the reset. It is not a fleet job. The operator has been told.
