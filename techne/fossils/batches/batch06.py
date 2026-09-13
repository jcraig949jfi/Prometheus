"""Batch 06 of the fossil harvest (2026-09-13): UNLOCK, FAILURE MACHINERY, PRESSURE, CULTURES -- records.

    python -m techne.fossils.batches.batch06

Charter: roles/Techne/prompts/2026-09-12_batch06/OPERATOR_CHARTER.md. Records added incrementally
as each phase lands; every "loser" / "known-bad" label is the human record's verdict, cited.
"""
from __future__ import annotations

from .. import record

S = []


def spec(sid, **kw):
    S.append(record.skeleton(sid, **kw))


TUHS = "https://www.tuhs.org/Archive/Distributions/UCB/4BSD/%s/%s"


def tape(version):
    files = ["FORMAT", "stand.gz", "miniroot.gz", "rootdump.gz", "usr.tar.gz"]
    return {"artifacts": [{"kind": "url", "url": TUHS % (version, f), "filename": f, "extract": False} for f in files]}


# ============================ PHASE 1 / TECHNE-69: the historical TCP world ====================
_tape_common = dict(
    domain=["operating-system", "networks", "TCP", "historical-toolchain", "distribution-tape", "vax"],
    source_type="HISTORICAL_ARCHIVE_MIRROR",
    license={"spdx": "BSD-4-Clause", "status": "permissive (original BSD licence; Caldera 2002 grant covers 32V-derived code); AT&T-derived portions were released by Caldera/SCO 2002", "evidence": "TUHS archive terms; Caldera licence 2002"},
    language=["C (4BSD kernel and userland)", "VAX assembler"],
    build_system="none: a distribution TAPE (stand / miniroot / rootdump / usr.tar as tape files)",
    compiler_or_interpreter="a VAX-11/780 -- emulated by SIMH vax780 (docker world prometheus-fossil-simh)",
    dependencies=["SIMH vax780 (Debian simh 3.8.1)", "a .tap image built from the tape files (Techne mktape, record sizes per FORMAT/notes)", "an RP06 disk image", "expect (console automation)"],
    recovered_status="NOT_RECOVERED_SOURCE_IS_ORIGINAL",
    environment={"runner": "docker", "image": "prometheus-fossil-simh:bookworm"},
)
spec("bsd-4.2-distribution-tape-1983",
    canonical_name="4.2BSD distribution tape (August 1983): stand, miniroot, root dump, usr.tar -- the bootable system whose TCP is bsd-tcp-4.2-1983",
    aliases=["4.2BSD tape", "4.2 BSD VAX"],
    lineage="The 4.2BSD release as shipped to VAX sites: the standalone boot programs, the miniroot filesystem, a dump of the root filesystem (with /vmunix) and the /usr tree. Preserved so that the kernel in bsd-tcp-4.2-1983 can be BOOTED under an emulated VAX-11/780 rather than only read. Transcribed from the physical 9-track tape into the TUHS archive.",
    era="1983",
    version="4.2BSD (Aug 1983); TUHS Archive/Distributions/UCB/4BSD/4.2BSD (stand, miniroot, rootdump, usr.tar; FORMAT)",
    source_origin=tape("4.2BSD"),
    source_identity={"archive": "tuhs.org/Archive/Distributions/UCB/4BSD/4.2BSD", "tape_files": "1 stand (199x512), 2 miniroot (205x10240), 3 rootdump (383x10240), 5 usr.tar (2148x10240)"},
    entry_points=["SIMH: boot ts0 -> standalone boot -> copy miniroot to hp(0,1) -> boot hp(0,1)vmunix -> newfs/restore root -> boot hp(0,0)vmunix"],
    example={"command": "python -m techne.fossils.harvest run bsd-4.2-distribution-tape-1983", "input": "the four tape files assembled into a .tap image", "output": "a booted 4.2BSD kernel on an emulated VAX-11/780 (stage of the install reached is the receipt)"},
    upstream_docs=["Installing and Operating 4.2BSD on the VAX (Leffler, Joy, Fabry; 1983)", "TUHS FORMAT file"],
    human_capability_summary={"built_to": "install a complete 4.2BSD system on a VAX from one magnetic tape", "pressure": "1983 hardware: a 9-track drive, an RP06 disk, a console; and the Internet that this release's TCP was about to collapse", "success_means": "the kernel boots multi-user from disk and its TCP answers on lo0"},
    known_human_problem_solved="distribution and installation of a research operating system",
    human_environmental_pressure="1983 media and hardware; the network stack shipped here had no congestion control",
    human_failure_condition="a bad tape or disk geometry stops the install; historically, its TCP collapsed under congestion",
    behavioral_entry_point="boot the installed disk under SIMH; netstat -s on the guest before/after a loopback transfer",
    acquisition_tags=["batch06", "phase1", "unlock", "depth:tcp", "historical_world"],
    lineage_relations=[{"relation": "shares_ancestor_with", "to": "bsd-tcp-4.2-1983", "note": "this tape CONTAINS the kernel whose netinet/tcp_* files are preserved as that specimen"}],
    **_tape_common)
