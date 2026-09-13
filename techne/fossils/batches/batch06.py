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
