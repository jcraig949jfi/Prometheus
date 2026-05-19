# DR-prompt discipline — doctrine for swarm-member Pythia enqueueing

**Filed:** 2026-05-19
**Owner:** Aporia (canonical), operationalized across Charon + Harmonia swarms
**Trigger:** Gemini compute-based usage (2026-05-18 platform update) gives Pythia ~30× headroom over current throughput. Bottleneck shifted from production to consumption. The 10 new swarm members are the natural consumers — but only Argos is currently wired. This doc is the canonical pattern for the other 9 to adopt.

---

## 1. The capability

**Pythia** is Aporia's Gemini Deep Research dispatcher on M1. It:
- Polls `agora.research_queue` (Postgres, schema in `scripts/agora_persist.py`)
- Maintains up to 3 in-flight Gemini interactions concurrently
- Persists each completed report under `aporia/docs/deep_research_reports/<YYYY-MM-DD>/<row_id>_<slug>.md`
- Auto-commits + auto-pushes so the GitHub URL is mobile-clickable
- Emits `deep_research_dispatched` + `deep_research_received` events to `agora.intelligence_outputs` for the brief
- Tracks compute consumption in its heartbeat (`compute_tracking.count_5h_window`, `count_weekly`)

**Any agent in the mesh can enqueue Pythia.** No special permissions needed. The base class `_base.py` (already inherited by every Harmonia + Charon swarm member) exposes `pythia_enqueue_dr(title, prompt, priority, tier)`. Argos was the first to use it; this doc documents the pattern for everyone else.

---

## 2. The Argos canonical template (proven 2026-05-19)

### 2a. Cap-aware enqueue logic

From `harmonia/agents/argos/daemon.py`:

```python
# Self-imposed daily cap so a single agent doesn't saturate Pythia's
# shared budget. Cap stored in agent's state dir; default 3/day.
dr_seeded_state: list = self.load_state("dr_seeded", default=[]) or []
today = datetime.now(timezone.utc).date().isoformat()
seeded_today = sum(
    1 for e in dr_seeded_state
    if str(e.get("ts", ""))[:10] == today
)
dr_cap = int(self.load_state("dr_daily_cap", default=3) or 3)
dr_quota_remaining = max(0, dr_cap - seeded_today)
stats["dr_seeded_today"] = seeded_today
stats["dr_quota_remaining"] = dr_quota_remaining

if (not dry_run) and proposed and dr_quota_remaining > 0:
    dr_title = f"Argos lens fingerprint: {chosen.get('title') or pid}"
    dr_prompt = self._build_dr_prompt(chosen, proposed)
    row_id = self.pythia_enqueue_dr(
        title=dr_title[:200],
        prompt=dr_prompt,
        priority=5,
        tier="T5",
    )
    if row_id is not None:
        stats["dr_seeded"] = True
        dr_seeded_state.append({
            "problem_id": pid,
            "queue_row_id": row_id,
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        self.save_state("dr_seeded", dr_seeded_state)
```

### 2b. Structured prompt builder

```python
def _build_dr_prompt(self, problem: dict, proposed: list[str]) -> str:
    pid = problem["id"]
    title = problem.get("title") or pid
    lens_lines = "\n".join(f"- `{lens}`" for lens in proposed) or "- _(none)_"
    return (
        f"Primary-literature lens fingerprint for open problem "
        f"`{pid}` ({title}).\n\n"
        f"For each of the following candidate lenses, identify the "
        f"two strongest primary-literature attempts (or "
        f"closest-analogue applications) and summarise "
        f"(a) the measurement projected, "
        f"(b) the verdict reached, "
        f"(c) the axis of disagreement with other lenses applied to the "
        f"same problem.\n\n"
        f"Candidate lenses (Argos proposal, this tick):\n"
        f"{lens_lines}\n\n"
        f"Schema reference: `harmonia/memory/catalogs/README.md`. "
        f"Multi-perspective methodology: "
        f"`harmonia/memory/methodology_multi_perspective_attack.md`."
    )
```

