# Long-run load receipt (2026-09-17T16:14:46Z)

engine sha256:4f7cef0f82e9e  schema 9  worlds 20 x gens 1000, producers 2 + 1 reader

    totals   {"events": 82660, "observations": 20000, "experiments": 20000, "artifacts": 200, "checkpoints": 380, "worlds": 40}
    storage  db 84.4 MB, wal 3454.6 MB, 1071 bytes/event -> 102.1 MB per 100K events
    phases   {"write_s": 363.0, "full_event_walk_s": 2.59, "full_event_walk_pages": 180, "default_obs_list_x3_s": 0.065, "kill_to_port_free_s": 1.11, "relaunch_to_version_s": 18.9, "anchor_sample_s": 0.11}
    restart  identity_same=True anchors 50/50
    5xx 0  stalls>5s 5  write_lock {"acquisitions": 0, "failures": 0, "max_wait_s": 0.0, "waits_over_1s": 0, "last_wait_s": null, "last_at": null}
    wal_max_bytes 3611044072  checkpointer {"alive": true, "runs": 0, "truncates": 0, "errors": 0, "max_wal_bytes_seen": 0}

    route                                     q1 p50/p95/max ms        q4 p50/p95/max ms      n
    GET /v2/health                           -/-/-                    58.9/67.7/67.7         2
    GET /v2/version                          547.9/1095.9/1095.9      3575.6/3575.6/3575.6   3
    GET /v2/worlds/{id}/events               -/-/-                    15.6/25.6/48.7         181
    GET /v2/worlds/{id}/observations         8.4/20.5/141.9           6.0/17.7/11515.7       35457
    POST /v2/audit/verify-anchor             -/-/-                    0.0/10.0/15.7          50
    POST /v2/clients                         0.0/0.0/0.0              -/-/-                  1
    POST /v2/sessions                        0.0/0.0/0.0              -/-/-                  1
    POST /v2/worlds                          7.0/18.6/18.6            18.2/29.2/29.2         20
    POST /v2/worlds/{id}/artifacts           6.7/36.9/114.9           10.7/1590.0/3731.3     200
    POST /v2/worlds/{id}/checkpoint          4.8/31.2/47.1            8.8/36.6/263.5         380
    POST /v2/worlds/{id}/events              3.7/22.5/63.4            6.9/31.9/789.2         2000
    POST /v2/worlds/{id}/experiments         5.4/29.3/2214.2          8.9/32.6/4567.0        20000
    POST /v2/worlds/{id}/experiments/{id}/co 1.8/23.4/176.9           3.5/31.2/1960.7        20000
    POST /v2/worlds/{id}/fork                7.9/23.2/23.2            7.8/17.8/17.8          20
    POST /v2/worlds/{id}/observations        5.7/30.4/2215.6          10.0/34.5/11522.8      20000
    POST /v2/worlds/{id}/start               10.3/18.0/18.0           33.9/36.1/36.1         20
    POST /v2/worlds/{id}/terminate           7.7/18.1/18.1            7.3/12.0/12.0          20
