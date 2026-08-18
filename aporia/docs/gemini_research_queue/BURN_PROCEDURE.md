# Burn the Tokens — Daily Procedure

**Filed:** 2026-05-11
**Owner:** Aporia (queue maintenance + survey logic), James (token spending decisions)
**Companion to:** `README.md`, `prompt_templates.md`, `queue.jsonl`, `fired_log.jsonl`
**Entry point:** `python aporia/scripts/burn_research_tokens.py`

---

## What "burn the tokens" means

Project Prometheus has a paid Gemini Pro account that grants **20 Gemini Deep Research tokens per day**. The tokens are **use-or-lose**: at the daily reset they pumpkin. They cannot be banked, traded, or carried over. There is no refund for an unfired token.

The substrate-grade default position is therefore: **fire 20 every day**, even on slow days, because an unfired token is a strictly worse outcome than a queue-burn token. The 423-entry prioritized backlog in `queue.jsonl` exists exactly so that there is always somewhere productive to spend.

"Burn the tokens" is the standing instruction Claude hears at the start of a session. The user says it, and the system:

1. Surveys current substrate state (STATUS files, registry, vocabulary, recent syntheses, fired log).
2. Re-assesses the queue against the last 24-48h of substrate findings.
3. Picks today's 20 topics across the four tiers.
4. Builds a deck file via the existing deck builder.
5. Fires the dispatcher in background, 3-at-a-time parallel.
6. Logs fires to `fired_log.jsonl` and mutates `queue.jsonl`.
7. After return, runs a synthesis pass.

The orchestrator script `burn_research_tokens.py` is the canonical entry point. It does not duplicate dispatcher logic — it composes the existing tools (`build_deck_from_queue.py`, `gemini_deep_research_dispatch.py`, `extract_dispatch_text.py`) into a daily-cycle wrapper.

---

## The 8-step daily procedure

### Step 1 — Survey current state

Before picking topics, read the following files in order and note any items urgent enough to bump from queue order. The script prints these counts automatically; the human-review path mirrors them.

**Mandatory reads:**

- `F:\Prometheus\ergon\STATUS.md` — Ergon's live status. If a `*_gap_scan.py` is gated on a Tier-F anchor pin, that pin is top-of-queue today.
- `F:\Prometheus\techne\CHANGELOG.md` — Techne's recent activity. Tier-A++/B/C/D/E/F/G primitive registrations in the last 48h indicate primitive-supporting-lit Tier-1 entries are urgent.
- `F:\Prometheus\techne\registry\anti_anchors.jsonl` — current anti-anchor count, last-verified dates. Any AA-NNN whose `last_verified` exceeds 90 days should pop to top-of-queue (already in the queue as `subdomain: "anti-anchor-revisit"`).
- `F:\Prometheus\techne\registry\compositions.jsonl` — current composition registrations. Pending compositions waiting on a primitive registration may have a queue entry blocking.
- `F:\Prometheus\aporia\doctrine\substrate_vocabulary\version.json` — vocabulary version. If `open_window: true`, vocabulary expansion Tier-4 entries are urgent. If pending patch is noted in `notes`, prioritize.
- Most recent `aporia/docs/*_synthesis_*.md` by mtime. This is the dominant signal: synthesis surfaces new anti-anchor candidates and `[VERIFY-LIVE]` catalog edits that should jump tier-1 priority. Synthesis from the last 24h has highest weight.
- `aporia/docs/gemini_research_queue/fired_log.jsonl` — skip already-fired entries. This is enforced by `queue.jsonl` mutation, but the log is the receipts trail.

**Optional reads (when survey suggests):**

- `F:\Prometheus\aporia\mathematics\tensor_open_problems_v1.md` — if a catalog row was edited in the last 24h with `[VERIFY-LIVE]`, that row is a fire-this-batch candidate.
- `F:\Prometheus\techne\WORK_QUEUE_*.md` — open Techne work that depends on Aporia literature inputs.
- `F:\Prometheus\learner\v1_0_plans\` — Learner v1.0 corpus design intake. Methodology Tier-4 entries that inform corpus filtering are urgent if v1.0 design is active.

The script's survey phase prints a state report to stdout, then the proposed pick, then asks for confirmation (or runs straight through if `--no-confirm` is passed). The human reader should glance at the report and decide whether mix-tuning is needed (see §"Mix-tuning rules" below).

### Step 2 — Re-assess the queue

Has anything in the queue become higher-priority because of recent substrate findings? Three concrete checks:

- **Synthesis-driven priority bump.** If `gemini_research_synthesis_<recent-date>.md` flagged new anti-anchor candidates AA-NNN, those candidates' queue entries should fire today (they are tagged in `queue.jsonl` with `source: "synthesis_<date> ..."`). Confirm they are still at the head of Tier 1.
- **Stale entry detection.** Read each prospective entry's `source`. If the source is older than 30 days and references a synthesis that has been superseded, the entry may need re-justification or removal. This is a manual judgement; the script flags entries older than 30 days but does not auto-drop them.
- **Downstream-consumer livelock.** Read each prospective entry's `downstream_consumer` field. If the named consumer (e.g., `T#NN`, `AA-NNN`, primitive name) has already been satisfied by a different fire, the entry is redundant and should be skipped.

