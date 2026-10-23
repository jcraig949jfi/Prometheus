# Ubuntu server machines

The log of converted machines. Install steps are in `D:\Prometheus\docs\ubuntu_server_install_runbook.md`.
Don't record passwords here.

| # | Hostname | Username | Installed  | OS                        | Disk                         | IP | Status |
|---|----------|----------|------------|---------------------------|------------------------------|----|--------|
| 1 | ubu001   | jcraig   | 2026-09-25 | Ubuntu Server 26.04.1 LTS | Samsung MZVLW256 238 GB NVMe | 192.168.1.218 (Wi-Fi) | **Ready**; Claude Code logged in |
| 2 | ubu002   | jcraig   | 2026-09-25 | Ubuntu Server 26.04.1 LTS | Samsung MZVLW256 238 GB NVMe | 192.168.1.219 (Wi-Fi) | **Ready**; Claude Code logged in |
| 3 | ubu003   | jcraig   | 2026-10-02 | Ubuntu Server 26.04.1 LTS | LITE-ON LMT-256 238 GB SATA (mSATA) | 192.168.1.220 (wired, eno1) | Setup done; Claude Code logged in (shared OAuth token, 2026-10-06) |
| 4 | ubu004   | jcraig   | 2026-10-02 | Ubuntu Server 26.04.1 LTS | WD5000LPCX 500 GB 5400 rpm HDD | 192.168.1.221 (USB Ethernet, canonical); Wi-Fi .178 (wlp2s0) | **Provisioned** (first autoinstall + provision_node.sh); GitHub token pending; Claude logged in 2026-10-06 |
| 5 | ubu005   | jcraig   | 2026-10-04 | Ubuntu Server 26.04.1 LTS | Team MP33 1 TB NVMe in a USB-C enclosure (external) | 192.168.1.222 (wired, enp0s31f6); Wi-Fi .227 (wlp4s0) | **Provisioned**, worker active (shared token); Claude logged in 2026-10-06 |
| 6 | ubu006   | jcraig   | 2026-10-03 | Ubuntu Server 26.04.1 LTS | Seagate ST500DM002 500 GB 7200 rpm HDD | 192.168.1.225 (wired, enp2s0); Wi-Fi .226 (wlp3s0) | **Provisioned**, worker active (shared token); Claude logged in 2026-10-06 |
| 7 | ubu007   | jcraig   | 2026-10-10 | Ubuntu Server 26.04.1 LTS | Patriot P210 256 GB SATA SSD, bay HDD 1 (root 232 GB) | 192.168.1.3 (wired, eno1; no Wi-Fi) | **HOLD -- BAD RAM** (one weak cell, confirmed); worker OFF until a DIMM is pulled/replaced |
| 8 | ubu008   | jcraig   | 2026-10-10 | Ubuntu Server 26.04.1 LTS | WD PC SN730 512 GB NVMe (root 466 GB) | 192.168.1.231 (wired via dock, enp0s31f6); Wi-Fi .232 (wlp0s20f3) | **Provisioned**, worker active (shared token); Claude token installed 2026-10-10 |
| 9 | ubu009   | jcraig   | 2026-10-11 | Ubuntu Server 26.04.1 LTS | Kioxia BG5 KBG50ZNT256G NVMe (root 232 GB) | 192.168.1.230 (USB Ethernet enx9cebe80ae6c4) | **SOAK TEST** (freezes); worker DISABLED until 24 h clean |
| 10 | ubu010  | jcraig   | 2026-10-20 | Ubuntu Server 26.04.1 LTS | WD PC SN730 256 GB NVMe (root 231 GB) | 192.168.1.235 (wired, enp0s31f6; no Wi-Fi) | **Skullport game host since 2026-10-22** (PROD + QA; worker disabled, out of pool); `mind` user + SKULLPORT key; Claude OAuth env copied; see section below |

## Fleet hardware (read live 2026-10-10: lscpu, free, dmidecode, DMI serial)

| Host | Machine | CPU | C/T | AVX2 | RAM | IP (wired / Wi-Fi) | Serial / tag |
|---|---|---|---|---|---|---|---|
| ubu001 | ThinkPad X1 Carbon 5th (20HQS2YJ00) | i5-7300U | 2C/4T | yes | 8 GB | .218 (Wi-Fi) | PF0V02XZ |
| ubu002 | ThinkPad X1 Carbon 5th (20HQS2YJ00) | i5-7300U | 2C/4T | yes | 8 GB | .219 (Wi-Fi) | PF0V0JL6 |
| ubu003 | Dell Latitude E7240 | i7-4600U | 2C/4T | yes | 8 GB | .220 | D5VYTZ1 |
| ubu004 | HP Pavilion x360 14m-ba0xx | i3-7100U | 2C/4T | yes | 8 GB | .221 (USB eth) / .178 | 8CG80912V3 |
| ubu005 | ThinkPad P52s (20LB0010US) | i5-8350U | 4C/8T | yes | 24 GB (8+16) | .222 / .227 | R90T9A2G |
| ubu006 | Dell Inspiron 3647 (desktop) | i3-4130 | 2C/4T | yes | 16 GB | .225 / .226 | J3B1K02 |
| ubu007 | Dell Precision M6500 | i7 Q720 | 4C/8T | **no AVX** | 16 GB | .3 | F64MDN1 |
| ubu008 | ThinkPad T490s (20NX0020US) | i7-8565U | 4C/8T | yes | 16 GB | .231 / .232 | PC1AHQQD |
| ubu009 | IdeaPad Flex 5 14IAU7 (82R7003WUS) | i3-1215U (2P+4E) | 6C/8T | yes | 8 GB LPDDR4X (soldered) | .230 (USB eth) | PW02YB1H |
| ubu010 | Lenovo ThinkCentre M910q tiny desktop (10MV000NUS) | i5-7500T | 4C/4T | yes | 8 GB (1 DIMM, 1 slot free) | .235 (wired) | MJ073DPV |

