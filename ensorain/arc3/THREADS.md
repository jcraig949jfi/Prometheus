# ARC3 research backlog: memory, compression, selectivity, generalization (Ensorain)

Directive: roles/Ensorain/prompts/2026-09-28_arc3_directive/.
Central question: WHEN IS DISCARDING INFORMATION NECESSARY FOR GENERALIZATION, rather than one way of implementing a
bounded learner?
Rules: merge duplicates, kill answered threads, demote low-information work. The historical order (incl. WTP-04) is not
binding.
Field order per thread: Q (question) / WHY (why it matters) / EV (current evidence, ours) / EXT (external evidence;
filled from the lit raids) / UNC (uncertainty) / DISC (cheapest discriminator) / METHOD / RES (resource class) / MAT
(maturity: idea < designed < ready < queued < running < answered).

## T01 LM01 frozen campaign
- Q: per stratum, what exact retention buys over same-optimizer bounded reservoirs; is a transient learned fit needed?
- WHY: the only frozen, calibrated measurement in the territory.
- EV: dev only. Reservoir AC rises with B; L-K ~0 AC on never-seen cells.
- UNC: 23 of 75 strata are UNTESTED; F-C has power in ~10 strata.
- DISC: the campaign itself.
- METHOD: WTP / lm01.
- RES: M2 cpu8 ~9 h.
- MAT: queued (Q1).

## T02 Where does compression occur (storage vs readout)
- Q: for a given accuracy, is the compression in what is STORED or in what the READOUT computes? Factorial:
  {exact store, bounded state} x {simple readout, refit readout}.
- WHY: this may be the real LM01 phenomenon (directive E); "lossless storage" is not "no compression".
- EV: L-K (exact + simple) ~0; L-R (exact + refit) ~2.8; S (bounded + simple readout) ~2.0; BufferALS (bounded +
  refit) climbs with B.
