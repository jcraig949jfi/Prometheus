"""Batch 06 phase 8: run the preserved SAT solvers and compression codecs over shared pressure
workloads and record raw behaviour. Techne constructs the inputs and records what each fossil does;
it does NOT rank them, cluster them, or name a winner. Drives the vault's docker worlds via wsl.

    python run_pressure.py sat   -> SAT_PRESSURE_<date>.json
    python run_pressure.py comp  -> COMPRESSION_PRESSURE_<date>.json

Each solver runs in the world its own recipe uses (picosat: lang-equivalent C world; minisat-2.2.0:
the preserved gcc:4.9). Each codec compresses and round-trips several payloads. Timing is host-side
wall clock around the docker invocation (coarse; the behavioural counters are the point).
"""
import json, pathlib, subprocess, sys, time, re

HERE = pathlib.Path(__file__).resolve().parent
VAULT = "/mnt/f/Prometheus/vault/fossils"
PHERE = "/mnt/f/Prometheus-worktrees/techne-pass-0912/techne/fossils/pressure"
DATE = "2026-09-13"


def wsl(script):
    return subprocess.run(["wsl.exe", "-e", "bash", "-lc", script], capture_output=True, text=True, timeout=1800).stdout


def docker(image, script, mounts=""):
    return wsl("docker run --rm %s -v %s:/vault:ro -v %s:/p %s bash -lc %s" % (
        mounts, VAULT, PHERE, image, _q(script)))


def _q(s):
    return "'" + s.replace("'", "'\\''") + "'"


SAT_PICOSAT = r'''
cp -r /vault/picosat-965/upstream/tree/picosat-965 /tmp/ps && cd /tmp/ps && ./configure.sh >/dev/null 2>&1 && make -s >/dev/null 2>&1
for cnf in /p/workload_sat/*.cnf; do
  out=$(timeout 60 /tmp/ps/picosat -v "$cnf" 2>&1); rc=$?
  res=$(echo "$out" | grep -oE 'SATISFIABLE|UNSATISFIABLE' | head -1); [ $rc -eq 124 ] && res=TIMEOUT
  dec=$(echo "$out" | grep -oE '[0-9]+ decisions' | grep -oE '^[0-9]+'); prop=$(echo "$out" | grep -oE '[0-9]+ propagations' | grep -oE '^[0-9]+')
  echo "PICO $(basename $cnf) ${res:-UNKNOWN} ${dec:-NA} ${prop:-NA}"
done
'''
SAT_MINISAT = r'''
cp -r /vault/minisat-2.2.0/upstream/tree/minisat /tmp/ms && cd /tmp/ms/core && MROOT=/tmp/ms make -s r >/dev/null 2>&1
for cnf in /p/workload_sat/*.cnf; do
  out=$(timeout 60 /tmp/ms/core/minisat_release "$cnf" /dev/null 2>&1); rc=$?
  res=$(echo "$out" | grep -oE 'SATISFIABLE|UNSATISFIABLE|INDETERMINATE' | head -1); [ $rc -eq 124 ] && res=TIMEOUT
  con=$(echo "$out" | grep -iE '^conflicts' | grep -oE '[0-9]+' | head -1); dec=$(echo "$out" | grep -iE '^decisions' | grep -oE '[0-9]+' | head -1)
  echo "MINI $(basename $cnf) ${res:-UNKNOWN} ${con:-NA} ${dec:-NA}"
done
'''


def run_sat():
    rows = []
    for solver, image, script, cols in (
        ("picosat-965", "prometheus-fossil-c:bookworm", SAT_PICOSAT, ("decisions", "propagations")),
        ("minisat-2.2.0", "gcc:4.9", SAT_MINISAT, ("conflicts", "decisions")),
    ):
        t0 = time.time(); out = docker(image, script); dt = time.time() - t0
        n = 0
        for line in out.splitlines():
            p = line.split()
            if p and p[0] in ("PICO", "MINI"):
                rows.append({"solver": solver, "instance": p[1], "result": p[2],
                             cols[0]: None if p[3] == "NA" else int(p[3]),
                             cols[1]: None if p[4] == "NA" else int(p[4])})
                n += 1
        print("%s: %d instances in %.0fs wall (build+run)" % (solver, n, dt))
    doc = {"schema": "techne.fossil.sat_pressure/1", "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "workload": "techne/fossils/pressure/workload_sat (gen_sat_workload.py, deterministic)",
           "note": "raw behaviour of preserved SAT solvers over one shared workload; NOT a ranking. minisat-2.2.0 exposes conflicts/decisions, picosat-965 decisions/propagations; walksat (stochastic) cannot prove UNSAT and is recorded separately when run.",
           "solvers": ["picosat-965", "minisat-2.2.0"], "rows": rows}
    out_path = HERE / ("SAT_PRESSURE_%s.json" % DATE)
    out_path.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("wrote", out_path, len(rows), "rows")


COMP = r'''
apt-get -qq update >/dev/null 2>&1; apt-get -qq install -y gzip bzip2 >/dev/null 2>&1
mkdir -p /tmp/pay
python3 - <<'PY'
import os
os.makedirs('/tmp/pay', exist_ok=True)
open('/tmp/pay/text','wb').write((("the quick brown fox %d jumps over the lazy dog %d\n" % (i,i*7)).encode() for i in range(6000)).__iter__() and b''.join(("the quick brown fox %d jumps over the lazy dog %d\n" % (i,i*7)).encode() for i in range(6000)))
import random; random.seed(1)
open('/tmp/pay/random','wb').write(bytes(random.randrange(256) for _ in range(300000)))
open('/tmp/pay/repeat','wb').write(b'ABCD'*75000)
open('/tmp/pay/zeros','wb').write(b'\x00'*300000)
PY
run() { # name file cmd_compress ext cmd_decompress
  nm=$1; f=$2; ext=$4; cp "$f" /tmp/c.in
  osz=$(stat -c%s /tmp/c.in)
  eval "$3" ; csz=$(stat -c%s /tmp/c.in$ext 2>/dev/null || echo NA)
  eval "$5" ; ok=$(cmp -s /tmp/c.rt /tmp/c.in && echo yes || echo no)
  echo "$nm $(basename $f) $osz $csz $ok"
}
'''


