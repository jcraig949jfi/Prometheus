"""Cut: bsd-4.3-reno-distribution-tape-1990 (the 4.3BSD-Reno distribution tape from the TUHS archive; Stage A COARSE, inventory only;
position 38 of the 2026-09-17 NOT_CUT order). The body is five files: FORMAT (a seven-line tape-file list), stand.gz, miniroot.gz,
rootdump.gz (filesystem images for an emulated VAX) and usr.tar.gz (4,188 entries: man pages, share/, libdata/, contrib/, include/).
Read: FORMAT; the tar listing of usr.tar.gz (grouped by top-level directory); the record. NOT dissectable as source: the tape files
5-7 that FORMAT names (src.tar, srcsys.tar, contrib.tar) are NOT in the vault, so the kernel source that would carry the Reno TCP is
absent; usr.tar.gz carries include/netinet headers and adb scripts (libdata/adb/tcpcb, tcpip, tcpreass) but no tcp_*.c. Nothing ran
(a VAX image; no emulator on M3). This cut records what the body IS and links it to the source body it was preserved to accompany.
"""
from nyx.atlas.author import Cut

U = "vault:bsd-4.3-reno-distribution-tape-1990/upstream/usr.tar.gz"; FM = "vault:bsd-4.3-reno-distribution-tape-1990/upstream/FORMAT"
c = Cut("bsd-4.3-reno-distribution-tape-1990", mode="ANCESTRY_AWARE", inspected=["FORMAT", "usr.tar.gz listing (4,188 entries)", "record.json"], evidence=[("SOURCE_READ", FM + ":1-7"), ("SOURCE_READ", U + ":tar listing")],
        note="a bootable-system fossil, not a program: the value the record assigns it ('the congestion-control lineage's BEFORE and AFTER both installable under one emulated VAX') depends on tape files the vault does not hold (src.tar, srcsys.tar per FORMAT lines 5-7), and on an emulator no seat has. No organ can be cut from filesystem images by reading; the source-level dissection of the Reno TCP is the bsd-tcp-4.3-reno-1990 cut in this atlas")

c.reject("the Reno TCP (slow start, congestion avoidance, fast retransmit, fast recovery) 'contained' in the tape", reason="OTHER", evidence="usr.tar.gz lists include/netinet headers and libdata/adb/tcp* debugger scripts only; no netinet/tcp_*.c; FORMAT names src.tar and srcsys.tar as tape files 5-6 and the vault holds files 1-4", note="the record's lineage sentence is true of the TAPE and not of the BODY in the vault; the source is in bsd-tcp-4.3-reno-1990 (cut, DEEP); record defect for Techne: the vault body cannot carry the kernel it is described by")
c.reject("stand, miniroot, rootdump (filesystem images, 2.1-3.3 MB each uncompressed)", reason="OTHER", evidence="binary images; not readable as mechanism; runnable only under a VAX emulator (SIMH), which the base role lists as an M1/M2 docker world, not M3")
c.reject("usr.tar.gz contents (man pages 1,336 entries; share/doc 531; libdata; contrib/lib 410; games)", reason="OTHER", evidence="documentation and userland data; no mechanism-bearing source seen in the listing", note="share/man/cat4/tcp.0 is the formatted manual page for the Reno TCP: a documentation fossil, not a body")
c.reject("'4.3BSD-Reno' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="a distribution is a container; its mechanisms live in the source bodies")

c.ancestry("shares_ancestor_with", "bsd-tcp-4.3-reno-1990 (in this atlas): the tape is the system that shipped that TCP (the atlas has no CONTAINS relation; Techne owns the vocabulary); the vault's copy of the tape omits the source tape files", note="by FORMAT and the tar listing")
c.residue("CUT_INSTRUMENT_INSUFFICIENT", ["filesystem images cannot be dissected by reading", "tape files 5-7 (src.tar, srcsys.tar, contrib.tar) absent from the vault: the record's 'contains the Reno TCP' is not verifiable from the body", "no emulator on M3; nothing ran"], note="recorded as an inventory cut with zero organs so the census counts it as inspected; the defect is Techne's to rule on (complete the tape or narrow the record)")
c.save(state="ORGAN0")
