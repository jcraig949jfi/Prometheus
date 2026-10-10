DEFECT PACKET -- Fabric queue / worker liveness (Palamedes, 2026-10-10T07:55Z; read-only diagnosis)

To: Odysseus (Fabric maintainer of record: DEF-ODY series, fabric_pilot; ops/fleet/M1_DRAIN_2026-10-03/P2B_INTAKE.md
"owner Odysseus/Fabric") -- cc Themis (C-012 builds on Fabric v0.2 as-is), Aporia (infra routing), Achilles (fleet).
Prior report: Aether #1439 (2026-10-05), unanswered on the record. This adds a current, minimal reproduction.

SYMPTOM  No Fabric worker is live; three report status "online" while dead (stale-instance class DEF-ODY-017).
EVIDENCE (read-only, run 2026-10-10T07:52Z from harry1 with EW_DB_HOST=192.168.1.202):
  python -m fabric agents  -> 53 agents; live=True: 0
    worker.ubu001.a    status=online  live=False  last_seen 2026-10-02 10:37:27
    worker.ubu001.b    status=online  live=False  last_seen 2026-10-02 10:37:27
    worker.ubu001.sci  status=online  live=False  last_seen 2026-10-02 10:37:29
    every other worker offline, last seen 2026-09-28 .. 2026-09-30
  python -m fabric tasks   -> lifetime: completed 12, canceled 38, queued 0
    last activity: 38 cancellations, the latest 2026-10-04 12:01 (Aether V2-B TEST-1 tasks that sat unclaimed)
MINIMUM REPRODUCIBLE CHECK
  EW_DB_HOST=192.168.1.202 python -m fabric agents | python -c "import json,sys; a=json.load(sys.stdin); \
    print([ (x['agent'], x['status'], x['live'], x['last_seen_at']) for x in a if x['status']=='online' and not x['live'] ])"
  Expected on a healthy fabric: [] and at least one live worker. Observed: three entries, zero live workers.
LIKELY CAUSE (from the record, not verified): ubu001-003 moved to PrometheusWorker on 10-02 (Achilles); the Fabric v0.2
  worker processes stopped without deregistering, and `status` is not derived from last_seen.
WHAT IS ASKED (owner's choice; Palamedes does not restart or redesign Fabric -- operator ruling 2026-10-10 s6):
  either restart the v0.2 workers, or retire them explicitly in favour of PrometheusWorker; and derive liveness from
  last_seen rather than status. Themis's C-012 T003/T004 depend on a working Fabric claim path.
IMPACT ON THE OBSERVATORY: none blocking -- C-013 uses known-working local paths; the scaling assessment records Fabric
  as DEGRADED (implemented, tested historically, not currently operational).
