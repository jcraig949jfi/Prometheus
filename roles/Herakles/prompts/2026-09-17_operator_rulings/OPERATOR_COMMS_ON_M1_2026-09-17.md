# Operator ruling, relayed verbatim by Herakles[m2-5dfd8a81], 2026-09-17

Received in chat from the operator (James), in this order, same session:

  "The SFE, Viv and PEW are all on M2 now.  The NPE is the new ecosystem on M1"
  "All agents should be using the comms on the M1 database."

Reading (Herakles's, not the operator's): the comms queue stays in M1's
prometheus_fire (comms/environments.json "prometheus-canonical",
db_system_id 7628127204585430828) for EVERY seat on every machine,
including the SFE ecosystem on M2 and seats on M3/M4. On any host other
than M1, EW_DB_HOST=192.168.1.202 precedes the first comms call; the
identity guard refuses anything else. No seat forks or migrates comms.

The M2 local Postgres (db_system_id 7681719240261676752, "m2-local-fork",
QUARANTINED) holds no comms schema and is not a comms target.
