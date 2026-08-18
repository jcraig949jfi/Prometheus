# Asymmetry in Retrieval Keys for Error-Conditioned Routing: A Comprehensive Analysis of Behavioral vs. Semantic Similarity in Cold-Start Scenarios

**Key Points:**
*   The asymmetry you observed—where behavioral co-solve clustering succeeds while naive semantic label routing returns NULL—is a globally recognized phenomenon across recommender systems, algorithm selection, and large language model (LLM) tool routing.
*   Your finding that "real fields performed no better than shuffled fields" under cold-start conditions is strongly supported by recent literature identifying a "fundamental information gap" between human-authored semantic metadata and machine-actionable latent spaces. 
*   However, evidence suggests this NULL result is a **design limitation, not a fundamental law**. Pure semantic cold-start routing *without* prior co-solve data has been successfully achieved in adjacent fields.
*   Attack vectors to solve this include curriculum learning frameworks (e.g., Trace-Free+), which rewrite human-facing semantic labels into agent-optimized instructions, and Zero-Shot Meta-Learning frameworks (e.g., MetaOOD, ZAP), which use dense language embeddings to predict algorithmic performance without historical traces.
*   The integration of topological weighting (such as Information Content utilized in biological Gene Ontology) and purely content-based contrastive loss mechanisms (such as SEMCo) provides robust mathematical foundations for bypassing the behavioral cold-start problem.

This report directly addresses the problem statement regarding the established efficacy of behavioral/functional similarity versus label/semantic similarity as retrieval keys. We investigate the asymmetry observed in your internal experiment, explore the theoretical underpinnings of the cold-start failure mode, and present established methodologies that overcome this limitation without relying on prior co-solve history. 

---

## 1. Introduction and Problem Definition

The query presents a fundamental challenge in the design of autonomous routing systems, whether applied to tool selection, algorithm selection, or error-conditioned debugging. Specifically, internal experimentation revealed a stark asymmetry: **behavioral co-solve clustering** (identifying similarities based on historical traces of successful resolutions) provided highly effective routing, whereas **routing on semantic labels of failures** (using descriptive text or categorical fields) yielded a NULL result. In the semantic approach, real fields performed no better than artificially shuffled fields. Consequently, a "hard posture" favoring behavioral over semantic routing has been adopted, though with the caveat that this may be an artifact of base rate neglect or specific design constraints rather than a generalized law.

The "hard case" identified is the **cold-start scenario**—a situation where no prior solve history or behavioral data exists for a given error, tool, or user. If behavioral routing requires historical co-solve data, cold-start becomes fundamentally intractable under a strictly behavioral paradigm. 

The primary objective of this report is to determine if the observed asymmetry is documented in the broader literature of computer science, and critically, to identify **attack vectors** that successfully execute cold-start routing *without* prior co-solve data. Drawing on extensive cross-disciplinary research spanning collaborative filtering, Zero-Shot Automated Machine Learning (AutoML), LLM agent tool selection, and bioinformatics (functional vs. semantic similarity in gene ontologies), this report establishes that pure semantic routing is viable, provided the semantic representations are structurally optimized for machine inference rather than human comprehension.

---

## 2. The Behavioral vs. Semantic Asymmetry in Literature

The asymmetry between behavioral (functional) and semantic (label-based) representations is not unique to your internal system; it is a well-documented phenomenon across multiple domains of machine learning and information retrieval. 

### 2.1. Recommender Systems: Collaborative Filtering vs. Content-Based
In recommender systems, this asymmetry manifests as the dichotomy between **Collaborative Filtering (CF)** and **Content-Based Filtering (CBF)**. CF relies entirely on the behavioral matrix of user-item interactions (clicks, purchases, co-solves) without needing any metadata [cite: 1]. The system assumes that behaviorally similar users will exhibit similar preferences. Empirical evidence consistently demonstrates that when data is abundant, CF dramatically outperforms CBF [cite: 1, 2]. The CF latent space naturally captures complex, non-linear relationships and hidden motivations that semantic labels fail to articulate [cite: 3, 4]. 

However, CF suffers completely from the cold-start problem. When a new user or new item enters the system, the interaction matrix row or column is entirely zero, making predictions impossible [cite: 5]. At this exact boundary, systems are forced to fall back on semantic (content-based) routing, utilizing metadata such as genres, descriptions, or categories [cite: 5, 6]. The fact that CBF is historically viewed as a "fallback" with lower top-tier accuracy reflects the very asymmetry you discovered: behavioral data is high-signal, while raw semantic data is often noisy, low-dimensional, or misaligned with actual user preference [cite: 7, 8].

### 2.2. LLM Agents and Tool Selection
In the domain of LLM agents, a parallel asymmetry is observed between trace-based (behavioral) and description-based (semantic) tool selection. Frameworks like AutoTool leverage "tool usage inertia"—the behavioral tendency of specific tool invocations to follow predictable sequential patterns based on historical trajectories [cite: 9, 10]. By converting historical co-solve data into a directed graph of transition probabilities, these systems can bypass the LLM's semantic reasoning entirely, achieving high efficiency [cite: 10]. 

