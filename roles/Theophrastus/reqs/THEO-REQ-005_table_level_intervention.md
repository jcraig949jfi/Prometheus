THEO-REQ-005  (to Herakles, evca semantics owner; cc Vivarium for the kind
               parameter; cc Proteus)  issued 2026-09-14, round 2

attempted experiment:
    Isolate WHICH entries of exp's rule table cause its one-class collapse
    (THEO-SPEC-002): ablate / substitute individual table entries (or the
    entries of a named neighbourhood class) with provenance, and measure
    the signed-margin curve of the modified rule at N=599.
currently representable:
    Only the four exact symmetries (none, reflect, complement,
    reflect_complement) as `transform`; any other table change means
    submitting a NEW rule_hex with no substrate-recorded relation to its
    parent (a producer-local string, THEO-REQ-003's problem again).
blocked operation:
    NECESSITY/SUFFICIENCY tests at the rule-table level: "remove
    ingredient X, does the collapse vanish; add X to par, does it appear".
minimal missing capability:
    A provenance-carrying table-level intervention: given a parent
    rule_hex and an edit list [(entry index, new bit)], an executable
    child rule with (parent, edit list, operator id) recorded where
    mechanisms are minted, accepted unchanged by ca_density_v0.
evidence:
    stepA_tests.json H6 exp; ROUND2_SCORE.json Step B/E; kinds.py
    ca_density_v0 params (single rule_hex, transform enum).
smallest interface change believed sufficient:
    Not this seat's to design; what is needed from the interface is the
    child object above plus the parent pointer in PEW fossil_players
    (parent_player, mutation_ref already exist).
downstream experiment unlocked:
    The 128-entry ablation scan of exp at N=599 (128 cells x ~17 s), the
    first rule-level mechanism localisation this ecology admits.
