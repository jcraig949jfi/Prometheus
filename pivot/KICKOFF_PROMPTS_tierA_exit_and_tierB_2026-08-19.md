# Kickoff Prompts — Tier A exit review, then Tier B (the decisive run)

**Where this stands.** The pilot ran clean (`7744ac28`): 146 post-screen tasks × 5 arms, 730
calls, zero parse failures, zero transport failures, `PIPELINE_ADMISSIBLE`. The reading ladder
came out in the spec's predicted order for the first time on real residue —
`F-answer 93.8% >> F-oracle 48.6% > F-prom 45.9% > F0 43.2% > F-null 36.3%` — with F-null
*below* F0, the identity control behaving as an identity control. Directional only:
**Δ_carry = +9.6pp, CI95 [−0.7, +19.2], p = 0.068**. The interval touches zero; it routes
nothing and classifies nothing, exactly as preregistered.

**Two sessions, in order.** Tier A exit is a review gate held by the co-signers, not by the
driver — the pilot was run by the seat whose thesis it tests, and the preregistration exists
precisely so that seat does not also certify its own readiness. Tier B follows only if exit
passes.

**Run order:** 1. Charon ∥ Harmonia B (Tier A exit review, independent) → 2. Ergon (Tier B).

---

## 1 — TIER A EXIT REVIEW: CHARON (M1) ∥ HARMONIA B (M2), independently

*Both seats get the same brief. Rule independently; reconcile after. The value of two reviews
is that they were reached separately (§1.6).*

---

You're **[Charon @roles/Charon on M1 — kill authority]** / **[Harmonia B @roles/Harmonia on M2
— meter integrity]**. `git pull origin main` first. This is the **Tier A exit review**: the gate
between a working pipeline and the decisive run. Read `ergon/probe/ledgers/pilot_d0_2026-08-19.json`
and commit `7744ac28` in full; then the four sessions that produced the leveled manifest
(`a88d5896` paid lane, `aaf5d377` host delta +14pp, `3d2226fb` first leveled manifest,
`3625ea6d` D0 leakage closed by method projection, `573334dd` R7-D0 + R3 live); then
`pivot/SPEC_METABOLIZATION_PROBE_2026-08-12.md` §4.2 (Tier A exit criteria) and
`pivot/PREREG_METABOLIZATION_PROBE_v1.md` §5.0 / §6.3.

**The question: does Tier A exit, or not?** Spec §4.2's criteria are R3 both controls, R7 both
layers, R13 stratification, the R14 planted-violation failing loud, typed results end-to-end,
and `F-answer ≫ F0` / `F-oracle > F0` at preregistered significance. Verify each against
committed artifacts rather than against the commit message — the standing rule is that a claim
is corroborated only when more than one agent has executed it.

**Specific items each of you should treat as yours:**

- **Charon.** R7-D0 passed at 0.317 on the *new* family — your F-null construction, re-verified
  against a manifest it was not built for; confirm the twelve marginals and the classifier
  bound still hold on the M30 family, and rule on whether D0-only scope is correctly carried
  into the pilot's reporting. Your own through-line (Δ_carry interpretable at D0 alone) is what
  reduced this experiment's scope; check the reduction was applied and not merely stated.
- **Harmonia B.** R3 controls ran live and all passed — verify against the OC standard you
  built them to, not against a pass/fail line. Note the recorded deviation: **token matching
  was unmeetable at projected-packet scale**, and per-arm means show F-null averaging 494
  tokens against F-prom's 212 — the losing arm carried more than twice the text. Rule on
  whether that asymmetry is acceptable (it runs conservative for Δ_carry, but it is a
  deviation from a binding requirement and it is yours to adjudicate), and on whether the
  ±5% rule needs re-specification for Tier B rather than a second deviation note.

**Both of you: rule on Tier B's parameters before the data exists.** N (prereg says target 400
/ floor 300 post-screen; the pilot's post-screen yield was 146 of a larger manifest — say what
manifest size delivers 400 post-screen), whether the +14pp host delta requires anything of the
Tier B solver pinning, and whether the single-solver design still satisfies R15 or whether a
second family is now affordable on the paid lane (it costs single-digit dollars; the constraint
was never money).

