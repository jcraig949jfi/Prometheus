# Prompt 102: Computational Models of Scientific Discovery reproducibility audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdiYmFmYXM3YkQ3VFFfdU1QdW9tVXdBcxIXYmJhZmFzN2JEN1RRX3VNUHVvbVV3QXM
**Elapsed:** 334s

---

NOT_REPRODUCIBLE

PART 1. VERDICT, IN THE FIRST LINE

NOT_REPRODUCIBLE

While the underlying algorithms of the BACON system have been successfully reconstructed in modern programming languages, the original system itself is not reproducible in the strict sense required by this audit. A faithful reimplementation of the heuristic search process can be built and run on current hardware, but the original publications by Pat Langley, Herbert Simon, Gary Bradshaw, and Jan Zytkow report no aggregate quantitative number, benchmark score, or statistical accuracy metric against which a reproduction could be definitively checked. The original evaluations were qualitative, boolean claims of success on hand-selected, highly curated data tables. Because reproducing a scientific system requires an objective empirical target to match, the absence of a published evaluation metric renders the original historical result irreproducible.

PART 2. THE ARTEFACT TRAIL

The original source code for BACON and its sister programs GLAUBER, STAHL, and DALTON is lost to the public domain and is not available in any standard open repository. The system was developed in the late 1970s and 1980s at Carnegie Mellon University and the University of California, Irvine. The original codebase was implemented in PRISM, a specialized production system language designed to model cognitive learning phenomena, which was itself written in LISP. The PRISM user manual, authored by Langley and Neches in 1981, survives as a technical report, but the LISP source code for BACON.1 through BACON.7 is unconfirmed to exist outside of inaccessible physical university archives or personal backups.

Despite the loss of the original LISP artefacts, several reimplementations have been created based on the detailed algorithmic descriptions provided in the 1987 MIT Press book Scientific Discovery: Computational Explorations of the Creative Processes. 

The two most notable surviving reimplementations are:

First, a Prolog-based reconstruction named bacon-logtalk, authored by Lindsey Spratt in the 1990s as MacProlog32 and later ported to Logtalk. This codebase survives at https://github.com/lindseyspratt/bacon-logtalk. The author claims it is an attempt at a faithful reconstruction based solely on reading the 1987 book, but explicitly notes that the system is chaotically sensitive to tolerance parameters and fails to reproduce the Ideal Gas Law.

Second, a modern Python-based reimplementation authored by Jonah Miller and Soumya Banerjee, published in late 2024. Their project, titled The BACON system for equation discovery from scientific data: Reconciling classical artificial intelligence with modern machine learning approaches, rebuilds the heuristics of BACON.1 through BACON.7. Their source code is available at https://github.com/JonahMiller/BACON, and the accompanying paper can be found under DOI 10.31219/OSF.IO/Z8KQV. This modern version claims faithfulness to the original algorithms while adding modern noise-handling wrappers like Monte Carlo Tree Search.

PART 3. THE PUBLISHED RESULT TO CHECK AGAINST

The original publications, including Langley's 1981 paper Data-Driven Discovery of Physical Laws and the 1987 book Scientific Discovery, claim that the BACON programs rediscovered a specific suite of historical scientific laws and generated new theoretical concepts from raw data.

The specific claims of boolean success include the rediscovery of Kepler's third law of planetary motion, Boyle's law, Galileo's law of uniform acceleration, Ohm's law for electric circuits, Black's law of specific heat, Snell's law of refraction, the Gay-Lussac law of gaseous chemical reactions, and aspects of Dalton's law of chemical proportions. In the process of these rediscoveries, the system is claimed to have autonomously generated the concepts of inertial mass, specific heat, refractive index, atomic weight, and molecular weight, while formulating conservation laws for momentum and heat.

However, the original papers report no number a reproduction could be checked against. There is no reported mean squared error, no classification accuracy, no replicate count, and no aggregate success rate over a standardized dataset. The results were presented entirely as anecdotal case studies demonstrating that the system could traverse a specific search space to find a specific algebraic relation when fed a specific, noiseless data table. For example, the Ideal Gas Law discovery was demonstrated by feeding the system 27 perfectly noiseless values for volume, derived from 3 specific values each of pressure, mass, and temperature. Because the original authors did not publish a quantitative evaluation metric, there is no numerical target for a modern reproduction to match.

PART 4. WHAT WOULD BREAK A REPRODUCTION

A strict reproduction of the original BACON results would fail today due to four primary breaking points:

First, hand-tuned parameters never published. The BACON heuristics rely heavily on predefined error tolerances to decide when two variables are linearly related or when a ratio is constant. Reimplementations have revealed that the system is chaotically sensitive to these hyperparameters. Spratt's Logtalk reconstruction requires highly specific manual tuning of constant tolerance, linear tolerance, and proportional tolerance to function at all, and even then, it fails to find the Ideal Gas Law. The exact tolerance values used in the 1980s runs were largely omitted from the publications.

