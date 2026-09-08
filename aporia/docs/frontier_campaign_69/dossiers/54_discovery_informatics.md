# Prompt 54: Discovery Informatics

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChcxbC1mYXBTSEpKLThfdU1QOGNXMnlBYxIXMWwtZmFwU0hKSi04X3VNUDhjVzJ5QWM
**Elapsed:** 365s

---

# FRONTIER PRACTITIONER DOSSIER: DISCOVERY INFORMATICS

Discovery Informatics, specifically the sub-discipline of Literature-Based Discovery, aims to automate the generation of scientifically valid hypotheses by uncovering implicit connections across disjoint bodies of scientific literature [cite: 1, 2]. The field operates on the premise that human researchers cannot read the millions of papers published annually, resulting in "undiscovered public knowledge" where the components of a breakthrough are already published but reside in isolated silos [cite: 3, 4].

The field has evolved significantly from its origins. It is highly likely that traditional heuristic and term-frequency models are now being superseded by massive semantic knowledge graphs paired with deep learning frameworks. Research suggests that while the algorithmic capability to connect distant concepts has improved dramatically with transformers and large language models, the field remains constrained by severe methodological bottlenecks in evaluation and data extraction. The evidence leans toward a future where generative models do not simply propose links, but actively verify them against raw literature to prevent hallucination.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Literature-Based Discovery today is primarily driven by the construction of massive, heterogeneous semantic knowledge graphs derived from natural language processing of publication abstracts, layered with deep learning prediction models [cite: 1, 5]. The core computational challenge is no longer finding paths between terms, but ranking the plausibility and scientific value of millions of potential bridges. The frontier is currently transitioning from purely embedding-based link prediction architectures, such as graph transformers, to hybrid systems that integrate large language models for both context retrieval and multi-hop reasoning. If there is a dominant trend, it is the absorption of this field into the broader domain of Scientific AI or "AI Scientists", where literature-based discovery is treated as the initial hypothesis generation step in a fully automated in-silico research pipeline [cite: 5, 6]. In this merge, the field has quietly lost some of its focus on human-in-the-loop interpretability, trading the highly curated, manually verifiable bridging term lists of the past for high-dimensional latent space proximity scores that are difficult for bench scientists to audit.

What is SETTLED in this field is the foundational ABC transitive reasoning paradigm: if literature A connects to bridging term B, and bridging term B connects to literature C, a latent hypothesis exists between A and C [cite: 7, 8]. It is also settled that simple keyword co-occurrence is functionally useless due to overwhelming false positive rates; relationships must be typed and semantically verified (e.g., "drug X inhibits protein Y" rather than merely appearing in the same sentence) [cite: 1, 9].

What is CONTESTED is the evaluation methodology, which is currently the most significant schism in the field. One side, representing historical continuity, evaluates new algorithms by their ability to replicate classic, human-curated discoveries (such as Swanson's historic link between dietary fish oil and Raynaud's syndrome) [cite: 10, 11]. The opposing side, led by researchers such as Erwan Moreau, argues that this retrospective replication is statistically invalid, highly overfitted, and akin to building on sand [cite: 10, 12]. They advocate for time-sliced temporal holdouts, where models are trained strictly on data published before a specific year and evaluated on their ability to predict the connections that actually emerged in subsequent years [cite: 12, 13]. 

What is OPEN is the challenge of fully automated verification and the elimination of structured data dependency. Current frontier systems still rely heavily on legacy rule-based natural language processing pipelines to extract semantic triples before doing any graph mathematics. Replacing these brittle extractors with generative agents that can read full text and reliably populate a graph without hallucination is an open problem [cite: 9, 14]. Furthermore, extending these architectures reliably outside of the heavily standardized biomedical domain (which benefits from ontologies like the Medical Subject Headings) remains largely unsolved [cite: 1, 15].

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL

Authors: Don R. Swanson
Year: 1986
Title: Undiscovered Public Knowledge
Venue: The Library Quarterly
Identifier: DOI 10.1086/601720
This is the genesis of the entire field, formalizing the epistemological argument that logically related but bibliographically disjoint fragments of literature constitute undiscovered knowledge. A practitioner must read this to understand the underlying philosophy of the ABC discovery model.

