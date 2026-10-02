# Ubuntu autoinstall stick (CIDATA)

Hands-off install for new swarm nodes (built 2026-10-02 by Achilles on ELSA). It replaces runbook §3 steps 2-7 and most of §8.

## What the stick sets up

- Wired port (`en*`) **and** Wi-Fi (`wl*`) via DHCP, so it works on any of the laptops
- Whole internal disk, LVM, root uses **all** the space, no passphrase
- User `jcraig` (console password from `pwhash.txt`), hostname `ubu-new` (renamed after first SSH)
- OpenSSH with the M2 and ELSA keys preinstalled; passwordless sudo; lid switch ignored; linger on
- Packages: git curl htop tmux iw gh jq wpasupplicant python3-venv python3-pip; all updates applied

## Make the stick (once)

1. A spare USB stick, **FAT32, volume label `CIDATA`**. (Windows only formats FAT32 up to 32 GB; for a bigger stick,
   make a small FAT32 partition.)
2. `C:\autoinstall_secrets\wifi.txt`: line 1 Wi-Fi name, line 2 Wi-Fi password.
3. `C:\autoinstall_secrets\pwhash.txt`, in PowerShell:
   `& "C:\Program Files\Git\usr\bin\openssl.exe" passwd -6 | Out-File -Encoding ascii C:\autoinstall_secrets\pwhash.txt`
4. Extra SSH public keys go in `C:\autoinstall_secrets\keys\*.pub` (M2's is there). The local `~/.ssh/id_ed25519.pub` is always added.
5. `python build_cidata.py E:` (it refuses unless E: is FAT and labelled CIDATA).

The stick then holds the Wi-Fi password in plain text. Keep it at home.

## Install a machine

1. Unplug any other USB drives. Plug in the **Ubuntu installer stick + the CIDATA stick**.
2. Boot from the installer stick (BIOS boot menu: F12 ThinkPad/Dell; or Windows `shutdown /r /o /t 0` → Use a device).
3. At GRUB just wait (or Enter). The installer finds the config and asks **"Continue with autoinstall? (yes|no)"**. Type
   `yes`, Enter. That is the last chance before the disk is erased.
4. About 15-25 min later it reboots by itself. Pull both sticks.
5. Tell Achilles. It finds `ubu-new` on the LAN, renames it `ubuNNN`, then runs `ubuntu_server_setup.sh`, the repo clone,
   git identity and the GitHub token.
