# Siegel zeros and Landau-Siegel zero existence 2024-2026 frontier

**Pythia queue id:** 153
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chc1VElQYXZLdUNjV3VfUFVQdkt1TmlBWRIXNVRJUGF2S3VDY1d1X1BVUHZLdU5pQVk
**Elapsed:** 187s
**Completed at:** 2026-05-21T16:32:33.120276+00:00

---

# The Frontier of Siegel and Landau-Siegel Zero Research (2024–2026)

**Key Points**
*   **Ongoing Revisions by Yitang Zhang:** Research suggests that the highly publicized 2022 preprint by Yitang Zhang, which claimed a weak form of the Landau-Siegel zero conjecture, remains under active revision. By 2024, Zhang acknowledged unresolved issues, and upon his 2025 relocation to Sun Yat-sen University, he stated the revised proof is "nearly complete" [cite: 1, 2].
*   **Conditional Breakthroughs:** It seems likely that the mathematical community is deeply invested in the *consequences* of Siegel zeros. Recent 2025 and 2026 papers show that if these zeros exist, they paradoxically prove major conjectures like Chowla’s conjecture, Sarnak’s Möbius disjointness, and the Twin Prime Conjecture [cite: 3, 4].
*   **Numerical and Analytic Constraints:** The evidence leans toward an increasingly shrinking space where these theoretical zeros could hide. Computations in 2026 have explicitly verified the non-existence of these zeros for moduli up to 2,000,000 [cite: 5, 6], and new zero-free regions have been established for higher-order Rankin-Selberg and triple product L-functions [cite: 7]. 

**Layman Summary**
In mathematics, prime numbers are the building blocks of all integers. To understand how primes are distributed, mathematicians use complex tools called "L-functions." According to the most widely believed theories, specifically the Generalized Riemann Hypothesis (GRH), these L-functions should not have certain types of values evaluating to zero. A "Siegel zero" (or Landau-Siegel zero) is a hypothetical, extremely stubborn exception—a zero that breaks the rules of the GRH. For nearly a century, mathematicians have tried to prove that Siegel zeros do not exist. 

If someone were to prove that a Siegel zero *does* exist, it would break our standard models of prime numbers but paradoxically solve several other impossible math problems as a side effect. Between 2024 and 2026, the mathematical frontier has been split into three fronts: (1) researchers like Yitang Zhang trying to prove unconditionally that these zeros do not exist (or are strictly bounded); (2) theorists charting out what happens if they *do* exist, finding that they would magically solve the Twin Prime Conjecture and Chowla's conjecture; and (3) computational mathematicians using supercomputers and advanced formulas to prove that if these zeros exist, they must be hiding at astronomically large numbers.

---

## 1. Introduction to the Landau-Siegel Zero Problem

The distribution of prime numbers in arithmetic progressions is one of the most rigorously studied domains in analytic number theory. The foundation of this study relies on Dirichlet L-functions, denoted as \( L(s, \chi) \), where \( \chi \) is a Dirichlet character modulo \( q \), and \( s = \sigma + it \) is a complex variable. The Generalized Riemann Hypothesis (GRH) posits that all non-trivial zeros of these L-functions lie precisely on the critical line \( \text{Re}(s) = \frac{1}{2} \).

However, the GRH remains unproven. Unconditionally, mathematicians have established classical "zero-free regions" for \( L(s, \chi) \). For most characters, these regions guarantee that no zeros exist too close to the line \( \text{Re}(s) = 1 \). An exception arises when \( \chi \) is a real, primitive quadratic character. In this specific case, classical techniques cannot rule out the existence of a single, simple, real zero \( \beta \) extremely close to \( s = 1 \) [cite: 4]. This hypothetical exception is known as a **Landau-Siegel zero**, or simply a **Siegel zero**, named after Edmund Landau and Carl Ludwig Siegel, who laid the foundational frameworks for studying them in the early 20th century [cite: 4, 8]. 

