# Long-run load receipt (2026-09-17T14:14:06Z)

engine sha256:3c7c3732ea131  schema 9  worlds 20 x gens 1000, producers 1 + 1 reader

    totals   {"events": 82660, "observations": 20000, "experiments": 20000, "artifacts": 200, "checkpoints": 380, "worlds": 40}
    storage  db 83.3 MB, wal 52.7 MB, 1056 bytes/event -> 100.7 MB per 100K events
    phases   {"write_s": 187.9, "full_event_walk_s": 2.58, "full_event_walk_pages": 180, "default_obs_list_x3_s": 0.067, "kill_to_port_free_s": 1.11, "relaunch_to_version_s": 0.51, "anchor_sample_s": 0.12}
    restart  identity_same=True anchors 50/50
    5xx 0  stalls>5s 0  write_lock {"acquisitions": 0, "failures": 0, "max_wait_s": 0.0, "waits_over_1s": 0, "last_wait_s": null, "last_at": null}
    wal_max_bytes 98579272  checkpointer {"alive": true, "runs": 0, "truncates": 0, "errors": 0, "max_wal_bytes_seen": 0}

    route                                     q1 p50/p95/max ms        q4 p50/p95/max ms      n
    GET /v2/health                           -/-/-                    52.1/56.6/56.6         2
    GET /v2/version                          798.2/1596.3/1596.3      510.8/510.8/510.8      3
    GET /v2/worlds/{id}/events               -/-/-                    14.2/28.2/45.7         181
    GET /v2/worlds/{id}/observations         5.6/22.6/661.9           6.1/20.5/425.9         834
    POST /v2/audit/verify-anchor             -/-/-                    0.5/8.6/15.7           50
    POST /v2/clients                         1.5/1.5/1.5              -/-/-                  1
    POST /v2/sessions                        0.0/0.0/0.0              -/-/-                  1
    POST /v2/worlds                          2.6/8.1/8.1              3.0/5.0/5.0            20
    POST /v2/worlds/{id}/artifacts           2.0/15.8/51.0            1.5/774.1/1493.7       200
    POST /v2/worlds/{id}/checkpoint          0.0/9.3/15.6             0.0/11.8/14.6          380
    POST /v2/worlds/{id}/events              1.0/9.7/156.7            0.0/12.6/31.1          2000
    POST /v2/worlds/{id}/experiments         1.5/10.7/721.2           0.0/11.0/815.1         20000
    POST /v2/worlds/{id}/experiments/{id}/co 0.0/8.9/631.4            0.0/9.7/889.2          20000
    POST /v2/worlds/{id}/fork                2.0/6.4/6.4              2.7/10.5/10.5          20
    POST /v2/worlds/{id}/observations        1.0/10.1/719.6           0.0/10.4/1015.8        20000
    POST /v2/worlds/{id}/start               0.0/2.0/2.0              0.0/2.0/2.0            20
    POST /v2/worlds/{id}/terminate           0.0/2.0/2.0              0.0/2.0/2.0            20
