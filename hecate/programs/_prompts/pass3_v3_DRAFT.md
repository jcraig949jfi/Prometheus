# DRAFT (not issued, not frozen) -- Hecate Pass 3 generator v3

Status: design artifact from Wave 2 (2026-10-01). Not for use until a
PREREG adopts it; under CWO-C Hecate starts no new program. It folds in
every world-design defect found in rounds 1-3 and the Wave-2 audits.

## Lessons, each with its evidence

L1 Self-declared baseline arm. Every world implements the mechanism's own
   Pass-1 `simpler_alternative` as an arm (SIMPLE_ALT); SIGNAL requires the
   treatment to beat SIMPLE_ALT on the deciding clause by a stated margin.
   Evidence: ledger Q6 -- in >= 2 of 5 signals the generator had already
   named the Pass-4 killer (8a87 channel reset; 71b6 fixed-depth listener).
L2 Every success clause is evaluated on the positive control in the pilot,
   not only the absolute one. Evidence: K4 (a9e2 W3: the deciding
   osc>comp clause was unattainable for PC and treatment, max diff 0.000).
L3 No pass-by-construction clause: for each clause, state the value a
   treatment that merely implements the named construction would get, and
   the value the SIMPLE_ALT would get; a clause both pass is not
   discriminating. Evidence: faa9 W5 design notes; 321a ALT counting (C2).
L4 Thresholds may not be lowered to the positive control's reach without
   recording the before/after and the reason in the spec. Evidence: 5516 W5
   S1/S3 0.15 -> 0.08 (INV_J pending).
L5 Spec bands (INCONCLUSIVE, etc.) are mapped to the PREREG's outcome
   classes in the spec itself. Evidence: C1 (ae38 W5).
L6 Self-contained specs; no reference to another world. Evidence: ae38 W4
   round 2 (spec deferred to W1, which the implementer could not read).
L7 Cost is not a selection criterion by itself. Evidence: ledger Q5 -- all
   5 signals came from the cheapest worlds (0.014-0.045 core-min, MWU
   p = 0.006); generators overestimate cost ~4x. Prefer the world with the
   most discriminating clause set; break ties by cost.
L8 Mechanisms that never receive a world are listed with the reason (not
   silently dropped). Evidence: 126/243 Pass-1 mechanisms never got a world
   (K5; INV_H pending).
L9 No attack or clause whose outcome is fixed by arithmetic: before
   freezing, compute it under the known-mechanism hypothesis. Evidence:
   calibration ledger row 2 (321a ALT), C2.
L10 Output files never share a case-folded name with input files.
    Evidence: K3 (detector controls overwritten by the gate output).

## Spec additions (on top of pass3_v2)

    "simple_alt": {"from_mechanism": "<id>", "implementation": "...",
                   "expected_on_clauses": {...}},
    "clauses": [{"id","text","statistic","comparison","threshold",
                 "pc_value","twin_value","simple_alt_value",
                 "construction_value","band_mapping": {...}}],
    "threshold_history": [{"clause","from","to","reason"}],
    "unbuilt_mechanisms": [{"id","reason"}]

Frozen only if every success clause: PC attains it; twin does not;
SIMPLE_ALT does not (or the clause is explicitly a SIMPLE_ALT-beating
margin); construction_value does not pass it trivially.
