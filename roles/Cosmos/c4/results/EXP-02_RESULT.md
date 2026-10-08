# EXP-02 RESULT -- challenge-proposal DISCOVERY batch 1 (EXPLORATORY; 2026-10-08)

Data EXP-02_discovery_b1_Q.jsonl (120 worlds; sha256 3894111dee75b33c...). Prereg prereg/EXP-02_CHALLENGE_DISCOVERY.md.

## Preregistered verdicts (frozen theta -4.3144 from EXP-01; no refit)
- C4-L-0003: SURVIVED_PROVISIONAL. (i) uplift over T3-DOWN on REGISTERED rows U = .487 (graph .50, rnn .50,
  sediment .46; stig dropped: 30/30 FUNCTIONAL); (ii) informative families graph, rnn, sediment; none below T2a.
- FOREIGN FAMILY (theseus_sediment): informative this time; frozen-theta BA .962 => PASSED (>= .60).
  Thin: only 3 NONE sediment worlds (+1 INCOHERENT excluded).
- T-C1 frame test (on EXP-01 stig): 1/30 class flips => NOT frame-dependent at class level (scores shift).

| family | frozen L-0003 | LOFO L-0003 | L-0001 | T3-DOWN | T2a | n (FUNCTIONAL) |
|---|---|---|---|---|---|---|
| graph | .972 | .944 | .819 | .528 | .50 | 22 (4) |
| rnn | 1.00 | 1.00 | 1.00 | .50 | .50 | 24 (20) |
| sediment | .962 | .962 | .981 | .50 | .756 | 29 (26) |
| stig | -- | -- | -- | -- | -- | 30 (30) |
Exclusions (A9): rnn 6 INDETERMINATE, graph 8 INDETERMINATE, sediment 1 INCOHERENT.

## Exploratory analyses AFTER the verdicts (several looks at discovery data: NO evidential weight)
1. A/B disagreement on sediment 5/29: all are A-FUNCTIONAL with tiny effects (P2 .014-.028; B acc .24-.26 vs chance
   .25). A's paired test detects near-chance usability that B's unpaired test cannot: a POWER difference, not a
   mechanism. The binary FUNCTIONAL label conflates barely-usable with usable.
2. Graded usability (B excess accuracy) vs log d2 (EXP-01+02): Spearman rnn .99, sediment .86, graph .65, stig .14
   (n.s.). One sigmoid for all families is 3x worse than per-family curves => L-0003 is ORDINAL within families,
   NOT a calibrated quantitative law across them.
3. S2 on binary A labels: FAILS (all three tests reject with stig; without stig offset p .0016, slope p .44).
   Per-family A boundaries in log d2: graph -3.80, rnn -4.20 (the two Cosmos-authored families) vs sediment -6.84
   (the foreign family). Read naively: an author-lineage offset.
4. Under B labels the boundaries COLLAPSE: graph -3.64, rnn -3.56, sediment -4.02; offset p .94. The A offset was
   a certificate-sensitivity artifact (point 1). What stays family-specific is SHARPNESS: sediment slope .93 vs
   2.4-3.1 (slope LRT p .0099; Holm-rejected).

## Candidate for confirmation (NOT run: confirmatory execution is gated on review reconciliation)
C4-L-0004 (new id; L-0003's score, a new claim): "B-usability (linear actor) is FUNCTIONAL iff log d2 > -3.8 in
LOCAL-FMC units, with a COMMON boundary across families; transition sharpness may differ by family."
It was shaped by multiple looks at discovery data and must be frozen in the vault, then scored once on fresh
CONFIRMATION worlds. Until then: hypothesis only.

## B5 family-identification test (R-STAT final, B5) on the same discovery data (EXPLORATORY)
1-NN leave-one-out family ID (chance .25): LOCAL coordinate vector (lam, eta, gamma, vis) .908 -- vis alone .863
(readout = full state in rnn and sediment, so vis = 1 there by construction); lam .53, eta .57, gamma .65.
The COMPOSED L-0003 score log d2: .425 (with k: .396).
=> the raw LOCAL coordinates are a family fingerprint and may enter a law only through within-family statistics
(B5 rule); the composed scalar carries far less family identity, but not none. A frozen family-ID bound for the law
input is required before F-0002.