spec("bsd-4.3-distribution-tape-1986",
    canonical_name="4.3BSD distribution tape (June 1986): stand, miniroot, root dump, usr.tar -- the last pre-slow-start BSD TCP, bootable",
    aliases=["4.3BSD tape", "4.3 BSD VAX"],
    lineage="Plain 4.3BSD (1986) predates Jacobson's slow start / congestion avoidance (which arrived in 4.3BSD-Tahoe, 1988): its TCP is the 4.2 design with two years of fixes -- a BEFORE point for the congestion lineage that, unlike the Tahoe tape (usr.tar cut short in the archive), is COMPLETE and installable. The classic SIMH-installable BSD.",
    era="1986",
    version="4.3BSD (Jun 1986); TUHS Archive/Distributions/UCB/4BSD/4.3BSD (stand, miniroot, rootdump, usr.tar; FORMAT)",
    source_origin=tape("4.3BSD"),
    source_identity={"archive": "tuhs.org/Archive/Distributions/UCB/4BSD/4.3BSD", "tape_files": "1 stand, 2 miniroot, 3 rootdump, 4 usr.tar"},
    entry_points=["SIMH: boot ts0 -> : ts(0,1)copy -> : hp(0,1)vmunix -> newfs / restore -> boot hp(0,0)vmunix"],
    example={"command": "python -m techne.fossils.harvest run bsd-4.3-distribution-tape-1986", "input": "the four tape files assembled into a .tap image", "output": "a booted 4.3BSD on an emulated VAX-11/780; netstat -s TCP counters around a loopback transfer"},
    upstream_docs=["Installing and Operating 4.3BSD on the VAX (Karels, Leffler, McKusick, Joy; 1986)", "Jacobson, Congestion Avoidance and Control, 1988 (what this release lacks)"],
    human_capability_summary={"built_to": "install a complete 4.3BSD system on a VAX from one tape", "pressure": "the 1986 congestion collapse happened on THIS release's TCP", "success_means": "boots multi-user; TCP answers; netstat -s shows the retransmission counters"},
    known_human_problem_solved="distribution and installation of 4.3BSD",
    human_environmental_pressure="the Internet of 1986: shared scarce links, loss as the only signal, no congestion window yet",
    human_failure_condition="congestion collapse (historical); install failure (tape/disk)",
    behavioral_entry_point="netstat -s before/after a loopback transfer; a second emulated VAX over a lossy Ethernet relay is the boundary (see record notes)",
    acquisition_tags=["batch06", "phase1", "unlock", "depth:tcp", "historical_world", "known_bad_lineage"],
    lineage_relations=[{"relation": "historical_version_of", "to": "bsd-tcp-4.2-1983", "note": "4.3's TCP = 4.2's design + fixes, still no congestion window"},
                       {"relation": "superseded", "to": "bsd-tcp-4.3-tahoe-1988", "note": "Tahoe added slow start / congestion avoidance"}],
    **_tape_common)