The script does the first check mechanically; the latter two are human-eyeball overrides applied via `--skip ID,ID,ID`.

### Step 3 — Pick today's 20 topics

Default mix:

| Tier | Default count | Rationale |
|---|---|---|
| 1 | 8 | Anti-anchor verification is highest-leverage per `feedback_verify_upstream_attributions.md`; capped at 8 to leave room for breadth. |
| 2 | 7 | Tensor catalog continuation; the backbone of Aporia's catalog maintenance. |
| 3 | 3 | Calibration-anchor mining for Ergon; steady cadence sufficient. |
| 4 | 2 | Methodology / vocabulary; usually one is enough but two prevents starvation. |

Within each tier, the script picks by `id` ascending (matches the `README.md` selection rule). This is the **standard mix.** Override via `--mix "10,5,3,2"` to tune.

### Step 4 — Build the deck

Generate `aporia/docs/gemini_deep_research_deck_<date>.md` via `build_deck_from_queue.py`. The orchestrator imports the deck builder's `build_prompt` function and produces a single deck file containing all 20 prompts numbered `### Prompt 1` through `### Prompt 20`, each with the inline framing string prepended and the tier-appropriate template body.

The deck file is the artifact passed to the dispatcher. It is committed to git after the burn completes (alongside the fired_log update).

### Step 5 — Fire the dispatcher

Launch `gemini_deep_research_dispatch.py` as a `subprocess.Popen` background process. Capture:

- The PID.
- The dispatcher's log path (stdout/stderr redirected to `aporia/docs/deep_research_batch_<date>/_dispatch.log`).
- The output directory path (`aporia/docs/deep_research_batch_<date>/`).

Print this triple so the user can poll later. The orchestrator script returns immediately after launching — it does **not** wait for the dispatcher to finish. The dispatcher itself handles batch parallelism (3 at a time) and writes `_dispatch_summary.jsonl` as fires complete.

Typical wall time at 20 prompts, batch-size 3: **90-180 minutes**. Longest single query observed to date: 13 minutes (Wave 5 prompt 13, 2026-05-10 batch).

### Step 6 — Log to fired_log.jsonl (POST-fire)

The orchestrator runs a second pass — `--log-only --batch-dir <path>` — that reads the dispatcher's `_dispatch_summary.jsonl`, extracts each successful fire, and appends one entry per fire to `fired_log.jsonl`:

```json
{"id": "DR-001", "fired_date": "2026-05-11", "output_path": "aporia/docs/deep_research_batch_2026-05-11/01_<slug>.md", "batch_id": "burn_2026-05-11", "status": "completed", "interaction_id": "<id>", "elapsed_s": <sec>}
```

This pass is idempotent — re-running it after a partial completion appends only entries not already logged.

### Step 7 — Update queue.jsonl (POST-fire)

Same orchestrator pass mutates `queue.jsonl` in place: for each fired entry, set `fired: true`, `fired_date: <today>`, `output_path: <path>`. The file is rewritten atomically (write to `queue.jsonl.tmp`, then rename).

The mutation is git-tracked. A periodic commit (typically at end-of-day) captures the running state. See `feedback_two_machine_sync.md` for the cross-machine sync rule — pull-before-burn is mandatory if a co-researcher's machine has touched the queue today.

### Step 8 — After return: synthesize

Once the dispatcher reports all 20 fires complete (`_dispatch_summary.jsonl` has 20 `completed` rows), run:

```bash
# Post-process any JSON-wrapped reports (rare, but happens)
python aporia/scripts/extract_dispatch_text.py --dir aporia/docs/deep_research_batch_<date>

# Hand-write the synthesis pass (no automation for this yet)
# Output: aporia/docs/gemini_research_synthesis_<date>.md
```

