# Study 04: Empirical Study of Rediscovery

**Date:** 2026-05-05
**Owner:** general-purpose subagent (Aporia delegation)
**Substrate connection:** Discovery-via-rediscovery framework foundation; whether the substrate's central claim about same-loop-different-oracle-state is empirically supported.

## Problem statement (Prometheus-adapted)

Prometheus runs a *discovery-via-rediscovery* loop: pipelines are calibrated against catalogs (Mossinghoff for Lehmer, LMFDB for BSD/modular forms, Cremona for elliptic curves, KnotInfo for trace fields). When a candidate appears in the catalog, the system declares "rediscovery." When it doesn't, the same machinery is supposed to be discovering. The load-bearing assumption is:

> *the rediscovery pathway and the discovery pathway are the same computational object, differing only in oracle state (catalog hit vs. catalog miss).*

This study asks whether the empirical literature on multiple independent discovery in mathematics supports, refutes, or qualifies that assumption. If historical "independent rediscoveries" of theorems share structural pathways, the analogy is plausible. If they diverge wildly, the substrate may be conflating two very different processes.

A second, sharper concern: Prometheus's "rediscovery" is not historical re-derivation by a human, it is *catalog matching by a computational pipeline*. So there are two analogies in play, and they should not be confused:

1. *Internal*: substrate pipelines that hit known answers vs. miss them.
2. *External*: human mathematicians who independently arrive at the same theorem.

Whether (2) supports (1) depends on whether the structural unit of "pathway" transfers across the analogy. This study tries to be honest about that gap.

## Literature scan

The classical reference frame is **Robert K. Merton's "Singletons and Multiples in Scientific Discovery"** (Proc. Amer. Phil. Soc. 105, 1961, repr. *The Sociology of Science*, U. Chicago, 1973). Merton argued, against the "lone genius" view, that multiples are the rule and singletons the exception, and that this implies a strong sociological-structural component to discovery (the work was "in the air"). Earlier compilations: **Ogburn & Thomas (1922)** catalogued ~150 multiples; **Kroeber (1917)** framed the cultural-readiness argument.

**Stigler's law of eponymy** (Stigler 1980) is a corollary: priority is socially assigned, often to the person best positioned to propagate, not the first to derive. **Boyer's law** is its mathematics-specific version.

For mathematics specifically, the canonical textbook cases:

- **Newton & Leibniz on calculus** (1666 fluxional version vs. 1674 differential version, published 1684). The historical literature (e.g., Hall 1980; modern reviews via MacTutor and the EWA Direct 2024 reanalysis) emphasizes that the two routes were *structurally distinct*: Newton geometric/kinematic (fluxions, fluents), Leibniz algebraic/symbolic (differentials, sums). They converge on *equivalent statements* but via methods that took two further centuries (rigorous limits, then non-standard analysis) to reconcile.
- **Bolyai/Lobachevsky/Gauss on hyperbolic geometry** (Lobachevsky 1829; Bolyai 1832; Gauss unpublished). All three negate Euclid's parallel postulate, but the framings differ: Lobachevsky uses a multiple-parallels axiom directly; Bolyai parameterizes Euclidean and hyperbolic in a single family; Gauss approaches it via the angle-sum deficit. All three reach equivalent geometries, but the *axiomatic entry point* differs.
- **Hadamard & de la Vallée Poussin on the Prime Number Theorem** (both 1896). Both used complex analysis and both relied on the non-vanishing of ζ(s) on Re(s)=1. This is a *high-convergence* multiple: very similar pathways, both built on Riemann's 1859 framework, both reaching the same statement by the same broad strategy. Later, Selberg/Erdős (1949) found "elementary" proofs avoiding complex analysis entirely — a *low-convergence* rederivation of the same theorem.

The book-length reference for mathematics specifically is **Dawson, *Why Prove It Again? Alternative Proofs in Mathematical Practice*** (Springer, 2015), which catalogs theorems with multiple proofs and proposes criteria for when two proofs count as "different." Dawson's central observation, adapted: alternative proofs serve different epistemic purposes (verification, generalization, simplification, didactic, structural-insight), and proofs of the same theorem can be partitioned by these purposes more cleanly than by chronology. **Aigner & Ziegler's *Proofs from THE BOOK*** is the canonical exhibit: many theorems shown with multiple proofs that are obviously different objects.

For computational analogues, the **Wos (1988) "automated theorem finding" problem** remains open. The reviewed literature on automated theorem discovery (Colton's HR, Larry Wos's OTTER/Prover9 work, recent ATD surveys) reports that automated systems *predominantly rediscover* known simple results and that the leap to genuinely new theorems is poorly understood. This is the closest external analog to Prometheus's situation, and its honest message is: rediscovery is *easier* than discovery, and the gap between them is not yet characterized.

