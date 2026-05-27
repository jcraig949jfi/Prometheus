# Prompt 17: G19 Proof-Obligation — v2 design audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdkWWNXYXFPOExNeVUxTWtQc3JpVzZBTRIXZFljV2FxTzhMTXlVMU1rUHNyaVc2QU0
**Elapsed:** 212s

---

# Formalizing G19: Transitioning from Empirical Ledger Transitivity to Lean 4 Proof-Obligation Graphs

**Key Points**
*   **Proof-Obligation Extraction is Advancing:** Recent 2024–2026 developments in automated theorem proving suggest that integrating Large Language Models (LLMs) with formal proof assistants (like Lean 4 and Coq) enables robust, machine-verifiable extraction of proof obligations [cite: 1, 2].
*   **Empirical Transitivity is Inherently Limited:** The current reliance on latest-verdict ledger states as a proxy for truth is a heuristic approach; evidence heavily leans toward the necessity of formal, proof-tree dependencies routed through a strictly typed kernel to avoid logical unsoundness.
*   **Cycle Detection Requires Semantic Depth:** Arbitrary recursion caps act as temporary band-aids. Research indicates that deriving natural graph diameters and computing approximate cycle resolutions via least-fixed-point semantics may offer a more rigorous solution to legitimate versus pathological self-reference.
*   **Proof Mining Offers Quantitative Substrates:** The integration of Kohlenbach proof mining into obligation graphs could theoretically allow systems to extract explicit quantitative bounds from qualitative macroscopic claims [cite: 3, 4].
*   **The Contrarian Reality:** It is highly probable that without deep integration into a formal verification kernel like Lean 4, meta-systems like G19 are merely recreating less efficient, unsound versions of the Calculus of Inductive Constructions that natively powers modern proof assistants.

The evaluation of complex macroscopic claims—whether in mathematics, software verification, or decentralized consensus—often requires decomposing a primary assertion into a dependency graph of smaller, verifiable proof obligations. Historically, systems like the G19 loader (versions 1 and 2) have approximated this process using ledger-based transitivity, where the truth of a macro claim is empirically correlated with the latest recorded verdicts of its constituent parts. While pragmatic, this approach lacks the absolute guarantees of formal logic. Recent breakthroughs between 2024 and 2026 in neuro-symbolic AI and interactive theorem provers (ITPs), specifically Lean 4, provide a pathway to replace these empirical heuristics with rigorous, machine-checked formalisms. 

This report provides an exhaustive, academic analysis of proof-obligation extraction, cycle resolution, and formal integration strategies for the proposed G19 v3 architecture. It surveys state-of-the-art systems like COPRA, ProofNet++, and Pantograph, detailing how they bridge the gap between heuristic search and logical absolute truth. Furthermore, it explores the theoretical integration of Kohlenbach proof mining to extract quantitative convergence rates from qualitative graphs. Finally, the report steelmans a contrarian perspective: the argument that G19’s inherent value relies *entirely* on its integration with Lean, and that attempting to manage proof obligations outside a formally verified kernel fundamentally reinvents the wheel—poorly.

## 1. Proof-Obligation Extraction in Modern Proof Assistants (2024–2026)

The landscape of automated theorem proving has undergone a paradigm shift, transitioning from purely heuristic-driven models to verifier-in-the-loop neuro-symbolic systems [cite: 5, 6]. In systems like Lean 4, Coq, and Isabelle, extracting a proof obligation means taking a high-level lemma and safely unwinding it into a sequence of rigorously typed sub-goals (the obligations) that must be discharged. The years 2024–2026 have seen the emergence of several pivotal systems that automate this extraction and verification process. 

Below, we survey three primary systems, identifying their extraction operators and their foundational literature.

### 1.1. COPRA (In-Context Prover Agent)
**Primary Citations:** Thakur et al. (2024), *An In-Context Learning Agent for Formal Theorem-Proving* [cite: 7, 8].

COPRA represents a significant leap in interacting with proof environments like Lean and Coq. Instead of relying purely on one-shot generation—which often leads to hallucinated logic—COPRA treats theorem proving as a stateful, depth-first search (DFS) over tactic sequences directed by a Large Language Model (GPT-4) [cite: 1, 7]. 

