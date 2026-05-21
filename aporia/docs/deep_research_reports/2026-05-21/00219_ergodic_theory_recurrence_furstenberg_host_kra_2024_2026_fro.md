# Ergodic theory + recurrence (Furstenberg, Host-Kra) 2024-2026 frontier

**Pythia queue id:** 219
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdDMDRQYW9HUEJKX0dqTWNQZ2RfZmdRYxIXQzA0UGFvR1BCSl9Hak1jUGdkX2ZnUWM
**Elapsed:** 249s
**Completed at:** 2026-05-21T18:29:24.834831+00:00

---

# Ergodic Theory and Multiple Recurrence: The 2024-2026 Frontier of Furstenberg and Host-Kra Structure Theory

**Key Points:**
*   **Resolution of the Bergelson-Tao-Ziegler Conjecture:** Research strictly confirms the breakdown of the Abramov system conjecture in low characteristics; specifically, a Host-Kra $\mathbb{F}_2^\omega$-system of order 5 is not Abramov of order 5, revealing deep non-measurability obstructions for the $U^6$ Gowers norm.
*   **Introduction of Polynomial Towers:** The structural theory of Host-Kra factors for bounded-exponent abelian groups has been revolutionized by the introduction of "polynomial towers," eliminating the need to embed into larger groups to prove inverse Gowers theorems.
*   **Pointwise Convergence Breakthroughs:** Significant advancements have been made in the pointwise almost everywhere convergence of multilinear polynomial ergodic averages, particularly along prime sequences weighted by the von Mangoldt and Möbius functions.
*   **Hardy Field Recurrence Dynamics:** New counterexamples have redefined our understanding of joint intersectivity and recurrence along Hardy field sequences, disproving established integer-coefficient hypotheses.
*   **Uncountable Ergodic Structure Theory:** The Furstenberg-Zimmer and Host-Kra-Ziegler structure theories have been generalized to uncountable amenable groups and inseparable probability spaces using pointfree probability algebras.

**Overview:**
Ergodic Ramsey theory, initiated by Hillel Furstenberg’s ergodic proof of Szemerédi's theorem, has undergone a paradigm shift between 2024 and 2026. The intersection of abstract topological dynamics, measure-theoretic multiple recurrence, and additive combinatorics has matured into a deeply algebraic discipline governed by the Gowers-Host-Kra uniformity seminorms. The classical Host-Kra structure theory, which elegantly described characteristic factors of $\mathbb{Z}$-actions as inverse limits of nilsystems, has now been pushed to its absolute limits over arbitrary abelian groups and finite fields. 

Recent research has not only generalized these structure theorems to groups of bounded torsion and uncountable amenable groups but has also unearthed profound structural barriers. The discovery of "extractive collapse" in the inverse theorem for the $U^6(\mathbb{F}_2^n)$ norm highlights that mathematical existence in higher-order Fourier analysis does not guarantee constructive algorithmic access. Simultaneously, the analytical machinery for proving pointwise convergence has reached new heights, successfully deploying the multilinear circle method to prime-weighted and sparse sequences. This report provides an exhaustive, highly detailed academic synthesis of the 2024–2026 frontier in ergodic theory, focusing on multiple recurrence, Host-Kra structure theory, and their combinatorial implications.

---

## 1. Foundations of Ergodic Ramsey Theory and Multiple Recurrence

### 1.1 The Furstenberg Correspondence Principle
The modern synthesis of dynamical systems and additive combinatorics began in the late 1970s when Hillel Furstenberg realized that Szemerédi's theorem—the assertion that any subset of integers with positive upper density contains arbitrarily long arithmetic progressions—could be recast as a multiple recurrence theorem in ergodic theory [cite: 1, 2]. Furstenberg's correspondence principle bridges the discrete geometry of subsets of $\mathbb{Z}$ to the measure-theoretic properties of probability-preserving dynamical systems [cite: 3]. 

For a measure-preserving system $(X, \mathcal{X}, \mu, T)$, where $X$ is a standard Borel space, $\mu$ a probability measure, and $T: X \to X$ an invertible measure-preserving transformation, Furstenberg’s multiple recurrence theorem established that for any measurable set $A \in \mathcal{X}$ with $\mu(A) > 0$ and any integer $k \geq 1$, there exists $n \geq 1$ such that:
\[ \mu(A \cap T^{-n}A \cap T^{-2n}A \cap \dots \cap T^{-kn}A) > 0 \]
This foundational result relies on the dichotomy between the "compact" and "weakly mixing" parts of a dynamical system [cite: 1].

### 1.2 The Host-Kra-Ziegler Structure Theory
While Furstenberg and Zimmer developed a conditional structure theory relative to abstract factors to prove recurrence [cite: 1], identifying the explicit algebraic nature of the limits of multiple ergodic averages remained a profound open problem. In the mid-2000s, Host and Kra, and independently Ziegler, established a breakthrough by defining a sequence of uniformity seminorms, now known as the Gowers-Host-Kra seminorms [cite: 4]. 