The existence of a Siegel zero would be a severe violation of the GRH [cite: 4]. The quality of a Siegel zero is typically quantified by its distance from 1: \( \beta = 1 - \frac{1}{n \log q} \), where a small \( n \) indicates a severe counterexample to expected zero-free regions [cite: 8]. While it is overwhelmingly expected that Siegel zeros do not exist, the inability to prove this unconditional non-existence—often referred to as the "no Landau-Siegel zeros conjecture"—remains one of the most formidable barriers in modern number theory [cite: 4, 9]. 

From 2024 to 2026, the frontier of research concerning Landau-Siegel zeros has experienced intense activity across multiple distinct avenues. These include conditional theoretical frameworks that map out the bizarre arithmetic consequences of their existence, heavy numerical computations aimed at pushing the lower bounds of where such zeros could hide, extensions of zero-free regions into automorphic and Rankin-Selberg L-functions, and the highly anticipated, heavily scrutinized efforts of Yitang Zhang to establish a definitive bound.

## 2. The Theoretical Framework and Classical Bounds

To appreciate the progress made between 2024 and 2026, it is vital to understand the historical bounding of the problem. Page's theorem (1935) proved that there exists at most one exceptional character modulo \( q \) that could possess a zero near \( s = 1 \), and this zero must be real [cite: 6, 10]. Furthermore, Siegel's theorem (1935) established that for any \( \epsilon > 0 \), there exists an ineffective constant \( C(\epsilon) \) such that \( L(1, \chi) > C(\epsilon) q^{-\epsilon} \), which translates to a bound on the zero \( \beta \). The major drawback of Siegel's theorem is its ineffectivity; because the constant \( C(\epsilon) \) cannot be explicitly computed, it drastically limits algorithmic and practical applications in prime distribution theories, such as providing effective bounds for the class number problem [cite: 10, 11].

The presence of a Siegel zero profoundly distorts the distribution of primes in arithmetic progressions, leading to a phenomenon known as Chebyshev's bias and affecting the error terms in the Prime Number Theorem (PNT) [cite: 10, 12]. Without exceptional characters, the error term in the PNT for arithmetic progressions could be explicitly bounded. However, if a Siegel zero exists, the error term is dominated by an exceptional term: \( - \chi(a) \frac{x^\beta}{\beta} \), creating massive discrepancies in the counting of primes up to \( x \) [cite: 10].

### 2.1 The Deuring-Heilbronn Phenomenon
A fascinating theoretical consequence of the existence of a Siegel zero is the **Deuring-Heilbronn zero repulsion phenomenon**. If a Dirichlet L-function possesses a zero extremely close to \( s = 1 \), this zero effectively "repels" all other non-trivial zeros of all other L-functions away from the line \( \text{Re}(s) = 1 \) [cite: 8]. 

In recent years, explicit quantitative formulations of this repulsion have been refined. By 2024 and moving into 2026, research has demonstrated that if there is a real zero \( \beta_1 > 1 - \frac{1}{10 \log q} \), all other zeros \( \rho = \beta + i\gamma \) in the critical strip are pushed significantly to the left [cite: 8]. A 2026 explicit improvement on the Deuring-Heilbronn repulsion by modern researchers provides a sharp convexity estimate for L-functions, asserting that this repulsion acts uniformly across the entire critical strip and establishes effective rates of convergence for quantum unique ergodicity in certain automorphic forms [cite: 5]. 

## 3. Yitang Zhang’s Claims and the 2024–2026 Status

Few developments in number theory have captured public and academic attention quite like the work of Yitang Zhang. In 2013, Zhang transitioned from relative obscurity to international acclaim by proving the first finite bound on the least gap between consecutive primes, a massive step toward the Twin Prime Conjecture [cite: 13, 14]. Following this triumph, Zhang turned his attention to the Landau-Siegel zero conjecture, a problem he had previously attempted to solve in an unpublished, flawed 2007 preprint [cite: 9, 13].

