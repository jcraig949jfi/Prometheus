# Argos lens fingerprint: Extreme TNO orbits

**Pythia queue id:** 230
**Tier:** T5
**Priority:** 5
**Requested by:** Argos
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdNMVVQYXVIdEdmYm5qTWNQbHM3dThBcxIXTTFVUGF1SHRHZmJuak1jUGxzN3U4QXM
**Elapsed:** 438s
**Completed at:** 2026-05-21T19:03:06.849474+00:00

---

# Primary-Literature Lens Fingerprint for Open Problem `ASTRO-0002` (Extreme TNO Orbits)

**Key Points:**
*   Research suggests that the clustering of Extreme Trans-Neptunian Objects (ETNOs) in orbital parameter space constitutes one of the most significant anomalies in modern celestial mechanics, challenging the completeness of the known Solar System architecture.
*   The evidence leans toward three distinct explanatory paradigms: the existence of a deterministic physical perturber (Planet Nine), complex observational biases revealing themselves through statistical asymmetries, or the manifestation of modified dynamical laws/algebraic attractors at large distances.
*   It seems likely that the `STANCE_DYNAMICAL_SYSTEMS@v1` lens provides the most physically intuitive framework, modeling unobserved masses via N-body Kozai-Lidov secular resonances. 
*   Conversely, the `STANCE_INFORMATION_THEORY@v1` lens introduces rigorous skepticism, suggesting that machine-learning clustering and information criteria (AIC/BIC) might reclassify these anomalies as emergent statistical properties or observational selection effects, though highly significant (62\(\sigma\)) mutual nodal asymmetries complicate a pure-bias explanation.
*   The `STANCE_RENORMALIZATION_GROUP@v1` lens offers a fundamentally different mathematical ontology, proposing that secular anomalies can be absorbed into running coupling constants (Chen-Goldenfeld-Oono method) or explained through effective field theories like Modified Newtonian Dynamics (MOND) and universal topological fixed points.

**Summary of the Problem Space:**
Open problem `ASTRO-0002` centers on the peculiar orbital dynamics of small bodies orbiting the Sun far beyond Neptune. Specifically, objects with semi-major axes \(a > 250\) AU and perihelia \(q > 30\) AU exhibit an unexpected alignment in their argument of perihelion (\(\omega\)) and longitude of ascending node (\(\Omega\)). Resolving this problem requires untangling whether these extreme orbits are the gravitational fingerprints of an unseen Super-Earth, the remnants of early stellar flybys, the artifacts of localized survey deployments, or the breakdown of Newtonian dynamics at ultra-low accelerations. 

**Summary of the Multi-Perspective Approach:**
To deconstruct `ASTRO-0002`, this report applies a multi-lens methodology. By triangulating the problem through Dynamical Systems, Information Theory, and Renormalization Group mathematics, we extract a "fingerprint" of the primary literature. This approach not only maps the projected measurements and verdicts of each scientific camp but explicitly highlights the axes of disagreement—revealing where fundamental assumptions about mass, data geometry, and algebraic symmetries collide.

---

## Introduction to `ASTRO-0002`: The Architecture of the Distant Solar System

The vast expanse of the Solar System beyond 100 astronomical units (AU) remains one of the least constrained domains in planetary astrophysics [cite: 1, 2]. The standard model of Solar System formation posits a collisionally and dynamically evolved planetesimal disk—the Kuiper Belt—sculpted by the outward migration of the four giant planets [cite: 3, 4]. However, the discovery of extreme trans-Neptunian objects (ETNOs) such as (90377) Sedna, 2012 VP113, and (541132) Leleakuhonua has revealed a detached population whose orbits cannot be easily explained by the current architecture of the known planets [cite: 5, 6]. 

These ETNOs exhibit orbital periods measured in millennia and perihelia well beyond the gravitational reach of Neptune (\(q > 50\) AU). More intriguingly, they display a statistically anomalous clustering in physical space, specifically in the orientation of their orbital ellipses [cite: 7]. The alignment of their perihelia and orbital planes points to a missing mechanism in our current dynamical models. This phenomenon, classified in astrodynamic taxonomy as `ASTRO-0002`, has birthed competing theoretical frameworks, ranging from the existence of a massive, undiscovered "Planet Nine" [cite: 8, 9] to alternative theories involving primordial stellar flybys [cite: 6], collective self-gravity of the planetesimal disk, or modified gravity (MOND) [cite: 10].

The following sections systematically apply three candidate theoretical lenses to this open problem. For each lens, the two strongest primary-literature attempts are identified, summarizing the specific measurements projected, the verdicts reached, and the fundamental axes of disagreement with competing paradigms.

---

## Lens 1: `STANCE_DYNAMICAL_SYSTEMS@v1`

