# Nestor inference ledger, Wave 2 (2026-09-30 → 2026-10-01 04:30 ET)

**Directive:** `roles/Nestor/prompts/2026-09-30_inference_saturation_wave2/` (sha256 4c1f7353…8468).
**Starting point:** Wave 1 rev 2, `roles/Nestor/inference_harvest_2026-09-30/` (2ca81ab32).
**Purpose:** a record that stops us rediscovering the same thought twice. One entry per investigation; entries are appended
in completion order.

**Entry format:**
- question;
- evidence inspected;
- inference/result;
- confidence;
- strongest objection;
- unresolved issue;
- next questions generated.

## Active queue (opened 00:30 UTC)

| id | investigation | directive item | owner |
|---|---|---|---|
| W2-1 | contradiction mine: evidence that would make each synthesis conclusion look wrong | A | Opus worker |
| W2-2 | near-miss science: precursor signatures and early-warning observables | B | Opus worker |
| W2-3 | heredity without our vocabulary: several independent re-descriptions, then divergent predictions | C | Opus worker |
| W2-4 | causal minimality: copied vs necessary vs establishment-only vs environment vs physics | D | Opus worker |
| W2-5 | historical error autopsy, with reusable instruments implemented | E | Opus worker |
| W2-6 | theory tournament: 21 pairs, existing evidence first | F | Opus worker, then attacked by Nestor |
| W2-7 | alien reproductive physics: VM modifications plus static competence-rate probes | G | Opus worker |
| W2-8 | executable-semantics audit of the NPE world, runners and rulers | code reading | Opus worker |
| W2-9 | statistical-method review of every CONFIRMED NPE verdict | review | Opus worker |
| W1-S3 | pairwise-knockout epistasis (T4(c)), carried over from Wave 1 | D/F | Opus worker (running) |

## Entries

### W1-S3: pairwise-knockout epistasis (T4(c)). Closed 00:55Z
- **Question.** Do state-free genomes carry multi-site organization that single knockouts miss?
- **Evidence.** 48 state-free + 48 state-dependent genomes (FOR panel), 100 dispensable pairs each, 3 draws, re-assay. Preregistration written before computing. Positive control: a redundant-setter construct. Negative control: passenger pairs of a minimal copier. See `inference_harvest_2026-09-30/forensics/FORENSIC_PAIRWISE_EPISTASIS.md`.
- **Result.** **T4(c) DEAD under the frozen rules.**
  - Excess: 0.77x null (state-free) vs 0.71x (state-dependent).
  - State-free rate is 0.56x the state-dependent rate. The ratio is 1.01 in the zero-null stratum.
  - Strict synthetic lethality is 3.7% in both groups, spread thinly, with no recurring motif.
  - Both controls passed. One deviation: 100 pairs per genome instead of 200, under the budget clause.
- **Confidence.** Moderate-high for "state-freedom carries no extra multi-site organization at the pair level".
- **Strongest objection.** The null over-predicts, so excess < 1 is uninformative. Pairwise knockouts cannot see higher-order or population-level organization. The test is static: competence and state-freedom screens, not in-world establishment.
- **Unresolved.** Establishment-level epistasis: a knockout pair that leaves the screens intact but kills the two-step map.
- **Next questions.** Does any pair change S1b's two-step predictor while leaving the screens intact? That is cheap and static, and it overlaps W2-4.

### N1: foreign-cell "victim magnet" (Nestor, primary session). Closed 00:58Z
- **Question.** Revision 2 moved the 9cba/e160 magnet to "unexplained", following RT B1. Is that right?
- **Evidence.** `inference_saturation_wave2/N1_foreign_magnet/magnet_rate.py` and `.json`. Static p11.interact with the C-SWAP-ACQUIRE cells, stock VM, ATOMIC predecessor criterion, 1,500 interactions per condition, attribution by `prov`.
- **Result.**
  - In both foreign cells the founder is overwritten (predecessor-accepted) by partners at about 0.1-0.5% per interaction, mostly at side 0:
    - 9cba: zero context 2/750, random 4/750;
    - e160: random 6+2/750.
  - The changed bytes are authored almost entirely by the partner's context (9cba random: 249 partner vs 2 founder bytes).
  - **LDIR knockout gives 0/1,500 overwrites in every cell and context.** SELF knockout does not remove them; SELF is absent from these cells' ops mask.
  - So the mechanism is a partner executing the founder's **LDIR**, not SELF.
  - Integrating per epoch: with a per-epoch hazard of about 0.07-0.27%, P(founder label lost by epoch 2000) is about 0.74 to 0.99. The observed figure is 100/240 lost, plus 44 spread. That matches in order of magnitude.
- **RT B1 contained a denominator error.** It compared a per-interaction rate (≤ 1.5%) with a per-run frequency (42%), and revision 2 accepted the comparison without checking the denominator.
- **Correction, in both directions.** The magnet is *plausibly* explained by partners executing the founder's LDIR, integrated over the run. That is a hijack via LDIR, not SELF. It is not demonstrated in-world.
- **Also measured.** In 7ae3's own cell the side-0 hijack is 320/750 (43%) per side-0 interaction under zero context, and 242/750 under random context.
- **Confidence.** Moderate: the mechanism dependence on the LDIR bytes is clean, and the integration is order-of-magnitude only.
- **Strongest objection.** Survival in 45-51 runs where the founder persists alone is hard to square with the integrated hazard. Possible reasons:
  - real contexts are not uniform random;
  - the founder is not paired every epoch (pressure or allocation);
  - other context effects.
  The hazard model over-predicts loss.
- **Unresolved.** In-world confirmation needs one instrumented replay.
- **Next questions.**
  - Does LDIR-hijack exposure explain founder loss in X-TICKET (the 28%)?
  - Does it predict which C-ATOMIC C2 specimens lose their founder?
