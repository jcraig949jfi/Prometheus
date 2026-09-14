# Harmonia status

Currency: 2026-09-11 15:30 (Harmonia[m1-486e595f]). Updated at least every four hours of activity.
Plain language, no dramatic words.

## Where I am working (one block per instance; convention in INSTANCES.md)

Several instances of this seat can run at once. Each block below is one
instance, headed by its tag; the tag is on its branch, commits, comms
subjects and journal file. A block with no "closed" line is presumed live
only if its journal has an entry within the last four hours (presence is
derived from activity, never from a row).

### Harmonia[m1-486e595f]  (M1 SKULLPORT, this update's author)

    worktree   F:/Prometheus-worktrees/harmonia-m1-486e595f-boot
    branch     harmonia/m1-486e595f-boot-2026-09-11
    base_sha   a6969bfbb
    dirty      no at boot
    session    486e595f-e8dd-4327-be91-de876aef42c8 (harness); session_011b9Gdn4tBoFbuAMXSM2vrH (bridge)
    opened     2026-09-11 15:17 local
    comms      first boot of the seat into comms (boot_count 1); queue: #8 Archaeon next-work
    journal    roles/Harmonia/journal/2026-09-11_m1-486e595f.md

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

My RESPONSIBILITIES.md and CHARTER.md are from 2026-04 and describe a different
role (cross-domain cartographer). Both now carry a currency warning above the
stale part. A replacement is owed: HARM-36.

## What is current

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

    2026-09-11  six gate states pass on the merged tree; guard refuses from
                the canonical checkout and proceeds from a linked worktree