The Dynamical Systems lens treats the Solar System as a deterministic, N-body classical mechanics environment. Within this framework, unexpected orbital clustering is inherently interpreted as the consequence of secular gravitational perturbations, resonant trapping, or discrete historical scattering events. The primary mathematical tools are Hamiltonian mechanics, numerical symplectic integration, and secular perturbation theory (e.g., the Kozai-Lidov mechanism).

### Primary Attempt 1: The Planet Nine Hypothesis and Kozai-Lidov Resonances
The most prominent application of dynamical systems to `ASTRO-0002` is the Planet Nine (P9) hypothesis, formalized by Batygin and Brown [cite: 7, 9]. This model proposes that a \(5-10 M_\oplus\) planet residing on a moderately inclined (\(i_9 \sim 15-25^\circ\)), eccentric (\(e_9 \sim 0.2-0.5\)) orbit with a semi-major axis \(a_9 \sim 400-800\) AU is actively shepherding the ETNOs [cite: 7]. 

The dynamical mechanism driving this shepherding is primarily the Kozai-Lidov effect inside mean-motion resonances (MMR). When a minor body is perturbed by a distant, massive companion, the secular variations of its orbit result in periodic exchanges between eccentricity (\(e\)) and inclination (\(i\)), governed by the conservation of the Kozai action:
\[ \mathcal{H}_{KL} \propto \sqrt{1 - e^2} \cos i = \text{constant} \]
Under the influence of P9, objects like 2015 BP519—the most extreme TNO discovered to date with an inclination \(i \approx 54^\circ\)—display rich dynamical behavior, including rapid diffusion in semi-major axis and constrained variations in \(e\) and \(i\) [cite: 4, 11]. The P9 model also explains the generation of highly inclined and retrograde centaurs as a natural byproduct of these resonant interactions [cite: 7, 11].

*   **(a) Measurement Projected**: The primary measurements are derived from \(N\)-body symplectic simulations (e.g., using the REBOUND code [cite: 9]) running over billion-year timescales. Researchers measure the clustering of the longitude of the ascending node (\(\Omega\)) and the argument of perihelion (\(\omega\)), alongside the stability of test particles near mean-motion resonances (e.g., the 3/1 MMR with Neptune) and Kozai secular resonances [cite: 12]. Additional projections involve mapping the allowed orbital positions and estimating the visual brightness of P9 (\(22 < V < 25\)) to constrain future observational surveys [cite: 4].
*   **(b) Verdict Reached**: The presence of an external, planetary-mass perturber convincingly explains the observed alignment of the orbital planes and the large perihelion distances of the Sedna population [cite: 4, 7]. The clustering is not an artifact but a stable dynamical attractor maintained by multi-body resonant trapping over the age of the Solar System.
*   **(c) Axis of Disagreement**: This approach asserts that the orbital anomalies are the result of *missing mass* interacting via classical Newtonian gravity. It fundamentally disagrees with Information Theory models that attribute the clustering to observational biases in telescope pointing [cite: 2]. It also explicitly conflicts with the Renormalization Group/Modified Gravity lens, which views the anomaly not as a missing object, but as a signature of non-Newtonian dynamics in the ultra-low acceleration regime [cite: 10].

### Primary Attempt 2: Primordial Stellar Flybys and Scattering Events
A competing dynamical attempt to explain the extreme TNO architecture without invoking a new planet is the hypothesis of a primordial stellar flyby. In the early days of the Solar System, while the Sun was still part of its birth cluster, a close encounter with another star could have perturbed objects from the primordial scattering disk, elevating their perihelia and detaching them from Neptune's gravitational influence [cite: 6].

Recent primary-literature investigations into this mechanism run highly detailed N-body simulations testing different stellar encounter configurations (e.g., varying the mass \(M_*\), impact parameter \(q_*\), and inclination \(i_*\) of the passing star) [cite: 6]. 

*   **(a) Measurement Projected**: Researchers project the resulting synthetic distributions of semi-major axis (\(a\)), perihelion distance (\(q\)), and inclination (\(i\)) of test particles after the flyby. These synthetic distributions are mathematically compared against newly identified constraints from Sednoid observations—specifically, the requirement to produce a low-inclination (\(i < 30^\circ\)) profile and to maintain a primordial orbital alignment [cite: 6].
*   **(b) Verdict Reached**: The verdict reached by rigorous dynamical constraints is that early stellar flybys are highly unlikely to be the sole cause of `ASTRO-0002`. Simulations show that to meet the low-inclination constraint of detached ETNOs, the passing star must have a nearly coplanar trajectory (\(i_* \sim 0^\circ\)) or be perfectly symmetric about the ecliptic plane. Factoring in the occurrence rate of such specific geometries during the Solar System's early stages, the probability of a stellar flyby satisfying all constraints is less than 5% [cite: 6].
*   **(c) Axis of Disagreement**: While remaining within the Dynamical Systems paradigm, this attempt seeks a *historical, transient* cause rather than a *current, persistent* perturber like Planet Nine. It disagrees with continuous-attractor models (like continuous Kozai-Lidov or continuous MOND) by positing that the current orbital architecture is a "fossilized" state. Its failure to robustly recreate the observations indirectly strengthens the continuous-perturber arguments.

