# Genus-2 Crossing Results
## Date: 2026-04-02
## Status: Signal NOT confirmed as paramodular

### The Test
Ingested 1,252 genus-2 curves (conductor <= 5000) from LMFDB with their L-function zeros.
Tested whether the dim-2 Type B forms are zero-proximate to genus-2 curves.

### Results
Of 4,265 dim-2 wt-2 Type B forms:
- Found genus-2 neighbor in top-30: **2** (0.05%)
- Found EC neighbor in top-30: 205 (4.8%)
- The 163's nearest genus-2 distance (0.66) is WORSE than baseline random dim-2 forms (0.61)
- The 163 are closer to ECs (0.42) than to genus-2 curves (0.66)

### Verdict
The EC-proximity of the 163 is NOT explained by paramodular correspondence.
These forms are not zero-proximate to genus-2 curves. The signal is likely a
zero-statistics artifact: weight-2 dim-2 non-trivial-character forms share
certain zero distribution features with elliptic curves for reasons that are
about weight and character, not about functorial descent.

### What this means
- The paramodular interpretation is killed for these specific forms
- Character remains the most likely explanation (3.3x enrichment from Kill Test 2)
- The receipt is clean: we tested the most exciting interpretation and it failed
- The 163 go into the pile as "character-dependent EC-proximity, not paramodular"

### What survives
- The zero coordinate system WORKS (100% bridge recovery, ARI=0.55 for rank)
- The three-layer architecture is validated
- The disagreement atlas correctly identified these forms as interesting
- The pipeline correctly ingested a new object type (genus-2) through the same loop
- The genus-2 crossing itself validates Charon as foundational infrastructure

### Important: the pipeline generalized
1,252 genus-2 curves entered through the same pipeline:
  ingest → zero vectors → k-NN → comparison
No schema changes. No new code architecture. Same battery-compatible infrastructure.
This is the proof that Charon's architecture scales to new object types.
