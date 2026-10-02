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

## Cleanup / mop-up list (started 2026-10-02, Achilles on ELSA)

Loose ends from adding ubu003 and the ELSA access. Tick with a date.

- [ ] **ubu003 Claude login** (operator): `ssh jcraig@192.168.1.220`, `claude`, open the link in a browser, paste the code back.
- [ ] **Router DHCP reservation for ubu003 → 192.168.1.220** (wired MAC, `eno1`). Same open item for .218 / .219 below.
- [ ] **ubu003 Wi-Fi hard block** (low priority; runs on Ethernet): EC reset with the battery disconnected, BIOS defaults, or a USB Wi-Fi adapter.
- [ ] **ubu003 temperature:** re-check at idle (79 °C during updates); clean the fan if it stays above ~70 °C.
- [ ] **ubu003 BIOS boot entry:** confirm it boots without the "Invalid partition table!" message; if not, set UEFI + ubuntu boot entry.
- [ ] **Delete `C:\tokens\finegrained tokens.txt` on M2** (also listed below). The old ubu001 token in it is dead; ubu002's is probably still live.
- [x] **ELSA key on ubu002** and consistency check across ubu001/002/003. Done 2026-10-02. ELSA can now log in to all three.
      ubu003 also got M2's key, so it matches the others (`jcraig@M2` + `achilles@elsa`).
- [x] Done 2026-10-02: pulled; all three at 17b6f02bc. ~~**Repos on ubu001/002 are far behind origin:**~~ ubu001 1760 commits (HEAD 22bfbc966, 09-25), ubu002 1432 (ca189b020, 09-27).
      Both trees are clean on `main` with `pull.ff=only`, so `git pull` is safe, but the live RC sessions work in `~/Prometheus`.
      Pull between tasks, or add a pull step to `claude-rc-loop.sh`.
- [x] Done 2026-10-02: full-upgrade + reboot, one at a time; all three on kernel 7.0.0-38, 0 upgradable; RC sessions came back by themselves. ~~**Pending apt updates:**~~ ubu001 9, ubu002 18 (kernel 7.0.0-34; ubu003 is on -38). Upgrade + reboot drops each phone
      session for ~2 min.
- [x] Done 2026-10-02: python3-venv + python3-pip on all three; setup script now installs `gh jq python3-venv python3-pip` too. ~~**Python packages differ:**~~ python3-venv on ubu001 only; python3-pip on ubu002 only; neither on ubu003. Pick one set for
      all nodes (likely both) and add it to `ubuntu_server_setup.sh`.
- [ ] **ubu001 → ubu002 SSH is broken:** ubu001 has `~/.ssh/id_ed25519_ubu002` (comment `odysseus@ubu001->ubu002`, 09-30) and
      a `Host ubu002` entry, but ubu002 doesn't have that public key in `authorized_keys` ("Permission denied"). Ask
      Odysseus whether it's still needed; if so, add the key on ubu002.
- [ ] `systemd-networkd-wait-online.service` shows as failed on ubu001/002 (the Wi-Fi nodes). Usually harmless at boot. Check
      whether anything depends on it.
- [ ] Wi-Fi power-save unit name differs: `wifi-powersave-off.service` on 001/002 vs `wifi-powersave-off-<iface>.service` on 003
      (the current script). Cosmetic.
- [ ] Claude Code versions differ (2.1.283 / .286 / .287); they update themselves. Not a problem.
- [ ] **Bring ubu003 up to the ubu001/002 node setup** if the check shows gaps (RC service, setup-token, etc.).
- [ ] **Update the "State at time of writing" section** below once ubu003 matches the others.
- [x] Commit the `infra/ubuntu_nodes/` changes: done 2026-10-02 (ffa083fad and later commits).
- [x] **Auusda A146 → stays Windows: `LIZZIE-42`** (operator 2026-10-02). Windows 11 Pro 24H2, activated; 8 GB soldered
      (Task Manager: "4 of 4 slots", which is how soldered LPDDR4 shows up). Built-in screen broken; used with an HDMI monitor via
      mini-HDMI. Role: command center / browsing, not a Linux node. See "Other fleet machines" in `ubuntu_server_machines.md`.
- [ ] **ubu004 = HP Pavilion x360 14m-ba0xx** (i3-7100U, 8 GB, no Ethernet port): **first autoinstall test** (CIDATA stick
      configures Wi-Fi). In progress 2026-10-02.
- [ ] **ubu005 = Lenovo ThinkPad P52s** (T580 platform, 2019). The **HDD1 ZIF connector's latch broke** while swapping
      drives; the connector body is still on the board, but reseating + taping the tray cable (several tries, both
      orientations) gives **no drive detected** in BIOS or the Ubuntu installer. The main M.2 2280 tray only connects through
      HDD1, so it's out. USB boot works (F12 boot menu, F1 setup; needed USB HDD moved out of "Excluded from boot order").
      **Fix: Samsung PM991 256GB M.2 2242 NVMe (MZALQ256HAJD) in the empty WWAN slot**, arriving 2026-10-03 (screw post H21;
      operator has the M2 screw). Leave the capped WWAN antenna wires alone. Then autoinstall. Parts on hand: Samsung MZVLB256
      (original, 2280) + Team MP33 1TB (2280), two Lenovo 2.5" NVMe trays.
- [ ] ELSA's own future: reimage as an Ubuntu worker (16 GB DDR3 kit ~$47) or Wake-on-LAN on demand. Its motherboard video
      ports are dead by design (the i7-860 has no integrated graphics); use the Radeon HD 5450 card for installing.
- [ ] **CIDATA stick** (32 GB, label CIDATA) holds the Wi-Fi password in plain text. Keep it at home; rebuild it with
      `autoinstall/build_cidata.py` if the Wi-Fi or keys change. Secrets live in `C:utoinstall_secrets\` on ELSA.

## Operator (needs hands at a keyboard or the router; not the phone)

- [ ] **BIOS: Power On with AC Attach = Enabled** on each laptop (F1 at boot → Config → Power; F10 to save). Also
      Config → Network → Wake On LAN = AC only. Without it, a power cut that drains the battery leaves the node off
      until someone presses the button. Each reboot takes that node's phone session down for about 2 min; it comes back by itself.
- [ ] **Router DHCP reservations:** ubu001 → .218, ubu002 → .219 (and every new node). A router reboot could otherwise
      move the addresses and break SSH from M2 (RC sessions would still work).
- [x] ~~**ubu001 GitHub token expires 2026-10-25**~~ Done 2026-10-02: the operator deleted the old token and created a new
      **no-expiry** one (public open-source repo, operator's choice); Achilles installed it over SSH from ELSA (file → shredded,
      never printed), `git push --dry-run` OK. ubu002's still expires 2027-09-25. ubu003's is no-expiry too.
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
- [ ] Next hostnames: `ubu004` (HP x360), `ubu005` (P52s), `ubu006`, ... (LIZZIE-42 stays Windows, no ubu number)

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
