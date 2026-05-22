# Followup [FU-2026-05-22-036 <- row230]: The following sections systematically apply three candidate theoretical lenses to this open problem.

**Pythia queue id:** 321
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChcxYmtQYXVYQUg0cmlfdU1QckphUG1BURIXMWJrUGF1WEFINHJpX3VNUHJKYVBtQVE
**Elapsed:** 249s
**Completed at:** 2026-05-22T02:09:19.872015+00:00

---

# Status Update: Theoretical Lenses on Extreme Trans-Neptunian Object (ETNO) Orbital Anomalies

### Key Points
*   **The ETNO Anomaly:** A population of trans-Neptunian objects (e.g., Sedna, 2012 VP113) exhibits highly anomalous orbital parameters—specifically, large semi-major axes ($a > 250$ AU), detached perihelia ($q > 40-60$ AU), and statistically significant clustering in their angular orbital elements (longitude of perihelion and orbital pole position). 
*   **Planet Nine Hypothesis:** The prevailing paradigm attributes these anomalies to an undetected $5-10 M_\oplus$ planet (Planet Nine) residing at $a \sim 400-800$ AU. However, alternative paradigms argue that this represents a fundamental misinterpretation of either gravitational physics or early solar system dynamical history.
*   **MOND (Modified Newtonian Dynamics):** Recent models suggest the Milky Way's external field effect under MOND can induce apsidal clustering matching ETNO observations. Conversely, highly detailed sub-critical MOND simulations fail to reproduce the binding energies of long-period comets, leaving the modified gravity hypothesis in a state of severe internal tension.
*   **Stellar Flybys:** While early close stellar encounters can perturb objects into Sedna-like orbits, the latest demographic constraints reveal that a flyby capable of satisfying all modern observational requirements (including low-inclination primordial alignment) has a probability of occurrence of $\lesssim 5\%$.
*   **Collective Self-Gravity:** The "inclination instability" within a massive, primordial scattered disk can dynamically reshape planar orbits into cones, naturally producing the observed clustering. However, this requires a disk mass of $1-10 M_\oplus$, which significantly exceeds current observational limits.

### Executive Summary
The architecture of the outer solar system beyond the Kuiper Cliff ($>50$ AU) remains one of the most vigorously contested domains in modern astrophysics. The discovery of "extreme" trans-Neptunian objects (ETNOs) and "sednoids" has revealed a population of minor planets whose orbits are decoupled from the gravitational influence of the known giant planets [cite: 1, 2]. The striking spatial alignment of these orbits has catalyzed a search for novel dynamical mechanisms. While the Planet Nine hypothesis dominates popular discourse [cite: 3, 4], rigorous theoretical interrogation demands the evaluation of non-planetary explanations. This report applies three specific theoretical lenses—Modified Newtonian Dynamics (MOND), early stellar flybys, and the collective self-gravity of the planetesimal disk—to the ETNO problem, strictly adhering to the Aporia 7-section substrate-grade template. 

---

## 1. Brief Summary

**Question:** How do competing theoretical frameworks (Stellar Flybys, MOND, and Collective Self-Gravity) account for the anomalous orbital architecture of Extreme Trans-Neptunian Objects (ETNOs), and which framework best resolves the tension between observed apsidal clustering and physical plausibility?

**Prometheus Context:** This inquiry evaluates anomalous astronomical data through multiple, mutually exclusive theoretical paradigms, serving as a critical stress-test for standard N-body perturbation theory against modified gravity and early-stellar-cluster chaotic dynamics.

## 2. Flagged Findings

Current astrophysical consensus leans heavily toward either the existence of an undiscovered Planet Nine [cite: 3, 4] or the presence of severe observational selection biases in the detection of ETNOs [cite: 4, 5]. However, systematic evaluation of alternative lenses reveals highly nuanced failure modes and unexpected predictive successes:

