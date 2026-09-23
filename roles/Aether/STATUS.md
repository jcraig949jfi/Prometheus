# Aether status

Currency: 2026-09-22 (bootstrap, then the AETH-01 memory-wall round
through Phase 6, on BUCKKEEP as Aether[buckkeep-7a10ca4b]).
Supersedes the 2026-09-19 status, which said the seat had no lane and
no science; both statements were true when written and are false now.

seat state: ACTIVE. Working the AETH-01 lane. Not blocked on any other
  seat.
what it asserts: PRESENT (booted in comms 2026-09-22T17:47Z as
  Aether[buckkeep-7a10ca4b] on the M1 canonical store; sync 0 new, 0
  queued, queue length 0), ACTIVE (this pass ran), PRODUCTIVE (the lane
  has committed artifacts through 251bc987e; this pass itself has
  produced the journal entry, this status and a verified test gate, no
  domain result yet), VALID not asserted for anything new this pass.
lane: the Aether artificial-physics ecosystem under Aether/ -- AETH-00
  (frozen conformance specimen), AETH-01 / aeth01.v1 (repaired freeze
  CANDIDATE, not frozen), the AGE GPU kernel, its CPU oracle, the RunPod
  canary and the scaling instrument. Governing doctrine:
  Aether/AETHER_DOCTRINE.md (currency 2026-09-20). Concept:
  Aether/AETHER_CONCEPT.md. NOTE: roles/Aether/RESPONSIBILITIES.md has
  NOT yet been rewritten around that doctrine and still says the charter
  is pending; that file is stale and is work item 4 below.
workspace: worktree C:/Prometheus-worktrees/aether-memwall, branch
  aether/aeth01-memwall-2026-09-22, base 251bc987e (tip of the pushed
  seat branch aether/base-role-adopt-2026-09-19). Host BUCKKEEP -- NOT
  M2/SPECTREX5, where this seat was created; the seat has moved hosts
  and the earlier workspace lines are historical.
guard: git-dir C:/Prometheus/.git/worktrees/aether-memwall differs from
  git-common-dir C:/Prometheus/.git (linked worktree; not canonical).
  origin/main = c351f00b2 recorded at boot; origin/main is NOT an
  ancestor of the seat branch (31 behind / 32 ahead), so integration
  requires an explicit merge and a re-test on the merged tree.
comms: EW_DB_HOST=192.168.1.202 (M1) set before the first call. Boot and
  sync both succeeded. psycopg2-binary 2.9.13 had to be installed on
  this host for comms to import at all.
monitors owned or fed: none. No row in roles/base-role/MONITORS.md, and
  no standing loop exists to register. If the AGE cleanup reaper or the
  RunPod orchestrator is ever left running, it gets a row with bound and
  accountable_seat BEFORE it is launched (base rules 7, 9, 10).
spend: no RunPod pod is outstanding. The last paid run (pod
  dc21hvohu9f79j, A40, 113 s, about $0.015) was terminated with ACK_204
  and its absence independently re-confirmed, ACTIVE_POD_COUNT 0. No API
  call and no spend this pass.
test gate: green. Before any edit, the three Phase-4 files passed
  (95 tests) and the full Aether/test suite passed at 251bc987e
  (984 passed, 5 skipped -- the 5 are Linux/POSIX pod-side gates, so
  they are UNMEASURED on this host, not passed).
work this pass: AETH-01 memory-wall round, Phases 2 through 6,
  COMPLETE. Disposition MEMORY_WALL_MOVED. Off-GPU peak allocation
  240.00 -> 113.01 bytes/site; on a real A40 the marginal pool cost
  measured 257 -> 128 bytes/site (2.008x). 16384^2 = 268,435,456 sites
  now runs on one A40 at 7.42 s/tick and 36.2 M sites/sec with 12.2 GiB
  free, where the previous kernel OOM'd. Canary 300/300 bit-exact on the
  GPU; all ten digests shared with the baseline A40 run are byte-
  identical. Report: Aether/AETH-01/GPU_MEMORY_OPTIMIZATION_01_2026-09-22.md;
  raw artifacts under Aether/AETH-01/evidence/2026-09-22_optimized_scale_run/.
spend to date: $0.0253 of a $3 authorization (0.84%), one pod
  (6q9raukca794ou, 186 s), terminated ACK_204 with absence confirmed
  twice, ACTIVE_POD_COUNT 0. Billing reconciliation is INCOMPLETE and is
  not claimed: the figure is computed from measured wall time at the
  quoted rate; this client has no billing endpoint.
new limiting boundary: 32768^2 OOMs. The fitted model
  (used_MiB = 270.2 + 128.000 B/site, intercept independently confirmed
  by the four smallest lattices) puts the device ceiling at about
  370.5 M sites (19249^2), so the next doubling is a device-count
  problem, not an allocation problem.
blockers: none. Three open operator decisions, none blocking: the
  canonical checkout is sitting on a seat branch (D-23 s1); the stale
  duplicate worktree C:/Prometheus-aether; and
  roles/Aether/RESPONSIBILITIES.md still saying charter PENDING.
known cosmetic defect: a NumPy RuntimeWarning ("overflow encountered in
  scalar multiply") now appears in pod logs from the in-place mix64_vec
  scalar path, which CuPy leaves outside np.seterr. Noise, not a defect;
  deliberately not fixed during the evidence run.
first light: DONE. 6 of 6 worlds at 4096^2 x 5,000 ticks on one A40,
  30,000 world-ticks, $2.022. No endogenous organization; the nulls are
  now mechanistic. Three carry-outs beyond the null: a certified-death
  condition HABITABILITY.md lacks, the first measurement of AETH-01's
  irreducible energy leak (3.04% per 5,000 ticks with every cost
  parameter at zero), and confirmation that a 128^2 CPU scout predicts
  16.7 M-site behaviour well enough to choose parameters with.
  Report: Aether/AETH-01/FIRST_LIGHT_2026-09-22.md.
observatory: built this pass (Aether/observatory/, 18 known-answer tests
  including a read-only guard). component_track and
  perturbation_divergence deliberately NOT implemented -- deepen-tier,
  and cheap wrong versions would produce numbers that look like
  structure tracking.
spend to date: about $2.09 of the $3 authorization across all runs
  today. Every pod terminated with absence independently confirmed;
  ACTIVE_POD_COUNT 0 now. Billing reconciliation remains INCOMPLETE and
  is not claimed: figures are computed from measured wall time at the
  quoted rate, because this client has no billing endpoint.
next executable action: operator's call, and it is a science decision
  rather than an engineering one. The three candidates the run leaves
  open: (a) extend B_balanced, the only world still changing at tick
  5,000 and right-censored by run length rather than by physics; (b) put
  the two proposed additions (the certified-death condition, the energy
  loss rate) into HABITABILITY.md and ECONOMICS.md, which are other
  documents' text and so want a ruling; (c) accept that aeth01.v1's
  soup does not organize and decide whether that falsifies the candidate
  or is a parameter-space question, which bears on whether to freeze
  aeth01.v1 at all. No further kernel work is indicated.
