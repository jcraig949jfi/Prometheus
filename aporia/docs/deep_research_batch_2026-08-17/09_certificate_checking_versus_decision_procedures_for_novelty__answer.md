# The Epistemology of Automated Discovery: Decidability, Novelty, and the Scandal of Deduction in Theorem Proving

**Key Points:**
*   **The user's theoretical hypothesis is formally known in the philosophy of logic as the "Scandal of Deduction,"** a concept originally popularized by Jaakko Hintikka. It posits that deductive inferences and decision procedures produce zero semantic information because their conclusions are logically entailed by their premises.
*   **However, this strict semantic view is strongly contested in computational contexts.** While a decision procedure's logical closure contains all true statements within its fragment, the *computational realization* of that closure is constrained by complexity. Thus, for computationally bounded agents (including humans), the output of a decision procedure is highly informative and can be genuinely surprising.
*   **A direct refutation of the user's "Attack Vector" exists:** The Boolean Pythagorean Triples problem was solved by a SAT solver (a decision procedure for propositional logic), revealing a highly unexpected strict cutoff at the integer 7,825. This generated a 200-terabyte proof certificate, demonstrating that the boundaries of a decision procedure's closure can be profoundly surprising to domain experts.
*   **The user's intuition regarding "certificate checking" perfectly aligns with modern proof assistant architecture (LCF).** Because finding a proof (proof search/decision) is distinct from verifying it, certificate checking acts as a finite, computationally tractable anchor for novelty, establishing trust without requiring the checker to navigate the entire logical closure.
*   **In Automated Conjecture Generation (ACG), novelty is almost never gated by pure decision procedures.** Instead, systems like TxGraffiti and the Ramanujan Machine rely on empirical heuristics (e.g., "touch numbers" or gradient descent on mathematical constants) and external literature comparisons to evaluate informativeness.

---

## 1. Introduction and Problem Statement

The intersection of automated theorem proving (ATP) and automated conjecture generation (ACG) presents a profound epistemological challenge: how do we define, quantify, and verify "novelty" when manipulating formal systems? The query presented theorizes that **decision procedures cannot serve as novelty gates** because their termination merely confirms that a statement was already implicit within the logical closure of the axioms. Consequently, anything derived in this manner is seemingly devoid of genuine novelty. The query further postulates that **finite computation and certificate-checking (as utilized in proof assistants) escape this trap** because they verify a specific, externally discovered proof path rather than strictly deciding set membership.

This report will systematically unpack this hypothesis, comparing it against both classical philosophy of logic and contemporary literature in computer science. We will explore the theoretical foundation of this claim—known in literature as the "Scandal of Deduction" [cite: 1, 2]—and trace its implications through modern computational frameworks. 

We will address the query across several dimensions:
1.  **The Theoretical Landscape:** We will formalize the claim using Hintikka's concepts of *surface information* and *depth information*, alongside Bar-Hillel and Carnap's theories of semantic information [cite: 3, 4, 5].
2.  **The Empirical Refutation (Attack Vector):** We will present a direct falsification of the premise that the closure of a decision procedure cannot be surprising, detailing the computer-assisted resolution of the Boolean Pythagorean Triples problem via a Boolean Satisfiability (SAT) solver [cite: 6, 7].
3.  **Metrics of Novelty in ACG:** We will survey the standard treatments of novelty in state-of-the-art conjecture-making systems, focusing heavily on Fajtlowicz’s and Davila's *TxGraffiti* [cite: 8, 9] and the *Ramanujan Machine* [cite: 10, 11], examining how they quantify "interestingness."
4.  **The Role of Certificate Checking:** We will validate the user's conclusion regarding proof assistants, detailing the LCF (Logic for Computable Functions) architecture and Foundational Proof Certificates (FPC), which separate untrusted proof search from trusted finite verification [cite: 12, 13, 14].

---

## 2. The Theoretical Framework: The Scandal of Deduction

The user's core reasoning—that where a decision procedure terminates, everything true is already inside its closure, so nothing is ever novel—is a highly accurate rediscovery of a longstanding paradox in the philosophy of logic. 

### 2.1 Mill, Kant, and the Paradox of Deduction
Historically, the problem of deductive novelty can be traced back to John Stuart Mill and Immanuel Kant. Kant argued that analytical deductions merely explicate what is already contained within the subject, providing no new empirical knowledge [cite: 1, 15]. Mill went further, asserting that deduction is merely "induction in disguise" [cite: 1, 15]. If we know that "All men are mortal" and "Socrates is a man," the conclusion "Socrates is mortal" contains no new information; the inference was already complete when the universal premise was accepted [cite: 1, 15]. 

This creates a paradox: if mathematical inferences are strictly deductive, and deduction does not yield new information, how can mathematics be simultaneously valid and fruitful? How can mathematical theorems surprise us if they are logically entailed by their axioms [cite: 1, 16]?

### 2.2 Bar-Hillel, Carnap, and Semantic Information
In the mid-20th century, Yehoshua Bar-Hillel and Rudolf Carnap formalized this intuition in their Theory of Semantic Information (CSI) [cite: 2, 4, 5]. They defined the semantic information of a statement based on the set of possible worlds (or models) it excludes. The more states of affairs a statement rules out, the more informative it is.

