# C-004 S4 triage of the S3 first-sight challenge (C-004-T040)

Palamedes, coordinator, 2026-10-05. Input: rso/slice001/challenge/S3/REPORT.md (Pallas, T030, integrated
bddb3c71d). The first-sight score is preserved unchanged: sound 4/5, broken 3/5, controls 2/2; edits 10
proposed / 10 applicable / 10 executed / 5 killed / 5 survived / 0 equivalent / 0 error / 0 timeout.
One repair round (plan s2 S4; OP-1). No case expectation changes; no contract amendment (OP-5 rule).

    item                         disposition      repair (one round)                                     owner
    ---------------------------  ---------------  -----------------------------------------------------  -------
    F1 CHANNEL clamp trace       IMPLEMENTATION   adapter._clamp_hook must clamp into the SAME instance,  Argus
       (G-RECOMP false accusal)                   as the registered instrument reset.channel /
                                                  clamp_answers does (A5 P5 "capture, set a := v,
                                                  restore": the same runtime); add a test with a runtime
                                                  whose capture omits state (S3_INVERT-like) where
                                                  receipt CHANNEL and recomputation agree
    F2 keeper manifest rows[-1]  IMPLEMENTATION   anchors_from_keeper selects the EVIDENCE_MANIFEST row   Argus
       (custody QUALIFIED on a                    of THIS bundle (by its manifest path or identity), and
       foreign manifest)                          custody refuses anchors whose manifest omits the
                                                  bundle's nodes; test: two registered manifests
    F3 G-INV borrowed run        IMPLEMENTATION   B3.3 (run_id = the inventory row that launched it) +    Argus
       (false admission)                          V7 (rows record the node_id they launched): G-INV FAIL
                                                  RECEIPT_WITHOUT_RUN when the cited row's node_id is not
                                                  the receipt's; test = S3.BROKEN.RUN_BORROW. (The
                                                  reviewer's alternative reading, B6.4 literal, is not
                                                  taken.)
    probe MEASUREMENT_LIE        IMPLEMENTATION   G-BIND checks cell.measurement == predicate version of  Argus
                                                  predicate.code (B3.2 defines it; nothing enforced it)
    E07 G-RECOMP horizon         TEST GAP         fire test: forbidden influence at lag exactly H = 3 in  Argus
                                                  the consumer recomputation
    E09 gate withdrawal          TEST GAP         fire test: withdrawing a consumer gate's own stage      Argus
                                                  record makes that gate UNQUALIFIED
    E10 suspension               TEST GAP         fire test separating unresolved = 0 from 1 (A4)         Argus
    E01 ERASE horizon            TEST GAP         fixture with forbidden influence at lag exactly H = 3   Cadmus
    E02 ERASE sends              TEST GAP         fixture leaking only through CUE sends                  Cadmus
    probe OBS_TRANSPLANT         CONTRACT (S5)    reason IDENTITY_MISMATCH:node_id not listed in B6.3     --
    O1 vacuous PRESERVE          S5 OBSERVATION   P4 says nothing for a runtime whose reset writes `a`    --
    probe VERSION_DRIFT          AS DESIGNED      --                                                      --

After the repair round (T042 Argus, T043 Cadmus), every instrument whose version changed loses its stage
(B4.1): new AUTHOR_TESTED fire receipts and records, registered with Aporia; then the S4 regression rerun of the
S2 matrix on the repaired code (F1 changes every bundle's CHANNEL trace, so all five bundles); then the
reviewer's fresh closure set (T041: 2 sound, 2 broken, 3 edits on touched predicates).

Caps (contract v1.0.3): launches 8 of 12 used; S4 needs about 8 (5 regression bundles + suite + cases +
mutation). CPU: about 42 ledgered minutes remain, enough. The launch cap needs an operator decision (OP-7).
