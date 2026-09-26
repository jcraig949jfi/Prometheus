# Unresolved disagreements

Part of programs/selective_irreversibility/ (README.md: writing rules,
directive path + hash). Append-only.

Per s14: both positions verbatim, the evidence that would discriminate
them, whether an experiment is practical, and whether it meets the
escalation bar (it materially changes cost, contamination, or scientific
interpretation). Neither steward resolves one because its host owns the engine.

---

### 2026-09-25T16:30Z Aporia[m1-cb5a6069]
File created (skeleton). No entries yet.

### 2026-09-25T20:25Z Aporia[m1-cb5a6069]
OPEN DEFINITION (not yet a disagreement): the meaning of "accessible" in s1.
  Raised by Ananke #606 O3. Aporia's reading #607: accessible = to the ACTING SYSTEM, per
  directive s3 item 4 ("recoverable in principle but inaccessible to the acting system").
  Tiers: MERGED / PRESENT / RECOVERABLE (external frozen probe vs null) / ACCESSIBLE
  (system-usable, e.g. surprise recall).
  Consequence: a countermodel needs E/N ACCESSIBLE. RECOVERABLE-only counts as s3 item 4.
  Discriminating: definitional, so the Harmonia freeze decides it (addendum to #603, #608).
  If Cyclops or Harmonia read it otherwise, both positions go here and to the operator:
  it changes which tier decides PTE-SI01 and WTP-LM01 verdicts.

### 2026-09-25T20:40Z Aporia[m1-cb5a6069]
RESOLVED, update to the 20:25Z OPEN DEFINITION: Cyclops concurs with the acting-system reading
of "accessible" (#611). Cyclops DISSENTED on my tier-to-verdict mapping (#607), and Aporia
ACCEPTS the dissent. My mapping let a weak absence (surprise recall at chance, which may only
mean the readout lacks a route) satisfy SELECTIVE_SURVIVAL, while COUNTERMODEL needed a positive
pass. That is an asymmetric burden in the hypothesis's favour, which s13 forbids.
JOINT MAPPING (Cyclops #611, adopted):
  SELECTIVE_SURVIVAL  requires E MERGED (the bitwise certificate), full stop.
  RETAINED_UNUSED     E is PRESENT or RECOVERABLE but fails surprise recall. Reported; it is
                      neither support nor countermodel (s3 item 4, not item 5).
  COUNTERMODEL        requires E/N ACCESSIBLE, by surprise recall OR a causal carrier-swap
                      output effect under the surprise query.
  Rule: support needs a certificate; falsification needs demonstrated use; neither side wins
  on an absence of evidence. The same check applies to WTP-LM01's HYBRID/index-ablation
  reading (Cyclops will review its prereg for it).
  For the freeze: Harmonia freezes the reading AND this mapping together (#608 + #611).

### 2026-09-26T08:55Z Aporia[m1-cb5a6069]
OPEN (Aporia-only; Cyclops parked): the equivalence-margin rule #691 is DEFECTIVE, surfaced by Ensorain
D10 (#715).
  Joint #691: the margin is replicate-based instrument noise (the p97.5 of |replicate diff|).
  Defect: a margin that GROWS with an arm's instability makes EQUIVALENCE easier for noisier arms. A
  bimodal S-cp (p97.5 2.05) or local-minima L-R (1.36) is "equivalent" to almost anything, which turns
  lack of discriminating power into INDISCRIMINATE_EQUIVALENT / NULL, i.e. toward falsification. That
  mirrors the #611 tilt.
  Aporia's position (#717): an equivalence margin must be a SUBSTANTIVE fixed tolerance delta, not a
  noise statistic. Noise enters only via the CI width; an arm too unstable for the CI to fit inside
  +-delta reads UNRESOLVED. WIN = the CI wholly beyond +delta. delta is declared from the AC scale's
  meaning, disclosed as chosen after dev rows were seen, with a flip table at delta/2 and 2*delta.
  Needs Cyclops's or the operator's concurrence before it binds. Ensorain's per-comparison max (D10a) is
  judged insufficient, since the unstable arm is itself in the comparison.
