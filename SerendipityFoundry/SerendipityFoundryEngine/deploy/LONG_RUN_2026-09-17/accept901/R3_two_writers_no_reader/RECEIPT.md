# Long-run load receipt (2026-09-17T16:28:08Z)

engine sha256:699ca0f952448  schema 9  worlds 20 x gens 1000, producers 2 + 1 reader

    totals   {"events": 82660, "observations": 20000, "experiments": 20000, "artifacts": 200, "checkpoints": 380, "worlds": 40}
    storage  db 84.0 MB, wal 3457.0 MB, 1066 bytes/event -> 101.7 MB per 100K events
    phases   {"write_s": 131.2, "full_event_walk_s": 3.32, "full_event_walk_pages": 180, "default_obs_list_x3_s": 0.064, "kill_to_port_free_s": 10.49, "relaunch_to_version_s": 4.86, "anchor_sample_s": 0.1}
    restart  identity_same=True anchors 50/50
    5xx 0  stalls>5s 0  write_lock {"acquisitions": 0, "failures": 0, "max_wait_s": 0.0, "waits_over_1s": 0, "last_wait_s": null, "last_at": null}
    wal_max_bytes 3566791152  checkpointer {"alive": true, "runs": 0, "truncates": 0, "errors": 0, "max_wal_bytes_seen": 0}

    route                                     q1 p50/p95/max ms        q4 p50/p95/max ms      n
    GET /v2/health                           -/-/-                    47.0/47.6/47.6         2
    GET /v2/version                          555.2/1109.0/1109.0      2563.0/2563.0/2563.0   3
    GET /v2/worlds/{id}/events               -/-/-                    14.2/27.9/735.1        181
    GET /v2/worlds/{id}/observations         -/-/-                    19.5/25.7/25.7         3
    POST /v2/audit/verify-anchor             -/-/-                    0.0/11.2/15.9          50
    POST /v2/clients                         7.2/7.2/7.2              -/-/-                  1
    POST /v2/sessions                        1.0/1.0/1.0              -/-/-                  1
    POST /v2/worlds                          1.8/7.6/7.6              0.0/1.5/1.5            20
    POST /v2/worlds/{id}/artifacts           1.6/23.5/31.5            2.0/31.2/33.3          200
    POST /v2/worlds/{id}/checkpoint          0.0/31.5/48.0            0.0/15.7/18.7          380
    POST /v2/worlds/{id}/events              0.0/18.9/38.0            0.0/22.1/46.9          2000
    POST /v2/worlds/{id}/experiments         0.0/18.4/234.6           0.0/20.6/96.0          20000
    POST /v2/worlds/{id}/experiments/{id}/co 0.0/17.4/232.6           0.0/16.8/67.5          20000
    POST /v2/worlds/{id}/fork                0.0/2.0/2.0              0.7/6.2/6.2            20
    POST /v2/worlds/{id}/observations        0.0/22.4/221.0           0.0/21.4/78.9          20000
    POST /v2/worlds/{id}/start               10.3/21.7/21.7           0.0/1.7/1.7            20
    POST /v2/worlds/{id}/terminate           3.0/20.7/20.7            0.0/31.4/31.4          20
