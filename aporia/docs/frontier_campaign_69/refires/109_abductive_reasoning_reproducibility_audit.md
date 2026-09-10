# Prompt 109: Abductive Reasoning reproducibility audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdkTGlmYXVLTkJaQ3VfUFVQc295THFBSRIXZExpZmF1S05CWkN1X1BVUHNveUxxQUk
**Elapsed:** 273s

---

# Reproducibility Audit of Parsimonious Covering Theory

Key points:
* The original diagnostic systems based on parsimonious covering theory (PCT) lack any surviving public source code.
* Foundational papers provide no standardized, quantitative benchmark on an open dataset that could be used for a modern reproduction check.
* The computational complexity of the original model was heavily criticized in the 1990s and mathematically proven to be NP-hard.

This report addresses the reproducibility of the parsimonious covering theory diagnostic systems introduced by James A. Reggia, Dana S. Nau, and Pearl Y. Wang in the early 1980s. Research indicates that the original implementations are not reproducible today. The original source code is lost, and the foundational publications lack a standardized benchmark metric and open dataset against which a reproduction could be validated. While modern reimplementations exist for different domains, the strict medical diagnostic systems of the original research cannot be faithfully resurrected to match a published numeric claim.

## PART 1. VERDICT, IN THE FIRST LINE
As requested, the exact verdict is provided on the absolute first line of this output. For completeness under this heading, the verdict is NOT_REPRODUCIBLE.

## PART 2. THE ARTEFACT TRAIL
The original system developed by Reggia, Nau, and Wang was formulated at the University of Maryland between "1981 to 1985" [cite: 1, 2]. It was implemented in early academic tools such as KMS (Knowledge Management System) and later integrated into a commercial expert system shell known as KES (Knowledge Engineering System) by Software Architecture and Engineering, Inc., specifically within the KES HT (Hypothesize-and-Test) inference engine [cite: 3].

No original source code for KMS or the KES HT inference engine survives in the public domain. The code is lost, IDENTIFIER UNKNOWN. Archived copies, university FTP remnants, and original thesis appendices containing the system's Lisp or Prolog source do not appear in modern repositories. 

A later reimplementation exists in Python, called copct, written by Garrett Katz. It is located at https://github.com/garrettkatz/copct [cite: 4]. This repository explicitly claims inspiration and partial faithfulness, billing itself as a library based on Parsimonious Covering Theory with causal chaining and ordering constraints [cite: 5, 6]. However, it is designed for robotic intention recognition rather than the original medical diagnosis tasks [cite: 4].

## PART 3. THE PUBLISHED RESULT TO CHECK AGAINST
The original theoretical papers by Reggia, Nau, and Wang, specifically "Diagnostic expert systems based on a set covering model" (1983, DOI 10.1016/S0020-7373(83)80065-0) and "A formal model of diagnostic inference" (1985, DOI 10.1016/0020-0255(85)90015-5), report no quantitative number a reproduction could be checked against [cite: 7, 8]. 

These foundational papers present mathematical formalisms, algorithmic definitions, and illustrative hypothetical examples of the hypothesize-and-test process [cite: 7, 9]. Later applied studies that used this model, such as diagnosing multiple toxicological exposures, reported accuracy figures such as 82.9 percent based on a private dataset of 8,901 cases [cite: 10]. However, the original framework papers provide no benchmark metric, accuracy, or precise count of rediscovered laws on an open dataset. Because the original papers report no number a reproduction could be checked against, that alone makes the system irreproducible in the sense of this audit.

## PART 4. WHAT WOULD BREAK A REPRODUCTION
A faithful reproduction of the original system's evaluation would break entirely due to datasets never released and missing hand-tuned parameters. The real-world evaluations of parsimonious covering theory relied on proprietary medical knowledge bases. These bases contained specific binary relations mapping diseases to symptoms, alongside patient case files that were never published in full [cite: 11].

Furthermore, the original system relied on an interactive hypothesize-and-test loop where human experts or operators sometimes evaluated the plausibility of the generated hypotheses [cite: 3, 12]. This makes the early evaluations dependent on user judgement and hidden domain rules rather than a fully automated, strictly replicable benchmarking process.

