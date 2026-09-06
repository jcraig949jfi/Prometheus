# CAPABILITY: Gemini Deep Research (shared, owned by Aporia)

**Status as of 2026-09-04: VERIFIED EXECUTABLE FROM THIS SEAT.**
Verified end to end by Herakles on 2026-09-04. Do not re-derive this; read
this file and go.

This file exists because the Herakles seat spent a full exploration pass
rediscovering a capability that was already documented in another seat's
responsibilities file. That cost is not to be paid twice.

---

## 1. What it is

Aporia owns the daily Gemini Deep Research dispatch. It is a real API
capability, not a human pasting from a web interface. Authority for the
capability, the doctrine around it and the daily budget is
`roles/Aporia/RESPONSIBILITIES.md`, section "Deep Research Dispatch (Gemini)".
Where this file disagrees with that one, that one wins.

Budget is roughly 20 reports per day on a use-or-lose basis. Tokens do not
roll over. See `feedback_use_or_lose_research_tokens` in memory.

---

## 2. The five components, and how to check each one

Run these checks before claiming the capability works. All five passed on
2026-09-04.

1. **Dispatcher.** `aporia/scripts/gemini_deep_research_dispatch.py`.
   Parses a deck, fires each prompt as a background interaction, polls every
   30 s, writes one report per prompt plus `_dispatch_summary.jsonl`.
2. **Client library.** `google-genai`, imported as `from google import genai`.
   Was version 2.8.0. It must expose `client.interactions`, which is marked
   experimental and emits a UserWarning. `google.generativeai` is a different,
   older package and is NOT installed.
3. **Credential.** Resolved through the repo-root helper, `from keys import
   get_key`, called as `get_key("GEMINI")`. NEVER print, echo, log, commit or
   quote the value. Check it only as a boolean and a length.
4. **Auth liveness.** `client.models.list()` must succeed. This is free and is
   the correct first check.
5. **Agent availability.** The deep research agent must appear in that model
   list. On 2026-09-04 three were live: the December 2025 pro preview that
   Aporia's doctrine and prompt format were tuned against, plus two April 2026
   variants (a plain and a max). Use Aporia's documented agent unless there is
   a reason not to, and say which one you used.

Preflight, safe to run any time, prints no secret:

    python -c "import sys,warnings; warnings.filterwarnings('ignore'); \
    sys.path.insert(0,'.'); from keys import get_key; from google import genai; \
    k=get_key('GEMINI'); print('key resolves:', bool(k)); \
    c=genai.Client(api_key=k); \
    print([m.name for m in c.models.list() if 'deep-research' in m.name])"

---

## 3. Deck format (this is a hard contract)

The dispatcher's parser is literal. A deck that does not match this shape
produces zero prompts and the dispatcher exits saying "Nothing to fire."

- Each prompt begins with a heading exactly of the form
  `### Prompt N: <title>` at the start of a line.
- The prompt body is the FIRST fenced block after that heading.
- The body therefore must NOT itself contain a triple backtick. Write any
  code, grammar or command inside a prompt as indented plain text.
- A body starting with `[TBD` or `[Pick based on` is skipped as a placeholder.
- The output filename is derived from the title, so titles should be short
  and distinctive.

Invocation:

    python aporia/scripts/gemini_deep_research_dispatch.py \
        --deck <deck>.md --out <outdir> --batch-size 3 --resume

Flags: `--probe` fires only prompt 01 as a smoke test. `--only N,M` fires a
subset. `--resume` skips prompts whose output already exists above 500 bytes.
Latency is 4 to 13 minutes per prompt, occasionally longer. Three concurrent
is the documented ceiling on the paid tier. Always run it backgrounded; never
babysit the terminal.

---

## 4. Rules this seat must follow

- **Secrets.** No credential, key, token, account identifier or email address
  is ever printed, committed, or included in a report, packet or chat message.
  Redact any grep over the dispatcher or `keys.py` before displaying it.
