# abc conjecture status 2024-2026 (Mochizuki-IUT debate, classical attacks)

**Pythia queue id:** 180
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdhendQYXIzdUNJN04xTWtQZ19pcjRRSRIXYXp3UGFyM3VDSTdOMU1rUGdfaXI0UUk
**Elapsed:** 252s
**Completed at:** 2026-05-21T17:14:16.415686+00:00

---

# Comprehensive Status Report on the abc Conjecture (2024–2026): The Mochizuki-IUT Debate and Advances in Classical Attacks

**Key Points:**
*   **The *abc* Conjecture:** Formulated in 1985, the *abc* conjecture remains one of the most profound and central open problems in Diophantine analysis, seeking to bridge the additive and multiplicative properties of integers.
*   **The Mochizuki-IUT Controversy:** The mathematical community remains deeply fractured over Shinichi Mochizuki’s 2012 claim to have proven the conjecture using Inter-universal Teichmüller (IUT) theory. The consensus outside of his immediate circle is that the proof contains an insurmountable logical gap.
*   **The Joshi Intervention (2024):** Mathematician Kirti Joshi published extensive preprints attempting to bridge classical arithmetic Teichmüller theory and Mochizuki's IUT, claiming to salvage the proof. Mochizuki vehemently rejected this in a 167-page rebuttal. 
*   **Financial Bounties and Sociological Fallout:** In 2024, the controversy escalated with the creation of the IUT Challenger Prize ($1,000,000 to disprove IUT) and the IUT Innovator Prize ($100,000 awarded to Mochizuki and his co-authors), intensifying the sociological schism.
*   **Classical Breakthroughs:** Bypassing the IUT drama entirely, mainstream number theorists have made historic, unconditional progress. Hector Pasten utilized Shimura curves to establish subexponential bounds, while Jared Duker Lichtman proved that the *abc* conjecture is true for "almost all" integer triples.
*   **Future Outlook:** As traditional peer review fails to bridge the IUT divide, some mathematicians are turning to automated computer proof assistants (like Lean) to objectively parse the logical foundations of the theory.

**Summary for the General Reader:**
The *abc* conjecture is a beautifully simple equation—if $a + b = c$, and the numbers share no common factors, then the prime building blocks of the product $a \times b \times c$ are rarely much smaller than $c$. Proving this would automatically solve a host of other famous math problems, including Fermat's Last Theorem. Since 2012, the math world has been locked in a bitter stalemate. Japanese mathematician Shinichi Mochizuki published a 500-page proof using entirely new math, but leading experts concluded it was flawed. 

Between 2024 and 2026, this academic debate evolved into a highly publicized saga involving $1 million bounties, blistering 167-page insults, and a deep geographical divide. Yet, mathematics marches on. Working completely independently of Mochizuki's contested theory, researchers like Hector Pasten and Jared Duker Lichtman have recently achieved major, uncontested breakthroughs using established classical mathematics, bringing us closer to understanding the true nature of addition and multiplication.

---

## 1. Introduction to the abc Conjecture

The *abc* conjecture is a cornerstone of modern number theory. Formulated independently by Joseph Oesterlé and David Masser in 1985 [cite: 1, 2], the conjecture emerged from attempts to understand the Szpiro conjecture regarding elliptic curves, which heavily features geometric structures [cite: 1]. The *abc* conjecture translates these deep geometric relationships into a purely arithmetic statement concerning the interplay between the operations of addition and multiplication. 

### 1.1 Mathematical Formulation
The conjecture is stated in terms of three positive integers $a, b,$ and $c$ that are relatively prime (meaning they share no common prime factors other than 1) and satisfy the additive equation $a + b = c$ [cite: 1, 2]. 

The core of the conjecture involves the concept of the *radical* of an integer, denoted as $\text{rad}(n)$. The radical is defined as the product of all the distinct prime factors of $n$ [cite: 3, 4]. For example, for any prime $p$ or its powers ($p^2, p^3$), the radical is simply $p$ [cite: 3].

The *abc* conjecture essentially posits that the product of the distinct prime factors of $abc$, or $\text{rad}(abc)$, cannot often be much smaller than $c$ [cite: 1, 4]. More formally, for any chosen positive real number $\epsilon > 0$, there exist only finitely many triples of coprime positive integers $(a, b, c)$ with $a + b = c$ such that:
\[ c > \text{rad}(abc)^{1+\epsilon} \]
[cite: 3, 4]. 

Alternatively, the conjecture implies the existence of a constant $K_\epsilon > 0$ such that for all such triples, the following inequality holds:
\[ \text{rad}(abc) > K_\epsilon \, c^{1-\epsilon} \]
[cite: 5, 6]. 

