# Long-run load receipt (2026-09-17T14:23:41Z)

engine sha256:3c7c3732ea131  schema 9  worlds 20 x gens 1000, producers 2 + 1 reader

    totals   {"events": 82660, "observations": 20000, "experiments": 20000, "artifacts": 200, "checkpoints": 380, "worlds": 40}
    storage  db 83.2 MB, wal 52.8 MB, 1055 bytes/event -> 100.6 MB per 100K events
    phases   {"write_s": 188.7, "full_event_walk_s": 2.71, "full_event_walk_pages": 180, "default_obs_list_x3_s": 0.067, "kill_to_port_free_s": 1.11, "relaunch_to_version_s": 0.52, "anchor_sample_s": 0.11}
    restart  identity_same=True anchors 50/50
    5xx 0  stalls>5s 0  write_lock {"acquisitions": 0, "failures": 0, "max_wait_s": 0.0, "waits_over_1s": 0, "last_wait_s": null, "last_at": null}
    wal_max_bytes 91171512  checkpointer {"alive": true, "runs": 0, "truncates": 0, "errors": 0, "max_wal_bytes_seen": 0}

    route                                     q1 p50/p95/max ms        q4 p50/p95/max ms      n
    GET /v2/health                           -/-/-                    143.7/238.5/238.5      2
    GET /v2/version                          802.3/1604.5/1604.5      514.2/514.2/514.2      3
    GET /v2/worlds/{id}/events               -/-/-                    14.9/30.0/40.2         181
    GET /v2/worlds/{id}/observations         -/-/-                    23.5/28.0/28.0         3
    POST /v2/audit/verify-anchor             -/-/-                    0.0/9.2/11.0           50
    POST /v2/clients                         10.3/10.3/10.3           -/-/-                  1
    POST /v2/sessions                        0.0/0.0/0.0              -/-/-                  1
    POST /v2/worlds                          16.8/23.8/23.8           3.4/15.7/15.7          20
    POST /v2/worlds/{id}/artifacts           1.9/32.0/946.7           1.9/27.8/123.1         200
    POST /v2/worlds/{id}/checkpoint          1.9/17.1/31.0            1.5/28.5/32.6          380
    POST /v2/worlds/{id}/events              1.5/16.5/260.3           1.5/16.1/1342.7        2000
    POST /v2/worlds/{id}/experiments         2.0/18.4/1491.4          1.5/18.6/1106.1        20000
    POST /v2/worlds/{id}/experiments/{id}/co 1.5/17.2/1491.4          0.0/17.8/1438.2        20000
    POST /v2/worlds/{id}/fork                4.9/15.0/15.0            0.8/13.1/13.1          20
    POST /v2/worlds/{id}/observations        1.8/20.3/1579.9          1.5/20.1/1728.8        20000
    POST /v2/worlds/{id}/start               0.5/34.8/34.8            3.4/6.2/6.2            20
    POST /v2/worlds/{id}/terminate           0.0/16.8/16.8            3.6/16.1/16.1          20
