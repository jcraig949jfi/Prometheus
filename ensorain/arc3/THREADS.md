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
- UNC: no Bayes-optimal reference exists in LM01 worlds.
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
- Q: does storing irrelevant items hurt through retrieval (k-NN neighbourhoods) rather than storage?
- DISC: inject k irrelevant records into an exact store and measure L-K / H degradation vs L-R.
- RES: light.
- MAT: idea.

## T12 Optimizer confound, general
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
