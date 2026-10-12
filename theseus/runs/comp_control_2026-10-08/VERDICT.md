# THESEUS-30a verdict (prereg roles/Theseus/prereg/2026-10-08_comp_control/, d63808519)

Run: python -m theseus.synth.comp_control --tag comp_control_2026-10-08 --workers 2 (69 s).
Flagged by the 23b detector (fingerprint distance to EMPTY, EPS 1.63 / TAU 4.31):
  planted 0/40; neg_active 0/40; neg_recall 0/40; neg_inert 0/40.
Verdict by the frozen rule: DETECTOR BLIND.

Why (descriptive): writer-only genomes, which never change the state by construction,
sit at median 8.47 fingerprint units from EMPTY. The fingerprint includes STRUCTURAL
interventions (mutate_rule turns "remember" into an active op, transplant inserts
"diffuse", duplicate/remove/reverse/randomize change rules), so it measures how a
genome's rules respond to editing, not whether the genome acts. Fingerprint distance
cannot express "inert"; the 23b detector was blind by construction.

Exploratory follow-up (post hoc, NOT a verdict; it motivates detector v2, which is
preregistered separately before use): a trace-based inertness test -- a part is inert
if its state trajectory is bitwise identical to EMPTY's at IC seeds 0 and 1 -- flags
planted 40/40 and each negative class 0/40 on these same genomes.

Predictions: C1 (VALID) WRONG; C2 (negatives <= 5%) RIGHT; C3 (failures on the
whole-not->TAU clause) WRONG -- failures were on the parts clause.
