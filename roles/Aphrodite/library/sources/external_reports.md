# External research reports held by other seats (pointers, not copies)

Currency: 2026-09-18. Owner: Aphrodite. Each entry points at another
seat's committed report, records what the library takes from it, and
what it must not take. The report stays in its owner's lane.

## XR-1 Aporia: Gemini Deep Research on RSI 2024-2026, with citation audit

- where: aporia/docs/deep_research_batch_2026-09-17/
  01_recursive_self_improvement_2024_2026_which_reported_successe.md
  (report, 33.5 KB), VERIFICATION_2026-09-17.md (audit),
  aporia/docs/gemini_deep_research_deck_2026-09-17.md (deck).
  Commits e0e78040f (report, deck, dispatch) and 9d7263f47 (audit);
  both verified as ancestors of origin/main by this seat on 2026-09-18.
- tier: the report is SECONDARY (a Gemini Deep Research synthesis whose
  links are all vertexaisearch redirects); Aporia's audit is a
  source-identity check (8/8 arXiv ids resolve; 5 attribution/venue
  errors).
- the library takes (after Aporia's edits): the tier taxonomy
  (scaffold / data / weights / evaluator), which matches rsi_core.md's
  "modifies" field; the finding that nearly all headline RSI is
  scaffold-level search over frozen weights (supports THEORIES T0); and
  that weight-level self-play compounding saturates within a few
  iterations -- SPIN's reward advantage vanishes across iterations,
  per its NeurIPS 2025 follow-ups T-SPIN (arXiv 2601.08198) and SPACE
  (arXiv 2512.07175). STOP's verbatim self-assessment ("Since the
  language models themselves are not altered, this is not full
  recursive self-improvement") is confirmed in the abstract.
- the library must NOT take:
  E1 the "AlphaEvolve does not compound" quote (0.791 -> 0.797 after
     100 iterations) as DeepMind's own ablation: it is from Liu et al.,
     "Scientific Algorithm Discovery by Augmenting AlphaEvolve with Deep
     Research", arXiv 2510.06056, a competitor's baseline run;
  E2 arXiv 2511.02864 as an AlphaEvolve source paper (it is Georgiev,
     Gomez-Serrano, Tao, Wagner, an application paper);
  E4 arXiv 2508.06026 as T-SPIN/SPACE (it is Temporal Self-Rewarding
     LMs);
  E5 "AI Scientist papers withdrawn over double-blind violations": the
     ICLR 2025 workshop submission was made with the organisers'
     cooperation under IRB approval and withdrawn by prior commitment;
  the report's Section C figures (the report's own estimates, unsourced).
- CORRECTION TO THE AUDIT (this seat, 2026-09-18): Aporia's E3 says the
  Darwin Godel Machine's ICLR 2026 status is "unsupported; treat as
  preprint". It is supported: ICLR 2026 poster
  (iclr.cc/virtual/2026/poster/10007327), the arXiv v3 PDF is headed
  "Published as a conference paper at ICLR 2026", and the ML Anthology
  lists it (zhang2026iclr-darwin). rsi_core.md's "ICLR 2026" for DGM
  stands. Sent to Aporia on comms.
- instrument lesson worth keeping (Aporia's): all five hypotheses the
  requester framed came back CONFIRMED; a synthesis that agrees with
  its prompt on every point is the one to distrust most. This applies
  to this seat's own deep-research run of 2026-09-18 (framed questions,
  results pending): its agreement with the v2 design is not evidence.


--------------------------------------------------------------------------
RELAYED COMMENTARY, 2026-09-21 (source not named by the operator)
--------------------------------------------------------------------------
Verbatim, as relayed:

  "For recursive self-improvement to actually work, the system must be
  able to reliably judge if a mutated reasoning substrate is genuinely
  better than the previous version. If the system cannot run rigorous
  falsification testing on its own outputs without a human in the loop,
  the evolutionary engine just optimizes for highly confident
  hallucinations. Evolution requires an unforgiving environment to test
  against, and building that automated 'reality check' for abstract
  logic is incredibly difficult.
  Second, there is the sheer complexity of state and communication. True
  open-ended evolution requires agents to constantly spin up, test
  hypotheses, share context, and overwrite themselves. That requires
  highly robust underlying infrastructure -- event streams that can route
  complex inter-agent messaging, and databases that can persist massive,
  multi-threaded reasoning traces without latency choking the system to
  death.
  We are no longer just training models; we are trying to engineer
  computational ecosystems. The frontier has shifted away from making a
  single monolithic network smarter, and toward how efficiently we can
  assemble the frameworks that let these intelligence primitives
  experiment on themselves."

WHAT THE LIBRARY TAKES (this seat, 2026-09-21):
- Claim 1 (the evaluator is the bottleneck) is ACCEPTED as a restatement
  of T6 and of one of the five confounds the charter names by name
  (evaluator exploitation). It is the deepest of the three claims.
- Claim 1 is ALSO INCOMPLETE, and this seat has a same-day measurement
  that shows how. The local engine's evaluator is a perfect oracle:
  deterministic gold answers, no model judging a model, no hallucination
  channel at all. Evolution still produced exactly nothing -- 10 of 10
  lineages returned artifacts byte-identical to the base image, dev
  scores [1.0]*8 (engine/QUALIFICATION_2026-09-21.json). An unforgiving
  judge is necessary and NOT sufficient. See T9.
- Claim 2 (infrastructure: event streams, databases, latency) is NOT
  accepted as a claim about the SCIENCE. The same engine runs 5,577
  lineages/hour on one core with no event stream, no database, no
  inter-agent messaging and no persisted reasoning traces, because the
  causal question needs the smallest auditable membrane, not an
  ecosystem. Claim 2 is a claim about building a PRODUCT. Conflating the
  two is the failure mode the operator named on the same day: "the
  engine is not the product. The causal artifact is."
- Claim 3 ("the frontier has shifted to assembling frameworks") is
  logged as a FIELD-SENTIMENT datum, not as evidence. Note that it would
  license exactly the scope creep the seat's own review packet asked
  about in Q6 ("Should this engine exist, or is it tractable work
  standing in for the real blocker?"). A commentary that recommends more
  framework-building should not be read uncritically at a moment when
  the seat is already tempted to build framework.