Conversely, relying solely on semantic tool descriptions (the equivalent of your "semantic labels of failures") often causes the system to collapse as the number of tools increases. Research indicates that when agents rely purely on reading semantic descriptions without behavioral traces, performance drops by 7% to 85% due to token bloat, ambiguity, and the inability of the model to distinguish between functionally overlapping tools [cite: 11]. 

### 2.3. Bioinformatics: Functional vs. Semantic Similarity
The most rigorous mathematical distinction between these concepts comes from bioinformatics, specifically the analysis of the Gene Ontology (GO). In this field, **semantic similarity** refers to the topological distance between descriptive terms in the GO hierarchy, whereas **functional similarity** refers to the actual observable behavior of gene products (e.g., co-expression in a pathway) [cite: 12, 13]. Researchers have long noted that semantic similarity often contains "asymmetric growth" and annotation bias, meaning two genes with similar semantic labels might not actually function similarly in vivo [cite: 14, 15]. 

### 2.4. Synthesis of the Asymmetry
Your conclusion that behavioral routing survives adversarial checks while naive semantic routing fails is fundamentally correct for *unoptimized* systems. Behavioral data measures *ground truth outcomes*, whereas semantic labels measure *human categorizations of symptoms*. As noted in React debugging workflows, a visible bug might possess the semantic label of a "rendering issue" (UI symptom) but behaviorally function as a "state flow" root cause [cite: 16]. When routing relies on human-applied semantic labels, it frequently points the model toward the symptom rather than the structural solution, resulting in the "NULL" performance you documented [cite: 16].

---

## 3. Diagnosing the NULL Result: Why Label-Based Routing Fails

Before exploring solutions, it is imperative to analyze why your semantic routing yielded a NULL result where real fields performed no better than shuffled ones. The literature identifies three primary failure modes for semantic routing in cold-start scenarios:

### 3.1. The Fundamental Information Gap
Recent research into cold-start collaborative filtering, specifically the SEMCo (Sampled Entmax for Cold-start) framework, highlights a "fundamental information gap between CF signals and content features" [cite: 8]. When engineers attempt to map auxiliary semantic content (like text descriptions or failure labels) directly into an existing behavioral (CF) embedding space, the mapping often fails. The variance in human-authored labels does not linearly correlate with the variance in successful algorithmic solutions [cite: 8]. If your routing algorithm attempted to map semantic failure labels onto a latent space derived from behavioral co-solves, the mathematical misalignment would render the real fields indistinguishable from random noise (shuffled fields).

### 3.2. Human-Oriented Ambiguity in Labels
In the context of API routing and LLM tool selection, semantic failure is almost always driven by human-oriented documentation. Tool interfaces and failure labels are written for human developers, who can implicitly navigate ambiguity and rely on shared domain knowledge [cite: 17, 18, 19]. An LLM or automated router lacks this implicit context. For instance, if an error label is "DatabaseTimeout," a human understands this might require checking network latency, scaling DB instances, or optimizing queries. A semantic router simply sees the token vector for "Database" and "Timeout." 

According to the authors of the *Trace-Free+* framework, this human-oriented ambiguity causes agents to fail repeatedly in cold-start settings [cite: 17]. When tools or errors are simply represented by their default semantic labels, agents "get confused between similar tools" and call the wrong operational pathways [cite: 20]. 

### 3.3. Input Layer Sparsity and Base Rate Neglect
In enterprise routing (such as CRM lead assignment or issue triaging), automated routing rules built on semantic fields frequently fail structurally because the critical qualification signals are incomplete or misaligned with the actual problem [cite: 21]. A routing framework is only as reliable as the data feeding it. Furthermore, relying entirely on semantic matching often triggers **PATTERN_BASE_RATE_NEGLECT**, where the system over-indexes on a highly specific semantic keyword match while ignoring the global base rate of common failure modes [cite: 1, 6]. 

---

## 4. Attack Vectors: Solving Cold-Start Routing WITHOUT Co-Solve Data

Your query specifically asks for methods that solve cold-start routing *without* prior co-solve data to prove that the NULL result was a design limitation rather than a physical law. The following subsections detail proven, state-of-the-art frameworks that achieve exact high-fidelity routing using *only* semantic or metadata features in pure cold-start environments.

### 4.1. Attack Vector 1: Zero-Shot AutoML and Meta-Learning (MetaOOD & ZAP)
In the field of Automated Machine Learning (AutoML), the "algorithm selection problem" is the quintessential cold-start routing challenge. Given a completely new dataset (a failure mode) with no prior evaluation history (no co-solve data), the system must route to the correct model or configuration [cite: 22, 23]. 

