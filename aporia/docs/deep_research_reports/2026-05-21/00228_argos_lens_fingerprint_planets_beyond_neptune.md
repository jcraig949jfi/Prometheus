# Argos lens fingerprint: Planets beyond Neptune

**Pythia queue id:** 228
**Tier:** T5
**Priority:** 5
**Requested by:** Argos
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdlMU1QYW9UU0NjQ2cxTWtQcnVyNDZBRRIXZTFNUGFvVFNDY0NnMU1rUHJ1cjQ2QUU
**Elapsed:** 565s
**Completed at:** 2026-05-21T18:57:53.052095+00:00

---

# Primary-Literature Lens Fingerprint for Open Problem ASTRO-0001: Planets Beyond Neptune

**Key Points:**
* Research suggests that the anomalous orbital clustering of extreme Trans-Neptunian Objects (eTNOs) could be explained by a massive, undiscovered "Planet Nine," though alternative theories remain highly competitive.
* It seems likely that observational bias plays a significant role in telescopic surveys, prompting intense debate over whether the observed eTNO clustering is a physical reality or a statistical artifact.
* The evidence leans toward a complex interplay of gravitational dynamics, where collective gravity from a massive planetesimal disk could potentially mimic the signature of a single large planet.
* Advanced mathematical frameworks, including Bayesian pulsar timing arrays and Renormalization Group applications to Modified Newtonian Dynamics (MOND) and KAM theory, offer independent axes of verification that bypass traditional optical survey limitations.

**Overview of the Debate**
The outer Solar System remains one of the most enigmatic frontiers in modern astrophysics. Following the discovery of objects like Sedna and 2012 VP113, astronomers noticed a peculiar spatial alignment in their orbits. To explain this, the "Planet Nine" hypothesis was formalized, proposing a super-Earth residing deep in the outer Solar System. However, this remains a deeply debated topic. Some astronomers argue that the clustering is a mirage caused by the limited locations where telescopes can look. Others propose that the collective gravity of thousands of smaller icy bodies could naturally shape the outer Solar System without the need for a hidden planet. 

**Methodological Perspectives**
To rigorously evaluate this open problem (ASTRO-0001), the scientific community applies diverse analytical lenses. Dynamical Systems approaches use large-scale computer simulations to track gravitational interactions over billions of years. Information Theory and Bayesian Inference models calculate the statistical probability of these orbits and seek mass signatures through the exquisite timing of distant pulsars. Finally, Renormalization Group theories and advanced celestial mechanics explore the fundamental stability of orbits and test whether modifications to our understanding of gravity itself might account for the anomalies.

***

## Introduction to Open Problem ASTRO-0001

The architectural structure of the Solar System beyond the orbit of Neptune constitutes a primary frontier in planetary astrophysics. For decades, the Kuiper Belt and the broader trans-Neptunian region were understood to be populated primarily by icy remnants of the primordial solar nebula, their orbital properties sculpted by the early migration of the gas giants [cite: 1, 2]. However, the discovery of extreme Trans-Neptunian Objects (eTNOs)—bodies with highly eccentric orbits, large semi-major axes ($a > 250$ AU), and perihelia decoupled from the direct gravitational influence of Neptune ($q > 40$ AU)—has introduced a profound anomaly: a statistically significant clustering in their arguments of perihelion ($\omega$) and longitudes of the ascending node ($\Omega$) [cite: 3, 4]. 

This orbital confinement has catalyzed the formulation of Open Problem `ASTRO-0001`: Does this clustering necessitate the existence of a massive, undetected planetary body (colloquially termed "Planet Nine"), or can it be resolved through alternative mechanisms such as collective self-gravity, observational selection biases, or modifications to gravitational theory?

To systematically dissect `ASTRO-0001`, this report applies a multi-perspective methodology, mapping the primary-literature footprint of three distinct candidate lenses:
1. `STANCE_DYNAMICAL_SYSTEMS@v1`
2. `STANCE_INFORMATION_THEORY@v1`
3. `STANCE_RENORMALIZATION_GROUP@v1`

For each lens, we identify the two strongest primary-literature attempts, summarizing the projected measurements, the verdicts reached, and the axes of disagreement with competing paradigms.

***

## Lens 1: Dynamical Systems (`STANCE_DYNAMICAL_SYSTEMS@v1`)

The Dynamical Systems lens models the Solar System as a complex, chaotic $N$-body system governed by Hamiltonian mechanics, secular perturbation theory, and mean-motion resonances. It seeks to understand the long-term phase-space evolution of eTNOs over billions of years. Within this lens, two dominant but mutually exclusive primary-literature attempts have emerged.

### Attempt 1: The Planet Nine Hypothesis (Batygin & Brown)

The most prominent application of the Dynamical Systems lens is the Planet Nine hypothesis, primarily advanced by K. Batygin and M. E. Brown (2016). They utilized extensive $N$-body simulations and semi-analytic secular perturbation theory to model the phase-space dynamics of the outer Solar System [cite: 3, 5].