---

## Lens 2: `STANCE_INFORMATION_THEORY@v1`

The Information Theory lens abstracts away from physical masses and forces, choosing instead to view the orbital parameters of ETNOs as a dataset generated by a noisy, biased information channel. This stance utilizes unsupervised machine learning, manifold geometry, continuous Shannon entropy, and information criteria (like AIC and BIC) to determine if the "signal" of clustering is statistically significant, or merely a phantom generated by the survey strategies of Earth-based telescopes.

### Primary Attempt 1: Unsupervised Machine Learning and Mutual Nodal Distance Asymmetries
A prominent application of this lens is the use of machine-learning algorithms (specifically k-means++ and agglomerative hierarchical clustering) to analyze the orbital parameter space of ETNOs without a priori dynamical assumptions [cite: 1, 2, 13]. De la Fuente Marcos and de la Fuente Marcos (2021, 2022) leveraged these techniques to investigate the mutual nodal distances—a geometric metric of how close two orbits can theoretically get to one another in 3D space [cite: 1, 14].

By shuffling the sample of known ETNOs and applying unbiased scattered-disc orbital models, they calculated the shortest mutual ascending (\(\Delta^+\)) and descending (\(\Delta^-\)) nodal distances.
\[ \Delta_{ij} = \min_{\theta} || \vec{r}_i(\theta_i) - \vec{r}_j(\theta_j) || \]

*   **(a) Measurement Projected**: The primary projected measurement is the statistical significance (measured in \(\sigma\)) of the asymmetry between the distributions of object pairs with small ascending versus descending nodal distances. Additionally, they use the k-means++ algorithm and the "elbow method" to evaluate clustering in multi-dimensional heliocentric orbital elements, relying on the first percentile of the nodal distance distribution (e.g., < 1.450 AU) to identify improbable correlations [cite: 2, 15, 16].
*   **(b) Verdict Reached**: The researchers confirm the presence of a massive, statistically significant (\(62\sigma\)) asymmetry between the shortest mutual ascending and descending nodal distances in a sample of 51 ETNOs [cite: 17]. They also identify highly improbable (\(p < 0.0002\)) correlated pairs of orbits with mutual nodal distances as low as 0.2 AU at 152 AU from the Solar System barycenter. The verdict concludes that these asymmetries are far too severe to be caused by observational bias alone, indicating a genuine response to external, trans-Plutonian perturbations (though not necessarily the exact Planet Nine prescribed by Batygin and Brown) [cite: 14, 17].
*   **(c) Axis of Disagreement**: This approach disagrees with classical dynamical systems by not assuming a specific physical cause (like a \(5 M_\oplus\) planet) but instead focusing on the topological geometry of the orbits. Furthermore, it directly conflicts with the subset of astronomers who argue that *all* ETNO clustering is simply observational bias [cite: 2]. By quantifying the nodal distances so rigorously, this lens proves that while bias exists, a true, non-random signal survives the noise.

### Primary Attempt 2: Bayesian Information Criterion (BIC), Latent Spaces, and Observational Bias Penalty
Another powerful information-theoretic attempt to frame the ETNO problem utilizes the Bayesian Information Criterion (BIC) and Akaike Information Criterion (AIC) to formalize planetary taxonomy and penalize overly complex models that claim to discover new sub-populations [cite: 18, 19, 20]. Furthermore, probabilistic latent-space frameworks and continuous Shannon entropy are used to quantify how much true physical information (e.g., spectral composition) is retained in sparse photometric data of TNOs [cite: 21].

The BIC is mathematically defined as:
\[ BIC = k \ln(n) - 2 \ln(\hat{L}) \]
where \(\hat{L}\) is the maximized likelihood of the model, \(k\) is the number of parameters, and \(n\) is the sample size [cite: 18]. When analyzing the clustering of ETNOs, applying BIC allows researchers to mathematically weigh the hypothesis of a uniform distribution (with observation bias applied) against a genuinely clustered distribution (Planet Nine hypothesis) [cite: 13, 20]. 

