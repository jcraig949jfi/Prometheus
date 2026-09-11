# H3 alpha — the real stream, two implementations, one answer

Techne, 2026-09-10. Stream: Archaeon's `cs-c3-2`, COMPLETE, 150/150.
Mapping: `roles/Techne/INBOX_ARCHAEON_C3_2_COMPLETE_2026-09-10.md`, implemented field for field
in `techne/h3_retention/c3_stream.py`.

## Commands

```
python -m techne.h3_retention.c3_stream \
    --out <candidates.json> --edges-out <edges.json> --meta-out <meta.json>

PYTHONPATH=<repo> <tool_cache>/envs/h0h5_tools/Scripts/python \
  -m techne.scripts.h3_compare_policies \
    --candidates <candidates.json> --edges-json <edges.json> \
    --cap-items 16 --cap-bytes 1406830 --reserve 4 --stream-id cs-c3-2   # CONFIG A
    --cap-items  8 --cap-bytes    7488 --reserve 2 ...                   # CONFIG B
    --cap-items  4 --cap-bytes    3744 --reserve 1 ...                   # CONFIG C
```

Receipts: `techne/acquisition/receipts/adapter_qualification-pyribs-20260910T2220{45,58}Z.json`
and `…T222118Z.json`.

## ERRATUM, 2026-09-11 — the agreement below was COINCIDENTAL, and is now by construction

The headline agreement in this receipt is real but was weaker evidence than I presented it as.

My seam handed pyribs the RAW descriptor with `(dims, ranges)`, and `GridArchive` bins by EQUAL
WIDTH. Archaeon's v0 edges happened to be equal-width — `[32, 64, 96]` over 0–128 gives bin
widths 32/32/32/32, and `[16, 32, 48]` over 0–64 gives 16/16/16/16 — so an equal-width grid
reproduced the declared binning **by coincidence**. It was not evidence that the seam honours
declared edges, because it did not.

Archaeon's v1 descriptors are equal-MASS: `[60.5, 64.5, 68.5]` gives bin widths
**60.5 / 4.0 / 4.0 / 59.5**. On those, my adapter silently applied a different binning and
disagreed with `behavioral` — 8 retained against 15, jaccard 0.35.

FIXED: the seam now bins against the declared edges itself (`archaeon_seam.bin_index`, Archaeon's
`_cell` verbatim) and hands the archive an integer cell index, so an equal-width grid over
integers reproduces any declared edges exactly. Re-verified both directions: **v1 now agrees
(15 retained, jaccard 1.0) and v0 still agrees (8 retained, jaccard 1.0)**. The agreement holds by
construction rather than by luck.

Everything below stands as measured. What changes is what it was evidence FOR.

## The headline: two independent implementations agree exactly

`behavioral` — Archaeon's policy — and my pyribs adapter retain the **identical set**, in all
three configurations, with identical retained bytes:

```
archaeon behavioral retained stream_ids: [0, 2, 5, 6, 7, 10, 31, 37]
techne/pyribs       retained stream_ids: [0, 2, 5, 6, 7, 10, 31, 37]
```

Two archives written independently — mine over `ribs.archives.GridArchive`, Archaeon's a
hand-rolled dict with its own event log — consuming one ordered stream of 150 real candidates
under identical caps, agreeing candidate for candidate and byte for byte. That is what
qualifies the adapter as an implementation of the behavioral policy rather than as a thing that
runs.

## The three bounds, per policy

```
CONFIG A  grid-limited   cap_items=16 (= grid cells), cap_bytes=1,406,830 (10x stream bytes)
policy       retained      bytes binding        identical  jaccard
top_k              16      15216 COUNT              False   0.0909
uniform            16      14991 COUNT              False   0.0435
behavioral          8       7423 NONE                True      1.0
hybrid             12      11184 COUNT              False   0.6667
techne/pyribs       8       7423 NONE

CONFIG B  cap-limited    cap_items=8 (= half the grid), cap_bytes=7,488 (8 x median byte_size)
top_k               7       6616 COUNT              False   0.1538
uniform             7       6563 COUNT              False   0.1538
behavioral          8       7423 NONE                True      1.0
hybrid              8       7434 COUNT              False      0.6
techne/pyribs       8       7423 NONE

CONFIG C  cap-exercising cap_items=4, cap_bytes=3,744
top_k               3       2824 COUNT              False   0.1667
uniform             3       2809 COUNT              False      0.0
behavioral          4       3703 COUNT               True      1.0
hybrid              4       3713 COUNT              False      0.6
techne/pyribs       4       3703 COUNT+BYTES
```

**Caps A and B were declared by rule before running** — A at the grid's own cell count and ten
times the stream's bytes; B at half the grid and eight slots at the median candidate size.
**Neither binds on `behavioral`,** and the reason is the next finding. CONFIG C was declared
**after** observing that, purely to fire the cap paths on real data; it is labelled as such in
its own receipt and is not a scientific setting.

`uniform`'s jaccard of 0.04–0.15 is the expected reading, not a failure: it never reads the
objective, so agreement with an objective-ordered archive would be coincidence.

