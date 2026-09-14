# diomedes K0 census -- failure landscape (the only product of a negative chop)

F1  cluster_bootstrap is DEGENERATE when the number of clusters is a power
    of two: _Lcg.below(n) = state % n reads the low bits of a mod-2^31 LCG,
    which for n = 2^k cycle through every residue in order; each resample
    of n draws is therefore a PERMUTATION of the clusters, every resample
    statistic equals the point estimate, half_width = 0.0 and
    includes_zero = False regardless of the data. Verified for n = 4 8 16 32
    (half-width 0.0, first two resamples permutations); n = 5 17 24 100
    behave (receipt C06-probe). The shipped self-test uses 24 clusters and
    cannot see it. Consequence: check 4 reports zero uncertainty, so check
    3 (gate vs its own error) passes ANY gate on such populations -- the
    instrument's own cheat path. Owner: Diomedes (parked). Reported.
F2  the 2x-error rule and the 0.05 floor are constants with no derivation
    in the file (POLICY presented as check).
F3  conditional_headroom returns None (not 0) when no state carries both
    classes; car() reads .get('qualifies') as falsy -> INADEQUATE unless
    entropy ~ 0; a population with headroom None and entropy > 0 is called
    INADEQUATE, not VACUOUS (read, not run).
F4  auc is O(pos x neg) per state; fine at the sizes here.

Ablations: none beyond the runs above (nothing to ablate that is not a
whole function). Cheat controls: c02 negative fired; c06 probe fired; c07
negative fired.