*   **The Measurement Projected**: The theoretical model projects the existence of a super-Earth with a mass of approximately 5 to 10 $M_\oplus$, residing on a highly eccentric ($e \approx 0.6$) and inclined orbit with a semi-major axis between 400 and 800 AU [cite: 6, 7]. The primary measurement projected is the survival and phase-space confinement of eTNOs. Specifically, the model predicts a bimodal population of eTNOs: one group apsidally aligned with Planet Nine and another apsidally anti-aligned, maintained via a web of mean-motion resonances and high-order secular resonances [cite: 3, 8]. Furthermore, the model projects the generation of a perpendicular population of high-inclination Centaurs resulting from the Kozai-Lidov-like mechanisms induced by Planet Nine [cite: 3, 9].
*   **The Verdict Reached**: The dynamical verdict is highly supportive of the existence of Planet Nine. The simulations demonstrate that without an external massive perturber, the observed clustering of eTNOs would quickly disperse due to differential precession induced by the known giant planets [cite: 4, 10]. Planet Nine not only actively shepherds the eTNOs into clustered configurations but also facilitates the dynamical detachment of their perihelia from Neptune, explaining objects like Sedna [cite: 3, 6].
*   **The Axis of Disagreement**: The primary axis of disagreement lies with theories invoking either purely random distributions (arguing against the validity of the clustering signal) or self-gravitating disks. Batygin and Brown explicitly contest the viability of a self-gravitating planetesimal disk, arguing that the primordial planetesimal disk was rapidly depleted by the giant planets' migration (the Nice model instability) long before collective gravity could shape the outer Solar System [cite: 11, 12]. They assert that the required disk mass ($\sim 10 M_\oplus$) contradicts observational limits and depletion timescales [cite: 11].

### Attempt 2: The Inclination Instability and Collective Gravity (Madigan & McCourt)

A formidable counter-application within the Dynamical Systems lens is the "Inclination Instability" theory, pioneered by A.-M. Madigan and M. McCourt (2016). This framework utilizes Gauss $N$-ring codes and $N$-body simulations to model the outer Solar System not as a collection of isolated test particles, but as a massive, self-gravitating disk of eccentric planetesimals [cite: 13, 14].

*   **The Measurement Projected**: The model projects the collective gravitational behavior of an axisymmetric disk of eccentric Kepler orbits. The primary projected measurement is an exponential growth in orbital inclinations coupled with a decrease in eccentricity, causing the initially flat disk to buckle into a conical shape [cite: 13, 14]. Concurrently, the secular (orbit-averaged) gravitational torques between individual orbits naturally drive a clustering in the arguments of perihelion ($\omega$) [cite: 4, 14]. This "collective gravity" mechanism projects that the eTNOs will undergo eccentricity-inclination cycles, naturally producing detached, high-perihelia objects [cite: 14, 15].
*   **The Verdict Reached**: The verdict is that the outer Solar System anomalies can be entirely explained by the internal dynamics of a massive scattered disk, rendering Planet Nine dynamically unnecessary [cite: 7, 16, 17]. The authors conclude that minor planets orbiting the Sun like the hands of a clock will gravitationally jostle one another; smaller, faster-moving orbits will pile up and crash into larger bodies like Sedna, changing their orbits from oval to more circular, detached states [cite: 18].
*   **The Axis of Disagreement**: This approach disagrees fundamentally with the Planet Nine hypothesis on the mass distribution of the outer Solar System. Madigan's model requires a "new Kuiper Belt" containing roughly 1 to 10 Earth masses of material to sustain the inclination instability against the differential precession caused by Jupiter, Saturn, Uranus, and Neptune [cite: 11, 13, 15, 17]. Critics argue that such a massive disk should have been detected in infrared surveys or would have been scattered away dynamically during the early Solar System [cite: 4, 11]. Madigan et al. counter that Planet Nine advocates underestimate the power of collective gravity over long secular timescales [cite: 16, 19].

### Summary Table: Dynamical Systems Lens

| Parameter | Attempt 1: Planet Nine Hypothesis (Batygin & Brown) | Attempt 2: Inclination Instability (Madigan & McCourt) |
| :--- | :--- | :--- |
| **Measurement Projected** | Resonance webs confining eTNOs; Generation of perpendicular high-inclination Centaurs. | Exponential growth of disk inclination; Conical disk expansion; Apsidal clustering via secular torques. |
| **Verdict Reached** | A 5-10 $M_\oplus$ planet is required to shepherd eTNOs and prevent secular dispersion. | Planet 9 is unnecessary; self-gravity of a 1-10 $M_\oplus$ eccentric disk naturally causes clustering. |
| **Axis of Disagreement** | Massive planetesimal disks would deplete too rapidly; collective gravity cannot persist. | A single massive perturber is redundant if the collective mass of the disk is sufficiently high. |

***

## Lens 2: Information Theory and Bayesian Inference (`STANCE_INFORMATION_THEORY@v1`)

The Information Theory and Bayesian Inference lens steps away from raw mechanical simulations and focuses on the rigorous quantification of uncertainty, observational biases, and the extraction of weak signals from noisy datasets. This lens relies heavily on Bayesian posteriors, Shannon entropy, and prior distributions to determine the true probability of Planet Nine's existence.

### Attempt 1: Pulsar Timing Arrays and Unmodelled Mass (Guo et al.)

An innovative application of this lens is the use of Pulsar Timing Arrays (PTAs) to search for unmodelled mass (UMOs) within the Solar System, as demonstrated by Y. J. Guo, K. J. Lee, and R. N. Caballero (2018) [cite: 20, 21, 22]. Millisecond pulsars act as exceptionally stable celestial clocks. To measure their signals accurately, arrival times must be corrected to the Solar System Barycenter (SSB).

