# Restricted partition asymptotics (k-cores, distinct parts) 2024-2026

**Pythia queue id:** 202
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChcwMFFQYXJmQk5ZZXlqTWNQZ0xDRXdBaxIXMDBRUGFyZkJOWWV5ak1jUGdMQ0V3QWs
**Elapsed:** 309s
**Completed at:** 2026-05-21T17:51:06.069282+00:00

---

# Restricted Partition Asymptotics: Advances in $k$-Cores, Distinct Parts, and Hook Length Biases (2024–2026)

The study of integer partitions, a classic subject in additive number theory and algebraic combinatorics, has undergone a rapid evolution in recent years. Between 2024 and 2026, researchers have deployed an array of sophisticated probabilistic, analytic, and combinatorial tools to unlock the precise asymptotic behavior of restricted partitions, particularly partitions into distinct parts (strict partitions) and $k$-core partitions.

**Key Points:**
*   **Asymptotic Normality of Core Partitions:** Through the use of Hoeffding decompositions and Stein's method, the size of a uniformly random strict $(n, dn+1)$-core partition has been definitively proven to follow a normal distribution asymptotically, exhibiting subgaussian concentration bounds.
*   **Moments of Reciprocal Sums:** Novel applications of Wright's Circle Method have yielded Rademacher-type asymptotic series for the moments of reciprocal sums of distinct parts, successfully overcoming the challenge posed by their non-modular generating functions.
*   **Hook Length Biases:** Broad classes of partitions exhibit unexpected structural preferences known as "hook length biases." Notably, hooks of fixed lengths ($t \ge 2$) appear significantly more frequently in odd partitions than in partitions with distinct parts, with analogous biases newly discovered in self-conjugate and $t$-core partitions.
*   **Shifted Hooks and Doubled Distinct Partitions:** The distributions of $t$-shifted hooks in strict partitions and $t$-hooks in doubled distinct partitions have been rigorously shown to be asymptotically normal.

This report synthesizes the latest advances in the study of restricted partitions. By restricting how a number can be partitioned—such as demanding all parts be distinct or prohibiting geometric sub-structures of specific sizes (core partitions)—mathematicians fundamentally alter the generating functions that encode these combinatorial sets. Consequently, exact enumeration becomes exceedingly difficult, and the focus shifts to estimating their behavior as the numbers approach infinity (asymptotics). Recent interdisciplinary approaches combining complex analysis, random graphs, limit shapes, and probabilistic concentration inequalities have provided unprecedented insights into the average behavior, limiting distributions, and hidden biases of these foundational mathematical objects.

## 1. Introduction to Partition Theory and Asymptotics

### 1.1 Fundamentals of Integer Partitions
A partition of a positive integer $n$ is defined as a non-increasing sequence of positive integers $\lambda = (\lambda_1, \lambda_2, \dots, \lambda_\ell)$ such that $\lambda_1 \ge \lambda_2 \ge \dots \ge \lambda_\ell > 0$ and the sum of the parts $\sum_{i=1}^\ell \lambda_i = n$ [cite: 1, 2]. The individual terms $\lambda_i$ are called the parts of $\lambda$, and the number of parts $\ell$ is known as the length of the partition, often denoted $\ell(\lambda)$ [cite: 2]. The total number of unrestricted partitions of an integer $n$ is given by the partition function $p(n)$ [cite: 3, 4]. 

The ordinary generating function for $p(n)$, which indexes the sequence across all non-negative integers, is famously given by the infinite product:
\[ P(q) := \sum_{n \ge 0} p(n)q^n = \prod_{m=1}^\infty \frac{1}{1-q^m} \]
This generating function is essentially a modular form, a property that grants access to powerful analytic techniques in the complex plane [cite: 5]. 

### 1.2 Classical Asymptotics: Hardy, Ramanujan, and Rademacher
The asymptotic behavior of $p(n)$ as $n \to \infty$ was first established by G.H. Hardy and S. Ramanujan in 1918 using the Hardy-Littlewood Circle Method. Their famous asymptotic formula is:
\[ p(n) \sim \frac{1}{4\sqrt{3}n} \exp\left( \pi \sqrt{\frac{2n}{3}} \right) \]
as $n \to \infty$ [cite: 5, 6]. Later, Hans Rademacher improved upon this result by providing an exact convergent series for $p(n)$. A key ingredient of Rademacher's proof was the modularity of $P(q)$ [cite: 5]. Rademacher's formula expresses $p(n)$ as an infinite sum involving Kloosterman sums $A_k(n)$ and modified Bessel functions of the first kind $I_{3/2}$:
\[ p(n) = \frac{2\pi}{(24n - 1)^{3/4}} \sum_{k \ge 1} \frac{A_k(n)}{k} I_{3/2} \left( \frac{\pi\sqrt{24n - 1}}{6k} \right) \]
This classical framework acts as the benchmark for all modern research into partition asymptotics [cite: 5].

### 1.3 Restricted Partitions Overview
When conditions are placed on the permissible parts of $\lambda$, we obtain restricted partitions. If we require $\lambda_1 > \lambda_2 > \dots > \lambda_\ell > 0$, the partitions are said to be strict, or partitions into distinct parts. The number of such partitions is denoted $p^*(n)$ (or $p_d(n)$ or $q(n)$ depending on the text) [cite: 3, 7]. Similarly, partitions can be restricted such that parts must be odd, even, congruent to a specific value modulo $N$, or absent of certain hook lengths ($k$-cores) [cite: 2, 8, 9]. The generating functions for restricted partitions often lack the clean modularity of $P(q)$, mandating the development of new analytic and probabilistic machinery [cite: 5, 10].

## 2. Partitions into Distinct Parts (Strict Partitions)

### 2.1 Generating Functions and Asymptotic Behavior
The generating function for partitions into distinct parts is given by the infinite product:
\[ \sum_{n=0}^\infty p^*(n) q^n = \prod_{m=1}^\infty (1+q^m) = 1 + q + q^2 + 2q^3 + 2q^4 + 3q^5 + 4q^6 + \dots \]
[cite: 7]. Utilizing analytic combinatorics, the coefficients $p^*(n)$ are asymptotically equivalent to:
\[ p^*(n) \sim \frac{3^{3/4}}{12 n^{3/4}} \exp\left( \pi \sqrt{\frac{n}{3}} \right) \]
as established in classic texts like Flajolet and Sedgewick's *Analytic Combinatorics* [cite: 7]. 

