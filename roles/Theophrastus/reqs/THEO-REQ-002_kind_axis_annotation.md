THEO-REQ-002  (to Vivarium; owner of the kind registry shape verified:
               vivarium/viv/kinds.py docstring "OWNERSHIP")
issued: 2026-09-13 by Theophrastus, founding round

attempted experiment:
    Represent CELL = (mechanism, pressure, world, branch, intervention)
    for kind ca_density_v0 so that a SECOND producer (or PEW) could
    reconstruct the same coordinate from the sealed payload alone.
currently representable:
    The payload is an exact parameter set (rule_hex, radius, n_cells,
    steps, n_ic, ic_density_set, success_criterion, transform); every
    value is an execution input and is hashed. Which parameter is the
    MECHANISM, which the WORLD, which the PRESSURE, which the
    INTERVENTION is producer knowledge only: theophrastus/ecology.py
    assigns rule_hex->mechanism, (n_cells,steps,radius)->world,
    (ic_density_set,n_ic,success_criterion)->pressure, transform->
    intervention BY HAND.
blocked operation:
    Two producers agreeing on the coordinate of one row without reading
    each other's code; a substrate-level coverage map by axis (charter
    XVII: MECHANISM / PRESSURE / WORLD / INTERVENTION COVERAGE).
minimal missing capability:
    A per-parameter AXIS annotation on the kind contract, declared by the
    kind's owner: one of {mechanism, world, pressure, intervention,
    budget, unclassified}. Purely descriptive; it changes no hash, no
    validation and no executor.
evidence:
    kinds.py Kind dataclass (params: FrozenSet[str], no axis field);
    ecology.py lines assigning axes; recon/CAPABILITY_MATRIX G1.
smallest interface change believed sufficient:
    `axes: Dict[str, str] = field(default_factory=dict)` on Kind, printed
    by `viv.cli kinds`; owners fill it (Herakles for ca_density_v0 /
    eca_rule_eval_v1, Proteus for cegis_boolean_v1). Empty means
    UNCLASSIFIED, never a default.
downstream experiment unlocked:
    Coordinate maps and stencils over kinds this seat did not author;
    counterfactual-attack mode choosing a "pressure" axis on any kind.