### 3.1 The 2022 Preprint
In November 2022, rumors circulated, and subsequently, Zhang uploaded a 111-page preprint to arXiv titled "Discrete mean estimates and the Landau-Siegel zero" [cite: 9, 10]. Zhang claimed to have proven a weak, yet incredibly significant, form of the Landau-Siegel zero conjecture. Specifically, he established that there exists an absolute, effectively computable constant \( C_1 > 0 \) such that \( L(1, \chi) > C_1 (\log q)^{-A} \), where he conservatively chose the exponent \( A = 2022 \) [cite: 10]. 

While this did not completely rule out Siegel zeros to the extent that the GRH would demand, it constituted a monumental improvement over existing lower bounds, effectively replacing the ineffective \( q^{-\epsilon} \) in Siegel's theorem with an explicit logarithmic bound [cite: 9, 10]. If verified, Zhang's result would reduce several profound open problems—such as classifying discriminants of binary quadratic forms with one class per genus—to a finite, albeit massive, computation (e.g., discriminants with lower bounds exceeding \( 10^{25734} \)) [cite: 10].

### 3.2 Expert Scrutiny and the 2024 Revision
Unlike the Mochizuki/abc conjecture situation, Zhang’s paper relied on conventional analytic number theory methods, leading experts to anticipate a relatively straightforward, though arduous, peer-review process [cite: 9]. However, shortly after its release, mathematicians, including Terence Tao, noted typographical and structural issues within the text [cite: 1]. As 2023 passed without formal publication, the mathematical community maintained a polite silence, recognizing Zhang's historical capability but also acknowledging his past track record of publishing flawed, unfixable proofs prior to his 2013 breakthrough [cite: 1].

In late May 2024, Zhang provided a crucial update during an interview with a Chinese magazine. Addressing the silence surrounding the paper, he explicitly stated: "I found that there are still some issues with the first draft of my paper on the Landau-Siegel Zeros Conjecture, at least in several places not clear. I am currently still revising this paper" [cite: 1]. This confirmation served as a "soft retraction" of the immediate finality of the 2022 preprint, though it affirmed that the overarching strategy might still be viable and that Zhang was actively working to repair the logic [cite: 1, 15].

### 3.3 Relocation to Sun Yat-sen University (2025)
A major biographical and institutional shift occurred in mid-2025 that further contextualized Zhang's ongoing research. In June 2025, at the age of 70, Yitang Zhang left his decade-long post at the University of California, Santa Barbara, and returned to China full-time [cite: 16, 17]. He joined Sun Yat-sen University (SYSU) as a professor at the newly established Institute of Advanced Studies Hong Kong, intending to reside in the Guangdong-Hong Kong-Macao Greater Bay Area [cite: 16]. 

In a subsequent interview with the *National Science Review* in September 2025, Zhang explained his motivations for returning to China, citing the rapid advancement of Chinese science and his desire to mentor the next generation of mathematical talent [cite: 2, 18]. When asked specifically about his research status regarding the Landau-Siegel zeros, Zhang provided an optimistic update: "I currently have an important paper in progress on Landau-Siegel zeros, which is nearly complete. I hope to finalize it at SYSU—it shouldn't take long" [cite: 2, 18]. 

As of the close of 2025 and into 2026, the mathematical community awaits the formalized, corrected version of Zhang's "Discrete mean estimates" paper. The frontier remains poised on the edge of this potential unconditional breakthrough.

## 4. Conditional Frontiers: The Arithmetic Consequences of Siegel Zeros (2024–2026)

While unconditional proofs regarding the non-existence of Siegel zeros remain elusive, a highly productive frontier of research revolves around *conditional* theorems. These studies operate under the hypothesis: "Suppose a Landau-Siegel zero actually exists; what happens to the rest of mathematics?" 

Because of the severe analytic distortion caused by a Siegel zero, assuming its existence frequently forces other structural regularities in arithmetic functions. It is a well-known paradox in analytic number theory that assuming the existence of this "bad" zero allows mathematicians to unconditionally prove—by contradiction or dichotomy—other massive conjectures [cite: 4].

### 4.1 The Twin Prime Conjecture and The Parity Problem
One of the most famous conditional results is Roger Heath-Brown's 1983 theorem, which proved that if there exist infinitely many Siegel zeros, then the Twin Prime Conjecture must be true [cite: 4, 19]. This creates a logical dichotomy: either there are no Siegel zeros, or there are infinitely many twin primes.

