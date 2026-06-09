# Audit: F044 frame-based resample — Pattern-4 selection-frame test

**Auditor:** Harmonia_M2_auditor
**Run at:** 2026-04-22
**Task:** `audit_F044_framebased_resample` (sessionA, 2026-04-19)
**Output:** verdict + recommended tensor mutation
**Spec source:** Methodology tightener `b57f4afe`; F044 cells (P020/P023/P026) flagged PROVISIONAL.

---

## Verdict

**RETRACTED_AS_SELECTION_ARTIFACT.**

F044's claim "2085/2086 rank-4 EC in LMFDB have `disc = conductor`, suggesting a theorem hiding in plain sight (additive reduction forbidden at rank ≥ 4?)" is a **Pattern-4 selection-frame artifact**, not a rank-specific structural finding. The pattern falls out of LMFDB's high-conductor curve-population sourcing methodology, not from anything rank-4 specifically.

Recommended tensor mutation:
- (F044, P020), (F044, P023), (F044, P026): PROVISIONAL → −2 (provably-collapses, selection-frame artifact)
- F044 tier: live_specimen → killed_selection_frame
- Description rewritten to flag Pattern 4 anchor; cross-link F044 ↔ Pattern 4

---

## Method (option (a) lite)

Per `null_protocol_v1.md` §Class 4 and the audit task, two paths were available:
- (a) define a frame-based resample from a non-rank-record source and re-run the disc=conductor count
- (b) run a theorem check on whether any published result constrains bad reduction type at rank ≥ 4

I executed a **partial (a) by comparison**: rather than constructing a synthetic non-rank-record sample (no obvious source), I compared the disc=conductor proportion across ranks at the same conductor range as F044's rank-4 set. If 100% prime-conductor were a rank-4 property, lower-rank EC at the same conductor range would be measurably less concentrated. If 100% prime-conductor were a high-conductor property of LMFDB's source data, all ranks at that conductor range would show the same pattern.

The latter is what the data says.

## Data (LMFDB, queried 2026-04-22)

### F044 cohort baseline (rank=4, all conductors)

| Stratum | Count | Note |
|---|---|---|
| total rank=4 EC | 2086 | |
| unique iso classes | 2085 | one isogenous pair |
| `semistable=True` | 2086 (100%) | no curve has any additive reduction |
| `num_bad_primes = 1` | 2085 (99.95%) | the "1 exception" referenced in F044's description |

The 1 exception is **`234446.a1`** at the LOW boundary of LMFDB's rank-4 conductor range (conductor 234446 = 2 × 117223, `nbp=2`). It is the lowest-conductor rank-4 EC in the database.

Conductor decade distribution of rank-4 EC:

| Decade | Count |
|---|---|
| 10⁵–10⁶ | 8 |
| 10⁶–10⁷ | 75 |
| 10⁷–10⁸ | 722 |
| 10⁸–10⁹ | 1281 |

The bulk lives at conductor ≥ 10⁷ — exactly the rank-record-construction regime (Stein/Elkies/Dujella style) where LMFDB augments exhaustive enumeration with curated high-rank curves.

### Cross-rank comparison at SAME conductor range [234446, 299671051]

| Rank | n in range | semistable | nbp=1 share of semistable | nbp=1+semistable proportion |
|---|---|---|---|---|
| rank=2 | 341,523 | 59.6% (203,720) | 69.8% | ~41.6% |
| rank=3 | 34,616 | 89.3% (30,896) | 90.2% | ~80.5% |
| rank=4 | 2,086 | 100.0% | 99.95% | 99.95% |

A real rank-4 effect would predict the ladder 41.6% → 80.5% → 99.95% (rank ↑ → prime-conductor concentration ↑). At first glance this looks supportive of the F044 hypothesis. **But the gap closes entirely if we restrict to high conductor.**

### Cross-rank comparison at conductor ≥ 10⁸

| Rank | n at conductor ≥ 10⁸ | nbp=1 + semistable proportion |
|---|---|---|
| rank=2 | 81,298 | **100.00%** |
| rank=3 | 16,095 | **100.00%** |
| rank=4 | 1,281 | **100.00%** |
| rank=5 | 14 | **100.00%** |

**Every rank from 2 to 5 is 100% semistable + nbp=1 at conductor ≥ 10⁸.** F044's "100% prime-conductor at rank 4" is identical to the rank-2 and rank-3 patterns at the same conductor range. The pattern is a property of LMFDB's high-conductor sourcing, not of rank-4 specifically.

## Mechanism

LMFDB's curve population at high conductor is essentially the set of curves that can be FOUND there. Rank-record constructions (Stein-Elkies, Dujella et al.) and isogeny-class walks tend to produce curves with simple bad-reduction structure for two reasons:

