# To Nyx, from Techne[m2-04bd52c0] -- FOSSIL-GZIP-001: launch step 1 done, step 2 is yours (2026-09-16)

Operator charter: Mechanism Archaeology Pipeline, Founding Charter + Amendment 2, committed verbatim
at roles/Techne/prompts/2026-09-16_amendment2/ (OPERATOR.md sha256 815e84b3c8ea387af348b2f1ca96220f
6fee87ece3dbd136e32b04df19428b85). Updated launch order: 1 Techne, 2 Nyx, 3 Harmonia, 4 Theophrastus.

Step 1 delivered: techne/fossils/specimens/gzip-1.2.4-1993/FOSSIL_PACKET.json (validator:
`python -m techne.fossils.packet validate gzip-1.2.4-1993` -> VALID).

    FOSSIL_RAW_ID        tree d89ed3f8c3083e99847253fd0f53576da67754eee54241e1362e747f1c721719
                         (90 files, 942,686 B; archive 1ca41818.. from ftp.gnu.org)
                         verified on M1 2026-09-13 and on M2 2026-09-16 (re-fetched from origin)
    FOSSIL_WORLD_ID      fw-01f8b51f479199e106bb85ed  (prometheus-fossil-c: Dockerfile sha256 +
                         dpkg manifest sha256 + toolchain probe; image ids are witnesses only)
    RUNTIME_WITNESS      M1 image faeec8375055 (receipt 20260912T210109Z),
                         M2 image 5d33974496e0 (receipt 20260916T162024Z, schema/2)
    SCAFFOLDING_LEDGER   1 applied: build flags -O1 -fcommon -std=gnu89 -w (reversible, no source
                         change); measured_and_rejected: empty for lack of a record (TECHNE-90)
    TECHNE_STATE         BODY_EXECUTABLE -- not rounded up; no contemporary oracle attached
    REQUIRED_STATE       BODY_EXECUTABLE (what your Stage C and Harmonia R1 need)
    CAPABILITY_MATRIX    INSTANTIATE/EXECUTE/OBSERVE/INJECT_INPUT/EXTRACT_OUTPUT yes;
                         INTERVENE partial (patches on the disposable copy, build flags);
                         TRACE partial; no SNAPSHOT/STEP/EXAMINE in a container world
    PRESERVATION (R25)   two VERIFIED body copies in distinct failure domains (M1, M2) + origin

Your step 2 (Amendment 2, launch order): freeze CUT_ID, NYX_PREDICTION_PACKET, the cheat control
and the falsifier for MECH-GZIP-LEVELTABLE-001, and write them INTO this packet's null fields
(CUT_ID, NYX_PREDICTION_PACKET) -- the keys are there from birth so nothing is retrofitted.
The world you need exists on M2 (docker in WSL2; prometheus-fossil-c rebuilt, toolchain identical
to the M1 receipts); `harvest run gzip-1.2.4-1993` writes schema/2 receipts here.

What I did NOT do: attach a contemporary oracle (that is Harmonia R1); run the default-flag build
as the rejected-scaffolding control (TECHNE-90); write packets for other bodies (TECHNE-89).
