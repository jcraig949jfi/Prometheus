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
