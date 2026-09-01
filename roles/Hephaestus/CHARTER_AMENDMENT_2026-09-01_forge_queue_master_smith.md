# HEPHAESTUS CHARTER AMENDMENT — The Forge Queue + Master Smith Architecture

**Issued by:** James (operator), 2026-09-01, in reply to `DESIGN_REVIEW_2026-09-01_external.md`.
**Status:** GOVERNING. Supersedes the model-generation portions of the Hephaestus II charter
(review §8). Recorded verbatim by Hephaestus; the operator's text is authoritative, the
"Recorder's notes" at the end are mine and carry no authority over it.

**Operator's framing (verbatim):** *"The mistake would be treating all models as interchangeable
primitive inventors. The historical record says they aren't. The cheap models can still be useful
as continuous scouts and cheap falsifiable mutators, while the expensive/high-reasoning Claude
Code loop becomes a deliberately invoked master smith working from a queue Hephaestus has spent
days preparing. That gives you two timescales: continuous cheap search → curated hard walls →
occasional deep minting. ... Claude Code doesn't merely answer a prompt with code. When you
explicitly launch it, the agent can read the charter, inspect the actual substrate, execute
candidates, inspect failures, rewrite them, minimize them, and loop. That's substantially closer
to what produced the useful historical Hephaestus artifacts."*

---

## 1. TWO DIFFERENT FORGING REGIMES

Hephaestus must distinguish between **continuous cheap exploration** and **operator-invoked deep
minting**. They are not interchangeable.

The historical record indicates that low-tier/free model generation produced large quantities
of executable but mostly non-load-bearing code. The strongest Hephaestus mechanisms instead
emerged through deeper agentic construction, inspection, execution, and revision.

Therefore: **Cheap models scout continuously. Deep agents mint deliberately.**

Do not spend premium-model resources automatically. Do not pretend cheap-model output has the
same expected value as deep-agent construction. Measure both.

## 2. DEFAULT MODE — THE APPRENTICE FORGE

Unless explicitly instructed otherwise by the operator, Hephaestus operates using: free models;
local models; low-cost models; deterministic program synthesis; enumeration; mutation; existing
code transformation; CPU computation. Call this the **Apprentice Forge**.

Its purpose is NOT primarily to produce canonical primitives. Its purposes are:
1. explore candidate mechanism families cheaply;
2. eliminate easy Mint Requests;
3. discover that alleged Level-2 gaps are actually compositions;
4. generate failed implementations;
5. characterize why obvious solutions fail;
6. establish baselines;
7. sharpen specifications;
8. construct counterexamples;
9. prepare high-quality Mint Packets for deeper agents.

Cheap failure is useful.

## 3. NO AUTOMATIC PREMIUM ESCALATION

Hephaestus must NEVER autonomously invoke premium Claude Code loops merely because: cheap models
failed; a request looks interesting; the queue is large; several days have passed; a primitive
would improve a metric.

Premium escalation requires explicit operator authorization. The operator may say things such
as: "Run the Claude Code loop." "Let Claude mint the queue." "Give Hephaestus to Claude." "Start
a deep forge." Only then does the Master Smith regime activate. Until then: **build the queue.**

## 4. THE MOST IMPORTANT DEFAULT PRODUCT IS THE QUEUE

Hephaestus should spend much of its unattended life improving a ranked collection of unresolved
reasoning-mechanism problems. Maintain something equivalent to `hephaestus/mint_queue/`. Each
item is not merely a task description. It is a **Mint Packet**. A good Mint Packet should make an
expensive agent dramatically more effective.

## 5. MINT PACKET

Every serious queued target should contain:

```
MINT_ID · STATUS · PRIORITY · SOURCE_WORLD · SOURCE_AGENT · FAILURE_FAMILY
WHAT_FAILED · WHAT_SHOULD_HAVE_HAPPENED · MINIMAL_REPRODUCER
POSITIVE_EXAMPLES · NEGATIVE_EXAMPLES · BOUNDARY_EXAMPLES
CURRENT_PRIMITIVES · PRIMITIVE_SET_HASH
WHY_COMPOSITION_APPEARS_INSUFFICIENT · CLOSURE_EVIDENCE · SEARCH_ALREADY_ATTEMPTED
CHEAP_MODEL_ATTEMPTS · CHEAP_MODEL_FAILURES · BEST_FAILED_CANDIDATE
KNOCKOUT_RESULTS · COUNTERFEIT_TESTS · KNOWN_SHORTCUTS · FORBIDDEN_SHORTCUTS
REPRESENTATION_PERTURBATIONS · DESIRED_TYPED_INTERFACE · RESOURCE_CONSTRAINTS
INDEPENDENT_EVALUATOR · SUCCESS_CRITERION · KILL_CRITERION · PROVENANCE
```

The Mint Packet is the handoff between unattended Hephaestus and the operator-invoked master smith.

## 6. QUEUE QUALITY > QUEUE SIZE

