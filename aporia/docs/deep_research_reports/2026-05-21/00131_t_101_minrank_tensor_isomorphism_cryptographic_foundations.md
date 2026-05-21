# T#101 MinRank / tensor isomorphism cryptographic foundations

**Pythia queue id:** 131
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdDeW9QYXJXNkNZN3hqckVQa3Iyd29RURIXQ3lvUGFyVzZDWTd4anJFUGtyMndvUVE
**Elapsed:** 251s
**Completed at:** 2026-05-21T15:55:50.891231+00:00

---

# The Cryptographic Foundations of the MinRank Problem, Tensor Isomorphism, and T-101 Protocols

### Key Points
*   **The Post-Quantum Imperative:** Evidence suggests that large-scale quantum computers will eventually compromise classical public-key cryptography. To preempt this, researchers are developing Post-Quantum Cryptography (PQC) schemes based on algebraic problems that remain intractable for quantum algorithms.
*   **The MinRank Problem:** MinRank is a classical NP-complete problem involving linear combinations of matrices. While historically used as a cryptanalytic tool to break schemes like Hidden Field Equations (HFE) and Rainbow, it is now actively being repurposed as a foundational building block for designing new, quantum-resistant digital signatures.
*   **Tensor Isomorphism (TI):** It seems highly likely that higher-dimensional algebraic problems, such as Tensor Isomorphism, offer a robust frontier for cryptography. The TI-complete complexity class bridges problems across graph theory, polynomial isomorphism, and machine learning, providing the mathematical bedrock for schemes like ALTEQ and MEDS.
*   **Cryptanalytic Arms Race:** The security of both MinRank and TI-based systems is a subject of active, intense debate. Novel attack vectors, such as minors modeling for MinRank and low-rank point distinguishing attacks for Tensor Isomorphism, continually force designers to iterate on key sizes and algorithmic structures.
*   **T-101 Operational Cryptography:** Beyond theoretical mathematics, cryptographic foundations must be applied to critical infrastructure. The securing of IEC 60870-5-101 (often abbreviated as T-101) SCADA protocols highlights the practical implementation of symmetric block ciphers to prevent fabrication and modification attacks on industrial systems.

### Understanding Post-Quantum Algebraic Hardness
Public-key encryption relies on the premise that certain mathematical operations are easy to perform but extraordinarily difficult to reverse without a secret trapdoor. Classical cryptography relies on integer factorization and discrete logarithms. As these problems are vulnerable to Shor's algorithm, the cryptographic community has turned its attention to multivariate equations, coding theory, and tensor algebra. These domains offer mathematical puzzles that appear impervious to quantum acceleration, forming the basis of the National Institute of Standards and Technology (NIST) PQC standardization process. 

### The Dual Role of MinRank and Tensors
The MinRank problem and Tensor Isomorphism share a fascinating duality in modern research. Initially, MinRank was primarily known as a destructive force—a mathematical tool used to break early multivariate encryption schemes by finding unintended low-rank matrices hidden within public keys. Today, leveraging Multi-Party Computation in the Head (MPCitH), MinRank is used to *build* security. Similarly, Tensor Isomorphism takes the familiar concept of matrix equivalence and extends it into a three-dimensional cubic array, creating a labyrinth of computational complexity that is theoretically appealing for zero-knowledge proofs and digital signatures.

---

## 1. Introduction to Post-Quantum Cryptographic Frameworks

The modern cryptographic landscape is undergoing a systemic transition driven by the looming threat of quantum computing. Classical asymmetric cryptography, underpinning protocols from TLS to digital currencies, relies almost entirely on the hardness of the RSA problem, the Discrete Logarithm Problem (DLP), and the Elliptic Curve Discrete Logarithm Problem (ECDLP). The discovery of Shor's algorithm demonstrated that a sufficiently large, fault-tolerant quantum computer could solve these problems in polynomial time, rendering current infrastructure insecure [cite: 1]. Because encrypted data harvested today can be stored and decrypted tomorrow—a strategy known as "harvest now, decrypt later"—the transition to quantum-resistant algorithms is an urgent contemporary priority [cite: 2].

To address this, the National Institute of Standards and Technology (NIST) initiated a multi-year standardization process to identify and vet public-key cryptographic algorithms capable of protecting sensitive information well into the quantum era [cite: 3]. While lattice-based cryptography (e.g., Kyber, Dilithium, Falcon) and hash-based signatures (e.g., SPHINCS+) have emerged as early primary standards, the cryptographic community strictly emphasizes the necessity of *assumption diversity* [cite: 4, 5, 6]. If an unforeseen mathematical breakthrough compromises lattice-based assumptions, alternative frameworks must be readily available.

This report comprehensively explores two such alternative frameworks that rely on deep algebraic and geometric hardness assumptions: **The MinRank Problem** and **Tensor Isomorphism**. Both problems are fundamentally rooted in linear algebra over finite fields but scale into realms of NP-hardness and TI-completeness, respectively. Furthermore, this report analyzes practical applications of cryptography within industrial control systems, specifically addressing the **IEC 60870-5-101 (T-101) SCADA protocol**, thereby bridging the gap between highly theoretical post-quantum mathematics and real-world operational security.

---

## 2. The MinRank Problem: Mathematical Formulation and Significance

The MinRank problem plays a central and dual role within multivariate cryptography and rank-metric code-based cryptography. It serves simultaneously as a devastating cryptanalytic tool and a constructive primitive for secure protocol design [cite: 7]. 

### 2.1 Formal Mathematical Definition

The MinRank problem, in its most general form, asks for a nontrivial linear combination of a given set of matrices that results in a matrix of a specified target rank or lower. 

Let $\mathbb{F}_q$ be a finite field of order $q$. Given an integer $r \geq 0$ (the target rank) and a set of $k$ linearly independent matrices $M_1, M_2, \dots, M_k \in \mathbb{F}_q^{m \times n}$, the generalized MinRank problem seeks to find a non-zero vector of coefficients $x = (x_1, x_2, \dots, x_k) \in \mathbb{F}_q^k$ such that:

\[ \text{Rank}\left( \sum_{i=1}^k x_i M_i \right) \leq r \]

