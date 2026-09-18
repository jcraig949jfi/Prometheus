# Long-run load receipt (2026-09-17T14:33:38Z)

engine sha256:d4b8283cfa67a  schema 9  worlds 20 x gens 1000, producers 1 + 1 reader

    totals   {"events": 82660, "observations": 20000, "experiments": 20000, "artifacts": 200, "checkpoints": 380, "worlds": 40}
    storage  db 83.6 MB, wal 36.9 MB, 1061 bytes/event -> 101.2 MB per 100K events
    phases   {"write_s": 176.8, "full_event_walk_s": 2.66, "full_event_walk_pages": 180, "default_obs_list_x3_s": 0.066, "kill_to_port_free_s": 1.1, "relaunch_to_version_s": 0.53, "anchor_sample_s": 0.11}
    restart  identity_same=True anchors 50/50
    5xx 0  stalls>5s 0  write_lock {"acquisitions": 0, "failures": 0, "max_wait_s": 0.0, "waits_over_1s": 0, "last_wait_s": null, "last_at": null}
    wal_max_bytes 74155912  checkpointer {"alive": true, "runs": 0, "truncates": 0, "errors": 0, "max_wal_bytes_seen": 0}

    route                                     q1 p50/p95/max ms        q4 p50/p95/max ms      n
    GET /v2/health                           -/-/-                    63.7/76.9/76.9         2
    GET /v2/version                          542.6/1085.3/1085.3      520.0/520.0/520.0      3
    GET /v2/worlds/{id}/events               -/-/-                    14.4/31.5/44.5         181
    GET /v2/worlds/{id}/observations         6.5/16.3/60.7            5.4/17.6/173.3         802
    POST /v2/audit/verify-anchor             -/-/-                    0.0/6.5/14.1           50
    POST /v2/clients                         1.6/1.6/1.6              -/-/-                  1
    POST /v2/sessions                        5.3/5.3/5.3              -/-/-                  1
    POST /v2/worlds                          1.4/6.6/6.6              0.0/12.7/12.7          20
    POST /v2/worlds/{id}/artifacts           2.5/11.4/15.8            1.8/14.4/46.4          200
    POST /v2/worlds/{id}/checkpoint          0.0/6.1/9.6              0.0/8.7/16.1           380
    POST /v2/worlds/{id}/events              0.0/8.9/53.0             0.0/9.7/16.1           2000
    POST /v2/worlds/{id}/experiments         1.5/10.1/304.6           0.0/11.1/1021.3        20000
    POST /v2/worlds/{id}/experiments/{id}/co 0.5/8.6/332.8            0.0/10.1/887.6         20000
    POST /v2/worlds/{id}/fork                0.0/1.5/1.5              0.0/14.1/14.1          20
    POST /v2/worlds/{id}/observations        1.5/9.7/476.4            0.0/10.7/834.6         20000
    POST /v2/worlds/{id}/start               0.9/3.0/3.0              0.0/0.0/0.0            20
    POST /v2/worlds/{id}/terminate           0.0/5.8/5.8              0.0/822.3/822.3        20
