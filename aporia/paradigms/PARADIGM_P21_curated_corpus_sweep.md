# PARADIGM P21 — Curated-Corpus Empirical Sweep (worked example + decision tree + code skeleton)

Aporia P90, 2026-08-21. Source: taxonomy confirmation line (P21 accepted
Tier-1). **NUMBERING FORK RECORDED**: `frontier_review_synthesis.md` assigns
P21 to Higher-Order Fourier under a competing P19-P24 scheme never reconciled
with the taxonomy; the taxonomy is operationally canonical (the backlog
generates from it) — a live phantom-canonical-references instance, routed to
James/Elenchus via the worklog. Consumer: Learner corpus type C.

**The move**: curate a corpus whose ground truth is KNOWN (calibration
anchors, report_10 primitive (d)); sweep it with an instrument battery; read
the battery's quality off the anchors — with ABSTENTION first-class (verb:
SWEEP-THE-ANCHORS; payoff verb: CALIBRATE-INSTRUMENTS-ON-KNOWN-TRUTH).

## 1. Worked example — EXECUTED, and the calibration arc IS the lesson
(`paradigm_p21_worked_example.py`)

A 10-anchor OEIS corpus (local mirror) with curated growth classes — three
polynomial, three exponential (incl. Catalan's exp-with-polynomial-factor),
two super-exponential, two expected-ABSTAIN (primes ~ n log n; partitions
e^(c√n)) — plus noise and stub decline legs. Final: **SWEEP-CALIBRATES,
12/12**, with the b-stability column separating exponentials (0.97-1.0) from
everything else (≤0.70) at a glance.

**The four-run calibration arc (all preserved in the worklog)** — the anchors
caught, in order: (1) MY mis-curation (primes labeled POLY; n·log n is not a
power law — the corpus corrected its curator); (2) index re-basing (a trailing
window that re-bases n turns power laws into shifted ones); (3) nested-model
confusion (the 3-param exponential fit CONTAINS the power law — POLY must be
read from its own fit with the nested linear term negligible, never from an
r² comparison against a nesting model); (4) √n-growth mimicry (partitions
fit small-b exponential locally — killed by requiring the linear coefficient
STABLE across window halves, a derived certificate). Every fix
mechanism-diagnosed, none threshold-shopped.

## 2. Decision tree

- Q1: Do you have (or can you curate) objects with KNOWN ground truth for
  the property the instrument measures? — NO: sweeping uncurated corpora
  yields unfalsifiable clusters; curate first or route to exploration.
- Q1 YES — Q2: Does the corpus span the instrument's claimed range AND
  include expected-ABSTAIN cases plus decline legs (noise, stubs)? — NO: a
  corpus of only positives calibrates confidence, not competence.
- Q2 YES — Q3: Is the battery's every verdict-rule derived (fits with stated
  models, certificates with stated mechanisms)? — NO: black-box batteries
  cannot be calibrated, only scored; derive or replace.
- Q3 YES — EXECUTE: sweep; on any miss, DIAGNOSE THE MECHANISM before
  touching a threshold (the four-run arc's rule); iterate transparently —
  calibration on the anchor corpus is the design, not p-hacking, BECAUSE
  the corpus is the labeled calibration set and every revision is mechanism-
  justified and preserved.
- Exit: only after the sweep calibrates does the battery earn deployment on
  unlabeled data — and its abstention rate there is a first-class output.

## 3. Code skeleton

```python
def corpus_sweep(anchors, battery, decline_legs):
    """P21 template. Misses demand mechanism diagnosis, not threshold nudges;
    the revision history is part of the result."""
    record = []
    for obj, truth in anchors + [(d, "ABSTAIN") for d in decline_legs]:
        verdict, diagnostics = battery(obj)
        record.append({"obj": obj, "truth": truth, "verdict": verdict,
                       "diag": diagnostics, "ok": verdict == truth})
    misses = [r for r in record if not r["ok"]]
    return {"calibrated": not misses, "misses": misses, "record": record}
```

## 4. Catalog assignment

Primary: the channel's OWN instruments — every battery the loop builds
(growth classifiers, spec smoke gates, the falsification battery itself)
owes a curated-anchor sweep before deployment; feedback_calibration_anchors_
in_depth is this paradigm as standing doctrine. Catalog: 0151-class corpus
work (sequence sweeps), the Sleeping-Beauties screening (68,770 sequences —
this battery is a candidate first-pass instrument). Anti-assignment:
single-object attacks (0057-0067-class) — nothing to sweep.

## Provenance and honesty

The growth classes are elementary; the content is the calibration arc — four
mechanism-diagnosed revisions caught by ten labeled anchors, including the
corpus correcting its own curator — and the b-stability certificate that
emerged from it. The numbering fork is recorded rather than silently
resolved: two documents claim different P21s and only James's ruling or an
Elenchus disposition can retire one.
