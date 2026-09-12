# hypothesis shrinker -- failure landscape, ablations, decoys

Currency: 2026-09-11 (CUT-2). Receipt: ablations/RECEIPT_N1_2026-09-11.json.

## F. Failure modes, each with a receipt or a line
F1  move-set local minima (standalone): 1000 stays 1000 under 'n >= 1000 or n == 5'   N-b
F2  move-set local minima (engine): find(integers, x >= 1000 or x == 5) -> 1000        N-f
F3  non-monotone predicates end at seed-dependent local minima (283, 325; min 101)     N-d
F4  the same seed gave different results in two runs of the same script (1291, 283)
    while derandomize=True was stable -- run-instability of seeded find()              N-d, S-a
F5  structural pass applicability is decided by strategy-recorded LABELS:
    pass_to_descendant fires on plain st.recursive, 0 calls on .map()/.filter()       N-g vs P-b
F6  the consumer's non-minimal case is reproduced exactly; the only pass that shrank
    it was reorder_spans, moving toward the ENCODING's order                            P-b
F7  the order is the encoding's, not the consumer's (Proteus says so in writing;
    24/45 measured by Techne; 1/1 here)                                                shrink.py docstring
F8  (read) coupled-value passes see only 3-4 nodes ahead                                shrinker.py 1396-1530
F9  (read) trees per pass reset on every successful shrink                              shrinker.py 830
F10 (read) run() without full=True is one step in the standalone shrinkers              common.py 78-88
F11 the first P-a5 cheat check was malformed and reported a vacuous 'true' -- a
    Nyx defect caught on reading the receipt; fixed and rerun                            CUTS.md

## A. Ablations
RUN  A-phase   Phase.shrink off (N-c): returned == first found (null config null)
RUN  A-derand  derandomize vs seed (S-a): equal
NOT RUN  remove-pass ablations (no switch; needs a pass-list harness)
NOT RUN  order swap (allow_transition can veto, not re-rank)
NOT RUN  the explain phase in isolation (c11)

## D. Decoys
D1  a shrinker that returns the initial for every input passes N-a and fails P-a1: run both
D2  a 'minimal' claim that is local-minimality under the move set (Techne separates SOUND from MINIMAL for this reason)
D3  success attributed to structure when reorder or deletion did it: read the profile per pass