*   **Extraction Operator:** *Stateful Backtracking Search with Environment Feedback.* 
*   **Mechanism:** COPRA decomposes a proof obligation by proposing a tactic and executing it in the underlying proof environment [cite: 1]. If the tactic successfully breaks the goal into sub-goals, COPRA updates its internal stack. If the tactic fails, the proof assistant's kernel rejects it, providing error feedback [cite: 8]. COPRA uses this feedback, alongside a "failure dictionary" to avoid circular or unproductive states, backtracks, and queries the LLM for a new extraction tactic [cite: 8, 9]. This ensures that any extracted sub-obligation is strictly valid according to the Lean/Coq kernel. On benchmarks like miniF2F (Lean) and CompCert (Coq), COPRA has demonstrated superior performance compared to finetuned models like ReProver [cite: 1, 8].

### 1.2. ProofNet++
**Primary Citations:** Ambati (2025), *ProofNet++: A Neuro-Symbolic System for Formal Proof Verification with Self-Correction* [cite: 2, 10].

While COPRA utilizes in-context learning, ProofNet++ represents a deeper neuro-symbolic integration. It specifically addresses the issue of LLM hallucination in logical steps by combining language models with explicit formal proof verification and self-correction mechanisms [cite: 11, 12]. 

*   **Extraction Operator:** *Symbolic Proof Tree Supervision and Verifier-Guided Reinforcement Learning (RL).*
*   **Mechanism:** ProofNet++ uses the formal kernel of proof assistants (Lean 4 and HOL Light) as a strict reward function in a reinforcement learning loop [cite: 2, 12]. The extraction of obligations is treated as generating a structured proof tree. When decomposing a macro claim, ProofNet++ generates sub-obligations and immediately routes them through a symbolic verifier [cite: 6]. If a sub-obligation transition is invalid, an iterative self-correction module prunes the invalid derivation, forcing the model to self-correct the subtree [cite: 6, 12]. This prevents the extraction of "fake" obligations that cannot theoretically be discharged, ensuring that the decomposed graph $C \leftrightarrow C_1 \land C_2 \dots \land C_n$ is mathematically sound.

### 1.3. Pantograph
**Primary Citations:** *Pantograph: A Machine-to-Machine Interaction Interface for Advanced Theorem Proving, High Level Reasoning, and Data Extraction in Lean 4* (2024) [cite: 13, 14].

Pantograph addresses the infrastructure gap in proof-obligation extraction by providing a direct machine-to-machine interface for Lean 4, bypassing the human-centric Language Server Protocol (LSP) which is often too rigid for search agents [cite: 15]. 

*   **Extraction Operator:** *Metavariable-Coupled Tree Search and Tactic Environment State Extraction.*
*   **Mechanism:** Pantograph exposes the Lean 4 frontend and environment to external agents, allowing them to construct expressions, examine the Lean environment, and extract raw tactic training data [cite: 15, 16]. When a macro claim is introduced, Pantograph allows an external search algorithm (such as Monte Carlo Tree Search) to parse the theorem and extract the exact formal dependencies (the proof tree) as they exist within Lean's `Environment` [cite: 13]. It robustly handles metavariable coupling and allows drafting incomplete proofs (goals), making it the ideal extraction operator for translating a Lean-verified theorem into a directed acyclic graph (DAG) of proof obligations.

### Table 1: Summary of Modern Proof-Obligation Systems (2024-2026)

| System | Primary Paradigm | Extraction Operator | Key Advantage for G19 Integration |
| :--- | :--- | :--- | :--- |
| **COPRA** [cite: 7] | LLM Agent + ICL | Stateful Backtracking + Feedback | High efficiency in navigating dynamic proof trees via context. |
| **ProofNet++** [cite: 2] | Neuro-Symbolic RL | Symbolic Proof Tree Supervision | Mathematically guarantees structural soundness via Lean kernel RL. |
| **Pantograph** [cite: 13] | M2M Lean 4 Interface | Metavariable-Coupled Tree Search | Native extraction of un-evaluated goals directly from Lean 4 memory. |

