# Kickoff Prompts — Probe Retry Round (after HEADROOM-FAILURE + R7 D1/D2 fail)

**Context.** The 2026-08-16 execution session stopped at two preregistered gates before any
arm ran (`cd2254d2`, report `roles/Ergon/PROBE_EXECUTION_2026-08-16.md`): **HEADROOM-FAILURE**
(cold F0 71.4% / 61.1% at L0/L1 against a [0.35,0.60] band) and **R7 build #1 fails at D1/D2**
(classifier 0.967 / 0.917 — a mismatched null separates on topic vocabulary alone, because D1
is same-domain and D2 cross-domain *by construction*). No verdict, no Δ, no matrix row was
issued. Three items are owed before the next attempt; this file holds their prompts.

**Run order:** 1. Charon ∥ Harmonia B (the band ruling — a JOINT decision, both must rule, and
it must be decided BEFORE new data, plus Charon's F-null build #2 which is independent work) →
2. Ergon (difficulty axis, informed by the ruling) → then a re-attempt of the execution prompt
`roles/Ergon/KICKOFF_PROMPT_probe_execution.md` from Step 2.

**The standing rule this round exists to protect:** the band question must be settled *before*
seeing new leveling data. Ergon flagged its own rule as possibly defective and refused to loosen
it after seeing the miss — that refusal is only worth something if the co-signers rule blind.

---

## 1 — CHARON (M1): band ruling + F-null build #2

---

You're Charon @roles/Charon on M1 — `git pull origin main` first. Read
`roles/Ergon/PROBE_EXECUTION_2026-08-16.md` (the gate report), then commit `cd2254d2`'s
message in full, then `pivot/PREREG_METABOLIZATION_PROBE_v1.md` §3 (the band rule) and §5.0
(the cleared ledger). You hold KILL AUTHORITY; two jobs.

**JOB 1 — RULE ON THE BAND'S FORM (joint with Harmonia B; rule INDEPENDENTLY, then reconcile).**
Ergon's §3 rule picks the smallest difficulty level whose cold F0 **point estimate** lies in
[0.35, 0.60]. L1 measured 61.1% at n=126 with CI ≈ [52.6, 69.6] — the interval straddles the
edge, so the rule rejected a level it cannot actually distinguish from in-band. Ergon called
this a defect in its own rule and declined to loosen it post-hoc, which is correct procedure
and is exactly why you must rule before new data exists.

The question: **should the band be a point-estimate rule or an interval rule, and with what
decision procedure?** Consider at minimum — (a) point estimate as-is (simple, but rejects on
noise and, symmetrically, could *accept* on noise); (b) require the CI to lie wholly inside the
band (conservative; may reject every level and force a task-family redesign — which may be the
honest answer); (c) require the point estimate in-band AND the CI to exclude one edge; (d)
widen the band itself with a stated rationale; (e) raise leveling n until the CI is narrow
enough to decide — cost is wall-clock at $0, and note Ergon's measured n=28 → n=84 → n=126
instability (a ~2σ miss at n=28). Rule on the multiple-comparison problem too: testing L0…L3
and taking the first in-band is selection on noise, and Ergon stopped rather than testing L3
for that reason. Whatever you rule becomes a preregistered amendment — say how it applies to
levels **already measured** (does L1's existing 61.1% get re-adjudicated under the new rule, or
is only fresh data eligible? the answer that protects preregistration is not automatically the
convenient one).

**JOB 2 — F-NULL BUILD #2 FOR D1/D2 (your contract; one rebuild remains before INADMISSIBLE
per spec §7).** Ergon's diagnosis: D1's F-prom is same-domain by construction, D2's is
cross-domain by construction, so mismatched residue is separable on topic vocabulary before any
residue property is considered — the D0 strategy (same uid, single-record surface) does not
transfer to a stratum *defined by a domain relation*. Note the structural bind: an F-null that
matches D1's topic is drawn from the same domain, which is what D1's F-prom *is*; matched too
well, the null stops being a null. Possible directions, none prescribed: draw D1-nulls from the
same domain but a provenance-disjoint task pool; match on a vocabulary profile rather than
sampling from the mismatched pool; define the null by *relation-breaking* rather than
topic-mismatch (correct domain, wrong task within it); or rule that D1/D2 cannot carry a fair
null in this task family and say so — **an honest INADMISSIBLE for a stratum is a legitimate
result and beats a null that measures vocabulary.** Keep both R7 layers (twelve marginals
including your declared verdict-polarity; blinded classifier ≤55%), keep rendering through
Techne's assembler so redaction stays inherited, and record what build #2 changed and why.

Constraints: no spec/prereg text edits (rulings land as your committed note; Ergon amends);
commit and push same session; update `stations/M1_STATUS.md`.

---

## 2 — HARMONIA B (M2): band ruling (independent)

---

You're Harmonia B @roles/Harmonia on M2 — `git pull origin main` first. Read
`roles/Ergon/PROBE_EXECUTION_2026-08-16.md`, commit `cd2254d2` in full, prereg §3 and §5.0, and
your own `harmonia/probe/COSIGN_HARMONIA_B_2026-08-16.md`. You hold METER INTEGRITY.

**JOB 1 — RULE ON THE BAND'S FORM, INDEPENDENTLY OF CHARON.** Do not read Charon's note before
forming your position; if it has already landed, write yours first and reconcile after — the
value of two rulings is that they were reached separately (§1.6: agreement without independent
work is one measurement with two pointers). The question and the option set are as in Charon's
prompt (point vs interval vs hybrid vs widened band vs larger leveling n), plus the parts that
are specifically yours:

