# 48H campaign hourly status log (append-only)

```
COSMOS / CWE -- 48H AUTONOMOUS CAMPAIGN
======================================================================
hour          1/48  (2026-10-08T06:00Z; start 05:26Z)
host          ubu003
model         claude-opus-5-5
branch        main 8ada21830 (records) | cosmos/c4-v03 b86466ac0 (C4 repairs)
head          8ada218306
state         REPAIRING
science       can C4 coordinates explain usability without remeasuring it?
experiment    reviewer-attack reproduction + planted calibration (no real worlds scored)
tests         full suite 112/0/0 on merged tree; c4 new 40/0/0
runtest       NOT RUN this window (pytest suite PASS)
worlds        planted only: Reservoir 20x3k (R-MECH grid), XorCue, HiddenCarrier
laws          proposed 0 | killed 0 | provisional 0
coordinates   LOCAL v0.3: rho, eta, gamma, vis (one-step, decoder-free)
attacks       A1 cheat 0/20 pass (was 200/200); F1 REL@q cheat -> HorizonError;
              S2 planted universal .93 pass, family-specific 0/60
finding       local one-step physics composes to predict 48/48 planted Reservoir
              labels in-sample (calibration, not evidence)
failure       S2 calibration-LRT falsely rejects 30% of planted universal laws
              (replaced); Cert A seed-unstable on XOR (F/P/I/P/F)
next          C4 DESIGN v0.3 text; LOCAL coords on theseus_sediment + C3 families
compute       ~1.5 CPU-h / <1 GB / $0
holdouts      D2 SEALED / UNREAD / UNSPENT
======================================================================
```

```
COSMOS / CWE -- 48H AUTONOMOUS CAMPAIGN
======================================================================
hour          2/48  (2026-10-08T07:05Z)
host          ubu003
model         claude-opus-5-5
branch        main (records) | cosmos/c4-v03 e68cc51e14
head          e68cc51e14
state         EXPERIMENTING
science       does a LOCAL one-step composition law (C4-L-0003, local Fisher
              memory curve) predict usability across families?
experiment    EXP-02: 120 challenge-proposal DISCOVERY worlds, frozen theta
tests         c4 suite 50/0/0 (new); full suite last 112/0/0
runtest       NOT RUN (pytest PASS)
worlds        EXP-01 120 (rnn/graph/stig/sediment, P) | EXP-02 120 running (Q)
laws          proposed 2 (L-0001, L-0003) | killed 0 | provisional 2 (by rule)
coordinates   LOCAL: lam, eta, gamma, vis; local LGSS (J, B, Q, C)
attacks       stig: moving-sensor reachability defeats both local laws;
              S0-A family-floor over-strict (fails 65% of true laws) -> tests
finding       L-0003 BA 1.00 rnn, .86 graph, but only +.024 over T3-DOWN;
              local linearization is FRAME-DEPENDENT (stig abs vs agent frame)
failure       foreign family uninformative under P (30/30 FUNCTIONAL); my own
              A1 floor rule was a new over-strictness (repaired v0.3a)
next          EXP-02 verdicts; ego-frame test; realistic power v0.3a
compute       ~4 CPU-h / <2 GB / $0
holdouts      D2 SEALED / UNREAD / UNSPENT
======================================================================
```

```
COSMOS / CWE -- 48H AUTONOMOUS CAMPAIGN
======================================================================
hour          3/48  (2026-10-08T08:10Z)
host          ubu003
model         claude-opus-5-5
branch        main (records) | cosmos/c4-v03 cd5f489284
head          cd5f489284
state         RESEARCHING
science       is the usability boundary in local-FMC units common across
              families once certificate sensitivity is controlled?
experiment    EXP-02 analysed; R-STAT final (REVISE) being reconciled
tests         c4 suite 50/0/0; full suite last 112/0/0
runtest       NOT RUN (pytest PASS)
worlds        240 discovery (EXP-01 P 120, EXP-02 Q 120), 4 families
laws          proposed 3 (L-0001, L-0003, L-0004 cand.) | killed 0 |
              provisional 2 by rule (L-0001, L-0003)
coordinates   LOCAL lam/eta/gamma/vis (family fingerprint .91); composed
              local-FMC log d2 (family-ID .43)
attacks       frozen-theta transfer to challenge worlds; foreign family;
              3 stig explanations refuted; S2 on A and B labels; B5 family-ID
finding       frozen L-0003 BA .96-1.00 on graph/rnn/FOREIGN sediment under Q;
              B-label boundaries collapse (log d2 -3.6/-3.6/-4.0, offset p .94)
failure       NOT a calibrated curve across families (ordinal only);
              stig unexplained (Spearman .14); A-label offset = cert. power
next          A14 class-count rule, A15 effect-size floor, B1 new mechanism,
              contract adapters; reconciliation after R-MECH final
compute       ~7 CPU-h / <2 GB / $0
holdouts      D2 SEALED / UNREAD / UNSPENT
======================================================================
```

```
COSMOS / CWE -- 48H CAMPAIGN FINAL RECEIPT (late: written 2026-10-11T06:20Z)
======================================================================
window        2026-10-08T05:26Z -> 2026-10-10T05:26Z   CLOSED_INCOMPLETE
productive    ~3 h of 48 (stall 08:19Z 10-08 -> found 18:37Z 10-10)
incident      I-1 stdin spawn pool crash loop x4,683,366, PID-only waiter,
              no independent wake  -> supervise.py + 11 failure tests
              I-2 (10-11) executor deadlock CAUGHT by watchdog, auto-resumed
rounds        W1 done; W2-W12 NOT_REACHED; recovery slice 10-11
worlds        300 discovery (5 families: rnn graph stig sediment* phase)
laws          proposed 4 | killed 2 (G-0007, G-0008) | provisional 1 (L-0001,
              weak, by rule) | confirmation: NONE, vault empty, F-0002 unfrozen
EXP-04        INCONCLUSIVE by rule (rnn/sediment hold; graph, phase fail;
              stig not reached); stig rise-with-k -> EXP-05 prereg fdd6097f0
reviews       R-STAT final reconciled (open A10 A13 B5 B6); R-MECH final MISSING
tests         full suite 165/166 -> G-0008 record fixed e030d9276; runtest NOT RUN
holdouts      D2 SEALED / UNREAD / UNSPENT; no other holdout used
compute       ~7.5 CPU-h useful, ~170 CPU-h wasted; $0
branches      main records | cosmos/c4-v03 e030d9276 (unmerged) | autopsy local
packet        REVIEW_PACKET_48H_2026-10-08.txt
next          4 h reliability test (RELIABILITY_4H_2026-10-11/PREREG.md)
======================================================================
```
