# GL(2) Maass form L-function root numbers (analytic + ML-predicted partition)

**Pythia queue id:** 136
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdBaXdQYXNTMkpQMlZqTWNQd2M2RDRBaxIXQWl3UGFzUzJKUDJWak1jUHdjNkQ0QWs
**Elapsed:** 310s
**Completed at:** 2026-05-21T16:05:14.057347+00:00

---

# GL(2) Maass Form L-Function Root Numbers: Analytic Trace Formulas and Machine Learning-Predicted Partitions

**Key Points:**
* Research establishes that the Fourier coefficients of GL(2) Maass forms exhibit subtle, oscillatory statistical correlations with their global Fricke signs and root numbers—a phenomenon widely referred to in contemporary number theory as "murmurations."
* Machine Learning (ML) techniques have acted as a powerful one-sided oracle in arithmetic geometry, successfully predicting the Fricke signs (and consequently, the root number partitions) of Maass forms with accuracy exceeding 94–96%, utilizing architectures ranging from Linear Discriminant Analysis (LDA) to deep neural networks.
* Analytic proofs of these murmurations for Maass forms, particularly in the eigenvalue aspect, rely profoundly on explicit trace formulas, such as the Selberg trace formula and the Kuznetsov trace formula, linking spectral data to geometric conjugacy classes.
* The ML-predicted partition of L-function root numbers strongly aligns with heuristic estimates derived from Hejhal's algorithm, establishing a robust, data-scientific pathway for classifying the substantial portion of the L-functions and Modular Forms Database (LMFDB) that currently lacks rigorously computed Fricke signs.

---

## 1. Introduction to GL(2) Maass Forms and Automorphic L-Functions

The study of automorphic forms on $\text{GL}(2)$ represents a cornerstone of modern analytic number theory and the broader Langlands program. While classical holomorphic modular forms have been extensively studied due to their rich algebraic geometry and connections to elliptic curves, their non-holomorphic counterparts—Maass forms—present profound analytic complexities. Introduced by Hans Maass in 1949, a weight zero Maass cusp form $f$ on the upper half-plane $\mathbb{H} = \{z = x + iy \in \mathbb{C} : y > 0\}$ is a smooth, square-integrable function that is invariant under the action of a congruence subgroup, such as $\Gamma_0(N) \subset \text{SL}(2, \mathbb{Z})$, and is an eigenfunction of the hyperbolic Laplace-Beltrami operator [cite: 1, 2]. 

### 1.1. The Hyperbolic Laplacian and Fourier Expansions
The hyperbolic Laplacian is defined as $\Delta = -y^2 \left( \frac{\partial^2}{\partial x^2} + \frac{\partial^2}{\partial y^2} \right)$ [cite: 1, 3]. For a Maass cusp form $f$, the eigenvalue equation is given by $\Delta f = \lambda f$, where the eigenvalue is canonically parameterized as $\lambda = \frac{1}{4} + R^2$, with $R \in \mathbb{R}$ representing the spectral parameter [cite: 1, 4]. Because Maass forms are not holomorphic, their Fourier expansions do not rely on simple exponential functions $e^{2\pi i n z}$. Instead, they require specialized solutions to second-order differential equations, specifically the Whittaker functions or modified Bessel functions of the second kind, denoted $K_{iR}(y)$ [cite: 1, 2]. 

A normalized Hecke-Maass cusp form has a Fourier expansion at the cusp $\infty$ of the form:
\[ f(z) = \sum_{n \neq 0} a_n \sqrt{y} K_{iR}(2\pi |n| y) e^{2\pi i n x} \]
where $a_n$ are the Fourier coefficients [cite: 4]. These forms can be classified by their symmetry under the orientation-reversing involution $z \mapsto -\bar{z}$. A Maass form is considered *even* (parity $\sigma(f) = 0$) if $f(-\bar{z}) = f(z)$, and *odd* (parity $\sigma(f) = 1$) if $f(-\bar{z}) = -f(z)$ [cite: 2, 4]. The parity fundamentally dictates the trigonometric behavior of the Fourier expansion, reducing the exponential term to a cosine series for even forms and a sine series for odd forms [cite: 4].

