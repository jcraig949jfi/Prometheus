"""Batch 10 P4: turn a DOCUMENTED supersession into a measured behavioural coordinate.

PREREG: techne/fossils/PREREG_SUPERSESSION_BEHAVIOR_2026-09-13.md (filed before LAPACK was built)

The LAPACK Users' Guide claims LINPACK/EISPACK were superseded because their Level-1 BLAS
organisation reuses cached data poorly, not because their mathematics was wrong. So the coordinate
is LEVEL3_FRACTION: the share of matrix element-references a factorisation issues through Level-3
(matrix-matrix) BLAS. It is machine-independent, deterministic, and cannot be improved by tuning a
timer -- unlike the wall-clock number the charter explicitly refused.

NEITHER PRESERVED BODY IS MODIFIED. Counting is done with ld --wrap, which redirects each
undefined BLAS reference to a __wrap_ shim at LINK time; the shim tallies the call and forwards to
__real_. The fossils' own sources are compiled exactly as preserved.

    python run_supersession_behavior.py -> SUPERSESSION_BEHAVIOR_<date>.json
"""
import json, pathlib, subprocess, time

HERE = pathlib.Path(__file__).resolve().parent
VAULT = "/mnt/f/Prometheus/vault/fossils"
DATE = "2026-09-13"
SIZES = [64, 128, 256, 512, 1024]          # PREREGISTERED, powers of two. Not changed after results.