*   **(a) Measurement Projected**: The primary measurements are the \(\Delta BIC\) and \(\Delta AIC\) values comparing competing statistical models of the outer Solar System. For instance, comparing the likelihood of 2, 3, 4, or 5 independent ETNO clusters. Additionally, continuous Shannon entropy (\(H_k = \frac{1}{2}\ln(2\pi e \sigma^2)\)) is measured to quantify the information retention and variance captured in low-dimensional latent representations of TNOs [cite: 18, 20, 21].
*   **(b) Verdict Reached**: The application of BIC to solar system body clustering indicates that while dynamical dominance is a natural organizing principle (separating planets from minor bodies), applying unsupervised clustering to the current ETNO sample yields ambiguous results heavily dependent on the penalization parameters [cite: 20]. While certain clusters emerge, the rigorous information-theoretic penalty for adding parameters (\(k\)) often renders the "undiscovered planet" models only marginally more statistically confident than models assuming complex observational selection functions [cite: 22].
*   **(c) Axis of Disagreement**: The Information Theory lens inherently penalizes the invention of unobserved variables (such as an unseen Planet Nine) unless the data absolutely demands it. It disagrees with the Dynamical Systems lens by suggesting that the "attractors" found in N-body simulations might just be mathematical apophenia (finding patterns in random data), amplified by the narrow sky-coverage of modern telescopes. It insists on evaluating the *information channel* (the telescope surveys) before declaring a physical discovery.

---

## Lens 3: `STANCE_RENORMALIZATION_GROUP@v1`

The Renormalization Group (RG) lens represents the most mathematically abstract and conceptually radical approach to the `ASTRO-0002` anomaly. Originally developed to handle ultra-violet divergences in quantum field theory, RG has been successfully mapped onto classical differential equations—specifically to handle singular perturbation problems and secular divergences in celestial mechanics [cite: 23, 24, 25]. Within this stance, orbital anomalies are either algebraic artifacts of secular terms that must be resummed, or they are evidence of fundamental modifications to the laws of gravity at large scales (where RG flows generate emergent effective field theories like MOND).

### Primary Attempt 1: Chen-Goldenfeld-Oono (CGO) Renormalization of Secular Terms in Celestial Mechanics
In classical perturbation theory (which governs how planets interact), expansions often generate "secular terms"—terms like \(t \sin(t)\) that grow without bound over time, causing the mathematical approximation to diverge [cite: 23]. The traditional celestial mechanics workaround involves the Poincaré-Lindstedt method or multiple-scale analysis [cite: 23, 25]. However, Chen, Goldenfeld, and Oono introduced an elegant RG method to absorb these divergences into a running coupling constant (amplitude and phase flow equations) [cite: 23, 24].

To apply this to ETNOs, one models the N-body Hamiltonian and identifies the secular divergences. Instead of introducing arbitrary multiple timescales, the CGO RG method introduces a renormalization parameter \(\tau\). The condition that the amplitude flow equation must vanish at each order of perturbation allows one to extract the true, long-term asymptotic behavior of the system—often revealing limit cycles or generalized resonances [cite: 24, 26, 27].

*   **(a) Measurement Projected**: The primary mathematical "measurement" is the extraction of the amplitude flow equations, \(\frac{dA_R}{d\tau}\) and \(\frac{d\theta_R}{d\tau}\), from the divergent perturbation series of the N-body Hamiltonian [cite: 23, 24]. By enforcing that the physical solution is independent of the arbitrary renormalization point \(\tau\) (i.e., the RG invariance condition), researchers calculate the exact period, amplitude, and transient path to limit cycles for conservative mechanical systems [cite: 26, 27].
*   **(b) Verdict Reached**: The RG analysis proves that many orbital systems exhibiting extreme apparent chaos or clustering are actually settling into predictable, structurally stable limit cycles or "Trojan Universality Classes" [cite: 3, 26, 28]. By elegantly resumming the secular terms, the RG flow demonstrates that multi-body resonances (like those experienced by ETNOs) are universal algebraic attractors. Therefore, the clustering of ETNOs may not require a bespoke historical event or a highly specific \(5 M_\oplus\) planet; rather, it is the inevitable fixed-point solution of the RG flow for a dissipatively-weak gravitational system [cite: 3, 26, 29].
*   **(c) Axis of Disagreement**: The CGO RG lens heavily critiques the traditional Dynamical Systems approach. It argues that numerical N-body integrations over billions of years are susceptible to the very secular divergences that RG cures algebraically. Furthermore, it disagrees with the requirement for specific initial conditions, positing instead that the observed ETNO architecture is a universal topological attractor invariant to the exact micro-details of the system's history [cite: 26, 29, 30].

### Primary Attempt 2: Modified Gravity (MOND) as an RG Effective Field Theory Alternative
Perhaps the most controversial application of the RG and field-theoretic lens to `ASTRO-0002` is the assertion that the anomalies are evidence of Modified Newtonian Dynamics (MOND) operating within the Solar System. Under RG flow, laws of physics can change depending on the scale (or acceleration regime). MOND proposes that below a certain acceleration threshold (\(a_0\)), gravity deviates from \(1/r^2\) [cite: 10]. 

