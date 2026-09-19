# Bellerophon status

Currency: 2026-09-18 (late; Worlds Kernel Phase 1 built and running, Phase 2 reference built).

seat state: ACTIVE. Charter in force: the WORLDS KERNEL directive
  (prompts/2026-09-18_worlds_kernel/, sha256 fc819348...). D-BELL-1..4
  adopted as the operator wrote them.
what it asserts: PRESENT (comms Bellerophon[m2-c95cc146]), ACTIVE,
  PRODUCTIVE at the kernel layer: prometheus/toolbox/ (18 kernel files,
  2,699 lines incl. tests/examples), EXP-001 runs end to end (96 runs,
  0 failed, 7/7 controls MET), 22 kernel tests pass + 1 skipped (Redis
  unreachable on M2), base-role self-test 11 passed. VALID: the kernel
  claims nothing about any world; its receipts are the evidence for
  itself only.
workspace: worktree bellerophon-base-role on M2 / SPECTREX5, branch
  bellerophon/base-role-adopt-2026-09-18 (task branch kept for the day's
  passes; a fresh task branch per slice from tomorrow).
comms: M1 store; queue empty at last sync.
monitors owned or fed: none; no MONITORS.md row (nothing loops).
lane: the kernel (contracts, IR, capabilities, devices, adapters,
  references, admission, lowering, conformance tests).
lowering status: local OK (executes); sfe TARGET_UNSUPPORTED for a general
  IR with six named mismatches (M1-M6, design s6) and OK for a frontier-
  shaped IR; npe UNAVAILABLE_INTERFACE by D-BELL-2 with a structurally
  valid BusJob.
blockers: none for the next slice. Held by decision: Techne/Nyx drafts
  (D-BELL-4); Box2D (phase order); NPE bridge (D-BELL-2, needs primordial/
  on main); Redis acceptance (needs M1).
next executable action: slice 1 of design s14 -- substrate.kv.v1 over
  the StateDevice + statemachine.v2 with workspace ops + EXP-002 (same
  players x {flat, kv, stream} substrates).
