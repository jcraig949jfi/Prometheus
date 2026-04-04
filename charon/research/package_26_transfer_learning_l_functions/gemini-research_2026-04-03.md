# Research Package 26: Transfer Learning Across Arithmetic Families

**Key Points:**
*   **Transfer Learning Success:** Recent research (Costa et al., 2025) demonstrates highly successful transfer learning (over 90% accuracy) between specific degree-4 $L$-function families (elliptic curves over number fields and genus 2 curves over $\mathbb{Q}$), but results for cross-degree transfers (degree-2 to degree-4) remain undocumented in the current literature.
*   **Optimal Representation:** Cross-family transfer relies heavily on mathematically rigorous feature scaling. Normalizing Dirichlet coefficients by their Hasse bounds ($a_p / (d p^{w/2})$) to map them into the $[-1, 1]$ interval is crucial for neural network generalization.
*   **Universal Signatures:** The "vanishing order" of a rational $L$-function leaves a universal, label-free geometric footprint in the early Dirichlet coefficients, detectable via Principal Component Analysis (PCA) across multiple $L$-function families, including degree-4 objects.
*   **Zero vs. Coefficient Approaches:** While coefficients encode specific arithmetic properties and have proven successful in recent ML models, an approach using $L$-function zeros offers a theoretical universality (governed by Random Matrix Theory). Empirical comparisons between zero-based and coefficient-based cross-family transfer learning remain an open frontier.
*   **Sequence Models (int2int):** François Charton’s `int2int` integer-sequence transformer successfully processes Dirichlet coefficients as tokens for within-family tasks (e.g., rank prediction, parity learning), but explicit cross-family transfer capabilities using this architecture have not yet been established.
*   **The Selberg Class:** While the Selberg class provides a unified axiomatic framework for $L$-functions, transfer learning "for free" breaks down due to differing motivic weights, degrees, and root analytic conductors, which require strict normalization to align feature spaces.

This report addresses the problem of transfer learning across arithmetic families, specifically within the context of building a unified $k$-NN search space where elliptic curves, modular forms, and higher-degree $L$-functions coexist. Grounded in recent literature, including the February 2025 release by Costa et al., the `int2int` transformer framework, and convolutional neural network models by Kazalicki and Vlah, this analysis evaluates the current empirical limits of cross-family generalization. It examines the nuances of feature representation, the universal hypothesis of vanishing orders, and the theoretical boundaries imposed by the Selberg class. 

---

## 1. Costa et al.'s Transfer Learning Results

In the recent paper *Machine learning the vanishing order of rational L-functions* (arXiv:2502.10360), Costa et al. investigated the vanishing order of rational $L$-functions using a dataset of 248,359 $L$-functions sourced from the LMFDB, known as the RAT dataset [cite: 1, 2]. This dataset comprises L-functions with a root analytic conductor of less than 4, purposefully chosen to balance the representations from different origins [cite: 1, 2]. 

The dataset is divided into several sub-datasets based on geometric and arithmetic origins: Classical Modular Forms (CMF), Elliptic Curves defined over Number Fields (ECNF), Dirichlet characters (DIR), Genus 2 curves defined over $\mathbb{Q}$ (G2Q), and Elliptic Curves over $\mathbb{Q}$ (ECQ) [cite: 1, 3]. 

### Specific Transfer Learning Accuracies
To evaluate transfer learning, the researchers explicitly trained models on one sub-dataset and evaluated them on another to test whether the learned representations captured something mathematically universal or something overly specific to a single family [cite: 1, 2].

*   **Train on ECNF (Elliptic Curves over Number Fields), Test on G2Q (Genus 2 Curves over $\mathbb{Q}$):** The researchers trained a convolutional neural network (CNN) on the ECNF subset and tested it on the G2Q subset. This transfer was highly successful, achieving an accuracy of over 90% on the test set [cite: 1].
*   **Train on G2Q, Test on ECNF:** Reversing the procedure, training on G2Q and testing on ECNF also yielded an accuracy of over 90% [cite: 1].
*   **Train on CMF, Test on HMF (Hilbert Modular Forms):** The paper does not provide explicit accuracy results for this specific transfer [cite: 1]. The study notes that HMF is a sub-dataset within ECNF, while CMF is a separate sub-dataset [cite: 1]. 
*   **Train on ECQ, Test on ECNF:** There are no results recorded in the document for the direct transfer from ECQ to ECNF [cite: 1].
*   **Train on Degree-2 L-functions, Test on Degree-4 L-functions:** This transfer was not addressed. The explicit transfer learning results provided in the paper are confined to the PRAT$^\star$ subset of the data [cite: 1]. The PRAT$^\star$ dataset exclusively contains $L$-functions with a degree of $d=4$ and a motivic weight of $w=1$ (which covers both ECNF and G2Q) [cite: 1, 3]. Therefore, cross-degree transfer learning (e.g., degree-2 ECQ to degree-4 G2Q) remains untested in this specific publication.