## Substrate-relevance

Mapping the literature to the substrate's claim:

**1. Does empirical rediscovery research support the same-loop-different-oracle-state claim?**

*Partially, with caveats.* Merton's data support that mathematical results are *over-determined* by their context — multiple investigators converging on the same theorem is normal, not exceptional. This is consistent with the substrate's view that a pipeline finding a known invariant via a generic strategy is doing the same kind of work as a pipeline finding an unknown one. However, the historical record also shows that the *path* often differs sharply (Newton/Leibniz, Selberg/Erdős vs. Hadamard) even when the *destination* matches. So "same loop" is true at the level of *result-equivalence-class*, but false at the level of *trace-equivalence*. For Prometheus, this matters: if the substrate identifies a candidate and the candidate is in the catalog, that's a rediscovery match in the *result* sense, but it tells us little about whether the pipeline traversed a discovery-shaped trajectory or a calibration-shaped shortcut.

**2. Structural difference: independent rediscovery vs. documented diffusion.**

Merton 1961 is explicit that telling these apart is hard and requires correspondence/manuscript evidence. Bolyai/Lobachevsky/Gauss is the cleanest "true independence" case (geographic isolation, no transmission). Newton/Leibniz is the canonical contested case (the priority dispute itself was an attempt to litigate this). For the substrate, the analog is whether two pipelines that hit the same target did so via the same primitives or via different ones — which is *measurable*, unlike for human mathematicians. This is actually a domain where the substrate has *better* introspection than the historical literature.

**3. Are some theorem-types more likely to have multiple independent routes?**

Suggestive but not rigorously established. Theorems that sit at the intersection of multiple frameworks (PNT: complex analysis ∩ analytic number theory ∩ elementary methods; FLT special exponents: descent ∩ cyclotomy ∩ modularity) tend to accumulate more independent proofs. Theorems that depend on a single specialized machine (e.g., classification of finite simple groups, four-color theorem) have not had many independent proofs even when widely studied. This *suggests* that "multiple-pathway-friendly" theorems live at high-degree nodes in the conceptual graph. For Prometheus this is interesting because the genus-2 / cross-domain bridge results in the substrate's own logs (project_genus2_rosetta) are precisely such intersection nodes — exactly the regime where multiple-route discovery should be easier and where catalog-match-as-rediscovery is most defensible.

**4. Has anyone catalogued which results in BSD / modular / knot domains were independently rediscovered?**

Not found, and this looks like a real gap. The MacTutor archive lists priority for individual results but does not aggregate "independent multiples per domain" as a metric. LMFDB / KnotInfo / Cremona are catalogs of *results*, not of *pathways to results*. This means the substrate cannot ground its rediscovery claims in a domain-specific empirical base; it has to assert the analogy.

**5. Falsification test.**

See dedicated section below.

## Concrete operational handles

From the literature, four handles transferable to the substrate:

- **Handle A (Dawson partition).** When the substrate hits a known result, classify the proof/trace by Dawson's purpose-categories (verification / generalization / simplification / structural). If the substrate's "rediscovery" traces almost always fall in the *verification* category, that is evidence that the pipeline is doing recognition, not discovery, and the same-loop claim weakens.

- **Handle B (Pathway diversity audit).** For a fixed catalog target, run the substrate from N independently-seeded entry points and measure how many *distinct primitive sequences* converge on the target. If diversity is high, the substrate is exhibiting the "Bolyai/Lobachevsky/Gauss" pattern (multiple structurally distinct routes), which is the strongest evidence for the same-loop claim. If diversity is near zero, the substrate is funnelling everything through one canonical recognizer.