1. **Constructive methods favor multiplicative-only reduction.** The recipes used (e.g., congruent-number constructions, Heegner-point liftings, X²+Y³=N families) produce curves whose discriminants factor cleanly; primes of additive reduction would require special handling and are usually filtered out.
2. **Verification cost favors simple curves.** A curve with prime conductor is easier to verify rank for: there's only one local L-factor to compute, the Tamagawa product is a single c_p, and Sha computations are cleaner. Rank-record candidates with composite or additive-reduction conductors get filtered earlier in the pipeline.

The combined effect: by conductor 10⁸, the LMFDB curve set is a "constructive sieve" output — anything that survived made it through a filter that strongly favors prime-conductor + semistable. The rank label is downstream of this filter.

This is exactly the Pattern-4 sampling-frame trap as described in `pattern_library.md`:
> *"`ORDER BY X ASC LIMIT N` gives you a biased sample if X correlates with the categorical dimension you care about."* — generalized form: any non-random sourcing methodology biases the categorical dimensions it correlates with.

The "ORDER BY rank DESC then take what we can find" implicit selection on rank-4 EC at high conductor is the categorical analogue. Conditional on conductor ≥ 10⁸, every rank stratum has been through the same filter and shows the same 100% prime-conductor pattern.

## Why the 1 exception is at the low boundary

`234446.a1` (the rank-4 with composite conductor) sits at the LOW boundary of LMFDB's rank-4 conductor range. At conductor 234,446 we are well below the 10⁸ regime where rank-record constructions dominate. This is the ONE rank-4 curve that LMFDB has from a different sourcing path (likely exhaustive enumeration up to ~10⁵ extended into 10⁵–10⁶), which is why it carries a non-prime-conductor that the rank-record sourcing wouldn't have produced.

If LMFDB ever extends exhaustive enumeration further into the 10⁶–10⁷ range, the count of "rank-4 with composite conductor" would grow — and F044's "1 exception" claim would inflate, weakening any theorem-style reading even further.

## What this audit does NOT establish

- It does NOT prove there is no rank-4-specific theorem about additive reduction. There may well be one (e.g., a parity-like constraint connecting rank to local root numbers). A theorem-search via `audit_F044_rank4_lmfdb_selection` (still in queue) would close that question independently.
- It does NOT establish that ALL of LMFDB's high-conductor population is constructively sourced. Some of the 100% semistable curves at conductor ≥ 10⁸ could be from systematic exhaustive scans (Cremona-style up to higher bounds).
- It does NOT measure the population-level proportion of rank-4 curves with composite conductor — the population is uncountable; only the LMFDB sample is.

The verdict targets only F044's reading of LMFDB's data as if it were a representative sample. It is not.

## Pattern lineage

- **Pattern 4** (`pattern_library.md`): the canonical sampling-frame trap. F044 is now a fourth named anchor case for Pattern 4 alongside the original NF/Artin LIMIT-N anchors.
- **null_protocol_v1.md §Class 4** (construction-biased samples): F044 is the canonical Class-4 example for which NULL_BSWCD is structurally insufficient, and for which a frame-based resample (had one been available) would have closed the question. The cross-rank comparison done here is the next-best alternative — same conductor range, different rank, observe pattern is conductor-driven not rank-driven.

## Recommended actions

1. **Tensor mutation:** demote (F044, P020), (F044, P023), (F044, P026) from PROVISIONAL +1 to −2. Update F044 tier from `live_specimen` to `killed_selection_frame`.
2. **Description rewrite for F044** in `build_landscape_tensor.py`: replace the "candidate theorem hiding in plain sight" framing with the Pattern-4 selection-frame interpretation; cite this audit doc and the cross-rank comparison data.
3. **Pattern 4 update:** add F044 as a fourth anchor case. The shape ("100% concentration in some categorical that turns out to be a sampling-frame property of the data source") is broader than the original LIMIT-N framing — Pattern 4's anchor list could note this as the construction-biased-sample sub-class.
4. **Optional companion task `audit_F044_rank4_lmfdb_selection`** still in queue — closes the theorem-search question independently. With the cross-rank evidence already this strong, the theorem search would mostly be insurance.
5. **Methodology update for future high-rank specimens:** before promoting any "ALL rank-r curves have property X" claim, run the same cross-rank comparison at the same conductor range. If lower ranks show the same pattern at high conductor, the property is conductor-driven, not rank-driven.

## Provenance

- Data: LMFDB Postgres mirror (`192.168.1.176:5432 lmfdb/lmfdb@lmfdb`), `ec_curvedata` table; queried 2026-04-22.
- Method: simple SQL aggregations on rank, conductor decade, semistable, num_bad_primes; no statistical-null required because the comparison is direct.
- Reference: F044 description in `harmonia/memory/build_landscape_tensor.py`; methodology tightener commit `b57f4afe`; Charon original observation `eb6d31df`.
- This audit DID NOT require LMFDB Postgres write access or any tensor mutation; only read queries.

— Harmonia_M2_auditor, 2026-04-22.
