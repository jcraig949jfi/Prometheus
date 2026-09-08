# Prompt 105: Computational Creativity reproducibility audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chd3cmVmYXR5TEd1dWpfdU1QaVAyOS1RcxIXd3JlZmF0eUxHdXVqX3VNUGlQMjktUXM
**Elapsed:** 364s

---

# Reproducibility Audit of Ritchie's Criteria Applied to the WASP Generative System

**Key Points:**
* The application of early computational creativity evaluation frameworks, specifically Ritchie's empirical criteria and Colton's Creative Tripod, to historical generative systems like the WASP poetry generator is fundamentally not reproducible.
* Reproducibility fails due to a reliance on sequestered source code, the absence of versioned training corpora known as the "Inspiring Set," and an epistemological dependence on subjective human evaluation for core mathematical variables such as artifact "Value" and "Typicality."
* Formal scholarly critiques of these frameworks emphasize that they necessitate excessive human intervention and provide too much opportunity for impressionistic claims, rendering them un-computable as purely algorithmic evaluation metrics.
* Although the original evaluation experiments cannot be faithfully replicated by a programmer today, modern frameworks such as the SciFi-100 dataset offer a rigorously defined substitute. These contemporary benchmarks evaluate generative creativity through LLM-as-a-judge mechanisms and rule-based novelty metrics against a canonical corpus, replacing the subjective artifact-centric scoring of the early 2000s.

## PART 1. VERDICT, IN THE FIRST LINE
NOT_REPRODUCIBLE

The attempt to algorithmically reproduce the evaluation frameworks the field built for itself, specifically the application of Ritchie's empirical criteria and Colton's Creative Tripod to a generative system like the WASP poetry generator, cannot be achieved today by a competent programmer with ordinary resources. A faithful algorithmic reproduction requires a fully automated pipeline capable of scoring artifacts against a predefined baseline. This is impossible because the foundational mathematical models of these frameworks rely heavily on arbitrary parameter tuning, subjective human aesthetic judgments, and unavailable historical datasets. Consequently, an independent researcher cannot reproduce the published criteria scores without injecting their own subjective interpretation or relying on human-in-the-loop survey data. 

## PART 2. THE ARTEFACT TRAIL
The historical trail of the original systems and their evaluation frameworks is fragmented, with critical components either completely lost or never made public in a standard repository.

**Ritchie's Empirical Criteria and Colton's Tripod:**
Graeme Ritchie formally proposed his empirical criteria for attributing creativity to a computer program in a series of papers culminating in a 2007 publication in Minds and Machines [cite: 1, 2]. The criteria are a set of mathematical formulas rather than a standalone software library. Similarly, Simon Colton's Creative Tripod, introduced in 2008, is a conceptual evaluation framework requiring a system to exhibit skill, appreciation, and imagination [cite: 3, 4]. Neither Ritchie's criteria nor Colton's tripod exists as a unified, downloadable evaluation software package. Their implementation is entirely dependent on the developers of the generative systems being evaluated.

**The Generative System (WASP):**
To test these criteria, researchers applied them to specific generative systems. The most heavily documented application of Ritchie's criteria was conducted by Francisco Pereira, Mateus Mendes, Pablo Gervas, and Amilcar Cardoso in 2005, published as "Experiments With Assessment of Creative Systems: An Application of Ritchie's Criteria" at the IJCAI Workshop on Computational Creativity [cite: 5, 6]. The generative system evaluated was WASP (Wishful Automatic Spanish Poet), created by Pablo Gervas around the year 2000 [cite: 7, 8]. WASP was initially constructed as a forward-reasoning rule-based system and an expert system logic program written in Prolog [cite: 7, 9]. 

The original logic program source code for WASP, exactly as it existed during the 2005 evaluation, is lost or sequestered. Its modern repository location is IDENTIFIER UNKNOWN. While some modules of WASP, particularly its metric scansion utility, were later reimagined and integrated into the broader PoeTryMe platform by Goncalo Oliveira et al. in 2014, the exact 2000-era rule base remains UNCONFIRMED in any public archive [cite: 9]. PoeTryMe itself is available and actively maintained, but it does not claim to be a faithful, character-for-character reimplementation of the original WASP logic program used for the 2005 Ritchie criteria experiments [cite: 10, 11].

**The Evaluation Code:**
The specific scripts or algorithms used by Pereira et al. in 2005 to compute the 14 mathematical criteria for WASP's output are IDENTIFIER UNKNOWN. Ten years later, Misztal and Indurkhya (2015) published "A Blackboard System for Generating Poetry," in which they reimplemented the Ritchie criteria evaluation against WASP to establish a comparative baseline for their own system [cite: 12, 13]. The source code for Misztal and Indurkhya's blackboard system, as well as the exact scripts they used to calculate the criteria thresholds for WASP, is IDENTIFIER UNKNOWN. There are no bare URLs, university FTP remnants, or archived GitHub repositories containing the evaluation pipeline used to generate the published numbers.

## PART 3. THE PUBLISHED RESULT TO CHECK AGAINST
A successful reproduction of this evaluation framework would require a programmer to run the WASP generative system and output a set of artifacts that match the Ritchie criteria satisfaction values published in the historical literature. 

The most specific, reproducible claims regarding the application of Ritchie's criteria to WASP are tabulated in Misztal and Indurkhya's 2015 comparative study, which sought to replicate and compare against the findings of Pereira et al. (2005) [cite: 12, 13]. In their published results, Misztal and Indurkhya provide evaluation scores for WASP across Ritchie's criteria 1 through 8. 

