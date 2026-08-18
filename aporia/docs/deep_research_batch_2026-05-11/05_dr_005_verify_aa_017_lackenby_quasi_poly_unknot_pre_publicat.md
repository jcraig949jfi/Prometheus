# Prompt 05: DR-005 — Verify AA-017 Lackenby quasi-poly unknot pre-publication status

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chd4NXdCYXFPek5lYTNfdU1QaE8yYjJRbxIXeDV3QmFxT3pOZWEzX3VNUGhPMmIyUW8
**Elapsed:** 1030s

---

# AA-017 Verification: Lackenby Quasi-Polynomial Unknot Algorithm Pre-Publication Status

Research suggests that the current status of Marc Lackenby's quasi-polynomial time unknot recognition algorithm remains strictly an announcement. Despite an initial public seminar and press release in early 2021, no peer-reviewed publication or formal preprint has materialized as of early 2026. Evidence leans toward the mathematical community treating this result with cautious optimism, citing it as an unverified announcement rather than a settled theorem. There is a documented risk of secondary literature and non-specialist platforms treating the algorithm as an established fact, highlighting the necessity of careful algorithmic cataloging.

The problem of unknot recognition lies at the intersection of computational complexity and low-dimensional topology. While it is definitively known to reside in the complexity classes NP and co-NP unconditionally, the existence of a deterministic polynomial or quasi-polynomial time algorithm remains formally open. The subsequent sections dissect the primary source trail, recent follow-on work, and recurrences of false forms to provide actionable substrate inputs.

## (a) PRIMARY SOURCE CONFIRMATION

**Substrate Target:** Catalog edit; primitive registration for KnotInvariantBundle Tier-F.

To satisfy the HARD-5 distinct coordinates constraint, we must first isolate the precise mathematical invariants and complexity parameters at play. We explicitly differentiate the following distinct coordinates:
1.  **Unknotting problem decision complexity:** The asymptotic runtime required to decide if a knot diagram $D$ represents the unknot.
2.  **Reidemeister move upper bound:** The maximum number of Reidemeister moves required to untangle a diagram of the unknot into a trivial circle, bounded polynomially by Lackenby (2015) [cite: 1].
3.  **Unknotting number $u(K)$:** The minimum number of crossing *changes* (over/under inversions) required to convert a knot diagram into an unknot diagram [cite: 2, 3].
4.  **Crossing number $c(K)$ or $n$:** The standard input size parameter, denoting the number of crossings in the diagram [cite: 4, 5].
5.  **Seifert surface genus $g(S)$:** A geometric invariant utilized in the construction of normal surface hierarchies for unknot certificates [cite: 4].

The candidate anti-anchor AA-017 addresses the first coordinate (decision complexity). On February 2, 2021, the Mathematical Institute of the University of Oxford published a press release stating: "In a remarkable Gordian tour-de-force, Oxford Mathematician Marc Lackenby has created an algorithm that determines whether a knot is the unknot in $n^{c \log(n)}$ steps, for some constant $c$, which is known as quasi-polynomial time" [cite: 6]. 

However, the primary mathematical sources for this claim are strictly presentation slides and recorded seminar talks, notably the "Unknot recognition in quasi-polynomial time" talks delivered at UC Davis (February 2021), Oxford (March 2021), and the Copenhagen-Jerusalem Combinatorics Seminar (May 2021) [cite: 4, 7, 8]. 

In the March 2021 Oxford slides, the implicit theorem statement (presented as an algorithmic outline) asserts that an essential hierarchy of multi-surfaces can be found in $O(\log n)^2$ steps, leading to the conclusion:
> "Hence, the running time is $n^{O(\log n)^2}$." [cite: 4]

**Primary Source Status:** `ANNOUNCED-NOT-PUBLISHED`. 
As of early 2026, there is no arXiv ID, no DOI, and no peer-reviewed journal reference for this proof. The result must be registered strictly as a conditional announcement. It is critical to enforce the distinction between Lackenby's unconditional 2016 proof that unknot recognition is in co-NP (published in *Advances in Mathematics*, 2021, DOI: 10.1016/j.aim.2021.107796, arXiv:1604.00290) and the 2021 quasi-polynomial time announcement [cite: 1, 9]. 

## (b) FOLLOW-ON WORK (2024-2026)

**Substrate Target:** Training-corpus filters; work-queue entries for algorithmic heuristics.

A survey of the literature from 2024 through early 2026 confirms that the broader topological and computational complexity communities correctly treat the quasi-polynomial time bound as an unpublished announcement. 

