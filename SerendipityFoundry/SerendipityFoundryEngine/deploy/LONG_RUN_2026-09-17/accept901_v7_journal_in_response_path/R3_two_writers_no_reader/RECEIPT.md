# Long-run load receipt (2026-09-17T16:08:18Z)

engine sha256:4f7cef0f82e9e  schema 9  worlds 20 x gens 1000, producers 2 + 1 reader

    totals   {"events": 82660, "observations": 20000, "experiments": 20000, "artifacts": 200, "checkpoints": 380, "worlds": 40}
    storage  db 84.3 MB, wal 3425.3 MB, 1070 bytes/event -> 102.0 MB per 100K events
    phases   {"write_s": 203.4, "full_event_walk_s": 2.87, "full_event_walk_pages": 180, "default_obs_list_x3_s": 0.074, "kill_to_port_free_s": 1.23, "relaunch_to_version_s": 0.54, "anchor_sample_s": 0.11}
    restart  identity_same=True anchors 50/50
    5xx 0  stalls>5s 2  write_lock {"acquisitions": 0, "failures": 0, "max_wait_s": 0.0, "waits_over_1s": 0, "last_wait_s": null, "last_at": null}
    wal_max_bytes 3503915832  checkpointer {"alive": true, "runs": 0, "truncates": 0, "errors": 0, "max_wal_bytes_seen": 0}

    route                                     q1 p50/p95/max ms        q4 p50/p95/max ms      n
    GET /v2/health                           -/-/-                    54.8/63.3/63.3         2
    GET /v2/version                          548.8/1097.7/1097.7      538.6/538.6/538.6      3
    GET /v2/worlds/{id}/events               -/-/-                    15.1/27.4/260.0        181
    GET /v2/worlds/{id}/observations         -/-/-                    27.3/29.0/29.0         3
    POST /v2/audit/verify-anchor             -/-/-                    0.0/8.3/10.1           50
    POST /v2/clients                         0.0/0.0/0.0              -/-/-                  1
    POST /v2/sessions                        6.5/6.5/6.5              -/-/-                  1
    POST /v2/worlds                          0.0/15.7/15.7            8.0/24.1/24.1          20
    POST /v2/worlds/{id}/artifacts           3.4/17.9/228.1           3.1/29.9/1185.9        200
    POST /v2/worlds/{id}/checkpoint          2.0/30.8/48.2            1.5/33.8/810.2         380
    POST /v2/worlds/{id}/events              1.5/16.5/106.7           0.0/17.9/63.4          2000
    POST /v2/worlds/{id}/experiments         1.8/17.7/4451.5          1.5/19.4/1403.2        20000
    POST /v2/worlds/{id}/experiments/{id}/co 1.0/17.1/6130.7          0.0/17.7/1158.8        20000
    POST /v2/worlds/{id}/fork                5.7/15.7/15.7            6.1/17.4/17.4          20
    POST /v2/worlds/{id}/observations        2.0/21.0/6126.7          1.5/20.2/3550.5        20000
    POST /v2/worlds/{id}/start               3.5/47.4/47.4            2.0/15.8/15.8          20
    POST /v2/worlds/{id}/terminate           0.8/19.7/19.7            4.2/17.7/17.7          20
