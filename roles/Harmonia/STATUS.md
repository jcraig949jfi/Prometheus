# Harmonia status

Currency: 2026-09-17 15:25 UTC (Harmonia[m2-038758c6]). Updated at least every four hours of activity.
Plain language, no dramatic words.

## Where I am working (one block per instance; convention in INSTANCES.md)

Several instances of this seat can run at once. Each block below is one
instance, headed by its tag; the tag is on its branch, commits, comms
subjects and journal file. A block with no "closed" line is presumed live
only if its journal has an entry within the last four hours (presence is
derived from activity, never from a row).

### Harmonia[m2-038758c6]  (M2 SPECTREX5, 2026-09-16, this update's author)

    worktree   D:/Prometheus-worktrees/harmonia-m2-038758c6-boot
    branch     harmonia/m2-038758c6-boot-2026-09-16
    base_sha   b3e62a959
    dirty      no at boot
    session    038758c6-2210-4d29-8492-f1f69d463240 (harness); session_01APeC753MberhMK4TGqo6jD (bridge)
    opened     2026-09-16 15:50 UTC
    comms      booted; sync 6 new / 0 queued (#269 #270 #282 #288 #295 #301); EW_DB_HOST=192.168.1.202
               required on M2 (WRONG_ENVIRONMENT otherwise, incident c84e26826cc12217)
    measured   M2 engine 192.168.1.191:8811 UP as the twin eng_906356f7 (build 726275da, schema 8);
               M1 192.168.1.202:8811 TIMEOUT. The ledger move (#270 steps 1-2) has not happened.
    working    step-3 PRECHECK done: promote refuses on ledger only (exit 2, nothing written);
               gate DRIFT on engine_instance_id only; CONFORMANT 68/68 with the twin id.
               #295 answered: contract models required query + no responses; include_spec and
               the two fields are invisible; the new build needs its own candidate.
               #282 G1/G2 reproduced independently (diff < 1e-14); GO as computed; issue = operator.
    superseded step 3 (promote 726275da) is MOOT: operator re-ruled in chat (SFE on M2 on its own
               ledger); Daedalus a1dd1458c launched production eng_906356f7 build 4dbcd3fd and landed a
               regenerated contract in roles/Harmonia/contracts/ under the operator's clearance;
               the 726275da candidate is superseded. Not yet re-verified by this seat (HARM-43 open).
    lane 2     MECHANISM ARCHAEOLOGY (Amendment 3 received from the operator in chat; RESPONSIBILITIES s8):
               #309 claimed; ACK #316; ruler CALIBRATED on RS_CALIBRATION_PAIR_001 (R-ID-1/2 IDENTICAL,
               R-DIV-1 DIVERGENT 1865/2000 + a 33/2000 word-level divergence nobody listed; controls
               clean); RETURN 1 CUT_SUPPORTED + ACCEPT; RETURN 2 PREDICTION_PACKET_CHALLENGE on
               MECH-GZIP-LEVELTABLE-002 (switch is at deflate.c:672, packet says 667; I2 unexecutable
               as written); packet 003 requested from Nyx. R1 opens against 003.
    2026-09-17 branch fast-forwarded to origin/main 3a671820b, no conflicts, nothing unpushed. #319: both
               returns ACCEPTED, packet 003 frozen 5dbf46a2 (re-hashed here: matches); R1 OPEN. #341 Proteus
               question UNANSWERED (HARM-44). Daedalus landed a schema-9 contract in my lane (fbfcfb276).
    next       HARM-38 (grade gzip oracle sources), HARM-39 (oracle corpus in fw-01f8b51f); then HARM-43
               (re-verify Daedalus's landed contract with my gate from this worktree); HARM-30/31 after.
    journal    roles/Harmonia/journal/2026-09-16_m2-038758c6.md

### Harmonia[m1-486e595f]  (M1 SKULLPORT; author of the 2026-09-11 update)

    worktree   F:/Prometheus-worktrees/harmonia-m1-486e595f-boot
    branch     harmonia/m1-486e595f-boot-2026-09-11
    base_sha   a6969bfbb
    dirty      no at boot
    session    486e595f-e8dd-4327-be91-de876aef42c8 (harness); session_011b9Gdn4tBoFbuAMXSM2vrH (bridge)
    opened     2026-09-11 15:17 local
    comms      first boot of the seat into comms (boot_count 1); queue: #8 Archaeon next-work
    journal    roles/Harmonia/journal/2026-09-11_m1-486e595f.md

### Harmonia[m2-54a6d694]  (M2 SPECTREX5, operator label "Harmonia A"; 2026-09-14)

    worktree   D:/Prometheus-worktrees/harmonia-a-boot-2026-09-14
    branch     harmonia/m2-54a6d694-boot-2026-09-14
    base_sha   0100d36cd
    dirty      no at boot
    session    54a6d694-ea3e-4ec9-b06c-633b5dbbac7d (harness); session_01NiqLgAgvtKZL7txRJoYXzZ (bridge)
    opened     2026-09-14 06:20 local
    comms      booted Harmonia[m2-54a6d694]; CLAIMED #215 (Daedalus contract step); #8 not claimed by me
    working    #215 DONE on my side: candidate contract for 726275da STAGED at contracts/candidates/726275da9c8d/,
               12/12 rows; promote_candidate_contract.py runs in Daedalus's deploy window AFTER the restart.
               Found: generator crashed at import on main since 7d302b5ae (fixed).
               Landed 671378c47 (merge 3da6c2439); report posted comms #256; #215 done.
    blocked    nothing on me for #215; promotion waits on Daedalus's restart onto 8c53d04e6
    journal    roles/Harmonia/journal/2026-09-14_m2-54a6d694.md

### Harmonia[m2-f541bed9]  (M2 SPECTREX5, operator label "Harmonia B"; 2026-09-14)

    worktree   D:/Prometheus-worktrees/harmonia-m2-f541bed9-boot
    branch     harmonia/m2-f541bed9-boot-2026-09-14
    base_sha   0100d36cd
    dirty      no at boot
    session    f541bed9-2bbc-47c0-8e08-dbb9062252c9 (harness); session_01G7RAgrwhQkn4RRf2yn3sKE (bridge)
    opened     2026-09-14 06:37 local
    comms      booted Harmonia[m2-f541bed9]; LOST #215 to m2-54a6d694 (handed it two traps, c4ea5840b / #254);
               CLAIMED #8 (Archaeon next work, four items)
    working    #8 item 1 DONE: RULING_3B_C3_3_PREFLIGHT_2026-09-14.md (be82cdd8b, #255) --
               C3-3 preflight NO-GO as printed (region gate a constant; 8.46 of 10 expected,
               P(all >= 8) 0.123); GO predicate G1-G6 mechanical; 3a/3b/3e/3f amended.
               #8 item 2 DONE: RULING_H1H0_PHASE2_CONTRASTS_2026-09-14.md (341a92b89, #257) --
               measures the instrument, not H0; G on vm_ops censoring-determined; CROSS-DEPLOY.
               #8 item 3 DONE on synthetic evidence: RULING_D3V2_CALIBRATION_2026-09-14.md
               (ca0dd0fd7, #259) -- d3.v2 ADMITTED at LIVE geometry, REFUSED at FLOOR/UNEQUAL;
               live use PENDING the v2 dossier delegated to Archaeon (#260).
               #8 item 4 (HARM-36) DONE in the commit that carries this line.
    blocked    nothing on me. Waiting on: Archaeon (C3-3 re-run preflight, option B or D;
               v2 live dossier #260). Operator: C3-3 issue decision.
    journal    roles/Harmonia/journal/2026-09-14_m2-f541bed9.md

### untagged instance, session_015xemUgVDH2DmFqYARdV8Gi  (M1, wrote the block below before tags existed)

    worktree   F:/Prometheus-worktrees/harmonia-hygiene
    branch     harmonia/workspace-hygiene-2026-09-11
    base_sha   2627fe37c
    dirty      no
    last seen  commit 5a99e9627 at 2026-09-11 05:38; worktree present and clean at 15:17

### untagged instance, session_01L96WUARbNnjNQgTXrxwX29  (M2 SPECTREX5)

    last seen  commit 29fc3ff4e (packet 02) at 2026-09-11 06:36; worktree unknown from M1

## What this seat is

The scientific audit and qualification seat for the SFE/PEW program. Units of
analysis, detector calibration, preregistration, claim boundaries, the
conformance contract, and the H0-H5 qualification gates. I adjudicate other
seats' claims against executable checks; I run no experiment of my own and no
long-lived process.

RESPONSIBILITIES.md and CHARTER.md were rewritten for this role on 2026-09-14
(HARM-36, Harmonia[m2-f541bed9]); the 2026-04 cartographer files are preserved
verbatim under roles/Harmonia/superseded/.

## What is current

    lane 2 (2026-09-16)  Mechanism Archaeology Pipeline, Harmonia stage (R1-R4);
                         equivalence ruler calibrated; FOSSIL-GZIP-001 at R1

    QR-1.1.0            H0-H5 qualification rules; contrast variance is
                        c' Sigma c, estimated per lane on a disjoint pilot
    AF-1.0.0            six adversarial fixtures, 6/6, no LLM in any path
    H4-ADAPTIVE-1.0.0   H4's protocol; distinct from M-SIGNAL
    d3.v1               pooled-within denominator, admitted; exchangeability
                        diagnostic declared at |r| 0.577 / 0.816
    contract            schema 8, 67 routes, 61 scoped, 6 exempt
    gate                four states 0/1/2/3, six-way verification passing

## Open, and on whom

    Archaeon    step 5: wire the conformance gate into Archaeon and Vivarium.
                Everything else in the contract lane is finished and unused.
    Archaeon    d3.v1 exchangeability diagnostic; C3-3 from my declared rules
    Daedalus    A0 (engine response models) blocks HARM-35
    Herakles    accept or refuse T=320 as at_T for the six C3 genomes
    Operator    the harmonia-m2 credential; C7 deploy authority; d3.v2
    Vivarium    a worktree lives inside the canonical checkout and is LOCKED

## Last verified

    2026-09-16  promote_candidate_contract.py and conformance_check.py run from
                a linked worktree against the M2 twin: refuse / DRIFT on the
                ledger identity only, CONFORMANT 68/68 once the identity matches
    2026-09-11  six gate states pass on the merged tree; guard refuses from
                the canonical checkout and proceeds from a linked worktree
