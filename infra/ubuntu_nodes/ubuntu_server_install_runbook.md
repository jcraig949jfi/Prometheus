# Ubuntu Server install runbook: converting old Windows machines

Started 2026-09-25. Use this for every machine being converted to an Ubuntu
server that will run Claude Code.

## 0. Machine log

Moved to `D:\Prometheus\docs\ubuntu_server_machines.md` (hostname, username, IP and status for each machine).

## 1. The installer ISO

- Image: **Ubuntu Server 26.04.1 LTS**, `ubuntu-26.04.1-live-server-amd64.iso` (2,927,861,760 bytes)
- Saved at: `D:\ISOs\ubuntu-26.04.1-live-server-amd64.iso`
- Source: https://releases.ubuntu.com/26.04/
- SHA256: `cc8a95cde20f6ced61a322420de00f10cc3c90ced545daa46cb9c1a117f1d927`

## 2. Making the bootable USB (already done; reuse the same stick)

The stick is a **Verbatim STORE N GO, 124 GB, serial 057A19C55070**. It showed up as disk 2 / `E:` on M2.
The same stick installs every machine; it does not need to be rewritten between installs.

How it was made (elevated PowerShell on M2):
1. Downloaded the ISO with curl and checked it with `sha256sum -c` (result OK).
2. `Clear-Disk -Number 2 -RemoveData -RemoveOEM` (removable disks can't be set offline; that error is harmless).
3. Raw-wrote the ISO to `\\.\PhysicalDrive2` in 4 MB blocks (same as `dd`).
   Script: `write_usb.ps1` (read-back loop must use `[long]`, not Int32, for files over 2 GB).
4. Read back 2,927,861,760 bytes from the stick: the SHA256 matched the ISO exactly.

To remake the stick, check the disk number with `Get-Disk` first. The number can change, and writing to the wrong one destroys that disk.

After writing, **Windows can't read the stick**. If Windows offers to format it, click **Cancel**.
The stick boots on both older BIOS machines and newer UEFI ones.

## 3. Per-machine install steps

1. Plug in the stick and power on. Press the boot-menu key (F12 / F11 / F10 / F9 / Esc, depending on the maker)
   and pick the USB drive. Having Windows installed doesn't block this.
   If it won't boot from USB: go into the BIOS setup and turn off Secure Boot, or turn on legacy/CSM mode.
   If the BIOS offers **USB CD / USB FDD / USB HDD**, pick **USB HDD**: the stick is written as a hard-disk image.
   If USB HDD doesn't boot, USB CD is the second thing to try. Never pick USB FDD (floppy).
2. Language / keyboard: defaults.
3. Network: a wired connection is easiest. Set up Wi-Fi here if the machine has no cable.
4. **Guided storage configuration**:
   - `(X) Use an entire disk` and select the machine's internal disk. This **wipes Windows**, which is the intent.
     The USB stick isn't listed as a target.
   - **Leave Passphrase / Confirm passphrase EMPTY.** A passphrase encrypts the disk and must be typed at the
     machine's keyboard on every boot, which breaks remote reboots of a headless server.
   - Leave "Also create a recovery key" unticked.
   - If "Set up this disk as an LVM group" appears, leave it ticked (standard).
   - Done, then Continue on the summary screen. **That confirmation is the point the disk gets erased.**
   - The other option, keeping Windows and dual-booting via Custom storage layout, was rejected as not worth it for a server.
5. Profile: your name, server name (hostname), username, password. Use a hostname scheme you'll recognise (e.g. m4, m5).
6. **Install OpenSSH server: YES.**
7. Featured snaps: skip.
8. The install runs. **It is finished when the bottom of the screen shows "Reboot Now"** (while it's still running,
   the button reads "Cancel update and reboot"). "View full log" is optional.
9. Choose Reboot Now. When it says "Please remove the installation medium", pull the USB stick and press Enter.
   If the stick is left in, the machine may boot the installer again.

## 4. First boot

On the console, log in with the username and password from step 5, then:

```
ip -br a                      # note the IP address
sudo apt update && sudo apt upgrade -y
```

From M2 (or any other machine): `ssh <username>@<ip>`.

Recommended:
- Give it a fixed IP: a DHCP reservation in the router is simplest.
- Copy an SSH key over: `ssh-copy-id <username>@<ip>` (from a machine with a key).
- If it's a laptop, stop it sleeping when the lid is closed: in `/etc/systemd/logind.conf` set `HandleLidSwitch=ignore`, then run `sudo systemctl restart systemd-logind`.

## 5. Claude Code

```
curl -fsSL https://claude.ai/install.sh | bash
claude
```

There's no browser on a server, so copy the login link it prints into a browser on another computer and paste the code back.
Git is usually preinstalled on Ubuntu Server; if it isn't, run `sudo apt install -y git`.

## 6. Notes / problems hit

- 2026-09-25 machine #1: the storage screen showed Windows' existing partitions (ESP 499M, MSR 128M, NTFS 235.4G,
  NTFS recovery 2.4G) on the Samsung 238 GB disk. Went with "Use an entire disk", no passphrase.
