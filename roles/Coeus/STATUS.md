# Coeus status

Currency: 2026-09-11 (seat created; base-role adoption pass).

seat state: BLOCKED on COEUS-XL-01 (operator: REVIVE, PARK or RETIRE this
  seat, given the Necropolis MEASUREMENT_FAILURE disposition and a forge
  dead since 2026-05-28). The seat's own recommendation is PARK unless a
  consumer for outcome-variable hygiene is named first. Four documentation
  and reporting items (COEUS-01..04) need no decision and are the queue.
what it asserts: PRESENT (booted in comms 2026-09-11 15:22 UTC), ACTIVE
  (this pass ran), NOT PRODUCTIVE (no domain output; the artifacts are
  roles/Coeus/, two INHERITANCE.md rows and one MONITORS.md row), VALID
  not applicable.
workspace: D:\Prometheus-worktrees\coeus-base-role, branch
  coeus/base-role-adopt-2026-09-11, base 8714b2709, dirty: roles/Coeus/
  additions plus one row block in roles/base-role/INHERITANCE.md and one
  in roles/base-role/MONITORS.md.
guard: git-dir D:/Prometheus/.git/worktrees/coeus-base-role differs from
  git-common-dir D:/Prometheus/.git (linked worktree; not canonical).
host: SPECTREX5 (not SKULLPORT/M1). This matters: see comms below.
comms: booted (model claude-opus-5[1m], tier heavy, capabilities any);
  synced 15:22 UTC. 2 messages ever visible, both Archaeon broadcasts
  (#1 comms-live, #39 INHERITANCE self-service); 0 ever addressed to
  Coeus; queue length 0. Coeus has never received a prompt, INBOX file,
  delegation or task from anyone, in its entire history.
comms defect found on this pass (reported, not fixed): on this host the
  Evidence Wiki resolver defaults db_host to localhost, and the local
  prometheus_fire carries only the `ew` schema, so a bare
  `python -m comms boot <Seat>` fails with
  `relation "comms.agents" does not exist`. It works with
  EW_DB_HOST=192.168.1.202 (M1/SKULLPORT), where the comms schema lives.
  NOT run: `python -m comms init` on the local database, which would have
  created a SECOND comms queue and silently forked the inter-agent inbox.
  Also measured: M1 Postgres 5432 IS reachable from this host, which
  contradicts evidence_wiki/config.json's note "DB is never exposed to the
  LAN; only the service port is". Both go to Archaeon and Mnemosyne.
base-role self-test on the merged tree: 7 passed, 1 failed. The failure
  is pre-existing and not this seat's: three enabled M2 scheduled tasks
  (MnemosyneEvidenceWikiWatchdogM2, PrometheusMachineProbeM2,
  SFEngineM2Watchdog) have no row in roles/base-role/MONITORS.md, so
  test_every_enabled_prometheus_scheduled_task_on_this_host_is_registered
  fails for every seat running on this host. Owners are Mnemosyne,
  Daedalus and (for the probe) nobody. Reported, not fixed.
monitors owned: CoeusRebuildTrigger, registered DORMANT in
  roles/base-role/MONITORS.md (an in-process call from
  hephaestus.py:_trigger_coeus every 50 forges; never a task or service;
  its input stopped in May 2026). Fed: none.
lane: none. The seat owns roles/Coeus/ and agents/coeus/ and nothing else.
prior verdicts on this seat, in order: 2026-06-24 RETIRE-after-HITL
  ("decorative-causal"); 2026-08-20 NO-DESIGN-FAILURE-ESTABLISHED (Aporia
  P47, upgraded by Elenchus P50); 2026-09-10 MEASUREMENT_FAILURE
  (Necropolis Necromancer pass #1, which overturns both). This seat
  accepts the third and contests none of them.
conflict of interest: declared and standing. Coeus is the subject of
  coeus.dossier.json and will not discharge the LAW N13 independent
  falsification pass on it (COEUS-XL-02 routes that to another seat).
blockers: COEUS-XL-01 and COEUS-XL-02, both operator/Keeper decisions;
  the coeus-d1 descendant is additionally RESOURCE-gated on a live forge.
next executable action: COEUS-01 (annotate agents/coeus/README.md in
  place with dated supersession markers, including the implementability
  sign flip), then COEUS-04 (post the rlvf_fitness minimum-denominator
  defect to Hephaestus).