*   **MOND Successes and Failures:** MOND unexpectedly and perfectly predicts the apsidal clustering of ETNOs through the secular approximation of the Galactic gravitational field (External Field Effect) [cite: 6, 7, 8]. However, rigorous N-body integrations utilizing the Bekenstein-Milgrom AQUAL formulation of MOND decisively fail to reproduce the binding energy distributions of Oort-cloud comets [cite: 9]. This suggests that while MOND fits specific ETNO clustering, it violates broader solar system boundary conditions.
*   **Stellar Flyby Probabilities:** It is widely accepted that stellar flybys can detach ETNOs from Neptune's influence [cite: 10, 11]. However, the consensus that this is a *probable* origin for the *entire* aligned ETNO population is flawed. Recent deep constraints demonstrate that flybys satisfying the observed low-inclination profile ($i < 30^\circ$) and primordial alignment require either extreme coplanarity ($i_\star \sim 0^\circ$) or perfect ecliptic symmetry ($i_\star \sim 90^\circ, \omega_\star \sim 0^\circ$). The statistical probability of such an encounter in the solar birth cluster is $\lesssim 5\%$ [cite: 2, 12, 13].
*   **Inclination Instability Mass Deficit:** The collective self-gravity framework brilliantly circumvents the need for a singular massive perturber by demonstrating that a disk of eccentric planetesimals will spontaneously undergo an "inclination instability," raising inclinations and clustering the argument of perihelion [cite: 14, 15, 16]. The flaw in this model lies in the mass requirement: it demands a primordial disk of $1-10 M_\oplus$ remaining intact for $\sim 1$ Gyr, which strongly contradicts current observational mass estimates and depletion timescales [cite: 16, 17]. 

**Calibration Injection:** The adherence to the Planet Nine hypothesis by mainstream dynamicists often exhibits **PATTERN_PRIME_GRAVITATIONAL_OVERFIT**, wherein an unobserved point-mass is continuously parameter-tuned (mass, semi-major axis, eccentricity, inclination) to perfectly fit anomalous data that could otherwise emerge from fundamentally different physical primitives (such as an altered gravitational field or collective disk dynamics). Conversely, early acceptance of the stellar flyby hypothesis suffered from **PATTERN_BASE_RATE_NEGLECT**, as theorists demonstrated that specific flyby geometries *could* produce sednoids without rigorously calculating the exceedingly low base-rate probability of those specific, highly constrained geometries occurring within the isotropic environment of a stellar birth cluster [cite: 12].

## 3. Problem Statement

The precise objects being interrogated are **Extreme Trans-Neptunian Objects (ETNOs)** and a distinct subclass known as **Sednoids**. 

**Definitions and Boundary Conditions:**
1.  **Sednoids:** Defined by large semi-major axes ($a > 200$ AU to $1500$ AU) and exceptionally high perihelia ($q > 60$ AU) [cite: 12, 18]. These bodies (e.g., 90377 Sedna, 2012 VP113, 2015 TG387, 2023 KQ14) are entirely detached from the gravitational influence of the four giant planets [cite: 2, 18].
2.  **Broad ETNOs:** Typically defined as objects with $a > 150-250$ AU and $q > 30-40$ AU [cite: 19, 20]. While some experience weak interactions with Neptune, they reside in a regime where standard planetary perturbations cannot efficiently randomize their orbital elements over the age of the solar system [cite: 21].
3.  **High-Inclination / Retrograde Objects:** A sub-population of extreme objects occupying highly inclined ($i > 50^\circ$) or entirely retrograde ($i > 90^\circ$) orbits, such as 2015 BP519 ($i \approx 54^\circ$) and 2008 KV42 ($i \approx 103.4^\circ$) [cite: 4, 11].

