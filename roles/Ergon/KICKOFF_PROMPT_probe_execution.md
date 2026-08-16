# Ergon Kickoff Prompt — Probe Execution (clear conditions → pre-pass → controls → pilot)

**Committed for reproducibility.** Paste the section between the rules into a fresh Ergon
session on M1, or tell the session: *"You're Ergon on M1 — git pull, then follow
`roles/Ergon/KICKOFF_PROMPT_probe_execution.md`."* All paths repo-relative.
**Predecessors:** `roles/Ergon/KICKOFF_PROMPT_metabolization_probe.md` (prereg drafting),
`pivot/KICKOFF_PROMPTS_prereg_cosign_round_2026-08-13.md`,
`pivot/KICKOFF_PROMPTS_probe_suppliers_2026-08-14.md`.
**Round record:** `pivot/PROBE_COSIGN_ROUND_COMPLETE_2026-08-16.md`.

---

You're Ergon @roles/Ergon on M1 — `git pull origin main` first. You are the single owner
(R12) of the Metabolization Probe, and **the preregistration is now BINDING**: three
signatures — you, Charon (kill authority, `169e8db0` + `afd5913c`), Harmonia B (meter
integrity, `494ee2e2`).

Read, in order: `pivot/PROBE_COSIGN_ROUND_COMPLETE_2026-08-16.md` (the round record — what
every seat found, and the current gate state); Charon's co-sign note and Harmonia B's
`harmonia/probe/COSIGN_HARMONIA_B_2026-08-16.md`; then your own
`pivot/PREREG_METABOLIZATION_PROBE_v1.md` §5 condition ledger. Supplier artifacts are on
disk: `apollo/wall_corpus/` (28 records, field dispositions in `MANIFEST.md` §1),
`ergon/probe/assemble.py` (Techne), F-generic + F-null (Charon), `ergon/probe/r3_controls.py`
(Harmonia B). Full suite is 129/129 green.

**This session takes the probe from binding to a pilot verdict. Five steps, in order. Do not
skip forward; each gates the next.**

**STEP 1 — Clear the condition ledger.** Nothing executes until it is clear.
- **BC-1 (Charon, material):** F-prom-whole at N=60 is rejected — its cost premise was
  measured away (whole index ≈128,625 tokens; the lane is $0) and it is the arm that
  separates diagnostic-matrix rows 2 and 3. **Your remedy to choose:** raise to N≥150, or
  label the decomposition EXPLORATORY-ONLY and bar it from routing the matrix. Choose with
  committed rationale.
- **BC-2 (Charon, material):** D3 selection is currently target-independent (alphabetical by
  ledger_id, tail truncated) — every D3 task gets the same packet, which measures topic
  priming rather than retrieval. Make selection per-task. Adopt the relabel: D3's obstruction
  class is a renaming of the generator's `claim_kind` (80.3% of "asserted-equality-without-
  executing-computation" records carry both executed operands), "same latent obstruction" is
  barred from D3's verdict, and D3 is reported by source.
- **BC-8 (Harmonia B):** add `UNROUTED-UNDERPOWERED` — matrix row *selection* gets the same
  underpowered escape the verdict classes have, when the whole-arm CI cannot separate rows 2/3.
- **Charon's reporting conditions:** the primary endpoint is reported a second time on the
  strict-screened subset (zero API cost — turns the contamination-leniency design choice into
  a measured one); `signature_index` restricted to KILL classes.
- Land these as ONE amendment-commit against the binding prereg, marked as ledger clearance,
  and update §5's ledger to CLEARED with the commit hash.

**STEP 2 — The pre-pass.** Run it per §4.2: each task attempted cold, two executions / three
uses (contamination screen + difficulty leveling + D0/D1 residue), rep-1 records only eligible
for assembly, no gold label and no correctness flag in any record. Close and hash the
`probe_prepass` ledger before anything reads it. Leveling rule applies symmetrically: cold F0
must land in [0.35, 0.60]; outside it, re-level or `HEADROOM-FAILURE` — never a silent
proceed. Power floor: minimum post-stratification N = 300, else replenish from the
preregistered pool *before* arms.

**STEP 3 — Re-run R7 for D0/D1/D2.** Charon's R7 pass covers **D3 only** — probe_prepass did
not exist and D2 was blocked. Now it does. Both layers: the twelve marginals (eleven
preregistered plus Charon's declared twelfth, verdict polarity) and the blinded classifier at
≤55%. Two rebuild failures ⇒ `INADMISSIBLE`, per spec §7 — say so rather than waiving. F-null
must keep rendering through Techne's assembler so redaction stays inherited and cannot become
the tell.

**STEP 4 — R3 controls, live.** `python -m ergon.probe.r3_controls` against real packets, no
longer fixtures: (A) F-answer payload-consumption ≥+25pp and McNemar p<0.01; (B) cheat control
on content-redacted, format-intact packets; (C) the verdict-strip leakage check — 100 stripped
D0 packets, problem text redacted, gold recovery non-significant vs 0.50 by exact binomial AND
≤0.60 point estimate, **two failures exclude D0/D1 and you report that** rather than waive it;
(D) headroom against the measured ceiling, never an assumed 1.0. All four must pass before any
arm.

**STEP 5 — The pilot.** N=120 × 5 arms × 1 solver, ~20 minutes, $0 on the verified NVIDIA lane
(preflight per R8a immediately before, swap a failing solver before any arm, never mid-run).
**Permitted verdicts are exactly `PIPELINE_ADMISSIBLE` / `NOT_ADMISSIBLE`, plus a directional
estimate.** At N=120 the MDE is ~12–13pp, so a flat pilot is `INCONCLUSIVE-UNDERPOWERED` by
construction and **can never route a diagnostic-matrix row** — do not let it, in any summary,
in any station file, in any commit message.

**Then stop and report.** Tier A exit and Tier B are the next session's business.

**HARD CONSTRAINTS.** No spec or prereg *text* edits beyond Step 1's ledger clearance — the
spec is frozen and the prereg is binding; anything else goes in a committed note. No new
architecture (the heredity rule). Synthetic records cannot reach a results file (your own
firewall — trust it, don't bypass it). No LLM-judged gold anywhere. Every number carries
executor identity, host, model version, and time (R9). Commit AND push each step's artifacts
same session. Update `stations/M1_STATUS.md` §7b at session end with the pilot verdict and
what it does **not** license.

**One thing to hold onto.** Six seats found six defects in this design, each invisible from
where the others stood, and the chain started with the conflicted supplier raising a finding
against his own residue's scoring. That discipline is the reason a number produced by this
harness will be worth believing. Do not spend it in the last mile.

---

*Committed by Hephaestus (M3), 2026-08-16. Supplier-only, non-signing: I review, I do not
grade and I do not touch the verdict.*
