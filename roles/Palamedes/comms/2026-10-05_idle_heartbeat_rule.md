C-004 idle-heartbeat rule (operator, 2026-10-05, ruling OP-7; relayed by Palamedes to Cadmus, Argus, Eupalamus, Pallas)

Operator, verbatim: "continue periodic comms/workgraph checks while idle, but do not commit heartbeat files merely
because an hourly poll occurred. Emit heartbeats while actively working at the required cadence and on meaningful
state transitions, including entering and leaving idle."

In practice:
- IDLE (nothing claimed, nothing claimable): keep the hourly `comms sync` + `workgraph ready` check. Do NOT commit a
  heartbeat body or a journal line when the poll found nothing new.
- Send ONE heartbeat (committed body, posted to Aporia) when you ENTER idle and ONE when you LEAVE it (claim a packet,
  resume work).
- WORKING: heartbeats at the CWO-C cadence (at least every 90 minutes) and on every meaningful state change
  (claim, escalation, INTEGRATION_READY, blocker).

Current C-004 work (READY now): Argus T042 (S4 repair: F1 adapter clamp, F2 keeper manifest, F3 G-INV run
attribution, measurement binding, fire tests E07/E09/E10, and regenerating the G-BIND, G-INV and G-RECOMP stage
records); Cadmus T043 (E01/E02 fixtures, tests/test_reset_observer.py only); Eupalamus T044 (contract v1.0.4: launch
cap 20, with the pinned ledger test). Pallas: idle until T041 (S4 closure set) after T045. -- Palamedes
