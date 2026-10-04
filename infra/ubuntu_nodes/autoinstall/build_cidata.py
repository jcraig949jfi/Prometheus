"""Write an Ubuntu autoinstall CIDATA stick from user-data.template.yaml.

Usage (on ELSA or M2):  python build_cidata.py E: [--allow-usb-target]
  --allow-usb-target  ONE-OFF: a machine with no usable internal disk may install onto exactly one external USB
                      disk >= 200 GB (never a stick). Rebuild without the flag right after that install.
  E: = a FAT32 USB stick whose volume label is CIDATA (format it in Explorer first).

Secrets are read from local files and never printed:
  C:\\autoinstall_secrets\\wifi.txt     line 1 = Wi-Fi name (SSID), line 2 = Wi-Fi password
  C:\\autoinstall_secrets\\pwhash.txt   output of `openssl passwd -6` (the jcraig console password, hashed)
SSH keys: this machine's ~/.ssh/id_ed25519.pub plus any *.pub in C:\\autoinstall_secrets\\keys\\.
"""
import ctypes
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
SECRETS = pathlib.Path(r"C:\autoinstall_secrets")


def volume_label(drive):
    buf = ctypes.create_unicode_buffer(261)
    fs = ctypes.create_unicode_buffer(261)
    ok = ctypes.windll.kernel32.GetVolumeInformationW(
        f"{drive}\\", buf, 261, None, None, None, fs, 261)
    return (buf.value, fs.value) if ok else (None, None)


def main():
    args = sys.argv[1:]
    allow_usb = "--allow-usb-target" in args
    args = [a for a in args if a != "--allow-usb-target"]
    if len(args) != 1 or not args[0].rstrip("\\/").endswith(":"):
        sys.exit("usage: python build_cidata.py E: [--allow-usb-target]")
    drive = args[0].rstrip("\\/")
    label, fs = volume_label(drive)
    if label != "CIDATA" or not (fs or "").upper().startswith("FAT"):
        sys.exit(f"refusing: {drive} has label={label!r} fs={fs!r}; need a FAT32 stick labelled CIDATA")

    wifi = (SECRETS / "wifi.txt").read_text(encoding="utf-8-sig").splitlines()
    ssid, wpass = wifi[0].strip(), wifi[1].strip()
    pwhash = (SECRETS / "pwhash.txt").read_text(encoding="utf-8-sig").strip()
    if not pwhash.startswith("$6$"):
        sys.exit("pwhash.txt doesn't look like `openssl passwd -6` output ($6$...)")

    keys = []
    for p in [pathlib.Path.home() / ".ssh" / "id_ed25519.pub", *sorted((SECRETS / "keys").glob("*.pub"))]:
        if p.exists():
            for line in p.read_text(encoding="utf-8-sig").splitlines():
                line = line.strip()
                if line.startswith("ssh-") and line not in keys:
                    keys.append(line)
    if not keys:
        sys.exit("no SSH public keys found")

    t = (HERE / "user-data.template.yaml").read_text(encoding="utf-8")
    # json.dumps gives double-quoted strings, which are valid YAML scalars (handles quotes/backslashes).
    t = (t.replace("@@WIFI_SSID@@", json.dumps(ssid))
          .replace("@@WIFI_PASSWORD@@", json.dumps(wpass))
          .replace("@@PASSWORD_HASH@@", json.dumps(pwhash))
          .replace("@@ALLOW_USB_TARGET@@", "1" if allow_usb else "0")
          .replace("@@AUTHORIZED_KEYS@@", "\n".join(f"      - {json.dumps(k)}" for k in keys)))
    left = re.findall(r"@@[A-Z_]+@@", t)
    if left:
        sys.exit(f"unfilled placeholder(s) left in template: {left}")

    root = pathlib.Path(drive + "\\")
    (root / "user-data").write_text(t, encoding="utf-8", newline="\n")
    (root / "meta-data").write_text("instance-id: prometheus-autoinstall\n", encoding="utf-8", newline="\n")
    print(f"wrote user-data + meta-data to {drive} (ssid set, password hash set, {len(keys)} SSH keys: "
          + ", ".join(k.split()[-1] for k in keys) + ")")
    if allow_usb:
        print("USB TARGET ALLOWED on this stick (one-off). Rebuild WITHOUT --allow-usb-target after this install.")


if __name__ == "__main__":
    main()