### 2c. Why this is the canonical shape

Five disciplines compressed into one builder:

1. **Names the substrate target.** "Open problem `<pid>`" is the specific consumer. No vague survey prompts.
2. **Specifies per-element output structure.** Each candidate lens gets a (measurement, verdict, axis-of-disagreement) tuple — the report is forced to be structured, not narrative.
3. **References canonical schemas.** Tells Gemini "ground your answer in our existing catalog" → reduces drift toward generic LLM responses.
4. **Pre-declares verification criterion.** "Two strongest primary-literature attempts" — checkable on read.
5. **Sets the landing path implicitly.** Output goes back into the PROBLEM_LENS_CATALOG schema Argos owns. Argos's downstream extractor knows what to look for.

---

## 3. Discipline requirements for every DR prompt

A DR prompt is substrate-grade if and only if:

- **Names its requester explicitly.** `requested_by` is auto-set by the base class but the prompt body should also frame findings for that specific agent.
- **Specifies substrate type.** A (falsification) / B (attack-angles) / C (paradigm refinement) / D (step-decomposition) / E (meta-circuits). One of these. Tag in the prompt body so the report comes back shaped for ingestion.
- **Sets a verification criterion.** "Cite primary source published since YYYY-MM", "Include arXiv ID + DOI", "Distinguish X from Y" — something checkable on the returned report.
- **Pre-declares landing path.** Where will the finding go? Specific catalog file? Your own intake? Substrate registry? If you can't name where it lands, you don't have a substrate-grade question yet.
- **Avoids recent coverage.** If a topic was DR'd within the last 7 days, don't re-fire unless an anti-anchor flag specifically demands re-verification. Check `agora.research_queue` history before enqueueing.

Prompts that fail these are noise — they consume compute, generate plausible-sounding text, and accumulate in the reports directory without anyone integrating them.

---

## 4. Self-imposed caps (mesh-wide budget coordination)

- **Default cap per swarm member:** 3 DR/day
- **Override:** state file `dr_daily_cap.json` in your agent's state directory; raise via explicit operator decision
- **Tracking:** every tick emit `dr_seeded_today` and `dr_quota_remaining` in your stats
- **Skip when cap reached:** never crash, never error; just `continue`

Mesh arithmetic at default caps:
- 10 swarm members × 3/day = 30 DR/day
- Aporia residual (bespoke + ad-hoc) = ~10/day
- Total = ~40/day, well under Pythia's compute headroom (~650/5h window observed)

If a swarm member needs more than 3/day for a specific campaign, raise the cap by editing `dr_daily_cap.json` — keep the bump time-bounded.

---

## 5. Consumption — your DR inbox

When Pythia completes a report you requested, a notification lands at:

```
<your-agent-state-dir>/dr_inbox/<row_id>.json
```

Contents:

```json
{
  "row_id": 42,
  "queue_ref": "ARGOS-12",
  "title": "Argos lens fingerprint: BL-A-007",
  "report_path": "aporia/docs/deep_research_reports/2026-05-19/00042_argos_lens_fingerprint_bl_a_007.md",
  "report_github_url": "https://github.com/jcraig949jfi/Prometheus/blob/main/aporia/docs/deep_research_reports/2026-05-19/00042_argos_lens_fingerprint_bl_a_007.md",
  "summary": "First non-header paragraph of the report (~280 chars)",
  "completed_at": "2026-05-19T17:42:11Z"
}
```

Your daemon's tick should:
1. Scan `dr_inbox/` for unprocessed files
2. Read each — extract findings, route to your downstream substrate target
3. Move processed files to `dr_inbox/processed/<row_id>.json` (or delete with a log)

This decouples production from consumption — Pythia doesn't block on you reading; you don't poll Pythia.

