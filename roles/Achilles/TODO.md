# Achilles TODO

Currency: 2026-10-01T01:45Z (from date -u). Closed items are deleted
with the closing commit and date, purged after 24 h (base role s7).

- [ ] ACHILLES-01..04: first published census, task registered, mailer
      change verified from the email_dispatched receipt, Pages verified
- [ ] ACHILLES-05: route the first-run data-quality defects to owners
- [ ] sync comms at least every 60 minutes while live (CWO-30C s12)
- [ ] ACHILLES-06 (2026-10-10): a parked census must be visible. While PARKED.json exists, exit non-zero (Task
      Scheduler shows the failure) and have the mailer/page flag a census older than 2 cycles. Found after a silent
      3-day park (DNS outage 2026-10-07).
- [ ] ubu007: BAD RAM (weak cell, bit 26 @ memtester offset 0x1678df398, 3/3 same spot). Waiting on operator: pull DIMM_D
      -> memtest DIMM_B alone -> replace/run 8 GB. Then hot test (memtester + full CPU) 12-24 h -> worker. Worker stays OFF.
- [ ] WATCH ubu007 TEMPERATURE (operator 2026-10-10): lid closed in its final spot, no battery, old fan (blown out).
      Light load (1 thread) 60-75 C in the first minutes. Check under real worker load; act above ~90 C (lid open or
      cap worker threads). Re-check periodically; add to the node health watchdog when that exists.
- [ ] ubu008: seat + engine to move off M2 (operator choosing; default proposal Aether REACH01); full /login for RC.
- [ ] WATCH ubu009 STABILITY (operator 2026-10-11: "sensitive to being moved"): 2 hard hangs 2026-10-11 (installer
      boot; provision clone while being moved). On each check: `journalctl --list-boots` for boots that end abruptly,
      record circumstances. Theories in order: 2-in-1 hinge/tablet-mode/accelerometer events (try disabling the
      tablet-mode switch handling), internal NVMe/cable seating, USB-C adapter port. Fixes list in the machines doc.
