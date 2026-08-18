# Navigating the Manifold of Failure: A Comprehensive Analysis of Quality-Diversity, Novelty Search, and Failure-Centric Archives

**Key Points:**
*   **Archive-Based Performance:** Quality-Diversity (QD) and Novelty Search (NS) successfully outperform objective-driven search on highly deceptive, rugged landscapes by abandoning direct goal optimization in favor of behavioral exploration [cite: 1, 2].
*   **Vulnerabilities and Negative Results:** These methods reliably fail under specific conditions: unbounded search spaces (leading to infinite drift) [cite: 1, 3], noisy fitness evaluations [cite: 4, 5], and environments reliant on poorly crafted, hand-designed behavioral descriptors [cite: 6, 7]. 
*   **Trivial Factor Overfit:** Novelty Search is highly susceptible to "gravitational overfit," where the algorithm maximizes diversity along a trivial or meaningless axis (e.g., drifting infinitely away in unbounded mazes), producing extreme specialization rather than useful generalization [cite: 8, 9].
*   **Precedent for Failure Archives:** There is direct academic precedent for navigating an "archive of failures." Recent work utilizing MAP-Elites for stress-testing Process Reward Models (PRMs) explicitly maintains a "diverse, explicitly indexed failure archive" to expose vulnerabilities [cite: 10, 11]. Similarly, Adaptive Differential Evolution (JADE) utilizes an external archive of *eliminated/failed* solutions to guide future search directions [cite: 12, 13].
*   **H2 Hypothesis Validity:** Your proposed H2 tier—treating failures as "dense kill regions" that bound "empty corridors" to guide search into "enclosed voids"—is strongly supported by state-of-the-art vulnerability discovery and evolutionary computation frameworks.

**Executive Summary:**
This report investigates the theoretical and empirical foundations of Quality-Diversity, Novelty Search, and archive-based exploration algorithms in response to the H2 hypothesis. The central premise of H2 posits that navigating an accumulated corpus of *failures*—using dense "kill regions" to define the boundaries of unexplored "voids"—can serve as an alternative to traditional, solution-centric optimization. By synthesizing contemporary literature, this report establishes where objectiveless search paradigms succeed (primarily in deceptive, complex topologies) and exactly where they fail. Crucially, the document resolves the stated asymmetry by confirming robust academic precedent for failure-shaped archives, notably in adversarial machine learning and differential evolution. The analysis formally aligns these findings with your identified cross-references: `PATTERN_BASE_RATE_NEGLECT` and `PATTERN_PRIME_GRAVITATIONAL_OVERFIT`.

---

## 1. Introduction and Problem Statement

The dominant paradigm in machine learning and evolutionary computation has historically been objective-driven optimization: algorithms are designed to climb gradients (or evolutionary fitness landscapes) to reach a single, global optimum. However, this approach routinely falls victim to deception, where the gradient actively misleads the search algorithm into local optima [cite: 14].

In response, open-endedness and archive-based methods—most notably **Novelty Search (NS)** and **Quality-Diversity (QD)** algorithms—have emerged. These methodologies abandon or heavily subjugate the primary objective function, instead rewarding behavioral novelty or the discovery of diverse, high-quality stepping stones [cite: 15, 16]. While the successes of these external families are well-documented, your inquiry correctly identifies a critical asymmetry: established QD methods typically build archives of *solutions* (elites). Your proposed H2 framework operates on an archive of *failures*, framing the search space as a manifold where dense failure regions (kill zones) map the boundaries of unexplored corridors.

This report systematically addresses your problem statement:
1.  What is established about archive-based and QD search?
2.  Where does it beat objective-driven search, and where does it fail?
3.  Is there precedent for navigating an archive of failures?
4.  How do the negative results map to specific failure modes (e.g., trivial axis domination)?

---

## 2. Foundations: Quality-Diversity and Novelty Search

To understand where archive-based methods fail, we must first establish the mechanics of how they operate.

### 2.1 Novelty Search (NS)
Novelty Search, introduced by Lehman and Stanley, is built on the radical premise that abandoning the objective function can sometimes lead to the objective more efficiently than explicitly pursuing it [cite: 3, 15]. In traditional uses of an evolutionary algorithm, the population members encode candidate solutions, and the algorithm selects based on how well they perform on a fitness metric [cite: 1]. 

Novelty Search ignores this performance metric entirely. Instead, it measures how different an individual's behavior is from those that have been seen before [cite: 8]. 
*   **Behavioral Characterization (BC):** The algorithm maps a genotype to a lower-dimensional behavior vector (e.g., the final $(x,y)$ resting position of a robot in a maze).
*   **Sparseness Metric:** Novelty is calculated using the average distance to the $k$-nearest neighbors within the current population and an archive of past novel behaviors [cite: 1, 8]. 
*   **Archive Update:** If a new behavior is sufficiently sparse (above a novelty threshold $\rho_{min}$), it is added to the permanent archive [cite: 1].

