"""Cut: bsd-4.2-distribution-tape-1983 (the 4.2BSD tape from the TUHS archive; Stage A ORGAN0; SOURCE_READ on M3; position 91 of the
2026-09-17 NOT_CUT order). Read: FORMAT (nine tape files; the vault holds files 1-3 and 5: stand, miniroot, rootdump, usr.tar), the tar
listing of usr.tar.gz (include/netinet is present as HEADERS; no kernel .c under any netinet path). The kernel source the record leans on
(srcsys.tar, tape file 4) is NOT in the vault, the same defect class as the 1986 and Reno tapes. Nothing ran (VAX images; no emulator on
M3). This is the third distribution-tape fossil; the BEFORE point of the congestion lineage as SOURCE is bsd-tcp-4.2-1983 (cut COARSE).
"""
from nyx.atlas.author import Cut

FM = "vault:bsd-4.2-distribution-tape-1983/upstream/FORMAT"; U = "vault:bsd-4.2-distribution-tape-1983/upstream/usr.tar.gz"
c = Cut("bsd-4.2-distribution-tape-1983", mode="ANCESTRY_AWARE", inspected=["FORMAT", "usr.tar.gz listing"], evidence=[("SOURCE_READ", FM + ":1-9"), ("SOURCE_READ", U + ":tar listing")],
        note="a bootable-system fossil: the record's purpose ('preserved so that the kernel in bsd-tcp-4.2-1983 can be BOOTED under emulation') depends on tape files the vault does not hold. FORMAT lists nine files (stand, miniroot, rootdump, srcsys.tar, usr.tar, vfont.tar, src.tar, new.tar, ingres.tar); the vault has stand, miniroot, rootdump and usr.tar. srcsys.tar (file 4, the kernel source) is absent; usr.tar carries include/netinet (headers) but no netinet/*.c. Same defect class as bsd-4.3-distribution-tape-1986 and bsd-4.3-reno-distribution-tape-1990; the pre-Tahoe TCP SOURCE is the cut bsd-tcp-4.2-1983")

c.reject("the 4.2BSD kernel (the BEFORE point of the congestion lineage) 'bootable' from the tape", reason="OTHER", evidence="srcsys.tar (tape file 4) absent from the vault; usr.tar.gz has include/netinet headers only, no netinet/*.c; the bootable images (stand, miniroot, rootdump) need a VAX emulator (an M1/M2 world)", note="record defect for Techne (third instance of the class): the object the tape is preserved for -- a bootable kernel -- needs the missing source tape file or an emulator; the source itself is in bsd-tcp-4.2-1983 (cut)")
c.reject("stand, miniroot, rootdump (VAX filesystem images)", reason="OTHER", evidence="binary images; runnable under SIMH only")
c.reject("usr.tar.gz contents (bin, adm, include/netinet headers, man, doc)", reason="OTHER", evidence="userland and headers; no mechanism-bearing kernel source read")
c.reject("'4.2BSD' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="a distribution is a container")

c.ancestry("shares_ancestor_with", "bsd-tcp-4.2-1983 (the SOURCE of the TCP this system runs); bsd-4.3-distribution-tape-1986 and bsd-4.3-reno-distribution-tape-1990 (the same archive series with the same missing source tape file)", note="by FORMAT and the listing")
c.residue("CUT_INSTRUMENT_INSUFFICIENT", ["filesystem images cannot be dissected by reading", "srcsys.tar and the other source tape files absent from the vault; the record's 'bootable kernel' purpose is not served by the body", "no emulator on M3; nothing ran"], note="ORGAN0 inventory cut; the three distribution tapes now share one repair note for Techne (complete the source tape files or narrow the records to what the vault holds)")
c.save(state="ORGAN0")
