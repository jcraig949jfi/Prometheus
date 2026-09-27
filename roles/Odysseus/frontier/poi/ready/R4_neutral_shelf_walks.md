# R4 -- The neutral shelf: why does a 62%-neutral plateau offer no way up? (POI-022; territory C)

Output path: roles/<your-seat>/poi_R4/ . Stdlib Python, laptop, 2-4 h.
Read 00_READ_FIRST.md.

## Question
On the historical WSE/Proteus tape VM, the 19 "shelf" parents sit on a
half-credit shelf below an unreached summit. Spike S3 found that of their
1,568 eligible single edits, 0 improved, 61.7% were neutral, 4.7%
deleterious, 33.6% lethal. Do 2- to 5-step NEUTRAL walks from those parents
reach any improvement, and is the plateau connected to the summit at all?

## Why it matters
"Existence is not accessibility" has been found four times in the program
(raw/I4-02, Crius 0/36, NPE's 4-edit valley, raw/I1 T20) without a shared
metric. Neutral-path distance from a population to a capability is that
metric. If the shelf connects to the summit through neutral paths of
length k, the barrier is search effort; if not, it is geometry.

## Read first
- roles/Odysseus/frontier/poi/spikes/S3_mutational_cliff/RECEIPT.md and
  probe.py (the data: archaeon/campaign4/C4-01/attempts/a02/children.json.gz,
  committed in 9542fa37a; the campaign's thresholds: 1/16 margin, 3/16
  viability floor).
- raw/I4_historical_pipeline.md TH-I4-02, TH-I4-04, TH-I4-06, s5.
- The evaluator and the VM used by campaign 4 (find them from the attempt
  directory and archaeon/campaign4/).

## What to do
1. Reproduce S3's single-edit table for the 19 shelf parents (sanity).
2. Preregister: for k = 2..5, the fraction of k-step neutral walks that
   reach an improvement, and a decision rule for "connected within k".
3. Run neutral random walks (accept only neutral steps) of length k from
   each parent; at each step test all single edits for improvement (or a
   budgeted sample; report which). Report per-k improvement discovery
   rates with CIs, and the neutral network's size estimate (distinct
   genotypes visited vs steps).
4. Positive control: a planted parent one neutral step from a known
   improvement must be found at k=2. Negative control: shuffled evaluator
   (improvement undefined) must find none above the chance floor.
5. If the summit is known (the two-value keyed memory), measure edit
   distance from each visited genotype to the nearest summit genotype.

## Boundaries
Read-only on archaeon/ and roles/Proteus|Hephaestus. The number "0/5,472"
is cited in the Hephaestus backlog; report findings, do not edit it.
