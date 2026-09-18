"""Cut: bsd-4.3-distribution-tape-1986 (the plain 4.3BSD tape from the TUHS archive; Stage A ORGAN0; SOURCE_READ on M3; position 65 of the
2026-09-17 NOT_CUT order). Read: FORMAT (nine tape files listed; the vault holds files 1-4: stand, miniroot, rootdump, usr.tar), the tar
listing of usr.tar.gz (3,814 entries: lib/learn, man, doc, lib/lisp, fonts; 0 entries under any netinet path). The kernel source the
record's lineage describes (srcsys.tar, tape file 5) and src.tar (6) are NOT in the vault, exactly as for the 4.3-Reno tape (cut ORGAN0).
Nothing ran (VAX images; no emulator on M3).
"""
from nyx.atlas.author import Cut

FM = "vault:bsd-4.3-distribution-tape-1986/upstream/FORMAT"; U = "vault:bsd-4.3-distribution-tape-1986/upstream/usr.tar.gz"
c = Cut("bsd-4.3-distribution-tape-1986", mode="ANCESTRY_AWARE", inspected=["FORMAT", "usr.tar.gz listing (3,814 entries)"], evidence=[("SOURCE_READ", FM + ":1-9"), ("SOURCE_READ", U + ":tar listing")],
        note="a bootable-system fossil whose value the record assigns ('a BEFORE point for the congestion lineage that, unlike the Tahoe tape, is COMPLETE') depends on tape files the vault does not hold: FORMAT lists stand, miniroot, rootdump, usr.tar, then srcsys.tar, src.tar, vfont.tar, new.tar, ingres.tar; the vault has the first four; usr.tar holds documentation, man pages, learn lessons, Franz Lisp and fonts and no kernel source. The same defect class as the 4.3-Reno tape; the record's 'COMPLETE' is true of the archive, not of the body")

c.reject("the 4.3BSD (1986) TCP, the 'BEFORE' point of the congestion lineage", reason="OTHER", evidence="no netinet path in usr.tar.gz (0 of 3,814 entries); srcsys.tar is tape file 5 and absent from the vault", note="record defect for Techne (second instance of the class after bsd-4.3-reno-distribution-tape-1990): the pre-Tahoe TCP source is the object the record was preserved for and it is not in the body; the vault's bsd-tcp-4.2-1983 (cut) is the nearest source-level BEFORE, and bsd-tcp-4.3-tahoe-1988 (cut this batch) the AFTER")
c.reject("stand, miniroot, rootdump (filesystem images)", reason="OTHER", evidence="binary images; runnable under SIMH only (an M1/M2 world)")
c.reject("usr.tar.gz contents (lib/learn 570, man 900+, doc 700+, lib/lisp 156, fonts)", reason="OTHER", evidence="documentation, lessons, a Lisp system and fonts; no mechanism read", note="lib/lisp (Franz Lisp's library) is a body of its own if anyone wants it")
c.reject("'4.3BSD' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="a distribution is a container")

c.ancestry("shares_ancestor_with", "bsd-4.3-reno-distribution-tape-1990 (the same archive series, the same missing tape files); bsd-tcp-4.2-1983 and bsd-tcp-4.3-tahoe-1988 hold the source on either side of this system", note="by FORMAT and the listing")
c.residue("CUT_INSTRUMENT_INSUFFICIENT", ["filesystem images cannot be dissected by reading", "tape files 5-9 absent from the vault; the record's 'COMPLETE' and 'BEFORE point' claims are not verifiable from the body", "no emulator on M3; nothing ran"], note="ORGAN0 inventory cut; the defect goes to Techne with the Reno tape's")
c.save(state="ORGAN0")
