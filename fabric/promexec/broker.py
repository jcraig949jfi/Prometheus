#!/usr/bin/python3 -I
"""promexec-run -- the root-owned execution broker (installed as /usr/local/sbin/promexec-run, root:root 0755).

EXPERIMENTAL / UNVERIFIED / NOT ENABLED FOR FABRIC WORKERS -- see fabric/promexec/STATUS_EXPERIMENTAL.md.
Operator ruling 2026-09-28: "Claude may propose code; only promexec executes it."

    sudo -n /usr/local/sbin/promexec-run --run-id ID --in STAGING_DIR --out RESULT_DIR
         [--wall-s N] [--mem-mb M] [--cpu-pct P] [--tasks T]

Round 2 (repairs for Aether round 1, roles/Aether/reviews/2026-09-28_promexec_round1/FINDINGS.md):
- B1 argv: the command line carries only an opaque run id, two absolute paths and integer limits. Nothing may
  follow "--" (refused). The entry point is the fixed file main.py in STAGING_DIR; script arguments travel in the
  file .promexec_args.json beside it ($PROMEXEC_ARGS). Unknown, unpaired or repeated options are refused (M19).
- B3 shared UID: every run gets its own transient UID (DynamicUser=yes). With ProtectProc=invisible a run cannot
  see another run's processes, and TemporaryFileSystem= hides the global runs directory; only this run's in/
  (read-only), out/ and work/ are bind-mounted into its namespace.
- B2 /tmp: PrivateTmp=yes (implied by DynamicUser, set explicitly) and TMPDIR inside the run's own work/.
- B4 systemd: NoNewPrivileges, RestrictSUIDSGID, ProtectSystem=strict, ProtectHome=yes, PrivateDevices,
  ProtectProc=invisible + ProcSubset=pid (M13), PrivateNetwork + IPAddressDeny=any (round-1 gap A: network),
  plus the memory / CPU / tasks / runtime bounds. NoNewPrivileges also closes round-1 gap B (setgid crontab).
- Finding 5 (root chown through a symlink): the run directory is root-owned for its whole life, so no
  unprivileged process can plant anything in it; root only creates fresh subdirectories there with mkdir.
  Ownership is set only on paths root has just created (the run directory's group, and in/'s owner via lchown),
  before any unprivileged process can reach them; out/ and work/ are never chowned.

Flow:
1. INPUT: the regular files in STAGING_DIR are read AS THE CALLER (SUDO_UID), so root never reads a path the caller
   could not. No symlinks, devices or special files; size and count caps. They are streamed as a tar and extracted
   AS the static account promexec (an inert file-owner identity: it never runs submitted code) into rundir/in.
2. RUN: /opt/promexec/py/bin/python -I -B main.py in a transient system unit under a dynamic UID, with the
   properties above, a clean environment and the declared bounds.
3. OUTPUT: after the unit has exited (so no process of its UID remains), the regular files under out/ are read
   AS promexec and extracted AS THE CALLER into RESULT_DIR. Symlinks and special files are skipped.
4. The run directory is removed. The broker prints one JSON summary line.
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
VIEW = "/var/lib/promexec"            # inside the unit: a tmpfs, with only this run's in/ out/ work/ bound in
PY = "/opt/promexec/py/bin/python"
XFER_USER = "promexec"               # static, inert: owns transferred files; never executes submitted code
ENTRY, ARGS_FILE = "main.py", ".promexec_args.json"
MAX_IN_BYTES, MAX_IN_FILES = 256 * 2**20, 2000
MAX_OUT_BYTES, MAX_OUT_FILES = 64 * 2**20, 500
LIMITS = {"wall_s": (1, 3600), "mem_mb": (64, 4096), "cpu_pct": (10, 400), "tasks": (4, 256)}
DEFAULTS = {"wall_s": 600}
OPTIONS = ("--run-id", "--in", "--out") + tuple("--" + k.replace("_", "-") for k in LIMITS)
# Isolation beyond resource bounds. Each line names the blocker or finding it answers.
HARDENING = [
    "DynamicUser=yes",                 # B3: a distinct transient UID per run (implies NoNewPrivileges, RestrictSUIDSGID)
    "NoNewPrivileges=yes",             # B4; also closes gap B (setgid crontab) and M8 (sudo)
    "RestrictSUIDSGID=yes",            # B4
    "ProtectSystem=strict",            # B4, M10: the whole file system read-only
    "ProtectHome=yes",                 # B4, M4-M6, M9: /home, /root, /run/user inaccessible
    "PrivateDevices=yes",              # B4
    "PrivateTmp=yes",                  # B2, M12
    "UMask=0022",                      # Aether round-2 source N2: outputs stay readable by the transfer identity
    "ProtectProc=invisible",           # B3/M11, M13: other UIDs' processes hidden in /proc
    "ProcSubset=pid",                  # M13
    "PrivateNetwork=yes",              # round-1 gap A: no network
    "IPAddressDeny=any",               # round-1 gap A, belt and braces
    "TemporaryFileSystem=%s:ro" % VIEW,  # B3: the global runs directory is not visible
]


def die(msg, code=2):
    print(json.dumps({"ok": False, "refused": msg}))
    sys.exit(code)


def parse_args(argv):
    """Strict: known options only, each exactly once with a value; nothing after "--". Raises ValueError."""
    if "--" in argv:
        raise ValueError("script arguments are not accepted on the command line (B1); use %s" % ARGS_FILE)
    if len(argv) % 2:
        raise ValueError("unpaired option")
    opts = {}
    for k, v in zip(argv[0::2], argv[1::2]):
        if k not in OPTIONS:
            raise ValueError("unknown option %r" % k[:40])
        if k in opts:
            raise ValueError("repeated option %s" % k)
        opts[k] = v
    run_id = opts.get("--run-id", "")
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", run_id):
        raise ValueError("bad run id")
    src, dst = opts.get("--in", ""), opts.get("--out", "")
    if not (os.path.isabs(src) and os.path.isabs(dst)):
        raise ValueError("--in and --out must be absolute")
    lim = {}
    for k, (lo, hi) in LIMITS.items():
        raw = opts.get("--" + k.replace("_", "-"), str(DEFAULTS.get(k, lo)))
        if not re.fullmatch(r"[0-9]{1,6}", raw):
            raise ValueError("--%s must be a small integer" % k.replace("_", "-"))
        lim[k] = max(lo, min(hi, int(raw)))
    return run_id, src, dst, lim


def unit_properties(rundir, lim):
    """The complete property list for one run. rundir is host-side; the unit sees it only through the binds."""
    return HARDENING + [
        "BindReadOnlyPaths=%s:%s/in" % (os.path.join(rundir, "in"), VIEW),
        "BindPaths=%s:%s/out %s:%s/work" % (os.path.join(rundir, "out"), VIEW, os.path.join(rundir, "work"), VIEW),
        "WorkingDirectory=%s/work" % VIEW,
        "MemoryMax=%dM" % lim["mem_mb"], "MemorySwapMax=0", "CPUQuota=%d%%" % lim["cpu_pct"],
        "TasksMax=%d" % lim["tasks"], "RuntimeMaxSec=%d" % lim["wall_s"],
        "StandardOutput=truncate:%s" % os.path.join(rundir, "stdout"),
        "StandardError=truncate:%s" % os.path.join(rundir, "stderr"),
        "Environment=HOME={v}/work TMPDIR={v}/work/tmp LANG=C.UTF-8 PROMEXEC_IN={v}/in PROMEXEC_OUT={v}/out "
        "PROMEXEC_ARGS={v}/in/{a} MPLBACKEND=Agg OMP_NUM_THREADS=2".format(v=VIEW, a=ARGS_FILE),
    ]


def drop_to(uid, gid):
    os.setgroups([])
    os.setgid(gid)
    os.setuid(uid)


def stream_tar_as(uid, gid, root, max_bytes, max_files):
    """Fork: as uid, tar the regular files under root (no symlinks) to a pipe. Returns the read end, the pid and a
    stats fd: on exit the child writes {"files": n, "skipped": k} to it (N2: nothing is skipped silently)."""
    r, w = os.pipe()
    sr, sw = os.pipe()
    pid = os.fork()
    if pid == 0:
        skipped = [0]

        def stats(n):
            try:
                os.write(sw, json.dumps({"files": n, "skipped": skipped[0]}).encode())
            except OSError:
                pass
        n = 0
        try:
            os.close(r); os.close(sr)
            drop_to(uid, gid)
            total = 0
            with os.fdopen(w, "wb") as f, tarfile.open(fileobj=f, mode="w|") as t:
                for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
                    dirnames[:] = [d for d in dirnames if not os.path.islink(os.path.join(dirpath, d))]
                    for fn in filenames:
                        p = os.path.join(dirpath, fn)
                        try:
                            fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
                        except OSError:
                            skipped[0] += 1                                   # symlink, unreadable: skipped
                            continue
                        st = os.fstat(fd)
                        if not (st.st_mode & 0o170000 == 0o100000):          # regular files only
                            os.close(fd); skipped[0] += 1
                            continue
                        n += 1; total += st.st_size
                        if n > max_files or total > max_bytes:
                            stats(n); os._exit(3)
                        ti = tarfile.TarInfo(os.path.relpath(p, root)); ti.size = st.st_size; ti.mode = 0o644; ti.mtime = int(st.st_mtime)  # DEF-ODY-001
                        with os.fdopen(fd, "rb") as fh:
                            t.addfile(ti, fh)
            stats(n); os._exit(0)
        except Exception:
            stats(n); os._exit(4)
    os.close(w); os.close(sw)
    return r, pid, sr


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
    r, p1, sr = stream_tar_as(src_uid, src_gid, src, max_bytes, max_files)
    p2 = extract_as(dst_uid, dst_gid, r, dst)
    s1 = os.waitpid(p1, 0)[1]; s2 = os.waitpid(p2, 0)[1]
    with os.fdopen(sr, "rb") as f:
        raw = f.read()
    try:
        counts = json.loads(raw)
    except ValueError:
        counts = {"files": None, "skipped": None}
    return os.waitstatus_to_exitcode(s1), os.waitstatus_to_exitcode(s2), counts


def make_rundir(run_id, xfer_gid):
    """root:promexec 0710 for its whole life. Subdirectories are fresh mkdirs by root; nothing is chowned later."""
    old = os.umask(0)
    try:
        rundir = os.path.join(RUNS, run_id + "-" + os.urandom(8).hex())
        os.mkdir(rundir, 0o710)
        os.chown(rundir, 0, xfer_gid)                  # set before any unprivileged process can know the name
        os.mkdir(os.path.join(rundir, "in"), 0o755)    # promexec extracts inputs here (owner set below, fresh dir)
        for d in ("out", "work"):
            os.mkdir(os.path.join(rundir, d), 0o777)   # reachable only through this unit's bind mounts
        os.mkdir(os.path.join(rundir, "work", "tmp"), 0o777)
    finally:
        os.umask(old)
    return rundir


def main():
    if os.geteuid() != 0:
        die("must run via sudo")
    try:
        run_id, src, dst, lim = parse_args(sys.argv[1:])
    except ValueError as e:
        die(str(e))
    caller = int(os.environ.get("SUDO_UID", "-1"))
    if caller <= 0:
        die("no non-root SUDO_UID")
    cpw = pwd.getpwuid(caller); xpw = pwd.getpwnam(XFER_USER)
    rundir = make_rundir(run_id, xpw.pw_gid)
    # in/ belongs to the transfer identity. It was created a moment ago by root inside a root-owned 0710
    # directory, so the path cannot have been replaced; lchown does not follow a link in any case.
    os.lchown(os.path.join(rundir, "in"), xpw.pw_uid, xpw.pw_gid)
    summary = {"ok": False, "run_dir": rundir, "limits": lim, "hardening": HARDENING}
    try:
        c1, c2, summary["input_counts"] = transfer(caller, cpw.pw_gid, src, xpw.pw_uid, xpw.pw_gid,
                                                   os.path.join(rundir, "in"), MAX_IN_BYTES, MAX_IN_FILES)
        if c1 or c2:
            die("input transfer failed (as caller: %s, as promexec: %s)" % (c1, c2))
        if not os.path.isfile(os.path.join(rundir, "in", ENTRY)):
            die("the staging directory has no %s" % ENTRY)
        unit = "promexec-" + re.sub(r"[^A-Za-z0-9]", "", run_id)[:40] + "-" + os.urandom(4).hex()
        cmd = ["systemd-run", "--unit=" + unit, "--wait", "--collect", "--service-type=exec"]
        for p in unit_properties(rundir, lim):
            cmd += ["-p", p]
        cmd += ["--", PY, "-I", "-B", VIEW + "/in/" + ENTRY]
        t0 = time.time()
        r = subprocess.run(cmd, capture_output=True, text=True, env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"})
        summary["wall_s_used"] = round(time.time() - t0, 2)
        summary["unit"] = unit
        m = re.search(r"Finished with result: (\S+)", r.stderr)
        summary["result"] = m.group(1) if m else ("success" if r.returncode == 0 else "unknown")
        m = re.search(r"status=(\d+)", r.stderr)
        summary["exit_code"] = int(m.group(1)) if m else r.returncode
        if not m and r.returncode != 0:
            summary["systemd_run_stderr"] = r.stderr[-2000:]
        for k in ("stdout", "stderr"):
            try:
                fd = os.open(os.path.join(rundir, k), os.O_RDONLY | os.O_NOFOLLOW)
                with os.fdopen(fd, "rb") as f:
                    f.seek(max(0, os.fstat(f.fileno()).st_size - 20000))
                    summary[k] = f.read().decode("utf-8", "replace")
            except OSError:
                summary[k] = ""
        c1, c2, summary["output_counts"] = transfer(xpw.pw_uid, xpw.pw_gid, os.path.join(rundir, "out"), caller, cpw.pw_gid, dst,
                          MAX_OUT_BYTES, MAX_OUT_FILES)
        summary["output_transfer"] = {"as_promexec": c1, "as_caller": c2}
        summary["ok"] = summary["result"] == "success" and c1 == 0 and c2 == 0
    finally:
        shutil.rmtree(rundir, ignore_errors=True)
    print(json.dumps(summary))
    sys.exit(0 if summary["ok"] else 1)


if __name__ == "__main__":
    main()