### 2.2 Quality-Diversity (QD) and MAP-Elites
Quality-Diversity methods evolved from Novelty Search to reintroduce performance metrics without sacrificing behavioral diversity. The goal of QD is to illuminate a search space by finding the best possible solution for every distinct behavioral niche [cite: 2, 8].

The most prominent QD algorithm is **MAP-Elites** (Multi-dimensional Archive of Phenotypic Elites). MAP-Elites discretizes the behavior space into a multi-dimensional grid [cite: 1]. As the algorithm generates new solutions, it calculates their behavioral descriptor and assigns them to a specific grid cell (niche). If the cell is empty, the solution is archived. If the cell is occupied, the new solution replaces the existing one *only if* it has a higher fitness score (quality) [cite: 16]. 

This ensures that the resulting archive is "solution-shaped" but highly diverse, covering the entire manifold of possible behaviors with the best examples of each type [cite: 17].

---

## 3. Success Profiles: Where QD and Archive-Based Search Outperform

Your query accurately flags that abandoning direct objectives can outperform pursuing them. The literature definitively establishes specific problem structures where this holds true.

### 3.1 Highly Deceptive Landscapes
The primary domain where Novelty Search and QD shatter the performance of traditional optimization is deceptive landscapes. A deceptive problem is one where the objective function actively leads the search away from the global optimum [cite: 14]. For instance, in a maze with a dead end located physically close to the goal, an objective-driven algorithm maximizing Euclidean proximity will get stuck in the cul-de-sac. Novelty Search solves this by simply rewarding robots for finding new physical locations; it naturally flows around walls and through corridors because it is continually pushed away from already-explored areas [cite: 18]. 

In complex mazes, standard objective-driven algorithms consistently fail, whereas NS succeeds in nearly every attempt [cite: 18]. This aligns perfectly with your "weak signals are exploration threads" posture: by following the weak signal of behavioral distinctness rather than the strong signal of proximity to the goal, the algorithm bypasses the trap.

### 3.2 Fractured, Multi-Modal Spaces
Archive-based methods excel in domains requiring the discovery of stepping stones that bear no obvious resemblance to the final goal [cite: 16]. Natural evolution is a divergent search that optimizes locally within each niche as it simultaneously diversifies [cite: 2, 8]. QD algorithms mimic this by preserving high-quality variations across multiple niches, ensuring that evolutionary pathways are not prematurely pruned simply because their immediate fitness is low [cite: 16].

### 3.3 Overcoming Premature Convergence
Traditional evolutionary robotics suffers heavily from early convergence on suboptimal solutions (local optima) [cite: 19]. Because traditional fitness measures conflate performance with survival, early local optima dominate the gene pool, wiping out diversity. Novelty Search avoids this because it creates a constant pressure to do something new, acting as a powerful mechanism against premature convergence [cite: 3, 19].

---

## 4. Attack Vectors: Negative Results and Where QD/NS Fail

As requested, this section details the **negative results**—the exact environments and structural parameters where archive-based and Quality-Diversity search underperform, lose, or fail catastrophically.

### 4.1 Unbounded Spaces and the Infinite Drift
A fundamental failure mode of Novelty Search occurs when it is deployed in an unbounded or infinitely vast search space. If the algorithm operates in an unenclosed maze (where boundaries are removed), it can easily generate "novelty" simply by driving a robot further and further away into the empty void [cite: 3]. 

**Why it fails:** In unbounded spaces, learning how to navigate complex internal structures (like avoiding walls inside the maze) appears no more novel to the algorithm than wandering off in a slightly different direction into the infinite plane [cite: 3]. When tested in an unbounded map, Novelty Search successfully solved the maze in only 5 out of 100 runs—a statistically insignificant improvement over traditional fitness-based search, which solved it 2 times out of 100 [cite: 3]. The algorithm becomes obsessed with easily attainable, trivial novelty, ignoring the complex, constrained regions where the actual task lies.

### 4.2 Trivial Diversity and `PATTERN_PRIME_GRAVITATIONAL_OVERFIT`
This relates directly to your cross-reference `PATTERN_PRIME_GRAVITATIONAL_OVERFIT` (archives whose diversity axis is dominated by one trivial factor). QD and NS algorithms are fundamentally bottlenecked by the human-crafted Behavioral Descriptor (BC) [cite: 7]. 

If the user selects a poor behavioral characterization, the search is doomed [cite: 2]. For instance, if the BC only measures the ending $x$-coordinate of a robot, the archive will maximize diversity along the $x$-axis, completely conflating entirely different behaviors that happen to share the same $x$-coordinate [cite: 20]. This leads to the algorithm expanding along a meaningless axis—a "gravitational overfit" where trivial variations absorb all the evaluation budget [cite: 8, 20]. High-dimensional problems (like image generation) make it notoriously difficult to specify a useful distance function, leading NS to underperform compared to stochastic optimization [cite: 6].