The synthesis is a manual Aporia task — read the 20 reports, surface anti-anchor candidates, `[VERIFY-LIVE]` catalog edits, primitive proposals, paradigm-class candidates. Drives tomorrow's mix-tuning. Synthesis cadence: after every 20-fire burn, or after ~9-18 fires accumulate if running sub-20-fire days.

---

## Mix-tuning rules

The default `8 / 7 / 3 / 2` mix is the baseline. Override when:

- **Synthesis surfaced more than 5 new anti-anchor candidates in the last 24-48h.** Boost Tier 1 to 12+. Pull from Tier 2 to backfill. Example mix: `12 / 5 / 2 / 1`. The reason: anti-anchor verifications are the highest-leverage class per `feedback_verify_upstream_attributions.md`; new candidates degrade in attribution-recovery quality the longer they sit unverified.
- **A substrate vocabulary v0.X.0 patch is pending** (`version.json` `open_window: true` or `notes` references a queued amendment). Boost Tier 4 to 5+. Example mix: `6 / 6 / 3 / 5`. Vocabulary expansion entries are the load-bearing intake for the patch.
- **A `[VERIFY-LIVE]` catalog edit is gating a Techne Wave.** Prioritize the specific T#NN entries first; the orchestrator's `--prioritize ID1,ID2,ID3` flag forces those to fire regardless of tier ordering. Example: gating verification on `T#84` (TensorNetwork) before the Tier-A++ Wave 1 substrate-tester probe can land.
- **An anti-anchor in `anti_anchors.jsonl` is at day-89 of its 90-120 day re-verification cadence.** Boost Tier 1 by inserting that AA's re-verify entry from the `anti-anchor-revisit` subdomain at top-of-queue.
- **Quiet day (no new synthesis, no pending vocabulary patch, no Techne gate)** — use default mix. Pure queue-burn.

The mix is a knob, not a hard rule. The 20-token budget is fixed; how it splits across tiers is the daily judgement call.

---

## Urgent-injection protocol

Occasionally an external trigger surfaces a topic that should supersede the queue entirely — e.g., a substrate finding 2 hours old that demands literature verification before tomorrow, or a James-flagged Twitter claim about a 2025 result that needs anti-anchor scrutiny by end-of-day.

Procedure:

1. **Confirm urgency.** Is this fire-today-or-pumpkin urgent, or can it wait for tomorrow's queue re-assessment? If it can wait, write the new candidate into `queue.jsonl` at Tier 1 head with `source: "urgent-injection <date> <reason>"` and let it fire tomorrow on standard burn.
2. **If genuinely urgent:** create a one-off ad-hoc deck (not from the queue). The orchestrator supports this via `--ad-hoc-deck <path>` — supply your hand-written deck and skip the queue-pick phase. The deck's prompts still get logged to `fired_log.jsonl` with synthetic IDs (`ADHOC-<date>-<NN>`).
3. **Update queue afterward** — promote the urgent topic to a proper queue entry post-fire, so future synthesis cycles see the source.

Hard rule: **ad-hoc fires count against the 20-token budget.** A 5-prompt urgent injection leaves only 15 for queue-burn that day. The orchestrator enforces this.

Frequency expectation: ad-hoc injection should be **rare** (single-digit per month). If you find yourself injecting daily, the queue maintenance is failing — re-rank Tier 1 to capture the urgent class.

---

## Synthesis cadence

After each 20-fire burn:

