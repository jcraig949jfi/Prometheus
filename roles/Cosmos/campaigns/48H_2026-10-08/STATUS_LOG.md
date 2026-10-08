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
