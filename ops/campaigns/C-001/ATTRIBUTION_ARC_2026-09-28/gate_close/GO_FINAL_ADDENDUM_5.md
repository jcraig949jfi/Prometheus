# GO_FINAL addendum 5 (2026-09-29): incident -- unauthorized production run 3 destroyed 10 of 11 files of the 1% sample
**Owner's report:** Nestor #943; roles/Nestor/campaigns/ancestry-replay-2026-09-28/INCIDENT_RUN3_2026-09-29.md.
- A stale scheduled task on M1 started an UNAUTHORIZED third production run at 00:45:03 -04:00. The owner killed it at 00:49:25.
- 10 of the 11 git-ignored run-2 files *.sample1pct.jsonl.gz were overwritten with truncated run-3 gzip. Only s9200010 is intact.
- Committed evidence is untouched: main, the 81895e729 exports, and the manifests SAMPLE_MANIFEST 694a7bb3 and
  SAMPLE_MANIFEST_CONTENT e1584484.
- A third run is outside GO_FINAL v2 and outside MWO-0001 ("No third production run is authorized"). Its partial outputs are
  forensic only and may never enter any E-003 analysis.

**Unaffected:**
- the preregistered production tracer agreement (addendum 3: 29 distinct births, raw 1.0, 0 discrepancies), which reads only
  committed files;
- s4 v2.2, which recomputes from committed files.

**RULING on the owner's options:**
1. **Restore from a surviving copy: ELIGIBLE.**
   - Any candidate copy is accepted only if the frozen verifier (npe_sample_verify.py; efd7295a0) passes for all 11 files: gz
     sha256, uncompressed sha256 and record count against the pinned manifest.
   - Per addendum 2, a copy whose gz bytes differ only in the header mtime also passes, via the uncompressed hash.
   - No other provenance is required, and none is trusted.
2. **Regenerate by re-running run 2: NOT ruled by Archaeon.**
   - It is a production run. MWO-0001 authorizes no third run, and s7 makes it the operator's decision.
3. **Declare the sample lost: NOT ruled by Archaeon either.**
   - The 1% agreement sample is an operator-directed check ("CLOSE THE INDEPENDENCE GATES"). Dropping it is the operator's call.
   - If no verified copy is found, the choice between 2 and 3 goes to the operator as an open decision.

**Fabric Task tsk-581bd93ac9f3:** unchanged. If it is ever claimed against the damaged files, its stage-1 failure is an EXPECTED
consequence of this incident, NOT a tracer finding. It fails closed by design; no content is read.

## Dated note 2026-09-29 (MWO-0004 G2): the 1% sample is VERIFIED; schema declared for stage 2
- **Stage 1 PASSED natively on SKULLPORT** (Nestor #990; g2_sample_check/ @ 85ca06ffd on main):
  * candidate 1, the run-1 copy _scratch/exports_run1_original;
  * verifier v2 (addendum-5 content identity): 11/11 files, 28,055 records;
  * gz bytes differ only in the gzip mtime.
  * The 1% sample is therefore RECOVERED and VERIFIED, not lost.
- **Stage 2 stopped SCHEMA_UNDECLARED (exit 2), as designed.** The schema is now declared in npe_sample_task.py.
  * It was taken from the owner's committed writer (tracer/run_trace.py sink()). No sample content was read by Archaeon.
  * Record: {run, iid, oids, pre, rng_state_at_writeback, accepted_sides, loci}.
  * The loci are POST-write-back, so the reference replays the write-back from rng_state_at_writeback at its T-003 cell rate.
  * Comparison: raw, per class, as before. accepted_sides is not gated.
- **One rerun is requested**, same host and candidate, at the commit carrying this note.

## Dated note 2026-09-29: stage 2 PASS
- The one rerun at 8631128c3 on SKULLPORT exited 0: AGREEMENT PASS, raw per class. The label floor is 0.99842; every other
  field is 1.0.
- 2,818 label-only discrepancies (mutation-shaped, undiagnosed). See E003_SYNTHESIS.md item G.
- The operator-directed 1% sample check is COMPLETE.
