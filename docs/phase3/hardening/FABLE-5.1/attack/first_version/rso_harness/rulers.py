"""G3, G4, G5. Three rulers on the RETAIN-1 panel, and the gate that says whether a ruler is shared.

A ruler returns POSITIVE or NEGATIVE for one organism. The panel knows the truth: each physics has a
designed positive and a matched impostor. A ruler is SHARED only if it returns the truth on every
positive and every impostor of at least three unlike physics. Otherwise it is PHYSICS_SPECIFIC, which
is valid, and supports no claim across physics.

One of the three rulers is physics-specific on purpose. It is the panel's own positive control: a
neutrality gate that cannot flag it has not been shown able to flag anything.
"""
from .retain1 import World, score
from .stats import class_exclusion
from .verdict import FAIL, PASS, UNQUALIFIED, Result

BOUND = 0.5         # exact best rate of the class that carries nothing across the gap
ALPHA = 1e-6
MIN_PHYSICS = 3


def exclusion_ruler(make, seeds):
    """World-side. Reads only what the organism answered. Needs nothing from inside it."""
    return "POSITIVE" if class_exclusion(score(make, seeds), len(seeds), BOUND, ALPHA) == "EXCLUDES" else "NEGATIVE"


def _interchange(make, seeds, grab, put, at=3):
    """Donor and recipient see the same distractors and opposite cues. At step `at` something is moved.

    POSITIVE if the recipient then answers the donor's cue in every pair, and a donor with the
    recipient's own cue (the sham) changes nothing.
    """
    for seed in seeds:
        for donor_bit in (0, 1):
            for sham in (False, True):
                recipient_bit = donor_bit if sham else 1 - donor_bit
                box = []
                World().episode(make(), seed, force_bit=donor_bit, interrupt={at: lambda org: box.append(grab(org))})
                got = World().episode(make(), seed, force_bit=recipient_bit,
                                      interrupt={at: lambda org: put(org, box[0])})["answer"]
                if got != donor_bit:
                    return "NEGATIVE"
    return "POSITIVE"


def interchange_ruler(make, seeds):
    """Moves the whole captured state through the runtime's own capture and restore."""
    return _interchange(make, seeds, lambda org: org.capture(), lambda org, state: org.restore(state))


def register_swap_ruler(make, seeds):
    """Physics-specific on purpose: it moves the attribute named `w` and nothing else."""
    missing = object()

    def put(org, value):
        if value is not missing and hasattr(org, "w"):
            org.w = value

    return _interchange(make, seeds, lambda org: getattr(org, "w", missing), put)


RULERS = {"CLASS_EXCLUSION": exclusion_ruler, "INTERCHANGE": interchange_ruler, "REGISTER_SWAP": register_swap_ruler}


def entry_gate(physics, panel, seeds):
    """G4. May a null, or a ruler that looks inside the organism, be read in this physics?

    Door one: the physics has a designed positive and a matched impostor, and the world-side ruler
    returns the truth on both. (Door two, a positive found by blind search and certified by class
    exclusion, is specified and not implemented here.)
    """
    gate = "G4.entry[%s]" % physics
    pair = panel.get(physics)
    if not pair or pair[0] is None or pair[1] is None:
        return Result(gate, UNQUALIFIED, "no known answer in this physics: a null here cannot be read")
    if exclusion_ruler(pair[0], seeds) != "POSITIVE":
        return Result(gate, FAIL, "the designed positive does not beat the exact bound")
    if exclusion_ruler(pair[1], seeds) != "NEGATIVE":
        return Result(gate, FAIL, "the impostor beats the exact bound: it is no impostor, or the world leaks")
    return Result(gate, PASS)


def measured_scope(ruler, panel, seeds):
    """Where does this ruler return the truth on both the positive and the impostor?"""
    table = {}
    for physics, (positive, impostor) in sorted(panel.items()):
        if positive is None or impostor is None:
            table[physics] = None                   # no known answer: the ruler has no authority here
            continue
        on_positive, on_impostor = ruler(positive, seeds), ruler(impostor, seeds)
        table[physics] = {"positive": on_positive, "impostor": on_impostor,
                          "agrees": on_positive == "POSITIVE" and on_impostor == "NEGATIVE"}
    return table


def neutrality_gate(name, ruler, declared, panel, seeds):
    """G5. Is the ruler's declared scope the scope it has shown?

    declared is "SHARED" or a list of physics names the ruler is declared valid in.
    """
    gate = "G5.neutrality[%s]" % name
    table = measured_scope(ruler, panel, seeds)
    known = [p for p, row in table.items() if row is not None]
    wrong = [p for p in known if not table[p]["agrees"]]
    if declared == "SHARED":
        unknown = [p for p, row in table.items() if row is None]
        if unknown:
            return Result(gate, UNQUALIFIED, "no positive and impostor in: %s" % ", ".join(unknown), table)
        if len(known) < MIN_PHYSICS:
            return Result(gate, UNQUALIFIED, "a shared ruler needs %d unlike physics; the panel has %d"
                          % (MIN_PHYSICS, len(known)), table)
        if wrong:
            return Result(gate, FAIL, "declared shared; returns the wrong answer in: %s" % ", ".join(wrong), table)
        return Result(gate, PASS, "shared across %d physics" % len(known), table)
    outside = [p for p in declared if table.get(p) is None]
    if outside:
        return Result(gate, UNQUALIFIED, "declared valid in a physics with no known answer: %s" % ", ".join(outside),
                      table)
    bad = [p for p in declared if not table[p]["agrees"]]
    if bad:
        return Result(gate, FAIL, "wrong answer inside its declared scope: %s" % ", ".join(bad), table)
    return Result(gate, PASS, "physics-specific: valid in %s; supports no claim across physics" % ", ".join(declared),
                  table)
