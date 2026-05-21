# Class number 1, 2, 3 imaginary quadratic field enumeration (Heegner, Stark, Baker) 2024-2026 extensions

**Pythia queue id:** 161
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdYelVQYXVqSUJ2WFVqTWNQa0xxRXdBaxIXWHpVUGF1aklCdlhVak1jUGtMcUV3QWs
**Elapsed:** 253s
**Completed at:** 2026-05-21T16:44:13.395385+00:00

---

# Class Number 1, 2, and 3 Imaginary Quadratic Field Enumeration: The Legacy of Heegner, Stark, and Baker and Recent Extensions (2024-2026)

**Key Points**
*   Research suggests that the foundational Gauss class number problem for imaginary quadratic fields—famously resolved for class numbers 1, 2, and 3 by Heegner, Stark, Baker, and Oesterlé—continues to inspire profound mathematical generalizations.
*   Recent theoretical developments between 2024 and 2026 indicate a major shift toward geometric methods; notably, the work of Caeiro, Darmon, and Geng offers geometric proofs for class numbers $\le 3$ that bypass traditional analytic bounds.
*   It appears likely that the framework of Heegner points is successfully being extended to real quadratic fields via conjectural Stark-Heegner points, providing conditional solutions to class number one problems for specific real quadratic orders.
*   Novel analytic tools, such as the "class number zeta function" introduced by Nikolaev (2026), seem to establish new rational invariants and lower bounds for the count of imaginary quadratic fields with prime class numbers.
*   Advanced computational mathematics is currently pushing the boundaries of what is known; researchers are extending the computation of Bianchi modular forms beyond fields of class numbers 1, 2, and 3 to imaginary quadratic fields with arbitrary class groups.

**What is the Class Number Problem?**
In number theory, a "quadratic field" is a mathematical realm created by adding the square root of a number to the standard rational numbers. If the number under the square root is negative, it is an *imaginary* quadratic field. The "class number" essentially measures how far this mathematical realm is from having the property of unique prime factorization (like standard integers do). A class number of 1 means unique factorization holds perfectly. In 1801, Carl Friedrich Gauss conjectured that there were exactly nine imaginary quadratic fields with a class number of 1. Proving this took over 150 years.

**The Historical Heroes: Heegner, Stark, and Baker**
The story of the class number 1 problem is one of the most famous in mathematics. In 1952, a high school teacher named Kurt Heegner published a proof, but it was largely ignored because experts believed it contained a flaw. In the late 1960s, mathematicians Harold Stark and Alan Baker independently proved the conjecture using different, highly advanced methods (Baker won the Fields Medal for his work). Shortly after, Stark realized Heegner's original proof was actually essentially correct, vindicating him posthumously. Together, their work formed the bedrock for enumerating fields with class numbers 2 and 3.

**Modern Extensions (2024-2026)**
Today, mathematicians are revisiting these classic problems with new technology. Instead of relying solely on heavy analytic estimates, modern researchers are using deep geometric structures—like modular curves and advanced zeta functions—to count these fields. Furthermore, they are applying the lessons learned from imaginary quadratic fields to the much more stubborn problem of *real* quadratic fields (where the number under the square root is positive), leading to an explosion of new algebraic and computational discoveries from 2024 to 2026.

---

## 1. Introduction to Quadratic Fields and Class Numbers

The class number problem, originating from the foundational work of Carl Friedrich Gauss in his 1801 magnum opus *Disquisitiones Arithmeticae*, represents one of the most deeply studied and historically rich subjects in algebraic number theory [cite: 1, 2]. Gauss formulated his conjectures in the language of binary quadratic forms, which in modern parlance translates directly to the study of the ideal class groups of quadratic number fields [cite: 2].

A quadratic number field $K$ is an extension of the rational numbers $\mathbb{Q}$ of degree 2, typically written as $K = \mathbb{Q}(\sqrt{d})$, where $d$ is a square-free integer. The field is termed a *real quadratic field* if $d > 0$ and an *imaginary quadratic field* if $d < 0$ [cite: 3, 4]. The ring of algebraic integers within this field is denoted as $\mathcal{O}_K$. 

The fundamental theorem of arithmetic guarantees that the standard integers $\mathbb{Z}$ possess unique factorization into primes. However, in general rings of algebraic integers $\mathcal{O}_K$, unique factorization can fail. To quantify this failure, mathematicians define the *ideal class group* $\text{Cl}(K)$, which is the quotient group of the fractional ideals of $\mathcal{O}_K$ modulo the principal fractional ideals [cite: 4, 5]. The size of this group is a finite integer $h_K$, known as the *class number* of the field [cite: 4]. A class number of $h_K = 1$ is geometrically and algebraically synonymous with $\mathcal{O}_K$ being a principal ideal domain (PID), which in turn implies that unique factorization holds [cite: 1, 4].

Gauss conjectured two distinct behaviors for class numbers based on the sign of the discriminant $d$:
1.  **Imaginary Quadratic Fields:** As $d \to -\infty$, the class number $h(d) \to \infty$. Furthermore, there are exactly nine imaginary quadratic fields with $h_K = 1$ [cite: 2, 6].
2.  **Real Quadratic Fields:** There are infinitely many real quadratic fields with class number $h_K = 1$ [cite: 2, 7].

While the imaginary case relies on a relatively straightforward analytic relationship—where the class number formula does not feature a complicated regulator term because the unit group is finite—the real quadratic case is complicated by the presence of fundamental units of infinite order, making bounds highly erratic [cite: 2, 7].

This report provides an exhaustive examination of the enumeration of imaginary quadratic fields with class numbers 1, 2, and 3, chronicling the historical resolutions by Heegner, Baker, and Stark [cite: 1, 8]. We will then pivot to a comprehensive analysis of the contemporary extensions of these theories in the 2024-2026 timeframe. This modern era has witnessed a renaissance in the field, marked by the introduction of the class number zeta function [cite: 9, 10], geometric proofs bypassing analytic bounds [cite: 6, 11], conditionally resolved class number problems for real quadratic fields via Stark-Heegner points [cite: 12, 13], and arbitrary-class computational advances in Bianchi modular forms [cite: 14, 15].

## 2. The Heegner-Stark-Baker Theorem for Class Number 1

The resolution of Gauss's class number 1 conjecture for imaginary quadratic fields is a watershed moment in the history of mathematics, illustrating the complex interplay between modular forms, transcendental number theory, and the sociology of mathematical peer review.

