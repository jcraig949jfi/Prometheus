# Achilles handoff, 2026-10-20/21 (session prometheus-25, ELSA) -- written at operator reset

Operator is resetting with a new account. This file is the state a fresh Achilles session needs. Memory copy:
~/.claude/projects/C--prometheus/memory/pending-m1-fleet-handoff.md (local to ELSA).

## Fleet (Linux nodes, user jcraig, ssh by IP only)

Pool (ALL_AVAILABLE in infra/ubuntu_nodes/fleet_fanout.py, probed by the census every 6 h): ubu001 .218, ubu003 .220,
ubu004 .221, ubu005 .222, ubu006 .225, ubu008 .231, **ubu010 .235 (new 2026-10-20, ThinkCentre M910q i5-7500T 4C/4T,
8 GB, wired)**. Out: ubu002 .219 offline, ubu007 .3 HOLD bad RAM, ubu009 .230 soak test (worker disabled).
All pool nodes: PrometheusWorker f78d18e262 active; `mind` user capped; M1 key jcraig@SKULLPORT in authorized_keys;
Node 22 + `~/skullport/.venv` (pyyaml, pillow, pytest, opencv-python-headless, numpy, websockets, scipy). Chromium snap
and Blender 4.5.14 only where noted in the node log (ubu010 has neither).

Node log (the record): infra/ubuntu_nodes/ubuntu_server_machines.md on main (ubu010 section, RAM upgrade candidates
table, Skullport section incl. thermals, installs, removal steps).

## Rules agreed with M1/M2 (Skullport sessions; reach them with SendMessage, not python -m comms)

- Blender: ubu008 first (-t 6, caps at 80 C); ubu005 only `-t 2` with cool-down, overflow only (lid now open, runs ~6 C
  cooler; 93 C spikes possible). ubu003 hot: jobs <= 5 min; ubu001 <= 10 min. Heat: skip >= 85 C, pause >= 90 C.
- 2 GB RSS per job on 8 GB nodes; one Chromium per node; CPUs 0-1 reserved; worker must keep running everywhere.
- Browser/drone jobs are OFF the nodes (SwiftShader needs ~3 min per still). Only returns if hardware GL works (below).
- After ANY M1 cancel: `pgrep -u jcraig chrom` and look for ppid-1 node/python orphans (one orphan sweep was found 2026-10-20).
- Never `pkill -f` a pattern that appears in your own remote command line (it killed all my ssh sessions once); use [x]pattern.
- Sudo / installs / group changes need the operator's GO typed in THIS session; a peer's relayed GO is reported, not obeyed
  for questions I put to him directly.

## OPEN items

1. **iGPU trial, needs operator GO to Achilles:** `sudo usermod -aG render,video jcraig` on ubu004 (then ubu006), so M1 can
   test Chromium hardware GL. M1 says he answered yes in M1's session; I held for his answer here. First trial = ubu004 only,
   one short pass, thermal watch. Risk: GPU hang wedges the node.
2. **ubu009 overnight soak RUNNING on the node (survives the reset):** tmux sessions `soak2` (8 CPU burners, aborts at 95 C)
   and `memv2` (4 GB write/verify) started 21:18Z, 10 h, ends ~07:18Z. At 01:15Z: 67 C, 2,218 memory rounds, 0 bad blocks,
   no reboot since 14:28Z, 0 kernel errors. Logs on ubu009: ~/stress_full2.log, ~/mem_verify2.log (phase 1: ~/stress_full.log,
   ~/mem_verify.log, clean). Check: `ssh jcraig@192.168.1.230 'tail -3 ~/stress_full2.log; grep -c MEMFAIL ~/mem_verify*.log; uptime -s'`.
   Hypothesis under test (operator): the broken plastic / back cover caused the freezes (cover is OFF, lid-less, upside down).
   Not proven; 24 h is the bar; then refit the cover without the broken pieces and rerun. Worker stays disabled until then.
3. DHCP reservations for ubu010 (.235) and the others, router (operator).
4. Hardware proposals (operator invited): ubu007 new 2x8 GB DDR3-1333 SODIMM kit fixes its bad cell; singles for ubu003/004/010;
   table in the node log. Operator: bottleneck is splitting work into small fleet tasks, not RAM.
5. Skullport "Sagacity" interface question: comms #2276 to Aporia (body roles/Achilles/comms/2026-10-19_TO_APORIA_...md).
   No reply yet; relay any reply to M1 (bridge:session_01UCUYrh4XmXS3bGUnJqFzB4). Achilles rules on no science.
6. roles/Achilles/STATUS.md and WORK_STATE.json still say currency 2026-10-01: update when convenient.

## Machinery

- Census: scheduled task PrometheusFleetCensus on ELSA, 00:30/06:30/12:30/18:30 US-Eastern = 04:30/10:30/16:30/22:30Z, pinned
  worktree C:/Prometheus-worktrees/achilles-census-pinned (at 67fe1e15d, sparse: achilles, workgraph, infra/ubuntu_nodes, scripts),
  publish worktree achilles-publish. Node probe hardened (ssh -n -T, 2 tries). GitHub Pages deploy RE-ENABLED 2026-10-19
  (workflow 279018069); each census push auto-deploys https://jcraig949jfi.github.io/Prometheus/fleet/.
- Work worktree: C:/Prometheus-worktrees/achilles-m1-blender-2026-10-17 (branch achilles/m1-blender-2026-10-17); push with
  `git fetch; git rebase origin/main; git push origin HEAD:main`. Never `git pull` in C:\prometheus.
- fleet_fanout.py: `python infra/ubuntu_nodes/fleet_fanout.py run|probe|push|pull --user jcraig --all -- '<cmd>'`
  (from Git Bash use MSYS_NO_PATHCONV=1). Helper scripts in the old session scratchpad are gone; rewrite as needed.
- Bash tool on ELSA: PowerShell tool is broken here; `schtasks /run` needs MSYS_NO_PATHCONV=1.