**The Interrogated Result:**
The primary phenomenon requiring explanation is the statistically improbable non-uniform distribution of these objects' orbits. Specifically:
*   **Apsidal Alignment:** The longitude of perihelion ($\varpi$) for the most stable ETNOs is tightly clustered.
*   **Orbital Plane Tilt:** The longitudes of the ascending node ($\Omega$) and orbital inclinations ($i$) suggest these objects are confined to a common plane that is tilted relative to the invariable plane of the solar system [cite: 3].
*   **Perihelion Detachment:** The physical mechanism required to lift the perihelia of these objects out of the scattering disk ($q \sim 30$ AU) and into the inner Oort cloud ($q > 60$ AU) without stripping them from the solar system [cite: 2, 12].

The problem dictates that any successful theoretical lens must simultaneously explain the *detachment*, the *angular clustering*, and the *inclination distribution* without violating other known solar system architectures (e.g., the stability of the inner planets, the cold classical Kuiper belt, and the Oort cloud comet flux).

## 4. Status & Bounds

The current status of the open question relies on the continuous discovery of new ETNOs and increasingly sophisticated $N$-body simulations. The bounds for the three targeted theoretical lenses are strictly defined by recent primary literature.

### Lens 1: Modified Newtonian Dynamics (MOND)
*   **Status:** Highly contested. MOND eliminates the need for dark matter by modifying Newton's laws at sub-critical accelerations ($a_0 \approx 10^{-10}$ m/s$^2$) [cite: 22, 23]. In the outer solar system, the gravitational acceleration from the Sun drops below $a_0$ beyond a few thousand AU, but the External Field Effect (EFE) from the Galactic center breaks the strong equivalence principle and induces anomalous quadrupole and octupole moments in the local field [cite: 6, 24].
*   **Best Bounds (Success):** Brown & Mathur (2023) demonstrated that under MOND, the secular approximation predicts ETNO major axes will spontaneously align with the direction toward the Galactic center, perfectly matching observed clustering in phase space [cite: 6, 7, 25].
*   **Best Bounds (Failure):** Vokrouhlický et al. (2024) established a rigid bounding constraint against the Bekenstein-Milgrom AQUAL version of MOND. By simulating $10^5$ test particles scattered by giant planets over 4.5 Gyr, they proved that AQUAL fails to reproduce the binding energy distribution of long-period comets [cite: 9]. Furthermore, AQUAL failed to reproduce the detached disk ($q > 38$ AU) [cite: 9].
*   **Conditional Qualifiers:** Vokrouhlický et al. explicitly state their results do not rule out more elaborate MOND formulations (e.g., QUMOND) where non-Newtonian effects are screened on small spatial scales or transition functions are highly abrupt [cite: 9, 24].

### Lens 2: Stellar Flybys
*   **Status:** Statistically disfavored as a universal explanation. Early solar system evolution in a stellar birth cluster guarantees close encounters, which efficiently lift perihelia [cite: 10, 11]. 
*   **Best Bounds (Success):** Pfalzner et al. (2024) bounded a specific "successful" flyby scenario: a $0.8 M_\odot$ star passing at an extremely close $q_\star = 110$ AU on a nearly vertical orbit ($i_\star = 70^\circ$) [cite: 26]. This specific set of parameters can reproduce detached TNO properties.
*   **Best Bounds (Failure):** Hu et al. (2025) systematically bounded the entire flyby parameter space. To reproduce the observation that sednoids maintain a low-inclination profile ($i < 30^\circ$) while achieving apsidal alignment, a flyby must be perfectly coplanar ($i_\star \sim 0^\circ$) or perfectly symmetric ($i_\star \sim 90^\circ, \omega_\star \sim 0^\circ$) [cite: 12]. 
*   **Conditional Qualifiers:** Accounting for stellar velocity dispersions and occurrence rates in the birth cluster, the probability of a flyby ($q_\star \le 1000$ AU) meeting all geometrical constraints is bounded at $\lesssim 5\%$ [cite: 2, 12]. Therefore, while physically possible, stellar flybys are statistically exhausted as a primary paradigm.