---

## 2. The Fallacy of Ledger-Transitivity: Proposing a Formal v3

The fundamental premise of the G19 PROOF-OBLIGATION is the decomposition of a macro claim into a conjunction over its parent obligations: $C \text{ is true} \iff \bigwedge_{i=1}^n C_i$. If any parent $C_i$ is rejected (`sub_claim_falsified`), the macro claim $C$ must be rejected. 

### 2.1. Weaknesses of the v1 and v2 Approximations
Current v1 and v2 loaders (e.g., `g19_ledger_transitivity`) compute the truth value of $C$ by querying a ledger for the "latest verdict" of $C_1, C_2, \dots, C_n$. This approach suffers from severe epistemological and systemic flaws:
1.  **Empirical vs. Formal Truth:** A ledger records *consensus* or *attestation* at a specific timestamp. The fact that a node signed off on $C_1$ does not mean $C_1$ is logically valid; it means a sociological or cryptoeconomic threshold was met. This is empirical correlation, not a formal mathematical proof.
2.  **Temporal Race Conditions:** In a distributed ledger, the "latest verdict" is subject to network latency and block reorganization. If $C_1$ is invalidated in block $t$, but $C$ is evaluated based on the ledger state at block $t-1$, $C$ may be erroneously accepted.
3.  **Lack of Semantic Checking:** The ledger has no understanding of the *content* of $C_i$. If $C_1$ is a claim that $P \implies Q$ and $C_2$ is a claim that $P$ is false, the ledger might independently accept both as "true" records, leading to an unsound macro claim based on vacuous truth or contradiction.

### 2.2. Proposing the v3 Architecture: Formal Obligation Graphs via Lean 4
To eliminate the reliance on empirical ledger correlations, v3 must integrate directly with a formal verification kernel. Lean 4 is the premier candidate due to its performant C++ kernel, its extensible meta-programming framework, and its modern machine-to-machine tooling like Pantograph [cite: 13, 15].

In the v3 architecture, the "ledger" is relegated to a mere storage medium for *certificates* of proof. The actual truth value is strictly mediated by the Lean 4 kernel.

**The Formalization Workflow for v3:**
1.  **Macro Claim Ingestion:** A macro claim $C$ is submitted to the v3 loader not as a string, but as a strictly typed Lean 4 `theorem` or `def` declaration.
2.  **Proof-Tree Extraction:** Using a tool analogous to Pantograph or LeanInfer [cite: 17], v3 extracts the exact abstract syntax tree (AST) and the corresponding proof tree. The dependencies $C_1, \dots, C_n$ are identified via Lean's `Environment` introspection (e.g., analyzing the expressions that the theorem depends upon that are not axioms).
3.  **Tactical Routing:** Each obligation $C_i$ is routed through Lean tactics. If an obligation is asserted but lacks a proof term, v3 converts it into a Lean `Goal`. 
4.  **Absolute Discharge:** The macro claim $C$ is only marked `VERIFIED` if Lean's kernel successfully type-checks the expression connecting $C$ to its discharged sub-goals. If any sub-goal $C_i$ cannot be discharged (type-checking fails or tactic times out), the loader yields the absolute, mathematically sound kill pattern: `sub_claim_falsified`.

By shifting from *ledger queries* to *type-checking*, v3 upgrades G19 from a decentralized voting mechanism to a decentralized formal verification engine.

---

## 3. Transcending Band-Aids: Cycle Detection and Natural Depth Caps

The v2 loader utilizes `g19_v2_recursive_obligations`, which performs a Breadth-First Search (BFS) to the leaves of the obligation graph with an arbitrary `MAX_RECURSION_DEPTH = 10` to prevent infinite loops. This is a heuristic band-aid. In complex mathematical proofs or software verification, proof depths frequently exceed 10. Conversely, a depth of 3 could contain a pathological cycle.

### 3.1. Deriving Depth Limits from the Natural Graph Diameter
An arbitrary depth limit assumes that all macro claims have roughly the same complexity. A formal approach requires defining the depth limit dynamically based on the topological properties of the proof-obligation graph $G = (V, E)$.

