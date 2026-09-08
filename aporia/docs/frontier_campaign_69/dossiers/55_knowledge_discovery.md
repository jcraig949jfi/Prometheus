# Prompt 55: Knowledge Discovery

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChcxbC1mYXNmZ0lkV3hfUFVQZ2F5QnlBSRIXMWwtZmFzZmdJZFd4X1BVUGdheUJ5QUk
**Elapsed:** 426s

---

# FRONTIER PRACTITIONER DOSSIER: Knowledge Discovery

WHO IS ASKING AND WHY
This dossier is constructed for a competent computational scientist initiating an in-silico experimental research programme in the field of Literature-Based Discovery, starting in 2026. The report focuses explicitly on the tacit knowledge, actionable software, rigorous evaluation of datasets, and the theoretical boundaries of the field, moving past high-level surveys into the mechanics of experimental execution.

KEY POINTS
The field of Literature-Based Discovery has existed for decades but has recently undergone a violent paradigm shift.
The classical ABC model formulated by Don Swanson is theoretically settled but computationally superseded. Purely statistical co-occurrence and graph-traversal methods have plateaued.
The frontier has been aggressively absorbed by Large Language Model research, transitioning from link prediction to natural language reasoning and contextualized hypothesis generation.
The most critical bottleneck in 2026 is not generation, but evaluation. The field suffers from a severe, structural evaluation crisis where historical baselines are heavily overfitted, and modern models suffer from unavoidable temporal data contamination.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Literature-Based Discovery is the computational pursuit of "undiscovered public knowledge." Originating with Don Swanson in the 1980s, the field is anchored in the ABC model: if literature A connects to B, and B connects to C, but A and C have never been jointly published, a novel hypothesis can be generated connecting A to C. Historically, this was framed as a closed discovery problem (given A and C, find B) or an open discovery problem (given A, find C via all possible Bs). By 2026, the field has fundamentally transformed. It is no longer just a text-mining or graph-node-link-prediction problem; it has been largely absorbed into the broader domain of AI-driven scientific discovery and agentic systems. Modern approaches synergize Retrieval-Augmented Generation, fine-tuned large language models, and knowledge graphs to generate explicit, context-aware hypotheses in natural language rather than merely outputting ranked pairs of Unified Medical Language System semantic types.

What is SETTLED: The basic premise that massive, disjoint bodies of scientific literature contain latent, highly valuable biological connections is settled. The utility of the ABC paradigm as a conceptual framing device is universally accepted. Furthermore, it is settled that simple lexical co-occurrence approaches (counting shared title words) are obsolete, having been entirely replaced first by dense neural embeddings (Word2Vec, LINE, SciBERT) and now by generative language models.

What is CONTESTED: The evaluation methodology is the single most violently contested aspect of the field. A vocal contingent, most notably Erwan Moreau, argues that the field is "built on sand." The traditional method of evaluating a new system involves checking if it can retroactively discover Swanson's original targets (Raynaud's syndrome and fish oil; migraine and magnesium). Critics argue this is statistically meaningless overfitting. The alternative, "time-slicing" (training on literature up to year T and testing on discoveries published in year T+1), is contested because it assumes unlinked nodes in T+1 are negative samples, when in reality they are often just unpublished or unfunded true biological links.

What is OPEN: The frontier revolves around zero-shot and few-shot contextualized Literature-Based Discovery using Large Language Models, and crucially, how to evaluate them. Because foundational models are trained on internet-scale data up to their cutoff date, evaluating their ability to "discover" something from a 2015 time-slice is impossible; the model has already memorized the 2016 papers that explicitly state the discovery. Creating a contamination-free evaluation harness for post-2024 discoveries remains entirely open. Furthermore, resolving complex aliases, extracting non-standard biological entities beyond strict Unified Medical Language System definitions, and generating full experimental protocols to test the generated hypotheses (moving from Literature-Based Discovery to automated wet-lab validation) are the immediate open challenges. 

What was LOST in the merge: As Literature-Based Discovery was absorbed by generic Large Language Model scientific agents, the field lost the strict, mathematically provable traceability of the graph-based ABC model. When an embedding model or a graph database links A to C, the exact bridging nodes (B) can be mathematically audited. When a generative model suggests an A to C link, its internal reasoning is opaque, and it is highly prone to hallucinating intermediate biological mechanisms that sound plausible but do not exist in the source literature.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: Swanson, D. R.
Year: 1986
Title: Fish oil, Raynaud's syndrome, and undiscovered public knowledge
Venue: Perspectives in Biology and Medicine
Identifier: DOI 10.1353/pbm.1986.0087
Why you must read it: This is the genesis of the entire field. It defines the exact manual methodology of the ABC model that every computational system attempts to automate, showing how blood viscosity and platelet aggregation served as the B-terms linking two entirely disparate literatures.

