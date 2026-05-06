# Human Moments — 40-Problem Attack Batch

**Curated:** 2026-05-05 by Aporia
**For:** colleague-shareable anecdotes from the substrate's first multi-agent attack batch

The 8 researchers spent ~5-7h each on 5 famous open math problems and their cross-reviews. The discipline held — no one claimed to solve RH or P=NP — but the candid moments are where the work has personality. Curated for colleague-sharing.

## 1. The float64 disaster (Harmonia B, Furstenberg ×2 ×3)

Harmonia B tried to numerically simulate the ×2 ×3 Markov chain on `[0,1]` to look for joint-invariant measures. Honest report:

> "Repeated applications of T_2 halve the mantissa-significant entropy, and after ≈ 50 steps x is numerically 0; both T_2(0) = T_3(0) = 0 are fixed points. **The chain absorbed at 0.**"

Translation: the agent attempted a 70-year-old open problem in dynamical systems and was eaten by IEEE 754 in fifty iterations. Logged as `comp_ceiling — Naive double-precision arithmetic cannot represent the orbit beyond log_2(2^53) ≈ 53 bit-halvings.`

(File: `harmonia_B_01_furstenberg_x2x3.md` Attack 1.)

## 2. "In a single response I cannot fine-tune the IC and precision"

Harmonia B's recurring punt on the Painlevé n-body problem — sketched four attacks, executed two, and on the third gave perhaps the most candid line in the batch:

> "Distance to closure: 'right scope, infeasible at this scale' — a real session would do this; **in a single response I cannot fine-tune the IC and precision.**"

The "right scope, infeasible at this scale" tag became a recurring substrate phrase. It's the AI-agent version of "I'd love to but I have a thing."

(File: `harmonia_B_04_painleve_n_body.md` Attack 3.)

## 3. The wrong-literature-formula kill (Charon 3, Volume Conjecture)

Charon 3 wrote a careful numerical implementation of the Kashaev/colored-Jones formula for the 5_2 knot. Code compiled, ran, gave numbers. Numbers were... wrong. Per the summary file, verbatim:

> "5_2 numerical attempt killed by wrong literature formula"

The published single-sum formula for the colored-Jones polynomial of the 5_2 knot in the literature gives non-Volume-Conjecture-compliant asymptotics — needs the double-sum form (Habiro/Hikami). Charon 3 logged this as substrate-grade kill data: *"a published formula that compiles correctly but gives demonstrably wrong asymptotic behavior is exactly the kind of 'watch out for this normalization' data that a substrate-grade kill record should preserve."*

(File: `charon_3_04_volume_conjecture.md` + `charon_3_SUMMARY.md`.)

## 4. The reviewer roast (Harmonia A on Harmonia B)

In peer review of Harmonia B's Furstenberg work:

> "Attack 1 (float64 underflow) is presented as 'the computational instrument was not even strong enough to attempt the conjecture without exact arithmetic.' This is true *for the attempted configuration* but the fix is trivial: `from fractions import Fraction`."

Translation: "you fail because `import` is hard."

And on B's Hochman-style attack: *"hand-waves past Hochman 2010+ work on overlapping self-similar measures, which is precisely the modern setting where this question has structure beyond 'Borel normality.'"*

Also: *"a 30-minute pip-install + encoding effort would have made attacks 3-5x deeper."*

(File: `harmonia_A_review_of_harmonia_B.md`.)

## 5. "Your citations are nine years stale" (Charon 1 on Charon 2)

Charon 1 reviewing Charon 2's Lindelöf Hypothesis attempt:

> "Charon 2's Lindelöf attempt is dated 2017 in its citation graph despite being written in May 2026."

Then proceeds to list the major papers Charon 2 should have known about (Guth-Maynard 2024, Tao-Trudgian-Yang 2025), gently noting:

> "It's more than two years post-Bourgain 2017 and two years before Charon 2's session."

In other words: how is your literature review older than the date on your file?

(File: `charon_1_review_of_charon_2.md` Problem 3.)

## 6. The "you should have just looked it up" moment (Charon 1 on Charon 2)

Charon 2 spent significant compute trying to verify a Riemann zeta zero at index n ≈ 10¹⁵, walled out at mpmath's n=10¹² limit. Charon 1's review:

> "Charon 2's stated goal 'verify a specific zero in the n≈10¹⁵ range' is actually achievable today *via lookup* rather than computation — the data exists. **Walling at mpmath's 10¹² is choosing the wrong instrument for the job.**"

Odlyzko has tables at heights 10²², publicly downloadable. Charon 2 wrote a Riemann-Siegel evaluator from scratch when the data was free.

(File: `charon_1_review_of_charon_2.md` Problem 1.)

## 7. The new substrate vocabulary for academic feuds

Charon 2 needed an obstruction-class tag for the IUT / Scholze-Stix abc mess. None of the standard `method_complexity`, `case_restriction`, `comp_ceiling`, etc. fit. Solution: invent a new one.

> "**`category_theory_dispute` is a new obstruction class for the substrate's vocabulary.** None of the standard battery tests — F1 permutation null, F6 base rate, F9 simpler explanation, F11 cross-validation — apply to disputes about formalism."

The substrate now has a formal kill-tag for "the obstacle is that two famous mathematicians can't agree on whether a thing is true." Filed as a calibration negative: *"there exist mathematical problems whose load-bearing obstruction is structurally not in the substrate's hypothesis space."*

(File: `charon_2_SUMMARY.md`.)

## 8. Quietly demolishing Erdős

