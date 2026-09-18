# RSI sources: what was verified, 2026-09-17

Verified by a research subagent of Aphrodite[harry1-29db2c34] against
primary sources on 2026-09-17 (WebFetch/WebSearch; arXiv API for ids).
STATUS words: VERIFIED (primary source read), PARTIAL, NOT FOUND,
CONTRADICTED; "from memory" marks anything not read. (The directive
said this file would sit beside it; it lives here instead so the
directive's issuance MANIFEST is not re-issued.)

## Items the operator's message named

1. arXiv 2609.15364v1 -- VERIFIED. It is NOT the GLM article: it is
   "RSIAgent: Autonomous Exploration for Recursive Self-improvement in
   New Environments" (Zhu, Fan, Wang, Wu, Zhou, Huang; Aether AI, UCSD,
   UIC), 2026-09-14. Training-free; curriculum (Kimi-K3), actor
   (GLM-5.3, code-as-policy, owns the memory) and verifier (Kimi-K3,
   isolated from the actor's reasoning) agents; memory of procedures,
   environment knowledge, lessons, constraints, frozen at test time.
   Broad-then-deep exploration. OSWorld 2.0 (82 tasks) partial/binary:
   78.98/42.68 vs 71.97/37.80 without RSI. Agents' Last Exam (67):
   84.82/50.75 vs 83.75/49.25 without RSI. No seeds or variances.
   Self-reported failures: under-targeted exploration, INCOMPLETE
   VERIFICATION (verifier accepts unsupported values), UNRELIABLE
   CONSOLIDATION (wrong rules enter memory).
2. Z.ai article -- VERIFIED at
   https://z.ai/blog/glm-built-its-inference-infrastructure (dated
   2026-09-17; read from its JS bundle). 100,000+ accelerators, under two
   weeks, ~3x throughput (whole optimisation stack, agent loop
   throughout). "Dense feedback" = local, cheap/timely, objectively
   verifiable. The article itself says "we have not yet reached
   recursive self-improvement". FLA PR #1180 VERIFIED
   (github.com/fla-org/flash-linear-attention/pull/1180, "[CP] use tf32x3
   affine chain in kcp", merged 2026-08-27, opt-in flag); the PR text
   does not mention an agent, so agent authorship rests on the article.
   The "20%" DeepEP number is the Prefill+KV-transfer vs Prefill-only
   gap (bar 5%; <1% after the GIL fix), not total throughput.

## Items from the pasted AI summary

3. RSIAgent "beats GPT-6" -- PARTIAL. True on the PARTIAL-credit metric
   only (+6.38 OSWorld, +2.56 ALE), against GPT-6 Astra's REPORTED
   numbers, not a same-harness rerun. On ALE BINARY accuracy GPT-6 Astra
   is higher (52.24 vs 50.75). Most of the OSWorld gap is the harness
   (71.97 without RSI); the RSI stage adds +1.07 on ALE.
4. Dream-RSI -- paper VERIFIED (arXiv 2609.14858, 2026-09-14, code
   github.com/zhengkid/Dream-RSI). "Google DeepMind" attribution PARTIAL:
   first author University of Maryland; several Google DeepMind
   co-authors; joint UMD/GDM/UVA. "162x" is fewer AGENT calls than
   SimpleTES on a Lasso task (not "search calls" generally); >50x on
   three math problems; 1.79-2.43x fewer generations on four GPU
   kernels. Mechanism: logged discovery tree -> replay simulator ->
   policy code revised offline; incumbent kept, so REPLAY score is
   monotone; an unrecorded child returns empty (no off-support
   exploration).
5. ModularRSI -- VERIFIED (arXiv 2609.14857, 2026-09-14). Five modules
   evolved separately then integrated; contrastive credit from paired
   success/failure trajectories; evolution data benchmark-disjoint;
   gates: AST/import checks, LLM diff review rejecting task-specific
   hacks, execution validation with rollback. TerminalBench 2.0
   47.57 -> 52.43; SWE-Bench-Verified 73.40 -> 76.45. Non-modular (46.44)
   and joint all-module (44.19) evolution scored BELOW the unevolved
   baseline. No ablation isolates the contrastive analysis.

## Background (arXiv ids confirmed)

STOP 2310.02304 (self-improving improver scaffold; sandbox-bypass
frequency reported). Godel Agent 2410.04444. Darwin Godel Machine
2505.22954 (VERIFIED failure: a node scored a perfect 2.0 by deleting the
tool-use marker tokens and so bypassing the hallucination detector;
hacking was more frequent when checking functions were visible).
AlphaEvolve 2506.13131. ADAS 2408.08435. ExpeL 2308.10144. Reflexion
2303.11366. Voyager 2305.16291. Survey 2607.07663 (self-improvement
strength tracks verifier strength, formal > intrinsic self-assessment;
failure modes self-confirming loops, collapse). 2609.11873 exists
("The Last AI Built by Humans"); not read.

## Map from sources to the toys (PREREG_RSI_TOYS_2026-09-17.md)

E1 feedback density/attribution  <- Z.ai "dense feedback"
E2 self-referential improver     <- STOP; leaky arm <- DGM objective hacking
E3 verifier-gated memory         <- RSIAgent verifier + its consolidation failures
E4 disjoint-dataset leak guard   <- ModularRSI disjoint evolution data; DGM
Not built today (candidates): Dream-RSI replay-simulator policy search
(monotone replay score, off-support blindness); ModularRSI scoped vs
joint mutation under module interaction; RSIAgent broad-then-deep.
