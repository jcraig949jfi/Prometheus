# 16 -- operator: 32-seed / 4-RNG-family pooling is the mandatory minimum for all baselines; purge the 8-seed baselines; G re-screens; B re-scores

Issued 2026-09-15 ~02:52 to Nestor-A[m1-449a9e76], conductor, after D-R4-2. Verbatim below the rule.

---

I completely agree with your recommendation. Lock in the 32-seed pool across 4 RNG families as the new mandatory minimum for all baseline calculations.
Lane D proving that w13 only survives the screen 13.6% of the time on 8-seed draws is the final nail in the coffin for small sample sizes. We already saw hints of this in Round 2 when D discovered that the 8-seed IQRs could swing by 2x just by changing the RNG family. If a world only passes the trivial-policy screen by getting lucky with its seed draw, it’s not a rigorously hard environment—it’s a statistical ghost.
Any Clause A compression claim built on a ghost baseline is mathematically hollow.
Here is the execution plan to enforce this:
 * Purge the Cache: Nuke the current 8-seed baseline cache entirely.
 * Re-Screen (Builder G): Have G re-run the Trivial Policy Suite and baseline calculations for all candidate worlds using the new 32-seed, 4-family pooling requirement.
 * Re-Score (Lane B): Once G establishes the mathematically rigorous floors, re-score Lane B's elites on w13 (and any other previously "passed" cells). If they fall below the 0.95 Progress Above Floor metric under the new 32-seed scrutiny, strip their PASS status immediately.
This guarantees that when Prometheus finally outputs a highly compressed cognitive primitive, we know with absolute certainty that it survived a genuinely hostile, statistically robust environment. Proceed with the re-screen.
