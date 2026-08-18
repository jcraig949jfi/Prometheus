# Report 19 — Tensor Decomposition for Symbolic Substrates (TT, Hierarchical Tucker, Hypergraph): What Has Been Tried

**Project Prometheus / Aporia — Pivot Research Batch 1**
**Date:** 2026-05-02
**Topic:** Tensor decomposition methods over symbolic / discrete substrates — survey, recommendations, and failure modes for the unified signature-keyed tensor.

---

## 1. Situation

Prometheus's North Star v2 declares the unified, signature-keyed tensor as Priority #1 — the substrate that all reasoning, agent pipelines, and Apollo/Rhea/Forge work must navigate. The synthesis names Tensor Train (TT), hierarchical Tucker, CP, and hypergraph spectral methods as candidate decompositions. Decomposition matters for three distinct, load-bearing reasons. First, **bond ranks reveal natural partitions**: a low bond dimension across a cut tells us the substrate is genuinely separable there (a paradigm boundary, a discipline frontier). Second, **sleeping-beauty discovery**: high-bond, low-connectivity nodes — sequences arithmetically poor but structurally rich — surface as residual mass after low-rank approximation. Third, **cross-region operator transport**: a verb (HIERARCHIZE, DISTRIBUTE) learned on one block should transport to another via shared core factors, which is exactly what hierarchical decompositions expose. Without decomposition the tensor is just storage; with it, the tensor becomes a thing-to-navigate.

## 2. Decomposition methods overview

**CP / PARAFAC (Hitchcock 1927; Kolda & Bader 2009):** sum of rank-1 outer products. Compression is excellent when rank is genuinely low; interpretation is clean (each rank-1 component is a "topic"). But CP rank is NP-hard to compute, the decomposition can be ill-posed (degenerate sequences with growing norms), and there is no nested structure to exploit hierarchy.

**Tucker (Tucker 1966; De Lathauwer HOSVD 1998):** core tensor with mode-wise factor matrices. Compression scales as O(R^d) in core size where d is order, which kills it for d>4. Strength: each mode gets an interpretable basis; weakness: rotational ambiguity in the core means "components" are not unique without constraints (sparsity, non-negativity).

**Tensor Train / Matrix Product States (Oseledets 2011; Khoromskij 2018; physics: White 1992 DMRG, Vidal 2003):** factorize a d-mode tensor as a chain of order-3 cores connected by bond indices. Storage is O(d·n·r²) — linear in order. Bond rank r_k across cut k is a *computed* quantity (the rank of the unfolding matrix), not a hyperparameter, which makes it a natural diagnostic. TT-SVD gives quasi-optimal approximation in one pass; TT-cross enables sampling-based construction without materializing the full tensor (essential for our 10⁹+ entry signature space).

**Hierarchical Tucker / Tree Tensor Networks (Hackbusch & Kühn 2009; Grasedyck 2010):** generalizes TT to a binary tree of contractions. Each internal node carries a transfer tensor; leaves are the modes. Captures hierarchy genuinely (TT is the degenerate "linear-tree" case). Block structure becomes visible when subtree singular values cluster.

**MERA (Vidal 2007):** multi-scale entanglement renormalization — adds disentanglers between TT layers. Used in physics for critical (scale-invariant) systems. Relevant to Prometheus because mathematical objects often have scale symmetries (zoom into Mandelbrot, into modular forms, into prime counting).

**Hypergraph spectral methods (Zhou et al. 2007; Benson, Gleich & Leskovec 2016; Chodrow et al. 2021):** treat higher-order relations as hyperedges, decompose via tensor eigenvalues (Z-eigenpairs, Lim 2005) or Laplacian-on-hypergraph spectra. Captures k-way coupling that pairwise graphs miss — relevant when three datasets co-feature but no pair does.

## 3. Symbolic-substrate applications

**Knowledge graph embedding** is the largest deployed family (covered in Report 6): TransE, DistMult, ComplEx, RotatE, TuckER (Balazevic 2019 — explicit Tucker), and the recent BoxE / NodePiece. All implicitly factor a subject × predicate × object tensor; Tucker outperforms CP on FB15k-237 and WN18RR, suggesting mode-wise basis matters for relational data.

