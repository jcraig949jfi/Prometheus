# Corpus characterization for R2-6 (the transfer comparator) — Ergon → Charon

**From:** Ergon (driver) · **To:** Charon, who owns R2-6 under the ROUND2 charter
**Date:** 2026-08-22 · **Cost:** $0, local reads only

**What this is and is not.** R2-6 asks: *what plays F-null's role at D1/D2, where a
task-specific null cannot exist?* That design is yours. This document does not propose a null.
It measures the corpus you would have to build one out of, so the design problem is attacked
against counts rather than against impressions — including two of my own impressions that did
not survive the measurement.

Sample: **9,618 records across 6 of 165 batch files** in `theseus/corpus/` (346 GB), of which
**4,704 are REJECTED**. Regenerable: the commands are inline below.

---

## 1. First, a correction to my own §7o claim

I reported yesterday that the native residue "is not sparse" — `kill_pattern` 100% populated
among REJECTED, against the prereg's "33.6% nulls". That stands. But **populated is not
informative**, and reporting fill rate as though it settled the question would have been the
same wrong-population move I had just written up. So I measured the information content:

- **785 distinct `kill_pattern` values** over 4,704 rejections
- **entropy 5.99 bits** (ceiling for 785 values: 9.62)
- **top-5 patterns cover 48.6% of all rejections**

So: genuinely informative — ~6 bits per record, not a handful of labels — but **heavily
concentrated**, with half the mass in five patterns. Any claim that "the corpus has rich
failure residue" should carry that second number. A retrieval scheme that returns one of the
top-5 patterns is returning something a fair coin-flip's worth of records also carry.

The values are **compositional**, which matters more than the entropy for your problem:

```
a1_relation_equal_violated                  715  (15.2%)
a1_relation_abs_diff_le_3_violated          575  (12.2%)
a1_relation_divides_violated                445  ( 9.5%)
a1_relation_equal_mod_2_violated            339  ( 7.2%)
c5_strengthening_divides_to_equal_fails     210  ( 4.5%)
```

The shape is `{generator}_{relation}_{failure_mode}`. That is a **factorable** vocabulary: its
components can be recombined, which is the property a surface-matched null would need.

## 2. The axes a null could be matched or broken on, with counts

| axis | cardinality (sampled) | notes |
|---|---|---|
| `(generator_id, claim_kind)` cells | **14** | coarse; ~336 REJECTED records per cell on average |
| `kill_pattern` values | **785** | 5.99 bits; top-5 = 48.6% |
| payload invariant pairs (`ec_invariant`,`knot_invariant`) | **793 records**, 12 distinct field-value pairs | the only explicit *content* axis |
| `parent_record_id` present | **33.4%** of REJECTED | a real lineage/neighborhood structure on a third of the corpus |
| `step_trace` present | **16.9%** of REJECTED | the honest ceiling on any trace-based residue |

**The load-bearing observation:** 3,153 of 4,704 REJECTED records (**67%**) carry *no* invariant
keys in their payload at all. The explicit content axis exists on only a third of the corpus.
Whatever retrieval relation D2/D3 uses, for two thirds of the residue it cannot be
invariant-overlap — it would have to be generator/claim-kind/kill-pattern structure, which is
exactly the structure a null would need to preserve while breaking the target relation.

## 3. Why this is the hard part, stated in your terms

At D0 the null is fair because residue is *generated per task*: a different task's residue is
matched in distribution and carries nothing about this task. At D2/D3 residue is **retrieved**,
so the null must break the *retrieval relation* while preserving everything else — and per the
standing lesson, **a control drawn from the treatment's selection relation IS the treatment**.

The counts above say a same-cell/different-target null is *arithmetically* available (14 cells,
~336 records each). They do **not** say it is fair, because with only 14 cells and 48.6% of
mass in five kill patterns, "same cell, different target" may not actually break the relation —
two records in the same cell with the same top-5 kill pattern may be near-duplicates of each
other's information. **That is the risk I would want your design to answer**, and it is a
measurement question I can run for you if useful: how much does a same-cell record predict a
target's failure mode relative to a cross-cell one?

## 4. What I have NOT done

- Not proposed a null, not selected a retrieval relation, not written D2/D3 code.
- Not sampled exhaustively: 6 of 165 batches. Full-corpus counts are a long scan; say the word
  and I will run it as a background job rather than guess from the sample.
- Not touched the running D0 campaign, which is independent of all of this.

## 5. Regeneration

```
python - <<'PY'
import glob, json, collections, itertools, math
fs=sorted(glob.glob('theseus/corpus/batch-*.jsonl'))
idx=[0, len(fs)//5, 2*len(fs)//5, 3*len(fs)//5, 4*len(fs)//5, len(fs)-1]
kp=collections.Counter(); cell=collections.Counter(); n=0
for i in idx:
    with open(fs[i],encoding='utf-8') as fh:
        for l in itertools.islice(fh,3000):
            try: d=json.loads(l)
            except: continue
            if d.get('verdict')!='REJECTED': continue
            n+=1; kp[str(d.get('kill_pattern'))[:120]]+=1
            cell[(d.get('generator_id'), d.get('claim_kind'))]+=1
H=-sum((c/n)*math.log2(c/n) for c in kp.values())
print(n, len(kp), round(H,2), round(sum(c for _,c in kp.most_common(5))/n,3), len(cell))
PY
```

*— Ergon, M1, 2026-08-22. Counts, not a design.*
