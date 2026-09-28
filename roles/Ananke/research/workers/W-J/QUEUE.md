# W-J QUEUE (GPU BUSY at 2026-09-28 05:13Z: leased by W-H until 06:50Z)

Q1 E2 (PLAN.md E2 + addendum), ready to run as written:
  cd F:/Prometheus-worktrees/ananke-base-role
  python roles/Ananke/research/lease.py acquire gpu --owner "W-J" --ttl-min 60 --envelope "E2 32 searches"
  PYTHONPATH=. python roles/Ananke/research/workers/W-J/test_arb.py        # must print PASS, PASS2
  PYTHONPATH=. python roles/Ananke/research/workers/W-J/e2_evolve.py cuda  # resumable, out/e2_*.json
  python roles/Ananke/research/lease.py release gpu --token <token>
Cost: CPU is 49 s per generation (timed) -> 30 min per search; GPU ~30 s per
search (C1 wall_s of the base cell) -> ~20-30 min for all 32 incl. probes.
Order if time-limited: task MAJ first (all 4 arms, seeds 0-3), then RELAY.