Authors: Don R. Swanson
Year: 1986
Title: Fish Oil, Raynaud's Syndrome, and Undiscovered Public Knowledge
Venue: Perspectives in Biology and Medicine
Identifier: DOI 10.1353/pbm.1986.0087
This paper operationalizes the theory into the field's first concrete experiment, successfully linking fish oil to Raynaud's syndrome via intermediate biological properties like blood viscosity. It established the replication benchmark that the field has fixated on for four decades.

Authors: Vetle I. Torvik, Neil R. Smalheiser
Year: 2007
Title: A quantitative model for linking two disparate sets of articles in MEDLINE
Venue: Bioinformatics
Identifier: DOI 10.1093/bioinformatics/btm161
This paper anchors the specific statistical method you are investigating. It demonstrates how to transform the chaotic output of a two-node search into a supervised machine learning problem by computing eight specific features for each bridging term and fitting a logistic regression model to rank them by relevance. 

Authors: Neil R. Smalheiser
Year: 2012
Title: Literature-based discovery: Beyond the ABCs
Venue: Journal of the American Society for Information Science and Technology
Identifier: DOI 10.1002/asi.21599
This is a critical, load-bearing paper that critiques the limitations of the strict ABC model and outlines the necessity for objective, literature-based interestingness measures. It defines the transition from simple heuristics to complex data mining.

CURRENT

Authors: Justin Sybrandt, Ilya Tyagin, Michael Shtutman, Ilya Safro
Year: 2020
Title: AGATHA: Automatic Graph-mining And Transformer based Hypothesis generation Approach
Venue: Proceedings of the 29th ACM International Conference on Information and Knowledge Management
Identifier: arXiv:2002.05635
This paper defines the modern graph-transformer frontier. It demonstrates how to replace Torvik and Smalheiser's hand-crafted features with embeddings derived from a 10-billion edge semantic graph, achieving best-in-class performance on temporal holdout validation.

Authors: Erwan Moreau
Year: 2023
Title: Literature-based discovery: addressing the issue of the subpar evaluation methodology
Venue: Bioinformatics
Identifier: DOI 10.1093/bioinformatics/btad090
This is the most important methodological critique of the last five years. It systematically dismantles the field's reliance on replicating Swanson's old discoveries and establishes why large-scale, time-sliced datasets are the only rigorous way forward.

Authors: Bojan Cestnik, Andrej Kastrin, Boshko Koloski, Nada Lavrac
Year: 2025
Title: Make Literature-Based Discovery Great Again through Reproducible Pipelines
Venue: Advances in Intelligent Data Analysis XXIII (IDA 2025)
Identifier: arXiv:2502.16450
This paper addresses the field's severe technical debt by publishing dockerized, reproducible Jupyter notebooks that implement the entire pipeline from data acquisition to evaluation. It is the best starting point for a computational scientist writing their first lines of code in this domain.

Authors: Menasha Thilakaratne, Katrina E. Falkner, Thushari Atapattu
Year: 2019
Title: A systematic review on literature-based discovery workflow
Venue: PeerJ Computer Science
Identifier: DOI 10.7717/peerj-cs.235
If you read only one survey, read this one. It provides a comprehensive technical breakdown of the inputs, processes, outputs, and evaluation metrics that define the LBD workflow prior to the large language model era.

PART 3. SOFTWARE I CAN ACTUALLY RUN

Name: AGATHA
URL: https://github.com/JSybrandt/agatha
Language: Python
Licence: GPL-3.0
Year: 2021
Verdict: DORMANT
This is the community standard for deep-learning-based hypothesis generation. It can run a temporal holdout experiment predicting post-2015 biomedical discoveries using a graph constructed from pre-2015 literature. The primary gotchas are its extreme compute and memory requirements, and its dependency on older PyTorch and CUDA versions (specifically 1.4 and 9.2) which can be notoriously difficult to build on modern toolchains without strict Conda environment replication. 