When a triple violates the general expectation and yields $\text{rad}(abc) < c$, it is referred to as an "*abc*-hit" [cite: 2]. A classic example is $1 + 8 = 9$. Here, $a=1, b=8=2^3, c=9=3^2$. The product $abc = 72$, and $\text{rad}(72) = 2 \times 3 = 6$. Since $6 < 9$, this is an *abc*-hit [cite: 2]. The conjecture does not forbid *abc*-hits; rather, it states that as the threshold becomes stricter with the $\epsilon$ power, the number of exceptions becomes finite [cite: 2].

### 1.2 Profound Consequences in Mathematics
Mathematician Dorian Goldfeld has described the *abc* conjecture as "the most important unsolved problem in Diophantine analysis" [cite: 1]. Its verification would serve as a master key, immediately resolving numerous standing conjectures and theorems in number theory. 

If the *abc* conjecture is true, it provides a much simpler proof for Fermat's Last Theorem, which took Andrew Wiles centuries of collective mathematical scaffolding to prove in the 1990s [cite: 1, 3, 7]. It would also resolve the Beal conjecture (a generalization of Fermat's Last Theorem), provide an effective version of Siegel's theorem about integral points on algebraic curves, imply Roth's theorem, and resolve the Erdős–Ulam problem regarding dense sets of Euclidean points with rational distances [cite: 1]. Because it acts as an "anabelian gateway to Diophantine geometry and analytic number theory," its resolution has been the ultimate prize for modern mathematicians [cite: 8].

---

## 2. The Mochizuki-IUT Controversy: Context and Escalation

While standard approaches to the conjecture struggled to bypass exponential bounds, the mathematical landscape was shocked in August 2012 when Shinichi Mochizuki of the Research Institute for Mathematical Sciences (RIMS) at Kyoto University uploaded four preprints claiming a complete proof of the *abc* conjecture [cite: 1, 7, 9]. 

### 2.1 Inter-universal Teichmüller Theory (IUTT)
Mochizuki’s proof was built upon a sprawling, entirely novel theoretical framework he called Inter-universal Teichmüller theory (IUT or IUTT) [cite: 1, 9]. The theory, spanning over 500 pages of dense, highly idiosyncratic notation, reconstructs arithmetic geometry from the ground up. It introduces concepts such as "Hodge theaters," "Frobenioids," and "canonical splittings of the Log-theta-lattice" to extract bounded volume estimates [cite: 10, 11, 12]. 

