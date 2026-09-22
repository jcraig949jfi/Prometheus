"""T-P4. The reservoir flag must require an ancestry certificate.

THE DEFECT. The predecessor fired RESERVOIR_CROSSED_A_MOAT on structure + moat + any
historical crossing:

    if summary.get("crossed") and cell["structure"] == "RESERVOIR" and d["moat"]:

Nothing there asks whether the easy niche supplied the lineage that crossed. In the
72-hour campaign it fired 124 times: 117 on seeded instrument populations and 7 on
exogenous controls, and every one adjudicated INADMISSIBLE.

Each case below is run through BOTH implementations. `legacy_flag` is the predecessor
condition reimplemented inline (from ../z80atlas-2026-09-19/scheduler.py, the block at
`if summary.get("crossed") and cell["structure"] == "RESERVOIR"`) so the test shows the
unrepaired code failing rather than asserting that it would.

Run:  python tests/test_p4_reservoir.py
Exit: 0 all checks pass, 1 otherwise.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import specials  # noqa: E402


# --------------------------------------------------------------- the unrepaired code
def legacy_flag(cell, d, summary):
    """The predecessor's condition, verbatim in substance."""
    return bool(summary.get("crossed") and cell["structure"] == "RESERVOIR" and d["moat"])


# --------------------------------------------------------------- fixtures
def cell(**kw):
    base = {"world": "GRID", "environment": "STATIC", "representation": "Z8_64",
            "reproduction": "ENDOGENOUS_COPY", "self_location": "PRIMITIVE",
            "copy_primitive": "BYTEWISE", "pressure": "NONE_IMPLICIT",
            "structure": "RESERVOIR", "task_transform": "ADD1",
            "read_order": "ANSWER_BEFORE_READ", "bridge": "VALLEY",
            "seeding": "RANDOM", "mutation_operator": "BOTH",
            "mutation_locality": "LOCAL", "mutation_rate": "MID", "atlas_axis": "NONE"}
    base.update(kw)
    return base


def derived(**kw):
    base = {"endogenous": True, "spontaneity_test": True, "constant_kind": "INCREMENTAL",
            "has_task": True, "moat": True, "seeded_instrument": False}
    base.update(kw)
    return base


def certificate(founder_niche=0, crossing_niche=2):
    return {"founder": 3, "founder_niche": founder_niche,
            "migration": {"oid": 3, "epoch": 40, "from_niche": 0, "to_niche": 2},
            "crossing_oid": 91, "crossing_niche": crossing_niche,
            "crossing_epoch": 120, "crossing_held": 0.95,
            "lineage_len": 6, "lineage_complete": True}


def summary(**kw):
    base = {"crossed": True, "crossed_ever": True, "crossed_at_final": True,
            "held_max_ever": 0.95, "held_max_final": 0.95, "n_cross_events": 1,
            "lineage_complete": True, "migration_events": 12,
            "has_reservoir_certificate": True, "ancestry_certificate": certificate(),
            "niche_occupancy": [21, 71, 107, 57], "replicated": True,
            "replication_events": 4, "births_similar_no_write": 2,
            "max_causal_replication_depth": 3, "propagating_replicators": 1,
            "span_mean_final": 60.0, "first_replicator": {"fidelity": 0.95}}
    base.update(kw)
    return base


# The case the directive names: all four niches uniformly occupied, no migration before
# the crossing, so no certificate exists. This is the shape of the 72-hour instances.
UNIFORM_NO_MIGRATION = summary(
    has_reservoir_certificate=False, ancestry_certificate=None,
    migration_events=0, niche_occupancy=[64, 64, 64, 64])


CASES = [
    # name, cell, derived, summary, legacy_should_fire, repaired_should_fire
    ("uniform niches, no migration before crossing",
     cell(), derived(), UNIFORM_NO_MIGRATION, True, False),
    ("seeded instrument with a valid certificate",
     cell(seeding="SEEDED_READER"), derived(seeded_instrument=True), summary(), True, False),
    ("lineage incomplete despite a certificate",
     cell(), derived(), summary(lineage_complete=False), True, False),
    ("exogenous control (external reproduction)",
     cell(reproduction="EXTERNAL"), derived(endogenous=False), summary(), True, False),
    ("crossing happened in the easy niche itself",
     cell(), derived(), summary(ancestry_certificate=certificate(crossing_niche=0)), True, False),
    ("no moat",
     cell(), derived(moat=False), summary(), False, False),
    ("complete certificate, hard-niche crossing (the real thing)",
     cell(), derived(), summary(), True, True),
]


def main():
    ok = True
    print("%-46s %-8s %-10s %s" % ("case", "legacy", "repaired", "result"))
    print("-" * 86)
    for name, c, d, s, want_legacy, want_new in CASES:
        got_legacy = legacy_flag(c, d, s)
        got_new = specials.reservoir_crossed_a_moat(c, d, s) is not None
        good = (got_legacy == want_legacy) and (got_new == want_new)
        if not good:
            ok = False
        print("%-46s %-8s %-10s %s" % (
            name[:46],
            "fires" if got_legacy else "-",
            "fires" if got_new else "-",
            "PASS" if good else "FAIL (wanted legacy=%s new=%s)" % (want_legacy, want_new)))
    print("-" * 86)

    # The defect is only demonstrated if the unrepaired code actually fails the cases the
    # repair exists to fix. A test where legacy and repaired agree everywhere proves
    # nothing about the repair.
    divergent = sum(1 for n, c, d, s, wl, wn in CASES if wl != wn)
    print("cases where the unrepaired code fires and the repaired one does not: %d" % divergent)
    if divergent < 5:
        print("FAIL: the unrepaired code must fail these cases, or T-P4 is vacuous")
        ok = False

    # A flag that can never fire is as useless as one that always does.
    fires = sum(1 for n, c, d, s, wl, wn in CASES
                if specials.reservoir_crossed_a_moat(c, d, s) is not None)
    print("cases where the repaired flag fires: %d" % fires)
    if fires != 1:
        print("FAIL: the repaired flag must still fire on a genuine certificate")
        ok = False

    print("\nT-P4:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