- 2026-09-25 ubu001 (ThinkPad X1 Carbon, no Ethernet port): came up with **no network** after install. The installer
  wasn't given Wi-Fi details, so the Wi-Fi was never configured. **For laptops without an Ethernet port, set up Wi-Fi on
  the installer's network screen**, or plug in a USB Ethernet dongle before installing.
- 2026-10-02 ubu003 (Dell Latitude E7240): first reboot showed "Invalid partition table!" (Dell Legacy/UEFI mismatch; see the
  machine log). **Plug the Ethernet cable in BEFORE installing.** With no cable at install time, the installer writes no config for
  the wired port and it comes up with IPv6 only. Fix with one-line YAML (no indentation to get wrong):
  `echo 'network: {version: 2, ethernets: {eno1: {dhcp4: true}}}' | sudo tee /etc/netplan/50-wired.yaml`, then `sudo chmod 600` it
  and `sudo netplan apply`. The same form works for Wi-Fi:
  `network: {version: 2, wifis: {wlp4s0: {dhcp4: true, access-points: {"SSID": {password: "PASS"}}}}}`.
  Wi-Fi names start with lowercase **wl** (never the digit 1); a wrong interface name gives "A dependency job failed".
  If the Wi-Fi stays DOWN, check `grep . /sys/class/rfkill/*/name /sys/class/rfkill/*/hard`: `hard=1` on `phy0` is a firmware
  block (ubu003 is stuck like this and runs on Ethernet).

## 7. Fixing "no network" after install (Wi-Fi via netplan)

```
ip -br a                      # list interfaces; Wi-Fi is usually wlp<N>s0, wired en*/eth*
ip route                      # which interface holds any address you see
dpkg -l wpasupplicant         # needed for Wi-Fi; see below if missing
```

Create the Wi-Fi config (replace the interface name, network name and password):

```
sudo nano /etc/netplan/60-wifi.yaml
```
```yaml
network:
  version: 2
  wifis:
    wlp4s0:
      dhcp4: true
      access-points:
        "YourNetworkName":
          password: "YourWifiPassword"
```
```
sudo chmod 600 /etc/netplan/60-wifi.yaml
sudo netplan apply
ip -br a                      # should now show a 192.168.1.x address on the Wi-Fi interface
ping -c 3 ubuntu.com
```

If `wpasupplicant` isn't installed, install it from the USB stick. Its package archive has the file, and there's no network needed:
```
sudo mkdir -p /mnt/usb && sudo mount /dev/sdb1 /mnt/usb     # check the device name with lsblk
find /mnt/usb/pool -name 'wpasupplicant*.deb'
sudo apt install /mnt/usb/pool/.../wpasupplicant_*.deb        # path from the find above
```
Troubleshooting order used on the X1 Carbons (2026-09-25):
1. `dpkg -l wpasupplicant | tail -1` should start with `ii` (installed).
2. Is the Wi-Fi switched off? `rfkill` isn't installed; use `grep . /sys/class/rfkill/*/name /sys/class/rfkill/*/soft /sys/class/rfkill/*/hard`. All 0 means not blocked.
3. `journalctl -u netplan-wpa-wlp4s0 -n 20 --no-pager`: this is where a **wrong password** shows up. That was the actual cause on the X1 Carbons.
   Fix the password in the yaml, then `sudo netplan apply`. If the password contains `"` or `\`, wrap it in single quotes
   instead (a `'` inside is written as `''`).

(The easy alternative: plug in a USB Ethernet dongle. Netplan's default config picks up wired connections automatically.)

## 8. Automated setup from M2 (after the network is up)

1. Copy M2's SSH key to the new machine (password asked once), in PowerShell:
   `type C:\Users\James\.ssh\id_ed25519.pub | ssh jcraig@<ip> "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"`
   (Don't leave off the leading `type`: PowerShell gives an "Unexpected token" error without it.)
2. Passwordless sudo (password asked once):
   `ssh -t jcraig@<ip> "echo 'jcraig ALL=(ALL) NOPASSWD:ALL' | sudo tee /etc/sudoers.d/jcraig && sudo chmod 440 /etc/sudoers.d/jcraig"`
3. Run `D:\Prometheus\docs\ubuntu_server_setup.sh` on it (usage line at the top of the script); log at `/tmp/prom_setup.log`.
   It extends the disk, installs updates, sets the lid switch to ignore, turns Wi-Fi power save off, installs Claude Code,
   sets battery charge limits 75/80 (laptops) and enables linger.
4. Reboot (`sudo systemctl reboot`), then check: `iw dev wlp4s0 get power_save` = off, `df -h /` shows the full disk,
   `claude --version` works.
5. Log in to Claude Code: `ssh jcraig@<ip>`, run `claude`, and open the printed link in a browser on M2.
   **Do this over SSH from M2, not at the laptop's own screen.** The link and code can't be copied and pasted on the laptop console.
   In PowerShell, select the link with the mouse and right-click to copy; right-click to paste the code back.
   Check from M2 afterwards: `ssh jcraig@<ip> 'bash -lc "claude -p \"Reply with exactly: OK\""'`
6. Next: turning the machine into an always-on swarm node (long-lived token, seat services, health watchdog, burn-in)
   is in `D:\Prometheus\docs\ubuntu_swarm_node_plan.md`.
