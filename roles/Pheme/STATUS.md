# Pheme status

Currency: 2026-09-11, second pass (PHEME-01 ruled; PHEME-02 delivered).

seat state: ACTIVE. Re-premised by the operator 2026-09-11 as the
  signal, novelty and attention-routing seat (ruling committed verbatim,
  sha256 cad7cdd160fa...). Standing state after this pass: BLOCKED on
  one operator decision, PHEME-03 (go/no-go on probe P1); everything
  that does not depend on it is listed in BACKLOG_H0H5.md and PHEME-04
  and PHEME-05 are startable now.
what it asserts: PRESENT (booted in comms 2026-09-11; synced 15:53 UTC,
  queue 0), ACTIVE (two passes), NOT PRODUCTIVE in the domain sense (no
  attention event emitted; no probe run; the design artifacts are the
  only output), VALID not applicable (the gate is frozen, not read).
answer delivered (PHEME-02): YES with a measured ceiling -- 13 of 22
  consequential events in the retro corpus had a typed footprint at
  occurrence; 14 of 15 boring event classes produce no transition once
  surfaces are differenced and a seen-set applied; five predicate
  classes, no model in the path. Probe P1 is a retrospective replay
  (no process, no host, one seat-day) with eligibility 10 positives /
  6 negatives and a preregistered gate. Strongest failure reason: typed
  surfaces record what seats already decided, so P1 may only echo; the
  echo fraction is the number that decides whether the live half is
  worth building.
workspace: F:\Prometheus-worktrees\pheme-base-role, branch
  pheme/base-role-adopt-2026-09-11, base 57533fa76 at creation; merged
  origin/main by named SHA up to db11b7e0b before this pass. dirty: only
  roles/Pheme/ changes.
guard: linked worktree (git-dir != git-common-dir); not canonical.
monitors owned or fed: the May daemon loop, registered DEAD in
  roles/base-role/MONITORS.md, unchanged. No Pheme loop exists and none
  is registered; none is started before PHEME-17.
lane: roles/Pheme/ only. No surface Pheme reads was written to. The
  Evidence Wiki was UNREACHABLE (HTTP 000 at localhost:8377, 15:58 UTC)
  from this worktree; recorded, not chased (Mnemosyne's watchdog row).
blockers: PHEME-03 (operator: run P1 yes/no). PHEME-14 waits on the
  wiki being reachable.
next executable action: on "go", PHEME-04 (ratchet self-test) then
  PHEME-06 (the replay engine), controls PHEME-07..09 before the gate is
  read (PHEME-10). Without a go: PHEME-05 (residue index) and PHEME-19
  (dependents resolvability, first measurement already taken).
