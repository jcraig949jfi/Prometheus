# T10 -- OBSERVE BREADTH AS THE CANDIDACY DISCRIMINATOR: REPORT + EXTERNAL-REVIEW PACKET

C-006 (C-P2B-APH-BETA-01), cycle 10, TEST window 10. Rung R2 (candidacy). Evidence tier 2.

| Item | Value |
|---|---|
| Spec | beta01/windows/T10_OBS_SPEC.md (t10_observe.py 9ced6b98..., frozen at daae87699 before data) |
| Receipts | beta01/runs/T10_OBS/{T10_RESULT.json, T10_DONORS.jsonl, T10_ROLES.json, T10_INDEX.json, T10_WALKS.jsonl, T10_CONTINUITY.json} |

## 1. Dispositions
- **Technical: CLEAN.**
  - Attempt 1; 30 donors; 384 new walks.
  - Ran 13:16-13:33Z with 4 workers, threads = 1, exit 0. About 1.1 core-h.
- **Scientific: MEASURED.** The gate passed:
  - continuity 2/2 exact;
  - NULL10 selected the planted OFF schema in 0/15 seeds;
  - NULL total 99 <= 99 + 2.

## 2. Frozen readouts

| Readout | Result |
|---|---|
| **CANDIDACY_POSITIVE** | **NO.** Total 98 (O4) -> 99 (O10). Better 4, worse 3, tied 8; sign p = 0.5 |
| **STARVATION_RESCUE** | **YES.** 2 of 3 zero-derivation seeds rescued: seed 0 (0 -> 11), seed 7 (0 -> 3). Seed 12 stays at 0 |

Frozen interpretation (spec s5, row 2): **breadth fixes the starved seeds but costs elsewhere.**

## 3. Per seed (gain of 32; n_observed / n_derived; selection)

| Seed | O4 | O10 | O4 obs/der | O10 obs/der | Selection O4 -> O10 |
|---|---|---|---|---|---|
| 0 | 0 | **11** | 1/0 | 11/5 | none -> (acc + {H}) |
| 7 | 0 | **3** | 3/0 | 6/2 | none -> ({H} + v) |
| 9 | 0 | **5** | 6/1 | 11/3 | none -> (acc + {H}): **wrong-class case fixed** |
| 4 | 5 | **7** | 4/2 | 12/6 | (acc - {H}) -> ({H} + v) |
| 1 | 10 | **5** | 8/2 | 16/5 | (acc - {H}) -> (acc + {H}) |
| 6 | 8 | **0** | 6/2 | 13/3 | (acc + {H}) -> **none** |
| 13 | 7 | **0** | 4/2 | 13/6 | (v - {H}) -> **none** |
| 12 | 0 | 0 | 1/0 | 8/3 | none -> none: **candidates now exist but none is selected** |
| 14 | 0 | 0 | 6/1 | 16/5 | none -> none (validation-content seed; as expected) |
| 2, 3, 5, 8, 10, 15 | = | = | -- | -- | unchanged |

NULL10 at O10 equals g10 at O10 in every seed. The planted OFF schema is never chosen.

## 4. Reading
1. **Observation starvation is real and is fixed by observing more.**
   - Every starved seed gains observations: seed 0 goes 1 -> 11, seed 12 goes 1 -> 8.
   - Every starved seed now derives candidates.
   - Two of three convert this into transfer. So does the wrong-class seed 9.
2. **Candidacy is NOT monotone in observation.**
   - In seeds 6 and 13, a useful candidate that O4 derived and selected disappears at O10. The improver then selects
     nothing.
   - In seed 1 the O10 candidate set yields a worse winner.
   - Extra observations do not just ADD candidates. They change the certified classes, and therefore the LGG schemas
     derived from them, so the earlier useful schema is no longer produced.
   - This is a property of the **derivation step** (certification + LGG over all observations jointly), not of supply
     or selection.
3. **Net:** observation supply and derivation stability trade off. Gains in the starved seeds (+21) are cancelled by
   losses in seeds where the derivation re-partitions (-20).

**First broken rung now: R2 derivation stability.** The improver's candidate generator is non-monotone: more evidence
can delete a good candidate.

This is a mechanism hypothesis drawn from the selection and count columns. The derived-candidate lists are not stored
in the T10 donor rows, so DEV-11 should verify it directly (cheaply: re-derive seeds 1, 6 and 13 at O4 and O10 and
diff the candidate sets).

## 5. Candidate T11 (for DEV-11; not frozen)
A content-free, monotone derivation rule: keep the candidates derived from the original observations and add those
derived from the enlarged set. Candidates = union over the nested observation sets O4 and O10. The selection rule
(g10) is unchanged.
- **If the non-monotonicity diagnosis holds,** this should keep the starvation rescues AND the seed-6/13 candidates.
- **It changes only the generator.** That makes it an improver-rule change (an R7 lever) aimed at the R2 defect, not
  representation (not W5P).

## 6. Attack questions
1. Is seed 6/13's loss caused by the O4 schema missing from the O10 candidate set (non-monotone derivation), or by the
   schema being present but losing to a new candidate under g10 net-gain? The DEV-11 re-derivation answers this.
2. Seed 12 now has 3 candidates and selects none, while ORACLE10 (T09) accepts G1 there with gain 2. Are the 3
   candidates wrong-class?
3. 8 tied seeds: is O10 inert there because their 4 original OBSERVE families already certify the same classes?

## 7. ERRATUM (DEV-11, 2026-10-05; the disposition and frozen readouts are unchanged)
**The s4 "non-monotone derivation" hypothesis is REFUTED.** The DEV-11 re-derivation
(D11_DERIVATION_DIAG.json; seeds 1, 6, 12 and 13 at O4 and O10, with selections reproduced 8/8) found:
- **Derivation is monotone.** Candidates lost from O4 to O10: **none** in all 4 seeds. The O4-selected schema is
  still derived at O10.
- **Seeds 6, 12 and 13:** under g10's net-gain score, **MEMORISE wins at O10.**
  - Its validation G rises with the number of observations: seed 6 27k -> 49k; seed 13 27k -> 66k; seed 12 0 -> 126k
    (L about 0-2k).
  - It transfers nothing.
- **Seed 1:** (acc + {H}) (G 55.7k, L 0) beats (acc - {H}) (G 54.0k, L 9.2k) on validation net gain, yet transfers 5
  vs 10. This is a validation-to-transfer mismatch between two real abstractions.

**Corrected first broken rung: R3.** The selection score admits a NON-GENERALISING library (memorisation), whose
validation savings grow with observation and do not transfer. Observation breadth feeds MEMORISE as much as it feeds
abstraction.
