# SFE DEPLOYMENT RECEIPT -- point release 2026-09 (schema 8 -> 9)

    seat       Daedalus[m2-d6ecd70b]      applied  2026-09-17T10:50:59Z
    engine     https://192.168.1.191:8811 (M2 production)
    commit     1b9286292e3fb7755282a468f55bc97564ab9382  (origin/main)
    tools      deploy/release_v9.py preflight | apply ; deploy/qualify_v9.py
    receipts   deploy/POINT_RELEASE_2026-09-17/{preflight,apply,qualify}.json

PREFLIGHT (order s8) -- 8/8 PASS at 2026-09-17T10:50:48Z
    [PASS] production ledger identity
    [PASS] current schema is 8 (this release migrates 8 -> 9)
    [PASS] pin agrees with the running build
    [PASS] release commit resolvable
    [PASS] candidate tree hashes to a NEW build
    [PASS] no scientific writes in the last 10 min
    [PASS] no work in flight
    [PASS] backup written and verified
    backup     D:\Prometheus-data\sfe\backup\engine.db.pre-schema9-20260917T105054Z.bak
               sha256 394202ba014c19a653ebc4d3e42cc35aae14bbb0d7bdfce474b959d362d88bbd  events 10995  schema 8
    blobs      255 files (untouched by the migration)
    consumers  additive routes read INCOMPLETE-covered, never DRIFT, for consumers that declare their routes (#256 C5); the schema bump 8->9 reads as a mismatch to any gate until the contract is regenerated and landed in the same window; no consumer process is running (C3 closed #326; Vivarium not launched, #318/#329); default list responses gain keys, no consumer parses them positionally
    The first preflight (10:40:51Z) REFUSED on 36 events in the prior 10 min -- a 7 s burst from
    clients pewC4-1789641629 / lineage-1789641631* (a fixture from 192.168.1.191); broadcast #334
    asked for quiet; the second preflight (10:50:54Z) found 0 events in 10 min and wrote a backup
    with the identical sha256 (nothing had changed in between).

APPLY (order s7) -- 12/12 PASS, outage 20.3 s
    [PASS] still nobody writing {"events_last_10min": 0}
    [PASS] pinned worktree advanced {"head": "1b9286292e3f"}
    [PASS] pinned tree reproduces the candidate hash {}
    [PASS] engine answers after restart {"outage_s": 20.3}
    [PASS] process is NEW (start time advanced, pid changed) {"before": "2026-09-16T17:22:44Z", "after": "2026-09-17T10:51:30Z"}
    [PASS] engine instance UNCHANGED (ledger state) {}
    [PASS] source hash == candidate {"live": "sha256:bc8d3a0caea47efdc766aaa49abdba9a9d1a5ac9dc35f3b722d0aa3397e99153"}
    [PASS] schema 9 live AND in the ledger {}
    [PASS] route digest changed (4 routes added) {"before": 68, "after": 72}
    [PASS] ledger path and bind unchanged {"bind": "192.168.1.191"}
    [PASS] no event lost across the migration {"events": 10995}
    [PASS] capabilities advertises the release {}

IDENTITIES (order s7 list), BEFORE -> AFTER
    process start (UTC)          2026-09-16T17:22:44Z                           2026-09-17T10:51:30Z                          
    pid                          8140                                           5596                                          
    engine_instance_id           eng_906356f7fb1da180131f9290                   eng_906356f7fb1da180131f9290                  
    engine_source_hash           sha256:4dbcd3fd249f0e2febef77b0a17379bca489a5f sha256:bc8d3a0caea47efdc766aaa49abdba9a9d1a5ac
    source_commit                dd10c90748228fd99f994c068748379de0d474bc       1b9286292e3fb7755282a468f55bc97564ab9382      
    schema (live / ledger)       8 / 8                                          9 / 9                                         
    route digest                 sha256:ba14a1918e4d0222bb4df22f1b8f58114f4be9a sha256:1e476859f79f901a5fac144c218479dbd28f5d3
    routes                       68                                             72                                            
    ledger                       D:\Prometheus-data\sfe\engine.db               D:\Prometheus-data\sfe\engine.db              
    ledger events                10995                                          10995                                         
    bind endpoint                192.168.1.191 https://192.168.1.191:8811       192.168.1.191 https://192.168.1.191:8811      
    descriptor pin (hash)        sha256:4dbcd3fd249f0e2febef77b0a17379bca489a5f sha256:bc8d3a0caea47efdc766aaa49abdba9a9d1a5ac
    cmdline after: "C:\Users\James\AppData\Local\Programs\Python\Python312\python.exe" "D:\Prometheus-worktrees\daedalus-sfengine\SerendipityFoundry\SerendipityFoundryEngine\serve.py" --db "D:\Prometheus-data\sfe\engine.db" --host 192.168.1.191 --port 8811 --max-artifact-bytes 33554432 --tls-cert "D:\Prometheus-data\sfe\m2.crt" --tls-key "D:\Prometheus-data\sfe\m2.key" 
    Every difference is the expected one (new process, new build, new schema, +4 routes);
    every identity that must not move (instance, ledger path, bind, event count) did not.

CONTRACT
    regenerated AFTER the restart (Harmonia's generator refuses pre-deploy contracts across a
    schema bump); live + loopback scratch probe of the same build; traps/bounds/policy identical
    to the committed ones modulo generation stamps; landed at main bef42b7df with a `landed`
    provenance block; conformance_check 0 plain and 0 with both consumers' 25 declared routes
    (gate_after_landing*.txt). Previous contract: sfe_contract.PREVIOUS_schema8.json.

QUALIFICATION (order s9) -- 20 held, 0 broke at 2026-09-17T10:52:29Z  (qualify.json)
    [HELD] engine is schema 9 on the production ledger
    [HELD] v9 columns present
    [HELD] every pre-migration world reads NULL facts (no backfill)
    [HELD] every pre-migration observation reads logical_time NULL
    [HELD] head hashes of the 25 oldest worlds unchanged
    [HELD] event count up to the backup's last seq identical
    [HELD] pre-migration observation anchors verify
    [HELD] capabilities route: schema 9, features, read semantics, no forbidden words
    [HELD] manifest hash round-trip
    [HELD] logical_time write/read
    [HELD] generic events: ordered, idempotent duplicate, undeclared kind refused
    [HELD] pagination traversal == single page; resume from a cursor exact
    [HELD] artifact list
    [HELD] checkpoint digest + fork ancestry + changed-field diff
    [HELD] advisory read semantics + strict extra-field rejection
    [HELD] typed termination write/read; writes refused after
    [HELD] harness 12/12
    [HELD] isolation 7/7
    [HELD] contract gate CONFORMANT (0)
    [HELD] D11 fixture (running-engine mode) all shapes held