When a macro claim is compiled, the loader should analyze the Directed Acyclic Graph (DAG) of its module dependencies. The **natural diameter** $D$ of the graph is the length of the longest shortest path between any two nodes. However, since proof graphs form trees (or DAGs with shared lemmas), the natural depth limit should be derived from the **longest path** in the topological sort of the provided module's dependency graph. 

If Lean 4 is integrated, this depth limit does not need to be guessed. Lean's `import` hierarchy and local context implicitly define the maximum depth. The loader can utilize Lean's `maxRecDepth` configuration, dynamically adjusting it based on the number of nodes in the extracted abstract syntax tree.

### 3.2. Cycle Classification: Legitimate vs. Pathological
In formal logic, not all self-references are logical fallacies. 
*   **Pathological Cycles (Circular Reasoning):** Claim $A$ depends on Claim $B$, which depends on Claim $A$. In Lean, attempting to prove a theorem using itself without structurally decreasing arguments results in a failure to type-check (an invalid proof term).
*   **Legitimate Self-Reference (Induction / Co-induction):** Mathematical induction and recursive functions rely on self-reference. For example, a proof about lists may rely on the proof for the tail of the list. In Coq and Lean, this is permitted provided the recursion is *well-founded* (the argument strictly decreases according to some well-founded relation) [cite: 8].

The v2 BFS cycle detector blindly kills both. The v3 loader must classify them by leveraging Lean's termination checker. If Lean's `Termination.wf` (well-foundedness) checker validates the recursion, the cycle is classified as *Legitimate*. If it fails, it is *Pathological*.

### 3.3. Approximate Cycle Resolution via Least-Fixed-Point (LFP) Computation
In scenarios involving mutually recursive obligations or continuous state evaluations (e.g., decentralized protocol states), obligations may take the form of recursive equations. Under domain theory, we can resolve these cycles using fixed-point semantics.

Let the obligation state be represented as a continuous function $F: L \to L$ over a complete lattice $L$ of truth values (e.g., `{False, Unknown, True}`). By the Kleene Fixed-Point Theorem, the least fixed point of $F$ can be computed by iterating $F$ starting from the bottom element ($\bot = \text{Unknown}$):
\[ \text{LFP}(F) = \sup_{n \ge 0} F^n(\bot) \]

In the v3 loader, if a set of obligations form a legitimate strongly connected component (SCC), the loader applies fixed-point resolution:
1. Initialize all nodes in the cycle to `Unknown`.
2. Iteratively evaluate the Lean tactics for the SCC.
3. If the truth values stabilize (e.g., all evaluate to `True` based on base cases propagating upward), the cycle is resolved.
4. If they oscillate or fail to stabilize within a mathematically defined bound, the loader triggers the new kill pattern: `cycle_unresolvable`.

---

## 4. Concrete Specification for the G19 v3 Loader

To operationalize the theoretical advancements discussed above, we propose the following concrete specification for the `g19_v3_formal_obligations` loader.

### 4.1. Architecture and Lean 4 Integration
The v3 loader will operate as a Python/Rust orchestration layer that communicates with the Lean 4 kernel via the Pantograph interface [cite: 13]. 

```python
class G19_v3_FormalLoader:
    def __init__(self, pantograph_client):
        self.client = pantograph_client
        
    def evaluate_macro_claim(self, claim_id, lean_source):
        # 1. Load the Lean Environment
        env = self.client.load_environment(lean_source)
        
        # 2. Extract Proof-Obligation DAG
        dag = self.client.extract_dependency_tree(claim_id)
        
        # 3. Calculate Natural Depth Limit
        natural_depth = dag.calculate_longest_path()
        
        # 4. Cycle Classification & LFP Resolution
        sccs = dag.find_strongly_connected_components()
        for scc in sccs:
            if not self.resolve_fixed_point(scc, env):
                return KillPattern("cycle_unresolvable", scc)
                
        # 5. Formal Verification Routing
        for obligation in dag.topological_sort():
            result = self.client.execute_tactic(obligation.tactic, env)
            if not result.is_success():
                return KillPattern("obligation_unsatisfiable_in_lean", obligation.id)
                
        return Verified()
```

