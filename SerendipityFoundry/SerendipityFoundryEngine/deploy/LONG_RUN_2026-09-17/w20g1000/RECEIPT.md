# Long-run load receipt (2026-09-17T11:26:50Z)

engine sha256:bc8d3a0caea47  schema 9  worlds 20 x gens 1000, producers 2 + 1 reader

    totals   {"events": 82660, "observations": 20000, "experiments": 20000, "artifacts": 200, "checkpoints": 380, "worlds": 40}
    storage  db 84.4 MB, wal 0.0 MB, 1071 bytes/event -> 102.1 MB per 100K events
    phases   {"write_s": 3042.0, "full_event_walk_s": 4.65, "full_event_walk_pages": 180, "default_obs_list_x3_s": 0.11, "kill_to_port_free_s": 1.12, "relaunch_to_version_s": 1.05, "anchor_sample_s": 0.4}
    restart  identity_same=True anchors 50/50
    5xx 0  stalls>5s 150  write_lock {"acquisitions": 0, "failures": 0, "max_wait_s": 0.0, "waits_over_1s": 0, "last_wait_s": null, "last_at": null}

    route                                     q1 p50/p95/max ms        q4 p50/p95/max ms      n
    GET /v2/health                           -/-/-                    67.6/72.2/72.2         2
    GET /v2/version                          587.5/1083.7/1083.7      1046.5/1046.5/1046.5   3
    GET /v2/worlds/{id}/events               -/-/-                    29.1/40.5/65.2         181
    GET /v2/worlds/{id}/observations         19.5/118.9/1737.9        17.7/127.0/12113.7     52768
    POST /v2/audit/verify-anchor             -/-/-                    4.5/18.8/26.0          50
    POST /v2/clients                         122.7/122.7/122.7        -/-/-                  1
    POST /v2/sessions                        52.2/52.2/52.2           -/-/-                  1
    POST /v2/worlds                          143.2/229.5/229.5        144.7/149.3/149.3      20
    POST /v2/worlds/{id}/artifacts           32.3/267.9/563.6         12.9/167.7/213.0       200
    POST /v2/worlds/{id}/checkpoint          15.1/218.0/632.3         18.8/175.2/207.6       380
    POST /v2/worlds/{id}/events              18.0/217.9/773.5         15.7/181.6/2475.2      2000
    POST /v2/worlds/{id}/experiments         21.8/213.9/1889.6        16.0/200.9/9654.4      20000
    POST /v2/worlds/{id}/experiments/{id}/co 18.8/183.1/1921.2        15.8/184.5/12247.7     20000
    POST /v2/worlds/{id}/fork                136.2/168.1/168.1        14.9/2853.3/2853.3     20
    POST /v2/worlds/{id}/observations        66.9/204.2/1896.8        56.3/197.1/8194.7      20000
    POST /v2/worlds/{id}/start               2.8/174.8/174.8          73.9/170.4/170.4       20
    POST /v2/worlds/{id}/terminate           115.3/230.1/230.1        137.5/204.8/204.8      20