Mathur and colleagues recently showed that the MOND galactic field exerts a profound effect within the outer Solar System. Unlike pure Newtonian gravity, the MOND field possesses significant quadrupolar and octupolar terms [cite: 10]. 

*   **(a) Measurement Projected**: The projected measurement utilizes the well-established secular approximation of solar system dynamics, augmented by the MOND-derived quadrupolar and octupolar galactic tidal fields. Researchers project the expected alignment of the major axes of Kuiper belt objects resulting strictly from these modified background fields, calculating the spatial clustering parameters without injecting any dark matter or undiscovered planets [cite: 10].
*   **(b) Verdict Reached**: The verdict is that MOND provides a mathematically self-consistent alternative to the Planet Nine hypothesis [cite: 10]. The MOND field effectively forces the population of distant Kuiper belt objects to align their major axes with the direction to the center of the galaxy. The predicted clustering in orbital parameters under MOND perfectly matches the newly discovered class of ETNOs [cite: 10]. Planet Nine, in this view, is a "Phantom Menace"—an illusion created by applying unmodified Newtonian mechanics in a MOND regime [cite: 10].
*   **(c) Axis of Disagreement**: This is the most severe axis of disagreement in the literature. It outright rejects the fundamental premise of the Dynamical Systems lens (which relies on Newtonian gravity and hidden masses). It also bypasses the Information Theory lens by providing a deterministic, physical reason for the clustering that is independent of observational bias. By shifting the paradigm to an effective field theory generated by the galactic environment, it redefines the entire ontology of the `ASTRO-0002` problem.

---

## Synthesis: The Multi-Perspective Fingerprint

To fully map the landscape of `ASTRO-0002`, we must view these three lenses not in isolation, but as a matrix of intersecting epistemologies. The table below synthesizes the primary-literature fingerprint, highlighting how each lens defines the problem, processes the data, and critiques the other frameworks.

| Feature | `STANCE_DYNAMICAL_SYSTEMS@v1` | `STANCE_INFORMATION_THEORY@v1` | `STANCE_RENORMALIZATION_GROUP@v1` |
| :--- | :--- | :--- | :--- |
| **Core Assumption** | Newtonian gravity holds; anomalies require missing mass or historical physical events. | Data is noisy and biased; apparent anomalies must survive strict mathematical penalization. | Macroscopic orbital phenomena are manifestations of algebraic fixed points or effective field theories. |
| **Primary Methodology** | N-body symplectic integrations, secular resonance mapping (Kozai-Lidov). | Unsupervised clustering (K-means++), mutual nodal distances, AIC/BIC. | CGO RG amplitude flow equations, MOND quadrupolar galactic fields. |
| **Explanation for ETNO Clustering** | A distant, unseen \(5-10 M_\oplus\) planet shepherds the orbits via mean-motion resonance. | A mix of profound geometric asymmetries (\(62\sigma\)) and observational telescope bias. | Universal topological attractors or the breakdown of Newtonian gravity at low accelerations. |
| **Primary Metric** | Kozai action \(\sqrt{1-e^2} \cos i\), semi-major axis \(a\), argument of perihelion \(\omega\). | \(\Delta BIC\), Shannon Entropy \(H_k\), shortest mutual nodal distance \(\Delta_{ij}\). | RG invariant coupling constants, MOND acceleration threshold \(a_0\). |
| **Critique of Other Lenses** | RG/MOND is an unnecessary modification of fundamental physics; IT ignores basic gravitational physics in favor of pure statistics. | DS overfits data by inventing unobserved planets; RG is overly abstract and ignores empirical telescope constraints. | DS relies on flawed perturbation theories or ad-hoc planets; IT fails to recognize fundamental algebraic structures underlying the data. |

### The Axes of Friction
1.  **Determinism vs. Probability**: The Dynamical Systems approach is heavily deterministic. If Planet Nine exists, its exact orbit can theoretically be traced backward and forward [cite: 4, 9]. The Information Theory lens introduces stochasticity, arguing that the true state of the outer Solar System is obscured by a probabilistic veil of selection functions [cite: 2, 20].
2.  **Missing Mass vs. Modified Mechanics**: The tension between Planet Nine (Dynamical Systems) and MOND (Renormalization Group) is a classic manifestation of the dark matter debate applied locally. Do we trust the laws of gravity and invent a hidden object, or do we observe the objects and modify the laws of gravity? [cite: 10].
3.  **Numerical Integration vs. Analytical Asymptotics**: Dynamical Systems relies heavily on brute-force computer simulations running billions of years of simulated time [cite: 6, 9]. The Renormalization Group lens distrusts this, utilizing CGO RG methods to analytically bypass secular divergences, proving that these systems naturally flow toward "Trojan Universality Classes" regardless of micro-initial conditions [cite: 23, 26, 29].

