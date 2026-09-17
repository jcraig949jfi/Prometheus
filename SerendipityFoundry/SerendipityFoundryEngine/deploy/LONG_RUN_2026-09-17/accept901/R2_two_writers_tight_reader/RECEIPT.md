# Long-run load receipt (2026-09-17T16:32:39Z)

engine sha256:699ca0f952448  schema 9  worlds 20 x gens 1000, producers 2 + 1 reader

    totals   {"events": 82660, "observations": 20000, "experiments": 20000, "artifacts": 200, "checkpoints": 380, "worlds": 40}
    storage  db 84.4 MB, wal 3426.9 MB, 1070 bytes/event -> 102.0 MB per 100K events
    phases   {"write_s": 254.4, "full_event_walk_s": 2.57, "full_event_walk_pages": 180, "default_obs_list_x3_s": 0.055, "kill_to_port_free_s": 1.13, "relaunch_to_version_s": 9.71, "anchor_sample_s": 0.1}
    restart  identity_same=True anchors 50/50
    5xx 0  stalls>5s 0  write_lock {"acquisitions": 0, "failures": 0, "max_wait_s": 0.0, "waits_over_1s": 0, "last_wait_s": null, "last_at": null}
    wal_max_bytes 3582879752  checkpointer {"alive": true, "runs": 0, "truncates": 0, "errors": 0, "max_wal_bytes_seen": 0}

    route                                     q1 p50/p95/max ms        q4 p50/p95/max ms      n
    GET /v2/health                           -/-/-                    62.6/74.7/74.7         2
    GET /v2/version                          546.8/1093.6/1093.6      3089.1/3089.1/3089.1   3
    GET /v2/worlds/{id}/events               -/-/-                    14.6/26.1/44.6         181
    GET /v2/worlds/{id}/observations         8.9/21.7/153.1           9.1/22.7/52.5          22730
    POST /v2/audit/verify-anchor             -/-/-                    0.0/10.3/11.5          50
    POST /v2/clients                         0.0/0.0/0.0              -/-/-                  1
    POST /v2/sessions                        8.2/8.2/8.2              -/-/-                  1
    POST /v2/worlds                          4.9/78.0/78.0            5.6/8.7/8.7            20
    POST /v2/worlds/{id}/artifacts           6.5/37.8/47.8            7.4/37.8/47.2          200
    POST /v2/worlds/{id}/checkpoint          1.6/30.9/60.1            7.2/32.0/44.3          380
    POST /v2/worlds/{id}/events              1.5/26.2/97.5            4.0/31.6/63.6          2000
    POST /v2/worlds/{id}/experiments         2.0/29.6/275.6           7.1/33.5/472.8         20000
    POST /v2/worlds/{id}/experiments/{id}/co 0.0/23.5/291.5           1.5/31.0/472.8         20000
    POST /v2/worlds/{id}/fork                2.5/22.8/22.8            5.6/18.0/18.0          20
    POST /v2/worlds/{id}/observations        3.1/29.5/184.5           7.9/32.2/97.0          20000
    POST /v2/worlds/{id}/start               0.8/15.5/15.5            1.4/4.5/4.5            20
    POST /v2/worlds/{id}/terminate           2.1/42.7/42.7            3.5/27.6/27.6          20