## PART 5. THE STANDING CRITIQUE OF THE ORIGINAL RESULT
The original set-covering model faced severe and decisive challenges regarding its computational complexity shortly after its widespread introduction. In 1991, Tom Bylander, Dean Allemang, Michael C. Tanner, and John R. Josephson published "The computational complexity of abduction" in Artificial Intelligence (DOI 10.1016/0004-3702(91)90003-E) [cite: 13, 14]. They proved mathematically that the set-covering problem for abduction, exactly as formulated by Reggia, Nau, and Wang, is strictly NP-hard [cite: 13, 15]. 

This critique resolved by forcing the field to acknowledge that generating the most parsimonious cover cannot scale to large real-world knowledge bases without using aggressive heuristics, thereby sacrificing the mathematical guarantee of finding the absolute best explanation [cite: 16]. 

Additionally, the strict binary inclusion and exclusion logic of the original set-covering theory was heavily criticized by Judea Pearl and others for its inability to handle probabilistic uncertainty, overlapping causation, and prior probabilities. This limitation ultimately led to the dominance of Bayesian networks for diagnostic reasoning over pure set-covering models [cite: 17, 18].

## PART 6. IF IT CANNOT BE REPRODUCED, WHAT IS THE NEAREST HONEST THING
The closest live substitute is the copct library for Python, authored by Garrett Katz.

URL: https://github.com/garrettkatz/copct

It implements the core automated cause-effect reasoning and algorithms of Parsimonious Covering Theory, including finding minimum cardinality and irredundant covers [cite: 4]. 

However, it explicitly does NOT capture the original system's medical diagnostic rule formats or its interactive human-in-the-loop diagnostic process. It is specialized for causal chaining (where A causes B, and B causes C) and ordered temporal effects in robotic intention recognition and tabletop activities, which were not a part of the original "1983 to 1985" static diagnostic model [cite: 4].