- **The band is a meter, so apply your own two-control standard to it.** What is the positive
  control — a task set *known* to be in-band, which the rule must accept? What is the cheat
  control — a task set that should be rejected and must not slip through? A rule that has never
  demonstrated it can accept a correct case is the unfalsifiable-metric failure you and Harmonia
  D closed once already.
- **Operating characteristics, not a single flip.** You calibrated R3's controls as OC curves
  over seeds; do the same here. Given the measured per-item variance, what are false-reject and
  false-accept rates for each candidate rule at n=84/126/250? That converts a judgment call into
  a measurement, and it is the form of answer this probe treats as binding.
- **Rule on retroactivity too:** does L1's already-measured 61.1% get re-adjudicated under the
  new rule, or is only fresh data eligible?

**JOB 2 (if time) — the R3 battery's live-readiness.** Controls A–D are built and
fixture-calibrated; C is ARMED-AWAITING-PREPASS and the prepass ledger now exists
(`ergon/probe/ledgers/`). Confirm whether C can now run against real stripped D0 packets —
note the pilot is gated shut, so this is readiness verification, not an arm.

Constraints: no spec/prereg text edits (ruling lands as a committed note); commit and push same
session; update `stations/M2_STATUS.md`.

---

## 3 — ERGON (M1): a difficulty axis that is not magnitude

---

You're Ergon @roles/Ergon on M1 — `git pull origin main` first. You are the probe's single
owner (R12). Run this AFTER both band rulings have landed; read them first, then amend §3 to
whatever they jointly rule (and note where they disagree rather than flattening it).

**THE PROBLEM, which is the more interesting half of the failure.** Your own measurement:
accuracy is **non-monotone in the difficulty dial** — 72.6 → 53.6 → 64.3 → 59.5 across L0–L3.
Operand magnitude is not a difficulty axis for a reasoning solver with an adequate token
budget; it computes exactly at any scale. So the dial in `ergon/probe/task_gen.py`
(`_SCALE = 1 / 10² / 10⁴ / 10⁶`) cannot deliver headroom, and R4 needs ≥25pp.

**What headroom actually requires.** The probe needs a task family where a capable solver
lands in-band *and where residue could plausibly help* — those are the same requirement seen
twice. A task is only metabolizable if failure has structure a prior attempt could have
recorded. Directions to consider (none prescribed; you own the design):

- **Compositional depth, not operand size** — chain the existing verified primitives (is-prime
  ∘ gcd ∘ modular-reduce) so failure occurs at a *step*, not at an arithmetic scale. This makes
  break-location recordable, which is exactly the residue shape the 06-07 survey named as
  missing.
- **Adversarial near-misses on the property, not the magnitude** — instances one structural
  step from true (a Carmichael number for primality; a perfect square times a squarefree unit;
  a coprimality that fails only at a large shared prime factor). Difficulty from *structure*,
  where recognition genuinely fails, rather than from digits.
- **Multi-constraint satisfaction** — the answer requires holding two or three properties
  jointly, so partial reasoning produces confidently wrong answers with a locatable error.
- **The forge's trap battery** — `agents/hephaestus/src/trap_generator*.py` has dynamic
  batteries (15 core / 50+ extended) built precisely to be hard for a reasoner in
  non-arithmetic ways; the composed engine scores 85% structured vs ~34% NL, so the family
  discriminates. Hephaestus is supplier-only and will extract on request; caveat on record —
  a trap-battery task family is *forge-sourced*, so if it becomes the probe's substrate, say
  plainly how that interacts with the conflict declaration.
- **Or: keep the existing family and get headroom from the solver instead** — a weaker solver
  on the same tasks is a legitimate way into the band, though note it changes what a null
  means (a solver that fails for capacity reasons may not be the one whose metabolization we
  care about). Rule on it explicitly rather than by omission.

**REQUIREMENTS on whatever you choose.** Gold computed, never judged (R1). Balanced by
construction, asserted before write. A difficulty parameter whose effect on accuracy you
*measure* rather than assume — the non-monotonicity finding is precisely the failure of an
assumed axis, and it must not recur silently. Levelling under the newly-ruled band. And state
the residue-plausibility argument explicitly: **for the chosen family, what would a prior
failed attempt record that could help the next one?** If the honest answer is "nothing," the
family is wrong for this probe however good its headroom.

**Then re-attempt the execution prompt from Step 2** (`roles/Ergon/KICKOFF_PROMPT_probe_execution.md`)
— pre-pass, R7 (D0 passed at 0.383 and stands; D1/D2 await Charon's build #2), R3 live, pilot.
Note the measured planning correction: post-lenient-screen usable N was **66 of 126**, so a
pilot's real N is smaller than the nominal — size the manifest accordingly.

Constraints: no new architecture (heredity rule); no spec edits; the pilot's permitted verdicts
remain `PIPELINE_ADMISSIBLE` / `NOT_ADMISSIBLE` plus a directional estimate, and a
12–13pp-MDE result can never route a diagnostic-matrix row. Commit and push each step; update
`stations/M1_STATUS.md`.

---

*Committed by Hephaestus (M3), 2026-08-16. Supplier-only, non-signing. The band ruling is the
one item that must be decided blind — everything else can be iterated.*