For an ergodic $\mathbb{Z}$-system, Host and Kra demonstrated that the limiting behavior of the $k$-term multiple ergodic averages:
\[ \frac{1}{N} \sum_{n=1}^N f_1(T^n x) f_2(T^{2n} x) \dots f_k(T^{kn} x) \]
is entirely governed by a specific factor of the system, denoted as $\mathcal{Z}_{k-1}(X)$, called the universal characteristic factor of order $k-1$ [cite: 5, 6]. The crowning achievement of the Host-Kra-Ziegler structure theory is the structural description of these characteristic factors for $\mathbb{Z}$-actions as inverse limits of rotations on nilmanifolds (nilsystems) [cite: 1, 7]. 

This continuous ergodic theory is deeply intertwined with higher-order Fourier analysis in additive combinatorics. The finitary counterpart of the Host-Kra-Ziegler structure theorem is the inverse theorem for the Gowers uniformity norms $U^k$, pioneered by Green, Tao, and Ziegler, which characterizes functions with large $U^k$ norm as those correlating with nilsequences [cite: 1, 8]. However, attempting to generalize this nilspace-theoretic approach from $\mathbb{Z}$-actions to actions of arbitrary countable abelian groups—particularly groups of bounded exponent like $\mathbb{F}_p^\omega$—has driven the principal research frontier of 2024-2026 [cite: 4, 9].

---

## 2. The Breakdown of the Abramov Conjecture and Low Characteristic Obstructions

A major theme in the 2024-2026 frontier is understanding Host-Kra factors for the action of $\mathbb{F}_p^\omega$, the infinite-dimensional vector space over a finite field of prime characteristic $p$. This setting is the ergodic analogue of studying the Gowers $U^k$ norms over $\mathbb{F}_p^n$.

### 2.1 Abramov Systems and the Bergelson-Tao-Ziegler Conjecture
To analyze Host-Kra factors for non-cyclic groups, researchers rely on the concept of **Abramov systems**. Let $G$ be a countable abelian group and $(X, \mathcal{X}, \mu, (T_g)_{g \in G})$ an ergodic $G$-system. The system is said to be an Abramov system of order $\leq k$ if it is generated (as a measure algebra) by polynomial phase functions of degree $\leq k$ [cite: 10, 11]. 

Bergelson, Tao, and Ziegler, in their foundational work on the inverse theorem for the uniformity seminorms associated with $\mathbb{F}_p^\omega$, conjectured that every Host-Kra $\mathbb{F}_p^\omega$-system of order $k$ is isomorphic to an Abramov system of order $k$ [cite: 5, 12]. For years, this conjecture was verified only for $k \leq p+1$, leaving the low-characteristic regime (where $k > p+1$) as a highly challenging open problem [cite: 4, 12]. In these contexts, researchers utilized p-homogeneous nilspaces to recast the conjecture into an algebraic problem on finite nilspaces [cite: 4, 5].

### 2.2 The Jamneshan-Shalom-Tao Refutation (2026)
In a landmark 2026 paper published in *Mathematische Annalen*, Asgar Jamneshan, Or Shalom, and Terence Tao conclusively demonstrated that the Bergelson-Tao-Ziegler conjecture fails in low characteristic. Specifically, they proved that for $k=5$ and $p=2$, a Host-Kra $\mathbb{F}_2^\omega$-system of order 5 is **not** an Abramov system of order 5 [cite: 12, 13]. 

This refutation represents a significant divergence between the high characteristic and low characteristic structural behavior of dynamical systems. The failure arises from the inability to cleanly express certain "strongly symmetric $k$-linear forms" as the $k$-fold derivative of a degree $k$ polynomial without invoking non-measurable choices of basis [cite: 12]. To finitize this assertion, Jamneshan, Shalom, and Tao translated this measure-theoretic obstruction into a combinatorial statement regarding the $U^6$ Gowers norm over $\mathbb{F}_2^n$.

### 2.3 Non-Measurability and "Extractive Collapse" of the $U^6(\mathbb{F}_2^n)$ Norm
The finitary analogue of the system's failure to be Abramov reveals a profound phenomenon in additive combinatorics. The authors produced a bounded function $f: \mathbb{F}_2^n \to \mathbb{C}$ that possesses a large Gowers uniformity norm $\|f\|_{U^6(\mathbb{F}_2^n)}$ [cite: 12, 14]. According to the qualitative inverse theorem for Gowers norms, this implies that $f$ must correlate with a non-classical quintic phase polynomial $e(P)$. 

However, Jamneshan, Shalom, and Tao proved that all such phase polynomials $e(P)$ correlating with $f$ are "non-measurable" [cite: 12, 15]. In this finitary setting, "non-measurable" means that $e(P)$ cannot be well-approximated by functions generated by a bounded number of random translates of $f$ [cite: 12]. 

