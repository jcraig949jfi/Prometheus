# E-BEL-MD failure ledger (Bellerophon multi-day campaign)

Every implementation, measurement, cost or reporting failure found, in the order found. Nothing is edited away.

| id | when | class | what failed | evidence | disposition |
|---|---|---|---|---|---|
| MD-F1 | pre-freeze scale probe | cost | per-tick cost looked superlinear; the profile showed the measurement-only competence tracker was 77% of the time | receipts/SCALE_PROBE_2026-09-26.json, receipts/MEASUREMENT_SPEEDUP_2026-09-26.md | verify_exact + stop_at_first_out, proven byte-identical (2.8x) |
| MD-F2 | smoke pilot | metric | lineage self-replicators often fail the isolated self_copy test, making joint robustness mostly ineligible | smoke results | Q2 eligibility changed to task competence BEFORE freeze |
| MD-F3 | smoke replay | tooling | 0/6 replay equality on a first attempt: the smoke records predated the robustness change (stale, not non-deterministic) | journal 2026-09-26 | fresh smoke replayed 30/30 |
| MD-F4 | pre-freeze | reporting | a smoke-analysis MD_RESULTS.json was committed by mistake | 8252930a2 | removed 99e8665fe |
| MD-F5 | production | cost model | the pilots underestimated the tails: max run 6,764 s vs 2,034 s; max worker 2,223 MB vs 1,016 MB; 47.1 h active vs ~27 h estimated | receipts/POSTHOC_SECONDARIES.json ops | cap and reserve held; pilots with 8 pairs do not sample the long-survivor tail |
| MD-F6 | analysis | defect (DEF-BEL-002) | md_analysis.py sets `holds` without conditioning on instrument_ok | Artemis R-08 (#877) | prereg s9 applied in the report; instrument_ok TRUE; frozen script not edited |
| MD-F7 | analysis | metric validity (DEF-BEL-003) | the endpoint reads the lineage SR label, not isolated capability | Odysseus #748/#804 | post-hoc label audit (report s3) |
| MD-F8 | analysis | omission | md_analysis.py omitted the per-K Q3 rates that prereg s8 names | merge reviews | computed post-hoc (receipts/POSTHOC_SECONDARIES.json) |
| MD-F9 | report draft | overclaims | an edit-distance mechanism, "replaces ECHO", "4.7 vs 6.7" as a horizon effect, "every contrast stronger", an untested base-income mechanism | Fabric reviews tsk-bc42e48a52be / tsk-def7523bd2f2 | report revised (s2, s3, s7) |
| MD-F10 | record | reproducibility | results.jsonl and the ops logs are host-local; several claims cannot be recomputed from Git | review s6 | stated in report s4; a durable archive is recommended |