Furthermore, in 2020, Andrew Granville applied the hypothesis of Siegel zeros to the "parity problem" in sieve theory. Sieve theory is notoriously unable to distinguish between integers with an even or odd number of prime factors. Granville showed that, under the assumption of the existence of Siegel zeros, the general upper bounds for sieving intervals are mathematically optimal. Thus, the extra factor of 2 that plagues the linear sieve is not an artificial limitation of human methodology, but an inherent mathematical barrier tied to the potential existence of these zeros [cite: 4].

### 4.2 The Chowla Conjecture
The Chowla conjecture concerns the Liouville function, \( \lambda(n) \), which equals 1 if \( n \) has an even number of prime factors (counted with multiplicity) and -1 if \( n \) has an odd number of prime factors [cite: 3]. The conjecture states that the values of the Liouville function are essentially random, and it should exhibit negligible correlations with its own shifts. Mathematically, for any distinct non-negative integers \( h_1, \dots, h_k \), the sum \( \sum_{n \le x} \lambda(n+h_1) \dots \lambda(n+h_k) \) should be \( o(x) \) [cite: 19].

Between 2021 and 2026, Jake Chinis, alongside researchers like Mikko Jaskari and Stelios Sachpazis, made profound strides linking Siegel zeros to the Chowla conjecture. In a paper published in the *Journal of the London Mathematical Society* (accepted late 2025, published early 2026), Chinis extended the work of Germán and Kátai to higher dimensions. He proved that **assuming the existence of Siegel zeros, Chowla's conjecture on \( k \)-point correlations holds at infinitely many scales** [cite: 3, 11, 20]. 

The core idea relies on the continuity of L-functions. If \( L(\beta, \chi) = 0 \) for a \( \beta \) very close to 1, then \( L(1, \chi) \) must be extremely small. Since \( L(1, \chi) \) can be expressed as an Euler product over primes, this implies that the product must be abnormally small. In conjunction with Mertens' theorems, this forces the character \( \chi(p) \) to equal -1 (and thus mimic the Liouville function \( \lambda(p) \)) for a vastly disproportionate number of primes [cite: 19]. By utilizing this forced pseudo-randomness, researchers can bound the correlation sums of the Liouville function. 

Jaskari and Sachpazis (2025) published a paper in the *Mathematical Proceedings of the Cambridge Philosophical Society* further refining this conditional approach. They established a highly non-trivial bound for the sums \( \sum_{n \le x} \lambda(n+h_1) \dots \lambda(n+h_k) \) within specific intervals that depend on the modulus \( q \) of the character linked to the hypothetical Landau-Siegel zero. Their work improved upon previous bounds set by Chinis, Tao, and Teräväinen [cite: 19].

### 4.3 Sarnak’s Conjecture on Möbius Disjointness
An immediate, striking corollary of proving the Chowla conjecture at infinitely many scales is the resolution of Sarnak's conjecture on Möbius disjointness. Sarnak's conjecture states that the Möbius function (and by extension, the Liouville function) is asymptotically orthogonal to any deterministic sequence—specifically, sequences generated by topological dynamical systems with zero entropy [cite: 11, 20]. 

Chinis’s 2026 findings formally outline that, as a consequence of the conditional validity of Chowla's conjecture, **Sarnak's conjecture on Möbius disjointness also holds at infinitely many scales, provided Siegel zeros exist** [cite: 3]. This establishes an intricate web of dependencies: the failure of the GRH (via a Siegel zero) would inherently enforce strict chaotic/random behaviors in multiplicative functions, thereby solving major outstanding problems in ergodic theory and arithmetic statistics [cite: 11].

## 5. Unconditional Progress: Computations and New Zero-Free Regions

While theoretical conditional logic flourishes, the practical, algorithmic side of number theory continues to push the boundaries of where a Siegel zero could physically exist. 

