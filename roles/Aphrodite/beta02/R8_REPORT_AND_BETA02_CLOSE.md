# BETA-02 E3 (R8) REPORT + BETA-02 CLOSE

C-007 (C-P2B-APH-BETA-02). The R8 assay was frozen in beta02/BETA02_PREREG.md s6 (122b0c8cb) before any E1/E2 outcome.
It was executed because REPLICATION_GATE = PASS (beta02/E12_REPORT.md). Evidence tier 2: local CPU engine. No
recursion beyond one generation.

| Item | Value |
|---|---|
| Receipts | beta02/runs/R8/{R8_RESULT.json, R8_LIBRARIES.json (sha 55bf5b85...), R8_PAIRS.json, R8_DONORS.jsonl, R8_INDEX.json, R8_WALKS.jsonl}; beta02/runs/SUPPLY/PLAN_R8.json |

## 1. Dispositions
- **Technical: CLEAN.** 05:16-09:14Z, 4 workers, exit 0.
  - Foundry: 3,456 families (LIN 48-71).
  - Donors: 120.
  - Walks: 6,848.
- **Supply:**
  - The libraries of the 22 E1 seeds were frozen and hashed (entries only). Hashes were re-verified at run time.
  - Pairs: **20 usable.** Next-generation seeds 56 and 60 (partners of 32 and 36) failed the pre-registered
    extras-fill rule. LIN 48 and 51 are partners of the excluded E seeds 24 and 27.
- **Donor-state isolation:**
  - Next-generation donors received only (machinery, unseen supply roles, library entry list), in fresh worker
    processes.
  - No donor history, caches, task identities, scoring traces or selection state crossed.
  - The transplant path was known-answer checked (K3).

## 2. Frozen readouts (improvement = held-out families the NEXT generation reaches where its OWN inherited library is censored)

| Machinery | improvement(L_g11) total | improvement(L_I0) total | improvement(L_P) total | L_g11 vs L_I0: better / worse / tied | p (one-sided) | Result |
|---|---|---|---|---|---|---|
| **I_0 @ O4 (primary)** | **10** | **39** | 56 | **0 / 5 / 15** | **1.0** | **R8_PASS = NO** |
| g11 @ O10 (secondary) | 37 | 87 | 134 | 1 / 10 / 9 | 0.9995 | NO |

Each library vs L_P:

| Machinery | L_g11 vs L_P | L_I0 vs L_P |
|---|---|---|
| I_0 | 0 / 7 / 13 (p two-sided 0.016) | 0 / 2 / 18 |
| g11 | 0 / 18 / 2 (p two-sided 8e-6) | 0 / 9 / 11 (p 0.004) |

**Inheritance REDUCES next-generation improvement, and the better the inherited library, the larger the reduction.**

## 3. Separate (NOT the R8 endpoint): what inheritance carries
**Capability of the inherited library itself on UNSEEN lineages** (families reached that PRISTINE cannot reach, 20 x
32):

| Library | Families reached |
|---|---|
| **L_g11** | **104** |
| L_I0 | 32 |
| L_P | 0 |

**End state after one more generation** (descriptive; families vs PRISTINE):

| Machinery | L_g11 | L_I0 | L_P |
|---|---|---|---|
| I_0 | **114** | 71 | 56 |
| g11 | 141 | 119 | 134 |

**Next-generation selections** (20 pairs):
- I_0 machinery with L_g11: INHERITED 14, MEMORISE 4, a new schema 2.
- g11 machinery with L_g11: a new schema 15, INHERITED 5.
- A new schema seldom adds held-out reach beyond the inherited base abstraction.

## 4. Frozen interpretation (prereg s6)
**"NOT PASS, with L_g11 capability > L_I0: inheritance transfers capability but not improvement (first-order
inheritance only)."**

Specifically:
1. **The g11-produced library is a strong, portable first-order asset.**
   - It carries capability across lineages: 104 vs 32 families on never-seen supply.
   - Under the original improver, inheriting it gives the best end state (114 vs 71 / 56).
2. **It does not make the next generation improve better.**
   - The next generation has little left to acquire on top of the inherited base abstraction (the T51 finding:
     composition beyond the base class pays little).
   - When the next generation runs g11 itself, a pristine start re-derives most of the same capability (134 vs 141).
   - **The inherited abstraction SUBSTITUTES for the next generation's own improvement. It does not enable more.**
3. **The ladder stops at R8 in this world.** The heritable product of the improved improver changes WHAT the next
   generation has, not HOW WELL it improves.

Per the directive (s16), the R8 failure is reported as data. It is not rescued by redefining the endpoint. The
end-state figures above are descriptive and are not label-bearing.

## 5. Beta-02 close: the operator's statement form
"Under natural lineage supply, the original improver confuses memorisation with transferable abstraction:
- it selects memorisation in half of fresh seeds;
- excluding memorisation from candidacy is the cause of a large, replicated improvement: 162 vs 63 held-out families
  on 22 unexposed seeds, 16/0/6, p = 1.5e-5;
- the effect holds at both observation widths;
- the subset criterion alone is inert;
- the library this improved improver produces transfers capability across lineages (104 vs 32 families);
- **but it does not make a fresh next-generation improver improve better. It substitutes for that improvement rather
  than enabling it.**

**Recursive chaining stops at R8.** In this grammar and supply there is no second level of reusable structure for an
inherited abstraction to unlock."

| Item | Status |
|---|---|
| IMPROVER_CHANGE_REPLICATED_LOCAL | YES (N = 22, p = 1.5e-5) |
| MECHANISM | MEMORISE exclusion (Holm-significant); width additive (not Holm-significant); interaction null |
| R8 | **NO** (first-order inheritance only) |
| EVIDENCE_TIER | 2 |
| RSI | no claim |

## 6. What this implies (proposals only; nothing started)
- **The R8 failure is consistent with the Beta-01 picture:** composition beyond the base class pays little.
  - This is the first point where a REPRESENTATION/SUPPLY-depth question is directly motivated: does any world or
    grammar contain a second level of reusable structure that an inherited abstraction could unlock?
  - A W5P design would now have a concrete target (an R8 retest).
  - **It stays separately authorised.**
- **E4 (endpoint-aligned criterion)** remains a design. It is still worth running as a generalisation of the exclusion
  rule.
- **The LLM skill-library bridge** now has a sharper, two-part prediction:
  1. acceptance by aggregate validation savings admits memorised solutions; excluding them raises held-out reuse;
  2. inheriting a good library raises capability but does not by itself make later learning better.
  - It stays parked pending the operator.

## 7. Compute
- Beta-02 total: about 38 core-h on M4/HARRY1 (E supply 9.8, E1/E2 7.1, R8 supply 10.7, R8 run/score 7.5, checks
  about 0.5).
- The rolling 24 h peaked at about 44 core-h at 09:14Z, under 48.