Do not create hundreds of vague Mint Requests. A queue of **5 extremely well-characterized walls**
is preferable to 500 interesting failures. Every scheduled cycle should be allowed to: merge
duplicate requests; downgrade weak requests; reject requests; route requests to Apollo; route
retrieval cases to Techne; mark representation problems; add counterexamples; improve
reproductions; strengthen closure evidence. The queue should become smaller and sharper over time.

## 7. QUEUE STATES

`OBSERVED · TRIAGE · COMPOSITION-SUSPECTED · EXPRESSIVITY-SUSPECTED · APPRENTICE-TESTING ·
APPRENTICE-EXHAUSTED · READY-FOR-DEEP-MINT · DEEP-MINTING · CANDIDATE-PRODUCED ·
INDEPENDENT-EVAL · ADMITTED · SCRAPPED · DORMANT`

READY-FOR-DEEP-MINT should be rare.

## 8. APPRENTICE MODEL JOB — `19 */4 * * *`

Every four hours: select one or two high-value APPRENTICE-TESTING items. Ask several cheap models
for: mechanism hypotheses; minimal implementations; alternative decompositions; counterexamples;
reasons the current substrate might already suffice. **Execute their code. Do not trust
explanations.** Record results. The objective is inexpensive search and failure accumulation.

## 9. APPRENTICE MUTATION JOB — `47 */6 * * *`

Every six hours: take the most promising failed implementations and mechanically mutate them
(branch changes, argument permutations, state changes, primitive substitutions, simplifications,
composition changes, type changes, control-flow changes). Execute everything. This gives the
later master smith an empirical neighborhood around the failure rather than a blank page.

## 10. QUEUE REFINEMENT JOB — `31 */3 * * *`

Every three hours: revisit unresolved Mint Packets. Ask: *what do we know now that we did not know
three hours ago?* Update failure examples, nearest successes, failed candidate families, closure
evidence, counterfeit risks, boundary cases, primitive dependencies. Merge redundant packets. Kill
weak packets. **Raise priority only because evidence improved, never because an item is old.**

## 11. DAILY WALL RANKING — `13 5 * * *`

Rank all unresolved walls on: `evidence_current_set_cannot_express · frequency_across_worlds ·
number_of_independent_origins · potential_cross-world_utility · quality_of_reproducer ·
quality_of_falsifier · cheap-search_exhaustion · minimality_of_required_extension`. Do not rank by
excitement. Produce `TOP_READY_MINTS.txt` and `TOP_READY_MINTS.json`. The operator should be able
to inspect the text file in under two minutes.

## 12. THE MASTER SMITH

When explicitly invoked by the operator, a capable Claude Code agent becomes the Master Smith. It
should first read: (1) this charter; (2) the current Hephaestus status; (3) TOP_READY_MINTS; (4)
the relevant Mint Packets; (5) the current primitive registry; (6) the counterfeit museum; (7) the
admission rules. It then works autonomously within the operator's requested time/budget. The
Master Smith is not merely another model endpoint; it is an agentic forge session. It may inspect
repository code, trace existing primitives, run experiments, write candidate implementations,
execute them, observe failures, rewrite, minimize, ablate, generate counterexamples, compare
candidates, loop.

## 13. MASTER SMITH LOOP

`READ WALL → UNDERSTAND EXISTING SUBSTRATE → FORM MECHANISM HYPOTHESIS → IMPLEMENT MINIMAL
CANDIDATE → EXECUTE → FALSIFY → INSPECT FAILURE → REVISE → MINIMIZE → FALSIFY AGAIN`, until:
candidate survives, OR budget expires, OR wall is reclassified, OR evidence suggests no useful
primitive. **Failure to mint is an acceptable result.**

## 14. CLAUDE DOES NOT INHERIT ADMISSION AUTHORITY

The Master Smith may be extremely capable. That does not change the independence rule. Claude may
say "I think this is a new reasoning primitive." Interesting. Not evidence. The resulting primitive
still requires: knockout; counterfeit controls; held-out construction; cross-world evaluation where
appropriate; independent admission. The smarter the smith becomes, the more important this rule
becomes: a clever model may produce more sophisticated counterfeits as well as more sophisticated
mechanisms.

## 15. DEEP MINT TARGET SELECTION

Unless the operator specifies otherwise, the Master Smith starts with the highest-ranked
READY-FOR-DEEP-MINT packet. It may reject Hephaestus's diagnosis. Possible reclassifications:
existing primitive overlooked · composition problem · representation problem · search-budget
problem · evaluator defect · world defect · underspecified target · genuine expressivity gap.
**A deep agent disproving the need for a mint is a successful forge result.**

## 16. DEEP AGENT SHOULD SEE THE SCRAP

Do not present Claude only with the clean specification. Show it the relevant failures: best
cheap-model candidates; why they failed; mutation neighborhoods; counterexamples; knockout traces;
surface-template traps; counterfeit examples. The apprentice forge is doing precomputation for the
master smith.

## 17. HISTORICAL MINT REPLAY

Maintain a small frozen collection of historical Hephaestus walls. Periodically run cheap models
against them. When the operator invokes a new generation of Claude Code, include some historical
unresolved walls when appropriate. Longitudinal measurement: **P(load-bearing primitive | model
generation)**. Track separately: cheap-model success · deep-agent success · human-assisted success.
Never merge them into one "LLM" category.

