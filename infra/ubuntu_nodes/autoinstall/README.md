# Ubuntu autoinstall stick (CIDATA)

Hands-off install for new swarm nodes (built 2026-10-02 by Achilles on ELSA). It replaces runbook §3 steps 2-7 and most of §8.

## What the stick sets up

- Wired port (`en*`) **and** Wi-Fi (`wl*`) via DHCP, so it works on any of the laptops
- Whole internal disk, LVM, root uses **all** the space, no passphrase. The target is the largest NON-USB disk
  (>= 60 GB), pinned by path in the first early-command; with no such disk the install REFUSES before touching
  any disk (P52s 2026-10-03: an invisible internal SSD made it install onto the CIDATA stick)
- User `jcraig` (console password from `pwhash.txt`), hostname `ubu-new` (renamed after first SSH)
- OpenSSH with the M2 and ELSA keys preinstalled; passwordless sudo; lid switch ignored; linger on
- Packages: only what installs from the stick (git curl htop tmux wpasupplicant); the rest (iw gh jq python3-venv
  python3-pip) and updates come from ubuntu_server_setup.sh / provision_node.sh after the first boot

## Make the stick (once)

1. A spare USB stick, **FAT32, volume label `CIDATA`**. The current one is the **32 GB Micro Center stick** ("the Micro Center stick"; the Ubuntu installer is the 124 GB Verbatim). (Windows only formats FAT32 up to 32 GB; for a bigger stick,
   make a small FAT32 partition.)
2. `C:\autoinstall_secrets\wifi.txt`: line 1 Wi-Fi name, line 2 Wi-Fi password.
3. `C:\autoinstall_secrets\pwhash.txt`, in PowerShell:
   `& "C:\Program Files\Git\usr\bin\openssl.exe" passwd -6 | Out-File -Encoding ascii C:\autoinstall_secrets\pwhash.txt`
4. Extra SSH public keys go in `C:\autoinstall_secrets\keys\*.pub` (M2's is there). The local `~/.ssh/id_ed25519.pub` is always added.
5. `python build_cidata.py E:` (it refuses unless E: is FAT and labelled CIDATA).

The stick then holds the Wi-Fi password in plain text. Keep it at home.

## Install a machine

1. Unplug any other USB drives. Plug in the **Ubuntu installer stick + the CIDATA stick**, and **a wired connection**
   (Ethernet port or USB Ethernet adapter). **Required:** the installer environment has no `wpa_supplicant` when it applies the
   network config, so Wi-Fi can't come up during the install, and the late `install_iw` download step fails without a cable
   (HP x360, 2026-10-02: `Unable to locate executable '/sbin/wpa_supplicant'`, then `install_iw` exit 100). The Wi-Fi
   config is still written into the installed system and works from the first boot, so the cable can come out after.
   Only two USB ports? Boot with both sticks, answer `yes`, then swap the CIDATA stick for the adapter (the config is
   already read; the network comes up on hotplug).
2. Boot from the installer stick (BIOS boot menu: F12 ThinkPad/Dell; or Windows `shutdown /r /o /t 0` → Use a device).
3. At GRUB just wait (or Enter). The installer finds the config and asks **"Continue with autoinstall? (yes|no)"**. Type
   `yes`, Enter. That is the last chance before the disk is erased.
4. About 15-25 min later it reboots by itself. Pull both sticks.
5. Tell Achilles, or run it yourself from ELSA/M2: `bash ../provision_node.sh <ip> ubuNNN` (rename, setup script, repo,
   git identity, GitHub token from `C:utoinstall_secrets	okens\`, reboot, inventory). About 30 s on an already-set-up node;
   10-15 min on a fresh one (updates).
