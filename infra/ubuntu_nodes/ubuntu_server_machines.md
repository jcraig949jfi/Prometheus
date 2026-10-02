# Ubuntu server machines

The log of converted machines. Install steps are in `D:\Prometheus\docs\ubuntu_server_install_runbook.md`.
Don't record passwords here.

| # | Hostname | Username | Installed  | OS                        | Disk                         | IP | Status |
|---|----------|----------|------------|---------------------------|------------------------------|----|--------|
| 1 | ubu001   | jcraig   | 2026-09-25 | Ubuntu Server 26.04.1 LTS | Samsung MZVLW256 238 GB NVMe | 192.168.1.218 (Wi-Fi) | **Ready**; Claude Code logged in |
| 2 | ubu002   | jcraig   | 2026-09-25 | Ubuntu Server 26.04.1 LTS | Samsung MZVLW256 238 GB NVMe | 192.168.1.219 (Wi-Fi) | **Ready**; Claude Code logged in |
| 3 | ubu003   | jcraig   | 2026-10-02 | Ubuntu Server 26.04.1 LTS | LITE-ON LMT-256 238 GB SATA (mSATA) | 192.168.1.220 (wired, eno1) | Setup done; Claude Code installed, **login pending** |
| 4 | ubu004   | jcraig   | 2026-10-02 | Ubuntu Server 26.04.1 LTS | WD5000LPCX 500 GB 5400 rpm HDD | 192.168.1.178 (Wi-Fi, wlp2s0) | **Provisioned** (first autoinstall + provision_node.sh); GitHub token + Claude login pending |

Fill in the IP after first login (`ip -br a`). SSH: `ssh jcraig@<ip>`.

## ubu001

- **Hardware:** Lenovo ThinkPad X1 Carbon, Intel Core i5 7th gen (Kaby Lake, so most likely the 5th-gen X1 Carbon, 2017).
  About 8 GB RAM (not confirmed; check with `free -h`). 238 GB Samsung NVMe SSD.
- **Network hardware:** there's no full-size Ethernet port. The small side port with the network symbol is Lenovo's
  **Ethernet Extension** connector, which needs a matching "ThinkPad Ethernet Extension Adapter" (check the seller's list
  says it works with the X1 Carbon 5th gen). A **USB-to-Ethernet dongle** (USB-A or USB-C, Realtek/ASIX chip) also works,
  needs no drivers on Ubuntu, and can be reused on other machines. Wi-Fi is built in (most likely an Intel 8265, which Ubuntu supports out of the box).
- **2026-09-25:** installed, rebooted, and logged in on the console as jcraig. **There's no network connection.** The screen shows the IP
  10.10.10.2. That isn't the home LAN, which is 192.168.1.x (M1 is 192.168.1.202), so it's unclear which interface or
  network that address belongs to. Still open.
- **Interfaces** (`ip -br a` on the X1 Carbon, 2026-09-25): `lo` UNKNOWN, `enp0s31f6` DOWN (the built-in Intel wired
  Ethernet, reached through the small Ethernet Extension port: it works as soon as a Lenovo adapter and cable are plugged in),
  `wlp4s0` DOWN (Wi-Fi, not configured yet). Neither interface had an address, so the 10.10.10.2 seen earlier wasn't a
  real LAN address.
- **2026-09-25: Wi-Fi fixed.** Configured `wlp4s0` with `/etc/netplan/60-wifi.yaml`. The first attempt failed because of a
  wrong password; after correcting it and running `sudo netplan apply`, the connection came up. IP 192.168.1.218.
- It's a laptop: set the lid switch to ignore once it's on the network (runbook section 4) so it doesn't sleep with the lid closed.

## ubu002 (machine #2)

- **Hardware:** believed to be the same model as ubu001 (ThinkPad X1 Carbon, 7th-gen i5), so it also lacks a full-size Ethernet port.
- **2026-09-25:** booted the installer with BIOS option **USB HDD**. Network/Wi-Fi was **skipped** on the installer screen,
  so it will also need Wi-Fi set up after install (runbook section 7), same as ubu001.
