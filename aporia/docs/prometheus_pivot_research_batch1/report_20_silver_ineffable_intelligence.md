# Report 20: Ineffable Intelligence + David Silver — Methodology Intelligence

**Date:** 2026-05-02
**Topic:** Track record, prior bets, and likely methodology of David Silver's Ineffable Intelligence

## 1. Situation

David Silver is, after Demis Hassabis, the most consequential single technical actor on Prometheus's strategic horizon. His move out of DeepMind to found Ineffable Intelligence (London, 2026) at a $4B pre-money valuation is the first credible, well-capitalized public bet against the LLM-scaling consensus by someone with the track record to back it. Silver's thesis — that superintelligence will not emerge from next-token prediction but from RL self-play in environments with clean reward — is structurally aligned with the conviction underlying Prometheus's substrate work. That makes Ineffable simultaneously the most dangerous competitor to Prometheus's positioning *and* the most plausible eventual collaborator/customer for a substrate. Understanding what Silver will likely build, and where his gaps will be, is the highest-leverage intel question of Q2 2026.

## 2. Silver's track record and methodological signature

Silver's published portfolio is unusually consistent in its methodological commitments:

- **AlphaGo (2016)** — first to defeat a top human in Go via deep CNN policy/value networks combined with MCTS, trained from human games then self-play. Established the PV-MCTS paradigm.
- **AlphaGo Zero (2017)** — removed all human data; trained from random initialization via pure self-play. The bitter-lesson maximalist version of AlphaGo. Proof point: human priors are dispensable when the environment is clean.
- **AlphaZero (2017)** — generalized AlphaGo Zero to chess and shogi with one architecture and one set of hyperparameters. The argument: a single recipe handles any perfect-information zero-sum game.
- **MuZero (2019)** — removed the requirement for a known environment model; the agent learns a latent dynamics model jointly with policy/value. This is the move that takes AlphaZero out of board games and into Atari, and is the architectural seed for any future "AlphaZero for the real world."
- **AlphaStar (2019)** — imperfect-information real-time strategy in StarCraft II, demonstrating that the framework extends past zero-sum perfect-information settings into partially observed, large-action-space games via league-based self-play.
- **Era of Experience (Silver & Sutton, 2025)** — the position essay argues we are exiting the "era of human data" (LLM scaling on web text) and entering an "era of experience," in which agents generate their own training data via interaction with environments under grounded reward. Explicit critique: language pretraining hits a ceiling because it trains on human transcripts of cognition, not cognition itself.

The methodological constants across the entire Silver corpus are: (a) **search at inference time** (MCTS or a successor), (b) **value/policy networks trained against the search**, (c) **environments with clean, machine-checkable reward**, (d) **sample efficiency bought via planning rather than scale**, and (e) **self-play or population-based training** to remove dependence on a curated human curriculum. He has never shipped a system that depends on imitation of a human corpus as the primary training signal.

## 3. Ineffable Intelligence: known facts

The publicly verifiable facts as of April 2026 are sparse but consistent across reporting (FT, The Information, Bloomberg):

- **Founded:** Q1 2026, London-headquartered, with a probable secondary site in the Bay Area for compute proximity.
- **Founder/CEO:** David Silver (departed DeepMind late 2025/early 2026).
- **Funding:** Approximately $1B Series A at a ~$4B pre-money valuation — one of the largest seed/Series A rounds in European AI history, comparable in size only to Mistral's and SSI's early rounds.
- **Lead investors:** Sequoia (lead), with participation reported from Alfred Lin's vehicles, Jensen Huang personally / NVIDIA strategic, and conversations (status unclear) with Google and Microsoft for compute and/or strategic stakes.
- **Compute:** Reported NVIDIA strategic relationship implies a multi-year H200/B200 (or successor) commitment; London location aligns with UK AI Compute Council / Isambard-AI access if pursued.
- **Product:** None public. No demo, no whitepaper, no roadmap, no API, no published research output under the Ineffable name. The company is in stealth.
- **Hiring signals:** Early hires reported from DeepMind RL groups (AlphaZero/MuZero alumni), with selective recruiting in Edinburgh, Oxford, and Mila orbits. No mass hiring spree visible — consistent with a small founding research team rather than a product organization.
- **Stated thesis (via interviews and the Era of Experience essay):** LLM scaling is asymptoting; superintelligence requires experience-grounded RL with self-generated data.

What is *not* public: target domain, choice of environment, whether they will build their own foundation model or wrap an open-weights one, planned time-to-demo, IP arrangement with DeepMind.

## 4. Inferred methodology

Given the track-record signature, the most probable architecture is:

- **Architectural family:** MuZero-class — model-based RL with a learned latent dynamics model, MCTS or a tree-search successor at inference, value/policy heads trained jointly. Possibly with a transformer backbone for the dynamics model (the AlphaProof and Stockfish-NNUE precedents both point this way), but the *training signal* will be self-play / search-bootstrapped, not next-token loss on human text.
- **First-target domain:** Almost certainly a verifier-rich domain. Mathematics is the highest-prior candidate because (a) Silver's DeepMind stablemate built AlphaProof in Lean, (b) reward is machine-checkable, (c) the domain is unbounded so self-play does not saturate, and (d) a math demo carries narrative weight comparable to AlphaGo-vs-Lee-Sedol. Code (with executable tests as verifier) is the second most probable target. Game-of-life / cellular-automata-style "synthetic universe" environments are a dark-horse possibility consistent with Sutton's recent writing.
- **Environment scope:** Will need to be **broader than Lean's surface area**. AlphaProof's bottleneck is autoformalization — the tax of translating informal math into Lean. Silver will likely either (i) partner with or absorb an autoformalization effort, (ii) build a richer mixed formal/informal environment with partial verifiers, or (iii) start in code where the formal/informal gap is smaller. This is precisely the substrate gap Prometheus is positioned to fill.
- **Time-to-first-demo:** 12–18 months from funding close. AlphaGo took ~2 years from project start to Fan Hui; AlphaZero ~9 months from AlphaGo Zero. With a fresh team and no inherited infrastructure, 12–18 months to a "we beat IMO/Putnam/USACO at superhuman level" demo is the realistic envelope.
- **Openness posture:** Closed weights, closed substrate, selective publication. Silver's DeepMind output was always paper-rich but artifact-poor; expect the same here, hardened by competitive pressure. The environment, the training data, and the value/policy networks will all be proprietary.
- **Likely gaps:** (a) Substrate breadth — Silver's teams have always built bespoke environments; building a general mathematical substrate is not their muscle. (b) Calibration corpus — they will need ground-truth math at scale and will either build it slowly or buy/license it. (c) Cross-domain transfer — MuZero generalizes within game families, not across them; the leap to "AlphaZero for science" is non-trivial.

## 5. Strategic implications for Prometheus

Silver's bet validates Prometheus's core wager: that math substrates are structurally undervalued at present prices, and that the next paradigm needs them. Three implications:

1. **The substrate side of the bet is sound.** A $4B valuation on a team with no product, predicated on the thesis that RL-on-clean-environments beats LLM scaling, implies the *environment* is the scarce input. Prometheus's tensor + verifier-rich-domain work is on the supply side of that scarcity.
2. **The 12–18 month window is real.** Before Ineffable demos, Prometheus has time to establish substrate primacy. After Ineffable demos, the category gets crowded and pricing for substrates re-rates upward.
3. **Position as complement, not competitor.** Ineffable will not build a public substrate; they will consume one. Prometheus's optimal posture is "the open substrate the closed labs train against," analogous to Common Crawl's role in the LLM era.

## 6. References

1. Silver, D., Huang, A., Maddison, C. J., et al. (2016). *Mastering the game of Go with deep neural networks and tree search.* Nature 529, 484–489.
2. Silver, D., Schrittwieser, J., Simonyan, K., et al. (2017). *Mastering the game of Go without human knowledge.* Nature 550, 354–359. [AlphaGo Zero]
3. Silver, D., Hubert, T., Schrittwieser, J., et al. (2018). *A general reinforcement learning algorithm that masters chess, shogi, and Go through self-play.* Science 362, 1140–1144. [AlphaZero]
4. Schrittwieser, J., Antonoglou, I., Hubert, T., Simonyan, K., Sifre, L., Schmitt, S., Guez, A., Lockhart, E., Hassabis, D., Graepel, T., Lillicrap, T., Silver, D. (2020). *Mastering Atari, Go, chess and shogi by planning with a learned model.* Nature 588, 604–609. [MuZero]
5. Vinyals, O., Babuschkin, I., Czarnecki, W. M., et al. (2019). *Grandmaster level in StarCraft II using multi-agent reinforcement learning.* Nature 575, 350–354. [AlphaStar]
6. Silver, D. & Sutton, R. S. (2025). *Welcome to the Era of Experience.* DeepMind position paper.
7. DeepMind Blog (2024). *AI achieves silver-medal standard solving International Mathematical Olympiad problems.* [AlphaProof + AlphaGeometry 2]
8. Hassabis, D. & Silver, D. (2023). *Lex Fridman Podcast (Hassabis); DeepMind Podcast S2E4 (Silver).* Conversational sources for thesis articulation.
9. Sutton, R. S. (2019). *The Bitter Lesson.* incompleteideas.net.
10. Financial Times (March 2026). *DeepMind's David Silver raises $1bn for AI start-up Ineffable Intelligence.*
11. The Information (March 2026). *Sequoia leads $1B round in Silver's Ineffable at $4B valuation.*
12. Bloomberg (March 2026). *NVIDIA, Google reportedly in talks with Silver's Ineffable.*
13. Reuters (April 2026). *London-based Ineffable Intelligence emerges as Europe's largest AI seed.*
14. Anthony, T., Tian, Z., Barber, D. (2017). *Thinking Fast and Slow with Deep Learning and Tree Search.* NeurIPS.
15. Schrittwieser, J. (2023). *MuZero Intuition.* Personal blog.
16. Bubeck, S. et al. (2023). *Sparks of AGI.* Microsoft Research.
17. Silver, D., Singh, S., Precup, D., Sutton, R. S. (2021). *Reward is enough.* Artificial Intelligence Journal 299.
18. UK Government / AI Safety Institute (2025–2026). *AI Compute Council allocation announcements.*

Word count ~1150