# ------------------------------------------------------------------ the counting shim (C)
SHIM_C = r'''
#include <stdio.h>
#include <string.h>
/* ld --wrap redirects the fossils' BLAS calls here at link time. Nothing in either preserved
   body is edited: we count, then forward to the real routine. */
typedef struct { const char *name; int level; long calls; double refs; } Ent;
static Ent T[] = {
  {"daxpy",1,0,0}, {"dscal",1,0,0}, {"ddot",1,0,0}, {"idamax",1,0,0}, {"dswap",1,0,0},
  {"dger",2,0,0}, {"dgemv",2,0,0}, {"dtrsv",2,0,0},
  {"dgemm",3,0,0}, {"dtrsm",3,0,0}, {"dsyrk",3,0,0}, {"dsyr2k",3,0,0},
};
static Ent *E(const char *n){ for(unsigned i=0;i<sizeof(T)/sizeof(T[0]);i++) if(!strcmp(T[i].name,n)) return &T[i]; return 0; }
static void tally(const char *n, double refs){ Ent *e=E(n); if(e){ e->calls++; e->refs+=refs; } }

void shim_reset_(void){ for(unsigned i=0;i<sizeof(T)/sizeof(T[0]);i++){ T[i].calls=0; T[i].refs=0; } }
void shim_report_(void){
  for(unsigned i=0;i<sizeof(T)/sizeof(T[0]);i++)
    if(T[i].calls) printf("SHIM %s %d %ld %.0f\n", T[i].name, T[i].level, T[i].calls, T[i].refs);
}

/* ---- Level 1 : PREREG formula = n element-references per call ---- */
extern void __real_daxpy_(int*,double*,double*,int*,double*,int*);
void __wrap_daxpy_(int*n,double*a,double*x,int*ix,double*y,int*iy){ tally("daxpy",(double)*n); __real_daxpy_(n,a,x,ix,y,iy); }
extern void __real_dscal_(int*,double*,double*,int*);
void __wrap_dscal_(int*n,double*a,double*x,int*ix){ tally("dscal",(double)*n); __real_dscal_(n,a,x,ix); }
extern double __real_ddot_(int*,double*,int*,double*,int*);
double __wrap_ddot_(int*n,double*x,int*ix,double*y,int*iy){ tally("ddot",(double)*n); return __real_ddot_(n,x,ix,y,iy); }
extern int __real_idamax_(int*,double*,int*);
int __wrap_idamax_(int*n,double*x,int*ix){ tally("idamax",(double)*n); return __real_idamax_(n,x,ix); }
#ifdef FULL_BLAS
extern void __real_dswap_(int*,double*,int*,double*,int*);
void __wrap_dswap_(int*n,double*x,int*ix,double*y,int*iy){ tally("dswap",(double)*n); __real_dswap_(n,x,ix,y,iy); }

/* ---- Level 2 : encountered in the unblocked panel factorisation; m*n + m + n ---- */
extern void __real_dger_(int*,int*,double*,double*,int*,double*,int*,double*,int*);
void __wrap_dger_(int*m,int*n,double*a,double*x,int*ix,double*y,int*iy,double*A,int*lda){
  tally("dger",(double)(*m)*(*n)+(*m)+(*n)); __real_dger_(m,n,a,x,ix,y,iy,A,lda); }
extern void __real_dgemv_(char*,int*,int*,double*,double*,int*,double*,int*,double*,double*,int*,int);
void __wrap_dgemv_(char*t,int*m,int*n,double*al,double*A,int*lda,double*x,int*ix,double*be,double*y,int*iy,int lt){
  tally("dgemv",(double)(*m)*(*n)+(*m)+(*n)); __real_dgemv_(t,m,n,al,A,lda,x,ix,be,y,iy,lt); }
extern void __real_dtrsv_(char*,char*,char*,int*,double*,int*,double*,int*,int,int,int);
void __wrap_dtrsv_(char*u,char*t,char*d,int*n,double*A,int*lda,double*x,int*ix,int lu,int lt,int ld){
  tally("dtrsv",(double)(*n)*(*n)/2.0+(*n)); __real_dtrsv_(u,t,d,n,A,lda,x,ix,lu,lt,ld); }

/* ---- Level 3 : PREREG formulas ---- */
extern void __real_dgemm_(char*,char*,int*,int*,int*,double*,double*,int*,double*,int*,double*,double*,int*,int,int);
void __wrap_dgemm_(char*ta,char*tb,int*m,int*n,int*k,double*al,double*A,int*lda,double*B,int*ldb,double*be,double*C,int*ldc,int la,int lb){
  tally("dgemm",(double)(*m)*(*n)+(double)(*m)*(*k)+(double)(*k)*(*n));
  __real_dgemm_(ta,tb,m,n,k,al,A,lda,B,ldb,be,C,ldc,la,lb); }
extern void __real_dtrsm_(char*,char*,char*,char*,int*,int*,double*,double*,int*,double*,int*,int,int,int,int);
void __wrap_dtrsm_(char*si,char*u,char*t,char*d,int*m,int*n,double*al,double*A,int*lda,double*B,int*ldb,int ls,int lu,int lt,int ld){
  double s = (*si=='L'||*si=='l') ? (double)(*m)*(*m)/2.0 : (double)(*n)*(*n)/2.0;
  tally("dtrsm",(double)(*m)*(*n)+s); __real_dtrsm_(si,u,t,d,m,n,al,A,lda,B,ldb,ls,lu,lt,ld); }
extern void __real_dsyrk_(char*,char*,int*,int*,double*,double*,int*,double*,double*,int*,int,int);
void __wrap_dsyrk_(char*u,char*t,int*n,int*k,double*al,double*A,int*lda,double*be,double*C,int*ldc,int lu,int lt){
  tally("dsyrk",(double)(*n)*(*n)+(double)(*n)*(*k)); __real_dsyrk_(u,t,n,k,al,A,lda,be,C,ldc,lu,lt); }
extern void __real_dsyr2k_(char*,char*,int*,int*,double*,double*,int*,double*,int*,double*,double*,int*,int,int);
void __wrap_dsyr2k_(char*u,char*t,int*n,int*k,double*al,double*A,int*lda,double*B,int*ldb,double*be,double*C,int*ldc,int lu,int lt){
  tally("dsyr2k",(double)(*n)*(*n)+2.0*(*n)*(*k)); __real_dsyr2k_(u,t,n,k,al,A,lda,B,ldb,be,C,ldc,lu,lt); }
#endif
'''

# ------------------------------------------------------------------ shared matrix + drivers
GEN_F = r'''
      subroutine genmat(a, lda, n, b)
c     Deterministic, identical in both arms: A(i,j)=1/(i+j), diagonally dominant by +n.
c     b = A * xexact with xexact = all ones, so the oracle is "recover the all-ones vector".
      integer lda, n, i, j
      double precision a(lda,*), b(*), s
      do 20 j = 1, n
         do 10 i = 1, n
            a(i,j) = 1.0d0 / dble(i + j)
   10    continue
   20 continue
      do 30 i = 1, n
         a(i,i) = a(i,i) + dble(n)
   30 continue
      do 50 i = 1, n
         s = 0.0d0
         do 40 j = 1, n
            s = s + a(i,j)
   40    continue
         b(i) = s
   50 continue
      return
      end
'''

