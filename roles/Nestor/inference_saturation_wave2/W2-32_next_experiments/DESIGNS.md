# W2-32: next experiments (DESIGN ONLY, three pre-registration drafts)

**Written:** 2026-10-01T02:43Z (`date -u`).
**By:** W2-32 design worker for Nestor.
**Status:** these are drafts. Nothing is frozen, dispatched or run. Each needs operator or Aporia authorization, a canonical Fabric lease and a freeze commit.
**Compute used:** about 0.5 CPU-min.
- `calc_bands.py`, pure arithmetic, about 14 CPU-s per run, run twice.
- Static checks of the planted genomes (`z8.dis`, hashes).
- JSON reads.
- No world code was executed. No git writes.

**Files in this folder:**
- `PREREG_DRAFT_IMPLANTED_MORPHS.md` (rank 1);
- `PREREG_DRAFT_HARV_INWORLD.md` (rank 2);
- `PREREG_DRAFT_FOUNDER_INDEPENDENCE.md` (rank 3);
- `calc_bands.py` and `calc_bands.json`: the band, eligibility and power derivations for all three.

## Answer first
The best experiment not yet authorized is **X-IMPLANT-MORPH**.
- **Design.** Implant the founder, 44→AC, 43→C3 and C3+AC as single founders under BASE in the X-TICKET cell, and store final genomes.
- **Why its result is decisive.** Its decisive arms are **C3 and C3+AC**, not the W2-17 morph. Both mappings from static law to lifetime law are calibrated on the founder and both are live. They predict:
  - P(B ≥ 163) **≤ 0.12–0.16** under per-call proportionality ("near-critical plus luck");
  - **≥ 0.86** under keep-leveraged lifetime ("a supercritical variant causes persistence").

  At 64 seeds per arm the count bands are disjoint (0–13/17 vs ≥ 41), with power of about 1.00 in both directions. Whatever the result, one theory dies:
  - if both arms fall between the bands, the static law fails under either mapping, and **F\* kill criterion 2 fires**.
- **Cost.** About 8–10 core-h in total, or about 5 core-h for the F + C3 + C3AC core.
- **Other two drafts.**
  - X-HARV-INWORLD is cheaper (about 1.1 core-h for its decisive stage A), but its primary outcome is nearly fixed by W2-23 (static 0/750).
  - X-INDEP-BATCH costs the most (about 12.7 core-h) and decides a theory, T4(a), that is already unsupported.

## Ranking by decisiveness per CPU-hour

| rank | draft | decisive core | core-h (plan / cap) | P(clean decisive call) | what the call kills |
|---|---|---|---|---|---|
| 1 | X-IMPLANT-MORPH | D1: C3 and C3AC counts vs disjoint M2/M3 bands | 10 / 15 (core about 5) | about 1.0 for D1; 0.63 for AC (D2) if N18 is true | H-NEAR-M2 or H-SUPER-M3; F\* criterion 2 if in the gap; W2-17's AC-morph headline (D2/D3); the persistence anomaly (D4) |
| 2 | X-HARV-INWORLD | P1–P3 on epoch-1 loss, paired seeds | 6.5 / 10 (stage A about 1.1) | about 1.0, but the P1 prior is about 0.9 PASS | N2's in-world bridge (P2/null); terminator vs confinement in-world (P3) |
| 3 | X-INDEP-BATCH | β̂ CI in K1 = 800 vs K8 = 400 | 12.7 / 15.5 | 0.63–0.89 at β = 1; 0.97–1.0 at β = 1.3; mostly UNRESOLVED at β = 1.15 | T4(a) (INDEPENDENT), or F\*'s no-kin term (SUPERADDITIVE) |

**Expected information per core-h.**
- **X-IMPLANT-MORPH** is the highest. Its outcome is genuinely uncertain: M2 and M3 are both calibrated and both live. Every outcome kills something.
- **X-HARV-INWORLD** has the highest certainty and the lowest surprise. Its value is upgrading the top Wave-2 headline from "one harness, static" to "in-world", plus the remainder accounting in P2.
- **X-INDEP-BATCH** is likely to return INDEPENDENT or UNRESOLVED and move no headline.

## Shared conventions (all three drafts)
1. **Physics.** X-TICKET: 7ae3 C9 arm-B cell, `atlas_axis = NONE`, tier M, BASE, `max_epochs = 300`.
   - The instrumentation is the X-TICKET subclass plus logging.
   - Bit-exact equivalence to the X-TICKET records is a gate (PC1).
2. **Matched readouts.** Primary readouts are cumulative counts (B; family depth) or end states, computed by identical code in every arm.
   - No maxima of noisy re-scored values (W2-19).
   - No occupancy or maxA (W2-14).
   - No pooling with batches that use a different horizon or readout (W2-14/W2-22/W2-25 R6).
