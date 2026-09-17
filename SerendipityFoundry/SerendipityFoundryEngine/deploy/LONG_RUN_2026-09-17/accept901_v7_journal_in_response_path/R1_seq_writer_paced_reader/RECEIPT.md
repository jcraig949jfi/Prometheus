# Long-run load receipt (2026-09-17T16:04:47Z)

engine sha256:4f7cef0f82e9e  schema 9  worlds 20 x gens 1000, producers 1 + 1 reader

    totals   {"events": 82660, "observations": 20000, "experiments": 20000, "artifacts": 200, "checkpoints": 380, "worlds": 40}
    storage  db 84.5 MB, wal 3408.8 MB, 1072 bytes/event -> 102.3 MB per 100K events
    phases   {"write_s": 174.7, "full_event_walk_s": 2.51, "full_event_walk_pages": 180, "default_obs_list_x3_s": 0.076, "kill_to_port_free_s": 1.12, "relaunch_to_version_s": 5.87, "anchor_sample_s": 0.11}
    restart  identity_same=True anchors 50/50
    5xx 0  stalls>5s 2  write_lock {"acquisitions": 0, "failures": 0, "max_wait_s": 0.0, "waits_over_1s": 0, "last_wait_s": null, "last_at": null}
    wal_max_bytes 3561179712  checkpointer {"alive": true, "runs": 0, "truncates": 0, "errors": 0, "max_wal_bytes_seen": 0}

    route                                     q1 p50/p95/max ms        q4 p50/p95/max ms      n
    GET /v2/health                           -/-/-                    64.0/80.2/80.2         2
    GET /v2/version                          548.4/1092.1/1092.1      3591.5/3591.5/3591.5   3
    GET /v2/worlds/{id}/events               -/-/-                    14.1/23.8/39.1         181
    GET /v2/worlds/{id}/observations         5.2/20.3/29.9            5.3/17.8/299.1         713
    POST /v2/audit/verify-anchor             -/-/-                    0.0/8.6/14.8           50
    POST /v2/clients                         4.4/4.4/4.4              -/-/-                  1
    POST /v2/sessions                        0.0/0.0/0.0              -/-/-                  1
    POST /v2/worlds                          0.0/19.5/19.5            1.3/13.6/13.6          20
    POST /v2/worlds/{id}/artifacts           1.5/15.8/119.0           0.0/9.3/14.5           200
    POST /v2/worlds/{id}/checkpoint          0.0/8.3/15.8             0.0/11.3/13.5          380
    POST /v2/worlds/{id}/events              0.0/9.9/41.2             0.0/10.0/85.4          2000
    POST /v2/worlds/{id}/experiments         0.0/11.1/115.3           0.0/11.7/1178.1        20000
    POST /v2/worlds/{id}/experiments/{id}/co 0.0/9.8/143.0            0.0/11.4/515.0         20000
    POST /v2/worlds/{id}/fork                1.4/10.5/10.5            1.8/13.9/13.9          20
    POST /v2/worlds/{id}/observations        0.0/11.0/196.9           0.0/11.8/2601.0        20000
    POST /v2/worlds/{id}/start               0.0/3.6/3.6              2.6/8.5/8.5            20
    POST /v2/worlds/{id}/terminate           2.8/9.3/9.3              0.0/0.0/0.0            20
