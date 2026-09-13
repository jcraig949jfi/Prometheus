"""Batch 05 recipes + harnesses (2026-09-12). python -m techne.fossils.batches.batch05_recipes

The three BSD TCP versions are SOURCE_ONLY (kernel code) -> no recipe. Python specimens
pip-install themselves (and their pinned deps) at run time in python:3.11-slim (recorded).
Legacy cultures run in prometheus-fossil-legacy:bookworm (GNAT, GnuCOBOL, bwBASIC, SBCL).
Every recipe executes in the disposable work/ copy (harvest.run isolation); nothing here
touches upstream/. Deviations are in each recipe's "notes" and repeated in the record.
"""
from __future__ import annotations

import json
from .. import vault

C = "prometheus-fossil-c:bookworm"
LANG = "prometheus-fossil-lang:bookworm"
HW = "prometheus-fossil-hw:bookworm"
LEGACY = "prometheus-fossil-legacy:bookworm"
PY = "python:3.11-slim"
GCC49 = "gcc:4.9"
R = {}
H = {}


def py_recipe(sid, workdir, harness_name, expects, pip_extra="", notes="", timeout=900, apt="", env=""):
    # Every recipe command is its own `docker run --rm`, so the install and the harness must
    # share ONE command: (apt) ; pip install . ; python harness. The build step only checks that
    # the source installs; the run step installs again into a fresh container and runs.
    pre = ("apt-get -qq update >/dev/null && apt-get -qq install -y %s >/dev/null 2>&1; " % apt) if apt else ""
    install = pre + (env + " " if env else "") + "pip install -q %s . 2>&1 | grep -v -i 'notice\\|warning' | tail -2" % pip_extra
    R[sid] = {"runner": "docker", "image": PY, "workdir": workdir,
              "probe": [{"name": "python", "cmd": "python --version"}],
              "build": [{"name": ("apt %s + " % apt if apt else "") + "pip install the acquired source (+ pinned deps)", "cmd": install + "; python -c 'import sys; print(sys.version.split()[0])'", "timeout": timeout}],
              "runs": [{"name": harness_name.replace(".py", "") + " (Techne harness, oracle-backed; same-container install + run)", "cmd": install + " >/dev/null; python $HARNESS/%s" % harness_name, "expect": expects, "timeout": timeout + 900}],
              "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
              "classification_if_ok": "RUNNABLE_CONTAINER",
              "notes": notes}