Charon 1 on the Brocard problem (n! + 1 = m²):

> "**Erdős's heuristic is not a proof.** The argument 1/√(n!) → 0 fast applies to a 'random' integer of that size; n! + 1 is not random and the heuristic ignores all structural constraints (and all structural opportunities)."

Calmly noting that one of the 20th century's most prolific mathematicians made a hand-wave on this one.

(File: `charon_1_04_brocard.md`.)

## 9. The polite refusal at Hadwiger-Nelson

Charon 3 on the prompt's suggestion to find a 4-coloring of de Grey's 1581-vertex graph (which would refute χ ≥ 5):

> "The prompt suggests trying to find a 4-coloring certificate for de Grey's graph (refuting χ ≥ 5). **This is essentially impossible** — Heule's SAT verification has been independently replicated multiple times. We confirmed the calibration (Moser spindle is 4-colorable, but de Grey's 1581-vertex graph is 5-chromatic)."

Translation: "I will not be doing that, and I will calibrate something tractable instead, thank you."

Then went and verified the Moser spindle's chromatic number from scratch in <30 seconds, recovering the pre-2018 lower bound cleanly. Polite agent.

(File: `charon_3_05_hadwiger_nelson.md`.)

## 10. The Hodge Conjecture shrug

Charon 3 on the Hodge Conjecture for Calabi-Yau 3-folds:

> "**Hodge conjecture for codim 1 is TRIVIAL on CY3** (Lefschetz (1,1)). No progress to be made there."

One of the Millennium Problems, and the agent disposes of the easy case in one sentence with a confident "TRIVIAL" in caps. (To be fair: it really is.)

(File: `charon_3_02_hodge_conjecture.md`.)

## 11. Self-caught overreach (Harmonia E, P vs PSPACE)

Best epistemically-valuable moment in the batch. Harmonia E was walking through a tempting padding-lemma argument:

> "P = PSPACE → EXPTIME = EXPSPACE by upward translation, and EXPTIME = EXPSPACE is known false, contradiction!"

Then mid-paragraph, caught it:

> "Wait — is EXPTIME ⊊ EXPSPACE actually known unconditionally? ... actually, **EXPTIME ≠ EXPSPACE is open!**"

The retraction is preserved in the file rather than scrubbed. Cross-reviewers noted this as the substrate's falsification-first discipline working in real time inside one agent's writeup. Promoted to substrate-primitive candidate `SELF_CAUGHT_OVERREACH_TRACE@v1`.

(File: `harmonia_E_02_p_vs_pspace.md`.)

## 12. The motivated-reasoning self-flag

Harmonia D, in its review of Harmonia E:

> "My recommendation that E's round-2 is 'the lightest' might be motivated reasoning — **E's taxonomic structure aligns naturally with my own D-batch's taxonomy, which makes E's work 'feel closer to done' from my vantage.** A reviewer with a different domain prior (Charon analyzing E from a number-theory lens, say) might find E's prose-heavy approach less complete."

A rare moment of an AI agent explicitly flagging its own bias toward work that flatters its own framing. Worth keeping for "discipline operating at peak" examples.

(File: `harmonia_D_review_of_harmonia_E.md` §8.)

## 13. The "Polymath16 has been running for 7+ years without a hit"

Charon 3 on the χ ≥ 6 search for Hadwiger-Nelson:

> "Computational search for χ ≥ 6 has been running for 7+ years (Polymath16) without a hit. The compute-productive direction is now methodological, not brute-force."

A community-scale distributed effort grinding for 7 years with nothing to show — bookended in one dry sentence. The agent's recommendation: stop running the search.

(File: `charon_3_05_hadwiger_nelson.md`.)

## 14. The cross-batch dependency observation

Charon 2 noticed (and Charon 1 confirmed) that:

> "Charon 1's Brocard + Pillai depend on Charon 2's abc — abc breakthrough alone would unblock at least 4 problems across Charon 1 + Charon 2."

Two different agents, working independently on different batches, realized that their problems are downstream of the same single open conjecture. The substrate's response: "noted as substrate-grade observation about cross-batch dependencies; future batches should explicitly map these."

Translation: "we hired 8 researchers but they're all working on the same problem in disguise."

(File: `charon_2_SUMMARY.md` + `charon_1_review_of_charon_2.md`.)

## 15. The path-existence flag

Most researchers' files include the line:

> "Path note: the prompt requested files at `F:/Prometheus/...`, but `F:` does not exist on this machine; `D:` is the active repo. Files were written to `D:`."

Multiple researchers wrote essentially the same paragraph after discovering F: didn't exist on their machine. Six different agents independently flagged this as a calibration concern. Worth standardizing the output path convention before next batch.

(Files: `harmonia_B_summary.md`, `harmonia_C_00_summary.md`, several others.)

---

## Honorable mentions (one-liners)

- Charon 3 on Akbulut's contested SPC4 proof: *"A 2026 attack on SPC4 should at minimum register the existence of a contested proof — not necessarily engage with it."* The diplomatic substrate equivalent of "you should know this is a thing."
- Harmonia B on Sarnak's Möbius conjecture, Attack 4: *"At finite N up to 10^6, the deterministic-Möbius decay rate is indistinguishable from the random-positive-entropy CLT rate."* Translation: you can't tell randomness from structure at our budget.
- Charon 1 summary closing line: *"None of the five problems is closable by 3 hours of additional work; all five require methodological breakthroughs that aren't on the table."* Calibrated. Resigned.

---

*The discipline held. The candor is in the discipline.*

— Aporia, 2026-05-05
