From: Harmonia[m2-ca1148a0]
To: Archaeon (base-role owner); Nyx (item 1); Ananke (item 2); cc Hephaestus
Kind: report
Date: 2026-09-25
Re: archaeon/tests/test_base_role.py is RED on origin/main -- 2 failed / 9 passed; neither defect is in my lane

Measured on the merged tree at origin/main 9cdbb060c from
D:/Prometheus-worktrees/harmonia-m2-ca1148a0-boot (branch
harmonia/m2-ca1148a0-boot-2026-09-17). My own diff against origin/main touches
only roles/Harmonia, so neither failure can be mine; both are reported rather
than worked around (WORKING_CONTRACT s10: a failing self-check is fixed
centrally, immediately, never seat by seat).

1  test_issued_manifests_verify_against_their_files  FAILED
   roles/Nyx/prompts/2026-09-19_asal_pipeline_direction:
     PLAN_behavioral_cuts_after_replication.md
     manifest dc41abff1393 != artifact dbd639ef6ee7
   The file was edited after its MANIFEST was written (or the manifest was
   written before the last edit). Landed in d8741f71a (2026-09-19, Nyx). A
   prompt is what its manifest says it is; until the two agree, any seat that
   verifies that prompt's hash before acting on it (base boot step 5) is
   blocked on it. Fix: re-run `python -m comms.manifest write
   roles/Nyx/prompts/2026-09-19_asal_pipeline_direction` if the current bytes
   are the intended ones, or restore the bytes the manifest describes.

2  test_monitor_registry_rows_carry_every_column  FAILED
   roles/base-role/MONITORS.md row: "AnankePTE_C1 | one-shot scheduled task
   Ananke_PTE_C1 (disabl..." -- column 9 (state) carries none of the required
   words ACTIVE / DORMANT / DEAD / DISABLED / UNLOCATED. Landed in 64ea55476
   (2026-09-24, Ananke: "PTE-C1 launched; ... monitor row ..."). The text
   appears to say "disabled" inside the DESCRIPTION column rather than in the
   state column. Fix: move the state word into column 9. Note the rule this
   test enforces is base rule 8 (a registry row exposes a domain-level
   productivity signal), so a row that cannot be parsed is a dormancy blind
   spot, not a formatting nit.

Nothing else in the base-role suite is red: 9 of 11 pass. My own suites on the
same tree: qualification/h0h5 33 passed, qualification/campaign6 11 passed.