spec("bsd-4.3-reno-distribution-tape-1990",
    canonical_name="4.3BSD-Reno distribution tape (June 1990): stand, miniroot, root dump, usr.tar -- fast retransmit / fast recovery TCP, bootable",
    aliases=["4.3BSD-Reno tape", "Reno VAX"],
    lineage="The bootable system containing the Reno TCP (bsd-tcp-4.3-reno-1990): slow start, congestion avoidance, fast retransmit and fast recovery. With the 4.3BSD tape this makes the congestion-control lineage's BEFORE and AFTER both installable under one emulated VAX-11/780; the Tahoe tape between them is cut short in the archive.",
    era="1990",
    version="4.3BSD-Reno (Jun 1990); TUHS Archive/Distributions/UCB/4BSD/4.3BSD-Reno (stand, miniroot, rootdump, usr.tar; FORMAT)",
    source_origin=tape("4.3BSD-Reno"),
    source_identity={"archive": "tuhs.org/Archive/Distributions/UCB/4BSD/4.3BSD-Reno", "tape_files": "1 stand, 2 miniroot, 3 rootdump, 4 usr.tar"},
    entry_points=["SIMH: boot ts0 -> standalone boot -> copy miniroot -> boot -> newfs / restore -> boot hp(0,0)vmunix"],
    example={"command": "python -m techne.fossils.harvest run bsd-4.3-reno-distribution-tape-1990", "input": "the four tape files assembled into a .tap image", "output": "a booted Reno on an emulated VAX; the same loopback pressure as the 4.3 tape"},
    upstream_docs=["4.3BSD-Reno release notes (CSRG, 1990)", "Fall & Floyd 1996 (Tahoe/Reno/SACK comparison)"],
    human_capability_summary={"built_to": "install 4.3BSD-Reno on a VAX from one tape", "pressure": "high bandwidth-delay paths and isolated losses (the Reno redesign's motive)", "success_means": "boots; TCP recovers from a single loss without draining the pipe"},
    known_human_problem_solved="distribution and installation of 4.3BSD-Reno",
    human_environmental_pressure="isolated loss on long fat pipes",
    human_failure_condition="multiple losses in one window still collapse the window (NewReno/SACK pressure)",
    behavioral_entry_point="the same controlled pressure as the 4.3 tape, so the two kernels' netstat -s counters can be set side by side (interpretation is Nyx's)",
    acquisition_tags=["batch06", "phase1", "unlock", "depth:tcp", "historical_world", "successor"],
    lineage_relations=[{"relation": "shares_ancestor_with", "to": "bsd-tcp-4.3-reno-1990", "note": "this tape CONTAINS that kernel"}],
    **_tape_common)


