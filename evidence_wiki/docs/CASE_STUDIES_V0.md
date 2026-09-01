# V0 Case Studies (charter §19, §20, §21)

All queries below were run against the live service on 2026-09-01;
raw numbers in `benchmarks/results_v0.json` and this file's command history
in the session journal.

## 1. Ergon Gen-1B cross-relation (§19)

Anchor: A-003 — "same phenotype ≠ same mutational affordances" (the behaviour
fingerprint collapses objects whose future transition neighborhoods differ).

What each retrieval mode found, asked for related findings across agents:

- **Document-to-document similarity (embeddings):** top-8 neighbors are all
  same-program vocabulary (A-008, A-005, A-012, B-002, A-014, …). The true
  cross-program partners (C-004, B-015, B-024) do NOT appear. Doc-doc
  similarity is captured by project vocabulary gravity.
- **Concept queries (embeddings over abstract phrasing):** "information loss
  under projection" ranks **B-015 first** (incubation trap world separating
  behaviourally equivalent operators) with B-022/B-025/B-005 following —
  the bridge appears when the QUERY carries the abstraction, not when the
  documents must supply it.
- **Curated mechanism page (metadata):** `/wiki/mechanisms/projection_equivalence`
  joins A-003, A-004, B-015, B-024, C-001, C-004, C-026 across **five agents**
  (Ergon, Incubation, Daedalus, Harmonia, Aporia). In the held-out benchmark
  this method scored MRR 0.605, hits@10 = 100%.
- **CP tensor factors:** MRR 0.023 on the held-out pairs — worse than raw
  text. At 99 observations over an ~85K-cell mode space the decomposition
  has nothing to compress.

Conclusion for §19: the cross-program relationship IS recoverable, and what
recovers it is the **typed substrate itself** (canonical mechanism terms with
preserved source vocabulary), not the factorization.

North-star loop closure: the A-003 × B-015 × C-004 link generated a concrete
falsifiable proposal, stored as `H-9b0a7922015e` (HYPOTHESIZED, never
evidence): *keying D-5 admission/retention on a mutation-neighborhood sketch
instead of the behaviour fingerprint should change Gen-2 retention outcomes;
B-015's trap-world discrimination predicts sketch-keyed admission recovers
affordances the fingerprint collapses.* This is an experiment proposal for
Ergon Gen-2, nothing more.

## 2. Failure metabolization (§20)

Anchor chain (all edges OBSERVED, packet-backed):

```
B-023  D6-A preregistered NULL (relational-history signal not established)
   └─ MOTIVATED → B-024  D-7 CERTIFIED_NONLINEAR_WORMHOLE
                          (history-conditioned synthesizer finds the
                           gate-opener/gated-writer pair marginals miss)
```

`dependencies(B-024)` reconstructs this chain through the API. The system
distinguishes *recording* a failure from *reusing* it structurally:

- **Reused negative evidence** carries an outbound `MOTIVATED` /
  `REUSES_NEGATIVE_EVIDENCE` edge (B-023→B-024; B-018 poverty kills → gv2
  freeze; B-017 prior exclusions reused by the v3 successor; B-012 trap
  boundary recovered from failures).
- **Merely recorded failures** are negative evidence rows with no outbound
  reuse edge — surfaced on `/wiki/orphans`.
- **The program-level backdrop** is C-027: the measured inheritance horizon
  is ~one campaign (only 1/37 late passes reached work before P100) — the
  Evidence Wiki's reason to exist, now queryable inside it.

## 3. Knowledge-gap discovery (§21)

The held-out missing-cell test (10 cells, `benchmarks/results_v0.json`
T5) put the **marginal-frequency baseline (0.787)** above CP (0.735),
Tucker (0.633) and TT (0.364 — below random). Gap surfacing in V0 therefore
uses the honest winner: marginal-weighted untested combinations from
`contract()`, stored as MISSING_CELL hypotheses (method=`marginal`):

- confound_conditioning × program_ecology — nobody has run a
  stratification/conditioning audit inside the Ergon ecology results.
- negative_evidence_reuse × program_ecology — failure reuse is proven in
  grammar worlds and residue corpora, untested in the flagship ecology.
- projection_equivalence × lmfdb_arithmetic — the fingerprint-collapse
  mechanism has never been probed on arithmetic-object representations.
- accessibility_geometry × llm_probe_band; transfer_mediation × program_ecology.

All carry status HYPOTHESIZED and cannot be promoted without a real
experiment (enforced by the store, tested in G8).
