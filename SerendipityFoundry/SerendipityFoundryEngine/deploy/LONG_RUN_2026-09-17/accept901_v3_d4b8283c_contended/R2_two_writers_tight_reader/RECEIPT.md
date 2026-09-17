# Long-run load receipt (2026-09-17T14:40:39Z)

engine sha256:d4b8283cfa67a  schema 9  worlds 20 x gens 1000, producers 2 + 1 reader

    totals   {"events": 82660, "observations": 20000, "experiments": 20000, "artifacts": 200, "checkpoints": 380, "worlds": 40}
    storage  db 84.4 MB, wal 5.9 MB, 1070 bytes/event -> 102.1 MB per 100K events
    phases   {"write_s": 414.5, "full_event_walk_s": 2.71, "full_event_walk_pages": 180, "default_obs_list_x3_s": 0.06, "kill_to_port_free_s": 1.11, "relaunch_to_version_s": 0.51, "anchor_sample_s": 0.12}
    restart  identity_same=True anchors 50/50
    5xx 0  stalls>5s 9  write_lock {"acquisitions": 0, "failures": 0, "max_wait_s": 0.0, "waits_over_1s": 0, "last_wait_s": null, "last_at": null}
    wal_max_bytes 52501192  checkpointer {"alive": true, "runs": 0, "truncates": 0, "errors": 0, "max_wal_bytes_seen": 0}

    route                                     q1 p50/p95/max ms        q4 p50/p95/max ms      n
    GET /v2/health                           -/-/-                    45.9/49.0/49.0         2
    GET /v2/version                          558.4/1116.8/1116.8      508.0/508.0/508.0      3
    GET /v2/worlds/{id}/events               -/-/-                    14.9/26.3/163.3        181
    GET /v2/worlds/{id}/observations         7.6/19.6/278.6           5.5/16.1/356.9         46957
    POST /v2/audit/verify-anchor             -/-/-                    0.0/9.5/18.7           50
    POST /v2/clients                         4.5/4.5/4.5              -/-/-                  1
    POST /v2/sessions                        5.6/5.6/5.6              -/-/-                  1
    POST /v2/worlds                          0.9/24.8/24.8            30.6/61.2/61.2         20
    POST /v2/worlds/{id}/artifacts           7.5/48.0/225.6           7.7/29.6/31.4          200
    POST /v2/worlds/{id}/checkpoint          6.5/31.9/446.2           9.3/53.2/7325.7        380
    POST /v2/worlds/{id}/events              2.9/30.2/553.3           6.7/31.8/681.9         2000
    POST /v2/worlds/{id}/experiments         4.9/29.8/609.9           8.3/33.0/12299.4       20000
    POST /v2/worlds/{id}/experiments/{id}/co 1.5/23.5/998.2           3.6/31.5/7422.4        20000
    POST /v2/worlds/{id}/fork                1.7/15.6/15.6            8.6/21.4/21.4          20
    POST /v2/worlds/{id}/observations        5.5/31.2/919.5           9.5/33.9/9867.7        20000
    POST /v2/worlds/{id}/start               0.0/19.6/19.6            41.4/42.0/42.0         20
    POST /v2/worlds/{id}/terminate           0.0/31.7/31.7            1.6/13.3/13.3          20