### Which Transfers Worked and Which Degraded?
The transfers between ECNF and G2Q worked exceptionally well. The authors attribute this high transferability to the strong structural similarity between $L$-functions that share the same motivic weight ($w=1$) and degree ($d=4$) [cite: 1]. Because the paper did not publish results outside of this specific degree/weight constraint, the data regarding "degraded" transfers is largely absent from the explicit findings [cite: 1]. However, the authors explicitly flagged predicting across different data subsets and varying conductor ranges as an area requiring further exploration, implying that transfers outside of strict degree/weight alignment would likely face degradation without further architectural interventions [cite: 1].

## 2. Feature Representation for Cross-Family Transfer

The choice of representation is the single most critical factor enabling cross-family transfer learning in the models deployed by Costa et al. They did not use raw Dirichlet coefficients ($a_p$), as raw coefficients scale differently depending on the mathematical origin, degree, and weight of the $L$-function [cite: 1]. 

### Normalization Mechanics
Machine learning algorithms, particularly distance-based models and neural networks, are highly sensitive to the scale of features. If an $L$-function with a higher motivic weight or degree produces exponentially larger coefficients, the neural network will overfit to the magnitude rather than the structural pattern (the murmuration) [cite: 1, 3]. 

To counter this, Costa et al. applied a specific normalization inspired by the Hasse bounds [cite: 1]. The feature vector $v(L)$ for a given $L$-function was constructed using the normalized Dirichlet coefficients $\overline{a}_p$ for primes $p \leq 1000$:
\[ v(L) = (\overline{a}_2, \overline{a}_3, \overline{a}_5, \dots, \overline{a}_{997}) \in \mathbb{R}^{168} \]
[cite: 1]

The normalization formula used is:
\[ \overline{a}_p = \frac{a_p}{d \cdot p^{w/2}} \]
where $a_p$ is the raw Dirichlet coefficient in the arithmetic normalization, $d$ is the degree of the $L$-function, and $w$ is its motivic weight [cite: 1]. 

### Impact on Transfer Success
This specific representation forces all coefficients into the interval $[-1, 1]$, entirely neutralizing the magnitude discrepancies between different $L$-function families [cite: 1]. By factoring out the degree and the weight, the neural network is forced to learn the underlying oscillating "murmuration" patterns rather than relying on trivial magnitude scaling [cite: 2, 3]. 

The success of this representation is stark: when using this normalized feature vector, the Convolutional Neural Network achieved over 95% classification accuracy across the dataset [cite: 1]. By contrast, using only the first two principal components of the data yielded a lower overall accuracy of 91% [cite: 1]. The normalization reflects the "arithmetic nature" of the functions and proves that proper feature scaling is a prerequisite for any unified cross-family architecture [cite: 1].

## 3. The "Universal Vanishing Order" Hypothesis

The Birch and Swinnerton-Dyer (BSD) conjecture famously predicts that the algebraic rank of an elliptic curve (or an abelian variety) is equal to the vanishing order of its $L$-function at the central point [cite: 2]. Costa et al.'s findings suggest that this vanishing order leaves a detectable, universal geometric footprint in the earliest Dirichlet coefficients [cite: 2]. 

### Universality Across Degrees and Families
The hypothesis of universality holds considerable empirical weight. The researchers discovered "murmuration-like" signatures (coherent oscillating patterns in the averages of coefficients) across all five sub-datasets: ECQ, ECNF, CMF, DIR, and G2Q [cite: 2, 3]. This proves that the phenomenon extends far beyond degree-2 elliptic curves over $\mathbb{Q}$, where murmurations were originally discovered in 2022 [cite: 2]. 

Crucially, this universality extends explicitly to degree-4 $L$-functions, encompassing both ECNF and G2Q (genus 2 curves) [cite: 2, 3]. 

### Label-Free Clustering
To test how universal this footprint is, the team utilized Principal Component Analysis (PCA) to project the 168-dimensional coefficient vectors down to two dimensions. The PCA naturally clustered the rational $L$-functions strictly by their vanishing order (rank 0, rank 1, rank 2) *without requiring any labels* [cite: 2]. The geometry of the normalized coefficient space itself naturally separates the mathematical objects by their rank, regardless of whether the source geometry is an elliptic curve or a genus 2 curve [cite: 2]. 

This provides strong empirical evidence that the analytic rank acts as a universal governor of the early Dirichlet coefficients, operating identically across structurally distinct geometric origins [cite: 2].

## 4. Zero-Based Transfer vs. Coefficient-Based Transfer