The published claim asserts that when setting the threshold parameters for both typicality and quality to a "medium" level of 0.5 on a continuous scale from 0 to 1, the WASP system achieved the following specific figures:
- Ratio of typical results to all results: 1.0 (meaning 100 percent of the outputs were deemed typical examples of the genre).
- Average typicality score: 0.98 to 0.99 depending on the specific thematic run [cite: 14].
- The authors explicitly claim that for WASP, "there are no good atypical outputs for a given threshold" [cite: 12]. 

The citation for these exact figures is the paper "A Blackboard System for Generating Poetry" by Joanna Misztal and Bipin Indurkhya, published in the proceedings of the 2015 international conferences on computational creativity, DOI UNKNOWN [cite: 12]. 

However, because the original papers explicitly report that the numbers generated for the "quality" or "value" mapping relied entirely on human volunteers judging the poems according to their own aesthetic preferences, there is no purely algorithmic number that a computational reproduction could be checked against [cite: 12]. This absolute reliance on post-hoc human surveys makes the historical system fundamentally irreproducible in the automated sense.

## PART 4. WHAT WOULD BREAK A REPRODUCTION
An attempt by a competent programmer to rebuild and run this evaluation framework today would immediately break against several insurmountable methodological and technical barriers.

**Missing Inspiring Sets:**
Ritchie's criteria are mathematically predicated on comparing the system's generated output (the Result Set) against the corpus of data the system was trained on (the Inspiring Set) [cite: 4, 15]. The mathematical intersection of these two sets determines the system's novelty score. The exact corpus of classical Spanish poetry used as the Inspiring Set for WASP in the early 2000s was never published as a standardized, version-controlled dataset [cite: 7, 8]. Without the exact identical Inspiring Set, any calculation of novelty or typicality ratios will wildly diverge from the published results, breaking the reproduction.

**Evaluation Done by Authors' Judgment Rather Than by a Rule:**
The most fatal break in reproducibility is the epistemological nature of Ritchie's "Value" metric and Colton's "Appreciation" metric. Ritchie's formulas require each artifact to be scored on a continuous scale for quality. Rather than using an objective heuristic or an automated aesthetic evaluator, the original researchers relied on interactive human input. Misztal and Indurkhya explicitly state, "In our evaluation, we asked the volunteers to judge the quality of the poems according to their aesthetic preferences" [cite: 12]. Furthermore, Colton's tripod requires a subjective judgment of whether a system is "skillful" and "imaginative" [cite: 3]. An independent programmer cannot algorithmically reproduce a published mathematical result that was originally derived from the subjective feelings of anonymous volunteers in 2005.

**Hand-Tuned Parameters Never Published:**
Ritchie's empirical criteria require the configuration of multiple arbitrary threshold parameters (such as alpha, beta, and gamma) to determine what constitutes "high," "medium," or "low" typicality and value [cite: 13]. While later attempts stated they used a 0.5 threshold to establish a medium baseline, the exact fractional weightings and internal configurations used by Pereira et al. (2005) were never formally published. As researchers subsequently noted, the overall evaluation strongly depends on the selection of these threshold values; minor deviations in parameter tuning cause catastrophic variations in the final criteria satisfaction scores [cite: 13].

**Dependencies on Vanished Languages and Tools:**
WASP heavily utilized early 2000s natural language processing primitives, including specific Spanish POS-tagging algorithms and early builds of WordNet for Spanish [cite: 9]. The original logic programming environment used to execute WASP's generate-and-test heuristics is obsolete, and the specific state of the lexical databases at the time of the experiment cannot be faithfully reconstructed.

## PART 5. THE STANDING CRITIQUE OF THE ORIGINAL RESULT
The attempt to quantify computational creativity using rigid evaluation frameworks like Ritchie's criteria and Colton's Creative Tripod was heavily criticized in the years following their publication. The field subsequently challenged and decisively rejected the notion that creativity could be objectively measured through purely artifact-centric, parameterized formulas.

**Critique of Ritchie's Criteria:**
Ritchie's framework was decisively challenged on the grounds that it was overly complex, un-computable, and too reliant on manual intervention. Franceschelli et al. (2021) and Pease and Colton (2011) re-examined the criteria and concluded that "the presence of many parameters to be tuned makes it difficult to use for comparisons between different systems" [cite: 4]. Critics pointed out that because the thresholds are arbitrary, researchers could easily cherry-pick parameter values that artificially inflated their system's creativity scores. Furthermore, the reliance on human evaluation for the "Value" metric meant that the criteria "rely too heavily on human intervention to be practically useful for computational evaluation of creativity" [cite: 16]. 

Boden (2004) and subsequent theorists criticized artifact-centric evaluations because they completely ignore the generative process, the creative agent's intent, and the cultural environment (the Four Ps of creativity: Person, Process, Product, Press) [cite: 17, 18]. Evaluating a poem based solely on its mathematical resemblance to an Inspiring Set fails to capture the transformational nature of true creativity [cite: 19].

**Critique of Colton's Creative Tripod:**
Colton's Creative Tripod was sharply criticized for lacking formal rigor. In a widely cited standing critique, Oliver Bown (2014) pointed out that "specific definitions for the three criteria are not provided" [cite: 20]. Bown argued that the tripod framework provides "too much opportunity for authors to make impressionistic statements about why their system meets the criteria, without rigorous, falsifiable inquiry into whether its performance in these areas is sufficient" [cite: 20]. Because Colton's definitions of "Skill" and "Imagination" were philosophical rather than mathematical, any claim that a system fulfilled the tripod was ultimately subjective and depended heavily on the authors' own interpretation of their software's behavior.