This mathematical event has been characterized by external analysts as an **"extractive collapse"** [cite: 16]. While the Gowers inverse theorem formally proves the *existence* of a correlating phase polynomial (and is thus true in Zermelo–Fraenkel set theory), it actively obstructs algorithmic or constructive reconstruction [cite: 16]. No Borel measurable selector exists to witness this correlation in low characteristics [cite: 16]. Consequently, any quantum or classical algorithms attempting property testing or arithmetic progression counting using the $U^6$ norm over $\mathbb{F}_2^n$ must inherit intractable tower-type complexities [cite: 16, 17]. This highlights an essential disconnect between mathematical truth and constructive utility in higher-order Fourier analysis [cite: 16].

---

## 3. Polynomial Towers and Bounded-Exponent Groups

With the failure of the Abramov conjecture in low characteristics, the structural classification of totally disconnected Host-Kra-Ziegler factors for bounded torsion groups required a new architectural framework [cite: 10, 18]. In early 2026, Jamneshan, Shalom, and Tao introduced a transformative concept known as the **polynomial tower** to bypass these obstructions [cite: 11, 19].

### 3.1 The Concept of Polynomial Towers
A polynomial tower is defined as a dynamical system obtained through a finite iteration of abelian extensions of the trivial system by polynomial cocycles [cite: 11, 13]. Crucially, unlike the classical Host-Kra structure theory, the intermediate extensions within a polynomial tower are *not required* to agree with the exact Host-Kra factors $\mathcal{Z}_{\leq k}(X)$ [cite: 11, 20].

The authors established that for an abelian group of bounded exponent, the Host-Kra factors associated with ergodic actions admit extensions that possess the structure of polynomial towers [cite: 11, 20]. By relinquishing the strict requirement that the system exactly matches the Host-Kra factors at every intermediate step, they bypassed the non-measurability obstructions found in the $U^6(\mathbb{F}_2^n)$ case. They proved that all such extensions are indeed Abramov (generalizing results by Candela, González-Sánchez, and Szegedy) and have the structure of $k$-step translational systems [cite: 11, 20]. However, they are not necessarily Weyl systems [cite: 11].

### 3.2 Solving the Inverse Gowers Theory for Bounded-Exponent Groups
This ergodic-theoretic innovation directly unlocked the inverse theorem for Gowers norms over arbitrary finite abelian groups of bounded exponent [cite: 11]. Previously, researchers were forced to treat "high characteristic" and "low characteristic" cases via entirely separate machineries, or by artificially extending the underlying group [cite: 11, 19]. 

Using the polynomial tower structure theorem, coupled with a correspondence principle, Jamneshan, Shalom, and Tao derived the inverse theorem: a large $U^{k+1}$ norm of a function on a finite abelian group of bounded exponent implies a large correlation with a polynomial of degree $\leq k$ *on the same group* [cite: 11]. This holds true even when the exponent of the group is not square-free or is divisible by small primes, entirely resolving a longstanding conjecture and answering questions posed by Candela, González-Sánchez, and Szegedy [cite: 11]. The induction process involves a delicate procedure of "straightening" cocycles by differentiating them, deriving Conze-Lesigne type equations, and splitting short exact sequences of topological abelian groups while maintaining properties like large spectrum and purity as one ascends the tower [cite: 19].

---

## 4. Pointwise Convergence of Polynomial Multiple Ergodic Averages

While norm convergence ($L^2$ convergence) of multiple ergodic averages has been deeply understood since the work of Host, Kra, and Walsh [cite: 7, 21], establishing pointwise almost everywhere (a.e.) convergence has remained one of the most notoriously difficult problems in ergodic theory. This forms the core of the Furstenberg-Bergelson-Leibman conjecture [cite: 3]. Between 2024 and 2026, dramatic progress occurred in identifying pointwise limits for averages along polynomial orbits and sparse sequences, specifically the primes.

### 4.1 The Shift to Sparse and Weighted Sequences
Bourgain originally established pointwise a.e. convergence for a single polynomial iterate and for single linear averages along the primes [cite: 22, 23]. Extending this to multiple polynomial iterates, especially with arithmetic weights, demands overcoming severe harmonic analysis challenges [cite: 23].

In 2025, Renhui Wan published a groundbreaking result establishing pointwise almost everywhere convergence for polynomial multiple ergodic averages weighted by the von Mangoldt function $\Lambda(n)$ (which acts as a weighted indicator for the primes) [cite: 23]. For an invertible measure-preserving system $(X, \nu, T)$ and functions $f_1, \dots, f_k \in L^\infty(X)$, the average:
\[ \frac{1}{N} \sum_{n=1}^N \Lambda(n) f_1(T^{P_1(n)}x) \dots f_k(T^{P_k(n)}x) \]
converges pointwise $\nu$-a.e., provided the integer polynomials $P_1, \dots, P_k$ have distinct degrees [cite: 23, 24]. 

### 4.2 The Multilinear Circle Method
Wan's proof represents a culmination of recent frameworks, directly building upon the unweighted polynomial averages of Krause, Mirek, and Tao (2022) and Kosz, Mirek, Peluse, Wright (2024) [cite: 23, 25]. Because the von Mangoldt weight $\Lambda(n)$ does not exhibit the clean polynomial decay in the minor arcs that unweighted averages do, traditional metric entropy arguments fail [cite: 25].