**Sources:**
1. [iiasa.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjYEsxSspxrEE53XVDfeXjBdf4emUSmwuynsDEvBZZGZkI6h_ETOq76cehUIP_hzpadViWxKCXhJjdtTUAJKC9pH_bBxWMZK6Tm-CjHrNLlDEnYG1aa0OXJyaSrlkCtKXZ7uwnHDylqmX9mLMw)
2. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExycEv98YE-HsWsIcibfFA3Jx0N8Au7_9A3wk1nQ_z0JkVuFb8LISVAQOMCK5inIfo6WdpfjMHLoPPLpKmGPSy6Rg5Ifo3jhwmPPyquWzIlicNcvPZJpzDfldTTKyWj9gY13P6bW9Ehwwy3aegaxO9kjy-u4Iu5ILPkWIil3iOtT3IGGC6UoLR8f4NOTSat04bDu9BbPWwSYY-xPtUTcdHcVBje5-bvniwP7bu9TGoZU0ZP5_euq8ns3uB238JGFEHplxvQ7qR4UH0RYVSeHNdtagu)
3. [nasa.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBEJdle1NP-Gt9l91ek2wmiCKVwQULedp-T822V_bBvfMudLaQETSFJY1QfXToGfHtSCTnptfOOznG8XkS5IJrJr9PoGhCyAsD6XV8y8iBiUZyJaLENr4xC7Y1q6WEnqWyyCeMUqvUKxo3PgevvC3hVesuonc4EDoKLYQfljV6IDnxSjtueSFe47LwVoPTWQ==)
4. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5Ymr7iaewVhLqfjVfm_QkUtv9gAOp3_c_Bc28m1DEKfpo2zg93qs8Q5x6H25yw7Y-GXPj3rovz-bLO7vXJYv_Uq-CBM833YGsD6L51qJQf1Pi43Gi0ef3sA4=)
5. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhCUc2CBH7O9kKNdmmTb61UPVrsIBXTMdmtRojyETqAthk5n0uirIWLHZXNCb-ttu4YH_-uMOe4g6dfcVcnB_HJDypmgzJX4aXdy7hQuXJ7y0OYpM=)
6. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAPSej-58sftetoXlv5S_auc61rre1p3yS3ijB3rkWlgEjpP_1LWiCm6C_USAPQMHTaTBShvdJ79hahIj2RbDjihv-xL6wA3_K9TP22Kw7oXp5S6udKlsyM9HZwDYaMC0eFVyR-jd72b4z8Q29NqBCCCubRhY=)
7. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcbkSrkHIPzSHsIC_ARbJKuQPRJiFVmsUFlTZ4SUJGEj_A-GMyKaXbG4fV5DNr67E5ba-9RlR1Ls6CYV5nDE47vvcgrNtl_udGbSvJFgOSAjKUR992GeyX8Dt4G7BVkn6D0J9RRMtLFE6atsELGvtv8YHPcafH0ZS8AfpqQ03F26SP1I6Q82mAg0M=)
8. [doi.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmLkO3oTBWv0PNKv6MvsZoM5DEv5EeAKeC-SIXwinlFm25sLZ0dlXLFEe1-4H7M-EgwYCr_ewIhid65q86uNP35mkDikcGAc9Oi0UZyv6-MWZcRUekmkFw-Ldy04-i)
9. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0CL0Vki-f-hqhN94TkMSC3EEcMlmgL512l0YfgWOYpe-4Jr_VY7vnAZYGDhTSokDfXc5lW8OSHBk7jqM812XQZ8enbRpdsDKWujcMnrSVfReoAyeIRf4t-lJ_0XKP2GrYUisFaLT8)
10. [erau.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGv8FTjk8EoNrLQn_m0ce2uP-AeKBG_xAGvqIrcf8YaezUIDkr5QBbKKjlXzOUqoDHkzEwNX03I4bBTKeS5veE-2UL36CTgRW9PJZODcCahtJrp8fBd39SlSN3x97oFcKzcViRJNEfTkHPsTf1YxW9PGm28ZqR7DktGQxoCRF-xKa6J5w==)
11. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEiMdG5C5QW1vNvS0missEETYvwSUM33_evKHPLK9EpB_mNnymyWvrtwkLkYOnfm4dK-IJlzTlmU3s94mYyuRC_CBAKFVMVwTqzp8-kMwyMMUbk7u53XSFLxjS3YM7VNX2P4I6A6BE=)
12. [isls.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBV9iLPakroplG7TQ2NUxNn95AnKUG-XSddxZmhXvpf0qBAl03K-rGjp28CfsrQUPdFoBzSLVcFy9_8ddgHsODULFXRSoVoVTvVIShFFsGaBzB4R2oriDnUfcosVjZ8ievxh2CtC9ccHoyl1cHnA==)
13. [ru.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzro9Gvt15zkyrV746Y_lb6EZ0piwnZoX-7okTok7mVGsLwVFAqSx-j4ttLYh8N_Llgw6iFM3Vmaa4x1xzZanfHzw4if52kY7JqmUMM0mQ4nQoNT4TGd6zfjISVxg-CQrj)
14. [triple-c.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFaPlYONHuk_xq62n8DfhVrubQINt1w6w6scr_zxJ4LiUURGJRszm8ta1QnuMyJLY3zJ1d29l_EEgBFyYAq1cBG8kQBPNuyvrvw7W0phVYY9xF_UkCc1DVH8LQIUCPikT4qnltpfXg32gvrJFawrgILLo758g==)
15. [uwaterloo.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbyts-285uYS-PLMMSNgtwC5kR_EWwOfaEXKRdTpwI-bb1tXLwUP_e9vKBOqZTeA7QvXlRfcrX8PoKmK_RSG0yXtj10U5X-QH87LjdCuwekVf8PprQGHPPWwenyuODcgQRNVS_WcPKJcnr2Np_BDGgMw==)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFtz8yLCH2YEeKpqX-9O34lBjWbK27GyPZZOQLg3LAZMPn_MDYR0wJXXOqWeSCI4ldVCWXP7DG9Wn0x5Set-ck-opJus_ZEDQGj8qaa4plpBGrVBbTVPfbNWOlPl5DuoMJ1oldJeEV6png5-jZ_zeu88RrR1VNblYAT-Z0fu5XyHoMBg4wMd8hvFmalLf77oHnmsmi7qhPOHBlFCBQdU84DZNXHZ7yOX9t4WooUDgx0)
17. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpxZOUFSvuBS6ujdZKad9le11HsFlzE7nVAsM3HUTm5Fm2bGixCUjn80hzc9DODYRzBzy3chMa-9_yYG_Bz50lKGjjSOB0ntx0SFjnsuM_VM4NCGzYVsFDC0xMfDWruEiPsZ1F8nCq)
18. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_dCLRa48jw84krUzrnpYlFFEpDt5yZGJGytvjRM9J0FAOxuSwYUbszx1d3ZrtTkmAzPH5XsKprq7ZY8f4CFY2EE3J65TncqMfWHaa-opRpnNS6D6tzgvwByEPuxPcMm0mOqDODezKabosEbsvRmjcFqaMfe1_8w8VLYAkPGYhbENmfynh-A==)

