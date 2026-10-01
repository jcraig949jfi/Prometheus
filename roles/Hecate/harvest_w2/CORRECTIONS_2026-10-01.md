# Hecate corrections, 2026-10-01 (Wave 2) -- each verified by Hecate from rows

Sources: Harmonia audit roles/Harmonia/audits/EVIDENCE_AUDIT_2026-09-30.md
(comms #1037); Hecate W2 audits roles/Hecate/harvest_w2/AUDIT_B_world_evaluators.md,
ATTACK_C_alien_headlines.md, ATTACK_D_autopsy_R1.md. Originals stay
visible; corrections are annotations.

K1 HT-55162c0ac0 W6 Pass 4 ORIG: recorded "fired: false" -> FIRED in substance.
   Verified: ALT_TREATMENT rows at r = 0.65 (Lyapunov -0.956..-0.853) and
   r = 0.8 (-0.057..-0.034): 10/10 seeds LLE < 0 and 10/10 ARI >= 0.8, non-
   degenerate trajectories. Caveat: those levels ran at noise sigma 0.05;
   the original world used sigma 0. Program stays PARK (ALT failed); prior
   art KNOWN_ANALOGUE_FOUND (perturbation-response network inference).
   Calibration ledger row 4 ("my ORIG prediction was wrong") is itself
   wrong: the prediction held; the attacker ran ORIG at one carrier only.
K2 REPORT_pilot "affine baseline (0.44) beats Claude (0.33)": KILLED.
   Verified: unlike subsets and metrics. Same 5 adversarial systems:
   Claude T2 comp 0.512 vs affine T2 comp 0.487; Claude code eval comp 0.513
   vs affine eval comp 0.436. The affine baseline did not run on the 3 map
   systems (silently absent from its group mean).
K3 hecate/gravity/calibration_v1.json never held the 14 detector controls:
   on this case-insensitive filesystem the gate writer's CALIBRATION_v1.json
   overwrote it before commit b15a475b8, whose message claimed "+ 14
   controls". Restored as hecate/gravity/controls_v1.json; verified 14/14
   restored texts scrub to the recorded blind texts, and the gate re-derived
   from calibration_rows_v1.jsonl equals the committed gate and table
   exactly. run.py now reads controls_v1.json and writes gate_v1.json;
   regression tests forbid case-colliding paths under hecate/.
K4 HT-a9e2ba7618 W3 (round 2): recorded NULL -> SPEC_UNATTAINABLE. Verified:
   osc - comp ARI max 0.000 over 50 PC and 50 treatment seeds (null twin
   exceeds it on 35/50): the pilot repair (KC = 1.6, above every clique's
   locking bound) made the deciding clause unattainable; the round-2 pilot
   checked only absolute ARI. Program PARK -> SPECULATIVE (one valid NULL,
   W4), by the round-2 consequence table.
K5 Novelty autopsy Part A "largest loss at admission; admission skewed by
   form": REVISED. Verified: 126/243 mechanisms never appear in any
   specified world; admission among those that do is 58/117. The by-form
   skew does not survive a permutation test (p ~ 0.18, ATTACK_D). The
   largest loss is at world SPECIFICATION.
K6 Novelty autopsy Part B input was not "exact rule text": the meta v1
   scrubber was applied and erased every rewrite rule ("YZ -> XW" -> "[X] ->
   [X]"). R1 still fires without the 8 rewrite aliens (0/24). R1 is a
   property of the definition on fully specified rules (FAMILIAR is literally
   correct at construction-class level), so it supports C6, not C4; it does
   not transfer to meta v1's prose inputs as argued. Meta v1's zero stays
   uninformative on better evidence: no item was ever labelled UNFAMILIAR at
   any prior_fit, and all 22 items with prior_fit <= 0.50 went COMPOSITE.
K7 Alien pilot sandbox rejected 4 Claude step programs (local lambda calls
   f, h; str join/split). Frozen scorer unchanged; sensitivity rescore with
   those allowed: 2 standard map aliens' code becomes eval exact 1.0 (both
   were already LEARNED via T2), 1 scramble null stays 0.0. Headline
   learned 28/32 unchanged; alien code-eval exact rises (reported as
   sensitivity only).
K8 REPORT_pilot, false-collapse story ("asked to implement the standard
   map, wrote the textbook map"): contradicted by the code (its own
   lookup-table shear; ATTACK_C item 6). Both FALSE_COLLAPSE cases are
   classifier artefacts; H5 reads 0/32 genuine collapses.
K9 Also from #1037 (minor, accepted): families ran concurrently, contrary
   to PREREG s10 ("A, then B, then C") -- recorded here as a protocol
   deviation; the Gemini RESULTS verdict now reads NOT_ELIGIBLE (missing
   inputs), Claude's verdict unchanged.
