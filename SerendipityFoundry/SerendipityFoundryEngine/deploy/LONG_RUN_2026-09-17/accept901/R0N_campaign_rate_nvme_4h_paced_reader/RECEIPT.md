# Long-run load receipt (2026-09-18T03:29:51Z)

engine sha256:699ca0f952448  schema 9  worlds 30 x gens 1000, producers 1 + 1 reader

    totals   {"events": 123990, "observations": 30000, "experiments": 30000, "artifacts": 300, "checkpoints": 570, "worlds": 60}
    storage  db 127.0 MB, wal 1.9 MB, 1074 bytes/event -> 102.4 MB per 100K events
    phases   {"write_s": 15408.3, "full_event_walk_s": 3.73, "full_event_walk_pages": 270, "default_obs_list_x3_s": 0.066, "kill_to_port_free_s": 1.02, "relaunch_to_version_s": 2.05, "anchor_sample_s": 0.1}
    restart  identity_same=True anchors 50/50
    5xx 0  stalls>5s 0  write_lock {"acquisitions": 0, "failures": 0, "max_wait_s": 0.0, "waits_over_1s": 0, "last_wait_s": null, "last_at": null}
    wal_max_bytes 2014712  checkpointer {"alive": true, "runs": 0, "truncates": 0, "errors": 0, "max_wal_bytes_seen": 0}

    route                                     q1 p50/p95/max ms        q4 p50/p95/max ms      n
    GET /v2/health                           -/-/-                    80.8/88.4/88.4         2
    GET /v2/version                          1020.0/2039.2/2039.2     2044.1/2044.1/2044.1   3
    GET /v2/worlds/{id}/events               -/-/-                    14.3/16.2/42.1         271
    GET /v2/worlds/{id}/observations         9.4/18.6/45.1            13.0/21.3/65.0         29006
    POST /v2/audit/verify-anchor             -/-/-                    1.2/1.7/13.6           50
    POST /v2/clients                         1.9/1.9/1.9              -/-/-                  1
    POST /v2/sessions                        1.9/1.9/1.9              -/-/-                  1
    POST /v2/worlds                          2.0/5.0/5.0              2.5/3.6/3.6            30
    POST /v2/worlds/{id}/artifacts           2.4/3.4/6.8              2.4/2.9/3.5            300
    POST /v2/worlds/{id}/checkpoint          1.5/2.4/24.4             1.5/1.9/25.0           570
    POST /v2/worlds/{id}/events              1.6/2.6/22.4             1.6/2.5/15.2           3000
    POST /v2/worlds/{id}/experiments         6.4/12.3/209.8           8.5/15.9/76.6          30000
    POST /v2/worlds/{id}/experiments/{id}/co 2.0/5.1/32.0             2.0/7.0/37.6           30000
    POST /v2/worlds/{id}/fork                4.6/9.1/9.1              9.4/13.1/13.1          30
    POST /v2/worlds/{id}/observations        1.9/3.6/32.0             1.9/4.2/37.7           30000
    POST /v2/worlds/{id}/start               1.5/2.2/2.2              1.5/2.1/2.1            30
    POST /v2/worlds/{id}/terminate           2.3/4.0/4.0              2.9/10.8/10.8          30