*   **The Measurement Projected**: The method projects that any unmodelled massive object in the Solar System (such as Planet Nine) will shift the true SSB relative to the ephemeris model (e.g., DE421) used by astronomers [cite: 21, 22]. This error projects a highly specific, time-dependent dipolar correlation in the timing residuals of widely separated pulsars across the sky [cite: 22]. By utilizing a Bayesian data-analysis framework, the researchers project the Bayes factor ($\mathcal{K}$), which is the ratio of the Bayesian evidence for a model containing an unknown Keplerian orbit versus a noise-only model [cite: 21].
*   **The Verdict Reached**: Currently, the PTA datasets place stringent upper limits on unknown masses in the Solar System rather than confirming a detection. The Bayesian inference framework proves capable of restricting the parameter space of theoretically proposed objects, mapping upper mass limits as a function of orbital distance [cite: 21, 23]. The researchers conclude that future PTA data will be sensitive enough to detect objects lighter than $10^{-11}$ to $10^{-12} M_\odot$, or to measure the mass of Jovian systems to fractional precisions of $10^{-8}$ to $10^{-9}$, thus providing a definitive, non-optical test for Planet Nine [cite: 21, 22].
*   **The Axis of Disagreement**: This approach differs entirely from optical and dynamical lenses by bypassing the TNO population entirely. It disagrees with the reliance on eTNO orbital distributions, which are subject to severe spatial and temporal biases. By treating the Solar System's gravitational field as a continuous information channel (measuring the Shannon entropy of timing residuals) [cite: 24, 25], the PTA method provides an independent axis of verification that is blind to the $1/r^4$ optical dimming that plagues traditional telescopic searches [cite: 26].

### Attempt 2: OSSOS and the Quantification of Observational Bias (Shankman et al.)

The most critical challenge to the Planet Nine hypothesis from the Information Theory perspective comes from the Outer Solar System Origins Survey (OSSOS), led by researchers like C. Shankman and J. Kavelaars [cite: 27, 28, 29]. This attempt focuses on the Bayesian prior and the rigorous statistical modeling of survey selection functions.

*   **The Measurement Projected**: Telescopic surveys suffer from the "streetlight effect." The brightness of distant objects varies as $1/r^4$, meaning highly elliptical eTNOs are exponentially more likely to be discovered when they are at perihelion (closest to the Sun) [cite: 26]. OSSOS projects that if the pointing history of discovery telescopes is heavily biased toward specific regions of the sky (due to weather, galactic plane avoidance, or seasonal observing schedules), the resulting catalog will exhibit an artificial clustering in orbital parameters [cite: 26, 29]. Using detailed statistical modeling to account for these biases, the projected measurement is the underlying true distribution of eTNOs.
*   **The Verdict Reached**: After rigorously quantifying the observational biases of the OSSOS survey—which discovered over 800 TNOs in carefully calibrated sky patches—the researchers concluded that the apparent clustering is a statistical artifact. When the detection biases are removed, the underlying distribution of eTNOs is consistent with a uniform, random distribution [cite: 28, 29, 30]. Therefore, the verdict reached is that there is no Bayesian evidence necessitating the existence of Planet Nine [cite: 29, 31].
*   **The Axis of Disagreement**: This is the most direct confrontation in the field. OSSOS researchers assert that Batygin and Brown's foundational dataset (the original clustered eTNOs) is inherently flawed by unquantified biases from mixed surveys [cite: 29, 32]. Batygin and Brown strongly disagree, countering that when combining data from multiple distinct surveys, the combined bias actually works *against* finding the observed clustering, calculating that the probability of the clustering being a random coincidence remains at 0.2% (a 99.8% confidence in the physical reality of the clustering) [cite: 26, 33, 34]. Furthermore, critics of the OSSOS conclusion argue that relying strictly on Bayesian parsimony or treating missing parameters as proof of absence overlooks the robust dynamical mechanisms that independent simulations demonstrate [cite: 30, 33].

### Summary Table: Information Theory and Bayesian Inference Lens

| Parameter | Attempt 1: Pulsar Timing Arrays (Guo et al.) | Attempt 2: OSSOS Bias Modeling (Shankman et al.) |
| :--- | :--- | :--- |
| **Measurement Projected** | Dipolar correlations in PTA timing residuals; Bayes factor for unmodelled Keplerian orbits. | Bayesian likelihood of underlying eTNO distributions factoring in $1/r^4$ flux and survey pointing biases. |
| **Verdict Reached** | Places rigorous upper mass limits; projects future PTA sensitivity will conclusively detect or rule out Planet 9. | The observed clustering is a statistical artifact (the streetlight effect); no evidence for Planet Nine. |
| **Axis of Disagreement** | Bypasses eTNOs entirely, arguing optical surveys are inferior to pure barycentric gravitational tracking. | Directly contradicts Batygin & Brown, claiming their 99.8% confidence signal is merely a selection bias. |

***

## Lens 3: Renormalization Group and Advanced Mechanics (`STANCE_RENORMALIZATION_GROUP@v1`)

The Renormalization Group (RG) lens evaluates the problem through the mathematics of scale transformations and asymptotic behaviors of differential systems [cite: 35]. In celestial mechanics, RG methods and related theories (like KAM theory) are utilized to study how Hamiltonian systems behave under perturbations, how resonances break down, and whether fundamental physical laws (like gravity) require scaling corrections at vast distances. 

### Attempt 1: Modified Newtonian Dynamics (MOND) as a Scaling Alternative (Mathur et al.)

