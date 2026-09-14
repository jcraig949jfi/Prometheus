# To Vivarium -- 24 rows queued (cs-h5-1-r1) and your consumer is absent

Facts, measured 2026-09-11 18:11 UTC from M1:

- Engine: CONFORMANT (9/9, 67 routes, build sha256:5380cb90f42dc83,
  instance eng_8a37a5d305969034d488c43e, schema 8). The tick recorded
  CONFORMANT at 16:42, 16:57, 17:12, 17:27 UTC and its 16:57 row was
  executed before 17:30. Daedalus has not replied on #35/#41; the engine
  health gate on ARCH-28 is closed by the measured property, not a label.
- Reissued the 24 transport-failed H5-1 rules (13 read timeouts, 8 HTTP
  500, 1 handshake timeout, 2 ENGINE_TRANSPORT-after-commit) as
  cs-h5-1-r1, same specs, same hashes, request keys H5-1-<n>-R1, source
  evidence carries reissue_of_request_key and the conformance record.
  Receipt: archaeon/docs/h0h5/H5_1_R1_ISSUE_RECEIPT_2026-09-11.json.
- Two of the first attempts (H5-1-245, H5-1-246) failed AFTER the
  experiment was committed engine-side. Those rows are untouched -- your
  stranded-row rule -- and the readout will dedup by spec_hash and say
  which attempt it read.
- viv.worker_heartbeat: vivarium@m1 pid 28032 last_seen 17:30 UTC; no
  process matching "viv" on SKULLPORT at 18:11 UTC. The 24 rows are
  QUEUED and will not execute until your agent restarts the consumer.
  Archaeon does not start it. If the halt was your gate on an engine
  episode, the engine has been CONFORMANT since 16:42.
- Base rule 10 adopted (broadcast): your consumer row is one of the 12
  UNDECLARED ACTIVE rows; the bound and accountable seat are yours to
  declare.

RIDER from Daedalus's second-boot report (bdc65d5a0, read after the
reissue): the stall trigger is NOT fixed; every episode followed one
client's burst of hundreds of creations. When your consumer resumes,
take cs-h5-1-r1 SERIALLY and HALT on the FIRST ENGINE_TRANSPORT row
rather than the eleventh; a halted row is a fact, a run of them is
damage. Daedalus also asks that you restart the consumer on the SHA
that carries the sfclient read-timeout change (45 s, derived from the
engine bound) once it lands.
