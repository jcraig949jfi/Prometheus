# Type B Candidate Characterization
## Date: 2026-04-01

## Summary

The 27,279 Type B candidates (tight zero clusters, no graph edges) are
**entirely higher-dimensional modular forms** (dim >= 2). They have no
graph edges because our graph only contains classical modularity bridges
(dim-1 EC-MF pairs), isogeny (EC-EC), and twist (MF-MF) edges.

This is NOT a discovery of unknown correspondences. It's a structural
observation: the zero-based geometry works for objects OUTSIDE the scope
of our current graph construction.

## Key Statistics

| Property | Value |
|----------|-------|
| Total Type B | 27,279 |
| Object type | 100% modular forms (0 ECs) |
| Dimension | 100% dim >= 2 (0% dim-1/rational) |
| Cross-conductor neighborhoods | 100% |
| Trivial character | 64.8% |
| Non-trivial character | 35.2% |
| Has EC zero-neighbor | 165 (0.6%) |

## Cluster Structure

DBSCAN (eps=0.5, min_samples=3):
- 11 clusters, 0.6% noise
- One dominant cluster: 25,357 members (93%) spanning 3,683 conductors
- One secondary cluster: 1,633 members (all dim-2, mostly trivial character)
- 9 small clusters (3-8 members each)

The dominant cluster contains forms of all dimensions (2-80+) and all
character orders. It's essentially the entire higher-dimensional MF
population clustered by zero similarity.

## Interpretation

These forms cluster because:
1. Zero distributions are governed by conductor and weight (Katz-Sarnak)
2. Higher-dimensional forms at similar conductors have similar zero statistics
3. The zero geometry creates a meaningful topology even for objects with no
   known algebraic relationships

They have no graph edges because:
1. The modularity theorem (our primary bridge source) only connects dim-1 forms to ECs
2. Higher-dimensional forms correspond to higher-dimensional abelian varieties
   (not in our database), Galois representations, or other objects we haven't ingested
3. Twist edges exist between some of these forms, but many have no known twist partners

## What to Do With This

1. **Don't claim these as "discoveries."** They're graph-incomplete, not graph-anomalous.
2. **Do use this to guide expansion.** If we ingest abelian varieties or Galois
   representations, these Type B forms are the ones most likely to gain new edges.
3. **The 165 with EC zero-neighbors are interesting.** Higher-dim forms whose zeros
   look like elliptic curve zeros — these might indicate unexpected correspondences
   or shared arithmetic structure across dimensions.
4. **Cluster 1 (1,633 dim-2 forms)** is the most homogeneous and might correspond
   to genus-2 curve families or specific Galois representation types.
