"""P5: EISPACK vs LAPACK -- the symmetric eigenproblem as a measured coordinate (batch 11).

THIS FILE IS THE PREREGISTRATION. It is committed before it is run.

Batch 10 measured the LU pair (LINPACK vs LAPACK) by counting BLAS calls with ld --wrap. That
instrument CANNOT be reused here, and the reason is itself a finding: EISPACK's tred2/tql2 make NO
BLAS CALLS AT ALL. They are hand-written Fortran loops. Counting BLAS traffic would give EISPACK a
denominator of zero -- not a low score, an undefined one. A coordinate that cannot even be
evaluated on one arm is not a comparison.

So the coordinate moves down a level, to the thing the LAPACK Users' Guide actually claims:
CACHE BEHAVIOUR. cachegrind counts data references and D1/LL data misses for any binary, without
touching a line of either preserved body.

    COORDINATE:  D1 data-miss rate = (D1mr + D1mw) / (Dr + Dw)
                 LL data-miss rate = (DLmr + DLmw) / (Dr + Dw)

PREREGISTERED SIZES: n in {32, 64, 128, 256}. Smaller than the LU pair's because cachegrind costs
~50x runtime. Derived mechanically as powers of two; not adjusted after seeing results.

TASK: all eigenvalues of the SAME real symmetric second-difference matrix
      A(i,i)=2, A(i,i+1)=A(i+1,i)=-1, whose spectrum is known in closed form:
      lambda_k = 2 - 2*cos(k*pi/(n+1)).
ORACLE: both arms must match that closed form to 1e-9. If they do not, no organisational claim may
be made from the run.

ARMS:  EISPACK  rs(matz=0) -> tred1 + tql1   (preserved body, compiled as-is)
       LAPACK   dsyev('N') -> dsytrd + ...   (preserved body, built by its own cmake)

PREREGISTERED PREDICTIONS:
  E-1 both arms match the closed-form spectrum at every n                     (validity gate)
  E-2 LAPACK's D1 data-miss RATE is lower than EISPACK's at the largest n
  E-3 the gap between them widens as n grows
  E-4 EISPACK issues zero Level-3 BLAS calls -- trivially true, it issues none at all; recorded so
      the LU pair's coordinate is explicitly shown to be inapplicable rather than silently dropped

FALSIFICATION: if LAPACK's miss rate is equal or higher at every n, the documented supersession
pressure is NOT reproduced on this task in this environment, and that is the result. Sizes will not
be enlarged and the coordinate will not be swapped to find a difference.

CONFOUND RECORDED IN ADVANCE: valgrind is not in the fossil image, so the MEASUREMENT container
installs it from the network. The measurement world therefore floats. The two FOSSIL BODIES are
untouched and are compiled with identical flags; the floating part is the instrument, not the
specimens.

    python -m techne.fossils.pressure.run_supersession_eigen
"""
import json, pathlib, re, subprocess, time

HERE = pathlib.Path(__file__).resolve().parent
VAULT = "/mnt/f/Prometheus/vault/fossils"
DATE = "2026-09-13"
SIZES = [32, 64, 128, 256]

DRIVER_EIS = r'''
      program eig
      integer NM
      parameter (NM=256)
      double precision a(NM,NM), w(NM), fv1(NM), fv2(NM), z(NM,NM)
      integer n, i, j, ierr
      character*16 arg
      call getarg(1, arg)
      read(arg,*) n
      do 20 j = 1, n
         do 10 i = 1, n
            a(i,j) = 0.0d0
   10    continue
   20 continue
      do 30 i = 1, n
         a(i,i) = 2.0d0
         if (i .lt. n) a(i,i+1) = -1.0d0
         if (i .gt. 1) a(i,i-1) = -1.0d0
   30 continue
      call rs(NM, n, a, w, 0, z, fv1, fv2, ierr)
      write(6,'(A,I6)') 'IERR ', ierr
      write(6,'(A,E22.14)') 'W1 ', w(1)
      write(6,'(A,E22.14)') 'WN ', w(n)
      end
'''

DRIVER_LAP = r'''
      program eig
      integer NM
      parameter (NM=256)
      double precision a(NM,NM), w(NM), work(64*NM)
      integer n, i, j, info, lwork
      character*16 arg
      call getarg(1, arg)
      read(arg,*) n
      do 20 j = 1, n
         do 10 i = 1, n
            a(i,j) = 0.0d0
   10    continue
   20 continue
      do 30 i = 1, n
         a(i,i) = 2.0d0
         if (i .lt. n) a(i,i+1) = -1.0d0
         if (i .gt. 1) a(i,i-1) = -1.0d0
   30 continue
      lwork = 64*NM
      call dsyev('N', 'U', n, a, NM, w, work, lwork, info)
      write(6,'(A,I6)') 'IERR ', info
      write(6,'(A,E22.14)') 'W1 ', w(1)
      write(6,'(A,E22.14)') 'WN ', w(n)
      end
'''