# ============================ PHASE 2: REAL CONCURRENT FAILURE ================================
spec("go-runtime-deadlock-fixtures-1.22",
    canonical_name="Go runtime deadlock regression fixtures (src/runtime/testdata/testprog/deadlock.go, go1.22.0): SimpleDeadlock, LockedDeadlock, LockedDeadlock2, GoexitDeadlock, InitDeadlock",
    aliases=["testprog deadlock.go", "all goroutines are asleep"],
    lineage="The Go runtime's own regression programs for its deadlock detector (checkdead(): 'fatal error: all goroutines are asleep - deadlock!'), kept since Go 1.x and run by runtime/crash_test.go on every release. Each program is a REAL concurrent deadlock -- goroutines blocked on channels/mutexes with no runnable goroutine left -- preserved as the runtime team wrote it; the runtime is the detector, not the fix. The failing programs are not repaired.",
    domain=["concurrency", "deadlock", "failure", "regression-fixture", "runtime", "go"],
    era="2014- (fixtures; Go 1.22.0 = Feb 2024)",
    version="golang/go tag go1.22.0, files src/runtime/testdata/testprog/{deadlock.go,main.go}",
    source_origin={"artifacts": [{"kind": "url", "url": "https://raw.githubusercontent.com/golang/go/go1.22.0/src/runtime/testdata/testprog/deadlock.go", "filename": "deadlock.go", "extract": False},
                                 {"kind": "url", "url": "https://raw.githubusercontent.com/golang/go/go1.22.0/src/runtime/testdata/testprog/main.go", "filename": "main.go", "extract": False},
                                 {"kind": "url", "url": "https://raw.githubusercontent.com/golang/go/go1.22.0/src/runtime/crash_test.go", "filename": "crash_test.go", "extract": False}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"repo": "github.com/golang/go", "tag": "go1.22.0", "path": "src/runtime/testdata/testprog"},
    license={"spdx": "BSD-3-Clause", "status": "permissive", "evidence": "Go LICENSE"},
    language=["Go"], build_system="go run (module-less package main)", compiler_or_interpreter="go 1.22 (docker golang:1.22-bookworm)",
    dependencies=["a Go toolchain"],
    entry_points=["go run . SimpleDeadlock | LockedDeadlock | LockedDeadlock2 | GoexitDeadlock ; crash_test.go names the expected output per case"],
    example={"command": "go run . SimpleDeadlock", "input": "the named fixture", "output": "fatal error: all goroutines are asleep - deadlock! + goroutine dump (exit 2); crash_test.go's expectation is the ORACLE"},
    environment={"runner": "docker", "image": "golang:1.22-bookworm"},
    upstream_docs=["src/runtime/crash_test.go (TestSimpleDeadlock etc.)", "Go runtime proc.go checkdead()"],
    human_capability_summary={"built_to": "keep the runtime's deadlock detector honest: each program must still be recognised as a deadlock on every release",
                              "pressure": "concurrent programs that block forever; a runtime that must tell 'everyone is waiting' from 'someone is still working'",
                              "success_means": "the runtime aborts with the deadlock diagnosis instead of hanging silently"},
    known_human_problem_solved="detection of whole-program deadlock in a concurrent runtime",
    human_environmental_pressure="many actors blocking on each other; no external observer",
    human_failure_condition="a hung program that never terminates and never explains why",
    behavioral_entry_point="run each named case; compare the goroutine dump; edit nothing (the fixtures are the fossil)",
    acquisition_tags=["batch06", "phase2", "deadlock", "executes_concurrency", "regression_fixture"],
    lineage_relations=[{"relation": "shares_ancestor_with", "to": "spin-pathfinder-priority-inversion-1997", "note": "a deadlock found by execution + runtime detector vs one found by model checking"}])

spec("valgrind-helgrind-fixtures-3.19",
    canonical_name="Valgrind 3.19.0 helgrind regression fixtures: tc01_simple_race, tc05_simple_race, tc09_bad_unlock, tc13_laog1 (lock-order inversion), tc19_shadowmem -- real pthread programs with their expected detector output",
    aliases=["helgrind tests", "tc01_simple_race.c", "tc13_laog1.c"],
    lineage="Valgrind's thread-error detector Helgrind (Nethercote/Seward, 2007-) ships regression programs that each commit a specific concurrency error -- unsynchronised access (a RACE), unlocking a lock the thread does not hold, acquiring locks in inconsistent order (the classic DEADLOCK precursor, reported via the lock-order acquisition graph) -- together with the .stderr.exp files the detector must reproduce. Preserved as the failing programs plus the expected traces; run under the detector.",
    domain=["concurrency", "race", "deadlock", "lock-order", "failure", "regression-fixture", "pthreads"],
    era="2007- (fixtures; 3.19.0 = 2022)",
    version="valgrind-3.19.0.tar.bz2 (sourceware), helgrind/tests/",
    source_origin={"artifacts": [{"kind": "url", "url": "https://sourceware.org/pub/valgrind/valgrind-3.19.0.tar.bz2", "filename": "valgrind-3.19.0.tar.bz2"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"archive": "sourceware.org/pub/valgrind", "file": "valgrind-3.19.0.tar.bz2", "path": "helgrind/tests"},
    license={"spdx": "GPL-2.0", "status": "copyleft", "evidence": "COPYING"},
    language=["C (pthreads)"], build_system="gcc -pthread per fixture; run under the distribution's valgrind --tool=helgrind", compiler_or_interpreter="gcc 12 + valgrind 3.19 (Debian bookworm, apt)",
    dependencies=["valgrind (the detector; Debian's 3.19.0-1 matches the fixture version)", "pthreads"],
    entry_points=["helgrind/tests/tc01_simple_race.c (race), tc05_simple_race.c, tc09_bad_unlock.c, tc13_laog1.c (lock order), tc19_shadowmem.c; *.stderr.exp"],
    example={"command": "gcc -pthread tc13_laog1.c && valgrind --tool=helgrind ./a.out", "input": "the fixture", "output": "Helgrind's report ('Thread #N: lock order ... violated' / 'Possible data race'); compared with the shipped .stderr.exp (the ORACLE, modulo addresses)"},
    environment={"runner": "docker", "image": "prometheus-fossil-c:bookworm"},
    upstream_docs=["Valgrind manual, Helgrind chapter", "helgrind/tests/*.stderr.exp"],
    human_capability_summary={"built_to": "make each class of thread error reproducible so the detector's report for it never regresses",
                              "pressure": "races and lock-order bugs are timing-dependent and invisible in normal runs; a detector must find them from one execution",
                              "success_means": "helgrind reports the planted error in the planted place, matching the expected trace"},
    known_human_problem_solved="detection of data races and lock-order deadlocks in pthread programs",
    human_environmental_pressure="nondeterministic scheduling, shared memory without discipline",
    human_failure_condition="silent corruption (race) or an eventual deadlock (lock order) in production, not in test",
    behavioral_entry_point="run a fixture natively (usually 'works') and under helgrind (the error is reported): the same binary, two observers",
    acquisition_tags=["batch06", "phase2", "race", "deadlock", "executes_concurrency", "regression_fixture"],
    lineage_relations=[{"relation": "shares_ancestor_with", "to": "go-runtime-deadlock-fixtures-1.22", "note": "two runtimes' regression corpora for concurrency failure"}])

spec("glibc-rwlock-writer-starvation-2.36",
    canonical_name="glibc 2.36 pthread_rwlock (nptl/pthread_rwlock_common.c): reader-preferring default and the documented writer STARVATION it permits",
    aliases=["pthread_rwlock_common.c", "PTHREAD_RWLOCK_PREFER_READER_NP", "writer starvation"],
    lineage="POSIX read-write locks as glibc implements them: the default kind PTHREAD_RWLOCK_PREFER_READER_NP lets a continuous stream of readers hold a writer off indefinitely -- documented in pthread_rwlockattr_setkind_np(3) ('may result in writer starvation') and in glibc bug reports; the alternative kind PREFER_WRITER_NONRECURSIVE_NP is the corrected behaviour the caller must opt into. Preserved: the 2.36 source of the lock (the machinery), and a harness that drives Debian's glibc (the same version) under reader pressure with both kinds. The lock is not modified.",
    domain=["concurrency", "starvation", "fairness", "failure", "readers-writer-lock", "glibc"],
    era="2017- (this rwlock rewrite, Torvald Riegel); glibc 2.36 = 2022",
    version="glibc tag glibc-2.36: nptl/pthread_rwlock_common.c, nptl/pthread_rwlock_wrlock.c (source); Debian bookworm libc6 2.36 (the running library)",
    source_origin={"artifacts": [{"kind": "url", "url": "https://sourceware.org/git/?p=glibc.git;a=blob_plain;f=nptl/pthread_rwlock_common.c;hb=glibc-2.36", "filename": "pthread_rwlock_common.c", "extract": False},
                                 {"kind": "url", "url": "https://sourceware.org/git/?p=glibc.git;a=blob_plain;f=nptl/pthread_rwlock_wrlock.c;hb=glibc-2.36", "filename": "pthread_rwlock_wrlock.c", "extract": False},
                                 {"kind": "url", "url": "https://sourceware.org/git/?p=glibc.git;a=blob_plain;f=nptl/pthread_rwlock_rdlock.c;hb=glibc-2.36", "filename": "pthread_rwlock_rdlock.c", "extract": False}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"repo": "sourceware.org/git/glibc.git", "tag": "glibc-2.36", "path": "nptl/"},
    license={"spdx": "LGPL-2.1-or-later", "status": "copyleft (library)", "evidence": "file headers"},
    language=["C"], build_system="none (the running glibc is Debian's 2.36; the source is preserved to read)", compiler_or_interpreter="gcc 12 + glibc 2.36 (docker bookworm)",
    dependencies=["glibc 2.36 (system)", "pthreads"],
    entry_points=["pthread_rwlock_rdlock/wrlock with PTHREAD_RWLOCK_PREFER_READER_NP (default) vs PREFER_WRITER_NONRECURSIVE_NP; harness/starve.c"],
    example={"command": "gcc -O2 -pthread starve.c; ./a.out reader 2; ./a.out writer 2", "input": "8 readers re-acquiring continuously for 2 s; 1 writer trying", "output": "writer acquisitions per second under each kind (the STARVATION shows as ~0 under reader preference)"},
    environment={"runner": "docker", "image": "prometheus-fossil-c:bookworm"},
    upstream_docs=["pthread_rwlockattr_setkind_np(3): 'Setting the value read-write lock kind to PTHREAD_RWLOCK_PREFER_READER_NP ... may result in writer starvation'", "glibc nptl/pthread_rwlock_common.c header comment (the algorithm)"],
    human_capability_summary={"built_to": "let many readers share a structure while excluding writers, with a policy choice the standard leaves to the implementation",
                              "pressure": "continuous reader arrivals; a writer whose progress is not guaranteed by the default policy",
                              "success_means": "readers proceed concurrently; a writer eventually acquires -- 'eventually' being the documented weakness"},
    known_human_problem_solved="readers-writer mutual exclusion",
    human_environmental_pressure="asymmetric contention (many readers, few writers)",
    human_failure_condition="writer starvation: updates never land while readers keep arriving",
    behavioral_entry_point="vary reader count and hold time; switch the kind attribute; measure writer acquisitions",
    acquisition_tags=["batch06", "phase2", "starvation", "executes_concurrency", "documented_pathology"],
    lineage_relations=[{"relation": "shares_ancestor_with", "to": "concurrencykit-0.7.2", "note": "ck_rwlock / ck_brlock are rival readers-writer designs with different fairness"}])


def main():
    from .. import record as R
    for rec in S:
        try:
            old = R.load(rec["specimen_id"])
            for k in ("run_classification", "test_classification", "receipts", "hashes", "acquisition_date",
                      "observability", "nyx_handoff"):
                if old.get(k):
                    rec[k] = old[k]
        except FileNotFoundError:
            pass
        probs = R.validate(rec)
        R.save(rec)
        print("%-40s %s" % (rec["specimen_id"], "ok" if not probs else probs))
    print(len(S), "records")


if __name__ == "__main__":
    main()
