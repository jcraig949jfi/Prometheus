# Crius status

Currency: 2026-09-19 (C0 CLOSED; C1 + C1b run and reported; frozen C1
family CLOSED per the GO's decision rule; instance m2-8d43bbf9).

seat state: ACTIVE. Lane: crius/ (isolated sandbox, charter Campaign 0).
what it asserts: PRESENT (booted in comms 2026-09-19T01:34Z), ACTIVE
  (charter pass), PRODUCTIVE (sandbox + 11 tests + baseline receipts +
  searches on disk), VALID = per the s13 checklist in each REPORT.md,
  never by this file.
host: M2 (SPECTREX5); EW_DB_HOST=192.168.1.202 for every comms call.
workspace: seat worktree crius-base-role, branch
  crius/base-role-adopt-2026-09-18; base 8bb1a28a0 at boot; commits
  f8f2df6b0 (charter) de2ea2fb2 (design) 68cc85ff9 (FREEZE, config_hash
  65fd4678cbcdd9c5) f4dae7a66 (search tooling, c0x).
monitors owned or fed: none. No row in roles/base-role/MONITORS.md.
  Campaign runs are finite commands (search, qualify, report).
frozen: c0.json 65fd4678cbcdd9c5 (CLOSED); c1.json 32dfb243be9fdec9
  (world 7c53db874324b532, generator 624728b00fdd3f2f; gate A-H PASS).
Campaign 0 verdict (2026-09-19): assay valid (positive control reuse_gain
  +3988/+3674; controls dissociate); search found no learning-to-learn.
  Three failure shapes: abstention under the ratio metric (c0),
  partition-specific enumeration orders (c0x seeded), hard-coded action
  scripts (c0x random). Packet: REVIEW_PACKET_C0_2026-09-19.md.
blockers: none. Two XL rows (CRIUS-25, CRIUS-26) name operator decisions
  for Campaign 1; neither blocks Campaign 0.
Campaign 1 verdict (2026-09-19): gate A-H PASS; positive control passes
  the full s13 checklist 3/3 incl. executable-component reuse; search
  (9 runs, 3 arms) found stride-counter random walkers (27-32/50 sealed)
  with zero acquired-state effect. Packet: REVIEW_PACKET_C1_2026-09-19.md.
C1b verdict (2026-09-19): walkers suppressed (RANDOM < 5 pct on chains);
  no reproducible ACC > FRESH, no invoked block, no ancestral gradient;
  compressed enumerators + one stream-sign-flipping record-id clock.
  Packet: REVIEW_PACKET_C1B_2026-09-19.md. Frozen C1 family CLOSED.
next executable action: crius/DESIGN_C2.md (CRIUS-25 / D2 substrate and
  operator campaign) preregistered before any code: typed blocks with a
  1-instruction argument port and invocation; two streams per iteration;
  PARTS-recombinability diagnostic arm kept out of the main population.