To circumvent this, a novel **multilinear circle method** was developed [cite: 23, 25]. This required transferring the system to the integer shift system $(\mathbb{Z}, \nu_\mathbb{Z}, T_\mathbb{Z})$ via the Calderón transference principle [cite: 25]. The analysis decomposes frequency space into major and minor arcs, utilizing Cramér and Heath-Brown approximants to model the von Mangoldt function [cite: 22, 25]. A generalized von Neumann theorem, relying on Peluse's inverse theorem for the Gowers norms, allows the reduction of the averages to bounds involving the "little" Gowers norms [cite: 25]. The framework establishes an inverse theorem and Weyl-type inequality for multilinear Cramér-weighted averages, alongside a multilinear Rademacher-Menshov inequality [cite: 24]. 

Interestingly, while convergence along prime sequences is challenging, convergence of ergodic averages weighted by the **Möbius function** $\mu(n)$ is highly robust [cite: 22, 26]. Recent progress in quantitative Gowers uniformity of the Möbius function demonstrates that Möbius-weighted non-conventional ergodic averages converge to zero pointwise almost everywhere, effectively showing that multiple polynomial dynamical systems possess no local correlations with the parity of prime factors [cite: 22].

### 4.3 Joint Ergodicity and Nilpotent Groups
Alongside single-transformation pointwise theorems, the 2024-2026 period saw expansions in joint ergodicity for nilpotent groups. Pointwise almost everywhere convergence was established for ergodic averages along polynomial sequences in nilpotent groups of step two, utilizing a "nilpotent circle method" to bypass the non-commutativity that standard Fourier transform tools cannot handle [cite: 27]. Furthermore, bounds for $r$-variation ($r > 4$) were proven for multiple ergodic averages generated by three commuting transformations, utilizing discrete telescoping and partial integration over lacunary cones [cite: 28].

---

## 5. Recurrence along Hardy Fields and Smooth Sublinear Functions

Moving beyond pure polynomials, ergodic Ramsey theory has vigorously investigated sequences generated by functions from a **Hardy field**—a field of germs of real-valued functions at $+\infty$ that are closed under differentiation [cite: 21, 29]. Hardy fields include standard polynomials but also functions like $t^{3/2}$, $t \log t$, and exponential integrals, representing "smooth functions of polynomial growth" [cite: 29].

### 5.1 Convergence and Equidistribution on Nilmanifolds
Building upon the quantitative behavior of polynomial orbits on nilmanifolds by Green and Tao, recent work by Bergelson, Moreira, and Richter (2024) utilized equidistribution results to prove the convergence of multiple ergodic averages along Hardy field sequences [cite: 30, 31]. 

When taking functions $h_1, \dots, h_d$ from a Hardy field $\mathcal{H}$ of polynomial growth (e.g., $x^{d_h} \ll h(x) \prec x^{d_h+1}$), researchers look at the Taylor expansions and separate them into a strongly non-polynomial part and a polynomial part [cite: 30]. Equidistribution occurs when the strongly non-polynomial parts do not align with any rational obstacles [cite: 30]. Tsinas (2023, 2024) successfully established joint ergodicity of Hardy field sequences, mapping the distance of smooth sublinear functions from rational polynomials to determine their uniform distribution properties [cite: 21, 32].

### 5.2 Counterexamples to Integer-Coefficient Criteria (2026)
A central question posed by Bergelson, Moreira, and Richter concerned finding exact derivative-span hypotheses to characterize joint intersectivity and recurrence for Hardy fields [cite: 33]. They proposed an integer-coefficient criteria involving the real linear span of the functions, asking whether specific algebraic combinations forced a set of recurrence times to be thick or piecewise syndetic [cite: 33].

In May 2026, Kangbo Ouyang, Leiye Xu, and Shuhao Zhang published definitive counterexamples to these hypotheses [cite: 33]. Focusing on the test case pair $f_1(t) = t^{3/2}$ and $f_2(t) = \lambda t^{3/2} + t$ (with $\lambda \in \mathbb{R} \setminus \mathbb{Q}$), they proved that the proposed integer-coefficient replacement does *not* imply thickness [cite: 33]. Furthermore, they demonstrated that the integer-coefficient hypothesis does not even force nonempty common recurrence [cite: 33]. This negative resolution dictates that the combinatorial configuration of recurrence times along arbitrary real-valued Hardy field sequences is fundamentally more chaotic than previously hypothesized by the Bergelson-Moreira-Richter criteria [cite: 33].

---

## 6. Uncountable Ergodic Theory and General Furstenberg-Zimmer Theory

Historically, the Furstenberg-Zimmer structure theory—which decomposes systems into compact and weakly mixing extensions—was formulated under strict countability and separability hypotheses on the underlying groups and standard Borel probability spaces [cite: 1].

### 6.1 Pointfree Probability Algebras and Boolean Topoi
Recent work by Asgar Jamneshan removed these restrictions entirely, establishing the Furstenberg-Zimmer structure theory in full generality for arbitrary, potentially uncountable, group actions on inseparable probability algebras [cite: 1]. 