Historically, meta-learning relied on handcrafted statistical features, but recent breakthroughs use **Zero-Shot LLM routing via semantic meta-features**.
*   **The ZAP Framework**: This zero-shot AutoML framework selects pre-trained models and hyperparameters for new datasets *without any trial-and-error* (no behavioral trace) [cite: 24]. It achieves this by training a meta-model on a vast corpus of prior tasks, representing new tasks using only their "trivial meta-features" (semantic descriptors, lexical diversity, etc.) [cite: 24]. 
*   **MetaOOD**: Specifically addressing Out-of-Distribution (OOD) detection, MetaOOD relies on a meta-learning approach that uses **language model embeddings of both datasets and detection models** to measure task similarity [cite: 25, 26]. Rather than waiting for historical performance data on a new task, MetaOOD extracts the semantic textual description of the dataset and the mathematical description of the algorithm, embeds them using an LLM, and calculates similarity in the semantic vector space [cite: 26, 27]. It significantly outperforms behavioral baselines in unsupervised scenarios without ground truth labels [cite: 26, 28].

**Why this breaks the NULL limitation:** These methods prove that semantic labels *can* work perfectly for zero-shot routing, provided the labels are transformed into dense language embeddings rather than treated as discrete, sparse categorical fields. The embedding space captures the implicit relational context that raw labels lack [cite: 26, 29].

### 4.2. Attack Vector 2: Curriculum Learning for Semantic Re-writing (Trace-Free+)
Perhaps the most direct refutation of your NULL result comes from recent research on LLM agent tool selection, specifically a framework called **Trace-Free+** [cite: 18, 30, 31]. 

The researchers acknowledged the exact asymmetry you found: trajectory-based (behavioral/trace) optimization works beautifully, but completely fails in cold-start where no execution traces exist [cite: 17, 31]. They also noted that trying to route purely on the standard semantic descriptions of tools failed [cite: 18, 19].

Their solution, Trace-Free+, proves that semantic routing can match behavioral routing if the semantic labels are mathematically optimized. They utilized **Curriculum Learning**:
1.  **Stage 1 (Trace-Rich):** The model is trained in an environment *with* historical co-solve data (execution traces/failures). It learns the relationship between successful outcomes and the structural elements of the tool [cite: 30, 32].
2.  **Stage 2 (Transformation):** The model uses this behavioral knowledge to **rewrite the semantic descriptions** of the tools. It translates human-oriented, ambiguous labels into highly precise, agent-optimized semantic instructions (defining exact boundaries, parameter dependencies, and constraints) [cite: 17, 30].
3.  **Stage 3 (Trace-Free Deployment):** The newly generated, highly optimized semantic labels are deployed in a pure cold-start environment. The router now relies *only* on these semantic descriptions without any trace data [cite: 31, 32].

**Why this breaks the NULL limitation:** Trace-Free+ achieved performance on par with Supervised Fine-Tuning (SFT) in pure cold-start scenarios [cite: 30]. It demonstrates that your NULL result was likely caused by evaluating *raw* semantic labels. By distilling behavioral wisdom into a pre-trained interface optimizer and re-writing the semantic labels, cold-start semantic routing becomes highly reliable [cite: 30, 32]. 

### 4.3. Attack Vector 3: Pure Content-Based Contrastive Alignment (SEMCo)
In recommender systems, the standard method to solve CF cold-start is to map item metadata (semantics) into the CF (behavioral) space [cite: 8]. As noted in Section 3.1, this often fails due to the information gap. 

The **SEMCo (Sampled Entmax for Cold-start)** architecture explicitly abandons the attempt to align semantic features with CF behavioral embeddings. Instead, it frames the cold-start prediction purely in terms of **item-item similarity in the content space** [cite: 8]. 
*   It trains a content encoder to project semantic labels into a unique latent space where distance strictly correlates with user preference [cite: 8].
*   It uses a "sparse generalization of sampled softmax loss with the \(\alpha\)-entmax family of activation functions." This sharpens the estimation of relevance by mathematically zeroing out gradients for uninformative negative samples (which helps avoid the noise of irrelevant semantic overlap) [cite: 8].

**Why this breaks the NULL limitation:** By decoupling the semantic latent space from the behavioral latent space, SEMCo prevents the topological distortion that occurs when trying to force descriptive text into a matrix factorization paradigm. If your experiment evaluated semantic labels by seeing if they clustered the same way behavioral co-solves clustered, SEMCo suggests this was a structural error. Semantic features must be evaluated within their own contrastively trained latent space [cite: 8].

### 4.4. Attack Vector 4: Semantic Graph Topology and Information Content (Bioinformatics)
If we look at the query's mention of "functional code similarity," the biological field of Gene Ontology (GO) is highly instructive. GO researchers measure "functional similarity" (how genes behave) using strictly "semantic similarity" (how genes are labeled in the ontology) [cite: 13, 33, 34].