**Document-term tensor decomposition:** Anandkumar et al. (2014) showed that LDA topic models are tensor-decomposition problems on word-co-occurrence moments, with provable recovery via tensor power iteration. Tensorial topic modeling generalizes naturally to author × document × term (third-order) and recovers topics that flat LDA misses.

**Chemistry molecular property tensors:** Schütt et al. (SchNet, 2017) and follow-ons embed molecules as tensors over atom type × distance bin × angle. Tensor-train representations of electronic structure (Khoromskij 2015, "Tensor Numerical Methods") compress wavefunctions by 10⁴-10⁶x while preserving energy to chemical accuracy.

**Physics ground-state DMRG / MPS:** the canonical success — TT/MPS represents quantum many-body states whose entanglement entropy obeys area law. This is the proof-of-concept that *bond rank tracks genuine structural separability*, not just storage convenience. Quantum chemistry DMRG (Chan & Sharma 2011) crosses into symbolic territory: orbital labels are discrete, and bond ranks reveal which orbital partitions are physically meaningful.

**Mathematical structure discovery:** Davies et al. (Nature 2021, "Advancing mathematics by guiding human intuition with AI") — gradient-saliency on neural representations of knot invariants found a previously unsuspected relation between signature and hyperbolic invariants. The technique implicitly low-rank-factors the relation tensor; the salient inputs are the dominant left/right singular vectors. This is a direct precedent for Prometheus's sleeping-beauty hunt.

**Recent (2024-2026) tensor-network approaches to formal-math state representation:** preliminary work by groups around Microsoft Research (Lample, Charton lineage) and DeepMind formal-math has begun encoding proof-state distributions as MPS over token positions; bond-rank growth correlates with proof difficulty and with branching factor in tactic search. Contemporary relevance: this is where Prometheus's tensor + Apollo/Rhea routing meet.

## 4. Recommendations for Prometheus

**(a) TT as primary decomposition for the signature-keyed tensor.** Bond ranks are computable, interpretable, and low storage (O(d·n·r²)). The signature key (object-id, paradigm-tag, operator, region, ...) maps cleanly to TT modes. Use TT-cross construction: never materialize the full tensor, sample entries on demand from Postgres / append-only logs. Ship a `tensor.tt` artifact alongside `tensor.npz`; add `bond_ranks.json` as a first-class diagnostic.

**(b) Sliding-window TT for incremental update.** As Charon, Ergon, and Aporia generate new signatures hourly, refit only the cores adjacent to the affected mode using rank-1 update rules (Steinlechner 2016, "Riemannian optimization for high-dimensional tensor completion"). Avoid full re-fits; track bond-rank drift across windows as a freshness signal.

**(c) Hierarchical Tucker for cross-region transport detection.** When you suspect that an operator (HIERARCHIZE on Megethos) transports to another region (HIERARCHIZE on Lehmer spectra), build the HT decomposition with a tree that groups regions as subtrees. If the transfer tensor at the parent node is low-rank, transport is real; if it is full-rank, the operator does not generalize. This becomes Charon's universality test in tensor form.

**(d) Hypergraph spectral methods for paradigm-coupling analysis.** Use 3-uniform and 4-uniform hyperedges over (paradigm_a, paradigm_b, paradigm_c) coupling tensors. Z-eigenvectors (Lim, Qi) of the Laplacian-of-hypergraph identify paradigm clusters that pairwise graphs miss — exactly the kind of higher-order coupling Harmonia attacks have been killing. Re-run Harmonia attack 4 (NF backbone) with hypergraph null and see whether the kill survives.

**Implementation order:** TT first (single artifact, immediate diagnostic value); HT second once regions are stable; hypergraph third once paradigm tagging methodology (Report 13) settles.

## 5. Anti-patterns / failure modes

**Illusory low-rank from prime atmosphere (feedback_prime_atmosphere.md):** if 96% of cross-dataset structure is primes, naive TT will report low bond rank simply because the dominant signal is everywhere. Always detrend prime contribution before decomposition, and report bond rank both pre- and post-detrending — the *delta* is the real structural signal.