If such a vector $x$ exists, the matrix $E = \sum_{i=1}^k x_i M_i$ is a low-rank matrix residing within the linear span of the provided basis matrices [cite: 8]. This problem is known to be NP-complete, a classification proven by Buss, Frandsen, and Shallit in 1996, which makes it an attractive candidate for constructing cryptographic primitives [cite: 7, 9, 10]. 

Another common formulation, frequently encountered in error-correcting codes and syndrome decoding, involves finding an error matrix $E$ of rank at most $r$ such that a given syndrome condition is satisfied [cite: 2, 11]. In the context of Minimum Rank-Distance Decoding, the problem can be reformulated to identify an error vector with minimal rank weight, effectively proving that rank-distance decoding is an instance of the MinRank problem [cite: 7].

### 2.2 MinRank as a Cryptanalytic Engine

Historically, MinRank first gained prominence in the cryptographic community as a highly effective attack methodology. The "MinRank Attack" was formally introduced at Crypto '99 by Kipnis and Shamir to break the Hidden Field Equations (HFE) cryptosystem [cite: 7, 9, 10]. 

Multivariate Public Key Cryptosystems (MPKCs) often rely on hiding a structured, easily invertible central map (such as a univariate polynomial over an extension field) using random affine transformations. Kipnis and Shamir observed that the structural weaknesses of the central map in HFE manifested as low-rank matrices when represented as quadratic forms. By solving the MinRank problem on the public key matrices, an attacker could strip away the affine masking and recover the equivalent private key [cite: 1, 12].

The MinRank attack subsequently devastated numerous MPKC proposals over the years:
1.  **HFE and its Variants:** HFE, Multi-HFE, and variants like HFEV- and ZHFE were routinely analyzed and often broken or forced to increase key sizes due to MinRank vulnerabilities [cite: 1, 2].
2.  **The TTM Cryptosystem:** Goubin and Courtois utilized MinRank to dismantle the TTM (Tractable Rational Map) cryptosystem in 2000 [cite: 9, 13].
3.  **Rainbow and UOV:** Rainbow, a prominent Round 3 finalist in the NIST PQC standardization process, relies on the Unbalanced Oil and Vinegar (UOV) paradigm. Cryptanalysts discovered that the first layer maps in Rainbow exhibit a rank defect. Using advanced MinRank techniques, researchers fundamentally compromised Rainbow's security margins, culminating in practical attacks (e.g., "breaking Rainbow takes a weekend on a laptop" by Beullens) [cite: 2, 12, 14].
4.  **Rank-Metric Codes:** Schemes like GeMSS and ROLLO, also submitted to NIST, were compromised via algebraic attacks that mapped their security directly to MinRank [cite: 2, 7, 15].

### 2.3 Methodologies for Solving MinRank

Because the security of numerous schemes hinges on the hardness of MinRank, algorithmic approaches to solving it are rigorously studied. If $q, m, n, k, r$ are the parameters of the system, a naive exhaustive search over the coefficients $x_i$ would take $O(q^k)$ operations [cite: 8]. However, algebraic modeling provides vastly superior heuristic and proven bounds.

#### 2.3.1 The Kipnis-Shamir Modeling
The original Kipnis-Shamir attack translates the rank condition into a kernel-finding problem. If a matrix $E = \sum x_i M_i$ has rank $r$, its left kernel has dimension $m - r$. An attacker guesses a basis for this kernel. If the correct kernel vectors $v_j$ are guessed, the system of equations $\sum x_i (v_j M_i) = 0$ becomes linear in the unknown $x_i$ coefficients [cite: 2, 11]. The complexity of this linear algebra search is highly dependent on the probability of correctly guessing kernel vectors, yielding a net complexity of roughly $O(m^\omega q^{r k})$ [cite: 11].

#### 2.3.2 Minors Modeling
To avoid the probabilistic guessing of kernel vectors, Bettale, Faugère, and Perret proposed the **Minors Modeling** [cite: 7, 11, 16]. A fundamental theorem of linear algebra states that a matrix has rank $\leq r$ if and only if all of its $(r+1) \times (r+1)$ submatrices have a determinant of zero. 