Authors: Smalheiser, N. R., & Torvik, V. I.
Year: 2006
Title: Collaborative development of the Arrowsmith two node search interface designed for laboratory investigators
Venue: Journal of Biomedical Discovery and Collaboration
Identifier: DOI 10.1186/1747-5333-1-8
Why you must read it: Details the transition from Swanson's manual logic to the first widely adopted computational tool (Arrowsmith). It demonstrates how constraints (like Unified Medical Language System semantic types) were applied to prevent combinatorial explosion when generating B-terms.

Authors: Henry, S., & McInnes, B. T.
Year: 2017
Title: Literature Based Discovery: Models, methods, and trends
Venue: Journal of Biomedical Informatics
Identifier: DOI 10.1016/j.jbi.2017.08.011
Why you must read it: The definitive pre-deep-learning survey. It maps out the exact architectures of the early graph and lexical systems (BITOLA, LION) and formally defines the distinction between open and closed discovery.

CURRENT SOURCES DEFINING THE FRONTIER

Authors: Moreau, E.
Year: 2023
Title: Literature-based discovery: addressing the issue of the subpar evaluation methodology
Venue: Bioinformatics
Identifier: DOI 10.1093/bioinformatics/btad090
Why you must read it: This is the most important methodological critique of the last decade. It eviscerates the field's standard practice of replicating Swanson's 1980s discoveries as proof of algorithmic efficacy, demonstrating that most published systems are merely overfitting to a tiny, unrepresentative dataset.

Authors: Crichton, G., Baker, S., Guo, Y., & Korhonen, A.
Year: 2020
Title: Neural networks for open and closed Literature-based Discovery
Venue: PLoS ONE
Identifier: DOI 10.1371/journal.pone.0232891
Why you must read it: The cleanest articulation of how to map the ABC model onto a modern (though now slightly dated) neural network architecture using graph embeddings (LINE) and convolutional neural networks, heavily benchmarking against the LION LBD system.

Authors: Wang, Z., Cao, L., Danek, B., Jin, Q., Lu, Z., & Sun, J.
Year: 2025
Title: Accelerating clinical evidence synthesis with large language models
Venue: NPJ Digital Medicine
Identifier: DOI 10.1038/s41746-025-01840-7
Why you must read it: Introduces TrialMind and the TrialReviewBench dataset. This marks the frontier of how Literature-Based Discovery is actually being done today: moving away from strict node-link prediction and using generative AI pipelines to synthesize evidence across thousands of clinical trials.

Authors: Kastrin, A., Cestnik, B., & Lavrac, N.
Year: 2025
Title: Recent Advances and Future Directions in Literature-Based Discovery
Venue: arXiv
Identifier: arXiv:2506.12385
Why you must read it: The best, most up-to-date survey currently available. It explicitly covers the transition from knowledge graph construction to the integration of pre-trained Large Language Models, detailing unresolved challenges in scalability and data reliance.

Authors: Cao, L., et al.
Year: 2026
Title: Benchmarking and developing large language models using one million clinical trials
Venue: PREPRINT UNCONFIRMED
Identifier: IDENTIFIER UNKNOWN
Why you must read it: Introduces the LEADS foundation model, highlighting the current brute-force approach to the domain: training specialized models on massive, structured corpora (1.6 million trial records) to outperform generic models like GPT-4 on specific literature mining tasks.

PART 3. SOFTWARE I CAN ACTUALLY RUN

Arrowsmith (UIC)
URL: http://arrowsmith.psych.uic.edu
Language: Perl / PHP (historical)
License: Unknown / Proprietary web interface
Last Activity: ~2017
Maturity: ABANDONED
Experiment it can run: Originally allowed users to input two search terms (A and C) and returned ranked B terms from MEDLINE.
Limitations/Gotchas: This is famous but effectively dead. The web interface frequently times out or returns 404 errors. The underlying Author-ity database is hopelessly out of date. Do not attempt to build on this; it is historically significant but practically useless for a 2026 pipeline.