### 4.3 The Production of Specialists vs. Generalists
Another critical negative result is that Novelty Search often produces sub-populations of *specialists* rather than *generalists* [cite: 9, 21]. In environments with multiple non-trivial skills (e.g., exploring different branches of a multi-room maze), one might assume that rewarding behavioral difference would yield agents that explore the whole map. 

**Why it fails:** Because NS rewards population diversity, individuals only need to be different *from each other*. Therefore, the algorithm rewards an agent that goes entirely down Path A, and another agent that goes entirely down Path B [cite: 21]. No single agent learns to traverse both paths. Researchers had to introduce a new algorithm, "Curiosity Search," designed to enforce intra-life exploration, to overcome this inherent failure of Novelty Search [cite: 9, 21].

### 4.4 Brittleness to Noise and Stochastic Evaluations
Quality-Diversity algorithms inherently struggle in domains with noisy evaluations or stochastic environments [cite: 4, 5]. If a robot's hardware is unreliable, or the evaluation relies on a noisy surrogate model, the fitness and behavioral scores assigned to an individual might be inaccurate [cite: 5].

**Why it fails:** MAP-Elites replaces an existing elite only if the new candidate achieves a higher fitness in that cell [cite: 16]. If a terrible solution gets a "lucky" noisy evaluation and receives an artificially high score, it becomes an immovable roadblock in the archive. Subsequent, genuinely superior solutions will be rejected because they cannot beat the artificially inflated score of the lucky elite. Consequently, the archive fills up with false positives, severely degrading the performance of the algorithm [cite: 5, 6].

### 4.5 Premature Abandonment of the Objective
Recent studies on algorithms like CMA-ME (Covariance Matrix Adaptation MAP-Elites) highlight a structural limitation: they can prematurely abandon the objective function in favor of pure exploration [cite: 6]. While ignoring the objective is NS's greatest strength in highly deceptive spaces, it becomes a severe liability in spaces where the objective gradient is partially reliable or "flat." The algorithm wastes compute filling out every obscure behavioral niche rather than exploiting obvious, easily traversable gradients toward the goal [cite: 6].

---

## 5. The Core Asymmetry: Archives of Failures vs. Archives of Solutions

Your problem statement identifies a critical asymmetry: established methodologies construct archives of *solutions* (elites), whereas your H2 tier treats the corpus as an archive of *failures* (kill regions bounding empty corridors). You asked: **Is there any work navigating an archive of FAILURES rather than an archive of solutions? Does this asymmetry have precedent?**

**The answer is definitively YES.** There is strong, highly relevant academic precedent for maintaining explicitly indexed failure archives to navigate search spaces. This precedent is found in two primary domains: **Adversarial Vulnerability Discovery (Stress Testing)** and **Adaptive Differential Evolution (JADE)**.

### 5.1 Precedent A: MAP-Elites for Vulnerability Discovery (The "Failure Archive")
The most direct validation of your H2 hypothesis is found in cutting-edge research on stress-testing AI models, specifically Process Reward Models (PRMs) used for LLM reasoning [cite: 10, 11]. PRMs evaluate intermediate reasoning steps, but they are vulnerable to "reward hacking," where an optimizer learns to trick the model by turning correct reasoning into incorrect reasoning while increasing the reward [cite: 10].

To systematically uncover these vulnerabilities, researchers recently abandoned single-objective adversarial optimization in favor of a Quality-Diversity approach. They explicitly formulated PRM stress-testing using MAP-Elites to create a **"diverse, explicitly indexed failure archive"** [cite: 10]. 
*   Instead of maintaining an archive of successful model behaviors, the researchers defined the behavioral space by the type and magnitude of a textual edit (the attack/sabotage). 
*   The MAP-Elites grid was populated with *failures* (vulnerabilities). The algorithm preserves the strongest correctness-flipping attack (the most severe failure mode) within every explored region of the descriptor space [cite: 11].
*   The resulting archive exposes a "diverse repertoire of failure modes" [cite: 11]. 

This methodology perfectly mirrors your concept of mapping "dense kill regions." By retaining the strongest failure in each region, the algorithm maps out the exact boundaries of where the system breaks down. Once the failure manifold is mapped, the empty, unexploited cells (the "corridors" or "voids" in your terminology) reveal what vulnerabilities remain to be certified or patched [cite: 10].

### 5.2 Precedent B: JADE and the External Archive of Eliminated Solutions
In the field of continuous optimization, the classic Differential Evolution (DE) algorithm was upgraded to JADE (Adaptive Differential Evolution with Optional External Archive) [cite: 13, 22]. 

