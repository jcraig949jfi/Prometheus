# MAP-Elites -- failure landscape, ablations, decoys (charter V)

Currency: 2026-09-11. Grades as in PROVENANCE.md. The T1 rows are the
ones a consumer should lean on; the T2 rows are remembered and await
NYX-05.

## Failures observed IN THIS REPOSITORY (T1)

F1  Binning disagreement between two implementations of one mechanism.
    pyribs GridArchive bins by equal width; Archaeon's declared edges
    are equal-mass from a pilot (widths 60.5 / 4.0 / 4.0 / 59.5 on axis
    0). Techne's adapter therefore PRE-BINS and hands pyribs an index.
    The 2026-09-10 agreement between the two was exact by coincidence
    (v0 edges were equal-width), not by construction.
    techne/acquisition/receipts/adapter_qualification-pyribs-20260911T064705Z.json
    Failure shape: a mechanism's boundary was mistaken for an
    implementation detail until a second implementation disagreed.
    Gradient: two implementations of any organ, compared on one stream,
    is a cheap cut-finder.

F2  Descriptors outside the declared edges: 10 of 150 in the same
    receipt. Whether they are clamped into the last bin or dropped is
    an implementation choice that changes the archive.
    Failure shape: a declared range that the stream does not respect.
    Gradient: the out-of-range policy is a PARAMETERIZATION organ.

F3  Tie policy is a donor property, not a mechanism property. Techne
    measured pyribs's FIRST_WRITER_WINS at both granularities and
    declared it, refusing to inherit it silently, because a future
    release changing it would move every retention number.
    techne/h3_retention/adapter.py TIE_POLICY, TIE_POLICY_MEANING.
    Failure shape (averted): silent inheritance of an arbitrary rule.
    Gradient: every organ record names its tie / comparison rule.

F4  Coverage is not discovery. "pyribs imposes no objective of its own
    -- it maximises whatever the caller passes, per behavioural cell.
    Archive coverage therefore measures the caller's descriptor choice
    as much as the search; it is not evidence of discovery."
    techne/DONOR_INVENTORY.md line 50.
    Failure shape: a read-out that rewards the experimenter's choice.
    Gradient: pressure.map_elites.hidden_axis.v0 exists because of this
    row -- the axis must not be handed over.

F5  The comparison the mechanism was imported for has not run. H3's
    four-policy replay (top_k / uniform / behavioral / hybrid) is built
    and tested on fixtures and "waits for the first real compatible
    stream (C3)". roles/Archaeon/H0H5_STATUS.md.
    Failure shape: designed, not measured. Every ablation claim in the
    organ records is downgraded to "expected" for this reason.

## Failures REMEMBERED from the lineage (T2; resolve under NYX-05)

F6  Cell count explodes with descriptor dimension; CVT-MAP-Elites
    (doi:10.1109/TEVC.2017.2735550) replaced the grid with nearest-
    centroid partitioning for this reason.
F7  Uniform parent selection wastes evaluations on saturated regions
    once the archive is mostly full; curiosity- and novelty-based
    selection operators (Cully and Demiris, doi:10.1109/TEVC.2017.2704781)
    were introduced against this.
F8  Non-stationary objectives leave stale incumbents that block better
    candidates because the mechanism has no re-evaluation step (this row
    is REASONED from the mechanism, not cited; grade T3 until a source
    is found or a local run shows it).

## Decoys and broken variants ready for a soup (charter XIII)

D1  DECOY keeper: same interface as cell replacement, accepts every
    candidate and evicts uniformly at random when the cap binds. Passes
    any coverage-only read-out on a dense stream; carries no quality.
D2  BROKEN keeper: comparison inverted (strictly WORSE replaces). Same
    interface; a monotone read-out must fall.
D3  BROKEN keeper: strictness removed (>=) on a degenerate-objective
    stream: churn with no quality change; F3's measured tie facts are
    the fixture.
D4  DECOY binning: random key ignoring the descriptor (the cheat control
    of organ.map_elites.descriptor_binning.v0). Maximises apparent
    coverage; the detector for any coverage claim is to run this too.
D5  BROKEN selection: fitness-proportional in place of uniform; the
    chi-square uniformity test is the detector.

None of D1-D5 is implemented yet; NYX-13 makes them importable against
Archaeon's H3 stream contract with a test that BROKEN and DECOY are
distinguishable from HUMAN on the fixture stream.
