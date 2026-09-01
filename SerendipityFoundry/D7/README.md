# D-7 — Blind Nonlinear Wormhole Synthesis

**Verdict:** `CERTIFIED_NONLINEAR_WORMHOLE` · `MOTIF_TRANSFER_ONLY` · `WORMHOLE_WITH_REVISION`
**Status:** frozen, independently audited (7/7 auditors SOUND, no defects)
**Constitution hash:** `9d5e490c209dbc91…`  ·  **Prepared:** 2026-08-28

Does relational executable history — with no human-authored composition template —
cause the synthesis of a **nonlinear, topology-changing** transform that opens a
**certified** barrier in a frozen finite machine? This experiment answers **yes**,
under matched controls that rule out the cheaper explanations.

## One-paragraph result

A 3-register machine mod 13 (2197 states) has a region its base physics provably
never reaches (T=(0,1,7) is barred; exact closure + conserved invariant, upgraded
by auditors to a 169-element operator monoid holding for any path length). Writing
the locked coordinate `s` is gated behind another coordinate `u` and is nonlinear
(`s += r·r`); the gate-opener is a *different* artifact, so **no single artifact
crosses**. Given only machine-native relational history of 32 artifacts (marginal
+ pairwise interaction) on unrelated developmental worlds, a history-conditioned
synthesizer (**H2**) finds a crossing in a median **23.5** evaluations vs **73** for
the strongest history-free baseline (3.1×, p≈0), **65.5** for the same hoard with
edges removed (H0), and **86** for shuffled edges (H1). The discovered transform is
non-affine, non-separable, context-dependent; it folds all six held-out pairs and
opens the 13-state island to the entire 2197-state space. It survives macro-replay,
edge-reweighting, NULL-preservation, hostile-revision, and transfer controls, plus
a synthetic validation battery and a leakage audit — and 7 independent auditors who
re-implemented every claim from scratch found it all SOUND.

## Directory layout

```
D7/
  README.md                     <- this file
  code/                         <- the full self-contained instrument (17 .py files)
    run.py                        entry point: freezes constitution, runs everything
    substrate.py                  micro-ISA + generic synthesis grammar
    worlds.py / altworlds.py      proof / transfer / null / hostile worlds + kits
    certify.py                    exact cut certifier (closure + invariant)
    hoard.py                      the messy 32-artifact hoard
    history.py                    relational history + H0/H1/H2 conditions + prior
    census.py                     grammar census (no hidden templates)
    search.py                     shared Z0/Z1 synthesis engine (only prior differs)
    evalz.py                      exact verifier (Gz closure)
    controls.py                   macro/reweight controls + nonlinear degeneracy gate
    verdict.py                    admission gates A-K + verdict ladder + geometry
    validate.py                   synthetic validation battery (11 cases)
    leakage.py                    anti-cheat / endpoint-leakage audit
    meter.py / stats.py / synthlang.py   metering, statistics, grammar ops
  reports/
    d7_report.json              <- full machine report (every metric)
    d7_report.html              <- visual report (published as a claude.ai artifact)
    REVIEW_PACKET.txt           <- paste-able ASCII external review packet
    run_log.txt                 <- stdout of the binding run
  audit/
    redteam_findings.json       <- 7 independent auditor findings (structured)
    redteam_synthesis.txt       <- readable findings + lead-auditor synthesis
```

## Reproduce

```
cd F:\Prometheus\SerendipityFoundry\D7\code
python run.py
```

Deterministic (all RNG seeded; no wall-clock dependence); ~13 min single-thread on
Python 3.12 + numpy. Rewrites `d7_report.json`. The order follows the protocol:
physics → certified cut → grammar → census → history/controls → synthetic
validation → **freeze** → developmental history → then the learner.

## Headline numbers

| Arm | Median first-solve (evals) | vs H2 |
|---|---|---|
| **H2 — intact relational history** | **23.5** | 1× |
| H0 — same hoard, edges removed | 65.5 | 2.8× slower |
| H1 — edges shuffled | 86 | 3.7× slower |
| best history-free baseline (Z0-sample) | 73 | 3.1× slower |

Census crossing density 0.36%, min size 3, no KILL flags · admission A–K all pass ·
nonlinear gate pass · geometry 13 → 2197 states · transfer Z-MECH 7.5 vs Z0 116 ·
NULL preserved (0/6 both arms) · hostile revision 6/6 · leakage clean.

## Provenance & caveats

Built fresh under Agent D-7 (no predecessor artifacts imported). All machine
verdicts were frozen before evidence and before any human interpretation. Honest
bounds (full list in `reports/REVIEW_PACKET.txt` §12): findability numbers are
budget-relative, not impossibility; byte-level transfer fails by design (mechanism
transfers); effect magnitudes are seed-sensitive; the mechanism depends on the
gated writer being marginally invisible, a designed property of this world. Post-
audit hardening (stronger separability test, real vacuity check, docstring fixes)
was applied transparently and the verdict re-verified unchanged.