### 2.2 Probabilistic Bounds for Partitions with Exactly $k$ Distinct Parts
When further restricting the partitions of $n$ to contain *exactly* $k$ distinct parts, exact enumeration formulas become excessively cumbersome. In a seminal 1990 paper, Charles Knessl and Joseph Keller analyzed this and proved that for $n \gg 1$ and $k=O(1)$, the number of partitions is asymptotic to $n^{k-1} / (k[k-1]!)$ [cite: 6]. 

To establish strong bounds for smaller $k$ relative to $n$ (such as $k \approx \sqrt{n}$), probabilistic methods are frequently deployed. A random sequence $A = (a_1, \dots, a_k)$ can be generated by selecting each $a_j$ independently according to a tuned distribution, specifically:
\[ \mathbb{P}(a_j=a) \approx (k-1) \frac{(n-a)^{k-2}}{n^{k-1}} \]
Discarding the rare sequences with repeated elements, the expected value of $\sum a_j$ centers closely on $n$. The probability that the sum exactly equals $n$ is roughly $1/(n\sqrt{k})$. Analyzing the statistical frequency of these combinations allows mathematicians to derive the following tight bounding theorem for the number of such partitions, $p_k^*(n)$:
\[ \frac{1}{C} \frac{n^k}{(e^2 n k^2)^k} \le p_k^*(n) \le C \frac{n^k}{(e^2 n k^2)^k} \]
for a constant $C$ [cite: 6]. This demonstrates the power of framing combinatorial enumeration as a probabilistic sampling problem.

### 2.3 Parity Biases in Strict Partitions
A "parity bias" in partition theory describes the phenomenon where one expects partitions to possess more parts of one parity than another [cite: 8, 11]. In standard unrestricted partitions, the frequent occurrence of the number 1 naturally skews the distribution toward containing more odd parts than even parts [cite: 11]. 

However, parity biases inside *strict* partitions are far more elusive. Kim, Kim, and Lovejoy recently conjectured that for $n \ge 20$, there are strictly more partitions into distinct parts having more odd parts than even parts than vice versa [cite: 8]. While combinatorial arguments provided initial proofs, a rigorous asymptotic formula for the parity bias remained an open problem until 2023. Kathrin Bringmann utilized the Circle Method to generalize this work, providing precise asymptotics for parity biases modulo $N$ for partitions into distinct parts [cite: 8]. By formulating the problem through Nahm-type $q$-hypergeometric series (sums over partial lattices of $q$ raised to quadratic polynomials divided by products of Pochhammer symbols), she derived explicit asymptotic expansions for $d_{1,2;2}^{[cite: 6]}(n)$, quantifying exactly the scale of the bias as $n \to \infty$ [cite: 8].

### 2.4 Log-Concavity and Multiplicative Inequalities
Beyond simple counts, the broader sequence of strict partition values exhibits striking geometric regularity. A sequence $\{x_n\}$ is defined as *log-concave* if $x_n^2 \ge x_{n-1}x_{n+1}$. Following a conjecture by Chen, DeSalvo and Pak proved that the ordinary partition sequence $\{p(n)\}$ is log-concave for $n \ge 26$ [cite: 3]. 

Furthermore, sequences can be described as "multiplicatively abundant" if $x_n x_m \ge x_{n+m}$ for $n \ge m$, or "multiplicatively deficient" if the inequality is reversed. Bessenrodt and Ono famously proved that $\{p(n)\}$ is abundant for all $n \ge m \ge 2$ [cite: 3]. Recent 2024-2025 research has confirmed that this is not a mere coincidence. The distinct partition function $p_d(n)$, alongside the overpartition function (which counts partitions where the last occurrence of a part can be distinguished), independently satisfies log-concavity and multiplicative abundance [cite: 3]. It has been shown that any log-concave sequence meeting specific initial conditions inherently satisfies $x_n x_m \ge x_{n+m}$ [cite: 3].

## 3. Core Partitions: Combinatorial Structures and Tools

To understand $k$-core partitions, we must map partitions onto a geometric space.

### 3.1 Ferrers Diagrams and Hook Lengths
To each partition $\lambda = (\lambda_1, \lambda_2, \dots, \lambda_\ell)$, we associate a visual representation known as a Young diagram (or Ferrers diagram). Using the English convention, this is a left-justified array of boxes (or cells), where the $i$-th row from the top contains exactly $\lambda_i$ boxes [cite: 12, 13, 14]. 

For any specific box located at coordinates $(i, j)$ within the diagram, the **hook length** is defined as the number of boxes directly to its right in the same row (the arm), plus the number of boxes directly below it in the same column (the leg), plus the box itself (the head) [cite: 2, 13]. Formally, the hook length $h(i,j) = \text{arm}(i,j) + \text{leg}(i,j) + 1$ [cite: 4, 13]. 

A partition $\lambda$ is called an **$s$-core partition** (or simply an $s$-core) if none of the hook lengths of its cells are divisible by $s$ [cite: 2, 15]. If a partition is both an $s_1$-core and an $s_2$-core, it is termed an $(s_1, s_2)$-core partition [cite: 15]. Core partitions natively govern the block structures of the representations of symmetric groups and have deep connections to modular representation theory [cite: 11, 16].

### 3.2 The Beta Set and Abacus Representations
A highly efficient method for tracking hook lengths without drawing the full Young diagram relies on the "beta set." The beta set $\beta(\lambda)$ of a partition is defined as the set of all hook lengths of the boxes strictly in the *first column* of the Young diagram [cite: 15, 17]. Equivalently, $\beta(\lambda) = \{ \lambda_i + \ell - i : 1 \le i \le \ell \}$ [cite: 15]. 