**Verdict vocabulary: `TIER-A-EXIT-PASS` / `TIER-A-EXIT-FAIL`, with conditions if pass.** A
conditional pass is legitimate; a silent pass is not. Commit your review; update your station
file. No spec/prereg text edits — conditions land as your note and Ergon amends.

---

## 2 — TIER B: ERGON (M1). Only after both exit reviews land.

---

You're Ergon @roles/Ergon on M1 — `git pull origin main` first. You are the probe's single
owner (R12). Both Tier A exit reviews have landed; read them, adopt their conditions, and note
where they disagree rather than flattening it.

**This is the decisive run.** Everything since 2026-08-12 exists to make this number
interpretable: the spec's two hardening rounds, three dead difficulty axes, two preregistered
gates that stopped the experiment rather than let it produce a defensible-looking number, six
seats' worth of adversarial findings, and a pilot that came out in the predicted order.

**Run it as preregistered. Specifically:**

- **N at full preregistered scale** — target 400 post-screen, floor 300 (§2, §5.0 BC-1 as you
  amended it). The pilot's 146 is below the floor; size the generated manifest so that
  post-screen yield clears 400, using the measured screen-out rate rather than an assumed one.
- **Primary endpoint, single and uncorrected (R15):** paired task-level
  `F-prom-retrieved − F-null` on the pooled manifest, unit = task, two-sided paired bootstrap,
  10,000 resamples, seed 0, via the instrument-validated `paired_bootstrap_p`. Everything else
  — per-domain, decomposition quantities, behavioral metrics — is secondary, BH-FDR at q=0.05,
  labeled exploratory.
- **The §6.3 verdict classes apply now, for the first time,** and they apply to the pooled
  endpoint only (`classify_pooled_only` raises on a stratum, by construction). CARRY-STRONG
  requires Δ ≥ +8pp AND CI-LB > 0 AND harm ≤ 0.5 × gain; CARRY-STRONG-BUT-HARMFUL, CARRY-WEAK,
  DETECTABLE-BUT-INERT below the +5pp practical floor, bounded-null, and
  `INCONCLUSIVE-UNDERPOWERED` — which **cannot route to Path γ** and routes to
  replenish-and-rerun instead.
- **Mandatory secondary metrics (§6.5):** harm_rate (P(arm breaks an F0 success)),
  solved→unsolved / unsolved→solved, answer-changed, and the behavioral set —
  attempts, tokens-to-verdict, and **repeated-dead-approach rate**. Given this family, the last
  one is unusually meaningful: did the solver re-run a test its own packet recorded as having
  failed? That is the KillVector thesis measured directly, and a +3pp accuracy change with a
  large drop in repeated-dead-approaches would be the more scientifically interesting result.
- **Report D1–D3 as the separately-named distance description** with no Δ_carry and no verdict
  class attached, exactly as recorded in `a6434d23`. The ladder's transfer question is not
  answered by this run and must not appear to be.
- **Preflight per R8a immediately before**, paid lane, atomic writes, per-arm parse/truncation/
  timeout diagnostics beside accuracy. If any two arms differ >10pp in parse-failure, that
  solver is `INADMISSIBLE-FORMAT-CONFOUNDED` and excluded — say so rather than waive it.

**Then stop and report — do not adjudicate your own verdict.** Per R10 the headline computation
gets an **independent re-computation from the committed result objects** (requested of Aporia;
fallback Harmonia B), and per §4.1 **Charon adjudicates the verdict against the preregistration**.
You produce the number and the artifacts; the classification is not yours to pronounce.

**Constraints.** No new architecture (heredity rule). No spec edits. Every number carries
executor identity, host, model version, time (R9). Suite green before push. Commit and push each
step; update `stations/M1_STATUS.md`.

**One line to hold.** A null here is a real result and the preregistration was built so it can
be read as one — bounded to the tested regime, never "at any capacity," with the four null
sublabels (representation / consumption / retrieval / residue) waiting to be assigned. The
program's failure mode has always been thin numbers becoming doctrine. This design's whole
purpose is that whatever comes out, we will know which kind of thing it is.

---

*Committed by Hephaestus (M3), 2026-08-19. Supplier-only, non-signing: the residue being priced
is substantially forge-sourced, so I do not review the exit gate, do not grade, and do not
adjudicate the verdict.*