### 2.1 Gauss's Conjecture and Early Bounds
In Article 303 of *Disquisitiones Arithmeticae*, Gauss correctly identified the nine negative discriminants for which the class number is 1, but a rigorous proof eluded him [cite: 1, 2]. For over a century, the problem remained intractable. In 1934, Hans Heilbronn took a monumental step by proving Gauss's first conjecture: that $h(d) \to \infty$ as $d \to -\infty$ [cite: 2, 10]. This established that there could only be a finite number of imaginary quadratic fields for any given class number. That same year, Heilbronn and Edward Linfoot proved that there were at most ten imaginary quadratic fields with class number 1: the nine known by Gauss, and at most one hypothetical tenth field with a massive discriminant [cite: 2]. However, their proof was *ineffective*, meaning it provided no absolute upper bound on the size of the hypothetical tenth discriminant, rendering an exhaustive search impossible [cite: 2].

### 2.2 Kurt Heegner's Vision and Rejection
In 1952, Kurt Heegner, a German academic outsider and independent researcher, published a paper claiming to solve the class number 1 problem [cite: 1, 16]. Heegner's approach utilized the theory of complex multiplication and modular functions [cite: 1]. He demonstrated that negative discriminants of class number one yield integral points on an affine modular curve of level 24, which he associated with the normalizer of a non-split Cartan subgroup [cite: 13, 17]. His proof required showing that a specific 24th-degree polynomial with rational coefficients had a 6th-degree factor [cite: 16]. 

Tragically, Heegner's work was largely dismissed by the mathematical establishment. Contemporary experts believed there was a gap in his justification regarding the reducibility of this polynomial [cite: 1, 16]. Consequently, Heegner's proof languished in obscurity, and he died before receiving any recognition for what was, in retrospect, a stroke of profound genius [cite: 1].

### 2.3 Baker and Stark: The Twin Pillars of Resolution
The problem was officially considered "solved" in the mid-1960s by two mathematicians working independently using drastically different methods. 

In 1966, Alan Baker developed a revolutionary method involving lower bounds for linear forms in logarithms of algebraic numbers [cite: 1]. Baker's method was *effective*; it allowed him to place a definitive upper bound on the discriminant, which was small enough that the hypothetical tenth field could be ruled out by finite computation [cite: 1]. For this broad and incredibly powerful theory of transcendental numbers, Baker was awarded the Fields Medal.

Concurrently in 1967, Harold Stark published a proof that expanded on the ideas of complex multiplication [cite: 1, 18]. Stark was able to effectively close the gap by reducing the problem to Diophantine equations that could be rigorously solved [cite: 13]. Stark later observed that Baker's original linear forms proof involving three logarithms could actually be reduced to two logarithms, leveraging older results from Gelfond and Linnik [cite: 1].

### 2.4 The Vindication of Heegner
In a remarkable turn of events in 1969, Harold Stark published a paper titled *On the "gap" in a theorem of Heegner* [cite: 1, 19]. Stark meticulously worked through Heegner's 1952 paper and demonstrated that what the community had perceived as a fatal gap was, at worst, a minor oversight that was easily justifiable using elementary properties of Galois theory and modular functions available to Heegner at the time [cite: 1]. Heegner's proof was essentially correct all along.

Today, the theorem is appropriately named the **Heegner-Stark-Baker Theorem** [cite: 1, 20]. It categorically states that if $d < 0$ is a square-free integer, the imaginary quadratic field $K = \mathbb{Q}(\sqrt{d})$ has class number 1 if and only if:
\[ d \in \{-1, -2, -3, -7, -11, -19, -43, -67, -163\} \]
[cite: 4]. These values of $d$ (or their associated fundamental discriminants $D$) are now universally referred to as the **Heegner numbers** [cite: 1, 4].

## 3. Enumeration of Class Numbers 2 and 3

Following the triumph of the class number 1 problem, attention immediately turned to classifying imaginary quadratic fields with class numbers 2 and 3 [cite: 2]. The techniques forged by Baker and Stark proved adaptable to these higher class numbers.

### 3.1 Class Number 2 Enumeration
The determination of all imaginary quadratic fields with class number 2 was achieved collaboratively and independently in 1971 by Alan Baker and Harold Stark [cite: 2]. Similarly, Montgomery and Weinberger provided extensive work on the problem [cite: 21]. By utilizing linear forms in logarithms and deep properties of $L$-functions, they proved that there are exactly 18 imaginary quadratic fields with class number 2 [cite: 21]. 

Letting $K = \mathbb{Q}(\sqrt{d})$ for $d < 0$ square-free, the class number $h_K = 2$ exactly for the following values of $d$:
\[ d \in \{-5, -6, -10, -13, -15, -22, -35, -37, -51, -58, -91, -115, -123, -187, -235, -267, -403, -427\} \]
[cite: 21].
These fields provide critical test cases for computational number theory and are highly relevant in the modern study of Galois extensions and embedding problems [cite: 22].

### 3.2 Class Number 3 Enumeration
The class number 3 problem was historically slightly more resistant because the class group of order 3 does not exhibit the strict 2-torsion symmetry that allows genus theory to heavily constrain the discriminants [cite: 23, 24]. The problem was eventually solved in 1985 by Joseph Oesterlé [cite: 2]. 

Using an extension of Goldfeld's analytic method—which relates the class number of imaginary quadratic fields to the $L$-functions of elliptic curves via the Gross-Zagier theorem—Oesterlé proved that the list of imaginary quadratic fields with class number 3 is finite and explicitly known [cite: 2, 24]. 

For fundamental discriminants $-D < 0$, the class number $h(-D)$ is odd only under strict conditions. Genus theory dictates that the 2-rank of the class group $\text{Cl}(K)$ is equal to $t - 1$, where $t$ is the number of distinct prime factors of the discriminant [cite: 7, 25]. Therefore, for the class number to be an odd prime like 3, the discriminant must have exactly one prime factor (i.e., $D$ is a prime) or be a power of a prime, leading to the condition that $D$ must be a prime $q \equiv 3 \pmod 4$, or $D \in \{4, 8\}$ [cite: 23, 26]. This drastically limits the search space compared to even class numbers.

The established imaginary quadratic fields with class number 3 are foundational for constructing more complex algebraic structures, such as unramified cyclic cubic extensions [cite: 24, 27].