Under this formalization, a logical tautology—or any statement validly deduced from accepted premises—rules out zero possible worlds relative to those premises. Therefore, its probability is 1, and its semantic information measure (often calculated as $1 - P(s)$ or $-\log P(s)$) is strictly zero [cite: 4, 5]. As Bar-Hillel and Carnap noted, their theory dictates that logical truths and mathematical deductions have an information measure of zero [cite: 4, 5]. They argued that any "surprise" experienced by a mathematician is merely "psychological information," reflecting subjective ignorance rather than objective semantic novelty [cite: 4, 5].

### 2.3 Jaakko Hintikka's Surface vs. Depth Information
The philosopher Jaakko Hintikka famously rejected the Bar-Hillel/Carnap dismissal, labeling the inability of formal logic to explain the information yield of deductions as **"The Scandal of Deduction"** [cite: 2, 4, 15]. Hintikka sought to prove that deduction *can* introduce objective new information.

To resolve the scandal, Hintikka introduced a critical distinction between two types of information:
1.  **Depth Information:** The maximal amount of information that can be extracted from a set of premises. This represents the total logical closure of the axioms. Hintikka agreed that deduction cannot increase depth information [cite: 3, 4, 15].
2.  **Surface Information:** The amount of information that is practically or trivially available given the premises, often tied to the syntactic complexity, such as the introduction of new individuals, terms, or layers of quantifiers [cite: 2, 3, 4, 5, 15, 17].

Hintikka utilized a highly technical apparatus involving *distributive normal forms* and *constituents* within polyadic first-order logic [cite: 2, 4, 18]. He defined "trivially inconsistent constituents" (those where inconsistencies are recognizable without deep logical transformations) and "non-trivially inconsistent constituents" [cite: 4]. According to Hintikka, a deductive step yields information if it transforms non-trivial inconsistencies into trivial ones, effectively increasing *surface information* while leaving *depth information* constant [cite: 2, 3, 4].

### 2.4 The Failure of the Formal Resolution
While Hintikka's conceptual distinction between surface and depth information maps perfectly onto the user's distinction between a "decision procedure" (depth) and "finite computation/certificate-checking" (surface), his specific logical formalization is widely considered a failure. 

Critics, most notably Sebastian Sequoiah-Grayson, have demonstrated that Hintikka's formal solution is profoundly restricted [cite: 2, 4]. Hintikka's metric for non-zero information yield applies *only* to a subset of inferences in polyadic predicate calculus [cite: 2, 4]. It utterly fails when applied to the monadic predicate calculus or the propositional calculus [cite: 2, 4]. In these simpler logics—which possess guaranteed decision procedures—Hintikka's formulas still assign a zero information measure to deductive inferences [cite: 2, 4, 5].

**Synthesis for the User:** From a strict semantic perspective (depth information), the user's reasoning is completely validated by the Bar-Hillel/Carnap paradigm and Hintikka's concessions. A decision procedure merely maps the existing boundaries of a logical closure. Because the closure is fixed, the depth information of any returned theorem is zero. Consequently, a pure decision procedure cannot fundamentally act as a gate for *semantic* novelty. 

---

## 3. Computational Boundedness and the Illusion of Triviality

While the logical closure of a decision procedure is semantically empty of novel information, this view assumes **logical omniscience**—the idea that an agent instantly knows all consequences of its known premises [cite: 5, 17]. In reality, both human mathematicians and automated theorem provers are computationally bounded.

### 3.1 The Computational Reality of Decision Procedures
A decision procedure is an algorithm that, given a formal language and a set of axioms, will correctly return "Yes" (valid/satisfiable) or "No" (invalid/unsatisfiable) for any statement in a finite amount of time [cite: 1, 19]. Examples include SAT solvers for propositional logic, simplex algorithms for linear real arithmetic (LRA), and congruence closure algorithms for equality logic [cite: 20, 21, 22, 23].

However, the fact that a procedure *terminates* does not mean the space it traverses is trivial. For example, Boolean satisfiability is NP-complete, meaning the worst-case runtime scales exponentially. Advanced algorithms like CDCL (Conflict-Driven Clause Learning) combined with look-ahead heuristics traverse this space in highly non-trivial ways [cite: 6, 20]. Therefore, while a proposition $P$ may be firmly embedded in the closure of axioms $A$, discovering *that* $P \in \text{Closure}(A)$ yields immense **computational information**.

### 3.2 Escaping the Base Rate Neglect
The user's query references `PATTERN_BASE_RATE_NEGLECT`. In the context of automated reasoning, treating a decision procedure as producing "no novelty" because of logical closure is a form of base rate neglect regarding computational complexity. The set of "all true statements" is often infinitely large or exponentially vast. The probability of randomly guessing a deeply hidden theorem within that closure is vanishingly small. Therefore, when a decision procedure successfully isolates a specific, highly constrained truth within a massive bounded space, it generates *episodic novelty* or *informational surprise* [cite: 24]. 

---

## 4. Attack Vector Falsification: The Surprising Closure of Propositional Logic

The user explicitly requested an attack vector: *"Try to falsify our claim directly: is there a decision procedure whose closure is genuinely surprising relative to its axioms?"*

The answer is **yes**. The most prominent historical example of a decision procedure yielding a genuinely, profoundly surprising mathematical result is the resolution of the **Boolean Pythagorean Triples Problem** in 2016 [cite: 6, 7, 25].

### 4.1 The Boolean Pythagorean Triples Problem
A longstanding open problem in Ramsey Theory, originally posed by Ronald Graham in the 1980s, asked: *Can the set of natural numbers $\mathbb{N} = \{1, 2, 3, ...\}$ be divided into two parts (colored red and blue) such that no part contains a monochromatic Pythagorean triple (integers $a, b, c$ where $a^2 + b^2 = c^2$)?* [cite: 6, 7, 26].