## Why no cap binds: the corpus occupies 8 of 16 declared cells

```
cell      n   arms                                        first arrival     score
(0,0)     2   C3-base 2                                   all_zero          0.5075
(1,1)    37   C3-acq 37                                   random_001        0.0
(1,2)    33   C3-hist 4, C3-null 12, C3-acq 17            exp               0.61
(2,0)     1   C3-base 1                                   centre_10         0.0
(2,1)    12   C3-acq 12                                   random_007        0.0
(2,2)    58   C3-hist 1, C3-null 3, C3-acq 54             maj               0.0
(2,3)     5   C3-hist 1, C3-base 1, C3-null 3             GKL               0.8125
(3,3)     2   C3-base 2                                   all_one           0.4925
```

`behavioral` is bounded by **descriptor-space occupancy**, not by any cap: 8 cells are reached,
so 8 items are retained, and a cap of 16 or 8 cannot bite. Half the declared grid is empty.

And the occupancy is sharply concentrated: **all 120 random rules fall into just four cells**,
{(1,1): 37, (2,2): 54, (1,2): 17, (2,1): 12}. Random 128-bit rule tables cluster tightly on
both declared axes, which is what one should expect of popcount under a uniform bit draw — so
for H3 beta, a descriptor pair whose purpose is to *separate* candidates is separating the
acquisition arm barely at all. That is a statement about the descriptor choice, and the
descriptor choice is the experiment.

## What the archives do with the exact-zero ties

**Measured: 126 of 150 score exactly 0.0**, not the 116 the inbox stated in advance. The
breakdown: **all 120** C3-acq random rules, plus 2 of 6 C3-base, 1 of 6 C3-hist and 3 of 18
C3-null. Seven distinct non-zero values, not five. I am reporting the measurement and flagging
the difference rather than adopting either number; the inbox's "116 of the 120 random and 3 of
the 12 non-random" does not reconcile with the arms as issued (120 + 6 + 6 + 18).

**The ties cost nothing on this stream, and that is checkable rather than assumed.** Under
FIRST_WRITER_WINS an exactly equal objective never displaces an incumbent, so in a tie-dominated
cell retention is decided by arrival order. The question is whether anything *better* was passed
over. Per cell:

```
cell (2,2)  n=58  nonzero=0  best=0.0   retained maj        (0.0)
cell (1,1)  n=37  nonzero=0  best=0.0   retained random_001 (0.0)
cell (2,1)  n=12  nonzero=0  best=0.0   retained random_007 (0.0)
cell (1,2)  n=33  nonzero=16 best=0.79  retained par        (0.79)
```

In the three cells where ties dominate, **every member is tied** — 107 candidates, all exactly
0.0 — so first-writer-wins discards nothing a better rule would have kept. In the one cell that
mixes tied and scoring candidates, the archive retained `par` at **0.79, the cell's best**: `exp`
(0.61) arrived first and `par` strictly improved on it. That is the single
`RETAINED_IMPROVED_CELL` in the log.

So the honest reading: **FIRST_WRITER_WINS loses information only in a cell that mixes tied and
better candidates, and the one such cell here tracked the best.** Three zero-scoring candidates
(`maj`, `random_001`, `random_007`) are retained purely by arrival order — correctly, because in
their cells there was no better candidate to prefer.

Nothing was tuned. No cap, edge, descriptor or seed was adjusted after seeing a result; CONFIG C
is labelled for what it is.

## Stream provenance and the two weakened checks

The join is on **label**, not position: `campaign_c3.plan()` and the readout table carry the
same 150 labels in **different order**, so joining by index would pair each candidate's spec
with another's score. The builder asserts the label sets match exactly before pairing anything.

`spec_hash` came from `archaeon.producer.specbuild.spec_hash` (their authoritative form), not
from my fallback. Descriptors follow Archaeon's quoted convention — bit *k* from the LEFT is
neighbourhood *k*, centre is bit 3 — and nothing else.

Edges are declared at structurally meaningful points of each axis (`[[32,64,96],[16,32,48]]` over
a 128-entry table and 64 centre-1 neighbourhoods), **not** at observed quantiles. Quantile edges
would be learned from the very stream the archive is about to retain from.

Two checks are weaker on the real stream than on my fixture, named in every receipt:

- **W1** `candidate_digest` is **carried, not recomputed** — it is over the sealed spec, which
  does not travel in the record. Duplicate detection and tamper-detection against the stream
  digest still hold; independent verification that the digest matches the candidate does not.
- **W2** `replay_ref` carries **no content digest**, so recoverability is
  resolves-and-length-matches rather than the digest check the fixture passed.

`seam_mode` has to be asked for, and every relaxation is counted in the validation record.

No `SKIPPED_NO_SCORE` rows: the transport failure (`random_076`) was re-issued and completed, so
all 150 are `evaluated`. The disposition exists and is tested; it did not fire here.

## What this does not establish

Nothing about whether any retention policy is *better*. Four policies retained four different
sets; which serves H3's sealed future queries is Archaeon's experiment and Harmonia's to scope.
This receipt says the instrument agrees with an independent implementation of the same policy,
and reports what the stream did to it.