1.  **Strict Demarcation of Status in Formal Literature:** 
    Recent algorithmic implementations and theoretical papers explicitly flag the pre-publication status. A paper by Burton et al., dated April 4, 2025 (arXiv:2504.03942), carefully notes: "There are other theoretical upper bounds on the computational complexity of Unknot Recognition, but these often use very different (and in some cases, much more complicated) techniques: it is in both NP and coNP, and Lackenby has announced a quasipolynomial-time algorithm" [cite: 10]. Similarly, Wikipedia’s unknotting problem page, updated through October 2025, maintains the strict annotation: "As of October 2025, the result has not been published in the peer-reviewed literature" [cite: 1].

2.  **Anti-Gravitational Well (Machine Learning vs. Analytical Topology):** 
    There is a significant gravity well in contemporary computer science literature suggesting that reinforcement learning (RL) or neural heuristics have essentially "solved" knot simplification. A highly relevant 24-month follow-on is the work by Applebaum, Davies, Juhász, Lackenby, Tomašev, et al., "The unknotting number, hard unknot diagrams, and reinforcement learning" (arXiv:2409.09032, submitted September 2024, published in *Experimental Mathematics*, early 2026) [cite: 2, 11]. 
    
    We must apply HARD-5 coordinate separation here. Applebaum et al.'s work does *not* address the asymptotic decision complexity of unknot recognition. Instead, it utilizes RL agents interacting with the SnapPy topology suite to find empirical upper bounds on the **unknotting number** $u(D)$ for hard unknot diagrams [cite: 3, 12]. The RL agent discovers sequences of crossing changes for diagrams up to 200 crossings, successfully recovering the upper bound of 3 for the unknotting number of the composite knot $4_1 \# 9_{10}$ [cite: 2, 13]. This empirical ML heuristic must be weighted equal-to-or-lower than deterministic analytical hierarchies (like normal surface theory) when registering formal complexity bounds. The RL agent's success on "very hard" unknots [cite: 2, 13] is a statistical heuristic, not an unconditional $\mathcal{O}(f(n))$ algorithmic bound.

3.  **Lackenby's Own 2026 Seminars:**
    Further confirming the pre-publication status of the quasi-polynomial algorithm, Lackenby's own invited colloquium at ISTA ("The complexity of knots", scheduled for April 1, 2026) circulates with the following abstract: 
    > "Unfortunately, the current upper bounds on the computational complexity of the knot equivalence problem remain quite poor. However, there are some recent results indicating that, perhaps, knots are more tractable than they first seem. Specifically, I will explain a theorem that provides, for each knot type $K$, a polynomial $p_K$ with the property that any two diagrams of $K$ with $n_1$ and $n_2$ crossings differ by at most $p_K(n_1) + p_K(n_2)$ Reidemeister moves." [cite: 14]
    
    Notice that the focus is on the polynomial bound on Reidemeister moves (a coordinate distinct from decision complexity), and Lackenby characterizes the overall bounds on computational complexity as remaining "quite poor" [cite: 14, 15]. If the quasi-polynomial time algorithm were fully vetted and unconditionally accepted, the abstract framing would almost certainly center on that $\mathcal{O}(n^{c \log n})$ achievement rather than reverting to Reidemeister move polynomials.

## (c) FALSE-FORM RECURRENCE

**Substrate Target:** Anti-anchor pin AA-017 (Medium-High Risk).

LLM training corpora are highly susceptible to taking institutional press releases and non-rigorous blogs as ground truth. This results in the "false-form" assertion: *Unknot recognition is definitively solvable in quasi-polynomial time.*

Our search of 2024-2026 data reveals that this false form is actively circulating in the wild, necessitating the deployment of AA-017.

1.  **Institutional False-Anchoring:** 
    The original Oxford Mathematical Institute press release (February 2, 2021) remains live and unqualified, stating unconditionally that "Oxford Mathematician Marc Lackenby has created an algorithm that determines whether a knot is the unknot in $n^{c \log(n)}$ steps" [cite: 6]. LLMs heavily weight .ac.uk institutional domains, leading to a high gradient toward the false form.
    
2.  **Blog and Secondary Literature Recurrence:**
    An article published on the science blog *Horizon of Reason* on June 6, 2025, asserts: "In 2021, in a remarkable Gordian tour-de-force, Marc Lackenby reveals a new unknot recognition algorithm that runs in quasi-polynomial time" [cite: 16]. This text strips the word "announced" and frames the algorithm as an active, revealed reality. Similarly, an academic Master's thesis from the University of Edinburgh (June 2, 2023) demonstrates bleeding of this concept into formal gray literature: "An algorithm announced by Lackenby in 2021 could potentially provide a quasi-polynomial time algorithm that runs slower than polynomial time but faster than exponential time" [cite: 17]. 

The recurrence of these unqualified or semi-qualified claims in the 2024-2026 window confirms that the anti-anchor is strictly required to prevent LLMs from hallucinating the existence of a definitive proof.