LION LBD
URL: https://github.com/cambridgeltl/lionlbd
Language: Python
License: MIT
Last Activity: 2020
Maturity: DORMANT
Experiment it can run: Replicates historical cancer biology discoveries and Swanson's classic ABC linkages using neural networks and graph metrics.
Limitations/Gotchas: The canonical implementation relies on older Python environments and pre-transformer neural architectures. The data files required to run it are too large for GitHub and are hosted on external servers that may be unstable. It is a vital reference implementation for graph-based Literature-Based Discovery but requires significant dependency wrangling (e.g., legacy TensorFlow/Keras versions) to execute today.

NN_for_LBD
URL: https://github.com/cambridgeltl/nn_for_LBD
Language: Python
License: MIT
Last Activity: 2020
Maturity: DORMANT
Experiment it can run: Performs open and closed discovery using multi-task convolutional models and LINE graph embeddings.
Limitations/Gotchas: Sibling repository to LION LBD. It suffers from the same toolchain rot. If you run this, you will need to construct a virtual environment running Python 3.6 and legacy machine learning libraries. It is unbuildable on modern toolchains out of the box, forcing practitioners to either port the code to PyTorch or run it inside heavily isolated Docker containers.

TrialMind / DeepRetrieval
URL: https://github.com/pat-jj/DeepRetrieval
Language: Python
License: Open Source (specific license unconfirmed)
Last Activity: 2024/2025
Maturity: MAINTAINED
Experiment it can run: Evaluates generative AI pipelines against human baselines for study search, screening, and data extraction over systematic medical reviews.
Limitations/Gotchas: This shifts the paradigm from finding B-nodes to synthesizing literature. It requires API access to frontier Large Language Models (like GPT-4) or massive local compute to run 3B+ parameter models. It is highly optimized for clinical trials rather than basic biology or molecular pathways.

LBD Contrast
URL: https://github.com/erwanm/lbd-contrast
Language: Python
License: CC-BY-NC (unconfirmed specifics)
Last Activity: 2021
Maturity: DORMANT
Experiment it can run: Executes Moreau's contrastive approach, highlighting the impact of different biomedical "views" and source data on the resulting knowledge base.
Limitations/Gotchas: Designed primarily to prove a methodological point about evaluation rather than to act as a standalone discovery engine. Highly useful for understanding the fragility of traditional evaluations.

PART 4. DATA AND BENCHMARKS