A radical application of RG-adjacent scaling principles to ASTRO-0001 is the use of Modified Newtonian Dynamics (MOND), proposed by H. Mathur and colleagues (2022) [cite: 36]. MOND operates on the premise that gravitational acceleration scales differently in the ultra-low acceleration regime (below a critical acceleration $a_0 \approx 10^{-10} \text{ m/s}^2$). The deep outer Solar System presents a unique laboratory for this, as the solar gravitational acceleration drops to $a_0$ at a distance of a few thousand AU [cite: 37].

*   **The Measurement Projected**: MOND modifies the effective gravitational potential. Mathur et al. demonstrate that when the Solar System is embedded within the Milky Way's galactic gravitational field, the MOND formulation induces significant quadrupolar and octupolar terms within the Solar System that are entirely absent in standard Newtonian gravity [cite: 36]. The projected measurement, using a secular approximation of Solar System dynamics under MOND, is an alignment of the major axes of Kuiper Belt objects with the direction to the center of the galaxy [cite: 36].
*   **The Verdict Reached**: The researchers conclude that MOND provides a compelling, planet-free alternative explanation for the observed eTNO alignment. The predicted clustering of orbital parameters matches the features exhibited by the newly discovered class of eTNOs [cite: 36]. Thus, the "Phantom Menace" of a hidden planet is replaced by the background scalar field of the galaxy acting through modified gravity scaling flows [cite: 36].
*   **The Axis of Disagreement**: This approach challenges the foundational premise of both the Planet Nine hypothesis and the Inclination Instability model—namely, that standard Newtonian/Einsteinian gravity is sufficient to model the distant Solar System. By altering the gravitational force law at large length scales, MOND theorists argue that introducing a new, unseen "dark" mass (Planet Nine) is an epicycle compensating for a flawed understanding of gravitational scaling, mirroring debates over galactic dark matter [cite: 36, 37].

### Attempt 2: KAM Theory and the Breakdown of Invariant Tori (Celletti, Calleja, de la Llave)

In mathematical physics, the Renormalization Group has been adapted to study the Kolmogorov-Arnold-Moser (KAM) theory, which governs the stability of the Solar System [cite: 38, 39, 40]. Researchers like A. Celletti, R. Calleja, and R. de la Llave use RG techniques and automatic reducibility to study the breakdown of invariant tori in dissipative and conformally symplectic systems, such as the spin-orbit problem in celestial mechanics [cite: 41, 42, 43, 44].

*   **The Measurement Projected**: The Solar System is a nearly-integrable Hamiltonian system. KAM theory projects that for small perturbations, most invariant tori carrying quasi-periodic motion persist [cite: 39, 45]. However, in the distant Solar System, eTNOs are subject to mean-motion resonances with giant planets and potential dissipative tidal forces or secular torques. The RG approach projects the exact "break-down value" or critical surface where these invariant tori disintegrate into chaotic motion (often associated with Arnold tongues and overlap of resonances) [cite: 38, 41, 45]. By utilizing RG transformations and Sobolev blow-up criteria, the method calculates the a-posteriori critical parameters where stable orbits become chaotic [cite: 42, 44, 45].
*   **The Verdict Reached**: While strictly mathematical, the application to celestial mechanics proves that long-term orbital stability in perturbed regions relies on precise Diophantine frequency conditions [cite: 45]. When applied to highly eccentric trans-Neptunian objects, RG-KAM theory indicates that without a stabilizing resonance mechanism (such as the mean-motion resonances provided by a shepherd like Planet Nine), the overlapping resonances of the known giant planets would lead to chaotic diffusion, causing the orbits to break down over secular timescales [cite: 46].
*   **The Axis of Disagreement**: This lens diverges from pure $N$-body numerical integrations by focusing on the rigorous analytical proof of stability bounds. Where a Dynamical Systems simulation might track an eTNO for 4 billion years and note its survival, the RG-KAM approach seeks the exact mathematical boundary (in parameter space) where the system transitions from quasi-periodic to chaotic [cite: 39, 47, 48]. It implicitly critiques brute-force simulations for potentially missing secular chaos due to numerical integration errors, advocating for RG-based "Lyapunov time" calculations to truly define the stability architecture of the outer Solar System [cite: 47].

### Summary Table: Renormalization Group Lens

| Parameter | Attempt 1: Modified Newtonian Dynamics (Mathur et al.) | Attempt 2: KAM Theory Breakdown (Celletti, Calleja, et al.) |
| :--- | :--- | :--- |
| **Measurement Projected** | Quadrupolar/octupolar galactic field effects under MOND scaling inducing apsidal alignment. | Critical breakdown surfaces of invariant KAM tori using Renormalization Group flows. |
| **Verdict Reached** | MOND fully explains eTNO alignment without requiring dark matter or a hidden Planet Nine. | Orbits require precise resonant parameters to survive; without a stabilizer, chaos ensues. |
| **Axis of Disagreement** | Disagrees with the Newtonian foundation of all other models; dark mass is an illusion of modified scaling. | Focuses on rigorous topological phase-space stability rather than phenomenological $N$-body simulations. |

***

## Cross-Lens Synthesis and the Core Axes of Disagreement

