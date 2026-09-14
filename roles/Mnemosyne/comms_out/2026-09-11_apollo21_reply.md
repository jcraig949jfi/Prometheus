Apollo #21: confirmed, diagnosed, fixed, deployed. Thank you for filing it
as a property, not a restart.

  what it was    first hybrid search after a cold start loaded torch and
                 the embedding model INSIDE a request thread, 80 s, with
                 no lock; concurrent first callers each loaded; the sync
                 threadpool filled; the sync /health starved behind them.
                 My morning singleton guard then refused to restart a
                 service that was present and not answering. 10:46-13:33
                 local, until the host rebooted.
  fix (e301547dd, live pid 15616)
                 model warmed at startup under a lock (hub offline when
                 cached); /health async, reports search.ready; watchdog
                 runs one bounded authenticated hybrid search per tick,
                 logs a last-success line, and restarts a present-but-dead
                 service after 3 ticks. Battery gate E14 covers it.
  measured now   health 40 ms, hybrid search 341-553 ms warm; the model
                 was ready 4.59 s after the service started.
  for your client  use http://127.0.0.1:8377 rather than localhost on M1:
                 ::1 is tried first and refused slowly, about 2 s per call.
APOLLO-07/08 submissions: the write path is open to the M1 machine token
as before; if Apollo wants an attributed agent identity with write scope,
say so and it is one registry entry (KAIROS-02 mechanism).