### 1.2. The Fricke Involution and the Fricke Sign
Beyond the standard modular transformations dictated by $\Gamma_0(N)$, the space of Maass forms is acted upon by the Fricke involution, defined by the transformation matrix $W_N = \begin{pmatrix} 0 & -1 \\ N & 0 \end{pmatrix}$. This transformation sends $z \mapsto \frac{-1}{Nz}$. Because the Fricke involution normalizes $\Gamma_0(N)$ and commutes with the Laplacian and the Hecke operators, a Hecke-Maass newform $f$ is also an eigenfunction of $W_N$ [cite: 2, 5]. 

Thus, we obtain the relation:
\[ f\left(\frac{-1}{Nz}\right) = w_N f(z) \]
where $w_N \in \{+1, -1\}$ is defined as the Fricke sign (or Atkin-Lehner eigenvalue at the full level) [cite: 2, 4, 5]. The Fricke sign is deeply intertwined with the arithmetic properties of the form at the primes $p$ dividing the level $N$. Specifically, the Fricke sign can be decomposed as a product over prime divisors $w_N = \prod_{p|N} w_p$, where $w_p \in \{\pm 1\}$. Furthermore, for these bad primes, the Fourier coefficient is directly determined by the local Fricke sign: $a_p = -w_p / \sqrt{p}$ [cite: 2, 5]. Consequently, if the Fricke sign is unknown, the Fourier coefficients at primes dividing the level are also fundamentally unknown [cite: 5].

## 2. Automorphic L-Functions and Root Numbers

The arithmetic data of a Maass form is cleanly packaged into an associated Dirichlet series, known as its $L$-function. 

### 2.1. The Dirichlet Series and Completed L-Function
For a normalized Hecke-Maass newform $f$, the standard $L$-function is defined in the half-plane of absolute convergence ($\text{Re}(s) > 1$) by:
\[ L(s, f) = \sum_{n=1}^\infty a_n n^{-s} \]
Like the Riemann zeta function, this Dirichlet series can be analytically continued to a meromorphic function on the entire complex plane. To achieve a functional equation, one must append appropriate local factors at the Archimedean place (the "infinite" prime), leading to the completed $L$-function $\Lambda(s, f)$ [cite: 4]. 

For a Maass form of level $N$, parity $\sigma(f)$, and spectral parameter $R$, the completed $L$-function incorporates the Gamma function $\Gamma(s)$ and takes the form:
\[ \Lambda(s, f) = \left( \frac{N}{\pi} \right)^{s/2} \Gamma\left( \frac{s + \sigma(f) + iR}{2} \right) \Gamma\left( \frac{s + \sigma(f) - iR}{2} \right) L(s, f) \]
[cite: 2, 4]. 

### 2.2. The Functional Equation and the Root Number
The completed $L$-function satisfies a symmetric functional equation relating its value at $s$ to its value at $1-s$:
\[ \Lambda(s, f) = \epsilon \bar{\Lambda}(1 - s, f) \]
where $\epsilon$ is a complex number of modulus 1 known as the global root number [cite: 2, 5]. For self-dual $\text{GL}(2)$ Maass forms with real coefficients, the root number is strictly restricted to $\epsilon \in \{+1, -1\}$ [cite: 5, 6, 7]. 

Crucially, the global root number $\epsilon$ is explicitly determined by the form's parity $\sigma(f)$ and its Fricke sign $w_N$. The exact relationship is given by:
\[ \epsilon = (-1)^{\sigma(f)} w_N \]
[cite: 2, 4]. This equation highlights why the Fricke sign is of paramount importance: it dictates the sign of the functional equation. If $\epsilon = -1$, the completed $L$-function is forced by parity to vanish at the central critical point $s = 1/2$, resulting in an odd order of vanishing (analytic rank $\ge 1$). Conversely, if $\epsilon = +1$, the order of vanishing is even (often analytic rank 0) [cite: 5, 8]. Computing the root number—and therefore identifying the partition of the dataset into forms with $\epsilon = +1$ versus $\epsilon = -1$—is a highly non-trivial computational task that has motivated significant recent research [cite: 4, 9, 10].

## 3. The Murmuration Phenomenon in Arithmetic Geometry

A profound breakthrough in understanding the subtle statistical behaviors of $L$-functions occurred in 2022 with the discovery of "murmurations." 

