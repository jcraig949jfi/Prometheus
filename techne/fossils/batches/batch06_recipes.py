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
    "probe": [{"name": "simh", "cmd": "cat /usr/local/share/simh-commit.txt; expect -v; printf 'show version\\nexit\\n' > /tmp/v.ini; vax780 /tmp/v.ini 2>&1 | head -2"}],
    "build": [{"name": "assemble the .tap from the tape files (stand 512-byte records; miniroot, rootdump, usr.tar 10240) and gunzip the miniroot as a raw disk",
               "cmd": "python3 $HARNESS/simh_mktape.py 43bsd.tap $BODY/upstream/stand.gz:512 $BODY/upstream/miniroot.gz:10240 $BODY/upstream/rootdump.gz:10240 $BODY/upstream/usr.tar.gz:10240 && gunzip -c $BODY/upstream/miniroot.gz > miniroot.raw && sha256sum miniroot.raw 43bsd.tap | cut -c1-80", "timeout": 600},
              {"name": "STAGE 1: console-load boot42, boot the miniroot from rq0, restore the root dump onto rq1 with the release's own xtr", "cmd": "expect $HARNESS/bsd43_install_stage1.exp miniroot.raw rq.dsk 43bsd.tap $HARNESS/boot42 > stage1.log 2>&1; grep -a STAGE1 stage1.log; grep -a -c 'Root filesystem extracted' stage1.log", "timeout": 3600},
              {"name": "STAGE 2: boot the restored root, newfs + extract /usr from tape file 4, fstab, home slice", "cmd": "expect $HARNESS/bsd43_install_stage2.exp rq.dsk 43bsd.tap $HARNESS/boot42 > stage2.log 2>&1; grep -a STAGE2 stage2.log", "timeout": 5400}],
    "runs": [{"name": "STAGE 3: multi-user boot; netstat -s before and after a loopback rsh transfer of /vmunix (the fossil's TCP moving bytes through itself)",
              "cmd": "expect $HARNESS/bsd43_tcp_experiment.exp rq.dsk $HARNESS/boot42 > stage3.log 2>&1; grep -a -E 'EXP:|4.3 BSD UNIX' stage3.log | head -12; grep -a -A3 'tcp:' stage3.log | head -40",
              "expect": {"exit": 0, "stdout_contains": ["4.3 BSD UNIX #1", "EXP: root shell", "tcp:"]}, "timeout": 3600}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_EMULATED",
    "notes": "Follows the documented SIMH procedure (gunkies.org, Neozeed): the 780 has no tape boot ROM, so the 4.2BSD console `boot` (boot42, a 6600-byte companion, sha256 a7bacc51...) is loaded at 0 with R10=9 (uda), R11=0 and started at 2; the miniroot is attached as a raw RA81 and boots directly. Nothing in the distribution is modified. Loss/delay injection is NOT available on one guest: the loopback transfer is the 'normal transfer' pressure only; two guests over a lossy Ethernet relay is the recorded boundary (TECHNE-69b). The full install is ~45 min of emulated VAX time per run."}

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
