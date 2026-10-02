"""G3, G4, G5. Three rulers on the RETAIN-1 panel, and the gates that say where a ruler may be believed.

A ruler returns one answer for one organism. The world-side ruler has five: POSITIVE, NEGATIVE,
UNDECIDED, INVERTED, UNDERPOWERED. A NEGATIVE is earned like a POSITIVE: the score must be too low
for the weakest positive the ruler is registered to detect. A score between the two is UNDECIDED.

The panel knows the truth: each physics has a designed positive and a matched impostor. A ruler is
SHARED only if it returns the truth on every positive and every impostor of at least three physics.
Otherwise it is PHYSICS_SPECIFIC, which is valid, and supports no claim across physics. One of the
three rulers is physics-specific on purpose: it is the panel's own positive control.

What these gates cannot see: whether two physics on a panel are really unlike, and whether an
organism entered under a physics is really of it. Both are declarations. meta.known_escapes pins
a case of each.
"""
from . import stats
from .retain1 import World, score
from .verdict import BLOCKED, FAIL, INDETERMINATE, PASS, UNQUALIFIED, Result, combine

BOUND = 0.5             # exact rate of the class that carries nothing across the gap
ALPHA = 1e-6
P_WEAKEST = 15 / 16     # the weakest positive the world-side ruler is registered to detect
MIN_PHYSICS = 3


def make_exclusion_ruler(bound=BOUND, alpha=ALPHA, weakest=P_WEAKEST):
    """World-side. Reads only what the organism answered. Needs nothing from inside it."""
    def ruler(make, seeds):
        got = stats.classify(score(make, seeds), len(seeds), bound, alpha, weakest)
        return {"EXCLUDES": "POSITIVE", "AT_BOUND": "NEGATIVE"}.get(got, got)
    return ruler


exclusion_ruler = make_exclusion_ruler()


def _interchange(make, seeds, grab, put, at=3):
    """Donor and recipient see the same distractors. At step `at` something is moved from donor to recipient.

    In half the pairs the two have opposite cues; in the other half (the sham) the same cue.
    POSITIVE if the recipient always answers the donor's cue; INVERTED if it always answers the
    complement of the donor's cue; NEGATIVE otherwise.
    """
    follows = inverted = total = 0
    for seed in seeds:
        for donor_bit in (0, 1):
            for sham in (False, True):
                recipient_bit = donor_bit if sham else 1 - donor_bit
                box = []
                World().episode(make(), seed, force_bit=donor_bit, interrupt={at: lambda org: box.append(grab(org))})
                got = World().episode(make(), seed, force_bit=recipient_bit,
                                      interrupt={at: lambda org: put(org, box[0])})["answer"]
                total += 1
                follows += got == donor_bit
                inverted += got == 1 - donor_bit
    return "POSITIVE" if follows == total else "INVERTED" if inverted == total else "NEGATIVE"


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


def _judge(what, expected, got):
    """One known answer against one returned answer."""
    if got == expected:
        return Result(what, PASS)
    if got == "UNDERPOWERED":
        return Result(what, BLOCKED, "too few episodes for any answer")
    if got == "UNDECIDED":
        return Result(what, INDETERMINATE, "the score is between the two registered answers")
    return Result(what, FAIL, "registered %s, returned %s" % (expected, got))


def exclusion_gate(ruler, panel, seeds, weak=None, blocks=()):
    """G3. The world-side ruler returns the known answer on every member of a panel that brackets its bound.

    Positives at the ceiling and impostors near one half are answered alike by any threshold between
    them. So the panel also holds a weak positive (which a bound set too high misses) and every
    impostor on several further blocks of seeds (some of which a bound set too low lets through).
    """
    gate = "G3.exclusion"
    if not panel or any(pos is None or imp is None for pos, imp in panel.values()):
        return Result(gate, UNQUALIFIED, "the panel lacks a positive or an impostor")
    if weak is None or not blocks:
        return Result(gate, UNQUALIFIED, "no weak positive, or no further impostor blocks: the bound is not bracketed")
    found = []
    for physics, (pos, imp) in sorted(panel.items()):
        found.append(_judge("%s positive" % physics, "POSITIVE", ruler(pos, seeds)))
        for i, block in enumerate([seeds] + list(blocks)):
            found.append(_judge("%s impostor, block %d" % (physics, i), "NEGATIVE", ruler(imp, block)))
    found.append(_judge("weak positive", "POSITIVE", ruler(weak, seeds)))
    out = combine(gate, found)
    return Result(gate, out.verdict, "; ".join("%s: %s" % (r.gate, r.reason) for r in found if r.verdict != PASS)[:400])


