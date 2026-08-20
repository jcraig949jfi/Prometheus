# Kickoff Prompts — Three Free-Tier Wins (James, 2026-08-19)

**Why this round.** The paid lane exhausted at −$0.70 after ~3,300 calls, and the money went on
*iterations* (two decision runs, a bisection sweep, the R3 battery, the pilot, a supplement that
died on a dead lane) rather than on the decisive run — Tier B itself is ~2,800 calls ≈ $9 at
measured burn. **New discipline: iterate on free, reserve paid for the single decisive run.**
James: *"we need some wins at the free tier before pushing $$$."*

All three below cost **$0** — two are fully local/deterministic (no API at all), the third is
retrodictive over existing data. Each closes something that has been open for months.

**Run order:** Win 3 (smallest, tests the forge's own claim) → Win 1 (M2, in parallel; the
metabolic cycle) → Win 2 (whenever Aporia's seat is free). The probe's free-lane re-level runs
as a background thread and is described at the end.

---

## WIN 3 — HEPHAESTUS (M3): grade the composed engine on the oracle

*Smallest, fully local, and it is the forge's own headline claim on the line. Assigned to
Hephaestus because it is the forge's debt; the oracle grades server-side and the candidate
cannot grade itself, so the conflict is structurally contained.*

---

You're Hephaestus @roles/Hephaestus on M3 — `git pull origin main` first. Read
`roles/Hephaestus/ROLE.md` §6, `agents/hephaestus/STATUS.md` §5 (James's exploit-first
directive, item 5), and `harmonia/services/grading_oracle.py`.

**The debt.** The +11pp R3 / +32pp R4 failure-mined engines are the seed of every organism plan
since June and are **still E0** — never independently measured, quoted only as "forge-internal
ruler." The grading oracle is deterministic (procedural probes + independent verifier, no API,
zero cost), the composed engine is local Python (`agents/hephaestus/src/composer.py`), and
`grade_reasoner` takes a callable or a `module:attr` reference. This has been one import away
since 2026-06-27 and is named as priority #5 in your own STATUS.

**Do it:**
1. Wire the composed engine as a reasoner reference and run `grade_reasoner` on it. Commit the
   staircase.
2. **Install z3 first** (`pip install z3-solver`) or the oracle's verifier leg silently degrades
   to 0/0 — that silent degrade is a known defect; if you cannot install, make the degrade
   **loud** and record that the run was single-leg.
