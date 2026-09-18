# Operator directive, 2026-09-17 (chat, to Aphrodite[harry1-29db2c34])

The operator's own words, verbatim:

    I'd like you to research RSI and build small prototypes testing the
    concept with simple python tests.  Lots of recent papers and news
    emerging around this:  https://arxiv.org/html/2609.15364v1, Toward
    Recursive Self-Improvement: How GLM Built Its Own Inference
    Infrastructure

The message then pasted two bodies of text that are NOT the operator's
words and are NOT reproduced here, because this repository is public
(unauthenticated GitHub API returned 200 on 2026-09-17) and the first is
a third party's published article:

1. The Z.ai (Zhipu) article "Toward Recursive Self-Improvement: How GLM
   Built Its Own Inference Infrastructure" (GLM-5.3-Flash, an "Infra
   Agent", "dense feedback": local, cheap/timely, objectively verifiable
   feedback; three cases: KDA kernel CP-path precision fix via
   input_precision="tf32x3", Flash Linear Attention PR #1180; a DeepEP
   intranode GIL-holding bottleneck blocking Mooncake KV transfer; a KDA
   decode kernel sped up via "optimization skeletons"). Cited by title;
   summarised in one clause each so the prototypes' sources are traceable.
2. A block that reads as an AI-assistant summary (it ends "Would you like
   to dive deeper ... ?"), asserting three further items: "RSIAgent"
   (training-free curriculum/actor/verifier agents distilling a
   structured memory pool; claimed to lift GLM-5.3 and Kimi-K3 above
   "GPT-6"), "Dream-RSI" attributed to Google DeepMind (history distilled
   into a replay simulator, offline "dreaming" of orchestration policies,
   "162x" fewer search calls), and "ModularRSI" (a five-module evolvable
   harness evolved with contrastive trajectories across disjoint
   datasets to prevent cheating/overfitting). Every claim in block 2 is
   UNVERIFIED at issuance; verification status is recorded in
   SOURCES.md in this directory once checked against primary sources.

Seat reading (Aphrodite's, not the operator's): this is the seat's first
commission. It does not by itself replace the pending charter
(APHRODITE-01). Deliverables: a verified source note, small deterministic
Python prototypes of the mechanisms, pytest tests with positive, negative
and cheat controls, a preregistration committed before any result, and a
review packet.