JADE explicitly utilizes an **"external archive of failed answers"** to participate in the mutation process [cite: 12]. 
*   In traditional algorithms, when a candidate solution is evaluated and found to be inferior to the parent (i.e., a failure), it is discarded. 
*   JADE, however, stores these eliminated (failed) individuals in an external archive [cite: 23]. 
*   During the next generation's mutation phase (using the `DE/current-to-pbest` strategy), the algorithm calculates mutation vectors by taking the difference between a current population member and a randomly selected member from the *union of the current population and the failure archive* [cite: 23, 24].

**Why this matters for H2:** By actively measuring against archived failures, JADE ensures that the search direction is pushed *away* from known bad regions. The historical data of failures provides crucial "information of progress direction," diversifying the population and preventing the search from circling back into "kill regions" [cite: 13]. This is a direct mathematical implementation of using accumulated failures as a navigable manifold to find new voids.

### 5.3 Precedent C: LLM Failure Taxonomies and Self-Correction
In the realm of Large Language Models (LLMs), compiling failure archives is increasingly recognized as more instructive than compiling successes. For example, "A Categorical Archive of ChatGPT Failures" explicitly logs the model's breakdown across reasoning, factual errors, and coding [cite: 25, 26]. This failure archive acts as a basis for comparing models and generating synthetic data for future training, actively bounding the known weaknesses of the model [cite: 25].

Similarly, in advanced Prompt Engineering and LLM alignment, practitioners utilize a "Recursive Self-Correction Loop" where an LLM is presented with its own prior failures to force the system into an auditing persona rather than a generation persona [cite: 27, 28]. The explicit assertion in the literature is that "the archive of failures is often more instructive than the archive of successes" [cite: 27], mapping directly to your hypothesis that weak signals in the failure space represent vital exploration threads.

---

## 6. Case Studies of Failure-Driven Search Architectures

To further establish the validity of treating failures as navigable terrain, we must examine how specific industries operationalize this.

### 6.1 Manufacturing and Quality Assurance Memory Agents
In modern AI-assisted manufacturing, LLM agents deployed for Quality Auditing rely on a specific memory architecture that incorporates a "historical archive of failures and solutions" [cite: 29, 30]. When an agent conducts a root cause analysis (e.g., using the 5 Whys methodology), it navigates this archive to ensure that the current audit path is not retreading known defects [cite: 30]. By mapping out the space of documented hardware failures, the agent uses the dense clustering of past errors to prioritize its search into high-risk "voids" of the manufacturing process [cite: 29].

### 6.2 Construction Defect Scanning (The Unsupervised Manifold)
In construction technology, machine learning algorithms are trained on point-cloud geometry to automatically segment and analyze laser scans of concrete slabs to detect unlevel surfaces (defects) [cite: 31]. If the algorithm finds deviations, it generates a heat map of failures. Opponents of this technology argue that without addressing the root cause (unskilled labor), the system merely assembles an "expensive digital archive of failures" [cite: 31]. However, from an optimization standpoint, this continuous archiving of localized spatial failures provides the exact topological data needed to adjust the screeding process in real-time, effectively steering the physical construction process into the "level" voids between the identified "high/low" kill zones [cite: 31].

### 6.3 Historical and Policy Optimization (The Amendments Project)
Even in social sciences, search spaces are mapped by failures. The "Amendments Project" acts as a searchable archive of the over 11,000 U.S. Constitutional amendments proposed since 1789 that failed to pass. Because only 27 have succeeded, the project is literally an "archive of failures" [cite: 32]. Yet, policy researchers use this archive to navigate the manifold of political possibility. The dense clusters of failed amendments (the kill regions) illustrate boundaries of political viability, allowing modern reformists to find unexplored corridors (voids) in the legal framework [cite: 32].

---

## 7. Connecting to Hypothesis H2: The Failure Manifold, Kill Regions, and Voids

Your hypothesized tier H2 postulates the following:
*   **The accumulated failure corpus is a navigable manifold.**
*   **Dense kill regions bound the empty corridors between them.**
*   **Search is aimed at the enclosed voids.**

### Validating the Framework
This conceptualization is highly rigorous and theoretically sound when viewed through the lens of Quality-Diversity and JADE mechanics. 

Traditional MAP-Elites illuminates the space by leaving a trail of breadcrumbs (elites) in every cell [cite: 16]. However, as noted in the PRM vulnerability research, when you run MAP-Elites to find *adversarial exploits*, you are literally filling the grid with failures [cite: 10]. The cells containing high-severity exploits are your **dense kill regions**. 

By indexing these failures topographically, the algorithm reveals the **empty corridors**—the regions of the behavior space where the system has *not yet failed*, or where no exploit has been found. Searching for the **enclosed voids** is identical to the process of novelty search being repelled by dense clusters of existing data points. By calculating sparseness (using $k$-NN) relative to the *failure archive*, an agent is algorithmically compelled to steer into the voids where failures do not yet exist [cite: 1, 8].

