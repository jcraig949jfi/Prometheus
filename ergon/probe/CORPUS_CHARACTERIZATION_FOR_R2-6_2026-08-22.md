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

## 3b. MEASURED — I ran the risk from §3, and both obvious nulls fail, for opposite reasons

I said §3's risk was "a measurement question I can run if useful". It was cheap, so I ran it.
200,000 sampled record pairs, seed 0:

- **P(same `kill_pattern` | SAME cell) = 0.4365**
- **P(same `kill_pattern` | DIFF cell) = 0.0000**
- P(same `kill_pattern` | uniformly random pair) = 0.0601
- P(same `kill_pattern` | same `parent_record_id`) = 0.1260 *(327 parents with ≥2 children)*
- H(kill_pattern) = 5.99 bits; **H(kill_pattern | cell) = 3.47** → the cell alone reveals
  **2.52 bits (42%)** of the target's failure mode.

**Both candidate nulls fail, and they fail in opposite directions:**

- A **same-cell null** carries the target's *exact* failure mode **43.7% of the time**. That is
  not a null; it is a treatment arm that delivers the answer on nearly half the draws.
- A **cross-cell null** carries it **0.0%** of the time — a `kill_pattern` never once crosses a
  cell boundary in 4,704 records — but is then trivially **arm-identifying**, which is the exact
  defect class that killed two exit reviews of this probe already.

**The provenance-strip projection does not rescue it.** The D0 fix for an analogous leak was a
deterministic census over a fixed vocabulary (`METHOD_VOCAB`). I tried the corpus analogue —
strip the `{generator}_` prefix and compare `{relation}_{failure_mode}` — verified working
(`e3_property_alternating_sign_violated` → `property_alternating_sign_violated`). Result:
**785 distinct patterns before, 785 after; zero projected patterns appear in more than one
cell.** The generator prefix is not the leak. The *vocabulary itself* is generator-specific,
because different generators test different things.

**At the token level it is almost — but not entirely — a partition**, and the exception is the
useful part:

- 287 distinct tokens; 63 (22.0%) appear in more than one cell
- **mean pairwise Jaccard across all 91 cell pairs: 0.0343**
- **79% of cell pairs (72/91) share literally no vocabulary at all**
- but a few pairs are genuinely connected: `b4/operator_rotation` vs `b3/composition_test`
  **J = 0.889 (56 shared tokens)**; `c5/mutation` vs `a1/invariant_equality` J = 0.545;
  `g5/symmetry_transform` vs `a1/invariant_equality` J = 0.385

**So the design space is narrow but not empty.** A null that is vocabulary-matched (so it is not
arm-identifying) yet pattern-disjoint (so it does not leak the failure mode) can only live in
that handful of high-Jaccard cell pairs. Identifying that those pairs exist is characterization
and is mine; **choosing them as the comparator is design and is yours.**

### 3c. FALSIFIED BY THE FULL SCAN — read this before §3b's conclusion

I said §3b's claim was too big for a 6-batch sample and launched the full 165-file scan. **It
falsified the claim, and the sample was the problem.** Partial results at **54/165 files,
42.5 million REJECTED records** (my sample saw 4,704 — about 0.01% of the corpus):

- distinct raw `kill_pattern` values: **93,175** (sample: 785)
- distinct cells: **31** (sample: 14)
- projected patterns crossing a cell: **4** — and those 4 cover
  **10.21% of all rejected records (4,334,674 of 42.5M)**

The crossing pairs `a1/invariant_equality` with `f1/invariant_equality`, on exactly the
vocabulary that dominates the corpus:

```
relation_equal_violated          1,485,458 recs   a1 + f1
relation_abs_diff_le_3_violated  1,144,184 recs   a1 + f1
relation_divides_violated          976,929 recs   a1 + f1
relation_equal_mod_2_violated      728,103 recs   a1 + f1
```

**So cross-generator failure-mode recurrence DOES exist, on a tenth of the corpus mass.** §3b's
"0.0000 cross-cell" and its inference that there is "little cross-generator transfer for D2/D3
to measure" are **withdrawn.**

**Why the sample lied.** I took the *first 3,000 lines of each of 6 files* — a contiguous
window, not a stratified draw. Batch files are written in generator-run order, so a
head-of-file window sees a handful of generators. My sample never contained `f1` at all: it
missed the very generator that produces the overlap. This is precisely the sampling-window
antipattern already recorded in program memory, committed by the person who recorded it.

**Also note:** the full scan's *raw*-pattern crossing count of 0 is near-tautological and should
not be quoted — `kill_pattern` embeds the generator id as a prefix (`a1_…`), so a raw pattern
cannot cross a cell by construction. Only the **projected** figure above is meaningful. I built
the scan tracking the raw form and had to derive the projected form post-hoc from saved state;
the number to cite is 4 patterns / 10.21% of records, not 0.

**What this does to §3b's dilemma — it opens the door §3b said was shut.** A null that is
vocabulary-matched *and* failure-mode-matched yet drawn from a **different generator lineage**
is exactly what the a1↔f1 overlap provides, across 4.3M records. That is the shape R2-6 needs:
matched on what the residue *says*, broken on where it *came from*. Whether it is fair remains
yours to rule — a1 and f1 may be near-duplicate generators, in which case the lineage break is
cosmetic, and that is the next thing worth measuring.

Scan still running (54/165); final numbers land in
`ergon/probe/ledgers/corpus_scan/full_scan.json`.

### The finding that outruns the null question  **[SUPERSEDED BY §3c — WITHDRAWN]**

If failure modes never recur across generators — 0.0000 cross-cell, and 79% of cell pairs
sharing no vocabulary — then there is **little cross-generator transfer in this corpus for
D2/D3 to measure**. Residue appears usable mainly *within* a generator, and within a generator
it is 43.7% likely to simply be the answer. That is
[[feedback-residue-must-be-navigable-not-logged]] answered with numbers, and it is a statement
about the year of accumulated corpus rather than about any null.

I am flagging it, not concluding it. Two honest limits: this is **6 of 165 batch files** (14
cells; the full corpus may hold more), and exact-string matching is a harsh test that a
*semantic* shared taxonomy might beat — though no such taxonomy exists, and building one is a
design act that would itself need leak-testing. **Say the word and I will run the full 165-batch
scan as a background job** rather than let a 6-batch sample carry a claim this size.

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
