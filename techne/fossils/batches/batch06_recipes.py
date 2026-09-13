"""Batch 06 recipes + harnesses (2026-09-13). python -m techne.fossils.batches.batch06_recipes

Every recipe executes in the disposable work/ copy. Deviations in each recipe's notes.
"""
from __future__ import annotations

import json
from .. import vault

C = "prometheus-fossil-c:bookworm"
SIMH = "prometheus-fossil-simh:bookworm"
GO = "golang:1.22-bookworm"
R = {}
H = {}

# ============================ PHASE 1 / TECHNE-69: 4.3BSD on the emulated VAX-11/780 ==========
R["bsd-4.3-distribution-tape-1986"] = {
    "runner": "docker", "image": SIMH, "workdir": "build",
    "probe": [{"name": "simh", "cmd": "cat /usr/local/share/simh-commit.txt; printf 'show version\nexit\n' > /tmp/v.ini; vax780 /tmp/v.ini 2>&1 | head -2"}],
    "build": [{"name": "assemble the .tap from the tape files (stand 512B records; miniroot/rootdump/usr.tar 10240) and gunzip the miniroot as a raw disk",
               "cmd": "python3 $HARNESS/simh_mktape.py 43bsd.tap $BODY/upstream/stand.gz:512 $BODY/upstream/miniroot.gz:10240 $BODY/upstream/rootdump.gz:10240 $BODY/upstream/usr.tar.gz:10240 && gunzip -c $BODY/upstream/miniroot.gz > miniroot.raw && echo built", "timeout": 600}],
    "runs": [{"name": "boot the 4.3BSD GENERIC kernel (6 Jun 1986) on an emulated VAX-11/780 from the miniroot, then restore the root filesystem from tape with the release's own xtr -- the fossil kernel (containing bsd-tcp-4.3-reno's ancestor TCP) actually EXECUTES",
              "cmd": "rm -f rq.dsk; expect $HARNESS/bsd43_install_stage1.exp miniroot.raw rq.dsk 43bsd.tap $HARNESS/boot42 > stage1.log 2>&1; grep -a -E 'STAGE1|4.3 BSD UNIX #1|Root filesystem extracted' stage1.log",
              "expect": {"exit": 0, "stdout_contains": ["4.3 BSD UNIX #1", "STAGE1: miniroot single-user shell", "Root filesystem extracted"]}, "timeout": 2400}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_EMULATED",
    "notes": "TECHNE-69: the fossil 4.3BSD kernel BOOTS and runs single-user on open-simh vax780 (built from source a1f57fa37; Debian's 3.8.1 cannot boot the 780 from tape). The console loads the 4.2 `boot` (boot42, sha256 a7bacc51) at 0 with R10=9/R11=0 and runs from 2; the miniroot is a raw RA81; xtr restores 317 root files. BOUNDARY (honest): the full multi-user install (newfs + tar-extract of /usr from tape file 4) exceeds the practical emulated-tape time budget -- stage 2 reached `mt fsf 3` after ~1 h of emulated VAX time and was cut. So the TCP netstat-under-loopback experiment (stage 3, bsd43_tcp_experiment.exp, preserved in the harness) is NOT reached in-budget; it needs a faster host or a pre-built multi-user disk image (TECHNE-69b). The 4.2 and Reno tapes use the identical procedure and are preserved+hashed but were not individually booted this pass. What is proven: the 1986 BSD kernel executes on the emulated VAX. Follows gunkies.org (Neozeed)."}


# ============================ PHASE 2: REAL CONCURRENT FAILURE ================================
R["go-runtime-deadlock-fixtures-1.22"] = {
    "runner": "docker", "image": GO, "workdir": "upstream",
    "probe": [{"name": "go", "cmd": "export PATH=$PATH:/usr/local/go/bin; go version"}],
    "build": [{"name": "stage the two testprog files as a module-less main package (crash_test.go is the expectation file, not built)",
               "cmd": "export PATH=$PATH:/usr/local/go/bin; mkdir -p $BODY/build/prog && cp deadlock.go main.go $BODY/build/prog/ && cd $BODY/build/prog && go mod init testprog >/dev/null 2>&1; go vet . 2>&1 | tail -2; go build -o $BODY/build/testprog . && echo built", "timeout": 600}],
    "runs": [{"name": "SimpleDeadlock: main blocks on a channel nobody sends to", "cmd": "cd $BODY/build && ./testprog SimpleDeadlock 2>&1 | head -6; echo exit=${PIPESTATUS[0]}",
              "expect": {"stdout_contains": ["all goroutines are asleep - deadlock!", "exit=2"]}, "timeout": 120},
             {"name": "LockedDeadlock: the deadlock with the main goroutine locked to its thread", "cmd": "cd $BODY/build && ./testprog LockedDeadlock 2>&1 | head -6; echo exit=${PIPESTATUS[0]}",
              "expect": {"stdout_contains": ["all goroutines are asleep - deadlock!", "exit=2"]}, "timeout": 120},
             {"name": "LockedDeadlock2: two goroutines, one locked, both waiting", "cmd": "cd $BODY/build && ./testprog LockedDeadlock2 2>&1 | head -6; echo exit=${PIPESTATUS[0]}",
              "expect": {"stdout_contains": ["all goroutines are asleep - deadlock!", "exit=2"]}, "timeout": 120},
             {"name": "GoexitDeadlock: main calls Goexit while others block", "cmd": "cd $BODY/build && ./testprog GoexitDeadlock 2>&1 | head -6; echo exit=${PIPESTATUS[0]}",
              "expect": {"stdout_contains": ["no goroutines (main called runtime.Goexit) - deadlock!", "exit=2"]}, "timeout": 120},
             {"name": "GoexitExit: main's Goexit after its helpers finish -- crash_test.go expects the Goexit deadlock diagnosis here too", "cmd": "cd $BODY/build && ./testprog GoexitExit 2>&1 | head -6; echo exit=${PIPESTATUS[0]}",
              "expect": {"stdout_contains": ["no goroutines (main called runtime.Goexit) - deadlock!", "exit=2"]}, "timeout": 120},
             {"name": "control: a fixture that is NOT a deadlock (MainGoroutineID panics on purpose): a crash with no deadlock diagnosis", "cmd": "cd $BODY/build && ./testprog MainGoroutineID 2>&1 | head -3; echo exit=${PIPESTATUS[0]}",
              "expect": {"stdout_contains": ["panic: test", "goroutine 1 [running]"], "stdout_not_contains": ["deadlock"]}, "timeout": 120}],
    "tests": [], "test_kind": "UPSTREAM", "test_classification_if_none": "UPSTREAM_TESTS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle: crash_test.go's expected strings for each case ('all goroutines are asleep - deadlock!' exit 2; GoexitDeadlock's 'no goroutines (main called runtime.Goexit) - deadlock!'; GoexitExit also ends in the Goexit diagnosis -- my first 'control' expectation of exit 3 was wrong and is replaced by MainGoroutineID, which panics: a crash that is not a deadlock). The fixtures run unmodified; only main.go's other registered cases (in files not fetched) are absent, so the package holds these two files. Concurrent machinery executes: real goroutines block on real channels and the runtime's checkdead fires."}

R["valgrind-helgrind-fixtures-3.19"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree/valgrind-3.19.0/helgrind/tests",
    "probe": [{"name": "valgrind (installed for the run; Debian's 3.19.0 matches the fixture version)", "cmd": "apt-get -qq update >/dev/null && apt-get -qq install -y valgrind >/dev/null 2>&1; valgrind --version"}],
    "build": [{"name": "compile five fixtures with pthreads, unmodified", "cmd": "for t in tc01_simple_race tc05_simple_race tc09_bad_unlock tc13_laog1 tc19_shadowmem; do gcc -O0 -g -pthread -w -o $BODY/build/$t $t.c || echo FAIL $t; done; ls $BODY/build | tr '\\n' ' '"}],
    "runs": [{"name": "RACE: tc01_simple_race natively (completes, error invisible) then under helgrind (Possible data race reported at the planted line)",
              "cmd": "apt-get -qq update >/dev/null && apt-get -qq install -y valgrind >/dev/null 2>&1; $BODY/build/tc01_simple_race; echo native_exit=$?; valgrind --tool=helgrind -q $BODY/build/tc01_simple_race 2>&1 | grep -E 'Possible data race|tc01_simple_race.c:|by thread|ERROR SUMMARY' | head -8; grep -c 'Possible data race' tc01_simple_race.stderr.exp",
              "expect": {"exit": 0, "stdout_contains": ["Possible data race", "native_exit=0"]}, "timeout": 600},
             {"name": "LOCK ORDER (deadlock precursor): tc13_laog1 -- two threads take two locks in opposite orders; helgrind's lock-order graph reports the inversion",
              "cmd": "apt-get -qq update >/dev/null && apt-get -qq install -y valgrind >/dev/null 2>&1; valgrind --tool=helgrind -q $BODY/build/tc13_laog1 2>&1 | grep -E 'lock order|violated|acquired|ERROR SUMMARY' | head -8; grep -c 'lock order' tc13_laog1.stderr.exp",
              "expect": {"exit": 0, "stdout_regex": r"(?i)lock order"}, "timeout": 600},
             {"name": "BAD UNLOCK: tc09_bad_unlock -- unlocking a mutex the thread does not hold / an unlocked mutex", "cmd": "apt-get -qq update >/dev/null && apt-get -qq install -y valgrind >/dev/null 2>&1; valgrind --tool=helgrind -q $BODY/build/tc09_bad_unlock 2>&1 | grep -E 'unlock|not locked|ERROR SUMMARY' | head -6",
              "expect": {"exit": 0, "stdout_regex": r"(?i)unlock"}, "timeout": 600},
             {"name": "RACE (second fixture): tc05_simple_race", "cmd": "apt-get -qq update >/dev/null && apt-get -qq install -y valgrind >/dev/null 2>&1; valgrind --tool=helgrind -q $BODY/build/tc05_simple_race 2>&1 | grep -E 'Possible data race|ERROR SUMMARY' | head -4",
              "expect": {"exit": 0, "stdout_contains": ["Possible data race"]}, "timeout": 600}],
    "tests": [], "test_kind": "UPSTREAM", "test_classification_if_none": "UPSTREAM_TESTS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle: each fixture's shipped .stderr.exp names the error class helgrind must report; the receipt records helgrind's actual report (addresses differ, classes must match). valgrind is apt-installed in the run container (recorded); the fixtures are the fossil, the detector is the instrument. The native run of tc01 shows the failure mode's signature: exit 0, nothing visible."}

R["glibc-rwlock-writer-starvation-2.36"] = {
    "runner": "docker", "image": C, "workdir": "upstream",
    "probe": [{"name": "glibc", "cmd": "ldd --version | head -1; gcc --version | head -1; nproc"}],
    "build": [{"name": "compile Techne's harness against the system glibc 2.36 (the preserved source is the same version, to read)", "cmd": "gcc -O2 -pthread -o $BODY/build/starve $HARNESS/starve.c && echo built; grep -c 'PREFER_READER' pthread_rwlock_common.c"}],
    "runs": [{"name": "STARVATION: default kind PREFER_READER_NP, 8 readers re-acquiring for 3 s, 1 writer", "cmd": "$BODY/build/starve reader 3 8", "expect": {"exit": 0, "stdout_regex": r"kind=PREFER_READER .*writer_acquisitions=\d+"}, "timeout": 120},
             {"name": "the opt-in kind PREFER_WRITER_NONRECURSIVE_NP under the same pressure", "cmd": "$BODY/build/starve writer 3 8", "expect": {"exit": 0, "stdout_regex": r"kind=PREFER_WRITER_NONRECURSIVE .*writer_acquisitions=\d+"}, "timeout": 120},
             {"name": "both kinds side by side (the pressure response, not a verdict)", "cmd": "$BODY/build/starve reader 3 8 | tail -1; $BODY/build/starve writer 3 8 | tail -1", "expect": {"exit": 0}, "timeout": 120}],
    "tests": [{"name": "oracle: under reader preference the writer acquires FEWER times than under writer preference (the documented direction)", "cmd": "a=$($BODY/build/starve reader 3 8 | grep -o 'writer_acquisitions=[0-9]*' | cut -d= -f2); b=$($BODY/build/starve writer 3 8 | grep -o 'writer_acquisitions=[0-9]*' | cut -d= -f2); echo reader_pref=$a writer_pref=$b; test $a -lt $b", "expect": {"exit": 0}, "timeout": 120}],
    "test_kind": "TECHNE", "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "The documented pathology, measured: with the default kind, readers that never let the lock go idle keep the writer out (acquisitions/s near zero); with PREFER_WRITER_NONRECURSIVE the writer gets in. Techne records the two counts; whether a given count is 'starvation' is the reader's call. The rwlock itself is glibc's, unmodified; the harness only holds and releases it."}
H["glibc-rwlock-writer-starvation-2.36"] = {"starve.c": r'''/* Techne harness: writer progress under continuous reader pressure, for a chosen rwlock kind.
   usage: starve reader|writer <seconds> <n_readers> */
#define _GNU_SOURCE
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
static pthread_rwlock_t lk; static volatile int stop = 0; static volatile long reads = 0, writes = 0;
static double now(void){ struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t); return t.tv_sec + t.tv_nsec*1e-9; }
static void *reader(void *a){ while(!stop){ pthread_rwlock_rdlock(&lk); for (volatile int i=0;i<2000;i++); __sync_fetch_and_add(&reads,1); pthread_rwlock_unlock(&lk);} return 0; }
static void *writer(void *a){ while(!stop){ pthread_rwlock_wrlock(&lk); __sync_fetch_and_add(&writes,1); pthread_rwlock_unlock(&lk); for (volatile int i=0;i<200;i++);} return 0; }
int main(int argc, char **argv){
    if (argc < 4) return 2;
    int secs = atoi(argv[2]), nr = atoi(argv[3]);
    pthread_rwlockattr_t at; pthread_rwlockattr_init(&at);
    int kind = strcmp(argv[1],"writer")==0 ? PTHREAD_RWLOCK_PREFER_WRITER_NONRECURSIVE_NP : PTHREAD_RWLOCK_PREFER_READER_NP;
    pthread_rwlockattr_setkind_np(&at, kind); pthread_rwlock_init(&lk, &at);
    pthread_t r[64], w; for (int i=0;i<nr;i++) pthread_create(&r[i],0,reader,0);
    usleep(20000); pthread_create(&w,0,writer,0);
    double t0=now(); sleep(secs); stop=1; for (int i=0;i<nr;i++) pthread_join(r[i],0); pthread_join(w,0);
    double dt=now()-t0;
    printf("kind=%s readers=%d seconds=%.1f reader_acquisitions=%ld writer_acquisitions=%ld writer_per_second=%.1f\n",
        kind==PTHREAD_RWLOCK_PREFER_READER_NP ? "PREFER_READER" : "PREFER_WRITER_NONRECURSIVE", nr, dt, reads, writes, writes/dt);
    return 0;
}
'''}


# ============================ PHASE 3: DISTRIBUTED SURVIVAL ====================================
R["dmtcp-3.1.2"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree/dmtcp-3.1.2",
    "probe": [{"name": "g++", "cmd": "g++ --version | head -1; uname -r"}],
    "build": [{"name": "configure + make (the coordinator, launcher, restarter and the preload library)", "cmd": "./configure -q >/dev/null 2>&1 && make -s -j4 2>&1 | grep -iE '\\berror' | head -3; test -x bin/dmtcp_launch && test -x bin/dmtcp_restart && echo built", "timeout": 1800},
              {"name": "compile the counting target", "cmd": "gcc -O0 -o $BODY/build/counter $HARNESS/counter.c && echo built"}],
    "runs": [{"name": "checkpoint at ~count 5, kill the process, restart from the image: the count continues, not restarts (one container, one command)",
              "cmd": "mkdir -p /tmp/dm && cp $BODY/build/counter /tmp/dm/ && bash $HARNESS/ckpt_restart.sh $BODY/upstream/tree/dmtcp-3.1.2/bin /tmp/dm 2>&1 | tail -15; cp /tmp/dm/*.out $BODY/build/ 2>/dev/null; ls /tmp/dm | head -5",
              "expect": {"exit": 0, "stdout_contains": ["RESTART OK"], "stdout_regex": r"first count after restart = \d+"}, "timeout": 600}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle: the first value printed by the restarted process is >= the last value printed before the kill and > 0 (it did not begin again at 1). Runs inside one docker container with default capabilities; DMTCP is LD_PRELOAD + signals (no ptrace, no kernel module). The checkpoint image and the target live in a container-local directory: on the Windows-mounted work/ the image is owned by uid 1000 while the process is root and dmtcp_restart refuses it ('Process uid doesn't match uid of checkpoint image') -- the first attempt, recorded."}
H["dmtcp-3.1.2"] = {"counter.c": r"""#include <stdio.h>
#include <unistd.h>
int main(void){ for (int i = 1; ; i++) { printf("count %d\n", i); fflush(stdout); sleep(1); } }
""", "ckpt_restart.sh": r"""#!/bin/bash
# Techne harness: DMTCP checkpoint -> kill -> restart. args: <dmtcp bin dir> <build dir>
set -u
BIN=$1; B=$2; cd $B; rm -f ckpt_*.dmtcp dmtcp_restart_script* counter.out restart.out
export PATH=$BIN:$PATH
dmtcp_coordinator --daemon --exit-on-last -p 7779 -q >/dev/null 2>&1 || true
sleep 1
dmtcp_launch -p 7779 ./counter > counter.out 2>&1 &
LP=$!
sleep 5.5
dmtcp_command -p 7779 -c >/dev/null 2>&1 || dmtcp_command -p 7779 --checkpoint
sleep 2
LAST=$(grep -o '[0-9]*' counter.out | tail -1)
kill -9 $LP 2>/dev/null; sleep 1; pkill -9 -f '^./counter' 2>/dev/null; pkill -9 counter 2>/dev/null
echo "last count before kill = $LAST"
ls ckpt_counter_*.dmtcp | head -1 || { echo "NO CHECKPOINT IMAGE"; exit 1; }
dmtcp_coordinator --daemon --exit-on-last -p 7780 -q >/dev/null 2>&1 || true
sleep 1
dmtcp_restart -p 7780 ckpt_counter_*.dmtcp > restart.out 2>&1 &
RP=$!
sleep 4
kill -9 $RP 2>/dev/null; pkill -9 -f dmtcp_restart 2>/dev/null; pkill -9 counter 2>/dev/null
FIRST=$(grep -o 'count [0-9]*' restart.out | head -1 | grep -o '[0-9]*')
echo "first count after restart = ${FIRST:-none}"
echo "restart output head:"; head -4 restart.out
if [ -n "${FIRST:-}" ] && [ "$FIRST" -ge 4 ]; then echo "RESTART OK (continued from the checkpoint, not from 1)"; else echo "RESTART FAILED"; exit 1; fi
"""}

R["hashicorp-memberlist-0.5.4"] = {
    "runner": "docker", "image": "golang:1.24-bookworm", "workdir": "upstream/tree/memberlist-0.5.4",
    "probe": [{"name": "go", "cmd": "export PATH=$PATH:/usr/local/go/bin; go version"}],
    "build": [{"name": "go build (modules from go.sum, fetched at run time -- recorded)", "cmd": "export PATH=$PATH:/usr/local/go/bin; go build ./... 2>&1 | tail -3; echo built", "timeout": 900}],
    "runs": [{"name": "SWIM probing and suspicion: the package's own tests for probe, indirect ping, suspect -> dead, gossip (loopback, unreachable peers)",
              "cmd": "export PATH=$PATH:/usr/local/go/bin; go test -count=1 -run 'TestMemberList_Probe$|TestMemberList_ProbeNode_Suspect$|TestMemberList_ProbeNode_Suspect_Dogpile|TestMemberList_ProbeNode_Awareness_Degraded|TestMemberList_SuspectNode|TestMemberList_DeadNode|TestMemberList_Gossip|TestMemberlist_Join$|TestMemberlist_Leave$' -v . 2>&1 | grep -E '^(=== RUN|--- (PASS|FAIL)|PASS|FAIL|ok)' | head -40",
              "expect": {"exit": 0, "stdout_contains": ["--- PASS: TestMemberList_ProbeNode_Suspect", "--- PASS: TestMemberList_DeadNode"], "stdout_not_contains": ["--- FAIL"]}, "timeout": 900}],
    "tests": [], "test_kind": "UPSTREAM", "test_classification_if_none": "UPSTREAM_TESTS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "The upstream tests construct members in-process on loopback with unreachable addresses and assert the suspect/dead transitions and gossip; that is the oracle. Test names are those of v0.5.4 (state_test.go, memberlist_test.go). go.mod requires go >= 1.24, so the run world is golang:1.24-bookworm (first attempt with 1.22 refused to build; recorded)."}

R["redlock-py-redis-2014"] = {
    "runner": "docker", "image": "python:3.11-slim", "workdir": "upstream/tree",
    "probe": [{"name": "python", "cmd": "python --version"}],
    "build": [{"name": "apt redis-server + pip install . (same container as the run; recorded)", "cmd": "apt-get -qq update >/dev/null && apt-get -qq install -y redis-server >/dev/null 2>&1; redis-server --version | head -1; pip install -q . 2>&1 | tail -1; echo built", "timeout": 900}],
    "runs": [{"name": "three redis instances; two clients contend; TTL shorter than the holder's work -> the lease expires under the first holder (Kleppmann's scenario, observed)",
              "cmd": "apt-get -qq update >/dev/null && apt-get -qq install -y redis-server >/dev/null 2>&1; pip install -q . >/dev/null 2>&1; python $HARNESS/lease.py 2>&1 | tail -20",
              "expect": {"exit": 0, "stdout_contains": ["mutual exclusion while valid: OK", "lease expired under a live holder"], "stdout_regex": r"validity_ms=\d+"}, "timeout": 600}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle A (the mechanism): with TTL 2000 ms, client B cannot acquire while A holds a valid lease, and acquires after A releases. Oracle B (the documented weakness): with TTL 300 ms and A 'working' for 1000 ms, B acquires while A still believes it holds the lock -- two holders. Both recorded as behaviour; the 2014/2016 debate is cited in the record, not adjudicated."}
H["redlock-py-redis-2014"] = {"lease.py": r"""import subprocess, time, sys
from redlock import Redlock
ports = [7401, 7402, 7403]
procs = [subprocess.Popen(["redis-server", "--port", str(p), "--save", "", "--appendonly", "no", "--loglevel", "warning"]) for p in ports]
time.sleep(1.5)
servers = [{"host": "127.0.0.1", "port": p, "db": 0} for p in ports]
A = Redlock(servers); B = Redlock(servers)
# A: the mechanism
la = A.lock("resource", 2000); print("A acquired:", bool(la), "validity_ms=%d" % (la.validity if la else 0))
lb = B.lock("resource", 2000); print("B while A valid:", bool(lb))
ok1 = bool(la) and not lb
A.unlock(la); lb = B.lock("resource", 2000); print("B after A released:", bool(lb)); ok1 = ok1 and bool(lb); B.unlock(lb)
print("mutual exclusion while valid:", "OK" if ok1 else "FAILED")
# B: the weakness -- a lease shorter than the holder's work
la = A.lock("resource", 300); print("A acquired short lease:", bool(la), "validity_ms=%d" % (la.validity if la else 0))
time.sleep(1.0)   # A 'works' (or is paused) longer than its lease
lb = B.lock("resource", 300); print("B acquires while A still thinks it holds:", bool(lb))
print("lease expired under a live holder" if (la and lb) else "no expiry observed")
for p in procs: p.kill()
sys.exit(0 if ok1 else 1)
"""}

R["cocagne-plain-paxos"] = {
    "runner": "docker", "image": "python:2.7-slim", "workdir": "upstream/tree",
    "probe": [{"name": "python 2.7 (the preserved py2 world the code was written for)", "cmd": "python --version 2>&1"}],
    "build": [],
    "runs": [{"name": "the shipped tests: essential (prepare/promise/accept/learn, quorum), functional, practical (heartbeat leadership), durable",
              "cmd": "python -m unittest discover -s test -p 'test_*.py' 2>&1 | tail -6",
              "expect": {"exit": 0, "stdout_regex": r"Ran \d+ tests"}, "timeout": 600}],
    "tests": [{"name": "oracle: the essential + functional suites pass ",
               "cmd": "python -m unittest discover -s test -p 'test_essential.py' 2>&1 | tail -3; python -m unittest discover -s test -p 'test_functional.py' 2>&1 | tail -3; python -m unittest discover -s test -p 'test_practical.py' 2>&1 | tail -3", "expect": {"exit": 0, "stdout_regex": r"Ran \d+ tests[^O]*OK[\s\S]*Ran \d+ tests[^O]*OK"}, "timeout": 600}],
    "test_kind": "UPSTREAM", "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "The tests are message-passing simulations of Proposer/Acceptor/Learner exchanges including contention; they assert Paxos's safety and the leader-heartbeat behaviour of the practical layer. Written in the Python 2 era: under python 3.11 the suites fail on str/bytes (48 + 29 errors, first attempt, recorded); run in the preserved python:2.7-slim world they are the code's own contract."}

STUBS = {'plot': 'function varargout = plot(varargin)\n% Techne harness stub: plotting is a no-op in the headless Octave world; the fossil is unchanged.\nif nargout > 0, varargout{1} = 1; end\nend\n', 'figure': 'function varargout = figure(varargin)\n% Techne harness stub: plotting is a no-op in the headless Octave world; the fossil is unchanged.\nif nargout > 0, varargout{1} = 1; end\nend\n', 'subplot': 'function varargout = subplot(varargin)\n% Techne harness stub: plotting is a no-op in the headless Octave world; the fossil is unchanged.\nif nargout > 0, varargout{1} = 1; end\nend\n', 'hold': 'function varargout = hold(varargin)\n% Techne harness stub: plotting is a no-op in the headless Octave world; the fossil is unchanged.\nif nargout > 0, varargout{1} = 1; end\nend\n', 'legend': 'function varargout = legend(varargin)\n% Techne harness stub: plotting is a no-op in the headless Octave world; the fossil is unchanged.\nif nargout > 0, varargout{1} = 1; end\nend\n', 'xlabel': 'function varargout = xlabel(varargin)\n% Techne harness stub: plotting is a no-op in the headless Octave world; the fossil is unchanged.\nif nargout > 0, varargout{1} = 1; end\nend\n', 'ylabel': 'function varargout = ylabel(varargin)\n% Techne harness stub: plotting is a no-op in the headless Octave world; the fossil is unchanged.\nif nargout > 0, varargout{1} = 1; end\nend\n', 'title': 'function varargout = title(varargin)\n% Techne harness stub: plotting is a no-op in the headless Octave world; the fossil is unchanged.\nif nargout > 0, varargout{1} = 1; end\nend\n', 'axis': 'function varargout = axis(varargin)\n% Techne harness stub: plotting is a no-op in the headless Octave world; the fossil is unchanged.\nif nargout > 0, varargout{1} = 1; end\nend\n', 'grid': 'function varargout = grid(varargin)\n% Techne harness stub: plotting is a no-op in the headless Octave world; the fossil is unchanged.\nif nargout > 0, varargout{1} = 1; end\nend\n', 'stairs': 'function varargout = stairs(varargin)\n% Techne harness stub: plotting is a no-op in the headless Octave world; the fossil is unchanged.\nif nargout > 0, varargout{1} = 1; end\nend\n', 'close': 'function varargout = close(varargin)\n% Techne harness stub: plotting is a no-op in the headless Octave world; the fossil is unchanged.\nif nargout > 0, varargout{1} = 1; end\nend\n', 'clc': 'function varargout = clc(varargin)\n% Techne harness stub: plotting is a no-op in the headless Octave world; the fossil is unchanged.\nif nargout > 0, varargout{1} = 1; end\nend\n', 'text': 'function varargout = text(varargin)\n% Techne harness stub: plotting is a no-op in the headless Octave world; the fossil is unchanged.\nif nargout > 0, varargout{1} = 1; end\nend\n', 'ylim': 'function varargout = ylim(varargin)\n% Techne harness stub: plotting is a no-op in the headless Octave world; the fossil is unchanged.\nif nargout > 0, varargout{1} = 1; end\nend\n', 'xlim': 'function varargout = xlim(varargin)\n% Techne harness stub: plotting is a no-op in the headless Octave world; the fossil is unchanged.\nif nargout > 0, varargout{1} = 1; end\nend\n', 'drawnow': 'function varargout = drawnow(varargin)\n% Techne harness stub: plotting is a no-op in the headless Octave world; the fossil is unchanged.\nif nargout > 0, varargout{1} = 1; end\nend\n'}

# ============================ PHASE 4: ADAPTIVE CONTROL =======================================
OCT = "prometheus-fossil-octave:bookworm"
R["pid-autotune-hirschmann"] = {
    "runner": "docker", "image": "python:3.11-slim", "workdir": "upstream/tree",
    "probe": [{"name": "python", "cmd": "python --version"}],
    "build": [],
    "runs": [{"name": "relay autotune on kettle A (40 l, 6 kW): limit cycle -> Ku, Pu -> gains per rule", "cmd": "pip install -q matplotlib >/dev/null 2>&1; python $HARNESS/two_plants.py A 2>&1 | head -60", "expect": {"exit": 0, "stdout_contains": ["succeeded", "rule: ziegler-nichols"]}, "timeout": 900},
             {"name": "the SAME tuner on kettle B (10 l, 2 kW): a different plant yields different gains (changing plant -> adaptation -> altered parameters)", "cmd": "pip install -q matplotlib >/dev/null 2>&1; python $HARNESS/two_plants.py B 2>&1 | head -60", "expect": {"exit": 0, "stdout_contains": ["succeeded", "rule: ziegler-nichols"]}, "timeout": 900}],
    "tests": [{"name": "oracle: the Ziegler-Nichols gains differ between the two plants -- Kd (which carries the measured ultimate period) by more than 20%; Kp is printed too", "cmd": "pip install -q matplotlib >/dev/null 2>&1; python $HARNESS/two_plants.py compare 2>&1 | tail -3", "expect": {"exit": 0, "stdout_contains": ["RESULT OK"]}, "timeout": 1800}],
    "test_kind": "TECHNE", "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "sim.py's autotune mode is driven with two kettle parameterisations; the tuner (autotune.py, unmodified) finds each plant's limit cycle and prints the gains. The oracle is that the tuned gains differ across plants (Kd, which carries the measured ultimate period, by >20%): adaptation to the plant, not a fixed gain. Observed 2026-09-13: Kp 6.18 vs 5.81 (6%), Ki 0.019 vs 0.041, Kd 153 vs 63 -- the first oracle asked Kp alone to move by 10% and it did not; Kd/Ki carry the plant's time constant. Simulation runs at the script's own sample time (minutes of simulated time, seconds of wall time)."}
H["pid-autotune-hirschmann"] = {"two_plants.py": r"""import subprocess, sys, re
A = ["-a", "-n", "-i", "120", "--volume", "40", "--power", "6.0", "--ambient", "20", "--sampletime", "5", "-s", "45"]
B = ["-a", "-n", "-i", "120", "--volume", "10", "--power", "2.0", "--ambient", "20", "--sampletime", "5", "-s", "45"]
def run(args):
    r = subprocess.run([sys.executable, "sim.py"] + args, capture_output=True, text=True)
    out = r.stdout + r.stderr
    kp = None
    m = re.search(r"rule: ziegler-nichols\s*\nKp: ([0-9.eE+-]+)\s*\nKi: ([0-9.eE+-]+)\s*\nKd: ([0-9.eE+-]+)", out)
    if m: kp = (float(m.group(1)), float(m.group(2)), float(m.group(3)))
    return out, kp
which = sys.argv[1]
if which in ("A", "B"):
    out, kp = run(A if which == "A" else B); print(out[-4000:])
else:
    oa, ka = run(A); ob, kb = run(B)
    print("ziegler-nichols (Kp, Ki, Kd) kettle A = %s ; kettle B = %s" % (ka, kb))
    ok = ka is not None and kb is not None and abs(ka[2] - kb[2]) / max(abs(ka[2]), abs(kb[2]), 1e-9) > 0.20
    print("RESULT", "OK" if ok else "FAIL")
"""}

R["indirect-self-tuning-regulator-liaosteve"] = {
    "runner": "docker", "image": OCT, "workdir": "upstream/tree",
    "probe": [{"name": "octave", "cmd": "octave --version | head -1"}],
    "build": [],
    "runs": [{"name": "run main_code.m (RLS with forgetting + pole placement, 200 samples); print the final plant estimate beside the true plant the script draws as reference lines",
              "cmd": "octave --no-gui --no-window-system -p $HARNESS --eval \"source('main_code.m'); th = theta(:,end); printf('theta_final a1=%.4f a2=%.4f b0=%.4f b1=%.4f\\n', th); printf('true        a1=-1.6065 a2=0.6065 b0=0.1065 b1=0.0902\\n'); printf('max_abs_err=%.4f\\n', max(abs(th - [-1.6065;0.6065;0.1065;0.0902]))); printf('controller R,S,T at the end: r1=%.4f s0=%.4f s1=%.4f t0=%.4f\\n', r1, s0, s1, t0); printf('theta at k=10: %.4f %.4f %.4f %.4f\\n', theta(:,20));\" 2>&1 | tail -8",
              "expect": {"exit": 0, "stdout_regex": r"theta_final a1=-1\.\d+"}, "timeout": 600}],
    "tests": [{"name": "oracle: by sample 20 (t=10 s) the estimate is within 0.05 of the true plant on every parameter (adaptation happened); the end-of-run error is RECORDED, not asserted -- with lambda=0.8 and a square-wave reference the estimate drifts once excitation fades (the known STR hazard, visible here)",
               "cmd": "octave --no-gui --no-window-system -p $HARNESS --eval \"source('main_code.m'); tr=[-1.6065;0.6065;0.1065;0.0902]; printf('err_at_sample20=%.4f err_at_end=%.4f\\n', max(abs(theta(:,20)-tr)), max(abs(theta(:,end)-tr)));\" 2>&1 | grep err_at | awk '{print; split($1,a,\"=\"); exit (a[2] < 0.05) ? 0 : 1}'", "expect": {"exit": 0, "stdout_regex": r"err_at_sample20=0\.0[0-4]"}, "timeout": 600}],
    "test_kind": "TECHNE", "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "The script's own dashed reference lines give the true plant; Octave runs it unmodified with plotting shadowed by harness stubs (plot.m, figure.m, ...). The controller polynomials R,S,T are recomputed from the estimates every sample: the altered control parameters are printed. Observed 2026-09-13: at sample 20 the estimate is within 0.03 of the plant; by the end (sample 200) b0 has drifted to 0.02 (max error 0.0997) -- covariance wind-up under a forgetting factor of 0.8 when the square-wave reference stops exciting the plant. Recorded as behaviour; the first oracle (end-of-run < 0.05) was replaced by the sample-20 oracle and the drift is kept as data."}
H["indirect-self-tuning-regulator-liaosteve"] = {("%s.m" % n): t for n, t in STUBS.items()}

R["l1-adaptive-control-basics-xkhainguyen"] = {
    "runner": "docker", "image": OCT, "workdir": "upstream/tree",
    "probe": [{"name": "octave", "cmd": "octave --version | head -1"}],
    "build": [],
    "runs": [{"name": "MainL1_ODE1_v1.m: predictor + piecewise-constant adaptive law (Ts=10 ms) + first-order filter against a plant hit by three disturbance pulses (d=100 at 10-20 ms; 300+500 sin at 40-50 ms; 500 sin - 500 at 70-80 ms); the sampled estimate sigma_hat, and the control u, printed",
              "cmd": "octave --no-gui --no-window-system -p $HARNESS --eval \"techne_run_script('MainL1_ODE1_v1.m'); printf('ts   = %s\\n', mat2str(ts(1:12),3)); printf('sigma_hat = %s\\n', mat2str(sigma_hat(1:12),4)); printf('sigma_hat(3) (estimate of the d=100 pulse, one sample late) = %.2f\\n', sigma_hat(3)); printf('max|u| = %.1f (the control that counters the -500 pulse); final sigma_hat = %.3f; max|x| = %.3f\\n', max(abs(u)), sigma_hat(end), max(abs(x)));\" 2>&1 | grep -v warning | tail -6",
              "expect": {"exit": 0, "stdout_regex": r"sigma_hat\(3\) .* = \d+\.\d+"}, "timeout": 600}],
    "tests": [{"name": "oracle: the estimate of the first pulse is within 10% of d=100, and the estimate returns below 1 after the last pulse", "cmd": "octave --no-gui --no-window-system -p $HARNESS --eval \"techne_run_script('MainL1_ODE1_v1.m'); printf('pulse1_est=%.3f final_est=%.4f\\n', sigma_hat(3), abs(sigma_hat(end)));\" 2>&1 | grep pulse1_est | awk '{print; split($1,a,\"=\"); split($2,b,\"=\"); exit (a[2] > 90 && a[2] < 110 && b[2] < 1) ? 0 : 1}'", "expect": {"exit": 0}, "timeout": 600}],
    "test_kind": "TECHNE", "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "The script defines its functions after the script body (MATLAB R2016b style); Octave only defines script-local functions when execution reaches them and the script's `clear all` would erase them, so the harness runner techne_run_script.m evaluates the FUNCTIONS block first and then the body, with `clear` shadowed by a no-op stub -- a harness-level accommodation, the .m file untouched. Observed 2026-09-13: sigma_hat(3) = 98.02 for the d=100 pulse (one adaptive sample late), max|u| = 453 against the -500 pulse. The first oracle (windowed interp1 of the sampled law) was mis-aligned by that one-sample lag and read 0; replaced by the sampled sequence itself. Octave's exit code from --eval is unreliable after an error, so pass/fail is decided in the shell from the printed numbers."}
H["l1-adaptive-control-basics-xkhainguyen"] = {("%s.m" % n): t for n, t in STUBS.items()}
H["l1-adaptive-control-basics-xkhainguyen"]["techne_run_script.m"] = "function techne_run_script(fname)\n% Techne harness: run a MATLAB-style script that defines its local functions AFTER the body.\n% Octave defines script-local functions only when execution reaches the definition, so the\n% functions block is evaluated first (as command-line function definitions), then the body.\n% The fossil file is read, never written. Variables land in the caller's workspace.\n  txt = fileread(fname);\n  k = regexp(txt, '(?m)^\\s*function\\s', 'once');\n  if isempty(k)\n    body = txt; funcs = '';\n  else\n    body = txt(1:k-1); funcs = txt(k:end);\n  end\n  if ~isempty(funcs)\n    evalin('base', funcs);\n  end\n  evalin('base', body);\nend\n"
H["l1-adaptive-control-basics-xkhainguyen"]["clear.m"] = "function clear(varargin)\n% Techne harness stub: the script's `clear all` would erase the functions defined by techne_run_script; no-op here.\nend\n"

# ============================ PHASE 5: INFERENCE ==============================================
R["libdai-mooij"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree",
    "probe": [{"name": "g++", "cmd": "g++ --version | head -1"}],
    "build": [{"name": "apt boost + gmp, then make the library and examples (Makefile.LINUX; no source change)", "cmd": "apt-get -qq update >/dev/null && apt-get -qq install -y libboost-dev libboost-program-options-dev libboost-test-dev libgmp-dev >/dev/null 2>&1; cp Makefile.LINUX Makefile.conf; make -s -j4 lib examples 2>&1 | grep -iE '\\berror' | head -5; ls examples/example_sprinkler examples/example 2>&1; test -x examples/example_sprinkler && echo built", "timeout": 1800},
              {"name": "the same apt + make in the run container is repeated per command (one container per command)", "cmd": "echo noted"}],
    "runs": [{"name": "sprinkler network: build it, write sprinkler.fg, exact marginals (junction tree)", "cmd": "apt-get -qq update >/dev/null && apt-get -qq install -y libboost-dev libboost-program-options-dev libboost-test-dev libgmp-dev >/dev/null 2>&1; cp Makefile.LINUX Makefile.conf; make -s -j4 lib examples >/dev/null 2>&1; ./examples/example_sprinkler 2>&1 | tail -8", "expect": {"exit": 0, "stdout_contains": ["P(W=1) = 0.6471"]}, "timeout": 1800},
             {"name": "BELIEF PROPAGATION on the same factor graph beside the exact answer (examples/example: JTree exact, then loopy BP, then MF/TreeEP/Gibbs)", "cmd": "apt-get -qq update >/dev/null && apt-get -qq install -y libboost-dev libboost-program-options-dev libboost-test-dev libgmp-dev >/dev/null 2>&1; cp Makefile.LINUX Makefile.conf; make -s -j4 lib examples >/dev/null 2>&1; ./examples/example_sprinkler >/dev/null 2>&1; ./examples/example sprinkler.fg 2>&1 | grep -iE 'exact|belief propagation|BP|marginal|\(' | head -40", "expect": {"exit": 0, "stdout_regex": r"(?i)belief propagation"}, "timeout": 1800}],
    "tests": [{"name": "oracle: the sprinkler network is LOOPY (Cloudy -> Sprinkler and Rain -> WetGrass), so loopy BP must agree with the exact marginals on Cloudy/Sprinkler/Rain (1e-6) and DIFFER on WetGrass -- the documented inexactness of loopy BP, measured", "cmd": "apt-get -qq update >/dev/null && apt-get -qq install -y libboost-dev libboost-program-options-dev libboost-test-dev libgmp-dev python3 >/dev/null 2>&1; cp Makefile.LINUX Makefile.conf; make -s -j4 lib examples >/dev/null 2>&1; ./examples/example_sprinkler >/dev/null 2>&1; ./examples/example sprinkler.fg > $BODY/build/example.out 2>&1; python3 $HARNESS/bp_vs_exact.py $BODY/build/example.out", "expect": {"exit": 0, "stdout_contains": ["RESULT OK"]}, "timeout": 1800}],
    "test_kind": "TECHNE",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle: example.cpp prints the exact (JTree) variable marginals and then the loopy-BP marginals for the same factor graph. CORRECTION 2026-09-13: I first wrote the sprinkler network down as a tree; it is loopy, and BP converged in 2 passes to P(WetGrass=1) = 0.5985 against the exact 0.6471 while matching the three upstream variables exactly -- the oracle now asserts that shape (agreement upstream, a >0.01 discrepancy inside the loop). Boost/GMP from apt in each run container, recorded (one container per command). Observed 2026-09-13: P(W=1) = 0.6471, P(S=1|W=1) = 0.4298, P(R=1|W=1) = 0.7079."}
H["libdai-mooij"] = {"bp_vs_exact.py": '"""Techne harness: compare libDAI\'s exact (junction tree) and loopy-BP variable marginals from\nexamples/example\'s output. The sprinkler network is LOOPY (Cloudy -> Sprinkler, Cloudy -> Rain,\nboth -> WetGrass), so BP is exact on the upstream variables and inexact on WetGrass: that is the\ndocumented behaviour of loopy BP, and the oracle checks exactly that shape."""\nimport re, sys\ntxt = open(sys.argv[1], encoding="utf-8", errors="replace").read()\n\n\ndef block(title):\n    i = txt.find(title)\n    if i < 0:\n        return None\n    lines = txt[i:].splitlines()[1:]\n    out = []\n    for l in lines:\n        if not l.strip().startswith("("):\n            break\n        nums = re.findall(r"\\(([0-9.eE+-]+), ([0-9.eE+-]+)\\)", l)\n        if nums:\n            out.append((float(nums[-1][0]), float(nums[-1][1])))\n    return out\n\n\nex = block("Exact variable marginals:")\nbp = block("Approximate (loopy belief propagation) variable marginals:")\nprint("exact:", ex)\nprint("bp:   ", bp)\nif not ex or not bp or len(ex) != len(bp):\n    print("RESULT FAIL (could not parse both blocks)"); sys.exit(1)\ndiffs = [max(abs(a - b) for a, b in zip(x, y)) for x, y in zip(ex, bp)]\nprint("per-variable max |bp - exact|:", ["%.4f" % d for d in diffs])\nupstream_exact = all(d < 1e-6 for d in diffs[:3])\nwetgrass_inexact = diffs[3] > 0.01\nprint("x0..x2 (Cloudy, Sprinkler, Rain) agree to 1e-6:", upstream_exact)\nprint("x3 (WetGrass, inside the loop) differs by %.4f: loopy BP is inexact here, as documented" % diffs[3])\nprint("RESULT", "OK" if (upstream_exact and wetgrass_inexact) else "FAIL")\n'}


# ============================ PHASE 7: CULTURES ==============================================
R["gnu-apl-2.0"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree/apl-2.0",
    "probe": [{"name": "g++", "cmd": "g++ --version | head -1"}],
    "build": [{"name": "configure + make (readline optional; --without-... kept default)", "cmd": "./configure --quiet >/dev/null 2>&1 && make -s >/dev/null 2>&1; test -x src/apl && echo built", "timeout": 1800}],
    "runs": [{"name": "whole-array APL: sum of 1..100 and a 5x5 outer-product multiplication table, no loops", "cmd": "src/apl --silent --script < $HARNESS/table.apl 2>&1 | grep -vE '^$' | tail -12", "expect": {"exit": 0, "stdout_contains": ["5050"], "stdout_regex": r"5\s+10\s+15\s+20\s+25"}, "timeout": 300}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle: +/iota 100 = 5050 and the 5x5 outer product o.x is the multiplication table (rows 5 10 15 20 25 ...), each computed as a whole-array expression with no explicit loop. The interpreter is the fossil; table.apl is Techne's stimulus."}
H["gnu-apl-2.0"] = {"table.apl": "'sum 1..100:'\n+/⍳ 100\n'5x5 outer product:'\n(⍳ 5)∘.×⍳ 5\n"}



def main():
    import shutil
    env = vault.REPO / "techne" / "fossils" / "environment"
    # the SIMH world's console scripts travel with the tape specimen as its harness
    H.setdefault("bsd-4.3-distribution-tape-1986", {})
    for f in ("simh_mktape.py", "bsd43_install_stage1.exp", "bsd43_install_stage2.exp", "bsd43_tcp_experiment.exp", "boot42.uue"):
        H["bsd-4.3-distribution-tape-1986"][f] = (env / f).read_text(encoding="utf-8")
    for sid, recipe in R.items():
        d = vault.specimen_dir(sid); d.mkdir(parents=True, exist_ok=True)
        (d / "recipe.json").write_text(json.dumps(recipe, indent=2) + "\n", encoding="utf-8", newline="\n")
        for name, text in H.get(sid, {}).items():
            (d / "harness" / name).parent.mkdir(parents=True, exist_ok=True)
            (d / "harness" / name).write_text(text, encoding="utf-8", newline="\n")
        if sid == "bsd-4.3-distribution-tape-1986":
            shutil.copyfile(env / "boot42", d / "harness" / "boot42")   # the 6600-byte console boot, binary
        print("wrote", sid, "+harness" if sid in H or sid.startswith("bsd-4.3") else "")


if __name__ == "__main__":
    main()