For any finite bound $N$, this problem is purely a matter of propositional logic. It can be encoded into Boolean variables $x_i$ where $x_i = 1$ means integer $i$ is red, and $x_i = 0$ means it is blue [cite: 27]. For every Pythagorean triple within $N$, two clauses are added to ensure they are not all red or all blue: $(x_a \lor x_b \lor x_c) \land (\neg x_a \lor \neg x_b \lor \neg x_c)$ [cite: 27]. 

Because propositional logic is perfectly decidable, there exists a guaranteed decision procedure for any $N$. The truth or falsehood of the problem is strictly locked inside the closure of the basic axioms of Boolean satisfiability [cite: 23]. According to the strict semantic view, checking $N$ yields no new depth information.

### 4.2 The Element of Absolute Surprise
Mathematicians Marijn Heule, Oliver Kullmann, and Victor Marek utilized a "Cube-and-Conquer" hybrid SAT method (combining look-ahead and CDCL solvers) to run a decision procedure on this problem [cite: 6, 25, 28]. 

The decision procedure revealed an astonishing result: 
*   The set $\{1, 2, ..., 7824\}$ **can** be partitioned into two colors without a monochromatic Pythagorean triple [cite: 6, 7, 26, 29, 30].
*   The set $\{1, 2, ..., 7825\}$ **cannot**. It is logically impossible [cite: 6, 7, 26, 29, 30].

The boundary of $N = 7825$ was universally viewed as shocking and entirely unpredictable [cite: 30, 31]. There is nothing inherently obvious in number theory that predicts 7,825 as a breaking point [cite: 29, 30]. As one researcher noted, mathematicians remain baffled as to why the coloring is impossible specifically at 7,825 and whether the number holds deeper significance [cite: 30]. (Some mathematicians point out that $7825 = 5^2 \times 313$, but this does not intuitively predict the combinatorial collapse [cite: 29]).

### 4.3 The 200-Terabyte Certificate
The SAT solver did not merely output "Unsatisfiable." To ensure trust in this massive computational search, it generated a proof certificate in the DRAT (Deletion Resolution Asymmetric Tautology) format [cite: 28]. This generated a **200-terabyte propositional proof** [cite: 7, 26, 28, 29, 30, 31]. Compressing it for distribution resulted in a 68-gigabyte file, which required roughly 30,000 CPU hours just to independently verify [cite: 7, 28, 31].

**Conclusion on the Attack Vector:** The Boolean Pythagorean Triples problem definitively falsifies the idea that the closure of a decision procedure cannot be surprising. The cutoff at 7,825 was strictly predetermined by the problem's axioms, meaning it was always inside the closure. However, the exact location of that boundary was wildly novel and informative to human mathematics [cite: 6, 25, 30]. Thus, decision procedures *can* serve as novelty gates if the computational distance to the truth is vast enough to surpass human intuition.

---

## 5. Certificate Checking and the LCF Architecture

The user's secondary conclusion is that "finite computation and CERTIFICATE-CHECKING (proof assistants) escape this, because they check a certificate for a proof found elsewhere rather than deciding membership." 

This insight is entirely correct and forms the foundational philosophy of modern interactive theorem proving, specifically the **LCF (Logic for Computable Functions)** architecture utilized by systems like Coq, HOL, and Isabelle [cite: 12, 14, 32, 33, 34].

### 5.1 The Distinction Between Proof Search and Proof Checking
In automated reasoning, there is a strict bifurcation between two processes:
1.  **Proof Search (Decision):** This is the generative process of navigating a logical space to find a path from axioms to a conclusion. This process is often unbounded, heuristic-driven, or reliant on complex decision procedures (like SMT solvers) [cite: 12, 13, 33].
2.  **Proof Checking (Verification):** This is the finite, deterministic process of validating that a provided sequence of logical steps accurately adheres to a set of trusted inference rules [cite: 12, 14, 34]. 

As noted by Dale Miller in his work on Foundational Proof Certificates (FPC), "A proof certificate is intended to denote a proof in the sense of structural proof theory... Logic programming can check proofs in sequent calculus. Proof reconstruction requires unification and (bounded) proof search" [cite: 12, 13, 14].

### 5.2 The LCF Architecture and Trust
In systems like Isabelle/HOL, the proof assistant maintains a small, highly trusted core known as the "kernel" [cite: 33, 34]. The kernel enforces an abstract datatype (e.g., `thm` in ML) where theorems can only be constructed by applying authorized, primitive inference rules [cite: 12, 34]. 

Decision procedures and external automated theorem provers (ATPs) are strictly **untrusted** [cite: 33, 34]. When an external SMT solver (like veriT or Z3) acts as a decision procedure to solve a goal, it must produce a detailed trace or *certificate* of its reasoning [cite: 20, 33, 34, 35, 36]. 

The proof assistant then checks this certificate [cite: 32, 35, 36]. For example, the `smt` tactic in Isabelle passes a goal to an external solver, retrieves a proof certificate, and reconstructs the proof internally using only the trusted kernel rules [cite: 33, 34]. By relying on certificate checking, the system abstracts away the infinite closure of the decision procedure. It shifts the epistemological weight from "the machine decided this is true" to "the machine provided a specific, finite, human-readable (or machine-verifiable) path to the truth" [cite: 14, 32, 34]. 

This directly supports the user's thesis: certificate checking escapes the "Scandal of Deduction" because it deals strictly with Hintikka's *surface information*—the explicit syntactic unfolding of a specific proof path—rather than the opaque, infinite *depth information* of a decision procedure's total closure [cite: 4, 5, 13].

