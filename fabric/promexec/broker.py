#!/usr/bin/python3 -I
"""promexec-run -- the root-owned execution broker (installed as /usr/local/sbin/promexec-run, root:root 0755).

Operator ruling 2026-09-28: "Claude may propose code; only promexec executes it."

    sudo -n /usr/local/sbin/promexec-run --run-id ID --in STAGING_DIR --out RESULT_DIR --script NAME
         [--wall-s N] [--mem-mb M] [--cpu-pct P] [--tasks T] [-- script args...]

1. INPUT: the files in STAGING_DIR are read AS THE CALLER (the SUDO_UID), so root never reads a path the caller
   could not. Only regular files are taken: no symlinks, devices or hardlink tricks. There are size and count caps.
   They are streamed as a tar into the run directory and extracted AS promexec. Root never touches content.
2. RUN: /opt/promexec/py/bin/python -I <script> runs as the promexec UID in a transient system unit
   (systemd-run) with MemoryMax, CPUQuota, TasksMax and RuntimeMaxSec, and a clean environment containing only
   HOME, LANG, PROMEXEC_IN and PROMEXEC_OUT. EXTRA_PROPERTIES adds hardening, but only where the hostile suite
   shows the UID alone is insufficient; each property is justified there.
3. OUTPUT: regular files under the run's out/ are read AS promexec and extracted AS THE CALLER into RESULT_DIR.
4. The run directory is removed. The broker prints one JSON summary line.
promexec has no credentials, no sudo, no groups, and cannot traverse /home/jcraig (0750).
"""
import json
import os
import pwd
import re
import shutil
import subprocess
import sys
import tarfile
import time

RUNS = "/var/lib/promexec/runs"
PY = "/opt/promexec/py/bin/python"
EXEC_USER = "promexec"
MAX_IN_BYTES, MAX_IN_FILES = 256 * 2**20, 2000
MAX_OUT_BYTES, MAX_OUT_FILES = 64 * 2**20, 500
LIMITS = {"wall_s": (1, 3600), "mem_mb": (64, 4096), "cpu_pct": (10, 400), "tasks": (4, 256)}
# Hardening beyond the UID. Each entry is justified by a hostile-suite finding (fabric/promexec/HOSTILE.md).
EXTRA_PROPERTIES = []


def die(msg, code=2):
    print(json.dumps({"ok": False, "refused": msg}))
    sys.exit(code)


def drop_to(uid, gid):
    os.setgroups([])
    os.setgid(gid)
    os.setuid(uid)


def stream_tar_as(uid, gid, root, max_bytes, max_files):
    """Fork: as uid, tar the regular files under root (no symlinks) to a pipe. Returns the read end and the pid."""
    r, w = os.pipe()
    pid = os.fork()
    if pid == 0:
        try:
            os.close(r)
            drop_to(uid, gid)
            total = n = 0
            with os.fdopen(w, "wb") as f, tarfile.open(fileobj=f, mode="w|") as t:
                for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
                    dirnames[:] = [d for d in dirnames if not os.path.islink(os.path.join(dirpath, d))]
                    for fn in filenames:
                        p = os.path.join(dirpath, fn)
                        fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW)
                        st = os.fstat(fd)
                        if not (st.st_mode & 0o170000 == 0o100000):          # regular files only
                            os.close(fd)
                            continue
                        n += 1; total += st.st_size
                        if n > max_files or total > max_bytes:
                            os._exit(3)
                        ti = tarfile.TarInfo(os.path.relpath(p, root)); ti.size = st.st_size; ti.mode = 0o644
                        with os.fdopen(fd, "rb") as fh:
                            t.addfile(ti, fh)
            os._exit(0)
        except Exception:
            os._exit(4)
    os.close(w)
    return r, pid


def extract_as(uid, gid, fd_r, dest):
    pid = os.fork()
    if pid == 0:
        try:
            drop_to(uid, gid)
            os.makedirs(dest, exist_ok=True)
            with os.fdopen(fd_r, "rb") as f, tarfile.open(fileobj=f, mode="r|") as t:
                t.extractall(dest, filter="data")                            # no links, devices, absolute or ../ names
            os._exit(0)
        except Exception:
            os._exit(5)
    os.close(fd_r)
    return pid


def transfer(src_uid, src_gid, src, dst_uid, dst_gid, dst, max_bytes, max_files):
    r, p1 = stream_tar_as(src_uid, src_gid, src, max_bytes, max_files)
    p2 = extract_as(dst_uid, dst_gid, r, dst)
    s1 = os.waitpid(p1, 0)[1]; s2 = os.waitpid(p2, 0)[1]
    return os.waitstatus_to_exitcode(s1), os.waitstatus_to_exitcode(s2)


