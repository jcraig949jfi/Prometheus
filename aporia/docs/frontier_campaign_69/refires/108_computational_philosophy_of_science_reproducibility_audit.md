# Prompt 108: Computational Philosophy of Science reproducibility audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdkTGlmYXFHMEJPcXQtOFlQcU92WW9RYxIXZExpZmFxRzBCT3F0LThZUHFPdllvUWM
**Elapsed:** 334s

---

REPRODUCIBLE

PART 1. VERDICT, IN THE FIRST LINE
The verdict is REPRODUCIBLE. The original source code survives and is publicly available, it can be run on modern systems with minor documented modifications to legacy paths, and exact numerical activation values from the original publications are available to check the reproduction against.

PART 2. THE ARTEFACT TRAIL
Original source code for ECHO, written in Common Lisp, has survived and remains accessible online. Paul Thagard integrated ECHO and several related coherence models into a unified framework known as COHERE, which was documented in his "2000" book Coherence in Thought and Action. The original Lisp files for this framework, including echo.lisp, cohere-start.lisp, variables.lisp, utilities.lisp, and network.lisp, are hosted on Thagard's University of Waterloo website at the bare URL http://cogsci.uwaterloo.ca/CoherenceCode/COHERE/COHERE.instructions.html cite: 36, 71.

In addition to the official host, the original Lisp files have been preserved and modified in a few GitHub repositories. Marshall Abrams created POPCO, an agent-based simulation framework incorporating Thagard's ECHO code. This repository is available at the bare URL https://github.com/mars0i/popco and contains the original echo.lisp files with a commit history dating back "13 to 14 years" ago cite: 1, 35.

Multiple modern reimplementations also exist. Toby Donaldson implemented JavaECHO as a Java applet around "1997 to 2001". The original source code for JavaECHO was hosted at the bare URL http://cogsci.uwaterloo.ca/JavaECHO/jecho.html cite: 9, 61, 62. Because Java applets pose security risks in modern browsers, this codebase was later archived and adapted. A developer named Russell Cameron Thomas updated Donaldson's JavaECHO, stripping out the graphical user interface to create a command-line version that runs on modern Java architectures. This faithful reimplementation is available at the bare URL https://github.com/russellcameronthomas/JavaECHO_command_line cite: 61, 62. Another repository archiving the Java applet code exists at the bare URL https://github.com/tjd/echo cite: 62. Furthermore, a Python reimplementation used to solve Sudoku with connectionist constraints is available at the bare URL https://github.com/MaxRae/ConnectionistSudoku/blob/master/ECHOSudoku.ipynb cite: 62.

PART 3. THE PUBLISHED RESULT TO CHECK AGAINST
The defining publication for ECHO is Paul Thagard's "1989" article Explanatory Coherence in Behavioral and Brain Sciences, identifier DOI 10.1017/S0140525X00057046 cite: 66, 68. This paper documents several historical simulations, providing precise numerical activation values that a faithful reproduction must match. Activation values in the ECHO connectionist network range from a minimum of -1, indicating complete rejection, to a maximum of 1, indicating complete acceptance cite: 8, 11.

The most prominent result to check against is the Darwin simulation, which models Charles Darwin's argument for evolution against creationism. A successful reproduction must show the hypothesis unit representing evolution, labelled DH3, reaching a final asymptotic activation value of 0.921. In the same run, the competing creationist hypothesis unit, labelled CHI, must decline to a final activation of -0.491. Furthermore, the final activations for other units in the Darwin network must match the following exactly: DH4 at 0.446, E1 at 0.688, DHZ at 0.922, DAG at 0.446, and units E15, ES, E12, E10, and E13 all settling at 0.738 cite: 51, 88.

A secondary target is the Lavoisier simulation, modeling the oxygen theory of combustion against the phlogiston theory. In this simulation, the reproduction must yield final activation values rounded to three decimal places as follows: OH3 at 0.840, OHZ at 0.435, EI at 0.702, PHI at -0.736, and ONL at 0.731 cite: 51.

PART 4. WHAT WOULD BREAK A REPRODUCTION
A reproduction attempt would be broken by failing to configure the Lisp environment properly, failing to manually edit the initialization scripts, or altering the delicate mathematical parameters.