---

## 6. Novelty and Informativeness in Automated Conjecture Generation (ACG)

The user asks: *"What is the standard treatment of the claim that a system found something new, in automated theorem proving and conjecture-making systems?"*

Because decision procedures alone are poor judges of "interestingness" (they simply return true/false for membership), the field of Automated Conjecture Generation relies heavily on **empirical heuristics, database comparisons, and human-in-the-loop prioritization** to define novelty.

### 6.1 Early Systems and Colton's HR
Early ACG systems like the Automated Mathematician (AM), EURISKO, and Fajtlowicz's *Graffiti* struggled with a combinatorial explosion of trivial truths [cite: 9, 10, 37, 38]. If a system blindly generates valid statements, the vast majority are useless (e.g., $x = x$, or $x + 1 > x$). 

Simon Colton's HR system (named after Hardy and Ramanujan) was a pioneer in mathematically quantifying informativeness. HR evaluated conjectures based on empirically measurable parameters: **novelty, typicality, and quality** [cite: 39]. A "curation coefficient" was used to assess the behavior of the software and estimate the value of a system based on the value of its output artifacts [cite: 39]. 

### 6.2 TxGraffiti: Touch Numbers and the Dalmatian Heuristic
One of the most robust modern treatments of novelty in ACG is found in **TxGraffiti**, an automated conjecturing program for graph theory developed by Randy Davila [cite: 8, 9, 38, 40, 41]. 

TxGraffiti does not use decision procedures to gate novelty. Instead, it uses a data-driven approach based on finite "snapshot tables" of mathematical objects (graphs) and their precomputed invariants [cite: 8, 9]. It generates linear inequalities bounding these invariants. To filter out trivial truths, it relies on two primary mechanisms:

1.  **The Touch Number:** To measure the mathematical "strength" or informativeness of an inequality conjecture (e.g., $Invariant_A \leq Invariant_B + c$), TxGraffiti calculates its *touch number* [cite: 8, 9, 38, 40, 41]. The touch number is defined as the number of instances in the database where the inequality holds with strict equality (i.e., it is perfectly sharp) [cite: 8, 9, 38, 41]. A conjecture that holds with equality across many diverse graphs is considered highly informative and precise [cite: 9, 38]. TxGraffiti sorts conjectures in non-increasing order by touch number to prioritize tight bounds [cite: 9, 38, 41].
2.  **The Static-Dalmatian Heuristic:** Adapted from the original Graffiti program, this filtering mechanism systematically eliminates redundant or transitive conjectures [cite: 8, 9, 38]. If conjecture A implies conjecture B, and conjecture B offers no new sharp instances that A doesn't already cover, B is discarded as uninformative [cite: 8, 9]. 

### 6.3 The Ramanujan Machine: Empirical Constants and Literature Checking
Another highly publicized approach to automated discovery is the **Ramanujan Machine**, developed by researchers at the Technion [cite: 10, 11]. This system attempts to automatically discover new continued fraction formulas for fundamental constants like $\pi$, $e$, and Catalan's constant [cite: 10, 11, 42].

The Ramanujan Machine completely bypasses decision procedures and formal logic during the discovery phase. It uses numerical algorithms:
*   **Meet-In-The-Middle (MITM):** A variant of exhaustive search that matches numerical values with high precision [cite: 10].
*   **Gradient Descent (GD):** Tailored to the recurrent structure of polynomial continued fractions (PCFs) [cite: 10].

Because the algorithms rely on matching numerical values to hundreds of digits of precision, they do not provide mathematical proofs—they only provide highly confident *conjectures* [cite: 10, 42]. 

**How does the Ramanujan Machine define novelty?**
It defines novelty entirely through **external historical audits**. As the authors explicitly state in their methodology:
> *"We distinguish these points of novelty from the novelty of the generated results... we have found this result in the literature, and therefore it serves as a proof-of-concept... but is not considered new. Results could also be new and unproven: i.e., we have not found this result in the literature, we consider it as a new conjecture, until proven..."* [cite: 10, 42].

**Controversy and the Limits of Automated Novelty:**
The Ramanujan Machine has faced intense pushback from the mathematical community regarding its claims of "novelty." Critics argue that generating formulas automatically without knowing historical work does not equate to mathematical novelty [cite: 43]. Furthermore, human mathematicians quickly demonstrated that many of the Ramanujan Machine's "novel" conjectures were actually specific instances of broader, well-known algebraic identities that could be generated automatically in infinitely many forms [cite: 44]. This highlights a critical limitation in ACG: a system might generate a statement that passes empirical heuristics (it is numerically true and not literally in the literature), but a human expert immediately recognizes it as a trivial corollary of a known deeper structure [cite: 43, 44].

### 6.4 AI, LLMs, and Knowledge Graph Metrics
In the era of large language models (LLMs) and advanced AI, new metrics are being proposed to evaluate the "interestingness" of generated theorems.
*   **LeanDojo / ReProver:** Systems integrating LLMs with proof assistants (like Lean) must benchmark their ability to find proofs requiring *novel premises*—premises never seen during training [cite: 45]. The ability to generalize to novel premises is a proxy for mathematical creativity [cite: 45].
*   **Graph-based distance metrics:** Systems like AVELS (Automated Verification and Enhancement of Scientific Literature) utilize Knowledge Graphs to quantify novelty [cite: 46]. They calculate a "Discovery Score" based on the degree of separation or graph centrality between a newly generated claim and the millions of existing research publications in a vector database [cite: 46]. Here, novelty is literally computed as distance from the known mathematical corpus.