def main():
    if os.geteuid() != 0:
        die("must run via sudo")
    a = sys.argv[1:]
    script_args = a[a.index("--") + 1:] if "--" in a else []
    a = a[:a.index("--")] if "--" in a else a
    opts = dict(zip(a[0::2], a[1::2]))
    caller = int(os.environ.get("SUDO_UID", "-1"))
    if caller <= 0:
        die("no non-root SUDO_UID")
    cpw = pwd.getpwuid(caller); epw = pwd.getpwnam(EXEC_USER)
    run_id = opts.get("--run-id", "")
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", run_id):
        die("bad run id")
    script = opts.get("--script", "")
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,120}\.py", script):
        die("script must be a plain *.py file name inside the staging dir")
    src, dst = opts.get("--in", ""), opts.get("--out", "")
    if not (os.path.isabs(src) and os.path.isabs(dst)):
        die("--in and --out must be absolute")
    lim = {}
    for k, (lo, hi) in LIMITS.items():
        v = int(opts.get("--" + k.replace("_", "-"), lo if k != "wall_s" else 600))
        lim[k] = max(lo, min(hi, v))
    rundir = os.path.join(RUNS, run_id + "-" + os.urandom(4).hex())
    os.makedirs(rundir, mode=0o700)
    os.chown(rundir, epw.pw_uid, epw.pw_gid)
    summary = {"ok": False, "run_dir": rundir, "limits": lim, "extra_properties": EXTRA_PROPERTIES}
    try:
        c1, c2 = transfer(caller, cpw.pw_gid, src, epw.pw_uid, epw.pw_gid, os.path.join(rundir, "in"), MAX_IN_BYTES, MAX_IN_FILES)
        if c1 or c2:
            die("input transfer failed (as caller: %s, as promexec: %s)" % (c1, c2))
        for d in ("out", "work"):
            os.makedirs(os.path.join(rundir, d), exist_ok=True); os.chown(os.path.join(rundir, d), epw.pw_uid, epw.pw_gid)
        unit = "promexec-" + re.sub(r"[^A-Za-z0-9]", "", run_id)[:40] + "-" + os.urandom(3).hex()
        props = ["User=" + EXEC_USER, "Group=" + EXEC_USER, "WorkingDirectory=" + os.path.join(rundir, "work"),
                 "MemoryMax=%dM" % lim["mem_mb"], "MemorySwapMax=0", "CPUQuota=%d%%" % lim["cpu_pct"],
                 "TasksMax=%d" % lim["tasks"], "RuntimeMaxSec=%d" % lim["wall_s"],
                 "StandardOutput=truncate:" + os.path.join(RUNS, unit + ".stdout"),
                 "StandardError=truncate:" + os.path.join(RUNS, unit + ".stderr"),
                 "Environment=HOME=%s LANG=C.UTF-8 PROMEXEC_IN=%s PROMEXEC_OUT=%s MPLBACKEND=Agg OMP_NUM_THREADS=2"
                 % (os.path.join(rundir, "work"), os.path.join(rundir, "in"), os.path.join(rundir, "out"))] + EXTRA_PROPERTIES
        cmd = ["systemd-run", "--unit=" + unit, "--wait", "--collect", "--service-type=exec"]
        for p in props:
            cmd += ["-p", p]
        cmd += ["--", PY, "-I", "-B", os.path.join(rundir, "in", script)] + script_args
        t0 = time.time()
        r = subprocess.run(cmd, capture_output=True, text=True, env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"})
        summary["wall_s_used"] = round(time.time() - t0, 2)
        m = re.search(r"Finished with result: (\S+)", r.stderr)
        summary["result"] = m.group(1) if m else ("success" if r.returncode == 0 else "unknown")
        m = re.search(r"status=(\d+)", r.stderr)
        summary["exit_code"] = int(m.group(1)) if m else r.returncode
        for k in ("stdout", "stderr"):
            p = os.path.join(RUNS, unit + "." + k)
            try:
                with open(p, "rb") as f:
                    summary[k] = f.read()[-20000:].decode("utf-8", "replace")
                os.unlink(p)
            except OSError:
                summary[k] = ""
        c1, c2 = transfer(epw.pw_uid, epw.pw_gid, os.path.join(rundir, "out"), caller, cpw.pw_gid, dst, MAX_OUT_BYTES, MAX_OUT_FILES)
        summary["output_transfer"] = {"as_promexec": c1, "as_caller": c2}
        summary["ok"] = summary["result"] == "success" and c1 == 0 and c2 == 0
    finally:
        shutil.rmtree(rundir, ignore_errors=True)
    print(json.dumps(summary))
    sys.exit(0 if summary["ok"] else 1)


if __name__ == "__main__":
    main()
