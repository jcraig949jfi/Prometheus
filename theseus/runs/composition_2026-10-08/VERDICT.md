# THESEUS-23b verdict (prereg roles/Theseus/prereg/2026-10-08_composition/, 279db6bdc)

Run: python -m theseus.synth.composition --tag composition_2026-10-08 --workers 4.
1011 viable v0_1 genomes (120 per arm; A 51). Wall 4533 s, CPU 15264 s (4.2 CPU-h;
prereg estimate 40 min / < 3 CPU-h was low -- ledger row).

Compositions (both parts <= EPS 1.63 from EMPTY, whole > TAU 4.31): 0 in EVERY arm
(D, E, S, G, B, C, P, R: 0/120; A: 0/51). Verdict by the frozen rule: INDETERMINATE
(wall and detector blindness cannot be separated). H-COMP: Fisher p = 1.0.

Failure shape (descriptive, from ROWS.jsonl):
- every genome's whole is > TAU from EMPTY (1011/1011);
- at each genome's most synergistic split, the SMALLER part alone is already
  5.77 (5th pct) / 8.99 (median) from EMPTY -- far above TAU. Contiguous parts are
  never inert alone in this substrate;
- best synergy ratio (whole / larger part): median 1.10-1.16 in every arm, 95th pct
  1.38, max 2.25 -- near-additive everywhere.
Reading: with this op set nearly every rule acts on the state by itself, so a
2-part mechanism whose parts are each worth nothing alone is close to impossible
BY CONSTRUCTION; the composition wall is, here, a property of the primitive set
before it is a property of the search (successor THESEUS-30).

Predictions: K1 (all rates < 5%) RIGHT; K2 (not supported / indeterminate) RIGHT;
K3 (R highest) WRONG (all tied at 0).

CORRECTION 2026-10-08 (THESEUS-30a, theseus/runs/comp_control_2026-10-08/VERDICT.md):
the detector used here is BLIND by construction -- planted compositions whose parts are
inert alone by construction are flagged 0/40, because fingerprint distance includes
structural interventions and cannot express "inert". The INDETERMINATE verdict above
stands; the "Reading" paragraph above (wall = property of the primitive set; "parts
never inert alone") is NOT SUPPORTED by this instrument and is withdrawn. A trace-based
detector v2 is preregistered under THESEUS-30b.