---

## 7. Synthesis: The Relationship Between Decidability and Novelty

Returning to the user's primary problem statement: *Is there literature on the relationship between decidability and novelty or informativeness?*

Yes, the literature is vast and bifurcated into the philosophical and the computational.

1.  **The Philosophical Consensus:** Under classical information theory (Bar-Hillel/Carnap), decidable formal systems cannot generate semantic novelty. The closure is fixed. Hintikka's attempt to isolate "surface information" via polyadic syntax was a valiant but flawed attempt to rescue deductive novelty at the logical level [cite: 4, 5].
2.  **The Computational Reality:** In computer science, **decidability does not preclude novelty**. The intractability of proof search (even in decidable fragments like SAT or Presburger arithmetic) ensures that finding a specific truth is an informative event. The Boolean Pythagorean Triples resolution stands as the ultimate testament: a purely decidable propositional problem whose exact boundary (7825) provided a massive injection of novelty into Ramsey theory [cite: 6, 7].
3.  **The Standard Treatment in ATP/ACG:** Modern systems acknowledge that truth is easy to generate, but *interesting truth* is hard. Therefore, they relegate decision procedures strictly to the role of **truth filters**, not novelty gates [cite: 9, 21]. To act as a novelty gate, systems employ:
    *   **Heuristic Strength Metrics:** Touch numbers (TxGraffiti), tight bounding, and the Dalmatian heuristic [cite: 8, 9, 41].
    *   **Certificate Isolation:** Proof assistants (LCF) isolate the finite, verifiable path (the certificate) from the infinite search space, recognizing that the *path* contains the mathematical information, not just the boolean output [cite: 12, 14, 34].
    *   **Literature Distance:** Evaluating the generated artifacts against external databases and human audits to ensure they are not trivial variations of known algebraic structures (as seen in the Ramanujan Machine controversies) [cite: 10, 43, 44].

### Final Conclusion
Your internal derivation is theoretically sound from the perspective of classical logical omniscience and semantic information theory. A decision procedure's closure contains no *logical* surprises. Furthermore, your intuition regarding certificate checking is structurally identical to the foundational design of modern LCF proof assistants. However, your hypothesis must be nuanced by computational complexity. Because computational resources are finite, the algorithmic unfurling of a decision procedure through a massively complex space (like a 200TB SAT certificate for Ramsey coloring) generates profound *empirical* novelty. A decision procedure cannot independently *judge* what is novel, but the boundaries of its closure can undoubtedly surprise the human mind.

