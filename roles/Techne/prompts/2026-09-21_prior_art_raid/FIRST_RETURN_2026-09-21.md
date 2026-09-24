# PRIOR-ART RAID -- FIRST RETURN (section XV)
Techne[gandalf-a04f7c25], M3, 2026-09-21. Directive: roles/Techne/prompts/2026-09-21_prior_art_raid/
OPERATOR_7_prior_art_raid.md (MANIFEST beside it). This answers section XV only (Voyager, SIMA 2,
Genie 3, fifth-engine feasibility). Sections I.B-XIV (the full raid: MCC/POET/ATEP/PLR/ACCEL/JaxUED/
OMNI-EPIC, QDax/AURORA, the digital-life lineage, OpenEvolve/DGM/GEA, skill-memory beyond Voyager,
AI Scientist v2, model-merge evolution, and the citation-graph search for unnamed systems) are NOT
done; each needs the same source-level treatment given here and is properly several more passes, not
one. Scope call stated up front, not buried: see closing section.

Every claim below is sourced to a primary document fetched today (GitHub API, arXiv API, or the
publisher's own page) or to source code read in full at a pinned commit. Nothing is from training
memory. Grades used: VERIFIED_SOURCE (code read at the pin), VERIFIED_API (repo/paper metadata),
PRIMARY_QUOTE (fetched from the lab's own page, quoted), NO_PUBLIC_SOURCE (searched, not found).

## A. VOYAGER

**Canonical repository.** github.com/MineDojo/Voyager, MIT licence (GitHub API), 7,221 stars, last
push 2024-04-03, not archived. Paper arXiv:2305.16291 (v1 2023-05-25, v2 2023-10-19, Wang/Xie/
Jiang/Mandlekar/Xiao/Zhu/Fan/Anandkumar). Pinned at commit 55e45a880755d0c8c66ca7fb5fe7962ac8974f89
and fossilized (techne/fossils/specimens/voyager-minedojo-2023, tree 23097fcc.., 457 files, verified).

**Runs?** SOURCE_ONLY here. The code is genuine and inspectable (source-level autopsy done below,
every function read at the pin), but execution needs a licensed Minecraft Java Edition client, a
Node.js mineflayer bridge, and a paid OpenAI API key (GPT-4/GPT-3.5). None were exercised: standing
rule 11 (no spending without authorization) and the M3 host both apply. This is a BLOCKED-not-FAILED
distinction: nothing about the code itself is in question.

**Skill-library architecture, exact** (voyager/agents/skill.py, class SkillManager):
  - a skill is `{"code": <JS source>, "description": <LLM-generated NL string>}`, keyed by
    `program_name` (the JS function's own name), stored in `skills.json` AND as a Chroma vector-store
    entry whose embedded text is the description (OpenAIEmbeddings). The two are asserted in sync at
    load time (`vectordb._collection.count() == len(skills)`).
  - `add_new_skill(info)`: called only after `CriticAgent` reports success. Generates the description
    with a second LLM call (`generate_skill_description`: the same code, prompt "skill", asked to
    summarise). A name COLLISION does not overwrite silently: the old vector-store entry is deleted,
    the code is versioned to disk as `<name>V2.js`, `V3.js`, ... but the IN-MEMORY dict is keyed by
    the bare name (i.e. only the newest version is retrievable at runtime; older versions survive
    only as files). One hardcoded exception: the chest-deposit skill is never persisted.
  - `retrieve_skills(query)`: `k = min(count, retrieval_top_k=5)`; `Chroma.similarity_search_with_score`
    against the query text (the current task context + a chat-log summary of the last rollout);
    returns the top-k skills' CODE (not description) to be spliced into the next prompt.
  - `.programs` property: every stored skill's code + every CONTROL PRIMITIVE's code, concatenated,
    forms the full "language" the action agent's generated code may call. Primitives
    (voyager/control_primitives/*.js: craftItem, mineBlock, killMob, placeItem, smeltItem, shoot,
    useChest, exploreUntil, waitForMobRemoved, givePlacedItemBack, craftHelper) are FIXED and never
    grow; skills are the only thing that accumulates.

**Automatic-curriculum architecture, exact** (voyager/agents/curriculum.py, class CurriculumAgent):
  - `propose_next_task`: three tiers, in order. (1) hardcoded bootstrap: the very first task is always
    "Mine 1 wood log" (`self.progress == 0`). (2) hardcoded homeostasis: if inventory >= 33/36 slots,
    force a deposit/place-chest/craft-chest task regardless of what an LLM would propose -- an
    ESCAPE HATCH from the LLM entirely, driven by a numeric threshold on live world state. (3)
    otherwise, `propose_next_ai_task`: render a system prompt + a human message built from 14
    observation channels (`curriculum_observations`: context, biome, time, nearby_blocks,
    other_blocks, nearby_entities, health, hunger, position, equipment, inventory, chests,
    completed_tasks, failed_tasks), each independently gated by a per-channel WARM-UP COUNTER
    (`default_warmup`, e.g. biome shown only after 10 iterations, position never shown at all) so the
    prompt's information density grows with experience rather than being constant. An `update_exploration_progress`
    call after every rollout appends the task to `completed_tasks` or `failed_tasks` (used both as
    LLM context and to detect no-progress loops via `clean_up_tasks`).
  - `decompose_task` + the `run_qa` two-step QA (ask clarifying questions, answer them, cache
    question->answer pairs in a second Chroma store) exist as a SEPARATE evaluation-mode capability
    (`Voyager.inference`), not part of the open-ended `learn()` loop itself.

**Self-verification / iterative prompting, exact:**
  - `ActionAgent.process_ai_message` (voyager/agents/action.py): parses the LLM's JS code block with
    `@babel/core`; asserts at least one function, finds the LAST async function as the entry point,
    asserts its single parameter is named `bot`. A parse failure retries the SAME LLM call up to 3
    times before giving up (as a STRING, which `Voyager.step()` detects via `isinstance(str)` and
    re-prompts). This is purely syntactic self-repair, separate from semantic critique.
  - Execution feedback: the env step returns `events`; any `onError` event is collected and rendered
    verbatim into the NEXT human message as `"Execution error:\n<text>\n\n"` (or "No error" if none) --
    the loop's only mechanism for "the code ran but broke."
  - `CriticAgent.check_task_success` (agents/critic.py): a THIRD, independent LLM call (not the
    action agent) given the full post-execution observation (biome, health, hunger, position,
    equipment, inventory, nearby blocks, chests) plus the task and context, asked to return
    `{"success": bool, "critique": str}` as JSON (`ai_check_task_success`, with its own 5-retry
    parse loop; a `human_check_task_success` manual mode also exists). The critique text is spliced
    into the action agent's next human message. Task success is therefore judged by a SEPARATE
    prompt/model call from the one that wrote the code, on OBSERVED WORLD STATE, never on the code
    or the model's own claim -- an external-oracle pattern, not self-report.

**What is genuinely environment-independent vs Minecraft-coupled.** Independent: the skill
representation (name + NL description + executable payload + embedding-indexed retrieval), the
curriculum's warm-up-gated observation renderer, the critic's separate-oracle verification pattern,
the syntactic-retry / semantic-critique two-tier error handling, the deposit-when-full style of
hardcoded homeostatic escape hatches. Minecraft-coupled: `voyager/env/bridge.py` and the mineflayer
JS bridge (the entire action space is JS calls into a Minecraft bot API); the 14 observation channels
are Minecraft-specific fields; `control_primitives` are Minecraft actions; the "code" a skill IS is
JavaScript executed inside that bridge. The extraction boundary is therefore exactly the
`SkillManager`/`CurriculumAgent`/`CriticAgent`/`ActionAgent` classes MINUS their Minecraft-specific
observation renderers and MINUS the JS execution sandbox -- an environment-independent core plus a
per-substrate adapter, which is precisely the "environment interface" shape Prometheus's SFE/BEE
lane already uses.

**First 3-5 organs worth fossilizing** (source now preserved whole at the pin; these are the
extraction targets for a later adapt pass, TAKE-graded):
  1. SkillManager's skill schema + versioning + vector retrieval (skill.py, ~130 lines) -- TAKE.
     Substrate-independent as written; only needs an embedding backend and a "programs" execution
     context, both of which Prometheus already has analogues for.
  2. The two-tier error-handling pattern (syntactic parse-retry vs semantic execution-error injection
     into the next prompt) -- ADAPT. The specific implementation is JS/babel-bound; the PATTERN
     (never re-prompt on a parse failure the same way as a runtime failure) is substrate-agnostic.
  3. CriticAgent's separate-oracle verification (a second, independently-prompted judge over raw
     world state, never over the code) -- LEARN_FROM. Prometheus's own doctrine ("no LLM adjudicates";
     Harmonia as an independent ruler) already enforces something stricter; Voyager's version is the
     weaker LLM-only case, useful as a documented failure mode to avoid, not a component to import.
  4. The warm-up-gated, per-channel observation renderer (curriculum.py `render_observation`) --
     ADAPT. A reusable pattern for growing prompt complexity with agent experience.
  5. The homeostatic hardcoded-escape-hatch pattern (deposit-when-full overriding the LLM curriculum
     entirely) -- LEARN_FROM. A concrete example of "do not let the curriculum generator get to
     decide everything"; relevant to any Prometheus curriculum-generation component.

**The deeper skill abstraction, answered.** A Voyager skill is NOT "JavaScript Minecraft routine."
By the code's own schema it is exactly four things: a stable NAME, a NATURAL-LANGUAGE DESCRIPTION
(used only for retrieval, never for execution), an EXECUTABLE PAYLOAD in whatever language the
substrate's action space accepts, and an EMBEDDING KEY. Nothing in `SkillManager` inspects the
payload's language or structure -- it is opaque text concatenated into a "programs" string and handed
to the substrate's executor. That schema is substrate-independent by construction: the payload could
be Python, a graph, a policy checkpoint reference, or a Prometheus fossil-packet HANDOFF.demonstration
command, and the class would not need to change. This is the same shape as the CAPSULE and
FOSSIL_PACKET.HANDOFF objects Techne already built for the ASAL branch (2026-09-18/19), and the same
shape Nyx's mechanism ledger (operator directive 6) was asked to adopt -- three independently-arrived-at
designs converging on {id, description, executable payload, provenance, retrieval key}. Worth flagging
to Nyx and Harmonia directly, not just noting here.

## B. SIMA 2

**Complete primary-source set found:** arXiv:2512.04797 ("SIMA 2: A Generalist Embodied Agent for
Virtual Worlds", SIMA Team, 65+ authors, published 2025-12-04, VERIFIED_API from the arXiv Atom feed);
DeepMind's own blog post (deepmind.google/blog/sima-2-an-agent-that-plays-reasons-and-learns-with-you-in-virtual-3d-worlds,
fetched today, PRIMARY_QUOTE); a technical report PDF linked from that post
(storage.googleapis.com/deepmind-media/.../SIMA_Tech_Report_2025.pdf, located, not yet fully read --
next pass). Predecessor: arXiv:2404.10179 ("Scaling Instructable Agents Across Many Simulated
Worlds", SIMA Team, 2024-03-13).

**Official code or weights: NO**, verified by direct quote from DeepMind's own post, not inferred
from search-result absence (directive rule 5): *"we are announcing SIMA 2 as a limited research
preview and providing early access to a small cohort of academics and game developers."* No weights,
no training data, no code repository is offered.

**Self-improvement mechanism, as precisely as public evidence allows** (PRIMARY_QUOTE, DeepMind's
blog): Gemini plays two roles simultaneously -- "Task Setter" (proposing achievable-looking
instructions from the current state) and reward model ("a function that provides a reward for any
possible task"). The loop: Gemini gives an initial task and an estimated reward for SIMA 2's
attempted behaviour; that record is added to "a bank of self-generated experience"; the agent
retrains on that bank in subsequent generations. Stated capability: *"SIMA 2 can transition to
learning in new games exclusively through self-directed play, developing its skills in previously
unseen worlds without additional human-generated data."* No public evidence describes the retraining
algorithm itself (RL? behaviour cloning on self-labelled trajectories? both?) -- that is exactly the
kind of detail the linked technical-report PDF may or may not contain; not yet checked.
Stated limitations (all direct quotes): long-horizon multi-step reasoning is still hard; the agent
"must use a limited context window to achieve low-latency interaction" (short memory, by design, not
oversight); "executing precise, low-level actions ... and achieving robust visual understanding ...
remain open challenges." Genie 3 integration is explicit and demonstrated (see D below).

**Closest open donor implementations, graded honestly.** kyegomez/SIMA (github.com/kyegomez/SIMA,
MIT, 35 stars, last push 2024-06-17) claims to be a "Pytorch Implementation of Deepmind's SIMA" but
on inspection (README + package usage) is an UNTRAINED, GENERIC encoder-decoder transformer stub
(`SimaTransformer(dim=..., enc_depth=..., dec_depth=...)`) with no training data, no simulated-world
integration, and no evidence it reproduces any SIMA-specific mechanism. Grade: TOY_CLONE. It is NOT
equivalent to the real system and should not be cited as if it demonstrates SIMA's architecture. No
other candidate reproduction was found in this pass. NO_PUBLIC_SOURCE for a faithful open SIMA/SIMA-2
reproduction.

## C. GENIE 3

**Complete primary-source set found:** DeepMind's blog post (deepmind.google/blog/genie-3-a-new-
frontier-for-world-models, fetched today, PRIMARY_QUOTE); the Genie lineage's Wikipedia summary
(secondary, used only for the generation timeline, not for technical claims). NO arXiv paper: the
"Genie Architecture Paper" is explicitly listed on the model's own resource page as "Coming Soon"
(found via WebSearch of genie3.org/resources; not independently re-verified today by direct fetch --
flagged as a gap for the next pass). Lineage per secondary sources (timeline only, treat as
unverified until the primary papers are read directly): Genie 1 (Feb 2024, 2D platformer worlds,
256x256, DOES have a published arXiv paper from that generation -- to be pinned next pass); Genie 2
(Dec 2024, 3D, no paper found yet); Genie 3 (Aug 2025 preview, Jan 2026 wider "Project Genie" access).

**Code/weights/API/access status: NOT PUBLIC, restricted preview**, direct quote: *"we are announcing
Genie 3 as a limited research preview, providing early access to a small cohort of academics and
creators"*; a wider "Project Genie" surfaced to Google AI Ultra subscribers in the US as of
2026-01-29 (per WebSearch; not yet independently confirmed by fetching that specific announcement --
next pass), still API-only, no weights, no architecture paper.

**Architecture disclosed:** minimal. Direct quotes only: "auto-regressive generation of each frame"
conditioned on "the previously generated trajectory" (i.e. autoregressive over its own generated
history, not just the prompt); described elsewhere (secondary sources, Wikipedia/press) as an
"autoregressive latent diffusion model," which is plausible but NOT confirmed by DeepMind's own
public text and should be treated as unverified until the architecture paper exists.

**Stated limitations, direct quotes:** duration "a few minutes of continuous interaction"; 720p at
24 fps; action richness "currently constrained"; multi-agent interaction "still an ongoing research
challenge"; text rendering only reliable "when provided in the input world description."

**SIMA integration, confirmed:** *"we generated worlds for a recent version of our SIMA agent"* to
*"test the compatibility of Genie 3 created worlds for future agent training,"* and separately (SIMA
2 blog) *"we combined it with ... Genie 3 ... SIMA 2 was able to sensibly orient itself, understand
user instructions, and take meaningful actions toward goals"* in those generated worlds. This is the
one place the two systems are confirmed, by DeepMind itself, to compose.

**Closest OPEN substitutes, ranked by the requested criteria (openness / controllability / determinism
/ compute / persistence horizon / action richness / agent compatibility / instrumentability /
suitability for evolutionary experiments):**
  1. **open-oasis** (github.com/etched-ai/open-oasis, MIT, 2,137 stars, weights on HF as
     Etched/oasis-500m). Genuinely runnable: `dit.py` (a diffusion transformer) + `vae.py` +
     `generate.py`, action-conditioned frame generation on a Minecraft-like world. HIGHEST openness
     (full weights + inference code); moderate everything else -- 500M params, single-GPU-plausible,
     unknown persistence horizon (not yet measured), action space limited to keyboard/mouse-style
     inputs. Best candidate for an actual local instrument.
  2. **microsoft/mineworld** (MIT, 493 stars, active -- pushed 2026-05-08, MOST RECENTLY MAINTAINED
     of the three). arXiv:2504.08388. A visual-action autoregressive transformer, real-time at 4-7
     fps via a parallel/"diagonal" decoding trick, explicitly framed by its own paper as "a fully-
     permissive counterpart to Oasis." Open code; weights availability on Hugging Face was not
     resolved today (the model page returned zero file siblings, worth a direct check next pass).
  3. **SkyworkAI/Matrix-Game** (MIT, 2,336 stars, pushed 2026-03-30) and its "Matrix-Game 2.0"
     successor (paper arXiv:2508.13009 found; no separate GitHub org located under that exact name
     today -- likely lives in the same repo under a different tag, unresolved, next pass): "an
     open-source real-time and streaming interactive world model," the most recently-papered of the
     three substitutes.
None of the three has been run yet (SOURCE_ONLY / WEIGHTS_LOCATED, not RUNS); none is fossilized
yet (deferred to a later batch, per the scope note below).

## D. FIFTH ENGINE

**Does a technically testable open approximation exist TODAY?** Partially, and unevenly across the
three legs. The AGENT leg (Voyager) is the strongest: fully open, MIT, source-level understood, and
its curriculum+skill+critic architecture is COMPLETELY environment-independent in design even though
today's implementation is Minecraft-bound. The WORLD leg (an open Genie-shaped generator) exists as
code+weights (open-oasis, MineWorld) but none has been measured for persistence horizon, determinism,
or action richness against the fossil-packet-grade bar Techne would need before trusting it as an
experimental substrate -- that measurement is the next concrete step, not yet done. The SELF-
IMPROVEMENT leg (SIMA 2's Gemini-as-task-setter-and-reward-model loop) has NO open equivalent found
in this pass: it is closed, and no faithful open reproduction exists (kyegomez/SIMA is a toy). The
loop's SHAPE, however -- a foundation model proposing tasks and grading attempts against its own
judgement, with successes banked as retraining data -- is not exotic; it resembles OMNI-EPIC and
several 2026 agent-evolution frameworks named in section V/IX of the full directive, none of which
have been autopsied yet (next pass). So: the LOOP as an abstract pattern is buildable from open parts
today; the SPECIFIC three systems named are not simultaneously reproducible, because one leg (Genie-
class world generation at DeepMind's fidelity) and one leg (SIMA 2's specific self-improvement
implementation) are both closed.

**Minimum components required, mapped to what exists:**
  - a world/environment GENERATOR that accepts (prompt/seed, history, actions) and returns
    persistent interactive dynamics -- open-oasis or MineWorld, UNMEASURED against this bar.
  - a GENERALIST CONTROLLER that observes and acts across worlds without per-world retraining from
    scratch -- NOT found open; SIMA 2 is the only system claiming this and it is closed. This is the
    single hardest gap.
  - a TASK/REWARD GENERATOR that proposes achievable goals and grades attempts from current state --
    architecturally this is just "an LLM given the current observation, asked for a task and later
    asked to grade the outcome," which is Voyager's CurriculumAgent + CriticAgent PATTERN, already
    fully understood and already environment-independent by design (section A above). This leg is
    ALREADY BUILDABLE from Voyager's organs alone, no new invention.
  - PERSISTENT SKILL STORAGE + RETRIEVAL + COMPOSITION -- Voyager's SkillManager, already
    substrate-independent by schema (section A). ALREADY BUILDABLE.
  - a way for acquired skills to CHANGE WHICH TASKS BECOME PROPOSABLE NEXT (the loop's closing arrow)
    -- this is Voyager's `completed_tasks`/`failed_tasks` feeding back into `propose_next_task`'s
    prompt, already implemented, already substrate-independent.

**What already exists in Prometheus (from the earlier ASAL/POET/Avida work, not re-derived here):**
the fossil-packet HANDOFF schema and the rollout CAPSULE (2026-09-18/19) are structurally the same
object as a Voyager skill (id + description + executable demonstration + provenance); the
distinction between "declared" and "open" discovery channels (operator directive 6 s2, given to Nyx)
is structurally the same distinction as Voyager's hardcoded-escape-hatch vs LLM-proposed curriculum;
Harmonia's independent-ruler doctrine is a STRICTER version of Voyager's CriticAgent pattern. None of
this was built with Voyager in mind; the convergence is worth reporting to Archaeon/Nyx/Harmonia as
evidence the shape is right, not as proof the fifth engine should be built.

**What genuinely requires new engineering:** (1) measuring an open world generator against the
persistence/determinism/action-richness bar a real experiment would need -- not done, cheap, next
pass; (2) a generalist controller with SIMA 2's cross-world claim -- no open equivalent exists; this
is either a genuine invention gap or a reason to test the loop with a NARROWER, single-world
controller first (directly contradicts nothing in the directive: "the important LOOP rather than the
visual spectacle" explicitly permits this); (3) wiring the task-setter/reward-model/experience-bank
retraining cycle (SIMA 2's mechanism) onto an open controller -- no prior art found that does this
end-to-end in the open; this is the one piece with no donor at all.

**What would falsify "this deserves to be a separate fifth engine" (not answered, only staged):**
this needs the rest of sections II-IX (QD/AURORA for the behavioural-descriptor question, OMNI-EPIC
for the task-generation-at-scale question, GEA for the cross-agent-experience-sharing question) before
it can be answered honestly; flagging rather than guessing.

## Scope call, stated plainly

This First Return took a full pass and covers exactly section XV. The remaining sections (II
open-ended-environment design, III QD, IV digital life, V evolving programs/agents, VI persistent
competence beyond Voyager, VII automated science, VIII model-merge evolution, IX the mandatory
unnamed-systems search, plus X-XIV's extraction/fossilization/atlas/report formats) are, at this
depth, realistically 6-10 further passes of comparable size, not one. Continuing all of them in this
single turn would mean shallow, memory-sourced summaries for most of them, which directive rule 1
("primary sources first") and the operator's own stated preference (source-level autopsy, not "40
interesting papers") forbid. Recommendation: continue the raid across subsequent passes, in the
order the directive already implies (II auto-curricula and III QD next, since Archaeon/Harmonia most
directly overlap them; IV-IX after). Proceeding on that basis unless redirected.
