<!-- DEPOSITED VERBATIM by Ananke for worker W-Z; sha256(report)=7134b1c5e05404ae; delimited; see REPORT.provenance.json -->
W-Z REPORT: E-ANANKE-W-Z, T-SWAP-AUDIT3, thread thr-5df816e9b844 (authority CWO 2026-09-30 + MWO-0004)

SUMMARY
- The Pa prediction held: 54 of the 64 AMBIGUOUS rows (84.4%) resolved to their REL2 label.
- The Pb prediction held: 35 of 124 covered groups (28.2%) are CARRIER-NAMED.
- The consistency check fell below its frozen bar: 92.7%, where the plan requires 95%. Per the plan this is reported as a seed-sensitivity finding and was not fixed.

WHAT I TESTED
- Plan: roles/Ananke/research/plans/T-SWAP-AUDIT3_PLAN.md at 6f25dc642. It was committed at 11:49:43Z. My first result (the known-answer gate) came at 11:52:44Z and my first specimen result at about 11:57Z, so the plan predates every result. I did not edit the plan.
- Rule: the promoted REL4 "H2" rule, via prometheus/ananke/swap_rel.from_pairs. The p_min passed is REL3's (P256_K11 or K12, from W-U out/rel3_table.json), as W-W's module documents.
- Transfer class for every FLIP_REL: W-U swap_rel3.z_ci, which gives COMPLETE, PARTIAL or OVERSHOOT.
- Runs reuse W-O's code by import: runner.load, sct_offset, fork_single and audit.arm_names. They use W-O's inventory groups and recorded offsets.
- Design: SINGLE-trial swaps, M = 512 worlds (P = 256 pairs), new namespace world_seeds(0x680, 512), all scored trials of W-O's trial set.
- Per (group, arm), the per-trial pair-mean arrays a and s are saved in out/pairs/<gid>.npz (uint8, 4 x the pair mean, 255 = not scored).
- Coverage: 124 of 249 groups and 365 of 733 rows.
  - All 31 groups that contain an AMBIGUOUS row were run first (113 rows, including all 64 AMBIGUOUS rows).
  - 93 further groups followed in ascending sha256 order.
  - The run stopped when the next group (61d65a4f) was projected to exceed the specimen budget.
  - There were no errors.

