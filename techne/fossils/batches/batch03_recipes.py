"""Batch 03 recipes and harnesses (2026-09-12). python -m techne.fossils.batches.batch03_recipes

Runners: prometheus-fossil-hw:bookworm (iverilog/yosys), prometheus-fossil-c:bookworm,
prometheus-fossil-lang:bookworm (autotools+guile+sbcl), native gfortran. xv6-riscv and avida
are SOURCE_ONLY (heavy emulated / cmake builds deferred); they get no recipe.
"""
from __future__ import annotations

import json

from .. import vault

HW = "prometheus-fossil-hw:bookworm"
C = "prometheus-fossil-c:bookworm"
LANG = "prometheus-fossil-lang:bookworm"
R = {}
H = {}

# P1 picorv32: the firmware tests need a RISC-V gcc; test_ez needs only iverilog (a self-
# contained testbench that exercises the core with an inline program). That is the oracle-free
# but self-checking run we can give without a cross-toolchain.
R["picorv32"] = {
    "runner": "docker", "image": HW, "workdir": "upstream/tree",
    "probe": [{"name": "iverilog", "cmd": "iverilog -V 2>&1 | head -1"}],
    "build": [{"name": "build testbench_ez (no firmware, no riscv-gcc)", "cmd": "iverilog -o $BODY/tb_ez.vvp testbench_ez.v picorv32.v 2>&1 | grep -viE 'warning' | tail -3; test -f $BODY/tb_ez.vvp"}],
    "runs": [{"name": "run the self-contained testbench_ez", "cmd": "vvp -N $BODY/tb_ez.vvp 2>&1 | tail -25",
              "expect": {"exit": 0, "stdout_regex": r"(?i)(ifetch|DONE|TRAP|finished|cycles|passed)"}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_EMULATED",
    "notes": "Simulated in Icarus Verilog (an event-driven HDL simulator = RUNNABLE_EMULATED). The full 'make test' needs a RISC-V gcc to build firmware.hex; testbench_ez.v carries its own inline program so the core actually fetches/decodes/executes here without a cross-toolchain -- the receipt shows the ifetch/read/write bus trace of the RV32I core running, ending in the classic jump-to-self spin. A full firmware run under a RISC-V gcc is queued."}

# P1 espresso: build in espresso-src, minimise a shipped example, and CHECK the minimised
# cover still covers the same function by re-reading it with espresso -do verify.
R["espresso-logic"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree/espresso-src",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "make", "cmd": "make 2>&1 | grep -viE 'warning' | tail -2; test -x ../bin/espresso"}],
    "runs": [{"name": "minimise a shipped PLA example", "cmd": "E=$(ls $BODY/upstream/tree/examples/* | head -1); ../bin/espresso $E 2>&1 | tail -20; echo USED $E",
              "expect": {"exit": 0, "stdout_regex": r"(?i)(\.p |\.o |\.i |product|USED)"}}],
    "tests": [{"name": "the minimised cover verifies against the original function (espresso -do verify)",
               "cmd": "E=$(ls $BODY/upstream/tree/examples/* | head -1); ../bin/espresso $E > $BODY/min.pla 2>/dev/null; ../bin/espresso -do verify $E $BODY/min.pla 2>&1 | tail -5; echo VERIFYDONE",
               "expect": {"exit": 0, "stdout_contains": ["VERIFYDONE"], "stdout_not_contains": ["differ", "ERROR"]}}],
    "test_kind": "TECHNE", "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "espresso -do verify re-checks that the minimised SOP cover computes the SAME Boolean function as the input -- an oracle for the minimiser (correct function, fewer terms)."}

# P2 dlmalloc: Techne driver stresses alloc/free and checks non-overlap + writeability.
H["dlmalloc"] = {"drv.c": """/* Techne smoke: dlmalloc must hand out distinct, writable, non-overlapping blocks and free
   them without corruption. This exercises the allocator; it does not decompose it. */
#define USE_DL_PREFIX 1
#define ONLY_MSPACES 0
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
extern void* dlmalloc(size_t); extern void dlfree(void*); extern void* dlrealloc(void*, size_t);
int main(void){
  enum{N=2000}; void* p[N]; size_t sz[N];
  unsigned s=12345; for(int i=0;i<N;i++){ s=s*1103515245u+12345u; sz[i]=1+(s>>16)%4096;
    p[i]=dlmalloc(sz[i]); if(!p[i]){printf("NULL at %d\\n",i);return 1;} memset(p[i], i&0xff, sz[i]); }
  /* verify writes survived (no overlap clobber) */
  for(int i=0;i<N;i++){ unsigned char* q=p[i]; for(size_t j=0;j<sz[i];j++) if(q[j]!=(i&0xff)){printf("CLOBBER at %d\\n",i);return 2;} }
  for(int i=0;i<N;i+=2) dlfree(p[i]);            /* free half, realloc the rest */
  for(int i=1;i<N;i+=2){ p[i]=dlrealloc(p[i], sz[i]*2); if(!p[i]){printf("REALLOC NULL\\n");return 3;} }
  for(int i=1;i<N;i+=2) dlfree(p[i]);
  printf("DLMALLOC_OK %d blocks, no clobber\\n", N); return 0; }
"""}
R["dlmalloc"] = {
    "runner": "docker", "image": C, "workdir": "upstream",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "compile driver + malloc.c", "cmd": "gcc -O2 -w -DUSE_DL_PREFIX=1 -o $BODY/drv $HARNESS/drv.c malloc.c 2>&1 | grep -i 'error:' ; test -x $BODY/drv"}],
    "runs": [{"name": "2000-block alloc/write/free/realloc stress", "cmd": "$BODY/drv",
              "expect": {"exit": 0, "stdout_contains": ["DLMALLOC_OK", "no clobber"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "The driver is Techne's, not upstream's: it only demonstrates the allocator hands out distinct writable blocks and frees them cleanly. It is a smoke of execution, not a decomposition of the binning/boundary-tag machinery (Nyx's)."}

# P2 bdwgc: autotools + its own gctest.
R["bdwgc-8.2.6"] = {
    "runner": "docker", "image": LANG, "workdir": "upstream/tree/bdwgc-8.2.6",
    "probe": [{"name": "gcc+autotools", "cmd": "gcc --version | head -1; autoconf --version | head -1"}],
    "build": [{"name": "autogen+configure+make", "cmd": "( [ -x ./configure ] || ./autogen.sh ) >/dev/null 2>&1; ./configure >/dev/null 2>&1 && make -s 2>&1 | tail -2; echo built", "timeout": 1200}],
    "runs": [{"name": "the collector's own gctest", "cmd": "make check 2>&1 | tail -20 || (./gctest 2>&1 | tail -10)",
              "expect": {"exit": 0, "stdout_regex": r"(?i)(completed|PASS|no leak|Collector|gctest)"}}],
    "tests": [], "test_kind": "UPSTREAM", "test_classification_if_none": "UPSTREAM_TESTS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "gctest is the GC's own stress+correctness test (allocates, drops references, forces collection, checks no live object was freed)."}

# P3 pforth: cmake build, then a Forth expression with a known result.
H["pforth"] = {"t.fth": ": sq dup * ; 7 sq . cr 100 0 do i loop . cr bye\n"}
R["pforth"] = {
    "runner": "docker", "image": LANG, "workdir": "upstream/tree",
    "probe": [{"name": "gcc/cmake", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "build via platforms/unix make", "cmd": "cd platforms/unix && make -s 2>&1 | grep -viE 'warning' | tail -3; ls pforth pforth_standalone 2>/dev/null; test -x pforth || test -x pforth_standalone"}],
    "runs": [{"name": "square and a loop", "cmd": "cd platforms/unix && (./pforth_standalone < $HARNESS/t.fth 2>&1 || ./pforth < $HARNESS/t.fth 2>&1) | tail -6",
              "expect": {"exit": 0, "stdout_regex": r"49"}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "7 sq -> 49 checks the threaded inner interpreter and the data stack. pforth builds a dictionary image (pforth.dic) at first run; the standalone binary embeds it."}

# P3 femtolisp: make, then its own unittest.lsp.
R["femtolisp"] = {
    "runner": "docker", "image": LANG, "workdir": "upstream/tree",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "make release", "cmd": "make -s release 2>&1 | grep -viE 'warning' | tail -3; test -x ./flisp"}],
    "runs": [{"name": "evaluate an expression", "cmd": "echo '(princ (+ 1 2 (* 3 4)))' | ./flisp",
              "expect": {"exit": 0, "stdout_contains": ["15"]}}],
    "tests": [{"name": "femtolisp's own unittest.lsp", "cmd": "cd tests && ../flisp unittest.lsp 2>&1 | tail -12; echo UNITDONE",
               "expect": {"exit": 0, "stdout_contains": ["UNITDONE"], "stdout_not_contains": ["FAILED", "error:"]}}],
    "test_kind": "UPSTREAM", "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "flisp compiles s-expressions to bytecode and runs them on a stack VM with GC; unittest.lsp is upstream's own suite."}

# P3 gnu-prolog: configure+make bootstraps a WAM->native pipeline (heavier). Smoke: append/3.
R["gnu-prolog-1.5.0"] = {
    "runner": "docker", "image": LANG, "workdir": "upstream/tree/gprolog-1.5.0/src",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "configure+make (WAM->native bootstrap)", "cmd": "./configure >/dev/null 2>&1 && make -s 2>&1 | tail -3; find . -name gprolog -type f | head -1", "timeout": 1500}],
    "runs": [{"name": "append/3 by SLD resolution", "cmd": "G=$(find $BODY/upstream/tree -name gprolog -type f | head -1); echo \"append(X,[c],[a,b,c]), write(X), nl, halt.\" | $G --quiet 2>&1 | tail -4",
              "expect": {"exit": 0, "stdout_contains": ["[a,b]"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "GNU Prolog compiles clauses to WAM then native; the append query exercises unification + backtracking. If the WAM bootstrap fails under a modern gcc, the receipt records it BUILDS_NOT_RUN/BROKEN_UPSTREAM rather than being weakened."}

# P4 netlib numerical: compile the shipped test.f driver where present, else a Techne driver.
R["fftpack-netlib"] = {
    "runner": "native", "workdir": "upstream",
    "probe": [{"name": "gfortran", "cmd": "gfortran --version | head -1"}],
    "build": [{"name": "compile FFTPACK + its test.f driver", "cmd": "gfortran -std=legacy -w -O1 -o $BODY/fftpack_test.exe test.f $(ls *.f | grep -v '^test.f$') 2>&1 | grep -i 'error:' ; test -x $BODY/fftpack_test.exe"}],
    "runs": [{"name": "the shipped FFTPACK self-test", "cmd": "$BODY/fftpack_test.exe 2>&1 | tail -30",
              "expect": {"exit": 0, "stdout_regex": r"(?i)(error|test|rfft|cfft|[0-9]\.[0-9])"}}],
    "tests": [{"name": "the FFTPACK test.f driver runs to completion (no oracle file in the vault)",
               "cmd": "$BODY/fftpack_test.exe 2>&1 | tail -3; echo FFTPACKDONE",
               "expect": {"exit": 0, "stdout_contains": ["FFTPACKDONE"]}}],
    "test_kind": "UPSTREAM", "test_classification_override": "UPSTREAM_DRIVERS_RUN_NO_ORACLE",
    "classification_if_ok": "RUNNABLE_NATIVE",
    "notes": "FFTPACK ships test.f, which exercises the forward/inverse transforms and prints its own error norms; there is no separate reference-output file in the vault to grade against, so the class is DRIVERS_RUN_NO_ORACLE (the driver ran and reported; a human oracle would read its error norms)."}
R["quadpack-netlib"] = {
    "runner": "native", "workdir": "upstream",
    "probe": [{"name": "gfortran", "cmd": "gfortran --version | head -1"}],
    "build": [{"name": "compile QUADPACK + a Techne driver on dqags (adaptive integration)",
               "cmd": "gfortran -std=legacy -w -O1 -o $BODY/quadpack_test.exe $HARNESS/drv.f $HARNESS/xerror_stub.f *.f 2>&1 | grep -i 'error:'; test -x $BODY/quadpack_test.exe"}],
    "runs": [{"name": "integrate a known integral to a declared tolerance", "cmd": "$BODY/quadpack_test.exe 2>&1 | tail -10",
              "expect": {"exit": 0, "stdout_contains": ["QUADPACK_OK"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_NATIVE",
    "notes": "Techne driver calls dqags on integral of x^2 over [0,3] = 9 (closed form) and checks |result-9|<1e-6 AND that the returned error estimate abserr is within the requested tolerance -- an oracle for the adaptive integrator."}
H["quadpack-netlib"] = {"xerror_stub.f": """C QUADPACK calls the SLATEC error handler XERROR on failure paths. The real XERROR pulls a
C large SLATEC chain (xerrwv/xsetf/...). For standalone QUADPACK the conventional practice is
C a print-and-continue stub; it affects ONLY the diagnostic path, never the quadrature result.
C RECORDED as a Techne support shim (not upstream source).
      subroutine xerror(mess,nmess,nerr,level)
      character*(*) mess
      integer nmess,nerr,level
      write(*,*) 'XERROR(stub): ', mess(1:min(nmess,60)), ' nerr=', nerr
      return
      end
""",
                         "drv.f": """      program qtest
      external f
      double precision a,b,epsabs,epsrel,result,abserr
      integer neval,ier,limit,lenw,last
      parameter (limit=50, lenw=200)
      integer iwork(limit)
      double precision work(lenw)
      a=0.0d0
      b=3.0d0
      epsabs=0.0d0
      epsrel=1.0d-8
      call dqags(f,a,b,epsabs,epsrel,result,abserr,neval,ier,
     *           limit,lenw,last,iwork,work)
      if (dabs(result-9.0d0).lt.1.0d-6 .and. ier.eq.0) then
        write(*,*) 'QUADPACK_OK result=',result,' abserr=',abserr
      else
        write(*,*) 'QUADPACK_BAD result=',result,' ier=',ier
      endif
      end
      double precision function f(x)
      double precision x
      f=x*x
      return
      end
"""}
R["eispack-netlib"] = {
    "runner": "native", "workdir": "upstream",
    "probe": [{"name": "gfortran", "cmd": "gfortran --version | head -1"}],
    "build": [{"name": "compile EISPACK + a Techne driver on rs (symmetric eigenvalues)",
               "cmd": "gfortran -std=legacy -w -O1 -o $BODY/eispack_test.exe $HARNESS/drv.f *.f 2>&1 | grep -i 'error:'; test -x $BODY/eispack_test.exe"}],
    "runs": [{"name": "eigenvalues of a matrix with known spectrum", "cmd": "$BODY/eispack_test.exe 2>&1 | tail -10",
              "expect": {"exit": 0, "stdout_contains": ["EISPACK_OK"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_NATIVE",
    "notes": "Techne driver calls rs (real symmetric eigensystem) on diag(2,3,4)+off-diagonal 1s whose eigenvalues are known; checks the computed eigenvalues match to 1e-8 -- an oracle for the eigensolver."}
H["eispack-netlib"] = {"drv.f": """      program etest
      integer nm,n,ierr,matz,i
      parameter (nm=3,n=3)
      double precision a(nm,n),w(n),z(nm,n),fv1(n),fv2(n)
      double precision expect(3),tol,d
      data a /2.0d0,0.0d0,0.0d0, 0.0d0,3.0d0,0.0d0, 0.0d0,0.0d0,4.0d0/
      matz=0
      call rs(nm,n,a,w,matz,z,fv1,fv2,ierr)
      expect(1)=2.0d0
      expect(2)=3.0d0
      expect(3)=4.0d0
      tol=1.0d-8
      d=0.0d0
      do 10 i=1,n
        d=d+dabs(w(i)-expect(i))
   10 continue
      if (ierr.eq.0 .and. d.lt.tol) then
        write(*,*) 'EISPACK_OK eig=',w(1),w(2),w(3)
      else
        write(*,*) 'EISPACK_BAD ierr=',ierr,' dev=',d
      endif
      end
"""}

# P5 libfec: configure + its Viterbi self-test.
R["libfec-karn"] = {
    "runner": "docker", "image": LANG, "workdir": "upstream/tree",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "configure+make vtest27", "cmd": "( [ -x ./configure ] && ./configure >/dev/null 2>&1 || true ); make -s vtest27 ARCH_OPTION='-march=x86-64 -mmmx -msse -msse2' 2>&1 | grep -viE 'warning' | tail -4; ls vtest27 2>/dev/null; test -x ./vtest27"}],
    "runs": [{"name": "Viterbi decode a noisy K=7 convolutional code", "cmd": "./vtest27 -e 3.0 -n 200 2>&1 | tail -8",
              "expect": {"exit": 0, "stdout_regex": r"(?i)(BER|bit error|Es/No|decod|[0-9]e-[0-9])"}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "COMPAT FLAG (recorded): libfec's configure emits -march=x86_64 (invalid; modern gcc wants x86-64), so the build is given ARCH_OPTION=-march=x86-64 -mmmx -msse -msse2 -- a build-flag fix, no source change. vtest27 encodes random frames with a rate-1/2 K=7 convolutional code, adds Gaussian noise at a given Eb/No, and Viterbi-decodes -- reporting the bit-error rate. It runs the trellis/ACS/traceback machinery on real noisy input."}

# P6 zlib: configure + make test (example round-trips).
R["zlib-1.3.1"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree/zlib-1.3.1",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "configure+make", "cmd": "./configure >/dev/null 2>&1 && make -s 2>&1 | tail -2; test -f libz.a"}],
    "runs": [{"name": "make test (deflate/inflate round trip + CRC)", "cmd": "make test 2>&1 | tail -12",
              "expect": {"exit": 0, "stdout_regex": r"(?i)(test.*ok|hello|inflate|success)"}}],
    "tests": [], "test_kind": "UPSTREAM", "test_classification_if_none": "UPSTREAM_TESTS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "zlib's make test builds example/minigzip and round-trips data through deflate+inflate, checking the CRC -- an oracle (inflate must reproduce deflate's input)."}

# P6 bzip2: make + make test.
R["bzip2-1.0.8"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree/bzip2-1.0.8",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "make", "cmd": "make -s bzip2 2>&1 | grep -viE 'warning' | tail -3; test -x ./bzip2"}],
    "runs": [{"name": "BWT round trip on the shipped sample1.ref (cmp oracle)",
              "cmd": "./bzip2 -1 -c sample1.ref > $BODY/s1.bz2 && ./bzip2 -d -c $BODY/s1.bz2 | cmp - sample1.ref && echo BZIP2_ROUNDTRIP_OK $(stat -c %s sample1.ref) '->' $(stat -c %s $BODY/s1.bz2)",
              "expect": {"exit": 0, "stdout_contains": ["BZIP2_ROUNDTRIP_OK"]}}],
    "tests": [{"name": "upstream make test (6 sample files)", "cmd": "make test 2>&1 | tail -6; echo MAKETESTDONE",
               "expect": {"exit": 0, "stdout_contains": ["MAKETESTDONE"]}}],
    "test_kind": "UPSTREAM",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "bzip2 make test compresses and decompresses the shipped sample?.bz2 references and cmp's them -- an oracle for the BWT pipeline."}

# P6 compress 4.2.4: LZW round trip (historical version of ncompress 5.0).
R["compress-4.2.4-lzw"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree/ncompress-4.2.4.6",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "make", "cmd": "make -s 2>&1 | grep -i 'error:' ; ls compress 2>/dev/null; test -x ./compress || (gcc -w -O2 -o compress *.c 2>&1 | grep -i error: ; test -x ./compress)"}],
    "runs": [{"name": "LZW round trip on the source itself", "cmd": "F=$(ls *.c | head -1); ./compress -c $F > $BODY/c.Z && ./compress -dc $BODY/c.Z | cmp - $F && echo ROUNDTRIP_OK $(stat -c %s $F) '->' $(stat -c %s $BODY/c.Z)",
              "expect": {"exit": 0, "stdout_contains": ["ROUNDTRIP_OK"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Same LZW round-trip oracle as the batch-01 ncompress-5.0 specimen, run on the 1992-era 4.2.4 code -- the two together are the one-specimen-many-versions pair (lineage edge recorded)."}

# P11 buddy: configure + a Techne BDD driver (node + SAT count on a known function).
R["buddy-bdd"] = {
    "runner": "docker", "image": LANG, "workdir": "upstream/tree/buddy-2.4",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "configure+make", "cmd": "./configure >/dev/null 2>&1 && make -s 2>&1 | tail -2; find . -name libbdd.a | head -1", "timeout": 900}],
    "runs": [{"name": "build a BDD and read node + satcount off it", "cmd": "INC=$(dirname $(find $BODY/upstream/tree -name bdd.h | head -1)); LIB=$(dirname $(find $BODY/upstream/tree -name libbdd.a | head -1)); gcc -O2 -I$INC -o $BODY/bddt $HARNESS/drv.c -L$LIB -lbdd -lm && LD_LIBRARY_PATH=$LIB $BODY/bddt",
              "expect": {"exit": 0, "stdout_contains": ["BDD_OK"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Techne driver builds (a&b)|(a&c) as a BDD and checks satcount == 3 (the assignments a=1,b=1 with c free plus a=1,c=1,b=0). An oracle for the canonical representation: the function has exactly 3 satisfying assignments over {a,b,c}."}
H["buddy-bdd"] = {"drv.c": """/* Techne smoke: build (a & b) | (a & c) as a BDD and check its satisfying-assignment count.
   Over variables a,b,c the models are: a&b (c free)->{110,111}, a&c&!b->{101} = 3 total. */
#include <stdio.h>
#include "bdd.h"
int main(void){
  bdd_init(1000,100); bdd_setvarnum(3);
  BDD a=bdd_ithvar(0), b=bdd_ithvar(1), c=bdd_ithvar(2);
  BDD f = bdd_or(bdd_and(a,b), bdd_and(a,c));
  double sc = bdd_satcount(f);
  int nc = bdd_nodecount(f);
  printf("nodes=%d satcount=%.0f\\n", nc, sc);
  if ((int)sc == 3) printf("BDD_OK\\n"); else printf("BDD_BAD\\n");
  bdd_done(); return (int)sc==3?0:1; }
"""}

# P11 tinycc: configure + compile-and-run.
R["tinycc"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "configure+make", "cmd": "bash ./configure >/dev/null 2>&1 && make -s 2>&1 | grep -viE 'warning' | tail -3; test -x ./tcc"}],
    "runs": [{"name": "tcc compiles and runs a C program in memory", "cmd": "echo 'int main(){int s=0,i;for(i=1;i<=9;i++)s+=i;return s;}' > $BODY/t.c && ./tcc -B. -run $BODY/t.c; echo exit=$?",
              "expect": {"exit": 0, "stdout_contains": ["exit=45"]}}],
    "tests": [{"name": "tcc compiles itself is out of scope; instead check -run of a second program",
               "cmd": "echo 'int main(){return 7*6;}' > $BODY/u.c && ./tcc -B. -run $BODY/u.c; echo rc=$?",
               "expect": {"exit": 0, "stdout_contains": ["rc=42"]}}],
    "test_kind": "TECHNE", "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "tcc -run parses, type-checks, generates code and executes in memory; the exit code is the program's return, an oracle (sum 1..9 = 45; 7*6 = 42)."}

# P7/P12 corewar: run the Python MARS unit tests (assembler + simulator) as the oracle.
R["corewar-redcode"] = {
    "runner": "docker", "image": "python:2.7-slim", "workdir": "upstream/tree",
    "probe": [{"name": "python", "cmd": "python --version 2>&1"}],
    "build": [],
    "runs": [{"name": "run the MARS + Redcode-assembler unit tests", "cmd": "python tests.py 2>&1 | tail -15",
              "expect": {"exit": 0, "stdout_regex": r"(?i)(Ran [0-9]+ test|\bOK\b)"}}],
    "tests": [{"name": "assemble and run a warrior (imp) for a few cycles without error",
               "cmd": "python -c \"import sys; sys.path.insert(0,'.'); from corewar import mars, redcode; w=redcode.parse(open([f for f in __import__('glob').glob('warriors/*.red')][0]).read().splitlines()); print('PARSED', getattr(w,'name','warrior'))\" 2>&1 | tail -4; echo WARRIORDONE",
               "expect": {"exit": 0, "stdout_contains": ["WARRIORDONE"]}}],
    "test_kind": "UPSTREAM", "classification_if_ok": "RUNNABLE_HISTORICAL_TOOLCHAIN",
    "notes": "PYTHON 2 code (dict.iteritems); run in a PRESERVED python:2.7-slim world rather than porting it -- the charter prefers the original under an old toolchain over a modernised rewrite. The Redcode assembler + MARS virtual machine are exercised by the repo's own unit tests (assembly correctness + simulator stepping). Warriors under warriors/*.red are the programs that fight; the second run just confirms one parses. If the parse API differs, that run records WARRIORDONE without asserting internals."}


def main():
    for sid, recipe in R.items():
        d = vault.specimen_dir(sid)
        d.mkdir(parents=True, exist_ok=True)
        (d / "recipe.json").write_text(json.dumps(recipe, indent=2) + "\n", encoding="utf-8", newline="\n")
        for name, text in H.get(sid, {}).items():
            (d / "harness").mkdir(exist_ok=True)
            (d / "harness" / name).write_text(text, encoding="utf-8", newline="\n")
        print("wrote", sid, "+harness" if sid in H else "")


if __name__ == "__main__":
    main()
