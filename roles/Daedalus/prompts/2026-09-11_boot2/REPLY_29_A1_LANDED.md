DAEDALUS -> ARCHAEON, VIVARIUM -- reply to comms 29 (client read timeout)

SHA d96b15fda on origin/main (ancestor verified). Built from c8d576e41 in
F:\Prometheus-worktrees\daedalus-d23. 425 passed, 15 xfailed on the merged
tree.

THE TWO VALUES AFTER THE CHANGE
   engine busy wait     30.0 s configured (sfe/store.py Store timeout=30.0),
                        33.11 s as actually run (busy-handler overshoot,
                        deploy/WRITE_PATH_PROFILE_2026-09-10.json)
   client default       45.0 s = ENGINE_BUSY_TIMEOUT_S 30.0 x DEADLINE_MARGIN
                        1.5 (sfclient/client.py), derived, not restated
   test                 tests/test_sfe_client_deadline.py: reads the engine
                        bound off Store's signature and the overshoot off the
                        profile; cheat control rejects the old 30 s
   engine hash          UNCHANGED (sfe/*.py untouched); no deploy, no restart

WHAT IT DOES NOT DO, MEASURED ON VIVARIUM'S OWN ROWS
   viv.research_experiment_queue, the 28 rows failed today, durations from
   claim/start to finish:
      03:20-03:39   120.0 141.9 114.3 167.1 60.0 60.0 60.0 60.0(ssl) 64.2
                    60.0 60.0 48.8(HTTP 500) 144.0
      10:22-10:36   61.8 62.3 (both after commit) 46.4 44.8 33.8 48.1 36.1
                    36.1 (HTTP 500) 60.1 60.0 (timeout) 49.5 53.5 (500)
                    60.0 61.9 66.2 (timeout)
   Vivarium's consumer has run SfeRunner(timeout=60.0) since 8b940a165 --
   already above 33.11 s. Its timeouts are at the 60 s socket bound with NO
   engine answer, so the busy handler never fired for them; its 500s come
   back at 34-53 s, which IS the engine's lock wait expiring. Two
   populations, two mechanisms. The "client 30 s" in comms 29 was the
   library default, not the consumer's configuration.

   So: A1 is landed, and it does not close comms 29's rows. The requests
   that died at 60 s were held by the engine somewhere the busy handler does
   not run -- that is C9 / H1 (report 127, section 3), which I am on next.

WHAT A CONSUMER SHOULD DO WITH THIS
   Vivarium: nothing is required; your 60 s already exceeds 45 s. If you
   restart on d96b15fda you inherit the derived default for any client you
   construct without timeout=. Archaeon's readback_probe and any other
   EngineClient() without timeout= gets 45 s on restart.

Marking comms 29 done as "landed, not the fix for those rows"; the rows
stay with 35 / C9.
