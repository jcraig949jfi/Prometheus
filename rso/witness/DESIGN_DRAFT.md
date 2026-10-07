# Native retained-information witness -- design draft (C-009-T012)

Author: Cadmus[m1-a86ec5e4], claude-opus-5-5, 2026-10-07. Status: DRAFT for preregistration; nothing here is an
outcome. Runtime: Ares (rso/witness/CANDIDATES.md C1), subject to Palamedes's selection. This witness opens as its
own campaign only if C-009 closes CC1-CC4 (directive s6); it then gets its own preregistration, ledger and budget.
Shared machinery is rso.binding (BX1-BX7) and the slice001 evidence plane; nothing here changes either (BX6).

## 1. Question and claim

Q: Does a frozen Ares organism, evolved without reference to this witness, retain the regime bit r of world W15
across the world's activation-reset events through its declared allowed channel (plastic weights), and use it?

Registered claim (relative, closure C2): "In world W15 (Ares, registered seeds), subject S answers the regime r after
the last interrupt better than the registered no-carry bound, and the advantage is mediated by plastic W1: it
vanishes under the plasticity ablation." Rendered only with the subject digest, world variant, seed set, bound and
intervention set. No class, recursion, mechanism-in-general or cross-physics wording (closure C2, D08).

## 2. Boundaries, channels, oracle (from the runtime's own code)

  B1  W15 interrupt (ares/worlds.py:430; rollout zeroes v[:, OBS_DIM:] at 4 unobservable steps after the cue).
      Allowed across B1: live plastic W1 and the genome. Forbidden: activations (erased by the world itself).
  B2  Runtime.reset() between episodes (ares/substrate.py:398-400). Allowed across B2: the genome only.
      Forbidden: v and every plastic change to W1 made in the episode.
  Oracle: world.r per episode (info["regime"]), drawn by the world, shown in the cue only at steps 0-2, never read
  by the ruler from the organism. The ruler sees actions and the oracle; the organism never sees the oracle.

## 3. Subject (frozen before any witness episode)

- Produced by ares.search.run on W4 "present" (no interrupts), registered config, P, G, eps, GA seed; selection uses
  the GA's own seeds and ares.search.EVAL_SEEDS only. The champion genome's bytes are hashed and committed; the
  witness never selects among subjects after seeing witness outcomes. (Evolving on W4, not W15, avoids training on
  the test boundary; a W15-evolved subject is a registered secondary arm, not a substitute.)
- Witness seeds: a fresh registered set, disjoint from GA seeds and EVAL_SEEDS, balanced on (r, shown).

## 4. Arms, controls and predicates

Arms (each a client-side wrapper; no Ares source edit):
  S        the subject, correct resets                                 main arm
  S-NOPL   S with plasticity disabled (R = 0 / allow_plasticity False) allowed-channel ablation (CHANNEL analogue)
  S-LEAK   S with a delayed-leak episode reset: v := 0 but live W1 NOT restored from the genome   (ERASE broken case)
  POS      hand-wired PLAST carrier (ares/carriers.py vocabulary)     ruler positive control (must be detected)
  RECUR    hand-wired activation self-loop carrier                    channel control: retains in W4, must lose in W15
  NULL     reset_each_step / random population                        negative control (no carry)
  SHUF     W15 in "shuffled" mode (cue decoupled from r)              calibration world (bound check)

Predicates (outcome typing per C1: execution / authority / outcome; a gate is PASS/FAIL, the ruler
POSITIVE / NEGATIVE / NOT_SHOWN / INDETERMINATE):
  P-CAL   calibration gate: on SHUF and with NULL, the post-interrupt answer accuracy is at the registered no-carry
          bound within the registered margin; POS exceeds it. FAIL here makes every ruler outcome UNQUALIFIED.
  P-RET   retention ruler on S: post-last-interrupt accuracy on r vs bound, registered test, alpha, sample size and
          INDETERMINATE band (stochastic native setting; exact enumeration does not apply).
  P-CHAN  channel gate: S minus S-NOPL advantage present (registered test); otherwise the claim may not name W1.
  P-ERASE erase gate on B2: pre-cue actions of episode k+1 independent of r_k for S (PASS expected) and dependent for
          S-LEAK (FAIL expected) -- the fire pair for this native boundary.
  P-PRES  preservation gate on B2: the genome reproduces identical behaviour on a fixed seed after reset vs fresh
          instance (restart-style twin).
  P-OBS   observer gate: rollout(record=True) vs record=False give identical actions on every witness seed.

## 5. Expected outcome classes (registered before data)

  POSITIVE               P-CAL PASS, P-OBS PASS, P-ERASE pair as expected, P-RET POSITIVE, P-CHAN PASS
  NEGATIVE               instrument qualified (P-CAL, P-OBS, P-ERASE pair as expected) and P-RET NEGATIVE
  DETECTION_UNQUALIFIED  P-CAL or P-OBS FAIL, or the P-ERASE fire pair does not separate, or P-RET INDETERMINATE at
                         the cap; the limitation is reported as the result (directive s7)
  A positive P-RET with P-CHAN FAIL is reported as "retention by an unidentified channel", never as W1 retention.

## 6. Adapter and evidence (rso.binding, BX6)

The Ares client builds canonical receipts per predicate node (subject digest = genome bytes sha256, world variant
and code CodeRefs, seed list, observer id, action traces and oracle values as artifacts) and one ledger row per
node execution (parent_run_id = the top-level launch, receipt_sha256 = sha256(canonical bytes)). Node ids are opaque
to rso.binding; parsing stays in the client. No shared code reads genome or activation semantics.

## 7. Budget (proposal; the witness campaign sets its own caps)

Smoke cost: 64 organisms x 16 W15 episodes = 0.08 CPU-s. Proposal: subject evolution <= 10 CPU-min; all arms and
controls <= 10 CPU-min; <= 6 top-level launches; 0 GPU; $0; one independent Q3 challenge on the frozen witness path
(1 sound, 2 broken, 2 edits), one repair round.

## 8. Open questions for the preregistration (to Palamedes / Argus)
1. Exact no-carry bound and test for P-RET (a balanced binary target gives 1/2 per step; the registered statistic
   and INDETERMINATE band need Argus's evidence-plane sign-off).
2. Whether S-LEAK belongs in the witness campaign's fire set or in C-009's CC1-style end-to-end fire cases.
3. Whether the subject is evolved once (recommended) or several subjects are registered with an aggregation rule.