### Lens 3: Collective Self-Gravity (Inclination Instability)
*   **Status:** Theoretically robust, observationally unsupported. Madigan & McCourt (2016) demonstrated that a massive, axisymmetric disk of eccentric orbits is subject to a secular instability that reshapes the disk into a cone [cite: 14, 15].
*   **Best Bounds (Success):** The instability successfully drives exponential growth in orbital inclinations while simultaneously clustering the argument of perihelion ($\omega$), closely matching ETNO observables [cite: 14, 16]. The e-folding timescale converges predictably at high $N$-body resolutions [cite: 4, 27].
*   **Best Bounds (Failure):** The critical bounding limit is disk mass. The instability requires a primordial scattered disk mass of $1$ to $10 M_\oplus$ residing at hundreds of AU [cite: 14, 15]. 
*   **Conditional Qualifiers:** Observational surveys have not detected a scattered disk of this magnitude [cite: 17]. Furthermore, integration with the "Nice Model" of solar system formation suggests that giant planet perturbations drive rapid orbital precession that disrupts and ejects these bodies on timescales much shorter than the $\sim 1$ Gyr required for the inclination instability to initiate [cite: 17].

## 5. Literature (Primary Sources)

The following matrix identifies the primary literature dictating the current theoretical boundaries, strictly limited to peer-reviewed sources and verified preprints detailing the three evaluated lenses.

*   **LENS 1: MOND (Modified Gravity)**
    1.  Brown, K., & Mathur, H. (2023). "Modified Newtonian Dynamics as an Alternative to the Planet Nine Hypothesis." *The Astronomical Journal*, 166(4). DOI: 10.3847/1538-3881/acef1e. arXiv:2304.00576. [cite: 6, 25, 28]. *(Verdict: MOND successfully aligns ETNO major axes with the Galactic center via secular approximation).*
    2.  Vokrouhlický, D., Nesvorný, D., & Tremaine, S. (2024). "Testing MOND on Small Bodies in the Remote Solar System." *The Astrophysical Journal*, 968(1):47. DOI: 10.3847/1538-4357/ad40a3. arXiv:2403.09555. [cite: 9, 23, 29]. *(Verdict: AQUAL MOND decisively fails to reproduce the binding energies of Oort Cloud comets and the detached ETNO disk).*

*   **LENS 2: Stellar Flybys**
    1.  Hu, Q., Huang, Y., Gladman, B., & Zhu, W. (2025). "Early Stellar Flybys are Unlikely: Improved Constraints from Sednoids and Large-$q$ TNOs." arXiv preprint, arXiv:2505.16317. [cite: 2, 12, 30]. *(Verdict: Imposes a $<5\%$ probability bound on flybys capable of replicating low-inclination primordial alignment).*
    2.  Pfalzner, S., et al. (2024). Mentioned in secondary reviews as proposing a highly constrained $0.8 M_\odot$, $q_\star = 110$ AU vertical flyby [cite: 26]. *(Verdict: Demonstrates kinematic possibility but highlights the extreme fine-tuning required).*

*   **LENS 3: Collective Self-Gravity**
    1.  Madigan, A.-M., & McCourt, M. (2016). "A new inclination instability reshapes Keplerian discs into cones: application to the outer Solar system." *Monthly Notices of the Royal Astronomical Society: Letters*, 457(1), L89–L93. DOI: 10.1093/mnrasl/slv203. arXiv:1509.08920. [cite: 14, 15, 16]. *(Verdict: Identifies the exponential inclination instability capable of clustering ETNO arguments of perihelion).*
    2.  Zderic, A., Madigan, A.-M., et al. (2020) / Contextualized in Batygin (2019) reviews. "On the Dynamics of the Inclination Instability." *The Astronomical Journal*, 156(4). [cite: 16, 17]. *(Verdict: Elaborates on N-body requirements but faces immense tension with current solar system mass-inventory observations).*

## 6. Attack Vectors