### 5.1 Numerical Computations up to Modulus 2,000,000
In February 2026, researchers published an algorithmically rigorous paper titled "Numerical Computations concerning Landau–Siegel Zeros" [cite: 6]. The standard zero-free region formula requires that for a modulus \( q \ge 3 \), there is at most one real zero \( \beta \) close to 1. The 2026 study explicitly verified that **no Dirichlet L-function with a modulus \( q \le 2,000,000 \) vanishes at its central point**, nor does it possess a Landau-Siegel zero violating the explicitly derived constants [cite: 5, 6].

The authors utilized explicit computations involving sums over primes weighted by Dirichlet characters, \( \sum_{p \le x} \chi(p) \log p \). Interestingly, the known asymptotic behavior of these sums is itself entangled with the potential existence of Siegel zeros. To bypass the circularity that would prevent the algorithm from terminating unconditionally, they utilized assumed bounds to refine the explicit calculation, achieving a verification runtime of \( O(q^{0.444}) \) for sufficiently large \( q \) [cite: 6]. This builds upon 2023 numerical estimates by Languasco, which previously bounded Dirichlet L-functions for odd primes \( q \le 10^7 \), yielding constraints like \( L(1, \chi) > 0.0125 \log q \) and \( \beta < 1 - \frac{0.0092}{\log q} \) [cite: 8].

### 5.2 Automophic and Rankin-Selberg L-Functions (2026)
Beyond classical Dirichlet L-functions, the frontier of zero-free regions has rapidly expanded into higher-order L-functions, specifically Rankin-Selberg convolutions and triple product L-functions. In the absence of the GRH, ensuring that these generalized L-functions do not possess exceptional zeros is critical for arithmetic applications, such as the quantum unique ergodicity of Hecke-Maass forms [cite: 5, 7].