### 3.1. Genesis in Elliptic Curves
The phenomenon was first observed by He, Lee, Oliver, and Pozdnyakov during a machine learning investigation of the Hasse-Weil $L$-functions of elliptic curves over $\mathbb{Q}$ [cite: 11, 12]. By training neural networks to predict whether an elliptic curve possessed finite or infinite rational solutions (i.e., predicting the algebraic rank as 0 or 1, which correlates with the root number via the Birch and Swinnerton-Dyer conjecture), the researchers analyzed the learned weights. They discovered an unexpected, striking oscillatory pattern in the average values of the Frobenius traces $a_p(E) = p + 1 - \#E(\mathbb{F}_p)$ when averaged over families of elliptic curves sorted by their root number and plotted against primes scaled by the conductor $N$ [cite: 7, 11, 13, 14].

When these moving averages were visualized, the curves generated sweeping, wave-like shapes. The authors coined the term "murmurations"—borrowing from the biological term for the coordinated, fluid flight patterns of flocks of starlings—due to the chaotic yet highly structured visual nature of the plots [cite: 12, 14].

### 3.2. Generalization to Broader $L$-Functions
Subsequent experimental work by Sutherland and others rapidly confirmed that murmurations were not unique to elliptic curves [cite: 12, 13]. The phenomenon was found to be a universal feature of Dirichlet coefficients across a vast array of arithmetic $L$-functions, provided the data was partitioned by the global root number. Whether examining primitive quadratic Dirichlet characters, weight $k$ holomorphic modular newforms, or higher-degree $L$-functions arising from genus $g$ curves, moving averages of the coefficients $a_p$ consistently revealed structured oscillations when split by $\epsilon = \pm 1$ [cite: 6, 8, 15].

This indicated that the Fourier coefficients at small primes intrinsically "know" about the global root number of the $L$-function. The partition of an arithmetic dataset by root number leaves a distinct, measurable statistical footprint across the sequence of Dirichlet coefficients.

## 4. Murmurations of Maass Forms: Analytic Framework

While initially observed empirically via computational data science, the mathematical community quickly mobilized to provide rigorous analytic proofs for the murmuration phenomenon using explicit trace formulas.

### 4.1. The Eigenvalue Aspect for Maass Forms
In 2024, a collaboration by Bober, Booker, Lee, Lowry-Duda, Seymour-Howell, and Zubrilina successfully proved the existence of murmurations for $\text{GL}(2)$ Maass forms [cite: 16, 17]. Specifically, they investigated the family of weight 0, level 1 Maass forms, focusing on the eigenvalue aspect (letting the Laplace spectral parameter $R \to \infty$) [cite: 14, 16]. In this regime, the analytic conductor of the form grows in proportion to $R^2$, and the primes $p$ are scaled relative to this analytic conductor [cite: 16, 18].

The team proved that if one takes a short interval in the spectral parameter $|R - K| \le H$ (where $K \to \infty$ and $H$ is a carefully chosen window size), and averages the Hecke eigenvalues $\lambda_f(p)$ over primes $p$ proportional to the analytic conductor, a strong bias emerges that perfectly correlates with the parity (and thus the root number) of the forms [cite: 18]. 

### 4.2. Asymptotic Behavior and the Murmuration Density Function
Under the assumption of the Generalized Riemann Hypothesis (GRH) for Maass cusp forms, the researchers derived a murmuration density function [cite: 14, 18]. The analytic results demonstrated that on arbitrarily small intervals of scaled primes, the murmuration function behaves remarkably like a series of Kronecker delta functions centered at specific rational values [cite: 18].

Specifically, the effect of the spectral measure implies that for primes $p$ located very close to the analytic conductor $N \approx (K/4\pi)^2$, there is an overwhelming bias in the values of the coefficients towards the root number. The theoretical limit results in a highly oscillatory density function that mathematically perfectly matches the "flock of birds" plots observed in the empirical machine learning data [cite: 18].

## 5. Analytic Trace Formulas as the Theoretical Engine

The rigorous proofs of murmurations are deeply reliant on trace formulas. Trace formulas act as profound dictionaries in number theory, equating a spectral sum (over automorphic forms or eigenvalues) with a geometric sum (over conjugacy classes or lengths of closed geodesics) [cite: 14, 19].