The debate over `ASTRO-0001` represents a classic paradigm struggle in astrophysics, characterized by the limits of observational data and the divergence of theoretical frameworks. The **Dynamical Systems** lens operates under the assumption that the physical data (the eTNO clustering) is fundamentally real and searches for a mechanical cause. Within this lens, the schism between a singular external force (Planet Nine) and internal collective dynamics (Inclination Instability) highlights our uncertainty regarding the primordial mass of the Solar System's disk.

The **Information Theory** lens serves as a skeptical auditor. The OSSOS application utilizes Bayesian priors to argue that the foundational data is irrevocably tainted by observation bias—if you only look under the streetlight, you only find objects under the streetlight. Yet, Information Theory also provides the tools for salvation: Pulsar Timing Arrays offer a path to circumvent optical bias entirely by listening for the gravitational "footsteps" of the Solar System's barycenter.

Finally, the **Renormalization Group** lens forces a fundamental questioning of the underlying physics. If MOND is correct, the entire search for Planet Nine is a wild goose chase born of applying Newtonian mechanics outside its valid scaling regime. Conversely, RG-KAM theory reminds us that the mathematical architecture of orbital stability is delicate; the very fact that eTNOs exist on these orbits implies a deeply structured phase space that demands a sophisticated stabilizing mechanism.

## Conclusion

The primary-literature fingerprint for `ASTRO-0001` reveals a vibrant, highly contested scientific landscape. The strongest arguments for Planet Nine (`STANCE_DYNAMICAL_SYSTEMS@v1`) project an elegant, resonance-driven shepherding of trans-Neptunian objects. However, these are fiercely contested by collective gravity models, undermined by Bayesian bias analyses (`STANCE_INFORMATION_THEORY@v1`), and potentially rendered obsolete by modified gravity frameworks (`STANCE_RENORMALIZATION_GROUP@v1`). 

Currently, no single lens has achieved absolute consensus. The resolution to the Planet Nine hypothesis will likely depend on next-generation empirical data—either a direct optical detection by upcoming observatories like the Vera C. Rubin Observatory, or a definitive gravitational mass limit established by the next decade of Pulsar Timing Array observations. Until then, `ASTRO-0001` remains one of the most compelling intersections of celestial mechanics, statistical data science, and theoretical physics in the 21st century.

