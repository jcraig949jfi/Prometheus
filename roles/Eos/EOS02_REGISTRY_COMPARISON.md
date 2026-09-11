# EOS-02: api_registry.json against prometheus_llm -- migrate or narrow

Currency: 2026-09-11. Operator's provisional ruling: do not create a second
general resource registry; compare, then propose either a migration into
the canonical registry or a narrowly scoped residue prometheus_llm
genuinely cannot represent. Duplication needs evidence.

## The comparison

agents/eos/data/api_registry.json holds 15 API rows and 4 local-model rows,
last touched 2026-04-01T07:21:55Z. prometheus_llm/registry.py holds 10
provider specs: openrouter, deepseek, groq, cerebras, nvidia, openai,
ollama, gemini, anthropic, claude_cli.

Splitting the 15 Eos rows by whether prometheus_llm's abstraction (a model
provider with a chat/completions interface) can represent them at all:

    MODEL-PROVIDER ROWS -- prometheus_llm's domain (8)
      cerebras                COVERED
      google_gemini           COVERED (as "gemini")
      groq                    COVERED
      openrouter              COVERED
      github_models           NOT covered
      huggingface_inference   NOT covered
      sambanova               NOT covered
      together_ai             NOT covered

    NON-MODEL ROWS -- prometheus_llm cannot represent these (7)
      arxiv_api               Atom XML paper search
      openalex                academic metadata
      semantic_scholar        TLDRs and citation graphs
      crossref                publication metadata
      tavily                  agent-oriented web retrieval
      serper_dev              web search, 2,500 LIFETIME budget
      google_custom_search    web search, 100/day

    LOCAL MODELS (4): qwen_coder_3b, qwen_coder_7b, deepseek_coder_6_7b,
      starcoder2_3b -- an inventory of WEIGHTS on disk, not API capacity.

## The evidence that the overlap is harmful, not merely redundant

Four rows are duplicated. The duplication is not inert: the Eos registry
still describes cerebras, groq, openrouter and gemini with April data and
NEVER NOTICED that prometheus_llm superseded it in August. A second source
of truth that cannot detect its own staleness is the defect, not the byte
count. That is calibration row C6 and it is the evidence the ruling asked
for.

A stronger fact covers all 15: NOT ONE ROW CARRIES AN OBSERVED
MEASUREMENT. Every free_tier and rate_limit value in the file was copied
from a provider's documentation. Under this seat's own constraint 5 a
RESOURCE row is not ACTIVE until a call has been made and the behaviour
recorded -- so today the registry contains 15 labels and 0 measurements.
The first season demonstrated the consequence deliberately: a RESOURCE
claim backed by a documented free tier was REFUSED by the gate, while the
one backed by this seat's own probe was accepted.

## Proposal

1. RETIRE the 4 covered model rows from api_registry.json. They are
   duplication with a demonstrated failure to stay current.
   prometheus_llm's measured behaviour wins by the seat's own charter.

2. OFFER the 4 uncovered model rows to prometheus_llm as candidate
   provider specs -- github_models, huggingface_inference, sambanova,
   together_ai. This is a one-time contribution to the canonical registry,
   not a lane Eos keeps. Whether they are worth adding is prometheus_llm's
   call, and every one of them must be measured before it is added,
   because the Eos rows are documentation claims.

3. KEEP a NARROW RESIDUE of 7 rows: the literature and web-retrieval
   sources. prometheus_llm is "one model API for the whole program"; these
   have no completions interface, no model names, no token accounting, and
   three of them (arXiv, OpenAlex, Crossref) need no credential at all.
   Representing them there would mean widening prometheus_llm into a
   general resource registry, which is the exact thing the ruling forbids.
   The residue is renamed for what it is -- SOURCES, not APIs -- so it
   cannot drift back into being a general registry.

4. RETIRE the 4 local-model rows or hand them to prometheus_llm's ollama
   provider. They are a weights inventory, and a weights inventory that
   has not been checked since April is a list of guesses about what is on
   a disk.

5. EVERY SURVIVING ROW IS MARKED UNVERIFIED until measured. Only
   arxiv_api has a measurement, taken today: 2 requests, HTTP 200, 431 ms
   and 244 ms, 12 items each, budget at or under 75 percent of the
   documented rate (roles/Eos/intake/probe_arxiv.json). serper_dev's
   lifetime budget of 2,500 stays unspent (EOS-R8, PARKED).

Net effect: 15 rows and 4 model entries become 7 rows, 1 of them measured,
6 marked UNVERIFIED, under a name that says SOURCES. No second general
registry exists at any point.

## What would falsify the "narrow residue" claim

If prometheus_llm's maintainer says the 7 source rows belong there -- that
the abstraction is "external capability" rather than "model provider" --
then the residue is not narrow and the right answer is full migration and
the deletion of api_registry.json. Eos will take that answer. The question
is asked in the comms report accompanying this pass; the proposal above is
what Eos does if no one objects, not a decision already taken.