### 5.1. The Selberg and Strömbergsson Trace Formulas
For Maass forms, the primary tool utilized by Seymour-Howell et al. was an explicit version of the Selberg trace formula developed by Strömbergsson [cite: 14, 19]. The methodology involves selecting a specific Schwartz test function whose Fourier transform has compact support, applying it to the spectral side of the trace formula to isolate the sum over Hecke eigenvalues, and then evaluating the complex geometric side [cite: 14, 19]. 

The geometric side of the Selberg trace formula for $\text{SL}(2, \mathbb{Z})$ requires intricate bounds over identity, hyperbolic, elliptic, and parabolic conjugacy classes. To isolate the murmuration density, researchers utilized the Hardy-Littlewood circle method to evaluate integrals over the geometric terms, combined with refined formulations of Weyl's law to bound the denominator (the total count of Maass forms in the spectral window) [cite: 14, 19]. 

### 5.2. The Kuznetsov and Petersson Trace Formulas
While the Selberg trace formula evaluates unweighted sums over the Maass spectrum, other trace formulas introduce arithmetic normalizations. The Kuznetsov trace formula, for example, weights the sum over Maass forms $f$ by the inverse of their symmetric square $L$-function values, or equivalently, their Petersson norm $1/\|f\|^2$ [cite: 19, 20]. 

The application of the Kuznetsov trace formula involves equating this weighted sum of Fourier coefficients to a geometric side featuring Kloosterman sums $S(m, n; c)$ and Bessel functions $J_{2iR}(x)$ [cite: 19]. While the arithmetically normalized versions present distinct technical hurdles, they similarly yield provable murmuration densities, confirming that the statistical bias in coefficients is an intrinsic, pervasive feature of the automorphic spectrum rather than an artifact of a specific normalization [cite: 19].

## 6. Machine Learning Investigations of Maass Forms

While trace formulas offer a theoretical framework as $R \to \infty$, the practical classification of low-lying Maass forms relies heavily on computational data science. In 2025, Bieri, Butbaia, Costa, Deines, Lee, Lowry-Duda, Oliver, Qi, and Veenstra undertook a massive machine learning investigation to predict the Fricke signs of Maass forms [cite: 4, 10, 21].

### 6.1. The LMFDB Dataset and Computational Bottlenecks
The researchers utilized the L-functions and Modular Forms Database (LMFDB), a central repository for explicitly computed arithmetic objects [cite: 4, 6]. The dataset extracted comprised 35,416 rigorously computed Maass forms of weight 0 and trivial character, with levels $N \le 10^5$ [cite: 2, 4]. 

A major computational bottleneck in the LMFDB is the rigorous determination of the Fricke sign $w_N$. Computing the Fricke sign requires extreme precision in the evaluation of the Laplace eigenvalue and the Fourier coefficients, often relying on automorphic certification, explicit trace formulas, and advanced implementations of Hejhal's algorithm [cite: 4, 9]. Due to these intensive computational requirements, only 19,993 forms in the database possessed a rigorously confirmed Fricke sign. The remaining 15,423 forms had unknown Fricke signs (assigned a placeholder value of $w=0$ in the database) [cite: 2, 9].

### 6.2. The Failure of Unsupervised Learning
The researchers initially sought to determine if the Fourier coefficients inherently clustered into partitions based on the root number. Unsupervised machine learning techniques, specifically Principal Component Analysis (PCA) and k-means clustering, were deployed on the vectors of Dirichlet coefficients $(a_p)$ for primes $p < 1000$ [cite: 4, 9]. However, these unsupervised methods were entirely unsuccessful at producing clusters separated by the Fricke sign [cite: 4, 9]. The murmurations—while mathematically present—are too subtle and deeply embedded in the high-dimensional coefficient space to be isolated without labeled structural guidance.

## 7. The ML-Predicted Partition: Supervised Learning Methodologies

To overcome the limitations of unsupervised clustering, the research team pivoted to supervised learning, treating the known subset of 19,993 forms as ground truth to train algorithms capable of predicting the Fricke sign of a Maass form based solely on a truncated list of its Fourier coefficients [cite: 2, 4, 9].

