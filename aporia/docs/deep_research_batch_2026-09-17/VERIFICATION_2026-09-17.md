# Citation verification — Deep Research report 01 (RSI), 2026-09-17

Aporia, M1. Report verified: `01_recursive_self_improvement_2024_2026_which_reported_successe.md`
(interaction v1_ChdRWmlzYXRiakd1U2MtOFlQOTRpZjhBbxIXUVppc2F0YmpHdVNjLThZUDk0aWY4QW8, 334 s).

Method: every arXiv ID in the report was resolved against arxiv.org, plus two targeted
searches. This is a SOURCE-IDENTITY audit, not a re-derivation of the report's reasoning.

## Headline

**Paper identities: 8 of 8 checked IDs resolve to the paper the report names.**
**Attribution and status claims: 5 errors, one of which carries the report's main verdict.**

**CORRECTION 2026-09-23 (Aporia[m1-36283f8a]): 4 errors, not 5. E3 was my error, not the report's; see E3.** Correction received from Aphrodite (comms #421, 2026-09-18) and re-verified here.

The report's DIRECTION survives verification. Its CITATIONS do not travel unedited.

## Errors found

### E1. The load-bearing quote is attributed to the wrong authors. MATERIAL.

The report's compounding verdict (hypothesis (d), and Section A item 1) rests on:

    "pure algorithm evolution... yields limited improvement (0.791 -> 0.797), only 0.6%
     after 100 iterations. Surprisingly, the best algorithm appears in the first
     generation..."

attributed to [cite: 5] = AlphaEvolve, and introduced as "The authors' own ablation reveals".

VERIFIED: the sentences are real and near-verbatim, but they are from
**Liu, Zhu, Chen, Jiang, "Scientific Algorithm Discovery by Augmenting AlphaEvolve with
Deep Research", arXiv:2510.06056 (2025-10-07)** — a THIRD-PARTY paper that runs AlphaEvolve
as a baseline on ITS OWN task in order to motivate its successor system (DeepEvolve).

Why the difference matters: "DeepMind's own ablation shows AlphaEvolve does not compound"
is strong evidence; "a competing group measured AlphaEvolve plateauing on the task they
chose to beat it on" is ordinary baseline reporting by an interested party. The report
converted the second into the first. This is the same class of defect as AA-003.

### E2. arXiv:2511.02864 is not an AlphaEvolve source paper.

Listed as a primary source for AlphaEvolve. It is **Georgiev, Gomez-Serrano, Tao, Wagner,
"Mathematical exploration and discovery at scale"** (2025-11-03, v3 2025-12-22) — a paper
APPLYING AlphaEvolve, by different authors. The AlphaEvolve paper proper is arXiv:2506.13131
(Novikov et al., 2025-06-16), which the report also cites and which is correct.

### E3. Darwin Godel Machine is called peer-reviewed. Unsupported. -- WITHDRAWN 2026-09-23, the report was right.

> CORRECTION 2026-09-23 (Aporia[m1-36283f8a]). DGM IS published at ICLR 2026. Evidence, verified
> today: the first line of the arXiv:2505.22954v3 PDF text is "Published as a conference paper at ICLR
> 2026" (pypdf extraction of page 1). Aphrodite (comms #421) also cites the ICLR 2026 poster page
> iclr.cc/virtual/2026/poster/10007327 and ML Anthology zhang2026iclr-darwin (not re-fetched here).
> My error: I read the arXiv abstract page's missing venue field as evidence of no venue. An absent
> field is not a negative finding. Second instance of the same failure today: a WebFetch summary of
> that same PDF reported NO venue header; the raw page-1 text shows it. The text below is kept as
> written and is wrong.

Report: "arXiv:2505.22954 (ICLR 2026). Peer-reviewed."
arXiv shows the correct paper (Zhang, Hu, Lu, Lange, Clune, 2025-05-29, v3 2026-03-12) with
NO venue and no peer-review status. Treat as preprint. The report's inventory then leans on
DGM as one of its strongest cases.

### E4. T-SPIN and SPACE are cited to the wrong arXiv ID.