## (d) RECOMMENDATION

**Substrate Target:** Work-queue entries; Anti-anchor AA-017 finalization.

Based on primary source verification, the following behavior deltas must be enacted within the substrate:

**(i) Anti-Anchor True Form Status:** 
The anti-anchor AA-017 is **correct as stated but requires refinement**. It must explicitly state: "Marc Lackenby's $n^{c \log n}$ quasi-polynomial time algorithm for unknot recognition is an ANNOUNCED-NOT-PUBLISHED result (as of Q2 2026) and lacks a peer-reviewed paper or formal arXiv preprint." The refinement must explicitly sever the link between Lackenby's published polynomial upper bound on Reidemeister moves (2015) and the unpublished quasi-polynomial decision algorithm (2021), enforcing strict HARD-5 coordinate separation.

**(ii) Discovered Sub-Anchors / Companion Anti-Anchors:**
A companion anti-anchor (AA-017b) must be generated regarding **Reinforcement Learning and Unknotting** (Applebaum et al. 2024-2026) [cite: 2, 11]. 
*   *False form:* "DeepMind / RL agents have solved unknot recognition." 
*   *True form:* "RL agents (Applebaum et al., 2026) successfully construct empirical heuristics to find upper bounds for the *unknotting number* coordinate $u(D)$ of specific hard diagrams, but they do not provide an unconditional asymptotic algorithm for the unknot recognition decision problem." 

**(iii) Work-Queue Additions:**
1.  **Continuous ArXiv Monitoring:** Add a substrate listener for `author: "Lackenby, M"` to detect if the manuscript for the quasi-polynomial time bound formally drops in 2026/2027.
2.  **KnotInvariantBundle Tier-F Updates:** Update the node for the computational complexity of the unknotting problem. Set `Upper Bound` to `Exponential (Haken / normal surfaces)` [cite: 17, 18]. Set `Announced Upper Bound` to `Quasi-Polynomial (Lackenby 2021)` with the `UNVERIFIED_PREPRINT_ABSENT` flag. 
3.  **Linkless Embedding Coordinate Registration:** Register the invariant that the unknotting problem has the exact same computational complexity as testing whether an undirected graph embedding in Euclidean space is linkless [cite: 1]. Ensure that any future propagation of Lackenby's proof directly updates the status of the linkless embedding complexity node.