This uncountable ergodic theory systematically avoids null set pathologies by utilizing pointfree probability algebras, where groups act by measure-preserving Boolean isomorphisms rather than pointwise transformations on a space [cite: 1]. By leveraging the internal logic within certain Boolean topoi, Jamneshan established an unconditional dichotomy [cite: 1]. Beyond intrinsic mathematical motivation, this framework directly influences higher-order Fourier analysis by providing a rigorous space to analyze ultraproduct systems and hyperfinite abelian groups on Loeb probability spaces, heavily utilized by Tao and Ziegler [cite: 1, 2, 34].

### 6.2 Syndeticity and Amenable Multiple Recurrence
A combinatorial application of this fully generalized theory is the establishment of uniform syndeticity in multiple recurrence [cite: 34]. A subset of a group is *syndetic* if finitely many left translates cover the group [cite: 34]. 

While Zorin-Kranich had extended Walsh’s $L^2$ norm convergence to arbitrary amenable groups, his functional-analytic approach did not yield multiple recurrence statements (i.e., that the intersection of shifted sets is strictly positive and syndetic) [cite: 2, 34]. Using the pointfree framework and sated extensions, Austin's amenable multiple recurrence theorem was successfully generalized to encompass actions of uncountable amenable groups on inseparable spaces [cite: 34]. This proves that for any integers $d, l \geq 1$ and $\epsilon > 0$, the set of recurrence times in arbitrary amenable groups is uniformly syndetic, heavily relying on ultraproduct systems [cite: 2, 34].

---

## 7. Topological Dynamics and Nil-Bohr Multiple Recurrence

Parallel to measure-theoretic multiple recurrence is topological multiple recurrence, applying to continuous maps on compact metric spaces. In this setting, the return time sets are analyzed through the lens of Bohr sets and generalized polynomials [cite: 35].

### 7.1 Separation of Recurrence Notions
In 2025, the separation between measurable recurrence and topological recurrence was further clarified [cite: 35]. A set $S \subset \mathbb{N}$ is a set of topological $d$-recurrence if for every compact dynamical system $(X, T)$, there is a point $x \in X$ such that $T^n x, T^{2n}x, \dots, T^{dn}x$ simultaneously return arbitrarily close to $x$ for $n \in S$ [cite: 35]. 

Researchers recently resolved the "higher-order" Katznelson's question posed by Huang, Shao, and Ye [cite: 35]. It was proven that there exists a set which is *not* a set of multiple recurrence, despite being a set of recurrence for nil-Bohr sets [cite: 35]. This was achieved by constructing a set $S$ such that there is a finite coloring of $\mathbb{N}$ lacking three-term arithmetic progressions with common differences in $S$, yet $S$ lacks the traditional polynomial obstacles [cite: 35]. This formally disconnects nil-Bohr recurrence from pure topological multiple recurrence [cite: 35].

### 7.2 Return-Time Sets and Total Minimality
Advanced structure theorems for return-time sets:
\[ R_{p}(U_1, \dots, U_d) := \{ n \in \mathbb{Z} : U_1 \cap T^{-p_1(n)}U_1 \dots \cap T^{-p_d(n)}U_d \neq \emptyset \} \]
have shown that polynomial multiple recurrence behaves predictably in totally minimal systems [cite: 6]. Under total minimality, the maximal $k$-step pronilfactor acts as the topological characteristic factor, providing a robust topological analogue to the measure-theoretic Host-Kra factors [cite: 6]. Recent theorems established that polynomial recurrence along arithmetic progressions in totally minimal systems shares deep equivalence with older conjectures by Leibman, confirming that topological multiple recurrence remains deeply linked to the underlying pronilfactors [cite: 6].

---

## 8. Conclusion and Future Directions

The frontier of ergodic theory from 2024 to 2026 has been defined by extreme technical triumphs and the unexpected discovery of fundamental limitations. The Host-Kra-Ziegler structure theory has survived contact with arbitrary countable abelian groups through the ingenious invention of "polynomial towers" by Jamneshan, Shalom, and Tao, which completely avoids the need to artificially expand bounded exponent groups to secure inverse Gowers theorems [cite: 11, 19]. 

Simultaneously, the collapse of the Bergelson-Tao-Ziegler conjecture in low characteristics (e.g., $k=5, p=2$) and the proof of non-measurability of Borel selectors for the $U^6$ norm stands as a stark reminder of the limits of classical mathematical logic when applied to higher-order Fourier analysis [cite: 12, 16]. This "extractive collapse" will heavily dictate the design of future classical and quantum algorithms dealing with Gowers norms and property testing, as the theoretical existence of phase polynomials does not yield computationally viable extraction paths [cite: 16, 17].

On the analytical side, the successful synthesis of the multilinear circle method with the latest additive combinatorics to prove the pointwise convergence of prime-weighted multiple ergodic averages closes a major gap in the Furstenberg-Bergelson-Leibman framework [cite: 23, 24]. Future research will likely focus on resolving the exact conditions of joint intersectivity for totally arbitrary Hardy field sequences [cite: 33], expanding the nilpotent circle method beyond step-two nilpotent groups [cite: 27], and mapping the exact boundary where topological nil-Bohr recurrence diverges from strict combinatorial multiple recurrence [cite: 35]. 