- EXT: the theory separates three compression loci: storage (IB, sufficient statistics), HYPOTHESIS (MDL, PAC-Bayes,
  MI/CMI bounds; the only one with a clean link to generalization), and readout (V-information, decodable IB).
  Attributing generalization to STORAGE compression repeats the error Saxe et al. 2018 refuted. LM01 measures storage
  (HR2, bytes) and readout (L-K vs L-R) but NOT hypothesis compression. Add a hypothesis-description-length meter (the
  fitted model's bits, e.g. rank x (rows + cols) x precision, and the information the weights hold about the sample).
- UNC: readout expressiveness is confounded with optimizer quality.
- DISC: a 2x2 on LM01 rows plus a 4th cell, "bounded state + refit" at matched state bytes: BufferALS at B -> 0 with
  factors only vs S-lowrank at the same cap.
- METHOD: analysis of T01 rows plus a small dev factorial.
- RES: light CPU; can run off M2 (numpy only).
- MAT: designed (below, E-plan).

## T03 Information-theoretic availability vs computationally accessible generalization
- Q: does extra exact history ever HURT a bounded-compute predictor while being unable to hurt the Bayes predictor?
- WHY: directive J; possibly the core result.
- EV: none measured yet. The reservoir ladder is monotone on planted low-rank (dev). F3 recency-blind mixing hurts
  L-K/L-R.
- EXT (lit/LIT_THEORY.md): free information can never hurt a correctly specified unbounded Bayesian (Good 1967,
  Blackwell 1953). "Accessible" information is formalized as V-information (Xu et al. 2020; the DPI fails, so
  computation can create usable information) and by epiplexity (Finzi et al. 2026, preprint), memory-sample bounds
  (Raz 2016) and computationally bounded prediction (Sharan et al. 2018). No framework unifies memory, compute and
  samples; a synthetic study sits in that gap. "More data hurts" is a LEARNER property (Nakkiran 2019; monotonization,
  Bousquet et al. 2022) or a sign of misspecification (Grunwald and van Ommen 2017).
- UNC: no Bayes-optimal reference exists in LM01 worlds. That is why T17 exists.
- DISC: worlds with a computable posterior predictive (Gaussian low-rank with known prior -> closed-form Bayes; switch
  worlds with known hazard -> Bayesian changepoint predictor). Compare Bayes vs bounded readouts as history grows.
- METHOD: new small engine on WTP generators; numpy.
- RES: light CPU, off M2.
- MAT: idea -> design in PKG-J.

## T04 Causal selectivity (restore the discarded distinctions)
- Q: does discarding particular distinctions CAUSE better generalization?
- WHY: REQUIREMENT is untested (D11); the central causal question.
- EV: D11 showed that swap-to-blind-merge is decided by construction.
- DISC: the restore design (PKG-F).
- METHOD: WTP arms plus a restore operator.
- RES: M2 or off-M2 (numpy).
- MAT: designing (Block F).

## T05 Capacity vs selection (reservoir as bridge)
- Q: at matched capacity, does semantic selection beat random retention, at matched bytes AND matched HR2?
- WHY: directive M. If random matches, the "selective" advantage is capacity.
- EV: dev positive control: oracle eviction +.91; both system candidates LOSE to random under heteroscedastic noise.
- DISC: T01 F-C readings plus a sweep of noise heteroscedasticity (where residual eviction should flip from harmful to
  helpful).
- RES: light.
- MAT: partly in T01; extension designed.

## T06 Nuisance taxonomy as a controlled axis
- Q: which kinds of extra information hurt (independent noise, spurious correlation, obsolete structure,
  regime-specific structure, high-frequency detail, episodic identity), and through which route (storage, retrieval,
  optimization)?
- WHY: directive G; turns forgetting into a causal adaptation question.
- EV: F5 at nuis_p = 1 means every arm falls; at .5 it is learnable; the L-R split-rule artefact on F5-lowrank.
- DISC: one world generator with a dial on how predictive a formerly useful distinction remains (reliability decays
  from 1 to 0 across the life).
- RES: light CPU.
- MAT: idea -> PKG-G.

## T07 Switching: mechanisms of context selection
- Q: do successful systems overwrite, discount, gate retrieval, infer regime, split, or keep multiple models?
- WHY: directive H. The exact store may lose only because the readout cannot find the relevant history.
- EV: F3: S-cp/S-tt 1.3-1.9 vs L-R-rec .5-.7; the reservoir is recency-blind; the recency half-life was chosen from 2
  values.
- DISC: add an oracle-regime-gated L-R (retrieve only the current episode). If it matches or beats S, then the loss was
  retrieval, not memory. Then a learned changepoint gate.
- RES: light.
- MAT: designed (cheap probe).

## T08 Transfer: examples vs latent structure vs reusable abstraction
- Q: which retained information survives a field change?
- WHY: directive I; the North Star (symbolic compression).
- EV: F4 is close (.2-.5) except spectral (S-tt leads); E6 fails in F4.
- DISC: transfer with a shared basis vs a shared component vs shared-nothing; measure how much of field A's retained
  state is used for field B (ablate A's records vs A's factors).
- RES: light.
- MAT: idea.

## T09 Compute-memory-accuracy trade surface
- Q: do systems substitute compute for compression? Is there a Pareto surface over (bytes, query ops, fit ops, AC)?
- WHY: directive K.
- EV: meters exist per arm (ops, replay ops, bytes, reads). L-R pays per-query refit ops.
- DISC: analysis of T01 meters; fit the frontier.
- RES: light, off M2.
- MAT: ready once T01 rows exist.

## T10 Minimal sufficient retained state
- Q: what is the smallest state from which future prediction is as good as from full history, per family?
- WHY: sufficient statistics; the North Star.
- EV: planted rank-r worlds have a known finite sufficient statistic (the factors) up to noise.
- DISC: compare B* (the reservoir saturation point) with the parameter count of the true generator.
- RES: light.
- MAT: idea.

## T11 Readout interference (irrelevant stored items)
- EXT (lit/LIT_MEMORY_SYSTEMS.md):
  - in exact stores, interference is mostly a READOUT property: harm scales with distractor SIMILARITY and position, not
    count (GSM-IC; Context Rot), and the fixes are readout-only;
  - the "random documents help" RAG claim failed reproduction;
  - dense associative memory raises capacity from ~0.14N to exp(N) by changing ONLY the readout nonlinearity.
- DISC update: vary distractor similarity at a FIXED distractor count (lit D6).
- Q: does storing irrelevant items hurt through retrieval (k-NN neighbourhoods) rather than storage?
- DISC: inject k irrelevant records into an exact store and measure L-K / H degradation vs L-R.
- RES: light.
- MAT: idea.

## T12 Optimizer confound, general
- EXT: kNN-LM's gain over its own parametric model on the SAME data is a readout effect (key representation,
  approximate search, softmax temperature; Xu, Alon, Neubig 2023). Parallel to our D6/D7: apparent memory effects
  decompose into readout and optimization effects.
