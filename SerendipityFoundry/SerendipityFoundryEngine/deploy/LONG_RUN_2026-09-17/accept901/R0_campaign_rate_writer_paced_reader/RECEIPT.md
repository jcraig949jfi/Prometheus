# Long-run load receipt (2026-09-17T16:23:20Z)

engine sha256:699ca0f952448  schema 9  worlds 4 x gens 150, producers 1 + 1 reader

    totals   {"events": 2492, "observations": 600, "experiments": 600, "artifacts": 8, "checkpoints": 8, "worlds": 8}
    storage  db 2.9 MB, wal 8.3 MB, 1218 bytes/event -> 116.2 MB per 100K events
    phases   {"write_s": 331.8, "full_event_walk_s": 0.07, "full_event_walk_pages": 8, "default_obs_list_x3_s": 0.016, "kill_to_port_free_s": 1.12, "relaunch_to_version_s": 1.05, "anchor_sample_s": 0.08}
    restart  identity_same=True anchors 50/50
    5xx 0  stalls>5s 0  write_lock {"acquisitions": 0, "failures": 0, "max_wait_s": 0.0, "waits_over_1s": 0, "last_wait_s": null, "last_at": null}
    wal_max_bytes 8656152  checkpointer {"alive": true, "runs": 0, "truncates": 0, "errors": 0, "max_wal_bytes_seen": 0}

    route                                     q1 p50/p95/max ms        q4 p50/p95/max ms      n
    GET /v2/health                           -/-/-                    2.8/5.6/5.6            2
    GET /v2/version                          804.5/1606.9/1606.9      1045.4/1045.4/1045.4   3
    GET /v2/worlds/{id}/events               -/-/-                    10.4/25.0/25.0         9
    GET /v2/worlds/{id}/observations         -/-/-                    9.3/15.1/19.6          463
    POST /v2/audit/verify-anchor             -/-/-                    0.0/13.2/15.7          50
    POST /v2/clients                         8.9/8.9/8.9              -/-/-                  1
    POST /v2/sessions                        1.5/1.5/1.5              -/-/-                  1
    POST /v2/worlds                          3.1/3.1/3.1              0.0/0.0/0.0            4
    POST /v2/worlds/{id}/artifacts           0.5/1.0/1.0              0.0/0.0/0.0            8
    POST /v2/worlds/{id}/checkpoint          1.5/3.0/3.0              1.6/1.6/1.6            8
    POST /v2/worlds/{id}/events              0.0/10.1/10.1            0.0/12.6/12.6          60
    POST /v2/worlds/{id}/experiments         5.1/168.3/1039.4         35.8/47.1/92.4         600
    POST /v2/worlds/{id}/experiments/{id}/co 1.2/10.3/1114.2          5.7/16.3/31.1          600
    POST /v2/worlds/{id}/fork                -/-/-                    35.8/37.0/37.0         4
    POST /v2/worlds/{id}/observations        0.0/7.6/12.2             2.0/9.2/16.0           600
    POST /v2/worlds/{id}/start               7.7/7.7/7.7              0.0/0.0/0.0            4
    POST /v2/worlds/{id}/terminate           -/-/-                    8.1/16.1/16.1          4