### 4.2. Graph-Natural Depth Limits Implementation
Instead of `MAX_RECURSION_DEPTH = 10`, v3 computes:
\[ \text{Depth Limit} = \mathcal{O}(|V|) \]
where $|V|$ is the number of distinct sub-theorems/lemmas extracted from the AST. If the Lean tactic engine exceeds this recursion depth, it mathematically guarantees that the proof tree is diverging, rather than hitting an arbitrary threshold.

### 4.3. Cycle Classification & Fixed-Point Resolution Protocol
1.  **SCC Extraction:** Use Tarjan's algorithm to identify cycles.
2.  **Kernel Inquiry:** Query the Lean 4 kernel: `is_well_founded(cycle_nodes)`.
3.  **LFP Iteration:** If true, allow the Lean kernel to unroll the recursion up to the termination metric. If false, or if dealing with external state-dependent claims, simulate LFP iteratively. 
4.  **Halt:** If LFP computation diverges, emit `cycle_unresolvable`.

### 4.4. New Kill Patterns
To reflect the shift from empirical ledgers to formal semantics, the standard `sub_claim_falsified` is supplemented with highly specific diagnostic kill patterns:

| Kill Pattern | Trigger Condition | Semantics |
| :--- | :--- | :--- |
| `obligation_unsatisfiable_in_lean` | A sub-claim compiles but the Lean tactic engine (or external SMT solver via Lean-SMT) fails to discharge the goal. | The claim is logically false or unprovable under the current axioms. |
| `cycle_unresolvable` | A topological cycle exists that fails Lean's well-foundedness check, or the LFP computation fails to converge. | The macro claim contains pathological circular reasoning. |
| `type_mismatch_in_graph` | An obligation claims to satisfy a parent node, but their Lean type signatures do not unify. | Structural error in the claim construction. |

---

## 5. Kohlenbach Proof Mining: The Quantitative Substrate Generator

Proof mining, a paradigm formulated within the school of Ulrich Kohlenbach, seeks to extract hidden finitary and combinatorial content from proofs that rely on highly infinitary principles [cite: 3, 18]. Utilizing proof-theoretic tools such as Gödel's Dialectica interpretation and Kohlenbach's monotone functional interpretation, one can take a qualitative statement (e.g., "Algorithm A converges to a fixed point") and extract a quantitative bound (e.g., "Algorithm A converges at rate $R(n)$") [cite: 3, 4, 19].

Between 2024 and 2026, the application of proof mining has expanded significantly into probability theory, stochastic processes, and non-linear analysis. Researchers such as Pischke, Powell, and Neri have successfully extracted effective convergence rates for stochastic proximal point algorithms, Bregman strongly nonexpansive operators, and generalized Halpern schemes [cite: 4, 20, 21, 22]. 

### 5.1. Integration with G19's Obligation Graph
Currently, the G19 graph is binary: a macro claim is either `VERIFIED` or `REJECTED`. By integrating proof mining, G19 becomes a **quantitative substrate generator**.

Consider a macro claim $C$: "The decentralized market protocol stabilizes."
*   **Qualitative Verification (Standard G19 v3):** The Lean 4 kernel verifies the obligations, ensuring the protocol mathematically guarantees stabilization.
*   **Quantitative Verification (Proof Mining G19 v3):** G19 applies proof-mining tactics to the verified proof tree. By applying monotone functional interpretations to the abstract types used in the protocol's proof, G19 extracts a computational bound. 

**The Mechanism:**
1.  **Formalization of Spaces:** The proof obligations are formalized using abstract base types representing the metric spaces (e.g., Hadamard spaces or Banach spaces) relevant to the macro claim [cite: 18, 21].
2.  **Bound Extraction Theorems:** G19 routes the verified proof graph through a proof-mining extraction algorithm. For instance, if the proof utilizes classical logic and non-effective existence statements, the Dialectica interpretation compiles it into a constructive functional program [cite: 4, 20].
3.  **Substrate Generation:** The output is no longer just a boolean verdict, but a verified software artifact—a "quantitative substrate." This substrate contains the exact mathematical bounds (e.g., maximum latency, bounded loss, or convergence rate limits) explicitly derived from the proof [cite: 21]. 