- Q: does every apparent memory effect survive equalising the optimizer (SGD vs ALS vs closed form)?
- EV: D6/D7.
- DISC: rerun the T01 secondary with ALS-fit bounded substrates (BufferALS at B = 0).
- RES: light.
- MAT: designed.

## T13 Stability as a phenomenon
- Q: why are S-cp (bimodal) and cold-start L-R seed-unstable while the warm reservoir is stable? Does warm-starting act
  as implicit memory?
- WHY: warm state carries history in its optimizer trajectory, a hidden form of retention.
- DISC: cold vs warm refit on the same store.
- RES: light.
- MAT: idea.

## T14 WTP-04 review (Block T)
- Former plan: N6 rung, cross-field transfer, class-agnostic admission, learning-time/lifetime search.
- LM01 absorbed N6 (converged L-R) and class-agnostic families. Cross-field transfer is T08.
- Verdict: DEMOTED. Its surviving content is merged into T08 (transfer) and T09 (lifetime/compute).
- Revive only if open-ended search over world genomes becomes the most discriminating tool again.

## T15 Cross-engine: presence vs causal use
- Q: Ananke-style "information present but not causally used" applied to LM01 arms. Which stored records does L-R
  actually use (leave-one-out influence)?
- DISC: influence of stored records on predictions (exactly computable for ridge ALS near convergence).
- RES: light.
- MAT: idea.

## T16 Learned memory policy
- Q: can an agent LEARN when to retain/evict/discount (meta-level) such that it beats fixed policies across families?
- WHY: an adaptive policy is what "intelligent selectivity" would look like.
- DISC: bandit over eviction policies per stratum on dev.
- RES: moderate.
- MAT: idea (after T04/T05).

## T17 Sufficiency-class ladder with exact oracles (NEW from lit/LIT_THEORY.md D1/D2/D8/D10)
- Q: does each memory strategy retain what is PROVABLY sufficient and nothing more, in worlds where the answer key is
  exact?
- WHY: LM01 has no Bayes reference. This ladder gives (loss - Bayes loss) and (retained bits - minimal sufficient bits)
  for every learner, which is a published answer key (doctrine: "measurement carries its answer").
- EXT: the worlds:
  - W0 iid;
  - W1 exchangeable with an unknown parameter (counts are sufficient);
  - W2 order-k Markov (window);
  - W3 Even process (finite causal state, no finite window);
  - W4 nonunifilar HMM (belief state);
  - W5 key-value long tail (exact history necessary).
  Crutchfield-Feldman truncation curves; crypticity pairs (equal E, different C_mu).