- **Handle C (Hadamard/Selberg test).** Force the substrate to attempt a known result with a *deliberately restricted* primitive set (e.g., disallow the canonical strategy for Lehmer's problem). If it can still rediscover via a structurally different route, the loop is robust; if it cannot, calibration successes are likely strategy-bound, not loop-bound.

- **Handle D (Multiple-routes prior).** Use the historical observation that intersection-node theorems support more independent routes as a *priority signal* in the discovery queue: candidates whose neighborhoods in the substrate's conceptual graph have high cross-domain degree should be probed first, because they are most likely to admit alternative routes that the substrate can verify against itself.

## Falsification

The same-loop-different-oracle-state claim is falsified if any of the following hold:

1. **Trace divergence between hit and miss.** If a controlled experiment shows that pipelines that *hit* the catalog use a structurally different distribution of primitives/strategies than pipelines that *miss* (where "miss" includes both true negatives and unverified candidates), then rediscovery and discovery are not the same loop. Concretely: bootstrap the empirical distribution over primitive-sequence n-grams for hit-runs vs. miss-runs and apply a permutation test (the substrate already has feedback_permutation_null infrastructure for this).
2. **Restricted-primitive failure (Handle C).** If the substrate cannot rediscover known results when the canonical strategy is masked, the "loop" is actually a strategy-specific recognizer.
3. **Pathway monoculture (Handle B).** If diversity-of-route is near 1 across all catalog targets, then "rediscovery" is just "look-up with extra steps."
4. **Calibration / discovery rate decoupling.** If across versions of the substrate the calibration rate (catalog rediscovery) and the novel-candidate confirmation rate (those that pass external follow-up) move *independently*, that is direct evidence the two metrics measure different things.

The cleanest single test is (4), because it does not require introspecting traces and only needs longitudinal data the substrate is already producing.

## Open questions raised

- **OQ-04.1.** Is there a principled way to assign substrate traces to Dawson's purpose-categories automatically? The categories were designed for human-readable proofs and may not survive translation to primitive-sequence traces.
- **OQ-04.2.** What is the right denominator for "calibration rate"? The catalog covers what humans found; results not in the catalog include both genuine discoveries *and* genuine errors, and the substrate currently can't distinguish them without an external oracle.
- **OQ-04.3.** Does the historical pattern that intersection-node theorems admit more independent proofs survive when you control for theorem age and community size? If older / more-studied theorems just accumulate more proofs by virtue of attention, the "intersection node" claim degrades to a popularity artifact and Handle D weakens.
- **OQ-04.4.** Are there documented cases of human *mis*-rediscovery — independent derivations that converged on a result that turned out to be wrong? These would be the cleanest analog to substrate false positives and would let us calibrate the false-positive rate of the same-loop heuristic. The literature on this is thin (cf. retraction studies), and finding examples in pure mathematics is harder than in experimental sciences.
- **OQ-04.5.** The substrate's "catalog" is itself a moving target (LMFDB grows). Is "rediscovery" defined relative to a frozen catalog snapshot, or live? This is not a deep question but it has not been pinned down in the operational protocol that this study reviewed.

## Citations

Primary literature (verified via search to exist; full-text not re-read for this study):

- Merton, R. K. (1961). "Singletons and Multiples in Scientific Discovery: A Chapter in the Sociology of Science." *Proc. Amer. Phil. Soc.* 105(5): 470–486. Reprinted in Merton (1973), *The Sociology of Science: Theoretical and Empirical Investigations*, U. Chicago Press.
- Merton, R. K. (1963). "Resistance to the Systematic Study of Multiple Discoveries in Science." *Eur. J. Sociology* 4(2): 237–282.
- Ogburn, W. F. & Thomas, D. S. (1922). "Are Inventions Inevitable?" *Political Science Quarterly* 37: 83–98.
- Kroeber, A. L. (1917). "The Superorganic." *American Anthropologist* 19(2).
- Stigler, S. M. (1980). "Stigler's Law of Eponymy." *Trans. NY Acad. Sci.* 39: 147–158.
- Dawson, J. W. (2015). *Why Prove It Again? Alternative Proofs in Mathematical Practice*. Springer.
- Aigner, M. & Ziegler, G. M. (multiple eds., 1998–). *Proofs from THE BOOK*. Springer.
- Hadamard, J. (1896) and de la Vallée Poussin, C. (1896): independent proofs of PNT. Modern review: Zagier, D. (1997), "Newman's Short Proof of the Prime Number Theorem," *Amer. Math. Monthly* 104(8).
- Selberg, A. (1949) / Erdős, P. (1949): elementary proofs of PNT.
- Wos, L. (1988). *Automated Reasoning: 33 Basic Research Problems.* Prentice-Hall.

Secondary / web-sourced framings consulted:

- Wikipedia, "List of multiple discoveries"; "Stigler's law of eponymy"; "Leibniz–Newton calculus controversy"; "Hyperbolic geometry"; "Prime number theorem."
- MacTutor History of Mathematics, "Non-Euclidean geometry."
- Cambridge Core abstract: Merton (1963) "Resistance to the Systematic Study of Multiple Discoveries."

No citations were fabricated. Where I have not personally re-read a source within this study, the citation reflects what the search returned and standard bibliographic practice; the specific page-level claims above (e.g., Lobachevsky 1829 publication date, "1896" for Hadamard/de la Vallée Poussin) are corroborated across multiple secondary references rather than from a single source.

---

**Calibrated bottom line.** The historical literature on multiple independent discovery in mathematics gives *qualified* support to the substrate's same-loop claim at the level of *result-equivalence*, and *clearly does not support* it at the level of *trace-equivalence*. The most useful contribution this literature makes to Prometheus is not validation but a set of falsifiers (Handles A–D, falsification 1–4), most of which the substrate already has the instrumentation to run.