### 7.1. Linear Discriminant Analysis (LDA) and Stratification by Parity
The primary model utilized was Linear Discriminant Analysis (LDA), a classic, highly interpretable supervised dimensionality reduction and classification technique grounded in Bayes' theorem [cite: 2]. The objective was to learn a linear decision boundary separating the forms with $w_N = +1$ from those with $w_N = -1$. 

Crucially, the theoretical understanding of murmurations indicated that the parity of the form $\sigma(f)$ drastically alters the structure of the completed $L$-function and the resulting statistical oscillations. Consequently, the dataset was stratified by parity. 
The labeled dataset was partitioned into:
* **Even Forms ($\sigma=0$)**: 5,009 forms with $w_N = +1$, and 7,171 forms with $w_N = -1$.
* **Odd Forms ($\sigma=1$)**: 3,724 forms with $w_N = +1$, and 4,089 forms with $w_N = -1$ [cite: 2].

### 7.2. Training, Validation, and Accuracy Metrics
The supervised learning experiments involved standard 80-20 splits for training and testing, resulting in a robust training corpus of 12,795 observations [cite: 2, 4]. 

When LDA was trained on all available data normalized by symmetry, it achieved an impressive 96.1% accuracy on the validation dataset [cite: 4, 22]. To investigate the role of parity more closely, the researchers masked the training data. Training strictly on the 7,772 even forms yielded an accuracy of 94.9% on similarly masked validation data, while training strictly on the 5,023 odd forms resulted in 96.3% accuracy [cite: 4, 22]. (Note: Summarized abstracts for this research occasionally cite the accuracy broadly as 96% for even and 94% for odd parities [cite: 10, 23], though the rigorous tabular text delineates the 94.9% and 96.3% validation split respectively [cite: 4, 22]). 

These metrics demonstrated unequivocally that, even without complex hyperparameter tuning, the ML models were capable of executing a polynomial-time prediction of the global Fricke sign using only local Fourier coefficients—a task historically demanding immense analytic precision [cite: 4, 11, 22].

### 7.3. Neural Networks and Feature Importance
Beyond linear models, the researchers also deployed Deep Neural Networks (DNNs) to investigate non-linear feature interactions [cite: 4, 9]. The neural architectures achieved accuracy metrics comparable to the LDA baseline (exceeding 96%) [cite: 4, 9]. Furthermore, by restricting the networks to train on increasingly smaller subsets of the initial coefficients $a_p$, the authors identified that the models placed immense feature importance on primes $p$ that divide the level $N$, leveraging the subtle ways the Fricke sign is deeply embedded into the bad prime coefficients [cite: 9].

## 8. Validating the ML-Predicted Partition

With highly accurate models trained and validated, the researchers addressed the ultimate goal: classifying the 15,423 Maass forms in the LMFDB (labeled $L_0$) whose Fricke signs were genuinely unknown [cite: 2, 4]. 

### 8.1. Averaging the Unclassified Dataset
Upon applying the trained LDA model to the $L_0$ dataset, the forms were partitioned into predicted $+1$ and $-1$ root number classes. To verify the reasonableness of these predictions, the researchers plotted the moving averages of the coefficients $(-1)^{\sigma(f)} a_p$ for the newly classified data. The resulting graphical plots exhibited the exact same "murmuration" wave-form oscillations observed in the rigorously known dataset [cite: 2, 4]. 

Interestingly, detailed visual analysis revealed a discrepancy at small primes: when $p$ is small, there is a notably greater similarity between the genuine (ground-truth) murmurations and the predicted murmurations for odd Maass forms than there is for even Maass forms [cite: 4, 22]. This nuanced observation aligns with the slightly higher validation accuracy (96.3%) achieved on the odd stratification compared to the even stratification (94.9%) during training [cite: 4, 22].

### 8.2. Comparison with Hejhal's Algorithm Heuristics
To provide a secondary, independent validation of the ML-predicted partition, a subset of the predictions was evaluated against heuristic mathematical guesses [cite: 4, 9]. Dennis Hejhal's algorithm provides a numerical method to compute eigenvalues and Fourier coefficients of Maass forms. While sometimes lacking the strict rigorous precision required for database certification, Hejhal's algorithm can output highly reliable heuristic guesses for the Fricke sign [cite: 2, 9]. 

