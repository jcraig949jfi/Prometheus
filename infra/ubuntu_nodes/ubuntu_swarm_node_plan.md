# Ubuntu swarm nodes: plan for always-on Claude sessions

Started 2026-09-25. **ubu001 and ubu002 are the guinea pigs.** Everything here gets proved on them first, then becomes the
standard for every old machine brought into the Prometheus swarm.

Related docs (all in `D:\Prometheus\docs\`):
- `ubuntu_server_install_runbook.md`: bare metal to Ubuntu + network (sections 1-7), post-install setup from M2 (section 8).
- `ubuntu_server_setup.sh`: the post-install script (disk, updates, lid, Wi-Fi power save, battery limits, linger, Claude Code).
- `ubuntu_server_machines.md`: per-machine log (hardware, IPs, battery health, what was changed).

Open items: `ubuntu_swarm_todo.md`.

## 1. Goal

Each node runs one or more Prometheus agent seats as **always-on Claude Code sessions** that:
- start at boot with nobody logged in,
- restart when they crash or hang,
- keep authenticated for months without a browser,
- are observable and controllable from M2 over SSH,
- warn a human **before** anything expires, never silently die.

## 2. Node lifecycle (the order every new machine goes through)

| Stage | What | How | Who | Status on ubu001/002 |
|-------|------|-----|-----|----------------------|
| N0 Install | Ubuntu Server 26.04.1 LTS from the Verbatim USB stick | runbook s1-s6 | operator at the machine | done |
| N1 Network | Wi-Fi via netplan (or Ethernet) | runbook s7 | operator at the machine | done |
| N2 Remote access | M2's SSH key + passwordless sudo | runbook s8 steps 1-2 | operator pastes 2 commands on M2 | done |
| N3 Base setup | `ubuntu_server_setup.sh`: full disk, updates, lid, Wi-Fi power save, battery 75/80, linger, Claude Code | runbook s8 step 3 | Claude from M2 | done |
| N4 Claude login | interactive login over SSH from M2 (NOT at the laptop console) | runbook s8 step 5 | operator | done |
| N5 Long-lived token | `claude setup-token`, token stored in `~/.config/prometheus/claude.env` (mode 600) | s4 below | operator runs it, Claude wires it in | done on both 2026-09-25 |
| N6 Code + secrets | Prometheus repo clone (deploy key) + key files for `keys.py` | s6 below | operator (secrets), Claude (clone) | code cloned on both 2026-09-25; secrets pending |
| N7 Seat services | one systemd user service + tmux session per agent seat | s5 below | Claude | generic remote-control session per node live + reboot-tested 2026-09-25; seat assignments pending |
| N8 Health watchdog | 15-min timer: auth check, liveness probe, restart, expiry countdown, status file | s7 below | Claude | **pending** |
| N9 Burn-in | reboot test, kill test, auth-failure test, 48 h unattended | s8 below | Claude + operator | **pending** |
| N10 Fleet member | listed in the machine log + fleet topology; the seat's RESUME points at the node | | | **pending** |

A machine is not a swarm node until N9 passes. Until then it's a Linux box with Claude on it.

## 3. What expires, and what can and can't be automated

| Thing | Expires / breaks when | Can a cron fix it? | Plan |
|-------|----------------------|--------------------|------|
| Interactive claude.ai login (N4) | Refreshes itself while in use; can still lapse (logout elsewhere, password change, long idle, revocation) | **No.** A new login needs a browser | Replace with the long-lived token (N5); keep the interactive login only as a fallback |
| `claude setup-token` token | Long-lived (about 1 year per Anthropic docs; **record the actual date it was issued**) | **No**, renewal needs a browser once | Watchdog counts down from the issue date, warns at 30 days and 7 days; renewal is a 2-minute SSH job |
| A running Claude session | Crashes, hangs, context fills up, or runs an old CLI version after an auto-update | **Yes** | systemd `Restart=always` + watchdog liveness probe + nightly respawn |
| Wi-Fi | Router reboot, DHCP change, power save | Mostly | netplan reconnects itself; DHCP reservations fix the IPs; power save is off (setup script) |
| Battery | Old cells swell if held at 100% | n/a | Charge limits 75/80 (setup script); battery health recorded in the machine log |
| Disk | Logs and transcripts fill it up | Yes | Watchdog reports disk use; journald is capped by default |

**Principle:** the cron's job is *detect, restart what can be restarted, and escalate what can't*. It never pretends to have
fixed a login. A health line that says OK must come from an actual `claude -p` answer, not from a process being present
(a heartbeat is not a productivity signal).

## 4. Authentication design (N5)

1. Operator, over SSH from M2: `ssh jcraig@<ip>`, then `claude setup-token`, and complete the browser step on M2.
2. The token it prints goes **straight into a file on the node**, never into chat, git or a doc:
   `mkdir -p ~/.config/prometheus && umask 077 && cat > ~/.config/prometheus/claude.env`, then type
   `CLAUDE_CODE_OAUTH_TOKEN=<paste>`, press Enter, then Ctrl+D.
3. Record the **issue date** (not the token) in `~/.config/prometheus/token_issued` and in the machine log.
4. Every seat service and the watchdog load it with `EnvironmentFile=%h/.config/prometheus/claude.env`.
5. Check: `claude auth status` shows loggedIn true; `claude -p "Reply with exactly: OK"` answers OK.
6. Renewal (yearly, or when the watchdog warns): repeat steps 1-3 and restart the services.

Claude (the assistant) never reads `claude.env` or `~/.claude/.credentials.json`; checks use `claude auth status` and
`test -f` only (CLAUDE.md key-file rule).

## 5. Always-on seat sessions (N7)

- **Linger** is on (`loginctl enable-linger jcraig`), so jcraig's user services start at boot without a login.
  Done on ubu001/002 on 2026-09-25.
- One systemd **user** unit per seat: `~/.config/systemd/user/prom-seat@.service`, instance name = seat (e.g.
  `prom-seat@harmonia`). It runs a detached tmux session named after the seat, in the seat's worktree, launching
  `claude` with the seat's boot prompt (and a `/loop` if the seat runs on a cadence).
  `Restart=always`, `RestartSec=60`, `EnvironmentFile=` the token file.
- Watch or intervene from M2: `ssh -t jcraig@<ip> tmux attach -t <seat>` (detach with Ctrl+B then D, never Ctrl+C).
- Stop/start: `ssh jcraig@<ip> systemctl --user restart prom-seat@<seat>`.
- An alternative is Claude Code's own background agents (`claude --bg`, `claude agents`, `claude respawn --all`).
  Keep it in mind; systemd + tmux was chosen first because it's transparent and survives reboots by design.
  Compare them during burn-in.
- Permission mode for unattended seats: **to decide per seat** (bypass is needed for real autonomy; limit the blast radius
  with a dedicated worktree and no secrets beyond what the seat needs).

## 6. Code and secrets (N6)

- Repo: `https://github.com/jcraig949jfi/Prometheus.git`. If private: one **read-only deploy key per node**, generated on
  the node; the operator adds the public half on GitHub. If seats need to push, use a write-enabled deploy key or a scoped token, per node.
- Nodes work in their own worktrees/branches, as M1/M2/M3 do; they never share a working tree.
- Fleet comms need `EW_DB_HOST=192.168.1.202` (M1 Postgres), the same as M3.
- Secrets for `keys.py`: the **operator** copies them with `scp`; Claude does not read or copy key files. Nodes get only the
  keys their seats need.

## 7. Health watchdog (N8)

A systemd user timer, every 15 minutes, runs `~/bin/prom_health.sh`, which:
1. `claude auth status` → loggedIn? authMethod?
2. Liveness probe: `claude -p "Reply with exactly: OK"` with a 90 s timeout (costs one tiny subscription request).
3. For each seat: is the service active, does the tmux session exist, and has its transcript or journal changed in the last N
   minutes? (Stale means restart, and after 3 restarts in an hour, escalate instead of looping.)
4. Token countdown from `token_issued`: WARN at ≤30 days, CRIT at ≤7.
5. Disk %, battery %, AC online, Wi-Fi IP.
6. Writes one line to `~/prom_health.log` and overwrites `~/prom_health.txt` (current state), readable from M2:
   `ssh jcraig@<ip> cat ~/prom_health.txt`.
7. Nightly (e.g. 04:00 local): restart seat sessions so they pick up the auto-updated CLI.
8. Escalation channel: **to decide**: status file only / fleet comms message on M1 / phone push.

## 8. Burn-in tests before a node counts as a swarm node (N9)

- **Reboot test:** `sudo systemctl reboot`. Seats and watchdog come back with nobody logged in.
- **Kill test:** `tmux kill-session -t <seat>` → back within one restart interval.
- **Hang test:** freeze a seat (`kill -STOP`). The watchdog detects staleness and restarts it.
- **Auth-failure test:** point the service at an empty token file. The watchdog reports CRIT and doesn't loop-restart forever.
  Then restore the file.
- **Network test:** turn the router's Wi-Fi off and on. The node reconnects by itself.
- **48 h unattended**, then read the health log: no gaps, no silent failures.
- Record every result in `ubuntu_server_machines.md`.

## 9. Open decisions (operator)

1. Which seats run on ubu001 / ubu002, and on what cadence (`/loop` or not)?
2. Is the GitHub repo private? Read-only or push access for node seats?
3. Escalation channel for watchdog alerts.
4. Permission mode for unattended seats.
5. Router DHCP reservations for .218 / .219 (and every future node).

## 10. Adding the next machine (checklist)

1. Runbook s3: install from the USB stick (pick **USB HDD** in the BIOS; set up Wi-Fi on the installer's network screen this time).
2. Runbook s8: SSH key, sudo, `ubuntu_server_setup.sh`, reboot and check.
3. Claude login over SSH from M2, then `claude setup-token` (s4).
4. Deploy key + clone + operator-copied secrets (s6).
5. Seat services + watchdog (s5, s7) using the files proven on the guinea pigs.
6. Burn-in (s8). Add a row to `ubuntu_server_machines.md`. DHCP reservation. Naming: `ubu003`, `ubu004`, ...

## 11. Log

- 2026-09-25: ubu001/002 through N4. Battery limits 75/80 set permanently on both (`battery-charge-limit.service`).
  Linger enabled on both. `claude setup-token` confirmed present in CLI 2.1.282. `claude auth status` shows
  loggedIn/claude.ai/max on ubu001. Plan written; waiting on N5 and decisions 1-4.
- 2026-09-25: **ubu001 N5 done.** `claude setup-token` token issued 2026-09-25, stored in `~/.config/prometheus/claude.env` (600).
  Verified from M2 with an EMPTY `CLAUDE_CONFIG_DIR` (so the normal login could not be used): authMethod oauth_token, `claude -p` answered OK.
  Token content never left the node.
- 2026-09-25: **ubu002 N5 done.** Token issued 2026-09-25; same isolated verification (oauth_token, OK). **Both tokens are due
  for renewal around 2026-09 next year**; the watchdog (N8) must count down from `token_issued`.
- 2026-09-25: **N6 code done on both.** The repo is **public** (GitHub API answers 200 unauthenticated), so no deploy key was needed
  to clone. `~/Prometheus` on ubu001 and ubu002 at origin HEAD 815cdb32a (2.8 GB working tree, 1.0 GB .git); disk 6% used.
  Push access and secrets are still pending (they depend on the seat assignments).
- 2026-09-25: **Remote-control sessions live on both (operator's request, for phone access).**
  - Command: `claude --dangerously-skip-permissions --remote-control <hostname>` in `~/Prometheus`, session names
    `ubu001` / `ubu002`.
  - Started by the systemd user unit `~/.config/systemd/user/claude-rc@.service` (enabled as `claude-rc@<hostname>`). It opens
    tmux session `<hostname>` running `~/bin/claude-rc-loop.sh`, which restarts claude 30 s after any exit and logs to
    `~/claude-rc.log`.
  - First-run prompts (folder trust, bypass-permissions warning) were accepted once by hand through tmux; they're remembered.
  - **Reboot test PASSED on both:** sessions came back with no human input. On ubu002, zero users were logged in.
  - Each restart creates a **new** claude.ai/code session URL under the same name.
  - **Auth caveat (open):** these sessions use the interactive claude.ai login (N4), NOT the setup-token (not loaded, and
    it's untested whether Remote Control accepts a setup-token). If that login lapses, the RC session fails, and fixing it
    needs a browser login over SSH from M2. The watchdog (N8) must detect it. **To test:** does RC work with only
    `CLAUDE_CODE_OAUTH_TOKEN`?
  - Watch/intervene from M2: `ssh -t jcraig@<ip> tmux attach -t <hostname>` (detach: Ctrl+B then D).
  - Stop: `ssh jcraig@<ip> systemctl --user stop claude-rc@<hostname>`. Disable at boot: `... disable ...`.
- 2026-09-25: GitHub CLI installed on both (`gh` 2.46.0 from Ubuntu apt). **Not authenticated.** Clone and pull need no
  auth (public repo); push, PRs and issues do. Recommended: a fine-grained GitHub token limited to jcraig949jfi/Prometheus
  (Contents + Pull requests: read/write), one per node, stored like the Claude token, rather than `gh auth login`,
  which grants the whole account to agents running with permissions bypassed. git user.name/email are not set on the
  nodes yet (M2 uses "James Craig").
- 2026-09-25: **Per-node git identity set** (operator's choice): `James Craig (ubu001)` / `James Craig (ubu002)`, email
  jcraig@jfi.ai (the same as M2, so GitHub still links commits to the account; the name shows which node made them).
  Also `pull.ff=only`. New nodes: `git config --global user.name "James Craig ($(hostname))"`.
- 2026-09-25: **GitHub push access working on both** (verified with `git push --dry-run` to a probe branch; nothing was
  pushed). One fine-grained token per node (names `ubu001` / `ubu002`), repo-limited to jcraig949jfi/Prometheus, Contents +
  Pull requests read/write. The operator entered each with `gh auth login --with-token` over SSH (the tokens never passed
  through Claude). Stored in `~/.config/gh/hosts.yml`; git uses them via `gh auth setup-git`.
  - **Token expiry:** ubu001 **2026-10-25** (30-day default), ubu002 **2027-09-25**. The watchdog must warn on both
    (`gh api -i` shows the `Github-Authentication-Token-Expiration` header).
  - **Gotcha seen twice:** a push 403 while reads work means the token's Repository access is "Public repositories"
    (read-only regardless of permissions) or Contents is still read-only. Fix: "Only select repositories → Prometheus" +
    Contents read/write, then Update. Edits apply to the existing token; nothing changes on the node.
  - Operator's plaintext copy of the tokens on M2 (`C:\tokens\`) should be deleted once no longer needed (advised).