The critical point of the proof lies in **Corollary 3.12** (also known as Mochizuki's inequality), which explicitly bounds the degrees of certain line bundles associated with elliptic curves, from which the *abc* conjecture is derived [cite: 7, 12].

### 2.2 The Scholze-Stix Rebuttal and the "RCS"
The mathematical community struggled to penetrate Mochizuki's writing. In 2018, Fields Medalist Peter Scholze and Jakob Stix traveled to Kyoto to discuss the theory with Mochizuki directly [cite: 13, 14]. Following this meeting, Scholze and Stix authored a definitive report stating that IUT contained a fatal, unbridgeable logical gap specifically in the proof of Corollary 3.12 [cite: 12, 13, 14]. They argued that Mochizuki's mechanism for comparing different "Hodge theaters" failed; when mathematical objects were identified across these theaters to force commutativity, the resulting bounds became trivial and could not prove the conjecture [cite: 14, 15].

Mochizuki firmly rejected their conclusions. He argued that Scholze and Stix were invalidly reverting his theory to conventional arithmetic geometry and destroying the "indeterminacies" and "multiradial" representations that define IUT [cite: 15]. He dismissively labeled their conventional approach the "Redundant Copies School" (RCS) [cite: 3, 15]. 

Despite the widespread global consensus that the proof was flawed, Mochizuki's papers were published in March 2021 in *Publications of the Research Institute for Mathematical Sciences* (PRIMS)—a journal where Mochizuki himself serves as editor-in-chief, though he reportedly recused himself from the review process [cite: 9, 16]. This publication formalized an unprecedented geographic and institutional schism in mathematics [cite: 15].

---

## 3. The Joshi Intervention (2024)

By early 2024, the mathematical world outside of Kyoto viewed IUT as a dead end. However, mathematician Kirti Joshi (University of Arizona) introduced a highly controversial middle ground [cite: 3]. Joshi believed that while Scholze and Stix were correct that Mochizuki's specific execution was flawed, Mochizuki’s underlying intuition possessed genuine mathematical value [cite: 7].

### 3.1 Arithmetic Teichmüller Spaces and the "Rosetta Stone"
Between 2021 and 2024, Joshi uploaded a series of preprints developing a theory of "Arithmetic Teichmuller Spaces" [cite: 10, 17]. In January and March 2024, he released preprints boldly claiming to provide a complete, corrected proof of Mochizuki’s Corollary 3.12, and consequently, the *abc* conjecture [cite: 7, 10, 12, 18]. 

Joshi provided what he termed a "Rosetta Stone," establishing a parallel reading of Mochizuki’s IUT and his own Arithmetic Teichmüller Theory [cite: 10, 19]. He argued that Mochizuki failed to properly define "arithmetic holomorphic structures," leading to the gaps Scholze identified [cite: 7]. By supplying these missing structures, Joshi claimed to organically glue the Hodge-theaters and Frobenioids together, fixing the critical flaws [cite: 7, 10].

### 3.2 Immediate Rejection by the Establishment
Joshi's attempt to bridge the gap was swiftly rejected by both sides of the schism [cite: 15]. 

Peter Scholze reviewed Joshi's preprints and concluded they did not salvage IUT [cite: 3, 13, 20]. Scholze pointed out on MathOverflow that Joshi’s version of Mochizuki’s Corollary 3.12 (Joshi’s Theorem 9.11.1) relied on a purely local proof [cite: 20]. Because it was a local proof, it intrinsically lacked the global Diophantine content required to prove the *abc* conjecture, rendering it fundamentally different from what Mochizuki intended [cite: 20]. 

### 3.3 Mochizuki’s 167-Page Rebuttal
If Scholze’s dismissal was highly technical, Mochizuki’s response was characteristically explosive. In March 2024, Mochizuki released a massive 167-page defense of his work, significantly expanded from a 65-page document he had previously circulated [cite: 3, 14]. 

The text was a masterpiece of academic hostility, launching scathing ad hominem attacks on both Scholze and Joshi [cite: 3, 14]. Mochizuki stated that it was "conspicuously obvious" that Joshi was "profoundly ignorant" of the actual mathematical content of IUT [cite: 13, 14, 15]. He declared that there was an entirely unanimous consensus among his colleagues that Joshi’s preprints were "obviously mathematically meaningless" [cite: 14]. 

In a bizarre modernization of mathematical insults, Mochizuki even compared Kirti Joshi’s mathematical reasoning to ChatGPT, characterizing his mathematical ideas as mere "hallucinations" [cite: 14]. Columbia University mathematician Peter Woit summarized Mochizuki's 167-page document by noting, "It's hard to imagine a more effective way to destroy one's own credibility and to convince people not to bother" [cite: 3]. 

Despite this, Joshi persisted, publishing his "Final Report on the Mochizuki-Scholze-Stix Controversy" in May 2025, maintaining that his enhancements proved the *abc* conjecture and that the Scholze-Stix critique was based on a "flawed premise" [cite: 20, 21].

---

## 4. Financial Bounties and Sociological Fallout (2024)

As traditional mathematical discourse broke down into factionalism and insults, the IUT debate transitioned into the realm of financial bounties and institutional maneuvering. 

### 4.1 Zen University and the Inter-universal Geometry Center (IUGC)
To forcibly revive engagement with IUT, Nobuo Kawakami, the billionaire founder of Dwango Co., Ltd., funded the creation of the Inter-universal Geometry Center (IUGC) [cite: 16, 22]. The institute was established under the banner of the newly announced online "Zen University" (scheduled to open in 2025), with Fumiharu Kato serving as Director and Ivan Fesenko as Vice-Director—both prominent sympathizers of Mochizuki [cite: 16, 22].

### 4.2 The Challenger and Innovator Prizes
In July 2023, the IUGC announced two highly publicized international prizes designed to challenge the global mathematical consensus, which officially took effect in 2024 [cite: 16]:
1.  **The IUT Challenger Prize:** A massive $1,000,000 bounty offered to the first mathematician to write a peer-reviewed paper exposing a fundamental, inherent flaw in IUT theory [cite: 15, 16, 22].
2.  **The IUT Innovator Prize:** An annual award ranging from $20,000 to $100,000, to be given over 10 years to the best paper containing new and important developments in IUT theory and related fields [cite: 16, 23].

### 4.3 The 2024 Innovator Prize Controversy
In April 2024, the IUGC announced the first recipient of the $100,000 IUT Innovator Prize. The global mathematical community was astounded when the prize was awarded to a 2022 paper published in the *Kodai Mathematical Journal* titled "Explicit estimates in inter-universal Teichmüller theory" [cite: 23].

The controversy lay in the authors of the winning paper: Shinichi Mochizuki, Ivan Fesenko, Yuichiro Hoshi, Arata Minamide, and Wojciech Porowski [cite: 23]. Essentially, the core group of IUT proponents at RIMS was awarding a prize to themselves [cite: 13, 22]. 

The winning paper claimed to establish effective *abc* inequalities with explicit constants, combining IUT with bounds from Preda Mihailescu to give a new proof of Fermat's Last Theorem [cite: 23]. While Ivan Fesenko declined to accept his portion of the money, Mochizuki and the remaining authors accepted the $100,000 and announced they would donate the funds back to RIMS to further support research into IUT and anabelian geometry [cite: 15, 23, 24]. 

Critics outside Japan viewed this maneuver with extreme skepticism. Bloggers and commentators characterized the award as "hand-outs" and a scheme by the IUT group to pull money from Kawakami to enrich their own insular research circle [cite: 22]. The incident served to further isolate the Kyoto group from mainstream arithmetic geometry.

---

## 5. Classical Breakthroughs I: Hector Pasten and Shimura Curves

While the IUT saga descended into institutional drama, mainstream number theory experienced a renaissance. Recognizing that the *abc* conjecture was a "very stuck subject," researchers turned to entirely different methodologies [cite: 25]. The most spectacular progress came from Hector Pasten, a mathematician at the Pontificia Universidad Católica de Chile [cite: 25, 26].

### 5.1 Bypassing Linear Forms in Logarithms
Historically, the primary tool for attacking the *abc* conjecture was the theory of linear forms in $p$-adic logarithms, pioneered by Alan Baker [cite: 27, 28]. While this theory provided some bounds on the $p$-adic valuations of $abc$ triples, it was inherently limited, yielding only exponential bounds [cite: 27, 29]. The sharpest result prior to Pasten was obtained by Stewart and Yu in 2001, who showed that $\text{rad}(abc) < (\log c)^{3-\epsilon}$ [cite: 4, 5]. 

Pasten discarded linear forms in logarithms entirely. Instead, he developed a general framework utilizing **Shimura curves** and their parametrizations to elliptic curves [cite: 27, 28]. By analyzing the comparison ratio of the degrees of these maps, Pasten could recover vital information regarding *abc* triples [cite: 27]. Because Shimura curves often lack simple $q$-expansions, Pasten relied on the Arakelov height of Complex Multiplication (CM) points, integral models, Galois representations, zero-density estimates for L-functions, and complex-analytic estimates [cite: 27, 28]. 

### 5.2 Breaking the 90-Year Mahler-Chowla Barrier
In a remarkable anecdote, Pasten solved a century-old problem while procrastinating writing a final exam for his number theory class in November 2023 (he eventually had his students write an essay instead) [cite: 25]. 

Pasten focused on the sequence $n^2 + 1$ (2, 5, 10, 17, 26...), which has been used for a century to probe the fraught relationship between addition and multiplication [cite: 25]. In 1934, Chowla and Mahler established a bound on the largest prime factor of this sequence, a record that stood essentially unchanged for 90 years [cite: 25, 30]. 

Combining transcendental methods with his modular approach to the *abc* conjecture, Pasten proved that the largest prime factor of $n^2+1$ is at least of size:
\[ \frac{(\log_2 n)^2}{\log_3 n} \]
where $\log_k$ is the $k$-th iterate of the logarithm [cite: 25, 30]. This result shattered the longstanding 1934 barrier.

### 5.3 Subexponential Bounds on the abc Conjecture
Pasten’s techniques directly translated into profound, unconditional progress on the *abc* conjecture itself [cite: 25, 27, 30]. Pasten established a new **subexponential bound** for the conjecture. Specifically, in the case where $a < c^{1-\epsilon}$, Pasten proved that:
\[ \text{rad}(abc) < \exp((\log \log c)^{2-\epsilon}) \]
[cite: 4]. 

This represents the first improvement on the Stewart-Yu bounds dating back over two decades [cite: 25, 30]. Pasten's work also yielded improved effective bounds for the Faltings height of elliptic curves over $\mathbb{Q}$ in terms of the conductor, acting as evidence toward Vojta's conjecture on algebraic points of bounded degree [cite: 27, 28]. For his immense contributions, specifically regarding arithmetic derivatives, Pasten was awarded the Canadian Mathematical Society's 2023 G. de B. Robinson Award [cite: 26]. Renowned number theorist Andrew Granville remarked that the "originality and promise of his methods deserve wide attention," signaling that Pasten’s approach represents the future of Diophantine analysis [cite: 25].

---

## 6. Classical Breakthroughs II: Jared Duker Lichtman’s Density Estimates

The momentum generated by Pasten in 2024 carried into 2025, culminating in a striking theorem by Jared Duker Lichtman of Stanford University and the University of Oxford, in joint work with Tim Browning and Joni Teräväinen [cite: 6, 31]. 

### 6.1 The "Almost Always" Theorem
While Pasten focused on the size of the bounds for individual triples, Lichtman and his collaborators focused on the *frequency* of the exceptions to the conjecture. Their result, colloquially known as "The *abc* conjecture is true almost always," quantifies the rarity of the triples that violate the expected bound [cite: 5, 6, 31].

Let $E(N)$ denote the set of exceptional triples $(a, b, c)$ in a cube $\{1, \ldots, N\}^3$ of length $N$ that are coprime, satisfy $a+b=c$, and violate the *abc* condition by having $\text{rad}(abc) < c^{1-\epsilon}$ [cite: 5, 6]. The *abc* conjecture is equivalent to stating that $|E(N)| \leq O_\epsilon(1)$ for all $N \ge 1$ (meaning the number of exceptions is finite) [cite: 5, 6].

A classical 1962 estimate by the mathematician de Bruijn established that out of the $O(N^2)$ many coprime solutions to $a+b=c$ in that cube, at most $O(N^{2/3})$ solutions satisfy the strict violation condition [cite: 5, 6]. Therefore, even under classical 20th-century mathematics, the conjecture was known to be true for the vast majority of triples [cite: 6].

### 6.2 Power-Saving Bounds
In September 2025, Lichtman announced a definitive refinement to de Bruijn's 1962 estimate [cite: 31]. Using a combination of bounds for the density of integer points on varieties, Lichtman, Browning, and Teräväinen proved a **power-saving bound** on the exceptional set of triples [cite: 31]. 

They successfully reduced the exponent from de Bruijn's $2/3 \approx 0.666$ to $33/50 = 0.66$ [cite: 6, 31]. Namely, they proved that:
\[ |E(N)| \leq O(N^{33/50}) \]
[cite: 6, 31]. 

This theorem provides the first power-savings on the exceptional set in over 60 years [cite: 6]. Their bounds actually extend to all variables up to $\lambda \le 1.001$, providing a power-savings toward Mazur's conjecture as well [cite: 4]. By proving that the density of counterexamples shrinks much faster than previously known, Lichtman's work provides massive statistical support for the absolute truth of the *abc* conjecture.

---

## 7. Conditional Consequences and Computational Searches

Because a full proof of the general *abc* conjecture remains formally unaccepted, mathematicians continue to map out what the world of number theory will look like if (or when) it is finally proved. This has led to an explosion of "conditional" results—theorems that are true *assuming* the *abc* conjecture holds.

### 7.1 The Goormaghtigh Conjecture
A prominent example is the Goormaghtigh conjecture, which states that the only two numbers with two non-trivial representations as repunits are 31 and 8191 [cite: 32]. A related concept is a "Goormaghtigh prime," a prime number fitting this description [cite: 32].

In October 2024, researchers published an algorithm and exhaustive computation proving that there are no new Goormaghtigh primes less than $10^{700}$ [cite: 32]. The computation was highly resource-intensive, taking approximately 480 core-days on a single core of an Intel SP Platinum 8280 CPU running at 2.7 GHz [cite: 32]. 

However, the authors also provided a conditional result. Utilizing Carl Pomerance's argument and the *abc* conjecture bound $c < \text{rad}(abc)^{1+\epsilon}$, they formally proved Theorem 2: *Assuming the abc conjecture, there are only finitely many Goormaghtigh numbers where neither representation is of length three or four* [cite: 32].

### 7.2 Squarefree Values of Polynomials
Similarly, Hector Pasten demonstrated that assuming the *abc* conjecture over number fields, one can obtain an exact asymptotic estimate for the number of squarefree values of a polynomial at prime arguments [cite: 33, 34]. 

For a polynomial $f \in \mathbb{Z}[t]$ of degree $r \ge 2$, calculating the number of prime arguments $p \le x$ where $f(p)$ is squarefree is notoriously difficult [cite: 33]. While the asymptotic formula is known unconditionally for degrees $r \le 3$ (requiring highly non-trivial results like the modularity theorem of Wiles), it remains unknown for any irreducible polynomial of degree strictly greater than 3 [cite: 33, 35]. Pasten showed that assuming the *abc* conjecture, and using results by Tao and Ziegler on arithmetic progressions of primes, the asymptotic formula holds universally [cite: 33, 35].

### 7.3 ABC@Home and Computational Searches
On the computational front, distributed computing projects like ABC@Home have relentlessly searched for *abc*-hits [cite: 1]. While no finite set of examples can resolve the conjecture [cite: 1], these searches provide critical data for heuristics. As of earlier project phases, millions of triples had been identified [cite: 1], with researchers like Michel Waldschmidt in 2026 highlighting prime examples such as $11^2 + 3^2 \cdot 5^6 \cdot 7^3 = 2^21 \cdot 23$, which yields an *abc*-hit with a radical of $53,130 < 48,234,496$ [cite: 2].

---

## 8. Conclusion: The Future of the abc Conjecture

The status of the *abc* conjecture in the 2024-2026 period is characterized by a stark dichotomy.

On one side lies the deeply entrenched Mochizuki-IUT controversy. The discourse has largely abandoned mathematical rigor in favor of sociological warfare, marked by $1 million bounties, closed-loop prize awards, and ad hominem attacks [cite: 14, 15, 22]. Because traditional peer review has failed to resolve the geographical and institutional schism, an increasing number of mathematicians believe that the only path forward for IUT is through formal computer proof assistants [cite: 15]. Efforts to translate Mochizuki's complex structures into the "Lean" theorem prover are currently underway, which may eventually provide an impartial, objective verification of the theory's logical foundations [cite: 15, 21].

On the other side lies the triumph of classical arithmetic geometry. Researchers like Hector Pasten and Jared Duker Lichtman have demonstrated that the *abc* conjecture is far from a "stuck subject" [cite: 25]. By forging new paths through Shimura curves, Arakelov geometry, and integer density bounds on varieties, they have bypassed the IUT debate entirely, delivering the first unconditional subexponential and power-saving bounds on the conjecture in decades [cite: 6, 27, 31]. 

The ultimate, unconditional proof of the *abc* conjecture remains elusive. However, the unprecedented breakthroughs of 2024 and 2025 ensure that mathematics is closer to understanding the profound connection between prime factors and integer relationships than at any point in history.

**Sources:**
1. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0IuBSBTNLC6RVjnzuYNy-J91f4pWjgMhV-Dl-n9qfGwIfRAKMtppNAkK3qoQOjox7-eyOIzwNAx4Qza0Vrhwnnalgeh0gUnXwczYJw7ng8GpU4gM17PB2j3P6HoLVolq3rw==)
2. [imj-prg.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-BJhmLr4lsZCZUZAv3krEcWijC02RkqYQeO7BeE84huKrTPxD1XDNkBPXie1TCMn9fE1UAh6dgKPfWGRZwLNAy3-rDwMNy1sLBgIEMampKxLoa6G1oz6NpRuBMP1vYS7RXHH1SxtyrOXF_0TJeZ7byTzu-XlXMjSLjJ8_zORi-fH8hKVhOA==)
3. [samlowe.dev](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_TmMxgked9mmZdkRM11tzelObU0VrkP0BVvAREQurPVQx5S8rICmPcOgW1MvQyJITJClVtMaEe8xruDiIrYYtnA_BLkEr8HxzKQWW9o2ni9mi9BrVMnSObdVZIlV2g3XALBoclHYcRSH1MXC8dCc=)
4. [cirm-math.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGc8izwxx9bFGhCy8m3Enq0Vshw0mBFXq0cOYzz7pWSiACStJBjC1XyBws-njfue_mWtspTR1G6WzgUzYQXrYikYfgZbbUKUV9dA7VBVq7SvETN2ngk2fJzxw2ccEEvFhYqPm8hykEV5DIf4WYoGuG6Khxt2Q==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-k34HF34TklvC5qNs20APGpK7cCep-mX-VSSt3nruFnNXpi8Hh0qw8s_ohoApcc-inwnFLSbWTmOjcWvtBlWdJ3fiau2oa6BYyjZmUWxboJhR83h_rA==)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH4-9fEWWdAwGg9my-q55bm2s-jqSzRTsb1-BBBLH08TnB_D-5krxJ1fIcDJbtIIb9L8ZfJgB_9c4BBXIZiYMnf_y3tZvB0-AvS-nQlXALn8luTGMqbQ07EFy_yGQeGCD5Fnp0Emv3zval_5zaDD4nLAOWPKoTaRF9FSUlb8c5zDOUJcffU25zpk2Ht2L1g50-4)
7. [earth.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEl06O_6KoJykmVvBztfALsW_P7Yx8ed1m51wctRLRV28jyg_ifmQHNNpPmZ0SCYtx1_J7NTHGgXaChEbE3-_JJSIXSOw8dUecMFT3PNH9DJFPo07fQNppTduwMrgVR4rhJL6kSP-NlXYz19KWCy79oHU4wTyLV9OgU8Q71AOSLPncs3e9FyxBhxhO8rtSYKj0LCI9lGuCCHFQK2qHk6-Q=)
8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFx8an-rpspMSwhGWdI_Q4CiGV_sIfoOifh2PhEjJBXE49arxImcUOLA0V3LHW2agHXU_7ON4RSx8C7o286M1sQbkeL7xZE-VwZJMeYtC2YtEbQ-9fZu2d0TDkz2VXKFHuDtaFPwyhWUYDJTr38i31u9-B5CeS7OLLte7kzDlahiRl16WU3jaj-65ZSEHigZwF2iKQayNMBCPenoYehf53FQZ2cUYl7WHcZtOf4ciV80w0uJ7-HMO9N5S0s-IytlH3Wy_M26po=)
9. [ivanfesenko.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFs17XJarvRjo-BuxOrEhJL2yCEraaUJiesX0Dq0w47ZWZZpMlhn0JqfWsVKrieSuiDAbN30GP-0mI3lt7wD9IOkU0S5lq8SZb-mbCfp5gRG2OB88-X4jkl0W13Z92-m2mmYRmq5tFa-qA=)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFauYy-rpLBO4sVYUcOTRaBXtSeoVJhYRrApRJVqPvQK5pwa_ea7waAfMDsMwTD8RgBGbMTXBk-L1rHnReGhUaW4QR1hCN-xi5yL5H-OPUFg5N9oFxY0w==)
11. [waseda.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHx6rlPK72-652ljZXn0dXU28ifoYf4GoWmGHixmLkFXZ7FhiYLMoK308kiY3fHPK5tw5KWGvgLvgXFvb2QHuEDm7bOwX-I-lhmYNHbXUGN_JvFXR-o-a2u5gy-poXN_o0F81Bh8cYM4H4GGAJ9Cz8TLioKPocLDA==)
12. [ncatlab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJ6uC4MmvYZUiFAprSsS4sciHCXw6dgNnR_3RucKNBsi3wHOnzBMWV_wvUj8iJI78Uf1f1raKop1OnGmGaJOZVrofEXamKanIMO7SxkD53RxO_zvxtWUAncTUN-yMkAb_LslK0omNeDJU4yAqPxKmU)
13. [columbia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_iKPDPyDLOYyOTfWQ7S8nLqwpxW2odpteWcTNZq4alQ8GU9ILGtYacNdpqE3Kt0zR-O2t6-IvcBUOHV-cYRAWR7Nt3xSHOY9-CLxkz26RqJA_UmpjLmqVKLhVkW4RFpG46mCRPz2MXjkCYsk=)
14. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqgqdAb4kt0De1MOacFJLa9Luhb6a13qfRGW0zj_1pMvGCbeK1S-6-XFoPY3kwQBY6EXkyC8Ec0yWX8PAH8sDRrDaGTwxLwBP0N1YxJrCBpWr1nqvDFrRH53-bcMvsLDOJKAOnQRDVLWh03q0Lfiuncwgv8zIfZj8RVCOXqJ8uTDcmK047Oa5IwG_H)
15. [mental-momentum.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHcd27kHsfwitzVD8Vc9T5BWG6ac8_48u4BKYAuQ1uDT1tQMTc3A7O-Mz8amOvsh3LXE3xzrbucE0GTJ4GQkIOyL0P1YOKBEX2xi1_eIJy3T2wSgqQWDbBClpTjtWjKWeqw_nJwRLHAYGAJq0NLjV6tTxcb6BrROQ4Rp37y-2xp2wK9EyXle-cQ7w==)
16. [zen.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFMgX386PDPinZRxedQpCdvS1-b7_XvBhrjFypU7y4BkpmsAPI5NaDp3pss9Db8c47dpFGLFqZ9TIlIB2XaqGryI_PFC0o-kfcMVoHHyo05GLOz13DMkkm)
17. [arizona.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwBpdG9etqufy1-OWphu4HqD6JOCGCRLpzjkFM0EIjZQIDTmzNTAm5pLfgNGERTUAUiws3nOJ8tHU3EnU3eS35rE5X7Je0AHradrYO_GrJggg0BdDIw1aqWYExUMXuaX7DIr21_zx3vjHWMaamzjy-f22XqTkzBF4ZLtdJr3CrpvfkOn5YCl6NOoLc-jfNWJ4FIGdTjT84jxoD)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG97VORa7ovFpOdHDmb7IEtnV5lo-FnD3oxs9LfozdZ8IS21AAZPcUXYmog-7QTHZhdTdUxRJRl9bZ2fMCDbeTWHB_el2n216GqDyGtYIAezjfAOFBAGQ==)
19. [columbia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrJiXj3d4p_Xm1MzIr91x6A250fwSdK97H_g7E3oRgcOpObrAHhtKzEZw7PM4E4t3u6CosS4DOHHiODoOIIIwpMMW9ajGNcrsUs-rR5hrkt3DPVqNzk8k-UsMirAicqpCoKtqoSsud_w-9RkvL)
20. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFu2fcJSGaAIc7Xgf6Ej2dAO82PmdXXrzf55JXPE5zpm7cQEhjDCcFJ_B4fduraTa3tGoEN_1Kwq7RA6Q4ui4bcwVybiQ956UB4cbvuK8MDOKPTIMBIKaFkWJnrtKg37TDQl4yFNbLY_fMwoO-smDr75AkIKcG2mP35QFonzcFC3nUgULsiVY_tTjuDjxcoL_9p1UeS0vkbhg5PyYa-i8u5502Aljg8CDFIW05cULbyKRi1fQM=)
21. [arizona.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqMlheb9Qj6UBIauVnD5mYmjQgHmim_ujaHG9ys7-L1Iq_wVTlLQt7oYt1JTKs2AAkQtVG8phrH7bdxixdS7thJHYfabKftOHKd5R621lAco89sqSwdX8YZ4by6w==)
22. [4bungi.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmb12616_dErqLJm259dIza7mRqBdbOqJOnuAFmva_hsFNWNGfeyzGF0Y5nlNy0_wiFQIAbKfE7mF1MyCCQmzOUIj84H8c-QBDqxromnRZ2xYCobLzkZD3p1wEpLb6DPfy_ckxjKF3sLr_3PVBbWcM)
23. [zen.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwELJTWtFD3WPmSc2ZhuHVVJmd-FeidpR5i9oeb9QwkTJb24JcxtN9uzJWvbVxpp7GSEFcYAIvV9TVIpFh3gI0x-6MxcFVer0Pjc4qZeE6alqNMEEgNcY=)
24. [kyoto-u.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERw3C19bmFjIinfuPc5XTFFtvp0pK1VbRf2rVnZLSerfOA-lvvwlmjmxlzN4ALaHCBeVc1eW9t7tZ_iCFiRj_8KOdjLE2-ugYyuV9M_zxANY22BW-tgqpt4vO_WcJhdTNEUONr9hnwnXv3o-Qz9H_X47VaKDlRx9tM2YyI98EULB0_SnkbmXk6rimxndjp6FYuLpPDvk2BRtVaq5WnfLsXtjIgqGpxymIJyPQZ1OH4dQ6Sqpg4tEJ_3olMb2UAwCRukkRDdpAOx2NzsDoWCAB3wQXFMw71W7sh)
25. [quantamagazine.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGf12D_4h6fv7YQHwphELMfGijVoURTSmwWVztsoy2xlJMiUK7HebLIjsxjhjBCfVZkiRPLqrbra_9XAtE4_Rz6oOcKmzGWtVC6TUmFiX1ZK6ugPNdT98gTjdlFnrIwVCoSU_QLB--HBLR6Sd8UlJJE5hZu45gS2HurXAFqIuWaASFd4CHdll97n6EjKLPEYJuiclJXierh7Pa3b1EXz-d8Epk8bSq-)
26. [math.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPABFSu1_qq5O6U8xrqv3tzqTnIX_E_KRXaenDwAAsmimxiNXC3z68EB8VdwuVKWNBYtGRRtDKljWUtrh8g3IJgCBmMMOIoCQuYh2CVe-MDML9wtmD3XuBqSy-xKFaLUK6SblcK8ChCUCBCr8EFb2NIgGe1m7MobT_NAB6iK2RaAqT_kEFNPrsRllqcEsQ2v3L9uHOA9MLbA==)
27. [columbia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlkds3F16ZlKnWHLhJk2i5Yd3tVUJMSWNjBGlAsIW0OJq5RihGMrOnLimasZwICCnyKswvLWuNBiun4xMUyEje9OACezkOp_Te4Q1d8oW6Nu0UDFCwWJLdGrELl0wsZMLGthEk9Nu4pA==)
28. [uc.cl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPHA0sOB34PGUfWNNns7Y2Ur9uTKNyXsmrfVv0GG3AUeXrVbPTuH6S5VYhZKQocXNFSABiXInvCf2C_OSKoB4nQUzotKxwbOoLf7Y5t1P0SldoJ7fG66XEivS7MqW1dsrH2UOUyO9Sb5UlOUSMgA==)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQER-6_oUXWVbEYK7mRfxc6H2JkwM8MacxuWfjElEGA0PXqcRQ9kHhnAVt4iMG81xmNwuRShjGIAQQVcP05TL1qLwo9c8iOZqJPXDXjTVyuc6_BFTlPRlQ==)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1Lgtyky6MtEBl7td_ebvDbeqn5hfrUVDWKsJ16avf_8oJUXrUcY4F4WhFq55KzNErqXjTFoGmAZGh54pvv_TeVq1zDX08EBryaDuDaI6KYgf2BpjPgQ==)
31. [stanford.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGaFBA5v9qZDR8GaBS38WUDgLEM5hn0dXSqwvxK-2BaoUhDbairugY9xZmj5smy9FQGDm_XSkI8ihFpMY0tsmoDM2OX1Yl9ZcBMQynGo5oa1HSv8DKZO42MfXswW7dyqkvcra-CYAqzbLGxB9y6dXpg6ozWu_X-Rd8XGA==)
32. [colgate.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHWb1yggtB5pwmZVxR-TFF81eWvvqY_KaRW3z3frASwAoy3W_yCGbhkhMBCpUE6IW1DdJyYPEQxzHCC_EQZIBH5_2QkYZjAAy2FV_a85dziO3lhI4g9Ix7b4JoIcBN_AG1im9X)
33. [uc.cl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpwg8-IOg5-F0sVmvOLFQjR6hcZzOa-EqFkHS3A3g5-athrFpcPyGPEBMBxNzc6XxqS2jTsj6boWwjwV8SYhArIX2rqmUObRDL89-mbAaK3dnT-vu0qHnzgsZpIfsg9nSsbjijqtcTsyY6tRr9xHsddECXNA==)
34. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIMl6iNEFDHH84SdiiuY7IMAyN2cGEo1awhz14pdgSWghXGhanprBJIxAK061TEssRhdDqujauXDy1GAC1OFxZwn8L8pleBINBd-321rMFag3o90JO31y1znimkwrz_QWsNuDBnX_NVdezI6g4V1I6VLUNVzKAzyE3ltsvqmYHjRQ4LsOkGwd00D-SmRog4n1dMWqjCfGfYwv-rnchUu6kJLYPCZGVgHf7SxOPfjs0TAAiHAlweh53zcIzud6wnrwoBA==)
35. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHOZO9I3nNZY1BDCzpO5RJKAFWETMTgyUzUMTmZGto1x5wV1vtegOJK6ri6PhHgXvsi1ZcPh8W0h9JFPqCK93YTIKWls1JQPG_EVlzTyD7SQgzzJiznB0V8hx8EBzL3-y8uBN5OwyiynAEoktnA-rNru94hK7-8fY=)