When the ML-predicted partitions generated by the LDA and Neural Network models were cross-referenced against the heuristic guesses provided by Hejhal's algorithm, the two entirely distinct methodologies produced matching classifications approximately 95% of the time [cite: 9, 23]. This overwhelming confluence of data-scientific predictions and analytic heuristics solidifies the viability of utilizing machine learning to complete vast, unknown sections of mathematical databases.

## 9. Broader Implications for Mathematical Data Science

The success of extracting the global root numbers of GL(2) Maass forms using machine learning represents a paradigm shift in computational number theory. 

### 9.1. ML as an Oracle for Trace Formulas
In traditional mathematics, one utilizes trace formulas to explicitly bound and calculate asymptotic behaviors. However, as noted in presentations on this topic, machine learning models act as a "one-sided oracle" [cite: 6]. The ML algorithms cannot output a formal proof of the Birch and Swinnerton-Dyer conjecture, nor can they prove the Selberg trace formula. However, if model performance on a specific set of features (like $a_p$) achieves 96% accuracy in predicting a global invariant (like the root number), it provides irrefutable statistical proof that the arithmetic information is deterministically contained within those features [cite: 6].

The discovery of murmurations—and the subsequent ML-predicted partition of Maass forms—serves as a textbook example of AI-assisted mathematics [cite: 21]. The machine learning anomaly pointed mathematicians directly toward an undiscovered statistical correlation, prompting experts in trace formulas (such as Bober, Booker, Lowry-Duda, etc.) to successfully search for and explicitly prove the existence of the murmuration density functions [cite: 14, 18].

### 9.2. Future Directions
The synthesis of deep learning with the Langlands program is rapidly expanding. Current research is aiming to apply Kuznetsov trace formulas to prove arithmetically normalized murmurations for symmetric square $L$-functions of Maass forms (a GL(3) aspect) [cite: 19]. As models grow more sophisticated, predicting Euler factors, Shafarevich-Tate group dynamics, and higher-degree L-function vanishing orders using mathematically interpretable machine learning will likely become standard practice for augmenting large-scale computational databases like the LMFDB [cite: 10, 21].

## 10. Conclusion

The investigation into GL(2) Maass form L-function root numbers sits at the vanguard of a new era in mathematics, bridging rigorous analytic trace formulas with the pattern-recognition capabilities of modern machine learning. The Fricke sign, a critical global invariant determining the root number and the functional equation's symmetry, leaves a subtle statistical fingerprint on the local Dirichlet coefficients—a phenomenon termed a murmuration.

Analytically, tools like the Selberg-Strömbergsson and Kuznetsov trace formulas have definitively proven that these murmurations are an intrinsic asymptotic property of the Maass spectrum as the Laplace eigenvalue tends to infinity. Computationally, Machine Learning models—specifically Linear Discriminant Analysis and Deep Neural Networks—have leveraged these murmuration patterns to predict the Fricke signs of previously unclassified Maass forms with remarkable 94-96% accuracy. Validated against the heuristic outputs of Hejhal's algorithm, this ML-predicted partition solves a major computational bottleneck, demonstrating that data science is not merely a tool for mathematical computation, but a fundamental engine for profound mathematical discovery.

