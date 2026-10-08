# EXP-01 -- LOCAL SYSID on fresh DISCOVERY worlds (EXPLORATORY; preregistered 2026-10-08 before any EXP-01 data)

Campaign 48H_2026-10-08, window W1. Code: prometheus/cosmos/c4/exp01.py, sysid_local.py, baselines.py, cert_b.py
at the commit that adds this file. No confirmation data is created or touched. No D2.
Nothing here is a confirmatory claim; the output decides what is FROZEN for a later CONFIRMATION batch.

## Worlds
DISCOVERY split, batch 0 (firewall.split_seed namespace DISCOVERY). Families: rnn, graph, stig (C3 public
substrate code; FRESH worlds: continuous natural ranges spanning the C3 lattices + fresh weight seeds) and
theseus_sediment (foreign, NATIVE.json natural distribution). 30 worlds per family, k uniform on {2, 4, 8},
V = 4. The C3 visible worlds (MAPS.json) are not used.

## Labels and baselines
Certificate A class (c3/certify.py, unchanged); Certificate B-linear (c4/cert_b.py); T3-DOWN (c4/baselines.py,
from the F-0001 text). Target: FUNCTIONAL vs not, determinate rows only (INDETERMINATE / INCOHERENT counted).

## Hypothesis H-LOCAL and the frozen law C4-L-0001 (zero fitted shape parameters, one threshold)
Usability at delay k follows from composing one-step physics:
    S = gamma * lam^(2(k+1))                                         (cue injected at t = 0, k+1 further steps)
    N = eta * sum_{i=0..k} lam^(2i) + gamma * sum_{i=1..k} lam^(2i)  (noise every step; distractor injection)
    s = log(S / N);  predict FUNCTIONAL iff s > theta
theta is the only fitted value: fitted by maximizing BA on the TRAINING families of each LOFO fold.

Comparators (all LOFO): T0/T1a majority; T2a logistic on k; T3-DOWN; C4-L-0002 = logistic on
(log lam, log eta, log gamma, vis, k) (5 slopes + intercept; an open-vocabulary-within-LOCAL control).

## What is reported (no gate is applied; this is discovery)
Per family and pooled-within-family (stats.within_family_uplift, equal family weights): BA of L-0001,
L-0002, T2a, T3-DOWN, under A labels and under B labels; A/B agreement per family; exclusion counts.

## What would kill H-LOCAL at discovery (decided now)
- KILL if L-0001's mean within-family BA uplift over T2a (k alone) is < 0.05 under A labels, OR if L-0001
  is below T2a in >= 2 of the 4 families.
- If L-0001 survives but L-0002 beats it by >= 0.10 mean within-family BA, H-LOCAL's specific composition
  is FAILED and only "local coordinates carry information" is kept (INCONCLUSIVE for the law).
- If sediment (the foreign family) alone fails while the C3 families pass, the result is recorded as
  FAMILY-BOUND (C3-authored worlds only), not as support.
Any surviving candidate is frozen (firewall.Vault.freeze) BEFORE a CONFIRMATION batch is generated.

## ADDENDUM 1 (2026-10-08, written while EXP-01 was running and BEFORE any EXP-01 label or coordinate was
## examined; only row counts and timings had been seen) -- candidate C4-L-0003

Motivation (from the literature and a planted case, not from EXP-01 data): L-0001 summarizes contraction by the
spectral radius alone. For non-normal dynamics that is wrong: a shift register has spectral radius 0 and perfect
memory for its length (Ganguli, Huh & Sompolinsky 2008, "Memory traces in dynamical systems", PNAS; White, Lee &
Sompolinsky 2004). Transport-like families (sediment drift, stigmergic fields) are non-normal.

C4-L-0003 (one fitted value, theta): from the LOCAL one-step description (sysid_local.local_lgss: J, B, Q, C; all
from at most one controlled step, G7), compose the linear-Gaussian discriminability of the cue at the readout
after the query:
    d2 = mean over cue pairs of  dl' Sr^-1 dl,  dl = C J^(k+1) (B_c - B_c'),
    Sr = C [ sum_{i=0..k+1} J^i Q J^i' + sum_{i=1..k} J^i S_B J^i' ] C',  S_B = cov of distractor injections
    predict FUNCTIONAL iff log d2 > theta   (theta: LOFO, max BA on training families)
The local description is recomputed for each EXP-01 world from its stored spec (no new labels, no new seeds for
the certificates). L-0003 is scored with the SAME kill rule as L-0001 (vs T2a) and is compared with L-0001.
If BOTH survive, the one with the higher mean within-family BA is the single candidate frozen for confirmation;
the other is recorded, not discarded.
