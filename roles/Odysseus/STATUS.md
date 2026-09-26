# Odysseus status

Currency: 2026-09-26T03:50Z (from date -u).

seat state: ACTIVE. Charter ADOPTED 2026-09-26 (distributed brain
  substrate; prompts/2026-09-26_charter/).
what it asserts: PRESENT, ACTIVE, PRODUCTIVE (brain v0 built and
  tested on ubu001). VALID: Linux only so far; Windows PENDING
  (ODYSSEUS-01); cross-host PENDING (ODYSSEUS-02).
brain v0: odysseus/brain/ + odysseus/tests/ -- 71 tests pass on ubu001
  (3 consecutive runs). Stress: 6 processes, 4000 neurons, 200 ticks,
  40% datagram loss -> 18,462 dropped, all repaired, 200/200 tick roots
  equal the in-process reference, full replay verifies; 57.6 s wall
  (2.9 s with no loss).
host: ubu001 (Ubuntu 26.04.1, 192.168.1.218, 4 cores, 7 GB, no GPU).
monitors owned or fed: none (no resident process launched).
blockers: Windows run needs a Windows seat (delegated); cross-host run
  needs a node on ubu002; Windows inbound UDP needs an operator firewall
  decision (ODYSSEUS-22).
next executable action: ODYSSEUS-03 measurements, ODYSSEUS-04 install note.