In January 2026, an exhaustive study established standard zero-free regions with **no exceptional Landau-Siegel zeros for several new families of Rankin-Selberg and triple product L-functions** for which modularity is not yet fully known [cite: 7]. The researchers eliminated exceptional zeros for highly complex mathematical objects, including:
*   \( L(s, \text{Sym}^2(\pi) \times \pi_0) \)
*   \( L(s, \text{Sym}^3(\pi) \times (\text{Sym}^2(\pi') \otimes \chi)) \)
*   \( L(s, \pi \times \pi' \times \pi'') \)
*   \( L(s, \pi \times \text{Sym}^2(\pi') \times \text{Sym}^2(\pi'')) \) [cite: 7].

These results rely heavily on generalized versions of Watson's triple product formula and Kuznetsov trace formulas [cite: 21, 22]. They prove that if an exceptional zero does exist for something like \( L(s, \text{Sym}^4(\pi) \otimes \chi) \), it must be a zero of a self-dual abelian factor. Because no such factor exists when the representation \( \pi \) is octahedral or of non-solvable polyhedral type, the Landau-Siegel zero is entirely eliminated for these classes [cite: 7]. This provides deep structural constraints, showing that as the complexity of the L-function increases, the mathematical "room" for an exceptional zero to exist is structurally annihilated.

## 6. Interdisciplinary Applications: Chaotic Dynamics and Engineering

An unexpected and somewhat unconventional frontier in the study of Landau-Siegel zeros emerged around 2023–2024 through the work of Rafik Zeraoulia. Exploring the intersection of analytic number theory, fractal geometry, and quantum chaos, Zeraoulia published findings in the *European Physical Journal Plus* that translated Yitang Zhang's recursive, discrete mean estimate framework into a stochastic complex dynamical system [cite: 23].

This research treated the Dirichlet L-functions and the hypothetical Landau-Siegel zero as variables within a nonlinear map with additive noise, dubbing the resulting system "Yitang dynamics" [cite: 23, 24]. The dynamic behavior of this system revealed profound mathematical chaos, characterized by positive Lyapunov exponents and high entropy [cite: 24]. 

Remarkably, Zeraoulia's work proposed that this spectral-dynamical approach offers indirect support for Zhang's theorem while simultaneously mapping these chaotic dynamics to practical applications in electrical control theory [cite: 24]. By exploring the instability of fixed points within electrical systems, the research suggested that the chaotic frameworks derived from the Landau-Siegel zero distributions could be harnessed to address real-world engineering challenges, such as optimizing the implicitly restarted Arnoldi method (IRAM) for computing eigenpairs of large sparse matrices in control circuits [cite: 23, 24]. While this sits at the periphery of mainstream number theory, it exemplifies how the abstract hunt for a zero on the complex plane can inspire mathematical modeling in applied physics.

## 7. Conclusion

As of 2026, the existence of the Landau-Siegel zero remains one of the greatest unresolved mysteries in mathematics. The frontier is characterized by a dual reality. On one side, massive computational efforts and structural algebraic proofs (like those in Rankin-Selberg L-functions) continue to squeeze the numerical and theoretical space where a Siegel zero could exist, rendering its existence increasingly improbable [cite: 6, 7]. 

On the other side, Yitang Zhang continues his meticulous effort to finalize an unconditional proof against their existence at Sun Yat-sen University, aiming to cement his legacy [cite: 2, 16]. Simultaneously, researchers like Jake Chinis have brilliantly demonstrated that the universe of mathematics has a fallback plan: if the GRH fails and a Siegel zero exists, the resulting mathematical anomalies will perfectly align to solve the Chowla conjecture, Sarnak's conjecture, and the Twin Prime Conjecture [cite: 11, 20]. Whether banished entirely by unconditional proof or utilized as a conditional skeleton key, the Landau-Siegel zero remains the pivot point upon which modern analytic number theory turns.

**Sources:**
1. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYd5FtG40qgUhNheOdnEF2kuYy04fcJrTpNs-Cy7k5Zc2ylinYsNHYGLF-wqxYyvELb6q2MZl9c52mgxzkD9x1ng9TucHr8Qcbwj5Z267IrmuIepAC1FNfzdZUCZPkO_HlvpCSFbWPFmEWC4CsFxFMOuNIHmOFFpwUHesT7QXosE-FF0QYKps-SNJUjYYAtwbQfRQaWNI=)
2. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsol7ym7jk9FJTEWJCgwMA0vFTyNgEDO5AF2gZ6MAe_98BJQs32mzZTLyl_TJaPvZMRr6-5xHduWcQwUm6rtOVY7MQ8ntLY17AEjd6Ge3PsCEdpkVYQnRT4E8kjJdR98EXxHo1eQfazxr_FfqIKi-z)
3. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBV3INbydsEbcS1y2vZoAQ0vfxZ_rLSC_9lGuIQLTvgoVtvKfQhCZxugVLHcgndUpe54qYxfSooRQZGGSj5vfKKVP6eWzPeMuKO-Yr2rG80Ssm7i2JQJmLoC12MrvjUcDSz25nh8iStG086eMrLcUJmPNc9lZDHFIiAeP0klXcoJIEOci-WvZ3FS4XVEY=)
4. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEIWXwbLfdO1rBE2IAp76RWXi4a3XuWHI1FQd9OSSilDCvInNs4YKMVU_7oAdlwY1VFi3_8hYq6yEJR-hTNozMqNaJuRJFMUIk4LFjir4A5AhQxLDJ2EmuMf5vgezcLfg==)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE05oiGl1ZJ9tJmIO7A2m9d65F9a63qs_GuVEy-9ko2SDthUig-vAZDbQhybb1cg5Q12PprJpRX3jgN4pwgeOigDMm3H1qXmQeKEzNI6Xh_eewf8sj381lX81ZACi19FknftB2pxyyrChPWqvY55p8T3aJmQNMVsxotMlgMEaU9GymNQadoOmCEOZlCm8IHaGoLbdoKyB-i-AdNcCPtkQ==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKq93z7WTOfJxpWX3xk9ueQ_fHSadZCmTNyLlrTFNAGtMgg2Ou3JQO9Xmmd40N6vW-_bxUAUVfoxHi6NyRFa1jmrFiNdOwU39Vnk3bjfXNlYlWfFfd-oBjeA==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3EMm6Kos-nYpqFCEYHwBFSrsgfD4vlk_VwhvCm08Pm3OcCmDQRzeYR-hCnldFsA6kLCOvnEjIVVPr91Gsu1nmbiezazJY7LuCAMRSp_yO9pDobaUpxA==)
8. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXli1F4Zl5rRGqQeAZVOXEpk52BVZruBBAPY3UEUz0h4NuM3WpNyKrXzXaWTUOkXXBJlWE_yKUqA5BtcFV36H0SL3PwLT6rxVkBkUVlcEw8b54SlMPru-QZJrX1s4R1RT6d4N93sBssWilSuA=)
9. [columbia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwb8bDFJIrA7Nzjnt22XqeWW3d9wqXgo4cWQvFAHlqOM5F_kokMIXDYN1Fh-MefKx0syyl2h6wZ4V7ZL-uXow_PlK3jL4NS8Sp6KpzOY7zKc1OOPUG4zAHbDjitzcUYfNKqlYurKmoQ1MS-I4=)
10. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdHLBltoJyrIj--aTzwsE4FcN4FV5Z6IiTxwAVivuYV4KbA0fPYBMpvyi2Vps4XAGyG1MtDO0agx-0uXs3qgjeUqs-0W9lnWlriQmZIhrv8Z7h8CfvalEvh9iCKldt6mjSL144gMRdAXeLlPCFVuM1tJ6JXI4e6oprdeBVsGIK-u-6B4DDa987hn6mk5s7MqYv5pBTSPCNyj8sWtw0-mIyewRkpRH9w-yQ4Wgex6_8)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETy3n2-r4UVfDWV0DqWzn7wX_Onf9dTj4oh1LXWiZvUUGXvcuDgj1JP58Wmyst_LH_hu4iZzvr7aE5sQTWAIQ9ThLbizGpx0xHzvvI7w0gbPrl38P2lg==)
12. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVniIMqk-olzVPt2XHZWqDTyKvzUa-__gquaUq7w4xktneukT2-cm5XWMYNudp6bCcxTTpeV2EBvJf5TkSikjlZ5t1-z0pH1m0xot-ab3ToCAtShwyw1IsCPecgq9SPMLQS-z3BRnUu1JxcRrE_1uEzc2oJIFDoiZG_ng5IzNc8shio9FJgE1w2Llc7wnmD1F8EEa27HrdE0O5aw==)
13. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhjM30MLPzJlrftwEff2n05pX5BOdSL91GnhEoWDJVwydJhApbKtNiS0bv8HaDH3UrlGxc_CwNyo-M4wy_jJ-K6MNZ60jEqir04gCDtaEL5GSTD0KfvnTDAr70Wvf2gyc=)
14. [quantamagazine.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHz2CvCHoSGD5sVmyIPQV0J38XTgMkMoN-eHyAsKVItCtbT_OogPVASjQyBxq-YwVHtfDvVLGuWYLnEtYaeXGTewZDUi4Iescx6TgWLBWBiinXsJ4g6CMAIhgWVS_1io6MP8YfFBzJkrp3vJXlT-hs6WTEbSe3se6D6S2caqu2U4LrtpkaC1blGYkwB8K11M7Xa1OjLNfT4LbTZLrprKDQkDMW4w==)
15. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJz9jQaW5zVVshPAVLhlfqm7qvu1BJHyAAtUGAeIXRzQ9LVl44K1JrVcEhLsZEiBqOCvK4qJjl9Yi_WrQ-_zzpcPBMEVkgzq85N-zzBLHmO3pGkHcjEs-rU_abYuw2bkPugGqoXr4slPhONWGGRUMa091FFK31iUWQjhZLXEGyqGIcsBPVJw==)
16. [sysu.edu.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQED9Ae6NPXQN_lPb2ozRII84ADpkRd73xnxFCQM8apiasLhf0VJE7vugLoMTUhEtDK6d9V4Htbn5hiVviZCJ7V02r8Ze7BB_rlAcijbjQc3i1sjLUh67lCz38KP1x2mOPBWdN2FEC7nHf4=)
17. [scmp.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxyR5avHbbtG3YMCeEY7hmi0u5bLK6e7S2728JI8BdzCalcCz89O4yB60G69B8yMPujCcjWLTvoRUUJ1RDXKsCrZd8FaVTOktVXCkELghcGmla6siPzP9Xk_q38_xk4YAwTCgj_4DcFZPHU5rX8vz_ZWzndHufvCPAyrx_Elg5HTYZMWIEc_hepHJg_tlrGyC2w4RkVW2CEoDAzuRbPNKUdGlbpTmG9Z-lSxfMaB5UuqBFVhbkzfQ=)
18. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJnzwb9dyybSfLPtcI-pszS-AGc9s6ghaqLSv4j2qkY4B92uS_0l991RFxj6kvh8nAfabu40B5DcspLNC1eXli23evtY85MZri07FD6jB2RUQE9p0lMjbLg8b7caRT2QGWSmAELHi-tw==)
19. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwGjvih5f6vYZs2Y_HM0PyM5buRXntFmoLr9wOY9QDrogwmLwEnpz6OlAmsTEof0-gkg6F4G9HdqBhPjzesPEMiy-sPaA5w1Zrwbq18KpnHKnkuDkOH51Z07CsoiLRJEc51qSrvhoPPuMOjMucVGxFMeNdQS4zilmdmhqs5drhOqYA91DQ_X6nuaMelZYKhiSKRUFArDt8OgIRLCxk6eYxLsdxFjXZcleUGiBT9-AmmrInvziBS7bRbKEX8yxHhrFa7n3d5on0EdyKmGH3UxmVY7xUtluotoRqbC_8RZe7WIqdmQXPBDb8m4ND5NF7jS0n)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1n8qAzODu2eXauZp_rN-ufXGoZ89ENMmlQCA4Uy2PSPh8gINrMd_6hSkFuV1rb0Xx-OHVISjLfS-7a-OtBTM1FSBfdgpdNcEmF-bXITk0cblAn_1FxG3oAj6yVUPK_yn2xFmzQWsj7ipb6LbCFh6uNe1shABOgNnllk5jpyxtoHNI)
21. [ethz.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJGfE4_IlKUbWU38O-DZ2kWejn3KTEAgeo7mQ1Nlitcq5-JE_4nzct0UKLxWr3qgC-GouQ7MmTP4W_FIgQ2Pvng9Cb2MX7gwpRtDMUoMhb9xroq_Re6U8NbQ-Q7IaYbE-s2WynPxY7ggM0EeWQvQ==)
22. [cornell.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtdzXyOaj_nvnJzmwdvGu8Kx7oA5AmEFxqXyQcmd8XxN8uw96hsIDTGhrZm6ckQMEW9iG2yNNjD4fhBBq8_K3Naw5QqnR4QH1O57FIX6blLTF5o3qALmUtRtbsLf7pOUg-lUqdqYrNiQIIOuO7pnJwGJSSxgLepHSHVg==)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmUsi5qrSkKHNVzGX0RSKBD-0CnAo1ncbCDVy4gob6OkqBFGIcuiIRBEYjXgM-4JtPJcUcH_Iy6kbimKRgJU7-nfz0J9lINK47-HYWTeqlfg8jYSxgIBtd-mZSEMPpKvjCW4G6NhM70P4H6YwWwz-Z-c2EZRPyNUI4SI1499BtYCReq3Uor9WU-a3_nGIzmJKz81-Zh3-a6rgENd5vuK-37WF-W3hLmyE49JtchX6N97TMKWV_3hWgLzlMdVKqFvDi4eE2wrgQDleLPotcRZTNNA9Ej3GO2Jy4dxIEdUY8gw-4zWZZSQ3Zdt87IDa0)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFggsWPh6er-S_b_4x2Zp9sna_i2RIMxH2oShse_fo-XT0t5J5_0Z8dA8DC7mxj9BIj09iArZS2GhyAxEvtvtG_lHKv-qaq9E-Vl43DYkKxQpBZQKPwnA==)

