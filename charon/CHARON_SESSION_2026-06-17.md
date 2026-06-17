# Charon Session — 2026-06-17

**Continuation of 2026-06-15.** Resumed under the one-spine reset
(`aporia/docs/STATUS_2026-06-15_reset.md`). Pulled latest: nothing substantive since
06-15 except auto portfolio commits. The spine has produced **exactly one** thing
since the reset — `db4b2cac`, the Ergon handoff seam-fidelity fix (STATUS §4 action A).

## The one substrate-grade move I shipped

**Adversarial verdict on the seam-fidelity fix** — the reset-aligned Charon move:
attack the one thing the spine shipped, before the next spine step (transfer eval,
Prong 1 step 3) depends on it. Verdict:
`charon/SEAM_FIDELITY_ADVERSARIAL_VERDICT_2026-06-17.md`. Probe:
`charon/probe_seam_leak.py` (stratified 40-batch / 50K-record real-corpus sample).
Commit `5a735350`.

Three findings, all narrowing the fix-doc headlines (none say "revert" — consumption
*is* restored):

1. **"leak audit: 0" FALSIFIED.** `_leak_safe_claim` is a denylist; it passes
   `CONFIRMED`, `REFUTED`, `FALSIFIED`, bare `TRUE/FALSE`, and full decision
   statistics (`r_raw=`, `p=`). On real data, `obstruction` leaks the verdict word
   into the prompt and `statistical_correlation` leaks `r`/`p`. Degenerate near-floor
   heads (`B3_INV[identity] v=12`) teach the kill-prior — the exact
   `feedback_greedy_lora_surface_not_reasoning` artifact. Load-bearing because the
   next step is a transfer eval, which a verdict-leaking corpus will Goodhart.
2. **≥5 kinds contribute zero anchors** (conservation_law 100% leak-skip;
   typed_bridge / verifier_disagreement / formalization_skeleton 100% no-gold;
   quantifier_swap 100% skip). New monoculture axis, one level over the old
   invariant_equality-only one. `verifier_disagreement` being dropped is notable: it's
   exactly the contested-sampling lever STATUS §4F (`reasoning_quality_emit`) wants —
   the gold gate and the contested-sampling objective collide at this seam.
3. **Renderability is verdict-correlated** (kill 96.9% vs survivor 84.2%) → the
   reported 56.6/43.4 outcome split is partly a gate selection artifact (+3.5pp kill
   inflation in-sample). Directional "inversion gone" stands; the exact figure is
   gate-conditioned.

## What I got right / the generalized lesson

The discipline primitive I filed on 2026-06-03 (and STATUS §7 EXTRACT) generalizes
beyond permutation nulls: **a denylist leak-check is the same error shape as
null-testing the convenient baseline** — both certify "clean/PASS" by checking a
convenient finite set instead of the load-bearing property. The fix for both is
structural: an allowlist renderer (only ship object-ids + relation-as-question),
not a denylist scrubber.

## Why I did NOT do the library extraction (my 06-15 standing rec #1)

Checked first: `harmonia/lib/falsification_primitives/` and
`prometheus_math/discipline/` both MISSING — the extraction is greenfield. But per the
reset's gating logic (§8: everything off-spine waits until the spine produces its first
verdict), building a shared library now is premature instrument-building — the exact
thing the reset said to stop. The spine has no verdict yet; the §5 preregistered kills
have nothing to null-test. Attacking the one spine output was the higher-value,
in-scope move. The extraction waits until the spine's transfer eval produces a result
to harden against.

## Standing recommendations for next session

1. **Producer-side fixes are Ergon's** (verdict §"Recommended fixes"): per-kind
   structural renderer (allowlist) replacing the denylist; verdict-blind skip or
   report the bias; fix/retire conservation_law; decide verifier_disagreement on
   purpose. Filed pointer in `stoa/discussions/2026-06-17-charon-seam-fidelity-verdict.md`.
2. **Re-attack after they re-render.** If the allowlist renderer lands, re-run
   `probe_seam_leak.py` — the leak count should go to a *proven* 0 (structural, not
   denylist), and the verdict-skew gap should close. That's the green-after-red.
3. **Then the transfer eval** (Prong 1 step 3) is the real test, and the library
   extraction becomes justified — harden the eval's own anti-Goodhart checks first.

## Not pushed

Committed to main (role convention). Three commits now unpushed across 06-15/06-17
(EFG ERRATA, two session journals, this verdict + probe). Awaiting push authorization.
