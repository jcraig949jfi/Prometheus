# C-017-T042 -- short Q3 re-check of FREEZE_Z80_ATTRIBUTION v1.1.0: PREDICTIONS (committed before the outcome runs)

Reviewer seat: Pallas. Surface: rso/z80 at v1.1.0 (FROZEN.json 3f14bf80, 27 files), base 9bbf984e3, branch pallas/c017-t042.
This is a bounded re-check of the one repair round (C-017-T041), NOT a second open challenge. Seeds: challenge partition
only (17_040_xxx and, for CDIST = arm index 10, 17_070_xxx); never 17_050_xxx or 17_080_xxx; no `assay confirm`.

MODEL-IDENTITY DISCLOSURE (read first). comms boot recorded runtime claude-fable-5-1 (Q3). A harness system message later
in the same session reported the runtime as claude-opus-4-8 (Opus 4.8, Q2). The two conflict. This packet requires Q3
(can_downgrade false). Every finding below is a DETERMINISTIC, independently re-runnable fact (mutant RED/GREEN, VM
invariance, replay equality, freeze hashes) whose validity does not depend on the reviewer's model. Whether the review
satisfies the Q3 PROCESS gate is escalated to Palamedes (s6). Nothing here is fitted to an outcome.

Order note: three checks were run while reading the surface and are verifications of the builder's deterministic claims,
not outcome-fitted predictions -- disclosed as already-run: the 51-test suite (OK), `freeze check` (OK), and the CDIST unit
under the repaired rule (reads=2, tags all K, label ENV). They are repeated in REPORT with that disclosure.

## Predictions

P1 (amendment order). PREREGISTRATION v1.1.0 (7ad0131b7) committed BEFORE FROZEN.json v1.1.0 (fed35e840). Expect: amendment
timestamp strictly precedes the re-freeze; FROZEN.json LF sha256 = 3f14bf80..; engine hashes unchanged from v1.0.0.

P2 (reads rule, R1). The repaired P tag makes a parent that read the window (reads_nbr>0) write no P byte. Expect CDIST unit
over kin: tags all K, label ENV; and the R1 mutant (drop the reads->K clause) RED on test_a_parent_that_reads_the_window_
writes_no_parent_byte.

P3 (reads-rule residual: can a parent depend on the target WITHOUT a counted read?). Channels: exec_foreign and SEAL (the
only window reads the VM does not count on reads_nbr). Expect: SEAL cannot move a target byte into a register without a
counted LD/COPY, so it yields no target-dependent P-tagged function byte. exec_foreign changes registers from executed
target bytes (invariant byte-pairs exist), but control returns only by fall-through to the pc wrap at byte 0, where any
register preset re-runs and clobbers the target-derived value, and a target HALT stops the parent before a store. Expect:
NO scored exec_foreign/SEAL escape constructible; the reads channel is CLOSED; the exec_foreign/SEAL residual remains as
PREREGISTRATION s11.5 already states (NOT CLOSED in principle, undemonstrated), now with a construction obstruction.

P4 (CDIST arm as a scored ENV class). CDIST_ENDO_IMPL at 5 epochs on challenge seeds 17_070_001..004. Expect run class ENV
(majority), b4 = ENDO, b1 = ENDO on the same records: the scored "recipe/label say ENDO, instrument says ENV, truth is ENV"
row the v1.0.0 set lacked. n_ENDO may be nonzero (organism-level) but not a majority.

P5 (b4 as a baseline that must fail for the stated reason). b4 is right on all ten v1.0.0 recipes and reads CDIST's recipe
as ENDO (its only error), so Q4 can fail b4 ONLY through the CDIST rows. Expect: b4 correct on all arms except CDIST
(cls=ENDO where gt=ENV); its sole Q1 error class is ENV, and only from CDIST.

P6 (Q2 narrowing). A constant INSERTED detector: expect w_max(n) at the confirmatory Q2 n (~267) is ~38, far above the
~24 ARISEN rows the run can produce, so a constant passes Q2 for every outcome. Q2 tests INSERTED origin only (as narrowed).

P7 (the new tests are RED on their mutants). Expect R1, R3, E1 and E3 each turn their named frozen test RED when applied
in place and GREEN when restored; suite otherwise GREEN; freeze check OK after restore.

P8 (my v1.0.0 witnesses under the reads rule). XORW (W1) reads the window (two LD A,(imm) from 128/130), so under v1.1.0
every XORW byte is K -- the reads rule SUBSUMES W1, which is why the builder re-pinned E1 via the exec-only XEXEC. INPW
(W5) does not read the window (writes input, copies own), so its byte 0 stays P. Expect W1 -> all K (changed), W5 -> byte 0
P (unchanged), W2/W3 label/verdict unchanged.
