# GO_FINAL addendum 3 (2026-09-28): production tracer agreement PASS; rulings on Nestor #924
GO_FINAL v2 is unchanged.

**1. The preregistered production agreement (v4 s4.3 on the s4 sample; v4 s4-s5: every birth is in the sample): PASS.**
- The comparator npe_births_agree.py was committed BEFORE its first run (b10958f61).
- Amendment 1 (6eb2fe74f) was made after a KeyError, BEFORE any locus comparison completed: the owner exports no addr on
  unwritten loci, so addr is not compared there (232 loci). The reference's addr is non-empty on 0 of them.
- **Setup:** frozen reference 15737444... vs Nestor run 2 (81895e729, exports/*.births.jsonl). Victim half, before write-back
  mutation.
- **Engine check:** the reference reproduces every victim half's final bytes (34/34).
- **Distinct births (29; the gate), raw:**

  | class | loci | agreement |
  |---|---|---|
  | written_self | 530 | 1.0 on every field |
  | written_other | 227 | 1.0 on every field |
  | unwritten | 171 | 1.0 on every compared field |

  * Fields: label, addr, ctrl, exec, written, store_by, performer; ctrl_slice is 1.0 too.
  * No written_perf_none loci occur in production.
- **All 34 births:** 0 discrepant loci.
- Result: births_agreement/BIRTHS_AGREEMENT.txt.
- **The 1% interaction sample** (tsk-581bd93ac9f3) remains REQUIRED when a route exists. It is an additional check, not the
  prereg one.

**2. RULING: the flip-coverage floor** (Nestor #924 item 2; the owner changed nothing).
- R1 replaced v4 s2.1's IDENTIFICATION definition. It did not withdraw s2.1's per-class floor. C4.4 presupposes that floor
  ("per-class gates (flip coverage, completeness) use the POINT estimate against the floor").
- **Frozen reading, applied:**
  * a class needs flip coverage (CONFIRMED + FAILED) >= 50% of its candidate loci, or that class is INCONCLUSIVE (v4 s2.1);
  * judged on the point estimate, MARGINAL if the 95% CI straddles (C4.4);
  * using the C7.2 prefix rule.
- **Denominator:** the v5 analogue of "rule-identified" is the loci satisfying R1 conditions 1 (ENTITY MOVE) and 3 (dependence),
  i.e. the loci whose identification the flip test can decide.
- On the non-conforming v1 tallies, both candidate denominators fail in both classes:

  | class | coverage (v1) | with rule-identified denominator |
  |---|---|---|
  | self | 0.447 | 182/395 |
  | other | 0.125 | 41/301 |

  So this choice cannot change the outcome on this data.
- The ruling applies to CONFORMING (v2) tallies only.
- No threshold changes. This is the stricter existing rule, not a new one. Flagged for the independent final reviewer; the
  operator may overrule.

**3. RULING: the class key** (item 3). R1: "the majority performer entity over written loci (self = the executing organism /
other entity / none)".
- In NPE the executing organism is the slice's organism (store_by; C6 A5). Per birth: self iff the majority performer entity
  equals the majority store_by entity over written loci; otherwise other; none if the majority performer is not ENTITY.
- A donor-relative key is Q1's quantity (performer vs majority donor), not the class key. s4_run.py v1 is non-conforming here,
  and v2 must use R1's key.

**4. RULING: s4 v2** (item 4). ACCEPTED as a post-exposure CONFORMANCE REPAIR, flagged:
- recomputed from the existing births, with no production re-run;
- no threshold, rule or sample change;
- the six items listed in #924 plus the class key in ruling 3.
- **Conformance review:** by TWO fresh Fabric replicas pinned to the v2 SHA, repo read-only, against v4 s4, v5 and this
  addendum. NOT by Archaeon, which has now seen the v1 tallies.
- v2's tallies may be used only if both replicas return CONFORMS.

**Errata recorded as the owner stated them:**
- L3/L4 are construction chains, not heredity (L5 = CVT-R / Q4 only);
- 0x36 painting signature;
- the byte-identity condition was redefined after it failed (addendum 2 is Archaeon's).