**Resolution of the Challenge:**
The challenge to these early frameworks resolved with a decisive paradigm shift in the computational creativity community. Recognizing that objective, artifact-only scoring was a dead end, researchers abandoned the pursuit of universal mathematical formulas like Ritchie's criteria. Instead, the field moved toward descriptive, multifaceted self-assessment models like FACE (Framing, Aesthetics, Concepts, Expressions) and IDEA, or embraced interaction-centric evaluations such as the Consensual Assessment Technique (CAT) and co-creative user studies [cite: 4, 21]. The consensus today is that creativity in computational systems is not an objective property of the artifact, but an inherently perspective-dependent phenomenon that varies across critical traditions and human interaction [cite: 22].

## PART 6. IF IT CANNOT BE REPRODUCED, WHAT IS THE NEAREST HONEST THING
Because the historical application of Ritchie's criteria to rule-based generative systems relies on lost code, vanished datasets, and irreproducible human aesthetic surveys, the nearest honest live substitute for evaluating generative computational creativity is the modern SciFi-100 benchmark.

**The Live Substitute:**
The closest rigorous modern proxy is the SciFi-100 dataset and its accompanying LLM Review evaluation framework, introduced in the 2026 paper "LLM Review: Enhancing Creative Writing via Blind Peer Review Feedback" (arXiv:2601.08003) [cite: 23, 24, 25]. 

SciFi-100 provides a unified, highly specified evaluation stack for computational creative writing. It combines LLM-as-a-judge scoring, human preference annotation, and rule-based novelty metrics measured against a canonical corpus of science fiction literature [cite: 23, 25]. Instead of relying on Colton's impressionistic tripod or Ritchie's arbitrary parameter thresholds, this framework operationalizes creativity evaluation through a "Blind Peer Review" interaction topology. In this system, multiple agent models exchange targeted critiques on drafts but revise independently, which preserves divergent creative trajectories and prevents the content homogenization that plagues standard generative models [cite: 24, 26]. 

**What SciFi-100 Does NOT Capture About the Original:**
While SciFi-100 is a robust standard for evaluating automated creativity today, a researcher using it must understand exactly what it fails to capture about the early 2000s evaluation paradigms:
1. It does not evaluate symbolic, logic-programmed expert systems like WASP or JAPE; it is explicitly designed to evaluate the outputs of transformer-based Large Language Models (LLMs) operating on next-token prediction [cite: 24].
2. It does not calculate Ritchie's 14 exact mathematical criteria or define set-theoretic intersections between an output set and an "Inspiring Set." Instead, it uses LLM-as-a-judge rubrics and semantic embedding distance to measure lexical novelty [cite: 23, 25].
3. It focuses on narrative prose (science fiction storytelling) rather than the strict metric scansion, syllable counting, and rhyming constraints of formal Spanish poetry generated by WASP [cite: 25, 27].
4. It abstracts away the philosophical components of Colton's Creative Tripod (Appreciation and Skill) into measurable benchmarks of peer-critique efficacy and human-LLM alignment scales, omitting the philosophical debate over whether the machine possesses genuine "imagination" [cite: 26, 28]. 

By substituting the un-computable subjective thresholds of the past with automated LLM-as-a-judge rubrics tied to a standardized canonical dataset, the SciFi-100 framework allows a competent programmer to reproduce a modern creativity audit, even if the historical criteria remain lost to time.

---

## Historical Context: The Quest to Quantify Computational Creativity
To fully understand why systems like WASP and frameworks like Ritchie's criteria were built—and why their reproducibility ultimately collapsed—it is necessary to examine the historical and philosophical landscape of Artificial Intelligence in the early 2000s. The discipline of Computational Creativity (CC) emerged as a distinct subfield seeking to answer a profound question: Can a machine be genuinely creative, and if so, how can we prove it?

During this era, Margaret Boden's foundational theories dominated the discourse. Boden proposed a crucial distinction between P-creativity (psychological creativity, where an idea is novel to the creator themselves) and H-creativity (historical creativity, where an idea is novel to the entire span of human history) [cite: 4, 29]. Boden further categorized creative processes into three types: combinational (combining familiar ideas in unfamiliar ways), exploratory (searching within a structured conceptual space), and transformational (altering the fundamental rules of the conceptual space itself) [cite: 4, 19, 29]. 

While Boden's philosophical definitions were highly influential, they were inherently qualitative. Computer scientists and engineers, accustomed to the rigorous benchmarking of traditional AI tasks (such as accuracy in classification or speed in search algorithms), demanded quantitative metrics. They needed a way to prove that their generative programs were not just executing deterministic loops, but were outputting artifacts that carried genuine creative weight. 

This demand for quantification gave rise to the "engineering approach" to computational creativity, which focused entirely on technical characteristics and mathematical outputs rather than cognitive parallels [cite: 17, 19]. In this climate, Graeme Ritchie and Simon Colton introduced their respective frameworks. They operated under the assumption that if creativity could be broken down into observable empirical properties—such as novelty, typicality, skill, and value—then a computer could be audited for creativity just as it could be audited for memory efficiency [cite: 22]. 

## Theoretical Architecture of the Evaluation Frameworks
The attempt to formalize creativity evaluation resulted in highly complex theoretical architectures. The two most prominent of these were Ritchie's empirical criteria and Colton's Creative Tripod.

### Ritchie's Empirical Criteria
Graeme Ritchie sought to decouple the evaluation of creativity from the internal, unobservable mechanisms of the software. He argued that human creativity is usually judged by the final product; therefore, to establish a level playing field, machines should be judged solely by their outputs [cite: 3]. This product-centric perspective led to the development of a formal, set-theoretic mathematical model [cite: 4, 17].

Ritchie defined a universe of artifacts and proposed that a generative system should be evaluated by comparing three specific sets of data:
1. The Universe (U): The total theoretical space of all possible artifacts in a given domain.
2. The Inspiring Set (I): The subset of artifacts that the system was exposed to during its development or training. This represents the system's baseline knowledge [cite: 4, 15, 30].
3. The Result Set (R): The subset of artifacts actually generated by the system during a specific run [cite: 15].