The fundamental utility of the beta set stems from the following lemma: A partition $\lambda$ is an $s$-core if and only if for any element $x \in \beta(\lambda)$ with $x \ge s$, the element $x - s$ is also present in $\beta(\lambda)$ [cite: 12, 18]. The size of the partition can be fully recovered solely from its beta set via the formula:
\[ |\lambda| = \sum_{x \in \beta(\lambda)} x - \frac{|\beta(\lambda)|(|\beta(\lambda)| - 1)}{2} \]
[cite: 18, 19]. 

To visualize beta sets, mathematicians use "abacus diagrams." An $s$-abacus consists of $s$ vertical columns (runners) labeled $0$ to $s-1$. The integer $x = s \cdot i + j$ is placed in the $i$-th row of the $j$-th runner. The beta set elements are marked with "beads" and the missing elements are marked with "spacers" [cite: 18, 20]. In an $s$-core partition, if there is a bead at position $x$, there must be a bead at position $x-s$ directly above it. This means every runner on an $s$-core abacus diagram consists of a continuous column of beads starting from the top, followed by empty spacers [cite: 20].

### 3.3 Posets and Order Ideals
Jaclyn Anderson discovered a beautiful bijection mapping simultaneous $(s, t)$-core partitions to specific algebraic structures called *order ideals* within a partially ordered set (poset), denoted $P_{s,t}$ [cite: 2, 13, 21]. The elements of $P_{s,t}$ map to the potential hook lengths. A subset $I \subseteq P_{s,t}$ is an order ideal if $x \in I$ and $y \le_{P} x$ necessarily implies $y \in I$ [cite: 13, 22]. 

When analyzing strict partitions (core partitions with distinct parts), a further constraint emerges. A partition features distinct parts if and only if there are no consecutive hook lengths in the first column of its diagram. Therefore, strict $(s, t)$-core partitions are in direct bijection with the order ideals of $P_{s,t}$ that contain *no consecutive labels* [cite: 13, 22].

### 3.4 Bounded Perimeters and Euler's Analogues
The perimeter of a partition is defined as the length of its largest hook, which corresponds to the top-left box. Algebraically, the perimeter is $\lambda_1 + \ell(\lambda) - 1$ [cite: 2, 17]. 

Euler's seminal partition identity states that the number of partitions of $n$ into odd parts equals the number of partitions of $n$ into distinct parts [cite: 5, 23]. Strikingly, Straub (2016) proved a fixed-perimeter analogue of Euler's identity: the equality holds even when counting partitions of any size that have a specific, fixed perimeter $N$ [cite: 23, 24]. This revelation has spawned recent research into fixed perimeter generalizations of Alder-Andrews theorems and reverse Alder-type inequalities [cite: 23, 24].

## 4. Simultaneous Core Partitions

### 4.1 Properties of $(s, t)$-Core Partitions
A partition that is simultaneously an $s$-core and a $t$-core is extremely restrictive. Anderson proved that the total number of $(s, t)$-cores is finite if and only if $s$ and $t$ are coprime ($\gcd(s,t)=1$) [cite: 2, 21, 25]. For coprime variables, the total number is given by the rational Catalan-like number $\frac{1}{s+t}\binom{s+t}{s}$. Furthermore, Armstrong conjectured, and Johnson and Wang later proved, that the average size of all $(s,t)$-core partitions is exactly $(s-1)(t-1)(s+t+1)/24$ [cite: 18, 19].

### 4.2 Core Partitions with Distinct Parts
When we intersect simultaneous core partitions with the strict condition (distinct parts), the enumeration simplifies beautifully. Amdeberhan conjectured that the total number of strict $(s, s+1)$-core partitions is exactly the Fibonacci number $F_{s+1}$ [cite: 2, 12, 25]. This was proven by Straub, who elegantly characterized the set: a strict partition is an $(s, s+1)$-core if and only if its perimeter $\lambda_1 + \ell(\lambda) - 1 \le s-1$ [cite: 2, 22]. Consequently, an $(s,s+1)$-core with exactly $k$ distinct parts exists if and only if its largest part $\lambda_1 \le s-k$ [cite: 2]. The largest possible size among these partitions is $\lfloor \frac{1}{3} \binom{s+1}{2} \rfloor$ [cite: 12].

Straub, Nath, and Sellers subsequently generalized these concepts to strict $(n, dn-1)$-core and $(n, dn+1)$-core partitions, deriving exact formulas for their enumerations [cite: 22, 26]. 

### 4.3 Cores Forming Arithmetic Progressions
Because the poset $P(t_1, t_2, t_3)$ exhibits a "nice" mathematical structure only under highly specific conditions, the bulk of current research (2024-2025) has focused on cores that form arithmetic progressions [cite: 27]. The poset $P[t, d] := P(t, t+d, t+2d)$ was heavily studied by Lee, Lee, and Nam (2025) to determine the exact largest size of $(t, t+d, t+2d)$-core partitions for any coprime positive integers $t$ and $d$ [cite: 27]. This represented the first comprehensive result on the largest size of core partitions with an arithmetic progression jump $d > 1$ [cite: 27]. Depending on the parity of $t$, they provided explicit polynomial boundaries [cite: 27].

### 4.4 Restrictions on Parity
Further granular research involves analyzing cores where all parts share the same parity. Nam and Yu calculated the largest size of an $(s, s+1)$-core partition where parts are universally even or odd [cite: 18, 27]. In 2025, Cho et al. extended this logic, proving that for an odd integer $s \ge 3$, the largest size of an $(s, s+2)$-core partition with strictly even parts is $\frac{1}{96}(s-1)(s+1)^2(s+3)$ [cite: 15]. For $s \ge 5$, the maximum size with exclusively odd parts is bounded by $\frac{1}{96}(s+1)(s^3 + 3s^2 - 25s + 69)$ [cite: 15]. 

## 5. Asymptotic Normality and Statistics of Core Partitions

A major paradigm shift in partition theory involves moving away from exact formulas and toward probability distributions. If we pick a uniform random partition from the finite set of strict $(s, t)$-core partitions, how is its size distributed?

### 5.1 Zaleski's Conjectures on Moments and Polynomiality
For a standard, unrestricted $(s,t)$-core partition, Even-Zohar (2022) demonstrated that the size converges in law to Watson's $U^2$ distribution [cite: 17]. 