This transforms G19 from a mere *checker* into a *generator* of high-value metadata. If a decentralized finance (DeFi) smart contract is submitted as a macro claim, G19 v3 not only proves it is safe from reentrancy but formally extracts the upper bound of gas consumption or time-to-finality based on Kohlenbach's logical metatheorems [cite: 22, 23].

---

## 6. The Contrarian Steelman: G19 is a Poor Re-implementation of Lean Tactics

Despite the theoretical elegance of G19 v3, academic rigor requires us to brutally critique the very existence of the G19 framework. A strict formalist perspective (the "steelman" argument) posits that **G19, absent direct and total subsumption by Lean 4, is structurally redundant and computationally inferior to existing proof assistants.**

### 6.1. Re-inventing the Calculus of Inductive Constructions (CIC)
The core of G19's `PROOF-OBLIGATION` is the decomposition of a macro claim into a conjunction of parent obligations. It models dependencies, checks for cycles, and propagates truth values. 

This is exactly what the Calculus of Inductive Constructions (the formal type theory underlying Coq and Lean) already does, natively, at the kernel level. 
*   **Macro Claims are just Theorems:** In Lean, a macro claim is defined as a `theorem`.
*   **Obligations are just Sub-goals:** When proving a theorem, Lean generates an environment of sub-goals.
*   **Transitivity is just function application:** Proving $C$ via $C_1$ and $C_2$ is simply providing a term of type $C_1 \to C_2 \to C$, and applying it to the terms of $C_1$ and $C_2$.

By building an external Python/Rust loader that parses a JSON graph of claims, checks for BFS depth limits, and maintains a ledger of verdicts, G19 is effectively building an amateur, loosely-typed typechecker on top of a highly optimized, battle-tested typechecker (Lean).

### 6.2. The Dangers of the "Semantic Gap"
When G19 manages the obligation graph externally, it introduces a "semantic gap." If G19's cycle detector has a bug, or if its definition of logical transitivity differs even slightly from Lean's kernel, the entire system becomes **unsound**. An attacker could theoretically craft a cyclic dependency that bypasses G19's arbitrary Python depth limit but would have been instantly caught by Lean's well-foundedness checker.

### 6.3. The True Value of G19
Therefore, the steelman argument concludes that **G19 has zero intrinsic value as a logic engine**. Its only valid role—its true value proposition—is serving as the **social-to-formal bridge** (the Lean Integration layer). 

Lean 4 is a pristine mathematical universe; it cannot read a decentralized ledger, it cannot fetch IPFS hashes of smart contracts, and it cannot participate in a crypto-economic consensus mechanism. G19 should completely abandon any attempt to perform logical operations (like transitivity checking or cycle detection). Instead, G19 must act purely as an I/O multiplexer:
1.  It fetches distributed claims from the ledger.
2.  It translates them into a singular Lean 4 environment.
3.  It asks the Lean kernel: *"Does this compile?"*
4.  It broadcasts the Lean kernel's binary answer back to the ledger.

Without this total surrender to the Lean kernel, G19 is merely a worse version of what Lean tactics already do. But as a pipeline that feeds real-world, decentralized data into the unyielding rigor of the Lean 4 kernel, it represents the ultimate convergence of empirical consensus and mathematical absolute truth.

---

## 7. Conclusion

The evolution of proof-obligation extraction from heuristic ledger correlations (v1 and v2) to formal verification (v3) mirrors the broader trajectory of computer science: replacing ad-hoc methods with rigorous, machine-checked mathematics. The rapid advancements in 2024–2026, exemplified by systems like COPRA, ProofNet++, and Pantograph, prove that the tooling now exists to fully integrate formal environments like Lean 4 into automated, distributed pipelines.