def entry_gate(physics, panel, seeds):
    """G4. May a null, or a ruler that looks inside the organism, be read in this physics?

    Door one: the physics has a designed positive and a matched impostor, both declared to be of this
    physics, and the world-side ruler returns the truth on both. (Door two, a positive found by blind
    search and certified by class exclusion, is specified and not implemented here.)
    """
    gate = "G4.entry[%s]" % physics
    pair = panel.get(physics)
    if not pair or pair[0] is None or pair[1] is None:
        return Result(gate, UNQUALIFIED, "no known answer in this physics: a null here cannot be read")
    pre = stats.preflight(len(seeds), BOUND, ALPHA, P_WEAKEST)
    if pre.verdict != PASS:
        return Result(gate, BLOCKED, pre.reason)
    strangers = [role for role, cls in zip(("positive", "impostor"), pair) if getattr(cls, "physics", None) != physics]
    found = [Result("label", FAIL, "not declared to be of this physics: the %s" % " and the ".join(strangers))] \
        if strangers else []
    on_positive, on_impostor = exclusion_ruler(pair[0], seeds), exclusion_ruler(pair[1], seeds)
    found.append(_judge("positive", "POSITIVE", on_positive))
    if on_impostor == "INVERTED":
        found.append(Result("impostor", FAIL, "the impostor carries the cue and answers its complement"))
    elif on_impostor == "POSITIVE":
        found.append(Result("impostor", FAIL, "the impostor beats the exact bound: it is no impostor, or the world leaks"))
    else:
        found.append(_judge("impostor", "NEGATIVE", on_impostor))
    out = combine(gate, found)
    return Result(gate, out.verdict, out.reason)


def known_answers(ruler, panel, seeds):
    """What the ruler returns on the positive and the impostor of each physics, and whether both are the truth."""
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

    declared is "SHARED" or a list of physics names the ruler is declared valid in. SHARED means: it
    returns the truth on every physics of the panel that has a known answer, and there are at least
    three. A physics with no known answer is reported as outside the ruler's authority.
    """
    gate = "G5.neutrality[%s]" % name
    table = known_answers(ruler, panel, seeds)
    known = [p for p, row in table.items() if row is not None]
    unknown = [p for p, row in table.items() if row is None]

    def judge(scope):
        rows = [r for p in scope for r in (_judge("%s positive" % p, "POSITIVE", table[p]["positive"]),
                                           _judge("%s impostor" % p, "NEGATIVE", table[p]["impostor"]))]
        return combine(gate, rows)

    if declared == "SHARED":
        if len(known) < MIN_PHYSICS:
            return Result(gate, UNQUALIFIED, "a shared ruler needs known answers in %d unlike physics; the panel has %d"
                          % (MIN_PHYSICS, len(known)), table)
        out = judge(known)
        if out.verdict != PASS:
            return Result(gate, out.verdict, "declared shared; " + out.reason, table)
        note = "shared across %d physics" % len(known)
        return Result(gate, PASS, note + ("; no authority in: %s" % ", ".join(unknown) if unknown else ""), table)
    if not declared:
        return Result(gate, BLOCKED, "a ruler must declare where it is valid", table)
    outside = [p for p in declared if table.get(p) is None]
    if outside:
        return Result(gate, UNQUALIFIED, "declared valid in a physics with no known answer: %s" % ", ".join(outside),
                      table)
    out = judge(declared)
    if out.verdict != PASS:
        return Result(gate, out.verdict, "inside its declared scope; " + out.reason, table)
    return Result(gate, PASS, "physics-specific: valid in %s; supports no claim across physics" % ", ".join(declared),
                  table)