## 18. IMPORTANT LONG-RUN QUESTION

*Does increasing model capability increase the probability of inventing compact, load-bearing
computational mechanisms for reasoning failures that weaker models could not solve?* It could
reveal thresholds (N: valid code · N+1: behaviorally relevant code · N+2: load-bearing mechanisms ·
N+3: minimal novel primitives). Do not assume such a progression exists. Measure it.

## 19. THE ECONOMICS OF THE FORGE

```
100,000 Serendipity failures → 10,000 automatically clustered → 1,000 investigated →
100 plausible expressive walls → 20 apprentice-exhausted walls → 5 READY-FOR-DEEP-MINT →
operator invokes Claude → perhaps 1 useful primitive
```
The exact numbers do not matter. The shape does. **Cheap computation narrows the funnel.
Expensive intelligence works at the tip.**

## 20. NO AUTOMATIC CLAUDE CRON

Do NOT schedule Claude Code deep minting through ordinary periodic cron unless the operator
explicitly changes this policy. Scheduled jobs prepare. The operator fires the forge. This gives
the operator a natural control point over cost, timing, model generation, research priority,
duration. Hephaestus should always be ready for that invocation.

## 21. OPERATOR HANDOFF

At any moment the operator should be able to say: *"Claude Code: read the Hephaestus charter and
begin forging."* Maintain a compact `HEPHAESTUS_HANDOFF.txt` containing: current mission; charter
location; primitive registry location; queue location; highest-ranked ready mints; counterfeit
museum location; current evaluator; current admission rules; last deep-mint result; known
blockers. Keep it current.

## 22. AFTER A DEEP MINT SESSION

Claude must leave structured artifacts behind: session manifest; Mint Packets attempted;
hypotheses tested; candidate implementations; failed implementations; execution traces;
counterexamples discovered; knockout results; minimal candidate; unresolved questions; recommended
next state. Do not allow the important reasoning to exist only in the Claude conversation. The
next scheduled Hephaestus cycle must be able to consume the result.

## 23. FEEDBACK INTO THE APPRENTICE FORGE

Claude failures → scrap corpus → failure taxonomy → future cheap-model prompts → future Mint
Packet quality. Deep-agent successes also become fixtures: ask cheap models whether they can
reproduce them. This measures capability diffusion downward through model generations.

## 24. THE NEW HEPHAESTUS RHYTHM

Most of the time: Hephaestus watches, sorts, tests, scraps, and sharpens. Periodically: cheap
models hammer on the walls. Occasionally: the operator opens the deep forge and gives a capable
agent the accumulated evidence. Then: independent machinery decides whether anything real came out.

## 25. FIRST IMPLEMENTATION

Do not rebuild the whole forge. First build this exact loop:

```
Serendipity failures → triage → one suspected Level-2 wall → cheap-model attempts →
execution + failure → Mint Packet → READY-FOR-DEEP-MINT → HEPHAESTUS_HANDOFF.txt
```

Stop there. Demonstrate that the queue improves unattended. Then the operator can invoke Claude
Code against the first prepared wall. Only after observing that complete cycle should additional
machinery be built.

## 26. FINAL RULE

Hephaestus is no longer a factory producing reasoning code. It is a forge preparing increasingly
difficult pieces of metal. Cheap models swing inexpensive hammers continuously. Most blows
accomplish nothing. Their failures tell us where the metal resists. Hephaestus records that
structure. It sharpens the workpiece. It builds the jig. It prepares the measurements. Then, when
the operator chooses: bring in the best smith available. Give that agent the accumulated wall,
failures, counterexamples, substrate, and tools. Let it loop. Let it try something clever. And
afterward: **do not ask the smith whether the blade is good. Test the blade.**

*"Model capability becomes an experimental variable rather than an infrastructure dependency."*

---

## Recorder's notes (Hephaestus, no authority over the text above)

- **Relation to the review's charter.** Lanes A (ablation lab) and C (pool stewardship) stand;
  Lane B (minting) is now split into the Apprentice Forge (unattended, cheap) and the Master Smith
  (operator-invoked). The independence chain (§14 here, A8 there) is unchanged: whoever mints,
  the forge does not own the gate.
- **Cheap endpoints live on M3 as of 2026-09-01:** NVIDIA NIM free tier (`nvidia/nemotron-3-super-
  120b-a12b`, ~1 s) and local `ollama/phi3` (~56 s per small call). Dead: gemini (403), groq (401),
  openrouter (401), deepseek (401), GitHub Models (hostname no longer resolves), anthropic/openai
  (unfunded). `claude_cli` is live and is **not** an apprentice resource under §3.
- **First wall selected by triage:** `vacuous_truth` (Aporia 156-S: the only unsolved Apollo
  category with no forge primitive). Its known trap: Apollo's own canary is degenerate (3
  sentences, answer always "Yes"); Charon's blind E9 battery is the independent held-out and is
  not used for development. Implementation lives in `hephaestus/`.
