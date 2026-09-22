# Long-run load receipt (2026-09-17T15:15:44Z)

engine sha256:d4b8283cfa67a  schema 9  worlds 20 x gens 1000, producers 2 + 1 reader

    totals   {"events": 82660, "observations": 20000, "experiments": 20000, "artifacts": 200, "checkpoints": 380, "worlds": 40}
    storage  db 83.9 MB, wal 13.5 MB, 1065 bytes/event -> 101.5 MB per 100K events
    phases   {"write_s": 481.9, "full_event_walk_s": 2.57, "full_event_walk_pages": 180, "default_obs_list_x3_s": 0.066, "kill_to_port_free_s": 11.81, "relaunch_to_version_s": 13.5, "anchor_sample_s": 0.1}
    restart  identity_same=True anchors 50/50
    5xx 0  stalls>5s 26  write_lock {"acquisitions": 0, "failures": 0, "max_wait_s": 0.0, "waits_over_1s": 0, "last_wait_s": null, "last_at": null}
    wal_max_bytes 85205752  checkpointer {"alive": true, "runs": 0, "truncates": 0, "errors": 0, "max_wal_bytes_seen": 0}

    route                                     q1 p50/p95/max ms        q4 p50/p95/max ms      n
    GET /v2/health                           -/-/-                    58.9/70.0/70.0         2
    GET /v2/version                          803.2/1606.5/1606.5      2553.1/2553.1/2553.1   3
    GET /v2/worlds/{id}/events               -/-/-                    14.4/24.2/43.9         181
    GET /v2/worlds/{id}/observations         7.5/19.0/440.6           5.3/15.7/272.2         59813
    POST /v2/audit/verify-anchor             -/-/-                    0.0/12.6/15.9          50
    POST /v2/clients                         1.0/1.0/1.0              -/-/-                  1
    POST /v2/sessions                        2.6/2.6/2.6              -/-/-                  1
    POST /v2/worlds                          6.3/28.3/28.3            -/-/-                  20
    POST /v2/worlds/{id}/artifacts           6.7/49.7/613.6           17.2/56.7/56.7         200
    POST /v2/worlds/{id}/checkpoint          4.6/19.3/45.1            7.8/38.8/45.0          380
    POST /v2/worlds/{id}/events              3.1/26.7/479.3           5.4/29.6/12619.9       2000
    POST /v2/worlds/{id}/experiments         5.4/29.2/1006.5          8.6/31.9/11671.9       20000
    POST /v2/worlds/{id}/experiments/{id}/co 2.5/23.4/902.2           4.0/30.6/12950.1       20000
    POST /v2/worlds/{id}/fork                7.5/25.3/25.3            10.4/19.4/19.4         20
    POST /v2/worlds/{id}/observations        5.7/31.1/1085.1          9.0/32.6/13001.5       20000
    POST /v2/worlds/{id}/start               8.0/24.8/24.8            -/-/-                  20
    POST /v2/worlds/{id}/terminate           0.0/9.8/9.8              7.4/7.9/7.9            20