By taking the matrix $E$ with indeterminate variables $x_1, \dots, x_k$, and setting the determinant of every $(r+1) \times (r+1)$ minor to 0, one generates a massive system of multivariate polynomial equations of degree $r+1$ [cite: 11, 15]. This system is then solved using Gröbner basis algorithms (such as Faugère's $F_4$ or $F_5$ algorithms) or the XL (eXtended Linearization) algorithm [cite: 12, 13]. The complexity of this attack is intimately tied to the degree of regularity of the generated polynomial ideal. Researchers actively study the syzygies (algebraic relations) between these minors to predict the precise step at which Gröbner basis algorithms will experience a "degree fall" and solve the system [cite: 12, 13].

#### 2.3.3 Support Minors Modeling
An enhancement over standard minors modeling is the **Support Minors Modeling**, introduced in 2020 by Bardet et al. [cite: 7]. This methodology combines the kernel approaches with minors modeling, evaluating the complexity by multiplying the original matrices by variables representing the kernel support. This technique generates bilinear systems of equations. Solving these bilinear systems via Gröbner bases significantly lowered the asymptotic complexity for MinRank, leading directly to the defeat of several NIST candidates [cite: 7, 11].

### 2.4 Constructive Cryptography: Building Schemes on MinRank

Despite its reputation as a cryptanalytic destroyer, MinRank's proven NP-completeness and flexibility make it an excellent candidate for building *new* post-quantum schemes [cite: 7, 17]. If the parameters are chosen such that Minors and Support Minors modeling remain computationally infeasible, MinRank can serve as a secure foundation.

#### 2.4.1 Public Key Encryption from MinRank
Recent theoretical work has demonstrated that it is possible to construct public-key encryption schemes directly from the MinRank problem over uniformly random instances [cite: 18]. This approach mimics the Learning With Errors (LWE) framework but uses rank-metric noise instead of Hamming-metric noise. By sampling uniformly random matrices and hiding a message within a planted low-rank combination, researchers established a scheme whose security requires no structured assumptions (unlike HFE or classical code-based cryptography) [cite: 8, 18]. This pure, random instance MinRank is widely believed to be post-quantum secure, as no quantum algorithm currently offers a significant speedup over classical Gröbner basis attacks for random parameters [cite: 8].

#### 2.4.2 Zero-Knowledge Proofs and MPC-in-the-Head Signatures
The most active area of constructive MinRank research lies in Digital Signatures via the **MPC-in-the-Head (MPCitH)** paradigm [cite: 2, 19]. 

In 2023, NIST announced an additional call for Post-Quantum Digital Signatures to diversify its portfolio [cite: 19]. Several submissions leveraged the MinRank problem. The premise is straightforward:
1.  **The Secret:** The signer possesses a secret solution $x = (x_1, \dots, x_k)$ to a MinRank instance.
2.  **The Proof:** Using the Kipnis-Shamir modeling, the signer proves they know a matrix $X$ and $Y$ such that $Z = X \cdot Y$, where $Z$ is the target low-rank matrix.
3.  **MPC-in-the-Head:** The signer simulates a Multi-Party Computation protocol computing this verification circuit. They commit to the views of all simulated parties.
4.  **Challenge & Fiat-Shamir:** The verifier challenges the signer to reveal a subset of the party views. By applying the Fiat-Shamir transform, this interactive Zero-Knowledge Proof of Knowledge (ZKPoK) becomes a non-interactive digital signature [cite: 2, 19].

Prominent candidates utilizing this architecture included:
*   **MiRitH (MinRank in the Head):** Developed by TII and Politecnico di Torino, MiRitH optimized the MPC protocol to minimize signature sizes. It provided a highly flexible parameter choice, achieving Level 1 security with public and private keys around 129-145 bytes [cite: 5, 14, 19].
*   **MIRA:** Another MPCitH scheme closely related to MiRitH [cite: 2, 14]. 

During the NIST evaluation process, the teams behind MiRitH and MIRA recognized their synergies and merged to form a unified submission known as **Mirath** [cite: 19]. Mirath benefited from massive performance improvements and stronger quantum security proofs [cite: 3]. However, as the NIST competition advanced to Round 3, Mirath was ultimately eliminated. NIST concluded that while Mirath was secure, competing MPCitH algorithms (such as MQOM and FAEST) possessed either stronger performance profiles (e.g., faster verification, smaller public keys) or more heavily vetted security assumptions [cite: 3].

---

## 3. Tensor Isomorphism: A New Cryptographic Frontier

While MinRank is historically tied to matrices (two-dimensional arrays), the cryptographic community has recently looked toward higher dimensions to evade the advanced linear algebra techniques that compromise matrix-based schemes. This shift has catalyzed the study of **Tensor Isomorphism (TI)** [cite: 20, 21, 22].

### 3.1 Tensors and the Isomorphism Problem

A tensor can be viewed as a generalization of a matrix into multiple dimensions. While a matrix is a 2-way array (rows and columns) defining a linear transformation between two vector spaces, a 3-tensor is a 3-way cubic array (rows, columns, and depth) representing a multilinear map. 

Formally, let $\mathcal{T}(\ell \times m \times n, \mathbb{F})$ be the linear space of $\ell \times m \times n$ 3-way arrays over a field $\mathbb{F}$. An element $\mathcal{A} \in \mathcal{T}$ is a cuboid of scalars $a_{i,j,k}$ [cite: 23]. 

The fundamental problem of **Tensor Isomorphism** asks: Given two tensors $\mathcal{A}$ and $\mathcal{B}$, do there exist invertible transformations that map $\mathcal{A}$ to $\mathcal{B}$? 
For 3-tensors, two tensors are deemed isomorphic (or equivalent) if one can be transformed into the other by multiplying along all three geometric dimensions by three separate invertible matrices [cite: 21, 24].

If we consider an alternating trilinear form $\phi : \mathbb{F}_q^n \times \mathbb{F}_q^n \times \mathbb{F}_q^n \rightarrow \mathbb{F}_q$, the action of a single basis change matrix $A \in GL(n, \mathbb{F}_q)$ on the tensor is defined as:
\[ (A, \phi(u, v, w)) \mapsto \phi(A^T u, A^T v, A^T w) \]
Two alternating trilinear forms $\phi$ and $\psi$ are isomorphic if there exists such a basis change $A$ taking one to the other [cite: 25].

### 3.2 The TI-Complete Complexity Class

Graph Isomorphism (GI) has long been a famous problem in computer science—it is not known to be in P, nor is it believed to be NP-complete [cite: 24]. The complexity class **Tensor Isomorphism (TI)** was formally introduced by Grochow and Qiao to capture a rich equivalence class of algebraic problems that are polynomially equivalent to 3-tensor isomorphism [cite: 21, 26].

The TI-complete class demonstrates that testing isomorphism for a massive variety of mathematical structures is fundamentally the same problem. Specifically, Grochow and Qiao proved that the following problems are all equivalent under polynomial-time Cook reductions [cite: 26, 27, 28]:
*   Isomorphism of $d$-tensors (for any $d \geq 3$).
*   Isomorphism of polynomials (Cubic Form Equivalence).
*   Isomorphism of matrix codes (Matrix Code Equivalence / MCE).
*   Isomorphism of $p$-groups of class 2 and exponent $p$.
*   Isomorphism of associative, commutative, and Lie algebras.

Algorithms for Tensor Isomorphism are notoriously slow. Unlike Graph Isomorphism, which enjoys quasi-polynomial algorithms (Babai's algorithm), TI-complete problems remain staunchly exponential. Despite recent theoretical breakthroughs that cracked the decades-old $n^{\log n}$ barrier for class-2 $p$-group isomorphism [cite: 21], practical implementations of TI algorithms fail even on incredibly small toy examples (e.g., $10 \times 10 \times 10$ tensors over $\mathbb{F}_{13}$) [cite: 20, 29]. This intense computational hardness serves as an exceptional foundation for cryptographic assumptions.

### 3.3 Cryptographic Schemes Based on TI and Equivalence

Recognizing the robust intractability of TI-complete problems, cryptographers have proposed several zero-knowledge protocols and digital signature schemes based on equivalence [cite: 30, 31]. Many of these were submitted to the NIST call for additional post-quantum signatures [cite: 23].

#### 3.3.1 The GMW Motif and Fiat-Shamir Transform
Most equivalence-based signature schemes utilize the Goldreich-Micali-Wigderson (GMW) zero-knowledge protocol paradigm [cite: 4, 6, 22]. 
1.  **Public Key:** Two isomorphic objects $\mathcal{O}_0$ and $\mathcal{O}_1$.
2.  **Private Key:** The isomorphism mapping $A$ such that $\mathcal{O}_1 = A(\mathcal{O}_0)$.
3.  **Commitment:** The prover generates a random invertible transformation $B$ and applies it to $\mathcal{O}_0$ to compute a commitment object $\mathcal{O}' = B(\mathcal{O}_0)$.
4.  **Challenge:** The verifier issues a binary challenge bit $c \in \{0, 1\}$.
5.  **Response:** 
    *   If $c = 0$, the prover reveals $B$. The verifier checks that $\mathcal{O}' = B(\mathcal{O}_0)$.
    *   If $c = 1$, the prover reveals $A^{-1}B$. The verifier checks that $\mathcal{O}' = (A^{-1}B)(\mathcal{O}_1)$.
Since an adversary without the private key cannot know both transformations simultaneously, they cannot predict the challenge. By repeating this process $r$ times (or expanding the challenge space using multiple public keys) and applying the Fiat-Shamir heuristic (replacing the verifier's challenge with a cryptographic hash of the message and commitments), this interactive proof is transformed into a post-quantum digital signature [cite: 6, 32, 33].

#### 3.3.2 ALTEQ (Alternating Trilinear Form Equivalence)
ALTEQ is a Round-1 NIST candidate based precisely on the Alternating Trilinear Form Equivalence (ATFE) problem [cite: 33, 34]. 
*   **The Objects:** The public key consists of two alternating 3-tensors (trilinear forms that evaluate to 0 whenever two arguments are identical).
*   **The Action:** The group $GL(n, \mathbb{F}_q)$ acts on the tensors via simultaneous basis change across all three dimensions [cite: 6, 25].
ALTEQ utilizes several optimizations to reduce signature sizes, including unbalanced challenges (where partial responses are replaced by CSPRNG seeds) and utilizing multiple matrices in the public key to increase the soundness space per round [cite: 25, 33]. ALTEQ was initially celebrated for injecting critical diversity into the NIST competition, moving away from codes and lattices into pure tensor algebra [cite: 6].

#### 3.3.3 MEDS (Matrix Equivalence Digital Signature)
MEDS is another Round-1 NIST signature scheme based on Matrix Code Equivalence (MCE) [cite: 5, 30, 35].
*   **The Objects:** A matrix rank-metric code, which can be viewed as a subspace of matrices.
*   **The Action:** The equivalence map acts via multiplication by a pair of invertible matrices (left and right), mapping one matrix code subspace to another [cite: 30]. MCE was formally proven by Grochow and Qiao to be TI-complete, linking MEDS directly to the Tensor Isomorphism class [cite: 23, 36].

#### 3.3.4 LESS (Linear Equivalence Signature Scheme)
LESS operates on the Linear Equivalence Problem (LEP) or Permutation Equivalence Problem [cite: 37, 38]. 
*   **The Objects:** Generator matrices of linear error-correcting codes.
*   **The Action:** Determining if two codes are equivalent up to permutation and scalar multiplication of their coordinates [cite: 35]. 
While LESS is fundamentally a code-based scheme, it completely avoids syndromes and traditional information-set decoding (ISD) vulnerabilities [cite: 37, 39]. By operating purely on the structural equivalence of the generator matrices, LESS allows for significantly smaller parameter choices than classical McEliece. Enhancements to LESS, such as LEQ, utilize canonical forms (Row-Reduced Echelon Forms, RREF) to drastically compress the signature data, reaching sizes as small as 2.4 KB for Category 1 security [cite: 32, 38, 40].

### 3.4 Cryptanalysis of Tensor Isomorphism: The Low-Rank Vulnerability

As ALTEQ and MEDS entered the public spotlight, they faced immediate, intense cryptanalytic scrutiny. The core vulnerability discovered in these tensor-based schemes involves the spectral properties of random matrices and the presence of **Low-Rank Points** [cite: 22, 35, 36].

Although the general Tensor Isomorphism problem is exceptionally hard, the specific instances generated for ALTEQ and MEDS public keys were found to possess exploitable geometric structures. Tensors can be "sliced" into matrices. If an attacker can find specific linear combinations of these slices that result in matrices of unusually low rank, these low-rank points act as invariant structural markers (or "fingerprints") across isomorphic tensors [cite: 30, 35, 36].

1.  **The Low-Rank Collision Attack:** Beullens, D'Alconzo, and others proposed polynomial-time distinguishing algorithms based on low-rank invariants [cite: 30, 33]. The algorithm samples low-rank points for both public tensors $\phi$ and $\psi$. By computing an isomorphism invariant (such as the kernel space of the low-rank point) and utilizing a birthday-paradox collision search, the algorithm can match corresponding structural features between the two tensors [cite: 35, 36]. Once matched, hybrid Gröbner basis techniques easily recover the full private isomorphism [cite: 36].
2.  **Impact on ALTEQ and MEDS:** This attack explicitly broke the parameters of an Asiacrypt 2023 commitment scheme based on TI, and severely threatened ALTEQ due to the anti-symmetry constraint which accelerated the discovery of 3-dimensional 2-singular structures [cite: 22, 30].
3.  **Mitigation Strategies:** To repair TI-based cryptography against these attacks, designers must shift away from standard cubic formats ($k \times k \times k$) to "boundary formats" (e.g., $(2k+1) \times (k+1) \times (k+1)$) where testing for degeneracy and low-rank hyperdeterminants becomes mathematically intractable [cite: 22]. Furthermore, increasing the finite field size $q$ exponentially neutralizes the birthday paradox probability of finding low-rank collisions, though this significantly inflates the resulting signature sizes [cite: 4, 22]. 

Table 1 summarizes the NIST digital signature candidates discussed, their underlying hard problems, and the structural vulnerabilities encountered.

| Protocol | Underlying Hard Problem | Paradigm | Primary Attack Vector |
| :--- | :--- | :--- | :--- |
| **Mirath (MiRitH/MIRA)** | MinRank Problem | MPC-in-the-Head | Minors / Support Minors Modeling (Gröbner Basis) |
| **ALTEQ** | Alternating Trilinear Form Equivalence (TI-Complete) | GMW + Fiat-Shamir | Low-Rank Points / Birthday Collision |
| **MEDS** | Matrix Code Equivalence (TI-Complete) | GMW + Fiat-Shamir | Low-Rank Points / Weak Key Orbits |
| **LESS** | Linear / Permutation Code Equivalence | GMW + Fiat-Shamir | Support Splitting Algorithm (SSA), Collision Search |

---

## 4. Applied Cryptography in Industrial Telemetry: The T-101 Protocol

While PQC focuses heavily on the mathematics of the future, the practical application of cryptography remains a vital concern for existing infrastructure. One area where cryptographic robustness is critically missing is in legacy Supervisory Control and Data Acquisition (SCADA) systems, particularly those utilizing the **IEC 60870-5-101** standard. Often abbreviated as the **T-101 protocol**, this standard governs serial communications in the electrical power industry and other critical utility sectors [cite: 41, 42].

### 4.1 SCADA Vulnerabilities and T-101
The IEC 60870-5-101 protocol was designed in an era prioritizing telemetry reliability and low-latency communication over cyber security. It operates as a non-routable open communication protocol without intrinsic cryptographic authentication or encryption [cite: 41]. Consequently, industrial control systems relying on T-101 frames are fundamentally exposed to:
*   **Passive Attacks:** Eavesdroppers analyzing grid data to map infrastructure vulnerabilities.
*   **Modification Attacks:** Adversaries intercepting and altering sensor data (e.g., falsely reporting normal pressure values during a pipeline rupture).
*   **Fabrication Attacks:** Threat actors directly injecting fraudulent command packets to trigger physical relays, open breakers, or disable safety overrides [cite: 41].

In an educational or theoretical context, the vulnerabilities of automated T-101 device communication are frequently used to demonstrate the necessity of IND-CCA2 (Indistinguishability under Chosen Ciphertext Attack) security and Message Authentication Codes (MACs). If an adversary can manipulate a CBC-mode encrypted telemetry packet without triggering a MAC failure, they possess a CCA2 oracle [cite: 42]. Thus, strict authenticated encryption mechanisms are mandatory.

### 4.2 Hardware-Based Cryptographic Retrofitting
Because T-101 devices are typically low-power remote terminal units (RTUs) or programmable logic controllers (PLCs), integrating heavy modern cryptography directly onto the hardware CPU introduces unacceptable latency. 

Recent research has focused on retrofitting these systems using **perfect secrecy implementation architectures** placed seamlessly between the physical and data-link layers of the T-101 enhanced performance architecture [cite: 41]. To achieve the necessary real-time throughput without delaying SCADA telemetry:
1.  **FPGA Implementations:** General-purpose cryptographic algorithms are etched into Field Programmable Gate Arrays (FPGAs). This allows deterministic, clock-cycle-precise encryption of the T-101 payloads before transmission.
2.  **GPU Acceleration and Warp Shuffling:** For centralized master stations processing millions of T-101 frames, massive parallelization is required. Researchers have successfully implemented symmetric block ciphers operating in Counter (CTR) mode on NVIDIA GPUs, exploiting the "warp shuffle" operation to exchange encryption keys between threads at extreme speeds. This architecture achieved throughputs of 149 Gbps for AES-128, 143 Gbps for CAST-128, and 111 Gbps for Blowfish [cite: 41].

### 4.3 ITU-T AI and Security Standardization
The security of telecommunication protocols is also seeing rapid convergence with Artificial Intelligence. The International Telecommunication Union (ITU-T), via its WTSA-24 Resolution 101 (T.101-2024), has actively emphasized the integration of AI within ICT security strategies [cite: 43]. The transition to Post-Quantum Cryptographic models (including the eventual standardization of MinRank or TI-based algorithms) will require deep interoperability studies. Future implementations of T-101 and equivalent telecommunications standards will likely rely on AI-driven DevSecOps pipelines to rapidly deploy and test new PQC signatures, ensuring that critical infrastructure is shielded from both classical fabrication attacks and advanced quantum adversaries [cite: 43].

---

## 5. Conclusion and Future Outlook

The transition to post-quantum cryptographic standards represents one of the most profound upgrades to global digital infrastructure in history. As the field matures, reliance on a single mathematical framework—such as lattices—is viewed as a systemic risk. This necessitates the rigorous exploration of alternative foundations.

The **MinRank Problem**, long respected for its destructive capability against multivariate schemes like HFE and Rainbow, has found new life. By integrating the NP-hardness of MinRank with MPC-in-the-Head frameworks, cryptographers successfully designed highly efficient signatures like MiRitH and Mirath. Although superseded in the final NIST rounds by other algorithms, the theoretical viability of pure, random-instance MinRank as a cryptographic cornerstone remains intact and actively researched.

In parallel, **Tensor Isomorphism (TI)** offers an entirely distinct frontier. By mapping the equivalence of algebraic structures into multi-dimensional tensor arrays, schemes like ALTEQ and MEDS attempted to leverage the TI-complete complexity class to build unforgeable digital signatures. However, the revelation that structural anomalies—such as low-rank points—can serve as deterministic fingerprints highlighted the immaturity of tensor-based cryptanalysis. To survive, future iterations of TI-based cryptography must adopt exponential field sizes or highly irregular boundary formats to mask these geometric vulnerabilities.

Ultimately, whether deploying a highly theoretical Tensor Isomorphism signature or retrofitting a legacy T-101 SCADA network with hardware-accelerated AES, the underlying requirement remains the same: cryptographic agility. As quantum computing advances and heuristic algorithms improve, our algebraic foundations must remain robust, diverse, and deeply analyzed to guarantee the integrity of future digital systems.

**Sources:**
1. [tsinghua.edu.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnO7YBOJMonaRIHT6aj8v2ebRyHeJK2QKaJoCqy7saOf2UBGtDYhptDUEk3mXs4Au-nNIZX8SCEJzciQtdXhIhDi9ectlGxjoYRVmPMC6zuIRnbmrMDQ4kc6f2zUNVhdqSY8iFHDmOHekBzZKlaN-eu-i4vg63heYrFsBY7SKLtw==)
2. [nist.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJUnL0WgOBVWGHuXOdsk3qlx9WbUTbqiAVut2hn75PefdbC9fBEQWUB17fU1mYcrx3v2nUecYhKObA_nmoWRYomcky4IG9m8VE56IuCter8fUN-axW8yOiLaVPgmW5EcAJSLQHkW6nagYsvRhjgjEm0mG-5FL9LkJ1-PeTBHFNugYc7CszDdke7dK4K6jDZr4WZxvBr62WYcRpBv_-JLecXs-feEBC2k2iWMjlG3d0OYc9ThVaylaThTPDnn4MSc1ul-eFBuMtXNNwPlt5_M2lPyA=)
3. [industrialcyber.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4lLXtcvL31o3PfLGFER3jOoBCQrAM0RjKCsffUmpheg_FXs4jKVcZTnoewMbD4rBsK_lgkU1pUV90aQ7UAjQTjvVltqA87d_lvVM2ZCYJ3Og86TYSaW8IjSX21jUUIGO22oATp7QTxaXB7hsdxNcU60DctCMoN5pfy4bZnhdGLdHGCEM_S6VfucSPfC6GyiIhJWvyz9_8JnxA8dXnGYuTh1EnDIwe7ohtOXlr4HFUpzH1jzwFFxW-9IsWTKQpWkZHKVo=)
4. [proquest.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7UWavtxhUgcSPXeoWjnK_ammBCXmaduTnpj9mTNKRjlOqN3ixp4iwHZlb8DXxE4if2NcnTc5-XV14Azx4IiTop08BOy9Nb3h43p4WeTH7TWi4JGxQF5QRNsfChJJbuWRvTOkGpKYZztCAwGZ3DRRE_DUomPdzFPsb3ZVWak5n9e3dJprzIwDDtyedffr6Ldtzeg2jRdmTvhsWm44J-C364TbT3-K4cM0=)
5. [asecuritysite.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcmoYDO5adbn4abXne6wrb0b4A3Cr_haTTuCVj-1MkzL6T2C8y6-XIvm6lhsqoU_kjquqb8d-DqNbU_t7jgTh5mNxk7SFp3vaBN6eWwRtoawcWaSd464cwGexpWd0=)
6. [sandboxaq.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFRaJlWVW-FVGR0cDJsApLsTNzZig-w-3MKPpa3yLo5JnQAB2Wq7HIIZbS9wNQDqxCBwRp96b3rGzuycC4ErkPKJ38YifGLsZKuUoJ7_chCFMCpAKpvvqfcAwBaxqhnTkXX6ijFkUJplw=)
7. [unpaywall.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXoUsR7UxnFXQMOTAObIBFi77cJgxszkNDkQAhqGj8i_2yTQaQ7QiIfM2fBynBpLqV1S7d7aMpNB3rRMgtwaRxtSqEMSNI8qap0euTL-D3UO2ogu9aqj5WdQjTD0kLlFVjVg4Iu30p)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfXlLpC5foyC_k9i870mw2ddglo8F58p0Jc86EPo7kqsK2h2g90hoZ8Y25nIt3-IczVRx5iacugOPOL90eyUvKEuC708aBBRolFWC6Uha2khmFzAduLga_)
9. [nicolascourtois.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRyzEHJBxiz4quDs39NBuVGcvt4KlagxdKzm28yikq2kpXP8EmKPp-yGpXjB0LzqNO8w4eReUQLy80rwc3MBpnscFBK7T_SCCDTgPdPvVStBgpPBnbaaPbd3QGguliqj0ZUwvpISk=)
10. [minrank.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG54RlfUZUoMbOIu24CtvUHv8whZSaZX6aIxVblt2xCX02qI9FW5cLTZyEIr8jkzs0G8LuhX8x5u5bsZa3bjilMaKQtHtFXbFTnBw7tbLFidq2l9LdyQE_K)
11. [ams.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6z6EXhC6K0ShW7CQ4oSlZ2kQONFEyY-s5GC05Ej4ZEyGxm61vEh9tE-CNI_DGvVmUanll3jRvRmXjWZqh7M0WsJtfRqKM9jFwgoRoOCU_NP46UghJRBCslsoWq15oYQc4n1xAMUwHZEv2JHWQVzIBc0JyfDyR-N-SfHvd5RYalrMI52Tcp3-aHwBf9THxpvpYflH-2hXYgQdZ5iEtjCC8-tuBBiKtNTIW4blI4cwWgRk=)
12. [nist.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6hajPrgc1SsSkwESxtYX8VHa5P4qW40P2Q7s5vbSKVZI4b9bkvd5AZynA9HMpVgIhCvnmW5txH1-L_l_YeIqZZeW6uJYCXOEnFAljeH1N55hHN4OsZkW7UE6hfqT3e1f2FeW0T0qn_1oJ8MSEiPq-3RU=)
13. [sorbonne-universite.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEY4i2Hpfrxd6UAsxq-C3NczdtExdjML_M5pSsUcg6EdfvDZ6KryAeXQnJxJfd3wQhYGLSSLxrekXKiwLTcKzAUeXzRVsHVItfRcIa5tLvEg-KSSkWT_nongbQ75IelFb3gEehFxpxVwQIMmVigNXx39-vo4r8D5FwjoHLyAKw2xhRZRdYnfIfWlPdu1cXbfNkHuusI9loKPpEdQLThPIFXVP0s6zHNIOwvZAuArFkrqVCm-cUDqvHx)
14. [growingscience.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGIs3xge6okmRp_AEsjsF0UifcrPQJvn4RxT5kCoiSa8KsRTiTv7YKfXLrLKBeTnGrAjzeT8vEFoqyaQVGlonDGv82wumuAZUb_C8cFB7ws21q5wPmYdPhFtXTqwY2hUkxkJoHV3VRWO0MappZ9ytNuO8Q-nn47-JJbXdk0hNou3AwcvsQ_yUXn4Kb3DykxPI_st5POHQAg3SO6ed77RDnM04Lo5ZAEudWz4G3apmI=)
15. [lip6.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjveZgbGF_yRxKEVJdSnU3X7wQPHFhQaXAYLKwYhEyUKFbufrj4F794oBDNe6-8iIekyXCko6JJF4tJ6LIIpINmVBi0Mme81gJGjCN9wgZNm7GtV03UBUB6D_Ps-M4vR_ToJ5WlUcxHMk=)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-zOV-K7n2PVTSgZcB8kDzdvH4fsqEFdYGE7nl9vkcE2q8tyTRv0m3NJO7DITCfRhBgJEYQR34l-TE93kYf8ofZWVuubQ3hx5e_3nHYAeuNBVtG3FQcewkWFEZRKwMxrG4n1RmQY9VGWrMin-IiBbeAZYESEZ7abh058FI36CmEpis3jdcoGpETRcw7pm8w5KKMfJ_mP0nUlWRTZIkEgfstX1A7TzaYd5zDMizxOl7)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQpAus6K-EwwJDrvkPAs4lkuEohtRTf88ORKFigCtAHfN1z5tVLWNcMpsXa-KGoiONha64-mvYs-qGU2nMtsC86osYY7o0m1LwDPY_933Lf6UWccRQ)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_SHWqmJ-7hPtZozhc-u4TSy_rWAJHQ8PsDf7-2vHSPaAAXHFgdYsyDfgMIuAiVu7-ivQprpyi3K_I2bqXPcij4h4U6HoVy9UIhfU6WFllgiy9njSk)
19. [pqc-mirith.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFSrZPOKFgOCjonKEgs_FV9XU07OyFFuBAC0aNtq8WOcViGYXmGbSdZzMHOQdQpxEIBYhXkOTViRxkuCxMnTk5galUEs3R49FyBqNb3)
20. [amsi.org.au](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhAuHWXt0wHPINtz7iTIw_Ryu1FhRUh9T0qfCyfxU7P6XosElYoUMp5-jDfCwcf0jr1ccRi_fgNqSQBNGWDfEM-Q50tKOshvA8Ao3Vz-vyCTSlV9Io-cJxe4CTbFXX0hIrZuuOEtT26tujR4H-yWqFQ95uexKC1kXvX6QUg7CT4trcOruQedrU2MSfaCfAJAA9x5c=)
21. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHr3tNqqjHVsk3epiZf2XPZv6FQhzRK-TfBZG4zaaeMRSHwDyfjS_A73EQAsT8bL5RANHIWqqMeos-vAlQ9meT6sOXXwBg0gYM3fg_Q7g0qgADCGz6_qdWG8BVCCBBox6YpDZw27fu-nDpgL715UyrxcUfcdrHNyH_smOEOd7hhJt9ph6Fe0IYyPM_rEGkOYF6seRV7D68=)
22. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFSF9Gi0YctJCKdEf7BwLItMj9Cqt-0CwkIMFiLJA1FD0elfnBQta93xAZ09xjUUCKMfn4kJkxL-StHCcM9y6UdQGXnQTTYlJQBQ40UOv6l2hFO9F7sbhHeAkdwuwwpGMlVQYjnBIvTM_0LuadfhJCoy1mPf5IStZsOQZAEpYeL9GjnPRinw3ZLl9quwl8oSJAaRopbkF-TYg6blU8H6ceMe3U=)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOioUtf2tc3j8vbqzk9cYgS6T5yuRZTkN9YHr_K9FM8vUbcXzgDcEOKRp-4mZE7Nggne_REsDL9qUeWFdhdKrs8B71bgiVVxCkvVx29mOhM-6uchJaD9Wu)
24. [ntu.edu.sg](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkl8osmivTtIV-N6z1LLwLueLDwDfHUlfFuYgT4cwUKuAfb45tsWDMbEeU816-zTG1729JxEpNNXFP4RFejUyGBvtaua5SiTtpHSlN3683PdPyqHnEUrOSj817NMAt2Kx-y4C4YOzbX14-Ew6CWcvFx7trhIDoq9OiUBAnhlU6UiCDOf_iBP9PTExUhuHwIIG3q6lVu659AFM0z9Ee9rKzBnotbVh1Ai3NB7iRa5FYARW6adkV3EGy6cwya9AbJo1hss9HWm8Tl3FP7wpR5zOgnhw=)
25. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxs4tmyROdTszV_TnS3cHzgrJdWtYGiiP-lGct8AraXZx8WNXEJdW6D9x45pkoRF5zUsRQMChmsSAVTHCvbfS4E8-QXyh4XtLu7KNNTCm_bXHfgvZNp2a00XBrgtF8lQ==)
26. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGywWZKtpL0Whid370Gm3bePD9gj6gVsvFd8Lr2VR4IsxjqyIdH9eFVoQtZpXLh8p1PwUjsfNEIZ7IA4nZJLUR6yb7hH314sL7smlY93GSgsCjmMcpyvqhhIIv7Aceg288dBA==)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRoM2r2s3TXW_B8oZxPBT_tJlj4zHCwmiwNqlBnc_872nTjYpNhqFVXq8o51zWFI1MVPOTnIzpG1yEtKuU1AOP4EnFubMjL12Ut8Pu_xyOXsqgzyDU)
28. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGl7FXXAz_JHmmwZ4i1wYI8HMqM1XzFJxx7rFLUSyG_d4QgoxFgY92unN9Khui1qu0tnKQhViLS8-fxoqPfG2r0Wm-q7Koru6Vot-qDL_AnnX9Op3tz419q1zvVHIEJnxUQDCnZHTTOZwJSVRrYBsoaJFLAM9K7mOMyz1ORiiL1abAgJb8CI4ro5kBqcHEgZ8c6E--mg1BHFU8HsPH4)
29. [colorado.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGg9ON-sNazdEluQpwQUsSeav6qH3vFp85HEPj78wPweo62mWKZCv6FFTe07oR9mtkETKqkch4JoXZRawDaIxv_oL7-kaB9oEB7FzLbyzQ--YSd94n2AVmYh6xsAyeViHeDxpORi8s)
30. [epfl.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHzOeidcyQYzea3B3c-t2HoboSGFyvpBSQL67_eVS7wyhqryndK_ywTd5C0aA9su1Kf_EhjueH2tw6fvp9ZJBrJQSuSPU0D9OtoqGkgfkAixQk-g0qhDQ8XAz809xXPQDViDndvd_FuvGRp5Ju1n-C0ilaGeaHEhPJSyKXNxNM1SajCGEeN4vwciKM=)
31. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMmGV7d5mGgl4iAljvtm7030Ap09zxyUhtxlso_aJBIsls1PL_nUOgwqZDIHdY68FV_WfiCcbIhKxdBe495b-JpEofw3sOKUCx_uuP9_erdOzjZ4D21KcctxWNHxYYzgryKVc=)
32. [nist.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmoPQRzQe03On5LYAS26el5NM8S9iLpAILaCxV1wcewqrszg1VChbDoACnaS9QCBIBiLzd3lYUg2cBWQS32wvScTkw5aE_41SIJXBOWVEZzLu1VVCP3zohSJ2B1z89E1dfHAdLVe8P724eWHJbhuln_nSSFjZJ_S--zX1W98ftANo5lJdiDQ7nleYoOzTQOR4k5EmcjlHoyM8=)
33. [nist.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEYJ_34jNc5YcBq1_qPFiIFm8GMLM0dR06wKRnoKIhT7UIXMSV2s1Z-yh0n3rDSloTC3kFFA6jS_4c0UcA-AhiTGf9unufRyYdTSkVMA6PkKZaFaheiNL_7R6c3GAeVhgClIzFW5IariM12-RCoicNoCtFjlcVzCrR2WyyUtaBEd3jq0zy4nFGFlb1eM38dmArHO0hUheUrc8Bo)
34. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGc6TWiKzvr6xFeRFt3u6_e4ZgjX2fU3_w3zSZ3lvL0JavQesz6XmocI9olmDOQRf_HL71F9H3IDoErPEEMjWhKTv7wsSEgD7HX1PYp8GoQ-rvghegbzvJc)
35. [nist.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLqhjept-O_Iu8a3ZozHW3N6-p7jUh2OpJ8EHRVevhm3kihfHldAmQvx18nQdfom2g_so2Doc1OPuiCrRKfGzlOBrhYV8-TxQO4s8WN7wjOkwI6vBX6ithMRbpUIy4yGJWtUXekd0vKGwnnpe66-3W6-tPPWs5tWbcYGG1hWisO_MhtwYOAARsA9_TcNXAPna9EsfOX3HtGQInICY32uRiqm2292bW-it3O_x3EDnGp385fymqZjHgp_-VVlhiFEaopVL4xKIllCU=)
36. [nist.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJ1Wv1i0pTlTkXdo-j2pR8cKOQNBN1RjGITh6zOHaCAaKLYytqYIiNbYKaDtuhFneI4Ns9T2hAShVEgPtvb0MqAEp8L_4bOL0Yet1n4C748h2zdeC0IsUnwe8FBdu8vl0Pt5hAU2UwDJGeUNKNBDXg0em4034SuWEibDaDiv9O3F9-qfE_8Y62f4S09qCcOhM4HkNm9bS8yFl4QeeD0jCrb6eOjZtXqCm71rbm2rO2sfLduidOelZWsh7u324sBLSN4GcZah7e5tIzIQ==)
37. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtyU6zfG5htFvTCA0bfzGs81Z9oVCwSDAkvlyUcKEDS595FldGFVzrjVQrX-Sci3rsUjWmT2oSgffUuM0K5I9jgcnzs4OC--cY-x_jJEO3Z18xyRB7z9osUQ-6XJQcRwaAmnVmDkQ=)
38. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElQ0RNvg6vlsr67nPNBzFzEeZwp4h1x3wpg1x3SiD7MQwTsmkwn406b1JZ24Mgv9IPrF4etXYq9eNDa-P0Mo5EoV3bSi6KRJBlyjMuyS48NuUStzqpEzGqWZLLJ8ta)
39. [cloudflare.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqSzQ-a2N8M8cQeoHvqFUbGPmRbC3voLZzrafR8ls9a73S8LjwB0SUI8ILB4nyLbdUolFwWgbUtC8jssaM1K-1uf2MY1-ZUC-o1pTAkC-Msykjb3m9SjJ6P4a93e5nofwQY0clYDvAnRfeeIEc6LU=)
40. [nist.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEghu8okmtVqLaUUCNYQMQHlaULWy2P8GoJTl-uJinT3lRFD5O58bKXdJGOnu-klogHHGEbB0ys1oCTsGEYs3dEGWM68koF09NEgSNLBm62UX4IVpI0fpb1YmjPn_Ia9TAnYhvx8hgzKnW2qgVKtakbx_7_r99tDBdoE73RaXN45F5XusaY2q7OfaoXPhDFj07iZ5C4o3zVU051qU6aF9SR)
41. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAVa9J2yvaQNZGnTuWzx71iveKcBi0GRf-5doFw8JYaOv3c0A3-In8AQ-lQmGv8MAbiUF5m6cw79D3U706DGABknt31JXq4eKTfoHuEEoMdN2SnlfiU2rZGoeg3GPYqfm0TwZHqgJITHHsFeZdsmkHYoPRmA0__90u1VUt6M8SQiMEUzDuLC9Sx3qLM_E_J7KgG4IqKScAJxg1VXKwuER1d_vBa3gpCT090CbMsSlrwaUzCo3iKJorLlq0aHl1kX2L3Ga5)
42. [jhu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHiI-1j50VGlqUaey8TG9v_p926JvtsxB6ZMBpy9W62BhUwHc7lUM_Xb1zQW6DiWFxpzk1RakUTFb9cJ-0F47HzW6-ceyMFEFAmg70fVqRfyZbS16ray_aNIQRoFnPTvInLLytrbHDkikXVHyB4Z13OcQmhoGwh4AnBBEhtlIab)
43. [ietf.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxj0Amty9qwbI-Oxc0ZsmMoBFX928q96by23Un1PQ5ZDPRhNjsZiZuVveqX9MKLxd8Ih5soS3yiVeAzKfCshzS_Z_gt8g0jDbU6C_GzaV4OBglEvKmE0hyBZfugbLHqySxB8NE9vYXghNrO-NxobYC373J68AeOo0Tzy6zdXioMn6Tuwf9PTFK7k13FRYUqnPs8gr0p-5FNyw0eG18XXIoSAmHMpsVTqAx8NLfJoESccJLwRUlGwER-mh8d8Walq_nET6wnX_n5NHtA3-irtoX1HxSMMAbk3gPFyLfh8gDQrc73lePTg8Y13BKw699gDQd1H2EMZT5cPitbGLTKvzxX2nH-WiisceXqkJn5Q0=)

