# Long-run load receipt (2026-09-17T14:44:13Z)

engine sha256:d4b8283cfa67a  schema 9  worlds 20 x gens 1000, producers 2 + 1 reader

    totals   {"events": 82660, "observations": 20000, "experiments": 20000, "artifacts": 200, "checkpoints": 380, "worlds": 40}
    storage  db 82.6 MB, wal 72.1 MB, 1047 bytes/event -> 99.9 MB per 100K events
    phases   {"write_s": 205.6, "full_event_walk_s": 2.76, "full_event_walk_pages": 180, "default_obs_list_x3_s": 0.066, "kill_to_port_free_s": 1.12, "relaunch_to_version_s": 0.52, "anchor_sample_s": 0.11}
    restart  identity_same=True anchors 50/50
    5xx 0  stalls>5s 2  write_lock {"acquisitions": 0, "failures": 0, "max_wait_s": 0.0, "waits_over_1s": 0, "last_wait_s": null, "last_at": null}
    wal_max_bytes 96189672  checkpointer {"alive": true, "runs": 0, "truncates": 0, "errors": 0, "max_wal_bytes_seen": 0}

    route                                     q1 p50/p95/max ms        q4 p50/p95/max ms      n
    GET /v2/health                           -/-/-                    53.8/66.0/66.0         2
    GET /v2/version                          1083.8/2167.5/2167.5     517.3/517.3/517.3      3
    GET /v2/worlds/{id}/events               -/-/-                    14.8/21.6/169.8        181
    GET /v2/worlds/{id}/observations         -/-/-                    20.3/28.8/28.8         3
    POST /v2/audit/verify-anchor             -/-/-                    1.5/6.2/7.4            50
    POST /v2/clients                         1.1/1.1/1.1              -/-/-                  1
    POST /v2/sessions                        7.1/7.1/7.1              -/-/-                  1
    POST /v2/worlds                          15.4/39.5/39.5           2.7/10.5/10.5          20
    POST /v2/worlds/{id}/artifacts           1.5/32.5/720.5           3.3/42.4/805.5         200
    POST /v2/worlds/{id}/checkpoint          1.3/21.5/62.6            3.0/21.3/47.6          380
    POST /v2/worlds/{id}/events              0.0/16.1/185.0           1.5/17.6/46.7          2000
    POST /v2/worlds/{id}/experiments         1.5/18.2/554.5           2.0/18.0/1335.5        20000
    POST /v2/worlds/{id}/experiments/{id}/co 0.0/17.3/1575.8          1.5/17.3/1555.1        20000
    POST /v2/worlds/{id}/fork                3.5/16.1/16.1            0.0/17.7/17.7          20
    POST /v2/worlds/{id}/observations        1.5/20.9/1840.8          1.7/19.4/1666.4        20000
    POST /v2/worlds/{id}/start               0.8/12.3/12.3            0.0/16.3/16.3          20
    POST /v2/worlds/{id}/terminate           0.0/1.5/1.5              3.4/10.7/10.7          20