- **The budget is not mine.** It is Aporia's daily allocation. Firing a large
  batch from this seat spends her tokens. One-off queries authorised by James
  are fine. A standing batch is not, without her seat or James saying so.
- **Log what I fire.** Every dispatch from this seat gets its deck, its
  outputs and its summary committed, so the spend is auditable and the report
  has provenance. A deep research report with no recorded deck is an
  unsourced claim.
- **Reports are Tier-2 anchors, not primary sources.** Same rule as any
  internal catalog. See `feedback_verify_upstream_attributions`. A returned
  report's citations must be checked against primary literature before any
  claim built on them is load-bearing. This matters especially for the
  Historical Collider, where the entire method is primary-source recovery.
- **Doctrine on prompt content.** Aporia's file carries binding constraints on
  what her decks may contain, including no paper or publication framing. If I
  fire against her queue or her agent, those constraints apply to me too. See
  `feedback_exploration_not_papers`.

---

## 5. Structured output: the square-bracket trap

**Deep Research cannot return JSON containing square brackets.** Learned the
hard way on 2026-09-06, across two full runs, at a cost of 17 of that day's 20
reports.

The grounding layer rewrites the report after the model writes it, replacing
bracketed spans with source markers of the form `[cite: 11, 13, 14]`. It cannot
tell a citation bracket from a JSON array, so **every array of numbers is
overwritten and its contents are lost**. A choice list of three integers comes
back as a source marker. Sometimes the value is deleted outright, leaving a key
with an empty slot. In the first run 14 of 15 template blocks were unparseable;
in the second, 67 of 69, after a prompt that explicitly forbade the behaviour.

**Instructing the model not to do it does not work**, because the substitution
happens after generation. This is a property of the tool, not of the prompt.

**The fix is to remove brackets from the format.** Ask for ranges and choice
lists as quoted strings and decode them on arrival:

    "length":    {"choices": "16, 24, 32"}
    "seed_root": {"int_range": "100000 to 999999"}

**If you already have corrupted output**, it is partly salvageable. Replacing a
source marker in a JSON value position with `null`, deleting markers inside
strings, and filling emptied slots with `null` recovered all 69 structures. What
never comes back is the numbers. Do not infer them: the value is gone, and a
plausible-looking number invented downstream is worse than an explicit gap.
`roles/Herakles/deep_research/2026-09-06_archaeon_template_mining/ingest.py`
implements that repair and flags every template it touched.

---

## 5. Known gaps and cautions

- The queue's `fired_log.jsonl` stops at 2026-05-14. Roughly four months of
  daily allocations have gone unspent. That is a standing waste, and it is
  Aporia's call, not mine, but it is worth surfacing when she returns.
- The December 2025 agent is a preview. Preview names get retired. If a
  dispatch fails at `create()`, check the model list before assuming the
  credential broke.
- **FIXED 2026-09-04.** The dispatcher's `extract_text_from_interaction` knew
  only the older `outputs` shape. SDK 2.8.0 returns the report inside `steps`,
  in the step of type `model_output`. The extractor found nothing, fell through
  to its last resort, and wrote a raw JSON dump to the report file. That file
  still looks like a report and still has a plausible size, so the failure is
  silent. Herakles added `steps` handling and verified it against the returned
  interaction: 52,563 characters of report where the dump had been. Any report
  in the tree from before this date should be checked for a JSON body.

- `client.interactions` is experimental in the SDK. An SDK upgrade could move
  or rename it. The dispatcher would fail at import or at `create()`, not
  silently.

---

## 6. Provenance of this file

Written by Herakles on 2026-09-04, after James asked whether the capability
could be found and executed from this seat while Aporia was unavailable. The
verification chain was: dispatcher located, SDK version confirmed, credential
resolved as a boolean only, `models.list()` succeeded, the deep research agent
confirmed present, and finally a throwaway one-line interaction created,
polled to `in_progress`, and cancelled. Only that last step proves the whole
path rather than just authentication.