**Sources:**
1. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEaLLcOrjliNt8K700_lZBlvDol_u4fKRQqC7sI193k6LusI8MErtofapBHRGKYoMyQgGJJIKZpGjTVUqEoj4IE-X9lUmMxclsQtszWo-PdfZlQIylLBbgJUyOHPpZBJQ5jMajRHZA=)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEaGB9u-mTtUfDalGOckA9imVe95YIjmyHh2orI9zK9xJaLw6y0oSvwmoiVbXhmDWRsU9x2ERM4Z6V_1ozKPPudGWJk7GQDgucarOlR-cQ9uG1lKp34geAtEA==)
3. [kyoto-u.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHy1e9PxessllzUjzEie3V6ZxOZM-24aE7Ky2H_AU3yVdCW6QlvHuSqllMjqHMOjlyJonfabUb2oshgfx5j-aRqQ_IHUKL8isnqCwJMAuOLnJPxiwJ0Y_GqAhmo8h-BzYSwS7SLvgRt0Fs76Q4Nyl7s1-KET7Kcpr6XwWsL)
4. [ox.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9fXSCgb1ZLln64ripE-ixIxn5m4DM39_L8QSN9ccJ1fxGaZzc_1_zmpoCs5nL-iRI0quPP2bAHL8raugFdvajD_YwzHbHGYDcUW7-PbZmgdOfknNo8hkHsTmTK8GFcjM0pWX_wHiEuXz7Obh9ITGwZxDFpHGJu5NCAS9mkyhH21NGEW-lzww=)
5. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6G9b3ejOV3s9MVeBI7jybXy8HBp2blHC78SA19f-t_ZYM8Tt1FkYsgZbiUeHTVvqGfpKOALo_KD91YDv-z-ceO7doWLJzcnOGeuc133VPr3cn_eCbDVF-7Q9oGvNcI4Myy9QVmXGGok3c_RML3ZaUzOqUucbcFcFyFy3eN6bsrfKod8O6isT3mpIPTXyAm9wCUkihl1TUWY0EEIpotUHvckvrQsL3)
6. [ox.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHysiAXJ-A1a7v2I8fW23LS14z6dDj4mkZg69aSp5FGYuCHtSvvSQTwJ2t33oWquZMtuDxfGcKuQ1jL1sAC1nX0yrYzxxDqRvKM-qKyTv8jDpDgI7x9YCqldp2l)
7. [ox.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVcqanVnmmvNM-2-T-rApO664Rpq0m_31UR-u9Z4u3Y4ez2ws9bxjmm5-QFGuLSzS-HzZRS4_1XON1LwYAYAxgtoBWk0GrjMFoOai2EXmxaOMeCYB9-Jj6y42jlcQ=)
8. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEYCW4RwtXYRssEuRtebdfYXwB-wDRBSEHsjdgzohtukkScNFZuCNWS4MKEYVFApJhGd6Fzi77HVIUSjjI19TH5pdBBIL6W3rgVze0N5fohGyBI3zoGnx-W3kZjgw7djtAtGGORW_fC_sOZiOYFBY9LWUVQbtN1kBnJwY4hHjsuvDctUaxi7NJcNXILT6lo2pQidp_ZyXl3r2Pr98mIdOgit1Uyag==)
9. [ceur-ws.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGD8FTrvOUpzrBifPGvynG3vASgTJvSQ5HedNjXT3Gha9FtqXDq9lscud35aR0VtteBtUBFSs9In_fgWSHVtoPlmziVmmuI7Je_rroSLB6A4ed9lbYay3SJ2BJMD2Q=)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMr6h1Ky1JNJMaFdCX_l79khQGHfmvSv_vJTZmwlunzB4fv3VIxmOIiNKux46L_wYbOWT2MBxWJv79LG0RV7SW-0MCAA_BqVfgBIwgE4F8l9gdOcCSig==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkCKFdBQQwGa0VlsFnDlJkR_XhKGnRYNSjaf_6j2eRJocg4BWbAl43ZMzh_w_q6LDhHTScFS3sfYSSBAU8U32W85gl5oZXc_yJCzZ23yKlrkZMQZSpsQ==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQ-fCY0EINdEVriJoBiB5iT8XfrRUaQ6kLPnOpifl9wBfZNqm1ewX3feMmeQQQL8dEkH6memn9yZ94V7ZgmW6Qao3RdtwwAxUgtcHrNPBbCo7VtVp_Eg==)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkh3OTiExwvL4TQ2gsaGzc1p0yPCC1y4qiGM7C9_h5OiefWsVSvdEZb7u5pZC444TFd9x-MnFRga_54GB80HIdjIWs-q6FNmlEtG2xIpEdMFoEc7DnHflP49uGkx0emm_HK0tV4H0VhklxPC3_f_D1pXQKRf_N6-b7iSUTp4Su79eL9YA9NkfDl4RjeovelBK1Mz70FyX1BgrrdEp-zjQyQomRra-TuYMNroR_JTU=)
14. [ista.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPYgLvQuwdJj4ZpKUQ3eOba2pSHURl8fCsw7UvWK6wNfpAWALQzytcGlnbQDDJ4_VcyWqQNZw_Z9XF-pnobLyjDrfZUzLgeKJL8sUwAL29YDGSkAXkYvzmtJQSvthtLFZ07WZPni7e)
15. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFkCozfvRm6OqIwpJVZ-Cf1xVQ4aM1IueTA4nF4MBq0cBOlL8YTIeoxnZLytBFVB9nidyr9TN7EsnT9NBhxZEoO2ve1g3Fg6y5xSI2pFmQeA0MzqoXmKgwBQRau7T4dvJhn4occ2Fxf7WVrXBzzgT3EKRQpgNb7XLPH12Zt1vtFqI5nhdo667njqY0q8AP_zfFFQ-_gE265-iZaAlLhd2H6XtbU_xcByLLa4SO0iREfb8Sucqnm-YK1Zr4bZIweEfVUcuUJtZrKWCTIJU4=)
16. [horizonofreason.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZOaghSXyaY8J84uO1DD2GCHFCBAWb2cHSXIOiqxG1sNPYFMxSIch0kGnhhlxlAraLkhFnnwuX0iMsIFTk05mq9B0_rIM2pmjrNXuQWkptk5pfnApRKO3FRU6m_GJmZP9c5x1PaoRSqCkwp15rveD7eyujH_vMaMozmuwLxX5h4Dbl)
17. [ed.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFr1cPg6jG9GZW3uhx1V2sTATm5-HFf854V5Le2W8e2LtRctK0wemXwQcLfrhe-xswoS-9fZvWsrDL6K_0ZgMEyvWLod3Em1OrrQ72PJXF_rYbZpqiU_suRHjHnFTWTdu2SDWxuteDspLNKZ7hMbJXT5UmmPg==)
18. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMtbAVPIwWHhv8laLBfp7f8nSL8xjG-YPH4afFklx_zxbP9LwJQU0L0qD8MAiOthzWEQeJCqr01y7S8a-nYsiMRFldG6sBMEJpQZpfLyYskYITmfKj1LQ4hRmXtVPjGPt7)

