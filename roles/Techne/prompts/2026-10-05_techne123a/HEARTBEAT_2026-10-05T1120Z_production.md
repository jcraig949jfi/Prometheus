HEARTBEAT -- PRODUCTION LAUNCH (CWO-2026-09-30C s13)   Techne -> Aporia   2026-10-05T11:20Z

SEAT / INSTANCE         Techne / GANDALF (M3) gandalf-4c0c7e64
MODEL                   claude-fable-5-1 (harness-reported id; heavy)
BRANCH / HEAD           techne/boot-2026-10-03 / ca24435d2 (ancestor of origin/main)
STATE                   WORKING (operator directive 8, TECHNE-123A)
CURRENT STEP            production run in flight on RunPod (A40, $0.49/h): 33 trajectories x 64 frames
                        (6 seeds x FWD/BACK/TURN/INTERVENE/NOOP + 3 replicates); ceiling 4500 s,
                        budget guard $1.50; projected ~40 min, ~$0.35
PROGRESS                Flight 1 FLIGHT1_PASS (161.7 s, $0.0220): weights verified against the
                        official sha256 on the pod; same-seed replicate BIT-IDENTICAL; actions change
                        the output. Flight 2 FLIGHT_PASS (672.5 s, $0.0915): 8 x 64 frames; replicate
                        bit-identical again; different-seed same-action divergence is large and still
                        growing at frame 63; FWD walks into the tree in this prompt and the scene
                        collapses to a texture by frame 48 while NOOP stays sharp. Amendment A (dated,
                        before launch): a BACK family added as a second normal arm; preregistered
                        FWD-based readings unchanged; incremental saving on the pod.
SPEND                   $0.1135 estimated so far of the $10 cap (two flights, not yet reconciled with
                        provider billing); both pods reaped and observed absent
BLOCKERS                none
LAST PUSHED SHA / TIME  ca24435d2 / 2026-10-05T11:16Z
FINISH CONDITION        production receipt + analysis + report + review packet committed; pod reaped
NEXT EXPECTED MILESTONE production receipt within ~45 min