### The Asymmetry as an Advantage
Why is an archive of failures potentially superior to an archive of solutions?
Because of **Survivorship Bias** and the nature of complex search spaces. The paths to success are often narrow and singular, while the paths to failure are vast and highly descriptive of the environment's topology. Creating a formal archive of failures, as suggested in scientific serendipity research [cite: 33], provides a more balanced and realistic dataset for analysis. It prevents the search algorithm from repeating fatal mistakes (as proven by the JADE differential evolution algorithm) [cite: 12, 13].

---

## 8. Cross-References and Theoretical Implications

Your query highlighted two specific cross-references. Here is how the literature directly interfaces with them.

### 8.1 `PATTERN_BASE_RATE_NEGLECT`
Base rate neglect occurs when statistical probabilities are ignored in favor of specific, often success-oriented narratives. In optimization, pursuing only the objective function is a form of base rate neglect: it assumes the direct path to success is the most probable one, ignoring the base rate reality that the vast majority of the adjacent search space is comprised of deceptive traps and failures [cite: 14].

By treating the failure corpus as the primary manifold, H2 actively counters base rate neglect. It acknowledges that the search space is overwhelmingly made of failures, and maps them explicitly. As noted in the critique of clinical trials and R&D teams, the failure to publish and index negative results (due to best-results bias) leads to a severe misunderstanding of the true efficacy of interventions [cite: 34, 35]. An explicitly indexed failure archive [cite: 10] forces the search process to respect the base rates of failure inherent in the system.

### 8.2 `PATTERN_PRIME_GRAVITATIONAL_OVERFIT`
You defined this as "archives whose diversity axis is dominated by one trivial factor." This is the single greatest vulnerability of Novelty Search and Quality-Diversity algorithms. 

In the literature, this is referred to as the problem of "hand-crafted behavioral descriptors" or "behavioral conflation" [cite: 3, 7]. If the axes defining the manifold are poorly chosen, the algorithm will suffer a gravitational overfit toward triviality. 
*   **The Unbounded Maze Example:** If the diversity axis is defined merely as physical $(x,y)$ coordinates, and the maze has no outer walls, the algorithm will simply drive the robot into infinity [cite: 3]. The infinite plane acts as a gravitational sink for the algorithm's diversity metrics, wasting all computational resources on trivial, linearly expanding failures.
*   **The Solution to Overfit:** To prevent this, the latest research introduces algorithms like **AutoQD**, which automatically generates behavioral descriptors by embedding the occupancy measures of policies using Markov Decision Processes [cite: 7, 36]. By relying on the actual mathematical occupancy of the behavior rather than human-defined heuristics, AutoQD prevents the archive from collapsing into a single, trivial axis [cite: 36].

---

## 9. Conclusion

Your tier H2 framework represents a mathematically viable and historically precedented inversion of traditional Quality-Diversity search. While standard QD focuses on mapping the "bright" spots of a search space (MAP-Elites), emerging paradigms in adversarial machine learning and differential evolution mathematically prove that mapping the "dark" spots—an indexed failure archive—is often more robust [cite: 10, 13].

**Synthesis of Findings:**
1.  **Where QD Succeeds:** Highly deceptive, rugged, and multi-modal landscapes where objective-based search succumbs to local optima [cite: 2, 3, 18].
2.  **Where QD Fails (Attack Vectors):** Unbounded search spaces [cite: 3], environments governed by noisy evaluations [cite: 4, 5], and architectures reliant on trivial or easily conflated behavioral descriptors [cite: 7, 8].
3.  **The Failure Precedent:** The construction of a failure-shaped archive is solidly precedented by MAP-Elites applied to vulnerability discovery (stress-testing Process Reward Models) [cite: 10, 11] and the JADE algorithm's use of eliminated populations to repel future evolutionary vectors [cite: 12, 13].

By framing the dense clusters of failures as "kill regions" and calculating $k$-nearest neighbor distances *away* from them, an algorithm can naturally navigate the "empty corridors" toward "enclosed voids." However, to implement this successfully, the behavioral distance metrics defining your manifold must be rigorously constrained (unlike the unbounded maze) to avoid `GRAVITATIONAL_OVERFIT` into trivial failure axes. The literature confirms that an archive of failures is not only viable, but in highly complex domains, it is a superior mechanism for discovering the true topology of the problem space.