Name: MOLIERE
URL: https://github.com/JSybrandt/MOLIERE
Language: Python
Licence: BSD-3-Clause-Clear
Year: 2018
Verdict: ABANDONED
This was the predecessor to AGATHA, representing the state-of-the-art for shortest-path graph searches combined with Latent Dirichlet Allocation topic modeling. You can theoretically run historical hypothesis generation queries with it. However, its network construction phase requires over 1 terabyte of RAM to execute the AutoPhrase module. It is famous, heavily cited, but effectively dead for modern practical deployment.

Name: ida2025lbd
URL: https://github.com/akastrin/ida2025lbd
Language: Python (Jupyter Notebooks)
Licence: UNCONFIRMED
Year: 2025
Verdict: MAINTAINED
This is a modern reimplementation of classical LBD methodologies. It allows you to run Swanson's closed discovery, open discovery, text-mining based linking (CrossBee), and outlier-based document discovery today. Its main advantage is that it is explicitly designed for reproducibility via Docker. Its limitation is that it focuses on demonstrating classical and bisociative architectures rather than scaling up to the massive graph-transformer sizes of AGATHA.

Name: HakkenOSS
URL: https://github.com/SonyResearch/HakkenOSS
Language: Python
Licence: UNCONFIRMED
Year: 2026
Verdict: MAINTAINED
This repository implements the THiGERLLM (Temporal Hierarchical Graph-based Encoder Representation with LLM) model. It allows you to run predictions for novel relationships using temporally indexed graph features. Because it is highly contemporary, it integrates modern LLM components for explainability. The limitation is that community adoption and third-party debugging are still in their infancy.

Name: Arrowsmith Two-Node Search
URL: http://arrowsmith.psych.uic.edu
Language: Web interface (Backend languages unknown)
Licence: Closed Source Web Service
Year: 2011
Verdict: DORMANT
This is the famous tool built by Torvik and Smalheiser to execute the statistical feature-ranking method you are anchoring to. It is not a software package you can download, but a web application. It is effectively dormant; while the theory is foundational, no serious computational practitioner would use a web GUI for a programmatic pipeline today, and the backend source code was never distributed for local execution.

PART 4. DATA AND BENCHMARKS

Name: SemMedDB (Semantic MEDLINE Database)
URL: https://skr3.nlm.nih.gov/SemMedDB
Size: Over 130 million semantic predications (triples).
Licence: Public access, but requires an active UMLS (Unified Medical Language System) license to download.
Used to measure: The base topology of biomedical knowledge. It is not a benchmark, but the foundational dataset used to construct the knowledge graphs for almost all modern LBD systems.
Known problems: Because the semantic triples are extracted using a legacy rule-based system called SemRep, the dataset contains significant noise, extraction errors, and heavily skewed generic relationships. 

Name: AGATHA 2015 Temporal Holdout
URL: Distributed via Google Drive (gdown) links in the AGATHA GitHub repository.
Size: 38.5 Gigabytes.
Licence: Open access.
Used to measure: Predictive validity via time-slicing. The model is trained on graph embeddings from pre-2015 text, and evaluated on its ability to highly rank term pairs that were first formally published together between 2015 and the present.
Known problems: It is authoritative for evaluating graph-transformer architectures, but is completely saturated with biomedical specificities.

Name: Swanson's Target Discoveries (Migraine-Magnesium, Raynaud-Fish Oil)
URL: Present in almost all LBD repositories, including ida2025lbd.
Size: A few megabytes of target terms and associated text.
Licence: Open access.
Used to measure: Historical replication capability. Can your algorithm find the B-terms connecting Migraine to Magnesium using literature prior to 1988?
Known problems: This is merely a popular benchmark, not an authoritative one. The field acknowledges severe overfitting to these specific discoveries. Solving this benchmark no longer proves that an algorithm generalizes to unguided discovery, and evaluating against it is heavily criticized as a methodological failure.

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment to establish baseline competence in this field is the AGATHA temporal holdout validation.

