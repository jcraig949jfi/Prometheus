# Long-run load receipt (2026-09-17T14:10:12Z)

engine sha256:1e81fe000d345  schema 9  worlds 20 x gens 1000, producers 2 + 1 reader

    totals   {"events": 82660, "observations": 20000, "experiments": 20000, "artifacts": 200, "checkpoints": 380, "worlds": 40}
    storage  db 83.5 MB, wal 91.1 MB, 1059 bytes/event -> 101.0 MB per 100K events
    phases   {"write_s": 190.9, "full_event_walk_s": 2.99, "full_event_walk_pages": 180, "default_obs_list_x3_s": 0.066, "kill_to_port_free_s": 1.11, "relaunch_to_version_s": 0.54, "anchor_sample_s": 0.11}
    restart  identity_same=True anchors 50/50
    5xx 0  stalls>5s 2  write_lock {"acquisitions": 0, "failures": 0, "max_wait_s": 0.0, "waits_over_1s": 0, "last_wait_s": null, "last_at": null}
    wal_max_bytes 143219472  checkpointer {"alive": true, "runs": 0, "truncates": 0, "errors": 0, "max_wal_bytes_seen": 0}

    route                                     q1 p50/p95/max ms        q4 p50/p95/max ms      n
    GET /v2/health                           -/-/-                    60.4/74.1/74.1         2
    GET /v2/version                          795.5/1591.0/1591.0      534.8/534.8/534.8      3
    GET /v2/worlds/{id}/events               -/-/-                    15.1/28.5/360.2        181
    GET /v2/worlds/{id}/observations         -/-/-                    22.2/28.2/28.2         3
    POST /v2/audit/verify-anchor             -/-/-                    0.0/7.5/11.3           50
    POST /v2/clients                         9.2/9.2/9.2              -/-/-                  1
    POST /v2/sessions                        3.7/3.7/3.7              -/-/-                  1
    POST /v2/worlds                          20.5/40.9/40.9           0.8/2.0/2.0            20
    POST /v2/worlds/{id}/artifacts           3.0/20.0/458.7           3.5/481.6/1063.2       200
    POST /v2/worlds/{id}/checkpoint          2.0/23.6/477.7           1.7/29.1/31.8          380
    POST /v2/worlds/{id}/events              1.5/18.9/90.6            1.5/16.3/50.2          2000
    POST /v2/worlds/{id}/experiments         1.6/17.5/493.0           2.0/18.4/1763.4        20000
    POST /v2/worlds/{id}/experiments/{id}/co 1.0/16.7/570.1           1.5/17.6/1432.9        20000
    POST /v2/worlds/{id}/fork                3.7/9.6/9.6              0.0/2.0/2.0            20
    POST /v2/worlds/{id}/observations        1.6/20.4/662.1           1.8/19.3/1231.9        20000
    POST /v2/worlds/{id}/start               2.1/5.2/5.2              1.3/21.7/21.7          20
    POST /v2/worlds/{id}/terminate           2.5/12.7/12.7            1.9/9.0/9.0            20
