# Crius status

Currency: 2026-09-19 (charter adopted; Campaign 0 built, run, reported;
instance m2-8d43bbf9).

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
frozen: configs/c0.json 65fd4678cbcdd9c5; world 57065ca240cee53d;
  partitions ece4bd004beb4710. c0x.json is EXPLORATORY (post hoc).
Campaign 0 verdict (2026-09-19): assay valid (positive control reuse_gain
  +3988/+3674; controls dissociate); search found no learning-to-learn.
  Three failure shapes: abstention under the ratio metric (c0),
  partition-specific enumeration orders (c0x seeded), hard-coded action
  scripts (c0x random). Packet: REVIEW_PACKET_C0_2026-09-19.md.
blockers: none. Two XL rows (CRIUS-25, CRIUS-26) name operator decisions
  for Campaign 1; neither blocks Campaign 0.
next executable action: CRIUS-12/13 -- preregister Campaign 1
  (cost metric, procedure world, recombination arm) in crius/DESIGN_C1.md
  before any code; XL rows CRIUS-25/26 await the operator.