1. Wait for all 20 to complete (the dispatcher's `_dispatch_summary.jsonl` will have 20 `completed` or `timeout`/`failed` rows).
2. Post-process JSON-wrapped reports (if any) via `extract_dispatch_text.py --dir aporia/docs/deep_research_batch_<date>`.
3. Hand-write `aporia/docs/gemini_research_synthesis_<date>.md`. Follow the section structure of `gemini_research_synthesis_2026-05-11.md` (executive summary → catalog `[VERIFY-LIVE]` updates → new anti-anchor candidates → primitive proposals → paradigm-class candidates → next-batch priority list).
4. Surface the next-batch priority list as the input to **tomorrow's** mix-tuning.

Synthesis is **not optional**. Unsynthesized reports are dead weight — they consumed a token but did not feed back into the substrate. A 20-fire batch without synthesis is a 20-token waste.

Synthesis word target: 4000-8000 words for a full 20-fire batch. Less for sub-20 days.

---

## Slow days / vacation mode

When no urgent work and no recent synthesis to chew on:

- **Default mix.** `8 / 7 / 3 / 2`.
- **No urgent-injection.** Pure queue-burn.
- **Synthesis still mandatory.** Even slow-day burns produce reports that need synthesis. Slow-day synthesis can be shorter (2000-4000 words) but it must surface what was learned for tomorrow.

If James is genuinely AFK for a multi-day stretch, the burn should continue on auto-pilot — that's the entire point of the queue. The procedure assumes someone (Claude under "burn the tokens" instruction, or scheduled via `/loop` if eventually wired up) is the daily executor.

---

## Failure modes

**Long-running queries.** Wave 5 prompt 13 took 13 minutes on the 2026-05-10 batch. The dispatcher's `POLL_TIMEOUT_SEC = 3600` (1 hour) ceiling absorbs this. If a query exceeds 30 minutes, log it but do not kill — the report when it returns is usually substantive.

**API errors.** `client.interactions.create()` can fail with rate-limit or transient errors. The dispatcher catches the exception and records `status: error, stage: create`. The orchestrator's log phase will see this as an unsuccessful fire and **not** mark the queue entry as fired. The entry remains unfired and pops back to the head of its tier next day.

**Dispatcher hangs.** If the dispatcher hasn't written to `_dispatch_summary.jsonl` in 30+ minutes after expected wall time (180 min for 20 prompts), the run is stuck. Kill the process (`taskkill /PID <pid>` on Windows, `kill <pid>` on Unix) and restart with:

```bash
python aporia/scripts/gemini_deep_research_dispatch.py \
    --deck <same-deck> \
    --out <same-out-dir> \
    --batch-size 3 \
    --resume
```

`--resume` skips prompts whose output already exists at >500 bytes, so the restart only re-fires the stuck/failed prompts.

If a specific subset is stuck, use `--only N,M,K` to re-fire only those numbers.

**JSON-wrapped report.** Older dispatcher runs saved the full Interaction `model_dump` instead of extracting `outputs[].text`. The current dispatcher fixed this, but if a report comes back wrapped (recognizable by the body starting with `{` after the header), run `extract_dispatch_text.py --dir <batch-dir>` to rewrite in place.

**Queue drift across machines.** If you burn on M1 while M2's working copy has stale queue.jsonl, the M2 commit can clobber the fired flags. Pull-before-burn is mandatory; per `feedback_two_machine_sync.md`. The orchestrator does not enforce this — it is a human discipline.

**Token quota already spent.** If James fired manually earlier and burnt some quota, the remaining is less than 20. Pass `--count <remaining>` to fire only that many. Tokens used outside the burn flow are not tracked in `fired_log.jsonl` — track manually in the day's notes.

---

## Token economics

- **Quota:** 20 Deep Research tokens/day on paid Gemini Pro (`jcraig949@gmail.com`).
- **Reset:** daily UTC midnight (TBD — verify against Gemini Pro docs; treat as midnight UTC by default).
- **Cost per token:** flat subscription, no marginal cost per query. Unfired tokens have no refund value.
- **Pumpkin policy:** at reset, unfired tokens vanish. There is no carryover.

Implication: **the marginal cost of firing today's 20th token is zero**, and the marginal cost of firing the 21st is infinite (it doesn't exist). So **always fire 20**. The only reason to fire fewer is if the queue is exhausted (unfired count < 20) — which at 423 entries with steady-cadence burn won't happen for ~3 weeks of daily burning at average 20/day.

If quota expands (Gemini Pro tier bump), update the orchestrator's `--count` default and revisit the mix.

---

## File manifest (this directory)

| File | Purpose |
|---|---|
| `README.md` | Queue purpose, fire protocol, tier structure, quality bar |
| `BURN_PROCEDURE.md` | THIS FILE — daily burn procedure, mix-tuning, failure modes |
| `prompt_templates.md` | 4 tier templates + inline framing string |
| `queue.jsonl` | 423 entries; mutated in-place as fires complete |
| `fired_log.jsonl` | Append-only fire log |

---

## Quick reference: one-line invocation

Standard daily burn (default mix 8/7/3/2):

```bash
python aporia/scripts/burn_research_tokens.py
```

Dry-run (survey + plan, no fire):

```bash
python aporia/scripts/burn_research_tokens.py --dry-run
```

Custom mix:

```bash
python aporia/scripts/burn_research_tokens.py --mix "12,5,2,1"
```

Log-only pass after a manual dispatcher run:

```bash
python aporia/scripts/burn_research_tokens.py --log-only --batch-dir aporia/docs/deep_research_batch_2026-05-11
```

---

End of procedure.