DRV_LINPACK_F = r'''
      program drvlin
      integer NMAX
      parameter (NMAX=1024)
      double precision a(NMAX,NMAX), b(NMAX)
      integer ipvt(NMAX), n, info, i, iarg
      double precision err, t0, t1
      character*16 arg
      call getarg(1, arg)
      read(arg,*) n
      call genmat(a, NMAX, n, b)
      call shim_reset()
      call cpu_time(t0)
      call dgefa(a, NMAX, n, ipvt, info)
      call dgesl(a, NMAX, n, ipvt, b, 0)
      call cpu_time(t1)
      err = 0.0d0
      do 10 i = 1, n
         err = max(err, abs(b(i) - 1.0d0))
   10 continue
      write(6,'(A,I6)')   'N ', n
      write(6,'(A,I6)')   'INFO ', info
      write(6,'(A,E14.6)')'MAXERR ', err
      write(6,'(A,F10.4)')'SECONDS ', t1-t0
      call shim_report()
      end
'''

DRV_LAPACK_F = r'''
      program drvlap
      integer NMAX
      parameter (NMAX=1024)
      double precision a(NMAX,NMAX), b(NMAX)
      integer ipiv(NMAX), n, info, i
      double precision err, t0, t1
      character*16 arg
      call getarg(1, arg)
      read(arg,*) n
      call genmat(a, NMAX, n, b)
      call shim_reset()
      call cpu_time(t0)
      call dgetrf(n, n, a, NMAX, ipiv, info)
      call dgetrs('N', n, 1, a, NMAX, ipiv, b, NMAX, info)
      call cpu_time(t1)
      err = 0.0d0
      do 10 i = 1, n
         err = max(err, abs(b(i) - 1.0d0))
   10 continue
      write(6,'(A,I6)')   'N ', n
      write(6,'(A,I6)')   'INFO ', info
      write(6,'(A,E14.6)')'MAXERR ', err
      write(6,'(A,F10.4)')'SECONDS ', t1-t0
      call shim_report()
      end
'''

# LINPACK's dgefa/dgesl reference only Level-1; wrapping a symbol that is not linked would
# leave __real_ undefined, so each arm wraps exactly what it can resolve.
L1 = ("daxpy", "dscal", "ddot", "idamax")
FULL = L1 + ("dswap", "dger", "dgemv", "dtrsv", "dgemm", "dtrsm", "dsyrk", "dsyr2k")
WRAPS_L1 = ",".join("--wrap=%s_" % r for r in L1)
WRAPS_FULL = ",".join("--wrap=%s_" % r for r in FULL)

SCRIPT = r'''
set -e
mkdir -p /tmp/x && cd /tmp/x
cat > shim.c <<'CEOF'
__SHIM__
CEOF
cat > gen.f <<'FEOF'
__GEN__
FEOF
cat > drvlin.f <<'FEOF'
__DRVLIN__
FEOF
cat > drvlap.f <<'FEOF'
__DRVLAP__
FEOF
gcc -O2 -c shim.c -o shim_l1.o
gcc -O2 -DFULL_BLAS -c shim.c -o shim_full.o

# ---- build reference LAPACK from the preserved body, by its own cmake, in a scratch copy
mkdir -p /tmp/la && cp -r /vault/lapack-reference/upstream/tree/. /tmp/la/
mkdir -p /tmp/la/b && cd /tmp/la/b
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF -DBUILD_SHARED_LIBS=OFF .. >/tmp/c.log 2>&1
make -j6 blas lapack >/tmp/m.log 2>&1
test -f /tmp/la/b/lib/liblapack.a && echo LAPACK_LIB_OK
cd /tmp/x

# ---- arm 1: the LINPACK fossil, compiled exactly as preserved
mkdir -p /tmp/x/lp && cp /vault/linpack-netlib-1979/upstream/*.f /tmp/x/lp/
gfortran -std=legacy -w -O2 -c /tmp/x/lp/dgefa.f /tmp/x/lp/dgesl.f /tmp/x/lp/daxpy.f /tmp/x/lp/dscal.f /tmp/x/lp/ddot.f /tmp/x/lp/idamax.f
gfortran -std=legacy -w -O2 -o drvlin drvlin.f gen.f dgefa.o dgesl.o daxpy.o dscal.o ddot.o idamax.o shim_l1.o -Wl,__WRAPS_L1__
echo BUILT_LINPACK

# ---- arm 2: reference LAPACK as preserved, built by its own cmake
gfortran -std=legacy -w -O2 -o drvlap drvlap.f gen.f shim_full.o -L/tmp/la/b/lib -llapack -lblas -Wl,__WRAPS_FULL__
echo BUILT_LAPACK

for N in __SIZES__; do
  echo "=== ARM linpack N=$N"; ./drvlin $N
  echo "=== ARM lapack  N=$N"; ./drvlap $N
done
'''


