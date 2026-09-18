"""Reproduce the committed locks on THIS host (TECHNE-34 / TECHNE-82, 2026-09-16).

    py -3.12 -m techne.scripts.reproduce_locks [--lock NAME ...] [--profile light_probe]

`techne.scripts.acquire` is the FIRST-host verb: it re-resolves and REWRITES the lock. This
is the every-later-host verb: the committed lock is installed exactly as written
(`pip install --require-hashes --no-deps`), nothing is re-resolved, no lock is rewritten,
and one INSTALLATION receipt records per lock whether the hashes still install, whether the
manifest entry's import works in the env, and the env's own pip freeze hash afterwards.

Refuses a lock whose interpreter tag (cpXY-platform in the file name) is not the running
interpreter's: a lock is not portable evidence, and installing a cp312 lock into a cp314
venv would be a different resolution wearing the lock's name.

CHEAT CONTROL, run every time: a one-line lock derived from the first real lock with one hex
digit of its hash flipped MUST fail to install (pip's --require-hashes refuses). If it does
not fail, the receipt is marked CONTROL_FAILED and the whole run is not evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
import sysconfig

from techne.acquisition import budget as _budget
from techne.acquisition import manifest_io, paths, pypi, receipt

HOST_TAG = f"cp{sys.version_info.major}{sys.version_info.minor}-{sysconfig.get_platform()}"


def _lock_tag(lock: pathlib.Path) -> str:
    m = re.match(r"^(?P<entry>.+?)-(?P<tag>cp\d+-.+)\.lock\.txt$", lock.name)
    return m.group("tag") if m else ""


def _lock_entry(lock: pathlib.Path) -> str:
    return lock.name.split("-cp")[0]


def _flip_one_hex(lock_text: str) -> str:
    m = re.search(r"--hash=sha256:([0-9a-f]{64})", lock_text)
    h = m.group(1)
    flipped = ("0" if h[0] != "0" else "1") + h[1:]
    return lock_text.replace(h, flipped, 1)


def _pip_freeze_sha256(py: pathlib.Path, b: _budget.Budget) -> tuple[str | None, int]:
    r = b.run([str(py), "-m", "pip", "freeze", "--all"])
    if r["returncode"] != 0:
        return None, 0
    lines = sorted(ln.strip().lower() for ln in r["stdout"].splitlines() if ln.strip())
    return hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest(), len(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lock", action="append", help="lock file name(s) under techne/acquisition/locks; default all")
    ap.add_argument("--profile", default="light_probe")
    a = ap.parse_args(argv)
    locks = sorted(paths.locks().glob("*.lock.txt"))
    if a.lock:
        locks = [l for l in locks if l.name in a.lock or _lock_entry(l) in a.lock]
    man = manifest_io.load() if hasattr(manifest_io, "load") else json.loads(paths.manifest_path().read_text(encoding="utf-8"))
    entries = {e["id"]: e for e in man["entries"]}
    prof = _budget.get_profile(a.profile)
    rec = receipt.new("INSTALLATION", "lock_reproduction", tool="committed locks")
    rec["host_tag"] = HOST_TAG
    rec["observations"]["locks"] = []
    rec["does_not_establish"].append("that any entry is QUALIFIED for a scientific run; this is reproduction of an INSTALLATION")
    with _budget.Budget(profile=prof) as b:
        env_cache = {}
        for lock in locks:
            row = {"lock": lock.name, "entry": _lock_entry(lock), "lock_sha256": hashlib.sha256(lock.read_bytes()).hexdigest(),
                   "lock_tag": _lock_tag(lock), "status": None}
            if row["lock_tag"] != HOST_TAG:
                row["status"] = "REFUSED_WRONG_INTERPRETER_TAG"
                row["why"] = f"lock is {row['lock_tag']}, this interpreter is {HOST_TAG}"
                rec["observations"]["locks"].append(row)
                print(row["lock"], row["status"], row["why"])
                continue
            head = lock.read_text(encoding="utf-8").splitlines()[0]
            m = re.search(r"isolated env '([^']+)'", head)
            env_name = m.group(1) if m else "h0h5_tools"
            row["env"] = env_name
            if env_name not in env_cache:
                env_cache[env_name] = pypi.ensure_env(env_name, b)
            envinfo = env_cache[env_name]
            row["env_python"] = envinfo["python_version"]
            if envinfo["is_live_interpreter"]:
                row["status"] = "REFUSED_WOULD_TOUCH_LIVE_INTERPRETER"
                rec["observations"]["locks"].append(row)
                continue
            inst = pypi.install_locked(env_name, lock, b)
            row["install_returncode"] = inst["returncode"]
            row["install_seconds"] = inst["wall_seconds"]
            row["stderr_tail"] = inst["stderr_tail"][-600:]
            row["env_created_now"] = envinfo["created_now"]   # False => "already satisfied" is possible
            if inst["returncode"] != 0:
                row["status"] = "LOCK_DOES_NOT_INSTALL"
            else:
                e = entries.get(row["entry"])
                if e and e.get("import_name"):
                    row["import"] = pypi.verify_import(env_name, e["import_name"], e["distribution"], b)
                    row["status"] = "REPRODUCED" if row["import"].get("imported") else "INSTALLED_IMPORT_FAILS"
                    row["pinned_version"] = e.get("pinned_version")
                    row["version_matches_pin"] = row["import"].get("dist_version") == e.get("pinned_version")
                else:
                    row["status"] = "INSTALLED_NO_MANIFEST_ENTRY"
            rec["observations"]["locks"].append(row)
            print("%-42s %-28s import=%s version=%s" % (row["lock"], row["status"],
                  (row.get("import") or {}).get("imported"), (row.get("import") or {}).get("dist_version")), flush=True)
        # cheat control: a flipped hash must be refused
        real = [l for l in locks if _lock_tag(l) == HOST_TAG]
        ctl = {"status": "NOT_RUN"}
        if real:
            src = real[0]
            tampered = paths.tool_cache() / "reports" / ("TAMPERED-" + src.name)
            tampered.parent.mkdir(parents=True, exist_ok=True)
            tampered.write_text(_flip_one_hex(src.read_text(encoding="utf-8")), encoding="utf-8")
            env_name = [r for r in rec["observations"]["locks"] if r["lock"] == src.name][0].get("env", "h0h5_tools")
            # --ignore-installed: the packages are already present after the real install, and pip
            # says "already satisfied" without checking a hash -- the first run of this control on
            # M2 passed a tampered lock for exactly that reason (CONTROL_FAILED, receipt
            # installation-lock_reproduction-20260916T141254Z). Forcing the fetch makes it bite.
            ci = pypi.install_locked(env_name, tampered, b, ignore_installed=True)
            ctl = {"derived_from": src.name, "install_returncode": ci["returncode"],
                   "status": "REFUSED_AS_EXPECTED" if ci["returncode"] != 0 else "CONTROL_FAILED",
                   "stderr_tail": ci["stderr_tail"][-400:]}
            tampered.unlink(missing_ok=True)
        rec["observations"]["cheat_control_tampered_hash"] = ctl
        for env_name, info in env_cache.items():
            h, n = _pip_freeze_sha256(pypi.env_python(env_name), b)
            info["pip_freeze_sha256_after"] = h
            info["pip_freeze_n_after"] = n
        rec["observations"]["envs"] = env_cache
    rows = rec["observations"]["locks"]
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    rec["observations"]["counts"] = counts
    eligible = [r for r in rows if r["status"] != "REFUSED_WRONG_INTERPRETER_TAG"]
    # a run with nothing eligible is NOT a reproduction (the offline test caught 0 == 0 reading as green)
    if ctl["status"] == "CONTROL_FAILED":
        rec["status"] = "CONTROL_FAILED"
    elif not eligible:
        rec["status"] = "NO_ELIGIBLE_LOCKS"
    elif counts.get("REPRODUCED", 0) == len(eligible) and ctl["status"] == "REFUSED_AS_EXPECTED":
        rec["status"] = "REPRODUCED"
    else:
        rec["status"] = "PARTIAL"
    out = receipt.write(rec)
    print("LOCK-REPRODUCTION", rec["status"], json.dumps(counts, sort_keys=True), "cheat:", ctl["status"], "->", out)
    return 0 if rec["status"] == "REPRODUCED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