To avoid the NULL equivalent in biology (where genes with similar tags have vastly different functions), researchers do not use raw labels. Instead, they use algorithms based on **Information Content (IC)** and Graph Embeddings (e.g., **GO2Vec**) [cite: 35, 36].
*   **Information Content (IC):** Algorithms like Resnik's or Lin's method weight semantic labels by their frequency in the corpus. A rare, highly specific semantic label carries massive weight, while a broad label (e.g., "protein binding") is mathematically discounted [cite: 12, 34]. 
*   **Graph/Vector Embeddings (GO2Vec):** This approach converts the semantic ontology graph into vector representations using graph embeddings. By capturing the shortest-path and topological relationships between semantic labels, the vector distance between two labels perfectly mirrors their functional similarity, bypassing the need for behavioral (expression) data [cite: 36, 37, 38].

**Why this breaks the NULL limitation:** Naive label matching fails because it assumes all labels carry equal discriminative power. By applying an Information Content weighting mechanism or topological graph embedding to your failure labels, the semantic routing algorithm can dynamically separate high-signal root-cause labels from low-signal symptom labels [cite: 37, 39].

---

## 5. Architectural Considerations for Production Routing

Having established that semantic cold-start routing is theoretically and practically solvable, we must examine the engineering architectures required to implement it effectively, particularly addressing latency, token limits, and fallback mechanisms.

### 5.1. Semantic Vector Routing vs. LLM Inference
One of the primary reasons semantic routing fails or degrades is the reliance on monolithic prompt evaluation [cite: 11]. If a system attempts to route a failure by passing the semantic labels to an LLM alongside a massive catalog of possible tools or solutions, the system suffers from "token bloat" (consuming up to 90% of the context window), leading to a selection accuracy drop of up to 85% [cite: 11].

The optimal production solution is **Vector-Based Intent Classification** (Semantic Routing). Instead of an LLM call, the system utilizes vector embeddings and cosine similarity to classify the intent of the failure semantic label [cite: 11, 40]. 
*   **Latency:** This reduces routing latency from ~2000ms to ~100ms [cite: 11].
*   **Cold Start Tuning:** This method requires careful threshold tuning. Setting the similarity threshold too high causes the router to miss valid queries; setting it too low causes misrouting [cite: 11]. A minimum of 5-10 high-quality utterances (or semantic descriptions) per route is required to seed the vector database accurately [cite: 11].

### 5.2. The WRP Architecture
Recent research out of the LLM inference optimization space proposes the **Workload-Router-Pool (WRP)** architecture [cite: 41]. This architecture classifies routing along three dimensions:
1.  **Workload:** Warm vs. Cold, Single-turn vs. Multi-turn.
2.  **Router:** Static semantic rules, online bandit adaptation, or RL-based model selection.
3.  **Pool:** The underlying compute topology [cite: 41].

To handle cold-start safely, systems like *vLLM-SR* utilize contrastive embedding classification that evaluates sequences of turns rather than individual messages [cite: 41]. Furthermore, modern architectures advocate for "Confidence-Based Routing"—trying a fast, cheap semantic routing vector first, and escalating to a more complex, trace-aware reasoning model only when the similarity confidence is below a certain threshold [cite: 42].

### 5.3. Managing Over-Optimization and Fallbacks
A critical flagged finding from production implementations of semantic routing is the danger of "Over-Optimized Routing" [cite: 40]. If a routing threshold is tuned entirely for cost or strict semantic matching, the fallback rate spikes (e.g., to 40%), and user experience degrades [cite: 40]. Semantic routing must be implemented with graceful degradation: if the primary semantic route fails, it cascades to a secondary generalized queue rather than dropping the request entirely [cite: 21, 42]. 

---

## 6. Addressing Cognitive and System Biases: Cross-References

Your query referenced `PATTERN_BASE_RATE_NEGLECT` and `PATTERN_RANK_PARITY_LEAK`. Both are highly relevant to why semantic routing fails and how to fix it.

### 6.1. PATTERN_BASE_RATE_NEGLECT
In the context of error-conditioned routing, **Base Rate Neglect** occurs when a routing algorithm heavily weights a specific semantic label (e.g., a rare error flag) while ignoring the overall statistical probability of failure modes [cite: 6]. For example, if 80% of all UI rendering issues are caused by state-flow root problems, but the semantic label strictly says "UI_RENDER_ERR," a naive semantic router will route to a UI tool. It neglected the base rate of the underlying functional cause [cite: 16].

**Solution:** This is precisely why the *Information Content (IC)* algorithms used in Gene Ontology are so effective. IC mathematically encodes the base rate into the semantic label. Furthermore, hybrid architectures in recommender systems always maintain a "Popularity-based (POP)" baseline alongside content-based routing. This ensures that in a pure cold-start, if semantic signals are weak, the system defaults to the statistically most likely solution rather than hallucinating a niche route [cite: 5, 6].

### 6.2. PATTERN_RANK_PARITY_LEAK
This pattern typically refers to scenarios where the ranking algorithm allows irrelevant or low-quality candidates to "leak" into top positions due to superficial parity in scoring. In semantic routing, this happens when "shuffled fields" achieve parity with "real fields" because the embedding model scores superficial lexical overlap identically to deep functional relevance [cite: 8, 43]. 