3. **Eligibility counts before freezing** (lesson 09-04). Each draft gives the expected number of conditioning events and an INELIGIBLE branch that is distinct from a null.
4. **Rulers need demonstrated reachability.** Each draft has:
   - a planted positive whose outcome is shown reachable in the exact harness (X-TICKET B ≥ 163 replays; certified-birth and loss fixtures under each physics);
   - a planted negative that cannot fire: the LDIR-knockout founder (N1 `ko_ldir`, 52–53 → 00), which has no authored copies.
5. **Final genomes** are stored for every run, including extinct-stopped runs.
6. **Multi-seed CVT-R** (lesson W2-23): any competence precondition uses ≥ 5 independent seeds.
7. **Seeds are fresh and disjoint.**

   | draft | seed base |
   |---|---|
   | X-IMPLANT-MORPH | `42_000_000 + s` |
   | X-INDEP-BATCH | `42_100_000 + s` |
   | X-HARV-INWORLD | `42_200_000 + s` |

   - The full used-range inventory is in PREREG_DRAFT_IMPLANTED_MORPHS §3.
   - Re-check against EXPERIMENT_GRAPH.jsonl and LEASES.jsonl at freeze.
8. **Timestamps** come only from `date -u`. Use no `hash()`-based seeding; W2-23 P3's seeding was not reproducible across processes.

## Findings made while designing (for the ledger)
1. **W2-25 §5 Experiment 1's frozen H-SUPER threshold cannot be passed by the model it tests.**
   - The threshold was "morph P(B≥163) ≥ 0.15 and ≥ 4x the founder".
   - N18's own best two-type fits (binned deviance ≤ 4), started from one implanted AC morph, give P(B≥163) = **0.030–0.117**. That is about 1.4–7x the founder's 0.016–0.021, and never ≥ 0.15.
   - The reason is overdispersion: at V = 7 an m = 1.1–1.2 lineage escapes only about 3–6% of the time.
   - Freezing W2-25's rule would have produced a false kill. It is replaced by model-derived bands.
2. **A single implanted AC morph has weak power to separate the two-type story from the near-critical story.** Even at 384 seeds, power is 0.63 if the truth is N18-native. The decisive contrast is the keep variants, where the mappings diverge by more than 5x.
3. **Keep-leveraged static law reproduces N18's fitted morph m from static data.**
   - m_life(AC) = m_life(F) × [conv/(1−keep)] ratio of 1.39, giving 1.11–1.24 with m_life(F) = 0.80–0.89.
   - Per-call proportionality gives 0.85–0.95.
   - So W2-25 F4's "+6% not +45%" is a statement about the per-call→lifetime **mapping**, which is untested. It is not yet a correction of W2-17's number. X-IMPLANT-MORPH D1 tests that mapping.
4. **The W2-22 "fresh seeds" overlap other experiments' seeds.**
   - 9_998_000 + 1000..2199 = 9_999_000..10_000_199, which overlaps X-DECAY 9_999_000–063, X-STERILE 9_999_500–563 and X-ATOMIC 9_999_800–863.
   - W2-22's verdict is internal (FIELD vs FREE), so it is not biased. The PREREG's "fresh" holds only relative to W2-14's seeds 0–39. Minor record defect.
5. **X-DOSE-CURVE's k-founder construction gives the extra founders anc 1..k−1** (they replace the first `_seed_genome()` draws). Its readout is *world* depth, which can be non-founder (W2-2).
   - So W2-12's β is a world-depth β at 2,000 epochs.
   - X-INDEP-BATCH uses family depth at 300 and must not be pooled with it.
6. **The static planted genomes check out against MANIFEST_FROZEN.**

   | genome | sha256[:12] | disassembly / bit distance |
   |---|---|---|
   | F | 42b930f55cc1 | |
   | AC | 65d0e50b8d2e | 44 = `XOR A,H`; 1 bit |
   | C3 | e589ac501689 | 43 = `JP 22EC`; 1 bit |
   | C3AC | 272f3b645ce3 | 43 = `JP 22AC`; 2 bits |
   | LDIR-KO | 576051df4e76 | |

   - The founder bytes are 37 = A5, 43 = C1 (NOP on this VM), 44 = EC, 45 = 22, 48 = 5F, 49 = 66, 52 = ED (LDIR). This is consistent with W2-24.

## Envelope (MWO-0004 R2)

| draft | core-h plan | core-h hard cap | ≤ 16 per item |
|---|---|---|---|
| X-IMPLANT-MORPH | 10 | 15 | yes |
| X-HARV-INWORLD | 6.5 | 10 | yes |
| X-INDEP-BATCH | 12.7 | 15.5 | yes (tight) |
| All three | about 29 | 40.5 | ≤ 48 per seat per 24 h only if trailing usage ≤ about 19 core-h at plan |

- **Before dispatch:** sum Nestor's trailing-24 h CPU, including Wave-2 workers (several core-h so far).
- **Recommended order:** X-IMPLANT-MORPH (or its 5 core-h core), then HARV stage A (1.1), then the rest.
- Each item needs a canonical Fabric lease.
- All three are new preregistrations, so R2's "no changed preregistration" clause means each needs explicit authorization.