Through continuous cross-pollination with harmonic analysis, additive combinatorics, and model theory, ergodic multiple recurrence remains one of the most vibrant, challenging, and profoundly fundamental areas of modern mathematics.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqXICh1RwLWudx9uQNKD6RQQ8hVr4VrEID0kt2P7ZMIajJkihzuI7lAhPIYM3OtttW3_8GrsKas4t633P7XU56tYNyxtdLgEVVv5JJ3pG5FQyXoY0AnMtDEQ==)
2. [aimsciences.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESWTLi7XL49bgi9WOR0lbFxZ16NzIQ8z6dzNOyBdPH1xgWMTjLffzNxzOgYYIT6qMe2H-5Qrg9FWipuN_hitrAdY6OOyUvLahQka85RJDQPxdNaWHXKfLgJvAMAlfQds8f6OZCnBaBj_w_TuWEgPcaPf8=)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7s68oLaTG5-PFYZ6N5a59mI14EZHcZ3UUZBOOMt3IsLwW6UQDBV7rTjJGQiFt5wpiVRqRbk930lYWwlprbiK36kEUsMazbaadpP5XLQdLTFMNu3eDvM_-gA==)
4. [csic.es](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHharkKx9Db4IhCr056h5KCMoXcxV7aY1gWUT0JCrc7KswR0mQxW15lDVlembtbF-THbvSfXtNfAPyR7Zb0OXar9aYN-5L4hUi8DubMJgTwsWB9Q95nlxRyHBCm_WQURMAQ_RlE6Axu-P20DOQt3PiUYDSZbDyVzjsT-QHP)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtdC8EbmIPrBGEmiXP0ByGIbFUMnTitFSLcuPtp7xOCWxag8rciH4RhnjYX53SMdbvghCiDwwZClB4aHFjVt6dQW-gF9sFd4bIK5Amp29BTR-aVFsC_WSm8ieKxNPara_2pHcH6xsI0LqW5WKNdJKQ2wAQcuhHJU5b-k2kZYF5s03gxbiLNR4okKAEt5_qnLyWDaA3RZVIOWShubHz)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmf0Zlb5ZAgXv59g1Hegcd_ICXBaFc-f1cVbdV4hR97nuG8mpkj9ii9_0jKsqf5S2ZQ7JdYhT-fW0ZE8mXAQo5Z0SnhK8-Z4rEUkCgWaxJG0IMoJBu8V4LIw==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGQubZx0w8DM2-b1cEa3Pp2kmIiR5ad1HffUG_iHVuAI2Yee6JSxro4CnuCU5p2vePORCuDXdVOtgLIZ8oYTVCSQG9l83ubZt9FuasqsXovM4GhZo9XQ==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE8BOwzVyKzSobbyFur76eGCg53D5Nz1mZU0-aMrKQtsfsF0z-jS0EfDD3RSaE4YXGd4D0HIqoCJAQ-ErNa86sIKhfwBqa3EYImdgWW1oaTgkO0Wufw0QvsSA==)
9. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2UWKjapOCYBsbczGNTELtFE2PKrnijeOZpkACJAaRJjYwTmpwW0KIcCpWM897i7I91eayIshjyoIGUbIRnxBgAk08Me0r8aCHoJMqjEm96RMWLOj56JMh4hEVU-uGAbs=)
10. [northwestern.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7lQ9IQoyytZmsDyXdM4J-RIv7csMTmXN7VeJF2erA6znHc5-VHLnkWkVAB7Sgwqtr1ZqVwypcuKo1xB3ZVypRFx2oDMgPVY68xFumTvYK6002CYAArwnWeVLVepju0wg-qvXYZyuDEwJw5HBa4LOahfmy6_rIyR79zeNH5w==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmhNgQR3XEd3fg4NH4ZWBeHIx-2ryvso3X2HDUVwOaHN52zfiq2nAj_pjPXUwB063x8h2hyIaUJxFKT31vBm93Mtu06XZ8n7noUpeUtyBwmLM9QHny8g==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEuh6WFVajvIXQUI9YwGCDUDT9vOrl17U_ezO4xSLqRP-oIQvje_2f-5WZJ3BoKj8rPHv49N8HMLct84vYDGG8n3Z1H67KmebLQwcgo4AfxQe3iksdJXjCqYg==)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGysKMvhrCsGyjut1vf88oVoQlfGG1yAOhV5woVFGLtlAWFVym-IroTVw9NDypy3hFu1o19km43YUKdgTgQqR_v8NRvTSOd6sTMQJy2k56nDU8V3kvQcuJ844ecy4DJCktxnEomXobkx7OuoauN1n95ocJQmBa6FVkUStHkBdiD3A==)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmlyDAEnXMBviape0myykSKZpjw4SdDOZNivaxVMGq0gBJRDYOmCPanbGgn2RXsba7XyH5MdRz7jZwBZE9nmHpTgrelIlhdFgbin8CjAOj84eBGzDNBfKe7mLwpK_mVt_BSdkG10MRBwftaYmzsrvAdFWWrlo1FMAatNs3iuBexUaI9jq92DVBvkKGcobM3p_ti_F2_tFsXBwd6cY_-D4bTG-sAHQFkgDFly8dJKS6xC4eZ8KXnSTOcd3dvFpx5CzenBEApWEwgUXJRDRxMQnSAf4CJ1ULwFRlt0CBDMRPp61kwlX6AbkEPSoW0jn6CeKt4uXa7zmXojYCmCOJYA==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqd4LhQd0gm0rMnhP2Lw3Pb3WG1iBMCuDspzNENBovenZQR3xpOm1x6uNs62nPOG7I07s08yBHxgDSqT4mtEDmrmyyh7XwnEM1wlobjS9OWNUe2NUYmg==)
16. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqrVCFQ7M2H6dSUcBI4CXyd5DdnsIiiwK2foxjIIvuQgQtl6orRwXJOTj2ryqUysvKxos9s6qi9suEF5gROyn6PaPriFfU2gGz6AsI0k2wiso-UDDFxRdCgVXFK8OSR3eOC22LxqMNactyMZ8t7Egr7wdFW1c5t6JFLw==)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYOXM_RvouUxdLkRZjMe6d8Crj3l9jXshdvRzMVuaCYPI_wnJ6eo7Z8B2knqC0kw4zT2th9DxhhPGhPZ48sDQR8hR-Cm6uojQb40ZUZYK54-AkeUW4ozhSQKMkyFHJphNzuaplUwdx7nMJ78Oh_vfd7PdxoF-ALF3Q2__SqEh3jQxjf2WQScpNnr2Za1NB7Lvf0OcGZA3uS7MzoHX4iuQULIZMN8DYQwfqiaeiysd1HHfDIsm-guDdUa3hIslbHH_inWs6qQotQPFNtlABjAa-9AGsKsfTtFisLbkKzGgbpc9tb35pf0N4dg==)
18. [biu.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHiOGHJBA2SnuePa3RLt0gcGNtbkP2L_9tLGOpv8a-t9SSADHTZGJrnd71t5VsEKYW5OSWr1yEWyBzUz3J9fSxCT206E8kyGAsi7LQ3vT1CVsos_x0qm-U=)
19. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGT7yjCgAJiwx9vHeMcHofv0uFzsUjeA07xW4suCK2D8SYSy53JtUkuhpJUg6VLG8SpB3L_ZdO-xgPUOsr3pBtsFt5UCmae6QSJ1YMUmp0iKN-_Dmh0shQ-PffmlruHH7EVMZRl3byTXqhZBzqxJdTNHs7ObJSf_57hLlGa2YtBjPrx0oBmlcnKqfnD0ex_TZLtN9gur8t8pIiS48pK_LZ0_zEY1ez1oHA=)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTE9pflaFKTGHGQsgRVAJvyYzonH4AJbaHilytXwDGkCraTVKoRFGbAvoinmFcgzxgoKO8hprvkVuYkdgptq-OLVat0CLwZCbMJ69Po-GdWDvytplJWCwiR65_to5gfMYmQRAnu3vlRFUMnekIyFFt-CqO_45gvg9D8n5K2zyY)
21. [osu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4RCWmrsBPYtwEbHGmssGaTm4l2u_ez_iKhEVpA4JKXmmvlzZCw5_4YNDKbfbWCfPJMuEy83uixe_-fSUAA9WdYO7kdVe2_Ze53-bqIe1Gy6Eqjto03sgZAM5b_d04L9BRFVRD9URUznHrP8WZ)
22. [cam.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgArI9ETWpRYq5p_e-givIE2OZxms6VOUSiywM5i1csqoWhN6pv8PWuoS2aRNGIll8BF4TvljCFa9IOSu9zSSrPsPqumgU60pH4B_Bn2vv_0glYp5InOGnhP2jpskh2AcCsGZ9kjPEz2iRR_DzO4ROxRXOBGEadky35OkSRuAUSVMEJU57ayGgBwYyt_hLrQ==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF97IiHTIHUq29t0NDO2WMwmpLkid1g75bSU07D8BnEBPaLZYSIN4gvz2mc84qM43pf1-2udgGSsDBxK0-yVntqLSzOOWPuwlyRTiRbImsYx_yp5Qz7StLodg==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHBMQVeJXvKJiWHvETJs1Jcve5UHxP644wvZZtJe2Pbh-n9nU27YW8BrVI86VO6jFbqbuCS3m_aJ1MnTdwTODzoUl_T40PJuL6bKs9OBCZ-YZRK2kLKQ==)
25. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvP0tYY7c8IIFIrR_9Je0N55cp3Ioh_MOIDarTJrQd4RrhkGKpi8NgWQVC3CgTaM6fj0ZMBBmoK5qtkMrSpvq0tpU3nKA4wfJ8wk3jU5nt-N2oczG_TfUc0ji7hGXJLOpcErRC_uNbN4WhAdzZDeyQMLYVdpko8WIAVMIA8zHggnUuoMgIHZu_dVXZaxJCJUb1P0xA2x0AWM_IJTHVHev2BYT2z3s4BbRiNA==)
26. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6JB1V-JRbFU9EYN7PTRTJFERxK6CjeFcJd6-KMlBhRVhKhj0uAgbVZSrcjv3oMF4Fh76AC_jkZpwFRcidzXjuhv5cGhvv8oNjfZGDbOnHSJVSGsMCCuERGaGPJU6GUm0DQtNGXhW5Ab-5f0xuMlGypby7MBK2ylgaaDAT1mFErKS8x93OQpokLGQDLClQMCI6e04Pw6aGbu8r48H06OOWVojYbDUYHGYe5U6u5TvMUAg_sVTSNNKeh10vbsBxcIYQzUXwKuUXea1VYCRcdyShRyo14qjAPJtRE57OQigAjNwCye1ap8FxTCEMJrGWgJXU-Q==)
27. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEY8cQl7a8cMZff_dctJV5pFfNz30p2HXuEI08Oy0hhtfoKFQzv8rbxGzVZJag-aKduyXN2SGDLtNfl-wLymKDjIrQaEyZrxb71Sfc6wGow_bsdo1xIMRg4Cgs26FlFC3gHA3AogX-tnzoDsh5bz5-oxfVhEQsuUC7MViLe7VMosvRwFLjrbWVoKbLr5nG2Jdxdv6c1qpi5IOI7P2_hj2fGM9tEZYw=)
28. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHueLjX_Vt2Dzt4OMoXwwaSHd6lZEAWwM1NqGdaHu6eKb0HUb2iW4znMl-lIla6KuJffQ88DnJ5hM8pHKpQ9LeF9mj9k9-F_QKIjOmNVJFOZhR19bj2PangEWZ0PMnvvBMv7Qse6kVV-yWi)
29. [texmacs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFhgjf6jAUfDmH_ec5U52d89W66_hs3fjEKodTYLGsctrpCyxAd5FrYCDPnzr6o0cy48DOo_xk26DGzE-QGeASrPYl3FJGZGqkwAGW3QmbHGQF-Vd8xVA7D1OQN4lQKA==)
30. [vt.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4EdGFExVLQEBFJBOuBvX9VoeHaU-S7rIv73FH9QD2pHX-DrQDPYDR2atmPo8kKDcfZVjZCswgI_JHT1AqG6JT8H1m10ylBESLoQ4l9yfJ4-ECL4t5dOOslcW5k51eR1XnRMDmgEwUO7TtQ3OxjjkSyOmUhuD7S9v2FjrOHRDq5yyQGRLGKsXiSvlSUQ==)
31. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDSHAt7pHHUh-eYj9kaIar80vqyTfUY9jLY1rwD82obTq-l0k9kbTotpyvSzEBmkmOj329xSJpVtdIT6gqEEiWc1DT_O0oAYWKfGA3I3kR2CRHB1sBfQQUkZ5JsGFx0vPmeZN8Q6qWR14XWKIS3I1V3fIS1Y6w7AtIBrLXY5qGlAJviLA5qsuAllsihZFCG5-xHfox60ocpH891wrO1zi2qnZNWHUnXBw-6uUxWYbN4cyNWjo0Uuq0sn7B14_2ZVfiWA3uAyJFkv4hGsTpgowaAhqkXXflhjzePo8Urcx0z-2HrcxbqJ4943ClgFI1Vut7SlbaOEr284nFoA_-Dg==)
32. [aimsciences.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdPQ8tHcVGnTIP72MRl5Qj3vWVwdIMHSs82dhO82pJ8AsX4Eub5w9s3I8lLRxr4gbXNxIWGZG8u5TiHqGlkP2TaohYoD7AkBc266PRzu_MgTyzPNLK_ww6U8xhUaqWsXI_A7w86IiQI86tCD1io7bRfw==)
33. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPBVmaCLGDostLpNFCxyvOOKZmDz-BTRYbZw4psdW_HxQOYGkpUcuMTtYF3jIfX7HioM_EX2ybptXroxlBYGIVathayxzZnqhvZghn28Qu-3-TURu74vUshg==)
34. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiQFrC3aZkfggk8vOrY1W1QgnIDt6UVpSBee3uQWdzN5iukC-4_EZ2_jBy93P9vxRgR7HCXstmz4yj2chm9X3EJb6RxvYNNWzmhV2bJKoGbMAf2TpFYNaHqFw1-alNqHFRIMaJCULC3ZR3iDjX-0Np4yZu13ykoehnl01oBQHispeVOCj5lnKNRw4N4JSApSFXcA0R1B0jRAl2G-opaqC_3ocwoRXMCOV6m-PQmVEGcfweyXcLNaB8ikcuT1ranvIOEPDsOE5qnsMVXSuPq4MMOUAA1leqEw==)
35. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHViaUbGPmEpDIog4D6ZBqjSrp33mPBftqk-0jwslt68jQLM76AN54xIghn3Hpr2TnrhgTSEML6HFbzOFV_2zoUVBUTzpneT5Y5h0RDtKc04-syL3kYQ==)