**Solution:** The SEMCo framework directly addresses rank parity leak by utilizing the \(\alpha\)-entmax activation function instead of standard softmax. Softmax assigns a non-zero probability to all items, allowing irrelevant semantic matches to leak into the ranking. Entmax induces sparsity, mathematically zeroing out the probabilities of uninformative negative samples, thereby strictly enforcing rank boundaries and preventing leakage of superficial semantic matches [cite: 8].

---

## 7. Strategic Synthesis and Conclusion

To directly answer your problem statement: **Yes, the asymmetry between behavioral and semantic routing is an established fact across multiple disciplines.** Behavioral history (collaborative filtering, tool usage inertia, functional co-expression) almost universally outperforms raw semantic routing when data is abundant. 

However, your finding that semantic routing on cold-start returns a "NULL" (where real fields equal shuffled fields) is unequivocally a **design limitation, not a fundamental law.**

The literature proves that cold-start routing WITHOUT prior co-solve data is entirely solvable using semantic retrieval keys, provided the system moves beyond raw, human-authored labels. The Attack Vectors to implement are clear:

1.  **Do not use human-authored labels natively.** Implement a curriculum learning framework (like *Trace-Free+*) to pre-process and rewrite your semantic failure labels into agent-optimized, highly structured schemas [cite: 31, 32].
2.  **Do not map semantic vectors into behavioral latent spaces.** Implement a purely content-based contrastive loss architecture (like *SEMCo* with entmax activation) that builds a latent space strictly based on semantic item-item similarity [cite: 8].
3.  **Use dense language embeddings, not discrete fields.** Adopt the *MetaOOD/ZAP* approach. Embed the full descriptive context of the failure and the tool using a zero-shot LLM encoder, and route based on cosine similarity in that dense space [cite: 11, 26].
4.  **Weight semantics by Information Content.** Borrow from bioinformatics and weight your semantic failure labels based on topological scarcity in your error taxonomy to prevent base rate neglect [cite: 34, 36].

By treating behavioral-not-semantic as a hard posture, you are artificially limiting your system's capability to handle novel, zero-day failures. By restructuring how your semantic metadata is generated, embedded, and mapped, you can build a semantic router that successfully survives the cold-start vacuum.