Exact software and version: AGATHA (commit hash from early 2020 via github.com/JSybrandt/agatha). You will need Python 3.8, PyTorch 1.4, and CUDA toolkit 9.2 exactly.
Exact dataset: The 38.5 GB AGATHA 2015 validation subset, downloaded via the repository's provided gdown script.
Parameters: The experiment uses the default pre-trained stacked transformer encoder layers. The input requires a set of UMLS concept term pairs and a fixed-size random subsample of predicates containing each term.
Independent replicates and seeding: 1 replicate. The validation set is a deterministic temporal slice of reality (what actually got published after 2015), so statistical variance comes from the negative sampling of random term pairs, which is seeded per the repository defaults.
Compute cost: Inference is heavy. Expect to require a P100 or V100 GPU, tens of GPU hours for processing the full test set, and over 100 GB of system RAM just to load the graph embeddings into memory.
Expected result: An Area Under the ROC Curve metric of approximately 0.9 or higher for ranking published subject-object pairs above randomly composed negative samples, across the twenty most popular relationship types. 
Citation: Sybrandt et al., 2020 (arXiv:2002.05635).

Three most common ways people get this experiment wrong:
1. Memory allocation failures. Attempting to load the entire graph embedding dictionary into standard desktop RAM will crash the process immediately.
2. Toolchain mismatches. Running the model on modern PyTorch versions (2.0+) will fail due to deprecated tensor operations and incompatible state dictionary formatting.
3. Data leakage. If rebuilding the graph from scratch rather than using the provided 38.5 GB holdout, users often accidentally include MEDLINE abstracts published after 2015, feeding the answers directly into the training data and artificially inflating the ROC curve to 1.0.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

No off-the-shelf tool currently provides a scalable, local LLM-based verification bridge between the graphical link prediction output and the raw source text. 

If you build an AGATHA-style system, it will suggest thousands of highly probable edges (A, C) based on graph topology. However, because the underlying graph (SemMedDB) was built with brittle rule-based extractors, many of those topological features are hallucinations of the extraction phase.

You will have to build a Verification Module.
What goes in: A candidate hypothesis represented as a semantic triple, and a list of PubMed IDs representing the abstracts that the graph algorithm claims support the bridging nodes.
What comes out: A boolean validity flag and a floating-point confidence score indicating whether the raw text actually implies the predicted biomedical mechanism, effectively acting as an automated peer reviewer for the graph's output.
The hard part: Managing context windows and API/local inference latency. You must retrieve hundreds of abstracts per candidate edge, inject them into an LLM context window, and force a constrained output, millions of times over. 
Effort: This is a massive engineering effort in data pipelining and orchestrating asynchronous local LLM inference (e.g., using vLLM), but it is the exact component that research groups are currently rebuilding privately to clean up their graph predictions.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The most critical negative finding in this field is the failure of the replication evaluation methodology. For decades, researchers evaluated their systems by restricting MEDLINE to pre-1986 and checking if their algorithm ranked "blood viscosity" high enough to connect fish oil and Raynaud's syndrome. Erwan Moreau (2023) authored the standing critique that this method is fundamentally flawed. It relies on a statistically insignificant sample size of cherry-picked historical discoveries, allows extreme algorithmic overfitting, and measures an artifact of the benchmark rather than true discovery capability. This critique has not been fully answered by the old guard, though the frontier has quietly shifted to temporal holdouts in response.

Another failed programme is the attempt to solve the "generic term" problem using stopword lists. Early systems found that their bridging terms were flooded with generic words like "disease", "patient", or "treatment", creating massive false bridges. Attempts to curate universal stopword lists failed because terms that are generic in one subdomain are highly specific in another. Relying on simple frequency cutoffs also failed because highly connected hub nodes are often the most important biological pathways. 

Pure co-occurrence has also been definitively shown to fail. Early methods assumed that if term A and term B simply appeared in the same abstract, a relationship existed. This yielded unmanageable false positive rates. The field learned that relationships must be semantically typed (extracting the subject, verb, and object) to be mathematically useful.

Finally, the field has a standing critique regarding rule-based extraction ceilings. SemRep, the algorithm that builds the standard SemMedDB graph, operates on rigid linguistic rules. It has been shown that SemRep completely misses complex, multi-sentence reasoning and frequently misidentifies subjects and objects in passive sentences. Graph algorithms built on top of this data will eventually hit a hard accuracy ceiling because they are optimizing over fundamentally corrupted topology.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

