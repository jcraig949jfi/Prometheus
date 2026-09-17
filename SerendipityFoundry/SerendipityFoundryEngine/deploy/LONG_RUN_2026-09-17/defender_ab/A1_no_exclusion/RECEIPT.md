# Long-run load receipt (2026-09-17T15:07:10Z)

engine sha256:d4b8283cfa67a  schema 9  worlds 20 x gens 1000, producers 2 + 1 reader

    totals   {"events": 82660, "observations": 20000, "experiments": 20000, "artifacts": 200, "checkpoints": 380, "worlds": 40}
    storage  db 84.3 MB, wal 8.6 MB, 1070 bytes/event -> 102.0 MB per 100K events
    phases   {"write_s": 460.3, "full_event_walk_s": 2.58, "full_event_walk_pages": 180, "default_obs_list_x3_s": 0.07, "kill_to_port_free_s": 1.13, "relaunch_to_version_s": 0.53, "anchor_sample_s": 0.11}
    restart  identity_same=True anchors 50/50
    5xx 0  stalls>5s 18  write_lock {"acquisitions": 0, "failures": 0, "max_wait_s": 0.0, "waits_over_1s": 0, "last_wait_s": null, "last_at": null}
    wal_max_bytes 89754232  checkpointer {"alive": true, "runs": 0, "truncates": 0, "errors": 0, "max_wal_bytes_seen": 0}

    route                                     q1 p50/p95/max ms        q4 p50/p95/max ms      n
    GET /v2/health                           -/-/-                    52.5/60.4/60.4         2
    GET /v2/version                          793.0/1585.0/1585.0      526.9/526.9/526.9      3
    GET /v2/worlds/{id}/events               -/-/-                    14.7/25.0/46.7         181
    GET /v2/worlds/{id}/observations         7.2/18.0/236.2           5.5/15.9/202.2         56777
    POST /v2/audit/verify-anchor             -/-/-                    0.5/6.9/10.8           50
    POST /v2/clients                         6.5/6.5/6.5              -/-/-                  1
    POST /v2/sessions                        1.0/1.0/1.0              -/-/-                  1
    POST /v2/worlds                          10.4/28.8/28.8           9.4/16.0/16.0          20
    POST /v2/worlds/{id}/artifacts           5.6/57.1/1073.2          8.8/31.6/41.2          200
    POST /v2/worlds/{id}/checkpoint          4.0/23.6/65.8            9.2/36.2/665.4         380
    POST /v2/worlds/{id}/events              2.2/22.6/2010.7          4.3/32.9/4524.9        2000
    POST /v2/worlds/{id}/experiments         4.6/28.0/1031.9          8.1/32.6/12535.0       20000
    POST /v2/worlds/{id}/experiments/{id}/co 1.7/22.1/672.1           3.3/29.5/12842.4       20000
    POST /v2/worlds/{id}/fork                2.6/16.9/16.9            18.1/33.4/33.4         20
    POST /v2/worlds/{id}/observations        5.1/29.9/1461.0          8.6/32.8/12455.3       20000
    POST /v2/worlds/{id}/start               3.9/50.6/50.6            0.0/0.0/0.0            20
    POST /v2/worlds/{id}/terminate           2.6/18.4/18.4            9.2/14.5/14.5          20
