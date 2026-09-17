# SFE RESTART RECEIPT -- 2026-09-17T10:50:59Z

    A deployed change to engine code, schema, route surface and contract received ONE clean
    process restart before qualification (order s7). No hot reload; no inherited state.

    stop        stopped 8140   (child python + launcher parent; port waited free)
    start       by the pinned supervisor D:\Prometheus-data\sfe\sfengine_m2_watchdog.ps1
                (the running instance is the supervised one)
    migration   sfe/store.py _migrate_8_to_9 at first open; meta.schema_version 8 -> 9
    outage      20.3 s (stop -> /v2/version answering)
    process     pid 8140 started 2026-09-16T17:22:44Z  ->  pid 5596 started 2026-09-17T10:51:30Z
    instance    eng_906356f7fb1da180131f9290  (unchanged; ledger state)
    build       sha256:bc8d3a0caea47efdc766aaa49abdba9a9d1a5ac9dc35f3b722d0aa3397e99153
    schema      9 live, 9 in the ledger
    routes      72  digest sha256:1e476859f79f901a5fac144c218479dbd28f5d3d4b782a3494bf3f2d082d59ae
    ledger      D:\Prometheus-data\sfe\engine.db  events 10995
    bind        192.168.1.191:8811  (https://192.168.1.191:8811)
    descriptor  deploy/DEPLOYED_BUILD_M2.json re-pinned to 1b9286292e3f / sha256:bc8d3a0caea47
    verify      deploy/release_v9.py verify re-records the same identities and compares to apply.json

    Qualification followed at 2026-09-17T10:52:29Z: 20 shapes held, 0 broke (qualify.json).
