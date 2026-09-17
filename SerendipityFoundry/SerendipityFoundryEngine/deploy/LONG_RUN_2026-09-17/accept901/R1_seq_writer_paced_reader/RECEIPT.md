# Long-run load receipt (2026-09-17T16:25:35Z)

engine sha256:699ca0f952448  schema 9  worlds 20 x gens 1000, producers 1 + 1 reader

    totals   {"events": 82660, "observations": 20000, "experiments": 20000, "artifacts": 200, "checkpoints": 380, "worlds": 40}
    storage  db 84.4 MB, wal 3421.1 MB, 1071 bytes/event -> 102.2 MB per 100K events
    phases   {"write_s": 127.9, "full_event_walk_s": 2.53, "full_event_walk_pages": 180, "default_obs_list_x3_s": 0.094, "kill_to_port_free_s": 1.24, "relaunch_to_version_s": 0.55, "anchor_sample_s": 0.1}
    restart  identity_same=True anchors 50/50
    5xx 0  stalls>5s 0  write_lock {"acquisitions": 0, "failures": 0, "max_wait_s": 0.0, "waits_over_1s": 0, "last_wait_s": null, "last_at": null}
    wal_max_bytes 3482722552  checkpointer {"alive": true, "runs": 0, "truncates": 0, "errors": 0, "max_wal_bytes_seen": 0}

    route                                     q1 p50/p95/max ms        q4 p50/p95/max ms      n
    GET /v2/health                           -/-/-                    113.8/172.0/172.0      2
    GET /v2/version                          544.8/1089.5/1089.5      544.4/544.4/544.4      3
    GET /v2/worlds/{id}/events               -/-/-                    14.2/24.3/48.5         181
    GET /v2/worlds/{id}/observations         6.4/27.2/36.3            4.6/24.2/71.1          577
    POST /v2/audit/verify-anchor             -/-/-                    0.0/9.4/15.9           50
    POST /v2/clients                         0.0/0.0/0.0              -/-/-                  1
    POST /v2/sessions                        0.0/0.0/0.0              -/-/-                  1
    POST /v2/worlds                          0.0/17.0/17.0            0.0/2.5/2.5            20
    POST /v2/worlds/{id}/artifacts           0.0/26.3/148.5           1.5/11.1/15.7          200
    POST /v2/worlds/{id}/checkpoint          0.0/7.4/10.8             0.0/9.4/27.0           380
    POST /v2/worlds/{id}/events              0.0/9.4/132.6            0.0/11.5/24.9          2000
    POST /v2/worlds/{id}/experiments         0.0/11.6/346.7           0.0/12.1/71.5          20000
    POST /v2/worlds/{id}/experiments/{id}/co 0.0/9.7/127.6            0.0/10.6/67.9          20000
    POST /v2/worlds/{id}/fork                0.0/0.0/0.0              0.0/16.0/16.0          20
    POST /v2/worlds/{id}/observations        0.0/11.2/254.5           0.0/11.3/110.2         20000
    POST /v2/worlds/{id}/start               0.0/22.6/22.6            0.0/13.5/13.5          20
    POST /v2/worlds/{id}/terminate           3.5/9.3/9.3              1.7/13.1/13.1          20