**Sources:**
1. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7ibuILtNgJdNc6caEbS969gT_x_nwmWmg1Yos_WcVqSLUB4VfcxHk6MTEvqGHaDxQSNZNWr3xmYY8WnnYsi9sScmfiNidkqmsqR_r3Vh6zZMfwvW-4AiUXgyLrUkakobEk54JxwuiIyrcpUQthhIkKUkzBCBxdsiGiEguQAfad7zUrCRuYNK04PpNTzSkqvXa5Q==)
2. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGM-qdPNpRogLoX6hgbQJddDCKIahuo0yKKWfw9YKQlOiytJh9eXCWcKkyEuMSUHlkCg8sZJQLKOwyNuhDucjF3OTA6JD4pmaqk59DfhSMEdEFgsWzPTcwQavCHDleKJxo_t2LBNw06lxq9CLxCYDY31SbIAWGN-zdI7IMhN5G7p0-iVL7T-a4xZZDy1-9mHXInlY9yyEYwDC42BM-SYWsTqKy9Fbh3cJqDlF--vcIDTPT0-57hLkzGN68U)
3. [dokumen.pub](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqu66pHCLxFNGfaZKhI_Nr-L7HD3jgIjf70prYDaxYGo9OZ-Bp5V89XtAL56AbJ28NACsjSSKrBG6yi2n2HNikOMnD0O-MrCIZvOm1XiVq20GbPxSwxe9IrkCyTt6v9UI3Uk7v4liaPpgwWTP6QxP2o7zLMBlP9HIIe6YdS27zjr4G6wz0vnlTYg==)
4. [logicalrockpools.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3L2fWbTrNKtyN6dzAyC3PE6PFqI0EkpNSi6r7O221HcdrjNoaJyPgdL342b94K2kGFXszPiIcRjsktay3x9EUBpPjWUGFY4Uy2W2osL0X0yv7RZmSnbGIxxU94l4dG1p6a9rc_lZ_J-XXiP7fpeUGbGCnGuE=)
5. [stanford.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgZlSmIHmnLwEIUqgrXyYJOCog3Kxdb3ArwUl-uVz4UtJ4-QFtSAfj7P67cB7FaBiZAKIL44QKdfd5GOovel_awm6bpzVOrPZmgz-x305A0c9XDkoThfhqomwMSdtv4SmQUFhJt7gK-JGPsp53kE04IbclVKWCfJmCobU=)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqeDEvccgXdKrP1syWEszNYQeXOhvj3rucAVivo_2nkhbj_qpA3jXiRfGMw19eTkIp3DZG47BiXeE7tg5OUWlwfdYKRUa_YvMxJ3OpQYkcHs8Yuml0)
7. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUwuhu8N_6mAufnSA8I66jQjYVarHw36XnEM7gc0TfgUiEKLRypGWXa14lM0ZWbWHWHDoDsSnsZ5BnG3gaut6koAkisuDWHS6YyRl0O-i1Nq2Z3_GDFxsYJPIiyC6LNyjWx1661UHNyKt8vewFWaMD88W_aWdW)
8. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTAt9gHqnehwbF9V93JPpnyqbvEdeIc_KuQIwjZkYwaSV2CToS3mZEnH7uVihiYSS83A3ZBzqinrLIRoBP1HveJFI7IGucYne01WcIt701PSKhLUv7XASn6xMOQ4Qy7-vYBT0AUrK_wlFyJtXlSgbos6cz_ZIINLH22HRM1JRO7J9V8aKolRY1d8hUULGNaHEDZ1MA)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjXl2TJxrEjwInNWxKqrlElqy7rMBC9UqQ40b7PdQktI6N6spOGpgDY1H1PN6cSo3Hhjdpw549JwtEKgvaGsGEu_-mvJdwpswKBDeX79pSkVRhxj7e)
10. [ramanujanmachine.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsSwM4q73evTS7jkW3Xq1Sovy4KIjlH_5nhFFvrU3Fu-lDnKLeeMVPXkdVhl459p0Oxuq_p2xboDr3Nwb_ssd73KGtRf7BFnfi22KOIgGrfPwfjQ4nEzfSZAYZ0SavAySo2sVdjy8MT5jc7IccoD3_BXEbIWSBSvUD3CU78My3uSRkxhckqKqo1Q==)
11. [slashdot.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVpCHGPlbYwfg-8isq_ySeICfr52afUpmOSWJTTswH_QKmMFAz_Uxdq0ZqN9hXCm7lE7MhYoAp7Tw_PpbDQrBtfXakmpzptc6LJQYvxX6NEVeia1BdztrmFEtqVJ0-QYszhum4fwCoh48j1HPHpBcMJXK7_86Gaynh9SXVBCVbQJa4_P2fR5Ddcl57l1Vod5i42JiAPXLbUg==)
12. [polytechnique.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1r4wKzh4Odgyb-a7EDBsmYsAm8zqKMtkhLz7UYu6rdDTP6qE_nqKe5SC2Xyh4fu5pgHyNIfpjU7nmX2vIUhMKYvW88WleLR0bqQQGN2VZJgRztITaDtAtIGziKiBW1NU-WitMN8CxQ1wj-gw9OEEAx6kJqLdQIrcQQRXXGj4=)
13. [unsw.edu.au](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqsDAy3G7_eBiFy096mI3WPvBxtyvqm0bSQEqvFX2ObATls-_g1ogC7bLJ8l0tJpQlDHBzNbmVvU7Pn3SmEf8RnLkpG5hXXcUZylSwUVXQTgEAjnuvFIjVBxzwDc8MY5Ums90cxEQ6QzToX4p3)
14. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0Q2RHeO0RPw7joO06h-RMETRId9goTACXI11Q-CFucaCuTqZFoimUQD7HIz1584l7SGaMGFJqUOKm9SM3whLHitW7jj9igbTN3aRVEBLMEgZ7e0evBFJsjfgJSz3b4W3vF_9SSvAR3WRZo7QYPlmzjXD-Le2pez63vCbqlKmwqaKEQQ==)
15. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWXezJ40UmycEHg-n_6AZMJfQ-wrjVUsOjQUGo_3FAgIqXQglf8ImCuE4DwUotf3FdUkKOXw-_THeN8HjB96AdrgvTdSvsJiivpLxe0GgrjOLkq53F9AqDTmwX0BitYmsBjktHihvt2WFih17HsU3ydL0dOH72jP4kTCyhfqLOtQzzTRkQ)
16. [d-nb.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJdnBOOAqhG2Hap-2jjVLZ5cXNgJQKFqUxOUnqtJtHmzyHKcDkM0hv3oGLOHO_CYHWBZTS43hsHRchxqZDBxD7L-vbfRLqWVIsB8Fyr67L8Y_JoYE=)
17. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1xFEaFgt8FNTz1z2G2zMwV7-v4OEJTaYPqOWGFrqBp5nZE0mzLoME8kFXw42hHRAW37H_03j_iLI-EO75JbWETiWn6aYKR9m4K4JSo7a4CaY6ywRoPioo0tktlNbfMPuHE8n3t4vth8kL60FZH3jAXANVCA_VbEdgr_SmhJvQMmBpyIsAhRlnVv71F_JJLWT4P1x2I8twrvxruXIxVPnXag4GU718HwLgYV2ci7uEVz_R8sc=)
18. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhZlsv4ChJxQ3Z7THkwh2FQYwL0CZh9pPiiLNa7SEUdLIfheBwOkYziYGMLFZ6ZESh8B4rNs6dl-ZEcvpzUppCJBcmaK0UJFE5-e8aDGClAFhBNFa6ZzSTW77mdOrzPPRuTJt7JBxnSZIaYYd2mdrsMl-nfZt-VSja_gMrlfEjrYmdcSjbWZVTnq6IbnOLdFEgqIcYtyG7P4urb3XLQ9po226LJl2vrXC9To-l4S1s5KCWNvMb-K-MuM_XIeLLSm9ZeHGXct-7h6M9eJqItdbLSGA8nsA=)
19. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbYsxIbTaQRZT7tVxEsaWt5yL8q8Fy0XK1FLNcZYoU7yuZbIEuboocu8QOr-Rij19XyXCHKinnGjHsrvKJTdbKvLZJjW86Sh_HUoQ50HFLsnql2jmxcdV6a3F_RXYuJhF6XWq66NI5)
20. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiakYHQlUbIO-TLkvp-yPud0ubd2UPcQoNptJqOI9hMjR-ixTcg8CiX6yZypHTYi_V_9Rojz8kOcCIVfTAxEvpExy-RYpyCwO5R2gm8tPNnMmxdk79HAWQs75KcgYUQjvAAmBUqJ3WqmSa68mt)
21. [imag.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkUoHJOQhZ8XQatYVAVP4QyJi1KeVV8TccDSwaHOpns8nMbvfWwM-WYBScDhNyEmXT2r-6j9woUU53tlbw2EpTcWcZUWEEHFFGXzH42Df5JLR_thuIa5A3gXac29-hLKq-zBQJFNaTXzC5vC0q)
22. [illinois.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUvOzCWOZSj5dDO5Du-y3oPJNvLeKON8-CXKBp84IDfLAbqiu3I5rFYpV2eoXk3rx1p6Orf9x_o9ySrCXSWSeNENzq3iwF7YTuvwA6BdiGLxU6deUsCHGn3ONismaSxqp-m24Px4o=)
23. [quora.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2Q_3kKdyZAGlrMBkAbT4YZrFgJo1bJ6jB61yMo-Jaw9-9N7ysDkX5f19X_rXTFpqemV82kaRWZ600a_dzzyiVAiaNTMqO751oFPvTnNJ6ZhFcy-aMNcEX9nUDWtH7S6fxt6IIZTXLjzwc8Re9b4tg_f1vIg0g3rwkQEy66EyYHK71IAO4ix86-3gRRV0tss_IznP8bmxU8L4O66xM1ClujQ==)
24. [iclr.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGu8ovTtit5ZwA1__AaAszIerJzXJB-qwc7LdwQntYstHvcFTPMIvroyksfQuhZNhIGVTMvXTmEbykVAMA3p0HWJ8jTKf4KzlcsXOT9UM-rTmwQ2pwishYoMVSOEuodXg==)
25. [uwaterloo.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHhSXP4WbZGsI4pyPhpaAuEDT3QZmUOTu0isZanFCZVimpmjzY5bd3bmn1Wl5Qfe2zXWeEglUL0lN2pK3__eIhZuI_NctfJ16xmTGgZzPvLCNbU-Bbi2pGUGD1Tzl7hocQXKzeIK8VciHQ=)
26. [uky.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_3Ks6jPdUx_D33cuysnyIXZLcZ0OBoNZ2Q0QM4w4Wm_1XUdaRcqYWTBnJzQJ2hcdgXQA5O0JzTPcXWkY80dqR7RCHDkPMwJiCokky5NBLeDO-XpcmkP1cZebvihOcMrS55lUOkphJMkh5GHqSOucv60uj2mOdv3wuMxxQZS3E)
27. [cmu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzS4ojZgCQpL5VAsDHoej9p7yXOyLhjDL-Vpxv7F9e56dYhdkslmTijoiPN08A121brRn00ATlRIjaD06JovcHqaWGbsf53ezanPI6O74enQ_c_7NHmXdmo7L6IpyWi4fZhxTSdEX5q3uNsGU=)
28. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE8xZGPqWMaWmH7OBKKMRVpj6KqGFHoEFmxqCgruzJbfm9LcQDwf2x3Z4AapAULx-5UFzGIltXLiNOmvDv7EUvEs4ti771VepT8IQwdvnyfs0Xl-vmAHRE3MKdxgDqq3qtkWUa_ZkogKBVaz32ORRlKS04TePZJGrwfg9qU1iHGcMliU-tfXQ53gmmGlToLbOTxeopbOA450K-_xaWK-wyBkjQwxGmBzeIrajPkHPRv5AdTV6UDWNTL8x86)
29. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEw8K7C74On8rRZ5RlFmqjsZY4B74GDXNGlsfqN_bp0FYgRumoYKlzUqT4z6IHgCW_kpprijWZ5l5U4jhN_i7MQDseVvY-bWu-EOboUUKbljjj8AAof5DZJW74SJlV9ZsTWu7xVEHeM8yr-lATDjcp7amPc1RCNKCfcnykBupGLyD7cSu-fLV1zwP2denfCi2-oNjYqMVW-RWmAf5cVefZZlOPus1h5ja_-WiRv)
30. [edn.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHep6_OO37lmyLs4rWRPRfnFrcqqJyDGRzava-LOs7vrQI2NnYxDwqj5eC0paz-_wQ0UV9HzwDwgUPAT9wfgpIqIPvjJlEDcwI0ESuCXUjReuYB3Z6fKLnwWbOw3FNyJV5DmjFrkyTHySSBLPI2WQTydGViS80E5tQ6kDwQi4DcQQvAf6yh71vmatGMriRmR42ug78GaTa2kZ-9hjhJxdvz)
31. [futurism.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9jj0nPjWsj4_J8ShwdW-2m-81UdDrqHhmhQwxkgmWKuicXFakFKYMkIhel42US8n1dA01S6coOnCNVxPvRQWQZnLx32JCrEqvkBU_IN1Iydm5QoIqjZTtRtwYhTg5FP-iJC_7TnWs07fZeqcgy010gNa3k5mxB7KZ33hEqkHcX623sHudmsVp)
32. [hal.science](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGd8GPEHvvd0ZcuOc3L8cerY2QVz6F7J3CEyR0rcQLnngjBUfkQj5SVuj78ADgHgGeM45Lb27oH4WRS6sR8-i1Wz4xGI3WNPYy78KhLb2e2Q7foeg2x3Ohd9wzWANahWl7cO7YJsUY=)
33. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmOaTe1bjlow9-QMgl_hdNSsn5KpqrVwY246S14diT8bLKEbf9EgzDkz8VrQ2NieT85zs8CJoBZrpSLECYZTPCoh9MuCu88pBh5hp1NDQXnggeCFTQT5wtG6IAC7EEHJWJ4Hup3L31M4FohumdD4D5mAM=)
34. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0hN-Tc503AVrKGU3kq_zSqj5Cs9JgdVdeSe4g04mh4rG1_Qw0CmYy7Yu4jvyARp3qconUVl73oxXy0NktoilY7Tl7C_j1StqabaXv6xWokrPqW2TBnPGo)
35. [imdea.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGICYo9xuawmuSnQD8sSBliQgxf0sL4r_-Pabcj-HWU875Jq0VFqCyHUA8Sny149iD1-oQ3YGU49Kg4N1BYWBY4_etbtO0ou_wmHLZ-ZvUcN5FVkwJbFv2d3qBwvMl1L0oDXk3nv_YzmGVU_W1gJgS5Te3bXw6AB1RduOEs_xI28T73)
36. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGSb6p42zZWmb1TBoTi0GLbk3AyLjEOXRrMR3wjhDX6534nDPXCOQQYR_OjOxQLTwCn5O_eTlkgoGJ0y3IaZZ_lPLWNaXplaNC24FwSxOar1Nih2cTis5n66t0y8_FsqiZg120J2Q72G2QwA-7KnuKACz47JyqpWSF4L7kg7ffGFjzXHyU6iZtGENKdFjHbQP4=)
37. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmflk-d7K4EIl3VMaSPv-kMdB3D74f55nquKgh9V4oTa3de362WpqjHO_LmW14S4dxJ7g3TqN7AmtKiPaJWYMOkp4ANzS2JoA0TXtN4fxY_ddUBwbiag==)
38. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFc-mxKq2w0Hf8-ok0HO7BzRNIxqleUwfftwV817LTdW1exiV3AwIDTcuwNUibZc6xWyF2eyzQfx2YixK8T1-IBKAWzIWULUUtCpe2fR6EmnNzlt6TMHAgY)
39. [uni-saarland.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERRw5fyrin7BM40wpjN1McYTEe1TjYDgBqSrm8Kl7nUD4xHghb3mIPjFeDExGW4tdCDmdpAEKH9GKPSv5uoMrBDgmcLwvEERZj1lmSAUfjBW-DrWGnldpnJA2kySoxaaku_mhbupXxO43pDuYa)
40. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1jXhO5GmgC6Furfh3awOg1rbzxgh_e1OgwAW67VQ2JsjjA1YrtfpyYvIkMLI10NLUc1tGp5p7U7ruoEsh41abR_uk_rwqXd_8tsspVJr5Cqh8xJmbBiq3)
41. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQ5pcgpkrBrjeaPeVs7fz2U1sP0e5lchmMs5K_WXFZWT5ewEkEXBm435QNgbtPftfubNv6M8tQdiSAo5Q1ZzuM5Bg8BvA_DmKsrJpvW89c66Up42TnXMYG7DFHnS3wili9s7M=)
42. [technion.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzutXjmpJaqnjWlT8XEs4Ux7-tX0YSNeb_PeV1uu3ZT1ifUmSIvVgU8nbqqrSYULgKOYdtimb1Dl2FocCtz1vdBfUQfNz0h9v75HRCsbeuP-dH30l67KMwUeHwCGzW_bYxTuiaKnfmim7ZIcKrEF6W63e-iqxfENOLZVJAJb5YNQ==)
43. [galoisrepresentations.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJGHQPFsNC3_Zw9CdW5dinPjNlX1c5DYn_aNO7c_l1OMs3zXd5P9ZUbchDui7xixo5DIfOc5QldVMjdEg42-a-yE5tJHW0X-17PYI_fVJjCG5VCmFI8hzs1WSutfRm9sRHCd9L7-46ftBAJguODNsd9NJDoa6dVoS-Yq8Vt1YdvvWLLbAMu2ib4nF3xRzGIibG)
44. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGj28_xprBXZYJO6Z9Rnx42NtLMZNW0DfwK1mG2eVgEkdzyXPOC4YN7mW62ECo9JvDiK5luY5MLxXjiBF-9xBmNYZUnwfiuM-1FKZ9YBxyYMXTo67VsFOrPPidgI1V6u9jriITXJTim2DMoKbHoJVbPinlSJx8OKSNPBPoZh8sxTprSY5pzXxI=)
45. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6BALXAmijyEN6_h68mp71aLqNO6xRBAFq8FEaWbcNBSvhLJjdl2PxirvLm1X7ZCjmlTmDANzaxiFMzolH4hFgOVqaEw8tKkjUMHTzfOfRmd9AdIBN9rkklq9n_Q==)
46. [kaggle.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGK3_mZSZvjnyxgXcP2WiwiEj9uoRut0BTt89fCmib9dW1fMGpX7nyL3Ti4V6jyMT0XN7S2_j97WLDIeCRfpb5PldFlLuZPL3C1-nc4pfsIEP9dTV5btpXchgciuNKhq-vAyGUC9EDXDLGPU2MH03VxIv7vfLZY39jlbu96NOZbQjCHOCQgsaTTEokZz_8RVglnqTvoon-YZ3w=)