3. Compare the oracle's per-tier result against the trap battery's own R-numbers. **They are
   different rulers** — the trap battery's CATEGORY_TIER is the 05-15 vocabulary, the oracle
   uses the testable ladder. Do not translate; report both and state the mapping is unresolved
   (this is D7 of the meta-assessment, and Aporia's Canon v2.0 now bears on it —
   `roles/Hephaestus/TICKET_category_tier_remap_2026-08-17.md` is addressed to you and can be
   read, but the remap is not this session's work).
4. **State plainly what the oracle says about +11/+32pp.** If the climb reproduces on an
   independent non-gameable instrument, the forge's one survived claim gets its first E3. If it
   does not, say so — that is the more valuable result and it is your own claim being killed.

Constraints: no agent-source edits beyond wiring (my authority covers writing tools, not editing
agents — if the wiring requires touching `composer.py`, ask James rather than assume). Commit,
push, update `stations/M3_STATUS.md`.

---

## WIN 1 — APOLLO (M2): the type-bridge cycle — the first completed metabolic cycle

*Deterministic substrate, no API, no money. This is heredity stage 2 under James's
constitutional rule: **no new architecture until one failure produces one verified improvement.***

---

You're Apollo @roles/Apollo on M2 — `git pull origin main` first. Read
`apollo/pivot/r2_run1_findings_2026-06-10.md` (the 481-generation flat run),
`apollo/pivot/recombination_ab_result_2026-06-16.json` (crossover finds cross-tier, 4 vs 0),
and `pivot/PROMETHEUS_DOSSIER_2026-08-12_where_we_go_from_here.md` §4 point 3 (the heredity
rule and this cycle named as a first-cycle candidate).

**The cycle, end to end, and it is fully specified already:**

- **The failure (T₀, recorded):** with the R2 op seeded, 481 generations produced `best_acc`
  flat at 0.42 and **zero cross-tier organisms**. Diagnosis: a **type-bridge gap** — no op reads
  `derived_facts` and writes `relations`/`counts`, so the organism was never in the search space.
  Mutation alone cannot bridge tiers; crossover can (4 de-novo cross-tier solvers vs 0, and 61
  de-novo events in the M2 evolve logs).
- **The intervention:** the bridging op. Hephaestus owes it under the gate that opened
  2026-06-09 (comp_lift 0.6–1.0, `forward_chain` load-bearing, `keystone_question_yes=true`) and
  is supplier-only — **request it, specify the type signature you need, and grade it yourself.**
  `apollo/src/hephaestus_ops.py` was repaired 2026-08-12 and now imports for the first time (9
  ops, honest `causal_trace: R1`), so the adapter path is live.
- **The measurement (T₁):** rerun the canary with crossover enabled, deterministic mode only
  (`--mode llm` fired its own kill condition — 2,152 mutations, zero lift — do not revive it).
  Report whether cross-tier organisms now appear and whether `comp_lift` / `n_load_bearing`
  move, against the same pre-registered gauntlet.
- **Reproduce it, then archive the lineage:** {failure signature at T₀ → diagnosis → intervention
  → measured delta at T₁ → reproduction}. **The lineage record is the deliverable**, not the
  accuracy number — an improvement that cannot be replayed is not inheritance.

**Preregister before running:** what counts as success (e.g. ≥1 cross-tier organism that is
load-bearing under the existing data-flow test, with `comp_lift` above the gauntlet's threshold),
and what counts as failure — including the honest one: *the bridging op is present, crossover is
on, and the organism still does not appear*, which would falsify the type-bridge diagnosis
itself and is a real result.

**Also settle, in an afternoon, the classification call Harmonia C flagged:** is the 2026-06-16
recombination result a `search_operator` or *part of* evolutionary search? Five kills in
`evolutionary_search` cross the exhaustion threshold under one reading and reset the count under
the other — it decides redirect-vs-continue for your whole lane and only you can make it.

Constraints: no new architecture (the heredity rule applies to you too — this is a *cycle*, not
a redesign). No paid API. Commit and push; update `stations/M2_STATUS.md`.

---

## WIN 2 — APORIA (M1): the two retrodictions

*Existing data, zero API, and they adjudicate what a year of nulls meant. Aporia's own top
research ask from `aporia/docs/META_SYNTHESIS_2026-08-12_v1.md` §5, never run.*

---

You're Aporia @roles/Aporia on M1 — `git pull origin main` first. Read your own
`aporia/docs/META_SYNTHESIS_2026-08-12_v1.md` §5 (the kill-resurrection retrodiction and the
detector-band audit, with the v4 correction re-keying them on **representability** rather than
`entails`-closure after Harmonia D's kill), and `roles/Harmonia/SYNTHESIS_20260812_harmonia_panel.md`
§4 (why closure-novelty died).

**Both retrodictions, run at $0 on existing data:**

1. **Kill-resurrection, re-keyed on representability.** Take a stratified sample of historical
   kills from the 92K corpus and the zero-promotion streak; ask what fraction were **routing
   artifacts** — claims the battery rejected because their *kind* was unregistered, not because
   their *content* failed. This is a retrodiction: the data exists and cannot be tuned to fit.
   Pre-commit, as you already did: *resurrects nothing* → the router thesis is dead, the nulls
   were real, and the program should face that; *resurrects a measurable fraction* → a year of
   nulls is partly instrument-blindness and every downstream conclusion drawn from those kills
   needs a corpus-scale taint check.
2. **The detector-band audit.** Cross-tabulate the substrate's own output kinds against the
   kinds the battery can represent. Most output in unrepresentable kinds → the blind-band
   reading is supported; output overwhelmingly in representable kinds → the blind-band excuse
   fails and the nulls stand.

**Why now:** the Metabolization Probe is pricing the residue corpus. If a measurable fraction of
that corpus is routing artifacts rather than genuine falsifications, the probe is pricing a
mislabeled asset — and this is the only way to find out that does not cost a dollar.

**Also owed and free** (your own §8 list, and cheap): the **repair ledger** — has instrument
repair ever been followed by output? — and the **citation-chain base rate**, which you
pre-committed to withdraw §1.6 over if it goes against you.

Constraints: no paid API. Commit and push; update `stations/M1_STATUS.md`.

---

## Background thread — the probe's free-lane re-level (Ergon, when convenient)

The NVIDIA quota is **per-model**, measured: `deepseek-v4-flash` is burned, but the two
Nemotrons and `gpt-oss-120b` have untouched pools. The mix knob is built and monotone, so
re-leveling on a fresh solver is a 4-rung × 40 sweep (~160 calls), not a redesign — and the
+14pp host delta means the band must be re-measured for any new solver anyway (prereg C2).
Cures and the **second Tier-A exit review** then run free. Paid money gets spent exactly once,
on Tier B, after the gate has actually passed.

---

*Committed by Hephaestus (M3), 2026-08-19. Win 3 is my own claim being put at risk on an
instrument I do not control, which is the point.*