By adopting natural graph depth limits, integrating least-fixed-point semantics for cycle resolution, and utilizing Kohlenbach proof mining to extract quantitative bounds, the proposed G19 v3 loader transcends its origins as a simple dependency tracker. It becomes a sophisticated, neuro-symbolic reasoning engine. Yet, as the contrarian perspective rightly highlights, the success of this architecture relies entirely on its humility: G19 must delegate all logical authority to the Lean kernel, serving not as the arbiter of truth, but as the unbreakable bridge between the messy reality of distributed networks and the pristine certainty of formal logic.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUUHdohNIVrEkGVaAirj1VTbDbQT5uzndjzaCIcuTWk13MCF9je3wDGJZ_c6P7CbnijpAF7ACdBdEcirpXKD6Uzcty-RmpJ_yziiUsBVJYh2G7x_AY8YNNJg==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwFEQGSXTdK0Sp6TeUansdOqx7qsfW2RJgKC5NXIPWw0JixcwVrPTnyiFrnNj_WYfAs9e7qcjaKLeCrqUw1mzJGOigDbFa5mh9a7JjW1ILP2KIsQfWGqU=)
3. [lc2024.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-kOdW_8g9TjUX_7VdJB6ddT6_x4wgp_kCOD21HoxZGDkH62QFBFAOhGy4FSaCXU93hOaESN-53saFXpURX5tDWbJQmuSUwqchoYQ-i9jSdHCwcnFbh-lp)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWCY7HTEdCtrI7aTxJSOhs913uhn5BqdyWYdbW87anEoZcYy_wER_3mjYGqL-7TlcG0AVyHbh62xMArGE5udOYYnFBCtx835-cJilL96GLCxKUAbri1cir5w==)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHS7u5t5N0--ybNiRjnRdsXNrQ2Od8LtR8sUhr5X2WJWNjN2KsTsw8qJOx9b3wQysv0vmepMSedp6Wza0CIbweLybNN8Mi6F9UGUlhYdVwbDJDpD-sdOvmdFjIr4nV3uVoYE5P-dpLGhy5hFp1b9FqrHrQtUn51lNngpaoIbUjYoZnr2PxF64ZT7vXUNlV5AZet9wB9agFVfTWNgU1KiXKej_sn13P_umCqAkhYWK-VnfbJsbW8JowO3-4=)
6. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEB4-mECS5U-0xTAnivbhn7Ez0_04VtG-88BxZ7H27srSe4_07sPXtOq0Z0MBgTr3DmLAosburGDWnRiegzmmB-YwPKSOFXX4VuOnO0DEqfJJHUKKwi9FjSOQn3VY6uo71nu3ehcrHjwgX27LcKyjBcvQ==)
7. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgQMSVca66oTFMeqamOrkQDBiR5hnnBIqr7ZrynWs5kh3IwfEQPa8Ly3UCD9rYyYgiHLatGxroisYB0QF1FdIxOhLLFDJiCzqK-8d70D71_TkjOm1eQRfEDNzCO07ot8k=)
8. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUGErfkC5McmoIoKtZ_qZExMmRkM06vhKGPmzUAZRJawiyfxZ-SdqFI2jrJlktXYPrp1oLArzJIBn5yHpqRi5omJIZDg_XS0U6LvVKQ1aOtsywpDx8nbsfrHGGXODu8dQ=)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhnC_vYmT3dUQqgKxbPk3GNQ9yPbic8yJT7ejC8_AAWBRBJQJL1OMzvDCGJU3syHLytuI7G-pmHKCyTnsZAbqOYSWMQXEzWE_NGSQiq7pPiFwqcYM38LH8Cw==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqUO8j2trOsjkoOWTxwhgOs_4jbSMd7WTXSOUO_feYvSLZHVHSxUPd4Nc2Cgbt7B6Y2HcMpz_Y26QpdUn9iwFgUBo6SHZ6ZicOWLC12pEX-DH-E_ujNg==)
11. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMqu9ZsfH1yMKEHfvobY56UwczO9Q0WLvPHS_t9R-B1D2VdmrnRkdI97fl3KOJnwBUwu88eqfTiagElx5RbYvAOGp1Ux4QbPqKv7X--ljfi4LxbT_O7jSnV7kSPjFtoqA=)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGpCsJktmZPVAyE8E90aIvY9Wy-8yt-A4vITzsshYObfI6j5ik6e3u5hDtfUnLXVNurDGPmVv7cR0RsdN0fbcsiGy0np6ic3wz8JFydIthqSaDQaJPvdYXLw==)
13. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENh1moS7lEdrLNZeJUH6JfVV5ldNVIPbpDm1_O24dCkOn-F8l8-AopQlcInOogGf7rmt6WL98LccGfmsAZn8BP89kY4ZpIPhA3h0WtlsbPZadDnGFY8Nk_-UGhkdSu)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFrRorK0y7KL8pz7qPwXaJgZ0lSnM-9g9sOQ62vdD-uqhJ06lFXRGbsm8uv7yf37b0vZ3IEyzMvFphThshxK5rQrKyo2_4VP6p7RJuXDOVYqTcOw9qq4w==)
15. [stanford.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPJJQwUj7BqdQimhnGiT2ueIxGh6Was9NaS_J3qu4Fr7LvLwaBQkEKiTIHToCd_r6_vCQ6uey3ROk87LF598_W10h9m9FfOh_-Zj8AjoAVISXPCTda1qfnOhtEncCriSAy55OHtjpODcY-)
16. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5cWGW8WHRMFOtmky3NcFoWDTWL2Flu9mwnB1ecqyx-UfcNLTAcIbPag5fMPv5jsPjBRxtFnXP6tWFezXelWc9aVlwcykzaT4qPJ35k6hB8KoG3Mge1yOgBVvdgYkq)
17. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpYJ4Q1Wp9EhSs8e9__wZ-u1T9cfBiH9cxr8-BTHU0c7FXCN_M4BprBBcaQaM-G3Oy0pgbtlcSZ8vfZubiHNE1dypZZRIf4TuD8RRlgOR-jcr-_tFmZJox9djFOmeR57DLPBdTYE8H)
18. [ilds.ro](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqUy84kht8gDdLT7aq3u4xkTmZaD3nq7J94hoTWaJMClCLWA0x3pQkGWdfSsZzeB6O0z8TmjlnVt4_KKl4UzdRCgoRQD8sF9kl3oCpWTe2_AWNGjQQdyYG4UgD)
19. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_lvjE593e6nfPp08cKWrMD30e-Ad2-4Lwf-IC-gDSw7BDOUjsCbvoN4aWF9uEC_1TvGKVfM8W1ZsmSs7eQoaNOnYhHhjXKXikB7c4yqxh52tOz3BuhB18)
20. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUsKXTu77lyenz9Zx0ADJm3wUYPV7yrwmGhJdndibvsfviSxL1toBycAqm_fbo-LQ2-aC5C1t_b-ay9K1k9B1TVaIXw1sUxepWc_SS2N61WS5Q7jSLWh2KQRj8CMPK80AudA==)
21. [tu-darmstadt.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGeOSdrVT4CpjxoWCIrrr9--JLpB6OC84hQSnCW7csgevLCkPWc-YQO87dD3BoBOdJFfo_rwoqZStkiAyeA8HP0styMeBmeKAPU5GlQt5PbYsiaOdw45j-1hnsT_X5KOOr4Z1e2FpTZRYB8Gm1WkL5KGW1dlMrwKSPPMVe6DcecaA==)
22. [bath.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIgVgJFJsy5cUk8FK_60uXHHOUahFDDDnciAMAg4OZi4xCUZolhFJ_X1Zipn-4-8omCNHLC5-y55_QuVPNcrn3OTjBtIOhaebCnKNlNlz4gJwg-dhVrUnnw00wkFAIkGKPo4Jfv-DqszX658fSUZIdkSN-nw==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0eaonJSr5_Dos1wn15NbPjtXio-vEqCPlLfkeU1Ihql9NgR9vEcHByU-aMhabnBVqgCp3s7XAH398zeaQZi7dwrmDa2z3yyDzZXQHXxxwcnO9plZtZcjwOg==)