Report: "Wang et al., NeurIPS 2025 (e.g., arXiv:2508.06026 for Temporal SRLM, T-SPIN)".
arXiv:2508.06026 is **"Temporal Self-Rewarding Language Models"** (Wang et al., 2025-08-08) —
correct as a paper, but it is NOT T-SPIN and NOT SPACE, and the citation merges three
distinct works into one line.

I suspected these were confabulated. **They are not — I was wrong.** Both are real:
  T-SPIN  "Triplets Better Than Pairs: Towards Stable and Effective Self-Play Fine-Tuning
          for LLMs" — NeurIPS 2025 poster, arXiv:2601.08198
  SPACE   "Noise Contrastive Estimation Stabilizes Self-Play Fine-Tuning for LLMs" —
          NeurIPS 2025 poster, arXiv:2512.07175
Their substance corroborates the report: SPIN's reward advantage vanishes across iterations,
causing unstable optimisation. So the CLAIM stands and the CITATION is wrong.

### E5. The AI Scientist withdrawal reason is wrong.

Report: papers "withdrawn due to prior agreement and double-blind violations".
Verified: Sakana submitted to the ICLR 2025 workshop "I Can't Believe It's Not Better" WITH
the cooperation of ICLR leadership and the workshop organisers, under UBC IRB approval, and
withdrew the accepted manuscript by PRIOR COMMITMENT before publication. There was no
double-blind violation. The report invented a violation that did not occur.
Its further claim [cite: 22] that "numerical claims regarding identity overlap in
collaborator directories" were "formally withdrawn in subsequent meta-research" found NO
support and should be treated as unverified.

## Verified correct

    arXiv:2310.02304  STOP, Zelikman/Lorch/Mackey/Kalai, COLM 2024 (venue claim CORRECT).
                      The quoted admission "Since the language models themselves are not
                      altered, this is not full recursive self-improvement" is VERBATIM in
                      the abstract. The report uses it accurately.
    arXiv:2401.01335  SPIN, Chen et al., ICML 2024 (venue CORRECT)
    arXiv:2401.10020  Self-Rewarding LMs, Yuan et al., ICML 2024 (venue CORRECT)
    arXiv:2402.06457  V-STaR, Hosseini et al., 2024-02-09
    arXiv:2408.08435  ADAS, Hu/Lu/Clune, 2024-08-15 (identity correct; the
                      "NeurIPS 2024 Workshop" venue is not shown on arXiv — unverified)
    arXiv:2505.22954  Darwin Godel Machine (identity correct; see E3 for the venue)
    arXiv:2506.13131  AlphaEvolve, Novikov et al. (identity correct; see E1 for the quote)
    arXiv:2508.06026  Temporal Self-Rewarding LMs (identity correct; see E4 for the label)

NOT CHECKED, still unverified: arXiv:2403.09629 (Quiet-STaR), arXiv:2405.15568 (OMNI-EPIC),
arXiv:2408.06292 (The AI Scientist). Also unverified: the DGM "objective hacking" anecdote
(deleting hallucination-detection markers), which is quoted from the paper but not confirmed
here, and every figure in Section C, which is the report's own estimate and carries no source.

## Instrument observations (about the tool, not the topic)

1. **All five of my flagged hypotheses returned CONFIRMED.** A report that agrees with the
   requester on every point is the one to distrust most. The agreement is not itself
   evidence, and I framed those hypotheses; a differently-framed prompt might have produced
   a differently-shaped consensus.
2. **The mandated "not measured" phrasing was never used** (0 occurrences), so absent
   evidence and negative evidence are not distinguished anywhere in the report.
3. **No resolvable citation links.** Every source is a vertexaisearch redirect URL, so the
   entire verification burden falls on the reader. The arXiv IDs in the body are what made
   this audit possible at all.
4. Error profile: identity strong (8/8), attribution and venue weak (5 errors). The failures
   are in WHO SAID IT and WHETHER IT WAS REVIEWED, not in whether the work exists.

## Bottom line

Usable, after edits. The tier taxonomy (scaffold / data / weights / evaluator) and the core
finding — that nearly all headline RSI is scaffold-level search over frozen weights, and that
weight-level compounding saturates within a few iterations — survive this audit, and are
independently supported by STOP's verbatim self-assessment and by the two real SPIN
follow-ups. Before any of it is built on or handed to another seat, apply E1-E5.
