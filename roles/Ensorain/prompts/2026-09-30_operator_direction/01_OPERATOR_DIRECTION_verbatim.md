I'd keep Ensorain on its current work long enough to finish the instrument repairs, then deliberately pull it back toward the substrate collider. Right now PKG-F/LM02 are useful plumbing, but they should not become Ensorain's scientific identity.

The sequence I'd use is:

1. Finish PKG-F on W-DRIFT. The important ruling is that low statistical power must never mean "unchanged." If a cell has too few records to detect drift, its state should be UNKNOWN / QUARANTINED, not admitted as fresh. Fix the per-cell power failure so stale records cannot leak back simply because n was small. Precommit a minimum effective sample size / CI-width or similar observability criterion. This is worth finishing because a bad drift gate can contaminate every later collider experiment.
2. Build LM02 as a bounded instrument test, not another research program. The question should be: When is a finite historical window sufficient to preserve the scientifically relevant result? Compare candidate windows against full-history/reference behavior across several drift rates, world families and substrates. Measure whether the window preserves downstream competence, substrate ordering and anomaly detection-not merely whether its statistics look similar. If there is no stable sufficiency region, record WINDOW_NOT_SUPPORTED and stop. Don't spend weeks tuning it into existence.
3. Then freeze this line. Keep LM01 held. I would not launch the old LM01 merely because its machinery is ready. It is an increasingly elaborate test of a fairly narrow selective-memory question. Ensorain now has a larger mission.

After those two instrument tasks, I think Ensorain's next major program should be something like WTP-04: Habitable Islands / Substrate Collider.

The striking WTP-03 result wasn't the hundreds of completion flags. It was that 38,000 candidates yielded only a tiny number of founding families that could support meaningful learning at all, and once one such family appeared, nearby mutations became fertile. That suggests a much more interesting scientific object than another broad random sweep:

Map the boundaries of computationally habitable worlds.

Take each genuinely independent founding family and perturb its physics outward in multiple directions: memory/environment ratio, world-change timescale, information cost, observation quality, irreversibility, credit delay, topology, compute budget, forgetting, active sensing, recurrence. Find where learning becomes possible and where it dies.

Do this before choosing a favored substrate.

Inside every habitable neighborhood, collide the same experience stream against:

TT . CP . matrix/low-rank . DCT/spectral . sparse . graph memory . dense . simple symbolic/programmatic representations . cheap nulls.

Then we can ask the much better question:

As world physics changes, where does the preferred carrier of competence change?

That gives Ensorain genuine phase diagrams rather than architecture leaderboards.

I would make two lanes especially important.

First: substrate transformation. Allow a bounded learner to pay to convert its representation-dense->sparse, matrix->TT, episodic->factorized, internal->graph-external, numerical->symbolic where implementable. The interesting event isn't that TT beats matrix. It's that an organism exposed to a changing environment discovers that switching how information is represented improves future capability enough to pay for the conversion.

Second: non-tensor-native worlds. WTP-03 necessarily enriched for tensor completion because much of the world grammar was factorized numerical structure. Ensorain needs stranger matter: dynamic graph laws, causal hidden-state systems, compositional programs, rewriting systems, temporal rules, graph-of-tensor worlds, recursive structures, topology-dependent puzzles, environments where the compact representation is not known beforehand. Tensor substrates should sometimes win and sometimes get crushed.

That is where the collider becomes interesting.

A useful operating split for the seat would therefore be:

CURRENT: finish PKG-F -> finish LM02 -> close the instrumentation loop.

NEXT: map the WTP-03 habitable islands and their boundaries.

THEN: collide substrates inside those regions and look for reproducible crossovers, transformations, hybrids and transferable artifacts.

RESERVE: radically new world grammars that are not naturally TT/CP/matrix problems.

HOLD: LM01 unless we later identify a collider result for which LM01 is the right falsifier.

And I would give Ensorain one very strong rule going forward:

Cheap competitors first, always.

Constant, running statistic, marginal model, tiny lookup, trivial compressor, simple linear predictor. A world doesn't earn TT/CP/DCT/graph/symbolic collision time until those cheap mechanisms demonstrably cannot explain the behavior.

The philosophical shift is important: Ensorain shouldn't spend most of its compute asking "can this learner work?" It should increasingly ask:

"What properties must a universe have before learning is physically useful at all, and once it is useful, what form of information-bearing substrate survives there?"

That feels like the highest-value continuation of the Ensorain program.