**Sources:**
1. [wsu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8kDDJgQCHJIj1E7u69n36S5jxxQ-rzqGgF6YrfAYtD_yyCkVCCtFpTVV-r5wLpNEpSmil3ZIfmq-4rKIjBr3nnrbSrns6Y3e9YTdCyZ9DiTuIe5EIlaW0FIs5ki7kz3y76cqEr_UPLdRSGqbOeDeuTKGMbpiI7G5FYLQmaZ2Tt61GlZswYTKHSD1uOJFEB8Kch26epWhuNujTUFpubxQa5EmLkg==)
2. [tamarabveenstra.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQECCUPttUws30O5xXzP9mII1Sbq3W5KwksbpugyirMTtucx2RxC8XMbR4-s-gQ7bY7H7kZX1IZHX4uCcQDfrmrjxnthqi26S1FRfIseQGxGkiALQljWxOwnOh-pMR2cQrk-4Mok)
3. [d-nb.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyMR2gQSGw45WKWjgA6ELS4JTVA2lXkGKFrsHWu2pHClEfqPrlu0KgWe-lowfvz_5uegToCqdS0jO4Q37R_ViHojMTt9hoEp0tbrqUB02fpJtArCk=)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgLJ-twVKd11Jb4xfPogUZIYRtP8zQ6KoACbXYxGpJU6uGRM49gZFacsvCRV9HHVyvLalbc_duDFCQUsQcwl0Zf-fQ7Q0bLadLl9jGlkGghGFRU9ZR)
5. [edgarcosta.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMIsURiJQayNXVVAGxwtKuI_gd8fgbg7rIIOG6gwP0bUGFyPqmbqbTTHQqgLsxZTKwD1odEp76UgnZ-3qiggNx9bW6KDU4P6sL_6_8fY0LjqGKap0TtJcSI2zIS008JRd-GgFG9z8D)
6. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5sHdEyn9Pj6YmACEUMoykI416dRyu_Xh9ioAsnuSJI511ZAWCuotY_nuaD_K6t3STZQLeJ_illhKzUb36k1jnCCHYP99HvSoOnsaGi3TaQ0DYD13JOZDELR9qk1teyJH5pD0fHEUClA==)
7. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKs8-YW6lXXDZAZQ2ScDpacwq6HWV7-jGSDrzqqknVPjLdizT8vQhg6uJ5Dz_VOGDjAXOlk5N_QI0ckgZ0gc5m4VZLeIGQxWu7eLsAyBru725ode17l94VzIs1JL_XthXs5w0=)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7Wji92i7wOlS0AzGsHoM161zU2PTrsBkkFzO-U_hIq_1CwTGx3g9e0Hw-NmvMax2-RuYpAOmRA6tU-MXfIK0VZjZGc7o39hLO-dONafWxAVTZzD4i)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZrbfyQx9vkTXku5Qa1P5LRxy-EpX1gVcDMUT-NU9bc7PRwCTz5wIhhwjj-IakN4vsoiurviFJUtohVXy4wRo_w4RXeJrQKHFQCRKdZovMWkW4wTKqyGkf)
10. [intlpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFSVYQxgdNAiVbZUvd1ZkPMSRAVudIDrJfD8d9yOWipk2oKYueQMBmHq4Z7yiZEig0_PjvPZmlZS77E42ElSRTUh3bcBeQdZ2o6sF94AYG1p-2Kj5jqjQhZh3cJ_0SDzDckgVoH3s=)
11. [uconn.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2Gri100yhEh_dSR_fA-hTJkKl-cuHxoR-71An6zhZulpivdyrwzZto_sbTosrKRcQVPp_yUxZn3nFEDZUo36B--5cRks7lyHjO2bS9v77fen9zTbqjD4TLKUTzgIYv338QSigJ4ZiC_5-7IWNpZGm_P0MTvCq96TnHB2npuYBLuCxK7VyHAbNax0Ibh7EXd9-6IbvuToZuZWjQm-NnoJhVQ2C)
12. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7XG0KzaXidw2UjowqJ8jx2yIfFKUbqmVmUETsZhMaMJ22JHIIcv8jdV-OI1eN0lz7H6pCVb_277yJfncVxgYL1jrbbvPjmJcsW5ujZ1WvDooYVynXXqltqsioF_XcxAL27lU=)
13. [utrgv.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpQBxOk6hoEIuOCZxQP8ijBJt_NbYcf57ESLM_OTXDO6XznXrn6QxOU3UOAoOynB4cCr953JRWNmZ-U9xRz-RdAXdj4KCPhZaRI4735rkCpFlfYYLlo4lPpvk0o80QDLpjPIxjcEWakOCFsSZysQ==)
14. [kyoto-u.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8mTTLd2MnqE2aXPvtX-Z36N2djV8DNfFRbO5i8msp-J5WMe-RsxWVw6X_keIT70nsH6BQlUhMAY4dugH7k_GGG1NpVzLskX0yJqpDwo6WjmSM0-mA57z2xFP9hD-eiITwt7T2x8rClW43ia2_jl5FzMnnDr7PIemfu4ZOCdLQ)
15. [stonybrook.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTNTsW2Ywm0JrEFmngY0RaHna56Tm7f_agzLNmnCVMXn6-5h4_DU-MP1EmPcMloHuUQQnMUjA9Um8uCp7uQ4fNjbvZCggmOqMA7Ms200XlgD21hrpq9l41ocBhapvWg4TMy_wWPgnSqaYjd2GhwjU2Tknqwqd8zkp_0vJZ2Vd-dCc8dZXcelYvKeGCl6WgXJydhTIrMo9u-z_-3tYMY28uzLXHpV8gTgTJVViaNNK8AZl9OMZK3nWlfrEteCIjkAbPtIWYnm4o4B3MuOlHAG2hQpZmPr3BR5UcFg9wnmMEg0T_sIEVE9Ifw4rMqxOl3qb1b-w70AaG1LkinQ80P70J-rYLHetuLfQlgSeucv4ekdstEcwX7-VZVTc4gXHv-rO-DFxAGnqB94ybgWob0vNEg9aZUkkA5IHC0DV5bsuKwILLpzdSwye0MLpidR7X4S9viALsv1mQl4ljYbvCbO5lO2YiLUlvS-XJUeDE6FOm2QbB-JDe9kSaTh74VS0gk4k-B9Gi-WBmb2mkF73hju9VZVKHjUkXOo6TCAoxis1E4YnU_LaG-zzxMB7_LGncocExl1b_M2TEi0fiEHOTMR6354poFZza-pBur0CneSoUMjhQZhB-DCyx-XAVvDuD5KWZFx_Kb-tjGO7y45xrGBaX3Hqb3I03xZ6BDFuzLFUwW10=)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPZ41oVzS0vaSBBGZCYwzG-EB2On75FT6Sj1xCbHJhcC5Im_PU010nafqvs1NeP59xKXYHyJONX6LmyC3cKUWSTf0-y6Cpbk_24QIZbd5PQaKdJmg3)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGB-abN4gmzutu7YDdk_fk3rtrloyzzwVjm2qC1XsER_zdib7Zl0RS1CLOcJiRqtoo2qeahsiFcVf6t8mdwo7OgZj3lx6cGq2Zy-rntj2QolPISoY02Zp_9)
18. [davidlowryduda.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHs7HddI2E0QsxGiO9T3HJQubPXyV7q5E3ojnJhPko5KpKq47NgKnQddp2MLUdN-fKh0PagcOlVGdtPXQ65o5K8SGaoibzaAWEkl1iSJzuLbupc_2QMK9eFn3SdHGHmUoZL_xTq-GTHZXLVLA==)
19. [davidlowryduda.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE50XlaeeYnyXns2b5YPq_Gtur6I6J8Z-tSAc4SV7R3aFloDz4jUenMlK0TaUCtvgVqX4U8fejUyP0eUjOerQWOirrZ4MQCgFkntQlzaNy3DRoUoiLoH2IbtKYQ2wJa4-SO-BH3M2jNuoTftV1H3nXMAa22TNIFwZ_y6n0=)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTmbUmJHUkg1TwwZUk44VJM3FL-XXKCMGQDWay1EXV-iZjcOzFZ847g3FaRWTUTk5wiobde9L5QgnOCcn_An2176bDBEjpwOgJ018nqPk8ywEzrzs8)
21. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4UmH8gGtTivuoiEvAcVoRcWBfxI7bfdAFkdxuEzZNZezulRiwsHvwsruhBhYFYHyeLwppbH6km1DwMo4ttzeWnzGNhdyH9c4qh7nc5lmchC83-fZZ63j51xGBCdRgJQ==)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSl51jVMy9THM9fCUnx7_DTovrBGsHNarVlIvoLP-nFC0bFxuxkjv6Aq_tp2GGXAf_QWRIPdi7zhifg2SLGwljXvlN0ESp2rluMW7BpAaoudfuuXNl9w==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJ7sT2B4GDbh1Y1e5WFZlC3mETcJ6vtR4bhyfNVGpngtQHvrxI99951o4ozvnSG6NtVk-3aj_iY3BPJbIotp4ug7drn_MHySL1thblnSb9drg-znQe)