(Inbox layer is `scripts/pythia_notify_requesters.py` on M1, runs each Pythia tick after marking complete. If your dr_inbox/ doesn't exist yet, the writer creates it.)

---

## 6. Per-swarm-role prompt examples

Suggestions matched to charter. Each operator should refine for their own swarm.

### Charon swarm (Substrate A — falsification)

- **Stygian** (v10-battery attack worker)
  *Topic:* "Survey 2025-2026 primary-literature attacks on `<specific_battery_target>`. Identify the two strongest published attempts and whether any have been retracted or contested."
  *Substrate:* A — informs which battery tests are still load-bearing.

- **Lethe** (anti-anchor miner via cold LLM probes)
  *Topic:* "Forward false-anchor hunt 2025-2026 in `<subdomain>`: identify three claims of the form 'X solved Y' that appeared in arXiv/journal preprints in the last 12 months and have been retracted, contested, or subsequently disproved."
  *Substrate:* A — direct anti-anchor candidate intake.

- **Hecate** (continuous gradient archaeology over kill ledger)
  *Topic:* "Pattern survey of recent (2024-2026) mathematical retractions in `<subdomain>` — group by failure mode (computation error, gap in proof, prior art collision, hypothesis failure)."
  *Substrate:* A — feeds gradient archaeology with patterned cases.

- **Moros** (cross-pollination automator)
  *Topic:* "Cross-pollination candidate: identify recent 2025 results in `<source domain>` whose technique might transfer to `<target domain>`. Name the technique, the source-domain claim, the target-domain open problem it would attack."
  *Substrate:* A/B/C cross-fertilization.

- **Acheron** (HARD-5 coordinate-collision detector)
  *Topic:* "Identify 2025 primary-literature cases where the same mathematical object appears under two non-isomorphic coordinate systems with conflicting reported invariants — coordinate-collision candidates."
  *Substrate:* A — collision-as-falsification signal.

### Harmonia swarm (Substrate B/C/D — angles, paradigms, decomposition)

- **Phylax** (pre-promotion gate)
  *Topic:* "Retraction-adjacency check for `<claim_id>`: identify any 2024-2026 primary literature that contests, refines, or extends the cited result. Specifically flag any retraction within 2 citation hops."
  *Substrate:* A/B — quality gate signal.

- **Sophia** (coordinate-system scout)
  *Topic:* "Canonical coordinate systems for `<problem_class>` in 2024-2026 literature. Identify 3-5 dominant frames, their proponents, their range-of-applicability, and points of disagreement."
  *Substrate:* C — paradigm-frame refinement.

- **Iris** (prose→symbol compressor)
  *Topic:* "Case studies of mathematical proof prose successfully compressed into symbolic form (Lean Mathlib, Coq Mathcomp, AFP entries) 2024-2026 — identify three exemplary compressions and the linguistic pattern they collapsed."
  *Substrate:* C/D — compression heuristic library.

- **Telos** (stalled-specimen reviver)
  *Topic:* "Conjecture-revival precedents in `<subdomain>` 2024-2026: identify cases where a stalled open problem received new attention via reframing or auxiliary-result import. For each: the reframing move, the auxiliary result, the new bound or partial."
  *Substrate:* B/D — revival-move pattern library.

- **Argos** ✓ already wired (lens fingerprinting — keep as canonical example)

---

## 7. When you don't have a clear ask

Skip the day's enqueue rather than fire a low-value prompt. Aporia maintains:
- `aporia/docs/gemini_research_queue/queue.jsonl` — 370+ tier-sorted unfired entries (general fallback)
- `scripts/pythia_seed_200.py` — 50 bespoke thesis prompts (substrate-priority)

Either runs as a residual filler. **Better to leave the budget than burn it on prompts without a named consumer + verification criterion + landing path.**

---

## 8. What to confirm after wiring

When your swarm member adopts the pattern, post a `dr_prompt_discipline_adopted` log_work event with:
- agent name
- daily cap chosen
- substrate type(s) targeted
- first prompt template's `_build_dr_prompt` reference

That confirmation flows through the brief, signaling to Aporia + Aletheia + James that consumption capacity is online for that agent.

— Aporia, 2026-05-19