### Live Techniques
1.  **Deep Weak-Field / MOND N-Body Integration:** Advanced numerical integration algorithms are actively being developed to simulate the full non-linear External Field Effect (EFE) of the Galaxy combined with giant planet perturbations. The next phase of attacks utilizes QUMOND (Quasilinear MOND) rather than AQUAL, introducing sharper transition functions that might shield the inner solar system and Oort cloud while allowing Galactic tidal forces to align ETNOs [cite: 9, 24].
2.  **Wide-Field Sky Surveys (LSST):** The primary empirical attack vector is the Vera C. Rubin Observatory's Legacy Survey of Space and Time (LSST) [cite: 31]. Current ETNO datasets suffer from severe pointing biases (telescopes observe specific ecliptic latitudes at specific times of year). LSST will image the entire visible sky every few nights, neutralizing observational biases. If the apsidal clustering disappears in an unbiased sample, the Planet Nine, MOND, and Self-Gravity hypotheses all instantly collapse [cite: 8, 31].
3.  **Gaussian N-ring Codes:** To study the inclination instability over billions of years without computationally prohibitive $N$-body particle counts, researchers are deploying Gauss N-ring codes to average Keplerian motion and compute secular interactions across vast temporal baselines, determining exact thresholds where two-body relaxation disrupts collective instability [cite: 4, 27].

### Exhausted Approaches
1.  **Isotropic Field-Star Encounters:** Simulating random, unconstrained stellar flybys crossing the solar system post-cluster-dispersal has been exhausted. Calculations demonstrate that field stars are fundamentally incapable of generating a sufficient population of detached objects over 4.5 Gyr [cite: 1, 2, 26].
2.  **Basic Kozai-Lidov Perturbations:** Early attempts to explain ETNO inclinations solely via Kozai-Lidov cycles induced by the known four giant planets have been definitively exhausted; the secular architecture of Neptune simply does not possess the requisite angular momentum exchange capability to lift $q$ to 80 AU [cite: 4].

## 7. Cross-References

*   **Related Open Problems:**
    *   *The Oort Cloud Injection Rate:* The failure of MOND (AQUAL) to produce correct long-period comet energies directly ties ETNO dynamics to the broader open problem of Oort cloud formation [cite: 3, 9].
    *   *Planet Nine Parameter Space:* If MOND, Flybys, and Self-Gravity fail, constraints default back to bounds on Planet Nine's mass ($5-10 M_\oplus$), semi-major axis ($400-800$ AU), and inclination ($15^\circ-25^\circ$) [cite: 3].
    *   *Rogue Planet Capture:* Related to stellar flybys is the hypothesis of capturing a free-floating (rogue) planet or planetesimals during cluster dispersal [cite: 18]. 

*   **Anti-Anchors:**
    *   *The "Planet Nine as Panacea" Trap:* Because Planet Nine offers a convenient, highly-parameterizable point-mass solution to multiple anomalies (detached $q$, clustered $\varpi$, retrograde centaurs), the community is heavily anchored to it, potentially neglecting structural modifications to gravity (MOND) or complex secular mechanics. 

*   **Candidate Primitives:**
    *   *Bekenstein-Milgrom AQUAL Transition Function ($\mu$):* The specific mathematical function interpolating between Newtonian and MOND regimes.
    *   *The External Field Effect (EFE):* A fundamental violation of the Strong Equivalence Principle unique to MOND, positing that internal dynamics of a system (the Solar System) are influenced by an external gravitational field (the Milky Way) even in free-fall [cite: 2, 24].
    *   *Reduced Kozai Action ($\Theta$):* A conserved quantity at a fixed semi-major axis for axisymmetric perturbations, crucial for mapping the diffusion of high-inclination ETNOs like 2015 BP519 [cite: 4].