To run frontier experiments that have not been done, a well-resourced newcomer should execute the following, ranked by impact:

1. The Non-Biomedical Temporal Holdout Evaluation
What it is: Build a time-sliced evaluation harness for a completely different scientific domain, such as materials science or quantum computing physics, utilizing the Torvik/Smalheiser feature ranking approach but with modern embeddings.
Feasibility: Feasible now because open-source LLMs can perform the named entity recognition and relation extraction required to build a custom knowledge graph for any arbitrary domain, bypassing the lack of a materials-science equivalent to UMLS.
What it measures: It measures whether the algorithms currently dominating LBD (like graph transformers) actually capture universal patterns of scientific discovery, or if they have merely overfitted to the specific citation topologies of the biomedical community.
Falsification: If the model achieves high AUC on biomedical temporal holdouts but fails entirely to predict 2025 materials science linkages from 2022 data, the hypothesis that LBD algorithms are domain-agnostic is falsified.

2. The Multimodal Text-Structure Fusion Experiment
What it is: Run an LBD link prediction experiment where the node embeddings are created by concatenating text-derived semantic vectors with structural graph vectors (e.g., molecular fingerprints or SMILES strings processed by a graph neural network). 
Feasibility: Feasible now due to the standardization of chemical graph neural networks and multimodal fusion architectures.
What it measures: It measures whether structural data provides orthogonal predictive signal to textual data in hypothesis generation.
Falsification: If the precision at k of the multimodal model is equal to or worse than the pure text model, the idea that literature graphs lack structurally inferable data is falsified.

3. The Generative SemRep Replacement
What it is: Rebuild the core subset of the SemMedDB knowledge graph using a localized, quantized LLM instruction-tuned specifically for strict semantic triple extraction, and run standard LBD ranking algorithms on the resulting clean graph versus the dirty legacy graph.
Feasibility: Feasible now due to the cheap local inference of highly capable 8-billion parameter models.
What it measures: The exact performance penalty inflicted by legacy rule-based extraction on downstream discovery ranking.
Falsification: If the LBD ranking AUC does not significantly improve on the LLM-extracted graph, the critique that SemRep's noise is the primary bottleneck to discovery is falsified.