To measure the creativity of the Result Set, Ritchie introduced two continuous functions, calculated for every artifact generated:
- Typicality: A measure from 0 to 1 indicating how strongly the generated artifact conforms to the established norms of the genre.
- Value: A measure from 0 to 1 indicating the quality, usefulness, or aesthetic success of the artifact [cite: 4].

Using these variables, Ritchie established thresholds: an alpha threshold for Typicality, a beta threshold for Value, and a gamma threshold for atypicality. By calculating the proportion of the Result Set that exceeded these thresholds, and comparing the intersection of the Result Set with the Inspiring Set, Ritchie generated 14 distinct mathematical criteria [cite: 13]. For example, a system might satisfy Criterion 1 if a large percentage of its outputs are highly typical, and satisfy Criterion 2 if a large percentage of its outputs are of high value. 

The fatal flaw in this architecture, which ultimately breaks reproducibility, is that the functions for Typicality and Value were never defined as executable algorithms. They were abstract mathematical placeholders. When researchers like Pereira et al. (2005) or Misztal and Indurkhya (2015) applied these criteria, they were forced to manually instantiate these functions using human volunteers to read the poems and assign numerical scores based on personal aesthetic preference [cite: 12, 13]. Consequently, the mathematical rigor of the criteria was entirely dependent on the un-computable subjectivity of the human judges.

### Colton's Creative Tripod
In contrast to Ritchie's mathematical product-centric view, Simon Colton introduced a process-centric philosophical framework known as the Creative Tripod [cite: 3, 31]. Colton observed that human perception of creativity is heavily influenced by understanding how an artifact was made. If two identical paintings are produced—one by a master artist and one by spilling paint randomly—the former is deemed creative and the latter is not, despite the products being identical [cite: 3, 4, 21].

To capture this, Colton argued that a generative system must demonstrably extend three "legs" of a tripod:
1. Skill: The system must possess the technical domain competence to produce the artifact. In a poetry generator, this means understanding metric scansion, syllable counts, and rhyming dictionaries.
2. Appreciation: The system must be able to evaluate its own work and recognize value. It cannot simply spew random permutations; it must have a fitness function or a selective filter that allows it to appreciate why one output is better than another.
3. Imagination: The system must be capable of generating material that is distinct from its Inspiring Set. It must synthesize new concepts rather than merely retrieving stored templates [cite: 20, 21, 29].

If a system lacks any of these three behaviors, the tripod falls, and the system cannot be considered genuinely creative. While philosophically compelling, the Tripod lacked the quantifiable rigor that computer scientists required. As Oliver Bown noted in his standing critique, Colton provided no specific, universally applicable definitions for these three terms, meaning that researchers could simply make impressionistic arguments that their system was skillful or imaginative without providing reproducible, falsifiable evidence [cite: 20].

## The Evolution of the Evaluated Generative Systems
To understand the practical application of these frameworks, it is necessary to examine the specific generative systems built during this era. These systems were primarily symbolic, rule-based expert systems operating in highly constrained domains, a stark contrast to the statistical neural networks of today.

### WASP (Wishful Automatic Spanish Poet)
WASP is one of the most historically significant generative systems in the field of computational poetry. Developed by Pablo Gervas, WASP was designed to tackle the complex linguistic constraints of formal Spanish poetry [cite: 7, 8]. Unlike English poetry, which relies heavily on stress patterns, traditional Spanish poetry requires strict adherence to syllable counting and complex phonetic rules like synaloepha (the merging of adjacent vowels into a single syllable) [cite: 9, 27].

WASP operated using a classic "generate-and-test" architecture implemented in logic programming. The system would take a prose message provided by a user, break it down using a Spanish morphological analyzer, and attempt to map the vocabulary onto a predefined metrical template, such as a sonnet or a quatrain [cite: 7, 32]. WASP utilized backward and forward reasoning to search a highly constrained conceptual space, iterating over drafts until the syllabic and rhyming constraints were met. 

When Pereira et al. (2005) evaluated WASP using Ritchie's criteria, they sought to prove that WASP was not merely a rigid template-filler, but a creative agent capable of producing typical and valuable novel verse [cite: 5, 33]. However, because WASP relied on specific early versions of natural language processing lexicons and hard-coded Prolog rules that are no longer maintained or publicly available, the exact state of the system during that 2005 evaluation is permanently lost. 

Later, the core metric scansion logic of WASP was salvaged and re-implemented as a module within PoeTryMe, a multilingual poetry generation platform developed by Goncalo Oliveira [cite: 9, 11]. While PoeTryMe represents the spiritual successor to WASP and remains a live, versatile platform for exploring computational poetry, it operates on a modernized architecture. It uses semantic networks, web APIs, and updated linguistic resources, meaning it cannot serve as a faithful bit-for-bit reproduction of the original WASP experiments [cite: 10, 34].

### JAPE and STANDUP
While WASP focused on poetry, Graeme Ritchie initially developed his empirical criteria with a different domain in mind: computational humor. Ritchie and Kim Binsted developed JAPE (Joke Analysis and Production Engine) in the mid-1990s [cite: 5, 35]. JAPE was a symbolic rule-based system designed to generate punning riddles. It utilized a large, general-purpose lexicon (an early version of WordNet) and applied schemas, description rules, and templates to construct puns [cite: 5, 36]. 

JAPE's success led to the development of STANDUP (System To Augment Non-speakers' Dialogue Using Puns), an interactive riddle builder designed to help children with complex communication needs play with language [cite: 5, 36, 37]. Ritchie frequently used JAPE and STANDUP as conceptual testbeds for his creativity evaluation theories [cite: 35, 37, 38]. He argued that any general theory of computational creativity must be able to account for the generation of humor, as humor requires a delicate balance of typicality (setup) and unexpected value (punchline) [cite: 35, 39]. However, just as with WASP, the application of Ritchie's criteria to JAPE relied on the authors' manual configurations of the Inspiring Set and subjective thresholds, preventing strict algorithmic reproduction today.