KNOWN-ANSWER CHECKS (run before any specimen; all passed)
- prometheus/ananke/tests/test_swap_rel.py: 11 passed, RC = 0.
- W-L champion n1_s3 (W-O's KA1 construction, seeds 0x680^0x1, offset -1):
  - S reads FLIP_REL COMPLETE (z = -1.079).
  - site_all reads FLIP_REL COMPLETE.
  - channel_all reads NO_EFFECT_REL.
- hold_latch plant on 4ab2ba01 (seeds 0x680^0x2, mid offset): channel_all reads NO_EFFECT_REL.
- Must-fail: the latch's site_all fed to the same check reads FLIP_REL, as required.

RESULTS

(a) The 64 AMBIGUOUS rows (W-U REL3 bound in rows, new label in columns)

| W-U REL3 bound | new label | rows |
|---|---|---|
| CHANCE_REL or INDETERMINATE | CHANCE_REL | 36 |
| CHANCE_REL or INDETERMINATE | INDETERMINATE | 8 |
| INDETERMINATE or NO_EFFECT_REL | NO_EFFECT_REL | 16 |
| INDETERMINATE or NO_EFFECT_REL | INDETERMINATE | 1 |
| FLIP_REL or INDETERMINATE | FLIP_REL | 1 |
| FLIP_REL or INDETERMINATE | INDETERMINATE | 1 |
| FLIP_REL or INDETERMINATE or NOT_ELIGIBLE | FLIP_REL | 1 |

- All 64 new labels fall inside W-U's bounds.
- Against REL2: 54 of 64 match (84.4%).
- The 10 misses all went from a REL2 certificate to INDETERMINATE, which W-U showed was the only possible drop:
  - 5 rows on specimen 42716814 (offsets 2, 9, 11)
  - 4 rows on 4781b0a1 (offset 14)
  - 1 row on 369f5a5b (offset 1)
  - All have intermediate z (|z| between 0.43 and 0.61).
- **Pa (>= 70%): HELD.**

(b) Group table (124 groups; class uses all arms run)

| class | groups |
|---|---|
| CARRIER-NAMED | 35 |
| CARRIER-PARTIAL | 22 |
| CARRIER-OVERSHOOT (addendum Z3) | 1 |
| NO-CARRIER-FOUND | 61 |
| UNDECIDED | 5 |

- CARRIER-NAMED is 28.2% of covered groups. **Pb (25-45%): HELD.**
- Recorded arms only (sensitivity): 32 NAMED, 8 PARTIAL, 78 NO-CARRIER-FOUND, 6 UNDECIDED. NAMED is 25.8%, also inside the band.
- The 31 AMBIGUOUS groups: 21 NO-CARRIER-FOUND, 8 CARRIER-PARTIAL, 1 CARRIER-NAMED (4ecdfb3f offset 5, joint arm COMPLETE), 1 UNDECIDED (4781b0a1 offset 14).
- By source:
  - WF: 32 NAMED of 52.
  - WI: 3 NAMED, 18 PARTIAL, 47 NO-CARRIER-FOUND of 70.
  - SCT: 1 PARTIAL, 1 NO-CARRIER-FOUND.
- FLIP_REL rows: 56 COMPLETE, 19 PARTIAL. Each matched a class W-U had allowed for that row.

(c) Consistency against W-U DETERMINED rows (frozen bar 95%)
- 279 of 301 rows agree (92.7%). **BELOW BAR.**
- None of the 22 disagreements flips one certificate into a different certificate. All are between a certificate and INDETERMINATE:
  - 20 rows went from INDETERMINATE to a certificate: 12 CHANCE_REL, 4 FLIP_REL, 4 NO_EFFECT_REL.
  - 2 rows went from NO_EFFECT_REL to INDETERMINATE.
- They are concentrated in 10 of 110 groups (8 specimens) where |z| is between 0.34 and 0.62 and normal lo99 is between 0.62 and 0.75.
- My reading: these are near-threshold, intermediate-transfer rows whose label changes with the seed (seed sensitivity), not an instrument defect. Arms in a group share one normal run, so the 22 rows are about 10 independent events, not 22.

DEVIATIONS
- None from the frozen plan. PLAN_ADDENDUM.md holds readings Z1-Z6, all written after the freeze and before any run:
  - Z1: arm set = W-O's (recorded arms plus the auto-added site_all / channel_all companions). A recorded-only class is reported beside it.
  - Z2: exact label inputs; p_min is REL3's for P256.
  - Z3: a CARRIER-OVERSHOOT class for a case the plan does not name. It is not counted as NAMED.
  - Z4: known-answer seeds are 0x680 xor 1 and 0x680 xor 2.
  - Z5: budget scheduler. It stops launching when finished CPU plus W-O's measured cost for claimed and next groups would exceed 7.3 core-h, and it keeps the plan's order strictly.
  - Z6: the consistency check uses W-U's non-strict rel3 column.

DISAGREEMENTS
- W-O (absolute CHANCE): 314 of the covered rows are CHANCE under W-O's absolute verdict. Under the relative rule 200 are CHANCE_REL, but 48 are FLIP_REL, 35 NO_EFFECT_REL and 31 INDETERMINATE. Also, 5 of W-O's absolute FLIP rows read CHANCE_REL here.
- W-U: the consistency bar was missed (92.7%) on fresh seeds. REL3's DETERMINED status does not guarantee the same label on a new draw at intermediate z (about 0.35-0.6).
- W-Q (group unit): I agree that the group is the right unit. Which arms are counted matters: W-O's auto-added companion arms move 14 groups to CARRIER-PARTIAL (8 recorded-only vs 22 all-arms). A carrier table should state its arm set.
- Point finding: in 78f3b0ec offset 11, channel_all and channel_count read FLIP_REL (z -0.56, PARTIAL) while site_all and S read NO_EFFECT_REL. W-U had all four as INDETERMINATE.

PYTEST
- Command: `CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider test_zbook.py`, run in W-Z/.
- Result: 3 passed, RC = 0 (out/pytest.txt). It checks group order and coverage (249 groups, 64 AMBIGUOUS rows in 31 groups, 733 rows), the group-class rules including a must-fail, and that the saved pair arrays round-trip to the label inputs.
- The swap_rel suite (11 passed, RC = 0) was run as the first known-answer gate.

LEASES
- skullport:cpu8, lease lse-d4c8d5dcc30b, acquired about 11:55Z and renewed at 12:35Z.
- Released at about 12:50Z; lease status shows no skullport lease.
- The known-answer run (1 thread) ran before the lease, unleased.
- Worker PIDs were 27532, 27520, 23144, 25856, 23056, 17708, 27240 and 15492. All exited; no python run processes remain.

COMPUTE
- Specimen runs: 25,070 CPU-s = 6.96 core-h.
- Known-answer run: 114 s; tests: negligible.
- Total about 7.0 core-h, within the 8 core-h cap. Wall time about 1 h.
- Outputs total 1.7 MB.

FILES (all under F:/Prometheus-worktrees/ananke-base-role/roles/Ananke/research/workers/W-Z/)
- Notes: PLAN_ADDENDUM.md, LOG.md
- Scripts: zcommon.py, ka_z.py, run_z.py, analyze_z.py, test_zbook.py
- Known-answer output: out/ka_z.json, out/ka_z.log
- Run output: out/runs_w0..7.jsonl, out/pairs/<gid>.npz (124 files), out/claims/, out/STOP
- Tables: out/row_table.csv, out/group_table.csv, out/summary.json
- Other: out/pytest.txt, out/lease_acquire.txt, out/pids.txt, logs/w0..7.log
