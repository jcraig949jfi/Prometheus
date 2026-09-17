# SFE BENCHMARK RECEIPT -- point release 2026-09

    Every fixture below is a "does the engine RECORD it" test, never "does
    the algorithm win". Numbers are from the named receipts.

    fixture                                    result           receipt
    unit suite (merged tree bc8d3a0c)          505 passed       pytest, tests/
    v9 facts (D1-D4, D6, D7 + cheat controls)  13/13            tests/test_sfe_v9_facts.py
    read surface (D5, D8, D9)                  8/8              tests/test_sfe_v9_read_surface.py
    Campaign-3-shaped acceptance (order s12)   PASS             tests/test_sfe_v9_campaign_fixture.py
    five-word grep over sfe/*.py               0 hits           test_engine_source_never_uses_the_scientific_words
    strict extra-field on every mutating route 25+ routes, 422  test_every_mutating_route_refuses_an_unknown_field_the_same_way
    D11 restart/duplicate/checkpoint, scratch  16/16 shapes     deploy/POINT_RELEASE_2026-09-17/ (smoke) ;
      kill -9 -> port free 1.11 s; relaunch -> version 0.53 s   $TEMP/longrun_smoke.json (n=300)
    D11 on PRODUCTION (running-engine mode)    15/15 shapes     deploy/POINT_RELEASE_2026-09-17/longrun_restart_production.json
    harness (12 capabilities) on production    12/12            qualify.json
    isolation (7 properties) on production     7/7              qualify.json
    contract gate on the landed contract       0 / 0 w/ routes  gate_after_landing*.txt
    preflight / apply / qualify                8/8, 12/12, 20/20 preflight.json, apply.json, qualify.json
    long-run 20 x 1000, 2 producers + reader   flat medians;    deploy/LONG_RUN_2026-09-17/w20g1000/
                                               150 stalls 5-13 s (FINDING, section 4 of SFE_LONG_RUN_REPORT.md)
    long-run control, --no-reader              [pending]        deploy/LONG_RUN_2026-09-17/w20g1000_noreader/