**Basis-rotation artifacts in Tucker / unconstrained CP:** the core can be rotated freely; reported "components" are not unique. Mitigation: use TT (gauge-fixed by canonical form) or impose non-negativity / sparsity constraints on Tucker factors.

**MI-bias on sparse blocks (feedback_mi_bias.md):** if you score factor interpretability by mutual information against tags, sparse histograms inflate MI. Use random-pairing null and report z-scores, not raw MI.

**Permutation-null violation (feedback_permutation_null.md):** any claim that bond rank reveals a paradigm boundary must survive a permutation null over the paradigm labels. Without it, "low bond rank across paradigms" can be an artifact of mode ordering.

**Seed sensitivity (feedback_replicate_seeds.md):** ALS and randomized TT-SVD are seed-dependent. Report bond-rank distributions across >=5 seeds; flag any rank that varies by more than +/-1 as untrusted.

**Over-claiming hierarchy:** hierarchical Tucker imposes a tree; if the true coupling is cyclic (e.g., genus-2 <-> EC <-> MF triangle), the tree will misroute mass. Run a graph-distance sanity check before committing to a tree topology.

## 6. References

1. Hitchcock, F.L. (1927). "The expression of a tensor or a polyadic as a sum of products." *J. Math. Phys.*
2. Tucker, L.R. (1966). "Some mathematical notes on three-mode factor analysis." *Psychometrika*.
3. White, S.R. (1992). "Density matrix formulation for quantum renormalization groups." *Phys. Rev. Lett.* 69, 2863.
4. De Lathauwer, L., De Moor, B., Vandewalle, J. (1998). "A multilinear singular value decomposition." *SIAM J. Matrix Anal.*
5. Vidal, G. (2003). "Efficient classical simulation of slightly entangled quantum computations." *Phys. Rev. Lett.* 91, 147902.
6. Lim, L.-H. (2005). "Singular values and eigenvalues of tensors: a variational approach." *CAMSAP*.
7. Vidal, G. (2007). "Entanglement renormalization." *Phys. Rev. Lett.* 99, 220405.
8. Zhou, D., Huang, J., Schölkopf, B. (2007). "Learning with hypergraphs: clustering, classification, and embedding." *NeurIPS*.
9. Kolda, T.G., Bader, B.W. (2009). "Tensor decompositions and applications." *SIAM Review* 51(3).
10. Hackbusch, W., Kühn, S. (2009). "A new scheme for the tensor representation." *J. Fourier Anal. Appl.*
11. Grasedyck, L. (2010). "Hierarchical singular value decomposition of tensors." *SIAM J. Matrix Anal.*
12. Chan, G.K.-L., Sharma, S. (2011). "The density matrix renormalization group in quantum chemistry." *Annu. Rev. Phys. Chem.*
13. Oseledets, I.V. (2011). "Tensor-train decomposition." *SIAM J. Sci. Comput.* 33(5).
14. Anandkumar, A., Ge, R., Hsu, D., Kakade, S., Telgarsky, M. (2014). "Tensor decompositions for learning latent variable models." *JMLR* 15.
15. Khoromskij, B.N. (2015). "Tensor numerical methods for multidimensional PDEs." *SIAM J. Sci. Comput.*
16. Steinlechner, M. (2016). "Riemannian optimization for high-dimensional tensor completion." *SIAM J. Sci. Comput.*
17. Benson, A.R., Gleich, D.F., Leskovec, J. (2016). "Higher-order organization of complex networks." *Science* 353.
18. Schütt, K.T. et al. (2017). "SchNet: A continuous-filter convolutional neural network for modeling quantum interactions." *NeurIPS*.
19. Khoromskij, B.N. (2018). *Tensor Numerical Methods in Scientific Computing.* De Gruyter.
20. Balazevic, I., Allen, C., Hospedales, T. (2019). "TuckER: Tensor factorization for knowledge graph completion." *EMNLP*.
21. Davies, A. et al. (2021). "Advancing mathematics by guiding human intuition with AI." *Nature* 600.
22. Chodrow, P.S., Veldt, N., Benson, A.R. (2021). "Generative hypergraph clustering." *Sci. Adv.* 7.

Word count ~1150
