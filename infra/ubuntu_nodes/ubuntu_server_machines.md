# Ubuntu server machines

The log of converted machines. Install steps are in `D:\Prometheus\docs\ubuntu_server_install_runbook.md`.
Don't record passwords here.

| # | Hostname | Username | Installed  | OS                        | Disk                         | IP | Status |
|---|----------|----------|------------|---------------------------|------------------------------|----|--------|
| 1 | ubu001   | jcraig   | 2026-09-25 | Ubuntu Server 26.04.1 LTS | Samsung MZVLW256 238 GB NVMe | 192.168.1.218 (Wi-Fi) | **Ready**; Claude Code logged in |
| 2 | ubu002   | jcraig   | 2026-09-25 | Ubuntu Server 26.04.1 LTS | Samsung MZVLW256 238 GB NVMe | 192.168.1.219 (Wi-Fi) | **Ready**; Claude Code logged in |

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
