# C3 RESUME (WITHHELD) -- read this first after a context reset

Currency: 2026-09-25T10:45Z. This file lives ONLY on the local branch cosmos/c3-s1-2026-09-24 in the M2
worktree Prometheus-worktrees/cosmos-base-role. NEVER push this branch (or merge it into anything that is
pushed) until D's seal is committed AND pushed by D's author. Public entry: roles/Cosmos/BOOTSTRAP.md.

## 1. Where C3 stands (all numbers are recorded in the files named)
- Certificate v3 QUALIFIED (roles/Cosmos/c3/S1_PREREG_P1P2_GATE.md, public).
- Visible families A rnn / B graph / C stig + hybrid H (prometheus/cosmos/c3/substrates.py).
- Preliminary law (S1_RESULT.md): FUNCTIONAL iff sR > 0.0304 [95% CI 0.0064, 0.0425]; PASSIVE iff
  sR ~ 0 and sF > 0; sR/sF = decoder-free history-signal shares of the actor view / full causal state
  (prometheus/cosmos/c3/geometry.py). Gates L1-L5 PASS (L5 2/44 confirmed misses).
- SCAR (frozen, NOT patched -- operator 2026-09-24): noisy excitable graph worlds (b = +.5, p .03-.1):
  predicted FUNCTIONAL, certified NONE; readout-view signal GROWS over the delay (sensitivity, not
  reliable information). D should say whether this is graph-specific or a second missing axis.
- Substitution attacks (S1_PREREG_SUBSTITUTION.md): COMM 23/23, POP 21/22, RECOMP 22/22 -> HOLD.
  QUALIFICATIONS TO KEEP PROMINENT (operator 2026-09-25): (1) COMM's positive side is EXPLORATORY only
  (period-2 loop, preregistered delays hit the wrong phase; odd-k supplement 12/12, not gated);
  (2) the RECOMP prediction (S3) was genuinely WRONG -- stays in the scar/calibration ledger.
- Session 1 review packet: roles/Cosmos/c3/REVIEW_PACKET_C3_S1_2026-09-24.txt (withheld; add the
  substitution results as an addendum when publishing).
- Operator notes: prompts/2026-09-24_operator_s1_decisions/, prompts/2026-09-25_operator_pre_D_notes/.

## 2. Frozen behaviour (operator 2026-09-25: "freeze behavior, preserve the scars")
NO methodological changes before D: not to sR, sF, geometry.py, the threshold, the certificate, the
lattices or the gates. Any idea goes into a note for AFTER D.

## 3. The sequence (do exactly this, in order)
1. WAIT for Nestor (M1) to push D's seal (comms #561; contract roles/Cosmos/c3/D_CONTRACT.md). Check with
   `python -m comms sync Cosmos` (EW_DB_HOST=192.168.1.202). Record every D fact in INFO_LEDGER.md.
   Verify the seal commit is an ancestor of origin/main before step 2.
2. PUBLISH the withheld branch: merge origin/main into it, confirm that commit 0ecafed159f9bc9756baefd55ec37fd75b83b822
   (the head hash-committed in INFO_LEDGER.md on main) is an ancestor of the branch head, run the tests,
   push to main. Announce that the committed withheld material is now public.
3. HARMONIA: post roles/Cosmos/prompts/2026-09-23_c3_harmonia_audit/PROMPT_TO_HARMONIA.md (update it to
   cite the frozen A/B/C coordinate construction geometry.py + normalisation + maps + per-family residuals;
   send ONLY the coordinate layer, no request to judge the law's truth). Verdicts: AUDIT_PASS / REVISE /
   REJECT. REVISE -> revise from A/B/C only, D stays sealed and unqueried. REJECT -> stop before D.
4. On AUDIT_PASS: write the D FREEZE file before any D outcome: the law + threshold + CI, the translation
   of D's native measurements into sR/sF (geometry.py run through D's System interface -- no D outcomes
   needed to compute coordinates? NO: coordinates need rollouts; decide in the freeze file whether
   Cosmos may compute coordinates on D's worlds before adjudication, and record it in INFO_LEDGER as
   KNOWN_TO_COSMOS_BEFORE_FREEZE), the prediction per sealed world, and ONE intervention do(knob: a->b)
   with direction/magnitude/uncertainty. Hash and push the freeze file.
5. SPEND D ONCE (broker pattern: predictions receipted before any D certificate runs). No iteration.
6. Only then consider E (Aether, from M4 only).

## 4. How to read D (operator 2026-09-25)
Narrow question: does the same actor-view accessibility relation predict functional historical use in a
substrate whose author did not know the law, coordinates, visible results or failure regions?
- PASS -> first genuinely nontrivial Cosmos result beyond instrument qualification.
- FAIL resembling the chaotic-graph scar -> sR likely misses a second axis (reliability/stability of
  transmitted history).
- PASS trivially (sR ~ equivalent to P2) -> next campaign goes one level deeper: what physical pressures
  CREATE reliable causal accessibility.
