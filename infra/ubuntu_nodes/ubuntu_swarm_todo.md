# Ubuntu swarm: TODO

Created 2026-09-25 at the end of the guinea-pig session (ubu001 + ubu002). None of these are urgent (operator's call); the
nodes are live and reachable from the phone. Tick items off here with a date. Design and history are in
`ubuntu_swarm_node_plan.md`; per-machine facts are in `ubuntu_server_machines.md`; install steps are in
`ubuntu_server_install_runbook.md`.

## State at time of writing (2026-09-25)

- ubu001 (192.168.1.218) and ubu002 (192.168.1.219): ThinkPad X1 Carbon 5th gen, Ubuntu 26.04.1, Wi-Fi.
- Always-on `claude --dangerously-skip-permissions --remote-control <hostname>` in tmux via `claude-rc@<hostname>`
  (user systemd, linger on); reboot-tested. The operator gives them work from the phone.
- Auth: interactive claude.ai login (used by the RC sessions), plus a setup-token in `~/.config/prometheus/claude.env`
  (verified, but NOT used by the RC sessions yet).
- GitHub: per-node fine-grained tokens, push verified (dry run). Git identity `James Craig (<hostname>)`.
- Battery limits 75/80, lid ignore, Wi-Fi power save off, full disk.

## Operator (needs hands at a keyboard or the router; not the phone)

- [ ] **BIOS: Power On with AC Attach = Enabled** on each laptop (F1 at boot → Config → Power; F10 to save). Also
      Config → Network → Wake On LAN = AC only. Without it, a power cut that drains the battery leaves the node off
      until someone presses the button. Each reboot takes that node's phone session down for about 2 min; it comes back by itself.
- [ ] **Router DHCP reservations:** ubu001 → .218, ubu002 → .219 (and every new node). A router reboot could otherwise
      move the addresses and break SSH from M2 (RC sessions would still work).
- [ ] **ubu001 GitHub token expires 2026-10-25** (30-day default). Extend or regenerate it; if regenerated, re-enter it on the node
      with `gh auth login --with-token` over SSH. ubu002's expires 2027-09-25.
- [ ] **Delete `C:\tokens\finegrained tokens.txt`** on M2 (plaintext working tokens).
- [ ] Optional: **SSH from the phone** (Termius or Blink): create a key in the app and send the public half to Claude to
      add to both nodes. That's the fallback for a lapsed Claude login while away from M2.
- [ ] Optional: **Tailscale** on the nodes (+ phone) so SSH works away from home Wi-Fi. Needs a browser login per node.
- [ ] Decide: escalation channel for watchdog alerts (status file / M1 fleet comms / phone push).
- [ ] Decide: seat assignments per node (currently generic sessions, work given from the phone).
- [ ] Decide: commit the ubuntu_* docs + setup script to git.
- [ ] If seats need the M1 database: the operator copies the needed `keys.py` key files to the node with `scp` (Claude doesn't
      handle key files). Set `EW_DB_HOST=192.168.1.202`.

## Claude (can be done over SSH from M2 without the operator)

- [ ] **Test Remote Control with only the setup-token** (empty `CLAUDE_CONFIG_DIR` + `CLAUDE_CODE_OAUTH_TOKEN`). If it
      works, switch `claude-rc-loop.sh` to load `~/.config/prometheus/claude.env` so the phone sessions stop depending
      on the interactive login. If it doesn't, record that and make the watchdog alert on interactive-login loss.
- [ ] **Health watchdog (plan s7):** 15-min user timer running `~/bin/prom_health.sh`:
  - `claude auth status` + a `claude -p` OK probe
  - RC session alive (tmux + service)
  - Claude token countdown from `token_issued`, and GitHub token expiry from the `gh api -i` header
  - disk / battery / AC / Wi-Fi IP
  - writes `~/prom_health.txt` (current) + `~/prom_health.log`
  - The operator checks from the phone by asking a session to read `~/prom_health.txt`.
- [ ] Nightly (04:00 local) RC session restart so it picks up auto-updated CLI versions. Note: each restart gives the
      phone a new session under the same name.
- [ ] Verify `unattended-upgrades` is on (security updates); keep automatic reboots OFF.
- [ ] Cap journald (`SystemMaxUse=500M`) and rotate `~/claude-rc.log`.
- [ ] Burn-in tests from plan s8 (kill, hang, auth failure, network drop, 48 h) and record the results.
- [ ] Fold everything proven above into `ubuntu_server_setup.sh` (or a second script, `ubuntu_swarm_node_setup.sh`),
      so a new node goes from fresh install to phone-reachable Claude in one pass.

## Next week: adding more machines

Before the session:
- [ ] Have the Verbatim USB stick (already written; reusable) and the ISO (`D:\ISOs\`) on hand.
- [ ] Collect for each machine: make/model, whether it has an Ethernet port, and whether it has Wi-Fi.
- [ ] Next hostnames: `ubu003`, `ubu004`, ...

Per machine (runbook + plan s10), with the lessons from the guinea pigs:
1. BIOS: boot **USB HDD**; set **Power On with AC Attach** while you're in there.
2. Installer: **set up Wi-Fi on the network screen** (both guinea pigs skipped it and needed the netplan fix), whole disk,
   no passphrase, hostname `ubuNNN`, user jcraig, **OpenSSH on**.
3. From M2: SSH key → passwordless sudo → `ubuntu_server_setup.sh` → reboot.
4. Claude login **over SSH from M2** (never at the laptop console), then `claude setup-token` → `claude.env`.
5. `git clone`, git identity, `gh` + a new fine-grained token for that node (**"Only select repositories → Prometheus"**,
   Contents + PRs read/write, 1-year expiry).
6. Install `claude-rc@.service` + `claude-rc-loop.sh`, accept the two first-run prompts via tmux, reboot test.
7. Router DHCP reservation. Add a row to `ubuntu_server_machines.md`.
