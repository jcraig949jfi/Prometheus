# D02 -- DEV WINDOW 2 REPORT: design packet

C-006 (C-P2B-APH-BETA-01), cycle 2, DEV. Active threads: TH-018 / TH-021. Evidence tier 2.

## 1. Information bottleneck after TEST-1
TEST-1 qualified the apparatus on all-or-nothing cases. The earliest rung at which the HISTORICAL frontier is still
uninterpretable is the measurement of capability itself: A23's CAPABILITY_SAME was read by three instruments that
DEV-1 repaired or replaced:
- a first-hit-at-escrow endpoint;
- tribunal v1;
- a 10M ladder against START/PRISTINE.
Its controls also turned out to be partly dead (below). Before spending T51's compute on natural recurrence, the
first-order positive the frontier rests on must be re-measured with the repaired apparatus. This is T53, the
operator's preferred first early probe.

## 2. New finding: A20-A23 controls P and OFF_0 were structurally unable to score
`engine/a20_c3.py:245`: `key = "%s:%s" % (held, cls) if held != "P" else None`.
- For P, the key is None, so the arm has no own families.
- For OFF_0, held = "OFF_0", but `assign()` creates tclasses only for ON = [G1, SHAM_0, SHAM_1, SHAM_2]. No
  "OFF_0:SAME" family exists (verified on A23_ROLES: the tclass set has no OFF_0 entries).

So REUSED_SAME and CAPABILITY_SAME are identically 0 for P and OFF_0. Two of the three sign-test controls in A23's
H1 verdict (`H1_G1`: vs G1_NC, P, OFF_0) could not succeed. The H1 verdict therefore rests on G1_NC as its only
live control, plus the absolute threshold. **A23's label is unchanged** (the verdict code was preregistered as
written). The finding is recorded for TH-021, and T53 makes these controls live by evaluating P's and OFF_0's
SELECTED libraries on the held abstraction's families.

## 3. Changes
- `engine/v2b/t53_rescore.py` (sha256 48e44d0e...): the TEST-2 runner. Plan / run / report; live controls; in-run
  apparatus controls PC_MOTIF / PC_ONE / NC_OTHER; bridge to A23 CAPABILITY_SAME; continuity check against A23's
  recorded charges; motif-recovery split; D-stratified summary.
- Plan `beta01/runs/T02_T53/T53_PLAN.json` (sha256 32ca8197...): 10 replicates, 2,912 unique exact walks at 10M.

## 4. Qualification and DISCLOSURE (smoke runs)
- The walker speed is identical to a18.fast_cost (0.23 s at 200k on an A23 cell). A censored 10M walk is about 21 s.
- **Disclosure (pre-freeze exposure risk, contained).** The first smoke run set a 200k cap in the parent process,
  but Windows spawn workers re-imported the module and walked at the frozen 10M cap on replicate 1. That made the
  "smoke" a partial real execution before the freeze.
  - It was stopped (TaskStop; no python process survived, checked by process list).
  - Its 208 rows (sha256 prefix d49e9b811cde68ad) were DELETED WITHOUT INSPECTION. Only per-walk seconds and
    spurious counts were read, for the timing diagnosis.
  - The frozen rules (T02 spec s4-s5) were not informed by any outcome.
  - The cap and output dir are now environment-driven (V2B_T53_CAP / V2B_T53_DIR), so they reach the workers.
- A second smoke at a 20k cap (not the endpoint) on replicate 1 validated the report code path: 0 technical failures;
  all result fields present. Its readouts at 20k are not results, and they were printed by the runner (disclosed).
  The outputs were deleted.

## 5. Erratum for T01 (non-verdict)
T01_RESULT K1 detail `pristine_all_censored = false` is wrong: the field included the qbda tribunal-case walks. On the
four transfer families PRISTINE was censored in 16/16 cells (capability_summary). The verdict did not use the field.
The frozen T01 runner is not edited. The fix lands in its next version (t1 v2).

## 6. Compatibility
Apparatus v2b-1 is unchanged; T53 adds a runner only. Cap, tribunal and ruler are as frozen. Compute is M4 with 4
workers, at the R2 edge (about 10-17 CPU-h). It is reported as measured.

## 7. Next frozen experiment
TEST-2 = T53: `beta01/windows/T02_T53_SPEC.md`.

## 8. Queued for later DEV windows (not frozen)
- t1 v2: graded/partial known-answer cases and selection (R3) known-answers. These are needed before T52, the
  validation-dose experiment.
- Fabric GENERIC_WORKER pilot on a small shard, as a cross-host replication, before T51.
- A no-donor-state receipt check (TRIAGE R2) before the S4 replication.