## 4. The 2024-2026 Geometric Revolution: Caeiro, Darmon, and Geng

Traditionally, the enumeration of class numbers up to 100 (completed by Watkins in 2004 [cite: 2, 26]) relied heavily on Goldfeld's lower bound [cite: 28]. Goldfeld's bound utilizes the Birch and Swinnerton-Dyer (BSD) conjecture and the Gross-Zagier formula to relate the class number $h(d)$ to the derivatives of $L$-functions of elliptic curves [cite: 28, 29]. However, between 2024 and 2026, a major theoretical shift occurred, pushing algebraic number theory toward purely geometric methods to resolve class number problems without invoking Goldfeld's analytic methods.

### 4.1 Bypassing Goldfeld: Geometric Proofs for $h \le 3$
In late 2025 and 2026, Elias Caeiro, Henri Darmon, and Jingxuan Geng presented a groundbreaking geometric approach to the class number problem [cite: 6, 11]. The classical Gauss problem asks for all imaginary quadratic fields for a fixed class number $h$ [cite: 6]. Caeiro and Darmon utilized the theory of Heegner points and the Gross-Zagier formula not merely as analytic bounds, but as geometric constraints on modular curves [cite: 6, 29].

In a series of seminars at institutions such as Princeton, Ohio State, and the Institute for Advanced Study (IASM) in 2026, Caeiro explained that they successfully determined all negative discriminants of class numbers at most 3 purely geometrically [cite: 6, 11]. Their method relies on classifying the rational points on specific modular curves. Just as Heegner used the modular curve $X_0(163)$ and the normalizer of a non-split Cartan subgroup of level 6, Caeiro and Darmon systematically mapped higher class number problems to integral points on higher-genus modular curves [cite: 17, 30]. By applying advanced Diophantine geometry and Chabauty-like bounds, they avoided the ineffective constants that plague analytic number theory [cite: 2, 11].

### 4.2 Stark-Heegner Points and Real Quadratic Fields
The most profound implication of Caeiro and Darmon's 2024-2026 work is the extension of these geometric principles to *real* quadratic fields [cite: 8, 12]. Gauss's conjecture that there are infinitely many real quadratic fields with class number 1 remains one of the greatest unsolved problems in mathematics [cite: 7]. 

The difficulty in real quadratic fields stems from the fundamental unit $\varepsilon$. Dirichlet's analytic class number formula states that for real quadratic fields, the residue of the Dedekind zeta function at $s=1$ is proportional to $h_K \log \varepsilon$ [cite: 2]. Because $\varepsilon$ can be arbitrarily large, the class number $h_K$ cannot be easily bounded [cite: 2, 7]. 

To circumvent this, Darmon introduced the conjectural theory of *Stark-Heegner points* (also known as Darmon points) [cite: 12, 16]. These are local points on rational elliptic curves, conjecturally defined over ring class fields of real quadratic fields, analogous to classical Heegner points for imaginary quadratic fields [cite: 12, 16]. 

In a landmark paper published in *Essential Number Theory* in early 2025, Caeiro and Darmon demonstrated that the conjectural extension of complex multiplication theory via rigid analytic elliptic cocycles yields lists of real quadratic orders of class number one with small regulators [cite: 8, 13]. Specifically, they applied this to families of real quadratic fields of Richaud-Degert type [cite: 17, 31]. These are fields with discriminants of the form $D = n^2 \pm 4$ or $D = n^2 \pm 1$ [cite: 13, 31]. 

By studying the "winding kernel"—the kernel of the natural map $J_0(N) \to J_w(N)$—Caeiro and Darmon proved that if Stark-Heegner points behave as conjectured, one can achieve a conditional solution to the class number one problem for real quadratic orders formulated by Yokoi, Mollin, and Chowla [cite: 12, 13, 17]. 
For instance, they establish that maximal quadratic orders of discriminant $\Delta_n^+ = n^2 - 4$ having class number one are precisely those for $n \in \{0, 1, 3, 4, 5, 9, 21\}$, corresponding to $\Delta \in \{-4, -3, 5, 12, 21, 77, 437\}$ [cite: 31]. This work represents a massive leap, translating the definitive Heegner-Baker-Stark methodology into the much more hostile territory of real quadratic fields [cite: 20, 31].

### 4.3 ATR Cycles and Mock Hilbert Modular Surfaces
In parallel with Stark-Heegner point research, literature from late 2024 highlights the equidistribution of S-arithmetic cycles [cite: 32]. The Stark-Heegner cycle attached to a character $\psi$ is a compact geodesic confined within a mock Hilbert modular surface [cite: 32]. The narrow class group parameterizes these cycles [cite: 32]. The study of Almost Totally Real (ATR) cycles by Darmon, Rotger, and Zhao has further solidified the geometric linkage between the arithmetic of real quadratic fields and topological cycles on modular varieties [cite: 29, 32].

## 5. Analytic and Zeta Function Methods: Nikolaev's 2026 Breakthrough

While geometric methods advanced the algebraic side of the class number problem, analytic number theory also saw a radical innovation in early 2026. Igor V. Nikolaev introduced a novel mathematical object: the **Class Number Zeta Function of Imaginary Quadratic Fields** [cite: 9, 10].

### 5.1 The Class Number Zeta Function
Historically, zeta functions (like the Riemann zeta function or the Dedekind zeta function) encode prime factorizations or ideal norms [cite: 3]. Nikolaev constructed a zeta function that explicitly counts imaginary quadratic number fields $\mathcal{Q}$ by their class numbers $h$ [cite: 10]. 