**Sources:**
1. [oca.eu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQYjn9CWqfibqal8GY4mbv5DElKbM778l6_ZSLR3qDNgJtFkTtpwHX6rUSZrFdMI4zXOepNtoRZ2E8uD2ClDqbqAdMynZ2NoN6aXzPUErfKcUf5hNZGtdxXaUoVziqTnvEdZZsw4sGiqNU9Mzk97IGo-kjQMaV93y0cHfalQfUwW10TwaV6GePiFU6uZRmP4r3RHLu5htUNzADATeOlCd9IPSv8MCH8A==)
2. [ucla.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcywqsOR_yVcMy50-9000GWDKIWd_SXwd6eH17qw7mcl-dayEWTYWpbWhKcMx336ipsB6WC2fZUmY1zLud_uNyPUnujl-LmMJDhfi34hn3fbCmPqSqk7wUmlUIEl5LPNht9H1RjK2f-RiBG59Ard2G)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyiAAbrBmwUD5S53j6nSfnICzg5CeDUlyRax1CrYNRF-6Y_vb7DrrVzKra-QFshXZeKvOYWwPH9HRhd58nN0e_moNXOf1OtCrweZLO3qlC_o4xSB5qxg==)
4. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1dm789nQmrjvxL9H8t8_w6iQqBgzelnPpwS0VvTF4w0RDmc8Nv_-cXtMKP-Sy3KsP9lSn3TR1ei7JjJGWi_O5idVSVYQlH16Pk2kunrdQ4zIzdbqhjuwnkOJN-hRTzi-RsAuG5ned)
5. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGt81he4vSo3BsvIYYC_7X5C9WHduj0_wjl7zjNP9aNHUeLJBD6G2B04gGZLvKGBhtMhGqi05DlpvYHAFJjyvQPMqG7P5fGUoVEu6p5CLlM8FJZCqh9SC92)
6. [planetary.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4WqxN_SnuA5DlCjMNL9Qu0oL08nStjeXY6p1Qtl2YF-idG2YiHxMJG3mZBIuuhlLYpIZEfNMwB0wo7hKkQBFy5TAY3aASvrp-3fdtW4cJIl69mZnL6vP_CtnSgqrUvLwV0kAbfQhl8EcihhvjB3iZ3dDFCR-3ddK1ujs=)
7. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgggB0lXSDrS-IpRBVPb2v1bxDA7DKuBXkWHMapi76J7d4M4td1ZiGMOImn4yyZjH63oBmGQ1gHJFWoDehD13AgHlgYg4bgMU7aKKPj4g5cqyKp4Bm7F9O7imYe20=)
8. [northwestern.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE16yxRO7w4gs_LaVeuVEov9zepIp3CgsPIDz0seXhmnHTxftRyeskqyGPOz6jjoLMnT_fqySbhsjrD2kYSPFmBsGqeszq5z3TqyBcDwwb3qam18CGuVMa4s_jyfNdJmRKbeSAX4Jl_REpup1q_uIs=)
9. [lims.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9qgGzQJxRn--eTxrNH3iWJnGzQdu9MXj0RcDg6PtfLVfAuuP2OsiNGNtUr3aFXcB66FADwjFLX3otnLU32XSAiGZ21x8a3BxrWqn4BUZ45duIKDsDTWbpJt_e2ew=)
10. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExq3vXcnbDsGmW-jUQ1I75XongQ4IlT2P6nQifdx29pZM1kKg6qnQdh3u0c9pqvASU91vjCegA4EjrF_DriSkr_vWVohJIRpz6_kR4yq0LXJ5f2CJmUu1LIHu7HprbKUg3PVOxMvg6)
11. [space.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFW9MzQ5XgyHEjCuDG51VAHsKQvMVsYuxuK9nR6horUnizSEZTDZpCbhEcmnrQI_AlXnNwEIgjhE1gTPMz_f54FPjBd-VIS_S4vA8oNM3XzSr0e7zXfhlKZcZuTTEwJHO4c0nCVF8-zqCWZi_APtP58J2ZFSjI=)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_7-7AinuVXSMhQs1lJH7GDqyzPJuJC9yqQSaQIlDMwkM4veZ8mxTotuk_djbOB836e9f8Rl_r_jiD_K_OTYoUJvuTZjT4Xw6yvG_Dmr5Zxv3E0mZapw==)
13. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsyyOqTP0G_uYMAXTSBPZqrvFLGgDhddg--TOuWQ6FJcu2-YHPvjRPeDWNFtEntYDCwr5FMi2kUlthwdKleibNPVTnmd83azH__ORGa6LbvSi8UNcgF7sUiXxD6nrWQQT8o9e8lkMPhbEx0w==)
14. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1F29cBgYz3v9JrGfkH3hkjnww3FP2TnsuvgSW7rJht4lhgqLw3ENjClOLHU4GlSFCzHZ8hZKOH44JyM_8aI6l9uh8G-5P3nPoxnTJpkzluUxYHnFZf-hiXfiEYZLbhrHtf3FYfcVR)
15. [d-nb.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGe06l9vX0mmQ6kd39bqUkNR5x3YeGw5u9tbO27eaWJwaIXCLtZPYE4c84MxIHo4MRpyL7eXGcgVBA2rvV0kpMRmu0PBzAtvNZs-QThQdiy773w4JFB)
16. [colorado.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFE9awkFU3AUG8_XoVl9IbF0LoqdNsGDdgRRDljqFGH0blMjQZsybuXTDS7Bz5n5bE2ZDH1CriP87Xo1bcjhJOnK2hj_xqVA-BzWs5-HV5ls3iOfz2lcirFpMgImo87cOyegwHMeuOT3Ea8A1TdQS5hZ64=)
17. [colorado.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHsDs-1Azl3SbkVNG9GV24GFXlZNF3YWoVX3KVE2MW3oPwPJZtc4b1RtxqBVY-RLMS3fkWnUeHv5tBw3FgjUPGF0AeMAn7LIJ2w5It2_9FlOd7S9zki8CL1ILzwVHpdy7YDkKyI8sQ51B0ADGRon9MX3dPg5cqIGwG9jwsQiCMiEw==)
18. [sci.news](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEoKQZ4OlSW7lkKqdpoMhJ7ZLdtJPxgX7WsTGAr6c6Hc2k381mwYcXe3jyfy2lMnBOd-FaIeHLyJt63zPKOyI8JvTuN7Nm9BWYLlgT6thxlx9L7SZNlsuyYitVqkoqfBPH_janstwXU7NsfBnJy2PN0M3vzaEPGMgVpoFocE8olFxuJ-3ItFO_LOopzM5LlxsE73kLVJMcTi1oCm_yj6TnaKmLgWhYHmOtqrMnSrRU=)
19. [earthsky.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEB8Ivc3V397NP_kti4uzwhGOM2Zy-Fpk7BD7W6iSRlpAKw5CVeE3K1PawEUnI_eupTDKHf002oZ0bkY_j0EVyacw-cnlcB4-fyoUMVPv1APaw4iznh7l-V7NQXNAr3xKShORhRroL0c5HFhUN1F1mCldAra-9NgwMxsd0mXgCZrvgz9ANJqe7smRE=)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8nu5Zrso3RaSKgS8iRjvmdtGYny2R2-yG4splXu898pmMu4iHnn52xkTwoj13-0pBH2nhz6bFQMSBnFdxgh34nW97OSIurx_9jDlmBlf_XMWwQTSacw==)
21. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3Zyz_N0ww6bLFp5-QWQMj5gqhHKXtGs6kNEyyeO447gZHWn_XIheVjCqZh8rtmWY7AQ6Yf3zlC64thgp_SS8jJ7_XQhbYl0MckSfOpcdYngLk6O-mfjKnIH-KIkbNBmPLtROZNlxloBRSsBSY0-U=)
22. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqSUUsDJ0gjvTWdlUCj4nU_Ougu6vSa3rsfCL8ChmRJ3gtrpXarv_19VL2PtxJ97VVo32amOD8PO_S3hMfGl79KyhrHRGpRd_SjQmneEizW-GIVNZetZDr1cs8rnv17UGe8rVcSc-P8WNlzFvKWIdjrVZW6H0khMUzD5DP90-gvQ==)
23. [iflscience.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNiY_VZAadCqrpUDt5QJqtaG61XQKzamYo-5uHRKP_c3F-dG7xDE8EFr9myhN1_ysxkPBXPgMci09xYIZxBvEfk_CKKhzCl0P2478WNqKw5M7VpfS0dLn_TaI-GtZeq9rRjn1q8h23p_kjup1ExFiNgO1s6iobitI2FCjTMRZwptNB3t3XCMOxhW666wg52agUGnQK)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTQkaVUl1jwcmhnuHQOh7BvKJnsnB_h_mYunJmqxY_T1Vzy3L6lq6gABq337sZx31smgzJULziLJxK_TalU_0M5syT4VlFELnt-ECa8Ijz9hh3ttJtYQ==)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmduS88O0f2W21WZMWScoO0AIA2dAj4fPKClcibfE4-RwaC6sNSxR2euemT0UvYJWzSNxjQds0glQ6aiA5-2chvHFR6kuSJy1kE9-rJJSy_bK2dZd-xNRalA==)
26. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELJhiVlkkQjOIX7TEcXjXoVj8AjMDkv5QznPXk14h_WLlfRlotnXP1PkFvAkitQPVI0XFpDSL82nXTqhDHQa9hvrgFdL1LPUPcIDz3IluBo-QZ3qx5ci5gvKCs-OG49gJ_2ebZQR-wbUI0vsVAb44uwjDFBz8H7aXGTXhFZdTGOyVQuNXIHOdWCLOr3mEQ0WkEXL1-gkuW7biD7m7l3bTXJ7DeQY-u2x51jSdIUmHEv6cIF3Zr)
27. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEi-A4DuuezRTdNLwqk0DiZH4ckfCwEAfHeSci5H47B8iR1HLgDz1QHk6OiHuUyNRzVjVFbCz7zEM9ibrviIBrnqUagAyLqNtmSeOipH4U3e6MlJJdKYHnw_xcWrjHA-n6Ie7NodfksJdxL-Pm9QWiFkgUR9ttcZu5Pq3XEFBY0QBm7rjfUm1FYT3x7BjNkMllEipxsM69wI1pfUwEfZxrtomN_o3zB2fSW2teL0i-AwreHqBeBwjpVmZVF_I5OkY9B1S1wmfNWNegkLny22NIPe70Ik8Y3uzgRIwhJwEg_RG4usnDJ9_SqPPfp26bm6GY5rUG-kWSC9kV5OkJj2weIoycUpLCdzRXJcaXRap-2ONbN-anLSFpR)
28. [quantamagazine.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJ4L4cMqV_99ak0YbXq0XcS066bgzbGrcyxV63otD0TP4HNWTYjCuyyGVUN_ok3C4rZtwrZIKs1gUtpkh-f3mGv2OhX7fYUaqB7Df3p34vOF8nv0d8iA_b1K9tKQU6e-G-1A3SmTUwxgz9sx991yTRxXPUuQECPC0XMgOYxRzfP0LWbwWPPQ==)
29. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFo4pT0Xd5AZoi517NvXlHGC8yIFIoSiTajYaW1XZozNwPwhkkiy_9AxhOrfG13jOn6UcuFXmxiCn6PdAIKpoR3f4Sso8AhJZLFsWcMGbJMN2Bx7HwZQLI4grZfcF_teBIyhfAV04S7JqudQg7UKWvbpQbVXAQRoI9gq_In4hu94fD2r5zh59Uh3AmN3Vm_7JLFBSjUTffw_jjPfdtLCq7uH7bu)
30. [ycombinator.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyPYx7DQoYpZfB-1IHxnmvM2Ecz-wF163kSrXNkDDRTp8VZMjvIkrdwSMmgMYFWJ1622XHSdL7EB4oXTEXVuTI7VxDW8PDUOEA8t_nsbfCAitN_o5ph88xkAmcILtBGi57kTg=)
31. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTg88brHDa9eDRUWH43r68pb5KopPBiUH2frAoZR2kESyFaiHKL7QzCxSrwqylJJsdEgN-s5oCOv19FHnt1L3xRlZoxibT0InI2FfJ2oAk6PJT8qHxL7LRgmyM1MAP7KFBha7lUIW66hZMVSadKxWB)
32. [forbes.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHziQbwOnfIH1Qp9V7jzZX1ZciB5v5nJ3xdWt1Aht9QZr3_Zdd8_L4SnZMesrnQcfiv3NcJ690gE9mpf52L4iXqf8d1X92tYjGBMnU6crJ3J6XnwczPYImoB70_BEPIplOFVPKTlr4DumZNLJVKuPAPxdJA9ApoiYd6uXVpeuvYrn8xdhG3BB1hu8U7OSzGDpO3Wc3bzPcXMfRUnfHk2SUnznyen2jGwHXRj9vToxo1iLAqjimn0ogGjdjHn_S9F6aXj88qBTOu)
33. [physicsforums.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFtEdVv7VaFZxGV2YOkQZ-VLw-x0izJuTik3HWdI2W7jznx7JVr7m-HFbztnq7Tk0lHekARdLL6kFTGO27sctthS3cqDktDCEZPD5fSjHOwCU2Ixx1Ia9QlOEPN-Egcism70AAKMbJUj_uchbX5QJP29AOYclG53j9J-NAU8Q-wOg5NM1Dj91sHbw==)
34. [nautil.us](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2UrIyVMfJf9axsO-uzB6m3OCVr_Xmbslw8AT-j4y6MZrn0V519rv3nlzD6bc_daSUsLWeJi6KJGTyojtB8tnD-6U-dQpzIYHPCSm2w9yM4BZw657Ab7lOUdVup4yq847io8DJRcfaPQQE-rGA-xVUlx4a36K7)
35. [itp.ac.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEjXDJYr1DeZqjatUzhH46Faww9wLhGppOvnuwP_w77hshnl_oiVigkruegVBxZerZS_mpkIFFn0wVM-_L_FeY7iF6IJ5JoQr3_87pRDpHSZ0m3CYcT4UEiZBTNP0aWfG_VyEKfs0mwYKrWw==)
36. [pirsa.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEIWIoydWJfRS0hGLvdGxT7xpRqvc8hYt-yYtdMedSfTyHtHDofouM7EiidG9_F9ruLWxJUPlRdOcVMvbx0wXOGrk3pMwcbpihxwE0zolfTaQ==)
37. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMNBMumBUgziduMMBRYac_O-1M8p2HrTmb9QovSRDGwZwZwCZKF81DZuBSNtLyAW_SzdyfMXek9w8yZaVcIwjAlwM5kNR1frQE_Y-o4OLdt6H5F1ZQ4RB29ikPGJJnGUNKDCWCHB26PQKIc8-rff2OhcmVgPSLBLZXgaMitClO3awRpSBmBec5Zg==)
38. [galileo-unbound.blog](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrAAiPGFRHlOabsJESVDiGvHHnk3WbIbHbRUPXl_AK0sA12E--GW_KTSgIt9KJguEISJEWxtQvmV6Q_juN6i_wJvd2GsIUQQ-F59erCIZvoZMLqgH_pCDdv0J1F48vVlactw==)
39. [helsinki.fi](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESn4rqdWbqmCyCfb4aDzi2_84dwT4viuS89KchBA9OD6xmvam-FdoolicM1gYg5MLEx22a9X8ecQVJPJA72P1UOXRd6cNDrKMtAdFoGWZgJ6ZxjH_26StamjP8CW4pYWZUoqO6ANs5bVb2USSA6N07IjMDRWz4TFWw4ebZhHA2KpXQIekM53MJ)
40. [muni.cz](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEq8kAf6iC1DKW0ABDx0_WrulpIe8EbYC501a1Lw3uVcpXhshQbfqh9cfvRmp0lZOK77iMzxngmPLCcm_LdBdSaHPTwrQA-uBk6pkz3hfWjBbIoIv2RkDCo1qM4SJY0uguQZ7By6nog49I5wo7hsIdAKnF4w5SL41sYgnJN-vepP0R7yPA9Psbm0A==)
41. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJXYOgRmj8RkhPcsydELiKb-lkpMNrxD9FS8PCtu6ZpAWi5BKQBPza-b_mTAFkPIeNfDgeI2OaNqr333hgfi3HFWM4rsY_EdjkHJmyo5nG9JdjMy0AnQ==)
42. [utexas.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDThaJJgKq_lmE_2hdCAHLeyY6mQzaReQoiOQ9DNlFMFvGyKfCXK5Gy129wbgwUrTIvX7WvoK1gX9s1FnSEnypiO0G756qKoWNJ1hGYvjCs5GBoDZ3c2Fdgnv-e5rQjorN76cTGw==)
43. [oca.eu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEh6qXIGhX43LVeW_F65V0g0d9J7kS_9IsYHbUdpix33_XHe7mKvuEbNPlZWb2f_URykfMKsrOZvtMXs00ugf5iEkbqZKYZgsq5DiDEd3CZnbxTUu7GCe3ZqHg=)
44. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHMcKB-JtVewuL8Kk7vvQ6faOPSXXFjFphFbxx2XIdm6eUalmJt5dPAk2pKqUK4HTDv6AAECR9_MCaP5uWV4w9yv6Pan7zKvpEed2XgtnbtHWcR4KDXyap0g2Bf4_lDph6ut3W5yNGEBSoosYFYdY4wZu8U_ib5db6qZm_I1S7Qtzp6rfR4nt6IBHMayum--c=)
45. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-5mxVSTt4kHQnjEpI1Bwpf__47JVCIjqIPVth33J6IktVqd9X6WnOgt0byl2RQOAdAGs9wcImBCwwmLsyX0D630nJ3fpXHEZmV1l9G-O-YR8otl8HGSoREDwVIPmViVPJtWA=)
46. [ics.org.ru](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5glGN9WsR3CvqwTTroFnkV-_V5s2GkqbmmCNVsr8uUBeTXeZ7iNOoLx2mxlBWbf0OGPQBw33tKXer9Y5vxiCV-hag33VzCSiUUw0ByXS0pP2cnQYmbY9D24AklO7AWdck9zskBjIX)
47. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGB4j6auXIEE72yQbI1e4W-H81NJaBzFbxo0xx6PQjxZUuVdxTmQGjS0pUbSIdqzvKMgT_5Us3MCCXKk464fe0fIICe1IzjPF8mn3_vmpzNl2Z-VZ6FO3vE9N0PUveBdi1dUgmql053T-yhulhsp7bKPSehJztez6d-okqf0lSLs8qUvA==)
48. [unimi.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJIx3KEuhcYG-BEdpQFsSziTB9LzJI9Ur6qPiL8EGYZ3TYqAKLV1PvyuMfk39W18v0YnjWh3iY75ZB9D0ZWhbojFCjpVGx8Fv9EGoWQqJMg6JEAFBPbJiFzIwU4maJzs-u1X-qOaGfj3i0_Zpa01eHEGMtHrVrfeapKCTGAl1EuSK2wg7tJQ==)