Corrections: ubu006 is an i3-4130 (was "Haswell, 4 threads"); ubu005 has 24 GB installed (22 GiB usable).
Screens: all nodes blank after 5 min idle (consoleblank=300, also set live); a key or Ctrl+Alt+F2, F1 wakes them.

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
| ELSA | Dell Optiplex 980, i7-860 (4C/8T, no AVX, no integrated graphics), 16 GB DDR3-1333 (4x4 GB, all slots; was 6 GB until 2026-10-05), 240 GB SATA SSD, Radeon HD 5450 | Windows 10 Home | Achilles' seat; builds the autoinstall stick | 192.168.1.163. Candidate Ubuntu conversion later. |
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

## ubu005 (machine #5, Lenovo ThinkPad P52s 20LB0010US)

- **Hardware:** i5-8350U (4C/8T), **22 GB RAM** (largest Linux node), battery limits 75/80 work. Ethernet `enp0s31f6`
  (.222) + Wi-Fi `wlp4s0` (.227). BIOS N27ET56P 1.42 (2025-04-01, current). F1 setup, F12 boot menu.
- **Disk saga:** the HDD1 ZIF connector latch broke (internal 2.5"/NVMe tray unusable). A Samsung PM991 256 GB 2242 in
  the WWAN slot stopped the machine from POSTing (fan at full, black screen; fine with it removed): return it.
  **Runs from a Team MP33 1 TB NVMe in a USB-C enclosure** (shows as `sda`, TRAN usb, model FP6001T). Keep it plugged in.
- **Autoinstall:** CIDATA built with the one-off `--allow-usb-target` (a60650da0); the guard picked the enclosure;
  powered off at the end; booted from the enclosure. **provision_node.sh 192.168.1.222 ubu005:** 2 min (the first try
  was killed by memory pressure on ELSA before it changed anything). Worker at f78d18e26, enabled, IDLE; 47 C idle.
- Still to do: rebuild CIDATA WITHOUT --allow-usb-target; Claude login; DHCP reservation for .222; return the PM991.

## ubu006 (machine #6, Dell Inspiron 3647 small desktop, 2014)

- **Hardware:** Haswell, 4 threads, **16 GB DDR3-1600 (2x 8 GB, since 2026-10-04; was 1x 4 GB)**,
  Seagate ST500DM002 500 GB 7200 rpm HDD (root LV 455 GB), Ethernet `enp2s0` + Wi-Fi `wlp3s0`. UEFI. No battery.
- **Autoinstall:** succeeded, but the old stick config rebooted into the installer with the sticks in, so it
  reinstalled in a loop (fixed on main by `shutdown: poweroff`, 34e7a9a62; stick rebuilt 2026-10-03). After pulling the
  sticks the BIOS said **"No bootable device"**: its UEFI boot list had no Ubuntu entry. Fix (operator, F2 setup):
  Boot -> Add Boot Option "ubuntu" -> `\EFI\ubuntu\shimx64.efi` on the disk's EFI partition. Then it booted.
- **provision_node.sh 192.168.1.225 ubu006:** 13 min (most of it the repo clone); shared token, push dry-run OK;
  no reboot needed. Worker installed at f78d18e26 with --enable: active, IDLE.
- Still to do: Claude login, DHCP reservation for .225.

## ubu007 (machine #7, Dell Precision M6500)

- **Hardware (opened 2026-10-10):** i7 Q720 (no AVX), RAM 2x 8 GB SODIMM in the bottom slots (one Centon; 2 more slots
  under the keyboard; confirm with dmidecode). Two 2.5" SATA bays, 3 Gb/s: **HDD 1** (in the bay by the battery) held an **Intel
  SSD 330 180 GB (SSDSC2CT180A3, fw 300i) = the Windows 7 drive**; **HDD 2** held a **Seagate Momentus 500 GB
  (ST9500424AS, 2012, marked "New")**. FCM and WWAN slots are Mini PCIe (not M.2): unusable for boot.
  Lower fan dusty. Win7 COA under the battery (do not photograph publicly).
- **Plan (operator 2026-10-10; replaces the 2026-10-04 USB-enclosure plan):** a **Patriot P210 256 GB SATA SSD**
  (P210S256G25; DRAM-less, low TBW: watch wear) in **HDD 1** for Ubuntu (the default-boot bay, so the worker comes back
  unattended after a power cut). The **Intel 330 (Win7) goes back in HDD 2**, unmodified; Windows via F12, or a GRUB
  chainload (os-prober) if F12 does not list HDD 2. Leave BIOS "SATA Operation" unchanged. Momentus = spare / backup target.
- **Install:** ONLY the Patriot in the machine (both Windows-side drives out; the guard wipes the largest internal disk
  >= 60 GB). Legacy BIOS, USB first, Ethernet. Normal internal-disk install, so the CIDATA stick needs no
  --allow-usb-target. Image the Intel 330 to M2 before the install (backup only; it is not wiped).
- **Install 2026-10-10:** BIOS boots USB from ONE specific port only (operator found it by trial). Attempt 1 failed in
  curtin extract: `SQUASHFS error: xz decompression failed, data probably corrupt` (no USB/SATA I/O errors; the same
  stick installed ubu008 cleanly). Attempt 2 failed at `netplan apply` (`netplan-wpa-wlan-none.service not found`):
  template bug, fixed in 092ee16a6 (wait 60 s for wl*, else drop wifis). Attempt 3 succeeded, wired only.
- **provision_node.sh 192.168.1.3 ubu007:** setup OK, but the repo clone failed `inflate: data stream error (incorrect
  data check)` -- a second in-memory corruption, now from the network. Suspect RAM: 2x 8 GB DDR3-1333
  (V01D3SF8GB52852813) in DIMM_B + DIMM_D; DIMM_A/C (under the keyboard) empty. `memtester 12G 2` started 17:42Z in
  tmux `memtest` (log ~/memtester_*.log). Pass 1 (12 GB) clean ~19:20Z. Re-clone 19:3xZ during pass 2: 2m10s,
  `git fsck` clean. provision_node.sh re-run: push dry-run OK; Claude token copied from ubu006, claude -p OK.
  Battery and HDD 2 bay left empty; fan blown out (operator). Screen blanked (backlight off + consoleblank=300).
- **BAD RAM CONFIRMED 2026-10-10 ~22:30Z:** memtester 12G (run 2, after a power cut ended run 1 in pass 2) failed 3x at the
  SAME offset 0x1678df398, SAME bit (bit 26 reads 0 instead of 1) under three different patterns: a single weak cell
  (charge-retention failure), not seating/timing (those scatter). Explains both install corruptions. Not localizable to a
  DIMM from software (interleaved; SPD serials blank). Fix: pull DIMM_D, memtest DIMM_B alone; if clean, the pulled stick
  is bad (replace, 8 GB DDR3-1333 SODIMM ~$10-15, or run 8 GB). Fallback: memmap= the page (needs its physical address)
  + 12-24 h hot test. Thermals, lid closed, 1-thread load: median 75 C, max 77 C.
- Wi-Fi: the Intel 6300 enumerated during installer boot 1 (iwlwifi 0000:0c:00.0) but is absent from lspci now: likely
  unseated at reassembly, or Internal WLAN disabled in BIOS. Not needed while wired.

## ubu008 (machine #8, Lenovo ThinkPad T490s)

- **Bought 2026-10-10** (Facebook Marketplace) with a dock and monitor; came with Fedora (wiped, operator OK).
- **Hardware (read 2026-10-10):** i7-8565U, 4C/8T, **AVX2**; 14 GiB usable (16 GB, partly soldered); WD PC SN730 512 GB
  NVMe; wired `enp0s31f6` through the dock (the laptop's own I219 NIC), Wi-Fi `wlp0s20f3`. UEFI, Secure Boot left on.
  Idle 50 C, fan ~2800 rpm (78 C briefly during setup).
- **Autoinstall:** first try, the 2026-10-04 stick (`--allow-usb-target` is harmless when an internal disk exists).
- **provision_node.sh 192.168.1.231 ubu008:** ~4 min; shared token, push dry-run OK; no reboot needed. Worker installed
  at f78d18e26 with --enable: active, IDLE. Claude: `~/.config/claude-oauth.env` copied node-to-node from ubu006 over
  stdin (never printed), sourced from `~/.bashrc` line 1 and `~/.profile`; `claude auth status` oauth_token, `claude -p` OK.
- Still to do: DHCP reservation for .231; BIOS Power On with AC Attach; full `/login` only if it is to host a seat.

## ubu009 (machine #9, Lenovo IdeaPad Flex 5 14IAU7, 2-in-1)

- **Bought 2026-10-11** at Savers for $50 (ex-student, personal; no BIOS lock). i3-1215U (2 P-cores to 4.4 GHz + 4
  E-cores, 8 threads, AVX2), 8 GB LPDDR4X SOLDERED (no upgrade path), Kioxia BG5 256 GB NVMe, BIOS J7CN56WW (2025-07).
  Touchscreen + Wacom pen. No RJ45: runs on a USB Ethernet adapter (enx9cebe80ae6c4).
- **Install:** the autoinstall boot hung ~1.2 s into the kernel (after the Wacom input lines; no Caps Lock response for
  10 min). Operator installed manually ("old school"): no CIDATA, so keys and NOPASSWD sudo were added by hand
  (ELSA key via ssh + password; /etc/sudoers.d/jcraig like the template; M2 key copied from ubu008).
- **Freeze 2026-10-11 20:03:56Z** during the first provision_node.sh repo clone, as the operator moved it: the journal
  stops dead, no shutdown (hard hang; lid-close suspend before the lid=ignore setting took effect is possible). The
  re-run with it still and lid open completed (clone 2m08s). Next boot started with the RTC at 2026-07-27 (chrony
  stepped it). Watch: if it hangs again, try nvme_core.default_ps_max_latency_us=0, then i915/intel_idle limits.
- **Tablet/motion sensors disabled 2026-10-11 ~20:52Z** (operator: "sensitive to being moved"): lenovo_ymc (tablet-mode
  switch via the EC) and hid_sensor_hub (2x accel_3d + intel_hinge) blacklisted in
  /etc/modprobe.d/ubu009-no-tablet-sensors.conf, initramfs rebuilt, unloaded live. Delete the file + reboot to restore
  (e.g. for auto-rotate under a desktop). If it still hangs when moved, suspect seating (NVMe / cables) next.
- **Freezes continue (2026-10-11/12):** 3rd hard hang 21:21Z, stationary, 29 min into memtester (pass 1 of 5 GB clean,
  died in pass 2: memory likely fine); two more boots overnight froze within minutes. NVMe SMART: healthy (0 media
  errors, 7% used) but **444 unsafe shutdowns of 898 power cycles** -- the instability predates us. The RTC resets to
  2026-07-27 20:44:02 on every hard power cycle (CMOS battery / EC). fwupd: BIOS + NVMe firmware current.
- **Mitigations 2026-10-12 10:3xZ:** kernel cmdline `intel_idle.max_cstate=1 i915.enable_dc=0 i915.enable_psr=0
  nvme_core.default_ps_max_latency_us=0`; sysctl soft/hardlockup_panic=1, panic_on_oops=1, panic=10 (auto-reboot, crash
  to efi_pstore); journald SyncIntervalSec=10s; worker disabled. BIOS pass (operator): load defaults, Fast Boot off,
  Flip-to-Start off -- pending. 24 h soak (memtester 3G loop + stress-ng 6 CPU + temp log, tmux `soak`) started 10:32Z.
  Pass -> worker back on. Fail -> REPAIR pile (operator), with this record.
- **Ethernet flow control OFF 2026-10-12 ~10:47Z:** ELSA logged its only DNS timeouts in 6 days (4x, 17:25-18:06 EDT
  10-11) in the 45 min after ubu009 froze at 17:21:32 while still cabled; the ASIX AX88772 had pause frames
  negotiated ("flow control rx/tx"). Hypothesis (inferred from timing, not measured): a hung host's NIC emitting PAUSE
  frames stalled the router's switch. `ethtool -A enx9cebe80ae6c4 autoneg off rx off tx off`, persisted by
  /etc/udev/rules.d/90-ubu009-usbeth-no-flowcontrol.rules; link renegotiated in 3 s ("flow control off"). Test: if it
  freezes again with no DNS stalls on ELSA, the hypothesis gains support.
- Plan (operator): add ubuntu-desktop-minimal later and switch netplan to NetworkManager (usable touchscreen laptop /
  travel machine); not urgent. Pause the worker when travelling.
- **Cover-off soak 2026-10-20/21 (Achilles from ELSA): PASS.** Operator hypothesis: the broken plastic / back cover caused
  the freezes; machine run with the cover OFF, lid-less, upside down. Booted 2026-10-20 14:28:45Z.
  Phase 1 19:16-21:16Z (2 h): stress burners + 4 GB write/verify (`~/stress_full.log`, `~/mem_verify.log`), 1,140 rounds,
  0 bad, peak pkg 72 C. Phase 2 21:18Z-07:18Z (10 h, tmux `soak2` 8 burners with 95 C abort + `memv2`): 5,442 rounds,
  0 MEMFAIL, peak pkg 73 C (60-72 typical, ~2.1-2.8 GHz). Then idle. Read 2026-10-21 21:20Z: up 30 h 51 min, no freeze,
  no reboot, 0 kernel err-level lines since 21:00Z on 10-20, no MCE/EDAC/lockup/hung-task messages.
  12 h under full load and 31 h uptime clear the 24 h bar for the cover-off case. Supports the cover hypothesis but
  doesn't prove it. Next (operator): refit the cover without the broken pieces and rerun the same soak; the worker stays
  disabled until that passes.

- **Back in the pool 2026-10-23 (operator, Achilles session: "I think we can use ubu009 now. We just note that it may get
  pulled if it flakes again").** The cover is still off (the refit and soak rerun were not done first). Probationary:
  pull it again (disable the worker, drop it from ALL_AVAILABLE) at the first freeze or network drop. State at
  return: up 2 d 18 h with no freeze, 8 cores, 7 GB, idle pkg 68 C (warm, cover off). It uses a USB NIC (asix
  enx9cebe80ae6c4, 100 Mb/s) whose journal shows `Failed to enable software MII access` and
  systemd-networkd-wait-online timeouts, so it is the likely flake point. Worker re-enabled (f78d18e26). M1 key
  jcraig@SKULLPORT added. Node and Chromium are NOT installed (that needs a GO), so it runs protocol explorers only.

## ubu010 (machine #10, Lenovo ThinkCentre M910q tiny desktop, 10MV000NUS)

**Skullport GAME HOST since 2026-10-22 (operator GO in the Achilles session: "Approved. ubu010 is now our rust
server").** Reserved: no fleet dispatch (removed from `ALL_AVAILABLE` in fleet_fanout.py, so not in the census pool),
PrometheusWorker disabled (`systemctl --user disable --now prometheus-worker`). Installed: socat, tailscale 1.104.2
(pkgs.tailscale.com apt repo, hostname ubu010; node approval by the operator in the Tailscale admin console;
`tailscale set --operator=skullport` so the game user can run serve/funnel). Game services run as the unprivileged
user `skullport` (uid 1002, no sudo, linger on, authorized_keys: jcraig@SKULLPORT + achilles@elsa), not as jcraig,
because Funnel exposes it to the internet and jcraig has sudo, fleet keys and the worker token. Always on:
sleep/suspend/hibernate targets masked, /etc/systemd/logind.conf.d/90-gamehost-nosleep.conf; BIOS "power on after
AC loss" is a physical step for the operator. Network-namespace isolation for the stacks (operator OK 2026-10-22,
option "scoped unshare"): `kernel.apparmor_restrict_unprivileged_userns` stays 1; a copy of unshare at
/usr/local/lib/skullport/unshare (dir and binary root:skullport 0750) with AppArmor profile
/etc/apparmor.d/skullport-unshare (`userns,` on that path only). Verified: skullport gets a private netns with only lo
(DOWN until the stack brings it up); skullport via /usr/bin/unshare still denied; jcraig cannot exec the copy. Undo:
`sudo apparmor_parser -R /etc/apparmor.d/skullport-unshare; sudo rm -r /etc/apparmor.d/skullport-unshare
/usr/local/lib/skullport`; `sudo tailscale logout; sudo apt-get remove tailscale socat;
sudo systemctl unmask sleep.target suspend.target hibernate.target hybrid-sleep.target suspend-then-hibernate.target;
sudo rm /etc/systemd/logind.conf.d/90-gamehost-nosleep.conf; sudo userdel -r skullport`; re-enable the worker and
put ubu010 back in ALL_AVAILABLE.

**PROD cutover 2026-10-22 ~09:45Z (M1, Skullport).** skullport-prod.service (user unit, rust-only, release
2026.10.21-6-e27dad9, MemoryMax 1500M, TasksMax 512) is enabled/active on 127.0.0.1:5760, next to skullport-qa (:5780)
and skullport-logcap.timer (hourly log cap). The world_5760.db was copied from M1 with the sqlite backup API (hash
checked at both ends, integrity ok). Public route: https://smugglers-hole.tail33be32.ts.net:8443 (M1's Funnel) -> M1
loopback 127.0.0.1:5765 (TCP forwarder, Windows task SkullportProdForward) -> ubu010 `tailscale serve --tcp 15760`
(tailnet only) -> 127.0.0.1:5760. Also tailnet-only on ubu010: https :8443 -> 5760 and :9443 -> 5780. **ubu010 itself
has no Funnel.** Backups: nightly pull to M1 at 04:15 (task SkullportProdBackup, tools/host/pull_backup.sh, keeps 14);
the first backup verified ok. Achilles read-only check right after: both units active, local :5760 HTTP 200, skullport
RSS ~450 MB, 6.3 GB available, 42 C. **Rollback (M1 side):** M1's untouched world_5760.db is in WSL ~/sh_nwn. If
ubu010 PROD has run since, copy its db back first. Then delete build/releases/sites/live5760/HOLD, run
`SK_PROD_ON_M1=1 tools/live.sh start --port 5760 --no-build --no-serve` and
`tailscale funnel --https=8443 http://127.0.0.1:5760` on M1, and stop skullport-prod on ubu010.

**Reboot test PASS 2026-10-22 12:30Z** (the operator's GO, "Reboot if m1 agrees"; M1 agreed with PROD idle).
`sudo systemctl reboot` at 12:30:25Z. Times from when the watcher started: ping back +24s; at +26s ssh, linger user
manager, tailscaled/tailnet, and skullport-prod, -qa and -qa-lan (socat LAN 192.168.1.235:5785 -> QA 5780, for fleet
monkeys) all active; HTTP 200 on 5760/5780/LAN 5785 at +30s; tailnet https 8443/9443 and tcp 15760 at +31s. Nothing
was touched by hand. After boot: no failed units (system or user), OperatorUser=skullport kept, no Funnel on ubu010,
userns restriction 1, skullport-unshare profile loaded, worker still disabled. M1's side also passed: PROD through the
public route (M1 Funnel :8443 -> forwarder -> ubu010 tcp 15760) invite smoke 4/4, and QA over the tailnet 4/4. The M1
forwarder reconnected on its own. Operator items still open: BIOS "power on after AC loss", Tailscale key expiry
off for ubu010, DHCP reservation for .235.

Operator 2026-10-20 ~00:15Z: "New e-waste machine coming online shortly, Lenovo i5, 8GB of RAM"; the operator ran the
autoinstall (typed `yes` ~00:20Z). Achilles (ELSA) provisioned it over SSH.

- **Hardware (read live):** i5-7500T, 4C/4T, AVX2; 8 GB in one of two DIMM slots (7.1 GiB usable); WDC PC SN730 256 GB
  NVMe (root 231 GB, LVM, all space); wired enp0s31f6 only (no Wi-Fi, no battery, no lid). Serial MJ073DPV. Idle 43 C.
- **Install:** autoinstall from the 2026-10-04 CIDATA stick (internal disk present, so `--allow-usb-target` was moot).
  The live installer showed on the LAN at .235 with the ISO's sshd (OpenSSH 2ubuntu3.5) refusing our key, powered off
  ~00:32Z, and the installed system came up at the same DHCP address ~00:40Z with a NEW host key (`ssh-keygen -R
  192.168.1.235` once, then `accept-new`). The installed system's host key is in known_hosts.fleet.
- **provision_node.sh 192.168.1.235 ubu010:** 2 min (updates were small): rename, setup script (Claude Code 2.1.304,
  linger, no battery thresholds), repo at `~/Prometheus` (d56af5024), git identity "James Craig (ubu010)", shared
  GitHub token, push dry-run OK, no reboot needed. Inventory vs ubu001: only the expected differences (no Claude
  login, no claude-rc loop).
- **Worker:** `install_prometheus_worker.sh f78d18e262 --enable` -> PrometheusWorker/ubu010, enabled, active, first
  cycle IDLE (probe: cpu 4, ram_gb_available 6.4, disk_gb_free 198). Same pinned code as the rest of the fleet.
- **Side project:** `mind` user (uid 1001, CPUQuota 200% of 4 threads, MemoryMax 40%, TasksMax 2048, linger) with the
  `smugglers-hole-mind@SKULLPORT` key, via add_side_project_user.sh; `jcraig@SKULLPORT` appended to jcraig's
  authorized_keys (now M2, ELSA, SKULLPORT). At M1's request (same day, under the operator's 2026-10-19 GO): `sudo
  apt-get install -y nodejs npm` (Node v22.22.1, npm 9.2.0) and `~/skullport/.venv` with the fleet set (pyyaml 6.0.3,
  pillow 13.0.0, pytest 9.1.1, opencv-python-headless 4.14.0, numpy 2.5.4, websockets 17.3, scipy 1.18.1; 425 MB).
  NO Chromium and NO Blender here: M1 classes it with ubu004 (8 GB, 2 usable cores, 2 GB RSS per job, protocol monkeys
  and tests only). M1 adds it to its dispatcher's machines.json on 2026-10-20.
- **Claude:** `~/.config/claude-oauth.env` copied node-to-node from ubu006 (piped through ELSA, never written there),
  mode 600, as for ubu007. Full `/login` only if it ever hosts a seat.
- **Still to do:** DHCP reservation for .235 in the router (operator). Added to fleet_fanout.py ALL_AVAILABLE, so the
  census probes it from the next run.
- **RAM upgrade option, deferred (operator 2026-10-20):** ChannelB-DIMM0 is empty; a matching 8 GB DDR4-2400 SODIMM
  (installed: SK Hynix HMA81GS6AFR8N-UH) is about $55 on Amazon and would give 16 GB dual-channel; max 32 GB. Operator:
  "We're not RAM constrained right now. Our issue is breaking work up into small enough tasks to distribute to the
  fleet." Later the same day the operator invited hardware proposals ("anything 2x2GB ... 2x4 is still cheap for older
  e-waste"); the survey below (dmidecode, 2026-10-20) is the basis.

## RAM upgrade candidates (dmidecode survey 2026-10-20, Achilles; operator invited proposals)

| Node | Installed | Slots / max | Upgrade | Amazon search |
|---|---|---|---|---|
| ubu007 | 2x 8 GB DDR3-1333 SODIMM, one cell BAD | 4 slots (2 free under keyboard) | replace both with a new kit; returns an 8-thread box now on HOLD | `16GB (2x8GB) DDR3 1333 SODIMM PC3-10600 laptop` |
| ubu003 | 1x 8 GB DDR3L-1600 | 2 / 16 GB, 1 free | add one stick (16 GB) | `8GB DDR3L 1600 SODIMM PC3L-12800 1.35V` |
| ubu004 | 1x 8 GB DDR4-2133 | 2 / 32 GB, 1 free | add one stick (16 GB) | `8GB DDR4 2400 SODIMM 260-pin` |
| ubu010 | 1x 8 GB DDR4-2400 | 2 / 32 GB, 1 free | add one stick (16 GB), ~$55 | `8GB DDR4 2400 SODIMM 260-pin 1.2V` |
| ubu005 | 8 + 16 GB DDR4-2400 | 2 / 32 GB, full | optional: swap the 8 GB for 16 GB (32 GB) | `16GB DDR4 2400 SODIMM` |
| ubu008 | 2x 8 GB DDR4 | 2 / 32 GB, full | none needed | |
| ubu006 | 2x 8 GB DDR3-1600 DIMM | 2 / 16 GB, full | none (at max) | |
| ubu001, ubu002, ubu009 | soldered LPDDR3 / LPDDR4X | none | cannot be upgraded | |

ubu009 2026-10-20: operator removed its back cover and runs it upside down with no panel (plastic bits fell out, no
visible damage). Not reachable on .230 that day (no ping/ssh, no ARP entry); likely the USB Ethernet adapter got
unplugged while it was moved, or it froze again. It is out of the pool, so the census does not probe it.

## PrometheusWorkers on the Linux nodes (2026-10-03)

Operator: "Yes. The linux fleet for generic workers" (chat 2026-10-03). Installed by Achilles with
`infra/ubuntu_nodes/install_prometheus_worker.sh <code-sha> --enable` (idempotent; roles/generic-worker-role/).

| node | worker | code pinned | push access | service |
|---|---|---|---|---|
| ubu001 | PrometheusWorker/ubu001/ubu001-svc | f78d18e26 | yes (node token) | enabled, active |
| ubu002 | PrometheusWorker/ubu002/ubu002-svc | f78d18e26 | yes (node token) | enabled, active |
| ubu003 | PrometheusWorker/ubu003/ubu003-svc | f78d18e26 | yes (node token) | enabled, active |
| ubu004 | PrometheusWorker/ubu004/ubu004-svc | f78d18e26 | yes (shared token) | enabled, active |
| ubu005 | PrometheusWorker/ubu005/ubu005-svc | f78d18e26 | yes (shared token) | enabled, active |
| ubu006 | PrometheusWorker/ubu006/ubu006-svc | f78d18e26 | yes (shared token) | enabled, active |
| ubu008 | PrometheusWorker/ubu008/ubu008-svc | f78d18e26 | yes (shared token) | enabled, active |
| ubu009 | PrometheusWorker/ubu009/ubu009-svc | f78d18e26 | yes (shared token) | enabled, active again 2026-10-23 (operator: use it now, pull if it flakes) |
| ubu010 | PrometheusWorker/ubu010/ubu010-svc | f78d18e26 | yes (shared token) | disabled 2026-10-22 (game host, out of pool) |

Per node: ~/prometheus-worker-code (detached at the pinned SHA; WORKING_CONTRACT s6), ~/prometheus-worker-state
(detached, re-synced to origin/main by the worker), ~/prometheus-worker (runs/ and results/), systemd user unit
~/.config/systemd/user/prometheus-worker.service (Restart=on-failure, Nice=10, PROMETHEUS_WORKER_CAPS=linux;
linger keeps it running without a login). Idle: one sync every 5 minutes, ~23 MB RSS.
- Log: `journalctl --user -u prometheus-worker -f` (one JSON line per cycle: IDLE / claim outcome).
- Stop: `systemctl --user stop prometheus-worker`. SIGTERM is handled like Ctrl-C (from the code SHA that adds
  it): a run in progress is terminated, receipted PREEMPTED_RESOURCE ("operator stop") and requeued unchanged;
  between runs the loop simply ends (KillMode=mixed, TimeoutStopSec=300 leave time for that).
- Advance the worker code (after tests pass at the new SHA): re-run the install script with the new SHA; it
  re-pins ~/prometheus-worker-code and restarts the service. Record the advance here.
- ubu004: enable after its GitHub token exists (shared token, tokens/shared.txt, then re-run with --enable).
- 2026-10-03 ~10:40Z: worker code advanced fa9cd8151 -> f78d18e26 on all four (clean SIGTERM stop; tests 49 passed
  at f78d18e26); services restarted between runs on ubu001-003.
- 2026-10-03: ubu004 got the shared GitHub token (nodes-shared, no expiry, Prometheus only; installed from
  C:/autoinstall_secrets/tokens/shared.txt, never printed, shredded on the node); push dry-run OK; worker enabled.
- 2026-10-11 ~20:37Z: ubu009 (IdeaPad Flex 5) provisioned with the shared token; worker at f78d18e26, enabled, IDLE.
- 2026-10-10 ~15:39Z: ubu008 (T490s) provisioned with the shared token; worker at f78d18e26, enabled, IDLE.
- 2026-10-04 ~14:12Z: ubu005 (P52s, USB-enclosure root) provisioned with the shared token; worker at f78d18e26, enabled, IDLE.
- 2026-10-03 ~20:05Z: ubu006 (Inspiron 3647) provisioned with the shared token; worker installed at f78d18e26, enabled, IDLE.

## Skullport (M1) side-project access, venvs and Blender (2026-10-17, Achilles from ELSA)

Operator 2026-10-16: give the M1 Claude Code session "Skullport Revive M1 949" all the help it needs to use the Linux
fleet as it sees fit. Coordination runs over Claude Code cross-session messages (not `python -m comms`).

- **SSH key `jcraig@SKULLPORT`** (M1's own ed25519 key, not the `mind` key) appended to `~jcraig/.ssh/authorized_keys` on
  ubu001, ubu003, ubu004, ubu005, ubu006, ubu008 (each now 3 keys: `jcraig@M2`, `achilles@elsa`, `jcraig@SKULLPORT`).
  Only the public line crossed the LAN. M1 confirmed login on .220/.222/.231. ubu002 (offline), ubu007 (HOLD), ubu009
  (soak) not touched.
- **ubu005 + ubu008 user-space setup:** `~/skullport/.venv` (Python 3.14.4; pyyaml 6.0.3, pytest 9.1.1, numpy 2.5.4,
  pillow 13.0.0; 123 MB). M1 scp'd a git bundle and cloned to `~/skullport/repo`; its outfits+minds suites passed on
  ubu005 (111 tests, 6 s). Sharded pytest over the two nodes is light and needs no GO.
- **Rust toolchain on ubu005 + ubu008 (2026-10-22, operator GO in the Achilles session: "Yes, coordinate with m1").**
  The reason: M1 hit a low-memory event from parallel Rust builds, and the operator wants all non-graphics work off M1.
  Installed as jcraig, user-space only, no sudo: rustup with `--profile minimal --default-toolchain stable
  --no-modify-path` (rustc/cargo 1.99.1), plus target x86_64-unknown-linux-musl; 818 MB in ~/.rustup. Use
  `PATH=$HOME/.cargo/bin:$PATH`. build-essential and libssl-dev were already present; pkg-config was not. Smoke test
  passed on both (glibc and static-pie musl builds). A copy installed under `mind` by mistake was uninstalled again.
  Build limits: `taskset -c 2-3 cargo ... -j 2` on ubu005 and `taskset -c 2-7 ... -j 6` on ubu008; Blender has first
  claim on ubu008, plus the usual heat/RSS rules. Release builds made here ship to PROD on ubu010, so these two nodes
  are now on the supply path. Undo: `~/.cargo/bin/rustup self uninstall -y`.
- **Round-the-clock Skullport QA loops (standing OK from Achilles, 2026-10-23).** The owner's policy, as relayed by M1:
  QA cycles run 24/7 and are throttled back on diminishing returns. The bots are "explorers" (websocket protocol) and
  "scouts" (browser). They target QA only (ubu010 :5785), never PROD. An M1 governor adds and removes loops itself within
  these hard limits. Fleet work (worker, pretest, Blender) always takes priority.
  - Per node, at most: ubu001 2 explorers (10 min or less per run); ubu003 2 explorers (5 min or less per run); ubu005
    2 explorers on CPUs 2-3, no Chromium, yields first; ubu006 1 scout (4 GiB PSS cap, yields to pretest) plus 1
    explorer; ubu004 exactly 1 Chromium (drone or scout alternating), 2 GiB PSS, a gap of at least 3 min between
    runs, at most 45 min of GPU work then a 10 min cool-down. ubu008: up to 2 explorers, plus 1 scout (4 GiB PSS cap),
    only while no Blender or cargo job is running (added 2026-10-23 after the operator confirmed continuous testing in
    the Achilles session). ubu009 (from 2026-10-23, probationary): up to 2 explorers, no Chromium until Node/Chromium
    are installed there. None on ubu010. Always nice 15 or more, CPUs 0-1 untouched.
  - The governor adds a loop only when the node is under 70 C, its load5 is under nproc-2, more than 1.5 GB is
    available, and no worker job, pretest or Blender job is running. It removes the newest loop at 80 C or more, when
    such a job starts, or when load goes over nproc-1. Skip at 85 C, pause at 90 C. No new runs between :25 and :40 past
    04/10/16/22Z (census).
  - ubu010 guard: at most 12 QA clients. Thin the loops if skullport-qa uses more than 1 GB or load5 goes over 2. If
    PROD is not active, all QA load stops.
  - Stops: on ubu004, any new i915 error or GPU hang halts GPU work until Achilles clears it. Kill switch: if
    `~/skullport/STOP_ALL` exists on a node, everything there stops within 1 min.
  - Notify Achilles at once when a stop rule fires or a node joins or leaves the set. Otherwise a daily digest.
  - PSS counts as memory (the sum of Pss from /proc/<pid>/smaps_rollup), not summed RSS, which overcounts shared pages
    by about 45% for Chromium.
- **Blender 4.5.14 LTS (headless CPU bakes/renders) on ubu005 + ubu008.** GO given by the operator in the M1 session
  (relayed verbatim). Steps, identical on both: `sudo apt-get install -y libgl1 libxi6 libxxf86vm1 libxfixes3
  libxrender1 libsm6 libice6` (the Blender binary links these even with `-b`; all were missing, ubu005 already had
  libxrender1); `blender-4.5.14-linux-x64.tar.xz` from download.blender.org/release/Blender4.5/, sha256 verified
  against `blender-4.5.14.sha256`, unpacked to `~jcraig/blender` (1.2 GB, archive deleted). Checks: `~/blender/blender
  --version` -> "Blender 4.5.14 LTS, build 2026-09-15 01:31:19"; `blender -b --python-expr "import bpy;
  print(bpy.app.version_string)"` -> `4.5.14 LTS`, hash 62c1db4208e8, clean quit. PrometheusWorker active on both after.
  Not on PATH; run as `~/blender/blender -b <file> -t 6 ...` under tmux.
- **Load agreement:** runs of 30-60 min at up to 6 threads per node, leaving 2 for the PrometheusWorker; M1 states node,
  duration and threads before each run. Sudo, package installs and anything heavier still need an operator GO.
- **Thermals under Blender (measured 2026-10-17 01:40-08:00Z, `x86_pkg_temp` every 2 min from ELSA; the `acpitz` zone
  lags and the `sort | tail -1` hottest-zone trick picks a lagging sensor, so read the zone whose `type` is
  `x86_pkg_temp`):** ubu005 (i5-8350U, thin chassis) swings 60-94 C and the firmware throttles it (clocks 2.8 -> 1.6-2.2
  GHz at the peaks) even at `-t 4`; 20% of busy samples were >= 91 C, trip points 98-115 C, never reached. M2's own
  30-s sampling agreed (91-93 C). Restarting at `-t 3` did not help: 92-94 C through the next two bakes (peak 94 C at
  08:08Z, my samples 93/86/93/77/89/93 C), because a bake is ~1-1.5 cores whatever `-t` says and the chassis cannot shed
  that. **Rule for ubu005 (M1/M2 + Achilles, 2026-10-17): Blender at `-t 2` with a cool-down between bodies, and long
  Blender runs go to ubu008 first.** ubu008 (i7-8565U) holds flat at its 80 C firmware cap (75-82 C over 42 busy
  samples) with no clock collapse, so `-t 6` stays fine there.
  Update 2026-10-17 ~09:10Z: the operator opened ubu005's lid and removed a laptop that had been stacked on it (also
  opened the lids of ubu004 and ubu008). Two 25-33 min `-t 2` bake runs afterwards (97 samples at 30 s): mean 74 C,
  max 93 C once then 88 C, 1% of samples >= 91 C (was 22%), clocks never below 1.9 GHz; the room temperature was not a
  factor (the idle nodes read the same throughout). So ubu005 must stay lid-open and unstacked; `-t 2` remains the rule
  until a `-t 3` trial after the planned compressed-air clean. ubu008's 80 C cap is unaffected by its lid, as expected.
- **Node, headless Chromium, OpenCV on all six available nodes (2026-10-19, Achilles from ELSA).** GO given by the
  operator in the M1 session ("Yes to all this", relayed by M1) so 14 browser/audit task types of M1's job queue
  (tools/fleet/ in the SmugglersHole repo) can leave the Windows PCs. On ubu001/003/004/005/006/008:
  `sudo apt-get install -y nodejs npm libnss3 libnspr4 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libdrm2
  libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2t64 libpango-1.0-0 libcairo2
  libatspi2.0-0t64 fonts-liberation libegl1 libgles2` -> Node v22.22.1 (Ubuntu's packaged LTS; the ask said 20 LTS,
  22 is what the distro ships and no third-party repo was added), npm 9.2.0, plus the Chrome/Playwright runtime
  library set. `sudo snap install chromium` -> chromium 155.0.8059.79 latest/stable at `/snap/bin/chromium` (Ubuntu
  ships Chromium only as a snap; `--headless=new --disable-gpu --dump-dom` verified on all six). OpenCV:
  `~/skullport/.venv` created on the four nodes that lacked it, `opencv-python-headless` 4.14.0 + numpy 2.5.4 installed
  on all six (`--only-binary`, cp314 wheels). Same day, after M1's first fleet wave (46 jobs, ~2 CPU-hours, clean):
  pyyaml 6.0.3, pillow 13.0.0, pytest 9.1.1 added on ubu001/003/004/006, so all six venvs are identical (284 MB:
  pyyaml, pillow, pytest, opencv-python-headless, numpy); then websockets 17.2 + scipy 1.18.1 on all six (operator
  "Yes. Approved" in the Achilles session 2026-10-19; venv 425 MB). Side effect: libegl1/libgles2 are in the Chrome library
  set, so headless Blender Workbench/EEVEE renders now work on ubu005/ubu008 (`-b -E BLENDER_WORKBENCH -f 1` ->
  1.3 MB PNG on both); this closes the EGL question that had waited since 2026-10-17. PrometheusWorker active on all six
  after every step. Install time 1-7 min per node (ubu004/ubu006 slowest, HDDs).
- **iGPU (hardware WebGL) trial, ubu004 (2026-10-21, Achilles from ELSA; operator GO typed in the Achilles session).**
  `sudo usermod -aG render,video jcraig` on ubu004 (Intel HD 620, Kaby Lake GT2). M1 ran the same drone sweep (area
  sk_lp0s, 8 stills, one snap Chromium on CPUs 2-3) twice; Achilles logged pkg temp / MemAvailable / load /
  `gt_act_freq_mhz` every 5 s (`~/gpu_trial_watch.log`) and watched dmesg.
  Pass 1, `--use-angle=gl`: no WebGL, so SwiftShader: area load ~2 m 17 s, ~33 s/still, GPU stayed at 300 MHz idle.
  Pass 2, `--use-angle=vulkan --enable-features=Vulkan --ignore-gpu-blocklist`: renderer "ANGLE (Intel, Vulkan 1.4.318
  (Intel(R) HD Graphics 620 (KBL GT2)), Intel open-source Mesa driver)", area load ~34 s, **~1.7 s/still** (8/8, exit 0,
  same image as pass 1), GPU at 1000 MHz during capture. Both passes: peak pkg 62 C, ~2.1 GB RAM at peak, 0 i915/drm
  errors, no orphans, worker untouched. dmesg shows harmless AppArmor DENIED for snap.chromium reading
  /etc/vulkan/{implicit_layer.d,icd.d} (the snap brings its own Mesa ICD). Verdict: clean; Vulkan is the recipe, GL is not.
  **ubu004 is the one node open for Vulkan browser jobs** (one Chromium per node, CPUs 0-1 free, 2 GB RSS).
  First sustained use 2026-10-22 00:32-00:54Z (M1 drone QA, release 2026.10.21-3, 15 areas x 8 stills, 120 stills,
  exit 0): peak pkg 72 C, mean 60 C, plateau 65-72 C, ~2.2 GB at peak, 0 i915 errors; crashpad handlers reparent to
  init during the run and exit with it. Standing OK to M1: QA after each release, 1-2/day, ~22 min, start notice only;
  ask first if >30 min or >15 areas.
  ubu006 (Intel HD 4400, Haswell GT2, Mesa hasvk), same day, same pass: renderer "ANGLE (Intel, Vulkan 1.2.318 (Intel(R)
  HD Graphics 4400 (HSW GT2)), Intel open-source Mesa driver)", 8/8 stills at ~1.7 s, GPU 1150 MHz, peak pkg 46 C,
  ~2.2 GB, 0 i915 errors: node safe, but **the image is wrong** (streaky roof textures, missing timber framing, blue
  cast; hasvk's incomplete format support). Verdict: GPU works, renders wrong; not for visual work. Groups reverted
  (`gpasswd -d jcraig render/video`) the same hour. The other nodes' GPUs are untested; any trial needs a fresh operator GO.
- Remove cleanly: `rm -rf ~jcraig/blender ~jcraig/skullport`; `sudo snap remove chromium`; `sudo apt-get remove
  nodejs npm libegl1 libgles2 libxi6 libxxf86vm1 libxfixes3 libsm6 libice6 libgl1` (libxrender1 was pre-existing on
  ubu005; the other Chrome libs are harmless to leave); delete the SKULLPORT line from `authorized_keys`; `sudo gpasswd -d jcraig render; sudo gpasswd -d jcraig video`
  on ubu004 (ubu006 already reverted).