What will NOT work:
Building another graphical user interface or web application for closed ABC discovery. The bottleneck in Discovery Informatics is no longer user experience or finding the computational resources to execute a shortest-path algorithm. The bottleneck is the mathematical representation of the text and the rigorous verification of the predicted bridges. An experiment focused on a new UI will measure software engineering preferences, not discovery capability.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZRCZWKkI6jjQefngwGZXRF3t7PfE9W8shwxS4q72e5jVga4npC6XLFYI8ESU6B-R1Pap9gxrs2KEMK16k7PmL83txDJWwNc5WlzHeG3EG-HvHW5fmQXhQwQ==)
2. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1YMBZ7Uli_pL7E7FB-sjn819jklFyeVLUMz4y5aeQSVPyrbF_9k49-xYxmyLKl35xr2SPR7qGDmNYKuBY_lcxol42SUGd_i1NGiwt9kXmbdLacodORtmU70YXkRQVtaDf_2lWmFpAakzIN3X0cQ==)
3. [semopenalex.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEK62qdeTA_TTdleB0zVrNksnjn95_f9I97LxoI1bSeZ_ZCfLyRqTQAW0hvqUofeXwEzwe__adwj7-TvG5Xt0mnlhOrtsuVOVXInxHofzge8EHAGdex_da9gktiIEOnyf8yorLppGhQxQHaJHqvyR40fWWGiI9eAZtbmOuAnVcac8lQ-IzNSCXbxMgRAuSX_4npS_sUcPos4Q4Z)
4. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGSSK9sCROWe7LvUUV3r9bfVNQpgMg1Yp_79PAH7HjrbrQAd_9qpjTYDSH92Tfj1wpGJLj9_SoMBwy5N8t6jS2fSwLGfjWrqYRFK_Pvfd_SPg1aQXEmOuegRs3ATJeEkh42ZjolDVeMEcBJ-0wxqDgZ5_UzQh5GSlseGQzA-MA77xf4Yp7luml2f_FlkyGQQ4BeTMZ8WljFMiZGdN9pc9fkB1m29m3PII8QINOaSe1gLjoG4WqRVg1iHUj1r6hDzg9IPw==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHV_68-SeYqavtJ5qB9hWEDpSL3iHPahmj2W9lTsEOKjMDPzTFqdYNc0FOSJXLanHd-0XGhLza0NKxHRkOttAl_BhPKA7jw_vVAeICSaAxR9jhDOLCn4g==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbxqAB1yKOVw0sCbPOBsUFahJbf3OuYrCNYlHPvihoVr_iSFXELL4fKqwK5-8oCQWulAq7YHNQ1BN2Tif8Fh2BnEXYGAu03MBc95Reugm0VZaDRZP2i3ISAQ==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0omTGMSYoIE4Jt067F3k8GA4Au0JBTibemN_QZvcen-x7hHhGgVPAP4hnYYi9rtGy7xAkzHYlqSFfBXAADEFw2sutuTX-FK_3HDAP9_jti1-00qlQPg==)
8. [maxapress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDLhsiPg0cW6FTsjMkUM3sd-8i4FcCucPNavL7f4K8M_5AaZjCvJgvVrRFiTPTAqYZZL0B4AizVT4bgcalsCzL0kb238QvT44dzQ6We0do-fhUzuCLhNLMz5ykaXDop7RnOIWC24CJhb0vushSatJ0UR0VoCPeP1GJhYXoD0o=)
9. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHf-C8lZIrjgP-MP7yxZI3TerW7uNnT9uWRaNwr0nxleizec2oMg3bqFhc4bp9Rzuj8umMZkThdvo0652C7Vt8M2DA3amTmJTDBMtNO_m_DJP6P3nX1HobUd5w8C3aKyg==)
10. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiE6_tax1jtHufnyfzeJmudK94MlMOAWwm_nKO6iHKxVVbQ8cqR72Cvnhd8tLqeLbIVW6U0m3eer-dzwvtEEbZM021VWpZuyEr_miKWdBvAMwibW4WtB2d5TRx43f2lIFI_VdUxBlS)
11. [elicit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmtPWDeMlQ6XDt7ncyRdyWqNeLD8WLnM39ihS-3QFyQB-6abZHzUFuu-oTfC5IIM0bpeYq5oeNflNhAnAFJuvMi96HFHW972TGXZcbqafoCvD_Ca5ShduPBnvPij2CLbSGvjwx5AMR2g==)
12. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGt0EB0oJp6I5Eklyr6k7p5d8RVSIDUOr7asviwwMxC35kaw29rS0wsnhus_K-VC1sK-nuvqQpshSNftU86jBmu7-hiRbnk9Ux14EFe-zqhdxVkULt9sIWv7sAlIn44wkk4TFJcTWximeMVXr3U2BP4bcuL3d0X8CWfJw==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9UgQUBn9_qXxDaqx-F4bzwLV6h8G8xcC5duUhMCoIm_ifdbP9Q41tYjdm7mPFQqXJkW78-x9bPDelPfPO-mE1OBlrnCLLbz5sT3iEqWkxfUTeUwtMVQ==)
14. [githubusercontent.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyA9XrNfAOlwDXUD2duGNvki30AtDAVByIwmurXOrF-UwhP3SIXCBOY_QSL27iErduyLZXrJUyE64UqQ0rnbx41gd2q7vuis9JqHYoPb6Oe2WDQ2DOtqVZLYRX4lOcw3qNhCvzBLUX0jSh7DjCLDZaoefUxfTzGyWODISNt5ZcoMrD0vQOgyWVG5Kv)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-UZiIiXbTQ5r3CxyyPgGTXrzKcq4PV7fIYHC-Ncp1dlBCl_MX-7wDzYvanbzshgatIbERF85s8Y98eXBkUvNlF-z6B2kULVzIa3RElWtSDCiKv7A-MFQCYA==)

