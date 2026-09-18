# Long-run load receipt (2026-09-17T16:01:41Z)

engine sha256:4f7cef0f82e9e  schema 9  worlds 4 x gens 150, producers 1 + 1 reader

    totals   {"events": 2492, "observations": 600, "experiments": 600, "artifacts": 8, "checkpoints": 8, "worlds": 8}
    storage  db 2.9 MB, wal 8.3 MB, 1220 bytes/event -> 116.3 MB per 100K events
    phases   {"write_s": 342.0, "full_event_walk_s": 0.09, "full_event_walk_pages": 8, "default_obs_list_x3_s": 0.012, "kill_to_port_free_s": 1.13, "relaunch_to_version_s": 1.05, "anchor_sample_s": 0.1}
    restart  identity_same=True anchors 50/50
    5xx 0  stalls>5s 0  write_lock {"acquisitions": 0, "failures": 0, "max_wait_s": 0.0, "waits_over_1s": 0, "last_wait_s": null, "last_at": null}
    wal_max_bytes 8750912  checkpointer {"alive": true, "runs": 0, "truncates": 0, "errors": 0, "max_wal_bytes_seen": 0}

    route                                     q1 p50/p95/max ms        q4 p50/p95/max ms      n
    GET /v2/health                           -/-/-                    9.8/17.9/17.9          2
    GET /v2/version                          540.0/1079.0/1079.0      1050.8/1050.8/1050.8   3
    GET /v2/worlds/{id}/events               -/-/-                    12.9/24.0/24.0         9
    GET /v2/worlds/{id}/observations         -/-/-                    7.8/14.1/16.1          473
    POST /v2/audit/verify-anchor             -/-/-                    0.0/9.8/11.5           50
    POST /v2/clients                         8.7/8.7/8.7              -/-/-                  1
    POST /v2/sessions                        0.0/0.0/0.0              -/-/-                  1
    POST /v2/worlds                          4.9/4.9/4.9              5.8/5.8/5.8            4
    POST /v2/worlds/{id}/artifacts           2.0/4.0/4.0              0.0/0.0/0.0            8
    POST /v2/worlds/{id}/checkpoint          1.0/2.0/2.0              0.0/0.0/0.0            8
    POST /v2/worlds/{id}/events              0.0/9.3/9.3              0.0/15.7/15.7          60
    POST /v2/worlds/{id}/experiments         7.7/377.4/1239.1         39.8/53.5/67.2         600
    POST /v2/worlds/{id}/experiments/{id}/co 2.8/12.1/15.9            3.5/15.8/23.1          600
    POST /v2/worlds/{id}/fork                -/-/-                    42.5/42.9/42.9         4
    POST /v2/worlds/{id}/observations        1.6/9.7/21.1             1.8/13.3/16.2          600
    POST /v2/worlds/{id}/start               1.5/1.5/1.5              0.0/0.0/0.0            4
    POST /v2/worlds/{id}/terminate           -/-/-                    3.9/6.1/6.1            4
