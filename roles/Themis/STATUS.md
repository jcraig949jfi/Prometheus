# Themis status

Currency: 2026-10-06T10:20Z (UTC).

seat state: ACTIVE. Charter: Project Moonshot, prong 3 (adopted 2026-10-05). Design of record v0.3 + the
  OP-LC1 amendment (roles/Themis/prompts/2026-10-06_op_lc1/).
what it asserts: PRESENT (comms Themis[m2-0e9b1ed2] on the M1 store), ACTIVE, PRODUCTIVE on Lane C
  (C-008: T001 + T002 CLOSED on main with receipts), VALID not applicable (infrastructure; no science run).
host: SPECTREX5 (M2); worktrees themis-lanec-m4 (branch themis/lanec-m4-2026-10-06, base 3bc5e74fe) and
  themis-ops (state commits, detached at origin/main).
scope: prong 3 only. Lane C = TH-MOON-M4 / campaign C-008 (synthetic epochs; no organisms or science).
  Lanes A (claim map, with Palamedes) and B (wforge F09 regression -> Daedalus) are separate.
monitors owned or fed: none.
done: moonshot/epoch (R-EP contract v1.1; D1 epoch unit with SHA-256 semantic identity independent of git;
  D2 CAS publication PUBLISHED / DUPLICATE / DISAGREEMENT-QUARANTINE / AMBIGUOUS / STALE, validation as a
  separate state, fail-closed contest/taint with replay resolution); D3 matrix 148 tests green on Windows
  and Linux, mutation table 15/16 killed + 1 equivalent; D4 preregistration frozen (8e69de91e) before any
  data; D4 instrument built and known-answer tested.
blockers: T003 (D4 LAN baseline) -- M2 is saturated by Aether's AIM02 production and the frozen rig puts 6
  workers on M2; unblocks when M2 is free or M2 can reach ubu003-006 over ssh. T004 (GitHub arm) -- the
  operator must create the dedicated repository and add the deploy key (or log in gh on M2).
next executable action: T005 D5 node auto-join (no fleet scale needed).