## The Methodological Shift in Modern Evaluation
The irreproducibility of the historical evaluations conducted on WASP and JAPE is not merely a failure of archival data retention; it represents a fundamental methodological shift in the scientific community. The standing critique of Ritchie's Criteria and Colton's Tripod forced the field of Computational Creativity to abandon the dream of a universal, objective mathematical formula for creativity.

### From Product to Process and Interaction
Researchers realized that attempting to isolate the "Product" (the generated artifact) from the "Process" (how it was generated), the "Person" (the computational agent), and the "Press" (the cultural context) was a flawed endeavor [cite: 18, 21]. A poem generated by a computer does not exist in a vacuum; its perceived creativity is inextricably linked to human interpretation [cite: 22].

This realization led to the development of more holistic, descriptive frameworks. Colton, recognizing the limitations of his own Tripod, collaborated with Alison Pease to develop the FACE and IDEA models [cite: 4, 40]. Rather than demanding a binary verdict of "creative" or "not creative," the FACE model allows developers to describe the creative acts performed by their software in terms of specific generative acts: Framing, Aesthetics, Concepts, and Expressions [cite: 4]. Similarly, Anna Jordanous developed the SPECS framework (Standardised Procedure for Evaluating Creative Systems), which explicitly requires developers to define what creativity means within their specific domain before attempting to evaluate it [cite: 41, 42].

Furthermore, the community shifted toward evaluating systems based on their capacity for co-creativity. Instead of viewing the computer as an autonomous solitary genius, modern systems are evaluated as collaborative partners. Metrics such as "Ease of writing," "Collaboration," and "Outcome satisfaction" are now used in human-computer interaction studies to determine the practical value of a generative tool [cite: 10, 16]. 

### The Rise of LLM-as-a-Judge and SciFi-100
Today, the symbolic expert systems of the early 2000s have been almost entirely eclipsed by Large Language Models (LLMs) based on transformer architectures. These models, trained on vast swaths of human text, are capable of generating highly fluent poetry, narratives, and humor without the need for hard-coded metrical rules or rigid logic programming [cite: 22, 27, 43]. 

Evaluating the creativity of an LLM requires entirely new benchmarks, which brings us to the closest live substitute for the historical WASP evaluations: the SciFi-100 dataset [cite: 23, 25]. 

Because modern LLMs can easily mimic typicality, the challenge has shifted to preventing homogenization—the tendency of statistical models to regress to the mean and produce bland, highly probable text [cite: 24, 26]. The SciFi-100 framework addresses this by implementing a "Blind Peer Review" system. Instead of applying arbitrary mathematical thresholds to single artifacts, SciFi-100 sets up a multi-agent environment where LLMs evaluate each other's drafts [cite: 24, 28]. 

This framework solves the primary reproducibility bottlenecks of the Ritchie era. First, the "Inspiring Set" is replaced by a standardized, version-controlled corpus of canonical science fiction literature [cite: 23, 25]. Second, the subjective human aesthetic judgment required by Ritchie's "Value" mapping is operationalized through carefully engineered LLM-as-a-judge prompts, which provide consistent, repeatable scoring [cite: 23, 25, 26]. While human preference alignment is still measured to ensure the LLM judge is accurate, the actual evaluation pipeline can be run automatically by a programmer, ensuring strict computational reproducibility [cite: 24, 26]. 

While the SciFi-100 benchmark evaluates semantic novelty in science fiction rather than the exact syllabic scansion of Spanish sonnets, it represents the modern, honest evolution of what Ritchie and Colton originally attempted to build: a rigorous, scientifically valid framework for proving that a machine can transcend rote generation and achieve something resembling true creativity. 

In conclusion, the specific historical application of Ritchie's criteria to the WASP generative system is lost to time, broken by vanished code, un-computable parameters, and the subjective whims of historical human evaluators. It is strictly irreproducible. However, the legacy of that failure paved the way for modern, reproducible evaluation standards that rely on multi-agent peer review and standardized canonical datasets, representing a massive leap forward in the scientific measurement of artificial creativity.