---

## Conclusion and Future Directions

The open problem `ASTRO-0002` remains unresolved, serving as a profound stress-test for modern astrophysics. By projecting the problem through three distinct primary-literature lenses, we achieve a comprehensive fingerprint of the current scientific frontier.

*   The **Dynamical Systems** lens continues to refine the search area for Planet Nine, predicting a faint (\(V \sim 22-25\)) object near aphelion that could be captured by upcoming deep-sky surveys [cite: 4, 7].
*   The **Information Theory** lens demands increasingly rigorous debiasing of observational data, highlighting that metrics like mutual nodal distance asymmetries already provide \(62\sigma\) proof of non-random structure, even if a single "Planet Nine" is not the sole cause [cite: 14, 17].
*   The **Renormalization Group** lens forces a fundamental philosophical question: is the outer Solar System the premier local laboratory for testing Modified Newtonian Dynamics (MOND) and universal topological attractors? [cite: 10, 29].

The forthcoming deployment of next-generation observatories, specifically the Vera C. Rubin Observatory's Legacy Survey of Space and Time (LSST), is poised to break this theoretical deadlock. By drastically increasing the sample size of known ETNOs and minimizing localized pointing biases, LSST will either provide the raw data required by Information Theory to erase the anomaly via BIC penalization, uncover the elusive missing mass demanded by Dynamical Systems, or reveal an orbital architecture so universally aligned with the galactic center that the Renormalization Group's MOND hypothesis becomes impossible to ignore.