However, for *strict* core partitions, the geometry shifts. Anthony Zaleski used computer-assisted poset generation to calculate the exact moments of the size $X_{s,s+1}$ of uniform random strict $(s, s+1)$-core partitions. He observed the sequence of moments and conjectured that as $s \to \infty$, the distribution becomes asymptotically normal [cite: 13, 22, 25]. Conversely, applying the same automated algorithmic approaches, Zaleski and Doron Zeilberger demonstrated that strict $(2n+1, 2n+3)$-core partitions explicitly *fail* to approach asymptotic normality [cite: 13, 22, 28]. 

Building on this, Xiong and Zang (2021) rigorously computed the asymptotics for the $k$-th moments of $X_{n, dn+1}$ and $X_{n, dn-1}$. By studying beta sets, they proved that these moments are asymptotically polynomials in $n$ of degrees at most $2k$ [cite: 2, 26, 29]. For the base case $d=1$, they definitively proved that the $k$-th moment $\mathbb{E}[X_{n,n+1}^k]$ is asymptotically equivalent to $(n^2/10)^k$ as $n \to \infty$ [cite: 26].

### 5.2 Asymptotic Normality via Hoeffding Decompositions (2024)
The culmination of this distributional quest was achieved in late 2024 by Jiange Li, Yetong Sha, and Huan Xiong [arXiv:2410.18596] [cite: 17, 30]. They successfully proved the overarching analog of Zaleski's conjecture: the distribution of the size of a random strict $(n, dn+1)$-core partition is strictly asymptotically normal when the arithmetic parameter $d \ge 3$ is fixed and $n \to \infty$ [cite: 17, 30]. This completely subsumes earlier partial results (such as Komlós, Sergel, and Tusnády's 2020 proof for $d=1$) [cite: 17, 30].

### 5.3 Probabilistic Concentration Inequalities
The proof by Li, Sha, and Xiong operates at the bleeding edge of probabilistic combinatorics. They utilized Stein's method—a powerful technique for assessing the distance between random variables and Gaussian distributions—bolstered by Hoeffding's combinatorial central limit theorem [cite: 17, 30]. 

Because the structure of core partitions induces global dependency networks between the possible hook lengths (a choice in one column of the abacus affects the permissible choices in others), standard independent variables could not be used. Instead, they relied on Efron-Stein inequalities mapped across product spaces and slices, allowing them to decompose the variance into a Hoeffding decomposition form [cite: 17, 30]. 

In addition to asymptotic normality in both Kolmogorov and Wasserstein $W_1$ distances, they proved that the length of the random strict $n$-core partition, the length of its Durfee square, and the size of random self-conjugate $n$-cores exhibit severe subgaussian concentration inequalities [cite: 17]. This means the tails of these statistics decay at least as fast as a Gaussian, cementing the notion that core partitions under strict bounds collapse rapidly around their mean sizes.

## 6. Asymptotics of Reciprocal Sums for Partitions into Distinct Parts

While the global size of a partition is well understood, local statistics regarding the values of the individual parts remain a frontier.

### 6.1 Moments of Reciprocal Sums
Let $\lambda \in \mathcal{D}(n)$ be a distinct parts partition of size $n$. The harmonic (reciprocal) sum of the partition is defined as $S(\lambda) := \sum_{i=1}^\ell \frac{1}{\lambda_i}$ [cite: 31]. Between 2024 and 2026, Kathrin Bringmann, Byungchan Kim, and Eunmi Kim undertook a massive investigation into the distributional moments of these reciprocal sums, defining $s_1(n)$ as the sum of $S(\lambda)$ across all distinct partitions of $n$, and $s_2(n)$ as the sum of squares of reciprocals [cite: 5, 10, 32, 33].