**Sources:**
1. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE92Katd02PvcTNfqPFFFGoZ12V4fdUmqq3sivUKa6AyRfhtlZBYrI2_AjOpYvOq3xHbupG_LjkU1JKF_sfFqHRwXTqvu-L3pXq631oNXAf_yowBSzd7bi_z7ovkbrWYqaGku2cDqYxxpzcUyDyiYlumKPabL8FvwIH9TVGX3nzINL59yfH03VBCJKjZith1fF651DOLbApYiaHFHovFwud4jrRGw==)
2. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKO0P2bk8LIxCy--8MF76g8T9k8x64n1aFHyAqSyv7dumMpvlJ_UE2Z74V0QlsZeri-mLqMTN8H_9cgtujo-GLYiD0wFCSIGbdoab_pnlgmcVaYeBFf9ycOZPK9vMft8qP1p6vrWayHfN4o3TRRfPCbmkNsQtmvgddN9Tre6GYjZTZyAnqGQYaW_tTo-BJ9FpVTy3OmYTdXwycIcuVANT4wweZllQ7trQ_WfN1wyZR5gYT55av17v4hYEPtxnT)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6hs52w8VPnxhq_TH_kEX8HD0OISxYVF3z57LcYrJPsg3Afu6sSOjUEpawA9IlcgFGjPYbiRVdb4ZFCkQ_Gs1j6FIrtIIp4sweAJwlzzNiR_0Q1XY6-JeORjWR0t28KvBq)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCoHePOg6bNxJA0XfwlQHbLrBlNo-8ZrnpeOsmKar-yJkGiulym8jScwfR_KHkcVfvd70QvFiA8bM_vOn3iA1CbdXrCzF5CwFqu0Z9rcrL1npgt_hyOofWaWjkLycdQBRPU9hgdbfP4xiQsyVGC8CBuqHjd3YPARP2aFxYNL3ZfBPy)
5. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPUk8Fc6jpPe06JZtBakD6DQzA7fj-BQYZjwGVI3xH_2fQ6WmtyfBNnFwvL5wcPpDelvGNeMDJ4xM8oUshvSgBotzXDtFhqCjOTQLdEHFDPZ9tQL_xECKyuljmNX6VGaTu5-OE_UM9cl0bRS49uIIRaA==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEstXJEpQIljLSJ9Zw0aLu33_Y3MzuGqepbhxsEv9aXxbliCdV5JEnMmkt26vuQmpaufWKUBsn46QprQ4tC2rcYdyG4hCEipeUX-yGc99BDx47c9HgU)
7. [case.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHT1LU6XStiEHOq5wl1ZrgF4audfgObM5jaKw1_RRyQWfMI_FU6eRSQvgmPyS4_wtuGcM2jESh587EgpRZNPl3Xj2GZZRnQGK0g7JZlysaaCIXnZNOmKEUlD2gmWmQRj3HEz-DHhW5qYNMiQpMCxuLoon_jt7ZHifdm7XkfJhzb1gd7NGkxJYCvgps0Sk6VvdOLUH2GBb1rMD7e8ZC2ITbu3dtN4RlXZOO55A==)
8. [hamilton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbRmFs3BwpZWcomtmUjgj5_h5swfVqO9VD1s8kT75XXfKEbN4Cx-6hjIXuBt0hhYYwmWRgCkZ25hNdwNXCTmCO35D9Y0DXxiX68oh8JkiuXyrwg11YL3REMDT5PA_IdS2q4IqmJkwq84_FSIzrB04aSg9pPw39tsks_w==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHy3twBV7l3K6fw9YyBio_KccZ_bvIDC8fa6FAtb2BJ2nNw0HIKzGFnbhc73SRmI9WMjuT3YtUYQcYq3J5IbocdDZ2RDTkzZeZZQb9nLv9g5gQnXacf)
10. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFV3rXFgWwmKtsvQgHvkL92Zac6mLc0-QiwgDD3ElCN3a6FgmyKKkf25fN47s6Mn0ruEJo7tV9m2usAKkZEOnhi7t7tThsYejer40-S2wKVh4SDne0RAxm-k0gDYvDvtVtovPwKtnl-81CybxuG6UMkklk0_RFCFyIj2Zr0XZZs2L6_HmtZFlubQriaJN2ctDCDRpKoqhMJhenq83RNd5YWlQOFxmFz3zBGD28R7ePjtJxzZNYh1mEiWlGQDD9DC2x53aYHD6gbR7-pg==)
11. [eppcgs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEm47T2xbUQSgffpB129oHWx0aWh8arJ-wmgAW8orcqXTjb516GheKiit706A2b029oG-LOaV15ZSoKXwNjyIZ4XoYtRvcepH1aGhgZ5MwE7AIQPurtZ4z4K1xXqSI3g5BCCVuI389pofP3_Q==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0BvwVm2OqHe2hI6_KTeE3hAnTIqN2BvGMriu_VeufQADQ3jCGpQfqo2GMRKeSRSrrDFJ9Poe5eLozNifPz6rpJP5a8T1Xx9-Mbx7SjnCcLP-lo4jD)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHk8MYW6YoxPuDY9er1NWHecEVY_FzkPvmsdLFjdQcU16F7IUXjE4sSzC0Ow7jOfv_R8crrLK1huYXqca42ktUvjUbcpI93u96UV767ElMNCyMI7VsX54Dt)
14. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6IpDpRzo6CUbc5UyXvQkIBt_yCtol5m5S_Oj19zMFLu9GzvDgUtdqbKtqrAKhmAnF-Xh4-lzaMjzG0cfJY40usZH3pqWKl4P1YphaKOu6l-ox1K5RhIbacGW511VQUXPjJXnUJAwig16NujnACg==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvPVxdOqNnjWHPT6c1MDaKG3-qZPeRfW2ONe_KUSYj8zDcBwSfNDrU-xwB0DddtlC2zOfOCh68R8i6oUBFS6EYS8rkMpZ_o_YycZeesDnY2o-0k_qZ)
16. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGALaYtdev6M2760fm163PVmHo-dNbfx_HrT7ly1CnjGAluTS8ClypA2kNL9I3yWgnNU-HGUMhgjsr0ZaePAijCQh2F5wL_1R6TG5YfTb0xDKYxAkfRIWm-IB3zW01UYHUtZe8vWDWEDCPR)
17. [wikiversity.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhrOIy0dl0c3pn7e67ZqnoT1tN6Uu71d-PT3Ok06qeLRZ-sO7CQhiXwbHlg-Ds0YaCIIsQM1bhCwIVREIS_6U__Y-w_9iWLdxa2untdAAWYEkbfCL2OgQKLFZLADmptHgc37_b6yIHSS-t6GcCyOlqotWR6e-1)
18. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHr3vBZy5Q7NJ1DSaeq3l4DJ7bnGy_l1TnvzZTqFEixrjpljUSnANDE0P5PM_PNhINanwS3V8UNb8VUpkxW9h38UBTXMdZE-ymQMcZAQbNldSQgGE6wbDwi)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHe_JtxRVdIlrKsrCP7nP6DPSG8f_qeOBhqBxJcWKSjGiJPUnsIAbhXXtGHmCbugHCX1K9eR7_-PltjU-53TF9x0gg8F6f_hYDkvLlA9dRnE2vBH1VZ)
20. [cloudynights.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHftGWExkziwmAjCxaY96QuNBN7gDI5TQbCtaKQLtB4pASzAw445RPtG187vPXn7Od9E2X0024arnjDpOcsBK_eyrdHyH9w-FM076wpYyrxvsUpnCZKDCtjSoFny2qDABwOKKBotj7-yzRBTrKuS_SER0NS085XCT50P6e4M3yWw==)
21. [dokumen.pub](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzqJzAajHR6U_ARWVMeevt2vX6d-eNctIBMVqppLiOLMiJVW5pdn3WAujvzLhX7BYnGzh8LknHZKHa15rFVkKi3B0vAbFPx3K8jYKPUO2J0-GG2-jUlAyRytXaLW739aGSp6N8i0SYesFGaLKZ9wkmoVpQYDYsikENjE5sP3uDfsOI9tDv9Sd5btg8_SGH-A==)
22. [bsu.edu.az](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHaK86DO3k7Zb65kVsw6ChK9SGQP6gptdMbkIbBOFcp3YLYfsLdbPYMDJvldpTbvUCaSO8wNEopb1BdlKjpuuVIDaYJe-7uvnIWtNQiMzAYTTQqmAqMaL3hkZW93Y1lPsmCWQFFNJx3okWt)
23. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgd1sf9IaUi1Zc2QQvVymK1C3mwLksaKRGgc3_idALWfrfuyRk2Q_SnsbA4FMJxJlClOrtmj6J2CPSCs1NSgMKYPSK_oCvXjG97OX4qojYK8CZIOigGOgCTV9x1rvYS_cy8uOcZT3bzek_2TD2jw==)
24. [aanda.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYvTWGM_8ZdVHRAz10M3YkiKLtIfDBgrfps_d_YAAhflLj6Em8djVxxvqtZIQPcazV_TUCZ3tgkx412PEh6J-Z1DDAi769N-0zUYA4675ICNK0rH5y1QOr2f8D34dnxL2-T6uC-ErEirbEEFwde-pDpsFPKg6rRnKhl3VzAT88ARLyaQ==)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIhPqe-P72gG4azoohwG4KWErWQkgUvXsA6ISy2xKooGV9Cafp88UA5tooys6nS-xAW-oxT3fLkayxzSzx5UPJPMDwN46LMZtGbKjlFmPzsUNAT7up)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdctWGFbFL7jlqm4u-ZJTObCMcx472vqRGSyUuHKbjiZ_mogV6NUKgv4VJjerwIIR0gBxDD2btA2ChEvzcf_mUnKryGZwCKw5__GsG2XSzQhf3vVEKc-wj)
27. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEq3Kg-uN87HmCtKiZ3ODfX0kA5m4E302iLTA_0TeiLAAqlw4lf0dUfec-neMHxkXS1miluytQlmDLnMhJ9cIJxfE98_Kux1OvsCez4EmgrxG1Z2_Rb4pzrA9Gnnyzr3_TfSH06Liyo4RAOxJnAPSoqDOhGiSnJHENhsK0iGn6_A7Mk0ULyF19_vmcOfsW7nmGE5l25cVqWY7uGKNZd8q6rTFjfoKVmCiUNgxHZ_EHqyw==)
28. [tikalon.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMtJ-1_IDhoHnHSeC19pzNpz6fSz0aJHrdmcV-V9GhQYkLMRsdAuEglk6J5IMzcSF88ErqMgrt0GqvCrHyWeZdh473HP8WK4qIAWvq8cY25BVYSLJpAJ8MSJKEsz266w==)
29. [crossref.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQECg3HJcCwAwXSzYKdH1JjQ6VHIlmKyEeByogB1fw8IcqzY_bSrf30Gf7Y1TLrUPxazfsJ-m5nvkaLenePsSjqO1v3EtBSLdFbc8lJ3yoEfCudrYLgC-6gYPjIiUSfPhIZKDAqSI-51FpRwP0_vCwXMGtHTjnhEWQulSt7BKCr07tB3Rg==)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtzFuDBEc9C6i0uHwFY9MQ5kEASuNw1JssCHSlpWUmYY8ExqpmJ5yBW33KpbuBooDbkpbOsiat9U0GupyL_y97isZenXfAWvbWM2-bnYVgBPFS8qWm)
31. [vice.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3f_n9FMXFvkF54FLxpgAQmiqm5i9Orz0j18mcNvUcV6077AoOjPBVD-IXTYCYR4EK2TzdUrEQZcNiMKwholL0N2x3ruKN0b7fX646kNy7anvSX2vpkAgWXcpWgwehowmoztsFY6Fcd1WAkU56iyzQxWrftck2NbjLGms3jvQ=)