**Sources:**
1. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSuw1n7sZoDyPhetpm9tNSkQyfuJvBlbfwrPVRi8s1-YTV7Fr66wpwE-VEFMlJJ1AS9RgRyq4Wbkc3POiwXmXAXimWXS5agRFMhvdvHC9I86sY1jjEkVqGrNx0PXYDMEimeL8PQOv3_QsGAoDJahtGBe6mAV2By2shNs1yXhRnMR95ElTpILcJvwHCvcBY50TdGE2TZUSqTJGtU10WDc8JEgLdOfQDuUAh)
2. [ucm.es](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlPCJ74YWzCv2gSO-_1ubhIxY9GqJ0UJfG9UUsf2JGJW7bFIVcfOzLE9_87_MUTWaVhVAbwGF8cBgpHtZ5vIf-JylStOXweGR5xIRXvu_mF6J82MqXm1XYQVFrPKjJ2INTIzlbu6zHQd1D-P2EBzx9x4hIZYbPpfJ9jiIMXF8w8Kmf3A==)
3. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHi5UzVzedwEaMKDJYzC0d_UViws_CkWHglKucuA-zGhkvVZTDW_TqgUX0B8eyeqFSR2DNpi_zn_KiMXfkt2-0HdOZA8osaOOxqn3KuxpOJ7q_w3IBt1V85dJnYgHtLH_thmQSDifpDUusoEE3es85H4ssNu27qdLESZ9cKugxxAeMR_Q8DDDbQL1cbxlzdHLPkSeSK6R3bXuSAmNyDkX7UuaRSXh9bWbFBWnIduct56nuBQKBDnRVckZgreRg8kRN4YrjNf0IJz9_W-citA0hBi4gOLBLg4S6zIIwpMM9-)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHF78lbmv7AlesndMcPZ07GG73lNB-BWzOMpI_-QmHbIkGb5BIt37eV8_kL0_S_u_gjryfo0Lujxvdx4O4UgS93GJdYLkEbGllUiLOFp0jErhTCZsxhfqmVVWTrYbkr_mSU3ZiArZpwGod7WLIvOOqESRTRKiZbBT2fChvE0wzy3OD-ow==)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtGmOP7yKO2w8768Has4fdazbCzRvUEeW_CmbSzhUF3PVu9U-zd3xsr8UBcvFdLH8MPoUveS1-xRYbNuTALy4WEeT9PdWb0t7a8IsdmDhbyMAsMcSoJd0JM3hl2KZaapzwL2lsVJG4L4dSZmGgJ731pd39zqlnf0vLJT0C3wAQz4mhV9gq7UtLGfT4s0sdTbR21KkIcmwe1Pa3XCFQPt00fXbIT_Ac0t9dS8JUNxD-kuQ=)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4RLp4mv99D2onQnCmfj1ALzovpry2pvAQG1JlJ-BpBOJhipWyTLBKHwYrnSBnChBNDT836lhpHXRGH8EFB9n3xdCvCItN71msWv096_SM0JVLyOyyVl6FCMUctsDymQe96Zb5XwaoXTrPNMdOyNUNi70et77VPN6MCuF0hWSDltuQqCaKFhtEMQhWOcx2KZKkmT39pkt49A5ABRw_zLmM0DTfqiMc1PASGCr5HQE9ftm6SfrE_r8bX4xR37X4mg==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5EubC-TaNjKrdmrSjoxffOzoR5WEnY3YVjGf5zyLwKyDE6kKxlUyqJfGJWvo1um_kHD8hiITQq5DExnHpXuQT5qvYXYvQnGnFXDqta7sU5IkZneFVQIMKxLi73nVTJjttiA==)
8. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFU4Dxd55abahs53mj6bkh6ajVRALC4Wj9gD3g-W5Hn2uTGCuv2VmNZnZ5ge7yyBVBJommCVClP5dwjqc5z2q3G0ceJIhaXsUzQV1rxotzvbz1LQb0TstAVx4woDBD20FSrgSqz_-L1DxEbf-_-KMoULbDUf2k7tNLW5tkXePwSYw==)
9. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrjePL1VZW3Pivgr1dIXjH-kHtDnd5d_5fxsT6KCfKuh4dj6_8n9WN-BSyqmuoE2piMRwLWaTGM1rThQYMzrP0mxv9r1JTmBS9OwcXqN7VXe66BSrs5lfm)
10. [pirsa.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQER_cTnAK8opN9JrHegPcUbLhQ66wBLtYBojJtDO73RrYh4NksOz8IEi6FA_tCN919oFLT32Axf3w3dr8AHYMMMbS-JFjrje1rl4RaWi8_Wng==)
11. [eppcgs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFobh0ENr1L2FGj2VKT7SJb2kTB4kZavdSLMzXrwnnqB-jsz0lJFcR-4DYNhYMri0DgA2QjJG95DgTRk8ASOpQPpTOm5nFKwM_FgP38tt7PKUF4F2pSrOy9wEI-e6WVsprKh8nJpKkkMSKQEQ==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUjgL1yfqVTVaU3FonQYuAxvDL5G8rEa9dhMwWWkyd_xAyJmfxCzCTAxqPzAsGQmGrDkHrGTDVOQBFPiQNOglja9QGTNOWTFOqHA1DOeR2wrgiXGLEBQ==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHO5SbiDFOOeAioDvq6c44DN7rLY6nk0TrygOj4WUJn4P8zsYsK2UOptteKCoTp5sZ3O4n7_Qf3668mrHSmEv7COt2Rz_JwUTV5tiUGikm9vkW1gcpKFg==)
14. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjYYD5w1SO2ImKUzcBW372vSpdklIVjdWy-GmEryTvEE4TP5QrMQq83BqBQ1IMOnunEoHKZwR4vrQw_Z-pCW2A7Y2p7Ajt_EUUb3IB4xfvLgfxEzvxzXj586AjVNvVRxTRRDETFujbVTkF7cnMS800GwLvQAM-1Q==)
15. [ucm.es](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6PUClHumjwCQ1r7Y6ZkDGdWuWKct8D1422g4o-QArNbCBFmqxd9YOYSCm_smLfXha4I2kPcH6z7Bb-9kHClcJeY3XTBiBVcMIb-z7GQBznFg1Hnz0kcxgUSvUsqTIWfhz_Hz5raUobPVrFduvJImcn6eHM_3jjzODNama10jmw1TiFQ==)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-X5JcQ5PZoot89T6C5l_CN5UDdHWiWUJvNV48cQJmgRbMWOyFVYd6fD_YNc26GbXUu0gqJcHNmnsyeIjHNCksAzLEHEfjQLLHAEbISKbjjWlw2wLzYJf0G39DVl-7b2BxC5FdUhDmxgqx9MkqGD0tinLPq9jHDVVP-atM8iSpTSQB-5VlRyuVrXhj2ehUexDPqsSptl-OxcjulQ4=)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgs8zo7s8cCI9NLt8VCR2Q2iCcAN2VDB0SyQ-ySmn4a27w1rvVDN_vJTJ5dQUbOBSJwcAK_0Z3ZNNMl9KNog5mSBpww33b1xfLYk-UfWADwrR-6ZPHfQ==)
18. [uni-muenchen.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZ_AIabbbw6PB2eOa3-ImILMDpK4B7GchmiyZlXa-pHvY9LyX8vR3LC6KySNT8cLpcarudK78IfavcmDFHnE6kh_-aP5xG0-dNiZTiaksUeewn-3nPFivY3ymcpnE_TPnQUzGt62V25Pv_ETwJaE22Thiqv8scqJ3N0Z-OI5hCOs0=)
19. [yale.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5Hg1T67iJnHniPcSVZrt52pVuGU2LsbjYR_7gff1cRjuZelV9vGvnMVvoymPHbq58FTj68-lsw9Vjws8QM5GlfTdeZJF2spUK6ZdhqauJp-JshADwCEnWA8OcyWNZ9IzjO7LUa9tOvcggt1Tq8s_xskPvUfAl0420_YJCbdJOHZaCPiqPU6gMxhNeZIB-PzP2YaKx3roCnvEx9sMddpx72ntRkrNH8VFwhlrH)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFw8UAanaf8ZGoWvLLadoK2oeYTosrjWPXdVtx48TiPtBO9i1TdwPDut8Uyf8QaQFVFVwubx20xQg5cmSuo-7zdit5-8PwUHWB4snxqYMQhJe-Ma5_W5kQlXSLiHvU5gvxAqjkjL9HPZNqY_LhDNefWwIAHUIFeLlML8OI4ss9Cp59AbAyAAE83WJY_bgSOguXsDiA=)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6IUixHoTff8SyObb9VlatuiIHFUETrO758Yt5jo95XIAYjdPvGSdZbfbJTshT5Vjanvnrjk2TvEW1JeKECrl_NXtJ_mRbzOWwFgQ4Qd3obpuOiobyTbDwvg==)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-SMSUnCXVQVK1n8DwXP5dxG_iRvk5Fc93zuHFkLksFRsruDtdHzrDgbDLbSy5VdTDQd9vwALbot3WN1ZJfLMfaMDAlumon4Jt9xbANAGvJ8xXpLQWsQ==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFs6BXAAu5x24FOWKUiyy1-fnzPH0xmgTL3CPDpOBQX1FkUsu8INKrfxUpWMenwYEsKvXk3cAh6gjo3BAGxvULBOa4drIR03cxPeO29V9s5JBHc9kjP)
24. [aip.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvCg4p3SCBvqzhTVRwRIFhZFq8-WHFDUBpYSSiBfDrk1rbFSSDdsNYBJIkfEDO9Y3dVo4sdgYEK7RiYdgU_MyN7Zaf7YmyZhik7GfQ78Pz--NjnY4RYGr2NNo1OSF8O_HiCeYaWuRYPXijRcaPbDroCHm-95MJIaM6E8eVQ7VpBFmptfsr41yTfP3IKS2VCjm16U44BHJbpA==)
25. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBP_jxOQ2eSKOFftQUMweP_qnWfo8Z-vr_4paUe2mfv7wFpOwaGFujJP9LG9FkzkRHzw4fs8C6X69BtBNeBYg_q6LnScU0z4fqM2lUEboe4UIaF698ixaRbDgqK57YLsgvQ8W8-7NJlNwcyiXVDfEMETY9AtfxKThXXi6GXTjW94yUZA==)
26. [itp.ac.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE0rw1V_dQoyyySobKWwLgedfhCb4-5XqxqaX8DiZuIkgJdL0NlmlgfjfVO3kHLyMVMNvswf_CMOV_uVNMrWcTSO7yIrtmKfhdJ8MtnbQh3bWXQrLzkBxEsgiEe618Im89f3W3GsprOBCZOdQ==)
27. [bose.res.in](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0U4hTi38_2rprg6_2w5bjWBDf0BchyhIa-gGAyQLpP7j-bz1GJ2sATsUAZcpZlQ-N77-d3Faf6xyaeK3GDZ-YzCjykG1q9yelxK_cv4YIzts5iPsYCVdiqAlye1XfwDnhSmm57cQ3LxObBqHCjYS-hfmrSM76hMd83nxig5ze_rhMYX595ERjY7ixc6uRqNsk2oQ-SdPyslHDlFr-oko=)
28. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRo4oqTAZbKKlLR-5DruUSBIVBVQa7mKtjwD5QvK93w-f7MURVclG7F4FPA-L4BlJid5fvuWBAsOuUywH7Uy6wu_viW27M5slnovhgBhxlCq4KrZS3a0d8i0At8u8T0WdR4ZJhvik=)
29. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJ5lqjsIANNZvV26USYx_YAgXiBAVoZjFIRi3dLN-WVpRMI8fFS006O0X4sOQmmH7_3KfAgdFjFbhIZJ82BV7hQb5NOThqByNQY7BJQCcDXka-tV2WeiIbd8LbuUA026H673MGGANokpPdtkBqHWQApOeVppCE-_QuQusKt4KXEBg-jf9548acQBwz8rBAlPmcvumcHQo4NexZkbxwXSU1d8NR8YKU_3RWgH-YnKV4sl8IwppuJzvu8-pA1oLfprZpdYup4Ws=)
30. [cornell.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6fPeXbgqmsUHdEodm5qkJqTObEF_5cwr4J0z4fb-v4ELkqMEWwENwCSXuyhxqegAzXsCB6SiiHW2Frqy0wyfUiIRDW3y-jwBjG6yBfaZ_6NurPZJjT4OBKfS5q8r762-xHbubtYqAWLo=)