First, the original Lisp code has unmaintained dependencies on legacy Macintosh Common LISP environments. To run it on a modern Common Lisp system like Steel Bank Common Lisp, the user must manually edit the cohere-start.lisp file. Specifically, the programmer must replace the hardcoded path Sanders HD with their local hard drive name and folder path. If not using Macintosh Common LISP, the user must explicitly delete the graphics file references and the function calls to start-graph, as well as the calls to resect-act in the input files. Without these manual code deletions, the reproduction will crash during initialization cite: 36, 71.

Second, reproduction would break if the specific parameters governing the connectionist network were left to arbitrary defaults rather than the exact values published in the "1989" runs. The deterministic mathematical settling of the network depends entirely on the following hand-tuned parameters: excitation at 0.05, inhibition at -0.2, data excitation at 0.1, decay or skepticism at 0.05, simplicity impact at 1, and analogy impact at 1 cite: 79. A tolerance parameter of 0.25 is derived from the inhibition weight. Altering any of these weights will change the activation dynamics and break the reproduction of the published numbers.

Finally, the most severe methodological dependency is that the evaluation of theories in ECHO relies fundamentally on the author's own judgement and interpretation of historical texts. The model does not read text or autonomously discover laws; rather, the inputs to ECHO are propositional structures, explanation statements, and contradiction statements painstakingly hand-coded by the programmer. If a reproducer attempted to rebuild the network from the raw historical text rather than using Thagard's exact Lisp input files, the reproduction would fail, as the structure of the constraint network is a direct product of human hand-holding and interpretation cite: 52.

PART 5. THE STANDING CRITIQUE OF THE ORIGINAL RESULT
The ECHO model faced intense and decisive criticism shortly after its publication, primarily focused on its psychological plausibility, its computational necessity, and the arbitrariness of its representations.

The philosopher Clark Glymour was one of ECHO's most caustic critics. In "1992", Glymour argued that the system was effectively a dog and pony show where the desired historical outcome was manually encoded into the network by the programmer. Glymour pointed out that ECHO begs the question of what an explanation actually is, because the programmer explicitly feeds the system assertions like P explains Q. He stated there was neither empirical nor historical evidence for Thagard's assumption that human theory comparison utilizes two distinct cognitive modules: one for judging what explains what, and another for computing the coherence of those propositions cite: 57, 84. Glymour concluded that ECHO lacked psychological plausibility and that the complex connectionist constraint satisfaction algorithm was an unnecessary facade for basic human curation cite: 57, 84.

This critique of unnecessary computational complexity was formally demonstrated by Gerard Vreeswijk. Vreeswijk argued that ECHO's non-transparent updating process intermingled explanatory success and simplicity in a way that obscured the actual reasoning. He proved that the exact same products of theory selection used in Thagard's historical case studies, including the Copernicus and Lavoisier simulations, could be replicated by hand in forty-five minutes using a vastly simpler Priority of Explanatory Coherence principle and a basic comparative Evaluation Matrix. Vreeswijk's work demonstrated that the heavy machinery of a neural network was entirely superfluous for achieving the published results cite: 72.

Paul Thagard himself acknowledged some of these vulnerabilities in the original publications, noting that a major limitation of ECHO was that the inputs were constructed by the programmer rather than automated, and that by basing the analyses on texts, the model might just be capturing the rhetoric of the scientists rather than their actual cognitive processes cite: 52.

PART 6. IF IT CANNOT BE REPRODUCED, WHAT IS THE NEAREST HONEST THING
Because PART 1 was a REPRODUCIBLE verdict, I am providing the exact reproduction recipe for the original system.

Exact software: The original Common Lisp implementation of ECHO, downloaded from the bare URL http://cogsci.uwaterloo.ca/CoherenceCode/COHERE/COHERE.instructions.html cite: 36. The code must be run in a modern Lisp compiler like SBCL, after manually removing the Macintosh graphics calls in cohere-start.lisp and updating the local directory paths cite: 71.
Parameters: To replicate the primary "1989" historical simulations, the network weights must be set as follows: excitation 0.05, inhibition -0.2, data excitation 0.1, decay 0.05, simplicity impact 1, and analogy impact 1 cite: 79.
Replicate count: 1 run is sufficient. Because the network settling process is deterministic given a fixed network topology and parameters, multiple runs will yield identical activation values.
Compute cost: Near zero. The model represents a tiny constraint satisfaction network that settles in under 100 cycles of activation adjustment cite: 28, 40. This requires fractions of a second on any modern processor.
Number to compare against: The final asymptotic activation of the DH3 unit representing Darwin's species evolution hypothesis must reach exactly 0.921, and the CHI unit representing creationism must reach exactly -0.491 cite: 51, 88.