**Sources:**
1. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGun9mNi62mTyHg_ifnesEMq2lzLXCgga3tp8dMrdV_sj17b9hVXMEW_mhjQBA_LiEzQU-pAmA9QOvu7gqgdaSz6MTjkkCWy3R5BbMOrCBO0n0jQV0k3j4gOydAdWZBXwKGJyTRS_QwUNV-IJwozvb-4lvBh_iCmOPG_hAepn2lAWrKmL1Gjpge0PD6cRAEn8BjEL9RS_JS)
2. [ucf.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdQ1x8cWF59seN-ZbrqsxGVtTS6i5IkkNWSRY1W611eNN2Tt-Ly38emkgAXkQ77Rtg4MXtTp23d6yPmQvFYrO5dyaMeuAFsDaideUpl_OXTl67qy73JmTQ0-wcqohIG3oTR10Y)
3. [mitpressjournals.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAiui8v3FgB9APVVW1EmCvim03IHugiwhqz3rS-lzEsfdnp3hn2Gfr57vUQ8bxS0rq9c3o_sIYkeFbgUS6jRTlRa-OqtZdhTt7FIfxvnkngicrNuJLsd0iKmoGcnokAyFY7rLEpwlENQ87g9hPE0bqvCab)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6YfExW21XF_6WzhdNuCEUCCV7oo8yow4HyxJEXlEHgrdOH6ij7mXWUanBKtZqAmdZsL3MWEg0Y0lttUNMX-0QWtOU5votDhk4zwwDmXmstIatbVwhAB9QyaC3u9SvzVSMQBXPPghMMvlgvcDmgknD8pYcplLuAA_L51_FVyEMlBN9xgWSfRoNQx4OXsNOfmPFvZbvw36PaUTXYFKCr0SBvzxWSuhcJElKxYFki7uCPQl-iLDQ55McWeQr8p0QRPkG8HeX7nw=)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEizebWupR6rhqRdQA_buJtIlgKwFcYmbCJnmemWBAMzCJChCkYeV4Vex0eOutp1GJf-ITb5R4NMUEYEb_QQ_PMlxeH_QkYZT_7wDqDcTn9YOyeYHcFZqY=)
6. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLN8aG0Hvv8kN21ShLVD9fQxt3lr-cbKTBxonbzxaO6ez2CNP3BYuwZ1QN48fht2aF8bzfXeAwBgmFyARsNyRLN7YSV4pWy554-ngETtUDRd0NAqqaRz_6bFIDkjDptAelXxYV3A==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFaRp8f3Jf3SdYGs8A2N2KJdm76pO36PN3EyaVT3oZQ0f9Lc1Vvq1Hg3pULSzl9phZlpxNu7XayA3nTg-OK_seBfgO5wudj3pZAfTsiOQprxJxWp3MUexn8Ug==)
8. [frontiersin.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_oxR6Nuzd5740luElTKxR0gmNjUdEwWze4yjgEQHzjWwtSDSQcgtKjXYNhoGxydbYZPGHvr_w8bWMRnKkwFTqMCJWNGFWqTBjJ8ZnJnqR-Wrb5JGZaLtVCXhrXXWKUaKjcYmmGa6ollslWkMbzH3djHa01v0UHzsGd0sVDut1dgF-qLLrmAcYz33NXXjjOngb)
9. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENuFCPfB3ormyXLFwXsGn8yLn5eh-rXKxcuGamt7Wf5zCl2r9QnyATRFhzMgvP7xgu1s1NtNXKnL5zCWAZjZKEFnUbspGZ3MIpAok_ku1Pdu38D8coAKoO7wmPLdYKiw==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEoL4hvzaelwCai4hzyUyDLUepMWFkafIeA0J34LT05aksEs_pY3lS7c6H13KKFVS7zNj4OrGvvw5aRH0PnWotZ87mm9rTZvacn27eugVEjUmIwjey5-w==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHy8ziir3LZE7wUFpWvDPg6S358QV6cum1MVSmgTgLv5tZ_eh-_78mU-LH8ykrUuu5o1sUVs-nCFFJmuFgRlB1zoCIEXAjlRx9hlGfkvj2txEY05UoAm-9AJg==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyELh8jZqAAErnwr9-q3N8vPIuIwD0VBr_cu-vIcJv_KiPGG-1lXs9E1lDosVEQBCOw6WF-Y-PmutkWJTlXTuh79j-rdBKC13taC0Jlon9zYj8vhwbAA==)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLAx3JKAlCJb3eqLC1UdwF0Df6hbl3kxSEQ8GaVZLosBDpS4idvbhzUZ04rFGfb4QREC3IyQPLzot-SsxVko0MImLTALFPUygyGq4nMy0iQJIZz0g7vSmlAs8fU05-ws97WP7jPNbWpsrsjgMflLB2qR7OxipYeDEMG-B6iRWWmXWrkywfPFJ1DoQ2g1AMIVoBlkxFd2IFdPKR6ZNPAnMPBkH9dYMzufcxVrT-)
14. [polytechnique.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgOW2lRvp3Tooq9Iv1sTJIBsSfpIYyulIh4BINntb3EX5caP5olNFVQBIDBYam3re2CwHBgSr1ghveCiijn-8ZhloA9uUCtQ-9_L5S-pur4SYMv5CdV5qdTUFyh7lC5h8Xjd-tL-MFelU99guef9LExY7AFSonuqxbYKVt27xQOtzlMLVNQd2_kNuS16mfXNCphm8=)
15. [kvfrans.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTkn5cSjziM4RLvgr0HaA7iZ0rzs1pzDRTVf06pXSxpcGWuuOtlrKRmRek8lX8ZaYChKtiB6LlPTg3uHhUT21lY7IF5WGgULBRaT3TdBClDcBR8GgMkmEO3-GeGw0E5Zdg6kARuvQkNFVkAhLKLieVJJzEHNc=)
16. [maximeallard.lu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwa_eaCLSOw3yDMOHv3uJwAbO3YK3CW52uRzv9Rw25wS6sT5U3xekHAHavY9ZA2_qOnCaJPv2rWOdM8AbqkFkz0MGxuU1Ojq9vxzlwet61vbiNASgpE-gtHtUdF5KxSrxtkeD-a2DZyxwUj1-FRz0QmSw7MRrQ)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmEkaeNJ5I8e9P_EL6ECWH9yMjtv_QRT4HJdNAlPjw06lDQYX5fLQOMzGb98nCoV_142PY5k0nI-q9j9LQrkGI8u1l1-SzV1bTGlPUb86FnOHZljmamayPKTf_49b8RcfEtdGUKgmtL35SwAg4TPlbE_-6KeqEYmuqBJvwA6qub73Gkyis64hvKx_udQY3uxX1GFFKBBk2SydkR1X_PsuoMBgH3zYs)
18. [gwern.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWXhopt37G9LvJiMDVwDp5QK9TUAbSXuW4uljDrrxuCtdOEWBqZVstJgpJvw0NhGCtWHx7-e7E4wXwPwMFCzD28f_A701-02xhswkbOxZs4UWfHsaFRTVGrUm_YOsvmj0-l_3o2tQ5mTYbfsXg7fVKoHo7c_Uu0jMh-qJCHVg=)
19. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjBsZCWiUm2BWZdf5ede8s4rqRsTGXTvAyXiAELLGqlhRwm8inr0yiYc9dp03REjOUvGVKu_GnFtRSjytvCxkEEKWi73kZ0zE7MAu-CUQeBNVyiuth4ZBTwhejf_mbfsVYKxnJhAhAaDmKeA3F9V9hoGCdOt5jmu-bkoLZPG2MpXDtHdlixwFn7Us1L8sm-38jnluT4vLZ-A==)
20. [frontiersin.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEB7CXqc-OoNATFzqfcUOau3iO0lJJTjaRS4pLnRBHFNgfaszuvOR-w6gBvUu742bwAu8HTFKzQCeP3LghvZXTHZZngH6OfJOj_deNdlBR9FssvRGCBlsvIhpJRHdC_kDmdJwsEc302msMfnnr864XaNtsGaufPpIrnMXQzZlk6mAV9FraC5Uw7-bNYxcaSzu0m)
21. [plos.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPdv3oNKVTnkNG2Dw3VOHLVR61cYI3DvaVokpeEo9Ma9EZmIPT4plFsdpASKJTOIbDu-9qwACbaY_gDhqEC2IrUJFIUtzyzXedzvBWDGhaw7dTpKuafky9MpZCc_Y1kCMj2L9ct1CLRK96d_wFcGxCEN3-QuKWHXmD4Y5MRzK8)
22. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYHyu7r_8FCWAEoYLcnGFye7iSYNHMUeTgsL4DAT3QHjBIqlyXjaZcCYm75x3k6t2DIiPtT0I5zBiWvIVAkMMHBR6560WNJy9TFJe2KMlWmKWMgZjrWIVaYld6oAJdajA0uJPrdNOVu8m54DSb09JHNHML3Si38PzqobIoCI7p6LgNARfVdHmq-EeS0xo7fxvhFMSTJvvAIr8vFs-fgYAC39swDFmQFVByLz6YB-RPqzg8P5nREimUP2EepXJx90zV_RIl4Xv8xzTYxQ==)
23. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHzcdAeF-BHoeO1IDeEV9ZhFx9LdVA1hnMzwT0Kb-fSfl6DgMHe9Qha8rg4MAZmi0PNulqOVmFzlA-9WhTyfGs8i-K0qIcNeHDSqRN7YarKP0GU-WhcSfV4Ml1JFBhLiAfqANMQHysu)
24. [knu.ac.kr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0IfT1Rz8Ei9qZ2BO1wjiLmZKtdghxysBmZU0ujIQ-aX0xyHUmQtEMl4KrcXtfOrxhwqk3hZmm4vJ9Gm4Pm9xoikkFqvZpOoeaMteMPmLqie0QzbdDeWUc2QHd-W3MLLwbdtxyFFosWJigkqwsjbA7V-Q-RtX2zTzotDtrqI95D5YhvYKXMDdcn1NCUGPhK34zsmOIAc3JL1QAzlIAn1AEKk4C)
25. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESGjapcXBRAgL2GNxLeE1ceWkCBkVafQNis5Qd46hmy20F4EfSY613ZhbPFaY8A4jbZyZP6djTdsuCnjS89IPV3ua5HJvvPAf4yrJh0i9-hG0U85A9ccKWjCSEx5EMp5zk0vpLmqC-Er8eYspZRKUp_2b6Q0jk_Ow8lhtGSWd9O4a_sGz6cN7IbCkJ_JV4NDQSJA==)
26. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXi8qKtTFUrpmPtot8ujRdUdEFux8F3vSHF2r0bSq4BkZ0PgDF2KyO8PjwiHXxP5snIspLk1U1BDRsNQWLs6v08SOJFpCJGDGFSu-edGKz55w1D-LTmg_tNneClPIfZ0uymZcPSa6HjJvb3qLdP0GGwmiGsX7NIbZN89yQXVxSn-ecWcQXpQoM2A==)
27. [campaignmastery.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEuoWiK2InUII6VjKuLX0NIyLUjZjyS89mW4A5fKdVG_PEbql9Ii7qEefe6MExia8ZsNvhCxzXdCZjEEwvgasgAzgDfNeZPbMXaeMxUJd4-5hftT5cr)
28. [campaignmastery.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFW_foumj_0D90cwuix0pxXir4RUYDqUVY1f64j1DCmXGt6QC3UjFfYd4fnM9bfM9N_Q-QJ5GOPH3kRtsGfgxJKmAu-a92VKbqV9tjOGHI7aD0fB6PcIM2biJqN1TY4d_uBS_4PGdmEa0ljrBRF0DEa385jwHb8_1BMQiXHUtouOlOkI0WHBxr_mLOIADIwBoICH7Y=)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEy04eqCrYPw1W9aqVH7KRtykeLzcQhZki9_JrN2qy5tXu5uKuKLTE58vtJh-TwVlX20CLacHk8GrhBGo0fUDVkhflTVjBC-pt01Kexxu69VJbd_-IbEw==)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWpHG43HjSCEqpiW2JB7XKlgJ360CGOfQSxKrfoAuQi1FJk9OdX7P-M2AYpHfrvUhJRPTSP8RpjGHj8pNWVl2xebYE6k1dDoCIY3MGuDc2kmry2t3kSXTaSg==)
31. [aihomebuilding.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrtj28tctK1IT-v59UX_5YDH_5EEdKgVBTi5WExRIL11oXfcIXvFBAFK_rNEkMR8XCk7uigOA0gsPd0eakZcREUNO3dK2WM-CT2spxCSHzq-T8B6-MfHFfo193fWf27psFjCb36Hjx-pyNzMVrXi1cHlrpZuFa6-qDeBQ=)
32. [amendmentsproject.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrRUoht2HfaeGYtbhO0JpIbuQjxsIknGuBVwwEzrkFkWjfSFm9dY7lVxoGhDhr6tzRjoBwkbJ0yICicX6jij9GlFcJodRDLHdp2nLeWAjgebRyoSyI_h898rwUOQ==)
33. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3e_hNXdSvnXcsQ0682YCvxIMo3qsNEsGQuCOkwQdGZW7uNNpjU1bHWEu1JZ8CjUV-sLrNAHpOM8SEBqFfkBr8kQAeLkGUrnBEq4bMOnf1fhNfUl_jFeZZas3hs8Kua2Omw8TUliYp)
34. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhght_qECF5SwaHsJCpNcwswKodT2p3rtiCuoDOIkiq1zfgJQiV5ojPvKDk9QFjWmGWY1BE6aRPPCayQr-GR-9QDqTZUHVLP2chXxP2-znLvU7255QIjbABTK0kj7taqYV2xuC-8xuxQgAMm8hqINX1TwsqnNZTrk=)
35. [bsky.app](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOonMzL5lC-rrMPJnl7nq6ruNqLgWjuym5-7EXHFL6cYZe-b5PrbDwA_-Odk1Ae05ZJqI5muNq8l4ttDX8OUxn4OpHM6NGdCRUeL5EBEZRvITiwN3tGLkKaeVa7AA-pt2cF_c_FKd5bA==)
36. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGy1kXDGe7dv1voS0Cf1ZsROoEJwfjfiVLDXcLaNc7ulKwyiX3-yceBiyTkTK-n43VPjnS2co_gDKdT4jvTpchZYaA_Aqso6AE636svu7pd7WefvP8bCl_ehhnv2SZA1EA=)
