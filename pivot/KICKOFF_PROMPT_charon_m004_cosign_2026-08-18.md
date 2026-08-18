# KICKOFF — Charon: M-004 co-sign, injection, and the standing co-signer seat

**Filed:** 2026-08-18 by Aporia · **For:** a Charon session (paste the block below).
**Why Charon:** kill authority is Charon's existing role, and M-004's controls require a party
who is *not* Aporia. Aporia wrote the protocol, wants a particular answer, and disclosed that in
the prereg — so Aporia is disqualified from injecting, from holding the blind, and from
adjudicating its own instrument.

---

## What Charon is being asked to do (three things, ~one session)

1. **Co-sign or refuse the M-004 pre-registration** (`pivot/PREREG_M004_kill_resurrection_2026-08-17.md`).
   Kill authority. Refusal with reasons is a fully acceptable outcome and is not a delay.
2. **Perform the independent synthetic-signal injection** — the control that decides whether the
   instrument is validated at all. Aporia must not learn N or which records.
3. **Hold the blinding offset** for the headline statistic until unblinding is declared.

Separately (a standing role, not this session's work): **take the non-lineage co-signer seat**
for the germline, if James assigns it — every birth certificate and graduation test needs a
signature from outside the lineage, and Charon is the natural fit for the same reason as above.

---

## PASTE THIS INTO A CHARON SESSION

```
You are Charon. Aporia has filed a pre-registration that requires your kill authority and,
critically, requires a party who is not Aporia. Read it first:

    pivot/PREREG_M004_kill_resurrection_2026-08-17.md

Context you need:
- M-004 asks what fraction of the ~92K historical kills were INSTRUMENT ARTIFACTS rather than
  genuine falsifications. Harmonia A/D established that verify() returns invalid (not unknown)
  on unregistered claim kinds, firing 160/160 at R5/R7/R8. A genuinely novel result is by
  construction an unregistered kind. So the archive may contain true claims we recorded as false.
- Aporia originally justified this as "retrodiction is strong evidence because frozen data cannot
  be tuned to fit." That justification is RETRACTED. External methodology (DR 2026-08-17 prompt
  20) established the data is frozen but the PIPELINE is not, and that the archive's own team is
  MORE prone to hindsight bias, not less. The protocol was rebuilt around that correction.
- Aporia has disclosed a motivated direction in prereg section 2: a positive result vindicates a
  program Aporia argued for and would retroactively excuse a year of nulls.

YOUR THREE TASKS.

(1) ADJUDICATE THE PREREG. Co-sign, or refuse with reasons. Attack it the way you attack any
    claim. Places Aporia would most like you to look hard:
    - Is the 80% injection-recovery floor the right threshold, or is it a number that sounds
      rigorous while being easy to clear?
    - Is "representable | unrepresentable | indeterminate" (Stage A) genuinely mechanical, or
      does it smuggle in judgement that could drift toward resurrection?
    - Does the negative control (redacted content, structure intact) actually catch a
      format-reading instrument, given what you found about denylist-vs-allowlist leakage?
    - Is the 5% calibration slice large enough to develop on, and small enough that the hold-out
      stays clean?
    - Anything in the kill conditions that lets a bad run survive.
    A refusal is a real result. Do not co-sign to be agreeable.

(2) BUILD AND INJECT THE SYNTHETIC SIGNAL. This is the control the whole experiment rests on.
    - Construct N synthetic records that are genuinely TRUE and genuinely OUTSIDE the battery's
      dispatch table — i.e. true-but-unrepresentable, the exact class M-004 claims exists.
    - Inject them into the archive slice. Record N, their identities, and your construction
      method somewhere Aporia cannot read (your own session notes or a file Aporia is told not
      to open — state which).
    - Choose N yourself. Aporia deliberately did not specify it.
    - Note the sharp edge: if you cannot construct true-but-unrepresentable records at all, that
      is itself a finding — it would mean the class M-004 is hunting may not exist, and the
      experiment should be reconsidered before it runs.

(3) HOLD THE BLIND. Generate a random offset for the headline resurrection rate, keep it, and
    release it only when the analysis is declared technically complete. Aporia does all
    diagnostics on the offset number.

DELIVERABLES: a signed-or-refused verdict appended to the prereg's section 9 amendment log; your
injection recorded privately; the offset held. Commit your verdict; do not commit the injection
identities.

DOCTRINE THAT APPLIES: feedback_control_must_break_the_selection_relation (a control drawn from
the treatment's own selection relation IS the treatment); feedback_null_must_perturb_the_
statistics_axis; feedback_counter_baseline_discriminator; your own charter (trust nothing, kill
everything).
```

---

## What happens after Charon reports

- **Co-signed** → Aporia builds the 5% calibration set, runs the instrument against Charon's
  injected signals, and reports recovery rate. Below 80% the instrument is unvalidated and the
  hold-out is never touched.
- **Refused** → the objection goes into the prereg amendment log, the protocol is rebuilt, and
  M-004 stays queued. Two rebuilds maximum before it escalates to James, because repeated
  rebuilding is how pipelines get tuned to noise.
- **Injection impossible** → the most interesting outcome: if true-but-unrepresentable records
  cannot be constructed, the class M-004 hunts may be empty, and that finding lands before any
  compute is spent.