def _build_script():
    s = (SCRIPT.replace("__SHIM__", SHIM_C).replace("__GEN__", GEN_F)
         .replace("__DRVLIN__", DRV_LINPACK_F).replace("__DRVLAP__", DRV_LAPACK_F)
         .replace("__WRAPS_L1__", WRAPS_L1).replace("__WRAPS_FULL__", WRAPS_FULL).replace("__SIZES__", " ".join(str(n) for n in SIZES)))
    return s


def parse(out):
    arms, cur = [], None
    for line in out.splitlines():
        t = line.strip()
        if t.startswith("=== ARM "):
            p = t.split()
            cur = {"arm": p[2], "n": int(p[3].split("=")[1]), "routines": {}, "info": None,
                   "max_err": None, "seconds": None}
            arms.append(cur)
        elif cur is None:
            continue
        elif t.startswith("SHIM "):
            _, name, lvl, calls, refs = t.split()
            cur["routines"][name] = {"level": int(lvl), "calls": int(calls), "element_refs": float(refs)}
        elif t.startswith("INFO "):
            cur["info"] = int(t.split()[1])
        elif t.startswith("MAXERR "):
            cur["max_err"] = float(t.split()[1])
        elif t.startswith("SECONDS "):
            cur["seconds"] = float(t.split()[1])
    for a in arms:
        tot = sum(r["element_refs"] for r in a["routines"].values())
        l3 = sum(r["element_refs"] for r in a["routines"].values() if r["level"] == 3)
        a["total_element_refs"] = tot
        a["level3_element_refs"] = l3
        a["LEVEL3_FRACTION"] = (l3 / tot) if tot else 0.0
    return arms


def main():
    out = subprocess.run(["wsl.exe", "-e", "bash", "-lc",
        "docker run --rm -v %s:/vault:ro prometheus-fossil-c:bookworm bash -lc %s" % (VAULT, _q(_build_script()))],
        capture_output=True, text=True, timeout=5400)
    arms = parse(out.stdout)
    doc = {"schema": "techne.fossil.supersession_behavior/1",
           "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "prereg": "techne/fossils/PREREG_SUPERSESSION_BEHAVIOR_2026-09-13.md",
           "pair": ["linpack-netlib-1979", "lapack-reference"],
           "preregistered_sizes": SIZES,
           "coordinate": "LEVEL3_FRACTION = element-references issued through Level-3 BLAS / total element-references",
           "method": "both fossils compiled exactly as preserved; BLAS calls counted with ld --wrap, which "
                     "redirects undefined references to a counting shim at LINK time. No preserved body edited.",
           "secondary_confounded": "SECONDS is cpu_time and is CONFOUNDED (one host, unoptimised reference BLAS, "
                                   "shim overhead penalises the arm making more calls). It carries no claim.",
           "arms": arms}
    op = HERE / ("SUPERSESSION_BEHAVIOR_%s.json" % DATE)
    op.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("%-9s %-6s %-12s %-12s %-9s %-10s %s" % ("arm", "n", "L3_refs", "total_refs", "L3_frac", "max_err", "routines"))
    for a in arms:
        print("%-9s %-6d %-12.4g %-12.4g %-9.4f %-10.2e %s" % (
            a["arm"], a["n"], a["level3_element_refs"], a["total_element_refs"], a["LEVEL3_FRACTION"],
            a["max_err"] if a["max_err"] is not None else float("nan"),
            ",".join(sorted(a["routines"]))))
    if not arms:
        print("NO ARMS PARSED -- build or run failed; stderr tail:")
        print(out.stderr[-2000:])
        print(out.stdout[-2000:])
    print("wrote", op)


def _q(s):
    return "'" + s.replace("'", "'\\''") + "'"


if __name__ == "__main__":
    main()
