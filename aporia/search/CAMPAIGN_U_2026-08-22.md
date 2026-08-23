# CAMPAIGN U — one pass, TERMINAL: **U3 SURVIVES**. The population correction does not destroy the result.

One-pass campaign, precedented by Campaigns B and T. Branches were committed in-script before any
computation ran.

## The defect being corrected

Campaign S defined "zero-connectivity" from `oeis_crossrefs.jsonl` alone, then discovered that
**23.9% of its own hit targets name an A-number in their title** — referenced sequences the edge
extraction had missed. The population was contaminated by construction, and every count downstream
of it inherited that.

**Corrected definition:** a sequence is neglected only if it has **no connectivity evidence in any
available source** — not a source or target of a cross-reference edge, its own title/formula/program
text names no other sequence, *and* no other sequence's text names it. All four datasets were used:
1,588,669 edges, 395,310 titles, 523,463 formula lines, 620,122 program lines.

## Pre-stated branches, and the prediction I attached to them

    U1 DESTROYED   R < 0.20          the S/T result rested on contamination — headline, not footnote
    U2 WEAKENED    0.20 <= R < 0.70  materially reduced but survives in part
    U3 SURVIVES    R >= 0.70         contamination did not drive the result

`R` = fraction of Campaign T's survivor targets still neglected under the corrected definition.
**Partition verified by enumeration:** 1,001 points over [0,1], zero unmapped, coverage U1 200 · U2
500 · U3 301, boundaries `0.199→U1`, `0.200→U2`, `0.699→U2`, `0.700→U3`. Census of all survivors, so
no sampling error; granularity 1/248 = 0.0040, far finer than either cut; the 0.20/0.70 thresholds
are **materiality judgements**, labelled as such. Null check: correction removing nothing → R = 1 →
U3; removing everything → R = 0 → U1.

**I declared in advance that I expected the correction to shrink the population *substantially*.
It did not.**

    Campaign S neglected population    31,189
    corrected neglected population     28,830      -> 7.6% removed

Direction right, magnitude wrong. The cross-reference extraction was better than Campaign S's 23.9%
figure suggested, because that figure was measured on **hit targets** — a biased subset, since
sequences that have findable relations mention other sequences more often than average. Whole-
population contamination is 7.6%; among survivor targets specifically it is 18.3% (47 of 257
removed), which is close to 23.9% exactly as that bias predicts.

## Result

    survivor targets (loose)   210/257 = 0.8171   -> U3
    survivor targets (strict)  203/248 = 0.8185   -> U3

Both readings fire the same branch. **The Campaign S/T result is not destroyed by the population
contamination.**

## A bookkeeping error of mine, surfaced by this campaign

Campaign T's headline said **248** surviving targets; its artifact contains **257**. Both are
defensible and they answer different questions — 248 counts targets with *no* stated record anywhere,
257 counts targets appearing in *at least one* unstated record — and **9 targets have both a stated
and an unstated relation.** But the headline and the artifact should have matched, and they did not.
The strict count is the right one for a claim about targets; the artifact was written per-record.
Corrected here rather than left to be found later.

## What stands after three campaigns on this line

**203 distinct OEIS sequences** carry a verified exact relation to a corpus sequence — holding over
20 to 45 terms — where:

- the relation is stated in **neither partner's title**,
- stated in **neither partner's formula field**,
- and the target is neglected under a **connectivity definition using every available source**,
  inbound and outbound.

Still unchecked and named: OEIS **comment and example** fields are not on disk. And the standing
scope holds — unwritten in OEIS does not mean unknown to mathematics. This is a **candidate set for
human triage**, and three successive attempts to demolish it cheaply have now failed.

## The product

`aporia/search/sb_candidates_corrected_population.jsonl` — 506 records over the corrected population,
each carrying both A-numbers with titles, operator, offset, exact term count, a plain-language claim,
provenance, and a status field naming which OEIS fields were checked and under which population
definition.

## Campaign U TERMINAL: U3 SURVIVES