def run_comp():
    # each codec: compress each payload, record original/compressed size and round-trip integrity
    codecs = {
      "gzip-1.2.4": r'''cp -r /vault/gzip-1.2.4-1993/upstream/tree/gzip-1.2.4 /tmp/g && cd /tmp/g && ./configure >/dev/null 2>&1 && make -s CFLAGS='-O1 -fcommon -std=gnu89 -w' >/dev/null 2>&1; G=/tmp/g/gzip
for f in /tmp/pay/*; do o=$(stat -c%s $f); $G -c -9 <$f >/tmp/o.gz 2>/dev/null; c=$(stat -c%s /tmp/o.gz); $G -dc /tmp/o.gz >/tmp/rt 2>/dev/null; cmp -s /tmp/rt $f && ok=yes || ok=no; echo "gzip-1.2.4 $(basename $f) $o $c $ok"; done''',
      "zlib-1.3.1": r'''cp -r /vault/zlib-1.3.1/upstream/tree/zlib-1.3.1 /tmp/z && cd /tmp/z && ./configure >/dev/null 2>&1 && make -s minigzip >/dev/null 2>&1; Z=/tmp/z/minigzip
for f in /tmp/pay/*; do o=$(stat -c%s $f); $Z -9 <$f >/tmp/o.gz 2>/dev/null; c=$(stat -c%s /tmp/o.gz); $Z -d </tmp/o.gz >/tmp/rt 2>/dev/null; cmp -s /tmp/rt $f && ok=yes || ok=no; echo "zlib-1.3.1 $(basename $f) $o $c $ok"; done''',
      "bzip2-1.0.8": r'''cp -r /vault/bzip2-1.0.8/upstream/tree/bzip2-1.0.8 /tmp/b && cd /tmp/b && make -s bzip2 >/dev/null 2>&1; B=/tmp/b/bzip2
for f in /tmp/pay/*; do o=$(stat -c%s $f); $B -c -9 <$f >/tmp/o.bz2 2>/dev/null; c=$(stat -c%s /tmp/o.bz2); $B -dc /tmp/o.bz2 >/tmp/rt 2>/dev/null; cmp -s /tmp/rt $f && ok=yes || ok=no; echo "bzip2-1.0.8 $(basename $f) $o $c $ok"; done''',
      "ncompress-5.0": r'''cp -r /vault/ncompress-5.0-lzw-1985/upstream/tree/ncompress-5.0 /tmp/n && cd /tmp/n && (make -s compress >/dev/null 2>&1 || make -s >/dev/null 2>&1); N=$(find /tmp/n -maxdepth 1 -name compress -type f | head -1)
for f in /tmp/pay/*; do o=$(stat -c%s $f); $N -c <$f >/tmp/o.Z 2>/dev/null; c=$(stat -c%s /tmp/o.Z); $N -dc /tmp/o.Z >/tmp/rt 2>/dev/null; cmp -s /tmp/rt $f && ok=yes || ok=no; echo "ncompress-5.0 $(basename $f) $o $c $ok"; done''',
    }
    payloads = r'''apt-get -qq update >/dev/null 2>&1; apt-get -qq install -y python3 >/dev/null 2>&1
mkdir -p /tmp/pay
python3 - <<'PY'
import random
with open('/tmp/pay/text','wb') as f:
    f.write(b''.join(("the quick brown fox %d jumps over the lazy dog %d\n" % (i,i*7)).encode() for i in range(6000)))
random.seed(1)
open('/tmp/pay/random','wb').write(bytes(random.randrange(256) for _ in range(300000)))
open('/tmp/pay/repeat','wb').write(b'ABCD'*75000)
open('/tmp/pay/zeros','wb').write(b'\x00'*300000)
PY
'''
    rows = []
    for name, script in codecs.items():
        out = docker("prometheus-fossil-c:bookworm", payloads + "\n" + script)
        for line in out.splitlines():
            p = line.split()
            if len(p) == 5 and p[0] == name:
                o, c = int(p[2]), (None if p[3] == "NA" else int(p[3]))
                rows.append({"codec": name, "payload": p[1], "original_bytes": o, "compressed_bytes": c,
                             "ratio": (round(c / o, 4) if c else None), "round_trip_ok": p[4] == "yes"})
        print("%s: %d payloads" % (name, sum(1 for r in rows if r["codec"] == name)))
    doc = {"schema": "techne.fossil.compression_pressure/1", "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "payloads": "text (compressible), random (incompressible), repeat (ABCD x 75000), zeros -- 300 KB each except text",
           "note": "raw behaviour of preserved codecs over one shared payload set; ratio = compressed/original; round_trip_ok is cmp of decompress(compress(x)) vs x. NOT a ranking.",
           "codecs": list(codecs), "rows": rows}
    out_path = HERE / ("COMPRESSION_PRESSURE_%s.json" % DATE)
    out_path.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("wrote", out_path, len(rows), "rows")


if __name__ == "__main__":
    {"sat": run_sat, "comp": run_comp}[sys.argv[1]]()