### 6.2 Modularity and Non-Modular Generating Functions
In traditional partition theory, statistics are extracted using the modularity of the generating functions (as seen in Rademacher's formula). However, the generating functions tracking the sum of reciprocal parts are notoriously *non-modular* and lack the infinite product expansions necessary to apply conventional saddle-point methods smoothly [cite: 5, 10]. 

Despite this, Bringmann, Kim, and Kim established a stunning breakthrough by deriving Rademacher-type asymptotic series for $s_1(n)$ and $s_2(n)$ [cite: 5, 31]. By developing highly complex adaptations to their contour integrals, they drastically improved the asymptotics, achieving tight $O(\sqrt{n})$ error bounds [cite: 5, 31]. 

### 6.3 Wright's Circle Method and Limit Shapes
To bypass the lack of modularity, the researchers leveraged a robust adaptation of Wright's Circle Method [cite: 5]. Wright's variant operates efficiently near the dominant singularities on the unit circle even when the underlying function fails full modular transformation properties [cite: 5]. Through precise complex integration, they calculated the exact asymptotic mean and variance of $S(\lambda)$ across the uniform probability measure on distinct partitions [cite: 5]. 

Furthermore, this analysis intersected with the study of Egyptian fractions (the representation of rational numbers as sums of distinct unit fractions) [cite: 31]. By formulating Boltzmann samplers to analyze the contribution of large partition parts, they derived a strong version of the "limit shape" for distinct parts partitions [cite: 31]. The limit shape dictates that as $n \to \infty$, the geometric boundary of a randomly selected distinct partition will, with probability 1, tightly hug a deterministic continuous curve parameterized by Fermi-Dirac statistics [cite: 31].

## 7. Hook Length Biases in Restricted Partitions

A surprising phenomenon discovered recently is the existence of widespread "hook length biases," where completely different sets of partitions share counterintuitive inequalities regarding their internal geometric hook counts.

### 7.1 Hook Lengths in Odd vs. Distinct Partitions
Motivated by hook-content formulas in the representation theory of symmetric groups, Ballantine, Burson, Craig, Folsom, and Wen (2023) compared the frequency of hook numbers across odd partitions versus distinct partitions [cite: 14, 34, 35]. Let $a_t(n)$ denote the total number of hooks of length $t$ in all partitions of $n$ into odd parts, and $b_t(n)$ be the total number in distinct parts [cite: 34, 35].

For $t=1$, a hook of length 1 corresponds to a box at the end of a row with no box below it. Therefore, the number of hooks of length 1 is exactly the number of *different part sizes* present in the partition [cite: 34, 35]. George Beck conjectured, and George Andrews analytically proved, that the difference between the total number of parts in all distinct partitions of $n$ and the total number of different part sizes in all odd partitions of $n$ is strictly non-negative: $b_1(n) - a_1(n) = c(n) \ge 0$, where $c(n)$ is the count of a specific constrained partition [cite: 34, 35]. Thus, distinct partitions dominate for 1-hooks.

However, Ballantine et al. discovered that for $t \ge 2$, the bias reverses abruptly. They demonstrated that $a_2(n) \ge b_2(n)$ and $a_3(n) \ge b_3(n)$ for large $n$, and derived asymptotic formulas showing that there are significantly more hooks of length $t \ge 2$ in all odd partitions than in all distinct partitions [cite: 4, 34]. Glaisher's classical bijection—which splits every even part in a distinct partition into equal odd parts—was heavily utilized to map these sets against each other [cite: 34, 35]. To complete their proofs, the authors established broad, general linear inequalities for partitions into distinct parts [cite: 34, 35].

### 7.2 Self-Conjugate Partitions vs. Distinct Odd Parts
In 2024, Craig, Dawsey, and Han extended the hook length bias framework to a new pairing: self-conjugate partitions (partitions whose Young diagram is symmetric across the main diagonal) versus partitions composed entirely of distinct odd parts [cite: 4, 36]. 

By analyzing the generating series via the saddle-point method, they proved that there are consistently more hooks of fixed length $t \ge 2$ among self-conjugate partitions than among distinct odd parts for sufficiently large $n$, completely resolving a lingering conjecture [cite: 4, 36]. The generating functions were mapped using $q = e^{-z}$ as $z \to 0$ in specific integration regions, yielding precise exponential equivalents tracking $e^{\pi\sqrt{n}/6}$ [cite: 4].

### 7.3 Hook Length Biases within $t$-Core Partitions
In 2026, Singh and Barman pushed the bias theory directly into regular and core partitions [cite: 14, 16]. Let $a_{t,k}(n)$ denote the total number of hooks of length $k$ across all $t$-core partitions of $n$ [cite: 14, 16]. Through intricate combinatorial dissections of the generating function $\sum a_t(n)q^n = \prod (1-q^{tj})^t / (1-q^j)$, they identified intrinsic internal biases [cite: 16]. 

For example, within 3-core partitions, the smaller the hook, the more frequent it is: $a_{3,1}(n) \ge a_{3,2}(n) \ge a_{3,4}(n)$ for all $n$ [cite: 14, 16]. Similar behavior occurs in 4-cores: $a_{4,1}(n) \ge a_{4,3}(n)$ [cite: 14, 16]. Furthermore, they cross-compared different core modules, proving that hooks of specific lengths are strictly denser in 4-cores than in 2-cores: $a_{2,k}(n) \le a_{4,k}(n)$ [cite: 16].

### 7.4 Shifted Hooks and Doubled Distinct Partitions (2025)
Building on this momentum, Cho, Kim, Kim, and Yee (2025) [arXiv:2503.12040] published a profound paper assessing the distributions of $t$-hooks in doubled distinct partitions and $t$-shifted hooks in strict partitions [cite: 37, 38, 39]. 

For a strict partition $\lambda$, the "shifted Young diagram" is constructed by shifting the $i$-th row to the right by $(i-1)$ boxes [cite: 37, 39]. The shifted hook length of a box $(i, j)$ incorporates boxes to its right, below it, and heavily relies on the boundaries of the shifted row structure [cite: 37, 39]. Shifted hooks are a vital component in computing the spin representations of symmetric groups [cite: 37, 39].

By adding $\lambda_i$ boxes to the $(i-1)$-st column of a shifted diagram, one generates a "doubled distinct partition", denoted $\lambda\lambda$, whose size is always even [cite: 37, 39]. The number of doubled distinct partitions of $2n$ exactly equals the number of strict partitions of $n$ [cite: 39]. More critically, the number of $t$-shifted hooks in the strict partition $\lambda$ flawlessly maps to the number of $t$-hooks above the main diagonal in the doubled distinct partition $\lambda\lambda$ [cite: 37].

To extract asymptotics, the authors leveraged the Littlewood decomposition to factor the partitions into a $t$-core and a quotient, building exact generating functions [cite: 37]. They applied advanced $q$-series manipulations, particularly the $q$-binomial theorem and the Heine transformation:
\[ \sum_{n \ge 0} \frac{(a;q)_n}{(q;q)_n} z^n = \frac{(az;q)_\infty}{(z;q)_\infty} \]
\[ \sum_{n \ge 0} \frac{(a;q)_n(b;q)_n}{(c;q)_n(q;q)_n} z^n = \frac{(b;q)_\infty(az;q)_\infty}{(c;q)_\infty(z;q)_\infty} \sum_{n \ge 0} \frac{(c/b;q)_n(z;q)_n}{(az;q)_n(q;q)_n} b^n \]
[cite: 37]. With these functions in hand, they executed Wright's circle method to prove that the respective counts of $t$-hooks and $t$-shifted hooks do not just grow deterministically, but are strictly asymptotically normally distributed as $n \to \infty$ [cite: 37, 38].

## 8. General Restricted Partition Asymptotics (2024-2026)

### 8.1 Mobius- and Liouville-Signed Partitions
Recent efforts have also focused on restricted partitions bounded by number-theoretic constraints. Daniels (2024) [arXiv:2310.10609] investigated sequences $p(n, f)$ defined using multiplicative functions $f$, particularly the Möbius $\mu(n)$ and Liouville $\lambda(n)$ functions [cite: 1, 9]. Because $\mu(n)$ alternates between $-1, 0,$ and $1$ based on prime factorizations, the sum $\sum p(n, \mu)$ suffers extreme cancellation [cite: 1, 9]. Employing the Hardy-Littlewood circle method, Daniels bounded the minor arcs and major arcs of the complex contour to isolate the principal arcs [cite: 1]. The result provided new biasymptotics for $p(n, \mu)$ and $p(n, \lambda)$, quantifying the exact degree of cancellation these arithmetic functions induce against the Hardy-Ramanujan standard baseline [cite: 1, 9].

### 8.2 Partitions into $\alpha$-Powers
Research by Erdős and Lehner on classic partitions showed the number of summands follows $\sim c n^{1/2}$. For partitions restricted purely to $\alpha$-powers (parts of the form $\lfloor k^\alpha \rfloor$), gaps rapidly form [cite: 40]. Using the moment-generating function $M_n(t) = \mathbb{E}[e^{(\varpi_n - \mu_n)t/\sigma_n}]$, researchers proved that the number of summands $\varpi_n$ in a random $\alpha$-power partition is asymptotically normally distributed [cite: 40]. Tight tail estimates via the Chernoff bound verified that the probability of deviation $\mathbb{P}( (\varpi_n - \mu_n)/\sigma_n \ge x )$ decays exponentially, specifically as $e^{-x^2/2}$ [cite: 40].

### 8.3 Alder-Type Inequalities at General Levels
Alder's theorem is a broad generalization of the Rogers-Ramanujan identities, defining inequalities between partitions with parts separated by differences of at least $d$ versus partitions restricted by specific congruences [cite: 24]. In 2024, researchers fused Alder-type partitions with Straub's fixed perimeter analogue to establish reverse Alder-type inequalities in bounded geometry scenarios, bridging congruence constraints directly with the geometric confines of the Young diagram [cite: 23, 24]. 

## 9. Conclusion

The period of 2024–2026 has witnessed an extraordinary maturation in the theory of restricted partitions. Moving beyond classical exact enumerations, mathematicians have embraced probabilistic limit theorems—such as Hoeffding decompositions, Efron-Stein concentration inequalities, and limit shapes—to prove that complex combinatorial structures like strict $(n, dn+1)$-core partitions invariably converge to normal distributions. Concurrently, advancements in Wright's Circle Method have breached the limits of non-modular generating functions, cleanly resolving the moments of reciprocal sums for distinct partitions. 

Perhaps most intriguingly, the discovery and mapping of widespread hook length biases—spanning odd partitions, distinct partitions, self-conjugate structures, and doubled distinct partitions—reveal an underlying hierarchy in how numbers inherently prefer to partition themselves. By merging representation theory, modular forms, and probabilistic combinatorics, the current asymptotic profiling of restricted partitions points toward a deeply interconnected geometrical reality hidden within the simple additive properties of integers.

**Sources:**
1. [purdue.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEfVnqFx_pixMGLCS9UywaGSzXTKSr4z4w7xBXqRHKc8gwktJZ5Ix4pLm35NKKi9WVuuayK7dQbOjO0NtSDMjP6Qau502C-fdUmJNs48xVWDMG_FKpDhnTSQ-fDwUrIp-hVMP8nGq9B4JL2)
2. [combinatorics.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbAjg8R5PQNFeV-Dp4Bxnfzg7n1Opb_bbDory3zv4p8YXe0Y3RoZ3PaKzQceAwUwij9ABmQG-WkHAN1hFmkCXL4RJ09rmPTs_6-eN08VQXf5S-THQ0IB129GgFMhGdoDm-66bnxTjEbBnM13SbHHHbI6S7w6IiAa3OR2ZvP-zjthlfYrng)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgc-1lRZ_7caIMxDT4q5oGpvA2Rr8GRjP9NPr7n5jugmKyed9fSoGtR422CSm8CARlxahvoEACzUQTp5cgo4IC1hzq3YDfCqq1-vtDisg4aVqG0HoyxA==)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWLuYc_IGGGBWPTKrNE0VURrVzLesOGyq9l2qhKEZ-p6gwRWrS2AoKSLvRegkUPZK9SR1UXkaXA47bgrUMqZAvoijsSXzTXYcavmCNLVcdd5Ju0v9GrGMmycbKMVtWugWFu54WBSrpJvC8SyFkyutKZcE4eJMrYLMTkiSv2GBwVo2nJ3V4Jxm_qqewxOZ4EsFo-CGF9aaXtTz8wZpkHF3rNCnKAIixLm_VDxgsnjHN0ibHUQZtPc1ZRmaKDbD9zet_)
5. [uni-koeln.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVlGwIcndsHtP_tXCoDCvV7BpWr4N178uW3iCiMkrFEkom369RrxukEpwgYcvNnsNbbtKWdmGs5jbVyKe6LVoCHKGLRf5P5K2LxcczrZZT0KGC9UDatHw7hcAxxW0T60QjgVlOf24Rb5YwVxIsURjjqnTJl1t0OQRuKt1zrkOn1PzQcE1JFu2bR1pmISAv9jbBnQXGpdAApWW1quIMowcVzXBFBs_def-BYuKSc_xfAzSKmRQXapYCCGIt4zz5FqNC1rIynYKxcoWYWRo=)
6. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGvCzC87ITetaoxFzv8L4FAl9GryA9-yREpJhzTtm8mnBij4bdEjhSCg58ZrmLZxg0_cQFs5ODblMQriwbuyqPiKEZ9nV2PAhKBttv1NXfAlBM9LOYnD2catAPaGDKbkbudwIeZA0WJRA0e88DAIVBiDf32qZWiCCX16DFPCEXN1CdwLG3kkTquHk3J9p6qWv_KDOOwvK13TengR5CNNt3bb2GXqaUpzjxtgE=)
7. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHo3etLSMBfoMQLrYKtr28Y_UESI5J8rU72tNmhvhkJNveqs8HcM5ejUi0b_XtZU6qbiXa8ZtSa0RSYYk8DpOg8k-kmUZ99wCUgtqGt-uKlmV-LcWupMnUucKAHREh9Us_h9tWSSFM26v2Oi2R7S7KZIdpShPXuFVo5F1swF8RqO1z43RQRrTdvarpNChysr_j8kJiBR0d)
8. [uni-koeln.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJBFL-sWJW5p8EA8E8ywHhw19joSWEeJESi4XmNL9nVlAWyV3R_0c7G7_YfqTCH-eDNRgQuEJeY2rtBSWysGTYw5xLEKsEBunIh5uShslMCPyz0B-5L_rPAKVjHLlOaeGFxLwt06GQ7u2E-vXshf6-c45KXqpgF0vSbgkvSs_W0Ba2f0btT8PCypAz01J9ZqT4xjNLb632GF0b0pwiW9MEN0XplZsRsaKcePWhQyuo6LWfYViSlsL0LwkZ9mi7Q8J0ayg=)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrbhVZqMp1TxsDmLJoH0cY-ufrlvtACSQ9p-NDGwRbwmyokBlz7Rwwz_0vQa75bYCX2H-nWgbqv3lDzvUDRmcMjOU2s04-GfAfj4TQR0VTGtyRIR0LlA==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_dCY_cH7FHYcijU2tkgKs-t4TK_e93VcTFYTydbJL1GmUAqQ8mhTcTaReHQs0vQ5_blIulbC6jJ1I6vMNUK-EybktsyOL18jflJReGkT7fX7F4EY7Lg==)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEacBvrY73AJfBubx-s7tJPvkmuAaI1WHQPEYV0oBDv4qUzBGIK1Ny9XCRuKPyZSfvAz2QXJeS5LHUEFpzUf0bB6-HOHAVNY6cZE4Gb-alZD537SW-wU25ghvVW_h4l515RXfr9hjzTi_TEr340lP66JLcOY9N6nHQ81GoRmHFans1zAAI=)
12. [combinatorics.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFh435M-99ZPHpNKCsRM9wQRQuGbEZhFg12JiVD3g4spFgAWLuZSS2fs9tufjKmTAdvxmp_7mzOgRGt57Afe4vzv-vDmQjkzF2M2ndIrO2eDmiGt_yV1DOJUfmB1KxscLgB5hrpF6xko0kMULgoqSWgJiAcnJJWbP9XH0c_JNuHD7o=)
13. [rutgers.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqHxlWL9XQwYa0mNsCpL1rdhqPfYmvkfSNPN7cQqJWgQx0YBSU40F2lkN192l0NX9hF6gYAzgJW1qXjZu-Jr-DKTJLQGfJd4KLLX0qZ_E3AMRt4NsyYOUSTpIlP1TP3DT0qpMBniGjdZzdl5Y=)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGF6V_eHt6umzsbUpT4s-5-MRKvxuqw5boX-a6A1R00_ddklBSZES4oexyihu2JMv8qLDsaN-aSIJ9dHwPBjsUwRz8er3Fx9AUoQ5pum7hkgZDuZJVYbqRxrA==)
15. [worldscientific.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDagdKlNmMevZ2-gwvHAbfDhad_fwjMeVZpjgFlAc8fQKXiUNndytZUCxN0-Crk5jMVtm8ffSUSoMK1LhiDT2FcW0sCAVhhHuvG8zBi0OdTH9MY0VVDWK6wcWw9YUzJg49Jyif7_Zk-2CxJSSHfmO7ExiPGFMd3n7AE2N8hCKKQE2Cmf-D)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUryLZNyCGbx4zwCI0M87_nunlSLtrW4hor4GKGaqvCI2zKoncKPel9j3uIeoFCm0WNeUyNYvtlzHzlTl_9Cg1x57deIacX2VIgj_CtPzUj0voh2U-cg==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFAGbINxT0-ahMcS4g-UUn2vKK36EwDHBMHK94lfRrPEbQuJnmpsprdbq905cuMXtz2LI9_RAyIREvB6WjpOy4s3VNX7_yKQ4LsSJZG6fM-MyFwwDu33g==)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUz9C-QDR3xJ01KmCJR4fuLae9r9Ocj5I7k5a-ayvTl2DZwlY5sGmKie6nA53rmqBcq4dC_U9kPm5ZdizZLNTZBbZBC0tvArCV362kj76uHt8Is-levA==)
19. [combinatorics.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnkcjWGdU9WyOjAcrpDoV7Y_pqpTq7zZr_H38PQIZWGjXtKwtLxXkFevnBgRd40sbdcpmQSbRuQINrBaFSPT72FRkpZlqTXzbh3zwbIHcbGT6g6EE8zblbeOGFwAFK2cD5cVd0kuNeBk2YJDkdmUFRrdv-kzNSb7E7OK9qq32hNb3XD20=)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgy-S4XdF6LuD6NI0JNNFkvpX9qxAMIPdfXikHqv0HMOFNbLFKE-THc1KSLcvdY_iRKunT4NYxUCWZn0hU7jrjnMeaDfQlZiFfovPfb8YduXfMqKu1WAI-cpOEVvHC64E2_fPuufrBfkBPPslaSROQs3GLskmwf2i-ownMmsVNvRPTZHnFRU9X43dQ)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGc59iGaYCjtzt6V4Xjh7U6H4mLk1b-3V84KQ_tzGsqtEB2wlkV1gulRJyc-Wc64C2EG-Eux3w1tpBlB3cB4OsVJyyKzCk2HnOD7tca1Y1QpYhZWTvesg==)
22. [colgate.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHP4xB6oas9T_q5zb8vORte0If1SrXFdvOrpFK7xpWTi8Msqhkt7IzjetI4cGrQPEsClC6WypcxHWTcSAOCOnhRmM7CUp1rpypW_nR53QDK-RGrwVf9CT5AQyUCzg9L8Lmy2vr)
23. [utrgv.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzDUFmZNJ8_BUjo6GvKQnH6yoD_dYyuqm14HT9y4LKpBI3SJS8wQYBOjGR2fu14wTowqbxvWBjaz24NKXGNB5FfU14O52XShX3igpWfxtSt9LTPN5Xlq2UkbD2WP5ZtTP3gi1elhfQiIL2lNTr1WG40exFPvD8MqBsZf2p2xDCrf51HAQS)
24. [colgate.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHhAu_jdrRomnfcTvm9TfsQ_bdJSDGmg0RWArxZF2zshb2R9EE3_me2ObVeAgHMHB-7HBpbULeoedmuyPUWPErYPwcQ8y3igjTPDJ5iYg9YOatUFW06VZUj70v_WiTp_H3ow2y9XP8=)
25. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9mcgSIdjqNmSLHOpsiYRsYNwkG_IJeWbQBVnX7msX_Dg3CQ-MZ_JnQTSXGGQ_KEaGJH5uD87AqOUNY4rDpOjC5agP4-Vzj9kpWMHWPdKqV_h_uybOcwSIUOYf0E6CSu2AXpeAvwI9UB-Numlt2DfO8z3tVptG0Az1ne1f0PrO9nrwJpilwISxluOl7BbwVBC7nKwAszM-1jfZXY2kkTvq2pFms0whQZ6hkkqPW2IM8vrg6ZZsigAyHd85-JjGv2rGFVO3NwkT)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnHkeSyrmezq-KvjdsK0hqDUmBVQqW2EmwG9sQBWkMytEIuF46uGNQK_9vQiGzebbmRHo55ZygA4vh36CAnmAqyjc0TMRliNf1gNNBsxrmqjlVKctq8A==)
27. [combinatorics.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-HCw9t98OG0VzTyWiU_8Xpdh0_erZ_b5tanRaUrBXJx75QI3zDdQUBsJB2BJ6meIh6X1tlLt7C3U_DbT6nlOrLIkDhSDWYKs9SJmlxBrkWJvEPhXSH6uI7huheQNGoazwK00swMz41W08QZvFVhVuocaPJP1KlYwydLXM0AbJsSTPmEN4)
28. [rutgers.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-7NxMMvjRjHqIyrNOhklHWJNC89xLyz5-benEws2qR1ZEMC6oTniAds9l7SPFRXWPrDjLL3gdNOwvTNhu7Idt4TLTOgsDl_--y_h3l7SbNv3UNauc7yPIttln73jSpxaw_8Cq2DjUF4rgdQ==)
29. [orcid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGURuHSH5YtlyA4GEQfquf_SxtGef41T1_2LIaxP0CdlTx5RaZCcWD-kHVcwayeD2rHsCYvUCkp7Syae1u3-Qd707tLxa7sz0DKDEGG10gOKPVFKVkeT3tzXis-)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXWg08zvnjoNgBWTdC7xWP8oBp3ffz06DMsn8FtUSdyYBZyaiYw63DgJT6SDGHn5Zs5hr4six2KJY5Pph-3ORaLxAQLYA0xEGWDRUXDct_ttvucHnWow==)
31. [mtu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGeO_6gc_pKmQMU6aOXphVkKyRYupt9rmFVqt8tKP1232TMG0aOrtIl0Cnabkb8f5ezBeTy_PWzunuiOnF4-PHF9ntpt__ycvN4LXruGn9o6H6tKvc5iEpsmicm-H8H3uvcVvwxq0ZRwoomeYjGKyvB_sTznSIK1VRwtVDPq74LaSLEawqZgXaiDhs=)
32. [dblp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8-CJ22k0rvpNERUe_QedCmp0Jtg7kY1FieNmpxtzv63Q2hEZ8n3Xje6sJOvitCqNhvRvh27-0uRYh9qcffXPNHrST5AlTUOiQN9UaGRlW6TA=)
33. [seoultech.ac.kr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFauqBgZ0a6raUBqQznBUwQPsmZAie19NJlgh5uGTO1kGxLgaGN7H-zjiDGWkblTmIA8_KwvMjURynTvvd-BP6_H02vwM4YijSRp9VkdIxIVLF18rZqA-fuieAUYF2VhwGP5eoSopR3AhWriz__OdT6Y-bPGhBl3_1wL6bHgkU83C5oTIE_dDxEl2B0-wlmGwV9QuFTb158sfY_S04SZ_RUj_ULZTo=)
34. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETwBQUUgtpSLxYIYSchvUq0Lu4aec6_FDYuUx4DhQBUdL5g60E0Nln04ctrdKhc-Z8_nI5U7j2hJ0D0VJhwizQnPWdT2WJShlCZJv0rIWZgYrYMcQwXVhIhYLk-FnzHgBLm3zEQK3GV11lL-yXUnzx)
35. [ucdavis.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-WiWlSpeI1dbkVk5E7ueQ4MZ3wYouc9dEsUR-Kl4oWxMCEQFcllrycMgrTWuVUYQDGBqTaO90l6RH1dTXxoLhb4mMgI1asGYVT7NAVuI9Na-iEVEWX9HX2c4ZV7c30lRDYsk16Zxti9NuXy8FnGUrPses4O_xVGpPZ3c3xD7rTe5t7HzTI9z67hlILQ==)
36. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5nQO1U4yOSNi_J-0YGyieFDgmi7hcMvog29Dc91e08I9aOr7d1uXOQYNebiN2IkYhKOV7PKRUWjcB5TDyGYCPiti82pFC4HfeQmTBYZMHgoj4grUy2w==)
37. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFVeNnKcnSlOngqGnfWOrsAeAbl58THKOxB0cFjeu5wYJg0HuFhg4GCK77zhott3hsgHwZyQ5UIPTs-Wxykwi0O_IvBU8wRBNMBxIl4XJsuBuAp5lHEEA==)
38. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcetZ5iGkf6-DacMl9fbOoUPyszGFDt3bJV17ns5aTm1NCLwX7Z2jBgRANTMf2ZxVsKBRb_uurq9H5ndafhJrwupKq1-A0lx-tdFB-eCZyri8c7ryFOw==)
39. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtEdCAY6mc575M7jvf0qicn0zbyPA5Ltz9qYK4hH4jhVZCfu_sFlBHFYk5KHeb05OqO6E846XbQ19diJTokj4KsDYdyjS23NR2iX4FftYJmxoPZvZ8xw2ckw==)
40. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7qLpkbMnY01vVvWhdZIzNs7SXtpKx_D37dtaRRnD7QxTu6p2B7oXNDZ7DMxVxUDlJWxIkSxcZvuL_bSaYYe5_03aNL5-5CA0zGYkeIpW74cMt3EVMAcaSzbYpnILAhRsuGWbKc3P8HA==)