- **2026-09-25: online at 192.168.1.219**, hostname **ubu002** (confirmed by the router's DNS). Wi-Fi set up after install,
  same as ubu001 (wrong password first, then fixed). Username jcraig (confirmed).

## Network check from M2 (2026-09-25)

- ubu001 = 192.168.1.218, ubu002 = 192.168.1.219. The router's DNS resolves both hostnames by name.
- Both answer ping (latency 100-300 ms, which is high for a LAN; probably Wi-Fi power saving).
- Both have SSH running (ed25519 host keys offered).
- SSH key login from M2 works for both (key `C:\Users\James\.ssh\id_ed25519`, made 2026-09-25, no passphrase;
  both hosts' fingerprints are saved in M2's known_hosts).

## Inventory over SSH (2026-09-25)

Both machines are identical:
- ThinkPad X1 Carbon **5th gen** (from the firmware), 4 CPU threads, 8 GB RAM (7.0 GiB usable)
- Samsung MZVLW256HEHP 238.5 GB NVMe
- Ubuntu 26.04.1 LTS, kernel 7.0.0-30-generic
- **The root filesystem is only 98 GB of the 238 GB disk** (the installer's LVM default leaves the rest unallocated).
  Fix: `sudo lvextend -r -l +100%FREE /dev/ubuntu-vg/ubuntu-lv`
- Before setup: `iw` not installed; sudo needed a password; lid switch at the default (suspend).

## Setup done over SSH from M2 (2026-09-25, both machines)

Script: `D:\Prometheus\docs\ubuntu_server_setup.sh` (the version saved there has the working Wi-Fi power-save fix).
- Passwordless sudo for jcraig: `/etc/sudoers.d/jcraig` (set by the operator).
- Root filesystem extended 100 GB -> **232 GB** (full disk).
- apt full-upgrade, kernel 7.0.0-30 -> **7.0.0-34**; installed iw, git, curl, htop, tmux.
- Lid switch -> ignore (`/etc/systemd/logind.conf.d/10-server-lid.conf`), confirmed after reboot.
- Wi-Fi power save **off**: the first attempt (udev rule) did NOT survive reboot; it's now done by
  `/etc/modprobe.d/iwlwifi-powersave-off.conf` + `wifi-powersave-off.service`. Confirmed off after a reboot;
  ping from M2 dropped from ~120 ms to **1-3 ms**.
- Claude Code **2.1.282** at `~/.local/bin/claude` (on PATH at login). Logged in 2026-09-25 (via SSH from M2); `claude -p` test answered OK on both.
- Rebooted twice; both came back on Wi-Fi at the same IPs.

Still to do: DHCP reservations for .218/.219 in the router.

## Batteries (2026-09-25, both on AC; read from /sys/class/power_supply/BAT0)

| Machine | Charge | Status | Full now / design | Health | Cycles |
|---------|--------|--------|-------------------|--------|--------|
| ubu001  | 100%   | Not charging (full) | 46.75 / 57.0 Wh | **82%** | 342 |
| ubu002  | 64%    | Charging at 22.4 W  | 19.11 / 57.0 Wh | **34%** (worn out) | 844 |

Both batteries are LGC 01AV494 (Li-poly). **Charge limits set 2026-09-25: start charging below 75%, stop at 80%**, made permanent by
`battery-charge-limit.service` (writes BAT0/charge_control_start_threshold and charge_control_end_threshold at boot).
ubu001 was at 100% when set, so it stays there until it drains below 80%; it does not discharge on purpose.
To check from M2: `ssh jcraig@<ip> upower -i /org/freedesktop/UPower/devices/battery_BAT0`

## ubu003 (machine #3, Dell Latitude E7240)

Converted 2026-10-02 by Achilles (ELSA) with the operator.

- **Hardware:** Dell Latitude E7240, Intel Core i7-4600U (Haswell, 2C/4T, AVX2), 8 GB RAM. Has a built-in RJ45 Ethernet port (`eno1`).
  Wi-Fi interface `wlp4s0`. Also has NFC (`nfc0`).
- **BIOS keys:** F2 = setup, F12 = one-time boot menu.
- **First reboot after install showed "Invalid partition table!"** from the Dell firmware (Legacy/UEFI mismatch). It still went on to
  boot Ubuntu. If it ever stops booting: F12 → pick the UEFI "ubuntu" entry; permanent fix is F2 → General → Boot Sequence → UEFI,
  Add Boot Option `\EFI\ubuntu\shimx64.efi`.
- **The installer didn't configure the wired port** because no cable was plugged in during install: it came up with only IPv6
  addresses. Fixed with a one-line netplan file (avoids the YAML indentation errors from typing in nano):
  `echo 'network: {version: 2, ethernets: {eno1: {dhcp4: true}}}' | sudo tee /etc/netplan/50-wired.yaml`, then `chmod 600` + `netplan apply`.
  IP **192.168.1.220** (wired). Still to do: DHCP reservation in the router.
- **Wi-Fi doesn't work: hard rfkill block on all radios.** `grep . /sys/class/rfkill/*/name /sys/class/rfkill/*/hard` shows
  `dell-wifi`, `dell-bluetooth` and **`phy0` (the card itself)** all at `hard=1`; `nfc0` is 0. So it's a real hardware/firmware block,
  not just the `dell_laptop` driver. Tried, with no change: BIOS Wireless Device Enable (WLAN ticked), Wireless Switch (WLAN ticked),
  Wireless Radio Control ("Control WLAN radio" off), Fn+End/PrtScrn, unplugging Ethernet, reboot.
  Not yet tried: EC reset (power off, charger out, battery disconnected, hold power 30 s), BIOS defaults, a USB Wi-Fi adapter.
  **Decision 2026-10-02 (operator): run on Ethernet only for now.** The first Wi-Fi attempt also used a wrong interface name (`wlp2s0`);
  the correct name is `wlp4s0` (lowercase L).
- First login showed 71 °C at load 2.6 (probably background updates). Check again at idle; clean the fan if it stays hot.
- **SSH:** ELSA's key (`achilles@elsa`) added to `authorized_keys` (only the public key was served from ELSA over the LAN, once).
- **Setup 2026-10-02 (from ELSA over SSH, `ubuntu_server_setup.sh`):** passwordless sudo (`/etc/sudoers.d/jcraig`, typed by the operator);
  root LV extended 100 GB -> **236 GB** (full disk); apt full-upgrade, kernel 7.0.0-30 -> **7.0.0-38**; lid switch -> ignore;
  Claude Code **2.1.287** at `~/.local/bin/claude`; linger on. **Battery limits 75/80 work on this Dell** (BAT0 exposes
  `charge_control_*_threshold`), unlike what we expected. Wi-Fi power-save service created for `wlp4s0` (harmless while blocked).
  Rebooted once; came back on 192.168.1.220. Memory at idle: ~630 MB used of 7.2 GiB.
- Temperature: up to 79 °C during boot and updates; 63 °C settling. Re-check at idle; clean the fan if it stays high.
- **Repo 2026-10-02:** cloned `~/Prometheus` (public repo, no auth needed to clone/pull); HEAD 17b6f02bc, `git pull` OK.
  3.6 GB tree incl. 1.1 GB .git; disk 6% used. Git identity `James Craig (ubu003)` / jcraig@jfi.ai, `pull.ff=only`.
  `gh` 2.46.0 installed, **not authenticated**: push needs a per-node fine-grained token (operator enters it; swarm todo step 5).
- **GitHub push 2026-10-02:** fine-grained token `ubu003` (Prometheus only; Contents + Pull requests read/write) entered by
  Achilles from a file the operator saved on ELSA: copied over SSH to a mode-600 temp file, fed to `gh auth login --with-token`,
  then shredded on ubu003 and deleted on ELSA; never printed. `gh auth setup-git` done. `git push --dry-run` to a probe branch
  succeeded (nothing pushed). **No expiry, by the operator's choice** (public open-source repo; GitHub sends no expiration header).

## Access from ELSA (2026-10-02)

ELSA's key (`achilles@elsa`) is in `authorized_keys` on **ubu001** and **ubu003** (not yet ubu002). On ubu001 the operator ran
`curl` at the console to fetch it from ELSA; the attempts before that, typed at ubu001's own console, had only added empty lines,
which were removed. ubu001's `authorized_keys` now has exactly two keys: `jcraig@M2`, `achilles@elsa`.

## Other fleet machines (not Ubuntu nodes)

| Name | Hardware | OS | Role | Notes |
|---|---|---|---|---|
| ELSA | Dell Optiplex 980, i7-860 (4C/8T, no AVX, no integrated graphics), 6 GB DDR3 (3x2 GB, 1 slot free), 240 GB SATA SSD, Radeon HD 5450 | Windows 10 Home | Achilles' seat; builds the autoinstall stick | 192.168.1.163. Candidate Ubuntu conversion later. |
| LIZZIE-42 | Auusda A146 14.1" (Celeron, 8 GB soldered, SATA SSD) | Windows 11 Pro 24H2 (activated) | Command center, browsing | Built-in screen broken: external monitor on mini-HDMI. Kept as Windows by the operator 2026-10-02. |

## ubu004 (machine #4, HP Pavilion x360 14m-ba0xx)

The **first node built with the autoinstall stick + `provision_node.sh`** (2026-10-02, Achilles on ELSA).

- **Hardware:** i3-7100U (2C/4T), 8 GB, **WD5000LPCX 500 GB 5400 rpm HDD (slow)**; PNY CS900 250 GB SATA SSD wishlisted.
  Wi-Fi Intel AC 3168 (`wlp2s0`, iwlwifi). No Ethernet port: installed with a USB Ethernet adapter (`enxa0cec801f116`, .221).
  BIOS: Esc = startup menu, F9 = boot devices, F10 = setup. No battery charge-limit support (BAT0 has no thresholds).
- **Autoinstall attempts:** #1 crashed at network apply (netplan refuses `match:` for Wi-Fi); #2 failed at `install_iw`
  (the installer environment has no `wpa_supplicant`, so Wi-Fi was down and there was no network); #3 with the USB Ethernet
  adapter plugged in: **success**, about 14 min from boot to SSH. It came up on Wi-Fi by itself.
- **provision_node.sh 192.168.1.178 ubu004:** 4 min (rename, updates, Claude Code 2.1.288, clone, git identity). Inventory
  matches ubu001 except the expected items (no GitHub token yet, no battery limit). Root LV is 455 GB (full disk, from the
  autoinstall layout).
- Still to do: shared GitHub token (`tokens/shared.txt` → re-run step 4 or the whole script), Claude login, DHCP reservation for .178.