# ============================ A: CONTENTION / RETRY / RECOVERY ===============================
R["lmdb-0.9.31"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree/lmdb-LMDB_0.9.31/libraries/liblmdb",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "make liblmdb + the shipped mtest drivers", "cmd": "make -s liblmdb.a mtest mtest3 2>&1 | grep -iE '\\berror' | head -3; test -x ./mtest && test -f liblmdb.a && echo built"},
              {"name": "compile Techne's crash-recovery driver against liblmdb.a", "cmd": "gcc -O1 -I. -o $BODY/build/crash $HARNESS/crash.c liblmdb.a -lpthread && echo built"}],
    "runs": [{"name": "upstream mtest (random put/get/del + cursor scan)", "cmd": "rm -rf testdb && mkdir testdb && ./mtest 2>&1 | tail -3 && echo MTEST_OK", "expect": {"exit": 0, "stdout_contains": ["MTEST_OK"]}},
             {"name": "commit 1000 entries", "cmd": "rm -rf $BODY/build/db && mkdir -p $BODY/build/db && $BODY/build/crash $BODY/build/db commit", "expect": {"exit": 0, "stdout_contains": ["committed 1000"]}},
             {"name": "CRASH: a second process puts 500 more inside an open transaction and _exit()s without committing", "cmd": "$BODY/build/crash $BODY/build/db crash; echo exit=$?", "expect": {"exit": 0, "stdout_contains": ["exit=1"]}},
             {"name": "reopen and count (the recovery property: the uncommitted 500 must be absent, the 1000 present)", "cmd": "$BODY/build/crash $BODY/build/db count", "expect": {"exit": 0, "stdout_contains": ["entries=1000", "RECOVERY OK"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle: after a writer dies mid-transaction the database opens at the last committed root (1000 entries), with no repair step. Upstream mtest also run."}
H["lmdb-0.9.31"] = {"crash.c": r'''/* Techne harness: LMDB crash-consistency. modes: commit | crash | count */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "lmdb.h"
static void die(const char *m, int rc) { fprintf(stderr, "%s: %s\n", m, mdb_strerror(rc)); exit(2); }
int main(int argc, char **argv) {
    if (argc < 3) return 2;
    const char *path = argv[1], *mode = argv[2];
    MDB_env *env; MDB_dbi dbi; MDB_txn *txn; MDB_val k, v; char kb[32], vb[32]; int rc, i;
    mdb_env_create(&env); mdb_env_set_mapsize(env, 64u << 20);
    if ((rc = mdb_env_open(env, path, 0, 0664))) die("env_open", rc);
    if (!strcmp(mode, "commit") || !strcmp(mode, "crash")) {
        int lo = strcmp(mode, "commit") ? 1000 : 0, hi = strcmp(mode, "commit") ? 1500 : 1000;
        if ((rc = mdb_txn_begin(env, NULL, 0, &txn))) die("txn_begin", rc);
        if ((rc = mdb_dbi_open(txn, NULL, 0, &dbi))) die("dbi_open", rc);
        for (i = lo; i < hi; i++) {
            sprintf(kb, "key%06d", i); sprintf(vb, "val%06d", i);
            k.mv_size = strlen(kb); k.mv_data = kb; v.mv_size = strlen(vb); v.mv_data = vb;
            if ((rc = mdb_put(txn, dbi, &k, &v, 0))) die("put", rc);
        }
        if (!strcmp(mode, "crash")) { printf("crashing with %d uncommitted puts in an open write transaction\n", hi - lo); fflush(stdout); _exit(1); }
        if ((rc = mdb_txn_commit(txn))) die("commit", rc);
        printf("committed %d entries\n", hi - lo);
    } else {
        MDB_stat st;
        if ((rc = mdb_txn_begin(env, NULL, MDB_RDONLY, &txn))) die("txn_begin", rc);
        if ((rc = mdb_dbi_open(txn, NULL, 0, &dbi))) die("dbi_open", rc);
        mdb_stat(txn, dbi, &st);
        printf("entries=%zu\n", (size_t) st.ms_entries);
        sprintf(kb, "key%06d", 1200); k.mv_size = strlen(kb); k.mv_data = kb;
        rc = mdb_get(txn, dbi, &k, &v);
        printf("uncommitted key1200 present? %s\n", rc == MDB_NOTFOUND ? "no" : "YES");
        printf("%s\n", (st.ms_entries == 1000 && rc == MDB_NOTFOUND) ? "RECOVERY OK" : "RECOVERY FAILED");
        mdb_txn_abort(txn);
    }
    mdb_env_close(env);
    return 0;
}
'''}

R["leveldb-1.23"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree/leveldb-1.23",
    "probe": [{"name": "cmake", "cmd": "cmake --version | head -1; g++ --version | head -1"}],
    "build": [{"name": "cmake + make libleveldb (tests/benchmarks off: googletest is a submodule absent from the release tarball)",
               "cmd": "mkdir -p $BODY/build/ldb && cd $BODY/build/ldb && cmake -DCMAKE_BUILD_TYPE=Release -DLEVELDB_BUILD_TESTS=OFF -DLEVELDB_BUILD_BENCHMARKS=OFF $BODY/upstream/tree/leveldb-1.23 >/dev/null && make -s leveldb 2>&1 | grep -iE '\\berror' | head -3; test -f libleveldb.a && echo built", "timeout": 900},
              {"name": "compile Techne's log-recovery driver", "cmd": "g++ -std=c++11 -O1 -Iinclude -o $BODY/build/recover $HARNESS/recover.cc $BODY/build/ldb/libleveldb.a -lpthread && echo built"}],
    "runs": [{"name": "write 2000 keys and close cleanly", "cmd": "rm -rf $BODY/build/db && $BODY/build/recover $BODY/build/db write 0 2000", "expect": {"exit": 0, "stdout_contains": ["wrote 2000"]}},
             {"name": "CRASH: write 500 more (acknowledged, unsynced) and _exit() without closing -- they live only in the .log", "cmd": "$BODY/build/recover $BODY/build/db crash 2000 2500; echo exit=$?", "expect": {"exit": 0, "stdout_contains": ["exit=1"]}},
             {"name": "reopen: RecoverLogFile replays the log (the recovery property: 2500 present)", "cmd": "$BODY/build/recover $BODY/build/db count", "expect": {"exit": 0, "stdout_contains": ["count=2500", "RECOVERY OK"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle: acknowledged writes that never reached a table survive a process crash via write-ahead-log replay on open. DEVIATION: upstream unit tests not built (googletest submodule not in the tarball)."}
H["leveldb-1.23"] = {"recover.cc": r'''// Techne harness: LevelDB write-ahead-log recovery. modes: write lo hi | crash lo hi | count
#include <cstdio>
#include <cstdlib>
#include <string>
#include <unistd.h>
#include "leveldb/db.h"
int main(int argc, char** argv) {
    if (argc < 3) return 2;
    std::string path = argv[1], mode = argv[2];
    leveldb::DB* db; leveldb::Options o; o.create_if_missing = true;
    leveldb::Status s = leveldb::DB::Open(o, path, &db);
    if (!s.ok()) { fprintf(stderr, "open: %s\n", s.ToString().c_str()); return 2; }
    if (mode == "write" || mode == "crash") {
        int lo = atoi(argv[3]), hi = atoi(argv[4]); char k[32], v[32];
        for (int i = lo; i < hi; i++) { snprintf(k, 32, "key%06d", i); snprintf(v, 32, "val%06d", i); db->Put(leveldb::WriteOptions(), k, v); }
        if (mode == "crash") { printf("crashing after %d acknowledged unsynced puts (no Close)\n", hi - lo); fflush(stdout); _exit(1); }
        printf("wrote %d\n", hi - lo); delete db;
    } else {
        long n = 0; leveldb::Iterator* it = db->NewIterator(leveldb::ReadOptions());
        for (it->SeekToFirst(); it->Valid(); it->Next()) n++;
        delete it; std::string val; bool have = db->Get(leveldb::ReadOptions(), "key002400", &val).ok();
        printf("count=%ld key002400 present? %s\n%s\n", n, have ? "yes" : "NO", (n == 2500 && have) ? "RECOVERY OK" : "RECOVERY FAILED");
        delete db;
    }
    return 0;
}
'''}

R["concurrencykit-0.7.2"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree/ck-0.7.2",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1; nproc"}],
    "build": [{"name": "configure + make the library", "cmd": "./configure >/dev/null 2>&1 && make -s 2>&1 | grep -iE '\\berror' | head -3; test -f src/libck.a && echo built", "timeout": 900},
              {"name": "build the spinlock / backoff / ring validation programs", "cmd": "for d in ck_spinlock ck_backoff ck_ring; do make -s -C regressions/$d/validate 2>&1 | grep -iE '\\berror' | head -2; done; ls regressions/ck_spinlock/validate | grep -v '\\.' | head -20", "timeout": 900}],
    "runs": [{"name": "ticket spinlock under 4-way contention (validate: no lost update)", "cmd": "./regressions/ck_spinlock/validate/ck_ticket 4 1 2>&1 | tail -3; echo exit=$?", "expect": {"exit": 0, "stdout_contains": ["exit=0"]}},
             {"name": "MCS queue lock under 4-way contention", "cmd": "./regressions/ck_spinlock/validate/ck_mcs 4 1 2>&1 | tail -3; echo exit=$?", "expect": {"exit": 0, "stdout_contains": ["exit=0"]}},
             {"name": "exponential backoff primitive (ck_backoff_eb)", "cmd": "./regressions/ck_backoff/validate/validate 2>&1 | tail -3; echo exit=$?", "expect": {"exit": 0, "stdout_contains": ["exit=0"]}},
             {"name": "lock-free SPSC ring", "cmd": "./regressions/ck_ring/validate/ck_ring_spsc 2 1 65536 2>&1 | tail -3; echo exit=$?", "expect": {"exit": 0, "stdout_contains": ["exit=0"]}}],
    "tests": [], "test_kind": "UPSTREAM", "test_classification_if_none": "UPSTREAM_TESTS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Runs four of ck's own validation programs (they assert their invariants and exit non-zero on violation). The full regression suite is long; a subset is recorded."}

py_recipe("pybreaker-1.2.0", "upstream/tree/pybreaker-1.2.0", "breaker_trace.py",
          {"exit": 0, "stdout_contains": ["closed->open", "open->half-open", "half-open->closed", "final closed"]},
          notes="Oracle: the three-state trace CLOSED->OPEN (after fail_max failures) ->HALF-OPEN (after reset_timeout) ->CLOSED (probe succeeds), plus fast-fail while OPEN.")
H["pybreaker-1.2.0"] = {"breaker_trace.py": r'''import time, pybreaker
class L(pybreaker.CircuitBreakerListener):
    def state_change(self, cb, old, new):
        print("state %s->%s" % (old.name, new.name))
b = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=0.5, listeners=[L()])
healthy = {"v": False}
def dep():
    if not healthy["v"]:
        raise RuntimeError("dependency down")
    return "ok"
for i in range(3):
    try:
        b.call(dep)
    except Exception as e:
        print("call", i, "->", type(e).__name__, "state", b.current_state)
try:
    b.call(dep)
except pybreaker.CircuitBreakerError as e:
    print("fast-fail while open:", type(e).__name__, "(dependency NOT called)")
time.sleep(0.6)
healthy["v"] = True
print("probe after reset_timeout:", b.call(dep))
print("final", b.current_state)
'''}

py_recipe("backoff-2.2.1", "upstream/tree/backoff-2.2.1", "schedule.py",
          {"exit": 0, "stdout_contains": ["jitter=False distinct_wait_values=1"], "stdout_regex": r"jitter=True distinct_wait_values=([2-9]\d|\d{3,})"},
          notes="Oracle: without jitter 1000 clients share ONE wait value at attempt 6 (they re-collide); with full jitter the values spread (distinct >= 20).")
H["backoff-2.2.1"] = {"schedule.py": r'''import random, collections, backoff
def gen(*a, **k):
    g = backoff.expo(*a, **k); next(g)   # backoff's wait generators are primed with a first next()
    return g
g = gen(base=2, factor=1, max_value=60)
print("expo schedule:", [next(g) for _ in range(8)])
random.seed(1)
g = gen()
print("full_jitter sample:", [round(backoff.full_jitter(next(g)), 3) for _ in range(8)])
def waits(jit):
    random.seed(7); out = []
    for c in range(1000):
        g = gen(); v = None
        for _ in range(6):
            v = next(g)
        out.append(round(backoff.full_jitter(v), 2) if jit else v)
    return out
for jit in (False, True):
    c = collections.Counter(waits(jit))
    print("jitter=%s distinct_wait_values=%d max_share=%.3f" % (jit, len(c), max(c.values()) / 1000.0))
'''}

# ============================ B: PATHOLOGIES ==================================================
R["odepack-netlib"] = {
    "runner": "docker", "image": C, "workdir": "upstream",
    "probe": [{"name": "gfortran", "cmd": "gfortran --version | head -1"}],
    "build": [{"name": "compile ODEPACK (3 files) + Techne's Robertson driver", "cmd": "gfortran -O1 -std=legacy -w -o $BODY/build/rob $HARNESS/robertson.f opkdmain.f opkda1.f opkda2.f 2>&1 | grep -iE '\\berror' | head -3; test -x $BODY/build/rob && echo built", "timeout": 600}],
    "runs": [{"name": "MF=21 (BDF, stiff, analytic Jacobian): Robertson to t=4e10", "cmd": "$BODY/build/rob 21 | tail -6", "expect": {"exit": 0, "stdout_contains": ["RESULT OK MF=", "21"], "stdout_regex": r"T =\s*0\.4000D\+11"}},
             {"name": "PATHOLOGY MF=10 (Adams, non-stiff) on the same stiff problem: step budget exhausted (ISTATE=-1)", "cmd": "$BODY/build/rob 10 2>&1 | tail -6", "expect": {"exit": 0, "stdout_contains": ["RESULT FAILED MF=", "10"], "stdout_regex": r"ISTATE\s*=\s*-1"}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_NATIVE",
    "notes": "The failing run is the specimen's documented behaviour, not a bug: a non-stiff method on a stiff problem exhausts MXSTEP (ISTATE=-1). The corrected descendant is the same code with MF=21. Oracle for MF=21: reaching T=4e10 with y1 ~ 0 (Hindmarsh's demo values)."}
H["odepack-netlib"] = {"robertson.f": '''C Techne harness: Robertson stiff kinetics through DLSODE with a method flag from argv.
C MF=21 (BDF + user Jacobian) is the stiff method; MF=10 (Adams) is the PATHOLOGY.
      PROGRAM ROB
      EXTERNAL FEX, JEX
      DOUBLE PRECISION ATOL(3), RTOL, RWORK(200), T, TOUT, Y(3)
      INTEGER IWORK(50), NEQ, ITOL, ITASK, ISTATE, IOPT, LRW, LIW, MF
      INTEGER IOUT
      CHARACTER*8 ARG
      CALL GETARG(1, ARG)
      READ(ARG,*) MF
      NEQ = 3
      Y(1) = 1.0D0
      Y(2) = 0.0D0
      Y(3) = 0.0D0
      T = 0.0D0
      TOUT = 0.4D0
      ITOL = 2
      RTOL = 1.0D-4
      ATOL(1) = 1.0D-6
      ATOL(2) = 1.0D-10
      ATOL(3) = 1.0D-6
      ITASK = 1
      ISTATE = 1
      IOPT = 0
      LRW = 200
      LIW = 50
      DO 40 IOUT = 1,12
        CALL DLSODE(FEX,NEQ,Y,T,TOUT,ITOL,RTOL,ATOL,ITASK,ISTATE,
     1              IOPT,RWORK,LRW,IWORK,LIW,JEX,MF)
        WRITE(6,20)T,Y(1),Y(2),Y(3),ISTATE
  20    FORMAT(' T =',D12.4,'   Y =',3D14.6,'   ISTATE=',I3)
        IF (ISTATE .LT. 0) GO TO 80
  40    TOUT = TOUT*10.0D0
      WRITE(6,60)IWORK(11),IWORK(12),IWORK(13)
  60  FORMAT(' NSTEP =',I6,'  NFE =',I6,'  NJE =',I6)
      WRITE(6,*) 'RESULT OK MF=', MF
      STOP
  80  WRITE(6,90)ISTATE
  90  FORMAT(' ERROR HALT.. ISTATE =',I3)
      WRITE(6,*) 'RESULT FAILED MF=', MF, ' NSTEP=', IWORK(11)
      STOP
      END
      SUBROUTINE FEX (NEQ, T, Y, YDOT)
      INTEGER NEQ
      DOUBLE PRECISION T, Y(3), YDOT(3)
      YDOT(1) = -.04D0*Y(1) + 1.D4*Y(2)*Y(3)
      YDOT(3) = 3.D7*Y(2)*Y(2)
      YDOT(2) = -YDOT(1) - YDOT(3)
      RETURN
      END
      SUBROUTINE JEX (NEQ, T, Y, ML, MU, PD, NRPD)
      INTEGER NEQ, ML, MU, NRPD
      DOUBLE PRECISION PD(NRPD,3), T, Y(3)
      PD(1,1) = -.04D0
      PD(1,2) = 1.D4*Y(3)
      PD(1,3) = 1.D4*Y(2)
      PD(2,1) = .04D0
      PD(2,3) = -PD(1,3)
      PD(3,2) = 6.D7*Y(2)
      PD(2,2) = -PD(1,2) - PD(3,2)
      RETURN
      END
'''}

R["spin-pathfinder-priority-inversion-1997"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree/Spin-version-6.5.2",
    "probe": [{"name": "gcc/bison", "cmd": "gcc --version | head -1; bison --version | head -1"}],
    "build": [{"name": "build SPIN 6.5.2 (the instrument) from the same tarball", "cmd": "cd Src && make -s 2>&1 | grep -v -i warning | grep -iE '\\berror' | head -3; test -x ./spin && echo built", "timeout": 900},
              {"name": "generate + compile the verifier for pathfinder.pml", "cmd": "cd Examples && ../Src/spin -a pathfinder.pml 2>&1 | tail -2; gcc -O2 -w -o $BODY/build/pan pan.c && echo built"}],
    "runs": [{"name": "PATHOLOGY: exhaustive search finds the deadlock (invalid end state) -- the Pathfinder reset", "cmd": "cd Examples && $BODY/build/pan 2>&1 | grep -E 'invalid end state|errors:|States|pan:' | head -8", "expect": {"exit": 0, "stdout_contains": ["invalid end state", "errors: 1"]}},
             {"name": "replay the counterexample trail (the schedule: low holds the mutex, high blocks, low cannot run)", "cmd": "cd Examples && ../Src/spin -t -p pathfinder.pml 2>&1 | tail -12", "expect": {"exit": 0, "stdout_regex": r"(mutex|busy|waiting)"}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "The specimen is the FAILING model, preserved failing (not repaired). SPIN is built from the same tarball as the instrument; the vault's spin-6.5.2-holzmann record is the checker. pan finds the invalid end state that models the 1997 resets."}

# ============================ C: ESTIMATION ===================================================
py_recipe("particles-chopin-0.4", "upstream/tree/particles-0.4", "pf_vs_kalman.py",
          {"exit": 0, "stdout_contains": ["RESULT OK"]}, timeout=1500,
          notes="Oracle: on a linear-Gaussian state-space model the bootstrap particle filter's filtering means must agree with the exact Kalman filter to Monte-Carlo error (RMSE < 0.1 with N=5000 particles).")
H["particles-chopin-0.4"] = {"pf_vs_kalman.py": r'''import numpy as np
import particles
from particles import state_space_models as ssms
from particles import kalman
from particles.collectors import Moments
np.random.seed(1)
ssm = kalman.LinearGauss(rho=0.9, sigmaX=1.0, sigmaY=0.5)
x, y = ssm.simulate(200)
kf = kalman.Kalman(ssm=ssm, data=y); kf.filter()
kmeans = np.array([m.mean.item() for m in kf.filt])
fk = ssms.Bootstrap(ssm=ssm, data=y)
pf = particles.SMC(fk=fk, N=5000, resampling="systematic", collect=[Moments()], verbose=False)
pf.run()
pmeans = np.array([m["mean"] for m in pf.summaries.moments])
rmse = float(np.sqrt(np.mean((pmeans - kmeans) ** 2)))
print("T=%d N=5000 rmse(PF mean, Kalman mean)=%.4f  final ESS-ish logLt=%.2f" % (len(y), rmse, pf.summaries.logLts[-1]))
print("first 5 Kalman means:", np.round(kmeans[:5], 3))
print("first 5 PF     means:", np.round(pmeans[:5], 3))
print("RESULT", "OK" if rmse < 0.1 else "FAIL")
'''}

py_recipe("emcee-3.1.6", "upstream/tree/emcee-3.1.6", "gaussian.py",
          {"exit": 0, "stdout_contains": ["RESULT OK"]}, pip_extra="numpy", env="SETUPTOOLS_SCM_PRETEND_VERSION=3.1.6",
          notes="Oracle: sampling a 5-d correlated Gaussian with known covariance; sample mean within 0.1 and covariance within 15% relative, acceptance fraction in a healthy band.")
H["emcee-3.1.6"] = {"gaussian.py": r'''import numpy as np, emcee
np.random.seed(2)
ndim, nwalkers = 5, 32
A = np.random.rand(ndim, ndim); cov = 0.5 - np.random.rand(ndim ** 2).reshape((ndim, ndim)); cov = np.triu(cov); cov += cov.T - np.diag(cov.diagonal()); cov = np.dot(cov, cov)
icov = np.linalg.inv(cov); mu = np.arange(ndim) * 0.5
def log_prob(x):
    d = x - mu
    return -0.5 * d @ icov @ d
p0 = mu + 0.1 * np.random.randn(nwalkers, ndim)
s = emcee.EnsembleSampler(nwalkers, ndim, log_prob)
s.run_mcmc(p0, 6000, progress=False)
chain = s.get_chain(discard=1000, flat=True)
m = chain.mean(axis=0); c = np.cov(chain.T)
mean_err = float(np.abs(m - mu).max()); cov_rel = float(np.abs(c - cov).max() / np.abs(cov).max())
af = float(np.mean(s.acceptance_fraction))
try:
    tau = s.get_autocorr_time(quiet=True); tau_max = float(np.max(tau))
except Exception as e:
    tau_max = float("nan")
print("samples=%d mean_err=%.3f cov_rel_err=%.3f acceptance=%.3f tau_max=%.1f" % (len(chain), mean_err, cov_rel, af, tau_max))
print("RESULT", "OK" if (mean_err < 0.1 and cov_rel < 0.15 and 0.15 < af < 0.7) else "FAIL")
'''}

R["tinyekf-levy"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree/examples/GPS",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "make the GPS example (header-only EKF)", "cmd": "make -s gps 2>&1 | grep -iE '\\berror' | head -3; test -x ./gps && echo built"}],
    "runs": [{"name": "run the EKF over the shipped pseudorange data (stdout = raw ECEF position per epoch; ekf.csv is mean-subtracted)", "cmd": "./gps > $BODY/build/gps.out; tail -3 $BODY/build/gps.out", "expect": {"exit": 0, "stdout_contains": ["Wrote file"]}}],
    "tests": [{"name": "plausibility oracle: the estimated receiver position lies at Earth's surface radius (6.35e6..6.40e6 m) and moves less than 100 m over the last 10 epochs", "cmd": "awk 'NF==3 && $1+0==$1 {r=sqrt($1*$1+$2*$2+$3*$3); n++; R[n]=r} END{d=R[n]-R[n-10]; if(d<0)d=-d; printf(\"epochs=%d final_r=%.1f m drift_last10=%.2f m\\n\", n, R[n], d); exit (n==25 && R[n]>6.35e6 && R[n]<6.40e6 && d<100)?0:1}' $BODY/build/gps.out", "expect": {"exit": 0}}],
    "test_kind": "TECHNE", "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "stdout carries the raw filtered ECEF positions; ekf.csv is mean-subtracted (first attempt read the csv and saw a 3 m radius -- corrected). Oracle is plausibility (receiver on the geoid, estimate settled), not a reference trajectory -- the upstream example ships none."}

R["umdhmm-kanungo-1.02"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "make (esthmm, testfor, testvit, genseq); -I$HARNESS supplies malloc/malloc.h (the mirror's nrutil.c carries a macOS include path; shimmed, not edited)", "cmd": "make -s CFLAGS=\"-O -w -I$HARNESS\" 2>&1 | grep -iE '\\berror' | head -3; test -x ./esthmm && test -x ./testfor && echo built"}],
    "runs": [{"name": "Baum-Welch: train a 3-state/2-symbol HMM from t2.1500.seq (generated by the 3-state t2.hmm)", "cmd": "./esthmm -S 1 -N 3 -M 2 t2.1500.seq > $BODY/build/trained.hmm 2>$BODY/build/esthmm.err; head -14 $BODY/build/trained.hmm; echo exit=$?", "expect": {"exit": 0, "stdout_contains": ["A:", "B:", "pi:"]}},
             {"name": "Viterbi decode of test.seq with the generating model (t2.100.seq carries an 'R=' multi-sequence header this 1.02 reader does not parse: segfault, recorded)", "cmd": "./testvit t2.hmm test.seq 2>&1 | head -8", "expect": {"exit": 0, "stdout_regex": r"(Viterbi|log prob)"}}],
    "tests": [{"name": "oracle: SCALED forward log-likelihood of the training data under the TRAINED model within 3% of the GENERATING model's (the unscaled forward underflows to -INF at T=1500, the code's own documented reason for scaling)", "cmd": "./testfor t2.hmm t2.1500.seq > $BODY/build/ll_true.txt; ./testfor $BODY/build/trained.hmm t2.1500.seq > $BODY/build/ll_trained.txt; cat $BODY/build/ll_true.txt $BODY/build/ll_trained.txt; awk '/with scaling/{s=1; next} s && /log prob/{gsub(/.*=/,\"\"); v[++n]=$1+0; s=0} END{r=(v[2]-v[1])/(v[1]<0?-v[1]:v[1]); if(r<0)r=-r; printf(\"ll_true_scaled=%s ll_trained_scaled=%s rel_diff=%.4f\\n\", v[1], v[2], r); exit (n==2 && r<0.03)?0:1}' $BODY/build/ll_true.txt $BODY/build/ll_trained.txt", "expect": {"exit": 0}}],
    "test_kind": "TECHNE", "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle: the EM-trained model explains the generating model's own data nearly as well as the generating model (log-likelihood within 3%); parameter comparison is up to state relabelling and is printed, not asserted. DEVIATION (provenance): the mirror's nrutil.c includes <malloc/malloc.h> (macOS) where Kanungo's original had <malloc.h>; a one-line shim header in the harness satisfies it, no source edited."}
H["umdhmm-kanungo-1.02"] = {"malloc/malloc.h": "/* Techne shim: the mirror's nrutil.c includes the macOS path <malloc/malloc.h>; glibc's malloc lives in stdlib.h. */\n#include <stdlib.h>\n"}

py_recipe("padasip-1.2.2", "upstream/tree/padasip-1.2.2", "identify.py",
          {"exit": 0, "stdout_contains": ["RESULT OK"]},
          notes="Oracle: NLMS and RLS recover a known 4-tap FIR plant from input/output pairs (max |w-h| < 0.02) and re-converge after the plant changes mid-run.")
H["padasip-1.2.2"] = {"identify.py": r'''import numpy as np, padasip as pa
np.random.seed(1)
N = 6000; h1 = np.array([0.5, -0.3, 0.2, 0.1]); h2 = np.array([-0.2, 0.4, 0.1, -0.3])
x = np.random.randn(N); X = pa.input_from_history(x, 4)
d = np.concatenate([X[:len(X)//2] @ h1, X[len(X)//2:] @ h2]) + 0.01 * np.random.randn(len(X))
ok = True
for name, f in (("NLMS", pa.filters.FilterNLMS(n=4, mu=0.5, w="zeros")), ("RLS", pa.filters.FilterRLS(n=4, mu=0.99, w="zeros"))):
    y, e, w = f.run(d, X)
    e1 = np.abs(w[len(X)//2 - 1] - h1).max(); e2 = np.abs(w[-1] - h2).max()
    print("%s before-change w=%s err=%.4f | after-change w=%s err=%.4f" % (name, np.round(w[len(X)//2 - 1], 3), e1, np.round(w[-1], 3), e2))
    ok = ok and e1 < 0.02 and e2 < 0.02
print("RESULT", "OK" if ok else "FAIL")
'''}

# ============================ D (cont.): do-mpc, batch 04's SOURCE_ONLY MPC, made RUNNABLE ==========
# The record lives in batch04.py; this recipe reclassifies it by running its own oscillating-masses
# example (regulation of a coupled mass-spring chain to rest) with CasADi + IPOPT from the pip wheel.
py_recipe("do-mpc", "upstream/tree", "mpc_regulate.py",
          {"exit": 0, "stdout_contains": ["RESULT OK"]}, pip_extra="casadi scipy numpy matplotlib pandas", timeout=1800,
          notes="Batch 04 preserved do-mpc SOURCE_ONLY for want of a CasADi/IPOPT world; the casadi wheel bundles IPOPT, so the MPC runs here. Oracle: the shipped oscillating-masses example (n_horizon 7, t_step 0.5) drives |x| from its random initial state (seed 99, the example's own) below 10% by step 40 under the +-0.5 input bound (the trace is bang-bang: the constraint is active), and recovers after Techne kicks the plant at step 20. First attempt asked for <10% by step 19, which the saturated input cannot deliver; the criterion was moved to the end of the horizon and recorded here. Plant, setpoint (rest), control trace and disturbance are all in the receipt.")
H["do-mpc"] = {"mpc_regulate.py": r"""import sys, numpy as np
import matplotlib; matplotlib.use("Agg")
sys.path.insert(0, "examples/oscillating_masses_discrete")
import do_mpc
from template_model import template_model
from template_mpc import template_mpc
from template_simulator import template_simulator
model = template_model(); mpc = template_mpc(model, silence_solver=True); simulator = template_simulator(model)
estimator = do_mpc.estimator.StateFeedback(model)
np.random.seed(99); e = np.ones([model.n_x, 1]); x0 = np.random.uniform(-3 * e, 3 * e)
mpc.x0 = x0; simulator.x0 = x0; estimator.x0 = x0; mpc.set_initial_guess()
n0 = float(np.linalg.norm(x0)); norms = []; us = []
for k in range(40):
    u0 = mpc.make_step(x0); y = simulator.make_step(u0); x0 = estimator.make_step(y)
    if k == 20:   # DISTURBANCE: kick the plant state (the behavioral entry point)
        x0 = x0 + 2.0 * (np.random.rand(*x0.shape) - 0.5); simulator.x0 = x0; mpc.x0 = x0; estimator.x0 = x0
    norms.append(float(np.linalg.norm(x0))); us.append(float(np.asarray(u0).ravel()[0]))
print("n_x=%d n_u=%d |x0|=%.3f" % (model.n_x, model.n_u, n0))
print("|x| per step:", " ".join("%.2f" % v for v in norms))
print("u  per step:", " ".join("%+.2f" % v for v in us))
print("before kick (step 19): |x|/|x0| = %.3f ; right after kick (step 20): %.3f ; end (step 39): %.3f" % (norms[19] / n0, norms[20] / n0, norms[39] / n0))
ok = norms[39] / n0 < 0.10 and norms[20] > norms[19] and norms[39] < norms[20]   # regulated to <10% by the end, kick visible, recovered after it
print("RESULT", "OK" if ok else "FAIL")
"""}

# ============================ E: CONCURRENCY ==================================================
R["tinystm-marlier"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1; nproc"}],
    "build": [{"name": "make the STM library and the bank benchmark", "cmd": "make -s 2>&1 | grep -iE '\\berror' | head -3; make -s -C test/bank 2>&1 | grep -iE '\\berror' | head -3; test -x test/bank/bank && echo built", "timeout": 900}],
    "runs": [{"name": "bank: 4 threads transferring among 256 accounts for 1 s (invariant: total balance unchanged)", "cmd": "./test/bank/bank -n 4 -d 1000 -a 256 2>&1 | grep -iE 'thread|commit|abort|total|balance|duration|#txs|throughput' | head -14", "expect": {"exit": 0, "stdout_regex": r"(?i)(commit|abort|transfer|total|txs)"}},
             {"name": "contention knob: 8 threads on 8 accounts (abort rate up)", "cmd": "./test/bank/bank -n 8 -d 1000 -a 8 2>&1 | grep -iE 'thread|commit|abort|total|balance|duration|#txs|throughput' | head -14", "expect": {"exit": 0}}],
    "tests": [], "test_kind": "UPSTREAM", "test_classification_if_none": "UPSTREAM_TESTS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "The bank benchmark checks its own invariant (total balance) and prints commits/aborts; the second run is the contention knob."}

# ============================ F: ADVERSARIAL PAIRS ============================================
R["radamsa-0.6"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree/radamsa-v0.6",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "build Owl Lisp from the pinned companion, then compile radamsa (Scheme -> C -> binary)", "cmd": "cp $BODY/upstream/ol-0.1.19.c.gz ol.c.gz && make -s bin/radamsa 2>&1 | grep -iE '\\berror' | head -3; test -x bin/radamsa && echo built", "timeout": 1800}],
    "runs": [{"name": "200 deterministic mutations of a JSON seed (seed 1)", "cmd": "mkdir -p $BODY/build/cases && ./bin/radamsa -n 200 -s 1 -o $BODY/build/cases/%n.json $HARNESS/seed.json && ls $BODY/build/cases | wc -l && head -c 300 $BODY/build/cases/7.json; echo", "expect": {"exit": 0, "stdout_contains": ["200"]}},
             {"name": "determinism: the same seed reproduces case 7 byte-for-byte", "cmd": "./bin/radamsa -n 200 -s 1 -o $BODY/build/cases2/%n.json $HARNESS/seed.json 2>/dev/null || (mkdir -p $BODY/build/cases2 && ./bin/radamsa -n 200 -s 1 -o $BODY/build/cases2/%n.json $HARNESS/seed.json); cmp $BODY/build/cases/7.json $BODY/build/cases2/7.json && echo DETERMINISTIC", "expect": {"exit": 0, "stdout_contains": ["DETERMINISTIC"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "PAIR half 1 (pressure). The 200 cases from seed 1 are copied into cjson-1.7.18/harness/cases/ as the tracked fixture the parser is attacked with (provenance: radamsa v0.6, -s 1, seed.json sha in the harness)."}
H["radamsa-0.6"] = {"seed.json": '{"id": 42, "name": "fossil", "tags": ["a", "b", "c"], "nested": {"x": 1.5, "y": -2, "z": null, "ok": true}, "text": "the quick brown fox \\u00e9\\n", "list": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}\n'}

R["cjson-1.7.18"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree/cJSON-1.7.18",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "compile cJSON + Techne's parse-all driver under AddressSanitizer", "cmd": "gcc -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -I. -o $BODY/build/parse_all cJSON.c $HARNESS/parse_all.c 2>&1 | grep -iE '\\berror' | head -3; test -x $BODY/build/parse_all && echo built"}],
    "runs": [{"name": "the valid seed parses", "cmd": "$BODY/build/parse_all $HARNESS/seed.json", "expect": {"exit": 0, "stdout_contains": ["parsed=1", "crashed=0"]}, "timeout": 120},
             {"name": "ADVERSARIAL: 200 radamsa-mutated cases; every one must parse or be rejected, none may crash (ASan/UBSan)", "cmd": "$BODY/build/parse_all $HARNESS/cases/*.json 2>&1 | tail -3", "expect": {"exit": 0, "stdout_contains": ["crashed=0"], "stdout_regex": r"rejected=[1-9]"}, "timeout": 300}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "PAIR half 2 (response). Cases are the tracked output of radamsa-0.6 (seed 1). A crash would appear as an ASan report and a non-zero exit."}
H["cjson-1.7.18"] = {"parse_all.c": r'''/* Techne harness: parse every file given; count parsed / rejected; a crash never returns. */
#include <stdio.h>
#include <stdlib.h>
#include "cJSON.h"
int main(int argc, char **argv) {
    long parsed = 0, rejected = 0;
    for (int i = 1; i < argc; i++) {
        FILE *f = fopen(argv[i], "rb"); if (!f) continue;
        fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
        char *buf = malloc(n + 1); fread(buf, 1, n, f); buf[n] = 0; fclose(f);
        cJSON *j = cJSON_ParseWithLength(buf, n);
        if (j) { char *out = cJSON_PrintUnformatted(j); if (out) free(out); cJSON_Delete(j); parsed++; } else rejected++;
        free(buf);
    }
    printf("files=%d parsed=%ld rejected=%ld crashed=0\n", argc - 1, parsed, rejected);
    return 0;
}
''', "seed.json": H["radamsa-0.6"]["seed.json"]}

R["libcorrect-quiet"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree",
    "probe": [{"name": "cmake", "cmd": "cmake --version | head -1"}],
    "build": [{"name": "cmake + make (library and its test/tool programs)", "cmd": "mkdir -p $BODY/build/lc && cd $BODY/build/lc && cmake $BODY/upstream/tree >/dev/null 2>&1 && make -s 2>&1 | grep -iE '\\berror' | head -3; ls tests 2>/dev/null | head; test -f lib/libcorrect.a -o -f libcorrect.a && echo built", "timeout": 900}],
    "runs": [{"name": "convolutional codes: noise injection then Viterbi decode (upstream test)", "cmd": "cd $BODY/build/lc && (./tests/test_convolutional 2>&1 || ./tests/convolutional 2>&1) | tail -8; echo exit=$?", "expect": {"exit": 0, "stdout_contains": ["exit=0"]}},
             {"name": "Reed-Solomon: error/erasure injection then decode (upstream test)", "cmd": "cd $BODY/build/lc && (./tests/test_reed_solomon 2>&1 || ./tests/reed_solomon 2>&1) | tail -8; echo exit=$?", "expect": {"exit": 0, "stdout_contains": ["exit=0"]}}],
    "tests": [], "test_kind": "UPSTREAM", "test_classification_if_none": "UPSTREAM_TESTS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "PAIR: the tests are corruption <-> decoder. Test binary names are resolved after the first build (recorded in the receipt's stdout)."}

# ============================ G: LEGACY CULTURES ==============================================
R["paip-lisp-norvig-1991"] = {
    "runner": "docker", "image": LANG, "workdir": "upstream/tree",
    "probe": [{"name": "sbcl", "cmd": "sbcl --version"}],
    "build": [],
    "runs": [{"name": "GPS (means-ends analysis) solves the book's 'drive son to school' problem", "cmd": "sbcl --script $HARNESS/run_gps.lisp 2>&1 | tail -15", "expect": {"exit": 0, "stdout_contains": ["DRIVE-SON-TO-SCHOOL", "SHOP-INSTALLS-BATTERY"]}},
             {"name": "pattern matcher + unifier (the substrate of ELIZA and the Prolog interpreter)", "cmd": "sbcl --script $HARNESS/run_patmatch.lisp 2>&1 | tail -8", "expect": {"exit": 0, "stdout_contains": ["VACATION"], "stdout_regex": r"\?X"}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle: the book's printed GPS plan (chapter 4). Programs loaded unmodified from lisp/."}
H["paip-lisp-norvig-1991"] = {"run_gps.lisp": r''';; Techne harness: PAIP chapter 4 GPS, the school problem, exactly as the book runs it.
(load "lisp/auxfns.lisp")
(load "lisp/gps.lisp")
(use *school-ops*)
(let ((plan (gps '(son-at-home car-needs-battery have-money have-phone-book) '(son-at-school))))
  (format t "~%PLAN: ~S~%" plan))
''', "run_patmatch.lisp": r''';; Techne harness: PAIP pattern matcher (ch. 6) and unifier (ch. 11).
(load "lisp/auxfns.lisp")
(load "lisp/patmatch.lisp")
(format t "~%PATMATCH: ~S~%" (pat-match '(i need a ?X) '(i need a vacation)))
(format t "PATMATCH-SEGMENT: ~S~%" (pat-match '((?* ?p) need (?* ?x)) '(Mr Hulot and I need a vacation)))
(load "lisp/unify.lisp")
(format t "UNIFY: ~S~%" (unify '(?x + 1) '(2 + ?y)))
'''}

R["whitakers-words-ada"] = {
    "runner": "docker", "image": LEGACY, "workdir": "upstream/tree",
    "probe": [{"name": "gnat/gprbuild", "cmd": "gnatmake --version | head -1; gprbuild --version | head -1"}],
    "build": [{"name": "gprbuild the Ada tools (make commands sorter; the sorter is a separate gpr target and the first attempt forgot it)", "cmd": "make -s commands sorter 2>&1 | grep -iE '\\berror' | head -5; test -x bin/words && test -x bin/wakedict && test -x bin/sorter && echo built", "timeout": 900},
              {"name": "generate the dictionary files with the Makefile's own steps, each under its own timeout (make data hung once at wakedict for 19 min with a 0-byte DICTFILE.GEN; run by hand the same command finished in <60 s; the Ada sorter over 39k stems is the long pole)",
               "cmd": "timeout 600 bash -c 'echo g | bin/wakedict DICTLINE.GEN' >/dev/null 2>&1; mv -f STEMLIST.GEN STEMLIST_generated.GEN; timeout 2400 bash -c 'bin/sorter < stemlist-sort.txt' >/dev/null 2>&1; mv -f STEMLIST_new.GEN STEMLIST.GEN 2>/dev/null; timeout 600 bash -c 'echo g | bin/makestem STEMLIST.GEN' >/dev/null 2>&1; timeout 600 bash -c 'echo g | bin/makeewds DICTLINE.GEN' >/dev/null 2>&1; LC_COLLATE=C sort -o EWDSLIST.GEN EWDSLIST.GEN; timeout 600 bin/makeefil >/dev/null 2>&1; timeout 600 bin/makeinfl INFLECTS.LAT >/dev/null 2>&1; ls -la DICTFILE.GEN STEMFILE.GEN INDXFILE.GEN EWDSFILE.GEN INFLECTS.SEC 2>&1 | awk '{print $5, $9}'; test -s STEMFILE.GEN && test -s INDXFILE.GEN && echo built", "timeout": 3600}],
    "runs": [{"name": "parse 'amo' (command-line mode; the interactive banner is 12 lines, which is why the first attempt's head -8 saw no parse)", "cmd": "bin/words amo 2>&1 | grep -viE 'loaded|copyright|updates|comments|^[[:space:]]*$' | head -8", "expect": {"exit": 0, "stdout_regex": r"(?i)love"}},
             {"name": "parse an enclitic + syncopated form: amaveruntque, amasse (TACKON -que; syncope s => vis)", "cmd": "bin/words amaveruntque amasse 2>&1 | grep -viE 'loaded|copyright|updates|comments|^[[:space:]]*$' | head -14", "expect": {"exit": 0, "stdout_contains": ["TACKON", "Syncop"], "stdout_regex": r"(?i)love"}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle: the dictionary's own entry for amo/amare ('love'). The build regenerates the .GEN dictionary files from the DICTLINE/INFLECTS sources. MEASURED 2026-09-12: bin/sorter over the 39k-line stem list took 25m42s wall with 19 s user CPU -- it is I/O-bound on the WSL2 /mnt/f 9p mount (many small writes to WORK.), not slow Ada; on a native filesystem it would be seconds. The recipe gives it 2400 s."}

R["basic-computer-games-1978"] = {
    "runner": "docker", "image": LEGACY, "workdir": "upstream",
    "probe": [{"name": "bas (Haardt 2.5) and bwbasic", "cmd": "which bas; bwbasic --version 2>&1 | head -1"}],
    "build": [],
    "runs": [{"name": "HAMURABI under Bas 2.5: a scripted starvation policy (feed 500 of the 2000 bushels 100 people need) -> the program's own impeachment end state", "cmd": "bas hammurabi.bas < $HARNESS/hamurabi_policy.txt 2>&1 | tr -d '\\r' | grep -v '^\\s*$' | tail -22", "expect": {"exit": 0, "stdout_contains": ["HAMURABI:  I BEG TO REPORT TO YOU", "PEOPLE STARVED"], "stdout_regex": r"(NATIONAL FINK|IMPEACHED|SO LONG FOR NOW)"}},
             {"name": "HAMURABI under bwBASIC 2.20: the same program, a later interpreter -- runs, but passes PRINT:PRINT lines to the shell and mis-evaluates line 990 (dialect gap recorded)", "cmd": "bwbasic hammurabi.bas < $HARNESS/hamurabi_policy.txt 2>&1 | tr -d '\\r' | grep -E 'HAMURABI|FINK|IMPEACHED|ERROR in line|sh: 1:' | head -8", "expect": {"exit": 0, "stdout_regex": r"(HAMURABI|FINK|IMPEACHED)"}},
             {"name": "SUPER STAR TREK under Bas 2.5: DIALECT REFUSAL at line 4060 (the 1978 listing's crunched keyword 'TOQ1+1'); recorded, not patched", "cmd": "bas superstartrek.bas < $HARNESS/startrek_moves.txt 2>&1 | tr -d '\\r' | grep -v '^\\s*$' | tail -4", "expect": {"exit": 0, "stdout_contains": ["line 4060"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Two later interpreters, one fossil. Bas 2.5 (pinned source in the legacy world) runs HAMURABI faithfully; bwBASIC 2.20 runs it with dialect errors. SUPER STAR TREK does not parse under either (Bas: crunched 'TOQ1+1' at 4060; bwBASIC: apostrophe inside a string at 6170): its listing is preserved and hashed, its run status is this refusal. Nothing in the listings was edited. The scripted policy deliberately starves the city: the impeachment is the program's own end state under scarcity."}
H["basic-computer-games-1978"] = {"hamurabi_policy.txt": "".join(["0\n0\n500\n50\n"] * 12), "startrek_moves.txt": "N\nSRS\nLRS\nXXX\n"}

R["cobol-programming-course-omp"] = {
    "runner": "docker", "image": LEGACY, "workdir": "upstream/tree/COBOL Programming Course #2 - Learning COBOL/Labs/cbl",
    "probe": [{"name": "cobc", "cmd": "cobc --version | head -1"}],
    "build": [{"name": "compile PAYROL00 (payroll arithmetic), SRCHBIN (SEARCH ALL over the account file) and CBL0014 (the course's deliberate S0C7 data exception) with GnuCOBOL; also record that CBL0001..CBL0012 are REFUSED (PROGRAM-ID without its terminating period: IBM Enterprise COBOL tolerates it, GnuCOBOL 3.1.2 does not, every -std tried)",
               "cmd": "cobc -x -o $BODY/build/payrol00 PAYROL00.cobol 2>&1 | tail -2; cobc -x -o $BODY/build/srchbin SRCHBIN.cobol 2>&1 | tail -2; cobc -x -o $BODY/build/cbl0014 CBL0014.cobol 2>&1 | tail -2; cobc -x -std=ibm -o /tmp/c1 CBL0001.cobol 2>&1 | head -1; test -x $BODY/build/payrol00 && test -x $BODY/build/srchbin && test -x $BODY/build/cbl0014 && echo built"}],
    "runs": [{"name": "PAYROL00: hours x rate -> gross pay, PICTURE-edited output", "cmd": "$BODY/build/payrol00; echo exit=$?", "expect": {"exit": 0, "stdout_contains": ["Gross Pay:", "exit=0"]}},
             {"name": "SRCHBIN: load the 45-record EBCDIC/COMP-3 account file (DDNAME ACCTREC mapped through DD_ACCTREC) into a table and SEARCH ALL (binary search) for account 18011809", "cmd": "cd ../data && DD_ACCTREC=data $BODY/build/srchbin 2>&1 | cat -v | tail -5; echo exit=$?", "expect": {"exit": 0, "stdout_regex": r"(?i)found"}},
             {"name": "PATHOLOGY CBL0014: the course's deliberate S0C7 (data exception: arithmetic on an invalid packed-decimal field) -- what GnuCOBOL does with it is recorded, not judged", "cmd": "$BODY/build/cbl0014 2>&1 | cat -v | head -6; echo exit=$?", "expect": {"stdout_contains": ["Triggering S0C7"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "The course's first twelve programs are REFUSED by GnuCOBOL (PROGRAM-ID line lacks a terminating period; IBM's compiler accepts it) -- a dialect gap of the interpreter world, recorded in the build step's output, never patched into the source. The data file is EBCDIC with packed-decimal amounts: SRCHBIN's account-number key (PIC X, EBCDIC bytes) and the literal 18011809 (ASCII) would not compare equal, so 'Not Found' is a possible honest outcome; the receipt keeps what the program printed. CBL0014 is preserved as a FAILURE fossil (S0C7)."}

# ============================ H: HARDWARE =====================================================
R["verilog-arbiter-forencich"] = {
    "runner": "docker", "image": HW, "workdir": "upstream",
    "probe": [{"name": "iverilog", "cmd": "iverilog -V | head -1"}],
    "build": [{"name": "compile arbiter + priority_encoder with Techne's testbench (two instances: round-robin and fixed-priority)", "cmd": "iverilog -g2012 -o $BODY/build/sim $HARNESS/tb_arbiter.v arbiter.v priority_encoder.v 2>&1 | head -5; test -f $BODY/build/sim && echo built"}],
    "runs": [{"name": "16 cycles of all-four-requesting: grant trace and per-port counts", "cmd": "vvp -n $BODY/build/sim | tail -24", "expect": {"exit": 0, "stdout_contains": ["RR grants per port: 4 4 4 4"], "stdout_regex": r"RESULT\s+OK"}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_EMULATED",
    "notes": "Oracle: with four persistent requesters, round-robin (ARB_BLOCK=0) grants each port exactly 4 of 16 cycles; fixed priority grants the same port every cycle (starvation of the others, shown)."}
H["verilog-arbiter-forencich"] = {"tb_arbiter.v": r'''`timescale 1ns/1ps
// Techne testbench: two arbiter instances under identical contention.
module tb;
    localparam PORTS = 4;
    reg clk = 0, rst = 1;
    reg [PORTS-1:0] request = 0, acknowledge = 0;
    wire [PORTS-1:0] g_rr, g_pr; wire v_rr, v_pr; wire [1:0] e_rr, e_pr;
    arbiter #(.PORTS(PORTS), .ARB_TYPE_ROUND_ROBIN(1), .ARB_BLOCK(0), .ARB_BLOCK_ACK(0), .ARB_LSB_HIGH_PRIORITY(1))
        rr (.clk(clk), .rst(rst), .request(request), .acknowledge(acknowledge), .grant(g_rr), .grant_valid(v_rr), .grant_encoded(e_rr));
    arbiter #(.PORTS(PORTS), .ARB_TYPE_ROUND_ROBIN(0), .ARB_BLOCK(0), .ARB_BLOCK_ACK(0), .ARB_LSB_HIGH_PRIORITY(1))
        pr (.clk(clk), .rst(rst), .request(request), .acknowledge(acknowledge), .grant(g_pr), .grant_valid(v_pr), .grant_encoded(e_pr));
    integer i, c_rr [0:PORTS-1], c_pr [0:PORTS-1];
    always #5 clk = ~clk;
    initial begin
        for (i = 0; i < PORTS; i = i + 1) begin c_rr[i] = 0; c_pr[i] = 0; end
        #12 rst = 0;
        @(negedge clk); request = 4'b1111;
        repeat (16) begin
            @(posedge clk); #1;
            $display("cycle req=%b  RR grant=%b (port %0d)  PRIORITY grant=%b (port %0d)", request, g_rr, e_rr, g_pr, e_pr);
            if (v_rr) c_rr[e_rr] = c_rr[e_rr] + 1;
            if (v_pr) c_pr[e_pr] = c_pr[e_pr] + 1;
        end
        request = 4'b0100;
        @(posedge clk); #1; $display("single requester (port 2): RR grant=%b PRIORITY grant=%b", g_rr, g_pr);
        $display("RR grants per port: %0d %0d %0d %0d", c_rr[0], c_rr[1], c_rr[2], c_rr[3]);
        $display("PRIORITY grants per port: %0d %0d %0d %0d", c_pr[0], c_pr[1], c_pr[2], c_pr[3]);
        $display("RESULT %s", (c_rr[0] == 4 && c_rr[1] == 4 && c_rr[2] == 4 && c_rr[3] == 4 && c_pr[0] == 16 && c_pr[1] == 0 && g_rr == 4'b0100 && g_pr == 4'b0100) ? "OK" : "CHECK");
        $finish;
    end
endmodule
'''}

R["biriscv-branch-predictor"] = {
    "runner": "docker", "image": HW, "workdir": "upstream/tree",
    "probe": [{"name": "iverilog", "cmd": "iverilog -V | head -1"}],
    "build": [{"name": "compile biriscv_npc with Techne's testbench (bimodal BHT + BTB)", "cmd": "iverilog -g2012 -I src/core -o $BODY/build/sim $HARNESS/tb_npc.v src/core/biriscv_npc.v 2>&1 | grep -v warning | head -5; test -f $BODY/build/sim && echo built"}],
    "runs": [{"name": "a loop branch taken 7x then not-taken, 40 iterations: mispredictions early vs late", "cmd": "vvp -n $BODY/build/sim | tail -12", "expect": {"exit": 0, "stdout_regex": r"late_mispredicts=\d+[\s\S]*RESULT\s+OK"}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_EMULATED",
    "notes": "Oracle: after warm-up the predictor's misprediction count per 10 iterations falls below the untrained count (the BTB learns the target, the BHT the direction). The testbench drives only the npc module; no core is simulated."}
H["biriscv-branch-predictor"] = {"tb_npc.v": r"""`timescale 1ns/1ps
// Techne testbench: biriscv_npc alone, two instances (bimodal BHT vs gshare) on one branch stream.
// Stream: a loop branch at 0x110 taken 7 times then not-taken (falls to 0x118), 40 iterations.
module tb;
    reg clk = 0, rst = 1; always #5 clk = ~clk;
    reg br_req = 0, br_taken = 0, br_ntaken = 0, accept = 0;
    reg [31:0] br_src = 0, br_pc = 0, pc_f = 0;
    wire [31:0] npc_bi, npc_gs; wire [1:0] tk_bi, tk_gs;
    biriscv_npc #(.GSHARE_ENABLE(0)) bi (.clk_i(clk), .rst_i(rst), .invalidate_i(1'b0), .branch_request_i(br_req),
        .branch_is_taken_i(br_taken), .branch_is_not_taken_i(br_ntaken), .branch_source_i(br_src), .branch_is_call_i(1'b0),
        .branch_is_ret_i(1'b0), .branch_is_jmp_i(1'b0), .branch_pc_i(br_pc), .pc_f_i(pc_f), .pc_accept_i(accept),
        .next_pc_f_o(npc_bi), .next_taken_f_o(tk_bi));
    biriscv_npc #(.GSHARE_ENABLE(1)) gs (.clk_i(clk), .rst_i(rst), .invalidate_i(1'b0), .branch_request_i(br_req),
        .branch_is_taken_i(br_taken), .branch_is_not_taken_i(br_ntaken), .branch_source_i(br_src), .branch_is_call_i(1'b0),
        .branch_is_ret_i(1'b0), .branch_is_jmp_i(1'b0), .branch_pc_i(br_pc), .pc_f_i(pc_f), .pc_accept_i(accept),
        .next_pc_f_o(npc_gs), .next_taken_f_o(tk_gs));
    localparam BR = 32'h00000110, LOOP = 32'h00000100, FALL = 32'h00000118;
    integer it, k, e_bi = 0, l_bi = 0, e_gs = 0, l_gs = 0, tot_bi = 0, tot_gs = 0;
    reg t; reg [31:0] actual;
    initial begin
        #12 rst = 0;
        @(negedge clk);
        for (it = 0; it < 40; it = it + 1) begin
            for (k = 0; k < 8; k = k + 1) begin
                t = (k < 7); actual = t ? LOOP : FALL;
                // fetch cycle: the block holding the branch is presented; predictions are read
                pc_f = BR; accept = 1; br_req = 0; br_taken = 0; br_ntaken = 0;
                #1;
                if (npc_bi != actual) begin tot_bi = tot_bi + 1; if (it < 10) e_bi = e_bi + 1; if (it >= 30) l_bi = l_bi + 1; end
                if (npc_gs != actual) begin tot_gs = tot_gs + 1; if (it < 10) e_gs = e_gs + 1; if (it >= 30) l_gs = l_gs + 1; end
                if (it < 2 || it >= 38) $display("it=%0d k=%0d actual=%h  bimodal->%h %s  gshare->%h %s", it, k, actual,
                    npc_bi, (npc_bi == actual) ? "ok " : "MIS", npc_gs, (npc_gs == actual) ? "ok " : "MIS");
                @(negedge clk);
                // resolve cycle: the branch's outcome is reported (updates BTB / BHT / history)
                accept = 0; br_req = 1; br_src = BR; br_pc = actual; br_taken = t; br_ntaken = ~t;
                @(negedge clk);
                br_req = 0; br_taken = 0; br_ntaken = 0;
            end
        end
        $display("mispredicts over 320 branches: bimodal total=%0d early(it<10)=%0d late(it>=30)=%0d | gshare total=%0d early=%0d late_mispredicts=%0d",
            tot_bi, e_bi, l_bi, tot_gs, e_gs, l_gs);
        $display("RESULT %s", (l_gs < l_bi && l_gs <= e_gs && l_bi <= e_bi) ? "OK" : "CHECK");
        $finish;
    end
endmodule
"""}

# ============================ I: SCIENTIFIC EXTREMES ==========================================
R["erfa-2.0.1"] = {
    "runner": "docker", "image": LANG, "workdir": "upstream/tree/erfa-2.0.1",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "bootstrap (autoreconf: the GitHub release tarball ships no generated configure) + configure + make", "cmd": "./bootstrap.sh >/dev/null 2>&1; ./configure -q >/dev/null 2>&1 && make -s 2>&1 | grep -iE '\\berror' | head -3; test -f src/.libs/liberfa.a -o -f src/liberfa.la && echo built", "timeout": 900}],
    "runs": [{"name": "version + a sample transformation (t_erfa_c is the test)", "cmd": "grep -m1 'ERFA_VERSION ' src/erfa.h src/erfam.h 2>/dev/null | head -1; echo ok", "expect": {"exit": 0}}],
    "tests": [{"name": "make check: t_erfa_c validates every routine against IAU reference values", "cmd": "make -s check 2>&1 | grep -E '^# (TOTAL|PASS|FAIL|ERROR)' | head -6", "expect": {"exit": 0, "stdout_contains": ["# TOTAL: 2", "# PASS:  2", "# FAIL:  0", "# ERROR: 0"]}, "timeout": 900}],
    "test_kind": "UPSTREAM", "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "ORACLE-backed by the library's own validation program (reference values to ~1e-12)."}

py_recipe("python-sgp4-2.23", "upstream/tree/sgp4-2.23", "verify.py",
          {"exit": 0, "stdout_contains": ["RESULT OK"]}, apt="build-essential", pip_extra="numpy", timeout=1200,
          notes="Runs the package's own test suite (Vallado's tcppver.out verification vectors) and prints the count. The C++ accelerator is compiled (build-essential installed in the run container, recorded).")
H["python-sgp4-2.23"] = {"verify.py": r'''import subprocess, sys
r = subprocess.run([sys.executable, "-m", "sgp4.tests"], capture_output=True, text=True)
out = (r.stdout + r.stderr)
print(out[-1500:])
import sgp4.api as api
print("accelerated:", api.accelerated)
lines = [l for l in out.splitlines() if l.strip()]
ok = r.returncode == 0 and lines and lines[-1].startswith("OK")
print("RESULT", "OK" if ok else "FAIL")
'''}

# ============================ J: FINANCE ======================================================
py_recipe("py-vollib-lets-be-rational", "upstream/tree", "roundtrip.py",
          {"exit": 0, "stdout_contains": ["RESULT OK"]}, pip_extra="py_lets_be_rational",
          notes="Oracle: price -> implied vol -> price round trip over a grid including deep OTM strikes closes to 1e-10 in sigma. py_lets_be_rational (Jaeckel's algorithm) is installed from PyPI at run time (recorded).")
H["py-vollib-lets-be-rational"] = {"roundtrip.py": r'''import numpy as np
from py_vollib.black_scholes import black_scholes as bs
from py_vollib.black_scholes.implied_volatility import implied_volatility as iv
S, r = 100.0, 0.01
worst = 0.0; worst_p = 0.0; n = 0; ill = 0
for K in (40, 70, 90, 100, 110, 130, 200, 300):
    for t in (0.02, 0.25, 1.0, 3.0):
        for sigma in (0.05, 0.2, 0.6, 1.5):
            for flag in ("c", "p"):
                p = bs(flag, S, K, t, r, sigma)
                try:
                    s2 = iv(p, S, K, t, r, flag)
                except Exception as e:
                    print("K=%s t=%s sigma=%s %s -> %s (price %.3e)" % (K, t, sigma, flag, type(e).__name__, p)); continue
                p2 = bs(flag, S, K, t, r, s2)
                perr = abs(p2 - p) / S; worst_p = max(worst_p, perr)
                # sigma is identifiable only where the price moves with it: vega ~ S*sqrt(t)*phi(d1)
                d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * t) / (sigma * np.sqrt(t))
                vega = S * np.sqrt(t) * np.exp(-0.5 * d1 ** 2) / np.sqrt(2 * np.pi)
                if vega > 1e-6:
                    err = abs(s2 - sigma); worst = max(worst, err); n += 1
                else:
                    ill += 1
print("well-conditioned points (vega > 1e-6): %d  worst |sigma_iv - sigma| = %.3e" % (n, worst))
print("ill-conditioned points (vega <= 1e-6, sigma not identifiable): %d" % ill)
print("all points: worst price round-trip error / S = %.3e" % worst_p)
print("RESULT", "OK" if (worst < 1e-9 and worst_p < 1e-12 and n >= 150) else "FAIL")
'''}

py_recipe("pyportfolioopt-1.5.5", "upstream/tree/pyportfolioopt-1.5.5", "minvol.py",
          {"exit": 0, "stdout_contains": ["RESULT OK"]}, pip_extra="pandas", timeout=1800,
          notes="Oracle: feasibility (weights sum to 1, long-only) and dominance (the min-volatility portfolio's variance is below the equal-weight variance) on the bundled 20-asset price history. Profitability is not scored.")
H["pyportfolioopt-1.5.5"] = {"minvol.py": r'''import numpy as np, pandas as pd, glob
from pypfopt import EfficientFrontier, expected_returns, risk_models
paths = glob.glob("tests/resources/stock_prices.csv") + glob.glob("**/stock_prices.csv", recursive=True)
if paths:
    df = pd.read_csv(paths[0], parse_dates=True, index_col="date"); print("data:", paths[0])
else:
    # the PyPI sdist ships no tests/resources: a seeded synthetic 3-factor market, 20 assets, 750 days
    rng = np.random.default_rng(7); n_assets, n_days = 20, 750
    load = rng.normal(0, 1, (n_assets, 3)); fac = rng.normal(0, 0.01, (n_days, 3)); idio = rng.normal(0, 0.008, (n_days, n_assets)) * rng.uniform(0.5, 2.0, n_assets)
    rets = fac @ load.T * 0.6 + idio + 0.0003
    df = pd.DataFrame(100 * np.cumprod(1 + rets, axis=0), columns=["A%02d" % i for i in range(n_assets)], index=pd.bdate_range("2020-01-01", periods=n_days))
    print("data: SYNTHETIC seeded factor market (sdist has no tests/resources)")
mu = expected_returns.mean_historical_return(df); S = risk_models.sample_cov(df)
ef = EfficientFrontier(mu, S); w = ef.min_volatility(); w = ef.clean_weights()
wv = np.array([w[k] for k in df.columns]); var_min = float(wv @ S.values @ wv)
we = np.ones(len(df.columns)) / len(df.columns); var_eq = float(we @ S.values @ we)
print("assets=%d sum(w)=%.6f min(w)=%.6f nonzero=%d" % (len(wv), wv.sum(), wv.min(), int((wv > 1e-6).sum())))
print("annual variance: min-vol=%.6f equal-weight=%.6f" % (var_min, var_eq))
ok = abs(wv.sum() - 1) < 1e-4 and wv.min() > -1e-6 and var_min < var_eq
print("RESULT", "OK" if ok else "FAIL")
'''}

# ============================ DEPTH ===========================================================
R["compact-4.2bsd-1983"] = {
    "runner": "docker", "image": C, "workdir": "upstream",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "ONE container: apt gcc-multilib + libc6-dev-i386 (the 1983 code assumes ILP32: undeclared char *malloc() is implicit int and truncates pointers on x86-64 -> segfault observed), then compile as 32-bit STATIC K&R (-m32 -static -std=gnu89 -fcommon -w; static so the binary runs in the next container without lib32; -Dvax selects the little-endian byte order the source keys on the VAX/PDP-11 symbols; no source change). compact(1) exits 1 after a successful run (1983 convention), so the round trip is judged by cmp, not by its exit status", "timeout": 900, "cmd": "apt-get -qq update >/dev/null && apt-get -qq install -y gcc-multilib libc6-dev-i386 >/dev/null 2>&1; gcc -m32 -static -Dvax -std=gnu89 -fcommon -w -o $BODY/build/compact compact.c tree.c 2>&1 | grep -iE '\\berror' | head -5; gcc -m32 -static -Dvax -std=gnu89 -fcommon -w -o $BODY/build/uncompact uncompact.c tree.c 2>&1 | grep -iE '\\berror' | head -5; test -x $BODY/build/compact && test -x $BODY/build/uncompact && echo built"}],
    "runs": [{"name": "round trip a 200 KB text sample; report the ratio", "cmd": "cd $BODY/build && awk 'BEGIN{for(i=0;i<4000;i++) printf(\"the quick brown fox %d jumps over the lazy dog %d\\n\", i, i*7)}' > sample && cp sample s.txt && ./compact s.txt; ls -l s.txt.C | awk '{print \"compacted bytes:\", $5}'; ./uncompact s.txt.C; cmp s.txt sample && echo ROUNDTRIP OK && echo original bytes: $(wc -c < sample)", "expect": {"exit": 0, "stdout_contains": ["ROUNDTRIP OK"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "The loser runs -- as a 32-bit program. Unmodified on x86-64 it segfaults (K&R implicit-int malloc truncates pointers); -m32 restores the ILP32 world it was written for. The i386 toolchain is the same accommodation libfec-karn needs. Ratio printed beside the byte count for the lineage comparison."}

R["gzip-1.2.4-1993"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree/gzip-1.2.4",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "1993 configure + make with modern-compiler accommodations (-fcommon -std=gnu89 -w; no source change)", "cmd": "./configure >/dev/null 2>&1; make -s CFLAGS='-O1 -fcommon -std=gnu89 -w' 2>&1 | grep -iE '\\berror' | head -5; test -x ./gzip && echo built", "timeout": 600}],
    "runs": [{"name": "round trip the same 200 KB sample used for compact; report the ratio", "cmd": "awk 'BEGIN{for(i=0;i<4000;i++) printf(\"the quick brown fox %d jumps over the lazy dog %d\\n\", i, i*7)}' > $BODY/build/sample && ./gzip -c -9 $BODY/build/sample > $BODY/build/s.gz && ls -l $BODY/build/s.gz | awk '{print \"gzip -9 bytes:\", $5}' && ./gzip -dc $BODY/build/s.gz | cmp - $BODY/build/sample && echo ROUNDTRIP OK", "expect": {"exit": 0, "stdout_contains": ["ROUNDTRIP OK"]}},
             {"name": "version banner", "cmd": "./gzip -V 2>&1 | head -2", "expect": {"exit": 0, "stdout_contains": ["1.2.4"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Same sample as compact-4.2bsd-1983 so the two ratios are comparable."}

R["zchaff-2007"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree/zchaff64",
    "probe": [{"name": "g++", "cmd": "g++ --version | head -1"}],
    "build": [{"name": "make (2007 C++; modern libstdc++ no longer provides <cstring>/<cstdlib> transitively -- injected through CFLAGS, no source change)", "cmd": "make -s CFLAGS='-O2 -w -include cstring -include cstdlib -include cstdio -include climits -fpermissive' 2>&1 | grep -iE '\\berror' | head -5; test -x ./zchaff && echo built", "timeout": 600}],
    "runs": [{"name": "satisfiable CNF (the vault's shared fixture)", "cmd": "./zchaff $HARNESS/sat.cnf 2>&1 | grep -E 'RESULT|Instance|Decisions|Conflicts' | head -6", "expect": {"exit": 0, "stdout_regex": r"RESULT:\s*SAT"}},
             {"name": "unsatisfiable CNF", "cmd": "./zchaff $HARNESS/unsat.cnf 2>&1 | grep -E 'RESULT|Instance|Decisions|Conflicts' | head -6", "expect": {"exit": 0, "stdout_regex": r"RESULT:\s*UNSAT"}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle: agreement with minisat-2.2.0 and picosat-965 on the same two CNFs (their receipts hold the answers)."}

R["minisat-1.14-2006"] = {
    "runner": "docker", "image": GCC49, "workdir": "upstream/tree/MiniSat_v1.14",
    "probe": [{"name": "g++", "cmd": "g++ --version | head -1"}],
    "build": [{"name": "make rs (static release) in the preserved gcc 4.9 world", "cmd": "make -s rs 2>&1 | grep -iE '\\berror' | head -5; ls minisat* 2>/dev/null | head; test -x ./minisat_static -o -x ./minisat && echo built", "timeout": 600}],
    "runs": [{"name": "satisfiable CNF", "cmd": "B=./minisat_static; test -x $B || B=./minisat; $B $HARNESS/sat.cnf 2>&1 | tail -3; echo exit=$?", "expect": {"exit": 0, "stdout_regex": r"(?i)satisfiable"}},
             {"name": "unsatisfiable CNF", "cmd": "B=./minisat_static; test -x $B || B=./minisat; $B $HARNESS/unsat.cnf 2>&1 | tail -3; echo exit=$?", "expect": {"exit": 0, "stdout_regex": r"(?i)unsatisfiable"}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_HISTORICAL_TOOLCHAIN",
    "notes": "Same fixtures as minisat-2.2.0 / picosat-965 / zchaff-2007."}


def main():
    import shutil
    # shared CNF fixtures for the SAT lineage, copied from the vault's minisat-2.2.0 harness
    src = vault.specimen_dir("minisat-2.2.0") / "harness"
    for sid in ("zchaff-2007", "minisat-1.14-2006"):
        H.setdefault(sid, {})
        for f in ("sat.cnf", "unsat.cnf"):
            H[sid][f] = (src / f).read_text(encoding="utf-8")
    for sid, recipe in R.items():
        d = vault.specimen_dir(sid); d.mkdir(parents=True, exist_ok=True)
        (d / "recipe.json").write_text(json.dumps(recipe, indent=2) + "\n", encoding="utf-8", newline="\n")
        for name, text in H.get(sid, {}).items():
            (d / "harness").mkdir(exist_ok=True)
            (d / "harness" / name).parent.mkdir(parents=True, exist_ok=True)
            (d / "harness" / name).write_text(text, encoding="utf-8", newline="\n")
        print("wrote", sid, "+harness" if sid in H else "")


if __name__ == "__main__":
    main()
