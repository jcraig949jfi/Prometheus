# Long-run load receipt (2026-09-17T14:06:53Z)

engine sha256:1e81fe000d345  schema 9  worlds 20 x gens 1000, producers 2 + 1 reader

    totals   {"events": 82660, "observations": 20000, "experiments": 20000, "artifacts": 200, "checkpoints": 380, "worlds": 40}
    storage  db 84.3 MB, wal 7.5 MB, 1070 bytes/event -> 102.0 MB per 100K events
    phases   {"write_s": 355.3, "full_event_walk_s": 2.81, "full_event_walk_pages": 180, "default_obs_list_x3_s": 0.068, "kill_to_port_free_s": 1.11, "relaunch_to_version_s": 0.73, "anchor_sample_s": 0.11}
    restart  identity_same=True anchors 50/50
    5xx 0  stalls>5s 2  write_lock {"acquisitions": 0, "failures": 0, "max_wait_s": 0.0, "waits_over_1s": 0, "last_wait_s": null, "last_at": null}
    wal_max_bytes 92749472  checkpointer {"alive": true, "runs": 0, "truncates": 0, "errors": 0, "max_wal_bytes_seen": 0}

    route                                     q1 p50/p95/max ms        q4 p50/p95/max ms      n
    GET /v2/health                           -/-/-                    62.0/75.5/75.5         2
    GET /v2/version                          542.6/1083.7/1083.7      729.4/729.4/729.4      3
    GET /v2/worlds/{id}/events               -/-/-                    14.5/23.0/263.9        181
    GET /v2/worlds/{id}/observations         7.5/19.8/1136.8          6.7/17.7/827.6         36147
    POST /v2/audit/verify-anchor             -/-/-                    0.0/10.4/15.8          50
    POST /v2/clients                         7.3/7.3/7.3              -/-/-                  1
    POST /v2/sessions                        0.0/0.0/0.0              -/-/-                  1
    POST /v2/worlds                          6.9/12.5/12.5            6.9/13.8/13.8          20
    POST /v2/worlds/{id}/artifacts           6.9/33.7/1233.2          8.8/33.3/36.3          200
    POST /v2/worlds/{id}/checkpoint          4.0/44.0/371.4           8.8/35.6/672.1         380
    POST /v2/worlds/{id}/events              3.2/26.1/675.1           5.5/31.4/73.3          2000
    POST /v2/worlds/{id}/experiments         4.6/27.3/1389.3          8.5/32.8/10015.5       20000
    POST /v2/worlds/{id}/experiments/{id}/co 2.0/22.3/1333.3          3.8/30.8/10094.7       20000
    POST /v2/worlds/{id}/fork                10.8/31.2/31.2           13.4/18.2/18.2         20
    POST /v2/worlds/{id}/observations        5.0/29.5/1380.3          9.2/33.4/1490.5        20000
    POST /v2/worlds/{id}/start               1.6/18.0/18.0            18.5/20.8/20.8         20
    POST /v2/worlds/{id}/terminate           3.4/10.5/10.5            3.0/51.0/51.0          20
