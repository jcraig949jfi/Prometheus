# T12 -- FRESH-SEED REPLICATION OF THE CUMULATIVE IMPROVER: REPORT + EXTERNAL-REVIEW PACKET

C-006 (C-P2B-APH-BETA-01), cycle 12, the final TEST window. Rung R7 (an improver-rule change), unexposed replication.
Evidence tier 2 (local engine).

| Item | Value |
|---|---|
| Spec | beta01/windows/T12_REPL_SPEC.md (t12_replicate.py ceed378d..., frozen at 417f20d46 before data) |
| Receipts | beta01/runs/T12_REPL/{T12_RESULT.json, T12_DONORS.jsonl, T12_ROLES.json, T12_INDEX.json, T12_WALKS.jsonl, T12_KNOWN.json}; beta01/runs/T12_T51/{T51_PLAN.json, T51_FOUNDRY.jsonl, T51_ROLES.json} |

## 1. Dispositions
- **Technical: CLEAN.**
  - Attempt 1, 14:15-15:31Z, 4 workers, threads = 1, exit 0.
  - Foundry 1,152 families; roles fillable 8/8 (quota 6); extras 8/8; 32 donors; 1,600 walks.
  - About 5 core-h.
- **Supply: OK.** 8/8 fresh seeds (W8 LIN 16-23, never used before).
- **Scientific: MEASURED.** The gate passed:
  - K1 and K2 passed;
  - NULL11 selected the planted OFF schema in 0/8 seeds;
  - NULL11 total 60 <= 60 + 2.

## 2. Frozen readouts

| Readout | Comparison | Totals | Better / worse / tied | Sign-flip p (attainable min) | Result |
|---|---|---|---|---|---|
| **IMPROVER_REPLICATED_POSITIVE** (primary) | g11 O10 vs g0 O4 (I_0) | **60 vs 20** | **5 / 0 / 3** | **0.031** (0.031) | **YES** |
| ABSTRACTION_ONLY_REPLICATED_POSITIVE | g11 O10 vs g10 O10 | 60 vs 20 | 5 / 0 / 3 | 0.031 (0.031) | **YES** |
| POOLED_descriptive (EXPOSED+FRESH, not label-bearing) | 23 seeds | sum of diffs +70 | -- | 0.002 | -- |

Frozen reading (spec s6, row 1): **first replicated R7 (tier 2).** A content-free improver-rule package, built by
causal localisation on exposed supply, makes a pristine improver acquire more reusable improvement on UNEXPOSED
natural supply. **It is first-order: NOT R8, NOT RSI, no real-model claim.**

## 3. Per seed (gain of 32 PRISTINE-censored transfer families)

| Seed | g0 O4 | g10 O10 | g11 O10 | g11 selection | MEMORISE chosen by |
|---|---|---|---|---|---|
| 16 | 0 | 0 | 0 | none (INHERITED) | g10 |
| 17 | 0 | 0 | **12** | (acc - {H}) | g0, g10 |
| 18 | 8 | 8 | 8 | (acc - {H}) | -- |
| 19 | 0 | 0 | **4** | (acc + {H}) | g0, g10 |
| 20 | 0 | 0 | **4** | ({H} + v) | g0, g10 |
| 21 | 0 | 0 | **15** | ({H} + v) | g10 |
| 22 | 12 | 12 | 12 | (acc + {H}) | -- |
| 23 | 0 | 0 | **5** | (acc + {H}) | g0, g10 |

## 4. What exactly replicated (the honest scope)
1. **The effect is carried by ONE of the three changes: abstraction-only candidacy (g11).**
   - g10 O10 equals g0 O4 in all 8 fresh seeds (20 = 20).
   - On fresh supply, the subset criterion plus observation breadth WITHOUT the MEMORISE exclusion adds nothing.
   - Observation breadth may be a precondition for g11's gains (O10 widens what g11 can choose among), but T12 does
     not isolate g11 at O4 on fresh seeds. On exposed seeds, g11 O4 gave only 101 vs 98.
2. **The mechanism replicates exactly.**
   - **Memorisation is selected by I_0 itself in 4/8 fresh seeds, and by g10 O10 in 6/8.**
   - In every seed where g11 gains, the baseline arms had chosen MEMORISE (or nothing).
   - The gains land on PRISTINE-censored held-out families: 40 additional transfer families, a 3x increase.
3. **Statistical margin:**
   - p = 0.031 is the attainable minimum for 5 non-tied seeds. Every changed seed moved up.
   - A reversal of moderate size would have failed the readout. One extra seed at -4 gives a sign-flip p of
     0.0625. Only a trivial reversal (-1) would have kept p at 0.031 (both computed with the frozen flip_p).
   - The power statement made before the data (s5: positive "less likely than not") did not anticipate how often I_0
     chooses memorisation on fresh seeds.
   - The pooled 23-seed figure (p = 0.002) is descriptive only (it includes exposed seeds).
4. **What this changes historically.** I_0, the improver used through ARC3 and Beta-01, selects a non-generalising
   memorised library on a large share of natural seeds (4/8 fresh; 3/15 exposed at O4). On natural supply, part of
   I_0's "failure to derive" was a failure to PREFER the derived abstraction over memorisation. No historical label is
   changed.

## 5. Next (for the Beta-01 close; no further TEST windows remain)
- **An independent replication** by a different seat, or on new W8 seeds (24+; needs W8 regeneration). It should be
  at higher power and should include **g11 at O4 on fresh seeds**, to separate the role of observation breadth.
- **The endpoint-aligned selection score** (T11 attack question 3): a principled replacement for the type rule.
- **R8 question** (operator order s16): does the improved improver change subsequent improvement dynamics? For
  example, does a g11-selected library seed a second generation better than I_0's? Cheapest discriminator: a
  two-generation chain on LIN 16-23 with g11 vs g0 libraries as the start. Design only here.

## 6. Attack questions
1. **Is "exclude MEMORISE" a hidden prior that favours abstraction by construction?**
   - The rule removes a candidate TYPE that every donor generates. It encodes no family, schema or answer content.
   - NULL11 still rejects the planted junk 8/8.
   - Gains are measured on held-out, PRISTINE-censored families. A rule that only pruned a competitor without
     enabling real abstraction could not create transfer there.
2. **Is MEMORISE's validation win a validation-design artefact** (validation families sharing exact programs with
   observed lineage siblings)? If so, the deeper fix is the validation design, not the rule. Both readings give the
   same improver-level conclusion: I_0's acceptance test cannot distinguish memorisation from abstraction on natural
   supply.
3. **Seed 16 is zero in every arm.** That is the starvation / validation-content boundary, the T09 seed-12 analogue.