SCRIPT = r'''
set -e
apt-get -qq update >/dev/null 2>&1
apt-get -qq install -y valgrind >/dev/null 2>&1 || { echo VALGRIND_UNAVAILABLE; exit 0; }
valgrind --version

mkdir -p /tmp/x && cd /tmp/x
cat > deis.f <<'FEOF'
__DEIS__
FEOF
cat > dlap.f <<'FEOF'
__DLAP__
FEOF

cp /vault/eispack-netlib-1976/upstream/*.f /tmp/x/
gfortran -std=legacy -w -O2 -o eis deis.f rs.f tred1.f tql1.f tred2.f tql2.f tqlrat.f pythag.f epslon.f
echo BUILT_EISPACK

mkdir -p /tmp/la && cp -r /vault/lapack-reference/upstream/tree/. /tmp/la/
mkdir -p /tmp/la/b && cd /tmp/la/b
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF -DBUILD_SHARED_LIBS=OFF .. >/tmp/c.log 2>&1
make -j4 blas lapack >/tmp/m.log 2>&1
cd /tmp/x
gfortran -std=legacy -w -O2 -o lap dlap.f -L/tmp/la/b/lib -llapack -lblas
echo BUILT_LAPACK

for N in __SIZES__; do
  for ARM in eis lap; do
    echo "=== ARM $ARM N=$N"
    valgrind --tool=cachegrind --cache-sim=yes --cachegrind-out-file=/tmp/cg.out ./$ARM $N 2>/tmp/cg.err
    sed -n 's/^==[0-9]*== //p' /tmp/cg.err | grep -E 'refs:|misses:'
  done
done
'''


def _q(s):
    return "'" + s.replace("'", "'\\''") + "'"


def _num(s):
    return int(re.sub(r"[^0-9]", "", s)) if re.search(r"\d", s) else 0


def parse(out):
    arms, cur = [], None
    for line in out.splitlines():
        t = line.strip()
        if t.startswith("=== ARM "):
            p = t.split()
            cur = {"arm": {"eis": "eispack", "lap": "lapack"}[p[2]], "n": int(p[3].split("=")[1]),
                   "ierr": None, "w1": None, "wn": None, "I_refs": 0, "D_refs": 0, "D1_misses": 0, "LLd_misses": 0}
            arms.append(cur)
        elif cur is None:
            continue
        elif t.startswith("IERR "):
            cur["ierr"] = int(t.split()[1])
        elif t.startswith("W1 "):
            cur["w1"] = float(t.split()[1])
        elif t.startswith("WN "):
            cur["wn"] = float(t.split()[1])
        else:
            # cachegrind pads its labels ("D   refs:", "D1  misses:"), so match on a regex rather
            # than a literal prefix. The first pass missed the DENOMINATOR for exactly this reason
            # and produced an undefined rate while the misses parsed fine.
            m = re.match(r"^(I\s+refs|D\s+refs|D1\s+misses|LLd\s+misses|LL\s+misses):\s*(.+)$", t)
            if m:
                key = re.sub(r"\s+", "_", m.group(1))
                val = _num(m.group(2).split("(")[0])
                {"I_refs": "I_refs", "D_refs": "D_refs", "D1_misses": "D1_misses",
                 "LLd_misses": "LLd_misses", "LL_misses": "LLd_misses"}.get(key)
                if key == "I_refs":
                    cur["I_refs"] = val
                elif key == "D_refs":
                    cur["D_refs"] = val
                elif key == "D1_misses":
                    cur["D1_misses"] = val
                elif key in ("LLd_misses", "LL_misses"):
                    cur["LLd_misses"] = val
    import math
    for a in arms:
        n = a["n"]
        a["expected_w1"] = 2 - 2 * math.cos(1 * math.pi / (n + 1))
        a["expected_wn"] = 2 - 2 * math.cos(n * math.pi / (n + 1))
        a["oracle_ok"] = (a["w1"] is not None and a["wn"] is not None
                          and abs(a["w1"] - a["expected_w1"]) < 1e-9
                          and abs(a["wn"] - a["expected_wn"]) < 1e-9)
        a["D1_miss_rate"] = a["D1_misses"] / a["D_refs"] if a["D_refs"] else None
        a["LL_miss_rate"] = a["LLd_misses"] / a["D_refs"] if a["D_refs"] else None
    return arms


def main():
    script = (SCRIPT.replace("__DEIS__", DRIVER_EIS).replace("__DLAP__", DRIVER_LAP)
              .replace("__SIZES__", " ".join(str(n) for n in SIZES)))
    r = subprocess.run(["wsl.exe", "-e", "bash", "-lc",
        "docker run --rm -v %s:/vault:ro prometheus-fossil-c:bookworm bash -lc %s" % (VAULT, _q(script))],
        capture_output=True, text=True, timeout=7200)
    arms = parse(r.stdout)
    doc = {"schema": "techne.fossil.supersession_eigen/1",
           "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "prereg": "this module, committed before it was run",
           "pair": ["eispack-netlib-1976", "lapack-reference"],
           "preregistered_sizes": SIZES,
           "coordinate": "D1 data-miss rate = (D1mr+D1mw)/(Dr+Dw), measured by cachegrind",
           "why_not_the_LU_coordinate": "EISPACK's tred2/tql2 make NO BLAS calls at all, so the "
                                        "LINPACK/LAPACK Level-3-fraction coordinate has an undefined "
                                        "denominator on this arm. Recorded, not silently dropped.",
           "confound": "valgrind is installed from the network into the MEASUREMENT container; that "
                       "world floats. Both fossil bodies are untouched and compiled with identical flags.",
           "arms": arms}
    op = HERE / ("SUPERSESSION_EIGEN_%s.json" % DATE)
    op.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("%-9s %-5s %-14s %-14s %-11s %s" % ("arm", "n", "D_refs", "D1_misses", "D1_rate", "oracle"))
    for a in arms:
        print("%-9s %-5d %-14d %-14d %-11s %s" % (
            a["arm"], a["n"], a["D_refs"], a["D1_misses"],
            ("%.6f" % a["D1_miss_rate"]) if a["D1_miss_rate"] is not None else "-", a["oracle_ok"]))
    if not arms:
        print("NO ARMS PARSED. stdout tail:\n", r.stdout[-1500:], "\nstderr tail:\n", r.stderr[-800:])
    print("wrote", op)


if __name__ == "__main__":
    main()
