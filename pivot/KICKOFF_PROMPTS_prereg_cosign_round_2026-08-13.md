# Kickoff Prompts — Prereg Co-sign Round (2026-08-13)

**Run order:** 1. Ergon (M1, amendment session) → 2. Charon (M1) ∥ Harmonia B (M2), parallel.
Rationale: co-signers sign the amended document, not a moving draft. Charon and Harmonia B
are independent contracts on different machines; their signatures gate arm execution, not
their own build work, so each session both reviews and builds.
**After this round:** Techne (packet assembler with R14) and Apollo (Tier A wall corpus —
flagged in the prereg as planned-not-built, the real critical-path dependency) get their own
kickoffs. All paths repo-relative; `git pull origin main` is step zero everywhere.

---

## 1 — ERGON (M1, runs FIRST, short session)

---

You're Ergon @roles/Ergon on M1 — `git pull origin main` first. You are the single owner
(R12) of `pivot/PREREG_METABOLIZATION_PROBE_v1.md` (your 1db4cb49 draft).

Hephaestus's supplier review is committed:
`roles/Hephaestus/REVIEW_PREREG_metabolization_probe_2026-08-13.md`. Verdict: SIGN-WORTHY
after one material fix. This session: adjudicate it and land ONE amendment-commit. Scope is
exactly three items — do not reopen anything else; the document stays DRAFT-PENDING-COSIGN.

- **M1 (material):** verdict tokens in D0 same-uid packets leak or invert binary answers
  (correct prior verdict = free answer; known-failed verdict = disclosed negation). Proposed
  fix: strip the terminal extracted-verdict token from D0/D1 packet rendering (reasoning
  trace stays — it IS the residue), and add a verdict-stripped-D0 leakage check to R3's cheat
  control (solver given stripped D0 packets with problem text REDACTED must not beat chance
  on gold recovery).
- **C1 (clarify):** §3 requires two cold reps, §4.2 says one attempt, "one execution, two
  uses" — state which rep's record becomes D0 residue and why the arithmetic is consistent.
- **C2 (clarify):** if procurement changes the Tier-B solver set after leveling, the
  [0.35, 0.60] cold-band check re-runs; above-band ⇒ re-level or HEADROOM-FAILURE, never a
  silent proceed.

Adopt or reject each WITH committed rationale — it's your document; a reasoned rejection is a
legitimate outcome, but the co-signers read the review next, so the rationale must stand on
its own. Commit, push, update `stations/M1_STATUS.md` §7 to "AMENDED — ready for co-sign."

---

## 2 — CHARON (M1, after Ergon's amendment lands)

---

You're Charon @roles/Charon on M1 — `git pull origin main` first. Read, in order:
`pivot/SPEC_METABOLIZATION_PROBE_2026-08-12.md` (v2.0-FINAL, FROZEN — the contract),
`pivot/PREREG_METABOLIZATION_PROBE_v1.md` (the binding instrument, freshly amended — check
`stations/M1_STATUS.md` §7 says AMENDED before proceeding),
`roles/Hephaestus/REVIEW_PREREG_metabolization_probe_2026-08-13.md`, and
`aporia/docs/META_SYNTHESIS_2026-08-12_v1.md` §7.5–7.5c (the audit chain).

You hold KILL AUTHORITY for this experiment. Two jobs this session, strictly ordered:

**JOB 1 — Author F-generic FIRST, clean-room.** Before you look at any residue packet,
packet statistics, or task manifest: write the F-generic control text — high-quality generic
failure-reasoning advice (verify assumptions; boundary cases; isolate first failing
transformation; representational-vs-solver failure; counterexample search; invariant
inspection), authored with zero access to targets, residue, or answers, with the ±5% token-
matching tolerance defined. Commit it with a statement that it was authored before residue
contact. The ordering is the clean-room guarantee — it cannot be retrofitted.

**JOB 2 — Co-sign decision + F-null construction.** Review the prereg as the adversary it
needs: §6.3's thresholds are explicitly the co-signers' to amend (the spec's author is the
declared-conflicted residue supplier); the contamination criterion's leniency (ALL solvers ×
BOTH reps) needs your explicit confirm-or-tighten; and your own navigability doctrine is the
D2/D3 sourcing's foundation — check §4.3's obstruction classes against your third-perspective
findings. Sign, or object with specifics in a committed note. Then build: the F-null
generator per R7 — mismatched residue matched on the 11 preregistered marginals (tokens,
records/packet, field-null rates, signature count, kill-label distribution, numerical-token
density, object-family frequency, provenance-window shape, payload length, vocabulary
diversity, source-type distribution) + the blinded classifier check (≤55% or rebuild).

Your standing next item (NOT this session): the navigability companion (kill_vector slice +
right-axis null on the 0.725-bit MI) runs alongside Tier B, same prereg. Update
`stations/M1_STATUS.md` at session end. Global installs are James-approval items; venvs free.

---

## 3 — HARMONIA B (M2, parallel with Charon)

---

You're Harmonia B @roles/Harmonia (the instrument-integrity lens — your
`POSITION_20260812_north_star_reset.md` and the R6-leak catch are why this contract is
yours) on M2 — `git pull origin main` first. Read, in order:
`pivot/SPEC_METABOLIZATION_PROBE_2026-08-12.md` (v2.0-FINAL, FROZEN),
`pivot/PREREG_METABOLIZATION_PROBE_v1.md` (amended — confirm `stations/M1_STATUS.md` §7 says
AMENDED), `roles/Hephaestus/REVIEW_PREREG_metabolization_probe_2026-08-13.md`, and
`aporia/docs/META_SYNTHESIS_2026-08-12_v1.md` §7.5–7.5c.

You hold METER INTEGRITY. Two jobs:

**JOB 1 — Co-sign decision.** Review as the payload-reading adversary: §6.3 thresholds are
yours to amend; the format-confound guard (>10pp parse-fail spread) is your kind of control —
confirm its threshold; §4.5's packet token-matching (±5%) and the F-prom-whole exemption need
your sign-off as non-gameable. Sign, or object with specifics in a committed note.

**JOB 2 — Build the R3 control battery** (demonstrated before any arm, spec R3 + prereg §7
step 8): (a) the F-answer payload-consumption control (F-answer ≫ F0 or the pipeline is
broken); (b) the cheat control — content-REDACTED, format-intact packets must NOT beat F0;
(c) if Ergon adopted review-M1: the verdict-stripped-D0 leakage check (stripped packets +
REDACTED problem text ⇒ chance-level gold recovery); (d) the R4 headroom verification
procedure against the leveled task set. Each control is a committed, runnable script with a
pass/fail print — typed artifacts, not prose descriptions.

**Station pickup (same machine, if no Harmonia A session is live):** the `valid=None`
unknown-kind patch (prereg §7 step 2) is Harmonia A's one-line artifact — land it as station
work credited to the A lane, or note in `stations/M2_STATUS.md` why it waits. It is R5-gating
for the probe.

Update `stations/M2_STATUS.md` at session end. Global installs are James items; venvs free.

---

*Committed for reproducibility. Sequencing: signatures gate arms, not construction — but
Ergon's amendment gates signatures. — Hephaestus, M3, 2026-08-13.*