**Sources:**
1. [elsevierpure.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjU0kvm4HbkTX5s8012gwGRPXjfpgaX-KxwKLOEBgQNWdqq9A06y0oBb_V_h3HhkbC-weJtqaKFHiqnjjJMpQ6S4EN1KeTmBJY9NDakYPPkLnQStu6JqBQloCNUeZJvkkbtwt8crHnr1XaJoCGIccHnkq5VS_kT0lY_hvrRT62hFCy5hE8LkgAkoEfogTGld5DwJIUOX9BgN3HIOkImLuqh4q9AVFyx188m67jT4PGOCrBxQ==)
2. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbcFDIqCGeWRG5FDsmjG6UcmmZtdg0XznJDG63xwGNrVOq14Md1gRoHG93e5PB186KBPI9O_xTC2L70EwsvPMVrWzDNQqXrGAPrYAyUTWB5c8yyZju8LleRuk3YZEJA-EEVp7ucoLyZ5XuSq_1YqfLoQp_Sd3o6Egd1jbjJoG5J7vJqlLfGlckXLI8LcEJAw2hxrrsufUZa9f2qUrxypOwpRhZZEPAqEIlvKnT2tsHshyYN5epgvOyiz5Xn4ocWV8=)
3. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4ismyEHD5AS2C9ddY1gGI_eQldKmZ01YeKDmP0tu-YDEYdMO_cOGOezZ_Tp70ZonyaLr9T75VHAAL3viJG6qKWXkmyyf6ZxHHXl2w9NB4hnchjsJJzHYIOCsPnDC_qxhCbF1qfTKApwowIHy-As654OxA8sO-fjs=)
4. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGiJGkqrKuYZpS9Tb2wRX49VJtJgFGQUMQM78QE8OkT3aPn2tPgGRPZq82YT64Nbec-EcJXR-q8PA9N9KefbkF9p64BndcdcEhcnZK64BJrvYSEZ6875j8eNyDorJfBg43a-iHSq2L8)
5. [computationalcreativity.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGI_siFh9dTHEx6fi0VA7WEaCY54H4PpXTNDzWlmEuBTfz9j24_GGWwLuJJGpBVqKd8dv1jRsaV8_vjT87y9wu5lGmgGbSJbGglJ_cIjSdwkmjNzexhf-Jt5vStGZKxU-w00NsiVIEyWasJ1xa4eeaKLAF3OxwfE0kaXw==)
6. [google.com.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_OUN_gV3KibLU-s61fGxLbCjdzuI5dh-6zFxHGDXrxr620PzI-xPf-x-2BoUlF_68LuNbuCdXK_Ol95nTy5v4oPsfYXOebCD229NaBSa1zsHgM2W4c7NajrBIhSgAFBY3ryesmSN42SBiejGvlk5PKC2sRE8=)
7. [doi.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-dATWmuzV42AdbT-cbx0GDCeRR5jGneM_ox6khAETrgr16rVXQE248i2if1jdwadSK377h2GzIDNrnn98uUgil4cjOyYzA4i7hUvwdoxtvBEw8YvcroSsc6LWGCs0)
8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTRqStN_3i1e6tJ9OHJ5o0pESRxRVxV7nLbDrMKvT7HO1cTd_gZYOQIQptxw51Jf_AjcTYAfkng9JzIohxQukM6CMvdAb6gnpvknU6DY5wm9sbebgYVuC0U10ojrNmgw7E64fMna9Hl6kmUpEG3SmwB3OP__IrXyAebl_EWlaPDjZ4epgiAK8DsuY2DrlBJua0LDqBvA==)
9. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH70ne-hhVnSlVSYOuNSlW_pjZg3PXQJOhSLbJDPrbnOX2i0qHgO3IzfLRdx3uK7KYXpYvpUFYfFEe3RRxjsSxLTjkrONMdyN-eU-0RWC--fOblvLiSStRc354a6PRJXifQ-ZCmrvMQwsSkwUGWk_nzVE0A6g-zwRAg8IIXAmH45H7NBc3-XJHl5M_Wd9C1SLQEoxsox_nVSwkHxFxfD0TNOyJCF7-tzKnnLI6-OzqRWqFMC2iQvVTEQ_gNmxs0p4MWH5HNIx0oPMn79WEnTanJ6ytTTx02ie5bcraMUHAxSg==)
10. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG__98oOKo6aqCzqa3LGaOPbV6e6criA-Zsd90w4xB_h3KUhRxuAG4LCFeuY8eg_BBPR7zegaz8oiwulwc3xZV4yOV2q7BRAaGLkgSOvDyIzJVVAZShwKzbXF82FBGhBy03YOkm1UGYaRTKXFn9Q-j2ZBWYtYifoABtMfwgsCX__r-ZXePLY7Lx)
11. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxTzY0M_zXU5L-3HxXuKSKp-VbJz1mdPy7KcEn3mHugmAQpgPtMvpuuSQNsKSkBhRLmzQekBMheATeaMhmWn6qK7iI-4SxJtiC-BrNVCMGQ-fJtGNKA8UmtjlEsUi_vfdktGvGabhioB6XOs5lXoP5X5vwIGR5nGD1GyTAhU3xdsQguhtjtE2hAIt65SQhRThFsiv4TWXz9OqzUK4F5Bm04ToaTUyJ9G9YBdLVSSCay1KJceEtuz2SV7gh)
12. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7TiGk_GufHAxxjp4b710NF2CNoA4vbFY2qzl0Kk-UZspu2uh5t-P-A6hKgu2UDjSe80C07SBd0RMFxijqXsnugdS472qGVXTheb07TNSQK5GW_Uac5lm37C8cdOtZF1N3GCx-9BTyMLJofiE1veZSI9wFQaacJyCduma4aoCvlGpSuAr1i-7FVAoBihhCc6347A==)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH94dnK8-K7HghsNHlA0pVsG1oFZuySk4jQOIu-n_VF0-wRabtAh9HVHUOt2djNAzfaL93PfxVEostEacrOzFMSZaIneRE-xljhg4WT-dBPLvG7A7LDDLddJKFQ6GzPBYqWb1-j7icYAh0ro0lg3PN_v0Q2BoSIV5Fh_sxnqcyThBgZp4t74LpUP3HeAPiXWAIETXHcgVqH7MfU40wzRdDNP6ybna2PFPd9tRRhWlLVn-7ThXDhRS1IA3Wm-ojHQA==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExlwhh4jgsc9V4RGscJmqak1c30Qm4Ztl8V1J1DQO_sX3TbHg96xZRqKyMqud_nQq3dbT3hYWIcV7O1vegZqTj9jXdZkYgeE7RLT8VF_D2YdxBRsUiRw==)
15. [aisb.org.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJCdDHUUs6nuMqjBweV3wIqkzaDPC1Wr5w2m3WutyEPkDgEPHggs-Gr-CMS7Ue6TY8LdOnTdVjgrYnws7TL-p8MJEfynpKJrfCNEwtDktkg8GZYvH3QOlyPviSA4vwMeMvfXjSXocgQkOkZZmh2ekHfIwnNgI=)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXG6ojH1wm0LyXf4EzwIJsEth62-HCwVne4HXOESCapP6lOyoEhIbRfRUXYn9m7LVJLz-2Uqqs0HMpOthuHN107N5tpGVpZgx_JimyQamMhQ0C8wI1WywM67LlFSmLjf-s_h6qvrlI6ICgsdab70LFOhWByHdD4ffr1ac=)
17. [helsinki.fi](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjTO1KZAj7pH8PQ4BHdv7mrx1FBziQxIUeDOFQWxabsA8MLIy5m9Dvc5ChuxfD4_DBg2ZB9bCq4aTNTPF2O2mikFM04CNZFn_JoVQ51qvqJrniQQEwa8FN4L30PhCuN3Y1o3nMyOxqiuOsBsewmliI66IiQDjKHEwsq_VKLbNZOj8lOK81X8rK)
18. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6LnmAOG-FgkbC3onX9c0qI3RTw26l88wv4ULyF6nRRtJjH0SRBrh9VuZhd0vwFw4Y1bKnZM01pgH209HxTTQQ8SlLCXbJ8k7U3elcgxzkuGb3kZ9M-JkEpLK2pOnVfmBD1NEPh1D-bNmeVDL7rA-s3B07Je-AsKw2f2HNHqYBEKm7eRFcq8Yfr8827v8aVN_rq8Cgmho=)
19. [dokumen.pub](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFd76gFOsxyiuO5KNgIK0fkMW3gFNrz7oNEtKOitzwAiAQo6HAW7EbkIVWOWpJrfUJR6hV_3bfXu8x4DKAQcbXQAg4IZ5JQBxy08FOdBvGR7pMqiuDSxrKAwKm4AqAJORkaQ_zRF47OvBwGgnTjY2UE5ao__h1DeKaftIL8etqp9M7Meyp2f_Jm74eTyilk9cGcKlHsqTseWkWfbbNBXEO2ZhmtTu5sRVc0IjbdK5O7dii2P-CLeGM=)
20. [computationalcreativity.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7lCpoSy3hU7w-iL_Zuj5ZqQInSQDCKbpjh5f76pFmP2jxpizNExQWn-mrW35O04vtQPvER01hakmYxdQLn05VfliyQWQh6KVajbzrw8EzBMTc0E-oeJjEqOS8dIWcZuj1cpT-7I_-1NU_S29UzVz9axLMo2KMAb5vcQ==)
21. [kent.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcipaGIkqM3_PhXGLSSO4ibspfGn3s4Ekvj7JQPv05ZL0Qm-3Y7TSm0YY3wxolO-DUMVUZgHO_UJUau_Kuu-uXD8758HCVdksnDQ1bwQy_n4kiYvVXDuLVV02tyGRW)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzFtobsdbcGSKVH3MUQC7JdzC1jRaIf4Dy0FSvv_7N5BgntgLPB3LSjyZ_SuH1ql1BrGkig-KvE8A_ZbRLBBqElxufUtMcVA6Ky5pI_TmED1JByegZn9Ht1e1M5Lgvu_tv_EumsKdgb6CQR7OA-1DOqx1L_DeqK-iL2wnWGb0PKdMXle7GqiW7GN-1SZBCxFAm_npTM5GLXG7hOQMs54o7DuYnj0IrqhjwyU5kTnEFFdY=)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFs18me4sq1bbtjx7HJN_wxmLBdM7Se6YbUDOIgwsgf3xuI5RJaEXEdrnAH6eoYA7k_Px_pT5Pp8yerxcV3yL1IB4J2J3YCysIJCX3fHCshQz6qYUWYYQ==)
24. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcpldZWTCncDvIeO7mCN9hutESTJ_sYhH2cB6pbmpw52oaat76LnJzwyHxAV0uvGfhN6t3a-cdx1iUwbQqzUqa3_67EZWVYBzULxLldXpwZ4YBSLYpcYl5fqjaxvdK-rg=)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENuWrZYI1wHlstJS0RXdlObVt259bxQdbqPhvk6ceIfRQ02bjHEvBipQe7dwuMCsMJWw0ydmMlzg3C6J__PATsAl9p6MLLKB1uTuxIOlcrR5HuYEAFwpxRaA==)
26. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElwsX3zry2rje-H7yowN7EEuvTjbL0_2zZym2LitOXPHAzzhWYpU84_RfFIhp-qhDvz4RXwJrTmuOgVjoR-Ly1tdzho25zIkWulbipKdMQRRBvTrHmqHq8xA==)
27. [computationalcreativity.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyEeolcJR67_Su3BvsWhGUcu07i5oc-tt36F8wU6BbzPMGTiSeD51PanwL1r4wFu2ULTNepo9iQEo8UL7HZuhdF3iFsTw5-fU8wfI97o_HvDbVp45vEz9wDukQ4hIqJQz0_RMSmjSvJOGMXGklYu5ByCgBFjM6jfaS3ANbWEvRn9VsJcF4rqfB_wyF)
28. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH4FT3aCYRwD-U2AGChAJLauKrlNYLFlwKLdfrEQ4aNEgvP3fN9NWwT3L1UOPBNPWXcNCH7BybncGsCRoiMsiWlMYBtl5rCL6oiqaxz3lNUvCTG)
29. [jcms.org.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnIBz1N1tarawYL3dEPib1BTa3EOXd5A0J2ZXl5xlPUUVNglxkZne_-yoF6Kgv8Qg-QwRTwimmLHgh10UVHZPZEneKtLV-ZzMOAN_-kDBtHQvZLmTY6Al-6ZaodsKf1NeFCltLPe35r3YKdkT6)
30. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgcia3UVqv7mu8rofb7g7Nu-7VdPe30iGGD6GdkxUiNDNk6wTrfL4lrThPLQpIs6-G-UbIOrjEww07YGVu72lUV7kcDl5uNfU4ZzVF7Zt7GHu1WWk52AWdlLWLPdH2E9ZW5q2_nLV845sauPO_DOOc5_SMLRgGAg==)
31. [womenintechpk.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGU6P36VWf16QtDtUNIu__DiIScVzYb6nFZ7H8B2uW8jDfAL-J0sMmkZQtqIUKKKizbuzBDu-yrzPvKdnEQ5u1n-FqbIg0jWMI9aPLpOnX3-mhJhYfbLlWfSp4zxtgXP3f70uDZaDB)
32. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFufhVjXkA1xnaCnKJdRpz8uSP9csJcJlbQoYycwuTnnU-Oelv6Ctt2TuSPKoaxW0i3_55OtYJg1SjHspEsmCc9LJF3zDrrUoqZ_eBulFNSGoWwmZbR4HOy-Q04QjRQiyXjPVUV3SrL3Pu1UYaKniE7ogQUJBAkaiEB02mxc3_lNXO35mIh1cuJrIY7GNtarWuylWijWaOEpSEvdQ-itU5MmY0XATUKlgy9pCBirGHV-LJvmofr2vMNBVXYkpFeQdoyYvl2Rahx)
33. [agh.edu.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6bdRG03saXr2bTFFb_EnwNfGmLKXm5W49oC3vOAvT9s14WWXtWIvSQCiTGHVf4WnJJ9UlCBvz2I9DvobhfMKSH49JT663NLTtGn6WfAAyQWFbZhWgTaJXnY2TOAVPHHWlRf7W2z8ETg==)
34. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-J_63ythL3OaWgdP25G9Tuf7qsjlo6UGuNNKaLNegiZ7CKzhO-5Dk4P_1Qz_1eN4hTkj966tgndljDW7Ldddt3StSUP6OlPBdjWDSgq5hzzh1N-xJrqO9GooMtHjsQakidzLiWunPWKgVr3x-ChK3w3OIoOzSufUUHGVnko2IhZKU97wmIyGrHZZfGTkKZTUMteMlZP736WCw0VNu8Zt9T0vZMnxB1GlH5PJr4xdBdwpO-DUqWNQe18LdWWyxdg==)
35. [academia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgfSnPf0az8v1VznODg5GXVKkJziMZT2YJlKeibAvU-_bWvF9ua9RuRdtzpv5KBEy8ErndHncw7N9SfyEdl-Ol18_JNSO8P7z-olXrrNSH0OrZyyVYqap3PEY6AdsUP_PL5sW_mdIHmHXXBQthMMr2nCg=)
36. [abdn.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVfkyR4APt0XhK9wsa9vsGTgfvdQpYdXSvBw1LAl6Cc-HdZ3gG3sVqpzggQ0_GCU83uh7yP0o45-JcQS_rgvTWf8BwNF1jd8h8uSUys1byJsP1f49_wf9yK6z9xNhrO7YMab1PRrhnaWMfGwO3M_C6jPduPw==)
37. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFCqO2_RLC5ScejpRKWDxkRmHEKayfIdwo7pTxh17hBcie9-p4nvIWZprBvvhEFUuRuiDbiiil9GapWk4a2_1rG2igYcpt4JoXxz3mSztDMdwxNYHTXNrHtqjXL3AsCzJuDMEB2jauZMbqp-MYPJdD_mwo=)
38. [byu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCfS7pfX5lOMusnPVZvGO3VzNKmEm_gnUa1MJ02wIkDlVJdiiGT8qJtSQ57MqJElYHR6FsyinUonpDnhqvd6lvzAsV1-6U1M8Z2M2nYNssg3TLiIukK3nIZa-A0g2hmxA-RT_lCsBOKOSPMFyQglrrSfS7vwoibyFsV0TBVUyZlDS3WQ==)
39. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqrrsjHrZsdvubkuYeHQqK2mJfiWaaJ5quc_-B-2tDyS-y4-OGQRULEFllzcjGQy6qAgXR6nNafQNEEKS9DC1TNhrWvApkBh_TtVfxTACY8cYwRdj5KJ7FO1Plc1s6OPLA_tOW93dPjNXfDtm8Yhrkb6Gem97RMdmyis8keGlSS50_lQ==)
40. [kent.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBAydXYwNPIk_uXM1kLw2thX939_qcMjmkSjRBTc2Pn2zpjNmD6b6aDzqsk1pCFH5Pnw9ifru0frNxYgRrjPIM_3VjuST3xeIplTdAc428M1J69Ek1odfE9K6Ipr3-viM=)
41. [computationalcreativity.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-pa1nDO3V4oVv_sMr6j3jX2VZDIjY_kcFV5ZGh8w5vW70TOXNGLeNVoJH3zSgyGnhCx3Nd-e22VgGVjpDFRJzVvL_LvqP7dtF8sdYdZ9UHttOQuVR8I79eh9afOcs7Fp5Ba9i-1Jc_I76huT93FEzesu-vOw-)
42. [openbookpublishers.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJAlJVKOIGGTLKMO_S27z63hAXFNb4aQmQdLKKsmLRFW4IlDsiDa16Up9wBn9pI935MEe0D-MJsgs7pf6esLkmpwThVuqsHCAyYi7VXh1yEEoks4GOf6eTC32mIJa2uZxqEO5PncmU1nTFwgTfdzl1rg3V9gO4kjY5st6YLg==)
43. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwImLKoPQUAPVCs7bAj7yViUniJt6BGzIQCvHV2pgsbDSdBouC5zxQ5tDxCQk56UWnCKNwoS6Y5D6lLj3SBXseKLhPfcgQVK22HcgarSB1PSYSIqzXvay-Kg==)