Your architecture proposes building a unified search space using the *zeros* of $L$-functions, whereas the recent breakthroughs by Costa, Kazalicki, and Vlah predominantly rely on Dirichlet *coefficients* [cite: 2, 4].

### The Theoretical Divide
There is currently a gap in the literature regarding direct, empirical comparisons between zero-based and coefficient-based machine learning for cross-family transfer. However, the theoretical distinctions are well understood:
*   **Zero-Based Universality:** The non-trivial zeros of $L$-functions, particularly their local spacing and distributions, are theorized to be governed by Random Matrix Theory (RMT) (the Katz-Sarnak philosophy) [cite: 5, 6]. Because zeros high up on the critical line adhere to universal statistical distributions dependent only on the symmetry type of the family, representations based on zeros are highly universal. However, this extreme universality may strip away the specific "arithmetic" identity of the object. Machine learning models have been applied to predict Riemann zeta zeros [cite: 7], but using them as features for cross-family transfer learning of arithmetic invariants (like rank) is largely untested in a comparative setting.
*   **Coefficient-Based Arithmetic Identity:** Dirichlet coefficients encode the precise local arithmetic of the geometric object (e.g., the number of points over finite fields $\mathbb{F}_p$) [cite: 4]. Studies like Kazalicki and Vlah (2022) use sequences of normalized $a_p$ values ($p < 10^k$) to train CNNs, outperforming traditional heuristics like Mestre-Nagao sums for rank prediction [cite: 4, 8]. Coefficients retain the "fingerprint" of the specific curve [cite: 2].

### Architectural Implications
If zeros are used as the feature space, transfer learning across families might be trivialized because the distributions (e.g., GUE) converge universally, but the model may lose the capacity to accurately classify low-level arithmetic invariants unless it focuses strictly on the low-lying zeros near the central point (which are sensitive to rank). Coefficients, conversely, require the strict normalization techniques proposed by Costa et al. (dividing by $d p^{w/2}$) to prevent magnitude disparities from breaking the transfer [cite: 1]. 

Ultimately, coefficients have a proven track record of $>90\%$ accuracy in transfer learning between degree-4 families [cite: 1], while zero-based transfer remains theoretically promising but empirically unverified in deep learning contexts.

## 5. Charton's `int2int` Transformer

François Charton developed the `int2int` framework, an open-source PyTorch implementation of an encoder-only sequence-to-sequence transformer specifically optimized for mathematical problems involving integers [cite: 9, 10]. In this framework, inputs are treated as sequences of digits (often in specific bases), and mathematical objects like Dirichlet coefficients or elliptic curve parameters are tokenized (e.g., tokenizing a sign followed by an absolute value) [cite: 10, 11].

### `int2int` Performance on $L$-functions
During the CMSA program at Harvard (Fall 2024), `int2int` was deployed to analyze $L$-functions and Dirichlet sequences [cite: 12]. 
*   **Möbius Function and Parity:** The model was tested on predicting the Möbius function and the parity of Frobenius traces ($a_p \pmod 2$). Given traces $\{a_q\}_{q \neq p, q < 100}$, the transformer was able to predict $a_p \pmod 2$ with accuracies close to 94% for most primes [cite: 11]. 
*   **Elliptic Curve Rank Prediction:** `int2int` was tasked with predicting the rank of an elliptic curve given its five parameters. After 100 epochs, the transformer achieved a 49.9% overall accuracy. It showed strength in predicting rank-1 curves (88.7% accuracy) but performed poorly on rank-0 curves (14.6% accuracy) and rank-2 curves (4.1% accuracy) [cite: 10]. 

### Cross-Family Testing
Based on the current available literature and repository documentation, explicit **cross-family prediction** (e.g., training the transformer on modular forms and testing on genus-2 curves) has not been rigorously documented or benchmarked using the `int2int` architecture [cite: 9, 13]. The `int2int` package excelling at sequence translation tasks within a defined mathematical context, but its capacity to act as a foundation model that transfers latent representations across disparate arithmetic families remains an open research question.

## 6. The Selberg Class as a Unifying Framework

The Selberg class provides an axiomatic framework that unites diverse $L$-functions—including the Riemann zeta function, Dirichlet $L$-functions, and $L$-functions associated with automorphic forms and elliptic curves [cite: 14]. Functions in the Selberg class must satisfy four axioms: the Ramanujan hypothesis (bounded coefficients), analytic continuation, a functional equation, and an Euler product [cite: 14].

### Why Transfer Learning Isn't "For Free"
Given this unifying structure, one might assume that once an $L$-function's degree ($d$) and conductor are normalized, a neural network should inherently generalize across the entire class. However, several mathematical barriers break this "free" transfer:

1.  **Motivic Weight ($w$):** As demonstrated by Costa et al., $L$-functions have varying motivic weights. The weight dictates the growth rate of the coefficients (by Hasse's theorem, $|a_p| \leq d p^{w/2}$) [cite: 1, 15]. If a network is trained on a weight-0 family and tested on a weight-1 family without explicit normalization (mapping to $[-1, 1]$), the raw numerical variance will destroy the network's gradient stability and feature alignment [cite: 1].
2.  **Degree Discrepancies ($d$):** The degree influences the number of Euler factors and the complexity of the local polynomials at prime $p$. A degree-2 Euler product behaves fundamentally differently in its early sequence variations than a degree-4 product. Costa et al. only reported successful transfer learning between families of the *same* degree ($d=4$) [cite: 1]. 
3.  **The $\Gamma$-Factors:** The functional equation in the Selberg class involves $\Gamma$-factors that depend on specific parameters ($\omega_i$ and $\mu_i$). The root analytic conductor normalizes the overarching exponential growth, but the specific archimedean components create subtle structural differences in the analytic landscape of the functions [cite: 3]. 
4.  **Conductor Ranges:** Costa et al. noted that the success of the classifiers depends heavily on the conductor range [cite: 1]. If a model is trained on $L$-functions with minimal conductor ranges, it is currently unknown how effectively it can transfer to data with vastly larger root analytic conductors, as the density and onset of murmurations shift dynamically with conductor size [cite: 1, 3].

## Conclusion for Architecture Design

To build a unified $k$-NN search space across arithmetic families, your architecture must account for the strict scaling laws dictating these mathematical objects.

If pursuing a **coefficient-based architecture**, you must aggressively normalize the features, adapting Costa et al.'s formula $\overline{a}_p = a_p / (d p^{w/2})$ to guarantee that the search space distance metrics (like Euclidean distance or Cosine similarity in a $k$-NN) are not skewed by weight and degree magnitudes [cite: 1]. Transfer between families of the same degree (e.g., ECNF and G2Q) is highly achievable (>90%), but you must prepare for potential architectural degradation when spanning across degrees (e.g., degree-2 to degree-4).

If pursuing a **zero-based architecture**, you gain the theoretical advantage of Random Matrix Theory universality, sidestepping the issues of coefficient magnitude growth. However, because zeros shed specific arithmetic identity in favor of universal symmetries, your $k$-NN space may struggle to separate fine-grained arithmetic invariants (like rank and parity) without focusing intensely on the lowest-lying zeros near the central point. Comparing the empirical viability of zeros against properly normalized coefficients in a cross-family transformer setting remains a high-value, unsolved target for your research agenda.

**Sources:**
1. [https://arxiv.org/html/2502.10360v1](https://arxiv.org/html/2502.10360v1)
2. [https://research.iaifi.org/posts/machine-learning-the-vanishing-order-of-rational-l-functions](https://research.iaifi.org/posts/machine-learning-the-vanishing-order-of-rational-l-functions)
3. [https://arxiv.org/pdf/2502.10360](https://arxiv.org/pdf/2502.10360)
4. [https://arxiv.org/pdf/2207.06699](https://arxiv.org/pdf/2207.06699)
5. [https://digitalcommons.lib.uconn.edu/context/usp_projects/article/1103/viewcontent/UConn_Thesis_Submission.pdf](https://digitalcommons.lib.uconn.edu/context/usp_projects/article/1103/viewcontent/UConn_Thesis_Submission.pdf)
6. [https://www.emergentmind.com/topics/l-zero-l0](https://www.emergentmind.com/topics/l-zero-l0)
7. [https://sites.google.com/site/riemannzetazeros/machinelearning](https://sites.google.com/site/riemannzetazeros/machinelearning)
8. [https://arxiv.org/abs/2207.06699](https://arxiv.org/abs/2207.06699)
9. [https://arxiv.org/html/2502.17513v2](https://arxiv.org/html/2502.17513v2)
10. [https://arxiv.org/pdf/2502.17513](https://arxiv.org/pdf/2502.17513)
11. [https://arxiv.org/pdf/2502.10357](https://arxiv.org/pdf/2502.10357)
12. [https://cmsa.fas.harvard.edu/media/2024-2025-CMSA-Newsletter-Electronic.pdf](https://cmsa.fas.harvard.edu/media/2024-2025-CMSA-Newsletter-Electronic.pdf)
13. [https://arxiv.org/html/2511.10811v1](https://arxiv.org/html/2511.10811v1)
14. [https://www.mdpi.com/2227-7390/11/3/737](https://www.mdpi.com/2227-7390/11/3/737)
15. [https://www.scribd.com/document/978161395/2502-10360v1](https://www.scribd.com/document/978161395/2502-10360v1)