- DISC: the three locus-of-compression arms (storage statistic / verbatim + query-time summary / verbatim + restricted
  readout) across W0-W5. Predicted: equal on W1-W3 at the sufficient rate; storage loses on W5; the restricted readout
  exposes V-information limits.
- METHOD: a NEW small sequence engine (numpy; not WTP), with epsilon-machines constructed by hand.
- RES: light CPU, OFF M2 (any node).
- MAT: designed in lit; package PKG-S1 to write.

## T18 Available vs accessible: nuisance geometry dial (NEW; lit D3/D4)
- Q: with equal Shannon content, does ROTATED nuisance hurt more than axis-aligned nuisance (Ng 2004: rotation-invariant
  learners pay linearly, L1 learners pay log)? Does a PRG world behave like noise for bounded learners?
- WHY: a direct test of the availability/accessibility distinction (directive J); nuisance as a controlled axis (T06).
- DISC: k appended iid dims, axis-aligned vs randomly rotated into the signal; learners: ridge (rotation-invariant) vs
  L1 vs k-NN vs a reservoir. PRG vs true-random twin; same content, permuted order.
- RES: light, off M2.
- MAT: idea+.

## T19 Memory-capped streaming parity (NEW; lit D5)
- Q: is there a sharp memory threshold below which a learner needs vastly more samples (Raz 2016, ~n^2/25 bits)?
- WHY: the cleanest "retention is NECESSARY for efficiency" demonstration; a positive control for the claim that
  discarding HURTS.
- DISC: n = 10-20, a bounded-memory learner at budgets above/below the threshold; samples-to-solve.
- RES: light, off M2.
- MAT: idea+.

## T20 Long-tail memorization (NEW; lit D7)
- Q: does aggressive compression lose exactly on rare subpopulations, and does the required retention decay with n
  (Feldman 2020; Brown et al. 2021)?
- DISC: Zipfian subpopulations with singleton labels; accuracy on the tail vs bits retained per item.
- RES: light.
- MAT: idea.

## T21 Is "excess history hurts" a learner property? (NEW; lit D6/D9)
- Q: when a learner's loss rises with history, does a monotone wrapper remove it (then it is a learner property), and
  does misspecification explain it (then it is a model property)?
- DISC: a sample-wise sweep at fixed capacity plus a holdout-accept monotonized wrapper; misspecified Bayes (order-k fit
  to the Even process) with a tempered posterior.
- RES: light.
- MAT: idea. Pairs with T03.

## T22 Change the question after writing (NEW; lit/LIT_MEMORY_SYSTEMS.md D3). KEY DISCRIMINATOR
- Q: after the stream ends, query a latent or a formerly-nuisance variable that was NOT useful at write time. Which
  memories can still answer it?
- WHY: a write-time compressor must decide before it knows the query; an exact store defers compression to the readout.
  This separates storage compression from readout compression without any capacity matching, and it is the natural
  core of the causal-selectivity experiment (T04, Block F): the "discarded" distinctions become causally testable when
  the task changes to need them.
- DISC: WTP fields with two targets, target A during the life and target B (a different linear functional of the
  latent, or the nuisance coordinate itself) at test. Arms: S (bounded, trained on A), BufferALS, L-R, L-K.
- RES: light, WTP code (M2 or any node with the repo).
- MAT: idea+, folded into PKG-F.

## T23 Memorization -> generalization transition in bounded superposed memories (NEW; lit D5)
- Q: as the number of stored episodes crosses a capacity, does exact recall fall WHILE unseen-combination accuracy
  rises (Pham, Krotov et al. 2025; Kalaj et al. 2025)?
- WHY: this is the regime where generalization is BOUGHT by compression; the direct counter to "lossless is the upper
  bound".
- DISC: sweep the stored count in a bounded low-rank / associative arm; plot recall-of-seen vs AC-on-unseen together.
  LM01 reservoir rows give a partial version (HR2 vs never-seen AC per rung).
- RES: light.
- MAT: idea; partial data from T01.