Second, datasets never released in raw form. The system's success depended on the data being fed in a highly structured manner. BACON requires data where one independent variable is varied while all others are held strictly constant, allowing it to calculate derivatives and constants layer by layer. The exact data matrices used by Langley and Simon were custom-crafted to satisfy this experimental design, effectively pre-solving the experimental control problem, and these exact tables were not preserved in a public dataset format.

Third, evaluation done by the authors' judgement rather than by a rule. As highlighted by Schaffer in 1990, the BACON system was evaluated by running it until it generated a desirable answer on hand-selected cases, and stopping. There was no objective function or automated test suite to determine if the system would also generate hundreds of spurious laws from the same data.

Fourth, dependencies on vanished languages. The original implementation relied on PRISM, a custom production system language that ran on LISP architectures. Without a functional PRISM interpreter and the exact LISP environment of the era, the cognitive architecture that dictated the order of rule-firing cannot be perfectly replicated.

PART 5. THE STANDING CRITIQUE OF THE ORIGINAL RESULT

The BACON system provoked significant and decisive criticism from philosophers of science, cognitive scientists, and artificial intelligence researchers in the years following its publication. The consensus of these critiques fundamentally undermines the claim that BACON models autonomous scientific discovery.

The most severe critique focused on hand-holding and variable representation. Researchers, including Chalmers, French, and Hofstadter in their work on high-level perception, argued that BACON's discoveries were trivial because the system bypassed the hardest part of science: choosing what to measure and how to represent it. Johannes Kepler spent 13 years sifting through chaotic data, discarding religious symbolism, Christian cosmology, and teleology before arriving at his third law. BACON, by contrast, was spoon-fed the exact dependent and independent variables required (mean distance and period) in an idealized format, with a built-in bias to seek standard algebraic polynomials. As critics noted, if Kepler had been handed a clean matrix of relevant variables and told to find a polynomial, he would have done it in an afternoon.

This critique was echoed by Sleeman et al. in 1989, who argued that quantitative law discovery systems are severely limited because human scientists must first design Informal Qualitative Models to even decide which variables to record. A separate critique in 2018 summarized that the data given to the algorithm was pre-processed by human operators so as to include only the relevant factors of the world, implicitly smuggling the human's scientific intuition into the machine's inputs.

Furthermore, Schaffer decisively challenged the empirical validity of the system in 1990. Schaffer pointed out that BACON and similar systems were supported only by anecdotal evidence on hand-selected artificial cases. Schaffer argued that without domain knowledge, such algorithms are liable to generate an incorrect or meaningless algebraic relation for every correct one, and that the authors had simply filtered out the failures. 

Finally, Gigerenzer and Goldstein argued that Simon and Langley's model of discovery was tool-driven rather than purely data-driven. They asserted that BACON's design simply projected the computational tools of the era onto the history of science, retroactively framing 17th-century physics as a heuristically guided database search. 

These critiques were largely accepted by the field, causing the community to shift away from pure heuristic search over pre-selected variables and toward systems that either heavily incorporate domain knowledge, dimensional analysis, or massive statistical robustness.

PART 6. IF IT CANNOT BE REPRODUCED, WHAT IS THE NEAREST HONEST THING

The closest live substitute to the original system is the modern Python reimplementation by Jonah Miller and Soumya Banerjee, located at https://github.com/JonahMiller/BACON. 

This substitute faithfully captures the heuristic layer of BACON.1 through BACON.7, successfully recreating the algorithmic steps used to discover the Ideal Gas Law and Kepler's laws. However, it explicitly does NOT capture the cognitive architecture of the original. Langley and Simon originally built BACON in PRISM because they intended it to be a psychological model of human working memory and rule-firing. Miller and Banerjee's version Abandons this cognitive science framing, treating the heuristics simply as a classical AI search algorithm written in Python. Furthermore, to make the system function on noisy data, the modern substitute wraps the historical heuristics in modern techniques like Monte Carlo Tree Search, which the original 1980s system entirely lacked.

If you are looking for a modern, production-grade system that solves the exact problem BACON attempted to solve (equation discovery from data), the nearest honest thing is PySR, developed by Cranmer et al. PySR uses deep neural networks and evolutionary algorithms to perform symbolic regression. What PySR does NOT capture is the step-by-step, explainable heuristic reasoning of BACON. PySR operates as a black-box optimizer that searches the space of equations statistically, completely discarding Langley's theory of scientific discovery as a logical, rule-based sequence of postulating intrinsic properties and testing symmetries.