Let $\#h$ be the cardinality of the subset of $\mathcal{Q}$ consisting of fields with exactly class number $h$ [cite: 10]. Nikolaev defined the zeta function $\zeta_{\mathcal{Q}}(s)$ via a Lambert series, or equivalently, as an Euler product:
\[ \zeta_{\mathcal{Q}}(s) := \exp\left( \sum_{h=1}^\infty \frac{\#h}{h} \frac{s^h}{1 - s^h} \right) = \prod_{h=1}^\infty \frac{1}{(1 - s^h)^{\frac{\#h}{h}}}, \quad s \in \mathbb{C} \]
[cite: 10]. 
Because of a theorem by Dold, the ratio $\frac{\#h}{h}$ is always an integer, guaranteeing that this Euler product is well-defined as a formal power series [cite: 10, 33]. Note that Nikolaev's definition precludes certain fields, such as $\mathbb{Q}(\sqrt{-1})$, making the actual value of $\#h$ slightly higher than the function's strict output [cite: 10].

### 5.2 Rationality and the "Riemann Hypothesis" for $\zeta_{\mathcal{Q}}(s)$
Nikolaev's main theorem proved that $\zeta_{\mathcal{Q}}(s)$ is a *rational* function [cite: 9, 10]. This is an extraordinary result, as it reduces an infinite sequence of seemingly erratic counts of class numbers into a closed algebraic form. Nikolaev showed that the rationality depends only on the eight roots of unity of degrees 1 and 2 [cite: 9, 10]. 

Furthermore, Nikolaev notes an analog of the Riemann Hypothesis for this zeta function: the single pole of the function at $s=1$ has order 8, and all zeros of the function lie precisely on the roots of unity of degrees 1 and 2 [cite: 10].

### 5.3 Noncommutative Geometry and Drinfeld Modules
The proof of this rationality relies on profound connections to non-commutative geometry and operator algebras [cite: 9, 34]. Nikolaev constructed a dynamical system arising in the representation theory of Drinfeld modules by bounded linear operators on a Hilbert space [cite: 9, 34]. 

By studying the periodic points of the map $f(z) = \lambda e^z$, Nikolaev demonstrated that the cardinality of the set of imaginary quadratic fields of class number $h$ equals the number of least $h$-periodic points of this dynamical map [cite: 33]. When uniformized on a Riemann sphere double cover by complex tori $\mathbb{C}/(\mathbb{Z} + \mathbb{Z}\tau)$, the zeta function of this dynamical system coincides exactly with the local zeta function of an elliptic curve over a finite field $\mathcal{E}(\mathbb{F}_1)$, which guarantees its rationality [cite: 10, 33].

### 5.4 A New Lower Bound for Prime Class Numbers
A direct, practical corollary of Nikolaev's zeta function is the establishment of rigorous new lower bounds for the number of imaginary quadratic fields with a given class number [cite: 9, 10]. 

By analyzing the rational form of $\zeta_{\mathcal{Q}}(s)$, Nikolaev proved that if $h = p$ where $p$ is a prime number, then there is an explicit lower bound:
\[ 2p \le \#p \]
[cite: 10, 33]. 
This means that for any prime $p$, there are at least $2p$ distinct imaginary quadratic fields with class number $p$ [cite: 10, 35]. For composite class numbers $h \neq p$, the bound generalizes to $d \cdot h \le \#h$ where $d \ge 3$ [cite: 33]. This establishes a deterministic floor for the density of fields with prime class numbers, a topic that previously relied heavily on the probabilistic Cohen-Lenstra heuristics [cite: 7].

## 6. Elementary Proofs and Binary Quadratic Forms (2024)

Amidst these highly advanced geometric and non-commutative approaches, 2024 also saw a return to elegant, elementary methods. James E. Carter published a purely elementary proof of the theorem on imaginary quadratic fields with class number 1 [cite: 19, 36]. 

Carter's methodology traces back to Gauss's original framework of binary quadratic forms $f(x,y) = ax^2 + bxy + cy^2$ [cite: 19]. Let $D$ be a square-free integer other than 1, and $K = \mathbb{Q}(\sqrt{D})$. Carter defines $\delta \in \{1, 2\}$, with $\delta = 2$ if $D \equiv 1 \pmod 4$ [cite: 19, 36]. 

Carter explicitly associates to each prime ideal $\mathcal{P}$ in $K$ that splits in the extension $K/\mathbb{Q}$ a binary quadratic form $f_\mathcal{P}$ [cite: 19, 36]. Carter rigorously proves that:
*   When $K$ is imaginary, $\mathcal{P}$ is a principal ideal if and only if the associated quadratic form $f_\mathcal{P}$ represents the integer $\delta^2$ [cite: 19, 36].
*   When $K$ is real, $\mathcal{P}$ is principal if and only if $f_\mathcal{P}$ represents $\pm \delta^2$ [cite: 19, 36].

By demonstrating this explicit necessary and sufficient condition for principality, Carter recovers the Heegner-Baker-Stark theorem entirely without relying on linear forms in logarithms, Heegner points, or elliptic curve $L$-functions [cite: 19, 36]. Carter’s proof reveals new necessary conditions regarding the integers represented by $f_\mathcal{P}$ for an imaginary quadratic field to have class number 1 specifically when $D \equiv 1 \pmod 4$ [cite: 19]. For instance, looking at the discriminant $D = -47$, Carter easily proves that the resulting form $7x^2 + 36xy + 47y^2 = 1$ has no integer solutions by showing it is not properly equivalent to the principal form $x^2 + 5y^2$, thus proving $\mathbb{Q}(\sqrt{-47})$ cannot have class number 1 [cite: 19].

## 7. Computational Frontiers: Bianchi Modular Forms (2025-2026)

The enumeration of class numbers 1, 2, and 3 has historically defined the limits of specific computational techniques in automorphic forms. Bianchi modular forms are the natural generalization of classical modular forms from the rational numbers $\mathbb{Q}$ to imaginary quadratic fields $K$ [cite: 15, 37].

### 7.1 Beyond the Class Number 3 Barrier
Classical modular forms of weight $k$ are defined as complex functions on the upper half-plane $\mathbb{H}^2$ that exhibit symmetry under the group $\text{SL}(2, \mathbb{Z})$ [cite: 38]. Bianchi modular forms, conversely, act on the hyperbolic 3-space $\mathbb{H}^3$ and are symmetric with respect to the Bianchi groups $\text{GL}_2(\mathcal{O}_K)$ [cite: 15]. 

In the 1980s, researchers like Grunewald and Mennicke, followed by John Cremona, developed algorithms to compute Bianchi modular forms [cite: 15, 37]. However, for decades, these implementations were strictly limited to imaginary quadratic fields $K$ with small class numbers. Cremona and his students extended calculations up to class number 3 (e.g., $K = \mathbb{Q}(\sqrt{-23})$ and $\mathbb{Q}(\sqrt{-31})$) using modular symbols and exact geometric tessellations of $\mathbb{H}^3$ [cite: 15, 39]. The primary bottleneck was the extreme algorithmic complexity of managing the tessellation and computing homology when the ideal class group is large [cite: 15].

### 7.2 Arbitrary Class Groups
In a highly anticipated paper set for publication in 2025-2026, Kalani Thalagoda, John Cremona, and Dan Yasaki successfully dismantled this barrier [cite: 14, 38]. Their research provides general techniques and fully realized algorithmic implementations to compute the space of Bianchi modular forms of level $\Gamma_0(\mathfrak{n})$ over imaginary quadratic fields with *arbitrary* class groups [cite: 14, 37].

For an integral ideal $\mathfrak{n}$ of $\mathcal{O}_K$, they consider the congruence subgroup $\Gamma_0(\mathfrak{n})$ of matrices in $\text{GL}_2(\mathcal{O}_K)$ that are upper triangular modulo $\mathfrak{n}$ [cite: 14, 15]. By computing the rational homology $H_1(\mathbb{H}^3 / \Gamma_0(\mathfrak{n}), \mathbb{Q})$ via a tessellation algorithm based on Swan's work, Thalagoda et al. derive the Hecke action on this space and its decomposition into Hecke eigenspaces [cite: 15, 39]. 

They provide explicit details for the field $K = \mathbb{Q}(\sqrt{-17})$, which has a cyclic class group of order 4, proving the modularity of an elliptic curve over this field [cite: 14, 37]. This leap forward allows researchers to systematically populate the L-functions and Modular Forms Database (LMFDB) with data on fields that were computationally inaccessible just a few years prior [cite: 14, 15].

## 8. Applications: Enumerating Imaginary Bicyclic Biquadratic Fields

The complete lists of imaginary quadratic fields with class numbers 1, 2, and 3 have acted as seed data for resolving class number problems in higher-degree number fields. Specifically, researchers extensively study **imaginary bicyclic biquadratic fields**. 

An imaginary bicyclic biquadratic field is a degree-4 extension of $\mathbb{Q}$ formed by adjoining the square roots of two distinct integers, taking the form $K = \mathbb{Q}(\sqrt{-x}, \sqrt{-y})$ or $K = \mathbb{Q}(\sqrt{-x}, \sqrt{y})$, where $x, y > 0$ are square-free integers [cite: 24]. 

### 8.1 Kuroda's Class Number Formula
The primary tool for these enumerations is **Kuroda's class number formula**. Because $K$ is a multiquadratic extension, Kuroda's formula relates the class number $h_K$ of the biquadratic field $K$ to the class numbers of its three quadratic subfields: $K_1 = \mathbb{Q}(\sqrt{-x})$, $K_2 = \mathbb{Q}(\sqrt{-y})$, and the real quadratic subfield $K_3 = \mathbb{Q}(\sqrt{xy})$ [cite: 5, 24]. The formula is given by $h_K = \frac{1}{Q} h_1 h_2 h_3$, where $h_i$ is the class number of $K_i$ and $Q$ is the unit index, defined as $[\mathcal{O}_K^\times : \mathcal{O}_{K_1}^\times \mathcal{O}_{K_2}^\times \mathcal{O}_{K_3}^\times]$, which takes the value of 1 or 2 [cite: 5].

### 8.2 Using $h \le 3$ to Solve $h \le 7$
Because the class number of the biquadratic field depends multiplicatively on the class numbers of its imaginary quadratic subfields, knowing the exact finite list of small imaginary quadratic class numbers allows mathematicians to perfectly bound and enumerate the biquadratic fields [cite: 24].
*   **Class Number 1:** Brown and Parry determined exactly 47 imaginary bicyclic biquadratic fields with class number 1 [cite: 5, 24].
*   **Class Number 2:** Buell, H. Williams, and K. Williams identified all 160 fields with class number 2 [cite: 5].
*   **Class Number 3:** Jung and Kwon utilized the known list of class number 1, 2, 3, and 6 imaginary quadratic fields to prove there are exactly 163 imaginary bicyclic biquadratic fields with class number 3. The maximum conductor among these is $163 \cdot 883$ [cite: 5, 40].
*   **Class Numbers 4, 5, 6, and 7:** In 2024 and 2025, researchers Jakhar, Kalwaniya, and Ram successfully algorithmized this process [cite: 24]. They proved that if all imaginary quadratic fields with class numbers up to $2n$ are known (Watkins provided lists up to 100), it is possible to effectively determine all imaginary bicyclic biquadratic fields with class number $n$ [cite: 24]. Consequently, they provided the complete class group structures and explicitly listed all such fields with class numbers 4, 6, and 7 (finding exactly 408 fields for class number 4) [cite: 24]. Similarly, Basilla et al. identified exactly 243 biquadratic fields for class number 5 [cite: 5].

## 9. Ideal Class Group Structures and Cohen-Lenstra Heuristics (2024)

Beyond simple enumeration, the modern study of class numbers heavily investigates the *structural parity* and $p$-parts of the ideal class groups, particularly focusing on how these empirical enumerations align with probabilistic models.

### 9.1 The 2-Part of the Class Group and Genus Theory
The structure of the 2-Sylow subgroup (the 2-part) of the class group of an imaginary quadratic field is dictated by Gauss's Genus Theory [cite: 7]. For $K = \mathbb{Q}(\sqrt{-D})$, if $D$ has $t$ distinct prime factors, the 2-rank of $\text{Cl}(K)$ is exactly $t - 1$ [cite: 7, 25]. This means the number of elements of order 2 (the subgroup $\text{Cl}_K[cite: 28]$) has order $2^{t-1}$ [cite: 25]. 

Because there are infinitely many fundamental discriminants $D$ with precisely two prime factors, there are infinitely many imaginary quadratic fields whose class group has a 2-part perfectly isomorphic to $\mathbb{Z}/2\mathbb{Z}$ [cite: 25]. Conversely, for a class group to have an *odd* size, the 2-rank must be 0, implying $t-1 = 0$, so $D$ must be prime (or a prime power in certain discriminant definitions) [cite: 23, 41]. This immediately forces the class number parity restrictions observed heavily in Oesterlé's enumeration of class number 3 [cite: 26, 41]. 

In a 2024 paper, researchers modeled these structures using directed graphs where vertices are the prime factors of $D$ and arcs exist based on the Legendre symbol $\left(\frac{p_j}{p_i}\right) = -1$ [cite: 7]. They proved theorems regarding the ideal decompositions and modular homomorphisms to construct imaginary quadratic fields with arbitrarily large absolute discriminants that possess specific 2-Sylow subgroups (e.g., of order 16) [cite: 7].

### 9.2 The Cohen-Lenstra Heuristics
The Cohen-Lenstra heuristics are a framework of conjectures predicting the distribution of class groups of quadratic fields [cite: 2, 3]. For real quadratic fields, Cohen and Lenstra predict that approximately 75.45% of fields generated by adjoining the square root of a prime will have class number 1 [cite: 2]. For imaginary quadratic fields, the heuristics accurately predict the probability of the odd part of the class group taking a specific structure [cite: 3]. 

Research in 2024 extensively tested the explicitly known enumerations of imaginary quadratic fields against the Cohen-Lenstra predictions for the 2-part of the class group [cite: 3, 7]. Because Genus theory heavily dictates the 2-part, traditional Cohen-Lenstra heuristics focus on the odd $p$-parts (where $p > 2$). The 2024 studies integrated the quadratic form class group properties to explore distribution deviations and provided theoretical alignment showing that the empirical distribution of small class groups (like 1, 2, and 3) correctly seeds the asymptotic behaviors predicted by Cohen and Lenstra [cite: 3, 7].

Furthermore, researchers Pujahari and Saikia (2024) explored connections between the class numbers of imaginary quadratic fields and the average of the $\ell$-adic expansion digits of $1/n$ [cite: 28]. They established that the average of these digits is intimately tied to the "trace" of generalized Bernoulli numbers and Dirichlet characters [cite: 28]. This work elegantly recovered well-known class number relations formulated by Gauss and Heilbronn [cite: 28], showing that class number properties remain highly relevant in adjacent domains like arithmetic statistics and digit equidistribution.

## 10. Conclusion

The enumeration of imaginary quadratic fields with class numbers 1, 2, and 3 stands as a monumental achievement in 20th-century mathematics. The resolution of the class number 1 problem by Heegner, Stark, and Baker did more than just count fields; it birthed the modern theory of transcendental number theory and vindicated the profound connections between complex multiplication and modular forms [cite: 1, 13]. 

As observed in the massive influx of theoretical research from 2024 to 2026, these classic problems are far from closed. The introduction of Nikolaev's class number zeta function has provided deterministic lower bounds for prime class numbers using noncommutative geometry [cite: 10, 33]. Simultaneously, Caeiro and Darmon have led a revolution in shifting class number proofs from analytic estimates to exact geometric methods, effectively mapping the tools of imaginary quadratic fields onto the elusive class number problems of real quadratic fields [cite: 11, 31]. 

Computational barriers continue to fall, as seen in Thalagoda, Cremona, and Yasaki's 2025 extension of Bianchi modular form algorithms to arbitrary class groups [cite: 14, 15]. Through the application of these foundational enumerations to bicyclic biquadratic fields [cite: 5, 24] and the continuous refinement of the Cohen-Lenstra heuristics [cite: 3, 7], the legacy of Heegner, Stark, and Baker remains a vital, driving force in contemporary algebraic number theory.

**Sources:**
1. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTEEtuRt-QU1qRADwqXES3r4RyZVfWGsVLLoEks0HMylJVj8EVoSqCgNXexEvQYM3gUJDjAq0JB5Ji8CrfS3JsxVrxGwM84G7IAbLANJ1DVK47lG3Mf-85hPIQXXinVQdmavsnNRSptGTb-lvBROYWjQ==)
2. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEhSFlNpuTpNa5VS7xuUHxEmFyvgVSnpMMxxypnY8rDDSEEkMN338mECsyGiDZnsjcpSRJeJOlfHDOEyIl0dSb-XVqKeh6DSa7Z2iraYT_2gE1i-PkbKhXZcdsVqHEQoFZBKAE9lAlNA==)
3. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQmgSHJl1r4ncG_bFVrTZHVOooCV7UW9L4w6mZv-r0RMkCXyBAIxh-YkdVz2hv8ov32hqo1GeMy8lfx4w6j25LVQaA8_rVYHj7UKdT300ORuxtPibrOTwkjf56vw==)
4. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1_zJJ8SR3C_jxzHYA4pgE16XqjXs9AurAOirLyYRT5G3OG39JQTUu1WNk4iRvR4qmNDLwK-FOY-ckrPiiV7buqZgfElALLO2E9cLhjdUN3UYsQf2KOly-gQ6neUrhypyE0dRHZrrOO1OrLI1MrSdGpvyeq6NWDyuLbKnYUpDR)
5. [knu.ac.kr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGj8coTuAUX8amZtw0iYfx7h57GFtUp2xSqzEhs1cOqYq4q-3RPyJBosKA1fX-SHGstTOC2fU4PAIcf6zttVlye-5fJb1sK0sSX499Sh6ltqgp4MX5Gjh15O_npx4jerqtpaMYBG80FzhsRlTB2hbY=)
6. [zju.edu.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2HdJQ2vvqoINklENvvpJFosMrAGSYvkjT4Q0d3_F3hej0-cKK8JStT9P0hBya_NvC7CywKBP7mkxQ1LAuQTYRfp0ttL6HVI7wNyfF3dk-DtLjPcG9CBC0sF2eqDMYUX34AtjjVUre37Q8lS3b83lTjjeohuiFhA==)
7. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHiTdrmGOYWYdnKBaFAYzKKxMagyGeJUwIC6VsX-tJfiQllW_ZdHPJd0aG-7JfzJ8YvvsYa4JWROxscX43W8hHa0QbVS0Q3HDhqv4oCJVB7UOfYW8YwWLTj3GQRHyu2PkAKTa8y3nWz3LA=)
8. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFN5dohxgV5chxUKlggVBX1O6TptZJcs-w8xYrsj_ll9FcmJ4C5Y661xdtCzjXcfEyO6-JvLSdweA5G3jglaApvH3Ed7hDgtp7NHi-LVYIzM34uB16uXIlMRfkf3Q==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF84xo4VbiP87FXcWTqCi-MHWgHgB3UAnpBoN4G5SEuZyEACntZp6eGgU961bcMu_OozRL590-yed0Gl7aFJr-1b0dQ3hGYXh7IQksKun9oYEo0dCXJZw==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3M7UFPWwIrWWjedF8yyFDt6dsfq-3lINvaO-1rcAugdFFE65TaSTTOt4mg7Dax70peu_ORUath6YOMY7r2DX2ujqz8CqtC2PRv7x8ZzlEIv7yDTsJ7VPwgA==)
11. [osu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtZF4WbNLsP4_-t8dR3MFck_z3D9e6Em-PqEzidDsWrLUEzT2mAceEJZ7yOro92XLq3nVh-F3ybzrUVXIFbJ8c9aadl29LglslJswxiREPOBGNQvvAIn7e-DfoAwF4Xmspmbl33rNg7quvZ1b1cJRNMF6OOAGZnQw6lThRvNW8sK5NS4cNqO7CJdMzTEixKBkFJDl_Nr_VSg==)
12. [ams.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHveLdLRrVF685zQu7KiTc3yebnxIde5s5riWE_XWbI-e_flQOGyvyZr2OF0LEi1fNFZb3FN5PmK0BfMgvLeOBCGnQSqqK9tzJmmYOVTRr-Npf-wsA3XaVq72NnT1JvKKjblXRO5CmeP_Rn0IJY5A_4yg09Ky75foA=)
13. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHj8WfgE89A6tfCg9o3wkEjUCj4NAvwX3nTeiP3-1dcJ0bxW1rqfXCWt4rfzXuzIQOEFXHs41wXGuiPl8lM6fvALf2FNWkSoZ_y8FRwb-UT0FpSM_NmsBAHjeXHkHXyQK6ICP8ZDHo=)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_DiW1M6bxLaFJzAwKG0yvF9SBqbjv3E0ZyqVm1VH3lZr_uMzsllg6GAyabTPovXRl68mL4YBsUbiOFqNGSiG4iq3aH4pMSnwrjNrd5W2NSdSlIT2pEA==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7lLbnkIxOEtDejZQ_sYiRtFwba9S7rLVAJyWU8iKKF_QiELcKTC8qSz98tNC8qdKfUqsLL1mctH7p2Jog2xvUltZXW5LX_whYYSI6JS_05Ym3igwI0A==)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdVRDOUwfMSw4O86ivd5ORo5zQpna0DWkadoeAViI_YvPW3j1KenGAOViiX_I3238lt08qWS1ZVhblX1bF_JTeFW3EYCkWP2_JQyBvtttSRgaPyYOk3BlmT4gVO9mldT1riqddmhgAxWtFFQc720M56CweiczamDJerORJcuR5kp1zCw2x3HFJHDoM7neN88vVqFZZqPznL38T8w==)
17. [simonsfoundation.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHG-677YRb61h5Hu3b0hjOgvxznwYDm64H7T6S8FCitouo0yFlFxF6uPbs-iEF0V2PfXGgc2d6lnrf-u0DvdACSbsITyQq6vNOojcrxO8Ut74d7dkYv5DJJIwBXAzkADYcvBYs_kxolqMW81uAEIJqOCPnYvZ0N2E3ashrRpKvDwgp6H9bs1v7kjrhxoUSRcw26Fo0nUgaGjgVWkLAfJ5s0H0WUV3s_uCKB3psMYSBSL5digjxXIV_2ykKU43OlcA==)
18. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEY4RJJBfbq1g7u-Av128Yog3ePo5UCqDNEOG5tMjmr8U1BtvhNWORSgLKytXXfgcqdTeuOgD9F99wfvHAD-rmh3R2SYf4Vj6q9QMzoT7y1cHFI1dISg7WQugNJsFX1gSnuXjfyUIIF6mz-ojKw6MYItiZsm4kV6ArtUVCZPvkcStVWRCNzwVThi310WheI54PtwTQyzl357ir5J8GN8YG84d_jP5WorXlzEN0vtSjyaFVt25SRUBOk7C3jemU=)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFns3yO2RJtOIENwp1AeSZVdKF2CglZWJFAZUpDjRtMawRRFqdj13bDUpNSYm_EgHfISyro68agYV6iQej0SLqqQdXcqn_vbudm2BOiP0rUA2jEwOx5w==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-n_NMVP_zG0rePVOPxYFCNFnJV3ykBHwyrjsEcpbH8LFRCdBT-QaK2bASHJ6ZniEFOvCoUmYJSZxOlcgEU8ZFnf9NM0y1mHqrBuibfAA4efGvjWD9-w==)
21. [carleton.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXVBc-MEbCfm_TodLrbAAvMpD9eKVyJ8TEyqG64hahu18Bhrmuv8o4P4gVJC3kHBTzP_a4FbOrY8w5mL5cwv2wmjob0JuQuGjoCSluw6EZ1b5Af5YFE8fQW4MO-ZL-XTF3RNDJNCy8hqdyyQQIG8tf8iU=)
22. [mathtube.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEX5n-zhOwpcKoxejOuyKHfZBfbzL6fuRfWMs9PmFdO4dlfGfmhnBSortj-R12kmkwq4kyYsiJcECE6ekkx93Xypp9mx9UeeaaDHpinkLe1f-i98KvzIYiZojfWG0qe28IMYHnm6-zAoMMrwqd1VkrilE2RqtNYDR3YBImyigHv4BJR3zcDCH4LYsS-jTH-Lre_Wn_ZBoV9sV_CsqxmeZxS5dCM6nWSRlIK)
23. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDVWvKf1FY015E00GYxAQrAz7N_QykXg6pUQaVlrbL9DjLCVq1JqH00XfupUMtZp7z89LWKBvjozO9aUZ2JqzdYvqANRsFedDlWbmYpLyD8-EZy9eymxjqrPqP4vBivM9u49Uq26akP9XjSu2VxDfIu3SB81b4KlCFN8DWZpVMsGcUqNZPFqKrpQhVxnkpPre4huYM87nRvcYjNQeS6xjG)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPQJC0DgDUZnuXFZgh8MTrT5R1Behr5t8mRuNnsIeOdsfPOvr-VgjylpenDp9pzDy_qkmTZUvFclUyyxxAza8F9FkL__hUTfoAAPhmLjMMHSP9ZfUPFw==)
25. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUqN2WXzfX2KvPe483JaoHVjFHZMFDhvxmlcN4Yz-PLpvFsIGvHERhkYXALsxpwSxicOGQsN_pMQJ0PihSBmfyJQV7wDqTY0qyqBbAekFrzmFFUZoFeuqz4GXsTy678ocbbNWYNNRRQ0bmz6eWRZZVt8uhhVrB0_DRsRuaHYUHvDsIONG9mZuXk2Nnf2KVBDZ16xV1t9wikCDSNZoguXYZHSR6B5f1u2KPIxqh)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYS3fFgYPEL22lAK1rt7b_Xu6TjGkxeI-e819Wy4T8WVGkaaZCEANcaLqqS4p0gxDHBdgMDyYQhsvgGg196ECwC3sYrGNwNjhRoeCSF9gXrIGNYZc9Ew==)
27. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnxwZtUesVe2wNItLAMQankFmt-OZzWuyLQNqiRaco6KS31WlJ8fNxap8t9PQmAW5jjh5bZWlAeoXfupfhesT3pYQQaddmLW_mfvlqNVUozVf92q4-qAaS4K5GHcpgqwJH00YuylHXzvaALFjGwBhhw2TevNLe8aXkd6pry5cWl9E8ReXZ_QgCL2lH25U30Yb_V7RjJcETTmwp2pZqdGlvtEA9gKuvfGIISRbax514qo8HJJaNf-k=)
28. [worldscientific.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGHlnCLP9_Go-v2j1j6PyWZ_t2yJSGWB_mEfd_70wi7LcxqWILyMIrKkUUfq3VhN9Hh31u4_8bgeNRdENh8_03V6XAkWJmhVGqFg2BCNrZmqXsKxYJkEWjihsG0YVXLUu-bLtNp-gIDhsFe3rPG8nd--6Pl)
29. [upc.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6NacDFpQo8HTfLodlXkpRIz0DlqscF2iwqfQMqKIwsZZxI3Xz2ldtybbbxY1nA2qlTrH6cbHF1qXqRHuOJdt-CFIp2mBhEPhn25VKXt7yunTKV2y9DdJm197-0MmQfzqE-DtjzxxVRGf5yj902t6-rAdTcvuASNil3ijv_yWBfLn7HbqQvo4C)
30. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEeQ11C-b5WFBDV9lv_u-vjMHXClscwY1zY0eBIDU8UeGKE7VQco6l9OQieZsFwVCU9kqti7z1jscZgSlSWuIU_PrMox7m1CXUaEMMs9vXVTfsWAX7jIlLUBtpR_S4IgFmBiKYWD9HpTC8OOcOhH2etrDc1vfb5ApUqfY31LIYTMQa3zB1ecI-uh-R53iqguWJh6BxAh8U=)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG37WlvcJSX36CMVQPTfQod57d7FmQAJuWSK5T_JEp47JAI0WuKqG1ZBJ8xk-x9bgqWRt44Kj-VhPxF-_6mL8fvlRw5IvAtZPzIJ7zVIeZemFyBKXb3Awo0TQ==)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHeu41L8z9MouKoLVJfv8sEfJLVId3QnnP-_mxjcjL-siMYHlIV0G98mrNHBLUBh65FDkkhAu1UbGVNCnYN9OKi5BsMhwRMMTIDUsu6wvBQvsV4LGF04g==)
33. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBh9LQAalxAnvdO2SQpCnKcCADRaZla2RXMVjLJiRxZWZtfbHUvVkvATXH3CKEc4tG0oxudre1S40AfixOnsHSKl2zJe7H8YGQVeU-3DEf8xitYS38wQ==)
34. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9uSXCW52ZmeW0KS-yNit3OpzLhOZhR70_eYoFIuycZ0rvGp2-nScob7tsL3l_A6AI5h8CUrWq6QTjR2YCt8lkngGe95RsZoa5sG9j651lXN6-1jtp40NMlLJouvLKSpThoVMAqRMdsQ==)
35. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOBSQu5Tblvx0dzZz_DrM8Yda9J3NlUERX3Duke44Qautvg_dSnj9ICQ5vOLqwufQ0RgtY_s8YewhHSJQ1iUSMCGFl8BkgSIVrSXrucJ4vkdpOnvsB7QVuUPk3UY6ysbn9CFrIt5di7GYB3yo9GZhkJVx9DFF8l2nANPLl6W4OudXsHp8_Unp5vRt1LA==)
36. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYiY7_Gk5hmMMjtrMenMbg1p_3CEZ4txv-CElG2YaUxP2pKrYYYI1HZi2NVMsQ19HAn5mXiys8hyhYPW7tV47btsdp9x7ulCbLHcfKblASj_TsfpWz1w==)
37. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4CsVyhijLtLZbrt9-ONHbSPQ6pkDdEqC8VoFBDlDqJr7YxQGwjpkqdAhVksqcyc8eyaUTiMyOGvAWtzA1XWXK6dIROycTPyXrAgqzsqwuxOv_kxJz6UYCnQ==)
38. [kalani-thalagoda.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_mI5B6SK5tlLH666awmnYHRSzyQuUmy8FvTFMEUMCEtz1vcWKAUPMtOMcJPBccnYkNEqBevda8O9Fy0TIgb2GuxIrWu_wchw9EAHaAD50Qx1JsD2lzUr-FO9qH-ivxg==)
39. [warwick.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHM9JFeZtTTSBMOe-d3mA2nrDH10TklKI1Qz_W-gSt0HVykLJUS5G44NSFvj0TKEtXg9SyWLUP6-XlJVHrECmqhSteBz9qGexFaKihvZ9nUwO8IPqC0zUiaCY15E0mIL4PGDpmWt8Knmk42u5Y7nt6oqdhhhfX4Zj06fuCcv0MxwjRo5LsK5rRkoPibcvlpJc_CaWIcFjlvFKw7jN4lYA==)
40. [kms.or.kr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1fffM57C--ijUID1mljXmvM2_rxHdhmqKG_jRUNczck7C1wHBeYE0P-pD2bEaKxWmX22jjHBKSd3GbGKJJYB2OmXQKFFWy0oeyQrRpRA4HDGLenRhG2ND7Hyk40cSPZLxNcpVlEWo)
41. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcCdcdRYpN5CHsb9DjCP_qtbLfz4cCfwxHv9QPgO5QgFD6nPhPWfhz7DzyBJjgqlxelwbuQugegN4IedvNrrf7G8ln_Jhyw8PNk5mn5hF3342GAKUJTtx68TuGZkYyMEchJQ1QKIyO5lKPUTUaeWbLTVi91vLmGiPdldqhUjzJVjYV5R_-w9Zf0iTkioipwGBDsg==)

