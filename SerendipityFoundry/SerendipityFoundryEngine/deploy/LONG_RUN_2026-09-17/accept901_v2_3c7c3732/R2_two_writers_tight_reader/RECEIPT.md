# Long-run load receipt (2026-09-17T14:20:24Z)

engine sha256:3c7c3732ea131  schema 9  worlds 20 x gens 1000, producers 2 + 1 reader

    totals   {"events": 82660, "observations": 20000, "experiments": 20000, "artifacts": 200, "checkpoints": 380, "worlds": 40}
    storage  db 84.2 MB, wal 10.7 MB, 1068 bytes/event -> 101.9 MB per 100K events
    phases   {"write_s": 370.4, "full_event_walk_s": 2.96, "full_event_walk_pages": 180, "default_obs_list_x3_s": 0.067, "kill_to_port_free_s": 1.12, "relaunch_to_version_s": 0.53, "anchor_sample_s": 0.13}
    restart  identity_same=True anchors 50/50
    5xx 0  stalls>5s 0  write_lock {"acquisitions": 0, "failures": 0, "max_wait_s": 0.0, "waits_over_1s": 0, "last_wait_s": null, "last_at": null}
    wal_max_bytes 85378792  checkpointer {"alive": true, "runs": 0, "truncates": 0, "errors": 0, "max_wal_bytes_seen": 0}

    route                                     q1 p50/p95/max ms        q4 p50/p95/max ms      n
    GET /v2/health                           -/-/-                    54.9/63.7/63.7         2
    GET /v2/version                          540.4/1080.8/1080.8      525.6/525.6/525.6      3
    GET /v2/worlds/{id}/events               -/-/-                    15.4/29.3/333.3        181
    GET /v2/worlds/{id}/observations         7.7/20.2/387.7           6.8/19.1/301.7         38374
    POST /v2/audit/verify-anchor             -/-/-                    0.0/8.3/15.8           50
    POST /v2/clients                         10.6/10.6/10.6           -/-/-                  1
    POST /v2/sessions                        0.0/0.0/0.0              -/-/-                  1
    POST /v2/worlds                          3.7/33.8/33.8            9.9/16.0/16.0          20
    POST /v2/worlds/{id}/artifacts           6.2/51.0/387.0           8.7/112.3/1016.0       200
    POST /v2/worlds/{id}/checkpoint          4.0/26.9/47.5            10.3/31.5/35.6         380
    POST /v2/worlds/{id}/events              3.0/29.3/431.0           5.5/32.6/597.2         2000
    POST /v2/worlds/{id}/experiments         5.1/30.4/815.4           8.8/34.7/2445.9        20000
    POST /v2/worlds/{id}/experiments/{id}/co 1.7/24.7/1377.1          4.0/31.8/1518.2        20000
    POST /v2/worlds/{id}/fork                7.4/15.7/15.7            10.5/11.4/11.4         20
    POST /v2/worlds/{id}/observations        5.4/31.1/808.4           9.6/35.8/2355.8        20000
    POST /v2/worlds/{id}/start               2.4/9.5/9.5              8.6/17.3/17.3          20
    POST /v2/worlds/{id}/terminate           2.3/7.7/7.7              6.8/17.5/17.5          20