Swanson's Classical Targets
URL: Various historical papers
Size: 2 to 8 target discoveries (e.g., Fish oil/Raynaud's, Magnesium/Migraine)
License: Public domain knowledge
What it measures: Whether a system can retroactively rank the correct B-terms and C-terms at the top of a list given the literature available right before the discovery was published.
Known problems: Catastrophically saturated and overfitted. The field treats this as authoritative out of tradition, but methodologically, designing a neural network with millions of parameters to hit a benchmark of 8 specific historical datapoints is statistical malpractice.

Time-Sliced MEDLINE / PubMed Baseline
URL: ftp.ncbi.nlm.nih.gov/pubmed/baseline/
Size: ~35 million citations
License: Public Domain (US Government)
What it measures: Evaluates systems by hiding all literature published after a specific year (e.g., 2015), asking the system to predict novel A-C links, and then checking the post-2015 literature to see if those links were actually published.
Known problems: It is notoriously noisy. If a system predicts a link that does not appear in the "future" text, it is penalized as a false positive. However, the link might be biologically true but simply unfunded, unresearched, or unpublished. Furthermore, modern foundation models are contaminated because they have already ingested the post-2015 text during pre-training.

TrialReviewBench
URL: Linked via TrialMind repositories
Size: 100 systematic reviews, 2,220 clinical studies, 1,334 manually annotated study characteristics.
License: Academic / Open
What it measures: The ability of an automated agent to search, screen, and extract data comparably to human systematic reviewers.
Known problems: Measures evidence synthesis and extraction rather than pure "discovery" of hidden physiological mechanisms. 

SemMedDB / SemRep Factuality Dataset
URL: semmeddb.nlm.nih.gov (subject to NLM access rules)
Size: Millions of semantic subject-predicate-object triples extracted from PubMed.
License: UMLS Metathesaurus license required (free but requires registration).
What it measures: Used as the foundational knowledge graph for many modern Literature-Based Discovery systems. The specific Factuality subset (500 manually annotated abstracts) measures whether an extracted relation is a confirmed fact, a conjecture, or a doubtful statement.
Known problems: SemRep extraction is highly rigid and misses nuanced or complex multi-sentence biological relationships. It is heavily biased toward strict Unified Medical Language System taxonomies.

PART 5. THE REPRODUCTION RECIPE

The harsh reality of this field is that there is NO single historical experiment that meets the strict bar for a modern, universally informative reproduction. As Erwan Moreau (2023) established, the classic ABC reproduction experiments (like running a graph model to rediscover Swanson's fish-oil connection) are fundamentally flawed due to extreme overfitting and subpar evaluation methodologies. 

However, if you must run a reproduction to understand the mechanics of the field before building something new, you must reproduce the time-sliced closed-discovery baseline using neural graph embeddings. The most rigorous target is the experiment detailed in Crichton et al., 2020 (Neural networks for open and closed Literature-based Discovery).

The Recipe:
Software: The nn_for_LBD repository, specifically the closed discovery pipeline. You will need to build a legacy Docker container running Python 3.6, TensorFlow 1.15, and Keras 2.2.4.
Dataset: The Cancer Landmark Discovery dataset (provided by the LION LBD project).
Parameters: 
- Embedding algorithm: LINE (Large-scale Information Network Embedding).
- Vector dimensionality: 200.
- Negative sampling ratio: Standard LINE defaults (typically 5 negative samples per positive edge).
- Training epoch count: Until convergence on the validation set (typically 10 to 50 epochs depending on batch size).
Replicates: 5 independent replicates with fixed random seeds (e.g., seeds 42, 100, 123, 456, 789).
Compute cost: Approximately 10 to 20 GPU hours on an older generation GPU (e.g., NVIDIA P100 or V100). Trivial on an A100.
Expected Result: In closed discovery, the multi-task CNN model should achieve a Mean Reciprocal Rank significantly higher than the baseline co-occurrence methods, demonstrating a 2x to 4x performance multiplier in ranking the hidden B-terms.
Citation: Crichton G, Baker S, Guo Y, Korhonen A (2020) Neural networks for open and closed Literature-based Discovery. PLoS ONE 15(5): e0232891.

The Three Most Common Ways People Get This Wrong:
1. Toolchain Mismatch: Attempting to run 2018-era graph embedding and CNN code on modern PyTorch/TensorFlow 2.x toolchains. The underlying APIs for negative sampling and graph traversal have changed, leading to silent mathematical errors or outright build failures.
2. Contaminated Baseline Splitting: Failing to strictly enforce the temporal slice. If a graph edge from 2017 accidentally leaks into the 2015 training graph, the model achieves near-perfect accuracy through temporal cheating.
3. Misinterpreting the Mean Reciprocal Rank: Assuming that a high rank on the test set means the model will output biologically valid novel discoveries. The model learns the topology of the biomedical graph (e.g., predicting that highly researched genes will have more links), which makes it rank popular concepts highly, but it does not mean the proposed mechanism is physically real.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you are entering this field with resources and engineering talent, do not rebuild another text-mining pipeline. The critical missing piece of infrastructure is a Temporal API for LLM Evaluation.

What is missing: A unified, queryable, time-versioned knowledge graph and text database of PubMed that can definitively mask all human knowledge published after a specific Unix timestamp, wrapped in an API designed specifically for autonomous LLM agents. 

The Interface:
Input: A natural language query or an A-C concept pair, plus a strict temporal cutoff date (e.g., "December 31, 2018").
Output: The system must behave exactly as the internet and PubMed did on that date. When the LLM requests a search, it receives only abstracts and relationships published prior to the cutoff. 
The Hard Part: You cannot easily "un-train" an LLM like GPT-4 from knowing things published in 2020. Therefore, to evaluate if an agentic LLM can actually perform Literature-Based Discovery, you must either train a custom LLM strictly on pre-2018 data (immense compute cost), or you must build a robust cryptographic-style zero-knowledge evaluation benchmark consisting of discoveries made in the last 30 days (which no LLM has trained on yet), and run the agents against that.
Work Estimate: Building the localized time-sliced search API is about three months of heavy data engineering. Creating a continuous pipeline of "post-training-cutoff" biological discoveries to test LLMs against is an ongoing, permanent curation task requiring wet-lab biological expertise.

Several groups have privately attempted to build localized, timestamped Neo4j databases of the Unified Medical Language System and SemRep triples to prevent data leakage during their experiments, but no authoritative, community-standard off-the-shelf tool exists.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

This is the most treacherous aspect of the field. Many intuitive approaches simply do not work.

Failed Programmes and Negative Results:
1. Pure Graph Link Prediction: Treating Literature-Based Discovery simply as a Knowledge Graph Completion task. Methods like node2vec or standard Graph Convolutional Networks applied to semantic triples often look incredibly successful in training, but fail in practice. They suffer from the "hub problem." The model simply learns to predict edges between highly connected, generic terms (e.g., "Inflammation" or "Apoptosis"). It measures the topological genericness of the term rather than uncovering a specific, actionable physiological pathway.
2. Lexical Co-occurrence on Full Text: Swanson relied on title words. Attempts to scale the ABC model to full-text articles result in combinatorial explosions. Almost every medical concept co-occurs with every other medical concept in the supplementary materials or discussion sections of millions of papers. The signal-to-noise ratio drops to zero without aggressive semantic filtering.

Standing Critiques:
The primary methodological critique comes from Erwan Moreau (2023). He asserts that the evaluation protocols of the field are fatally flawed. 
The Critique: For twenty years, researchers validated their algorithms by showing they could recreate Swanson's discovery of the fish-oil/Raynaud's connection. Replicating two or three known data points provides zero statistical evidence that the algorithm generalizes. When the field shifted to "time-slicing" (evaluating on thousands of novel connections across a time barrier), it created a new problem: false negatives. If an algorithm predicts a link between a drug and a disease, and that link does not appear in the literature five years later, it is marked as a failure. But biology is not fully mapped. The algorithm might be correct, but no pharmaceutical company has funded the trial.
Has it been answered? No. The critique remains unanswered because the only true way to resolve it is to take the algorithm's output and run a physical wet-lab experiment or clinical trial to prove the "false positive" is actually a true discovery.

The LLM Contamination Critique: 
Currently, researchers are using LLMs to perform Literature-Based Discovery. The standing critique is that a model trained in 2024 cannot be tested on a historical time-slice from 2010. The LLM has already internalized the explicit A-C connection from its 2024 training data. It will hallucinate a "discovery" process (A to B to C) to satisfy the prompt, but it is actually reasoning backward from the known answer. This makes historical evaluation of foundation models in this field intellectually bankrupt.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

If you have compute, engineering talent, and want to run frontier experiments, do not attempt to incrementally improve the graph-embedding ABC model. Aim entirely at Contextualized, Agentic Literature-Based Discovery.

Experiment 1: The Zero-Contamination Preprint Evaluator (Rank 1)
What makes it feasible now: High-quality open-source LLMs (Llama-3 architectures) and daily API access to preprint servers (bioRxiv, medRxiv).
The Experiment: Scrape the last 30 days of preprints to identify highly novel, biologically verified connections (the A-C links). Take an LLM whose training cutoff strictly predates this 30-day window. Force the LLM into an agentic loop (like TrialMind or an AutoGPT setup) constrained only to a vector database of literature from before the cutoff. Measure if the agent can generate the exact hypothesis published in the new preprint.
What it measures: The true zero-shot inferential capacity of an LLM to connect disjoint literatures without the possibility of training data contamination.
Falsifiability: If the agent's success rate is indistinguishable from random node-pairing or a baseline BM25 search retrieval, the hypothesis that LLMs can perform genuine multi-hop scientific discovery is falsified.

Experiment 2: High-Throughput Hypothesis to High-Throughput Screening (Rank 2)
What makes it feasible now: Cloud laboratories (e.g., Emerald Cloud Lab) and automated synthesis APIs.
The Experiment: Constrain the ABC model specifically to drug-repurposing for a highly specific cellular phenotype. Use a fine-tuned LLM to ingest literature (A = Target Disease), find intermediate pathways (B), and identify existing FDA-approved compounds (C). Instead of publishing a paper on the computational results, output the results directly as a machine-readable protocol and pay a cloud lab to execute the high-throughput phenotypic screen.
What it measures: The actual, physical hit rate of computational Literature-Based Discovery vs. a random compound library screen.
Falsifiability: If the hit rate of the computational pipeline is statistically equal to or worse than random screening, the utility of the text-mined knowledge graph for this specific domain is falsified.

What will NOT work and why:
Do not attempt to build a better BERT-based relation extraction tool to feed a traditional Neo4j knowledge graph for simple ABC traversal. This is a dead end. The extraction of rigid subject-predicate-object triples (e.g., Drug-TREATS-Disease) discards the rich, contextual modalities of the literature (patient populations, dosages, experimental conditions). Graph traversal on these sterile triples has been researched to death for twenty years and has saturated. LLMs inherently capture the contextual probability distributions of the text; discarding that to build a rigid graph is a regression to 2015 methodologies.