**Sources:**
1. [stackoverflow.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUQrdInYviOJLRq2GZHsau5qenYMqI4vNWWEggEFgWjmaX7pLpaDBfYC60KD-6iPC9R0gy6shh4JktC7tWOazqA63rihThVO_KyA-EfDnMg1kBkmUoeW1wZVHoar-ZFaSRQtap8l_PGw1JyTGpSf7dT_4CMMHC2bB55v9d4xGDvhblPZ1CxQLa8z2zfkza2pvYmgx61noigg==)
2. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnPoRQTpwB70Wxc7jPDi-sZ05PK-zLgdtZPbCei8jpYyWm_tSK-Jezg6lxcHOiQeBLElROCzTPmzZannTizm5nHz5nueB2UW2fW7YyTwrkf0wmJFXy7h4UzsjEpTPckjAKJqB3gLf-GjRhsyvyx0RKgmb9IeH7)
3. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCe9Lunh_mbZYSVx0jIRw6TGOpSXXGjFQ6bNGeaWCm-gtbsGp5d8flxVpMGHRCPQE41C78aSBvDfxBD1Tl8MNopxmbMHKwH1_v15kksl0nWLo4qOJEmU10pJAfYwndfzaMjxpGisHgu1IeOTagLudKeOyGOsCceazlFqkcb_an_Jx0jMtlurl6qA_mBpYTZ1UTtvpGTOAb0tI7JPvt-m0RPfqBrv5kkgehtbZE6R56_GxCmra8CGz1UXdUfA1M975oIwSa4SmLuoTf6a9Grvm8RmvpkRTNj0INi6lXHudZ2hXjQ7c=)
4. [cikm2025.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGexYO143VEWSqRs340pWoD41_v_pif58xNkDw5y3OYYZu82ba2RAQjDcIS4W5cycb7Y_xrN07xAql3DkJ25UOuq1RvkVb75Vy1LxRZvy9H1fN0wyNRXo9iFjyNDw3m)
5. [mlwhiz.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPTZ3wdc50CeLUmRD4KTpINN88bgOCl16UZ1fmUVX236eojWxJohAbpl1UciwfCvNe7eC5PK_f7bT5EZhiau103zKUFD4Q0QVk_Ys_7hHS_2UfL3xeJ0Zx6HjpDulvsZU3elFUuEnmN6oY4ppivaywm3fiNDe9YiWCfw==)
6. [poliba.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFC5hBuYvJf7LdWTKAGnbHVcQMjbQ_qPBu3LjpCO63Pv25wea-JHtAZ5wyGjVB2fr87nKt6dBkYdjMxtyXUAQpPZr21gIK2Xk5zm2ayFUMWQ9qo7R4OajoGGscuKQYtqhlE58GIypRJt14TWZeEOREIHQPzGGyh5AHZrz8BIX3fuXVlZPxZV1WOEE2KA0giAP4J7zivJp2YZ5Po48n8zG6UHAL5pljic2qspB2i3acKq53F_ZxZi9iWF9KKtsjIe_UVs8_bF9NkeEfFrbzp0MIOiJBn7yOPdFRgfRPdACY=)
7. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHH34gCPGqYb1kALoCA05OwQZF3X2g_WrauZfDxLYlKdT51zcTxPRFIG2aAHWJkdCxDv75cumWSKLiyAQRN8Yhq8A9gUwsisP7aCK9bphaLSB1ujd7skqaMshBpN-ie)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_lIFh2TLpimk0RWa3rRTuKkHhUpSLSGkzLLfbCJCSHyqfCEzq6Dgtudb7ZiomI68tYh6pfqCTJf09tW1dJY5kfMuyCmYBZtlLpLNktue5zFpj3d_CNN-nxA==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnpffRYvLEERtqMVxrmYPUccLsjk8FpOlejVpqj7fACdFJ1Jej9a-teoJjjg_pJWGHiOS_WLq5IAZf5WMhoWK6lgzy_iH9jCu5m4kKPkEsmZxqfwZF9SK3Lg==)
10. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1F9yemSQ190jN-8Vz39039AGe0Xcu5iH4DdWy6rjMzBiOMv3MGN0pRK94svnksImkmRolZMNtvNkWcTtPuEQfnEHWyGoUL1rT6DrJlh-D2ZzLJYjAOYl0-NAM7qk6XUnr-QVqcn0jLAFZ25W8dYPsnYg=)
11. [truto.one](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQj-dMWgcvYDpLZA9dlxU2UK5XRkVapzL7jx9LRdZhJUhelgcl0ln5QT_VVSGJnAdQSyylUxEBGG4IkF6eXHzmNW5cNqW1196gcuTogh4riidkW1umgTfJn-WRRp84VM7BOeWTtL3CjHbr1E17xMI5djO_dCFL0oycRydZPF6oJUNQP3ByWldCpxgjT0Y_Z3YiN5vdTw==)
12. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuMSjajW9tVJhB_rHaR-E9ZlPAVy236hj-1VeVwf221esmNKQCxkPAV4wa0C4Htt-SqZ7oLtfZMZXeD3hQmVATTE8NJwHQjBTzZb13YSpw_TrtAOcFdbhSr9CaarBkr259eg_DSqiS)
13. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzuybCxWH0QCGEGsG6yEBhB9nL-s0a8YUwjiouqUeCvSuKeLJ4vz20jSgWW-BoMwD2Jr6MlQ5Hbay5zD9yFFeOinCWGfaI-OWxD4PY3ZEofQaQXEjRzZqFujF3mZ2AY4xAlPYUtuif)
14. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqoEQ71sjNgjruj5j7MI-L_gVH2_jDThI5VoULpp5hYrtdBDlqwgK5Ce920skcDFKhv3VozS17BLcfdGwsNv-pS2cjlgrAtmKfn1RnzC3L03b4oN9o3p-BExdVaAZAIn-CW2Al1LHD)
15. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFX8BQubx1d-LUngMlkUoLNqxORPoCaXe7g2L6t-UZ40UWJr6NGw1sZJ6YxwV3Xvq23JEvlGZj2rC8fUYlU-EM2u4oFO-tYX8F4Oxoorw2neJgA1FKkVLm9ClTumSrtpijAhhAn6uGt1UZ-RWssmoCjagNrmb-7jDc=)
16. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcWKyZqrWWrYTdySEm4K8b5DqfY9BZYy4Catm8u8GGFF6RCSBpSTFljEe9juZwmOtcC5lBKDguHy5FHDJZciZGfjsXmb_NqqBpmF_niQn30JEWtietB6XjWB_ZPT3-auBvQ-Dx0RFMGSiyBHctdekSqf4kzRdlxGMHRVSwgVK5p4p12CR2qO2DdaWEC89sIq1kVpI=)
17. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3spe3Ypi-z54vKKQDAc9ZJhwPwszO7jD8HeS1XLxUdPDRIltQ5WG2emUfwPTb0ieOb1HJE-ORd6uMfYWJ2GNoYEn8AtU6R-jJRQsLs7RbqdWDJm8Rs7Qxocb4LKo=)
18. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpFJDLd5jHdZ2CYl0sq-Arus5naWq_K5LjJuin_WRBqQYn5hr3z_4dSvcez8BjWdOx7mU0TnSX82aOLJYr9MCTF55MrPaWkBuc7TpvOatbwcykOZPuuQvPPR81UjoC)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFT4Yn5qdi08LZfMkFLDG5gyUQBFHP9CBFLcd6gB1VJPrvFUcOZavUIS9FWgl4-NyyHz_uXgc-qeP_gLCIZCOA9ppt36gjEWl89BP0fmO0W_MuDDjvXWA==)
20. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUl3-GAZqWJaG8S5Wh98xnuFCCO7k91pwRohLNPgYNtLmidSVQ0567zkdSKt9sUdUrA3CltxDEUnVF0vQzq4RCnFe53haezzOsCURogLYMKNhxd7gMZaRVMQvxClCBfzm_SKc7LZMnvmI9Tmr3KVVBA-ZHTqQ9KXlE_QKxQ9PW3ctV6xDxSxfNvAyQRwcHSkioO7WUJoA=)
21. [askelephant.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKO8ZEY81XPM_sGO3eoKZ3B8zFWSPY9KcHMokZ6HvPtGxkwuJkfPPvAlV3MTsZGbl-pamqI1RxTZTVwf0o7AraD9XdTVMO7_kbOc0K8WJyg7x3n6MeDLgqxIfouEzcWOyTN_GW6cJpn-2Z4NA4jPWuBYzjmvRF-jWnZUJnGLsTEjk=)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUG6Hj8xWZlsn-KuHA2IYq2ZNhy0sZO_w5vcSZQdYuflKKslPLSrDEGpaYx4rJ-aHOdL9ijtRjL58FcGLuQ82Ssu0kc-vFCnRbd5s3CDMZBOmrZnzH57D5icNrqhSZkejOksuIhJjYdE0fSVQeyIfJi0ert0goVDPra2D0KJuQHhv7cnFLRjVTTXClb-_BtcBc-wOrcimybhd8QiJS5s2owXwKoZicS5fvYvzRub2R5r22HAI9To9mo21vd2g-7A==)
23. [exei.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEymbiDIJ38piaBasS33N1Uhn5iG9pOl1u3z3zgst88v-xzdyWlSvwO24XV2Om152XIlmnBwezBVwpVkQ14FbreLiQBnzvSHktLUVWuuiDIEo2BXWLNft4Unf74aITbcKZowW1fGbpY-PmMeCJLY84gFOKVeB4qUSdoRYob)
24. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbAWhARC-MIayc0m97QJZG7BNN6ERSkZFMAM1pTQnLMrnePOnDS1lA5nDoGV_f0BZeDTczZweA6ZSocq7qCW9_eKDxyYedz8lMjrdq-DkwDw0ZPjMfFWrEGekJ9Q20EBn9vas=)
25. [iclr.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJ_TpUf6avQo-23_P9sAHOeHDUyR5rQRaVBofAKFc-dds3KzHNpkCDAbNUa797uxUUnlOIbjcpsRg8wdUMMY5peKN84lrfClqB0wE5zmUIBDxx1TIe16YJA8rcoF4o7WNrEwrlQOu0u4wmdovt8S3oabXdxAuZsaOSJRm1G5EsUGz9lLr_fMYN6oSZJYb-8oly1vcvm07-iyJ7fU6gTm4amy8N)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnj8F8NJIrzEQvl6jfPeVmPTRje2FEOvnVnZj4wTneg8_yMbH0rwx50OETyIQjds5J3oKnWdIKQ2L8nsmx11O1tCOQFhOMh_g2DGG1JD4j05XNJtwAPNRCww==)
27. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5Q-Sa8JK2LPe7dTVsMoGiynJjjwTZ-eJgFnNv8PjxztNTdGMCJZMEO73pBzVGmjxPSQbY1hmOi1ZBJGqSzawzPlgOtKfwMzS_uz-nuS94j0sN5_2Crgs9e4redj4tE7WjRcQ99KdZUiGELha5gEEr63XtmGd7gu0v-_h0Sn8Xq0YLCFTRXGsGucJV7gbmr5H13eLRqxRZ_VUwqIdtmF6EA3xBFC7Jhfs1MgIivMMOentgvPdvM-uFew==)
28. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEROMlOh9BKNIwYKaTRSqrHEfGSlt39y1pCxLl32o8ORtGuYB5Fv_WRWwxZ5odgEeXP8ljy0LBHbusHPPH5M2hH14KamSooLH3wyaGUaCbX_PmSI5eIS3LRW9l1KRWoqrk=)
29. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQECyTrKjDqLcqO3wGH0VbSOii1I-dJ3vVya_61A1vBvb3madgpVDxVgwD4rTmv6xQigYeJ3NRW9RvEo68ezhqj_IArk3rtqA8dcz-1cgTFRvf9cGTAJ5BI2SmH51tLcbsV27j6gvbfCA-1Whn3yZad938OuEIT49ruCadMTF0AJhcwyXeqTYBQUMCZcRYeuiLgTtTLfxBQRscxajC4=)
30. [wispaper.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExJyjCJ_bcW3yyekcXlzMaPRC8u3Kbj4d_ffmpaNy70gwEiEW_H_zjJHwkEg4cUcGJdrixSE_R-SOKZ-2CkX1HaBN1fdKQuYSfJBUbkoNk9NW-FA5ax5tNalwEXiUbtWogf4JIT5fvW2xEWf0ryzt4_QC94jTN6wm8LUcltYPiD1d6qzDZ_DcvmIT9vQw-qXZkkQeCpo7zlGjs)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFB9Sd7Ws3jHVmRadjToW0JyiHX0WpjYV9-unrQKcclLMq439S1cFoog_jXjEF1SNp1MJFzgsk10Adwc4XidSByhLDO3-vXpdLedWkKc8YRKD2rLoC3GEIkgw==)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1WRcNrM2AS_D9Q4FiZu_C-5KRBlZqVHjMVsraquoDcKS2kK6smbbtWTaUHzMhQ2cOzGhrsn3-WfzpVD1WtWPqlxd2w9zMnnDPy3CPYXw-EiJfENIU5bKwvw==)
33. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRBAYeTqGmhLIVSJVsfoZfPKVe1XKWd9HCMBLYLOZ5Ne29tFBeE8Hqe3vCX9nI0poYqyVe_5Kdn8W9UF2vDf5c-HcysGFoALycV4Mten4UOOwj3ajhqcQMVy3tmm1FbvqvL6MHUgi8)
34. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGeTvhH0Hnn_lSFL_ahbHH8eCdekBPi2Y9pAPKiK1wY0TJdgxF9tXqAzJXHLnenrZTy3KeZvmTthHCzCDecLP6X3W2AA0BAksynWXVmGN_gKpv9oaWvrkcVehzCbpWv0pMoiFIxBRLYwk7gVb07tnt1pkOu5aktA==)
35. [usm.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPgynixxjdBU42qsUiQHiJQ1M2OZfn3mvtk_GZY6x4BZnLL-AmoZtOt0x8KfzTpVRSTx9y31AIhC0gjzmevZWC3jT6DYXFmes8gnTJZt4Yq0TSy3O2Kl6zV11ib2feuOw2-GiGtvwbjDO8OXdwup90finyct6zrPXJmUk5c1hgnRpE-AU=)
36. [bio.tools](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1RjoVn5v2jd47zvALAMBNN9bsMEuKOHZk8XQkVAcwn61_EzDsLiFYFrklPzI1eUsx1Iu8l-Gv2lvBHEwMObrRR6CKYaTMed75lE3PkO8=)
37. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELoTMDV-nW9TC4lLSebTxRvclKeGNEs98WxrZ2geaYijr6X5n97EnHj5sUCqa2CAnYT3wLsARlGoKYVoy88zNoK_G4wy07OtuK3sHLiTn8wSMd1xyRcml9D2jhvJAvpjDsST4Lkjucp-GqqIBqmqebmL7WB6RKRA==)
38. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEuLkV9c9lS3alysNtkS7r5EXcPdij5FZfFVSZ8r3lJ2FWhcHi64Tt-RpMptBVfmqDKRSxxHvKqkzi5tfo4sFg90tVn5Dya6Uc7GUTgNKlxkjRV4rKDzTjGY0PIgrQMulKPc48IpMHs)
39. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGc82DQbAfZj1LjaGiWE8J9zvd7v0cWpfspx901xIZHb5CoUPyNlqzo5zMSFMcGybxlPm6mCV9SO1AFHKF-6CHh3IBmN1kTVgCFXG962Wddjr5m_YHfnl3YDXK_LNR-mKJiOr2QK5cjqohqEQ==)
40. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFXphLJT_xNF0o45BeZl4wKn59GFNcPzn4yN3E1ly6gdtwBEqY4Sej5n-paz5cx3XqaTi88PtTRc9g9yzta9h_X93gdmt_Q8oal9k_XX66KSswt6OC_1jsAxwRvBSZICH7ysjiNO-kSQ6yiQWS7hRmrA-UVnGoIW6szvs1-5VDtlsIKVMDPznXpuQjIjKXjv48sPMNVaI4lda3Ciyn3lXhkZF91Y0sXemQKhN2rBfy0w==)
41. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEIUR4goneKnIy0s2HxGycq0M_fNK26kZFFHU-dXwPV8XiyGtD-EbqHT1WjlYR1H_xaNelYbI9IsftQWaITVD0XRr2kCUJEsJKyakk_lOiil-DUBzSQs3glsw==)
42. [logrocket.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEM8Gvy2KyPK8Mz0B9IMZbIXScPwsZoPcDIRQGzCfWiDpiwMxU6pqJtPy_I4MQq2SMhyK3TNpq4d8_R7dHQ6YnWBr4L328uipITodoZuifzPPTcZ194IMH1jAVmEp553TZqZlax0c_iZbo-hgk1Ok9VTuMZwYhn)
43. [springerprofessional.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMlkFF14XgkqLoS-7RjDhufIOHJgKCd82ZgCbRtnlyua0zY_QnMHgt4oD1mFa84OSvhTriV4ZEtoPKE2LAdrfREgWiTYi9VW17qDj4tXv6vpyyihLCsjxtK_2BWd_1lLHRWFZgXuFPshTdouW3_n7kWvaMMHRFAIlnGdetEXf0vgV76rV8WvA=)
